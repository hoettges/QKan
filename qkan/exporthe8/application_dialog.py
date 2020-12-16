import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, cast

from qgis.core import Qgis
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QWidget,
)
from qkan import QKan, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
)
from qkan.tools.dialogs import QKanDBDialog

from .export_to_he8 import exporthe8

if TYPE_CHECKING:
    from .application import ExportToHE8

logger = logging.getLogger("QKan.exporthe8.application_dialog")
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "application_dialog_base.ui")
)


def click_help() -> None:
    """Reaktion auf Klick auf Help-Schaltfläche"""
    helpfile = Path(__file__).parent / ".." / "doc" / "exporthe8.html"
    os.startfile(str(helpfile))


class ExportToHE8Dialog(QKanDBDialog, FORM_CLASS):  # type: ignore
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

    tf_heDB_dest: QLineEdit
    tf_heDB_template: QLineEdit

    def __init__(self, plugin: "ExportToHE8", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.button_box.helpRequested.connect(click_help)
        self.cb_selActive.stateChanged.connect(self.click_selection)
        self.lw_teilgebiete.itemClicked.connect(self.count_selection)
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)
        self.pb_exportall.clicked.connect(lambda _: self.set_export(True))
        self.pb_exportnone.clicked.connect(lambda _: self.set_export(False))
        self.pb_modifyall.clicked.connect(lambda _: self.set_export(True))
        self.pb_modifynone.clicked.connect(lambda _: self.set_export(False))

        self.bind_select_path(
            title="Dateinamen der Ziel-HE-Datenbank eingeben",
            file_filter="*.idbm",
            line_edit=self.tf_heDB_dest,
            push_button=self.pb_selectHeDB_dest,
            is_open=False,
        )
        self.bind_select_path(
            title="Vorlage-HE-Datenbank auswählen",
            file_filter="*.idbm",
            line_edit=self.tf_heDB_template,
            push_button=self.pb_selectHeDB_template,
            is_open=True,
        )
        self.bind_select_path(
            title="Leere Vorlage-HE-Datenbank auswählen",
            file_filter="*.idbm",
            line_edit=self.tf_heDB_template,
            push_button=self.pb_selectHeDB_emptytemplate,
            is_open=True,
        )

    # noinspection DuplicatedCode
    def set_export(self, status: bool = True) -> None:
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
    def set_modify(self, status: bool = True) -> None:
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

        liste_teilgebiete: List[str] = list_selected_items(self.lw_teilgebiete)

        # Zu berücksichtigende Flächen zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE flaechen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
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
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE schaechte.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
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
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE haltungen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
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

    def run(self) -> None:
        """Run method that performs all the real work"""

        self.tf_qkanDB.setText(QKan.config.database.qkan)
        self.tf_heDB_dest.setText(QKan.config.he.database)
        self.tf_heDB_template.setText(QKan.config.he.template)

        # Auswahl der zu exportierenden Tabellen ----------------------------------------------

        # Eigene Funktion für die zahlreichen Checkboxen

        def cb_set(name: str, cbox: QCheckBox, default: bool) -> bool:
            if hasattr(QKan.config.check_export, name):
                checked = cast(bool, getattr(QKan.config.check_export, name))
            else:
                checked = default
            cbox.setChecked(checked)
            return checked

        def cb_setfalse(_name: str, cbox: QCheckBox, _default: bool) -> bool:
            """Die selbe Funktion wie vor, deaktiviert jedoch die Optionen,
               weil die entsprechende Funktion noch nicht fertig ist"""
            checked = False
            cbox.setChecked(checked)
            return checked

        cb_set("export_schaechte", self.cb_export_schaechte, True)
        cb_setfalse("export_auslaesse", self.cb_export_auslaesse, True)
        cb_set("export_speicher", self.cb_export_speicher, True)
        cb_set("export_haltungen", self.cb_export_haltungen, True)
        cb_setfalse("export_pumpen", self.cb_export_pumpen, False)
        cb_setfalse("export_wehre", self.cb_export_wehre, False)
        cb_set("export_flaechenrw", self.cb_export_flaechenrw, True)
        cb_setfalse("export_einleitdirekt", self.cb_export_einleitdirekt, True)
        cb_setfalse("export_aussengebiete", self.cb_export_aussengebiete, True)
        cb_setfalse("export_abflussparameter", self.cb_export_abflussparameter, True)
        cb_setfalse("export_regenschreiber", self.cb_export_regenschreiber, False)
        cb_setfalse("export_rohrprofile", self.cb_export_rohrprofile, False)
        cb_setfalse(
            "export_speicherkennlinien", self.cb_export_speicherkennlinien, False
        )
        cb_setfalse("export_bodenklassen", self.cb_export_bodenklassen, False)

        cb_set("modify_schaechte", self.cb_modify_schaechte, False)
        cb_setfalse("modify_auslaesse", self.cb_modify_auslaesse, False)
        cb_set("modify_speicher", self.cb_modify_speicher, False)
        cb_set("modify_haltungen", self.cb_modify_haltungen, False)
        cb_setfalse("modify_pumpen", self.cb_modify_pumpen, False)
        cb_setfalse("modify_wehre", self.cb_modify_wehre, False)
        cb_set("modify_flaechenrw", self.cb_modify_flaechenrw, False)
        cb_setfalse("modify_einleitdirekt", self.cb_modify_einleitdirekt, False)
        cb_setfalse("modify_aussengebiete", self.cb_modify_aussengebiete, False)
        cb_setfalse("modify_abflussparameter", self.cb_modify_abflussparameter, False)
        cb_setfalse("modify_regenschreiber", self.cb_modify_regenschreiber, False)
        cb_setfalse("modify_rohrprofile", self.cb_modify_rohrprofile, False)
        cb_setfalse(
            "modify_speicherkennlinien", self.cb_modify_speicherkennlinien, False
        )
        cb_setfalse("modify_bodenklassen", self.cb_modify_bodenklassen, False)

        cb_setfalse("combine_einleitdirekt", self.cb_combine_einleitdirekt, True)

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {"flaechen", "haltungen", "linkfl", "tezg", "schaechte"}
                & get_editable_layers()
            )
            > 0
        ):
            self.plugin.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            fehlermeldung(
                "Fehler in exporthe8",
                "database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!",
            )
            logger.error(
                "exporthe8: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return

        if database_qkan != "":
            self.tf_qkanDB.setText(database_qkan)

        # Datenbankverbindung für Abfragen
        self.db_qkan = DBConnection(
            dbname=database_qkan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen
        if not self.db_qkan.connected:
            logger.error(
                "Fehler in exportdyna.application:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )
            return

        # Check, ob alle Teilgebiete in Flächen, Schächten und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (1) "):
            del self.db_qkan
            return

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (2) "):
            del self.db_qkan
            return

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM schaechte 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (3) "):
            del self.db_qkan
            return

        self.db_qkan.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        liste_teilgebiete = QKan.config.selections.teilgebiete

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (4) "):
            del self.db_qkan
            return
        daten = self.db_qkan.fetchall()
        self.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in liste_teilgebiete:
                    self.lw_teilgebiete.setCurrentRow(ielem)
            except BaseException as err:
                fehlermeldung(
                    "QKan_ExportHE (6), Fehler in elem = {}\n".format(elem), repr(err)
                )
                # if len(daten) == 1:
                # self.lw_teilgebiete.setCurrentRow(0)

        # Ereignis bei Auswahländerung in Liste Teilgebiete

        if not self.count_selection():
            del self.db_qkan
            return

        # Autokorrektur
        self.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

        # Festlegung des Fangradius
        # Kann über Menü "Optionen" eingegeben werden
        fangradius = QKan.config.fangradius

        # Haltungsflächen (tezg) berücksichtigen
        self.cb_regardTezg.setChecked(QKan.config.mit_verschneidung)

        # Mindestflächengröße
        # Kann über Menü "Optionen" eingegeben werden
        mindestflaeche = QKan.config.mindestflaeche

        if not self.count_selection():
            del self.db_qkan
            return

        # Formular anzeigen
        self.show()
        # Run the dialog event loop
        result = self.exec_()
        # See if OK was pressed
        if result:
            # Abrufen der ausgewählten Elemente in beiden Listen
            liste_teilgebiete = list_selected_items(self.lw_teilgebiete)

            # Eingaben aus Formular übernehmen
            database_qkan = cast(str, self.tf_qkanDB.text())
            database_he: str = self.tf_heDB_dest.text()
            dbtemplate_he: str = self.tf_heDB_template.text()
            autokorrektur: bool = self.cb_autokorrektur.isChecked()
            mit_verschneidung: bool = self.cb_regardTezg.isChecked()

            export_flaechen_he8: bool = self.cb_copyFlaechenHE8.isChecked()

            check_export = {
                "export_schaechte": self.cb_export_schaechte.isChecked(),
                "export_auslaesse": self.cb_export_auslaesse.isChecked(),
                "export_speicher": self.cb_export_speicher.isChecked(),
                "export_haltungen": self.cb_export_haltungen.isChecked(),
                "export_pumpen": self.cb_export_pumpen.isChecked(),
                "export_wehre": self.cb_export_wehre.isChecked(),
                "export_flaechenrw": self.cb_export_flaechenrw.isChecked(),
                "export_einleitdirekt": self.cb_export_einleitdirekt.isChecked(),
                "export_aussengebiete": self.cb_export_aussengebiete.isChecked(),
                "export_abflussparameter": self.cb_export_abflussparameter.isChecked(),
                "export_regenschreiber": self.cb_export_regenschreiber.isChecked(),
                "export_rohrprofile": self.cb_export_rohrprofile.isChecked(),
                "export_speicherkennlinien": self.cb_export_speicherkennlinien.isChecked(),
                "export_bodenklassen": self.cb_export_bodenklassen.isChecked(),
                "modify_schaechte": self.cb_modify_schaechte.isChecked(),
                "modify_auslaesse": self.cb_modify_auslaesse.isChecked(),
                "modify_speicher": self.cb_modify_speicher.isChecked(),
                "modify_haltungen": self.cb_modify_haltungen.isChecked(),
                "modify_pumpen": self.cb_modify_pumpen.isChecked(),
                "modify_wehre": self.cb_modify_wehre.isChecked(),
                "modify_flaechenrw": self.cb_modify_flaechenrw.isChecked(),
                "modify_einleitdirekt": self.cb_modify_einleitdirekt.isChecked(),
                "modify_aussengebiete": self.cb_modify_aussengebiete.isChecked(),
                "modify_abflussparameter": self.cb_modify_abflussparameter.isChecked(),
                "modify_regenschreiber": self.cb_modify_regenschreiber.isChecked(),
                "modify_rohrprofile": self.cb_modify_rohrprofile.isChecked(),
                "modify_speicherkennlinien": self.cb_modify_speicherkennlinien.isChecked(),
                "modify_bodenklassen": self.cb_modify_bodenklassen.isChecked(),
                "combine_einleitdirekt": self.cb_combine_einleitdirekt.isChecked(),
            }

            # Konfigurationsdaten schreiben
            QKan.config.autokorrektur = autokorrektur
            QKan.config.selections.teilgebiete = liste_teilgebiete
            QKan.config.database.qkan = database_qkan
            QKan.config.fangradius = fangradius
            QKan.config.he.database = database_he
            QKan.config.he.template = dbtemplate_he
            QKan.config.mindestflaeche = mindestflaeche
            QKan.config.mit_verschneidung = mit_verschneidung

            for el in check_export:
                setattr(QKan.config.check_export, el, check_export[el])

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            logger.debug(
                f"""QKan-Modul Aufruf
                exporthe8(
                "{database_he}",
                "{dbtemplate_he}",
                self.db_qkan,
                {liste_teilgebiete},
                {autokorrektur},
                {fangradius},
                {mindestflaeche},
                {mit_verschneidung},
                {export_flaechen_he8},
                {check_export},
            )"""
            )

            if not exporthe8(
                database_he,
                dbtemplate_he,
                self.db_qkan,
                liste_teilgebiete,
                autokorrektur,
                fangradius,
                mindestflaeche,
                mit_verschneidung,
                export_flaechen_he8,
                check_export,
            ):
                del self.db_qkan
