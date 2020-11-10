# -*- coding: utf-8 -*-

"""
Datenbankmanagement

Definition einer Klasse mit Methoden fuer den Zugriff auf
eine SpatiaLite-Datenbank.
"""
import datetime
import logging
import os
import shutil
from sqlite3 import Connection
from typing import Any, List, Optional, Union, cast

from qgis.core import Qgis, QgsVectorLayer
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import spatialite_connect
from qkan import QKan

from .qkan_database import createdbtables, db_version, versionolder
from .qkan_utils import fehlermeldung, meldung

__author__ = "Joerg Hoettges"
__date__ = "September 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"


logger = logging.getLogger("QKan.database.dbfunc")

progress_bar = None


# Pruefung, ob in Tabellen oder Spalten unerlaubte Zeichen enthalten sind
def checkchars(text: str) -> bool:
    """
    Pruefung auf nicht erlaubte Zeichen in Tabellen- und Spaltennamen.

    :param text: zu pruefende Bezeichnung einer Tabelle oder Tabellenspalte

    :returns: Testergebnis: True = alles o.k.
    """

    return not (max([ord(t) > 127 for t in text]) or ("." in text) or ("-" in text))


class DBConnection:
    """SpatiaLite Datenbankobjekt"""

    def __init__(
        self,
        dbname: Optional[str] = None,
        tab_object: Optional[QgsVectorLayer] = None,
        epsg: int = 25832,
        qkan_db_update: bool = False,
    ):
        """Constructor. Überprüfung, ob die QKan-Datenbank die aktuelle Version hat, mit dem Attribut isCurrentVersion. 

        :param dbname:      Pfad zur SpatiaLite-Datenbankdatei. Falls nicht vorhanden, 
                            wird es angelegt.
        :type dbname:        String

        :param tab_object:   Vectorlayerobjekt, aus dem die Parameter zum 
                            Zugriff auf die SpatiaLite-Tabelle ermittelt werden.
        :type tab_object:    QgsVectorLayer

        :param epsg:        EPSG-Code aller Tabellen in einer neuen Datenbank

        :qkanDBUpdate:      Bei veralteter Datenbankversion automatisch Update durchführen. Achtung:
                            Nach Durchführung muss k_layersadapt mindestens mit den Optionen 
        :type qkan_db_update: Boolean

        
        public attributes:

        reload:             Update der Datenbank macht Neuladen des Projektes notwendig, weil Tabellenstrukturen
                            geändert wurden. Wird von self.updateversion() gesetzt

        connected:          Datenbankverbindung erfolgreich

        isCurrentVersion:   Datenbank ist auf dem aktuellen Stand
        """

        # Übernahme einiger Attribute in die Klasse
        self.dbname = dbname
        self.epsg: Optional[int] = epsg

        # Die nachfolgenden Klassenobjekte dienen dazu, gleichartige (sqlidtext) SQL-Debug-Meldungen
        # nur einmal pro Sekunde zu erzeugen.
        self.sqltime = datetime.datetime(2017, 1, 1, 1, 0, 0)
        self.sqltime = self.sqltime.now()
        self.sqltext = ""
        self.sqlcount = 0

        self.actversion = db_version()

        # QKan-Datenbank ist auf dem aktuellen Stand.
        self.isCurrentVersion = True

        # Verbindung hergestellt, d.h. weder fehlgeschlagen noch wegen reload geschlossen
        self.connected = True

        # reload = True: Datenbank wurde aktualisiert und dabei sind gravierende Änderungen aufgetreten,
        # die ein Neuladen des Projektes erforderlich machen
        self.reload = False

        self.versiondbQK = "unknown"

        if dbname is not None:
            # Verbindung zur Datenbank herstellen oder die Datenbank neu erstellen
            if os.path.exists(dbname):
                self.consl = spatialite_connect(
                    database=dbname, check_same_thread=False
                )
                self.cursl = self.consl.cursor()

                self.epsg = self.getepsg()
                if self.epsg is None:
                    logger.error(
                        "dbfunc.DBConnection.__init__: EPSG konnte nicht ermittelt werden. \n"
                        + " QKan-DB: {}\n".format(dbname)
                    )

                logger.debug(
                    "dbfunc.DBConnection.__init__: Datenbank existiert und Verbindung hergestellt:\n"
                    + "{}".format(dbname)
                )
                # Versionsprüfung

                if not self.check_version():
                    logger.debug("dbfunc: Datenbank ist nicht aktuell")
                    if qkan_db_update:
                        logger.debug(
                            "dbfunc: Update aktiviert. Deshalb wird Datenbank aktualisiert"
                        )
                        self.updateversion()
                        # if self.reload:
                        #     logger.debug("dbfunc: Datenbank muss neu geladen werden")
                        #     self.connected = False
                        #     self.consl.close()
                    else:
                        meldung(
                            f"Projekt muss aktualisiert werden. Die QKan-Version der Datenbank {self.versiondbQK} stimmt nicht ",
                            f"mit der aktuellen QKan-Version {self.actversion} überein und muss aktualisiert werden!",
                        )
                        self.consl.close()
                        self.isCurrentVersion = False
                        self.connected = False  # Verbindungsstatus zur Kontrolle

            else:
                QKan.instance.iface.messageBar().pushMessage(
                    "Information",
                    "SpatiaLite-Datenbank wird erstellt. Bitte waren...",
                    level=Qgis.Info,
                )

                datenbank_qkan_template = os.path.join(QKan.template_dir, "qkan.sqlite")
                try:
                    shutil.copyfile(datenbank_qkan_template, dbname)

                    self.consl = spatialite_connect(database=dbname)
                    self.cursl = self.consl.cursor()

                    # sql = 'SELECT InitSpatialMetadata()'
                    # self.cursl.execute(sql)

                    QKan.instance.iface.messageBar().pushMessage(
                        "Information",
                        "SpatiaLite-Datenbank ist erstellt!",
                        level=Qgis.Info,
                    )
                    if not createdbtables(
                        self.consl, self.cursl, self.actversion, self.epsg
                    ):
                        fehlermeldung(
                            "Fehler",
                            "SpatiaLite-Datenbank: Tabellen konnten nicht angelegt werden",
                        )
                except BaseException as err:
                    logger.debug(f"Datenbank ist nicht vorhanden: {dbname}")
                    fehlermeldung(
                        "Fehler in dbfunc.DBConnection:\n{}\n".format(err),
                        "Kopieren von: {}\nnach: {}\n nicht möglich".format(
                            QKan.template_dir, dbname
                        ),
                    )
                    self.connected = False  # Verbindungsstatus zur Kontrolle
                    self.consl = None
        elif tab_object is not None:
            tabconnect = tab_object.publicSource()
            t_db, t_tab, t_geo, t_sql = tuple(tabconnect.split())
            dbname = t_db.split("=")[1].strip("'")
            self.tabname = t_tab.split("=")[1].strip('"')

            # Pruefung auf korrekte Zeichen in Namen
            if not checkchars(self.tabname):
                fehlermeldung(
                    "Fehler",
                    "Unzulaessige Zeichen in Tabellenname: {}".format(self.tabname),
                )
                self.connected = False  # Verbindungsstatus zur Kontrolle
                self.consl = None
            else:
                try:
                    self.consl = spatialite_connect(database=dbname)
                    self.cursl = self.consl.cursor()

                    self.epsg = self.getepsg()
                except:
                    fehlermeldung(
                        "Fehler",
                        "Fehler beim Öffnen der SpatialLite-Datenbank {}!\nAbbruch!".format(
                            dbname
                        ),
                    )
                    self.connected = False  # Verbindungsstatus zur Kontrolle
                    self.consl = None
        else:
            fehlermeldung(
                "Fehler",
                "Fehler beim Anbinden der SpatialLite-Datenbank {}!\nAbbruch!".format(
                    dbname
                ),
            )
            self.connected = False  # Verbindungsstatus zur Kontrolle
            self.consl = None

    def __del__(self) -> None:
        """Destructor.
        
        Beendet die Datenbankverbindung.
        """
        try:
            cast(Connection, self.consl).close()
            logger.debug(f"Verbindung zur Datenbank {self.dbname} wieder geloest.")
        except BaseException:
            fehlermeldung(
                "Fehler in dbfunc.DBConnection:",
                f"Verbindung zur Datenbank {self.dbname} konnte nicht geloest werden.\n",
            )

    def attrlist(self, tablenam: str) -> Union[List[str]]:
        """Gibt Spaltenliste zurück."""

        sql = 'PRAGMA table_info("{0:s}")'.format(tablenam)
        if not self.sql(sql, "dbfunc.DBConnection.attrlist fuer {}".format(tablenam)):
            return []

        daten = self.cursl.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == 'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def getepsg(self) -> Optional[int]:
        """ Feststellen des EPSG-Codes der Datenbank"""

        sql = """SELECT srid
            FROM geom_cols_ref_sys
            WHERE Lower(f_table_name) = Lower('haltungen')
            AND Lower(f_geometry_column) = Lower('geom')"""
        if not self.sql(sql, "dbfunc.DBConnection.getepsg (1)"):
            return None

        data = self.fetchone()
        if data is None:
            fehlermeldung(
                "Fehler in dbfunc.DBConnection.getepsg (2)",
                "Konnte EPSG nicht ermitteln",
            )
        epsg: int = data[0]
        return epsg

    def sql(
        self,
        sql: str,
        sqlinfo: str = "allgemein",
        repeatmessage: bool = False,
        transaction: bool = False,
    ) -> bool:
        # TODO: Safe SQL queries with parameter binding
        """Fuehrt eine SQL-Abfrage aus."""

        try:
            self.cursl.execute(sql)

            # Identische Protokollmeldungen werden für 2 Sekunden unterdrückt...
            if self.sqltext == sqlinfo and not repeatmessage:
                if (self.sqltime.now() - self.sqltime).seconds < 2:
                    self.sqlcount += 1
                    return True
            self.sqltext = sqlinfo
            self.sqltime = self.sqltime.now()
            if self.sqlcount == 0:
                logger.debug("dbfunc.DBConnection.sql: {}\n{}\n".format(sqlinfo, sql))
            else:
                logger.debug(
                    "dbfunc.DBConnection.sql (Nr. {}): {}\n{}\n".format(
                        self.sqlcount, sqlinfo, sql
                    )
                )
            self.sqlcount = 0
            return True
        except BaseException as err:
            fehlermeldung(
                "dbfunc.DBConnection.sql: SQL-Fehler in {e}".format(e=sqlinfo),
                "{e}\n{s}".format(e=repr(err), s=sql),
            )
            # if transaction:
            # self.cursl.commit("ROLLBACK;")
            return False

    def fetchall(self) -> List[Any]:
        """Gibt alle Daten aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten: List[Any] = self.cursl.fetchall()
        return daten

    def fetchone(self) -> Any:
        """Gibt einen Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten = self.cursl.fetchone()
        return daten

    def fetchnext(self) -> Any:
        """Gibt den naechsten Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten = self.cursl.fetchnext()
        return daten

    def commit(self) -> None:
        """Schliesst eine SQL-Abfrage ab"""

        self.consl.commit()

    # Versionskontrolle der QKan-Datenbank

    def rowcount(self) -> int:
        """Gibt die Anzahl zuletzt geänderte Datensätze zurück"""

        return cast(int, self.cursl.rowcount)

    def check_version(self) -> bool:
        """Prüft die Version der Datenbank. 

            :returns: Anpassung erfolgreich: True = alles o.k.
            :rtype: logical
            
            Voraussetzungen: 
             - Die aktuelle Datenbank ist bereits geöffnet. 

            Die aktuelle Versionsnummer steht in der Datenbank: info.version
            Diese wird mit dem Attribut self.actversion verglichen.         """

        logger.debug("0 - actversion = {}".format(self.actversion))

        # ---------------------------------------------------------------------------------------------
        # Aktuelle Version abfragen

        sql = """SELECT value
                FROM info
                WHERE subject = 'version'"""

        if not self.sql(sql, "dbfunc.DBConnection.version (1)"):
            return False

        data = self.cursl.fetchone()
        if data is not None:
            self.versiondbQK = data[0]
            logger.debug(
                "dbfunc.DBConnection.version: Aktuelle Version der qkan-Datenbank ist {}".format(
                    self.versiondbQK
                )
            )
        else:
            logger.debug(
                "dbfunc.DBConnection.version: Keine Versionsnummer vorhanden. data = {}".format(
                    repr(data)
                )
            )
            sql = """INSERT INTO info (subject, value) Values ('version', '1.9.9')"""
            if not self.sql(sql, "dbfunc.DBConnection.version (2)"):
                return False

            self.versiondbQK = "1.9.9"

        logger.debug("0 - versiondbQK = {}".format(self.versiondbQK))

        return cast(bool, self.actversion == self.versiondbQK)

    # Ändern der Attribute einer Tabelle

    def alter_table(
        self, tabnam: str, attributes_new: List[str], attributes_del: List[str] = None,
    ) -> bool:
        """Changes attribute columns in QKan tables except geom columns.

        :tabnam:                Name der Tabelle
        :attributes_new:         zukünftige Attribute, Syntax wie in Create-Befehl, ohne Primärschlüssel
        :attributes_del:         zu entfernende Attribute

        Ändert die Tabelle so, dass sie die Attribute aus attributesNew in der gegebenen
        Reihenfolge sowie die in der bestehenden Tabelle vom Benutzer hinzugefügten Attribute
        enthält. Nur falls attributesDel Attribute enthält, werden diese nicht übernommen.

        example:
        alter_table('flaechen',
            [   'flnam TEXT',
                'haltnam TEXT',
                'ueberfluessig1 REAL',
                'ueberfluessig2 TEXT',
                "simstatus TEXT DEFAULT 'vorhanden'",
                'teilgebiet TEXT',
                "createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now'))"],
            ['ueberfluessig1', 'ueberfluessig2'])
        """

        # Attributlisten
        # Schema:
        # - attrSet.. ist ein Set, das nur die Attributnamen enthält
        # - attrDict.. ist ein Dict, das als Key den Attributnamen und als Wert die SQL-Definitionszeile enthält
        # - ..Old enthält die Attribute der bestehenden Tabelle inkl. der Benutzerattribute,
        #     ohne Primärschlüssel sowie Geoobjekte
        # - ..New enthält die Attribute nach dem Update ohne Benutzerattribute, Primärschlüssel sowie Geoattribute
        # - ..Diff enthält die zu übertragenden Attribute inkl. Geoattribute

        # - attrPk:string enthält den Namen des Primärschlüssels

        geo_type = [
            None,
            "POINT",
            "LINESTRING",
            "POLYGON",
            "MULTIPOINT",
            "MULTILINESTRING",
            "MULTIPOLYGON",
        ]

        # 1. bestehende Tabelle
        # Benutzerdefinierte Felder müssen übernommen werden
        sql = f"PRAGMA table_info('{tabnam}')"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (1)", transaction=False):
            return False
        data = self.fetchall()
        attr_pk = [el[1] for el in data if el[5] == 1][0]
        attr_dict_old = dict(
            [
                (
                    el[1],
                    el[1]
                    + " "
                    + el[2]
                    + ("" if el[4] is None else f" DEFAULT {el[4]}"),
                )
                for el in data
                if el[5] == 0
            ]
        )
        attr_set_old = set(attr_dict_old.keys())

        attr_set_del = set(attributes_del) if attributes_del is not None else set([])

        # Geometrieattribute
        sql = f"""SELECT f_geometry_column, geometry_type, srid, coord_dimension, spatial_index_enabled 
                    FROM geometry_columns WHERE f_table_name = '{tabnam}'"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (2)", transaction=False):
            return False
        data = self.fetchall()
        attr_dict_geo = dict(
            [
                (el[0], f"'{el[0]}', {el[2]}, '{geo_type[el[1]]}', {el[3]}")
                for el in data
            ]
        )
        attr_set_geo = set(attr_dict_geo.keys())

        attr_set_new = {el.strip().split(" ", maxsplit=1)[0] for el in attributes_new}

        # Hinzufügen der Benutzerattribute
        attr_set_new |= attr_set_old
        # Entfernen von Primärschlüssel, Geoattributen und zu Löschenden Attributen
        attr_set_new -= {attr_pk}
        attr_set_new -= attr_set_geo
        attr_set_new -= attr_set_del

        # Attribute zur Datenübertragung zwischen alter und neuer Tabelle.
        attr_set_both = set(attr_set_old) & set(attr_set_new)
        attr_set_both |= {attr_pk}
        attr_set_both |= attr_set_geo

        # Zusammenstellen aller Attribute. Begonnen wird mit dem Primärschlüssel
        attr_dict_new = {attr_pk: f"{attr_pk} INTEGER PRIMARY KEY"}
        # Zusammenstellen aller Attribute in der neuen Tabelle inkl. Benutzerattributen
        for el in attributes_new:
            attr = el.strip().split(" ")[0].strip()
            typ = el.strip()
            attr_dict_new[attr] = typ
        # Hinzufügen aller Attribute der bisherigen Tabelle (dies umfasst auch die Benutzerattribute)
        for attr in attr_set_old:
            if attr not in attr_dict_new:
                attr_dict_new[attr] = attr_dict_old[attr]
        # Entfernen der zu entfernenden Attribute:
        for attr in attr_set_del:
            if attr in attr_dict_new:
                del attr_dict_new[attr]
        # Zur Sicherheit: Entfernen aller Geoattribute
        for attr in attr_set_geo:
            if attr in attr_dict_new:
                del attr_dict_new[attr]

        # Attribute der neuen Tabelle als String für SQL-Anweisung
        attr_text_new = ",\n".join(attr_dict_new.values())
        logger.debug(f"dbfunc.DBConnection.alter_table - attr_text_new:{attr_text_new}")

        # 0. Foreign key constrain deaktivieren
        sql = "PRAGMA foreign_keys=OFF;"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (3)", transaction=False):
            return False

        # 1. Transaktion starten
        sql = "BEGIN TRANSACTION;"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (4)", transaction=False):
            return False

        # 2. Indizes und Trigger speichern
        sql = f"""SELECT type, sql 
                FROM sqlite_master 
                WHERE tbl_name='{tabnam}' AND (type = 'trigger' OR type = 'index')"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (5)", transaction=False):
            return False
        # triggers = [el[1] for el in self.fetchall()]

        # 2.1. Temporäre Hilfstabelle erstellen
        sql = f"CREATE TABLE IF NOT EXISTS {tabnam}_t ({attr_text_new});"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (6)", transaction=False):
            return False

        # 2.2. Geo-Attribute in Tabelle ergänzen
        for attr in attr_set_geo:
            sql = f"""SELECT AddGeometryColumn('{tabnam}_t', {attr_dict_geo[attr]})"""
            if not self.sql(
                sql, "dbfunc.DBConnection.alter_table (7)", transaction=False
            ):
                return False

        # 3. Hilfstabelle entleeren
        sql = f"DELETE FROM {tabnam}_t"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (8)", transaction=False):
            return False

        # 4. Daten aus Originaltabelle übertragen, dabei nur gemeinsame Attribute berücksichtigen
        sql = f"""INSERT INTO {tabnam}_t ({', '.join(attr_set_both)})
                SELECT {', '.join(attr_set_both)}
                FROM {tabnam};"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (9)", transaction=False):
            return False

        # 5.1. Löschen der Geoobjektattribute
        for attr in attr_set_geo:
            sql = f"SELECT DiscardGeometryColumn('{tabnam}','{attr}')"
            if not self.sql(
                sql, "dbfunc.DBConnection.alter_table (10)", transaction=False
            ):
                return False

        # 5.2. Löschen der Tabelle
        sql = f"DROP TABLE {tabnam};"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (11)", transaction=False):
            return False

        # 6.1 Geänderte Tabelle erstellen
        sql = f"""CREATE TABLE {tabnam} ({attr_text_new});"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (12)", transaction=False):
            return False

        # 6.2. Geo-Attribute in Tabelle ergänzen und Indizes erstellen
        for attr in attr_set_geo:
            sql = f"""SELECT AddGeometryColumn('{tabnam}', {attr_dict_geo[attr]})"""
            if not self.sql(
                sql, "dbfunc.DBConnection.alter_table (13)", transaction=False
            ):
                return False
            sql = f"""SELECT CreateSpatialIndex('{tabnam}', '{attr}')"""
            if not self.sql(
                sql, "dbfunc.DBConnection.alter_table (14)", transaction=False
            ):
                return False

        # 7. Daten aus Hilfstabelle übertragen, dabei nur gemeinsame Attribute berücksichtigen
        sql = f"""INSERT INTO {tabnam} ({', '.join(attr_set_both)})
                SELECT {', '.join(attr_set_both)}
                FROM {tabnam}_t;"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (15)", transaction=False):
            return False

        # 8.1. Löschen der Geoobjektattribute der Hilfstabelle
        for attr in attr_set_geo:
            sql = f"SELECT DiscardGeometryColumn('{tabnam}_t','{attr}')"
            if not self.sql(
                sql, "dbfunc.DBConnection.alter_table (16)", transaction=False
            ):
                return False

        # 9. Löschen der Hilfstabelle
        sql = """DROP TABLE {t}_t;""".format(t=tabnam)
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (17)", transaction=False):
            return False

        # 9. Indizes und Trigger wiederherstellen
        # for sql in triggers:
        #     if not self.sql(sql, 'dbfunc.DBConnection.alter_table (18)', transaction=False):
        #         return False

        # 10. Verify key constraints
        sql = "PRAGMA foreign_key_check"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (19)", transaction=False):
            return False

        # 11. Transaktion abschließen
        self.commit()

        # 12. Foreign key constrain wieder aktivieren
        sql = "PRAGMA foreign_keys=ON;"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (20)", transaction=False):
            return False

        return True

    # Aktualisierung der QKan-Datenbank auf aktuellen Stand

    def updateversion(self) -> bool:
        """Aktualisiert die QKan-Datenbank auf den aktuellen Stand. 

           Es werden die nötigen Anpassungen vorgenommen und die Versionsnummer jeweils aktualisiert.
           Falls Tabellenspalten umbenannt oder gelöscht wurden, wird eine Warnmeldung erzeugt
           mit der Empfehlung, das aktuelle Projekt neu zu laden. 

        """

        # Nur wenn Stand der Datenbank nicht aktuell
        if not self.check_version():
            self.versionlis = [
                int(el.replace("a", "").replace("b", "").replace("c", ""))
                for el in self.versiondbQK.split(".")
            ]
            logger.debug(
                "dbfunc.DBConnection.updateversion: versiondbQK = {}".format(
                    self.versiondbQK
                )
            )

            # Status, wenn die Änderungen so gravierend waren, dass das Projekt neu geladen werden muss.
            self.reload = False

            global progress_bar
            progress_bar = QProgressBar(QKan.instance.iface.messageBar())
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)

            # ---------------------------------------------------------------------------------------------
            # Aktualisierung von Version 1.9.9 und früher

            if versionolder(self.versionlis, [2, 0, 2]):

                # Tabelle einleit
                sqllis = [
                    """CREATE TABLE IF NOT EXISTS einleit (
                    pk INTEGER PRIMARY KEY,
                    elnam TEXT,
                    haltnam TEXT,
                    teilgebiet TEXT, 
                    zufluss REAL,
                    kommentar TEXT,
                    createdat TEXT DEFAULT CURRENT_DATE)""",
                    """SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('einleit','geom')""",
                ]
                for sql in sqllis:
                    if not self.sql(sql, "dbfunc.DBConnection.version (3c)"):
                        return False

                sqllis = [
                    """CREATE TABLE IF NOT EXISTS linksw (
                        pk INTEGER PRIMARY KEY,
                        elnam TEXT,
                        haltnam TEXT,
                        teilgebiet TEXT)""",
                    """SELECT AddGeometryColumn('linksw','geom',{},'POLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('linksw','geom')""",
                ]
                for sql in sqllis:
                    if not self.sql(sql, "dbfunc.DBConnection.version (3d)"):
                        return False

                self.versionlis = [2, 0, 2]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 1, 2]):

                attrlis = self.attrlist("linksw")
                if not attrlis:
                    fehlermeldung(
                        "dbfunc.DBConnection.version (2.0.2):",
                        "attrlis für linksw ist leer",
                    )
                    return False
                elif "elnam" not in attrlis:
                    logger.debug("linksw.elnam ist nicht in: {}".format(str(attrlis)))
                    sql = """ALTER TABLE linksw ADD COLUMN elnam TEXT"""
                    if not self.sql(sql, "dbfunc.DBConnection.version (2.0.2-1)"):
                        return False
                    self.commit()

                attrlis = self.attrlist("linkfl")
                if not attrlis:
                    fehlermeldung(
                        "dbfunc.DBConnection.version (2.0.2):",
                        "attrlis für linkfl ist leer",
                    )
                    return False
                elif "tezgnam" not in attrlis:
                    logger.debug("linkfl.tezgnam ist nicht in: {}".format(str(attrlis)))
                    sql = """ALTER TABLE linkfl ADD COLUMN tezgnam TEXT"""
                    if not self.sql(sql, "dbfunc.DBConnection.version (2.0.2-3)"):
                        return False
                    self.commit()

                self.versionlis = [2, 1, 2]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 2, 0]):
                attrlis = self.attrlist("einleit")
                if not attrlis:
                    return False
                elif "ew" not in attrlis:
                    logger.debug("einleit.ew ist nicht in: {}".format(str(attrlis)))
                    sql = """ALTER TABLE einleit ADD COLUMN ew REAL"""
                    if not self.sql(sql, "dbfunc.DBConnection.version (2.1.2-1)"):
                        return False
                    sql = """ALTER TABLE einleit ADD COLUMN einzugsgebiet TEXT"""
                    if not self.sql(sql, "dbfunc.DBConnection.version (2.1.2-2)"):
                        return False
                    self.commit()

                sql = """CREATE TABLE IF NOT EXISTS einzugsgebiete (
                    pk INTEGER PRIMARY KEY,
                    tgnam TEXT,
                    ewdichte REAL,
                    wverbrauch REAL,
                    stdmittel REAL,
                    fremdwas REAL,
                    kommentar TEXT,
                    createdat TEXT DEFAULT CURRENT_DATE)"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.1.2-3)"):
                    return False

                sql = """SELECT AddGeometryColumn('einzugsgebiete','geom',{},'MULTIPOLYGON',2)""".format(
                    self.epsg
                )
                if not self.sql(sql, "dbfunc.DBConnection.version (2.1.2-4)"):
                    return False

                sql = """SELECT CreateSpatialIndex('einzugsgebiete','geom')"""
                if not self.sql(sql, "dbfunc.DBConnection.version (2.1.2-5)"):
                    return False

                self.versionlis = [2, 2, 0]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 2, 1]):

                attrlis = self.attrlist("flaechen")
                if not attrlis:
                    return False
                elif "abflusstyp" not in attrlis:
                    logger.debug(
                        "flaechen.abflusstyp ist nicht in: {}".format(str(attrlis))
                    )
                    sql = """ALTER TABLE flaechen ADD COLUMN abflusstyp TEXT"""
                    if not self.sql(sql, "dbfunc.DBConnection.version (2.2.0-1)"):
                        return False
                    self.commit()

                self.versionlis = [2, 2, 1]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 2, 2]):

                attrlis = self.attrlist("flaechen")
                if not attrlis:
                    return False
                elif "abflusstyp" not in attrlis:
                    logger.debug(
                        "flaechen.abflusstyp ist nicht in: {}".format(str(attrlis))
                    )
                    sql = """ALTER TABLE flaechen ADD COLUMN abflusstyp TEXT"""
                    if not self.sql(sql, "dbfunc.DBConnection.version (2.2.1-1)"):
                        return False
                    self.commit()

                self.versionlis = [2, 2, 2]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 2, 3]):

                # Tabelle flaechen -------------------------------------------------------------

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='flaechen'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (1)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS flaechen_t (
                            pk INTEGER PRIMARY KEY,
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
                    """SELECT AddGeometryColumn('flaechen_t','geom',{},'MULTIPOLYGON',2);""".format(
                        self.epsg
                    ),
                    """DELETE FROM flaechen_t""",
                    """INSERT INTO flaechen_t 
                            (
                            "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit",
                            "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", 
                            "kommentar", "createdat", "geom"
                            )
                            SELECT "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", 
                            "fliesszeit", "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", 
                            "aufteilen", "kommentar", "createdat", "geom"
                            FROM "flaechen";""",
                    """SELECT DiscardGeometryColumn('flaechen','geom')""",
                    """DROP TABLE flaechen;""",
                    """CREATE TABLE flaechen (
                            pk INTEGER PRIMARY KEY,
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
                    """SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2);""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('flaechen','geom')""",
                    """INSERT INTO flaechen 
                            (
                            "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit",
                            "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", 
                            "kommentar", "createdat", "geom")
                            SELECT "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", 
                            "fliesszeit", "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", 
                            "aufteilen", "kommentar", "createdat", "geom"
                            FROM "flaechen_t";""",
                    """SELECT DiscardGeometryColumn('flaechen_t','geom')""",
                    """DROP TABLE flaechen_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.2.2-1)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'flaechen' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-2)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen
                self.commit()

                # 5. Schritt: Spalte abflusstyp aus Spalte he_typ übertragen
                sql = """UPDATE flaechen SET abflusstyp = 
                        CASE he_typ 
                            WHEN 0 THEN 'Direktabfluss' 
                            WHEN 1 THEN 'Fließzeiten' 
                            WHEN 2 THEN 'Schwerpunktfließzeit'
                            ELSE NULL END
                        WHERE abflusstyp IS NULL"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.2.2-3)"):
                    return False

                progress_bar.setValue(15)

                # Tabelle linksw -------------------------------------------------------------

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linksw'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (3)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
                # 14.10.2018: Unklar, warum überhaupt. Es findet keine Änderung statt. Möglicherweise
                # muss hier eine händische Änderung "eingefangen werden".
                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS linksw_t (
                            pk INTEGER PRIMARY KEY,
                            elnam TEXT,
                            haltnam TEXT)""",
                    """SELECT AddGeometryColumn('linksw_t','geom',{},'POLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw_t','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw_t','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """DELETE FROM linksw_t""",
                    """INSERT INTO linksw_t 
                            (      "elnam", "haltnam", "geom", "gbuf", "glink")
                            SELECT "elnam", "haltnam", "geom", "gbuf", "glink"
                            FROM "linksw";""",
                    """SELECT DiscardGeometryColumn('linksw','geom')""",
                    """SELECT DiscardGeometryColumn('linksw','gbuf')""",
                    """SELECT DiscardGeometryColumn('linksw','glink')""",
                    """DROP TABLE linksw;""",
                    """CREATE TABLE linksw (
                            pk INTEGER PRIMARY KEY,
                            elnam TEXT,
                            haltnam TEXT,
                            teilgebiet TEXT)""",
                    """SELECT AddGeometryColumn('linksw','geom',{},'POLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('linksw','geom')""",
                    """INSERT INTO linksw 
                            (      "elnam", "haltnam", "geom", "gbuf", "glink")
                            SELECT "elnam", "haltnam", "geom", "gbuf", "glink"
                            FROM "linksw_t";""",
                    """SELECT DiscardGeometryColumn('linksw_t','geom')""",
                    """SELECT DiscardGeometryColumn('linksw_t','gbuf')""",
                    """SELECT DiscardGeometryColumn('linksw_t','glink')""",
                    """DROP TABLE linksw_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.2.2-4)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'linksw' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-5)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen
                self.commit()

                progress_bar.setValue(30)

                # Tabelle linkfl -------------------------------------------------------------

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linkfl'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (5)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Temporäre Tabelle anlegen, Daten rüber kopieren,
                #             Tabelle löschen und wieder neu anlegen und Daten zurück kopieren

                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS linkfl_t (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            tezgnam TEXT);""",
                    """SELECT AddGeometryColumn('linkfl_t','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl_t','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl_t','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """DELETE FROM linkfl_t""",
                    """INSERT INTO linkfl_t 
                            (      "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink")
                            SELECT "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink"
                            FROM "linkfl";""",
                    """SELECT DiscardGeometryColumn('linkfl','geom')""",
                    """SELECT DiscardGeometryColumn('linkfl','gbuf')""",
                    """SELECT DiscardGeometryColumn('linkfl','glink')""",
                    """DROP TABLE linkfl;""",
                    """CREATE TABLE linkfl (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            tezgnam TEXT,
                            teilgebiet TEXT);""",
                    """SELECT AddGeometryColumn('linkfl','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('linkfl','glink')""",
                    """INSERT INTO linkfl 
                            (      "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink")
                            SELECT "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink"
                            FROM "linkfl_t";""",
                    """SELECT DiscardGeometryColumn('linkfl_t','geom')""",
                    """SELECT DiscardGeometryColumn('linkfl_t','gbuf')""",
                    """SELECT DiscardGeometryColumn('linkfl_t','glink')""",
                    """DROP TABLE linkfl_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.2.2-6)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'linkfl' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-7)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen
                self.commit()

                progress_bar.setValue(45)

                # Tabelle einleit -------------------------------------------------------------

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='einleit'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (7)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS einleit_t (
                            pk INTEGER PRIMARY KEY,
                            elnam TEXT,
                            haltnam TEXT,
                            teilgebiet TEXT, 
                            zufluss REAL,
                            ew REAL,
                            einzugsgebiet TEXT,
                            kommentar TEXT,
                            createdat TEXT DEFAULT CURRENT_DATE);""",
                    """SELECT AddGeometryColumn('einleit_t','geom',{},'POINT',2)""".format(
                        self.epsg
                    ),
                    """DELETE FROM einleit_t""",
                    """
                    INSERT INTO einleit_t 
                    ("elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", "createdat", 
                    "geom")
                    SELECT "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", 
                            "createdat", "geom"
                    FROM "einleit";
                    """,
                    """SELECT DiscardGeometryColumn('einleit','geom')""",
                    """DROP TABLE einleit;""",
                    """CREATE TABLE einleit (
                            pk INTEGER PRIMARY KEY,
                            elnam TEXT,
                            haltnam TEXT,
                            teilgebiet TEXT, 
                            zufluss REAL,
                            ew REAL,
                            einzugsgebiet TEXT,
                            kommentar TEXT,
                            createdat TEXT DEFAULT CURRENT_DATE);""",
                    """SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('einleit','geom')""",
                    """
                    INSERT INTO einleit 
                        ("elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", 
                        "createdat", "geom")
                    SELECT "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", 
                            "createdat", "geom"
                    FROM "einleit_t";
                    """,
                    """SELECT DiscardGeometryColumn('einleit_t','geom')""",
                    """DROP TABLE einleit_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.2.2-8)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'einleit' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-9)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen

                self.commit()

                progress_bar.setValue(60)

                self.reload = True

                # Versionsnummer hochsetzen

                self.versionlis = [2, 2, 3]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 2, 16]):

                sql = """
                    CREATE TABLE IF NOT EXISTS dynahal (
                        pk INTEGER PRIMARY KEY,
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
                if not self.sql(sql, "dbfunc.DBConnection.version (2.4.1-1)"):
                    return False

                sql = """
                    ALTER TABLE profile ADD COLUMN kp_key TEXT
                """
                if not self.sql(sql, "dbfunc.DBConnection.version (2.4.1-3)"):
                    return False

                sql = """
                    ALTER TABLE entwaesserungsarten ADD COLUMN kp_nr INTEGER
                """
                if not self.sql(sql, "dbfunc.DBConnection.version (2.4.1-2)"):
                    return False

                sqllis = [
                    """UPDATE entwaesserungsarten SET kp_nr = 0 WHERE bezeichnung = 'Mischwasser'""",
                    """UPDATE entwaesserungsarten SET kp_nr = 1 WHERE bezeichnung = 'Schmutzwasser'""",
                    """UPDATE entwaesserungsarten SET kp_nr = 2 WHERE bezeichnung = 'Regenwasser'""",
                ]

                for sql in sqllis:
                    if not self.sql(sql, "dbfunc.DBConnection.version (2.4.1-4)"):
                        return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [2, 2, 16]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 4, 9]):

                sql = '''DROP VIEW IF EXISTS "v_linkfl_check"'''

                if not self.sql(sql, "dbfunc.DBConnection.version (2.4.9-1)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_linkfl_check" AS 
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
                        SELECT pk, anzahl, CASE 
                                                WHEN anzahl > 1 THEN 'mehrfach vorhanden'
                                                WHEN flaech_nam IS NULL THEN 'Keine Fläche'
                                                WHEN linkfl_haltnam IS NULL THEN  'Keine Haltung' ELSE 'o.k.'
                                            END AS fehler
                        FROM lfok"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.4.9-2)"):
                    return False

                sql = '''DROP VIEW IF EXISTS "v_flaechen_ohne_linkfl"'''

                if not self.sql(sql, "dbfunc.DBConnection.version (2.4.9-3)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_flaechen_ohne_linkfl" AS 
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
                            (0, '', '', 'o.k.')"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.4.9-4)"):
                    return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [2, 4, 9]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 5, 2]):

                # Einleitungen aus Aussengebieten ----------------------------------------------------------------

                sql = """CREATE TABLE IF NOT EXISTS aussengebiete (
                    pk INTEGER PRIMARY KEY, 
                    gebnam TEXT, 
                    schnam TEXT, 
                    hoeheob REAL, 
                    hoeheun REAL, 
                    fliessweg REAL, 
                    basisabfluss REAL, 
                    cn REAL, 
                    regenschreiber TEXT, 
                    teilgebiet TEXT, 
                    kommentar TEXT, 
                    createdat TEXT DEFAULT CURRENT_DATE)"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.2-1)"):
                    return False

                sql = """SELECT AddGeometryColumn('aussengebiete','geom',{},'MULTIPOLYGON',2)""".format(
                    self.epsg
                )

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.2-2)"):
                    return False

                sql = """SELECT CreateSpatialIndex('aussengebiete','geom')"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.2-3)"):
                    return False

                # Anbindung Aussengebiete -------------------------------------------------------------------------

                sql = """CREATE TABLE IF NOT EXISTS linkageb (
                    pk INTEGER PRIMARY KEY,
                    gebnam TEXT,
                    schnam TEXT)"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.2-4)"):
                    return False

                sql = """SELECT AddGeometryColumn('linkageb','glink',{epsg},'LINESTRING',2)""".format(
                    epsg=self.epsg
                )

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.2-5)"):
                    return False

                sql = """SELECT CreateSpatialIndex('linkageb','glink')"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.2-6)"):
                    return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [2, 5, 2]

                # Formulare aktualisieren ----------------------------------------------------------
                #
                # Dieser Block muss im letzten Update vorkommen, in dem auch Formulare geändert wurden...
                #
                # Spielregel: QKan-Formulare werden ohne Rückfrage aktualisiert.
                # Falls eigene Formulare gewünscht sind, können diese im selben Verzeichnis liegen,
                # die Eingabeformulare müssen jedoch andere Namen verwenden, auf die entsprechend
                # in der Projektdatei verwiesen werden muss.

                # try:
                # projectpath = os.path.dirname(self.dbname)
                # if 'eingabemasken' not in os.listdir(projectpath):
                # os.mkdir(os.path.join(projectpath, 'eingabemasken'))
                # formpath = os.path.join(projectpath, 'eingabemasken')
                # formlist = os.listdir(formpath)

                # logger.debug("\nEingabeformulare aktualisieren: \n" +
                # "projectpath = {projectpath}\n".format(projectpath=projectpath) +
                # "formpath = {formpath}\n".format(formpath=formpath) +
                # "formlist = {formlist}\n".format(formlist=formlist) +
                # "templatepath = {templatepath}".format(templatepath=self.templatepath)
                # )

                # for formfile in glob.iglob(os.path.join(self.templatepath, '*.ui')):
                # logger.debug("Eingabeformular aktualisieren: {} -> {}".format(formfile, formpath))
                # shutil.copy2(formfile, formpath)
                # except BaseException as err:
                # fehlermeldung('Fehler beim Aktualisieren der Eingabeformulare\n',
                # "{e}".format(e=repr(err)))

            # ------------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 5, 7]):
                # Tabelle linkfl um die Felder [abflusstyp, speicherzahl, speicherkonst,
                #                               fliesszeitkanal, fliesszeitflaeche]
                # erweitern. Wegen der Probleme mit der Anzeige in QGIS wird die Tabelle dazu umgespeichert.

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linkfl'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (5)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Temporäre Tabelle anlegen, Daten rüber kopieren,
                #             Tabelle löschen und wieder neu anlegen und Daten zurück kopieren

                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS linkfl_t (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            tezgnam TEXT);""",
                    """SELECT AddGeometryColumn('linkfl_t','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl_t','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl_t','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """DELETE FROM linkfl_t""",
                    """INSERT INTO linkfl_t 
                            (      "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink")
                            SELECT "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink"
                            FROM "linkfl";""",
                    """SELECT DiscardGeometryColumn('linkfl','geom')""",
                    """SELECT DiscardGeometryColumn('linkfl','gbuf')""",
                    """SELECT DiscardGeometryColumn('linkfl','glink')""",
                    """DROP TABLE linkfl;""",
                    """CREATE TABLE linkfl (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            tezgnam TEXT,
                            teilgebiet TEXT,
                            abflusstyp TEXT,
                            speicherzahl INTEGER,
                            speicherkonst REAL,
                            fliesszeitkanal REAL,
                            fliesszeitflaeche REAL);""",
                    """SELECT AddGeometryColumn('linkfl','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('linkfl','glink')""",
                    """INSERT INTO linkfl 
                            (      "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink")
                            SELECT "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink"
                            FROM "linkfl_t";""",
                    """SELECT DiscardGeometryColumn('linkfl_t','geom')""",
                    """SELECT DiscardGeometryColumn('linkfl_t','gbuf')""",
                    """SELECT DiscardGeometryColumn('linkfl_t','glink')""",
                    """DROP TABLE linkfl_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.5.7-1)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'linkfl' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-7)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen
                self.commit()

                # Oberflächenabflussdaten von Tabelle "flaechen" in Tabelle "linkfl" übertragen
                sql = """
                UPDATE linkfl SET 
                    (abflusstyp, speicherzahl, speicherkonst, fliesszeitkanal, fliesszeitflaeche) =
                (SELECT abflusstyp, speicherzahl, speicherkonst, fliesszeitkanal, fliesszeit
                FROM flaechen
                WHERE linkfl.flnam = flaechen.flnam)
                """
                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.7-2)"):
                    return False
                self.commit()

                # Tabelle flaechen um die Felder [abflusstyp, speicherzahl, speicherkonst,
                #                                 fliesszeitkanal, fliesszeitflaeche]
                # bereinigen. Wegen der Probleme mit der Anzeige in QGIS wird die Tabelle dazu umgespeichert.

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='flaechen'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (5)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Temporäre Tabelle anlegen, Daten rüber kopieren,
                #             Tabelle löschen und wieder neu anlegen und Daten zurück kopieren

                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS flaechen_t (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            neigkl INTEGER DEFAULT 0,
                            teilgebiet TEXT,
                            regenschreiber TEXT,
                            abflussparameter TEXT,
                            aufteilen TEXT DEFAULT 'nein',
                            kommentar TEXT,
                            createdat TEXT DEFAULT CURRENT_DATE);""",
                    """SELECT AddGeometryColumn('flaechen_t','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """DELETE FROM flaechen_t""",
                    """
                    INSERT INTO flaechen_t 
                        ("flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen",
                        "kommentar", "createdat", "geom")
                    SELECT "flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter",
                            "aufteilen", "kommentar", "createdat", "geom"
                    FROM "flaechen";
                    """,
                    """SELECT DiscardGeometryColumn('flaechen','geom')""",
                    """DROP TABLE flaechen;""",
                    """CREATE TABLE flaechen (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            neigkl INTEGER DEFAULT 0,
                            teilgebiet TEXT,
                            regenschreiber TEXT,
                            abflussparameter TEXT,
                            aufteilen TEXT DEFAULT 'nein',
                            kommentar TEXT,
                            createdat TEXT DEFAULT CURRENT_DATE);""",
                    """SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('flaechen','geom')""",
                    """
                    INSERT INTO flaechen 
                        ("flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter", 
                        "aufteilen", "kommentar", "createdat", "geom")
                    SELECT "flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter", 
                            "aufteilen", "kommentar", "createdat", "geom"
                    FROM "flaechen_t";
                    """,
                    """SELECT DiscardGeometryColumn('flaechen_t','geom')""",
                    """DROP TABLE flaechen_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.5.7-3)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'flaechen' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-7)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen
                self.commit()

                progress_bar.setValue(75)

                self.reload = True

                # Versionsnummer hochsetzen

                self.versionlis = [2, 5, 7]

            if versionolder(self.versionlis, [2, 5, 8]):

                # Tabelle linkfl um das Feld teilgebiet erweitern.
                # Wegen der Probleme mit der Anzeige in QGIS wird die Tabelle dazu umgespeichert.

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linkfl'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (5)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Temporäre Tabelle anlegen, Daten rüber kopieren,
                #             Tabelle löschen und wieder neu anlegen und Daten zurück kopieren

                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS linkfl_t (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            tezgnam TEXT,
                            abflusstyp TEXT,
                            speicherzahl INTEGER,
                            speicherkonst REAL,
                            fliesszeitkanal REAL,
                            fliesszeitflaeche REAL);""",
                    """SELECT AddGeometryColumn('linkfl_t','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl_t','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl_t','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """DELETE FROM linkfl_t""",
                    """INSERT INTO linkfl_t 
                            (      "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
                                   "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
                                   "geom", "gbuf", "glink")
                            SELECT "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
                                   "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
                                   "geom", "gbuf", "glink"
                            FROM "linkfl";""",
                    """SELECT DiscardGeometryColumn('linkfl','geom')""",
                    """SELECT DiscardGeometryColumn('linkfl','gbuf')""",
                    """SELECT DiscardGeometryColumn('linkfl','glink')""",
                    """DROP TABLE linkfl;""",
                    """CREATE TABLE linkfl (
                            pk INTEGER PRIMARY KEY,
                            flnam TEXT,
                            haltnam TEXT,
                            tezgnam TEXT,
                            teilgebiet TEXT,
                            abflusstyp TEXT,
                            speicherzahl INTEGER,
                            speicherkonst REAL,
                            fliesszeitkanal REAL,
                            fliesszeitflaeche REAL);""",
                    """SELECT AddGeometryColumn('linkfl','geom',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linkfl','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('linkfl','glink')""",
                    """INSERT INTO linkfl 
                            (      "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
                                   "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
                                   "geom", "gbuf", "glink")
                            SELECT "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
                                   "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
                                   "geom", "gbuf", "glink"
                            FROM "linkfl_t";""",
                    """SELECT DiscardGeometryColumn('linkfl_t','geom')""",
                    """SELECT DiscardGeometryColumn('linkfl_t','gbuf')""",
                    """SELECT DiscardGeometryColumn('linkfl_t','glink')""",
                    """DROP TABLE linkfl_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.5.8-1)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'linkfl' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-7)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen
                self.commit()

                # Tabelle linksw -------------------------------------------------------------

                # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
                # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linksw'"""
                # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (3)'):
                # return False
                # triggers = self.fetchall()

                # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
                sqllis = [
                    """BEGIN TRANSACTION;""",
                    """CREATE TABLE IF NOT EXISTS linksw_t (
                            pk INTEGER PRIMARY KEY,
                            elnam TEXT,
                            haltnam TEXT)""",
                    """SELECT AddGeometryColumn('linksw_t','geom',{},'POLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw_t','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw_t','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """DELETE FROM linksw_t""",
                    """INSERT INTO linksw_t 
                            (      "elnam", "haltnam", "geom", "gbuf", "glink")
                            SELECT "elnam", "haltnam", "geom", "gbuf", "glink"
                            FROM "linksw";""",
                    """SELECT DiscardGeometryColumn('linksw','geom')""",
                    """SELECT DiscardGeometryColumn('linksw','gbuf')""",
                    """SELECT DiscardGeometryColumn('linksw','glink')""",
                    """DROP TABLE linksw;""",
                    """CREATE TABLE linksw (
                            pk INTEGER PRIMARY KEY,
                            elnam TEXT,
                            haltnam TEXT,
                            teilgebiet TEXT)""",
                    """SELECT AddGeometryColumn('linksw','geom',{},'POLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw','gbuf',{},'MULTIPOLYGON',2)""".format(
                        self.epsg
                    ),
                    """SELECT AddGeometryColumn('linksw','glink',{},'LINESTRING',2)""".format(
                        self.epsg
                    ),
                    """SELECT CreateSpatialIndex('linksw','geom')""",
                    """INSERT INTO linksw 
                            (      "elnam", "haltnam", "geom", "gbuf", "glink")
                            SELECT "elnam", "haltnam", "geom", "gbuf", "glink"
                            FROM "linksw_t";""",
                    """SELECT DiscardGeometryColumn('linksw_t','geom')""",
                    """SELECT DiscardGeometryColumn('linksw_t','gbuf')""",
                    """SELECT DiscardGeometryColumn('linksw_t','glink')""",
                    """DROP TABLE linksw_t;""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.2.2-4)", transaction=True
                    ):
                        return False

                # 3. Schritt: Trigger wieder herstellen
                # for el in triggers:
                # if el[0] != 'table':
                # sql = el[1]
                # logger.debug("Trigger 'linksw' verarbeitet:\n{}".format(el[1]))
                # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-5)', transaction=True):
                # return False
                # else:
                # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

                # 4. Schritt: Transaction abschließen
                self.commit()

                progress_bar.setValue(90)

                self.reload = True

                # Versionsnummer hochsetzen

                self.versionlis = [2, 5, 8]

            if versionolder(self.versionlis, [2, 5, 9]):

                # ValueMaps durch RelationMaps ersetzen, weil die entsprechende Funktion
                # aus der QGIS-API in Python nicht gemappt ist, somit also in Python nicht verfügbar ist.
                # Deshalb werden nachfolgend drei Tabellen ergänzt. In der Projektdatei muss entsprechend
                # die Felddefinition angepasst werden.

                # 1. Tabelle abflusstypen

                sqllis = [
                    """CREATE TABLE abflusstypen (
                            pk INTEGER PRIMARY KEY, 
                            abflusstyp TEXT)""",
                    """INSERT INTO abflusstypen ('abflusstyp') 
                          Values 
                            ('Fliesszeiten'),
                            ('Schwerpunktlaufzeit'),
                            ('Speicherkaskade')""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.5.9) - abflusstypen"
                    ):
                        return False
                self.commit()

                # 2. Tabelle Knotentypen

                sqllis = [
                    """CREATE TABLE knotentypen (
                            pk INTEGER PRIMARY KEY, 
                            knotentyp TEXT)""",
                    """INSERT INTO knotentypen ('knotentyp') 
                          Values
                            ('Anfangsschacht'),
                            ('Einzelschacht'),
                            ('Endschacht'),
                            ('Hochpunkt'),
                            ('Normalschacht'),
                            ('Tiefpunkt'),
                            ('Verzweigung'),
                            ('Fliesszeiten')""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.5.9) - knotentypen"
                    ):
                        return False
                self.commit()

                # 3. Tabelle Schachttypen

                sqllis = [
                    """CREATE TABLE schachttypen (
                            pk INTEGER PRIMARY KEY, 
                            schachttyp TEXT)""",
                    """INSERT INTO schachttypen ('schachttyp') 
                          Values
                            ('Auslass'),
                            ('Schacht'),
                            ('Speicher')""",
                ]

                for sql in sqllis:
                    if not self.sql(
                        sql, "dbfunc.DBConnection.version (2.5.9) - schachttypen"
                    ):
                        return False
                self.commit()

                progress_bar.setValue(100)

                # Versionsnummer hochsetzen

                self.versionlis = [2, 5, 9]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 5, 24]):

                # Vergleich der Flächengröße mit der Summe der verschnittenen Teile

                sql = '''DROP VIEW IF EXISTS "v_flaechen_check"'''

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.24-1)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_flaechen_check" AS 
                        WITH flintersect AS (
                            SELECT fl.flnam AS finam, 
                                   CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                                   ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                                   END AS flaeche
                            FROM linkfl AS lf
                            INNER JOIN flaechen AS fl
                            ON lf.flnam = fl.flnam
                            LEFT JOIN tezg AS tg
                            ON lf.tezgnam = tg.flnam)
                        SELECT fa.flnam, fi.finam, sum(fi.flaeche) AS fl_int, 
                               AREA(fa.geom) AS fl_ori, sum(fi.flaeche) - AREA(fa.geom) AS diff
                        FROM flaechen AS fa
                        LEFT JOIN flintersect AS fi
                        ON fa.flnam = fi.finam
                        GROUP BY fa.flnam
                        HAVING ABS(sum(fi.flaeche) - AREA(fa.geom)) > 2"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.24-2)"):
                    return False

                sql = '''DROP VIEW IF EXISTS "v_tezg_check"'''

                # Vergleich der Haltungsflächengrößen mit der Summe der verschnittenen Teile

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.24-3)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_tezg_check" AS 
                        WITH flintersect AS (
                            SELECT tg.flnam AS finam, 
                                   CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                                   ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                                   END AS flaeche
                            FROM linkfl AS lf
                            INNER JOIN flaechen AS fl
                            ON lf.flnam = fl.flnam
                            LEFT JOIN tezg AS tg
                            ON lf.tezgnam = tg.flnam)
                        SELECT tg.flnam, fi.finam, sum(fi.flaeche) AS fl_int, 
                               AREA(tg.geom) AS fl_ori, sum(fi.flaeche) - AREA(tg.geom) AS diff
                        FROM tezg AS tg
                        LEFT JOIN flintersect AS fi
                        ON tg.flnam = fi.finam
                        GROUP BY tg.flnam
                        HAVING ABS(sum(fi.flaeche) - AREA(tg.geom)) > 2"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.24-4)"):
                    return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [2, 5, 24]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [2, 5, 27]):

                # Vergleich der Flächengröße mit der Summe der verschnittenen Teile

                sql = '''DROP VIEW IF EXISTS "v_flaechen_check"'''

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.27-1)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_flaechen_check" AS 
                        WITH flintersect AS (
                            SELECT fl.flnam AS finam, 
                                   CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                                   ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                                   END AS flaeche
                            FROM linkfl AS lf
                            INNER JOIN flaechen AS fl
                            ON lf.flnam = fl.flnam
                            LEFT JOIN tezg AS tg
                            ON lf.tezgnam = tg.flnam)
                        SELECT fa.flnam, 
                               AREA(fa.geom) AS flaeche, 
                               sum(fi.flaeche) AS "summe_flaechen_stuecke", 
                               sum(fi.flaeche) - AREA(fa.geom) AS differenz
                        FROM flaechen AS fa
                        LEFT JOIN flintersect AS fi
                        ON fa.flnam = fi.finam
                        GROUP BY fa.flnam
                        HAVING ABS(sum(fi.flaeche) - AREA(fa.geom)) > 2"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.27-2)"):
                    return False

                sql = '''DROP VIEW IF EXISTS "v_tezg_check"'''

                # Vergleich der Haltungsflächengrößen mit der Summe der verschnittenen Teile

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.27-3)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_tezg_check" AS 
                        WITH flintersect AS (
                            SELECT tg.flnam AS finam, 
                                   CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                                   ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                                   END AS flaeche
                            FROM linkfl AS lf
                            INNER JOIN flaechen AS fl
                            ON lf.flnam = fl.flnam
                            LEFT JOIN tezg AS tg
                            ON lf.tezgnam = tg.flnam)
                        SELECT tg.flnam, 
                               AREA(tg.geom) AS haltungsflaeche, 
                               sum(fi.flaeche) AS summe_flaechen_stuecke, 
                               sum(fi.flaeche) - AREA(tg.geom) AS differenz
                        FROM tezg AS tg
                        LEFT JOIN flintersect AS fi
                        ON tg.flnam = fi.finam
                        GROUP BY tg.flnam
                        HAVING ABS(sum(fi.flaeche) - AREA(tg.geom)) > 2"""

                if not self.sql(sql, "dbfunc.DBConnection.version (2.5.27-4)"):
                    return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [2, 5, 27]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [3, 0, 1]):

                # Spalte "teilgebiet" in Tabelle "pumpen" ergänzen
                attrlis = self.attrlist("pumpen")
                if not attrlis:
                    fehlermeldung(
                        "dbfunc.DBConnection.version (3.0.1):",
                        "attrlis für pumpen ist leer",
                    )
                    return False
                elif "teilgebiet" not in attrlis:
                    logger.debug(
                        "pumpen.teilgebiet ist nicht in: {}".format(str(attrlis))
                    )

                self.alter_table(
                    "pumpen",
                    [
                        "pnam TEXT",
                        "schoben TEXT",
                        "schunten TEXT",
                        "pumpentyp TEXT",
                        "volanf REAL",
                        "volges REAL",
                        "sohle REAL",
                        "steuersch TEXT",
                        "einschalthoehe REAL",
                        "ausschalthoehe REAL",
                        "teilgebiet TEXT",
                        "simstatus TEXT DEFAULT 'vorhanden'",
                        "kommentar TEXT",
                        "createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now'))",
                    ],
                    ["volanf", "volges"],
                )

                # Spalte "teilgebiet" in Tabelle "wehre" ergänzen
                attrlis = self.attrlist("wehre")
                if not attrlis:
                    fehlermeldung(
                        "dbfunc.DBConnection.version (3.0.1):",
                        "attrlis für wehre ist leer",
                    )
                    return False
                elif "teilgebiet" not in attrlis:
                    logger.debug(
                        "wehre.teilgebiet ist nicht in: {}".format(str(attrlis))
                    )

                self.alter_table(
                    "wehre",
                    [
                        "wnam TEXT",
                        "schoben TEXT",
                        "schunten TEXT",
                        "wehrtyp TEXT",
                        "schwellenhoehe REAL",
                        "kammerhoehe REAL",
                        "laenge REAL",
                        "uebeiwert REAL",
                        "aussentyp TEXT",
                        "aussenwsp REAL",
                        "teilgebiet TEXT",
                        "simstatus TEXT DEFAULT 'vorhanden'",
                        "kommentar TEXT",
                        "createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now'))",
                    ],
                )

                # Versionsnummer hochsetzen

                self.versionlis = [3, 0, 1]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [3, 0, 2]):

                #  Temporäre Tabelle zum Export von Flächen für HE 8 -----------------------------

                sql = """
                    CREATE TABLE IF NOT EXISTS flaechen_he8 (
                        pk INTEGER PRIMARY KEY,
                        Name TEXT, 
                        Haltung TEXT, 
                        Groesse REAL, 
                        Regenschreiber TEXT, 
                        BerechnungSpeicherkonstante INTEGER, 
                        Typ INTEGER, 
                        AnzahlSpeicher INTEGER, 
                        Speicherkonstante REAL, 
                        Schwerpunktlaufzeit REAL, 
                        FliesszeitOberflaeche REAL, 
                        LaengsteFliesszeitKanal REAL, 
                        Parametersatz TEXT, 
                        Neigungsklasse INTEGER, 
                        ZuordnUnabhEZG INTEGER,
                        LastModified TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')), 
                        Kommentar TEXT)"""

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.2-1)"):
                    return False

                sql = """SELECT AddGeometryColumn('flaechen_he8','Geometry',{epsg},
                        'MULTIPOLYGON',2)""".format(
                    epsg=self.epsg
                )

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.2-2)"):
                    return False

                sql = """SELECT CreateSpatialIndex('flaechen_he8','Geometry')"""

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.2-3)"):
                    return False

                # Erweitern der Tabelle "abflusstypen"

                sqllis = [
                    """ALTER TABLE abflusstypen ADD COLUMN he_nr INTEGER""",
                    """ALTER TABLE abflusstypen ADD COLUMN kp_nr INTEGER""",
                ]

                for sql in sqllis:
                    if not self.sql(sql, "dbfunc.DBConnection.version (3.0.2-4)"):
                        return False

                # Initialisierung

                daten = [
                    "'Speicherkaskade', 0, 0",
                    "'Direktabfluss', 0, 0",
                    "'Fliesszeiten', 1, 1",
                    "'Schwerpunktlaufzeit', 2, 2",
                    "'Schwerpunktfließzeit', 2, 2",
                ]

                for ds in daten:
                    sql = """INSERT INTO abflusstypen
                             (abflusstyp, he_nr, kp_nr) Values ({})""".format(
                        ds
                    )
                    if not self.sql(sql, "dbfunc.DBConnection.version (3.0.2-5)"):
                        return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [3, 0, 2]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [3, 0, 5]):

                # Zusätzliches Attribut flaechentyp in abflussfaktoren -----------------------------

                sql = """
                    ALTER TABLE abflussparameter ADD COLUMN flaechentyp TEXT"""

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.5-1)"):
                    return False

                # Initialisierung

                for nam, typ in [
                    ["$Default_Unbef", "Grünfläche"],
                    ["Gebäude", "Gebäude"],
                    ["Straße", "Straße"],
                    ["Grünfläche", "Grünfläche"],
                    ["Gewässer", "Gewässer"],
                ]:
                    sql = """UPDATE abflussparameter
                             SET flaechentyp = '{typ}'
                             WHERE apnam = '{nam}'
                             """.format(
                        typ=typ, nam=nam
                    )
                    if not self.sql(sql, "dbfunc.DBConnection.version (3.0.5-2)"):
                        return False

                # Neue Tabelle "flaechentypen"

                sql = """CREATE TABLE IF NOT EXISTS flaechentypen (
                    pk INTEGER PRIMARY KEY,
                    bezeichnung TEXT,
                    he_nr INTEGER)"""

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.5-3)"):
                    return False

                # Initialisierung

                for bez, num in [
                    ["Gebäude", 0],
                    ["Straße", 1],
                    ["Grünfläche", 2],
                    ["Gewässer", 3],
                ]:
                    sql = """INSERT INTO flaechentypen
                             (bezeichnung, he_nr) Values ('{bez}', {num})""".format(
                        bez=bez, num=num
                    )
                    if not self.sql(sql, "dbfunc.DBConnection.version (3.0.5-4)"):
                        return False

                # Zusätzliche Attribute flaechen_he8

                attrlis = [
                    "Flaechentyp INTEGER",
                    "IstPolygonalflaeche INTEGER",
                    "ZuordnungGesperrt INTEGER",
                ]

                for attr in attrlis:
                    sql = f"ALTER TABLE flaechen_he8 ADD COLUMN {attr}"

                    if not self.sql(sql, "dbfunc.DBConnection.version (3.0.5-5)"):
                        return False

                # Änderung des EPSG-Codes in flaechen_he8 auf -1

                sqllis = [
                    "SELECT DiscardGeometryColumn('flaechen_he8', 'Geometry')",
                    "SELECT AddGeometryColumn('flaechen_he8','Geometry', -1, 'MULTIPOLYGON',2)",
                ]

                for sql in sqllis:
                    if not self.sql(sql, "dbfunc.DBConnection.version (3.0.5-6)"):
                        return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [3, 0, 5]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [3, 0, 8]):

                sqllis = [
                    """SELECT DiscardGeometryColumn('flaechen_he8', 'Geometry')""",
                    """DROP TABLE flaechen_he8;""",
                    """CREATE TABLE IF NOT EXISTS flaechen_he8 (
                        pk INTEGER PRIMARY KEY,
                        Name TEXT, 
                        Haltung TEXT, 
                        Groesse REAL, 
                        Regenschreiber TEXT, 
                        Flaechentyp INTEGER, 
                        BerechnungSpeicherkonstante INTEGER, 
                        Typ INTEGER, 
                        AnzahlSpeicher INTEGER, 
                        Speicherkonstante REAL, 
                        Schwerpunktlaufzeit REAL, 
                        FliesszeitOberflaeche REAL, 
                        LaengsteFliesszeitKanal REAL, 
                        Parametersatz TEXT, 
                        Neigungsklasse INTEGER, 
                        ZuordnUnabhEZG INTEGER,
                        IstPolygonalflaeche SMALLINT, 
                        ZuordnungGesperrt SMALLINT, 
                        LastModified TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')), 
                        Kommentar TEXT)""",
                    """SELECT AddGeometryColumn('flaechen_he8','Geometry', -1,'MULTIPOLYGON',2)""",
                ]

                for sql in sqllis:
                    if not self.sql(sql, "dbfunc.DBConnection.version (3.0.8-1)"):
                        return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [3, 0, 8]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [3, 0, 10]):

                sql = '''DROP VIEW IF EXISTS "v_linkfl_redundant"'''

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.10-1)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_linkfl_redundant" AS 
                        WITH lfm AS (
                            SELECT flnam, tezgnam, count(*) AS anz
                            FROM linkfl AS lf
                            GROUP BY flnam, tezgnam)
                        SELECT lf.pk, lf.flnam, lf.tezgnam, lfm.anz
                        FROM linkfl AS lf
                        LEFT JOIN lfm
                        ON lf.flnam = lfm.flnam and lf.tezgnam = lfm.tezgnam
                        WHERE anz <> 1 or lf.flnam IS NULL
                        ORDER BY lf.flnam"""

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.10-2)"):
                    return False

                sql = '''DROP VIEW IF EXISTS "v_linksw_redundant"'''

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.10-3)"):
                    return False

                sql = """CREATE VIEW IF NOT EXISTS "v_linksw_redundant" AS 
                        WITH lsm AS (
                            SELECT elnam, count(*) AS anz
                            FROM linksw AS ls
                            GROUP BY elnam)
                        SELECT ls.pk, ls.elnam, lsm.anz
                        FROM linksw AS ls
                        LEFT JOIN lsm
                        ON ls.elnam = lsm.elnam
                        WHERE anz <> 1 or ls.elnam IS NULL
                        ORDER BY ls.elnam"""

                if not self.sql(sql, "dbfunc.DBConnection.version (3.0.10-4)"):
                    return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [3, 0, 10]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [3, 1, 2]):

                # Zusätzliches Attribut befgrad in tezg -----------------------------

                sql = """
                    ALTER TABLE tezg ADD COLUMN befgrad REAL"""

                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.2-1)"):
                    return False

                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [3, 1, 2]

            # ------------------------------------------------------------------------------------
            if versionolder(self.versionlis, [3, 1, 3]):

                # Flächen können auch an Schächte angeschlossen sein. Dies gilt bei
                # folgenden Programmen:
                # SWMM, Mike Urban

                sql = """
                    ALTER TABLE flaechen ADD COLUMN schnam TEXT"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-1)"):
                    return False
                self.commit()

                sql = """
                    ALTER TABLE tezg ADD COLUMN schnam TEXT"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-2)"):
                    return False
                self.commit()

                sql = """
                    ALTER TABLE tezg ADD COLUMN neigung REAL"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-3)"):
                    return False
                self.commit()

                sql = """
                    ALTER TABLE linkfl ADD COLUMN schnam TEXT"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-4)"):
                    return False
                self.commit()

                sql = """
                    ALTER TABLE linksw ADD COLUMN schnam TEXT"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-5)"):
                    return False
                self.commit()

                sql = """
                    ALTER TABLE einleit ADD COLUMN schnam TEXT"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-6)"):
                    return False
                self.commit()

                # Zusätzliche Parameter für SWMM

                sql = """
                    ALTER TABLE abflussparameter ADD COLUMN rauheit_kst REAL"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-7)"):
                    return False
                self.commit()

                sql = """
                    ALTER TABLE abflussparameter ADD COLUMN pctZero REAL"""
                if not self.sql(sql, "dbfunc.DBConnection.version (3.1.3-8)"):
                    return False
                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [3, 1, 3]

            # ------------------------------------------------------------------------------------

            # Version 3.1.4: Trigger wurden verworfen, deshalb Zusatz unter Version 3.1.5

            # ------------------------------------------------------------------------------------
            logger.debug(f"Version: {self.versionlis}")
            if versionolder(self.versionlis, [3, 1, 5]):
                logger.debug(f"Version älter 3.1.5 erkannt: {self.versionlis}")
                if not versionolder(self.versionlis, [3, 1, 4]):
                    logger.debug(f"Version 3.1.4 erkannt: {self.versionlis}")
                    # Trigger aus Version 3.1.4 wieder löschen

                    if not self.sql(
                        "DROP TRIGGER create_missing_geoobject_haltungen",
                        "dbfunc.DBConnection.version (3.1.5-1",
                    ):
                        return False
                    self.commit()

                    if not self.sql(
                        "DROP TRIGGER create_missing_geoobject_schaechte",
                        "dbfunc.DBConnection.version (3.1.5-2",
                    ):
                        return False
                    self.commit()

                    if not self.sql(
                        "DROP TRIGGER create_missing_geoobject_pumpen",
                        "dbfunc.DBConnection.version (3.1.5-3",
                    ):
                        return False
                    self.commit()

                    if not self.sql(
                        "DROP TRIGGER create_missing_geoobject_wehre",
                        "dbfunc.DBConnection.version (3.1.5-4",
                    ):
                        return False
                    self.commit()

                # Schächte -----------------------------------------------------------------

                sql = f"""CREATE VIEW IF NOT EXISTS schaechte_data AS 
                      SELECT
                        schnam, 
                        xsch, ysch, 
                        sohlhoehe, 
                        deckelhoehe, durchm, 
                        druckdicht, ueberstauflaeche, 
                        entwart, strasse, teilgebiet, 
                        knotentyp, auslasstyp, schachttyp, 
                        simstatus, 
                        kommentar, createdat
                      FROM schaechte;"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-5)"
                    + "VIEW schaechte_data konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                sql = f"""CREATE TRIGGER IF NOT EXISTS schaechte_insert_clipboard
                        INSTEAD OF INSERT ON schaechte_data FOR EACH ROW
                      BEGIN
                        INSERT INTO schaechte
                          (schnam, sohlhoehe, 
                           deckelhoehe, durchm, 
                           druckdicht, ueberstauflaeche, 
                           entwart, strasse, teilgebiet, 
                           knotentyp, auslasstyp, schachttyp, 
                           simstatus, 
                           kommentar, createdat, 
                           geop, geom)
                        VALUES (
                          new.schnam, new.sohlhoehe,
                          new.deckelhoehe, 
                          CASE WHEN new.durchm > 200 THEN new.durchm/1000 ELSE new.durchm END, 
                          coalesce(new.druckdicht, 0), coalesce(new.ueberstauflaeche, 0), 
                          coalesce(new.entwart, 'Regenwasser'), new.strasse, new.teilgebiet, 
                          new.knotentyp, new.auslasstyp, coalesce(new.schachttyp, 'Schacht'), 
                          coalesce(new.simstatus, 'vorhanden'),
                          new.kommentar, coalesce(new.createdat, strftime('%d.%m.%Y %H:%M','now')),
                          MakePoint(new.xsch, new.ysch, {self.epsg}),
                          CastToMultiPolygon(
                            MakePolygon(
                              MakeCircle(
                                new.xsch,
                                new.ysch,
                                coalesce(new.durchm/2, 0.5), {self.epsg}
                              )
                            )
                          )
                        );
                      END"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-6)"
                    + "TRIGGER schaechte_insert_clipboard konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                # Haltungen -----------------------------------------------------------------

                sql = f"""CREATE VIEW IF NOT EXISTS haltungen_data AS
                      SELECT 
                        haltnam, schoben, schunten, 
                        hoehe, breite, laenge, 
                        sohleoben, sohleunten, 
                        deckeloben, deckelunten, 
                        xschob, yschob, xschun, yschun, 
                        teilgebiet, qzu, profilnam, 
                        entwart, rohrtyp, ks,
                        simstatus, kommentar, createdat
                      FROM haltungen;"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-5)"
                    + "VIEW haltungen_data konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                sql = f"""CREATE TRIGGER IF NOT EXISTS haltungen_insert_clipboard
                        INSTEAD OF INSERT ON haltungen_data FOR EACH ROW
                      BEGIN
                        INSERT INTO haltungen
                          (haltnam, schoben, schunten,
                           hoehe, breite, laenge,
                           sohleoben, sohleunten,
                           deckeloben, deckelunten, 
                           teilgebiet, qzu, profilnam, 
                           entwart, rohrtyp, ks,
                           simstatus, kommentar, createdat,  
                           geom)
                        SELECT 
                          new.haltnam, new.schoben, new.schunten, 
                          CASE WHEN new.hoehe > 20 THEN new.hoehe/1000 ELSE new.hoehe END, 
                          CASE WHEN new.breite > 20 THEN new.breite/1000 ELSE new.breite END,
                          new.laenge, 
                          new.sohleoben, new.sohleunten, 
                          new.deckeloben, new.deckelunten, 
                          new.teilgebiet, new.qzu, coalesce(new.profilnam, 'Kreisquerschnitt'), 
                          coalesce(new.entwart, 'Regenwasser'), new.rohrtyp, coalesce(new.ks, 1.5), 
                          coalesce(new.simstatus, 'vorhanden'), new.kommentar, 
                          coalesce(new.createdat, strftime('%d.%m.%Y %H:%M','now')), 
                          MakeLine(
                            coalesce(
                              MakePoint(new.xschob, new.yschob, {self.epsg}),
                              schob.geop
                            ), 
                            coalesce(
                              MakePoint(new.xschun, new.yschun, {self.epsg}),
                              schun.geop
                            )
                          )
                        FROM
                          schaechte AS schob,
                          schaechte AS schun
                        WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
                      END;"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-6)"
                    + "TRIGGER haltungen_insert_clipboard konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                # Pumpen -----------------------------------------------------------------

                sql = f"""CREATE VIEW IF NOT EXISTS pumpen_data AS
                      SELECT 
                        pnam, schoben, schunten, 
                        pumpentyp, volanf, volges, 
                        sohle, steuersch, 
                        einschalthoehe, ausschalthoehe,
                        teilgebiet, simstatus, 
                        kommentar, createdat
                      FROM pumpen;"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-5)"
                    + "VIEW haltungen_data konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                sql = f"""CREATE TRIGGER IF NOT EXISTS pumpen_insert_clipboard
                        INSTEAD OF INSERT ON pumpen_data FOR EACH ROW
                      BEGIN
                        INSERT INTO pumpen
                          (pnam, schoben, schunten, 
                           pumpentyp, volanf, volges, 
                           sohle, steuersch, 
                           einschalthoehe, ausschalthoehe,
                           teilgebiet, simstatus, 
                           kommentar, createdat, 
                           geom)
                        SELECT 
                          new.pnam, new.schoben, new.schunten, 
                          new.pumpentyp, new.volanf, new.volges, 
                          new.sohle, new.steuersch, 
                          new.einschalthoehe, new.ausschalthoehe,
                          new.teilgebiet, coalesce(new.simstatus, 'vorhanden'), 
                          new.kommentar, new.createdat,
                          MakeLine(schob.geop, schun.geop)
                        FROM
                          schaechte AS schob,
                          schaechte AS schun
                        WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
                      END;"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-6)"
                    + "TRIGGER haltungen_insert_clipboard konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                # Wehre -----------------------------------------------------------------

                sql = f"""CREATE VIEW IF NOT EXISTS wehre_data AS
                      SELECT 
                        wnam, schoben, schunten, 
                        wehrtyp, schwellenhoehe, kammerhoehe, 
                        laenge, uebeiwert, aussentyp, aussenwsp, 
                        teilgebiet, simstatus, 
                        kommentar, createdat
                      FROM wehre;"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-5)"
                    + "VIEW haltungen_data konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                sql = f"""CREATE TRIGGER IF NOT EXISTS wehre_insert_clipboard
                        INSTEAD OF INSERT ON wehre_data FOR EACH ROW
                      BEGIN
                        INSERT INTO wehre
                          (wnam, schoben, schunten, 
                           wehrtyp, schwellenhoehe, kammerhoehe, 
                           laenge, uebeiwert, aussentyp, aussenwsp, 
                           teilgebiet, simstatus, 
                           kommentar, createdat, 
                           geom)
                        SELECT 
                          new.wnam, new.schoben, new.schunten, 
                          new.wehrtyp, new.schwellenhoehe, new.kammerhoehe, 
                          new.laenge, new.uebeiwert, new.aussentyp, new.aussenwsp, 
                          new.teilgebiet, coalesce(new.simstatus, 'vorhanden'), 
                          new.kommentar, new.createdat,
                          MakeLine(schob.geop, schun.geop)
                        FROM
                          schaechte AS schob,
                          schaechte AS schun
                        WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
                      END;"""
                if not self.sql(
                    sql,
                    "dbfunc.DBConnection.version (3.1.5-6)"
                    + "TRIGGER haltungen_insert_clipboard konnten nicht erstellt werden.",
                ):
                    return False
                self.commit()

                # Versionsnummer hochsetzen

                self.versionlis = [3, 1, 5]

            # ------------------------------------------------------------------------------------
            # Aktuelle Version in Tabelle "info" schreiben

            sql = """UPDATE info SET value = '{}' WHERE subject = 'version'""".format(
                self.actversion
            )
            if not self.sql(sql, "dbfunc.DBConnection.version (aktuell)"):
                return False

            self.commit()

            if self.reload:
                meldung(
                    "Achtung! Benutzerhinweis!",
                    "Die Datenbank wurde geändert. Bitte QGIS-Projekt nach dem Speichern neu laden...",
                )
                return False

        # Alles gut gelaufen...
        return True
