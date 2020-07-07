import os
import typing

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QPushButton,
)
from qgis.gui import QgsMapLayerComboBox

from . import QKanDBDialog

if typing.TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_read_data, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_readData.ui")
)


class ReadDataDialog(QKanDBDialog, FORM_CLASS_read_data):
    button_box: QDialogButtonBox
    cbLayerSchaechte_2: QgsMapLayerComboBox
    cbLayerSchaechte_3: QgsMapLayerComboBox
    cbLayerSchaechte_4: QgsMapLayerComboBox
    cbLayerSchaechte_5: QgsMapLayerComboBox
    cbLayerSchaechte_6: QgsMapLayerComboBox
    cbLayerSchaechte: QgsMapLayerComboBox

    pbSchaechteFromClipboard_2: QPushButton
    pbSchaechteFromClipboard_3: QPushButton
    pbSchaechteFromClipboard_4: QPushButton
    pbSchaechteFromClipboard_5: QPushButton
    pbSchaechteFromClipboard_6: QPushButton
    pbSchaechteFromClipboard: QPushButton

    def __init__(self, plugin: "QKanTools", parent=None):
        super().__init__(plugin, parent)
