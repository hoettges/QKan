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

from qgis.gui import QgisInterface

from qkan import QKan, get_default_dir, list_selected_items
from qkan.database.qkan_utils import get_database_QKan
from qkan.plugin import QKanPlugin

from .application_dialog import SurfaceToolDialog, VoronoiDialog
from .surfaceTool import SurfaceTask

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class SurfaceTools(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.iface = iface
        default_dir = get_default_dir()
        self.surface_dlg = SurfaceToolDialog(default_dir, tr=self.tr)
        self.voronoi_dlg = VoronoiDialog(default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_path = ":/plugins/qkan/surfaceTools/res/icon_surfaceTool.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Entferne Überlappungen"),
            callback=self.run_cut,
            parent=self.iface.mainWindow(),
        )
        icon_path = ":/plugins/qkan/surfaceTools/res/icon_voronoiTool.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Erzeuge Voronoiflächen zu Haltungen"),
            callback=self.run_voronoi,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.surface_dlg.close()

    def run_cut(self) -> None:
        # database_qkan, _ = get_database_QKan()
        # self.surface_dlg.tf_qkanDB.setText(QKan.config.database.qkan)
        # Fetch the currently loaded layers
        # Fetch the currently loaded layers

        database_qkan, epsg = get_database_QKan()

        self.surface_dlg.prepareDialog(database_qkan, epsg)

        # show the dialog
        self.surface_dlg.show()
        # Run the dialog event loop
        result = self.surface_dlg.exec_()
        # See if OK was pressed
        if result:
            schneiden = self.surface_dlg.cb_haupt.currentText()
            geschnitten = self.surface_dlg.cb_geschnitten.currentText()

            self.log.debug(f'run_cut - Auswahl:\nschneiden: {schneiden}\ngeschnitten: {geschnitten}')

            # QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(f"""QKan-Modul Aufruf SurfaceTask.run_cut """)

            run = SurfaceTask(self.iface, database_qkan, epsg)
            run.run_cut(schneiden, geschnitten)
            del run
            self.iface.mapCanvas().refreshAllLayers()

    def run_voronoi(self) -> None:
        """Erzeugt Voronoi-Flächen zu ausgewählten Haltungen"""

        database_qkan, epsg = get_database_QKan()

        self.log.debug(f'Modul {__name__}: database_qkan: {database_qkan}')

        self.voronoi_dlg.prepareDialog(database_qkan, epsg)

        # show the dialog
        self.voronoi_dlg.show()
        # Run the dialog event loop
        result = self.voronoi_dlg.exec_()
        # See if OK was pressed
        if result:
            # Start der Verarbeitung

            liste_entwarten = list_selected_items(self.voronoi_dlg.lw_hal_entw)
            self.log.debug(f"Modul {__name__}: liste_entwarten = {liste_entwarten}")

            # Modulaufruf in Logdatei schreiben
            self.log.debug(f"""QKan-Modul Aufruf SurfaceTask.run_voronoi """)

            QKan.config.save()

            run = SurfaceTask(self.iface, database_qkan, epsg)
            run.run_voronoi(liste_entwarten)
            del run
            self.iface.mapCanvas().refreshAllLayers()
