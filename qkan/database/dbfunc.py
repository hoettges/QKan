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
import glob
import datetime

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

import pyspatialite.dbapi2 as splite
from qgis.utils import iface, pluginDirectory

from PyQt4.QtGui import QProgressBar

from qkan_database import createdbtables
from qgis_utils import fortschritt, fehlermeldung

logger = logging.getLogger(u'QKan')

progress_bar = None

    
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

        # Übernahme einiger Attribute in die Klasse
        self.epsg = epsg
        self.dbname = dbname

        # Die nachfolgenden Klassenobjekte dienen dazu, gleichartige (sqlidtext) SQL-Debug-Meldungen 
        # nur einmal pro Sekunde zu erzeugen. 
        self.sqltime = datetime.datetime(2017,1,1,1,0,0)
        self.sqltime = self.sqltime.now()
        self.sqltext = ''
        self.sqlcount = 0
        self.actversion = '2.4.7'
        self.templatepath = os.path.join(pluginDirectory('qkan'), u"database/templates")

        if dbname is not None:
            # Verbindung zur Datenbank herstellen oder die Datenbank neu erstellen
            if os.path.exists(dbname):
                self.consl = splite.connect(database=dbname, check_same_thread=False)
                self.cursl = self.consl.cursor()

                logger.debug(u'dbfund.__init__: Datenbank existiert und Verbindung hergestellt:\n{}'.format(dbname))
                # Versionsprüfung
                if not self.updateVersion():
                    self.consl.close()
                    return None

            else:
                iface.messageBar().pushMessage(u"Information", u"SpatiaLite-Datenbank wird erstellt. Bitte waren...",
                                               level=QgsMessageBar.INFO)

                datenbank_QKan_Template = os.path.join(self.templatepath, u"qkan.sqlite")
                try:
                    shutil.copyfile(datenbank_QKan_Template, dbname)
                except BaseException as err:
                    fehlermeldung(u'Fehler in dbfunc.DBConnection:\n{}\n'.format(err), 
                                  u'Kopieren von: {}\nnach: {}\n nicht möglich'.format(self.templatepath, dbname))
                    return None

                self.consl = splite.connect(database=dbname)
                self.cursl = self.consl.cursor()

                # sql = u'SELECT InitSpatialMetadata()'
                # self.cursl.execute(sql)

                iface.messageBar().pushMessage(u"Information", u"SpatiaLite-Datenbank ist erstellt!",
                                               level=QgsMessageBar.INFO)
                if not createdbtables(self.consl, self.cursl, self.actversion, epsg):
                    iface.messageBar().pushMessage(u"Fehler",
                                                   u"SpatiaLite-Datenbank: Tabellen konnten nicht angelegt werden",
                                                   level=QgsMessageBar.CRITICAL)
        elif tabObject is not None:
            tabconnect = tabObject.publicSource()
            t_db, t_tab, t_geo, t_sql = tuple(tabconnect.split())
            dbname = t_db.split(u'=')[1].strip(u"'")
            self.tabname = t_tab.split(u'=')[1].strip(u'"')

            # Pruefung auf korrekte Zeichen in Namen
            if not checknames(self.tabname):
                iface.messageBar().pushMessage(u"Fehler", u"Unzulaessige Zeichen in Tabellenname: " + self.tabname,
                                               level=QgsMessageBar.CRITICAL)
                self.consl = None
            else:

                try:
                    self.consl = splite.connect(database=dbname)
                    self.cursl = self.consl.cursor()
                except:
                    iface.messageBar().pushMessage(u"Fehler",
                                                   u'Fehler beim Öffnen der SpatialLite-Datenbank {:s}!\nAbbruch!'.format(
                                                       dbname), level=QgsMessageBar.CRITICAL)
                    self.consl = None
        else:
            iface.messageBar().pushMessage(u"Fehler",
                                           u'Fehler beim Anbinden der SpatialLite-Datenbank {:s}!\nAbbruch!'.format(
                                               dbname), level=QgsMessageBar.CRITICAL)
            self.consl = None

    def __del__(self):
        """Destructor.
        
        Beendet die Datenbankverbindung.
        """
        self.consl.close()

    # Hilfsprogramm zum Versionscheck
    def versionolder(self, verlis):
        """Prüft ob die QKan-Datenbank upgedated werden muss"""
        for v1, v2 in zip(self.versionlis, verlis):
            if v1 < v2:
                return True
            elif v1 > v2:
                return False
        return False

    def attrlist(self, tablenam):
        """Gibt Spaltenliste zurück."""

        sql = u'PRAGMA table_info("{0:s}")'.format(tablenam)
        if not self.sql(sql, u'dbfunc.attrlist fuer {}'.format(tablenam)):
            return False

        daten = self.cursl.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == u'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def sql(self, sql, errormessage = u'allgemein', repeatmessage=False, transaction=False):
        """Fuehrt eine SQL-Abfrage aus."""

        try:
            self.cursl.execute(sql)

            # Identische Protokollmeldungen werden für 2 Sekunden unterdrückt...
            if self.sqltext == errormessage and not repeatmessage:
                if (self.sqltime.now() - self.sqltime).seconds <2:
                    self.sqlcount += 1
                    return True
            self.sqltext = errormessage
            self.sqltime = self.sqltime.now()
            if self.sqlcount == 0:
                logger.debug(u'dbfunc.sql: {}\n{}\n'.format(errormessage,sql))
            else:
                logger.debug(u'dbfunc.sql (Nr. {}): {}\n{}\n'.format(self.sqlcount, errormessage, sql))
            self.sqlcount = 0
            return True
        except BaseException as err:
            fehlermeldung(u'dbfunc.sql: SQL-Fehler in {e}'.format(e=errormessage), 
                          u"{e}\n{s}".format(e=repr(err), s=sql))
            # if transaction:
                # self.cursl.commit("ROLLBACK;")
            self.__del__()
            return False

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

    # Versionskontrolle der QKan-Datenbank

    def updateVersion(self):
        """Prüft die Version der Datenbank. 

            :returns: Anpassung erfolgreich: True = alles o.k.
            :rtype: logical
            
            Voraussetzungen: 
             - Die aktuelle Datenbank ist bereits geöffnet. 

            Die aktuelle Versionsnummer steht in der Datenbank: info.version
            Diese wird mit dem Attribut self.actversion verglichen. Bei Differenz werden 
            die nötigen Anpassungen vorgenommen und die Versionsnummer jeweils aktualisiert.
            Falls Tabellenspalten umbenannt oder gelöscht wurden, wird eine Warnmeldung erzeugt
            mit der Empfehlung, das aktuelle Projekt neu zu laden. 
        """

        logger.debug('0 - actversion = {}'.format(self.actversion))

        # ---------------------------------------------------------------------------------------------
        # Aktuelle Version abfragen

        sql = u"""SELECT value
                FROM info
                WHERE subject = 'version'"""

        if not self.sql(sql, u'dbfunc.version (1)'):
            return False

        data = self.cursl.fetchone()
        if data is not None:
            versiondbQK = data[0]
            logger.debug('dbfunc.version: Aktuelle Version der qkan-Datenbank ist {}'.format(versiondbQK))
        else:
            logger.debug('dbfunc.version: Keine Versionsnummer vorhanden. data = {}'.format(repr(data)))
            sql = u"""INSERT INTO info (subject, value) Values ('version', '1.9.9')"""
            if not self.sql(sql, u'dbfunc.version (2)'):
                return False

            versiondbQK = u'1.9.9'

        logger.debug('0 - versiondbQK = {}'.format(versiondbQK))

        self.versionlis = [int(el) for el in versiondbQK.split('.')]

        # ---------------------------------------------------------------------------------------------
        # Aktualisierung von Version 1.9.9 und früher

        if self.versionolder([2, 0, 2]):

            # Tabelle einwohner
            # sqllis = [u"""CREATE TABLE IF NOT EXISTS einwohner (
                # pk INTEGER PRIMARY KEY AUTOINCREMENT, 
                # elnam TEXT, 
                # haltnam TEXT, 
                # ew REAL, 
                # teilgebiet TEXT, 
                # kommentar TEXT, 
                # createdat TEXT DEFAULT CURRENT_DATE)""", 
            # u"""SELECT AddGeometryColumn('einwohner','geom',25832,'POINT',2)"""]
            # for sql in sqllis:
                # if not self.sql(sql, 'dbfunc.version (3a)'):
                    # return False

            # sqllis = [u"""CREATE TABLE IF NOT EXISTS linkew (
                # pk INTEGER PRIMARY KEY AUTOINCREMENT,
                # elnam TEXT,
                # haltnam TEXT,
                # teilgebiet TEXT)""", 
                # u"""SELECT AddGeometryColumn('linksw','geom',25832,'POLYGON',2)""", 
                # u"""SELECT AddGeometryColumn('linksw','gbuf',25832,'MULTIPOLYGON',2)""", 
                # u"""SELECT AddGeometryColumn('linksw','glink',25832,'LINESTRING',2)"""]
            # for sql in sqllis:
                # if not self.sql(sql, 'dbfunc.version (3b)'):
                    # return False

            # Tabelle einleit
            sqllis = [u"""CREATE TABLE IF NOT EXISTS einleit(
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                elnam TEXT,
                haltnam TEXT,
                teilgebiet TEXT, 
                zufluss REAL,
                kommentar TEXT,
                createdat TEXT DEFAULT CURRENT_DATE)""", 
            u"""SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)""".format(self.epsg)]
            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (3c)'):
                    return False

            sqllis = [u"""CREATE TABLE IF NOT EXISTS linksw (
                    pk INTEGER PRIMARY KEY AUTOINCREMENT,
                    elnam TEXT,
                    haltnam TEXT,
                    teilgebiet TEXT)""", 
                    u"""SELECT AddGeometryColumn('linksw','geom',{},'POLYGON',2)""".format(self.epsg), 
                    u"""SELECT AddGeometryColumn('linksw','gbuf',{},'MULTIPOLYGON',2)""".format(self.epsg), 
                    u"""SELECT AddGeometryColumn('linksw','glink',{},'LINESTRING',2)""".format(self.epsg)]
            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (3d)'):
                    return False

            sql = u"""UPDATE info SET value = '2.0.2' WHERE subject = 'version' and value = '1.9.9';"""
            if not self.sql(sql, u'dbfunc.version (3e)'):
                return False

            self.versionlis = [2, 0, 2]


        # ---------------------------------------------------------------------------------------------------------
        if self.versionolder([2, 1, 2]):

            attrlis = self.attrlist(u'linksw')
            if not attrlis:
                fehlermeldung(u'dbfunc.version (2.0.2):', u'attrlis für linksw ist leer')
                return False
            elif u'elnam' not in attrlis:
                logger.debug(u'linksw.elnam ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE linksw ADD COLUMN elnam TEXT"""
                if not self.sql(sql, u'dbfunc.version (2.0.2-1)'):
                    return False
                self.commit()

            attrlis = self.attrlist(u'linkfl')
            if not attrlis:
                fehlermeldung(u'dbfunc.version (2.0.2):', u'attrlis für linkfl ist leer')
                return False
            elif u'tezgnam' not in attrlis:
                logger.debug(u'linkfl.tezgnam ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE linkfl ADD COLUMN tezgnam TEXT"""
                if not self.sql(sql, u'dbfunc.version (2.0.2-3)'):
                    return False
                self.commit()

            sql = u"""UPDATE info SET value = '2.1.2' WHERE subject = 'version' and value = '2.0.2';"""
            if not self.sql(sql, u'dbfunc.version (2.0.2-4)'):
                return False

            self.versionlis = [2, 1, 2]


        # ---------------------------------------------------------------------------------------------------------
        if self.versionolder([2, 2, 0]):
            attrlis = self.attrlist(u'einleit')
            if not attrlis:
                return False
            elif u'ew' not in attrlis:
                logger.debug(u'einleit.ew ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE einleit ADD COLUMN ew REAL"""
                if not self.sql(sql, u'dbfunc.version (2.1.2-1)'):
                    return False
                sql = u"""ALTER TABLE einleit ADD COLUMN einzugsgebiet TEXT"""
                if not self.sql(sql, u'dbfunc.version (2.1.2-2)'):
                    return False
                self.commit()


            sql = u"""CREATE TABLE IF NOT EXISTS einzugsgebiete (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                tgnam TEXT,
                ewdichte REAL,
                wverbrauch REAL,
                stdmittel REAL,
                fremdwas REAL,
                kommentar TEXT,
                createdat TEXT DEFAULT CURRENT_DATE)"""

            if not self.sql(sql, u'dbfunc.version (2.1.2-3)'):
                return False

            sql = u"""SELECT AddGeometryColumn('einzugsgebiete','geom',{},'MULTIPOLYGON',2)""".format(self.epsg)
            if not self.sql(sql, u'dbfunc.version (2.1.2-4)'):
                return False

            sql = u"""SELECT CreateSpatialIndex('einzugsgebiete','geom')"""
            if not self.sql(sql, u'dbfunc.version (2.1.2-5)'):
                return False

            sql = u"""UPDATE info SET value = '2.1.6' WHERE subject = 'version' and value = '2.1.2';"""
            if not self.sql(sql, u'dbfunc.version (2.1.2-6)'):
                return False

            self.versionlis = [2, 2, 0]


        # ---------------------------------------------------------------------------------------------------------
        if self.versionolder([2, 2, 1]):

            attrlis = self.attrlist(u'flaechen')
            if not attrlis:
                return False
            elif u'abflusstyp' not in attrlis:
                logger.debug(u'flaechen.abflusstyp ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE flaechen ADD COLUMN abflusstyp TEXT"""
                if not self.sql(sql, u'dbfunc.version (2.2.0-1)'):
                    return False
                self.commit()

            sql = u"""UPDATE info SET value = '2.2.1' WHERE subject = 'version' and value = '2.2.0';"""
            if not self.sql(sql, u'dbfunc.version (2.2.0-2)'):
                return False

            self.versionlis = [2, 2, 1]


        # ---------------------------------------------------------------------------------------------------------
        if self.versionolder([2, 2, 2]):

            attrlis = self.attrlist(u'flaechen')
            if not attrlis:
                return False
            elif u'abflusstyp' not in attrlis:
                logger.debug(u'flaechen.abflusstyp ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE flaechen ADD COLUMN abflusstyp TEXT"""
                if not self.sql(sql, u'dbfunc.version (2.2.1-1)'):
                    return False
                self.commit()

            sql = u"""UPDATE info SET value = '2.2.2' WHERE subject = 'version' and value = '2.2.1';"""
            if not self.sql(sql, u'dbfunc.version (2.2.1-2)'):
                return False

            self.versionlis = [2, 2, 2]


        # ---------------------------------------------------------------------------------------------------------
        if self.versionolder([2, 2, 3]):

            global progress_bar
            progress_bar = QProgressBar(iface.messageBar())
            progress_bar.setRange(0, 100)
            status_message = iface.messageBar().createMessage(u"", u"Die Datenbank wird an Version 2.2.3 angepasst. Bitte warten...")
            status_message.layout().addWidget(progress_bar)
            iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

            progress_bar.setValue(80)

            # Tabelle flaechen -------------------------------------------------------------

            # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
            # sql = u"""SELECT type, sql FROM sqlite_master WHERE tbl_name='flaechen'"""
            # if not self.sql(sql, u'dbfunc.version.pragma (1)'):
                # return False
            # triggers = self.fetchall()

            # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
            sqllis = [u"""BEGIN TRANSACTION;""",
                      u"""CREATE TABLE flaechen_t (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        flnam TEXT,
                        haltnam TEXT,
                        neigkl INTEGER DEFAULT 0,
                        abflusstyp TEXT, 
                        he_typ INTEGER DEFAULT 0,
                        speicherzahl INTEGER DEFAULT 2,
                        speicherkonst REAL,
                        fliesszeit REAL,
                        fliesszeitkanal REAL,
                        teilgebiet TEXT,
                        regenschreiber TEXT,
                        abflussparameter TEXT,
                        aufteilen TEXT DEFAULT 'nein',
                        kommentar TEXT,
                        createdat TEXT DEFAULT CURRENT_DATE);""",
                      u"""SELECT AddGeometryColumn('flaechen_t','geom',{},'MULTIPOLYGON',2);""".format(self.epsg),
                      u"""INSERT INTO flaechen_t 
                        (      "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit", "fliesszeitkanal",
                               "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", "kommentar", "createdat", "geom")
                        SELECT "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit", "fliesszeitkanal",
                               "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", "kommentar", "createdat", "geom"
                        FROM "flaechen";""",
                      u"""SELECT DiscardGeometryColumn('flaechen','geom')""",
                      u"""DROP TABLE flaechen;""",
                      u"""CREATE TABLE flaechen (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        flnam TEXT,
                        haltnam TEXT,
                        neigkl INTEGER DEFAULT 0,
                        abflusstyp TEXT, 
                        he_typ INTEGER DEFAULT 0,
                        speicherzahl INTEGER DEFAULT 2,
                        speicherkonst REAL,
                        fliesszeit REAL,
                        fliesszeitkanal REAL,
                        teilgebiet TEXT,
                        regenschreiber TEXT,
                        abflussparameter TEXT,
                        aufteilen TEXT DEFAULT 'nein',
                        kommentar TEXT,
                        createdat TEXT DEFAULT CURRENT_DATE);""",
                      u"""SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2);""".format(self.epsg),
                      u"""INSERT INTO flaechen 
                        (      "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit", "fliesszeitkanal",
                               "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", "kommentar", "createdat", "geom")
                        SELECT "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit", "fliesszeitkanal",
                               "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", "kommentar", "createdat", "geom"
                        FROM "flaechen_t";""",
                      u"""SELECT DiscardGeometryColumn('flaechen_t','geom')""",
                      u"""DROP TABLE flaechen_t;"""]

            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (2.2.2-1)', transaction=True):
                    return False

            # 3. Schritt: Trigger wieder herstellen
            # for el in triggers:
                # if el[0] != 'table':
                    # sql = el[1]
                    # logger.debug(u"Trigger 'flaechen' verarbeitet:\n{}".format(el[1]))
                    # if not self.sql(sql, u'dbfunc.version (2.2.2-2)', transaction=True):
                        # return False
                # else:
                    # logger.debug(u"1. Trigger 'table' erkannt:\n{}".format(el[1]))

            # 4. Schritt: Transaction abschließen
            self.commit()

            # 5. Schritt: Spalte abflusstyp aus Spalte he_typ übertragen
            sql = u"""UPDATE flaechen SET abflusstyp = 
                    CASE he_typ 
                        WHEN 0 THEN 'Direktabfluss' 
                        WHEN 1 THEN 'Fließzeiten' 
                        WHEN 2 THEN 'Schwerpunktfließzeit'
                        ELSE NULL END
                    WHERE abflusstyp IS NULL"""

            if not self.sql(sql, u'dbfunc.version (2.2.2-3)'):
                return False


            progress_bar.setValue(20)

            # Tabelle linksw -------------------------------------------------------------

            # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
            # sql = u"""SELECT type, sql FROM sqlite_master WHERE tbl_name='linksw'"""
            # if not self.sql(sql, u'dbfunc.version.pragma (3)'):
                # return False
            # triggers = self.fetchall()

            # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
            sqllis = [u"""BEGIN TRANSACTION;""",
                      u"""CREATE TABLE linksw_t (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        elnam TEXT,
                        haltnam TEXT,
                        teilgebiet TEXT)""",
                      u"""SELECT AddGeometryColumn('linksw_t','geom',{},'POLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linksw_t','gbuf',{},'MULTIPOLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linksw_t','glink',{},'LINESTRING',2)""".format(self.epsg),
                      u"""INSERT INTO linksw_t 
                        (      "elnam", "haltnam", "teilgebiet", "geom", "gbuf", "glink")
                        SELECT "elnam", "haltnam", "teilgebiet", "geom", "gbuf", "glink"
                        FROM "linksw";""",
                      u"""SELECT DiscardGeometryColumn('linksw','geom')""",
                      u"""SELECT DiscardGeometryColumn('linksw','gbuf')""",
                      u"""SELECT DiscardGeometryColumn('linksw','glink')""",
                      u"""DROP TABLE linksw;""",
                      u"""CREATE TABLE linksw (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        elnam TEXT,
                        haltnam TEXT,
                        teilgebiet TEXT)""",
                      u"""SELECT AddGeometryColumn('linksw','geom',{},'POLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linksw','gbuf',{},'MULTIPOLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linksw','glink',{},'LINESTRING',2)""".format(self.epsg),
                      u"""INSERT INTO linksw 
                        (      "elnam", "haltnam", "teilgebiet", "geom", "gbuf", "glink")
                        SELECT "elnam", "haltnam", "teilgebiet", "geom", "gbuf", "glink"
                        FROM "linksw_t";""",
                      u"""SELECT DiscardGeometryColumn('linksw_t','geom')""",
                      u"""SELECT DiscardGeometryColumn('linksw_t','gbuf')""",
                      u"""SELECT DiscardGeometryColumn('linksw_t','glink')""",
                      u"""DROP TABLE linksw_t;"""]

            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (2.2.2-4)', transaction=True):
                    return False

            # 3. Schritt: Trigger wieder herstellen
            # for el in triggers:
                # if el[0] != 'table':
                    # sql = el[1]
                    # logger.debug(u"Trigger 'linksw' verarbeitet:\n{}".format(el[1]))
                    # if not self.sql(sql, u'dbfunc.version (2.2.2-5)', transaction=True):
                        # return False
                # else:
                    # logger.debug(u"1. Trigger 'table' erkannt:\n{}".format(el[1]))

            # 4. Schritt: Transaction abschließen
            self.commit()


            progress_bar.setValue(40)

            # Tabelle linkfl -------------------------------------------------------------

            # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
            # sql = u"""SELECT type, sql FROM sqlite_master WHERE tbl_name='linkfl'"""
            # if not self.sql(sql, u'dbfunc.version.pragma (5)'):
                # return False
            # triggers = self.fetchall()

            # 2. Schritt: Temporäre Tabelle anlegen, Daten rüber kopieren, 
            #             Tabelle löschen und wieder neu anlegen und Daten zurück kopieren

            sqllis = [u"""BEGIN TRANSACTION;""",
                      u"""CREATE TABLE linkfl_t (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        flnam TEXT,
                        haltnam TEXT,
                        tezgnam TEXT,
                        aufteilen TEXT,
                        teilgebiet TEXT);""",
                      u"""SELECT AddGeometryColumn('linkfl_t','geom',{},'MULTIPOLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linkfl_t','gbuf',{},'MULTIPOLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linkfl_t','glink',{},'LINESTRING',2)""".format(self.epsg),
                      u"""INSERT INTO linkfl_t 
                        (      "flnam", "haltnam", "tezgnam", "aufteilen", "teilgebiet", "geom", "gbuf", "glink")
                        SELECT "flnam", "haltnam", "tezgnam", "aufteilen", "teilgebiet", "geom", "gbuf", "glink"
                        FROM "linkfl";""",
                      u"""SELECT DiscardGeometryColumn('linkfl','geom')""",
                      u"""SELECT DiscardGeometryColumn('linkfl','gbuf')""",
                      u"""SELECT DiscardGeometryColumn('linkfl','glink')""",
                      u"""DROP TABLE linkfl;""",
                      u"""CREATE TABLE linkfl (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        flnam TEXT,
                        haltnam TEXT,
                        tezgnam TEXT,
                        aufteilen TEXT,
                        teilgebiet TEXT);""",
                      u"""SELECT AddGeometryColumn('linkfl','geom',{},'MULTIPOLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linkfl','gbuf',{},'MULTIPOLYGON',2)""".format(self.epsg),
                      u"""SELECT AddGeometryColumn('linkfl','glink',{},'LINESTRING',2)""".format(self.epsg),
                      u"""INSERT INTO linkfl 
                        (      "flnam", "haltnam", "tezgnam", "aufteilen", "teilgebiet", "geom", "gbuf", "glink")
                        SELECT "flnam", "haltnam", "tezgnam", "aufteilen", "teilgebiet", "geom", "gbuf", "glink"
                        FROM "linkfl_t";""",
                      u"""SELECT DiscardGeometryColumn('linkfl_t','geom')""",
                      u"""SELECT DiscardGeometryColumn('linkfl_t','gbuf')""",
                      u"""SELECT DiscardGeometryColumn('linkfl_t','glink')""",
                      u"""DROP TABLE linkfl_t;"""]

            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (2.2.2-6)', transaction=True):
                    return False

            # 3. Schritt: Trigger wieder herstellen
            # for el in triggers:
                # if el[0] != 'table':
                    # sql = el[1]
                    # logger.debug(u"Trigger 'linkfl' verarbeitet:\n{}".format(el[1]))
                    # if not self.sql(sql, u'dbfunc.version (2.2.2-7)', transaction=True):
                        # return False
                # else:
                    # logger.debug(u"1. Trigger 'table' erkannt:\n{}".format(el[1]))

            # 4. Schritt: Transaction abschließen
            self.commit()


            progress_bar.setValue(60)

            # Tabelle einleit -------------------------------------------------------------

            # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
            # sql = u"""SELECT type, sql FROM sqlite_master WHERE tbl_name='einleit'"""
            # if not self.sql(sql, u'dbfunc.version.pragma (7)'):
                # return False
            # triggers = self.fetchall()

            # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
            sqllis = [u"""BEGIN TRANSACTION;""",
                      u"""CREATE TABLE einleit_t (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        elnam TEXT,
                        haltnam TEXT,
                        teilgebiet TEXT, 
                        zufluss REAL,
                        ew REAL,
                        einzugsgebiet TEXT,
                        kommentar TEXT,
                        createdat TEXT DEFAULT CURRENT_DATE);""",
                      u"""SELECT AddGeometryColumn('einleit_t','geom',{},'POINT',2)""".format(self.epsg),
                      u"""INSERT INTO einleit_t 
                        (      "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", "createdat", "geom")
                        SELECT "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", "createdat", "geom"
                        FROM "einleit";""",
                      u"""SELECT DiscardGeometryColumn('einleit','geom')""",
                      u"""DROP TABLE einleit;""",
                      u"""CREATE TABLE einleit (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        elnam TEXT,
                        haltnam TEXT,
                        teilgebiet TEXT, 
                        zufluss REAL,
                        ew REAL,
                        einzugsgebiet TEXT,
                        kommentar TEXT,
                        createdat TEXT DEFAULT CURRENT_DATE);""",
                      u"""SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)""".format(self.epsg),
                      u"""INSERT INTO einleit 
                        (      "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", "createdat", "geom")
                        SELECT "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", "createdat", "geom"
                        FROM "einleit_t";""",
                      u"""SELECT DiscardGeometryColumn('einleit_t','geom')""",
                      u"""DROP TABLE einleit_t;"""]

            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (2.2.2-8)', transaction=True):
                    return False

            # 3. Schritt: Trigger wieder herstellen
            # for el in triggers:
                # if el[0] != 'table':
                    # sql = el[1]
                    # logger.debug(u"Trigger 'einleit' verarbeitet:\n{}".format(el[1]))
                    # if not self.sql(sql, u'dbfunc.version (2.2.2-9)', transaction=True):
                        # return False
                # else:
                    # logger.debug(u"1. Trigger 'table' erkannt:\n{}".format(el[1]))

            # 4. Schritt: Transaction abschließen
            sql = u"""UPDATE info SET value = '2.2.3' WHERE subject = 'version' and value = '2.2.2';"""
            if not self.sql(sql, u'dbfunc.version (2.2.2-10)'):
                return False

            self.commit()

            progress_bar.setValue(100)
            status_message.setText(u"Achtung! Benutzerhinweis: Die Datenbank wurde geändert. Bitte QGIS-Projekt neu laden...")
            status_message.setLevel(QgsMessageBar.WARNING)
            iface.messageBar().pushMessage(u"Achtung! Benutzerhinweis!", u"Die Datenbank wurde geändert. Bitte QGIS-Projekt neu laden...",
                                               level=QgsMessageBar.WARNING, duration=0)
                
            # Versionsnummer hochsetzen

            self.versionlis = [2, 2, 3]

        # ---------------------------------------------------------------------------------------------------------
        if self.versionolder([2, 2, 16]):

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
            if not self.sql(sql, u'dbfunc.version (2.4.1-1)'):
                return False

            sql = u"""
                ALTER TABLE profile ADD COLUMN kp_key TEXT
            """
            if not self.sql(sql, u'dbfunc.version (2.4.1-3)'):
                return False

            sql = u"""
                ALTER TABLE entwaesserungsarten ADD COLUMN kp_nr INTEGER
            """
            if not self.sql(sql, u'dbfunc.version (2.4.1-2)'):
                return False

            sqllis = [u"""UPDATE entwaesserungsarten SET kp_nr = 0 WHERE bezeichnung = 'Mischwasser'""",
                      u"""UPDATE entwaesserungsarten SET kp_nr = 1 WHERE bezeichnung = 'Schmutzwasser'""",
                      u"""UPDATE entwaesserungsarten SET kp_nr = 2 WHERE bezeichnung = 'Regenwasser'"""]

            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (2.4.1-4)'):
                    return False

            sql = u"""UPDATE info SET value = '2.4.1' WHERE subject = 'version';"""
            if not self.sql(sql, u'dbfunc.version (2.4.1-5)'):
                return False

            self.commit()

            # Versionsnummer hochsetzen

            self.versionlis = [2, 2, 16]

        # ---------------------------------------------------------------------------------------------------------
        if self.versionolder([2, 4, 3]):

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

            if not self.sql(sql, u'dbfunc.version (2.4.3-1)'):
                return False

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

            if not self.sql(sql, u'dbfunc.version (2.4.3-2)'):
                return False


            sql = u"""UPDATE info SET value = '2.4.3' WHERE subject = 'version';"""
            if not self.sql(sql, u'dbfunc.version (2.4.3-3)'):
                return False

            self.commit()

            # Versionsnummer hochsetzen

            self.versionlis = [2, 4, 3]


        versiondbQK = '.'.join([str(el) for el in self.versionlis])
        logger.debug('1 - versiondbQK = {}'.format(versiondbQK))

        # ---------------------------------------------------------------------------------------------------------
        actverslis = [int(el) for el in self.actversion.split('.')]
        if self.versionolder(actverslis):

            # Formulare aktualisieren ----------------------------------------------------------
            # Spielregel: QKan-Formulare werden ohne Rückfrage aktualisiert. 
            # Falls eigene Formulare gewünscht sind, können diese im selben Verzeichnis liegen, 
            # die Eingabeformulare müssen jedoch andere Namen verwenden, auf die entsprechend 
            # in der Projektdatei verwiesen werden muss. 

            logger.debug('2 - versiondbQK = {}'.format(versiondbQK))

            try:
                projectpath = os.path.dirname(self.dbname)
                if u'eingabemasken' not in os.listdir(projectpath):
                    os.mkdir(os.path.join(projectpath, u'eingabemasken'))
                formpath = os.path.join(projectpath, u'eingabemasken')
                formlist = os.listdir(formpath)

                logger.debug(u"\nEingabeformulare aktualisieren: \n" + 
                              "projectpath = {projectpath}\n".format(projectpath=projectpath) + 
                              "formpath = {formpath}\n".format(formpath=formpath) + 
                              "formlist = {formlist}\n".format(formlist=formlist) + 
                              "templatepath = {templatepath}".format(templatepath=self.templatepath)
                              )

                for formfile in glob.iglob(os.path.join(self.templatepath, u'*.ui')):
                    logger.debug(u"Eingabeformular aktualisieren: {} -> {}".format(formfile, formpath))
                    shutil.copy2(formfile, formpath)
            except BaseException as err:
                fehlermeldung(u'Fehler beim Aktualisieren der Eingabeformulare\n', 
                              u"{e}".format(e=repr(err)))


            sql = u"""UPDATE info SET value = '{}' WHERE subject = 'version';""".format(self.actversion)
            if not self.sql(sql, u'dbfunc.version (aktuell)'):
                return False

        self.commit()
        return True

