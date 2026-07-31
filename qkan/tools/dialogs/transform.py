import os
from typing import Callable, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QLineEdit,
    QWidget,
)
from qgis.gui import QgsProjectionSelectionWidget
from qgis.core import QgsCoordinateReferenceSystem

from qkan import QKan
from qkan.utils import get_logger
from qkan.tools.qkan_utils import get_database_QKan

logger = get_logger("QKan.sync.application_dialog")


class _Dialog(QDialog):
    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)
        self.default_dir = default_dir
        self.tr = tr


TRANSFORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_transform.ui")
)


class TransformDialog(_Dialog, TRANSFORM_CLASS):  # type: ignore
    tf_database: QLineEdit
    pw_epsg_from: QgsProjectionSelectionWidget
    pw_epsg: QgsProjectionSelectionWidget

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyCallByClass,PyArgumentList
        super().__init__(default_dir, tr, parent)

        self.epsg_from = QKan.config.epsg       # Default. Muss aber durch den User geändert werden

        # No events to be attached

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""

        help_file = "https://qkan.eu/QKan_Daten.html#Transformation"
        os.startfile(help_file)

    def prepareDialog(self):
        """Read fields from Config"""

        # Lesen der geladenen Datenbank sowie des KBS
        if get_database_QKan():

            self.tf_database.setText(QKan.config.database.qkan)
            self.pw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
            self.pw_epsg_from.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(self.epsg_from))

            return True
        else:
            logger.warning_user("Es ist noch keine Projekt geöffnet!")
            return False

    def finishDialog(self):
        # Read from form and save to config

        self.epsg_from = int(self.pw_epsg.crs().postgisSrid())

        QKan.config.save()
