from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.0.5"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut flaechentyp in abflussfaktoren
    if not dbcon.sql(
        "ALTER TABLE abflussparameter ADD COLUMN flaechentyp TEXT",
        "dbfunc.DBConnection.version (3.0.5-1)",
    ):
        return False

    # Initialisierung
    for nam, typ in [
        ["$Default_Unbef", "Grünfläche"],
        ["Gebäude", "Gebäude"],
        ["Straße", "Straße"],
        ["Grünfläche", "Grünfläche"],
        ["Gewässer", "Gewässer"],
    ]:
        if not dbcon.sql(
            "UPDATE abflussparameter SET flaechentyp = ? WHERE apnam = ?",
            "dbfunc.DBConnection.version (3.0.5-2)",
            parameters=(typ, nam),
        ):
            return False

    # Neue Tabelle "flaechentypen"
    sql = """
    CREATE TABLE IF NOT EXISTS flaechentypen (
        pk INTEGER PRIMARY KEY,
        bezeichnung TEXT,
        he_nr INTEGER
    )
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.5-3)"):
        return False

    # Initialisierung
    for bez, num in [
        ["Gebäude", 0],
        ["Straße", 1],
        ["Grünfläche", 2],
        ["Gewässer", 3],
    ]:
        if not dbcon.sql(
            "INSERT INTO flaechentypen (bezeichnung, he_nr) Values (?, ?)",
            "dbfunc.DBConnection.version (3.0.5-4)",
            parameters=[bez, num],
        ):
            return False

    # Zusätzliche Attribute flaechen_he8
    attrlis = [
        "Flaechentyp INTEGER",
        "IstPolygonalflaeche INTEGER",
        "ZuordnungGesperrt INTEGER",
    ]

    for attr in attrlis:
        if not dbcon.sql(
            f"ALTER TABLE flaechen_he8 ADD COLUMN {attr}",
            "dbfunc.DBConnection.version (3.0.5-5)",
        ):
            return False

    # Änderung des EPSG-Codes in flaechen_he8 auf -1
    sqllis = [
        "SELECT DiscardGeometryColumn('flaechen_he8', 'Geometry')",
        "SELECT UpdateLayerStatistics('flaechen_he8')",
        "SELECT AddGeometryColumn('flaechen_he8', 'geom', -1, 'MULTIPOLYGON', 2)",
        "SELECT CreateSpatialIndex('flaechen_he8', 'geom')",
    ]

    # "SELECT DisableSpatialIndex('flaechen_he8', 'Geometry')",
    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (3.0.5-6)"):
            return False
        dbcon.commit()

    dbcon.commit()  # Wurde schon durchgeführt
    return True
