import os
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QWidget,
)

from qkan import QKan
from qkan.database.qkan_utils import meldung

from . import QKanDBDialog, logger

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_layersadapt, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_layersadapt.ui")
)


class LayersAdaptDialog(QKanDBDialog, FORM_CLASS_layersadapt):  # type: ignore
    button_box: QDialogButtonBox

    cb_adaptDB: QCheckBox
    cb_adaptMacros: QCheckBox
    cb_adaptForms: QCheckBox
    cb_adaptKBS: QCheckBox
    cb_adaptTableLookups: QCheckBox
    cb_applyQKanTemplate: QCheckBox
    cb_completeLayers: QCheckBox
    cb_qkanDBUpdate: QCheckBox
    cb_updateNodetype: QCheckBox
    cb_zoomAll: QCheckBox

    gb_LayersAdapt: QGroupBox
    gb_projectTemplate: QGroupBox
    gb_selectLayers: QGroupBox
    gb_setNodeTypes: QGroupBox

    lb_projectTemplate: QLabel

    pb_selectProjectTemplate: QPushButton

    rb_adaptAll: QRadioButton
    rb_adaptSelected: QRadioButton

    tf_projectTemplate: QLineEdit

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent, readonly=True)

        self.pb_selectProjectTemplate.clicked.connect(self.select_project_template)
        self.button_box.helpRequested.connect(self.click_help)
        # self.cb_adaptForms.clicked.connect(self.click_adapt_forms)
        self.cb_adaptTableLookups.clicked.connect(self.click_adapt_table_lookups)
        self.cb_adaptKBS.clicked.connect(self.click_adapt_kbs)
        self.cb_applyQKanTemplate.clicked.connect(self.click_apply_template)

    def select_qkan_db(self) -> None:
        self.cb_adaptDB.setChecked(True)  # automatisch aktivieren
        super().select_qkan_db()

    def click_adapt_table_lookups(self) -> None:
        self.enable_project_template_group()

    def click_adapt_kbs(self) -> None:
        """
        Hält Checkbutton cb_adaptKBS aktiv, solange cb_adaptDB aktiv ist, weil bei
        Änderung der Datenbankanbindung immer das Projektionssystem überprüft
        werden soll.
        """
        if self.cb_adaptDB.isChecked():
            if not self.cb_adaptKBS.isChecked():
                meldung(
                    "",
                    "Bei einer Anpassung der Layeranbindungen muss auch die Anpassung des KBS aktiviert sein!",
                )
            self.cb_adaptKBS.setChecked(True)

    def click_apply_template(self) -> None:
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.cb_applyQKanTemplate.isChecked()
        self.tf_projectTemplate.setEnabled(not checked)

    def enable_project_template_group(self) -> None:
        """
        Aktiviert oder deaktiviert die Groupbox für das Projektdatei-Template
        abhängig von den angeklickten Checkbuttons
        """

        checked = self.cb_adaptTableLookups.isChecked()
        self.gb_projectTemplate.setEnabled(checked)

    def select_project_template(self) -> None:
        """Vorlage-Projektdatei auswählen"""

        self.cb_applyQKanTemplate.setChecked(False)  # automatisch deaktivieren
        self.click_apply_template()  # Auswirkungen auslösen

        if self.cb_adaptTableLookups.isChecked():
            template_dir = QKan.template_dir
        else:
            if self.db_qkan:
                template_dir = os.path.dirname(self.db_qkan.dbname or QKan.template_dir)
            else:
                logger.error(
                    "Programmfehler in tools.run_layersadapt:\nPfad konnte nicht auf "
                    + "database_QKan gesetzt werden.\n database_QKan = {}".format(
                        self.database_QKan
                    )
                )
                template_dir = QKan.template_dir

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "Projektdatei als Vorlage auswählen", template_dir, "*.qgs"
        )
        if os.path.dirname(filename) != "":
            self.tf_projectTemplate.setText(filename)

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_Formulare.html#projektlayer-aktualisieren"
        os.startfile(help_file)
