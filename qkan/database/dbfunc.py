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
import sqlite3
from distutils.version import LooseVersion
from sqlite3 import Connection
from typing import Any, Iterable, List, Optional, Union, cast

from qgis.core import Qgis, QgsVectorLayer
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import spatialite_connect

from qkan import QKan

from .qkan_database import createdbtables, db_version
from .qkan_utils import fehlermeldung, warnung, meldung, get_database_QKan

__author__ = "Joerg Hoettges"
__date__ = "September 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"


logger = logging.getLogger("QKan.database.dbfunc")


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
        self.sqltime = datetime.datetime(2017, 1, 1, 1, 0, 0)
        self.sqltime = self.sqltime.now()
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

        if not tab_object:
            if not self.dbname:
                self.dbname, _ = get_database_QKan()
                if not self.dbname:
                    fehlermeldung("Fehler: Für den Export muss ein Projekt geladen sein!")
                    return None

            # Verbindung zur Datenbank herstellen oder die Datenbank neu erstellen
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
                        # if self.reload:
                        #     logger.debug("dbfunc: Datenbank muss neu geladen werden")
                        #     self.connected = False
                        #     self.consl.close()
                    else:
                        meldung(
                            f"Projekt muss aktualisiert werden. Die QKan-Version der Datenbank {self.current_version} stimmt nicht ",
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
                    shutil.copyfile(datenbank_qkan_template, self.dbname)

                    self.consl = spatialite_connect(database=self.dbname)
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
                    logger.debug(f"Datenbank ist nicht vorhanden: {self.dbname}")
                    fehlermeldung(
                        "Fehler in dbfunc.DBConnection:\n{}\n".format(err),
                        "Kopieren von: {}\nnach: {}\n nicht möglich".format(
                            QKan.template_dir, self.dbname
                        ),
                    )
                    self.connected = False  # Verbindungsstatus zur Kontrolle
                    self.consl = None
        elif tab_object is not None:
            tabconnect = tab_object.publicSource()
            t_db, t_tab, t_geo, t_sql = tuple(tabconnect.split())
            self.dbname = t_db.split("=")[1].strip("'")
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
                    self.consl = spatialite_connect(database=self.dbname)
                    self.cursl = self.consl.cursor()

                    self.epsg = self.getepsg()
                except:
                    fehlermeldung(
                        "Fehler",
                        "Fehler beim Öffnen der SpatialLite-Datenbank {}!\nAbbruch!".format(
                            self.dbname
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
        parameters = (),              # : Optional[Iterable, dict[str, str]]   "Iterable" is deprecated
        mute_logger: bool = False,
        transaction: bool = False,  # Unused, for compatibility only
        ignore: bool = False,      # ignore error and continue
    ) -> bool:
        try:
            self.cursl.execute(sql, parameters)

            if mute_logger:
                return True

            # Suppress log message for 2 seconds if category is identical to last query
            if self.sqltext == stmt_category:
                if (self.sqltime.now() - self.sqltime).seconds < 2:
                    self.sqlcount += 1
                    return True

            self.sqltext = stmt_category
            self.sqltime = self.sqltime.now()
            if self.sqlcount == 0:
                logger.debug(
                    "dbfunc.DBConnection.sql: {}\nsql: {}\nparameters: {}\n".format(stmt_category, sql, parameters)
                )
            else:
                logger.debug(
                    "dbfunc.DBConnection.sql (Nr. {}): {}\n{}\n{}\n".format(
                        self.sqlcount, stmt_category, sql, parameters
                    )
                )
            self.sqlcount = 0
            return True
        except sqlite3.Error as e:
            if ignore:
                warnung(
                    "dbfunc.DBConnection.sql: SQL-Fehler in {e}".format(e=stmt_category),
                    "{e}\n{s}\n{p}".format(e=repr(e), s=sql, p=parameters),
                )
            else:
                logger.error(f'dbfunc.sql: \nsql: {sql}\n'
                             f'parameters: {parameters}')
                fehlermeldung(
                    "dbfunc.DBConnection.sql: SQL-Fehler in {e}".format(e=stmt_category),
                    "{e}\n{s}\n{p}".format(e=repr(e), s=sql, p=parameters),
                )
                self.__del__()
            return False

    def insertdata(
            self,
            tabnam: str,
            stmt_category: str = "allgemein",
            mute_logger: bool = False,
            transaction: bool = False,  # Unused, for compatibility only
            ignore: bool = False,  # ignore error and continue
            **parameters: dict[str, str]) -> bool:
        """Fügt einen Datensatz mit Geo-Objekt hinzu"""

        if tabnam == 'schaechte':
            parlis = ['schnam', 'sohlhoehe', 'deckelhoehe', 'durchm', 'druckdicht',
                    'ueberstauflaeche', 'entwart', 'strasse', 'teilgebiet',
                    'knotentyp', 'auslasstyp', 'schachttyp', 'simstatus',
                    'material', 'kommentar', 'createdat', 'xsch', 'ysch', 'geom', 'geop', 'epsg']
            for el in parlis:
                if parameters.get(el, None) is None:
                    parameters[el] = None

            sql = """
                INSERT INTO schaechte (
                    schnam, sohlhoehe, deckelhoehe, 
                    durchm, 
                    druckdicht, 
                    ueberstauflaeche, 
                    entwart, strasse, teilgebiet, 
                    knotentyp, auslasstyp, schachttyp, 
                    simstatus, material,
                    kommentar, createdat, 
                    geop, geom)
               VALUES (
                    :schnam, :sohlhoehe, :deckelhoehe,
                    CASE WHEN :durchm > 200 THEN :durchm/1000 ELSE :durchm END, 
                    :druckdicht, coalesce(:ueberstauflaeche, 0), 
                    coalesce(:entwart, 'Regenwasser'), :strasse, :teilgebiet, 
                    :knotentyp, :auslasstyp, coalesce(:schachttyp, 'Schacht'), 
                    coalesce(:simstatus, 'vorhanden'), :material,
                    :kommentar, coalesce(:createdat, CURRENT_TIMESTAMP),
                    CASE WHEN :geop IS NULL
                        THEN MakePoint(:xsch, :ysch, :epsg)
                        ELSE GeomFromText(:geop, :epsg)
                    END,
                    CASE WHEN :geom IS NULL
                        THEN CastToMultiPolygon(MakePolygon(
                            MakeCircle(:xsch,:ysch,coalesce(:durchm, 1.0)/2.0, :epsg)))
                        ELSE GeomFromText(:geom, :epsg)
                    END);"""

        elif tabnam == 'haltungen':
            parlis = ['haltnam', 'schoben', 'schunten', 'hoehe', 'breite',
                      'laenge', 'sohleoben', 'sohleunten', 'teilgebiet', 'profilnam',
                      'entwart', 'strasse', 'material', 'ks', 'haltungstyp', 'simstatus', 'kommentar',
                      'createdat', 'xschob', 'yschob', 'xschun', 'yschun', 'geom', 'epsg']
            for el in parlis:
                if parameters.get(el, None) is None:
                    parameters[el] = None
            sql = """
                INSERT INTO haltungen
                  (haltnam, schoben, schunten,
                   hoehe, breite, laenge,
                   sohleoben, sohleunten, 
                   teilgebiet, profilnam, 
                   entwart, strasse, material, ks,
                   simstatus, kommentar, createdat,  
                   geom)
                SELECT 
                  :haltnam, :schoben, :schunten,
                  CASE WHEN :hoehe > 20 THEN :hoehe/1000 ELSE :hoehe END,
                  CASE WHEN :breite > 20 THEN :breite/1000 ELSE :breite END,
                  :laenge,
                  :sohleoben, :sohleunten,
                  :teilgebiet, coalesce(:profilnam, 'Kreisquerschnitt'),
                  coalesce(:entwart, 'Regenwasser'), :strasse, :material, coalesce(:ks, 1.5),
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
                    ELSE GeomFromText(:geom, :epsg)
                  END
                  ;"""

        elif tabnam == 'haltungen_untersucht':
            parlis = ['haltnam', 'schoben', 'schunten', 'hoehe', 'breite', 'laenge',
                      'kommentar', 'createdat', 'baujahr', 'xschob', 'yschob',
                      'xschun', 'yschun', 'untersuchtag', 'untersucher', 'wetter',
                      'strasse', 'bewertungsart', 'bewertungstag', 'datenart',
                      'max_ZD', 'max_ZB', 'max_ZS', 'geom', 'epsg']
            for el in parlis:
                if parameters.get(el, None) is None:
                    parameters[el] = None
            sql = f"""
                INSERT INTO haltungen_untersucht
                  (haltnam, schoben, schunten,
                   hoehe, breite, laenge,
                   kommentar, createdat, baujahr,  
                   geom, untersuchtag, untersucher, wetter, strasse, bewertungsart, bewertungstag, datenart, max_ZD, max_ZB, max_ZS)
                SELECT 
                  :haltnam, :schoben, :schunten, 
                  CASE WHEN :hoehe > 20 THEN :hoehe/1000 ELSE :hoehe END, 
                  CASE WHEN :breite > 20 THEN :breite/1000 ELSE :breite END,
                  :laenge, :kommentar, 
                  coalesce(:createdat, CURRENT_TIMESTAMP), :baujahr,
                  MakeLine(
                    coalesce(
                      MakePoint(:xschob, :yschob, :epsg),
                      schob.geop
                    ), 
                    coalesce(
                      MakePoint(:xschun, :yschun, :epsg),
                      schun.geop
                    )
                  ), :untersuchtag, :untersucher, :wetter, :strasse, :bewertungsart, :bewertungstag, :datenart, coalesce(:max_ZD, 63), coalesce(:max_ZB, 63), coalesce(:max_ZS, 63)
                FROM
                  schaechte AS schob,
                  schaechte AS schun
                WHERE schob.schnam = :schoben AND schun.schnam = :schunten;"""

        elif tabnam == 'untersuchdat_haltung':
            parlis = ['untersuchhal', 'untersuchrichtung', 'schoben', 'schunten', 'id',
                      'videozaehler', 'inspektionslaenge', 'station', 'timecode',
                      'video_offset', 'kuerzel', 'charakt1', 'charakt2', 'quantnr1',
                      'quantnr2', 'streckenschaden', 'streckenschaden_lfdnr',
                      'pos_von', 'pos_bis', 'foto_dateiname', 'film_dateiname',
                      'ordner_bild', 'ordner_video', 'richtung',
                      'ZD', 'ZB', 'ZS', 'createdat', 'geom', 'epsg']
            for el in parlis:
                if parameters.get(el, None) is None:
                    parameters[el] = None
            sql = f"""  
                INSERT INTO untersuchdat_haltung
                  (untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler, inspektionslaenge, station, timecode, video_offset, kuerzel, 
                    charakt1, charakt2, quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, foto_dateiname, film_dateiname, 
                    ordner_bild, ordner_video, richtung, ZD, ZB, ZS, createdat, geom)
                SELECT
                  :untersuchhal, :untersuchrichtung, :schoben, :schunten, 
                    :id, :videozaehler, :inspektionslaenge , :station, :timecode, :video_offset, :kuerzel, 
                    :charakt1, :charakt2, :quantnr1, :quantnr2, :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, :foto_dateiname, :film_dateiname,
                    :ordner_bild, :ordner_video, :richtung, coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63),
                    coalesce(:createdat, CURRENT_TIMESTAMP),
                    CASE
                    WHEN :untersuchrichtung = 'in Fließrichtung' 
                        AND ((ST_Y(schun.geop)-ST_Y(schob.geop) >= 0) <> (:schoben = haltung.schoben AND :schunten = haltung.schunten)) THEN 
                        MakeLine(coalesce(Line_Interpolate_Point(haltung.geom, min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schob.geop), 
                                 coalesce(Line_Interpolate_Point(OffsetCurve(haltung.geom, 2.0), min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schun.geop)                       -- Station in Haltungsrichtung, nach links
                        )
                    WHEN :untersuchrichtung = 'in Fließrichtung' 
                        AND ((ST_Y(schun.geop)-ST_Y(schob.geop) >= 0) = (:schoben = haltung.schoben AND :schunten = haltung.schunten)) THEN 
                        MakeLine(
                            coalesce(Line_Interpolate_Point(haltung.geom, min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schob.geop), 
                            coalesce(Line_Interpolate_Point(OffsetCurve(haltung.geom, -2.0), 1.0 - min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schun.geop)                     -- Station in Haltungsrichtung, nach rechts
                        )
                    WHEN :untersuchrichtung = 'gegen Fließrichtung' 
                        AND ((ST_Y(schob.geop)-ST_Y(schun.geop)  < 0) = (:richtung = 'untersuchungsrichtung')) THEN 
                        MakeLine(
                            coalesce(Line_Interpolate_Point(haltung.geom, 1.0 - min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schob.geop), 
                            coalesce(Line_Interpolate_Point(OffsetCurve(haltung.geom, 2.0), 1.0 - min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schun.geop)                      -- Station gegen Haltungsrichtung, bezogen auf Haltungsobjekt nach links
                        )
                    WHEN :untersuchrichtung = 'gegen Fließrichtung' 
                        AND ((ST_Y(schob.geop)-ST_Y(schun.geop) >= 0) = (:richtung = 'untersuchungsrichtung')) THEN 
                        MakeLine(
                            coalesce(Line_Interpolate_Point(haltung.geom, 1.0 - min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schob.geop), 
                            coalesce(Line_Interpolate_Point(OffsetCurve(haltung.geom, -2.0), min(:station/COALESCE(:inspektionslaenge, haltung.laenge, ST_Length(haltung.geom)), 1.0)),schun.geop)                           -- Station gegen Haltungsrichtung, bezogen auf Haltungsobjekt nach rechts
                        )
                    ELSE NULL
                    END
                FROM
                schaechte AS schob,
                schaechte AS schun,
                haltungen AS haltung
                WHERE schob.schnam = :schoben AND schun.schnam = :schunten AND haltung.haltnam = :untersuchhal 
                UNION
                SELECT
                  :untersuchhal, :untersuchrichtung, :schoben, :schunten, 
                    :id, :videozaehler, :inspektionslaenge , :station, :timecode, :video_offset, :kuerzel, 
                    :charakt1, :charakt2, :quantnr1, :quantnr2, :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, :foto_dateiname, :film_dateiname,
                    :ordner_bild, :ordner_video, :richtung, coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63),
                    coalesce(:createdat, CURRENT_TIMESTAMP),
                    CASE
                    WHEN :untersuchrichtung = 'in Fließrichtung' 
                        AND ((ST_Y(schun.geop)-ST_Y(schob.geop) >= 0) <> (:schoben = leitung.schoben AND :schunten = leitung.schunten)) THEN 
                        MakeLine(coalesce(Line_Interpolate_Point(leitung.geom, min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schob.geop), 
                                 coalesce(Line_Interpolate_Point(OffsetCurve(leitung.geom, 2.0), min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schun.geop)                       -- Station in Anschlussleitungsrichtung, nach links
                        )
                    WHEN :untersuchrichtung = 'in Fließrichtung' 
                        AND ((ST_Y(schun.geop)-ST_Y(schob.geop) >= 0) = (:schoben = leitung.schoben AND :schunten = leitung.schunten)) THEN 
                        MakeLine(
                            coalesce(Line_Interpolate_Point(leitung.geom, min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schob.geop), 
                            coalesce(Line_Interpolate_Point(OffsetCurve(leitung.geom, -2.0), 1.0 - min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schun.geop)                     -- Station in Anschlussleitungsrichtung, nach rechts
                        )
                    WHEN :untersuchrichtung = 'gegen Fließrichtung' 
                        AND ((ST_Y(schob.geop)-ST_Y(schun.geop)  < 0) = (:richtung = 'untersuchungsrichtung')) THEN 
                        MakeLine(
                            coalesce(Line_Interpolate_Point(leitung.geom, 1.0 - min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schob.geop), 
                            coalesce(Line_Interpolate_Point(OffsetCurve(leitung.geom, 2.0), 1.0 - min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schun.geop)                      -- Station gegen Anschlussleitungsrichtung, bezogen auf Geo-Objekt nach links
                        )
                    WHEN :untersuchrichtung = 'gegen Fließrichtung' 
                        AND ((ST_Y(schob.geop)-ST_Y(schun.geop) >= 0) = (:richtung = 'untersuchungsrichtung')) THEN 
                        MakeLine(
                            coalesce(Line_Interpolate_Point(leitung.geom, 1.0 - min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schob.geop), 
                            coalesce(Line_Interpolate_Point(OffsetCurve(leitung.geom, -2.0), min(:station/COALESCE(:inspektionslaenge, leitung.laenge, ST_Length(leitung.geom)), 1)),schun.geop)                           -- Station gegen Anschlussleitungsrichtung, bezogen auf Geo-Objekt nach rechts
                        )
                    ELSE NULL
                    END
                FROM
                schaechte AS schob,
                schaechte AS schun,
                anschlussleitungen AS leitung
                WHERE schob.schnam = :schoben AND schun.schnam = :schunten AND leitung.leitnam = :untersuchhal;
            """

        elif tabnam == 'anschlussleitungen':
            parlis = ['leitnam', 'schoben', 'schunten', 'hoehe', 'breite', 'laenge',
                      'sohleoben', 'sohleunten',
                      'teilgebiet', 'qzu', 'profilnam', 'entwart', 'material', 'ks',
                      'simstatus', 'kommentar', 'createdat',
                      'xschob', 'yschob', 'xschun', 'yschun', 'geom', 'epsg']
            for el in parlis:
                if parameters.get(el, None) is None:
                    parameters[el] = None
            sql = """
                INSERT INTO anschlussleitungen
                  (leitnam, schoben, schunten,
                   hoehe, breite, laenge,
                   sohleoben, sohleunten,
                   teilgebiet, qzu, profilnam, 
                   entwart, material, ks,
                   simstatus, kommentar, createdat,  
                   geom)
                VALUES( 
                  :leitnam, :schoben, :schunten, 
                  CASE WHEN :hoehe > 20 THEN :hoehe/1000 ELSE :hoehe END, 
                  CASE WHEN :breite > 20 THEN :breite/1000 ELSE :breite END,
                  :laenge, 
                  :sohleoben, :sohleunten, 
                  :teilgebiet, :qzu, coalesce(:profilnam, 'Kreisquerschnitt'), 
                  coalesce(:entwart, 'Regenwasser'), :material, coalesce(:ks, 1.5), 
                  coalesce(:simstatus, 'vorhanden'), :kommentar, 
                  coalesce(:createdat, CURRENT_TIMESTAMP), 
                  CASE WHEN :geom IS NULL
                      THEN MakeLine(
                          MakePoint(:xschob, :yschob, :epsg), 
                          MakePoint(:xschun, :yschun, :epsg))
                      ELSE GeomFromText(:geom, :epsg)
                  END
                );"""

        elif tabnam == 'schaechte_untersucht':
            parlis = ['schnam', 'durchm', 'kommentar', 'createdat', 'baujahr',
                      'untersuchtag', 'untersucher', 'wetter', 'strasse',
                      'bewertungsart', 'bewertungstag', 'datenart', 'max_ZD',
                      'max_ZB', 'max_ZS']
            for el in parlis:
                if parameters.get(el, None) is None:
                    parameters[el] = None
            sql = f"""
                INSERT INTO schaechte_untersucht
                  (schnam, durchm,  
                   kommentar, createdat, baujahr,
                   geop, untersuchtag, untersucher, 
                   wetter, strasse, bewertungsart, 
                   bewertungstag, datenart, max_ZD, max_ZB, max_ZS)
                SELECT
                  :schnam,
                  CASE WHEN :durchm > 200 THEN :durchm/1000 ELSE :durchm END, 
                  :kommentar, coalesce(:createdat, CURRENT_TIMESTAMP), :baujahr,
                  sch.geop,
                  :untersuchtag, :untersucher, 
                  :wetter, :strasse, :bewertungsart, 
                  :bewertungstag, :datenart, 
                  coalesce(:max_ZD, 63), coalesce(:max_ZB, 63), coalesce(:max_ZS, 63)
                FROM
                  schaechte AS sch
                  WHERE sch.schnam = :schnam;"""

        elif tabnam == 'untersuchdat_schacht':
            parlis = ['untersuchsch', 'id', 'videozaehler', 'timecode', 'kuerzel',
                      'charakt1', 'charakt2', 'quantnr1', 'quantnr2', 'streckenschaden',
                      'streckenschaden_lfdnr', 'pos_von', 'pos_bis', 'vertikale_lage',
                      'inspektionslaenge', 'bereich', 'foto_dateiname', 'ordner',
                      'ZD', 'ZB', 'ZS', 'createdat']
            for el in parlis:
                if parameters.get(el, None) is None:
                    parameters[el] = None
            sql = """
                INSERT INTO untersuchdat_schacht
                  (untersuchsch, id, videozaehler, timecode, kuerzel, 
                    charakt1, charakt2, quantnr1, quantnr2, 
                    streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, 
                    vertikale_lage, inspektionslaenge, bereich, 
                    foto_dateiname, ordner, 
                    ZD, ZB, ZS, 
                    createdat, geop)
                SELECT 
                  :untersuchsch, :id, :videozaehler, :timecode, :kuerzel, 
                    :charakt1, :charakt2, :quantnr1, :quantnr2, 
                    :streckenschaden, :streckenschaden_lfdnr, :pos_von, :pos_bis, 
                    :vertikale_lage, :inspektionslaenge, :bereich, 
                    :foto_dateiname, :ordner, 
                    coalesce(:ZD, 63), coalesce(:ZB, 63), coalesce(:ZS, 63), 
                    coalesce(:createdat, CURRENT_TIMESTAMP), sch.geop
                FROM
                    schaechte AS sch
                    WHERE sch.schnam = :untersuchsch;"""

        elif tabnam == 'tezg':
            parlis = ['flnam', 'regenschreiber', 'schnam', 'befgrad', 'neigung',
                       'createdat', 'haltnam', 'neigkl', 'schwerpunktlaufzeit', 'teilgebiet', 'abflussparameter',
                      'kommentar']
            for el in parlis:
                if not parameters.get(el, None):
                    parameters[el] = None
            sql = """
                    INSERT INTO tezg
                      (flnam, regenschreiber, schnam, befgrad, neigung, 
                        createdat, haltnam, neigkl, schwerpunktlaufzeit, teilgebiet, abflussparameter,
                      kommentar)
                    VALUES (
                    :flnam, :regenschreiber, :schnam, :befgrad, :neigung, 
                        coalesce(:createdat, CURRENT_TIMESTAMP), :haltnam, :neigkl, :schwerpunktlaufzeit, :teilgebiet, 
                        :abflussparameter, :kommentar
                    );"""

        result = self.sql(sql, stmt_category, parameters, mute_logger,
                          transaction, ignore)

        return result

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
            self.__del__()
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
        :attributes_new:        bestehende und neue Attribute, Syntax wie in Create-Befehl, ohne Primärschlüssel.
                                Alle übrigen Attribute aus der alten Tabelle, die nicht entfernt werden sollen,
                                werden zufällig sortiert dahinter angeordnet übernommen.
        :attributes_del:        zu entfernende Attribute

        Ändert die Tabelle so, dass sie die Attribute aus attributesNew in der gegebenen
        Reihenfolge sowie die in der bestehenden Tabelle vom Benutzer hinzugefügten Attribute
        enthält. Nur falls attributesDel Attribute enthält, werden diese nicht übernommen.

        example:
        alter_table('flaechen',
            [   'flnam TEXT                       -- eindeutiger Flächenname',
                'haltnam TEXT',
                'entfernen1 REAL              -- nur so...',
                'entfernen2 TEXT              /* nur so...*/',
                "simstatus TEXT DEFAULT 'vorhanden'",
                'teilgebiet TEXT',
                "createdat TEXT DEFAULT (datetime('now'))"]
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
            transaction=False,
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
            transaction=False,
        ):
            return False
        data = self.fetchall()
        attr_dict_geo = dict(
            [
                (el[0], [el[0], el[2], geo_type[el[1]], el[3]])
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
        attr_text_new = "\n,".join(attr_dict_new.values())
        logger.debug(f"dbfunc.DBConnection.alter_table - attr_text_new:{attr_text_new}")

        # 0. Foreign key constraint deaktivieren
        if not self.sql(
            "PRAGMA foreign_keys=OFF;",
            "dbfunc.DBConnection.alter_table (3)",
            transaction=False,
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
        #     transaction=False,
        # ):
        #     return False
        # triggers = [el[1] for el in self.fetchall()]

        # 2.1. Temporäre Hilfstabelle erstellen
        sql = f"CREATE TABLE IF NOT EXISTS {tabnam}_t ({attr_text_new});"
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (6)", transaction=False):
            return False

        # 2.2. Geo-Attribute in Tabelle ergänzen
        for attr in attr_set_geo:
            gnam, epsg, geotype, nccords = attr_dict_geo[attr]
            if not self.sql(
                "SELECT AddGeometryColumn(?, ?, ?, ?, ?)",
                "dbfunc.DBConnection.alter_table (7)",
                parameters=(f'{tabnam}_t', gnam, epsg, geotype, nccords),
                transaction=False,
            ):
                return False

        # 3. Hilfstabelle entleeren
        if not self.sql(
            f"DELETE FROM {tabnam}_t",
            "dbfunc.DBConnection.alter_table (8)",
            transaction=False,
        ):
            return False

        # 4. Daten aus Originaltabelle übertragen, dabei nur gemeinsame Attribute berücksichtigen
        sql = f"""INSERT INTO {tabnam}_t ({', '.join(attr_set_both)})
                SELECT {', '.join(attr_set_both)}
                FROM {tabnam};"""
        if not self.sql(sql, "dbfunc.DBConnection.alter_table (9)", transaction=False):
            return False

        # 5.1. Löschen der Geoobjektattribute
        for attr in attr_set_geo:
            if not self.sql(
                "SELECT DiscardGeometryColumn(?, ?)",
                "dbfunc.DBConnection.alter_table (10)",
                parameters=(tabnam, attr),
                transaction=False,
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
            gnam, epsg, geotype, nccords = attr_dict_geo[attr]
            if not self.sql(
                "SELECT AddGeometryColumn(?, ?, ?, ?, ?)",
                "dbfunc.DBConnection.alter_table (13)",
                parameters=(tabnam, gnam, epsg, geotype, nccords),
                transaction=False,
            ):
                return False
            if not self.sql(
                "SELECT CreateSpatialIndex(?, ?)",
                "dbfunc.DBConnection.alter_table (14)",
                parameters=(tabnam, attr),
                transaction=False,
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
            if not self.sql(
                "SELECT DiscardGeometryColumn(?, ?)",
                "dbfunc.DBConnection.alter_table (16)",
                parameters=(f"{tabnam}_t", attr),
                transaction=False,
            ):
                return False

        # 9. Löschen der Hilfstabelle
        if not self.sql(
            f"DROP TABLE {tabnam}_t;",
            "dbfunc.DBConnection.alter_table (17)",
            transaction=False,
        ):
            return False

        # 9. Indizes und Trigger wiederherstellen
        # for sql in triggers:
        #     if not self.sql(sql, 'dbfunc.DBConnection.alter_table (18)', transaction=False):
        #         return False

        # 10. Verify key constraints
        if not self.sql(
            "PRAGMA foreign_key_check;",
            "dbfunc.DBConnection.alter_table (19)",
            transaction=False,
        ):
            return False

        # 11. Transaktion abschließen
        self.commit()

        # 12. Foreign key constrain wieder aktivieren
        if not self.sql(
            "PRAGMA foreign_keys=ON;",
            "dbfunc.DBConnection.alter_table (20)",
            transaction=False,
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


