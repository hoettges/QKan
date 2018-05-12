# -*- coding: utf-8 -*-

'''

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

'''

__author__ = 'Joerg Hoettges'
__date__ = 'September 2016'
__copyright__ = '(C) 2016, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import logging
import os

from qgis.core import QgsMessageLog, QgsProject, QgsCoordinateReferenceSystem
from qgis.gui import QgsMessageBar
from qgis.utils import iface, pluginDirectory

from qgis.PyQt.QtGui import QProgressBar
from PyQt4.QtCore import QFileInfo

from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import fortschritt, fehlermeldung

import xml.etree.ElementTree as ET

logger = logging.getLogger(u'QKan')

progress_bar = None


def qgsadapt(projectTemplate, qkanDB, epsg, projectFile, setPathToTemplateDir = True, 
              dbtyp = u'SpatiaLite'):
    '''Lädt eine (Vorlage-) Projektdatei (*.qgs) und adaptiert diese auf eine QKan-Datenbank an. 
    Anschließend wird dieses Projekt geladen. 
    Voraussetzungen: keine

    :projectTemplate:           Vorlage-Projektdatei
    :type database:             String

    :qkanDB:                    Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :type qkanDB:               String

    :projectFile:               Zu Erzeugende Projektdatei
    :type projectFile:          String

    :setPathToTemplateDir:      Option, ob das Suchverzeichnis auf das Template-Verzeichnis gesetzt werden soll. 
    :type setPathToTemplateDir: Boolean

    :copy_forms:                Option, ob die Eingabeformulare kopiert oder, falls vorhanden, aktualisiert werden sollen. 
    :type copy_forms:           Boolean

    :dbtyp:                     Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:                String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbQK = DBConnection(dbname=qkanDB, epsg=epsg)      # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        fehlermeldung(u"Fehler in qgsadapt", 
                      u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(qkanDB))
        iface.messageBar().pushMessage(u"Fehler in qgsadapt", 
                    u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
            qkanDB), level=QgsMessageBar.CRITICAL)
        return None

    # --------------------------------------------------------------------------
    # Zoom-Bereich für die Projektdatei vorbereiten
    sql = u'''SELECT min(xsch) AS xmin, 
                    max(xsch) AS xmax, 
                    min(ysch) AS ymin, 
                    max(ysch) AS ymax
             FROM schaechte'''
    try:
        dbQK.sql(sql)
    except BaseException as e:
        fehlermeldung('SQL-Fehler', str(e))
        fehlermeldung("Fehler in qgsadapt", u"\nFehler in sql_zoom: \n" + sql + '\n\n')

    daten = dbQK.fetchone()
    try:
        zoomxmin, zoomxmax, zoomymin, zoomymax = daten
    except BaseException as e:
        fehlermeldung('SQL-Fehler', str(e))
        fehlermeldung("Fehler in qgsadapt", u"\nFehler in sql_zoom; daten= " + str(daten) + '\n')

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten
    sql = """SELECT srid
            FROM geom_cols_ref_sys
            WHERE Lower(f_table_name) = Lower('schaechte')
            AND Lower(f_geometry_column) = Lower('geom')"""
    if not dbQK.sql(sql, 'importkanaldaten_dyna (37)'):
        return None

    srid = dbQK.fetchone()[0]
    try:
        crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
        srsid = crs.srsid()
        proj4text = crs.toProj4()
        description = crs.description()
        projectionacronym = crs.projectionAcronym()
        if 'ellipsoidacronym' in dir(crs):
            ellipsoidacronym = crs.ellipsoidacronym()
        else:
            ellipsoidacronym = None
    except BaseException as e:
        srid, srsid, proj4text, description, projectionacronym, ellipsoidacronym = \
            'dummy', 'dummy', 'dummy', 'dummy', 'dummy', 'dummy'

        fehlermeldung('\nFehler in "daten"', str(e))
        fehlermeldung("Fehler in qgsadapt", u"\nFehler bei der Ermittlung der srid: \n" + str(daten))


    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

    del dbQK


    # --------------------------------------------------------------------------
    # Projektdatei schreiben, falls ausgewählt

    if projectFile is None or projectFile == u'':
        fehlermeldung(u'Bedienerfehler!', u'Es wurde keine Projektdatei ausgewählt')
        return False

    if setPathToTemplateDir:
        templatepath = os.path.join(pluginDirectory('qkan'), u"database/templates")

    projectpath = os.path.dirname(projectFile)
    if os.path.dirname(qkanDB) == projectpath:
        datasource = qkanDB.replace(os.path.dirname(qkanDB), u'.')
    else:
        datasource = qkanDB

    # Liste der Geotabellen aus QKan, um andere Tabellen von der Bearbeitung auszuschliessen
    # Liste steht in 3 Modulen: tools.k_tools, importdyna.import_from_dyna, importhe.import_from_he
    tabliste = [u'einleit', u'einzugsgebiete', u'flaechen', u'haltungen', u'linkfl', u'linksw', 
                u'pumpen', u'schaechte', u'teilgebiete', u'tezg', u'wehre']

    # Lesen der Projektdatei ------------------------------------------------------------------
    qgsxml = ET.parse(projectTemplate)
    root = qgsxml.getroot()

    for tag_maplayer in root.findall(u".//projectlayers/maplayer"):

        # Nur QKan-Tabellen bearbeiten
        tag_datasource = tag_maplayer.find(u"./datasource")
        tex = tag_datasource.text
        if tex[tex.index(u'table="') + 7:].split(u'" ')[0] in tabliste:

            # <extend> löschen
            for tag_extent in tag_maplayer.findall(u"./extent"):
                tag_maplayer.remove(tag_extent)

            for tag_spatialrefsys in tag_maplayer.findall(u"./srs/spatialrefsys"):
                tag_spatialrefsys.clear()

                elem = ET.SubElement(tag_spatialrefsys, u'proj4')
                elem.text = proj4text
                elem = ET.SubElement(tag_spatialrefsys, u'srsid')
                elem.text = u'{}'.format(srsid)
                elem = ET.SubElement(tag_spatialrefsys, u'srid')
                elem.text = u'{}'.format(srid)
                elem = ET.SubElement(tag_spatialrefsys, u'authid')
                elem.text = u'EPSG: {}'.format(srid)
                elem = ET.SubElement(tag_spatialrefsys, u'description')
                elem.text = description
                elem = ET.SubElement(tag_spatialrefsys, u'projectionacronym')
                elem.text = projectionacronym
                if ellipsoidacronym is not None:
                    elem = ET.SubElement(tag_spatialrefsys, u'ellipsoidacronym')
                    elem.text = ellipsoidacronym

    for tag_extent in root.findall(u".//mapcanvas/extent"):
        elem = tag_extent.find(u"./xmin")
        elem.text = u'{:.3f}'.format(zoomxmin)
        elem = tag_extent.find(u"./ymin")
        elem.text = u'{:.3f}'.format(zoomymin)
        elem = tag_extent.find(u"./xmax")
        elem.text = u'{:.3f}'.format(zoomxmax)
        elem = tag_extent.find(u"./ymax")
        elem.text = u'{:.3f}'.format(zoomymax)

    for tag_spatialrefsys in root.findall(u".//mapcanvas/destinationsrs/spatialrefsys"):
        tag_spatialrefsys.clear()

        elem = ET.SubElement(tag_spatialrefsys, u'proj4')
        elem.text = proj4text
        elem = ET.SubElement(tag_spatialrefsys, u'srid')
        elem.text = u'{}'.format(srid)
        elem = ET.SubElement(tag_spatialrefsys, u'authid')
        elem.text = u'EPSG: {}'.format(srid)
        elem = ET.SubElement(tag_spatialrefsys, u'description')
        elem.text = description
        elem = ET.SubElement(tag_spatialrefsys, u'projectionacronym')
        elem.text = projectionacronym
        if ellipsoidacronym is not None:
            elem = ET.SubElement(tag_spatialrefsys, u'ellipsoidacronym')
            elem.text = ellipsoidacronym

    for tag_datasource in root.findall(u".//projectlayers/maplayer/datasource"):
        text = tag_datasource.text
        tag_datasource.text = u"dbname='" + datasource + u"' " + text[text.find(u'table='):]

    qgsxml.write(projectFile)  # writing modified project file
    logger.debug(u'Projektdatei: {}'.format(projectFile))
    # logger.debug(u'encoded string: {}'.format(tex))

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage("Information", "Datenimport ist fertig!", level=QgsMessageBar.INFO)
    # QgsMessageLog.logMessage("\nFertig: Datenimport erfolgreich!", level=QgsMessageLog.INFO)

    # Importiertes Projekt laden
    # project = QgsProject.instance()
    # project.read(QFileInfo(projectFile))         # read the new project file
    # logger.debug(u'Geladene Projektdatei: {}   ({})'.format(project.fileName()))

