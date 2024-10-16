import os
from typing import Callable, Optional

from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsDataSourceUri, Qgis
from qgis.utils import iface
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QTableWidget,
)
from qkan.database.qkan_utils import (
    get_database_QKan,
)

from qkan import QKan

class _Dialog(QDialog):
    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)
        self.default_dir = str(default_dir)
        self.tr = tr
        self.canv_1 = None



INFO_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "info2.ui")
)


class InfoDialog(_Dialog, INFO_CLASS):  # type: ignore
    tf_qkanversion: QLineEdit
    tf_anz_teilgeb: QLineEdit
    textBrowser_7: QLineEdit
    textBrowser_8: QLineEdit
    textBrowser_9: QLineEdit
    textBrowser_10: QLineEdit
    textBrowser_11: QLineEdit
    textBrowser_12: QLineEdit
    textBrowser_13: QLineEdit
    tableWidget: QTableWidget
    tableWidget_2: QTableWidget
    pb_exportExcel: QPushButton
    pb_exportXML: QPushButton
    date: QLineEdit


    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        self.pb_exportExcel.clicked.connect(self.export)
        self.pb_exportXML.clicked.connect(self.export_xml)

        self.filename = ''


    def select_date(self):

        try:
            database_qkan, epsg = get_database_QKan()
            if not database_qkan:
                return
            db_x = database_qkan #Datenbank name

            uri = QgsDataSourceUri()
            uri.setDatabase(db_x)
            schema = ''
            table = 'haltungen_untersucht'
            geom_column = 'geom'
            uri.setDataSource(schema, table, geom_column)
            vlayer = QgsVectorLayer(uri.uri(), 'haltungen_untersucht', 'spatialite')
            list = []
            for feature in vlayer.getFeatures():
                name = feature["untersuchtag"]
                name = str(name)[0:4]
                if str(name) == 'NULL':
                    pass
                elif name in list:
                    pass
                else:
                    list.append(name)

            self.date.clear()
            self.date.addItems(list)
            if list ==[]:
                try:
                    db_x = self.db.text()

                    uri = QgsDataSourceUri()
                    uri.setDatabase(db_x)
                    schema = ''
                    table = 'schaechte_untersucht'
                    geom_column = 'geop'
                    uri.setDataSource(schema, table, geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), 'schaechte_untersucht', 'spatialite')
                    list = []
                    for feature in vlayer.getFeatures():
                        name = feature["untersuchtag"]
                        name = str(name)[0:4]
                        if str(name) == 'NULL':
                            pass
                        elif name in list:
                            pass
                        else:
                            list.append(name)

                    self.date.clear()
                    self.date.addItems(list)
                except:
                    pass
        except:
            pass


    def export(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        self.filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende Excel-Datei"),
            self.default_dir,
            "*.xlsx",
        )
        if self.filename:
            #self.tf_import.setText(filename)
            self.default_dir = os.path.dirname(self.filename)

    def export_xml(self) -> None:
        # noinspection PyArgumentList,PyCallByClass
        self.filename_xml, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende Excel-Datei"),
            self.default_dir,
            "*.xml",
        )
        if self.filename_xml:
            #self.tf_import.setText(filename)
            self.default_dir = os.path.dirname(self.filename_xml)





