import re, os
#import xml.etree.ElementTree as ElementTree
import lxml.etree as ElementTree
from typing import Dict, Iterator, Union

from qgis.PyQt.QtCore import QByteArray
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis, QgsGeometry, QgsPoint, QgsPointXY, QgsCircle, QgsMultiPolygon, QgsPolygon

from qkan import QKan, enums
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanError, QkanDbError
from qkan.tools.k_xml import _get_float, _get_int
from qkan.tools.k_schadenstexte import Schadenstexte
from qkan.tools.k_befahrung import setbefahrung

logger = get_logger("QKan.xml.import")

# region objects
class Schacht(ClassObject):
    schnam: str = ""
    sohlhoehe: float = 0.0
    deckelhoehe: float = 0.0
    durchm: float = 0.0
    druckdicht: int = 0
    baujahr: int = 0
    entwart: str = ""
    strasse: str = ""
    bauwerksart: str = ""
    schachttyp: str = ""
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
    bauwerksart: str = ""
    kommentar: str = ""
    baujahr: int = 0
    untersuchtag: str = ""
    untersucher: str = ""
    film_dateiname: str = ""
    wetter: str = ""
    bewertungsart: str = ""
    bewertungstag: str = ""
    datenart: str = ""
    max_ZD: int = None
    max_ZB: int = None
    max_ZS: int = None
    geop: QByteArray = None

class Untersuchdat_schacht(ClassObject):
    untersuchsch: str = ""
    id: int = 0
    untersuchtag: str = ""
    #TODO: videozaehler = Uhrzeit hh:mm
    videozaehler: str = ""
    timecode: str = ""
    kuerzel: str = ""
    langtext: str = ""
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

class Haltung(ClassObject):
    haltnam: str = ""
    schoben: str = ""
    schunten: str = ""
    hoehe: float = 0.0
    breite: float = 0.0
    laenge: float = 0.0
    material: str = ""
    sohleoben: float = 0.0
    sohleunten: float = 0.0
    profilnam: str = ""
    baujahr: int = 0
    entwart: str = ""
    strasse: str = ""
    ks: float = 1.5
    simstatus: str = ""
    kommentar: str = ""
    aussendurchmesser: float = 0.0
    profilauskleidung: str = ""
    innenmaterial: str = ""
    geom: QByteArray = None

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
    untersuchrichtung: str = ""
    film_dateiname: str = ""
    bezugspunkt: str = ""
    wetter: str = ""
    strasse: str = ""
    bewertungsart: str = ""
    bewertungstag: str = ""
    datenart: str = ""
    max_ZD: int = None
    max_ZB: int = None
    max_ZS: int = None
    geom: QByteArray = None

class Untersuchdat_haltung(ClassObject):
    untersuchhal: str = ""
    schoben: str = ""
    schunten: str = ""
    id: int = 0
    untersuchtag: str = ""
    untersuchrichtung: str = ""
    inspektionslaenge: float = 0.0
    videozaehler: str = ""
    station: float = 0.0
    timecode: str = ""
    kuerzel: str = ""
    langtext: str = ""
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
    ZD: int = None
    ZB: int = None
    ZS: int = None
    geom: QByteArray = None

class Anschlussleitung(ClassObject):
    leitnam: str = ""
    schoben: str = ""
    schunten: str = ""
    haltnam: str= ""
    urstation: float = 0.0
    ursprung: str= ""
    inFliessrichtung: bool = True
    lageanschluss: int = 0
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
    geom: QByteArray = None

Anschlussleitung_untersucht = Haltung_untersucht

Untersuchdat_anschlussleitung = Untersuchdat_haltung

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
    entwart: str = ""
    baujahr: int = 0
    geom: QByteArray = None

class Pumpe(ClassObject):
    pnam: str =""
    schoben: str = ""
    schunten: str = ""
    # pumpentyp: int = 0
    volanf: float = 0.0
    volges: float = 0.0
    sohle: float = 0.0
    laenge: float
    steuersch: str = ""
    einschalthoehe: float = 0.0
    ausschalthoehe: float = 0.0
    simstatus: str = ""
    kommentar: str = ""
    baujahr: int = 0
    entwart: str = ""
    geom: QByteArray = None

# endregion

# noinspection SqlNoDataSourceInspection, SqlResolve
class ImportTask(Schadenstexte):
    def __init__(self, db_qkan: DBConnection):
        self.db_qkan = db_qkan

        xml_file = QKan.config.xml.import_file
        data_choice = QKan.config.xml.data_choice
        self.ordner_bild = QKan.config.fotoPathCurrent
        self.ordner_video = QKan.config.videoPathCurrent

        self.data_choice= data_choice
        if self.data_choice == "ISYBAU Daten":
            self.datenart = "ISYBAU"
        if self.data_choice == "DWA M-150 Daten":
            self.datenart = "DWA"

        # nr (str) => description
        self.mapper_entwart: Dict[str, str] = {}
        self.mapper_material: Dict[str, str] = {}
        self.mapper_profile: Dict[str, str] = {}
        self.mapper_simstatus: Dict[str, str] = {}
        self.mapper_wetter: Dict[str, str] = {}
        self.mapper_m150knotenarten: Dict[str, str] = {}
        self.mapper_bauwerksarten: Dict[str, str] = {}
        self.mapper_haltungsarten: Dict[str, str] = {}
        self.mapper_strassen: Dict[str, str] = {}

        db_qkan.loadmodule('m150porter')

        # Load XML
        self.xml = ElementTree.ElementTree()
        self.xml.parse(xml_file)

    def _get_KG_GO(self,
                   block: ElementTree._Element,
                   name: str,
                   durchmesser: float = 1.0,
                   link: bool = False,
                   ) -> tuple[Union[str, None], Union[str, None], Union[float, None], Union[float, None]]:
        """Liest Knotenobjekte sowie Sohl- und Deckelhoehe aus einem KG/GO-Block

        - geop:          Punktobjekt
        - geom:          Schachtobjekt als Multipolygon
        - sohlhoehe:     Sohlhöhe in mNN
        - deckelhoehe:   Deckelhöhe in mNN

        :param block: <KG>-Element aus m150-Datei
        :param name:  Name des Knotenelementes, nur für Fehlermeldungen
        """
        sohlhoehe = None
        deckelhoehe = None
        geop_d = None  # falls kein Gerinnepunktobjekt, wird Deckel übernommen
        geom_g = None  # falls kein Objekt für Bauwerk oder Deckel, wird Kreis aus Gerinne übernommen
        geop = QgsPoint()
        geom = None
        sohle_b = None  # falls kein Gerinnepunktobjekt, wird Sohlhöhe aus Bauwerk übernommen
        proj = None
        blocks_go = block.findall("GO")
        if len(blocks_go) == 0:
            logger.debug(f'Keine Geometrieobjektdaten bei Knoten "{name}"')
            blocks_go = self.xml.findall(f"HG/GO/GP[GP001='{name}']")
            logger.debug(f"Keine Geometriedaten bei Knoten '{name}. -> Suche in Haltungsknickpunkten'")

            # Koordinate aus Knickpunkten gleichen Namens
            blocks_hp = self.xml.findall(f"HG/GO/GP[GP001='{name}']")
            if len(blocks_hp) == 0:
                logger.debug(f'Auch keine Geometriepunktdaten bei Haltungsknickpunkten "{name}"')
                return None, None, None, None

            xp, yp = (None, None)
            for bl_hp in blocks_hp:
                proj = bl_hp.findtext(path='GP002')
                xp = _get_float(bl_hp, "GP003")
                if xp is None or proj == 'UTM':
                    xp = _get_float(bl_hp, "GP005")
                    yp = _get_float(bl_hp, "GP006")
                else:
                    yp = _get_float(bl_hp, "GP004")
                zp = _get_float(bl_hp, "GP007")
                if xp is not None:
                    # Nur 1 Knickpunkt verarbeiten
                    break

            geop = QgsGeometry.fromPointXY(QgsPointXY(xp, yp))
            # falls kein Bauwerk oder Deckel:
            geom = QgsGeometry(QgsCircle.fromCenterDiameter(QgsPoint(xp, yp), durchmesser).toLineString())
            geom.convertToMultiType()

        for bl_go in blocks_go:
            # Schleife über alle Geometrieobjekte
            pnam = bl_go.findtext('GO001')
            pttyp = bl_go.findtext('GO002')
            geotyp = bl_go.findtext('GO003')

            gplis = []                      # Bauwerkspolygon in geom
            blocks_gp = bl_go.findall("GP")
            if len(blocks_gp) == 0:
                logger.debug(f'Keine Geometriepunktdaten bei Knoten "{name}"')
                continue
            xp = yp = zp = None               # Falls keine Koordinaten in Geometriepunktdaten enthalten (s. u.)
            for bl_gp in blocks_gp:
                # Schleife über alle Stützstellen
                proj = bl_go.findtext(path='GP002')
                xp = _get_float(bl_gp, "GP003")
                if xp is None or proj == 'UTM':
                    xp = _get_float(bl_gp, "GP005")
                    yp = _get_float(bl_gp, "GP006")
                else:
                    yp = _get_float(bl_gp, "GP004")
                zp = _get_float(bl_gp, "GP007")

                if xp is None:                  # kommt gleich weg
                    # Koordinate aus Knickpunkten gleichen Namens
                    blocks_hp = self.xml.findall(f"HG/GO/GP[GP001='{name}']")
                    if len(blocks_hp) == 0:
                        logger.debug(f'Auch keine Geometriepunktdaten bei Haltungsknickpunkten "{name}"')
                        continue

                    for bl_hp in blocks_hp:
                        proj = bl_go.findtext(path='GP002')
                        xp = _get_float(bl_hp, "GP003")
                        if xp is None or proj == 'UTM':
                            xp = _get_float(bl_hp, "GP005")
                            yp = _get_float(bl_hp, "GP006")
                        else:
                            yp = _get_float(bl_hp, "GP004")
                        zp = _get_float(bl_hp, "GP007")
                        if xp is not None:
                            # Nur 1 Knickpunkt verarbeiten
                            break

                if xp is not None and geotyp in ('L', 'Poly', 'Fl'):
                    gplis.append([xp, yp])
            if xp is None:
                # Keine Koordinaten in Geometriepunktdaten enthalten
                logger.debug(f'In Knoten "{name}" wurden im Geometrieobjekt {pnam} keine Koordinaten gefunden')
                continue
            if link:                    # Sonderfall Pumpwerk, muss als Linienobjekt zurückgegeben werden.
                if geotyp == 'Pkt':
                    geom = QgsGeometry.fromPolyline([QgsPoint(xp, yp), QgsPoint(xp + 1.0, yp + 1.0)])
                else:
                    logger.info(f"Pumpwerk kann nicht als Bauwerk dargestellt werden")
            elif geotyp == 'Pkt':
                # Normalfall
                if False and pttyp in ('B', 'D'):
                    geocircle = QgsGeometry.fromPolyline(
                        QgsCircle.fromCenterDiameter(QgsPoint(xp, yp), durchmesser).points(36)
                    )
                    geocircle.convertToMultiType()
                    if geom is None:
                        geom = geocircle
                    else:
                        geom = QgsGeometry.collectGeometry([geom, geocircle])
                    geop_d = QgsGeometry.fromPointXY(QgsPointXY(xp, yp))                  # nur für den Fall, dass pttyp == 'G'fehlt
                elif pttyp == 'G':
                    geop = QgsGeometry.fromPointXY(QgsPointXY(xp, yp))
                    # falls kein Bauwerk oder Deckel:
                    geocircle = QgsGeometry(QgsCircle.fromCenterDiameter(QgsPoint(xp, yp), durchmesser).toLineString())
                    geocircle.convertToMultiType()
                    if geom_g is None:
                        geom_g = geocircle
                        geom_g.convertToMultiType()
                    else:
                        geom_g = QgsGeometry.collectGeometry([geom_g, geocircle])
            # elif geotyp == 'Kr':
            #     geocircle = QgsGeometry.fromPolyline(
            #         QgsCircle.fromCenterDiameter(QgsPoint(xp, yp), durchmesser).points(36))
            #     geom = QgsGeometry.collectGeometry([geom, geocircle])
            elif geotyp in ('Poly', 'Fl'):
                ptlis = [QgsPointXY(x, y) for x, y in gplis]
                gmline = QgsGeometry.fromPolylineXY(ptlis)
                gmline.convertToMultiType()
                if geom is None:
                    geom = gmline
                else:
                    geom = QgsGeometry.collectGeometry([geom, gmline])
            elif geotyp in ('L',):
                logger.error(f"Linienelement nicht zulässig in Element <KG001> = {name}")
            else:
                logger.warning(f'm150._get_KG_GO: geotyp unbekannt: {geotyp}')
                continue

            if pttyp == 'D':
                deckelhoehe = zp
            elif pttyp == 'G':
                sohlhoehe = zp
            elif pttyp in ('B',):
                sohle_b = zp
            else:
                logger.warning(f'm150._get_KG_GO: pttyp unbekannt: {pttyp}')
                continue

        if sohlhoehe is None:
            sohlhoehe = sohle_b
        if geop is None:
            geop = geop_d
        # if geom is None:
        #     geom = geom_g

        if geop:
            geop_wkb = geop.asWkb()
        else:
            geop_wkb = None
            logger.warning(f"M150-Import: Konnte kein Punktobjekt finden für {name}")

        if geom is not None:
            geom_wkb = geom.asWkb()
        else:
            geom_wkb = None
            logger.debug(f"M150-Import: Konnte kein Polygonobjekt finden für {name}")

        return geop_wkb , geom_wkb, sohlhoehe, deckelhoehe

    def _get_KG_201(self, block: ElementTree._Element, name: str) -> ([str, None], [str, None], [float, None], [float, None]):
        """Liest Knotenobjekte sowie Sohl- und Deckelhoehe aus den alten m150-Feldern KG201 ff.

        - geop:          Punktobjekt
        - geom:          Schachtobjekt als Multipolygon
        - sohlhoehe:     Sohlhöhe in mNN
        - deckelhoehe:   Deckelhöhe in mNN

        :param block: <KG>-Element aus m150-Datei
        :param name:  Name des Knotenelementes, nur für Fehlermeldungen
        """

        xs = _get_float(block, "KG206")
        ys = _get_float(block, "KG207")
        zs = _get_float(block, "KG209")
        xd = _get_float(block, "KG201")
        yd = _get_float(block, "KG202")
        zd = _get_float(block, "KG204")

        if xs:
            geop = QgsGeometry.fromPointXY(QgsPointXY(xs, ys))
            sohlhoehe = zs
        else:
            geop = None
            sohlhoehe = None

        if xd is None:
            xd, yd, zd = xs, ys, zs
        geom = QgsGeometry(QgsCircle.fromCenterDiameter(QgsPoint(xd, yd), 1.0).toCircularString(36))
        deckelhoehe = zd

        if geop:
            geop_wkb = geop.asWkb()
        else:
            geop_wkb = None
            logger.debug(f"M150-Import alt: Konnte kein Punktobjekte KG206 ... finden für {name}")

        if geom:
            geom_wkb = geom.asWkb()
        else:
            geom_wkb = None
            logger.debug(f"M150-Import alt: Konnte kein Punktobjekte KG201 ... finden für {name}")

        return geop_wkb , geom_wkb, sohlhoehe, deckelhoehe

    def _get_HG_GO(self, block: ElementTree._Element, name: str, switchDirection: bool = False) \
            -> ([str, None], [str, None], [float, None], [float, None], [float, None], [float, None]):
        """Liest Linienobjekte sowie Sohl- und Deckelhoehe aus einem HG/GO-Block

        - geom:          Haltungsobjekt als Linienobjekt
        - sohleoben:     Sohlhöhe oben in mNN
        - sohleunten:    Sohlhöhe unten in mNN

        :param block: <HG>-Element aus m150-Datei
        :param name:  Name des Knotenelementes, nur für Fehlermeldungen
        :param switchDirection: Kehrt Polyonrichtung um

        """
        sohleoben = None
        sohleunten = None
        schoben = None              # bei HA-Leitungen
        schunten = None             # bei HA-Leitungen
        geom = None
        blocks_go = block.findall("GO")
        if len(blocks_go) == 0:
            logger.debug(f'Keine Geometrieobjektdaten bei Haltungsobjekt "{name}"')
            return None, None, None
        for bl_go in blocks_go:
            pttyp = bl_go.findtext('GO002')
            if pttyp != 'H':
                logger.warning(f'Datentyp in <GO002> muss "H" sein, ist aber: {pttyp}')
            geotyp = bl_go.findtext('GO003')

            gplis = []
            blocks_gp = bl_go.findall("GP")
            if len(blocks_gp) == 0:
                logger.debug(f'Keine Geometriepunktdaten bei Haltungsobjekt "{name}"')
                continue
            for bl_gp in blocks_gp:
                xp = _get_float(bl_gp, "GP003")
                if xp is None:
                    xp = _get_float(bl_gp, "GP005")
                yp = _get_float(bl_gp, "GP004")
                if yp is None:
                    yp = _get_float(bl_gp, "GP006")
                zp = _get_float(bl_gp, "GP007")
                if geotyp in ('L', 'Poly'):
                    gplis.append([xp, yp])

                if schoben is None:
                    schoben = bl_gp.findtext('GP001')   # nur erste Stützstelle
                schunten = bl_gp.findtext('GP001')      # letzte Stützstelle

                if sohleoben is None:
                    sohleoben = zp                      # erste Sohlhöhe
                sohleunten = zp                         # letzte Sohlhöhe

            if geotyp in ('Poly', 'L'):
                ptlis = [QgsPoint(x, y) for x, y in gplis]
                if switchDirection:
                    # Für Hausanschlüsse: Umkehren der Richtung
                    ptlis.reverse()
                geom = QgsGeometry.fromPolyline(ptlis)
                if geom is None:
                    logger.error(f'Fehler bei polyline: {ptlis}')
            else:
                logger.warning(f'm150._get_HG_coords: geotyp unbekannt: {geotyp}')
                continue

        if geom is not None:
            geom_wkb = geom.asWkb()
        else:
            geom_wkb = None
            logger.warning(f"M150-Import: Konnte keine Punktobjekte finden für Haltung {name}")

        return geom_wkb, sohleoben, sohleunten, schoben, schunten

    def _get_HG_201(self, block: ElementTree._Element, name: str) \
            -> ([str, None], [str, None], [float, None], [float, None]):
        """Liest Haltungsobjekte sowie Sohl- und Deckelhoehe aus den alten m150-Feldern KG201 ff.

        - geom:          Haltungsobjekt als Linienobjekt
        - sohleoben:     Sohlhöhe oben in mNN
        - sohleunten:    Sohlhöhe unten in mNN

        :param block: <KG>-Element aus m150-Datei
        :param name:  Name des Knotenelementes, nur für Fehlermeldungen
        """

        xob = _get_float(block, "KG201")
        yob = _get_float(block, "KG202")
        zob = _get_float(block, "KG204")
        xun = _get_float(block, "KG206")
        yun = _get_float(block, "KG207")
        zun = _get_float(block, "KG209")

        if xun and xob:
            geom = QgsGeometry.fromPolyline([QgsPoint(xob, yob), QgsPoint(xun, yun)])
            sohleoben =  zob
            sohleunten = zun
        else:
            geom = None
            sohleoben =  None
            sohleunten = None


        if geom:
            geom_wkb = geom.asWkb()
        else:
            geom_wkb = None
            logger.debug(f"M150-Import alt: Konnte keine Punktobjekte KG201 ... finden für Haltung {name}")

        return geom_wkb, sohleoben, sohleunten

    def run(self) -> bool:
        """Import ausführen.

        Einlesen der M150-Daten in zwei Schritten:
        1. Einlesen der benutzerdefinierten Referenztabellen. Wenn diese nicht existieren, werden
           Standardwerte gesetzt.
        2. Import der M150-Daten

        Der Status wird in _reftables() festgestellt, Wenn das Ergebnis knotenarten_uncomplete nicht leer ist, wird der Import
        zunächst beendet und der Benutzer aufgefordert, den Knotentyp für jeden Schachttyp im Layer M150:Knotenarten
        festzulegen.

        :returns:   knotenarten_uncomplete
        :rtype:     bool, bool

        **knotenarten_uncomplete** gibt an, ob in allen Datensätzen der Referenztabelle refdata die
        QKan-Bezeichnung (Attribut "bezqkan") nicht leer ist.
        **tabM150Exists** gibt an, ob die Tabelle m150_knotenarten (und der dazugehörige Layer) existiert
        """

        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Import aus M150 läuft. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.MessageLevel.Info, 10)

        knotenarten_uncomplete = self._reftables()           ;self.progress_bar.setValue(5)

        self._init_mappers()
#        if getattr(QKan.config.xml, "import_stamm", True):
        if QKan.config.xml.import_stamm:
            self._schaechte()                             #  ;self.progress_bar.setValue(10)
            #self._auslaesse()                            #   ;self.progress_bar.setValue(20)   # in _schaechte() enthalten
            #self._speicher()
            self._haltungen()                             #  ;self.progress_bar.setValue(30)
            self._wehre()
            self._pumpen()                                #  ;self.progress_bar.setValue(40)
        # if getattr(QKan.config.xml, "import_haus", True):
        if QKan.config.xml.import_haus:
            self._anschlussleitungen()                    #  ;self.progress_bar.setValue(50)
            self._anschluss_untersucht()                  #  ;self.progress_bar.setValue(55)
            self._untersuchdat_anschluss()                #  ;self.progress_bar.setValue(60)
        # if getattr(QKan.config.xml, "import_zustand", True):
        if QKan.config.xml.import_zustand:
            self._schaechte_untersucht()                  #  ;self.progress_bar.setValue(65)
            self._untersuchdat_schaechte()                #  ;self.progress_bar.setValue(75)
            self._haltungen_untersucht()                  #  ;self.progress_bar.setValue(85)
            self._untersuchdat_haltung()                  #  ;self.progress_bar.setValue(95)
        # self.db_qkan._adapt_reftable('entwaesserungsarten')

        if QKan.config.xml.import_teilbefahrung:
            setbefahrung(self.db_qkan)


#        self.progress_bar.setValue(100)
        status_message.setText("Fertig! M150-Import abgeschlossen.")

        return knotenarten_uncomplete

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für DWA-Import füllen

        :returns:   knotenarten_uncomplete
        :rtype:     bool

        **knotenarten_uncomplete** gibt an, ob in der Referenztabelle refdata die
        QKan-Bezeichnung (Attribut "bezqkan") für die Datensätze
        (modul = 'm150porter' AND 'subject = 'import_knotentypen') nicht leer ist.
        Die Zuordnung zu 'Schacht', 'Auslass', etc. ist in der Layertabelle im Attribut
        'Bezeichnung' hinterlegt.
        """
        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert - SQLite

        # Referenztabelle Entwässerungsarten

        params = []

        blocks = self.xml.findall("RT/[RT001='104']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Kanalnutzung": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            # Falls einer der beiden Einträge fehlt:
            if bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': None,
                    'kommentar': 'aus Referenztabelle in der M150-Datei',
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if len(blocks) == 0:
            data = [
                ('Regenwasser', 'R'),
                ('Schmutzwasser', 'S'),
                ('Mischwasser', 'M'),
                ('Rinnen/Gräben', 'GR'),
                ('stillgelegt', 'X'),
                ('sonstige', 'U'),
            ]

            for (langtext, kuerzel) in data:
                params.append(
                    {
                        'bezext': langtext,
                        'kuerzel': kuerzel,
                        'bezqkan': langtext,
                        'kommentar': 'QKan-Standard',
                    }
                )

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'import_entwaesserungsarten', :kommentar
                    WHERE :bezext NOT IN (
                        SELECT bezext FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'import_entwaesserungsarten')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenztabelle Nr. 104 Kanalnutzung", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Referenztabelle eingefügt werden:'
                f'{params=}')
            raise QkanError

        # Patterns anwenden, damit möglicherweise der Anwender keine Zuordnungen mehr bearbeiten muss ...
        self.db_qkan._adapt_reftable('m150porter','import_entwaesserungsarten')

        # Neue Datensätze aus der Importdatei hinzufügen
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung)
                    SELECT coalesce(:bezqkan, :bezext), :kuerzel, :kommentar
                    WHERE coalesce(:bezqkan, :bezext) NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "M150 Import Referenzliste entwaesserungsarten", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Tabelle entwaesserungsarten eingefügt werden:'
                f'{params=}')
            raise QkanError

        # Referenztabelle Profile

        params = []

        blocks = self.xml.findall("RT/[RT001='106']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Profilart": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            bemerkung = block.findtext(
                "RT999",
                'aus Referenztabelle in der M150-Datei'
            )
            # Falls einer der beiden Einträge fehlt:
            if bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': bez,
                    'kommentar': bemerkung,
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if len(blocks) == 0:
            data = [
                ('Kreis', 'DN'),
                ('Rechteck', 'RE'),
                ('Ei (B:H = 2:3)', 'EI'),
                ('Maul (B:H = 2:1.66)', 'MA'),
                ('Halbschale (offen) (B:H = 2:1)', 'HS'),
                ('Kreis gestreckt (B:H=2:2.5)', None),
                ('Kreis überhöht (B:H=2:3)', None),
                ('Ei überhöht (B:H=2:3.5)', None),
                ('Ei breit (B:H=2:2.5)', None),
                ('Ei gedrückt (B:H=2:2)', None),
                ('Drachen (B:H=2:2)', None),
                ('Maul (DIN) (B:H=2:1.5)', None),
                ('Maul überhöht (B:H=2:2)', None),
                ('Maul gedrückt (B:H=2:1.25)', None),
                ('Maul gestreckt (B:H=2:1.75)', None),
                ('Maul gestaucht (B:H=2:1)', None),
                ('Haube (B:H=2:2.5)', 'BO'),
                ('Parabel (B:H=2:2)', None),
                ('Rechteck mit geneigter Sohle (B:H=2:1)', None),
                ('Rechteck mit geneigter Sohle (B:H=1:1)', None),
                ('Rechteck mit geneigter Sohle (B:H=1:2)', None),
                ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.2B)', None),
                ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.2B)', None),
                ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.2B)', None),
                ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.4B)', None),
                ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.4B)', None),
                ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.4B)', None),
                ('Sonderprofil', 68),
                ('Gerinne', 'RI'),
                ('Trapez (offen)', 'TR'),
                ('Rechteck offen', None),
                ('Doppeltrapez (offen)', None),
                ('Offener Graben', 'GR'),
                ('Oval', 'OV')
            ]

            for (langtext, kuerzel) in data:
                params.append(
                    {
                        'bezext': langtext,
                        'kuerzel': kuerzel,
                        'bezqkan': langtext,
                        'kommentar': 'ITWH-Standard',
                    }
                )

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'import_profile', :kommentar
                    WHERE :bezext NOT IN (
                        SELECT bezext FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'import_profile')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenztabelle Nr. 106 Profile", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Referenztabelle eingefügt werden: '
                f'{params=}')
            raise QkanError

        # Patterns anwenden, damit möglicherweise der Anwender keine Zuordnungen mehr bearbeiten muss ...
        self.db_qkan._adapt_reftable('m150porter', 'import_profile')

        # Neue Datensätze aus der Importdatei hinzufügen
        sql = """INSERT INTO profile (
                    profilnam, kuerzel, kommentar)
                SELECT coalesce(:bezqkan, :bezext), :kuerzel, :kommentar
                WHERE coalesce(:bezqkan, :bezext) NOT IN (SELECT profilnam FROM profile)"""
        if not self.db_qkan.sql(sql, "M150 Import Referenzliste profile", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Tabelle profile eingefügt werden:'
                f'{params=}')
            raise QkanError

        # Referenztabelle Simulationsarten (M150: Funktionszustand)

        params = []

        blocks = self.xml.findall("RT/[RT001='109']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Funktionszustand": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            bemerkung = block.findtext(
                "RT999",
                'aus Referenztabelle in der M150-Datei'
            )
            # Falls einer der beiden Einträge fehlt:
            if bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': bez,
                    'kommentar': bemerkung,
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if len(blocks) == 0:
            data = [
                ('in Betrieb', 'B'),
                ('außer Betrieb', 'AB'),
                ('geplant', 'P'),
                ('stillgelegt', 'N'),
                ('verdämmert', 'V'),
                ('fiktiv', 'F'),
                ('rückgebaut', 'P'),
            ]

            for (langtext, kuerzel) in data:
                params.append(
                    {
                        'bezext': langtext,
                        'kuerzel': kuerzel,
                        'bezqkan': langtext,
                        'kommentar': 'QKan-Standard',
                    }
                )

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'import_simulationsstatus', :kommentar
                    WHERE :bezext NOT IN (
                        SELECT bezext FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'import_simulationsstatus')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenztabelle Nr. 109 Funktionszustand", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Referenztabelle eingefügt werden: '
                f'{params=}')
            raise QkanError

        # Patterns anwenden, damit möglicherweise der Anwender keine Zuordnungen mehr bearbeiten muss ...
        self.db_qkan._adapt_reftable('m150porter', 'import_simulationsstatus')

        # Neue Datensätze aus der Importdatei hinzufügen
        sql = """INSERT INTO simulationsstatus (
                    bezeichnung, kuerzel, kommentar)
                SELECT coalesce(:bezqkan, :bezext), :kuerzel, :kommentar
                WHERE coalesce(:bezqkan, :bezext) NOT IN (SELECT bezeichnung FROM simulationsstatus)"""
        if not self.db_qkan.sql(sql, "M150 Import Referenzliste simulationsstatus", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Tabelle simulationsstatus eingefügt werden:'
                f'{params=}')
            raise QkanError

        # Referenztabelle Material

        params = []

        blocks = self.xml.findall("RT/[RT001='105']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Material": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            bemerkung = block.findtext(
                "RT999",
                'aus Referenztabelle in der M150-Datei'
            )
            # Falls einer der beiden Einträge fehlt:
            if bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': bez,
                    'kommentar': bemerkung,
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if len(blocks) == 0:
            data = [
                ('Asbestzement', 'AZ'),
                ('Beton', 'B'),
                ('Bitumen', 'BIT'),
                ('Betonsegmente', 'BS'),
                ('Betonsegmente kunststoffmodifiziert', 'BSK'),
                ('Bitumen', 'BT'),
                ('Edelstahl', 'CN'),
                ('Nichtidentifiziertes Metall (z. B. Eisen und Stahl)', 'EIS'),
                ('Epoxydharz', 'EPX'),
                ('Epoxydharz mit Synthesefaser', 'EPSF'),
                ('Faserzement', 'FZ'),
                ('Glasfaserverstärkter Kunststoff', 'GFK'),
                ('Grauguß', 'GG'),
                ('Duktiles Gußeisen', 'GGG'),
                ('Nichtidentifizierter Kunststoff', 'KST'),
                ('Mauerwerk', 'MA'),
                ('Ortbeton', 'OB'),
                ('Polymerbeton', 'PC'),
                ('Polymermodifizierter Zementbeton', 'PCC'),
                ('Polyethylen', 'PE'),
                ('Polyesterharz', 'PH'),
                ('Polyesterharzbeton', 'PHB'),
                ('Polypropylen', 'PP'),
                ('Polyurethanharz', 'PUR'),
                ('Polyvinylchlorid modifiziert', 'PVCM'),
                ('Polyvinylchlorid hart', 'PVCU'),
                ('Stahlfaserbeton', 'SFB'),
                ('Spannbeton', 'SPB'),
                ('Stahlbeton', 'SB'),
                ('Stahl', 'ST'),
                ('Steinzeug', 'STZ'),
                ('Spritzbeton', 'SZB'),
                ('Spritzbeton kunststoffmodifiziert', 'SZBK'),
                ('Teerfaser', 'TF'),
                ('Ungesättigtes Polyesterharz mit Glasfaser', 'UPGF'),
                ('Ungesättigtes Polyesterharz mit Synthesefaser', 'UPSF'),
                ('Vinylesterharz mit Synthesefaser', 'VEGF'),
                ('Vinylesterharz mit Glasfaser', 'VESF'),
                ('Verbundrohr Beton-/StahlbetonKun', 'VBK'),
                ('Verbundrohr Beton-/Stahlbeton Steinzeug', 'VBS'),
                ('Nichtidentifizierter Werkstoff', 'W'),
                ('Wickelrohr (PEHD)', 'WPE'),
                ('Wickelrohr (PVCU)', 'WPVC'),
                ('Zementmörtel', 'ZM'),
                ('Ziegelwerk', 'ZG'),
            ]

            for (langtext, kuerzel) in data:
                params.append(
                    {
                        'bezext': langtext,
                        'kuerzel': kuerzel,
                        'bezqkan': langtext,
                        'kommentar': 'M150-Standard',
                    }
                )

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'import_material', :kommentar
                    WHERE :bezext NOT IN (
                        SELECT bezext FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'import_material')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenztabelle Nr. 105 Bauwerksart", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Referenztabelle eingefügt werden: '
                f'{params=}')
            raise QkanError

        # Patterns anwenden, damit möglicherweise der Anwender keine Zuordnungen mehr bearbeiten muss ...
        self.db_qkan._adapt_reftable('m150porter', 'import_material')

        # Neue Datensätze aus der Importdatei hinzufügen
        sql = """INSERT INTO material (
                        bezeichnung, kuerzel, kommentar)
                    SELECT coalesce(:bezqkan, :bezext), :kuerzel, :kommentar
                    WHERE coalesce(:bezqkan, :bezext) NOT IN (SELECT bezeichnung FROM material)"""
        if not self.db_qkan.sql(sql, "M150 Import Referenzliste material", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Tabelle material eingefügt werden:'
                f'{params=}')
            raise QkanError

        # Referenztabelle Bauwerksarten

        params = []

        blocks = self.xml.findall("RT/[RT001='117']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Bauwerksart": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            # Falls einer der beiden Einträge fehlt:
            if bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': bez,
                    'kommentar': 'aus Referenztabelle in der M150-Datei',
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if len(blocks) == 0:
            data = [
                ('ZABA', 'Absturzbauwerk mit außenliegendem Untersturz'),
                ('ZABI', 'Absturzbauwerk mit innenliegendem Untersturz'),
                ('ZABK', 'Absturzbauwerk mit Kaskaden'),
                ('ZABS', 'Absturzbauwerk mit Schussrinne'),
                ('ZABU', 'Absturzbauwerk mit Untersturz'),
                ('ZAL',  'Auslaufbauwerk'),
                ('ZASA', 'Abscheideranlagen'),
                ('ZDUE', 'Düker'),
                ('ZERD', 'Bauwerk für erdverlegte Abwasserleitungen und -kanäle'),
                ('ZEL',  'Einlaufbauwerk'),
                ('ZES',  'Einsteigschacht'),
                ('ZFS',  'Fallschacht'),
                ('ZHEB', 'Heber'),
                ('ZKB',  'Kurvenbauwerk'),
                ('ZMS',  'Messschächte'),
                ('ZPW',  'Pumpwerke'),
                ('ZRKB', 'Regenklärbecken'),
                ('ZRRB', 'Regenrückhaltebecken'),
                ('ZRUB', 'Regenüberlaufbecken'),
                ('ZRUE', 'Regenüberlauf'),
                ('ZSA',  'Straßenablauf'),
                ('ZSB',  'Schieberbauwerk'),
                ('ZSS',  'Spülschacht'),
                ('ZVB',  'Verbindungsbauwerk'),
                ('ZVT',  'Verteilerwerke'),
                ('ZWS',  'Wirbelfallschacht'),
                ('Z',    'Sonstige'),
            ]

            for (langtext, kuerzel) in data:
                params.append(
                    {
                        'bezext': langtext,
                        'kuerzel': kuerzel,
                        'bezqkan': langtext,
                        'kommentar': 'M150-Standard',
                    }
                )

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'import_bauwerksarten', :kommentar
                    WHERE :bezext NOT IN (
                        SELECT bezext FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'import_bauwerksarten')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenztabelle Nr. 117 Bauwerksarten", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Referenztabelle eingefügt werden: '
                f'{params=}')
            raise QkanError

        # Patterns anwenden, damit möglicherweise der Anwender keine Zuordnungen mehr bearbeiten muss ...
        self.db_qkan._adapt_reftable('m150porter', 'import_bauwerksarten')

        # Straßen - in refdata, aber keine eigene Referenztabelle

        params = []

        blocks = self.xml.findall("RT/[RT001='001']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Straßen": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            # Falls einer der beiden Einträge fehlt:
            if kuerzel is None or bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': bez,
                    'kommentar': 'aus Referenztabelle in der M150-Datei',
                }
            )

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'strassen', :kommentar
                    WHERE :bezqkan NOT IN (
                        SELECT bezqkan FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'strassen')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenztabelle Nr. 101 Straßen", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Referenztabelle eingefügt werden: '
                f'{params=}')
            raise QkanError

        # Knotenarten aus Referenztabelle Nr. 116 einlesen.
        # Die Daten werden nur intern verarbeitet, weil unterschiedliche Tabellen betroffen sind.

        params = []

        blocks = self.xml.findall("RT/[RT001='116']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Knotenart": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)
            # Falls Kürzel nicht verwendet oder einer der beiden Einträge fehlt:
            if len(self.xml.findall(f".//KG[KG305='{kuerzel}']")) == 0 or kuerzel is None or bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': None,                     # anschließend durch den Anwender zu ergänzen
                    'kommentar': 'aus Referenztabelle in der M150-Datei',
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if len(blocks) == 0:
            #    bezeichnung, kuerzel,      schachttyp (qkan-Tabelle)
            data = [
                ('Auslass', 'A',            'Auslass'),
                ('Bauwerk', 'B',            'Speicher'),     # hier wird bewusst vereinfacht!
                ('Straßenablauf', 'E',      'Symbol'),       # wird in Tabelle symbole eingefügt
                ('Fiktiver Schacht', 'F',   'Schacht'),
                ('Gebäudeanschluss', 'G',   'Schacht'),
                ('Inspektionsöffnung', 'I', 'Symbol'),
                ('Lampenschacht', 'L',      'Symbol'),       # wird in Tabelle symbole eingefügt
                ('Reinigungsöffnung', 'R',  'Symbol'),       # wird in Tabelle symbole eingefügt
                ('Schacht', 'S',            'Schacht'),
                ('Sanitärgegenstand', 'W',  'Symbol'),       # wird in Tabelle symbole eingefügt
                ('Sonstige', 'Z',           'Symbol'),       # wird in Tabelle symbole eingefügt
            ]

            for (langtext, kuerzel, schachttyp) in data:
                params.append(
                    {
                        'bezext': langtext,
                        'kuerzel': kuerzel,
                        'bezqkan': schachttyp,
                        'kommentar': 'M150-Standard',
                    }
                )
            logger.debug("M150-Referenztabelle: Standardtabelle")

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'import_knotentypen', :kommentar
                    WHERE :bezext NOT IN (
                        SELECT bezext FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'import_knotentypen')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenzliste Nr. 116 Knotenart", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Tabelle m150_knotenarten eingefügt werden:'
                f'{params=}')
            raise QkanError

        # Patterns anwenden, damit möglicherweise der Anwender keine Zuordnungen mehr bearbeiten muss ...
        self.db_qkan._adapt_reftable('m150porter','import_knotentypen')

        # Prüfung, ob noch Zuordnungen NULL oder leer sind
        sql = """SELECT pk
            FROM refdata
            WHERE (bezqkan IS NULL OR bezqkan = '') 
              AND modul = 'm150porter'
              AND subject = 'import_knotentypen'"""

        self.db_qkan.sql(sql, f'{self.__class__.__name__}._reftables()')
        data = self.db_qkan.fetchone()
        knotenarten_uncomplete = (data is not None)

        # Referenztabelle Haltungsart (HG313)

        params = []

        blocks = self.xml.findall("RT/[RT001='108']")

        logger.debug(f'Anzahl Datensätze in M150-Referenztabelle "Haltungsart": {len(blocks)}')

        for block in blocks:
            kuerzel = block.findtext("RT002", None)
            bez = block.findtext("RT004", None)

            # Falls einer der beiden Einträge fehlt:
            if bez is None:
                continue
            params.append(
                {
                    'bezext': bez,
                    'kuerzel': kuerzel,
                    'bezqkan': bez,
                    'kommentar': 'aus Referenztabelle in der M150-Datei',
                }
            )

        # Falls keine Referenztabelle in der M150-Datei vorhanden ist:
        if len(blocks) == 0:
            data = [
                ('A' ,'Kanal', 'Haltung'),
                ('B', 'Anschlussleitung', 'Anschlussleitung'),
                ('C', 'Entlastungsleitung', 'Haltung'),
                ('Z', 'Sonstige', 'Haltung'),
            ]

            for (kuerzel, langtext, haltungstyp) in data:
                params.append(
                    {
                        'bezext': langtext,
                        'kuerzel': kuerzel,
                        'bezqkan': haltungstyp,
                        'kommentar': 'M150-Standard',
                    }
                )

        sql = """INSERT INTO refdata (
                    bezext, bezqkan, kuerzel, modul, subject, kommentar)
                    SELECT :bezext, :bezqkan, :kuerzel, 'm150porter', 'import_haltungsarten', :kommentar
                    WHERE :bezext NOT IN (
                        SELECT bezext FROM refdata
                        WHERE modul = 'm150porter'
                          AND subject = 'import_haltungsarten')"""
        if not self.db_qkan.sql(sql, "M150 Import Referenztabelle Nr. 108 Haltungsarten", params, many=True):
            logger.error_data(
                f'{self.__class__.__name__}: '
                f'Datensätze konnten nicht in Referenztabelle eingefügt werden: '
                f'{params=}')
            raise QkanError

        # Patterns anwenden, damit möglicherweise der Anwender keine Zuordnungen mehr bearbeiten muss ...
        self.db_qkan._adapt_reftable('m150porter','import_haltungsarten')

        # todo: Einlesen, Patterns, Mapper beim Einlesen von Haltungen, Anschlussleitungen einsetzen,
        #       Schächte ohne Koordinaten aus Haltungspunktdaten holen

        self.db_qkan.commit()

        return knotenarten_uncomplete

    def _init_mappers(self) -> None:

        # Entwässerungsarten
        # sql = "SELECT m150, FIRST_VALUE(bezeichnung) OVER (PARTITION BY m150 ORDER BY pk) " \
        #       "FROM entwaesserungsarten WHERE m150 IS NOT NULL GROUP BY m150"
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'import_entwaesserungsarten'"
        subject = "xml_import_entwaesserungsarten"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_entwart)

        # Profilarten
        # sql = "SELECT m150, FIRST_VALUE(profilnam) OVER (PARTITION BY m150 ORDER BY pk) " \
        #       "FROM profile WHERE m150 IS NOT NULL GROUP BY m150"
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'import_profile'"
        subject = "xml_import profile"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_profile)

        # sql = "SELECT he_nr, bezeichnung FROM pumpentypen"
        # subject = "xml_import pumpentypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_pump)

        # Materialarten
        # sql = "SELECT m150, FIRST_VALUE(bezeichnung) OVER (PARTITION BY m150 ORDER BY pk) " \
        #       "FROM material WHERE m150 IS NOT NULL GROUP BY m150"
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'import_material'"
        subject = "xml_import material"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_material)

        # sql = "SELECT he_nr, bezeichnung FROM auslasstypen"
        # subject = "xml_import auslasstypen"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_outlet)

        # Planungs-/Simulationsstatus
        # sql = "SELECT m150, FIRST_VALUE(bezeichnung) OVER (PARTITION BY m150 ORDER BY pk) " \
        #       "FROM simulationsstatus WHERE m150 IS NOT NULL GROUP BY m150"
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'import_simulationsstatus'"
        subject = "xml_import simulationsstatus"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_simstatus)

        # sql = "SELECT kuerzel, bezeichnung FROM untersuchrichtung"
        # subject = "xml_import untersuchrichtung"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_untersuchrichtung)

        # Wetter
        sql = "SELECT m150, FIRST_VALUE(bezeichnung) OVER (PARTITION BY m150 ORDER BY pk) " \
              "FROM wetter WHERE m150 IS NOT NULL GROUP BY m150"
        subject = "xml_import wetter"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_wetter)

        # Knotentypen
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'import_knotentypen'"
        subject = "xml_import m150_knotenarten"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_m150knotenarten)
        logger.debug(f'{self.mapper_m150knotenarten=}')

        # Bauwerksarten
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'import_bauwerksarten'"
        subject = "xml_import m150_bauwerksarten"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_bauwerksarten)
        logger.debug(f'{self.mapper_bauwerksarten=}')

        # Straßen
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'strassen'"
        subject = "xml_import m150_strassen"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_strassen)
        logger.debug(f'{self.mapper_strassen=}')

        # Haltungsarten
        sql = "SELECT kuerzel, bezqkan " \
              "FROM refdata WHERE modul = 'm150porter' AND subject = 'import_haltungsarten'"
        subject = "xml_import m150_haltungsarten"
        self.db_qkan.consume_mapper(sql, subject, self.mapper_haltungsarten)
        logger.debug(f'{self.mapper_haltungsarten=}')

        # sql = "SELECT kuerzel, bezeichnung FROM bewertungsart"
        # subject = "xml_import bewertungsart"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_bewertungsart)
        #
        # sql = "SELECT kuerzel, bezeichnung FROM druckdicht"
        # subject = "xml_import druckdicht"
        # self.db_qkan.consume_mapper(sql, subject, self.mapper_druckdicht)

        # XPATH-Filter zur Unterscheidung von Haltungen und Hausanschlussleitungen
        kuerzel = [
            key for key in self.mapper_haltungsarten
            if self.mapper_haltungsarten[key]=='Haltung'
        ]
        if kuerzel != []:
            self.m150_haltung = kuerzel[0]
        else:
            self.m150_haltung = None    # kein Kürzel für Hausanschlussleitung vorhanden

        kuerzel = [
            key for key in self.mapper_haltungsarten
            if self.mapper_haltungsarten[key]=='Hausanschlussleitung'
        ]
        if kuerzel != []:
            self.m150_anschlussleitung = kuerzel[0]
        else:
            self.m150_anschlussleitung = None    # kein Kürzel für Hausanschlussleitung vorhanden


    def _schaechte(self) -> None:
        """Schächte und Anschlussschächte einlesen"""
        def _iter() -> Iterator[Schacht]:
            blocks = self.xml.findall("KG")                                           # old: KG[KG305='S']

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name = block.findtext("KG001", None)

                # Entwässerungsarten
                entwart = self.db_qkan.get_from_mapper(
                    block.findtext("KG302", None),
                    self.mapper_entwart,
                    'schaechte',
                    'entwaesserungsarten',
                    'bezeichnung',
                    'm150',
                    'bemerkung',
                    'kuerzel',
                )

                # Simulationsstatus
                simstatus = self.db_qkan.get_from_mapper(
                    block.findtext("KG401", None),
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
                    block.findtext("KG304", None),
                    self.mapper_material,
                    'schacht',
                    'material',
                    'bezeichnung',
                    'm150',
                    'kommentar',
                    'kuerzel',
                )

                ka = block.findtext("KG305")
                knotenart = self.db_qkan.get_from_mapper(
                    key=ka,                                 # m150-Knotenart (Ref.-Tab. 116)
                    mapper=self.mapper_m150knotenarten,
                    table='Schacht/Anschlussschacht/Symbol',
                    default='Schacht',
                )
                logger.debug(f'Zuordnung {ka=} -> {knotenart=}')

                bauwerksart = self.db_qkan.get_from_mapper(
                    block.findtext("KG306"),                               # m150-Bauwerksart (Ref.-Tab. 117)
                    self.mapper_bauwerksarten,
                    'bauwerksarten',
                )
                # bauwerksart = self.mapper_bauwerkswart.get(bwart)

                # Pumpwerke und Wehre ausschließen, weil Linienobjekte
                # Bezeichnungen in Wertabbildung zu schachttyp in Layer "M150 Knotenarten"
                if knotenart in ('Pumpe', 'Wehr'):
                    continue

                if knotenart in ('Speicher', 'Schacht', 'Auslass', 'Anschlussschacht'):
                    schachttyp = knotenart
                else:
                    # alle anderen
                    schachttyp = 'Symbol'

                if knotenart == 'Anschlussschacht':
                    durchmesser = 0.25
                else:
                    durchmesser = 0.5
                geop, geom, sohlhoehe, deckelhoehe = self._get_KG_GO(block, name, durchmesser)
                if geop is None:
                    logger.warning(f'Kein Punktobjekt für Schacht "{name}" gefunden. Versuche alte M150-Felder KG201 ...')
                    geop, geom, sohlhohe, deckelhoehe = self._get_KG_201(block, name)

                yield Schacht(
                    schnam=name,
                    sohlhoehe=sohlhoehe,
                    deckelhoehe=deckelhoehe,
                    baujahr=_get_int(block,"KG303", None),
                    durchm=_get_float(block, "KG309", None),
                    druckdicht=_get_int(block, "KG315", None),
                    entwart=entwart,
                    strasse=block.findtext("KG102", None),
                    bauwerksart=bauwerksart,
                    schachttyp=schachttyp,
                    material=material,
                    simstatus=simstatus,
                    kommentar=block.findtext("KG999", None),
                    geom=geom,
                    geop=geop,
                )

        for schacht in _iter():

            # Je nach Knotentyp wird das Element unterschiedlichen Tabellen hinzugefügt!

            if schacht.schachttyp in ('Schacht', 'Auslass', 'Speicher'):
                params = {'schnam': schacht.schnam,
                          'sohlhoehe': schacht.sohlhoehe, 'deckelhoehe': schacht.deckelhoehe,
                          'bauwerksart': schacht.bauwerksart,
                          'durchm': schacht.durchm, 'druckdicht': schacht.druckdicht,
                          'entwart': schacht.entwart, 'strasse': schacht.strasse,
                          'baujahr': schacht.baujahr, 'material': schacht.material,
                          'simstatus': schacht.simstatus, 'kommentar': schacht.kommentar,
                          'geop': schacht.geop,
                          'geom': schacht.geom,
                          'schachttyp': schacht.schachttyp, 'epsg': QKan.config.epsg}
                try:
                    if not self.db_qkan.insertdata(
                            tabnam="schaechte",
                            stmt_category='m150-import schaechte',
                            mute_logger=False,
                            parameters=params,
                    ):
                        logger.error_data(
                            f'{self.__class__.__name__}: '
                            f'Schacht {schacht.schnam} kann nicht eingefügt werden')
                        raise QkanError
                except QkanDbError:
                    geop_err = QgsGeometry()
                    geop_err.fromWkb(schacht.geop)
                    geom_err = QgsGeometry()
                    geom_err.fromWkb(schacht.geom)
                    logger.error_code(f'Schachtdatensatz kann nicht eingefügt werden.\n'
                                      f'Punktobjekt: {geop_err.asWkt()}\n'
                                      f'Multilineobjekt: {geom_err.asWkt()}')
                    raise QkanDbError
            elif schacht.schachttyp == 'Anschlussschacht':
                params = {'schnam': schacht.schnam,
                          'sohlhoehe': schacht.sohlhoehe, 'deckelhoehe': schacht.deckelhoehe,
                          'bauwerksart': schacht.bauwerksart,
                          'durchm': schacht.durchm, 'druckdicht': schacht.druckdicht,
                          'entwart': schacht.entwart, 'strasse': schacht.strasse,
                          'baujahr': schacht.baujahr, 'material': schacht.material,
                          'simstatus': schacht.simstatus, 'kommentar': schacht.kommentar,
                          'geom': schacht.geop,
                          'epsg': QKan.config.epsg}
                if not self.db_qkan.insertdata(
                        tabnam="anschlussschaechte",
                        stmt_category='m150-import anschlussschaechte',
                        mute_logger=False,
                        parameters=params,
                ):
                    logger.error_data(
                        f'{self.__class__.__name__}: '
                        f'Anschlussschacht {schacht.schnam} kann nicht eingefügt werden')
                    raise QkanError
            else:
                params = {'bezeichnung': schacht.schnam,
                          'art': schacht.bauwerksart,
                          'gruppe': 'Entwässerung',
                          'kommentar': 'M150-Import',
                          'geom': schacht.geop,
                          'epsg': QKan.config.epsg,
                          }
                if not self.db_qkan.insertdata(
                        tabnam="symbole",
                        stmt_category='m150-import symbole',
                        mute_logger=False,
                        parameters=params,
                ):
                    logger.error_data(
                        f'{self.__class__.__name__}: '
                        f'Symbol {schacht.schnam} kann nicht eingefügt werden')
                    raise QkanError

        self.db_qkan.commit()

    def _schaechte_untersucht(self) -> None:
        def _iter() -> Iterator[Schacht_untersucht]:
            blocks = self.xml.findall("KG/KI/..")

            logger.debug(f"Anzahl Schächte: {len(blocks)}")

            for block in blocks:
                name = block.findtext("KG001", None)
                strasse = block.findtext("KG102", None)
                baujahr = _get_int(block, "KG303")

                geop, _, sohlhoehe, _ = self._get_KG_GO(block, name)

                if geop is None:
                    logger.warning(f'Kein Punktobjekt für Schacht_untersucht "{name}" gefunden. Versuche alte M150-Felder KG201 ...')
                    geop, _, sohlhohe, _ = self._get_KG_201(block, name)

                # smp = block.find("GO/GP")
                # if smp is None:
                #     fehlermeldung(
                #         "Fehler beim XML-Import: Schächte untersucht",
                #         f'Keine Geometrie "SMP" für Schacht {name}',
                #     )
                #     xsch, ysch, sohlhoehe = (0.0,) * 3
                # else:
                #     xsch = _get_float(smp, "GP003")
                #     if xsch is None:
                #         xsch = _get_float(smp, "GP005")
                #
                #     ysch =  _get_float(smp, "GP004")
                #     if ysch is None:
                #         ysch =  _get_float(smp, "GP006")
                #     sohlhoehe =  _get_float(smp, "GP007", 0.0)

                _schacht = block.find("KI")
                if _schacht:
                    untersuchtag = _schacht.findtext("KI104", None)
                    _datei = _schacht.findtext("KI/KI116", None)
                    if _datei:
                        film_dateiname = _datei.replace("\\", "/")
                    else:
                        film_dateiname = None
                    untersucher = _schacht.findtext("KI112", None)
                    wetter = _schacht.findtext("KI106", None)
                    bewertungsart = _schacht.findtext("KI005", None)
                    bewertungstag = _schacht.findtext("KI204", None)
                    max_ZD = _get_int(_schacht, "KI206", None)
                    max_ZB = _get_int(_schacht, "KI208", None)
                    max_ZS = _get_int(_schacht, "KI207", None)
                else:
                    untersuchtag = ""
                    untersucher = ""
                    wetter = ""
                    bewertungsart = ""
                    bewertungstag = ""
                    max_ZD = None
                    max_ZB = None
                    max_ZS = None
                datenart = self.datenart

                yield Schacht_untersucht(
                    schnam=name,
                    strasse=strasse,
                    sohlhoehe=sohlhoehe,
                    durchm=1.0,  # TODO: Not listed in ISYBAU?
                    baujahr=baujahr,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    film_dateiname=film_dateiname,
                    wetter=wetter,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                    max_ZD=max_ZD,
                    max_ZB=max_ZB,
                    max_ZS=max_ZS,
                    geop=geop,
                )

        for schacht_untersucht in _iter():

            # Wetter
            # wetter = self.db_qkan.get_from_mapper(
            #     schacht_untersucht.wetter,
            #     self.mapper_wetter,
            #     'schaechte_untersucht',
            #     'wetter',
            #     'bezeichnung',
            #     'm150',
            #     'bemerkung',
            #     'kuerzel',
            # )

            # Datensatz einfügen
            params = {'schnam': schacht_untersucht.schnam,
                      'durchm': schacht_untersucht.durchm, 'kommentar': schacht_untersucht.kommentar,
                      'untersuchtag': schacht_untersucht.untersuchtag, 'untersucher': schacht_untersucht.untersucher,
                      'wetter': schacht_untersucht.wetter,
                      'baujahr': schacht_untersucht.baujahr, 'bewertungsart': schacht_untersucht.bewertungsart,
                      'bewertungstag': schacht_untersucht.bewertungstag,
                      'datenart': schacht_untersucht.datenart, 'max_ZD': schacht_untersucht.max_ZD,
                      'max_ZB': schacht_untersucht.max_ZB, 'max_ZS': schacht_untersucht.max_ZS,
                      'geop': schacht_untersucht.geop, 'epsg': QKan.config.epsg}

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: schaechte_untersucht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="schaechte_untersucht",
                    stmt_category='m150-import schachte_untersucht',
                    mute_logger=False,
                    parameters=params,
            ):
                return

            params = {'name': schacht_untersucht.schnam,
                      'untersuchtag': schacht_untersucht.untersuchtag,
                      'datei': schacht_untersucht.film_dateiname, 'objekt': 'Schacht'}

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

    def _untersuchdat_schaechte(self) -> None:
        def _iter() -> Iterator[Untersuchdat_schacht]:
            blocks = self.xml.findall("KG/KI/..")

            logger.debug(f"Anzahl Untersuchungsdaten Schacht: {len(blocks)}")

            name = ""
            inspektionslaenge = 0.0
            id = 0
            videozaehler = ""
            timecode = ""
            kuerzel = ""
            langtext = ""
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
            film_dateiname = ""
            ZD = None
            ZB = None
            ZS = None

            for block in blocks:

                name = block.findtext("KG001", None)
                untersuchtag = block.findtext("KI/KI104")


                for _untersuchdat_schacht in block.findall("KI/KZ"):

                    #id = _get_int(_untersuchdat_schacht.findtext("d:Index", "0", self.NS))
                    inspektionslaenge =  _get_float(_untersuchdat_schacht, "KZ001", 0.0)
                    videozaehler = _untersuchdat_schacht.findtext("KZ008")
                    timecode = _untersuchdat_schacht.findtext("KZ008", None)
                    kuerzel = _untersuchdat_schacht.findtext("KZ002", None)
                    langtext = _untersuchdat_schacht.findtext("KZ010", None)
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

                    _datei = _untersuchdat_schacht.findtext("KZ009", None)
                    if _datei and self.ordner_bild:
                        foto_dateiname = os.path.join(self.ordner_bild, _datei).replace("\\","/")
                    else:
                        foto_dateiname = None

                    ZD = _get_int(_untersuchdat_schacht, "KZ206", None)
                    ZB = _get_int(_untersuchdat_schacht, "KZ208", None)
                    ZS = _get_int(_untersuchdat_schacht, "KZ207", None)


                    yield Untersuchdat_schacht(
                    untersuchsch = name,
                    id = id,
                    untersuchtag = untersuchtag,
                    videozaehler = videozaehler,
                    timecode = timecode,
                    kuerzel = kuerzel,
                    langtext = langtext,
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
                    ordner_bild = self.ordner_bild,
                    ZD=ZD,
                    ZB=ZB,
                    ZS=ZS,
                    )

        untersuchdat_schacht = None
        for untersuchdat_schacht in _iter():

            params = {'untersuchsch': untersuchdat_schacht.untersuchsch, 'id': untersuchdat_schacht.id,
                      'untersuchtag': untersuchdat_schacht.untersuchtag,
                      'videozaehler': untersuchdat_schacht.videozaehler, 'timecode': untersuchdat_schacht.timecode,
                      'kuerzel': untersuchdat_schacht.kuerzel, 'langtext': untersuchdat_schacht.langtext,
                      'charakt1': untersuchdat_schacht.charakt1,
                      'charakt2': untersuchdat_schacht.charakt2, 'quantnr1': untersuchdat_schacht.quantnr1,
                      'quantnr2': untersuchdat_schacht.quantnr2, 'streckenschaden': untersuchdat_schacht.streckenschaden,
                      'streckenschaden_lfdnr': untersuchdat_schacht.streckenschaden_lfdnr, 'pos_von': untersuchdat_schacht.pos_von,
                      'pos_bis': untersuchdat_schacht.pos_bis, 'vertikale_lage': untersuchdat_schacht.vertikale_lage,
                      'inspektionslage': untersuchdat_schacht.inspektionslaenge, 'bereich': untersuchdat_schacht.bereich,
                      'foto_dateiname': untersuchdat_schacht.foto_dateiname, 'ordner_bild': untersuchdat_schacht.ordner_bild,
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

        # Textpositionen für Schadenstexte berechnen

        #self.db_qkan.setschadenstexte_schaechte()
        if untersuchdat_schacht is not None:
            Schadenstexte.setschadenstexte_schaechte(self.db_qkan)

    # def _auslaesse(self) -> None:
    #     def _iter() -> Iterator[Schacht]:
    #         blocks = self.xml.findall("KG[KG305='A']")
    #
    #         logger.debug(f"Anzahl Ausläufe: {len(blocks)}")
    #
    #         for block in blocks:
    #             #name, knotentyp, xsch, ysch, sohlhoehe = self._consume_smp_block(block)
    #
    #             name = block.findtext("KG001", None)
    #             baujahr = _get_int(block,"KG303", 0)
    #             schachttyp = "Auslass"                       # QKan-Logik
    #
    #             geop, geom, sohlhoehe, deckelhoehe = self._get_KG_GO(block, name)
    #
    #             if geop is None:
    #                 geop, geom, sohlhohe, deckelhoehe = self._get_KG_201(block, name)
    #
    #             # smp = block.find("GO[GO002='G']/GP")
    #             # if smp is None:
    #             #     smp = block.find("GO[GO002='B']/GP")
    #             #
    #             # if smp is None:
    #             #     fehlermeldung(
    #             #         "Fehler beim XML-Import: Schächte",
    #             #         f'Keine Geometrie "SMP[GO002=\'G\']" oder "SMP[GO002=\'B\']" für Auslass {name}',
    #             #     )
    #             #     xsch, ysch, sohlhoehe = (0.0,) * 3
    #             # else:
    #             #     xsch =  _get_float(smp, "GP003")
    #             #     if xsch is None:
    #             #         xsch =  _get_float(smp, "GP005")
    #             #
    #             #     ysch =  _get_float(smp, "GP004")
    #             #     if ysch is None:
    #             #         ysch =  _get_float(smp, "GP006")
    #             #
    #             #     sohlhoehe =  _get_float(smp, "GP007", 0.0)
    #             #
    #             # smpD = block.find("GO[GO002='D']/GP")
    #             #
    #             # if smpD == None:
    #             #     deckelhoehe = None
    #             #
    #             # else:
    #             #     deckelhoehe =  _get_float(smpD, "GP007", 0.0)
    #
    #             yield Schacht(
    #                 schnam=name,
    #                 sohlhoehe=sohlhoehe,
    #                 deckelhoehe=deckelhoehe,
    #                 baujahr=baujahr,
    #                 durchm= _get_float(block, "KG309", 0.0),
    #                 entwart=block.findtext("KG302", None),
    #                 strasse=block.findtext("KG102", None),
    #                 bauwerksart=None,
    #                 simstatus=block.findtext("KG401", None),
    #                 kommentar=block.findtext("KG999", None),
    #                 geop=geop,
    #                 geom=geom,
    #             )
    #
    #     for auslass in _iter():
    #
    #         # Entwässerungsarten
    #         entwart = self.db_qkan.get_from_mapper(
    #             auslass.entwart,
    #             self.mapper_entwart,
    #             'Auslässe',
    #             'entwaesserungsarten',
    #             'bezeichnung',
    #             'm150',
    #             'bemerkung',
    #             'kuerzel',
    #         )
    #
    #         # Simstatus
    #         simstatus = self.db_qkan.get_from_mapper(
    #             auslass.simstatus,
    #             self.mapper_simstatus,
    #             'Auslässe',
    #             'simulationsstatus',
    #             'bezeichnung',
    #             'm150',
    #             'kommentar',
    #             'kuerzel',
    #         )
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
    #         params = {'schnam': auslass.schnam,
    #                   'sohlhoehe': auslass.sohlhoehe, 'deckelhoehe': auslass.deckelhoehe, 'baujahr': auslass.baujahr,
    #                   'durchm': auslass.durchm, 'entwart': entwart, 'strasse': auslass.strasse, 'simstatus': simstatus,
    #                   'kommentar': auslass.kommentar, 'schachttyp': 'Auslass',
    #                   'geop': auslass.geop, 'geom': auslass.geom, 'epsg': QKan.config.epsg}
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

    def _haltungen(self) -> None:
        def _iter() -> Iterator[Haltung]:
            blocks = self.xml.findall(f"HG")

            logger.debug(f"Anzahl Haltungen: {len(blocks)}")

            for block in blocks:
                # Objekte, deren Haltungsart nicht 'Haltung' ist, überspringen
                if self.m150_haltung is not None:
                    haltungsart = block.findtext("HG313", None)
                    if haltungsart is not None and haltungsart != self.m150_haltung:
                        continue
                name = block.findtext("HG001")
                if name is None:
                    name = block.findtext("HG002", None)

                baujahr = _get_int(block,"HG303", 0)

                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)

                laenge = _get_float(block, "HG314", None)
                if laenge is None:
                    laenge = _get_float(block, "HG310", None)

                material = block.findtext("HG304", None)

                profilauskleidung = block.findtext("HG008", None)
                innenmaterial = block.findtext("HG009", None)


                profilnam = block.findtext("HG305", None)
                hoehe = (_get_float(block, "HG307", 0.0))
                breite = (_get_float(block, "HG306", 0.0))

                geom, sohleoben, sohleunten, *_ = self._get_HG_GO(block, name)
                if geom is None:
                    logger.warning(f'Kein Punktobjekt für Haltung "{name}" gefunden. Versuche alte M150-Felder HG201 ...')
                    geom, sohleoben, sohleunten = self._get_HG_201(block, name)

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
                    profilnam=profilnam,
                    baujahr=baujahr,
                    entwart=block.findtext("HG302", None),
                    strasse=block.findtext("HG102", None),
                    ks=1.5,  # in Hydraulikdaten enthalten.
                    simstatus=block.findtext("HG401", None),
                    kommentar=block.findtext("HG999", None),
                    aussendurchmesser=None,
                    profilauskleidung=profilauskleidung,
                    innenmaterial=innenmaterial,
                    geom=geom,
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
                      'ks': haltung.ks, 'simstatus': simstatus, 'kommentar': haltung.kommentar,
                      'geom': haltung.geom, 'epsg': QKan.config.epsg}

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

    #Haltung_untersucht
    def _haltungen_untersucht(self) -> None:
        def _iter() -> Iterator[Haltung_untersucht]:
            if self.m150_haltung is None:
                blocks = self.xml.findall(f"HG/HI/..")
            else:
                blocks = self.xml.findall(f"HG[HG313='{self.m150_haltung}']/HI/..")
            logger.debug(f"Anzahl Haltungen untersucht: {len(blocks)}")

            for block in blocks:
                # Anschlussleitungen überspringen
                # if block.findtext("HG005") or block.findtext("HG006"):
                #     continue

                name = block.findtext("HG001", None)
                if name is None:
                    name = block.findtext("HG002", None)

                baujahr = _get_int(block, "HG303", 0)

                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)

                laenge = _get_float(block, "HG314", None)
                if laenge is None:
                    laenge = _get_float(block, "HG310", None)

                hoehe = _get_float(block, "HG307")
                breite = _get_float(block, "HG306")

                strasse = block.findtext("HG102", None)
                kommentar = block.findtext("HG999", None)

                geom, sohleoben, sohleunten, *_ = self._get_HG_GO(block, name)
                if geom is None:
                    logger.warning(f'Kein Punktobjekt für Haltung_untersucht "{name}" gefunden. Versuche alte M150-Felder HG201 ...')
                    geom, sohleoben, sohleunten = self._get_HG_201(block, name)

                # coords = []
                # geom = None
                #
                # for _gp in block.findall("GO/GP"):
                #
                #     xsch = _get_float(_gp, "GP003")
                #     if xsch is None:
                #         xsch = _get_float(_gp, "GP005")
                #     ysch = _get_float(_gp, "GP004")
                #     if ysch is None:
                #         ysch = _get_float(_gp, "GP006")
                #
                #     coords.append((xsch, ysch))
                #
                # # Linienobjekt aus Punktobjekten
                # if len(coords) > 0:
                #     pts = [QgsPoint(x, y) for x, y in coords]
                #     line = QgsGeometry.fromPolyline(pts)
                #     geom = line.asWkb()
                # else:
                #     geom = None

                _haltung = block.find("HI")
                if _haltung:
                    untersuchtag = _haltung.findtext("HI104", None)
                    _datei = _haltung.findtext("HI116", None)
                    if _datei:
                        film_dateiname = _datei.replace("\\", "/")
                    else:
                        film_dateiname = None
                    untersucher = _haltung.findtext("HI112", None)
                    wetter = _haltung.findtext("HI106", None)
                    bewertungsart = _haltung.findtext("HI005", None)
                    bewertungstag = _haltung.findtext("HI204", None)
                    max_ZD = _get_int(_haltung, "HI206", None)
                    max_ZB = _get_int(_haltung, "HI208", None)
                    max_ZS = _get_int(_haltung, "HI207", None)

                    _val = _haltung.findtext("HI101", None)
                    if _val == "I":
                        untersuchrichtung = "in Fließrichtung"
                    elif _val == "G":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.info(f"Untersuchungsdaten Haltung: Feld HI/HI101 fehlt oder falscher Wert: {_val}")
                        continue

                    _val = block.findtext("HI/HI102")
                    if _val == 'A' or not _val:
                        bezugspunkt = enums.UntersuchBezugpunkt.ROHRANFANG.value
                    else:
                        bezugspunkt = enums.UntersuchBezugpunkt.GERINNEMITTELPUNKT.value    # HI 102 in ('C' , 'D', 'Z')

                else:
                    untersuchtag = None
                    untersucher = None
                    untersuchrichtung = None
                    bezugspunkt = None
                    wetter = ""
                    bewertungsart = None
                    bewertungstag = None
                    max_ZD = None
                    max_ZB = None
                    max_ZS = None
                datenart = self.datenart

                yield Haltung_untersucht(
                    haltnam=name,
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    strasse=strasse,
                    kommentar=kommentar,
                    baujahr=baujahr,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    untersuchrichtung=untersuchrichtung,
                    film_dateiname=film_dateiname,
                    bezugspunkt=bezugspunkt,
                    wetter=wetter,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                    max_ZD=max_ZD,
                    max_ZB=max_ZB,
                    max_ZS=max_ZS,
                    geom=geom,
                )

        for haltung_untersucht in _iter():

            params = {'haltnam': haltung_untersucht.haltnam,
                      'schoben': haltung_untersucht.schoben,
                      'schunten': haltung_untersucht.schunten, 'hoehe': haltung_untersucht.hoehe,
                      'breite': haltung_untersucht.breite, 'laenge': haltung_untersucht.laenge,
                      'kommentar': haltung_untersucht.kommentar, 'baujahr': haltung_untersucht.baujahr,
                      'strasse': haltung_untersucht.strasse,
                      'untersuchtag': haltung_untersucht.untersuchtag,
                      'untersuchrichtung': haltung_untersucht.untersuchrichtung,
                      'bezugspunkt': haltung_untersucht.bezugspunkt,
                      'untersucher': haltung_untersucht.untersucher, 'wetter': haltung_untersucht.wetter,
                      'bewertungsart': haltung_untersucht.bewertungsart,
                      'bewertungstag': haltung_untersucht.bewertungstag,
                      'datenart': haltung_untersucht.datenart, 'max_ZD': haltung_untersucht.max_ZD,
                      'max_ZB': haltung_untersucht.max_ZB, 'max_ZS': haltung_untersucht.max_ZS,
                      'geom': haltung_untersucht.geom, 'epsg': QKan.config.epsg,
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

            params = {'name': haltung_untersucht.haltnam, 'untersuchtag': haltung_untersucht.untersuchtag,
                      'untersuchrichtung': haltung_untersucht.untersuchrichtung,
                      'datei': haltung_untersucht.film_dateiname, 'objekt': 'Haltung'}

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

    def _untersuchdat_haltung(self) -> None:
        def _iter() -> Iterator[Untersuchdat_haltung]:
            if self.m150_haltung is None:
                blocks = self.xml.findall(f"HG/HI/..")
            else:
                blocks = self.xml.findall(f"HG[HG313='{self.m150_haltung}']/HI/..")

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
            langtext = ""
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
            ZD = None
            ZB = None
            ZS = None


            for block in blocks:

                name = block.findtext("HG001", None)
                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)
                _val = block.findtext("HI/HI101", None)
                if _val == "I":
                    untersuchrichtung = "in Fließrichtung"
                elif _val == "G":
                    untersuchrichtung = "gegen Fließrichtung"
                else:
                    logger.info(f"Untersuchungsdaten Haltung: Feld HI/HI101 fehlt oder falscher Wert: {_val}")
                    continue

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
                    langtext = _untersuchdat.findtext("HZ010", None)
                    charakt1 = _untersuchdat.findtext("HZ014", None)
                    charakt2 = _untersuchdat.findtext("HZ015", None)
                    quantnr1 = _get_float(_untersuchdat, "HZ003", 0.0)
                    quantnr2 = _get_float(_untersuchdat, "HZ004", 0.0)
                    _text = _untersuchdat.findtext("HZ005", None)
                    if _text:
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

                    _datei = _untersuchdat.findtext("HZ009", None)
                    if _datei and self.ordner_bild:
                        foto_dateiname = os.path.join(self.ordner_bild, _datei).replace("\\","/")
                    else:
                        foto_dateiname = None

                    ZD = _get_int(_untersuchdat, "HZ206", None)
                    ZB = _get_int(_untersuchdat, "HZ208", None)
                    ZS = _get_int(_untersuchdat, "HZ207", None)

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
                    langtext=langtext,
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

        untersuchdat_haltung = None
        for untersuchdat_haltung in _iter():

            params = {'untersuchhal': untersuchdat_haltung.untersuchhal, 'untersuchrichtung': untersuchdat_haltung.untersuchrichtung,
                      'schoben': untersuchdat_haltung.schoben, 'schunten': untersuchdat_haltung.schunten,
                      'id': untersuchdat_haltung.id, 'untersuchtag': untersuchdat_haltung.untersuchtag,
                      'videozaehler': untersuchdat_haltung.videozaehler,
                      'inspektionslaenge': untersuchdat_haltung.inspektionslaenge, 'station': untersuchdat_haltung.station,
                      'timecode': untersuchdat_haltung.timecode, 'langtext': untersuchdat_haltung.langtext,
                      'kuerzel': untersuchdat_haltung.kuerzel,
                      'charakt1': untersuchdat_haltung.charakt1, 'charakt2': untersuchdat_haltung.charakt2,
                      'quantnr1': untersuchdat_haltung.quantnr1, 'quantnr2': untersuchdat_haltung.quantnr2,
                      'streckenschaden': untersuchdat_haltung.streckenschaden, 'streckenschaden_lfdnr': untersuchdat_haltung.streckenschaden_lfdnr,
                      'pos_von': untersuchdat_haltung.pos_von, 'pos_bis': untersuchdat_haltung.pos_bis,
                      'foto_dateiname': untersuchdat_haltung.foto_dateiname,
                      'ordner_bild': untersuchdat_haltung.ordner_bild,
                       'ZD': untersuchdat_haltung.ZD,
                      'ZB': untersuchdat_haltung.ZB, 'ZS': untersuchdat_haltung.ZS}

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_haltung",
                    stmt_category='m150-import untersuchdat_haltung',
                    mute_logger=False,
                    parameters=params,
            ):
                return

        self.db_qkan.commit()

        # Textpositionen für Schadenstexte berechnen
        #self.db_qkan.setschadenstexte_haltungen()
        if untersuchdat_haltung is not None:
            Schadenstexte.setschadenstexte_haltungen(self.db_qkan)

    def _anschlussleitungen(self) -> None:
        if self.m150_anschlussleitung is None:
            return

        def _iter() -> Iterator[Anschlussleitung]:
            blocks = self.xml.findall(f"HG[HG313='{self.m150_anschlussleitung}']")

            logger.debug(f"Anzahl Hausanschlussleitungen: {len(blocks)}")

            for block in blocks:
                leitnam = block.findtext("HG011", None)

                baujahr = _get_int(block,"HG303", None)

                haltnam = block.findtext("HG001", None)
                laenge = _get_float(block, "HG310", None)

                urstation_t = _get_float(block, "HG007", None)
                inFliessrichtung = (block.findtext("HG008", None) != 'G')
                if inFliessrichtung:
                    urstation = urstation_t
                elif urstation_t is not None:
                    kindVon = block.findtext("HG012", None)
                    if kindVon is not None:
                        # schließt an weitere Hausanschlussleitung an
                        hblocks = self.xml.findall(f"HG[HG011='{kindVon}']")
                        haltungslaenge = None
                        for hblock in hblocks:
                            # letzter wird übernommen
                            haltungslaenge = _get_float(hblock, "HG314", None)
                        if haltungslaenge is None:
                            haltungslaenge = _get_float(hblock, "HG310", None)
                    else:
                        # schließt an Haltung an
                        hblocks = self.xml.findall(f"HG[HG001='{haltnam}']")
                        haltungslaenge = None
                        for hblock in hblocks:
                            # letzter wird übernommen
                            haltungslaenge = _get_float(hblock, "HG314", None)
                        if haltungslaenge is None:
                            haltungslaenge = _get_float(hblock, "HG310", None)
                    if haltungslaenge is not None:
                        urstation = round(float(haltungslaenge) - urstation_t, 3)
                    else:
                        urstation = None
                else:
                    urstation = None
                material = block.findtext("HG304", None)

                profilnam = block.findtext("HG305", None)
                breite = _get_float(block, "HG306", None)
                hoehe = _get_float(block, "HG307", None)

                lageanschluss = _get_int(block, "HG009")

                geom, sohleoben, sohleunten, schoben, schunten = self._get_HG_GO(
                    block,
                    leitnam,
                )
                if geom is None:
                    logger.warning(f'Kein Punktobjekt für Anschlussleitung "{leitnam}" gefunden. Versuche alte M150-Felder HG201 ...')
                    geom, sohleoben, sohleunten = self._get_HG_201(block, leitnam)

                yield Anschlussleitung(
                    leitnam=leitnam,
                    schoben=schoben,
                    schunten=schunten,
                    haltnam=haltnam,
                    urstation=urstation,
                    inFliessrichtung=inFliessrichtung,
                    lageanschluss=lageanschluss,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    material=material,
                    baujahr=baujahr,
                    sohleoben=sohleoben,
                    sohleunten=sohleunten,
                    deckeloben=None,
                    deckelunten=None,
                    profilnam=profilnam,
                    entwart=block.findtext("HG302", None),
                    ks=1.5,                                         # in Hydraulikdaten enthalten.
                    simstatus=block.findtext("HG401", None),
                    kommentar=block.findtext("HG999", None),
                    geom=geom,
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

            params = {'leitnam': anschlussleitung.leitnam,
                      'schoben': anschlussleitung.schoben, 'schunten': anschlussleitung.schunten,
                      'haltnam': anschlussleitung.haltnam,
                      'urstation': anschlussleitung.urstation,
                      'inFliessrichtung,': anschlussleitung.inFliessrichtung,
                      'lageanschluss,': anschlussleitung.lageanschluss,
                      'hoehe': anschlussleitung.hoehe, 'breite': anschlussleitung.breite,
                      'laenge': anschlussleitung.laenge, 'material': material,
                      'sohleoben': anschlussleitung.sohleoben, 'sohleunten': anschlussleitung.sohleunten,
                      'deckeloben': anschlussleitung.deckeloben, 'deckelunten': anschlussleitung.deckelunten,
                      'profilnam': profilnam, 'entwart': entwart, 'baujahr': anschlussleitung.baujahr,
                      'ks': anschlussleitung.ks, 'simstatus': simstatus,
                      'kommentar': anschlussleitung.kommentar,
                      'geom': anschlussleitung.geom , 'epsg': QKan.config.epsg}

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen",
                    stmt_category='m150-import anschlussleitung',
                    mute_logger=False,
                    parameters=params,
            ):
                logger.error_data("Fehler beim Einfügen")
                raise QkanDbError

            if not anschlussleitung.inFliessrichtung:
                if not self.db_qkan.sqlyml(
                    sqlnam='m150_im_stationierung_umkehren',
                    stmt_category='m150_im_stationierung_umkehren',
                    parameters={'leitnam': anschlussleitung.leitnam}
                ):
                    logger.error_data("Fehler beim Einfügen")
                    raise QkanDbError

        self.db_qkan.commit()

    def _anschluss_untersucht(self) -> None:
        if self.m150_anschlussleitung is None:
            return

        def _iter() -> Iterator[Anschlussleitung_untersucht]:
            blocks = self.xml.findall(f"HG[HG313='{self.m150_anschlussleitung}']/HI/..")
            logger.debug(f"Anzahl Hausanschlussleitungen untersucht: {len(blocks)}")

            for block in blocks:
                name = block.findtext("HG001", None)
                if name is None:
                    name = block.findtext("HG002", None)

                baujahr = _get_int(block,"HG303", 0)

                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)

                laenge = _get_float(block,"HG314", None)
                if laenge is None:
                    laenge = _get_float(block, "HG310", None)

                hoehe = (_get_float(block,"HG307", 0.0))
                breite = (_get_float(block,"HG306", 0.0))

                strasse = block.findtext("HG102", None)
                kommentar = block.findtext("HG999", None)

                geom, sohleoben, sohleunten, *_ = self._get_HG_GO(block, name)
                if geom is None:
                    logger.warning(f'Kein Punktobjekt für Anschlussleitung_untersucht "{name}" gefunden. Versuche alte M150-Felder HG201 ...')
                    geom, sohleoben, sohleunten = self._get_HG_201(block, name)

                # coords = []
                # geom = None
                #
                # for _gp in block.findall("GO/GP"):
                #
                #     xsch = _get_float(_gp, "GP003")
                #     if xsch is None:
                #         xsch = _get_float(_gp, "GP005")
                #     ysch = _get_float(_gp, "GP004")
                #     if ysch is None:
                #         ysch = _get_float(_gp, "GP006")
                #
                #     coords.append((xsch, ysch))
                #
                # # Linienobjekt aus Punktobjekten
                # if len(coords) > 0:
                #     pts = [QgsPoint(x, y) for x, y in coords]
                #     line = QgsGeometry.fromPolyline(pts)
                #     geom = line.asWkb()
                # else:
                #     geom = None

                _haltung = block.find("HI")
                if _haltung:
                    untersuchtag = _haltung.findtext("HI104", None)
                    _datei = _haltung.findtext("HI116", None)
                    if _datei:
                        film_dateiname = _datei.replace("\\", "/")
                    else:
                        film_dateiname = None

                    untersucher = _haltung.findtext("HI112", None)
                    wetter = _haltung.findtext("HI106", None)
                    bewertungsart = _haltung.findtext("HI005", None)
                    bewertungstag = _haltung.findtext("HI204", None)
                    max_ZD = _get_int(_haltung, "HI206", None)
                    max_ZB = _get_int(_haltung, "HI208", None)
                    max_ZS = _get_int(_haltung, "HI207", None)

                    _val = _haltung.findtext("HI101", None)
                    if _val == "I":
                        untersuchrichtung = "in Fließrichtung"
                    elif _val == "G":
                        untersuchrichtung = "gegen Fließrichtung"
                    else:
                        logger.info(f"Untersuchungsdaten Haltung: Feld HI/HI101 fehlt oder falscher Wert: {_val}")
                        continue

                    _val = block.findtext("HI/HI102")
                    if _val == 'A' or not _val:
                        bezugspunkt = enums.UntersuchBezugpunkt.ROHRANFANG.value
                    else:
                        bezugspunkt = enums.UntersuchBezugpunkt.GERINNEMITTELPUNKT.value    # HI 102 in ('C' , 'D', 'Z')
                else:
                    untersuchtag = None
                    untersucher = None
                    wetter = ""
                    bewertungsart = None
                    bewertungstag = None
                    max_ZD = None
                    max_ZB = None
                    max_ZS = None
                    untersuchrichtung = None
                    bezugspunkt = None
                datenart = self.datenart

                yield Anschlussleitung_untersucht(
                    haltnam=name,                                   # Hinweis: Anschlussleitung_untersucht = Haltung_untersucht
                    schoben=schoben,
                    schunten=schunten,
                    hoehe=hoehe,
                    breite=breite,
                    laenge=laenge,
                    strasse=strasse,
                    kommentar=kommentar,
                    baujahr=baujahr,
                    untersuchtag=untersuchtag,
                    untersucher=untersucher,
                    untersuchrichtung=untersuchrichtung,
                    film_dateiname=film_dateiname,
                    bezugspunkt=bezugspunkt,
                    wetter=wetter,
                    bewertungsart=bewertungsart,
                    bewertungstag=bewertungstag,
                    datenart=datenart,
                    max_ZD=max_ZD,
                    max_ZB=max_ZB,
                    max_ZS=max_ZS,
                    geom=geom,
                )

        for anschluss_untersucht in _iter():

            params = {'leitnam': anschluss_untersucht.haltnam,      # Hinweis: Anschlussleitung_untersucht = Haltung_untersucht
                      'schoben': anschluss_untersucht.schoben,
                      'schunten': anschluss_untersucht.schunten, 'hoehe': anschluss_untersucht.hoehe,
                      'breite': anschluss_untersucht.breite, 'laenge': anschluss_untersucht.laenge,
                      'kommentar': anschluss_untersucht.kommentar, 'baujahr': anschluss_untersucht.baujahr,
                      'strasse': anschluss_untersucht.strasse,
                      'untersuchtag':anschluss_untersucht.untersuchtag,
                      'untersuchrichtung': anschluss_untersucht.untersuchrichtung,
                      'bezugspunkt': anschluss_untersucht.bezugspunkt,
                      'untersucher': anschluss_untersucht.untersucher, 'wetter': anschluss_untersucht.wetter,
                      'bewertungsart': anschluss_untersucht.bewertungsart,
                      'bewertungstag': anschluss_untersucht.bewertungstag,
                      'datenart': anschluss_untersucht.datenart, 'max_ZD': anschluss_untersucht.max_ZD,
                      'max_ZB': anschluss_untersucht.max_ZB, 'max_ZS': anschluss_untersucht.max_ZS,
                      'geom': anschluss_untersucht.geom, 'epsg': QKan.config.epsg,
            }

            # logger.debug(f'm150porter.import - insertdata:\ntabnam: haltungen_untersucht\n'
            #              f'params: {params}')

            if not self.db_qkan.insertdata(
                    tabnam="anschlussleitungen_untersucht",
                    stmt_category='m150-import haltungen_untersucht',
                    mute_logger=False,
                    parameters=params,
            ):
                return

            params = {'name': anschluss_untersucht.haltnam,
                      'untersuchtag': anschluss_untersucht.untersuchtag,
                      'untersuchrichtung': anschluss_untersucht.untersuchrichtung,
                      'datei': anschluss_untersucht.film_dateiname, 'objekt': 'Anschlussleitung'}

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

    def _untersuchdat_anschluss(self) -> None:
        if self.m150_anschlussleitung is None:
            return

        def _iter() -> Iterator[Untersuchdat_anschlussleitung]:
            blocks = self.xml.findall(f"HG[HG313='{self.m150_anschlussleitung}']/HI/..")

            logger.debug(f"Anzahl Untersuchungsdaten Hausanschlussleitungen: {len(blocks)}")

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
            langtext = ""
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
            ZD = None
            ZB = None
            ZS = None

            for block in blocks:

                name = block.findtext("HG001", None)
                schoben = block.findtext("HG003", None)
                schunten = block.findtext("HG004", None)
                _val = block.findtext("HI/HI101", None)
                if _val == "I":
                    untersuchrichtung = "in Fließrichtung"
                elif _val == "G":
                    untersuchrichtung = "gegen Fließrichtung"
                else:
                    logger.info(f"Untersuchungsdaten Anschluss: Feld HI/HI101 fehlt oder falscher Wert: {_val}")
                    continue

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
                    langtext = _untersuchdat.findtext("HZ010", None)
                    charakt1 = _untersuchdat.findtext("HZ014", None)
                    charakt2 = _untersuchdat.findtext("HZ015", None)
                    quantnr1 = _get_float(_untersuchdat,"HZ003", 0.0)
                    quantnr2 = _get_float(_untersuchdat,"HZ004", 0.0)
                    _text = _untersuchdat.findtext("HZ005", None)
                    if _text:
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

                    _datei = _untersuchdat.findtext("HZ009", None)
                    if _datei and self.ordner_bild:
                        foto_dateiname = os.path.join(self.ordner_bild, _datei).replace("\\","/")
                    else:
                        foto_dateiname = None

                    ZD = _get_int(_untersuchdat,"HZ206", None)
                    ZB = _get_int(_untersuchdat, "HZ208", None)
                    ZS = _get_int(_untersuchdat,"HZ207", None)

                    yield Untersuchdat_anschlussleitung(
                        untersuchhal=name,                                      # Hinweis: Untersuchdat_anschlussleitung = Untersuchdat_haltung
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
                        langtext=langtext,
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

        untersuchdat_anschlussleitung = None
        for untersuchdat_anschlussleitung in _iter():

            params = {'untersuchleit': untersuchdat_anschlussleitung.untersuchhal,     # Hinweis: Untersuchdat_anschlussleitung = Untersuchdat_haltung
                      'untersuchrichtung': untersuchdat_anschlussleitung.untersuchrichtung,
                      'schoben': untersuchdat_anschlussleitung.schoben, 'schunten': untersuchdat_anschlussleitung.schunten,
                      'id': untersuchdat_anschlussleitung.id, 'untersuchtag': untersuchdat_anschlussleitung.untersuchtag,
                      'videozaehler': untersuchdat_anschlussleitung.videozaehler,
                      'inspektionslaenge': untersuchdat_anschlussleitung.inspektionslaenge,
                      'station': untersuchdat_anschlussleitung.station,
                      'timecode': untersuchdat_anschlussleitung.timecode, 'langtext': untersuchdat_anschlussleitung.langtext,
                      'kuerzel': untersuchdat_anschlussleitung.kuerzel,
                      'charakt1': untersuchdat_anschlussleitung.charakt1, 'charakt2': untersuchdat_anschlussleitung.charakt2,
                      'quantnr1': untersuchdat_anschlussleitung.quantnr1, 'quantnr2': untersuchdat_anschlussleitung.quantnr2,
                      'streckenschaden': untersuchdat_anschlussleitung.streckenschaden,
                      'streckenschaden_lfdnr': untersuchdat_anschlussleitung.streckenschaden_lfdnr,
                      'pos_von': untersuchdat_anschlussleitung.pos_von, 'pos_bis': untersuchdat_anschlussleitung.pos_bis,
                      'foto_dateiname': untersuchdat_anschlussleitung.foto_dateiname,
                      'film_dateiname': untersuchdat_anschlussleitung.film_dateiname,
                      'ordner_bild': untersuchdat_anschlussleitung.ordner_bild,
                      'ordner_video': untersuchdat_anschlussleitung.ordner_video,
                      'ZD': untersuchdat_anschlussleitung.ZD,
                      'ZB': untersuchdat_anschlussleitung.ZB, 'ZS': untersuchdat_anschlussleitung.ZS}

            if not self.db_qkan.insertdata(
                    tabnam="untersuchdat_anschlussleitung",
                    stmt_category='m150-import untersuchdat_anschlussleitung',
                    mute_logger=False,
                    parameters=params,
            ):
                return


        # Textpositionen für Schadenstexte berechnen

        self.db_qkan.commit()

        #Schadenstexte.setschadenstexte_anschlussleitungen()
        # self.db_qkan.setschadenstexte_anschlussleitungen()
        if untersuchdat_anschlussleitung is not None:
            Schadenstexte.setschadenstexte_anschlussleitungen(self.db_qkan)

    def _wehre(self) -> None:
        def _iter() -> Iterator[Wehr]:
            blocks = self.xml.findall("KG[KG306='ZVB']")
            logger.debug(f"Anzahl Wehre: {len(blocks)}")

            wnam=""
            schoben= ""
            schunten = ""

            for block in blocks:
                # wnam, knotentyp, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                wnam = block.findtext("KG001", None)

                baujahr = block.findtext("KG303", None)

                kommentar = block.findtext("KG999", None)

                laenge = 5.0

                #In QKan sind Wehre in der Tabelle haltungen gespeichert.
                _, geom, sohlhoehe, deckelhoehe = self._get_KG_GO(block, wnam, link=True)

                yield Wehr(
                    wnam=wnam,
                    schoben=wnam,
                    schunten=None,
                    sohle=sohlhoehe,
                    geom=geom,
                    laenge=laenge,
                    baujahr=baujahr,
                    simstatus=block.findtext("KG401", None),
                    entwart=block.findtext("KG302", None),
                    kommentar=kommentar,
                    schwellenhoehe = 0.0
                )

        for wehr in _iter():

            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                wehr.simstatus,
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
                wehr.entwart,
                self.mapper_entwart,
                'Anschlussleitungen',
                'entwaesserungsarten',
                'bezeichnung',
                'm150',
                'bemerkung',
                'kuerzel',
            )

            sql = f"""
                INSERT INTO haltungen
                                (wnam, schoben, schunten, haltungstyp,
                                 laenge, kommentar, baujahr, simstatus, entwart)
                SELECT '{wehr.wnam}', '{wehr.schoben}', '{wehr.schunten}', 'Wehr', {wehr.laenge}, {wehr.kommentar}, {wehr.baujahr},
                {simstatus},{entwart}
                FROM schaechte AS SCHOB, schaechte AS SCHUN
                WHERE SCHOB.schnam = '{wehr.schoben}' AND SCHUN.schnam = '{wehr.schunten}'
                """

            if not self.db_qkan.sql(sql, "xml_import Wehre [1]"):
                return None

        if not self.db_qkan.sql(
            "UPDATE haltungen SET geom = geom WHERE haltungstyp = 'Wehr'", 'xml_import Wehre [1a]'
        ):
            return None

        self.db_qkan.commit()

    def _pumpen(self) -> None:
        def _iter() -> Iterator[Pumpe]:
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

            for block in blocks:
                # pnam, knotentyp, xsch, ysch, sohlhoehe = self._consume_smp_block(block)

                pnam = block.findtext("KG001", None)

                baujahr = block.findtext("KG303", None)

                kommentar = block.findtext("KG999", None)

                laenge = 5.0

                # TODO: In QKan sind Pumpen in der Tabelle haltungen gespeichert.
                _, geom, sohlhoehe, deckelhoehe = self._get_KG_GO(block, pnam, link=True)

                # smp = block.find("GO/GP")
                #
                # if smp is None:
                #     fehlermeldung(
                #         "Fehler beim XML-Import: Pumpen",
                #         f'Keine Geometrie "SMP" für Pumpe {pnam}',
                #     )
                #     xsch, ysch, sohlhoehe = (0.0,) * 3
                # else:
                #     xsch = _get_float(smp, "GP003")
                #     if xsch is None:
                #         xsch = _get_float(smp, "GP005", 0.0)
                #
                #     ysch = _get_float(smp, "GP004")
                #     if ysch is None:
                #         ysch = _get_float(smp, "GP006", 0.0)
                #
                #     sohlhoehe = _get_float(smp, "GP007", 0.0)

                yield Pumpe(
                    pnam=pnam,
                    schoben=pnam,
                    schunten=None,
                    laenge=laenge,
                    baujahr=baujahr,
                    kommentar=kommentar,
                    simstatus=block.findtext("KG401", None),
                    entwart=block.findtext("KG302", None),
                    geom=geom,
                )


        for pumpe in _iter():

            # Simulationsstatus
            simstatus = self.db_qkan.get_from_mapper(
                pumpe.simstatus,
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
                pumpe.entwart,
                self.mapper_entwart,
                'Anschlussleitungen',
                'entwaesserungsarten',
                'bezeichnung',
                'm150',
                'bemerkung',
                'kuerzel',
            )


            params = {'haltnam': pumpe.pnam, 'schoben': pumpe.schoben, 'schunten': pumpe.schunten,
                      'haltungtyp': 'Pumpe', 'laenge': pumpe.laenge, 'baujahr': pumpe.baujahr,
                      'simstatus': pumpe.simstatus, 'kommentar': pumpe.kommentar, 'entwart': entwart,
                      'geom': pumpe.geom, 'epsg': QKan.config.epsg}
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
