# -*- coding: utf-8 -*-

"""

  QGIS-Plugin
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
import logging
import os

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QFileDialog

# from qgis.utils import iface
from qkan import QKan

# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences
from . import resources

# Import the code for the dialog
from .application_dialog import ImportFromDynaDialog
from .import_from_dyna import importKanaldaten

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.importdyna.application")


class ImportFromDyna:
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
        self.dlg = ImportFromDynaDialog()

        # # Declare instance attributes
        # self.actions = []
        # self.menu = self.tr(u'&QKan Import aus DYNA-Datei')
        # # TODO: We are going to let the user set this up in a future iteration
        # self.toolbar = self.iface.addToolBar(u'ImportFromDyna')
        # self.toolbar.setObjectName(u'ImportFromDyna')

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 09.10.2016)

        logger.info(u"QKan_ImportDyna initialisiert...")

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        self.dlg.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)
        self.dlg.pb_selectDynaFile.clicked.connect(self.select_dynaFile)
        self.dlg.pb_selectProjectFile.clicked.connect(self.selectProjectFile)

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
        return QCoreApplication.translate("ImportFromDyna", message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/importdyna/icon_ImportFromDyna.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr(u"Import aus DYNA-Datei (*.EIN)"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        pass

    # Anfang Eigene Funktionen -------------------------------------------------
    # (jh, 09.10.2016)

    def select_dynaFile(self):
        u"""DYNA (*.ein) -datei auswählen"""

        filename, __ = QFileDialog.getOpenFileName(
            self.dlg,
            "Dateinamen der zu lesenden Kanal++-Datei eingeben",
            self.default_dir,
            "*.ein",
        )
        self.dlg.tf_dynaFile.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != "":
            os.chdir(os.path.dirname(filename))

    def selectFile_qkanDB(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiaLite) auswaehlen, aber noch nicht verbinden.
           Falls die Datenbank noch nicht existiert, wird sie nach Betaetigung von [OK] erstellt. """

        filename, __ = QFileDialog.getSaveFileName(
            self.dlg,
            "Dateinamen der zu erstellenden SpatiaLite-Datenbank eingeben",
            self.default_dir,
            "*.sqlite",
        )
        self.dlg.tf_qkanDB.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != "":
            os.chdir(os.path.dirname(filename))

    def selectProjectFile(self):
        """Zu erzeugende Projektdatei festlegen, falls ausgewählt."""

        filename, __ = QFileDialog.getSaveFileName(
            self.dlg,
            "Dateinamen der zu erstellenden Projektdatei eingeben",
            self.default_dir,
            "*.qgs",
        )
        self.dlg.tf_projectFile.setText(filename)

        # Aktuelles Verzeichnis wechseln
        if os.path.dirname(filename) != "":
            os.chdir(os.path.dirname(filename))

    # Ende Eigene Funktionen ---------------------------------------------------

    def run(self):
        """Run method that performs all the real work"""

        self.dlg.tf_qkanDB.setText(QKan.config.database.qkan)
        self.dlg.tf_dynaFile.setText(QKan.config.dyna.dynafile)

        self.dlg.qsw_epsg.setCrs(
            QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg)
        )

        self.dlg.tf_projectFile.setText(QKan.config.project_file)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Namen der Datenbanken uebernehmen
            dynafile: str = self.dlg.tf_dynaFile.text()
            database_qkan: str = self.dlg.tf_qkanDB.text()
            projectfile: str = self.dlg.tf_projectFile.text()
            epsg: int = int(self.dlg.qsw_epsg.crs().postgisSrid())

            # Konfigurationsdaten schreiben
            QKan.config.epsg = self.epsg
            QKan.config.database.qkan = database_qkan
            QKan.config.dyna.dynafile = dynafile
            QKan.config.project_file = projectfile

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            logger.info(
                """qkan-Modul:\n        importKanaldaten(
                dynafile='{dynafile}', 
                database_QKan='{database_QKan}', 
                projectfile='{projectfile}', 
                epsg='{epsg}', 
                dbtyp = '{dbtyp}')""".format(
                    dynafile=dynafile,
                    database_QKan=database_qkan,
                    projectfile=projectfile,
                    epsg=self.epsg,
                    dbtyp="SpatiaLite",
                )
            )

            importKanaldaten(
                dynafile, database_qkan, projectfile, self.epsg, "SpatiaLite"
            )
