import logging
import os
import typing
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
)
from qkan import QKan, get_default_dir, list_selected_items

if typing.TYPE_CHECKING:
    from .application import ExportToHE8

logger = logging.getLogger("QKan.exporthe8.application_dialog")
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "application_dialog_base.ui")
)


def click_help():
    """Reaktion auf Klick auf Help-Schaltfläche"""
    helpfile = Path(__file__).parent / ".." / "doc" / "exporthe8.html"
    os.startfile(str(helpfile))


class ExportToHE8Dialog(QDialog, FORM_CLASS):
    button_box: QDialogButtonBox
    cb_autokorrektur: QCheckBox
    cb_combine_einleitdirekt: QCheckBox
    cb_copyFlaechenHE8: QCheckBox
    cb_export_abflussparameter: QCheckBox
    cb_export_auslaesse: QCheckBox
    cb_export_aussengebiete: QCheckBox
    cb_export_bodenklassen: QCheckBox
    cb_export_einleitdirekt: QCheckBox
    cb_export_flaechenrw: QCheckBox
    cb_export_haltungen: QCheckBox
    cb_export_pumpen: QCheckBox
    cb_export_regenschreiber: QCheckBox
    cb_export_rohrprofile: QCheckBox
    cb_export_schaechte: QCheckBox
    cb_export_speicher: QCheckBox
    cb_export_speicherkennlinien: QCheckBox
    cb_export_wehre: QCheckBox
    cb_modify_abflussparameter: QCheckBox
    cb_modify_auslaesse: QCheckBox
    cb_modify_aussengebiete: QCheckBox
    cb_modify_bodenklassen: QCheckBox
    cb_modify_einleitdirekt: QCheckBox
    cb_modify_flaechenrw: QCheckBox
    cb_modify_haltungen: QCheckBox
    cb_modify_pumpen: QCheckBox
    cb_modify_regenschreiber: QCheckBox
    cb_modify_rohrprofile: QCheckBox
    cb_modify_schaechte: QCheckBox
    cb_modify_speicher: QCheckBox
    cb_modify_speicherkennlinien: QCheckBox
    cb_modify_wehre: QCheckBox
    cb_regardTezg: QCheckBox
    cb_selActive: QCheckBox

    lf_anzahl_flaechen: QLabel
    lf_anzahl_haltungen: QLabel
    lf_anzahl_schaechte: QLabel

    lw_teilgebiete: QListWidget

    pb_exportall: QPushButton
    pb_exportnone: QPushButton
    pb_modifyall: QPushButton
    pb_modifynone: QPushButton
    pb_selectHeDB_dest: QPushButton
    pb_selectHeDB_emptytemplate: QPushButton
    pb_selectHeDB_template: QPushButton
    pb_selectQKanDB: QPushButton

    tf_QKanDB: QLineEdit
    tf_heDB_dest: QLineEdit
    tf_heDB_template: QLineEdit

    def __init__(self, plugin: "ExportToHE8", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin
        self.default_dir = get_default_dir()

        self.button_box.helpRequested.connect(click_help)
        self.cb_selActive.stateChanged.connect(self.click_selection)
        self.lw_teilgebiete.itemClicked.connect(self.count_selection)
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)
        self.pb_exportall.clicked.connect(lambda _: self.set_export(True))
        self.pb_exportnone.clicked.connect(lambda _: self.set_export(False))
        self.pb_modifyall.clicked.connect(lambda _: self.set_export(True))
        self.pb_modifynone.clicked.connect(lambda _: self.set_export(False))
        self.pb_selectHeDB_dest.clicked.connect(self.select_he_db_dest)
        self.pb_selectHeDB_emptytemplate.clicked.connect(
            self.select_he_db_empty_template
        )
        self.pb_selectHeDB_template.clicked.connect(self.select_he_db_template)
        self.pb_selectQKanDB.clicked.connect(self.select_qkan_db)

    def select_he_db_dest(self):
        """
        Datenbankverbindung zur HE-Datenbank (Firebird) auswaehlen und
        gegebenenfalls die Zieldatenbank erstellen, aber noch nicht verbinden.
        """

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getSaveFileName(
            self,
            "Dateinamen der Ziel-HE-Datenbank eingeben",
            self.default_dir,
            "*.idbm",
        )
        self.tf_heDB_dest.setText(filename)

    def select_he_db_template(self):
        """Vorlage-HE-Datenbank (Firebird) auswaehlen."""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "Vorlage-HE-Datenbank auswählen", self.default_dir, "*.idbm"
        )
        self.tf_heDB_template.setText(filename)

    def select_he_db_empty_template(self):
        """Vorlage-HE-Datenbank (Firebird) auswaehlen."""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "Leere Vorlage-HE-Datenbank auswählen", QKan.template_dir, "*.idbm",
        )
        self.tf_heDB_template.setText(filename)

    def select_qkan_db(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "QKan-Datenbank auswählen", self.default_dir, "*.sqlite"
        )
        self.tf_QKanDB.setText(filename)

    # noinspection DuplicatedCode
    def set_export(self, status: bool = True):
        self.cb_export_schaechte.setChecked(status)
        self.cb_export_auslaesse.setChecked(status)
        self.cb_export_speicher.setChecked(status)
        self.cb_export_haltungen.setChecked(status)
        self.cb_export_pumpen.setChecked(status)
        self.cb_export_wehre.setChecked(status)
        self.cb_export_flaechenrw.setChecked(status)
        self.cb_export_einleitdirekt.setChecked(status)
        self.cb_export_aussengebiete.setChecked(status)
        self.cb_export_abflussparameter.setChecked(status)
        self.cb_export_regenschreiber.setChecked(status)
        self.cb_export_rohrprofile.setChecked(status)
        self.cb_export_speicherkennlinien.setChecked(status)
        self.cb_export_bodenklassen.setChecked(status)

    # noinspection DuplicatedCode
    def set_modify(self, status: bool = True):
        self.cb_modify_schaechte.setChecked(status)
        self.cb_modify_auslaesse.setChecked(status)
        self.cb_modify_speicher.setChecked(status)
        self.cb_modify_haltungen.setChecked(status)
        self.cb_modify_pumpen.setChecked(status)
        self.cb_modify_wehre.setChecked(status)
        self.cb_modify_flaechenrw.setChecked(status)
        self.cb_modify_einleitdirekt.setChecked(status)
        self.cb_modify_aussengebiete.setChecked(status)
        self.cb_modify_abflussparameter.setChecked(status)
        self.cb_modify_regenschreiber.setChecked(status)
        self.cb_modify_rohrprofile.setChecked(status)
        self.cb_modify_speicherkennlinien.setChecked(status)
        self.cb_modify_bodenklassen.setChecked(status)

    def click_selection(self):
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

    def click_lw_teilgebiete(self):
        """Reaktion auf Klick in Tabelle"""

        self.cb_selActive.setChecked(True)
        self.count_selection()

    def count_selection(self):
        """
        Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen
        """

        liste_teilgebiete: typing.List[str] = list_selected_items(self.lw_teilgebiete)

        # Zu berücksichtigende Flächen zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE flaechen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM flaechen {auswahl}"

        if not self.plugin.db_qkan.sql(
            sql, "QKan_ExportHE.application.countselection (1)"
        ):
            return False
        daten = self.plugin.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.lf_anzahl_flaechen.setText("0")

        # Zu berücksichtigende Schächte zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE schaechte.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM schaechte {auswahl}"
        if not self.plugin.db_qkan.sql(
            sql, "QKan_ExportHE.application.countselection (2) "
        ):
            return False
        daten = self.plugin.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_schaechte.setText(str(daten[0]))
        else:
            self.lf_anzahl_schaechte.setText("0")

        # Zu berücksichtigende Haltungen zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE haltungen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM haltungen {auswahl}"
        if not self.plugin.db_qkan.sql(
            sql, "QKan_ExportHE.application.countselection (3) "
        ):
            return False
        daten = self.plugin.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.lf_anzahl_haltungen.setText("0")
        return True
