import sys
import xml.etree.ElementTree as ElementTree
from lxml import etree
from typing import Dict, Iterator, Union
from fnmatch import fnmatch
from qkan import QKan
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis
from qgis.utils import iface
from qkan.utils import get_logger


logger = get_logger("QKan.m145porter.import")


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
    simstatus: str = ""
    kommentar: str = ""
    material: str = ""
    coord: str = ""


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
    untersuchtag: str = ""
    #TODO: videozaehler = Uhrzeit hh:mm
    videozaehler: str = ""
    timecode: int = 0
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
    entwart: str = ""
    material: str = ""
    baujahr: int = 0
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
    coord: str = ""


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
    ordner_bild: str = ""
    ordner_video: str = ""
    richtung: str = ""
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


class Wehr(ClassObject):
    wnam: str = ""
    schoben: str = ""
    schunten: str = ""
    wehrtyp: str = ""
    schwellenhoehe: float
    kammerhoehe: float
    laenge: float
    uebeiwert: float
    simstatus: int = 0
    kommentar: str = ""
    xsch: float = 0.0
    ysch: float = 0.0


class Pumpe(ClassObject):
    pnam: str = ""
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

def fzahl(text: str, n: float = 0.0, default: float = 0.0) -> float:
    """Wandelt einen Text in eine Zahl um. Falls kein Dezimalzeichen
       enthalten ist, werden n Nachkommastellen angenommen.

       text: Text welcher in ein float umgewandelt werden soll.
       n:
    """

    zahl = text.strip()
    if zahl == "":
        return default
    elif "." in zahl:
        try:
            return float(zahl)
        except BaseException as err:
            logger.error("10: {}".format(err))
            return default
    else:
        return float(zahl) / 10.0 ** n


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
            print("_m145porter._import.py._get_int: %s" % sys.exc_info()[1])
        except Exception:
            print("_m145porter._import.py._get_int: %s" % sys.exc_info()[1])
    return default


# noinspection SqlNoDataSourceInspection, SqlResolve
class ImportTask:
    def __init__(self, db_qkan: DBConnection, xml_file: str, richt_choice: str, data_choice: str, ordner_bild: str, ordner_video: str):
        self.db_qkan = db_qkan
        self.ordner_bild = ordner_bild
        self.ordner_video = ordner_video

        #Richutung der Untersuchungsdaten
        self.richt_choice = richt_choice
        if self.richt_choice == "Anzeigen in Fließrichtung rechts der Haltung":
            self.richtung = "fließrichtung"
        if self.richt_choice == "Anzeigen in Untersuchungsrichtung rechts der Haltung":
            self.richtung = "untersuchungsrichtung"

        self.data_coice= data_choice
        if data_choice == "ISYBAU Daten":
            self.datenart = "ISYBAU"
        if data_choice == "DWA M-150 Daten":
            self.datenart = "DWA"

        # nr (str) => description
        self.mapper_entwart: Dict[str, str] = {}
        self.mapper_pump: Dict[str, str] = {}
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

        # Get Namespace
        tree = etree.parse(xml_file)
        x = tree.xpath('namespace-uri(.)')
        self.NS = {"d": x}

    def run(self) -> bool:

        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Import aus M145 läuft. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

        self._reftables()                                   ;self.progress_bar.setValue(5)
        self._init_mappers()
#        if getattr(QKan.config.xml, "import_stamm", True):
        if QKan.config.xml.import_stamm:
            self._schaechte()                               ;self.progress_bar.setValue(10)
            #self._auslaesse()                               ;self.progress_bar.setValue(20)
            #self._speicher()
            self._haltungen()                               ;self.progress_bar.setValue(30)
            self._haltunggeom()                             ;self.progress_bar.setValue(35)
            #self._wehre()
            #self._pumpen()                                  ;self.progress_bar.setValue(40)
        # if getattr(QKan.config.xml, "import_haus", True):
        if QKan.config.xml.import_haus:
            self._anschlussleitungen()                      ;self.progress_bar.setValue(50)
            #self._anschlussleitunggeom()                    ;self.progress_bar.setValue(55)
        # if getattr(QKan.config.xml, "import_zustand", True):
        if QKan.config.xml.import_zustand:
            self._schaechte_untersucht()                    ;self.progress_bar.setValue(65)
            self._untersuchdat_schaechte()                  ;self.progress_bar.setValue(75)
            self._haltungen_untersucht()                    ;self.progress_bar.setValue(85)
            self._untersuchdat_haltung()                    ;self.progress_bar.setValue(95)

        self.progress_bar.setValue(100)
        status_message.setText("Fertig! M145-Import abgeschlossen.")

        return True

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für DWA-Import füllen"""

        #TODO: Referenztabellen mit 145 daten füllen!

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert
        daten = [
            ('Regenwasser', 'R', 'Regenwasser', 1, 2, 3, 'KR', 0, 0),
            ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1,2, 'KS', 0, 0),
            ('Mischwasser', 'M', 'Mischwasser', 0, 0, 1, 'KM', 0, 0),
            ('RW Druckleitung', 'RD', 'Transporthaltung ohne Anschlüsse', 1, 2, None, 'DR', 1, 1),
            ('SW Druckleitung', 'SD', 'Transporthaltung ohne Anschlüsse', 2, 1, None, 'DS', 1, 1),
            ('MW Druckleitung', 'MD', 'Transporthaltung ohne Anschlüsse', 0, 0, None, 'DW', 1, 1),
            ('RW nicht angeschlossen', 'RT', 'Transporthaltung ohne Anschlüsse', 1, 2, None, None, 1, 0),
            ('MW nicht angeschlossen', 'MT', 'Transporthaltung ohne Anschlüsse', 0, 0, None, None, 1, 0),
            ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, 'Ge', None, 0, None),
            ('Grund-/Schichtenwasser', 'GS', 'Grund-/Schichtenwasser', None, None, 'Gr', None, 0, None),
            ('Sonstige', 'SO', 'Sonstige', None, None, 'So', None, 0, None),
            ('Entlastungshaltung', 'E', 'Entlastungshaltung', None, None, 'E', None, 0, None),
            ('Drainagewasser', 'DW', 'Drainagewasser', None, None, 'D', None, 0, None),
            ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None, 0, None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m145, isybau, transport, druckdicht)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "he8_import Referenzliste entwaesserungsarten", daten, many=True):
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
        sql = """INSERT INTO haltungstypen (bezeichnung, bemerkung)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM haltungstypen)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste haltungstypen", daten, many=True):
            return False

        daten = [
            ('Kreis', 1, 1, None),
            ('Rechteck', 2, 3, None),
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
        sql = """INSERT INTO profile (profilnam, he_nr, mu_nr, kp_key)
                    SELECT ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT profilnam FROM profile)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste profile", daten, many=True):
            return False

        daten = [
             ('Offline', 1),
             ('Online Schaltstufen', 2),
             ('Online Kennlinie', 3),
             ('Online Wasserstandsdifferenz', 4),
             ('Ideal', 5),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO pumpentypen (bezeichnung, he_nr)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM pumpentypen)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste pumpentypen", daten, many=True):
            return False

        self.db_qkan.commit()
        return True

    def _init_mappers(self) -> None:

        # Entwässerungsarten
        blocks = self.xml.findall("d:RT1005", self.NS)
        pattern = QKan.config.tools.clipboardattributes.qkan_patterns.get('entwart')
        if pattern and blocks:
            for block in blocks:
                nr = block.findtext("RT0001", None)
                bez = block.findtext("RT0003", None)
                # Falls einer der beiden Einträge fehlt:
                if nr is None or bez is None:
                    continue
                qkan_bez = None
                for x in pattern.keys():
                    for patt in pattern[x]:
                        if fnmatch(bez, patt):
                            qkan_bez = x
                            break
                    if qkan_bez:
                        break
                self.mapper_entwart[nr] = qkan_bez
        else:
            self.mapper_entwart = {
                'M': 'Mischwasser',
                'S': 'Schmutzwasser',
                'R': 'Regenwasser',
                'U': 'Sonstige',
                'E': 'Entlastungshaltung',
                'D': 'Drainagewasser',
                '1': 'Mischwasser',
                '2': 'Schmutzwasser',
                '3': 'Regenwasser',
                '4': 'Rinnen/Gräben',
                '5': 'Grund-/Schichtenwasser',
                '99': 'Sonstige'
            }

        # Planungsstatus
        blocks = self.xml.findall("d:RT1010", self.NS)
        pattern = QKan.config.tools.clipboardattributes.qkan_patterns.get('simstatus')
        if pattern and blocks:
            for block in blocks:
                nr = block.findtext("RT0001", None)
                bez = block.findtext("RT0003", None)
                # Falls einer der beiden Einträge fehlt:
                if nr is None or bez is None:
                    continue
                qkan_bez = None
                for x in pattern.keys():
                    for patt in pattern[x]:
                        if fnmatch(bez, patt):
                            qkan_bez = x
                            break
                    if qkan_bez:
                        break
                self.mapper_simstatus[nr] = qkan_bez
        else:
            self.mapper_simstatus = {
                '1': 'In Betrieb',
                '10': 'Geplant',
                '20': 'Außer Betrieb',
                '21': 'Stillgelegt',
                '22': 'Rückgebaut',
                '99': 'Fiktiv'
            }

        # sql = "SELECT he_nr, bezeichnung FROM pumpentypen"
        # subject = "xml_import pumpentypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_pump)
        #
        # sql = "SELECT he_nr, profilnam FROM profile"
        # subject = "xml_import profile"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_profile)

        # Profilarten nicht über Referenztabelle
        self.mapper_profile = {
            'DN': 'Kreis',                          # DWA-M 145/150, April 2010
            'EI': 'Ei (B:H = 2:3)',                 # DWA-M 145/150, April 2010
            'MA': 'Maul (B:H = 2:1,66)',            # DWA-M 145/150, April 2010
            'RE': 'Rechteck',                       # DWA-M 145/150, April 2010
        }

        # sql = "SELECT he_nr, bezeichnung FROM auslasstypen"
        # subject = "xml_import auslasstypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_outlet)

        sql = "SSELECT m145, FIRST_VALUE(bezeichnung) OVER (PARTITION BY m145 ORDER BY pk) " \
              "FROM simulationsstatus WHERE m145 IS NOT NULL GROUP BY m145"
        subject = "xml_import simulationsstatus"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_simstatus)

        # sql = "SELECT kuerzel, bezeichnung FROM untersuchrichtung"
        # subject = "xml_import untersuchrichtung"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_untersuchrichtung)

        sql = "SSELECT m145, FIRST_VALUE(bezeichnung) OVER (PARTITION BY m145 ORDER BY pk) " \
              "FROM wetter"
        subject = "xml_import wetter WHERE m145 IS NOT NULL GROUP BY m145"
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
            blocks = self.xml.findall("d:BW", self.NS)                                           # old: KG[KG305='S']

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                #name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                name = block.findtext("d:BW0001", None, self.NS)
                id = _get_int(block.findtext("d:BW0002", 0, self.NS))
                #TODO: netztyp in teilgebiet schreiben!
                netz_typ = block.findtext("d:BW0004", 0, self.NS)
                #TODO: Knoten und Schachttyp raussuchen
                knoten_typ = 'Normalschacht'
                schachttyp = 'Schacht'
                baujahr = _get_int(block.findtext("d:BW3502", 0, self.NS))
                #schacht_typ = block.findtext("d:KG305",None, self.NS)

                material = _get_int(block.findtext("d:BW1631", 0, self.NS))

                sohlhoehe = _get_float(block.findtext("d:BW2030", 0.0, self.NS))

                deckelhoehe = _get_float(block.findtext("d:BW2023", 0.0, self.NS))

                coord = block.findtext("d:BW2501/{http://www.opengis.net/gml/3.2}pos", None, self.NS)

                if coord is not None:
                    l=list(coord.split(" "))
                    xsch=float(l[0])
                    ysch=float(l[1])


                yield Schacht(
                    schnam=name,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=deckelhoehe,
                    durchm=_get_float(block.findtext("d:BW1634", None, self.NS)),
                    entwart=block.findtext("d:BW1005", None, self.NS),
                    knotentyp=knoten_typ,
                    schachttyp=schachttyp,
                    simstatus=block.findtext("d:BW1010", None, self.NS),
                    kommentar=block.findtext("d:BW8501", "-", self.NS),
                    material = material,
                    baujahr=baujahr,
                    xsch=xsch,
                    ysch=ysch,
                )


        for schacht in _iter():
            # Entwässerungsarten
            if schacht.entwart in self.mapper_entwart:
                entwart = self.mapper_entwart[schacht.entwart]
            else:
                entwart = schacht.entwart
                sql = "INSERT INTO entwaesserungsarten (bezeichnung, kuerzel, bemerkung)" \
                      "VALUES (?, ?, ?)"
                params = (entwart, entwart, 'unbekannt')
                if not self.db_qkan.sql(sql, "nicht zugeordnete Entwässerungsarten", params):
                    return None

            if schacht.druckdicht in self.mapper_druckdicht:
                druckdicht = self.mapper_druckdicht[schacht.druckdicht]
            else:
                sql = """
                INSERT INTO druckdicht (kuerzel, bezeichnung)
                VALUES ('{e}', '{e}')
                """.format(
                    e=schacht.druckdicht
                )
                self.mapper_druckdicht[schacht.druckdicht] = schacht.druckdicht
                druckdicht = schacht.druckdicht

                if not self.db_qkan.sql(sql, "xml_import Schächte [2]"):
                    return None

            # Simulationsstatus
            if schacht.simstatus in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[schacht.simstatus]
            else:
                sql = """
                INSERT INTO simulationsstatus (he_nr, bezeichnung)
                VALUES ({s}, '{s}')
                """.format(
                    s=schacht.simstatus
                )
                simstatus = f"{schacht.simstatus}"
                self.mapper_simstatus[schacht.simstatus] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Schächte [3]"):
                    return None


            params = {'schnam': schacht.schnam, 'xsch': schacht.xsch, 'ysch': schacht.ysch,
                      'sohlhoehe': schacht.sohlhoehe, 'deckelhoehe': schacht.deckelhoehe, 'knotentyp': schacht.knotentyp,
                      'durchm': schacht.durchm, 'druckdicht': druckdicht, 'entwart': entwart, 'strasse': schacht.strasse, 'baujahr': schacht.baujahr,
                      'simstatus': simstatus, 'kommentar': schacht.kommentar, 'material': schacht.material, 'schachttyp': schacht.schachttyp,
                      'epsg': QKan.config.epsg}

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
            blocks = self.xml.findall("d:/BW/d:IN/..", self.NS)

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name = block.findtext("d:BW0001", None, self.NS)

                for _in in block.findall("d:IN/", self.NS):

                    id = _get_int(_in.findtext("d:IN0001", None, self.NS))


                    strasse = _in.findtext("d:KG102", None, self.NS)

                # smp = block.find("GO/GP")
                # if smp is None:
                #     fehlermeldung(
                #         "Fehler beim XML-Import: Schächte untersucht",
                #         f'Keine Geometrie "SMP" für Schacht {name}',
                #     )
                #     xsch, ysch, sohlhoehe = (0.0,) * 3
                # else:
                #     wert = smp.findtext("GP003")
                #     if wert is None:
                #         wert = smp.findtext("GP005")
                #     xsch = _get_float(wert)
                #
                #     wert = smp.findtext("GP004")
                #     if wert is None:
                #         wert = smp.findtext("GP006")
                #     ysch = _get_float(wert)
                #     sohlhoehe = _get_float(smp.findtext("GP007", 0.0))

                yield Schacht_untersucht(
                    name=name,
                    object= id,
                    strasse=strasse,
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    kommentar=block.findtext("Kommentar", "-"),
                )


        def _iter3() -> Iterator[Schacht_untersucht]:
            blocks = self.xml.findall(
                "d:IN", self.NS
            )
            logger.debug(f"Anzahl Schaechte: {len(blocks)}")

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
                #name = block.findtext("KG001", None)

                #baujahr = _get_int(block.findtext("KG303"))

                untersuchtag = block.findtext("d:IN0002", None, self.NS)

                untersucher = block.findtext("d:IN1001", None, self.NS)

                wetter = _get_int(block.findtext("d:IN0530", self.NS))

                #bewertungsart = block.findtext("KI005")

                bewertungstag = block.findtext("d:IN1000", None, self.NS)

                max_ZD = _get_int(block.findtext("d:IN1002", 63, self.NS))
                max_ZB = _get_int(block.findtext("d:IN1004", 63, self.NS))
                max_ZS = _get_int(block.findtext("d:IN1003", 63, self.NS))

                yield Schacht_untersucht(
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

            # sql = f"""
            # INSERT INTO schaechte_untersucht (schnam, strasse, durchm, kommentar, geop)
            # VALUES (?, ?, ?, ?, MakePoint(?, ?, ?))
            # """
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import Schächte_untersucht [1]",
            #     parameters=(
            #         schacht_untersucht.schnam,
            #         schacht_untersucht.strasse,
            #         schacht_untersucht.durchm,
            #         schacht_untersucht.kommentar,
            #         schacht_untersucht.xsch, schacht_untersucht.ysch, QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'schnam': schacht_untersucht.schnam, 'xsch': schacht_untersucht.xsch, 'ysch': schacht_untersucht.ysch,
                      'durchm': schacht_untersucht.durchm, 'kommentar': schacht_untersucht.kommentar, 'epsg': QKan.config.epsg}

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


        for schacht_untersucht in _iter3():
            if schacht_untersucht.wetter in self.mapper_wetter:
                wetter = self.mapper_wetter[schacht_untersucht.wetter]
            else:
                wetter = schacht_untersucht.wetter
                self.mapper_wetter[schacht_untersucht.wetter] = schacht_untersucht.wetter

                sql = "INSERT INTO wetter (kuerzel, bezeichnung, bemerkung) " \
                      "VALUES (?, ?, ?)"
                params = (wetter, wetter, 'unbekannt')
                if not self.db_qkan.sql(sql, "schacht_untersucht: nicht zugeordnete Werte für wetter", params):
                    return None

            # if schacht_untersucht.bewertungsart in self.mapper_bewertungsart:
            #     bewertungsart = self.mapper_bewertungsart[schacht_untersucht.bewertungsart]
            # else:
            #     sql = """
            #                INSERT INTO bewertungsart (kuerzel, bezeichnung)
            #                VALUES ('{e}', '{e}')
            #                """.format(
            #         e=schacht_untersucht.bewertungsart
            #     )
            #     self.mapper_bewertungsart[schacht_untersucht.bewertungsart] = schacht_untersucht.bewertungsart
            bewertungsart = schacht_untersucht.bewertungsart
            #
            #     if not self.db_qkan.sql(sql, "xml_import Schächte_untersucht [3]"):
            #         return None

            if not self.db_qkan.sql(
                "UPDATE schaechte_untersucht SET untersuchtag=?, untersucher=?, wetter=?, baujahr=?, bewertungsart=?," 
                "bewertungstag=?, datenart=?, max_ZD=?, max_ZB=?, max_ZS=? WHERE schnam = ?",
                "xml_import Schächte_untersucht [4]",
                parameters=(schacht_untersucht.untersuchtag, schacht_untersucht.untersucher, wetter,
                            schacht_untersucht.baujahr, bewertungsart, schacht_untersucht.bewertungstag,
                            schacht_untersucht.datenart, schacht_untersucht.max_ZD, schacht_untersucht.max_ZB,
                            schacht_untersucht.max_ZS, schacht_untersucht.schnam),
            ):
                return None

        self.db_qkan.commit()

    def _untersuchdat_schaechte(self) -> None:
        def _iter() -> Iterator[Untersuchdat_schacht]:
            blocks = self.xml.findall("d:BW/d:IN/d:FS/..", self.NS)

            ordner = self.ordner_bild
            ordner_video = self.ordner_video

            logger.debug(f"Anzahl Untersuchungsdaten Schacht: {len(blocks)}")

            name = ""
            inspektionslaenge = 0.0
            id = 0
            videozaehler = ""
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
            ZD = 63
            ZB = 63
            ZS = 63
            xsch= 0.0
            ysch= 0.0

            for block in blocks:

                #name = block.findtext("KG001", None)

                untersuchtag = block.findtext("d:IN0002", None, self.NS)
                inspektionslaenge = _get_float(block.findtext("d:IN0535", 0.0, self.NS))

                for _untersuchdat_schacht in block.findall("FS"):

                    id = _get_int(_untersuchdat_schacht.findtext("d:FS0001", "0", self.NS))
                    videozaehler = _untersuchdat_schacht.findtext("d:FS0016", None, self.NS)
                    #timecode = _get_int(_untersuchdat_schacht.findtext("d:Timecode", "0", self.NS))
                    kuerzel = _untersuchdat_schacht.findtext("d:FS0003", None, self.NS)
                    charakt1 = _untersuchdat_schacht.findtext("d:FS0004", None, self.NS)
                    charakt2 = _untersuchdat_schacht.findtext("d:FS0005", None, self.NS)
                    quantnr1 = _get_float(_untersuchdat_schacht.findtext("d:FS0007", 0.0, self.NS))
                    quantnr2 = _get_float(_untersuchdat_schacht.findtext("d:FS0008", 0.0, self.NS))
                    streckenschaden = _untersuchdat_schacht.findtext("d:FS0014", None, self.NS)
                    streckenschaden_lfdnr = _get_int(_untersuchdat_schacht.findtext("d:FS0015", "0", self.NS))
                    pos_von = _get_int(_untersuchdat_schacht.findtext("d:FS0009", 0, self.NS))
                    pos_bis = _get_int(_untersuchdat_schacht.findtext("d:FS0010", 0, self.NS))
                    #vertikale_lage = _get_float(_untersuchdat_schacht.findtext("KZ001", 0.0))
                    bereich = _untersuchdat_schacht.findtext("d:FS0012", None, self.NS)
                    foto_dateiname = _untersuchdat_schacht.findtext("d:FO/FO0001", None, self.NS)
                    film_datainame = _untersuchdat_schacht.findtext("d:FI/FI0001", None, self.NS)

                    ZD = _get_int(_untersuchdat_schacht.findtext("d:FS1002", 63, self.NS))
                    ZB = _get_int(_untersuchdat_schacht.findtext("d:FS1004", 63, self.NS))
                    ZS = _get_int(_untersuchdat_schacht.findtext("d:FS1003", 63, self.NS))


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
                    inspektionslaenge = inspektionslaenge,
                    bereich = bereich,
                    foto_dateiname = foto_dateiname,
                    ordner = ordner,
                    film_datainame=film_datainame,
                    ordner_video = ordner_video,
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

    # def _auslaesse(self) -> None:
    #     def _iter() -> Iterator[Schacht]:
    #         # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage
    #         blocks = self.xml.findall("KG[KG305='A']")
    #
    #         logger.debug(f"Anzahl Ausläufe: {len(blocks)}")
    #
    #         for block in blocks:
    #             #name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)
    #
    #             name = block.findtext("KG001", None)
    #             knoten_typ = 0
    #
    #             knoten_typ = block.findtext("KG305", -1)
    #
    #             smp = block.find("GO[GO002='G']/GP")
    #             if smp is None:
    #                 smp = block.find("GO[GO002='B']/GP")
    #
    #             if smp is None:
    #                 fehlermeldung(
    #                     "Fehler beim XML-Import: Schächte",
    #                     f'Keine Geometrie "SMP[GO002=\'G\']" oder "SMP[GO002=\'B\']" für Auslass {name}',
    #                 )
    #                 xsch, ysch, sohlhoehe = (0.0,) * 3
    #             else:
    #                 xsch = _get_float(smp.findtext("GP003", 0.0))
    #                 if xsch == 0.0:
    #                     xsch = _get_float(smp.findtext("GP005", 0.0))
    #                 else:
    #                     pass
    #                 ysch = _get_float(smp.findtext("GP004", 0.0))
    #                 if ysch == 0.0:
    #                     ysch = _get_float(smp.findtext("GP006", 0.0))
    #                 else:
    #                     pass
    #                 sohlhoehe = _get_float(smp.findtext("GP007", 0.0))
    #
    #             smpD = block.find("GO[GO002='D']/GP")
    #
    #             if smpD == None:
    #                 deckelhoehe = 0.0
    #
    #             else:
    #                 deckelhoehe = _get_float(smpD.findtext("GP007", 0.0))
    #
    #
    #             yield Schacht(
    #                 schnam=name,
    #                 xsch=xsch,
    #                 ysch=ysch,
    #                 sohlhoehe=sohlhoehe,
    #                 deckelhoehe=deckelhoehe,
    #                 durchm=_get_float(block.findtext("KG309", 0.0)),
    #                 entwart=block.findtext("KG302", None),
    #                 strasse=block.findtext("KG102", None),
    #                 knotentyp=knoten_typ,
    #                 simstatus=_get_int(block.findtext("KG407", None)),
    #                 kommentar=block.findtext("KG999", "-")
    #             )
    #
    #     for auslass in _iter():
    #         # Simstatus-Nr aus HE ersetzten
    #         if auslass.simstatus in self.mapper_simstatus:
    #             simstatus = self.mapper_simstatus[auslass.simstatus]
    #         else:
    #             sql = """
    #             INSERT INTO simulationsstatus (he_nr, bezeichnung)
    #             VALUES ({s}, '{s}')
    #             """.format(
    #                 s=auslass.simstatus
    #             )
    #             simstatus = f"{auslass.simstatus}"
    #             self.mapper_simstatus[auslass.simstatus] = simstatus
    #             if not self.db_qkan.sql(sql, "xml_import Auslässe [1]"):
    #                 return None
    #
    #         # sql = f"""
    #         # INSERT INTO schaechte (
    #         #     schnam, xsch, ysch,
    #         #     sohlhoehe, deckelhoehe, durchm, entwart,
    #         #     schachttyp, simstatus, kommentar, geop)
    #         # VALUES (?, ?, ?, ?, ?, ?, ?, 'Auslass', ?, ?, MakePoint(?, ?, ?))
    #         # """
    #         # if not self.db_qkan.sql(
    #         #     sql,
    #         #     "xml_import Auslässe [2]",
    #         #     parameters=(
    #         #         auslass.schnam,
    #         #         auslass.xsch,
    #         #         auslass.ysch,
    #         #         auslass.sohlhoehe,
    #         #         auslass.deckelhoehe,
    #         #         auslass.durchm,
    #         #         auslass.entwart,
    #         #         simstatus,
    #         #         auslass.kommentar,
    #         #         auslass.xsch, auslass.ysch, QKan.config.epsg,
    #         #     ),
    #         # ):
    #         #     return None
    #
    #         params = {'schnam': auslass.schnam, 'xsch': auslass.xsch, 'ysch': auslass.ysch,
    #                   'sohlhoehe': auslass.sohlhoehe, 'deckelhoehe': auslass.deckelhoehe,
    #                   'durchm': auslass.durchm, 'entwart': auslass.entwart, 'strasse':auslass.strasse, 'simstatus': simstatus,
    #                   'kommentar': auslass.kommentar, 'schachttyp': 'Auslass', 'epsg': QKan.config.epsg}
    #
    #         # logger.debug(f'm150porter.import - insertdata:\ntabnam: schaechte\n'
    #         #              f'params: {params}')
    #
    #         if not self.db_qkan.insertdata(
    #                 tabnam="schaechte",
    #                 stmt_category='m150-import auslaesse',
    #                 mute_logger=False,
    #                 parameters=params,
    #         ):
    #             return
    #
    #     self.db_qkan.commit()

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
    #         knoten_typ = 0
    #         for block in blocks:
    #             name = block.findtext("d:Objektbezeichnung", None, self.NS)
    #
    #             for _schacht in block.findall("d:Knoten", self.NS):
    #                 knoten_typ = _get_int(_schacht.findtext("d:KnotenTyp", -1, self.NS))
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
    #                 knotentyp=knoten_typ,
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
            blocks = self.xml.findall("d:HG", self.NS)

            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            schoben, schunten, profilnam = ("",) * 3
            (
                sohleoben,
                sohleunten,
                laenge,
                hoehe,
                breite,
            ) = (0.0,) * 5

            for block in blocks:
                # if block.findtext("[HG006='L']")is not None:
                #     pass
                #     #continue
                # else:

                name = block.findtext("d:HG0001", None, self.NS)
                #objekt_id = block.findtext("d:HG0002", None, self.NS)

                schoben = block.findtext("d:HG0030", None, self.NS)
                schunten = block.findtext("d:HG0032", None, self.NS)

                sohleoben = _get_float(block.findtext("d:HG2024", 0.0, self.NS))
                sohleunten = _get_float(block.findtext("d:HG2030", 0.0, self.NS))

                laenge = _get_float(block.findtext("d:HG2002", 0.0, self.NS))

                material = block.findtext("d:HG3501", None, self.NS)
                baujahr = _get_int(block.findtext("d:HG3502", None, self.NS))

                profilauskleidung = block.findtext("d:HG3505", None, self.NS)
                innenmaterial = block.findtext("d:HG3506", None, self.NS)


                profilnam = block.findtext("d:HG2005", None, self.NS)
                hoehe = (
                    _get_float(block.findtext("d:HG2008", 0.0, self.NS))

                )
                breite = (
                    _get_float(block.findtext("d:HG2007", 0.0, self.NS))

                )



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
                    entwart=block.findtext("d:HG1005", None, self.NS),
                    strasse=block.findtext("d:HG0510", None, self.NS),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=block.findtext("d:HG1010", None, self.NS),
                    kommentar=block.findtext("d:HG8501", "-", self.NS),
                    profilauskleidung=profilauskleidung,
                    innenmaterial=innenmaterial,
                )

        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung in _iter():
            if haltung.simstatus in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[haltung.simstatus]
            else:
                simstatus = f"{haltung.simstatus}"
                self.mapper_simstatus[haltung.simstatus] = simstatus
                if not self.db_qkan.sql(
                    "INSERT INTO simulationsstatus (he_nr, bezeichnung) VALUES (?, ?)",
                    "xml_import Haltungen [1]",
                    parameters=(haltung.simstatus, haltung.simstatus),
                ):
                    return None

            if haltung.entwart in self.mapper_entwart:
                entwart = self.mapper_entwart[haltung.entwart]
            else:
                bez = 'NULL'
                entwaesserung = {'Mischwasser': ['Mi*'],
                                 'Regenwasser': ['Re*'],
                                 'Schmutzwasser': ['Sc*']}
                for x in entwaesserung.keys():
                    for patt in entwaesserung[x]:
                        if fnmatch(str(haltung.entwart), patt):
                            key = [i for i, x in entwaesserung.items() if str(patt) in x][0]
                            bez = key

                sql = """
                               INSERT INTO entwaesserungsarten (kuerzel, bezeichnung)
                               VALUES ('{e}', '{f}')
                               """.format(
                    e=bez, f=haltung.entwart
                )

                self.mapper_entwart[haltung.entwart] = haltung.entwart
                entwart = haltung.entwart

                if not self.db_qkan.sql(sql, "xml_import Haltung [1]"):
                    return None


            params = {'haltnam': haltung.haltnam, 'schoben': haltung.schoben, 'schunten': haltung.schunten, 'hoehe': haltung.hoehe,
                      'breite': haltung.breite, 'laenge': haltung.laenge, 'material': haltung.material, 'profilauskleidung': haltung.profilauskleidung,
                      'innenmaterial': haltung.innenmaterial, 'sohleoben': haltung.sohleoben, 'baujahr': haltung.baujahr,
                      'sohleunten': haltung.sohleunten, 'profilnam': haltung.profilnam, 'entwart': entwart, 'strasse': haltung.strasse,
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

            # sql = f"""
            #                         UPDATE haltung SET geom = GeomFromGML(?)
            #                         WHERE haltnam = ?
            #                      """
            #
            # paralist = [haltung.coord, haltung.haltnam]
            #
            # if not self.db_qkan.sql(
            #         sql, parameters=paralist
            # ):
            #     return False

            #'xschob': haltung.xschob, 'xschun': haltung.xschun, 'yschob': haltung.yschob, 'yschun': haltung.yschun


        self.db_qkan.commit()

    def _haltunggeom(self):
        blocks = self.xml.findall(
            "d:HG",
            self.NS,
        )

        x_start = 0
        y_start = 0
        x_end = 0
        y_end = 0

        list = []
        for block in blocks:
            x_liste = []
            y_liste = []

            name = block.findtext("d:HG0001", None, self.NS)

            # alle Koordinaten raus suchen für die Haltungen und diese in Liste schreiben!
            gp = block.findall("d:HG2501{http://www.opengis.net/gml/3.2}pos", self.NS)

            for i in block.findall("d:HG2501", self.NS):

                iface.messageBar().pushMessage("Error",
                                               str(i),
                                               level=Qgis.Critical)

                #coord = i.find('d:{http://www.opengis.net/gml/3.2}pos')

                #coord = i.text
                coord = i.find('gml:pos', namespaces={'gml': 'http://www.opengis.net/gml/3.2'})


                x_liste = []
                y_liste = []
                if coord is not None:
                    iface.messageBar().pushMessage("Error",
                                                   str(coord),
                                                   level=Qgis.Critical)

                    l = list(coord.text.split(" "))
                    xschob = float(l[0])
                    yschob = float(l[1])
                    x_liste.append(xschob)
                    y_liste.append(yschob)

                    text = str(name), x_liste, y_liste
                    list.append(text)

        list.append('Ende')

        iface.messageBar().pushMessage("Error",
                                       str(list),
                                       level=Qgis.Critical)

        for line in list:
            #line_tokens = line.split(',')
            x_liste = line[1]
            x_start = x_liste[0]
            y_liste = line[2]
            y_start = y_liste[0]
            name = line[0]
            if line != "Ende":
                x_liste = line[1]   # xsch
                x_liste.pop(0)
                #x_liste.pop(-1)
                y_liste = line[2]   # ysch
                y_liste.pop(0)
                #y_liste.pop(-1)


            # if line == "Ende":
            #     x_liste = line[1]
            #     x_end = x_liste[0]
            #     y_liste = line[2]
            #     y_end = y_liste[0]
            npt=1

            for xsch, ysch in zip(x_liste, y_liste):

                sql = f"""
                                UPDATE haltungen SET geom = MakeLine(MakePoint(?, ?, ?), MakePoint(?, ?, ?)),
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
            blocks = self.xml.findall("d:HG/d:IN", self.NS)
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

            # name = block.findtext("HG0001", None)

            for block in blocks:
                #name = block.findtext("HG0001", None)
                id = block.findtext("d:IN0001", None, self.NS)

                untersuchtag = _get_int(block.findtext("d:IN0002", None, self.NS))

                #strasse = block.findtext("HG102", None)

                untersucher = block.findtext("d:IN1001", None, self.NS)

                wetter = _get_int(block.findtext("d:IN0530", 0, self.NS))

                #bewertungsart = blocks.findtext("HI005")

                bewertungstag = block.findtext("d:IN1000", None, self.NS)

                max_ZD = _get_int(block.findtext("d:IN1002", 63, self.NS))
                max_ZB = _get_int(block.findtext("d:IN1003", 63, self.NS))
                max_ZS = _get_int(block.findtext("d:IN1004", 63, self.NS))

                laenge = _get_float(block.findtext("d:IN0535", 0.0, self.NS))

                yield Haltung_untersucht(
                    id=id,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    kommentar=block.findtext("d:IN0534", "-", self.NS),
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

            if haltung_untersucht.wetter in self.mapper_wetter:
                wetter = self.mapper_wetter[haltung_untersucht.wetter]
            else:
                wetter = haltung_untersucht.wetter
                self.mapper_wetter[haltung_untersucht.wetter] = haltung_untersucht.wetter

                sql = "INSERT INTO wetter (kuerzel, bezeichnung, bemerkung) " \
                      "VALUES (?, ?, ?)"
                params = (wetter, wetter, 'unbekannt')
                if not self.db_qkan.sql(sql, "haltung_untersucht: nicht zugeordnete Werte für wetter", params):
                    return None

            params = {'haltnam': haltung_untersucht.haltnam, 'schoben': haltung_untersucht.schoben,
                      'schunten': haltung_untersucht.schunten, 'hoehe': haltung_untersucht.hoehe,
                      'breite': haltung_untersucht.breite, 'laenge': haltung_untersucht.laenge,
                      'kommentar': haltung_untersucht.kommentar, 'baujahr': haltung_untersucht.baujahr,
                      'strasse': haltung_untersucht.strasse, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: haltungen_untersucht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen_untersucht",
                    stmt_category='m145-import haltungen_untersucht',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        self.db_qkan.commit()

    def _untersuchdat_haltung(self) -> None:
        def _iter() -> Iterator[Untersuchdat_haltung]:
            blocks = self.xml.findall(
                "d:HG/d:IN/d:FS/..", self.NS
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
            richtung = self.richtung
            streckenschaden_lfdnr=0
            ZD = 63
            ZB = 63
            ZS = 63


            for block in blocks:

                id = block.findtext("d:IN0001", None, self.NS)

                _ = block.findtext("d:IN0005", None, self.NS)
                if _ == "1":
                    untersuchrichtung = "in Fließrichtung"
                elif _ == "2":
                    untersuchrichtung = "gegen Fließrichtung"
                else:
                    logger.warning(f"Untersuchungsdaten Haltung: Fehlerhafter Wert in Feld IN0005: {_}")
                    untersuchrichtung = None

                untersuchtag = block.findtext("d:IN0002", None, self.NS)

                for _untersuchdat in block.findall("d:FS", self.NS):

                    id = _get_int(_untersuchdat.findtext("d:FS0001", "0", self.NS))
                    videozaehler = _untersuchdat.findtext("d:FS0016", None, self.NS)
                    station = _get_float(_untersuchdat.findtext("d:FS0002", 0.0, self.NS))
                    #timecode = _get_int(_untersuchdat.findtext("d:Timecode", "0", self.NS))
                    kuerzel = _untersuchdat.findtext("d:FS0003", None, self.NS)
                    charakt1 = _untersuchdat.findtext("d:FS0004", None, self.NS)
                    charakt2 = _untersuchdat.findtext("d:FS0005", None, self.NS)
                    quantnr1 = _get_float(_untersuchdat.findtext("d:FS0007", 0.0, self.NS))
                    quantnr2 = _get_float(_untersuchdat.findtext("d:FS0008", 0.0, self.NS))
                    streckenschaden = _untersuchdat.findtext("FS0014", None, self.NS)
                    streckenschaden_lfdnr = _get_float(_untersuchdat.findtext("d:FS0015", 0.0, self.NS))

                    pos_von = _get_int(_untersuchdat.findtext("d:FS0009", 0, self.NS))
                    pos_bis = _get_int(_untersuchdat.findtext("d:FS0010", 0, self.NS))
                    foto_dateiname = _untersuchdat.findtext("d:FS0017", None, self.NS)
                    ZD = _get_int(_untersuchdat.findtext("d:FS1002", 63, self.NS))
                    ZB = _get_int(_untersuchdat.findtext("d:FS1003", 63, self.NS))
                    ZS = _get_int(_untersuchdat.findtext("d:FS1004", 63, self.NS))


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
                    richtung=richtung,
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
                      'richtung': untersuchdat_haltung.richtung, 'ZD': untersuchdat_haltung.ZD,
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

        # Textpositionen für Schadenstexte berechnen

        sql = """SELECT
            uh.pk, uh.untersuchhal || '-' || uh.untersuchtag AS id,
            CASE untersuchrichtung
                WHEN 'gegen Fließrichtung' THEN GLength(hu.geom) - uh.station
                WHEN 'in Fließrichtung'    THEN uh.station
                                           ELSE NULL END        AS station,
            GLength(hu.geom)                                     AS laenge
            FROM untersuchdat_haltung AS uh
            JOIN haltungen_untersucht AS hu ON hu.haltnam = uh.untersuchhal AND hu.untersuchtag = uh.untersuchtag
            WHERE uh.untersuchhal IS NOT NULL AND uh.untersuchtag IS NOT NULL AND coalesce(laenge, 0) > 0.05
            GROUP BY uh.untersuchhal, uh.untersuchtag, station, uh.kuerzel
            ORDER BY id, station;"""

        if not self.db_qkan.sql(
            sql, "untersuchdat_haltung.station read"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler beim Lesen der Stationen")
        data = self.db_qkan.fetchall()
        logger.debug(f'Anzahl Datensätze in calctextpositions: {len(data)}')
        # logger.debug(f'{data[1]=}')
        # logger.debug(f'{[type(el) for el in data[1]]}')
        #self.db_qkan.calctextpositions(data, 0.5, 0.25)

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
                SELECT MakeLine(Line_Interpolate_Point(OffsetCurve(ha.geom, di.d), 
                    (
                    CASE untersuchrichtung
                        WHEN 'gegen Fließrichtung' THEN ST_Length(ha.geom) - uh.station
                        WHEN 'in Fließrichtung'    THEN uh.station
                                                   ELSE ST_Length(ha.geom) - uh.station END * di.stat +  
                    uh.stationtext * di.tpos) / ST_Length(ha.geom))) AS textline
                FROM dist AS di, untersuchdat_haltung AS uh
                JOIN haltungen_untersucht AS ha ON ha.haltnam = uh.untersuchhal
                WHERE uh.pk = untersuchdat_haltung.pk
                GROUP BY uh.pk)"""
        if not self.db_qkan.sql(
                sql=sql,
                stmt_category="untersuchdat_haltung.geom SET"
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler beim Erzeugen der Schadenspolylinien")

        self.db_qkan.commit()


    def _anschlussleitungen(self) -> None:
        def _iter() -> Iterator[Anschlussleitung]:
            blocks = self.xml.findall(
                "d:AN", self.NS
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

                #TODO: Laenge, Sohlhoehe und Anschlusspunkt Adresse ergänzen

                name = block.findtext("d:AN0001", None, self.NS)
                #objekt_id = _get_int(block.findtext("d:AN0002", None, self.NS))
                haltnam = block.findtext("d:AN0035", None, self.NS)

                schoben = block.findtext("d:AN0036", None, self.NS)
                #schunten = block.findtext("HG004", None)

                baujahr = _get_int(block.findtext("d:AN3502", 0))

                #laenge = _get_float(block.findtext("HG310", 0.0))

                #material = block.findtext("HG304", None)

                profilnam = block.findtext("d:AN2005", None, self.NS)
                hoehe = (
                        _get_float(block.findtext("d:AN2008", 0.0, self.NS))

                )
                breite = (
                        _get_float(block.findtext("d:AN2007", 0.0, self.NS))

                )

                sohleoben = _get_float(block.findtext("GP007", 0.0, self.NS))
                sohleunten = _get_float(block.findtext("GP007", 0.0, self.NS))



                yield Anschlussleitung(
                    leitnam=name,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    baujahr=baujahr,
                    sohleoben=sohleoben,
                    sohleunten=sohleunten,
                    deckeloben=deckeloben,
                    deckelunten=deckelunten,
                    profilnam=profilnam,
                    entwart=block.findtext("HG302", None),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=block.findtext("HG407", None),
                    kommentar=block.findtext("HG999", "-"),
                )


        # 1. Teil: Hier werden die Stammdaten zu den anschlussleitung in die Datenbank geschrieben
        for anschlussleitung in _iter():
            if anschlussleitung.simstatus in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[anschlussleitung.simstatus]
            else:
                simstatus = f"{anschlussleitung.simstatus}"
                self.mapper_simstatus[anschlussleitung.simstatus] = simstatus
                if not self.db_qkan.sql(
                    "INSERT INTO simulationsstatus (he_nr, bezeichnung) VALUES (?, ?)",
                    "xml_import anschlussleitung [1]",
                    parameters=(anschlussleitung.simstatus, anschlussleitung.simstatus),
                ):
                    return None

            if anschlussleitung.entwart in self.mapper_entwart:
                entwart = self.mapper_entwart[anschlussleitung.entwart]
            else:
                self.mapper_entwart[anschlussleitung.entwart] = anschlussleitung.entwart
                entwart = anschlussleitung.entwart

                if not self.db_qkan.sql(
                    "INSERT INTO entwaesserungsarten (kuerzel, bezeichnung) VALUES (?, ?)",
                    "xml_import anschlussleitung [2]",
                    parameters=(anschlussleitung.entwart, anschlussleitung.entwart),
                ):
                    return None

            params = {'leitnam': anschlussleitung.leitnam,
                      'schoben': anschlussleitung.schoben, 'schunten': anschlussleitung.schunten,
                      'hoehe': anschlussleitung.hoehe, 'breite': anschlussleitung.breite,
                      'laenge': anschlussleitung.laenge, 'baujahr': anschlussleitung.baujahr,
                      'sohleoben': anschlussleitung.sohleoben, 'sohleunten': anschlussleitung.sohleunten,
                      'deckeloben': anschlussleitung.deckeloben, 'deckelunten': anschlussleitung.deckelunten,
                      'profilnam': anschlussleitung.profilnam, 'entwart': entwart,
                      'ks': anschlussleitung.ks, 'simstatus': anschlussleitung.simstatus,
                      'kommentar': anschlussleitung.kommentar, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: anschlussleitungen\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen",
                    stmt_category='m145-import anschlussleitung',
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

                        xsch = _get_float(_gp.findtext("GP003", 0.0))
                        if xsch == 0.0:
                            xsch = _get_float(_gp.findtext("GP005", 0.0))
                        ysch = _get_float(_gp.findtext("GP004", 0.0))
                        if ysch == 0.0:
                            ysch = _get_float(_gp.findtext("GP006", 0.0))

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

    #TODO: Inspektionsdaten der Anschlussleitungen ergänzen

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
            pumpentyp= 0
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
                # pnam, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                pnam = block.findtext("KG001", None)
                knoten_typ = 0

                knoten_typ = block.findtext("KG305", -1)

                smp = block.find("GO/GP")

                if smp is None:
                    fehlermeldung(
                        "Fehler beim XML-Import: Pumpen",
                        f'Keine Geometrie "SMP" für Pumpe {pnam}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    wert = smp.findtext("GP003")
                    if wert is None:
                        wert = smp.findtext("GP005", 0.0)
                    xsch = _get_float(wert)

                    wert = smp.findtext("GP004")
                    if wert is None:
                        wert = smp.findtext("GP006", 0.0)
                    ysch = _get_float(wert)
                    sohlhoehe = _get_float(smp.findtext("GP007", 0.0))

                yield Pumpe(
                    pnam=pnam,
                    schoben=pnam,
                    schunten=schunten,
                    pumpentyp=pumpentyp,
                    volanf=volanf,
                    volges=volges,
                    sohle=sohlhoehe,
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
                    parameters=(pumpe.pumpentyp,),
                ):
                    break

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

