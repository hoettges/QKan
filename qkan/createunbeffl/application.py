from qgis.gui import QgisInterface

from qkan import QKan
from qkan.plugin import QKanPlugin

from .application_dialog import CreateUnbefFlDialog

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
