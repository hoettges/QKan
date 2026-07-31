from .base_test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.strakatporter.application import StrakatPorter


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestSTRAKATQKan(QgisTest):
    case = 3
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        dataset = [
            "test_strakatImport.zip",
            "test_strakat_Wegberg_Server.zip",
            "test_strakat_rommerskirchen.zip",
            "test_strakat_juelich.zip",
        ][cls.case]
        with ZipFile(BASE_DATA / dataset) as z:
            z.extractall(BASE_WORK)

    @classmethod
    def test_import(cls) -> None:
        database, project, importdir = [
            [
                "test.sqlite",
                "plan.qgs",
                "strakat",
            ],
            [
                "wegberg.sqlite",
                "wegberg.qgs",
                "Wegberg_OpenStrakat_Server"
            ],
            [
                "rommerskirchen.sqlite",
                "rommerskirchen.qgs",
                "strakat"
            ],
            [
                "juelich.sqlite",
                "plan.qgs",
                "strakat"
            ],
        ][cls.case]
        QKan.config.database.qkan = str(BASE_WORK / database)
        QKan.config.project.file = str(BASE_WORK / project)
        QKan.config.strakat.import_dir = str(BASE_WORK / importdir)


        QKan.config.check_import.haltungen = True
        QKan.config.check_import.schaechte = True
        QKan.config.check_import.hausanschluesse = True
        QKan.config.check_import.schachtschaeden = True
        QKan.config.check_import.haltungsschaeden = True
        QKan.config.check_import.hausanschluesse = True
        QKan.config.check_import.testmodus = True

        QKan.config.check_import.abflussparameter = False
        QKan.config.check_import.rohrprofile = False
        QKan.config.check_import.bodenklassen = False

        QKan.config.check_import.allrefs = False

        QKan.config.strakat.coords_from_rohr = True

        QKan.config.epsg = 25832

        imp = StrakatPorter(iface())
        erg = imp._doimport()

        LOGGER.debug("erg (Validate_STRAKAT_Export): %s", erg)
        if not erg:
            LOGGER.info("Fehler in TestSTRAKATQKan")

        del erg

        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()
