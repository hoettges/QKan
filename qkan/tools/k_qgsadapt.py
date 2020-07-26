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

from qgis.core import Qgis, QgsCoordinateReferenceSystem
from qgis.utils import iface, pluginDirectory
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
):
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
                    max(x(coalesce(geop, centroid(geom)))) AS xmax, 
                    min(y(coalesce(geop, centroid(geom)))) AS ymin, 
                    max(y(coalesce(geop, centroid(geom)))) AS ymax
             FROM schaechte"""
    try:
        dbQK.sql(sql)
    except BaseException as err:
        fehlermeldung("SQL-Fehler", repr(err))
        fehlermeldung("Fehler in qgsadapt", "\nFehler in sql_zoom: \n" + sql + "\n\n")
        return False

    daten = dbQK.fetchone()
    try:
        zoomxmin, zoomxmax, zoomymin, zoomymax = daten
    except BaseException as err:
        fehlermeldung("SQL-Fehler", repr(err))
        fehlermeldung(
            "\nFehler in sql_zoom; daten= " + str(daten) + "\n",
        )

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten,
    # außer: Wenn epsg aus Parameterliste vorgegeben, dann übernehmen
    if epsg:
        srid = epsg
        logger.debug(f"Vorgabe epsg: {epsg}")
    else:
        sql = """SELECT srid
                FROM geom_cols_ref_sys
                WHERE Lower(f_table_name) = Lower('schaechte')
                AND Lower(f_geometry_column) = Lower('geom')"""
        if not dbQK.sql(sql, "k_qgsadapt (1)"):
            return False

        srid = dbQK.fetchone()[0]
    try:
        crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
        srsid = crs.srsid()
        proj4text = crs.toProj4()
        # description = crs.description()
        # projectionacronym = crs.projectionAcronym()
        # if "ellipsoidacronym" in dir(crs):
        #     ellipsoidacronym = crs.ellipsoidacronym()
        # else:
        #     ellipsoidacronym = None
    except BaseException as err:
        srid, srsid, proj4text, description, projectionacronym, ellipsoidacronym = (
            "dummy",
            "dummy",
            "dummy",
            "dummy",
            "dummy",
            "dummy",
        )

        fehlermeldung('\nFehler in "daten"', repr(err))
        fehlermeldung(
            "Fehler in qgsadapt",
            "\nFehler bei der Ermittlung der srid: \n" + str(daten),
        )

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

        # Liste der Geotabellen aus QKan, um andere Tabellen von der Bearbeitung auszuschliessen
        # Liste steht in 3 Modulen: tools.k_tools, importdyna.import_from_dyna, importhe.import_from_he
        tabliste = [
            "einleit",
            "einzugsgebiete",
            "flaechen",
            "haltungen",
            "linkfl",
            "linksw",
            "pumpen",
            "schaechte",
            "teilgebiete",
            "tezg",
            "wehre",
        ]

        # Liste der QKan-Formulare, um individuell erstellte Formulare von der Bearbeitung auszuschliessen
        formsliste = [
            "qkan_abflussparameter.ui",
            "qkan_anbindungageb.ui",
            "qkan_anbindungeinleit.ui",
            "qkan_anbindungflaechen.ui",
            "qkan_auslaesse.ui",
            "qkan_auslasstypen.ui",
            "qkan_aussengebiete.ui",
            "qkan_bodenklassen.ui",
            "qkan_einleit.ui",
            "qkan_einzugsgebiete.ui",
            "qkan_entwaesserungsarten.ui",
            "qkan_flaechen.ui",
            "qkan_haltungen.ui",
            "qkan_profildaten.ui",
            "qkan_profile.ui",
            "qkan_pumpen.ui",
            "qkan_pumpentypen.ui",
            "qkan_schaechte.ui",
            "qkan_simulationsstatus.ui",
            "qkan_speicher.ui",
            "qkan_speicherkennlinien.ui",
            "qkan_swref.ui",
            "qkan_teilgebiete.ui",
            "qkan_tezg.ui",
            "qkan_wehre.ui",
        ]

        # Lesen der Projektdatei ------------------------------------------------------------------
        qgsxml = ET.parse(projecttemplate)
        root = qgsxml.getroot()

        # Projektionssystem anpassen --------------------------------------------------------------

        for tag_maplayer in root.findall(".//projectlayers/maplayer"):
            tag_datasource = tag_maplayer.find("./datasource")
            tex = tag_datasource.text
            # Nur QKan-Tabellen bearbeiten
            if tex[tex.index(u'table="') + 7 :].split(u'" ')[0] in tabliste:

                # <extend> löschen
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
                    elem.text = "EPSG:{}".format(srid)
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
            if tag_editform.text:
                dateiname = os.path.basename(tag_editform.text)
                if dateiname in formsliste:
                    # Nur QKan-Tabellen bearbeiten
                    tag_editform.text = os.path.join(formspath, dateiname)

        # Zoom für Kartenfenster einstellen -------------------------------------------------------

        if not isinstance(zoomxmin, (int, float)):
            zoomxmin = 0.0
            zoomxmax = 100.0
            zoomymin = 0.0
            zoomymax = 100.0

        for tag_extent in root.findall(".//mapcanvas/extent"):
            elem = tag_extent.find("./xmin")
            elem.text = "{:.3f}".format(zoomxmin)
            elem = tag_extent.find("./ymin")
            elem.text = "{:.3f}".format(zoomymin)
            elem = tag_extent.find("./xmax")
            elem.text = "{:.3f}".format(zoomxmax)
            elem = tag_extent.find("./ymax")
            elem.text = "{:.3f}".format(zoomymax)

        # Projektionssystem des Plans anpassen --------------------------------------------------------------

        for tag_spatialrefsys in root.findall(".//mapcanvas/destinationsrs/spatialrefsys"):
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