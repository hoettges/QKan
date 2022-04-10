import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.29"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Ergänze verschiedene Haltungstypen, die alle in der Tabelle haltungen gespeichert werden.
    """

    # Attribute sonderelement und material in Tabelle haltungen ergänzen

    attrlis = dbcon.attrlist("haltungen")
    if not attrlis:
        logger.error(
            f"Fehler 1 bei Migration zu Version {VERSION}: "
            "attrlis für pumpen ist leer"
        )
        return False

    if not dbcon.alter_table(
        "haltungen",
        [
            "haltnam TEXT",
            "schoben TEXT",
            "schunten TEXT",
            "hoehe REAL",
            "breite REAL",
            "laenge REAL",
            "sohleoben REAL",
            "sohleunten REAL",
            "teilgebiet TEXT",
            "qzu REAL",
            "profilnam TEXT DEFAULT 'Kreisquerschnitt'",
            "entwart TEXT DEFAULT 'Regenwasser'",
            "material TEXT",
            "ks REAL DEFAULT 1.5",
            "sonderelement TEXT",
            "simstatus TEXT DEFAULT 'vorhanden'",
            "kommentar TEXT",
            "createdat TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))",
            "xschob REAL",
            "yschob REAL",
            "xschun REAL",
            "yschun REAL",
        ],
        [   "deckeloben REAL",
            "deckelunten REAL",
        ],
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Hinzufügen von sonderelement und material zu Tabelle haltungen fehlgeschlagen"
        )

    # Daten von Wehren und Pumpen in Tabelle 'haltungen' als Sonderelemente übertragen
    sqllis = [
        """INSERT INTO haltungen (
            haltnam, schoben, schunten,
            hoehe,
            sonderelement, 
            simstatus,
            kommentar, createdat, 
            geom)
        SELECT 
            pnam AS haltnam, 
            schoben, schunten,
            0.3 AS hoehe,                   /* nur fuer Laengsschnitt */
            'Pumpe' AS sonderelement,
            simstatus,
            kommentar, createdat, 
            geom
            FROM pumpen
        """,
        """INSERT INTO haltungen (
            haltnam, schoben, schunten,
            hoehe,
            sohleoben, sohleunten,
            sonderelement, 
            simstatus,
            kommentar, createdat, 
            geom)
        SELECT 
            wnam AS haltnam, 
            schoben, schunten,
            0.5 AS hoehe,                   /* nur fuer Laengsschnitt */
            schwellenhoehe AS sohleoben,    /* nur fuer Laengsschnitt */
            schwellenhoehe AS sohleunten,   /* nur fuer Laengsschnitt */
            'Wehr' AS sonderelement,
            simstatus,
            kommentar, createdat, 
            geom
            FROM wehre
        """,
    ]
    for sql in sqllis:
        if not dbcon.sql(sql):
            logger.error(f"Fehler 2 bei Migration zu Version {VERSION}")
            return False

    sql = "DELETE FROM abflusstypen WHERE abflusstyp IN ('Direktabfluss', 'Schwerpunktfließzeit')"
    if not dbcon.sql(sql):
        logger.error(f"Fehler 3 bei Migration zu Version {VERSION}")
        return False

    dbcon.commit()
    return True
