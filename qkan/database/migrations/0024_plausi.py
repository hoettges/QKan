from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.2.15"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Ergänze Tabellen für Plausibilitätschecks"""

    # Tabelle mit SQL-Abfragen
    sql = """
        CREATE TABLE IF NOT EXISTS pruefsql (
            pk INTEGER PRIMARY KEY,
            gruppe TEXT,                        -- zur Auswahl nach Thema
            warntext TEXT,                      -- Beschreibung der SQL-Abfrage
            warntyp TEXT,                       -- 'Info', 'Warnung', 'Fehler'
            warnlevel INTEGER,                  -- zur Sortierung, 1-3: Info, 4-7: Warnung, 8-10: Fehler
            sql TEXT,
            layername TEXT,                     -- Objektsuche: Layername
            attrname TEXT                       -- Objektsuche: Attribut zur Objektidentifikation,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)
    """
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False

    # Tabelle mit Ergebnissen der Plausibilitätschecks
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
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False

    dbcon.commit()
    return True
