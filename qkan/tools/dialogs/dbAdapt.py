import os
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QWidget,
)

from . import QKanDBDialog, QKanProjectDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_dbAdapt, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_dbadapt.ui")
)


class DbAdaptDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_dbAdapt):  # type: ignore

    button_box: QDialogButtonBox

    gb_projectFile: QGroupBox
    gb_qkanDB: QGroupBox

    pb_selectProjectFile: QPushButton
    pb_selectQKanDB: QPushButton

    tf_projectFile: QLineEdit
    tf_qkanDB: QLineEdit

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent, readonly=True)

        self.pb_selectProjectFile.clicked.connect(self.select_project_file)
        self.button_box.helpRequested.connect(self.click_help)

    def click_help(self) -> None:
        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_Formulare.html#datenbank-aktualisieren"
        os.startfile(help_file)
