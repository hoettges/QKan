import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.41"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliche Tabelle Notizen

    sql = """
        CREATE TABLE IF NOT EXISTS notizen (
            pk INTEGER PRIMARY KEY,
            notiz TEXT,
            createdat TEXT DEFAULT CURRENT_TIMESTAMP),
        SELECT AddGeometryColumn('notiz','geop',{},'POINT',2)
        )
        """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.2.41)"):
        return False

    sql = """
            CREATE TABLE IF NOT EXISTS notizen_data (
                pk INTEGER PRIMARY KEY,
                notiz TEXT,
                createdat TEXT DEFAULT CURRENT_TIMESTAMP),
            SELECT AddGeometryColumn('notiz','geop',{},'POINT',2)
            )
            """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.2.41)"):
        return False

    dbcon.commit()  # Wurde schon durchgeführt
    return True
