from typing import Optional

from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QTableWidgetItem
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.plugin import QKanPlugin

from .application_dialog import CreateUnbefFlDialog, list_selected_tab_items
from .k_unbef import create_unpaved_areas

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class CreateUnbefFl(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.dlg = CreateUnbefFlDialog(self)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_path = ":/plugins/qkan/createunbeffl/icon.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Erzeuge unbefestigte Flächen..."),
            callback=self.dlg.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlg.close()
