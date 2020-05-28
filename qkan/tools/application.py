# -*- coding: utf-8 -*-
"""
Flaechenzuordnungen
Diverse Tools zur QKan-Datenbank
"""

import logging
import os
import typing

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from qkan import QKan, enums, get_default_dir, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
    warnung,
)
# noinspection PyUnresolvedReferences
from . import resources
from .application_dialog import (
    LayersAdaptDialog,
    QKanOptionsDialog,
    QgsAdaptDialog,
    RunoffParamsDialog,
)
from .k_layersadapt import layersadapt
from .k_qgsadapt import qgsadapt
from .k_runoffparams import setRunoffparams

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.tools.application")


class QKanTools:
    def __init__(self, iface: QgisInterface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.default_dir = get_default_dir()
        self.db_qkan: typing.Optional[DBConnection] = None

        self.dlgla = LayersAdaptDialog(self)
        self.dlgop = QKanOptionsDialog(self)
        self.dlgpr = QgsAdaptDialog(self)
        self.dlgro = RunoffParamsDialog(self)

        logger.info("QKan_Tools initialisiert...")

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("QKanTools", message)

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_qgsadapt_path = ":/plugins/qkan/tools/res/icon_qgsadapt.png"
        QKan.instance.add_action(
            icon_qgsadapt_path,
            text=self.tr("Projektdatei auf bestehende QKan-Datenbank übertragen"),
            callback=self.run_qgsadapt,
            parent=self.iface.mainWindow(),
        )

        icon_layersadapt_path = ":/plugins/qkan/tools/res/icon_layersadapt.png"
        QKan.instance.add_action(
            icon_layersadapt_path,
            text=self.tr("Projektlayer auf QKan-Standard setzen"),
            callback=self.run_layersadapt,
            parent=self.iface.mainWindow(),
        )

        icon_qkanoptions_path = ":/plugins/qkan/tools/res/icon_qkanoptions.png"
        QKan.instance.add_action(
            icon_qkanoptions_path,
            text=self.tr("Allgemeine Optionen"),
            callback=self.run_qkanoptions,
            parent=self.iface.mainWindow(),
        )

        icon_runoffparams_path = ":/plugins/qkan/tools/res/icon_runoffparams.png"
        QKan.instance.add_action(
            icon_runoffparams_path,
            text=self.tr("Oberflächenabflussparameter eintragen"),
            callback=self.run_runoffparams,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        self.dlgla.close()
        self.dlgop.close()
        self.dlgpr.close()
        self.dlgro.close()

    def run_qgsadapt(self):
        """Erstellen einer Projektdatei aus einer Vorlage"""

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.db_qkan, epsg = get_database_QKan(silent=True)

        if self.db_qkan:
            self.default_dir = os.path.dirname(
                self.db_qkan
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.db_qkan = QKan.config.database.qkan
            self.dlgpr.tf_qkanDB.setText(self.db_qkan)
            self.default_dir = os.path.dirname(self.db_qkan)
        self.dlgpr.tf_qkanDB.setText(self.db_qkan)

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgpr.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # Status initialisieren
        self.dlgpr_applyQKanTemplate()

        # show the dialog
        self.dlgpr.show()
        # Run the dialog event loop
        result = self.dlgpr.exec_()

        # See if OK was pressed
        if result:
            # Inhalte aus Formular lesen --------------------------------------------------------------

            self.db_qkan: str = self.dlgpr.tf_qkanDB.text()
            project_file: str = self.dlgpr.tf_projectFile.text()
            self.apply_qkan_template: bool = self.dlgpr.cb_applyQKanTemplate.isChecked()

            # QKanTemplate nur, wenn nicht Option "QKan_Standard_anwenden" gewählt
            if self.apply_qkan_template:
                project_template: str = os.path.join(QKan.template_dir, "Projekt.qgs")
            else:
                project_template: str = self.dlgpr.tf_projectTemplate.text()

            # Konfigurationsdaten schreiben -----------------------------
            QKan.config.database.qkan = self.db_qkan
            QKan.config.project.file = project_file
            QKan.config.project.template = project_template
            QKan.config.tools.apply_qkan_template = self.apply_qkan_template

            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            logger.debug(
                f"""QKan-Modul Aufruf
                qgsadapt(
                    "{project_template}",
                    "{self.db_qkan}",
                    "{project_file}",
                    {self.apply_qkan_template},
                    epsg = None, 
                )"""
            )

            qgsadapt(
                project_template,
                self.db_qkan,
                project_file,
                self.apply_qkan_template,
                epsg=None,
            )

    def run_qkanoptions(self):
        """Bearbeitung allgemeiner QKan-Optionen"""

        # Formularfelder setzen -------------------------------------------------------------------------

        # Fangradius für Anfang der Anbindungslinie
        self.dlgop.tf_fangradius.setText(str(QKan.config.fangradius))

        # Mindestflächengröße
        self.dlgop.tf_mindestflaeche.setText(str(QKan.config.mindestflaeche))

        # Maximalzahl Schleifendurchläufe
        self.dlgop.tf_max_loops.setText(str(QKan.config.max_loops))

        # Optionen zum Typ der QKan-Datenbank
        datenbanktyp = QKan.config.database.type

        if datenbanktyp == enums.QKanDBChoice.SPATIALITE:
            self.dlgop.rb_spatialite.setChecked(True)
        # elif datenbanktyp == enums.QKanDBChoice.POSTGIS:
        # self.dlgop.rb_postgis.setChecked(True)

        epsg = QKan.config.epsg
        # noinspection PyCallByClass
        self.dlgop.qsw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(epsg))

        self.dlgop.tf_logeditor.setText(QKan.config.tools.logeditor)

        # Textfeld für Editor deaktivieren, falls leer:
        status_logeditor = QKan.config.tools.logeditor == ""
        self.dlgop.tf_logeditor.setEnabled(status_logeditor)

        # show the dialog
        self.dlgop.show()
        # Run the dialog event loop
        result = self.dlgop.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            fangradius: float = float(self.dlgop.tf_fangradius.text())
            mindestflaeche: float = float(self.dlgop.tf_mindestflaeche.text())
            max_loops: int = int(self.dlgop.tf_max_loops.text())
            logeditor: str = self.dlgop.tf_logeditor.text().strip()
            if self.dlgop.rb_spatialite.isChecked():
                datenbanktyp = enums.QKanDBChoice.SPATIALITE
            # elif self.dlgop.rb_postgis.isChecked():
            # datenbanktyp = enums.QKanDBChoice.POSTGIS
            else:
                fehlermeldung(
                    "tools.application.run",
                    f"Fehlerhafte Option: \ndatenbanktyp = {datenbanktyp}",
                )
            epsg: int = int(self.dlgop.qsw_epsg.crs().postgisSrid())

            QKan.config.database.type = datenbanktyp
            QKan.config.epsg = epsg
            QKan.config.fangradius = fangradius
            QKan.config.max_loops = max_loops
            QKan.config.mindestflaeche = mindestflaeche
            QKan.config.tools.logeditor = logeditor
            QKan.config.save()

    def run_runoffparams(self):
        """Berechnen und Eintragen der Oberflächenabflussparameter in die Tabelle flaechen"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({"flaechen"} & get_editable_layers()) > 0:
            warnung(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
            )
            return False

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            logger.error(
                "tools.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False
        self.dlgro.tf_QKanDB.setText(database_QKan)

        manningrauheit_bef = QKan.config.tools.manningrauheit_bef
        manningrauheit_dur = QKan.config.tools.manningrauheit_dur

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in tools.application.runoffparams:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        # Check, ob alle Teilgebiete in Flächen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, "QKan_Tools.application.run (1) "):
            del self.dbQK
            return False

        # Check, ob alle Abflussparameter in Flächen auch in Tabelle "abflussparameter" enthalten

        sql = """INSERT INTO abflussparameter (apnam)
                SELECT abflussparameter FROM flaechen 
                WHERE abflussparameter IS NOT NULL AND
                abflussparameter NOT IN (SELECT apnam FROM abflussparameter)
                GROUP BY abflussparameter"""
        if not self.dbQK.sql(sql, "QKan_Tools.application.run (2) "):
            del self.dbQK
            return False

        self.dbQK.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        liste_teilgebiete = QKan.config.selections.teilgebiete

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = '''SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'''
        if not self.dbQK.sql(sql, "QKan_Tools.application.run (4) "):
            del self.dbQK
            return False
        daten = self.dbQK.fetchall()
        self.dlgro.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.dlgro.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in liste_teilgebiete:
                    self.dlgro.lw_teilgebiete.setCurrentRow(ielem)
                    self.dlgro.cb_selTgbActive.setChecked(True)
            except BaseException as err:
                fehlermeldung(
                    "QKan_Tools (6), Fehler in elem = {}\n".format(elem), repr(err)
                )
                # if len(daten) == 1:
                # self.dlgro.lw_teilgebiete.setCurrentRow(0)

        # Anlegen der Tabelle zur Auswahl der Abflussparameter

        # Zunächst wird die Liste der beim letzten Mal gewählten Abflussparameter aus config gelesen
        liste_abflussparameter = QKan.config.selections.abflussparameter

        # Abfragen der Tabelle abflussparameter nach Abflussparametern
        sql = '''SELECT "apnam" FROM "abflussparameter" GROUP BY "apnam"'''
        if not self.dbQK.sql(sql, "QKan_Tools.application.run (4) "):
            del self.dbQK
            return False
        daten = self.dbQK.fetchall()
        self.dlgro.lw_abflussparameter.clear()

        for ielem, elem in enumerate(daten):
            self.dlgro.lw_abflussparameter.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in liste_abflussparameter:
                    self.dlgro.lw_abflussparameter.setCurrentRow(ielem)
                    self.dlgro.cb_selParActive.setChecked(True)
            except BaseException as err:
                fehlermeldung(
                    "QKan_Tools (6), Fehler in elem = {}\n".format(elem), repr(err)
                )
                # if len(daten) == 1:
                # self.dlgro.lw_abflussparameter.setCurrentRow(0)

        self.dlgro_countselection()

        # Funktionen zur Berechnung des Oberflächenabflusses
        # Werden nur gelesen
        runoffparamsfunctions = QKan.config.tools.runoffparamsfunctions

        # Optionen zur Berechnung des Oberflächenabflusses
        runoffparamstype_choice = QKan.config.tools.runoffparamstype_choice

        if runoffparamstype_choice == enums.RunOffParamsType.ITWH:
            self.dlgro.rb_itwh.setChecked(True)
        elif runoffparamstype_choice == enums.RunOffParamsType.DYNA:
            self.dlgro.rb_dyna.setChecked(True)
        elif runoffparamstype_choice == enums.RunOffParamsType.MANIAK:
            self.dlgro.rb_maniak.setChecked(True)

        runoffmodeltype_choice = QKan.config.tools.runoffmodeltype_choice

        if runoffmodeltype_choice == enums.RunOffModelType.SPEICHERKASKADE:
            self.dlgro.rb_kaskade.setChecked(True)
        elif runoffmodeltype_choice == enums.RunOffModelType.FLIESSZEITEN:
            self.dlgro.rb_fliesszeiten.setChecked(True)
        elif runoffmodeltype_choice == enums.RunOffModelType.SCHWERPUNKTLAUFZEIT:
            self.dlgro.rb_schwerpunktlaufzeit.setChecked(True)

        # Status Radiobuttons initialisieren
        self.dlgro_activateitwh()
        # Datenbanktyp
        datenbanktyp = QKan.config.database.type

        # Formular anzeigen

        self.dlgro.show()
        # Run the dialog event loop
        result = self.dlgro.exec_()
        # See if OK was pressed
        if result:

            # Abrufen der ausgewählten Elemente in den Listen
            liste_teilgebiete: typing.List[str] = list_selected_items(
                self.dlgro.lw_teilgebiete
            )
            liste_abflussparameter: typing.List[str] = list_selected_items(
                self.dlgro.lw_abflussparameter
            )

            # Eingaben aus Formular übernehmen
            database_QKan: str = self.dlgro.tf_QKanDB.text()
            if self.dlgro.rb_itwh.isChecked():
                runoffparamstype_choice = enums.RunOffParamsType.ITWH
            elif self.dlgro.rb_dyna.isChecked():
                runoffparamstype_choice = enums.RunOffParamsType.DYNA
            elif self.dlgro.rb_maniak.isChecked():
                runoffparamstype_choice = enums.RunOffParamsType.MANIAK
            else:
                fehlermeldung(
                    "tools.runoffparams.run_runoffparams",
                    "Fehlerhafte Option: runoffparamstype_choice",
                )
            if self.dlgro.rb_kaskade.isChecked():
                runoffmodeltype_choice = enums.RunOffModelType.SPEICHERKASKADE
            elif self.dlgro.rb_fliesszeiten.isChecked():
                runoffmodeltype_choice = enums.RunOffModelType.FLIESSZEITEN
            elif self.dlgro.rb_schwerpunktlaufzeit.isChecked():
                runoffmodeltype_choice = enums.RunOffModelType.SCHWERPUNKTLAUFZEIT
            else:
                fehlermeldung(
                    "tools.runoffparams.run_runoffparams",
                    "Fehlerhafte Option: runoffmodeltype_choice",
                )

            # Konfigurationsdaten schreiben
            QKan.config.selections.abflussparameter = liste_abflussparameter
            QKan.config.selections.teilgebiete = liste_teilgebiete
            QKan.config.database.qkan = database_QKan
            QKan.config.tools.runoffmodeltype_choice = runoffmodeltype_choice
            QKan.config.tools.runoffparamstype_choice = runoffparamstype_choice

            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            logger.debug(
                f"""QKan-Modul Aufruf
                setRunoffparams(
                    self.dbQK,
                    {runoffparamstype_choice},
                    {runoffmodeltype_choice},
                    {runoffparamsfunctions},
                    {liste_teilgebiete},
                    {liste_abflussparameter},
                )"""
            )

            setRunoffparams(
                self.dbQK,
                runoffparamstype_choice,
                runoffmodeltype_choice,
                runoffparamsfunctions,
                liste_teilgebiete,
                liste_abflussparameter,
            )
        del self.dbQK

    def run_layersadapt(self):
        """Anpassen oder Ergänzen von Layern entsprechend der QKan-Datenstrukturen"""

        # QKan-Projekt
        project = QgsProject.instance()

        if project.count() == 0:
            warnung("Benutzerfehler: ", "Es ist kein Projekt geladen.")
            return

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.db_qkan, epsg = get_database_QKan(silent=True)

        if self.db_qkan:
            self.default_dir = os.path.dirname(
                self.db_qkan
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.db_qkan = QKan.config.database.qkan
            self.dlgla.tf_qkanDB.setText(self.db_qkan)
            self.default_dir = os.path.dirname(self.db_qkan)
        self.dlgla.tf_qkanDB.setText(self.db_qkan)

        dbQK = DBConnection(
            dbname=self.db_qkan, qkanDBUpdate=False
        )  # Datenbankobjekt der QKan-Datenbank
        # qkanDBUpdate: mit Update

        # Falls die Datenbank nicht aktuell ist (self.dbIsUptodate = False), werden alle Elemente im Formular
        # deaktiviert. Nur der Checkbutton zur Aktualisierung der Datenbank bleibt aktiv und es erscheint
        # eine Information.
        self.dbIsUptodate = dbQK.isCurrentVersion

        # Datenbank wieder schließen.
        del dbQK

        self.dlgla.gb_projectTemplate.setEnabled(self.dbIsUptodate)
        self.dlgla.gb_LayersAdapt.setEnabled(self.dbIsUptodate)
        self.dlgla.gb_selectLayers.setEnabled(self.dbIsUptodate)
        self.dlgla.gb_setNodeTypes.setEnabled(self.dbIsUptodate)
        self.dlgla.gb_updateQkanDB.setEnabled(not self.dbIsUptodate)
        self.dlgla.cb_qkanDBUpdate.setChecked(not self.dbIsUptodate)

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgla.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # GGfs. Standardvorlage schon eintragen
        if self.apply_qkan_template:
            self.projectTemplate = os.path.join(QKan.template_dir, "Projekt.qgs")
            self.dlgla.tf_projectTemplate.setText(self.projectTemplate)

        # Groupbox "Layer anpassen" ---------------------------------------------------------------------------

        # Checkbox "Datenbankanbindung"
        adapt_db = QKan.config.adapt.database
        self.dlgla.cb_adaptDB.setChecked(adapt_db)

        # Checkbox "Projektionssystem anpassen"
        adapt_kbs = QKan.config.adapt.kbs
        self.dlgla.cb_adaptKBS.setChecked(adapt_kbs)

        # Checkbox "Wertbeziehungungen in Tabellen"
        adapt_table_lookups = QKan.config.adapt.table_lookups
        self.dlgla.cb_adaptTableLookups.setChecked(adapt_table_lookups)

        # Checkbox "Formularanbindungen"
        adapt_forms = QKan.config.adapt.forms
        self.dlgla.cb_adaptForms.setChecked(adapt_forms)

        # Groupbox "QKan-Layer" ---------------------------------------------------------------------------

        # Optionen zur Berücksichtigung der vorhandenen Tabellen
        adapt_selected = QKan.config.adapt.selected_layers
        if adapt_selected == enums.SelectedLayers.SELECTED:
            self.dlgla.rb_adaptSelected.setChecked(True)
        elif adapt_selected == enums.SelectedLayers.ALL:
            self.dlgla.rb_adaptAll.setChecked(True)
        else:
            fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
            return False

        # Checkbox: Fehlende QKan-Layer ergänzen
        fehlende_layer_ergaenzen = QKan.config.adapt.add_missing_layers
        self.dlgla.cb_completeLayers.setChecked(fehlende_layer_ergaenzen)

        # Weitere Formularfelder ---------------------------------------------------------------------------

        # Checkbox: Knotentype per Abfrage ermitteln und in "schaechte.knotentyp" eintragen
        update_node_type = QKan.config.adapt.update_node_type
        self.dlgla.cb_updateNodetype.setChecked(update_node_type)

        # Checkbox: Nach Aktualisierung auf alle Layer zoomen
        self.dlgla.cb_zoomAll.setChecked(QKan.config.adapt.zoom_all)

        # Checkbox: QKan-Standard anwenden
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgla.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # # Checkbox: QKan-Datenbank aktualisieren
        # if self.dbIsUptodate:
        # self.qkanDBUpdate = QKan.config.tools.qkan_db_update
        # else:
        # self.qkanDBUpdate = True
        # else:
        # self.qkanDBUpdate = True

        # Status initialisieren
        self.dlgla_enableQkanDB()
        self.dlgla_applyQKanTemplate()
        self.dlgla_enableProjectTemplateGroup()

        # -----------------------------------------------------------------------------------------------------
        # show the dialog
        self.dlgla.show()
        # Run the dialog event loop
        result = self.dlgla.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            self.qkanDBUpdate: bool = self.dlgla.cb_qkanDBUpdate.isChecked()
            # Achtung: Beeinflusst auch
            #  - adapt_table_lookups
            #  - adapt_selected

            self.db_qkan: str = self.dlgla.tf_qkanDB.text()
            adapt_db: bool = self.dlgla.cb_adaptDB.isChecked()
            adapt_table_lookups: bool = (
                self.dlgla.cb_adaptTableLookups.isChecked() or self.qkanDBUpdate
            )
            adapt_forms: bool = self.dlgla.cb_adaptForms.isChecked()
            adapt_kbs: bool = self.dlgla.cb_adaptKBS.isChecked()
            update_node_type: bool = self.dlgla.cb_updateNodetype.isChecked()
            zoom_alles: bool = self.dlgla.cb_zoomAll.isChecked()
            self.apply_qkan_template: bool = self.dlgla.cb_applyQKanTemplate.isChecked()
            if self.apply_qkan_template:
                self.projectTemplate = ""
            else:
                self.projectTemplate: str = self.dlgla.tf_projectTemplate.text()

            # Optionen zur Berücksichtigung der vorhandenen Tabellen
            fehlende_layer_ergaenzen: bool = self.dlgla.cb_completeLayers.isChecked()
            if self.dlgla.rb_adaptAll.isChecked() or self.qkanDBUpdate:
                adapt_selected = enums.SelectedLayers.ALL
            elif self.dlgla.rb_adaptSelected.isChecked():
                adapt_selected = enums.SelectedLayers.SELECTED
            else:
                fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
                return False

            # Konfigurationsdaten schreiben -----------------------------------------------------------

            QKan.config.adapt.add_missing_layers = fehlende_layer_ergaenzen
            QKan.config.adapt.database = adapt_db
            QKan.config.adapt.forms = adapt_forms
            QKan.config.adapt.kbs = adapt_kbs
            QKan.config.adapt.qkan_db_update = self.qkanDBUpdate
            QKan.config.adapt.selected_layers = adapt_selected
            QKan.config.adapt.table_lookups = adapt_table_lookups
            QKan.config.adapt.update_node_type = update_node_type
            QKan.config.adapt.zoom_all = zoom_alles
            QKan.config.database.qkan = self.db_qkan
            QKan.config.tools.apply_qkan_template = self.apply_qkan_template
            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            logger.debug(
                f"""QKan-Modul Aufruf
                layersadapt(
                    "{self.db_qkan}",
                    "{self.projectTemplate}",
                    {self.dbIsUptodate},
                    {self.qkanDBUpdate},
                    {adapt_db},
                    {adapt_table_lookups},
                    {adapt_forms},
                    {adapt_kbs},
                    {update_node_type},
                    {zoom_alles},
                    {fehlende_layer_ergaenzen},
                    {adapt_selected},
                )"""
            )

            layersadapt(
                self.db_qkan,
                self.projectTemplate,
                self.dbIsUptodate,
                self.qkanDBUpdate,
                adapt_db,
                adapt_table_lookups,
                adapt_forms,
                adapt_kbs,
                update_node_type,
                zoom_alles,
                fehlende_layer_ergaenzen,
                adapt_selected,
            )
