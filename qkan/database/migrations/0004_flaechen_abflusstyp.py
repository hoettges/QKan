import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.2.2"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    attrlis = dbcon.attrlist("flaechen")
    if not attrlis:
        return False
    elif "abflusstyp" not in attrlis:
        logger.debug("flaechen.abflusstyp ist nicht in: {}".format(str(attrlis)))
        if not dbcon.sql(
            "ALTER TABLE flaechen ADD COLUMN abflusstyp TEXT",
            "dbfunc.DBConnection.version (2.2.0-1)",
        ):
            return False
        dbcon.commit()

    return True
