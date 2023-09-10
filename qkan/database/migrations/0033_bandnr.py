import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.3.2"              # must be higher than previous one

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut bandnr in untersuchungsdaten
    if not dbcon.sql(
        "ALTER TABLE untersuchdat_haltung ADD COLUMN bandnr INTEGER",
        "dbfunc.DBConnection.version (3.3.2)",
    ):
        return False

    if not dbcon.sql(
        "ALTER TABLE untersuchdat_schacht ADD COLUMN bandnr INTEGER",
        "dbfunc.DBConnection.version (3.3.2)",
    ):
        return False


    dbcon.commit()  # Wurde schon durchgeführt
    return True
