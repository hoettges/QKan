from qgis.gui import QgisInterface

from qkan import QKan
from qkan.plugin import QKanPlugin
from qkan.tools.qkan_utils import get_default_dir
from qkan.utils import get_logger

logger = get_logger("QKan.uploadPostgis.application")

from .application_dialog import UploadPostgisDialog

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401


class UploadPostgis(QKanPlugin):
    """
    Plugin zum Upload einer SQLite-Datenbank auf PostGIS WebSuite.
    
    Ermöglicht den Transfer aller geometrischen Objekte aus einer QKan
    SQLite-Datenbank auf einen PostGIS-Server für die Kartendarstellung
    in der WebSuite.
    """
    
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.uploadPostgis_dlg = UploadPostgisDialog(default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_uploadPostgis = ":/plugins/qkan/uploadPostgis/res/icon_uploadPostgis.png"
        QKan.instance.add_action(
            icon_uploadPostgis,
            text=self.tr("Upload nach PostGIS WebSuite"),
            toolbar='QKan-Datenaustausch',
            callback=self.openform_uploadPostgis,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.uploadPostgis_dlg.close()

    def openform_uploadPostgis(self) -> None:
        """Anzeigen des Formulars für den Upload zu PostGIS WebSuite"""

        self.uploadPostgis_dlg._load_uploadPostgis_config()

        self.uploadPostgis_dlg.show()

        if self.uploadPostgis_dlg.exec():
            self.uploadPostgis_dlg._save_uploadPostgis_config()
            
            # Upload wird im Dialog gestartet (über DatabaseDialog)
            self.log.info("Upload-Dialog abgeschlossen")

