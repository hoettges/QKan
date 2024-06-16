import re
import sys
import xml.etree.ElementTree as ElementTree
from typing import Dict, Iterator

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis

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
    # entwart: str = ""
    strasse: str = ""
    knotentyp: str = ""
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
    untersuchtag: str = ""
    #TODO: videozaehler = Uhrzeit hh:mm
    videozaehler: str = ""
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
    haltnam: str = ""
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    sohleoben: float = 0.0
    sohleunten: float = 0.0
    profilnam: str = ""
    baujahr: int = 0
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
    haltnam: str = ""
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
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0
    datenart: str = ""
    max_ZD: int = 63
    max_ZB: int = 63
    max_ZS: int = 63

class Untersuchdat_haltung(ClassObject):
    untersuchhal: str = ""
    untersuchrichtung: str = ""
    schoben: str = ""
    schunten: str = ""
    id: int = 0
    untersuchtag: str = ""
    inspektionslaenge: float = 0.0
    videozaehler: str = ""
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
    baujahr: int = 0
    entwart: str = ""
    material: str = ""
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
    bewertungsart: int = 0
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
    wnam: str =""
    schoben: str =""
    schunten: str =""
    wehrtyp: str =""
    schwellenhoehe: float
    kammerhoehe: float
    laenge: float
    uebeiwert: float
    simstatus: str = ""
    kommentar: str = ""
    xsch: float = 0.0
    ysch: float = 0.0

class Pumpe(ClassObject):
    pnam: str =""
    schoben: str = ""  # //HydraulikObjekt/Pumpe/SchachtZulauf
    schunten: str = ""  # //HydraulikObjekt/Pumpe/SchachtAblauf
    # pumpentyp: int = 0  # //HydraulikObjekt/Pumpe/PumpenTyp
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

def _get_float(block, tag: str, default: float = None) -> [float, None]:
    """Liest einen Tag und meldet falschen Datentyp"""
    text = block.findtext(tag, default)
    if text is None:
        return None
    elif isinstance(text, float):
        return text
    elif text.strip() == "":
        logger.warning(f'Feld <{tag}> ist leer')
    elif isinstance(text, str):
        try:
            return float(text)
        except ValueError:
            logger.warning("_m150porter._import.py._get_float: %s" % sys.exc_info()[1])
            logger.warning(f'Falscher Datentyp in Feld <{tag}>')
        except Exception:
            logger.warning("_m150porter._import.py._get_float: %s" % sys.exc_info()[1])
            logger.warning(f'Fehler in Feld <{tag}>')
    return default

def _get_int(block, tag: str, default: int = None) -> [int, None]:
    """Liest einen Tag und meldet falschen Datentyp"""
    text = block.findtext(tag, default)
    if text is None:
        return None
    elif isinstance(text, int):
        return text
    elif text.strip() == "":
        logger.warning(f'Feld <{tag}> ist leer')
    elif isinstance(text, str):
        try:
            return int(text)
        except ValueError:
            logger.warning("_m150porter._import.py._get_int: %s" % sys.exc_info()[1])
            logger.warning(f'Falscher Datentyp in Feld <{tag}>')
        except Exception:
            logger.warning("_m150porter._import.py._get_int: %s" % sys.exc_info()[1])
            logger.warning(f'Fehler in Feld <{tag}>')
    return default


# noinspection SqlNoDataSourceInspection, SqlResolve
class ImportTask:
    def __init__(self, db_qkan: DBConnection, xml_file: str, data_choice: str, ordner_bild: str, ordner_video: str):
        self.db_qkan = db_qkan
        self.ordner_bild = ordner_bild
        self.ordner_video = ordner_video


        self.data_coice= data_choice
        if data_choice == "ISYBAU Daten":
            self.datenart = "ISYBAU"
        if data_choice == "DWA M-150 Daten":
            self.datenart = "DWA"

        # nr (str) => description
        self.mapper_entwart: Dict[str, str] = {}
        self.mapper_pump: Dict[str, str] = {}
        self.mapper_material: Dict[str, str] = {}
        self.mapper_profile: Dict[str, str] = {}
        # self.mapper_outlet: Dict[str, str] = {}
        self.mapper_simstatus: Dict[str, str] = {}
        # self.mapper_untersuchrichtung: Dict[str, str] = {}
        self.mapper_wetter: Dict[str, str] = {}
        # self.mapper_bewertungsart: Dict[str, str] = {}
        self.mapper_druckdicht: Dict[str, str] = {}


        # Load XML
        self.xml = ElementTree.ElementTree()
        self.xml.parse(xml_file)

    def run(self) -> bool:

        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Import aus M150 läuft. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

        self._reftables()                                   ;self.progress_bar.setValue(5)
        self._init_mappers()
#        if getattr(QKan.config.xml, "import_stamm", True):
        if QKan.config.xml.import_stamm:
            self._schaechte()                               ;self.progress_bar.setValue(10)
            self._auslaesse()                               ;self.progress_bar.setValue(20)
            #self._speicher()
            self._haltungen()                               ;self.progress_bar.setValue(30)
            self._haltunggeom()                             ;self.progress_bar.setValue(35)
            #self._wehre()
            self._pumpen()                                  ;self.progress_bar.setValue(40)
        # if getattr(QKan.config.xml, "import_haus", True):
        if QKan.config.xml.import_haus:
            self._anschlussleitungen()                      ;self.progress_bar.setValue(50)
            self._anschlussleitunggeom()                    ;self.progress_bar.setValue(55)
        # if getattr(QKan.config.xml, "import_zustand", True):
        if QKan.config.xml.import_zustand:
            self._schaechte_untersucht()                    ;self.progress_bar.setValue(65)
            self._untersuchdat_schaechte()                  ;self.progress_bar.setValue(75)
            self._haltungen_untersucht()                    ;self.progress_bar.setValue(85)
            self._untersuchdat_haltung()                    ;self.progress_bar.setValue(95)

        self.progress_bar.setValue(100)
        status_message.setText("Fertig! M150-Import abgeschlossen.")

        return True

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für DWA-Import füllen"""

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert - SQLite

        # Referenztabelle Entwässerungsarten

        params = []

        blocks = self.xml.findall("RT/RT001[.='104']/..")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Kanalnutzung": {len(blocks)}')

        for block in blocks:
            nr = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            # Falls einer der beiden Einträge fehlt:
            if nr is None or bez is None:
                continue
            params.append(
                {
                    'bezeichnung': bez,
                    'kuerzel': nr,
                    'bemerkung': 'aus Referenztabelle in der M150-Datei',
                    'he_nr': None,
                    'kp_nr': None,
                    'm150':nr,
                    'isybau': None,
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if not blocks:
            data = [
                ('Regenwasser', 'R', 'Regenwasser', 1, 2, 'R', 'KR'),
                ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1, 'S', 'KS'),
                ('Mischwasser', 'M', 'Mischwasser', 0, 0, 'M', 'KM'),
                ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, 'Ge', None),
            ]

            for langtext, kurztext, kommentar, he_nr, kp_nr, m150, isybau in data:
                params.append(
                    {
                        'bezeichnung': langtext,
                        'kuerzel': kurztext,
                        'bemerkung': kommentar,
                        'he_nr': None,
                        'kp_nr': None,
                        'm150': m150,
                        'isybau': None,
                    }
                )

        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau)
                    SELECT :bezeichnung, :kuerzel, :bemerkung, :he_nr, :kp_nr, :m150, :isybau
                    WHERE bezeichnung NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "M150 Import Referenzliste entwaesserungsarten", params, many=True):
            return False

        # Referenztabelle Profile

        params = []

        blocks = self.xml.findall("RT/RT001[.='106']/..")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Profilart": {len(blocks)}')

        for block in blocks:
            nr = block.findtext("RT002", None)
            kuerzel = block.findtext("RT003", nr)
            bez = block.findtext("RT004", None)
            bemerkung = block.findtext("RT999", 'aus Referenztabelle in der M150-Datei')
            # Falls einer der beiden Einträge fehlt:
            if nr is None or bez is None:
                continue
            params.append(
                {
                    'profilnam': bez,
                    'kuerzel': kuerzel,
                    'bemerkung': bemerkung,
                    'he_nr': None,
                    'kp_nr': None,
                    'm150':nr,
                    'isybau': None,
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:

        if not blocks:
            data = [
                ('Kreis', 'DN', 1, 1, None, 0, 'DN', None),
                ('Rechteck', 'RE', 2, 3, None, 3, 'RE', None),
                ('Ei (B:H = 2:3)', 'EI', 3, 5, None, 1, 'EI', None),
                ('Maul (B:H = 2:1,66)', 'MA', 4, 4, None, 2, 'MA', None),
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
                ('Sonderprofil', 68, 2, None, None, None, None),
                ('Gerinne', 'RI', 69, None, None, None, None, None),
                ('Trapez (offen)', 'TR', 900, None, None, 8, None, None),
                ('Rechteck offen', None, None, None, None, 5, None, None)
                ('Doppeltrapez (offen)', None, 901, None, None, None, None, None),
                ('Offener Graben', 'GR', None, None, None, None, 'GR', None),
                ('Oval', 'OV', None, None, None, 12, 'OV', None),
            ]

            for profilnam, kuerzel, he_nr, mu_nr, kp_key, isybau, m150, m145 in data:
                params.append(
                    {
                        'profilnam': profilnam,
                        'kuerzel': kuerzel,
                        'he_nr': None,
                        'mu_nr': None,
                        'kp_key': None,
                        'isybau': None,
                        'm150': m150,
                        'm145': None,
                        'kommentar': 'QKan-Standard',
                    }
                )

            sql = """INSERT INTO profile (profilnam, kuerzel, he_nr, mu_nr, kp_key, isybau, m150, m145, kommentar)
                        SELECT
                            :profilnam, :kuerzel, :he_nr, :mu_nr, :kp_key, 
                            :isybau, :m150, :m145, :kommentar
                        WHERE profilnam NOT IN (SELECT profilnam FROM profile)"""
            if not self.db_qkan.sql(sql, "M150 Import Referenzliste profile", params, many=True):
                return False

        # Referenztabelle Simulationsarten (M150: Funktionszustand)

        params = []

        blocks = self.xml.findall("RT/RT001[.='109']/..")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Funktionszustand": {len(blocks)}')

        for block in blocks:
            nr = block.findtext("RT002", None)
            kuerzel = block.findtext("RT003", nr)
            bez = block.findtext("RT004", None)
            bemerkung = block.findtext("RT999", 'aus Referenztabelle in der M150-Datei')
            # Falls einer der beiden Einträge fehlt:
            if nr is None or bez is None:
                continue
            params.append(
                {
                    'bezeichnung': bez,
                    'kuerzel': kuerzel,
                    'he_nr': None,
                    'mu_nr': None,
                    'kp_nr': None,
                    'm150':nr,
                    'm145': None,
                    'isybau': None,
                    'kommentar': bemerkung,
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:

        if not blocks:
            data = [          #   kurz    he    mu    kp  m150  m145   isy
                ('in Betrieb',     'B',    1,    1,    0,  'B',  '1',  '0', 'QKan-Standard'),
                ('außer Betrieb',  'AB',   4, None,    3,  'B',  '1', '20', 'QKan-Standard'),
                ('geplant',        'P',    2, None,    1,  'P', None, '10', 'QKan-Standard'),
                ('stillgelegt',    'N', None, None,    4,  'N', None, '21', 'QKan-Standard'),
                ('verdämmert',     'V',    5, None, None,  'V', None, None, 'QKan-Standard'),
                ('fiktiv',         'F',    3, None,    2, None, None, '99', 'QKan-Standard'),
                ('rückgebaut',     'P', None, None,    6, None, None, '22', 'QKan-Standard'),
            ]

            for bezeichnung, kuerzel, he_nr, mu_nr, kp_nr, m150, m145, isybau, kommentar in data:
                params.append(
                    {
                        'bezeichnung': bezeichnung,
                        'kuerzel': kuerzel,
                        'he_nr': he_nr,
                        'mu_nr': mu_nr,
                        'kp_nr': kp_nr,
                        'isybau': None,
                        'm150': m150,
                        'm145': None,
                        'kommentar': 'QKan-Standard',
                    }
                )

            sql = """INSERT INTO simulationsstatus (profilnam, kuerzel, he_nr, mu_nr, kp_nr, isybau, m150, m145, kommentar)
                        SELECT
                            :bezeichnung, :kuerzel, :he_nr, :mu_nr, :kp_nr, 
                            :isybau, :m150, :m145, :kommentar
                        WHERE bezeichnung NOT IN (SELECT bezeichnung FROM simulationsstatus)"""
            if not self.db_qkan.sql(sql, "M150 Import Referenzliste Simulationsstatus", params, many=True):
                return False

        # Referenztabelle Material

        params = []

        blocks = self.xml.findall("RT/RT001[.='105']/..")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Material": {len(blocks)}')

        for block in blocks:
            nr = block.findtext("RT002", None)
            kuerzel = block.findtext("RT003", nr)
            bez = block.findtext("RT004", None)
            bemerkung = block.findtext("RT999", 'aus Referenztabelle in der M150-Datei')
            # Falls einer der beiden Einträge fehlt:
            if nr is None or bez is None:
                continue
            params.append(
                {
                    'bezeichnung': bez,
                    'kuerzel': kuerzel,
                    'm150':nr,
                    'm145': None,
                    'isybau': None,
                    'kommentar': bemerkung,
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:

        if not blocks:
            data = [          #   kurz    m150  m145   isy
                ('Asbestzement', 'AZ', 'AZ', '7', 'AZ'),
                ('Beton', 'B', 'B', '2', 'B'),
                ('Bitumen', 'BIT', 'BIT', None, None),
                ('Betonsegmente', 'BS', 'BS', None, 'BS'),
                ('Betonsegmente kunststoffmodifiziert', 'BSK', 'BSK', None, None),
                ('Bitumen', 'BT', 'BT', None, None),
                ('Edelstahl', 'CN', 'CN', '22', None),
                ('Nichtidentifiziertes Metall (z. B. Eisen und Stahl)', 'EIS', 'EIS', None, 'EIS'),
                ('Epoxydharz', 'EPX', 'EPX', None, None),
                ('Epoxydharz mit Synthesefaser', 'EPSF', 'EPSF', None, None),
                ('Faserzement', 'FZ', 'FZ', '6', 'FZ'),
                ('Glasfaserverstärkter Kunststoff', 'GFK', 'GFK', '51', 'GFK'),
                ('Grauguß', 'GG', 'GG', '4', 'GG'),
                ('Duktiles Gußeisen', 'GGG', 'GGG', '5', 'GGG'),
                ('Nichtidentifizierter Kunststoff', 'KST', 'KST', '50', 'KST'),
                ('Mauerwerk', 'MA', 'MA', '3', 'MA'),
                ('Ortbeton', 'OB', 'OB', None, 'OB'),
                ('Polymerbeton', 'PC', 'PC', None, 'PC'),
                ('Polymermodifizierter Zementbeton', 'PCC', 'PCC', None, 'PCC'),
                ('Polyethylen', 'PE', 'PE', '52', 'PE'),
                ('Polyesterharz', 'PH', 'PH', None, 'PH'),
                ('Polyesterharzbeton', 'PHB', 'PHB', None, 'PHB'),
                ('Polypropylen', 'PP', 'PP', '54', 'PP'),
                ('Polyurethanharz', 'PUR', 'PUR', None, None),
                ('Polyvinylchlorid modifiziert', 'PVCM', 'PVCM', None, None),
                ('Polyvinylchlorid hart', 'PVCU', 'PVCU', None, 'PVCU'),
                ('Stahlfaserbeton', 'SFB', 'SFB', None, 'SFB'),
                ('Spannbeton', 'SPB', 'SPB', '12', 'SPB'),
                ('Stahlbeton', 'SB', 'SB', '13', 'SB'),
                ('Stahl', 'ST', 'ST', '21', 'ST'),
                ('Steinzeug', 'STZ', 'STZ', '1', 'STZ'),
                ('Spritzbeton', 'SZB', 'SZB', '14', 'SZB'),
                ('Spritzbeton kunststoffmodifiziert', 'SZBK', 'SZBK', None, None),
                ('Teerfaser', 'TF', 'TF', None, None),
                ('Ungesättigtes Polyesterharz mit Glasfaser', 'UPGF', 'UPGF', None, None),
                ('Ungesättigtes Polyesterharz mit Synthesefaser', 'UPSF', 'UPSF', None, None),
                ('Vinylesterharz mit Synthesefaser', 'VEGF', 'VEGF', None, None),
                ('Vinylesterharz mit Glasfaser', 'VESF', 'VESF', None, None),
                ('Verbundrohr Beton-/StahlbetonKun', 'VBK', 'VBK', None, None),
                ('Verbundrohr Beton-/Stahlbeton Steinzeug', 'VBS', 'VBS', None, None),
                ('Nichtidentifizierter Werkstoff', 'W', 'W', None, None),
                ('Wickelrohr (PEHD)', 'WPE', 'WPE', None, None),
                ('Wickelrohr (PVCU)', 'WPVC', 'WPVC', None, None),
                ('Zementmörtel', 'ZM', 'ZM', None, None),
                ('Ziegelwerk', 'ZG', 'ZG', None, 'ZG'),
            ]

            for bezeichnung, kuerzel, m150, m145, isybau, kommentar in data:
                params.append(
                    {
                        'bezeichnung': bezeichnung,
                        'kuerzel': kuerzel,
                        'isybau': None,
                        'm150': m150,
                        'm145': None,
                        'kommentar': 'QKan-Standard',
                    }
                )

            sql = """INSERT INTO material (bezeichnung, kuerzel, isybau, m150, m145, kommentar)
                        SELECT
                            :bezeichnung, :kuerzel, 
                            :isybau, :m150, :m145, :kommentar
                        WHERE bezeichnung NOT IN (SELECT bezeichnung FROM material)"""
            if not self.db_qkan.sql(sql, "M150 Import Referenzliste Material", params, many=True):
                return False

    def _init_mappers(self) -> None:

        # Entwässerungsarten
        sql = "SELECT m150, bezeichnung FROM entwaesserungsarten"
        subject = "M150 Import entwaesserungsarten"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_entwart)

        # Profilarten
        sql = "SELECT m150, profilnam FROM profile"
        subject = "xml_import profile"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_profile)

        # sql = "SELECT he_nr, bezeichnung FROM pumpentypen"
        # subject = "xml_import pumpentypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_pump)

        sql = "SELECT m150, bezeichnung FROM material"
        subject = "xml_import material"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_material)

        # sql = "SELECT he_nr, bezeichnung FROM auslasstypen"
        # subject = "xml_import auslasstypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_outlet)

        sql = "SELECT m150, bezeichnung FROM simulationsstatus"
        subject = "xml_import simulationsstatus"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_simstatus)

        # sql = "SELECT kuerzel, bezeichnung FROM untersuchrichtung"
        # subject = "xml_import untersuchrichtung"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_untersuchrichtung)

        sql = "SELECT m150, bezeichnung FROM wetter"
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
            blocks = self.xml.findall("KG")                                           # old: KG[KG305='S']

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                #name, knotentyp, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                name = block.findtext("KG001", None)
                knotentyp = 'Normalschacht'
                baujahr = _get_int(block,"KG303", 0)

                schachttyp = 'Schacht'
                schacht_typ = block.findtext("KG305")
                if schacht_typ == "A":
                    continue                                        # Anschlussschacht

                smp = block.find("GO[GO002='B']/GP")
                if smp is None:
                    smp = block.find("GO[GO002='G']/GP")

                if smp is not None:
                    xsch = _get_float(smp, "GP003")
                    if xsch is None:
                        xsch = _get_float(smp, "GP005")

                    ysch = _get_float(smp, "GP004")
                    if ysch is None:
                        ysch = _get_float(smp, "GP006")

                    sohlhoehe = _get_float(smp, "GP007", 0.0)
                else:
                    xsch = None
                    ysch = None
                    sohlhoehe = 0.0

                smpD = block.find("GO[GO002='D']/GP")

                if smpD is None:
                    deckelhoehe = 0.0
                else:
                    deckelhoehe = _get_float(smpD, "GP007", 0.0)

                material = block.findtext("KG304", None)

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=deckelhoehe,
                    baujahr=baujahr,
                    durchm=_get_float(block, "KG309", 0.0),
                    druckdicht=_get_int(block, "KG315", 0),
                    entwart=block.findtext("KG302", None),
                    strasse=block.findtext("KG102", None),
                    knotentyp=knotentyp,
                    schachttyp=schachttyp,
                    material=material,
                    simstatus=block.findtext("KG401", None),
                    kommentar=block.findtext("KG999", "-")
                )

        for schacht in _iter():

            # Entwässerungsarten
            entwart = self.db_qkan.get_from_mapper(
                schacht.entwart,
                self.mapper_entwart,
                'schaechte',
                'entwaesserungsarten',
                'bezeichnung',
                'm150',
                'bemerkung',
                'kuerzel',
            )

            # Druckdichtigkeit
            # if schacht.druckdicht in self.mapper_druckdicht:
            #     druckdicht = self.mapper_druckdicht[schacht.druckdicht]
            # else:
            #     druckdicht = schacht.druckdicht
            #     self.mapper_druckdicht[druckdicht] = druckdicht
            #
            #     sql = """
            #     INSERT INTO druckdicht (kuerzel, bezeichnung)
            #     VALUES (?, ?)"""
            #
            #     params = (entwart, entwart)
            #     if not self.db_qkan.sql(sql, "nicht zugeordnete Werte für Druckdicht", params):
            #         return None

            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                schacht.simstatus,
                self.mapper_simstatus,
                'schacht',
                'simulationsstatus',
                'bezeichnung',
                'm150',
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
                'm150',
                'kommentar',
                'kuerzel',
            )

            # Datensatz einfügen
            params = {'schnam': schacht.schnam, 'xsch': schacht.xsch, 'ysch': schacht.ysch,
                      'sohlhoehe': schacht.sohlhoehe, 'deckelhoehe': schacht.deckelhoehe,
                      'knotentyp': schacht.knotentyp,
                      'durchm': schacht.durchm, 'druckdicht': schacht.druckdicht,
                      'entwart': entwart, 'strasse': schacht.strasse,
                      'baujahr': schacht.baujahr, 'material': material,
                      'simstatus': simstatus, 'kommentar': schacht.kommentar,
                      'schachttyp': schacht.schachttyp, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: schaechte\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    stmt_category='m150-import schaechte',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        self.db_qkan.commit()


    def _schaechte_untersucht(self) -> None:
        def _iter() -> Iterator[Schacht_untersucht]:
            # .//Schacht/../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall("KG/KI/..")

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name = block.findtext("KG001", None)
                strasse = block.findtext("KG102", None)

                smp = block.find("GO/GP")
                if smp is None:
                    fehlermeldung(
                        "Fehler beim XML-Import: Schächte untersucht",
                        f'Keine Geometrie "SMP" für Schacht {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _get_float(smp, "GP003")
                    if xsch is None:
                        xsch = _get_float(smp, "GP005")

                    ysch =  _get_float(smp, "GP004")
                    if ysch is None:
                        ysch =  _get_float(smp, "GP006")
                    sohlhoehe =  _get_float(smp, "GP007", 0.0)

                name = block.findtext("KG001", None)
                baujahr = _get_int(block, "KG303")

                _schacht = block.find("KI")
                if _schacht:
                    untersuchtag = _schacht.findtext("KI104", None)
                    untersucher = _schacht.findtext("KI112", None)
                    wetter = _get_int(_schacht, "KI106")
                    bewertungsart = _schacht.findtext("KI005")
                    bewertungstag = _schacht.findtext("KI204", None)
                    max_ZD = _get_int(_schacht, "KI206", 63)
                    max_ZB = _get_int(_schacht, "KI208", 63)
                    max_ZS = _get_int(_schacht, "KI207", 63)
                else:
                    untersuchtag = ""
                    untersucher = ""
                    wetter = 0
                    bewertungsart = ""
                    bewertungstag = ""
                    datenart = self.datenart
                    max_ZD = 63
                    max_ZB = 63
                    max_ZS = 63
                datenart = self.datenart

                yield Schacht_untersucht(
                    schnam=name,
                    strasse=strasse,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    baujahr=baujahr,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    wetter=wetter,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                    max_ZD=max_ZD,
                    max_ZB=max_ZB,
                    max_ZS=max_ZS,
                )

        for schacht_untersucht in _iter():

            # Wetter
            wetter = self.db_qkan.get_from_mapper(
                schacht_untersucht.wetter,
                self.mapper_wetter,
                'schaechte_untersucht',
                'wetter',
                'bezeichnung',
                'm150',
                'bemerkung',
                'kuerzel',
            )

            # Datensatz einfügen
            params = {'schnam': schacht_untersucht.schnam, 'xsch': schacht_untersucht.xsch,
                      'ysch': schacht_untersucht.ysch,
                      'durchm': schacht_untersucht.durchm, 'kommentar': schacht_untersucht.kommentar,
                      'untersuchtag': schacht_untersucht.untersuchtag, 'untersucher': schacht_untersucht.untersucher,
                      'wetter': wetter,
                      'baujahr': schacht_untersucht.baujahr, 'bewertungsart': schacht_untersucht.bewertungsart,
                      'bewertungstag': schacht_untersucht.bewertungstag,
                      'datenart': schacht_untersucht.datenart, 'max_ZD': schacht_untersucht.max_ZD,
                      'max_ZB': schacht_untersucht.max_ZB, 'max_ZS': schacht_untersucht.max_ZS,
                      'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: schaechte_untersucht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte_untersucht",
                    stmt_category='m150-import schachte_untersucht',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        self.db_qkan.commit()

    def _untersuchdat_schaechte(self) -> None:
        def _iter() -> Iterator[Untersuchdat_schacht]:
            blocks = self.xml.findall("KG/KI/..")

            ordner = self.ordner_bild
            ordner_video = self.ordner_video

            logger.debug(f"Anzahl Untersuchungsdaten Schacht: {len(blocks)}")

            name = ""
            inspektionslaenge = 0.0
            id = 0
            videozaehler = ""
            timecode = ""
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
            ZD = 63
            ZB = 63
            ZS = 63
            xsch= 0.0
            ysch= 0.0

            for block in blocks:

                name = block.findtext("KG001", None)
                untersuchtag = block.findtext("KI/KI104")
                film_dateiname = _untersuchdat_schacht.findtext("KI/KI116", None)

                for _untersuchdat_schacht in block.findall("KI/KZ"):

                    #id = _get_int(_untersuchdat_schacht.findtext("d:Index", "0", self.NS))
                    inspektionslaenge =  _get_float(_untersuchdat_schacht, "KZ001", 0.0)
                    videozaehler = _untersuchdat_schacht.findtext("KZ008")
                    timecode = _untersuchdat_schacht.findtext("KZ008", None)
                    kuerzel = _untersuchdat_schacht.findtext("KZ002", None)
                    charakt1 = _untersuchdat_schacht.findtext("KZ014", None)
                    charakt2 = _untersuchdat_schacht.findtext("KZ015", None)
                    quantnr1 =  _get_float(_untersuchdat_schacht, "KZ003", 0.0)
                    quantnr2 =  _get_float(_untersuchdat_schacht, "KZ004", 0.0)
                    streckenschaden = _untersuchdat_schacht.findtext("KZ005", None)
                    #streckenschaden_lfdnr = _get_int(_untersuchdat_schacht.findtext("KZ005", "0"))
                    pos_von = _get_int(_untersuchdat_schacht, "KZ006", 0)
                    pos_bis = _get_int(_untersuchdat_schacht, "KZ007", 0)
                    vertikale_lage =  _get_float(_untersuchdat_schacht, "KZ001", 0.0)
                    bereich = _untersuchdat_schacht.findtext("KZ013", None)
                    foto_dateiname = _untersuchdat_schacht.findtext("KZ009", None)

                    ZD = _get_int(_untersuchdat_schacht, "KZ206", 63)
                    ZB = _get_int(_untersuchdat_schacht, "KZ208", 63)
                    ZS = _get_int(_untersuchdat_schacht, "KZ207", 63)


                    yield Untersuchdat_schacht(
                    untersuchsch = name,
                    id = id,
                    untersuchtag = untersuchtag,
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
                    film_dateiname = film_dateiname,
                    ordner = ordner,
                    ZD=ZD,
                    ZB=ZB,
                    ZS=ZS,
                    )

        for untersuchdat_schacht in _iter():

            params = {'untersuchsch': untersuchdat_schacht.untersuchsch, 'id': untersuchdat_schacht.id,
                      'untersuchtag': untersuchdat_schacht.untersuchtag,
                      'videozaehler': untersuchdat_schacht.videozaehler, 'timecode': untersuchdat_schacht.timecode,
                      'kuerzel': untersuchdat_schacht.kuerzel, 'charakt1': untersuchdat_schacht.charakt1,
                      'charakt2': untersuchdat_schacht.charakt2, 'quantnr1': untersuchdat_schacht.quantnr1,
                      'quantnr2': untersuchdat_schacht.quantnr2, 'streckenschaden': untersuchdat_schacht.streckenschaden,
                      'streckenschaden_lfdnr': untersuchdat_schacht.streckenschaden_lfdnr, 'pos_von': untersuchdat_schacht.pos_von,
                      'pos_bis': untersuchdat_schacht.pos_bis, 'vertikale_lage': untersuchdat_schacht.vertikale_lage,
                      'inspektionslage': untersuchdat_schacht.inspektionslaenge, 'bereich': untersuchdat_schacht.bereich,
                      'foto_dateiname': untersuchdat_schacht.foto_dateiname, 'ordner': untersuchdat_schacht.ordner,
                      'film_dateiname': untersuchdat_schacht.film_dateiname, 'ordner_video': untersuchdat_schacht.ordner_video,
                      'ZD': untersuchdat_schacht.ZD, 'ZB': untersuchdat_schacht.ZB, 'ZS': untersuchdat_schacht.ZS, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: untersuchdat_schacht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_schacht",
                    stmt_category='m150-import untersuchdat_schacht',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        self.db_qkan.commit()

    def _auslaesse(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall("KG[KG305='A']")

            logger.debug(f"Anzahl Ausläufe: {len(blocks)}")

            for block in blocks:
                #name, knotentyp, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                name = block.findtext("KG001", None)
                baujahr = _get_int(block,"KG303", 0)
                knotentyp = "Auslass"                       # QKan-Logik

                smp = block.find("GO[GO002='G']/GP")
                if smp is None:
                    smp = block.find("GO[GO002='B']/GP")

                if smp is None:
                    fehlermeldung(
                        "Fehler beim XML-Import: Schächte",
                        f'Keine Geometrie "SMP[GO002=\'G\']" oder "SMP[GO002=\'B\']" für Auslass {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch =  _get_float(smp, "GP003")
                    if xsch is None:
                        xsch =  _get_float(smp, "GP005")

                    ysch =  _get_float(smp, "GP004")
                    if ysch is None:
                        ysch =  _get_float(smp, "GP006")

                    sohlhoehe =  _get_float(smp, "GP007", 0.0)

                smpD = block.find("GO[GO002='D']/GP")

                if smpD == None:
                    deckelhoehe = 0.0

                else:
                    deckelhoehe =  _get_float(smpD, "GP007", 0.0)

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=deckelhoehe,
                    baujahr=baujahr,
                    durchm= _get_float(block, "KG309", 0.0),
                    entwart=block.findtext("KG302", None),
                    strasse=block.findtext("KG102", None),
                    knotentyp=knotentyp,
                    simstatus=block.findtext("KG401", 'vorhanden'),
                    kommentar=block.findtext("KG999", "-")
                )

        for auslass in _iter():

            # Entwässerungsarten
            entwart = self.db_qkan.get_from_mapper(
                auslass.entwart,
                self.mapper_entwart,
                'Auslässe',
                'entwaesserungsarten',
                'bezeichnung',
                'm150',
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
                'm150',
                'kommentar',
                'kuerzel',
            )

            # sql = f"""
            # INSERT INTO schaechte (
            #     schnam, xsch, ysch,
            #     sohlhoehe, deckelhoehe, durchm, entwart,
            #     schachttyp, simstatus, kommentar, geop)
            # VALUES (?, ?, ?, ?, ?, ?, ?, 'Auslass', ?, ?, MakePoint(?, ?, ?))
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
            #     ),
            # ):
            #     return None

            params = {'schnam': auslass.schnam, 'xsch': auslass.xsch, 'ysch': auslass.ysch,
                      'sohlhoehe': auslass.sohlhoehe, 'deckelhoehe': auslass.deckelhoehe, 'baujahr': auslass.baujahr,
                      'durchm': auslass.durchm, 'entwart': entwart, 'strasse':auslass.strasse, 'simstatus': simstatus,
                      'kommentar': auslass.kommentar, 'schachttyp': 'Auslass', 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: schaechte\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    stmt_category='m150-import auslaesse',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        self.db_qkan.commit()

    # def _speicher(self) -> None:
    #     def _iter() -> Iterator[Schacht]:
    #         # .//Becken/../../.. nimmt AbwassertechnischeAnlage
    #         blocks = self.xml.findall(
    #             "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage"
    #             "/d:Knoten/d:Bauwerk/d:Becken/../../..",
    #             self.NS,
    #         )
    #
    #         logger.debug(f"Anzahl Becken: {len(blocks)}")
    #
    #         knotentyp = 0
    #         for block in blocks:
    #             name = block.findtext("d:Objektbezeichnung", None, self.NS)
    #
    #             for _schacht in block.findall("d:Knoten", self.NS):
    #                 knotentyp = _get_int(_schacht.findtext("d:KnotenTyp", -1, self.NS))
    #
    #             smp = block.find(
    #                 "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='KOP']",
    #                 self.NS,
    #             )
    #
    #             if not smp:
    #                 fehlermeldung(
    #                     "Fehler beim XML-Import: Speicher",
    #                     f'Keine Geometrie "KOP" für Becken {name}',
    #                 )
    #                 xsch, ysch, sohlhoehe = (0.0,) * 3
    #             else:
    #                 xsch = _get_float(smp.findtext("d:Rechtswert", 0.0, self.NS))
    #                 ysch = _get_float(
    #                     smp.findtext("d:Hochwert", 0.0, self.NS),
    #                 )
    #                 sohlhoehe = _get_float(smp.findtext("d:Punkthoehe", 0.0, self.NS))
    #
    #             yield Schacht(
    #                 schnam=name,
    #                 xsch=xsch,
    #                 ysch=ysch,
    #                 sohlhoehe=sohlhoehe,
    #                 deckelhoehe=float(
    #                     block.findtext(
    #                         "d:Geometrie/d:Geometriedaten/d:Knoten"
    #                         "/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe",
    #                         0.0,
    #                         self.NS,
    #                     )
    #                 ),
    #                 durchm=0.5,
    #                 entwart="",
    #                 knotentyp=knotentyp,
    #                 simstatus=_get_int(block.findtext("d:Status", 0, self.NS)),
    #                 kommentar=block.findtext("d:Kommentar", "-", self.NS),
    #             )
    #
    #     for speicher in _iter():
    #         if speicher.simstatus in self.mapper_simstatus:
    #             simstatus = self.mapper_simstatus[speicher.simstatus]
    #         else:
    #             simstatus = f"{speicher.simstatus}_he"
    #             self.mapper_simstatus[speicher.simstatus] = simstatus
    #             if not self.db_qkan.sql(
    #                 "INSERT INTO simulationsstatus (he_nr, bezeichnung) VALUES (?, ?)",
    #                 "xml_import Speicher [1]",
    #                 parameters=(speicher.simstatus, speicher.simstatus),
    #             ):
    #                 return None
    #
    #         # Geo-Objekte
    #         # geop, geom = geo_smp(speicher)
    #
    #         sql = f"""
    #         INSERT INTO schaechte_data (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart,
    #                 schachttyp, simstatus, kommentar)
    #         VALUES (?, ?, ?, ?, ?, ?, ?, 'Speicher', ?, ?)
    #         """
    #         if not self.db_qkan.sql(
    #             sql,
    #             "xml_import Speicher [2]",
    #             parameters=(
    #                 speicher.schnam,
    #                 speicher.xsch,
    #                 speicher.ysch,
    #                 speicher.sohlhoehe,
    #                 speicher.deckelhoehe,
    #                 speicher.durchm,
    #                 speicher.entwart,
    #                 simstatus,
    #                 speicher.kommentar,
    #             ),
    #         ):
    #             return None
    #
    #     if not self.db_qkan.sql(
    #         "UPDATE schaechte SET (geom, geop) = (geom, geop)",
    #         "xml_import Speicher [2a]",
    #     ):
    #         return None
    #
    #     self.db_qkan.commit()

    def _haltungen(self) -> None:
        def _iter() -> Iterator[Haltung]:
            blocks = self.xml.findall("HG")

            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            for block in blocks:
                if block.findtext("[HG006='L']")is not None:
                    pass
                    #continue
                else:

                    name = block.findtext("HG001")
                    if name is None:
                        name = block.findtext("HG002", "")
                        # if name is None:
                        #     logger.warning("Haltung ohne (Alternativ-) Name HG001/HG002 wird ignoriert!")
                        #     continue

                    baujahr = _get_int(block,"HG303", 0)

                    schoben = block.findtext("HG003", None)
                    schunten = block.findtext("HG004", None)

                    laenge =  _get_float(block, "HG310", 0.0)

                    material = block.findtext("HG304", None)

                    profilauskleidung = block.findtext("HG008", None)
                    innenmaterial = block.findtext("HG009", None)


                    profilnam = block.findtext("HG305", None)
                    hoehe = (
                        _get_float(block, "HG307", 0.0)
                        / 1000
                    )
                    breite = (
                        _get_float(block, "HG306", 0.0)
                        / 1000
                    )

                    sohleoben = 0
                    sohleunten = 0
                    xschob = 0.0
                    yschob = 0.0
                    xschun = 0.0
                    yschun = 0.0

                    if block.findall("GO[GO002='L']") is not None:
                        pass
                        # for _gp in block.findall("GO[GO002='L']/GP[1]"):
                        #
                        #     xschob = _get_float(_gp.findtext("GP003", 0.0))
                        #     if xschob == 0.0:
                        #         xschob = _get_float(_gp.findtext("GP005", 0.0))
                        #     yschob = _get_float(_gp.findtext("GP004", 0.0))
                        #     if yschob == 0.0:
                        #         yschob = _get_float(_gp.findtext("GP006", 0.0))
                        #     sohleoben = _get_float(
                        #         _gp.findtext("GP007", 0.0)
                        #     )

                    if block.findall("GO[GO002='H']") is not None:
                        _gp = block.find("GO[GO002='H']/GP[1]")

                        xschob =  _get_float(_gp, "GP003")
                        if xschob is None:
                            xschob = _get_float(_gp, "GP005")

                        yschob = _get_float(_gp, "GP004")
                        if yschob is None:
                            yschob = _get_float(_gp, "GP006")

                        sohleoben = _get_float(_gp, "GP007", 0.0)

                        _gp = block.find("GO[GO002='H']/GP[last()]")

                        xschun = _get_float(_gp, "GP003")
                        if xschun is None:
                            xschun = _get_float(_gp, "GP005")

                        yschun = _get_float(_gp, "GP004")
                        if yschun is None:
                            yschun = _get_float(_gp, "GP006")

                        sohleunten = _get_float(_gp, "GP007", 0.0)

                yield Haltung(
                    haltnam=name,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    material=material,
                    baujahr=baujahr,
                    sohleoben=sohleoben,
                    sohleunten=sohleunten,
                    profilnam=profilnam,
                    entwart=block.findtext("HG302", None),
                    strasse=block.findtext("HG102", None),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=block.findtext("HG401", 'vorhanden'),
                    kommentar=block.findtext("HG999", "-"),
                    profilauskleidung=profilauskleidung,
                    innenmaterial=innenmaterial,
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
                )

        # def _iter2() -> Iterator[Haltung]:
        #     blocks = self.xml.findall(
        #         "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
        #         "d:HydraulikObjekte/d:HydraulikObjekt/d:Haltung/..",
        #         self.NS,
        #     )
        #     logger.debug(f"Anzahl HydraulikObjekte_Haltungen: {len(blocks)}")
        #
        #     ks = 1.5
        #     laenge = 0.0
        #     for block in blocks:
        #         name = block.findtext("d:Objektbezeichnung", None, self.NS)
        #
        #         # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
        #
        #         #nicht vorhanden in DWA?
        #
        #         # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
        #         for _haltung in block.findall("d:Haltung", self.NS):
        #             cs1 = _haltung.findtext("d:Rauigkeitsansatz", "0", self.NS)
        #             if cs1 == "1":
        #                 ks = _get_float(
        #                     _haltung.findtext("d:RauigkeitsbeiwertKb", 0.0, self.NS)
        #                 )
        #             elif cs1 == "2":
        #                 ks = _get_float(
        #                     _haltung.findtext("d:RauigkeitsbeiwertKst", 0.0, self.NS)
        #                 )
        #             else:
        #                 ks = 0.0
        #                 fehlermeldung(
        #                     "Fehler im XML-Import von HydraulikObjekte_Haltungen",
        #                     f"Ungültiger Wert für Rauigkeitsansatz {cs1} in Haltung {name}",
        #                 )
        #
        #             laenge = _get_float(
        #                 _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
        #             )
        #
        #         yield Haltung(
        #             haltnam=name,
        #             laenge=laenge,
        #             ks=ks,
        #        )


        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung in _iter():

            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                haltung.simstatus,
                self.mapper_simstatus,
                'Haltungen',
                'simulationsstatus',
                'bezeichnung',
                'm150',
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
                'm150',
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
                'm150',
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
                'm150',
                'kommentar',
                'kuerzel',
            )

            params = {'haltnam': haltung.haltnam, 'schoben': haltung.schoben, 'schunten': haltung.schunten, 'hoehe': haltung.hoehe,
                      'breite': haltung.breite, 'laenge': haltung.laenge, 'material': material, 'profilauskleidung': haltung.profilauskleidung,
                      'innenmaterial': haltung.innenmaterial, 'sohleoben': haltung.sohleoben, 'baujahr': haltung.baujahr,
                      'sohleunten': haltung.sohleunten, 'profilnam': profilnam, 'entwart': entwart, 'strasse': haltung.strasse,
                      'ks': haltung.ks, 'simstatus': simstatus, 'kommentar': haltung.kommentar, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: haltungen\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen",
                    stmt_category='m150-import haltungen',
                    mute_logger=False,
                    parameters=params,
            ):
                return

            #TODO: Alternative einfügen, damit ausgewählt werden kann, dass die Geoobjekte anhand der Koordinaten gewählt werden
            #'xschob': haltung.xschob, 'xschun': haltung.xschun, 'yschob': haltung.yschob, 'yschun': haltung.yschun


        self.db_qkan.commit()

    def _haltunggeom(self):
        blocks = self.xml.findall("HG")

        x_start = 0
        y_start = 0
        x_end = 0
        y_end = 0

        list = []
        for block in blocks:
            x_liste=[]
            y_liste=[]
            name = block.findtext("HG001", None)
            if name == None:
                name = block.findtext("HG002", None)
            if name == None:
                continue

            if block.findall("GO[GO002='H']") is not None:
                if len(block.findall("GO[GO002='H']/GP")) > 2:
                    for _gp in block.findall("GO[GO002='H']/GP"):

                        xsch = _get_float(_gp, "GP003")
                        if xsch is None:
                            xsch = _get_float(_gp, "GP005")
                        ysch = _get_float(_gp, "GP004")
                        if ysch is None:
                            ysch = _get_float(_gp, "GP006")

                        x_liste.append(xsch)
                        y_liste.append(ysch)

                    text = str(name), x_liste, y_liste
                    list.append(text)

        list.append('Ende')

        for line in list:
            #line_tokens = line.split(',')
            name = line[0]
            if line != "Ende":
                x_liste = line[1]   # xsch
                x_liste.pop(0)
                x_liste.pop(-1)
                y_liste = line[2]   # ysch
                y_liste.pop(0)
                y_liste.pop(-1)

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

                    self.db_qkan.sql(sql, parameters=(name,))
                    for attr in self.db_qkan.fetchall():
                        x_start, y_start, x_end, y_end = attr

                    # altes haltungsobjekt löschen, da AddPoint ansonsten nicht richtig funktioniert
                    sql = f"""
                                                 UPDATE haltungen SET geom = NULL
                                                 WHERE haltnam = ?
                                                 """

                    if not self.db_qkan.sql(
                            sql, parameters=(name,)
                    ):
                        return False

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
                        return False

                npt+=1
            self.db_qkan.commit()



        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        # for haltung in _iter2():
        #     if not self.db_qkan.sql(
        #         "UPDATE haltungen SET ks = ?, laenge = ? WHERE haltnam = ?",
        #         "xml_import Haltung [4]",
        #         parameters=(haltung.ks, haltung.laenge, haltung.haltnam),
        #     ):
        #         return None
        #
        # self.db_qkan.commit()

    #Haltung_untersucht
    def _haltungen_untersucht(self) -> None:
        def _iter() -> Iterator[Haltung_untersucht]:
            blocks = self.xml.findall("HG/HI/..")
            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            for block in blocks:
                name = block.findtext("HG001", None)
                baujahr = _get_int(block, "HG303", 0)

                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)

                laenge = _get_float(block, "HG314", 0.0)

                hoehe = (
                    _get_float(block, "HG307", 0.0)
                    / 1000
                )
                breite = (
                    _get_float(block, "HG306", 0.0)
                    / 1000
                )

                strasse = block.findtext("HG102", None)
                kommentar = block.findtext("HG999", "-")

                _gp = block.find("GO/GP[1]")
                xschob = _get_float(_gp, "GP003")
                if xschob is None:
                    xschob = _get_float(_gp, "GP005")

                yschob = _get_float(_gp, "GP004")
                if yschob is None:
                    yschob = _get_float(_gp, "GP006")

                deckeloben = _get_float(_gp, "GP007", 0.0)

                _gp = block.find("GO/GP[2]")
                xschun = _get_float(_gp, "GP003")
                if xschun is None:
                    xschun = _get_float(_gp, "GP005")

                yschun = _get_float(_gp, "GP004")
                if yschun is None:
                    yschun = _get_float(_gp, "GP006")

                deckelunten = _get_float(_gp, "GP007", 0.0)

                _haltung = block.find("HI")
                if _haltung:
                    untersuchtag = _haltung.findtext("HI104", None)
                    untersucher = _haltung.findtext("HI112", None)
                    wetter = _get_int(_haltung, "HI106", 0)
                    bewertungsart = _haltung.findtext("HI005")
                    bewertungstag = _haltung.findtext("HI204", None)
                    max_ZD = _get_int(_haltung, "HI206", 63)
                    max_ZB = _get_int(_haltung, "HI208", 63)
                    max_ZS = _get_int(_haltung, "HI207", 63)
                else:
                    untersuchtag = None
                    untersucher = None
                    wetter = 0
                    bewertungsart = None
                    bewertungstag = None
                    max_ZD = 63
                    max_ZB = 63
                    max_ZS = 63
                datenart = self.datenart

                yield Haltung_untersucht(
                    haltnam=name,
                    strasse=strasse,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    kommentar=kommentar,
                    baujahr=baujahr,
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    wetter=wetter,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                    max_ZD=max_ZD,
                    max_ZB=max_ZB,
                    max_ZS=max_ZS,
                )

        for haltung_untersucht in _iter():

            # Wetter
            wetter = self.db_qkan.get_from_mapper(
                haltung_untersucht.wetter,
                self.mapper_wetter,
                'haltung_untersucht',
                'wetter',
                'bezeichnung',
                'm150',
                'bemerkung',
                'kuerzel',
            )

            params = {'haltnam': haltung_untersucht.haltnam, 'schoben': haltung_untersucht.schoben,
                      'schunten': haltung_untersucht.schunten, 'hoehe': haltung_untersucht.hoehe,
                      'breite': haltung_untersucht.breite, 'laenge': haltung_untersucht.laenge,
                      'kommentar': haltung_untersucht.kommentar, 'baujahr': haltung_untersucht.baujahr,
                      'strasse': haltung_untersucht.strasse, 'xschob': haltung_untersucht.xschob,
                      'yschob': haltung_untersucht.yschob, 'xschun': haltung_untersucht.xschun,
                      'yschun': haltung_untersucht.yschun, 'epsg': QKan.config.epsg,
                      'untersuchtag': haltung_untersucht.untersuchtag,
                      'untersucher': haltung_untersucht.untersucher, 'wetter': wetter,
                      'bewertungsart': haltung_untersucht.bewertungsart, 'bewertungstag': haltung_untersucht.bewertungstag,
                      'datenart': haltung_untersucht.datenart, 'max_ZD': haltung_untersucht.max_ZD,
                      'max_ZB': haltung_untersucht.max_ZB, 'max_ZS': haltung_untersucht.max_ZS,
            }

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: haltungen_untersucht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen_untersucht",
                    stmt_category='m150-import haltungen_untersucht',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        self.db_qkan.commit()


    def _untersuchdat_haltung(self) -> None:
        def _iter() -> Iterator[Untersuchdat_haltung]:
            blocks = self.xml.findall(
                "HG/HI/..",
            )

            logger.debug(f"Anzahl Untersuchungsdaten Haltung: {len(blocks)}")

            ordner_bild = self.ordner_bild
            ordner_video = self.ordner_video

            name = ""
            untersuchrichtung = ""
            schoben = ""
            schunten = ""
            id = 0
            untersuchtag = ""
            inspektionslaenge = 0.0
            videozaehler = ""
            station = 0.0
            timecode = ""
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
            streckenschaden_lfdnr=0
            ZD = 63
            ZB = 63
            ZS = 63


            for block in blocks:

                name = block.findtext("HG001", None)
                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)
                _ = block.findtext("HI/HI101", None)
                if _ == "I":
                    untersuchrichtung = "in Fließrichtung"
                elif _ == "G":
                    untersuchrichtung = "gegen Fließrichtung"
                else:
                    logger.warning(f"Untersuchungsdaten Haltung: Fehlerhafter Wert in Feld HI/HI101: {_}")
                    untersuchrichtung = None

                untersuchtag = block.findtext("HI/HI104")

                    #inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("d:Inspektionslaenge", "0.0", self.NS))
                    #if inspektionslaenge == 0.0:
                     #   inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("d:Inspektionsdaten/d:RZustand[d:InspektionsKode='BCE'][d:Charakterisierung1='XP']/d:Station", "0.0", self.NS))


                    #schoben = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenZulauf", None, self.NS)
                    #schunten = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenAblauf", None, self.NS)


                for _untersuchdat in block.findall("HI/HZ"):

                    #id = _get_int(_untersuchdat.findtext("d:Index", "0", self.NS))
                    videozaehler = _untersuchdat.findtext("HZ008")
                    station = _get_float(_untersuchdat, "HZ001", 0.0)
                    timecode = _untersuchdat.findtext("HZ008", None)
                    kuerzel = _untersuchdat.findtext("HZ002", None)
                    charakt1 = _untersuchdat.findtext("HZ014", None)
                    charakt2 = _untersuchdat.findtext("HZ015", None)
                    quantnr1 = _get_float(_untersuchdat, "HZ003", 0.0)
                    quantnr2 = _get_float(_untersuchdat, "HZ004", 0.0)
                    _text = _untersuchdat.findtext("HZ005", None)
                    if _text is not None:
                        streckenschaden = _text[0]
                        if any(i.isdigit() for i in _text) == True:
                            streckenschaden_lfdnr = [int(num) for num in re.findall(r"\d+", _text)][0]
                        else:
                            streckenschaden_lfdnr = 0
                    else:
                        streckenschaden = None
                        streckenschaden_lfdnr = None
                    pos_von = _get_int(_untersuchdat, "HZ006", 0)
                    pos_bis = _get_int(_untersuchdat, "HZ007", 0)
                    foto_dateiname = _untersuchdat.findtext("HZ009", None)
                    ZD = _get_int(_untersuchdat, "HZ206", 63)
                    ZB = _get_int(_untersuchdat, "HZ208", 63)
                    ZS = _get_int(_untersuchdat, "HZ207", 63)


                    yield Untersuchdat_haltung(
                    untersuchhal=name,
                    untersuchrichtung=untersuchrichtung,
                    schoben=schoben,
                    schunten=schunten,
                    id=id,
                    untersuchtag=untersuchtag,
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
                    ZB=ZB,
                    ZS=ZS,
            )

        for untersuchdat_haltung in _iter():

            params = {'untersuchhal': untersuchdat_haltung.untersuchhal, 'untersuchrichtung': untersuchdat_haltung.untersuchrichtung,
                      'schoben': untersuchdat_haltung.schoben, 'schunten': untersuchdat_haltung.schunten,
                      'id': untersuchdat_haltung.id, 'untersuchtag': untersuchdat_haltung.untersuchtag,
                      'videozaehler': untersuchdat_haltung.videozaehler,
                      'inspektionslaenge': untersuchdat_haltung.inspektionslaenge, 'station': untersuchdat_haltung.station,
                      'timecode': untersuchdat_haltung.timecode, 'kuerzel': untersuchdat_haltung.kuerzel,
                      'charakt1': untersuchdat_haltung.charakt1, 'charakt2': untersuchdat_haltung.charakt2,
                      'quantnr1': untersuchdat_haltung.quantnr1, 'quantnr2': untersuchdat_haltung.quantnr2,
                      'streckenschaden': untersuchdat_haltung.streckenschaden, 'streckenschaden_lfdnr': untersuchdat_haltung.streckenschaden_lfdnr,
                      'pos_von': untersuchdat_haltung.pos_von, 'pos_bis': untersuchdat_haltung.pos_bis,
                      'foto_dateiname': untersuchdat_haltung.foto_dateiname, 'film_dateiname': untersuchdat_haltung.film_dateiname,
                      'ordner_bild': untersuchdat_haltung.ordner_bild, 'ordner_video': untersuchdat_haltung.ordner_video,
                       'ZD': untersuchdat_haltung.ZD,
                      'ZB': untersuchdat_haltung.ZB, 'ZS': untersuchdat_haltung.ZS}

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_haltung",
                    stmt_category='m150-import untersuchdat_haltung',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        #for untersuchdat_haltung in _iter2():
        #    if not self.db_qkan.sql(
         #       "UPDATE untersuchdat_haltung SET film_dateiname=?"
          #      " WHERE  untersuchhal= ?",
           #     "xml_import untersuchhal [2a]",
            #    parameters=(untersuchdat_haltung.film_dateiname, untersuchdat_haltung.untersuchhal),
            #):
             #   return None

        self.db_qkan.commit()

        # Textpositionen für Schadenstexte berechnen

        self.db_qkan.setschadenstexte()


    def _anschlussleitungen(self) -> None:
        def _iter() -> Iterator[Anschlussleitung]:
            blocks = self.xml.findall(
                "HG[HG006='L']",
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
                name = block.findtext("HG001", None)

                baujahr = _get_int(block,"HG303", 0)

                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)

                laenge = _get_float(block, "HG310", 0.0)

                material = block.findtext("HG304", None)

                profilnam = block.findtext("HG305", None)
                hoehe = (
                        _get_float(block, "HG307", 0.0)
                        / 1000
                )
                breite = (
                        _get_float(block, "HG306", 0.0)
                        / 1000
                )

                if block.findall("GO[GO002='L']") is not None:

                    _gp = block.find("GO[GO002='L']/GP[1]")

                    xschob = _get_float(_gp, "GP003")
                    if xschob is None:
                        xschob = _get_float(_gp, "GP005")

                    yschob = _get_float(_gp, "GP004")
                    if yschob is None:
                        yschob = _get_float(_gp, "GP006")

                    sohleoben = _get_float(_gp, "GP007", 0.0)

                    _gp = block.find("GO[GO002='L']/GP[last()]")

                    xschun = _get_float(_gp, "GP003")
                    if xschun is None:
                        xschun = _get_float(_gp, "GP005")

                    yschun = _get_float(_gp, "GP004")
                    if yschun is None:
                        yschun = _get_float(_gp, "GP006")

                    sohleunten = _get_float(_gp, "GP007", 0.0)

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
                    entwart=block.findtext("HG302", None),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=block.findtext("HG401", 'vorhanden'),
                    kommentar=block.findtext("HG999", "-"),
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
                )


        # 1. Teil: Hier werden die Stammdaten zu den anschlussleitung in die Datenbank geschrieben
        for anschlussleitung in _iter():

            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                anschlussleitung.simstatus,
                self.mapper_simstatus,
                'anschlussleitung',
                'simulationsstatus',
                'bezeichnung',
                'm150',
                'kommentar',
                'kuerzel',
            )

            # Entwässerungsart
            entwart = self.db_qkan.get_from_mapper(
                anschlussleitung.entwart,
                self.mapper_entwart,
                'Anschlussleitungen',
                'entwaesserungsarten',
                'bezeichnung',
                'm150',
                'bemerkung',
                'kuerzel',
            )

            # Profile
            profilnam = self.db_qkan.get_from_mapper(
                anschlussleitung.profilnam,
                self.mapper_profile,
                'Haltungen',
                'profile',
                'profilnam',
                'm150',
                'kommentar',
                'kuerzel',
            )

            # Material
            material = self.db_qkan.get_from_mapper(
                anschlussleitung.material,
                self.mapper_material,
                'Anschlussleitung',
                'material',
                'bezeichnung',
                'm150',
                'kommentar',
                'kuerzel',
            )

            # sql = f"""
            #     INSERT INTO anschlussleitungen
            #         (leitnam, schoben, schunten,
            #         hoehe, breite, laenge, material, sohleoben, sohleunten, deckeloben, deckelunten,
            #         profilnam, entwart, ks, simstatus, kommentar, xschob, xschun, yschob, yschun, geom)
            #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, MakeLine(MakePoint(?,?,?),MakePoint(?,?,?)))
            #     """
            #
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import anschlussleitung [3]",
            #     parameters=(
            #         anschlussleitung.leitnam,
            #         anschlussleitung.schoben,
            #         anschlussleitung.schunten,
            #         anschlussleitung.hoehe,
            #         anschlussleitung.breite,
            #         anschlussleitung.laenge,
            #         anschlussleitung.material,
            #         anschlussleitung.sohleoben,
            #         anschlussleitung.sohleunten,
            #         anschlussleitung.deckeloben,
            #         anschlussleitung.deckelunten,
            #         anschlussleitung.profilnam,
            #         entwart,
            #         anschlussleitung.ks,
            #         simstatus,
            #         anschlussleitung.kommentar,
            #         anschlussleitung.xschob,
            #         anschlussleitung.xschun,
            #         anschlussleitung.yschob,
            #         anschlussleitung.yschun,
            #         anschlussleitung.xschob, anschlussleitung.yschob, QKan.config.epsg,
            #         anschlussleitung.xschun, anschlussleitung.yschun, QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'leitnam': anschlussleitung.leitnam,
                      'schoben': anschlussleitung.schoben, 'schunten': anschlussleitung.schunten,
                      'hoehe': anschlussleitung.hoehe, 'breite': anschlussleitung.breite,
                      'laenge': anschlussleitung.laenge, 'material': material,
                      'sohleoben': anschlussleitung.sohleoben, 'sohleunten': anschlussleitung.sohleunten,
                      'deckeloben': anschlussleitung.deckeloben, 'deckelunten': anschlussleitung.deckelunten,
                      'profilnam': profilnam, 'entwart': entwart, 'baujahr': anschlussleitung.baujahr,
                      'ks': anschlussleitung.ks, 'simstatus': simstatus,
                      'kommentar': anschlussleitung.kommentar, 'xschob': anschlussleitung.xschob,
                      'xschun': anschlussleitung.xschun, 'yschob': anschlussleitung.yschob,
                      'yschun': anschlussleitung.yschun, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: anschlussleitungen\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen",
                    stmt_category='m150-import anschlussleitung',
                    mute_logger=False,
                    parameters=params,
            ):
                return


        self.db_qkan.commit()

    def _anschlussleitunggeom(self):
        blocks = self.xml.findall("HG")

        x_start = 0
        y_start = 0
        x_end = 0
        y_end = 0

        list = []
        for block in blocks:
            x_liste=[]
            y_liste=[]
            name = block.findtext("HG001", None)
            if name == None:
                name = block.findtext("HG002", None)
            if name == None:
                continue

            if block.findall("GO[GO002='L']") is not None:
                if len(block.findall("GO[GO002='L']/GP")) > 2:
                    for _gp in block.findall("GO[GO002='L']/GP"):

                        xsch = _get_float(_gp, "GP003", 0.0)
                        if xsch is None:
                            xsch = _get_float(_gp, "GP005", 0.0)
                        ysch = _get_float(_gp, "GP004", 0.0)
                        if ysch is None:
                            ysch = _get_float(_gp, "GP006", 0.0)

                        x_liste.append(xsch)
                        y_liste.append(ysch)

                    text = str(name), x_liste, y_liste
                    list.append(text)

        list.append('Ende')

        for line in list:
            #line_tokens = line.split(',')
            name = line[0]
            if line != "Ende":
                x_liste = line[1]   # xsch
                x_liste.pop(0)
                x_liste.pop(-1)
                y_liste = line[2]   # ysch
                y_liste.pop(0)
                y_liste.pop(-1)

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
                            sql, parameters=(name,)
                    ):
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
                        return False

                npt+=1
            self.db_qkan.commit()

    # TODO: Anschluss_untersucht
    def _anschluss_untersucht(self) -> None:
        def _iter() -> Iterator[Haltung_untersucht]:
            blocks = self.xml.findall("HG/HI/..")
            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            for block in blocks:
                name = block.findtext("HG001", None)
                baujahr = _get_int(block,"HG303", 0)

                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)

                laenge = _get_float(block,"HG314", 0.0)

                hoehe = (
                        _get_float(block,"HG307", 0.0)
                        / 1000
                )
                breite = (
                        _get_float(block,"HG306", 0.0)
                        / 1000
                )

                _gp = block.find("GO/GP[1]")
                wert = _gp.findtext("GP003")
                if wert is None:
                    wert = _gp.findtext("GP005")
                xschob = _get_float(wert)

                wert = _gp.findtext("GP004")
                if wert is None:
                    wert = _gp.findtext("GP006")
                yschob = _get_float(wert)
                deckeloben = _get_float(_gp,"GP007", 0.0)

                _gp = block.find("GO/GP[2]")
                wert = _gp.findtext("GP003")
                if wert is None:
                    wert = _gp.findtext("GP005")
                xschun = _get_float(wert)

                wert = _gp.findtext("GP004")
                if wert is None:
                    wert = _gp.findtext("GP006")
                yschun = _get_float(wert)
                deckelunten = _get_float(_gp,"GP007", 0.0)

                yield Haltung_untersucht(
                    haltnam=name,
                    strasse=block.findtext("HG102", None),
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    kommentar=block.findtext("HG999", "-"),
                    baujahr=baujahr,
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
                )

        # def _iter2() -> Iterator[Haltung_untersucht]:
        #     blocks = self.xml.findall(
        #         "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
        #         "d:HydraulikObjekte/d:HydraulikObjekt/d:Haltung/..",
        #         self.NS,
        #     )
        #     logger.debug(f"Anzahl HydraulikObjekte_Haltungen: {len(blocks)}")
        #
        #     laenge = 0.0
        #     for block in blocks:
        #         name = block.findtext("HG001", None)
        #
        #         # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
        #         # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
        #         for _haltung in block.findall("d:Haltung", self.NS):
        #
        #             laenge = _get_float(
        #                 _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
        #             )
        #
        #         yield Haltung_untersucht(
        #             haltnam=name,
        #             laenge=laenge,
        #         )

        def _iter3() -> Iterator[Haltung_untersucht]:
            blocks = self.xml.findall("HG/HI/..")
            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            untersuchtag = ""
            untersucher = ""
            wetter = 0
            bewertungsart = ""
            bewertungstag = ""
            datenart = self.datenart
            max_ZD = 63
            max_ZB = 63
            max_ZS = 63

            for block in blocks:
                name = block.findtext("HG001", None)

                for _haltung in block.findall("HI"):
                    untersuchtag = _haltung.findtext("HI104", None)

                    untersucher = _haltung.findtext("HI112", None)

                    wetter = _get_int(_haltung,"HI106", 0)

                    bewertungsart = _haltung.findtext("HI005")

                    bewertungstag = _haltung.findtext("HI204", None)

                    max_ZD = _get_int(_haltung,"HI206", 63)
                    max_ZB = _get_int(_haltung,"HI208", 63)
                    max_ZS = _get_int(_haltung,"HI207", 63)

                yield Haltung_untersucht(
                    haltnam=name,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    wetter=wetter,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                    max_ZD=max_ZD,
                    max_ZB=max_ZB,
                    max_ZS=max_ZS,
                )

        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung_untersucht in _iter():

            # sql = f"""
            #     INSERT INTO haltungen_untersucht
            #         (haltnam, schoben, schunten,
            #         hoehe, breite, laenge, kommentar,baujahr, strasse, xschob, yschob, xschun, yschun, geom)
            #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, MakeLine(MakePoint(?,?,?),MakePoint(?,?,?)))
            #     """
            #
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import Haltungen_untersucht [1]",
            #     parameters=(
            #         haltung_untersucht.haltnam,
            #         haltung_untersucht.schoben,
            #         haltung_untersucht.schunten,
            #         haltung_untersucht.hoehe,
            #         haltung_untersucht.breite,
            #         haltung_untersucht.laenge,
            #         haltung_untersucht.kommentar,
            #         haltung_untersucht.baujahr,
            #         haltung_untersucht.strasse,
            #         haltung_untersucht.xschob,
            #         haltung_untersucht.yschob,
            #         haltung_untersucht.xschun,
            #         haltung_untersucht.yschun,
            #         haltung_untersucht.xschob, haltung_untersucht.yschob, QKan.config.epsg,
            #         haltung_untersucht.xschun, haltung_untersucht.yschun, QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'haltnam': haltung_untersucht.haltnam, 'schoben': haltung_untersucht.schoben,
                      'schunten': haltung_untersucht.schunten, 'hoehe': haltung_untersucht.hoehe,
                      'breite': haltung_untersucht.breite, 'laenge': haltung_untersucht.laenge,
                      'kommentar': haltung_untersucht.kommentar, 'baujahr': haltung_untersucht.baujahr,
                      'strasse': haltung_untersucht.strasse, 'xschob': haltung_untersucht.xschob,
                      'yschob': haltung_untersucht.yschob, 'xschub': haltung_untersucht.xschun,
                      'yschun': haltung_untersucht.yschun, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: haltungen_untersucht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen_untersucht",
                    stmt_category='m150-import haltungen_untersucht',
                    mute_logger=False,
                    params=params,
            ):
                return

        self.db_qkan.commit()

        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        # for haltung_untersucht in _iter2():
        #     if not self.db_qkan.sql(
        #         "UPDATE haltungen_untersucht SET laenge = ? WHERE haltnam = ?",
        #         "xml_import Haltungen_untersucht [2]",
        #         parameters=( haltung_untersucht.laenge, haltung_untersucht.haltnam),
        #     ):
        #         return None
        #
        # self.db_qkan.commit()

        for haltung_untersucht in _iter3():

            # Wetter
            wetter = self.db_qkan.get_from_mapper(
                haltung_untersucht.wetter,
                self.mapper_wetter,
                'haltung_untersucht',
                'wetter',
                'bezeichnung',
                'm150',
                'bemerkung',
                'kuerzel',
            )

            # if haltung_untersucht.bewertungsart in self.mapper_bewertungsart:
            #     bewertungsart = self.mapper_bewertungsart[haltung_untersucht.bewertungsart]
            # else:
            #     sql = """
            #                INSERT INTO bewertungsart (kuerzel, bezeichnung)
            #                VALUES ('{e}', '{e}')
            #                """.format(
            #         e=haltung_untersucht.bewertungsart
            #     )
            #     self.mapper_bewertungsart[haltung_untersucht.bewertungsart] = haltung_untersucht.bewertungsart
            bewertungsart = haltung_untersucht.bewertungsart
            #
            #     if not self.db_qkan.sql(sql, "xml_import Haltungen_untersucht [4]"):
            #         return None

            if not self.db_qkan.sql(
                    "UPDATE haltungen_untersucht SET untersuchtag=?, untersucher=?, wetter=?, bewertungsart=?,"
                    "bewertungstag=?, datenart=?, max_ZD=?, max_ZB=?, max_ZS=? WHERE haltnam = ?",
                    "xml_import Haltungen_untersucht [5]",
                    parameters=(
                    haltung_untersucht.untersuchtag, haltung_untersucht.untersucher, wetter, bewertungsart,
                    haltung_untersucht.bewertungstag,
                    haltung_untersucht.datenart, haltung_untersucht.max_ZD, haltung_untersucht.max_ZB,
                    haltung_untersucht.max_ZS, haltung_untersucht.haltnam),
            ):
                return None

        self.db_qkan.commit()

    def _untersuchdat_anschluss(self) -> None:
        def _iter() -> Iterator[Untersuchdat_haltung]:
            blocks = self.xml.findall(
                "HG/HI/..",
            )

            logger.debug(f"Anzahl Untersuchungsdaten Haltung: {len(blocks)}")

            ordner_bild = self.ordner_bild
            ordner_video = self.ordner_video

            name = ""
            untersuchrichtung = ""
            schoben = ""
            schunten = ""
            id = 0
            untersuchtag = ""
            inspektionslaenge = 0.0
            videozaehler = ""
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
            streckenschaden_lfdnr = 0
            ZD = 63
            ZB = 63
            ZS = 63

            for block in blocks:

                name = block.findtext("HG001", None)
                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)
                _ = block.findtext("HI/HI101", None)
                if _ == "I":
                    untersuchrichtung = "in Fließrichtung"
                elif _ == "G":
                    untersuchrichtung = "gegen Fließrichtung"
                else:
                    logger.warning(f"Untersuchungsdaten Anschluss: Fehlerhafter Wert in Feld HI/HI101: {_}")
                    untersuchrichtung = None

                untersuchtag = block.findtext("HI/HI104")

                # inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("d:Inspektionslaenge", "0.0", self.NS))
                # if inspektionslaenge == 0.0:
                #   inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("d:Inspektionsdaten/d:RZustand[d:InspektionsKode='BCE'][d:Charakterisierung1='XP']/d:Station", "0.0", self.NS))

                # schoben = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenZulauf", None, self.NS)
                # schunten = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenAblauf", None, self.NS)

                for _untersuchdat in block.findall("HI/HZ"):

                    # id = _get_int(_untersuchdat.findtext("d:Index", "0", self.NS))
                    videozaehler = _untersuchdat.findtext("HZ008")
                    station = _get_float(_untersuchdat,"HZ001", 0.0)
                    # timecode = _get_int(_untersuchdat.findtext("d:Timecode", "0", self.NS))
                    kuerzel = _untersuchdat.findtext("HZ002", None)
                    charakt1 = _untersuchdat.findtext("HZ014", None)
                    charakt2 = _untersuchdat.findtext("HZ015", None)
                    quantnr1 = _get_float(_untersuchdat,"HZ003", 0.0)
                    quantnr2 = _get_float(_untersuchdat,"HZ004", 0.0)
                    _text = _untersuchdat.findtext("HZ005", None)
                    if _text is not None:
                        streckenschaden = _text[0]
                        if any(i.isdigit() for i in _text) == True:
                            streckenschaden_lfdnr = [int(num) for num in re.findall(r"\d+", _text)][0]
                        else:
                            streckenschaden_lfdnr = 0
                    else:
                        streckenschaden = None
                        streckenschaden_lfdnr = None
                    pos_von = _get_int(_untersuchdat,"HZ006", 0)
                    pos_bis = _get_int(_untersuchdat,"HZ007", 0)
                    foto_dateiname = _untersuchdat.findtext("HZ009", None)
                    ZD = _get_int(_untersuchdat,"HZ206", 63)
                    ZB = _get_int(_untersuchdat, "HZ208", 63)
                    ZS = _get_int(_untersuchdat,"HZ207", 63)

                    yield Untersuchdat_haltung(
                        untersuchhal=name,
                        untersuchrichtung=untersuchrichtung,
                        schoben=schoben,
                        schunten=schunten,
                        id=id,
                        untersuchtag=untersuchtag,
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
                        ZB=ZB,
                        ZS=ZS,
                    )

        for untersuchdat_haltung in _iter():

            params = {'untersuchhal': untersuchdat_haltung.untersuchhal, 'untersuchrichtung': untersuchdat_haltung.untersuchrichtung,
                      'schoben': untersuchdat_haltung.schoben, 'schunten': untersuchdat_haltung.schunten,
                      'id': untersuchdat_haltung.id, 'untersuchtag': untersuchdat_haltung.untersuchtag,
                      'videozaehler': untersuchdat_haltung.videozaehler,
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
                      'ordner_video': untersuchdat_haltung.ordner_video,
                      'ZD': untersuchdat_haltung.ZD,
                      'ZB': untersuchdat_haltung.ZB, 'ZS': untersuchdat_haltung.ZS}

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_haltung",
                    stmt_category='m150-import untersuchdat_haltung',
                    mute_logger=False,
                    params=params,
            ):
                return

        # for untersuchdat_haltung in _iter2():
        #    if not self.db_qkan.sql(
        #       "UPDATE untersuchdat_haltung SET film_dateiname=?"
        #      " WHERE  untersuchhal= ?",
        #     "xml_import untersuchhal [2a]",
        #    parameters=(untersuchdat_haltung.film_dateiname, untersuchdat_haltung.untersuchhal),
        # ):
        #   return None

        # Textpositionen für Schadenstexte berechnen

        sql = """SELECT
            uh.pk, hu.pk AS id,
            CASE untersuchrichtung
                WHEN 'gegen Fließrichtung' THEN GLength(hu.geom) - uh.station
                WHEN 'in Fließrichtung'    THEN uh.station
                                           ELSE uh.station END        AS station,
            GLength(hu.geom)                                     AS laenge
            FROM untersuchdat_haltung AS uh
            JOIN haltungen_untersucht AS hu
            ON hu.haltnam = uh.untersuchhal AND
               hu.schoben = uh.schoben AND
               hu.schunten = uh.schunten AND
               hu.untersuchtag = uh.untersuchtag
            WHERE hu.haltnam IS NOT NULL AND
                  hu.untersuchtag IS NOT NULL AND
                  coalesce(laenge, 0) > 0.05 AND
                  uh.station IS NOT NULL AND
                  abs(uh.station) < 10000 AND
                  untersuchrichtung IS NOT NULL
            GROUP BY hu.haltnam, hu.untersuchtag, round(station, 3), uh.kuerzel
            ORDER BY id, station;"""

        if not self.db_qkan.sql(
                sql, "untersuchdat_haltung.station read"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler beim Lesen der Stationen")
        data = self.db_qkan.fetchall()
        logger.debug(f'Anzahl Datensätze in calctextpositions: {len(data)}')
        # logger.debug(f'{data[1]=}')
        # logger.debug(f'{[type(el) for el in data[1]]}')
        self.db_qkan.calctextpositions(data, 0.50, 0.15)

        params = ()
        for ds in data:
            params += ([ds[2], ds[0]],)

        sql = """UPDATE untersuchdat_haltung
            SET stationtext = round(?, 3)
            WHERE pk = ?"""
        if not self.db_qkan.sql(
                sql=sql,
                stmt_category="untersuchdat_haltung.station write",
                parameters=params,
                many=True
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler beim Schreiben der Stationen")

        # Erzeugen der Polylinien für die Schadenstexte
        sql = """
            WITH dist AS (
                SELECT column1 AS d, column2 AS stat, column3 AS tpos 
                FROM (VALUES (0.0000000001, 1.0, 0.0), (1.0, 1.0, 0.0), (1.5, 0.0, 1.0), (4.0, 0.0, 1.0))
            )
            UPDATE untersuchdat_haltung SET geom = (
                SELECT MakeLine(Line_Interpolate_Point(OffsetCurve(hu.geom, di.d), 
                    (
                    CASE untersuchrichtung
                        WHEN 'gegen Fließrichtung' THEN ST_Length(hu.geom) - uh.station
                        WHEN 'in Fließrichtung'    THEN uh.station
                                                   ELSE ST_Length(hu.geom) - uh.station END * di.stat +  
                    uh.stationtext * di.tpos) / ST_Length(hu.geom))) AS textline
                FROM dist AS di, untersuchdat_haltung AS uh
                JOIN haltungen_untersucht AS hu
                ON hu.haltnam = uh.untersuchhal AND
                   hu.schoben = uh.schoben AND
                   hu.schunten = uh.schunten AND
                   hu.untersuchtag = uh.untersuchtag
                WHERE uh.pk = untersuchdat_haltung.pk
                GROUP BY uh.pk)"""
        if not self.db_qkan.sql(
                sql=sql,
                stmt_category="untersuchdat_haltung.geom SET"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler beim Erzeugen der Schadenspolylinien")

        self.db_qkan.commit()

    # def _wehre(self) -> None:
    #     # Hier werden die Hydraulikdaten zu den Wehren in die Datenbank geschrieben.
    #     # Bei Wehren stehen alle wesentlichen Daten im Hydraulikdatenkollektiv, weshalb im Gegensatz zu den
    #     # Haltungsdaten keine Stammdaten verarbeitet werden.
    #
    #     def _iter() -> Iterator[Wehr]:
    #         blocks = self.xml.findall(
    #             "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
    #             "d:HydraulikObjekte/d:HydraulikObjekt/d:Wehr/..",
    #             self.NS,
    #         )
    #         logger.debug(f"Anzahl HydraulikObjekte_Wehre: {len(blocks)}")
    #
    #         schoben, schunten, wehrtyp = ("",) * 3
    #         schwellenhoehe, kammerhoehe, laenge, uebeiwert = (0.0,) * 4
    #         for block in blocks:
    #             # TODO: Does <HydraulikObjekt> even contain multiple <Wehr>?
    #             for _wehr in block.findall("d:Wehr", self.NS):
    #                 schoben = _wehr.findtext("d:SchachtZulauf", None, self.NS)
    #                 schunten = _wehr.findtext("d:SchachtAblauf", None, self.NS)
    #                 wehrtyp = _wehr.findtext("d:WehrTyp", None, self.NS)
    #
    #                 schwellenhoehe = _get_float(
    #                     _wehr.findtext("d:Schwellenhoehe", 0.0, self.NS)
    #                 )
    #                 laenge = _get_float(
    #                     _wehr.findtext("d:LaengeWehrschwelle", 0.0, self.NS)
    #                 )
    #                 kammerhoehe = _get_float(_wehr.findtext("d:Kammerhoehe", 0.0, self.NS))
    #
    #                 # Überfallbeiwert der Wehr Kante (abhängig von Form der Kante)
    #                 uebeiwert = _get_float(
    #                     _wehr.findtext("d:Ueberfallbeiwert", 0.0, self.NS)
    #                 )
    #
    #             yield Wehr(
    #                 wnam=block.findtext("d:Objektbezeichnung", None, self.NS),
    #                 schoben=schoben,
    #                 schunten=schunten,
    #                 wehrtyp=wehrtyp,
    #                 schwellenhoehe=schwellenhoehe,
    #                 kammerhoehe=kammerhoehe,
    #                 laenge=laenge,
    #                 uebeiwert=uebeiwert,
    #             )
    #
    #     for wehr in _iter():
    #         # geom = geo_hydro()
    #
    #         # Bei den Wehren muessen im Gegensatz zu den Haltungen die
    #         # Koordinaten aus den Schachtdaten entnommen werden.
    #         # Dies ist in QKan einfach, da auch Auslaesse und Speicher in der
    #         # Tabelle "schaechte" gespeichert werden.
    #
    #         sql = f"""
    #             INSERT INTO wehre_data
    #                             (wnam, schoben, schunten, wehrtyp, schwellenhoehe, kammerhoehe, laenge, uebeiwert)
    #             SELECT '{wehr.wnam}', '{wehr.schoben}', '{wehr.schunten}', '{wehr.wehrtyp}', {wehr.schwellenhoehe},
    #                     {wehr.kammerhoehe}, {wehr.laenge}, {wehr.uebeiwert}
    #             FROM schaechte AS SCHOB, schaechte AS SCHUN
    #             WHERE SCHOB.schnam = '{wehr.schoben}' AND SCHUN.schnam = '{wehr.schunten}'
    #             """
    #
    #         if not self.db_qkan.sql(sql, "xml_import Wehre [1]"):
    #             return None
    #
    #     if not self.db_qkan.sql(
    #         "UPDATE wehre SET geom = geom", "xml_import Wehre [1a]"
    #     ):
    #         return None
    #
    #     self.db_qkan.commit()

    def _pumpen(self) -> None:

        def _iter2() -> Iterator[Pumpe]:
            # Hydraulik
            blocks = self.xml.findall("KG[KG306='ZPW']") + \
                     self.xml.findall("KG[KG306='RSPW']") + \
                     self.xml.findall("KG[KG306='5']") + \
                     self.xml.findall("KG[KG306='9']")
            logger.debug(f"Anzahl Pumpen: {len(blocks)}")

            pnam=""
            schoben= ""
            schunten = ""
            # pumpentyp= 0
            volanf = 0.0
            volges = 0.0
            sohle = 0.0
            steuersch = ""
            einschalthoehe = 0.0
            ausschalthoehe = 0.0
            simstatus = ""
            kommentar = ""
            xsch = 0.0
            ysch = 0.0

            for block in blocks:
                # pnam, knotentyp, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                pnam = block.findtext("KG001", None)
                knotentyp = 0

                knotentyp = block.findtext("KG305", -1)

                smp = block.find("GO/GP")

                if smp is None:
                    fehlermeldung(
                        "Fehler beim XML-Import: Pumpen",
                        f'Keine Geometrie "SMP" für Pumpe {pnam}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _get_float(smp, "GP003")
                    if xsch is None:
                        xsch = _get_float(smp, "GP005", 0.0)

                    ysch = _get_float(smp, "GP004")
                    if ysch is None:
                        ysch = _get_float(smp, "GP006", 0.0)

                    sohlhoehe = _get_float(smp, "GP007", 0.0)

                yield Pumpe(
                    pnam=pnam,
                    schoben=pnam,
                    schunten=schunten,
                    # pumpentyp=pumpentyp,
                    volanf=volanf,
                    volges=volges,
                    sohle=sohlhoehe,
                    steuersch=steuersch,
                )


        for pumpe in _iter2():
            # geom = geo_hydro()

            # if str(pumpe.pumpentyp) in self.mapper_pump:
            #     pumpentyp = self.mapper_pump[str(pumpe.pumpentyp)]
            # else:
            #     pumpentyp = "{}_he".format(pumpe.pumpentyp)
            #     self.mapper_pump[str(pumpe.pumpentyp)] = pumpentyp
            #     if not self.db_qkan.sql(
            #         "INSERT INTO pumpentypen (bezeichnung) Values (?)",
            #         "xml_import Pumpe [1]",
            #         parameters=(pumpe.pumpentyp,),
            #     ):
            #         break

            # Bei den Pumpen muessen im Gegensatz zu den Haltungen die
            # Koordinaten aus den Schachtdaten entnommen werden.
            # Dies ist in QKan einfach, da auch Auslaesse und Speicher
            # in der Tabelle "schaechte" gespeichert werden.

            # sql = f"""
            #                INSERT INTO haltungen
            #                    (haltnam, schoben, schunten, hoehe, haltungstyp, simstatus, kommentar)
            #                SELECT :pnam, :schoben, :schunten, :sohle, :pumpentyp, :simstatus, :kommentar
            #                FROM schaechte AS SCHOB, schaechte AS SCHUN
            #                WHERE SCHOB.schnam = :schoben AND SCHUN.schnam = :schunten"""

            params = {'haltnam': pumpe.pnam, 'schoben': pumpe.schoben, 'schunten': pumpe.schunten,
                      'sohle': pumpe.sohle,
                      'haltungtyp': 'Pumpe',                        # dient dazu, das Verbindungselement als Pumpe zu klassifizieren
                      'simstatus': pumpe.simstatus, 'kommentar': pumpe.kommentar, 'epsg': QKan.config.epsg}
            # if not self.db_qkan.sql(sql, "xml_import Pumpen [2]", params):
            #     return None

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: haltungen\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                tabnam="haltungen",
                stmt_category='m150-import pumpen',
                mute_logger=False,
                parameters=params,
            ):
                return

        self.db_qkan.commit()

