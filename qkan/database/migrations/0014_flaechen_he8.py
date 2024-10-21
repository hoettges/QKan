import packaging.version

from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.0.2"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    #  Temporäre Tabelle zum Export von Flächen für HE 8 -----------------------------

    sql = """
    CREATE TABLE IF NOT EXISTS flaechen_he8 (
        pk INTEGER PRIMARY KEY,
        Name TEXT, 
        Haltung TEXT, 
        Groesse REAL, 
        Regenschreiber TEXT, 
        BerechnungSpeicherkonstante INTEGER, 
        Typ INTEGER, 
        AnzahlSpeicher INTEGER, 
        Speicherkonstante REAL, 
        Schwerpunktlaufzeit REAL, 
        FliesszeitOberflaeche REAL, 
        LaengsteFliesszeitKanal REAL, 
        Parametersatz TEXT, 
        Neigungsklasse INTEGER, 
        ZuordnUnabhEZG INTEGER,
        LastModified TEXT DEFAULT (datetime('now')), 
        Kommentar TEXT
    )
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.2-1)"):
        return False

    # Ab Version 3.0.5 nochmal geändert
    if dbcon.current_dbversion < packaging.version.parse("3.0.5"):
        if not dbcon.sql(
            f"""
            SELECT AddGeometryColumn('flaechen_he8', 'Geometry', 
            {dbcon.epsg},'MULTIPOLYGON',2)
            """,
            "dbfunc.DBConnection.version (3.0.2-2)",
        ):
            return False
    else:
        if not dbcon.sql(
            f"""
            SELECT AddGeometryColumn('flaechen_he8', 
            'Geometry', -1, 'MULTIPOLYGON',2)
            """,
            "dbfunc.DBConnection.version (3.0.2-3)",
        ):
            return False

    if not dbcon.sql(
        "SELECT CreateSpatialIndex('flaechen_he8','Geometry')",
        "dbfunc.DBConnection.version (3.0.2-4)",
    ):
        return False

    # Erweitern der Tabelle "abflusstypen"

    sqllis = [
        "ALTER TABLE abflusstypen ADD COLUMN he_nr INTEGER",
        "ALTER TABLE abflusstypen ADD COLUMN kp_nr INTEGER",
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.2-5)"):
            return False

    # Initialisierung

    daten = [
        "'Speicherkaskade', 0, 0",
        "'Direktabfluss', 0, 0",
        "'Fliesszeiten', 1, 1",
        "'Schwerpunktlaufzeit', 2, 2",
        "'Schwerpunktfließzeit', 2, 2",
    ]

    for ds in daten:
        sql = f"""INSERT INTO abflusstypen
                                 (abflusstyp, he_nr, kp_nr) Values ({ds})"""
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.2-6)"):
            return False

    dbcon.commit()
    return True
