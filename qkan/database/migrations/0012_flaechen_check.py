import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.5.27"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Vergleich der Flächengröße mit der Summe der verschnittenen Teile

    if not dbcon.sql(
        'DROP VIEW IF EXISTS "v_flaechen_check"',
        "dbfunc.DBConnection.version (2.5.24-1)",
    ):
        return False

    sql = """
    CREATE VIEW IF NOT EXISTS "v_flaechen_check" AS 
    WITH flintersect AS (
        SELECT fl.flnam AS finam, 
               CASE WHEN (fl.aufteilen <> 'ja' AND not fl.aufteilen) OR fl.aufteilen IS NULL THEN area(fl.geom) 
               ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
               END AS flaeche
        FROM linkfl AS lf
        INNER JOIN flaechen AS fl
        ON lf.flnam = fl.flnam
        LEFT JOIN tezg AS tg
        ON lf.tezgnam = tg.flnam)
    SELECT fa.flnam, fi.finam, sum(fi.flaeche) AS fl_int, 
           AREA(fa.geom) AS fl_ori, sum(fi.flaeche) - AREA(fa.geom) AS diff
    FROM flaechen AS fa
    LEFT JOIN flintersect AS fi
    ON fa.flnam = fi.finam
    GROUP BY fa.flnam
    HAVING ABS(sum(fi.flaeche) - AREA(fa.geom)) > 2
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.24-2)"):
        return False

    # Vergleich der Haltungsflächengrößen mit der Summe der verschnittenen Teile
    if not dbcon.sql(
        'DROP VIEW IF EXISTS "v_tezg_check"',
        "dbfunc.DBConnection.version (2.5.24-3)",
    ):
        return False

    sql = """
    CREATE VIEW IF NOT EXISTS "v_tezg_check" AS 
    WITH flintersect AS (
        SELECT tg.flnam AS finam, 
               CASE WHEN (fl.aufteilen <> 'ja' AND not fl.aufteilen) OR fl.aufteilen IS NULL THEN area(fl.geom) 
               ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
               END AS flaeche
        FROM linkfl AS lf
        INNER JOIN flaechen AS fl
        ON lf.flnam = fl.flnam
        LEFT JOIN tezg AS tg
        ON lf.tezgnam = tg.flnam)
    SELECT tg.flnam, fi.finam, sum(fi.flaeche) AS fl_int, 
           AREA(tg.geom) AS fl_ori, sum(fi.flaeche) - AREA(tg.geom) AS diff
    FROM tezg AS tg
    LEFT JOIN flintersect AS fi
    ON tg.flnam = fi.finam
    GROUP BY tg.flnam
    HAVING ABS(sum(fi.flaeche) - AREA(tg.geom)) > 2
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.24-4)"):
        return False

    dbcon.commit()
    return True
