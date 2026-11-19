import os
from typing import Callable, Optional, TYPE_CHECKING
from qgis.PyQt import uic
from qgis.gui import QgsProjectionSelectionWidget
from qgis.core import QgsCoordinateReferenceSystem
from qgis.PyQt.QtWidgets import (
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QDialog,
    QRadioButton,
)
from qkan import QKan

class _Dialog(QDialog):
    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)
        self.default_dir = default_dir
        self.tr = tr


NEIGUNG_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "neigung.ui")
)

class NeigungDialog(_Dialog, NEIGUNG_CLASS):  # type: ignore
    #button_box: QDialogButtonBox
    speicher_neigung: QLineEdit
    speicher_dgm: QLineEdit
    url_dgm_daten: QLineEdit
    select_ordner_neigung: QPushButton
    select_ordner_dgm: QPushButton
    dgm_automatisch: QRadioButton
    dgm_manuell: QRadioButton
    epsg: QgsProjectionSelectionWidget


    def __init__(self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        self.select_ordner_neigung.clicked.connect(self.select_dgm_ordner)

        self.select_ordner_dgm.clicked.connect(self.select_dgm_speicher)

        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.button_box.helpRequested.connect(self.click_help)


    def select_dgm_ordner(self):
        dirname = QFileDialog.getExistingDirectory(
            self,
            self.tr("Speicherort DGM wählen"),
            self.default_dir,
        )
        if dirname:
            self.speicher_neigung.setText(dirname)
            self.default_dir = os.path.dirname(dirname)


    def select_dgm_speicher(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Vorhandene DGM Datei wählen"),
            self.default_dir,
            "*.tif",
        )

        if filename:
            self.speicher_dgm.setText(filename)

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_Flaechenverarbeitung.html#neigungsklasse-ermitteln"
        os.startfile(help_file)

