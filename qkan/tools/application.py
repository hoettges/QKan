# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Flaechenzuordnungen
                                 A QGIS plugin
 Diverse Tools zur QKan-Datenbank
                              -------------------
        begin                : 2017-06-12
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Jörg Höttges/FH Aachen
        email                : hoettges@fh-aachen.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import json
import logging
import os
import site
import subprocess
import tempfile
from datetime import datetime as dt
from pathlib import Path

from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QFileDialog, QListWidgetItem
from qgis.gui import QgsMessageBar
from qgis.utils import iface, pluginDirectory
from qgis.core import QgsProject, QgsCoordinateReferenceSystem

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (get_database_QKan, get_editable_layers, 
            warnung, fehlermeldung, meldung, sqlconditions)
# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences
from . import resources
# Import the code for the dialog
from .application_dialog import QgsAdaptDialog, LayersAdaptDialog, QKanOptionsDialog, RunoffParamsDialog
from .k_layersadapt import layersadapt
from .k_qgsadapt import qgsadapt
from .k_runoffparams import setRunoffparams

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger(u'QKan.tools.application')


class QKanTools:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # Create the dialog (after translation) and keep reference
        self.dlgpr = QgsAdaptDialog()
        self.dlgla = LayersAdaptDialog()
        self.dlgop = QKanOptionsDialog()
        self.dlgro = RunoffParamsDialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 12.06.2017)

        logger.info(u'\n\nQKan_Tools initialisiert...')

        # Pfad zum Vorlagenverzeichnis sicherstellen
        self.templateDir = os.path.join(pluginDirectory('qkan'), u"templates")

        # Formularereignisse anbinden ----------------------------------------------

        # Formular dlgpr - QKan-Projektdatei übertragen
        self.dlgpr.pb_selectProjectFile.clicked.connect(self.dlgpr_selectFileProjectfile)
        self.dlgpr.pb_selectQKanDB.clicked.connect(self.dlgpr_selectFile_qkanDB)
        self.dlgpr.pb_selectProjectTemplate.clicked.connect(self.dlgpr_selectFileProjectTemplate)
        self.dlgpr.cb_applyQKanTemplate.clicked.connect(self.dlgpr_applyQKanTemplate)

        # Formular dlgla - Projektdatei anpassen an QKan-Standard
        self.dlgla.pb_selectQKanDB.clicked.connect(self.dlgla_selectFile_qkanDB)
        self.dlgla.cb_adaptDB.clicked.connect(self.dlgla_enableQkanDB)
        self.dlgla.pb_selectProjectTemplate.clicked.connect(self.dlgla_selectProjectTemplate)
        self.dlgla.button_box.helpRequested.connect(self.dlgla_helpClick)
        self.dlgla.cb_adaptForms.clicked.connect(self.dlgla_cb_adaptForms)
        self.dlgla.cb_adaptTableLookups.clicked.connect(self.dlgla_cb_adaptTableLookups)
        self.dlgla.cb_adaptKBS.clicked.connect(self.dlgla_cb_adaptKBS)
        self.dlgla.cb_applyQKanTemplate.clicked.connect(self.dlgla_applyQKanTemplate)
        self.dlgla.cb_qkanDBUpdate.clicked.connect(self.dlgla_checkqkanDBUpdate)

        # Formular dlgop - QKan-Optionen
        self.dlgop.pb_fangradiusDefault.clicked.connect(self.dlgop_fangradiusDefault)
        self.dlgop.pb_mindestflaecheDefault.clicked.connect(self.dlgop_mindestflaecheDefault)
        self.dlgop.pb_max_loopsDefault.clicked.connect(self.dlgop_maxLoopsDefault)
        self.dlgop.pb_openLogfile.clicked.connect(self.dlgop_openLogfile)
        self.dlgop.pb_selectLogeditor.clicked.connect(self.dlgop_selectLogeditor)

        # Formular dlgro - Oberflächenabflussparameter ermitteln
        self.dlgro.lw_teilgebiete.itemClicked.connect(self.dlgro_lwTeilgebieteClick)
        self.dlgro.lw_abflussparameter.itemClicked.connect(self.dlgro_lwAbflussparamsClick)
        self.dlgro.cb_selTgbActive.stateChanged.connect(self.dlgro_selTgbActiveClick)
        self.dlgro.cb_selParActive.stateChanged.connect(self.dlgro_selParActiveClick)
        self.dlgro.button_box.helpRequested.connect(self.dlgro_helpClick)
        self.dlgro.pb_selectQKanDB.clicked.connect(self.dlgro_selectFile_qkanDB)
        self.dlgro.rb_itwh.toggled.connect(self.dlgro_activateitwh)
        # self.dlgop.rb_itwh.toggled.connect(self.dlgro_activatedyna)

        # Ende Eigene Funktionen ---------------------------------------------------

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QKanTools', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_qgsadapt_path = ':/plugins/qkan/tools/res/icon_qgsadapt.png'
        QKan.instance.add_action(
            icon_qgsadapt_path,
            text=self.tr(u'Projektdatei auf bestehende QKan-Datenbank übertragen'),
            callback=self.run_qgsadapt,
            parent=self.iface.mainWindow())

        icon_layersadapt_path = ':/plugins/qkan/tools/res/icon_layersadapt.png'
        QKan.instance.add_action(
            icon_layersadapt_path,
            text=self.tr(u'Projektlayer auf QKan-Standard setzen'),
            callback=self.run_layersadapt,
            parent=self.iface.mainWindow())

        icon_qkanoptions_path = ':/plugins/qkan/tools/res/icon_qkanoptions.png'
        QKan.instance.add_action(
            icon_qkanoptions_path,
            text=self.tr('Allgemeine Optionen'),
            callback=self.run_qkanoptions,
            parent=self.iface.mainWindow())

        icon_runoffparams_path = ':/plugins/qkan/tools/res/icon_runoffparams.png'
        QKan.instance.add_action(
            icon_runoffparams_path,
            text=self.tr(u'Oberflächenabflussparameter eintragen'),
            callback=self.run_runoffparams,
            parent=self.iface.mainWindow())

    def unload(self):
        pass

    @staticmethod
    def listselecteditems(listWidget):
        """Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

        :param listWidget: String for translation.
        :type listWidget: QListWidgetItem

        :returns: Tuple containing selected teilgebiete
        :rtype: tuple
        """
        items = listWidget.selectedItems()
        liste = []
        for elem in items:
            liste.append(elem.text())
        return liste

    # -----------------------------------------------------------------------------------------------------
    # Erstellen einer Projektdatei aus einer Vorlage

    # 1. Formularfunktionen

    def dlgpr_selectFileProjectfile(self):
        """Zu erstellende Projektdatei festlegen"""

        filename, __ = QFileDialog.getSaveFileName(self.dlgpr,
                                                       u"Dateinamen der zu erstellenden Projektdatei eingeben",
                                                       self.default_dir,
                                                       "*.qgs")
        # logger.info('Dateiname wurde erkannt zu:\n{}'.format(filename))

        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgpr.tf_projectFile.setText(filename)

    def dlgpr_selectFile_qkanDB(self):
        """Anzubindende QKan-Datenbank festlegen"""

        filename, __ = QFileDialog.getOpenFileName(self.dlgpr,
                                                       u"QKan-Datenbank auswählen",
                                                       self.default_dir,
                                                       "*.sqlite")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgpr.tf_qkanDB.setText(filename)

    def dlgpr_applyQKanTemplate(self):
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.dlgpr.cb_applyQKanTemplate.isChecked()
        self.dlgpr.tf_projectTemplate.setEnabled(not checked)

    def dlgpr_selectFileProjectTemplate(self):
        """Vorlage-Projektdatei auswählen"""

        self.dlgpr.cb_applyQKanTemplate.setChecked(False)  # automatisch deaktivieren
        self.dlgpr_applyQKanTemplate()  # Auswirkungen auslösen

        filename, __ = QFileDialog.getOpenFileName(self.dlgpr,
                                                       u"Vorlage für zu erstellende Projektdatei auswählen",
                                                       self.templateDir,
                                                       "*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgpr.tf_projectTemplate.setText(filename)

    # -----------------------------------------------------------------------------------------------------
    # 2. Aufruf des Formulars

    def run_qgsadapt(self):
        '''Erstellen einer Projektdatei aus einer Vorlage'''

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.database_QKan, self.epsg = get_database_QKan(silent=True)

        if self.database_QKan:
            self.default_dir = os.path.dirname(self.database_QKan)  # bereits geladene QKan-Datenbank übernehmen
        elif 'database_QKan' in QKan.config:
            self.database_QKan = QKan.config['database_QKan']
            self.dlgpr.tf_qkanDB.setText(self.database_QKan)
            self.default_dir = os.path.dirname(self.database_QKan)
        else:
            self.database_QKan = ''
            self.default_dir = '.'
        self.dlgpr.tf_qkanDB.setText(self.database_QKan)

        # Formularfeld Vorlagedatei
        if 'projectTemplate' in QKan.config:
            projectTemplate = QKan.config['projectTemplate']
        else:
            projectTemplate = ''

        # Formularfeld Projektdatei
        if 'projectfile' in QKan.config:
            projectFile = QKan.config['projectfile']
        else:
            projectFile = ''

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen 
        if 'QKan_Standard_anwenden' in QKan.config:
            self.applyQKanTemplate = QKan.config['QKan_Standard_anwenden']
        else:
            self.applyQKanTemplate = True
        self.dlgpr.cb_applyQKanTemplate.setChecked(self.applyQKanTemplate)

        # Status initialisieren
        self.dlgpr_applyQKanTemplate()

        # show the dialog
        self.dlgpr.show()
        # Run the dialog event loop
        result = self.dlgpr.exec_()

        # See if OK was pressed
        if result:
            # Inhalte aus Formular lesen --------------------------------------------------------------

            self.database_QKan = self.dlgpr.tf_qkanDB.text()
            projectFile = self.dlgpr.tf_projectFile.text()
            self.applyQKanTemplate = self.dlgpr.cb_applyQKanTemplate.isChecked()

            # QKanTemplate nur, wenn nicht Option "QKan_Standard_anwenden" gewählt
            if self.applyQKanTemplate:
                templateDir = os.path.join(pluginDirectory('qkan'), u"templates")
                projectTemplate = os.path.join(templateDir,'Projekt.qgs')
            else:
                projectTemplate = self.dlgpr.tf_projectTemplate.text()


            # Konfigurationsdaten schreiben -----------------------------------------------------------

            QKan.config['projectTemplate'] = projectTemplate
            QKan.config['database_QKan'] = self.database_QKan
            QKan.config['projectfile'] = projectFile
            QKan.config['QKan_Standard_anwenden'] = self.applyQKanTemplate

            QKan.save_config()

            qgsadapt(projectTemplate, self.database_QKan, self.epsg, projectFile,
                     self.applyQKanTemplate, u'SpatiaLite')

    # ----------------------------------------------------------------------------------------------------
    # Allgemeine QKan-Optionen bearbeiten

    # 1. Formularfunktionen

    def dlgop_fangradiusDefault(self):
        self.dlgop.tf_fangradius.setText('0.1')

    def dlgop_mindestflaecheDefault(self):
        self.dlgop.tf_mindestflaeche.setText('0.5')

    def dlgop_maxLoopsDefault(self):
        self.dlgop.tf_max_loops.setText('1000')

    def dlgop_openLogfile(self):
        """Öffnet die Log-Datei mit dem Standard-Editor für Log-Dateien oder einem gewählten Editor"""

        fnam = Path(tempfile.gettempdir()) / "QKan_{}.log".format(dt.today().strftime("%Y-%m-%d"))
        # dnam = dt.today().strftime("%Y%m%d")
        # fnam = os.path.join(tempfile.gettempdir(), 'QKan{}.log'.format(dnam))
        if self.logeditor == '':
            os.startfile(fnam, 'open')
        else:
            command = '"{}" "{}"'.format(os.path.normpath(self.logeditor), os.path.normcase(fnam))
            res = subprocess.call(command)
            logger.debug('command: {}\nres: '.format(command, res))

    def dlgop_selectLogeditor(self):
        """Alternativen Text-Editor auswählen"""

        # Textfeld wieder deaktivieren
        self.dlgop.tf_logeditor.setEnabled(True)

        filename, __ = QFileDialog.getOpenFileName(self.dlgop,
                                                       u"Alternativen Texteditor auswählen",
                                                       "c:/",
                                                       "*.exe")
        self.logeditor = filename
        self.dlgop.tf_logeditor.setText(filename)
        if os.path.dirname(filename) == '':
            # Textfeld wieder deaktivieren
            self.dlgop.tf_logeditor.setEnabled(False)

    # -----------------------------------------------------------------------------------------
    # 2. Aufruf des Formulars

    def run_qkanoptions(self):
        '''Bearbeitung allgemeiner QKan-Optionen'''

        # Formularfelder setzen -------------------------------------------------------------------------

        # Fangradius für Anfang der Anbindungslinie
        if 'fangradius' in QKan.config:
            fangradius = QKan.config['fangradius']
        else:
            fangradius = u'0.1'
        self.dlgop.tf_fangradius.setText(str(fangradius))

        # Mindestflächengröße
        if 'mindestflaeche' in QKan.config:
            mindestflaeche = QKan.config['mindestflaeche']
        else:
            mindestflaeche = u'0.5'
        self.dlgop.tf_mindestflaeche.setText(str(mindestflaeche))

        # Maximalzahl Schleifendurchläufe
        if 'max_loops' in QKan.config:
            max_loops = QKan.config['max_loops']
        else:
            max_loops = 1000
        self.dlgop.tf_max_loops.setText(str(max_loops))

        # Optionen zum Typ der QKan-Datenbank
        if 'datenbanktyp' in QKan.config:
            datenbanktyp = QKan.config['datenbanktyp']
        else:
            datenbanktyp = u'spatialite'

        if datenbanktyp == u'spatialite':
            self.dlgop.rb_spatialite.setChecked(True)
        # elif datenbanktyp == u'postgis':
        # self.dlgop.rb_postgis.setChecked(True)

        if 'epsg' in QKan.config:
            self.epsg = QKan.config['epsg']
            # logger.debug('tools.run_qkanoptions (1): id(QKan): {0:}\n\t\tepsg: {1:}'.format(id(QKan), self.epsg))
        else:
            self.epsg = u'25832'
        self.dlgop.qsw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(int(self.epsg)))

        if 'logeditor' in QKan.config:
            self.logeditor = QKan.config['logeditor']
        else:
            self.logeditor = ''
        self.dlgop.tf_logeditor.setText(self.logeditor)

        # Textfeld für Editor deaktivieren, falls leer:
        status_logeditor = (self.logeditor == '')
        self.dlgop.tf_logeditor.setEnabled(status_logeditor)

        # show the dialog
        self.dlgop.show()
        # Run the dialog event loop
        result = self.dlgop.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            fangradius = self.dlgop.tf_fangradius.text()
            mindestflaeche = self.dlgop.tf_mindestflaeche.text()
            max_loops = int(self.dlgop.tf_max_loops.text())
            self.logeditor = self.dlgop.tf_logeditor.text().strip()
            if self.dlgop.rb_spatialite.isChecked():
                datenbanktyp = u'spatialite'
            # elif self.dlgop.rb_postgis.isChecked():
            # datenbanktyp = u'postgis'
            else:
                fehlermeldung(u"tools.application.run",
                              u"Fehlerhafte Option: \ndatenbanktyp = {}".format(repr(datenbanktyp)))
            self.epsg = str(self.dlgop.qsw_epsg.crs().postgisSrid())

            QKan.config['fangradius'] = fangradius
            QKan.config['mindestflaeche'] = mindestflaeche
            QKan.config['max_loops'] = max_loops
            QKan.config['datenbanktyp'] = datenbanktyp
            QKan.config['epsg'] = self.epsg
            QKan.config['logeditor'] = self.logeditor

            QKan.save_config()

    # ----------------------------------------------------------------------------------------------------
    # Oberflächenabflussparameter in QKan-Tabellen eintragen, ggfs. nur für ausgewählte Teilgebiete

    # 1. Formularfunktionen

    def dlgro_selectFile_qkanDB(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        filename, __ = QFileDialog.getOpenFileName(self.dlgro, u"QKan-Datenbank auswählen",
                                                       self.default_dir, "*.sqlite")
        # if os.path.dirname(filename) != '':
        # os.chdir(os.path.dirname(filename))
        self.dlgro.tf_QKanDB.setText(filename)

    def dlgro_helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(self.plugin_dir,
                                '../doc/sphinx/build/html/Qkan_Formulare.html#berechnung-von-oberflachenabflussparametern')
        webbrowser.open_new_tab(helpfile)

    def dlgro_lwTeilgebieteClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlgro.cb_selTgbActive.setChecked(True)
        self.dlgro_countselection()

    def dlgro_lwAbflussparamsClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlgro.cb_selParActive.setChecked(True)
        self.dlgro_countselection()

    def dlgro_selTgbActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlgro.cb_selTgbActive.isChecked():
            # Nix tun ...
            logger.debug('\nChecked = True')
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlgro.lw_teilgebiete.count()
            for i in range(anz):
                item = self.dlgro.lw_teilgebiete.item(i)
                item.setSelected(False)
                # self.dlgro.lw_teilgebiete.setItemSelected(item, False)

            # Anzahl in der Anzeige aktualisieren
            self.dlgro_countselection()

    def dlgro_selParActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlgro.cb_selParActive.isChecked():
            # Nix tun ...
            logger.debug('\nChecked = True')
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlgro.lw_abflussparameter.count()
            for i in range(anz):
                item = self.dlgro.lw_abflussparameter.item(i)
                item.setSelected(False)
                # self.dlgro.lw_abflussparameter.setItemSelected(item, False)

            # Anzahl in der Anzeige aktualisieren
            self.dlgro_countselection()

    def dlgro_activateitwh(self):
        """Reagiert auf Auswahl itwh und deaktiviert entsprechend die Option Fließzeiten"""

        if self.dlgro.rb_itwh.isChecked():
            if self.dlgro.rb_fliesszeiten.isChecked():
                self.dlgro.rb_kaskade.setChecked(True)
            self.dlgro.rb_fliesszeiten.setEnabled(False)
        else:
            self.dlgro.rb_fliesszeiten.setEnabled(True)

    def dlgro_countselection(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        liste_teilgebiete = self.listselecteditems(self.dlgro.lw_teilgebiete)
        liste_abflussparameter = self.listselecteditems(self.dlgro.lw_abflussparameter)

        # Auswahl der zu bearbeitenden Flächen
        auswahl = sqlconditions('WHERE', ('teilgebiet', 'abflussparameter'),
                                (liste_teilgebiete, liste_abflussparameter))

        sql = u"""SELECT count(*) AS anzahl FROM flaechen{auswahl}""".format(auswahl=auswahl)

        if not self.dbQK.sql(sql, u"QKan_Tools.application.dlgro_countselection (1)"):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlgro.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.dlgro.lf_anzahl_flaechen.setText('0')

    def run_runoffparams(self):
        """Berechnen und Eintragen der Oberflächenabflussparameter in die Tabelle flaechen"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({'flaechen'} & get_editable_layers()) > 0:
            warnung("Bedienerfehler: ",
                   'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!')
            return False

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_QKan = ''

        database_QKan, self.epsg = get_database_QKan()
        if not database_QKan:
            logger.error(u"tools.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False
        self.dlgro.tf_QKanDB.setText(database_QKan)

        if 'manningrauheit_bef' in QKan.config:
            manningrauheit_bef = QKan.config['manningrauheit_bef']
        else:
            manningrauheit_bef = 0.02
            QKan.config['manningrauheit_bef'] = manningrauheit_bef
        if 'manningrauheit_dur' in QKan.config:
            manningrauheit_dur = QKan.config['manningrauheit_dur']
        else:
            manningrauheit_dur = 0.10
            QKan.config['manningrauheit_dur'] = manningrauheit_dur

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            fehlermeldung(u"Fehler in tools.application.runoffparams:\n",
                         u'QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!'.format(
                             database_QKan))
            return None

        # Check, ob alle Teilgebiete in Flächen auch in Tabelle "teilgebiete" enthalten

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"QKan_Tools.application.run (1) "):
            return False

        # Check, ob alle Abflussparameter in Flächen auch in Tabelle "abflussparameter" enthalten

        sql = u"""INSERT INTO abflussparameter (apnam)
                SELECT abflussparameter FROM flaechen 
                WHERE abflussparameter IS NOT NULL AND
                abflussparameter NOT IN (SELECT apnam FROM abflussparameter)
                GROUP BY abflussparameter"""
        if not self.dbQK.sql(sql, u"QKan_Tools.application.run (2) "):
            return False

        self.dbQK.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        liste_teilgebiete = []
        if 'liste_teilgebiete' in QKan.config:
            liste_teilgebiete = QKan.config['liste_teilgebiete']

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = '''SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'''
        if not self.dbQK.sql(sql, u"QKan_Tools.application.run (4) "):
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
                fehlermeldung(u'QKan_Tools (6), Fehler in elem = {}\n'.format(elem), repr(err))
                # if len(daten) == 1:
                # self.dlgro.lw_teilgebiete.setCurrentRow(0)

        # Anlegen der Tabelle zur Auswahl der Abflussparameter

        # Zunächst wird die Liste der beim letzten Mal gewählten Abflussparameter aus config gelesen
        liste_abflussparameter = []
        if 'liste_abflussparameter' in QKan.config:
            liste_abflussparameter = QKan.config['liste_abflussparameter']

        # Abfragen der Tabelle abflussparameter nach Abflussparametern
        sql = '''SELECT "apnam" FROM "abflussparameter" GROUP BY "apnam"'''
        if not self.dbQK.sql(sql, u"QKan_Tools.application.run (4) "):
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
                fehlermeldung(u'QKan_Tools (6), Fehler in elem = {}\n'.format(elem), repr(err))
                # if len(daten) == 1:
                # self.dlgro.lw_abflussparameter.setCurrentRow(0)

        self.dlgro_countselection()

        # Funktionen zur Berechnung des Oberflächenabflusses
        # Werden nur gelesen
        if 'runoffparamsfunctions' in QKan.config:
            runoffparamsfunctions = QKan.config['runoffparamsfunctions']
        else:
            runoffparamsfunctions = {
                'itwh': [
                    '0.8693*log(area(geom))+ 5.6317',
                    'pow(18.904*pow(neigkl,0.686)*area(geom), 0.2535*pow(neigkl,0.244))'],
                'dyna': [
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(
                        rauheit_bef=manningrauheit_bef),
                    'pow(2*{rauheit_dur} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(
                        rauheit_dur=manningrauheit_dur)],
                'Maniak': [
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(
                        rauheit_bef=manningrauheit_bef),
                    'pow(2*{rauheit_dur} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(
                        rauheit_dur=manningrauheit_dur),
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * abstand / SQRT(neigung), 0.467)'.format(
                        rauheit_bef=manningrauheit_bef),
                    'pow(2*{rauheit_dur} * abstand / SQRT(neigung), 0.467)'.format(rauheit_dur=manningrauheit_dur),
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * fliesslaenge / SQRT(neigung), 0.467)'.format(
                        rauheit_bef=manningrauheit_bef),
                    'pow(2*{rauheit_dur} * fliesslaenge / SQRT(neigung), 0.467)'.format(rauheit_dur=manningrauheit_dur)]
            }
            QKan.config['runoffparamsfunctions'] = runoffparamsfunctions

        # Optionen zur Berechnung des Oberflächenabflusses
        if 'runoffparamstype_choice' in QKan.config:
            runoffparamstype_choice = QKan.config['runoffparamstype_choice']
        else:
            runoffparamstype_choice = u'Maniak'

        if runoffparamstype_choice == u'itwh':
            self.dlgro.rb_itwh.setChecked(True)
        elif runoffparamstype_choice == u'dyna':
            self.dlgro.rb_dyna.setChecked(True)
        elif runoffparamstype_choice == u'Maniak':
            self.dlgro.rb_maniak.setChecked(True)

        if 'runoffmodelltype_choice' in QKan.config:
            runoffmodelltype_choice = QKan.config['runoffmodelltype_choice']
        else:
            runoffmodelltype_choice = u'Speicherkaskade'

        if runoffmodelltype_choice == u'Speicherkaskade':
            self.dlgro.rb_kaskade.setChecked(True)
        elif runoffmodelltype_choice == u'Fliesszeiten':
            self.dlgro.rb_fliesszeiten.setChecked(True)
        elif runoffmodelltype_choice == u'Schwerpunktlaufzeit':
            self.dlgro.rb_schwerpunktlaufzeit.setChecked(True)

        # Status Radiobuttons initialisieren
        self.dlgro_activateitwh()
        # Datenbanktyp
        if 'datenbanktyp' in QKan.config:
            datenbanktyp = QKan.config['datenbanktyp']
        else:
            datenbanktyp = 'spatialite'

        # Formular anzeigen

        self.dlgro.show()
        # Run the dialog event loop
        result = self.dlgro.exec_()
        # See if OK was pressed
        if result:

            # Abrufen der ausgewählten Elemente in den Listen
            liste_teilgebiete = self.listselecteditems(self.dlgro.lw_teilgebiete)
            liste_abflussparameter = self.listselecteditems(self.dlgro.lw_abflussparameter)

            # Eingaben aus Formular übernehmen
            database_QKan = self.dlgro.tf_QKanDB.text()
            if self.dlgro.rb_itwh.isChecked():
                runoffparamstype_choice = u'itwh'
            elif self.dlgro.rb_dyna.isChecked():
                runoffparamstype_choice = u'dyna'
            elif self.dlgro.rb_maniak.isChecked():
                runoffparamstype_choice = u'Maniak'
            else:
                fehlermeldung(u"tools.runoffparams.run_runoffparams",
                              u"Fehlerhafte Option: \nrunoffparamstype_choice = {}".format(
                                  repr(runoffparamstype_choice)))
            if self.dlgro.rb_kaskade.isChecked():
                runoffmodelltype_choice = u'Speicherkaskade'
            elif self.dlgro.rb_fliesszeiten.isChecked():
                runoffmodelltype_choice = u'Fliesszeiten'
            elif self.dlgro.rb_schwerpunktlaufzeit.isChecked():
                runoffmodelltype_choice = u'Schwerpunktlaufzeit'
            else:
                fehlermeldung(u"tools.runoffparams.run_runoffparams",
                              u"Fehlerhafte Option: \nrunoffmodelltype_choice = {}".format(
                                  repr(runoffmodelltype_choice)))

            # Konfigurationsdaten schreiben
            QKan.config['database_QKan'] = database_QKan
            QKan.config['liste_teilgebiete'] = liste_teilgebiete
            QKan.config['liste_abflussparameter'] = liste_abflussparameter
            QKan.config['runoffparamstype_choice'] = runoffparamstype_choice
            QKan.config['runoffmodelltype_choice'] = runoffmodelltype_choice

            QKan.save_config()

            setRunoffparams(self.dbQK, runoffparamstype_choice, runoffmodelltype_choice, runoffparamsfunctions,
                            liste_teilgebiete, liste_abflussparameter, datenbanktyp)

    # -----------------------------------------------------------------------------------------------------
    # Anpassen/Ergänzen von QKan-Layern

    # 1. Formularfunktionen

    def dlgla_helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(self.plugin_dir,
                                '../doc/sphinx/build/html/Qkan_Formulare.html#projektlayer-auf-qkan-standard-setzen')
        webbrowser.open_new_tab(helpfile)

    def dlgla_selectFile_qkanDB(self):
        """Anzubindende QKan-Datenbank festlegen"""

        self.dlgla.cb_adaptDB.setChecked(True)  # automatisch aktivieren
        filename, __ = QFileDialog.getOpenFileName(self.dlgla,
                                                       u"QKan-Datenbank auswählen",
                                                       self.default_dir,
                                                       "*.sqlite")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgla.tf_qkanDB.setText(filename)

    def dlgla_enableQkanDB(self):
        """Aktiviert oder deaktiviert das Textfeld für die Datenbankanbindung"""

        checked = self.dlgla.cb_adaptDB.isChecked()

        self.dlgla.tf_qkanDB.setEnabled(checked)
        # self.dlgla.pb_selectQKanDB.setEnabled(checked)

        self.dlgla_cb_adaptKBS()  # Korrigiert ggfs. cb_adaptKBS

    def dlgla_enableProjectTemplateGroup(self):
        """Aktiviert oder deaktiviert die Groupbox für das Projektdatei-Template
            abhängig von den angeklickten Checkbuttons
        """

        checked = self.dlgla.cb_adaptTableLookups.isChecked()
        self.dlgla.gb_projectTemplate.setEnabled(checked)

    def dlgla_cb_adaptForms(self):
        self.dlgla_checkqkanDBUpdate()

    def dlgla_cb_adaptTableLookups(self):
        self.dlgla_checkqkanDBUpdate()
        self.dlgla_enableProjectTemplateGroup()

    def dlgla_cb_adaptKBS(self):
        """Hält Checkbutton cb_adaptKBS aktiv, solange cb_adaptDB aktiv ist, weil bei 
           Änderung der Datenbankanbindung immer das Projektionssystem überprüft 
           werden soll. 
        """
        if self.dlgla.cb_adaptDB.isChecked():
            if not self.dlgla.cb_adaptKBS.isChecked():
                meldung("", u"Bei einer Anpassung der Layeranbindungen muss auch die Anpassung des KBS aktiviert sein!")
            self.dlgla.cb_adaptKBS.setChecked(True)

    def dlgla_applyQKanTemplate(self):
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.dlgla.cb_applyQKanTemplate.isChecked()
        self.dlgla.tf_projectTemplate.setEnabled(not checked)

    def dlgla_selectProjectTemplate(self):
        """Vorlage-Projektdatei auswählen"""

        self.dlgla.cb_applyQKanTemplate.setChecked(False)  # automatisch deaktivieren
        self.dlgla_applyQKanTemplate()  # Auswirkungen auslösen

        if self.dlgla.cb_adaptTableLookups.isChecked():
            self.templateDir = os.path.join(pluginDirectory('qkan'), u"templates")
        else:
            try:
                self.templateDir = os.path.dirname(self.database_QKan)
            except:
                logger.error('Programmfehler in tools.run_layersadapt:\nPfad konnte nicht auf ' + \
                             'database_QKan gesetzt werden.\n database_QKan = {}'.format(
                                 self.database_QKan))
                self.templateDir = ''

        filename, __ = QFileDialog.getOpenFileName(self.dlgla,
                                                       "Projektdatei als Vorlage auswählen",
                                                       self.templateDir,
                                                       "*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgla.tf_projectTemplate.setText(filename)

    def dlgla_checkqkanDBUpdate(self):
        """Setzt cb_adaptTableLookups, wenn cb_qkanDBUpdate gesetzt
        """

        if self.dlgla.cb_qkanDBUpdate.isChecked():
            if not self.dlgla.cb_adaptTableLookups.isChecked():
                meldung("",
                        u"Bei einem Update der QKan-Datenbank muss auch die Anpassung von Wertbeziehungungen und Formularanbindungen aktiviert sein!")

            self.dlgla.cb_adaptTableLookups.setChecked(True)
            # self.dlgla_cb_adaptTableLookups()

    # -----------------------------------------------------------------------------------------------------
    # 2. Aufruf des Formulars

    def run_layersadapt(self):
        '''Anpassen oder Ergänzen von Layern entsprechend der QKan-Datenstrukturen'''

        # QKan-Projekt
        project = QgsProject.instance()
        
        if project.count() == 0:
            warnung(u'Benutzerfehler: ', u'Es ist kein Projekt geladen.')
            return

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.database_QKan, self.epsg = get_database_QKan(silent=True)

        if self.database_QKan:
            self.default_dir = os.path.dirname(self.database_QKan)  # bereits geladene QKan-Datenbank übernehmen
        elif 'database_QKan' in QKan.config:
            self.database_QKan = QKan.config['database_QKan']
            self.dlgla.tf_qkanDB.setText(self.database_QKan)
            self.default_dir = os.path.dirname(self.database_QKan)
        else:
            self.database_QKan = ''
            self.default_dir = '.'
        self.dlgla.tf_qkanDB.setText(self.database_QKan)

        dbQK = DBConnection(dbname=self.database_QKan, qkanDBUpdate=False)  # Datenbankobjekt der QKan-Datenbank
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
        if 'QKan_Standard_anwenden' in QKan.config:
            self.applyQKanTemplate = QKan.config['QKan_Standard_anwenden']
        else:
            self.applyQKanTemplate = True
        self.dlgla.cb_applyQKanTemplate.setChecked(self.applyQKanTemplate)

        # GGfs. Standardvorlage schon eintragen
        if self.applyQKanTemplate:
            self.projectTemplate = os.path.join(self.templateDir, 'Projekt.qgs')
            self.dlgla.tf_projectTemplate.setText(self.projectTemplate)

        # Groupbox "Layer anpassen" ---------------------------------------------------------------------------

        # Checkbox "Datenbankanbindung"
        if 'anpassen_Datenbankanbindung' in QKan.config:
            self.anpassen_Datenbankanbindung = QKan.config['anpassen_Datenbankanbindung']
        else:
            self.anpassen_Datenbankanbindung = True
        self.dlgla.cb_adaptDB.setChecked(self.anpassen_Datenbankanbindung)

        # Checkbox "Projektionssystem anpassen"
        if 'anpassen_Projektionssystem' in QKan.config:
            self.anpassen_Projektionssystem = QKan.config['anpassen_Projektionssystem']
        else:
            self.anpassen_Projektionssystem = True
        self.dlgla.cb_adaptKBS.setChecked(self.anpassen_Projektionssystem)

        # Checkbox "Wertbeziehungungen in Tabellen"
        if 'anpassen_Wertebeziehungen_in_Tabellen' in QKan.config:
            self.anpassen_Wertebeziehungen_in_Tabellen = QKan.config['anpassen_Wertebeziehungen_in_Tabellen']
        else:
            self.anpassen_Wertebeziehungen_in_Tabellen = True
        self.dlgla.cb_adaptTableLookups.setChecked(self.anpassen_Wertebeziehungen_in_Tabellen)

        # Checkbox "Formularanbindungen"
        if 'anpassen_Formulare' in QKan.config:
            self.anpassen_Formulare = QKan.config['anpassen_Formulare']
        else:
            self.anpassen_Formulare = True
        self.dlgla.cb_adaptForms.setChecked(self.anpassen_Formulare)

        # Groupbox "QKan-Layer" ---------------------------------------------------------------------------

        # Optionen zur Berücksichtigung der vorhandenen Tabellen
        if 'anpassen_auswahl' in QKan.config:
            anpassen_auswahl = QKan.config['anpassen_auswahl']
        else:
            anpassen_auswahl = 'alle_anpassen'

        if anpassen_auswahl == 'auswahl_anpassen':
            self.dlgla.rb_adaptSelected.setChecked(True)
        elif anpassen_auswahl == 'alle_anpassen':
            self.dlgla.rb_adaptAll.setChecked(True)
        else:
            fehlermeldung(u"Fehler im Programmcode", u"Nicht definierte Option")
            return False

        # Checkbox: Fehlende QKan-Layer ergänzen
        if 'fehlende_layer_ergaenzen' in QKan.config:
            self.fehlende_layer_ergaenzen = QKan.config['fehlende_layer_ergaenzen']
        else:
            self.fehlende_layer_ergaenzen = True
        self.dlgla.cb_completeLayers.setChecked(self.fehlende_layer_ergaenzen)

        # Weitere Formularfelder ---------------------------------------------------------------------------

        # Checkbox: Knotentype per Abfrage ermitteln und in "schaechte.knotentyp" eintragen
        if 'aktualisieren_Schachttypen' in QKan.config:
            aktualisieren_Schachttypen = QKan.config['aktualisieren_Schachttypen']
        else:
            aktualisieren_Schachttypen = True
        self.dlgla.cb_updateNodetype.setChecked(aktualisieren_Schachttypen)

        # Checkbox: Nach Aktualisierung auf alle Layer zoomen
        if 'zoom_alles' in QKan.config:
            zoom_alles = QKan.config['zoom_alles']
        else:
            zoom_alles = True
        self.dlgla.cb_zoomAll.setChecked(zoom_alles)

        # Checkbox: QKan-Standard anwenden
        if 'QKan_Standard_anwenden' in QKan.config:
            self.applyQKanTemplate = QKan.config['QKan_Standard_anwenden']
        else:
            self.applyQKanTemplate = True
        self.dlgla.cb_applyQKanTemplate.setChecked(self.applyQKanTemplate)

        # # Checkbox: QKan-Datenbank aktualisieren
        # if self.dbIsUptodate:
            # if 'qkanDBUpdate' in QKan.config:
                # self.qkanDBUpdate = QKan.config['qkanDBUpdate']
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

            self.qkanDBUpdate = self.dlgla.cb_qkanDBUpdate.isChecked()
            # Achtung: Beeinflusst auch
            #  - self.anpassen_Wertebeziehungen_in_Tabellen
            #  - anpassen_auswahl

            self.database_QKan = self.dlgla.tf_qkanDB.text()
            self.anpassen_Datenbankanbindung = self.dlgla.cb_adaptDB.isChecked()
            self.anpassen_Wertebeziehungen_in_Tabellen = self.dlgla.cb_adaptTableLookups.isChecked() or self.qkanDBUpdate
            self.anpassen_Formulare = self.dlgla.cb_adaptForms.isChecked()
            self.anpassen_Projektionssystem = self.dlgla.cb_adaptKBS.isChecked()
            aktualisieren_Schachttypen = self.dlgla.cb_updateNodetype.isChecked()
            zoom_alles = self.dlgla.cb_zoomAll.isChecked()
            self.applyQKanTemplate = self.dlgla.cb_applyQKanTemplate.isChecked()
            if self.applyQKanTemplate:
                self.projectTemplate = ''
            else:
                self.projectTemplate = self.dlgla.tf_projectTemplate.text()

            # Optionen zur Berücksichtigung der vorhandenen Tabellen
            fehlende_layer_ergaenzen = self.dlgla.cb_completeLayers.isChecked()
            if self.dlgla.rb_adaptAll.isChecked() or self.qkanDBUpdate:
                anpassen_auswahl = 'alle_anpassen'
            elif self.dlgla.rb_adaptSelected.isChecked():
                anpassen_auswahl = 'auswahl_anpassen'
            else:
                fehlermeldung(u"Fehler im Programmcode", u"Nicht definierte Option")
                return False

            # Konfigurationsdaten schreiben -----------------------------------------------------------

            QKan.config['database_QKan'] = self.database_QKan
            QKan.config['anpassen_Datenbankanbindung'] = self.anpassen_Datenbankanbindung
            QKan.config['anpassen_Wertebeziehungen_in_Tabellen'] = self.anpassen_Wertebeziehungen_in_Tabellen
            QKan.config['anpassen_Formulare'] = self.anpassen_Formulare
            QKan.config['anpassen_Projektionssystem'] = self.anpassen_Projektionssystem
            QKan.config['fehlende_layer_ergaenzen'] = fehlende_layer_ergaenzen
            QKan.config['anpassen_auswahl'] = anpassen_auswahl
            QKan.config['qkanDBUpdate'] = self.qkanDBUpdate
            QKan.config['aktualisieren_Schachttypen'] = aktualisieren_Schachttypen
            QKan.config['zoom_alles'] = zoom_alles
            QKan.config['QKan_Standard_anwenden'] = self.applyQKanTemplate

            QKan.save_config()

            # Modulaufruf in Logdatei schreiben
            logger.debug('''qkan-Modul:\n        layersadapt(
                database_QKan={database_QKan}), 
                projectTemplate={projectTemplate}, 
                dbIsUptodate={dbIsUptodate}, 
                qkanDBUpdate={qkanDBUpdate}, 
                anpassen_Datenbankanbindung={anpassen_Datenbankanbindung}, 
                anpassen_Wertebeziehungen_in_Tabellen={anpassen_Wertebeziehungen_in_Tabellen}, 
                anpassen_Formulare={anpassen_Formulare}, 
                anpassen_Projektionssystem={anpassen_Projektionssystem}, 
                aktualisieren_Schachttypen={aktualisieren_Schachttypen}, 
                zoom_alles={zoom_alles}, 
                fehlende_layer_ergaenzen ={fehlende_layer_ergaenzen}, 
                anpassen_auswahl = {anpassen_auswahl}, 
                dbtyp = {dbtyp})'''.format(
                database_QKan=self.database_QKan, 
                projectTemplate=self.projectTemplate, 
                qkanDBUpdate=self.qkanDBUpdate, 
                dbIsUptodate=self.dbIsUptodate, 
                anpassen_Datenbankanbindung=self.anpassen_Datenbankanbindung, 
                anpassen_Wertebeziehungen_in_Tabellen=self.anpassen_Wertebeziehungen_in_Tabellen, 
                anpassen_Formulare=self.anpassen_Formulare, 
                anpassen_Projektionssystem=self.anpassen_Projektionssystem, 
                aktualisieren_Schachttypen=aktualisieren_Schachttypen, 
                zoom_alles=zoom_alles, 
                fehlende_layer_ergaenzen =fehlende_layer_ergaenzen, 
                anpassen_auswahl = anpassen_auswahl, 
                dbtyp = 'SpatiaLite'))

            layersadapt(self.database_QKan, self.projectTemplate, self.dbIsUptodate, self.qkanDBUpdate,
                        self.anpassen_Datenbankanbindung, self.anpassen_Wertebeziehungen_in_Tabellen,
                        self.anpassen_Formulare,
                        self.anpassen_Projektionssystem, aktualisieren_Schachttypen, zoom_alles,
                        fehlende_layer_ergaenzen, anpassen_auswahl, u'SpatiaLite')
