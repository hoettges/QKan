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

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.tools.k_qgsadapt import qgsadapt

# noinspection PyUnresolvedReferences
from . import resources
from ._export import ExportTask
from ._import import ImportTask
from .application_dialog import ExportDialog, ImportDialog

logger = logging.getLogger("QKan.he8.application")


class He8Porter:
    def __init__(self, iface: QgisInterface):
        self.iface = iface

        # noinspection PyArgumentList
        project_path = QgsProject.instance().fileName()
        if project_path:
            self.default_dir = Path(project_path).parent
        else:
            self.default_dir = Path(QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[-1])

        self.export_dlg = ExportDialog(default_dir=self.default_dir, tr=self.tr)
        self.import_dlg = ImportDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyCallByClass, PyArgumentList
        return QCoreApplication.translate("he8", message)

    # noinspection PyPep8Naming
    def initGui(self):
        icon_export = ":/plugins/qkan/he8porter/res/icon_export.png"
        QKan.instance.add_action(
            icon_export,
            text=self.tr("Export in HE8"),
            callback=self.run_export,
            parent=self.iface.mainWindow(),
        )
        icon_import = ":/plugins/qkan/he8porter/res/icon_import.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus HE8"),
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

            # Read from form and save to config
            QKan.config.database.qkan = database_qkan = self.export_dlg.tf_database.text()
            QKan.config.he8.export_file = export_file = self.export_dlg.tf_export.text()

            QKan.config.check_export.export_schaechte = self.export_dlg.cb_export_schaechte.isChecked()
            QKan.config.check_export.export_auslaesse = self.export_dlg.cb_export_auslaesse.isChecked()
            QKan.config.check_export.export_speicher = self.export_dlg.cb_export_speicher.isChecked()
            QKan.config.check_export.export_haltungen = self.export_dlg.cb_export_haltungen.isChecked()
            QKan.config.check_export.export_pumpen = self.export_dlg.cb_export_pumpen.isChecked()
            QKan.config.check_export.export_wehre = self.export_dlg.cb_export_wehre.isChecked()

            QKan.config.save()

            db_qkan = DBConnection(dbname=database_qkan)
            if not db_qkan:
                fehlermeldung(
                    "Fehler im HE8-Export",
                    f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im HE8-Export",
                    f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )
                return False

            # Attach SQLite-Database with HE8 Data
            sql = f'ATTACH DATABASE "{export_file}" AS he'
            if not db_qkan.sql(sql, "He8Porter.run_export_to_he8 Attach HE8"):
                return False

            # Run export
            ExportTask(db_qkan).run()

    def run_import(self):
        self.import_dlg.show()

        if self.import_dlg.exec_():

            # Read from form and save to config
            QKan.config.database.qkan = database_qkan = self.import_dlg.tf_database.text()
            QKan.config.project.file = project_file = self.import_dlg.tf_project.text()
            QKan.config.he8.import_file = import_file = self.import_dlg.tf_import.text()

            QKan.config.check_import.haltungen = self.import_dlg.cb_haltungen.isChecked()
            QKan.config.check_import.schaechte = self.import_dlg.cb_schaechte.isChecked()
            QKan.config.check_import.auslaesse = self.import_dlg.cb_auslaesse.isChecked()
            QKan.config.check_import.speicher = self.import_dlg.cb_speicher.isChecked()
            QKan.config.check_import.pumpen = self.import_dlg.cb_pumpen.isChecked()
            QKan.config.check_import.wehre = self.import_dlg.cb_wehre.isChecked()
            QKan.config.check_import.rohrprofile = self.import_dlg.cb_rohrprofile.isChecked()
            QKan.config.check_import.regenschreiber = self.import_dlg.cb_regenschreiber.isChecked()
            QKan.config.check_import.abflussparameter = self.import_dlg.cb_abflussparameter.isChecked()
            QKan.config.check_import.bodenklassen = self.import_dlg.cb_bodenklassen.isChecked()
            QKan.config.check_import.einleitdirekt = self.import_dlg.cb_einleitdirekt.isChecked()
            QKan.config.check_import.aussengebiete = self.import_dlg.cb_aussengebiete.isChecked()

            QKan.config.check_import.tezg_ef = self.import_dlg.cb_tezg_ef.isChecked()
            QKan.config.check_import.tezg_hf = self.import_dlg.cb_tezg_hf.isChecked()
            QKan.config.check_import.tezg_tf = self.import_dlg.cb_tezg_tf.isChecked()

            QKan.config.check_import.append = self.import_dlg.rb_append.isChecked()
            QKan.config.check_import.update = self.import_dlg.rb_update.isChecked()
            QKan.config.check_import.synch = self.import_dlg.rb_synch.isChecked()

            QKan.config.save()

            if not import_file:
                fehlermeldung("Fehler beim Import", "Es wurde keine Datei ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde keine Datei ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                crs: QgsCoordinateReferenceSystem = self.import_dlg.pw_epsg.crs()

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
                        dbname=database_qkan, epsg=QKan.config.epsg
                    )

                    if not db_qkan:
                        fehlermeldung(
                            "Fehler im HE8-Import",
                            f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                        )
                        self.iface.messageBar().pushMessage(
                            "Fehler im HE8-Import",
                            f"QKan-Datenbank {database_qkan} wurde nicht gefunden!\nAbbruch!",
                            level=Qgis.Critical,
                        )
                        return

                    # Attach SQLite-Database with HE8 Data
                    sql = f'ATTACH DATABASE "{import_file}" AS he'
                    if not db_qkan.sql(sql, "He8Porter.run_import_to_he8 Attach HE8"):
                        return False

                    logger.info("DB creation finished, starting importer")
                    imp = ImportTask(db_qkan)
                    imp.run()
                    
                    del db_qkan
                    logger.debug("Closed DB")

                    # TODO: Replace with QKan.config.project.template?
                    template_project = (
                        Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
                    )
                    qgsadapt(
                        str(template_project), database_qkan, QKan.config.project.file, epsg
                    )

                    # Load generated project
                    # noinspection PyArgumentList
                    project = QgsProject.instance()
                    project.read(QKan.config.project.file)
                    project.reloadAllLayers()
                    # TODO: Some layers don't have a valid EPSG attached or wrong coordinates
