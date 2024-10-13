import os
import sys
from pathlib import Path

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

#sys.path.append(os.path.join(os.path.split(__file__)[0], ".."))

from base_test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from qkan import QKan

from qkan.tools.dialogs.empty_db import EmptyDBDialog

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestPlausi(QgisTest):
    """Test des Moduls Plausi"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files: No files necessary

    def test_emptyDB(self) -> None:

        QKan.config.database.qkan = str(BASE_WORK / "test.sqlite")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")
        QKan.config.epsg = 25832

        test = EmptyDBDialog(iface())
        test._doemptydb()
        del test
        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()
