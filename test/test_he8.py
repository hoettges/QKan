from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.core import QgsProject
from qgis.testing import unittest

from qkan import enums
from qkan.database.dbfunc import DBConnection
#from qkan.importhe8.import_from_he8 import importhe8
from qkan.exporthe8.export_to_he8 import exporthe8
from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest
from qkan.tools.k_layersadapt import layersadapt

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestHE8QKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_he8Import.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self):
        database_qkan = str(BASE_WORK / "itwh.sqlite")
        he8file = str(BASE_WORK / "muster-modelldatenbank.idbf")
        project_file = str(BASE_WORK / "plan.qgs")

        erg = importKanaldaten(
            database_HE=he8file,
            database_QKan=database_qkan,
            projectfile=project_file,
            epsg=31467,
        )

        LOGGER.debug("erg (Validate_HE8_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in TestHE8QKan")
        # self.assertTrue(False, "Fehlernachricht")

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKanHE8(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_he8Export.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self):
        database_qkan = str(BASE_WORK / "itwh.sqlite")
        database_he8 = str(BASE_WORK / "itwh.idbm")
        #project_file = str(BASE_WORK / "plan_export.qgs")
        template_he8 = str(BASE_WORK / "muster_vorlage.idbm")

        #project = QgsProject.instance()
        #project.read(project_file)
        #LOGGER.debug("Geladene Projektdatei: %s", project.fileName())

        layersadapt(
            database_QKan= database_qkan,
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

        db = DBConnection(dbname=database_qkan)
        if not db.connected:
            raise Exception("Datenbank nicht gefunden oder nicht aktuell.")

        exportChoice = {'export_schaechte': True, 'export_auslaesse': False, 'export_speicher': True, 'export_haltungen': True,
             'export_pumpen': False, 'export_wehre': False, 'export_flaechenrw': True, 'export_einleitdirekt': False,
             'export_aussengebiete': False, 'export_abflussparameter': False, 'export_regenschreiber': False,
             'export_rohrprofile': False, 'export_speicherkennlinien': False, 'export_bodenklassen': False,
             'modify_schaechte': True, 'modify_auslaesse': False, 'modify_speicher': True, 'modify_haltungen': True,
             'modify_pumpen': False, 'modify_wehre': False, 'modify_flaechenrw': True, 'modify_einleitdirekt': False,
             'modify_aussengebiete': False, 'modify_abflussparameter': False, 'modify_regenschreiber': False,
             'modify_rohrprofile': False, 'modify_speicherkennlinien': False, 'modify_bodenklassen': False,
             'combine_einleitdirekt': False}

        erg = exporthe8(
            iface=self.iface,
            database_HE=database_he8,
            dbtemplate_HE=template_he8,
            dbQK=db,
            liste_teilgebiete =[],
            autokorrektur=False,
            fangradius=0.1,
            mindestflaeche=0.5,
            mit_verschneidung=True,
            exportFlaechenHE8=False,
            check_export=exportChoice,
        )

        LOGGER.debug(f"erg (Validate_HE8_export): {erg}")
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        del db
        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()