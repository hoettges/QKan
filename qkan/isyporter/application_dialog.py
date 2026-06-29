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
    QComboBox,
)

from qkan import QKan
from qkan.utils import get_logger, QkanDbError
from qkan.database.dbfunc import DBConnection
logger = get_logger("QKan.isybau.application_dialog")

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
    tf_export_2: QLineEdit

    pb_export: QPushButton
    pb_export_2: QPushButton

    cb_export_schaechte: QCheckBox
    cb_export_auslaesse: QCheckBox
    cb_export_speicher: QCheckBox
    cb_export_haltungen: QCheckBox
    cb_export_pumpen: QCheckBox
    cb_export_wehre: QCheckBox
    cb_export_anschlussleitungen: QCheckBox
    cb_export_zustandsdaten: QCheckBox
    comboBox: QComboBox
    cb_selectedObjects: QCheckBox

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        self.cb_selectedObjects.stateChanged.connect(self.count)

        # Attach events
        self.pb_export.clicked.connect(self.select_export)
        self.pb_export_2.clicked.connect(self.select_vorlage)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_export.setText(QKan.config.xml.export_file)
        self.tf_export_2.setText(QKan.config.xml.vorlage)
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
        self.cb_export_zustandsdaten.setChecked(
            getattr(QKan.config.check_export, "export_zustandsdaten", True)
        )
        self.cb_selectedObjects.setChecked(
            getattr(QKan.config.selections, "selectedObjects", False)
        )

        self._prepared = False

    def select_export(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende XML-Datei"),
            self.default_dir,
            filter="*.xml",
        )
        if filename:
            self.tf_export.setText(filename)

    def select_vorlage(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Vorlage XML-Datei wählen"),
            self.default_dir,
            "*.xml",
        )
        if filename:
            self.tf_export_2.setText(filename)

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

    def count(self) -> None:
        """ Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
            der betroffenen Flächen und Haltungen
        """
        logger.debug('Event: SelectionChanged')

        if QgsProject.instance().fileName() != '':
            with DBConnection() as db_qkan:
                db_qkan.loadmodule('m150porter')

                dbname = db_qkan.dbname

                # Datenbankpfad in Dialog übernehmen
                QKan.config.database.qkan = dbname

                self.tf_database.setText(QKan.config.database.qkan)

                # Checkbox hat den Status nach dem Klick
                selected = self.cb_selectedObjects.isChecked()
                if selected:
                    selection = '_sel'
                else:
                    selection = '_all'

                # Checkbox hat den Status nach dem Klick
                # included = self.cb_includeMissingKeys.isChecked()
                # if included:
                #     selection += '_include'

                # Ausgewählte Objekte in temporäre Tabellen übernehmen
                n_haltungen, n_schaechte, _ = db_qkan.getSelection(selected)        # flaechen not used here
                logger.debug(f'Selection in Layern: {n_haltungen=}, {n_schaechte=}')

                if not db_qkan.sqlyml('m150_count_haltungen' + selection, f'count selected haltungen ({selection=})'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 105")
                n_haltungen = db_qkan.fetchone()[0]
                if not db_qkan.sqlyml('m150_count_schaechte' + selection, f'count selected schaechte ({selection=})'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 106")
                n_schaechte = db_qkan.fetchone()[0]

                self.lf_anzahl_haltungen.setText(f'{n_haltungen}')
                self.lf_anzahl_schaechte.setText(f'{n_schaechte}')

                if not self._prepared:
                    self._prepare_refdata(db_qkan)
                    self._prepared = True

    def _prepare_refdata(self, db_qkan: DBConnection) -> None:
        """Fügt Refernzdaten aus dem Import für den Export hinzu und ergänzt falls nicht
        vorhanden Knotenarten
        """
        sqls = [
            'm150_insert_refdatafromimport',
            'm150_insert_knotenarten',
            'm150_insert_refdatafromtables',
        ]
        for sqlnam in sqls:
            if not db_qkan.sqlyml(
                sqlnam
            ):
                raise QkanDbError

        # Leere Referenztabellen mit Standardwerten füllen
        subjects = ['simulationsstatus', 'entwaesserungsarten']
        for subject in subjects:
            sqlnam = f'm150_ex_count_{subject}'
            if not db_qkan.sqlyml(
                sqlnam
            ):
                raise QkanDbError

            if db_qkan.fetchone()[0] == 0:
                sqlnam = f'm150_ex_insert_{subject}'
                if not db_qkan.sqlyml(
                    sqlnam
                ):
                    raise QkanDbError

        db_qkan.commit()

    def prepareDialog(self, iface) -> bool:
        # Initialisierung der Anzeige der Anzahl zu exportierender Objekte

        self.iface = iface

        # Für 3 Layer Selection-Change-Events definieren
        for layernam in ['Haltungen', 'Schächte', 'Flächen']:
            layerobjects = QgsProject().instance().mapLayersByName(layernam)
            for layer in layerobjects:
                layer.selectionChanged.connect(self.count)

        try:
            self.count()
        except:
            logger.error_code('prepareDialog: Fehler beim Aufruf von count')
            return False

        return True

    def finishDialog(self) -> bool:
        # Aufheben der Anzeige der Anzahl zu exportierender Objekte

        # Aufheben der Selections-Change-Events
        for layernam in ['Haltungen', 'Schächte', 'Flächen']:
            layerobjects = QgsProject().instance().mapLayersByName(layernam)
            for layer in layerobjects:
                layer.selectionChanged.disconnect()

        return True


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

    pb_ordnerFotos: QPushButton
    tf_ordnerFotos: QLineEdit

    pb_ordnervideo: QPushButton
    tf_ordnervideo: QLineEdit

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
        self.pb_ordnerFotos.clicked.connect(self.select_ordnerbild)
        self.pb_ordnervideo.clicked.connect(self.select_ordnervideo)
        self.pb_project.clicked.connect(self.select_project)
        self.pb_database.clicked.connect(self.select_database)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.xml.import_file)
        self.tf_ordnerFotos.setText(QKan.config.fotoPathCurrent)
        self.tf_ordnervideo.setText(QKan.config.videoPathCurrent)

        self.tf_rootFotos.setText(QKan.config.fotoRootPath)
        self.tf_rootVideos.setText(QKan.config.videoRootPath)

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

    def select_ordnerbild(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        ordner_bild = QFileDialog.getExistingDirectory(
            self,
            self.tr("Ordner zur Speicherung der Fotos"),
            self.default_dir,
        )
        if ordner_bild:
            self.tf_ordnerFotos.setText(ordner_bild)
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
        options = QFileDialog.Options()
        options |= QFileDialog.DontConfirmOverwrite  # keine Überschreib-Rückfrage
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende SQLite-Datei"),
            self.default_dir,
            filter="*.sqlite",
            options=options,
        )
        if filename:
            self.tf_database.setText(filename)
            self.default_dir = os.path.dirname(filename)
