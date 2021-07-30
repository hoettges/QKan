import os
from typing import Callable, Optional

from qgis.core import QgsCoordinateReferenceSystem
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

EXPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "xml_export_dialog_base.ui")
)


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
        self.default_dir = str(default_dir)
        self.tr = tr


class ExportDialog(_Dialog, EXPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_export: QLineEdit

    pb_database: QPushButton
    pb_export: QPushButton

    cb_export_schaechte: QCheckBox
    cb_export_auslaesse: QCheckBox
    cb_export_speicher: QCheckBox
    cb_export_haltungen: QCheckBox
    cb_export_pumpen: QCheckBox
    cb_export_wehre: QCheckBox
    cb_export_anschlussleitungen: QCheckBox

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_database.clicked.connect(self.select_database)
        self.pb_export.clicked.connect(self.select_export)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_export.setText(QKan.config.xml.export_file)
        self.cb_export_schaechte.setChecked(
            getattr(QKan.config.check_export, "export_schaechte", True)
        )
        self.cb_export_auslaesse.setChecked(
            getattr(QKan.config.check_export, "export_auslaesse", True)
        )
        self.cb_export_speicher.setChecked(
            getattr(QKan.config.check_export, "export_speicher", True)
        )
        self.cb_export_haltungen.setChecked(
            getattr(QKan.config.check_export, "export_haltungen", True)
        )
        self.cb_export_anschlussleitungen.setChecked(
            getattr(QKan.config.check_export, "export_anschlussleitungen", True)
        )
        self.cb_export_pumpen.setChecked(
            getattr(QKan.config.check_export, "export_pumpen", True)
        )
        self.cb_export_wehre.setChecked(
            getattr(QKan.config.check_export, "export_wehre", True)
        )

    def select_export(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende XML-Datei"),
            self.default_dir,
            "*.xml",
        )
        if filename:
            self.tf_export.setText(filename)

    def select_database(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende SQLite-Datei"),
            self.default_dir,
            "*.sqlite",
        )

        if filename:
            self.tf_database.setText(filename)


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "xml_import_dialog_base.ui")
)


class ImportDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_database: QPushButton
    pb_import: QPushButton
    pb_project: QPushButton

    pb_import_2: QPushButton
    tf_import_2: QLineEdit

    pb_import_3: QPushButton
    tf_import_3: QLineEdit

    cb_import_tabinit: QCheckBox

    epsg: QgsProjectionSelectionWidget

    checkBox: QCheckBox
    checkBox_2: QCheckBox
    checkBox_3: QCheckBox

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_import.clicked.connect(self.select_import)
        self.pb_import_2.clicked.connect(self.select_import_2)
        self.pb_import_3.clicked.connect(self.select_import_3)
        self.pb_project.clicked.connect(self.select_project)
        self.pb_database.clicked.connect(self.select_database)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.xml.import_file)
        self.tf_import_2.setText(QKan.config.xml.ordner_bild)
        self.tf_import_3.setText(QKan.config.xml.ordner_video)
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_project.setText(QKan.config.project.file)

        self.checkBox.setChecked(
            getattr(QKan.config.xml, "import_stamm", True)
        )

        self.checkBox_2.setChecked(
            getattr(QKan.config.xml, "import_haus", True)
        )

        self.checkBox_3.setChecked(
            getattr(QKan.config.xml, "import_zustand", True)
        )

    def select_import(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende XML-Datei"),
            self.default_dir,
            "*.xml",
        )
        if filename:
            self.tf_import.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def select_import_2(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        ordner_bild = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner Pfad"),
            self.default_dir,
        )
        if ordner_bild:
            self.tf_import_2.setText(ordner_bild)
            self.default_dir = os.path.dirname(ordner_bild)

    def select_import_3(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        ordner_video = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner Pfad"),
            self.default_dir,
        )
        if ordner_video:
            self.tf_import_3.setText(ordner_video)
            self.default_dir = os.path.dirname(ordner_video)

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
