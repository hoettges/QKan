import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional
from xml.etree import ElementTree

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget
from qgis.utils import pluginDirectory

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.tools.k_qgsadapt import qgsadapt

from . import QKanDBDialog, QKanProjectDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_empty_db, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_emptyDB.ui")
)

logger = logging.getLogger("QKan.tools.dialogs.empty_db")


class EmptyDBDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_empty_db):  # type: ignore
    epsg: QgsProjectionSelectionWidget

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.open_mode = False

    def run(self) -> None:
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_qkanDB.setText(QKan.config.database.qkan)
        self.tf_projectFile.setText(QKan.config.project.file)
        self.show()

        if self.exec_():
            QKan.config.database.qkan = self.tf_qkanDB.text()
            QKan.config.project.file = self.tf_projectFile.text()
            QKan.config.epsg = int(self.epsg.crs().postgisSrid())
            QKan.config.save()

            self._doemptydb()

            # Load project
            # noinspection PyArgumentList
            QgsProject.instance().read(QKan.config.project.file)

    def _doemptydb(self):

        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung("Fehler beim Erstellen der Datenbank:\n")
                return

            logger.debug('empty_db(2)')

            if QKan.config.project.file == "":
                return

            logger.debug(f'empty_db(5): project_file={QKan.config.project.file}')

            # Create project file
            qgsadapt(
                QKan.config.database.qkan,
                db_qkan,
                QKan.config.project.file,
                None,
                QKan.config.epsg
            )
