import os
from typing import Callable, Optional

from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsDataSourceUri
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
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


ZUSTAND_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "zustandsklassen_dialog_base.ui")
)


class ZustandDialog(_Dialog, ZUSTAND_CLASS):  # type: ignore
    db: QLineEdit
    date: QLineEdit

    epsg: QgsProjectionSelectionWidget

    checkBox: QCheckBox
    checkBox_1: QCheckBox
    checkBox_2: QCheckBox
    checkBox_3: QCheckBox
    checkBox_4: QCheckBox
    checkBox_5: QCheckBox
    checkBox_6: QCheckBox
    checkBox_7: QCheckBox
    checkBox_8: QCheckBox
    checkBox_9: QCheckBox
    checkBox_10: QCheckBox
    checkBox_11: QCheckBox
    checkBox_12: QCheckBox
    checkBox_13: QCheckBox
    checkBox_14: QCheckBox


    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        #if 'db' in self.config:
         #   db = self.config['db']
        #else:
         #   db = ''
        #self.dlg.db.setText(db)

        self.pushButton.clicked.connect(self.select_db)

        self.db.textChanged.connect(self.select_date)
        self.checkBox.clicked.connect(self.checkBox_click)
        self.checkBox_2.clicked.connect(self.checkBox_click_2)
        self.checkBox_4.clicked.connect(self.checkBox_click_4)
        self.checkBox_6.clicked.connect(self.checkBox_click_6)
        self.checkBox_12.clicked.connect(self.checkBox_click_12)
        self.checkBox_13.clicked.connect(self.checkBox_click_13)

        # Init fields
        self.db.setText(QKan.config.database.qkan)
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))


    def checkBox_click(self):
        if self.checkBox.isChecked():
            self.checkBox.setChecked(1)
            self.checkBox_2.setChecked(0)

        else:
            self.checkBox.setChecked(0)
            self.checkBox_2.setChecked(1)

    def checkBox_click_2(self):
        if self.checkBox.isChecked():
            self.checkBox.setChecked(0)
            self.checkBox_2.setChecked(1)

        else:
            self.checkBox.setChecked(1)
            self.checkBox_2.setChecked(0)

    def checkBox_click_4(self):
        if self.checkBox.isChecked():
            self.checkBox_6.setChecked(0)
            self.checkBox_4.setChecked(1)

        else:
            self.checkBox_6.setChecked(1)
            self.checkBox_4.setChecked(0)

    def checkBox_click_6(self):
        if self.checkBox.isChecked():
            self.checkBox_6.setChecked(1)
            self.checkBox_4.setChecked(0)

        else:
            self.checkBox_6.setChecked(0)
            self.checkBox_4.setChecked(1)

    def checkBox_click_12(self):
        if self.checkBox.isChecked():
            self.checkBox_13.setChecked(0)
            self.checkBox_12.setChecked(1)

        else:
            self.checkBox_13.setChecked(1)
            self.checkBox_12.setChecked(0)

    def checkBox_click_13(self):
        if self.checkBox.isChecked():
            self.checkBox_13.setChecked(1)
            self.checkBox_12.setChecked(0)

        else:
            self.checkBox_13.setChecked(0)
            self.checkBox_12.setChecked(1)


    def select_db(self):
        filename, _filter = QFileDialog.getOpenFileName(self, "Datenbank wählen", "", '*.sqlite')
        self.db.setText(filename)

        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))



    def select_date(self):

        try:
            db_x = self.db.text()

            uri = QgsDataSourceUri()
            uri.setDatabase(db_x)
            schema = ''
            table = 'Untersuchdat_haltung'
            geom_column = 'geom'
            uri.setDataSource(schema, table, geom_column)
            vlayer = QgsVectorLayer(uri.uri(), 'Untersuchdat_haltung', 'spatialite')
            list = []
            for feature in vlayer.getFeatures():
                name = feature["createdat"]
                name=name[0:16]
                if name in list:
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
                    table = 'Untersuchdat_schacht'
                    geom_column = 'geop'
                    uri.setDataSource(schema, table, geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), 'Untersuchdat_schacht', 'spatialite')
                    list = []
                    for feature in vlayer.getFeatures():
                        name = feature["createdat"]
                        name = name[0:16]
                        if name in list:
                            pass
                        else:
                            list.append(name)

                    self.date.clear()
                    self.date.addItems(list)
                except:
                    pass
        except:
            pass
