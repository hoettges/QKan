from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile
from pathlib import Path

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.isyporter.application import IsyPorter
from qkan.tools.k_dbAdapt import dbAdapt


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestISYQKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_isybau_aj_import.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "test.sqlite")
        QKan.config.xml.import_file = str(BASE_WORK / "Datenausgabe ISYBAU-2017_29-01-21.xml")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")
        QKan.config.epsg = 25832

        imp = IsyPorter(iface())
        erg = imp._doimport()

        LOGGER.debug("erg (Validate_ISY_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in Test150QKan")
        # self.assertTrue(False, "Fehlernachricht")


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKanISY(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_dynaExport.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "nette.sqlite")
        QKan.config.xml.export_file = str(BASE_WORK / "nette.xml")

        dbAdapt(
            qkanDB=QKan.config.database.qkan,
        )

        QKan.config.check_export.schaechte = True
        QKan.config.check_export.auslaesse = True
        QKan.config.check_export.speicher = True
        QKan.config.check_export.haltungen = True
        QKan.config.check_export.pumpen = True
        QKan.config.check_export.wehre = True
        QKan.config.check_export.flaechen = True
        QKan.config.check_export.einleitdirekt = False
        QKan.config.check_export.aussengebiete = False
        QKan.config.check_export.einzugsgebiete = True
        QKan.config.check_export.tezg = True

        QKan.config.check_export.abflussparameter = True
        QKan.config.check_export.bodenklassen = True

        QKan.config.check_export.append = True
        QKan.config.check_export.update = False
        QKan.config.check_export.synch = False

        exp = IsyPorter(iface())
        erg = exp._doexport()

        LOGGER.debug(f"erg (Validate_ISY_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanISY")

        del exp
        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
