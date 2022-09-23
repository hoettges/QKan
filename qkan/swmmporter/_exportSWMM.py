# -*- coding: utf-8 -*-

import os
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, cast
from lxml import etree
from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.utils import pluginDirectory, iface
from qgis.PyQt.QtWidgets import QProgressBar
from qkan import QKan, enums
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.tools.k_qgsadapt import qgsadapt
import math

logger = logging.getLogger("QKan.exportswmm")


progress_bar = None

# --------------------------------------------------------------------------------------------------
# Start des eigentlichen Programms

# MOUSE-Haltungstyp: 1 = Kreis, 2 = Profil (CRS), 3 = Rechteck, 4 = Maulprofil, 5 = Eiprofil, 6 = Quadrat, 7 = "Natural Channel"

ref_profile = {"1": "CIRCULAR", "3": "RECT_CLOSED", "5": "EGG"}


class ExportTask:
    def __init__(
        self,
        inpfile: str,
        db_qkan: DBConnection,
        projectfile: str,
        liste_teilgebiete: List[str],
        epsg: int = 25832,
    ):
        self.epsg = epsg
        #self.dbtyp = dbtyp
        self.inpobject = Path(inpfile)
        self.data: Dict[str, List[str]] = {}
        self.db_qkan = db_qkan
        self.projectfile = projectfile
        #self.xoffset, self.yoffset = offset
        self.xoffset, self.yoffset = 100,100
        self.liste_teilgebiete = liste_teilgebiete

        #self.dbQK = DBConnection(
        #    dbname=database_qkan, epsg=epsg
        #)  # Datenbankobjekt der QKan-Datenbank zum Schreiben
        self.dbQK = db_qkan

        self.connected = self.dbQK.connected

        self.ergfileSwmm = self.projectfile
        self.file=None

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in import_from_swmm:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    db_qkan
                ),
            )

        if len(liste_teilgebiete) != 0:
            self.auswahlw = " WHERE teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            self.auswahlw = ""
        self.auswahlw.replace(" WHERE teilgebiet ", " AND teilgebiet ")


    def __del__(self) -> None:
        self.dbQK.sql("SELECT RecoverSpatialIndex()")
        del self.dbQK

    def run(self) -> bool:
        self.exportKanaldaten()
        self.raingages()
        self.subcatchments()
        self.subareas()
        self.infiltration()
        self.junctions()
        self.outfalls()
        self.conduits()
        self.xsection()
        self.transects()
        self.losses()
        self.timeseries()
        self.report()
        self.tags()
        self.map()
        self.coordinates()
        self.vertices()
        self.polygons()
        self.symbols()
        self.labels()
        self.backdrop()
        return True


    def exportKanaldaten(
        self
    ) -> None:
        """
        :iface:                 QGIS-Interface zur GUI
        :type:                  QgisInterface

        :databaseQKan:         Pfad zur QKan-Datenbank
        :type:                  string

        :templateSwmm:          Vorlage für die zu erstellende SWMM-Datei
        :type:                  string

        :ergfileSwmm:           Ergebnisdatei für SWMM
        :type:                  string

        :liste_teilgebiete:     Liste der ausgewählten Teilgebiete
        :type:                  string
        """

        # fortschritt('Start...',0.02)

        # --------------------------------------------------------------------------------------------------
        # Zuordnungstabellen. Profile sind in einer json-Datei gespeichert, die sich auf dem
        # Roaming-Verzeichnis befindet (abrufbar mit site.getuserbase()
        # Andere Tabellen sind in diesem Quellcode integriert, wie z. B. ref_typen

        databaseQKan=self.db_qkan
        templateSwmm=self.inpobject
        ergfileSwmm=self.projectfile
        liste_teilgebiete=self.liste_teilgebiete

        iface = QKan.instance.iface

        # Create progress bar
        progress_bar = QProgressBar(iface.messageBar())
        progress_bar.setRange(0, 100)

        #status_message = iface.messageBar().createMessage(
        #    "", "Export in Arbeit. Bitte warten..."
        #)
        #status_message.layout().addWidget(progress_bar)
        #iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

        # Einlesen der Vorlagedatei

        with open(templateSwmm) as swvorlage:
            swdaten = swvorlage.read()

        # Verbindung zur Spatialite-Datenbank mit den Kanaldaten

        #dbQK = DBConnection(
        #    dbname=databaseQKan
        #)  # Datenbankobjekt der QKan-Datenbank zum Lesen
        dbQK=self.dbQK
        if not dbQK.connected:
            logger.error(
                """Fehler in exportSwmm:
                QKan-Datenbank {databaseQKan} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"""
            )
            return None

        file_to_delete = open(ergfileSwmm, 'w')
        file_to_delete.close()

        self.file = open(ergfileSwmm, 'a')

        allgemein = (
            "[TITLE]"
            "\nExample"
            "\nDual Drainage System"
            "\nFinal Design"
            "\n"
            "\n[OPTIONS]"
            "\nFLOW_UNITS           CFS"
            "\nINFILTRATION         HORTON"
            "\nFLOW_ROUTING         DYNWAVE"
            "\nSTART_DATE           01/01/2007"
            "\nSTART_TIME           00:00:00"
            "\nREPORT_START_DATE    01/01/2007"
            "\nREPORT_START_TIME    00:00:00"
            "\nEND_DATE             01/01/2007"
            "\nEND_TIME             12:00:00"
            "\nSWEEP_START          01/01"
            "\nSWEEP_END            12/31"
            "\nDRY_DAYS             0"
            "\nREPORT_STEP          00:01:00"
            "\nWET_STEP             00:01:00"
            "\nDRY_STEP             01:00:00"
            "\nROUTING_STEP         0:00:15"
            "\nALLOW_PONDING        NO"
            "\nINERTIAL_DAMPING     PARTIAL"
            "\nVARIABLE_STEP        0.75"
            "\nLENGTHENING_STEP     0"
            "\nMIN_SURFAREA         0"
            "\nNORMAL_FLOW_LIMITED  SLOPE"
            "\nSKIP_STEADY_STATE    NO"
            "\nFORCE_MAIN_EQUATION  H-W"
            "\nLINK_OFFSETS         DEPTH"
            "\nMIN_SLOPE            0"
            "\n"
            "\n[EVAPORATION]"
            "\n;;Type       Parameters"
            "\n;;---------- ----------"
            "\nCONSTANT     0.0"
            "\n"
            )
        self.file.write(allgemein)
        self.file.close()

    def raingages(self):

        text = ("\n[RAINGAGES]"
                "\n;;               Rain      Time   Snow   Data"
                "\n;;Name           Type      Intrvl Catch  Source"
                "\n;;-------------- --------- ------ ------ ----------"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def subcatchments(self):
        text = ("\n[SUBCATCHMENTS]"
                "\n;;                                                 Total    Pcnt.             Pcnt.    Curb     Snow"
                "\n;;Name           Raingage         Outlet           Area     Imperv   Width    Slope    Length   Pack"
                "\n;;-------------- ---------------- ---------------- -------- -------- -------- -------- -------- --------"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)

        sql = f"""
                    SELECT
                      tg.flnam AS name,
                      tg.regenschreiber AS rain_gage,
                      tg.schnam AS outlet,
                      area(tg.geom)/10000 AS area,
                      pow(area(tg.geom), 0.5)*1.3 AS width,
                      tg.befgrad AS imperv,
                      tg.neigung AS neigung
                      FROM tezg AS tg
                    {self.auswahlw}"""

        if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
            del self.dbQK
            return

        datasc = ""  # Datenzeilen [subcatchments]

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_1,
                rain_gage,
                outlet_1,
                area,
                width,
                imperv,
                neigung,
            ) = [0 if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_1.replace(" ", "_")
            outlet = outlet_1.replace(" ", "_")

            datasc += (
                f"{name:<16s} {rain_gage:<16s} {outlet:<16s} {area:<8.2f} "
                f"{imperv:<8.1f} {width:<8.0f} {neigung:<8.1f} 0                        \n"
            )

        self.file.write(datasc)

        self.file.close()


    def subareas(self):
        text = ("\n[SUBAREAS]"
                "\n;;Subcatchment   N-Imperv   N-Perv     S-Imperv   S-Perv     PctZero    RouteTo    PctRouted"
                "\n;;-------------- ---------- ---------- ---------- ---------- ---------- ---------- ----------"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)

        sql = f"""
                    SELECT
                        tg.flnam AS name,
                        tg.regenschreiber AS rain_gage,
                        tg.schnam AS outlet,
                        area(tg.geom)/10000. AS area,
                        pow(area(tg.geom), 0.5)*1.3 AS width,                        -- 1.3: pauschaler Faktor für SWMM
                        tg.befgrad AS imperv,
                        tg.neigung AS neigung,
                        tg.abflussparameter AS abflussparameter, 
                        apbef.rauheit_kst AS nImperv, 
                        apdur.rauheit_kst AS nPerv,
                        apbef.muldenverlust AS sImperv, 
                        apdur.muldenverlust AS sPerv,
                        apbef.pctZero AS pctZero, 
                        bk.infiltrationsrateende*60 AS maxRate,                     -- mm/min -> mm/h
                        bk.infiltrationsrateanfang*60 AS minRate,
                        bk.rueckgangskonstante/24. AS decay,                        -- 1/d -> 1/h 
                        1/(coalesce(bk.regenerationskonstante, 1./7.)) AS dryTime,   -- 1/d -> d , Standardwert aus SWMM-Testdaten
                        bk.saettigungswassergehalt AS maxInfil
                    FROM tezg AS tg
                    LEFT JOIN abflussparameter AS apbef
                    ON tg.abflussparameter = apbef.apnam and (apbef.bodenklasse IS NULL OR apbef.bodenklasse = '')
                    LEFT JOIN abflussparameter AS apdur
                    ON tg.abflussparameter = apdur.apnam and apdur.bodenklasse IS NOT NULL AND apdur.bodenklasse <> ''
                    LEFT JOIN bodenklassen AS bk
                    ON apdur.bodenklasse = bk.bknam
                    {self.auswahlw}"""

        if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
            del self.dbQK
            return

        datasa = ""  # Datenzeilen [subareas]

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_1,
                rain_gage,
                outlet_1,
                area,
                width,
                imperv,
                neigung,
                abflussparameter,
                nImperv,
                nPerv,
                sImperv,
                sPerv,
                pctZero,
                maxRate,
                minRate,
                decay,
                dryTime,
                maxInfil,
            ) = [0 if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_1.replace(" ", "_")
            outlet = outlet_1.replace(" ", "_")

            datasa += (
                f"{name:<16s} {nImperv:<10.3f} {nPerv:<10.2f} {sImperv:<10.2f} {sPerv:<10.1f} "
                f"{pctZero:<10.0f} OUTLET    \n"
            )

        self.file.write(datasa)
        self.file.close()


    def infiltration(self):
        text = ("\n[INFILTRATION]"
                "\n;;Subcatchment   MaxRate    MinRate    Decay      DryTime    MaxInfil"
                "\n;;-------------- ---------- ---------- ---------- ---------- ----------"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)

        sql = f"""
                            SELECT
                                tg.flnam AS name,
                                tg.regenschreiber AS rain_gage,
                                tg.schnam AS outlet,
                                area(tg.geom)/10000. AS area,
                                pow(area(tg.geom), 0.5)*1.3 AS width,                        -- 1.3: pauschaler Faktor für SWMM
                                tg.befgrad AS imperv,
                                tg.neigung AS neigung,
                                tg.abflussparameter AS abflussparameter, 
                                apbef.rauheit_kst AS nImperv, 
                                apdur.rauheit_kst AS nPerv,
                                apbef.muldenverlust AS sImperv, 
                                apdur.muldenverlust AS sPerv,
                                apbef.pctZero AS pctZero, 
                                bk.infiltrationsrateende*60 AS maxRate,                     -- mm/min -> mm/h
                                bk.infiltrationsrateanfang*60 AS minRate,
                                bk.rueckgangskonstante/24. AS decay,                        -- 1/d -> 1/h 
                                1/(coalesce(bk.regenerationskonstante, 1./7.)) AS dryTime,   -- 1/d -> d , Standardwert aus SWMM-Testdaten
                                bk.saettigungswassergehalt AS maxInfil
                            FROM tezg AS tg
                            LEFT JOIN abflussparameter AS apbef
                            ON tg.abflussparameter = apbef.apnam and (apbef.bodenklasse IS NULL OR apbef.bodenklasse = '')
                            LEFT JOIN abflussparameter AS apdur
                            ON tg.abflussparameter = apdur.apnam and apdur.bodenklasse IS NOT NULL AND apdur.bodenklasse <> ''
                            LEFT JOIN bodenklassen AS bk
                            ON apdur.bodenklasse = bk.bknam
                            {self.auswahlw}"""

        if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
            del self.dbQK
            return

        datain = ""  # Datenzeilen [infiltration]

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_1,
                rain_gage,
                outlet_1,
                area,
                width,
                imperv,
                neigung,
                abflussparameter,
                nImperv,
                nPerv,
                sImperv,
                sPerv,
                pctZero,
                maxRate,
                minRate,
                decay,
                dryTime,
                maxInfil,
            ) = [0 if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_1.replace(" ", "_")

            datain += f"{name:<16s} {maxRate:<10.1f} {minRate:<10.1f} {decay:<10.1f} {dryTime:<10.0f} {maxInfil}\n"

        self.file.write(datain)
        self.file.close()


    def junctions(self):
        text = ("\n[JUNCTIONS]"
                "\n;;               Invert     Max.       Init.      Surcharge  Ponded"
                "\n;;Name           Elev.      Depth      Depth      Depth      Area"
                "\n;;-------------- ---------- ---------- ---------- ---------- ----------"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)

        sql = """SELECT
                    s.schnam AS name, 
                    s.sohlhoehe AS invertElevation, 
                    s.deckelhoehe - s.sohlhoehe AS maxDepth, 
                    0 AS initDepth, 
                    0 AS surchargeDepth,
                    0 AS pondedArea,   
                    X(geop) AS xsch, Y(geop) AS ysch 
                FROM schaechte AS s
                WHERE s.schachttyp = 'Schacht'
                """

        if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
            del self.dbQK
            return

        dataju = ""  # Datenzeilen [JUNCTIONS]

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_t,
                invertElevation,
                maxDepth,
                initDepth,
                surchargeDepth,
                pondedArea,
                xsch,
                ysch,
            ) = [0 if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_t.replace(" ", "_")

            # [JUNCTIONS]
            dataju += (
                f"{name:<16s} {invertElevation:<10.3f} {maxDepth:<10.3f} {initDepth:<10.3f} "
                f"{surchargeDepth:<10.3f} {pondedArea:<10.1f}\n"
            )

        self.file.write(dataju)
        self.file.close()


    def outfalls(self):
        text = ("\n[OUTFALLS]"
                "\n;;               Invert     Outfall    Stage/Table      Tide"
                "\n;;Name           Elev.      Type       Time Series      Gate"
                "\n;;-------------- ---------- ---------- ---------------- ----"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)

        sql = """SELECT
                            s.schnam AS name, 
                            s.sohlhoehe AS invertElevation, 
                            s.deckelhoehe - s.sohlhoehe AS maxDepth, 
                            0 AS initDepth, 
                            0 AS surchargeDepth,
                            0 AS pondedArea,   
                            X(geop) AS xsch, Y(geop) AS ysch 
                        FROM schaechte AS s
                        WHERE s.schachttyp = 'Auslass'
                        """

        if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
            del self.dbQK
            return
        dataou = ""  # Datenzeilen [OUTFALLS]

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_t,
                invertElevation,
                maxDepth,
                initDepth,
                surchargeDepth,
                pondedArea,
                xsch,
                ysch,
            ) = [0 if el is None else el for el in b]

            name = name_t.replace(" ", "_")

            dataou += (
                f"{name:<16s} {invertElevation:<10.3f} FREE                        NO                       \n"
            )


        self.file.write(dataou)
        self.file.close()


    def conduits(self):
        text = ("\n[CONDUITS]"
                "\n;;               Inlet            Outlet                      Manning    Inlet      Outlet     Init.      Max."
                "\n;;Name           Node             Node             Length     N          Offset     Offset     Flow       Flow"
                "\n;;-------------- ---------------- ---------------- ---------- ---------- ---------- ---------- ---------- ----------"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)

        sql = """SELECT
                    h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, h.haltungstyp
                FROM
                    haltungen AS h
                WHERE h.haltungstyp IS 'Haltung'
                """
        if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
            del self.dbQK
            return

        datacd = ""  # Datenzeilen

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_t,
                schoben,
                schunten,
                laenge,
                ks,
                haltungstyp,
            ) = [0 if el is None else el for el in b]

            name = name_t.replace(" ", "_")

            datacd += (
                f"{name:<16s} {schoben:<17s}{schunten:<17s}{laenge:<11.3f}{ks:<10.3f} 0          0          0          0         \n"
            )

        self.file.write(datacd)
        self.file.close()


    def xsection(self):
        text = ("\n[XSECTIONS]"
                "\n;;Link           Shape        Geom1            Geom2      Geom3      Geom4      Barrels"
                "\n;;-------------- ------------ ---------------- ---------- ---------- ---------- ----------"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)

        sql = """SELECT
                    h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, h.haltungstyp
                FROM
                    haltungen AS h
                JOIN
                    teilgebiete AS g
                ON 
                    Intersects(h.geom,g.geom) and h.haltungstyp IS 'Haltung'
                GROUP BY h.haltnam"""
        if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
            del self.dbQK
            return

        dataxs = ""  # Datenzeilen

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen

            (
                name_t,
                schoben,
                schunten,
                laenge,
                ks,
                haltungstyp,
            ) = [0 if el is None else el for el in b]

            name = name_t.replace(" ", "_")

            dataxs += (
                f"{name:<16s} {schoben:<16s}{schunten:<<16s}{laenge:<10.3f}{ks:<10.3f}  0          0          1                    \n"
            )

        self.file.write(dataxs)
        self.file.close()


    def transects(self):
        text = ("\n[TRANSECTS]"
                "\n")

    def losses(self):
        text = ("\n[LOSSES]"
                "\n;;Link           Inlet      Outlet     Average    Flap Gate"
                "\n;;-------------- ---------- ---------- ---------- ----------"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def timeseries(self):
        text = ("\n[TIMESERIES]"
                "\n;;Name           Date       Time       Value"
                "\n;;-------------- ---------- ---------- ----------"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def report(self):
        text = ("\n[REPORT]"
                "\nINPUT      YES"
                "\nCONTROLS   NO"
                "\nSUBCATCHMENTS ALL"
                "\nNODES ALL"
                "\nLINKS ALL"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def tags(self):
        #sind die Infos enthalten in QKan?

        text = ("\n[TAGS]"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def map(self):
        text = ("\n[MAP]"
                "\nDIMENSIONS -0.123 0.000 1423.123 1475.000"
                "\nUnits      Feet"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        dataco=''
        list=''

        extent = iface.mapCanvas().extent()
        ext = str(extent)
        list = ext.replace('QgsRectangle:', '')
        list = list.replace(',', '')

        dataco += f"DIMENSIONS{list} \n"
        self.file.write(dataco)

        text = ("\nUnits      Feet"
                "\n")

        self.file.write(text)
        self.file.close()


    def coordinates(self):
        text = ("\n[COORDINATES]"
                "\n;;Node           X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        dataco = ""  # Datenzeilen [COORDINATES]

        sql = """SELECT
                    s.schnam AS name,   
                    X(geop) AS xsch, 
                    Y(geop) AS ysch 
                FROM schaechte AS s
                WHERE s.schachttyp = 'Schacht'
                """
        self.dbQK.sql(sql)

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_t,
                xsch,
                ysch,
            ) = [0 if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_t.replace(" ", "_")

            # [COORDINATES]
            dataco += f"{name:<16s} {xsch:<18.3f} {ysch:<18.3f}\n"

        self.file.write(dataco)
        self.file.close()

    def vertices(self):
        text = ("\n[VERTICES]"
                "\n;;Link           X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)


        sql = """SELECT
                h.haltnam, h.schoben, h.schunten, ST_AsText(h.geom)
                from haltungen AS h
                WHERE h.haltungstyp IS 'Haltung'
                """
        self.dbQK.sql(sql)

        dataver=""

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_t,
                schoben,
                schunten,
                list,
            ) = [0 if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_t.replace(" ", "_")

            list = list.replace('LINESTRING(', '')
            list = list.replace(')', '')
            list = list.replace(',', '')
            x = 2
            liste = list.split()
            for i in liste:
                while x + 2 <= len(liste) and x<len(liste)-2:
                    xsch = float(liste[x])
                    ysch = float(liste[x + 1])
                    x += 2

                    dataver += f"{name:<16s} {xsch:<18.3f} {ysch:<18.3f}\n"

        self.file.write(dataver)
        self.file.close()

    def polygons(self):
        #Koordinaten fehlen die Nachkommerstellen!!!

        text = ("\n[Polygons]"
                "\n;;Subcatchment   X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        dataver = ""

        sql = """SELECT
                tg.flnam, tg.schnam, st_astext(tg.geom)
                from tezg AS tg"""
        self.dbQK.sql(sql)

        for b in self.dbQK.fetchall():
            # In allen Feldern None durch NULL ersetzen
            (
                name_t,
                schoben,
                list,
            ) = [0 if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_t.replace(" ", "_")

            list = list.replace('MULTIPOLYGON(((', '')
            list = list.replace(')))', '')
            list = list.replace(',', '')
            x = 0
            liste = list.split()
            for i in liste:
                while x + 2 <= len(liste) and x<len(liste)-2:
                    xsch = float(liste[x])
                    ysch = float(liste[x + 1])
                    x += 2

                    dataver += f"{name:<16s} {xsch:<18.3f} {ysch:<18.3f}\n"

        self.file.write(dataver)
        self.file.close()


    def symbols(self):
        text = ("\n[SYMBOLS]"
                "\n;;Gage           X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

        # sql = """SELECT f.regnr FROM flaechen AS f
        # JOIN
        #     teilgebiete AS g
        # ON
        #     Intersects(f.geom,g.geom)
        # GROUP BY f.regnr"""
        #
        # self.dbQK.sql(sql)
        #
        # datarm = ""  # Datenzeilen
        # datasy = ""  # Datenzeilen
        #
        # for c in self.dbQK.fetchall():
        #
        #     datarm += (
        #         "{:<16d} INTENSITY 1:00     1.0      TIMESERIES TS1             \n".format(
        #             c[0]
        #         )
        #     )
        #     datasy += "{:<16d} 9999.999           9999.999          \n".format(c[0])
        #
        # swdaten = swdaten.replace("{RAINGAGES}\n", datarm)
        # swdaten = swdaten.replace("{SYMBOLS}\n", datasy)

    def labels(self):
        text = ('\n[LABELS]'
            '\n;;X-Coord          Y-Coord            Label'
              "\n")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def backdrop(self):
        text = ("\n[BACKDROP]"
            "\n"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()




