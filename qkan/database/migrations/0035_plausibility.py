import logging

from qkan.database.dbfunc import DBConnection
from qkan.tools.k_layersadapt import load_plausisql

VERSION = "3.3.6"              # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Zusätzliche Tabelle Notizen
    :type dbcon:    DBConnection
    """

    if not load_plausisql(dbcon):
        logger.error("Fehler in migration 0035_plausibility")
        return False
    return True
