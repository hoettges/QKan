import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.40"              # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut bandnr in untersuchungsdaten
    if not dbcon.sql(
        "ALTER TABLE untersuchdat_haltung ADD COLUMN bandnr INTEGER",
        "dbfunc.DBConnection.version (3.2.40)",
    ):
        return False

    if not dbcon.sql(
        "ALTER TABLE untersuchdat_schacht ADD COLUMN bandnr INTEGER",
        "dbfunc.DBConnection.version (3.2.40)",
    ):
        return False

    dbcon.commit()  # Wurde schon durchgeführt
    return True
