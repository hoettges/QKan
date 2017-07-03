# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LinkFlaechenToHaltung
                                 A QGIS plugin
 Verknüpft Flächen mit nächster Haltung
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QListWidgetItem
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from application_dialog import LinkFlaechenToHaltungDialog
import os.path

# Ergaenzt (jh, 12.06.2017) -------------------------------------------------
import json, site
import logging

from qgis.utils import iface
from qgis.gui import QgsMessageBar
from qgis.core import QgsProject, QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
from k_link import linkFlaechenToHaltungen
from QKan_Database.qgis_utils import get_database_QKan
from QKan_Database.dbfunc import DBConnection
import codecs

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger('QKan')

def fortschritt(text,prozent):
    logger.debug(u'{:s} ({:.0f}%)'.format(text,prozent*100))
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text,prozent*100), 'Export: ', QgsMessageLog.INFO)

def fehlermeldung(title, text):
    logger.debug(u'{:s} {:s}'.format(title,text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)

class LinkFlaechenToHaltung:
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
            'LinkFlaechenToHaltung_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LinkFlaechenToHaltungDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QKan_LinkFlaechen')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LinkFlaechenToHaltung')
        self.toolbar.setObjectName(u'LinkFlaechenToHaltung')

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 12.06.2017)

        logger.info('\n\nQKan_LinkFlaechen initialisiert...')

        # --------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(),'qkan')

        if not os.path.isdir(wordir):
            os.makedirs(wordir)

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
        return QCoreApplication.translate('LinkFlaechenToHaltung', message)


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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LinkFlaechenToHaltung/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Link Flaechen To Haltungen'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QKan_LinkFlaechen'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""

        # Funktion zur Zusammenstellung einer Auswahlliste für eine SQL-Abfrage
        def listitems(listWidget):
            items = listWidget.selectedItems()
            liste = u''
            for elem in items:
                if liste == '':
                    liste = "'{}'".format(elem.text())
                else:
                    liste += ", '{}'".format(elem.text())
            return liste

        database_QKan = ''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in k_link", u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error("k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Datenbankverbindung für Abfragen
        dbQK = DBConnection(dbname=database_QKan)      # Datenbankobjekt der QKan-Datenbank zum Lesen
        if dbQK is None:
            fehlermeldung("Fehler in QKan_CreateUnbefFl", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage("Fehler in QKan_Import_from_HE", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        # Abfragen der Tabelle tezg nach verwendeten Abflussparametern
        sql = 'SELECT abflussparameter FROM flaechen GROUP BY abflussparameter'
        dbQK.sql(sql)
        daten = dbQK.fetchall()
        self.dlg.lw_flaechen_abflussparam.clear()
        for elem in daten:
            self.dlg.lw_flaechen_abflussparam.addItem(QListWidgetItem(elem[0]))
        if len(daten) == 1:
            self.dlg.lw_flaechen_abflussparam.setCurrentRow(0)

        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = 'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
        dbQK.sql(sql)
        daten = dbQK.fetchall()
        self.dlg.lw_hal_entw.clear()
        for elem in daten:
            self.dlg.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
        if len(daten) == 1:
            self.dlg.lw_hal_entw.setCurrentRow(0)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # Start der Verarbeitung

            # Abrufen der ausgewählten Elemente in beiden Listen
            liste_flaechen_abflussparam = listitems(self.dlg.lw_flaechen_abflussparam)
            liste_hal_entw = listitems(self.dlg.lw_hal_entw)

            if len(liste_flaechen_abflussparam) == 0 or len(liste_hal_entw) == 0:
                iface.messageBar().pushMessage(u"Bedienerfehler: ", 
                       u'Bitte in beiden Tabellen mindestens ein Element auswählen!', 
                       level=QgsMessageBar.CRITICAL)
                self.run()

            linkFlaechenToHaltungen(database_QKan, liste_flaechen_abflussparam, liste_hal_entw)

            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = iface.legendInterface().layers()
            if 'Anbindung' not in [lay.name() for lay in layers]:        # layers wurde oben erstellt
                uri = QgsDataSourceURI()
                uri.setDatabase(database_QKan)
                uri.setDataSource('', 'linkfl', 'glink')
                vlayer = QgsVectorLayer(uri.uri(), 'Anbindung', 'spatialite')
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)