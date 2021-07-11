from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.muporter.application import MuPorter
from qkan.tools.k_dbAdapt import dbAdapt


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestMUQKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_mu2021Import.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.mu.database = str(BASE_WORK / "urban_qk.sqlite")
        QKan.config.mu.import_file = str(BASE_WORK / "Urban flooding.sqlite")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")

        imp = MuPorter(iface())
        erg = imp._doimport()

        LOGGER.debug("erg (Validate_MU_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in TestMUQKan")
        # self.assertTrue(False, "Fehlernachricht")


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKanMU(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_MUExport.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self) -> None:
        QKan.config.mu.database = str(BASE_WORK / "urban_qk.sqlite")
        QKan.config.mu.export_file = str(BASE_WORK / "Urban flooding.sqlite")
        # project_file = str(BASE_WORK / "plan_export.qgs")
        QKan.config.mu.template = str(BASE_WORK / "mu_vorlage.sqlite")

        # project = QgsProject.instance()
        # project.read(project_file)
        # LOGGER.debug("Geladene Projektdatei: %s", project.fileName())

        dbAdapt(qkanDB=QKan.config.mu.database)

        # layersadapt(
        #     database_QKan=QKan.config.mu.database,
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
        QKan.config.check_export.rohrprofile = False

        QKan.config.check_export.append = True
        QKan.config.check_export.update = False
        QKan.config.check_export.synch = False

        imp = MuPorter(iface())
        imp.connectQKanDB(QKan.config.mu.database)
        erg = imp._doexport()

        LOGGER.debug(f"erg (Validate_MU_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanMU")

        del imp
        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
