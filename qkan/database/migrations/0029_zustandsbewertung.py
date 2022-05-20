import logging
import os
import csv
from qgis.utils import pluginDirectory

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.18"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:

    # Tabelle mit SQL-Abfragen
    sql = "ALTER TABLE haltungen ADD COLUMN strasse TEXT",
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False
    dbcon.commit()

    sql =  "ALTER TABLE haltungen_untersucht ADD COLUMN max_ZD INTEGER, ADD COLUMN max_ZB INTEGER, ADD COLUMN max_ZS INTEGER, ADD COLUMN strasse TEXT",
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False
    dbcon.commit()

    # Tabelle mit SQL-Abfragen

    sql ="ALTER TABLE schaechte_untersucht ADD COLUMN max_ZD INTEGER, ADD COLUMN max_ZB INTEGER, ADD COLUMN max_ZS INTEGER, ADD COLUMN strasse TEXT",
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False
    dbcon.commit()

    sql = "ALTER TABLE untersuchdat_schaechte ADD COLUMN ZD INTEGER, ADD COLUMN ZB INTEGER, ADD COLUMN ZS INTEGER",
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False
    dbcon.commit()

    sql = "ALTER TABLE untersuchdat_haltungen ADD COLUMN ZD INTEGER, ADD COLUMN ZB INTEGER, ADD COLUMN ZS INTEGER",
    if not dbcon.sql(sql):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}")
        return False
    dbcon.commit()



    return True
