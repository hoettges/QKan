from qgis.core import Qgis, QgsCoordinateReferenceSystem
from qgis.gui import QgisInterface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
from .application_dialog import ZustandDialog
from .zustandsklassen_funkt import Zustandsklassen_funkt


class Zustandsklassen(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.import_dlg = ZustandDialog(default_dir=self.default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/zustandsklassen/res/icon_zustandsklassen.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Zustandsklassen ermitteln"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.import_dlg.close()

    def run_import(self) -> None:
        """Anzeigen des Importformulars Zustandsklassen und anschließender Start der Ermittlung der Zustandsklassen"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.database.qkan = self.import_dlg.db.text()
            QKan.config.zustand.date =  self.import_dlg.date.currentText()

            check_cb = {}
            check_cb['cb1'] = self.import_dlg.checkBox.isChecked()
            check_cb['cb2'] = self.import_dlg.checkBox_2.isChecked()
            check_cb['cb3'] = self.import_dlg.checkBox_3.isChecked()
            check_cb['cb4'] = self.import_dlg.checkBox_4.isChecked()
            check_cb['cb5'] = self.import_dlg.checkBox_5.isChecked()
            check_cb['cb6'] = self.import_dlg.checkBox_6.isChecked()
            check_cb['cb7'] = self.import_dlg.checkBox_7.isChecked()
            check_cb['cb8'] = self.import_dlg.checkBox_8.isChecked()
            check_cb['cb9'] = self.import_dlg.checkBox_9.isChecked()
            check_cb['cb10'] = self.import_dlg.checkBox_10.isChecked()
            check_cb['cb11'] = self.import_dlg.checkBox_11.isChecked()
            check_cb['cb12'] = self.import_dlg.checkBox_12.isChecked()
            check_cb['cb13'] = self.import_dlg.checkBox_13.isChecked()
            check_cb['cb14'] = self.import_dlg.checkBox_14.isChecked()
            check_cb['cb15'] = self.import_dlg.checkBox_15.isChecked()
            check_cb['cb16'] = self.import_dlg.checkBox_16.isChecked()
            check_cb['cb17'] = self.import_dlg.checkBox_17.isChecked()
            check_cb['cb18'] = self.import_dlg.checkBox_18.isChecked()

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
        check_cb['cb1'] = self.import_dlg.checkBox.isChecked()
        check_cb['cb2'] = self.import_dlg.checkBox_2.isChecked()
        check_cb['cb3'] = self.import_dlg.checkBox_3.isChecked()
        check_cb['cb4'] = self.import_dlg.checkBox_4.isChecked()
        check_cb['cb5'] = self.import_dlg.checkBox_5.isChecked()
        check_cb['cb6'] = self.import_dlg.checkBox_6.isChecked()
        check_cb['cb7'] = self.import_dlg.checkBox_7.isChecked()
        check_cb['cb8'] = self.import_dlg.checkBox_8.isChecked()
        check_cb['cb9'] = self.import_dlg.checkBox_9.isChecked()
        check_cb['cb10'] = self.import_dlg.checkBox_10.isChecked()
        check_cb['cb11'] = self.import_dlg.checkBox_11.isChecked()
        check_cb['cb12'] = self.import_dlg.checkBox_12.isChecked()
        check_cb['cb13'] = self.import_dlg.checkBox_13.isChecked()
        check_cb['cb14'] = self.import_dlg.checkBox_14.isChecked()
        check_cb['cb15'] = self.import_dlg.checkBox_15.isChecked()
        check_cb['cb16'] = self.import_dlg.checkBox_16.isChecked()
        check_cb['cb17'] = self.import_dlg.checkBox_17.isChecked()
        check_cb['cb18'] = self.import_dlg.checkBox_18.isChecked()

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
        zustand = Zustandsklassen_funkt(
            check_cb,
            QKan.config.database.qkan,
            QKan.config.zustand.date,
            QKan.config.epsg,
        )
        zustand.run()
        del zustand

        # TODO: Some layers don't have a valid EPSG attached or wrong coordinates
        return True
