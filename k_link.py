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
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text,prozent*100), u'Link Flächen: ', QgsMessageLog.INFO)

def fehlermeldung(title, text):
    logger.debug(u'{:s} {:s}'.format(title,text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)

# ------------------------------------------------------------------------------
# Hauptprogramm

def linkFlaechenToHaltungen(database_QKan, liste_flaechen_abflussparam='', liste_hal_entw='', dbtyp = 'SpatiaLite'):

    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :database_QKan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :liste_flaechen_abflussparam: Liste der ausgewählten Abflussparameter für die Flächen
    :type liste_flaechen_abflussparam: String

    :liste_hal_entw: Liste der ausgewählten Entwässerungsarten für die Haltungen
    :type liste_hal_entw: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbQK = DBConnection(dbname=database_QKan)      # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        fehlermeldung("Fehler", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        iface.messageBar().pushMessage("Fehler", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
            database_QKan), level=QgsMessageBar.CRITICAL)
        return None

    # ------------------------------------------------------------------------------
    # Die Bearbeitung erfolgt in einer zusätzlichen Tabelle 'linkfl'
    # Sie wird zunächst aus der Tabelle "flaechen" erstellt, und enthält zusätzlich
    # zwei weitere Geo-Attribute: 
    #  gbuf  - Buffer sind die mit einem Buffer erweiterten Flächen
    #  glink - linkfl sind Verbindungslinien, die von der Fläche zur Haltung zeigen
    # zusätzlich wird die zugeordnete Haltung im entsprechenden Attribut verwaltet. 
    #
    # Flächen, bei denen im Feld "haltungen" bereits eine Eintragung vorhanden ist, 
    # werden nicht bearbeitet. Damit ist eine manuelle Zuordnung möglich. 

    # Tabelle "linkfl" anlegen und ggfs. leeren
    sql = """CREATE TABLE IF NOT EXISTS linkfl (
            pk INTEGER,
            flnam TEXT,
            haltnam TEXT)"""
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"(1) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    sql1 = """SELECT AddGeometryColumn('linkfl','geom',25832,'MULTIPOLYGON',2)"""
    sql2 = """SELECT AddGeometryColumn('linkfl','gbuf',25832,'POLYGON',2)"""
    sql3 = """SELECT AddGeometryColumn('linkfl','glink',25832,'LINESTRING',2)"""
    try:
        dbQK.sql(sql1)
        dbQK.sql(sql2)
        dbQK.sql(sql3)
    except:
        fehlermeldung(u"(2) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    sql = "DELETE FROM linkfl"
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"(3) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Kopieren der Flaechenobjekte in die Tabelle linkfl
    if liste_flaechen_abflussparam == '':
        auswahl = ''
        # Keine Auswahl. Soll eigentlich nicht vorkommen, funktioniert aber...
        logger.debug(u'Warnung in Link Flaechen: Keine Auswahl bei Flächen...')
    else:
        auswahl = ' WHERE flaechen.abflussparameter in ({})'.format(liste_flaechen_abflussparam)

    sql = """INSERT INTO linkfl (pk, flnam, haltnam, geom)
            SELECT pk, flnam, haltnam, geom
            FROM flaechen{}""".format(auswahl)
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"(4) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Zurücksetzen des Bufferobjektes um die Fläche
    sql = "UPDATE linkfl SET glink = NULL"                      # entfernt: haltnam = NULL, 
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"(5) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Jetzt werden die Flächenobjekte Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = "UPDATE linkfl SET gbuf = buffer(geom,50)"
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"(1) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Erzeugung der Verbindungslinie zwischen den Zentroiden. 
    # Achtung: Bei Flächen mit konkaven Bereichen kann der Zentroiden
    # ausßerhalb der Fläche liegen...

    if liste_hal_entw == '':
        # Keine Auswahl. Soll eigentlich nicht vorkommen, funktioniert aber...
        auswahl = ''
    else:
        auswahl = ' WHERE hal.entwart in ({})'.format(liste_hal_entw)
    
    sql ="""WITH tlink AS
            (	SELECT fl.pk AS pk, hal.haltnam AS haltnam, fl.pk AS pk, fl.haltnam AS linkhal,
                    Distance(hal.geom,fl.geom) AS dist, 
                    hal.geom AS geohal, fl.geom AS geofl
                FROM
                    haltungen AS hal
                INNER JOIN
                    linkfl AS fl
                ON MbrOverlaps(hal.geom,fl.gbuf){})
            UPDATE linkfl SET glink =  
            (SELECT MakeLine(PointOnSurface(t1.geofl),Centroid(t1.geohal))
            FROM tlink AS t1
            INNER JOIN (SELECT haltnam, pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.haltnam=t2.haltnam AND t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.0001 AND t1.linkhal IS NULL
            WHERE linkfl.pk = t1.pk)""".format(auswahl)
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"(1) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # ... gleiche Abfrage, aber Eintrag der zugeordneten Haltung
    sql= """WITH tlink AS
            (	SELECT fl.pk AS pk, hal.haltnam AS haltnam, fl.pk AS pk, fl.haltnam AS linkhal,
                    Distance(hal.geom,fl.geom) AS dist, 
                    hal.geom AS geohal, fl.geom AS geofl
                FROM
                    haltungen AS hal
                INNER JOIN
                    linkfl AS fl
                ON MbrOverlaps(hal.geom,fl.gbuf){})
            UPDATE linkfl SET haltnam =  
            (SELECT t1.haltnam
            FROM tlink AS t1
            INNER JOIN (SELECT haltnam, pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.haltnam=t2.haltnam AND t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.0001 AND t1.linkhal IS NULL
            WHERE linkfl.pk = t1.pk)""".format(auswahl)
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"(1) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False


    # Linie erzeugen für alle Elemente, die bereits vorher manuell zugeordnet waren. Sie 
    # werden daran erkannt, dass im Feld "haltnam" ein Eintrag, aber kein Objekt
    # im Feld "glink" vorhanden ist. 

    # noch zu bearbeiten...


    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

    del dbQK


    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
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
