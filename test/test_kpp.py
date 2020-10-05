from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.core import QgsProject
from qgis.testing import unittest

from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.exportdyna.export_to_dyna import export_kanaldaten
from qkan.importdyna.import_from_dyna import import_kanaldaten
from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest
from qkan.tools.k_layersadapt import layersadapt

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestKpp2QKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_dynaImport.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self):
        database_qkan = str(BASE_WORK / "Oleanderweg.sqlite")
        dynafile = str(BASE_WORK / "Oleanderweg.ein")
        project_file = str(BASE_WORK / "plan.qgs")

        erg = import_kanaldaten(
            dynafile=dynafile,
            database_qkan=database_qkan,
            projectfile=project_file,
            epsg=3044,
        )

        LOGGER.debug("erg (Validate_KPP_Import): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")
        # self.assertTrue(False, "Fehlernachricht")

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKan2Kpp(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_dynaExport.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self):
        database_qkan = str(BASE_WORK / "nette.sqlite")
        dynafile = str(BASE_WORK / "nette.ein")
        #project_file = str(BASE_WORK / "plan_export.qgs")
        template_dyna = str(BASE_WORK / "dyna_vorlage.ein")

        #project = QgsProject.instance()
        #project.read(project_file)
        #LOGGER.debug("Geladene Projektdatei: %s", project.fileName())

        layersadapt(
            database_QKan= database_qkan,
            projectTemplate= "",
            dbIsUptodate= False,
            qkanDBUpdate= True,
            anpassen_ProjektMakros= False,
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

        erg = export_kanaldaten(
            self.iface,
            dynafile=dynafile,
            template_dyna=template_dyna,
            db_qkan=db,
            dynabef_choice=enums.BefChoice.FLAECHEN,
            dynaprof_choice=enums.ProfChoice.PROFILNAME,
            liste_teilgebiete="[]",
            profile_ergaenzen=True,
            autonum_dyna=True,
            mit_verschneidung=True,
            fangradius=0.1,
            mindestflaeche=0.5,
            max_loops=1000,
        )

        LOGGER.debug("erg (Validate_KPP_export): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        del db
        # self.assertTrue(False, "Fehlernachricht")



if __name__ == "__main__":
    unittest.main()
