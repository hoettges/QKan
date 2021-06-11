import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.1.6"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Zusätzlicher Parameter für Mike+ (vormals Mike Urban)"""

    attrlis = dbcon.attrlist("flaechen")
    if not attrlis:
        return False
    elif "neigung" not in attrlis:
        logger.debug("flaechen.neigung ist nicht in: {}".format(str(attrlis)))
        if not dbcon.sql(
            "ALTER TABLE flaechen ADD COLUMN neigung REAL",
            "dbfunc.DBConnection.version (3.1.6)",
        ):
            return False
        dbcon.commit()

    return True
