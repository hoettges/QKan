from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.strakatporter.application import StrakatPorter


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestSTRAKATQKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_strakatImport.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "test.sqlite")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")
        QKan.config.strakat.import_dir = str(BASE_WORK / "strakat")

        QKan.config.check_import.haltungen = True
        QKan.config.check_import.schaechte = True
        QKan.config.check_import.hausanschluesse = True
        QKan.config.check_import.schachtschaeden = False
        QKan.config.check_import.haltungsschaeden = False

        QKan.config.check_import.abflussparameter = False
        QKan.config.check_import.rohrprofile = False
        QKan.config.check_import.bodenklassen = False

        QKan.config.check_import.allrefs = False

        imp = StrakatPorter(iface())
        erg = imp._doimport()

        LOGGER.debug("erg (Validate_MU_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in TestMUQKan")

        del erg

        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()
