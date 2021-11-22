import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.18"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Ergänze Views für Flächenimport aus DYNA"""

    # Tabelle mit SQL-Abfragen

    return True
