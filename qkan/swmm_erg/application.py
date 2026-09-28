from qgis.gui import QgisInterface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import get_database_QKan, get_default_dir
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
from ._SWMM_erg import ImportTask
from .application_dialog import ImportDialog
from ..utils import QkanUserError, QkanAbortError, get_logger

logger = get_logger("QKan.importswmm")


class SWMMErg(QKanPlugin):
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"SWMM_erg: default_dir: {default_dir}")
        self.import_dlg = ImportDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_import = ":/plugins/qkan/swmm_erg/res/icon_ergSWMM.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import von SWMM-Ergebnissen (*.RPT)"),
            toolbar='QKan-Datenaustausch',
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.import_dlg.close()


    def run_import(self) -> None:
        """Anzeigen des Importformulars SWMM und anschließender Start des Imports aus einer SWMM-Datei"""

        self.import_dlg.show()

        if self.import_dlg.exec():
            # Read from form and save to config
           # QKan.config.database.qkan = self.import_dlg.tf_database.text()
            #QKan.config.swmm_erg.import_file = self.import_dlg.tf_import.text()

            QKan.config.save()

            if not self.import_dlg.tf_import.text():
                logger.error_user("Es wurde keine Ergebnisdatei ausgewählt!")
                return
            else:

                QKan.config.save()

                self._doimport()


    def _doimport(self) -> bool:
        """Start des Imports aus einer SWMM-Datei

        Einspringpunkt für Test
        """
        #self.logger.info("Creating DB")

        #QKan.config.database.qkan = self.import_dlg.tf_database.text()
        #QKan.config.project.file = self.import_dlg.tf_project.text()

        get_database_QKan()
        database_qkan, epsg = QKan.config.database.qkan, QKan.config.epsg
        if not database_qkan:
            logger.error_code(
                "selection.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            raise QkanAbortError

        with DBConnection(
                dbname=database_qkan, epsg=epsg
        ) as db_qkan:
            if not db_qkan.connected:
                return False

            self.log.info("DB creation finished, starting importer")
            imp = ImportTask(self.import_dlg.tf_import.text(), db_qkan)
            try:
                imp.run()
            except QkanUserError as e:
                # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
                logger.debug(f"Anwenderfehler bei Tool SWMM Ergebnisse: {e}")
            except Exception as e:
                logger.error_code(f"Fehler bei Tool SWMM Ergebnisse: {e}")
                raise QkanAbortError
            del imp

        #self.log.debug("Closed DB")
        return True
