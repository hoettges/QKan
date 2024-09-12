import sys, os
import xml.etree.ElementTree as ElementTree
from typing import Dict, Iterator, Tuple, Union

from lxml import etree

from qkan import QKan
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.utils import get_logger

logger = get_logger("QKan.xml.import")


# region objects
class Schacht(ClassObject):
    schnam: str = ""
    xsch: float = 0.0
    ysch: float = 0.0
    sohlhoehe: float = 0.0
    deckelhoehe: float = 0.0
    durchm: float = 0.0
    druckdicht: int = 0
    baujahr: int = 0
    entwart: str = ""
    strasse: str = ""
    knotentyp: str = ""
    schachttyp: str = ""
    material: str = ""
    simstatus: str = ""
    kommentar: str = ""

class Schacht_untersucht(ClassObject):
    schnam: str = ""
    durchm: float = 0.0
    sohlhoehe: float = 0.0
    druckdicht: int = 0
    entwart: str = ""
    strasse: str = ""
    knotentyp: str = ""
    simstatus: str = ""
    kommentar: str = ""
    baujahr: int = 0
    untersuchtag: str = ""
    untersucher: str = ""
    wetter: str = ""
    bewertungsart: str = ""
    bewertungstag: str = ""
    datenart: str = ""
    max_ZD: int = 63
    max_ZB: int = 63
    max_ZS: int = 63
    xsch: float = 0.0
    ysch: float = 0.0


class Untersuchdat_schacht(ClassObject):
    untersuchsch: str = ""
    id: int = 0
    bandnr: int = 0
    videozaehler: int = 0
    timecode: str = ""
    kuerzel: str = ""
    charakt1: str = ""
    charakt2: str = ""
    quantnr1: float = 0.0
    quantnr2: float = 0.0
    streckenschaden: str = ""
    streckenschaden_lfdnr: int = 0
    bereich: str = ""
    pos_von: int = 0
    pos_bis: int = 0
    vertikale_lage: float = 0.0
    inspektionslaenge: float = 0.0
    foto_dateiname: str = ""
    ordner: str = ""
    film_dateiname: str = ""
    ordner_video: str = ""
    ZD: int = 63
    ZB: int = 63
    ZS: int = 63


class Haltung(ClassObject):
    haltnam: str
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    sohleoben: float = 0.0
    sohleunten: float = 0.0
    deckeloben: float = 0.0
    deckelunten: float = 0.0
    baujahr: int = 0
    profilnam: str = ""
    entwart: str = ""
    material: str = ""
    strasse: str = ""
    ks: float = 1.5
    simstatus: str = ""
    kommentar: str = ""
    aussendurchmesser: float = 0.0
    profilauskleidung: str = ""
    innenmaterial: str = ""
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0


class Haltung_untersucht(ClassObject):
    haltnam: str
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    baujahr: int = 0
    kommentar: str = ""
    untersuchtag: str = ""
    untersucher: str = ""
    wetter: str = ""
    strasse: str = ""
    bewertungsart: str = ""
    bewertungstag: str = ""
    datenart: str = ""
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0
    max_ZD: int = 63
    max_ZB: int = 63
    max_ZS: int = 63


class Untersuchdat_haltung(ClassObject):
    untersuchhal: str = ""
    untersuchrichtung: str = ""
    schoben: str = ""
    schunten: str = ""
    id: int = 0
    inspektionslaenge: float = 0.0
    videozaehler: int = 0
    station: float = 0.0
    timecode: str = ""
    kuerzel: str = ""
    charakt1: str = ""
    charakt2: str = ""
    quantnr1: float = 0.0
    quantnr2: float = 0.0
    streckenschaden: str = ""
    streckenschaden_lfdnr: int = 0
    pos_von: int = 0
    pos_bis: int = 0
    foto_dateiname: str = ""
    film_dateiname: str = ""
    bandnr: int = 0
    ordner_bild: str = ""
    ordner_video: str = ""
    ZD: int = 63
    ZB: int = 63
    ZS: int = 63
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0

class Anschlussleitung(ClassObject):
    leitnam: str = ""
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    sohleoben: float = 0.0
    sohleunten: float = 0.0
    deckeloben: float = 0.0
    deckelunten: float = 0.0
    profilnam: str = ""
    entwart: str = ""
    material: str = ""
    baujahr: int = 0
    ks: float = 1.5
    simstatus: str = ""
    kommentar: str = ""
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0

class Anschlussleitung_untersucht(ClassObject):
    haltnam: str
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    baujahr: int = 0
    kommentar: str = ""
    untersuchtag: str = ""
    untersucher: str = ""
    wetter: str = ""
    strasse: str = ""
    bewertungsart: str = ""
    bewertungstag: str = ""
    datenart: str = ""
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0
    max_ZD: int = 63
    max_ZB: int = 63
    max_ZS: int = 63


class Untersuchdat_anschlussleitung(ClassObject):
    untersuchhal: str = ""
    untersuchrichtung: str = ""
    schoben: str = ""
    schunten: str = ""
    id: int = 0
    inspektionslaenge: float = 0.0
    videozaehler: int = 0
    station: float = 0.0
    timecode: int = 0
    kuerzel: str = ""
    charakt1: str = ""
    charakt2: str = ""
    quantnr1: float = 0.0
    quantnr2: float = 0.0
    streckenschaden: str = ""
    streckenschaden_lfdnr: int = 0
    pos_von: int = 0
    pos_bis: int = 0
    foto_dateiname: str = ""
    film_dateiname: str = ""
    bandnr: int = 0
    ordner_bild: str = ""
    ordner_video: str = ""
    ZD: int = 63
    ZB: int = 63
    ZS: int = 63
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0


class Wehr(ClassObject):
    wnam: str
    schoben: str
    schunten: str
    wehrtyp: str
    sohle: float = 0.0
    schwellenhoehe: float
    kammerhoehe: float
    laenge: float
    uebeiwert: float
    simstatus: str = ""
    kommentar: str = ""
    xsch: float = 0.0
    ysch: float = 0.0


class Pumpe(ClassObject):
    pnam: str
    schoben: str = ""  # //HydraulikObjekt/Pumpe/SchachtZulauf
    schunten: str = ""  # //HydraulikObjekt/Pumpe/SchachtAblauf
    pumpentyp: int = 0  # //HydraulikObjekt/Pumpe/PumpenTyp
    volanf: float = 0.0  # //HydraulikObjekt/Pumpe/Anfangsvolumen
    volges: float = 0.0  # //HydraulikObjekt/Pumpe/Gesamtvolumen
    sohle: float = 0.0  # //HydraulikObjekt/Pumpe/Sohlhoehe
    steuersch: str = ""  # //HydraulikObjekt/Pumpe/Steuerschacht
    einschalthoehe: float = 0.0  # Nicht in ISYBAU gefunden, TODO: XSD prüfen
    ausschalthoehe: float = 0.0  # Nicht in ISYBAU gefunden, TODO: XSD prüfen
    simstatus: str = ""
    kommentar: str = ""
    xsch: float = 0.0
    ysch: float = 0.0


# endregion


def _get_float(value: Union[str, float], default: float = 0.0) -> float:
    if isinstance(value, float):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return float(value)
        except ValueError:
            return default

    return default


def _get_int(value: Union[str, int], default: int = 0) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return int(value)
        except ValueError:
            print("isyporter._import.py._get_int: %s" % sys.exc_info()[1])

    return default


# noinspection SqlNoDataSourceInspection, SqlResolve
class ImportTask:
    def __init__(self, db_qkan: DBConnection, xml_file: str, data_choice: str, ordner_bild: str, ordner_video: str):
        self.db_qkan = db_qkan
        self.ordner_bild = ordner_bild
        self.ordner_video = ordner_video


        self.data_coice = data_choice
        if data_choice == "ISYBAU Daten":
            self.datenart = "ISYBAU"
        if data_choice == "DWA M-150 Daten":
            self.datenart = "DWA"

        # nr (str) => description
        self.mapper_entwart: Dict[str, str] = {}
        self.mapper_material: Dict[str, str] = {}
        #self.mapper_pump: Dict[str, str] = {}
        self.mapper_profile: Dict[str, str] = {}
        #self.mapper_outlet: Dict[str, str] = {}
        self.mapper_simstatus: Dict[str, str] = {}
        # self.mapper_untersuchrichtung: Dict[str, str] = {}        # direkt umgesetzt
        self.mapper_wetter: Dict[str, str] = {}
        #self.mapper_bewertungsart: Dict[str, str] = {}
        #self.mapper_druckdicht: Dict[str, str] = {}


        # Load XML
        self.xml = ElementTree.ElementTree()
        self.xml.parse(xml_file)

        # Get Namespace
        tree = etree.parse(xml_file)
        x = tree.xpath('namespace-uri(.)')
        self.NS = {"d": x}

    def _consume_smp_block(self,
            _block: ElementTree.Element,
    ) -> Tuple[str, int, float, float, float]:
        name = _block.findtext("d:Objektbezeichnung", None, self.NS)
        schacht_typ = 0

        for _schacht in _block.findall("d:Knoten", self.NS):
            schacht_typ = _get_int(_schacht.findtext("d:KnotenTyp", -1, self.NS))


        smp = _block.find(
            "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='SMP']",
            self.NS,
        )

        if not smp:
            #fehlermeldung(
            #    "Fehler beim XML-Import: Schächte",
            #    f'Keine Geometrie "SMP" für Schacht {name}',
            #)
            xsch = _get_float(_block.findtext("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt/d:Rechtswert", 0.0, self.NS))
            ysch = _get_float(_block.findtext("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt/d:Hochwert", 0.0, self.NS))
            sohlhoehe = _get_float(_block.findtext("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt/d:Punkthoehe", 0.0, self.NS))
            #xsch, ysch, sohlhoehe = (0.0,) * 3
        else:
            xsch = _get_float(smp.findtext("d:Rechtswert", 0.0, self.NS))
            ysch = _get_float(smp.findtext("d:Hochwert", 0.0, self.NS))
            sohlhoehe = _get_float(smp.findtext("d:Punkthoehe", 0.0, self.NS))
        return name, schacht_typ, xsch, ysch, sohlhoehe

    def run(self) -> bool:
        self._reftables()
        self._init_mappers()
        if getattr(QKan.config.xml, "import_stamm", True):
            self._schaechte()
            self._auslaesse()
            self._speicher()
            self._haltungen()
            self._haltunggeom()
            self._wehre()
            self._pumpen()
        if getattr(QKan.config.xml, "import_haus", True):
            self._anschlussleitungen()
            self._anschlussleitunggeom()
        if getattr(QKan.config.xml, "import_zustand", True):
            self._schaechte_untersucht()
            self._untersuchdat_schaechte()
            self._haltungen_untersucht()
            self._untersuchdat_haltung()

        return True

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für ISYBAU-Import füllen"""

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

        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau, transport, druckdicht)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "Isybau Referenzliste entwaesserungsarten", daten, many=True):
            return False


        #Referenztabelle Profile
        params = []

        data = [
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

        for profilnam, kuerzel, he_nr, mu_nr, kp_key, isybau, m150, m145 in data:
            params.append(
                {
                    'profilnam': profilnam,
                    'kuerzel': kuerzel,
                    'he_nr': he_nr,
                    'mu_nr': mu_nr,
                    'kp_key': kp_key,
                    'isybau': isybau,
                    'm150': m150,
                    'm145': None,
                    'kommentar': 'QKan-Standard',
                }
            )

        sql = """INSERT INTO profile (profilnam, kuerzel, he_nr, mu_nr, kp_key, isybau, m150, m145, kommentar)
                                SELECT
                                    :profilnam, :kuerzel, :he_nr, :mu_nr, :kp_key, 
                                    :isybau, :m150, :m145, :kommentar
                                WHERE :profilnam NOT IN (SELECT profilnam FROM profile)"""
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste profile", params, many=True):
            return False

        # Referenztabelle Simulationsarten

        params = []
        data = [  # kurz    he    mu    kp  m150  m145   isy
            ('in Betrieb', 'B', 1, 1, 0, 'B', '1', '0', 'QKan-Standard'),
            ('außer Betrieb', 'AB', 4, None, 3, 'B', '1', '20', 'QKan-Standard'),
            ('geplant', 'P', 2, None, 1, 'P', None, '10', 'QKan-Standard'),
            ('stillgelegt', 'N', None, None, 4, 'N', None, '21', 'QKan-Standard'),
            ('verdämmert', 'V', 5, None, None, 'V', None, None, 'QKan-Standard'),
            ('fiktiv', 'F', 3, None, 2, None, None, '99', 'QKan-Standard'),
            ('rückgebaut', 'P', None, None, 6, None, None, '22', 'QKan-Standard'),
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

        sql = """INSERT INTO simulationsstatus (bezeichnung, kuerzel, he_nr, mu_nr, kp_nr, isybau, m150, m145, kommentar)
                                SELECT
                                    :bezeichnung, :kuerzel, :he_nr, :mu_nr, :kp_nr, 
                                    :isybau, :m150, :m145, :kommentar
                                WHERE :bezeichnung NOT IN (SELECT bezeichnung FROM simulationsstatus)"""
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste Simulationsstatus", params, many=True):
            return False

        # Referenztabelle Material

        params = []
        data = [  # kurz    m150  m145   isy
            ('Asbestzement', 'AZ', 'AZ', '7', 'AZ', None),
            ('Beton', 'B', 'B', '2', 'B', None),
            ('Bitumen', 'BIT', 'BIT', None, None, None),
            ('Betonsegmente', 'BS', 'BS', None, 'BS', None),
            ('Betonsegmente kunststoffmodifiziert', 'BSK', 'BSK', None, None, None),
            ('Bitumen', 'BT', 'BT', None, None, None),
            ('Edelstahl', 'CN', 'CN', '22', None, None),
            ('Nichtidentifiziertes Metall (z. B. Eisen und Stahl)', 'EIS', 'EIS', None, 'EIS', None),
            ('Epoxydharz', 'EPX', 'EPX', None, None, None),
            ('Epoxydharz mit Synthesefaser', 'EPSF', 'EPSF', None, None, None),
            ('Faserzement', 'FZ', 'FZ', '6', 'FZ', None),
            ('Glasfaserverstärkter Kunststoff', 'GFK', 'GFK', '51', 'GFK', None),
            ('Grauguß', 'GG', 'GG', '4', 'GG', None),
            ('Duktiles Gußeisen', 'GGG', 'GGG', '5', 'GGG', None),
            ('Nichtidentifizierter Kunststoff', 'KST', 'KST', '50', 'KST', None),
            ('Mauerwerk', 'MA', 'MA', '3', 'MA', None),
            ('Ortbeton', 'OB', 'OB', None, 'OB', None),
            ('Polymerbeton', 'PC', 'PC', None, 'PC', None),
            ('Polymermodifizierter Zementbeton', 'PCC', 'PCC', None, 'PCC', None),
            ('Polyethylen', 'PE', 'PE', '52', 'PE', None),
            ('Polyesterharz', 'PH', 'PH', None, 'PH', None),
            ('Polyesterharzbeton', 'PHB', 'PHB', None, 'PHB', None),
            ('Polypropylen', 'PP', 'PP', '54', 'PP', None),
            ('Polyurethanharz', 'PUR', 'PUR', None, None, None),
            ('Polyvinylchlorid modifiziert', 'PVCM', 'PVCM', None, None, None),
            ('Polyvinylchlorid hart', 'PVCU', 'PVCU', None, 'PVCU', None),
            ('Stahlfaserbeton', 'SFB', 'SFB', None, 'SFB', None),
            ('Spannbeton', 'SPB', 'SPB', '12', 'SPB', None),
            ('Stahlbeton', 'SB', 'SB', '13', 'SB', None),
            ('Stahl', 'ST', 'ST', '21', 'ST', None),
            ('Steinzeug', 'STZ', 'STZ', '1', 'STZ', None),
            ('Spritzbeton', 'SZB', 'SZB', '14', 'SZB', None),
            ('Spritzbeton kunststoffmodifiziert', 'SZBK', 'SZBK', None, None, None),
            ('Teerfaser', 'TF', 'TF', None, None, None),
            ('Ungesättigtes Polyesterharz mit Glasfaser', 'UPGF', 'UPGF', None, None, None),
            ('Ungesättigtes Polyesterharz mit Synthesefaser', 'UPSF', 'UPSF', None, None, None),
            ('Vinylesterharz mit Synthesefaser', 'VEGF', 'VEGF', None, None, None),
            ('Vinylesterharz mit Glasfaser', 'VESF', 'VESF', None, None, None),
            ('Verbundrohr Beton-/StahlbetonKun', 'VBK', 'VBK', None, None, None),
            ('Verbundrohr Beton-/Stahlbeton Steinzeug', 'VBS', 'VBS', None, None, None),
            ('Nichtidentifizierter Werkstoff', 'W', 'W', None, None, None),
            ('Wickelrohr (PEHD)', 'WPE', 'WPE', None, None, None),
            ('Wickelrohr (PVCU)', 'WPVC', 'WPVC', None, None, None),
            ('Zementmörtel', 'ZM', 'ZM', None, None, None),
            ('Ziegelwerk', 'ZG', 'ZG', None, 'ZG', None),
        ]

        for bezeichnung, kuerzel, m150, m145, isybau, kommentar in data:
            params.append(
                {
                    'bezeichnung': bezeichnung,
                    'kuerzel': kuerzel,
                    'isybau': isybau,
                    'm150': m150,
                    'm145': None,
                    'kommentar': 'QKan-Standard',
                }
            )

        sql = """INSERT INTO material (bezeichnung, kuerzel, isybau, m150, m145, kommentar)
                                SELECT
                                    :bezeichnung, :kuerzel, 
                                    :isybau, :m150, :m145, :kommentar
                                WHERE :bezeichnung NOT IN (SELECT bezeichnung FROM material)"""
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste Material", params, many=True):
            return False

        # Referenztabelle Wetter

        params = []
        data = [  # bezeichnung  m150  m145   isy
            ('keine Angabe', None, None, None),
            ('kein Niederschlag', None, None, 1),
            ('Regen', None, None, 2),
            ('Schnee- oder Eisschmelzwasser', None, None, 3),
            ]

        for bezeichnung, m150, m145, isybau in data:
            params.append(
                {
                    'bezeichnung': bezeichnung,
                    'isybau': isybau,
                    'm150': m150,
                    'm145': m145,
                }
            )

        sql = """INSERT INTO wetter (bezeichnung, isybau, m150, m145)
                                SELECT
                                    :bezeichnung, 
                                    :isybau, :m150, :m145
                                WHERE :bezeichnung NOT IN (SELECT bezeichnung FROM wetter)"""
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste Wetter", params, many=True):
            return False

    def _init_mappers(self) -> None:
        # Entwässerungsarten
        sql = "SELECT isybau, FIRST_VALUE(bezeichnung) OVER (PARTITION BY isybau ORDER BY pk) " \
              "FROM entwaesserungsarten WHERE isybau IS NOT NULL GROUP BY isybau"
        subject = "isybau Import entwaesserungsarten"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_entwart)

        # Profilarten
        sql = "SELECT isybau, FIRST_VALUE(profilnam) OVER (PARTITION BY isybau ORDER BY pk) " \
              "FROM profile WHERE isybau IS NOT NULL GROUP BY isybau"
        subject = "xml_import profile"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_profile)

        # sql = "SELECT he_nr, bezeichnung FROM pumpentypen"
        # subject = "xml_import pumpentypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_pump)

        sql = "SELECT isybau, FIRST_VALUE(bezeichnung) OVER (PARTITION BY isybau ORDER BY pk) " \
              "FROM material WHERE isybau IS NOT NULL GROUP BY isybau"
        subject = "xml_import material"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_material)

        # sql = "SELECT he_nr, bezeichnung FROM auslasstypen"
        # subject = "xml_import auslasstypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_outlet)

        sql = "SELECT isybau, FIRST_VALUE(bezeichnung) OVER (PARTITION BY isybau ORDER BY pk) " \
              "FROM simulationsstatus WHERE isybau IS NOT NULL GROUP BY isybau"
        subject = "xml_import simulationsstatus"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_simstatus)

        # sql = "SELECT kuerzel, bezeichnung FROM untersuchrichtung"
        # subject = "xml_import untersuchrichtung"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_untersuchrichtung)

        sql = "SELECT isybau, FIRST_VALUE(bezeichnung) OVER (PARTITION BY isybau ORDER BY pk) " \
              "FROM wetter WHERE isybau IS NOT NULL GROUP BY isybau"
        subject = "xml_import wetter"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_wetter)

        # sql = "SELECT kuerzel, bezeichnung FROM bewertungsart"
        # subject = "xml_import bewertungsart"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_bewertungsart)
        #
        # sql = "SELECT kuerzel, bezeichnung FROM druckdicht"
        # subject = "xml_import druckdicht"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_druckdicht)

    def _schaechte(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Schacht/../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='2']",
                self.NS,
            )

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name, schacht_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)
                schachttyp = 'Schacht'

                if schacht_typ == 1:
                    schachttyp = 'Anschlussschacht'

                knoten_typ = 'Normalschacht'
                baujahr = _get_int(block.findtext("d:Baujahr", None, self.NS))

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=_get_float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten"
                            "/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe",
                            None,
                            self.NS
                        )
                    ),
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    entwart=block.findtext("d:Entwaesserungsart", None, self.NS),
                    strasse=block.findtext("d:Lage/d:Strassenname", None, self.NS),
                    baujahr=baujahr,
                    knotentyp=knoten_typ,
                    schachttyp=schachttyp,
                    simstatus=_get_int(block.findtext("d:Status", None, self.NS)),
                    material=block.findtext("d:Knoten/d:Schacht/d:Aufbau/d:MaterialAufbau", None, self.NS),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                )

        def _iter2() -> Iterator[Schacht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Schacht/..",
                self.NS,
            )
            logger.debug(f"Anzahl Schaechte: {len(blocks)}")

            druckdicht = None
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)

                for _schacht in block.findall("d:Schacht", self.NS):
                    druckdicht = _get_int(_schacht.findtext("d:DruckdichterDeckel", None, self.NS))


                yield Schacht(
                    schnam=name,
                    druckdicht=druckdicht,
                )


        for schacht in _iter():

            # Entwässerungsarten
            entwart = self.db_qkan.get_from_mapper(
                schacht.entwart,
                self.mapper_entwart,
                'schaechte',
                'entwaesserungsarten',
                'bezeichnung',
                'isybau',
                'bemerkung',
                'kuerzel',
            )

            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                schacht.simstatus,
                self.mapper_simstatus,
                'schacht',
                'simulationsstatus',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            # Material
            material = self.db_qkan.get_from_mapper(
                schacht.material,
                self.mapper_material,
                'schacht',
                'material',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            params = {'schnam': schacht.schnam, 'xsch': schacht.xsch, 'ysch': schacht.ysch,
                      'sohlhoehe': schacht.sohlhoehe, 'deckelhoehe': schacht.deckelhoehe,
                      'durchm': schacht.durchm, 'baujahr': schacht.baujahr, 'entwart': entwart,
                      'strasse': schacht.strasse, 'knotentyp': schacht.knotentyp,'material': material,
                      'simstatus': simstatus, 'kommentar': schacht.kommentar, 'schachttyp': schacht.schachttyp, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        for schacht in _iter2():
            if not self.db_qkan.sql(
                "UPDATE schaechte SET druckdicht = ? WHERE schnam = ?",
                "xml_import Schacht [4b]",
                parameters=[schacht.druckdicht, schacht.schnam],
            ):
                return None

        self.db_qkan.commit()


    def _schaechte_untersucht(self) -> None:
        def _iter() -> Iterator[Schacht_untersucht]:
            # .//Schacht/../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='2']",
                self.NS,
            )


            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                yield Schacht_untersucht(
                    schnam=name,
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                    xsch=xsch,
                    ysch=ysch,
                )


        def _iter3() -> Iterator[Schacht_untersucht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Zustandsdatenkollektiv/d:InspizierteAbwassertechnischeAnlage/"
                "d:OptischeInspektion/d:Knoten/../..",
                self.NS,
            )
            logger.debug(f"Anzahl Schaechte: {len(blocks)}")

            untersuchtag = ""
            untersucher = ""
            wetter = None
            strasse = ""
            bewertungsart = 0
            bewertungstag = ""
            datenart = self.datenart

            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)
                baujahr = _get_int(block.findtext("d:Baujahr", 0, self.NS))
                strasse = block.findtext("d:Lage/d:Strassenname", None, self.NS)

                for _schacht in block.findall("d:OptischeInspektion", self.NS):

                    untersuchtag = _schacht.findtext("d:Inspektionsdatum", None, self.NS)

                    untersucher = _schacht.findtext("d:NameUntersucher", None, self.NS)

                    wetter = _get_int(_schacht.findtext("d:Wetter", "0", self.NS))

                    for _schachtz in _schacht.findall("d:Knoten/d:Bewertung", self.NS):

                        bewertungsart = _get_int(_schachtz.findtext("d:Bewertungsverfahren", "0", self.NS))

                        bewertungstag = _schachtz.findtext("d:Bewertungsdatum", None, self.NS)

                yield Schacht_untersucht(
                    schnam=name,
                    baujahr=baujahr,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    wetter=wetter,
                    strasse=strasse,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                )

        for schacht_untersucht in _iter():

            # Datensatz einfügen
            params = {'schnam': schacht_untersucht.schnam, 'xsch': schacht_untersucht.xsch,
                      'ysch': schacht_untersucht.ysch,
                      'durchm': schacht_untersucht.durchm, 'kommentar': schacht_untersucht.kommentar, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte_untersucht\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte_untersucht",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return


        self.db_qkan.commit()


        for schacht_untersucht in _iter3():
            # Wetter

            wetter = self.db_qkan.get_from_mapper(
                schacht_untersucht.wetter,
                self.mapper_wetter,
                'schaechte_untersucht',
                'wetter',
                'bezeichnung',
                'isybau',
                'bemerkung',
            )

            if not self.db_qkan.sql(
                "UPDATE schaechte_untersucht SET untersuchtag=?, untersucher=?, wetter=?, baujahr=?, strasse=?, bewertungsart=?," 
                "bewertungstag=?, datenart=? WHERE schnam = ?",
                "xml_import Schächte_untersucht [4]",
                parameters=[schacht_untersucht.untersuchtag, schacht_untersucht.untersucher, wetter,
                            schacht_untersucht.baujahr, schacht_untersucht.strasse, schacht_untersucht.bewertungsart, schacht_untersucht.bewertungstag,
                            schacht_untersucht.datenart, schacht_untersucht.schnam],
            ):
                return None

        self.db_qkan.commit()

    def _untersuchdat_schaechte(self) -> None:
        def _iter() -> Iterator[Untersuchdat_schacht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Zustandsdatenkollektiv/d:InspizierteAbwassertechnischeAnlage/d:OptischeInspektion/"
                "d:Knoten/d:Inspektionsdaten/d:KZustand/../../../..",
                self.NS,
            )

            ordner = self.ordner_bild

            logger.debug(f"Anzahl Untersuchungsdaten Schacht: {len(blocks)}")

            name = ""
            inspektionslaenge = 0.0
            id = 0
            bandnr = 0
            videozaehler = 0
            timecode = 0
            kuerzel = ""
            charakt1 = ""
            charakt2 = ""
            quantnr1 = 0.0
            quantnr2 = 0.0
            streckenschaden = ""
            streckenschaden_lfdnr = 0
            pos_von = 0
            pos_bis = 0
            bereich = ""
            foto_dateiname = ""
            xsch= 0.0
            ysch= 0.0

            for block in blocks:

                name = block.findtext("d:Objektbezeichnung", None, self.NS)
                inspektionslaenge = _get_float(block.findtext(
                    "d:OptischeInspektion/d:Knoten/d:Inspektionsdaten/d:KZustand[d:InspektionsKode='DDB'][d:Streckenschaden='B']/d:VertikaleLage",
                    "0.0", self.NS))

                for _untersuchdat_schacht in block.findall("d:OptischeInspektion/d:Knoten/d:Inspektionsdaten/d:KZustand", self.NS):

                    id = _get_int(_untersuchdat_schacht.findtext("d:Index", "0", self.NS))
                    videozaehler = _get_int(_untersuchdat_schacht.findtext("d:Videozaehler", "0", self.NS))
                    timecode = _get_int(_untersuchdat_schacht.findtext("d:Timecode", "0", self.NS))
                    kuerzel = _untersuchdat_schacht.findtext("d:InspektionsKode", None, self.NS)
                    charakt1 = _untersuchdat_schacht.findtext("d:Charakterisierung1", None, self.NS)
                    charakt2 = _untersuchdat_schacht.findtext("d:Charakterisierung2", None, self.NS)
                    quantnr1 = _get_float(_untersuchdat_schacht.findtext("d:Quantifizierung1Numerisch", "0.0", self.NS))
                    quantnr2 = _get_float(_untersuchdat_schacht.findtext("d:Quantifizierung2Numerisch", "0.0", self.NS))
                    streckenschaden = _untersuchdat_schacht.findtext("d:Streckenschaden", None, self.NS)
                    streckenschaden_lfdnr = _get_int(_untersuchdat_schacht.findtext("d:StreckenschadenLfdNr", "0", self.NS))
                    pos_von = _get_int(_untersuchdat_schacht.findtext("d:PositionVon", "0", self.NS))
                    pos_bis = _get_int(_untersuchdat_schacht.findtext("d:PositionBis", "0", self.NS))
                    vertikale_lage = _get_float(_untersuchdat_schacht.findtext("d:VertikaleLage", "0.0", self.NS))
                    bereich = _untersuchdat_schacht.findtext("d:Schachtbereich", None, self.NS)

                    _datei = _untersuchdat_schacht.findtext("d:Fotodatei", None, self.NS)
                    if _datei is not None and self.ordner_bild is not None:
                        foto_dateiname = os.path.join(self.ordner_bild, _datei)
                    else:
                        foto_dateiname = None

                    ZD = _get_int(_untersuchdat_schacht.findtext("d:Klassifizierung/d:Dichtheit/d:SKDvAuto", 63, self.NS))
                    ZS = _get_int(_untersuchdat_schacht.findtext("d:Klassifizierung/d:Standsicherheit/d:SKSvAuto", 63, self.NS))
                    ZB = _get_int(_untersuchdat_schacht.findtext("d:Klassifizierung/d:Standsicherheit/d:SKBvAuto", 63, self.NS))


                    yield Untersuchdat_schacht(
                    untersuchsch = name,
                    id = id,
                    videozaehler = videozaehler,
                    timecode = timecode,
                    kuerzel = kuerzel,
                    charakt1 = charakt1,
                    charakt2 = charakt2,
                    quantnr1 = quantnr1,
                    quantnr2 = quantnr2,
                    streckenschaden = streckenschaden,
                    streckenschaden_lfdnr = streckenschaden_lfdnr,
                    pos_von = pos_von,
                    pos_bis = pos_bis,
                    vertikale_lage = vertikale_lage,
                    inspektionslaenge = inspektionslaenge,
                    bereich = bereich,
                    foto_dateiname = foto_dateiname,
                    ordner = ordner,
                        ZD=ZD,
                        ZS=ZS,
                        ZB=ZB,
                    )

        def _iter2() -> Iterator[Untersuchdat_schacht]:
                blocks = self.xml.findall(
                    "d:Datenkollektive/d:Zustandsdatenkollektiv/d:Filme/d:Film/d:Filmname/../..",
                    self.NS,
                )
                logger.debug(f"Anzahl Untersuchdat_schacht: {len(blocks)}")

                film_dateiname = ""
                for block in blocks:
                    for _untersuchdat_schacht in block.findall("d:Film/d:FilmObjekte/..", self.NS):

                        name = _untersuchdat_schacht.findtext("d:FilmObjekte/d:FilmObjekt/d:Objektbezeichnung", None, self.NS)

                        film_dateiname = self.ordner_video+_untersuchdat_schacht.findtext("d:Filmname", None, self.NS)

                        bandnr = _get_int(_untersuchdat_schacht.findtext("d:Videoablagereferenz", 0, self.NS))

                        yield Untersuchdat_schacht(
                            untersuchsch=name,
                            film_dateiname=film_dateiname,
                            bandnr=bandnr
                        )

        for untersuchdat_schacht in _iter():

            params = {'untersuchsch': untersuchdat_schacht.untersuchsch, 'id': untersuchdat_schacht.id,
                      'videozaehler': untersuchdat_schacht.videozaehler, 'timecode': untersuchdat_schacht.timecode,
                      'kuerzel': untersuchdat_schacht.kuerzel, 'charakt1': untersuchdat_schacht.charakt1,
                      'charakt2': untersuchdat_schacht.charakt2, 'quantnr1': untersuchdat_schacht.quantnr1,
                      'quantnr2': untersuchdat_schacht.quantnr2,
                      'streckenschaden': untersuchdat_schacht.streckenschaden,
                      'streckenschaden_lfdnr': untersuchdat_schacht.streckenschaden_lfdnr,
                      'pos_von': untersuchdat_schacht.pos_von,
                      'pos_bis': untersuchdat_schacht.pos_bis, 'vertikale_lage': untersuchdat_schacht.vertikale_lage,
                      'inspektionslage': untersuchdat_schacht.inspektionslaenge,
                      'bereich': untersuchdat_schacht.bereich,
                      'foto_dateiname': untersuchdat_schacht.foto_dateiname, 'ordner': untersuchdat_schacht.ordner,
                      'ZD': untersuchdat_schacht.ZD, 'ZB': untersuchdat_schacht.ZB, 'ZS': untersuchdat_schacht.ZS, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: untersuchdat_schacht\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_schacht",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        for untersuchdat_schacht in _iter2():
            if not self.db_qkan.sql(
                "UPDATE untersuchdat_schacht SET film_dateiname=?, bandnr=?" 
                " WHERE  untersuchsch= ?",
                "xml_import untersuchsch [2a]",
                parameters=[untersuchdat_schacht.film_dateiname,untersuchdat_schacht.bandnr, untersuchdat_schacht.untersuchsch],
            ):
                return None

        self.db_qkan.commit()

    def _auslaesse(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/"
                "d:Knoten/d:Bauwerk/d:Auslaufbauwerk/../../..", self.NS,)

            logger.debug(f"Anzahl Ausläufe: {len(blocks)}")

            for block in blocks:
                name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                baujahr = _get_int(block.findtext("d:Baujahr", 0, self.NS))

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=_get_float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten"
                            "/d:Punkt[d:PunktattributAbwasser='GOK']/d:Punkthoehe",
                            0.0,
                            self.NS,
                        )
                    ),
                    baujahr=baujahr,
                    durchm=0.5,
                    entwart=block.findtext("d:Entwaesserungsart", None, self.NS),
                    strasse=block.findtext("d:Lage/d:Strassenname", None, self.NS),
                    knotentyp=knoten_typ,
                    material=block.findtext("d:Knoten/d:Bauwerk/d:Auslaufbauwerk/d:Material", None, self.NS),
                    simstatus=_get_int(block.findtext("d:Status", None, self.NS)),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                )

        for auslass in _iter():
            # Entwässerungsarten
            entwart = self.db_qkan.get_from_mapper(
                auslass.entwart,
                self.mapper_entwart,
                'Auslässe',
                'entwaesserungsarten',
                'bezeichnung',
                'isybau',
                'bemerkung',
                'kuerzel',
            )

            # Simstatus
            simstatus = self.db_qkan.get_from_mapper(
                auslass.simstatus,
                self.mapper_simstatus,
                'Auslässe',
                'simulationsstatus',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )


            # Geo-Objekte

            # geop = f"MakePoint({auslass.xsch}, {auslass.ysch}, {QKan.config.epsg})"
            # geom = (
            #     "CastToMultiPolygon(MakePolygon("
            #     f"MakeCircle({auslass.xsch}, {auslass.ysch}, {auslass.durchm / 1000}, {QKan.config.epsg})"
            #     "))"
            # )
            #
            # sql = f"""
            # INSERT INTO schaechte (
            #     schnam, xsch, ysch,
            #     sohlhoehe, deckelhoehe, durchm, entwart,
            #     schachttyp, simstatus, kommentar, geop, geom)
            # VALUES (?, ?, ?, ?, ?, ?, ?, 'Auslass', ?, ?, MakePoint(?, ?, ?), CastToMultiPolygon(MakePolygon(
            # MakeCircle(?, ?, ?, ?))))
            # """
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import Auslässe [2]",
            #     parameters=(
            #         auslass.schnam,
            #         auslass.xsch,
            #         auslass.ysch,
            #         auslass.sohlhoehe,
            #         auslass.deckelhoehe,
            #         auslass.durchm,
            #         auslass.entwart,
            #         simstatus,
            #         auslass.kommentar,
            #         auslass.xsch, auslass.ysch, QKan.config.epsg,
            #         auslass.xsch, auslass.ysch, auslass.durchm, QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'schnam': auslass.schnam, 'xsch': auslass.xsch, 'ysch': auslass.ysch,
                      'sohlhoehe': auslass.sohlhoehe, 'deckelhoehe': auslass.deckelhoehe, 'baujahr': auslass.baujahr,
                      'durchm': auslass.durchm, 'entwart': entwart, 'strasse': auslass.strasse, 'simstatus': simstatus,
                      'kommentar': auslass.kommentar, 'material': auslass.material, 'schachttyp': 'Auslass', 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _speicher(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Becken/../../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage"
                "/d:Knoten/d:Bauwerk/d:Becken/../../..",
                self.NS,
            )

            logger.debug(f"Anzahl Becken: {len(blocks)}")

            knoten_typ = 'Schacht'
            knoten = 0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)
                baujahr = _get_int(block.findtext("d:Baujahr", 0, self.NS))

                for _schacht in block.findall("d:Knoten", self.NS):
                    knoten = _get_int(_schacht.findtext("d:Bauwerkstyp", None, self.NS))
                    if knoten == 1:
                        knoten_typ = 'Regenrückhaltebecken(RRB)'
                    if knoten == 2:
                        knoten_typ = 'Regenüberlaufbecken(RÜB)'
                    if knoten == 3:
                        knoten_typ = 'Regenklärbecken(RKB)'
                    if knoten == 4:
                        knoten_typ = 'Versickerungsanlage'
                    if knoten == 5:
                        knoten_typ = 'Bodenfilter'

                smp = block.find(
                    "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='KOP']",
                    self.NS,
                )

                if not smp:
                    fehlermeldung(
                        "Fehler beim XML-Import: Speicher",
                        f'Keine Geometrie "KOP" für Becken {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _get_float(smp.findtext("d:Rechtswert", 0.0, self.NS))
                    ysch = _get_float(
                        smp.findtext("d:Hochwert", 0.0, self.NS),
                    )
                    sohlhoehe = _get_float(smp.findtext("d:Punkthoehe", 0.0, self.NS))

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten"
                            "/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe",
                            0.0,
                            self.NS,
                        )
                    ),
                    baujahr=baujahr,
                    durchm=0.5,
                    entwart=block.findtext("d:Entwaesserungsart", None, self.NS),
                    strasse=block.findtext("d:Lage/d:Strassenname", None, self.NS),
                    knotentyp=knoten_typ,
                    simstatus=_get_int(block.findtext("d:Status", None, self.NS)),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                )

        for speicher in _iter():
            # Simstatus
            simstatus = self.db_qkan.get_from_mapper(
                speicher.simstatus,
                self.mapper_simstatus,
                'Auslässe',
                'simulationsstatus',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            params = {'schnam': speicher.schnam, 'xsch': speicher.xsch, 'ysch': speicher.ysch,
                      'sohlhoehe': speicher.sohlhoehe, 'deckelhoehe': speicher.deckelhoehe, 'baujahr': speicher.baujahr,
                      'durchm': speicher.durchm, 'strasse': speicher.strasse,  'entwart': speicher.entwart, 'simstatus': simstatus,
                      'kommentar': speicher.kommentar, 'schachttyp': 'Speicher', 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _haltungen(self) -> None:
        def _iter() -> Iterator[Haltung]:

            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']/d:Kante/d:Haltung/../..",
                self.NS,
            )
            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            schoben, schunten, profilnam = ("",) * 3
            (
                sohleoben,
                sohleunten,
                laenge,
                hoehe,
                breite,
                deckeloben,
                deckelunten,
                xschob,
                yschob,
                xschun,
                yschun
            ) = (0.0,) * 11


            for block in blocks:
                #found_leitung = block.findtext("d:Kante/d:Haltung", "", self.NS)
                name = block.findtext("d:Objektbezeichnung", None, self.NS)
                baujahr = _get_int(block.findtext("d:Baujahr", 0, self.NS))
                schoben = block.findtext("d:Kante/d:KnotenZulauf", None, self.NS)
                schunten = block.findtext("d:Kante/d:KnotenAblauf", None, self.NS)
                sohleoben = _get_float(block.findtext("d:Kante/d:SohlhoeheZulauf", 0.0, self.NS))
                sohleunten = _get_float(block.findtext("d:Kante/d:SohlhoeheAblauf", 0.0, self.NS))
                laenge = _get_float(block.findtext("d:Kante/d:Laenge", 0.0, self.NS))
                material = block.findtext("d:Kante/d:Material", None, self.NS)
                aussendurchmesser = _get_float(block.findtext("d:Kante/d:Profil/d:Aussendurchmesser", None, self.NS))
                profilauskleidung = block.findtext("d:Kante/d:Haltung/d:Auskleidung", None, self.NS)
                innenmaterial = block.findtext("d:Kante/d:Haltung/d:MaterialAuskleidung", None, self.NS)
                profilnam = block.findtext("d:Kante/d:Profil/d:Profilart", None, self.NS)
                hoehe = _get_float(block.findtext("d:Kante/d:Profil/d:Profilhoehe", 0.0, self.NS))
                breite = _get_float(block.findtext("d:Kante/d:Profil/d:Profilbreite", 0.0, self.NS))


                found_kanten = block.findtext("d:Geometrie/d:Geometriedaten/d:Kanten", None, self.NS)
                if found_kanten:
                    xschob = _get_float(block.findtext(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start/d:Rechtswert",
                        0.0, self.NS)
                    )
                    yschob = _get_float(block.findtext(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start/d:Hochwert",
                        0.0, self.NS)
                    )
                    xschun = _get_float(block.findtext(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende/d:Rechtswert",
                        0.0, self.NS)
                    )
                    yschun = _get_float(block.findtext(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende/d:Hochwert",
                        0.0, self.NS)
                    )
                else:
                    for kante in block.findall(
                            "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante",
                            self.NS
                    ):
                        if kante is not None:
                            # Für mehr als 1 Kante: Start der 1. Kante (siehe break)
                            for _start in block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Start[1]", self.NS
                            ):
                                xschob = _get_float(_start.findtext("d:Rechtswert", 0.0, self.NS))
                                yschob = _get_float(_start.findtext("d:Hochwert", 0.0, self.NS))
                                deckeloben = _get_float(
                                    _start.findtext("d:Punkthoehe", 0.0, self.NS)
                                )
                                break
                            # Für mehr als 1 Kante: Ende der letzten Kante
                            for _ende in block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Ende[last()]", self.NS
                            ):
                                xschob = _get_float(_ende.findtext("d:Rechtswert", 0.0, self.NS))
                                yschob = _get_float(_ende.findtext("d:Hochwert", 0.0, self.NS))
                                deckeloben = _get_float(
                                    _ende.findtext("d:Punkthoehe", 0.0, self.NS)
                                )

                yield Haltung(
                    haltnam=name,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    material=material,
                    sohleoben=sohleoben,
                    sohleunten=sohleunten,
                    deckeloben=deckeloben,
                    deckelunten=deckelunten,
                    profilnam=profilnam,
                    baujahr=baujahr,
                    entwart=block.findtext("d:Entwaesserungsart", None, self.NS),
                    strasse=block.findtext("d:Lage/d:Strassenname", None, self.NS),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=_get_int(block.findtext("d:Status", None, self.NS)),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                    aussendurchmesser=aussendurchmesser,
                    profilauskleidung=profilauskleidung,
                    innenmaterial=innenmaterial,
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
                )
            else:
                pass

        def _iter2() -> Iterator[Haltung]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Haltung/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Haltungen: {len(blocks)}")

            ks = 1.5
            laenge = 0.0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Haltung", self.NS):
                    cs1 = _haltung.findtext("d:Rauigkeitsansatz", "0", self.NS)
                    if cs1 == "1":
                        ks = _get_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKb", 0.0, self.NS)
                        )
                    elif cs1 == "2":
                        ks = _get_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKst", 0.0, self.NS)
                        )
                    else:
                        ks = 0.0
                        fehlermeldung(
                            "Fehler im XML-Import von HydraulikObjekte_Haltungen",
                            f"Ungültiger Wert für Rauigkeitsansatz {cs1} in Haltung {name}",
                        )

                    laenge = _get_float(
                        _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
                    )

                yield Haltung(
                    haltnam=name,
                    laenge=laenge,
                    ks=ks,
                )



        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung in _iter():
            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                haltung.simstatus,
                self.mapper_simstatus,
                'Haltungen',
                'simulationsstatus',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            # Entwässerungsarten
            entwart = self.db_qkan.get_from_mapper(
                haltung.entwart,
                self.mapper_entwart,
                'Haltungen',
                'entwaesserungsarten',
                'bezeichnung',
                'isybau',
                'bemerkung',
                'kuerzel',
            )

            # Profile
            profilnam = self.db_qkan.get_from_mapper(
                haltung.profilnam,
                self.mapper_profile,
                'Haltungen',
                'profile',
                'profilnam',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            # Material
            material = self.db_qkan.get_from_mapper(
                haltung.material,
                self.mapper_material,
                'Haltungen',
                'material',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )


            params = {'haltnam': haltung.haltnam, 'schoben': haltung.schoben, 'schunten': haltung.schunten,
                      'hoehe': haltung.hoehe,
                      'breite': haltung.breite, 'laenge': haltung.laenge,
                      'sohleoben': haltung.sohleoben, 'sohleunten': haltung.sohleunten, 'baujahr': haltung.baujahr,
                      'material': material, 'aussendurchmesser': haltung.aussendurchmesser, 'profilauskleidung': haltung.profilauskleidung,
                      'innenmaterial': haltung.innenmaterial, 'profilnam': profilnam, 'entwart': entwart,
                      'strasse': haltung.strasse,
                      'ks': haltung.ks, 'simstatus': simstatus, 'kommentar': haltung.kommentar, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()


        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        for haltung in _iter2():
            if not self.db_qkan.sql(
                "UPDATE haltungen SET ks = ?, laenge = ? WHERE haltnam = ?",
                "xml_import Haltung [4]",
                parameters=[haltung.ks, haltung.laenge, haltung.haltnam],
            ):
                return None

        self.db_qkan.commit()


    def _haltunggeom(self):
        blocks = self.xml.findall(
            "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']/d:Kante/d:Haltung/../..",
            self.NS,
        )

        x_start = 0
        y_start = 0
        x_end = 0
        y_end = 0

        # list = []
        for block in blocks:
            x_liste = []
            y_liste = []
            name = block.findtext("d:Objektbezeichnung", None, self.NS)

            found_kanten = block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS)
            if found_kanten is not None:
                if len(found_kanten) > 2:
                    for _gp in found_kanten:
                        xschob = _get_float(_gp.findtext("d:Kante/d:Start/d:Rechtswert", 0.0, self.NS))
                        yschob = _get_float(_gp.findtext("d:Kante/d:Start/d:Hochwert",0.0, self.NS))

                        x_liste.append(xschob)
                        y_liste.append(yschob)

                    text = str(name), x_liste, y_liste
                    # list.append(text)
            else:
                found_kanten = block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS)
                if found_kanten is not None:
                    if len(found_kanten) > 1:
                        for _gp in found_kanten:
                            xschob = _get_float(_gp.findtext("d:Start/d:Rechtswert", 0.0, self.NS))
                            yschob = _get_float(_gp.findtext("d:Start/d:Hochwert", 0.0, self.NS))

                            x_liste.append(xschob)
                            y_liste.append(yschob)

                        # text = str(name), x_liste, y_liste
                        # list.append(text)
        # list.append('Ende')

            if len(x_liste) == 0:
                continue
        # for line in list:
            #line_tokens = line.split(',')
            # name = line[0]
            # if line != "Ende":
            #     x_liste = line[1]   # xsch
            x_liste.pop(0)
                # #x_liste.pop(-1)
                # y_liste = line[2]   # ysch
            y_liste.pop(0)
                #y_liste.pop(-1)

            npt=1

            for xsch, ysch in zip(x_liste, y_liste):
                if npt == 1:
                    # Start und Endpunkt der Haltung ausgeben
                    sql = f"""Select 
                                ST_X(StartPoint(geom)) AS xanf,
                                ST_Y(StartPoint(geom)) AS yanf,
                                ST_X(EndPoint(geom))   AS xend,
                                ST_Y(EndPoint(geom))   AS yend
                            FROM haltungen
                            WHERE haltnam =?"""

                    self.db_qkan.sql(sql, parameters=[name,])
                    for attr in self.db_qkan.fetchall():
                        x_start, y_start, x_end, y_end = attr

                    # altes haltungsobjekt löschen, da AddPoint ansonsten nicht richtig funktioniert
                    sql = f"""
                                                 UPDATE haltungen SET geom = NULL
                                                 WHERE haltnam = ?
                                                 """

                    if not self.db_qkan.sql(
                            sql, parameters=[name,]
                    ):
                        del self.db_qkan
                        return False

                    #TODO: Geometrie erstellung anpassen
                    #prüfen ob die Erstellung und Löschung der einfachen Haltung notwendig ist
                    # if geotyp in ('Poly', 'L'):
                    #     ptlis = [QgsPoint(x, y) for x, y in gplis]
                    #     geom = QgsGeometry.fromPolyline(ptlis)
                    #     if not geom:
                    #         logger.error(f'Fehler bei polyline: {ptlis}')
                    #     else:
                    #         logger.warning(f'm150._get_HG_coords: geotyp unbekannt: {geotyp}')
                    #     continue
                    #
                    # if geom:
                    #     geom_wkb = geom.asWkb()
                    # else:
                    #     geom_wkb = None
                    #     logger.warning(f"M150-Import: Konnte keine Punktobjekte finden für Haltung {name}")

                    sql = f"""
                                     UPDATE haltungen SET geom = AddPoint(MakeLine(MakePoint(?, ?, ?), MakePoint(?, ?, ?)),
                                                    MakePoint(?, ?, ?), ?)
                                    WHERE haltnam = ?
                                 """

                    paralist = [x_start, y_start, QKan.config.epsg, x_end, y_end, QKan.config.epsg, xsch, ysch,
                                QKan.config.epsg, npt, name]

                    if not self.db_qkan.sql(
                               sql, parameters=paralist
                    ):
                        del self.db_qkan
                        return False

                if npt > 1:
                    # weitere punkte ergänzen
                    sql = f"""
                                        UPDATE haltungen SET geom = AddPoint(geom,MakePoint(?, ?, ?), ?)
                                        WHERE haltnam = ?
                                     """

                    paralist = [xsch, ysch, QKan.config.epsg, npt, name]

                    if not self.db_qkan.sql(
                            sql, parameters=paralist
                    ):
                        del self.db_qkan
                        return False

                npt+=1
            self.db_qkan.commit()


    #Haltung_untersucht
    def _haltungen_untersucht(self) -> None:
        def _iter() -> Iterator[Haltung_untersucht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']/d:Kante/d:Haltung/../..",
                self.NS,
            )

            logger.debug(f"Anzahl Haltungen: {len(blocks)}")


            schoben, schunten, profilnam = ("",) * 3
            (
                sohleoben,
                sohleunten,
                laenge,
                hoehe,
                breite,
                deckeloben,
                deckelunten,
            ) = (0.0,) * 7
            for block in blocks:

                name = block.findtext("d:Objektbezeichnung", None, self.NS)
                baujahr = _get_int(block.findtext("d:Baujahr", 0, self.NS))

                # TODO: Does <AbwassertechnischeAnlage> even contain multiple <Kante>?
                for _haltung in block.findall("d:Kante/d:KantenTyp/..", self.NS):
                    schoben = _haltung.findtext("d:KnotenZulauf", None, self.NS)
                    schunten = _haltung.findtext("d:KnotenAblauf", None, self.NS)

                    laenge = _get_float(_haltung.findtext("d:Laenge", 0.0, self.NS))


                    for profil in _haltung.findall("d:Profil", self.NS):
                        hoehe = (
                            _get_float(profil.findtext("d:Profilhoehe", 0.0, self.NS))

                        )
                        breite = (
                            _get_float(profil.findtext("d:Profilbreite", 0.0, self.NS))

                        )

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start", self.NS
                ):
                    if _haltung is not None:
                        xschob = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschob = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckeloben = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass


                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Start",
                        self.NS
                ):
                    if _haltung is not None:
                        xschob = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschob = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckeloben = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende", self.NS
                ):
                    if _haltung is not None:
                        xschun = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschun = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckelunten = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Ende",
                        self.NS
                ):
                    if _haltung is not None:
                        xschun = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschun = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckelunten = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                yield Haltung_untersucht(
                    haltnam=name,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                    baujahr=baujahr,
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
                )
                #else:
                 #   pass

        def _iter2() -> Iterator[Haltung_untersucht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Haltung/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Haltungen: {len(blocks)}")

            laenge = 0.0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Haltung", self.NS):

                    laenge = _get_float(
                        _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
                    )

                yield Haltung_untersucht(
                    haltnam=name,
                    laenge=laenge,
                )

        def _iter3() -> Iterator[Haltung_untersucht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Zustandsdatenkollektiv/d:InspizierteAbwassertechnischeAnlage/"
                "d:OptischeInspektion/d:Rohrleitung/../..",
                self.NS,
            )
            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            untersuchtag = ""
            untersucher = ""
            wetter = 0
            strasse = ""
            bewertungsart = 0
            bewertungstag = ""
            datenart = self.datenart

            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)
                strasse = block.findtext("d:Lage/d:Strassenname", None, self.NS)

                for _haltung in block.findall("d:OptischeInspektion", self.NS):

                    untersuchtag = _haltung.findtext("d:Inspektionsdatum", None, self.NS)

                    untersucher = _haltung.findtext("d:NameUntersucher", None, self.NS)

                    wetter = _get_int(_haltung.findtext("d:Wetter", "0", self.NS))

                    for _haltungz in _haltung.findall("d:Rohrleitung/d:Bewertung", self.NS):

                        bewertungsart = _get_int(_haltungz.findtext("d:Bewertungsverfahren", "0", self.NS))

                        bewertungstag = _haltungz.findtext("d:Bewertungsdatum", None, self.NS)

                yield Haltung_untersucht(
                    haltnam=name,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    wetter=wetter,
                    strasse=strasse,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                )

        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung_untersucht in _iter():

            params = {'haltnam': haltung_untersucht.haltnam, 'schoben': haltung_untersucht.schoben,
                      'schunten': haltung_untersucht.schunten, 'hoehe': haltung_untersucht.hoehe,
                      'breite': haltung_untersucht.breite, 'laenge': haltung_untersucht.laenge,
                      'kommentar': haltung_untersucht.kommentar, 'baujahr': haltung_untersucht.baujahr,
                      'strasse': haltung_untersucht.strasse, 'xschob': haltung_untersucht.xschob,
                      'yschob': haltung_untersucht.yschob, 'xschub': haltung_untersucht.xschun,
                      'yschun': haltung_untersucht.yschun, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen_untersucht\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen_untersucht",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        for haltung_untersucht in _iter2():
            if not self.db_qkan.sql(
                "UPDATE haltungen_untersucht SET laenge = ? WHERE haltnam = ?",
                "xml_import Haltungen_untersucht [2]",
                parameters=[haltung_untersucht.laenge, haltung_untersucht.haltnam],
            ):
                return None

        self.db_qkan.commit()

        for haltung_untersucht in _iter3():
            # Wetter
            wetter = self.db_qkan.get_from_mapper(
                haltung_untersucht.wetter,
                self.mapper_wetter,
                'haltungen_untersucht',
                'wetter',
                'bezeichnung',
                'isybau',
                'bemerkung',
            )

            if not self.db_qkan.sql(
                "UPDATE haltungen_untersucht SET untersuchtag=?, untersucher=?, wetter=?, strasse=?, bewertungsart=?," 
                "bewertungstag=?, datenart=? WHERE haltnam = ?",
                "xml_import Haltungen_untersucht [5]",
                parameters=[haltung_untersucht.untersuchtag, haltung_untersucht.untersucher, wetter, haltung_untersucht.strasse, haltung_untersucht.bewertungsart, haltung_untersucht.bewertungstag,
                            haltung_untersucht.datenart, haltung_untersucht.haltnam],
            ):
                return None

        self.db_qkan.commit()

    def _untersuchdat_haltung(self) -> None:
        def _iter() -> Iterator[Untersuchdat_haltung]:
            blocks = self.xml.findall(
               "d:Datenkollektive/d:Zustandsdatenkollektiv/d:InspizierteAbwassertechnischeAnlage/[d:Anlagentyp='1']/d:OptischeInspektion/"
               "d:Rohrleitung/d:Inspektionsdaten/d:RZustand/../../../..",
               self.NS,
            )

            logger.debug(f"Anzahl Untersuchungsdaten Haltung: {len(blocks)}")

            ordner_bild = self.ordner_bild
            ordner_video = self.ordner_video

            name = ""
            untersuchrichtung = ""
            schoben = ""
            schunten = ""
            id = 0
            inspektionslaenge = 0.0
            videozaehler = 0
            station = 0.0
            timecode = 0
            kuerzel = ""
            charakt1 = ""
            charakt2 = ""
            quantnr1 = 0.0
            quantnr2 = 0.0
            streckenschaden = ""
            pos_von = 0
            pos_bis = 0
            foto_dateiname = ""
            film_dateiname = ""


            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)

                for _untersuchdat_haltung in block.findall("d:OptischeInspektion/d:Rohrleitung", self.NS):

                    _ = _untersuchdat_haltung.findtext("d:Inspektionsrichtung", None, self.NS)
                    if _ == "O":
                        untersuchrichtung = "in Fließrichtung"
                    elif _ == "U":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.warning(f"Untersuchungsdaten Haltung: Fehlerhafter Wert in Feld Inspektionsrichtung: {_}")
                        untersuchrichtung = None

                    inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("d:Inspektionslaenge", "0.0", self.NS))
                    if inspektionslaenge == 0.0:
                        inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("d:Inspektionsdaten/d:RZustand[d:InspektionsKode='BCE'][d:Charakterisierung1='XP']/d:Station", "0.0", self.NS))


                    schoben = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenZulauf", None, self.NS)
                    schunten = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenAblauf", None, self.NS)


                    for _untersuchdat in _untersuchdat_haltung.findall("d:Inspektionsdaten/d:RZustand", self.NS):

                        id = _get_int(_untersuchdat.findtext("d:Index", "0", self.NS))
                        videozaehler = _get_int(_untersuchdat.findtext("d:Videozaehler", 0, self.NS))
                        station = _get_float(_untersuchdat.findtext("d:Station", 0.0, self.NS))
                        timecode = _get_int(_untersuchdat.findtext("d:Timecode", 0, self.NS))
                        kuerzel = _untersuchdat.findtext("d:InspektionsKode", None, self.NS)
                        charakt1 = _untersuchdat.findtext("d:Charakterisierung1", None, self.NS)
                        charakt2 = _untersuchdat.findtext("d:Charakterisierung2", None, self.NS)
                        quantnr1 = _get_float(_untersuchdat.findtext("d:Quantifizierung1Numerisch", 0.0, self.NS))
                        quantnr2 = _get_float(_untersuchdat.findtext("d:Quantifizierung2Numerisch", 0.0, self.NS))
                        streckenschaden = _untersuchdat.findtext("d:Streckenschaden", None, self.NS)
                        streckenschaden_lfdnr = _get_int(_untersuchdat.findtext("d:StreckenschadenLfdNr", 0, self.NS))
                        pos_von = _get_int(_untersuchdat.findtext("d:PositionVon", 0, self.NS))
                        pos_bis = _get_int(_untersuchdat.findtext("d:PositionBis", 0, self.NS))

                        _datei = _untersuchdat.findtext("d:Fotodatei", None, self.NS)
                        if _datei is not None and self.ordner_bild is not None:
                            foto_dateiname = os.path.join(self.ordner_bild, _datei)
                        else:
                            foto_dateiname = None

                        ZD = _get_int(_untersuchdat.findtext("d:Klassifizierung/d:Dichtheit/d:SKDvAuto", 63, self.NS))
                        ZS = _get_int(_untersuchdat.findtext("d:Klassifizierung/d:Standsicherheit/d:SKSvAuto", 63, self.NS))
                        ZB = _get_int(_untersuchdat.findtext("d:Klassifizierung/d:Standsicherheit/d:SKBvAuto", 63, self.NS))



                        yield Untersuchdat_haltung(
                        untersuchhal=name,
                        untersuchrichtung=untersuchrichtung,
                        schoben=schoben,
                        schunten=schunten,
                        id=id,
                        inspektionslaenge=inspektionslaenge,
                        videozaehler=videozaehler,
                        station=station,
                        timecode=timecode,
                        kuerzel=kuerzel,
                        charakt1=charakt1,
                        charakt2=charakt2,
                        quantnr1=quantnr1,
                        quantnr2=quantnr2,
                        streckenschaden=streckenschaden,
                        streckenschaden_lfdnr=streckenschaden_lfdnr,
                        pos_von=pos_von,
                        pos_bis=pos_bis,
                        foto_dateiname=foto_dateiname,
                        film_dateiname=film_dateiname,
                        ordner_bild=ordner_bild,
                        ordner_video=ordner_video,
                        ZD=ZD,
                        ZS=ZS,
                        ZB=ZB,

            )

        def _iter2() -> Iterator[Untersuchdat_haltung]:
                blocks = self.xml.findall(
                    "d:Datenkollektive/d:Zustandsdatenkollektiv/d:Filme/d:Film/d:Filmname/../..",
                    self.NS,
                )
                logger.debug(f"Anzahl Untersuchdat_haltung: {len(blocks)}")

                film_dateiname = ""
                for block in blocks:
                    for _untersuchdat_haltung in block.findall("d:Film/d:FilmObjekte/..", self.NS):

                        name = _untersuchdat_haltung.findtext("d:FilmObjekte/d:FilmObjekt/d:Objektbezeichnung", None, self.NS)

                        film_dateiname = self.ordner_video+_untersuchdat_haltung.findtext("d:Filmname", None, self.NS)

                        bandnr = _get_int(_untersuchdat_haltung.findtext("d:Videoablagereferenz", 0, self.NS))

                        yield Untersuchdat_haltung(
                            untersuchhal=name,
                            film_dateiname=film_dateiname,
                            bandnr=bandnr
                        )

        for untersuchdat_haltung in _iter():

            params = {'untersuchhal': untersuchdat_haltung.untersuchhal, 'untersuchrichtung': untersuchdat_haltung.untersuchrichtung,
                      'schoben': untersuchdat_haltung.schoben, 'schunten': untersuchdat_haltung.schunten,
                      'id': untersuchdat_haltung.id, 'videozaehler': untersuchdat_haltung.videozaehler,
                      'inspektionslaenge': untersuchdat_haltung.inspektionslaenge,
                      'station': untersuchdat_haltung.station,
                      'timecode': untersuchdat_haltung.timecode, 'kuerzel': untersuchdat_haltung.kuerzel,
                      'charakt1': untersuchdat_haltung.charakt1, 'charakt2': untersuchdat_haltung.charakt2,
                      'quantnr1': untersuchdat_haltung.quantnr1, 'quantnr2': untersuchdat_haltung.quantnr2,
                      'streckenschaden': untersuchdat_haltung.streckenschaden,
                      'streckenschaden_lfdnr': untersuchdat_haltung.streckenschaden_lfdnr,
                      'pos_von': untersuchdat_haltung.pos_von, 'pos_bis': untersuchdat_haltung.pos_bis,
                      'foto_dateiname': untersuchdat_haltung.foto_dateiname,
                      'film_dateiname': untersuchdat_haltung.film_dateiname,
                      'ordner_bild': untersuchdat_haltung.ordner_bild,
                      'ordner_video': untersuchdat_haltung.ordner_video, 'ZD': untersuchdat_haltung.ZD,
                      'ZB': untersuchdat_haltung.ZB, 'ZS': untersuchdat_haltung.ZS, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: untersuchdat_haltung\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_haltung",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        for untersuchdat_haltung in _iter2():

            if not self.db_qkan.sql(
                "UPDATE untersuchdat_haltung SET film_dateiname=?, bandnr=?" 
                " WHERE  untersuchhal= ?",
                "xml_import untersuchhal [2a]",
                parameters=[untersuchdat_haltung.film_dateiname,untersuchdat_haltung.bandnr, untersuchdat_haltung.untersuchhal],
            ):
                return None

        self.db_qkan.commit()

        self.db_qkan.setschadenstexte_haltungen()


    def _anschlussleitungen(self) -> None:
        def _iter() -> Iterator[Anschlussleitung]:

            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']",
                self.NS,
            )
            logger.debug(f"Anzahl Anschlussleitungen: {len(blocks)}")

            schoben, schunten, profilnam = ("",) * 3
            (
                sohleoben,
                sohleunten,
                laenge,
                hoehe,
                breite,
                deckeloben,
                deckelunten,
            ) = (0.0,) * 7
            for block in blocks:
                found_leitung = block.findtext("d:Kante/d:Leitung", "", self.NS)
                if found_leitung != '':
                    name = block.findtext("d:Objektbezeichnung", None, self.NS)
                    baujahr = _get_int(block.findtext("d:Baujahr", 0, self.NS))

                    # TODO: Does <AbwassertechnischeAnlage> even contain multiple <Kante>?
                    for _haltung in block.findall("d:Kante/d:KantenTyp/..", self.NS):
                        schoben = _haltung.findtext("d:KnotenZulauf", None, self.NS)
                        schunten = _haltung.findtext("d:KnotenAblauf", None, self.NS)

                        sohleoben = _get_float(
                            _haltung.findtext("d:SohlhoeheZulauf", 0.0, self.NS)
                        )
                        sohleunten = _get_float(
                            _haltung.findtext("d:SohlhoeheAblauf", 0.0, self.NS)
                        )
                        laenge = _get_float(_haltung.findtext("d:Laenge", 0.0, self.NS))

                        material = _haltung.findtext("d:Material", None, self.NS)

                        for profil in _haltung.findall("d:Profil", self.NS):
                            profilnam = profil.findtext("d:Profilart", None, self.NS)
                            hoehe = (
                                _get_float(profil.findtext("d:Profilhoehe", 0.0, self.NS))

                            )
                            breite = (
                                _get_float(profil.findtext("d:Profilbreite", 0.0, self.NS))

                            )


                    for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start", self.NS
                    ):
                        if _haltung is not None:
                            xschob = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschob = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckeloben = _get_float(
                                _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                            )
                        else:
                            pass

                    for _haltung in block.findall(
                            "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Start[1]",
                            self.NS
                    ):
                        if _haltung is not None:
                            xschob = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschob = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckeloben = _get_float(
                                _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                            )
                        else:
                            pass


                    for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende", self.NS
                    ):
                        if _haltung is not None:
                            xschun = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschun = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckelunten = _get_float(
                                _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                            )
                        else:
                            pass

                    for _haltung in block.findall(
                            "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Ende[last()]",
                            self.NS
                    ):
                        if _haltung is not None:
                            xschun = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschun = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckelunten = _get_float(
                                _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                            )
                        else:
                             pass

                    yield Anschlussleitung(
                        leitnam=name,
                        schoben=schoben,
                        schunten=schunten,
                        hoehe=hoehe,
                        breite=breite,
                        laenge=laenge,
                        material=material,
                        baujahr=baujahr,
                        sohleoben=sohleoben,
                        sohleunten=sohleunten,
                        deckeloben=deckeloben,
                        deckelunten=deckelunten,
                        profilnam=profilnam,
                        entwart=block.findtext("d:Entwaesserungsart", None, self.NS),
                        ks=1.5,  # in Hydraulikdaten enthalten.
                        simstatus=_get_int(block.findtext("d:Status", None, self.NS)),
                        kommentar=block.findtext("d:Kommentar", "-", self.NS),
                        xschob=xschob,
                        yschob=yschob,
                        xschun=xschun,
                        yschun=yschun,
                    )
                else:
                    pass

        def _iter2() -> Iterator[Anschlussleitung]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Leitung/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Anschlussleitung: {len(blocks)}")

            ks = 1.5
            laenge = 0.0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Leitung", self.NS):
                    cs1 = _haltung.findtext("d:Rauigkeitsansatz", "0", self.NS)
                    if cs1 == "1":
                        ks = _get_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKb", 0.0, self.NS)
                        )
                    elif cs1 == "2":
                        ks = _get_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKst", 0.0, self.NS)
                        )
                    else:
                        ks = 0.0
                        fehlermeldung(
                            "Fehler im XML-Import von HydraulikObjekte_Anschlussleitung",
                            f"Ungültiger Wert für Rauigkeitsansatz {cs1} in Anschlussleitung {name}",
                        )

                    laenge = _get_float(
                        _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
                    )

                yield Anschlussleitung(
                    leitnam=name,
                    laenge=laenge,
                    ks=ks,
                )


        # 1. Teil: Hier werden die Stammdaten zu den anschlussleitung in die Datenbank geschrieben
        for anschlussleitung in _iter():
            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                anschlussleitung.simstatus,
                self.mapper_simstatus,
                'anschlussleitungen',
                'simulationsstatus',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            # Entwässerungsart
            entwart = self.db_qkan.get_from_mapper(
                anschlussleitung.entwart,
                self.mapper_entwart,
                'anschlussleitungen',
                'entwaesserungsarten',
                'bezeichnung',
                'isybau',
                'bemerkung',
                'kuerzel',
            )

            # Profile
            profilnam = self.db_qkan.get_from_mapper(
                anschlussleitung.profilnam,
                self.mapper_profile,
                'anschlussleitungen',
                'profile',
                'profilnam',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            # Material
            material = self.db_qkan.get_from_mapper(
                anschlussleitung.material,
                self.mapper_material,
                'anschlussleitungen',
                'material',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            params = {'leitnam': anschlussleitung.leitnam,
                      'schoben': anschlussleitung.schoben, 'schunten': anschlussleitung.schunten,
                      'hoehe': anschlussleitung.hoehe, 'breite': anschlussleitung.breite,
                      'laenge': anschlussleitung.laenge, 'material': material, 'baujahr': anschlussleitung.baujahr,
                      'sohleoben': anschlussleitung.sohleoben, 'sohleunten': anschlussleitung.sohleunten,
                      'deckeloben': anschlussleitung.deckeloben, 'deckelunten': anschlussleitung.deckelunten,
                      'profilnam': profilnam, 'entwart': entwart,
                      'ks': anschlussleitung.ks, 'simstatus': simstatus,
                      'kommentar': anschlussleitung.kommentar, 'xschob': anschlussleitung.xschob,
                      'xschun': anschlussleitung.xschun, 'yschob': anschlussleitung.yschob,
                      'yschun': anschlussleitung.yschun, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: anschlussleitungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return


        self.db_qkan.commit()

        for anschlussleitung in _iter2():
            if not self.db_qkan.sql(
                "UPDATE anschlussleitungen SET ks = ?, laenge = ? WHERE leitnam = ?",
                "xml_import anschlussleitung [4]",
                parameters=[anschlussleitung.ks, anschlussleitung.laenge, anschlussleitung.leitnam],
            ):
                return None

        self.db_qkan.commit()

    def _anschlussleitunggeom(self):
        #blocks = self.xml.findall("HG")
        blocks = self.xml.findall(
            "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']",
            self.NS,
        )

        x_start = 0
        y_start = 0
        x_end = 0
        y_end = 0

        # list = []
        for block in blocks:
            x_liste = []
            y_liste = []

            found_leitung = block.findtext("d:Kante/d:Leitung", "", self.NS)
            if found_leitung != '':

                name = block.findtext("d:Objektbezeichnung", None, self.NS)

                # hier ergännzen mit dem fall das x,y unter Polygone steht!!
                # Haltungen können alternativ als Kanten oder als Polygone vorkommen.

                found_kanten = block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS)
                if found_kanten is not None:
                    if len(found_kanten) > 2:
                        for _gp in found_kanten:
                            xschob = _get_float(_gp.findtext("d:Kante/d:Start/d:Rechtswert", 0.0, self.NS))
                            yschob = _get_float(_gp.findtext("d:Kante/d:Start/d:Hochwert",0.0, self.NS))

                            x_liste.append(xschob)
                            y_liste.append(yschob)

                        text = str(name), x_liste, y_liste
                        list.append(text)


                else:
                    found_kanten = block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS)
                    if found_kanten is not None:
                        if len(found_kanten) > 1:
                            for _gp in found_kanten:
                                xschob = _get_float(_gp.findtext("d:Start/d:Rechtswert", 0.0, self.NS))
                                yschob = _get_float(_gp.findtext("d:Start/d:Hochwert", 0.0, self.NS))

                                x_liste.append(xschob)
                                y_liste.append(yschob)

                            text = str(name), x_liste, y_liste
                            list.append(text)
        # list.append('Ende')

            if len(x_liste) == 0:
                continue
            # for line in list:
            #line_tokens = line.split(',')
            # name = line[0]
            # if line != "Ende":
            #     x_liste = line[1]   # xsch
            x_liste.pop(0)
                #x_liste.pop(-1)
                # y_liste = line[2]   # ysch
            y_liste.pop(0)
                #y_liste.pop(-1)

            npt=1

            for xsch, ysch in zip(x_liste, y_liste):
                if npt == 1:
                    # Start und Endpunkt der Haltung ausgeben
                    sql = f"""Select 
                                ST_X(StartPoint(geom)) AS xanf,
                                ST_Y(StartPoint(geom)) AS yanf,
                                ST_X(EndPoint(geom))   AS xend,
                                ST_Y(EndPoint(geom))   AS yend
                            FROM anschlussleitungen
                            WHERE leitnam =?"""

                    self.db_qkan.sql(sql, parameters=(name,))
                    for attr in self.db_qkan.fetchall():
                        x_start, y_start, x_end, y_end = attr

                    # altes haltungsobjekt löschen, da AddPoint ansonsten nicht richtig funktioniert
                    sql = f"""
                                                 UPDATE anschlussleitungen SET geom = NULL
                                                 WHERE leitnam = ?
                                                 """

                    if not self.db_qkan.sql(
                            sql, parameters=[name,]
                    ):
                        del self.db_qkan
                        return False

                    sql = f"""
                                    UPDATE anschlussleitungen SET geom = AddPoint(MakeLine(MakePoint(?, ?, ?), MakePoint(?, ?, ?)),
                                                    MakePoint(?, ?, ?), ?)
                                    WHERE leitnam = ?
                                 """

                    paralist = [x_start, y_start, QKan.config.epsg, x_end, y_end, QKan.config.epsg, xsch, ysch,
                                QKan.config.epsg, npt, name]

                    if not self.db_qkan.sql(
                            sql, parameters=paralist
                    ):
                        del self.db_qkan
                        return False

                if npt > 1:
                    # weitere punkte ergänzen
                    sql = f"""
                                        UPDATE anschlussleitungen SET geom = AddPoint(geom,MakePoint(?, ?, ?), ?)
                                        WHERE leitnam = ?
                                     """

                    paralist = [xsch, ysch, QKan.config.epsg, npt, name]

                    if not self.db_qkan.sql(
                            sql, parameters=paralist
                    ):
                        del self.db_qkan
                        return False

                npt+=1
            self.db_qkan.commit()

    #TODO:Anschlussleitungen_untersucht ergänzen!
    # Anschluss_untersucht
    def _anschluss_untersucht(self) -> None:
        def _iter() -> Iterator[Anschlussleitung_untersucht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']/d:Kante/d:Leitung/../..",
                self.NS,
            )

            logger.debug(f"Anzahl Anschlussleitungen: {len(blocks)}")

            schoben, schunten, profilnam = ("",) * 3
            (
                sohleoben,
                sohleunten,
                laenge,
                hoehe,
                breite,
                deckeloben,
                deckelunten,
            ) = (0.0,) * 7
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)
                baujahr = _get_int(block.findtext("d:Baujahr", 0, self.NS))

                # TODO: Does <AbwassertechnischeAnlage> even contain multiple <Kante>?
                for _haltung in block.findall("d:Kante/d:KantenTyp/..", self.NS):
                    schoben = _haltung.findtext("d:KnotenZulauf", None, self.NS)
                    schunten = _haltung.findtext("d:KnotenAblauf", None, self.NS)

                    laenge = _get_float(_haltung.findtext("d:Laenge", 0.0, self.NS))

                    for profil in _haltung.findall("d:Profil", self.NS):
                        hoehe = (
                                _get_float(profil.findtext("d:Profilhoehe", 0.0, self.NS))

                        )
                        breite = (
                                _get_float(profil.findtext("d:Profilbreite", 0.0, self.NS))

                        )

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start", self.NS
                ):
                    if _haltung is not None:
                        xschob = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschob = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckeloben = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Start",
                        self.NS
                ):
                    if _haltung is not None:
                        xschob = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschob = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckeloben = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende", self.NS
                ):
                    if _haltung is not None:
                        xschun = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschun = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckelunten = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Ende",
                        self.NS
                ):
                    if _haltung is not None:
                        xschun = _get_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschun = _get_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckelunten = _get_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

            yield Anschlussleitung_untersucht(
                leitnam=name,
                schoben=schoben,
                schunten=schunten,
                hoehe=hoehe,
                breite=breite,
                laenge=laenge,
                kommentar=block.findtext("d:Kommentar", "-", self.NS),
                baujahr=baujahr,
                xschob=xschob,
                yschob=yschob,
                xschun=xschun,
                yschun=yschun,
            )
            # else:
            #   pass

        def _iter2() -> Iterator[Anschlussleitung_untersucht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Haltung/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Haltungen: {len(blocks)}")

            laenge = 0.0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", None, self.NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Haltung", self.NS):
                    laenge = _get_float(
                        _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
                    )

                yield Anschlussleitung_untersucht(
                    leitnam=name,
                    laenge=laenge,
                )

        def _iter3() -> Iterator[Anschlussleitung_untersucht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Zustandsdatenkollektiv/d:InspizierteAbwassertechnischeAnlage/"
                "d:OptischeInspektion/d:Rohrleitung/../..",
                self.NS,
            )
            logger.debug(f"Anzahl Anschlussleitungen: {len(blocks)}")

            untersuchtag = ""
            untersucher = ""
            wetter = None
            strasse = ""
            bewertungsart = None
            bewertungstag = ""
            datenart = self.datenart

            for block in blocks:
                found_leitung = block.findtext("d:Kante/d:Leitung", "", self.NS)
                if found_leitung != '':
                    name = block.findtext("d:Objektbezeichnung", None, self.NS)
                    strasse = block.findtext("d:Lage/d:Strassenname", None, self.NS)

                    for _haltung in block.findall("d:OptischeInspektion", self.NS):

                        untersuchtag = _haltung.findtext("d:Inspektionsdatum", None, self.NS)

                        untersucher = _haltung.findtext("d:NameUntersucher", None, self.NS)

                        wetter = _get_int(_haltung.findtext("d:Wetter", None, self.NS))

                        for _haltungz in _haltung.findall("d:Rohrleitung/d:Bewertung", self.NS):
                            bewertungsart = _get_int(_haltungz.findtext("d:Bewertungsverfahren", "0", self.NS))

                            bewertungstag = _haltungz.findtext("d:Bewertungsdatum", None, self.NS)

                    yield Anschlussleitung_untersucht(
                        haltnam=name,
                        untersuchtag=untersuchtag,
                        untersucher=untersucher,
                        wetter=wetter,
                        strasse=strasse,
                        bewertungsart=bewertungsart,
                        bewertungstag=bewertungstag,
                        datenart=datenart,
                    )

        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for anschlussleitung_untersucht in _iter():

            params = {'leitnam': anschlussleitung_untersucht.haltnam, 'schoben': anschlussleitung_untersucht.schoben,
                      'schunten': anschlussleitung_untersucht.schunten, 'hoehe': anschlussleitung_untersucht.hoehe,
                      'breite': anschlussleitung_untersucht.breite, 'laenge': anschlussleitung_untersucht.laenge,
                      'kommentar': anschlussleitung_untersucht.kommentar, 'baujahr': anschlussleitung_untersucht.baujahr,
                      'strasse': anschlussleitung_untersucht.strasse, 'xschob': anschlussleitung_untersucht.xschob,
                      'yschob': anschlussleitung_untersucht.yschob, 'xschub': anschlussleitung_untersucht.xschun,
                      'yschun': anschlussleitung_untersucht.yschun, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: anschlussleitung_untersucht\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen_untersucht",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        for anschlussleitung_untersucht in _iter2():
            if not self.db_qkan.sql(
                    "UPDATE anschlussleitungen_untersucht SET laenge = ? WHERE leitnam = ?",
                    "xml_import anschlussleitungen_untersucht [2]",
                    parameters=[anschlussleitung_untersucht.laenge, anschlussleitung_untersucht.leitnam],
            ):
                return None

        self.db_qkan.commit()

        for anschlussleitung_untersucht in _iter3():
            # Wetter
            wetter = self.db_qkan.get_from_mapper(
                anschlussleitung_untersucht.wetter,
                self.mapper_wetter,
                'anschlussleitungen_untersucht',
                'wetter',
                'bezeichnung',
                'isybau',
                'bemerkung',
            )

            if not self.db_qkan.sql(
                    "UPDATE anschlussleitungen_untersucht SET untersuchtag=?, untersucher=?, wetter=?, strasse=?, bewertungsart=?,"
                    "bewertungstag=?, datenart=? WHERE leitnam = ?",
                    "xml_import Haltungen_untersucht [5]",
                    parameters=[anschlussleitung_untersucht.untersuchtag, anschlussleitung_untersucht.untersucher, wetter,
                                anschlussleitung_untersucht.strasse, anschlussleitung_untersucht.bewertungsart, anschlussleitung_untersucht.bewertungstag,
                                anschlussleitung_untersucht.datenart, anschlussleitung_untersucht.leitnam],
            ):
                return None

        self.db_qkan.commit()

    def _untersuchdat_anschluss(self) -> None:
        def _iter() -> Iterator[Untersuchdat_anschlussleitung]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Zustandsdatenkollektiv/d:InspizierteAbwassertechnischeAnlage/[d:Anlagentyp='2']/d:OptischeInspektion/"
                "d:Rohrleitung/d:Inspektionsdaten/d:RZustand/../../../..",
                self.NS,
            )

            logger.debug(f"Anzahl Untersuchungsdaten Anschluesse: {len(blocks)}")

            ordner_bild = self.ordner_bild
            ordner_video = self.ordner_video

            name = ""
            untersuchrichtung = ""
            schoben = ""
            schunten = ""
            id = 0
            inspektionslaenge = 0.0
            videozaehler = 0
            station = 0.0
            timecode = 0
            kuerzel = ""
            charakt1 = ""
            charakt2 = ""
            quantnr1 = 0.0
            quantnr2 = 0.0
            streckenschaden = ""
            pos_von = 0
            pos_bis = 0
            foto_dateiname = ""
            film_dateiname = ""

            for block in blocks:
                found_leitung = block.findtext("d:Kante/d:Leitung", "", self.NS)
                if found_leitung != '':

                    name = block.findtext("d:Objektbezeichnung", None, self.NS)

                    for _untersuchdat_haltung in block.findall("d:OptischeInspektion/d:Rohrleitung", self.NS):

                        _ = _untersuchdat_haltung.findtext("d:Inspektionsrichtung", None, self.NS)
                        if _ == "O":
                            untersuchrichtung = "in Fließrichtung"
                        elif _ == "U":
                            untersuchrichtung = "gegen Fließrichtung"
                        else:
                            logger.warning(f"Untersuchungsdaten Anschluss: Fehlerhafter Wert in Feld Inspektionsrichtung: {_}")
                            untersuchrichtung = None

                        inspektionslaenge = _get_float(
                            _untersuchdat_haltung.findtext("d:Inspektionslaenge", "0.0", self.NS))
                        if inspektionslaenge == 0.0:
                            inspektionslaenge = _get_float(_untersuchdat_haltung.findtext(
                                "d:Inspektionsdaten/d:RZustand[d:InspektionsKode='BCE'][d:Charakterisierung1='XP']/d:Station",
                                "0.0", self.NS))

                        schoben = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenZulauf", None, self.NS)
                        schunten = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenAblauf", None, self.NS)

                        for _untersuchdat in _untersuchdat_haltung.findall("d:Inspektionsdaten/d:RZustand", self.NS):
                            id = _get_int(_untersuchdat.findtext("d:Index", "0", self.NS))
                            videozaehler = _get_int(_untersuchdat.findtext("d:Videozaehler", 0, self.NS))
                            station = _get_float(_untersuchdat.findtext("d:Station", 0.0, self.NS))
                            timecode = _get_int(_untersuchdat.findtext("d:Timecode", 0, self.NS))
                            kuerzel = _untersuchdat.findtext("d:InspektionsKode", None, self.NS)
                            charakt1 = _untersuchdat.findtext("d:Charakterisierung1", None, self.NS)
                            charakt2 = _untersuchdat.findtext("d:Charakterisierung2", None, self.NS)
                            quantnr1 = _get_float(_untersuchdat.findtext("d:Quantifizierung1Numerisch", 0.0, self.NS))
                            quantnr2 = _get_float(_untersuchdat.findtext("d:Quantifizierung2Numerisch", 0.0, self.NS))
                            streckenschaden = _untersuchdat.findtext("d:Streckenschaden", None, self.NS)
                            streckenschaden_lfdnr = _get_int(
                                _untersuchdat.findtext("d:StreckenschadenLfdNr", 0, self.NS))
                            pos_von = _get_int(_untersuchdat.findtext("d:PositionVon", 0, self.NS))
                            pos_bis = _get_int(_untersuchdat.findtext("d:PositionBis", 0, self.NS))

                            _datei = _untersuchdat.findtext("d:Fotodatei", None, self.NS)
                            if _datei is not None and self.ordner_bild is not None:
                                foto_dateiname = os.path.join(self.ordner_bild, _datei)
                            else:
                                foto_dateiname = None

                            ZD = _get_int(
                                _untersuchdat.findtext("d:Klassifizierung/d:Dichtheit/d:SKDvAuto", 63, self.NS))
                            ZS = _get_int(
                                _untersuchdat.findtext("d:Klassifizierung/d:Standsicherheit/d:SKSvAuto", 63, self.NS))
                            ZB = _get_int(
                                _untersuchdat.findtext("d:Klassifizierung/d:Standsicherheit/d:SKBvAuto", 63, self.NS))

                            yield Untersuchdat_anschlussleitung(
                                untersuchhal=name,
                                untersuchrichtung=untersuchrichtung,
                                schoben=schoben,
                                schunten=schunten,
                                id=id,
                                inspektionslaenge=inspektionslaenge,
                                videozaehler=videozaehler,
                                station=station,
                                timecode=timecode,
                                kuerzel=kuerzel,
                                charakt1=charakt1,
                                charakt2=charakt2,
                                quantnr1=quantnr1,
                                quantnr2=quantnr2,
                                streckenschaden=streckenschaden,
                                streckenschaden_lfdnr=streckenschaden_lfdnr,
                                pos_von=pos_von,
                                pos_bis=pos_bis,
                                foto_dateiname=foto_dateiname,
                                film_dateiname=film_dateiname,
                                ordner_bild=ordner_bild,
                                ordner_video=ordner_video,
                                ZD=ZD,
                                ZS=ZS,
                                ZB=ZB,

                            )

        def _iter2() -> Iterator[Untersuchdat_anschlussleitung]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Zustandsdatenkollektiv/d:Filme/d:Film/d:Filmname/../..",
                self.NS,
            )
            logger.debug(f"Anzahl Untersuchdat_haltung: {len(blocks)}")

            film_dateiname = ""
            for block in blocks:
                for _untersuchdat_haltung in block.findall("d:Film/d:FilmObjekte/..", self.NS):
                    name = _untersuchdat_haltung.findtext("d:FilmObjekte/d:FilmObjekt/d:Objektbezeichnung", None,
                                                          self.NS)

                    film_dateiname = self.ordner_video+_untersuchdat_haltung.findtext("d:Filmname", None, self.NS)

                    bandnr = _get_int(_untersuchdat_haltung.findtext("d:Videoablagereferenz", 0, self.NS))

                    yield Untersuchdat_anschlussleitung(
                        untersuchhal=name,
                        film_dateiname=film_dateiname,
                        bandnr=bandnr
                    )

        for untersuchdat_anschlussleitung in _iter():

            params = {'untersuchleit': untersuchdat_anschlussleitung.untersuchhal, 'untersuchrichtung': untersuchdat_anschlussleitung.untersuchrichtung,
                      'schoben': untersuchdat_anschlussleitung.schoben, 'schunten': untersuchdat_anschlussleitung.schunten,
                      'id': untersuchdat_anschlussleitung.id, 'videozaehler': untersuchdat_anschlussleitung.videozaehler,
                      'inspektionslaenge': untersuchdat_anschlussleitung.inspektionslaenge,
                      'station': untersuchdat_anschlussleitung.station,
                      'timecode': untersuchdat_anschlussleitung.timecode, 'kuerzel': untersuchdat_anschlussleitung.kuerzel,
                      'charakt1': untersuchdat_anschlussleitung.charakt1, 'charakt2': untersuchdat_anschlussleitung.charakt2,
                      'quantnr1': untersuchdat_anschlussleitung.quantnr1, 'quantnr2': untersuchdat_anschlussleitung.quantnr2,
                      'streckenschaden': untersuchdat_anschlussleitung.streckenschaden,
                      'streckenschaden_lfdnr': untersuchdat_anschlussleitung.streckenschaden_lfdnr,
                      'pos_von': untersuchdat_anschlussleitung.pos_von, 'pos_bis': untersuchdat_anschlussleitung.pos_bis,
                      'foto_dateiname': untersuchdat_anschlussleitung.foto_dateiname,
                      'film_dateiname': untersuchdat_anschlussleitung.film_dateiname,
                      'ordner_bild': untersuchdat_anschlussleitung.ordner_bild,
                      'ordner_video': untersuchdat_anschlussleitung.ordner_video, 'ZD': untersuchdat_anschlussleitung.ZD,
                      'ZB': untersuchdat_anschlussleitung.ZB, 'ZS': untersuchdat_anschlussleitung.ZS, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: untersuchdat_anschlussleitung\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_anschlussleitung",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        # geometrieobjekt erzeugen

        for untersuchdat_anschlussleitung in _iter2():
            if not self.db_qkan.sql(
                    "UPDATE untersuchdat_anschlussleitung SET film_dateiname=?, bandnr=?"
                    " WHERE  untersuchhal= ?",
                    "xml_import untersuchhal [2a]",
                    parameters=[untersuchdat_anschlussleitung.film_dateiname, untersuchdat_anschlussleitung.bandnr,
                                untersuchdat_anschlussleitung.untersuchhal],
            ):
                return None

        self.db_qkan.commit()

    def _wehre(self) -> None:
        # Hier werden die Hydraulikdaten zu den Wehren in die Datenbank geschrieben.
        # Bei Wehren stehen alle wesentlichen Daten im Hydraulikdatenkollektiv, weshalb im Gegensatz zu den
        # Haltungsdaten keine Stammdaten verarbeitet werden.

        def _iter() -> Iterator[Wehr]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Wehr/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Wehre: {len(blocks)}")

            schoben, schunten, wehrtyp = ("",) * 3
            schwellenhoehe, kammerhoehe, laenge, uebeiwert = (0.0,) * 4
            for block in blocks:
                # TODO: Does <HydraulikObjekt> even contain multiple <Wehr>?
                for _wehr in block.findall("d:Wehr", self.NS):
                    schoben = _wehr.findtext("d:SchachtZulauf", None, self.NS)
                    schunten = _wehr.findtext("d:SchachtAblauf", None, self.NS)
                    wehrtyp = _wehr.findtext("d:WehrTyp", None, self.NS)

                    schwellenhoehe = _get_float(
                        _wehr.findtext("d:Schwellenhoehe", 0.0, self.NS)
                    )
                    laenge = _get_float(
                        _wehr.findtext("d:LaengeWehrschwelle", 0.0, self.NS)
                    )
                    kammerhoehe = _get_float(_wehr.findtext("d:Kammerhoehe", 0.0, self.NS))

                    # Überfallbeiwert der Wehr Kante (abhängig von Form der Kante)
                    uebeiwert = _get_float(
                        _wehr.findtext("d:Ueberfallbeiwert", 0.0, self.NS)
                    )

                yield Wehr(
                    wnam=block.findtext("d:Objektbezeichnung", None, self.NS),
                    schoben=schoben,
                    schunten=schunten,
                    wehrtyp=wehrtyp,
                    schwellenhoehe=schwellenhoehe,
                    kammerhoehe=kammerhoehe,
                    laenge=laenge,
                    uebeiwert=uebeiwert,
                )

        for wehr in _iter():


            params = {'haltnam': wehr.wnam, 'schoben': wehr.schoben, 'schunten': wehr.schunten,
                      'sohleunten': wehr.sohle,
                      'haltungtyp': 'Wehr',  # dient dazu, das Verbindungselement als Pumpe zu klassifizieren
                      'simstatus': wehr.simstatus, 'kommentar': wehr.kommentar, 'epsg': QKan.config.epsg}
            # if not self.db_qkan.sql(sql, "xml_import Pumpen [2]", params):
            #     return None

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _pumpen(self) -> None:
        def _iter() -> Iterator[Pumpe]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/"
                "d:Knoten/d:Bauwerk/d:Pumpe/../../..",
                self.NS,
            )
            logger.debug(f"Anzahl Pumpen: {len(blocks)}")

            for block in blocks:
                yield Pumpe(
                    pnam=block.findtext("d:Objektbezeichnung", None, self.NS),
                    simstatus=_get_int(block.findtext("d:Status", None, self.NS)),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                )

        def _iter2() -> Iterator[Pumpe]:
            # Hydraulik
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Pumpe/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Pumpen: {len(blocks)}")

            schoben, schunten, steuersch = ("",) * 3
            _pumpentyp = 0
            volanf, volges, sohle = (0.0,) * 3
            for block in blocks:
                # TODO: Does <HydraulikObjekt> even contain multiple <Pumpe>?
                # `_pumpe = block.find("d:Pumpe", NS)` should be used if it does not
                for _pumpe in block.findall("d:Pumpe", self.NS):
                    _pumpentyp = _get_int(_pumpe.findtext("d:PumpenTyp", -1, self.NS))
                    schoben = _pumpe.findtext("d:SchachtZulauf", None, self.NS)
                    schunten = _pumpe.findtext("d:SchachtAblauf", None, self.NS)
                    steuersch = _pumpe.findtext("d:Steuerschacht", None, self.NS)
                    sohle = _get_float(_pumpe.findtext("d:Sohlhoehe", 0.0, self.NS))
                    volanf = _get_float(_pumpe.findtext("d:Anfangsvolumen", 0.0, self.NS))
                    volges = _get_float(_pumpe.findtext("d:Gesamtvolumen", 0.0, self.NS))

                yield Pumpe(
                    pnam=block.findtext("d:Objektbezeichnung", None, self.NS),
                    schoben=schoben,
                    schunten=schunten,
                    pumpentyp=_pumpentyp,
                    volanf=volanf,
                    volges=volges,
                    sohle=sohle,
                    steuersch=steuersch,
                )

        for pumpe in _iter2():
            # geom = geo_hydro()

            if str(pumpe.pumpentyp) in self.mapper_pump:
                pumpentyp = self.mapper_pump[str(pumpe.pumpentyp)]
            else:
                pumpentyp = "{}".format(pumpe.pumpentyp)
                self.mapper_pump[str(pumpe.pumpentyp)] = pumpentyp
                if not self.db_qkan.sql(
                    "INSERT INTO pumpentypen (bezeichnung) Values (?)",
                    "xml_import Pumpe [1]",
                    parameters=[pumpe.pumpentyp,],
                ):
                    break


            params = {'haltnam': pumpe.pnam, 'schoben': pumpe.schoben, 'schunten': pumpe.schunten,
                     'sohleunten': pumpe.sohle,
                     'haltungtyp': 'Pumpe',  # dient dazu, das Verbindungselement als Pumpe zu klassifizieren
                     'simstatus': pumpe.simstatus, 'kommentar': pumpe.kommentar, 'epsg': QKan.config.epsg}
            # if not self.db_qkan.sql(sql, "xml_import Pumpen [2]", params):
            #     return None

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return


        self.db_qkan.commit()

        for pumpe in _iter():
            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                pumpe.simstatus,
                self.mapper_simstatus,
                'schacht',
                'simulationsstatus',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            if not self.db_qkan.sql(
                "UPDATE haltungen SET simstatus = ?, kommentar = ? WHERE haltnam = ?",
                "xml_import (22)",
                parameters=[simstatus, pumpe.kommentar, pumpe.pnam],
            ):
                return None

        self.db_qkan.commit()
