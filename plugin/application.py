#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

  QGis-Plugin
  ===========

  Definition der Formularklasse

  | Dateiname            : application.py
  | Date                 : Februar 2017
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.                                  

"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog         # jh, 07.04.2017
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from application_dialog import ExportToHEDialog
import site, os.path

# Ergaenzt (jh, 08.02.2017) -------------------------------------------------
import json
import logging

# from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.core import QgsProject
from k_qkhe import exportKanaldaten
import codecs

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger('QKan')

class ExportToHE:
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
            'ExportToHE_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ExportToHEDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Export to HE')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ExportToHE')
        self.toolbar.setObjectName(u'ExportToHE')

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 08.02.2017)

        logger.info('\n\nQKan_ExportHE initialisiert...')

        # --------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(),'qkan')

        if not os.path.isdir(wordir):
            os.makedirs(wordir)
        # --------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        self.configfil = os.path.join(wordir, 'qkan.json')
        if os.path.exists(self.configfil):
            with codecs.open(self.configfil,'r','utf-8') as fileconfig:
                self.config = json.loads(fileconfig.read().replace('\\','/'))
        else:
            self.config['database_HE'] = ''
            # Vorlagedatenbank nur für den Fall, dass der Anwender keine eigene Vorlage erstellen will
            self.config['dbtemplate_HE'] = os.path.join(os.path.dirname(__file__), "templates","itwh.idbf")
            self.config['database_QKan'] = ''
            with codecs.open(self.configfil,'w','utf-8') as fileconfig:
                fileconfig.write(json.dumps(self.config))

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        if 'database_QKan' in self.config:
            database_QKan = self.config['database_QKan']
        else:
            database_QKan = ''
        self.dlg.tf_QKanDB.setText(database_QKan)
        self.dlg.pb_selectQKanDB.clicked.connect(self.selectFile_QKanDB)

        if 'database_HE' in self.config:
            database_HE = self.config['database_HE']
        else:
            database_HE = ''
        self.dlg.tf_heDB_dest.setText(database_HE)
        self.dlg.pb_selectHeDB_dest.clicked.connect(self.selectFile_HeDB_dest)

        if 'dbtemplate_HE' in self.config:
            dbtemplate_HE = self.config['dbtemplate_HE']
        else:
            dbtemplate_HE = ''
        self.dlg.tf_heDB_template.setText(dbtemplate_HE)
        self.dlg.pb_selectHeDB_template.clicked.connect(self.selectFile_HeDB_template)

        if 'auswahl_teilgebiete' in self.config:
            auswahl_teilgebiete = self.config['auswahl_teilgebiete']
        else:
            auswahl_teilgebiete = ''
        self.dlg.tf_auswahlTeilgebiete.setText(auswahl_teilgebiete)

        if 'check_tabinit' in self.config:
            check_tabinit = (self.config['check_tabinit'] == u'True')
        else:
            check_tabinit = True
        self.dlg.cb_tabinit.setChecked(check_tabinit)

        # if check_tabinit:
        #     self.dlg.cb_tabinit.setChecked(QFileDialog.Qt.Checked)
        # else:
        #     self.dlg.cb_tabinit.setChecked(QFileDialog.Qt.Unchecked)

        if 'check_difftezg' in self.config:
            check_difftezg = (self.config['check_difftezg'] == u'True')
        else:
            check_difftezg = True
        self.dlg.cb_difftezg.setChecked(check_difftezg)

        # if check_difftezg:
        #     self.dlg.cb_difftezg.setChecked(QFileDialog.Qt.Checked)
        # else:
        #     self.dlg.cb_difftezg.setChecked(QFileDialog.Qt.Unchecked)

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
        return QCoreApplication.translate('ExportToHE', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/QKan_ExportHE/icon_qk2he.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Export to Hystem-Extran'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Export to HE'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # Anfang Eigene Funktionen -------------------------------------------------
    # (jh, 08.02.2017)


    def selectFile_HeDB_dest(self, default_dir):
        """Datenbankverbindung zur HE-Datenbank (Firebird) auswaehlen und gegebenenfalls die Zieldatenbank
           erstellen, aber noch nicht verbinden."""

        filename = QFileDialog.getSaveFileName(self.dlg, "Dateinamen der Ziel-HE-Datenbank eingeben",
                                               self.default_dir,"*.idbf")
        # if os.path.dirname(filename) != '':
            # os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB_dest.setText(filename)


    def selectFile_HeDB_template(self):
        """Vorlage-HE-Datenbank (Firebird) auswaehlen."""

        filename = QFileDialog.getOpenFileName(self.dlg, "Dateinamen der Vorlage-HE-Datenbank eingeben",
                                               self.default_dir,"*.idbf")
        # if os.path.dirname(filename) != '':
            # os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB_template.setText(filename)


    def selectFile_QKanDB(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        filename = QFileDialog.getOpenFileName(self.dlg, "QKan-Datenbank auswählen",
                                               self.default_dir,"*.sqlite")
        # if os.path.dirname(filename) != '':
            # os.chdir(os.path.dirname(filename))
        self.dlg.tf_QKanDB.setText(filename)


    # Ende Eigene Funktionen ---------------------------------------------------


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_QKan = ''

        # Layerliste erstellen
        self.layers = self.iface.legendInterface().layers()
        # logger.debug('Layerliste erstellt')
        if len(self.layers) == 0:
            logger.warning('Keine Layer vorhanden...')
        for lay in self.layers:
            # logger.debug('Verbindungsstring: {}'.format(lay.source()))
            lyattr = {}
            for le in lay.source().split(' '):
                if '=' in le:
                    key, value = le.split('=')
                    lyattr[key] = value.strip('"').strip("'")
                    # logger.debug('Verbindung gefunden: {}: {}'.format(key,value))
            if 'table' in lyattr and 'dbname' in lyattr:
                # logger.debug('table und dbname in keys enthalten')
                if lyattr['table'] in ['haltungen', 'schaechte']:
                    # logger.debug('table ist "haltungen" oder "schaechte"')
                    if database_QKan == '':
                        database_QKan = lyattr['dbname']
                        # logger.debug('Datenbank erstmals gesetzt: {}'.format(database_QKan))
                    elif database_QKan != lyattr['dbname']:
                        database_QKan = ''
                        logger.warning('Abweichende Datenbankanbindung gefunden: {}'.format(lyattr['dbname']))
                        break           # Im Projekt sind mehrere Sqlite-Datenbanken eingebungen...

        if database_QKan != '':
            self.dlg.tf_QKanDB.setText(database_QKan)

        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # (jh, 08.02.2017)

            # Namen der Datenbanken uebernehmen
            database_Qkan = self.dlg.tf_QKanDB.text()
            database_HE = self.dlg.tf_heDB_dest.text()
            dbtemplate_HE = self.dlg.tf_heDB_template.text()
            # logger.debug(u"Kontrolle: database_HE = {}",database_HE)
            auswahl_teilgebiete = self.dlg.tf_auswahlTeilgebiete.text()
            check_tabinit = self.dlg.cb_tabinit.isChecked()
            check_difftezg = self.dlg.cb_difftezg.isChecked()

            # Konfigurationsdaten schreiben
            self.config['database_HE'] = database_HE
            self.config['dbtemplate_HE'] = dbtemplate_HE
            self.config['database_Qkan'] = database_Qkan
            self.config['auswahl_TG'] = auswahl_teilgebiete

            with codecs.open(self.configfil,'w') as fileconfig:
                # logger.debug(u"Config-Dictionary: {}".format(self.config))
                fileconfig.write(json.dumps(self.config))


            # Start der Verarbeitung

            exportKanaldaten(iface, database_HE, dbtemplate_HE, database_Qkan,
                             auswahl_teilgebiete, check_tabinit, check_difftezg)
