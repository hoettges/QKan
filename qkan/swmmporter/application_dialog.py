import logging
import os
from pathlib import Path
from typing import Callable, Optional

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

logger = logging.getLogger("QKan.swmm.application_dialog")


EXPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "exportSWMM.ui")
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
        logger.debug(
            f"swmm.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr

class ExportDialog(_Dialog, EXPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_SWMM_template: QLineEdit
    tf_SWMM_dest: QLineEdit

    cb_use_templatedir: QCheckBox

    pb_database: QPushButton
    pb_SWMM_template: QPushButton
    pb_SWMM_dest: QPushButton

    rb_flaechen: QRadioButton
    rb_tezg: QRadioButton

    lw_teilgebiete: QListWidget

    db_qkan: DBConnection

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        self.default_dir = default_dir

        # Attach events
        #self.pb_database.clicked.connect(self.select_database)    # ergibt sich aus Projekt
        self.pb_SWMM_dest.clicked.connect(self.select_exportdb)
        self.pb_SWMM_template.clicked.connect(self.select_template)
        self.cb_flaechen.clicked.connect(self.check_flaechen)
        self.cb_tezg_hf.clicked.connect(self.check_tezg_hf)
        #self.button_box.helpRequested.connect(self.click_help)

        # Aktionen zu lw_teilgebiete: QListWidget
        self.cb_selActive.stateChanged.connect(self.click_selection)
        self.lw_teilgebiete.itemClicked.connect(self.count_selection)      # ist schon in click_lw_teilgebiete enthalten
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)

        # Init fields

        # Datenbanken und Vorlagen aus config übernehmen
        self.tf_database.setText(QKan.config.database.qkan)

        self.tf_database.setText(QKan.config.swmm.export_file)
        self.tf_SWMM_template.setText(QKan.config.swmm.template)


    def select_template(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        #if self.cb_use_templatedir.isChecked():

        # TODO: Replace with QKan.config.project.template?
        #   searchdir = str(Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs")
        #else:
        searchdir = self.default_dir

        # noinspection PyCallByClass,PyArgumentList
        filename, _ = QFileDialog.getOpenFileName(
             self,
             self.tr("Vorlage für die zu erstellende SWMM-Datei"),
             searchdir,
             "*.INP",
        )
        if filename:
            self.tf_SWMM_template.setText(filename)
            self.default_dir = os.path.dirname(filename)

    def select_exportdb(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende SWMM-Datei"),
            self.default_dir,
            "*.INP",
        )
        if filename:
            self.tf_SWMM_dest.setText(filename)
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
        self.db_qkan = DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg)

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

        if not self.db_qkan.sql(sql, "QKan_ExportSWMM.application.countselection (1)"):
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
        if not self.db_qkan.sql(sql, "QKan_ExportSWMM.application.countselection (2) "):
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
        if not self.db_qkan.sql(sql, "QKan_ExportSWMM.application.countselection (3) "):
            return False
        daten = self.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.lf_anzahl_haltungen.setText("0")
        return True

    def prepareDialog(self, db_qkan) -> bool:
         """Füllt Auswahllisten im Export-Dialog"""

         self.db_qkan = DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg)
         #self.db_qkan = db_qkan
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
    os.path.join(os.path.dirname(__file__), "res", "importSWMM.ui")
)


class ImportDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    tf_database: QLineEdit
    tf_import: QLineEdit
    tf_project: QLineEdit

    pb_import: QPushButton
    pb_project: QPushButton


    epsg: QgsProjectionSelectionWidget

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pb_import.clicked.connect(self.select_import)
        self.pb_project.clicked.connect(self.select_project)

        # Init fields
        self.tf_database.setText(QKan.config.database.qkan)
        self.tf_import.setText(QKan.config.xml.import_file)

        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_project.setText(QKan.config.project.file)


    def select_import(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende SWMM-Datei"),
            self.default_dir,
            "*.inp",
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

