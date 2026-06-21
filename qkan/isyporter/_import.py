import sys, os
#import xml.etree.ElementTree as ElementTree
import lxml.etree as ElementTree
from typing import Dict, Iterator, Tuple, Union

from qgis.PyQt.QtCore import QByteArray
from qgis.core import Qgis, QgsGeometry, QgsPoint, QgsPointXY, QgsCircle
from qkan import QKan, enums
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import fehlermeldung
from qkan.utils import get_logger
from qkan.tools.k_schadenstexte import Schadenstexte
from qkan.tools.k_befahrung import setbefahrung

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
    auslasstyp: str = ""
    material: str = ""
    simstatus: str = ""
    kommentar: str = ""
    geop: QByteArray = None
    geom: QByteArray = None

class Schacht_untersucht(ClassObject):
    schnam: str = ""
    durchm: float = 0.0
    sohlhoehe: float = 0.0
    druckdicht: int = 0
    # entwart: str = ""
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
    auftragsbezeichnung: str = ""
    datenart: str = ""
    max_ZD: int = None
    max_ZB: int = None
    max_ZS: int = None
    geop: QByteArray = None
    xsch: float = 0.0
    ysch: float = 0.0

class Untersuchdat_schacht(ClassObject):
    untersuchsch: str = ""
    id: int = 0
    untersuchtag: str = ""
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
    ordner_bild: str = ""
    film_dateiname: str = ""
    ordner_video: str = ""
    ZD: int = None
    ZB: int = None
    ZS: int = None

class Untersuchdat_daten(ClassObject):
    untersuchsch: str = ""
    untersuchtag: str = ""
    untersuchrichtung: str = ""
    datei: str = ""
    objekt: str = ""

class Haltung(ClassObject):
    haltnam: str = ""
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    laengehyd: float = 0.0
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
    geom: QByteArray = None
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0

class Haltung_untersucht(ClassObject):
    haltnam: str = ""
    bezugspunkt: str = ""
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    baujahr: int = 0
    id: int = 0
    untersuchtag: str = ""
    untersucher: str = ""
    untersuchrichtung: str = ""
    wetter: str = ""
    bewertungsart: str = ""
    bewertungstag: str = ""
    strasse: str = ""
    datenart: str = ""
    auftragsbezeichnung: str = ""
    max_ZD: int = None
    max_ZB: int = None
    max_ZS: int = None
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0
    kommentar: str = ""
    geom: QByteArray = None

class Untersuchdat_haltung(ClassObject):
    untersuchhal: str = ""
    untersuchrichtung: str = ""
    schoben: str = ""
    schunten: str = ""
    id: int = 0
    untersuchtag: str = ""
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
    ZD: int = None
    ZB: int = None
    ZS: int = None
    geom: QByteArray = None
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0

class Anschlussleitung(ClassObject):
    leitnam: str = ""
    schoben: str = ""
    schunten: str = ""
    haltnam: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    sohleoben: float = 0.0
    sohleunten: float = 0.0
    deckeloben: float = 0.0
    deckelunten: float = 0.0
    entwart: str = ""
    material: str = ""
    baujahr: int = 0
    ks: float = 1.5
    simstatus: str = ""
    kommentar: str = ""
    geom: QByteArray = None
    xschob: float = 0.0
    yschob: float = 0.0
    xschun: float = 0.0
    yschun: float = 0.0

Anschlussleitung_untersucht = Haltung_untersucht

Untersuchdat_anschlussleitung = Untersuchdat_haltung

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
    geom: QByteArray = None
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
    geom: QByteArray = None
    xsch: float = 0.0
    ysch: float = 0.0

# endregion

def _get_float(value: Union[str, float], default: float = None) -> float:
    if isinstance(value, float):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return float(value)
        except ValueError:
            return default

    return default


def _get_int(value: Union[str, int], default: int = None) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        try:
            return int(value)
        except ValueError:
            logger.error("isyporter._import.py._get_int: %s" % sys.exc_info()[1])

    return default


# noinspection SqlNoDataSourceInspection, SqlResolve
class ImportTask(Schadenstexte):
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
        self.mapper_pump: Dict[str, str] = {}
        self.mapper_profile: Dict[str, str] = {}
        #self.mapper_outlet: Dict[str, str] = {}
        self.mapper_simstatus: Dict[str, str] = {}
        # self.mapper_untersuchrichtung: Dict[str, str] = {}        # direkt umgesetzt
        self.mapper_wetter: Dict[str, str] = {}
        #self.mapper_bewertungsart: Dict[str, str] = {}
        #self.mapper_druckdicht: Dict[str, str] = {}
        self.mapper_bauwerkstypen: Dict[str, str] = {}

        # dictionary zum Ergänzen der Daten beim Einlesen von Schaechte-, Haltungen- und Hausanschluessen_untersucht
        self.schachtdaten = {}
        self.haltungsdaten = {}
        self.anschlussdaten = {}
        self.hydraulikdaten = {}

        # Load XML
        self.xml = ElementTree.ElementTree()
        self.xml.parse(xml_file)

        # Set Namespace
        # tree = etree.parse(xml_file)
        # x = tree.xpath('namespace-uri(.)')
        t = self.xml.getroot()
        self.NS = {"": t.tag[1:].split('}')[0]}

        #TODO: prüfen ob Namespace doch eingelesen werden muss, wenn ja aber mit ElementTree arbeiten

    def _consume_smp_block(self,
            _block: ElementTree.Element,
    ) -> Tuple[str, int, float, float, float]:
        name = _block.findtext("Objektbezeichnung", None, self.NS)
        schacht_typ = 0

        for _schacht in _block.findall("Knoten", self.NS):
            schacht_typ = _get_int(_schacht.findtext("KnotenTyp", None, self.NS))

        smp = _block.find(
            "Geometrie/Geometriedaten/Knoten/Punkt[PunktattributAbwasser='SMP']",
            self.NS,
        )

        if smp is not None:
            #fehlermeldung(
            #    "Fehler beim XML-Import: Schächte",
            #    f'Keine Geometrie "SMP" für Schacht {name}',
            #)
            xsch = _get_float(_block.findtext("Geometrie/Geometriedaten/Knoten/Punkt/Rechtswert", None, self.NS))
            ysch = _get_float(_block.findtext("Geometrie/Geometriedaten/Knoten/Punkt/Hochwert", None, self.NS))
            sohlhoehe = _get_float(_block.findtext("Geometrie/Geometriedaten/Knoten/Punkt/Punkthoehe", None, self.NS))
            #xsch, ysch, sohlhoehe = (0.0,) * 3
        else:
            xsch = _get_float(smp.findtext("Rechtswert", None, self.NS))
            ysch = _get_float(smp.findtext("Hochwert", None, self.NS))
            sohlhoehe = _get_float(smp.findtext("Punkthoehe", None, self.NS))
        return name, schacht_typ, xsch, ysch, sohlhoehe

    def _get_knoten2(self, x_geodaten: ElementTree.Element, with_grafik: bool = True) -> Tuple[
        Union[bytes, None],
        Union[bytes, None],
        Union[float, None],
        Union[float, None],
    ]:
        """Liest ein Geooobjekt, dass ggfs. aus mehreren Teilen besteht, aus dem Geometriedatenblock <Geometrie>: Punkt, Multipoloygon

            :param x_geodaten:  xml-Block mit den Geodaten

            :param with_grafik:   Zusätzliches Einlesen der Schachtgrafik (geom)

            :returns: Objektname, Schachttyp, Punktobjekt, Multipolygonobjekt, Sohlhöhe, Deckelhöhe, Baujahr
        """
        if x_geodaten is None:
            return (None,)*4

        geop = None                     # Schacht als Punktobjekt
        geom = None                     # Schacht als Multipolygon
        xs = ys = xd = yd = xa = ya = sohlhoehe = deckelhoehe = None

        plis = []
        for x_pkt in x_geodaten.findall("Knoten/Punkt", self.NS):
            _typ = x_pkt.findtext("PunktattributAbwasser", None, self.NS)
            if _typ == 'SMP':
                xs = _get_float(x_pkt.findtext("Rechtswert", None, self.NS))
                ys = _get_float(x_pkt.findtext("Hochwert", None, self.NS))
                zs = _get_float(x_pkt.findtext("Punkthoehe", None, self.NS))
                sohlhoehe = zs
                xp = xs
                yp = ys
            elif _typ == 'DMP':
                xd = _get_float(x_pkt.findtext("Rechtswert", None, self.NS))
                yd = _get_float(x_pkt.findtext("Hochwert", None, self.NS))
                zd = _get_float(x_pkt.findtext("Punkthoehe", None, self.NS))
                deckelhoehe = zd
                xp = xd
                yp = yd
            elif _typ == 'GOK':
                zd = _get_float(x_pkt.findtext("Punkthoehe", None, self.NS))
                deckelhoehe = zd
                continue
            else:
                xa = _get_float(x_pkt.findtext("Rechtswert", None, self.NS))
                ya = _get_float(x_pkt.findtext("Hochwert", None, self.NS))
                xp = xa
                yp = ya
                # logger.warning(f'Schacht darf als PunktattributAbwasser nur "SMP" oder "DMP", '
                #                f'aber nicht {_typ} haben')

            # Alle Punkte sammeln, die mehr als 0.03 auseinander liegen
            if plis:
                for x, y in plis:
                    if abs((x - xp)**2 + (y - yp)**2) < 0.03 **2:
                        break
                    else:
                        plis.append([xp, yp])

            # geom wird nur erzeugt, wenn es aus mehreren Punkten besteht, die um mehr als 0.03 verschoben liegen
        if len(plis) > 1:
            xp, yp = plis[0]
            geom = QgsGeometry(QgsCircle.fromCenterDiameter(QgsPoint(xp, yp), 1.0).toLineString())
            geom.convertToMultiType()
            for xp, yp in plis[1:]:
                geom = geom.combine(QgsGeometry(QgsCircle.fromCenterDiameter(QgsPoint(xp, yp), 1.0).toLineString()))

        if xs is not None:
            geop = QgsGeometry.fromPointXY(QgsPointXY(xs, ys))      # Standard: SMP
        elif xa is not None:
            geop = QgsGeometry.fromPointXY(QgsPointXY(xa, ya))      # Alternativ: Andere "V106 PunktattributAbwasser"
        elif xd is not None:
            geop = QgsGeometry.fromPointXY(QgsPointXY(xd, yd))      # Falls nichts anderes gegeben: DMP

        if geop:
            geop_wkb = geop.asWkb()
            logger.debug(f'geop = {geop.asWkt()}')
        else:
            geop_wkb = None

        if not with_grafik:
            return geop_wkb, None, sohlhoehe, deckelhoehe

        for x_polygon in x_geodaten.findall("Polygone/Polygon", self.NS):
            polygonart = x_polygon.findtext("Polygonart", None, self.NS)
            gplis = []
            for x_kante in x_polygon.findall("Kante", self.NS):
                if gplis == []:  # nur 1. Kante
                    x = _get_float(x_kante.findtext("Start/Rechtswert", None, self.NS))
                    y = _get_float(x_kante.findtext("Start/Hochwert", None, self.NS))
                    gplis.append([x, y])
                x = _get_float(x_kante.findtext("Ende/Rechtswert", None, self.NS))
                y = _get_float(x_kante.findtext("Ende/Hochwert", None, self.NS))
                gplis.append([x, y])

                mpunkt = _get_float(x_kante.findtext("Mitte", None, self.NS))
                if mpunkt is not None:
                    logger.error("Kreisbögen können zurzeit nicht verarbeitet werden")

            ptlis = [QgsPointXY(x, y) for x, y in gplis]
            if geom is None:
                geom = QgsGeometry.fromPolylineXY(ptlis)
                geom.convertToMultiType()
            elif polygonart in ('1', '2', '3', ''):
                geom = geom.combine(QgsGeometry.fromPolylineXY(ptlis))         # Achtung: combine ist anders bei QgsGeometry
            else:
                logger.error(f'Die Polygonart {polygonart} kann nicht verarbeitet werden!')
                raise BaseException

        if geom is not None:
            geom_wkb = geom.asWkb()
            logger.debug(f'geom = {geom.asWkt()}')
        else:
            geom_wkb = None

        return geop_wkb, geom_wkb, sohlhoehe, deckelhoehe

    def _get_kante(self, x_geodaten: ElementTree.Element) -> Union[bytes, None]:
        """Liest ein Linienobjekt aus dem Geometriedatenblock

            :param x_geodaten:  xml-Block mit den Geodaten
            :type  x_geodaten:  ElementTree.Element

            :rtpye:             bytes
        """
        if x_geodaten is None:
            return None
        gplis = []
        for x_kante in x_geodaten.findall("Kanten/Kante", self.NS):
            if not gplis:  # nur 1. Kante
                x = _get_float(x_kante.findtext("Start/Rechtswert", None, self.NS))
                y = _get_float(x_kante.findtext("Start/Hochwert", None, self.NS))
                gplis.append([x, y])
            x = _get_float(x_kante.findtext("Ende/Rechtswert", None, self.NS))
            y = _get_float(x_kante.findtext("Ende/Hochwert", None, self.NS))
            gplis.append([x, y])

            mpunkt = _get_float(x_kante.findtext("Mitte", None, self.NS))
            if mpunkt is not None:
                logger.error("Kreisbögen können zurzeit nicht verarbeitet werden")
        for x_polygon in x_geodaten.findall("Polygone/Polygon", self.NS):
            polygonart = x_polygon.findtext("Polygonart", None, self.NS)
            if polygonart != '3':
                logger.error("Innere und äußere Polygone können zurzeit nicht verarbeitet werden.")
            for x_kante in x_polygon.findall("Kante", self.NS):
                if not gplis:  # nur 1. Kante
                    x = _get_float(x_kante.findtext("Start/Rechtswert", None, self.NS))
                    y = _get_float(x_kante.findtext("Start/Hochwert", None, self.NS))
                    gplis.append([x, y])
                x = _get_float(x_kante.findtext("Ende/Rechtswert", None, self.NS))
                y = _get_float(x_kante.findtext("Ende/Hochwert", None, self.NS))
                gplis.append([x, y])

                mpunkt = _get_float(x_kante.findtext("Mitte", None, self.NS))
                if mpunkt is not None:
                    logger.error("Kreisbögen können zurzeit nicht verarbeitet werden")

        # Geoobjekt erstellen
        if gplis:
            ptlis = [QgsPoint(x, y) for x, y in gplis]
            geomobj = QgsGeometry.fromPolyline(ptlis)
            if not geomobj:
                logger.error(f'Fehler bei polyline: {ptlis}')
            geom = geomobj.asWkb()
        else:
            geom = None

        return geom

    def run(self) -> bool:

        self._reftables()
        self._init_mappers()
        if getattr(QKan.config.xml, "import_stamm", True):
            self._schaechte()
            self._auslaesse()
            self._speicher()
            self._haltungen()
            self._wehre()
            self._pumpen()
        if getattr(QKan.config.xml, "import_haus", True):
            self._anschlussleitungen()
        if getattr(QKan.config.xml, "import_zustand", True):
            self._schaechte_untersucht()
            self._untersuchdat_schaechte()
            self._haltungen_untersucht()
            self._untersuchdat_haltung()
            self._anschluss_untersucht()
            self._untersuchdat_anschluss()
            self._untersuchdat_schaechte_daten()
            self._untersuchdat_haltung_daten()
            self._untersuchdat_anschlussleitung_daten()

        if getattr(QKan.config.xml, "import_zustand", True) and not getattr(QKan.config.xml, "import_stamm", True):
            self._schaechte_untersucht_geom()
            self._haltungen_untersucht_geom()
            self._anschluss_untersucht_geom()

        if QKan.config.xml.import_teilbefahrung:
            setbefahrung(self.db_qkan)


        return True

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für ISYBAU-Import füllen"""

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
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau)
                    SELECT ?, ?, ?, ?, ?, ?, ?
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

        # Referenztabelle Pumpe

        params = []
        data = [  # bezeichnung isy he
            ('Offline', 1, 1),
            ('Online Schaltstufen', 2, 2),
            ('Online Kennlinie', 3, 3),
            ('Online Wasserstandsdifferenz', 4, 4),
            ('Ideal', 5, 5),
        ]

        for bezeichnung, he_nr, isybau in data:
            params.append(
                {
                    'bezeichnung': bezeichnung,
                    'he_nr': he_nr,
                    'isybau': isybau,
                }
            )

        sql = """INSERT INTO pumpentypen (bezeichnung,he_nr, isybau)
                                    SELECT
                                        :bezeichnung, :he_nr,
                                        :isybau
                                    WHERE :bezeichnung NOT IN (SELECT bezeichnung FROM pumpentypen)"""
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste pumpentypen", params, many=True):
            return False

        params = []
        data = [  # bezeichnung kuerzel isy m150 m145
            ('in Fließrichtung', 'in', 'O', 'I', 'I'),
            ('gegen Fließrichtung', 'gegen', 'U', 'G', 'G'),
        ]

        for bezeichnung, kuerzel, isybau, m150, m145 in data:
            params.append(
                {
                    'bezeichnung': bezeichnung,
                    'kuerzel': kuerzel,
                    'isybau': isybau,
                    'm150': m150,
                    'm145': m145,
                }
            )

        sql = """INSERT INTO untersuchrichtung (bezeichnung, kuerzel, isybau, m150, m145)
                                            SELECT
                                                :bezeichnung, :kuerzel,
                                                :isybau, :m150, :m145
                                            WHERE :bezeichnung NOT IN (SELECT bezeichnung FROM untersuchrichtung)"""
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste untersuchrichtung", params, many=True):
            return False

        # Referenztabelle Bauwerksarten (ISYBAU) / Knotentypen (QKan)
        # bis zur Umstellung der Referenztabellen auf refdata noch doppelt geführt (s. u.)
        params = []
        data = [
            ('1', 'Pumpwerk', '1', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('2', 'Becken', '2', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('3', 'Behandlungsanlage', '3', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('4', 'Klaeranlage', '4', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('5', 'Auslaufbauwerk', '5', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('6', 'Pumpe', '6', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('7', 'Wehr/Überlauf', '7', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('8', 'Drossel', '8', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('9', 'Schieber', '9', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('10', 'Rechen', '10', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('11', 'Sieb', '11', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('12', 'Versickerungsanlage', '12', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('13', 'Regenwassernutzungsanlage', '13', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
            ('14', 'Einlaufbauwerk', '14', 'bauwerkstyp', 'import_isy', 'QKan-Standard', '2026-0621',),
        ]
        for bezext, bezqkan, kuerzel, subject, modul, kommentar, createdat in data:
            params.append(
                {
                    'bezext': bezext,
                    'bezqkan': bezqkan,
                    'kuerzel': kuerzel,
                    'subject': subject,
                    'modul': modul,
                    'kommentar': kommentar,
                    'createdat': createdat,
                }
            )
        # Einfügen in refdata
        sql = """INSERT INTO refdata (bezext, bezqkan, kuerzel, subject, modul, kommentar, createdat)
            SELECT :bezext, :bezqkan, :kuerzel, :subject, :modul, :kommentar, :createdat
            WHERE :bezqkan NOT IN (SELECT bezqkan FROM refdata)
        """
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste Bauwerkstypen", params, many=True):
            return False

        # Einfügen in alte Referenztabelle knotentyp
        sql = """INSERT INTO knotentypen (knotentyp)
            SELECT :bezqkan
            WHERE :bezqkan NOT IN (SELECT knotentyp FROM knotentypen)
        """
        if not self.db_qkan.sql(sql, "Isybau Import Referenzliste Bauwerkstypen", params, many=True):
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

        sql = "SELECT isybau, bezeichnung FROM pumpentypen"
        subject = "xml_import pumpentypen"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_pump)

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

        sql = "SELECT kuerzel, FIRST_VALUE(bezqkan) OVER (PARTITION BY kuerzel ORDER BY pk) " \
              "FROM refdata WHERE kuerzel IS NOT NULL GROUP BY kuerzel"
        subject = "xml_import bauwerksarten"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_bauwerkstypen)

    def _schaechte(self) -> None:
        def _iter() -> Iterator[Schacht]:
            # .//Schacht/../.. nimmt AbwassertechnischeAnlage
            x_anlagen = self.xml.findall(
                "Datenkollektive/Stammdatenkollektiv/AbwassertechnischeAnlage[Objektart='2']",
                self.NS,
            )

            x_hydraulik = self.xml.find("Datenkollektive/Hydraulikdatenkollektiv/Rechennetz/"
                                        f"HydraulikObjekte",
                                        self.NS)

            logger.debug(f"Anzahl Schächte: {len(x_anlagen)}")

            for x_anlage in x_anlagen:
                knotentyp = x_anlage.findtext("Knoten[KnotenTyp='0']", None, self.NS)
                if knotentyp != None:
                    schnam = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                    # schacht_typ = _get_int(x_anlage.findtext("Knoten/KnotenTyp", None, self.NS), 0)
                    baujahr = _get_int(x_anlage.findtext("Baujahr", None, self.NS))

                    # wird so in QKan nicht verwendet, jh 19.6.2026
                    # if schacht_typ == 1:
                    #     schachttyp = 'Anschlussschacht'
                    # else:
                    #     schachttyp = 'Schacht'

                    x_geometrie = x_anlage.find("Geometrie/Geometriedaten",self.NS)
                    try:
                        geop, geom, sohlhoehe, deckelhohe = self._get_knoten2(x_geometrie)
                    except:
                        logger.error(f'Fehler beim Lesen der Geometrie in _schaechte: {schnam=}')
                        raise BaseException

                    if x_hydraulik is not None:
                        druckdicht = _get_int(x_hydraulik.findtext(
                            f"HydraulikObjekt/[Objektbezeichnung='{schnam}']/Schacht/DruckdichterDeckel",
                            None,
                            self.NS), 0)
                    else:
                        druckdicht = 0

                    yield Schacht(
                        schnam=schnam,
                        sohlhoehe=sohlhoehe,
                        deckelhoehe=deckelhohe,
                        durchm=1.0,  # nicht in Isybau 2013 enthalten
                        entwart=x_anlage.findtext("Entwaesserungsart", None, self.NS),
                        strasse=x_anlage.findtext("Lage/Strassenname", None, self.NS),
                        baujahr=baujahr,
                        schachttyp='Schacht',
                        druckdicht=druckdicht,
                        simstatus=x_anlage.findtext("Status", None, self.NS),
                        material=x_anlage.findtext("Knoten/Schacht/Aufbau/MaterialAufbau", None, self.NS),
                        kommentar=x_anlage.findtext("Kommentar", None, self.NS),
                        geom=geom,
                        geop=geop,
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

            # Schachtdaten für Zustand in dict übernehmen
            if getattr(QKan.config.xml, "import_zustand", True):
                self.schachtdaten[schacht.schnam] = {
                    'durchm': schacht.durchm,
                    'kommentar': schacht.kommentar,
                    'baujahr': schacht.baujahr,
                    'xsch': None,
                    'ysch': None,
                    'geop': schacht.geop,
                }

            params = {'schnam': schacht.schnam, 'sohlhoehe': schacht.sohlhoehe, 'deckelhoehe': schacht.deckelhoehe,
                      'durchm': schacht.durchm, 'entwart': entwart, 'strasse': schacht.strasse,
                      'baujahr': schacht.baujahr, 'schachttyp': schacht.schachttyp,
                      'druckdicht': schacht.druckdicht, 'simstatus': simstatus, 'material': material,
                      'kommentar': schacht.kommentar, 'geom': schacht.geom, 'geop': schacht.geop,
                      'epsg': QKan.config.epsg}

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

    def _schaechte_untersucht(self) -> None:
        def _iter() -> Iterator[Schacht_untersucht]:

            x_zustandsdaten = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv",
                self.NS,
            )

            for x_zustandsdat in x_zustandsdaten:

                x_zustaende = x_zustandsdat.findall(
                    "InspizierteAbwassertechnischeAnlage/[Anlagentyp='3']",
                    self.NS,
                )

                schnam = None
                untersuchtag = None
                untersucher = None
                wetter = None
                strasse = None
                baujahr = None
                bewertungsart = None
                bewertungstag = None
                datenart = self.datenart

                for x_zustand in x_zustaende:
                    schnam = x_zustand.findtext("Objektbezeichnung", None, self.NS)
                    baujahr = _get_int(x_zustand.findtext("Baujahr", None, self.NS))
                    strasse = x_zustand.findtext("Lage/Strassenname", None, self.NS)

                    for _schacht in x_zustand.findall("OptischeInspektion", self.NS):
                        untersuchtag = _schacht.findtext("Inspektionsdatum", None, self.NS)
                        untersucher = _schacht.findtext("NameUntersucher", None, self.NS)
                        wetter = _schacht.findtext("Wetter", None, self.NS)
                        auftragsbezeichnung = _schacht.findtext("Auftragskennung", None, self.NS)

                        for _schachtz in _schacht.findall("Knoten/Bewertung", self.NS):
                            bewertungsart = _schachtz.findtext("Bewertungsverfahren", None, self.NS)
                            bewertungstag = _schachtz.findtext("Bewertungsdatum", None, self.NS)

                            yield Schacht_untersucht(
                                schnam=schnam,
                                untersuchtag=untersuchtag,
                                untersucher=untersucher,
                                wetter=wetter,
                                strasse=strasse,
                                bewertungsart=bewertungsart,
                                bewertungstag=bewertungstag,
                                datenart=datenart,
                                auftragsbezeichnung=auftragsbezeichnung,
                            )

        for schacht_untersucht in _iter():

            wetter = self.db_qkan.get_from_mapper(
                schacht_untersucht.wetter,
                self.mapper_wetter,
                'schaechte_untersucht',
                'wetter',
                'bezeichnung',
                'isybau',
                'bemerkung',
            )

            # Datensatz einfügen

            if pdat := self.schachtdaten.get(schacht_untersucht.schnam, {}):
                params = {'schnam': schacht_untersucht.schnam,
                          'untersuchtag': schacht_untersucht.untersuchtag,
                          'untersucher': schacht_untersucht.untersucher, 'wetter': wetter,
                          'auftragsbezeichnung': schacht_untersucht.auftragsbezeichnung,
                          'strasse': schacht_untersucht.strasse,
                          'bewertungsart': schacht_untersucht.bewertungsart,
                          'bewertungstag': schacht_untersucht.bewertungstag,
                          'datenart': schacht_untersucht.datenart,
                          'epsg': QKan.config.epsg} \
                         | pdat

            else:
                logger.warning(f'Untersuchter Schacht {schacht_untersucht.schnam} fehlt in den Stammdaten')
                params = {'schnam': schacht_untersucht.schnam,
                          'untersuchtag': schacht_untersucht.untersuchtag,
                          'untersucher': schacht_untersucht.untersucher, 'wetter': wetter,
                          'auftragsbezeichnung': schacht_untersucht.auftragsbezeichnung,
                          'strasse': schacht_untersucht.strasse,
                          'bewertungsart': schacht_untersucht.bewertungsart,
                          'bewertungstag': schacht_untersucht.bewertungstag,
                          'datenart': schacht_untersucht.datenart,
                          'epsg': QKan.config.epsg}

            # logger.debug(f'isyporter.import - insertdata:\ntabnam: schaechte_untersucht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte_untersucht",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _untersuchdat_schaechte(self) -> None:
        def _iter() -> Iterator[Untersuchdat_schacht]:

            ordner_bild = self.ordner_bild

            x_zustandsdaten = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv",
                self.NS,
            )

            for x_zustandsdat in x_zustandsdaten:

                x_anlagen = x_zustandsdat.findall(
                    "InspizierteAbwassertechnischeAnlage",
                    self.NS,
                )

                logger.debug(f"Anzahl Untersuchungsdaten Schacht: {len(x_anlagen)}")

                for x_anlage in x_anlagen:

                    untersuchsch = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                    untersuchtag = x_anlage.findtext("OptischeInspektion/Inspektionsdatum", None, self.NS)
                    inspektionslaenge = _get_float(x_anlage.findtext(
                        "OptischeInspektion/Knoten/Inspektionsdaten/KZustand[InspektionsKode='DDB']"
                        "[Streckenschaden='B']/VertikaleLage",
                        None, self.NS))

                    kennung = _get_int(x_anlage.findtext("OptischeInspektion/Auftragskennung", None, self.NS))

                    for _untersuchdat_schacht in x_anlage.findall("OptischeInspektion/Knoten/Inspektionsdaten/KZustand", self.NS):

                        #id = _get_int(_untersuchdat_schacht.findtext("Index", None, self.NS))
                        videozaehler = _get_int(_untersuchdat_schacht.findtext("Videozaehler", None, self.NS))
                        timecode = _untersuchdat_schacht.findtext("Timecode", None, self.NS)
                        kuerzel = _untersuchdat_schacht.findtext("InspektionsKode", None, self.NS)
                        charakt1 = _untersuchdat_schacht.findtext("Charakterisierung1", None, self.NS)
                        charakt2 = _untersuchdat_schacht.findtext("Charakterisierung2", None, self.NS)
                        quantnr1 = _get_float(_untersuchdat_schacht.findtext("Quantifizierung1Numerisch", None, self.NS))
                        quantnr2 = _get_float(_untersuchdat_schacht.findtext("Quantifizierung2Numerisch", None, self.NS))
                        streckenschaden = _untersuchdat_schacht.findtext("Streckenschaden", None, self.NS)
                        streckenschaden_lfdnr = _get_int(_untersuchdat_schacht.findtext("StreckenschadenLfdNr", None, self.NS))
                        pos_von = _get_int(_untersuchdat_schacht.findtext("PositionVon", None, self.NS))
                        pos_bis = _get_int(_untersuchdat_schacht.findtext("PositionBis", None, self.NS))
                        vertikale_lage = _get_float(_untersuchdat_schacht.findtext("VertikaleLage", None, self.NS))
                        bereich = _untersuchdat_schacht.findtext("Schachtbereich", None, self.NS)

                        foto_dateiname = _untersuchdat_schacht.findtext("Fotodatei", None, self.NS)
                        #if _datei is not None and self.ordner_bild is not None:
                        #    foto_dateiname = os.path.join(self.ordner_bild, _datei)
                        #else:
                        #    foto_dateiname = None

                        ZD = _get_int(_untersuchdat_schacht.findtext("Klassifizierung/Dichtheit/SKDvAuto", None, self.NS))
                        ZS = _get_int(_untersuchdat_schacht.findtext("Klassifizierung/Betriebssicherheit/SKSvAuto", None, self.NS))
                        ZB = _get_int(_untersuchdat_schacht.findtext("Klassifizierung/Standsicherheit/SKBvAuto", None, self.NS))

                        # x_filme = self.xml.findall(
                        #     "Datenkollektive/Zustandsdatenkollektiv/Filme"
                        #     f"/FilmObjekte/FilmObjekt/[Objektbezeichnung='{untersuchsch}']/../..",
                        #     self.NS,
                        # )
                        # logger.debug(f"Anzahl Filme in Untersuchdat_schacht zu Schacht {untersuchsch}: {len(x_filme)}")
                        #
                        # for x_film in x_filme:
                        #     for _untersuchdat_schacht in x_film.findall("Film", self.NS):
                        #
                        #         _datei = _untersuchdat_schacht.findtext("Filmname", None, self.NS)
                        #         if _datei is not None and self.ordner_bild is not None:
                        #             film_dateiname = os.path.join(self.ordner_video, _datei)
                        #         else:
                        #             film_dateiname = None

                        yield Untersuchdat_schacht(
                        untersuchsch = untersuchsch,
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
                        ordner_bild = ordner_bild,
                        ZD=ZD,
                        ZS=ZS,
                        ZB=ZB,
                        )

        untersuchdat_schacht = None
        for untersuchdat_schacht in _iter():

            params = {'untersuchsch': untersuchdat_schacht.untersuchsch,
                      'untersuchtag': untersuchdat_schacht.untersuchtag,
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
                      'foto_dateiname': untersuchdat_schacht.foto_dateiname,
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

        # for untersuchdat_schacht in _iter2():
        #     if not self.db_qkan.sql(
        #         "UPDATE untersuchdat_schacht SET film_dateiname=?"
        #         " WHERE  untersuchsch= ?",
        #         "xml_import untersuchsch [2a]",
        #         parameters=[untersuchdat_schacht.film_dateiname, untersuchdat_schacht.untersuchsch],
        #     ):
        #         return None
        #
        if untersuchdat_schacht is not None:
            Schadenstexte.setschadenstexte_schaechte(self.db_qkan)

    def _untersuchdat_schaechte_daten(self) -> None:
        # TODO: für Fotos auch ergänzan ab Isybau 2020!
        def _iter() -> Iterator[Untersuchdat_daten]:
            x_zustandsdaten = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv",
                self.NS,
            )

            for x_zustandsdat in x_zustandsdaten:

                x_anlagen = x_zustandsdat.findall(
                    "InspizierteAbwassertechnischeAnlage/[Anlagentyp='3']",
                    self.NS,
                )

                logger.debug(f"Anzahl Untersuchungsdaten Haltung: {len(x_anlagen)}")

                liste = {}

                for x_anlage in x_anlagen:
                    untersuchsch = x_anlage.findtext("Objektbezeichnung", None, self.NS)

                    untersuchtag = x_anlage.findtext("OptischeInspektion/Inspektionsdatum", None, self.NS)

                    id = _get_int(x_anlage.findtext("OptischeInspektion/Auftragskennung", None, self.NS))

                    liste[untersuchsch] = [untersuchtag, id]


                filme = x_zustandsdat.findall("Filme/Film", self.NS, )

                for film in filme:
                    bezeichnungen = film.findtext("FilmObjekte/FilmObjekt/Objektbezeichnung", None, self.NS)
                    _ = film.findtext("FilmObjekte/FilmObjekt/Inspektionsrichtung", None, self.NS)
                    if _ == "O":
                        untersuchrichtung = "in Fließrichtung"
                    elif _ == "U":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.warning(f"Haltung untersucht: Fehlerhafter Wert in Feld Inspektionsrichtung: {_}")
                        untersuchrichtung = None
                    x = _get_int(film.findtext("Auftragskennung", None, self.NS))
                    if bezeichnungen in liste and x == liste[bezeichnungen][1]:

                        typ = film.findtext("FilmObjekte/FilmObjekt/Typ", None, self.NS)
                        if typ == '1':
                            objekt = "Haltung"
                        elif typ == '2':
                            objekt = "Anschlussleitung"
                        elif typ == '3':
                            objekt = "Schacht"
                        elif typ == '4':
                            objekt = "Bauwerk"

                        if typ == "2":

                            _datei = film.findtext("Filmname", None, self.NS)

                            # relativer pfad mit einfügen in datei
                            # relativer pfad mit einfügen in datei
                            filmpfad = film.findtext("Filmpfad", None, self.NS)
                            if _datei is not None and filmpfad is not None:
                                filmdatei = os.path.join(filmpfad, _datei)
                            else:
                                filmdatei = _datei

                            yield Untersuchdat_daten(
                                untersuchsch=bezeichnungen,
                                untersuchtag=liste[bezeichnungen][0],
                                untersuchrichtung=untersuchrichtung,
                                datei=filmdatei,
                                objekt=objekt,
                            )

        for untersuchdat_daten in _iter():

            params = {'name': untersuchdat_daten.untersuchsch, 'untersuchtag': untersuchdat_daten.untersuchtag,
                      'untersuchrichtung': untersuchdat_daten.untersuchrichtung,
                      'datei': untersuchdat_daten.datei, 'objekt': untersuchdat_daten.objekt}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: videos\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="videos",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _auslaesse(self) -> None:
        def _iter1() -> Iterator[Schacht]:
            """Hydraulikdaten zu Schacht einlesen und in self.hydraulikdaten einfügen"""

            x_hydrauliken = self.xml.findall("Datenkollektive/Hydraulikdatenkollektiv/Rechennetz/"
                                          "HydraulikObjekte/HydraulikObjekt/FreierAuslass",
                                           self.NS)
            logger.debug(f"Anzahl HydraulikObjekte_Schaechte: {len(x_hydrauliken)}")

            for x_hydraulik in x_hydrauliken:
                schnam = x_hydraulik.findtext("../Objektbezeichung", None, self.NS)

                _auslasstyp = x_hydraulik.findtext("Freier Auslass Typ", None, self.NS)


                _randbedingung = x_hydraulik.findtext("Randbedingung", None, self.NS)

                if _auslasstyp == "1" and _randbedingung == "0" :
                    auslasstyp = "freier Auslass"
                elif _randbedingung == "1":
                    auslasstyp = "konstant"
                elif _randbedingung == "2":
                    auslasstyp = "Tiede"
                else:
                    auslasstyp = "freier Auslass"
                    logger.warnung(f"Kein Auslasstyp gefunden {_randbedingung=}, {_auslasstyp=}")

                yield Schacht(
                    schanm=schnam,
                    auslasstyp=auslasstyp,
                )

        def _iter() -> Iterator[Schacht]:
            # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage
            x_anlagen = self.xml.findall(
                "Datenkollektive/Stammdatenkollektiv/AbwassertechnischeAnlage[Objektart='2']", self.NS,)

            logger.debug(f"Anzahl Ausläufe: {len(x_anlagen)}")

            for x_anlage in x_anlagen:
                bauwerkstyp = x_anlage.findtext("Knoten[KnotenTyp='2']/Bauwerk/Bauwerkstyp", None, self.NS)
                if bauwerkstyp == '5':
                    name, knoten_typ, xsch, ysch, sohlhoehe = self._consume_smp_block(x_anlage)

                    baujahr = _get_int(x_anlage.findtext("Baujahr", None, self.NS))

                    yield Schacht(
                        schnam=name,
                        xsch=xsch,
                        ysch=ysch,
                        sohlhoehe=sohlhoehe,
                        deckelhoehe=_get_float(
                            x_anlage.findtext(
                                "Geometrie/Geometriedaten/Knoten"
                                "/Punkt[PunktattributAbwasser='GOK']/Punkthoehe",
                                None,
                                self.NS,
                            )
                        ),
                        baujahr=baujahr,
                        durchm=0.5,
                        entwart=x_anlage.findtext("Entwaesserungsart", None, self.NS),
                        strasse=x_anlage.findtext("Lage/Strassenname", None, self.NS),
                        knotentyp='Auslaufbauwerk',
                        schachttyp='Auslass',
                        material=x_anlage.findtext("Knoten/Bauwerk/Auslaufbauwerk/Material", None, self.NS),
                        simstatus=x_anlage.findtext("Status", None, self.NS),
                        kommentar=x_anlage.findtext("Kommentar", None, self.NS),
                    )

        for hydraulik in _iter1():
            self.hydraulikdaten[hydraulik.schnam] = {
                'auslasstyp':    hydraulik.auslasstyp,
            }

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

            if (pdat := self.hydraulikdaten.get(auslass.schnam, {})) == {}:
                logger.info(f'Haltung {auslass.schnam} fehlt in den Hydraulikdaten')
                pdat = {
                    'auslastyp':    None,
                }

            params = {'schnam': auslass.schnam, 'xsch': auslass.xsch, 'ysch': auslass.ysch,
                      'sohlhoehe': auslass.sohlhoehe, 'deckelhoehe': auslass.deckelhoehe, 'baujahr': auslass.baujahr,
                      'durchm': auslass.durchm, 'entwart': entwart, 'strasse': auslass.strasse, 'simstatus': simstatus,
                      'kommentar': auslass.kommentar, 'material': auslass.material,
                      'schachttyp': auslass.schachttyp, 'knotentyp': auslass.knotentyp,
                      'epsg': QKan.config.epsg} | pdat

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
            x_anlagen = self.xml.findall(
                "Datenkollektive/Stammdatenkollektiv/AbwassertechnischeAnlage[Objektart='2']",
                self.NS,
            )

            logger.debug(f"Anzahl Becken: {len(x_anlagen)}")

            for x_anlage in x_anlagen:
                bauwerkstyp = x_anlage.findtext("Knoten[KnotenTyp='2']/Bauwerk/Bauwerkstyp", None, self.NS)
                if bauwerkstyp in ('3', '4', '12', '13',):
                    name = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                    baujahr = _get_int(x_anlage.findtext("Baujahr", None, self.NS))

                    smp = x_anlage.find(
                        "Geometrie/Geometriedaten/Knoten/Punkt[PunktattributAbwasser='KOP']",
                        self.NS,
                    )

                    if smp is None:
                        fehlermeldung(
                            "Fehler beim XML-Import: Speicher",
                            f'Keine Geometrie "KOP" für Becken {name}',
                        )
                        xsch, ysch, sohlhoehe = (0.0,) * 3
                    else:
                        xsch = _get_float(smp.findtext("Rechtswert", None, self.NS))
                        ysch = _get_float(
                            smp.findtext("Hochwert", None, self.NS)
                        )
                        sohlhoehe = _get_float(smp.findtext("Punkthoehe", None, self.NS))

                    yield Schacht(
                        schnam=name,
                        xsch=xsch,
                        ysch=ysch,
                        sohlhoehe=sohlhoehe,
                        deckelhoehe=_get_float(
                            x_anlage.findtext(
                                "Geometrie/Geometriedaten/Knoten"
                                "/Punkt[PunktattributAbwasser='DMP']/Punkthoehe",
                                None,
                                self.NS,
                            )
                        ),
                        baujahr=baujahr,
                        durchm=0.5,
                        entwart=x_anlage.findtext("Entwaesserungsart", None, self.NS),
                        strasse=x_anlage.findtext("Lage/Strassenname", None, self.NS),
                        knotentyp=bauwerkstyp,
                        simstatus=x_anlage.findtext("Status", None, self.NS),
                        kommentar=x_anlage.findtext("Kommentar", None, self.NS),
                    )

        for speicher in _iter():
            # Simstatus
            simstatus = self.db_qkan.get_from_mapper(
                speicher.simstatus,
                self.mapper_simstatus,
                'Speicher',
                'simulationsstatus',
                'bezeichnung',
                'isybau',
                'kommentar',
                'kuerzel',
            )

            # Unbekannte Knotentypen nicht ergänzen
            knotentyp = self.db_qkan.get_from_mapper(
                speicher.knotentyp,
                self.mapper_bauwerkstypen,
                'Speicher',
            )

            params = {'schnam': speicher.schnam, 'xsch': speicher.xsch, 'ysch': speicher.ysch,
                      'sohlhoehe': speicher.sohlhoehe, 'deckelhoehe': speicher.deckelhoehe, 'baujahr': speicher.baujahr,
                      'durchm': speicher.durchm, 'strasse': speicher.strasse,  'entwart': speicher.entwart,
                      'simstatus': simstatus, 'kommentar': speicher.kommentar,
                      'schachttyp': 'Speicher', 'knotentyp': knotentyp, 'epsg': QKan.config.epsg}

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
        """Import der Haltungsdaten"""

        def _iter1() -> Iterator[Haltung]:
            """Hydraulikdaten zu Haltungen einlesen und in self.hydraulikdaten einfügen"""

            x_hydrauliken = self.xml.findall("Datenkollektive/Hydraulikdatenkollektiv/Rechennetz/"
                                          "HydraulikObjekte/HydraulikObjekt/Haltung",
                                           self.NS)
            logger.debug(f"Anzahl HydraulikObjekte_Haltungen: {len(x_hydrauliken)}")

            for x_hydraulik in x_hydrauliken:
                haltnam = x_hydraulik.findtext("../Objektbezeichnung", None, self.NS)
                _rauansatz = x_hydraulik.findtext("Rauigkeitsansatz", None, self.NS)
                if _rauansatz == "1":
                    ks = _get_float(x_hydraulik.findtext("RauigkeitsbeiwertKb", None, self.NS))
                elif _rauansatz == "2":
                    ks = _get_float(x_hydraulik.findtext("RauigkeitsbeiwertKst", None, self.NS))
                else:
                    ks = None
                    logger.warning("Fehler im XML-Import von HydraulikObjekte_Haltungen",
                                   f"Ungültiger Wert für Rauigkeitsansatz {_rauansatz} in Haltung {haltnam}",
                                   )

                laengehyd = _get_float(x_hydraulik.findtext("Berechnungslaenge", None, self.NS))

                yield Haltung(
                    haltnam=haltnam,
                    laengehyd=laengehyd,
                    ks=ks,
                )

        def _iter() -> Iterator[Haltung]:

            x_anlagen = self.xml.findall(
                "Datenkollektive/Stammdatenkollektiv/AbwassertechnischeAnlage/[Objektart='1']", self.NS
            )
            logger.debug(f"Anzahl Haltungen: {len(x_anlagen)}")

            for x_anlage in x_anlagen:
                schoben = schunten = hoehe = breite = laenge = material = sohleoben = \
                sohleunten = deckeloben = deckelunten = profilnam = \
                ks = aussendurchmesser = profilauskleidung = innenmaterial = None

                haltnam = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                baujahr = _get_int(x_anlage.findtext("Baujahr", None, self.NS), None)
                entwart = x_anlage.findtext("Entwaesserungsart", None, self.NS)
                strasse = x_anlage.findtext("Lage/Strassenname", None, self.NS)
                simstatus = x_anlage.findtext("Status", None, self.NS)
                kommentar = x_anlage.findtext("Kommentar", None, self.NS)

                x_kante = x_anlage.find("Kante", self.NS)
                if x_kante is not None:
                    schoben = x_kante.findtext("KnotenZulauf", None, self.NS)
                    schunten = x_kante.findtext("KnotenAblauf", None, self.NS)
                    sohleoben = _get_float(x_kante.findtext("SohlhoeheZulauf", None, self.NS))
                    sohleunten = _get_float(x_kante.findtext("SohlhoeheAblauf", None, self.NS))
                    laenge = _get_float(x_kante.findtext("Laenge", None, self.NS))
                    material = x_kante.findtext("Material", None, self.NS)

                    x_profil = x_kante.find("Profil", self.NS)
                    if x_profil is not None:
                        aussendurchmesser = _get_float(x_profil.findtext("Aussendurchmesser", None, self.NS))
                        profilnam = x_profil.findtext("Profilart", None, self.NS)
                        hoehe = _get_float(x_profil.findtext("Profilhoehe", None, self.NS))
                        breite = _get_float(x_profil.findtext("Profilbreite", None, self.NS))

                    x_haltung = x_kante.find("Haltung", self.NS)
                    if x_haltung is not None:
                        profilauskleidung = x_haltung.findtext("Auskleidung", None, self.NS)
                        innenmaterial = x_haltung.findtext("MaterialAuskleidung", None, self.NS)

                # hier ergännzen mit dem fall das x,y unter Polygone steht!!
                # Haltungen können alternativ als Kanten oder als Polygone vorkommen.

                x_geodaten = x_anlage.find("Geometrie/Geometriedaten", self.NS)
                geom = self._get_kante(x_geodaten)

                yield Haltung(
                    haltnam=haltnam,
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
                    entwart=entwart,
                    strasse=strasse,
                    simstatus=simstatus,
                    kommentar=kommentar,
                    aussendurchmesser=aussendurchmesser,
                    profilauskleidung=profilauskleidung,
                    innenmaterial=innenmaterial,
                    geom=geom,
                )


        # 1. Teil: Vorab werden die Hydraulikdaten in das dict "hydraulikdaten" geschrieben
        for hydraulik in _iter1():
            self.hydraulikdaten[hydraulik.haltnam] = {
                'laengehyd':    hydraulik.laengehyd,
                'ks':           hydraulik.ks,
            }

        # 2. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
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

            # Haltungsdaten für Zustand in dict übernehmen
            if getattr(QKan.config.xml, "import_zustand", True):
                self.haltungsdaten[haltung.haltnam] = {
                    'schoben': haltung.schoben,
                    'schunten': haltung.schunten,
                    'hoehe': haltung.hoehe,
                    'breite': haltung.breite,
                    'laenge': haltung.laenge,
                    'kommentar': haltung.kommentar,
                    'baujahr': haltung.baujahr,
                    'geom': haltung.geom,
                }

            if (pdat := self.hydraulikdaten.get(haltung.haltnam, {})) == {}:
                logger.info(f'Haltung {haltung.haltnam} fehlt in den Hydraulikdaten')
                pdat = {
                    'laengehyd':    None,
                    'ks':           None,
                }

            params = {'haltnam': haltung.haltnam,
                      'schoben': haltung.schoben,
                      'schunten': haltung.schunten,
                      'hoehe': haltung.hoehe,
                      'breite': haltung.breite,
                      'laenge': haltung.laenge,
                      'sohleoben': haltung.sohleoben,
                      'sohleunten': haltung.sohleunten,
                      'baujahr': haltung.baujahr,
                      'material': material,
                      'profilnam': profilnam,
                      'entwart': entwart,
                      'strasse': haltung.strasse,
                      'simstatus': simstatus,
                      'aussendurchmesser': haltung.aussendurchmesser,
                      'profilauskleidung': haltung.profilauskleidung,
                      'innenmaterial': haltung.innenmaterial,
                      'kommentar': haltung.kommentar,
                      'epsg': QKan.config.epsg,
                      'geom': haltung.geom}\
                     | pdat

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


    #Haltung_untersucht
    def _haltungen_untersucht(self) -> None:
        """Einlesen der untersuchten Haltungen"""
        def _iter() -> Iterator[Haltung_untersucht]:
            x_anlagen = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv/InspizierteAbwassertechnischeAnlage/[Anlagentyp='1']",
                self.NS,
            )
            logger.debug(f"Anzahl Haltungen_unteruscht: {len(x_anlagen)}")

            untersuchtag = ""
            untersucher = ""
            wetter = None
            bewertungsart = None
            bewertungstag = ""
            inspektionslaenge = None
            untersuchrichtung = None
            datenart = self.datenart

            for x_anlage in x_anlagen:
                haltnam = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                strasse = x_anlage.findtext("Lage/Strassenname", None, self.NS)

                untersuchtag = x_anlage.findtext("OptischeInspektion/Inspektionsdatum", None, self.NS)
                untersucher = x_anlage.findtext("OptischeInspektion/NameUntersucher", None, self.NS)
                wetter = x_anlage.findtext("OptischeInspektion/Wetter", None, self.NS)
                auftragsbezeichnung = x_anlage.findtext("OptischeInspektion/Auftragskennung", None, self.NS)

                inspektionslaenge = _get_float(x_anlage.findtext("OptischeInspektion/Rohrleitung/Inspektionslaenge", None, self.NS))
                _ = x_anlage.findtext("OptischeInspektion/Rohrleitung/Inspektionsrichtung", None, self.NS)
                if _ == "O":
                    untersuchrichtung = "in Fließrichtung"
                elif _ == "U":
                    untersuchrichtung = "gegen Fließrichtung"
                else:
                    logger.warning(f"Haltung untersucht: Fehlerhafter Wert in Feld Inspektionsrichtung: {_} "
                                   f"bei Haltung {haltnam}, untersucht am: {untersuchtag}")
                    untersuchrichtung = None

                _val = x_anlage.findtext("OptischeInspektion/Rohrleitung/BezugspunktLage", None, self.NS)
                if _val == '2' or not _val:
                    bezugspunkt = enums.UntersuchBezugpunkt.ROHRANFANG.value
                else:
                    bezugspunkt = enums.UntersuchBezugpunkt.GERINNEMITTELPUNKT.value

                for _haltungz in x_anlage.findall("OptischeInspektion/Rohrleitung/Bewertung", self.NS):
                    bewertungsart = _haltungz.findtext("OptischeInspektion/Bewertungsverfahren", None, self.NS)
                    bewertungstag = _haltungz.findtext("OptischeInspektion/Bewertungsdatum", None, self.NS)

                yield Haltung_untersucht(
                    haltnam=haltnam,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    wetter=wetter,
                    laenge= inspektionslaenge,
                    untersuchrichtung=untersuchrichtung,
                    strasse=strasse,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                    bezugspunkt=bezugspunkt,
                    auftragsbezeichnung=auftragsbezeichnung,
                )

        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben
        for haltung_untersucht in _iter():

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

            if (pdat := self.haltungsdaten.get(haltung_untersucht.haltnam, {})):

                pdat['laenge'] = haltung_untersucht.laenge


                params = {'haltnam': haltung_untersucht.haltnam,
                          'untersuchtag': haltung_untersucht.untersuchtag,
                          'untersucher': haltung_untersucht.untersucher,
                          'wetter': haltung_untersucht.wetter,
                          'auftragsbezeichnung': haltung_untersucht.auftragsbezeichnung,
                          'untersuchrichtung': haltung_untersucht.untersuchrichtung,
                          'strasse': haltung_untersucht.strasse,
                          'bewertungsart': haltung_untersucht.bewertungsart,
                          'bewertungstag': haltung_untersucht.bewertungstag,
                          'datenart': haltung_untersucht.datenart,
                          'bezugspunkt': haltung_untersucht.bezugspunkt,
                          'epsg': QKan.config.epsg,}\
                         | pdat

            else:
                logger.warning(f'Untersuchte Haltung {haltung_untersucht.haltnam} fehlt in den Stammdaten')
                #continue
                params = {'haltnam': haltung_untersucht.haltnam,
                          'untersuchtag': haltung_untersucht.untersuchtag,
                          'untersucher': haltung_untersucht.untersucher,
                          'wetter': haltung_untersucht.wetter,
                          'auftragsbezeichnung': haltung_untersucht.auftragsbezeichnung,
                          'untersuchrichtung': haltung_untersucht.untersuchrichtung,
                          'strasse': haltung_untersucht.strasse,
                          'bewertungsart': haltung_untersucht.bewertungsart,
                          'bewertungstag': haltung_untersucht.bewertungstag,
                          'datenart': haltung_untersucht.datenart,
                          'bezugspunkt': haltung_untersucht.bezugspunkt,
                          'epsg': QKan.config.epsg, }


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

    def _untersuchdat_haltung(self) -> None:
        def _iter() -> Iterator[Untersuchdat_haltung]:
            x_anlagen = self.xml.findall(
               "Datenkollektive/Zustandsdatenkollektiv/InspizierteAbwassertechnischeAnlage/[Anlagentyp='1']",
               self.NS,
            )

            logger.debug(f"Anzahl Untersuchungsdaten Haltung: {len(x_anlagen)}")

            ordner_bild = self.ordner_bild
            ordner_video = self.ordner_video

            name = ""
            untersuchrichtung = ""
            schoben = ""
            schunten = ""
            inspektionslaenge = 0.0
            videozaehler = 0
            station = 0.0
            timecode = None
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


            for x_anlage in x_anlagen:
                name = x_anlage.findtext("Objektbezeichnung", None, self.NS)

                untersuchtag = x_anlage.findtext("OptischeInspektion/Inspektionsdatum", None, self.NS)
                for _untersuchdat_haltung in x_anlage.findall("OptischeInspektion/Rohrleitung", self.NS):

                    #id = _get_int(_untersuchdat_haltung.findtext("../Auftragskennung", None, self.NS))

                    _ = _untersuchdat_haltung.findtext("Inspektionsrichtung", None, self.NS)
                    if _ == "O":
                        untersuchrichtung = "in Fließrichtung"
                    elif _ == "U":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.warning(f"Untersuchungsdaten Haltung: Fehlerhafter Wert in Feld Inspektionsrichtung: {_}")
                        untersuchrichtung = None

                    inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("Inspektionslaenge", None, self.NS))
                    if inspektionslaenge == 0.0:
                        inspektionslaenge = _get_float(_untersuchdat_haltung.findtext("Inspektionsdaten/RZustand[InspektionsKode='BCE'][Charakterisierung1='XP']/Station", None, self.NS))


                    schoben = _untersuchdat_haltung.findtext("RGrunddaten/KnotenZulauf", None, self.NS)
                    schunten = _untersuchdat_haltung.findtext("RGrunddaten/KnotenAblauf", None, self.NS)

                    for _untersuchdat in _untersuchdat_haltung.findall("Inspektionsdaten/RZustand", self.NS):

                        videozaehler = _get_int(_untersuchdat.findtext("Videozaehler", None, self.NS))
                        station = _get_float(_untersuchdat.findtext("Station", None, self.NS))
                        timecode = _untersuchdat.findtext("Timecode", None, self.NS)
                        kuerzel = _untersuchdat.findtext("InspektionsKode", None, self.NS)
                        charakt1 = _untersuchdat.findtext("Charakterisierung1", None, self.NS)
                        charakt2 = _untersuchdat.findtext("Charakterisierung2", None, self.NS)
                        quantnr1 = _get_float(_untersuchdat.findtext("Quantifizierung1Numerisch", None, self.NS))
                        quantnr2 = _get_float(_untersuchdat.findtext("Quantifizierung2Numerisch", None, self.NS))
                        streckenschaden = _untersuchdat.findtext("Streckenschaden", None, self.NS)
                        streckenschaden_lfdnr = _get_int(_untersuchdat.findtext("StreckenschadenLfdNr", None, self.NS))
                        pos_von = _get_int(_untersuchdat.findtext("PositionVon", None, self.NS))
                        pos_bis = _get_int(_untersuchdat.findtext("PositionBis", None, self.NS))

                        foto_dateiname = _untersuchdat.findtext("Fotodatei", None, self.NS)
                        #if _datei is not None and self.ordner_bild is not None:
                        #    foto_dateiname = os.path.join(self.ordner_bild, _datei)
                        #else:
                        #    foto_dateiname = None

                        ZD = _get_int(_untersuchdat.findtext("Klassifizierung/Dichtheit/SKDvAuto", None, self.NS))
                        ZS = _get_int(_untersuchdat.findtext("Klassifizierung/Betriebssicherheit/SKSvAuto", None, self.NS))
                        ZB = _get_int(_untersuchdat.findtext("Klassifizierung/Standsicherheit/SKBvAuto", None, self.NS))


                        yield Untersuchdat_haltung(
                        untersuchhal=name,
                        untersuchrichtung=untersuchrichtung,
                        schoben=schoben,
                        schunten=schunten,
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
                        ZS=ZS,
                        ZB=ZB,

            )

        # def _iter2() -> Iterator[Untersuchdat_haltung]:
        #         x_filme = self.xml.findall(
        #             "Datenkollektive/Zustandsdatenkollektiv/Filme/Film/Filmname/../..",
        #             self.NS,
        #         )
        #         logger.debug(f"Anzahl Untersuchdat_haltung: {len(x_filme)}")
        #
        #         film_dateiname = ""
        #         for x_film in x_filme:
        #             for _untersuchdat_haltung in x_film.findall("Film/FilmObjekte/..", self.NS):
        #
        #                 name = _untersuchdat_haltung.findtext("FilmObjekte/FilmObjekt/Objektbezeichnung", None, self.NS)
        #
        #                 _datei = _untersuchdat_haltung.findtext("Filmname", None, self.NS)
        #                 if _datei is not None and self.ordner_bild is not None:
        #                     film_dateiname = os.path.join(self.ordner_video, _datei)
        #                 else:
        #                     film_dateiname = None
        #
        #                 # bandnr = _get_int(_untersuchdat_haltung.findtext("Videoablagereferenz", None, self.NS))
        #
        #                 yield Untersuchdat_haltung(
        #                     untersuchhal=name,
        #                     film_dateiname=film_dateiname,
        #                     # bandnr=bandnr
        #                 )

        untersuchdat_haltung = None
        for untersuchdat_haltung in _iter():

            params = {'untersuchhal': untersuchdat_haltung.untersuchhal,
                      'untersuchrichtung': untersuchdat_haltung.untersuchrichtung,
                      'schoben': untersuchdat_haltung.schoben, 'schunten': untersuchdat_haltung.schunten,
                       'untersuchtag': untersuchdat_haltung.untersuchtag,
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
                         'ZD': untersuchdat_haltung.ZD,
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

        # for untersuchdat_haltung in _iter2():
        #
        #     if not self.db_qkan.sql(
        #         "UPDATE untersuchdat_haltung SET film_dateiname=?"
        #         " WHERE  untersuchhal= ?",
        #         "xml_import untersuchhal [2a]",
        #         parameters=[untersuchdat_haltung.film_dateiname,untersuchdat_haltung.untersuchhal],
        #     ):
        #         return None
        #
        # self.db_qkan.commit()

        if untersuchdat_haltung is not None:
            Schadenstexte.setschadenstexte_haltungen(self.db_qkan)

    def _untersuchdat_haltung_daten(self):
        # TODO: für Fotos auch ergänzan ab Isybau 2020!
        def _iter() -> Iterator[Untersuchdat_daten]:
            x_zustandsdaten = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv",
                self.NS,
            )

            for x_zustandsdat in x_zustandsdaten:

                x_anlagen = x_zustandsdat.findall(
                    "InspizierteAbwassertechnischeAnlage/[Anlagentyp='1']",
                    self.NS,
                )

                logger.debug(f"Anzahl Untersuchungsdaten Haltung: {len(x_anlagen)}")

                liste = {}

                for x_anlage in x_anlagen:
                    untersuchsch = x_anlage.findtext("Objektbezeichnung", None, self.NS)

                    untersuchtag = x_anlage.findtext("OptischeInspektion/Inspektionsdatum", None, self.NS)

                    #id = _get_int(x_anlage.findtext("OptischeInspektion/Auftragskennung", None, self.NS))

                    liste[untersuchsch] = [untersuchtag, id]


                filme = x_zustandsdat.findall("Filme/Film", self.NS,)

                for film in filme:
                    bezeichnungen = film.findtext("FilmObjekte/FilmObjekt/Objektbezeichnung", None, self.NS)
                    _ = film.findtext("FilmObjekte/FilmObjekt/Inspektionsrichtung", None, self.NS)
                    if _ == "O":
                        untersuchrichtung = "in Fließrichtung"
                    elif _ == "U":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.warning(f"Haltung untersucht: Fehlerhafter Wert in Feld Inspektionsrichtung: {_}")
                        untersuchrichtung = None
                    x = _get_int(film.findtext("Auftragskennung", None, self.NS))
                    #if bezeichnungen in liste and x == liste[bezeichnungen][1]:
                    if bezeichnungen in liste:

                        typ = film.findtext("FilmObjekte/FilmObjekt/Typ", None, self.NS)
                        if typ == '1':
                            objekt = "Haltung"
                        elif typ == '2':
                            objekt = "Anschlussleitung"
                        elif typ == '3':
                            objekt = "Schacht"
                        elif typ == '4':
                            objekt = "Bauwerk"

                        if typ == "1":

                            _datei = film.findtext("Filmname", None, self.NS)

                            # relativer pfad mit einfügen in datei
                            filmpfad = film.findtext("Filmpfad", None, self.NS)
                            if _datei is not None and filmpfad is not None:
                                filmdatei = os.path.join(filmpfad, _datei)
                            else:
                                filmdatei = _datei


                            yield Untersuchdat_daten(
                                untersuchsch=bezeichnungen,
                                untersuchtag=liste[bezeichnungen][0],
                                untersuchrichtung=untersuchrichtung,
                                datei=filmdatei,
                                objekt=objekt,
                            )

        for untersuchdat_daten in _iter():

            params = {'name': untersuchdat_daten.untersuchsch, 'untersuchtag': untersuchdat_daten.untersuchtag,
                      'untersuchrichtung': untersuchdat_daten.untersuchrichtung,
                      'datei': untersuchdat_daten.datei, 'objekt': untersuchdat_daten.objekt}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: videos\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="videos",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()


    def _anschlussleitungen(self) -> None:
        def _iter() -> Iterator[Anschlussleitung]:

            x_anlagen = self.xml.findall(
                "Datenkollektive/Stammdatenkollektiv/AbwassertechnischeAnlage/[Objektart='1']",
                self.NS,
            )
            logger.debug(f"Anzahl Anschlussleitungen: {len(x_anlagen)}")

            schoben = schunten = material = haltnam = ""
            sohleoben = sohleunten = laenge = hoehe = breite = deckeloben = deckelunten = 0.0

            for x_anlage in x_anlagen:
                x_leitung = x_anlage.find("Kante/Leitung", self.NS)
                if x_leitung is not None:
                    name = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                    baujahr = _get_int(x_anlage.findtext("Baujahr", None, self.NS))
                    haltnam = x_leitung.findtext("Anschlussdaten/Objektbezeichnung", None, self.NS)
                    entwart = x_anlage.findtext("Entwaesserungsart", None, self.NS)
                    ks = 1.5  # in Hydraulikdaten enthalten.
                    simstatus = x_anlage.findtext("Status", None, self.NS)
                    kommentar = x_anlage.findtext("Kommentar", None, self.NS)

                    for _haltung in x_anlage.findall("Kante/KantenTyp/..", self.NS):
                        schoben = _haltung.findtext("KnotenZulauf", None, self.NS)
                        schunten = _haltung.findtext("KnotenAblauf", None, self.NS)

                        sohleoben = _get_float(
                            _haltung.findtext("SohlhoeheZulauf", None, self.NS)
                        )
                        sohleunten = _get_float(
                            _haltung.findtext("SohlhoeheAblauf", None, self.NS)
                        )
                        laenge = _get_float(_haltung.findtext("Laenge", None, self.NS))

                        material = _haltung.findtext("Material", None, self.NS)

                        for profil in _haltung.findall("Profil", self.NS):
                            # profilnam = profil.findtext("Profilart", None, self.NS)     # nicht in QKan verwaltet
                            hoehe = (
                                _get_float(profil.findtext("Profilhoehe", None, self.NS))

                            )
                            breite = (
                                _get_float(profil.findtext("Profilbreite", None, self.NS))

                            )

                    x_geodaten = x_anlage.find("Geometrie/Geometriedaten", self.NS)
                    geom = self._get_kante(x_geodaten)

                    # for _haltung in x_anlage.findall(
                    #     "Geometrie/Geometriedaten/Kanten/Kante/Start", self.NS
                    # ):
                    #     if _haltung is not None:
                    #         xschob = _get_float(_haltung.findtext("Rechtswert", None, self.NS))
                    #         yschob = _get_float(_haltung.findtext("Hochwert", None, self.NS))
                    #         deckeloben = _get_float(
                    #             _haltung.findtext("Punkthoehe", None, self.NS)
                    #         )
                    #     else:
                    #         pass
                    #
                    # for _haltung in x_anlage.findall(
                    #         "Geometrie/Geometriedaten/Polygone/Polygon/Kante/Start[1]",
                    #         self.NS
                    # ):
                    #     if _haltung is not None:
                    #         xschob = _get_float(_haltung.findtext("Rechtswert", None, self.NS))
                    #         yschob = _get_float(_haltung.findtext("Hochwert", None, self.NS))
                    #         deckeloben = _get_float(
                    #             _haltung.findtext("Punkthoehe", None, self.NS)
                    #         )
                    #     else:
                    #         pass
                    #
                    #
                    # for _haltung in x_anlage.findall(
                    #     "Geometrie/Geometriedaten/Kanten/Kante/Ende", self.NS
                    # ):
                    #     if _haltung is not None:
                    #         xschun = _get_float(_haltung.findtext("Rechtswert", None, self.NS))
                    #         yschun = _get_float(_haltung.findtext("Hochwert", None, self.NS))
                    #         deckelunten = _get_float(
                    #             _haltung.findtext("Punkthoehe", None, self.NS)
                    #         )
                    #     else:
                    #         pass
                    #
                    # for _haltung in x_anlage.findall(
                    #         "Geometrie/Geometriedaten/Polygone/Polygon/Kante/Ende[last()]",
                    #         self.NS
                    # ):
                    #     if _haltung is not None:
                    #         xschun = _get_float(_haltung.findtext("Rechtswert", None, self.NS))
                    #         yschun = _get_float(_haltung.findtext("Hochwert", None, self.NS))
                    #         deckelunten = _get_float(
                    #             _haltung.findtext("Punkthoehe", None, self.NS)
                    #         )
                    #     else:
                    #          pass

                    yield Anschlussleitung(
                        leitnam=name,
                        schoben=schoben,
                        schunten=schunten,
                        haltnam=haltnam,
                        hoehe=hoehe,
                        breite=breite,
                        laenge=laenge,
                        material=material,
                        baujahr=baujahr,
                        sohleoben=sohleoben,
                        sohleunten=sohleunten,
                        deckeloben=deckeloben,
                        deckelunten=deckelunten,
                        entwart=entwart,
                        ks=ks,
                        simstatus=simstatus,
                        kommentar=kommentar,
                        geom=geom,
                    )
                else:
                    pass

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

            # # Profile
            # profilnam = self.db_qkan.get_from_mapper(
            #     anschlussleitung.profilnam,
            #     self.mapper_profile,
            #     'anschlussleitungen',
            #     'profile',
            #     'profilnam',
            #     'isybau',
            #     'kommentar',
            #     'kuerzel',
            # )
            #
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

            # Hausanschlussdaten für Zustand in dict übernehmen
            if getattr(QKan.config.xml, "import_zustand", True):
                self.anschlussdaten[anschlussleitung.leitnam] = {
                    'schoben': anschlussleitung.schoben, 'schunten': anschlussleitung.schunten,
                    'hoehe': anschlussleitung.hoehe, 'breite': anschlussleitung.breite,
                    'laenge': anschlussleitung.laenge,
                    'kommentar': anschlussleitung.kommentar, 'baujahr': anschlussleitung.baujahr,
                }

            params = {'leitnam': anschlussleitung.leitnam,
                      'schoben': anschlussleitung.schoben, 'schunten': anschlussleitung.schunten,
                      'hoehe': anschlussleitung.hoehe, 'breite': anschlussleitung.breite,
                      'laenge': anschlussleitung.laenge, 'material': material, 'baujahr': anschlussleitung.baujahr,
                      'sohleoben': anschlussleitung.sohleoben, 'sohleunten': anschlussleitung.sohleunten,
                      'deckeloben': anschlussleitung.deckeloben, 'deckelunten': anschlussleitung.deckelunten,
                      'entwart': entwart,
                      'ks': anschlussleitung.ks, 'simstatus': simstatus,
                      'kommentar': anschlussleitung.kommentar,
                      'geom': anschlussleitung.geom, 'epsg': QKan.config.epsg}

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


    # Anschluss_untersucht
    def _anschluss_untersucht(self) -> None:
        def _iter() -> Iterator[Anschlussleitung_untersucht]:
            x_anlagen = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv/InspizierteAbwassertechnischeAnlage/[Anlagentyp='2']",
                self.NS,
            )
            logger.debug(f"Anzahl Anschlussleitungen: {len(x_anlagen)}")

            untersuchtag = ""
            untersucher = ""
            wetter = None
            strasse = ""
            bewertungsart = None
            bewertungstag = ""
            datenart = self.datenart
            laenge = None

            for x_anlage in x_anlagen:
                found_leitung = x_anlage.findtext("Kante/Leitung", None, self.NS)
                if found_leitung != '':
                    name = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                    strasse = x_anlage.findtext("Lage/Strassenname", None, self.NS)

                    for _haltung in x_anlage.findall("OptischeInspektion", self.NS):

                        _val = _haltung.findtext("Rohrleitung/BezugspunktLage", None, self.NS)
                        if _val == '2' or not _val:
                            bezugspunkt = enums.UntersuchBezugpunkt.ROHRANFANG.value
                        else:
                            bezugspunkt = enums.UntersuchBezugpunkt.GERINNEMITTELPUNKT.value

                        laenge = _get_float(x_anlage.findtext("Rohrleitung/Inspektionslaenge",None, self.NS))

                        untersuchtag = _haltung.findtext("Inspektionsdatum", None, self.NS)

                        untersucher = _haltung.findtext("NameUntersucher", None, self.NS)

                        wetter = _haltung.findtext("Wetter", None, self.NS)

                        auftragsbezeichnung = _haltung.findtext("Auftragskennung", None, self.NS)

                        for _haltungz in _haltung.findall("Rohrleitung/Bewertung", self.NS):
                            bewertungsart = _haltungz.findtext("Bewertungsverfahren", None, self.NS)

                            bewertungstag = _haltungz.findtext("Bewertungsdatum", None, self.NS)

                    yield Anschlussleitung_untersucht(
                        haltnam=name,
                        untersuchtag=untersuchtag,
                        untersucher=untersucher,
                        wetter=wetter,
                        auftragsbezeichnung=auftragsbezeichnung,
                        strasse=strasse,
                        bewertungsart=bewertungsart,
                        bewertungstag=bewertungstag,
                        datenart=datenart,
                        laenge=laenge,
                        bezugspunkt=bezugspunkt

                    )

        for anschlussleitung_untersucht in _iter():
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

            if pdat := self.anschlussdaten.get(anschlussleitung_untersucht.haltnam, {}):
                params = {'leitnam': anschlussleitung_untersucht.haltnam,
                          'untersuchtag': anschlussleitung_untersucht.untersuchtag,
                          'untersucher': anschlussleitung_untersucht.untersucher,
                          'wetter': wetter,
                          'auftragsbezeichnung': anschlussleitung_untersucht.auftragsbezeichnung,
                          'strasse': anschlussleitung_untersucht.strasse,
                          'bewertungsart': anschlussleitung_untersucht.bewertungsart,
                          'laenge': anschlussleitung_untersucht.laenge,
                          'bezugspunkt': anschlussleitung_untersucht.bezugspunkt,
                          'bewertungstag': anschlussleitung_untersucht.bewertungstag, } \
                         | pdat

            else:
                logger.warning(
                    f'Untersuchte Anschlussleitung {anschlussleitung_untersucht.haltnam} fehlt in den Stammdaten')
                params = {'leitnam': anschlussleitung_untersucht.haltnam,
                          'untersuchtag': anschlussleitung_untersucht.untersuchtag,
                          'untersucher': anschlussleitung_untersucht.untersucher,
                          'wetter': wetter,
                          'auftragsbezeichnung': anschlussleitung_untersucht.auftragsbezeichnung,
                          'strasse': anschlussleitung_untersucht.strasse,
                          'bewertungsart': anschlussleitung_untersucht.bewertungsart,
                          'laenge': anschlussleitung_untersucht.laenge,
                          'bezugspunkt': anschlussleitung_untersucht.bezugspunkt,
                          'bewertungstag': anschlussleitung_untersucht.bewertungstag, }

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen_untersucht",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _untersuchdat_anschluss(self) -> None:
        def _iter() -> Iterator[Untersuchdat_anschlussleitung]:
            x_anlagen = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv/InspizierteAbwassertechnischeAnlage/[Anlagentyp='2']",
                self.NS,
            )

            logger.debug(f"Anzahl Untersuchungsdaten Anschluesse: {len(x_anlagen)}")

            ordner_bild = self.ordner_bild
            ordner_video = self.ordner_video

            name = ""
            untersuchrichtung = ""
            schoben = ""
            schunten = ""
            inspektionslaenge = 0.0
            videozaehler = 0
            station = 0.0
            timecode = None
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

            for x_anlage in x_anlagen:

                name = x_anlage.findtext("Objektbezeichnung", None, self.NS)
                untersuchtag = x_anlage.findtext("OptischeInspektion/Inspektionsdatum", None, self.NS)

                for _untersuchdat_haltung in x_anlage.findall("OptischeInspektion/Rohrleitung", self.NS):

                    #id = _get_int(_untersuchdat_haltung.findtext("../Auftragskennung", None, self.NS))

                    _ = _untersuchdat_haltung.findtext("Inspektionsrichtung", None, self.NS)
                    if _ == "O":
                        untersuchrichtung = "in Fließrichtung"
                    elif _ == "U":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.warning(f"Untersuchungsdaten Anschluss: Fehlerhafter Wert in Feld Inspektionsrichtung: {_}")
                        untersuchrichtung = None

                    inspektionslaenge = _get_float(
                        _untersuchdat_haltung.findtext("Inspektionslaenge", None, self.NS))
                    if inspektionslaenge == 0.0:
                        inspektionslaenge = _get_float(_untersuchdat_haltung.findtext(
                            "Inspektionsdaten/RZustand[InspektionsKode='BCE'][Charakterisierung1='XP']/Station",
                            None, self.NS))

                    schoben = _untersuchdat_haltung.findtext("RGrunddaten/KnotenZulauf", None, self.NS)
                    schunten = _untersuchdat_haltung.findtext("RGrunddaten/KnotenAblauf", None, self.NS)

                    for _untersuchdat in _untersuchdat_haltung.findall("Inspektionsdaten/RZustand", self.NS):
                        videozaehler = _get_int(_untersuchdat.findtext("Videozaehler", None, self.NS))
                        station = _get_float(_untersuchdat.findtext("Station", None, self.NS))
                        timecode = _untersuchdat.findtext("Timecode", None, self.NS)
                        kuerzel = _untersuchdat.findtext("InspektionsKode", None, self.NS)
                        charakt1 = _untersuchdat.findtext("Charakterisierung1", None, self.NS)
                        charakt2 = _untersuchdat.findtext("Charakterisierung2", None, self.NS)
                        quantnr1 = _get_float(_untersuchdat.findtext("Quantifizierung1Numerisch", None, self.NS))
                        quantnr2 = _get_float(_untersuchdat.findtext("Quantifizierung2Numerisch", None, self.NS))
                        streckenschaden = _untersuchdat.findtext("Streckenschaden", None, self.NS)
                        streckenschaden_lfdnr = _get_int(
                            _untersuchdat.findtext("StreckenschadenLfdNr", None, self.NS))
                        pos_von = _get_int(_untersuchdat.findtext("PositionVon", None, self.NS))
                        pos_bis = _get_int(_untersuchdat.findtext("PositionBis", None, self.NS))

                        foto_dateiname = _untersuchdat.findtext("Fotodatei", None, self.NS)
                        #if _datei is not None and self.ordner_bild is not None:
                        #    foto_dateiname = os.path.join(self.ordner_bild, _datei)
                        #else:
                        #    foto_dateiname = None

                        ZD = _get_int(
                            _untersuchdat.findtext("Klassifizierung/Dichtheit/SKDvAuto", None, self.NS))
                        ZS = _get_int(
                            _untersuchdat.findtext("Klassifizierung/Standsicherheit/SKSvAuto", None, self.NS))
                        ZB = _get_int(
                            _untersuchdat.findtext("Klassifizierung/Betriebssicherheit/SKBvAuto", None, self.NS))

                        yield Untersuchdat_anschlussleitung(
                            untersuchhal=name,
                            untersuchrichtung=untersuchrichtung,
                            schoben=schoben,
                            schunten=schunten,
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
                            ZS=ZS,
                            ZB=ZB,

                        )

        # def _iter2() -> Iterator[Untersuchdat_anschlussleitung]:
        #     x_filme = self.xml.findall(
        #         "Datenkollektive/Zustandsdatenkollektiv/Filme/Film/Filmname/../..",
        #         self.NS,
        #     )
        #     logger.debug(f"Anzahl Untersuchdat_haltung: {len(x_filme)}")
        #
        #     film_dateiname = ""
        #     for x_film in x_filme:
        #         for _untersuchdat_haltung in x_film.findall("Film/FilmObjekte/..", self.NS):
        #             name = _untersuchdat_haltung.findtext("FilmObjekte/FilmObjekt/Objektbezeichnung", None,
        #                                                   self.NS)
        #
        #             _datei = _untersuchdat_haltung.findtext("Filmname", None, self.NS)
        #             if _datei is not None and self.ordner_video is not None:
        #                 film_dateiname = os.path.join(self.ordner_video, _datei)
        #             else:
        #                 film_dateiname = None
        #
        #             # bandnr = _get_int(_untersuchdat_haltung.findtext("Videoablagereferenz", None, self.NS))
        #
        #             yield Untersuchdat_anschlussleitung(
        #                 untersuchhal=name,
        #                 film_dateiname=film_dateiname,
        #                 # bandnr=bandnr
        #             )

        untersuchdat_anschluss = None
        for untersuchdat_anschlussleitung in _iter():

            params = {'untersuchleit': untersuchdat_anschlussleitung.untersuchhal,
                      'untersuchrichtung': untersuchdat_anschlussleitung.untersuchrichtung,
                      'schoben': untersuchdat_anschlussleitung.schoben, 'schunten': untersuchdat_anschlussleitung.schunten,
                       'untersuchtag': untersuchdat_anschlussleitung.untersuchtag,
                      'videozaehler': untersuchdat_anschlussleitung.videozaehler,
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
                         'ZD': untersuchdat_anschlussleitung.ZD,
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

        if untersuchdat_anschluss is not None:
            Schadenstexte.setschadenstexte_anschlussleitungen(self.db_qkan)

        # geometrieobjekt erzeugen

        # for untersuchdat_anschlussleitung in _iter2():
        #     if not self.db_qkan.sql(
        #             "UPDATE untersuchdat_anschlussleitung SET film_dateiname=?"
        #             " WHERE  untersuchleit= ?",
        #             "xml_import untersuchleit [2a]",
        #             parameters=[untersuchdat_anschlussleitung.film_dateiname,
        #                         untersuchdat_anschlussleitung.untersuchhal],
        #     ):
        #         return None
        #
        # self.db_qkan.commit()

    def _untersuchdat_anschlussleitung_daten(self):
        # TODO: für Fotos auch ergänzan ab Isybau 2020!
        def _iter() -> Iterator[Untersuchdat_daten]:
            x_zustandsdaten = self.xml.findall(
                "Datenkollektive/Zustandsdatenkollektiv",
                self.NS,
            )

            for x_zustandsdat in x_zustandsdaten:

                x_anlagen = x_zustandsdat.findall(
                    "InspizierteAbwassertechnischeAnlage/[Anlagentyp='2']",
                    self.NS,
                )

                logger.debug(f"Anzahl Untersuchungsdaten Haltung: {len(x_anlagen)}")

                liste = {}

                for x_anlage in x_anlagen:
                    untersuchsch = x_anlage.findtext("Objektbezeichnung", None, self.NS)

                    untersuchtag = x_anlage.findtext("OptischeInspektion/Inspektionsdatum", None, self.NS)

                    id = _get_int(x_anlage.findtext("OptischeInspektion/Auftragskennung", None, self.NS))

                    liste[untersuchsch] = [untersuchtag, id]

                filme = x_zustandsdat.findall("Filme/Film", self.NS, )

                for film in filme:
                    bezeichnungen = film.findtext("FilmObjekte/FilmObjekt/Objektbezeichnung", None, self.NS)
                    _ = film.findtext("FilmObjekte/FilmObjekt/Inspektionsrichtung", None, self.NS)
                    if _ == "O":
                        untersuchrichtung = "in Fließrichtung"
                    elif _ == "U":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.warning(f"Haltung untersucht: Fehlerhafter Wert in Feld Inspektionsrichtung: {_}")
                        untersuchrichtung = None
                    x = _get_int(film.findtext("Auftragskennung", None, self.NS))
                    if bezeichnungen in liste and x == liste[bezeichnungen][1]:
                        if bezeichnungen in liste:

                            typ = film.findtext("FilmObjekte/FilmObjekt/Typ", None, self.NS)
                            if typ == '1':
                                objekt = "Haltung"
                            elif typ == '2':
                                objekt = "Anschlussleitung"
                            elif typ == '3':
                                objekt = "Schacht"
                            elif typ == '4':
                                objekt = "Bauwerk"

                            if typ == "2":

                                _datei = film.findtext("Filmname", None, self.NS)

                                # relativer pfad mit einfügen in datei
                                # relativer pfad mit einfügen in datei
                                filmpfad = film.findtext("Filmpfad", None, self.NS)
                                if _datei is not None and filmpfad is not None:
                                    filmdatei = os.path.join(filmpfad, _datei)
                                else:
                                    filmdatei = _datei

                                yield Untersuchdat_daten(
                                    untersuchsch=bezeichnungen,
                                    untersuchtag=liste[bezeichnungen][0],
                                    untersuchrichtung=untersuchrichtung,
                                    datei=filmdatei,
                                    objekt=objekt,
                                )

        for untersuchdat_daten in _iter():

            params = {'name': untersuchdat_daten.untersuchsch, 'untersuchtag': untersuchdat_daten.untersuchtag,
                      'untersuchrichtung': untersuchdat_daten.untersuchrichtung,
                      'datei': untersuchdat_daten.datei, 'objekt': untersuchdat_daten.objekt}

            logger.debug(f'isyporter.import - insertdata:\ntabnam: videos\n'
                         f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="videos",
                    mute_logger=False,
                    parameters=params,
            ):
                del self.db_qkan
                return

        self.db_qkan.commit()

    def _schaechte_untersucht_geom(self):
        sql = f"""
                UPDATE schaechte_untersucht
        		SET geop = (select schaechte.geop from schaechte where schaechte_untersucht.schnam =schaechte.schnam);
                						"""
        data = ()
        try:
            self.db_qkan.sql(sql, parameters=data)
            self.db_qkan.commit()
        except:
            pass

    def _haltungen_untersucht_geom(self):
        sql = f"""
                UPDATE haltungen_untersucht
                SET geom = (select haltungen.geom from haltungen where haltungen_untersucht.haltnam =haltungen.haltnam);
                    """
        data = ()
        try:
            self.db_qkan.sql(sql, parameters=data)
            self.db_qkan.commit()
        except:
            pass

    def _anschluss_untersucht_geom(self):
        sql = f"""
                UPDATE anschlussleitungen_untersucht
                SET geom = (select anschlussleitungen.geom from anschlussleitungen where anschlussleitungen_untersucht.leitnam =anschlussleitungen.leitnam);
                """
        data = ()
        try:
            self.db_qkan.sql(sql, parameters=data)
            self.db_qkan.commit()
        except:
            pass



    def _wehre(self) -> None:
        # Hier werden die Hydraulikdaten zu den Wehren in die Datenbank geschrieben.
        # Bei Wehren stehen alle wesentlichen Daten im Hydraulikdatenkollektiv, weshalb im Gegensatz zu den
        # Haltungsdaten keine Stammdaten verarbeitet werden.

        def _iter() -> Iterator[Wehr]:
            x_hydobjekte = self.xml.findall(
                "Datenkollektive/Hydraulikdatenkollektiv/Rechennetz/"
                "HydraulikObjekte/HydraulikObjekt/WehrUeberlauf/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Wehre: {len(x_hydobjekte)}")

            schoben, schunten, wehrtyp = ("",) * 3
            schwellenhoehe, kammerhoehe, laenge, uebeiwert = (0.0,) * 4
            for x_hydobjekt in x_hydobjekte:
                _wehr = x_hydobjekt.find("WehrUeberlauf", self.NS)
                schoben = _wehr.findtext("SchachtZulauf", None, self.NS)
                schunten = _wehr.findtext("SchachtAblauf", None, self.NS)
                wehrtyp = _wehr.findtext("WehrTyp", None, self.NS)

                schwellenhoehe = _get_float(
                    _wehr.findtext("Schwellenhoehe", None, self.NS)
                )
                laenge = _get_float(
                    _wehr.findtext("LaengeWehrschwelle", None, self.NS)
                )
                kammerhoehe = _get_float(_wehr.findtext("Kammerhoehe", None, self.NS))

                # Überfallbeiwert der Wehr Kante (abhängig von Form der Kante)
                uebeiwert = _get_float(
                    _wehr.findtext("Ueberfallbeiwert", None, self.NS)
                )

                yield Wehr(
                    wnam=x_hydobjekt.findtext("Objektbezeichnung", None, self.NS),
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
            x_anlagen = self.xml.findall(
                "Datenkollektive/Stammdatenkollektiv/AbwassertechnischeAnlage",
                self.NS,
            )
            logger.debug(f"Anzahl Pumpen: {len(x_anlagen)}")

            for x_anlage in x_anlagen:
                yield Pumpe(
                    pnam=x_anlage.findtext("Objektbezeichnung", None, self.NS),
                    simstatus=x_anlage.findtext("Status", None, self.NS),
                    kommentar=x_anlage.findtext("Kommentar", None, self.NS),
                )

        def _iter2() -> Iterator[Pumpe]:
            # Hydraulik
            x_hydobjekte = self.xml.findall(
                "Datenkollektive/Hydraulikdatenkollektiv/Rechennetz/"
                "HydraulikObjekte/HydraulikObjekt/Pumpe/..",
                self.NS,
            )
            logger.debug(f"Anzahl HydraulikObjekte_Pumpen: {len(x_hydobjekte)}")

            schoben, schunten, steuersch = ("",) * 3
            _pumpentyp = 0
            volanf, volges, sohle = (0.0,) * 3
            for x_hydobjekt in x_hydobjekte:
                _pumpe = x_hydobjekt.find("Pumpe", self.NS)
                _pumpentyp = _get_int(_pumpe.findtext("PumpenTyp", None, self.NS))
                schoben = _pumpe.findtext("SchachtZulauf", None, self.NS)
                schunten = _pumpe.findtext("SchachtAblauf", None, self.NS)
                steuersch = _pumpe.findtext("Steuerschacht", None, self.NS)
                sohle = _get_float(_pumpe.findtext("Sohlhoehe", None, self.NS))
                volanf = _get_float(_pumpe.findtext("Anfangsvolumen", None, self.NS))
                volges = _get_float(_pumpe.findtext("Gesamtvolumen", None, self.NS))

                yield Pumpe(
                    pnam=x_hydobjekt.findtext("Objektbezeichnung", None, self.NS),
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
                     'sohleunten': pumpe.sohle, 'pumpentyp': pumpentyp,
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


