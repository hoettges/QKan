import os
from typing import TYPE_CHECKING, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import fehlermeldung
from qkan.tools.k_qgsadapt import qgsadapt
from qkan.utils import get_logger
from . import QKanDBDialog, QKanProjectDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_empty_db, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_emptyDB.ui")
)

logger = get_logger("QKan.tools.dialogs.empty_db")


class EmptyDBDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_empty_db):  # type: ignore
    epsg: QgsProjectionSelectionWidget

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.open_mode = False
        self.db_qkan: DBConnection = None
        self.button_box.helpRequested.connect(self.click_help)

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
            ('Regenwasser', 'R', 'Regenwasser', 1, 2, 'R', 'KR'),
            ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1, 'S', 'KS'),
            ('Mischwasser', 'M', 'Mischwasser', 0, 0, 'M', 'KM'),
            ('RW Druckleitung', 'RD', 'RW Druckleitung', 1, 2, None, 'DR'),
            ('SW Druckleitung', 'SD', 'RW Druckleitung', 2, 1, None, 'DS'),
            ('MW Druckleitung', 'MD', 'RW Druckleitung', 0, 0, None, 'DW'),
            ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, None, None),
            ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None),
        ]

        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau)
                    SELECT ?, ?, ?, ?, ?, ?, ?"""
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


        daten = [  # kurz    he    mu    kp  isy m150  m145
            ('Kreis', 'DN', 1, 1, None, 0, 'DN', None),
            ('Rechteck', 'RE', 2, 3, None, 3, 'RE', None),
            ('Ei (B:H = 2:3)', 'EI', 3, 5, None, 1, 'EI', None),
            ('Maul (B:H = 2:1.66)', 'MA', 4, 4, None, 2, 'MA', None),
            ('Halbschale (offen) (B:H = 2:1)', 'HS', 5, None, None, None, None, None),
            ('Kreis gestreckt (B:H=2:2.5)', None, 6, None, None, None, None, None),
            ('Kreis überhöht (B:H=2:3)', None, 7, None, None, None, None, None),
            ('Ei überhöht (B:H=2:3.5)', None, 8, None, None, None, None, None),
            ('Ei breit (B:H=2:2.5)', None, 9, None, None, None, None, None),
            ('Ei gedrückt (B:H=2:2)', None, 10, None, None, None, None, None),
            ('Drachen (B:H=2:2)', None, 11, None, None, None, None, None),
            ('Maul (DIN) (B:H=2:1.5)', None, 12, None, None, None, None, None),
            ('Maul überhöht (B:H=2:2)', None, 13, None, None, None, None, None),
            ('Maul gedrückt (B:H=2:1.25)', None, 14, None, None, None, None, None),
            ('Maul gestreckt (B:H=2:1.75)', None, 15, None, None, None, None, None),
            ('Maul gestaucht (B:H=2:1)', None, 16, None, None, None, None, None),
            ('Haube (B:H=2:2.5)', 'BO', 17, None, None, 11, 'BO', None),
            ('Parabel (B:H=2:2)', None, 18, None, None, None, None, None),
            ('Rechteck mit geneigter Sohle (B:H=2:1)', None, 19, None, None, None, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:1)', None, 20, None, None, None, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:2)', None, 21, None, None, None, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.2B)', None, 22, None, None, None, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.2B)', None, 23, None, None, None, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.2B)', None, 24, None, None, None, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.4B)', None, 25, None, None, None, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.4B)', None, 26, None, None, None, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.4B)', None, 27, None, None, None, None, None),
            ('Sonderprofil', 68, 2, None, None, None, None, None),
            ('Gerinne', 'RI', 69, None, None, None, None, None),
            ('Trapez (offen)', 'TR', 900, None, None, 8, None, None),
            ('Rechteck offen', None, None, None, None, 5, None, None),
            ('Doppeltrapez (offen)', None, 901, None, None, None, None, None),
            ('Offener Graben', 'GR', None, None, None, None, 'GR', None),
            ('Oval', 'OV', None, None, None, 12, 'OV', None),
        ]

        sql = "INSERT INTO profile (profilnam, kuerzel, he_nr, mu_nr, kp_key, isybau, m150, m145) VALUES (?,?, ?, ?, ?, ?, ?, ?)"

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

    def click_help(self) -> None:
        help_file = "https://qkan.eu/QKan_Formulare_Allgemein.html#neue-datenbank-erstellen"
        os.startfile(help_file)
