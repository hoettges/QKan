# -*- coding: utf-8 -*-
import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLineEdit,
    QPushButton,
)
from qgis.gui import QgsProjectionSelectionWidget

from qkan import get_default_dir

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "application_dialog_base.ui")
)


class ImportFromDynaDialog(QDialog, FORM_CLASS):
    button_box: QDialogButtonBox

    pb_selectDynaFile: QPushButton
    pb_selectProjectFile: QPushButton
    pb_selectqkanDB: QPushButton

    qsw_epsg: QgsProjectionSelectionWidget

    tf_dynaFile: QLineEdit
    tf_projectFile: QLineEdit
    tf_qkanDB: QLineEdit

    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.default_dir = get_default_dir()

        self.pb_selectqkanDB.clicked.connect(self.select_qkan_db)
        self.pb_selectDynaFile.clicked.connect(self.select_dyna_file)
        self.pb_selectProjectFile.clicked.connect(self.select_project_file)

    def select_dyna_file(self):
        """DYNA (*.ein) -datei auswählen"""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self,
            "Dateinamen der zu lesenden Kanal++-Datei eingeben",
            self.default_dir,
            "*.ein",
        )
        self.tf_dynaFile.setText(filename)

    def select_qkan_db(self):
        """
        Datenbankverbindung zur QKan-Datenbank (SpatiaLite) auswaehlen, aber noch nicht verbinden.
        Falls die Datenbank noch nicht existiert, wird sie nach Betaetigung von [OK] erstellt.
        """

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getSaveFileName(
            self,
            "Dateinamen der zu erstellenden SpatiaLite-Datenbank eingeben",
            self.default_dir,
            "*.sqlite",
        )
        self.tf_qkanDB.setText(filename)

    def select_project_file(self):
        """Zu erzeugende Projektdatei festlegen, falls ausgewählt."""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getSaveFileName(
            self,
            "Dateinamen der zu erstellenden Projektdatei eingeben",
            self.default_dir,
            "*.qgs",
        )
        self.tf_projectFile.setText(filename)
