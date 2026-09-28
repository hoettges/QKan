import os
from typing import TYPE_CHECKING, Optional
from typing import Callable, Optional
import webbrowser
from qgis.gui import QgisInterface
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QWidget,
    QTextBrowser,
    QDialog,
    QButtonGroup,
    QRadioButton,
)



if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

SELECT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), ".", "res", "selection.ui")
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
        self.tr = tr


class SelectionDialog(_Dialog, SELECT_CLASS):  # type: ignore
    button_box: QDialogButtonBox
    cb_selectFlaechen: QCheckBox
    cb_selectHaltungen: QCheckBox
    cb_selectSchaechte: QCheckBox
    obj_oberhalb: QPushButton
    obj_innerhalb: QPushButton
    obj_unterhalb: QPushButton
    obj_zwischen: QPushButton
    fliessweg: QPushButton



    def __init__(self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(default_dir, tr, parent)

        self.geklickter_button = None

        # Signale verbinden
        self.obj_innerhalb.clicked.connect(lambda: self.button_clicked("Teilgebiet"))
        self.obj_unterhalb.clicked.connect(lambda: self.button_clicked("unterhalb"))
        self.obj_zwischen.clicked.connect(lambda: self.button_clicked("kuerzester"))
        self.obj_oberhalb.clicked.connect(lambda: self.button_clicked("oberhalb"))
        self.fliessweg.clicked.connect(lambda: self.button_clicked("Fliessweg"))
        self.button_box.helpRequested.connect(self.click_help)

    def button_clicked(self, name):
        self.geklickter_button = name
        self.accept()

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""
        help_file = "https://qkan.eu/QKan_Daten.html#auswahl-erweitern-netzverfolgung"
        os.startfile(help_file)

