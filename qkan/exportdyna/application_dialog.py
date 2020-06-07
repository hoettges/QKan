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
    QRadioButton,
)

from qkan import get_default_dir, list_selected_items

if typing.TYPE_CHECKING:
    from .application import ExportToKP

logger = logging.getLogger("QKan.exportdyna.application_dialog")
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_exportDYNA.ui")
)


def click_help():
    """Reaktion auf Klick auf Help-Schaltfläche"""

    help_file = Path(__file__).parent / ".." / "doc" / "exportdyna.html"
    os.startfile(str(help_file))


class ExportToKPDialog(QDialog, FORM_CLASS):
    button_box: QDialogButtonBox

    cb_autonummerierung_dyna: QCheckBox
    cb_profile_ergaenzen: QCheckBox
    cb_regardTezg: QCheckBox
    cb_selActive: QCheckBox

    lf_anzahl_flaechen: QLabel
    lf_anzahl_haltungen: QLabel
    lf_anzahl_schaechte: QLabel

    lw_teilgebiete: QListWidget

    pb_selectQKanDB: QPushButton
    pb_select_KP_dest: QPushButton
    pb_select_KP_template: QPushButton

    rb_flaechen: QRadioButton
    rb_profkey: QRadioButton
    rb_profnam: QRadioButton
    rb_tezg: QRadioButton

    tf_KP_dest: QLineEdit
    tf_KP_template: QLineEdit
    tf_QKanDB: QLineEdit

    def __init__(self, plugin: "ExportToKP", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.default_dir = get_default_dir()

        self.plugin = plugin

        self.button_box.helpRequested.connect(click_help)
        self.cb_selActive.stateChanged.connect(self.click_selection)
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)
        self.pb_selectQKanDB.clicked.connect(self.select_qkan_db)
        self.pb_select_KP_dest.clicked.connect(self.select_kp_db_dest)
        self.pb_select_KP_template.clicked.connect(self.select_kp_db_template)

    def select_kp_db_dest(self):
        """Zu erstellende DYNA-Datei eingeben"""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getSaveFileName(
            self,
            "Dateinamen der zu schreibenden DYNA-Datei eingeben",
            self.default_dir,
            "*.ein",
        )
        self.tf_KP_dest.setText(filename)

    def select_kp_db_template(self):
        """Vorlage-DYNA-Datei auswaehlen."""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "Vorlage-DYNA-Datei auswählen", self.default_dir, "*.ein"
        )
        self.tf_KP_template.setText(filename)

    def select_qkan_db(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "QKan-Datenbank auswählen", self.default_dir, "*.sqlite"
        )
        self.tf_QKanDB.setText(filename)

    def click_lw_teilgebiete(self):
        """Reaktion auf Klick in Tabelle"""

        self.cb_selActive.setChecked(True)
        self.count_selection()

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

    def count_selection(self):
        """
        Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen
        """

        logger.debug("arg: {}".format(self.lw_teilgebiete))
        liste_teilgebiete: typing.List[str] = list_selected_items(self.lw_teilgebiete)

        # Zu berücksichtigende Flächen zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = "WHERE flaechen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM flaechen {auswahl}"

        if not self.plugin.db_qkan.sql(
            sql, "QKan_ExportDYNA.application.countselection (1)"
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
            auswahl = "WHERE schaechte.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM schaechte {auswahl}"
        if not self.plugin.db_qkan.sql(
            sql, "QKan_ExportDYNA.application.countselection (2) "
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
            auswahl = "WHERE haltungen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = f"SELECT count(*) AS anzahl FROM haltungen {auswahl}"
        if not self.plugin.db_qkan.sql(
            sql, "QKan_ExportDYNA.application.countselection (3) "
        ):
            return False
        daten = self.plugin.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.lf_anzahl_haltungen.setText("0")

        return True