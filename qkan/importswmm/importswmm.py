# -*- coding: utf-8 -*-

import os
from pathlib import Path

__author__ = "Joerg Hoettges"
__date__ = "März 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"


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

def kstFromKr(kr):
    """Umrechnung des Wertes für die äquivalente Sandrauheit k in die Rauheit nach Manning-Strickler"""
    C_Chezy = 25.68
    erg = C_Chezy / kr ** (1/6)
    return erg

def krFromKst(kst):
    """Umrechnung des Wertes für die äquivalente Sandrauheit k in die Rauheit nach Manning-Strickler"""
    C_Chezy = 25.68
    erg = (C_Chezy / kst) ** 6
    return erg


class DBConnection():
    """Ersetzt während der Entwicklungszeit den Datenbankzugriff"""
    def __init__(self, dbname, epsg=25832):
        self.sqlobject = Path(dbname).open("w")
        self.connected = True

    def error(self, title, meldung):
        """Ersetzt während der Entwicklungszeit den logger-Befehl"""
        self.sqlobject.write(f"Fehler {title}: {meldung}")

    def sql(self, sqltext):
        """Führt den SQL-Befehl aus"""
        sql = sqltext.strip().replace("\n                ","\n")
        try:
            self.sqlobject.write(sql)
            self.sqlobject.write('\n\n')
        except BaseException as err:
            self.error(
                "dbfunc.DBConnection.sql: SQL-Fehler in {e}".format(e=sqlinfo),
                "{e}\n{s}".format(e=repr(err), s=sql),
            )
            return False

        return True

class SWMM():
    def __init__(self, inpfile, database_QKan, epsg=25832, dbtyp="SpatiaLite"):
        self.epsg = epsg
        self.dbtyp = dbtyp
        self.inpobject = Path(inpfile)
        self.data = {}

        self.dbQK = DBConnection(
            dbname=database_QKan, epsg=epsg
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in import_from_dyna:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return False

    # def __del__(self):
    #    del self.dbQK

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
                INSERT into schaechte (
                    schnam, sohlhoehe, deckelhoehe, ueberstauflaeche)
                VALUES (
                    '{name}', {elevation}, {elevation} + {maxdepth}, {areaPonded})
                """
            if not self.dbQK.sql(sql):
                del self.dbQK
                return False

        return True

    def coordinates(self):
        """Liest die Koordinaten zu den bereits angelegten Schaechten ein"""
        data = self.data.get("coordinates", [])
        for line in data:
            name = line[0:17].strip()           # schnam
            xsch = line[17:36].strip()          # xsch
            ysch = line[36:54].strip()          # ysch

            # Geo-Objekte erzeugen

            #if QKan.config.database.type == enums.QKanDBChoice.SPATIALITE:
            geop = f"MakePoint({xsch},{ysch},{self.epsg})"
            du = 1.0
            geom = f"CastToMultiPolygon(MakePolygon(MakeCircle({xsch}, {ysch}, {du}, {self.epsg})))"
            #elif QKan.config.database.type == enums.QKanDBChoice.POSTGIS:
            #    geop = f"ST_SetSRID(ST_MakePoint({xsch}, {ysch}), {self.epsg})"
            #else:
            #    fehlermeldung(
            #        "Programmfehler!",
            #        "Datenbanktyp ist fehlerhaft {}!\nAbbruch!".format(QKan.config.database.type),
            #    )

            sql = f"""
                UPDATE schaechte SET (
                    xsch, ysch, geom, geop) =
                (   {xsch}, {ysch}, {geom}, {geop})
                WHERE schnam = '{name}'
                """
            if not self.dbQK.sql(sql):
                del self.dbQK
                return False

        return True

    def subcatchments(self):
        """Liest einen Teil der Daten zu tezg-Flächen ein"""
        data = self.data.get("subcatchments", [])
        for line in data:
            # Attribute bitte aus qkan.database.qkan_database.py entnehmen
            name = line[0:0]
            regenschreiber = line[0:0]
            
            


    def polygons(self):
        """Liest die Polygone zu den bereits angelegten tezg-Flächen ein"""

        data = self.data.get("polygons", [])
        data.append('ende')                     # Trick, damit am Ende das letzte Polygon geschrieben wird
        
        nampoly = ''                            # Solange der Name gleich bleibt, gehören 
                                                # die Eckpunkte zum selben Polygon (tezg-Fläche)
        for line in data:
            name = line[0:17].strip()           # schnam
            xsch = line[17:36].strip()          # xsch
            ysch = line[36:54].strip()          # ysch

            if nampoly != name:
                if nampoly != '':
                    # Polygon schreiben
                    coords = ' '.join([f'{x},{y}' for x,y in zip(xlis, ylis)])
                    geom = f'MULTIPOLYGON((({coords})), {self.epsg})'
                    sql = f"""
                        UPDATE schaechte SET geom = {geom}
                        WHERE schnam = '{name}'
                        """
                    if not self.dbQK.sql(sql):
                        del self.dbQK
                        return False
                # Listen zurücksetzen
                xlis = []                               # x-Koordinaten zum Polygon
                ylis = []                               # y-Koordinaten zum Polygon
            if nampoly == 'ende':
                continue                                # Letzte Zeile ist nur ein dummy

            # Koordinaten des Eckpunktes übernehmen
            xlis.append(xsch)
            ylis.append(ysch)

        return True

    def conduits(self):
        """Liest einen Teil der Haltungsdaten ein"""

        data = self.data.get("conduits", [])
        for line in data:
            # Attribute bitte aus qkan.database.qkan_database.py entnehmen
            haltnam = line[0:0]
            schoben = line[0:0]
            schunten = line[0:0]
            laenge = line[0:0]
            
            # Rauheitsbeiwerte
            mannings_n = fzahl(line[0:0])
            kst = 1/mannings_n                      # interessant: die Einheit von mannings_n ist s/m**(1/3)!
            ks = f'{krFromKst(kst)}'

            # todo: SQL-Anweisung wie oben ergänzen

    def xsections(self):
        """Liest die Profildaten zu den Haltungen ein. Dabei werden sowohl Haltungsdaten ergänzt
        als auch Profildaten erfasst"""

        data = self.data.get("xsections", [])
        for line in data:
            # Attribute bitte aus qkan.database.qkan_database.py entnehmen
            haltnam = line[0:0]
            profilnam = line[0:0]               # shape
            hoehe = line[0:0]                   # Geom1
            breite = line[0:0]                  # Geom2
            barrels = line[0:0]                 # Falls > 1, muss die Haltung mehrfach angelegt werden
            
            # todo: SQL-Anweisung wie oben ergänzen

            
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

    def outfalls(self):
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

    def vertices(self):
        pass                    # in QKan nicht verwaltet

def readKanaldaten(inpfile: str, sqlcommandfile: str):
    """Ruft die Klasse SWMM zur Verarbeitung der Daten auf"""

    if not os.path.exists(inpfile):
        return False

    swmm = SWMM(inpfile, sqlcommandfile)
    swmm.read()

    print(swmm.title)
    #print(swmm.options)        # wird nicht benötigt

    if not swmm.junctions():
        fehlermeldung('Fehler in readKanaldaten', 'junctions()')
    if not swmm.coordinates():
        fehlermeldung('Fehler in readKanaldaten', 'coordinates()')
    if not swmm.polygons():
        fehlermeldung('Fehler in readKanaldaten', 'polygons()')

    # from pprint import pprint

    # pprint(swmm.data)


if __name__ == "__main__" or __name__ == "console":
    readKanaldaten("tutorial.inp", "sqlcommands.sql")
