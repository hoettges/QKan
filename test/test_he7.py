from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest
from qkan_he7.exporthe.export_to_he7 import exportKanaldaten
from qkan_he7.importhe.import_from_he import importKanaldaten

from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.tools.k_layersadapt import layersadapt


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestHE7QKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_he7Import.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        database_qkan = str(BASE_WORK / "itwh.sqlite")
        he7file = str(BASE_WORK / "muster-modelldatenbank.idbf")
        project_file = str(BASE_WORK / "plan.qgs")

        erg = importKanaldaten(
            database_HE=he7file,
            database_QKan=database_qkan,
            projectfile=project_file,
            epsg=31467,
        )

        LOGGER.debug("erg (Validate_HE7_Import): %s", erg)
        if not erg:
            LOGGER.info("Fehler in TestHE7QKan")
        # self.assertTrue(False, "Fehlernachricht")


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKanHE7(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_he7Export.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self) -> None:
        database_qkan = str(BASE_WORK / "modell.sqlite")
        database_he7 = str(BASE_WORK / "modell.idbf")
        # project_file = str(BASE_WORK / "plan_export.qgs")
        template_he7 = str(BASE_WORK / "muster_nur_bauwerke.idbf")

        # project = QgsProject.instance()
        # project.read(project_file)
        # LOGGER.debug("Geladene Projektdatei: %s", project.fileName())

        layersadapt(
            database_QKan=database_qkan,
            projectTemplate="",
            anpassen_ProjektMakros=False,
            anpassen_Datenbankanbindung=False,
            anpassen_Wertebeziehungen_in_Tabellen=False,
            anpassen_Formulare=False,
            anpassen_Projektionssystem=False,
            aktualisieren_Schachttypen=False,
            zoom_alles=False,
            fehlende_layer_ergaenzen=False,
            anpassen_auswahl=enums.SelectedLayers.NONE,
        )

        db = DBConnection(dbname=database_qkan)
        if not db.connected:
            raise Exception("Datenbank nicht gefunden oder nicht aktuell.")

        exportChoice = {
            "export_schaechte": True,
            "export_auslaesse": False,
            "export_speicher": True,
            "export_haltungen": True,
            "export_pumpen": False,
            "export_wehre": False,
            "export_flaechenrw": True,
            "export_einleitdirekt": False,
            "export_aussengebiete": False,
            "export_abflussparameter": False,
            "export_regenschreiber": False,
            "export_rohrprofile": False,
            "export_speicherkennlinien": False,
            "export_bodenklassen": False,
            "modify_schaechte": True,
            "modify_auslaesse": False,
            "modify_speicher": True,
            "modify_haltungen": True,
            "modify_pumpen": False,
            "modify_wehre": False,
            "modify_flaechenrw": True,
            "modify_einleitdirekt": False,
            "modify_aussengebiete": False,
            "modify_abflussparameter": False,
            "modify_regenschreiber": False,
            "modify_rohrprofile": False,
            "modify_speicherkennlinien": False,
            "modify_bodenklassen": False,
            "combine_flaechenrw": False,
            "combine_einleitdirekt": False,
        }

        erg = exportKanaldaten(
            self.iface,
            database_he=database_he7,
            dbtemplate_he=template_he7,
            db_qkan=db,
            liste_teilgebiete=[],
            autokorrektur=False,
            fangradius=0.1,
            mindestflaeche=0.5,
            mit_verschneidung=True,
            export_flaechen_he8=False,
            check_export=exportChoice,
        )

        LOGGER.debug("erg (Validate_HE7_export): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        del db
        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
