import os
import typing
import webbrowser
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox, QLineEdit, QPushButton, QGroupBox
)

from . import QKanDBDialog, QKanProjectDialog

if typing.TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_dbAdapt, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_dbadapt.ui")
)


def click_help():
    helpfile = (
        Path(__file__).parent.parent.parent
        / "doc/sphinx/build/html/Qkan_Formulare.html"
    )
    webbrowser.open_new_tab(str(helpfile) + "#datenbank-aktualisieren")


class DbAdaptDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_dbAdapt):

    button_box:             QDialogButtonBox

    tf_qkanDB:              QLineEdit
    pb_selectQKanDB:        QPushButton

    gb_qkanDB:              QGroupBox
    gb_projectFile:         QGroupBox

    pb_selectProjectFile:   QPushButton

    tf_projectFile:         QLineEdit


    def __init__(self, plugin: "QKanTools", parent=None):
        super().__init__(plugin, parent)

        self.pb_selectQKanDB.clicked.connect(self.select_qkan_db)
        self.pb_selectProjectFile.clicked.connect(self.select_qkan_db)
        self.button_box.helpRequested.connect(click_help)


    def select_qkan_db(self):
        # noinspection PyArgumentList,PyCallByClass
        super().select_qkan_db()


    def select_project_file(selfself):
        # noinspection PyArgumentList,PyCallByClass
        super().select_project_file()