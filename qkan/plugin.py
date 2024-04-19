from typing import cast

from qgis.PyQt.QtCore import QCoreApplication
from qgis.gui import QgisInterface

from qkan import get_default_dir
from qkan.utils import get_logger


class QKanPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.log = get_logger(f"QKan.{type(self).__name__}")
        self.default_dir = get_default_dir()

        self.log.info("Initialised.")

    # noinspection PyMethodMayBeStatic
    def tr(self, message: str) -> str:
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return cast(str, QCoreApplication.translate(type(self).__name__, message))

    def unload(self) -> None:
        """
        Override this if you initialized a QDialog anywhere
        """
