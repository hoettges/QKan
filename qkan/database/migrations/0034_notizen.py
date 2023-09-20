import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.41"              # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliche Tabelle Notizen

    sql = """
        CREATE TABLE IF NOT EXISTS notizen (
            pk INTEGER PRIMARY KEY,
            notiz TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP)
        """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.2.41)"):
        return False

    sql = f"""
        SELECT AddGeometryColumn('notizen','geom',{dbcon.epsg},'POINT',2)
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.2.41)"):
        return False

    dbcon.commit()  # Wurde schon durchgeführt

    return True
