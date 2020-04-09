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
from qkan import QKan, enums

# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences
from . import resources

# Import the code for the dialog
from .application_dialog import ImportSWMMDialog
from .importSWMM import importKanaldaten

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.swmmporter.application")


class ImportFromSWMM:
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
        self.dlg = ImportSWMMDialog()

        # # Declare instance attributes
        # self.actions = []
        # self.menu = self.tr(u'&QKan Import aus DYNA-Datei')
        # # TODO: We are going to let the user set this up in a future iteration
        # self.toolbar = self.iface.addToolBar(u'ImportFromDyna')
        # self.toolbar.setObjectName(u'ImportFromDyna')

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 09.10.2016)

        logger.info("QKan_ImportSWMM initialisiert...")

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        self.dlg.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)
        self.dlg.pb_selectSWMMFile.clicked.connect(self.select_SWMMFile)
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
        return QCoreApplication.translate("ImportFromSWMM", message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/swmmporter/icon_importSWMM.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr(u"Import aus SWMM-Datei (*.INP)"), # QGIS中ICON旁的文字
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        pass

    # Anfang Eigene Funktionen -------------------------------------------------
    # (jh, 09.10.2016)

    def select_SWMMFile(self):
        u"""DYNA (*.ein) -datei auswählen"""

        filename, __ = QFileDialog.getOpenFileName(
            self.dlg,
            "Dateinamen der zu lesenden SWMM-Datei eingeben",
            self.default_dir,
            "*.inp",
        )
        self.dlg.tf_SWMMFile.setText(filename)

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
        self.dlg.tf_SWMMFile.setText(QKan.config.dyna.file)

        self.dlg.qsw_epsg.setCrs(
            QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg)
        )

        self.dlg.tf_projectFile.setText(QKan.config.project.file)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Namen der Datenbanken uebernehmen
            SWMMfile: str = self.dlg.tf_SWMMFile.text()
            database_qkan: str = self.dlg.tf_qkanDB.text()
            projectfile: str = self.dlg.tf_projectFile.text()
            epsg: int = int(self.dlg.qsw_epsg.crs().postgisSrid())

            # Konfigurationsdaten schreiben
            QKan.config.database.qkan = database_qkan
            QKan.config.dyna.file = SWMMfile
            QKan.config.epsg = epsg
            QKan.config.project.file = projectfile

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            logger.debug(f"""QKan-Modul Aufruf
                importKanaldaten(
                    "{SWMMfile}", 
                    "{database_qkan}", 
                    "{projectfile}", 
                    {epsg}, 
                )""")

            importKanaldaten(
                SWMMfile,
                database_qkan, 
                projectfile, 
                epsg,
            )
