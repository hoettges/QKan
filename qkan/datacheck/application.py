import logging
import os
import shutil
from pathlib import Path

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from qkan import QKan, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from ._export import ExportTask
from ._import import ImportTask
from .application_dialog import PlausiDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip

logger = logging.getLogger("QKan.he8.application")


class Plausi(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"Plausi: default_dir: {default_dir}")
        self.plausi_dlg = PlausiDialog(default_dir, tr=self.tr)

        self.db_qkan: DBConnection = None

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_plausi = ":/plugins/qkan/mu_porter/res/icon_plausi.png"
        QKan.instance.add_action(
            icon_plausi,
            text=self.tr("Plausibilitätsprüfungen"),
            callback=self.run_plausi,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.plausi_dlg.close()
