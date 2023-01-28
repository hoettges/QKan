import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.5"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Typfehler in 'abflussparemeter.flaechentyp' korrigieren"""

    sqllis = [
        """
        CREATE TABLE IF NOT EXISTS abflussparameter_t (
        apnam TEXT, 
        anfangsabflussbeiwert REAL, 
        endabflussbeiwert REAL, 
        benetzungsverlust REAL, 
        muldenverlust REAL, 
        benetzung_startwert REAL, 
        mulden_startwert REAL, 
        rauheit_kst REAL,                       -- Rauheit Stricklerbeiwert = 1/n
        pctZero REAL,                           -- SWMM: % Zero-Imperv
        bodenklasse TEXT, 
        flaechentyp TEXT, 
        kommentar TEXT, 
        createdat TEXT DEFAULT (datetime('now')))""",
        "DELETE FROM abflussparameter_t",
        """
        INSERT INTO abflussparameter_t
            (
                apnam, 
                anfangsabflussbeiwert, endabflussbeiwert, 
                benetzungsverlust, muldenverlust, 
                benetzung_startwert, mulden_startwert, 
                rauheit_kst, pctZero, bodenklasse, flaechentyp, 
                kommentar, createdat
            )
        SELECT
            apnam, 
            anfangsabflussbeiwert, endabflussbeiwert, 
            benetzungsverlust, muldenverlust, 
            benetzung_startwert, mulden_startwert, 
            rauheit_kst, pctZero, bodenklasse, flaechentyp, 
            kommentar, createdat
        FROM abflussparameter
       """,
        "DROP TABLE abflussparameter",
        """CREATE TABLE abflussparameter (
            pk INTEGER PRIMARY KEY, 
            apnam TEXT, 
            anfangsabflussbeiwert REAL, 
            endabflussbeiwert REAL, 
            benetzungsverlust REAL, 
            muldenverlust REAL, 
            benetzung_startwert REAL, 
            mulden_startwert REAL, 
            rauheit_kst REAL,                       -- Rauheit Stricklerbeiwert = 1/n
            pctZero REAL,                           -- SWMM: % Zero-Imperv
            bodenklasse TEXT, 
            flaechentyp TEXT, 
            kommentar TEXT, 
            createdat TEXT DEFAULT (datetime('now')))""",
        """
        INSERT INTO abflussparameter
            (
                apnam, 
                anfangsabflussbeiwert, endabflussbeiwert, 
                benetzungsverlust, muldenverlust, 
                benetzung_startwert, mulden_startwert, 
                rauheit_kst, pctZero, bodenklasse, flaechentyp, 
                kommentar, createdat
            )
        SELECT
            apnam, 
            anfangsabflussbeiwert, endabflussbeiwert, 
            benetzungsverlust, muldenverlust, 
            benetzung_startwert, mulden_startwert, 
            rauheit_kst, pctZero, bodenklasse, flaechentyp, 
            kommentar, createdat
        FROM abflussparameter_t
       """,
        "DROP TABLE abflussparameter_t",
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.1.6)"):
            return False

    dbcon.commit()
    return True
