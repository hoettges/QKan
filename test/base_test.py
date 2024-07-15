import logging
import os
import shutil
from pathlib import Path
from unittest import mock

# noinspection PyUnresolvedReferences
from qgis.gui import QgisInterface, QgsMessageBar
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMainWindow
from qgis.testing import start_app, unittest

from qkan import QKan

LOGGER = logging.getLogger("QKan.tests")

BASE_DIR = Path(__file__).parent
BASE_DATA = BASE_DIR / "data"
BASE_WORK = BASE_DIR / "work"


def iface() -> QgisInterface:
    _iface = mock.Mock(spec=QgisInterface)

    # noinspection PyArgumentList
    _iface.mainWindow.return_value = QMainWindow()
    _iface.messageBar.return_value = QgsMessageBar()

    return _iface


class QgisTest(unittest.TestCase):
    qgs = start_app()

    @classmethod
    def setUpClass(cls) -> None:
        LOGGER.info("Setting up tests")

        QSettings().setValue("locale/userLocale", "deutsch")

        cls.iface = iface()
        cls.qkan = QKan(cls.iface)
        cls.qkan.initGui()

        # Clean work dir
        if BASE_WORK.exists():
            for f in BASE_WORK.iterdir():
                if f.is_dir():
                    shutil.rmtree(f)
                else:
                    f.unlink()

        os.makedirs(BASE_WORK, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.qgs.exitQgis()
