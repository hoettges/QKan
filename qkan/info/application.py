from qgis.gui import QgisInterface
from qgis.core import QgsProject
from PyQt5.QtWidgets import *
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin
from qkan.database.qkan_database import qgs_version
from qkan.database.qkan_utils import warnung
from xml.etree.ElementTree import Element, SubElement, tostring
import win32com.client as w3c
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from typing import Dict, List, Optional, Union
from pathlib import Path
from xml.dom import minidom

from qkan.utils import get_logger
logger = get_logger("QKan.strakat.import")

from PyQt5.QtWidgets import QTableWidgetItem

from ._info import Info
from .application_dialog import InfoDialog

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
import pandas as pd
import os

def _create_children(parent: Element, names: List[str]) -> None:
    for child in names:
        SubElement(parent, child)


def _create_children_text(
    parent: Element, children: Dict[str, Union[str, int, None]]
) -> None:
    for name, text in children.items():
        if text is None:
            SubElement(parent, name)
        else:
            SubElementText(parent, name, str(text))


# noinspection PyPep8Naming
def SubElementText(parent: Element, name: str, text: Union[str, int]) -> Element:
    s = SubElement(parent, name)
    if text is not None:
        s.text = str(text)
    return s


class Infos(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.info_dlg = InfoDialog(default_dir=self.default_dir, tr=self.tr)
        self.info_dlg.pb_exportExcel.clicked.connect(self.run_info)
        self.info_dlg.pb_exportXML.clicked.connect(self.run_info_2)

        self.stamm: Optional[Element] = None
        self.hydraulik_objekte: Optional[Element] = None
        self.get_widget_1()
        self.get_widget_2()
        self.get_widget_3()
        self.get_widget_4()
        # self.canv_1 = None


    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/info/res/info.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Infos zum QKan Projekt"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.info_dlg.close()

    def get_widget_1(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        #layout='constrained' damit die Texte sich nicht überschneiden!
        self.dialog.fig_1 = plt.figure(layout='constrained')
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_1 = FigureCanvas(self.dialog.fig_1)

        self.dialog.verticalLayout_1.addWidget(self.dialog.canv_1)
        self.dialog.verticalLayout_1.addWidget(NavigationToolbar(self.dialog.canv_1, qw, True))

    def get_widget_2(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        self.dialog.fig_2 = plt.figure(layout='constrained')
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_2 = FigureCanvas(self.dialog.fig_2)

        self.dialog.verticalLayout_2.addWidget(self.dialog.canv_2)
        self.dialog.verticalLayout_2.addWidget(NavigationToolbar(self.dialog.canv_2, qw, True))

    def get_widget_3(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        self.dialog.fig_3 = plt.figure(layout='constrained')
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_3 = FigureCanvas(self.dialog.fig_3)

        self.dialog.verticalLayout_3.addWidget(self.dialog.canv_3)
        self.dialog.verticalLayout_3.addWidget(NavigationToolbar(self.dialog.canv_3, qw, True))

    def get_widget_4(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        self.dialog.fig_4 = plt.figure(layout='constrained')
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_4 = FigureCanvas(self.dialog.fig_4)

        self.dialog.verticalLayout_4.addWidget(self.dialog.canv_4)
        self.dialog.verticalLayout_4.addWidget(NavigationToolbar(self.dialog.canv_4, qw, True))

    def on_click(self, event):
        Info.handle_click(event, Info.anzeigen, Info.anzeigen)



    def run(self) -> None:
        # Prüfen, ob ein Projekt geladen ist
        project = QgsProject.instance()
        layers = project.mapLayers()

        self.info_dlg.select_date()
        if len(layers) > 0:

            self.fig_1 = self.dialog.fig_1
            self.canv_1 = self.dialog.canv_1
            self.fig_2 = self.dialog.fig_2
            self.canv_2 = self.dialog.canv_2
            self.fig_3 = self.dialog.fig_3
            self.canv_3 = self.dialog.canv_3
            self.fig_4 = self.dialog.fig_4
            self.canv_4 = self.dialog.canv_4

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected

            test = Info(self.fig_1, self.canv_1, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.fig_4, self.canv_4, DBConnection())
            test.run(self.info_dlg.date.currentText())

            def on_click(self, event):
                test.handle_click(event, self.pie_wedges, run_script)

            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            # self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            version = qgs_version()
            self.info_dlg.tf_qkanversion.setText(str(version))
            self.info_dlg.tf_anz_teilgeb.setText(str(test.anz_teilgeb))

            # Felder Haltungen
            if test.bew_art == 'DWA':
                self.info_dlg.comboBox.setItemText(0, 'DWA')
            if test.bew_art == 'ISYBAU':
                self.info_dlg.comboBox.setItemText(1, 'ISYBAU')
            self.info_dlg.tableWidget.setItem(0, 1, QTableWidgetItem(str(test.laenge_haltungen_rw)))
            self.info_dlg.tableWidget.setItem(1, 1, QTableWidgetItem(str(test.laenge_haltungen_sw)))
            self.info_dlg.tableWidget.setItem(2, 1, QTableWidgetItem(str(test.laenge_haltungen_mw)))

            self.info_dlg.tableWidget.setItem(0, 2, QTableWidgetItem(str(test.haltungen_0_rw)))
            self.info_dlg.tableWidget.setItem(0, 3, QTableWidgetItem(str(test.haltungen_1_rw)))
            self.info_dlg.tableWidget.setItem(0, 4, QTableWidgetItem(str(test.haltungen_2_rw)))
            self.info_dlg.tableWidget.setItem(0, 5, QTableWidgetItem(str(test.haltungen_3_rw)))
            self.info_dlg.tableWidget.setItem(0, 6, QTableWidgetItem(str(test.haltungen_4_rw)))
            self.info_dlg.tableWidget.setItem(0, 7, QTableWidgetItem(str(test.haltungen_5_rw)))
            self.info_dlg.tableWidget.setItem(0, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_rw)))
            self.info_dlg.tableWidget.setItem(0, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_rw)))
            self.info_dlg.tableWidget.setItem(0, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_rw)))

            self.info_dlg.tableWidget.setItem(1, 2, QTableWidgetItem(str(test.haltungen_0_sw)))
            self.info_dlg.tableWidget.setItem(1, 3, QTableWidgetItem(str(test.haltungen_1_sw)))
            self.info_dlg.tableWidget.setItem(1, 4, QTableWidgetItem(str(test.haltungen_2_sw)))
            self.info_dlg.tableWidget.setItem(1, 5, QTableWidgetItem(str(test.haltungen_3_sw)))
            self.info_dlg.tableWidget.setItem(1, 6, QTableWidgetItem(str(test.haltungen_4_sw)))
            self.info_dlg.tableWidget.setItem(1, 7, QTableWidgetItem(str(test.haltungen_5_sw)))
            self.info_dlg.tableWidget.setItem(1, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_sw)))
            self.info_dlg.tableWidget.setItem(1, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_sw)))
            self.info_dlg.tableWidget.setItem(1, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_sw)))

            self.info_dlg.tableWidget.setItem(2, 2, QTableWidgetItem(str(test.haltungen_0_mw)))
            self.info_dlg.tableWidget.setItem(2, 3, QTableWidgetItem(str(test.haltungen_1_mw)))
            self.info_dlg.tableWidget.setItem(2, 4, QTableWidgetItem(str(test.haltungen_2_mw)))
            self.info_dlg.tableWidget.setItem(2, 5, QTableWidgetItem(str(test.haltungen_3_mw)))
            self.info_dlg.tableWidget.setItem(2, 6, QTableWidgetItem(str(test.haltungen_4_mw)))
            self.info_dlg.tableWidget.setItem(2, 7, QTableWidgetItem(str(test.haltungen_5_mw)))
            self.info_dlg.tableWidget.setItem(2, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_mw)))
            self.info_dlg.tableWidget.setItem(2, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_mw)))
            self.info_dlg.tableWidget.setItem(2, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_mw)))

            # Felder Schäachte

            self.info_dlg.tableWidget_2.setItem(0, 1, QTableWidgetItem(str(test.anz_schaechte_rw)))
            self.info_dlg.tableWidget_2.setItem(1, 1, QTableWidgetItem(str(test.anz_schaechte_sw)))
            self.info_dlg.tableWidget_2.setItem(2, 1, QTableWidgetItem(str(test.anz_schaechte_mw)))

            self.info_dlg.tableWidget_2.setItem(0, 2, QTableWidgetItem(str(test.anz_schaechte_0_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 3, QTableWidgetItem(str(test.anz_schaechte_1_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 4, QTableWidgetItem(str(test.anz_schaechte_2_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 5, QTableWidgetItem(str(test.anz_schaechte_3_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 6, QTableWidgetItem(str(test.anz_schaechte_4_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 7, QTableWidgetItem(str(test.anz_schaechte_5_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_rw)))

            self.info_dlg.tableWidget_2.setItem(1, 2, QTableWidgetItem(str(test.anz_schaechte_0_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 3, QTableWidgetItem(str(test.anz_schaechte_1_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 4, QTableWidgetItem(str(test.anz_schaechte_2_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 5, QTableWidgetItem(str(test.anz_schaechte_3_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 6, QTableWidgetItem(str(test.anz_schaechte_4_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 7, QTableWidgetItem(str(test.anz_schaechte_5_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_sw)))

            self.info_dlg.tableWidget_2.setItem(2, 2, QTableWidgetItem(str(test.anz_schaechte_0_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 3, QTableWidgetItem(str(test.anz_schaechte_1_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 4, QTableWidgetItem(str(test.anz_schaechte_2_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 5, QTableWidgetItem(str(test.anz_schaechte_3_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 6, QTableWidgetItem(str(test.anz_schaechte_4_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 7, QTableWidgetItem(str(test.anz_schaechte_5_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_mw)))

    def run_info(self) -> None:
        # Prüfen, ob ein Projekt geladen ist
        project = QgsProject.instance()
        layers = project.mapLayers()

        self.info_dlg.select_date()
        if len(layers) > 0:

            self.fig_1 = self.dialog.fig_1
            self.canv_1 = self.dialog.canv_1
            self.fig_2 = self.dialog.fig_2
            self.canv_2 = self.dialog.canv_2
            self.fig_3 = self.dialog.fig_3
            self.canv_3 = self.dialog.canv_3
            self.fig_4 = self.dialog.fig_4
            self.canv_4 = self.dialog.canv_4

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected

            test = Info(self.fig_1, self.canv_1, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.fig_4, self.canv_4, DBConnection())
            test.run(self.info_dlg.date.currentText())
            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            # self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            version = qgs_version()
            self.info_dlg.tf_qkanversion.setText(str(version))
            self.info_dlg.textBrowser_3.setText(str(test.anz_haltungen))
            self.info_dlg.textBrowser_4.setText(str(test.anz_schaechte))
            self.info_dlg.textBrowser_5.setText(str(test.laenge_haltungen))
            self.info_dlg.tf_anz_teilgeb.setText(str(test.anz_teilgeb))

            # Felder Haltungen
            if test.bew_art == 'DWA':
                self.info_dlg.comboBox.setItemText(0, 'DWA')
            if test.bew_art == 'ISYBAU':
                self.info_dlg.comboBox.setItemText(1, 'ISYBAU')
            self.info_dlg.tableWidget.setItem(0, 1, QTableWidgetItem(str(test.laenge_haltungen_rw)))
            self.info_dlg.tableWidget.setItem(1, 1, QTableWidgetItem(str(test.laenge_haltungen_sw)))
            self.info_dlg.tableWidget.setItem(2, 1, QTableWidgetItem(str(test.laenge_haltungen_mw)))

            self.info_dlg.tableWidget.setItem(0, 2, QTableWidgetItem(str(test.haltungen_0_rw)))
            self.info_dlg.tableWidget.setItem(0, 3, QTableWidgetItem(str(test.haltungen_1_rw)))
            self.info_dlg.tableWidget.setItem(0, 4, QTableWidgetItem(str(test.haltungen_2_rw)))
            self.info_dlg.tableWidget.setItem(0, 5, QTableWidgetItem(str(test.haltungen_3_rw)))
            self.info_dlg.tableWidget.setItem(0, 6, QTableWidgetItem(str(test.haltungen_4_rw)))
            self.info_dlg.tableWidget.setItem(0, 7, QTableWidgetItem(str(test.haltungen_5_rw)))
            self.info_dlg.tableWidget.setItem(0, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_rw)))
            self.info_dlg.tableWidget.setItem(0, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_rw)))
            self.info_dlg.tableWidget.setItem(0, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_rw)))

            self.info_dlg.tableWidget.setItem(1, 2, QTableWidgetItem(str(test.haltungen_0_sw)))
            self.info_dlg.tableWidget.setItem(1, 3, QTableWidgetItem(str(test.haltungen_1_sw)))
            self.info_dlg.tableWidget.setItem(1, 4, QTableWidgetItem(str(test.haltungen_2_sw)))
            self.info_dlg.tableWidget.setItem(1, 5, QTableWidgetItem(str(test.haltungen_3_sw)))
            self.info_dlg.tableWidget.setItem(1, 6, QTableWidgetItem(str(test.haltungen_4_sw)))
            self.info_dlg.tableWidget.setItem(1, 7, QTableWidgetItem(str(test.haltungen_5_sw)))
            self.info_dlg.tableWidget.setItem(1, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_sw)))
            self.info_dlg.tableWidget.setItem(1, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_sw)))
            self.info_dlg.tableWidget.setItem(1, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_sw)))

            self.info_dlg.tableWidget.setItem(2, 2, QTableWidgetItem(str(test.haltungen_0_mw)))
            self.info_dlg.tableWidget.setItem(2, 3, QTableWidgetItem(str(test.haltungen_1_mw)))
            self.info_dlg.tableWidget.setItem(2, 4, QTableWidgetItem(str(test.haltungen_2_mw)))
            self.info_dlg.tableWidget.setItem(2, 5, QTableWidgetItem(str(test.haltungen_3_mw)))
            self.info_dlg.tableWidget.setItem(2, 6, QTableWidgetItem(str(test.haltungen_4_mw)))
            self.info_dlg.tableWidget.setItem(2, 7, QTableWidgetItem(str(test.haltungen_5_mw)))
            self.info_dlg.tableWidget.setItem(2, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_mw)))
            self.info_dlg.tableWidget.setItem(2, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_mw)))
            self.info_dlg.tableWidget.setItem(2, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_mw)))

            # Felder Schäachte

            self.info_dlg.tableWidget_2.setItem(0, 1, QTableWidgetItem(str(test.anz_schaechte_rw)))
            self.info_dlg.tableWidget_2.setItem(1, 1, QTableWidgetItem(str(test.anz_schaechte_sw)))
            self.info_dlg.tableWidget_2.setItem(2, 1, QTableWidgetItem(str(test.anz_schaechte_mw)))

            self.info_dlg.tableWidget_2.setItem(0, 2, QTableWidgetItem(str(test.anz_schaechte_0_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 3, QTableWidgetItem(str(test.anz_schaechte_1_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 4, QTableWidgetItem(str(test.anz_schaechte_2_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 5, QTableWidgetItem(str(test.anz_schaechte_3_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 6, QTableWidgetItem(str(test.anz_schaechte_4_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 7, QTableWidgetItem(str(test.anz_schaechte_5_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_rw)))

            self.info_dlg.tableWidget_2.setItem(1, 2, QTableWidgetItem(str(test.anz_schaechte_0_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 3, QTableWidgetItem(str(test.anz_schaechte_1_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 4, QTableWidgetItem(str(test.anz_schaechte_2_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 5, QTableWidgetItem(str(test.anz_schaechte_3_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 6, QTableWidgetItem(str(test.anz_schaechte_4_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 7, QTableWidgetItem(str(test.anz_schaechte_5_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_sw)))

            self.info_dlg.tableWidget_2.setItem(2, 2, QTableWidgetItem(str(test.anz_schaechte_0_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 3, QTableWidgetItem(str(test.anz_schaechte_1_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 4, QTableWidgetItem(str(test.anz_schaechte_2_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 5, QTableWidgetItem(str(test.anz_schaechte_3_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 6, QTableWidgetItem(str(test.anz_schaechte_4_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 7, QTableWidgetItem(str(test.anz_schaechte_5_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_mw)))

            # XML-Export
            if self.info_dlg.filename != '':

                cwd = os.path.dirname(os.path.abspath(__file__))

                root = Element(
                    "SuewVO",
                )

                ks = SubElement(root, "KS")
                ges = SubElement(ks, "Gesamtnetz")
                if test.bew_art == 'DWA':
                    _create_children_text(
                        ges,
                        {
                            "Zustandsbewertung": 'DWA',
                        },
                    )
                if test.bew_art == 'ISYBAU':
                    _create_children_text(
                        ges,
                        {
                            "Zustandsbewertung": 'ISYBAU',
                        },
                    )

                abw = SubElement(ks, "Haltungen")
                rw = SubElement(abw, "RW")
                _create_children_text(
                    rw,
                    {
                        "Netzlaenge": str(test.laenge_haltungen_rw),
                        "Z_0": str(test.haltungen_0_rw),
                        "Z_1": str(test.haltungen_1_rw),
                        "Z_2": str(test.haltungen_2_rw),
                        "Z_3": str(test.haltungen_3_rw),
                        "Z_4": str(test.haltungen_4_rw),
                        "Z_5": str(test.haltungen_5_rw),
                        "Untersucht_gesamt": str(test.laenge_haltungen_untersuch_rw),
                        "Untersucht_BJ": str(test.laenge_haltungen_untersuch_bj_rw),
                        "Saniert_BJ": str(test.laenge_haltungen_saniert_rw),
                    },
                )

                sw = SubElement(abw, "SW")
                _create_children_text(
                    sw,
                    {
                        "Netzlaenge": str(test.laenge_haltungen_sw),
                        "Z_0": str(test.haltungen_0_sw),
                        "Z_1": str(test.haltungen_1_sw),
                        "Z_2": str(test.haltungen_2_sw),
                        "Z_3": str(test.haltungen_3_sw),
                        "Z_4": str(test.haltungen_4_sw),
                        "Z_5": str(test.haltungen_5_sw),
                        "Untersucht_gesamt": str(test.laenge_haltungen_untersuch_sw),
                        "Untersucht_BJ": str(test.laenge_haltungen_untersuch_bj_sw),
                        "Saniert_BJ": str(test.laenge_haltungen_saniert_sw),
                    },
                )

                mw = SubElement(abw, "MW")
                _create_children_text(
                    mw,
                    {
                        "Netzlaenge": str(test.laenge_haltungen_mw),
                        "Z_0": str(test.haltungen_0_mw),
                        "Z_1": str(test.haltungen_1_mw),
                        "Z_2": str(test.haltungen_2_mw),
                        "Z_3": str(test.haltungen_3_mw),
                        "Z_4": str(test.haltungen_4_mw),
                        "Z_5": str(test.haltungen_5_mw),
                        "Untersucht_gesamt": str(test.laenge_haltungen_untersuch_mw),
                        "Untersucht_BJ": str(test.laenge_haltungen_untersuch_bj_mw),
                        "Saniert_BJ": str(test.laenge_haltungen_saniert_mw),
                    },
                )

                schaechte = SubElement(ks, "Schaechte")

                rw_s = SubElement(schaechte, "RW")
                _create_children_text(
                    rw_s,
                    {
                        "Anzahl": str(test.anz_schaechte_rw),
                        "Z_0": str(test.haltungen_0_rw),
                        "Z_1": str(test.haltungen_1_rw),
                        "Z_2": str(test.haltungen_2_rw),
                        "Z_3": str(test.haltungen_3_rw),
                        "Z_4": str(test.haltungen_4_rw),
                        "Z_5": str(test.haltungen_5_rw),
                        "Untersucht_gesamt": str(test.anz_schaechte_untersuch_rw),
                        "Untersucht_BJ": str(test.anz_schaechte_untersuch_bj_rw),
                        "Saniert_BJ": str(test.anz_schaechte_saniert_rw),
                    },
                )

                sw_s = SubElement(schaechte, "SW")
                _create_children_text(
                    sw_s,
                    {
                        "Anzahl": str(test.anz_schaechte_sw),
                        "Z_0": str(test.haltungen_0_sw),
                        "Z_1": str(test.haltungen_1_sw),
                        "Z_2": str(test.haltungen_2_sw),
                        "Z_3": str(test.haltungen_3_sw),
                        "Z_4": str(test.haltungen_4_sw),
                        "Z_5": str(test.haltungen_5_sw),
                        "Untersucht_gesamt": str(test.anz_schaechte_untersuch_sw),
                        "Untersucht_BJ": str(test.anz_schaechte_untersuch_bj_sw),
                        "Saniert_BJ": str(test.anz_schaechte_saniert_sw),
                    },
                )

                mw_s = SubElement(schaechte, "MW")
                _create_children_text(
                    mw_s,
                    {
                        "Anzahl": str(test.anz_schaechte_mw),
                        "Z_0": str(test.haltungen_0_mw),
                        "Z_1": str(test.haltungen_1_mw),
                        "Z_2": str(test.haltungen_2_mw),
                        "Z_3": str(test.haltungen_3_mw),
                        "Z_4": str(test.haltungen_4_mw),
                        "Z_5": str(test.haltungen_5_mw),
                        "Untersucht_gesamt": str(test.anz_schaechte_untersuch_mw),
                        "Untersucht_BJ": str(test.anz_schaechte_untersuch_bj_mw),
                        "Saniert_BJ": str(test.anz_schaechte_saniert_mw),
                    },
                )
                path = os.path.dirname(__file__)
                Path(path + r"\suewvo.xml").write_text(
                    minidom.parseString(tostring(root)).toprettyxml(indent="  ")
                )

            path = os.path.dirname(__file__)
            xl = w3c.Dispatch("Excel.Application")
            xl.Workbooks.Open(Filename=path + r"\süwvo abw-erhebungsbögen 2021_test.xlsm", ReadOnly=1)
            xl.Application.Run("Tabelle2.ImportXMLData")
            xl.Workbooks.Close(SaveChanges=0)
            xl.Application.Quit()
            xl.Quit()
            xl = 0

            # Run the dialog event loop
            result = self.info_dlg.exec_()

        else:
            warnung('Hinweis', 'Es ist kein Projekt geladen!')

    def run_info_2(self) -> None:
        # Prüfen, ob ein Projekt geladen ist
        project = QgsProject.instance()
        layers = project.mapLayers()

        self.info_dlg.select_date()
        if len(layers) > 0:

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected
            self.fig_1 = self.dialog.fig_1
            self.canv_1 = self.dialog.canv_1

            test = Info(self.fig_1, self.canv_1, DBConnection())
            test.run(self.info_dlg.date.currentText())
            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            # self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            version = qgs_version()
            self.info_dlg.tf_qkanversion.setText(str(version))
            self.info_dlg.textBrowser_3.setText(str(test.anz_haltungen))
            self.info_dlg.textBrowser_4.setText(str(test.anz_schaechte))
            self.info_dlg.textBrowser_5.setText(str(test.laenge_haltungen))
            self.info_dlg.tf_anz_teilgeb.setText(str(test.anz_teilgeb))

            # Felder Haltungen
            if test.bew_art == 'DWA':
                self.info_dlg.comboBox.setItemText(0, 'DWA')
            if test.bew_art == 'ISYBAU':
                self.info_dlg.comboBox.setItemText(1, 'ISYBAU')
            self.info_dlg.tableWidget.setItem(0, 1, QTableWidgetItem(str(test.laenge_haltungen_rw)))
            self.info_dlg.tableWidget.setItem(1, 1, QTableWidgetItem(str(test.laenge_haltungen_sw)))
            self.info_dlg.tableWidget.setItem(2, 1, QTableWidgetItem(str(test.laenge_haltungen_mw)))

            self.info_dlg.tableWidget.setItem(0, 2, QTableWidgetItem(str(test.haltungen_0_rw)))
            self.info_dlg.tableWidget.setItem(0, 3, QTableWidgetItem(str(test.haltungen_1_rw)))
            self.info_dlg.tableWidget.setItem(0, 4, QTableWidgetItem(str(test.haltungen_2_rw)))
            self.info_dlg.tableWidget.setItem(0, 5, QTableWidgetItem(str(test.haltungen_3_rw)))
            self.info_dlg.tableWidget.setItem(0, 6, QTableWidgetItem(str(test.haltungen_4_rw)))
            self.info_dlg.tableWidget.setItem(0, 7, QTableWidgetItem(str(test.haltungen_5_rw)))
            self.info_dlg.tableWidget.setItem(0, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_rw)))
            self.info_dlg.tableWidget.setItem(0, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_rw)))
            self.info_dlg.tableWidget.setItem(0, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_rw)))

            self.info_dlg.tableWidget.setItem(1, 2, QTableWidgetItem(str(test.haltungen_0_sw)))
            self.info_dlg.tableWidget.setItem(1, 3, QTableWidgetItem(str(test.haltungen_1_sw)))
            self.info_dlg.tableWidget.setItem(1, 4, QTableWidgetItem(str(test.haltungen_2_sw)))
            self.info_dlg.tableWidget.setItem(1, 5, QTableWidgetItem(str(test.haltungen_3_sw)))
            self.info_dlg.tableWidget.setItem(1, 6, QTableWidgetItem(str(test.haltungen_4_sw)))
            self.info_dlg.tableWidget.setItem(1, 7, QTableWidgetItem(str(test.haltungen_5_sw)))
            self.info_dlg.tableWidget.setItem(1, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_sw)))
            self.info_dlg.tableWidget.setItem(1, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_sw)))
            self.info_dlg.tableWidget.setItem(1, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_sw)))

            self.info_dlg.tableWidget.setItem(2, 2, QTableWidgetItem(str(test.haltungen_0_mw)))
            self.info_dlg.tableWidget.setItem(2, 3, QTableWidgetItem(str(test.haltungen_1_mw)))
            self.info_dlg.tableWidget.setItem(2, 4, QTableWidgetItem(str(test.haltungen_2_mw)))
            self.info_dlg.tableWidget.setItem(2, 5, QTableWidgetItem(str(test.haltungen_3_mw)))
            self.info_dlg.tableWidget.setItem(2, 6, QTableWidgetItem(str(test.haltungen_4_mw)))
            self.info_dlg.tableWidget.setItem(2, 7, QTableWidgetItem(str(test.haltungen_5_mw)))
            self.info_dlg.tableWidget.setItem(2, 8, QTableWidgetItem(str(test.laenge_haltungen_untersuch_mw)))
            self.info_dlg.tableWidget.setItem(2, 9, QTableWidgetItem(str(test.laenge_haltungen_untersuch_bj_mw)))
            self.info_dlg.tableWidget.setItem(2, 10, QTableWidgetItem(str(test.laenge_haltungen_saniert_mw)))

            # Felder Schäachte

            self.info_dlg.tableWidget_2.setItem(0, 1, QTableWidgetItem(str(test.anz_schaechte_rw)))
            self.info_dlg.tableWidget_2.setItem(1, 1, QTableWidgetItem(str(test.anz_schaechte_sw)))
            self.info_dlg.tableWidget_2.setItem(2, 1, QTableWidgetItem(str(test.anz_schaechte_mw)))

            self.info_dlg.tableWidget_2.setItem(0, 2, QTableWidgetItem(str(test.anz_schaechte_0_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 3, QTableWidgetItem(str(test.anz_schaechte_1_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 4, QTableWidgetItem(str(test.anz_schaechte_2_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 5, QTableWidgetItem(str(test.anz_schaechte_3_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 6, QTableWidgetItem(str(test.anz_schaechte_4_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 7, QTableWidgetItem(str(test.anz_schaechte_5_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_rw)))
            self.info_dlg.tableWidget_2.setItem(0, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_rw)))

            self.info_dlg.tableWidget_2.setItem(1, 2, QTableWidgetItem(str(test.anz_schaechte_0_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 3, QTableWidgetItem(str(test.anz_schaechte_1_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 4, QTableWidgetItem(str(test.anz_schaechte_2_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 5, QTableWidgetItem(str(test.anz_schaechte_3_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 6, QTableWidgetItem(str(test.anz_schaechte_4_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 7, QTableWidgetItem(str(test.anz_schaechte_5_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_sw)))
            self.info_dlg.tableWidget_2.setItem(1, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_sw)))

            self.info_dlg.tableWidget_2.setItem(2, 2, QTableWidgetItem(str(test.anz_schaechte_0_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 3, QTableWidgetItem(str(test.anz_schaechte_1_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 4, QTableWidgetItem(str(test.anz_schaechte_2_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 5, QTableWidgetItem(str(test.anz_schaechte_3_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 6, QTableWidgetItem(str(test.anz_schaechte_4_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 7, QTableWidgetItem(str(test.anz_schaechte_5_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 8, QTableWidgetItem(str(test.anz_schaechte_untersuch_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 9, QTableWidgetItem(str(test.anz_schaechte_untersuch_bj_mw)))
            self.info_dlg.tableWidget_2.setItem(2, 10, QTableWidgetItem(str(test.anz_schaechte_saniert_mw)))

            # XML-Export
            if self.info_dlg.filename_xml != '':

                cwd = os.path.dirname(os.path.abspath(__file__))

                root = Element(
                    "SuewVO",
                )

                ks = SubElement(root, "KS")
                ges = SubElement(ks, "Gesamtnetz")
                if test.bew_art == 'DWA':
                    _create_children_text(
                        ges,
                        {
                            "Zustandsbewertung": 'DWA',
                        },
                    )
                if test.bew_art == 'ISYBAU':
                    _create_children_text(
                        ges,
                        {
                            "Zustandsbewertung": 'ISYBAU',
                        },
                    )

                abw = SubElement(ks, "Haltungen")
                rw = SubElement(abw, "RW")
                _create_children_text(
                    rw,
                    {
                        "Netzlaenge": str(test.laenge_haltungen_rw),
                        "Z_0": str(test.haltungen_0_rw),
                        "Z_1": str(test.haltungen_1_rw),
                        "Z_2": str(test.haltungen_2_rw),
                        "Z_3": str(test.haltungen_3_rw),
                        "Z_4": str(test.haltungen_4_rw),
                        "Z_5": str(test.haltungen_5_rw),
                        "Untersucht_gesamt": str(test.laenge_haltungen_untersuch_rw),
                        "Untersucht_BJ": str(test.laenge_haltungen_untersuch_bj_rw),
                        "Saniert_BJ": str(test.laenge_haltungen_saniert_rw),
                    },
                )

                sw = SubElement(abw, "SW")
                _create_children_text(
                    sw,
                    {
                        "Netzlaenge": str(test.laenge_haltungen_sw),
                        "Z_0": str(test.haltungen_0_sw),
                        "Z_1": str(test.haltungen_1_sw),
                        "Z_2": str(test.haltungen_2_sw),
                        "Z_3": str(test.haltungen_3_sw),
                        "Z_4": str(test.haltungen_4_sw),
                        "Z_5": str(test.haltungen_5_sw),
                        "Untersucht_gesamt": str(test.laenge_haltungen_untersuch_sw),
                        "Untersucht_BJ": str(test.laenge_haltungen_untersuch_bj_sw),
                        "Saniert_BJ": str(test.laenge_haltungen_saniert_sw),
                    },
                )

                mw = SubElement(abw, "MW")
                _create_children_text(
                    mw,
                    {
                        "Netzlaenge": str(test.laenge_haltungen_mw),
                        "Z_0": str(test.haltungen_0_mw),
                        "Z_1": str(test.haltungen_1_mw),
                        "Z_2": str(test.haltungen_2_mw),
                        "Z_3": str(test.haltungen_3_mw),
                        "Z_4": str(test.haltungen_4_mw),
                        "Z_5": str(test.haltungen_5_mw),
                        "Untersucht_gesamt": str(test.laenge_haltungen_untersuch_mw),
                        "Untersucht_BJ": str(test.laenge_haltungen_untersuch_bj_mw),
                        "Saniert_BJ": str(test.laenge_haltungen_saniert_mw),
                    },
                )

                schaechte = SubElement(ks, "Schaechte")

                rw_s = SubElement(schaechte, "RW")
                _create_children_text(
                    rw_s,
                    {
                        "Anzahl": str(test.anz_schaechte_rw),
                        "Z_0": str(test.haltungen_0_rw),
                        "Z_1": str(test.haltungen_1_rw),
                        "Z_2": str(test.haltungen_2_rw),
                        "Z_3": str(test.haltungen_3_rw),
                        "Z_4": str(test.haltungen_4_rw),
                        "Z_5": str(test.haltungen_5_rw),
                        "Untersucht_gesamt": str(test.anz_schaechte_untersuch_rw),
                        "Untersucht_BJ": str(test.anz_schaechte_untersuch_bj_rw),
                        "Saniert_BJ": str(test.anz_schaechte_saniert_rw),
                    },
                )

                sw_s = SubElement(schaechte, "SW")
                _create_children_text(
                    sw_s,
                    {
                        "Anzahl": str(test.anz_schaechte_sw),
                        "Z_0": str(test.haltungen_0_sw),
                        "Z_1": str(test.haltungen_1_sw),
                        "Z_2": str(test.haltungen_2_sw),
                        "Z_3": str(test.haltungen_3_sw),
                        "Z_4": str(test.haltungen_4_sw),
                        "Z_5": str(test.haltungen_5_sw),
                        "Untersucht_gesamt": str(test.anz_schaechte_untersuch_sw),
                        "Untersucht_BJ": str(test.anz_schaechte_untersuch_bj_sw),
                        "Saniert_BJ": str(test.anz_schaechte_saniert_sw),
                    },
                )

                mw_s = SubElement(schaechte, "MW")
                _create_children_text(
                    mw_s,
                    {
                        "Anzahl": str(test.anz_schaechte_mw),
                        "Z_0": str(test.haltungen_0_mw),
                        "Z_1": str(test.haltungen_1_mw),
                        "Z_2": str(test.haltungen_2_mw),
                        "Z_3": str(test.haltungen_3_mw),
                        "Z_4": str(test.haltungen_4_mw),
                        "Z_5": str(test.haltungen_5_mw),
                        "Untersucht_gesamt": str(test.anz_schaechte_untersuch_mw),
                        "Untersucht_BJ": str(test.anz_schaechte_untersuch_bj_mw),
                        "Saniert_BJ": str(test.anz_schaechte_saniert_mw),
                    },
                )
                Path(self.info_dlg.filename_xml).write_text(
                    minidom.parseString(tostring(root)).toprettyxml(indent="  ")
                )

            # Run the dialog event loop
            result = self.info_dlg.exec_()

        else:
            logger.warning('Es ist kein Projekt geladen!')

