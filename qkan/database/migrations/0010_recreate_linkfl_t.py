import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.5.8"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Tabelle linkfl um das Feld teilgebiet erweitern.
    # Wegen der Probleme mit der Anzeige in QGIS wird die Tabelle dazu umgespeichert.

    # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
    # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linkfl'"""
    # if not dbcon.sql(sql, 'dbfunc.DBConnection.version.pragma (5)'):
    # return False
    # triggers = dbcon.fetchall()

    # 2. Schritt: Temporäre Tabelle anlegen, Daten rüber kopieren,
    #             Tabelle löschen und wieder neu anlegen und Daten zurück kopieren

    sqllis = [
        "BEGIN TRANSACTION;",
        """
        CREATE TABLE IF NOT EXISTS linkfl_t (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,
            tezgnam TEXT,
            abflusstyp TEXT,
            speicherzahl INTEGER,
            speicherkonst REAL,
            fliesszeitkanal REAL,
            fliesszeitflaeche REAL
        )
        """,
        f"SELECT AddGeometryColumn('linkfl_t','geom',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linkfl_t','gbuf',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linkfl_t','glink',{dbcon.epsg},'LINESTRING',2)",
        "DELETE FROM linkfl_t",
        """
        INSERT INTO linkfl_t 
            (
                "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
               "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
               "geom", "gbuf", "glink"
            )
        SELECT "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
               "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
               "geom", "gbuf", "glink"
        FROM "linkfl"
        """,
        "SELECT DiscardGeometryColumn('linkfl','geom')",
        "SELECT DiscardGeometryColumn('linkfl','gbuf')",
        "SELECT DiscardGeometryColumn('linkfl','glink')",
        "DROP TABLE linkfl;",
        """
        CREATE TABLE linkfl (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,
            tezgnam TEXT,
            teilgebiet TEXT,
            abflusstyp TEXT,
            speicherzahl INTEGER,
            speicherkonst REAL,
            fliesszeitkanal REAL,
            fliesszeitflaeche REAL
        )
        """,
        f"SELECT AddGeometryColumn('linkfl','geom',{dbcon.epsg},'MULTIPOLYGON',2)" "",
        f"SELECT AddGeometryColumn('linkfl','gbuf',{dbcon.epsg},'MULTIPOLYGON',2)" "",
        f"SELECT AddGeometryColumn('linkfl','glink',{dbcon.epsg},'LINESTRING',2)" "",
        "SELECT CreateSpatialIndex('linkfl','glink')",
        """
        INSERT INTO linkfl 
            (
                "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
                "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
                "geom", "gbuf", "glink"
            )
        SELECT "flnam", "haltnam", "tezgnam", "abflusstyp", "speicherzahl", 
               "speicherkonst", "fliesszeitkanal", "fliesszeitflaeche", 
               "geom", "gbuf", "glink"
        FROM "linkfl_t"
        """,
        "SELECT DiscardGeometryColumn('linkfl_t','geom')",
        "SELECT DiscardGeometryColumn('linkfl_t','gbuf')",
        "SELECT DiscardGeometryColumn('linkfl_t','glink')",
        "DROP TABLE linkfl_t;",
    ]

    for sql in sqllis:
        if not dbcon.sql(
            sql, "dbfunc.DBConnection.version (2.5.8-1)"
        ):
            return False

    # 3. Schritt: Trigger wieder herstellen
    # for el in triggers:
    # if el[0] != 'table':
    # sql = el[1]
    # logger.debug("Trigger 'linkfl' verarbeitet:\n{}".format(el[1]))
    # if not dbcon.sql(sql, 'dbfunc.DBConnection.version (2.2.2-7)'):
    # return False
    # else:
    # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

    # 4. Schritt: Transaction abschließen
    dbcon.commit()

    # Tabelle linksw -------------------------------------------------------------

    # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
    # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linksw'"""
    # if not dbcon.sql(sql, 'dbfunc.DBConnection.version.pragma (3)'):
    # return False
    # triggers = dbcon.fetchall()

    # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
    sqllis = [
        "BEGIN TRANSACTION;",
        """
        CREATE TABLE IF NOT EXISTS linksw_t (
            pk INTEGER PRIMARY KEY,
            elnam TEXT,
            haltnam TEXT
        )
        """,
        f"SELECT AddGeometryColumn('linksw_t','geom',{dbcon.epsg},'POLYGON',2)",
        f"SELECT AddGeometryColumn('linksw_t','gbuf',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linksw_t','glink',{dbcon.epsg},'LINESTRING',2)",
        "DELETE FROM linksw_t",
        """
        INSERT INTO linksw_t 
                ("elnam", "haltnam", "geom", "gbuf", "glink")
        SELECT "elnam", "haltnam", "geom", "gbuf", "glink"
        FROM "linksw"
        """,
        "SELECT DiscardGeometryColumn('linksw','geom')",
        "SELECT DiscardGeometryColumn('linksw','gbuf')",
        "SELECT DiscardGeometryColumn('linksw','glink')",
        "DROP TABLE linksw;",
        """
        CREATE TABLE linksw (
            pk INTEGER PRIMARY KEY,
            elnam TEXT,
            haltnam TEXT,
            teilgebiet TEXT
        )
        """,
        f"SELECT AddGeometryColumn('linksw','geom',{dbcon.epsg},'POLYGON',2)",
        f"SELECT AddGeometryColumn('linksw','gbuf',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linksw','glink',{dbcon.epsg},'LINESTRING',2)",
        """SELECT CreateSpatialIndex('linksw','geom')""",
        """
        INSERT INTO linksw 
            ("elnam", "haltnam", "geom", "gbuf", "glink")
        SELECT "elnam", "haltnam", "geom", "gbuf", "glink"
        FROM "linksw_t"
        """,
        "SELECT DiscardGeometryColumn('linksw_t','geom')",
        "SELECT DiscardGeometryColumn('linksw_t','gbuf')",
        "SELECT DiscardGeometryColumn('linksw_t','glink')",
        "DROP TABLE linksw_t;" "",
    ]

    for sql in sqllis:
        if not dbcon.sql(
            sql, "dbfunc.DBConnection.version (2.2.2-4)"
        ):
            return False

    # 3. Schritt: Trigger wieder herstellen
    # for el in triggers:
    # if el[0] != 'table':
    # sql = el[1]
    # logger.debug("Trigger 'linksw' verarbeitet:\n{}".format(el[1]))
    # if not dbcon.sql(sql, 'dbfunc.DBConnection.version (2.2.2-5)'):
    # return False
    # else:
    # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

    # 4. Schritt: Transaction abschließen
    dbcon.commit()

    dbcon.reload = True
    return True
