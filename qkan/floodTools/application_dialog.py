import logging
import os
from typing import Callable, Optional

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
)

from qkan import QKan
from .flood_db import FloodDB

logger = logging.getLogger("QKan.floodTools.application_dialog")


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


ANIMATION_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "animation_dialog_base.ui")
)


class AnimationDialog(_Dialog, ANIMATION_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_database: QPushButton
    pb_import: QPushButton
    pb_project: QPushButton

    pw_epsg: QgsProjectionSelectionWidget

    cb_velo: QCheckBox
    cb_wlevel: QCheckBox

    tf_faktor_v: QLineEdit
    tf_min_w: QLineEdit
    tg_min_v: QLineEdit

    def __init__(
        self,
        iface,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyCallByClass,PyArgumentList
        super().__init__(default_dir, tr, parent)

        self.iface = iface
        # Attach events
        self.pb_import.clicked.connect(self.select_import)
        self.pb_project.clicked.connect(self.select_project)
        self.pb_database.clicked.connect(self.select_database)
        # self.button_box.helpRequested.connect(self.click_help)

        # Init fields
        self.tf_database.setText(QKan.config.flood.database)
        self.tf_import.setText(QKan.config.flood.import_dir)
        # noinspection PyCallByClass,PyArgumentList
        self.pw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_project.setText(QKan.config.project.file)

        self.cb_velo.setChecked(QKan.config.flood.velo)
        self.cb_wlevel.setChecked(QKan.config.flood.wlevel)
        self.cb_gdb_remove.setChecked(QKan.config.flood.gdblayer)

        self.tf_faktor_v.setText(QKan.config.flood.faktor_v)
        self.tf_min_v.setText(QKan.config.flood.min_v)
        self.tf_min_w.setText(QKan.config.flood.min_w)

    def select_import(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        dirname = QFileDialog.getExistingDirectory (
            self,
            self.tr("Zu importierendes Geodatabase-Verzeichnis"),
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

