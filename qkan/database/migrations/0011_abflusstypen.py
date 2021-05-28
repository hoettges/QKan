import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.5.9"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # ValueMaps durch RelationMaps ersetzen, weil die entsprechende Funktion
    # aus der QGIS-API in Python nicht gemappt ist, somit also in Python nicht verfügbar ist.
    # Deshalb werden nachfolgend drei Tabellen ergänzt. In der Projektdatei muss entsprechend
    # die Felddefinition angepasst werden.

    # 1. Tabelle abflusstypen

    sqllis = [
        """
        CREATE TABLE abflusstypen (
            pk INTEGER PRIMARY KEY, 
            abflusstyp TEXT
        )
        """,
        """
        INSERT INTO abflusstypen ('abflusstyp')
        VALUES
            ('Fliesszeiten'),
            ('Schwerpunktlaufzeit'),
            ('Speicherkaskade')
        """,
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.9) - abflusstypen"):
            return False
    dbcon.commit()

    # 2. Tabelle Knotentypen

    sqllis = [
        """
        CREATE TABLE knotentypen (
            pk INTEGER PRIMARY KEY, 
            knotentyp TEXT
        )
        """,
        """
        INSERT INTO knotentypen ('knotentyp') 
        VALUES
            ('Anfangsschacht'),
            ('Einzelschacht'),
            ('Endschacht'),
            ('Hochpunkt'),
            ('Normalschacht'),
            ('Tiefpunkt'),
            ('Verzweigung'),
            ('Fliesszeiten')
        """,
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.9) - knotentypen"):
            return False
    dbcon.commit()

    # 3. Tabelle Schachttypen

    sqllis = [
        """
        CREATE TABLE schachttypen (
            pk INTEGER PRIMARY KEY, 
            schachttyp TEXT
        )
        """,
        """
        INSERT INTO schachttypen ('schachttyp') 
        VALUES
            ('Auslass'),
            ('Schacht'),
            ('Speicher')
        """,
    ]

    for sql in sqllis:
        if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.9) - schachttypen"):
            return False
    dbcon.commit()
    return True
