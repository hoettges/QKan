import os

from qgis.core import Qgis, QgsMessageLog
from qgis.utils import iface, pluginDirectory

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import get_database_QKan, warnung
from qkan.tools.application import QKanTools
from qkan.tools.k_layersadapt import layersadapt
from qkan.utils import get_logger


def initQKanProject():
    """Update tables to actual version if necessary"""
    try:
        logger = get_logger("QKan.openproject")
        logger.debug("openProjekt started\n")
        database_qkan, _ = get_database_QKan(silent=True)
        db_qkan = DBConnection(dbname=database_qkan)
        is_actual = db_qkan.isCurrentVersion
        if not is_actual:
            qkt = QKanTools(QKan.instance.iface)
            warnung(
                "Versionskontrolle",
                "Die Datenbank muss aktualisiert werden!",
                duration=5,
            )
            qkt.run_dbAdapt()
    except ImportError:
        import traceback

        traceback.print_exc()
        msg = "Diese Projektdatei wurde mit dem Programm QKan (Prof. Höttges, FH Aachen) erstellt."
        QgsMessageLog.logMessage(
            message=msg,
            level=Qgis.Info,
        )
        iface.messageBar().pushMessage("Information", msg, level=Qgis.Info)

    projectTemplate = os.path.join(pluginDirectory("qkan"), "templates/Projekt.qgs")
    layersadapt(
        database_QKan=None,
        projectTemplate=projectTemplate,
        anpassen_ProjektMakros=False,
        anpassen_Datenbankanbindung=False,
        anpassen_Layerstile=False,
        anpassen_Formulare=True,
        anpassen_Projektionssystem=False,
        aktualisieren_Schachttypen=False,
        zoom_alles=False,
        fehlende_layer_ergaenzen=False,
        anpassen_auswahl=enums.SelectedLayers.ALL,
    )
