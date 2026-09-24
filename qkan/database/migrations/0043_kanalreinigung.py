from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError
VERSION = "3.4.20"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations.0043")

def run(dbcon: DBConnection) -> bool:
    # Ergänzung von Kanalreinigungstabelle

    sql = """CREATE TABLE IF NOT EXISTS kanalreinigung(
        pk INTEGER PRIMARY KEY,
        reinigungsdatum TEXT,
        ablagerungen TEXT,
        reinigungszeit TEXT,                                  
        fahrer TEXT,                                  
        beifahrer TEXT,                                     
        haltungsnummer INT,
        bemerkung TEXT,
        kontrolle TEXT,
        haltnam TEXT,
        createdat TEXT DEFAULT CURRENT_TIMESTAMP)"""
    try:
        dbcon.sql(
            sql=sql,
            stmt_category=f"migration 0043, Version {VERSION}: Erstellen der Tabelle kanalreinigung"
        )
    except:
        logger.error_code('Fehlgeschlagen: migration_0043, Tabelle kanalreinigung ergänzen')

    return True
