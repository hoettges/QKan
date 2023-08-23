import os
from typing import TYPE_CHECKING, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QWidget,
)

from qkan import QKan

from . import QKanDBDialog, QKanProjectDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_qgsadapt, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_qgsadapt.ui")
)


class QgsAdaptDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_qgsadapt):  # type: ignore
    button_box: QDialogButtonBox

    cb_applyQKanTemplate: QCheckBox
    cb_qkanDBUpdate: QCheckBox

    groupBox_2: QGroupBox
    groupBox: QGroupBox

    pb_selectProjectTemplate: QPushButton

    tf_projectTemplate: QLineEdit

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent, readonly=True)

        self.pb_selectProjectTemplate.clicked.connect(self.select_project_template)
        self.cb_applyQKanTemplate.clicked.connect(self.click_apply_template)
        self.button_box.helpRequested.connect(self.click_help)

    def click_apply_template(self) -> None:
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.cb_applyQKanTemplate.isChecked()
        self.tf_projectTemplate.setEnabled(not checked)

    def select_project_template(self) -> None:
        """Vorlage-Projektdatei auswählen"""

        self.cb_applyQKanTemplate.setChecked(False)  # automatisch deaktivieren
        self.click_apply_template()  # Auswirkungen auslösen

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self,
            "Vorlage für zu erstellende Projektdatei auswählen",
            QKan.template_dir,
            "*.qgs",
        )
        if os.path.dirname(filename) != "":
            self.tf_projectTemplate.setText(filename)

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_Datenaustausch.html#projektdatei-ubertragen"
        os.startfile(help_file)
