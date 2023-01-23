import logging
import os
import webbrowser
from pathlib import Path
from typing import Callable, List, Optional

from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QWidget,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QCheckBox
)
from qgis.utils import pluginDirectory

from qkan import QKan, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

logger = logging.getLogger("QKan.datacheck.application_dialog")


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
            f"datacheck.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_datacheck.ui")
)


class PlausiDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    lw_themen: QListWidget
    le_anzahl: QLineEdit

    db_qkan: DBConnection

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None
        ):
        # noinspection PyCallByClass,PyArgumentList
        super().__init__(default_dir, tr, parent)

        self.lw_themen.itemClicked.connect(self.click_lw_themen)
        self.buttonBox.helpRequested.connect(self.click_help)

    def click_lw_themen(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.count_selection()

    def count_selection(self) -> bool:
        """
        Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen
        """

        self.themen = list_selected_items(self.lw_themen)

        anzahl = 0
        
        for thema in self.themen:
            anzahl += self.themesdata[thema]

        self.le_anzahl.setText(str(anzahl))
        return True

    def prepareDialog(self, db_qkan) -> bool:
        """Füllt Themenliste der Plausibilitätsabfragen"""
        self.db_qkan = db_qkan

        # gespeicherte Optionen abrufen
        self.cb_keepdata.setChecked(QKan.config.plausi.keepdata)

        # Anlegen der Tabelle zur Auswahl der Themen
        # Zunächst wird die Liste der beim letzten Mal gewählten Themen aus config gelesen
        self.themen: list[str] = QKan.config.plausi.themen

        # Abfragen der Tabelle plausisql nach Themen, wird gespeichert als dict in self.themesdata
        sql = '''SELECT gruppe, count(*) AS n FROM pruefsql GROUP BY gruppe;'''
        if not self.db_qkan.sql(sql, "datacheck.application_dialog.connectQKanDB (1) "):
            return False
        data = self.db_qkan.fetchall()

        self.themesdata: dict[str, int] = dict(data)                    # dict(Themen: Anzahl) zur Verwaltung der Anzahl ausgewählter Plausibilitätsabfragen
        themeslist: list[str] = [elem[0] for elem in data]              # Liste der Themen
        self.lw_themen.clear()

        for ielm, elem in enumerate(themeslist):
            self.lw_themen.addItem(QListWidgetItem(elem))
            try:
                if elem in self.themen:
                    self.lw_themen.setCurrentRow(ielm)
            except BaseException as err:
                fehlermeldung(
                    (
                        "datacheck.application_dialog.connectQKanDB, "
                        f"Fehler in elem = {elem}\n"
                    ),
                    repr(err),
                )

        self.count_selection()

        return True

    def selected_themes(self):
        """Gibt die gewählten Themen zurück"""
        return self.themen

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_flaechen.html?highlight=plausibili"
        os.startfile(help_file)


