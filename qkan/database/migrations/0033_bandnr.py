from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.2.40"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut bandnr in untersuchungsdaten
    attrlis = dbcon.attrlist("untersuchdat_haltung")
    if "bandnr" not in attrlis:
        if not dbcon.sql(
            "ALTER TABLE untersuchdat_haltung ADD COLUMN bandnr INTEGER",
            "dbfunc.DBConnection.version (3.2.40)",
        ):
            return False

    attrlis = dbcon.attrlist("untersuchdat_schacht")
    if "bandnr" not in attrlis:
        if not dbcon.sql(
            "ALTER TABLE untersuchdat_schacht ADD COLUMN bandnr INTEGER",
            "dbfunc.DBConnection.version (3.2.40)",
        ):
            return False

    dbcon.commit()  # Wurde schon durchgeführt
    return True
