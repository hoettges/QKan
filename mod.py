# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Gangliniengrafik
                                 A QGIS plugin
 Dieses Plugin erzeugt Ganglininen von Kanalnetzen
                              -------------------
        begin                : 2017-02-09
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Michael Gesenhues
        email                : Gesenhues@fh-aachen.de
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

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__),'..\QKan_Database'))

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon,QMessageBox,QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from mod_dialog import GangliniengrafikDialog
import ganglinien
from dbfunc import DBConnection
# from dbmanager import DBConnection       # alte Version von M. Gesenhues arbeitete noch mit lokalem Modul
from qgis.core import *
from qgis.gui import *

class Gangliniengrafik:
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
            'Gangliniengrafik_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Gangliniengrafik')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Gangliniengrafik')
        self.toolbar.setObjectName(u'Gangliniengrafik')
        self.dbname=''
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
        return QCoreApplication.translate('Gangliniengrafik', message)


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
        self.dlg = GangliniengrafikDialog()

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

        icon_path = ':/plugins/Gangliniengrafik/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Ganglinien erzeugen'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.dlg.btnPath.clicked.connect(self.sel_dbPath)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Gangliniengrafik'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def showMessageBox(self,s):
        msg = QMessageBox()
        msg.setText(s)
        msg.show()
        msg.exec_()
    def sel_dbPath(self):
        filename=QFileDialog.getOpenFileName(self.dlg,"Select Database")
        self.dbname=filename
        self.dlg.label.setText(filename)
        self.run()
    def run(self):
        self.dlg.comboBox.clear()
        #ausgewählter Layer(Rohr,schacht o.Ä.
        layer = self.iface.activeLayer()
        #Parameter für die Abfrage
        method_haltung = ["Durchfluss", "Geschwindigkeit", "Auslastung"]
        method_schacht = ["Zufluss", "Wasserstand", "Durchfluss"]
        datatypeH=["cbm/s","m/s","%","cbm"]
        datatypeS = ["cbm/s", "m NN", "cbm/s"]
        colors=['r','g','b','c','m','y','k']
        if layer!=None:
            layertype = layer.name()
            columns=[]
            #Anzahl der Layer
            selLayerCount = layer.selectedFeatureCount()
            if (selLayerCount >= 1):
                layerObject = layer.selectedFeatures()[0]
                if layertype == "haltungen":
                    self.dlg.comboBox.addItems(method_haltung)
                    columns=method_haltung
                elif layertype == "schaechte":
                    self.dlg.comboBox.addItems(method_schacht)
                    columns=method_schacht
                    layertype="schacht"
                else:
                    self.showMessageBox("Layer not supported!")
                    return
            else:
                self.showMessageBox("Pls Select one or more objects of that Layer!!")
                return
            db = DBConnection(self.dbname)
            if(db.con==None):
                self.showMessageBox("select a Database")
                self.sel_dbPath()
                return
            #dbname = "C:/Users/ba/Desktop/he78-Beispiel-T5a-E.idbf"
            self.dlg.label.setText("Messwerte-Datenbank:"+ self.dbname)
            #Für jeden Parameter eine Grafik erzeugen
            for col in columns:
                i = 0
                p=ganglinien.Presenter()
                #Für jedes objekt(Feature) eine Linie in der Grafik erzeugen
                for feature in layer.selectedFeatures():
                    times, data = db.getData(layertype, feature[1], col)
                    p.addLine(times,data,colors[i],feature[1])
                    p.setAxLabels("time",datatypeH[columns.index(col)])
                    i=i+1
                    if i==len(colors):
                        i=0
                #grafik als widget in die GUI einbinden
                self.dlg.stackedWidget.insertWidget(columns.index(col),p.getWidget())
                del p




            self.dlg.stackedWidget.setCurrentIndex(0)
            self.dlg.show()

            del db
        else:
            self.showMessageBox("Select a Layer!")
            return
        """Run method that performs all the real work"""
        # show the dialog




        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            pass
