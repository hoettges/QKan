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

from . import QKanDBDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_filepath, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_filepath.ui")
)


class QgsFileDialog(QKanDBDialog, FORM_CLASS_filepath):  # type: ignore
    button_box: QDialogButtonBox
    pushButton: QPushButton
    pushButton_2: QPushButton
    pushButton_3: QPushButton
    lineEdit: QLineEdit
    lineEdit_2: QLineEdit
    lineEdit_3: QLineEdit
    checkBox: QCheckBox
    checkBox_2: QCheckBox


    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent, readonly=True)

        self.pushButton.clicked.connect(self.select_videopath)
        self.pushButton_2.clicked.connect(self.select_fotopath1)
        self.pushButton_3.clicked.connect(self.select_fotopath2)
        self.button_box.helpRequested.connect(self.click_help)

    def click_help(self) -> None:
        help_file = "https://qkan.eu/Qkan_Formulare.html#datenbank-aktualisieren"
        os.startfile(help_file)

    def select_videopath(self) -> None:

        ordner_video = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner Pfad")
        )
        if ordner_video:
            self.lineEdit.setText(ordner_video)

    def select_fotopath1(self) -> None:

        ordner_bild = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner Pfad")
        )
        if ordner_bild:
            self.lineEdit_2.setText(ordner_bild)

    def select_fotopath2(self) -> None:

        ordner_bild = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner Pfad")
        )
        if ordner_bild:
            self.lineEdit_3.setText(ordner_bild)

