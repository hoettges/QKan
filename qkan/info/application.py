from qgis.gui import QgisInterface
from qgis.core import QgsProject
from PyQt5.QtWidgets import *
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin
from xml.etree.ElementTree import Element, SubElement, tostring
try:
    import win32com.client as w3c
except:
    w3c = None
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from typing import Dict, List, Optional, Union
from pathlib import Path
from xml.dom import minidom

from qkan.utils import get_logger
logger = get_logger("QKan")

from PyQt5.QtWidgets import QTableWidgetItem

from ._info import Info
from .application_dialog import InfoDialog

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
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
        self.info_dlg.lineEdit.textChanged.connect(self.run)
        self.info_dlg.lineEdit_2.textChanged.connect(self.run)
        self.info_dlg.lineEdit_3.textChanged.connect(self.run)

        self.info_dlg.comboBox_2.currentTextChanged.connect(self.run)
        self.info_dlg.checkBox_2.clicked.connect(self.run)
        #self.info_dlg.comboBox_3.currentTextChanged.connect(self.run)
        self.info_dlg.comboBox_8.currentTextChanged.connect(self.run)
        self.info_dlg.comboBox_9.currentTextChanged.connect(self.run)

        self.stamm: Optional[Element] = None
        self.hydraulik_objekte: Optional[Element] = None


    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/info/res/info.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Infos zum QKan Projekt"),
            toolbar='QKan-Allgemein',
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
        self.dialog.fig_1 = plt.figure()
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
        self.dialog.fig_2 = plt.figure()
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
        self.dialog.fig_3 = plt.figure()
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
        self.dialog.fig_4 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_4 = FigureCanvas(self.dialog.fig_4)

        self.dialog.verticalLayout_4.addWidget(self.dialog.canv_4)
        self.dialog.verticalLayout_4.addWidget(NavigationToolbar(self.dialog.canv_4, qw, True))

    def get_widget_5(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        self.dialog.fig_5 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_5 = FigureCanvas(self.dialog.fig_5)

        self.dialog.verticalLayout.addWidget(self.dialog.canv_5)
        self.dialog.verticalLayout.addWidget(NavigationToolbar(self.dialog.canv_5, qw, True))

    def get_widget_6(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        #self.dialog.fig_6 = plt.figure(layout='constrained')
        self.dialog.fig_6 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_6 = FigureCanvas(self.dialog.fig_6)

        self.dialog.verticalLayout_10.addWidget(self.dialog.canv_6)
        self.dialog.verticalLayout_10.addWidget(NavigationToolbar(self.dialog.canv_6, qw, True))

    def get_widget_7(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        #self.dialog.fig_6 = plt.figure(layout='constrained')
        self.dialog.fig_7 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_7 = FigureCanvas(self.dialog.fig_7)

        self.dialog.verticalLayout_12.addWidget(self.dialog.canv_7)
        self.dialog.verticalLayout_12.addWidget(NavigationToolbar(self.dialog.canv_7, qw, True))

    def get_widget_8(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        #self.dialog.fig_6 = plt.figure(layout='constrained')
        self.dialog.fig_8 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_8 = FigureCanvas(self.dialog.fig_8)

        self.dialog.verticalLayout_13.addWidget(self.dialog.canv_8)
        self.dialog.verticalLayout_13.addWidget(NavigationToolbar(self.dialog.canv_8, qw, True))

    def get_widget_9(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        #self.dialog.fig_6 = plt.figure(layout='constrained')
        self.dialog.fig_9 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_9 = FigureCanvas(self.dialog.fig_9)

        self.dialog.verticalLayout_45.addWidget(self.dialog.canv_9)
        self.dialog.verticalLayout_45.addWidget(NavigationToolbar(self.dialog.canv_9, qw, True))

    def get_widget_10(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.info_dlg
        #self.dialog.fig_6 = plt.figure(layout='constrained')
        self.dialog.fig_10 = plt.figure()
        #in der self.fig können die Matplotlib sachen angezeigt werden

        qw = QWidget(self.dialog)
        self.dialog.canv_10 = FigureCanvas(self.dialog.fig_10)

        self.dialog.verticalLayout_47.addWidget(self.dialog.canv_10)
        self.dialog.verticalLayout_47.addWidget(NavigationToolbar(self.dialog.canv_10, qw, True))

    # def on_click(self, event):
    #     Info.handle_click(event, Info.anzeigen, Info.anzeigen)



    def run(self) -> None:
        # Prüfen, ob ein Projekt geladen ist
        project = QgsProject.instance()
        layers = project.mapLayers()

        self.get_widget_1()
        self.get_widget_2()
        self.get_widget_3()
        self.get_widget_4()
        self.get_widget_5()
        self.get_widget_6()
        self.get_widget_7()
        self.get_widget_8()
        self.get_widget_9()
        self.get_widget_10()
        # self.canv_1 = None

        if len(layers) > 0:

            self.fig_1 = self.dialog.fig_1
            self.canv_1 = self.dialog.canv_1
            self.fig_2 = self.dialog.fig_2
            self.canv_2 = self.dialog.canv_2
            self.fig_3 = self.dialog.fig_3
            self.canv_3 = self.dialog.canv_3
            self.fig_4 = self.dialog.fig_4
            self.canv_4 = self.dialog.canv_4
            self.fig_5 = self.dialog.fig_5
            self.canv_5 = self.dialog.canv_5
            self.fig_6 = self.dialog.fig_6
            self.canv_6 = self.dialog.canv_6
            self.fig_7 = self.dialog.fig_7
            self.canv_7 = self.dialog.canv_7
            self.fig_8 = self.dialog.fig_8
            self.canv_8 = self.dialog.canv_8
            self.fig_9 = self.dialog.fig_9
            self.canv_9 = self.dialog.canv_9
            self.fig_10 = self.dialog.fig_10
            self.canv_10 = self.dialog.canv_10
            self.comboBox_2 = self.dialog.comboBox_2.currentText()
            #self.comboBox_3 = self.dialog.comboBox_3.currentText()
            #self.comboBox_3 = self.dialog.comboBox_3.currentText()
            self.comboBox_8 = self.dialog.comboBox_8.currentText()
            self.comboBox_9 = self.dialog.comboBox_9.currentText()
            self.dat_1 = self.dialog.lineEdit.text()
            self.dat_2 = self.dialog.lineEdit_2.text()
            self.dat_3 = self.dialog.lineEdit_3.text()
            self.check = self.dialog.checkBox_2.isChecked()

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected

            test = Info(self.fig_1, self.canv_1, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.fig_4, self.canv_4, self.fig_5, self.canv_5, self.fig_6, self.canv_6, self.fig_7, self.canv_7, self.fig_8, self.canv_8, self.fig_9, self.canv_9, self.fig_10, self.canv_10, self.comboBox_2,  self.comboBox_8, self.comboBox_9, self.dat_1, self.dat_2, self.dat_3, DBConnection(),self.check)
            test.run()

            # def on_click(self, event):
            #     test.handle_click(event, self.pie_wedges, run_script)

            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            # self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            self.info_dlg.tf_qkanversion.setText(str(QKan.qgsVersion))
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

        if len(layers) > 0:

            self.fig_1 = self.dialog.fig_1
            self.canv_1 = self.dialog.canv_1
            self.fig_2 = self.dialog.fig_2
            self.canv_2 = self.dialog.canv_2
            self.fig_3 = self.dialog.fig_3
            self.canv_3 = self.dialog.canv_3
            self.fig_4 = self.dialog.fig_4
            self.canv_4 = self.dialog.canv_4
            self.fig_5 = self.dialog.fig_5
            self.canv_5 = self.dialog.canv_5
            self.fig_6 = self.dialog.fig_6
            self.canv_6 = self.dialog.canv_6
            self.fig_7 = self.dialog.fig_7
            self.canv_7 = self.dialog.canv_7
            self.fig_8 = self.dialog.fig_8
            self.canv_8 = self.dialog.canv_8
            self.fig_9 = self.dialog.fig_9
            self.canv_9 = self.dialog.canv_9
            self.fig_10 = self.dialog.fig_10
            self.canv_10 = self.dialog.canv_10
            self.comboBox_2 = self.dialog.comboBox_2.currentText()
            #self.comboBox_3 = self.dialog.comboBox_3.currentText()
            self.comboBox_8 = self.dialog.comboBox_8.currentText()
            self.comboBox_9 = self.dialog.comboBox_9.currentText()
            self.dat_1 = self.dialog.lineEdit.text()
            self.dat_2 = self.dialog.lineEdit_2.text()
            self.dat_3 = self.dialog.lineEdit_3.text()
            self.check = self.dialog.checkBox_2.isChecked()

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected

            test = Info(self.fig_1, self.canv_1, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.fig_4,
                        self.canv_4, self.fig_5, self.canv_5, self.fig_6, self.canv_6, self.fig_7, self.canv_7,
                        self.fig_8, self.canv_8, self.fig_9, self.canv_9, self.fig_10, self.canv_10, self.comboBox_2,
                         self.comboBox_8, self.comboBox_9, self.dat_1, self.dat_2, self.dat_3,
                        DBConnection(), self.check)
            test.run()
            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            # self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            self.info_dlg.tf_qkanversion.setText(str(QKan.qgsVersion))
            #self.info_dlg.textBrowser_3.setText(str(test.anz_haltungen))
            #self.info_dlg.textBrowser_4.setText(str(test.anz_schaechte))
            #self.info_dlg.textBrowser_5.setText(str(test.laenge_haltungen))
            #self.info_dlg.tf_anz_teilgeb.setText(str(test.anz_teilgeb))

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
            if w3c:
                xl = w3c.Dispatch("Excel.Application")
                xl.Visible = True
                wb = xl.Workbooks.Open(Filename=path + r"\süwvo abw-erhebungsbögen 2021_test.xlsm", ReadOnly=1)
                #xl.Application.Run("Tabelle2.ImportXMLData")
                xl.Application.Run("ImportXMLData")
                #xl.Workbooks.Close(SaveChanges = 0)
                wb.Close(SaveChanges=0)
                xl.Application.Quit()
                xl.Quit()
                xl = 0

                # Run the dialog event loop
                result = self.info_dlg.exec_()
            else:
                logger.warning("Es tut mir leid: Excel kann nur unter Windows ausgeführt werden.")

        else:
            logger.warning('Hinweis: Es ist kein Projekt geladen!')

    def run_info_2(self) -> None:
        # Prüfen, ob ein Projekt geladen ist
        project = QgsProject.instance()
        layers = project.mapLayers()

        if len(layers) > 0:

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected
            self.fig_1 = self.dialog.fig_1
            self.canv_1 = self.dialog.canv_1
            self.fig_2 = self.dialog.fig_2
            self.canv_2 = self.dialog.canv_2
            self.fig_3 = self.dialog.fig_3
            self.canv_3 = self.dialog.canv_3
            self.fig_4 = self.dialog.fig_4
            self.canv_4 = self.dialog.canv_4
            self.fig_5 = self.dialog.fig_5
            self.canv_5 = self.dialog.canv_5
            self.fig_6 = self.dialog.fig_6
            self.canv_6 = self.dialog.canv_6
            self.fig_7 = self.dialog.fig_7
            self.canv_7 = self.dialog.canv_7
            self.fig_8 = self.dialog.fig_8
            self.canv_8 = self.dialog.canv_8
            self.fig_9 = self.dialog.fig_9
            self.canv_9 = self.dialog.canv_9
            self.fig_10 = self.dialog.fig_10
            self.canv_10 = self.dialog.canv_10
            self.comboBox_2 = self.dialog.comboBox_2.currentText()
            #self.comboBox_3 = self.dialog.comboBox_3.currentText()
            self.comboBox_8 = self.dialog.comboBox_9.currentText()
            self.comboBox_9 = self.dialog.comboBox_9.currentText()
            self.dat_1 = self.dialog.lineEdit.text()
            self.dat_2 = self.dialog.lineEdit_2.text()
            self.dat_3 = self.dialog.lineEdit_3.text()
            self.check = self.dialog.checkBox_2.isChecked()

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected

            test = Info(self.fig_1, self.canv_1, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.fig_4,
                        self.canv_4, self.fig_5, self.canv_5, self.fig_6, self.canv_6, self.fig_7, self.canv_7,
                        self.fig_8, self.canv_8, self.fig_9, self.canv_9, self.fig_10, self.canv_10, self.comboBox_2,
                         self.comboBox_8, self.comboBox_9, self.dat_1, self.dat_2, self.dat_3,
                        DBConnection(),self.check)
            test.run()
            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            # self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            self.info_dlg.tf_qkanversion.setText(str(QKan.qgsVersion))
            #self.info_dlg.textBrowser_3.setText(str(test.anz_haltungen))
            #self.info_dlg.textBrowser_4.setText(str(test.anz_schaechte))
            #self.info_dlg.textBrowser_5.setText(str(test.laenge_haltungen))
            #self.info_dlg.tf_anz_teilgeb.setText(str(test.anz_teilgeb))

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

