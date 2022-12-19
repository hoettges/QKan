from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.surfaceTools.surfaceTool import SurfaceTask
from qkan.tools.k_dbAdapt import dbAdapt
from qgis.core import QgsApplication


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestCutOverlaps(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_surfaceCutOverlaps.zip") as z:
            z.extractall(BASE_WORK)

    def test_cut(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "itwh.sqlite")
        database_qkan = QKan.config.database.qkan
        dbAdapt(qkanDB=database_qkan,)

        # obj = SurfaceTools(iface())
        # obj.connectQKanDB(QKan.config.database.qkan)
        overlap = SurfaceTask(iface(), database_qkan, epsg=25832, dbtyp="SpatiaLite")
        schneiden = 'Dach'
        geschnitten = '$Default_Unbef'
        erg = overlap.run_cut(schneiden, geschnitten)

        LOGGER.debug("erg (Validate_CutOverlaps): %s", erg)
        if not erg:
            LOGGER.info("Fehler in TestCutOverlaps")
        # self.assertTrue(False, "Fehlernachricht")

        del erg


# TestCreateVoronoi funktioniert nicht, weil processing.run in surfaceTool.py meldet: 'qgis.processing' has no attribute 'run'

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
# class TestCreateVoronoi(QgisTest):
#     @classmethod
#     def setUpClass(cls) -> None:
#         super().setUpClass()
#
#         # Extract files
#         with ZipFile(BASE_DATA / "test_voronoi.zip") as z:
#             z.extractall(BASE_WORK)
#
#     def test_voronoi(self) -> None:
#         QKan.config.database.qkan = str(BASE_WORK / "demo.sqlite")
#
#         database_qkan = QKan.config.database.qkan
#         dbAdapt(qkanDB=database_qkan,)
#
#         liste_entwarten = ['Mischwasser']
#         erg = SurfaceTask(iface(), database_qkan, epsg=25832, dbtyp="SpatiaLite")
#         erg.run_voronoi(liste_entwarten)
#         LOGGER.debug("erg (Validate_CreateVoronoi): %s", erg)
#         if not erg:
#             LOGGER.info("Fehler in TestCreateVoronoi")
#         # self.assertTrue(False, "Fehlernachricht")
#
#         del erg

if __name__ == "__main__":
    unittest.main()
