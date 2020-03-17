from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.core import QgsProject
from qgis.testing import unittest

import sys, os

sys.path.append(os.path.join(os.path.split(__file__)[0],'..'))

from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.exportswmm.k_qksw import exportKanaldaten
from qkan.importswmm.importswmm import importKanaldaten
from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest
from qkan.tools.k_layersadapt import layersadapt

class TestSwmm2QKan(QgisTest):
    """Aktuell nur als Vorlage. Muss noch programmiert werden"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_swmmImport.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self):
        database_qkan = BASE_WORK / "tutorial.sqlite"
        swmmfile = BASE_WORK / "tutorial.inp"
        project_file = BASE_WORK / "plan.qgs"

        layersadapt(
            database_QKan= str(database_qkan),
            projectTemplate= "",
            dbIsUptodate= False,
            qkanDBUpdate= True,
            anpassen_Datenbankanbindung= False,
            anpassen_Wertebeziehungen_in_Tabellen= False,
            anpassen_Formulare= False,
            anpassen_Projektionssystem= False,
            aktualisieren_Schachttypen= False,
            zoom_alles= False,
            fehlende_layer_ergaenzen= False,
            anpassen_auswahl= enums.SelectedLayers.NONE,
        )

        erg = importKanaldaten(
            inpfile=str(swmmfile),
            database_QKan=str(database_qkan),
            projectfile=str(project_file),
            epsg=3044,
        )

        LOGGER.debug("erg (Validate_Swmm_Import): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")

class TestQKan2Swmm(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_swmmExport.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self):
        database_qkan = BASE_WORK / "nette.sqlite"
        swmmfile = BASE_WORK / "nette.inp"
        template_swmm = BASE_WORK / "swmm_vorlage.inp"

        layersadapt(
            database_QKan= str(database_qkan),
            projectTemplate= "",
            dbIsUptodate= False,
            qkanDBUpdate= True,
            anpassen_Datenbankanbindung= False,
            anpassen_Wertebeziehungen_in_Tabellen= False,
            anpassen_Formulare= False,
            anpassen_Projektionssystem= False,
            aktualisieren_Schachttypen= False,
            zoom_alles= False,
            fehlende_layer_ergaenzen= False,
            anpassen_auswahl= enums.SelectedLayers.NONE,
        )

        erg = exportKanaldaten(
            iface=self.iface,
            databaseQKan=str(database_qkan),
            templateSwmm=str(template_swmm),
            ergfileSwmm=str(swmmfile),
            mit_verschneidung=True,
            liste_teilgebiete=['Fa20', 'Fa22', 'Fa23', 'Fa25'],
        )

        LOGGER.debug("erg (Validate_Swmm_export): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

if __name__ == "__main__":
    unittest.main()
