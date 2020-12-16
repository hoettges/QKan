import os
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLabel, QWidget

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "surfaceTool.ui")
)


class SurfaceToolDialog(QDialog, FORM_CLASS):  # type: ignore
    buttonBox: QDialogButtonBox
    label_2: QLabel
    label: QLabel
    layoutWidget: QWidget

    def __init__(self, parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super(SurfaceToolDialog, self).__init__(parent)
        self.setupUi(self)
