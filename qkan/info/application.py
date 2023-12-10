from qgis.gui import QgisInterface
from qgis.core import QgsProject
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin
from qkan.database.qkan_database import qgs_version
from qkan.database.qkan_utils import warnung

from PyQt5.QtWidgets import QTableWidgetItem

from ._info import Info
from .application_dialog import InfoDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip
import pandas as pd
import os
from qgis.utils import iface
from qgis.core import Qgis


class Infos(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.info_dlg = InfoDialog(default_dir=self.default_dir, tr=self.tr)
        self.info_dlg.pushButton.clicked.connect(self.run_info)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/info/res/info.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Infos zum QKan Projekt"),
            callback=self.run_info,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.info_dlg.close()

    def run_info(self) -> None:
        # Prüfen, ob ein Projekt geladen ist
        project = QgsProject.instance()
        layers = project.mapLayers()

        self.info_dlg.select_date()
        if len(layers) > 0:

            # with DBConnection() as db_qkan:
            #     connected = db_qkan.connected

            test = Info(DBConnection())
            test.run(self.info_dlg.date.currentText())
            # Vorgabe Projektname aktivieren, wenn kein Projekt geladen
            #self.info_dlg.gb_projectfile.setEnabled(QgsProject.instance().fileName() == '')

            self.info_dlg.show()
            version = qgs_version()
            self.info_dlg.textBrowser_2.setText(str(version))
            self.info_dlg.textBrowser_3.setText(str(test.anz_haltungen))
            self.info_dlg.textBrowser_4.setText(str(test.anz_schaechte))
            self.info_dlg.textBrowser_5.setText(str(test.laenge_haltungen))
            self.info_dlg.textBrowser_6.setText(str(test.anz_teilgeb))

            #Felder Haltungen
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

            #Felder Schäachte

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

            #export Excel
            if self.info_dlg.filename != '':

                cwd = os.path.dirname(os.path.abspath(__file__))
                file = cwd + '/suewvo.xlsx'
                df = pd.read_excel(file, header=None, sheet_name='Beauftragte')
                df1 = pd.read_excel(file, header=None, sheet_name='KS - Kanäle und Schachtbauwerke')
                df2 = pd.read_excel(file, header=None, sheet_name='GAL - Grundstücksanschlussleit')
                df3 = pd.read_excel(file, header=None, sheet_name='DK - Düker')
                df4 = pd.read_excel(file, header=None, sheet_name='PW - Abwasserpumpwerke')
                df5 = pd.read_excel(file, header=None, sheet_name='DL - Druckleitungen (o.N.)')
                df6 = pd.read_excel(file, header=None, sheet_name='DN - Drucknetze')
                df7 = pd.read_excel(file, header=None, sheet_name='RÜ - Regenüberläufe')
                df8 = pd.read_excel(file, header=None, sheet_name='RB - Regenbecken')
                df9 = pd.read_excel(file, header=None, sheet_name='EB - Einleitungsbauwerk')
                df10 = pd.read_excel(file, header=None, sheet_name='ÜP - Übergangspunkte')

                df1.loc[19, 1] = str(test.laenge_haltungen_rw)
                df1.loc[20, 1] = str(test.laenge_haltungen_sw)
                df1.loc[21, 1] = str(test.laenge_haltungen_mw)
                df1.loc[19, 2] = str(test.haltungen_0_rw)
                df1.loc[20, 2] = str(test.haltungen_0_sw)
                df1.loc[21, 2] = str(test.haltungen_0_mw)
                df1.loc[19, 3] = str(test.haltungen_1_rw)
                df1.loc[20, 3] = str(test.haltungen_1_sw)
                df1.loc[21, 3] = str(test.haltungen_1_mw)
                df1.loc[19, 4] = str(test.haltungen_2_rw)
                df1.loc[20, 4] = str(test.haltungen_2_sw)
                df1.loc[21, 4] = str(test.haltungen_2_mw)
                df1.loc[19, 5] = str(test.haltungen_3_rw)
                df1.loc[20, 5] = str(test.haltungen_3_sw)
                df1.loc[21, 5] = str(test.haltungen_3_mw)
                df1.loc[19, 6] = str(test.haltungen_4_rw)
                df1.loc[20, 6] = str(test.haltungen_4_sw)
                df1.loc[21, 6] = str(test.haltungen_4_mw)
                df1.loc[19, 7] = str(test.haltungen_5_rw)
                df1.loc[20, 7] = str(test.haltungen_5_sw)
                df1.loc[21, 7] = str(test.haltungen_5_mw)
                df1.loc[19, 8] = str(test.laenge_haltungen_untersuch_rw)
                df1.loc[20, 8] = str(test.laenge_haltungen_untersuch_sw)
                df1.loc[21, 8] = str(test.laenge_haltungen_untersuch_mw)
                df1.loc[19, 9] = str(test.laenge_haltungen_untersuch_bj_rw)
                df1.loc[20, 9] = str(test.laenge_haltungen_untersuch_bj_sw)
                df1.loc[21, 9] = str(test.laenge_haltungen_untersuch_bj_mw)
                df1.loc[19, 10] = str(test.laenge_haltungen_saniert_rw)
                df1.loc[20, 10] = str(test.laenge_haltungen_saniert_sw)
                df1.loc[21, 10] = str(test.laenge_haltungen_saniert_mw)

                df1.loc[27, 1] = str(test.anz_schaechte_rw)
                df1.loc[28, 1] = str(test.anz_schaechte_sw)
                df1.loc[29, 1] = str(test.anz_schaechte_mw)
                df1.loc[27, 2] = str(test.anz_schaechte_0_rw)
                df1.loc[28, 2] = str(test.anz_schaechte_0_sw)
                df1.loc[29, 2] = str(test.anz_schaechte_0_mw)
                df1.loc[27, 3] = str(test.anz_schaechte_1_rw)
                df1.loc[28, 3] = str(test.anz_schaechte_1_sw)
                df1.loc[29, 3] = str(test.anz_schaechte_1_mw)
                df1.loc[27, 4] = str(test.anz_schaechte_2_rw)
                df1.loc[28, 4] = str(test.anz_schaechte_2_sw)
                df1.loc[29, 4] = str(test.anz_schaechte_2_mw)
                df1.loc[27, 5] = str(test.anz_schaechte_3_rw)
                df1.loc[28, 5] = str(test.anz_schaechte_3_sw)
                df1.loc[29, 5] = str(test.anz_schaechte_3_mw)
                df1.loc[27, 6] = str(test.anz_schaechte_4_rw)
                df1.loc[28, 6] = str(test.anz_schaechte_4_sw)
                df1.loc[29, 6] = str(test.anz_schaechte_4_mw)
                df1.loc[27, 7] = str(test.anz_schaechte_5_rw)
                df1.loc[28, 7] = str(test.anz_schaechte_5_sw)
                df1.loc[29, 7] = str(test.anz_schaechte_5_mw)
                df1.loc[27, 8] = str(test.anz_schaechte_untersuch_rw)
                df1.loc[28, 8] = str(test.anz_schaechte_untersuch_sw)
                df1.loc[29, 8] = str(test.anz_schaechte_untersuch_mw)
                df1.loc[27, 9] = str(test.anz_schaechte_untersuch_bj_rw)
                df1.loc[28, 9] = str(test.anz_schaechte_untersuch_bj_sw)
                df1.loc[29, 9] = str(test.anz_schaechte_untersuch_bj_mw)
                df1.loc[27, 10] = str(test.anz_schaechte_saniert_rw)
                df1.loc[28, 10] = str(test.anz_schaechte_saniert_sw)
                df1.loc[29, 10] = str(test.anz_schaechte_saniert_mw)


                # Änderungen speichern
                #with pd.ExcelWriter(self.info_dlg.filename, mode='A', if_sheet_exists='replace') as writer:
                with pd.ExcelWriter(self.info_dlg.filename) as writer:
                    df.to_excel(writer, sheet_name='Beauftragte', index=False)
                    df1.to_excel(writer, sheet_name='KS - Kanäle und Schachtbauwerke', index=False)
                    df2.to_excel(writer, sheet_name='GAL - Grundstücksanschlussleit', index=False)
                    df3.to_excel(writer, sheet_name='DK - Düker', index=False)
                    df4.to_excel(writer, sheet_name='PW - Abwasserpumpwerk', index=False)
                    df5.to_excel(writer, sheet_name='DL - Druckleitungen (o.N.)', index=False)
                    df6.to_excel(writer, sheet_name='DN - Drucknetze', index=False)
                    df7.to_excel(writer, sheet_name='RÜ - Regenüberläufe', index=False)
                    df8.to_excel(writer, sheet_name='RB - Regenbecken', index=False)
                    df9.to_excel(writer, sheet_name='EB - Einleitungsbauwerk', index=False)
                    df10.to_excel(writer, sheet_name='ÜP - Übergangspunkte', index=False)

            # Run the dialog event loop
            result = self.info_dlg.exec_()

        else:
            warnung('Hinweis', 'Es ist kein Projekt geladen!')
