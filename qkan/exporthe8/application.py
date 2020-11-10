from qgis.gui import QgisInterface

from qkan import QKan
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip
from .application_dialog import ExportToHE8Dialog


class ExportToHE8(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.dlg = ExportToHE8Dialog(self)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/exporthe8/icon_qk2he8.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Export to Hystem-Extran 8"),
            callback=self.dlg.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlg.close()
