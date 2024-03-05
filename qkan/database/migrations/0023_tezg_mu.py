from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.2.8"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut befgrad in tezg -----------------------------
    if not dbcon.sql(
        "ALTER TABLE tezg ADD COLUMN schwerpunktlaufzeit REAL",
        "dbfunc.DBConnection.version (3.2.8)",
    ):
        return False

    dbcon.commit()
    return True
