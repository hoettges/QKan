# -*- coding: utf-8 -*-

'''

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

'''

__author__ = 'Joerg Hoettges'
__date__ = 'September 2016'
__copyright__ = '(C) 2016, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

# import tempfile
import logging
import os

from PyQt4.QtCore import QFileInfo
from qgis.core import QgsMessageLog, QgsProject, QgsCoordinateReferenceSystem, QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar
from qgis.utils import iface, pluginDirectory

from qkan.database.dbfunc import DBConnection
from qkan.database.fbfunc import FBConnection

from qkan.database.qkan_utils import fortschritt, fehlermeldung

logger = logging.getLogger(u'QKan')


# ------------------------------------------------------------------------------
# Hauptprogramm

def importResults(database_HE, database_QKan, qml_choice, qmlfileResults, epsg=25832, dbtyp=u'SpatiaLite'):
    '''Importiert Simulationsergebnisse aus einer HE-Firebird-Datenbank und schreibt diese in Tabellen 
       der QKan-SpatiaLite-Datenbank.

    :database_HE:   Datenbankobjekt, das die Verknüpfung zur HE-Firebird-Datenbank verwaltet
    :type database: DBConnection (geerbt von firebirdsql...)

    :database_QKan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbHE = FBConnection(database_HE)  # Datenbankobjekt der HE-Datenbank zum Lesen

    if dbHE is None:
        fehlermeldung(u"Fehler in QKan_Import_from_HE",
                      u'ITWH-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_HE))
        return None

    dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        fehlermeldung(u"Fehler in QKan_Import_from_HE",
                      u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        return None

    # Vorbereiten der temporären Ergebnistabellen
    sqllist = [
        u'''CREATE TABLE IF NOT EXISTS ResultsSch(
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            schnam TEXT,
            uebstauhaeuf REAL,
            uebstauanz REAL, 
            maxuebstauvol REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE)''',
        u"""SELECT AddGeometryColumn('ResultsSch','geom',{},'POINT',2)""".format(epsg), 
        u'''DELETE FROM ResultsSch''']
        # , u'''CREATE TABLE IF NOT EXISTS ResultsHal(
            # pk INTEGER PRIMARY KEY AUTOINCREMENT,
            # haltnam TEXT,
            # uebstauhaeuf REAL,
            # uebstauanz REAL, 
            # maxuebstauvol REAL,
            # kommentar TEXT,
            # createdat TEXT DEFAULT CURRENT_DATE)''',
        # u"""SELECT AddGeometryColumn('ResultsHal','geom',{},'LINESTRING',2)""".format(epsg)
        # u'''DELETE FROM ResultsHal''']

    for sql in sqllist:
        if not dbQK.sql(sql, u"QKan_Import_Results (1)"):
            return False

    # Die folgende Abfrage gilt sowohl bei Einzel- als auch bei Seriensimulationen:
    sql = u'''SELECT MR.KNOTEN, LZ.HAEUFIGKEITUEBERSTAU, LZ.ANZAHLUEBERSTAU, MR.UEBERSTAUVOLUMEN
            FROM LAU_MAX_S AS MR
            LEFT JOIN LANGZEITKNOTEN AS LZ
            ON MR.KNOTEN = LZ.KNOTEN
            ORDER BY KNOTEN'''

    if not dbHE.sql(sql, u"QKan_Import_Results (4)"):
        return False

    for attr in dbHE.fetchall():
        # In allen Feldern None durch NULL ersetzen
        (schnam, uebstauhaeuf, uebstauanz, maxuebstauvol) = \
            (u'NULL' if el is None else el for el in attr)

        sql = u'''INSERT INTO ResultsSch
                (schnam, uebstauhaeuf, uebstauanz, maxuebstauvol, kommentar)
                VALUES ('{schnam}', {uebstauhaeuf}, {uebstauanz}, {maxuebstauvol}, '{kommentar}')'''.format(
                schnam=schnam, uebstauhaeuf=uebstauhaeuf, uebstauanz=uebstauanz, 
                maxuebstauvol=maxuebstauvol, kommentar=os.path.basename(database_HE))

        if not dbQK.sql(sql, u'QKan_Import_Results (5)'):
            return False

    sql = '''UPDATE ResultsSch
            SET geom = 
            (   SELECT geop
                FROM schaechte
                WHERE schaechte.schnam = ResultsSch.schnam)'''
    if not dbQK.sql(sql, u'QKan_Import_Results (6)'):
        return False

    dbQK.commit()

    # Einfügen der Ergebnistabelle in die Layerliste, wenn nicht schon geladen
    layers = iface.legendInterface().layers()
    if u'Ergebnisse_LZ' not in [lay.name() for lay in layers]:
        uri = QgsDataSourceURI()
        uri.setDatabase(database_QKan)
        uri.setDataSource(u'', u'ResultsSch', u'geom')
        vlayer = QgsVectorLayer(uri.uri(), u'Überstau Schächte', u'spatialite')
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)

        # Stilvorlage nach Benutzerwahl laden
        templatepath = os.path.join(pluginDirectory('qkan'), u"database/templates")
        if qml_choice == 'uebh':
            template = os.path.join(templatepath, u"Überstauhäufigkeit.qml")
            try:
                vlayer.loadNamedStyle(template)
            except:
                fehlermeldung(u"Fehler in QKan_Results_from_HE",
                          u'Stildatei "Überstauhäufigkeit.qml" wurde nicht gefunden!\nAbbruch!')
        elif qml_choice == 'uebvol':
            template = os.path.join(templatepath, u"Überstauvolumen.qml")
            try:
                vlayer.loadNamedStyle(template)
            except:
                fehlermeldung(u"Fehler in QKan_Results_from_HE",
                          u'Stildatei "Überstauvolumen.qml" wurde nicht gefunden!\nAbbruch!')
        elif qml_choice == 'userqml':
            try:
                vlayer.loadNamedStyle(qmlfileResults)
            except:
                fehlermeldung(u"Fehler in QKan_Results_from_HE",
                          u'Benutzerdefinierte Stildatei {:s} wurde nicht gefunden!\nAbbruch!'.format(qml_choice))

    del dbQK
    del dbHE
