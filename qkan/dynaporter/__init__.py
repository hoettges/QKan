from typing import Optional

from qgis.gui import QgisInterface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin

from .dialogs import ExportDialog, ImportDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class DynaPorter(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.db_qkan: Optional[DBConnection] = None

        self.dlg_import = ImportDialog(self)
        self.dlg_export = ExportDialog(self)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/dynaporter/res/icon_export.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Export in DYNA-Datei..."),
            callback=self.dlg_export.run,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/qkan/dynaporter/res/icon_import.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Import aus DYNA-Datei (*.EIN)"),
            callback=self.dlg_import.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlg_import.close()
        self.dlg_export.close()
