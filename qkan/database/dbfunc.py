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
from qgis_utils import fortschritt, fehlermeldung

logger = logging.getLogger(u'QKan')


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

        # Übernahme von epsg in die Klasse
        self.epsg = epsg

        if dbname is not None:
            # Verbindung zur Datenbank herstellen oder die Datenbank neu erstellen
            if os.path.exists(dbname):
                self.consl = splite.connect(database=dbname, check_same_thread=False)
                self.cursl = self.consl.cursor()

                # Versionsprüfung
                if not self.version():
                    self.consl.close()
                    return None

            else:
                iface.messageBar().pushMessage(u"Information", u"SpatiaLite-Datenbank wird erstellt. Bitte waren...",
                                               level=QgsMessageBar.INFO)

                datenbank_QKan_Template = os.path.join(os.path.dirname(__file__), u"templates", u"qkan.sqlite")
                shutil.copyfile(datenbank_QKan_Template, dbname)

                self.consl = splite.connect(database=dbname)
                self.cursl = self.consl.cursor()

                sql = u'SELECT InitSpatialMetadata()'
                self.cursl.execute(sql)

                iface.messageBar().pushMessage(u"Information", u"SpatiaLite-Datenbank ist erstellt!",
                                               level=QgsMessageBar.INFO)
                if not createdbtables(self.consl, self.cursl, epsg):
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

    def attrlist(self, tablenam):
        """Gibt Spaltenliste zurück."""

        sql = u'PRAGMA table_info("{0:s}")'.format(tablenam)
        if not self.sql(sql, u'dbfunc.attrlist'):
            return False

        daten = self.cursl.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == u'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def sql(self, sql, errormessage = u'allgemein'):
        """Fuehrt eine SQL-Abfrage aus."""

        try:
            self.cursl.execute(sql)
            logger.debug(u'dbfunc.sql: {}\n{}\n'.format(errormessage,sql))
            return True
        except BaseException as err:
            fehlermeldung(u'SQL-Fehler in {e}'.format(e=errormessage), 
                          u"{e}\n{s}".format(e=err, s=sql))
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

    def version(self, actversion = u'2.2.1'):
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

        if not self.sql(sql, u'dbfunc.version (1)'):
            return False

        data = self.cursl.fetchone()
        if data is not None:
            versiondbQK = data[0]
        else:
            sql = u"""INSERT INTO info (subject, value) Values ('version', '1.9.9')"""
            if not self.sql(sql, u'dbfunc.version (2)'):
                return False

            versiondbQK = u'1.9.9'

        # ---------------------------------------------------------------------------------------------
        # Aktualisierung von Version 1.9.9 und früher

        if versiondbQK == u'1.9.9':

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
            u"""SELECT AddGeometryColumn('einleit','geom',25832,'POINT',2)"""]
            for sql in sqllis:
                if not self.sql(sql, u'dbfunc.version (3c)'):
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
                if not self.sql(sql, u'dbfunc.version (3d)'):
                    return False

            sql = u"""UPDATE info SET value = '2.0.2' WHERE subject = 'version' and value = '1.9.9';"""
            if not self.sql(sql, u'dbfunc.version (3e)'):
                return False

            versiondbQK = u'2.0.2'


        if versiondbQK == u'2.0.2':

            attrlis = self.attrlist(u'linksw')
            if not attrlis:
                return False
            elif u'elnam' not in attrlis:
                logger.debug(u'linksw.elnam ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE linksw ADD COLUMN elnam TEXT"""
                if not self.sql(sql, u'dbfunc.version (4a)'):
                    return False
                self.commit()

            attrlis = self.attrlist(u'linkew')
            if not attrlis:
                return False
            elif u'elnam' not in attrlis:
                logger.debug(u'linkew.elnam ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE linkew ADD COLUMN elnam TEXT"""
                if not self.sql(sql, u'dbfunc.version (4b)'):
                    return False
                self.commit()

            attrlis = self.attrlist(u'linkfl')
            if not attrlis:
                return False
            elif u'tezgnam' not in attrlis:
                logger.debug(u'linkfl.tezgnam ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE linkfl ADD COLUMN tezgnam TEXT"""
                if not self.sql(sql, u'dbfunc.version (4c)'):
                    return False
                self.commit()

            sql = u"""UPDATE info SET value = '2.1.2' WHERE subject = 'version' and value = '2.0.2';"""
            if not self.sql(sql, u'dbfunc.version (4d)'):
                return False

            versiondbQK = u'2.1.2'


        if versiondbQK == u'2.1.2':
            attrlis = self.attrlist(u'einleit')
            if not attrlis:
                return False
            elif u'ew' not in attrlis:
                logger.debug(u'einleit.ew ist nicht in: {}'.format(str(attrlis)))
                sql = u"""ALTER TABLE einleit ADD COLUMN ew REAL"""
                if not self.sql(sql, u'dbfunc.version (4f)'):
                    return False
                sql = u"""ALTER TABLE einleit ADD COLUMN einzugsgebiet TEXT"""
                if not self.sql(sql, u'dbfunc.version (4g)'):
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

            if not self.sql(sql, u'dbfunc.version (4h)'):
                return False

            sql = u"""SELECT AddGeometryColumn('einzugsgebiete','geom',{},'MULTIPOLYGON',2)""".format(self.epsg)
            if not self.sql(sql, u'dbfunc.version (4i)'):
                return False

            sql = u"""SELECT CreateSpatialIndex('einzugsgebiete','geom')"""
            if not self.sql(sql, u'dbfunc.version (4j)'):
                return False

            sql = u"""UPDATE info SET value = '2.1.6' WHERE subject = 'version' and value = '2.1.2';"""
            if not self.sql(sql, u'dbfunc.version (4k)'):
                return False

            versiondbQK = u'2.1.6'


        if versiondbQK < actversion:

            sql = u"""UPDATE info SET value = '{}' WHERE subject = 'version' and value = '{}';""".format(actversion, versiondbQK)
            if not self.sql(sql, u'dbfunc.version (4e)'):
                return False

        self.commit()
        return True

