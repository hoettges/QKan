from base_test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.floodTools.application import FloodTools


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestHEFlood(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_heflood2d.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.epsg = 25832
        QKan.config.flood.import_dir = str(BASE_WORK / "Ergebnisse.result" / "Result2D.gdb")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")
        QKan.config.flood.database = str(BASE_WORK / "flood.sqlite")
        QKan.config.flood.velo = True
        QKan.config.flood.wlevel = True
        QKan.config.flood.gdblayer = False
        QKan.config.flood.faktor_v = 2.
        QKan.config.flood.min_v = 0.05
        QKan.config.flood.min_w = 0.05

        run = FloodTools(iface())
        erg = run._dofloodAnimation()

        LOGGER.debug(f"Validate_Flood2D: {erg=}")
        if not erg:
            self.assertTrue(False, "Test von Flood2D nicht erfolgreich!")


if __name__ == "__main__":
    unittest.main()
