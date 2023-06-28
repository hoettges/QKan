# -*- coding: utf-8 -*-
import logging
import os
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from qgis.core import Qgis
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QWidget,
)

from qkan import list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.tools.dialogs import QKanDialog

from .k_link import reload_group, store_group

if TYPE_CHECKING:
    from .application import LinkFl

logger = logging.getLogger("QKan.linkflaechen.application_dialog")

FORM_CLASS_assigntgeb, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_assigntgeb.ui")
)
FORM_CLASS_createlinefl, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_createlinefl.ui")
)
FORM_CLASS_createlinesw, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_createlinesw.ui")
)
FORM_CLASS_updatelinks, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_updatelinks.ui")
)
FORM_CLASS_managegroups, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_managegroups.ui")
)


class AssigntgebDialog(QDialog, FORM_CLASS_assigntgeb):  # type: ignore
    button_box: QDialogButtonBox

    cb_autokorrektur: QCheckBox
    cb_geomMakeValid: QCheckBox

    groupBox_2: QGroupBox

    lb_bufferradius: QLabel

    lw_teilgebiete: QListWidget

    rb_overlaps: QRadioButton
    rb_within: QRadioButton

    tf_bufferradius: QLineEdit

    unit_bufferradius: QLabel

    def __init__(self, parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.rb_within.clicked.connect(lambda _: self.enable_bufferradius(True))
        self.rb_overlaps.clicked.connect(lambda _: self.enable_bufferradius(False))

    def enable_bufferradius(self, status: bool = True) -> None:
        """
        Aktiviert/Deaktiviert die Eingabe der Pufferbreite abhängig von der
        Auswahloption
        """

        self.lb_bufferradius.setEnabled(status)
        self.tf_bufferradius.setEnabled(status)
        self.unit_bufferradius.setEnabled(status)


class CreatelineflDialog(QKanDialog, FORM_CLASS_createlinefl):  # type: ignore
    button_box: QDialogButtonBox

    cb_autokorrektur: QCheckBox
    cb_geomMakeValid: QCheckBox
    cb_linksInTezg: QCheckBox
    cb_regardTezg: QCheckBox
    cb_selFlActive: QCheckBox
    cb_selHalActive: QCheckBox
    cb_selTgbActive: QCheckBox

    lf_anzahl_flaechen: QLabel
    lf_anzahl_flaechsec: QLabel
    lf_anzahl_haltungen: QLabel

    lw_flaechen_abflussparam: QListWidget
    lw_hal_entw: QListWidget
    lw_teilgebiete: QListWidget

    rb_abstandkante: QRadioButton
    rb_abstandmittelpunkt: QRadioButton

    tf_fangradius: QLineEdit
    tf_suchradius: QLineEdit

    plugin: "LinkFl"

    def __init__(self, plugin: "LinkFl", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.lw_flaechen_abflussparam.itemClicked.connect(
            self.click_lw_flaechen_abflussparam
        )
        self.lw_hal_entw.itemClicked.connect(self.click_lw_hal_entw)
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)
        self.cb_selFlActive.stateChanged.connect(self.click_selection)
        self.cb_selHalActive.stateChanged.connect(self.click_hal_selection)
        self.cb_selTgbActive.stateChanged.connect(self.click_tgb_selection)
        self.button_box.helpRequested.connect(self.click_help_fl)
        self.tf_fangradius.textChanged.connect(self.changed_tf_fangradius)

    def click_lw_flaechen_abflussparam(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selFlActive.setChecked(True)
        self.count_selection()

    def click_lw_hal_entw(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selHalActive.setChecked(True)
        self.count_selection()

    def click_lw_teilgebiete(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selTgbActive.setChecked(True)
        self.count_selection()

    def click_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selFlActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_flaechen_abflussparam.count()
            for i in range(anz):
                item = self.lw_flaechen_abflussparam.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def click_hal_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selHalActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_hal_entw.count()
            for i in range(anz):
                item = self.lw_hal_entw.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def click_tgb_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selTgbActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_teilgebiete.count()
            for i in range(anz):
                item = self.lw_teilgebiete.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def changed_tf_fangradius(self) -> None:
        """Gibt eine Warnung, falls Fangradius zu groß"""
        try:
            fangradius = float(self.tf_fangradius.text().replace(",", "."))
        except:
            return
        if fangradius > 0.5:
            self.tf_fangradius.setStyleSheet("border: 2px solid red; color: red")
            self.lf_warning.setText("Wert zu groß!")
            self.lf_warning.setStyleSheet("color: red; font: bold;")
            self.lf_unit_fangradius.setStyleSheet("color: red")
        else:
            self.tf_fangradius.setStyleSheet("border: 1px solid black;")
            self.lf_warning.setText("")
            self.lf_warning.setStyleSheet("color: black; font: bold;")
            self.lf_unit_fangradius.setStyleSheet("color: black")

    def count_selection(self) -> None:
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""

        liste_flaechen_abflussparam: List[str] = list_selected_items(
            self.lw_flaechen_abflussparam
        )
        liste_hal_entw: List[str] = list_selected_items(self.lw_hal_entw)
        liste_teilgebiete: List[str] = list_selected_items(self.lw_teilgebiete)
        # Aufbereiten für SQL-Abfrage

        # Zu berücksichtigende ganze Flächen zählen
        if len(liste_flaechen_abflussparam) == 0:
            # Keine Auswahl. Soll eigentlich nicht vorkommen, funktioniert aber...
            auswahl = ""
            logger.debug(
                "liste_flaechen_abflussparam:\n{}".format(liste_flaechen_abflussparam)
            )
        else:
            auswahl = " AND flaechen.abflussparameter in ('{}')".format(
                "', '".join(liste_flaechen_abflussparam)
            )

        if len(liste_teilgebiete) != 0:
            auswahl += " and flaechen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        with DBConnection(self.plugin.database_name) as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in linkflaechen.applications_dialog.CreatelineflDialog.count_selection:\n"
                    "QKan-Datenbank %s wurde nicht"
                    " gefunden oder war nicht aktuell!\nAbbruch!", self.database_qkan
                )
                return

            sql = f"""SELECT count(*) AS anzahl FROM flaechen
                    WHERE ((aufteilen <> 'ja' AND not aufteilen) OR aufteilen IS NULL){auswahl}"""

            if not db_qkan.sql(sql, "QKan_LinkFlaechen.countselectionfl (1)"):
                return
            daten = db_qkan.fetchone()
            if not (daten is None):
                self.lf_anzahl_flaechen.setText(str(daten[0]))
            else:
                self.lf_anzahl_flaechen.setText("0")

            # Zu berücksichtigende zu verschneidende Flächen zählen

            sql = (
                f"SELECT count(*) AS anzahl FROM flaechen WHERE aufteilen = 'ja' {auswahl}"
            )
            logger.debug("sql Flaechen zu verschneiden:\n{}".format(sql))
            if not db_qkan.sql(sql, "QKan_LinkFlaechen.countselectionfl (2)"):
                return
            daten = db_qkan.fetchone()
            if not (daten is None):
                self.lf_anzahl_flaechsec.setText(str(daten[0]))
            else:
                self.lf_anzahl_flaechsec.setText("0")

            # Zu berücksichtigende Haltungen zählen
            if len(liste_hal_entw) == 0:
                auswahl = ""
            else:
                auswahl = " WHERE haltungen.entwart in ('{}')".format(
                    "', '".join(liste_hal_entw)
                )

            if len(liste_teilgebiete) != 0:
                if auswahl == "":
                    auswahl = " WHERE haltungen.teilgebiet in ('{}')".format(
                        "', '".join(liste_teilgebiete)
                    )
                else:
                    auswahl += " and haltungen.teilgebiet in ('{}')".format(
                        "', '".join(liste_teilgebiete)
                    )

            sql = f"SELECT count(*) AS anzahl FROM haltungen {auswahl}"
            if not db_qkan.sql(sql, "QKan_LinkFlaechen.countselectionfl (3)"):
                return
            daten = db_qkan.fetchone()
            if not (daten is None):
                self.lf_anzahl_haltungen.setText(str(daten[0]))
            else:
                self.lf_anzahl_haltungen.setText("0")

    def click_help_fl(self) -> None:
        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_Formulare.html#automatisches-erzeugen-von-flachenanbindungen"
        os.startfile(help_file)


class CreatelineswDialog(QDialog, FORM_CLASS_createlinesw):  # type: ignore

    button_box: QDialogButtonBox
    cb_selHalActive: QCheckBox
    cb_selTgbActive: QCheckBox

    groupBox_2: QGroupBox

    lf_anzahl_einleit: QLabel
    lf_anzahl_haltungen: QLabel

    lw_hal_entw: QListWidget
    lw_teilgebiete: QListWidget

    tf_suchradius: QLineEdit

    plugin: "LinkFl"

    def __init__(self, plugin: "LinkFl", parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        self.lw_hal_entw.itemClicked.connect(self.click_lw_hal_entw)
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)
        self.cb_selHalActive.stateChanged.connect(self.click_hal_selection)
        self.cb_selTgbActive.stateChanged.connect(self.click_tgb_selection)
        self.button_box.helpRequested.connect(self.click_help_sw)

    def click_lw_hal_entw(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selHalActive.setChecked(True)
        self.count_selection()

    def click_lw_teilgebiete(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selTgbActive.setChecked(True)
        self.count_selection()

    def click_hal_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selHalActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_hal_entw.count()
            for i in range(anz):
                item = self.lw_hal_entw.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def click_tgb_selection(self) -> None:
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selTgbActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_teilgebiete.count()
            for i in range(anz):
                item = self.lw_teilgebiete.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def count_selection(self) -> None:
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Haltungen"""

        liste_hal_entw: List[str] = list_selected_items(self.lw_hal_entw)
        liste_teilgebiete: List[str] = list_selected_items(self.lw_teilgebiete)
        # Aufbereiten für SQL-Abfrage

        # Zu berücksichtigende Haltungen zählen
        if len(liste_hal_entw) == 0:
            auswahl = ""                    # keine Einschränkung auf Teilgebiete
        else:
            auswahl = " WHERE haltungen.entwart in ('{}')".format(
                "', '".join(liste_hal_entw)
            )

        if len(liste_teilgebiete) != 0:
            if auswahl == "":
                auswahl = " WHERE haltungen.teilgebiet in ('{}')".format(
                    "', '".join(liste_teilgebiete)
                )
            else:
                auswahl += " and haltungen.teilgebiet in ('{}')".format(
                    "', '".join(liste_teilgebiete)
                )

        with DBConnection(self.plugin.database_name) as db_qkan:
            sql = f"SELECT count(*) AS anzahl FROM haltungen {auswahl}"
            if not db_qkan.sql(sql, "QKan_LinkFlaechen.countselectionsw (1)"):
                return
            daten = db_qkan.fetchone()
            if not (daten is None):
                self.lf_anzahl_haltungen.setText(str(daten[0]))
            else:
                self.lf_anzahl_haltungen.setText("0")

            # Zu berücksichtigende Direkteinleitungen zählen
            if len(liste_teilgebiete) != 0:
                auswahl = " WHERE einleit.teilgebiet in ('{}')".format(
                    "', '".join(liste_teilgebiete)
                )
            else:
                auswahl = ""

            sql = f"SELECT count(*) AS anzahl FROM einleit {auswahl}"
            if not db_qkan.sql(sql, "QKan_LinkFlaechen.countselectionsw (2)"):
                return
            daten = db_qkan.fetchone()
            if not (daten is None):
                self.lf_anzahl_einleit.setText(str(daten[0]))
            else:
                self.lf_anzahl_einleit.setText("0")

    def click_help_sw(self) -> None:
        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_Formulare.html#automatisches-erzeugen-von-anbindungen-von-einzeleinleitern"
        os.startfile(help_file)


class UpdateLinksDialog(QDialog, FORM_CLASS_updatelinks):  # type: ignore
    button_box: QDialogButtonBox

    cb_deleteGeomNone: QCheckBox
    cb_geomMakeValid: QCheckBox
    cb_linkfl: QCheckBox
    cb_linksw: QCheckBox

    groupBox: QGroupBox

    tf_fangradius: QLineEdit
    tf_qkDB: QLineEdit

    def __init__(self, parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.tf_fangradius.textChanged.connect(self.changed_tf_fangradius)

    def changed_tf_fangradius(self) -> None:
        """Gibt eine Warnung, falls Fangradius zu groß"""
        try:
            fangradius = float(self.tf_fangradius.text().replace(",", "."))
        except:
            return
        if fangradius > 0.5:
            self.tf_fangradius.setStyleSheet("border: 2px solid red; color: red")
            self.lf_warning.setText("Wert zu groß!")
            self.lf_warning.setStyleSheet("color: red; font: bold;")
            self.lf_unit_fangradius.setStyleSheet("color: red")
        else:
            self.tf_fangradius.setStyleSheet("border: 1px solid black;")
            self.lf_warning.setText("")
            self.lf_warning.setStyleSheet("color: black; font: bold;")
            self.lf_unit_fangradius.setStyleSheet("color: black")


class ManagegroupsDialog(QDialog, FORM_CLASS_managegroups):  # type: ignore
    button_box: QDialogButtonBox

    groupBox_2: QGroupBox
    groupBox_4: QGroupBox

    lw_gruppen: QListWidget

    pb_reloadgroup: QPushButton
    pb_storegroup: QPushButton

    tf_kommentar: QTextEdit
    tf_newgroup: QLineEdit

    tw_gruppenattr: QTableWidget

    # Extra
    gruppe: Optional[str] = None

    plugin: "LinkFl"

    def __init__(self, plugin: "LinkFl", parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        self.lw_gruppen.itemClicked.connect(self.click_lw_groups)
        self.pb_storegroup.clicked.connect(self.click_store_group)
        self.pb_reloadgroup.clicked.connect(self.click_reload_group)

    def click_reload_group(self) -> None:
        if not self.gruppe:
            return

        with DBConnection(self.plugin.database_name) as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in linkflaechen.application.connectQKanDB:\n"
                    "QKan-Datenbank %s wurde nicht gefunden oder war nicht aktuell!\nAbbruch!", self.database_name
                )
            reload_group(self.plugin.iface, db_qkan, self.gruppe)


        self.plugin.iface.messageBar().pushMessage(
            "Fertig!", "Teilgebiete wurden geladen!", level=Qgis.Info
        )

    def click_store_group(self) -> None:
        neuegruppe = self.tf_newgroup.text()
        if neuegruppe != "" and neuegruppe is not None:
            kommentar = self.tf_kommentar.toPlainText()
            if kommentar is None:
                kommentar = ""

            with DBConnection(self.plugin.database_name) as db_qkan:
                if not db_qkan.connected:
                    logger.error(
                        "Fehler in linkflaechen.application_dialog.click_store_group:\n"
                        "QKan-Datenbank %s wurde nicht gefunden oder war nicht aktuell!\nAbbruch!", self.database_name
                    )
                store_group(self.plugin.iface, db_qkan, neuegruppe, kommentar)

            self.show_groups()
            self.plugin.iface.messageBar().pushMessage(
                "Fertig!", "Teilgebiete wurden gespeichert", level=Qgis.Info
            )

    def click_lw_groups(self) -> None:
        """
        Funktion zum Abfragen der zugeordneten Teilgebiete, betroffenen Tabellen und
        Anzahl für eine ausgewählte Gruppe
        """

        # Angeklickte Gruppe aus QListWidget
        gr: List[str] = list_selected_items(self.lw_gruppen)
        if len(gr) > 0:
            self.gruppe = gr[0]  # Im Formular gesetzt: selectionMode = SingleSelection

            sql = """
                SELECT teilgebiet, tabelle, printf('%i',count(*)) AS Anzahl
                FROM gruppen
                WHERE grnam = ?
                GROUP BY tabelle, teilgebiet
                ORDER BY tabelle, teilgebiet
                """
            with DBConnection(self.plugin.database_name) as db_qkan:
                if not db_qkan.connected:
                    logger.error(
                        "Fehler in linkflaechen.application_dialog.click_lw_groups:\n"
                        "QKan-Datenbank %s wurde nicht gefunden oder war nicht aktuell!\nAbbruch!", self.database_name
                    )
                    return

                if not db_qkan.sql(
                    sql, "QKan_LinkFlaechen.listGroupAttr (1)", parameters=(self.gruppe,)
                ):
                    return
                daten = db_qkan.fetchall()

            logger.debug("\ndaten: {}".format(str(daten)))  # debug
            nzeilen = len(daten)
            self.tw_gruppenattr.setRowCount(nzeilen)
            # self.tw_gruppenattr.setHorizontalHeaderLabels(["Teilgebiet", "Tabelle", "Anzahl"])
            self.tw_gruppenattr.setColumnWidth(
                0, 174
            )  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
            self.tw_gruppenattr.setColumnWidth(1, 80)
            self.tw_gruppenattr.setColumnWidth(2, 50)
            for i, elem in enumerate(daten):
                for j, item in enumerate(elem):
                    self.tw_gruppenattr.setItem(i, j, QTableWidgetItem(elem[j]))
                    self.tw_gruppenattr.setRowHeight(i, 20)

    def show_groups(self) -> None:
        """Abfragen der Tabelle gruppen nach verwendeten vorhandenen Gruppen"""

        sql = """SELECT grnam FROM gruppen GROUP BY grnam"""

        with DBConnection(self.plugin.database_name) as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in linkflaechen.application_dialog.show_groups:\n"
                    "QKan-Datenbank %s wurde nicht gefunden oder war nicht aktuell!\nAbbruch!", self.database_name
                )
            if not db_qkan.sql(sql, "QKan_LinkFlaechen.showgroups (1)"):
                return
            daten = db_qkan.fetchall()

        self.lw_gruppen.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.lw_gruppen.addItem(QListWidgetItem(elem[0]))
