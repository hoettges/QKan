# -*- coding: utf-8 -*-

"""

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

"""

__author__ = "Joerg Hoettges"
__date__ = "August 2019"
__copyright__ = "(C) 2016, Joerg Hoettges"
__dbVersion__ = "3.3.8"  # Version der QKan-Datenbank
__qgsVersion__ = "3.3.8"  # Version des Projektes und der Projektdatei. Kann höher als die der QKan-Datenbank sein


import logging
import os
import traceback
from sqlite3.dbapi2 import Connection, Cursor

from qgis.core import Qgis, QgsProject
from qgis.PyQt import Qt
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import spatialite_connect, pluginDirectory

from .qkan_utils import fehlermeldung, fortschritt, meldung
from qkan import QKan

logger = logging.getLogger("QKan.database.qkan_database")


def db_version() -> str:
    """Returns actual version of the QKan database"""
    return __dbVersion__


def qgs_version() -> str:
    """Returns actual project version"""
    return __qgsVersion__


def qgs_actual_version(update: bool = True, warning: bool = False) -> bool:
    """Prüft die Version des aktiven Projektes und aktualisiert die Layer gegebenenfalls

    :param warning: Aktiviert Warnung in QGIS-Meldungsleiste

    Prüft im Vergleich zur Version der QKan-Datenbank, ob das geladene Projekt die gleiche oder höhere
    Versionsnummer aufweist.
    """

    iface = QKan.instance.iface

    layers = iface.layerTreeCanvasBridge().rootGroup().findLayers()
    if len(layers) == 0 and warning:
        logger.error("qkan_database.qgs_actual_version: Keine Layer vorhanden...")
        meldung("Fehler: ", "Kein QKan-Projekt geladen!")
        return False

    # noinspection PyArgumentList
    act_qgs_version = QgsProject.instance().title().replace("QKan Version ", "")
    if act_qgs_version == "":
        if len(layers) == 0:
            meldung("Benutzerfehler: ", "Es ist kein Projekt geladen")
        else:
            act_qgs_version = "2.5.3"  # davor wurde die Version der Projektdatei noch nicht verwaltet.
    cur_qgs_version = qgs_version()
    try:
        act_qgs_version_lis = [
            int(el.replace("a", "").replace("b", "").replace("c", ""))
            for el in act_qgs_version.split(".")
        ]
    except BaseException as err:
        logger.error(
            "\nqkan_database.qgs_actual_version: {}\nVersionsstring fehlerhaft: {}".format(
                err, act_qgs_version
            )
        )
        act_qgs_version = (
            "2.5.3"  # davor wurde die Version der Projektdatei noch nicht verwaltet.
        )
        act_qgs_version_lis = [
            int(el.replace("a", "").replace("b", "").replace("c", ""))
            for el in act_qgs_version.split(".")
        ]

    cur_qgs_version_lis = [
        int(el.replace("a", "").replace("b", "").replace("c", ""))
        for el in cur_qgs_version.split(".")
    ]

    logger.debug("act_qgs_version: {}".format(act_qgs_version))
    logger.debug("cur_qgs_version: {}".format(cur_qgs_version))

    # Änderungen an den Layern werden nur in layersadapt vorgenommen.

    return True


# Erzeuge QKan-Tabellen


def createdbtables(
    consl: Connection, cursl: Cursor, version: str = __dbVersion__, epsg: int = 25832
) -> bool:
    """Erstellt fuer eine neue QKan-Datenbank die benötigten Tabellen.

    :param consl: Datenbankobjekt der SpatiaLite-QKan-Datenbank
    :param cursl: Zugriffsobjekt der SpatiaLite-QKan-Datenbank
    :param version: Database version
    :param epsg: EPSG ID

    :returns: Testergebnis: True = alles o.k.
    """

    # Notizen ----------------------------------------------------------------

    sqls = [""" CREATE TABLE notizen (
            pk INTEGER PRIMARY KEY,
            notiz TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        """SELECT AddGeometryColumn('notizen','geom',{},'POINT',2);""".format(epsg),
        """SELECT CreateSpatialIndex('notizen','geom')""",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "Notizen" konnte nicht erstellt werden',
            )
            consl.close()
            return False

    consl.commit()

    # Haltungen ----------------------------------------------------------------

    sqls = [
        """ CREATE TABLE haltungen (
            pk INTEGER PRIMARY KEY,
            haltnam TEXT,
            schoben TEXT,                                   -- join schaechte.schnam
            schunten TEXT,                                  -- join schaechte.schnam
            hoehe REAL,                                     -- Profilhoehe (m)
            breite REAL,                                    -- Profilbreite (m)
            laenge REAL,                                    -- abweichende Haltungslänge (m)
            aussendurchmesser REAL,
            sohleoben REAL,                                 -- abweichende Sohlhöhe oben (m)
            sohleunten REAL,                                -- abweichende Sohlhöhe unten (m)
            teilgebiet TEXT,                                -- join teilgebiet.tgnam
            strasse TEXT,                                   -- für ISYBAU benötigt
            profilnam TEXT DEFAULT 'Kreisquerschnitt',      -- join profile.profilnam
            entwart TEXT DEFAULT 'Regenwasser',             -- join entwaesserungsarten.bezeichnung
            material TEXT,
            profilauskleidung TEXT,
            innenmaterial TEXT,
            ks REAL DEFAULT 1.5,                            -- abs. Rauheit (Prandtl-Colebrook)
            haltungstyp TEXT DEFAULT 'Haltung',             -- join haltungstypen.bezeichnung
            simstatus TEXT DEFAULT 'vorhanden',             -- join simulationsstatus.bezeichnung
            transport INTEGER DEFAULT 0,                    -- Transporthaltung?
            druckdicht INTEGER DEFAULT 0,                   -- Druckleitung?
            xschob REAL,
            yschob REAL,
            xschun REAL,
            yschun REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('haltungen','geom',{},'LINESTRING',2)".format(epsg),
        "SELECT CreateSpatialIndex('haltungen','geom')",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "Haltungen" konnte nicht erstellt werden',
            )
            consl.close()
            return False

    with open(os.path.join(pluginDirectory("qkan"), 'database/triggers', 'haltungen.sql'), 'r') as sql_file:
        try:
            cursl.executescript(sql_file.read())
        except BaseException as err:
            logger.debug(f"Fehler in {__name__}.trigger haltungen, {sql_file =}")
            return False

    consl.commit()

    # Haltungen_untersucht ----------------------------------------------------------------

    sqls = [
        """CREATE TABLE haltungen_untersucht(
            pk INTEGER PRIMARY KEY,
            haltnam TEXT,
            schoben TEXT,                                   -- join schaechte.schnam
            schunten TEXT,                                  -- join schaechte.schnam
            hoehe REAL,                                     -- Profilhoehe (m)
            breite REAL,                                    -- Profilbreite (m)
            laenge REAL,                                    -- abweichende Haltungslänge (m)
            baujahr INTEGER,
            id INTEGER,                                     -- absolute Nummer der Inspektion
            untersuchtag TEXT,
            untersucher TEXT,
            wetter INTEGER DEFAULT 0,
            bewertungsart TEXT,
            bewertungstag TEXT,
            strasse TEXT,
            datenart TEXT,
            max_ZD INTEGER,
            max_ZB INTEGER, 
            max_ZS INTEGER,
            xschob REAL,
            yschob REAL,
            xschun REAL,
            yschun REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('haltungen_untersucht','geom',{},'LINESTRING',2)".format(epsg),
        "SELECT CreateSpatialIndex('haltungen_untersucht','geom')"
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "Haltungen" konnte nicht erstellt werden',
            )
            consl.close()
            return False

    # untersuchungsdaten Haltung

    sqls = [
        """CREATE TABLE untersuchdat_haltung (
            pk INTEGER PRIMARY KEY,
            untersuchhal TEXT,
            untersuchrichtung TEXT,
            schoben TEXT,                                   -- join schaechte.schnam 
            schunten TEXT,                                  -- join schaechte.schnam
            id INTEGER,                                     -- absolute Nummer der Inspektion
            untersuchtag TEXT,
            bandnr INTEGER,
            videozaehler TEXT,
            inspektionslaenge REAL,
            station REAL,
            stationtext REAL,
            timecode INTEGER,
            video_offset REAL,
            kuerzel TEXT,
            charakt1 TEXT,
            charakt2 TEXT,
            quantnr1 REAL, 
            quantnr2 REAL, 
            streckenschaden TEXT,
            streckenschaden_lfdnr INTEGER,
            pos_von INTEGER, 
            pos_bis INTEGER,
            foto_dateiname TEXT,
            film_dateiname TEXT,
            ordner_bild TEXT,
            ordner_video TEXT,
            richtung TEXT,
            ZD INTEGER,
            ZB INTEGER,
            ZS INTEGER,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('untersuchdat_haltung','geom',{},'LINESTRING',2)".format(epsg),
        "SELECT CreateSpatialIndex('untersuchdat_haltung','geom')",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "untersuchdat_haltung" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Anschlussleitung ----------------------------------------------------------------

    sqls = [
        """CREATE TABLE anschlussleitungen (
            pk INTEGER PRIMARY KEY,
            leitnam TEXT,
            schoben TEXT,                                   -- join schaechte.schnam
            schunten TEXT,                                  -- join schaechte.schnam
            hoehe REAL,                                     -- Profilhoehe (m)
            breite REAL,                                    -- Profilbreite (m)
            laenge REAL,                                    -- abweichende Haltungslänge (m)
            sohleoben REAL,                                 -- abweichende Sohlhöhe oben (m)
            sohleunten REAL,                                -- abweichende Sohlhöhe unten (m)
            deckeloben REAL,
            deckelunten REAL,
            teilgebiet TEXT,                                -- join teilgebiet.tgnam
            qzu REAL,
            profilnam TEXT DEFAULT 'Kreisquerschnitt',
            entwart TEXT DEFAULT 'Regenwasser',             -- join entwaesserungsarten.bezeichnung
            material TEXT,
            ks REAL DEFAULT 1.5,
            simstatus TEXT DEFAULT 'vorhanden',             -- join simulationsstatus.bezeichnung
            xschob REAL,
            yschob REAL,
            xschun REAL,
            yschun REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('anschlussleitungen','geom',{},'LINESTRING',2)".format(epsg),
        "SELECT CreateSpatialIndex('anschlussleitungen','geom')",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
                fehlermeldung(
                    "qkan_database.createdbtables: {}".format(err),
                    'Tabelle "anschlussleitungen" konnte nicht erstellt werden',
                )
                consl.close()
                return False

    consl.commit()

    # Schaechte ----------------------------------------------------------------
    # [knotentyp]: Typ der Verknüpfung (kommt aus Kanal++)

    sqls = [
        """CREATE TABLE schaechte (
            pk INTEGER PRIMARY KEY,
            schnam TEXT,
            sohlhoehe REAL,
            deckelhoehe REAL,
            durchm REAL,
            druckdicht INTEGER, 
            ueberstauflaeche REAL DEFAULT 0,
            entwart TEXT DEFAULT 'Regenwasser',             -- join entwaesserungsarten.bezeichnung
            strasse TEXT,
            teilgebiet TEXT,                                -- join teilgebiet.tgnam
            knotentyp TEXT,                                 -- join knotentypen.knotentyp
            auslasstyp TEXT,                                -- join auslasstypen.bezeichnung
            schachttyp TEXT DEFAULT 'Schacht',              -- join schachttypen.schachttyp
            simstatus TEXT DEFAULT 'vorhanden',             -- join simulationsstatus.bezeichnung
            material TEXT,
            xsch REAL, 
            ysch REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        """SELECT AddGeometryColumn('schaechte','geop',{},'POINT',2);""".format(epsg),
        """SELECT AddGeometryColumn('schaechte','geom',{},'MULTIPOLYGON',2);""".format(epsg),
        """SELECT CreateSpatialIndex('schaechte','geom')""",
        """SELECT CreateSpatialIndex('schaechte','geop')""",
        "DROP TRIGGER ggi_schaechte_geom",
        "DROP TRIGGER ggu_schaechte_geom",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                f'Tabelle "Schaechte" konnte nicht erstellt werden:\n{sql}',
            )
            consl.close()
            return False

    sql = f"""CREATE VIEW IF NOT EXISTS schaechte_data AS 
          SELECT
            schnam, 
            xsch, ysch, 
            sohlhoehe, 
            deckelhoehe, durchm, 
            druckdicht, ueberstauflaeche, 
            entwart, strasse, teilgebiet, 
            knotentyp, auslasstyp, schachttyp, 
            simstatus, material,
            kommentar, createdat,
            geop, geom
          FROM schaechte;"""
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'View "schaechte_data" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    consl.commit()


    # Schaechte_untersucht ----------------------------------------------------------------
    # [knotentyp]: Typ der Verknüpfung (kommt aus Kanal++)

    sqls = [
        """CREATE TABLE schaechte_untersucht (
            pk INTEGER PRIMARY KEY,
            schnam TEXT, 
            durchm REAL,
            baujahr INTEGER,
            id INTEGER,                                     -- absolute Nummer der Inspektion
            untersuchtag TEXT, 
            untersucher TEXT, 
            wetter INTEGER DEFAULT 0, 
            strasse TEXT,
            bewertungsart TEXT, 
            bewertungstag TEXT,
            datenart TEXT,
            max_ZD INTEGER,
            max_ZB INTEGER,
            max_ZS INTEGER, 
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
        """SELECT AddGeometryColumn('schaechte_untersucht','geop',{},'POINT',2);""".format(epsg),
        """SELECT CreateSpatialIndex('schaechte_untersucht','geop')""",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "schaechte_untersucht" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # untersuchungsdaten Schaechte

    sqls = [
        """CREATE TABLE untersuchdat_schacht (
            pk INTEGER PRIMARY KEY,
            untersuchsch TEXT,
            id INTEGER,                                     -- absolute Nummer der Inspektion
            untersuchtag TEXT,
            bandnr INTEGER,
            videozaehler TEXT,
            timecode INTEGER,
            kuerzel TEXT,
            charakt1 TEXT,
            charakt2 TEXT,
            quantnr1 REAL,
            quantnr2 REAL,
            streckenschaden TEXT,
            streckenschaden_lfdnr INTEGER,
            pos_von INTEGER,
            pos_bis INTEGER,
            vertikale_lage INTEGER,
            inspektionslaenge INTEGER,
            bereich TEXT,
            foto_dateiname TEXT,
            ordner TEXT,
            ZD INTEGER,
            ZB INTEGER,
            ZS INTEGER,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP
            )""",
        """SELECT AddGeometryColumn('Untersuchdat_schacht','geop',{},'POINT',2);""".format(epsg),
        """SELECT CreateSpatialIndex('Untersuchdat_schacht','geop')""",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "Untersuchdat_Schächte" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Profile ------------------------------------------------------------------

    sql = """CREATE TABLE profile (
            pk INTEGER PRIMARY KEY,
            profilnam TEXT,
            he_nr INTEGER,
            mu_nr INTEGER,
            kp_key TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Profile" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Entwaesserungssysteme ----------------------------------------------------

    sql = """CREATE TABLE entwaesserungsarten (
            pk INTEGER PRIMARY KEY, 
            bezeichnung TEXT,                   -- eindeutige QKan-Bezeichnung 
            kuerzel TEXT,                       -- nur für Beschriftung
            bemerkung TEXT, 
            he_nr INTEGER,                      -- HYSTEM-EXTRAN
            kp_nr INTEGER,                      -- DYNA / Kanal++
            isybau TEXT,                        -- BFR Abwasser
            m150 TEXT,                          -- DWA M150
            m145 TEXT,                          -- DWA M145
            transport INTEGER,                  -- Transporthaltung? - deprecated
            druckdicht INTEGER                  -- Druckleitung? - deprecated
            )"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "entwaesserungsarten" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Sonderelemente Haltungen -------------------------------------------------

    sql = """CREATE TABLE haltungstypen(
            pk INTEGER PRIMARY KEY, 
            bezeichnung TEXT, 
            bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "haltungstypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Untersuchungsrichtung ----------------------------------------------------

    sql = """CREATE TABLE untersuchrichtung (
        pk INTEGER PRIMARY KEY, 
        kuerzel TEXT, 
        bezeichnung TEXT, 
        bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "untersuchrichtung" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            ('O', 'in Fließrichtung', 'automatisch hinzugefügt'),
            ('U', 'gegen Fließrichtung', 'automatisch hinzugefügt'),
        ]

        cursl.executemany(
            "INSERT INTO untersuchrichtung (kuerzel, bezeichnung, bemerkung) VALUES (?, ?, ?)",
            daten
        )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "untersuchrichtung" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # wetter ----------------------------------------------------

    sql = """CREATE TABLE wetter (
            pk INTEGER PRIMARY KEY, 
            kuerzel INTEGER, 
            bezeichnung TEXT, 
            bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "wetter" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            (0, 'keine Angabe', None),
            (1, 'kein Niederschlag', None),
            (2, 'Regen', None),
            (3, 'Schnee- oder Eisschmelzwasser', None),
        ]

        cursl.executemany(
            "INSERT INTO wetter (kuerzel, bezeichnung, bemerkung) VALUES (?, ?, ?)",
            daten
        )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "wetter" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # bewertungsart ----------------------------------------------------

    sql = """CREATE TABLE bewertungsart (
            pk INTEGER PRIMARY KEY, 
            kuerzel INTEGER, 
            bezeichnung TEXT, 
            bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "bewertungsart" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            (0, 'keine Angabe', None),
            (1, 'ISYBAU 2006/DIN-EN 13508-2:2011', None),
            (2, 'ISYBAU 2001', None),
            (3, 'ISYBAU 1996', None),
            (4, 'Anderes Verfahren', None),
        ]

        cursl.executemany(
            "INSERT INTO bewertungsart (kuerzel, bezeichnung, bemerkung) VALUES (?, ?, ?)",
            daten
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "bewertungsart" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # druckdicht ----------------------------------------------------

    sql = """CREATE TABLE druckdicht (
                pk INTEGER PRIMARY KEY, 
                bezeichnung TEXT, 
                kuerzel INTEGER, 
                bemerkung TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "druckdicht" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            (1, 'vorhanden', None),
            (0, 'nicht vorhanden', None),
        ]

        cursl.executemany(
            "INSERT INTO druckdicht (kuerzel, bezeichnung, bemerkung) VALUES (?, ?, ?)",
            daten
        )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "druckdicht" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Pumpentypen --------------------------------------------------------------

    sql = """CREATE TABLE pumpentypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT, 
    he_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "pumpentypen" konnte nicht erstellt werden.',
        )
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

    sqls = [
        """CREATE TABLE einzugsgebiete (
            pk INTEGER PRIMARY KEY,
            tgnam TEXT,
            ewdichte REAL,
            wverbrauch REAL,
            stdmittel REAL,
            fremdwas REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('einzugsgebiete','geom',{},'MULTIPOLYGON',2)".format(epsg),
        "SELECT CreateSpatialIndex('einzugsgebiete','geom')",
        "DROP TRIGGER ggi_einzugsgebiete_geom",
        "DROP TRIGGER ggu_einzugsgebiete_geom",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "Einzugsgebiete" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Teilgebiete ------------------------------------------------------------------
    #  Verwendung:
    # Auswahl von Objekten in verschiedenen Tabellen für verschiedene Aufgaben (z. B.
    # automatische Verknüpfung von befestigten Flächen und direkten Einleitungen).

    sqls = [
        """CREATE TABLE teilgebiete (
            pk INTEGER PRIMARY KEY,
            tgnam TEXT,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('teilgebiete','geom',{},'MULTIPOLYGON',2)".format(epsg),
        "SELECT CreateSpatialIndex('teilgebiete','geom')",
        "DROP TRIGGER ggi_teilgebiete_geom",
        "DROP TRIGGER ggu_teilgebiete_geom",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "Teilgebiete" konnte nicht erstellt werden.',
            )
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

    sql = """CREATE TABLE gruppen (
            pk INTEGER PRIMARY KEY,
            pktab INTEGER,
            grnam TEXT,
            teilgebiet TEXT,                               -- join teilgebiet.tgnam
            tabelle TEXT,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "gruppen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Befestigte und unbefestigte Flächen ------------------------------------------------------

    sqls = [
        """CREATE TABLE flaechen (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,                           -- join haltungen.haltnam
            schnam TEXT,                            -- join schaechte.schnam
            neigkl INTEGER DEFAULT 1,               -- Neigungsklasse (1-4)
            neigung REAL,                           -- absolute Neigung (%)
            teilgebiet TEXT,                        -- join teilgebiet.tgnam
            regenschreiber TEXT,
            abflussparameter TEXT,                  -- join abflussparameter.apnam
            aufteilen TEXT DEFAULT 'nein',
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        """SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2)""".format(epsg),
        """SELECT CreateSpatialIndex('flaechen','geom')""",
        "DROP TRIGGER ggi_flaechen_geom",
        "DROP TRIGGER ggu_flaechen_geom",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "flaechen" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Anbindung Flächen
    # Die Tabelle linkfl verwaltet die Anbindung von Flächen an Haltungen. Diese Anbindung
    # wird ausschließlich grafisch verwaltet und beim Export direkt verwendet.
    # Flächen, bei denen das Attribut "aufteilen" den Wert 'ja' hat, werden mit dem
    # Werkzeug "QKan_Link_Flaechen" mit allen durch die Verschneidung mit tezg entstehenden
    # Anteilen zugeordnet.

    sqls = [
        """CREATE TABLE linkfl (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,               -- join haltungen.haltnam
            schnam TEXT,                -- join schaechte.schnam
            tezgnam TEXT,               -- join tezg.flnam
            teilgebiet TEXT,            -- join teilgebiet.tgnam
            abflusstyp TEXT,            -- JOIN abflusstypen.abflusstyp
            speicherzahl INTEGER,       -- HE8: AnzahlSpeicher
            speicherkonst REAL,         -- HE8: Speicherkonstante (Typ 0)
            fliesszeitkanal REAL,       -- HE8: LaengsteFliesszeitKanal (Typ 1)
            fliesszeitflaeche REAL      -- HE8: FliesszeitOberflaeche (Typ 1) oder
                                        -- Schwerpunktlaufzeit (Typ 2)
            )""",
        """SELECT AddGeometryColumn('linkfl','geom',{epsg},'MULTIPOLYGON',2)""".format(epsg=epsg),
        """SELECT AddGeometryColumn('linkfl','gbuf',{epsg},'MULTIPOLYGON',2)""".format(epsg=epsg),
        """SELECT AddGeometryColumn('linkfl','glink',{epsg},'LINESTRING',2)""".format(epsg=epsg),
        "SELECT CreateSpatialIndex('linkfl','glink')",
        "DROP TRIGGER ggi_linkfl_geom",
        "DROP TRIGGER ggi_linkfl_gbuf",
        "DROP TRIGGER ggu_linkfl_geom",
        "DROP TRIGGER ggu_linkfl_gbuf",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "linkfl" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Anbindung Direkteinleitungen --------------------------------------------------------------
    # Die Tabelle linksw verwaltet die Anbindung von Gebäuden an Haltungen. Diese Anbindung
    # wird anschließend in das Feld haltnam eingetragen. Der Export erfolgt allerdings anhand
    # der grafischen Verknüpfungen dieser Tabelle.

    sqls = [
        """CREATE TABLE linksw (
            pk INTEGER PRIMARY KEY,
            elnam TEXT,
            haltnam TEXT,               -- join haltungen.haltnam
            schnam TEXT,                -- join schaechte.schnam
            teilgebiet TEXT)""",
        """SELECT AddGeometryColumn('linksw','geom',{epsg},'POLYGON',2)""".format(epsg=epsg),
        """SELECT AddGeometryColumn('linksw','gbuf',{epsg},'MULTIPOLYGON',2)""".format(epsg=epsg),
        """SELECT AddGeometryColumn('linksw','glink',{epsg},'LINESTRING',2)""".format(epsg=epsg),
        "SELECT CreateSpatialIndex('linksw','geom')",
        "DROP TRIGGER ggi_linksw_geom",
        "DROP TRIGGER ggi_linksw_gbuf",
        "DROP TRIGGER ggu_linksw_geom",
        "DROP TRIGGER ggu_linksw_gbuf",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(traceback.format_exc()),
                'Tabelle "linksw" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Teileinzugsgebiete ------------------------------------------------------------------

    sqls = [
        """-- Haltungsflächen. Verschneidung, Verwaltung der Befestigungsgrade (alte Programme)
            CREATE TABLE tezg (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,               -- join haltungen.haltnam
            schnam TEXT,                -- join schaechte.schnam
            neigkl INTEGER DEFAULT 1,   -- Werte [1-5], als Vorgabe fuer automatisch erzeugte unbef Flaechen
            neigung REAL,               -- absolute Neigung (%)
            befgrad REAL,               -- (-) Befestigungsgrad absolut, nur optional fuer SWMM und HE6
            schwerpunktlaufzeit REAL,   -- nur, wenn nur Haltungsflächen aber keine Flächen eingelesen werden
            regenschreiber TEXT,        -- Regenschreiber beziehen sich auf Zieldaten
            teilgebiet TEXT,            -- join teilgebiet.tgnam
            abflussparameter TEXT,      -- als Vorgabe fuer automatisch erzeugte unbef Flaechen
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('tezg','geom',{},'MULTIPOLYGON',2)".format(epsg),
        "SELECT CreateSpatialIndex('tezg','geom')",
        "DROP TRIGGER ggi_tezg_geom",
        "DROP TRIGGER ggu_tezg_geom",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "tezg" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Direkte Einleitungen ----------------------------------------------------------
    # Erfasst alle Direkteinleitungen mit festem SW-Zufluss (m³/a)
    # Die Zuordnung zum Teilgebiet dient nur der Auswahl

    sqls = [
        """CREATE TABLE einleit (
            pk INTEGER PRIMARY KEY,
            elnam TEXT,
            haltnam TEXT,               -- join haltungen.haltnam
            schnam TEXT,                -- join schaechte.schnam
            teilgebiet TEXT,            -- join teilgebiet.tgnam 
            zufluss REAL,
            ew REAL,
            einzugsgebiet TEXT,         -- join einzugsgebiete.tgnam
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        "SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)".format(epsg),
        "SELECT CreateSpatialIndex('einleit','geom')",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "einleit" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Einleitungen aus Aussengebieten ----------------------------------------------------------------
    # Erfasst alle Außengebiete
    # Die Zuordnung zum Teilgebiet dient nur der Auswahl

    sqls = [
        """CREATE TABLE aussengebiete (
            pk INTEGER PRIMARY KEY, 
            gebnam TEXT, 
            schnam TEXT,                -- join schaechte.schnam 
            hoeheob REAL, 
            hoeheun REAL, 
            fliessweg REAL, 
            basisabfluss REAL, 
            cn REAL, 
            regenschreiber TEXT, 
            teilgebiet TEXT,            -- join teilgebiet.tgnam 
            kommentar TEXT, 
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)""",
        """SELECT AddGeometryColumn('aussengebiete','geom',{epsg},'MULTIPOLYGON',2)""".format(epsg=epsg),
        "SELECT CreateSpatialIndex('aussengebiete','geom')",
        "DROP TRIGGER ggi_aussengebiete_geom",
        "DROP TRIGGER ggu_aussengebiete_geom",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                'Tabelle "aussengebiete" konnte nicht erstellt werden: \n{}'.format(
                    repr(err)
                )
            )
            consl.close()
            return False

    consl.commit()

    # Anbindung Aussengebiete -----------------------------------------------------------------------------
    # Die Tabelle linkageb verwaltet die Anbindung von Aussengebieten an Schächte. Diese Anbindung
    # wird anschließend in das Feld schnam eingetragen. Der Export erfolgt allerdings anhand
    # der grafischen Verknüpfungen dieser Tabelle.

    sqls = [
        """CREATE TABLE linkageb (
            pk INTEGER PRIMARY KEY,
            gebnam TEXT,
            schnam TEXT)""",
        """SELECT AddGeometryColumn('linkageb','glink',{epsg},'LINESTRING',2)""".format(epsg=epsg),
        "SELECT CreateSpatialIndex('linkageb','glink')",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabelle "linkageb" konnte nicht erstellt werden.',
            )
            consl.close()
            return False

    consl.commit()

    # Simulationsstatus/Planungsstatus -----------------------------------------

    sql = """CREATE TABLE simulationsstatus (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "simulationsstatus" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            ('keine Angabe', 0, None, 5),
            ('vorhanden', 1, 1, 0),
            ('geplant', 2, None, 1),
            ('fiktiv', 3, None, 2),
            ('außer Betrieb (keine Sim.)', 4, None, 3),
            ('verfüllt (keine Sim.)', 5, None, None),
            ('stillgelegt', None, None, 4),
            ('rückgebaut', None, None, 6),
        ]

        cursl.executemany(
            "INSERT INTO simulationsstatus (bezeichnung, he_nr, mu_nr, kp_nr) VALUES (?, ?, ?, ?)",
            daten
        )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "simulationsstatus" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Auslasstypen -------------------------------------------------------------

    sql = """CREATE TABLE auslasstypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "auslasstypen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            ('frei', 0, None, None),
            ('normal', 1, None, None),
            ('konstant', 2, None, None),
            ('Tide', 3, None, None),
            ('Zeitreihe', 4, None, None),
        ]

        cursl.executemany(
            "INSERT INTO auslasstypen (bezeichnung, he_nr, mu_nr, kp_nr) VALUES (?, ?, ?, ?)",
            daten
        )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "auslasstypen" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Abflussparameter -------------------------------------------------------------

    sql = """CREATE TABLE abflussparameter (
            pk INTEGER PRIMARY KEY, 
            apnam TEXT, 
            anfangsabflussbeiwert REAL, 
            endabflussbeiwert REAL, 
            benetzungsverlust REAL, 
            muldenverlust REAL, 
            benetzung_startwert REAL, 
            mulden_startwert REAL, 
            rauheit_kst REAL,                       -- Rauheit Stricklerbeiwert = 1/n
            pctZero REAL,                           -- SWMM: % Zero-Imperv
            bodenklasse TEXT,                       -- impervious: NULL, pervious: JOIN TO bodenklasse.bknam
            flaechentyp TEXT,                       -- JOIN TO flaechentypen.bezeichnung
            kommentar TEXT, 
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "abflussparameter" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Tabelle "flaechentypen" --------------------------------------------------------------------

    sql = """CREATE TABLE IF NOT EXISTS flaechentypen (
        pk INTEGER PRIMARY KEY,
        bezeichnung TEXT,
        he_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "flaechentypen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:
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
            cursl.execute(sql)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "abflussparameter" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Bodenklasse -------------------------------------------------------------

    sql = """CREATE TABLE bodenklassen (
            pk INTEGER PRIMARY KEY, 
            bknam TEXT, 
            infiltrationsrateanfang REAL,               -- (mm/min)
            infiltrationsrateende REAL,                 -- (mm/min)
            infiltrationsratestart REAL,                -- (mm/min)
            rueckgangskonstante REAL,                   -- (1/d)
            regenerationskonstante REAL,                -- (1/d)
            saettigungswassergehalt REAL,               -- (mm)
            kommentar TEXT, 
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "bodenklassen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Abflusstypen -------------------------------------------------------------

    sql = """CREATE TABLE abflusstypen (
    pk INTEGER PRIMARY KEY, 
    abflusstyp TEXT,
    he_nr INTEGER,              -- JOIN he.Flaeche.BerechnungSpeicherkonstante
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "abflusstypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        ('Speicherkaskade', 0, 0),
        ('Fliesszeiten', 1, 1),
        ('Schwerpunktlaufzeit', 2, 2),
    ]

    try:
        sql = """INSERT INTO abflusstypen
                 (abflusstyp, he_nr, kp_nr) Values (?, ?, ?)"""
        cursl.executemany(sql, daten)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "abflusstypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                err
            ),
        )
        consl.close()
        return False

    consl.commit()

    # Knotentypen -------------------------------------------------------------

    sql = """CREATE TABLE knotentypen (
    pk INTEGER PRIMARY KEY, 
    knotentyp TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "knotentypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        ('Anfangsschacht',),
        ('Einzelschacht',),
        ('Endschacht',),
        ('Hochpunkt',),
        ('Normalschacht',),
        ('Tiefpunkt',),
        ('Verzweigung',),
        ('Fliesszeiten',),
    ]

    try:
        sql = """INSERT INTO knotentypen
                 (knotentyp) Values (?)"""
        cursl.executemany(sql, daten)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "knotentypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                err
            ),
        )
        consl.close()
        return False

    consl.commit()

    # Schachttypen -------------------------------------------------------------

    sql = """CREATE TABLE schachttypen (
    pk INTEGER PRIMARY KEY, 
    schachttyp TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "schachttypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [("Auslass",),
             ("Schacht",),
             ("Anschlussschacht",),
             ("Speicher",)]

    try:
        sql = f"""INSERT INTO schachttypen (schachttyp) Values (?)"""
        cursl.executemany(sql, daten)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "schachttypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                err
            ),
        )
        consl.close()
        return False

    consl.commit()

    # Hilfstabelle für den DYNA-Export -----------------------------------------
    # TODO: als temporäre Tabelle in das Export-Modul verschieben

    sql = """
        CREATE TABLE IF NOT EXISTS dynahal (
            pk INTEGER PRIMARY KEY,
            haltnam TEXT,
            schoben TEXT,                                   -- join schaechte.schnam
            schunten TEXT,                                  -- join schaechte.schnam
            teilgebiet TEXT,                                -- join teilgebiet.tgnam
            kanalnummer TEXT,
            haltungsnummer TEXT,
            anzobob INTEGER,
            anzobun INTEGER,
            anzunun INTEGER,
            anzunob INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "dynahal".',
        )
        consl.close()
        return False
    consl.commit()

    # Hilfstabelle für den Flächen-Export

    sqls = [
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
            LastModified TEXT DEFAULT CURRENT_TIMESTAMP, 
            Kommentar TEXT)""",
        """SELECT AddGeometryColumn('flaechen_he8','Geometry', -1,'MULTIPOLYGON',2)""",
        """SELECT CreateSpatialIndex('flaechen_he8', 'Geometry')""",
        "DROP TRIGGER ggi_flaechen_he8_geometry",
        "DROP TRIGGER ggu_flaechen_he8_geometry",
    ]
    for sql in sqls:
        try:
            cursl.execute(sql)
        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Fehler beim Erzeugen der Tabelle "flaechen_he8".',
            )
            consl.close()
            return False

    consl.commit()

    # Abfragen für Plausibilitätsprüfungen
    sql = """
        CREATE TABLE IF NOT EXISTS pruefsql (
            pk INTEGER PRIMARY KEY,
            gruppe TEXT,                        -- zur Auswahl nach Thema
            warntext TEXT,                      -- Beschreibung der SQL-Abfrage
            warntyp TEXT,                       -- 'Info', 'Warnung', 'Fehler'
            warnlevel INTEGER,                  -- zur Sortierung, 1-3: Info, 4-7: Warnung, 8-10: Fehler
            sql TEXT,
            layername TEXT,                     -- Objektsuche: Layername
            attrname TEXT,                      -- Objektsuche: Attribut zur Objektidentifikation,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)
    """

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "pruefsql".',
        )
        consl.close()
        return False

    plausisqlfile = os.path.join(pluginDirectory("qkan"), "templates", "plausibilitaetspruefungen.sql")
    try:
        with open(plausisqlfile) as fr:
            sqlfile = fr.read()
        cursl.executescript(sqlfile)
    except BaseException as err:
        fehlermeldung(
            "dbfunc.DBConnection.sql: SQL-Fehler beim Lesen der Plausibilitätsabfragen",
            "{err}\n{f}".format(err=repr(err), f=plausisqlfile),
        )
        consl.close()
        return False

    # Ergebnisse der Plausibilitätsprüfungen
    sql = """
        CREATE TABLE IF NOT EXISTS pruefliste (
            pk INTEGER PRIMARY KEY,
            warntext TEXT,                      -- Beschreibung der SQL-Abfrage
            warntyp TEXT,                       -- 'Info', 'Warnung', 'Fehler'
            warnlevel INTEGER,                  -- zur Sortierung, 1-3: Info, 4-7: Warnung, 8-10: Fehler
            layername TEXT,                     -- Objektsuche: Layername
            attrname TEXT,                      -- Objektsuche: Attribut zur Objektidentifikation,
            objname TEXT,                       -- Objektsuche: Objektname
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)
    """

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "pruefliste".',
        )
        consl.close()
        return False

    consl.commit()

    # Referenztabelle für Plausi Zustandsklassen -----------------------------

    sql = """
                CREATE TABLE IF NOT EXISTS reflist_zustand (
                    pk INTEGER PRIMARY KEY,
                    art TEXT,                      -- 
                    hauptcode TEXT,                -- 
                    charakterisierung1 TEXT,        --
                    charakterisierung2 TEXT,         -- 
                    bereich TEXT        -- 
                    )
            """

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "reflist_zustand".',
        )
        consl.close()
        return False

    consl.commit()

    # Allgemeine Informationen -----------------------------------------------

    sql = """CREATE TABLE info (
            pk INTEGER PRIMARY KEY, 
            subject TEXT, 
            value TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Tabelle "Info".',
        )
        consl.close()
        return False

    consl.commit()

    # Abschluss --------------------------------------------------------------------

    # Aktuelle Version eintragen
    sql = """INSERT INTO info (subject, value) VALUES ('version', '{}'); \n""".format(
        version
    )
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Einfügen der Tabelle "Info".',
        )
        consl.close()
        return False
    consl.commit()

    fortschritt("Tabellen erstellt...", 0.01)

    return True


# ----------------------------------------------------------------------------------------------------------------------
def test() -> None:
    # Verzeichnis der Testdaten

    iface = QKan.instance.iface

    pfad = "C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/modelldb_itwh"
    database_qkan = os.path.join(pfad, "test1.sqlite")

    if os.path.exists(database_qkan):
        os.remove(database_qkan)

    consl = spatialite_connect(database=database_qkan)
    cursl = consl.cursor()

    progress_message_bar = iface.messageBar().createMessage("Doing something boring...")
    progress = QProgressBar()
    progress.setMaximum(10)
    progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    progress_message_bar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progress_message_bar, iface.messageBar().INFO)
    progress.setValue(2)
    iface.messageBar().clearWidgets()

    iface.mainWindow().statusBar().showMessage(
        "SpatiaLite-Datenbank wird erstellt. Bitte warten... {} %".format(20)
    )
    import time

    time.sleep(1)

    sql = "SELECT InitSpatialMetadata(transaction = TRUE)"
    cursl.execute(sql)

    iface.messageBar().pushMessage(
        "Information", "SpatiaLite-Datenbank ist erstellt!", level=Qgis.Info
    )

    createdbtables(consl, cursl, version="1.0.0")
    consl.close()


if __name__ in ("__main__", "__console__", "__builtin__"):
    test()
