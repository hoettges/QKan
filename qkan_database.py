# -*- coding: iso-8859-1 -*-

'''
***************************************************************************
    qkan_database.py

    Datenbankmanagement der QKan-Datenbank

    Erstellt eine leere QKan-Datenbank und legt die Referenztabellen an.

    ---------------------
    Date                 : Oktober 2016
    Copyright            : (C) 2016 by Joerg Hoettges
    Email                : hoettges@fh-aachen.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

'''

__author__ = 'Joerg Hoettges'
__date__ = 'Oktober 2016'
__copyright__ = '(C) 2016, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import os
import pyspatialite.dbapi2 as splite
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.gui import QgsMessageBar

epsg = '31467'

def createdbtables(consl,cursl):
    ''' Erstellt fuer eine neue QKan-Datenbank die zum Import aus Hystem-Extran
        benoetigten Referenztabellen.

        :param consl: Datenbankobjekt der SpatiaLite-QKan-Datenbank
        :type consl: spatialite.dbapi2.Connection

        :param cursl: Zugriffsobjekt der SpatiaLite-QKan-Datenbank
        :type cursl: spatialite.dbapi2.Cursor

        :returns: Testergebnis: True = alles o.k.
        :rtype: logical
    '''

    # Haltungen ----------------------------------------------------------------

    sql = '''
    CREATE TABLE haltungen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    haltnam TEXT,
    schoben TEXT,
    schunten TEXT,
    hoehe REAL,
    breite REAL,
    laenge REAL,
    sohleoben REAL,
    sohleunten REAL,
    deckeloben REAL,
    deckelunten REAL,
    teilgebiet TEXT,
    qzu REAL,
    profilnam TEXT,
    entwart TEXT,
    rohrtyp TEXT,
    ks REAL,
    simstatus INTEGER,
    createdat TEXT DEFAULT CURRENT_DATE,
    xschob REAL,
    yschob REAL,
    xschun REAL,
    yschun REAL)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "Haltungen" konnte nicht erstellt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('haltungen','geom',{:s},'LINESTRING',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "Haltungen" konnte das Attribut "geom" nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    consl.commit()


    # Schaechte ----------------------------------------------------------------

    sql = '''
    CREATE TABLE schaechte (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    schnam TEXT,
    xsch REAL,
    ysch REAL,
    sohlhoehe REAL,
    deckelhoehe REAL,
    durchm REAL,
    druckdicht INTEGER, 
    entwart TEXT,
    teilgebiet INTEGER,
    strasse TEXT,
    simstatus INTEGER,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "Schaechte" konnte nicht erstellt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    sql1 = """SELECT AddGeometryColumn('schaechte','geop',{0:s},'POINT',2);""".format(epsg)
    sql2 = """SELECT AddGeometryColumn('schaechte','geom',{0:s},'MULTIPOLYGON',2);""".format(epsg)
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "Schaechte" konnten die Attribute "geop" und "geom" nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    consl.commit()


    # Profile ------------------------------------------------------------------

    sql = '''
    CREATE TABLE profile (
    pk INTEGER Primary Key,
    profilnam TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "Profile" konnte nicht erstellt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    try:

        daten = ["'Kreisprofil', 1, 1, NULL", 
                 "'Eiprofil 0,67', 3, 5, NULL", 
                 "'Maulprofil 2,00', 16, 4, NULL", 
                 "'TrapezProfil', 68, NULL, NULL", 
                 "'Rechteckprofil', 2, 3, NULL"]

        for ds in daten:
            cursl.execute('INSERT INTO profile (profilnam, he_nr, mu_nr, kp_nr) Values (' + ds + ')')
        
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "Profile" konnten nicht hinzugefuergt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Entwaesserungssysteme ----------------------------------------------------

    sql = '''
    CREATE TABLE entwaesserungsart (
    pk INTEGER PRIMARY KEY, 
    kuerzel TEXT , 
    bedeutung TEXT , 
    bemerkung TEXT , 
    he_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "entwaesserungsart" konnte nicht erstellt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    try:

        daten = ["'MW', 'Mischwasser', NULL, 0", 
                 "'RW', 'Regenwasser', NULL, 1", 
                 "'SW', 'Schmutzwasser', NULL, 2"]

        for ds in daten:
            cursl.execute('INSERT INTO entwaesserungsart (kuerzel, bedeutung, bemerkung, he_nr) Values (' + ds + ')')
        
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "entwaesserungsart" konnten nicht hinzugefuergt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Pumpentypen --------------------------------------------------------------

    sql = '''
    CREATE TABLE pumpentypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT , 
    he_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "pumpentypen" konnte nicht erstellt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    try:

        daten = ["'Offline', 1", 
                 "'Online Schaltstufen', 2", 
                 "'Online Kennlinie', 3", 
                 "'Online Wasserstandsdifferenz', 4", 
                 "'Ideal', 5"]

        for ds in daten:
            cursl.execute('INSERT INTO pumpentypen (bezeichnung, he_nr) Values (' + ds + ')')
        
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "pumpentypen" konnten nicht hinzugefuergt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Pumpen -------------------------------------------------------------------

    sql = '''
    CREATE TABLE pumpen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    schoben TEXT,
    schunten TEXT,
    typ TEXT,
    volanf REAL,
    volges REAL,
    sohle REAL,
    steuersch TEXT,
    einschalthoehe REAL,
    ausschalthoehe REAL,
    createdat TEXT DEFAULT CURRENT_DATE)'''
    
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "pumpen" konnte nicht erstellt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('pumpen','geom',{:s},'LINESTRING',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "pumpen" konnte das Attribut "geom" nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Alles prima gelaufen...
    return True

    
    
# ----------------------------------------------------------------------------------------------------------------------

if __name__ in ('__main__', '__console__', '__builtin__'):

    # Verzeichnis der Testdaten
    pfad = 'C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/modelldb_itwh'
    database_QKan = os.path.join(pfad,'test1.sqlite')

    if os.path.exists(database_QKan):
        os.remove(database_QKan)

    consl = splite.connect(database = database_QKan)
    cursl = consl.cursor()

    # iface.messageBar().pushMessage("Information", "SpatiaLite-Datenbank wird erstellt. Bitte warten...", level=QgsMessageBar.INFO)
    progressMessageBar = iface.messageBar().createMessage("Doing something boring...")
    progress = QProgressBar()
    progress.setMaximum(10)
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)
    progress.setValue(2)
    iface.messageBar().clearWidgets()

    iface.mainWindow().statusBar().showMessage("SpatiaLite-Datenbank wird erstellt. Bitte warten... {} %".format(20))
    import time
    time.sleep(1)

    sql = 'SELECT InitSpatialMetadata(transaction = TRUE)'
    cursl.execute(sql)

    iface.messageBar().pushMessage("Information", "SpatiaLite-Datenbank ist erstellt!", level=QgsMessageBar.INFO)

    createdbtables(consl, cursl)
    consl.close()
