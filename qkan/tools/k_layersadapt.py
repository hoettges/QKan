# -*- coding: utf-8 -*-

'''

  Adapt QKan-Layers to QKan-Standard
  ==============
  
  Für ein bestehendes Projekt werden alle oder ausgewählte Layer auf den QKan-Standard
  (zurück-) gesetzt. Dabei können optional der Layerstil, die Werteanbindungen, die 
  Formularverknüpfung sowie die Datenbankanbindung bearbeitet werden. 
  
  | Dateiname            : k_layersadapt.py
  | Date                 : September 2018
  | Copyright            : (C) 2018 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$
  
  This program is free software; you can redistribute it and/or modify   
  it under the terms of the GNU General Public License as published by   
  the Free Software Foundation; either version 2 of the License, or      
  (at your option) any later version.

'''

__author__ = 'Joerg Hoettges'
__date__ = 'September 2018'
__copyright__ = '(C) 2018, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import logging
import os, time

from qgis.core import QgsMessageLog, QgsProject, QgsCoordinateReferenceSystem
from qgis.gui import QgsMessageBar, QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.utils import iface, pluginDirectory

from qgis.PyQt.QtGui import QProgressBar
from PyQt4.QtCore import QFileInfo
import xml.etree.ElementTree as et

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fortschritt, meldung, fehlermeldung, get_qkanlayerAttributes, evalNodeTypes

logger = logging.getLogger(u'QKan')

progress_bar = None

def layersadapt(database_QKan, projectFile, projectTemplate, qkanDBUpdate, 
                anpassen_Datenbankanbindung, anpassen_Wertebeziehungen_in_Tabellen, 
                anpassen_Formulare, 
                anpassen_Projektionssystem, aktualisieren_Schachttypen, zoom_alles, 
                anpassen_auswahl, dbtyp = u'spatialite'):
    '''Anpassen von Projektlayern an den QKan-Standard 
    Voraussetzungen: keine

    :database_QKan:                                 Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :type database_QKan:                            String

    :projectFile:                                   Zu Erzeugende Projektdatei
    :type projectFile:                              String

    :projectTemplate:                               Vorlage-Projektdatei für die anzupassenden Layereigenschaften
    :type projectTemplate:                          String

    :anpassen_Datenbankanbindung:                   Datenbankanbindungen werden angepasst
    :type anpassen_Datenbankanbindung:              Boolean

    :anpassen_Wertebeziehungen_in_Tabellen:         Wertebeziehungen werden angepasst
    :type anpassen_Wertebeziehungen_in_Tabellen:    Boolean

    :anpassen_Formulare:                            Formulare werden anpasst
    :type anpassen_Formulare:                       Boolean

    :anpassen_Projektionssystem:                    Projektionssystem wird angepasst
    :type anpassen_Wertebeziehungen_in_Tabellen:    Boolean

    :aktualisieren_Schachttypen:                    Knotentypen in schaechte.knotentyp setzen
    :type aktualisieren_Schachttypen                Boolean

    :anpassen_auswahl:                              Wahl der anzupassenden Layer
    :type anpassen_auswahl:                         list

    :dbtyp:                                         Typ der Datenbank (spatialite, postgis)
    :type dbtyp:                                    string

    :returns: void
    '''

    # -----------------------------------------------------------------------------------------------------
    # Liste aller widgetv2type-Arten: 
    widgetv2types = ['ValueRelation', 'ValueMap', 'DateTime', 'CheckBox']

    # Liste aller QKan-Layernamen: 

    templateDir = os.path.join(pluginDirectory('qkan'), u"templates")
    qgsTemplate = os.path.join(templateDir,'Projekt.qgs')
    tag = u"projectlayers/maplayer[provider='spatialite']"
    qgsxml = et.ElementTree()
    try:
        qgsxml.parse(qgsTemplate)
    except:
        fehlermeldung(u'Dateifehler bei Layeranpassung:', 
                      u'Projekt-Template {} nicht vorhanden.'.format(qgsTemplate))
        return
    qgslayer = qgsxml.findall(tag)
    qkanLayers = [tag.findtext('./layername') for tag in qgslayer]
    del qgsxml

    # Dictionary aller Layer für legendInterface
    allLayers = iface.legendInterface().layers()
    if len(allLayers) == 0:
        meldung(u'Benutzerfehler: ', u'Es ist kein Projekt geladen.')
        return

    layerIndex = {}
    for layer in allLayers:
        layerIndex[layer.name()] = layer

    # Dictionary aller Layer für mapCanvas
    canvas = iface.mapCanvas()
    allCanvasLayers = canvas.layers()
    if len(allCanvasLayers) == 0:
        meldung(u'Benutzerfehler: ', u'Es ist kein Projekt geladen.')
        return

    canvasIndex = {}
    for layer in allCanvasLayers:
        canvasIndex[layer.name()] = layer


    # -----------------------------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbQK = DBConnection(dbname=database_QKan, qkanDBUpdate=qkanDBUpdate)   # Datenbankobjekt der QKan-Datenbank
                                                                            # qkanDBUpdate: mit Update

    if (not dbQK.connected) and (not qkanDBUpdate):
        logger.debug(u'k_layersadapt: Datenbankverbindung konnte nicht hergestellt werden.')
        # fehlermeldung(u"Fehler in k_layersadapt", 
                      # u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        # iface.messageBar().pushMessage(u"Fehler in k_layersadapt", 
                    # u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
            # database_QKan), level=QgsMessageBar.CRITICAL)
        return None

    # Status, wenn die Änderungen so gravierend waren, dass das Projekt neu geladen werden muss. 
    # status_neustart = False

    if not dbQK.updatestatus:
        # QKan-Datenbank ist nicht aktuell
        logger.debug(u'k_layersadapt: QKan-Datenbank ist nicht aktuell')
        if qkanDBUpdate:
            # Kontrolle, ob auch anpassen_Wertebeziehungen_in_Tabellen und anpassen_Formulare aktiviert
            if not (anpassen_Wertebeziehungen_in_Tabellen and anpassen_Formulare):
                # In diesem Fall ist ein Update der Datenbank nicht zulässig
                fehlermeldung(u'Fehler in k_layersadapt:', 
                    u'Nicht aktivierte Optionen lassen ein Update der QKan-Datenbank nicht zu!')
                return None
            else:
                logger.debug(u'k_layersadapt: QKan-Datenbank wird aktualisiert')
                dbQK.updateversion()
        else:
            return False                # Fehlermeldungen wurden schon von dbQK ausgegeben

    if projectTemplate is None or projectTemplate == u'':
        fehlermeldung(u'Bedienerfehler!', u'Es wurde keine Vorlage-Projektdatei ausgewählt')
        return False

    logger.debug(u'Projekttemplate: {}'.format(projectTemplate))

    qgsxml = et.ElementTree()
    qgsxml.parse(projectTemplate)

    # Liste der zu bearbeitenden Layer
    if anpassen_auswahl == 'auswahl_anpassen':
        # Im Formular wurde "nur ausgewählte Layer" angeklickt
        
        selectedLayers = iface.legendInterface().selectedLayers()
        selectedLayerNames = [lay.name() for lay in selectedLayers]
    else:
        selectedLayerNames = qkanLayers

    for layername in selectedLayerNames:

        layer = layerIndex[layername]         # Layerobjekt ermitteln

        tag = u"projectlayers/maplayer[layername='{}'][provider='spatialite']".format(layername)
        qgslayer = qgsxml.findall(tag)
        if len(qgslayer) > 1:
            fehlermeldung(u'DateifFehler!', 
                u'In der Vorlage-Projektdatei wurden mehrere Layer {} gefunden'.format(layername))
            del dbQK
            return None
        elif len(qgslayer) == 0:
            meldung(u'DateifFehler!', 
                u'In der Vorlage-Projektdatei wurden kein Layer {} gefunden'.format(layername))
            continue                        # Layer ist in Projekt-Templatenicht vorhanden...

        if anpassen_Datenbankanbindung:
            datasource = layer.source()
            dbname, table, geom, sql = get_qkanlayerAttributes(datasource)
            if geom != '':
                # Vektorlayer
                newdatasource = u'dbname=\'{dbname}\' table="{table}" ({geom}) sql={sql}'.format(
                                dbname=database_QKan, table=table, geom=geom, sql=sql)
            else:
                # Tabellenlayer
                newdatasource = u'dbname=\'{dbname}\' table="{table}" sql={sql}'.format(
                                dbname=database_QKan, table=table, geom=geom, sql=sql)
            layer.setDataSource(newdatasource, layername, 'spatialite')
            logger.debug(u'\nAnbindung neue QKanDB: {}\n'.format(newdatasource))

        if anpassen_Projektionssystem:
                # epsg-Code des Layers an angebundene Tabelle anpassen
            datasource = layer.source()
            dbname, table, geom, sql = get_qkanlayerAttributes(datasource)

            sql = u"""SELECT srid
                    FROM geom_cols_ref_sys
                    WHERE Lower(f_table_name) = Lower('{table}')
                    AND Lower(f_geometry_column) = Lower('{geom}')""".format(table=table, geom=geom)
            if not dbQK.sql(sql, u'dbQK: k_layersadapt (1)'):
                return None

            data = dbQK.fetchone()
            if data is not None:
                epsg = data[0]
            else:
                logger.debug(u'\nAnbindung neue QKanDB: {}\n'.format(datasource))
            
            crs = QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId)
            if crs.isValid():
                layer.setCrs(crs)
            else:
                fehlermeldung(u'Fehler bei Festlegung des Koordinatensystems!', 
                u'Layer {}'.format(layername))

        if anpassen_Formulare:
            formpath = qgslayer[0].findtext('./editform')
            form = os.path.basename(formpath)
            editFormConfig = layer.editFormConfig()
            editFormConfig.setUiForm(form)

        if anpassen_Wertebeziehungen_in_Tabellen:
            # Schleife über alle widgetv2type-Arten (Liste s. o.)
            for widgetv2type in widgetv2types:
                lntext = u"projectlayers/maplayer[layername='{ln}']".format(ln=layername)
                node_maplayer = qgsxml.find(lntext)
                try:
                    wttext = u"./edittypes/edittype[@widgetv2type='{wt}']".format(wt=widgetv2type)
                    nodes_edittype = node_maplayer.findall(wttext)
                except:
                    fehlermeldung(u'Fehler in k_layersadapt:\n', u'lntext: {}\nwttext: {}'.format(lntext, wttext))
                    del qgsxml
                    del dbQK
                    return None

                logger.debug(u'k_layersadapt: lntext: {}\nwttext: {}'.format(lntext, wttext))
                for node_edittype in nodes_edittype:
                    att = node_edittype.find('widgetv2config')
                    widgetConfig = att.attrib

                    fieldname = node_edittype.attrib['name']
                    fieldIndex = layer.fieldNameIndex(fieldname)
                    layerId = layer.id()

                    editFormConfig = layer.editFormConfig()
                    widgetType = editFormConfig.widgetType(fieldIndex)
                    # widgetConfig = editFormConfig.widgetConfig(fieldIndex)

                    editFormConfig.setWidgetType(fieldIndex, widgetv2type)

                    editFormConfig.setWidgetConfig(fieldIndex, widgetConfig)
                    logger.debug('widgetConfig: \n{}\n'.format(widgetConfig))


    if aktualisieren_Schachttypen:
        # Schachttypen auswerten
        evalNodeTypes(dbQK)                     # in qkan.database.qkan_utils

    del qgsxml
    del dbQK

    # Schreiben der neuen Projektdatei
    if projectFile != '':
        project = QgsProject.instance()
        project.write(QFileInfo(projectFile))

    # if status_neustart:
        # meldung(u"Achtung! Benutzerhinweis!", u"Die Datenbank wurde geändert. Bitte QGIS-Projekt neu laden...")
        # return False

    # Zoom auf alles
    elif zoom_alles:
        canvas.zoomToFullExtent()


    # Noch zu bearbeiten:
    #  - Sicherungskopie der Datenbank, falls Versionsupdate



    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    iface.mainWindow().statusBar().clearMessage()
    if projectFile:
        iface.messageBar().pushMessage("Information", 
            "Projektdatei ist angepasst und als {file} gespeichert!".format(file=projectFile), level=QgsMessageBar.INFO)
    else:
        iface.messageBar().pushMessage("Information", 
            "Projektdatei ist angepasst und muss noch gespeichert werden!", level=QgsMessageBar.INFO)
    # QgsMessageLog.logMessage("\nFertig: Datenimport erfolgreich!", level=QgsMessageLog.INFO)

