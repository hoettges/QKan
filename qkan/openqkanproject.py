import os

from qgis.core import Qgis, QgsMessageLog, QgsProject
from qgis.utils import iface, pluginDirectory

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import get_database_QKan
from qkan.tools.k_layersadapt import layersadapt
from qkan.utils import get_logger

logger = get_logger("QKan.openproject")

def initQKanProject():
    """Update tables to actual version if necessary"""
    logger.debug("openProjekt started\n")

    try:
        _ = QKan.config.database.qkan                 # nur zum Test, ob QQKan geladen ist
    except:
        logger.debug(f'{id(QKan)=}')
        logger.error("QKan ist nicht aktiviert!")
        QgsMessageLog.logMessage(
            tag="QKan",
            message=f"QKan ist nicht aktiviert!"
        )
        iface.openMessageLog()

        iface.messageBar().pushMessage("QKan ist nicht aktiviert!", level=Qgis.MessageLevel.Warning)
        return

    # try:
    get_database_QKan(silent=True)
    database_name = QKan.config.database.qkan
    with DBConnection(dbname=database_name) as db_qkan:
        is_actual = db_qkan.isCurrentDbVersion
    # if not is_actual:
        # qkt = QKanTools(QKan.instance.iface)
        # logger.warning_user(
        #     "Versionskontrolle: Die Datenbank muss aktualisiert werden!"
        # )
    #         # qkt.run_dbAdapt()
    #         # iface = QKan.instance.iface
    #         # iface.newProject(True)
    #         # QgsProject.instance().clear()
    #         # project.read(pname)
    #
    # except ImportError:
    #     import traceback
    #
    #     traceback.print_exc()
    #     msg = "Diese Projektdatei wurde mit dem Programm QKan (Prof. Höttges, FH Aachen) erstellt."
    #     QgsMessageLog.logMessage(
    #         message=msg,
    #         level=Qgis.MessageLevel.Info,
    #     )
    #     QKan.instance.messageBar().pushMessage("Information", msg, level=Qgis.MessageLevel.Info)

    # Anpassen der Formularpfade
    projectTemplate = os.path.join(pluginDirectory("qkan"), "templates/Projekt.qgs")
    layersadapt(
        database_QKan=None,
        projectTemplate=projectTemplate,
        anpassen_ProjektMakros=False,
        anpassen_svgPaths=True,
        anpassen_Datenbankanbindung=False,
        anpassen_Layerstile=False,
        anpassen_Formulare=True,
        anpassen_Projektionssystem=False,
        aktualisieren_Schachttypen=False,
        zoom_alles=False,
        fehlende_layer_ergaenzen=False,
        anpassen_auswahl=enums.SelectedLayers.ALL,
    )

    # Alias für hinzugefügtes Feld "rwanschluss", kann ab 1.2027 wieder entfernt werden
    # project = QgsProject.instance()
    # layers = project.mapLayersByName('Haltungen')
    # for layer in layers:
    #     fields = layer.fields()
    #     for i, field in enumerate(fields):
    #         if field.name() == 'rwanschluss':
    #             layer.setFieldAlias(i, 'hat RW-Anschlüsse')
