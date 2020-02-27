from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.core import QgsProject
from qgis.testing import unittest

from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.exportdyna.k_qkkp import exportKanaldaten
from qkan.importdyna.import_from_dyna import importKanaldaten
from tests import BASE_DATA, BASE_WORK, LOGGER, QgisTest


class TestKpp(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "kpp.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self):
        database_qkan = BASE_WORK / "Oleanderweg.sqlite"
        dynafile = BASE_WORK / "Oleanderweg.ein"
        project_file = BASE_WORK / "plan.qgs"

        erg = importKanaldaten(
            dynafile=str(dynafile),
            database_QKan=str(database_qkan),
            projectfile=str(project_file),
            epsg=3044,
        )

        LOGGER.debug("erg (Validate_KPP_Import): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")

    def test_export(self):
        database_qkan = BASE_WORK / "nette.sqlite"
        dynafile = BASE_WORK / "nette.ein"
        project_file = BASE_WORK / "plan_export.qgs"
        template_dyna = BASE_WORK / "dyna_vorlage.ein"

        project = QgsProject.instance()
        project.read(str(project_file))
        LOGGER.debug("Geladene Projektdatei: %s", project.fileName())

        db = DBConnection(dbname=str(database_qkan))
        if not db.connected:
            raise Exception("Datenbank nicht gefunden oder nicht aktuell.")

        erg = exportKanaldaten(
            self.iface,
            dynafile=dynafile,
            template_dyna=template_dyna,
            dbQK=db,
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


if __name__ == "__main__":
    unittest.main()
