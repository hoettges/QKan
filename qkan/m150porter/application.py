from pathlib import Path

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt
from qkan.tools.qkan_utils import loadLayer, zoomAll

from ._export import ExportTask
from ._import import ImportTask
from .application_dialog import ExportDialog, ImportDialog

from qkan.utils import get_logger, QkanDbError

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401

logger = get_logger("QKan.m150.application")

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
            text=self.tr("Import aus DWA-150-XML"),
            toolbar='QKan-Datenaustausch',
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

        icon_export = ":/plugins/qkan/m150porter/res/icon_export.png"
        QKan.instance.add_action(
            icon_export,
            text=self.tr("Export nach DWA-150-XML"),
            toolbar='QKan-Datenaustausch',
            callback=self.run_export,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.export_dlg.close()
        self.import_dlg.close()

    def run_export(self) -> None:
        """Anzeigen des Exportformulars und anschließender Start des Exports in eine M150-XML-Datei"""

        # noinspection PyArgumentList
        if not self.export_dlg.prepareDialog(self.iface):
            return

        # Formular anzeigen
        self.export_dlg.show()

        # Fill dialog with current info
        # get_database_QKan()
        # self.database_name = QKan.config.database.qkan
        # if self.database_name:
        #     self.export_dlg.tf_database.setText(self.database_name)
        #
        if self.export_dlg.exec_():
            export_file = self.export_dlg.tf_export.text()
            self.database_name = self.export_dlg.tf_database.text()

            # Save to config
            QKan.config.database.qkan = str(self.database_name)
            QKan.config.xml.export_file = export_file

            QKan.config.check_export.schaechte = (
                self.export_dlg.cb_export_schaechte.isChecked()
            )
            QKan.config.check_export.auslaesse = (
                self.export_dlg.cb_export_auslaesse.isChecked()
            )
            QKan.config.check_export.speicher = (
                self.export_dlg.cb_export_speicher.isChecked()
            )
            QKan.config.check_export.haltungen = (
                self.export_dlg.cb_export_haltungen.isChecked()
            )
            QKan.config.check_export.anschlussleitungen = (
                self.export_dlg.cb_export_anschlussleitungen.isChecked()
            )
            QKan.config.check_export.pumpen = (
                self.export_dlg.cb_export_pumpen.isChecked()
            )
            QKan.config.check_export.wehre = (
                self.export_dlg.cb_export_wehre.isChecked()
            )
            QKan.config.check_export.includeMissingKeys = (
                self.export_dlg.cb_includeMissingKeys.isChecked()
            )
            QKan.config.selections.selectedObjects = (
                self.export_dlg.cb_selectedObjects.isChecked()
            )
            QKan.config.check_export.cutNames = (
                self.export_dlg.cb_cutNames.isChecked()
            )
            if self.export_dlg.rb_mnn.isChecked():
                QKan.config.check_export.hoehensystem = enums.Hoehensystem.METER_UEBER_NN
            elif self.export_dlg.rb_nhn.isChecked():
                QKan.config.check_export.hoehensystem = enums.Hoehensystem.NORMAL_HOEHENNULL
            else:
                logger.error_code("Hoehensystem not recognized")

            QKan.config.save()

            self._doexport()

    def _doexport(self):
        """Start des Export in eine M150-XML-Datei

        Einspringpunkt für Test
        """

        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:
            if not db_qkan.connected:
                self.log.error(
                    "Fehler im XML-Export\n"
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                raise Exception(f"{self.__class__.__name__}: {QKan.config.database.qkan} wurde nicht gefunden!")

            # Run export
            ExportTask(db_qkan, QKan.config.xml.export_file).run()

    def run_import(self) -> None:
        """Anzeigen des Importformulars ISYBAU-XML und anschließender Start des Import"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.database.qkan = self.import_dlg.tf_database.text()
            QKan.config.project.file = self.import_dlg.tf_project.text()
            QKan.config.xml.data_choice = self.import_dlg.comboBox_2.currentText()
            QKan.config.fotoPathCurrent = self.import_dlg.tf_ordnerFotos.text()
            QKan.config.videoPathCurrent = self.import_dlg.tf_ordnervideo.text()
            #QKan.config.fotoRootPath = self.dlgop.tf_fotopath.text()
            #QKan.config.videoRootPath = self.dlgop.tf_videopath.text()

            QKan.config.xml.import_stamm = self.import_dlg.cb_impStamm.isChecked()
            QKan.config.xml.import_zustand = self.import_dlg.cb_zustand.isChecked()
            QKan.config.xml.import_haus = self.import_dlg.cb_impAnschluesse.isChecked()

            QKan.config.save()

            QKan.config.xml.import_file = self.import_dlg.tf_import.text()
            if not QKan.config.xml.import_file:
                self.log.error_data("Fehler beim Import: Es wurde keine Datei ausgewählt!")
                raise QkanDbError
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

        self.log.info("Creating DB")

        iface = QKan.instance.iface

        with DBConnection(
                dbname=QKan.config.database.qkan, epsg=QKan.config.epsg
        ) as db_qkan:
            if not db_qkan.connected:
                self.log.error_data(
                    "Fehler im M150-Import: "
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                raise QkanDbError

            self.log.info("DB creation finished, starting importer")
            imp = ImportTask(
                db_qkan
            )
            knotentypen_uncomplete = imp.run()
            del imp

            # eval_node_types(db_qkan)  # in qkan.database.qkan_utils

            # Write and load new project file, only if new project
            project = QgsProject.instance()
            if project.fileName() == '':
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
                project.read(QKan.config.project.file)
                project.reloadAllLayers()

            # Layer mit M150-Referenztabelle hinzufügen
            grouppath = [
                enums.LAYERBEZ.QKAN_GROUP.value,
                enums.LAYERBEZ.REFERENZTABELLEN_GROUP.value,
                enums.LAYERBEZ.M150_GROUP.value,
            ]

            loadLayer(
                layerbez=   enums.LAYERBEZ.M150_KNOTENARTEN.value,
                table=      "refdata",
                geom_column=None,
                qmlfile=    "qkan_m150_knotenarten.qml",
                filter=     "modul = 'm150porter' AND subject = 'import_knotentypen'",
                uifile=     "qkan_m150_knotenarten.ui",
                group=      grouppath
            )
            project.write()
            if knotentypen_uncomplete:
                msg = ('\n\nIn der M150-Datei sind individuelle Knotentypen definiert. Vor einem Import muss \n'
                       'in der Referenztabelle "M150 Knotenarten" der QKan-Schachttyp ausgewählt werden. \n\n'
                       'Anschließend muss der Import neu gestartet werden. \n(siehe <a href='
                       '"https://qkan.eu/versionen/new/QKan_XML.html#start-des-importes">QKan Dokumentation</a>)!\n\n'
                       )
                self.log.warning_user(msg)

                # Attributtabelle zur Bearbeitung anzeigen
                layer = project.mapLayersByName(enums.LAYERBEZ.M150_KNOTENARTEN.value,)[0]
                iface.showAttributeTable(layer)


        self.log.debug("Closed DB")

        return True
