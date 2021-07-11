import os
import sys
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

sys.path.append(os.path.join(os.path.split(__file__)[0], ".."))

from test import BASE_DATA, BASE_WORK, LOGGER, QgisTest

from qkan import enums
from qkan.createunbeffl.k_unbef import create_unpaved_areas
from qkan.database.dbfunc import DBConnection
from qkan.linkflaechen.k_link import createlinkfl, createlinksw


# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestLinkfl(QgisTest):
    """Test des Moduls Linkfl"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_linkfl.zip") as z:
            z.extractall(BASE_WORK)

    def test_linkfl(self) -> None:
        database_qkan = str(BASE_WORK / "nette.sqlite")

        # Aktualisierung der Datenbank auf aktuelle Version
        # layersadapt(
        #     database_QKan=database_qkan,
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

        # Anbindung an die Datenbank, weil Module mit QKan-Objekt aufgerufen werden.
        db = DBConnection(dbname=database_qkan, qkan_db_update=True)
        if not db.connected:
            raise Exception("Datenbank nicht gefunden oder nicht aktuell.")

        # Erzeugen der unbefestigten Flächen
        erg = create_unpaved_areas(
            self.iface, db_qkan=db, selected_abflparam=[], autokorrektur=False
        )

        LOGGER.debug("erg (Validate_createUnbefFlaechen): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")

        # Erzeugen der Flächenanbindungen
        erg = createlinkfl(
            self.iface,
            db_qkan=db,
            liste_flaechen_abflussparam=[],
            liste_hal_entw=[],
            liste_teilgebiete=[],
            links_in_tezg=True,
            mit_verschneidung=True,
            autokorrektur=False,
            flaechen_bereinigen=False,
            suchradius=50.0,
            mindestflaeche=0.5,
            fangradius=0.1,
            bezug_abstand=enums.BezugAbstand.KANTE,
        )

        LOGGER.debug("erg (Validate_createlinkfl): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")

        # Erzeugen der Anbindungen der SW-Einleiter
        erg = createlinksw(
            self.iface,
            db_qkan=db,
            liste_teilgebiete=[],
            suchradius=50.0,
            epsg=25832,
        )

        LOGGER.debug("erg (Validate_createlinksw): %s", erg)
        if not erg:
            LOGGER.info("Nicht ausgeführt, weil zuerst QKan-DB aktualisiert wurde.!")

        # self.assertTrue(False, "Fehlernachricht")


if __name__ == "__main__":
    unittest.main()
