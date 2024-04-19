from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "2.2.0"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    attrlis = dbcon.attrlist("einleit")
    if not attrlis:
        return False
    elif "ew" not in attrlis:
        logger.debug("einleit.ew ist nicht in: {}".format(str(attrlis)))
        if not dbcon.sql(
            "ALTER TABLE einleit ADD COLUMN ew REAL",
            "dbfunc.DBConnection.version (2.1.2-1)",
        ):
            return False
        if not dbcon.sql(
            "ALTER TABLE einleit ADD COLUMN einzugsgebiet TEXT",
            "dbfunc.DBConnection.version (2.1.2-2)",
        ):
            return False
        dbcon.commit()

    sql = """
    CREATE TABLE IF NOT EXISTS einzugsgebiete (
        pk INTEGER PRIMARY KEY,
        tgnam TEXT,
        ewdichte REAL,
        wverbrauch REAL,
        stdmittel REAL,
        fremdwas REAL,
        kommentar TEXT,
        createdat TEXT DEFAULT CURRENT_DATE
    )
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.1.2-3)"):
        return False

    if not dbcon.sql(
        "SELECT AddGeometryColumn('einzugsgebiete','geom',?,'MULTIPOLYGON',2)",
        "dbfunc.DBConnection.version (2.1.2-4)",
        parameters=(dbcon.epsg,),
    ):
        return False

    if not dbcon.sql(
        "SELECT CreateSpatialIndex('einzugsgebiete','geom')",
        "dbfunc.DBConnection.version (2.1.2-5)",
    ):
        return False

    return True
