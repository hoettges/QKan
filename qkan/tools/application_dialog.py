# -*- coding: utf-8 -*-
"""
LinkFlaechenToHaltungDialog
Verknüpft Flächen mit nächster Haltung
"""
import datetime
import logging
import os
import site
import subprocess
import tempfile
import typing
import webbrowser
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
)
from qgis._gui import QgsProjectionSelectionWidget

from qkan import QKan, list_selected_items
from qkan.database.qkan_utils import meldung, sqlconditions

if typing.TYPE_CHECKING:
    from .application import QKanTools

logger = logging.getLogger("QKan.tools.application_dialog")
FORM_CLASS_qgsadapt, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_qgsadapt.ui")
)
FORM_CLASS_layersadapt, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_layersadapt.ui")
)
FORM_CLASS_qkanoptions, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_qkanoptions.ui")
)
FORM_CLASS_runoffparams, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_runoffparams.ui")
)


def click_help_la():
    helpfile = (
        Path(__file__).parent / ".." / "doc/sphinx/build/html/Qkan_Formulare.html",
    )
    webbrowser.open_new_tab(str(helpfile) + "#projektlayer-auf-qkan-standard-setzen")


def click_help_rp():
    helpfile = (
        Path(__file__).parent / ".." / "doc/sphinx/build/html/Qkan_Formulare.html",
    )
    webbrowser.open_new_tab(
        str(helpfile) + "#berechnung-von-oberflachenabflussparametern"
    )


class QgsAdaptDialog(QDialog, FORM_CLASS_qgsadapt):
    button_box: QDialogButtonBox

    cb_applyQKanTemplate: QCheckBox
    cb_qkanDBUpdate: QCheckBox

    groupBox_2: QGroupBox
    groupBox: QGroupBox

    pb_selectProjectFile: QPushButton
    pb_selectProjectTemplate: QPushButton
    pb_selectQKanDB: QPushButton

    tf_projectFile: QLineEdit
    tf_projectTemplate: QLineEdit
    tf_qkanDB: QLineEdit

    def __init__(self, plugin: "QKanTools", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        self.pb_selectProjectFile.clicked.connect(self.select_project_file)
        self.pb_selectQKanDB.clicked.connect(self.select_qkan_db)
        self.pb_selectProjectTemplate.clicked.connect(self.select_project_template)
        self.cb_applyQKanTemplate.clicked.connect(self.click_apply_template)

    def select_project_file(self):
        """Zu erstellende Projektdatei festlegen"""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getSaveFileName(
            self,
            "Dateinamen der zu erstellenden Projektdatei eingeben",
            self.plugin.default_dir,
            "*.qgs",
        )

        if os.path.dirname(filename) != "":
            self.tf_projectFile.setText(filename)

    def select_qkan_db(self):
        """Anzubindende QKan-Datenbank festlegen"""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "QKan-Datenbank auswählen", self.plugin.default_dir, "*.sqlite"
        )
        if os.path.dirname(filename) != "":
            self.tf_qkanDB.setText(filename)

    def click_apply_template(self):
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.cb_applyQKanTemplate.isChecked()
        self.tf_projectTemplate.setEnabled(not checked)

    def select_project_template(self):
        """Vorlage-Projektdatei auswählen"""

        self.cb_applyQKanTemplate.setChecked(False)  # automatisch deaktivieren
        self.click_apply_template()  # Auswirkungen auslösen

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self,
            "Vorlage für zu erstellende Projektdatei auswählen",
            self.templateDir,
            "*.qgs",
        )
        if os.path.dirname(filename) != "":
            self.tf_projectTemplate.setText(filename)


class LayersAdaptDialog(QDialog, FORM_CLASS_layersadapt):
    button_box: QDialogButtonBox

    cb_adaptDB: QCheckBox
    cb_adaptForms: QCheckBox
    cb_adaptKBS: QCheckBox
    cb_adaptTableLookups: QCheckBox
    cb_applyQKanTemplate: QCheckBox
    cb_completeLayers: QCheckBox
    cb_qkanDBUpdate: QCheckBox
    cb_updateNodetype: QCheckBox
    cb_zoomAll: QCheckBox

    gb_LayersAdapt: QGroupBox
    gb_projectTemplate: QGroupBox
    gb_selectLayers: QGroupBox
    gb_setNodeTypes: QGroupBox
    gb_updateQkanDB: QGroupBox

    lb_projectTemplate: QLabel

    pb_selectProjectTemplate: QPushButton
    pb_selectQKanDB: QPushButton

    rb_adaptAll: QRadioButton
    rb_adaptSelected: QRadioButton

    tf_projectTemplate: QLineEdit
    tf_qkanDB: QLineEdit

    def __init__(self, plugin: "QKanTools", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        self.pb_selectQKanDB.clicked.connect(self.select_qkan_db)
        self.cb_adaptDB.clicked.connect(self.click_enable_qkan_db)
        self.pb_selectProjectTemplate.clicked.connect(self.select_project_template)
        self.button_box.helpRequested.connect(click_help_la)
        self.cb_adaptForms.clicked.connect(self.click_adapt_forms)
        self.cb_adaptTableLookups.clicked.connect(self.click_adapt_table_lookups)
        self.cb_adaptKBS.clicked.connect(self.click_adapt_kbs)
        self.cb_applyQKanTemplate.clicked.connect(self.click_apply_template)
        self.cb_qkanDBUpdate.clicked.connect(self.click_qkan_db_update)

    def select_qkan_db(self):
        """Anzubindende QKan-Datenbank festlegen"""

        self.cb_adaptDB.setChecked(True)  # automatisch aktivieren

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "QKan-Datenbank auswählen", self.plugin.default_dir, "*.sqlite"
        )
        if os.path.dirname(filename) != "":
            self.tf_qkanDB.setText(filename)

    def click_enable_qkan_db(self):
        """Aktiviert oder deaktiviert das Textfeld für die Datenbankanbindung"""

        checked = self.cb_adaptDB.isChecked()

        self.tf_qkanDB.setEnabled(checked)
        # self.pb_selectQKanDB.setEnabled(checked)

        self.click_adapt_kbs()  # Korrigiert ggfs. cb_adaptKBS

    def click_adapt_forms(self):
        self.click_qkan_db_update()

    def click_adapt_table_lookups(self):
        self.click_qkan_db_update()
        self.enable_project_template_group()

    def click_adapt_kbs(self):
        """
        Hält Checkbutton cb_adaptKBS aktiv, solange cb_adaptDB aktiv ist, weil bei
        Änderung der Datenbankanbindung immer das Projektionssystem überprüft
        werden soll.
        """
        if self.cb_adaptDB.isChecked():
            if not self.cb_adaptKBS.isChecked():
                meldung(
                    "",
                    "Bei einer Anpassung der Layeranbindungen muss auch die Anpassung des KBS aktiviert sein!",
                )
            self.cb_adaptKBS.setChecked(True)

    def click_qkan_db_update(self):
        """
        Setzt cb_adaptTableLookups, wenn cb_qkanDBUpdate gesetzt
        """

        if self.cb_qkanDBUpdate.isChecked():
            if not self.cb_adaptTableLookups.isChecked():
                meldung(
                    "",
                    "Bei einem Update der QKan-Datenbank muss auch die "
                    "Anpassung von Wertbeziehungungen und Formularanbindungen "
                    "aktiviert sein!",
                )

            self.cb_adaptTableLookups.setChecked(True)
            # self.click_adapt_table_lookups()

    def click_apply_template(self):
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.cb_applyQKanTemplate.isChecked()
        self.tf_projectTemplate.setEnabled(not checked)

    def enable_project_template_group(self):
        """
        Aktiviert oder deaktiviert die Groupbox für das Projektdatei-Template
        abhängig von den angeklickten Checkbuttons
        """

        checked = self.cb_adaptTableLookups.isChecked()
        self.gb_projectTemplate.setEnabled(checked)

    def select_project_template(self):
        """Vorlage-Projektdatei auswählen"""

        self.cb_applyQKanTemplate.setChecked(False)  # automatisch deaktivieren
        self.click_apply_template()  # Auswirkungen auslösen

        if self.cb_adaptTableLookups.isChecked():
            template_dir = QKan.template_dir
        else:
            try:
                template_dir = os.path.dirname(self.plugin.db_qkan.dbname)
            except:
                logger.error(
                    "Programmfehler in tools.run_layersadapt:\nPfad konnte nicht auf "
                    + "database_QKan gesetzt werden.\n database_QKan = {}".format(
                        self.database_QKan
                    )
                )
                template_dir = QKan.template_dir

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self.dlgla, "Projektdatei als Vorlage auswählen", template_dir, "*.qgs"
        )
        if os.path.dirname(filename) != "":
            self.tf_projectTemplate.setText(filename)


class QKanOptionsDialog(QDialog, FORM_CLASS_qkanoptions):
    button_box: QDialogButtonBox

    pb_fangradiusDefault: QPushButton
    pb_max_loopsDefault: QPushButton
    pb_mindestflaecheDefault: QPushButton
    pb_openLogfile: QPushButton
    pb_openOptionsfile: QPushButton
    pb_selectLogeditor: QPushButton

    qsw_epsg: QgsProjectionSelectionWidget

    rb_postgis: QRadioButton
    rb_spatialite: QRadioButton

    tf_fangradius: QLineEdit
    tf_logeditor: QLineEdit
    tf_max_loops: QLineEdit
    tf_mindestflaeche: QLineEdit

    def __init__(self, plugin: "QKanTools", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        self.pb_fangradiusDefault.clicked.connect(self.click_reset_fangradius)
        self.pb_mindestflaecheDefault.clicked.connect(self.click_reset_mindestflaeche)
        self.pb_max_loopsDefault.clicked.connect(self.click_reset_max_loops)
        self.pb_openLogfile.clicked.connect(self.click_open_log)
        self.pb_openOptionsfile.clicked.connect(self.click_open_settings)
        self.pb_selectLogeditor.clicked.connect(self.select_log_editor)
        # self.rb_itwh.toggled.connect(self.dlgro_activatedyna)

    def click_reset_fangradius(self):
        self.tf_fangradius.setText("0.1")

    def click_reset_mindestflaeche(self):
        self.tf_mindestflaeche.setText("0.5")

    def click_reset_max_loops(self):
        self.tf_max_loops.setText("1000")

    def click_open_log(self):
        """
        Öffnet die Log-Datei mit dem Standard-Editor für Log-Dateien
        oder einem gewählten Editor
        """

        if QKan.config.tools.logeditor == "":
            os.startfile(QKan.instance.log_path, "open")
        else:
            command = '"{}" "{}"'.format(
                os.path.normpath(QKan.config.tools.logeditor),
                os.path.normcase(QKan.instance.log_path),
            )
            res = subprocess.call(command)
            logger.debug("command: {}\nres: ".format(command, res))

    def click_open_settings(self):
        """
        Öffnet die Optionen-Datei (*.json) mit dem Standard-Editor für
        Log-Dateien oder einem gewählten Editor
        """

        config_file = Path(site.getuserbase()) / "qkan" / "qkan.json"

        if QKan.config.tools.logeditor == "":
            os.startfile(config_file, "open")
        else:
            command = '"{}" "{}"'.format(
                os.path.normpath(QKan.config.tools.logeditor),
                os.path.normcase(config_file),
            )
            res = subprocess.call(command)
            logger.debug("command: {}\nres: ".format(command, res))

    def select_log_editor(self):
        """Alternativen Text-Editor auswählen"""

        # Textfeld wieder deaktivieren
        self.tf_logeditor.setEnabled(True)

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self.dlgop, "Alternativen Texteditor auswählen", "c:/", "*.exe"
        )
        QKan.config.tools.logeditor = filename
        self.tf_logeditor.setText(filename)
        if os.path.dirname(filename) == "":
            # Textfeld wieder deaktivieren
            self.tf_logeditor.setEnabled(False)


class RunoffParamsDialog(QDialog, FORM_CLASS_runoffparams):
    button_box: QDialogButtonBox

    cb_selParActive: QCheckBox
    cb_selTgbActive: QCheckBox

    lf_anzahl_flaechen: QLabel

    lw_abflussparameter: QListWidget
    lw_teilgebiete: QListWidget

    pb_selectQKanDB: QPushButton

    rb_dyna: QRadioButton
    rb_fliesszeiten: QRadioButton
    rb_itwh: QRadioButton
    rb_kaskade: QRadioButton
    rb_maniak: QRadioButton
    rb_schwerpunktlaufzeit: QRadioButton

    tf_QKanDB: QLineEdit

    def __init__(self, plugin: "QKanTools", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

        self.lw_teilgebiete.itemClicked.connect(self.click_lw_teilgebiete)
        self.lw_abflussparameter.itemClicked.connect(self.click_lw_abflussparam)
        self.cb_selTgbActive.stateChanged.connect(self.click_tgb_selection)
        self.cb_selParActive.stateChanged.connect(self.click_par_selection)
        self.button_box.helpRequested.connect(click_help_rp)
        self.pb_selectQKanDB.clicked.connect(self.select_qkan_db)
        self.rb_itwh.toggled.connect(self.toggle_itwh)

    def select_qkan_db(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self.dlgro, "QKan-Datenbank auswählen", self.plugin.default_dir, "*.sqlite"
        )
        self.tf_QKanDB.setText(filename)

    def click_lw_teilgebiete(self):
        """Reaktion auf Klick in Tabelle"""

        self.cb_selTgbActive.setChecked(True)
        self.count_selection()

    def click_lw_abflussparam(self):
        """Reaktion auf Klick in Tabelle"""

        self.cb_selParActive.setChecked(True)
        self.count_selection()

    def click_tgb_selection(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selTgbActive.isChecked():
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

    def click_par_selection(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selParActive.isChecked():
            # Nix tun ...
            logger.debug("\nChecked = True")
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_abflussparameter.count()
            for i in range(anz):
                item = self.lw_abflussparameter.item(i)
                item.setSelected(False)
                # self.lw_abflussparameter.setItemSelected(item, False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def toggle_itwh(self):
        """Reagiert auf Auswahl itwh und deaktiviert entsprechend die Option Fließzeiten"""

        if self.rb_itwh.isChecked():
            if self.rb_fliesszeiten.isChecked():
                self.rb_kaskade.setChecked(True)
            self.rb_fliesszeiten.setEnabled(False)
        else:
            self.rb_fliesszeiten.setEnabled(True)

    def count_selection(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        liste_teilgebiete: typing.List[str] = list_selected_items(self.lw_teilgebiete)
        liste_abflussparameter: typing.List[str] = list_selected_items(
            self.lw_abflussparameter
        )

        # Auswahl der zu bearbeitenden Flächen
        auswahl = sqlconditions(
            "WHERE",
            ["teilgebiet", "abflussparameter"],
            [liste_teilgebiete, liste_abflussparameter],
        )

        sql = f"SELECT count(*) AS anzahl FROM flaechen {auswahl}"

        if not self.plugin.db_qkan.sql(sql, "QKan_Tools.application.dlgro_countselection (1)"):
            return False
        daten = self.plugin.db_qkan.fetchone()
        if not (daten is None):
            self.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.lf_anzahl_flaechen.setText("0")
