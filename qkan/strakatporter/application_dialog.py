import logging
import os
from pathlib import Path
from typing import Callable, List, Optional

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QWidget,
)
from qgis.utils import pluginDirectory

from qkan import QKan, enums, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

logger = logging.getLogger("QKan.strakat.application_dialog")

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
        logger.debug(
            f"strakatporter.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "strakat_import_dialog_base.ui")
)


class ImportDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_database: QPushButton
    pb_import: QPushButton
    pb_project: QPushButton

    pw_epsg: QgsProjectionSelectionWidget

    cb_haltungen: QCheckBox
    cb_schaechte: QCheckBox
    cb_hausanschluesse: QCheckBox

    cb_schachtschaeden: QCheckBox
    cb_haltungsschaeden: QCheckBox

    cb_abflussparameter: QCheckBox
    cb_rohrprofile: QCheckBox
    cb_bodenklassen: QCheckBox

    cb_allrefs: QCheckBox

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyCallByClass,PyArgumentList
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_import.clicked.connect(self.select_import)
        self.pb_project.clicked.connect(self.select_project)
        self.pb_database.clicked.connect(self.select_database)
        # self.button_box.helpRequested.connect(self.click_help)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.strakat.import_dir)
        # noinspection PyCallByClass,PyArgumentList
        self.pw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_project.setText(QKan.config.project.file)

        self.cb_schaechte.setChecked(QKan.config.check_import.schaechte)
        self.cb_haltungen.setChecked(QKan.config.check_import.haltungen)
        self.cb_hausanschluesse.setChecked(QKan.config.check_import.hausanschluesse)
        self.cb_schachtschaeden.setChecked(QKan.config.check_import.schachtschaeden)
        self.cb_haltungsschaeden.setChecked(QKan.config.check_import.haltungsschaeden)
        self.cb_abflussparameter.setChecked(QKan.config.check_import.abflussparameter)
        self.cb_rohrprofile.setChecked(QKan.config.check_import.rohrprofile)
        self.cb_bodenklassen.setChecked(QKan.config.check_import.bodenklassen)

        self.cb_allrefs.setChecked(QKan.config.check_import.allrefs)

    def select_import(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        dirname = QFileDialog.getExistingDirectory (
            self,
            self.tr("Zu importierendes STRAKAT-Verzeichnis"),
            self.default_dir,
        )
        if dirname:
            self.tf_import.setText(dirname)
            self.default_dir = os.path.dirname(dirname)

    def select_project(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende Projektdatei"),
            self.default_dir,
            "*.qgs",
        )
        if filename:
            self.tf_project.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def select_database(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende SQLite-Datei"),
            self.default_dir,
            "*.sqlite",
        )
        if filename:
            self.tf_database.setText(filename)
            self.default_dir = os.path.dirname(filename)


RESULTS_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "strakat_import_dialog_base.ui")
)


