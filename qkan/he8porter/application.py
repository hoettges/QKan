import os
import shutil
from pathlib import Path

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory
from qkan import QKan, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from ._export import ExportTask
from ._import import ImportTask
from .application_dialog import ExportDialog, ImportDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class He8Porter(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"He8Porter: default_dir: {default_dir}")
        self.export_dlg = ExportDialog(default_dir, tr=self.tr)
        self.import_dlg = ImportDialog(default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_export = ":/plugins/qkan/he8porter/res/icon_export.png"
        QKan.instance.add_action(
            icon_export,
            text=self.tr("Export nach Hystem-Extran 8"),
            callback=self.run_export,
            parent=self.iface.mainWindow(),
        )
        icon_import = ":/plugins/qkan/he8porter/res/icon_import.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus Hystem-Extran 8"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.export_dlg.close()
        self.import_dlg.close()

    def run_export(self) -> None:
        """Anzeigen des Exportformulars und anschließender Start des Exports in eine HE8-Datenbank"""

        # noinspection PyArgumentList
        project_path = QgsProject.instance().fileName()

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        teilgebiete = QKan.config.selections.teilgebiete

        self.export_dlg.connectQKanDB(project_path, teilgebiete)

        # Formular anzeigen
        self.export_dlg.show()

        # Im Formular wurde [OK] geklickt
        if self.export_dlg.exec_():

            # Read from form and save to config
            QKan.config.he8.database = (
                database_qkan
            ) = self.export_dlg.tf_database.text()
            QKan.config.he8.export_file = (
                database_he
            ) = self.export_dlg.tf_exportdb.text()
            QKan.config.he8.template = templatedb = self.export_dlg.tf_template.text()

            QKan.config.check_export.haltungen = (
                self.export_dlg.cb_haltungen.isChecked()
            )
            QKan.config.check_export.schaechte = (
                self.export_dlg.cb_schaechte.isChecked()
            )
            QKan.config.check_export.auslaesse = (
                self.export_dlg.cb_auslaesse.isChecked()
            )
            QKan.config.check_export.speicher = self.export_dlg.cb_speicher.isChecked()
            QKan.config.check_export.pumpen = self.export_dlg.cb_pumpen.isChecked()
            QKan.config.check_export.wehre = self.export_dlg.cb_wehre.isChecked()
            QKan.config.check_export.flaechen = self.export_dlg.cb_flaechen.isChecked()
            QKan.config.check_export.rohrprofile = (
                self.export_dlg.cb_rohrprofile.isChecked()
            )
            QKan.config.check_export.abflussparameter = (
                self.export_dlg.cb_abflussparameter.isChecked()
            )
            QKan.config.check_export.bodenklassen = (
                self.export_dlg.cb_bodenklassen.isChecked()
            )
            QKan.config.check_export.einleitdirekt = (
                self.export_dlg.cb_einleitdirekt.isChecked()
            )
            QKan.config.check_export.aussengebiete = (
                self.export_dlg.cb_aussengebiete.isChecked()
            )
            QKan.config.check_export.einzugsgebiete = (
                self.export_dlg.cb_einzugsgebiete.isChecked()
            )
            QKan.config.check_export.tezg = self.export_dlg.cb_tezg.isChecked()

            QKan.config.check_export.append = self.export_dlg.rb_append.isChecked()
            QKan.config.check_export.update = self.export_dlg.rb_update.isChecked()

            teilgebiete = [
                _.text() for _ in self.export_dlg.lw_teilgebiete.selectedItems()
            ]
            QKan.config.selections.teilgebiete = teilgebiete

            QKan.config.save()

            # Zieldatenbank aus Vorlage kopieren
            if os.path.exists(templatedb):
                try:
                    shutil.copyfile(templatedb, database_he)
                except BaseException:
                    fehlermeldung(
                        "Fehler in Export nach HE8",
                        "Fehler beim Kopieren der Vorlage: \n   {self.templatedb}\n"
                        + "nach Ziel: {self.database_he}\n",
                    )

            self.export_dlg.connectHEDB(database_he)

            # Run export
            ExportTask(self.export_dlg.dbQK, teilgebiete).run()

            # Close connection
            del self.export_dlg.dbQK
            self.log.debug("Closed DB")

    def run_import(self) -> None:
        """Anzeigen des Importformulars HE8 und anschließender Start des Import aus einer HE8-Datenbank"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.he8.database = (
                database_qkan_import
            ) = self.import_dlg.tf_database.text()
            QKan.config.project.file = project_file = self.import_dlg.tf_project.text()
            QKan.config.he8.import_file = import_file = self.import_dlg.tf_import.text()

            QKan.config.check_import.haltungen = (
                self.import_dlg.cb_haltungen.isChecked()
            )
            QKan.config.check_import.schaechte = (
                self.import_dlg.cb_schaechte.isChecked()
            )
            QKan.config.check_import.auslaesse = (
                self.import_dlg.cb_auslaesse.isChecked()
            )
            QKan.config.check_import.speicher = self.import_dlg.cb_speicher.isChecked()
            QKan.config.check_import.pumpen = self.import_dlg.cb_pumpen.isChecked()
            QKan.config.check_import.wehre = self.import_dlg.cb_wehre.isChecked()
            QKan.config.check_import.flaechen = self.import_dlg.cb_flaechen.isChecked()
            QKan.config.check_import.rohrprofile = (
                self.import_dlg.cb_rohrprofile.isChecked()
            )
            QKan.config.check_import.abflussparameter = (
                self.import_dlg.cb_abflussparameter.isChecked()
            )
            QKan.config.check_import.bodenklassen = (
                self.import_dlg.cb_bodenklassen.isChecked()
            )
            QKan.config.check_import.einleitdirekt = (
                self.import_dlg.cb_einleitdirekt.isChecked()
            )
            QKan.config.check_import.aussengebiete = (
                self.import_dlg.cb_aussengebiete.isChecked()
            )
            QKan.config.check_import.einzugsgebiete = (
                self.import_dlg.cb_einzugsgebiete.isChecked()
            )

            QKan.config.check_import.tezg_ef = self.import_dlg.cb_tezg_ef.isChecked()
            QKan.config.check_import.tezg_hf = self.import_dlg.cb_tezg_hf.isChecked()
            QKan.config.check_import.tezg_tf = self.import_dlg.cb_tezg_tf.isChecked()

            QKan.config.check_import.append = self.import_dlg.rb_append.isChecked()
            QKan.config.check_import.update = self.import_dlg.rb_update.isChecked()

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

                    self.log.info("Creating DB")
                    db_qkan_import = DBConnection(
                        dbname=database_qkan_import, epsg=QKan.config.epsg
                    )

                    if not db_qkan_import:
                        fehlermeldung(
                            "Fehler im HE8-Import",
                            f"QKan-Datenbank {database_qkan_import} wurde nicht gefunden!\nAbbruch!",
                        )
                        self.iface.messageBar().pushMessage(
                            "Fehler im HE8-Import",
                            f"QKan-Datenbank {database_qkan_import} wurde nicht gefunden!\nAbbruch!",
                            level=Qgis.Critical,
                        )
                        return

                    # Attach SQLite-Database with HE8 Data
                    sql = f'ATTACH DATABASE "{import_file}" AS he'
                    if not db_qkan_import.sql(
                        sql, "He8Porter.run_import_to_he8 Attach HE8"
                    ):
                        return

                    self.log.info("DB creation finished, starting importer")
                    imp = ImportTask(db_qkan_import)
                    imp.run()

                    # TODO: Replace with QKan.config.project.template?
                    template_project = (
                        Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
                    )
                    qgsadapt(
                        str(template_project),
                        database_qkan_import,
                        db_qkan_import,
                        QKan.config.project.file,
                        epsg,
                    )

                    del db_qkan_import
                    self.log.debug("Closed DB")

                    # Load generated project
                    # noinspection PyArgumentList
                    project = QgsProject.instance()
                    project.read(QKan.config.project.file)
                    project.reloadAllLayers()
                    # TODO: Some layers don't have a valid EPSG attached or wrong coordinates
