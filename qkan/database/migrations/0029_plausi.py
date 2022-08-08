import logging
import os
from qgis.utils import pluginDirectory

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.31"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Plausibilitätsabfragen werden jetzt beim Anlegen einer neuen QKan-Datenbank eingefügt
    """

    plausisqlfile = os.path.join(pluginDirectory("qkan"), "templates", "plausibilitaetspruefungen.sql")
    if not dbcon.executefile(plausisqlfile):
        logger.error(f'Plausibilitätsabfragen konnten nicht gelesen oder '
                       f'ausgeführt werden:\n{plausisqlfile}\n')

    return True
