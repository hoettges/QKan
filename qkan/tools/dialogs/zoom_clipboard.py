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
    QToolButton,
    QApplication,
)
from PyQt6.QtGui import QClipboard

from qkan import QKan

from . import QKanDBDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_zoom, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_zoom_clipboard.ui")
)


class QgsZoomDialog(QKanDBDialog, FORM_CLASS_zoom):  # type: ignore
    toolButton: QToolButton


    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent, readonly=True)

        self.clip = QApplication.clipboard()


        self.toolButton.toggled.connect(self.toggle_action)

        self.button_box.helpRequested.connect(self.click_help)
        self.text = None

    def on_change(self):
        text = self.clip.text()
        self.text = text

    def toggle_action(self, checked):
        if checked:
            self.button = True
            self.clip.dataChanged.connect(self.on_change)
            return self.text

        else:
            self.button = False
            self.clip.dataChanged.disconnect()



    def click_help(self) -> None:
        help_file = "https://qkan.eu//QKan_Formulare_Allgemein.html"
        os.startfile(help_file)

