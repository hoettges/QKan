import os
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QWidget

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "importSWMM.ui")
)


class ImportSWMMDialog(QDialog, FORM_CLASS):  # type: ignore
    def __init__(self, parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super(ImportSWMMDialog, self).__init__(parent)
        self.setupUi(self)
