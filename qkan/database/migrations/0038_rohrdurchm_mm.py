from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger
from qgis.core import QgsProject
from qgis.utils import pluginDirectory
import os

VERSION = "3.3.9"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Zusätzliches Attribut bandnr in untersuchungsdaten

    # Umwandeln von Rohrhöhe und -breite auf mm
    sqls = [
        "UPDATE haltungen SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE haltungen SET breite = breite * 1000. WHERE breite < 15",
        "UPDATE haltungen SET aussendurchmesser = aussendurchmesser * 1000. WHERE aussendurchmesser < 15",
        "UPDATE haltungen_untersucht SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE haltungen_untersucht SET breite = breite * 1000. WHERE breite < 15",
        "UPDATE anschlussleitungen SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE anschlussleitungen SET breite = breite * 1000. WHERE breite < 15",
        "UPDATE anschlussleitungen_untersucht SET hoehe = hoehe * 1000. WHERE hoehe < 15",
        "UPDATE anschlussleitungen_untersucht SET breite = breite * 1000. WHERE breite < 15",
    ]
    for sql in sqls:
        if not dbcon.sql(sql, f"migration 0038, Version {VERSION}: "
                              f"Umwandeln der Rohrabmessungen von m in mm"):
            logger.error('Fehler in migration 0038')
            raise Exception(f"{__name__}")

    dbcon.commit()

    project = QgsProject.instance()
    layerobjects = project.mapLayersByName("Haltungen")
    for layer in layerobjects:

        stfile = os.path.join(
            pluginDirectory("qkan"), "database/migrations/haltungen_mm.qml"
        )
        try:
            layer.loadNamedStyle(stfile)
        except:
            logger.error('Fehler in migration 0038: Stildatei konnte nicht geladen werden.')
            raise Exception(f"{__name__}")

    logger.info('Die Projektdatei wurde angepasst: Im Layer "Haltungen" wurden die Einheiten von m auf mm umgestellt.'
        '\n\nBitte speichern Sie die Projektdatei!'
    )

    return True
