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
from qkan import QKan
from qkan.database.qkan_utils import get_database_QKan
from qkan.plugin import QKanPlugin

from .application_dialog import SurfaceToolDialog
from .surfaceTool import FlaechenVerarbeitung, AccessAttr

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class SurfaceTools(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.dlg = SurfaceToolDialog()

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_path = ":/plugins/qkan/surfaceTools/icon_surfaceTool.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Solve Overlap of Layers"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlg.close()

    def run(self) -> None:
        # database_qkan, _ = get_database_QKan()
        # self.dlg.tf_qkanDB.setText(QKan.config.database.qkan)
        # Fetch the currently loaded layers
        # Fetch the currently loaded layers

        database_qkan, _ = get_database_QKan()
        if not database_qkan:
            self.log.error("database_qkan is undefined")
            return

        self.dlg.cb_haupt.clear()
        self.dlg.cb_geschnitten.clear()
        obj = AccessAttr(database_qkan)
        temp_list = obj.accessAttribute()
        abflussparameter = list(set(temp_list))
        for tempAttr in abflussparameter:
            attr = str(tempAttr).lstrip("('").rstrip(",')")
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
            QKan.config.database.qkan = str(database_qkan)

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                            FlaechenVerarbeitung
                            """
            )

            FlaechenVerarbeitung(str(database_qkan), schneiden, geschnitten)
            del obj
