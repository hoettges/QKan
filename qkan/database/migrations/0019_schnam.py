import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.1.3"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Flächen können auch an Schächte angeschlossen sein. Dies gilt bei
    # folgenden Programmen:
    # SWMM, Mike Urban

    if not dbcon.sql(
        "ALTER TABLE flaechen ADD COLUMN schnam TEXT",
        "dbfunc.DBConnection.version (3.1.3-1)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE tezg ADD COLUMN schnam TEXT",
        "dbfunc.DBConnection.version (3.1.3-2)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE tezg ADD COLUMN neigung REAL",
        "dbfunc.DBConnection.version (3.1.3-3)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE linkfl ADD COLUMN schnam TEXT",
        "dbfunc.DBConnection.version (3.1.3-4)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE linksw ADD COLUMN schnam TEXT",
        "dbfunc.DBConnection.version (3.1.3-5)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE einleit ADD COLUMN schnam TEXT",
        "dbfunc.DBConnection.version (3.1.3-6)",
    ):
        return False
    dbcon.commit()

    # Zusätzliche Parameter für SWMM
    if not dbcon.sql(
        "ALTER TABLE abflussparameter ADD COLUMN rauheit_kst REAL",
        "dbfunc.DBConnection.version (3.1.3-7)",
    ):
        return False
    dbcon.commit()

    if not dbcon.sql(
        "ALTER TABLE abflussparameter ADD COLUMN pctZero REAL",
        "dbfunc.DBConnection.version (3.1.3-8)",
    ):
        return False
    dbcon.commit()
    return True
