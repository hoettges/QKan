import os
import shutil
from pathlib import Path

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from qkan import QKan, enums, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import read_qml, eval_node_types, fehlermeldung
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from ._import import ImportTask
from .application_dialog import ImportDialog

# noinspection PyUnresolvedReferences
from . import resources

# logger = logging.getLogger("QKan.strakat.application")


class StrakatPorter(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"StrakatPorter: default_dir: {default_dir}")

        self.import_dlg = ImportDialog(default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/strakatporter/res/icon_import.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus STRAKAT"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.import_dlg.close()

    def run_import(self) -> None:
        """Anzeigen des Importformulars STRAKAT und anschließender Start des Import aus einer STRAKAT-Datenbank"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.database.qkan = self.import_dlg.tf_database.text()
            QKan.config.project.file = self.import_dlg.tf_project.text()
            QKan.config.strakat.import_dir = self.import_dlg.tf_import.text()

            QKan.config.check_import.haltungen = (self.import_dlg.cb_haltungen.isChecked())
            QKan.config.check_import.schaechte = (self.import_dlg.cb_schaechte.isChecked())
            QKan.config.check_import.hausanschluesse = (self.import_dlg.cb_hausanschluesse.isChecked())
            QKan.config.check_import.schachtschaeden = (self.import_dlg.cb_schachtschaeden.isChecked())
            QKan.config.check_import.haltungsschaeden = (self.import_dlg.cb_haltungsschaeden.isChecked())

            QKan.config.check_import.abflussparameter = (self.import_dlg.cb_abflussparameter.isChecked())
            QKan.config.check_import.rohrprofile = (self.import_dlg.cb_rohrprofile.isChecked())
            QKan.config.check_import.bodenklassen = (self.import_dlg.cb_bodenklassen.isChecked())

            QKan.config.check_import.testmodus = (self.import_dlg.cb_testmodus.isChecked())

            QKan.config.check_import.allrefs = (self.import_dlg.cb_allrefs.isChecked())

            if not QKan.config.strakat.import_dir:
                fehlermeldung("Fehler beim Import", "Es wurde kein Verzeichnis ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde kein Verzeichnis ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                crs: QgsCoordinateReferenceSystem = self.import_dlg.pw_epsg.crs()

                try:
                    epsg = int(crs.postgisSrid())
                except ValueError:
                    # TODO: Reporting this to the user might be preferable
                    self.log.exception(
                        "Failed to parse selected CRS %s\nauthid:%s\n"
                        "description:%s\nproj:%s\npostgisSrid:%s\nsrsid:%s\nacronym:%s",
                        crs,
                        crs.authid(),
                        crs.description(),
                        crs.findMatchingProj(),
                        crs.postgisSrid(),
                        crs.srsid(),
                        crs.ellipsoidAcronym(),
                    )
                else:
                    # TODO: This should all be run in a QgsTask to prevent the main
                    #  thread/GUI from hanging. However this seems to either not work
                    #  or crash QGIS currently. (QGIS 3.10.3/0e1f846438)
                    QKan.config.epsg = epsg

                    QKan.config.save()

                    self._doimport()


    def _doimport(self) -> bool:
        """Start des Import aus einer STRAKAT-Datenbank

        Einspringpunkt für Test
        """

        self.log.info("Creating DB")
        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung(
                    "Fehler im STRAKAT-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im STRAKAT-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )
                return False

            #
            # sql = 'SELECT count(*) AS anz FROM he.Rohr'
            # db_qkan.sql(sql)
            # datatest = db_qkan.fetchone()
            # self.log.debug(f"Testdaten:\n{datatest}")
            #
            #
            self.log.info("DB creation finished, starting importer")
            imp = ImportTask(db_qkan)
            imp.run()
            del imp

            eval_node_types(db_qkan)  # in qkan.database.qkan_utils

            # Write and load new project file, only if new project
            if QgsProject.instance().fileName() == '':
                QKan.config.project.template = str(
                    Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
                )
                qgsadapt(
                    QKan.config.database.qkan,
                    db_qkan,
                    QKan.config.project.file,
                    QKan.config.project.template,
                    QKan.config.epsg,
                )

                # Load generated project
                # noinspection PyArgumentList
                project = QgsProject.instance()
                project.read(QKan.config.project.file)
                project.reloadAllLayers()

        self.log.debug("Closed DB")

        return True

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""

        help_file = "https://qkan.eu/Qkan_allgemein.html?highlight=strakat"
        os.startfile(help_file)

































