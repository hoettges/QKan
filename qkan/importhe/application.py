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
import codecs
import json
import logging
import os
import site

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QFileDialog  # (jh, 20.09.2016)
from qgis.core import QgsProject
from qgis.gui import QgsGenericProjectionSelector

# Initialize Qt resources from file resources.py
# Import the code for the dialog
from application_dialog import ImportFromHEDialog
# from qgis.utils import iface
from import_from_he import importKanaldaten
# Anbindung an Logging-System (Initialisierung in __init__)
from qkan import Dummy
# noinspection PyUnresolvedReferences
import resources

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
        self.dlg = ImportFromHEDialog()

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
            with codecs.open(self.configfil, 'r', 'utf-8') as fileconfig:
                self.config = json.loads(fileconfig.read().replace('\\', '/'))
        else:
            self.config = {'epsg': '25832'}  # Projektionssystem
            self.config['database_QKan'] = ''
            self.config['database_HE'] = ''
            self.config['projectfile'] = ''
            with codecs.open(self.configfil, 'w', 'utf-8') as fileconfig:
                fileconfig.write(json.dumps(self.config))

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        if 'database_QKan' in self.config:
            database_QKan = self.config['database_QKan']
        else:
            database_QKan = ''
        self.dlg.tf_qkanDB.setText(database_QKan)
        self.dlg.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)

        if 'database_HE' in self.config:
            database_HE = self.config['database_HE']
        else:
            database_HE = ''
        self.dlg.tf_heDB.setText(database_HE)
        self.dlg.pb_selectHeDB.clicked.connect(self.selectFile_HeDB)

        if 'epsg' in self.config:
            self.epsg = self.config['epsg']
        else:
            self.epsg = '25832'
        self.dlg.tf_epsg.setText(self.epsg)
        self.dlg.pb_selectKBS.clicked.connect(self.selectKBS)

        if 'projectfile' in self.config:
            projectfile = self.config['projectfile']
        else:
            projectfile = ''
        self.dlg.tf_projectFile.setText(projectfile)
        self.dlg.pb_selectProjectFile.clicked.connect(self.selectProjectFile)

        if 'check_copy_forms' in self.config:
            check_copy_forms = self.config['check_copy_forms']
        else:
            check_copy_forms = True
        self.dlg.cb_copy_forms.setChecked(check_copy_forms)

        if 'check_inittab' in self.config:
            check_inittab = self.config['check_inittab']
        else:
            check_inittab = True
        self.dlg.cb_import_tabinit.setChecked(check_inittab)

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
        return QCoreApplication.translate('ImportFromHE', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/qkan/importhe/icon.png'
        Dummy.instance.add_action(
            icon_path,
            text=self.tr(u'Import aus Hystem-Extran'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        pass

    # Anfang Eigene Funktionen -------------------------------------------------
    # (jh, 09.10.2016)


    def selectFile_HeDB(self):
        """Datenbankverbindung zur HE-Datenbank (Firebird) auswaehlen und gegebenenfalls die Zieldatenbank
           erstellen, aber noch nicht verbinden."""

        filename = QFileDialog.getOpenFileName(self.dlg,
                                               u"Dateinamen der zu lesenden HE-Datenbank eingeben",
                                               self.default_dir,
                                               u"*.idbf")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB.setText(filename)

    def selectFile_qkanDB(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiaLite) auswaehlen, aber noch nicht verbinden.
           Falls die Datenbank noch nicht existiert, wird sie nach Betaetigung von [OK] erstellt. """

        filename = QFileDialog.getSaveFileName(self.dlg,
                                               u"Dateinamen der zu erstellenden SpatiaLite-Datenbank eingeben",
                                               self.default_dir,
                                               u"*.sqlite")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg.tf_qkanDB.setText(filename)

    def selectProjectFile(self):
        """Zu erzeugende Projektdatei festlegen, falls ausgewählt."""

        filename = QFileDialog.getSaveFileName(self.dlg,
                                               u"Dateinamen der zu erstellenden Projektdatei eingeben",
                                               self.default_dir,
                                               u"*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
        self.dlg.tf_projectFile.setText(filename)

    def selectKBS(self):
        """KBS auswählen. Setzt das KBS für die weiteren Funktionen

        :returns: void
        """
        projSelector = QgsGenericProjectionSelector()
        projSelector.exec_()
        erg = projSelector.selectedAuthId()
        if len(erg.split(u':')) == 2:
            self.dlg.tf_epsg.setText(erg.split(u':')[1])
        else:
            self.dlg.tf_epsg.setText(erg)

            # Ende Eigene Funktionen ---------------------------------------------------

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # (jh, 09.10.2016)

            # Namen der Datenbanken uebernehmen

            database_HE = self.dlg.tf_heDB.text()
            database_QKan = self.dlg.tf_qkanDB.text()
            projectfile = self.dlg.tf_projectFile.text()
            self.epsg = self.dlg.tf_epsg.text()
            check_copy_forms = self.dlg.cb_copy_forms.isChecked()
            check_inittab = self.dlg.cb_import_tabinit.isChecked()

            # Konfigurationsdaten schreiben

            self.config['epsg'] = self.epsg
            self.config['database_QKan'] = database_QKan
            self.config['database_HE'] = database_HE
            self.config['projectfile'] = projectfile
            self.config['check_copy_forms'] = check_copy_forms
            self.config['check_inittab'] = check_inittab

            with codecs.open(self.configfil, 'w', 'utf-8') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            # Start der Verarbeitung

            importKanaldaten(database_HE, database_QKan, projectfile, self.epsg, check_copy_forms, check_inittab)
