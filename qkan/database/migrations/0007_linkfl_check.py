import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.4.9"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    if not dbcon.sql(
        'DROP VIEW IF EXISTS "v_linkfl_check"',
        "dbfunc.DBConnection.version (2.4.9-1)",
    ):
        return False

    sql = """
    CREATE VIEW IF NOT EXISTS "v_linkfl_check" AS 
    WITH lfok AS
    (
        SELECT 
                lf.pk AS "pk",
                lf.flnam AS "linkfl_nam", 
                lf.haltnam AS "linkfl_haltnam", 
                fl.flnam AS "flaech_nam",
                tg.flnam AS "tezg_nam",
                min(lf.pk) AS pkmin, 
                max(lf.pk) AS pkmax,
                count(*) AS anzahl
        FROM linkfl AS lf
        LEFT JOIN flaechen AS fl
        ON lf.flnam = fl.flnam
        LEFT JOIN tezg AS tg
        ON lf.tezgnam = tg.flnam
        WHERE fl.aufteilen = "ja" and fl.aufteilen IS NOT NULL
        GROUP BY fl.flnam, tg.flnam
        UNION
        SELECT 
            lf.pk AS "pk",
            lf.flnam AS "linkfl_nam", 
            lf.haltnam AS "linkfl_haltnam", 
            fl.flnam AS "flaech_nam",
            NULL AS "tezg_nam",
            min(lf.pk) AS pkmin, 
            max(lf.pk) AS pkmax,
            count(*) AS anzahl
        FROM linkfl AS lf
        LEFT JOIN flaechen AS fl
        ON lf.flnam = fl.flnam
        WHERE fl.aufteilen <> "ja" OR fl.aufteilen IS NULL
        GROUP BY fl.flnam
    )
    SELECT pk, anzahl, CASE 
            WHEN anzahl > 1 THEN 'mehrfach vorhanden'
            WHEN flaech_nam IS NULL THEN 'Keine Fläche'
            WHEN linkfl_haltnam IS NULL THEN  'Keine Haltung' ELSE 'o.k.'
        END AS fehler
    FROM lfok
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.4.9-2)"):
        return False

    if not dbcon.sql(
        'DROP VIEW IF EXISTS "v_flaechen_ohne_linkfl"',
        "dbfunc.DBConnection.version (2.4.9-3)",
    ):
        return False

    sql = """
        CREATE VIEW IF NOT EXISTS "v_flaechen_ohne_linkfl" AS 
        SELECT
            fl.pk,
            fl.flnam AS "flaech_nam",
            fl.aufteilen AS "flaech_aufteilen",
            'Verbindung fehlt' AS "Fehler"
        FROM flaechen AS fl
        LEFT JOIN linkfl AS lf
        ON lf.flnam = fl.flnam
        LEFT JOIN tezg AS tg
        ON tg.flnam = lf.tezgnam
        WHERE (
            (fl.aufteilen <> "ja" or fl.aufteilen IS NULL) AND lf.pk IS NULL)
            OR
            (fl.aufteilen = "ja" AND fl.aufteilen IS NOT NULL AND lf.pk IS NULL)
        UNION
        VALUES
            (0, '', '', 'o.k.')
        """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.4.9-4)"):
        return False

    dbcon.commit()
    return True
