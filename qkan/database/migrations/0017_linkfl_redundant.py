from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.0.10"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    if not dbcon.sql(
        'DROP VIEW IF EXISTS "v_linkfl_redundant"',
        "dbfunc.DBConnection.version (3.0.10-1)",
    ):
        return False

    sql = """
    CREATE VIEW IF NOT EXISTS "v_linkfl_redundant" AS 
    WITH lfm AS (
        SELECT flnam, tezgnam, count(*) AS anz
        FROM linkfl AS lf
        GROUP BY flnam, tezgnam)
    SELECT lf.pk, lf.flnam, lf.tezgnam, lfm.anz
    FROM linkfl AS lf
    LEFT JOIN lfm
    ON lf.flnam = lfm.flnam and lf.tezgnam = lfm.tezgnam
    WHERE anz <> 1 or lf.flnam IS NULL
    ORDER BY lf.flnam
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.10-2)"):
        return False

    if not dbcon.sql(
        'DROP VIEW IF EXISTS "v_linksw_redundant"',
        "dbfunc.DBConnection.version (3.0.10-3)",
    ):
        return False

    sql = """
    CREATE VIEW IF NOT EXISTS "v_linksw_redundant" AS 
    WITH lsm AS (
        SELECT elnam, count(*) AS anz
        FROM linksw AS ls
        GROUP BY elnam)
    SELECT ls.pk, ls.elnam, lsm.anz
    FROM linksw AS ls
    LEFT JOIN lsm
    ON ls.elnam = lsm.elnam
    WHERE anz <> 1 or ls.elnam IS NULL
    ORDER BY ls.elnam
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.10-4)"):
        return False

    dbcon.commit()
    return True
