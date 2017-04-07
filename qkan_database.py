# -*- coding: utf-8 -*-

'''

  Datenbankmanagement der QKan-Datenbank
  ======================================

  Erstellt eine leere QKan-Datenbank und legt die Referenztabellen an.

  | Dateiname            : qkan_database.py
  | Date                 : October 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  
  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.                                   
  
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

def createdbtables(consl,cursl,epsg=25832):
    ''' Erstellt fuer eine neue QKan-Datenbank die zum Import aus Hystem-Extran
        benötigten Referenztabellen.

        :param consl: Datenbankobjekt der SpatiaLite-QKan-Datenbank
        :type consl: spatialite.dbapi2.Connection

        :param cursl: Zugriffsobjekt der SpatiaLite-QKan-Datenbank
        :type cursl: spatialite.dbapi2.Cursor

        :returns: Testergebnis: True = alles o.k.
        :rtype: logical
    '''

    # Protokoll-Tabelle anlegen

    sql = 'CREATE TABLE protokoll (inhalt TEXT, zeit TEXT CONSTRAINT log_timestamp DEFAULT CURRENT_TIMESTAMP)'

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "protokoll" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()

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
    simstatus TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE,
    xschob REAL,
    yschob REAL,
    xschun REAL,
    yschun REAL)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "Haltungen" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('haltungen','geom',{},'LINESTRING',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "Haltungen" konnte das Attribut "geom" ' + 
            'nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Schaechte ----------------------------------------------------------------
    # [knotentyp]: Typ der Verknüpfung (kommt aus Kanal++)

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
    ueberstauflaeche REAL,
    entwart TEXT,
    strasse TEXT,
    teilgebiet TEXT,
    knotentyp TEXT,
    auslasstyp TEXT,
    schachttyp TEXT, 
    istspeicher INTEGER, 
    istauslass INTEGER, 
    simstatus TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "Schaechte" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    sql1 = """SELECT AddGeometryColumn('schaechte','geop',{},'POINT',2);""".format(epsg)
    sql2 = """SELECT AddGeometryColumn('schaechte','geom',{},'MULTIPOLYGON',2);""".format(epsg)
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "Schaechte" konnten die Attribute "geop" ' + 
            'und "geom" nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Auslaesse ----------------------------------------------------------------

    # sql = '''
    # CREATE TABLE auslaesse (
    # pk INTEGER PRIMARY KEY AUTOINCREMENT,
    # schnam TEXT,
    # xsch REAL,
    # ysch REAL,
    # sohlhoehe REAL,
    # deckelhoehe REAL,
    # auslasstyp TEXT,
    # simstatus TEXT,
    # kommentar TEXT,
    # createdat TEXT DEFAULT CURRENT_DATE)'''

    # try:
        # cursl.execute(sql)
    # except:
        # iface.messageBar().pushMessage("Fehler", 'Tabelle "Auslaesse" konnte nicht erstellt werden!\nAbbruch!',
        #     level=QgsMessageBar.CRITICAL)
        # return False

    # sql1 = """SELECT AddGeometryColumn('auslaesse','geop',{},'POINT',2);""".format(epsg)
    # sql2 = """SELECT AddGeometryColumn('auslaesse','geom',{},'MULTIPOLYGON',2);""".format(epsg)
    # try:
        # cursl.execute(sql1)
        # cursl.execute(sql2)
    # except:
        # iface.messageBar().pushMessage("Fehler", 'In der Tabelle "Auslaesse" konnten das Attribute "geom" ' + 
        #     'nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        # return False

    # consl.commit()


    # Speicherschaechte --------------------------------------------------------

    # sql = '''
    # CREATE TABLE speicherschaechte (
    # pk integer PRIMARY KEY AUTOINCREMENT,
    # schnam TEXT,
    # xsch REAL,
    # ysch REAL,
    # sohlhoehe REAL,
    # deckelhoehe REAL,
    # ueberstauflaeche REAL,
    # exponent REAL,
    # koeffizient REAL,
    # konstante REAL,
    # simstatus TEXT,
    # kommentar TEXT,
    # createdat TEXT DEFAULT CURRENT_DATE)'''

    # try:
        # cursl.execute(sql)
    # except:
        # iface.messageBar().pushMessage("Fehler", 'Tabelle "Speicherschaechte" konnte nicht erstellt werden!\nAbbruch!',
        #     level=QgsMessageBar.CRITICAL)
        # return False

    # sql1 = """SELECT AddGeometryColumn('speicherschaechte','geop',{},'POINT',2);""".format(epsg)
    # sql2 = """SELECT AddGeometryColumn('speicherschaechte','geom',{},'MULTIPOLYGON',2);""".format(epsg)
    # try:
        # cursl.execute(sql1)
        # cursl.execute(sql2)
    # except:
        # iface.messageBar().pushMessage("Fehler", 'In der Tabelle "Speicherschaechte" konnten die Attribute' + 
        #     ' "geop" und "geom" nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        # return False

    # consl.commit()


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
        iface.messageBar().pushMessage("Fehler", 'Tabelle "Profile" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    try:

        daten = [u"'Kreisquerschnitt', 1, NULL, NULL",
                u"'Rechteckquerschnitt', 2, NULL, NULL",
                u"'Eiquerschnitt 0,67', 3, NULL, NULL",
                u"'Maulquerschnitt 1,20', 4, NULL, NULL",
                u"'Halbschalenquerschnitt, offen 2,00', 5, NULL, NULL",
                u"'Kreisquerschnitt, gestreckt 0,89', 6, NULL, NULL",
                u"'Kreisquerschnitt, \xfcberh\xf6ht 0,67', 7, NULL, NULL",
                u"'Eiquerschnitt, \xfcberh\xf6ht 0,57', 8, NULL, NULL",
                u"'Eiquerschnitt, breit 0,80', 9, NULL, NULL",
                u"'Eiquerschnitt, gedr\xfcckt 1,00', 10, NULL, NULL",
                u"'Drachenquerschnitt 1,00', 11, NULL, NULL",
                u"'Maulquerschnitt 1,33', 12, NULL, NULL",
                u"'Maulquerschnitt, \xfcberh\xf6ht 1,00', 13, NULL, NULL",
                u"'Maulquerschnitt, gedr\xfcckt 0,89', 14, NULL, NULL",
                u"'Maulquerschnitt, gestreckt 1,14', 15, NULL, NULL",
                u"'Maulquerschnitt, gestaucht 2,00', 16, NULL, NULL",
                u"'Haubenquerschnitt 0,89', 17, NULL, NULL",
                u"'Parabelquerschnitt 1,00', 18, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle 2,00', 19, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle 1,00', 20, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle 0,50', 21, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 2,00, b=0,2B', 22, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 1,00, b=0,2B', 23, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 0,50, b=0,2B', 24, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 2,00, b=0,4B', 25, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 1,00, b=0,4B', 26, NULL, NULL",
                u"'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 0,50, b=0,4B', 27, NULL, NULL",
                u"'Trapezquerschnitt', 68, NULL, NULL"]

        for ds in daten:
            cursl.execute(u'INSERT INTO profile (profilnam, he_nr, mu_nr, kp_nr) Values (' + ds + ')')
        
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "Profile" konnten nicht hinzugefuegt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Geometrie Sonderprofile --------------------------------------------------

    sql = '''
    CREATE TABLE profildaten (
    pk INTEGER PRIMARY KEY, 
    profilnam TEXT, 
    wspiegel REAL, 
    wbreite REAL)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "profildaten" konnte nicht erstellt werden!\nAbbruch!', 
            level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Entwaesserungssysteme ----------------------------------------------------

    sql = '''
    CREATE TABLE entwaesserungsart (
    pk INTEGER PRIMARY KEY, 
    kuerzel TEXT, 
    bezeichnung TEXT, 
    bemerkung TEXT, 
    he_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "entwaesserungsart" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    try:

        daten = ["'MW', 'Mischwasser', NULL, 0", 
                 "'RW', 'Regenwasser', NULL, 1", 
                 "'SW', 'Schmutzwasser', NULL, 2"]

        for ds in daten:
            cursl.execute('INSERT INTO entwaesserungsart (kuerzel, bezeichnung, bemerkung, he_nr) Values (' + ds + ')')
        
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "entwaesserungsart" konnten nicht hinzugefuegt ' + 
            'werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Pumpentypen --------------------------------------------------------------

    sql = '''
    CREATE TABLE pumpentypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT, 
    he_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "pumpentypen" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
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
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "pumpentypen" konnten nicht hinzugefuegt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Pumpen -------------------------------------------------------------------

    sql = '''
    CREATE TABLE pumpen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    pnam TEXT,
    schoben TEXT,
    schunten TEXT,
    pumpentyp TEXT,
    volanf REAL,
    volges REAL,
    sohle REAL,
    steuersch TEXT,
    einschalthoehe REAL,
    ausschalthoehe REAL,
    simstatus TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''
    
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "pumpen" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('pumpen','geom',{},'LINESTRING',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "pumpen" konnte das Attribut "geom" ' + 
            'nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Wehre --------------------------------------------------------------------

    sql = '''CREATE TABLE wehre (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    wnam TEXT,
    schoben TEXT,
    schunten TEXT,
    wehrtyp TEXT,
    schwellenhoehe REAL,
    kammerhoehe REAL,
    laenge REAL,
    uebeiwert REAL,
    aussentyp TEXT,
    aussenwsp REAL,
    simstatus TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''
    
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "wehre" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('wehre','geom',{},'LINESTRING',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "wehre" konnte das Attribut "geom" ' + 
            'nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Teilgebiete ------------------------------------------------------------------
    # Entsprechen in HYSTEM-EXTRAN 7.x den Siedlungstypen
    # [flaeche] wird nur für den Import benötigt, wenn keine Flächenobjekte vorhanden sind

    sql = '''CREATE TABLE teilgebiete (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        tgnam TEXT,
        ewdichte REAL,
        wverbrauch REAL,
        stdmittel REAL,
        fremdwas REAL,
        flaeche REAL,
        kommentar TEXT,
        createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "Teilgebiete" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('teilgebiete','geom',{},'MULTIPOLYGON',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "Teilgebiete" konnte das Attribut "geom" ' + 
            'nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Befestigte und unbefestigte Flächen ------------------------------------------------------

    sql = '''CREATE TABLE flaechen (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        flnam TEXT,
        haltnam TEXT,
        neigkl INTEGER,
        teilgebiet TEXT,
        regenschreiber TEXT,
        abflussparameter TEXT,
        kommentar TEXT,
        createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "flaechen" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "flaechen" konnte das Attribut "geom" ' + 
            'nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Teileinzugsgebiete ------------------------------------------------------------------
    # Bei aktivierte Option "check_difftezg" wird je Teileinzugsgebiet eine unbefestigte 
    # Fläche als Differenz zu den innerhalb liegenden Flächen (befestigte und unbefestigte!)
    # gebildet

    sql = '''CREATE TABLE tezg (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        flnam TEXT,
        haltnam TEXT,
        neigkl INTEGER,
        regenschreiber TEXT,
        abflussparameter TEXT,
        kommentar TEXT,
        createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "tezg" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    sql = "SELECT AddGeometryColumn('tezg','geom',{},'MULTIPOLYGON',2)".format(epsg)
    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'In der Tabelle "tezg" konnte das Attribut "geom" ' + 
            'nicht hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Simulationsstatus/Planungsstatus -----------------------------------------

    sql = '''
    CREATE TABLE simulationsstatus (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "simulationsstatus" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    try:

        daten = ["'keine Angabe', 0, NULL, NULL", 
                 "'vorhanden', 1, NULL, NULL", 
                 "'geplant', 2, NULL, NULL", 
                 "'fiktiv', 3, NULL, NULL", 
                 u"'außer Betrieb (keine Sim.)', 4, NULL, NULL", 
                 u"'verfüllt (keine Sim.)', 5, NULL, NULL"]

        for ds in daten:
            cursl.execute('INSERT INTO simulationsstatus (bezeichnung, he_nr, mu_nr, kp_nr) Values (' + 
                            ds + ')')
        
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "simulationsstatus" konnten nicht ' + 
            'hinzugefuegt werden!\nAbbruch!', level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Auslasstypen -------------------------------------------------------------

    sql = '''
    CREATE TABLE auslasstypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "auslasstypen" konnte nicht erstellt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False

    try:

        daten = ["'frei', 0, NULL, NULL", 
                 "'normal', 1, NULL, NULL", 
                 "'konstant', 2, NULL, NULL", 
                 "'Tide', 3, NULL, NULL", 
                 "'Zeitreihe', 4, NULL, NULL"]

        for ds in daten:
            cursl.execute('INSERT INTO auslasstypen (bezeichnung, he_nr, mu_nr, kp_nr) Values (' + 
                            ds + ')')
        
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabellendaten "auslasstypen" konnten nicht hinzugefuegt werden!\nAbbruch!',
            level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()


    # Abflussparameter -------------------------------------------------------------

    sql = '''
    CREATE TABLE abflussparameter (
    pk INTEGER PRIMARY KEY, 
    apnam TEXT, 
    kommentar TEXT, 
    anfangsabflussbeiwert REAL, 
    endabflussbeiwert REAL, 
    benetzungsverlust REAL, 
    muldenverlust REAL, 
    benetzung_startwert REAL, 
    mulden_startwert REAL, 
    bodenklasse TEXT, 
    interz_jahresganglinie TEXT, 
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "abflussparameter" konnte nicht erstellt werden!\nAbbruch!', 
            level=QgsMessageBar.CRITICAL)
        return False


    # Kennlinie Speicherbauwerke -----------------------------------------------

    sql = '''
    CREATE TABLE speicherkennlinie (
    pk INTEGER PRIMARY KEY, 
    schnam TEXT, 
    wspiegel REAL, 
    oberfl REAL)'''

    try:
        cursl.execute(sql)
    except:
        iface.messageBar().pushMessage("Fehler", 'Tabelle "speicherkennlinie" konnte nicht erstellt werden!\nAbbruch!', 
            level=QgsMessageBar.CRITICAL)
        return False
    consl.commit()



# ----------------------------------------------------------------------------------------------------------------------
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

    # iface.messageBar().pushMessage("Information", "SpatiaLite-Datenbank wird erstellt. Bitte warten...",
    #     level=QgsMessageBar.INFO)
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
