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
import os

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QFileDialog

from qkan import QKan
from qkan.plugin import QKanPlugin

from .application_dialog import ImportSWMMDialog
from .importSWMM import importKanaldaten

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class ImportFromSWMM(QKanPlugin):
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        super().__init__(iface)
        self.dlg = ImportSWMMDialog()

        self.dlg.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)
        self.dlg.pb_selectSWMMFile.clicked.connect(self.select_SWMMFile)
        self.dlg.pb_selectProjectFile.clicked.connect(self.selectProjectFile)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/swmmporter/res/icon_importSWMM.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Import aus SWMM-Datei (*.INP)"),  # QGIS中ICON旁的文字
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlg.close()

    def select_SWMMFile(self) -> None:
        """DYNA (*.ein) -datei auswählen"""

        # noinspection PyArgumentList
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

    def selectFile_qkanDB(self) -> None:
        """Datenbankverbindung zur QKan-Datenbank (SpatiaLite) auswaehlen, aber noch nicht verbinden.
        Falls die Datenbank noch nicht existiert, wird sie nach Betaetigung von [OK] erstellt."""

        # noinspection PyArgumentList
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

    def selectProjectFile(self) -> None:
        """Zu erzeugende Projektdatei festlegen, falls ausgewählt."""

        # noinspection PyArgumentList
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

    def run(self) -> None:
        """Run method that performs all the real work"""

        self.dlg.tf_qkanDB.setText(QKan.config.database.qkan)
        self.dlg.tf_SWMMFile.setText(QKan.config.dyna.file)

        # noinspection PyCallByClass,PyArgumentList
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
            swm_mfile: str = self.dlg.tf_SWMMFile.text()
            database_qkan: str = self.dlg.tf_qkanDB.text()
            projectfile: str = self.dlg.tf_projectFile.text()
            epsg: int = int(self.dlg.qsw_epsg.crs().postgisSrid())

            # Konfigurationsdaten schreiben
            QKan.config.database.qkan = database_qkan
            QKan.config.dyna.file = swm_mfile
            QKan.config.epsg = epsg
            QKan.config.project.file = projectfile

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                importKanaldaten(
                    "{swm_mfile}", 
                    "{database_qkan}", 
                    "{projectfile}", 
                    {epsg}, 
                )"""
            )

            importKanaldaten(
                swm_mfile,
                database_qkan,
                projectfile,
                epsg,
            )
