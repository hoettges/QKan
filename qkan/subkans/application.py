from pathlib import Path

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from .subkans_funkt import Subkans_funkt
from .application_dialog import SubkansDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class subkans(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.import_dlg = SubkansDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/subkans/res/icon_subkans.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Substanzklassen ermitteln"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.import_dlg.close()


    def run_import(self) -> None:
        """Anzeigen des Importformulars Substanzklassen und anschließender Start der Ermittlung der Substanzklassen"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.database.qkan = self.import_dlg.db.text()
            QKan.config.zustand.date =  self.import_dlg.date.currentText()

            check_cb = {}
            check_cb['cb1'] = self.import_dlg.checkBox_1.isChecked()
            check_cb['cb2'] = self.import_dlg.checkBox_2.isChecked()
            check_cb['cb3'] = self.import_dlg.checkBox_3.isChecked()
            check_cb['cb4'] = self.import_dlg.checkBox_4.isChecked()
            check_cb['cb5'] = self.import_dlg.checkBox_5.isChecked()

            QKan.config.save()


            if not QKan.config.database.qkan:
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
        """Start der Zustandsklassenbewertung

        Einspringpunkt für Test
        """
        QKan.config.database.qkan = self.import_dlg.db.text()
        QKan.config.zustand.date = self.import_dlg.date.currentText()

        check_cb = {}
        check_cb['cb1'] = self.import_dlg.checkBox_1.isChecked()
        check_cb['cb2'] = self.import_dlg.checkBox_2.isChecked()
        check_cb['cb3'] = self.import_dlg.checkBox_3.isChecked()
        check_cb['cb4'] = self.import_dlg.checkBox_4.isChecked()
        check_cb['cb5'] = self.import_dlg.checkBox_5.isChecked()

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

        self.log.info("DB creation finished, starting Zustandsklassen")
        subkans = Subkans_funkt(check_cb, QKan.config.database.qkan, QKan.config.zustand.date, QKan.config.epsg)
        subkans.run()
        del subkans

        # TODO: Some layers don't have a valid EPSG attached or wrong coordinates
        return True
