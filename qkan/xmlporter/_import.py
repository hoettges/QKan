import logging
import typing
import xml.etree.ElementTree as ElementTree

from qkan import QKan, enums
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

NS = {"d": "http://www.ofd-hannover.la/Identifikation"}
logger = logging.getLogger("QKan.xml.import")


# region objects
class Schacht(ClassObject):
    schnam: str
    xsch: float
    ysch: float
    sohlhoehe: float
    deckelhoehe: float
    durchm: float
    entwart: str
    knotentyp: int
    simstatus: int
    kommentar: str


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


def _strip_float(value: typing.Union[str, float], default: float = 0.0):
    if isinstance(value, float):
        return value

    if isinstance(value, str) and value.strip() != "":
        return float(value)

    return default


def _consume_smp_block(
    _block: ElementTree.Element,
) -> typing.Tuple[str, int, float, float, float]:
    name = _block.findtext("d:Objektbezeichnung", "not found", NS)
    knoten_typ = 0

    for _schacht in _block.findall("d:Knoten", NS):
        knoten_typ = int(_schacht.findtext("d:KnotenTyp", -1, NS))

    smp = _block.find(
        "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='SMP']",
        NS,
    )

    if not smp:
        fehlermeldung(
            "Fehler beim XML-Import: Schächte",
            f'Keine Geometrie "SMP" für Schacht {name}',
        )
        xsch, ysch, sohlhoehe = (0.0,) * 3
    else:
        xsch = _strip_float(smp.findtext("d:Rechtswert", 0.0, NS))
        ysch = _strip_float(smp.findtext("d:Hochwert", 0.0, NS))
        sohlhoehe = _strip_float(smp.findtext("d:Punkthoehe", 0.0, NS))
    return name, knoten_typ, xsch, ysch, sohlhoehe


def geo_smp(_schacht: Schacht) -> typing.Tuple[str, str]:
    """
    Returns geom, geom SQL expressions
    """
    db_type = QKan.config.database.type
    if db_type == enums.QKanDBChoice.SPATIALITE:
        geop = f"MakePoint({_schacht.xsch}, {_schacht.ysch}, {QKan.config.epsg})"
        geom = (
            "CastToMultiPolygon(MakePolygon("
            f"MakeCircle({_schacht.xsch}, {_schacht.ysch}, {_schacht.durchm / 1000}, {QKan.config.epsg})"
            "))"
        )
    elif db_type == enums.QKanDBChoice.POSTGIS:
        geop = f"ST_SetSRID(ST_MakePoint({_schacht.xsch},{_schacht.ysch}),{QKan.config.epsg})"
        geom = ""  # TODO: GEOM is missing
    else:
        raise Exception("Unimplemented database type: {}".format(db_type))

    return geop, geom


def geo_hydro() -> str:
    db_type = QKan.config.database.type
    if db_type == enums.QKanDBChoice.SPATIALITE:
        geom = (
            f"MakeLine(MakePoint(SCHOB.xsch, SCHOB.ysch, {QKan.config.epsg}), "
            f"MakePoint(SCHUN.xsch, SCHUN.ysch, {QKan.config.epsg}))"
        )
    elif db_type == enums.QKanDBChoice.POSTGIS:
        geom = (
            f"ST_MakeLine(ST_SetSRID(ST_MakePoint(SCHOB.xsch, SCHOB.ysch, {QKan.config.epsg}),"
            f"ST_SetSRID(ST_MakePoint(SCHUN.xsch, SCHUN.ysch, {QKan.config.epsg}))"
        )
    else:
        raise Exception("Unimplemented database type: {}".format(db_type))
    return geom


# TODO: DRY loops
# noinspection SqlNoDataSourceInspection, SqlResolve
class ImportTask:
    def __init__(self, db_qkan: DBConnection, xml_file: str):
        self.db_qkan = db_qkan

        # nr (str) => description
        self.mapper_entwart: typing.Dict[str, str] = {}
        self.mapper_pump: typing.Dict[int, str] = {}
        self.mapper_profile: typing.Dict[str, str] = {}
        self.mapper_outlet: typing.Dict[str, str] = {}
        self.mapper_simstatus: typing.Dict[int, str] = {}

        # Load XML
        self.xml = ElementTree.ElementTree()
        self.xml.parse(xml_file)

    def run(self):
        self._init_mappers()
        self._schaechte()
        self._auslaesse()
        self._speicher()
        self._haltungen()
        self._wehre()
        self._pumpen()

        del self.db_qkan
        logger.debug("Closed DB")

        return True

    def _init_mappers(self):
        def consume(target: typing.Dict[typing.Union[int, str], str]):
            for row in self.db_qkan.fetchall():
                if str(row[0]).isnumeric():
                    target[int(row[0])] = row[1]
                else:
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

    def _schaechte(self):
        def _iter() -> typing.Iterator[Schacht]:
            # .//Schacht/../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/d:Knoten/d:Schacht/../..",
                NS,
            )

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name, knoten_typ, xsch, ysch, sohlhoehe = _consume_smp_block(block)

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=_strip_float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe",
                            0.0,
                            NS,
                        )
                    ),
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    entwart=block.findtext("d:Entwaesserungsart", "not found", NS),
                    knotentyp=knoten_typ,
                    simstatus=int(block.findtext("d:Status", 0, NS)),
                    kommentar=block.findtext("d:Kommentar", "-", NS),
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
                simstatus = f"{schacht.simstatus}_he"
                self.mapper_simstatus[schacht.simstatus] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Schächte [2]"):
                    return None

            # Geo-Objekte
            db_type = QKan.config.database.type
            if db_type == enums.QKanDBChoice.SPATIALITE:
                geop = f"MakePoint({schacht.xsch}, {schacht.ysch}, {QKan.config.epsg})"
                geom = (
                    "CastToMultiPolygon(MakePolygon("
                    f"MakeCircle({schacht.xsch}, {schacht.ysch}, {schacht.durchm / 1000}, {QKan.config.epsg})"
                    "))"
                )
            elif db_type == enums.QKanDBChoice.POSTGIS:
                geop = f"ST_SetSRID(ST_MakePoint({schacht.xsch},{schacht.ysch}),{QKan.config.epsg})"
                geom = ""  # TODO: GEOM is missing
            else:
                fehlermeldung(
                    "Programmfehler!", "Datenbanktyp ist fehlerhaft.\nAbbruch!",
                )
                return None

            sql = f"""
            INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, 
                    schachttyp, simstatus, kommentar, geop, geom)
            VALUES ('{schacht.schnam}', {schacht.xsch}, {schacht.ysch}, {schacht.sohlhoehe}, {schacht.deckelhoehe}, 
                    {schacht.durchm}, '{entwart}', 'Schacht', '{simstatus}', '{schacht.kommentar}', {geop}, {geom})
            """
            if not self.db_qkan.sql(sql, "xml_import Schächte [3]"):
                return None

        self.db_qkan.commit()

    def _auslaesse(self):
        def _iter() -> typing.Iterator[Schacht]:
            # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/"
                "d:Knoten/d:Bauwerk/d:Auslaufbauwerk/../../..",
                NS,
            )

            logger.debug(f"Anzahl Ausläufe: {len(blocks)}")

            for block in blocks:
                name, knoten_typ, xsch, ysch, sohlhoehe = _consume_smp_block(block)

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=_strip_float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='GOK']/d:Punkthoehe",
                            0.0,
                            NS,
                        )
                    ),
                    durchm=0.5,
                    entwart="",
                    knotentyp=knoten_typ,
                    simstatus=int(block.findtext("d:Status", 0, NS)),
                    kommentar=block.findtext("d:Kommentar", "-", NS),
                )

        for auslass in _iter():
            # Simstatus-Nr aus HE ersetzten
            if auslass.simstatus in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[auslass.simstatus]
            else:
                sql = """
                INSERT INTO simulationsstatus (he_nr, bezeichnung)
                VALUES ({s}, '{s}')
                """.format(
                    s=auslass.simstatus
                )
                simstatus = f"{auslass.simstatus}_he"
                self.mapper_simstatus[auslass.simstatus] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Auslässe [1]"):
                    return None

            # Geo-Objekte
            geop, geom = geo_smp(auslass)

            sql = f"""
            INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, 
                    schachttyp, simstatus, kommentar, geop, geom)
            VALUES ('{auslass.schnam}', {auslass.xsch}, {auslass.ysch}, {auslass.sohlhoehe}, {auslass.deckelhoehe}, 
                        {auslass.durchm}, '{auslass.entwart}', 'Auslass', '{simstatus}', '{auslass.kommentar}', {geop}, 
                    {geom})
            """
            if not self.db_qkan.sql(sql, "xml_import Auslässe [2]"):
                return None

        self.db_qkan.commit()

    def _speicher(self):
        def _iter() -> typing.Iterator[Schacht]:
            # .//Becken/../../.. nimmt AbwassertechnischeAnlage
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage"
                "/d:Knoten/d:Bauwerk/d:Becken/../../..",
                NS,
            )

            logger.debug(f"Anzahl Becken: {len(blocks)}")

            knoten_typ = 0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", "not found", NS)

                for _schacht in block.findall("d:Knoten", NS):
                    knoten_typ = int(_schacht.findtext("d:KnotenTyp", -1, NS))

                smp = block.find(
                    "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='KOP']",
                    NS,
                )

                if not smp:
                    fehlermeldung(
                        "Fehler beim XML-Import: Speicher",
                        f'Keine Geometrie "KOP" für Becken {name}',
                    )
                    xsch, ysch, sohlhoehe = (0.0,) * 3
                else:
                    xsch = _strip_float(smp.findtext("d:Rechtswert", 0.0, NS))
                    ysch = _strip_float(smp.findtext("d:Hochwert", 0.0, NS),)
                    sohlhoehe = _strip_float(smp.findtext("d:Punkthoehe", 0.0, NS))

                yield Schacht(
                    schnam=name,
                    xsch=xsch,
                    ysch=ysch,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=float(
                        block.findtext(
                            "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe",
                            0.0,
                            NS,
                        )
                    ),
                    durchm=0.5,
                    entwart="",
                    knotentyp=knoten_typ,
                    simstatus=int(block.findtext("d:Status", 0, NS)),
                    kommentar=block.findtext("d:Kommentar", "-", NS),
                )

        for speicher in _iter():
            if speicher.simstatus in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[speicher.simstatus]
            else:
                sql = """
                INSERT INTO simulationsstatus (he_nr, bezeichnung)
                VALUES ({s}, '{s}')
                """.format(
                    s=speicher.simstatus
                )
                simstatus = f"{speicher.simstatus}_he"
                self.mapper_simstatus[speicher.simstatus] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Speicher [1]"):
                    return None

            # Geo-Objekte
            geop, geom = geo_smp(speicher)

            sql = f"""
            INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, 
                    schachttyp, simstatus, kommentar, geop, geom)
            VALUES ('{speicher.schnam}', {speicher.xsch}, {speicher.ysch}, {speicher.sohlhoehe}, {speicher.deckelhoehe}, 
                {speicher.durchm}, '{speicher.entwart}', 'Speicher', '{simstatus}', '{speicher.kommentar}', {geop}, 
                {geom})
            """
            if not self.db_qkan.sql(sql, "xml_import Speicher [2]"):
                return None

    def _haltungen(self):
        def _iter() -> typing.Iterator[Haltung]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/d:Kante/d:Haltung/../..",
                NS,
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
                yschun,
            ) = (0.0,) * 11
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", "not found", NS)

                # TODO: Does <AbwassertechnischeAnlage> even contain multiple <Kante>?
                for _haltung in block.findall("d:Kante/d:KantenTyp/..", NS):
                    schoben = _haltung.findtext("d:KnotenZulauf", "not found", NS)
                    schunten = _haltung.findtext("d:KnotenAblauf", "not found", NS)

                    sohleoben = _strip_float(
                        block.findtext("d:SohlhoeheZulauf", 0.0, NS)
                    )
                    sohleunten = _strip_float(
                        block.findtext("d:SohlhoeheAblauf", 0.0, NS)
                    )
                    laenge = _strip_float(block.findtext("d:Laenge", 0.0, NS))

                    for profil in _haltung.findall("d:Profil", NS):
                        profilnam = profil.findtext("d:Profilart", "not found", NS)
                        hoehe = (
                            _strip_float(profil.findtext("d:Profilhoehe", 0.0, NS))
                            / 1000
                        )
                        breite = (
                            _strip_float(profil.findtext("d:Profilbreite", 0.0, NS))
                            / 1000
                        )

                for _haltung in block.findall(
                    "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start", NS
                ):
                    xschob = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, NS))
                    yschob = _strip_float(_haltung.findtext("d:Hochwert", 0.0, NS))
                    deckeloben = _strip_float(
                        _haltung.findtext("d:Punkthoehe", 0.0, NS)
                    )

                for _haltung in block.findall(
                    "d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende", NS
                ):
                    xschun = _strip_float(_haltung.findtext("d:Rechtswert", 0.0, NS))
                    yschun = _strip_float(_haltung.findtext("d:Hochwert", 0.0, NS))
                    deckelunten = _strip_float(
                        _haltung.findtext("d:Punkthoehe", 0.0, NS)
                    )

                yield Haltung(
                    haltnam=name,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    sohleoben=sohleoben,
                    sohleunten=sohleunten,
                    deckeloben=deckeloben,
                    deckelunten=deckelunten,
                    profilnam=profilnam,
                    entwart=block.findtext("d:Entwaesserungsart", "not found", NS),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=int(block.findtext("d:Status", 0, NS)),
                    kommentar=block.findtext("d:Kommentar", "-", NS),
                    xschob=xschob,
                    yschob=yschob,
                    xschun=xschun,
                    yschun=yschun,
                )

        def _iter2() -> typing.Iterator[Haltung]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Haltung/..",
                NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Haltungen: {len(blocks)}")

            ks = 1.5
            laenge = 0.0
            for block in blocks:
                name = block.findtext("d:Objektbezeichnung", "not found", NS)

                # RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
                # TODO: Does <HydraulikObjekt> even contain multiple <Haltung>?
                for _haltung in block.findall("d:Haltung", NS):
                    cs1 = _haltung.findtext("d:Rauigkeitsansatz", "0", NS)
                    if cs1 == "1":
                        ks = _strip_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKb", 0.0, NS)
                        )
                    elif cs1 == "2":
                        ks = _strip_float(
                            _haltung.findtext("d:RauigkeitsbeiwertKst", 0.0, NS)
                        )
                    else:
                        ks = 0.0
                        fehlermeldung(
                            "Fehler im XML-Import von HydraulikObjekte_Haltungen",
                            f"Ungültiger Wert für Rauigkeitsansatz {cs1} in Haltung {name}",
                        )

                    laenge = _strip_float(
                        _haltung.findtext("d:Berechnungslaenge", 0.0, NS)
                    )

                yield Haltung(
                    haltnam=name, laenge=laenge, ks=ks,
                )

        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung in _iter():
            if haltung.simstatus in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[haltung.simstatus]
            else:
                sql = """
                INSERT INTO simulationsstatus (he_nr, bezeichnung)
                VALUES ({s}, '{s}')
                """.format(
                    s=haltung.simstatus
                )
                simstatus = f"{haltung.simstatus}_he"
                self.mapper_simstatus[haltung.simstatus] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Haltungen [1]"):
                    return None

            if haltung.entwart in self.mapper_entwart:
                entwart = self.mapper_entwart[haltung.entwart]
            else:
                sql = """
                INSERT INTO entwaesserungsarten (kuerzel, bezeichnung)
                VALUES ('{e}', '{e}')
                """.format(
                    e=haltung.entwart
                )
                self.mapper_entwart[haltung.entwart] = haltung.entwart
                entwart = haltung.entwart

                if not self.db_qkan.sql(sql, "xml_import Haltungen [2]"):
                    return None

            # Geo
            db_type = QKan.config.database.type
            if db_type == enums.QKanDBChoice.SPATIALITE:
                geom = (
                    f"MakeLine(MakePoint({haltung.xschob},{haltung.yschob},{QKan.config.epsg}),"
                    f"MakePoint({haltung.xschun},{haltung.yschun},{QKan.config.epsg}))"
                )
            elif db_type == enums.QKanDBChoice.POSTGIS:
                geom = (
                    f"ST_MakeLine(ST_SetSRID(ST_MakePoint({haltung.xschob},{haltung.yschob},{QKan.config.epsg}),"
                    f"ST_SetSRID(ST_MakePoint({haltung.xschun},{haltung.yschun}),{QKan.config.epsg}))"
                )
            else:
                fehlermeldung(
                    "Programmfehler!", "Datenbanktyp ist fehlerhaft.\nAbbruch!",
                )
                return None

            sql = f"""
                INSERT INTO haltungen 
                    (geom, haltnam, schoben, schunten, 
                    hoehe, breite, laenge, sohleoben, sohleunten, deckeloben, deckelunten, 
                    profilnam, entwart, ks, simstatus, kommentar, xschob, xschun, yschob, yschun)
                VALUES (
                    {geom}, '{haltung.haltnam}', '{haltung.schoben}', '{haltung.schunten}', {haltung.hoehe},
                    {haltung.breite}, {haltung.laenge}, {haltung.sohleoben}, {haltung.sohleunten}, 
                    {haltung.deckeloben}, {haltung.deckelunten}, '{haltung.profilnam}', '{entwart}', 
                    0, '{simstatus}', '{haltung.kommentar}', '{haltung.xschob}', '{haltung.xschun}', 
                    '{haltung.yschob}', '{haltung.yschun}'
                    )
                """

            if not self.db_qkan.sql(sql, "xml_import Haltungen [3]"):
                return None

        self.db_qkan.commit()

        # 2. Teil: Hier werden die hydraulischen Haltungsdaten in die Datenbank geschrieben
        for haltung in _iter2():
            sql = f"""
                        UPDATE haltungen
                            SET ks = {haltung.ks},
                            laenge = {haltung.laenge}
                            WHERE haltnam = '{haltung.haltnam}'
                            """

            if not self.db_qkan.sql(sql, "xml_import Haltung [4]"):
                return None

        self.db_qkan.commit()

    def _wehre(self):
        # Hier werden die Hydraulikdaten zu den Wehren in die Datenbank geschrieben.
        # Bei Wehren stehen alle wesentlichen Daten im Hydraulikdatenkollektiv, weshalb im Gegensatz zu den
        # Haltungsdaten keine Stammdaten verarbeitet werden.

        def _iter() -> typing.Iterator[Wehr]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Wehr/..",
                NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Wehre: {len(blocks)}")

            schoben, schunten, wehrtyp = ("",) * 3
            schwellenhoehe, kammerhoehe, laenge, uebeiwert = (0.0,) * 4
            for block in blocks:
                # TODO: Does <HydraulikObjekt> even contain multiple <Wehr>?
                for _wehr in block.findall("d:Wehr", NS):
                    schoben = _wehr.findtext("d:SchachtZulauf", "not found", NS)
                    schunten = _wehr.findtext("d:SchachtAblauf", "not found", NS)
                    wehrtyp = _wehr.findtext("d:WehrTyp", "not found", NS)

                    schwellenhoehe = _strip_float(
                        _wehr.findtext("d:Schwellenhoehe", 0.0, NS)
                    )
                    laenge = _strip_float(
                        _wehr.findtext("d:LaengeWehrschwelle", 0.0, NS)
                    )
                    kammerhoehe = _strip_float(_wehr.findtext("d:Kammerhoehe", 0.0, NS))

                    # Überfallbeiwert der Wehr Kante (abhängig von Form der Kante)
                    uebeiwert = _strip_float(
                        _wehr.findtext("d:Ueberfallbeiwert", 0.0, NS)
                    )

                yield Wehr(
                    wnam=block.findtext("d:Objektbezeichnung", "not found", NS),
                    schoben=schoben,
                    schunten=schunten,
                    wehrtyp=wehrtyp,
                    schwellenhoehe=schwellenhoehe,
                    kammerhoehe=kammerhoehe,
                    laenge=laenge,
                    uebeiwert=uebeiwert,
                )

        for wehr in _iter():
            geom = geo_hydro()

            # Bei den Wehren muessen im Gegensatz zu den Haltungen die
            # Koordinaten aus den Schachtdaten entnommen werden.
            # Dies ist in QKan einfach, da auch Auslaesse und Speicher in der
            # Tabelle "schaechte" gespeichert werden.

            sql = f"""
                INSERT INTO wehre 
                                (wnam, schoben, schunten, wehrtyp, schwellenhoehe, kammerhoehe, laenge, uebeiwert, geom)
                SELECT '{wehr.wnam}', '{wehr.schoben}', '{wehr.schunten}', '{wehr.wehrtyp}', {wehr.schwellenhoehe}, 
                        {wehr.kammerhoehe}, {wehr.laenge}, {wehr.uebeiwert}, {geom}
                FROM schaechte AS SCHOB, schaechte AS SCHUN
                WHERE SCHOB.schnam = '{wehr.schoben}' AND SCHUN.schnam = '{wehr.schunten}'
                """

            if not self.db_qkan.sql(sql, "xml_import Wehre [1]"):
                return None

        self.db_qkan.commit()

    def _pumpen(self):
        def _iter() -> typing.Iterator[Pumpe]:
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/"
                "d:Knoten/d:Bauwerk/d:Pumpe/../../..",
                NS,
            )
            logger.debug(f"Anzahl Pumpen: {len(blocks)}")

            for block in blocks:
                yield Pumpe(
                    pnam=block.findtext("d:Objektbezeichnung", "not found", NS),
                    simstatus=int(block.findtext("d:Status", 0, NS)),
                    kommentar=block.findtext("d:Kommentar", "-", NS),
                )

        def _iter2() -> typing.Iterator[Pumpe]:
            # Hydraulik
            blocks = self.xml.findall(
                "d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/"
                "d:HydraulikObjekte/d:HydraulikObjekt/d:Pumpe/..",
                NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Pumpen: {len(blocks)}")

            schoben, schunten, steuersch = ("",) * 3
            _pumpentyp = 0
            volanf, volges, sohle = (0.0,) * 3
            for block in blocks:
                # TODO: Does <HydraulikObjekt> even contain multiple <Pumpe>?
                # `_pumpe = block.find("d:Pumpe", NS)` should be used if it does not
                for _pumpe in block.findall("d:Pumpe", NS):
                    _pumpentyp = int(_pumpe.findtext("d:PumpenTyp", -1, NS))
                    schoben = _pumpe.findtext("d:SchachtZulauf", "not found", NS)
                    schunten = _pumpe.findtext("d:SchachtAblauf", "not found", NS)
                    steuersch = _pumpe.findtext("d:Steuerschacht", "not found", NS)
                    sohle = _strip_float(_pumpe.findtext("d:Sohlhoehe", 0.0, NS))
                    volanf = _strip_float(_pumpe.findtext("d:Anfangsvolumen", 0.0, NS))
                    volges = _strip_float(_pumpe.findtext("d:Gesamtvolumen", 0.0, NS))

                yield Pumpe(
                    pnam=block.findtext("d:Objektbezeichnung", "not found", NS),
                    schoben=schoben,
                    schunten=schunten,
                    pumpentyp=_pumpentyp,
                    volanf=volanf,
                    volges=volges,
                    sohle=sohle,
                    steuersch=steuersch,
                )

        for pumpe in _iter2():
            geom = geo_hydro()

            if pumpe.pumpentyp in self.mapper_pump:
                pumpentyp = self.mapper_pump[pumpe.pumpentyp]
            else:
                pumpentyp = "{}_he".format(pumpe.pumpentyp)
                sql = f"INSERT INTO pumpentypen (bezeichnung) Values ('{pumpe.pumpentyp}')"
                self.mapper_pump[pumpe.pumpentyp] = pumpentyp
                if not self.db_qkan.sql(sql, "xml_import Pumpe [1]"):
                    break

            # Bei den Pumpen muessen im Gegensatz zu den Haltungen die
            # Koordinaten aus den Schachtdaten entnommen werden.
            # Dies ist in QKan einfach, da auch Auslaesse und Speicher
            # in der Tabelle "schaechte" gespeichert werden.
            sql = f"""
                INSERT INTO pumpen 
                    (pnam, volanf, volges, sohle, schoben, schunten, pumpentyp, steuersch, geom)
                SELECT '{pumpe.pnam}', {pumpe.volanf}, {pumpe.volges}, {pumpe.sohle}, '{pumpe.schoben}', 
                        '{pumpe.schunten}', '{pumpentyp}', '{pumpe.steuersch}', {geom}
                FROM schaechte AS SCHOB, schaechte AS SCHUN
                WHERE SCHOB.schnam = '{pumpe.schoben}' AND SCHUN.schnam = '{pumpe.schunten}'"""

            if not self.db_qkan.sql(sql, "xml_import Pumpe [2]"):
                return None

        self.db_qkan.commit()

        for pumpe in _iter():
            if pumpe.simstatus in self.mapper_simstatus:
                simstatus = self.mapper_simstatus[pumpe.simstatus]
            else:
                sql = """
                INSERT INTO simulationsstatus (he_nr, bezeichnung)
                VALUES ({s}, '{s}')
                """.format(
                    s=pumpe.simstatus
                )
                simstatus = f"{pumpe.simstatus}_he"
                self.mapper_simstatus[pumpe.simstatus] = simstatus
                if not self.db_qkan.sql(sql, "xml_import Pumpe [3]"):
                    return None

            sql = f"""
                    UPDATE pumpen
                    SET 
                    simstatus = '{simstatus}',
                    kommentar = '{pumpe.kommentar}'
                    WHERE pnam = '{pumpe.pnam}'
                    """

            if not self.db_qkan.sql(sql, "xml_import (22)"):
                return None

        self.db_qkan.commit()
