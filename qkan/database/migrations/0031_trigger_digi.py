import os

from qgis.utils import pluginDirectory

from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.2.37"  # must be higher than previous one

logger = get_logger("QKan.database.migrations")


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
