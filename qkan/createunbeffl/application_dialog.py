import os
from typing import TYPE_CHECKING, List, Optional, Union

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTableWidgetSelectionRange,
    QWidget,
)

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import get_database_QKan
from qkan.tools.dialogs import QKanDialog
from .k_unbef import create_unpaved_areas
from ..utils import get_logger, QkanAbortError

if TYPE_CHECKING:
    from .application import CreateUnbefFl

logger = get_logger("QKan.createunbeffl.application_dialog")
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "application_dialog_base.ui")
)


def list_selected_tab_items(table_widget: QTableWidget, n_cols: int = 5) -> List:
    """Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

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


class CreateUnbefFlDialog(QKanDialog, FORM_CLASS):  # type: ignore
    button_box: QDialogButtonBox

    cb_selectedTgbs: QCheckBox
    cb_autokorrektur: QCheckBox
    cb_geomMakeValid: QCheckBox

    label_10: QLabel
    label_4: QLabel
    lf_anzahl_tezg: QLabel
    tw_selAbflparamTeilgeb: QTableWidget

    def __init__(self, plugin: "CreateUnbefFl", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.db_name: Union[str, None] = None

        self.button_box.helpRequested.connect(self.click_help)
        self.cb_selectedTgbs.stateChanged.connect(self.click_sel_active)
        self.tw_selAbflparamTeilgeb.itemClicked.connect(self.click_param_teilgebiete)

    def click_param_teilgebiete(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selectedTgbs.setChecked(True)
        self.count_selection()

    def click_sel_active(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selectedTgbs.isChecked():
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

    def count_selection(self) -> None:
        """
        Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen TEZG-Flächen
        """

        if not self.db_name:
            logger.error("Programmfehler: db_name is not initialized.")
            raise QkanAbortError

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

        if len(selected_abflparam) > 0:
            auswahl = ' AND ( (' + \
              ') OR\n ('.join(
                  [
                      f"tezg.abflussparameter = '{attr[0]}' AND tezg.teilgebiet = '{attr[1]}'"
                      for attr in selected_abflparam if attr[1] is not None
                  ]
              ) + '))'
        else:
            auswahl = ''

        # Trick: Der Zusatz "WHERE 1" dient nur dazu, dass der Block zur Zusammenstellung
        # von 'auswahl' identisch mit dem Block in 'k_unbef.py' bleiben kann...

        with DBConnection(dbname=self.db_name) as db_qkan:
            if not db_qkan.connected:
                return

            # db_qkan.loadmodule('createunbeffl')

            if not db_qkan.sql(
                f"SELECT count(*) AS anz FROM tezg WHERE 1{auswahl}",
                "QKan.CreateUnbefFlaechen (5)",
            ):
                logger.info(
                    "CreateUnbefFlDialog.count_selection: QKan-Datenbank wurde wegen eines Fehlers geschlossen"
                )
                return

            data = db_qkan.fetchone()

        if not (data is None):
            self.lf_anzahl_tezg.setText("{}".format(data[0]))
        else:
            self.lf_anzahl_tezg.setText("0")

    def run(self) -> None:
        """Run method that performs all the real work"""

        get_database_QKan()
        database_qkan, epsg = QKan.config.database.qkan, QKan.config.epsg
        if not database_qkan:
            logger.error_code(
                "CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )

        self.db_name = database_qkan

        # Abfragen der Tabelle tezg nach verwendeten Abflussparametern
        with DBConnection(dbname=database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error_user(
                    "Fehler in createunbeffl.application:\n"
                    f"QKan-Datenbank {database_qkan} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"
                )
                return

            # Kontrolle, ob in Tabelle "abflussparameter" ein Datensatz für unbefestigte Flächen vorhanden ist
            # (Standard: apnam = '$Default_Unbef')

            sql = """SELECT apnam
                FROM abflussparameter
                WHERE bodenklasse IS NOT NULL AND trim(bodenklasse) <> ''"""

            if not db_qkan.sql(sql, "createunbeffl.run (1)"):
                return

            data = db_qkan.fetchone()

            if data is None:
                if QKan.config.autokorrektur:
                    sql = """
                    INSERT INTO abflussparameter
                        ('apnam', 'kommentar', 'anfangsabflussbeiwert', 'endabflussbeiwert', 'benetzungsverlust', 
                        'muldenverlust', 'benetzung_startwert', 'mulden_startwert', 'bodenklasse', 
                        'createdat') 
                    VALUES (
                        '$Default_Unbef', 'von QKan ergänzt', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', '13.01.2011 08:44:50'
                        )
                    """
                    if not db_qkan.sql(sql, "createunbeffl.run (2)"):
                        return
                else:
                    logger.error_user(
                        "Datenfehler: "
                        'Bitte ergänzen Sie in der Tabelle "abflussparameter" einen Datensatz \n'
                        'für unbefestigte Flächen ("bodenklasse" darf nicht leer oder NULL sein)',
                    )
                    return

            sql = """SELECT te.abflussparameter, te.teilgebiet, bk.bknam, count(*) AS anz, 
                    CASE WHEN te.abflussparameter IS NULL THEN 'Fehler: Kein Abflussparameter angegeben' 
					     WHEN te.teilgebiet IS NULL THEN 'Fehler: Teilgebiet nicht definiert'
					ELSE
                        CASE WHEN bk.infiltrationsrateanfang IS NULL THEN 'Fehler: Keine Bodenklasse angegeben' 
                             WHEN bk.infiltrationsrateanfang < 0.00001 THEN 'Fehler: undurchlässige Bodenart'
                             ELSE ''
                        END
                    END AS status
                                FROM tezg AS te
                                LEFT JOIN abflussparameter AS ap
                                ON te.abflussparameter = ap.apnam
                                LEFT JOIN bodenklassen AS bk
                                ON bk.bknam = ap.bodenklasse
                                GROUP BY abflussparameter, teilgebiet"""
            if not db_qkan.sql(sql, "createunbeffl.run (4)"):
                return

            listetezg = db_qkan.fetchall()
            nzeilen = len(listetezg)
            self.tw_selAbflparamTeilgeb.setRowCount(nzeilen)
            self.tw_selAbflparamTeilgeb.setHorizontalHeaderLabels(
                [
                    "Abflussparameter",
                    "Teilgebiet",
                    "Bodenklasse",
                    "Anzahl",
                    "Anmerkungen",
                    "",
                ]
            )
            self.tw_selAbflparamTeilgeb.setColumnWidth(
                0, 144
            )  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
            self.tw_selAbflparamTeilgeb.setColumnWidth(1, 140)
            self.tw_selAbflparamTeilgeb.setColumnWidth(2, 90)
            self.tw_selAbflparamTeilgeb.setColumnWidth(3, 50)
            self.tw_selAbflparamTeilgeb.setColumnWidth(4, 200)
            for i, elem in enumerate(listetezg):
                for j, item in enumerate(elem):
                    cell = "{}".format(elem[j])
                    self.tw_selAbflparamTeilgeb.setItem(i, j, QTableWidgetItem(cell))
                    self.tw_selAbflparamTeilgeb.setRowHeight(i, 20)

            # Autokorrektur
            self.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

            self.count_selection()

            # show the dialog
            self.show()
            # Run the dialog event loop
            result = self.exec()
            logger.debug("result = {}".format(repr(result)))
            # See if OK was pressed
            if result:
                selected_abflparam = list_selected_tab_items(
                    self.tw_selAbflparamTeilgeb
                )
                logger.debug(
                    "\nliste_selAbflparamTeilgeb (1): {}".format(selected_abflparam)
                )
                autokorrektur: bool = self.cb_autokorrektur.isChecked()

                QKan.config.autokorrektur = autokorrektur
                QKan.config.save()

                # Start der Verarbeitung

                # Modulaufruf in Logdatei schreiben

                iface = QKan.instance.iface

                logger.debug(
                    f"""QKan-Modul Aufruf
                    createUnbefFlaechen(
                        iface, 
                        self.dbQK, 
                        {selected_abflparam}, 
                        {autokorrektur}
                    )"""
                )

                if not create_unpaved_areas(
                    iface, db_qkan, selected_abflparam, autokorrektur
                ):
                    return

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_Flaechenverarbeitung.html#erzeugen-von-unbefestigten-flachen"
        os.startfile(help_file)
