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

from qgis.core import (QgsMessageLog, QgsProject, QgsCoordinateReferenceSystem, 
    QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry)
from qgis.gui import QgsMessageBar, QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.utils import iface, pluginDirectory

from qgis.PyQt.QtGui import QProgressBar
from PyQt4.QtCore import QFileInfo

import xml.etree.ElementTree as et

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (fortschritt, meldung, fehlermeldung, warnung, 
    get_qkanlayerAttributes, isQkanLayer, listQkanLayers, evalNodeTypes)

from qkan.database.qkan_database import dbVersion, qgsVersion, qgsActualVersion

logger = logging.getLogger(u'QKan')

progress_bar = None


def layersadapt(database_QKan, projectFile, projectTemplate, qkanDBUpdate, 
                anpassen_Datenbankanbindung, anpassen_Wertebeziehungen_in_Tabellen, 
                anpassen_Formulare, 
                anpassen_Projektionssystem, aktualisieren_Schachttypen, zoom_alles, 
                fehlende_layer_ergaenzen, anpassen_auswahl, dbtyp = u'spatialite'):
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

    :zoom_alles:                                    Nach der Bearbeitung die Karte auf gesamte Gebiet zoomen
    :type zoom_alles:                               Boolean

    :fehlende_layer_ergaenzen:                      Fehlende QKan-Layer werden ergänzt
    :type fehlende_layer_ergaenzen:                 Boolean

    :anpassen_auswahl:                              Wahl der anzupassenden Layer
    :type anpassen_auswahl:                         list

    :dbtyp:                                         Typ der Datenbank (spatialite, postgis)
    :type dbtyp:                                    string

    :returns: void
    '''

    # -----------------------------------------------------------------------------------------------------
    # Liste aller widgetv2type-Arten: 
    widgetv2types = ['ValueRelation', 'DateTime', 'CheckBox']          # 'ValueMap' entfällt, weil entsprechende 
                                                                        # C-API-Funktion nicht in Python gemappt!

    # Liste aller QKan-Layernamen. Diese wird auf jeden Fall aus der Standardvorlage entnommen!
    # Dabei wird trotzdem geprüft, ob es sich um einen QKan-Layer handelt; es könnte sich ja um eine 
    # vom Benutzer angepasste Vorlage handeln. 

    # Layernamen auf aktuellen Stand bringen
    qgsActualVersion()

    # Dictionary aller Layer für legendInterface
    allLayers = iface.legendInterface().layers()
    if len(allLayers) == 0:
        meldung(u'Benutzerfehler: ', u'Es ist kein Projekt geladen.')
        return

    layerList = {}
    for layer in allLayers:
        layerList[layer.name()] = layer

    logger.debug(u'k_layersadapt, layerList: {}'.format(layerList))
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

    if not dbQK.connected:
        if not qkanDBUpdate:
            logger.debug(u'k_layersadapt: QKan-Datenbank ist nicht aktuell, aber keine Update aktiviert. Abbruch')
        else:
            logger.debug(u'k_layersadapt: QKan-Datenbank wurde aktualisiert, Neuladen des Projektes erforderlich')
            # tw = iface.layerTreeView()
            # tw.repaint()
            # project = QgsProject.instance()
            # project.clear()
        meldung(u'Update der Datenbank erfolgreich!',  u'Bitte aktualisieren Sie alle entsprechenden Projekte!')
        return None

    actversion = dbQK.actversion
    logger.debug('actversion: {}'.format(actversion))

    # Status, wenn die Änderungen so gravierend waren, dass das Projekt neu geladen werden muss. 
    # status_neustart = False

    # if not dbQK.isCurrentVersion:
        # # QKan-Datenbank ist nicht aktuell
        # logger.debug(u'k_layersadapt: QKan-Datenbank ist nicht aktuell')
        # if qkanDBUpdate:
            # # Kontrolle, ob auch anpassen_Wertebeziehungen_in_Tabellen und anpassen_Formulare aktiviert
            # # if not (anpassen_Wertebeziehungen_in_Tabellen and anpassen_Formulare):
                # # # In diesem Fall ist ein Update der Datenbank nicht zulässig
                # # fehlermeldung(u'Fehler in k_layersadapt:', 
                    # # u'Nicht aktivierte Optionen lassen ein Update der QKan-Datenbank nicht zu!')
                # # return None
            # # else:
                # # logger.debug(u'k_layersadapt: QKan-Datenbank wird aktualisiert')
                # # dbQK.updateversion()
            # logger.debug(u'k_layersadapt: QKan-Datenbank wird aktualisiert')
            # dbQK.updateversion()
            # logger.debug("Status dbQK:\n connected: {}".format(dbQK.connected))
            # if not dbQK.connected:
                # warnung("Achtung!", "Datenbank wurde aktualisiert. Jetzt müssen noch alle Projektdateien angepasst werden!")
                # return
        # else:
            # return False                # Fehlermeldungen wurden schon von dbQK ausgegeben

    # Vorlage-Projektdatei. Falls Standard oder keine Vorgabe, wird die Standard-Projektdatei verwendet

    if projectTemplate is None or projectTemplate == u'':
        templateDir = os.path.join(pluginDirectory('qkan'), u"templates")
        projectTemplate = os.path.join(templateDir,'Projekt.qgs')

    logger.debug(u'Projekttemplate: {}'.format(projectTemplate))

    qgsxml = et.ElementTree()
    qgsxml.parse(projectTemplate)

    # Fehlende Layer ergänzen. Unabhängig von der Auswahl werden die fehlenden Referenztabellen 
    # auf jeden Fall ergänzt. 

    qkanLayers = listQkanLayers()
    logger.debug(u'qkanLayers: {}'.format(qkanLayers))

    layersRoot = QgsProject.instance().layerTreeRoot()
    for layername in qkanLayers:
        if layername not in layerList:
            # layername fehlt in aktuellem Projekt
            isVector = (qkanLayers[layername][1] != '')
            if not isVector or fehlende_layer_ergaenzen:
                # Referenzlisten werden auf jeden Fall ergänzt. 
                table, geom_column, sql, group = qkanLayers[layername]
                uri = QgsDataSourceURI()
                uri.setDatabase(database_QKan)
                uri.setDataSource(sql, table, geom_column)
                try:
                    layer = QgsVectorLayer(uri.uri(), layername, 'spatialite')
                except BaseException as err:
                    fehlermeldung(u'Fehler in k_layersadapt (11): {}'.format(err), 
                                  u'layername: {}'.format(layername))
                    return False
                QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                atcGroup = layersRoot.findGroup(group)
                if atcGroup == '':
                    layersRoot.addGroup(group)
                atcGroup.addLayer(layer)
                logger.debug(u"k_layersadapt: Layer ergänzt: {}".format(layername))
            else:
                logger.debug(u"k_layersadapt: Layer nicht ergänzt: {}".format(layername))
        # else:
            # logger.debug(u"k_layersadapt: Layer schon vorhanden: {}".format(layername))

    # Liste der zu bearbeitenden Layer
    if anpassen_auswahl == 'auswahl_anpassen':
        # Im Formular wurde "nur ausgewählte Layer" angeklickt
        
        selectedLayers = iface.legendInterface().selectedLayers()
        selectedLayerNames = [lay.name() for lay in selectedLayers]
    else:
        legendLayers = iface.legendInterface().layers()
        selectedLayerNames = [lay.name() for lay in legendLayers]

    logger.debug(u'k_layersadapt (9), selectedLayerNames: {}'.format(selectedLayerNames))

    layerNotQkanMeldung = False             # Am Schluss erscheint ggfs. eine Meldung, dass Nicht-QKan-Layer gefunden wurden.

    for layername in selectedLayerNames:
        if layername not in layerList:
            logger.info(u'Projektlayer {} ist in QKan-Template nicht enthalten'.format(layername))
            continue
        
        try: 
            layer = layerList[layername]         # Layerobjekt ermitteln
        except BaseException as err:
            fehlermeldung(u'Fehler in k_layersadapt (10): {}'.format(err), 
                                  u'layername: {}'.format(layername))

        logger.debug(u'k_layersadapt (8), layername: {}'.format(layername))

        tagLayer = u"projectlayers/maplayer[layername='{}'][provider='spatialite']".format(layername)
        qgsLayers = qgsxml.findall(tagLayer)
        if len(qgsLayers) > 1:
            fehlermeldung(u'DateifFehler!', 
                u'In der Vorlage-Projektdatei wurden mehrere Layer {} gefunden'.format(layername))
            del dbQK
            return None
        elif len(qgsLayers) == 0:
            layerNotQkanMeldung = True
            logger.info(u'In der Vorlage-Projektdatei wurden kein Layer {} gefunden'.format(layername))
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
            if geom != '':
                # Nur für Vektorlayer
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
            formpath = qgsLayers[0].findtext('./editform')
            form = os.path.basename(formpath)
            editFormConfig = layer.editFormConfig()
            formsDir = os.path.join(pluginDirectory('qkan'), u"forms")
            editFormConfig.setUiForm(os.path.join(formsDir, form))

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

                logger.debug(u'k_layersadapt: \n lntext: {}\n wttext: {}\n'.format(lntext, wttext))
                for node_edittype in nodes_edittype:
                    logger.debug(u'k_layersadapt: (1)')
                    try:
                        att = node_edittype.find('widgetv2config')
                        widgetConfig = att.attrib

                        logger.debug(u'k_layersadapt: (2)')

                        fieldname = node_edittype.attrib['name']
                        fieldIndex = layer.fieldNameIndex(fieldname)
                        layerId = layer.id()

                        logger.debug(u'k_layersadapt: (3)')

                        editFormConfig = layer.editFormConfig()
                        widgetType = editFormConfig.widgetType(fieldIndex)
                        # widgetConfig = editFormConfig.widgetConfig(fieldIndex)

                        logger.debug(u'k_layersadapt: (4)')

                        editFormConfig.setWidgetType(fieldIndex, widgetv2type)

                        logger.debug(u'k_layersadapt: (5)')

                        editFormConfig.setWidgetConfig(fieldIndex, widgetConfig)
                        logger.debug('widgetConfig: \n{}\n'.format(widgetConfig))
                    except BaseException as err:
                        fehlermeldung(u'Fehler in k_layersadapt (2): {}'.format(err), 
                                  u'')

        logger.debug(u'k_layersadapt (6)')
    logger.debug(u'k_layersadapt (7)')
    if layerNotQkanMeldung:
        meldung(u'Information zu den Layern', u'Es wurden Layer gefunden, die nicht zum QKan-Standard gehörten. Eine Liste steht in der LOG-Datei...')

    if aktualisieren_Schachttypen:
        # Schachttypen auswerten
        evalNodeTypes(dbQK)                     # in qkan.database.qkan_utils

    del qgsxml
    del dbQK

    project = QgsProject.instance()
    project.setTitle('QKan Version {}'.format(qgsVersion()))

    # Schreiben der neuen Projektdatei
    if projectFile != '':
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

    return True