import logging

from qkan.database.dbfunc import DBConnection
from qkan.tools.k_layersadapt import load_plausisql

VERSION = "3.3.7"              # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Zusätzliche Spalten in der Haltungstabelle
    :type dbcon:    DBConnection
    """

    if not dbcon.sql(
        "ALTER TABLE haltungen ADD COLUMN aussendurchmesser REAL",
        "dbfunc.DBConnection.version (3.3.7)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE haltungen ADD COLUMN profilauskleidung TEXT",
        "dbfunc.DBConnection.version (3.3.7)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE haltungen ADD COLUMN innenmaterial TEXT",
        "dbfunc.DBConnection.version (3.3.7)",
    ):
        return False
    dbcon.commit()


    if not load_plausisql(dbcon):
        logger.error("Fehler in migration 0036_haltung_ergaenzung")
        return False
    return True
