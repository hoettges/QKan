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

import os

from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer
from qgis.utils import pluginDirectory

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import get_database_QKan
from qkan import enums
from qkan.utils import get_logger
from qkan.tools.qkan_utils import loadLayer

logger = get_logger("QKan")


class ResultsTask:
    def __init__(self, db_qkan):
        self.db_qkan = db_qkan

    def run(self) -> bool:

        # Vorbereiten der temporären Ergebnistabellen
        sqllis = [
            ["he8_create_results_attr", ()],
            ["he8_create_results_geom", {'epsg': self.db_qkan.epsg}],
            ["he8_reset_results", ()],
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

        for sql, params in sqllis:
            if not self.db_qkan.sqlyml(
                sqlnam=sql,
                stmt_category="QKan_Import_Results (1)",
                parameters=params,
            ):
                return False

        # Die folgende Abfrage gilt sowohl bei Einzel- als auch bei Seriensimulationen:
        sql = "he8_insertresults"

        if not self.db_qkan.sqlyml(
                sqlnam= sql,
                stmt_category="QKan_Import_Results (4)",
        ):
            return False

        self.db_qkan.commit()

        # Einfügen der Ergebnistabelle in die Layerliste, wenn nicht schon geladen
        project = QgsProject.instance()
        logger.debug(f'project.mapLayersByName("Überstau Schächte")= {project.mapLayersByName("Überstau Schächte")}')
        if not project.mapLayersByName(enums.LAYERBEZ.UEBERSTAUSCHAECHTE.value):

            # database_qkan = self.db_qkan.dbname
            # uri = QgsDataSourceUri()
            # uri.setDatabase(database_qkan)
            # logger.debug(f"database_qkan (1): {database_qkan}")
            # uri.setDataSource("", "ResultsSch", "geom")
            # logger.debug(f"(2) uri.database(): {uri.database()}")
            # vlayer = QgsVectorLayer(uri.uri(), "Überstau Schächte", "spatialite")
            #
            # #root = project.layerTreeRoot()
            # #group = root.addGroup("Ergebnisse")
            # #project.addMapLayer(vlayer, False)
            # #group.addLayer(vlayer)
            #
            # group = 'Ergebnisse'
            # layersRoot = QgsProject.instance().layerTreeRoot()
            # QgsProject.instance().addMapLayer(vlayer, False)
            # actGroup = layersRoot.findGroup(group)
            # if actGroup is None:
            #     actGroup = layersRoot.addGroup(group)
            # actGroup.addLayer(vlayer)
            # vlayer.triggerRepaint()
            #
            # # Stilvorlage nach Benutzerwahl laden
            # templatepath = os.path.join(pluginDirectory("qkan"), "templates")
            # if QKan.config.he8.qml_choice == enums.QmlChoice.UEBH:
            #     template = os.path.join(templatepath, "qml", "ueberstauhaeufigkeit.qml")
            #     try:
            #         vlayer.loadNamedStyle(template)
            #         vlayer.triggerRepaint()
            #     except:
            #         errormsg = "Fehler in QKan_Results_from_HE\n" + \
            #                    'Stildatei "Überstauhäufigkeit.qml" wurde nicht gefunden!\nAbbruch!'
            #         logger.warning(errormsg)
            #
            # elif QKan.config.he8.qml_choice == enums.QmlChoice.UEBVOL:
            #     template = os.path.join(templatepath, "qml", "ueberstauvolumen.qml")
            #     try:
            #         vlayer.loadNamedStyle(template)
            #         vlayer.triggerRepaint()
            #     except:
            #         errormsg = "Fehler in QKan_Results_from_HE\n" + \
            #                    'Stildatei "Überstauvolumen.qml" wurde nicht gefunden!\nAbbruch!'
            #         logger.warning(errormsg)
            #
            # elif QKan.config.he8.qml_choice == enums.QmlChoice.USERQML:
            #     try:
            #         vlayer.loadNamedStyle(QKan.config.he8.qml_file_results)
            #         vlayer.triggerRepaint()
            #     except:
            #         errormsg = "Fehler in QKan_Results_from_HE\n" + \
            #                   f"Benutzerdefinierte Stildatei {QKan.config.he8.qml_choice.value}\n" + \
            #                    "wurde nicht gefunden!\nAbbruch!"
            #         logger.warning(errormsg)

            templatepath = os.path.join(pluginDirectory("qkan"), "templates")
            if QKan.config.he8.qml_choice == enums.QmlChoice.UEBH:
                loadLayer(
                    layerbez=enums.LAYERBEZ.UEBERSTAUSCHAECHTE,
                    gpos=1,
                    table='ResultsSch',
                    geom_column='geom',
                    qmlfile=os.path.join(templatepath, "qml", "ueberstauhaeufigkeit.qml"),
                    filter='',
                    group=[enums.LAYERBEZ.ERGEBNISSE_GROUP],
                )
            elif QKan.config.he8.qml_choice == enums.QmlChoice.UEBVOL:
                loadLayer(
                    layerbez=enums.LAYERBEZ.UEBERSTAUSCHAECHTE,
                    table='ResultsSch',
                    geom_column='geom',
                    qmlfile=os.path.join(templatepath, "qml", "ueberstauvolumen.qml"),
                    filter='',
                    group=[enums.LAYERBEZ.ERGEBNISSE_GROUP],
                )
            elif QKan.config.he8.qml_choice == enums.QmlChoice.USERQML:
                loadLayer(
                    layerbez=enums.LAYERBEZ.UEBERSTAUSCHAECHTE,
                    table='ResultsSch',
                    geom_column='geom',
                    qmlfile=QKan.config.he8.qml_file_results,
                    filter='',
                    group=[enums.LAYERBEZ.ERGEBNISSE_GROUP],
                )
