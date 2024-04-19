from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "2.2.2"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Zusätzlicher Parameter flaechen.abflusstyp"""

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
