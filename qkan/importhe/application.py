#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

  QGis-Plugin
  ===========

  Definition der Formularklasse

  | Dateiname            : application.py
  | Date                 : October 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.                                  

"""
import json
import logging
import os
import site

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QFileDialog  # (jh, 20.09.2016)
from qgis.core import QgsProject
from qgis.gui import QgsGenericProjectionSelector
from qkan.database.qgis_utils import get_database_QKan

# Initialize Qt resources from file resources.py
# Import the code for the dialog
import resources
from application_dialog import ImportFromHEDialog, ResultsFromHEDialog
from import_from_he import importKanaldaten
from results_from_he import importResults
from qkan import Dummy
# noinspection PyUnresolvedReferences

LOGGER = logging.getLogger(u'QKan')


class ImportFromHE:
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
            'ImportFromHE_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg_he = ImportFromHEDialog()
        self.dlg_lz = ResultsFromHEDialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 09.10.2016)

        # --------------------------------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(), 'qkan')

        if not os.path.isdir(wordir):
            os.makedirs(wordir)
        # --------------------------------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        self.configfil = os.path.join(wordir, 'qkan.json')
        if os.path.exists(self.configfil):
            with open(self.configfil, 'r') as fileconfig:
                self.config = json.loads(fileconfig.read())

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        # Formularereignisse run_import()
        self.dlg_he.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDBHE)
        self.dlg_he.pb_selectHeDB.clicked.connect(self.selectFile_HeDB)
        self.dlg_he.pb_selectKBS.clicked.connect(self.selectKBS)
        self.dlg_he.pb_selectProjectFile.clicked.connect(self.selectProjectFile)

        # Formularereignisse run_results()

        self.dlg_lz.pb_selectqmlfile.clicked.connect(self.selectqmlfileResults)

        # Klick auf eine Option zum Layerstil aktiviert/deaktiviert das Textfeld und die Schaltfläche
        self.dlg_lz.pb_selectHeDB.clicked.connect(self.selectFile_HeDB)
        self.dlg_lz.rb_userqml.clicked.connect(self.enable_tf_qmlfile)
        self.dlg_lz.rb_uebh.clicked.connect(self.disable_tf_qmlfile)
        self.dlg_lz.rb_uebvol.clicked.connect(self.disable_tf_qmlfile)
        self.dlg_lz.rb_none.clicked.connect(self.disable_tf_qmlfile)

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
        return QCoreApplication.translate('ImportFromHE', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_import_path = ':/plugins/qkan/importhe/res/icon_import.png'
        Dummy.instance.add_action(
            icon_import_path,
            text=self.tr(u'Import aus Hystem-Extran'),
            callback=self.run_import,
            parent=self.iface.mainWindow())

        icon_results_path = ':/plugins/qkan/importhe/res/icon_results.png'
        Dummy.instance.add_action(
            icon_results_path,
            text=self.tr(u'Ergebnisse aus Hystem-Extran einlesen'),
            callback=self.run_results,
            parent=self.iface.mainWindow())

    def unload(self):
        pass


    # Formularfunktionen zum HE-Import -------------------------------------------------

    def selectFile_HeDB(self):
        """Datenbankverbindung zur HE-Datenbank (Firebird) auswaehlen"""

        filename = QFileDialog.getOpenFileName(self.dlg_he,
                                               u"Dateinamen der zu lesenden HE-Datenbank auswählen",
                                               self.default_dir,
                                               u"*.idbf")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg_he.tf_heDB.setText(filename)

    def selectFile_qkanDBHE(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiaLite) auswaehlen"""

        filename = QFileDialog.getSaveFileName(self.dlg_he,
                                               u"Dateinamen der zu erstellenden SpatiaLite-Datenbank eingeben",
                                               self.default_dir,
                                               u"*.sqlite")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg_he.tf_qkanDB.setText(filename)

    def selectProjectFile(self):
        """Zu erzeugende Projektdatei festlegen, falls ausgewählt."""

        filename = QFileDialog.getSaveFileName(self.dlg_he,
                                               u"Dateinamen der zu erstellenden Projektdatei eingeben",
                                               self.default_dir,
                                               u"*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg_he.tf_projectFile.setText(filename)

    def selectKBS(self):
        """KBS auswählen. Setzt das KBS für die weiteren Funktionen

        :returns: void
        """
        projSelector = QgsGenericProjectionSelector()
        projSelector.exec_()
        erg = projSelector.selectedAuthId()
        if len(erg.split(u':')) == 2:
            self.dlg_he.tf_epsg.setText(erg.split(u':')[1])
        else:
            self.dlg_he.tf_epsg.setText(erg)

    # Formularfunktionen zum Lesen der LZ-Ergebnisse ----------------------------------------------

    def selectFile_HELZ(self):
        """Datenbankverbindung zur HE-Datenbank (Firebird) auswaehlen"""

        filename = QFileDialog.getOpenFileName(self.dlg_lz,
                                               u"Dateinamen der HE-Datenbank mit den LZ-Ergebnissen auswählen",
                                               self.default_dir,
                                               u"*.idbf")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg_lz.tf_heDB.setText(filename)

        # Ende Eigene Funktionen ---------------------------------------------------

    def run_import(self):
        """Öffnen des Formulars zum Import aus HE"""

        if 'database_QKan' in self.config:
            database_QKan = self.config['database_QKan']
        else:
            database_QKan = ''
        self.dlg_he.tf_qkanDB.setText(database_QKan)

        if 'database_HE' in self.config:
            database_HE = self.config['database_HE']
        else:
            database_HE = ''
        self.dlg_he.tf_heDB.setText(database_HE)

        if 'epsg' in self.config:
            self.epsg = self.config['epsg']
        else:
            self.epsg = u'25832'
        self.dlg_he.tf_epsg.setText(self.epsg)

        if 'projectfile' in self.config:
            projectfile = self.config['projectfile']
        else:
            projectfile = ''
        self.dlg_he.tf_projectFile.setText(projectfile)

        if 'check_copy_forms' in self.config:
            check_copy_forms = self.config['check_copy_forms']
        else:
            check_copy_forms = True
        self.dlg_he.cb_copy_forms.setChecked(check_copy_forms)

        if 'check_inittab' in self.config:
            check_inittab = self.config['check_inittab']
        else:
            check_inittab = True
        self.dlg_he.cb_import_tabinit.setChecked(check_inittab)

        # Ende Eigene Funktionen ---------------------------------------------------


        # show the dialog
        self.dlg_he.show()
        # Run the dialog event loop
        result = self.dlg_he.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # (jh, 09.10.2016)

            # Namen der Datenbanken uebernehmen

            database_HE = self.dlg_he.tf_heDB.text()
            database_QKan = self.dlg_he.tf_qkanDB.text()
            projectfile = self.dlg_he.tf_projectFile.text()
            self.epsg = self.dlg_he.tf_epsg.text()
            check_copy_forms = self.dlg_he.cb_copy_forms.isChecked()
            check_inittab = self.dlg_he.cb_import_tabinit.isChecked()

            # Konfigurationsdaten schreiben

            self.config['epsg'] = self.epsg
            self.config['database_QKan'] = database_QKan
            self.config['database_HE'] = database_HE
            self.config['projectfile'] = projectfile
            self.config['check_copy_forms'] = check_copy_forms
            self.config['check_inittab'] = check_inittab

            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            # Start der Verarbeitung

            importKanaldaten(database_HE, database_QKan, projectfile, self.epsg, check_copy_forms, check_inittab)

    # Formularfunktionen -------------------------------------------------------

    def enable_tf_qmlfile(self):
        '''aktiviert das Textfeld für die qml-Stildatei'''
        self.dlg_lz.tf_qmlfile.setEnabled(True)
        self.dlg_lz.pb_selectqmlfile.setEnabled(True)

    def disable_tf_qmlfile(self):
        '''deaktiviert das Textfeld für die qml-Stildatei'''
        self.dlg_lz.tf_qmlfile.setEnabled(False)
        self.dlg_lz.pb_selectqmlfile.setEnabled(False)

    def selectqmlfileResults(self):
        """qml-Stildatei auswählen"""

        filename = QFileDialog.getOpenFileName(self.dlg_lz,
                                               u"Dateinamen der einzulesenen Stildatei auswählen",
                                               self.default_dir,
                                               u"*.qml")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg_lz.tf_qmlfile.setText(filename)

    # Ende Formularfunktionen --------------------------------------------------

    def run_results(self):
        """Öffnen des Formulars zum Einlesen der Simulationsergebnisse aus HE"""

        database_QKan, epsg = get_database_QKan()

        # Auswahl der HE-Ergebnisdatenbank zum Laden
        if 'database_ErgHE' in self.config:
            database_ErgHE = self.config['database_ErgHE']
        else:
            database_ErgHE = ''
        self.dlg_lz.tf_heDB.setText(database_ErgHE)

        # Option für Stildatei
        if 'qml_choice' in self.config:
            qml_choice = self.config['qml_choice']
        else:
            qml_choice = u'uebh'

        # Standard: User-qml-File ist deaktiviert
        self.disable_tf_qmlfile()

        if qml_choice == u'uebh':
            self.dlg_lz.rb_uebh.setChecked(True)
        elif qml_choice == u'uebvol':
            self.dlg_lz.rb_uebvol.setChecked(True)
        elif qml_choice == u'userqml':
            self.dlg_lz.rb_userqml.setChecked(True)
            # User-qml-File ist aktivieren
            self.enable_tf_qmlfile()
        elif qml_choice == u'none':
            self.dlg_lz.rb_none.setChecked(True)
        else:
            fehlermeldung(u"Fehler im Programmcode (1)", u"Nicht definierte Option")
            return False

        # Individuelle Stildatei
        if 'qmlfileResults' in self.config:
            qmlfileResults = self.config['qmlfileResults']
        else:
            qmlfileResults = ''
        self.dlg_lz.tf_qmlfile.setText(qmlfileResults)
        
        # show the dialog
        self.dlg_lz.show()
        # Run the dialog event loop
        result = self.dlg_lz.exec_()
        # See if OK was pressed
        if result:
            
            # Daten aus Formular übernehmen

            database_ErgHE = self.dlg_lz.tf_heDB.text()
            qmlfileResults =  self.dlg_lz.tf_qmlfile.text()

            if self.dlg_lz.rb_uebh.isChecked():
                qml_choice = u'uebh'
            elif self.dlg_lz.rb_uebvol.isChecked():
                qml_choice = u'uebvol'
            elif self.dlg_lz.rb_userqml.isChecked():
                qml_choice = u'userqml'
            elif self.dlg_lz.rb_none.isChecked():
                qml_choice = u'none'
            else:
                fehlermeldung(u"Fehler im Programmcode (2)", u"Nicht definierte Option")
                return False
            # Konfigurationsdaten schreiben

            self.config['database_QKan'] = database_QKan
            self.config['database_ErgHE'] = database_ErgHE
            self.config['qmlfileResults'] = qmlfileResults
            self.config['qml_choice'] = qml_choice

            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            # Start der Verarbeitung

            importResults(database_ErgHE, database_QKan, qml_choice, qmlfileResults, epsg)
