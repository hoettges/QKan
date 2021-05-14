import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.1.2"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut befgrad in tezg -----------------------------
    if not dbcon.sql(
        "ALTER TABLE tezg ADD COLUMN befgrad REAL",
        "dbfunc.DBConnection.version (3.1.2-1)",
    ):
        return False

    dbcon.commit()
    return True
