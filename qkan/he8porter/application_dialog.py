import os
from typing import Callable, List, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QDialogButtonBox,
    QWidget,
)
from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError, QkanAbortError

logger = get_logger("QKan.he8.application_dialog")

EXPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "he8_export_dialog_base.ui")
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
        self.default_dir = default_dir
        self.tr = tr


class ExportDialog(_Dialog, EXPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_template: QLineEdit
    tf_exportdb: QLineEdit

    # cb_use_templatedir: QCheckBox
    button_box: QDialogButtonBox

    pb_database: QPushButton
    pb_template: QPushButton
    pb_exportdb: QPushButton

    cb_haltungen: QCheckBox
    cb_schaechte: QCheckBox
    cb_auslaesse: QCheckBox
    cb_speicher: QCheckBox
    cb_pumpen: QCheckBox
    cb_wehre: QCheckBox
    cb_drosseln: QCheckBox
    cb_schieber: QCheckBox
    cb_qregler: QCheckBox
    cb_hregler: QCheckBox
    cb_grundseitenauslaesse: QCheckBox
    cb_rohrprofile: QCheckBox
    cb_abflussparameter: QCheckBox
    cb_bodenklassen: QCheckBox
    cb_einleitdirekt: QCheckBox
    cb_aussengebiete: QCheckBox
    cb_einzugsgebiete: QCheckBox

    cb_flaechen: QCheckBox
    cb_tezg_hf: QCheckBox
    cb_tezg: QCheckBox

    rb_update: QRadioButton
    rb_append: QRadioButton

    cb_selectedObjects: QCheckBox

    db_qkan: DBConnection

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_exportdb.clicked.connect(self.select_exportdb)
        self.pb_template.clicked.connect(self.select_template)
        self.button_box.helpRequested.connect(self.click_help)

        # Aktionen zu Selektionen
        self.cb_selectedObjects.stateChanged.connect(self.count)

    def select_template(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        # if self.cb_use_templatedir.isChecked():
        #
        #     # TODO: Replace with QKan.config.project.template?
        #     searchdir = str(Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs")
        # else:
        searchdir = self.default_dir

        # noinspection PyCallByClass,PyArgumentList
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Vorlage für die zu erstellende HE8-Datei"),
            searchdir,
            "*.idbm",
        )
        if filename:
            self.tf_template.setText(filename)
            # self.default_dir = os.path.dirname(filename)

    def select_exportdb(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende HE8-Datei"),
            self.default_dir,
            "*.idbm",
        )
        if filename:
            self.tf_exportdb.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def click_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Anzahl in der Anzeige aktualisieren
        self.count()

    def count(self) -> None:
        """ Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
            der betroffenen Flächen und Haltungen
        """
        logger.debug('Event: SelectionChanged')
        with DBConnection() as db_qkan:
            db_qkan.loadmodule('he8porter')

            dbname = db_qkan.dbname

            # Datenbankpfad in Dialog übernehmen
            QKan.config.database.qkan = dbname

            self.tf_database.setText(QKan.config.database.qkan)

            # Checkbox hat den Status nach dem Klick
            selected = self.cb_selectedObjects.isChecked()
            # Ausgewählte Objekte in temporäre Tabellen übernehmen
            if selected:
                n_haltungen, n_schaechte, n_flaechen = db_qkan.getSelection(selected)
                logger.debug(f'Selection 2: {n_haltungen}, {n_schaechte}, {n_flaechen}')
                if not db_qkan.sqlyml('he8_count_haltungen_sel', 'count selected haltungen'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 105")
                n_haltungen = db_qkan.fetchone()[0]
                if not db_qkan.sqlyml('he8_count_sel_schaechte', 'count selected schaechte'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 106")
                n_schaechte = db_qkan.fetchone()[0]
                if not db_qkan.sqlyml('he8_count_sel_flaechen', 'count selected flaechen'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 107")
                n_flaechen = db_qkan.fetchone()[0]

            else:
                if not db_qkan.sqlyml('he8_count_haltungen_all', 'count selected haltungen'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 105")
                n_haltungen = db_qkan.fetchone()[0]
                if not db_qkan.sqlyml('he8_count_schaechte_all', 'count selected schaechte'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 106")
                n_schaechte = db_qkan.fetchone()[0]
                if not db_qkan.sqlyml('he8_count_flaechen_all', 'count selected flaechen'):
                    raise QkanDbError(f"{self.__class__.__name__}: errno. 107")
                n_flaechen = db_qkan.fetchone()[0]

            self.lf_anzahl_haltungen.setText(f'{n_haltungen}')
            self.lf_anzahl_schaechte.setText(f'{n_schaechte}')
            self.lf_anzahl_flaechen.setText(f'{n_flaechen}')

    def prepareDialog(self, iface) -> bool:
        """Prepare the dialog"""

        # Datenbanken und Vorlagen aus config übernehmen
        # self.tf_database.setText(QKan.config.database.qkan)
        self.tf_exportdb.setText(QKan.config.he8.export_file)
        self.tf_template.setText(QKan.config.he8.template)

        # Auswahl der zu exportierenden Tabellen
        self.cb_haltungen.setChecked(QKan.config.check_export.haltungen)
        self.cb_schaechte.setChecked(QKan.config.check_export.schaechte)
        self.cb_auslaesse.setChecked(QKan.config.check_export.auslaesse)
        self.cb_speicher.setChecked(QKan.config.check_export.speicher)
        self.cb_pumpen.setChecked(QKan.config.check_export.pumpen)
        self.cb_wehre.setChecked(QKan.config.check_export.wehre)
        self.cb_drosseln.setChecked(QKan.config.check_export.drosseln)
        self.cb_schieber.setChecked(QKan.config.check_export.schieber)
        self.cb_qregler.setChecked(QKan.config.check_export.qregler)
        self.cb_hregler.setChecked(QKan.config.check_export.hregler)
        self.cb_grundseitenauslaesse.setChecked(QKan.config.check_export.grundseitenauslaesse)
        self.cb_flaechen.setChecked(QKan.config.check_export.flaechen)
        self.cb_tezg_hf.setChecked(QKan.config.check_export.tezg_hf)
        self.cb_rohrprofile.setChecked(QKan.config.check_export.rohrprofile)
        self.cb_abflussparameter.setChecked(QKan.config.check_export.abflussparameter)
        self.cb_bodenklassen.setChecked(QKan.config.check_export.bodenklassen)
        self.cb_einleitdirekt.setChecked(QKan.config.check_export.einleitdirekt)
        self.cb_aussengebiete.setChecked(QKan.config.check_export.aussengebiete)
        self.cb_einzugsgebiete.setChecked(QKan.config.check_export.einzugsgebiete)
        self.cb_tezg.setChecked(QKan.config.check_export.tezg)
        self.cb_selectedObjects.setChecked(False)  # zunächst deaktiviert

        # Aktionen beim Export
        self.rb_append.setChecked(QKan.config.check_export.append)
        self.rb_update.setChecked(QKan.config.check_export.update)

        # Initialisierung der Anzeige der Anzahl zu exportierender Objekte

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
        help_file = "https://qkan.eu/QKan_Hystem_Extran.html#export-nach-hystem-extran"
        os.startfile(help_file)


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "he8_import_dialog_base.ui")
)


class ImportDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    button_box: QDialogButtonBox

    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_database: QPushButton
    pb_import: QPushButton
    pb_project: QPushButton

    pw_epsg: QgsProjectionSelectionWidget

    cb_haltungen: QCheckBox
    cb_schaechte: QCheckBox
    cb_auslaesse: QCheckBox
    cb_speicher: QCheckBox
    cb_pumpen: QCheckBox
    cb_wehre: QCheckBox
    cb_drosseln: QCheckBox
    cb_schieber: QCheckBox
    cb_qregler: QCheckBox
    cb_hregler: QCheckBox
    cb_grundseitenauslaesse: QCheckBox
    cb_flaechen: QCheckBox
    cb_rohrprofile: QCheckBox
    cb_abflussparameter: QCheckBox
    cb_bodenklassen: QCheckBox
    cb_einleitdirekt: QCheckBox
    cb_aussengebiete: QCheckBox
    cb_einzugsgebiete: QCheckBox

    cb_tezg_ef: QCheckBox
    cb_tezg_hf: QCheckBox
    cb_tezg_tf: QCheckBox

    rb_update: QRadioButton
    rb_append: QRadioButton

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
        self.button_box.helpRequested.connect(self.click_help)

    def prepareDialog(self, iface) -> bool:
        """Init fields"""

        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.he8.import_file)
        # noinspection PyCallByClass,PyArgumentList
        self.pw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_project.setText(QKan.config.project.file)

        self.cb_haltungen.setChecked(QKan.config.check_import.haltungen)
        self.cb_schaechte.setChecked(QKan.config.check_import.schaechte)
        self.cb_auslaesse.setChecked(QKan.config.check_import.auslaesse)
        self.cb_speicher.setChecked(QKan.config.check_import.speicher)
        self.cb_pumpen.setChecked(QKan.config.check_import.pumpen)
        self.cb_wehre.setChecked(QKan.config.check_import.wehre)
        self.cb_drosseln.setChecked(QKan.config.check_import.drosseln)
        self.cb_schieber.setChecked(QKan.config.check_import.schieber)
        self.cb_qregler.setChecked(QKan.config.check_import.qregler)
        self.cb_hregler.setChecked(QKan.config.check_import.hregler)
        self.cb_grundseitenauslaesse.setChecked(QKan.config.check_import.grundseitenauslaesse)
        self.cb_flaechen.setChecked(QKan.config.check_import.flaechen)
        self.cb_rohrprofile.setChecked(QKan.config.check_import.rohrprofile)
        self.cb_abflussparameter.setChecked(QKan.config.check_import.abflussparameter)
        self.cb_bodenklassen.setChecked(QKan.config.check_import.bodenklassen)
        self.cb_einleitdirekt.setChecked(QKan.config.check_import.einleitdirekt)
        self.cb_aussengebiete.setChecked(QKan.config.check_import.aussengebiete)
        self.cb_einzugsgebiete.setChecked(QKan.config.check_import.einzugsgebiete)

        self.cb_tezg_ef.setChecked(QKan.config.check_import.tezg_ef)
        self.cb_tezg_hf.setChecked(QKan.config.check_import.tezg_hf)
        self.cb_tezg_tf.setChecked(QKan.config.check_import.tezg_tf)

        # self.rb_append.setChecked(QKan.config.check_import.append)
        # self.rb_update.setChecked(QKan.config.check_import.update)

        self.cb_allrefs.setChecked(QKan.config.check_import.allrefs)

        return True

    def select_import(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende HE8-Datei"),
            self.default_dir,
            "*.idbm",
        )
        if filename:
            self.tf_import.setText(filename)
            self.default_dir = os.path.dirname(filename)

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
        help_file = "https://qkan.eu/QKan_Hystem_Extran.html#import-aus-hystem-extran"
        os.startfile(help_file)

RESULTS_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "he8_results_dialog_base.ui")
)


class ResultsDialog(_Dialog, RESULTS_CLASS):  # type: ignore
    button_box: QDialogButtonBox
    tf_database: QLineEdit
    tf_resultsDB: QLineEdit
    tf_project: QLineEdit

    pb_selectqmlfile: QPushButton
    pb_results: QPushButton
    pb_project: QPushButton

    rb_userqml: QRadioButton
    rb_uebh: QRadioButton
    rb_uebvol: QRadioButton
    rb_none: QRadioButton

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyCallByClass,PyArgumentList
        super().__init__(default_dir, tr, parent)

        self.default_dir = default_dir

        self.pb_selectqmlfile.clicked.connect(self.selectqmlfileResults)

        # Klick auf eine Option zum Layerstil aktiviert/deaktiviert das Textfeld und die Schaltfläche
        self.pb_selectResultsDB.clicked.connect(self.selectFile_ResultsDB)
        self.rb_userqml.clicked.connect(self.enable_tf_qmlfile)
        self.rb_uebh.clicked.connect(self.disable_tf_qmlfile)
        self.rb_uebvol.clicked.connect(self.disable_tf_qmlfile)
        self.rb_none.clicked.connect(self.disable_tf_qmlfile)

        self.button_box.helpRequested.connect(self.click_help)

        self.tf_resultsDB.setText(QKan.config.he8.results_file)

        # Option für Stildatei
        qml_choice = QKan.config.he8.qml_choice

        # Standard: User-qml-File ist deaktiviert
        self.disable_tf_qmlfile()

        if qml_choice == enums.QmlChoice.UEBH:
            self.rb_uebh.setChecked(True)
        elif qml_choice == enums.QmlChoice.UEBVOL:
            self.rb_uebvol.setChecked(True)
        elif qml_choice == enums.QmlChoice.USERQML:
            self.rb_userqml.setChecked(True)
            # User-qml-File ist aktivieren
            self.enable_tf_qmlfile()
        elif qml_choice == enums.QmlChoice.NONE:
            self.rb_none.setChecked(True)
        else:
            fehlermeldung = "Nicht definierte Option"
            logger.error_code(fehlermeldung)
            raise QkanAbortError(f"{self.__class__.__name__}: {fehlermeldung}")

        # Individuelle Stildatei
        self.tf_qmlfile.setText(QKan.config.he8.qml_file_results)

    def selectqmlfileResults(self):
        """qml-Stildatei auswählen"""

        filename, __ = QFileDialog.getOpenFileName(
            self,
            "Dateinamen der einzulesenen Stildatei auswählen",
            self.default_dir,
            "*.qml",
        )
        if os.path.dirname(filename) != "":
            os.chdir(os.path.dirname(filename))
        self.tf_qmlfile.setText(filename)

    def selectFile_ResultsDB(self):
        """Datenbankverbindung zur HE-Ergebnisdatenbank auswaehlen"""

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Dateinamen der zu lesenden HE-Ergebnisdatenbank auswählen",
            self.default_dir,
            "*.idbr",
        )
        if os.path.dirname(filename) != "":
            os.chdir(os.path.dirname(filename))
        self.tf_resultsDB.setText(filename)

    def enable_tf_qmlfile(self):
        """aktiviert das Textfeld für die qml-Stildatei"""
        self.tf_qmlfile.setEnabled(True)
        self.pb_selectqmlfile.setEnabled(True)

    def disable_tf_qmlfile(self):
        """deaktiviert das Textfeld für die qml-Stildatei"""
        self.tf_qmlfile.setEnabled(False)
        self.pb_selectqmlfile.setEnabled(False)

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_Hystem_Extran.html#ergebnisse-aus-hystem-extran-8"
        os.startfile(help_file)
