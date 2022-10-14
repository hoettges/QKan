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
        template: str,
        liste_teilgebiete: List[str],
        status: str,
        epsg: int = 25832,
    ):
        self.epsg = epsg
        self.inpobject = Path(inpfile)
        self.data: Dict[str, List[str]] = {}
        self.db_qkan = db_qkan
        self.projectfile = projectfile
        self.template = template
        #self.xoffset, self.yoffset = offset
        self.xoffset, self.yoffset = 100,100
        self.liste_teilgebiete = liste_teilgebiete
        self.status = status

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

    def __del__(self) -> None:
        self.dbQK.sql("SELECT RecoverSpatialIndex()")
        del self.dbQK

    def insertfunk(self, search_phrase, value):

        line_num = 0
        line_num2 = 0
        z = 0
        z2 = 0
        x = False
        with open(self.ergfileSwmm, 'r') as f:
            liste = [line for line in f.readlines()]
        for line in liste:
            line_num += 1
            line_num2 += 1
            if line.find(search_phrase) >= 0:
                z = line_num
                x = True

            if len(line.strip()) == 0 and x:
                z2 = line_num2
                break

        if z == 0:
            return False

        if self.status == 'append':
            liste.insert(line_num2 - 1, value)
        if self.status == 'update':
            #liste[line_num + 3:line_num2] = [value]
            value += '\n'
            liste[z+3:z2] = [value]
        else:
            pass
        with open(self.ergfileSwmm, 'w') as f:
            # schreibt an richtige stelle die daten (ergänzen)
            f.writelines(liste)



    def run(self) -> bool:
        self.exportKanaldaten()
        self.title()
        self.raingages()
        self.subcatchments()
        self.subareas()
        self.infiltration()
        self.junctions()
        self.outfalls()
        self.storage()
        self.conduits()
        self.pumps()
        self.weirs()
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


        # Verbindung zur Spatialite-Datenbank mit den Kanaldaten

        dbQK=self.dbQK
        if not dbQK.connected:
            logger.error(
                """Fehler in exportSwmm:
                QKan-Datenbank {databaseQKan} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"""
            )
            return None

        file_to_delete = open(ergfileSwmm, 'w')
        file_to_delete.close()

    def title(self):
        self.file = open(self.ergfileSwmm, 'a')

        if self.status == 'new':
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

        elif self.status == 'append' or self.status == 'update':
            with open(self.template) as f:
                lines = [line for line in f.readlines()]
                with open(self.ergfileSwmm, "w") as f2:
                    f2.writelines(lines)

        else:
            pass

    def raingages(self):

        if self.status == 'new':

            text = ("\n[RAINGAGES]"
                    "\n;;               Rain      Time   Snow   Data"
                    "\n;;Name           Type      Intrvl Catch  Source"
                    "\n;;-------------- --------- ------ ------ ----------"
                    "\n"
                    )
            self.file = open(self.ergfileSwmm, 'a')
            self.file.write(text)
            self.file.close()
        else:
            pass

    def subcatchments(self):

        if QKan.config.check_export.flaechen:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND tg.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

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
                                        {auswahl}"""

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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[SUBCATCHMENTS]", datasc)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[SUBCATCHMENTS]", datasc) is False):

                text = ("\n[SUBCATCHMENTS]"
                        "\n;;                                                 Total    Pcnt.             Pcnt.    Curb     Snow"
                        "\n;;Name           Raingage         Outlet           Area     Imperv   Width    Slope    Length   Pack"
                        "\n;;-------------- ---------------- ---------------- -------- -------- -------- -------- -------- --------"
                        "\n"
                        )
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(datasc)

                self.file.close()

            else:
                pass


    def subareas(self):

        if QKan.config.check_export.flaechen:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND tg.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

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
                                        {auswahl}"""

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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[SUBAREAS]", datasa)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[SUBAREAS]", datasa) is False):

                text = ("\n[SUBAREAS]"
                        "\n;;Subcatchment   N-Imperv   N-Perv     S-Imperv   S-Perv     PctZero    RouteTo    PctRouted"
                        "\n;;-------------- ---------- ---------- ---------- ---------- ---------- ---------- ----------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(datasa)
                self.file.close()

            else:
                pass


    def infiltration(self):

        if QKan.config.check_export.flaechen:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND tg.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

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
                                                {auswahl}"""

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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[INFILTRATION]", datain)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[INFILTRATION]", datain) is False):

                text = ("\n[INFILTRATION]"
                        "\n;;Subcatchment   MaxRate    MinRate    Decay      DryTime    MaxInfil"
                        "\n;;-------------- ---------- ---------- ---------- ---------- ----------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(datain)
                self.file.close()

            else:
                pass


    def junctions(self):

        if QKan.config.check_export.schaechte:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                        s.schnam AS name, 
                                        s.sohlhoehe AS invertElevation, 
                                        s.deckelhoehe - s.sohlhoehe AS maxDepth, 
                                        0 AS initDepth, 
                                        0 AS surchargeDepth,
                                        0 AS pondedArea,   
                                        X(geop) AS xsch, Y(geop) AS ysch 
                                    FROM schaechte AS s
                                    WHERE s.schachttyp = 'Schacht'
                                    {auswahl}"""

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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[JUNCTIONS]", dataju)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[JUNCTIONS]", dataju) is False):

                text = ("\n[JUNCTIONS]"
                        "\n;;               Invert     Max.       Init.      Surcharge  Ponded"
                        "\n;;Name           Elev.      Depth      Depth      Depth      Area"
                        "\n;;-------------- ---------- ---------- ---------- ---------- ----------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(dataju)
                self.file.close()

            else:
                pass


    def outfalls(self):

        if QKan.config.check_export.auslaesse:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                                s.schnam AS name, 
                                                s.sohlhoehe AS invertElevation, 
                                                s.deckelhoehe - s.sohlhoehe AS maxDepth, 
                                                0 AS initDepth, 
                                                0 AS surchargeDepth,
                                                0 AS pondedArea,   
                                                X(geop) AS xsch, Y(geop) AS ysch 
                                            FROM schaechte AS s
                                            WHERE s.schachttyp = 'Auslass'
                                            {auswahl}"""

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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[OUTFALLS]", dataou)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[OUTFALLS]", dataou) is False):

                text = ("\n[OUTFALLS]"
                        "\n;;               Invert     Outfall    Stage/Table      Tide"
                        "\n;;Name           Elev.      Type       Time Series      Gate"
                        "\n;;-------------- ---------- ---------- ---------------- ----"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(dataou)
                self.file.close()

            else:
                pass

    def storage(self):

        if QKan.config.check_export.speicher:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                                s.schnam AS name, 
                                                s.sohlhoehe AS invertElevation, 
                                                s.deckelhoehe - s.sohlhoehe AS maxDepth, 
                                                0 AS initDepth, 
                                                0 AS surchargeDepth,
                                                0 AS pondedArea,   
                                                X(geop) AS xsch, Y(geop) AS ysch 
                                            FROM schaechte AS s
                                            WHERE s.schachttyp = 'Speicher'
                                            {auswahl}"""

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
                    f"{name:<16s} {invertElevation:<8.1f} {maxDepth:<10.3f} {initDepth:<10.3f} FUNCTIONAL 1000      0         0        0        0\n"
                )

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[STORAGE]", dataou)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[STORAGE]", dataou) is False):

                text = ("\n[STORAGE]"
                        "\n;;Name           Elev.    MaxDepth   InitDepth  Shape      Curve Name/Params            N/A      Fevap    Psi      Ksat     IMD "
                        "\n;;-------------- -------- ---------- ----------- ---------- ---------------------------- -------- --------          -------- --------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(dataou)
                self.file.close()

            else:
                pass

    def conduits(self):

        if QKan.config.check_export.haltungen:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND haltungen.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                        h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, h.haltungstyp
                                    FROM
                                        haltungen AS h
                                    WHERE h.haltungstyp IS 'Haltung'
                                    {auswahl}"""
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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[CONDUITS]", datacd)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[CONDUITS]", datacd) is False):

                text = ("\n[CONDUITS]"
                        "\n;;               Inlet            Outlet                      Manning    Inlet      Outlet     Init.      Max."
                        "\n;;Name           Node             Node             Length     N          Offset     Offset     Flow       Flow"
                        "\n;;-------------- ---------------- ---------------- ---------- ---------- ---------- ---------- ---------- ----------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(datacd)
                self.file.close()

            else:
                pass

    def pumps(self):

        if QKan.config.check_export.pumpen:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND haltungen.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                        h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, h.haltungstyp
                                    FROM
                                        haltungen AS h
                                    WHERE h.haltungstyp IS 'Pumpe'
                                    {auswahl}"""
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
                    f"{name:<16s} {schoben:<17s}{schunten:<17s} *                ON       0        0     \n"
                )

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[PUMPS]", datacd)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[PUMPS]", datacd) is False):

                text = ("\n[PUMPS]"
                        "\n;;Name           From Node        To Node          Pump Curve       Status   Sartup Shutoff "
                        "\n;;-------------- ---------------- ---------------- ---------------- ------ -------- --------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(datacd)
                self.file.close()

            else:
                pass


    def weirs(self):

        if QKan.config.check_export.wehre:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                        h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, h.haltungstyp
                                    FROM
                                        haltungen AS h
                                    WHERE h.haltungstyp IS 'Wehr'
                                    {auswahl}"""
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
                    f"{name:<16s} {schoben:<17s}{schunten:<17s} TRANSVERSE   0          3.33       NO       0        0          YES   \n"
                )

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[WEIRS]", datacd)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[WEIRS]", datacd) is False):

                text = ("\n[WEIRS]"
                        "\n;;Name           From Node        To Node          Type         CrestHt    Qcoeff     Gated    EndCon   EndCoeff   Surcharge  RoadWidth  RoadSurf   Coeff. Curve"
                        "\n;;-------------- ---------------- ---------------- ------------ ---------- ---------- -------- -------- ---------- ---------- ---------- ---------- ----------------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(datacd)
                self.file.close()

            else:
                pass

    def xsection(self):

        if QKan.config.check_export.haltungen:

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" WHERE h.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                        h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, h.haltungstyp
                                    FROM
                                        haltungen AS h
                                    JOIN
                                        teilgebiete AS g
                                    ON 
                                        Intersects(h.geom,g.geom) and h.haltungstyp IS 'Haltung'
                                    GROUP BY h.haltnam
                                    {auswahl}"""
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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[XSECTIONS]", dataxs)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[XSECTIONS]", dataxs) is False):

                text = ("\n[XSECTIONS]"
                        "\n;;Link           Shape        Geom1            Geom2      Geom3      Geom4      Barrels"
                        "\n;;-------------- ------------ ---------------- ---------- ---------- ---------- ----------"
                        "\n"
                        )
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(dataxs)
                self.file.close()

            else:
                pass


    def transects(self):

        if self.status == 'new':

            text = ("\n[TRANSECTS]"
                    "\n")

        else:
            pass

    def losses(self):

        if self.status == 'new':

            text = ("\n[LOSSES]"
                    "\n;;Link           Inlet      Outlet     Average    Flap Gate"
                    "\n;;-------------- ---------- ---------- ---------- ----------"
                    "\n")
            self.file = open(self.ergfileSwmm, 'a')
            self.file.write(text)
            self.file.close()

        else:
            pass

    def timeseries(self):

        if self.status == 'new':

            text = ("\n[TIMESERIES]"
                    "\n;;Name           Date       Time       Value"
                    "\n;;-------------- ---------- ---------- ----------"
                    "\n"
                    )
            self.file = open(self.ergfileSwmm, 'a')
            self.file.write(text)
            self.file.close()

        else:
            pass

    def report(self):

        if self.status == 'new':

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

        else:
            pass

    def tags(self):

        if self.status == 'new':

            #sind die Infos enthalten in QKan?

            text = ("\n[TAGS]"
                    "\n")
            self.file = open(self.ergfileSwmm, 'a')
            self.file.write(text)
            self.file.close()

        else:
            pass

    def map(self):

        if self.status == 'new':

            text = ("\n[MAP]\n")
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

        else:
            pass


    def coordinates(self):

        if QKan.config.check_export.schaechte:

            dataco = ""  # Datenzeilen [COORDINATES]
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                        s.schnam AS name,   
                                        X(s.geop) AS xsch, 
                                        Y(s.geop) AS ysch 
                                    FROM schaechte AS s
                                    WHERE s.schachttyp = 'Schacht'
                                    {auswahl}"""

            if not self.dbQK.sql(sql, "dbQK: exportSWMM (3)"):
                del self.dbQK
                return

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

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[COORDINATES]", dataco)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[COORDINATES]", dataco) is False):

                text = ("\n[COORDINATES]"
                        "\n;;Node           X-Coord            Y-Coord"
                        "\n;;-------------- ------------------ ------------------"
                        "\n"
                        )
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(dataco)
                self.file.close()

            else:
                pass

    def vertices(self):

        if QKan.config.check_export.haltungen:
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND haltungen.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                    h.haltnam, h.schoben, h.schunten, ST_AsText(h.geom)
                                    from haltungen AS h
                                    WHERE h.haltungstyp IS 'Haltung'
                                    {auswahl}"""
            self.dbQK.sql(sql)

            dataver = ""

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
                    while x + 2 <= len(liste) and x < len(liste) - 2:
                        xsch = float(liste[x])
                        ysch = float(liste[x + 1])
                        x += 2

                        dataver += f"{name:<16s} {xsch:<18.3f} {ysch:<18.3f}\n"

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[VERTICES]", dataver)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[VERTICES]", dataver) is False):

                text = ("\n[VERTICES]"
                        "\n;;Link           X-Coord            Y-Coord"
                        "\n;;-------------- ------------------ ------------------"
                        "\n")
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(dataver)
                self.file.close()

            else:
                pass

    def polygons(self):

        # Koordinaten fehlen die Nachkommerstellen!!!

        # nicht als wkt sondern als geojson in sqlite schreiben
        # Update
        # tezg
        # set
        # geom = AsText(GeomFromGeoJSON(
        #     '{
        #     "type": "Multipolygon",
        #             "coordinates": [[[[281.9999999999999, 1334], [111, 1100.999999999999],
        #                               [171.9999999999999, 1062], [231, 1026.999999999999], [306, 990],
        #                               [370, 958.9999999999999], [408.9999999999999, 946], [444, 935.9999999999999],
        #                               [492.9999999999999, 924], [532, 915], [569, 907], [609.9999999999999, 897],
        #                               [654.9999999999999, 897], [683.9999999999999, 1318],
        #                               [650.9999999999999, 1320.999999999999], [595.9999999999999, 1332],
        #                               [550.9999999999999, 1346], [495, 1366.999999999999],
        #                               [454.9999999999999, 1383.999999999999],
        #                               [409.9999999999999, 1408.999999999999], [385.9999999999999, 1427],
        #                               [362.9999999999999, 1441.999999999999], [281.9999999999999, 1334]]]]}'))

        if QKan.config.check_export.flaechen:

            dataver = ""

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" WHERE tg.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            sql = f"""SELECT
                                    tg.flnam, tg.schnam, st_astext(tg.geom)
                                    from tezg AS tg
                                    {auswahl}"""
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
                    while x + 2 <= len(liste) and x < len(liste) - 2:
                        xsch = float(liste[x])
                        ysch = float(liste[x + 1])
                        x += 2

                        dataver += f"{name:<16s} {xsch:<18.3f} {ysch:<18.3f}\n"

            if self.status == 'append' or self.status == 'update':
                self.insertfunk("[Polygons]", dataver)

            if self.status == 'new' or (self.status == 'append' and self.insertfunk("[Polygons]", dataver) is False):
                text = ("\n[Polygons]"
                        "\n;;Subcatchment   X-Coord            Y-Coord"
                        "\n;;-------------- ------------------ ------------------"
                        "\n"
                        )
                self.file = open(self.ergfileSwmm, 'a')
                self.file.write(text)

                self.file.write(dataver)
                self.file.close()

            else:
                pass


    def symbols(self):

        if self.status == 'new':

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

        else:
            pass

    def labels(self):

        if self.status == 'new':

            text = ('\n[LABELS]'
                '\n;;X-Coord          Y-Coord            Label'
                  "\n")
            self.file = open(self.ergfileSwmm, 'a')
            self.file.write(text)
            self.file.close()

        else:
            pass

    def backdrop(self):

        if self.status == 'new':

            text = ("\n[BACKDROP]"
                "\n"
                    )
            self.file = open(self.ergfileSwmm, 'a')
            self.file.write(text)
            self.file.close()

        else:
            pass
