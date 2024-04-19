__author__ = "Jörg Höttges"

import os.path

from qgis.utils import spatialite_connect

from qkan.utils import get_logger


class FloodDB:
    """Zugriff auf eine SQLite Datenbank"""

    def __init__(self, dbname):
        """Initialiseren der Datenbankverbindung.
           Wenn die Datenbank nicht existiert, wird sie neu angelegt"""

        if os.path.exists(dbname):
            self.db = spatialite_connect(
                database=dbname, check_same_thread=False
            )
            self.conn = self.db.cursor()
        else:
            self.db = spatialite_connect(
                database=dbname, check_same_thread=False
            )
            self.conn = self.db.cursor()
            self.conn.execute("SELECT InitSpatialMetaData()")

        # Init logging
        self.logger = get_logger("QKan.floodTools.application_dialog")

    def __del__(self):
        self.logger.debug('FloodDB.__del__')
        self.db.commit()                                # Transaktionen abschliessen
        self.db.close()                                 # Datenbankzugriff lösen

    def __enter__(self):
        """Allows use via context manager (e.g. with)"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Allows use via context manager (e.g. with)"""
        self.logger.debug('FloodDB.__exit__')

    def sql(self, sqltext, kommentar=''):
        # SQL-Anweisung in Datenbank ausführen
        try:
            self.conn.execute(sqltext)
            self.logger.debug(f'FloodDB.sql: {sqltext=}')
            return True
        except self.db.Error as errortext:
            self.logger.error(f'Fehler in Datenbankaufruf {kommentar}:\n{errortext}\n{sqltext=}')
            return False

    def sqlmany(self, sqllis, kommentar=''):
        # SQL-Anweisung in Datenbank ausführen
        for sqltext in sqllis:
            try:
                self.conn.execute(sqltext)
                self.logger.debug(f'FloodDB.sqlmany {kommentar}:\n{sqltext=}')
            except self.db.Error as errortext:
                self.logger.error(f'Fehler in Datenbankaufruf {kommentar}:\n{errortext}\n{sqltext=}')
                return False
        return True

    def fetchone(self):
        """Einen Datensatz abfragen"""
        dataset = self.conn.fetchone()
        return dataset

    def fetchall(self):
        """Alle Datensätze abfragen"""
        dataset = self.conn.fetchall()
        return dataset

    def select(self, sqltext, kommentar=''):
        """Führt eine SQL-Abfrage aus und gibt alle Datensätze zurück"""
        if self.sql(sqltext, kommentar):
            dataset = self.fetchall()
            return dataset
        else:
            return None

    def commit(self):
        self.db.commit()
