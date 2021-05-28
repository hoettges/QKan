import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.0.8"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliche Parameter für Mike+ (vormals Mike Urban)

    if not dbcon.sql(
        "ALTER TABLE flaechen ADD COLUMN neigung REAL",
        "dbfunc.DBConnection.version (3.1.6)",
    ):
        return False
    dbcon.commit()
    return True
