import logging
import sys
import re
import xml.etree.ElementTree as ElementTree
from typing import Dict, Iterator, Tuple, Union
from lxml import etree
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
         return float(value)

     return default


def _strip_int(value: Union[str, int], default: int = 0) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return int(value)
        except Exception:
            print("_m145porter._import.py._strip_int: %s" % sys.exc_info()[1])

    return default

def _strip_int_2(value: Union[str, int], default: int = 63) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return int(value)
        except Exception:
            print("_m145porter._import.py._strip_int: %s" % sys.exc_info()[1])

    return default


# def _consume_smp_block(
#     _block: ElementTree.Element,
# ) -> Tuple[str, int, float, float, float]:
#      name = _block.findtext("d:Objektbezeichnung", "not found", self.NS)
#      knoten_typ = 0
#
#      for _schacht in _block.findall("d:Knoten", self.NS):
#          knoten_typ = _strip_int(_schacht.findtext("d:KnotenTyp", -1, self.NS))
#
#      smp = _block.find(
#          "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='SMP']",
#          self.NS,
#      )
#
#      if not smp:
#          fehlermeldung(
#              "Fehler beim XML-Import: Schächte",
#              f'Keine Geometrie "SMP" für Schacht {name}',
#          )
#          xsch, ysch, sohlhoehe = (0.0,) * 3
#      else:
#          xsch = _strip_float(smp.findtext("d:Rechtswert", 0.0, self.NS))
#          ysch = _strip_float(smp.findtext("d:Hochwert", 0.0, self.NS))
#          sohlhoehe = _strip_float(smp.findtext("d:Punkthoehe", 0.0, self.NS))
#      return name, knoten_typ, xsch, ysch, sohlhoehe

# def geo_smp(_schacht: Schacht) -> Tuple[str, str]:
#     """
#     Returns geom, geom SQL expressions
#     """
#     db_type = QKan.config.database.type
#     if db_type == enums.QKanDBChoice.SPATIALITE:
#         geop = f"MakePoint({_schacht.xsch}, {_schacht.ysch}, {QKan.config.epsg})"
#         geom = (
#             "CastToMultiPolygon(MakePolygon("
#             f"MakeCircle({_schacht.xsch}, {_schacht.ysch}, {_schacht.durchm / 1000}, {QKan.config.epsg})"
#             "))"
#         )
#     elif db_type == enums.QKanDBChoice.POSTGIS:
#         geop = f"ST_SetSRID(ST_MakePoint({_schacht.xsch},{_schacht.ysch}),{QKan.config.epsg})"
#         geom = ""  # TODO: GEOM is missing
#     else:
#         raise Exception("Unimplemented database type: {}".format(db_type))
#
#     return geop, geom
#
#
# def geo_hydro() -> str:
#     db_type = QKan.config.database.type
#     if db_type == enums.QKanDBChoice.SPATIALITE:
#         geom = (
#             f"MakeLine(MakePoint(SCHOB.xsch, SCHOB.ysch, {QKan.config.epsg}), "
#             f"MakePoint(SCHUN.xsch, SCHUN.ysch, {QKan.config.epsg}))"
#         )
#     elif db_type == enums.QKanDBChoice.POSTGIS:
#         geom = (
#             f"ST_MakeLine(ST_SetSRID(ST_MakePoint(SCHOB.xsch, SCHOB.ysch, {QKan.config.epsg}),"
#             f"ST_SetSRID(ST_MakePoint(SCHUN.xsch, SCHUN.ysch, {QKan.config.epsg}))"
#         )
#     else:
#         raise Exception("Unimplemented database type: {}".format(db_type))
#     return geom
#

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
        #tree = etree.parse(xml_file)
        #x = tree.xpath('namespace-uri(.)')
        #self.NS = {"d": x}

    def run(self) -> bool:
        self._init_mappers()
        if getattr(QKan.config.xml, "import_stamm", True):
            self._schaechte()
            self._auslaesse()
            #self._speicher()
            self._haltungen()
            #self._wehre()
            self._pumpen()
        if getattr(QKan.config.xml, "import_haus", True):
            self._anschlussleitungen()
        if getattr(QKan.config.xml, "import_zustand", True):
            self._schaechte_untersucht()
            self._untersuchdat_schaechte()
            self._haltungen_untersucht()
            self._untersuchdat_haltung()

        return True

    def _init_mappers(self) -> None:
        def consume(target: Dict[str, str]) -> None:
            for row in self.db_qkan.fetchall():
                target[row[0]] = row[1]

        if not self.db_qkan.sql(
            "SELECT kuerzel, bezeichnung FROM entwaesserungsarten",
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
                "KG[KG305='S']"
            )

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                #name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                name = block.findtext("KG001", "not found")
                knoten_typ = 0

                knoten_typ = block.findtext("KG305", -1)

                smp = block.find("GO[GO002='G']/GP")

                if not smp:
                    fehlermeldung(
                        "Fehler beim XML-Import: Schächte",
                        f'Keine Geometrie "SMP[G=002=\'G\']" für Schacht {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _strip_float(smp.findtext("GP003", 0.0))
                    if xsch == 0.0:
                        xsch = _strip_float(smp.findtext("GP005", 0.0))
                    else:
                        pass
                    ysch = _strip_float(smp.findtext("GP004", 0.0))
                    if ysch == 0.0:
                        ysch = _strip_float(smp.findtext("GP006", 0.0))
                    else:
                        pass
                    sohlhoehe = _strip_float(smp.findtext("GP007", 0.0))

                smpD = block.find("GO[GO002='D']/GP")

                deckelhoehe = _strip_float(smpD.findtext("GP007", 0.0))
                if name == '13358032':
                    print(f"Deckelhöhe von Schacht 13358032: {deckelhoehe}")


                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=deckelhoehe,
                    durchm=_strip_int(block.findtext("KG309", 0)),
                    entwart=block.findtext("KG302", "not found"),
                    strasse=block.findtext("KG102", "not found"),
                    knotentyp=knoten_typ,
                    simstatus=block.findtext("KG407", "not found"),
                    kommentar=block.findtext("KG999", "-"),
                    druckdicht=block.findtext("KG315", 0)
                )


        for schacht in _iter():
            # Entwässerungsarten
            if schacht.entwart in self.mapper_entwart:
                entwart = self.mapper_entwart[schacht.entwart]
            else:
                sql = """
                INSERT INTO entwaesserungsarten (kuerzel, bezeichnung)
                VALUES ('{e}', '{e}')
                """.format(
                    e=schacht.entwart
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

            sql = f"""
            INSERT INTO schaechte (schnam, sohlhoehe, deckelhoehe, durchm,druckdicht, entwart, strasse,
                    schachttyp, simstatus, kommentar, xsch, ysch, geop, geom)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Schacht', ?, ?, ?, ?, MakePoint(?, ?, ?), CastToMultiPolygon(MakePolygon(
            MakeCircle(?, ?, ?, ?)
                )))
            """
            if not self.db_qkan.sql(
                sql,
                "xml_import Schächte [4]",
                parameters=(
                    schacht.schnam,
                    schacht.sohlhoehe,
                    schacht.deckelhoehe,
                    schacht.durchm,
                    druckdicht,
                    entwart,
                    schacht.strasse,
                    simstatus,
                    schacht.kommentar,
                    schacht.xsch,
                    schacht.ysch,
                    schacht.xsch, schacht.ysch, QKan.config.epsg,
                    schacht.xsch, schacht.ysch, schacht.durchm, QKan.config.epsg,
                ),
            ):
                return None

        self.db_qkan.commit()


    def _schaechte_untersucht(self) -> None:
        def _iter() -> Iterator[Schacht_untersucht]:
            # .//Schacht/../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "KG/KI/.."
            )

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name = block.findtext("KG001", "not found")
                strasse = block.findtext("KG102", "not found"),
                smp = block.find(
                    "GO/GP"
                )

                if not smp:
                    fehlermeldung(
                        "Fehler beim XML-Import: Schächte",
                        f'Keine Geometrie "SMP" für Schacht {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _strip_float(smp.findtext("GP003", 0.0))
                    if xsch == 0.0:
                        xsch = _strip_float(smp.findtext("GP005", 0.0))
                    else:
                        pass
                    ysch = _strip_float(smp.findtext("GP004", 0.0))
                    if ysch == 0.0:
                        ysch = _strip_float(smp.findtext("GP006", 0.0))
                    else:
                        pass
                    sohlhoehe = _strip_float(smp.findtext("GP007", 0.0))

                yield Schacht_untersucht(
                    schnam=name,
                    strasse=strasse,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    kommentar=block.findtext("Kommentar", "-"),
                )


        def _iter3() -> Iterator[Schacht_untersucht]:
            blocks = self.xml.findall(
                "KG"
            )
            logger.debug(f"Anzahl Schaechte: {len(blocks)}")

            untersuchtag = ""
            untersucher = ""
            wetter = 0
            bewertungsart = 0
            bewertungstag = ""
            datenart = self.datenart
            max_ZD = 63
            max_ZB = 63
            max_ZS = 63

            for block in blocks:
                name = block.findtext("KG001", "not found")
                baujahr = _strip_int(block.findtext("KG303", 0))

                for _schacht in block.findall("KI"):

                    untersuchtag = _schacht.findtext("KI104", "not found")

                    untersucher = _schacht.findtext("KI112", "not found")

                    wetter = _strip_int(_schacht.findtext("KI106", 0))

                    bewertungsart = _schacht.findtext("KI005", "0")

                    bewertungstag = _schacht.findtext("KI204", "not found")

                    max_ZD = _strip_int_2(_schacht.findtext("KI206", 63))
                    max_ZB = _strip_int_2(_schacht.findtext("KI208", 63))
                    max_ZS = _strip_int_2(_schacht.findtext("KI207", 63))

                yield Schacht_untersucht(
                    schnam=name,
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

            sql = f"""
            INSERT INTO schaechte_untersucht (schnam, strasse, durchm, kommentar, geop)
            VALUES (?, ?, ?, ?, MakePoint(?, ?, ?))
            """
            if not self.db_qkan.sql(
                sql,
                "xml_import Schächte_untersucht [1]",
                parameters=(
                    schacht_untersucht.schnam,
                    schacht_untersucht.strasse,
                    schacht_untersucht.durchm,
                    schacht_untersucht.kommentar,
                    schacht_untersucht.xsch, schacht_untersucht.ysch, QKan.config.epsg,
                ),
            ):
                return None

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
                "UPDATE schaechte_untersucht SET untersuchtag=?, untersucher=?, wetter=?, baujahr=?, bewertungsart=?," 
                "bewertungstag=?, datenart=?, max_ZD=?, max_ZB=?, max_ZS=? WHERE schnam = ?",
                "xml_import Schächte_untersucht [4]",
                parameters=(schacht_untersucht.untersuchtag, schacht_untersucht.untersucher, wetter, schacht_untersucht.baujahr, bewertungsart, schacht_untersucht.bewertungstag, schacht_untersucht.datenart,
                            schacht_untersucht.max_ZD, schacht_untersucht.max_ZB, schacht_untersucht.max_ZS, schacht_untersucht.schnam),
            ):
                return None

        self.db_qkan.commit()

    def _untersuchdat_schaechte(self) -> None:
        def _iter() -> Iterator[Untersuchdat_schacht]:
            blocks = self.xml.findall(
                "KG"
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
            ZD = 63
            ZB = 63
            ZS = 63
            xsch= 0.0
            ysch= 0.0

            for block in blocks:

                name = block.findtext("KG001", "not found")
                #inspektionslaenge = _strip_float(_untersuchdat_schacht.findtext(
                 #   "d:OptischeInspektion/d:Knoten/d:Inspektionsdaten/d:KZustand[d:InspektionsKode='DDB'][d:Streckenschaden='B']/d:VertikaleLage",
                  #  "0.0", self.NS))

                for _untersuchdat_schacht in block.findall("KI/KZ"):

                    #id = _strip_int(_untersuchdat_schacht.findtext("d:Index", "0", self.NS))
                    inspektionslaenge = _strip_float(_untersuchdat_schacht.findtext("KZ001", 0.0))
                    videozaehler = _strip_int(_untersuchdat_schacht.findtext("KZ008", 0))
                    #timecode = _strip_int(_untersuchdat_schacht.findtext("d:Timecode", "0", self.NS))
                    kuerzel = _untersuchdat_schacht.findtext("KZ002", "not found")
                    charakt1 = _untersuchdat_schacht.findtext("KZ014", "not found")
                    charakt2 = _untersuchdat_schacht.findtext("KZ015", "not found")
                    quantnr1 = _strip_float(_untersuchdat_schacht.findtext("KZ003", 0.0))
                    quantnr2 = _strip_float(_untersuchdat_schacht.findtext("KZ004", 0.0))
                    streckenschaden = _untersuchdat_schacht.findtext("KZ005", "not found")
                    #streckenschaden_lfdnr = _strip_int(_untersuchdat_schacht.findtext("KZ005", "0"))
                    pos_von = _strip_int(_untersuchdat_schacht.findtext("KZ006", 0))
                    pos_bis = _strip_int(_untersuchdat_schacht.findtext("KZ007", 0))
                    vertikale_lage = _strip_float(_untersuchdat_schacht.findtext("KZ001", 0.0))
                    bereich = _untersuchdat_schacht.findtext("KZ013", "not found")
                    foto_dateiname = _untersuchdat_schacht.findtext("KZ009", "not found")

                    ZD = _strip_int_2(_untersuchdat_schacht.findtext("KZ206", 63))
                    ZB = _strip_int_2(_untersuchdat_schacht.findtext("KZ208", 63))
                    ZS = _strip_int_2(_untersuchdat_schacht.findtext("KZ207", 63))


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
                    ZB=ZB,
                    ZS=ZS,
                    )

        for untersuchdat_schacht in _iter():

            sql = f"""
            INSERT INTO untersuchdat_schacht (untersuchsch, id, videozaehler, timecode, kuerzel, 
                                                    charakt1, charakt2, quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, vertikale_lage, inspektionslaenge, bereich, foto_dateiname, ordner, ZD, ZB, ZS)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?)
            """
            if not self.db_qkan.sql(
                sql,
                "xml_import untersuchdat_schacht [1]",
                parameters=(
                    untersuchdat_schacht.untersuchsch,
                    untersuchdat_schacht.id,
                    untersuchdat_schacht.videozaehler,
                    untersuchdat_schacht.timecode,
                    untersuchdat_schacht.kuerzel,
                    untersuchdat_schacht.charakt1,
                    untersuchdat_schacht.charakt2,
                    untersuchdat_schacht.quantnr1,
                    untersuchdat_schacht.quantnr2,
                    untersuchdat_schacht.streckenschaden,
                    untersuchdat_schacht.streckenschaden_lfdnr,
                    untersuchdat_schacht.pos_von,
                    untersuchdat_schacht.pos_bis,
                    untersuchdat_schacht.vertikale_lage,
                    untersuchdat_schacht.inspektionslaenge,
                    untersuchdat_schacht.bereich,
                    untersuchdat_schacht.foto_dateiname,
                    untersuchdat_schacht.ordner,
                    untersuchdat_schacht.ZD,
                    untersuchdat_schacht.ZB,
                    untersuchdat_schacht.ZS,
                ),
            ):
                return None

        sql = """UPDATE untersuchdat_schacht SET geop = schaechte.geop FROM
                                        schaechte
                                        WHERE schaechte.schnam = untersuchdat_schacht.untersuchsch"""
        if not self.db_qkan.sql(
                sql,
                "xml_import untersuchdat_schacht [2]",
        ):
            return None

        self.db_qkan.commit()

    def _auslaesse(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "KG[KG305='A']"
            )

            logger.debug(f"Anzahl Ausläufe: {len(blocks)}")

            for block in blocks:
                #name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                name = block.findtext("KG001", "not found")
                knoten_typ = 0

                knoten_typ = block.findtext("KG305", -1)

                smp = block.find("GO[GO002='G']/GP")

                if not smp:
                    fehlermeldung(
                        "Fehler beim XML-Import: Schächte",
                        f'Keine Geometrie "SMP[G=002=\'G\']" für Schacht {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _strip_float(smp.findtext("GP003", 0.0))
                    if xsch == 0.0:
                        xsch = _strip_float(smp.findtext("GP005", 0.0))
                    else:
                        pass
                    ysch = _strip_float(smp.findtext("GP004", 0.0))
                    if ysch == 0.0:
                        ysch = _strip_float(smp.findtext("GP006", 0.0))
                    else:
                        pass
                    sohlhoehe = _strip_float(smp.findtext("GP007", 0.0))

                smpD = block.find("GO[GO002='D']/GP")

                deckelhoehe = _strip_float(smpD.findtext("GP007", 0.0))
                if name == '13358032':
                    print(f"Deckelhöhe von Schacht 13358032: {deckelhoehe}")


                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=deckelhoehe,
                    durchm=_strip_int(block.findtext("KG309", 0)),
                    entwart=block.findtext("KG302", "not found"),
                    strasse=block.findtext("KG102", "not found"),
                    knotentyp=knoten_typ,
                    simstatus=block.findtext("KG407", "not found"),
                    kommentar=block.findtext("KG999", "-")
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

            sql = f"""
            INSERT INTO schaechte (
                schnam, xsch, ysch, 
                sohlhoehe, deckelhoehe, durchm, entwart, 
                schachttyp, simstatus, kommentar, geop)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Auslass', ?, ?, MakePoint(?, ?, ?))
            """
            if not self.db_qkan.sql(
                sql,
                "xml_import Auslässe [2]",
                parameters=(
                    auslass.schnam,
                    auslass.xsch,
                    auslass.ysch,
                    auslass.sohlhoehe,
                    auslass.deckelhoehe,
                    auslass.durchm,
                    auslass.entwart,
                    simstatus,
                    auslass.kommentar,
                    auslass.xsch, auslass.ysch, QKan.config.epsg,
                ),
            ):
                return None


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
    #         knoten_typ = 0
    #         for block in blocks:
    #             name = block.findtext("d:Objektbezeichnung", "not found", self.NS)
    #
    #             for _schacht in block.findall("d:Knoten", self.NS):
    #                 knoten_typ = _strip_int(_schacht.findtext("d:KnotenTyp", -1, self.NS))
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
    #                 xsch = _strip_float(smp.findtext("d:Rechtswert", 0.0, self.NS))
    #                 ysch = _strip_float(
    #                     smp.findtext("d:Hochwert", 0.0, self.NS),
    #                 )
    #                 sohlhoehe = _strip_float(smp.findtext("d:Punkthoehe", 0.0, self.NS))
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
    #                 simstatus=_strip_int(block.findtext("d:Status", 0, self.NS)),
    #                 kommentar=block.findtext("d:Kommentar", "-", self.NS),
    #             )
    #
    #     for speicher in _iter():
    #         if str(speicher.simstatus) in self.mapper_simstatus:
    #             simstatus = self.mapper_simstatus[str(speicher.simstatus)]
    #         else:
    #             simstatus = f"{speicher.simstatus}_he"
    #             self.mapper_simstatus[str(speicher.simstatus)] = simstatus
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
            blocks = self.xml.findall(
                "HG"
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
                if block.findtext("HG006")is not None:
                    continue

                name = block.findtext("HG001", "not found")


                schoben = block.findtext("HG003", "not found")
                schunten = block.findtext("HG004", "not found")

                sohleoben = _strip_float(
                    block.findtext("SohlhoeheZulauf", 0.0)
                )
                sohleunten = _strip_float(
                    block.findtext("SohlhoeheAblauf", 0.0)
                )
                laenge = _strip_float(block.findtext("HG310", 0.0))

                material = block.findtext("HG304", "not found")


                profilnam = block.findtext("HG305", "not found")
                hoehe = (
                    _strip_float(block.findtext("HG307", 0.0))
                    / 1000
                )
                breite = (
                    _strip_float(block.findtext("HG306", 0.0))
                    / 1000
                )

                xschob = 0.0
                yschob = 0.0
                xschun = 0.0
                yschun = 0.0
                #x=0

                # for _haltung in block.findall(
                #         "GO/GP[GP999='S']"
                # ):
                #     if x == 0:
                #         xschob = _strip_float(_haltung.findtext("GP003", 0.0))
                #         if xschob == 0.0:
                #             xschob = _strip_float(_haltung.findtext("GP005", 0.0))
                #             print(str(xschob))
                #         yschob = _strip_float(_haltung.findtext("GP004", 0.0))
                #         if yschob == 0.0:
                #             yschob = _strip_float(_haltung.findtext("GP006", 0.0))
                #         deckeloben = _strip_float(
                #             _haltung.findtext("GP007", 0.0)
                #         )
                #
                #     if x == 1:
                #         xschun = _strip_float(_haltung.findtext("GP003", 0.0))
                #         if xschun == 0.0:
                #             xschun = _strip_float(_haltung.findtext("GP005", 0.0))
                #             print(str(xschun))
                #         yschun = _strip_float(_haltung.findtext("GP004", 0.0))
                #         if yschun == 0.0:
                #             yschun = _strip_float(_haltung.findtext("GP006", 0.0))
                #         deckelunten = _strip_float(
                #             _haltung.findtext("GP007", 0.0)
                #         )
                #     x += 1
                #
                # if xschob == 0.0 and yschob == 0.0:
                #     for _haltung in block.findall(
                #             "GO/GP[1]"
                #     ):
                #         xschob = _strip_float(_haltung.findtext("GP003", 0.0))
                #         if xschob == 0.0:
                #             xschob = _strip_float(_haltung.findtext("GP005", 0.0))
                #         yschob = _strip_float(_haltung.findtext("GP004", 0.0))
                #         if yschob == 0.0:
                #             yschob = _strip_float(_haltung.findtext("GP006", 0.0))
                #         deckeloben = _strip_float(
                #             _haltung.findtext("GP007", 0.0)
                #         )
                #
                # if xschun == 0.0 and yschun == 0.0:
                #     for _haltung in block.findall(
                #             "GO/GP[2]"
                #     ):
                #         xschun = _strip_float(_haltung.findtext("GP003", 0.0))
                #         if xschun == 0.0:
                #             xschun = _strip_float(_haltung.findtext("GP005", 0.0))
                #         yschun = _strip_float(_haltung.findtext("GP004", 0.0))
                #         if yschun == 0.0:
                #             yschun = _strip_float(_haltung.findtext("GP006", 0.0))
                #         deckelunten = _strip_float(
                #             _haltung.findtext("GP007", 0.0)
                #         )

                #if block.find("GO[GO002='H']") is not None:
                if block.findall("GO[GO002='H']") is not None:

                    for _gp in block.findall("GO[GO002='H']/GP[1]"):

                        xschob = _strip_float(_gp.findtext("GP003", 0.0))
                        if xschob == 0.0:
                            xschob = _strip_float(_gp.findtext("GP005", 0.0))
                        yschob = _strip_float(_gp.findtext("GP004", 0.0))
                        if yschob == 0.0:
                            yschob = _strip_float(_gp.findtext("GP006", 0.0))
                        deckeloben = _strip_float(
                            _gp.findtext("GP007", 0.0)
                        )


                if block.findall("GO[GO002='H']") is not None:
                    for _gp in block.findall("GO[GO002='H']/GP[last()]"):

                        xschun = _strip_float(_gp.findtext("GP003", 0.0))
                        if xschun == 0.0:
                            xschun = _strip_float(_gp.findtext("GP005", 0.0))
                        yschun = _strip_float(_gp.findtext("GP004", 0.0))
                        if yschun == 0.0:
                            yschun = _strip_float(_gp.findtext("GP006", 0.0))
                        deckelunten = _strip_float(
                            _gp.findtext("GP007", 0.0)
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
                    entwart=block.findtext("HG302", "not found"),
                    strasse=block.findtext("HG102", "not found"),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus= block.findtext("HG407", 0),
                    kommentar=block.findtext("HG999", "-"),
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
        #         name = block.findtext("d:Objektbezeichnung", "not found", self.NS)
        #
        #         # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
        #
        #         #nicht vorhanden in DWA?
        #
        #         # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
        #         for _haltung in block.findall("d:Haltung", self.NS):
        #             cs1 = _haltung.findtext("d:Rauigkeitsansatz", "0", self.NS)
        #             if cs1 == "1":
        #                 ks = _strip_float(
        #                     _haltung.findtext("d:RauigkeitsbeiwertKb", 0.0, self.NS)
        #                 )
        #             elif cs1 == "2":
        #                 ks = _strip_float(
        #                     _haltung.findtext("d:RauigkeitsbeiwertKst", 0.0, self.NS)
        #                 )
        #             else:
        #                 ks = 0.0
        #                 fehlermeldung(
        #                     "Fehler im XML-Import von HydraulikObjekte_Haltungen",
        #                     f"Ungültiger Wert für Rauigkeitsansatz {cs1} in Haltung {name}",
        #                 )
        #
        #             laenge = _strip_float(
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
                self.mapper_entwart[haltung.entwart] = haltung.entwart
                entwart = haltung.entwart

                if not self.db_qkan.sql(
                    "INSERT INTO entwaesserungsarten (kuerzel, bezeichnung) VALUES (?, ?)",
                    "xml_import Haltungen [2]",
                    parameters=(haltung.entwart, haltung.entwart),
                ):
                    return None


            sql = f"""
                INSERT INTO haltungen
                    (haltnam, schoben, schunten, 
                    hoehe, breite, laenge, material, sohleoben, sohleunten,
                    profilnam, entwart, strasse, ks, simstatus, kommentar, xschob, xschun, yschob, yschun, geom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, MakeLine(MakePoint(?,?,?),MakePoint(?,?,?)
            ))
                """

            if not self.db_qkan.sql(
                sql,
                "xml_import Haltungen [3]",
                parameters=(
                    haltung.haltnam,
                    haltung.schoben,
                    haltung.schunten,
                    haltung.hoehe,
                    haltung.breite,
                    haltung.laenge,
                    haltung.material,
                    haltung.sohleoben,
                    haltung.sohleunten,
                    haltung.profilnam,
                    entwart,
                    haltung.strasse,
                    haltung.ks,
                    simstatus,
                    haltung.kommentar,
                    haltung.xschob,
                    haltung.xschun,
                    haltung.yschob,
                    haltung.yschun,
                    haltung.xschob, haltung.yschob, QKan.config.epsg,
                    haltung.xschun, haltung.yschun, QKan.config.epsg,
                ),
            ):
                return None


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
            blocks = self.xml.findall(
                "HG"
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
                name = block.findtext("HG001", "not found")
                baujahr = _strip_int(block.findtext("HG303", 0))


                schoben = block.findtext("HG003", "not found")
                schunten = block.findtext("HG004", "not found")

                laenge = _strip_float(block.findtext("HG314", 0.0))


                hoehe = (
                    _strip_float(block.findtext("HG307", 0.0))
                    / 1000
                )
                breite = (
                    _strip_float(block.findtext("HG306", 0.0))
                    / 1000
                )

                for _haltung in block.findall(
                        "GO/GP[1]"
                ):
                    xschob = _strip_float(_haltung.findtext("GP003", 0.0))
                    if xschob == 0.0:
                        xschob = _strip_float(_haltung.findtext("GP005", 0.0))
                    else:
                        pass
                    yschob = _strip_float(_haltung.findtext("GP004", 0.0))
                    if yschob == 0.0:
                        yschob = _strip_float(_haltung.findtext("GP006", 0.0))
                    else:
                        pass
                    deckeloben = _strip_float(
                        _haltung.findtext("GP007", 0.0)
                    )

                for _haltung in block.findall(
                        "GO/GP[2]"
                ):
                    xschun = _strip_float(_haltung.findtext("GP003", 0.0))
                    if xschun == 0.0:
                        xschun = _strip_float(_haltung.findtext("GP005", 0.0))
                    else:
                        pass
                    yschun = _strip_float(_haltung.findtext("GP004", 0.0))
                    if yschun == 0.0:
                        yschun = _strip_float(_haltung.findtext("GP006", 0.0))
                    else:
                        pass
                    deckelunten = _strip_float(
                        _haltung.findtext("GP007", 0.0)
                    )

                yield Haltung_untersucht(
                    haltnam=name,
                    strasse=block.findtext("HG102", "not found"),
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
        #         name = block.findtext("HG001", "not found")
        #
        #         # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
        #         # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
        #         for _haltung in block.findall("d:Haltung", self.NS):
        #
        #             laenge = _strip_float(
        #                 _haltung.findtext("d:Berechnungslaenge", 0.0, self.NS)
        #             )
        #
        #         yield Haltung_untersucht(
        #             haltnam=name,
        #             laenge=laenge,
        #         )

        def _iter3() -> Iterator[Haltung_untersucht]:
            blocks = self.xml.findall(
                "HG/HI/.."
            )
            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            untersuchtag = ""
            untersucher = ""
            wetter = 0
            bewertungsart = 0
            bewertungstag = ""
            datenart = self.datenart
            max_ZD = 63
            max_ZB = 63
            max_ZS = 63


            for block in blocks:
                name = block.findtext("HG001", "not found")

                for _haltung in block.findall("HI"):

                    untersuchtag = _haltung.findtext("HI104", "not found")

                    untersucher = _haltung.findtext("HI112", "not found")

                    wetter = _strip_int(_haltung.findtext("HI106", 0))

                    bewertungsart = _strip_int(_haltung.findtext("HI005", "0"))

                    bewertungstag = _haltung.findtext("HI204", "not found")

                    max_ZD = _strip_int_2(_haltung.findtext("HI206", 63))
                    max_ZB = _strip_int_2(_haltung.findtext("HI208", 63))
                    max_ZS = _strip_int_2(_haltung.findtext("HI207", 63))

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

            sql = f"""
                INSERT INTO haltungen_untersucht 
                    (haltnam, schoben, schunten, 
                    hoehe, breite, laenge, kommentar,baujahr, strasse, xschob, yschob, xschun, yschun, geom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, MakeLine(MakePoint(?,?,?),MakePoint(?,?,?)))
                """

            if not self.db_qkan.sql(
                sql,
                "xml_import Haltungen_untersucht [1]",
                parameters=(
                    haltung_untersucht.haltnam,
                    haltung_untersucht.schoben,
                    haltung_untersucht.schunten,
                    haltung_untersucht.hoehe,
                    haltung_untersucht.breite,
                    haltung_untersucht.laenge,
                    haltung_untersucht.kommentar,
                    haltung_untersucht.baujahr,
                    haltung_untersucht.strasse,
                    haltung_untersucht.xschob,
                    haltung_untersucht.yschob,
                    haltung_untersucht.xschun,
                    haltung_untersucht.yschun,
                    haltung_untersucht.xschob, haltung_untersucht.yschob, QKan.config.epsg,
                    haltung_untersucht.xschun, haltung_untersucht.yschun, QKan.config.epsg,
                ),
            ):
                return None


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
                "UPDATE haltungen_untersucht SET untersuchtag=?, untersucher=?, wetter=?, bewertungsart=?," 
                "bewertungstag=?, datenart=?, max_ZD=?, max_ZB=?, max_ZS=? WHERE haltnam = ?",
                "xml_import Haltungen_untersucht [5]",
                parameters=(haltung_untersucht.untersuchtag, haltung_untersucht.untersucher, wetter, bewertungsart, haltung_untersucht.bewertungstag,
                            haltung_untersucht.datenart,haltung_untersucht.max_ZD, haltung_untersucht.max_ZB, haltung_untersucht.max_ZS, haltung_untersucht.haltnam),
            ):
                return None

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
            streckenschaden_lfdnr=0
            ZD = 63
            ZB = 63
            ZS = 63


            for block in blocks:

                name = block.findtext("HG001", "not found")
                schoben = block.findtext("HG003", "not found")
                schunten = block.findtext("HG004", "not found")



                untersuchrichtung = block.findtext("HI/HI101", "not found")
                if untersuchrichtung == "I":
                    untersuchrichtung = "in Fließrichtung"

                if untersuchrichtung == "G":
                    untersuchrichtung = "gegen Fließrichtung"

                    #inspektionslaenge = _strip_float(_untersuchdat_haltung.findtext("d:Inspektionslaenge", "0.0", self.NS))
                    #if inspektionslaenge == 0.0:
                     #   inspektionslaenge = _strip_float(_untersuchdat_haltung.findtext("d:Inspektionsdaten/d:RZustand[d:InspektionsKode='BCE'][d:Charakterisierung1='XP']/d:Station", "0.0", self.NS))


                    #schoben = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenZulauf", "not found", self.NS)
                    #schunten = _untersuchdat_haltung.findtext("d:RGrunddaten/d:KnotenAblauf", "not found", self.NS)


                for _untersuchdat in block.findall("HI/HZ"):

                    #id = _strip_int(_untersuchdat.findtext("d:Index", "0", self.NS))
                    videozaehler = _untersuchdat.findtext("HZ008", "0")
                    station = _strip_float(_untersuchdat.findtext("HZ001", 0.0))
                    #timecode = _strip_int(_untersuchdat.findtext("d:Timecode", "0", self.NS))
                    kuerzel = _untersuchdat.findtext("HZ002", "not found")
                    charakt1 = _untersuchdat.findtext("HZ014", "not found")
                    charakt2 = _untersuchdat.findtext("HZ015", "not found")
                    quantnr1 = _strip_float(_untersuchdat.findtext("HZ003", 0.0))
                    quantnr2 = _strip_float(_untersuchdat.findtext("HZ004", 0.0))
                    if len(_untersuchdat.findtext("HZ005", "not found"))<1:
                        streckenschaden = "not found"
                    else:
                        streckenschaden = (_untersuchdat.findtext("HZ005", "not found"))[0]
                    streckenschaden_lfdnra = _untersuchdat.findtext("HZ005", "not found")
                    if any(i.isdigit() for i in streckenschaden_lfdnra) == True:
                        streckenschaden_lfdnr = [int(num) for num in re.findall(r"\d+", streckenschaden_lfdnra)][0]
                    else:
                        streckenschaden_lfdnr = 0
                    #if streckenschaden_lfdnr is not None or streckenschaden_lfdnr != "" or streckenschaden_lfdnr != "not found":
                    #    streckenschaden_lfdnr = int(streckenschaden_lfdnr)
                    pos_von = _strip_int(_untersuchdat.findtext("HZ006", 0))
                    pos_bis = _strip_int(_untersuchdat.findtext("HZ007", 0))
                    foto_dateiname = _untersuchdat.findtext("HZ009", "not found")
                    ZD = _strip_int_2(_untersuchdat.findtext("HZ206", 63))
                    ZB = _strip_int_2(_untersuchdat.findtext("HZ208", 63))
                    ZS = _strip_int_2(_untersuchdat.findtext("HZ207", 63))


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
                    ZB=ZB,
                    ZS=ZS,

            )

#        def _iter2() -> Iterator[Untersuchdat_haltung]:
#                blocks = self.xml.findall(
#                    "d:Datenkollektive/d:Zustandsdatenkollektiv/d:Filme/d:Film/d:Filmname/../..",
#                    self.NS,
#                )
#                logger.debug(f"Anzahl Untersuchdat_haltung: {len(blocks)}")
#
#                film_dateiname = ""
#                for block in blocks:
#                    for _untersuchdat_haltung in block.findall("d:Film/d:FilmObjekte/..", self.NS):
#
#                        name = _untersuchdat_haltung.findtext("d:FilmObjekte/d:FilmObjekt/d:Objektbezeichnung", "not found", self.NS)
#
#                        film_dateiname = _untersuchdat_haltung.findtext("d:Filmname", "not found", self.NS)
#
#                        yield Untersuchdat_haltung(
#                            untersuchhal=name,
#                            film_dateiname=film_dateiname,
#                        )

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

            sql = f"""
            INSERT INTO untersuchdat_haltung (untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler,inspektionslaenge, station, timecode, kuerzel, 
                                                    charakt1, charakt2, quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, foto_dateiname, film_dateiname,
                                                     ordner_bild, ordner_video, richtung, ZD, ZB, ZS)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)
            """
            if not self.db_qkan.sql(
                sql,
                "xml_import untersuchdat_haltung [2]",
                parameters=(
                    untersuchdat_haltung.untersuchhal,
                    untersuchrichtung,
                    untersuchdat_haltung.schoben,
                    untersuchdat_haltung.schunten,
                    untersuchdat_haltung.id,
                    untersuchdat_haltung.videozaehler,
                    untersuchdat_haltung.inspektionslaenge,
                    untersuchdat_haltung.station,
                    untersuchdat_haltung.timecode,
                    untersuchdat_haltung.kuerzel,
                    untersuchdat_haltung.charakt1,
                    untersuchdat_haltung.charakt2,
                    untersuchdat_haltung.quantnr1,
                    untersuchdat_haltung.quantnr2,
                    untersuchdat_haltung.streckenschaden,
                    untersuchdat_haltung.streckenschaden_lfdnr,
                    untersuchdat_haltung.pos_von,
                    untersuchdat_haltung.pos_bis,
                    untersuchdat_haltung.foto_dateiname,
                    untersuchdat_haltung.film_dateiname,
                    untersuchdat_haltung.ordner_bild,
                    untersuchdat_haltung.ordner_video,
                    untersuchdat_haltung.richtung,
                    untersuchdat_haltung.ZD,
                    untersuchdat_haltung.ZB,
                    untersuchdat_haltung.ZS,
                ),
            ):
                return None

        #geomobjekt ergänzen

        self.db_qkan.commit()

        #for untersuchdat_haltung in _iter2():
        #    if not self.db_qkan.sql(
         #       "UPDATE untersuchdat_haltung SET film_dateiname=?"
          #      " WHERE  untersuchhal= ?",
           #     "xml_import untersuchhal [2a]",
            #    parameters=(untersuchdat_haltung.film_dateiname, untersuchdat_haltung.untersuchhal),
            #):
             #   return None

      #  self.db_qkan.commit()


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
                name = block.findtext("HG001", "not found")

                schoben = block.findtext("HG003", "not found")
                schunten = block.findtext("HG004", "not found")

                sohleoben = _strip_float(
                    block.findtext("SohlhoeheZulauf", 0.0)
                )
                sohleunten = _strip_float(
                    block.findtext("SohlhoeheAblauf", 0.0)
                )
                laenge = _strip_float(block.findtext("HG310", 0.0))

                material = block.findtext("HG304", "not found")

                profilnam = block.findtext("HG305", "not found")
                hoehe = (
                        _strip_float(block.findtext("HG307", 0.0))
                        / 1000
                )
                breite = (
                        _strip_float(block.findtext("HG306", 0.0))
                        / 1000
                )

                for _haltung in block.findall(
                        "GO/GP[1]"
                ):
                    xschob = _strip_float(_haltung.findtext("GP003", 0.0))
                    if xschob == 0.0:
                        xschob = _strip_float(_haltung.findtext("GP005", 0.0))
                    else:
                        pass
                    yschob = _strip_float(_haltung.findtext("GP004", 0.0))
                    if yschob == 0.0:
                        yschob = _strip_float(_haltung.findtext("GP006", 0.0))
                    else:
                        pass
                    deckeloben = _strip_float(
                        _haltung.findtext("GP007", 0.0)
                    )

                for _haltung in block.findall(
                        "GO/GP[2]"
                ):
                    xschun = _strip_float(_haltung.findtext("GP003", 0.0))
                    if xschun == 0.0:
                        xschun = _strip_float(_haltung.findtext("GP005", 0.0))
                    else:
                        pass
                    yschun = _strip_float(_haltung.findtext("GP004", 0.0))
                    if yschun == 0.0:
                        yschun = _strip_float(_haltung.findtext("GP006", 0.0))
                    else:
                        pass
                    deckelunten = _strip_float(
                        _haltung.findtext("GP007", 0.0)
                    )

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
                    entwart=block.findtext("HG302", "not found"),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=block.findtext("HG407", 0),
                    kommentar=block.findtext("HG999", "-"),
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
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
                    "INSERT INTO entwaesserungsarten (kuerzel, bezeichnung) VALUES (?, ?)",
                    "xml_import anschlussleitung [2]",
                    parameters=(anschlussleitung.entwart, anschlussleitung.entwart),
                ):
                    return None

            sql = f"""
                INSERT INTO anschlussleitungen 
                    (leitnam, schoben, schunten, 
                    hoehe, breite, laenge, material, sohleoben, sohleunten, deckeloben, deckelunten, 
                    profilnam, entwart, ks, simstatus, kommentar, xschob, xschun, yschob, yschun, geom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, MakeLine(MakePoint(?,?,?),MakePoint(?,?,?)))
                """

            if not self.db_qkan.sql(
                sql,
                "xml_import anschlussleitung [3]",
                parameters=(
                    anschlussleitung.leitnam,
                    anschlussleitung.schoben,
                    anschlussleitung.schunten,
                    anschlussleitung.hoehe,
                    anschlussleitung.breite,
                    anschlussleitung.laenge,
                    anschlussleitung.material,
                    anschlussleitung.sohleoben,
                    anschlussleitung.sohleunten,
                    anschlussleitung.deckeloben,
                    anschlussleitung.deckelunten,
                    anschlussleitung.profilnam,
                    entwart,
                    anschlussleitung.ks,
                    simstatus,
                    anschlussleitung.kommentar,
                    anschlussleitung.xschob,
                    anschlussleitung.xschun,
                    anschlussleitung.yschob,
                    anschlussleitung.yschun,
                    anschlussleitung.xschob, anschlussleitung.yschob, QKan.config.epsg,
                    anschlussleitung.xschun, anschlussleitung.yschun, QKan.config.epsg,
                ),
            ):
                return None


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
    #                 schoben = _wehr.findtext("d:SchachtZulauf", "not found", self.NS)
    #                 schunten = _wehr.findtext("d:SchachtAblauf", "not found", self.NS)
    #                 wehrtyp = _wehr.findtext("d:WehrTyp", "not found", self.NS)
    #
    #                 schwellenhoehe = _strip_float(
    #                     _wehr.findtext("d:Schwellenhoehe", 0.0, self.NS)
    #                 )
    #                 laenge = _strip_float(
    #                     _wehr.findtext("d:LaengeWehrschwelle", 0.0, self.NS)
    #                 )
    #                 kammerhoehe = _strip_float(_wehr.findtext("d:Kammerhoehe", 0.0, self.NS))
    #
    #                 # Überfallbeiwert der Wehr Kante (abhängig von Form der Kante)
    #                 uebeiwert = _strip_float(
    #                     _wehr.findtext("d:Ueberfallbeiwert", 0.0, self.NS)
    #                 )
    #
    #             yield Wehr(
    #                 wnam=block.findtext("d:Objektbezeichnung", "not found", self.NS),
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
            blocks = self.xml.findall(
                "KG[KG306='ZPW']"
            )
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
            simstatus = 0
            kommentar = ""
            xsch = 0.0
            ysch = 0.0

            for block in blocks:
                # name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                name = block.findtext("KG001", "not found")
                knoten_typ = 0

                knoten_typ = block.findtext("KG305", -1)

                smp = block.find(
                    "GO/GP"
                )

                if not smp:
                    fehlermeldung(
                        "Fehler beim XML-Import: Schächte",
                        f'Keine Geometrie "SMP" für Schacht {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _strip_float(smp.findtext("GP003", 0.0))
                    if xsch == 0.0:
                        xsch = _strip_float(smp.findtext("GP005", 0.0))
                    else:
                        pass
                    ysch = _strip_float(smp.findtext("GP004", 0.0))
                    if ysch == 0.0:
                        ysch = _strip_float(smp.findtext("GP006", 0.0))
                    else:
                        pass
                    sohlhoehe = _strip_float(smp.findtext("GP007", 0.0))

                yield Pumpe(
                    pnam=name,
                    schoben=name,
                    schunten=schunten,
                    pumpentyp=pumpentyp,
                    volanf=volanf,
                    volges=volges,
                    sohle=sohlhoehe,
                    steuersch=steuersch
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
            sql = f"""
                           INSERT INTO haltungen 
                               (haltnam, schoben, schunten, hoehe, haltungstyp, simstatus, kommentar)
                           SELECT :pnam, :schoben, :schunten, :sohle, :pumpentyp, :simstatus, :kommentar
                           FROM schaechte AS SCHOB, schaechte AS SCHUN
                           WHERE SCHOB.schnam = :schoben AND SCHUN.schnam = :schunten"""

            params = {'pnam': pumpe.pnam, 'schoben': pumpe.schoben, 'schunten': pumpe.schunten,
                      'sohle': pumpe.sohle, 'pumpentyp': pumpe.pumpentyp,
                      'simstatus': pumpe.simstatus, 'kommentar': pumpe.kommentar}
            if not self.db_qkan.sql(sql, "xml_import Pumpen [2]", params):
                return None

        self.db_qkan.commit()

