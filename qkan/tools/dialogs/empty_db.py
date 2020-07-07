import os
import typing

from qgis.PyQt import uic
from qgis.gui import QgsProjectionSelectionWidget

from . import QKanDBDialog, QKanProjectDialog

if typing.TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_empty_db, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_emptyDB.ui")
)


class EmptyDBDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_empty_db):
    epsg: QgsProjectionSelectionWidget

    def __init__(self, plugin: "QKanTools", parent=None):
        super().__init__(plugin, parent)
