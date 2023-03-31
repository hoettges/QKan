import os
import sys
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

sys.path.append(os.path.join(os.path.split(__file__)[0], ".."))

from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface

from qkan.datacheck.application import Plausi
from qkan.database.dbfunc import DBConnection


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestPlausi(QgisTest):
    """Test des Moduls Plausi"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_plausi.zip") as z:
            z.extractall(BASE_WORK)

    def test_plausi(self) -> None:
        database_qkan = str(BASE_WORK / "modell.sqlite")
        db_qkan = DBConnection(database_qkan, qkan_db_update=True)              # inkl. automatischem DB-Update

        test = Plausi(iface())
        test._doplausi(db_qkan)

        # self.assertTrue(False, "Fehlernachricht")

        LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
