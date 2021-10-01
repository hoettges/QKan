# -*- coding: utf-8 -*-

"""

  Results from HE
  ==============
  
  Aus einer Hystem-Extran-Datenbank im Firebird-Format werden Ergebnisdaten
  in die QKan-Datenbank importiert und ausgewertet.
  
  | Dateiname            : results_from_he.py
  | Date                 : September 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$
  
  This program is free software; you can redistribute it and/or modify   
  it under the terms of the GNU General Public License as published by   
  the Free Software Foundation; either version 2 of the License, or      
  (at your option) any later version.

"""

__author__ = "Joerg Hoettges"
__date__ = "September 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ":%H$"

# import tempfile
import logging
import os

from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer
from qgis.utils import pluginDirectory

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan

logger = logging.getLogger("QKan")


class ResultsTask:
    def __init__(self):
        pass

    def run(self) -> bool:

        database_QKan, epsg = get_database_QKan()

        """Attach SQLite-Database with HE8 Data"""
        sql = f'ATTACH DATABASE "{QKan.config.he8.results_file}" AS he'

        dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben
        if not dbQK.connected:
            return None

        if dbQK is None:
            fehlermeldung(
                "Fehler in QKan_Import_from_HE",
                "QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        if not dbQK.sql(sql, "He8Porter.run_export_to_he8 Attach HE8"):
            logger.error(
                f"Fehler in He8Porter._doexport(): Attach fehlgeschlagen: {QKan.config.he8.results_file}"
            )
            return False

        # Vorbereiten der temporären Ergebnistabellen
        sqllist = [
            """CREATE TABLE IF NOT EXISTS ResultsSch(
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                schnam TEXT,
                uebstauhaeuf REAL,
                uebstauanz REAL, 
                maxuebstauvol REAL,
                kommentar TEXT,
                createdat TEXT DEFAULT CURRENT_DATE)""",
            """SELECT AddGeometryColumn('ResultsSch','geom',{},'POINT',2)""".format(
                epsg
            ),
            """DELETE FROM ResultsSch""",
        ]
        # , '''CREATE TABLE IF NOT EXISTS ResultsHal(
        # pk INTEGER PRIMARY KEY AUTOINCREMENT,
        # haltnam TEXT,
        # uebstauhaeuf REAL,
        # uebstauanz REAL,
        # maxuebstauvol REAL,
        # kommentar TEXT,
        # createdat TEXT DEFAULT CURRENT_DATE)''',
        # """SELECT AddGeometryColumn('ResultsHal','geom',{},'LINESTRING',2)""".format(epsg)
        # '''DELETE FROM ResultsHal''']

        for sql in sqllist:
            if not dbQK.sql(sql, "QKan_Import_Results (1)"):
                return False

        # Die folgende Abfrage gilt sowohl bei Einzel- als auch bei Seriensimulationen:
        sql = f"""INSERT INTO ResultsSch
                (schnam, uebstauhaeuf, uebstauanz, maxuebstauvol, geom, kommentar)
                SELECT 
                    MR.KNOTEN, LZ.HAEUFIGKEITUEBERSTAU, 
                    LZ.ANZAHLUEBERSTAU, MR.UEBERSTAUVOLUMEN, SC.geop,  '{QKan.config.he8.results_file}'
                FROM he.LAU_MAX_S AS MR
                LEFT JOIN LANGZEITKNOTEN AS LZ
                ON MR.KNOTEN = LZ.KNOTEN
                JOIN schaechte AS SC
                ON SC.schnam = MR.KNOTEN
                """

        if not dbQK.sql(sql, stmt_category="QKan_Import_Results (4)"):
            return False

        dbQK.commit()

        # Einfügen der Ergebnistabelle in die Layerliste, wenn nicht schon geladen
        project = QgsProject.instance()
        if not project.mapLayersByName("Überstau Schächte"):

            uri = QgsDataSourceUri()
            uri.setDatabase(database_QKan)
            logger.debug(f"database_QKan (1): {database_QKan}")
            uri.setDataSource("", "ResultsSch", "geom")
            logger.debug(f"(2) uri.database(): {uri.database()}")
            vlayer = QgsVectorLayer(uri.uri(), "Überstau Schächte", "spatialite")

            root = project.layerTreeRoot()
            group = root.addGroup("Ergebnisse")
            project.addMapLayer(vlayer, False)
            group.addLayer(vlayer)

            # Stilvorlage nach Benutzerwahl laden
            templatepath = os.path.join(pluginDirectory("qkan"), "templates")
            if QKan.config.he8.qml_choice == "uebh":
                template = os.path.join(templatepath, "Überstauhäufigkeit.qml")
                try:
                    vlayer.loadNamedStyle(template)
                except:
                    fehlermeldung(
                        "Fehler in QKan_Results_from_HE",
                        'Stildatei "Überstauhäufigkeit.qml" wurde nicht gefunden!\nAbbruch!',
                    )
            elif QKan.config.he8.qml_choice == "uebvol":
                template = os.path.join(templatepath, "Überstauvolumen.qml")
                try:
                    vlayer.loadNamedStyle(template)
                except:
                    fehlermeldung(
                        "Fehler in QKan_Results_from_HE",
                        'Stildatei "Überstauvolumen.qml" wurde nicht gefunden!\nAbbruch!',
                    )
            elif QKan.config.he8.qml_choice == "userqml":
                try:
                    vlayer.loadNamedStyle(QKan.config.he8.qml_file_results)
                except:
                    fehlermeldung(
                        "Fehler in QKan_Results_from_HE",
                        f"Benutzerdefinierte Stildatei {QKan.config.he8.qml_choice} "
                        "wurde nicht gefunden!\nAbbruch!",
                    )

        del dbQK
