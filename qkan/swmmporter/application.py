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

from pathlib import Path
import shutil

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory
import logging

import qkan.config
from qkan import QKan, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import read_qml, fehlermeldung
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from ._exportSWMM import ExportTask
from ._importSWMM import ImportTask
from .application_dialog import ExportDialog, ImportDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip

logger = logging.getLogger("QKan.importswmm")

class SWMMPorter(QKanPlugin):
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

        default_dir = get_default_dir()
        self.log.debug(f"He8Porter: default_dir: {default_dir}")
        self.import_dlg = ImportDialog(default_dir=self.default_dir, tr=self.tr)
        self.export_dlg = ExportDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_export = ":/plugins/qkan/swmmporter/res/icon_exportSWMM.png"
        QKan.instance.add_action(
            icon_export,
            text=self.tr("Export in SWMM-Datei (*.INP)"),
            callback=self.run_export,
            parent=self.iface.mainWindow(),
        )

        icon_import = ":/plugins/qkan/swmmporter/res/icon_importSWMM.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus SWMM-Datei (*.INP)"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.export_dlg.close()
        self.import_dlg.close()


    def run_export (self) -> None:
        """Anzeigen des Exportformulars und anschließender Start des Exports in eine *.inp-Datei"""

        # noinspection PyArgumentList

        with DBConnection() as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in swmmporter.SWMMPorter.run_export:\n"
                    "QKan-Datenbank wurde nicht "
                    "gefunden oder war nicht aktuell!\nAbbruch!"
                )
                return

            self.export_dlg.tf_database.setText(db_qkan.dbname)

            if not self.export_dlg.prepareDialog(db_qkan):
                return

            # Formular anzeigen
            self.export_dlg.show()

            # Im Formular wurde [OK] geklickt
            if self.export_dlg.exec_():
                self._save_config()
                self._doexport(db_qkan)

        self.log.debug("Closed DB")

    def _save_config(self) -> None:
        """Read from form and save to config"""
        QKan.config.database.qkan = self.export_dlg.tf_database.text()
        QKan.config.swmm.export_file = self.export_dlg.tf_SWMM_dest.text()
        QKan.config.swmm.template = self.export_dlg.tf_SWMM_template.text()

        QKan.config.check_export.haltungen = (
            self.export_dlg.cb_haltungen.isChecked()
        )
        QKan.config.check_export.schaechte = (
            self.export_dlg.cb_schaechte.isChecked()
        )
        QKan.config.check_export.auslaesse = (
            self.export_dlg.cb_auslaesse.isChecked()
        )
        QKan.config.check_export.speicher = self.export_dlg.cb_speicher.isChecked()
        QKan.config.check_export.pumpen = self.export_dlg.cb_pumpen.isChecked()
        QKan.config.check_export.wehre = self.export_dlg.cb_wehre.isChecked()
        QKan.config.check_export.flaechen = self.export_dlg.cb_flaechen.isChecked()

        QKan.config.check_export.einzugsgebiete = (
            self.export_dlg.cb_einzugsgebiete.isChecked()
        )

        QKan.config.check_export.append = self.export_dlg.rb_append.isChecked()
        QKan.config.check_export.update = self.export_dlg.rb_update.isChecked()
        QKan.config.check_export.new = self.export_dlg.rb_new.isChecked()

        teilgebiete = [
            _.text() for _ in self.export_dlg.lw_teilgebiete.selectedItems()
        ]
        QKan.config.selections.teilgebiete = teilgebiete

        QKan.config.save()

    def _doexport(self, db_qkan: DBConnection) -> bool:
        """Start des Exports in eine SWMM-Datei

        Einspringpunkt für Test
        """

        if self.export_dlg.rb_update.isChecked():
            status = 'update'
        elif self.export_dlg.rb_append.isChecked():
            status = 'append'
        else:
            status = 'new'

        # Run export
        ExportTask(db_qkan, QKan.config.swmm.export_file, QKan.config.swmm.template, QKan.config.selections.teilgebiete, status).run()

        return True

    def run_import(self) -> None:
        """Anzeigen des Importformulars SWMM und anschließender Start des Imports aus einer SWMM-Datei"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.database.qkan = self.import_dlg.tf_database.text()
            QKan.config.swmm.file = self.import_dlg.tf_project.text()
            QKan.config.swmm.import_file = self.import_dlg.tf_import.text()

            QKan.config.save()

            if not QKan.config.swmm.import_file:
                fehlermeldung("Fehler beim Import", "Es wurde keine Datei ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde keine Datei ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                crs: QgsCoordinateReferenceSystem = self.import_dlg.epsg.crs()

                try:
                    epsg = int(crs.postgisSrid())
                except ValueError:
                    # TODO: Reporting this to the user might be preferable
                    self.log.exception(
                        "Failed to parse selected CRS %s\nauthid:%s\n"
                        "description:%s\nproj:%s\npostgisSrid:%s\nsrsid:%s\nacronym:%s",
                        crs,
                        crs.authid(),
                        crs.description(),
                        crs.findMatchingProj(),
                        crs.postgisSrid(),
                        crs.srsid(),
                        crs.ellipsoidAcronym(),
                    )
                else:
                    # TODO: This should all be run in a QgsTask to prevent the main
                    #  thread/GUI from hanging. However this seems to either not work
                    #  or crash QGIS currently. (QGIS 3.10.3/0e1f846438)
                    QKan.config.epsg = epsg

                    QKan.config.save()

                    self._doimport()


    def _doimport(self) -> bool:
        """Start des Imports aus einer SWMM-Datei

        Einspringpunkt für Test
        """
        self.log.info("Creating DB")

        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung(
                    "Fehler im SWMM-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im SWMM-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )
                return False

            self.log.info("DB creation finished, starting importer")
            imp = ImportTask(QKan.config.swmm.import_file, db_qkan, QKan.config.project.file)
            imp.run()
            del imp

            # Write and load new project file, only if new project
            if QgsProject.instance().fileName() == '':
                QKan.config.project.template = str(
                    Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
                )
                qgsadapt(
                    QKan.config.database.qkan,
                    db_qkan,
                    QKan.config.project.file,
                    QKan.config.project.template,
                    QKan.config.epsg,
                )

                # Load generated project
                # noinspection PyArgumentList
                project = QgsProject.instance()
                project.read(QKan.config.project.file)
                project.reloadAllLayers()

        self.log.debug("Closed DB")
        return True
