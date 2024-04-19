import os

from qgis.utils import pluginDirectory

from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.2.31"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Plausibilitätsabfragen werden jetzt beim Anlegen einer neuen QKan-Datenbank eingefügt
    """

    plausisqlfile = os.path.join(pluginDirectory("qkan"), "templates", "plausibilitaetspruefungen.sql")
    if not dbcon.executefile(plausisqlfile):
        logger.error(f'Plausibilitätsabfragen konnten nicht gelesen oder '
                       f'ausgeführt werden:\n{plausisqlfile}\n')

    return True
