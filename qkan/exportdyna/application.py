import typing

from qgis.core import Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QListWidgetItem
from qkan import QKan, enums, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
)
from qkan.plugin import QKanPlugin

from .application_dialog import ExportToKPDialog
from .export_to_dyna import export_kanaldaten

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class ExportToKP(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        # Save reference to the QGIS interface
        super().__init__(iface)
        self.db_qkan: typing.Optional[DBConnection] = None
        self.dlg = ExportToKPDialog(self)

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/exportdyna/res/icon_qk2kp.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Export in DYNA-Datei..."),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        self.dlg.close()

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog

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

        self.dlg.tf_KP_dest.setText(QKan.config.dyna.file)
        self.dlg.tf_KP_template.setText(QKan.config.dyna.template)

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            self.log.error(
                "exportdyna.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False
        self.dlg.tf_QKanDB.setText(database_qkan)

        # Datenbankverbindung für Abfragen
        if database_qkan != "":
            # Nur wenn schon eine Projekt geladen oder eine QKan-Datenbank ausgewählt
            self.db_qkan = DBConnection(
                dbname=database_qkan
            )  # Datenbankobjekt der QKan-Datenbank zum Lesen
            if not self.db_qkan.connected:
                fehlermeldung(
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
            if not self.db_qkan.sql(sql, "QKan_ExportDYNA.application.run (1) "):
                return False

            sql = """INSERT INTO teilgebiete (tgnam)
                    SELECT teilgebiet FROM haltungen 
                    WHERE teilgebiet IS NOT NULL AND
                    teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                    GROUP BY teilgebiet"""
            if not self.db_qkan.sql(sql, "QKan_ExportDYNA.application.run (2) "):
                return False

            sql = """INSERT INTO teilgebiete (tgnam)
                    SELECT teilgebiet FROM schaechte 
                    WHERE teilgebiet IS NOT NULL AND
                    teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                    GROUP BY teilgebiet"""
            if not self.db_qkan.sql(sql, "QKan_ExportDYNA.application.run (3) "):
                return False

            self.db_qkan.commit()

            # Anlegen der Tabelle zur Auswahl der Teilgebiete

            # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
            liste_teilgebiete = QKan.config.selections.teilgebiete

            # Abfragen der Tabelle teilgebiete nach Teilgebieten
            sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
            if not self.db_qkan.sql(sql, "QKan_ExportDYNA.application.run (4) "):
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
                        "QKan_ExportDYNA (6), Fehler in elem = {}\n".format(elem),
                        repr(err),
                    )
                    # if len(daten) == 1:
                    # self.dlg.lw_teilgebiete.setCurrentRow(0)

            # Ereignis bei Auswahländerung in Liste Teilgebiete

        if not self.dlg.count_selection():
            del self.db_qkan
            return False

        # Autokorrektur
        self.dlg.cb_profile_ergaenzen.setChecked(QKan.config.dyna.profile_ergaenzen)
        self.dlg.cb_autonummerierung_dyna.setChecked(QKan.config.dyna.autonummerierung)

        # Festlegung des Fangradius
        # Kann über Menü "Optionen" eingegeben werden
        fangradius = QKan.config.fangradius

        # Haltungsflächen (tezg) berücksichtigen
        self.dlg.cb_regardTezg.setChecked(QKan.config.mit_verschneidung)

        # Mindestflächengröße
        # Kann über Menü "Optionen" eingegeben werden
        mindestflaeche = QKan.config.mindestflaeche

        # Maximalzahl Schleifendurchläufe
        max_loops = QKan.config.max_loops

        # Optionen zur Berechnung der befestigten Flächen
        dynabef_choice = QKan.config.dyna.bef_choice
        if dynabef_choice == enums.BefChoice.FLAECHEN:
            self.dlg.rb_flaechen.setChecked(True)
        elif dynabef_choice == enums.BefChoice.TEZG:
            self.dlg.rb_tezg.setChecked(True)

        # Optionen zur Zuordnung des Profilschlüssels
        dynaprof_choice = QKan.config.dyna.prof_choice

        if dynaprof_choice == enums.ProfChoice.PROFILNAME:
            self.dlg.rb_profnam.setChecked(True)
        elif dynaprof_choice == enums.ProfChoice.PROFILKEY:
            self.dlg.rb_profkey.setChecked(True)

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
            dynafile: str = self.dlg.tf_KP_dest.text()
            template_dyna: str = self.dlg.tf_KP_template.text()
            profile_ergaenzen: bool = self.dlg.cb_profile_ergaenzen.isChecked()
            autonummerierung_dyna: bool = self.dlg.cb_autonummerierung_dyna.isChecked()
            mit_verschneidung: bool = self.dlg.cb_regardTezg.isChecked()
            if self.dlg.rb_flaechen.isChecked():
                dynabef_choice = enums.BefChoice.FLAECHEN
            elif self.dlg.rb_tezg.isChecked():
                dynabef_choice = enums.BefChoice.TEZG
            else:
                fehlermeldung(
                    "exportdyna.application.run",
                    "Fehlerhafte Option: \ndynabef_choice = {}".format(
                        repr(dynabef_choice)
                    ),
                )
            if self.dlg.rb_profnam.isChecked():
                dynaprof_choice = enums.ProfChoice.PROFILNAME
            elif self.dlg.rb_profkey.isChecked():
                dynaprof_choice = enums.ProfChoice.PROFILKEY
            else:
                fehlermeldung(
                    "exportdyna.application.run",
                    "Fehlerhafte Option: \ndynaprof_choice = {}".format(
                        repr(dynaprof_choice)
                    ),
                )

            # Konfigurationsdaten schreiben
            QKan.config.selections.teilgebiete = liste_teilgebiete
            QKan.config.database.qkan = database_qkan
            QKan.config.dyna.autonummerierung = autonummerierung_dyna
            QKan.config.dyna.bef_choice = dynabef_choice
            QKan.config.dyna.file = dynafile
            QKan.config.dyna.prof_choice = dynaprof_choice
            QKan.config.dyna.profile_ergaenzen = profile_ergaenzen
            QKan.config.dyna.template = template_dyna
            QKan.config.fangradius = fangradius
            QKan.config.max_loops = max_loops
            QKan.config.mindestflaeche = mindestflaeche
            QKan.config.mit_verschneidung = mit_verschneidung

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                exportKanaldaten(
                    iface,
                    "{dynafile}",
                    "{template_dyna}",
                    {self.db_qkan},
                    {dynabef_choice},
                    {dynaprof_choice},
                    {liste_teilgebiete},
                    {profile_ergaenzen},
                    {autonummerierung_dyna},
                    {mit_verschneidung},
                    {fangradius},
                    {mindestflaeche},
                    {max_loops},
            )"""
            )

            export_kanaldaten(
                self.iface,
                dynafile,
                template_dyna,
                self.db_qkan,
                dynabef_choice,
                dynaprof_choice,
                liste_teilgebiete,
                profile_ergaenzen,
                autonummerierung_dyna,
                mit_verschneidung,
                fangradius,
                mindestflaeche,
                max_loops,
            )

            del self.db_qkan
