import logging

from qkan.database.dbfunc import DBConnection
from qkan.tools.k_layersadapt import load_plausisql

VERSION = "3.3.8"              # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Zusätzliche Spalten in der Haltungstabelle
    :type dbcon:    DBConnection
    """
    if not dbcon.alter_table(
        "haltungen_untersucht",
        [
            "haltnam TEXT",
            "schoben TEXT                                    -- join schaechte.schnam",
            "schunten TEXT                                   -- join schaechte.schnam",
            "hoehe REAL                                      -- Profilhoehe (m)",
            "breite REAL                                     -- Profilbreite (m)",
            "laenge REAL                                     -- abweichende Haltungslänge (m)",
            "baujahr INTEGER",
            "id INTEGER                                      -- absolute Nummer der Inspektion",
            "untersuchtag TEXT",
            "untersucher TEXT",
            "wetter INTEGER DEFAULT 0",
            "bewertungsart TEXT",
            "bewertungstag TEXT",
            "strasse TEXT",
            "datenart TEXT",
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
            "timecode INTEGER",
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
            "max_ZD INTEGER",
            "max_ZB INTEGER",
            "max_ZS INTEGER",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
        ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Hinzufügen von untersuchtag "
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
            "timecode INTEGER",
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

    return True
