import logging
import os
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
    QDialogButtonBox,
)

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
    button_box: QDialogButtonBox
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
        # noinspection PyArgumentList
        super().__init__(default_dir, tr, parent)

        self.default_dir = default_dir

        # Attach events
        self.pb_SWMM_dest.clicked.connect(self.select_exportfile)
        self.pb_SWMM_template.clicked.connect(self.select_template)
        self.button_box.helpRequested.connect(self.click_help)

        # Aktionen zu lw_teilgebiete: QListWidget
        self.cb_selActive.stateChanged.connect(self.click_selection)
        #self.lw_teilgebiete.itemClicked.connect(self.count_selection)      # ist schon in click_lw_teilgebiete enthalten
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
            # self.default_dir = os.path.dirname(filename)

    def select_exportfile(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende SWMM-Datei"),
            self.default_dir,
            "*.INP",
        )
        if filename:
            self.tf_SWMM_dest.setText(filename)
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
        """ Zählung mit Herstellung der Datenbankverbindung
        """
        with DBConnection() as db_qkan:
            self.count(db_qkan)

    def count(self, db_qkan: DBConnection) -> bool:
        """ Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
            der betroffenen Flächen und Haltungen
        """
        if not db_qkan.connected:
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

        if not db_qkan.sql(sql, "QKan_ExportSWMM.application.countselection (1)"):
            return False
        daten = db_qkan.fetchone()
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
        if not db_qkan.sql(sql, "QKan_ExportSWMM.application.countselection (2) "):
            return False
        daten = db_qkan.fetchone()
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
        if not db_qkan.sql(sql, "QKan_ExportSWMM.application.countselection (3) "):
            return False
        daten = db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.lf_anzahl_haltungen.setText("0")
        return True

    def prepareDialog(self, db_qkan: DBConnection) -> bool:
        """Füllt Auswahllisten im Export-Dialog"""

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
        if not db_qkan.sql(sql, "swmmporter.application_dialog.connectQKanDB (1) "):
            return False

        db_qkan.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        teilgebiete = QKan.config.selections.teilgebiete

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not db_qkan.sql(sql, "swmmporter.application_dialog.connectQKanDB (4) "):
            return False
        daten = db_qkan.fetchall()
        self.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in teilgebiete:
                    self.lw_teilgebiete.setCurrentRow(ielem)
            except BaseException as err:
                fehlermeldung(
                    (
                        "swmmporter.application_dialog.connectQKanDB, "
                        f"Fehler in elem = {elem}\n"
                    ),
                    repr(err),
                )

        # Initialisierung der Anzeige der Anzahl zu exportierender Objekte
        self.count(db_qkan)

        return True

    #def check_flaechen(self) -> None:
    #    # noinspection PyArgumentList,PyCallByClass
    #    if self.cb_flaechen.isChecked():
    #        QKan.config.check_export.tezg_hf = False
    #        self.cb_tezg_hf.setChecked(False)

    #def check_tezg_hf(self) -> None:
    #    # noinspection PyArgumentList,PyCallByClass
    #    if self.cb_tezg_hf.isChecked():
    #        QKan.config.check_export.flaechen = False
    #        self.cb_flaechen.setChecked(False)

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_SWMM.html#export-in-swmm-datei"
        os.startfile(help_file)


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "importSWMM.ui")
)


class ImportDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    button_box: QDialogButtonBox
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
        self.pb_database.clicked.connect(self.select_database)
        self.button_box.helpRequested.connect(self.click_help)

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

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_SWMM.html#import-aus-swmm-datei"
        os.startfile(help_file)

