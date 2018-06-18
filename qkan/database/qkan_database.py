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
__version__ = '2.5.1'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import logging
import os

import pyspatialite.dbapi2 as splite
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis_utils import fortschritt, fehlermeldung

logger = logging.getLogger(u'QKan')


def createdbtables(consl, cursl, version=__version__, epsg=25832):
    ''' Erstellt fuer eine neue QKan-Datenbank die zum Import aus Hystem-Extran
        benötigten Referenztabellen.

        :param consl: Datenbankobjekt der SpatiaLite-QKan-Datenbank
        :type consl: spatialite.dbapi2.Connection

        :param cursl: Zugriffsobjekt der SpatiaLite-QKan-Datenbank
        :type cursl: spatialite.dbapi2.Cursor

        :returns: Testergebnis: True = alles o.k.
        :rtype: logical
    '''

    # Haltungen ----------------------------------------------------------------

    sql = u'''CREATE TABLE haltungen (
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
    profilnam TEXT DEFAULT 'Kreisquerschnitt',
    entwart TEXT,
    rohrtyp TEXT,
    ks REAL,
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE,
    xschob REAL,
    yschob REAL,
    xschun REAL,
    yschun REAL)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "Haltungen" konnte nicht erstellt werden')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('haltungen','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('haltungen','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "Haltungen" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Schaechte ----------------------------------------------------------------
    # [knotentyp]: Typ der Verknüpfung (kommt aus Kanal++)

    sql = u'''CREATE TABLE schaechte (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    schnam TEXT,
    xsch REAL,
    ysch REAL,
    sohlhoehe REAL,
    deckelhoehe REAL,
    durchm REAL,
    druckdicht INTEGER DEFAULT 0, 
    ueberstauflaeche REAL,
    entwart TEXT,
    strasse TEXT,
    teilgebiet TEXT,
    knotentyp TEXT,
    auslasstyp TEXT,
    schachttyp TEXT DEFAULT 'Schacht', 
    istspeicher INTEGER, 
    istauslass INTEGER, 
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "Schaechte" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql1 = u"""SELECT AddGeometryColumn('schaechte','geop',{},'POINT',2);""".format(epsg)
    sql2 = u"""SELECT AddGeometryColumn('schaechte','geom',{},'MULTIPOLYGON',2);""".format(epsg)
    sqlindex = u"""SELECT CreateSpatialIndex('schaechte','geom')"""
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "Schaechte" konnten die Attribute "geop" und "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False

    consl.commit()

    # Profile ------------------------------------------------------------------

    sql = u'''CREATE TABLE profile (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    profilnam TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_key TEXT)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "Profile" konnte nicht erstellt werden.')
        consl.close()
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
            cursl.execute(u'INSERT INTO profile (profilnam, he_nr, mu_nr, kp_key) VALUES ({})'.format(ds))

    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabellendaten "Profile" konnten nicht hinzugefuegt werden.')
        consl.close()
        return False

    consl.commit()

    # Geometrie Sonderprofile --------------------------------------------------

    sql = u'''CREATE TABLE profildaten (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    profilnam TEXT, 
    wspiegel REAL, 
    wbreite REAL)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "profildaten" konnte nicht erstellt werden.')
        consl.close()
        return False
    consl.commit()

    # Entwaesserungssysteme ----------------------------------------------------

    sql = u'''CREATE TABLE entwaesserungsarten (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    kuerzel TEXT, 
    bezeichnung TEXT, 
    bemerkung TEXT, 
    he_nr INTEGER, 
    kp_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "entwaesserungsarten" konnte nicht erstellt werden.')
        consl.close()
        return False

    try:

        daten = [u"'MW', 'Mischwasser', NULL, 0, 0",
                 u"'RW', 'Regenwasser', NULL, 1, 2",
                 u"'SW', 'Schmutzwasser', NULL, 2, 1"]

        for ds in daten:
            cursl.execute(
                u'INSERT INTO entwaesserungsarten (kuerzel, bezeichnung, bemerkung, he_nr, kp_nr) VALUES ({})'.format(ds))

    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabellendaten "entwaesserungsarten" konnten nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Pumpentypen --------------------------------------------------------------

    sql = u'''CREATE TABLE pumpentypen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    bezeichnung TEXT, 
    he_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "pumpentypen" konnte nicht erstellt werden.')
        consl.close()
        return False

    try:

        daten = [u"'Offline', 1",
                 u"'Online Schaltstufen', 2",
                 u"'Online Kennlinie', 3",
                 u"'Online Wasserstandsdifferenz', 4",
                 u"'Ideal', 5"]

        for ds in daten:
            cursl.execute(u'INSERT INTO pumpentypen (bezeichnung, he_nr) VALUES ({})'.format(ds))

    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabellendaten "pumpentypen" konnten nicht hinzugefuegt werden.')
        consl.close()
        return False

    consl.commit()

    # Pumpen -------------------------------------------------------------------

    sql = u'''CREATE TABLE pumpen (
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
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "pumpen" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('pumpen','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('pumpen','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "pumpen" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False

    consl.commit()

    # Wehre --------------------------------------------------------------------

    sql = u'''CREATE TABLE wehre (
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
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "wehre" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('wehre','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('wehre','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "wehre" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False

    consl.commit()

    # Einzugsgebiete ------------------------------------------------------------------
    # Entsprechen in HYSTEM-EXTRAN 7.x den Siedlungstypen
    # "flaeche" wird nur für den Import benötigt, wenn keine Flächenobjekte vorhanden sind
    # Verwendung: 
    # Spezifische Verbrauchsdaten in Verbindung mit "einwohner"
    # Einheiten:
    #  - ewdichte: EW/ha
    #  - wverbrauch: l/(EW·d)
    #  - stdmittel: h/d
    #  - fremdwas: %
    #  - flaeche: ha


    sql = u'''CREATE TABLE einzugsgebiete (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    tgnam TEXT,
    ewdichte REAL,
    wverbrauch REAL,
    stdmittel REAL,
    fremdwas REAL,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "Einzugsgebiete" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('einzugsgebiete','geom',{},'MULTIPOLYGON',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('einzugsgebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "Einzugsgebiete" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Teilgebiete ------------------------------------------------------------------
    #  Verwendung:
    # Auswahl von Objekten in verschiedenen Tabellen für verschiedene Aufgaben (z. B. 
    # automatische Verknüpfung von befestigten Flächen und direkten Einleitungen). 


    sql = u'''CREATE TABLE teilgebiete (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    tgnam TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "Teilgebiete" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('teilgebiete','geom',{},'MULTIPOLYGON',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('teilgebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "Teilgebiete" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Gruppen ------------------------------------------------------------------
    # Bearbeitungen, die auf Auswahlen basieren, verwenden ausschließlich die 
    # Tabelle "Teilgebiete". Diese Zuordnung ist sozusagen aktiv, im Gegensatz 
    # zu inaktiven Zuordnungen, die in der Tabelle "gruppen" gespeichert werden. 
    # Mit einem plugin "Zuordnung zu Teilgebieten" können gespeicherte 
    # Zuordnungen gespeichert und geladen werden. Dabei werden die 
    # Zuordnungen für folgende Tabellen verwaltet: 
    #  - "haltungen" 
    #  - "schaechte" 
    #  - "flaechen" 
    #  - "linkfl" 
    #  - "linksw" 
    #  - "tezg" 
    #  - "einleit" 
    #  - "swgebaeude"

    sql = u'''CREATE TABLE gruppen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    pktab INTEGER,
    grnam TEXT,
    teilgebiet TEXT,
    tabelle TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "gruppen" konnte nicht erstellt werden.')
        consl.close()
        return False
    consl.commit()

    # Befestigte und unbefestigte Flächen ------------------------------------------------------

    sql = u'''CREATE TABLE flaechen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    flnam TEXT,
    haltnam TEXT,
    neigkl INTEGER DEFAULT 0,
    abflusstyp TEXT, 
    speicherzahl INTEGER DEFAULT 3,
    speicherkonst REAL,
    fliesszeit REAL,
    fliesszeitkanal REAL,
    teilgebiet TEXT,
    regenschreiber TEXT,
    abflussparameter TEXT,
    aufteilen TEXT DEFAULT 'nein',
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "flaechen" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('flaechen','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "flaechen" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Anbindung Flächen ---------------------------------------------------------------------------
    # Die Tabelle linkfl verwaltet die Anbindung von Flächen an Haltungen. Diese Anbindung
    # wird ausschließlich grafisch verwaltet und beim Export direkt verwendet. 
    # Flächen, bei denen das Attribut "aufteilen" den Wert 'ja' hat, werden mit dem 
    # Werkzeug "QKan_Link_Flaechen" mit allen durch die Verschneidung mit tezg entstehenden
    # Anteilen zugeordnet. 

    sql = u"""CREATE TABLE linkfl (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    flnam TEXT,
    tezgnam TEXT,
    haltnam TEXT,
    aufteilen TEXT,
    teilgebiet TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "linkfl" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql1 = u"""SELECT AddGeometryColumn('linkfl','geom',{epsg},'MULTIPOLYGON',2)""".format(epsg=epsg)
    sql2 = u"""SELECT AddGeometryColumn('linkfl','gbuf',{epsg},'MULTIPOLYGON',2)""".format(epsg=epsg)
    sql3 = u"""SELECT AddGeometryColumn('linkfl','glink',{epsg},'LINESTRING',2)""".format(epsg=epsg)
    sqlindex = u"SELECT CreateSpatialIndex('linkfl','glink')"
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sql3)
        cursl.execute(sqlindex)
    except:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u"QKan_Database (1) SQL-Fehler in SpatiaLite: \n", sql)
        consl.close()
        return False
    consl.commit()

    # Anbindung Direkteinleitungen --------------------------------------------------------------
    # Die Tabelle linksw verwaltet die Anbindung von Gebäuden an Haltungen. Diese Anbindung
    # wird anschließend in das Feld haltnam eingetragen. Der Export erfolgt allerdings anhand
    # der grafischen Verknüpfungen dieser Tabelle. 

    sql = u"""CREATE TABLE linksw (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    elnam TEXT,
    haltnam TEXT,
    teilgebiet TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "linksw" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql1 = u"""SELECT AddGeometryColumn('linksw','geom',{epsg},'POLYGON',2)""".format(epsg=epsg)
    sql2 = u"""SELECT AddGeometryColumn('linksw','gbuf',{epsg},'MULTIPOLYGON',2)""".format(epsg=epsg)
    sql3 = u"""SELECT AddGeometryColumn('linksw','glink',{epsg},'LINESTRING',2)""".format(epsg=epsg)
    sqlindex = u"SELECT CreateSpatialIndex('linksw','geom')"
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sql3)
        cursl.execute(sqlindex)
    except:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u"QKan_Database (2) SQL-Fehler in SpatiaLite: \n", sql)
        consl.close()
        return False
    consl.commit()

    # Teileinzugsgebiete ------------------------------------------------------------------
    # Bei aktivierter Option "check_difftezg" wird je Teileinzugsgebiet eine unbefestigte 
    # Fläche als Differenz zu den innerhalb liegenden Flächen (befestigte und unbefestigte!)
    # gebildet

    sql = u'''CREATE TABLE tezg (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    flnam TEXT,
    haltnam TEXT,
    neigkl INTEGER DEFAULT 1,
    regenschreiber TEXT,
    teilgebiet TEXT,
    abflussparameter TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "tezg" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('tezg','geom',{},'MULTIPOLYGON',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('tezg','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "tezg" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()


    # Direkte Einleitungen ----------------------------------------------------------
    # Erfasst alle Direkteinleitungen mit festem SW-Zufluss (m³/a)
    # Die Zuordnung zum Teilgebiet dient nur der Auswahl

    sql = u'''CREATE TABLE einleit (
    pk INTEGER PRIMARY KEY AUTOINCREMENT,
    elnam TEXT,
    haltnam TEXT,
    teilgebiet TEXT, 
    zufluss REAL,
    ew REAL,
    einzugsgebiet TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "einleit" konnte nicht erstellt werden.')
        consl.close()
        return False

    sql = u"SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)".format(epsg)
    sqlindex = u"SELECT CreateSpatialIndex('einleit','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'In der Tabelle "einleit" konnte das Attribut "geom" nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()


    # Einleitungen aus Wasserverbrauchstabellen ----------------------------------------------------------
    # Die Tabelle wird individuell verwaltet und anschließend auf die Tabelle "einleit" übertragen

    # sql = u'''CREATE TABLE swref (
        # pk INTEGER PRIMARY KEY AUTOINCREMENT, 
        # oi TEXT, 
        # gebnam TEXT, 
        # ags TEXT, 
        # strassenname TEXT, 
        # hausnummer TEXT, 
        # zusatz TEXT, 
        # haltnam TEXT, 
        # wasserverbrauch REAL, 
        # teilgebiet TEXT, 
        # kommentar TEXT, 
        # createdat TEXT DEFAULT CURRENT_DATE)'''

    # try:
        # cursl.execute(sql)
    # except BaseException as err:
        # fehlermeldung(u'Tabelle "swref" konnte nicht erstellt werden: \n{}'.format(repr(err)))
        # consl.close()
        # return False

    # sql = u"SELECT AddGeometryColumn('swref','geom',{},'POINT',2)".format(epsg)
    # sqlindex = u"SELECT CreateSpatialIndex('swref','geom')"
    # try:
        # cursl.execute(sql)
        # cursl.execute(sqlindex)
    # except BaseException as err:
        # fehlermeldung(u'In der Tabelle "swref" konnte das Attribut "geom" nicht hinzugefuegt werden: \n{}'.format(repr(err)))
        # consl.close()
        # return False
    # consl.commit()


    # Simulationsstatus/Planungsstatus -----------------------------------------

    sql = u'''CREATE TABLE simulationsstatus (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "simulationsstatus" konnte nicht erstellt werden.')
        consl.close()
        return False

    try:

        daten = [u"'keine Angabe', 0, NULL, 5",
                 u"'vorhanden', 1, NULL, 0",
                 u"'geplant', 2, NULL, 1",
                 u"'fiktiv', 3, NULL, 2",
                 u"'außer Betrieb (keine Sim.)', 4, NULL, 3",
                 u"'verfüllt (keine Sim.)', 5, NULL, NULL",
                 u"'stillgelegt', NULL, NULL, 4",
                 u"'rückgebaut', NULL, NULL, 6"]

        for ds in daten:
            cursl.execute(u'INSERT INTO simulationsstatus (bezeichnung, he_nr, mu_nr, kp_nr) VALUES ({})'.format(ds))

    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabellendaten "simulationsstatus" konnten nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Auslasstypen -------------------------------------------------------------

    sql = u'''CREATE TABLE auslasstypen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "auslasstypen" konnten nicht erstellt werden.')
        consl.close()
        return False

    try:

        daten = [u"'frei', 0, NULL, NULL",
                 u"'normal', 1, NULL, NULL",
                 u"'konstant', 2, NULL, NULL",
                 u"'Tide', 3, NULL, NULL",
                 u"'Zeitreihe', 4, NULL, NULL"]

        for ds in daten:
            cursl.execute(u'INSERT INTO auslasstypen (bezeichnung, he_nr, mu_nr, kp_nr) VALUES ({})'.format(ds))

    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabellendaten "auslasstypen" konnten nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Abflussparameter -------------------------------------------------------------

    sql = u'''CREATE TABLE abflussparameter (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    apnam TEXT, 
    anfangsabflussbeiwert REAL, 
    endabflussbeiwert REAL, 
    benetzungsverlust REAL, 
    muldenverlust REAL, 
    benetzung_startwert REAL, 
    mulden_startwert REAL, 
    bodenklasse TEXT, 
    kommentar TEXT, 
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "abflussparameter" konnten nicht erstellt werden.')
        consl.close()
        return False

    try:
        daten = [u"'$Default_Bef', 'Exportiert mit qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, 'NULL', '13.01.2011 08:44:50'",
                 u"'$Default_Unbef', 'Exportiert mit qkhe', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', '13.01.2011 08:44:50'"]

        for ds in daten:
            sql = u"""INSERT INTO abflussparameter
                     ( 'apnam', 'kommentar', 'anfangsabflussbeiwert', 'endabflussbeiwert', 'benetzungsverlust', 
                       'muldenverlust', 'benetzung_startwert', 'mulden_startwert', 'bodenklasse', 
                       'createdat') Values ({})""".format(ds)
            cursl.execute(sql)

    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabellendaten "abflussparameter" konnten nicht hinzugefuegt werden.')
        consl.close()
        return False
    consl.commit()

    # Bodenklasse -------------------------------------------------------------

    sql = u'''CREATE TABLE bodenklassen (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    bknam TEXT, 
    infiltrationsrateanfang REAL,
    infiltrationsrateende REAL,
    infiltrationsratestart REAL,
    rueckgangskonstante REAL,
    regenerationskonstante REAL,
    saettigungswassergehalt REAL,
    kommentar TEXT, 
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabelle "bodenklassen" konnten nicht erstellt werden.')
        consl.close()
        return False

    daten = [u"'VollDurchlaessig', 10, 9, 10, 144, 1.584, 100, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
             u"'Sand', 2.099, 0.16, 1.256, 227.9, 1.584, 12, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
             u"'SandigerLehm', 1.798, 0.101, 1.06, 143.9, 0.72, 18, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
             u"'LehmLoess', 1.601, 0.081, 0.94, 100.2, 0.432, 23, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
             u"'Ton', 1.9, 0.03, 1.087, 180, 0.144, 16, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
             u"'Undurchlaessig', 0, 0, 0, 100, 1, 0, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
             u"NULL, 0, 0, 0, 0, 0, 0, '13.01.2011 08:44:50', 'nur für interne QKan-Aufgaben'"]

    for ds in daten:
        try:
            sql = u"""INSERT INTO bodenklassen
                     ( 'bknam', 'infiltrationsrateanfang', 'infiltrationsrateende', 'infiltrationsratestart', 
                       'rueckgangskonstante', 'regenerationskonstante', 'saettigungswassergehalt', 
                       'createdat', 'kommentar') Values ({})""".format(ds)
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Tabellendaten "bodenklassen" konnten nicht hinzugefuegt werden: \n{}\n'.format(err), sql)
            consl.close()
            return False
    consl.commit()

    # Kennlinie Speicherbauwerke -----------------------------------------------

    sql = u'''CREATE TABLE speicherkennlinien (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    schnam TEXT, 
    wspiegel REAL, 
    oberfl REAL)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Fehler beim Erzeugen der Tabelle "Speicherkennlinien".')
        consl.close()
        return False
    consl.commit()

    # Hilfstabelle für den DYNA-Export -----------------------------------------

    sql = u"""
        CREATE TABLE IF NOT EXISTS dynahal (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            haltnam TEXT,
            schoben TEXT,
            schunten TEXT,
            teilgebiet TEXT,
            kanalnummer TEXT,
            haltungsnummer TEXT,
            anzobob INTEGER,
            anzobun INTEGER,
            anzunun INTEGER,
            anzunob INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Fehler beim Erzeugen der Tabelle "dynahal".')
        consl.close()
        return False
    consl.commit()
    
    # Allgemeiner Informationen -----------------------------------------------

    sql = u'''CREATE TABLE info (
    pk INTEGER PRIMARY KEY AUTOINCREMENT, 
    subject TEXT, 
    value TEXT,
    createdat TEXT DEFAULT CURRENT_DATE)'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.version: Fehler {}'.format(err), 
                      u'Fehler beim Erzeugen der Tabelle "Info".')
        consl.close()
        return False

    # Plausibilitätskontrollen --------------------------------------------------

    # Prüfung der Anbindungen in "linkfl" auf eindeutige Zuordnung zu Flächen und Haltungen

    sql = u'''CREATE VIEW IF NOT EXISTS "v_linkfl_check" AS 
            WITH lfok AS
            (   SELECT 
                    lf.pk AS "pk",
                    lf.flnam AS "linkfl_nam", 
                    lf.haltnam AS "linkfl_haltnam", 
                    fl.flnam AS "flaech_nam",
                    tg.flnam AS "tezg_nam",
                    min(lf.pk) AS pkmin, 
                    max(lf.pk) AS pkmax,
                    count(*) AS anzahl
                FROM linkfl AS lf
                LEFT JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam
                WHERE fl.aufteilen = "ja" and fl.aufteilen IS NOT NULL
                GROUP BY fl.flnam, tg.flnam
                UNION
                SELECT 
                    lf.pk AS "pk",
                    lf.flnam AS "linkfl_nam", 
                    lf.haltnam AS "linkfl_haltnam", 
                    fl.flnam AS "flaech_nam",
                    NULL AS "tezg_nam",
                    min(lf.pk) AS pkmin, 
                    max(lf.pk) AS pkmax,
                    count(*) AS anzahl
                FROM linkfl AS lf
                LEFT JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                WHERE fl.aufteilen <> "ja" OR fl.aufteilen IS NULL
                GROUP BY fl.flnam)
            SELECT pk, anzahl, CASE WHEN anzahl > 1 THEN 'mehrfach vorhanden' WHEN flaech_nam IS NULL THEN 'Keine Fläche' WHEN linkfl_haltnam IS NULL THEN  'Keine Haltung' ELSE 'o.k.' END AS fehler
            FROM lfok'''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.version: Fehler {}'.format(err), 
                      u'Fehler beim Erzeugen der Plausibilitätskontrolle "v_linkfl_check".')
        consl.close()
        return False

    # Feststellen der Flächen ohne Anbindung

    sql = u'''CREATE VIEW IF NOT EXISTS "v_flaechen_ohne_linkfl" AS 
            SELECT 
                fl.pk, 
                fl.flnam AS "flaech_nam",
                fl.aufteilen AS "flaech_aufteilen", 
                'Verbindung fehlt' AS "Fehler"
            FROM flaechen AS fl
            LEFT JOIN linkfl AS lf
            ON lf.flnam = fl.flnam
            LEFT JOIN tezg AS tg
            ON tg.flnam = lf.tezgnam
            WHERE ( (fl.aufteilen <> "ja" or fl.aufteilen IS NULL) AND
                     lf.pk IS NULL) OR
                  (  fl.aufteilen = "ja" AND fl.aufteilen IS NOT NULL AND 
                     lf.pk IS NULL)
            UNION
            VALUES
                (0, '', '', 'o.k.') '''

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.version: Fehler {}'.format(err), 
                      u'Fehler beim Erzeugen der Plausibilitätskontrolle "v_flaechen_ohne_linkfl".')
        consl.close()
        return False

    # Abschluss --------------------------------------------------------------------

    # Aktuelle Version eintragen
    sql = u"""INSERT INTO info (subject, value) VALUES ('version', '{}'); \n""".format(version)
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u'qkan_database.createdbtables: {}'.format(err), 
                      u'Fehler beim Erzeugen der Tabelle "Info".')
        consl.close()
        return False
    consl.commit()

    fortschritt(u'Tabellen erstellt...', 0.01)

    # ----------------------------------------------------------------------------------------------------------------------
    # Alles prima gelaufen...

    return True


# ----------------------------------------------------------------------------------------------------------------------

if __name__ in ('__main__', '__console__', '__builtin__'):

    # Verzeichnis der Testdaten
    pfad = u'C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/modelldb_itwh'
    database_QKan = os.path.join(pfad, u'test1.sqlite')

    if os.path.exists(database_QKan):
        os.remove(database_QKan)

    consl = splite.connect(database=database_QKan)
    cursl = consl.cursor()

    # iface.messageBar().pushMessage("Information", "SpatiaLite-Datenbank wird erstellt. Bitte warten...",
    #     level=QgsMessageBar.INFO)
    progressMessageBar = iface.messageBar().createMessage("Doing something boring...")
    progress = QProgressBar()
    progress.setMaximum(10)
    progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)
    progress.setValue(2)
    iface.messageBar().clearWidgets()

    iface.mainWindow().statusBar().showMessage("SpatiaLite-Datenbank wird erstellt. Bitte warten... {} %".format(20))
    import time

    time.sleep(1)

    sql = u'SELECT InitSpatialMetadata(transaction = TRUE)'
    cursl.execute(sql)

    iface.messageBar().pushMessage("Information", "SpatiaLite-Datenbank ist erstellt!", level=QgsMessageBar.INFO)

    createdbtables(consl, cursl, version='1.0.0')
    consl.close()
