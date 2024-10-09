import os

from qgis.core import Qgis, QgsMessageLog, QgsSettings
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

        # Add QKan SVG path
        qkanSvgPath = os.path.join(pluginDirectory("qkan"), "templates/svg")
        svgPaths = QgsSettings().value('svg/searchPathsForSVG')
        if qkanSvgPath not in svgPaths:
            svgPaths.append(qkanSvgPath)
            QgsSettings().setValue('svg/searchPathsForSVG', svgPaths)

        # Set Identify Forms Option
        QgsSettings().setValue('Map/identifyAutoFeatureForm', 'true')
        QgsSettings().setValue('Map/identifyMode', 'LayerSelection')

        database_qkan, _ = get_database_QKan(silent=True)
        with DBConnection(dbname=database_qkan) as db_qkan:
            is_actual = db_qkan.isCurrentDbVersion
        if not is_actual:
            qkt = QKanTools(QKan.instance.iface)
            logger.warning(
                "Versionskontrolle: "
                "Die Datenbank muss aktualisiert werden!"
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
