import logging
import os
from pathlib import Path
from typing import Callable, List, Optional

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QStandardPaths
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
from qkan import QKan, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan

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
    cb_flaechen: QCheckBox
    cb_rohrprofile: QCheckBox
    cb_abflussparameter: QCheckBox
    cb_bodenklassen: QCheckBox
    cb_einleitdirekt: QCheckBox
    cb_aussengebiete: QCheckBox
    cb_einzugsgebiete: QCheckBox

    cb_tezg: QCheckBox

    rb_update: QRadioButton
    rb_append: QRadioButton

    lw_teilgebiete: QListWidget

    db_qkan: DBConnection

    # cb_export_schaechte: QCheckBox
    # cb_export_auslaesse: QCheckBox
    # cb_export_speicher: QCheckBox
    # cb_export_haltungen: QCheckBox
    # cb_export_pumpen: QCheckBox
    # cb_export_wehre: QCheckBox

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
        # self.pb_database.clicked.connect(self.select_database)    # ergibt sich aus Projekt
        self.pb_exportdb.clicked.connect(self.select_exportdb)
        self.pb_template.clicked.connect(self.select_template)
        # self.button_box.helpRequested.connect(self.click_help)

        # Aktionen zu lw_teilgebiete: QListWidget
        self.cb_selActive.stateChanged.connect(self.click_selection)
        self.lw_teilgebiete.itemClicked.connect(self.count_selection)
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)

        # Init fields

        # Datenbanken und Vorlagen aus config übernehmen
        # self.tf_database.setText(QKan.config.he8.database)
        self.tf_exportdb.setText(QKan.config.he8.export_file)
        self.tf_template.setText(QKan.config.he8.template)

        # Auswahl der zu exportierenden Tabellen
        self.cb_haltungen.setChecked(QKan.config.check_export.haltungen)
        self.cb_schaechte.setChecked(QKan.config.check_export.schaechte)
        self.cb_auslaesse.setChecked(QKan.config.check_export.auslaesse)
        self.cb_speicher.setChecked(QKan.config.check_export.speicher)
        self.cb_pumpen.setChecked(QKan.config.check_export.pumpen)
        self.cb_wehre.setChecked(QKan.config.check_export.wehre)
        self.cb_flaechen.setChecked(QKan.config.check_export.flaechen)
        self.cb_rohrprofile.setChecked(QKan.config.check_export.rohrprofile)
        self.cb_abflussparameter.setChecked(QKan.config.check_export.abflussparameter)
        self.cb_bodenklassen.setChecked(QKan.config.check_export.bodenklassen)
        self.cb_einleitdirekt.setChecked(QKan.config.check_export.einleitdirekt)
        self.cb_aussengebiete.setChecked(QKan.config.check_export.aussengebiete)
        self.cb_einzugsgebiete.setChecked(QKan.config.check_export.einzugsgebiete)
        self.cb_tezg.setChecked(QKan.config.check_export.tezg)

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
            # self.default_dir = os.path.dirname(filename)

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
        """Füllt Auswahllisten im Dialog"""

        self.db_qkan = db_qkan
        # Check, ob alle Teilgebiete in Flächen, Schächten und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "he8porter.application_dialog.connectQKanDB (1) "):
            return False

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "he8porter.application_dialog.connectQKanDB (2) "):
            return False

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM schaechte 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "he8porter.application_dialog.connectQKanDB (3) "):
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
        return True

    def connectHEDB(self, database_he: str) -> None:
        """Attach SQLite-Database with HE8 Data"""
        sql = f'ATTACH DATABASE "{database_he}" AS he'

        if self.db_qkan is None or not self.db_qkan.sql(
            sql, "He8Porter.run_export_to_he8 Attach HE8"
        ):
            return


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
        self.tf_database.setText(QKan.config.he8.database)
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
