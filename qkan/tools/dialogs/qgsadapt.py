import os

import typing
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLineEdit,
    QPushButton,
)

from . import QKanDBDialog, QKanProjectDialog

if typing.TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_qgsadapt, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_qgsadapt.ui")
)


class QgsAdaptDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_qgsadapt):
    button_box: QDialogButtonBox

    cb_applyQKanTemplate: QCheckBox
    cb_qkanDBUpdate: QCheckBox

    groupBox_2: QGroupBox
    groupBox: QGroupBox

    pb_selectProjectTemplate: QPushButton

    tf_projectTemplate: QLineEdit

    def __init__(self, plugin: "QKanTools", parent=None):
        super().__init__(plugin, parent)

        self.pb_selectProjectTemplate.clicked.connect(self.select_project_template)
        self.cb_applyQKanTemplate.clicked.connect(self.click_apply_template)

    def click_apply_template(self):
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.cb_applyQKanTemplate.isChecked()
        self.tf_projectTemplate.setEnabled(not checked)

    def select_project_template(self):
        """Vorlage-Projektdatei auswählen"""

        self.cb_applyQKanTemplate.setChecked(False)  # automatisch deaktivieren
        self.click_apply_template()  # Auswirkungen auslösen

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self,
            "Vorlage für zu erstellende Projektdatei auswählen",
            self.templateDir,
            "*.qgs",
        )
        if os.path.dirname(filename) != "":
            self.tf_projectTemplate.setText(filename)
