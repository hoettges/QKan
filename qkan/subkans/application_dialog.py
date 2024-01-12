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
    QDialogButtonBox,
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


SUBKANS_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "subkans_dialog_base.ui")
)


class SubkansDialog(_Dialog, SUBKANS_CLASS):  # type: ignore
    button_box: QDialogButtonBox
    db: QLineEdit
    date: QLineEdit

    epsg: QgsProjectionSelectionWidget

    checkBox_1: QCheckBox
    checkBox_2: QCheckBox
    checkBox_3: QCheckBox
    checkBox_4: QCheckBox
    checkBox_5: QCheckBox


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
        #self.checkBox_1.clicked.connect(self.checkBox_click)
        #self.checkBox_2.clicked.connect(self.checkBox_click_2)
        #self.checkBox_4.clicked.connect(self.checkBox_click_4)
        #self.checkBox_6.clicked.connect(self.checkBox_click_6)
        #self.checkBox_12.clicked.connect(self.checkBox_click_12)
        #self.checkBox_13.clicked.connect(self.checkBox_click_13)

        # Init fields
        self.db.setText(QKan.config.database.qkan)
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.button_box.helpRequested.connect(self.click_help)

    def select_db(self):
        filename, _filter = QFileDialog.getOpenFileName(self, "Datenbank wählen", "", '*.sqlite')
        self.db.setText(filename)

        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))

    def click_help(self) -> None:
        help_file = "https://www.subkans.de/"
        os.startfile(help_file)

    def select_date(self):

        try:
            db_x = self.db.text()

            uri = QgsDataSourceUri()
            uri.setDatabase(db_x)
            schema = ''
            table = 'untersuchdat_haltung'
            geom_column = 'geom'
            uri.setDataSource(schema, table, geom_column)
            vlayer = QgsVectorLayer(uri.uri(), 'untersuchdat_haltung', 'spatialite')
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
