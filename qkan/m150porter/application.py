from pathlib import Path

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from ._export import ExportTask
from ._import import ImportTask
from .application_dialog import ExportDialog, ImportDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class M150Porter(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.export_dlg = ExportDialog(default_dir=self.default_dir, tr=self.tr)
        self.import_dlg = ImportDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/m150porter/res/icon_import.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus DWA-XML"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.export_dlg.close()
        self.import_dlg.close()

    def run_export(self) -> None:
        self.export_dlg.show()

        # Fill dialog with current info
        self.database_name, _ = get_database_QKan()
        if self.database_name:
            self.export_dlg.tf_database.setText(self.database_name)

        if self.export_dlg.exec_():
            export_file = self.export_dlg.tf_export.text()
            self.database_name = self.export_dlg.tf_database.text()

            # Save to config
            QKan.config.database.qkan = str(self.database_name)
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
            QKan.config.check_export.export_anschlussleitungen = (
                self.export_dlg.cb_export_anschlussleitungen.isChecked()
            )
            QKan.config.check_export.export_pumpen = (
                self.export_dlg.cb_export_pumpen.isChecked()
            )
            QKan.config.check_export.export_wehre = (
                self.export_dlg.cb_export_wehre.isChecked()
            )

            QKan.config.save()

            with DBConnection(self.database_name) as db_qkan:
                if not db_qkan.connected:
                    fehlermeldung(
                        "Fehler im XML-Export",
                        f"QKan-Datenbank {self.database_name} wurde nicht gefunden!\nAbbruch!",
                    )
                    self.iface.messageBar().pushMessage(
                        "Fehler im XML-Export",
                        f"QKan-Datenbank {self.database_name} wurde nicht gefunden!\nAbbruch!",
                        level=Qgis.Critical,
                    )
                    return

                # Run export
                ExportTask(db_qkan, export_file).run()

    def run_import(self) -> None:
        """Anzeigen des Importformulars ISYBAU-XML und anschließender Start des Import"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.database.qkan = self.import_dlg.tf_database.text()
            QKan.config.project.file = self.import_dlg.tf_project.text()
            QKan.config.xml.richt_choice = self.import_dlg.comboBox.currentText()
            QKan.config.xml.data_choice = self.import_dlg.comboBox_2.currentText()
            QKan.config.xml.ordner_bilder = self.import_dlg.tf_import_2.text()
            QKan.config.xml.ordner_video = self.import_dlg.tf_import_3.text()

            QKan.config.xml.import_stamm = (
                self.import_dlg.checkBox.isChecked()
            )

            QKan.config.xml.import_haus = (
                self.import_dlg.checkBox_2.isChecked()
            )

            QKan.config.xml.import_zustand = (
                self.import_dlg.checkBox_3.isChecked()
            )

            QKan.config.save()

            QKan.config.xml.import_file = self.import_dlg.tf_import.text()
            if not QKan.config.xml.import_file:
                fehlermeldung("Fehler beim Import", "Es wurde keine Datei ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde keine Datei ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                crs: QgsCoordinateReferenceSystem = self.import_dlg.epsg.crs()

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
        """Start des Import aus einer ISYBAU-XML-Datei

        Einspringpunkt für Test
        """
        QKan.config.xml.richt_choice = self.import_dlg.comboBox.currentText()
        QKan.config.xml.data_choice = self.import_dlg.comboBox_2.currentText()
        QKan.config.xml.ordner_bild = self.import_dlg.tf_import_2.text()
        QKan.config.xml.ordner_video = self.import_dlg.tf_import_3.text()

        self.log.info("Creating DB")
        with DBConnection(
                dbname=QKan.config.database.qkan, epsg=QKan.config.epsg
        ) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung(
                    "Fehler im XML-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im XML-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )
                return False

            self.log.info("DB creation finished, starting importer")
            imp = ImportTask(
                db_qkan,
                QKan.config.xml.import_file,
                QKan.config.xml.richt_choice,
                QKan.config.xml.data_choice,
                QKan.config.xml.ordner_bild,
                QKan.config.xml.ordner_video
            )
            imp.run()
            del imp

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

            # TODO: Some layers don't have a valid EPSG attached or wrong coordinates

        self.log.debug("Closed DB")

        return True
