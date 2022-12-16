import os
import logging
from typing import Callable, Optional

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QComboBox,
    QToolButton,
    QMessageBox,
    QDialogButtonBox,
)


logger = logging.getLogger("QKan.laengs.application_dialog")


LAENGS_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "laengsschnitt.ui")
)


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
        self.default_dir = str(default_dir)
        logger.debug(
            f"laengs.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr



class LaengsDialog(_Dialog, LAENGS_CLASS):  # type: ignore

    buttonBox: QDialogButtonBox
    pushButton: QPushButton
    pushButton_2: QPushButton
    lineEdit: QLineEdit
    lineEdit_2: QLineEdit


    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pushButton.clicked.connect(self.export_cad)
        self.pushButton_2.clicked.connect(self.refresh)
        self.refresh_function = None
        self.export_cad_function = None


    def export_cad(self):
        self.export_cad_function()

    def refresh(self):
        self.refresh_function()



