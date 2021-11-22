import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, cast

from qgis.core import Qgis, QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QWidget,
)

from qkan import QKan, enums, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
)
from qkan.tools.dialogs import QKanDBDialog

from .export_to_dyna import export_kanaldaten
from .import_from_dyna import import_kanaldaten

if TYPE_CHECKING:
    from qkan.dynaporter import DynaPorter

logger = logging.getLogger("QKan.dynaporter.dialogs")
EXPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "export.ui")
)
IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "import.ui")
)


def click_help() -> None:
    """Reaktion auf Klick auf Help-Schaltfläche"""

    help_file = Path(__file__).parent / ".." / "doc" / "exportdyna.html"
    os.startfile(str(help_file))


class ExportDialog(QKanDBDialog, EXPORT_CLASS):  # type: ignore
    button_box: QDialogButtonBox

    cb_autonummerierung_dyna: QCheckBox
    cb_profile_ergaenzen: QCheckBox
    cb_regardTezg: QCheckBox
    cb_selActive: QCheckBox

    lf_anzahl_flaechen: QLabel
    lf_anzahl_haltungen: QLabel
    lf_anzahl_schaechte: QLabel

    lw_teilgebiete: QListWidget

    pb_select_KP_dest: QPushButton
    pb_select_KP_template: QPushButton
    pb_selectQKanDB: QPushButton            # disabled in Form "export.ui"

    rb_flaechen: QRadioButton
    rb_profkey: QRadioButton
    rb_profnam: QRadioButton
    rb_tezg: QRadioButton

    tf_KP_dest: QLineEdit
    tf_KP_template: QLineEdit

    def __init__(self, plugin: "DynaPorter", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.iface = QKan.instance.iface

        self.db_qkan: Optional[DBConnection] = None

        self.button_box.helpRequested.connect(click_help)
        self.cb_selActive.stateChanged.connect(self.click_selection)
        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)

        self.bind_select_path(
            title="Dateinamen der zu schreibenden DYNA-Datei eingeben",
            file_filter="*.ein",
            line_edit=self.tf_KP_dest,
            push_button=self.pb_select_KP_dest,
            is_open=False,
        )
        self.bind_select_path(
            title="Vorlage-DYNA-Datei auswählen",
            file_filter="*.ein",
            line_edit=self.tf_KP_template,
            push_button=self.pb_select_KP_template,
            is_open=True,
        )

    def click_lw_teilgebiete(self) -> None:
        """Reaktion auf Klick in Tabelle"""

        self.cb_selActive.setChecked(True)
        self.count_selection()

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

    def count_selection(self) -> bool:
        """
        Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen
        """

        if self.db_qkan is None:
            logger.error("qkan_db is not initialized.")
            return False

        logger.debug("arg: {}".format(self.lw_teilgebiete))
        liste_teilgebiete: List[str] = list_selected_items(self.lw_teilgebiete)

        # Zu berücksichtigende Flächen zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = "WHERE flaechen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        if not self.db_qkan.sql(
            f"SELECT count(*) AS anzahl FROM flaechen {auswahl}",
            "QKan_ExportDYNA.application.countselection (1)",
        ):
            return False
        daten = self.db_qkan.fetchone()
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

        if not self.db_qkan.sql(
            f"SELECT count(*) AS anzahl FROM schaechte {auswahl}",
            "QKan_ExportDYNA.application.countselection (2) ",
        ):
            return False
        daten = self.db_qkan.fetchone()
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

        if not self.db_qkan.sql(
            f"SELECT count(*) AS anzahl FROM haltungen {auswahl}",
            "QKan_ExportDYNA.application.countselection (3) ",
        ):
            return False
        daten = self.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.lf_anzahl_haltungen.setText("0")

        return True

    def run(self) -> None:
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
            return

        self.tf_KP_dest.setText(QKan.config.dyna.file)
        self.tf_KP_template.setText(QKan.config.dyna.template)

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            logger.error(
                "exportdyna.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return
        self.tf_qkanDB.setText(database_qkan)

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
                return

            # Check, ob alle Teilgebiete in Flächen, Schächten und Haltungen auch in Tabelle "teilgebiete" enthalten

            sql = """INSERT INTO teilgebiete (tgnam)
                    SELECT teilgebiet FROM flaechen 
                    WHERE teilgebiet IS NOT NULL AND
                    teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                    GROUP BY teilgebiet"""
            if not self.db_qkan.sql(sql, "QKan_ExportDYNA.application.run (1) "):
                return

            sql = """INSERT INTO teilgebiete (tgnam)
                    SELECT teilgebiet FROM haltungen 
                    WHERE teilgebiet IS NOT NULL AND
                    teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                    GROUP BY teilgebiet"""
            if not self.db_qkan.sql(sql, "QKan_ExportDYNA.application.run (2) "):
                return

            sql = """INSERT INTO teilgebiete (tgnam)
                    SELECT teilgebiet FROM schaechte 
                    WHERE teilgebiet IS NOT NULL AND
                    teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                    GROUP BY teilgebiet"""
            if not self.db_qkan.sql(sql, "QKan_ExportDYNA.application.run (3) "):
                return

            self.db_qkan.commit()

            # Anlegen der Tabelle zur Auswahl der Teilgebiete

            # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
            liste_teilgebiete = QKan.config.selections.teilgebiete

            # Abfragen der Tabelle teilgebiete nach Teilgebieten
            if not self.db_qkan.sql(
                'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"',
                "QKan_ExportDYNA.application.run (4) ",
            ):
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
                        "QKan_ExportDYNA (6), Fehler in elem = {}\n".format(elem),
                        repr(err),
                    )
                    # if len(daten) == 1:
                    # self.dlg.lw_teilgebiete.setCurrentRow(0)

            # Ereignis bei Auswahländerung in Liste Teilgebiete

        if not self.db_qkan:
            logger.error("self.qkan_db is not initialized.")
            return

        if not self.count_selection():
            del self.db_qkan
            return

        # Autokorrektur
        self.cb_profile_ergaenzen.setChecked(QKan.config.dyna.profile_ergaenzen)
        self.cb_autonummerierung_dyna.setChecked(QKan.config.dyna.autonummerierung)

        # Festlegung des Fangradius
        # Kann über Menü "Optionen" eingegeben werden
        fangradius = QKan.config.fangradius

        # Haltungsflächen (tezg) berücksichtigen
        self.cb_regardTezg.setChecked(QKan.config.mit_verschneidung)

        # Mindestflächengröße
        # Kann über Menü "Optionen" eingegeben werden
        mindestflaeche = QKan.config.mindestflaeche

        # Maximalzahl Schleifendurchläufe
        max_loops = QKan.config.max_loops

        # Optionen zur Berechnung der befestigten Flächen
        dynabef_choice = QKan.config.dyna.bef_choice
        if dynabef_choice == enums.BefChoice.FLAECHEN:
            self.rb_flaechen.setChecked(True)
        elif dynabef_choice == enums.BefChoice.TEZG:
            self.rb_tezg.setChecked(True)

        # Optionen zur Zuordnung des Profilschlüssels
        dynaprof_choice = QKan.config.dyna.prof_choice

        if dynaprof_choice == enums.ProfChoice.PROFILNAME:
            self.rb_profnam.setChecked(True)
        elif dynaprof_choice == enums.ProfChoice.PROFILKEY:
            self.rb_profkey.setChecked(True)

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
            dynafile: str = self.tf_KP_dest.text()
            template_dyna: str = self.tf_KP_template.text()
            profile_ergaenzen: bool = self.cb_profile_ergaenzen.isChecked()
            autonummerierung_dyna: bool = self.cb_autonummerierung_dyna.isChecked()
            mit_verschneidung: bool = self.cb_regardTezg.isChecked()
            if self.rb_flaechen.isChecked():
                dynabef_choice = enums.BefChoice.FLAECHEN
            elif self.rb_tezg.isChecked():
                dynabef_choice = enums.BefChoice.TEZG
            else:
                fehlermeldung(
                    "exportdyna.application.run",
                    "Fehlerhafte Option: \ndynabef_choice = {}".format(
                        repr(dynabef_choice)
                    ),
                )
            if self.rb_profnam.isChecked():
                dynaprof_choice = enums.ProfChoice.PROFILNAME
            elif self.rb_profkey.isChecked():
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
            logger.debug(
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


class ImportDialog(QKanDBDialog, IMPORT_CLASS):  # type: ignore
    button_box: QDialogButtonBox

    pb_selectDynaFile: QPushButton
    pb_selectProjectFile: QPushButton
    pb_selectQKanDB: QPushButton

    qsw_epsg: QgsProjectionSelectionWidget

    tf_dynaFile: QLineEdit
    tf_projectFile: QLineEdit

    def __init__(self, plugin: "DynaPorter", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        QKanDBDialog.open_mode = False

        self.bind_select_path(
            title="Dateinamen der zu lesenden Kanal++-Datei eingeben",
            file_filter="*.ein",
            line_edit=self.tf_dynaFile,
            push_button=self.pb_selectDynaFile,
            is_open=True,
        )
        self.bind_select_path(
            title="Dateinamen der zu erstellenden Projektdatei eingeben",
            file_filter="*.qgs",
            line_edit=self.tf_projectFile,
            push_button=self.pb_selectProjectFile,
            is_open=False,
        )

    def run(self) -> None:
        """Run method that performs all the real work"""

        self.tf_qkanDB.setText(QKan.config.database.qkan)
        self.tf_dynaFile.setText(QKan.config.dyna.file)

        # noinspection PyArgumentList,PyCallByClass
        self.qsw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))

        self.tf_projectFile.setText(QKan.config.project.file)

        # show the dialog
        self.show()
        # Run the dialog event loop
        result = self.exec_()
        # See if OK was pressed
        if result:
            # Namen der Datenbanken uebernehmen
            dynafile: str = self.tf_dynaFile.text()
            database_qkan: str = self.tf_qkanDB.text()
            projectfile: str = self.tf_projectFile.text()
            epsg: int = int(self.qsw_epsg.crs().postgisSrid())

            # Konfigurationsdaten schreiben
            QKan.config.database.qkan = database_qkan
            QKan.config.dyna.file = dynafile
            QKan.config.epsg = epsg
            QKan.config.project.file = projectfile

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            logger.debug(
                f"""QKan-Modul Aufruf
                importKanaldaten(
                    "{dynafile}", 
                    "{database_qkan}", 
                    "{projectfile}", 
                    {epsg}, 
                )"""
            )

            import_kanaldaten(
                dynafile,
                database_qkan,
                projectfile,
                epsg,
            )
