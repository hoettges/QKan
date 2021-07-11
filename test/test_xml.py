from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest, iface
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

from qkan import QKan, enums
from qkan.tools.k_dbAdapt import dbAdapt
from qkan.tools.k_layersadapt import layersadapt
from qkan.xmlporter.application import XmlPorter


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestXmlQKan(QgisTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_isybau_aj_import.zip") as z:
            z.extractall(BASE_WORK)

    def test_import(self) -> None:
        QKan.config.database.qkan = str(BASE_WORK / "guissem.sqlite")
        QKan.config.xml.import_file = str(
            BASE_WORK / "Datenausgabe ISYBAU-2017_29-01-21.xml"
        )
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")

        imp = XmlPorter(iface())
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
        # project_file = str(BASE_WORK / "plan_export.qgs")
        QKan.config.he8.template = str(BASE_WORK / "muster_vorlage.idbm")

        # project = QgsProject.instance()
        # project.read(project_file)
        # LOGGER.debug("Geladene Projektdatei: %s", project.fileName())

        dbAdapt(qkanDB=QKan.config.database.qkan)

        layersadapt(
            database_QKan=QKan.config.database.qkan,
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
        imp.connectQKanDB(QKan.config.database.qkan)
        erg = imp._doexport()

        LOGGER.debug(f"erg (Validate_HE8_export): {erg}")
        if not erg:
            LOGGER.info("Fehler in TestQKanHE8")

        del imp
        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
