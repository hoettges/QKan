from .base_test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.m150porter.application import M150Porter
from qkan.database.dbfunc import DBConnection

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestM150QKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        # with ZipFile(BASE_DATA / "test_m150Import_kanalprofi.zip") as z:
        with ZipFile(BASE_DATA / "test_m150Import_barbarastrasse.zip") as z:
        # with ZipFile(BASE_DATA / 'test_m150Import.zip') as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        # QKan.config.database.qkan = str(BASE_WORK / "HKuSuHA.sqlite")
        # QKan.config.xml.import_file = str(BASE_WORK / "HKuSuHA.xml")
        # QKan.config.xml.import_file = str(BASE_WORK / "M150_2_Z_2010_HKuSuHA.xml")
        # QKan.config.xml.import_file = str(BASE_WORK / "M150_Z_2010_HKuSuHA.xml")

        # QKan.config.database.qkan = str(BASE_WORK / "alsdorf.sqlite")
        # QKan.config.xml.import_file = str(BASE_WORK / "Alsdorf_Test_mit Zustand_25832.xml")

        # QKan.config.database.qkan = str(BASE_WORK / "lemgo.sqlite")
        # QKan.config.xml.import_file = str(BASE_WORK / "Lemgo_test_DWA-M_150.XML")

        # QKan.config.database.qkan = str(BASE_WORK / "maarbruecke.sqlite")
        # QKan.config.xml.import_file = str(BASE_WORK / "An der Maarbruecke ABK 3394.xml")
        #
        QKan.config.database.qkan = str(BASE_WORK / "test.sqlite")
        QKan.config.xml.import_file = str(BASE_WORK / "barbarastrasse_AP1_5.xml")

        QKan.config.project.file = str(BASE_WORK / "test.qgs")
        QKan.config.epsg = 25832

        imp = M150Porter(iface())
        erg = imp._doimport()

        LOGGER.debug("erg (Validate_M150_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in Test150QKan")
        # self.assertTrue(False, "Fehlernachricht")


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKanM150(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_dynaExport.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "nette.sqlite")
        QKan.config.xml.export_file = str(BASE_WORK / "nette.xml")

        QKan.config.selections.selectedObjects = False

        with DBConnection(
                dbname=QKan.config.database.qkan,
                qkan_db_update=True,
                writeDbBackup=False,
                writeQgsBackup=False,
        ) as dbQK:  # Datenbankobjekt zur Aktualisierung öffnen

            if not dbQK.connected:
                errormsg = (
                    "Fehler in k_qgsadapt:\n"
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"
                )
                raise Exception(f"{__name__}: {errormsg}")

            dbQK.sql("SELECT RecoverSpatialIndex()")  # Geometrie-Indizes bereinigen

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

        imp = M150Porter(iface())
        erg = imp._doexport()

        LOGGER.debug(f"erg (Validate_M150_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanM150")

        del imp
        # self.assertTrue(False, "Fehlernachricht")


# Testdatensatz TV-Inspektion aus Abnahmebefahrung ATD
class TestM150_BA6(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_m150Import_BA6.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "ba6.sqlite")
        QKan.config.xml.import_file = str(BASE_WORK / "E24E0261 Hattinger Str. BA6 KANALERNEUERUNG Haltungen.xml")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")
        QKan.config.epsg = 25832

        imp = M150Porter(iface())
        erg = imp._doimport()

        LOGGER.debug("erg (Validate_M150_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in Test150QKan")
        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()
