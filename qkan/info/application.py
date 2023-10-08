from qgis.gui import QgisInterface
from qgis.core import QgsProject
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin
from qkan.database.qkan_database import db_version
from qkan.database.qkan_utils import warnung

from ._info import Info
from .application_dialog import InfoDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class Infos(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.info_dlg = InfoDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/info/res/info.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Infos zum QKan Projekt"),
            callback=self.run_info,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.info_dlg.close()


    def run_info(self) -> None:
        # Prüfen, ob ein Projekt geladen ist
        project = QgsProject.instance()
        layers = project.mapLayers()
        if len(layers) > 0:

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected

            test = Info(DBConnection())
            test.run()
            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            #self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            version = db_version()
            self.info_dlg.textBrowser_2.setText(str(version))
            self.info_dlg.textBrowser_3.setText(str(test.anz_haltungen))
            self.info_dlg.textBrowser_4.setText(str(test.anz_schaechte))
            self.info_dlg.textBrowser_5.setText(str(test.laenge_haltungen))
            self.info_dlg.textBrowser_6.setText(str(test.anz_teilgeb))

            # Run the dialog event loop
            result = self.info_dlg.exec_()

        else:
            warnung( 'Hinweis', 'Es ist kein Projekt geladen!')
