import logging
from pathlib import Path
from unittest import mock

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMainWindow

# noinspection PyUnresolvedReferences
from qgis.gui import QgisInterface
from qgis.testing import start_app, unittest

from qkan import QKan

LOGGER = logging.getLogger("QGIS")

BASE_DIR = Path(__file__).parent


def iface():
    _iface = mock.Mock(spec=QgisInterface)

    _mainwindow = QMainWindow()
    _iface.mainWindow.return_value = _mainwindow
    return _iface


class QgisTest(unittest.TestCase):
    files = []
    qgs = start_app()

    @classmethod
    def setUpClass(cls) -> None:
        LOGGER.info("Setting up tests")

        QSettings().setValue("locale/userLocale", "deutsch")

        cls.iface = iface()
        cls.qkan = QKan(cls.iface)
        cls.qkan.initGui()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.qgs.exitQgis()

        for _file in cls.files:
            if _file.exists():
                _file.unlink()
