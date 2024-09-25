from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger
from qgis.core import QgsProject
from qgis.utils import pluginDirectory
import os

VERSION = "3.4.1"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:

    # Untersuchungsrichtung in Anschlussleitungen_untersucht ergänzen
    if not dbcon.alter_table(
        "anschlussleitungen_untersucht",
        [
            "leitnam TEXT",
            "bezugspunkt TEXT",
            "schoben TEXT                                    -- join schaechte.schnam",
            "schunten TEXT                                   -- join schaechte.schnam",
            "hoehe REAL                                      -- Profilhoehe (mm)",
            "breite REAL                                     -- Profilbreite (mm)",
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
            "max_ZB INTEGER",
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
            "Hinzufügen von Attribut untersuchrichtung in Tabelle anschlussleitungen_untersucht fehlgeschlagen"
        )

    # Umwandeln von Rohrhöhe und -breite auf mm
    sqls = [
        "UPDATE haltungen SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE haltungen SET breite = breite * 1000. WHERE breite < 15",
        "UPDATE haltungen SET aussendurchmesser = aussendurchmesser * 1000. WHERE aussendurchmesser < 15",
        "UPDATE haltungen_untersucht SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE haltungen_untersucht SET breite = breite * 1000. WHERE breite < 15",
        "UPDATE anschlussleitungen SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE anschlussleitungen SET breite = breite * 1000. WHERE breite < 15",
        "UPDATE anschlussleitungen_untersucht SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE anschlussleitungen_untersucht SET breite = breite * 1000. WHERE breite < 15",
    ]
    for sql in sqls:
        if not dbcon.sql(sql, f"migration 0038, Version {VERSION}: "
                              f"Umwandeln der Rohrabmessungen von m in mm"):
            logger.error('Fehler in migration 0038')
            raise Exception(f"{__name__}")

    # Neue Tabelle Eigentum

    sql = """CREATE TABLE IF NOT EXISTS eigentum (
    pk INTEGER PRIMARY KEY,
    name TEXT, 
    kommentar TEXT)"""

    if not dbcon.sql(sql, f"migration 0038, Version {VERSION}: "
                          f"Neue Tabelle Eigentum"):
        logger.error('Fehler in migration 0038')
        raise Exception(f"{__name__}")

    # Attribut Eigentum ergänzen

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
            "baujahr INTEGER",
            "eigentum TEXT                                   -- join eigentum.name",
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

    if not dbcon.alter_table(
        "schaechte",
        [
            "schnam TEXT",
            "sohlhoehe REAL",
            "deckelhoehe REAL",
            "durchm REAL",
            "druckdicht INTEGER DEFAULT 0                   -- ist Druckleitung",
            "ueberstauflaeche REAL DEFAULT 0",
            "entwart TEXT DEFAULT 'Regenwasser'             -- join entwaesserungsarten.bezeichnung",
            "strasse TEXT",
            "baujahr INTEGER",
            "eigentum TEXT                                  -- join eigentum.name",
            "teilgebiet TEXT                                -- join teilgebiet.tgnam",
            "knotentyp TEXT                                 -- join knotentypen.knotentyp",
            "auslasstyp TEXT                                -- join auslasstypen.bezeichnung",
            "schachttyp TEXT DEFAULT 'Schacht'              -- join schachttypen.schachttyp",
            "simstatus TEXT DEFAULT 'vorhanden'             -- join simulationsstatus.bezeichnung",
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

    dbcon.commit()

    return True
