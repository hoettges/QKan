from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

logger = get_logger("QKan.he8._import")


class ImportTask:
    def __init__(self, db_qkan: DBConnection):
        # all parameters are passed via QKan.config
        self.db_qkan = db_qkan
        self.append = QKan.config.check_import.append
        self.update = QKan.config.check_import.update
        self.allrefs = QKan.config.check_import.allrefs
        self.fangradius = QKan.config.fangradius

        self.epsg = QKan.config.epsg

    def run(self) -> bool:

        self.db_qkan.loadmodule('he8porter')

        result = all(
            [
                self._reftables(),
                self._profile(),
                self._bodenklassen(),
                self._abflussparameter(),
                self._schaechte(),
                self._auslaesse(),
                self._speicher(),
                self._haltungen(),
                self._wehre(),
                self._pumpen(),
                self._drosseln(),
                self._schieber(),
                self._qregler(),
                self._hregler(),
                self._grundseitenauslaesse(),
                self._flaechen(),
                self._einleitdirekt(),
                self._aussengebiete(),
                self._einzugsgebiet(),
                self._tezg(),
            ]
        )

        return result

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für HE-Import füllen"""

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert
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

        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        if not self.db_qkan.sqlyml(
            'he8_insert_entwaesserungsarten',
            "he8_import Referenzliste entwaesserungsarten",
            daten,
            many=True
        ):
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

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        if not self.db_qkan.sqlyml(
            'he8_insert_haltungstypen',
            "he8_import Referenzliste haltungstypen",
            daten,
            many=True
        ):
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

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement

        if not self.db_qkan.sqlyml(
            'he8_insert_profile',
            "he8_import Referenzliste profile",
            daten,
            many=True
        ):
            return False

        daten = [
             ('Offline', 1),
             ('Online Schaltstufen', 2),
             ('Online Kennlinie', 3),
             ('Online Wasserstandsdifferenz', 4),
             ('Ideal', 5),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement

        if not self.db_qkan.sqlyml(
            'he8_insert_pumpentypen',
            "he8_import Referenzliste pumpentypen",
            daten,
            many=True
        ):
            return False

        # Referenztabelle Simulationsarten

        params = []
        data = [  # kurz    he    mu    kp  m150  m145   isy
            ('in Betrieb', 'B', 1, 1, 0, 'B', '1', '0', 'QKan-Standard'),
            ('außer Betrieb', 'AB', 4, None, 3, 'B', '1', '3', 'QKan-Standard'),
            ('geplant', 'P', 2, None, 1, 'P', None, '1', 'QKan-Standard'),
            ('stillgelegt', 'N', None, None, 4, 'N', None, '3', 'QKan-Standard'),
            ('verdämmert', 'V', 5, None, None, 'V', None, '4', 'QKan-Standard'),
            ('fiktiv', 'F', 3, None, 2, None, None, '2', 'QKan-Standard'),
            ('rückgebaut', 'P', None, None, 6, None, None, '6', 'QKan-Standard'),
        ]

        for bezeichnung, kuerzel, he_nr, mu_nr, kp_nr, m150, m145, isybau, kommentar in data:
            params.append(
                {
                    'bezeichnung': bezeichnung,
                    'kuerzel': kuerzel,
                    'he_nr': he_nr,
                    'mu_nr': mu_nr,
                    'kp_nr': kp_nr,
                    'isybau': isybau,
                    'm150': m150,
                    'm145': None,
                    'kommentar': 'QKan-Standard',
                }
            )

        if not self.db_qkan.sqlyml(
            'he8_insert_simulationsstatus',
            "Isybau Import Referenzliste Simulationsstatus",
            params,
            many=True
        ):
            return False

        self.db_qkan.commit()
        return True

    def _schaechte(self) -> bool:
        """Import der Schächte"""

        if QKan.config.check_import.schaechte:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_schaechte',
                    "he8_import Schächte",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _auslaesse(self) -> bool:
        """Import der Auslässe"""

        if QKan.config.check_import.auslaesse:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_auslaesse',
                    "he8_import Auslässe",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _speicher(self) -> bool:
        """Import der Speicher"""

        if QKan.config.check_import.speicher:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_speicher',
                    "he8_import Speicher",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _haltungen(self) -> bool:
        """Import der Haltungen"""

        # Haltungen
        if QKan.config.check_import.haltungen:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_haltungen',
                    "he8_import Haltungen",
                    parameters=params,
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _wehre(self) -> bool:
        """Import der Wehre"""

        if QKan.config.check_import.wehre:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_wehre',
                    "he8_import Wehre",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _pumpen(self) -> bool:
        """Import der Pumpen"""

        if QKan.config.check_import.pumpen:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_pumpen',
                    "he8_import Pumpen",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _drosseln(self) -> bool:
        """Import der Drosseln"""

        if QKan.config.check_import.drosseln:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_drosseln',
                    "he8_import Drosseln",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _schieber(self) -> bool:
        """Import der Schieber"""

        if QKan.config.check_import.schieber:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_schieber',
                    "he8_import Schieber",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _qregler(self) -> bool:
        """Import der Q-Regler"""

        if QKan.config.check_import.qregler:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_qregler',
                    "he8_import Q-Regler",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _hregler(self) -> bool:
        """Import der H-Regler"""

        if QKan.config.check_import.hregler:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_hregler',
                    "he8_import H-Regler",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _grundseitenauslaesse(self) -> bool:
        """Import der Grund- und Seitenauslässe"""

        if QKan.config.check_import.grundseitenauslaesse:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_gusauslaesse',
                    "he8_import Grund- und Seitenauslässe",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _flaechen(self) -> bool:
        """Import der Flächen"""

        if QKan.config.check_import.flaechen:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_flaechen',
                    "he8_import Flaechen",
                    params
                ):
                    return False

                self.db_qkan.commit()

                params = {'epsg': self.epsg, 'fangradius': self.fangradius}
                if not self.db_qkan.sqlyml(
                    'he8_insert_linkfl',
                    "he8_import linkfl",
                    params
                ):
                    return False

                self.db_qkan.commit()

        return True

    def _abflussparameter(self) -> bool:
        """Import der Abflussbeiwerte

        Wahlweise (allrefs) werden nur die in QKan fehlenden Abflussbeiwerte, die in der
        HE-Datenbank in Flächen verwendet werden, importiert"""

        if QKan.config.check_import.abflussparameter:
            if self.append:
                if self.allrefs:
                    # Auch nicht referenzierte Datensätze importieren
                    if not self.db_qkan.sqlyml(
                        'he8_insert_abflussparameter_all',
                        "he8_import Abflussparameter"):
                        return False
                else:
                    if not self.db_qkan.sqlyml(
                        'he8_insert_abflussparameter_filtered',
                        "he8_import Abflussparameter"):
                        return False
                    self.db_qkan.commit()
        return True

    def _bodenklassen(self) -> bool:
        """Import der Bodenklassen

        Wahlweise (allrefs) werden nur die in QKan fehlenden Bodenklassen, die in der
        HE-Datenbank in Abflussparametern verwendet werden, importiert"""

        if QKan.config.check_import.bodenklassen:

            # Auch nicht referenzierte Datensätze importieren
            if self.allrefs:
                filter = ""
            else:
                filter = """
"""

            if self.append:
                if self.allrefs:
                    if not self.db_qkan.sqlyml(
                        'he8_insert_bodenklasse_all',
                        "he8_import Bodenklassen"):
                        return False
                else:
                    if not self.db_qkan.sqlyml(
                            'he8_insert_bodenklasse_filtered',
                            "he8_import Bodenklassen"):
                        return False
                self.db_qkan.commit()
        return True

    def _profile(self) -> bool:
        """Import der Rohrprofile

        Wahlweise (allrefs) werden nur die in QKan fehlenden Rorhprifle, die in der
        HE-Datenbank in Abflussparametern verwendet werden, importiert"""

        if QKan.config.check_import.rohrprofile:
            if self.append:
                if self.allrefs:
                    # Auch nicht referenzierte Datensätze importieren
                    if not self.db_qkan.sqlyml(
                        'he8_insert_profiles_all',
                        "he8_import Sonderprofile"):
                        return False
                else:
                    if not self.db_qkan.sqlyml(
                            'he8_insert_profiles_filtered',
                            "he8_import Sonderprofile"):
                        return False
                self.db_qkan.commit()

    def _aussengebiete(self) -> bool:
        """Import der Aussengebiete"""

        if QKan.config.check_import.aussengebiete:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_aussengebiete',
                    "he8_import Außengebiete",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _einleitdirekt(self) -> bool:
        """Import der Direkteinleiter"""

        if QKan.config.check_import.einleitdirekt:
            if self.append:
                params = {'epsg': self.epsg}
                if not self.db_qkan.sqlyml(
                    'he8_insert_direkteinleiter',
                    "he8_import Direkteinleiter",
                    params
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _einzugsgebiet(self) -> bool:
        """Import der Einzugsgebiete"""

        if QKan.config.check_import.einzugsgebiete:
            if self.append:
                if not self.db_qkan.sqlyml(
                    'he8_insert_einzugsgebiete',
                    "he8_import Einzugsgebiete"
                ):
                    return False
                self.db_qkan.commit()
        return True

    def _tezg(self) -> bool:
        """Import der Haltungsflaechen (tezg)

        Diese sind in HYSTEM-EXTRAN zusätzlich markiert als
         - Einzugsfläche
         - Haltungsfläche
         - TWEinzugsfläche

        Dieses Attribut wird nicht in QKan übernommen. Allerdings kann
        der Flächentyp selektiert werden.
        """

        if (
            QKan.config.check_import.tezg_ef
            or QKan.config.check_import.tezg_hf
        ):

            if self.append:
                params = {'epsg': self.epsg,
                          'choice_ef': QKan.config.check_import.tezg_ef,
                          'choice_hf': QKan.config.check_import.tezg_hf
                          }
                if not self.db_qkan.sqlyml(
                    'he8_insert_haltungsflaechen_einzel',
                    "he8_import Haltungsflächen",
                    params
                ):
                    return False
        elif QKan.config.check_import.tezg_tf:
            if self.append:
                params = {'epsg': self.epsg,
                          'choice_tf': QKan.config.check_import.tezg_tf
                          }
                if not self.db_qkan.sqlyml(
                    'he8_insert_haltungsflaechen_teilfl',
                    "he8_import Haltungsflächen",
                    params
                ):
                    return False
        self.db_qkan.commit()
        return True
