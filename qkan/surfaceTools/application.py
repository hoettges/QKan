# -*- coding: utf-8 -*-

"""

  QGIS-Plugin
  ===========

  Definition der Formularklasse

  | Dateiname            : application.py
  | Date                 : Mai 2020
  | Copyright            : (C) 2020 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

"""
import logging
import os

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QFileDialog

# from qgis.utils import iface
from qkan import QKan, enums

# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences
from . import resources

# Import the code for the dialog
from .application_dialog import SurfaceToolDialog
from .surfaceTool import FlaechenVerarbeitung, accessAttr
from qkan.database.qkan_utils import get_database_QKan

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.surfaceTools.application")

class SurfaceTools:
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
        self.dlg = SurfaceToolDialog()

        # # Declare instance attributes
        # self.actions = []
        # self.menu = self.tr(u'&QKan Import aus DYNA-Datei')
        # # TODO: We are going to let the user set this up in a future iteration
        # self.toolbar = self.iface.addToolBar(u'ImportFromDyna')
        # self.toolbar.setObjectName(u'ImportFromDyna')

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 09.10.2016)

        logger.info("Qkan_SurfaceTools initialisiert...")

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())
        # self.dlg.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

                We implement this ourselves since we do not inherit QObject.

                :param message: String for translation.
                :type message: str, QString

                :returns: Translated version of message.
                :rtype: QString
                """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("SurfaceTools", message)

    def initGui(self):
        icon_path = ":/plugins/qkan/surfaceTools/icon_surfaceTool.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr(u"Solve Overlap of Layers"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )


    def unload(self):
        pass

    def run(self):
        # database_qkan, _ = get_database_QKan()
        # self.dlg.tf_qkanDB.setText(QKan.config.database.qkan)
        # Fetch the currently loaded layers
        # Fetch the currently loaded layers

        database_qkan, _ = get_database_QKan()
        self.dlg.cb_haupt.clear()
        self.dlg.cb_geschnitten.clear()
        obj = accessAttr(database_qkan)
        tempList = obj.accessAttribute()
        abflussparameter = list(set(tempList))
        for tempAttr in abflussparameter:
            attr = str(tempAttr).lstrip('(\'').rstrip(',\')')
            self.dlg.cb_haupt.addItem(attr)
            self.dlg.cb_geschnitten.addItem(attr)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            schneiden = self.dlg.cb_haupt.currentText()
            geschnitten = self.dlg.cb_geschnitten.currentText()
            QKan.config.database.qkan = database_qkan

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            logger.debug(f"""QKan-Modul Aufruf
                            FlaechenVerarbeitung
                            """)

            FlaechenVerarbeitung(database_qkan, schneiden, geschnitten)
            del obj
