import os
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QRadioButton,
    QWidget,
)

from qkan import list_selected_items
from qkan.database.qkan_utils import sqlconditions

from . import QKanDBDialog, logger

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_runoffparams, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_runoffparams.ui")
)


class RunoffParamsDialog(QKanDBDialog, FORM_CLASS_runoffparams):  # type: ignore
    button_box: QDialogButtonBox

    cb_selParActive: QCheckBox
    cb_selTgbActive: QCheckBox

    lf_anzahl_flaechen: QLabel

    lw_abflussparameter: QListWidget
    lw_teilgebiete: QListWidget

    rb_dyna: QRadioButton
    rb_fliesszeiten: QRadioButton
    rb_itwh: QRadioButton
    rb_kaskade: QRadioButton
    rb_maniak: QRadioButton
    rb_schwerpunktlaufzeit: QRadioButton

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent, readonly=True)

        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)
        self.lw_abflussparameter.itemClicked.connect(self.click_lw_abflussparam)
        self.cb_selTgbActive.stateChanged.connect(self.click_tgb_selection)
        self.cb_selParActive.stateChanged.connect(self.click_par_selection)
        self.button_box.helpRequested.connect(self.click_help)
        self.rb_itwh.toggled.connect(self.toggle_itwh)

        self.db_qkan = None

    def click_lw_teilgebiete(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selTgbActive.setChecked(True)
        self.count_selection()

    def click_lw_abflussparam(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selParActive.setChecked(True)
        self.count_selection()

    def click_tgb_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selTgbActive.isChecked():
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

    def click_par_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selParActive.isChecked():
            # Nix tun ...
            logger.debug("\nChecked = True")
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_abflussparameter.count()
            for i in range(anz):
                item = self.lw_abflussparameter.item(i)
                item.setSelected(False)
                # self.lw_abflussparameter.setItemSelected(item, False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def toggle_itwh(self) -> None:
        """Reagiert auf Auswahl itwh und deaktiviert entsprechend die Option Fließzeiten"""

        if self.rb_itwh.isChecked():
            if self.rb_fliesszeiten.isChecked():
                self.rb_kaskade.setChecked(True)
            self.rb_fliesszeiten.setEnabled(False)
        else:
            self.rb_fliesszeiten.setEnabled(True)

    def count_selection(self) -> None:
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        if not self.db_qkan.connected:
            logger.debug("Error in RunoffParamsDialog.count_selection: db_qkan nicht verbunden...")
            return

        liste_teilgebiete: List[str] = list_selected_items(self.lw_teilgebiete)
        liste_abflussparameter: List[str] = list_selected_items(
            self.lw_abflussparameter
        )

        # Auswahl der zu bearbeitenden Flächen
        auswahl = sqlconditions(
            "WHERE",
            ["teilgebiet", "abflussparameter"],
            [liste_teilgebiete, liste_abflussparameter],
        )

        logger.debug(f'RunoffParamsDialog.count_selection: auswahl = {auswahl}')

        if not self.db_qkan.sql(
            f"SELECT count(*) AS anzahl FROM flaechen {auswahl}",
            "RunoffParamsDialog.count_selection (1)",
        ):
            return
        daten = self.db_qkan.fetchone()

        logger.debug(f'RunoffParamsDialog.count_selection: daten = {daten}')

        if daten is not None:
            self.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.lf_anzahl_flaechen.setText("0")

    def click_help(self) -> None:
        help_file = "https://qkan.eu/Qkan_Formulare.html#berechnung-von-oberflachenabflussparametern"
        os.startfile(help_file)
