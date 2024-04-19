from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "2.5.7"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Tabelle linkfl um die Felder [abflusstyp, speicherzahl, speicherkonst,
    #                               fliesszeitkanal, fliesszeitflaeche]
    # erweitern. Wegen der Probleme mit der Anzeige in QGIS wird die Tabelle dazu umgespeichert.

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
            tezgnam TEXT
        )
        """,
        f"SELECT AddGeometryColumn('linkfl_t','geom',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linkfl_t','gbuf',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linkfl_t','glink',{dbcon.epsg},'LINESTRING',2)",
        "DELETE FROM linkfl_t;",
        """
        INSERT INTO linkfl_t 
            ("flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink")
        SELECT "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink"
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
        f"SELECT AddGeometryColumn('linkfl','geom',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linkfl','gbuf',{dbcon.epsg},'MULTIPOLYGON',2)",
        f"SELECT AddGeometryColumn('linkfl','glink',{dbcon.epsg},'LINESTRING',2)",
        "SELECT CreateSpatialIndex('linkfl','glink')",
        """
        INSERT INTO linkfl 
            ("flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink")
        SELECT "flnam", "haltnam", "tezgnam", "geom", "gbuf", "glink"
        FROM "linkfl_t"
        """,
        "SELECT DiscardGeometryColumn('linkfl_t','geom')",
        "SELECT DiscardGeometryColumn('linkfl_t','gbuf')",
        "SELECT DiscardGeometryColumn('linkfl_t','glink')",
        "DROP TABLE linkfl_t;",
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.7-1)"):
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

    # Oberflächenabflussdaten von Tabelle "flaechen" in Tabelle "linkfl" übertragen
    sql = """
    UPDATE linkfl SET 
        (abflusstyp, speicherzahl, speicherkonst, fliesszeitkanal, fliesszeitflaeche) =
        (
            SELECT abflusstyp, speicherzahl, speicherkonst, fliesszeitkanal, fliesszeit
            FROM flaechen
            WHERE linkfl.flnam = flaechen.flnam
        )
    """
    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.7-2)"):
        return False
    dbcon.commit()

    # Tabelle flaechen um die Felder [abflusstyp, speicherzahl, speicherkonst,
    #                                 fliesszeitkanal, fliesszeitflaeche]
    # bereinigen. Wegen der Probleme mit der Anzeige in QGIS wird die Tabelle dazu umgespeichert.

    # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
    # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='flaechen'"""
    # if not dbcon.sql(sql, 'dbfunc.DBConnection.version.pragma (5)'):
    # return False
    # triggers = dbcon.fetchall()

    # 2. Schritt: Temporäre Tabelle anlegen, Daten rüber kopieren,
    #             Tabelle löschen und wieder neu anlegen und Daten zurück kopieren

    sqllis = [
        "BEGIN TRANSACTION;",
        """
        CREATE TABLE IF NOT EXISTS flaechen_t (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,
            neigkl INTEGER DEFAULT 0,
            teilgebiet TEXT,
            regenschreiber TEXT,
            abflussparameter TEXT,
            aufteilen TEXT DEFAULT 'nein',
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE
        )
        """,
        f"SELECT AddGeometryColumn('flaechen_t','geom',{dbcon.epsg},'MULTIPOLYGON',2)",
        "DELETE FROM flaechen_t",
        """
        INSERT INTO flaechen_t 
            ("flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen",
            "kommentar", "createdat", "geom")
        SELECT "flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter",
                "aufteilen", "kommentar", "createdat", "geom"
        FROM "flaechen";
        """,
        "SELECT DiscardGeometryColumn('flaechen','geom')",
        "DROP TABLE flaechen;",
        """
        CREATE TABLE flaechen (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,
            neigkl INTEGER DEFAULT 0,
            teilgebiet TEXT,
            regenschreiber TEXT,
            abflussparameter TEXT,
            aufteilen TEXT DEFAULT 'nein',
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE
        )
        """,
        f"SELECT AddGeometryColumn('flaechen','geom',{dbcon.epsg},'MULTIPOLYGON',2)",
        "SELECT CreateSpatialIndex('flaechen','geom')",
        """
        INSERT INTO flaechen 
            ("flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter", 
            "aufteilen", "kommentar", "createdat", "geom")
        SELECT "flnam", "haltnam", "neigkl", "teilgebiet", "regenschreiber", "abflussparameter", 
                "aufteilen", "kommentar", "createdat", "geom"
        FROM "flaechen_t";
        """,
        "SELECT DiscardGeometryColumn('flaechen_t','geom')",
        "DROP TABLE flaechen_t;",
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.7-3)"):
            return False

    # 3. Schritt: Trigger wieder herstellen
    # for el in triggers:
    # if el[0] != 'table':
    # sql = el[1]
    # logger.debug("Trigger 'flaechen' verarbeitet:\n{}".format(el[1]))
    # if not dbcon.sql(sql, 'dbfunc.DBConnection.version (2.2.2-7)'):
    # return False
    # else:
    # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

    # 4. Schritt: Transaction abschließen
    dbcon.commit()

    dbcon.reload = True
    return True
