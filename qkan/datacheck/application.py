import os
from qgis.utils import pluginDirectory
from qgis.gui import QgisInterface

from qkan import QKan, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin

from ._plausi import PlausiTask
from .application_dialog import PlausiDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip

# logger = logging.getLogger("QKan.he8.application")


class Plausi(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"Plausi: default_dir: {default_dir}")
        self.plausi_dlg = PlausiDialog(default_dir, tr=self.tr)

        self.db_qkan: DBConnection = None

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_plausi = ":/plugins/qkan/datacheck/res/icon_plausi.png"
        QKan.instance.add_action(
            icon_plausi,
            text=self.tr("Plausibilitätsprüfungen"),
            callback=self.run_plausi,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.plausi_dlg.close()


    def run_plausi(self) -> None:
        """Anzeigen des Formulars zur Auswahl der durchzuführenden Plausibilitätsprüfungen und anschließender Start"""

        self.db_qkan = DBConnection()
        if not self.db_qkan:            # Setzt self.db_qkan und self.database_qkan
            return False

        plausisqlfile = os.path.join(pluginDirectory("qkan"), "templates", "plausibilitaetspruefungen.sql")
        if not self.db_qkan.executefile(plausisqlfile):
            self.log.error(f'Plausibilitätsabfragen konnten nicht gelesen oder ausgeführt werden:\n{plausisqlfile}\n')

        if not self.plausi_dlg.prepareDialog(self.db_qkan):
            return False

        self.plausi_dlg.show()

        if self.plausi_dlg.exec_():
            # Read from form and save to config
            QKan.config.plausi.themen = self.plausi_dlg.selected_themes()       # alternativ auch aus self.plausi_dlg.lw_themen zu entnehmen.
            QKan.config.plausi.keepdata = self.plausi_dlg.cb_keepdata.isChecked()

            QKan.config.save()

            self._doplausi(self.db_qkan)

    def _doplausi(self, db_test: DBConnection = None) -> bool:
        """Start der Plausibilitätsabragen

        Einspringpunkt für Test
        """

        self.log.info("QKan: Plausibilitätsabragen")
        
        # Nur für Test: Datenbankverbindung zur Testdatenbank herstellen
        if db_test:
            self.db_qkan = db_test

        plau = PlausiTask(self.db_qkan)
        plau.run()

        del self.db_qkan
        self.log.debug("Closed DB")

        # Anzeige der Attributtabelle, nicht im Testmodus
        if not db_test:
            layers = project.mapLayersByName("Fehlerliste")
            if not layers:
                self.log.warning('Layer "Fehlerliste" fehlt!')
                return True
            self.iface.showAttributeTable(layers[0])

        return True

