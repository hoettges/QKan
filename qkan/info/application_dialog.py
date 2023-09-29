import os
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
)

from qkan import QKan

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
        self.tr = tr



INFO_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "info.ui")
)


class InfoDialog(_Dialog, INFO_CLASS):  # type: ignore
    textBrowser_2: QLineEdit
    textBrowser_3: QLineEdit
    textBrowser_4: QLineEdit
    textBrowser_5: QLineEdit
    textBrowser_6: QLineEdit


    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)


