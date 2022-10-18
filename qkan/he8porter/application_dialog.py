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

logger = logging.getLogger("QKan.he8.application_dialog")

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
        logger.debug(
            f"he8porter.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr


class ExportDialog(_Dialog, EXPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_template: QLineEdit
    tf_exportdb: QLineEdit

    cb_use_templatedir: QCheckBox

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
    cb_flaechen: QCheckBox
    cb_rohrprofile: QCheckBox
    cb_abflussparameter: QCheckBox
    cb_bodenklassen: QCheckBox
    cb_einleitdirekt: QCheckBox
    cb_aussengebiete: QCheckBox
    cb_einzugsgebiete: QCheckBox

    cb_tezg: QCheckBox
    cb_tezg_hf: QCheckBox

    rb_update: QRadioButton
    rb_append: QRadioButton

    lw_teilgebiete: QListWidget

    db_qkan: DBConnection

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(default_dir, tr, parent)

        self.default_dir = default_dir

        # Attach events
        self.pb_exportdb.clicked.connect(self.select_exportdb)
        self.pb_template.clicked.connect(self.select_template)
        self.cb_flaechen.clicked.connect(self.check_flaechen)
        self.cb_tezg_hf.clicked.connect(self.check_tezg_hf)
        # self.button_box.helpRequested.connect(self.click_help)

        # Aktionen zu lw_teilgebiete: QListWidget
        self.cb_selActive.stateChanged.connect(self.click_selection)
        # self.lw_teilgebiete.itemClicked.connect(self.count_selection)      # ist schon in click_lw_teilgebiete enthalten
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)

        # Init fields

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
        self.cb_tezg_hf.setChecked(QKan.config.check_export.tezg_hf)

        # Aktionen beim Export
        self.rb_append.setChecked(QKan.config.check_export.append)
        self.rb_update.setChecked(QKan.config.check_export.update)

    # deaktiviert, weil sich die Quelldatenbank aus dem Projekt ergibt
    # def select_database(self):
    #     # noinspection PyArgumentList,PyCallByClass
    #     filename, _ = QFileDialog.getOpenFileName(
    #         self,
    #         self.tr("Zu importierende SQLite-Datei"),
    #         self.default_dir,
    #         "*.sqlite",
    #     )
    #     if filename:
    #         self.tf_database.setText(filename)
    #         self.default_dir = os.path.dirname(filename)

    def select_template(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        if self.cb_use_templatedir.isChecked():

            # TODO: Replace with QKan.config.project.template?
            searchdir = str(Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs")
        else:
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

        # Checkbox hat den Status nach dem Klick
        if self.cb_selActive.isChecked():
            # Nix tun ...
            logger.debug("\nChecked = True")
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_teilgebiete.count()
            for i in range(anz):
                item = self.lw_teilgebiete.item(i)
                item.setSelected(False)
                # self.lw_teilgebiete.setItemSelected(item, False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def click_lw_teilgebiete(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selActive.setChecked(True)
        self.count_selection()

    def count_selection(self) -> bool:
        """
        Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen
        """

        if not self.db_qkan:
            logger.error("db_qkan is not initialized.")
            return False

        teilgebiete: List[str] = list_selected_items(self.lw_teilgebiete)
        # teilgebiete: List[str] = []        # Todo: wieder aktivieren

        # Zu berücksichtigende Flächen zählen
        auswahl = ""
        if len(teilgebiete) != 0:
            auswahl = " WHERE flaechen.teilgebiet in ('{}')".format(
                "', '".join(teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM flaechen {auswahl}"

        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.countselection (1)"):
            return False
        daten = self.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.lf_anzahl_flaechen.setText("0")

        # Zu berücksichtigende Schächte zählen
        auswahl = ""
        if len(teilgebiete) != 0:
            auswahl = " WHERE schaechte.teilgebiet in ('{}')".format(
                "', '".join(teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM schaechte {auswahl}"
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.countselection (2) "):
            return False
        daten = self.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_schaechte.setText(str(daten[0]))
        else:
            self.lf_anzahl_schaechte.setText("0")

        # Zu berücksichtigende Haltungen zählen
        auswahl = ""
        if len(teilgebiete) != 0:
            auswahl = " WHERE haltungen.teilgebiet in ('{}')".format(
                "', '".join(teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM haltungen {auswahl}"
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.countselection (3) "):
            return False
        daten = self.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.lf_anzahl_haltungen.setText("0")
        return True

    def prepareDialog(self, db_qkan) -> bool:
        """Füllt Auswahllisten im Export-Dialog"""

        self.db_qkan = db_qkan
        # Alle Teilgebiete in Flächen, Schächten und Haltungen, die noch nicht in Tabelle "teilgebiete" enthalten
        # sind, ergänzen

        sql = """WITH tgb AS (
                SELECT teilgebiet FROM flaechen
                WHERE teilgebiet IS NOT NULL
                UNION
                SELECT teilgebiet FROM haltungen
                WHERE teilgebiet IS NOT NULL
                UNION
                SELECT teilgebiet FROM schaechte
                WHERE teilgebiet IS NOT NULL
                )
                INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM tgb
                WHERE teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "he8porter.application_dialog.connectQKanDB (1) "):
            return False

        self.db_qkan.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        teilgebiete = QKan.config.selections.teilgebiete

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.db_qkan.sql(sql, "he8porter.application_dialog.connectQKanDB (4) "):
            return False
        daten = self.db_qkan.fetchall()
        self.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in teilgebiete:
                    self.lw_teilgebiete.setCurrentRow(ielem)
            except BaseException as err:
                fehlermeldung(
                    (
                        "he8porter.application_dialog.connectQKanDB, "
                        f"Fehler in elem = {elem}\n"
                    ),
                    repr(err),
                )

        # Initialisierung der Anzeige der Anzahl zu exportierender Objekte
        self.count_selection()

        return True

    def check_flaechen(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        if self.cb_flaechen.isChecked():
            QKan.config.check_export.tezg_hf = False
            self.cb_tezg_hf.setChecked(False)

    def check_tezg_hf(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        if self.cb_tezg_hf.isChecked():
            QKan.config.check_export.flaechen = False
            self.cb_flaechen.setChecked(False)


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "he8_import_dialog_base.ui")
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

        self.default_dir = default_dir

        # Attach events
        self.pb_import.clicked.connect(self.select_import)
        self.pb_project.clicked.connect(self.select_project)
        self.pb_database.clicked.connect(self.select_database)
        # self.button_box.helpRequested.connect(self.click_help)

        # Init fields
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

        self.rb_append.setChecked(QKan.config.check_import.append)
        self.rb_update.setChecked(QKan.config.check_import.update)

        self.cb_allrefs.setChecked(QKan.config.check_import.allrefs)

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
    os.path.join(os.path.dirname(__file__), "res", "he8_results_dialog_base.ui")
)


class ResultsDialog(_Dialog, RESULTS_CLASS):  # type: ignore
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
            fehlermeldung("Fehler im Programmcode (1)", "Nicht definierte Option")
            return

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
