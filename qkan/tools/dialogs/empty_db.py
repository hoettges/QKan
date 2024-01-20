import logging
import os
from typing import TYPE_CHECKING, List, Optional

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.tools.k_qgsadapt import qgsadapt

from . import QKanDBDialog, QKanProjectDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_empty_db, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_emptyDB.ui")
)

logger = logging.getLogger("QKan.tools.dialogs.empty_db")


class EmptyDBDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_empty_db):  # type: ignore
    epsg: QgsProjectionSelectionWidget

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.open_mode = False
        self.db_qkan: DBConnection = None

    def run(self) -> None:
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_qkanDB.setText(QKan.config.database.qkan)
        self.tf_projectFile.setText(QKan.config.project.file)
        self.show()

        if self.exec_():
            QKan.config.database.qkan = self.tf_qkanDB.text()
            QKan.config.project.file = self.tf_projectFile.text()
            QKan.config.epsg = int(self.epsg.crs().postgisSrid())
            QKan.config.save()

            self._doemptydb()

            # Load project
            # noinspection PyArgumentList
            QgsProject.instance().read(QKan.config.project.file)

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für HE-Import füllen"""

        daten = [
            ('Regenwasser', 'R', 'Regenwasser', 1, 2, 'R', 'KR', 0, 0),
            ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1, 'S', 'KS', 0, 0),
            ('Mischwasser', 'M', 'Mischwasser', 0, 0, 'M', 'KM', 0, 0),
            ('RW Druckleitung', 'RD', 'Transporthaltung ohne Anschlüsse', 1, 2, None, 'DR', 1, 1),
            ('SW Druckleitung', 'SD', 'Transporthaltung ohne Anschlüsse', 2, 1, None, 'DS', 1, 1),
            ('MW Druckleitung', 'MD', 'Transporthaltung ohne Anschlüsse', 0, 0, None, 'DW', 1, 1),
            ('RW nicht angeschlossen', 'RT', 'Transporthaltung ohne Anschlüsse', 1, 2, None, None, 1, 0),
            ('MW nicht angeschlossen', 'MT', 'Transporthaltung ohne Anschlüsse', 0, 0, None, None, 1, 0),
            ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, None, None, 0, None),
            ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None, 0, None),
        ]

        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau, transport, druckdicht)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?"""
        if not self.db_qkan.sql(sql, "he8_import Referenzlisten", daten, many=True):
            return False

        daten = [
            ('Haltung', None),
            ('Drossel', 'HYSTEM-EXTRAN 8'),
            ('H-Regler', 'HYSTEM-EXTRAN 8'),
            ('Q-Regler', 'HYSTEM-EXTRAN 8'),
            ('Schieber', 'HYSTEM-EXTRAN 8'),
            ('GrundSeitenauslass', 'HYSTEM-EXTRAN 8'),
            ('Pumpe', None),
            ('Wehr', None),
        ]
        sql = "INSERT INTO haltungstypen (bezeichnung, bemerkung) VALUES (?, ?)"

        if not self.db_qkan.sql(sql, "he8_import Referenzliste haltungstypen", daten, many=True):
            return False


        daten = [
            ('Kreis', 1, 1, None),
            ('Rechteck (geschlossen)', 2, 3, None),
            ('Ei (B:H = 2:3)', 3, 5, None),
            ('Maul (B:H = 2:1,66)', 4, 4, None),
            ('Halbschale (offen) (B:H = 2:1)', 5, None, None),
            ('Kreis gestreckt (B:H=2:2.5)', 6, None, None),
            ('Kreis überhöht (B:H=2:3)', 7, None, None),
            ('Ei überhöht (B:H=2:3.5)', 8, None, None),
            ('Ei breit (B:H=2:2.5)', 9, None, None),
            ('Ei gedrückt (B:H=2:2)', 10, None, None),
            ('Drachen (B:H=2:2)', 11, None, None),
            ('Maul (DIN) (B:H=2:1.5)', 12, None, None),
            ('Maul überhöht (B:H=2:2)', 13, None, None),
            ('Maul gedrückt (B:H=2:1.25)', 14, None, None),
            ('Maul gestreckt (B:H=2:1.75)', 15, None, None),
            ('Maul gestaucht (B:H=2:1)', 16, None, None),
            ('Haube (B:H=2:2.5)', 17, None, None),
            ('Parabel (B:H=2:2)', 18, None, None),
            ('Rechteck mit geneigter Sohle (B:H=2:1)', 19, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:1)', 20, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:2)', 21, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.2B)', 22, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.2B)', 23, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.2B)', 24, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.4B)', 25, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.4B)', 26, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.4B)', 27, None, None),
            ('Druckrohrleitung', 50, None, None),
            ('Sonderprofil', 68, 2, None),
            ('Gerinne', 69, None, None),
            ('Trapez (offen)', 900, None, None),
            ('Doppeltrapez (offen)', 901, None, None),
        ]

        sql = "INSERT INTO profile (profilnam, he_nr, mu_nr, kp_key) VALUES (?, ?, ?, ?)"

        if not self.db_qkan.sql(sql, "he8_import Referenzliste profile", daten, many=True):
            return False

        daten = [
            ('$Default_Bef', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, None, None, '2011-01-13 08:44'),
            ('$Default_Unbef', 'Standart qkhe', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', 'Grünfläche', '2011-01-13 08:44'),
            ('Gebäude', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, None, 'Gebäude', '2020-01-13 14:13'),
            ('Straße', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, None, 'Straße', '2020-01-13 14:13'),
            ('Grünfläche', 'Standart qkhe', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', 'Grünfläche', '2020-01-13 14:13'),
            ('Gewässer', 'Standart qkhe', 0, 0, 0, 0, 0, 0, None, 'Gewässer', '2020-01-13 14:13'),
        ]

        sql = """INSERT INTO abflussparameter
                 ( apnam, kommentar, anfangsabflussbeiwert, endabflussbeiwert, benetzungsverlust, 
                   muldenverlust, benetzung_startwert, mulden_startwert, bodenklasse, flaechentyp, 
                   createdat) Values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste abflussparameter", daten, many=True):
            return False

        daten = [
            ('VollDurchlaessig', 10, 9, 10, 144, 1.584, 100, '2011-01-13 08:44:50', 'Importiert mit qg2he'),
            ('Sand', 2.099, 0.16, 1.256, 227.9, 1.584, 12, '2011-01-13 08:44:50', 'Importiert mit qg2he'),
            ('SandigerLehm', 1.798, 0.101, 1.06, 143.9, 0.72, 18, '2011-01-13 08:44:50', 'Importiert mit qg2he'),
            ('LehmLoess', 1.601, 0.081, 0.94, 100.2, 0.432, 23, '2011-01-13 08:44:50', 'Importiert mit qg2he'),
            ('Ton', 1.9, 0.03, 1.087, 180, 0.144, 16, '2011-01-13 08:44:50', 'Importiert mit qg2he'),
            ('Undurchlaessig', 0, 0, 0, 100, 1, 0, '2011-01-13 08:44:50', 'Importiert mit qg2he'),
            (None, 0, 0, 0, 0, 0, 0, '2011-01-13 08:44:50', 'nur für interne QKan-Aufgaben'),
        ]

        sql = """INSERT INTO bodenklassen
                 ( 'bknam', 'infiltrationsrateanfang', 'infiltrationsrateende', 'infiltrationsratestart', 
                   'rueckgangskonstante', 'regenerationskonstante', 'saettigungswassergehalt', 
                   'createdat', 'kommentar') Values (?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste bodenklassen", daten, many=True):
            return False

        self.db_qkan.commit()
        return True

    def _doemptydb(self):

        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as self.db_qkan:
            if not self.db_qkan.connected:
                fehlermeldung("Fehler beim Erstellen der Datenbank:\n")
                return

            logger.debug('empty_db(2)')

            if QKan.config.project.file == "":
                return

            logger.debug(f'empty_db(5): project_file={QKan.config.project.file}')

            self._reftables()

            # Create project file
            qgsadapt(
                QKan.config.database.qkan,
                self.db_qkan,
                QKan.config.project.file,
                None,
                QKan.config.epsg
            )
