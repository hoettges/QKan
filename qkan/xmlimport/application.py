    # -*- coding: utf-8 -*-
"""
/***************************************************************************
 xmlimport
                                 A QGIS plugin
 xml
                              -------------------
        begin                : 2018-05-18
        git sha              : $Format:%H$
        copyright            : (C) 2018 by fhaachen
        email                : @fhaachen
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QgsProject, QgsMapLayerRegistry
from qgis.utils import iface, pluginDirectory
from qgis.gui import QgsGenericProjectionSelector
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from application_dialog import xmlimportDialog
from xml_import import M150Xml
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fortschritt, fehlermeldung
from qkan.tools.k_qgsadapt import qgsadapt

from shapely.geometry import MultiPolygon, MultiLineString
import os
import sys
import json
import logging
import site
from application_dialog import xmlimportDialog
# noinspection PyUnresolvedReferences

logger = logging.getLogger(u'QKan')



class xmlimport:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
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
            'xmlimport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = xmlimportDialog()

        logger.info(u'\n\nxmlimport initialisiert...')

        # --------------------------------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(), u'qkan')

        if not os.path.isdir(wordir):
            os.makedirs(wordir)

        # --------------------------------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        self.configfil = os.path.join(wordir, u'qkan.json')
        if os.path.exists(self.configfil):
            with open(self.configfil, 'r') as fileconfig:
                self.config = json.loads(fileconfig.read())
        else:
            self.config = {'epsg': '25832'}                # Projektionssystem
            self.config['database_QKan'] = ''
            self.config['xmlImportFile'] = ''
            self.config['projectfile'] = ''
            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        if 'database_QKan' in self.config:
            database_QKan = self.config['database_QKan']
        else:
            database_QKan = ''
        self.dlg.tf_qkanDB.setText(database_QKan)

        if 'xmlImportFile' in self.config:
            xmlImportFile = self.config['xmlImportFile']
        else:
            xmlImportFile = ''
        self.dlg.tf_xmlImportFile.setText(xmlImportFile)

        if 'epsg' in self.config:
            epsg = self.config['epsg']
        else:
            epsg = '25832'
        self.dlg.tf_epsg.setText(epsg)

        if 'projectfile' in self.config:
            projectfile = self.config['projectfile']
        else:
            projectfile = ''
        self.dlg.tf_projectFile.setText(projectfile)



        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Xml-Import')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'xmlimport')
        self.toolbar.setObjectName(u'xmlimport')

        self.dlg.pb_selectXmlImportFile.clicked.connect(self.select_xmlImportFile)
        self.dlg.pb_selectProjectFile.clicked.connect(self.selectProjectFile)
        self.dlg.pb_selectKBS.clicked.connect(self.selectKBS)
        self.dlg.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)


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
        return QCoreApplication.translate('xmlimport', message)

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

        # Create the dialog (after translation) and keep reference

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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/xmlimport/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Xml-Import'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_xmlImportFile(self):
        filename = QFileDialog.getOpenFileName(self.dlg, "Zu importierende XML-Datei auswählen", "", '*.xml')
        self.dlg.tf_xmlImportFile.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))

    def selectKBS(self):
        """KBS auswählen. Setzt das KBS für die weiteren Funktionen

        :returns: void
        """
        projSelector = QgsGenericProjectionSelector()
        projSelector.exec_()
        erg = projSelector.selectedAuthId()
        if len(erg.split(':')) == 2:
            self.dlg.tf_epsg.setText(erg.split(':')[1])
        else:
            self.dlg.tf_epsg.setText(erg)

    def selectProjectFile(self):
        """Zu erzeugende Projektdatei festlegen, falls ausgewählt."""

        filename = QFileDialog.getSaveFileName(self.dlg,
                                               "Dateinamen der zu erstellenden Projektdatei eingeben",
                                               self.default_dir,
                                               "*.qgs")
        self.dlg.tf_projectFile.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))

    def selectFile_qkanDB(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "QKan-Datenbank eingeben/auswählen", "", '*.sqlite')
        self.dlg.tf_qkanDB.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))




    def run(self):
        """Run method that performs all the real work"""

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            # Übernahme der Eingaben aus dem Formular

            xmlImportFile = self.dlg.tf_xmlImportFile.text()
            database_QKan = self.dlg.tf_qkanDB.text()
            projectfile = self.dlg.tf_projectFile.text()
            epsg = self.dlg.tf_epsg.text()


            # Konfigurationsdaten schreiben

            self.config['xmlImportFile'] = xmlImportFile
            self.config['epsg'] = epsg
            self.config['database_QKan'] = database_QKan
            self.config['projectfile'] = projectfile


            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))


            # Start der Verarbeitung

            if len(xmlImportFile) == 0:

                fehlermeldung(u"Fehler in xml_import",
                                u'Es wurde keine Datei ausgewählt!')
                iface.messageBar().pushMessage(u"Fehler in xml_import",
                                               u'Es wurde keine Datei ausgewählt!', level=QgsMessageBar.CRITICAL)


            else:
                # Datenbankverbindung

                dbQK = DBConnection(dbname=database_QKan, epsg=epsg)      # Datenbankobjekt der QKan-Datenbank zum Schreiben

                if dbQK is None:
                    fehlermeldung(u"Fehler in xmlimport.application.run", 
                                  u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
                    iface.messageBar().pushMessage(u"Fehler in xmlimport.application.run",
                                u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                        database_QKan), level=QgsMessageBar.CRITICAL)


                    return None
                elif not dbQK:

                    # Datenbank wurde geändert
                    return None


                data = M150Xml(xmlImportFile, dbQK, epsg)
                data.importSchaechte()
                data.importAuslaesse()
                data.importSpeicher()
                data.importHaltungen()
                data.importWehre()
                data.importPumpen()

                #data.xml_speichern()

                # Projektdatei schreiben
                templateDir = os.path.join(pluginDirectory('qkan'), u"templates")
                projectTemplate = os.path.join(templateDir,'Projekt.qgs')

                qgsadapt(projectTemplate, database_QKan, epsg, projectfile, True, u'SpatiaLite')

                # Erzeugtes Projekt laden
                project = QgsProject.instance()
                # project.read(QFileInfo(projectfile))
                project.read(QFileInfo(projectfile))         # read the new project file
                QgsMapLayerRegistry.instance().reloadAllLayers()

