import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.2.16"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    sql = """
        CREATE TABLE IF NOT EXISTS dynahal (
            pk INTEGER PRIMARY KEY,
            haltnam TEXT,
            schoben TEXT,
            schunten TEXT,
            teilgebiet TEXT,
            kanalnummer TEXT,
            haltungsnummer TEXT,
            anzobob INTEGER,
            anzobun INTEGER,
            anzunun INTEGER,
            anzunob INTEGER
        )
        """
    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.4.1-1)"):
        return False

    if not dbcon.sql(
        "ALTER TABLE profile ADD COLUMN kp_key TEXT",
        "dbfunc.DBConnection.version (2.4.1-3)",
    ):
        return False

    if not dbcon.sql(
        "ALTER TABLE entwaesserungsarten ADD COLUMN kp_nr INTEGER",
        "dbfunc.DBConnection.version (2.4.1-2)",
    ):
        return False

    sqllis = [
        "UPDATE entwaesserungsarten SET kp_nr = 0 WHERE bezeichnung = 'Mischwasser';",
        "UPDATE entwaesserungsarten SET kp_nr = 1 WHERE bezeichnung = 'Schmutzwasser';",
        "UPDATE entwaesserungsarten SET kp_nr = 2 WHERE bezeichnung = 'Regenwasser';",
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.4.1-4)"):
            return False

    dbcon.commit()
    return True
