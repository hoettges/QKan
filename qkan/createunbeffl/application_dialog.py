import logging
import os
import typing
import webbrowser
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTableWidget,
    QTableWidgetSelectionRange,
)
from qkan.database.qkan_utils import fehlermeldung

if typing.TYPE_CHECKING:
    from .application import CreateUnbefFl

logger = logging.getLogger("QKan.createunbeffl.application_dialog")
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "application_dialog_base.ui")
)


def click_help():
    """Reaktion auf Klick auf Help-Schaltfläche"""
    helpfile = (
        Path(__file__).parent / ".." / "doc/sphinx/build/html/Qkan_Formulare.html"
    )
    webbrowser.open_new_tab(str(helpfile) + "#erzeugen-der-unbefestigten-flachen")


class CreateUnbefFlDialog(QDialog, FORM_CLASS):
    button_box: QDialogButtonBox

    cb_selActive: QCheckBox
    cb_autokorrektur: QCheckBox
    cb_geomMakeValid: QCheckBox

    label_10: QLabel
    label_4: QLabel
    lf_anzahl_tezg: QLabel
    tw_selAbflparamTeilgeb: QTableWidget

    def __init__(self, plugin: "CreateUnbefFl", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        self.button_box.helpRequested.connect(click_help)
        self.cb_selActive.stateChanged.connect(self.click_sel_active)
        self.tw_selAbflparamTeilgeb.itemClicked.connect(self.click_param_teilgebiete)

    def click_param_teilgebiete(self):
        """Reaktion auf Klick in Tabelle"""

        self.cb_selActive.setChecked(True)
        self.count_selection()

    def click_sel_active(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selActive.isChecked():
            # Nix tun ...
            logger.debug("\nChecked = True")
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.tw_selAbflparamTeilgeb.rowCount()
            _range = QTableWidgetSelectionRange(0, 0, anz - 1, 4)
            self.tw_selAbflparamTeilgeb.setRangeSelected(_range, False)
            logger.debug("\nChecked = False\nQWidget: anzahl = {}".format(anz))

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def count_selection(self):
        """
        Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen TEZG-Flächen
        """

        selected_abflparam = list_selected_tab_items(self.tw_selAbflparamTeilgeb)

        # Aufbereiten für SQL-Abfrage

        # Unterschiedliches Vorgehen, je nachdem ob mindestens eine oder keine Zeile
        # ausgewählt wurde

        # if len(selected_abflparam) == 0:
        # anzahl = sum([int(attr[-2]) for attr in self.listetezg])
        # else:
        # anzahl = sum([int(attr[-2]) for attr in selected_abflparam])

        # Vorbereitung des Auswahlkriteriums für die SQL-Abfrage: Kombination aus abflussparameter und teilgebiet
        # Dieser Block ist identisch in k_unbef und in application enthalten

        if len(selected_abflparam) == 0:
            auswahl = ""
        elif len(selected_abflparam) == 1:
            auswahl = " AND"
        elif len(selected_abflparam) >= 2:
            auswahl = " AND ("
        else:
            fehlermeldung("Interner Fehler", "Fehler in Fallunterscheidung!")
            return False

        # Anfang SQL-Krierien zur Auswahl der tezg-Flächen
        first = True
        for attr in selected_abflparam:
            if attr[4] == "None" or attr[1] == "None":
                fehlermeldung(
                    "Datenfehler: ",
                    'In den ausgewählten Daten sind noch Datenfelder nicht definiert ("NULL").',
                )
                return False
            if first:
                first = False
                auswahl += f""" (tezg.abflussparameter = '{attr[0]}' AND
                                tezg.teilgebiet = '{attr[1]}')"""
            else:
                auswahl += f""" OR\n      (tezg.abflussparameter = '{attr[0]}' AND
                                tezg.teilgebiet = '{attr[1]}')"""

        if len(selected_abflparam) >= 2:
            auswahl += ")"
        # Ende SQL-Krierien zur Auswahl der tezg-Flächen

        # Trick: Der Zusatz "WHERE 1" dient nur dazu, dass der Block zur Zusammenstellung
        # von 'auswahl' identisch mit dem Block in 'k_unbef.py' bleiben kann...

        if not self.plugin.db_qkan.sql(
            f"SELECT count(*) AS anz FROM tezg WHERE 1{auswahl}",
            "QKan.CreateUnbefFlaechen (5)",
        ):
            del self.plugin.db_qkan
            return False

        data = self.plugin.db_qkan.fetchone()

        if not (data is None):
            self.lf_anzahl_tezg.setText("{}".format(data[0]))
        else:
            self.lf_anzahl_tezg.setText("0")


def list_selected_tab_items(table_widget: QTableWidget, n_cols: int = 5) -> typing.List:
    """
    Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen
    
    :param table_widget:    Tabelle zur Auswahl der Arten von Haltungsflächen.
    :param n_cols:          Anzahl Spalten des tableWidget-Elements
    """
    items = table_widget.selectedItems()
    anz = len(items)
    n_rows = anz // n_cols

    if len(items) > n_cols:
        # mehr als eine Zeile ausgewählt
        if table_widget.row(items[1]) == 1:
            # Elemente wurden spaltenweise übergeben
            liste = [[el.text() for el in items][i:anz:n_rows] for i in range(n_rows)]
        else:
            # Elemente wurden zeilenweise übergeben
            liste = [[el.text() for el in items][i : i + 5] for i in range(0, anz, 5)]
    else:
        # Elemente wurden zeilenweise übergeben oder Liste ist leer
        liste = [[el.text() for el in items][i : i + 5] for i in range(0, anz, 5)]

    return liste
