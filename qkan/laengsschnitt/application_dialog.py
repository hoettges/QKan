import os
import logging
import sys
from typing import Callable, Optional
from qkan import QKan
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget
from qgis.utils import iface
from qgis.core import Qgis
from qgis.utils import pluginDirectory,iface
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QEvent
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QComboBox,
    QToolButton,
    QMessageBox,
    QDialogButtonBox,
    QLabel,

)

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


logger = logging.getLogger("QKan.laengs.application_dialog")


LAENGS_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "laengsschnitt.ui")
)


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
        logger.debug(
            f"laengs.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr



class LaengsDialog(_Dialog, LAENGS_CLASS):  # type: ignore

    buttonBox: QDialogButtonBox
    pushButton: QPushButton
    pushButton_2: QPushButton
    pushButton_3: QPushButton
    lineEdit: QLineEdit
    lineEdit_2: QLineEdit
    label: QLabel
    lineEdit_3: QLineEdit
    pushButton_4: QPushButton
    pushButton_5: QPushButton


    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        self.pushButton.clicked.connect(self.export_cad)
        self.pushButton_2.clicked.connect(self.refresh)
        self.pushButton_3.clicked.connect(self.show_selection)
        self.pushButton_4.clicked.connect(self.select_erg)
        self.pushButton_5.clicked.connect(self.ganglinie)
        self.refresh_function = None
        self.export_cad_function = None
        self.show_function = None
        self.gang_function = None
        self.fig = None
        self.canv = None
        self.database = None
        self.selected = None
        self.auswahl = {}
        self.features = []
        self.point = self.lineEdit.text()
        self.massstab = self.lineEdit_2.text()
        #self.pushButton_2.installEventFilter(self)


    #def eventFilter(self, _widget, event):
     #   if event.type() == QEvent.Enter:  # Catch the TouchBegin event.
      #      iface.messageBar().pushMessage("Fehler", 'Test', level=Qgis.Critical)
       #     return super(LaengsDialog, self).eventFilter(_widget, event)
       # else:
        #    return False


    def export_cad(self):
        self.export_cad_function(self.database, self.fig, self.canv, self.selected, self.auswahl, self.point, self.massstab, self.features)

    def show_selection(self):
        self.show_function(self.database, self.fig, self.canv, self.selected, self.auswahl, self.point, self.massstab, self.features)

    def refresh(self):
        self.refresh_function(self.database, self.fig, self.canv, self.selected, self.auswahl, self.point, self.massstab, self.features)

        if self.refresh_function(self.database, self.fig, self.canv, self.selected, self.auswahl, self.point, self.massstab, self.features) == 'nicht erstellt':
            self.label.setText('Bitte Elemente vom Schacht- oder Haltungslayer auswählen und den "refresh" Knopf drücken!')

        else:
            self.label.setText('')
            #self.auswahl = \
            self.refresh_function(self.database, self.fig, self.canv, self.selected, self.auswahl, self.point, self.massstab, self.features)

    def select_erg(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende Hystem-Extran Ergebnisse"),
            self.default_dir,
            "*.idbr",
        )

        if filename:
            self.lineEdit_3.setText(filename)

    def ganglinie(self):
        self.gang_function(self.database, self.fig, self.canv, self.selected, self.auswahl, self.point, self.massstab, self.features)




