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
import tempfile
import os
import site
from datetime import datetime as dt
import subprocess

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QFileDialog, QListWidgetItem, QTableWidgetItem
from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface, pluginDirectory
from qgis.gui import QgsGenericProjectionSelector

# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences 
import resources
# Import the code for the dialog
from application_dialog import QgsAdaptDialog, LayersAdaptDialog, QKanOptionsDialog, RunoffParamsDialog
from k_qgsadapt import qgsadapt
from k_layersadapt import layersadapt
from k_runoffparams import setRunoffparams
from qkan import Dummy
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import get_database_QKan, get_editable_layers, fehlermeldung, meldung, sqlconditions, isQkanLayer

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
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Flaechenzuordnungen_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlgpr = QgsAdaptDialog()
        self.dlgla = LayersAdaptDialog()
        self.dlgop = QKanOptionsDialog()
        self.dlgro = RunoffParamsDialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 12.06.2017)

        logger.info(u'\n\nQKan_Tools initialisiert...')

        # --------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(), 'qkan')

        # Pfad zum Vorlagenverzeichnis sicherstellen
        self.templateDir = os.path.join(pluginDirectory('qkan'), u"templates")

        if not os.path.isdir(wordir):
            os.makedirs(wordir)

        # --------------------------------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        self.configfil = os.path.join(wordir, 'qkan.json')
        if os.path.exists(self.configfil):
            with open(self.configfil, 'r') as fileconfig:
                self.config = json.loads(fileconfig.read())
        else:
            self.config = {'epsg': '25832'}  # Projektionssystem
            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

        # Formularereignisse anbinden ----------------------------------------------

        # Formular dlgpr - QKan-Projektdatei übertragen
        self.dlgpr.pb_selectProjectFile.clicked.connect(self.dlgpr_selectFileProjectfile)
        self.dlgpr.pb_selectQKanDB.clicked.connect(self.dlgpr_selectFile_qkanDB)
        self.dlgpr.pb_selectProjectTemplate.clicked.connect(self.dlgpr_selectFileProjectTemplate)
        self.dlgpr.cb_applyQKanTemplate.clicked.connect(self.dlgpr_applyQKanTemplate)

        # Formular dlgla - Projektdatei anpassen an QKan-Standard
        self.dlgla.pb_selectProjectFile.clicked.connect(self.dlgla_selectFileProjectfile)
        self.dlgla.pb_selectQKanDB.clicked.connect(self.dlgla_selectFile_qkanDB)
        self.dlgla.cb_adaptDB.clicked.connect(self.dlgla_enableQkanDB)
        self.dlgla.pb_selectProjectTemplate.clicked.connect(self.dlgla_selectFileProjectTemplate)
        self.dlgla.button_box.helpRequested.connect(self.dlgla_helpClick)
        self.dlgla.cb_adaptForms.clicked.connect(self.dlgla_cb_adaptForms)
        self.dlgla.cb_adaptTableLookups.clicked.connect(self.dlgla_cb_adaptTableLookups)
        self.dlgla.cb_adaptKBS.clicked.connect(self.dlgla_cb_adaptKBS)
        self.dlgla.cb_applyQKanTemplate.clicked.connect(self.dlgla_applyQKanTemplate)
        self.dlgla.cb_saveProjectFile.clicked.connect(self.dlgla_enableSaveProjectFile)
        self.dlgla.cb_qkanDBUpdate.clicked.connect(self.dlgla_checkqkanDBUpdate)

        # Formular dlgop - QKan-Optionen
        self.dlgop.pb_fangradiusDefault.clicked.connect(self.dlgop_fangradiusDefault)
        self.dlgop.pb_mindestflaecheDefault.clicked.connect(self.dlgop_mindestflaecheDefault)
        self.dlgop.pb_max_loopsDefault.clicked.connect(self.dlgop_maxLoopsDefault)
        self.dlgop.pb_selectKBS.clicked.connect(self.dlgop_selectKBS)
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
        return QCoreApplication.translate('Flaechenzuordnungen', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_qgsadapt_path = ':/plugins/qkan/tools/res/icon_qgsadapt.png'
        Dummy.instance.add_action(
            icon_qgsadapt_path, 
            text=self.tr(u'Projektdatei auf bestehende QKan-Datenbank übertragen'), 
            callback=self.run_qgsadapt, 
            parent=self.iface.mainWindow())

        icon_layersadapt_path = ':/plugins/qkan/tools/res/icon_layersadapt.png'
        Dummy.instance.add_action(
            icon_layersadapt_path, 
            text=self.tr(u'Projektlayer auf QKan-Standard setzen'), 
            callback=self.run_layersadapt, 
            parent=self.iface.mainWindow())

        icon_qkanoptions_path = ':/plugins/qkan/tools/res/icon_qkanoptions.png'
        Dummy.instance.add_action(
            icon_qkanoptions_path, 
            text=self.tr(u'Allgemeine Optionen'), 
            callback=self.run_qkanoptions, 
            parent=self.iface.mainWindow())

        icon_runoffparams_path = ':/plugins/qkan/tools/res/icon_runoffparams.png'
        Dummy.instance.add_action(
            icon_runoffparams_path, 
            text=self.tr(u'Oberflächenabflussparameter eintragen'), 
            callback=self.run_runoffparams, 
            parent=self.iface.mainWindow())

    def unload(self):
        pass


    # -----------------------------------------------------------------------------------------------------
    # Allgemeine Funktionen

    # -------------------------------------------------------------------------
    # Funktion zur Zusammenstellung einer Auswahlliste für eine SQL-Abfrage

    def listselecteditems(self, listWidget):
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

        filename = QFileDialog.getSaveFileName(self.dlgpr,
                                              u"Dateinamen der zu erstellenden Projektdatei eingeben",
                                               self.default_dir,
                                               "*.qgs")
        # logger.info('Dateiname wurde erkannt zu:\n{}'.format(filename))
        
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgpr.tf_projectFile.setText(filename)


    def dlgpr_selectFile_qkanDB(self):
        """Anzubindende QKan-Datenbank festlegen"""

        filename = QFileDialog.getOpenFileName(self.dlgpr,
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

        self.dlgpr.cb_applyQKanTemplate.setChecked(False)              # automatisch deaktivieren
        self.dlgpr_applyQKanTemplate()                                 # Auswirkungen auslösen

        filename = QFileDialog.getOpenFileName(self.dlgpr,
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
        self.database_QKan, epsg = get_database_QKan(silent = True)

        if self.database_QKan:
            self.default_dir = os.path.dirname(self.database_QKan)       # bereits geladene QKan-Datenbank übernehmen
        elif 'database_QKan' in self.config:
            self.database_QKan = self.config['database_QKan']
            self.dlgpr.tf_qkanDB.setText(self.database_QKan)
            self.default_dir = os.path.dirname(self.database_QKan)
        else:
            self.database_QKan = ''
            self.default_dir = '.'
        self.dlgpr.tf_qkanDB.setText(self.database_QKan)

        # Formularfeld Vorlagedatei
        if 'projectTemplate' in self.config:
            projectTemplate = self.config['projectTemplate']
        else:
            projectTemplate = ''

        # Formularfeld Projektdatei
        if 'projectfile' in self.config:
            projectFile = self.config['projectfile']
        else:
            projectFile = ''

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen 
        if 'QKan_Standard_anwenden' in self.config:
            self.applyQKanTemplate = self.config['QKan_Standard_anwenden']
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

            self.config['projectTemplate'] = projectTemplate
            self.config['database_QKan'] = self.database_QKan
            self.config['projectfile'] = projectFile
            self.config['QKan_Standard_anwenden'] = self.applyQKanTemplate

            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            qgsadapt(projectTemplate, self.database_QKan, epsg, projectFile, 
                     self.applyQKanTemplate, u'SpatiaLite')

    # ----------------------------------------------------------------------------------------------------
    # Allgemeine QKan-Optionen bearbeiten

    # 1. Formularfunktionen

    def dlgop_selectKBS(self):
        """KBS auswählen. Setzt das KBS für die weiteren Funktionen

        :returns: void
        """
        projSelector = QgsGenericProjectionSelector()
        projSelector.exec_()
        erg = projSelector.selectedAuthId()
        if len(erg.split(u':')) == 2:
            self.dlgop.tf_epsg.setText(erg.split(u':')[1])
        else:
            self.dlgop.tf_epsg.setText(erg)

    def dlgop_fangradiusDefault(self):
        self.dlgop.tf_fangradius.setText('0.1')

    def dlgop_mindestflaecheDefault(self):
        self.dlgop.tf_mindestflaeche.setText('0.5')

    def dlgop_maxLoopsDefault(self):
        self.dlgop.tf_max_loops.setText('1000')

    def dlgop_openLogfile(self):
        """Öffnet die Log-Datei mit dem Standard-Editor für Log-Dateien oder einem gewählten Editor"""

        dnam = dt.today().strftime("%Y%m%d")
        fnam = os.path.join(tempfile.gettempdir(), 'QKan{}.log'.format(dnam))
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

        filename = QFileDialog.getOpenFileName(self.dlgop,
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
        if 'fangradius' in self.config:
            fangradius = self.config['fangradius']
        else:
            fangradius = u'0.1'
        self.dlgop.tf_fangradius.setText(str(fangradius))

        # Mindestflächengröße
        if 'mindestflaeche' in self.config:
            mindestflaeche = self.config['mindestflaeche']
        else:
            mindestflaeche = u'0.5'
        self.dlgop.tf_mindestflaeche.setText(str(mindestflaeche))

        # Maximalzahl Schleifendurchläufe
        if 'max_loops' in self.config:
            max_loops = self.config['max_loops']
        else:
            max_loops = '1000'
        self.dlgop.tf_max_loops.setText(str(max_loops))

        # Optionen zum Typ der QKan-Datenbank
        if 'datenbanktyp' in self.config:
            datenbanktyp = self.config['datenbanktyp']
        else:
            datenbanktyp = u'spatialite'

        if datenbanktyp == u'spatialite':
            self.dlgop.rb_spatialite.setChecked(True)
        # elif datenbanktyp == u'postgis':
            # self.dlgop.rb_postgis.setChecked(True)

        if 'epsg' in self.config:
            self.epsg = self.config['epsg']
        else:
            self.epsg = u'25832'
        self.dlgop.tf_epsg.setText(self.epsg)

        if 'logeditor' in self.config:
            self.logeditor = self.config['logeditor']
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
            epsg = self.dlgop.tf_epsg.text()

            self.config['fangradius'] = fangradius
            self.config['mindestflaeche'] = mindestflaeche
            self.config['max_loops'] = max_loops
            self.config['datenbanktyp'] = datenbanktyp
            self.config['epsg'] = epsg
            self.config['logeditor'] = self.logeditor

            with open(self.configfil, 'w') as fileconfig:
                # logger.debug(u"Config-Dictionary: {}".format(self.config))
                fileconfig.write(json.dumps(self.config))


    # ----------------------------------------------------------------------------------------------------
    # Oberflächenabflussparameter in QKan-Tabellen eintragen, ggfs. nur für ausgewählte Teilgebiete

    # 1. Formularfunktionen

    def dlgro_selectFile_qkanDB(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        filename = QFileDialog.getOpenFileName(self.dlgro, u"QKan-Datenbank auswählen",
                                               self.default_dir, "*.sqlite")
        # if os.path.dirname(filename) != '':
        # os.chdir(os.path.dirname(filename))
        self.dlgro.tf_QKanDB.setText(filename)

    def dlgro_helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(self.plugin_dir, '../doc/sphinx/build/html/Qkan_Formulare.html#berechnung-von-oberflachenabflussparametern')
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
                self.dlgro.lw_teilgebiete.setItemSelected(item, False)

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
                self.dlgro.lw_abflussparameter.setItemSelected(item, False)

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
        auswahl = sqlconditions('WHERE', ('teilgebiet', 'abflussparameter'), (liste_teilgebiete, liste_abflussparameter))

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
            iface.messageBar().pushMessage(u"Bedienerfehler: ",
                                           u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                                           level=QgsMessageBar.CRITICAL)
            return False

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_QKan = ''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            logger.error(u"tools.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False
        self.dlgro.tf_QKanDB.setText(database_QKan)

        if 'manningrauheit_bef' in self.config:
            manningrauheit_bef = self.config['manningrauheit_bef']
        else:
            manningrauheit_bef = 0.02
            self.config['manningrauheit_bef'] = manningrauheit_bef
        if 'manningrauheit_dur' in self.config:
            manningrauheit_dur = self.config['manningrauheit_dur']
        else:
            manningrauheit_dur = 0.10
            self.config['manningrauheit_dur'] = manningrauheit_dur

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            logger.error(u"Fehler in tools.application.runoffparams:\n",
                          u'QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!'.format(database_QKan))
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
        if 'liste_teilgebiete' in self.config:
            liste_teilgebiete = self.config['liste_teilgebiete']

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
        if 'liste_abflussparameter' in self.config:
            liste_abflussparameter = self.config['liste_abflussparameter']

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
        if 'runoffparamsfunctions' in self.config:
            runoffparamsfunctions = self.config['runoffparamsfunctions']
        else:
            runoffparamsfunctions = {
                'itwh': [
                    '0.8693*log(area(geom))+ 5.6317', 
                    'pow(18.904*pow(neigkl,0.686)*area(geom), 0.2535*pow(neigkl,0.244))'], 
                'dyna': [
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(rauheit_bef=manningrauheit_bef), 
                    'pow(2*{rauheit_dur} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(rauheit_dur=manningrauheit_dur)], 
                'Maniak': [
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(rauheit_bef=manningrauheit_bef), 
                    'pow(2*{rauheit_dur} * (abstand + fliesslaenge) / SQRT(neigung), 0.467)'.format(rauheit_dur=manningrauheit_dur),
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * abstand / SQRT(neigung), 0.467)'.format(rauheit_bef=manningrauheit_bef), 
                    'pow(2*{rauheit_dur} * abstand / SQRT(neigung), 0.467)'.format(rauheit_dur=manningrauheit_dur),
                    '0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*{rauheit_bef} * fliesslaenge / SQRT(neigung), 0.467)'.format(rauheit_bef=manningrauheit_bef), 
                    'pow(2*{rauheit_dur} * fliesslaenge / SQRT(neigung), 0.467)'.format(rauheit_dur=manningrauheit_dur)]
                }
            self.config['runoffparamsfunctions'] = runoffparamsfunctions
        
        # Optionen zur Berechnung des Oberflächenabflusses
        if 'runoffparamstype_choice' in self.config:
            runoffparamstype_choice = self.config['runoffparamstype_choice']
        else:
            runoffparamstype_choice = u'Maniak'

        if runoffparamstype_choice == u'itwh':
            self.dlgro.rb_itwh.setChecked(True)
        elif runoffparamstype_choice == u'dyna':
            self.dlgro.rb_dyna.setChecked(True)
        elif runoffparamstype_choice == u'Maniak':
            self.dlgro.rb_maniak.setChecked(True)

        if 'runoffmodelltype_choice' in self.config:
            runoffmodelltype_choice = self.config['runoffmodelltype_choice']
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
        if 'datenbanktyp' in self.config:
            datenbanktyp = self.config['datenbanktyp']
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
                              u"Fehlerhafte Option: \nrunoffparamstype_choice = {}".format(repr(runoffparamstype_choice)))
            if self.dlgro.rb_kaskade.isChecked():
                runoffmodelltype_choice = u'Speicherkaskade'
            elif self.dlgro.rb_fliesszeiten.isChecked():
                runoffmodelltype_choice = u'Fliesszeiten'
            elif self.dlgro.rb_schwerpunktlaufzeit.isChecked():
                runoffmodelltype_choice = u'Schwerpunktlaufzeit'
            else:
                fehlermeldung(u"tools.runoffparams.run_runoffparams", 
                              u"Fehlerhafte Option: \nrunoffmodelltype_choice = {}".format(repr(runoffmodelltype_choice)))

            # Konfigurationsdaten schreiben
            self.config['database_QKan'] = database_QKan
            self.config['liste_teilgebiete'] = liste_teilgebiete
            self.config['liste_abflussparameter'] = liste_abflussparameter
            self.config['runoffparamstype_choice'] = runoffparamstype_choice
            self.config['runoffmodelltype_choice'] = runoffmodelltype_choice

            with open(self.configfil, 'w') as fileconfig:
                # logger.debug(u"Config-Dictionary: {}".format(self.config))
                fileconfig.write(json.dumps(self.config))

            setRunoffparams(self.dbQK, runoffparamstype_choice, runoffmodelltype_choice, runoffparamsfunctions, 
                liste_teilgebiete, liste_abflussparameter, datenbanktyp)


    # -----------------------------------------------------------------------------------------------------
    # Anpassen/Ergänzen von QKan-Layern

    # 1. Formularfunktionen

    def dlgla_helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(self.plugin_dir, '../doc/sphinx/build/html/Qkan_Formulare.html#projektlayer-auf-qkan-standard-setzen')
        webbrowser.open_new_tab(helpfile)

    def dlgla_selectFile_qkanDB(self):
        """Anzubindende QKan-Datenbank festlegen"""

        self.dlgla.cb_adaptDB.setChecked(True)                       # automatisch aktivieren
        filename = QFileDialog.getOpenFileName(self.dlgla,
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

        self.dlgla_cb_adaptKBS()            # Korrigiert ggfs. cb_adaptKBS

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
            self.dlgla.cb_adaptKBS.setChecked(True)
            meldung("", u"Bei einer Anpassung der Layeranbindungen muss auch die Anpassung des KBS aktiviert sein!")

    def dlgla_applyQKanTemplate(self):
        """Aktiviert oder deaktiviert das Textfeld für die Template-Projektdatei"""

        checked = self.dlgla.cb_applyQKanTemplate.isChecked()
        self.dlgla.tf_projectTemplate.setEnabled(not checked)

    def dlgla_selectFileProjectTemplate(self):
        """Vorlage-Projektdatei auswählen"""

        self.dlgla.cb_applyQKanTemplate.setChecked(False)              # automatisch deaktivieren
        self.dlgla_applyQKanTemplate()                                 # Auswirkungen auslösen

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

        filename = QFileDialog.getOpenFileName(self.dlgla,
                                               "Projektdatei als Vorlage auswählen",
                                               self.templateDir,
                                               "*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgla.tf_projectTemplate.setText(filename)


    def dlgla_enableSaveProjectFile(self):
        """Aktiviert oder deaktiviert das Textfeld für die zu Schreibende Projektdatei
            abhängig vom angeklickten Checkbutton cb_saveProjectFile
        """
        checked = self.dlgla.cb_saveProjectFile.isChecked()

        self.dlgla.tf_projectFile.setEnabled(checked)
        # self.dlgla.pb_selectProjectFile.setEnabled(checked)
        self.dlgla.lb_projectFile.setEnabled(checked)

    def dlgla_selectFileProjectfile(self):
        """Zu erstellende Projektdatei festlegen"""

        self.dlgla.cb_saveProjectFile.setChecked(True)                 # automatisch aktivieren
        self.dlgla_enableSaveProjectFile()
        filename = QFileDialog.getSaveFileName(self.dlgla,
                                               u"Dateinamen der zu erstellenden Projektdatei eingeben",
                                               self.default_dir,
                                               "*.qgs")
        # logger.info('Dateiname wurde erkannt zu:\n{}'.format(filename))
        
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlgla.tf_projectFile.setText(filename)


    def dlgla_checkqkanDBUpdate(self):
        """Setzt cb_adaptTableLookups, wenn cb_qkanDBUpdate gesetzt
        """

        if self.dlgla.cb_qkanDBUpdate.isChecked():
            if not self.dlgla.cb_adaptTableLookups.isChecked():
                meldung("", u"Bei einem Update der QKan-Datenbank muss auch die Anpassung von Wertbeziehungungen und Formularanbindungen aktiviert sein!")

            self.dlgla.cb_adaptTableLookups.setChecked(True)
            # self.dlgla_cb_adaptTableLookups()


    # -----------------------------------------------------------------------------------------------------
    # 2. Aufruf des Formulars

    def run_layersadapt(self):
        '''Anpassen oder Ergänzen von Layern entsprechend der QKan-Datenstrukturen'''

        # QKan-Projekt prüfen
        layers = iface.legendInterface().layers()
        
        if len(layers) == 0:
            fehlermeldung(u'Benutzerfehler: ', u'Es ist kein Projekt geladen.')
            return

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.database_QKan, epsg = get_database_QKan(silent = True)

        if self.database_QKan:
            self.default_dir = os.path.dirname(self.database_QKan)       # bereits geladene QKan-Datenbank übernehmen
        elif 'database_QKan' in self.config:
            self.database_QKan = self.config['database_QKan']
            self.dlgla.tf_qkanDB.setText(self.database_QKan)
            self.default_dir = os.path.dirname(self.database_QKan)
        else:
            self.database_QKan = ''
            self.default_dir = '.'
        self.dlgla.tf_qkanDB.setText(self.database_QKan)

        # Formularfeld Projektdatei
        if 'projectfile' in self.config:
            projectFile = self.config['projectfile']
        else:
            projectFile = ''

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen 
        if 'QKan_Standard_anwenden' in self.config:
            self.applyQKanTemplate = self.config['QKan_Standard_anwenden']
        else:
            self.applyQKanTemplate = True
        self.dlgla.cb_applyQKanTemplate.setChecked(self.applyQKanTemplate)

        # GGfs. Standardvorlage schon eintragen
        if self.applyQKanTemplate:
            self.projectTemplate = os.path.join(self.templateDir,'Projekt.qgs')
            self.dlgla.tf_projectTemplate.setText(self.projectTemplate)

        # Groupbox "Layer anpassen" ---------------------------------------------------------------------------

        # Checkbox "Datenbankanbindung"
        if 'anpassen_Datenbankanbindung' in self.config:
            self.anpassen_Datenbankanbindung = self.config['anpassen_Datenbankanbindung']
        else:
            self.anpassen_Datenbankanbindung = True
        self.dlgla.cb_adaptDB.setChecked(self.anpassen_Datenbankanbindung)

        # Checkbox "Projektionssystem anpassen"
        if 'anpassen_Projektionssystem' in self.config:
            self.anpassen_Projektionssystem = self.config['anpassen_Projektionssystem']
        else:
            self.anpassen_Projektionssystem = True
        self.dlgla.cb_adaptKBS.setChecked(self.anpassen_Projektionssystem)

        # Checkbox "Wertbeziehungungen in Tabellen"
        if 'anpassen_Wertebeziehungen_in_Tabellen' in self.config:
            self.anpassen_Wertebeziehungen_in_Tabellen = self.config['anpassen_Wertebeziehungen_in_Tabellen']
        else:
            self.anpassen_Wertebeziehungen_in_Tabellen = True
        self.dlgla.cb_adaptTableLookups.setChecked(self.anpassen_Wertebeziehungen_in_Tabellen)

        # Checkbox "Formularanbindungen"
        if 'anpassen_Formulare' in self.config:
            self.anpassen_Formulare = self.config['anpassen_Formulare']
        else:
            self.anpassen_Formulare = True
        self.dlgla.cb_adaptForms.setChecked(self.anpassen_Formulare)

        # Groupbox "QKan-Layer" ---------------------------------------------------------------------------

        # Optionen zur Berücksichtigung der vorhandenen Tabellen
        if 'anpassen_auswahl' in self.config:
            anpassen_auswahl = self.config['anpassen_auswahl']
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
        if 'fehlende_layer_ergaenzen' in self.config:
            self.fehlende_layer_ergaenzen = self.config['fehlende_layer_ergaenzen']
        else:
            self.fehlende_layer_ergaenzen = True
        self.dlgla.cb_completeLayers.setChecked(self.fehlende_layer_ergaenzen)
        
        # Weitere Formularfelder ---------------------------------------------------------------------------

        # Checkbox: Knotentype per Abfrage ermitteln und in "schaechte.knotentyp" eintragen
        if 'aktualisieren_Schachttypen' in self.config:
            aktualisieren_Schachttypen = self.config['aktualisieren_Schachttypen']
        else:
            aktualisieren_Schachttypen = True
        self.dlgla.cb_updateNodetype.setChecked(aktualisieren_Schachttypen)

        # Checkbox: Nach Aktualisierung auf alle Layer zoomen
        if 'zoom_alles' in self.config:
            zoom_alles = self.config['zoom_alles']
        else:
            zoom_alles = True
        self.dlgla.cb_zoomAll.setChecked(zoom_alles)

        # Checkbox: QKan-Standard anwenden
        if 'QKan_Standard_anwenden' in self.config:
            self.applyQKanTemplate = self.config['QKan_Standard_anwenden']
        else:
            self.applyQKanTemplate = True
        self.dlgla.cb_applyQKanTemplate.setChecked(self.applyQKanTemplate)

        # Checkbox: Erzeugte Projektdatei speichern
        if 'Projektdatei_speichern' in self.config:
            self.saveProjectFile = self.config['Projektdatei_speichern']
        else:
            self.saveProjectFile = True
        self.dlgla.cb_saveProjectFile.setChecked(self.saveProjectFile)

        # Checkbox: QKan-Datenbank aktualisieren
        if 'qkanDBUpdate' in self.config:
            self.qkanDBUpdate = self.config['qkanDBUpdate']
        else:
            self.qkanDBUpdate = True
        self.dlgla.cb_qkanDBUpdate.setChecked(self.qkanDBUpdate)

        # Status initialisieren
        self.dlgla_enableQkanDB()
        self.dlgla_applyQKanTemplate()
        self.dlgla_enableSaveProjectFile()
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
            self.saveProjectFile = self.dlgla.cb_saveProjectFile.isChecked()
            projectFile = self.dlgla.tf_projectFile.text()

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

            self.config['database_QKan'] = self.database_QKan
            if projectFile != '':
                self.config['projectfile'] = projectFile
            self.config['anpassen_Datenbankanbindung'] = self.anpassen_Datenbankanbindung
            self.config['anpassen_Wertebeziehungen_in_Tabellen'] = self.anpassen_Wertebeziehungen_in_Tabellen
            self.config['anpassen_Formulare'] = self.anpassen_Formulare
            self.config['anpassen_Projektionssystem'] = self.anpassen_Projektionssystem
            self.config['fehlende_layer_ergaenzen'] = fehlende_layer_ergaenzen
            self.config['anpassen_auswahl'] = anpassen_auswahl
            self.config['qkanDBUpdate'] = self.qkanDBUpdate
            self.config['aktualisieren_Schachttypen'] = aktualisieren_Schachttypen
            self.config['zoom_alles'] = zoom_alles
            self.config['QKan_Standard_anwenden'] = self.applyQKanTemplate
            self.config['Projektdatei_speichern'] = self.saveProjectFile

            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            logger.debug(u"""layersadapt(database_QKan='{0:}', 
                                projectFile='{1:}', 
                                projectTemplate='{2:}', 
                                qkanDBUpdate={3:}, 
                                anpassen_Datenbankanbindung={4:}, 
                                anpassen_Wertebeziehungen_in_Tabellen={5:}, 
                                anpassen_Formulare={6:}, 
                                anpassen_Projektionssystem={7:}, 
                                aktualisieren_Schachttypen={8:}, 
                                zoom_alles={9:}, 
                                fehlende_layer_ergaenzen={10:}, 
                                anpassen_auswahl = '{11}', 
                                dbtyp = '{12}')""".format( \
                                self.database_QKan, 
                                projectFile, 
                                self.projectTemplate, 
                                self.qkanDBUpdate, 
                                self.anpassen_Datenbankanbindung, 
                                self.anpassen_Wertebeziehungen_in_Tabellen, 
                                self.anpassen_Formulare, 
                                self.anpassen_Projektionssystem, 
                                aktualisieren_Schachttypen, 
                                zoom_alles, 
                                fehlende_layer_ergaenzen, 
                                anpassen_auswahl, 
                                u'SpatiaLite'))
            layersadapt(self.database_QKan, projectFile, self.projectTemplate, self.qkanDBUpdate, 
                        self.anpassen_Datenbankanbindung, self.anpassen_Wertebeziehungen_in_Tabellen, 
                        self.anpassen_Formulare, 
                        self.anpassen_Projektionssystem, aktualisieren_Schachttypen, zoom_alles, 
                        fehlende_layer_ergaenzen, anpassen_auswahl, u'SpatiaLite')

