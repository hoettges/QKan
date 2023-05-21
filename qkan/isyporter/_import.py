import logging
import sys
import xml.etree.ElementTree as ElementTree
from typing import Dict, Iterator, Tuple, Union
from lxml import etree
from fnmatch import fnmatch
from qgis.core import Qgis
from qgis.utils import iface
from qkan import QKan
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung


logger = logging.getLogger("QKan.xml.import")


# region objects
class Schacht(ClassObject):
    schnam: str = ""
    xsch: float = 0.0
    ysch: float = 0.0
    sohlhoehe: float = 0.0
    deckelhoehe: float = 0.0
    durchm: float = 0.0
    druckdicht: int = 0
    entwart: str = ""
    strasse: str = ""
    knotentyp: int = 0
    material: str = ""
    simstatus: int = 0
    kommentar: str = ""

class Schacht_untersucht(ClassObject):
    schnam: str = ""
    durchm: float = 0.0
    druckdicht: int = 0
    entwart: str = ""
    strasse: str = ""
    knotentyp: int = 0
    simstatus: int = 0
    kommentar: str = ""
    baujahr: int = 0
    untersuchtag: str = ""
    untersucher: str = ""
    wetter: int = 0
    bewertungsart: int = 0
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
    videozaehler: int = 0
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
    profilnam: str = ""
    entwart: str = ""
    material: str = ""
    strasse: str = ""
    ks: float = 1.5
    simstatus: int = 0
    kommentar: str = ""
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
    wetter: int = 0
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


class Untersuchdat_haltung(ClassObject):
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
    ks: float = 1.5
    simstatus: int = 0
    kommentar: str = ""
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0

class Wehr(ClassObject):
    wnam: str
    schoben: str
    schunten: str
    wehrtyp: str
    schwellenhoehe: float
    kammerhoehe: float
    laenge: float
    uebeiwert: float
    simstatus: int = 0
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
    simstatus: int = 0
    kommentar: str = ""
    xsch: float = 0.0
    ysch: float = 0.0


# endregion


def _strip_float(value: Union[str, float], default: float = 0.0) -> float:
    if isinstance(value, float):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return float(value)
        except ValueError:
            return default

    return default


def _strip_int(value: Union[str, int], default: int = 0) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return int(value)
        except ValueError:
            return default


    return default


def _strip_int_2(value: Union[str, int], default: int = 63) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return int(value)
        except ValueError:
            print("_m145porter._import.py._strip_int: %s" % sys.exc_info()[1])
            return default

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

        self.data_coice = data_choice
        if data_choice == "ISYBAU Daten":
            self.datenart = "ISYBAU"
        if data_choice == "DWA M-150 Daten":
            self.datenart = "DWA"

        # nr (str) => description
        self.mapper_entwart: Dict[str, str] = {}
        self.mapper_pump: Dict[str, str] = {}
        self.mapper_profile: Dict[str, str] = {}
        self.mapper_outlet: Dict[str, str] = {}
        self.mapper_simstatus: Dict[str, str] = {}
        self.mapper_untersuchrichtung: Dict[str, str] = {}
        self.mapper_wetter: Dict[str, str] = {}
        self.mapper_bewertungsart: Dict[str, str] = {}
        self.mapper_druckdicht: Dict[str, str] = {}


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
        name = _block.findtext("d:Objektbezeichnung", "not found", self.NS)
        knoten_typ = 0

        for _schacht in _block.findall("d:Knoten", self.NS):
            knoten_typ = _strip_int(_schacht.findtext("d:KnotenTyp", -1, self.NS))


        smp = _block.find(
            "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='SMP']",
            self.NS,
        )

        if not smp:
            #fehlermeldung(
            #    "Fehler beim XML-Import: Schächte",
            #    f'Keine Geometrie "SMP" für Schacht {name}',
            #)
            xsch = _strip_float(_block.findtext("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt/d:Rechtswert", 0.0, self.NS))
            ysch = _strip_float(_block.findtext("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt/d:Hochwert", 0.0, self.NS))
            sohlhoehe = _strip_float(_block.findtext("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt/d:Punkthoehe", 0.0, self.NS))
            #xsch, ysch, sohlhoehe = (0.0,) * 3
        else:
            xsch = _strip_float(smp.findtext("d:Rechtswert", 0.0, self.NS))
            ysch = _strip_float(smp.findtext("d:Hochwert", 0.0, self.NS))
            sohlhoehe = _strip_float(smp.findtext("d:Punkthoehe", 0.0, self.NS))
        return name, knoten_typ, xsch, ysch, sohlhoehe

    def run(self) -> bool:
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
            ('RW Druckleitung', 'RD', 'Transporthaltung ohne Anschlüsse', 1, 2, None, 'DR', None, 1),
            ('SW Druckleitung', 'SD', 'Transporthaltung ohne Anschlüsse', 2, 1, None, 'DS', None, 1),
            ('MW Druckleitung', 'MD', 'Transporthaltung ohne Anschlüsse', 0, 0, None, 'DW', None, 1),
            ('RW nicht angeschlossen', 'RT', 'Transporthaltung ohne Anschlüsse', 1, 2, None, None, 1, 0),
            ('MW nicht angeschlossen', 'MT', 'Transporthaltung ohne Anschlüsse', 0, 0, None, None, 1, 0),
            ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, None, None, 0, None),
            ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None, 0, None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m145, isybau, transport, druckdicht)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "he8_import Referenzliste entwaesserungsarten", daten, many=True):
            return False

    def _init_mappers(self) -> None:
        def consume(target: Dict[str, str]) -> None:
            for row in self.db_qkan.fetchall():
                target[row[0]] = row[1]

        if not self.db_qkan.sql(
            "SELECT isybau, bezeichnung FROM entwaesserungsarten",
            "xml_import entwaesserungsarten",
        ):
            raise Exception("Failed to init ENTWART mapper")
        consume(self.mapper_entwart)

        if not self.db_qkan.sql(
            "SELECT he_nr, bezeichnung FROM pumpentypen", "xml_import pumpentypen"
        ):
            raise Exception("Failed to init PUMP mapper")
        consume(self.mapper_pump)

        if not self.db_qkan.sql(
            "SELECT he_nr, profilnam FROM profile", "xml_import profile"
        ):
            raise Exception("Failed to init PROFILE mapper")
        consume(self.mapper_profile)

        if not self.db_qkan.sql(
            "SELECT he_nr, bezeichnung FROM auslasstypen", "xml_import auslasstypen"
        ):
            raise Exception("Failed to init OUTLET mapper")
        consume(self.mapper_outlet)

        if not self.db_qkan.sql(
            "SELECT he_nr, bezeichnung FROM simulationsstatus",
            "xml_import simulationsstatus",
        ):
            raise Exception("Failed to init SIMSTATUS mapper")
        consume(self.mapper_simstatus)

        if not self.db_qkan.sql(
            "SELECT kuerzel, bezeichnung FROM untersuchrichtung",
            "xml_import untersuchrichtung",
        ):
            raise Exception("Failed to init untersuchrichtung mapper")
        consume(self.mapper_untersuchrichtung)

        if not self.db_qkan.sql(
            "SELECT kuerzel, bezeichnung FROM wetter",
            "xml_import wetter",
        ):
            raise Exception("Failed to init wetter mapper")
        consume(self.mapper_wetter)

        if not self.db_qkan.sql(
            "SELECT kuerzel, bezeichnung FROM bewertungsart",
            "xml_import bewertungsart",
        ):
            raise Exception("Failed to init bewertungsart mapper")
        consume(self.mapper_bewertungsart)

        if not self.db_qkan.sql(
            "SELECT kuerzel, bezeichnung FROM druckdicht",
            "xml_import druckdicht",
        ):
            raise Exception("Failed to init druckdicht mapper")
        consume(self.mapper_druckdicht)

    def _schaechte(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Schacht/../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='2']",
                self.NS,
            )

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)


                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=_strip_float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten"
                            "/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe",
                            0.0,
                            self.NS
                        )
                    ),
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    entwart=block.findtext("d:Entwaesserungsart", "not found", self.NS),
                    strasse=block.findtext("d:Lage/d:Strassenname", "not found", self.NS),
                    knotentyp=knoten_typ,
                    simstatus=_strip_int(block.findtext("d:Status", 0, self.NS)),
                    material=block.findtext("d:Knoten/d:Schacht/d:Aufbau/d:MaterialAufbau", "not found", self.NS),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                )

        def _iter2() -> Iterator[Schacht]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Schacht/..",
                self.NS,
            )
            logger.debug(f"Anzahl Schaechte: {len(blocks)}")

            druckdicht = 0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                for _schacht in block.findall("d:Schacht", self.NS):
                    druckdicht = _strip_int(_schacht.findtext("d:DruckdichterDeckel", "0", self.NS))


                yield Schacht(
                    schnam=name,
                    druckdicht=druckdicht,
                )


        for schacht in _iter():
            # Entwässerungsarten
            bez = 'NULL'
            if schacht.entwart in self.mapper_entwart:
                entwart = self.mapper_entwart[schacht.entwart]
            else:
                entwaesserung = {'Mischwasser': ['Mi*'],
                                 'Regenwasser': ['Re*'],
                                 'Schmutzwasser': ['Sc*']}
                for x in entwaesserung.keys():
                    for patt in entwaesserung[x]:
                        if fnmatch(schacht.entwart, patt):
                            key = [i for i, x in entwaesserung.items() if str(patt) in x][0]
                            bez = key

                sql = """
                INSERT INTO entwaesserungsarten (isybau, bezeichnung)
                VALUES ('{e}', '{f}')
                """.format(
                    e=schacht.entwart, f=bez
                )
                self.mapper_entwart[schacht.entwart] = schacht.entwart
                entwart = schacht.entwart

                if not self.db_qkan.sql(sql, "xml_import Schächte [1]"):
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
            if str(schacht.simstatus) in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[str(schacht.simstatus)]
            else:
                sql = """
                INSERT INTO simulationsstatus (he_nr, bezeichnung)
                VALUES ({s}, '{s}')
                """.format(
                    s=schacht.simstatus
                )
                simstatus = f"{schacht.simstatus}_he"
                self.mapper_simstatus[str(schacht.simstatus)] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Schächte [3]"):
                    return None


            # sql = f"""
            # INSERT INTO schaechte (schnam, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, strasse,
            #         schachttyp, simstatus, material, kommentar, xsch, ysch, geop, geom)
            # VALUES (?, ?, ?, ?, ?, ?, ?, 'Schacht', ?, ?, ?, ?, ?, MakePoint(?, ?, ?),
            #          CastToMultiPolygon(MakePolygon(MakeCircle(?, ?, ?, ?))
            #      ))
            # """
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import Schächte [4]",
            #     parameters=(
            #         schacht.schnam,
            #         schacht.sohlhoehe,
            #         schacht.deckelhoehe,
            #         schacht.durchm,
            #         druckdicht,
            #         entwart,
            #         schacht.strasse,
            #         simstatus,
            #         schacht.material,
            #         schacht.kommentar,
            #         schacht.xsch,
            #         schacht.ysch,
            #         schacht.xsch,
            #         schacht.ysch,
            #         QKan.config.epsg,
            #         schacht.xsch,
            #         schacht.ysch,
            #         schacht.durchm,
            #         QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'schnam': schacht.schnam, 'xsch': schacht.xsch, 'ysch': schacht.ysch,
                      'sohlhoehe': schacht.sohlhoehe, 'deckelhoehe': schacht.deckelhoehe,
                      'durchm': schacht.durchm, 'druckdicht': druckdicht, 'entwart': schacht.entwart,
                      'strasse': schacht.strasse, 'knotentyp': schacht.knotentyp,
                      'simstatus': simstatus, 'kommentar': schacht.kommentar, 'schachttyp': 'Schacht', 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        for schacht in _iter2():
            if not self.db_qkan.sql(
                "UPDATE schaechte SET druckdicht = ? WHERE schnam = ?",
                "xml_import Schacht [4b]",
                parameters=(schacht.druckdicht, schacht.schnam),
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
            wetter = 0
            strasse = ""
            bewertungsart = 0
            bewertungstag = ""
            datenart = self.datenart

            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)
                baujahr = _strip_int(block.findtext("d:Baujahr", 0, self.NS))
                strasse = block.findtext("d:Lage/d:Strassenname", "not found", self.NS)

                for _schacht in block.findall("d:OptischeInspektion", self.NS):

                    untersuchtag = _schacht.findtext("d:Inspektionsdatum", "not found", self.NS)

                    untersucher = _schacht.findtext("d:NameUntersucher", "not found", self.NS)

                    wetter = _strip_int(_schacht.findtext("d:Wetter", "0", self.NS))

                    for _schachtz in _schacht.findall("d:Knoten/d:Bewertung", self.NS):

                        bewertungsart = _strip_int(_schachtz.findtext("d:Bewertungsverfahren", "0", self.NS))

                        bewertungstag = _schachtz.findtext("d:Bewertungsdatum", "not found", self.NS)

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

            # sql = f"""
            # INSERT INTO schaechte_untersucht (schnam, durchm, kommentar, geop)
            # VALUES (?, ?, ?, MakePoint(?,?,?))
            # """
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import Schächte_untersucht [1]",
            #     parameters=(
            #         schacht_untersucht.schnam,
            #         schacht_untersucht.durchm,
            #         schacht_untersucht.kommentar,
            #         schacht_untersucht.xsch, schacht_untersucht.ysch, QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'schnam': schacht_untersucht.schnam, 'xsch': schacht_untersucht.xsch,
                      'ysch': schacht_untersucht.ysch,
                      'durchm': schacht_untersucht.durchm, 'kommentar': schacht_untersucht.kommentar, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte_untersucht\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte_untersucht",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return


        self.db_qkan.commit()


        for schacht_untersucht in _iter3():
            if schacht_untersucht.wetter in self.mapper_wetter:
                wetter = self.mapper_wetter[schacht_untersucht.wetter]
            else:
                sql = """
                INSERT INTO wetter (kuerzel, bezeichnung)
                VALUES ('{e}', '{e}')
                """.format(
                    e=schacht_untersucht.wetter
                )
                self.mapper_untersuchrichtung[schacht_untersucht.wetter] = schacht_untersucht.wetter
                wetter = schacht_untersucht.wetter

                if not self.db_qkan.sql(sql, "xml_import Schächte_untersucht [2]"):
                    return None

            if schacht_untersucht.bewertungsart in self.mapper_bewertungsart:
                bewertungsart = self.mapper_bewertungsart[schacht_untersucht.bewertungsart]
            else:
                sql = """
                           INSERT INTO bewertungsart (kuerzel, bezeichnung)
                           VALUES ('{e}', '{e}')
                           """.format(
                    e=schacht_untersucht.bewertungsart
                )
                self.mapper_untersuchrichtung[schacht_untersucht.bewertungsart] = schacht_untersucht.bewertungsart
                bewertungsart = schacht_untersucht.bewertungsart

                if not self.db_qkan.sql(sql, "xml_import Schächte_untersucht [3]"):
                    return None

            if not self.db_qkan.sql(
                "UPDATE schaechte_untersucht SET untersuchtag=?, untersucher=?, wetter=?, baujahr=?, strasse=?, bewertungsart=?," 
                "bewertungstag=?, datenart=? WHERE schnam = ?",
                "xml_import Schächte_untersucht [4]",
                parameters=(schacht_untersucht.untersuchtag, schacht_untersucht.untersucher, wetter, schacht_untersucht.baujahr, schacht_untersucht.strasse, bewertungsart, schacht_untersucht.bewertungstag,
                            schacht_untersucht.datenart, schacht_untersucht.schnam),
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

                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)
                inspektionslaenge = _strip_float(block.findtext(
                    "d:OptischeInspektion/d:Knoten/d:Inspektionsdaten/d:KZustand[d:InspektionsKode='DDB'][d:Streckenschaden='B']/d:VertikaleLage",
                    "0.0", self.NS))

                for _untersuchdat_schacht in block.findall("d:OptischeInspektion/d:Knoten/d:Inspektionsdaten/d:KZustand", self.NS):

                    id = _strip_int(_untersuchdat_schacht.findtext("d:Index", "0", self.NS))
                    videozaehler = _strip_int(_untersuchdat_schacht.findtext("d:Videozaehler", "0", self.NS))
                    timecode = _strip_int(_untersuchdat_schacht.findtext("d:Timecode", "0", self.NS))
                    kuerzel = _untersuchdat_schacht.findtext("d:InspektionsKode", "not found", self.NS)
                    charakt1 = _untersuchdat_schacht.findtext("d:Charakterisierung1", "not found", self.NS)
                    charakt2 = _untersuchdat_schacht.findtext("d:Charakterisierung2", "not found", self.NS)
                    quantnr1 = _strip_float(_untersuchdat_schacht.findtext("d:Quantifizierung1Numerisch", "0.0", self.NS))
                    quantnr2 = _strip_float(_untersuchdat_schacht.findtext("d:Quantifizierung2Numerisch", "0.0", self.NS))
                    streckenschaden = _untersuchdat_schacht.findtext("d:Streckenschaden", "not found", self.NS)
                    streckenschaden_lfdnr = _strip_int(_untersuchdat_schacht.findtext("d:StreckenschadenLfdNr", "0", self.NS))
                    pos_von = _strip_int(_untersuchdat_schacht.findtext("d:PositionVon", "0", self.NS))
                    pos_bis = _strip_int(_untersuchdat_schacht.findtext("d:PositionBis", "0", self.NS))
                    vertikale_lage = _strip_float(_untersuchdat_schacht.findtext("d:VertikaleLage", "0.0", self.NS))
                    bereich = _untersuchdat_schacht.findtext("d:Schachtbereich", "not found", self.NS)
                    foto_dateiname = _untersuchdat_schacht.findtext("d:Fotodatei", "not found", self.NS)

                    ZD = _strip_int_2(_untersuchdat_schacht.findtext("d:Klassifizierung/d:Dichtheit/d:SKDvAuto", 63, self.NS))
                    ZS = _strip_int_2(_untersuchdat_schacht.findtext("d:Klassifizierung/d:Standsicherheit/d:SKSvAuto", 63, self.NS))
                    ZB = _strip_int_2(_untersuchdat_schacht.findtext("d:Klassifizierung/d:Standsicherheit/d:SKBvAuto", 63, self.NS))


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

        for untersuchdat_schacht in _iter():

            # sql = f"""
            # INSERT INTO untersuchdat_schacht(untersuchsch, id, videozaehler, timecode, kuerzel,
            #                                         charakt1, charakt2, quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, vertikale_lage, inspektionslaenge, bereich, foto_dateiname, ordner, ZD, ZS, ZB)
            # VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?)
            # """
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import untersuchdat_schacht [1]",
            #     parameters=(
            #         untersuchdat_schacht.untersuchsch,
            #         untersuchdat_schacht.id,
            #         untersuchdat_schacht.videozaehler,
            #         untersuchdat_schacht.timecode,
            #         untersuchdat_schacht.kuerzel,
            #         untersuchdat_schacht.charakt1,
            #         untersuchdat_schacht.charakt2,
            #         untersuchdat_schacht.quantnr1,
            #         untersuchdat_schacht.quantnr2,
            #         untersuchdat_schacht.streckenschaden,
            #         untersuchdat_schacht.streckenschaden_lfdnr,
            #         untersuchdat_schacht.pos_von,
            #         untersuchdat_schacht.pos_bis,
            #         untersuchdat_schacht.vertikale_lage,
            #         untersuchdat_schacht.inspektionslaenge,
            #         untersuchdat_schacht.bereich,
            #         untersuchdat_schacht.foto_dateiname,
            #         untersuchdat_schacht.ordner,
            #         untersuchdat_schacht.ZD,
            #         untersuchdat_schacht.ZS,
            #         untersuchdat_schacht.ZB,
            #     ),
            # ):
            #     return None
            #
            # sql = """UPDATE untersuchdat_schacht SET geop = schaechte.geop FROM
            #                     schaechte
            #                     WHERE schaechte.schnam = untersuchdat_schacht.untersuchsch"""
            # if not self.db_qkan.sql(
            #         sql,
            #         "xml_import Schächte_untersucht [2]",
            # ):
            #     return None

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
                    **params
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _auslaesse(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/"
                "d:Knoten/d:Bauwerk/d:Auslaufbauwerk/../../..",
                self.NS,
            )

            logger.debug(f"Anzahl Ausläufe: {len(blocks)}")

            for block in blocks:
                name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=_strip_float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten"
                            "/d:Punkt[d:PunktattributAbwasser='GOK']/d:Punkthoehe",
                            0.0,
                            self.NS,
                        )
                    ),
                    durchm=0.5,
                    entwart="",
                    strasse=block.findtext("d:Lage/d:Strassenname", "not found", self.NS),
                    knotentyp=knoten_typ,
                    simstatus=_strip_int(block.findtext("d:Status", 0, self.NS)),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                )

        for auslass in _iter():
            # Simstatus-Nr aus HE ersetzten
            if str(auslass.simstatus) in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[str(auslass.simstatus)]
            else:
                sql = """
                INSERT INTO simulationsstatus (he_nr, bezeichnung)
                VALUES ({s}, '{s}')
                """.format(
                    s=auslass.simstatus
                )
                simstatus = f"{auslass.simstatus}_he"
                self.mapper_simstatus[str(auslass.simstatus)] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Auslässe [1]"):
                    return None

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
                      'sohlhoehe': auslass.sohlhoehe, 'deckelhoehe': auslass.deckelhoehe,
                      'durchm': auslass.durchm, 'entwart': auslass.entwart, 'strasse': auslass.strasse, 'simstatus': simstatus,
                      'kommentar': auslass.kommentar, 'schachttyp': 'Auslass', 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    mute_logger=False,
                    **params
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

            knoten_typ = 0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                for _schacht in block.findall("d:Knoten", self.NS):
                    knoten_typ = _strip_int(_schacht.findtext("d:KnotenTyp", -1, self.NS))

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
                    xsch = _strip_float(smp.findtext("d:Rechtswert", 0.0, self.NS))
                    ysch = _strip_float(
                        smp.findtext("d:Hochwert", 0.0, self.NS),
                    )
                    sohlhoehe = _strip_float(smp.findtext("d:Punkthoehe", 0.0, self.NS))

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
                    durchm=0.5,
                    entwart="",
                    strasse=block.findtext("d:Lage/d:Strassenname", "not found", self.NS),
                    knotentyp=knoten_typ,
                    simstatus=_strip_int(block.findtext("d:Status", 0, self.NS)),
                    kommentar=block.findtext("d:Kommentar", "-", self.NS),
                )

        for speicher in _iter():
            if str(speicher.simstatus) in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[str(speicher.simstatus)]
            else:
                simstatus = f"{speicher.simstatus}_he"
                self.mapper_simstatus[str(speicher.simstatus)] = simstatus
                if not self.db_qkan.sql(
                    "INSERT INTO simulationsstatus (he_nr, bezeichnung) VALUES (?, ?)",
                    "xml_import Speicher [1]",
                    parameters=(speicher.simstatus, speicher.simstatus),
                ):
                    return None

            # sql = f"""
            # INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart,
            #         schachttyp, simstatus, kommentar, geop, geom)
            # VALUES (?, ?, ?, ?, ?, ?, ?, 'Speicher', ?, ?, MakePoint(?, ?, ?), CastToMultiPolygon(MakePolygon(
            #     MakeCircle(?, ?, ?, ?))
            #     ))
            # """
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import Speicher [2]",
            #     parameters=(
            #         speicher.schnam,
            #         speicher.xsch,
            #         speicher.ysch,
            #         speicher.sohlhoehe,
            #         speicher.deckelhoehe,
            #         speicher.durchm,
            #         speicher.entwart,
            #         simstatus,
            #         speicher.kommentar,
            #         speicher.xsch, speicher.ysch, QKan.config.epsg,
            #         speicher.xsch, speicher.ysch, speicher.durchm, QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'schnam': speicher.schnam, 'xsch': speicher.xsch, 'ysch': speicher.ysch,
                      'sohlhoehe': speicher.sohlhoehe, 'deckelhoehe': speicher.deckelhoehe,
                      'durchm': speicher.durchm, 'strasse': speicher.strasse,  'entwart': speicher.entwart, 'simstatus': simstatus,
                      'kommentar': speicher.kommentar, 'schachttyp': 'Speicher', 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _haltungen(self) -> None:
        def _iter() -> Iterator[Haltung]:

            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']",
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
                found_leitung = block.findtext("d:Kante/d:Leitung", "", self.NS)
                if found_leitung == '':

                    name = block.findtext("d:Objektbezeichnung", "not found", self.NS)
                    schoben = block.findtext("d:Kante/d:KnotenZulauf", "not found", self.NS)
                    schunten = block.findtext("d:Kante/d:KnotenAblauf", "not found", self.NS)
                    sohleoben = _strip_float(block.findtext("d:Kante/d:SohlhoeheZulauf", 0.0, self.NS))
                    sohleunten = _strip_float(block.findtext("d:Kante/d:SohlhoeheAblauf", 0.0, self.NS))
                    laenge = _strip_float(block.findtext("d:Kante/d:Laenge", 0.0, self.NS))
                    material = block.findtext("d:Kante/d:Material", "not found", self.NS)
                    profilnam = block.findtext("d:Kante/d:Profil/d:Profilart", "not found", self.NS)
                    hoehe = _strip_float(block.findtext("d:Kante/d:Profil/d:Profilhoehe", 0.0, self.NS)) / 1000.
                    breite = _strip_float(block.findtext("d:Kante/d:Profil/d:Profilbreite", 0.0, self.NS)) / 1000.


                    found_kanten = block.findtext("d:Geometrie/d:Geometriedaten/d:Kanten", "not found", self.NS)
                    if found_kanten:
                        xschob = _strip_float(block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start/d:Rechtswert",
                            0.0, self.NS)
                        )
                        yschob = _strip_float(block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start/d:Hochwert",
                            0.0, self.NS)
                        )
                        xschun = _strip_float(block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende/d:Rechtswert",
                            0.0, self.NS)
                        )
                        yschun = _strip_float(block.findtext(
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
                                    xschob = _strip_float(_start.findtext("d:Rechtswert", 0.0, self.NS))
                                    yschob = _strip_float(_start.findtext("d:Hochwert", 0.0, self.NS))
                                    deckeloben = _strip_float(
                                        _start.findtext("d:Punkthoehe", 0.0, self.NS)
                                    )
                                    break
                                # Für mehr als 1 Kante: Ende der letzten Kante
                                for _ende in block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Ende[last()]", self.NS
                                ):
                                    xschob = _strip_float(_ende.findtext("d:Rechtswert", 0.0, self.NS))
                                    yschob = _strip_float(_ende.findtext("d:Hochwert", 0.0, self.NS))
                                    deckeloben = _strip_float(
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
                        entwart=block.findtext("d:Entwaesserungsart", "not found", self.NS),
                        strasse=block.findtext("d:Lage/d:Strassenname", "not found", self.NS),
                        ks=1.5,  # in Hydraulikdaten enthalten.
                        simstatus=_strip_int(block.findtext("d:Status", 0, self.NS)),
                        kommentar=block.findtext("d:Kommentar", "-", self.NS),
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
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Haltung", self.NS):
                    cs1 = _haltung.findtext("d:Rauigkeitsansatz", "0", self.NS)
                    if cs1 == "1":
                        ks = _strip_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKb", 0.0, self.NS)
                        )
                    elif cs1 == "2":
                        ks = _strip_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKst", 0.0, self.NS)
                        )
                    else:
                        ks = 0.0
                        fehlermeldung(
                            "Fehler im XML-Import von HydraulikObjekte_Haltungen",
                            f"Ungültiger Wert für Rauigkeitsansatz {cs1} in Haltung {name}",
                        )

                    laenge = _strip_float(
                        _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
                    )

                yield Haltung(
                    haltnam=name,
                    laenge=laenge,
                    ks=ks,
                )



        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung in _iter():
            if str(haltung.simstatus) in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[str(haltung.simstatus)]
            else:
                simstatus = f"{haltung.simstatus}_he"
                self.mapper_simstatus[str(haltung.simstatus)] = simstatus
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
                if haltung.entwart in self.mapper_entwart:
                    entwart = self.mapper_entwart[haltung.entwart]
                else:
                    entwaesserung = {'Mischwasser': ['Mi*'],
                                     'Regenwasser': ['Re*'],
                                     'Schmutzwasser': ['Sc*']}
                    for x in entwaesserung.keys():
                        for patt in entwaesserung[x]:
                            if fnmatch(haltung.entwart, patt):
                                key = [i for i, x in entwaesserung.items() if str(patt) in x][0]
                                bez = key

                    sql = """
                                INSERT INTO entwaesserungsarten (isybau, bezeichnung)
                                VALUES ('{e}', '{f}')
                                """.format(
                        e=haltung.entwart, f=bez
                    )

                    self.mapper_entwart[haltung.entwart] = haltung.entwart
                    entwart = haltung.entwart

                    if not self.db_qkan.sql(sql, "xml_import Haltung [1]"):
                        return None



            # sql = f"""
            #     INSERT INTO haltungen
            #         (haltnam, schoben, schunten,
            #         hoehe, breite, laenge, material, sohleoben, sohleunten,
            #         profilnam, entwart, ks, simstatus, kommentar, xschob, xschun, yschob, yschun, geom)
            #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, MakeLine(MakePoint(?,?,?),MakePoint(?,?,?)
            # ))
            #     """
            #
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import Haltungen [3]",
            #     parameters=(
            #         haltung.haltnam,
            #         haltung.schoben,
            #         haltung.schunten,
            #         haltung.hoehe,
            #         haltung.breite,
            #         haltung.laenge,
            #         haltung.material,
            #         haltung.sohleoben,
            #         haltung.sohleunten,
            #         haltung.profilnam,
            #         entwart,
            #         haltung.ks,
            #         simstatus,
            #         haltung.kommentar,
            #         haltung.xschob,
            #         haltung.xschun,
            #         haltung.yschob,
            #         haltung.yschun,
            #         haltung.xschob, haltung.yschob, QKan.config.epsg,
            #         haltung.xschun, haltung.yschun, QKan.config.epsg,
            #     ),
            # ):
            #     return None

            params = {'haltnam': haltung.haltnam, 'schoben': haltung.schoben, 'schunten': haltung.schunten,
                      'hoehe': haltung.hoehe,
                      'breite': haltung.breite, 'laenge': haltung.laenge,
                      'sohleoben': haltung.sohleoben, 'sohleunten': haltung.sohleunten,
                      'material': haltung.material, 'profilnam': haltung.profilnam, 'entwart': entwart,
                      'strasse': haltung.strasse,
                      'ks': haltung.ks, 'simstatus': simstatus, 'kommentar': haltung.kommentar, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()


        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        for haltung in _iter2():
            if not self.db_qkan.sql(
                "UPDATE haltungen SET ks = ?, laenge = ? WHERE haltnam = ?",
                "xml_import Haltung [4]",
                parameters=(haltung.ks, haltung.laenge, haltung.haltnam),
            ):
                return None

        self.db_qkan.commit()


    def _haltunggeom(self):
        blocks = self.xml.findall(
            "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']",
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
            found_leitung = block.findtext("d:Kante/d:Leitung", "", self.NS)
            if found_leitung == '':

                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                found_kanten = block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS)
                if found_kanten:

                    if block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS) is not None:
                        if len(block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS)) > 2:
                            for _gp in block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS):
                                xschob = _strip_float(_gp.findtext("d:Kante/d:Start/d:Rechtswert", 0.0, self.NS))
                                yschob = _strip_float(_gp.findtext("d:Kante/d:Start/d:Hochwert",0.0, self.NS))

                                x_liste.append(xschob)
                                y_liste.append(yschob)

                            text = str(name), x_liste, y_liste
                            list.append(text)


                else:
                    if block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS) is not None:
                        if len(block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS)) > 1:
                            for _gp in block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS):
                                xschob = _strip_float(_gp.findtext("d:Start/d:Rechtswert", 0.0, self.NS))
                                yschob = _strip_float(_gp.findtext("d:Start/d:Hochwert", 0.0, self.NS))

                                x_liste.append(xschob)
                                y_liste.append(yschob)

                            text = str(name), x_liste, y_liste
                            list.append(text)
        list.append('Ende')

        for line in list:
            #line_tokens = line.split(',')
            name = line[0]
            if line != "Ende":
                x_liste = line[1]   # xsch
                x_liste.pop(0)
                #x_liste.pop(-1)
                y_liste = line[2]   # ysch
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
                        del self.db_qkan
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
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektart='1']",
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
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)
                baujahr = _strip_int(block.findtext("d:Baujahr", 0, self.NS))

                # TODO: Does <AbwassertechnischeAnlage> even contain multiple <Kante>?
                for _haltung in block.findall("d:Kante/d:KantenTyp/..", self.NS):
                    schoben = _haltung.findtext("d:KnotenZulauf", "not found", self.NS)
                    schunten = _haltung.findtext("d:KnotenAblauf", "not found", self.NS)

                    laenge = _strip_float(_haltung.findtext("d:Laenge", 0.0, self.NS))


                    for profil in _haltung.findall("d:Profil", self.NS):
                        hoehe = (
                            _strip_float(profil.findtext("d:Profilhoehe", 0.0, self.NS))
                            / 1000
                        )
                        breite = (
                            _strip_float(profil.findtext("d:Profilbreite", 0.0, self.NS))
                            / 1000
                        )

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start", self.NS
                ):
                    if _haltung is not None:
                        xschob = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschob = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckeloben = _strip_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass


                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Start",
                        self.NS
                ):
                    if _haltung is not None:
                        xschob = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschob = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckeloben = _strip_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende", self.NS
                ):
                    if _haltung is not None:
                        xschun = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschun = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckelunten = _strip_float(
                            _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                        )
                    else:
                        pass

                for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Ende",
                        self.NS
                ):
                    if _haltung is not None:
                        xschun = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                        yschun = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                        deckelunten = _strip_float(
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
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Haltung", self.NS):

                    laenge = _strip_float(
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
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)
                strasse = block.findtext("d:Lage/d:Strassenname", "not found", self.NS)

                for _haltung in block.findall("d:OptischeInspektion", self.NS):

                    untersuchtag = _haltung.findtext("d:Inspektionsdatum", "not found", self.NS)

                    untersucher = _haltung.findtext("d:NameUntersucher", "not found", self.NS)

                    wetter = _strip_int(_haltung.findtext("d:Wetter", "0", self.NS))

                    for _haltungz in _haltung.findall("d:Rohrleitung/d:Bewertung", self.NS):

                        bewertungsart = _strip_int(_haltungz.findtext("d:Bewertungsverfahren", "0", self.NS))

                        bewertungstag = _haltungz.findtext("d:Bewertungsdatum", "not found", self.NS)

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

            #geom = u"MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:}))".format(
            #    haltung_untersucht.xschob, haltung_untersucht.yschob, haltung_untersucht.xschun, haltung_untersucht.yschun, int(QKan.config.epsg)
            #)

            # sql = f"""
            #     INSERT INTO haltungen_untersucht
            #         (haltnam, schoben, schunten,
            #         hoehe, breite, laenge, kommentar,baujahr, xschob, yschob, xschun, yschun, geom)
            #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, MakeLine(MakePoint(?,?,?),MakePoint(?,?,?)))
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

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen_untersucht\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen_untersucht",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        for haltung_untersucht in _iter2():
            if not self.db_qkan.sql(
                "UPDATE haltungen_untersucht SET laenge = ? WHERE haltnam = ?",
                "xml_import Haltungen_untersucht [2]",
                parameters=( haltung_untersucht.laenge, haltung_untersucht.haltnam),
            ):
                return None

        self.db_qkan.commit()

        for haltung_untersucht in _iter3():
            if haltung_untersucht.wetter in self.mapper_wetter:
                wetter = self.mapper_wetter[haltung_untersucht.wetter]
            else:
                sql = """
                INSERT INTO wetter (kuerzel, bezeichnung)
                VALUES ('{e}', '{e}')
                """.format(
                    e=haltung_untersucht.wetter
                )
                self.mapper_untersuchrichtung[haltung_untersucht.wetter] = haltung_untersucht.wetter
                wetter = haltung_untersucht.wetter

                if not self.db_qkan.sql(sql, "xml_import Haltungen_untersucht [3]"):
                    return None

            if haltung_untersucht.bewertungsart in self.mapper_bewertungsart:
                bewertungsart = self.mapper_bewertungsart[haltung_untersucht.bewertungsart]
            else:
                sql = """
                           INSERT INTO bewertungsart (kuerzel, bezeichnung)
                           VALUES ('{e}', '{e}')
                           """.format(
                    e=haltung_untersucht.bewertungsart
                )
                self.mapper_untersuchrichtung[haltung_untersucht.bewertungsart] = haltung_untersucht.bewertungsart
                bewertungsart = haltung_untersucht.bewertungsart

                if not self.db_qkan.sql(sql, "xml_import Haltungen_untersucht [4]"):
                    return None

            if not self.db_qkan.sql(
                "UPDATE haltungen_untersucht SET untersuchtag=?, untersucher=?, wetter=?, strasse=?, bewertungsart=?," 
                "bewertungstag=?, datenart=? WHERE haltnam = ?",
                "xml_import Haltungen_untersucht [5]",
                parameters=(haltung_untersucht.untersuchtag, haltung_untersucht.untersucher, wetter, haltung_untersucht.strasse, bewertungsart, haltung_untersucht.bewertungstag,
                            haltung_untersucht.datenart, haltung_untersucht.haltnam),
            ):
                return None

        self.db_qkan.commit()

    def _untersuchdat_haltung(self) -> None:
        def _iter() -> Iterator[Untersuchdat_haltung]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Zustandsdatenkollektiv/d:InspizierteAbwassertechnischeAnlage/d:OptischeInspektion/"
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
            richtung = self.richtung


            for block in blocks:

                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                for _untersuchdat_haltung in block.findall("d:OptischeInspektion/d:Rohrleitung", self.NS):

                    untersuchrichtung = _untersuchdat_haltung.findtext("d:Inspektionsrichtung", "not found", self.NS)
                    inspektionslaenge = _strip_float(_untersuchdat_haltung.findtext("d:Inspektionslaenge", "0.0", self.NS))
                    if inspektionslaenge == 0.0:
                        inspektionslaenge = _strip_float(_untersuchdat_haltung.findtext("d:Inspektionsdaten/d:RZustand[d:InspektionsKode='BCE'][d:Charakterisierung1='XP']/d:Station", "0.0", self.NS))


                    schoben = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenZulauf", "not found", self.NS)
                    schunten = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenAblauf", "not found", self.NS)


                    for _untersuchdat in _untersuchdat_haltung.findall("d:Inspektionsdaten/d:RZustand", self.NS):

                        id = _strip_int(_untersuchdat.findtext("d:Index", "0", self.NS))
                        videozaehler = _strip_int(_untersuchdat.findtext("d:Videozaehler", 0, self.NS))
                        station = _strip_float(_untersuchdat.findtext("d:Station", 0.0, self.NS))
                        timecode = _strip_int(_untersuchdat.findtext("d:Timecode", 0, self.NS))
                        kuerzel = _untersuchdat.findtext("d:InspektionsKode", "not found", self.NS)
                        charakt1 = _untersuchdat.findtext("d:Charakterisierung1", "not found", self.NS)
                        charakt2 = _untersuchdat.findtext("d:Charakterisierung2", "not found", self.NS)
                        quantnr1 = _strip_float(_untersuchdat.findtext("d:Quantifizierung1Numerisch", 0.0, self.NS))
                        quantnr2 = _strip_float(_untersuchdat.findtext("d:Quantifizierung2Numerisch", 0.0, self.NS))
                        streckenschaden = _untersuchdat.findtext("d:Streckenschaden", "not found", self.NS)
                        streckenschaden_lfdnr = _strip_int(_untersuchdat.findtext("d:StreckenschadenLfdNr", 0, self.NS))
                        pos_von = _strip_int(_untersuchdat.findtext("d:PositionVon", 0, self.NS))
                        pos_bis = _strip_int(_untersuchdat.findtext("d:PositionBis", 0, self.NS))
                        foto_dateiname = _untersuchdat.findtext("d:Fotodatei", "not found", self.NS)


                        ZD = _strip_int_2(_untersuchdat.findtext("d:Klassifizierung/d:Dichtheit/d:SKDvAuto", 63, self.NS))
                        ZS = _strip_int_2(_untersuchdat.findtext("d:Klassifizierung/d:Standsicherheit/d:SKSvAuto", 63, self.NS))
                        ZB = _strip_int_2(_untersuchdat.findtext("d:Klassifizierung/d:Standsicherheit/d:SKBvAuto", 63, self.NS))



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
                        richtung=richtung,
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

                        name = _untersuchdat_haltung.findtext("d:FilmObjekte/d:FilmObjekt/d:Objektbezeichnung", "not found", self.NS)

                        film_dateiname = _untersuchdat_haltung.findtext("d:Filmname", "not found", self.NS)

                        yield Untersuchdat_haltung(
                            untersuchhal=name,
                            film_dateiname=film_dateiname,
                        )

        for untersuchdat_haltung in _iter():

            if untersuchdat_haltung.untersuchrichtung in self.mapper_untersuchrichtung:
                untersuchrichtung = self.mapper_untersuchrichtung[untersuchdat_haltung.untersuchrichtung]
            else:
                sql = """
                INSERT INTO untersuchrichtung (kuerzel, bezeichnung)
                VALUES ('{e}', '{e}')
                """.format(
                    e=untersuchdat_haltung.untersuchrichtung
                )
                self.mapper_untersuchrichtung[untersuchdat_haltung.untersuchrichtung] = untersuchdat_haltung.untersuchrichtung
                untersuchrichtung = untersuchdat_haltung.untersuchrichtung

                if not self.db_qkan.sql(sql, "xml_import untersuchdat_haltung [1]"):
                    return None


            # sql = f"""
            # INSERT INTO untersuchdat_haltung (untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler,inspektionslaenge, station, timecode, kuerzel,
            #                                         charakt1, charakt2, quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, foto_dateiname, film_dateiname,
            #                                          ordner_bild, ordner_video, richtung, ZD, ZB, ZS)
            # VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)
            # """
            # if not self.db_qkan.sql(
            #     sql,
            #     "xml_import untersuchdat_haltung [2]",
            #     parameters=(
            #         untersuchdat_haltung.untersuchhal,
            #         untersuchrichtung,
            #         untersuchdat_haltung.schoben,
            #         untersuchdat_haltung.schunten,
            #         untersuchdat_haltung.id,
            #         untersuchdat_haltung.videozaehler,
            #         untersuchdat_haltung.inspektionslaenge,
            #         untersuchdat_haltung.station,
            #         untersuchdat_haltung.timecode,
            #         untersuchdat_haltung.kuerzel,
            #         untersuchdat_haltung.charakt1,
            #         untersuchdat_haltung.charakt2,
            #         untersuchdat_haltung.quantnr1,
            #         untersuchdat_haltung.quantnr2,
            #         untersuchdat_haltung.streckenschaden,
            #         untersuchdat_haltung.streckenschaden_lfdnr,
            #         untersuchdat_haltung.pos_von,
            #         untersuchdat_haltung.pos_bis,
            #         untersuchdat_haltung.foto_dateiname,
            #         untersuchdat_haltung.film_dateiname,
            #         untersuchdat_haltung.ordner_bild,
            #         untersuchdat_haltung.ordner_video,
            #         untersuchdat_haltung.richtung,
            #         untersuchdat_haltung.ZD,
            #         untersuchdat_haltung.ZB,
            #         untersuchdat_haltung.ZS
            #     ),
            # ):
            #     return None

            params = {'untersuchhal': untersuchdat_haltung.untersuchhal, 'untersuchrichtung': untersuchrichtung,
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
                      'ordner_video': untersuchdat_haltung.ordner_video,
                      'richtung': untersuchdat_haltung.richtung, 'ZD': untersuchdat_haltung.ZD,
                      'ZB': untersuchdat_haltung.ZB, 'ZS': untersuchdat_haltung.ZS, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: untersuchdat_haltung\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_haltung",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()


        #geometrieobjekt erzeugen


        for untersuchdat_haltung in _iter2():
            if not self.db_qkan.sql(
                "UPDATE untersuchdat_haltung SET film_dateiname=?" 
                " WHERE  untersuchhal= ?",
                "xml_import untersuchhal [2a]",
                parameters=(untersuchdat_haltung.film_dateiname, untersuchdat_haltung.untersuchhal),
            ):
                return None

        self.db_qkan.commit()


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
                    name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                    # TODO: Does <AbwassertechnischeAnlage> even contain multiple <Kante>?
                    for _haltung in block.findall("d:Kante/d:KantenTyp/..", self.NS):
                        schoben = _haltung.findtext("d:KnotenZulauf", "not found", self.NS)
                        schunten = _haltung.findtext("d:KnotenAblauf", "not found", self.NS)

                        sohleoben = _strip_float(
                            _haltung.findtext("d:SohlhoeheZulauf", 0.0, self.NS)
                        )
                        sohleunten = _strip_float(
                            _haltung.findtext("d:SohlhoeheAblauf", 0.0, self.NS)
                        )
                        laenge = _strip_float(_haltung.findtext("d:Laenge", 0.0, self.NS))

                        material = _haltung.findtext("d:Material", "not found", self.NS)

                        for profil in _haltung.findall("d:Profil", self.NS):
                            profilnam = profil.findtext("d:Profilart", "not found", self.NS)
                            hoehe = (
                                _strip_float(profil.findtext("d:Profilhoehe", 0.0, self.NS))
                                / 1000
                            )
                            breite = (
                                _strip_float(profil.findtext("d:Profilbreite", 0.0, self.NS))
                                / 1000
                            )


                    for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start", self.NS
                    ):
                        if _haltung is not None:
                            xschob = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschob = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckeloben = _strip_float(
                                _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                            )
                        else:
                            pass

                    for _haltung in block.findall(
                            "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Start[1]",
                            self.NS
                    ):
                        if _haltung is not None:
                            xschob = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschob = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckeloben = _strip_float(
                                _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                            )
                        else:
                            pass


                    for _haltung in block.findall(
                        "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende", self.NS
                    ):
                        if _haltung is not None:
                            xschun = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschun = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckelunten = _strip_float(
                                _haltung.findtext("d:Punkthoehe", 0.0, self.NS)
                            )
                        else:
                            pass

                    for _haltung in block.findall(
                            "d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante/d:Ende[last()]",
                            self.NS
                    ):
                        if _haltung is not None:
                            xschun = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, self.NS))
                            yschun = _strip_float(_haltung.findtext("d:Hochwert", 0.0, self.NS))
                            deckelunten = _strip_float(
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
                        sohleoben=sohleoben,
                        sohleunten=sohleunten,
                        deckeloben=deckeloben,
                        deckelunten=deckelunten,
                        profilnam=profilnam,
                        entwart=block.findtext("d:Entwaesserungsart", "not found", self.NS),
                        ks=1.5,  # in Hydraulikdaten enthalten.
                        simstatus=_strip_int(block.findtext("d:Status", 0, self.NS)),
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
                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Leitung", self.NS):
                    cs1 = _haltung.findtext("d:Rauigkeitsansatz", "0", self.NS)
                    if cs1 == "1":
                        ks = _strip_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKb", 0.0, self.NS)
                        )
                    elif cs1 == "2":
                        ks = _strip_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKst", 0.0, self.NS)
                        )
                    else:
                        ks = 0.0
                        fehlermeldung(
                            "Fehler im XML-Import von HydraulikObjekte_Anschlussleitung",
                            f"Ungültiger Wert für Rauigkeitsansatz {cs1} in Anschlussleitung {name}",
                        )

                    laenge = _strip_float(
                        _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
                    )

                yield Anschlussleitung(
                    leitnam=name,
                    laenge=laenge,
                    ks=ks,
                )


        # 1. Teil: Hier werden die Stammdaten zu den anschlussleitung in die Datenbank geschrieben
        for anschlussleitung in _iter():
            if str(anschlussleitung.simstatus) in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[str(anschlussleitung.simstatus)]
            else:
                simstatus = f"{anschlussleitung.simstatus}_he"
                self.mapper_simstatus[str(anschlussleitung.simstatus)] = simstatus
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
                    "INSERT INTO entwaesserungsarten (isybau, bezeichnung) VALUES (?, ?)",
                    "xml_import anschlussleitung [2]",
                    parameters=(anschlussleitung.entwart, anschlussleitung.entwart),
                ):
                    return None


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
                      'laenge': anschlussleitung.laenge, 'material': anschlussleitung.material,
                      'sohleoben': anschlussleitung.sohleoben, 'sohleunten': anschlussleitung.sohleunten,
                      'deckeloben': anschlussleitung.deckeloben, 'deckelunten': anschlussleitung.deckelunten,
                      'profilnam': anschlussleitung.profilnam, 'entwart': entwart,
                      'ks': anschlussleitung.ks, 'simstatus': anschlussleitung.simstatus,
                      'kommentar': anschlussleitung.kommentar, 'xschob': anschlussleitung.xschob,
                      'xschun': anschlussleitung.xschun, 'yschob': anschlussleitung.yschob,
                      'yschun': anschlussleitung.yschun, 'epsg': QKan.config.epsg}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: anschlussleitungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return


        self.db_qkan.commit()

        for anschlussleitung in _iter2():
            if not self.db_qkan.sql(
                "UPDATE anschlussleitungen SET ks = ?, laenge = ? WHERE leitnam = ?",
                "xml_import anschlussleitung [4]",
                parameters=(anschlussleitung.ks, anschlussleitung.laenge, anschlussleitung.leitnam),
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

        list = []
        for block in blocks:
            x_liste = []
            y_liste = []

            found_leitung = block.findtext("d:Kante/d:Leitung", "", self.NS)
            if found_leitung != '':

                name = block.findtext("d:Objektbezeichnung", "not found", self.NS)

                # hier ergännzen mit dem fall das x,y unter Polygone steht!!
                # Haltungen können alternativ als Kanten oder als Polygone vorkommen.

                found_kanten = block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS)
                if found_kanten:

                    if block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS) is not None:
                        if len(block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS)) > 2:
                            for _gp in block.findall("d:Geometrie/d:Geometriedaten/d:Kanten", self.NS):
                                xschob = _strip_float(_gp.findtext("d:Kante/d:Start/d:Rechtswert", 0.0, self.NS))
                                yschob = _strip_float(_gp.findtext("d:Kante/d:Start/d:Hochwert",0.0, self.NS))

                                x_liste.append(xschob)
                                y_liste.append(yschob)

                            text = str(name), x_liste, y_liste
                            list.append(text)


                else:
                    if block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS) is not None:
                        if len(block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS)) > 1:
                            for _gp in block.findall("d:Geometrie/d:Geometriedaten/d:Polygone/d:Polygon/d:Kante", self.NS):
                                xschob = _strip_float(_gp.findtext("d:Start/d:Rechtswert", 0.0, self.NS))
                                yschob = _strip_float(_gp.findtext("d:Start/d:Hochwert", 0.0, self.NS))

                                x_liste.append(xschob)
                                y_liste.append(yschob)

                            text = str(name), x_liste, y_liste
                            list.append(text)

        list.append('Ende')

        for line in list:
            #line_tokens = line.split(',')
            name = line[0]
            if line != "Ende":
                x_liste = line[1]   # xsch
                x_liste.pop(0)
                #x_liste.pop(-1)
                y_liste = line[2]   # ysch
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
                            sql, parameters=(name,)
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
                    schoben = _wehr.findtext("d:SchachtZulauf", "not found", self.NS)
                    schunten = _wehr.findtext("d:SchachtAblauf", "not found", self.NS)
                    wehrtyp = _wehr.findtext("d:WehrTyp", "not found", self.NS)

                    schwellenhoehe = _strip_float(
                        _wehr.findtext("d:Schwellenhoehe", 0.0, self.NS)
                    )
                    laenge = _strip_float(
                        _wehr.findtext("d:LaengeWehrschwelle", 0.0, self.NS)
                    )
                    kammerhoehe = _strip_float(_wehr.findtext("d:Kammerhoehe", 0.0, self.NS))

                    # Überfallbeiwert der Wehr Kante (abhängig von Form der Kante)
                    uebeiwert = _strip_float(
                        _wehr.findtext("d:Ueberfallbeiwert", 0.0, self.NS)
                    )

                yield Wehr(
                    wnam=block.findtext("d:Objektbezeichnung", "not found", self.NS),
                    schoben=schoben,
                    schunten=schunten,
                    wehrtyp=wehrtyp,
                    schwellenhoehe=schwellenhoehe,
                    kammerhoehe=kammerhoehe,
                    laenge=laenge,
                    uebeiwert=uebeiwert,
                )

        for wehr in _iter():
            # geom = geo_hydro()

            # Bei den Wehren muessen im Gegensatz zu den Haltungen die
            # Koordinaten aus den Schachtdaten entnommen werden.
            # Dies ist in QKan einfach, da auch Auslaesse und Speicher in der
            # Tabelle "schaechte" gespeichert werden.

            # sql = f"""
            #     INSERT INTO haltungen
            #                     (haltnam, schoben, schunten, haltungstyp, laenge, geom)
            #     SELECT '{wehr.wnam}', '{wehr.schoben}', '{wehr.schunten}', '{wehr.wehrtyp}', {wehr.laenge},{wehr.geom}
            #     """
            #
            # if not self.db_qkan.sql(sql, "xml_import Wehre [1]"):
            #     return None


            params = {'haltnam': wehr.wnam, 'schoben': wehr.schoben, 'schunten': wehr.schunten,
                      'sohle': wehr.sohle,
                      'haltungtyp': 'Wehr',  # dient dazu, das Verbindungselement als Pumpe zu klassifizieren
                      'simstatus': wehr.simstatus, 'kommentar': wehr.kommentar, 'epsg': QKan.config.epsg}
            # if not self.db_qkan.sql(sql, "xml_import Pumpen [2]", params):
            #     return None

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen",
                    mute_logger=False,
                    **params
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
                    pnam=block.findtext("d:Objektbezeichnung", "not found", self.NS),
                    simstatus=_strip_int(block.findtext("d:Status", 0, self.NS)),
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
                    _pumpentyp = _strip_int(_pumpe.findtext("d:PumpenTyp", -1, self.NS))
                    schoben = _pumpe.findtext("d:SchachtZulauf", "not found", self.NS)
                    schunten = _pumpe.findtext("d:SchachtAblauf", "not found", self.NS)
                    steuersch = _pumpe.findtext("d:Steuerschacht", "not found", self.NS)
                    sohle = _strip_float(_pumpe.findtext("d:Sohlhoehe", 0.0, self.NS))
                    volanf = _strip_float(_pumpe.findtext("d:Anfangsvolumen", 0.0, self.NS))
                    volges = _strip_float(_pumpe.findtext("d:Gesamtvolumen", 0.0, self.NS))

                yield Pumpe(
                    pnam=block.findtext("d:Objektbezeichnung", "not found", self.NS),
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
                pumpentyp = "{}_he".format(pumpe.pumpentyp)
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
            #     INSERT INTO haltungen
            #         (haltnam, schoben, schunten, hoehe, haltungstyp, simstatus, kommentar, geom)
            #     SELECT '{pumpe.haltnam}', '{pumpe.schoben}', '{pumpe.schunten}', '{pumpe.hoehe}', '{pumpentyp}', '{pumpe.simstatus}'
            #     FROM schaechte AS SCHOB, schaechte AS SCHUN
            #     WHERE SCHOB.schnam = '{pumpe.schoben}' AND SCHUN.schnam = '{pumpe.schunten}'"""
            #
            # if not self.db_qkan.sql(sql, "xml_import Pumpen [2]"):
            #     return None

            params = {'haltnam': pumpe.pnam, 'schoben': pumpe.schoben, 'schunten': pumpe.schunten,
                     'sohle': pumpe.sohle,
                     'haltungtyp': 'Pumpe',  # dient dazu, das Verbindungselement als Pumpe zu klassifizieren
                     'simstatus': pumpe.simstatus, 'kommentar': pumpe.kommentar, 'epsg': QKan.config.epsg}
            # if not self.db_qkan.sql(sql, "xml_import Pumpen [2]", params):
            #     return None

            logger.debug(f'isyporter.import - insertdata:\ntabnam: haltungen\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="haltungen",
                    mute_logger=False,
                    **params
            ):
                del self.db_qkan
                return


        self.db_qkan.commit()

        for pumpe in _iter():
            if str(pumpe.simstatus) in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[str(pumpe.simstatus)]
            else:
                simstatus = f"{pumpe.simstatus}_he"
                self.mapper_simstatus[str(pumpe.simstatus)] = simstatus
                if not self.db_qkan.sql(
                    "INSERT INTO simulationsstatus (he_nr, bezeichnung) VALUES (?, ?)",
                    "xml_import Pumpe [3]",
                    parameters=(pumpe.simstatus, pumpe.simstatus),
                ):
                    return None

            if not self.db_qkan.sql(
                "UPDATE haltungen SET simstatus = ?, kommentar = ? WHERE haltnam = ?",
                "xml_import (22)",
                parameters=(simstatus, pumpe.kommentar, pumpe.pnam),
            ):
                return None

        self.db_qkan.commit()
