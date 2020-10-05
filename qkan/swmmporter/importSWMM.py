# -*- coding: utf-8 -*-

__author__ = "Joerg Hoettges"
__date__ = "März 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

import os
from pathlib import Path

from qkan import QKan, enums
from qkan import QKan, QKAN_FORMS, QKAN_TABLES
from qkan.database.dbfunc import DBConnection
from qgis.utils import pluginDirectory
from qkan.tools.k_qgsadapt import qgsadapt
import xml.etree.ElementTree as ET
from qgis.core import QgsCoordinateReferenceSystem, QgsProject

import logging

logger = logging.getLogger("QKan.importswmm.import_from_swmm")

# Hilfsfunktionen, werden wenn Sie in QKan integriert sind importiert
# from qkan.database.qkan_utils import evalNodeTypes, fehlermeldung, fzahl

def fehlermeldung(self, title, text=""):
    """Ersetzt während der Entwicklungszeit die QKan-Funktion"""
    with open('fehler.log', 'a') as prot:
        prot.write(title + '\n')
        prot.write(text + '\n')

def fzahl(text, n=0.0, default=0.0):
    """Ersetzt während der Entwicklungszeit die QKan-Funktion"""
    """Wandelt einen Text in eine Zahl um. Falls kein Dezimalzeichen
       enthalten ist, werden n Nachkommastellen angenommen"""
    zahl = text.strip()
    if zahl == "":
        return default
    elif "." in zahl:
        try:
            return float(zahl)
        except BaseException as err:
            logger.error("10: {}".format(err))
            return None
    else:
        return float(zahl) / 10.0 ** n

def kstFromKs(ks):
    """Umrechnung des Wertes für die äquivalente Sandrauheit k in die Rauheit nach Manning-Strickler"""
    C_Chezy = 25.68
    erg = C_Chezy / ks ** (1/6)
    return erg

def ksFromKst(kst):
    """Umrechnung des Wertes für die äquivalente Sandrauheit k in die Rauheit nach Manning-Strickler"""
    C_Chezy = 25.68
    erg = (C_Chezy / kst) ** 6
    return erg


class SWMM:
    def __init__(self, inpfile, database_QKan, projectfile, offset=[0., 0.], epsg=25832, dbtyp="SpatiaLite"):
        self.epsg = epsg
        self.dbtyp = dbtyp
        self.inpobject = Path(inpfile)
        self.data = {}
        self.database_QKan = database_QKan
        self.projectfile = projectfile
        self.xoffset, self.yoffset = offset

        self.dbQK = DBConnection(
            dbname=database_QKan, epsg=epsg
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben

        self.connected = self.dbQK.connected

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in import_from_swmm:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )

    def __del__(self):
        self.dbQK.sql("SELECT RecoverSpatialIndex()")
        del self.dbQK

    def read(self):
        with self.inpobject.open("r") as inp:
            position = inp.tell()
            block = ""

            while True:
                zeile = inp.readline().strip()

                # Break at end of file
                if position == inp.tell():
                    break
                position = inp.tell()

                # Skip comments and empty lines
                if zeile.startswith(";") or len(zeile) < 1:
                    continue

                # Block starts
                if zeile.startswith("["):
                    block = zeile.replace("[", "").replace("]", "").lower()

                # Block data
                if not zeile.startswith("[") and block != "":
                    data = self.data.get(block, [])
                    data.append(zeile)
                    self.data[block] = data

    @property
    def title(self) -> str:
        return self.data.get("title", ["Unknown"])[0]

    @property
    def options(self) -> dict:
        # Könnte auch direkt gesetzt werden, um Rechenzeit zu sparen
        opts = self.data.get("options", [])
        ret = {}
        for line in opts:
            opt = line.split()
            ret[opt[0]] = opt[1]
        return ret

    def junctions(self):
        """Liest einen Teil der Schachtdaten ein. Rest siehe coordinates"""
        data = self.data.get("junctions", [])
        for line in data:
            name = line[0:17].strip()           # schnam
            elevation = line[17:28].strip()     # sohlhoehe
            maxdepth = line[28:39].strip()      # = deckelhoehe - sohlhoehe
            initdepth = line[39:50].strip()     # entfällt
            surDepth = line[50:61].strip()      # entfällt
            areaPonded = line[61:72].strip()    # ueberstauflaeche

            sql = f"""
                INSERT into schaechte_data (
                    schnam, sohlhoehe, deckelhoehe, ueberstauflaeche, schachttyp)
                VALUES (
                    '{name}', {elevation}, {elevation} + {maxdepth}, {areaPonded}, 'Schacht')
                """
            if not self.dbQK.sql(sql, repeatmessage=True):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def outfalls(self):
        """Liest die Ausläufe ein. Rest siehe coordinates"""

        outtypes = {
            'FREE': 'frei',
            'NORMAL': 'normal',
            'FIXED': 'konstant',
            'TIDAL': 'Tide',
            'TIMESERIES': 'Zeitreihe'
        }

        data = self.data.get("outfalls", [])
        for line in data:
            name = line[0:17].strip()  # schnam
            elevation = line[17:28].strip()  # sohlhoehe
            outtype = line[28:39].strip()  # Auslasstyp
            if outtype != '':
                auslasstyp = outtypes[outtype]
            else:
                auslasstyp = 'frei'

            sql = f"""
                INSERT into schaechte_data (
                    schnam, sohlhoehe, auslasstyp, schachttyp)
                VALUES (
                    '{name}', {elevation}, '{auslasstyp}', 'Auslass')
                """
            if not self.dbQK.sql(sql):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def coordinates(self):
        """Liest die Koordinaten zu den bereits angelegten Schaechten ein"""
        data = self.data.get("coordinates", [])
        for line in data:
            name = line[0:17].strip()                                               # schnam
            xsch = fzahl(line[17:36].strip(),3,self.xoffset) + self.xoffset         # xsch
            ysch = fzahl(line[36:54].strip(),3,self.yoffset) + self.yoffset         # ysch
            du = 1.

            # Geo-Objekte erzeugen

            if QKan.config.database.type == enums.QKanDBChoice.SPATIALITE:
                geop = f"MakePoint({xsch},{ysch},{self.epsg})"
                geom = f"CastToMultiPolygon(MakePolygon(MakeCircle({xsch}, {ysch}, {du}, {self.epsg})))"
            elif QKan.config.database.type == enums.QKanDBChoice.POSTGIS:
                geop = f"ST_SetSRID(ST_MakePoint({xsch}, {ysch}), {self.epsg})"
            else:
                fehlermeldung(
                    "Programmfehler!",
                    "Datenbanktyp ist fehlerhaft {}!\nAbbruch!".format(QKan.config.database.type),
                )

            du = 1.0

            sql = f"""
                UPDATE schaechte SET (
                    xsch, ysch, geom, geop) =
                (   {xsch}, {ysch}, {geom}, {geop})
                WHERE schnam = '{name}'
                """
            if not self.dbQK.sql(sql):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def subcatchments(self):
        """Liest einen Teil der Daten zu tezg-Flächen ein"""
        data = self.data.get("subcatchments", [])
        for line in data:
            # Attribute bitte aus qkan.database.qkan_database.py entnehmen
            name = line[0:16].strip()
            regenschreiber = line[17:33].strip()
            schnam = line[34:50].strip()
            befgrad = fzahl(line[61:69].strip())
            neigung = fzahl(line[78:86].strip())

            sql = f"""
                INSERT into tezg (
                    flnam, regenschreiber, schnam,befgrad, neigung)
                VALUES (
                    '{name}', '{regenschreiber}', '{schnam}', {befgrad}, {neigung})
                """
            if not self.dbQK.sql(sql):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def polygons(self):
        """Liest die Polygone zu den bereits angelegten tezg-Flächen ein"""

        data = self.data.get("polygons", [])
        data.append('ende')                     # Trick, damit am Ende das letzte Polygon geschrieben wird
        
        nampoly = ''                            # Solange der Name gleich bleibt, gehören 
                                                # die Eckpunkte zum selben Polygon (tezg-Fläche)
        for line in data:
            name = line[0:17].strip()                               # schnam
            xsch = fzahl(line[17:36].strip(), 3, self.xoffset) + self.xoffset        # xsch
            ysch = fzahl(line[36:54].strip(), 3, self.yoffset) + self.yoffset        # ysch

            if nampoly != name:
                if nampoly != '':
                    # Koordinaten des ersten Punkte am Ende nochmal anhängen
                    xlis.append(xlis[0])
                    ylis.append(ylis[0])

                    # Polygon schreiben
                    coords = ', '.join([f'{x} {y}' for x,y in zip(xlis, ylis)])
                    geom = f"GeomFromText('MULTIPOLYGON((({coords})))', {self.epsg})"
                    sql = f"""
                        UPDATE tezg SET geom = {geom}
                        WHERE flnam = '{nampoly}'
                        """
                    if not self.dbQK.sql(sql, repeatmessage=True):
                        del self.dbQK
                        return False
                nampoly = name
                # Listen zurücksetzen
                xlis = []                               # x-Koordinaten zum Polygon
                ylis = []                               # y-Koordinaten zum Polygon
            if name == 'ende':
                continue                                # Letzte Zeile ist nur ein dummy

            # Koordinaten des Eckpunktes übernehmen
            xlis.append(xsch)
            ylis.append(ysch)

        self.dbQK.commit()

        return True

    def conduits(self):
        """Liest einen Teil der Haltungsdaten ein"""

        data = self.data.get("conduits", [])
        for line in data:
            # Attribute bitte aus qkan.database.qkan_database.py entnehmen
            haltnam = line[0:17].strip()
            schoben = line[17:34].strip()
            schunten = line[34:51].strip()
            laenge = line[51:62].strip()

            # Rauheitsbeiwerte
            mannings_n = fzahl(line[62:73])
            # kst = 1/mannings_n                      # interessant: die Einheit von mannings_n ist s/m**(1/3)!
            # ks = ksFromKst(kst)

            sql = f"""
                INSERT into haltungen_data (
                    haltnam, schoben, schunten, laenge, ks, entwart, simstatus)
                VALUES (
                    '{haltnam}', '{schoben}', '{schunten}', {laenge}, {mannings_n}, 'Regenwasser', 'vorhanden')
                """
            if not self.dbQK.sql(sql):
                del self.dbQK
                return False

        # Haltungsobjekte mithilfe der Schachtkoordinaten erzeugen
        # sql = f"""
            # UPDATE haltungen 
            # SET geom = (
                # SELECT
                    # MakeLine(schob.geop, schun.geop)
                # FROM
                    # schaechte AS schob,
                    # schaechte AS schun
                # WHERE schob.schnam = haltungen.schoben AND schun.schnam = haltungen.schunten
            # )
            # """
        # if not self.dbQK.sql(sql):
            # del self.dbQK
            # return False

        self.dbQK.commit()

        return True

    def vertices(self):
        data = self.data.get("vertices", [])
        data.append('ende')  # Trick, damit am Ende das letzte Polygon geschrieben wird

        namvor = ''     # Solange der Name gleich bleibt, gehören
                        # die Eckpunkte zur selben Haltung
        npt = 2         # Punkt, der eingefügt werden muss

        for line in data:
            name = line[0:17].strip()  # schnam
            xsch = fzahl(line[17:37].strip(), 3, self.xoffset) + self.xoffset  # xsch
            ysch = fzahl(line[36:56].strip(), 3, self.yoffset) + self.yoffset  # ysch

            if name == namvor:
                npt += 1
            else:
                npt = 2

            sql = f"""
                UPDATE haltungen SET geom = AddPoint(geom, MakePoint({xsch}, {ysch}, {self.epsg}), {npt})
                WHERE halnam = '{name}'
                """

            if not self.dbQK.sql(sql, repeatmessage=True):
                del self.dbQK
                return False

            namvor = name

        self.dbQK.commit()

        return True

    def xsections(self):
        """Liest die Profildaten zu den Haltungen ein. Dabei werden sowohl Haltungsdaten ergänzt
        als auch Profildaten erfasst"""

        profiltypes = {
            'CIRCULAR': 'Kreisquerschnitt'
        }

        data = self.data.get("xsections", [])
        for line in data:
            # Attribute bitte aus qkan.database.qkan_database.py entnehmen
            haltnam = line[0:17].strip()
            xsection = line[17:30].strip()               # shape
            hoehe = line[30:47].strip()                   # Geom1
            breite = line[47:58].strip()                  # Geom2
            barrels = line[80:91].strip()                 # Falls > 1, muss die Haltung mehrfach angelegt werden

            if xsection == 'IRREGULAR':
                hoehe = 'NULL'
                breite = 'NULL'

            if xsection in profiltypes:
                profilnam = profiltypes[xsection]
            else:
                profilnam = 'Kreisquerschnitt'

            sql = f"""
                UPDATE haltungen SET (
                    profilnam, hoehe, breite) = 
                (   '{profilnam}', {hoehe}, {breite})
                WHERE haltnam = '{haltnam}'
                """
            if not self.dbQK.sql(sql):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

            # todo: SQL-Anweisung wie oben ergänzen


    def writeProjektfile(self):
        # --------------------------------------------------------------------------
        # Zoom-Bereich für die Projektdatei vorbereiten
        sql = """SELECT min(x(geop)) AS xmin, 
                        max(x(geop)) AS xmax, 
                        min(y(geop)) AS ymin, 
                        max(y(geop)) AS ymax
                 FROM schaechte"""
        try:
            if not self.dbQK.sql(sql, "importkanaldaten_swmm (17)"
                            ):
                del self.dbQK
                return False
        except BaseException as e:
            fehlermeldung("SQL-Fehler", str(e))
            fehlermeldung(
                "Fehler in QKan_Import_from_KP", "\nFehler in sql_zoom: \n" + sql + "\n\n"
            )

        daten = self.dbQK.fetchone()
        try:
            zoomxmin, zoomxmax, zoomymin, zoomymax = daten
        except BaseException as e:
            fehlermeldung("SQL-Fehler", str(e))
            fehlermeldung(
                "Fehler in QKan_Import_from_KP",
                "\nFehler in sql_zoom; daten= " + str(daten) + "\n",
            )

        # --------------------------------------------------------------------------
        # Projektionssystem für die Projektdatei vorbereiten
        sql = """SELECT srid
                FROM geom_cols_ref_sys
                WHERE Lower(f_table_name) = Lower('schaechte')
                AND Lower(f_geometry_column) = Lower('geom')"""
        if not self.dbQK.sql(sql, "importkanaldaten_swmm (37)"):
            del self.dbQK
            return False

        srid = self.dbQK.fetchone()[0]
        try:
            crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
            srsid = crs.srsid()
            proj4text = crs.toProj4()
            description = crs.description()
            projectionacronym = crs.projectionAcronym()
            if "ellipsoidAcronym" in dir(crs):
                ellipsoidacronym = crs.ellipsoidAcronym()
            else:
                ellipsoidacronym = None
        except BaseException as e:
            srid, srsid, proj4text, description, projectionacronym, ellipsoidacronym = (
                "dummy",
                "dummy",
                "dummy",
                "dummy",
                "dummy",
                "dummy",
            )

            fehlermeldung('\nFehler in "daten"', str(e))
            fehlermeldung(
                "Fehler in QKan_Import_from_KP",
                "\nFehler bei der Ermittlung der srid: \n" + str(daten),
            )

        # --------------------------------------------------------------------------
        # Projektdatei schreiben, falls ausgewählt

        if self.projectfile is not None and self.projectfile != "":
            templatepath = os.path.join(pluginDirectory("qkan"), "templates")
            projecttemplate = os.path.join(templatepath, "projekt.qgs")
            projectpath = os.path.dirname(self.projectfile)
            if os.path.dirname(self.database_QKan) == projectpath:
                datasource = self.database_QKan.replace(os.path.dirname(self.database_QKan), ".")
            else:
                datasource = self.database_QKan

            # Lesen der Projektdatei ------------------------------------------------------------------
            qgsxml = ET.parse(projecttemplate)
            root = qgsxml.getroot()

            # Projektionssystem anpassen --------------------------------------------------------------

            for tag_maplayer in root.findall(".//projectlayers/maplayer"):
                tag_datasource = tag_maplayer.find("./datasource")
                tex = tag_datasource.text
                # Nur QKan-Tabellen bearbeiten
                if tex[tex.index(u'table="') + 7:].split(u'" ')[0] in QKAN_TABLES:

                    # <extend> löschen
                    for tag_extent in tag_maplayer.findall("./extent"):
                        tag_maplayer.remove(tag_extent)

                    for tag_spatialrefsys in tag_maplayer.findall("./srs/spatialrefsys"):
                        tag_spatialrefsys.clear()

                        elem = ET.SubElement(tag_spatialrefsys, "proj4")
                        elem.text = proj4text
                        elem = ET.SubElement(tag_spatialrefsys, "srsid")
                        elem.text = "{}".format(srsid)
                        elem = ET.SubElement(tag_spatialrefsys, "srid")
                        elem.text = "{}".format(srid)
                        elem = ET.SubElement(tag_spatialrefsys, "authid")
                        elem.text = "EPSG: {}".format(srid)
                        elem = ET.SubElement(tag_spatialrefsys, "description")
                        elem.text = description
                        elem = ET.SubElement(tag_spatialrefsys, "projectionacronym")
                        elem.text = projectionacronym
                        if ellipsoidacronym is not None:
                            elem = ET.SubElement(tag_spatialrefsys, "ellipsoidacronym")
                            elem.text = ellipsoidacronym

            # Pfad zu Formularen auf plugin-Verzeichnis setzen -----------------------------------------

            formspath = os.path.join(pluginDirectory("qkan"), "forms")
            for tag_maplayer in root.findall(u".//projectlayers/maplayer"):
                tag_editform = tag_maplayer.find(u"./editform")
                if tag_editform.text:
                    dateiname = os.path.basename(tag_editform.text)
                    if dateiname in QKAN_FORMS:
                        # Nur QKan-Tabellen bearbeiten
                        tag_editform.text = os.path.join(formspath, dateiname)

            # Zoom für Kartenfenster einstellen -------------------------------------------------------

            if not isinstance(zoomxmin, (int, float)):
                zoomxmin = 0.0
                zoomxmax = 100.0
                zoomymin = 0.0
                zoomymax = 100.0

            for tag_extent in root.findall(u".//mapcanvas/extent"):
                elem = tag_extent.find(u"./xmin")
                elem.text = "{:.3f}".format(zoomxmin)
                elem = tag_extent.find(u"./ymin")
                elem.text = "{:.3f}".format(zoomymin)
                elem = tag_extent.find(u"./xmax")
                elem.text = "{:.3f}".format(zoomxmax)
                elem = tag_extent.find(u"./ymax")
                elem.text = "{:.3f}".format(zoomymax)

            # Projektionssystem anpassen --------------------------------------------------------------

            for tag_spatialrefsys in root.findall(
                    ".//projectCrs/spatialrefsys"
            ):
                tag_spatialrefsys.clear()

                elem = ET.SubElement(tag_spatialrefsys, "proj4")
                elem.text = proj4text
                elem = ET.SubElement(tag_spatialrefsys, "srid")
                elem.text = "{}".format(srid)
                elem = ET.SubElement(tag_spatialrefsys, "authid")
                elem.text = "EPSG: {}".format(srid)
                elem = ET.SubElement(tag_spatialrefsys, "description")
                elem.text = description
                elem = ET.SubElement(tag_spatialrefsys, "projectionacronym")
                elem.text = projectionacronym
                if ellipsoidacronym is not None:
                    elem = ET.SubElement(tag_spatialrefsys, "ellipsoidacronym")
                    elem.text = ellipsoidacronym

            # Pfad zur QKan-Datenbank anpassen

            for tag_datasource in root.findall(u".//projectlayers/maplayer/datasource"):
                text = tag_datasource.text
                tag_datasource.text = (
                        "dbname='" + datasource + "' " + text[text.find("table="):]
                )

            qgsxml.write(self.projectfile)  # writing modified project file
            logger.debug("Projektdatei: {}".format(self.projectfile))
            # logger.debug(u'encoded string: {}'.format(tex))


    def subareas(self):
        pass                    # in QKan nicht verwaltet

    def symbols(self):
        pass                    # in QKan nicht verwaltet

    def coverages(self):
        pass                    # in QKan nicht verwaltet

    def evaporation(self):
        pass                    # in QKan nicht verwaltet

    def raingages(self):
        pass                    # in QKan nicht verwaltet

    def infiltration(self):
        pass                    # in QKan nicht verwaltet

    def pollutants(self):
        pass                    # in QKan nicht verwaltet

    def landuses(self):
        pass                    # in QKan nicht verwaltet

    def loadings(self):
        pass                    # in QKan nicht verwaltet

    def buildup(self):
        pass                    # in QKan nicht verwaltet

    def washoff(self):
        pass                    # in QKan nicht verwaltet

    def timeseries(self):
        pass                    # in QKan nicht verwaltet

    def report(self):
        pass                    # in QKan nicht verwaltet

    def tags(self):
        pass                    # in QKan nicht verwaltet

    def map(self):
        pass                    # in QKan nicht verwaltet

def importKanaldaten(inpfile: str, database_QKan: str, projectfile: str, epsg: int = 25832):
    """Ruft die Klasse SWMM zur Verarbeitung der Daten auf"""

    if not os.path.exists(inpfile):
        return False

    swmm = SWMM(
        inpfile,
        database_QKan,
        projectfile,
        offset=[0., 0.],
        epsg=epsg,
        dbtyp="SpatiaLite"
    )

    if not swmm.connected:
        return False

    swmm.read()

    print(swmm.title)
    #print(swmm.options)        # wird nicht benötigt

    if not swmm.junctions():
        fehlermeldung('Fehler in importKanaldaten', 'junctions()')
    if not swmm.outfalls():
        fehlermeldung('Fehler in importKanaldaten', 'outfalls()')
    if not swmm.coordinates():
        fehlermeldung('Fehler in importKanaldaten', 'coordinates()')
    if not swmm.conduits():
        fehlermeldung('Fehler in importKanaldaten', 'conduits()')
    if not swmm.xsections():
        fehlermeldung('Fehler in importKanaldaten', 'xsections()')
    if not swmm.subcatchments():
        fehlermeldung('Fehler in importKanaldaten', 'subcatchments()')
    if not swmm.polygons():
        fehlermeldung('Fehler in importKanaldaten', 'polygons()')

    # from pprint import pprint

    # pprint(swmm.data)



    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

    template_project = (
            Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
    )
    qgsadapt(
        str(template_project),
        database_QKan,
        swmm.dbQK,
        projectfile,
        epsg
    )

    project = QgsProject.instance()
    project.read(projectfile)
    project.reloadAllLayers()

    # swmm.writeProjektfile()

    del swmm

    return True

if __name__ == "__main__" or __name__ == "console":
    importKanaldaten("tutorial.inp", "sqlcommands.sql")
