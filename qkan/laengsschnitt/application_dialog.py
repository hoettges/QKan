import os
from typing import Callable, Optional

from PyQt6 import QtCore
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
    QComboBox,
    QDialogButtonBox,
    QLabel,
    QSlider,
)
from qgis.core import Qgis
from qgis.utils import iface

from qkan.tools.qkan_utils import get_qkanlayer_attributes
from qkan.utils import get_logger

logger = get_logger("QKan.laengs.application_dialog")


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

    buttonBox_2: QDialogButtonBox
    pushButton: QPushButton
    pushButton_2: QPushButton
    pushButton_3: QPushButton
    lineEdit: QLineEdit
    lineEdit_2: QLineEdit
    label: QLabel
    label_4: QLabel
    #lineEdit_3: QLineEdit
    pushButton_4: QPushButton
    pushButton_5: QPushButton
    lineEdit_4: QLineEdit
    pushButton_6: QPushButton
    pushButton_7: QPushButton
    comboBox: QComboBox
    checkBox: QCheckBox
    horizontalSlider_3: QSlider
    geschw_2: QSlider


    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        # Attach events
        help_button = self.buttonBox_2.button(QDialogButtonBox.Help)
        help_button.clicked.disconnect()
        help_button.clicked.connect(self.click_help)
        self.pushButton.clicked.connect(self.export_cad)
        self.pushButton_2.clicked.connect(self.refresh)
        self.checkBox.stateChanged.connect(self.check)
        self.pushButton_3.clicked.connect(self.show_selection)
        self.pushButton_5.clicked.connect(self.ganglinie)
        self.pushButton_6.clicked.connect(self.animiert_laengs)
        self.geschw_2.sliderReleased.connect(self.slider_geschw_released)
        #self.geschw_2.sliderReleased.connect(self.animiert_laengs)
        #self.horizontalSlider_3.sliderMoved.connect(self.animiert_laengs)
        #self.horizontalSlider_3.sliderPressed.connect(self.stop_laengs)
        self.horizontalSlider_3.sliderReleased.connect(self.slider_released)
        self.pushButton_7.clicked.connect(self.select_erg)
        self.checkBox.toggled.connect(self.clicked)
        self.refresh_function = None
        self.export_cad_function = None
        self.show_function = None
        self.gang_function = None
        self.animiert_laengs = None
        self.fig = None
        self.canv = None
        self.fig_2 = None
        self.canv_2 = None
        self.fig_3 = None
        self.canv_3 = None
        self.database = None
        self.selected = None
        self.auswahl = {}
        self.anf = 0
        self.max = False
        self.features = []
        self.anim = None
        self.point = self.lineEdit.text()
        self.massstab = self.lineEdit_2.text()
        self.db_erg = self.lineEdit_4.text()
        list_schacht = ["Zufluss", "Wasserstand", "Wassertiefe", "Durchfluss"]
        list_haltung = ["Durchfluss", "Geschwindigkeit", "Auslastung", "Wassertiefe"]
        layer = iface.activeLayer()
        if layer is None:
            logger.warning("Bitte wählen Sie für den Längsschnitt Haltungen oder Schächte aus")
            return
        x = layer.source()

        dbname, table, geom, sql = get_qkanlayer_attributes(x)

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.MessageLevel.Critical)
            return

        if table == 'schaechte':
            self.comboBox.clear()
            self.comboBox.addItems(list_schacht)
        if table == 'haltungen':
            self.comboBox.clear()
            self.comboBox.addItems(list_haltung)

        self.ausgabe = self.comboBox.currentText()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.pushButton_4.click()

    def clicked(self):
        self.max = True

    def check(self):
        if self.checkBox.isChecked():
            self.refresh()

    def slider_geschw_released(self):
        self.canv_2.flush_events()
        self.fig_2.clear()
        self.db_erg = self.lineEdit_4.text()
        self.anf = self.horizontalSlider_3.value()
        self.animiert_laengs_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3,
                                      self.canv_3, self.selected, self.auswahl,
                                      self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max,
                                      self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)

    def slider_released(self):
        self.canv_2.flush_events()
        self.fig_2.clear()
        self.anf = self.horizontalSlider_3.value()
        self.db_erg = self.lineEdit_4.text()
        self.animiert_laengs_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3,
                                      self.canv_3, self.selected, self.auswahl,
                                      self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max,
                                      self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)


    def export_cad(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellende DXF-Datei"),
            self.default_dir,
            "*.dxf",
        )
        if filename:
            self.lineEdit.setText(filename)

        self.db_erg = self.lineEdit_4.text()
        self.point = self.lineEdit.text()
        self.massstab = self.lineEdit_2.text()
        self.export_cad_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl, self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)

    def show_selection(self):
        self.db_erg = self.lineEdit_4.text()
        self.show_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl, self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)

    def refresh(self):
        self.fig.clear()
        self.db_erg = self.lineEdit_4.text()
        #self.refresh_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl, self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)

        if self.refresh_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl, self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf) == 'nicht erstellt':
            self.label.setText('Bitte Elemente vom Schacht- oder Haltungslayer auswählen und den "refresh" Knopf drücken!')

        else:
            self.label.setText('')
            #self.refresh_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl, self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)

    def select_erg(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Zu importierende Hystem-Extran Ergebnisse"),
            self.default_dir,
            "*.idbr",
        )

        if filename:
            self.lineEdit_4.setText(filename)

    def ganglinie(self):
        self.fig_3.clear()
        self.db_erg = self.lineEdit_4.text()
        self.ausgabe = self.comboBox.currentText()
        self.gang_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl, self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)

    def animiert_laengs(self):
        self.canv_2.flush_events()
        self.fig_2.clear()
        #self.anf = 0
        self.anf = self.horizontalSlider_3.value()
        self.db_erg = self.lineEdit_4.text()
        self.animiert_laengs_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl,
                           self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)


    # def stop_laengs(self):
    #     self.anf = 0
    #     self.canv_2.flush_events()
    #     self.fig_2.clear()
    #     self.db_erg = self.lineEdit_4.text()
    #     self.stop_function(self.database, self.fig, self.canv, self.fig_2, self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl,
    #                        self.point, self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4, self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf)
    #

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_Daten.html#langsschnitt"
        os.startfile(help_file)
