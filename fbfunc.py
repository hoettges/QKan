# -*- coding: utf-8 -*-

'''
***************************************************************************
    fbfunc.py
    
    Datenbankmanagement fuer Firebird-Datenbanken

    Definition einer Klasse mit Methoden fuer den Zugriff auf 
    eine Firebird-Datenbank.

    ---------------------
    Date                 : October 2016
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
__date__ = 'October 2016'
__copyright__ = '(C) 2016, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import os
import sqlite3
import pyspatialite.dbapi2 as splite
import firebirdsql
from qgis.utils import iface
from qgis.gui import QgsMessageBar

# Hauptprogramm ----------------------------------------------------------------

class FBConnection:
    """Firebird Datenbankobjekt"""

    def __init__(self, dbname=None):
        """Constructor.

        :param dbname: Pfad zur Firebird-Datenbankdatei.
        :type tabObject: String
        """

            # Verbindung zur Datenbank herstellen
        if os.path.exists(dbname):
            try:
                self.confb = firebirdsql.connect(database = dbname, user = 'SYSDBA', password = 'masterke')
                self.curfb = self.confb.cursor()
            except:
                iface.messageBar().pushMessage("Fehler", 'Fehler beim Anbinden der ITWH-Datenbank {:s}!\nAbbruch!'.format(dbname), level=QgsMessageBar.CRITICAL)
                self.confb = None
        else:
            iface.messageBar().pushMessage("Fehler", 'ITWH-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(dbname), level=QgsMessageBar.CRITICAL)
            self.confb = None

    def __del__(self):
        """Destructor.
        
        Beendet die Datenbankverbindung.
        """
        self.confb.close()

    def __exit__(self):
        """Destructor.
        
        Beendet die Datenbankverbindung.
        """
        self.confb.close()

    def attrlist(self, tablenam):
        """Gibt Spaltenliste zurück."""

        sql = 'PRAGMA table_info("{0:s}")'.format(tablenam)
        self.curfb.execute(sql)
        daten = self.curfb.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == u'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def sql(self, sql):
        """Fuehrt eine SQL-Abfrage aus."""

        self.curfb.execute(sql)

    def fetchall(self):
        """Gibt alle Daten aus der vorher ausgeführten SQL-Abfrage zurueck"""
    
        daten = self.curfb.fetchall()
        return daten

    def fetchone(self):
        """Gibt einen Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""
    
        daten = self.curfb.fetchone()
        return daten

    def fetchnext(self):
        """Gibt den naechsten Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""
    
        daten = self.curfb.fetchnext()
        return daten

    def commit(self):
        """Schliesst eine SQL-Abfrage ab"""

        self.confb.commit()
