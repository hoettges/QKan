"""
Datenbankmanagement

Definition einer Klasse mit Methoden fuer den Zugriff auf
eine SpatiaLite-Datenbank.
"""

import datetime
import os
import shutil
import sqlite3
from array import array
from distutils.version import LooseVersion
from sqlite3 import Connection
from typing import Any, List, Optional, Union, cast, Dict, Tuple
from fnmatch import fnmatch

from qgis.core import Qgis, QgsVectorLayer, QgsGeometry, QgsPoint
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import spatialite_connect

from qkan import QKan
from .qkan_database import createdbtables, db_version
from .qkan_utils import fehlermeldung, warnung, meldung, get_database_QKan

__author__ = "Joerg Hoettges"
__date__ = "September 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"

from ..utils import get_logger

logger = get_logger("QKan.database.dbfunc")


# Pruefung, ob in Tabellen oder Spalten unerlaubte Zeichen enthalten sind
def checkchars(text: str) -> bool:
    """
    Pruefung auf nicht erlaubte Zeichen in Tabellen- und Spaltennamen.

    :param text: zu pruefende Bezeichnung einer Tabelle oder Tabellenspalte

    :returns: Testergebnis: True = alles o.k.
    """

    return not (max([ord(t) > 127 for t in text]) or ("." in text) or ("-" in text))


class DBConnectError(Exception):
    """Raised when connecting to the database fails."""


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

        :param dbname:      Pfad zur SpatiaLite-Datenbankdatei.
                            - Falls angegeben und nicht vorhanden, wird es angelegt.
                            - Falls nicht angegeben, wird die Datenbank aus den Layern "Schächte" und
                              "Flächen" gelesen und verbunden
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
        self.sqltime = datetime.datetime.now()
        self.sqltext = ""
        self.sqlcount = 0

        self.actversion: str = db_version()

        # QKan-Datenbank ist auf dem aktuellen Stand.
        self.isCurrentVersion = True

        # Verbindung hergestellt, d.h. weder fehlgeschlagen noch wegen reload geschlossen
        self.connected = True

        # reload = True: Datenbank wurde aktualisiert und dabei sind gravierende Änderungen aufgetreten,
        # die ein Neuladen des Projektes erforderlich machen
        self.reload = False

        self.current_version = LooseVersion("0.0.0")

        self._connect(tab_object=tab_object, qkan_db_update=qkan_db_update)

    def __enter__(self) -> "DBConnection":
        """Allows use via context manager for easier connection handling"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes connection once we're out of context"""
        self._disconnect()

    def __del__(self) -> None:
        """Closes connection once object is deleted"""
        # warnings.warn(
        #     "Deleting the database object is deprecated. Use a context manager instead.",
        #     DeprecationWarning,
        # )
        self._disconnect()

    def _connect(
        self, tab_object: Optional[QgsVectorLayer], qkan_db_update: bool
    ) -> None:
        """Connects to SQLite3 database.

        Raises:
            DBConnectError: dbname is not set & could not be determined from project
        """
        if tab_object is not None:
            self._connect_with_object(tab_object)
            return

        if not self.dbname:
            self.dbname, _ = get_database_QKan()
            if not self.dbname:
                fehlermeldung("Fehler: Für den Export muss ein Projekt geladen sein!")
                raise DBConnectError()

        # Load existing database
        if os.path.exists(self.dbname):
            self.consl = spatialite_connect(
                database=self.dbname, check_same_thread=False
            )
            self.cursl = self.consl.cursor()

            self.epsg = self.getepsg()
            if self.epsg is None:
                logger.error(
                    "dbfunc.DBConnection.__init__: EPSG konnte nicht ermittelt werden. \n"
                    + " QKan-DB: {}\n".format(self.dbname)
                )

            logger.debug(
                "dbfunc.DBConnection.__init__: Datenbank existiert und Verbindung hergestellt:\n"
                + "{}".format(self.dbname)
            )

            # Versionsprüfung
            if not self.check_version():
                logger.debug("dbfunc: Datenbank ist nicht aktuell")
                if qkan_db_update:
                    logger.debug(
                        "dbfunc: Update aktiviert. Deshalb wird Datenbank aktualisiert"
                    )
                    self.upgrade_database()
                else:
                    warnung(
                        f"Projekt muss aktualisiert werden. Die QKan-Version der Datenbank {self.current_version} stimmt nicht ",
                        f"mit der aktuellen QKan-Version {self.actversion} überein und muss aktualisiert werden!",
                    )
                    self.consl.close()
                    self.isCurrentVersion = False
                    self.connected = False

                    return None

        # Create new database
        else:
            QKan.instance.iface.messageBar().pushMessage(
                "Information",
                "SpatiaLite-Datenbank wird erstellt. Bitte waren...",
                level=Qgis.Info,
            )

            datenbank_qkan_template = os.path.join(QKan.template_dir, "qkan.sqlite")
            try:
                shutil.copyfile(datenbank_qkan_template, self.dbname)

                self.consl = spatialite_connect(database=self.dbname)
                self.cursl = self.consl.cursor()

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
                logger.debug(f"Datenbank ist nicht vorhanden: {self.dbname}")
                fehlermeldung(
                    "Fehler in dbfunc.DBConnection:\n{}\n".format(err),
                    "Kopieren von: {}\nnach: {}\n nicht möglich".format(
                        QKan.template_dir, self.dbname
                    ),
                )
                self.connected = False
                self.consl = None

    def _connect_with_object(self, tab_object: QgsVectorLayer) -> None:
        tab_connect = tab_object.publicSource()
        t_db, t_tab, t_geo, t_sql = tuple(tab_connect.split())
        self.dbname = t_db.split("=")[1].strip("'")
        self.tabname = t_tab.split("=")[1].strip('"')

        # Pruefung auf korrekte Zeichen in Namen
        if not checkchars(self.tabname):
            fehlermeldung(
                "Fehler",
                "Unzulaessige Zeichen in Tabellenname: {}".format(self.tabname),
            )
            self.connected = False
            self.consl = None

    def _disconnect(self) -> None:
        """Closes database connection."""
        try:
            if self.consl is not None:
                cast(Connection, self.consl).close()
            logger.debug(f"Verbindung zur Datenbank {self.dbname} wieder geloest.")
        except sqlite3.Error:
            fehlermeldung(
                "Fehler in dbfunc.DBConnection:",
                f"Verbindung zur Datenbank {self.dbname} konnte nicht geloest werden.\n",
            )

    def attrlist(self, tablenam: str) -> Union[List[str]]:
        """Gibt Spaltenliste zurück."""

        if not self.sql(
            f"PRAGMA table_info({tablenam})",
            f"dbfunc.DBConnection.attrlist fuer {tablenam}",
        ):
            return []

        daten = self.cursl.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == 'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def getepsg(self) -> Optional[int]:
        """Feststellen des EPSG-Codes der Datenbank"""

        sql = """
        SELECT srid
        FROM geom_cols_ref_sys
        WHERE Lower(f_table_name) = Lower('haltungen')
        AND Lower(f_geometry_column) = Lower('geom')
        """
        if not self.sql(sql, "dbfunc.DBConnection.getepsg (1)"):
            return None

        data = self.fetchone()
        if data is None:
            meldung(
                "Fehler in dbfunc.DBConnection.getepsg (2)",
                "Konnte EPSG nicht ermitteln",
            )
            return None

        return data[0]

    def sql(
        self,
        sql: str,
        stmt_category: str = "allgemein",
        parameters: Union[Tuple, List, dict[str, any]] = (),
        many: bool = False,
        mute_logger: bool = False,
        ignore: bool = False,
    ) -> bool:
        """Execute a sql query on connected database

        :sql:                   SQL-statement
        :type sql:              String

        :stmt_category:         Category name. Allows suppression of sql-statement in logfile for
                                2 seconds appending on mute_logger
        :type stmt_category:    String

        :parameters:            parameters used in sql statement
        :type parameters:       Tuple, List or Dict

        :many:                  executes sql for every element in parameters -> must be a sequence of lists
        :type many:             Boolean

        :mute_logger:           suppress logging message for the same stmt_category for 2 seconds
        :type mute_logger:      String

        :ignore:                ignore error and continue
        :type ignore:           Boolean

        :returns: void
        """
        if not self.isCurrentVersion:
            warnung(
                f"Projekt muss aktualisiert werden. Die QKan-Version der Datenbank {self.current_version} stimmt nicht ",
                f"mit der aktuellen QKan-Version {self.actversion} überein und muss aktualisiert werden!",
            )
            return False
        try:
            # fürs logging:
            if isinstance(parameters, tuple):
                logparams = parameters[:5]      # Länge der Ausgabe beschränken...
            else:
                logparams = parameters

            if many:
                try:
                    self.cursl.executemany(sql, parameters)
                except ValueError as err:
                    raise ValueError(f"{err}\nTyp von parameters: {type(parameters)}")
            else:
                try:
                    self.cursl.execute(sql, parameters)
                except ValueError as err:
                    logger.error(f"{err}\nTyp von parameters: {type(parameters)}")
                    raise ValueError(f"{err}\nTyp von parameters: {type(parameters)}")

            if mute_logger:
                return True

            # Suppress log message for 2 seconds if category is identical to last query
            if self.sqltext == stmt_category:
                self.sqlcount += 1
                if (self.sqltime.now() - self.sqltime).seconds < 2:
                    return True
            else:
                self.sqlcount = 0
                self.sqltext = stmt_category

            # Log-Message if new category or same category for more than 2 seconds
            self.sqltime = self.sqltime.now()
            logger.debug(
                "dbfunc.DBConnection.sql (Nr. {}): {}\nsql: {}\nparameters: {}\n".format(
                    self.sqlcount+1, stmt_category, sql, logparams
                )
            )
            return True
        except sqlite3.Error as e:
            if ignore:
                logger.debug(f'Typ von parameters: {type(parameters)}')
                warnung(
                    "dbfunc.DBConnection.sql: SQL-Fehler in {e}".format(
                        e=stmt_category
                    ),
                    "{e}\n{s}\n{p}".format(e=repr(e), s=sql, p=logparams),
                )
            else:
                logger.debug(f'Typ von parameters: {type(parameters)}')
                logger.error(f"dbfunc.sql: \nsql: {sql}\n" f"parameters: {logparams}")
                fehlermeldung(
                    "dbfunc.DBConnection.sql: SQL-Fehler in {e}".format(
                        e=stmt_category
                    ),
                    "{e}\n{s}\n{p}".format(e=repr(e), s=sql, p=logparams),
                )
                self._disconnect()
            return False

    def insertdata(
            self,
            tabnam: str,
            stmt_category: str = "allgemein",
            mute_logger: bool = False,
            ignore: bool = False,  # ignore error and continue
            parameters: [dict, tuple] = None
    ) -> bool:
        """Fügt einen Datensatz mit Geo-Objekt hinzu

        :tabnam:            Tabelle zum Einfügen der Daten
        :stmt_category:     Erläuterung für Protokoll und Fehlermeldungen
        :mute_logger:       suppress logging message for the same stmt_category for 2 seconds
        :ignore:            ignore error and continue
        :parameters:        Parameter für das SQL-Statement, 2 Varainten:
                             - dict:  einzelner Datensatz wird eingefügt
                             - tuple: jeder Datensatz muss ein dict darstellen und wird mit "executemany" eingefügt
        """

        if isinstance(parameters, tuple):
            param1 = parameters[0]
        else:
            param1 = parameters

        if tabnam == "schaechte":
            parlis = [
                "schnam",
                "sohlhoehe",
                "deckelhoehe",
                "durchm",
                "druckdicht",
                "ueberstauflaeche",
                "entwart",
                "strasse",
                "baujahr",
                "teilgebiet",
                "knotentyp",
                "auslasstyp",
                "schachttyp",
                "simstatus",
                "material",
                "kommentar",
                "createdat",
                "xsch",
                "ysch",
                "geom",
                "geop",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = """
                INSERT INTO schaechte (
                    schnam, sohlhoehe, deckelhoehe, 
                    durchm, 
                    druckdicht,
                    ueberstauflaeche, 
                    entwart, strasse, baujahr, teilgebiet, 
                    knotentyp, auslasstyp, schachttyp,
                    simstatus, material,
                    kommentar, createdat, 
                    geop, geom)
               VALUES (
                    :schnam, :sohlhoehe, :deckelhoehe,
                    CASE WHEN :durchm > 200 THEN :durchm/1000 ELSE :durchm END, 
                    :druckdicht, coalesce(:ueberstauflaeche, 0), 
                    coalesce(:entwart, 'Regenwasser'), :strasse, :baujahr, :teilgebiet, 
                    :knotentyp, :auslasstyp, coalesce(:schachttyp, 'Schacht'), 
                    coalesce(:simstatus, 'vorhanden'), :material,
                    :kommentar, coalesce(:createdat, CURRENT_TIMESTAMP),
                    CASE WHEN :geop IS NULL
                        THEN MakePoint(:xsch, :ysch, :epsg)
                        ELSE GeomFromWKB(:geop, :epsg)
                    END,
                    CASE WHEN :geom IS NULL
                        THEN CastToMultiPolygon(MakePolygon(
                            MakeCircle(:xsch,:ysch,coalesce(:durchm, 1.0)/2.0, :epsg)))
                        ELSE GeomFromWKB(:geom, :epsg)
                    END);"""

        elif tabnam == "haltungen":
            parlis = [
                "haltnam",
                "baujahr",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "laenge",
                "aussendurchmesser",
                "sohleoben",
                "sohleunten",
                "teilgebiet",
                "profilnam",
                "entwart",
                "strasse",
                "material",
                "profilauskleidung",
                "innenmaterial",
                "ks",
                "haltungstyp",
                "simstatus",
                "kommentar",
                "createdat",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = """
                INSERT INTO haltungen
                  (haltnam, baujahr, schoben, schunten,
                   hoehe, breite, laenge, aussendurchmesser,
                   sohleoben, sohleunten, 
                   teilgebiet, profilnam, 
                   entwart, strasse, material, profilauskleidung, innenmaterial, ks, haltungstyp,
                   simstatus, kommentar, createdat,  
                   geom)
                SELECT 
                  :haltnam, :baujahr, :schoben, :schunten,
                  CASE WHEN :hoehe > 20 THEN :hoehe/1000 ELSE :hoehe END,
                  CASE WHEN :breite > 20 THEN :breite/1000 ELSE :breite END,
                  :laenge, :aussendurchmesser,
                  :sohleoben, :sohleunten,
                  :teilgebiet, coalesce(:profilnam, 'Kreisquerschnitt'),
                  coalesce(:entwart, 'Regenwasser'), :strasse, :material, :profilauskleidung, :innenmaterial, coalesce(:ks, 1.5), coalesce(:haltungstyp, 'Haltung'),
                  coalesce(:simstatus, 'vorhanden'), :kommentar,
                  coalesce(:createdat, CURRENT_TIMESTAMP),
                  CASE WHEN :geom IS NULL
                    THEN
                      MakeLine(
                        coalesce(
                          (SELECT geop FROM schaechte WHERE schnam = :schoben LIMIT 1),
                          MakePoint(:xschob, :yschob, :epsg)
                        ),
                        coalesce(
                          (SELECT geop FROM schaechte WHERE schnam = :schunten LIMIT 1),
                          MakePoint(:xschun, :yschun, :epsg)
                        )
                      )
                    ELSE GeomFromWKB(:geom, :epsg)
                  END
                  ;"""

        elif tabnam == "haltungen_untersucht":
            parlis = [
                "haltnam",
                "bezugspunkt",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "breite",
                "laenge",
                "kommentar",
                "createdat",
                "baujahr",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "untersuchtag",
                "untersucher",
                "wetter",
                "strasse",
                "bewertungsart",
                "bewertungstag",
                "datenart",
                "max_ZD",
                "max_ZB",
                "max_ZS",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = f"""
                INSERT INTO haltungen_untersucht
                  (haltnam, bezugspunkt, schoben, schunten,
                   hoehe, breite, laenge,
                   kommentar, createdat, baujahr,  
                   geom, untersuchtag, untersucher, wetter, strasse, bewertungsart,
                   bewertungstag, datenart, max_ZD, max_ZB, max_ZS)
                SELECT 
                  :haltnam, :bezugspunkt, :schoben, :schunten, 
                  CASE WHEN :hoehe > 20 THEN :hoehe/1000 ELSE :hoehe END, 
                  CASE WHEN :breite > 20 THEN :breite/1000 ELSE :breite END,
                  :laenge, :kommentar, 
                  coalesce(:createdat, CURRENT_TIMESTAMP), :baujahr,
                  CASE WHEN :geom IS NULL
                    THEN
                      MakeLine(
                        coalesce(
                          MakePoint(:xschob, :yschob, :epsg),
                          suo.geop,
                          so.geop
                        ), 
                        coalesce(
                          MakePoint(:xschun, :yschun, :epsg),
                          suu.geop,
                          su.geop
                        )
                      )
                    ELSE GeomFromWKB(:geom, :epsg)
                  END,
                  :untersuchtag, :untersucher, :wetter, :strasse, :bewertungsart,
                  :bewertungstag, :datenart, coalesce(:max_ZD, 63), coalesce(:max_ZB, 63), coalesce(:max_ZS, 63)
                FROM
                  (SELECT :schoben AS schoben, :schunten AS schunten) AS ha
                  LEFT JOIN schaechte_untersucht AS suo ON suo.schnam = ha.schoben
                  LEFT JOIN schaechte_untersucht AS suu ON suu.schnam = ha.schunten
                  LEFT JOIN schaechte AS so ON so.schnam = ha.schoben
                  LEFT JOIN schaechte AS su ON su.schnam = ha.schunten;"""

        elif tabnam == "untersuchdat_haltung":
            parlis = [
                "untersuchhal",
                "untersuchrichtung",
                "schoben",
                "schunten",
                "id",
                "untersuchtag",
                "bandnr",
                "videozaehler",
                "inspektionslaenge",
                "station",
                "timecode",
                "video_offset",
                "kuerzel",
                "charakt1",
                "charakt2",
                "quantnr1",
                "quantnr2",
                "streckenschaden",
                "streckenschaden_lfdnr",
                "pos_von",
                "pos_bis",
                "foto_dateiname",
                "film_dateiname",
                "ordner_bild",
                "ordner_video",
                "ZD",
                "ZB",
                "ZS",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = f"""  
                INSERT INTO untersuchdat_haltung
                  (untersuchhal, untersuchrichtung, schoben, schunten, id, untersuchtag, bandnr, videozaehler, 
                    inspektionslaenge, station, timecode, video_offset, kuerzel, charakt1, charakt2, 
                    quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, foto_dateiname, 
                    film_dateiname, ordner_bild, ordner_video, ZD, ZB, ZS, createdat)
                SELECT
                  :untersuchhal, :untersuchrichtung, :schoben, :schunten, :id, :untersuchtag, :bandnr, :videozaehler, 
                  :inspektionslaenge , :station, :timecode, :video_offset, :kuerzel, :charakt1, :charakt2, 
                  :quantnr1, :quantnr2, :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, 
                  :foto_dateiname, :film_dateiname, :ordner_bild, :ordner_video,
                  coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63), coalesce(:createdat, CURRENT_TIMESTAMP)
                FROM
                schaechte AS schob,
                schaechte AS schun,
                haltungen AS haltung
                WHERE schob.schnam = :schoben AND schun.schnam = :schunten AND haltung.haltnam = :untersuchhal 
                UNION
                SELECT
                  :untersuchhal, :untersuchrichtung, :schoben, :schunten, :id, :untersuchtag, :bandnr, :videozaehler, 
                  :inspektionslaenge , :station, :timecode, :video_offset, :kuerzel, :charakt1, :charakt2, 
                  :quantnr1, :quantnr2, :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, 
                  :foto_dateiname, :film_dateiname, :ordner_bild, :ordner_video,
                  coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63), coalesce(:createdat, CURRENT_TIMESTAMP)
                FROM
                schaechte AS schob,
                schaechte AS schun,
                anschlussleitungen AS leitung
                WHERE schob.schnam = :schoben AND schun.schnam = :schunten AND leitung.leitnam = :untersuchhal;
            """

        elif tabnam == "anschlussleitungen":
            parlis = [
                "leitnam",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "laenge",
                "aussendurchmesser",
                "sohleoben",
                "sohleunten",
                "baujahr",
                "haltnam",
                "teilgebiet",
                "qzu",
                "profilnam",
                "entwart",
                "material",
                "profilauskleidung",
                "innenmaterial",
                "ks",
                "anschlusstyp",
                "simstatus",
                "kommentar",
                "createdat",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = """
                INSERT INTO anschlussleitungen
                  (leitnam, schoben, schunten,
                   hoehe, breite, laenge, aussendurchmesser,
                   sohleoben, sohleunten, baujahr, haltnam,
                   teilgebiet, qzu, profilnam, 
                   entwart, material, profilauskleidung, innenmaterial, ks, anschlusstyp, 
                   simstatus, kommentar, createdat,  
                   geom)
                VALUES( 
                  :leitnam, :schoben, :schunten, 
                  CASE WHEN :hoehe > 20 THEN :hoehe/1000 ELSE :hoehe END, 
                  CASE WHEN :breite > 20 THEN :breite/1000 ELSE :breite END,
                  :laenge, :aussendurchmesser,
                  :sohleoben, :sohleunten, :baujahr, :haltnam,
                  :teilgebiet, :qzu, coalesce(:profilnam, 'Kreisquerschnitt'), 
                  coalesce(:entwart, 'Regenwasser'), :material, :profilauskleidung, :innenmaterial, coalesce(:ks, 1.5), 
                  :anschlusstyp, coalesce(:simstatus, 'vorhanden'), :kommentar, 
                  coalesce(:createdat, CURRENT_TIMESTAMP), 
                  CASE WHEN :geom IS NULL
                      THEN MakeLine(
                          MakePoint(:xschob, :yschob, :epsg), 
                          MakePoint(:xschun, :yschun, :epsg))
                      ELSE GeomFromWKB(:geom, :epsg)
                  END
                );"""

            logger.debug(
                f"insert anschlussleitung - sql: {sql}\n" f"parameter: {param1}"
            )

        elif tabnam == "anschlussleitungen_untersucht":
            parlis = [
                "leitnam",
                "bezugspunkt",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "breite",
                "laenge",
                "kommentar",
                "createdat",
                "baujahr",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "untersuchtag",
                "untersucher",
                "wetter",
                "strasse",
                "bewertungsart",
                "bewertungstag",
                "datenart",
                "max_ZD",
                "max_ZB",
                "max_ZS",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = """
                INSERT INTO anschlussleitungen_untersucht
                  (leitnam, bezugspunkt, schoben, schunten,
                   hoehe, breite, laenge,
                   kommentar, createdat, baujahr,  
                   geom, untersuchtag, untersucher, wetter, strasse, bewertungsart, bewertungstag, datenart, max_ZD, max_ZB, max_ZS)
                SELECT 
                  :leitnam, :bezugspunkt, :schoben, :schunten, 
                  CASE WHEN :hoehe > 20 THEN :hoehe/1000 ELSE :hoehe END, 
                  CASE WHEN :breite > 20 THEN :breite/1000 ELSE :breite END,
                  :laenge, :kommentar, 
                  coalesce(:createdat, CURRENT_TIMESTAMP), :baujahr,
                  CASE WHEN :geom IS NULL
                    THEN
                      MakeLine(
                        coalesce(
                          MakePoint(:xschob, :yschob, :epsg),
                          suo.geop,
                          so.geop
                        ), 
                        coalesce(
                          MakePoint(:xschun, :yschun, :epsg),
                          suu.geop,
                          su.geop
                        )
                      )
                    ELSE GeomFromWKB(:geom, :epsg)
                  END, 
                  :untersuchtag, :untersucher, :wetter, :strasse, :bewertungsart,
                  :bewertungstag, :datenart, coalesce(:max_ZD, 63), coalesce(:max_ZB, 63), coalesce(:max_ZS, 63)
                FROM
                  (SELECT :schoben AS schoben, :schunten AS schunten) AS ha
                  LEFT JOIN schaechte_untersucht AS suo ON suo.schnam = ha.schoben
                  LEFT JOIN schaechte_untersucht AS suu ON suu.schnam = ha.schunten
                  LEFT JOIN schaechte AS so ON so.schnam = ha.schoben
                  LEFT JOIN schaechte AS su ON su.schnam = ha.schunten;"""

            logger.debug(
                f"insert anschlussleitung - sql: {sql}\n" f"parameter: {param1}"
            )

        elif tabnam == "untersuchdat_anschlussleitungen":
            parlis = [
                "untersuchleit",
                "untersuchrichtung",
                "schoben",
                "schunten",
                "id",
                "untersuchtag",
                "bandnr",
                "videozaehler",
                "inspektionslaenge",
                "station",
                "timecode",
                "video_offset",
                "kuerzel",
                "charakt1",
                "charakt2",
                "quantnr1",
                "quantnr2",
                "streckenschaden",
                "streckenschaden_lfdnr",
                "pos_von",
                "pos_bis",
                "foto_dateiname",
                "film_dateiname",
                "ordner_bild",
                "ordner_video",
                "ZD",
                "ZB",
                "ZS",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = f"""  
                INSERT INTO untersuchdat_anschlussleitungen
                  (untersuchleit, untersuchrichtung, schoben, schunten, id, untersuchtag, bandnr, videozaehler, 
                    inspektionslaenge, station, timecode, video_offset, kuerzel, charakt1, charakt2, 
                    quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, foto_dateiname, 
                    film_dateiname, ordner_bild, ordner_video, ZD, ZB, ZS, createdat)
                SELECT
                  :untersuchleit, :untersuchrichtung, :schoben, :schunten, :id, :untersuchtag, :bandnr, :videozaehler, 
                  :inspektionslaenge , :station, :timecode, :video_offset, :kuerzel, :charakt1, :charakt2, 
                  :quantnr1, :quantnr2, :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, 
                  :foto_dateiname, :film_dateiname, :ordner_bild, :ordner_video,
                  coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63), coalesce(:createdat, CURRENT_TIMESTAMP)
                FROM
                schaechte AS schob,
                schaechte AS schun,
                haltungen AS haltung
                WHERE schob.schnam = :schoben AND schun.schnam = :schunten AND haltung.haltnam = :untersuchhal 
                UNION
                SELECT
                  :untersuchleit, :untersuchrichtung, :schoben, :schunten, :id, :untersuchtag, :bandnr, :videozaehler, 
                  :inspektionslaenge , :station, :timecode, :video_offset, :kuerzel, :charakt1, :charakt2, 
                  :quantnr1, :quantnr2, :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, 
                  :foto_dateiname, :film_dateiname, :ordner_bild, :ordner_video,
                  coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63), coalesce(:createdat, CURRENT_TIMESTAMP)
                FROM
                schaechte AS schob,
                schaechte AS schun,
                anschlussleitungen AS leitung
                WHERE schob.schnam = :schoben AND schun.schnam = :schunten AND leitung.leitnam = :untersuchhal;
            """

        elif tabnam == "schaechte_untersucht":
            parlis = [
                "schnam",
                "durchm",
                "bezugspunkt",
                "id",
                "xsch",
                "ysch",
                "kommentar",
                "createdat",
                "baujahr",
                "untersuchtag",
                "untersucher",
                "wetter",
                "strasse",
                "bewertungsart",
                "bewertungstag",
                "datenart",
                "max_ZD",
                "max_ZB",
                "max_ZS",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = f"""
                INSERT INTO schaechte_untersucht
                  (schnam, durchm, bezugspunkt, id,
                   kommentar, createdat, baujahr,
                   geop, untersuchtag, untersucher, 
                   wetter, strasse, bewertungsart, 
                   bewertungstag, datenart, max_ZD, max_ZB, max_ZS)
                SELECT
                  :schnam,
                  CASE WHEN :durchm > 200 THEN :durchm/1000 ELSE :durchm END, :bezugspunkt, :id,
                  :kommentar, coalesce(:createdat, CURRENT_TIMESTAMP), :baujahr,
                  CASE WHEN :geop IS NULL
                    THEN
                      coalesce(
                        MakePoint(:xsch, :ysch, :epsg),
                        sch.geop
                      )
                    ELSE GeomFromWKB(:geop, :epsg)
                  END,
                  :untersuchtag, :untersucher, 
                  :wetter, :strasse, :bewertungsart, 
                  :bewertungstag, :datenart, 
                  coalesce(:max_ZD, 63), coalesce(:max_ZB, 63), coalesce(:max_ZS, 63)
                FROM
                  (SELECT :schnam AS schnam) AS val
                  LEFT JOIN schaechte AS sch ON val.schnam = sch.schnam;"""

        elif tabnam == "untersuchdat_schacht":
            parlis = [
                "untersuchsch",
                "id",
                "untersuchtag",
                "bandnr",
                "videozaehler",
                "timecode",
                "kuerzel",
                "charakt1",
                "charakt2",
                "quantnr1",
                "quantnr2",
                "streckenschaden",
                "streckenschaden_lfdnr",
                "pos_von",
                "pos_bis",
                "vertikale_lage",
                "inspektionslaenge",
                "bereich",
                "foto_dateiname",
                "ordner",
                "film_dateiname",
                "ordner_video",
                "ZD",
                "ZB",
                "ZS",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sql = """
                INSERT INTO untersuchdat_schacht
                  (untersuchsch, id, untersuchtag, bandnr, videozaehler, timecode, kuerzel, 
                    charakt1, charakt2, quantnr1, quantnr2, 
                    streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, 
                    vertikale_lage, inspektionslaenge, bereich, 
                    foto_dateiname, ordner, film_dateiname, ordner_video,
                    ZD, ZB, ZS, 
                    createdat)
                SELECT 
                  :untersuchsch, :id, :untersuchtag, :bandnr, :videozaehler, :timecode, :kuerzel, 
                    :charakt1, :charakt2, :quantnr1, :quantnr2, 
                    :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, 
                    :vertikale_lage, :inspektionslaenge, :bereich, 
                    :foto_dateiname, :ordner, :film_dateiname, :ordner_video,
                    coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63), 
                    coalesce(:createdat, CURRENT_TIMESTAMP)
                FROM
                    schaechte AS sch
                    WHERE sch.schnam = :untersuchsch;"""

        elif tabnam == 'tezg':
            parlis = ['flnam', 'regenschreiber', 'schnam', 'befgrad', 'neigung',
                       'createdat', 'haltnam', 'neigkl', 'schwerpunktlaufzeit', 'teilgebiet', 'abflussparameter',
                      'kommentar', 'geom', 'epsg']
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sql = """
                    INSERT INTO tezg
                      (flnam, regenschreiber, schnam, befgrad, neigung, 
                        createdat, haltnam, neigkl, schwerpunktlaufzeit, teilgebiet, abflussparameter,
                      kommentar, geom)
                    VALUES (
                    :flnam, :regenschreiber, :schnam, :befgrad, :neigung, 
                        coalesce(:createdat, CURRENT_TIMESTAMP), :haltnam, :neigkl, :schwerpunktlaufzeit, :teilgebiet, 
                        :abflussparameter, :kommentar,
                    GeomFromWKB(:geom, :epsg)
                );"""

        elif tabnam == "flaechen":
            parlis = ['flnam', 'haltnam', 'schnam', 'neigkl', 'neigung',
                      'teilgebiet', 'regenschreiber', 'abflussparameter',
                      'aufteilen', 'kommentar', 'createdat',
                      'geom', 'epsg']
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sql = """
                    INSERT INTO flaechen
                      (flnam, haltnam, schnam, neigkl, neigung, 
                      teilgebiet, regenschreiber, abflussparameter, 
                      aufteilen, kommentar, createdat, 
                      geom)
                    VALUES (
                    :flnam, :haltnam, :schnam, :neigkl, :neigung, 
                    :teilgebiet, :regenschreiber, :abflussparameter, 
                    :aufteilen, :kommentar, 
                    coalesce(:createdat, CURRENT_TIMESTAMP),
                    GeomFromWKB(:geom, :epsg)
                );"""

        elif tabnam == "teilgebiete":
            parlis = ["tgnam", "kommentar", "createdat", "geom", "epsg"]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sql = """
                INSERT INTO teilgebiete
                  (tgnam, kommentar, createdat, geom)
                VALUES (
                    :tgnam, :kommentar, 
                    coalesce(:createdat, CURRENT_TIMESTAMP),
                    GeomFromWKB(:geom, :epsg)
                );"""

        else:
            warnung(
                "dbfunc.DBConnection.insertdata:",
                f"Daten für diesen Layer {tabnam} können (noch) nicht "
                "über die QKan-Clipboardfunktion eingefügt werden",
            )
            return False

        if isinstance(parameters, dict):
            logger.debug(f'read_data.insertdata: einzelner Datensatz')
            result = self.sql(
                sql,
                stmt_category,
                parameters=parameters,
                many=False,
                mute_logger=mute_logger,
                ignore=ignore)
        else:
            logger.debug(f'read_data.insertdata: Tuple von Datensaetzen')
            result = self.sql(
                sql,
                stmt_category,
                parameters=parameters,
                many=True,
                mute_logger=mute_logger,
                ignore=ignore)

        return result

    def calctextpositions(self, data_hu, data_uh, tdist: float = 0.35, bdist: float = 0.10,
                          richtung: str = 'Anzeigen in Fließrichtung rechts der Haltung', epsg: int = 25832
                          ):
        """Berechnet in einer internen Tabelle die Textpositionen für die Haltungsschäden.
           Dabei werden zunächst vom Haltungsanfang (pa) sowie dem Haltungsende aus die Textpositionen
           mindestens im Abstand bdist gesetzt. Die endgültigen Textpositionen ergeben sich im Anfangs-
           und Endbereich jeweils aus diesen Werten, dazwischen aus deren Mittelwert.
        """

        # Die folgenden Felder enthalten die Textpositionen einer Haltung. Aus Effizienzgründen wird auf
        # 1000 dimensioniert. Falls das zuwenig ist, muss individuell neu dimensioniert werden.
        maxsj = 1000
        sj = maxsj
        pa = array('d', [0.0] * sj)  # Textposition berechnet mit Haltungsrichtung
        pe = array('d', [0.0] * sj)  # Textposition berechnet gegen Haltungsrichtung
        ma = array('B', [0] * sj)  # markiert den Anfangsbereich, in dem nur pa verwendet wird
        me = array('B', [0] * sj)  # markiert den Endbereich, in dem nur pe verwendet wird
        po = array('d', [0.0] * sj)  # Für ma: pa, für me: pe, sonst: (pa+pe)/2.

        abst = [0., 1.0, 1.5, 4.0]  # Abstände der Knickpunkte von der Haltung

        si = len(data_uh)  # Anzahl Untersuchungen
        if si == 0:
            logger.error(
                "Es konnten keine Schadenstexte erzeugt werden. Wahrscheinlich ist ein notwendiges Attribut noch leer",
            )
            return

        id = data_uh[0][1]
        ianf = 0
        for iend in range(si + 1):
            if iend < si and data_uh[iend][1] == id:
                # iend innerhalb eines Blocks der aktuellen id
                continue

            # Hinweis: Nach der Vergrößerung bleiben die Felder so, Zurücksetzen wäre zu umständlich ...
            if iend - ianf > si:
                si = iend - ianf
                pa = array('d', [0.0] * sj)  # Textposition berechnet mit Haltungsrichtung
                pe = array('d', [0.0] * sj)  # Textposition berechnet gegen Haltungsrichtung
                ma = array('B', [0] * sj)  # markiert den Anfangsbereich, in dem nur pa verwendet wird
                me = array('B', [0] * sj)  # markiert den Endbereich, in dem nur pe verwendet wird
                po = array('d', [0.0] * sj)  # Für ma: pa, für me: pe, sonst: (pa+pe)/2.

            pavor = 0
            mavor = 1  # Initialisierung mit 1 = True
            stvor = 0
            for i in range(ianf, iend):
                station = data_uh[i][2]
                if i == ianf:
                    dist = 0
                else:
                    dist = (abs(station - stvor) > 0.0001) * bdist + tdist
                pa[i - ianf] = max(station, pavor + dist)
                ma[i - ianf] = mavor * (pavor + dist > station - 0.0001)
                pavor = pa[i - ianf]
                mavor = ma[i - ianf]
                stvor = station

            xa, ya, xe, ye = data_hu[id]
            laenge = ((xe - xa) ** 2. + (ye - ya) ** 2.) ** 0.5

            pevor = laenge - (tdist + bdist)
            mevor = 1  # Initialisierung mit 1 = True
            stvor = 0
            for i in range(iend - 1, ianf - 1, -1):
                station = data_uh[i][2]
                if i == iend - 1:
                    dist = 0
                else:
                    dist = (abs(station - stvor) > 0.0001) * bdist + tdist
                pe[i - ianf] = min(station, pevor - dist)
                me[i - ianf] = mevor * (pevor - dist < station + 0.0001)
                pevor = pe[i - ianf]
                mevor = me[i - ianf]
                stvor = station

            for i in range(ianf, iend):
                if ma[i - ianf]:
                    po[i - ianf] = pa[i - ianf]
                elif me[i - ianf]:
                    po[i - ianf] = pe[i - ianf]
                else:
                    po[i - ianf] = (pa[i - ianf] + pe[i - ianf]) / 2.

            # Verbindungsobjekte für diese untersuchte Haltung schreiben

            if laenge > 0.045:
                # Koordinaten relativ zur Haltung
                xu = (xe - xa) / laenge
                yu = (ye - ya) / laenge
                if richtung == 'Anzeigen in Fließrichtung rechts der Haltung':
                    xv = yu
                    yv = -xu
                else:
                    xv = -yu
                    yv = xu

                for i in range(ianf, iend):
                    id = data_uh[i][0]
                    st0 = data_uh[i][2]
                    st1 = po[i - ianf]
                    x1 = xa + xu * st0 + xv * abst[0]
                    y1 = ya + yu * st0 + yv * abst[0]
                    x2 = xa + xu * st0 + xv * abst[1]
                    y2 = ya + yu * st0 + yv * abst[1]
                    x3 = xa + xu * st1 + xv * abst[2]
                    y3 = ya + yu * st1 + yv * abst[2]
                    x4 = xa + xu * st1 + xv * abst[3]
                    y4 = ya + yu * st1 + yv * abst[3]
                    geoobj = QgsGeometry.asWkb(
                        QgsGeometry.fromPolyline([QgsPoint(x1, y1), QgsPoint(x2, y2), QgsPoint(x3, y3), QgsPoint(x4, y4)]))
                    sql = "UPDATE untersuchdat_haltung SET geom = GeomFromWKB(?, ?) WHERE pk = ? AND geom IS NULL"

                    if not self.sql(sql, 'set_objekt', parameters=(geoobj, epsg, id,)):
                        logger.error(f"Fehler in {sql}")

            # Nächsten Block vorbereiten
            if iend < si:
                ianf = iend
                id = data_uh[iend][1]

        self.commit()

    def setschadenstexte_haltungen(self):
        """Textpositionen für Schadenstexte berechnen"""

        logger.debug("Schadenstexte Haltungen werden neu arrangiert ...")

        sql = """SELECT
            hu.pk AS id,
            st_x(pointn(hu.geom, 1))                AS xanf,
            st_y(pointn(hu.geom, 1))                AS yanf,
            st_x(pointn(hu.geom, -1))               AS xend,
            st_y(pointn(hu.geom, -1))               AS yend
            FROM haltungen_untersucht AS hu
            WHERE hu.haltnam IS NOT NULL AND
                  hu.untersuchtag IS NOT NULL AND
                  coalesce(hu.laenge, 0) > 0.05
            ORDER BY id"""

        if not self.sql(
            sql, "read haltungen_untersucht"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler beim Lesen der Stationen (1)")
        data = self.fetchall()

        data_hu = {}
        for vals in data:
            data_hu[vals[0]] = vals[1:]

        sql = """SELECT
            uh.pk, hu.pk AS id,
            CASE coalesce(uh.untersuchrichtung, hu.untersuchrichtung)
                WHEN 'gegen Fließrichtung' THEN GLength(hu.geom) - uh.station
                WHEN 'in Fließrichtung'    THEN uh.station
                                           ELSE uh.station END        AS station
            FROM untersuchdat_haltung AS uh
            JOIN haltungen_untersucht AS hu
            ON hu.haltnam = uh.untersuchhal AND
               hu.schoben = uh.schoben AND
               hu.schunten = uh.schunten AND
               hu.untersuchtag = uh.untersuchtag
            WHERE hu.haltnam IS NOT NULL AND
                  hu.untersuchtag IS NOT NULL AND
                  coalesce(laenge, 0) > 0.05 AND
                  uh.station IS NOT NULL AND
                  hu.geom IS NOT NULL AND
                  abs(uh.station) < 10000 AND
                  uh.untersuchrichtung IS NOT NULL
            GROUP BY hu.haltnam, hu.untersuchtag, round(station, 3), uh.kuerzel
            ORDER BY id, station;"""

        if not self.sql(
            sql, "read untersuchdat_haltungen"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler beim Lesen der Stationen (2)")

        data_uh = self.fetchall()

        richtung = 'Anzeigen in Fließrichtung rechts der Haltung'

        self.calctextpositions(data_hu, data_uh, 0.35, 0.10, richtung, self.epsg)

        # Nummerieren der Untersuchungen an der selben Haltung "haltungen_untersucht"

        sql = """
            UPDATE haltungen_untersucht
            SET id = unum.row_number
            FROM (
                SELECT
                    hu.pk AS pk, hu.haltnam, 
                    row_number() OVER (PARTITION BY hu.haltnam, hu.schoben, hu.schunten ORDER BY hu.untersuchtag DESC) AS row_number
                FROM haltungen_untersucht AS hu
                GROUP BY hu.haltnam, hu.schoben, hu.schunten, hu.untersuchtag
            ) AS unum
            WHERE haltungen_untersucht.pk = unum.pk
        """

        if not self.sql(
            sql, "num haltungen_untersucht"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler in num haltungen_untersucht")

        # Nummerieren der Untersuchungsdaten "untersuchdat_haltung"

        sql = """
            WITH num AS (
                SELECT
                    hu.haltnam, hu.schoben, hu.schunten, hu.untersuchtag, 
                    row_number() OVER (PARTITION BY hu.haltnam, hu.schoben, hu.schunten ORDER BY hu.untersuchtag DESC) AS row_number
                FROM haltungen_untersucht AS hu
                GROUP BY hu.haltnam, hu.schoben, hu.schunten, hu.untersuchtag
            )
            UPDATE untersuchdat_haltung
            SET id = uid.id
            FROM (
                SELECT uh.pk AS pk, num.row_number AS id
                FROM untersuchdat_haltung AS uh
                JOIN num
                ON	uh.untersuchhal = num.haltnam AND
                    uh.schoben = num.schoben AND
                    uh.schunten = num.schunten AND
                    uh.untersuchtag = num.untersuchtag
            ) AS uid
            WHERE untersuchdat_haltung.pk = uid.pk
        """

        if not self.sql(
            sql, "num untersuchdat_haltung"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler in num untersuchdat_haltung")

        self.commit()

        return True

    def executefile(self, filenam):
        """Liest eine Datei aus dem template-Verzeichnis und führt sie als SQL-Befehle aus"""
        try:
            with open(filenam) as fr:
                sqlfile = fr.read()
            self.cursl.executescript(sqlfile)
        except sqlite3.Error as e:
            fehlermeldung(
                "dbfunc.DBConnection.sql: SQL-Fehler beim Ausführen der SQL-Datei",
                "{e}\n{f}".format(e=repr(e), f=filenam),
            )
            self._disconnect()
            return False
        return True

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
        Diese wird mit dem Attribut self.actversion verglichen."""

        logger.debug("0 - actversion = {}".format(self.actversion))

        # ---------------------------------------------------------------------------------------------
        # Aktuelle Version abfragen

        if not self.sql(
            """
                SELECT value
                FROM info
                WHERE subject = 'version'
                """,
            "dbfunc.DBConnection.version (1)",
        ):
            return False

        data = self.cursl.fetchone()
        if data is not None:
            self.current_version = LooseVersion(data[0])
            logger.debug(
                "dbfunc.DBConnection.version: Aktuelle Version der qkan-Datenbank ist {}".format(
                    self.current_version
                )
            )
        else:
            logger.debug(
                "dbfunc.DBConnection.version: Keine Versionsnummer vorhanden. data = {}".format(
                    repr(data)
                )
            )
            if not self.sql(
                "INSERT INTO info (subject, value) Values ('version', '1.9.9')",
                "dbfunc.DBConnection.version (2)",
            ):
                return False

            self.current_version = LooseVersion("1.9.9")

        logger.debug(f"0 - versiondbQK = {self.current_version}")

        return self.actversion == self.current_version

    # Ändern der Attribute einer Tabelle

    def alter_table(
        self,
        tabnam: str,
        attributes_new: List[str],
        attributes_del: List[str] = None,
    ) -> bool:
        """Changes attribute columns in QKan tables except geom columns.

        :tabnam:                Name der Tabelle
        :attributes_new:        bestehende und neue Attribute, Syntax wie in Create-Befehl, ohne Primärschlüssel
                                und Geometrieobjekte.
                                Alle übrigen Attribute aus der alten Tabelle, die nicht entfernt werden sollen,
                                werden zufällig sortiert dahinter angeordnet übernommen.
        :attributes_del:        zu entfernende Attribute

        Ändert die Tabelle so, dass sie die Attribute aus attributesNew in der gegebenen
        Reihenfolge sowie die in der bestehenden Tabelle vom Benutzer hinzugefügten Attribute
        enthält. Nur falls attributesDel Attribute enthält, werden diese nicht übernommen.

        example:
        alter_table('flaechen',
            [   'flnam TEXT',
                'haltnam TEXT',
                'neu1 REAL                              -- Kommentar Schreibweise 1 ',
                'neu2 TEXT                              /* Kommentar Schreibweise 2 */',
                "simstatus TEXT DEFAULT 'vorhanden'     -- Kommentar Schreibweise 1 ",
                'teilgebiet TEXT                        /* Kommentar Schreibweise 2 */',
                "createdat TEXT DEFAULT CURRENT_TIMESTAMP"]
            ['entfernen1', 'entfernen2'])
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
        if not self.sql(
            f"PRAGMA table_info({tabnam})",
            "dbfunc.DBConnection.alter_table (1)",
        ):
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
        sql = """
                SELECT f_geometry_column, geometry_type, srid, 
                        coord_dimension, spatial_index_enabled
                FROM geometry_columns WHERE f_table_name = ?"""
        if not self.sql(
            sql,
            "dbfunc.DBConnection.alter_table (2)",
            parameters=(tabnam,),
        ):
            return False
        data = self.fetchall()
        attr_dict_geo = dict(
            [(el[0], [el[0], el[2], geo_type[el[1]], el[3]]) for el in data]
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
        attr_text_new = "\n,".join(attr_dict_new.values())
        logger.debug(f"dbfunc.DBConnection.alter_table - attr_text_new:{attr_text_new}")

        # 0. Foreign key constraint deaktivieren
        if not self.sql(
            "PRAGMA foreign_keys=OFF;",
            "dbfunc.DBConnection.alter_table (3)",
        ):
            return False

        # 1. Transaktion starten
        # if not self.sql(
        # "BEGIN TRANSACTION;",
        # "dbfunc.DBConnection.alter_table (4)",
        # transaction=False,
        # ):
        # return False

        # 2. Indizes und Trigger speichern
        # sql = """SELECT type, sql
        #         FROM sqlite_master
        #         WHERE tbl_name=? AND (type = 'trigger' OR type = 'index')"""
        # if not self.sql(
        #     sql,
        #     "dbfunc.DBConnection.alter_table (5)",
        #     parameters=(tabnam,),
        # ):
        #     return False
        # triggers = [el[1] for el in self.fetchall()]

        # 2.1. Temporäre Hilfstabelle erstellen
        sql = f"CREATE TABLE IF NOT EXISTS {tabnam}_t ({attr_text_new}\n);"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (6)"):
            logger.error(f'{sql =}')
            return False

        # 2.2. Geo-Attribute in Tabelle ergänzen
        for attr in attr_set_geo:
            gnam, epsg, geotype, nccords = attr_dict_geo[attr]
            if not self.sql(
                "SELECT AddGeometryColumn(?, ?, ?, ?, ?)",
                "dbfunc.DBConnection.alter_table (7)",
                parameters=(f'{tabnam}_t', gnam, epsg, geotype, nccords),
                ):
                return False

        # 3. Hilfstabelle entleeren
        if not self.sql(
            f"DELETE FROM {tabnam}_t",
            "dbfunc.DBConnection.alter_table (8)",
        ):
            return False

        # 4. Daten aus Originaltabelle übertragen, dabei nur gemeinsame Attribute berücksichtigen
        sql = f"""INSERT INTO {tabnam}_t ({', '.join(attr_set_both)}\n)
                SELECT {', '.join(attr_set_both)}
                FROM {tabnam};"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (9)"):
            return False

        # 5.1. Löschen der Geoobjektattribute
        for attr in attr_set_geo:
            if not self.sql(
                "SELECT DiscardGeometryColumn(?, ?)",
                "dbfunc.DBConnection.alter_table (10)",
                parameters=(tabnam, attr),
                ):
                return False

        # 5.2. Löschen der Tabelle
        sql = f"DROP TABLE {tabnam};"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (11)"):
            return False

        # 6.1 Geänderte Tabelle erstellen
        sql = f"""CREATE TABLE {tabnam} ({attr_text_new}\n);"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (12)"):
            return False

        # 6.2. Geo-Attribute in Tabelle ergänzen und Indizes erstellen
        for attr in attr_set_geo:
            gnam, epsg, geotype, nccords = attr_dict_geo[attr]
            if not self.sql(
                "SELECT AddGeometryColumn(?, ?, ?, ?, ?)",
                "dbfunc.DBConnection.alter_table (13)",
                parameters=(tabnam, gnam, epsg, geotype, nccords),
                ):
                return False
            if not self.sql(
                "SELECT CreateSpatialIndex(?, ?)",
                "dbfunc.DBConnection.alter_table (14)",
                parameters=(tabnam, attr),
                ):
                return False

        # 7. Daten aus Hilfstabelle übertragen, dabei nur gemeinsame Attribute berücksichtigen
        sql = f"""INSERT INTO {tabnam} ({', '.join(attr_set_both)}\n)
                SELECT {', '.join(attr_set_both)}
                FROM {tabnam}_t;"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (15)"):
            return False

        # 8.1. Löschen der Geoobjektattribute der Hilfstabelle
        for attr in attr_set_geo:
            if not self.sql(
                "SELECT DiscardGeometryColumn(?, ?)",
                "dbfunc.DBConnection.alter_table (16)",
                parameters=(f"{tabnam}_t", attr),
                ):
                return False

        # 9. Löschen der Hilfstabelle
        if not self.sql(
            f"DROP TABLE {tabnam}_t;",
            "dbfunc.DBConnection.alter_table (17)",
        ):
            return False

        # 9. Indizes und Trigger wiederherstellen
        # for sql in triggers:
        #     if not self.sql(sql, 'dbfunc.DBConnection.alter_table (18)'):
        #         return False

        # 10. Verify key constraints
        if not self.sql(
            "PRAGMA foreign_key_check;",
            "dbfunc.DBConnection.alter_table (19)",
        ):
            return False

        # 11. Transaktion abschließen
        self.commit()

        # 12. Foreign key constrain wieder aktivieren
        if not self.sql(
            "PRAGMA foreign_keys=ON;",
            "dbfunc.DBConnection.alter_table (20)",
        ):
            return False

        return True

    def upgrade_database(self) -> bool:
        """
        Ugprades the existing database to the current version.

        Each migration is run separately to ensure that we always end up at a
        consistent state, even if an upgrade fails.
        Once we are done, the user is told to reload the project as glitches
        may occur.
        """

        from .migrations import find_migrations

        # Database is already on the current version
        if self.check_version():
            return True

        logger.debug(
            "dbfunc.DBConnection.updateversion: versiondbQK = %s", self.current_version
        )

        progress_bar = QProgressBar(QKan.instance.iface.messageBar())
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)

        migrations = find_migrations(self.current_version)
        for i, migration in enumerate(migrations):
            if not migration.run(self):
                fehlermeldung("Fehler beim Ausführen des Datenbankupdates.")
                return False

            if not self.sql(
                "UPDATE info SET value = ? WHERE subject = 'version'",
                "dbfunc.DBConnection.version (aktuell)",
                parameters=(str(migration.version),),
            ):
                return False

            # Update progress bar
            progress_bar.setValue(100 // len(migrations) * (i + 1))

        self.commit()

        if self.reload:
            meldung(
                "Achtung! Benutzerhinweis!",
                "Die Datenbank wurde geändert. Bitte QGIS-Projekt nach dem Speichern neu laden...",
            )
            return False

        return True

    def get_from_mapper(
        self,
            key: str,
            mapper: dict,
            table: str,
            reftable: str,
            attr_name: str,
            attr_key: str,
            attr_bem: str = None,
            attr_short: str = None,
            default: str = None
    ) -> Union[bool, str, None]:
        """
    Liefert Langbezeichnung für einen key mit Hilfe eines mappers.
    Wenn der key im mapper nicht vorhanden ist, wird der key sowohl
    im mapper als auch der zugehörigen Datenbanktabelle ergänzt.

    :param key:                 gelesener Schlüsselwert
    :param mapper:              Schlüsselwerte mit zugeodneten Feldwerten
    :param table:               Name der Tabelle, in die der Feldwert eingetragen werden soll. Nur für Fehlermeldung benötigt!
    :param reftable:            Name der Referenztabelle
    :param attr_name:           Referenztabelle: Attributname der Langbezeichnung
    :param attr_key:            Referenztabelle: Attributname des Schlüsselwertes
    :param attr_bem:            Referenztabelle: Attributname des Kommentarwertes
    :param attr_short:          Referenztabelle: Attributname der Kurzbezeichnung
    :param default:             optional: Defaultwert, falls key None ist
        """

        if key in mapper:
            result = mapper[key]
        elif key is None:
            result = default
        else:
            result = key
            mapper[key] = key  # Ergänzung des Dict braucht nicht zurückgegeben werden

            if attr_short is None:
                sql = f"INSERT INTO {reftable} ({attr_name}, {attr_key}, {attr_bem}) " \
                      "VALUES (?, ?, ?)"
                params = (result, result, 'unbekannt')
            else:
                sql = f"INSERT INTO {reftable} ({attr_name}, {attr_key}, {attr_short}, {attr_bem}) " \
                      "VALUES (?, ?, ?, ?)"
                params = (result, result, result, 'unbekannt')
            if not self.sql(sql, f"{table}: nicht zugeordneter Wert für {reftable}", params):
                return False
        return result

    def consume_mapper(self, sql: str, subject: str, target: Dict[str, str]) -> None:
        if not self.sql(sql, subject):
            raise Exception(f"Failed to init {subject} mapper")
        for row in self.fetchall():
            target[row[0]] = row[1]

    def _adapt_reftable(self, table: str):
        """Ersetzt die importierten Bezeichnungen der Entwässerungsarten durch die QKan-Standards.
           Die entsprechenden Attribute in den Detailtabellen werden automatisch durch die definierten
           Trigger angepasst."""
        patterns = QKan.config.tools.clipboardattributes.qkan_patterns.get(table)
        sql = f"SELECT bezeichnung FROM {table}"
        if not self.sql(sql, 'Anpassen der Entwässerungsarten an den QKan-Standard (1)'):
            raise Exception(f'_adapt_reftable: Fehler beim Einlesen der Bezeichnungen aus {table}')
        for data in self.fetchall():
            bezeichnung = data[0]
            qkan_bez = None
            for qkan_patt in patterns.keys():
                # Schleife über alle QKan-Bezeichnungen
                for patt in patterns[qkan_patt]:
                    # Schleife über die Matchliste
                    if fnmatch(bezeichnung.lower(), patt):
                        # Match gefunden
                        qkan_bez = qkan_patt
                        if qkan_bez != bezeichnung:
                            sql = f'UPDATE {table} SET bezeichnung = :qkan_bez WHERE bezeichnung = :bezeichnung'
                            if not self.sql(
                                sql=sql,
                                stmt_category='Anpassen der Entwässerungsarten an den QKan-Standard (1)',
                                parameters={'qkan_bez': qkan_bez, 'bezeichnung': bezeichnung}
                            ):
                                raise Exception(f'_adapt_reftable: Fehler beim Wechsel der Bezeichnungen in {table}')
                            logger.debug(f'Tabelle entwaesserungsarten: Wechsel von {bezeichnung} zu {qkan_bez}')
                        break
                else:
                    continue            # nichts in der Matchliste gefunden, gehe zum nächsten QKan-Bezeichnungen
                break                   # eine QKan-Bezeichnung gefunden, gehe zum nächsten Datensatz
