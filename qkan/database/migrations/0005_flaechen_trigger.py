import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.2.3"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Tabelle flaechen -------------------------------------------------------------

    # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
    # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='flaechen'"""
    # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (1)'):
    # return False
    # triggers = self.fetchall()

    # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
    sqllis = [
        "BEGIN TRANSACTION;",
        """
        CREATE TABLE IF NOT EXISTS flaechen_t (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,
            neigkl INTEGER DEFAULT 0,
            abflusstyp TEXT, 
            he_typ INTEGER DEFAULT 0,
            speicherzahl INTEGER DEFAULT 2,
            speicherkonst REAL,
            fliesszeit REAL,
            fliesszeitkanal REAL,
            teilgebiet TEXT,
            regenschreiber TEXT,
            abflussparameter TEXT,
            aufteilen TEXT DEFAULT 'nein',
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE
        )
        """,
        f"SELECT AddGeometryColumn('flaechen_t','geom',{dbcon.epsg},'MULTIPOLYGON',2);",
        "DELETE FROM flaechen_t",
        """
        INSERT INTO flaechen_t 
            (
            "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit",
            "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", 
            "kommentar", "createdat", "geom"
            )
        SELECT "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", 
                "fliesszeit", "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", 
                "aufteilen", "kommentar", "createdat", "geom"
        FROM "flaechen"
        """,
        "SELECT DiscardGeometryColumn('flaechen','geom');",
        "DROP TABLE flaechen;",
        """
        CREATE TABLE flaechen (
            pk INTEGER PRIMARY KEY,
            flnam TEXT,
            haltnam TEXT,
            neigkl INTEGER DEFAULT 0,
            abflusstyp TEXT, 
            he_typ INTEGER DEFAULT 0,
            speicherzahl INTEGER DEFAULT 2,
            speicherkonst REAL,
            fliesszeit REAL,
            fliesszeitkanal REAL,
            teilgebiet TEXT,
            regenschreiber TEXT,
            abflussparameter TEXT,
            aufteilen TEXT DEFAULT 'nein',
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE
        )
        """,
        f"SELECT AddGeometryColumn('flaechen','geom',{dbcon.epsg},'MULTIPOLYGON',2);",
        "SELECT CreateSpatialIndex('flaechen','geom');",
        """
        INSERT INTO flaechen 
            (
                "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", "fliesszeit",
                "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", "aufteilen", 
                "kommentar", "createdat", "geom"
            )
        SELECT "flnam", "haltnam", "neigkl", "he_typ", "speicherzahl", "speicherkonst", 
                "fliesszeit", "fliesszeitkanal", "teilgebiet", "regenschreiber", "abflussparameter", 
                "aufteilen", "kommentar", "createdat", "geom"
        FROM "flaechen_t"
        """,
        "SELECT DiscardGeometryColumn('flaechen_t','geom');",
        "DROP TABLE flaechen_t;",
    ]

    for sql in sqllis:
        if not dbcon.sql(
            sql, "dbfunc.DBConnection.version (2.2.2-1)", transaction=True
        ):
            return False

    # 3. Schritt: Trigger wieder herstellen
    # for el in triggers:
    # if el[0] != 'table':
    # sql = el[1]
    # logger.debug("Trigger 'flaechen' verarbeitet:\n{}".format(el[1]))
    # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-2)', transaction=True):
    # return False
    # else:
    # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

    # 4. Schritt: Transaction abschließen
    dbcon.commit()

    # 5. Schritt: Spalte abflusstyp aus Spalte he_typ übertragen
    if not dbcon.sql(
        """
        UPDATE flaechen SET abflusstyp = 
        CASE he_typ 
            WHEN 0 THEN 'Direktabfluss' 
            WHEN 1 THEN 'Fließzeiten' 
            WHEN 2 THEN 'Schwerpunktfließzeit'
        ELSE NULL END
        WHERE abflusstyp IS NULL
        """,
        "dbfunc.DBConnection.version (2.2.2-3)",
    ):
        return False

    # Tabelle linksw -------------------------------------------------------------

    # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
    # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linksw'"""
    # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (3)'):
    # return False
    # triggers = self.fetchall()

    # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
    # 14.10.2018: Unklar, warum überhaupt. Es findet keine Änderung statt. Möglicherweise
    # muss hier eine händische Änderung "eingefangen werden".
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
        "DELETE FROM linksw_t;",
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
        "SELECT CreateSpatialIndex('linksw','geom')",
        """
        INSERT INTO linksw 
            ("elnam", "haltnam", "geom", "gbuf", "glink")
        SELECT "elnam", "haltnam", "geom", "gbuf", "glink"
        FROM "linksw_t"
        """,
        "SELECT DiscardGeometryColumn('linksw_t','geom')",
        "SELECT DiscardGeometryColumn('linksw_t','gbuf')",
        "SELECT DiscardGeometryColumn('linksw_t','glink')",
        "DROP TABLE linksw_t;",
    ]

    for sql in sqllis:
        if not dbcon.sql(
            sql, "dbfunc.DBConnection.version (2.2.2-4)", transaction=True
        ):
            return False

    # 3. Schritt: Trigger wieder herstellen
    # for el in triggers:
    # if el[0] != 'table':
    # sql = el[1]
    # logger.debug("Trigger 'linksw' verarbeitet:\n{}".format(el[1]))
    # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-5)', transaction=True):
    # return False
    # else:
    # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

    # 4. Schritt: Transaction abschließen
    dbcon.commit()

    # Tabelle linkfl -------------------------------------------------------------

    # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
    # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='linkfl'"""
    # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (5)'):
    # return False
    # triggers = self.fetchall()

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
        "DELETE FROM linkfl_t",
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
            teilgebiet TEXT
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
        if not dbcon.sql(
            sql, "dbfunc.DBConnection.version (2.2.2-6)", transaction=True
        ):
            return False

    # 3. Schritt: Trigger wieder herstellen
    # for el in triggers:
    # if el[0] != 'table':
    # sql = el[1]
    # logger.debug("Trigger 'linkfl' verarbeitet:\n{}".format(el[1]))
    # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-7)', transaction=True):
    # return False
    # else:
    # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

    # 4. Schritt: Transaction abschließen
    dbcon.commit()

    # Tabelle einleit -------------------------------------------------------------

    # 1. Schritt: Trigger für zu ändernde Tabelle abfragen und in triggers speichern
    # sql = """SELECT type, sql FROM sqlite_master WHERE tbl_name='einleit'"""
    # if not self.sql(sql, 'dbfunc.DBConnection.version.pragma (7)'):
    # return False
    # triggers = self.fetchall()

    # 2. Schritt: Tabelle umbenennen, neu anlegen und Daten rüberkopieren
    sqllis = [
        "BEGIN TRANSACTION;",
        """
        CREATE TABLE IF NOT EXISTS einleit_t (
            pk INTEGER PRIMARY KEY,
            elnam TEXT,
            haltnam TEXT,
            teilgebiet TEXT, 
            zufluss REAL,
            ew REAL,
            einzugsgebiet TEXT,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE
        )
        """,
        f"SELECT AddGeometryColumn('einleit_t','geom',{dbcon.epsg},'POINT',2)",
        "DELETE FROM einleit_t;",
        """
        INSERT INTO einleit_t 
            ("elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", "createdat", 
            "geom")
        SELECT "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", 
                "createdat", "geom"
        FROM "einleit";
        """,
        "SELECT DiscardGeometryColumn('einleit','geom')",
        "DROP TABLE einleit;",
        """
        CREATE TABLE einleit (
            pk INTEGER PRIMARY KEY,
            elnam TEXT,
            haltnam TEXT,
            teilgebiet TEXT, 
            zufluss REAL,
            ew REAL,
            einzugsgebiet TEXT,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE
        )
        """,
        f"SELECT AddGeometryColumn('einleit','geom',{dbcon.epsg},'POINT',2)",
        "SELECT CreateSpatialIndex('einleit','geom')",
        """
        INSERT INTO einleit 
            ("elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", 
            "createdat", "geom")
        SELECT "elnam", "haltnam", "teilgebiet", "zufluss", "ew", "einzugsgebiet", "kommentar", 
                "createdat", "geom"
        FROM "einleit_t";
        """,
        """SELECT DiscardGeometryColumn('einleit_t','geom')""",
        """DROP TABLE einleit_t;""",
    ]

    for sql in sqllis:
        if not dbcon.sql(
            sql, "dbfunc.DBConnection.version (2.2.2-8)", transaction=True
        ):
            return False

    # 3. Schritt: Trigger wieder herstellen
    # for el in triggers:
    # if el[0] != 'table':
    # sql = el[1]
    # logger.debug("Trigger 'einleit' verarbeitet:\n{}".format(el[1]))
    # if not self.sql(sql, 'dbfunc.DBConnection.version (2.2.2-9)', transaction=True):
    # return False
    # else:
    # logger.debug("1. Trigger 'table' erkannt:\n{}".format(el[1]))

    # 4. Schritt: Transaction abschließen

    dbcon.commit()

    dbcon.reload = True
    return True
