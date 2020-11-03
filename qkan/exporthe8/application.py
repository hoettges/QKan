import logging
import typing

from qgis.core import Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QListWidgetItem
from qkan import QKan, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
)
from qkan.plugin import QKanPlugin

from .application_dialog import ExportToHE8Dialog
from .export_to_he8 import exporthe8

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.exporthe8.application")


class ExportToHE8(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.db_qkan: typing.Optional[DBConnection] = None
        self.dlg = ExportToHE8Dialog(self)

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/exporthe8/icon_qk2he8.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Export to Hystem-Extran 8"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        self.dlg.close()

    def run(self):
        """Run method that performs all the real work"""

        self.dlg.tf_QKanDB.setText(QKan.config.database.qkan)
        self.dlg.tf_heDB_dest.setText(QKan.config.he.database)
        self.dlg.tf_heDB_template.setText(QKan.config.he.template)

        # Auswahl der zu exportierenden Tabellen ----------------------------------------------

        # Eigene Funktion für die zahlreichen Checkboxen

        def cb_set(name, cbox, default):
            if hasattr(QKan.config.check_export, name):
                checked = getattr(QKan.config.check_export, name)
            else:
                checked = default
            cbox.setChecked(checked)
            return checked

        def cb_setfalse(_name, cbox, _default):
            """Die selbe Funktion wie vor, deaktiviert jedoch die Optionen,
               weil die entsprechende Funktion noch nicht fertig ist"""
            checked = False
            cbox.setChecked(checked)
            return checked

        cb_set("export_schaechte", self.dlg.cb_export_schaechte, True)
        cb_setfalse("export_auslaesse", self.dlg.cb_export_auslaesse, True)
        cb_set("export_speicher", self.dlg.cb_export_speicher, True)
        cb_set("export_haltungen", self.dlg.cb_export_haltungen, True)
        cb_setfalse("export_pumpen", self.dlg.cb_export_pumpen, False)
        cb_setfalse("export_wehre", self.dlg.cb_export_wehre, False)
        cb_set("export_flaechenrw", self.dlg.cb_export_flaechenrw, True)
        cb_setfalse("export_einleitdirekt", self.dlg.cb_export_einleitdirekt, True)
        cb_setfalse("export_aussengebiete", self.dlg.cb_export_aussengebiete, True)
        cb_setfalse(
            "export_abflussparameter", self.dlg.cb_export_abflussparameter, True
        )
        cb_setfalse("export_regenschreiber", self.dlg.cb_export_regenschreiber, False)
        cb_setfalse("export_rohrprofile", self.dlg.cb_export_rohrprofile, False)
        cb_setfalse(
            "export_speicherkennlinien", self.dlg.cb_export_speicherkennlinien, False
        )
        cb_setfalse("export_bodenklassen", self.dlg.cb_export_bodenklassen, False)

        cb_set("modify_schaechte", self.dlg.cb_modify_schaechte, False)
        cb_setfalse("modify_auslaesse", self.dlg.cb_modify_auslaesse, False)
        cb_set("modify_speicher", self.dlg.cb_modify_speicher, False)
        cb_set("modify_haltungen", self.dlg.cb_modify_haltungen, False)
        cb_setfalse("modify_pumpen", self.dlg.cb_modify_pumpen, False)
        cb_setfalse("modify_wehre", self.dlg.cb_modify_wehre, False)
        cb_set("modify_flaechenrw", self.dlg.cb_modify_flaechenrw, False)
        cb_setfalse("modify_einleitdirekt", self.dlg.cb_modify_einleitdirekt, False)
        cb_setfalse("modify_aussengebiete", self.dlg.cb_modify_aussengebiete, False)
        cb_setfalse(
            "modify_abflussparameter", self.dlg.cb_modify_abflussparameter, False
        )
        cb_setfalse("modify_regenschreiber", self.dlg.cb_modify_regenschreiber, False)
        cb_setfalse("modify_rohrprofile", self.dlg.cb_modify_rohrprofile, False)
        cb_setfalse(
            "modify_speicherkennlinien", self.dlg.cb_modify_speicherkennlinien, False
        )
        cb_setfalse("modify_bodenklassen", self.dlg.cb_modify_bodenklassen, False)

        cb_setfalse("combine_einleitdirekt", self.dlg.cb_combine_einleitdirekt, True)

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {"flaechen", "haltungen", "linkfl", "tezg", "schaechte"}
                & get_editable_layers()
            )
            > 0
        ):
            self.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return False

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
            return False

        if database_qkan != "":
            self.dlg.tf_QKanDB.setText(database_qkan)

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
            return None

        # Check, ob alle Teilgebiete in Flächen, Schächten und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (1) "):
            del self.db_qkan
            return False

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (2) "):
            del self.db_qkan
            return False

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM schaechte 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (3) "):
            del self.db_qkan
            return False

        self.db_qkan.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        liste_teilgebiete = QKan.config.selections.teilgebiete

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.db_qkan.sql(sql, "QKan_ExportHE.application.run (4) "):
            del self.db_qkan
            return False
        daten = self.db_qkan.fetchall()
        self.dlg.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.dlg.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in liste_teilgebiete:
                    self.dlg.lw_teilgebiete.setCurrentRow(ielem)
            except BaseException as err:
                fehlermeldung(
                    "QKan_ExportHE (6), Fehler in elem = {}\n".format(elem), repr(err)
                )
                # if len(daten) == 1:
                # self.dlg.lw_teilgebiete.setCurrentRow(0)

        # Ereignis bei Auswahländerung in Liste Teilgebiete

        if not self.dlg.count_selection():
            del self.db_qkan
            return False

        # Autokorrektur
        self.dlg.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

        # Festlegung des Fangradius
        # Kann über Menü "Optionen" eingegeben werden
        fangradius = QKan.config.fangradius

        # Haltungsflächen (tezg) berücksichtigen
        self.dlg.cb_regardTezg.setChecked(QKan.config.mit_verschneidung)

        # Mindestflächengröße
        # Kann über Menü "Optionen" eingegeben werden
        mindestflaeche = QKan.config.mindestflaeche

        if not self.dlg.count_selection():
            del self.db_qkan
            return False

        # Formular anzeigen
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Abrufen der ausgewählten Elemente in beiden Listen
            liste_teilgebiete: typing.List[str] = list_selected_items(
                self.dlg.lw_teilgebiete
            )

            # Eingaben aus Formular übernehmen
            database_qkan: str = self.dlg.tf_QKanDB.text()
            database_he: str = self.dlg.tf_heDB_dest.text()
            dbtemplate_he: str = self.dlg.tf_heDB_template.text()
            autokorrektur: bool = self.dlg.cb_autokorrektur.isChecked()
            mit_verschneidung: bool = self.dlg.cb_regardTezg.isChecked()

            export_flaechen_he8: bool = self.dlg.cb_copyFlaechenHE8.isChecked()

            check_export = {
                "export_schaechte": self.dlg.cb_export_schaechte.isChecked(),
                "export_auslaesse": self.dlg.cb_export_auslaesse.isChecked(),
                "export_speicher": self.dlg.cb_export_speicher.isChecked(),
                "export_haltungen": self.dlg.cb_export_haltungen.isChecked(),
                "export_pumpen": self.dlg.cb_export_pumpen.isChecked(),
                "export_wehre": self.dlg.cb_export_wehre.isChecked(),
                "export_flaechenrw": self.dlg.cb_export_flaechenrw.isChecked(),
                "export_einleitdirekt": self.dlg.cb_export_einleitdirekt.isChecked(),
                "export_aussengebiete": self.dlg.cb_export_aussengebiete.isChecked(),
                "export_abflussparameter": self.dlg.cb_export_abflussparameter.isChecked(),
                "export_regenschreiber": self.dlg.cb_export_regenschreiber.isChecked(),
                "export_rohrprofile": self.dlg.cb_export_rohrprofile.isChecked(),
                "export_speicherkennlinien": self.dlg.cb_export_speicherkennlinien.isChecked(),
                "export_bodenklassen": self.dlg.cb_export_bodenklassen.isChecked(),
                "modify_schaechte": self.dlg.cb_modify_schaechte.isChecked(),
                "modify_auslaesse": self.dlg.cb_modify_auslaesse.isChecked(),
                "modify_speicher": self.dlg.cb_modify_speicher.isChecked(),
                "modify_haltungen": self.dlg.cb_modify_haltungen.isChecked(),
                "modify_pumpen": self.dlg.cb_modify_pumpen.isChecked(),
                "modify_wehre": self.dlg.cb_modify_wehre.isChecked(),
                "modify_flaechenrw": self.dlg.cb_modify_flaechenrw.isChecked(),
                "modify_einleitdirekt": self.dlg.cb_modify_einleitdirekt.isChecked(),
                "modify_aussengebiete": self.dlg.cb_modify_aussengebiete.isChecked(),
                "modify_abflussparameter": self.dlg.cb_modify_abflussparameter.isChecked(),
                "modify_regenschreiber": self.dlg.cb_modify_regenschreiber.isChecked(),
                "modify_rohrprofile": self.dlg.cb_modify_rohrprofile.isChecked(),
                "modify_speicherkennlinien": self.dlg.cb_modify_speicherkennlinien.isChecked(),
                "modify_bodenklassen": self.dlg.cb_modify_bodenklassen.isChecked(),
                "combine_einleitdirekt": self.dlg.cb_combine_einleitdirekt.isChecked(),
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
                self.iface,
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
                self.iface,
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
