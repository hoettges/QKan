from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger
from qgis.utils import pluginDirectory
import os

VERSION = "3.4.3"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Korrektur der Trigger für einige Referenztabellen

    sqls = [
        "DROP TRIGGER IF EXISTS trig_ref_profile",
        "DROP TRIGGER IF EXISTS trig_ref_entwart",
        "DROP TRIGGER IF EXISTS trig_ref_simstatus",
        "DROP TRIGGER IF EXISTS trig_ref_material",
    ]

    for sql in sqls:
        if not dbcon.sql(sql, f"migration 0039, Version {VERSION}: "
                              f"Korrektur der Trigger für einige Referenztabellen"):
            logger.error('Fehler in migration 0039')
            raise Exception(f"{__name__}")

    sql_file = os.path.join(pluginDirectory("qkan"), 'database/triggers', 'reftables.sql')
    try:
        dbcon.executefile(sql_file)
    except BaseException as err:
        logger.debug(f"Fehler in {__name__}.trigger reftables, {sql_file =}")
        return False

    dbcon.commit()

    return True
