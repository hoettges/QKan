# -*- coding: utf-8 -*-

"""

  Datenbankmanagement fuer Firebird-Datenbanken
  =============================================

  Definition einer Klasse mit Methoden fuer den Zugriff auf 
  eine Firebird-Datenbank.

  | Dateiname            : fbfunc.py
  | Date                 : October 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de

  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.

"""

__author__ = "Joerg Hoettges"
__date__ = "October 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"

import logging
import os
from typing import Any, List, Union

import firebirdsql

from .qkan_utils import fehlermeldung

logger = logging.getLogger(u"QKan")

# Hauptprogramm ----------------------------------------------------------------


class FBConnection:
    """Firebird Datenbankobjekt"""

    def __init__(self, dbname: str):
        """Constructor.
    
        :param dbname: Pfad zur Firebird-Datenbankdatei.
        """
        # Verbindung zur Datenbank herstellen
        if os.path.exists(dbname):
            try:
                self.confb = firebirdsql.connect(
                    database=dbname,
                    user="SYSDBA",
                    password="masterke",
                    charset="latin1",
                )
                self.curfb = self.confb.cursor()
            except:
                logger.debug(
                    "Fehler beim Anbinden der ITWH-Datenbank {:s}!\nAbbruch!".format(
                        dbname
                    )
                )
                self.confb = None
        else:
            logger.debug(
                "Fehler: ITWH-Datenbank {:s} wurde nicht gefunden!\nAbbruch!".format(
                    dbname
                )
            )
            self.confb = None

    def __del__(self) -> None:
        """Destructor.
            
        Beendet die Datenbankverbindung.
        """
        self.confb.close()

    def __exit__(self) -> None:
        """Destructor.
            
        Beendet die Datenbankverbindung.
        """
        self.confb.close()

    def attrlist(self, tablenam: str) -> Union[List[str]]:
        """Gibt Spaltenliste zurueck."""

        sql = u'PRAGMA table_info("{0:s}")'.format(tablenam)
        self.curfb.execute(sql)
        daten = self.curfb.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == u'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def sql(self, sql: str, errormessage: str = "allgemein") -> bool:
        """Fuehrt eine SQL-Abfrage aus."""

        try:
            self.curfb.execute(sql)
            return True
        except AttributeError:
            fehlermeldung(
                u"QKan.FBConnection: Datenbankzugriff gesperrt, moeglicherweise durch eine andere Anwendung?"
            )
            return False
        except BaseException as err:
            fehlermeldung(
                u"SQL-Fehler in {e}".format(e=errormessage),
                u"{e}\n{s}".format(e=repr(err), s=sql),
            )
            return False

    def fetchall(self) -> List[Any]:
        """Gibt alle Daten aus der vorher ausgefuehrten SQL-Abfrage zurueck"""

        daten: List[Any] = self.curfb.fetchall()
        return daten

    def fetchone(self) -> Any:
        """Gibt einen Datensatz aus der vorher ausgefuehrten SQL-Abfrage zurueck"""

        daten = self.curfb.fetchone()
        return daten

    def fetchnext(self) -> Any:
        """Gibt den naechsten Datensatz aus der vorher ausgefuehrten SQL-Abfrage zurueck"""

        daten = self.curfb.fetchnext()
        return daten

    def commit(self) -> None:
        """Schliesst eine SQL-Abfrage ab"""

        self.confb.commit()
