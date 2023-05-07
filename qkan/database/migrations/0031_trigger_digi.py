import logging
import os

from qkan.database.dbfunc import DBConnection
from qgis.utils import pluginDirectory

VERSION = "3.2.37"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Trigger zur automatischen Datenübernahme bei der Erstellung und 
    Bearbeitung von Haltungsgeometrien"""

    # Datei mit SQL-Abfragen ausführen
    sql_file =os.path.join(pluginDirectory("qkan"), 'database/triggers', 'haltungen.sql')

    if not dbcon.executefile(sql_file):
        logger.debug(f"Fehler bei Migration zu Version {VERSION}, SQL-Nr. {i}")
        return False

    dbcon.commit()
    return True
