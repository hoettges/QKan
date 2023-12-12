import os
from typing import TYPE_CHECKING, Optional
import webbrowser
from qgis.gui import QgisInterface
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QWidget,
    QTextBrowser,
)

from qkan import QKan

from . import QKanDialog, logger

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_help, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_help.ui")
)


class QgsHelpDialog(QKanDialog, FORM_CLASS_help):  # type: ignore
    pushButton: QPushButton
    pushButton_2: QPushButton
    textBrowser: QTextBrowser
    textBrowser_2: QTextBrowser

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.pushButton.clicked.connect(self.open_doku)
        self.pushButton_2.clicked.connect(self.open_team)

    def open_team(self) -> None:

        webbrowser.open('https://qkan.eu/Qkan_allgemein.html#team')

    def open_doku(self) -> None:

        webbrowser.open('https://qkan.eu/index.html')
