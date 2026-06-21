from .base_test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile
from pathlib import Path

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.isyporter.application import IsyPorter
from qkan.database.dbfunc import DBConnection


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestISYQKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        # with ZipFile(BASE_DATA / "test_isybau_aj_import.zip") as z:
        # with ZipFile(BASE_DATA / "test_ISYBAU13_HKuSuHA.zip") as z:
        with ZipFile(BASE_DATA / "test_isy_Import_tum.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        # QKan.config.database.qkan = str(BASE_WORK / "blankenhd.sqlite")
        QKan.config.database.qkan = str(BASE_WORK / "metelen.sqlite")
        # QKan.config.xml.import_file = str(BASE_WORK / "Datenausgabe ISYBAU-2017_29-01-21.xml")
        # QKan.config.xml.import_file = str(BASE_WORK / "ISYBAU13_HKuSuHA.xml")
        QKan.config.xml.import_file = str(BASE_WORK / "Metelen Gemeinde-Metelen 2026 Metelen 2026-Neu.XML")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")
        QKan.config.fotoRootPath = "C:/FHAC/hoettges/Kanalprogramme/QKan/test/work/fotos"
        QKan.config.fotoPathCurrent = "C:/FHAC/hoettges/Kanalprogramme/QKan/test/work/fotos"
        QKan.config.xml.import_stamm = True
        QKan.config.xml.import_haus = True
        QKan.config.xml.import_zustand = True
        QKan.config.xml.import_teilbefahrung = False
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

        QKan.config.selections.selectedObjects = False

        exp = IsyPorter(iface())
        erg = exp._doexport()

        LOGGER.debug(f"erg (Validate_ISY_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanISY")

        del exp
        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
