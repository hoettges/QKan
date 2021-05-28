from qkan.database.dbfunc import DBConnection

VERSION = "2.0.2"


def run(dbcon: DBConnection) -> bool:
    # Tabelle einleit
    sqllis = [
        """
        CREATE TABLE IF NOT EXISTS einleit (
            pk INTEGER PRIMARY KEY,
            elnam TEXT,
            haltnam TEXT,
            teilgebiet TEXT, 
            zufluss REAL,
            kommentar TEXT,
            createdat TEXT DEFAULT CURRENT_DATE
        )
        """,
        f"SELECT AddGeometryColumn('einleit','geom',{dbcon.epsg},'POINT',2)",
        """SELECT CreateSpatialIndex('einleit','geom')""",
    ]
    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (3c)"):
            return False

    sqllis = [
        """
        CREATE TABLE IF NOT EXISTS linksw (
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
    ]
    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (3d)"):
            return False

    return True
