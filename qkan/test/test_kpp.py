from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.core import QgsProject
from qgis.testing import unittest

from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.exportdyna.k_qkkp import exportKanaldaten
from qkan.importdyna.import_from_dyna import importKanaldaten
from qkan.test import BASE_DIR, LOGGER, QgisTest


class TestKpp(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DIR / "data/kpp.zip") as z:
            z.extractall(BASE_DIR / "data")

            for name in z.namelist():
                name = BASE_DIR / "data" / name
                if name not in cls.files:
                    cls.files.append(name)

    def test_import(self):
        database_qkan = BASE_DIR / "data/Oleanderweg.sqlite"
        dynafile = BASE_DIR / "data/Oleanderweg.ein"
        project_file = BASE_DIR / "data/plan.qgs"
        self.files += [database_qkan, dynafile, project_file]

        erg = importKanaldaten(
            dynafile=str(dynafile),
            database_QKan=str(database_qkan),
            projectfile=str(project_file),
            epsg=3044,
            dbtyp="SpatiaLite",
        )

        LOGGER.debug("erg (Validate_KPP_Import): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")

    def test_export(self):
        database_qkan = BASE_DIR / "data/nette.sqlite"
        dynafile = BASE_DIR / "data/nette.ein"
        project_file = BASE_DIR / "data/plan_export.qgs"
        template_dyna = BASE_DIR / "data/dyna_vorlage.ein"
        self.files += [database_qkan, dynafile, project_file, template_dyna]

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
            datenbanktyp="SpatiaLite",
        )

        LOGGER.debug("erg (Validate_KPP_export): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        del db


if __name__ == "__main__":
    unittest.main()
