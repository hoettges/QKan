import logging
import os
import csv
from qgis.utils import pluginDirectory

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.18"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:

    # Tabelle mit SQL-Abfragen

    sql =  "ALTER TABLE haltungen_untersucht ADD COLUMN datenart TEXT",
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False
    dbcon.commit()

    # Tabelle mit SQL-Abfragen

    sql ="ALTER TABLE schaechte_untersucht ADD COLUMN datenart TEXT",
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False
    dbcon.commit()

    sql = """
                    CREATE TABLE IF NOT EXISTS reflist_zustand (
                        pk INTEGER PRIMARY KEY,
                        art TEXT,                      -- 
                        hauptcode TEXT,                -- 
                        charakterisierung1 TEXT,        --
                        charakterisierung2 TEXT,         -- 
                        bereich TEXT        -- 
                        )
                """

    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False

    reflist_zustandfile = os.path.join(pluginDirectory("qkan"), "database", "Plausi_Zustandsklassen.csv")

    with open(reflist_zustandfile, 'r') as fin:
        dr = csv.reader(fin, delimiter=";")
        to_db = [(i[0], i[1], i[2], i[3], i[4]) for i in dr]

    cursl = dbcon.cursor()
    cursl.executemany(
        "INSERT INTO reflist_zustand (art, hauptcode, charakterisierung1, charakterisierung2, bereich) VALUES (?, ?, ?, ?, ?);",
        to_db)
    dbcon.commit()


    return True
