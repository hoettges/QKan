from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile
from pathlib import Path

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan
from qkan.he8porter.application import He8Porter
from qkan.tools.k_dbAdapt import dbAdapt


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestHE8QKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_he8Import.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "itwh.sqlite")
        QKan.config.he8.import_file = str(BASE_WORK / "modell.idbm")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")

        imp = He8Porter(iface())
        erg = imp._doimport()

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

    def test_export(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "itwh.sqlite")
        QKan.config.he8.export_file = str(BASE_WORK / "itwh.idbm")
        QKan.config.he8.template = str(BASE_WORK / "muster_vorlage.idbm")

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

        imp = He8Porter(iface())
        erg = imp._doexport()

        LOGGER.debug(f"erg (Validate_HE8_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanHE8")

        del imp
        # self.assertTrue(False, "Fehlernachricht")


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestQKanUpdateHE8(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_he8_Export_only_update.zip") as z:
            z.extractall(BASE_WORK)

    def test_export(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "itwh.sqlite")
        QKan.config.he8.export_file = str(BASE_WORK / "itwh.idbm")
        QKan.config.he8.template = str(BASE_WORK / "muster_vorlage.idbm")

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

        QKan.config.check_export.append = False
        QKan.config.check_export.update = True
        QKan.config.check_export.synch = False

        imp = He8Porter(iface())
        erg = imp._doexport()

        LOGGER.debug(f"erg (Validate_HE8_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanUpdateHE8")

        del imp
        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
