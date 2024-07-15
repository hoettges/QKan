from qkan.database.dbfunc import DBConnection
from base_test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile
from pathlib import Path

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.swmmporter.application import SWMMPorter
from qkan.tools.k_dbAdapt import dbAdapt


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestSWMM2QKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_swmmImport.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "tutorial.sqlite")             # 4: Simple_green_roof_example
        QKan.config.swmm.import_file = str(BASE_WORK / "tutorial.inp")             # 4: Simple_green_roof_example
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")

        imp = SWMMPorter(iface())
        erg = imp._doimport()

        LOGGER.debug("erg (Validate_SWMM_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in TestSWMMQKan")
        # self.assertTrue(False, "Fehlernachricht")


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKan2SWMM(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_swmmExport.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "nette.sqlite")
        QKan.config.swmm.export_file = str(BASE_WORK / "nette.imp")
        QKan.config.swmm.template = str(BASE_WORK / "swmm_vorlage.inp")

        # Datenbank auf aktuelle Version aktualisieren
        dbAdapt(qkanDB=QKan.config.database.qkan,)

        QKan.config.check_export.schaechte = True
        QKan.config.check_export.auslaesse = False
        QKan.config.check_export.speicher = True
        QKan.config.check_export.haltungen = True
        QKan.config.check_export.pumpen = False
        QKan.config.check_export.wehre = False
        QKan.config.check_export.flaechen = True
        QKan.config.check_export.einleitdirekt = False
        QKan.config.check_export.aussengebiete = False
        QKan.config.check_export.einzugsgebiete = False
        QKan.config.check_export.tezg = True

        QKan.config.check_export.abflussparameter = False
        QKan.config.check_export.bodenklassen = False

        QKan.config.check_export.append = True
        QKan.config.check_export.update = False
        QKan.config.check_export.synch = False

        imp = SWMMPorter(iface())
        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:
            erg = imp._doexport(db_qkan)

        LOGGER.debug(f"erg (Validate_SWMM_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanSWMM")

        del imp
        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()
