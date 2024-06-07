from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile
from pathlib import Path

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.m150porter.application import M150Porter
from qkan.tools.k_dbAdapt import dbAdapt


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestM150QKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_m150Import.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "alsdorf.sqlite")
        QKan.config.xml.import_file = str(BASE_WORK / "Alsdorf_Test_mit Zustand_25832.xml")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")

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
        with ZipFile(BASE_DATA / "test_M150Export.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "itwh.sqlite")
        QKan.config.m150.export_file = str(BASE_WORK / "itwh.idbm")
        QKan.config.m150.template = str(BASE_WORK / "muster_vorlage.idbm")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")

        dbAdapt(
            qkanDB=QKan.config.database.qkan,
        )

        # Nicht nötig für Test:
        # layersadapt(
        #     database_QKan=QKan.config.database.qkan,
        #     projectTemplate="",
        #     anpassen_ProjektMakros=False,
        #     anpassen_Datenbankanbindung=False,
        #     anpassen_Wertebeziehungen_in_Tabellen=False,
        #     anpassen_Formulare=False,
        #     anpassen_Projektionssystem=False,
        #     aktualisieren_Schachttypen=False,
        #     zoom_alles=False,
        #     fehlende_layer_ergaenzen=False,
        #     anpassen_auswahl=enums.SelectedLayers.NONE,
        # )
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


if __name__ == "__main__":
    unittest.main()
