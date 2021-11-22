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


def click_help() -> None:
    helpfile = (
        Path(__file__).parent.parent.parent
        / "doc/sphinx/build/html/Qkan_Formulare.html"
    )
    webbrowser.open_new_tab(str(helpfile) + "#datenbank-aktualisieren")


class DbAdaptDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_dbAdapt):  # type: ignore

    button_box: QDialogButtonBox

    gb_projectFile: QGroupBox
    gb_qkanDB: QGroupBox

    pb_selectProjectFile: QPushButton
    pb_selectQKanDB: QPushButton

    tf_projectFile: QLineEdit
    tf_qkanDB: QLineEdit

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.pb_selectProjectFile.clicked.connect(self.select_project_file)
        self.button_box.helpRequested.connect(click_help)
