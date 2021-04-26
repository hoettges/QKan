# -*- coding: utf-8 -*-

"""

  Import from HE
  ==============
  
  Aus einer Hystem-Extran-Datenbank im Firebird-Format werden Kanaldaten
  in die QKan-Datenbank importiert. Dazu wird eine Projektdatei erstellt,
  die verschiedene thematische Layer erzeugt, u.a. eine Klassifizierung
  der Schachttypen.
  
  | Dateiname            : import_from_he.py
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

import logging
import os
from xml.etree import ElementTree as ET

from qgis.core import Qgis ,QgsCoordinateReferenceSystem
from qgis.utils import pluginDirectory
from qkan import QKAN_FORMS, QKAN_TABLES
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

logger = logging.getLogger("QKan.tools.k_qgsadapt")

progress_bar = None


def qgsadapt(
    projecttemplate: str,
    database_QKan: str,
    dbQK: DBConnection,
    projectfile: str,
    epsg: int = None,
) -> bool:
    """Lädt eine (Vorlage-) Projektdatei (*.qgs) und adaptiert diese auf eine QKan-Datenbank an.
    Anschließend wird dieses Projekt geladen.
    Voraussetzungen: keine

    :projecttemplate:           Vorlage-Projektdatei
    :type database:             String

    :database_QKan:             Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :type database_QKan:        String

    :projectfile:               Zu Erzeugende Projektdatei
    :type projectfile:          String

    :epsg:                      EPSG-Code. Falls nicht vorgegeben, wird dieser aus der Tabelle 'schaechte' gelesen
    :type epsg:                 Integer

    :returns:                   Success
    :type:                      Boolean
    """

    # --------------------------------------------------------------------------
    # Zoom-Bereich für die Projektdatei vorbereiten
    sql = """SELECT min(x(coalesce(geop, centroid(geom)))) AS xmin, 
                    min(y(coalesce(geop, centroid(geom)))) AS ymin, 
                    max(x(coalesce(geop, centroid(geom)))) AS xmax, 
                    max(y(coalesce(geop, centroid(geom)))) AS ymax
             FROM schaechte"""
    try:
        dbQK.sql(sql)
    except BaseException as err:
        fehlermeldung("SQL-Fehler", repr(err))
        fehlermeldung("Fehler in qgsadapt", "\nFehler in sql_zoom: \n" + sql + "\n\n")
        return False

    try:
        zoom = dbQK.fetchone()
    except BaseException as err:
        fehlermeldung("SQL-Fehler", repr(err))
        fehlermeldung(
            "\nFehler in sql_zoom; daten= \n",
        )
        zoom = [0.0, 0.0, 100.0, 100.0]

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten,
    # außer: Wenn epsg aus Parameterliste vorgegeben, dann übernehmen
    if epsg:
        srsid = epsg
        if Qgis.QGIS_VERSION_INT < 31000:
            proj4text = QgsCoordinateReferenceSystem(srsid).toProj4()
        else:
            proj4text = QgsCoordinateReferenceSystem(srsid).toProj()
        logger.debug(f"Vorgabe epsg: %s", epsg)
    else:
        sql = """SELECT srid, proj4text
                FROM geom_cols_ref_sys
                WHERE Lower(f_table_name) = Lower('schaechte')
                AND Lower(f_geometry_column) = Lower('geom')"""
        if not dbQK.sql(sql, "k_qgsadapt (1)"):
            return False
        srsid, proj4text = dbQK.fetchone()

    srid = srsid

    # --------------------------------------------------------------------------
    # Projektdatei schreiben, falls ausgewählt

    if projectfile is not None and projectfile != "":
        templatepath = os.path.join(pluginDirectory("qkan"), "templates")
        projecttemplate = os.path.join(templatepath, "projekt.qgs")
        projectpath = os.path.dirname(projectfile)
        if os.path.dirname(database_QKan) == projectpath:
            datasource = database_QKan.replace(os.path.dirname(database_QKan), ".")
        else:
            datasource = database_QKan

        # Lesen der Projektdatei ------------------------------------------------------------------
        qgsxml = ET.parse(projecttemplate)
        root = qgsxml.getroot()

        # Projektionssystem anpassen --------------------------------------------------------------

        for tag_maplayer in root.findall(".//projectlayers/maplayer"):
            tag_datasource = tag_maplayer.find("./datasource")
            if tag_datasource is None:
                continue

            tex = tag_datasource.text
            if not tex or tex[:6] != 'dbname':
                continue

            # Nur QKan-Tabellen bearbeiten
            if tex[tex.index('table="') + 7 :].split('" ')[0] in QKAN_TABLES:

                # <extent> löschen
                for tag_extent in tag_maplayer.findall("./extent"):
                    tag_maplayer.remove(tag_extent)

                for tag_spatialrefsys in tag_maplayer.findall("./srs/spatialrefsys"):
                    tag_spatialrefsys.clear()

                    elem = ET.SubElement(tag_spatialrefsys, "proj4")
                    elem.text = proj4text
                    elem = ET.SubElement(tag_spatialrefsys, "srsid")
                    elem.text = "{}".format(srsid)
                    # elem = ET.SubElement(tag_spatialrefsys, "srid")
                    # elem.text = "{}".format(srid)
                    elem = ET.SubElement(tag_spatialrefsys, "authid")
                    elem.text = "EPSG:{}".format(srsid)
                    # elem = ET.SubElement(tag_spatialrefsys, "description")
                    # elem.text = description
                    # elem = ET.SubElement(tag_spatialrefsys, "projectionacronym")
                    # elem.text = projectionacronym
                    # if ellipsoidacronym is not None:
                    #     elem = ET.SubElement(tag_spatialrefsys, "ellipsoidacronym")
                    #     elem.text = ellipsoidacronym

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
            zoom = [0.0, 0.0, 100.0, 100.0]
        for tag_extent in root.findall(".//mapcanvas/extent"):
            for idx, name in enumerate(["xmin", "ymin", "xmax", "ymax"]):
                element = tag_extent.find(f"./{name}")
                if element is not None:
                    element.text = "{:.3f}".format(zoom[idx])

        # Projektionssystem des Plans anpassen --------------------------------------------------------------

        for tag_spatialrefsys in root.findall(
            ".//mapcanvas/destinationsrs/spatialrefsys"
        ):
            tag_spatialrefsys.clear()

            elem = ET.SubElement(tag_spatialrefsys, "proj4")
            elem.text = proj4text
            # elem = ET.SubElement(tag_spatialrefsys, "srid")
            # elem.text = "{}".format(srid)
            elem = ET.SubElement(tag_spatialrefsys, "srsid")
            elem.text = "{}".format(srsid)
            elem = ET.SubElement(tag_spatialrefsys, "authid")
            elem.text = "EPSG:{}".format(srid)
            # elem = ET.SubElement(tag_spatialrefsys, "description")
            # elem.text = description
            # elem = ET.SubElement(tag_spatialrefsys, "projectionacronym")
            # elem.text = projectionacronym
            # if ellipsoidacronym is not None:
            #     elem = ET.SubElement(tag_spatialrefsys, "ellipsoidacronym")
            #     elem.text = ellipsoidacronym

        # Projektionssystem von QGIS anpassen --------------------------------------------------------------

        for tag_spatialrefsys in root.findall(".//projectCrs/spatialrefsys"):
            tag_spatialrefsys.clear()

            elem = ET.SubElement(tag_spatialrefsys, "proj4")
            elem.text = proj4text
            # elem = ET.SubElement(tag_spatialrefsys, "srid")
            # elem.text = "{}".format(srid)
            elem = ET.SubElement(tag_spatialrefsys, "srsid")
            elem.text = "{}".format(srsid)
            elem = ET.SubElement(tag_spatialrefsys, "authid")
            elem.text = "EPSG:{}".format(srid)
            # elem = ET.SubElement(tag_spatialrefsys, "description")
            # elem.text = description
            # elem = ET.SubElement(tag_spatialrefsys, "projectionacronym")
            # elem.text = projectionacronym
            # if ellipsoidacronym is not None:
            #     elem = ET.SubElement(tag_spatialrefsys, "ellipsoidacronym")
            #     elem.text = ellipsoidacronym

        # Pfad zur QKan-Datenbank anpassen

        for tag_datasource in root.findall(".//projectlayers/maplayer/datasource"):
            text = tag_datasource.text
            if not text or text[:6] != 'dbname':
                continue

            tag_datasource.text = (
                "dbname='" + datasource + "' " + text[text.find("table=") :]
            )

        qgsxml.write(projectfile)  # writing modified project file
        logger.debug("Projektdatei: {}".format(projectfile))
        # logger.debug(u'encoded string: {}'.format(tex))

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage(
    # "Information",
    # "Projektdatei ist angepasst und muss neu geladen werden!",
    # level=Qgis.Info,
    # )

    # Importiertes Projekt laden
    # project = QgsProject.instance()
    # canvas = QgsMapCanvas(None)
    # bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(),
    # canvas)  # synchronise the loaded project with the canvas
    # project.read(QFileInfo(projectfile))  # read the new project file
    # logger.debug(u'Geladene Projektdatei: {}   ({})'.format(project.fileName()))

    return True
