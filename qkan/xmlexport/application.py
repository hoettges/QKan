    # -*- coding: utf-8 -*-
"""
/***************************************************************************
 xmlexport
                                 A QGIS plugin
 xml
                              -------------------
        begin                : 2019-05-18
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
from application_dialog import xmlexportDialog
from xml_export import exportKanaldaten
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import get_database_QKan, fortschritt, fehlermeldung
from qkan.tools.k_qgsadapt import qgsadapt

from shapely.geometry import MultiPolygon, MultiLineString
import os
import sys
import json
import logging
import site
from application_dialog import xmlexportDialog
# noinspection PyUnresolvedReferences

logger = logging.getLogger(u'QKan')



class xmlexport:
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
            'xmlexport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = xmlexportDialog()

        logger.info(u'\n\nxmlexport initialisiert...')

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
            self.config['xmlExportFile'] = ''
            #self.config['projectfile'] = ''


            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        if 'database_QKan' in self.config:
            database_QKan = self.config['database_QKan']
        else:
            database_QKan = ''
        self.dlg.tf_database_QKan.setText(database_QKan)

        if 'xmlExportFile' in self.config:
            xmlExportFile = self.config['xmlExportFile']
        else:
            xmlExportFile = ''
        self.dlg.tf_xmlExportFile.setText(xmlExportFile)

        #if 'epsg' in self.config:
        #    epsg = self.config['epsg']
        #else:
        #    epsg = '25832'
        #self.dlg.epsg.setText(epsg)

        #if 'projectfile' in self.config:
        #    projectfile = self.config['projectfile']
        #else:
        #    projectfile = ''
        #self.dlg.tf_projectFile.setText(projectfile)



        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Xml-Export')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'xmlexport')
        self.toolbar.setObjectName(u'xmlexport')

        self.dlg.pb_selectXmlExportFile.clicked.connect(self.selectXmlExportFile)
        #self.dlg.pb_selectProjectFile.clicked.connect(self.selectProjectFile)
        #self.dlg.pb_selectKBS.clicked.connect(self.selectKBS)
        self.dlg.pb_selectdatabase_QKan.clicked.connect(self.selectdatabase_QKan)


        def cb_set(name, cbox, default):
            if name in self.config:
                checked = self.config[name]
            else:
                checked = default
            cbox.setChecked(checked)
            return checked

        schaechte = cb_set('export_schaechte', self.dlg.cb_export_schaechte, True)
        auslaesse = cb_set('export_auslaesse', self.dlg.cb_export_auslaesse, True)
        speicher = cb_set('export_speicher', self.dlg.cb_export_speicher, True)
        haltungen = cb_set('export_haltungen', self.dlg.cb_export_haltungen, True)
        pumpen = cb_set('export_pumpen', self.dlg.cb_export_pumpen, False)
        wehre = cb_set('export_wehre', self.dlg.cb_export_wehre, False)



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
        return QCoreApplication.translate('xmlexport', message)

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

        icon_path = ':/plugins/xmlexport/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Xml-Export'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def selectXmlExportFile(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "zu erstellende xml datei", self.default_dir, "*.xml")
        self.dlg.tf_xmlExportFile.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))

    def selectdatabase_QKan(self):
        filename = QFileDialog.getOpenFileName(self.dlg, "Zu importierende SQlite-Datei auswählen", "", '*.sqlite')
        self.dlg.tf_database_QKan.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))

    #def selectKBS(self):
     #   """KBS auswählen. Setzt das KBS für die weiteren Funktionen

      #  :returns: void
       # """
        #projSelector = QgsGenericProjectionSelector()
        #projSelector.exec_()
        #erg = projSelector.selectedAuthId()
        #if len(erg.split(':')) == 2:
        #    self.dlg.tf_epsg.setText(erg.split(':')[1])
        #else:
        #    self.dlg.tf_epsg.setText(erg)

    #def selectProjectFile(self):
    #    """Zu erzeugende Projektdatei festlegen, falls ausgewählt."""

    #    filename = QFileDialog.getOpenFileName(self.dlg,
    #                                           "Dateinamen der zu erstellenden Projektdatei eingeben",
    #                                           self.default_dir,
    #                                           "*.qgs")
    #    self.dlg.tf_projectFile.setText(filename)

         #Aktuelles Verzeichnis wechseln
    #    if os.path.dirname(filename) != '':
    #        os.chdir(os.path.dirname(filename))

    def selectFile_database_QKan(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "QKan-Datenbank auswählen", "", '*.sqlite')
        self.dlg.tf_database_QKan.setText(filename)

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

        database_QKan = ''
        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in k_link", u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error("k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        if database_QKan != '':
            self.dlg.tf_database_QKan.setText(database_QKan)

        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen
        if self.dbQK is None:
            fehlermeldung("Fehler in QKan_CreateUnbefFl",
                          u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage("Fehler in QKan_Import_from_HE",
                                           u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                                               database_QKan), level=QgsMessageBar.CRITICAL)
            return None


        if result:

            # Übernahme der Eingaben aus dem Formular

            xmlExportFile = self.dlg.tf_xmlExportFile.text()
            database_QKan = self.dlg.tf_database_QKan.text()




            # Konfigurationsdaten schreiben

            self.config['xmlExportFile'] = xmlExportFile

            self.config['database_QKan'] = database_QKan

            check_export = {}
            check_export['export_schaechte'] = self.dlg.cb_export_schaechte.isChecked()
            check_export['export_auslaesse'] = self.dlg.cb_export_auslaesse.isChecked()
            check_export['export_speicher'] = self.dlg.cb_export_speicher.isChecked()
            check_export['export_haltungen'] = self.dlg.cb_export_haltungen.isChecked()
            check_export['export_pumpen'] = self.dlg.cb_export_pumpen.isChecked()
            check_export['export_wehre'] = self.dlg.cb_export_wehre.isChecked()


            for el in check_export:
                self.config[el] = check_export[el]

            with open(self.configfil, 'w') as fileconfig:
                # logger.debug(u"Config-Dictionary: {}".format(self.config))
                fileconfig.write(json.dumps(self.config))

            exportKanaldaten(self.dbQK, xmlExportFile, check_export, liste_teilgebiete=[], datenbanktyp=u'spatialite')


