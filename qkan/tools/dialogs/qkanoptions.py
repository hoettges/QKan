import os
import site
import subprocess
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QWidget,
)
from qkan import QKan

from . import QKanDialog, logger

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_qkanoptions, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_qkanoptions.ui")
)


class QKanOptionsDialog(QKanDialog, FORM_CLASS_qkanoptions):  # type: ignore
    button_box: QDialogButtonBox

    pb_fangradiusDefault: QPushButton
    pb_max_loopsDefault: QPushButton
    pb_mindestflaecheDefault: QPushButton
    pb_openLogfile: QPushButton
    pb_openOptionsfile: QPushButton
    pb_selectLogeditor: QPushButton

    qsw_epsg: QgsProjectionSelectionWidget

    rb_postgis: QRadioButton
    rb_spatialite: QRadioButton

    tf_fangradius: QLineEdit
    tf_logeditor: QLineEdit
    tf_max_loops: QLineEdit
    tf_mindestflaeche: QLineEdit

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.pb_fangradiusDefault.clicked.connect(self.click_reset_fangradius)
        self.pb_mindestflaecheDefault.clicked.connect(self.click_reset_mindestflaeche)
        self.pb_max_loopsDefault.clicked.connect(self.click_reset_max_loops)
        self.pb_openLogfile.clicked.connect(self.click_open_log)
        self.pb_openOptionsfile.clicked.connect(self.click_open_settings)
        self.pb_selectLogeditor.clicked.connect(self.select_log_editor)
        # self.rb_itwh.toggled.connect(self.dlgro_activatedyna)
        self.tf_fangradius.textChanged.connect(self.changed_tf_fangradius)

    def click_reset_fangradius(self) -> None:
        self.tf_fangradius.setText("0.1")

    def click_reset_mindestflaeche(self) -> None:
        self.tf_mindestflaeche.setText("0.5")

    def click_reset_max_loops(self) -> None:
        self.tf_max_loops.setText("1000")

    def click_open_log(self) -> None:
        """
        Öffnet die Log-Datei mit dem Standard-Editor für Log-Dateien
        oder einem gewählten Editor
        """

        if QKan.config.tools.logeditor == "":
            os.startfile(QKan.instance.log_path, "open")
        else:
            command = '"{}" "{}"'.format(
                os.path.normpath(QKan.config.tools.logeditor),
                os.path.normcase(QKan.instance.log_path),
            )
            res = subprocess.call(command)
            logger.debug("command: %s\nres: %s", command, res)

    @staticmethod
    def click_open_settings() -> None:
        """
        Öffnet die Optionen-Datei (*.json) mit dem Standard-Editor für
        Log-Dateien oder einem gewählten Editor
        """

        config_file = Path(site.getuserbase()) / "qkan" / "qkan.json"

        if QKan.config.tools.logeditor == "":
            os.startfile(config_file, "open")
        else:
            command = '"{}" "{}"'.format(
                os.path.normpath(QKan.config.tools.logeditor),
                os.path.normcase(config_file),
            )
            res = subprocess.call(command)
            logger.debug("command: %s\nres: %s", command, res)

    def select_log_editor(self) -> None:
        """Alternativen Text-Editor auswählen"""

        # Textfeld wieder deaktivieren
        self.tf_logeditor.setEnabled(True)

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "Alternativen Texteditor auswählen", "c:/", "*.exe"
        )
        QKan.config.tools.logeditor = filename
        self.tf_logeditor.setText(filename)
        if os.path.dirname(filename) == "":
            # Textfeld wieder deaktivieren
            self.tf_logeditor.setEnabled(False)

    def changed_tf_fangradius(self) -> None:
        """Gibt eine Warnung, falls Fangradius zu groß"""
        try:
            fangradius = float(self.tf_fangradius.text().replace(",", "."))
        except:
            return
        if fangradius > 0.5:
            self.tf_fangradius.setStyleSheet("border: 2px solid red; color: red")
            self.lf_warning.setText("Wert zu groß!")
            self.lf_warning.setStyleSheet("color: red; font: bold;")
            self.lf_unit_fangradius.setStyleSheet("color: red")
        else:
            self.tf_fangradius.setStyleSheet("border: 1px solid black;")
            self.lf_warning.setText("")
            self.lf_warning.setStyleSheet("color: black; font: bold;")
            self.lf_unit_fangradius.setStyleSheet("color: black")
