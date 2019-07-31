# -*- coding: utf-8 -*-

"""

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

"""
from xml.etree import ElementTree

__author__ = 'Joerg Hoettges'
__date__ = 'September 2018'
__copyright__ = '(C) 2018, Joerg Hoettges'

import logging

import os

from qgis.core import (QgsProject, QgsCoordinateReferenceSystem, QgsVectorLayer, Qgis,
            QgsDataSourceUri, QgsEditorWidgetSetup)
from qgis.utils import iface, pluginDirectory

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_database import qgsVersion, qgsActualVersion
from qkan.database.qkan_utils import (meldung, fehlermeldung, warnung, 
            get_qkanlayerAttributes, listQkanLayers, evalNodeTypes, getEditWidgetConfigFromQgsTemplate)

logger = logging.getLogger(u'QKan.tools.k_layersadapt')

progress_bar = None


def layersadapt(database_QKan, projectTemplate, qkanDBUpdate,
                anpassen_Datenbankanbindung, anpassen_Wertebeziehungen_in_Tabellen,
                anpassen_Formulare,
                anpassen_Projektionssystem, aktualisieren_Schachttypen, zoom_alles,
                fehlende_layer_ergaenzen, anpassen_auswahl, dbtyp=u'spatialite'):
    """Anpassen von Projektlayern an den QKan-Standard
    Voraussetzungen: keine

    :database_QKan:                                 Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :type database_QKan:                            String

    :projectTemplate:                               Vorlage-Projektdatei für die anzupassenden Layereigenschaften
    :type projectTemplate:                          String

    :anpassen_Datenbankanbindung:                   Datenbankanbindungen werden angepasst
    :type anpassen_Datenbankanbindung:              Boolean

    :anpassen_Wertebeziehungen_in_Tabellen:         Wertebeziehungen werden angepasst
    :type anpassen_Wertebeziehungen_in_Tabellen:    Boolean

    :anpassen_Formulare:                            Formulare werden anpasst
    :type anpassen_Formulare:                       Boolean

    :anpassen_Projektionssystem:                    Projektionssystem wird angepasst
    :type anpassen_Projektionssystem:               Boolean

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
    """

    # -----------------------------------------------------------------------------------------------------
    # QKan-Projekt
    project = QgsProject.instance()
    
    if project.count() == 0:
        fehlermeldung(u'Benutzerfehler: ', u'Es ist kein Projekt geladen.')
        return

    # -----------------------------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbQK = DBConnection(dbname=database_QKan, qkanDBUpdate=qkanDBUpdate)  # Datenbankobjekt der QKan-Datenbank
    # qkanDBUpdate: mit Update

    if not dbQK.connected:
        if not qkanDBUpdate:
            warnung('Versionsfehler', 'QKan-Datenbank ist nicht aktuell, aber die Anpassung ist deaktiviert. Abbruch.')
            logger.debug(u'k_layersadapt: QKan-Datenbank ist nicht aktuell, aber die Anpassung ist deaktiviert. Abbruch')
        else:
            logger.debug(u'k_layersadapt: QKan-Datenbank wurde aktualisiert, Neuladen des Projektes erforderlich')
            meldung(u'Update der Datenbank erfolgreich!', u'Bitte aktualisieren Sie alle entsprechenden Projekte!')
        return False

    actversion = dbQK.actversion
    logger.debug(u'actversion: {}'.format(actversion))

    # Projekt auf aktuelle Version updaten
    qgsActualVersion()

    # Vorlage-Projektdatei. Falls Standard oder keine Vorgabe, wird die Standard-Projektdatei verwendet

    templateDir = os.path.join(pluginDirectory('qkan'), u"templates")
    if projectTemplate is None or projectTemplate == u'':
        projectTemplate = os.path.join(templateDir, 'Projekt.qgs')

    logger.debug(u'Projekttemplate: {}'.format(projectTemplate))

    # Liste aller QKan-Layernamen aus gewählter QGS-Vorlage.
    # Dabei wird trotzdem geprüft, ob es sich um einen QKan-Layer handelt; es könnte sich ja um eine 
    # vom Benutzer angepasste Vorlage handeln. 

    qkanLayers = listQkanLayers(projectTemplate)            # Liste aller Layernamen aus gewählter QGS-Vorlage
    # logger.debug(u'qkanLayers: {}'.format(qkanLayers))

    # Fehlende Layer ergänzen. Unabhängig von der Auswahl werden die fehlenden Referenztabellen 
    # auf jeden Fall ergänzt. 

    layersRoot = project.layerTreeRoot()
    for layername in qkanLayers:
        if len(project.mapLayersByName(layername)) == 0:
            # layername fehlt in aktuellem Projekt
            isVector = (qkanLayers[layername][1] != '')             # Test, ob Vorlage-Layer spatial ist
            if not isVector or fehlende_layer_ergaenzen:
                # Referenzlisten werden auf jeden Fall ergänzt. 
                table, geom_column, sql, group = qkanLayers[layername]
                uri = QgsDataSourceUri()
                uri.setDatabase(database_QKan)
                uri.setDataSource(sql, table, geom_column)
                try:
                    layer = QgsVectorLayer(uri.uri(), layername, 'spatialite')
                except BaseException as err:
                    fehlermeldung(u'Fehler in k_layersadapt (11): {}'.format(err),
                                  u'layername: {}'.format(layername))
                    return False
                project.addMapLayer(layer, False)
                atcGroup = layersRoot.findGroup(group)
                if atcGroup == '':
                    layersRoot.addGroup(group)
                atcGroup.addLayer(layer)

                # Stildatei laden, falls vorhanden
                qlsnam = os.path.join(templateDir, 'Layer_{}.qml'.format(layername))
                if os.path.exists(qlsnam):
                    layer.loadNamedStyle(qlsnam)
                    logger.debug('Layerstil geladen: {}'.format(qlsnam))
                # layerList[layer.name()] = layer           --> in QGIS3 nicht nötig 
                logger.debug(u"k_layersadapt: Layer ergänzt: {}".format(layername))
            else:
                logger.debug(u"k_layersadapt: Layer nicht ergänzt: {}".format(layername))
        # else:
        # logger.debug(u"k_layersadapt: Layer schon vorhanden: {}".format(layername))

    # Dictionary, das alle LayerIDs aus der Template-Projektdatei den entsprechenden (QKan-) LayerIDs
    # des aktuell geladenen Projekts zuordnet. Diese Liste wird bei der Korrektur der Wertelisten 
    # benötigt. 

    qgsxml = ElementTree.ElementTree()
    qgsxml.parse(projectTemplate)

    layerNotInProjektMeldung = False
    rltext = u"projectlayers/maplayer"
    nodes_refLayerTemplate = qgsxml.findall(rltext)
    layerIdList = {}
    for node in nodes_refLayerTemplate:
        refLayerName = node.findtext('layername')
        refLayerId = node.findtext('id')
        layerobjects = project.mapLayersByName(refLayerName)
        if len(layerobjects) > 0:
            layer = layerobjects[0]             # Der Layername muss eindeutig sein.
            layerId = layer.id()
            logger.debug(u'layerId: {}'.format(layerId))
            layerIdList[refLayerId] = layerId
            if len(layerobjects) > 1:
                warnung('Layername doppelt: {}', 'Es wird nur ein Layer bearbeitet.'.format(refLayerName))
        else:
            layerNotInProjektMeldung = not fehlende_layer_ergaenzen  # nur setzen, wenn keine Ergänzung gewählt
            logger.info(u'k_layersadapt: QKan-Layer nicht in Projekt: {}'.format(refLayerName))
    logger.debug(u'Refliste Layer-Ids: \n{}'.format(layerIdList))

    # Liste der zu bearbeitenden Layer
    if anpassen_auswahl == 'auswahl_anpassen':
        # Im Formular wurde "nur ausgewählte Layer" angeklickt

        selectedLayers = iface.layerTreeCanvasBridge().rootGroup().checkedLayers()
        selectedLayerNames = [lay.name() for lay in selectedLayers]
    else:
        legendLayers = iface.layerTreeCanvasBridge().rootGroup().findLayers()
        selectedLayerNames = [lay.name() for lay in legendLayers]

    logger.debug(u'k_layersadapt (9), selectedLayerNames: {}'.format(selectedLayerNames))

    layerNotQkanMeldung = False  # Am Schluss erscheint ggfs. eine Meldung, dass Nicht-QKan-Layer gefunden wurden.

    # Alle (ausgewählten) Layer werden jetzt anhand der entsprechenden Layer des Template-Projektes angepasst

    formsDir = os.path.join(pluginDirectory('qkan'), u"forms")

    for layername in selectedLayerNames:
        layerobjects = project.mapLayersByName(layername)
        if len(layerobjects) == 0:
            logger.info(u'Projektlayer {} ist in QKan-Template nicht enthalten'.format(layername))
            continue
        else:
            layer = layerobjects[0]

        tagLayer = u"projectlayers/maplayer[layername='{}'][provider='spatialite']".format(layername)
        qgsLayers = qgsxml.findall(tagLayer)
        if len(qgsLayers) > 1:
            fehlermeldung(u'DateifFehler!',
                          u'In der Vorlage-Projektdatei wurden mehrere Layer {} gefunden'.format(layername))
            del dbQK
            return False
        elif len(qgsLayers) == 0:
            layerNotQkanMeldung = True
            logger.info(u'In der Vorlage-Projektdatei wurden kein Layer {} gefunden'.format(layername))
            continue  # Layer ist in Projekt-Templatenicht vorhanden...

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
            logger.debug('anpassen_Projektionssystem...')
            datasource = layer.source()
            dbname, table, geom, sql = get_qkanlayerAttributes(datasource)
            logger.debug('Prüfe KBS von Tabelle {}'.format(table))
            if geom != '':
                # Nur für Vektorlayer
                sql = u"""SELECT srid
                        FROM geom_cols_ref_sys
                        WHERE Lower(f_table_name) = Lower('{table}')
                        AND Lower(f_geometry_column) = Lower('{geom}')""".format(table=table, geom=geom)
                if not dbQK.sql(sql, u'dbQK: k_layersadapt (1)'):
                    return False

                data = dbQK.fetchone()
                if data is not None:
                    epsg = data[0]
                else:
                    logger.debug(u'\nTabelle hat kein KBS: {}\n'.format(datasource))

                crs = QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId)
                if crs.isValid():
                    layer.setCrs(crs)
                    logger.debug('KBS angepasst für Tabelle "{0:} auf {1:}"'.format(table, crs.postgisSrid()))
                else:
                    fehlermeldung(u'Fehler bei Festlegung des Koordinatensystems!',
                                  u'Layer {}'.format(layername))

        if anpassen_Formulare:
            formpath = qgsLayers[0].findtext('./editform')
            form = os.path.basename(formpath)
            editFormConfig = layer.editFormConfig()
            editFormConfig.setUiForm(os.path.join(formsDir, form))
            layer.setEditFormConfig(editFormConfig)

        if anpassen_Wertebeziehungen_in_Tabellen:
            dictOfEditWidgets = getEditWidgetConfigFromQgsTemplate(qgsxml, layername)

            # iterating over all fieldnames in template project
            for idx, field in enumerate(layer.fields()):
                fieldname = field.name()
                if fieldname in dictOfEditWidgets:
                    type, options = dictOfEditWidgets[fieldname]
                    ews = QgsEditorWidgetSetup(type, options)
                    layer.setEditorWidgetSetup(idx, ews)

    if layerNotInProjektMeldung:
        meldung(u'Information zu den Layern',
                u'Es fehlten Layer, die zum QKan-Standard gehörten. Eine Liste steht in der LOG-Datei...')
    # if layerNotQkanMeldung:
    # meldung(u'Information zu den Layern', u'Es wurden Layer gefunden, die nicht zum QKan-Standard gehörten. Eine Liste steht in der LOG-Datei...')

    if aktualisieren_Schachttypen:
        # Schachttypen auswerten
        evalNodeTypes(dbQK)  # in qkan.database.qkan_utils

    del qgsxml
    del dbQK

    project.setTitle(u'QKan Version {}'.format(qgsVersion()))

    # if status_neustart:
    # meldung(u"Achtung! Benutzerhinweis!", u"Die Datenbank wurde geändert. Bitte QGIS-Projekt neu laden...")
    # return False

    # Zoom auf alles
    if zoom_alles:
        canvas.zoomToFullExtent()

    # Noch zu bearbeiten:
    #  - Sicherungskopie der Datenbank, falls Versionsupdate

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage("Information",
                                   "Projektdatei ist angepasst und muss noch gespeichert werden!", level=Qgis.Info)

    return True
