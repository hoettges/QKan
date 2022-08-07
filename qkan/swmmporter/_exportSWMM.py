# -*- coding: utf-8 -*-

"""----------------------------------------------------------------------------------
/***************************************************************************
 k_qgsw
                                 A QGIS plugin
 Transfer von Kanaldaten aus QKan nach SWMM 5.0.1
                              -------------------
                            begin                : 2015-08-10
                            git sha              : $Format:%H$
                            copyright            : (C) 2015 by Jörg Höttges / FH Aachen
                            email                : hoettges@fh-aachen.de
 ***************************************************************************/

 Tool Name:   k_qgsw.py
 Source Name: k_qgsw.py
 Version:     1.0.0
 Date:        29.05.2016
 Author:      Joerg Hoettges
 Required Arguments:

Transfer von Kanaldaten aus QKan nach SWMM 5.0.1


----------------------------------------------------------------------------------"""

import os
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, cast
from lxml import etree
from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.utils import pluginDirectory
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
            "\n[TITLE]"
            "\nExample 7"
            "\nDual Drainage System"
            "\nFinal Design"
            "\n"
            "\n[OPTIONS]"
            "\nFLOW_UNITS           CFS"
            "\nINFILTRATION         HORTON"
            "\nFLOW_ROUTING         DYNWAVE"
            "\nSTART_DATE           01 / 01 / 2007"
            "\nSTART_TIME           00:00:00"
            "\nREPORT_START_DATE    01 / 01 / 2007"
            "\nREPORT_START_TIME    00:00:00"
            "\nEND_DATE             01 / 01 / 2007"
            "\nEND_TIME             12:00:00"
            "\nSWEEP_START          01 / 01"
            "\nSWEEP_END            12 / 31"
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
                "\nRainGage         INTENSITY 0:05   1.0    TIMESERIES 100-yr"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def subcatchments(self):
        text = ("\n[SUBCATCHMENTS]"
                "\n;;                                                 Total    Pcnt.             Pcnt.    Curb     Snow"
                "\n;;Name           Raingage         Outlet           Area     Imperv   Width    Slope    Length   Pack"
                "\n;;-------------- ---------------- ---------------- -------- -------- -------- -------- -------- --------"
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
                      tg.neigung AS neigung,
                      tg.abflussparameter AS abflussparameter, 
                      apbef.rauheit_kst AS nImperv, 
                      apdur.rauheit_kst AS nPerv,
                      apbef.muldenverlust AS sImperv, 
                      apdur.muldenverlust AS sPerv,
                      apbef.pctZero AS pctZero, 
                      bk.infiltrationsrateende*60 AS maxRate, -- mm/min -> mm/h
                      bk.infiltrationsrateanfang*60 AS minRate,
                      bk.rueckgangskonstante/24. AS decay, -- 1/d -> 1/h 
                      1/(coalesce(bk.regenerationskonstante, 1./7.)) AS dryTime, -- 1/d -> d , Standardwert aus SWMM-Testdaten
                      bk.saettigungswassergehalt AS maxInfil
                      FROM tezg AS tg
                      JOIN abflussparameter AS apbef
                      ON tg.abflussparameter = apbef.apnam and (apbef.bodenklasse IS NULL OR apbef.bodenklasse = '')
                      JOIN abflussparameter AS apdur
                      ON tg.abflussparameter = apdur.apnam and apdur.bodenklasse IS NOT NULL AND apdur.bodenklasse = ''
                      JOIN bodenklassen AS bk
                      ON apdur.bodenklasse = bk.bknam
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
            ) = ["NULL" if el is None else el for el in b]

            # In allen Namen Leerzeichen durch '_' ersetzen
            name = name_1.replace(" ", "_")
            outlet = outlet_1.replace(" ", "_")

            datasc += (
                f"{name:<16s} {rain_gage:<16s} {outlet:<16s} {area:<8.2f} "
                f"{imperv:<8.1f} {width:<8.0f} {neigung:<8.1f} 0                        \n"
            )
            self.file = open(self.ergfileSwmm, 'a')
            self.file.write(datasc)

        self.file.close()


    def subareas(self):
        text = ("\n[SUBAREAS]"
                "\n;;Subcatchment   N-Imperv   N-Perv     S-Imperv   S-Perv     PctZero    RouteTo    PctRouted"
                "\n;;-------------- ---------- ---------- ---------- ---------- ---------- ---------- ----------"
                "\nS1               0.015      0.24       0.06       0.3        25         OUTLET")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()


    def infiltration(self):
        text = ("\n[INFILTRATION]"
                "\n;;Subcatchment   MaxRate    MinRate    Decay      DryTime    MaxInfil"
                "\n;;-------------- ---------- ---------- ---------- ---------- ----------"
                "\nS1               4.5        0.2        6.5        7          0")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()


    def junctions(self):
        text = ("\n[JUNCTIONS]"
                "\n;;               Invert     Max.       Init.      Surcharge  Ponded"
                "\n;;Name           Elev.      Depth      Depth      Depth      Area"
                "\n;;-------------- ---------- ---------- ---------- ---------- ----------"
                "\nJ1               4969       0          0          0          0")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()


    def outfalls(self):
        text = ("\n[OUTFALLS]"
                "\n;;               Invert     Outfall    Stage/Table      Tide"
                "\n;;Name           Elev.      Type       Time Series      Gate"
                "\n;;-------------- ---------- ---------- ---------------- ----"
                "\nO1               4956       FREE                        NO")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def conduits(self):
        text = ("\n[CONDUITS]"
                "\n;;               Inlet            Outlet                      Manning    Inlet      Outlet     Init.      Max."
                "\n;;Name           Node             Node             Length     N          Offset     Offset     Flow       Flow"
                "\n;;-------------- ---------------- ---------------- ---------- ---------- ---------- ---------- ---------- ----------"
                "\nC2a              J2a              J2               157.48     0.016      4          4          0          0")
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def xsection(self):
        text = ("\n[XSECTIONS]"
                "\n;;Link           Shape        Geom1            Geom2      Geom3      Geom4      Barrels"
                "\n;;-------------- ------------ ---------------- ---------- ---------- ---------- ----------"
                "\nC2a              IRREGULAR    Half_Street      3          5          5          1"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def transects(self):
        text = ("\n[TRANSECTS]")

    def losses(self):
        text = ("\n[LOSSES]"
                "\n;;Link           Inlet      Outlet     Average    Flap Gate"
                "\n;;-------------- ---------- ---------- ---------- ----------"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def timeseries(self):
        text = ("\n[TIMESERIES]"
                "\n;;Name           Date       Time       Value"
                "\n;;-------------- ---------- ---------- ----------"
                "\n2-yr                        0:00       0.29"
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
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def tags(self):
        text = ("\n[TAGS]"
                "\nLink       C2a              Half_Street"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def map(self):
        text = ("\n[MAP]"
                "\nDIMENSIONS -0.123 0.000 1423.123 1475.000i"
                "\nUnits      Feet"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def coordinates(self):
        text = ("\n[COORDINATES]"
                "\n;;Node           X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\nJ1               648.532            1043.713"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def vertices(self):
        text = ("\n[VERTICES]"
                "\n;;Link           X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\nC2               1321.339           774.591"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def polygons(self):
        text = ("\n[Polygons]"
                "\n;;Subcatchment   X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\nS1               282.657            1334.810"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def symbols(self):
        text = ("\n[SYMBOLS]"
                "\n;;Gage           X-Coord            Y-Coord"
                "\n;;-------------- ------------------ ------------------"
                "\nRainGage         -175.841           1212.778"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def labels(self):
        text = ('\n[LABELS]'
            '\n;;X-Coord          Y-Coord            Label'
            '\n145.274            1129.896           "S1" "" "Arial" 14 0 0'
              )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()

    def backdrop(self):
        text = ("\n[BACKDROP]"
            "\nFILE       'Site-Post.jpg'"
            "\nDIMENSIONS -0.123 0.000 1423.123 1475.000"
                )
        self.file = open(self.ergfileSwmm, 'a')
        self.file.write(text)
        self.file.close()




