from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.1.2"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut befgrad in tezg -----------------------------
    if not dbcon.sql(
        "ALTER TABLE tezg ADD COLUMN befgrad REAL",
        "dbfunc.DBConnection.version (3.1.2-1)",
    ):
        return False

    dbcon.commit()
    return True
