import os
from typing import Callable, Optional

from PyQt5.QtWidgets import QRadioButton
from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QDialogButtonBox,
)

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError
from qkan.tools.qkan_utils import loadLayer

logger = get_logger("QKan.m150.application_dialog")

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
    button_box: QDialogButtonBox
    tf_database: QLineEdit
    tf_export: QLineEdit

    pb_export: QPushButton
    pb_showKeyTable: QPushButton

    cb_export_schaechte: QCheckBox
    cb_export_auslaesse: QCheckBox
    cb_export_speicher: QCheckBox
    cb_export_haltungen: QCheckBox
    cb_export_pumpen: QCheckBox
    cb_export_wehre: QCheckBox
    cb_export_anschlussleitungen: QCheckBox
    cb_includeMissingKeys: QCheckBox
    cb_selectedObjects: QCheckBox
    cb_cutNames: QCheckBox
    rb_mnn: QRadioButton
    rb_nhn: QRadioButton


    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_export.clicked.connect(self.select_export)
        self.button_box.helpRequested.connect(self.click_help)
        self.pb_showKeyTable.clicked.connect(self.showKeyTable)

        # Aktionen zu Selektionen
        self.cb_selectedObjects.stateChanged.connect(self.count)
        logger.debug("cb_selectedObjects.stateChanged.connect(self.count)")
        self.cb_includeMissingKeys.stateChanged.connect(self.count)
        logger.debug("cb_includeMissingKeys.stateChanged.connect(self.count)")

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_export.setText(QKan.config.xml.export_file)
        self.cb_export_schaechte.setChecked(
            getattr(QKan.config.check_export, "schaechte", True)
        )
        self.cb_export_auslaesse.setChecked(
            getattr(QKan.config.check_export, "auslaesse", True)
        )
        self.cb_export_speicher.setChecked(
            getattr(QKan.config.check_export, "speicher", True)
        )
        self.cb_export_haltungen.setChecked(
            getattr(QKan.config.check_export, "haltungen", True)
        )
        self.cb_export_anschlussleitungen.setChecked(
            getattr(QKan.config.check_export, "anschlussleitungen", True)
        )
        self.cb_export_pumpen.setChecked(
            getattr(QKan.config.check_export, "pumpen", True)
        )
        self.cb_export_wehre.setChecked(
            getattr(QKan.config.check_export, "wehre", True)
        )
        self.cb_includeMissingKeys.setChecked(
            getattr(QKan.config.check_export, "includeMissingKeys", True)
        )
        self.cb_selectedObjects.setChecked(
            getattr(QKan.config.selections, "selectedObjects", False)
        )
        self.cb_cutNames.setChecked(
            getattr(QKan.config.check_export, "cutNames", False)
        )
        if QKan.config.check_export.hoehensystem == enums.Hoehensystem.METER_UEBER_NN:
            self.rb_mnn.setChecked(True)
        elif QKan.config.check_export.hoehensystem == enums.Hoehensystem.NORMAL_HOEHENNULL:
            self.rb_nhn.setChecked(True)
        else:
            logger.error("Hoehensystem not recognized")

        self._prepared = False                      # self._prepare_refdata() nur einmal in count aufrufen

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
            self.default_dir = os.path.dirname(filename)

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
                included = self.cb_includeMissingKeys.isChecked()
                if included:
                    selection += '_include'

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

    def showKeyTable(self):
        """Anzeige des Attributlayers M150-Kürzel zur Kontrolle fehlender Einträg"""

        project = QgsProject().instance()
        layerobjects = project.mapLayersByName(enums.LAYERBEZ.M150_KUERZEL_ERG.value)
        layerexists = (len(layerobjects) > 0)
        if not layerexists:
            grouppath = [
                enums.LAYERBEZ.QKAN_GROUP.value,
                enums.LAYERBEZ.REFERENZTABELLEN_GROUP.value,
                    enums.LAYERBEZ.M150_GROUP.value,
            ]

            loadLayer(
                layerbez=   enums.LAYERBEZ.M150_KUERZEL_ERG.value,
                table=      "refdata",
                geom_column=None,
                qmlfile=    "qkan_m150_kuerzel_erg.qml",
                filter=     "(kuerzel IS NULL OR kuerzel = '') AND modul = 'm150porter'",
                uifile=     None,
                group=      grouppath
            )
            project.write()

            # msg = ('\n\nIn der M150-Datei sind individuelle Knotentypen definiert. Vor einem Import muss \n'
            #        'in der Referenztabelle "M150 Knotenarten" der QKan-Schachttyp ausgewählt werden. \n\n'
            #        'Anschließend muss der Import neu gestartet werden. \n(siehe <a href='
            #        '"https://qkan.eu/versionen/new/QKan_XML.html#start-des-importes">QKan Dokumentation</a>)!\n\n')
            # self.log.warning_user(msg)

        # Attributtabelle zur Bearbeitung anzeigen
        layer = project.mapLayersByName(enums.LAYERBEZ.M150_KUERZEL_ERG.value, )[0]
        self.iface.showAttributeTable(layer)

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

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_XML.html#export-nach-dwa-m150"
        os.startfile(help_file)


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

        self.button_box.helpRequested.connect(self.click_help)

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

        self.cb_impStamm.setChecked(getattr(QKan.config.xml, "import_stamm", True))
        self.cb_impAnschluesse.setChecked(getattr(QKan.config.xml, "import_haus", True))
        self.cb_zustand.setChecked(getattr(QKan.config.xml, "import_zustand", True))
        self.cb_teilbefahrung.setChecked(getattr(QKan.config.xml, "import_teilbefahrung", True))

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

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_XML.html#import-aus-dwa-m-150"
        os.startfile(help_file)
