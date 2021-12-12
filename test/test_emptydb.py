import os
import sys
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

sys.path.append(os.path.join(os.path.split(__file__)[0], ".."))

from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface

from qkan.tools.dialogs.empty_db import EmptyDBDialog

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestPlausi(QgisTest):
    """Test des Moduls Plausi"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files: No files necessary

    def test_emptyDB(self) -> None:

        test = EmptyDBDialog(iface())
        test._doemptydb()

        # self.assertTrue(False, "Fehlernachricht")

        LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()
