# -*- coding: utf-8 -*-

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgisInterface
from qkan import QKan
from qkan.plugin import QKanPlugin

from .application_dialog import ImportFromDynaDialog
from .import_from_dyna import import_kanaldaten

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class ImportFromDyna(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.dlg = ImportFromDynaDialog()

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/importdyna/icon_ImportFromDyna.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Import aus DYNA-Datei (*.EIN)"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        self.dlg.close()

    def run(self):
        """Run method that performs all the real work"""

        self.dlg.tf_qkanDB.setText(QKan.config.database.qkan)
        self.dlg.tf_dynaFile.setText(QKan.config.dyna.file)

        # noinspection PyArgumentList,PyCallByClass
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
            dynafile: str = self.dlg.tf_dynaFile.text()
            database_qkan: str = self.dlg.tf_qkanDB.text()
            projectfile: str = self.dlg.tf_projectFile.text()
            epsg: int = int(self.dlg.qsw_epsg.crs().postgisSrid())

            # Konfigurationsdaten schreiben
            QKan.config.database.qkan = database_qkan
            QKan.config.dyna.file = dynafile
            QKan.config.epsg = epsg
            QKan.config.project.file = projectfile

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                importKanaldaten(
                    "{dynafile}", 
                    "{database_qkan}", 
                    "{projectfile}", 
                    {epsg}, 
                )"""
            )

            import_kanaldaten(
                dynafile, database_qkan, projectfile, epsg,
            )
