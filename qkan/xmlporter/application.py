import logging
from pathlib import Path

from qgis.PyQt.QtCore import QCoreApplication, QStandardPaths
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsProject,
)
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from qkan import QKan, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.tools.k_qgsadapt import qgsadapt

# noinspection PyUnresolvedReferences
from . import resources
from ._export import ExportTask
from ._import import ImportTask
from .application_dialog import ExportDialog, ImportDialog

logger = logging.getLogger("QKan.xml.application")


class XmlPorter:
    def __init__(self, iface: QgisInterface):
        self.iface = iface

        self.default_dir = get_default_dir()

        self.export_dlg = ExportDialog(default_dir=self.default_dir, tr=self.tr)
        self.import_dlg = ImportDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyCallByClass, PyArgumentList
        return QCoreApplication.translate("xml", message)

    # noinspection PyPep8Naming
    def initGui(self):
        icon_export = ":/plugins/qkan/xmlporter/res/icon_export.png"
        QKan.instance.add_action(
            icon_export,
            text=self.tr("Export in XML"),
            callback=self.run_export,
            parent=self.iface.mainWindow(),
        )
        icon_import = ":/plugins/qkan/xmlporter/res/icon_import.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus XML"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        self.export_dlg.close()
        self.import_dlg.close()

    def run_export(self):
        self.export_dlg.show()

        # Fill dialog with current info
        database_qkan, _ = get_database_QKan()
        if database_qkan:
            self.export_dlg.tf_database.setText(database_qkan)

        if self.export_dlg.exec_():
            export_file = self.export_dlg.tf_export.text()
            database_qkan = self.export_dlg.tf_database.text()

            # Save to config
            QKan.config.database.qkan = database_qkan
            QKan.config.xml.export_file = export_file

            QKan.config.check_export.export_schaechte = (
                self.export_dlg.cb_export_schaechte.isChecked()
            )
            QKan.config.check_export.export_auslaesse = (
                self.export_dlg.cb_export_auslaesse.isChecked()
            )
            QKan.config.check_export.export_speicher = (
                self.export_dlg.cb_export_speicher.isChecked()
            )
            QKan.config.check_export.export_haltungen = (
                self.export_dlg.cb_export_haltungen.isChecked()
            )
            QKan.config.check_export.export_pumpen = (
                self.export_dlg.cb_export_pumpen.isChecked()
            )
            QKan.config.check_export.export_wehre = (
                self.export_dlg.cb_export_wehre.isChecked()
            )

            QKan.config.save()

            db_qkan = DBConnection(dbname=database_qkan)
            if not db_qkan:
                fehlermeldung(
                    "Fehler im XML-Export",
                    f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im XML-Export",
                    f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )

            # Run export
            ExportTask(db_qkan, export_file).run()

    def run_import(self):
        self.import_dlg.show()

        if self.import_dlg.exec_():
            QKan.config.xml.init_database = (
                self.import_dlg.cb_import_tabinit.isChecked()
            )
            QKan.config.database.qkan = (
                database_qkan
            ) = self.import_dlg.tf_database.text()
            QKan.config.project.file = self.import_dlg.tf_project.text()

            import_file = self.import_dlg.tf_import.text()
            if not import_file:
                fehlermeldung("Fehler beim Import", "Es wurde keine Datei ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde keine Datei ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                QKan.config.xml.import_file = import_file

                crs: QgsCoordinateReferenceSystem = self.import_dlg.epsg.crs()

                try:
                    epsg = int(crs.postgisSrid())
                except ValueError:
                    # TODO: Reporting this to the user might be preferable
                    logger.exception(
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

                    logger.info("Creating DB")
                    db_qkan = DBConnection(
                        dbname=database_qkan, epsg=str(QKan.config.epsg)
                    )

                    if not db_qkan:
                        fehlermeldung(
                            "Fehler im XML-Import",
                            f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                        )
                        self.iface.messageBar().pushMessage(
                            "Fehler im XML-Import",
                            f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                            level=Qgis.Critical,
                        )
                        return

                    logger.info("DB creation finished, starting importer")
                    imp = ImportTask(db_qkan, import_file)
                    imp.run()

                    # TODO: Replace with QKan.config.project.template?
                    template_project = (
                        Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
                    )
                    qgsadapt(
                        str(template_project),
                        database_qkan,
                        QKan.config.project.file,
                        epsg=epsg,
                    )

                    # Load generated project
                    # noinspection PyArgumentList
                    project = QgsProject.instance()
                    project.read(QKan.config.project.file)
                    project.reloadAllLayers()
                    # TODO: Some layers don't have a valid EPSG attached or wrong coordinates
