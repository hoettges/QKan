from qkan.database.dbfunc import DBConnection
from qkan.tools.k_layersadapt import load_plausisql
from qkan.utils import get_logger

VERSION = "3.3.8"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Zusätzliche Spalten in der Haltungstabelle
    :type dbcon:    DBConnection
    """
    if not dbcon.alter_table(
        "haltungen_untersucht",
        [
            "haltnam TEXT",
            "bezugspunkt TEXT",
            "schoben TEXT                                    -- join schaechte.schnam",
            "schunten TEXT                                   -- join schaechte.schnam",
            "hoehe REAL                                      -- Profilhoehe (m)",
            "breite REAL                                     -- Profilbreite (m)",
            "laenge REAL                                     -- abweichende Haltungslänge (m)",
            "baujahr INTEGER",
            "id INTEGER                                      -- absolute Nummer der Inspektion",
            "untersuchtag TEXT",
            "untersucher TEXT",
            "untersuchrichtung TEXT",
            "wetter INTEGER DEFAULT 0",
            "bewertungsart TEXT",
            "bewertungstag TEXT",
            "strasse TEXT",
            "datenart TEXT",
            "auftragsbezeichnung TEXT",
            "max_ZD INTEGER",
            "max_ZB INTEGER ",
            "max_ZS INTEGER",
            "xschob REAL",
            "yschob REAL",
            "xschun REAL",
            "yschun REAL",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
        ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von untersuchtag "
            "zu Tabelle 'haltungen_untersucht' fehlgeschlagen"
        )

    if not load_plausisql(dbcon):
        logger.error("Fehler in migration 0036_haltung_ergaenzung")
        return False

    if not dbcon.alter_table(
        "untersuchdat_haltung",
        [
            "untersuchhal TEXT",
            "untersuchrichtung TEXT",
            "schoben TEXT                                    -- join schaechte.schnam ",
            "schunten TEXT                                   -- join schaechte.schnam",
            "id INTEGER                                      -- absolute Nummer der Inspektion",
            "untersuchtag TEXT",
            "bandnr INTEGER",
            "videozaehler TEXT",
            "inspektionslaenge REAL",
            "station REAL",
            "stationtext REAL",
            "timecode TEXT",
            "video_offset REAL",
            "kuerzel TEXT",
            "charakt1 TEXT",
            "charakt2 TEXT",
            "quantnr1 REAL",
            "quantnr2 REAL",
            "streckenschaden TEXT",
            "streckenschaden_lfdnr INTEGER",
            "pos_von INTEGER",
            "pos_bis INTEGER",
            "foto_dateiname TEXT",
            "film_dateiname TEXT",
            "ordner_bild TEXT",
            "ordner_video TEXT",
            "richtung TEXT",
            "filmtyp INTEGER",
            "video_start INTEGER",
            "video_ende INTEGER",
            "ZD INTEGER",
            "ZB INTEGER",
            "ZS INTEGER",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
        ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von untersuchtag "
            "zu Tabelle 'untersuchdat_haltung' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "schaechte_untersucht",
        [
            "schnam TEXT",
            "bezugspunkt TEXT",
            "durchm REAL",
            "baujahr INTEGER",
            "id INTEGER                                      -- absolute Nummer der Inspektion",
            "untersuchtag TEXT",
            "untersucher TEXT",
            "wetter INTEGER DEFAULT 0",
            "strasse TEXT",
            "bewertungsart TEXT",
            "bewertungstag TEXT",
            "datenart TEXT",
            "auftragsbezeichnung TEXT",
            "max_ZD INTEGER",
            "max_ZB INTEGER",
            "max_ZS INTEGER",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
        ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von untersuchtag und Viedeodaten"
            "zu Tabelle 'schaechte_untersucht' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "untersuchdat_schacht",
        [
            "untersuchsch TEXT",
            "id INTEGER                                      -- absolute Nummer der Inspektion",
            "untersuchtag TEXT",
            "bandnr INTEGER",
            "videozaehler TEXT",
            "timecode TEXT",
            "kuerzel TEXT",
            "charakt1 TEXT",
            "charakt2 TEXT",
            "quantnr1 REAL",
            "quantnr2 REAL",
            "streckenschaden TEXT",
            "streckenschaden_lfdnr INTEGER",
            "pos_von INTEGER",
            "pos_bis INTEGER",
            "vertikale_lage INTEGER",
            "inspektionslaenge INTEGER",
            "bereich TEXT",
            "foto_dateiname TEXT",
            "ordner TEXT",
            "film_dateiname TEXT",
            "ordner_video TEXT",
            "ZD INTEGER",
            "ZB INTEGER",
            "ZS INTEGER",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
        ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von untersuchtag "
            "zu Tabelle 'untersuchdat_schacht' fehlgeschlagen"
        )


    if not dbcon.alter_table(
        "haltungen",
        [
            "haltnam TEXT",
            "schoben TEXT                                    -- join schaechte.schnam",
            "schunten TEXT                                   -- join schaechte.schnam",
            "hoehe REAL                                      -- Profilhoehe (m)",
            "breite REAL                                     -- Profilbreite (m)",
            "laenge REAL                                     -- abweichende Haltungslänge (m)",
            "aussendurchmesser REAL",
            "sohleoben REAL                                  -- abweichende Sohlhöhe oben (m)",
            "sohleunten REAL                                 -- abweichende Sohlhöhe unten (m)",
            "baujahr INT",
            "teilgebiet TEXT                                 -- join teilgebiet.tgnam",
            "strasse TEXT                                    -- für ISYBAU benötigt",
            "profilnam TEXT DEFAULT 'Kreisquerschnitt'       -- join profile.profilnam",
            "entwart TEXT DEFAULT 'Regenwasser'              -- join entwaesserungsarten.bezeichnung",
            "material TEXT",
            "profilauskleidung TEXT",
            "innenmaterial TEXT",
            "ks REAL DEFAULT 1.5                             -- abs. Rauheit (Prandtl-Colebrook)",
            "haltungstyp TEXT DEFAULT 'Haltung'              -- join haltungstypen.bezeichnung",
            "simstatus TEXT DEFAULT 'vorhanden'              -- join simulationsstatus.bezeichnung",
            "transport INTEGER DEFAULT 0                     -- ist Transporthaltung",
            "druckdicht INTEGER DEFAULT 0                    -- ist Druckleitung",
            "xschob REAL",
            "yschob REAL",
            "xschun REAL",
            "yschun REAL",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von aussendurchmesser, profilauskleidung, innenmaterial "
            "zu Tabelle 'haltungen' fehlgeschlagen"
        )

    if not load_plausisql(dbcon):
        logger.error("Fehler in migration 0037_untersuchdat")
        return False

    if not dbcon.alter_table(
        "anschlussleitungen",
        [
            "leitnam TEXT",
            "haltnam TEXT",
            "schoben TEXT                                    -- join schaechte.schnam",
            "schunten TEXT                                   -- join schaechte.schnam",
            "hoehe REAL                                      -- Profilhoehe (m)",
            "breite REAL                                     -- Profilbreite (m)",
            "laenge REAL                                     -- abweichende Haltungslänge (m)",
            "aussendurchmesser REAL",
            "sohleoben REAL                                  -- abweichende Sohlhöhe oben (m)",
            "sohleunten REAL                                 -- abweichende Sohlhöhe unten (m)",
            "baujahr INT",
            "teilgebiet TEXT                                 -- join teilgebiet.tgnam",
            "strasse TEXT                                    -- für ISYBAU benötigt",
            "profilnam TEXT DEFAULT 'Kreisquerschnitt'       -- join profile.profilnam",
            "entwart TEXT DEFAULT 'Regenwasser'              -- join entwaesserungsarten.bezeichnung",
            "material TEXT",
            "profilauskleidung TEXT",
            "innenmaterial TEXT",
            "ks REAL DEFAULT 1.5                             -- abs. Rauheit (Prandtl-Colebrook)",
            "anschlusstyp TEXT",
            "simstatus TEXT DEFAULT 'vorhanden'              -- join simulationsstatus.bezeichnung",
            "xschob REAL",
            "yschob REAL",
            "xschun REAL",
            "yschun REAL",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von aussendurchmesser, profilauskleidung, innenmaterial "
            "zu Tabelle 'anschlussleitungen' fehlgeschlagen"
        )

    if not load_plausisql(dbcon):
        logger.error("Fehler in migration 0037_untersuchdat")
        return False

    if not dbcon.alter_table(
            "schaechte",
            [
                "schnam TEXT",
                "sohlhoehe REAL",
                "deckelhoehe REAL",
                "durchm REAL",
                "druckdicht INTEGER",
                "ueberstauflaeche REAL DEFAULT 0",
                "entwart TEXT DEFAULT 'Regenwasser' -- join entwaesserungsarten.bezeichnung",
                "strasse TEXT",
                "baujahr INT",
                "teilgebiet TEXT -- join teilgebiet.tgnam",
                "knotentyp TEXT -- join knotentypen.knotentyp",
                "auslasstyp TEXT -- join auslasstypen.bezeichnung",
                "schachttyp TEXT DEFAULT 'Schacht' -- join schachttypen.schachttyp",
                "simstatus TEXT DEFAULT 'vorhanden' -- join simulationsstatus.bezeichnung",
                "material TEXT",
                "xsch REAL",
                "ysch REAL",
                "kommentar TEXT",
                "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
            ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von aussendurchmesser, profilauskleidung, innenmaterial "
            "zu Tabelle 'schaechte' fehlgeschlagen"
        )

    if not load_plausisql(dbcon):
        logger.error("Fehler in migration 0037_untersuchdat")
        return False

    #Löschen der Spalte richtung
    if not dbcon.alter_table(
            "untersuchdat_haltung",[],
            [
                "richtung TEXT",

            ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Löschen der Spalte richtung in der Tabelle untersuchdat_haltung fehlgeschlagen"
        )

    # Löschen der Spalte deckeloben, deckelunten
    if not dbcon.alter_table(
            "anschlussleitungen", [],
            [
                "deckeloben REAL",
                "deckelunten REAL",

            ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Löschen der Spalte deckeloben, deckelunten in der Tabelle anschlussleitungen fehlgeschlagen"
        )

    if not load_plausisql(dbcon):
        logger.error("Fehler in migration 0037_untersuchdat")
        return False

    #Anschlussleitungen_untersucht
    sql = """
            CREATE TABLE IF NOT EXISTS anschlussleitungen_untersucht (
                leitnam TEXT,
            bezugspunkt TEXT,
            schoben TEXT,                                   -- join schaechte.schnam
            schunten TEXT,                                  -- join schaechte.schnam
            hoehe REAL,                                     -- Profilhoehe (m)
            breite REAL,                                    -- Profilbreite (m)
            laenge REAL,                                    -- abweichende Haltungslänge (m)
            baujahr INTEGER,
            id INTEGER,                                     -- absolute Nummer der Inspektion
            objekt_id INTEGER,
            untersuchtag TEXT,
            untersucher TEXT,
            wetter INTEGER DEFAULT 0,
            bewertungsart TEXT,
            bewertungstag TEXT,
            strasse TEXT,
            datenart TEXT,
            auftragsbezeichnung TEXT,
            max_ZD INTEGER,
            max_ZB INTEGER, 
            max_ZS INTEGER,
            xschob REAL,
            yschob REAL,
            xschun REAL,
            yschun REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)
            """

    if not dbcon.sql(sql, f"dbfunc.DBConnection.version {VERSION}"):
        return False

    sql = f"""
            SELECT AddGeometryColumn('anschlussleitungen_untersucht','geom',{dbcon.epsg},'LINESTRING',2)
        """

    if not dbcon.sql(sql, f"dbfunc.DBConnection.version {VERSION}"):
        return False

    sql = """
                CREATE TABLE IF NOT EXISTS untersuchdat_anschlussleitung (
                    pk INTEGER PRIMARY KEY,
            untersuchleit TEXT,
            untersuchrichtung TEXT,
            schoben TEXT,                                   -- join schaechte.schnam 
            schunten TEXT,                                  -- join schaechte.schnam
            id INTEGER,                                     -- absolute Nummer der Inspektion
            objekt_id INTEGER,
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
            filmtyp INTEGER,
            video_start INTEGER,
            video_ende INTEGER,
            ZD INTEGER,
            ZB INTEGER,
            ZS INTEGER,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)
                """

    if not dbcon.sql(sql, f"dbfunc.DBConnection.version {VERSION}"):
        return False

    sql = f"""
                SELECT AddGeometryColumn('anschlussleitungen_untersucht','geom',{dbcon.epsg},'LINESTRING',2)
            """

    if not dbcon.sql(sql, f"dbfunc.DBConnection.version {VERSION}"):
        return False

