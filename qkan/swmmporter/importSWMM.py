# -*- coding: utf-8 -*-

__author__ = "Joerg Hoettges"
__date__ = "März 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, cast

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.utils import pluginDirectory
from qkan import QKAN_FORMS, QKAN_TABLES, QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.tools.k_qgsadapt import qgsadapt

logger = logging.getLogger("QKan.importswmm.import_from_swmm")

# Hilfsfunktionen, werden wenn Sie in QKan integriert sind importiert
# from qkan.database.qkan_utils import eval_node_types, fehlermeldung, fzahl


def fehlermeldung(title: str, text: str = "") -> None:
    """Ersetzt während der Entwicklungszeit die QKan-Funktion"""
    with open("fehler.log", "a") as prot:
        prot.write(title + "\n")
        prot.write(text + "\n")


def fzahl(text: str, n: float = 0.0, default: float = 0.0) -> float:
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
            return default
    else:
        return float(zahl) / 10.0 ** n


def kstFromKs(ks: float) -> float:
    """Umrechnung des Wertes für die äquivalente Sandrauheit k in die Rauheit nach Manning-Strickler"""
    c_chezy = 25.68
    erg = c_chezy / ks ** (1 / 6)
    return erg


def ksFromKst(kst: float) -> float:
    """Umrechnung des Wertes für die äquivalente Sandrauheit k in die Rauheit nach Manning-Strickler"""
    c_chezy = 25.68
    erg = (c_chezy / kst) ** 6
    return erg


class SWMM:
    def __init__(
        self,
        inpfile: str,
        database_qkan: str,
        projectfile: str,
        offset: List[float],
        epsg: int = 25832,
        dbtyp: str = "SpatiaLite",
    ):
        self.epsg = epsg
        self.dbtyp = dbtyp
        self.inpobject = Path(inpfile)
        self.data: Dict[str, List[str]] = {}
        self.database_QKan = database_qkan
        self.projectfile = projectfile
        self.xoffset, self.yoffset = offset

        self.dbQK = DBConnection(
            dbname=database_qkan, epsg=epsg
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben

        self.connected = self.dbQK.connected

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in import_from_swmm:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )

    def __del__(self) -> None:
        self.dbQK.sql("SELECT RecoverSpatialIndex()")
        del self.dbQK

    def read(self) -> None:
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
        title = cast(List[str], self.data.get("title", ["Unknown"]))
        return title[0]

    @property
    def options(self) -> dict:
        # Könnte auch direkt gesetzt werden, um Rechenzeit zu sparen
        opts = self.data.get("options", [])
        ret = {}
        for line in opts:
            opt = line.split()
            ret[opt[0]] = opt[1]
        return ret

    def junctions(self) -> bool:
        """Liest einen Teil der Schachtdaten ein. Rest siehe coordinates"""
        data = self.data.get("junctions", [])
        for line in data:
            name = line[0:17].strip()  # schnam
            elevation = line[17:28].strip()  # sohlhoehe
            maxdepth = line[28:39].strip()  # = deckelhoehe - sohlhoehe
            initdepth = line[39:50].strip()  # entfällt
            surDepth = line[50:61].strip()  # entfällt
            areaPonded = line[61:72].strip()  # ueberstauflaeche

            sql = f"""
                INSERT into schaechte_data (
                    schnam, sohlhoehe, deckelhoehe, ueberstauflaeche, schachttyp)
                VALUES (?, ?, ?, ? 'Schacht')
                """
            if not self.dbQK.sql(
                sql,
                mute_logger=True,
                parameters=(name, elevation, elevation + maxdepth, areaPonded),
            ):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def outfalls(self) -> bool:
        """Liest die Ausläufe ein. Rest siehe coordinates"""

        outtypes = {
            "FREE": "frei",
            "NORMAL": "normal",
            "FIXED": "konstant",
            "TIDAL": "Tide",
            "TIMESERIES": "Zeitreihe",
        }

        data = self.data.get("outfalls", [])
        for line in data:
            name = line[0:17].strip()  # schnam
            elevation = line[17:28].strip()  # sohlhoehe
            outtype = line[28:39].strip()  # Auslasstyp
            if outtype != "":
                auslasstyp = outtypes[outtype]
            else:
                auslasstyp = "frei"

            sql = f"""
                INSERT into schaechte_data (
                    schnam, sohlhoehe, auslasstyp, schachttyp)
                VALUES (?, ?, ?, 'Auslass')
                """
            if not self.dbQK.sql(sql, parameters=(name, elevation, auslasstyp)):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def coordinates(self) -> bool:
        """Liest die Koordinaten zu den bereits angelegten Schaechten ein"""
        data = self.data.get("coordinates", [])
        for line in data:
            name = line[0:17].strip()  # schnam
            xsch = fzahl(line[17:36].strip(), 3, self.xoffset) + self.xoffset  # xsch
            ysch = fzahl(line[36:54].strip(), 3, self.yoffset) + self.yoffset  # ysch
            du = 1.0

            # Geo-Objekte erzeugen

            if QKan.config.database.type == enums.QKanDBChoice.SPATIALITE:
                geop = f"MakePoint({xsch},{ysch},{self.epsg})"
                geom = f"CastToMultiPolygon(MakePolygon(MakeCircle({xsch}, {ysch}, {du}, {self.epsg})))"
            elif QKan.config.database.type == enums.QKanDBChoice.POSTGIS:
                geop = f"ST_SetSRID(ST_MakePoint({xsch}, {ysch}), {self.epsg})"
            else:
                fehlermeldung(
                    "Programmfehler!",
                    "Datenbanktyp ist fehlerhaft {}!\nAbbruch!".format(
                        QKan.config.database.type
                    ),
                )

            du = 1.0

            sql = f"""
                UPDATE schaechte SET (xsch, ysch, geom, geop) =
                (?, ?, ?, ?)
                WHERE schnam = ?
                """
            if not self.dbQK.sql(sql, parameters=(xsch, ysch, geom, geop, name)):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def subcatchments(self) -> bool:
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
                VALUES (?, ?, ?, ?, ?)
                """
            if not self.dbQK.sql(
                sql, parameters=(name, regenschreiber, schnam, befgrad, neigung)
            ):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

    def polygons(self) -> bool:
        """Liest die Polygone zu den bereits angelegten tezg-Flächen ein"""

        data = self.data.get("polygons", [])
        data.append("ende")  # Trick, damit am Ende das letzte Polygon geschrieben wird

        nampoly = ""  # Solange der Name gleich bleibt, gehören
        # die Eckpunkte zum selben Polygon (tezg-Fläche)

        xlis: List[float] = []  # x-Koordinaten zum Polygon
        ylis: List[float] = []  # y-Koordinaten zum Polygon
        for line in data:
            name = line[0:17].strip()  # schnam
            xsch = fzahl(line[17:36].strip(), 3, self.xoffset) + self.xoffset  # xsch
            ysch = fzahl(line[36:54].strip(), 3, self.yoffset) + self.yoffset  # ysch

            if nampoly != name:
                if nampoly != "":
                    # Koordinaten des ersten Punkte am Ende nochmal anhängen
                    xlis.append(xlis[0])
                    ylis.append(ylis[0])

                    # Polygon schreiben
                    coords = ", ".join([f"{x} {y}" for x, y in zip(xlis, ylis)])
                    geom = f"GeomFromText('MULTIPOLYGON((({coords})))', {self.epsg})"
                    if not self.dbQK.sql(
                        "UPDATE tezg SET geom = ? WHERE flnam = ?",
                        mute_logger=True,
                        parameters=(geom, nampoly),
                    ):
                        del self.dbQK
                        return False
                nampoly = name

                # Listen zurücksetzen
                xlis = []
                ylis = []
            if name == "ende":
                continue  # Letzte Zeile ist nur ein dummy

            # Koordinaten des Eckpunktes übernehmen
            xlis.append(xsch)
            ylis.append(ysch)

        self.dbQK.commit()

        return True

    def conduits(self) -> bool:
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
                VALUES (?, ?, ?, ?, ?, 'Regenwasser', 'vorhanden')
                """
            if not self.dbQK.sql(
                sql, parameters=(haltnam, schoben, schunten, laenge, mannings_n)
            ):
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

    def vertices(self) -> bool:
        data = self.data.get("vertices", [])
        data.append("ende")  # Trick, damit am Ende das letzte Polygon geschrieben wird

        namvor = ""  # Solange der Name gleich bleibt, gehören
        # die Eckpunkte zur selben Haltung
        npt = 2  # Punkt, der eingefügt werden muss

        for line in data:
            name = line[0:17].strip()  # schnam
            xsch = fzahl(line[17:37].strip(), 3, self.xoffset) + self.xoffset  # xsch
            ysch = fzahl(line[36:56].strip(), 3, self.yoffset) + self.yoffset  # ysch

            if name == namvor:
                npt += 1
            else:
                npt = 2

            sql = f"""
                UPDATE haltungen SET geom = AddPoint(geom, MakePoint(?, ?, ?), ?)
                WHERE halnam = ?
                """

            if not self.dbQK.sql(
                sql, mute_logger=True, parameters=(xsch, ysch, self.epsg, npt, name)
            ):
                del self.dbQK
                return False

            namvor = name

        self.dbQK.commit()

        return True

    def xsections(self) -> bool:
        """Liest die Profildaten zu den Haltungen ein. Dabei werden sowohl Haltungsdaten ergänzt
        als auch Profildaten erfasst"""

        profiltypes = {"CIRCULAR": "Kreisquerschnitt"}

        data = self.data.get("xsections", [])
        for line in data:
            # Attribute bitte aus qkan.database.qkan_database.py entnehmen
            haltnam = line[0:17].strip()
            xsection = line[17:30].strip()  # shape
            hoehe = line[30:47].strip()  # Geom1
            breite = line[47:58].strip()  # Geom2
            barrels = line[
                80:91
            ].strip()  # Falls > 1, muss die Haltung mehrfach angelegt werden

            if xsection == "IRREGULAR":
                hoehe = "NULL"
                breite = "NULL"

            if xsection in profiltypes:
                profilnam = profiltypes[xsection]
            else:
                profilnam = "Kreisquerschnitt"

            sql = f"""
                UPDATE haltungen SET (profilnam, hoehe, breite) = (?, ?, ?)
                WHERE haltnam = ?
                """
            if not self.dbQK.sql(sql, parameters=(profilnam, hoehe, breite, haltnam)):
                del self.dbQK
                return False

        self.dbQK.commit()

        return True

        # todo: SQL-Anweisung wie oben ergänzen

    def writeProjektfile(self) -> bool:
        # --------------------------------------------------------------------------
        # Zoom-Bereich für die Projektdatei vorbereiten
        sql = """SELECT min(x(geop)) AS xmin, 
                        max(x(geop)) AS xmax, 
                        min(y(geop)) AS ymin, 
                        max(y(geop)) AS ymax
                 FROM schaechte"""
        try:
            if not self.dbQK.sql(sql, "importkanaldaten_swmm (17)"):
                del self.dbQK
                return False
        except BaseException as e:
            fehlermeldung("SQL-Fehler", str(e))
            fehlermeldung(
                "Fehler in QKan_Import_from_KP",
                "\nFehler in sql_zoom: \n" + sql + "\n\n",
            )

        try:
            zoom = self.dbQK.fetchone()
        except BaseException as e:
            fehlermeldung("SQL-Fehler", str(e))
            fehlermeldung(
                "Fehler in QKan_Import_from_KP",
                "\nFehler in sql_zoom;\n",
            )
            zoom = [0.0, 100.0, 0.0, 100.0]

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
            crs = QgsCoordinateReferenceSystem(
                srid, QgsCoordinateReferenceSystem.EpsgCrsId
            )
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
                "\nFehler bei der Ermittlung der srid: \n",
            )

        # --------------------------------------------------------------------------
        # Projektdatei schreiben, falls ausgewählt

        if self.projectfile is not None and self.projectfile != "":
            templatepath = os.path.join(pluginDirectory("qkan"), "templates")
            projecttemplate = os.path.join(templatepath, "projekt.qgs")
            projectpath = os.path.dirname(self.projectfile)
            if os.path.dirname(self.database_QKan) == projectpath:
                datasource = self.database_QKan.replace(
                    os.path.dirname(self.database_QKan), "."
                )
            else:
                datasource = self.database_QKan

            # Lesen der Projektdatei ------------------------------------------------------------------
            qgsxml = ET.parse(projecttemplate)
            root = qgsxml.getroot()

            # Projektionssystem anpassen --------------------------------------------------------------

            for tag_maplayer in root.findall(".//projectlayers/maplayer"):
                tag_datasource = tag_maplayer.find("./datasource")
                if not tag_datasource:
                    continue

                tex = tag_datasource.text
                if not tex:
                    continue

                # Nur QKan-Tabellen bearbeiten
                if tex[tex.index('table="') + 7 :].split('" ')[0] in QKAN_TABLES:

                    # <extend> löschen
                    for tag_extent in tag_maplayer.findall("./extent"):
                        tag_maplayer.remove(tag_extent)

                    for tag_spatialrefsys in tag_maplayer.findall(
                        "./srs/spatialrefsys"
                    ):
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
            for tag_maplayer in root.findall(".//projectlayers/maplayer"):
                tag_editform = tag_maplayer.find("./editform")
                if tag_editform and tag_editform.text:
                    dateiname = os.path.basename(tag_editform.text)
                    if dateiname in QKAN_FORMS:
                        # Nur QKan-Tabellen bearbeiten
                        tag_editform.text = os.path.join(formspath, dateiname)

            # Zoom für Kartenfenster einstellen -------------------------------------------------------
            if len(zoom) == 0 or any([x is None for x in zoom]):
                zoom = [0.0, 100.0, 0.0, 100.0]

            for extent in root.findall(".//mapcanvas/extent"):
                for idx, name in enumerate(["xmin", "ymin", "xmax", "ymax"]):
                    element = extent.find(f"./{name}")
                    if element is not None:
                        element.text = "{:.3f}".format(zoom[idx])

            # Projektionssystem anpassen --------------------------------------------------------------

            for tag_spatialrefsys in root.findall(".//projectCrs/spatialrefsys"):
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

            for tag_datasource in root.findall(".//projectlayers/maplayer/datasource"):
                text = tag_datasource.text

                if not text:
                    continue

                tag_datasource.text = (
                    "dbname='" + datasource + "' " + text[text.find("table=") :]
                )

            qgsxml.write(self.projectfile)  # writing modified project file
            logger.debug("Projektdatei: {}".format(self.projectfile))
            # logger.debug(u'encoded string: {}'.format(tex))
        return True

    def subareas(self) -> None:
        pass  # in QKan nicht verwaltet

    def symbols(self) -> None:
        pass  # in QKan nicht verwaltet

    def coverages(self) -> None:
        pass  # in QKan nicht verwaltet

    def evaporation(self) -> None:
        pass  # in QKan nicht verwaltet

    def raingages(self) -> None:
        pass  # in QKan nicht verwaltet

    def infiltration(self) -> None:
        pass  # in QKan nicht verwaltet

    def pollutants(self) -> None:
        pass  # in QKan nicht verwaltet

    def landuses(self) -> None:
        pass  # in QKan nicht verwaltet

    def loadings(self) -> None:
        pass  # in QKan nicht verwaltet

    def buildup(self) -> None:
        pass  # in QKan nicht verwaltet

    def washoff(self) -> None:
        pass  # in QKan nicht verwaltet

    def timeseries(self) -> None:
        pass  # in QKan nicht verwaltet

    def report(self) -> None:
        pass  # in QKan nicht verwaltet

    def tags(self) -> None:
        pass  # in QKan nicht verwaltet

    def map(self) -> None:
        pass  # in QKan nicht verwaltet


def importKanaldaten(
    inpfile: str, database_qkan: str, projectfile: str, epsg: int = 25832
) -> bool:
    """Ruft die Klasse SWMM zur Verarbeitung der Daten auf"""

    if not os.path.exists(inpfile):
        return False

    swmm = SWMM(
        inpfile,
        database_qkan,
        projectfile,
        offset=[0.0, 0.0],
        epsg=epsg,
        dbtyp="SpatiaLite",
    )

    if not swmm.connected:
        return False

    swmm.read()

    print(swmm.title)
    # print(swmm.options)        # wird nicht benötigt

    if not swmm.junctions():
        fehlermeldung("Fehler in importKanaldaten", "junctions()")
    if not swmm.outfalls():
        fehlermeldung("Fehler in importKanaldaten", "outfalls()")
    if not swmm.coordinates():
        fehlermeldung("Fehler in importKanaldaten", "coordinates()")
    if not swmm.conduits():
        fehlermeldung("Fehler in importKanaldaten", "conduits()")
    if not swmm.xsections():
        fehlermeldung("Fehler in importKanaldaten", "xsections()")
    if not swmm.subcatchments():
        fehlermeldung("Fehler in importKanaldaten", "subcatchments()")
    if not swmm.polygons():
        fehlermeldung("Fehler in importKanaldaten", "polygons()")

    # from pprint import pprint

    # pprint(swmm.data)

    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

    template_project = Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
    qgsadapt(str(template_project), database_qkan, swmm.dbQK, projectfile, epsg)

    # noinspection PyArgumentList
    project = QgsProject.instance()
    project.read(projectfile)
    project.reloadAllLayers()

    # swmm.writeProjektfile()

    del swmm

    return True


if __name__ == "__main__" or __name__ == "console":
    # importKanaldaten("tutorial.inp", "sqlcommands.sql")
    pass
