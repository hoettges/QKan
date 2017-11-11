# -*- coding: utf-8 -*-

'''  

  Datenbankmanagement
  ===================

  Definition einer Klasse mit Methoden fuer den Zugriff auf 
  eine SpatiaLite-Datenbank.

  | Dateiname            : dbfunc.py
  | Date                 : September 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de

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
import shutil

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

import pyspatialite.dbapi2 as splite
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from qkan_database import createdbtables

logger = logging.getLogger('QKan')


# Funktionen -------------------------------------------------------------------

def fehlermeldung(title, text, dauer=0):
    logger.error(u'{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)
    iface.messageBar().pushMessage(title, text, level=QgsMessageBar.CRITICAL, duration=dauer)


# Versionskontrolle der QKan-Datenbank

def attrlist2(dbcursl, tablenam):
    """Gibt Spaltenliste zurück."""

    sql = 'PRAGMA table_info("{0:s}")'.format(tablenam)
    dbcursl.execute(sql)
    daten = dbcursl.fetchall()
    # lattr = [el[1] for el in daten if el[2]  == u'TEXT']
    lattr = [el[1] for el in daten]
    return lattr

def version(dbcursl, actversion = '2.1.1'):
    """Checks database version. Database is just connected by the calling procedure.

        :param actversion: aktuelle Version
        :type actversion: text

        :returns: Anpassung erfolgreich: True = alles o.k.
        :rtype: logical
    """

    # ---------------------------------------------------------------------------------------------
    # Aktuelle Version abfragen

    sql = u"""SELECT value
            FROM info
            WHERE subject = 'version'"""

    try:
        dbcursl.execute(sql)
    except BaseException as err:
        fehlermeldung(u"QKan.qgis_utils.version(1) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
        return False

    data = dbcursl.fetchone()
    if data is not None:
        versiondbQK = data[0]
    else:
        sql = u"""INSERT INTO info (subject, value) Values ('version', '1.9.9')"""
        try:
            dbcursl.execute(sql)
        except BaseException as err:
            fehlermeldung(u"QKan.qgis_utils.version(2) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                           "SQL: {}\n".format(sql))
            return False

        versiondbQK = '1.9.9'

    # ---------------------------------------------------------------------------------------------
    # Aktualisierung von Version 1.9.9 und früher

    if versiondbQK == '1.9.9':

        # Tabelle einwohner
        sqllis = [u"""CREATE TABLE IF NOT EXISTS einwohner (
            pk INTEGER PRIMARY KEY AUTOINCREMENT, 
            elnam TEXT, 
            haltnam TEXT, 
            ew REAL, 
            teilgebiet TEXT, 
            kommentar TEXT, 
            createdat TEXT DEFAULT CURRENT_DATE)""", 
        u"""SELECT AddGeometryColumn('einwohner','geom',25832,'POINT',2)"""]
        for sql in sqllis:
            try:
                dbcursl.execute(sql)
            except BaseException as err:
                fehlermeldung(u"QKan.qgis_utils.version(3a) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                               "SQL: {}\nS".format(sql))
                return False

        sqllis = [u"""CREATE TABLE IF NOT EXISTS linkew (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            elnam TEXT,
            haltnam TEXT,
            teilgebiet TEXT)""", 
            u"""SELECT AddGeometryColumn('linksw','geom',25832,'POLYGON',2)""", 
            u"""SELECT AddGeometryColumn('linksw','gbuf',25832,'MULTIPOLYGON',2)""", 
            u"""SELECT AddGeometryColumn('linksw','glink',25832,'LINESTRING',2)"""]
        for sql in sqllis:
            try:
                dbcursl.execute(sql)
            except BaseException as err:
                fehlermeldung(u"QKan.qgis_utils.version(3b) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                               "SQL: {}\nS".format(sql))
                return False

        # Tabelle einleit
        sqllis = [u"""CREATE TABLE IF NOT EXISTS einleit(
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            elnam TEXT,
            haltnam TEXT,
            zufluss REAL,
            teilgebiet TEXT, 
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE)""", 
        u"""SELECT AddGeometryColumn('einleit','geom',25832,'POINT',2)"""]
        for sql in sqllis:
            try:
                dbcursl.execute(sql)
            except BaseException as err:
                fehlermeldung(u"QKan.qgis_utils.version(3c) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                                   "SQL: {}\nS".format(sql))
                return False

        sqllis = [u"""CREATE TABLE IF NOT EXISTS linksw (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                elnam TEXT,
                haltnam TEXT,
                teilgebiet TEXT)""", 
                u"""SELECT AddGeometryColumn('linksw','geom',25832,'POLYGON',2)""", 
                u"""SELECT AddGeometryColumn('linksw','gbuf',25832,'MULTIPOLYGON',2)""", 
                u"""SELECT AddGeometryColumn('linksw','glink',25832,'LINESTRING',2)"""]
        for sql in sqllis:
            try:
                dbcursl.execute(sql)
            except BaseException as err:
                fehlermeldung(u"QKan.qgis_utils.version(3d) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                               "SQL: {}\nS".format(sql))
                return False

        sql = u"""UPDATE info SET value = '2.0.2' WHERE subject = 'version' and value = '1.9.9';"""
        try:
            dbcursl.execute(sql)
        except BaseException as err:
            fehlermeldung(u"QKan.qgis_utils.version(3e) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                           "SQL: {}\n".format(sql))
            return False

        versiondbQK = '2.0.2'

    if versiondbQK == '2.0.2':

        if u'elnam' not in attrlist2(dbcursl,'linksw'):
            logger.debug('linksw.elnam ist nicht in: {}'.format(str(attrlist2(dbcursl,'linksw'))))
            sql = u"""ALTER TABLE linksw ADD COLUMN elnam TEXT"""
            try:
                dbcursl.execute(sql)
            except BaseException as err:
                fehlermeldung(u"QKan.qgis_utils.version(4a) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                               "SQL Nr. 1: {}\n".format(sql))
                return False

        if u'elnam' not in attrlist2(dbcursl,'linkew'):
            logger.debug('linkew.elnam ist nicht in: {}'.format(str(attrlist2(dbcursl,'linkew'))))
            sql = u"""ALTER TABLE linkew ADD COLUMN elnam TEXT"""
            try:
                dbcursl.execute(sql)
            except BaseException as err:
                fehlermeldung(u"QKan.qgis_utils.version(4b) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                               "SQL Nr. 1: {}\n".format(sql))
                return False

        if u'tezgnam' not in attrlist2(dbcursl,'linkfl'):
            logger.debug('linkfl.tezgnam ist nicht in: {}'.format(str(attrlist2(dbcursl,'linkfl'))))
            sql = u"""ALTER TABLE linkfl ADD COLUMN tezgnam TEXT"""
            try:
                dbcursl.execute(sql)
            except BaseException as err:
                fehlermeldung(u"QKan.qgis_utils.version(4b) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                               "SQL Nr. 1: {}\n".format(sql))
                return False

        sql = u"""UPDATE info SET value = '2.1.1' WHERE subject = 'version' and value = '2.0.2';"""
        try:
            dbcursl.execute(sql)
        except BaseException as err:
            fehlermeldung(u"QKan.qgis_utils.version(4c) SQL-Fehler in QKan-DB: \n{}\n".format(err), 
                           "SQL: {}\n".format(sql))
            return False

        versiondbQK = '2.1.1'

    return True


# Pruefung, ob in Tabellen oder Spalten unerlaubte Zeichen enthalten sind
def checknames(text):
    ''' Pruefung auf nicht erlaubte Zeichen in Tabellen- und Spaltennamen.

        :param text: zu pruefende Bezeichnung einer Tabelle oder Tabellenspalte
        :type text: Boolean

        :returns: Testergebnis: True = alles o.k.
        :rtype: logical
    '''

    if max([ord(t) > 127 for t in text]) or ('.' in text) or ('-' in text):
        return False  # Fehler gefunden
    else:
        return True  # alles o.k.


# Hauptprogramm ----------------------------------------------------------------

class DBConnection:
    """SpatiaLite Datenbankobjekt"""

    def __init__(self, dbname=None, tabObject=None, epsg=25832):
        """Constructor.

        :param dbname: Pfad zur SpatiaLite-Datenbankdatei. Falls nicht vorhanden, 
               wird es angelegt.
        :type tabObject: String

        :param tabObject: Vectorlayerobjekt, aus dem die Parameter zum 
            Zugriff auf die SpatiaLite-Tabelle ermittelt werden.
        :type tabObject: QgsVectorLayer
        """

        if dbname is not None:
            # Verbindung zur Datenbank herstellen oder die Datenbank neu erstellen
            if os.path.exists(dbname):
                self.consl = splite.connect(database=dbname, check_same_thread=False)
                self.cursl = self.consl.cursor()

                # Versionsprüfung
                if not version(self.cursl):
                    self.consl.close()
                    return None

            else:
                iface.messageBar().pushMessage("Information", "SpatiaLite-Datenbank wird erstellt. Bitte waren...",
                                               level=QgsMessageBar.INFO)

                datenbank_QKan_Template = os.path.join(os.path.dirname(__file__), "templates", "qkan.sqlite")
                shutil.copyfile(datenbank_QKan_Template, dbname)

                self.consl = splite.connect(database=dbname)
                self.cursl = self.consl.cursor()

                sql = 'SELECT InitSpatialMetadata()'
                self.cursl.execute(sql)

                iface.messageBar().pushMessage("Information", "SpatiaLite-Datenbank ist erstellt!",
                                               level=QgsMessageBar.INFO)
                if not createdbtables(self.consl, self.cursl, epsg):
                    iface.messageBar().pushMessage("Fehler",
                                                   "SpatiaLite-Datenbank: Tabellen konnten nicht angelegt werden",
                                                   level=QgsMessageBar.CRITICAL)
        elif tabObject is not None:
            tabconnect = tabObject.publicSource()
            t_db, t_tab, t_geo, t_sql = tuple(tabconnect.split())
            dbname = t_db.split('=')[1].strip("'")
            self.tabname = t_tab.split('=')[1].strip('"')

            # Pruefung auf korrekte Zeichen in Namen
            if not checknames(self.tabname):
                iface.messageBar().pushMessage("Fehler", "Unzulaessige Zeichen in Tabellenname: " + self.tabname,
                                               level=QgsMessageBar.CRITICAL)
                self.consl = None
            else:

                try:
                    self.consl = splite.connect(database=dbname)
                    self.cursl = self.consl.cursor()
                except:
                    iface.messageBar().pushMessage("Fehler",
                                                   'Fehler beim Öffnen der SpatialLite-Datenbank {:s}!\nAbbruch!'.format(
                                                       dbname), level=QgsMessageBar.CRITICAL)
                    self.consl = None
        else:
            iface.messageBar().pushMessage("Fehler",
                                           'Fehler beim Anbinden der SpatialLite-Datenbank {:s}!\nAbbruch!'.format(
                                               dbname), level=QgsMessageBar.CRITICAL)
            self.consl = None

    def __del__(self):
        """Destructor.
        
        Beendet die Datenbankverbindung.
        """
        self.consl.close()

    def attrlist(self, tablenam):
        """Gibt Spaltenliste zurück."""

        sql = 'PRAGMA table_info("{0:s}")'.format(tablenam)
        self.cursl.execute(sql)
        daten = self.cursl.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == u'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def sql(self, sql):
        """Fuehrt eine SQL-Abfrage aus."""

        try:
            self.cursl.execute(sql)
        except BaseException as err:
            logger.error(u"(1) Fehler in SQL: {}".format(sql))
            logger.error(err)

    def fetchall(self):
        """Gibt alle Daten aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten = self.cursl.fetchall()
        return daten

    def fetchone(self):
        """Gibt einen Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten = self.cursl.fetchone()
        return daten

    def fetchnext(self):
        """Gibt den naechsten Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten = self.cursl.fetchnext()
        return daten

    def commit(self):
        """Schliesst eine SQL-Abfrage ab"""

        self.consl.commit()
