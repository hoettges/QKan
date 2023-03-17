from pathlib import Path

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory,iface
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

import matplotlib.dates as mdates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from qgis.PyQt.QtWidgets import QWidget, QCheckBox, QFileDialog

from ._laengsschnitt import LaengsTask
from .application_dialog import LaengsDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip
from PyQt5.QtWidgets import *


class Laengsschnitt(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.laengs_dlg = None
        self.db_qkan: DBConnection = None
        self.auswahl={}
        #self.get_widget()

        #self.laengs_dlg.refresh_function = self.refresh_function
        #self.laengs_dlg.export_cad_function = self.export_cad_function

    def refresh_function(self, database, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg):
        LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg).zeichnen()
        canv.draw()

        return LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg).zeichnen()


    def export_cad_function(self,database, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg):
        LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg).cad()

    def show_function(self,database, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg):
        LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg).show()

    def gang_function(self, database, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg):
        LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, selected, auswahl, point, massstab, features, db_erg).ganglinie()


    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon = ":/plugins/qkan/laengsschnitt/res/laengsschnitt.png"
        QKan.instance.add_action(
            icon,
            text=self.tr("Laengsschnitt"),
            callback=self.run_laengs,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        if self.laengs_dlg is None:
            return
        else:
            self.laengs_dlg.close()

    def get_widget(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.laengs_dlg
        self.dialog.fig = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv = FigureCanvas(self.dialog.fig)

        self.dialog.verticalLayout.addWidget(self.dialog.canv)
        self.dialog.verticalLayout.addWidget(NavigationToolbar(self.dialog.canv, qw, True))

    def get_widget_2(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog_2 = self.laengs_dlg
        self.dialog.fig_2 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog_2)
        self.dialog.canv_2 = FigureCanvas(self.dialog.fig_2)

        self.dialog.verticalLayout_2.addWidget(self.dialog.canv_2)
        self.dialog.verticalLayout_2.addWidget(NavigationToolbar(self.dialog.canv_2, qw, True))


    # def laengsschnitt(self) -> None:
    #     """Anzeigen des Formulares für den Längsschnitt und anschließender Erstellung"""
    #
    #     # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
    #
    #     self.laengs_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')
    #
    #     #self.laengs_dlg.show()
    #
    #     if self.laengs_dlg.exec_():
    #         # Read from form and save to config
    #
    #         QKan.config.save()
    #
    #         #Hatung auswählen!
    #         QKan.config.xml.import_file = self.laengs_dlg.tf_import.text()
    #         if not QKan.config.xml.import_file:
    #             fehlermeldung("Fehler beim Erstellen des Längsschnittes", "Es wurde keine passende Haltung ausgewählt!")
    #             self.iface.messageBar().pushMessage(
    #                 "Fehler beim Erstellen",
    #                 "Es wurde keine Haltung ausgewählt!",
    #                 level=Qgis.Critical,
    #             )
    #             return
    #         else:
    #             crs: QgsCoordinateReferenceSystem = self.laengs_dlg.epsg.crs()
    #
    #             try:
    #                 epsg = int(crs.postgisSrid())
    #             except ValueError:
    #                 # TODO: Reporting this to the user might be preferable
    #                 self.log.exception(
    #                     "Failed to parse selected CRS %s\nauthid:%s\n"
    #                     "description:%s\nproj:%s\npostgisSrid:%s\nsrsid:%s\nacronym:%s",
    #                     crs,
    #                     crs.authid(),
    #                     crs.description(),
    #                     crs.findMatchingProj(),
    #                     crs.postgisSrid(),
    #                     crs.srsid(),
    #                     crs.ellipsoidAcronym(),
    #                 )
    #             else:
    #                 # TODO: This should all be run in a QgsTask to prevent the main
    #                 #  thread/GUI from hanging. However this seems to either not work
    #                 #  or crash QGIS currently. (QGIS 3.10.3/0e1f846438)
    #                 QKan.config.epsg = epsg
    #
    #                 QKan.config.save()
    #
    #                 self._dolaengs()

    def run_laengs(self) -> None:

        #if self.laengs_dlg is not None:
        #    self.laengs_dlg.pushButton.setEnabled(False)
        #    self.laengs_dlg.pushButton_2.setEnabled(False)
        self.laengs_dlg = LaengsDialog(default_dir=self.default_dir, tr=self.tr)

        self.get_widget()
        self.get_widget_2()
        self.fig = self.dialog.fig
        self.canv = self.dialog.canv
        self.selected = self.dialog.selected
        self.auswahl = self.dialog.auswahl
        self.features = self.dialog.features
        self.fig_2 = self.dialog_2.fig_2
        self.canv_2 = self.dialog_2.canv_2
        self.db_erg = self.dialog_2.db_erg


        # Fill dialog with current info
        self.database_qkan, _ = get_database_QKan()
        self.db_qkan = DBConnection(dbname=self.database_qkan)
        self.log.debug(f"{__file__}: Datenbankverbindung wurde hergestellt...")

        self.laengs_dlg.refresh_function = self.refresh_function
        self.laengs_dlg.export_cad_function = self.export_cad_function
        self.laengs_dlg.show_function = self.show_function

        self.laengs_dlg.pushButton_2.click()
        self.laengs_dlg.show()

        self.point = self.laengs_dlg.lineEdit.text()
        self.massstab = self.laengs_dlg.lineEdit_2.text()

        if self.laengs_dlg.exec_():

            # Save to config
            QKan.config.save()

            #db_qkan = DBConnection(dbname=self.database_qkan)
            if not self.db_qkan:
                fehlermeldung(
                    "Fehler im Längsschnitt",
                    f"QKan-Datenbank {self.database_qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im Längsschnitt",
                    f"QKan-Datenbank {self.database_qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )

            # Run
            LaengsTask(self.db_qkan, self.database_qkan, self.fig, self.canv, self.fig_2, self.canv_2, self.selected, self.auswahl, self.point, self.massstab, self.features, self.db_erg).run()
