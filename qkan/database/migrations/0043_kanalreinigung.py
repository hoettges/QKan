from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError
VERSION = "3.4.11"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations.0043")

def run(dbcon: DBConnection) -> bool:
    # Ergänzung von Kanalreinigungstabelle

    sqls = [
        """CREATE TABLE IF NOT EXISTS kanalreinigung(
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
    ]
    for sql in sqls:
        if not dbcon.sql(sql, f"migration 0043, Version {VERSION}: "
                              f"Erstellen der Tabelle kanalreinigung"):
            return False

    return True
