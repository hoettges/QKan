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


import os, time

from QKan_Database.dbfunc import DBConnection

# import tempfile
import glob, shutil

from qgis.core import QgsFeature, QgsGeometry, QgsMessageLog, QgsProject, QgsCoordinateReferenceSystem
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QAction, QIcon

from qgis.utils import iface
from qgis.gui import QgsMessageBar, QgsMapCanvas, QgsLayerTreeMapCanvasBridge
import codecs
import pyspatialite.dbapi2 as splite
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger('QKan')

# Fortschritts- und Fehlermeldungen

def fortschritt(text,prozent):
    logger.debug(u'{:s} ({:.0f}%)'.format(text,prozent*100))
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text,prozent*100), 'Export: ', QgsMessageLog.INFO)

def fehlermeldung(title, text):
    logger.debug(u'{:s} {:s}'.format(title,text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)

# ------------------------------------------------------------------------------
# Hauptprogramm

def createUnbefFlaechen(database_QKan, epsg, dbtyp = 'SpatiaLite'):

    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :database_QKan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :epsg:          EPSG-Nummer des Projektionssystems
    :type epsg:     Integer

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbQK = DBConnection(dbname=database_QKan, epsg=epsg)      # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        fehlermeldung("Fehler", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        iface.messageBar().pushMessage("Fehler", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
            database_QKan), level=QgsMessageBar.CRITICAL)
        return None

    # Für die Erzeugung der Restflächen reicht eine SQL-Abfrage aus. 

    sql = """INSERT INTO flaechen (flnam, haltnam, neigkl, regenschreiber, teilgebiet, abflussparameter, geom) 
            SELECT 'fu_' || tezg.flnam AS flnam, tezg.haltnam, tezg.neigkl, tezg.regenschreiber, tezg.teilgebiet, tezg.abflussparameter, CastToMultiPolygon(Difference(tezg.geom,GUnion(Intersection(flaechen.geom,tezg.geom)))) AS geom
            FROM tezg
            INNER JOIN flaechen
            ON Intersects(tezg.geom,flaechen.geom)
            GROUP BY tezg.pk"""
    try:
        dbQK.sql(sql)
        dbQK.commit()
    except:
        fehlermeldung(u"SQL-Fehler in QKan_CreateUnbefFl: \n", sql)
        del dbQK
        return False

    del dbQK

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Restflächen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)


# ----------------------------------------------------------------------------------------------------------------------

# Verzeichnis der Testdaten
pfad = 'C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/linges_deng'

database_QKan = os.path.join(pfad,'netz.sqlite')
epsg = '31466'

if __name__ == '__main__':
    linkFlaechenToHaltungen(database_QKan, epsg)
elif __name__ == '__console__':
    # QMessageBox.information(None, "Info", "Das Programm wurde aus der QGIS-Konsole aufgerufen")
    linkFlaechenToHaltungen(database_QKan, epsg)
elif __name__ == '__builtin__':
    # QMessageBox.information(None, "Info", "Das Programm wurde aus der QGIS-Toolbox aufgerufen")
    linkFlaechenToHaltungen(database_QKan, epsg)
# else:
    # QMessageBox.information(None, "Info", "Die Variable __name__ enthält: {0:s}".format(__name__))
