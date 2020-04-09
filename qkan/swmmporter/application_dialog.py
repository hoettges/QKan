import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "importSWMM.ui")
)


class ImportSWMMDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ImportSWMMDialog, self).__init__(parent)
        self.setupUi(self)