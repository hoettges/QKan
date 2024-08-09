import os
from typing import Callable, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QDialogButtonBox,
)
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget

from qkan import QKan
from qkan.utils import get_logger

logger = get_logger("QKan.strakat.application_dialog")


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
    button_box: QDialogButtonBox
    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_database: QPushButton
    pb_import: QPushButton
    pb_project: QPushButton

    pb_ordnerbild: QPushButton
    tf_ordnerbild: QLineEdit

    pb_ordnervideo: QPushButton
    tf_ordnervideo: QLineEdit

    tf_maxdist: QLineEdit

    pw_epsg: QgsProjectionSelectionWidget

    cb_haltungen: QCheckBox
    cb_schaechte: QCheckBox
    cb_hausanschluesse: QCheckBox

    cb_schachtschaeden: QCheckBox
    cb_haltungsschaeden: QCheckBox

    cb_testmodus: QCheckBox

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
        self.button_box.helpRequested.connect(self.click_help)
        #self.pb_ordnerbild.clicked.connect(self.select_ordnerbild)
        #self.pb_ordnervideo.clicked.connect(self.select_ordnervideo)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.strakat.import_dir)
        # noinspection PyCallByClass,PyArgumentList
        self.pw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_project.setText(QKan.config.project.file)

        self.tf_maxdist.setText(str(QKan.config.strakat.maxdiff))

        self.cb_schaechte.setChecked(QKan.config.check_import.schaechte)
        self.cb_haltungen.setChecked(QKan.config.check_import.haltungen)
        self.cb_hausanschluesse.setChecked(QKan.config.check_import.hausanschluesse)
        self.cb_schachtschaeden.setChecked(QKan.config.check_import.schachtschaeden)
        self.cb_haltungsschaeden.setChecked(QKan.config.check_import.haltungsschaeden)

        #self.cb_testmodus.setChecked(False)         # Standard: deaktiviert, vorher QKan.config.check_import.testmodus

    def select_import(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        dirname = QFileDialog.getExistingDirectory(
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

    def select_ordnerbild(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        ordner_bild = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner zur Speicherung der Fotos"),
            self.default_dir,
        )
        if ordner_bild:
            self.tf_ordnerbild.setText(ordner_bild)
            self.default_dir = os.path.dirname(ordner_bild)

    def select_ordnervideo(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        ordner_video = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner zur Speicherung der Videos"),
            self.default_dir,
        )
        if ordner_video:
            self.tf_ordnervideo.setText(ordner_video)
            self.default_dir = os.path.dirname(ordner_video)

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_STRAKAT.html#import-aus-strakat"
        os.startfile(help_file)


RESULTS_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "strakat_import_dialog_base.ui")
)
