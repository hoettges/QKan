from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.utils import get_logger

VERSION = "2.1.2"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    attrlis = dbcon.attrlist("linksw")
    if not attrlis:
        fehlermeldung(
            "dbfunc.DBConnection.version (2.0.2):",
            "attrlis für linksw ist leer",
        )
        return False
    elif "elnam" not in attrlis:
        logger.debug("linksw.elnam ist nicht in: %s", attrlis)
        if not dbcon.sql(
            "ALTER TABLE linksw ADD COLUMN elnam TEXT",
            "dbfunc.DBConnection.version (2.0.2-1)",
        ):
            return False
        dbcon.commit()

    attrlis = dbcon.attrlist("linkfl")
    if not attrlis:
        fehlermeldung(
            "dbfunc.DBConnection.version (2.0.2):",
            "attrlis für linkfl ist leer",
        )
        return False
    elif "tezgnam" not in attrlis:
        logger.debug("linkfl.tezgnam ist nicht in: {}".format(str(attrlis)))
        if not dbcon.sql(
            "ALTER TABLE linkfl ADD COLUMN tezgnam TEXT",
            "dbfunc.DBConnection.version (2.0.2-3)",
        ):
            return False
        dbcon.commit()

    return True
