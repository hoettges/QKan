"""Exportiert ausgewählte QKan-Netzobjekte in das XML-Format nach DWA-M 150.

Haltungen und Anschlussleitungen werden als HG-Datensätze, Schächte und
erforderliche Anschlusspunkte als KG-Datensätze ausgegeben. Die zugehörigen
Geometrien werden in GO- und GP-Datensätze übertragen.

Da sich das QKan-Datenmodell nicht in allen Fällen direkt auf die
M150-Felder abbilden lässt, sind an einigen Stellen zusätzliche
Umrechnungen und Ersatzregeln erforderlich. Dazu gehören insbesondere die
Ausrichtung von Leitungen, die Behandlung freier Anschlussenden sowie die
Ermittlung fehlender oder ungültiger Höhenangaben. Diese Regeln sind
QKan-spezifisch und werden an den betreffenden Stellen im Code erläutert.

Der Export liest die vorhandenen QKan-Daten ausschließlich aus und verändert
keine Objekte in den verwendeten Layern oder in der QKan-Datenbank.
"""

from __future__ import annotations

import logging
import os
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TYPE_CHECKING,
    Union,
)

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.PyQt.QtGui import QColor

from qgis.core import (
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsRectangle,
    QgsProject,
    QgsVectorLayer,
    QgsSpatialIndex,
    Qgis,
)

from qgis.gui import QgsMapTool, QgsRubberBand, QgsHighlight

from qkan.utils import QkanDbError

from .datenquelle import (
    Datenquelle,
    datenbank_oeffnen,
    datenquelle_waehlen,
    layer_finden,
)

from .m150_info import zeige_m150_info


LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from qgis.PyQt.QtCore import QPoint
    from qgis.PyQt.QtWidgets import QListWidgetItem
    from qgis.core import QgsFeature
    from qgis.gui import QgisInterface, QgsMapMouseEvent

    ExportZeile = Dict[str, Any]
    ExportObjekt = Union[QgsFeature, ExportZeile]


class _EinfachesXmlElement:
    """Kleines internes XML-Element für den M150-Export ohne XML-Parser.

    Die Kinderliste bewahrt die Einfügereihenfolge. Das ist fachlich relevant,
    weil DWA-M 150 die Feldreihenfolge entsprechend dem gewählten Format bzw.
    dessen XSD erwartet.
    """

    def __init__(
        self,
        tag: str,
        attrib: Optional[Mapping[str, object]] = None,
    ) -> None:
        """Initialisiert ein internes XML-Element.

        :param tag: Name des XML-Elements.
        :param attrib: Optionale XML-Attribute.
        """
        self.tag = str(tag)
        self.attrib = {
            str(name): wert
            for name, wert in (attrib or {}).items()
        }
        self.text: Optional[str] = None
        self._children: List["_EinfachesXmlElement"] = []
        self._indent_space = "  "

    def append(self, child: "_EinfachesXmlElement") -> None:
        """Hängt ein Kind an das XML-Element an.

        :param child: Hinzuzufügendes Kind-Element.
        """
        self._children.append(child)


def Element(
    tag: str,
    attrib: Optional[Mapping[str, object]] = None,
) -> _EinfachesXmlElement:
    """Erzeugt ein XML-Element für den M150-Export.

    :param tag: Name des XML-Elements.
    :param attrib: Optionale XML-Attribute.
    :return: Neu erzeugtes internes XML-Element.
    """
    return _EinfachesXmlElement(tag, attrib)


def SubElement(
    parent: _EinfachesXmlElement,
    tag: str,
    attrib: Optional[Mapping[str, object]] = None,
) -> _EinfachesXmlElement:
    """Erzeugt ein Kind-XML-Element für den M150-Export.

    :param parent: Übergeordnetes XML-Element.
    :param tag: Name des Kind-Elements.
    :param attrib: Optionale XML-Attribute.
    :return: Neu erzeugtes Kind-Element.
    """
    child = _EinfachesXmlElement(tag, attrib)
    parent.append(child)
    return child


def indent(xml_wurzel: _EinfachesXmlElement, space: str = "  ") -> None:
    """Legt die Einrückung für die XML-Serialisierung fest."""
    xml_wurzel._indent_space = space


def _xml_zeichen_ist_gueltig(zeichen: str) -> bool:
    """Prüft ein Zeichen gegen die erlaubten XML-1.0-Zeichenbereiche."""
    codepunkt = ord(zeichen)
    return (
        codepunkt in (0x09, 0x0A, 0x0D)
        or 0x20 <= codepunkt <= 0xD7FF
        or 0xE000 <= codepunkt <= 0xFFFD
        or 0x10000 <= codepunkt <= 0x10FFFF
    )


def _xml_text_bereinigen(wert: object) -> str:
    """Entfernt Zeichen, die in XML 1.0 nicht erlaubt sind."""
    if wert is None:
        return ""
    return "".join(
        zeichen
        for zeichen in str(wert)
        if _xml_zeichen_ist_gueltig(zeichen)
    )


def _xml_text_escapen(wert: object) -> str:
    """Bereinigt und maskiert einen XML-Textwert."""
    text = _xml_text_bereinigen(wert)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _xml_attribut_escapen(wert: object) -> str:
    """Bereinigt und maskiert einen Wert für ein doppelt zitiertes
    XML-Attribut.
    """
    return _xml_text_escapen(wert).replace('"', "&quot;")


def _xml_element_serialisieren(
    element: _EinfachesXmlElement,
    ebene: int = 0,
    space: str = "  ",
) -> str:
    """Serialisiert ein internes XML-Element rekursiv.

    :param element: Zu serialisierendes XML-Element.
    :param ebene: Aktuelle Einrückungsebene.
    :param space: Zeichenfolge für eine Einrückungsebene.
    :return: Serialisierter XML-Text.
    """
    einzug = space * ebene
    kinder = element._children
    text = _xml_text_escapen(element.text)
    attribute = "".join(
        f' {name}="{_xml_attribut_escapen(wert)}"'
        for name, wert in element.attrib.items()
    )

    if not kinder and text == "":
        return f"{einzug}<{element.tag}{attribute}/>"

    if not kinder:
        return (
            f"{einzug}<{element.tag}{attribute}>"
            f"{text}</{element.tag}>"
        )

    zeilen = [f"{einzug}<{element.tag}{attribute}>"]
    if text:
        zeilen.append(f"{space * (ebene + 1)}{text}")
    for child in kinder:
        zeilen.append(_xml_element_serialisieren(child, ebene + 1, space))
    zeilen.append(f"{einzug}</{element.tag}>")
    return "\n".join(zeilen)


def tostring(
    element: _EinfachesXmlElement,
    encoding: str = "unicode",
    xml_declaration: bool = False,
    standalone: Optional[bool] = None,
) -> Union[str, bytes]:
    """Serialisiert ein internes XML-Dokument.

    :param element: Wurzelelement des Dokuments.
    :param encoding: Zielkodierung oder ``unicode``.
    :param xml_declaration: Gibt an, ob eine XML-Deklaration geschrieben wird.
    :param standalone: Optionaler Standalone-Wert der XML-Deklaration.
    :return: XML als Text oder Bytefolge, abhängig von ``encoding``.
    """
    space = element._indent_space
    xml_text = _xml_element_serialisieren(element, 0, space)

    if xml_declaration:
        deklaration = f'<?xml version="1.0" encoding="{encoding}"'
        if standalone is not None:
            standalone_text = "yes" if standalone else "no"
            deklaration += f' standalone="{standalone_text}"'
        xml_text = deklaration + "?>\n" + xml_text

    if encoding == "unicode":
        return xml_text

    return xml_text.encode(encoding, errors="xmlcharrefreplace")


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "m150_export.ui")
)


class KartenauswahlWerkzeug(QgsMapTool):
    """Werkzeug zur kombinierten Karten- und Rechteckauswahl.

    Nutzung im QGIS-Kartenfenster.
    """

    finished = pyqtSignal()
    auswahl_geaendert = pyqtSignal()

    def __init__(
        self,
        iface: QgisInterface,
        exportdialog: "BefahrungExportDialog",
    ) -> None:
        """Richtet das Kartenwerkzeug für den Exportdialog ein."""
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.kartenfenster = iface.mapCanvas()
        self.exportdialog = exportdialog

        self.startpunkt: Optional[QgsPointXY] = None
        self.startposition: Optional[QPoint] = None
        self.zieht_auswahl = False
        self._spatial_index: Optional[QgsSpatialIndex] = None
        self._spatial_index_layer_id: Optional[str] = None

        self.auswahlrahmen = QgsRubberBand(
            self.kartenfenster, Qgis.GeometryType.Polygon
        )
        self.auswahlrahmen.setColor(Qt.red)
        self.auswahlrahmen.setWidth(1)

        self.setCursor(Qt.CrossCursor)

    def activate(self) -> None:
        """Aktiviert das Kartenwerkzeug.

        Setzt den Fokus auf die Kartenansicht.
        """
        super().activate()
        self.kartenfenster.setFocus()

    def deactivate(self) -> None:
        """Deaktiviert das Kartenwerkzeug.

        Entfernt die temporäre Rechteckdarstellung.
        """
        self.auswahlrahmen.reset(Qgis.GeometryType.Polygon)
        super().deactivate()

    def canvasPressEvent(self, maus_event: QgsMapMouseEvent) -> None:
        """Startet bei einem Linksklick die Punkt- oder Rechteckauswahl."""
        if maus_event.button() == Qt.RightButton:
            self._kartenauswahl_beenden()
            return

        if maus_event.button() != Qt.LeftButton:
            return

        self.startpunkt = self.toMapCoordinates(maus_event.pos())
        self.startposition = maus_event.pos()
        self.zieht_auswahl = False

    def canvasMoveEvent(self, maus_event: QgsMapMouseEvent) -> None:
        """Zeichnet das Auswahlrechteck während der Mausbewegung."""
        if not self.startpunkt:
            return

        if (maus_event.pos() - self.startposition).manhattanLength() < 4:
            return

        self.zieht_auswahl = True
        end = self.toMapCoordinates(maus_event.pos())
        suchrechteck = QgsRectangle(self.startpunkt, end)
        self._zeichne_auswahlrechteck(suchrechteck)

    def canvasReleaseEvent(self, maus_event: QgsMapMouseEvent) -> None:
        """Übernimmt die Objekte aus der abgeschlossenen Kartenauswahl."""
        if maus_event.button() != Qt.LeftButton or not self.startpunkt:
            return

        layer = self.exportdialog._layer_holen("haltungen")
        if layer is None:
            return

        modifiers = maus_event.modifiers()

        if self.zieht_auswahl:
            end = self.toMapCoordinates(maus_event.pos())
            suchrechteck = QgsRectangle(self.startpunkt, end)
            objekte = self._objektauswahl_rechteck(layer, suchrechteck)
        else:
            objekte = self._naechstes_objekt_finden(layer, maus_event.pos())

        objekt_ids = [objekt.id() for objekt in objekte]
        aktuelle_ids = set(layer.selectedFeatureIds())

        if modifiers & Qt.ControlModifier:
            neue_ids = aktuelle_ids.union(objekt_ids)
        elif modifiers & Qt.ShiftModifier:
            neue_ids = aktuelle_ids.difference(objekt_ids)
        else:
            neue_ids = aktuelle_ids.union(objekt_ids)

        layer.selectByIds(list(neue_ids))
        self.auswahl_geaendert.emit()

        self._auswahl_zueruecksetzen()

    def _kartenauswahl_beenden(self) -> None:
        """Beendet die Kartenauswahl und zeigt den Exportdialog wieder an."""
        self.kartenfenster.unsetMapTool(self)
        self.exportdialog._update()
        self.exportdialog.show()
        self.exportdialog.raise_()
        self.exportdialog.activateWindow()

    def _layer_id_lesen(self, layer: QgsVectorLayer) -> str:
        """Gibt die ID des Layers zurück."""
        return layer.id()

    def _erzeuge_spatial_index(
        self, layer: QgsVectorLayer
    ) -> QgsSpatialIndex:
        """Gibt den räumlichen Index des Layers zurück und erstellt ihn bei
        Bedarf neu.
        """
        layer_id = self._layer_id_lesen(layer)
        if (
            self._spatial_index is None
            or self._spatial_index_layer_id != layer_id
        ):
            self._spatial_index = QgsSpatialIndex(layer.getFeatures())
            self._spatial_index_layer_id = layer_id
        return self._spatial_index

    def _objektauswahl_rechteck(
        self,
        layer: QgsVectorLayer,
        suchrechteck: QgsRectangle,
    ) -> List[QgsFeature]:
        """Ermittelt die Features innerhalb des Auswahlrechtecks."""
        index = self._erzeuge_spatial_index(layer)
        objekt_ids = index.intersects(suchrechteck)
        if not objekt_ids:
            return []
        return list(
            layer.getFeatures(QgsFeatureRequest().setFilterFids(objekt_ids))
        )

    def _naechstes_objekt_finden(
        self, layer: QgsVectorLayer, pos: QPoint
    ) -> List[QgsFeature]:
        """Sucht das Feature mit dem geringsten Abstand zur Mausposition."""
        kartenpunkt = self.toMapCoordinates(pos)
        tol = self.kartenfenster.mapUnitsPerPixel() * 6

        suchrechteck = QgsRectangle(
            kartenpunkt.x() - tol,
            kartenpunkt.y() - tol,
            kartenpunkt.x() + tol,
            kartenpunkt.y() + tol,
        )

        naechstes_objekt = None
        kleinste_distanz = None
        punktgeom = QgsGeometry.fromPointXY(kartenpunkt)

        for objekt in self._objektauswahl_rechteck(layer, suchrechteck):
            geometrie = objekt.geometry()
            if not geometrie:
                continue

            abstand = geometrie.distance(punktgeom)

            if abstand is None or abstand < 0 or abstand > tol:
                continue

            if kleinste_distanz is None or abstand < kleinste_distanz:
                kleinste_distanz = abstand
                naechstes_objekt = objekt

        return [naechstes_objekt] if naechstes_objekt else []

    def _zeichne_auswahlrechteck(
        self, suchrechteck: QgsRectangle
    ) -> None:
        """Zeigt das aktuelle Auswahlrechteck im Kartenfenster an."""
        self.auswahlrahmen.reset(Qgis.GeometryType.Polygon)

        linienpunkte = [
            QgsPointXY(suchrechteck.xMinimum(), suchrechteck.yMinimum()),
            QgsPointXY(suchrechteck.xMaximum(), suchrechteck.yMinimum()),
            QgsPointXY(suchrechteck.xMaximum(), suchrechteck.yMaximum()),
            QgsPointXY(suchrechteck.xMinimum(), suchrechteck.yMaximum()),
            QgsPointXY(suchrechteck.xMinimum(), suchrechteck.yMinimum()),
        ]

        for p in linienpunkte:
            self.auswahlrahmen.addPoint(p, False)

        self.auswahlrahmen.show()

    def _auswahl_zueruecksetzen(self) -> None:
        """Setzt Startpunkt und Rechteckdarstellung der Auswahl zurück."""
        self.startpunkt = None
        self.startposition = None
        self.zieht_auswahl = False
        self.auswahlrahmen.reset(Qgis.GeometryType.Polygon)


class BefahrungExportDialog(QDialog, FORM_CLASS):
    """Dialog für den Export von QKan-Daten in eine DWA-M150-XML-Datei."""

    # Die Werte gelten in den Karteneinheiten des QKan-Projekts (üblicherweise
    # Meter). Sie steuern nur die geometrische QKan-Zuordnung und sind keine
    # Grenzwerte aus DWA-M 150.
    AUSWAHL_SUCHBEREICH_M = 100.0
    ANSCHLUSS_ENDPOINT_TOLERANZ_M = 0.05
    EXPORT_TABELLEN = {
        "haltungen",
        "schaechte",
        "anschlussleitungen",
        "anschlussschaechte",
    }

    # DWA-M 150, Abschnitt 7: Standard-Langtexte der Referenztabellen,
    # die von diesem Modul tatsächlich ausgewertet bzw. geschrieben werden.
    # Externe RT-Blöcke einer Import-XML haben beim Import Vorrang.
    M150_STANDARD_RT = {
        "101": {
            "D": "Digitalisiert",
            "G": "Geschätzt",
            "V": "Vermessen",
        },
        "102": {
            "B": "Berechnet",
            "G": "Geschätzt",
            "V": "Vermessen",
        },
        "103": {
            "F": "Offene Freispiegelleitung (Gerinne)",
            "D": "Druckrohrleitung",
            "G": "Dränageleitung",
            "K": "Geschlossene Freispiegelleitung",
        },
        "104": {
            "B": "Bach (Gewässer)",
            "M": "Mischwasser",
            "R": "Regenwasser",
            "S": "Schmutzwasser",
            "Z": "Sondernutzung",
        },
        "105": {
            "AZ": "Asbestzement",
            "B": "Beton",
            "BIT": "Bitumen",
            "BS": "Betonsegmente",
            "BSK": "Betonsegmente kunststoffmodifiziert",
            "BT": "Bitumen",
            "CN": "Edelstahl",
            "EIS": "Nichtidentifiziertes Metall (z. B. Eisen und Stahl)",
            "EPX": "Epoxydharz",
            "EPSF": "Epoxydharz mit Synthesefaser",
            "FZ": "Faserzement",
            "GFK": "Glasfaserverstärkter Kunststoff",
            "GG": "Grauguß",
            "GGG": "Duktiles Gußeisen",
            "KST": "Nichtidentifizierter Kunststoff",
            "MA": "Mauerwerk",
            "OB": "Ortbeton",
            "PC": "Polymerbeton",
            "PCC": "Polymermodifizierter Zementbeton",
            "PE": "Polyethylen",
            "PH": "Polyesterharz",
            "PHB": "Polyesterharzbeton",
            "PP": "Polypropylen",
            "PUR": "Polyurethanharz",
            "PVCM": "Polyvinylchlorid modifiziert",
            "PVCU": "Polyvinylchlorid hart",
            "SFB": "Stahlfaserbeton",
            "SPB": "Spannbeton",
            "SB": "Stahlbeton",
            "ST": "Stahl",
            "STZ": "Steinzeug",
            "SZB": "Spritzbeton",
            "SZBK": "Spritzbeton kunststoffmodifiziert",
            "TF": "Teerfaser",
            "UPGF": "Ungesättigtes Polyesterharz mit Glasfaser",
            "UPSF": "Ungesättigtes Polyesterharz mit Synthesefaser",
            "VEGF": "Vinylesterharz mit Synthesefaser",
            "VESF": "Vinylesterharz mit Glasfaser",
            "VBK": "Verbundrohr Beton-/Stahlbeton-Kunststoff",
            "VBS": "Verbundrohr Beton-/Stahlbeton-Steinzeug",
            "W": "Nichtidentifizierter Werkstoff",
            "WPE": "Wickelrohr (PEHD)",
            "WPVC": "Wickelrohr (PVCU)",
            "Z": "Sonstiger Werkstoff",
            "ZM": "Zementmörtel",
            "ZG": "Ziegelwerk",
        },
        "106": {
            "BO": (
                "Bogenförmig (kreisförmiger Scheitel und flache Sohle bei "
                "parallelen Wänden), Haubenquerschnitt"
            ),
            "DN": "Kreisförmig, Kreisquerschnitt",
            "EI": "Eiförmig, Eiquerschnitt",
            "GR": "Offener Graben",
            "MA": "Maulquerschnitt",
            "OV": (
                "Oval (kreisförmige Sohle und Scheitel bei parallelen Wänden)"
            ),
            "RE": "Rechteckig, Rechteckquerschnitt",
            "RI": "Rinnenquerschnitt",
            "U": "U-förmig",
            "Z": "Sonstige Profilart",
        },
        "107": {
            "A": "Beschichtung werkseitig",
            "B": "Auskleidung werkseitig",
            "C": "Schlauchliner",
            "D": "Close-Fit Liner",
            "E": "Liner mit Ringraumverfüllung",
            "F": "Teil-/Vollauskleidung vor Ort",
            "G": "Teil-/Vollbeschichtung vor Ort",
            "Z": "Sonstige Auskleidung",
        },
        "108": {
            "A": "Kanal",
            "B": "Anschlussleitung",
            "C": "Entlastungsleitung",
            "Z": "Sonstige",
        },
        "109": {
            "B": "In Betrieb",
            "N": "Nicht in Betrieb",
            "P": "Geplant",
            "V": "Verschlossen",
            "Z": "Sonstige",
        },
        "116": {
            "A": "Auslass",
            "B": "Bauwerk",
            "E": "Straßenablauf",
            "F": "Fiktiver Schacht",
            "G": "Gebäudeanschluss",
            "I": "Inspektionsöffnung",
            "L": "Lampenschacht",
            "R": "Reinigungsöffnung",
            "S": "Schacht",
            "W": "Sanitärgegenstand",
            "Z": "Sonstige",
        },
        "128": {
            "H": "Abwasserkanal",
            "K": "Knoten",
            "L": "Abwasserleitung",
        },
        "201": {
            "A": "Abnahme",
            "E": "Ersterfassung",
            "G": "Gewährleistung",
            "K": "Eigenkontrollverordnung",
            "N": "Nachuntersuchung",
            "S": "Nach Sanierung",
            "V": "Vor Sanierung",
            "Z": "Sonstige",
        },
        "202": {
            "ATVM143": "Merkblatt ATV-M 143-2",
            "DWAM149-2:2006": (
                "Merkblatt DWA-M 149-2 in Verbindung mit DIN EN 13508-2"
            ),
            "EN13508": "DIN EN 13508-2",
            "ISYBAU96": "ISYBAU 1996",
            "ISYBAU01": "ISYBAU 2001",
            "Z": "Sonstige",
        },
        "203": {
            "BG": "Begehung",
            "KTV": "Kamera-Inspektion",
            "SP": "Spiegelung/von der Oberfläche inspiziert",
            "Z": "Sonstige",
        },
        "204": {
            "FROST": "Frost",
            "REGEN": "Regen",
            "SCHNEE": "Schnee",
            "TROCKEN": "Trocken",
        },
        "205": {
            "J": "Wurde vor Inspektion gereinigt",
            "N": "Wurde vor Inspektion nicht gereinigt",
        },
        "206": {
            "J": "Untersuchung mit Vorflutsicherung wurde durchgeführt",
            "N": "Untersuchung ohne Vorflutsicherung",
        },
        "207": {
            "CD": "Compact Disk",
            "DVD": "DVD-Medium",
            "HD": "Wechselfestplatte (HardDrive)",
            "MOD": "Magnet-optisches Laufwerk (magneto optical disk)",
            "SVHS": "SVHS Videokassette",
            "ST": "USB Stick",
            "Z": "Sonstige",
        },
        "208": {
            "FOTO": "Foto als Filmabzug",
            "DIGFOTO": "Digitales Bild",
            "Z": "Sonstige",
        },
        "300": {
            "B": "Bauwerk",
            "D": "Deckel",
            "G": "Gerinne",
            "H": "Haltung",
        },
        "301": {
            "FL": "Fläche",
            "KR": "Kreis",
            "L": "Linie",
            "PKT": "Punkt",
            "POLY": "Polygon",
        },
        "302": {
            "GK": "Gauß-Krüger",
            "UTM": "Universal Transversal Mercator",
        },
        "303": {
            "MNN": "m.ü.NN",
            "NHN": "Normalhöhennull",
        },
    }

    def __init__(self, iface: QgisInterface) -> None:
        """Richtet den Exportdialog und seine Bedienelemente ein."""
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.setupUi(self)

        self._material_ref_m150: Dict[str, str] = {}
        self._material_codes_m150: Set[str] = set()
        self._profil_ref_m150: Dict[str, str] = {}
        self._profil_codes_m150: Set[str] = set()
        self._profilauskleidung_ref_m150: Dict[str, str] = {}
        self._knotenart_ref_m150: Dict[str, str] = {}
        self._entwart_ref_m150: Dict[str, str] = {}
        self._export_ref_warnungen: Set[Tuple[str, str, str]] = set()
        self.hervorhebung: Optional[QgsHighlight] = None
        self._datenquelle: Optional[Datenquelle] = None

        self.auswahlwerkzeug: Optional[KartenauswahlWerkzeug] = None

        self.ausgewaehlte_haltungen: Set[str] = set()
        self.ausgewaehlte_schaechte: Set[str] = set()
        self.ausgewaehlte_anschlussleitungen: Set[str] = set()

        self.kartenauswahl.clicked.connect(self._start_selektion)
        self.auswahl_zureuck.clicked.connect(self._auswahl_zuruecksetzen)

        self.pb_export.clicked.connect(self._waehle_speicherort)
        self.export_2.clicked.connect(self._export_xml)
        self.pb_info.clicked.connect(
            lambda: zeige_m150_info(self)
        )

        # Klicks in den drei Auswahllisten mit der Kartenhervorhebung verbinden
        self.haltungen.itemClicked.connect(self._haltung_hervorheben)
        self.schaechte.itemClicked.connect(self._schacht_hervorheben)
        self.hausanschluesse.itemClicked.connect(
            self._anschlussleitung_hervorheben
        )

    def _datenquelle_waehlen(
        self,
        erforderliche_tabellen: Iterable[str],
    ) -> bool:
        """Wählt eine gemeinsame SpatiaLite- oder PostgreSQL-Quelle."""
        tabellen = tuple(dict.fromkeys(erforderliche_tabellen))
        if (
            self._datenquelle is not None
            and all(
                layer_finden(
                    QgsProject.instance(), tabelle, self._datenquelle
                ) is not None
                for tabelle in tabellen
            )
        ):
            return True

        self._datenquelle = datenquelle_waehlen(
            QgsProject.instance(),
            tabellen,
            self,
            "M150-Export – QKan-Datenquelle",
        )
        if self._datenquelle is not None:
            return True

        meldung = (
            "Es wurde keine vollständige QKan-Datenquelle mit den benötigten "
            "Layern gefunden oder die Auswahl wurde abgebrochen. Unterstützt "
            "werden SpatiaLite und PostgreSQL/PostGIS; alle Layer müssen aus "
            "derselben Datenquelle stammen."
        )
        QMessageBox.warning(self, "M150-Export", meldung)
        return False

    def _layer_holen(self, tabellenname: str) -> Optional[QgsVectorLayer]:
        """Liefert nur den Layer aus der gewählten QKan-Datenquelle."""
        if self._datenquelle is None:
            return None
        return layer_finden(
            QgsProject.instance(),
            tabellenname,
            self._datenquelle,
        )

    # Hervorhebung im Kartenfenster

    def _highlight_zuruecksetzen(self) -> None:
        """Entfernt ein bestehendes Karten-Highlight."""
        if self.hervorhebung:
            self.hervorhebung.hide()
            self.hervorhebung = None

    def _kartenauswahl_hervorheben(
        self, objekt: QgsFeature, layer: QgsVectorLayer
    ) -> None:
        """Hebt ein Feature im Kartenfenster hervor."""
        geometrie = objekt.geometry()

        self._highlight_zuruecksetzen()

        self.hervorhebung = QgsHighlight(
            self.iface.mapCanvas(), geometrie, layer
        )
        self.hervorhebung.setColor(QColor(255, 0, 0))
        self.hervorhebung.setWidth(4)
        self.hervorhebung.show()

    def _haltung_hervorheben(self, listeneintrag: QListWidgetItem) -> None:
        """Hebt die in der Liste ausgewählte Haltung hervor."""
        name = listeneintrag.text()
        layer = self._layer_holen("haltungen")
        if layer is None:
            return

        for objekt in layer.getFeatures():
            if str(objekt["haltnam"]) == name:
                self._kartenauswahl_hervorheben(objekt, layer)
                break

    def _schacht_hervorheben(self, listeneintrag: QListWidgetItem) -> None:
        """Hebt den in der Liste ausgewählten Schacht hervor."""
        name = listeneintrag.text()
        layer = self._layer_holen("schaechte")
        if layer is None:
            return

        for objekt in layer.getFeatures():
            if str(objekt["schnam"]) == name:
                self._kartenauswahl_hervorheben(objekt, layer)
                break

    def _anschlussleitung_hervorheben(
        self, listeneintrag: QListWidgetItem
    ) -> None:
        """Hebt die in der Liste ausgewählte Anschlussleitung hervor."""
        name = listeneintrag.text()
        layer = self._layer_holen("anschlussleitungen")
        if layer is None:
            return

        for objekt in layer.getFeatures():
            if str(objekt["leitnam"]) == name:
                self._kartenauswahl_hervorheben(objekt, layer)
                break

    def _start_selektion(self) -> None:
        """Startet die interaktive Selektion auf dem Haltungen-Layer."""
        if not self._datenquelle_waehlen(("haltungen",)):
            return

        layer = self._layer_holen("haltungen")
        if layer is None:
            QMessageBox.warning(
                self,
                "M150-Export",
                "Der QKan-Layer 'Haltungen' aus der Tabelle 'haltungen' "
                "ist in der gewählten Datenquelle nicht eindeutig geladen.",
            )
            return
        self.iface.setActiveLayer(layer)

        self.auswahlwerkzeug = KartenauswahlWerkzeug(self.iface, self)
        self.auswahlwerkzeug.auswahl_geaendert.connect(self._update)

        self.iface.mapCanvas().setMapTool(self.auswahlwerkzeug)

        self.hide()

    def _objekt_suchbereich_erstellen(
        self,
        objekte: Iterable[QgsFeature],
        radius: Optional[float] = None,
    ) -> Optional[QgsRectangle]:
        """Bildet einen erweiterten Suchbereich um die ausgewählten Features.
        """
        if radius is None:
            radius = self.AUSWAHL_SUCHBEREICH_M

        suchbereich = None
        for objekt in objekte:
            geometrie = objekt.geometry()
            if not geometrie:
                continue
            suchrechteck = geometrie.boundingBox()
            suchrechteck.grow(radius)
            if suchbereich is None:
                suchbereich = QgsRectangle(suchrechteck)
            else:
                suchbereich.combineExtentWith(suchrechteck)
        return suchbereich

    def _objekte_in_suchbereich_liefern(
        self,
        layer: Optional[QgsVectorLayer],
        suchbereich: Optional[QgsRectangle],
    ) -> Iterable[QgsFeature]:
        """Liefert die Features innerhalb des Suchbereichs oder alle Features
        des Layers.
        """
        if layer is None:
            return []
        if suchbereich is None:
            return layer.getFeatures()
        return layer.getFeatures(
            QgsFeatureRequest().setFilterRect(suchbereich)
        )

    def _update(self) -> None:
        """Aktualisiert die interne Auswahl.

        Betrifft Haltungen, Schächte und Anschlussleitungen.
        """
        layer = self._layer_holen("haltungen")
        if layer is None:
            return
        objekte = layer.selectedFeatures()

        self.ausgewaehlte_haltungen = {
            str(objekt["haltnam"]) for objekt in objekte if objekt["haltnam"]
        }
        if not self.ausgewaehlte_haltungen:
            self._auswahl_zuruecksetzen()
            return

        ausgewaehlte_haltungsobjekte = {
            str(objekt["haltnam"]): objekt
            for objekt in objekte
            if objekt["haltnam"]
        }
        suchbereich = self._objekt_suchbereich_erstellen(objekte)

        self.ausgewaehlte_schaechte = set()
        self.ausgewaehlte_anschlussleitungen = set()

        schacht_ids = set()
        anschluss_ids = []

        schacht_layer = self._layer_holen("schaechte")

        for objekt in objekte:
            if objekt["haltnam"] in self.ausgewaehlte_haltungen:
                if objekt["schoben"]:
                    self.ausgewaehlte_schaechte.add(str(objekt["schoben"]))
                if objekt["schunten"]:
                    self.ausgewaehlte_schaechte.add(str(objekt["schunten"]))

        if self.cb_export_anschlussleitungen.isChecked():
            anschluss_layer = self._layer_holen("anschlussleitungen")

            if anschluss_layer is not None:

                for al_objekt in self._objekte_in_suchbereich_liefern(
                    anschluss_layer, suchbereich
                ):
                    verbundene_haltung = self._finde_haltung_von_anschluss(
                        al_objekt,
                        layer,
                        ausgewaehlte_haltungen=self.ausgewaehlte_haltungen,
                        haltungskandidaten=ausgewaehlte_haltungsobjekte,
                    )
                    if verbundene_haltung is None:
                        continue

                    leitnam = (
                        str(al_objekt["leitnam"])
                        if al_objekt["leitnam"]
                        else ""
                    )
                    if leitnam:
                        self.ausgewaehlte_anschlussleitungen.add(leitnam)
                        anschluss_ids.append(al_objekt.id())

                    anschlussgeom = al_objekt.geometry()
                    if not anschlussgeom:
                        continue

                    linienpunkte = self._lade_linienpunkte(anschlussgeom)
                    if len(linienpunkte) < 2:
                        continue

                    haltungsgeom = verbundene_haltung.geometry()
                    (
                        ausgerichtete_linienpunkte,
                        _projected,
                        freies_ende,
                        _attached_at_start,
                    ) = self._orient_anschlussleitung_zu_haltung(
                        linienpunkte,
                        haltungsgeom,
                    )
                    if not ausgerichtete_linienpunkte or freies_ende is None:
                        continue

                    schacht_feat = self._finde_schacht_nach_punkt(
                        freies_ende, schacht_layer
                    )
                    if schacht_feat is not None and schacht_feat["schnam"]:
                        self.ausgewaehlte_schaechte.add(
                            str(schacht_feat["schnam"])
                        )
                        schacht_ids.add(schacht_feat.id())

        for objekt in self._objekte_in_suchbereich_liefern(
            schacht_layer, suchbereich
        ):
            if objekt["schnam"] in self.ausgewaehlte_schaechte:
                schacht_ids.add(objekt.id())

        if schacht_layer is not None:
            schacht_layer.selectByIds(list(schacht_ids))

        anschluss_layer = self._layer_holen("anschlussleitungen")
        if anschluss_layer is not None:
            anschluss_layer.selectByIds(anschluss_ids)

        self.haltungen.clear()
        self.haltungen.addItems(sorted(self.ausgewaehlte_haltungen))

        self.schaechte.clear()
        self.schaechte.addItems(sorted(self.ausgewaehlte_schaechte))

        self.hausanschluesse.clear()
        self.hausanschluesse.addItems(
            sorted(self.ausgewaehlte_anschlussleitungen)
        )

    def _auswahl_zuruecksetzen(self) -> None:
        """Setzt Auswahl, Highlight und UI-Listen zurück."""
        for tabellenname in self.EXPORT_TABELLEN:
            layer = self._layer_holen(tabellenname)
            if layer is not None:
                layer.removeSelection()

        self._highlight_zuruecksetzen()

        self.ausgewaehlte_haltungen.clear()
        self.ausgewaehlte_schaechte.clear()
        self.ausgewaehlte_anschlussleitungen.clear()

        self.haltungen.clear()
        self.schaechte.clear()
        self.hausanschluesse.clear()

    def _objekt_wert(self, objekt: ExportObjekt, feld: str) -> Any:
        """Liest einen Attributwert aus QgsFeature oder YAML-Zeile."""
        if isinstance(objekt, dict):
            return objekt.get(feld)
        try:
            return objekt[feld]
        except (KeyError, TypeError):
            return None

    def _objekt_geometrie(
        self, objekt: ExportObjekt
    ) -> Optional[QgsGeometry]:
        """Liest die Geometrie aus QgsFeature oder YAML-Zeile."""
        if isinstance(objekt, dict):
            return objekt.get("__geometry")
        geometrie = getattr(objekt, "geometry", None)
        return geometrie() if callable(geometrie) else None

    def _objekte_iterieren(
        self,
        quelle: object,
        request: Optional[QgsFeatureRequest] = None,
    ) -> Iterable[ExportObjekt]:
        """Iteriert ein QGIS-Layer, Wörterbuch oder eine YAML-Zeilenliste."""
        if quelle is None:
            return []
        if isinstance(quelle, dict):
            return quelle.values()
        get_features = getattr(quelle, "getFeatures", None)
        if callable(get_features):
            return (
                get_features(request)
                if request is not None
                else get_features()
            )
        return quelle

    def _geometrie_aus_wkb(self, wert: object) -> Optional[QgsGeometry]:
        """Erzeugt eine QGIS-Geometrie aus dem gelesenen WKB-Wert."""
        if wert is None:
            return None

        try:
            wkb = bytes(wert)
        except (TypeError, ValueError):
            return None

        if not wkb:
            return None

        geometrie = QgsGeometry()
        try:
            geometrie.fromWkb(wkb)
        except (TypeError, ValueError):
            return None
        if geometrie.isEmpty():
            return None
        return geometrie

    def _sql_zeilen_laden(
        self,
        db_qkan: object,
        sqlnam: str,
        parameter: Union[Mapping[str, object], Sequence[object]] = (),
        ersetzungsfunktion: Optional[Callable[[str], str]] = None,
    ) -> List[ExportZeile]:
        """Lädt eine benannte YAML-Abfrage als Wörterbuchzeilen.

        :param db_qkan: Geöffnete QKan-Datenbankverbindung.
        :param sqlnam: Name der datenbankspezifischen YAML-Abfrage.
        :param parameter: Gebundene SQL-Parameter.
        :param ersetzungsfunktion: Optionale Funktion zur Anpassung des
            SQL-Texts.
        :return: Ergebniszeilen als Wörterbücher.
        :raises RuntimeError: Wenn die YAML-Abfrage nicht ausgeführt werden
            kann.
        """
        if not db_qkan.sqlyml(
            sqlnam,
            stmt_category=f"Inspektion: {sqlnam}",
            parameters=parameter,
            replacefun=ersetzungsfunktion,
        ):
            raise RuntimeError(
                f"Die YAML-Abfrage '{sqlnam}' konnte nicht ausgeführt werden."
            )

        beschreibung = db_qkan.cursl.description or ()
        spalten = [eintrag[0] for eintrag in beschreibung]
        ergebnis: List[ExportZeile] = []

        for daten in db_qkan.fetchall():
            zeile = dict(zip(spalten, daten))
            if "__geom_wkb" in zeile:
                zeile["__geometry"] = self._geometrie_aus_wkb(
                    zeile.pop("__geom_wkb")
                )
            ergebnis.append(zeile)

        return ergebnis

    def _sql_auswahl_zeilen_laden(
        self,
        db_qkan: object,
        sqlnam: str,
        auswahlwerte: Iterable[object],
    ) -> List[ExportZeile]:
        """Lädt ausschließlich ausgewählte Objekte über gebundene Werte.

        :param db_qkan: Geöffnete QKan-Datenbankverbindung.
        :param sqlnam: Name der datenbankspezifischen Auswahlabfrage.
        :param auswahlwerte: Zu ladende Objektkennungen.
        :return: Sortierte Ergebniszeilen der ausgewählten Objekte.
        """
        werte = sorted(
            {
                str(wert).strip()
                for wert in auswahlwerte
                if wert is not None and str(wert).strip()
            }
        )
        if not werte:
            return []

        ergebnis: List[ExportZeile] = []
        # Auswahlwerte in Blöcken zu höchstens 900 Parametern abfragen;
        # vollständige Tabellen werden dabei nicht geladen.
        for start in range(0, len(werte), 900):
            teilwerte = werte[start:start + 900]
            parameter = {
                f"auswahl_{index}": wert
                for index, wert in enumerate(teilwerte)
            }
            platzhalter = ", ".join(
                f":auswahl_{index}" for index in range(len(teilwerte))
            )

            def auswahl_einsetzen(sqltext: str) -> str:
                """Setzt vorbereitete Auswahlplatzhalter in eine Abfrage ein.

                :param sqltext: SQL-Text mit dem Platzhalter ``{auswahl}``.
                :return: SQL-Text mit benannten Parametern.
                """
                return sqltext.replace("{auswahl}", platzhalter)

            ergebnis.extend(
                self._sql_zeilen_laden(
                    db_qkan,
                    sqlnam,
                    parameter=parameter,
                    ersetzungsfunktion=auswahl_einsetzen,
                )
            )

        ergebnis.sort(
            key=lambda zeile: (
                zeile.get("pk") is None,
                zeile.get("pk") if zeile.get("pk") is not None else 0,
            )
        )
        return ergebnis

    def _ungespeicherte_exportaenderungen(self) -> List[str]:
        """Liefert exportrelevante Layer mit offenen Änderungen."""
        geaendert: List[str] = []

        for tabellenname in self.EXPORT_TABELLEN:
            layer = self._layer_holen(tabellenname)
            if layer is not None and layer.isModified():
                geaendert.append(layer.name())

        return geaendert

    def _normalisiere_refwert(self, wert: object) -> str:
        """Normalisiert einen Referenzwert für YAML-Zuordnungen."""
        return "".join(
            zeichen
            for zeichen in str(wert or "").upper()
            if zeichen.isalnum()
        )

    def _standard_rt_code_fuer_wert(
        self, referenztabelle: str, wert: object
    ) -> str:
        """Löst Code oder DWA-Standardlangtext auf den RT-Schlüssel zurück."""
        text = str(wert or "").strip()
        if not text or text.upper() == "NULL":
            return ""

        rt = self.M150_STANDARD_RT.get(str(referenztabelle).zfill(3), {})
        code_direkt = text.upper()
        if code_direkt in rt:
            return code_direkt

        vergleichswert = self._normalisiere_refwert(text)
        for code, langtext in rt.items():
            if self._normalisiere_refwert(langtext) == vergleichswert:
                return code
        return ""

    def _unbekannten_refwert_exportieren(
        self, feld: str, referenztabelle: str, wert: object
    ) -> str:
        """Gibt einen unbekannten Text unverändert aus und protokolliert ihn."""
        text = str(wert or "").strip()
        if not text or text.upper() == "NULL":
            return ""

        warnung = (feld, str(referenztabelle).zfill(3), text)
        if warnung not in self._export_ref_warnungen:
            self._export_ref_warnungen.add(warnung)
            LOGGER.warning(
                "M150-Export: %s='%s' ist in RT %s nicht zugeordnet; "
                "Rohtext wird unverändert exportiert.",
                feld,
                text,
                str(referenztabelle).zfill(3),
            )
        return text

    def _referenzen_laden(self, db_qkan: object) -> None:
        """Lädt alle Exportzuordnungen aus den Datenbankabfragen.

        DWA-M 150 transportiert zahlreiche Werte als Schlüssel aus
        Referenztabellen. Die YAML-Abfragen bündeln die Standardcodes,
        QKan-Tabellenwerte und Schreibvarianten; Python arbeitet anschließend
        nur noch mit den daraus aufgebauten Indizes.
        """
        self._material_ref_m150 = {}
        self._material_codes_m150 = set()
        for zeile in self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_material_m150"
        ):
            vergleichswert = self._normalisiere_refwert(
                zeile.get("vergleichswert")
            )
            code = str(zeile.get("m150_code") or "").strip().upper()
            if not code:
                continue
            self._material_codes_m150.add(code)
            if vergleichswert:
                # Bei Aliasen mit gleichem Vergleichswert bleibt die erste,
                # durch die YAML-Sortierung festgelegte Zuordnung maßgeblich.
                self._material_ref_m150.setdefault(vergleichswert, code)

        self._profil_ref_m150 = {}
        self._profil_codes_m150 = set()
        for zeile in self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_profile_m150"
        ):
            vergleichswert = self._normalisiere_refwert(
                zeile.get("profilnam")
            )
            code = str(zeile.get("m150_code") or "").strip().upper()
            if not code:
                continue
            self._profil_codes_m150.add(code)
            if vergleichswert:
                self._profil_ref_m150.setdefault(vergleichswert, code)

        self._profilauskleidung_ref_m150 = {}
        for zeile in self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_profilauskleidung_m150"
        ):
            code = str(zeile.get("m150_code") or "").strip().upper()
            if not code:
                continue
            self._profilauskleidung_ref_m150.setdefault(code, code)
            vergleichswert = self._normalisiere_refwert(
                zeile.get("bezeichnung")
            )
            if vergleichswert:
                self._profilauskleidung_ref_m150.setdefault(
                    vergleichswert, code
                )

        self._knotenart_ref_m150 = {}
        for zeile in self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_knotenart_m150"
        ):
            code = str(zeile.get("m150_code") or "").strip().upper()
            if not code:
                continue
            self._knotenart_ref_m150.setdefault(code, code)
            vergleichswert = self._normalisiere_refwert(
                zeile.get("vergleichswert")
            )
            if vergleichswert:
                self._knotenart_ref_m150.setdefault(vergleichswert, code)

        self._entwart_ref_m150 = {}
        for zeile in self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_entwaesserungsarten_m150"
        ):
            vergleichswert = self._normalisiere_refwert(
                zeile.get("vergleichswert")
            )
            code = str(zeile.get("m150_code") or "").strip().upper()
            if vergleichswert and code in {"M", "R", "S"}:
                self._entwart_ref_m150[vergleichswert] = code

    def _wert_in_zahl_oder_none(self, wert: object) -> Optional[float]:
        """Konvertiert einen Wert in eine Fließkommazahl, sofern das möglich
        ist.
        """
        if wert is None:
            return None
        try:
            return float(wert)
        except (TypeError, ValueError):
            return None

    def _formatiere_zahlen_export(
        self,
        wert: object,
        standardwert: str = "",
        nachkommastellen: int = 3,
    ) -> str:
        """Formatiert einen Zahlenwert für den XML-Export.

        :param wert: Zu formatierender Wert.
        :param standardwert: Text für nicht numerische Werte.
        :param nachkommastellen: Anzahl der auszugebenden Nachkommastellen.
        :return: Formatierter Zahlenwert.
        """
        number = self._wert_in_zahl_oder_none(wert)
        return (
            f"{number:.{nachkommastellen}f}"
            if number is not None
            else standardwert
        )

    def _formatiere_zahl_oder_leer(
        self, wert: object, nachkommastellen: int = 3
    ) -> str:
        """Formatiert einen Zahlenwert oder gibt bei ungültigen Werten einen
        Leerstring zurück.
        """
        number = self._wert_in_zahl_oder_none(wert)
        return f"{number:.{nachkommastellen}f}" if number is not None else ""

    def _entwart_map_in_m150(self, wert: object) -> str:
        """Mappt Kanalnutzung: QKan/YAML, DWA-Standard, sonst Rohtext."""
        vergleichswert = self._normalisiere_refwert(wert)
        code = self._entwart_ref_m150.get(vergleichswert, "")
        if code:
            return code
        code = self._standard_rt_code_fuer_wert("104", wert)
        if code:
            return code
        return self._unbekannten_refwert_exportieren(
            "HG302/KG302", "104", wert
        )

    def _kanalart_aus_abflussart_map_m150(self, wert: object) -> str:
        """Wandelt die QKan-Abflussart in die M150-Kanalart um.

        Bereits gespeicherte M150-Schlüssel werden unverändert übernommen.
        Die QKan-Bezeichnungen ``Freispiegel`` und ``Druckleitung`` werden
        auf die fachlich entsprechenden Schlüssel der Referenztabelle 103
        abgebildet. Unbekannte Werte werden nicht geraten.
        """
        text = str(wert or "").strip()
        if not text or text.upper() == "NULL":
            return ""

        code = text.upper()
        if code in {"F", "D", "G", "K"}:
            return code

        vergleichswert = self._normalisiere_refwert(text)
        zuordnung = {
            "FREISPIEGEL": "K",
            "GESCHLOSSENEFREISPIEGELLEITUNG": "K",
            "DRUCKLEITUNG": "D",
            "DRUCKROHRLEITUNG": "D",
            "OFFENEFREISPIEGELLEITUNG": "F",
            "OFFENEFREISPIEGELLEITUNGGERINNE": "F",
            "GERINNE": "F",
            "DRÄNAGELEITUNG": "G",
            "DRAENAGELEITUNG": "G",
            "DRAINAGELEITUNG": "G",
        }
        code = zuordnung.get(vergleichswert, "")
        if code:
            return code
        code = self._standard_rt_code_fuer_wert("103", wert)
        if code:
            return code
        return self._unbekannten_refwert_exportieren("HG301", "103", wert)

    def _material_map_m150(self, wert: object) -> str:
        """Wandelt QKan-Materialwerte über YAML in M150-Codes um."""
        text = str(wert or "").strip()
        if not text or text.upper() == "NULL":
            return ""

        upper = text.upper()
        # Bereits als M150-Code gespeicherte Werte werden unverändert
        # durchgereicht; auch ein vorangestellter Code wie "STZ Steinzeug"
        # bleibt kompatibel zu bestehenden QKan-Projekten.
        if upper in self._material_codes_m150:
            return upper

        erster_teil = upper.split()[0]
        if erster_teil in self._material_codes_m150:
            return erster_teil

        code = self._material_ref_m150.get(
            self._normalisiere_refwert(text), ""
        )
        if code:
            return code
        code = self._standard_rt_code_fuer_wert("105", text)
        if code:
            return code
        return self._unbekannten_refwert_exportieren(
            "HG304/HG309", "105", text
        )

    def _profil_map_m150(self, wert: object) -> str:
        """Wandelt QKan-Profilwerte über YAML in M150-Codes um."""
        text = str(wert or "").strip()
        if not text or text.upper() == "NULL":
            return ""

        upper = text.upper()
        if upper in self._profil_codes_m150:
            return upper
        code = self._profil_ref_m150.get(
            self._normalisiere_refwert(text), ""
        )
        if code:
            return code
        code = self._standard_rt_code_fuer_wert("106", text)
        if code:
            return code
        return self._unbekannten_refwert_exportieren("HG305", "106", text)

    def _profilauskleidung_map_m150(self, wert: object) -> str:
        """Mappt Profilauskleidung: YAML, DWA-Standard, sonst Rohtext."""
        code = self._profilauskleidung_ref_m150.get(
            self._normalisiere_refwert(wert), ""
        )
        if code:
            return code
        code = self._standard_rt_code_fuer_wert("107", wert)
        if code:
            return code
        return self._unbekannten_refwert_exportieren("HG308", "107", wert)

    def _knotenart_map_m150(self, wert: object) -> str:
        """Wandelt Knotenarten über YAML in M150-Codes um."""
        return self._knotenart_ref_m150.get(
            self._normalisiere_refwert(wert), ""
        )

    def _lade_linienpunkte(
        self, geometrie: QgsGeometry
    ) -> List[QgsPointXY]:
        """Liest die Punktfolge aus einer ein- oder mehrteiligen
        Liniengeometrie.
        """
        linienpunkte = geometrie.asPolyline()
        if not linienpunkte:
            parts = geometrie.asMultiPolyline()
            if parts and parts[0]:
                linienpunkte = parts[0]
        return linienpunkte or []

    def _finde_schacht_nach_punkt(
        self,
        punkt: Optional[QgsPointXY],
        quelle: object,
        toleranz: float = 0.25,
    ) -> Optional[ExportObjekt]:
        """Sucht den nächsten Schacht an einem Punkt.

        :param punkt: Zu prüfender Kartenpunkt.
        :param quelle: QGIS-Layer oder geladene Exportzeilen.
        :param toleranz: Maximaler Abstand in Karteneinheiten.
        :return: Nächstes passendes Objekt oder ``None``.
        """
        if punkt is None or quelle is None:
            return None

        punkt_geom = QgsGeometry.fromPointXY(QgsPointXY(punkt))
        request = None
        if callable(getattr(quelle, "getFeatures", None)):
            request = QgsFeatureRequest().setFilterRect(
                QgsRectangle(
                    punkt.x() - toleranz,
                    punkt.y() - toleranz,
                    punkt.x() + toleranz,
                    punkt.y() + toleranz,
                )
            )

        bestes_objekt = None
        kleinste_distanz = None
        for objekt in self._objekte_iterieren(quelle, request):
            geometrie = self._objekt_geometrie(objekt)
            if geometrie is None or geometrie.isEmpty():
                continue
            abstand = geometrie.distance(punkt_geom)
            if abstand <= toleranz and (
                kleinste_distanz is None or abstand < kleinste_distanz
            ):
                kleinste_distanz = abstand
                bestes_objekt = objekt
        return bestes_objekt

    def _anschluss_endpunkte_lesen(
        self, al_objekt: ExportZeile
    ) -> List[QgsPointXY]:
        """Liest Endpunkte einer per YAML geladenen Anschlussleitung."""
        geometrie = al_objekt.get("__geometry")
        if geometrie is None or geometrie.isEmpty():
            return []
        linienpunkte = self._lade_linienpunkte(geometrie)
        if len(linienpunkte) < 2:
            return []
        return [linienpunkte[0], linienpunkte[-1]]

    def _anschluss_beruehrt_haltung(
        self,
        al_objekt: ExportZeile,
        haltungsgeom: QgsGeometry,
        toleranz: float = 0.05,
    ) -> bool:
        """Prüft einen Leitungsendpunkt gegen eine Haltungsgeometrie."""
        if haltungsgeom is None:
            return False
        for punkt in self._anschluss_endpunkte_lesen(al_objekt):
            punkt_geom = QgsGeometry.fromPointXY(QgsPointXY(punkt))
            if haltungsgeom.distance(punkt_geom) <= toleranz:
                return True
        return False

    def _anschlussleitungen_am_punkt_finden(
        self,
        aktuelles_objekt: ExportZeile,
        punkt: QgsPointXY,
        a_objekte: List[ExportZeile],
        toleranz: float = 0.05,
    ) -> List[ExportZeile]:
        """Sucht weitere Anschlussleitungen an einem Punkt.

        :param aktuelles_objekt: Ausgangsleitung, die ausgeschlossen wird.
        :param punkt: Gemeinsamer Endpunkt.
        :param a_objekte: Geladene Anschlussleitungen.
        :param toleranz: Maximaler Abstand in Karteneinheiten.
        :return: Nach Abstand sortierte Anschlussleitungen.
        """
        if punkt is None:
            return []

        aktuelle_id = aktuelles_objekt.get("pk")
        punkt_geom = QgsGeometry.fromPointXY(QgsPointXY(punkt))
        treffer: List[Tuple[float, ExportZeile]] = []

        for objekt in a_objekte:
            if aktuelle_id is not None and objekt.get("pk") == aktuelle_id:
                continue
            if not objekt.get("leitnam"):
                continue

            geometrie = objekt.get("__geometry")
            if geometrie is None or geometrie.isEmpty():
                continue

            abstand = geometrie.distance(punkt_geom)
            if abstand <= toleranz:
                treffer.append((abstand, objekt))

        treffer.sort(key=lambda eintrag: eintrag[0])
        return [objekt for _abstand, objekt in treffer]

    def _anschluss_hat_pfad_zur_haltung(
        self,
        al_objekt: ExportZeile,
        a_objekte: List[ExportZeile],
        haltungsgeom: QgsGeometry,
        toleranz: float = 0.05,
        besuchte_ids: Optional[Set[int]] = None,
    ) -> bool:
        """Prüft rekursiv einen Anschlussleitungspfad bis zur Haltung.

        Der Pfad wird benötigt, um bei verzweigten Anschlussnetzen das
        M150-Feld HG012 (``Kind von``) zu bestimmen. ``besuchte_ids``
        verhindert Endlosschleifen in ringförmigen oder fehlerhaft
        verbundenen Netzen.

        :param al_objekt: Aktuell geprüfte Anschlussleitung.
        :param a_objekte: Alle geladenen Anschlussleitungen.
        :param haltungsgeom: Geometrie der Zielhaltung.
        :param toleranz: Toleranz für geometrische Berührungen.
        :param besuchte_ids: Bereits geprüfte Objektkennungen.
        :return: ``True``, wenn ein Pfad zur Haltung besteht.
        """
        if al_objekt is None:
            return False

        if besuchte_ids is None:
            besuchte_ids = set()

        objekt_id = al_objekt.get("pk")
        if objekt_id is not None:
            if objekt_id in besuchte_ids:
                return False
            besuchte_ids.add(objekt_id)

        if self._anschluss_beruehrt_haltung(al_objekt, haltungsgeom, toleranz):
            return True

        for punkt in self._anschluss_endpunkte_lesen(al_objekt):
            for kandidat in self._anschlussleitungen_am_punkt_finden(
                al_objekt, punkt, a_objekte, toleranz
            ):
                if self._anschluss_hat_pfad_zur_haltung(
                    kandidat,
                    a_objekte,
                    haltungsgeom,
                    toleranz,
                    set(besuchte_ids),
                ):
                    return True

        return False

    def _finde_eltern_anschlussleitung_nach_endpunkten(
        self,
        aktuelles_objekt: ExportZeile,
        a_objekte: List[ExportZeile],
        haltungsgeom: QgsGeometry,
        toleranz: float = 0.05,
    ) -> str:
        """Sucht die direkte Elternleitung einer Anschlussleitung.

        Berührt die Leitung die Haltung selbst, bleibt HG012 leer. Andernfalls
        wird an ihren Endpunkten die erste Nachbarleitung gewählt, über die
        ein geometrischer Pfad zur Haltung besteht.

        :param aktuelles_objekt: Anschlussleitung, deren Elternleitung gesucht
            wird.
        :param a_objekte: Alle geladenen Anschlussleitungen.
        :param haltungsgeom: Geometrie der zugehörigen Haltung.
        :param toleranz: Toleranz für geometrische Berührungen.
        :return: Name der Elternleitung oder ein Leerstring.
        """
        if aktuelles_objekt is None:
            return ""

        if self._anschluss_beruehrt_haltung(
            aktuelles_objekt, haltungsgeom, toleranz
        ):
            return ""

        aktuelle_id = aktuelles_objekt.get("pk")
        for punkt in self._anschluss_endpunkte_lesen(aktuelles_objekt):
            for kandidat in self._anschlussleitungen_am_punkt_finden(
                aktuelles_objekt, punkt, a_objekte, toleranz
            ):
                besuchte_ids: Set[int] = set()
                if aktuelle_id is not None:
                    besuchte_ids.add(aktuelle_id)

                if self._anschluss_hat_pfad_zur_haltung(
                    kandidat,
                    a_objekte,
                    haltungsgeom,
                    toleranz,
                    besuchte_ids,
                ):
                    return str(kandidat.get("leitnam") or "").strip()

        return ""

    def _anschlussendpunkt_distanz_zu_haltung(
        self, anschlussgeom: QgsGeometry, haltungsgeom: QgsGeometry
    ) -> Optional[float]:
        """Berechnet den kleinsten Abstand eines Leitungsendpunkts zur Haltung.
        """
        linienpunkte = self._lade_linienpunkte(anschlussgeom)
        if len(linienpunkte) < 2 or haltungsgeom is None:
            return None

        kleinste_distanz = None
        for linienpunkt in (linienpunkte[0], linienpunkte[-1]):
            abstand = haltungsgeom.distance(
                QgsGeometry.fromPointXY(QgsPointXY(linienpunkt))
            )
            if kleinste_distanz is None or abstand < kleinste_distanz:
                kleinste_distanz = abstand
        return kleinste_distanz

    def _finde_haltung_von_anschluss(
        self,
        al_objekt: ExportObjekt,
        h_quelle: object,
        ausgewaehlte_haltungen: Optional[Iterable[str]] = None,
        toleranz: float = 0.25,
        haltungskandidaten: Optional[Mapping[str, ExportObjekt]] = None,
    ) -> Optional[ExportObjekt]:
        """Ermittelt die zugehörige Haltung einer Anschlussleitung.

        Eine explizite QKan-Beziehung über ``haltnam`` hat Vorrang. Nur wenn
        sie fehlt, wird geometrisch gesucht. Bei einer Benutzerauswahl werden
        ausschließlich Leitungsendpunkte und eine enge Toleranz verwendet,
        damit eine kreuzende Leitung nicht der falschen Haltung zugeordnet
        wird.

        :param al_objekt: Anschlussleitung aus QGIS- oder YAML-Daten.
        :param h_quelle: Quelle der Haltungsobjekte.
        :param ausgewaehlte_haltungen: Optionale Einschränkung auf ausgewählte
            Haltungen.
        :param toleranz: Maximaler geometrischer Abstand.
        :param haltungskandidaten: Optionaler Index bereits geladener
            Haltungen.
        :return: Zugehörige Haltung oder ``None``.
        """
        haltungen_auswahl = set(ausgewaehlte_haltungen or [])
        anschlussgeom = self._objekt_geometrie(al_objekt)
        if anschlussgeom is None or anschlussgeom.isEmpty():
            return None

        haltnam = str(self._objekt_wert(al_objekt, "haltnam") or "").strip()
        if haltnam:
            if (
                ausgewaehlte_haltungen is not None
                and haltnam not in haltungen_auswahl
            ):
                return None

            objekt = (
                haltungskandidaten.get(haltnam)
                if haltungskandidaten is not None
                else self._finde_haltung_durch_name(h_quelle, haltnam)
            )
            return objekt

        bestes_objekt = None
        kleinste_distanz = None
        h_objekte = (
            haltungskandidaten.values()
            if haltungskandidaten is not None
            else self._objekte_iterieren(h_quelle)
        )
        for hal_objekt in h_objekte:
            h_name = str(
                self._objekt_wert(hal_objekt, "haltnam") or ""
            )
            if haltungen_auswahl and h_name not in haltungen_auswahl:
                continue

            haltungsgeom = self._objekt_geometrie(hal_objekt)
            if haltungsgeom is None or haltungsgeom.isEmpty():
                continue

            if haltungen_auswahl:
                abstand = self._anschlussendpunkt_distanz_zu_haltung(
                    anschlussgeom, haltungsgeom
                )
                pruef_toleranz = self.ANSCHLUSS_ENDPOINT_TOLERANZ_M
            else:
                abstand = anschlussgeom.distance(haltungsgeom)
                pruef_toleranz = toleranz

            if (
                abstand is not None
                and abstand <= pruef_toleranz
                and (kleinste_distanz is None or abstand < kleinste_distanz)
            ):
                kleinste_distanz = abstand
                bestes_objekt = hal_objekt

        return bestes_objekt

    def _proj_punkt_auf_linie(
        self, liniengeom: QgsGeometry, punkt: QgsPointXY
    ) -> Optional[QgsPointXY]:
        """Projiziert einen Punkt auf die nächstgelegene Stelle einer Linie."""
        if liniengeom is None or punkt is None:
            return None
        punktgeom = QgsGeometry.fromPointXY(QgsPointXY(punkt))
        projektionspunkt = liniengeom.nearestPoint(punktgeom)
        if projektionspunkt and not projektionspunkt.isEmpty():
            return projektionspunkt.asPoint()

        projektionspunkt = liniengeom.closestPoint(punktgeom)
        if projektionspunkt and not projektionspunkt.isEmpty():
            return projektionspunkt.asPoint()

        return None

    def _orient_anschlussleitung_zu_haltung(
        self,
        linienpunkte: Sequence[QgsPointXY],
        haltungsgeom: QgsGeometry,
    ) -> Tuple[
        List[QgsPointXY],
        Optional[QgsPointXY],
        Optional[QgsPointXY],
        Optional[bool],
    ]:
        """Orientiert eine Anschlussleitung von der Haltung zum freien Ende.

        Für die Zuordnung wird das der Haltung nähere Ende als Anschlusspunkt
        verwendet und die Arbeitskopie von dort zum freien Ende orientiert.
        Diese Reihenfolge dient nur der topologischen Auswertung. Die von
        DWA-M 150 geforderte GO-Ausgabe in Fließrichtung muss der aufrufende
        Export getrennt sicherstellen.

        :param linienpunkte: Punktfolge der Anschlussleitung.
        :param haltungsgeom: Geometrie der zugehörigen Haltung.
        :return: Orientierte Punkte, projizierter Anschlusspunkt, freies Ende
            und Kennzeichen, ob der ursprüngliche Start an der Haltung lag.
        """
        if not linienpunkte or len(linienpunkte) < 2 or haltungsgeom is None:
            return list(linienpunkte), None, None, None

        startpunkt = QgsPointXY(linienpunkte[0])
        endpunkt = QgsPointXY(linienpunkte[-1])
        start_geom = QgsGeometry.fromPointXY(startpunkt)
        end_geom = QgsGeometry.fromPointXY(endpunkt)
        startabstand = haltungsgeom.distance(start_geom)
        endabstand = haltungsgeom.distance(end_geom)

        if startabstand <= endabstand:
            ausgerichtete_linienpunkte = list(linienpunkte)
            haltung_end = startpunkt
            freies_ende = endpunkt
            anschluss_start = True
        else:
            ausgerichtete_linienpunkte = list(reversed(list(linienpunkte)))
            haltung_end = endpunkt
            freies_ende = startpunkt
            anschluss_start = False

        projektionspunkt = self._proj_punkt_auf_linie(
            haltungsgeom, haltung_end
        )
        return (
            ausgerichtete_linienpunkte,
            projektionspunkt,
            freies_ende,
            anschluss_start,
        )

    def _finde_naechste_haltung(
        self, geometrie: QgsGeometry, h_quelle: object
    ) -> Optional[ExportObjekt]:
        """Sucht die nächstgelegene Haltung in QGIS- oder YAML-Daten."""
        bestes_objekt = None
        kleinste_distanz = None
        for hal_objekt in self._objekte_iterieren(h_quelle):
            haltungsgeom = self._objekt_geometrie(hal_objekt)
            if haltungsgeom is None or haltungsgeom.isEmpty():
                continue
            abstand = geometrie.distance(haltungsgeom)
            if kleinste_distanz is None or abstand < kleinste_distanz:
                kleinste_distanz = abstand
                bestes_objekt = hal_objekt
        return bestes_objekt

    def _anschluss_codewerte(
        self, objekt: ExportZeile
    ) -> Tuple[str, str]:
        """Liefert HG008 und HG009 aus den tatsächlich verfügbaren Werten.

        Für HG008 ist in QKan weiterhin kein eindeutiges Feld vorhanden und
        es bleibt deshalb leer. HG009 wird direkt aus
        ``anschlussleitungen.lageanschluss`` übernommen.
        """
        hg008 = ""
        lageanschluss = self._wert_in_zahl_oder_none(
            objekt.get("lageanschluss")
        )
        if lageanschluss is None:
            return hg008, ""

        return hg008, f"{int(lageanschluss):02d}"

    def _finde_anschlussschacht_nach_punkt(
        self,
        punkt: Optional[QgsPointXY],
        quelle: object,
        haltnam: object = None,
        urstation: object = None,
    ) -> Optional[ExportObjekt]:
        """Findet am freien Leitungsende den passendsten Anschlussschacht.

        Die Geometrie innerhalb der vorhandenen 5-cm-Endpunkttoleranz ist
        zwingend. Haltung und Urstation entscheiden nur zwischen mehreren
        geometrischen Treffern; ``pk`` dient als stabile letzte Sortierung.
        """
        if punkt is None or quelle is None:
            return None

        toleranz = self.ANSCHLUSS_ENDPOINT_TOLERANZ_M
        punkt_geom = QgsGeometry.fromPointXY(QgsPointXY(punkt))
        ziel_haltnam = str(haltnam or "").strip()
        ziel_station = self._wert_in_zahl_oder_none(urstation)
        treffer = []

        for objekt in self._objekte_iterieren(quelle):
            geometrie = self._objekt_geometrie(objekt)
            if geometrie is None or geometrie.isEmpty():
                continue
            abstand = geometrie.distance(punkt_geom)
            if abstand > toleranz:
                continue

            objekt_haltnam = str(
                self._objekt_wert(objekt, "haltnam") or ""
            ).strip()
            haltnam_abweichung = (
                0
                if ziel_haltnam and objekt_haltnam == ziel_haltnam
                else 1
            )

            objekt_station = self._wert_in_zahl_oder_none(
                self._objekt_wert(objekt, "urstation")
            )
            if ziel_station is not None and objekt_station is not None:
                stationsabweichung = abs(objekt_station - ziel_station)
            else:
                stationsabweichung = float("inf")

            pk = self._wert_in_zahl_oder_none(
                self._objekt_wert(objekt, "pk")
            )
            treffer.append((
                haltnam_abweichung,
                stationsabweichung,
                abstand,
                pk if pk is not None else float("inf"),
                objekt,
            ))

        if not treffer:
            return None
        treffer.sort(key=lambda eintrag: eintrag[:-1])
        return treffer[0][-1]

    def _anschlussknoten_exportname_erzeugen(
        self,
        leitnam: str,
        verwendete_namen: Set[str],
    ) -> str:
        """Erzeugt für namenlose Anschluss-/Fiktivknoten einen KG001-Namen."""
        basis = str(leitnam or "ANSCHLUSSKNOTEN").strip()
        nummer = 1
        while True:
            kandidat = f"{basis}_{nummer:02d}"
            if kandidat not in verwendete_namen:
                verwendete_namen.add(kandidat)
                return kandidat
            nummer += 1

    def _export_anschlussschacht_kg(
        self,
        xml_wurzel: _EinfachesXmlElement,
        objekt: ExportObjekt,
        kg_id: str,
        fallback_entwart: object,
        fallback_punkt: QgsPointXY,
        fallback_z: object,
    ) -> None:
        """Exportiert einen realen QKan-Anschlussschacht als M150-KG."""
        x, y = self._lese_schacht_koord(objekt)
        if x is None or y is None:
            x = fallback_punkt.x()
            y = fallback_punkt.y()

        entwart_wert = self._objekt_wert(objekt, "entwart")
        if entwart_wert in (None, "", "NULL"):
            entwart_wert = fallback_entwart
        entwart_code = self._entwart_map_in_m150(entwart_wert)

        knotentyp = self._objekt_wert(objekt, "knotentyp")
        kg305 = self._knotenart_map_m150(knotentyp)
        if not kg305:
            if str(knotentyp or "").strip():
                warnung = ("KG305", "116", str(knotentyp).strip())
                if warnung not in self._export_ref_warnungen:
                    self._export_ref_warnungen.add(warnung)
                    LOGGER.warning(
                        "M150-Export: Anschlussknoten '%s' hat die nicht "
                        "zuordenbare Knotenart '%s'; KG305 wird als Z "
                        "(Sonstige) exportiert.",
                        kg_id,
                        knotentyp,
                    )
                kg305 = "Z"
            else:
                kg305 = "F"

        xml_kg = SubElement(xml_wurzel, "KG")
        SubElement(xml_kg, "KG001").text = kg_id
        strasse = self._objekt_wert(objekt, "strasse")
        if strasse not in (None, "", "NULL"):
            SubElement(xml_kg, "KG102").text = str(strasse)
        if entwart_code:
            SubElement(xml_kg, "KG302").text = entwart_code

        baujahr = self._text_in_ganzzahl(
            self._objekt_wert(objekt, "baujahr")
        )
        if baujahr:
            SubElement(xml_kg, "KG303").text = baujahr

        material_code = self._material_map_m150(
            self._objekt_wert(objekt, "material")
        )
        if material_code:
            SubElement(xml_kg, "KG304").text = material_code
        SubElement(xml_kg, "KG305").text = kg305

        durchm_wert = self._wert_in_zahl_oder_none(
            self._objekt_wert(objekt, "durchm")
        )
        if durchm_wert is not None:
            durchm = str(int(durchm_wert * 1000))
            SubElement(xml_kg, "KG308").text = durchm
            SubElement(xml_kg, "KG309").text = durchm

        simstatus = self._objekt_wert(objekt, "simstatus")
        kg401 = self._standard_rt_code_fuer_wert("109", simstatus)
        if kg401:
            SubElement(xml_kg, "KG401").text = kg401

        kommentar = self._objekt_wert(objekt, "kommentar")
        if kommentar not in (None, "", "NULL"):
            SubElement(xml_kg, "KG999").text = str(kommentar)

        xml_go = SubElement(xml_kg, "GO")
        SubElement(xml_go, "GO001").text = kg_id
        SubElement(xml_go, "GO002").text = "G"
        SubElement(xml_go, "GO003").text = "Pkt"

        z_value = self._objekt_wert(objekt, "sohlhoehe")
        if z_value in (None, "", "NULL"):
            z_value = fallback_z
        self._erzeuge_gp_block(
            xml_go,
            kg_id,
            x,
            y,
            self._formatiere_zahl_oder_leer(z_value),
        )

    def _export_anschlusspunkt_kg(
        self,
        xml_wurzel: _EinfachesXmlElement,
        kg_id: str,
        entwart_code: str,
        punkt: QgsPointXY,
        z_value: object,
    ) -> None:
        """Schreibt einen künstlichen KG-Knoten für ein freies Leitungsende.

        Endet die Anschlussleitung nicht an einem realen QKan-Schacht,
        benötigt die M150-Netztopologie trotzdem einen bezeichneten Endpunkt.
        Er wird mit KG305=F gemäß Referenztabelle 116 als fiktiver Schacht
        exportiert, ohne ein neues QKan-Bestandsobjekt anzulegen.

        :param xml_wurzel: Wurzelelement des Exportdokuments.
        :param kg_id: Kennung des künstlichen Knotens.
        :param entwart_code: M150-Code der Entwässerungsart.
        :param punkt: Lage des freien Leitungsendes.
        :param z_value: Optionale Höhenangabe.
        """
        xml_kg = SubElement(xml_wurzel, "KG")
        SubElement(xml_kg, "KG001").text = kg_id
        if entwart_code:
            SubElement(xml_kg, "KG302").text = entwart_code
        SubElement(xml_kg, "KG305").text = "F"

        xml_go = SubElement(xml_kg, "GO")
        SubElement(xml_go, "GO001").text = kg_id
        SubElement(xml_go, "GO002").text = "G"
        SubElement(xml_go, "GO003").text = "Pkt"

        self._erzeuge_gp_block(
            xml_go,
            kg_id,
            punkt.x(),
            punkt.y(),
            self._formatiere_zahl_oder_leer(z_value),
        )

    def _bestimme_fliessrichtung_haltung(
        self,
        objekt: ExportZeile,
        linienpunkte: Sequence[QgsPointXY],
    ) -> Tuple[str, str, List[QgsPointXY]]:
        """Bestimmt Start, Ende und Punktreihenfolge einer Exportzeile.

        DWA-M 150 fordert GO-Linien in Fließrichtung. Widersprechen die beiden
        numerischen Sohlhöhen der gespeicherten QGIS-Reihenfolge, werden
        sowohl Knotenrollen als auch Geometriepunkte umgedreht. Ohne zwei
        Höhen bleibt die QKan-Reihenfolge maßgeblich.
        """
        schoben = str(objekt.get("schoben") or "")
        schunten = str(objekt.get("schunten") or "")

        startname = schoben
        endname = schunten
        linienpunkte = list(linienpunkte)

        sohle_oben = self._wert_in_zahl_oder_none(objekt.get("sohleoben"))
        sohle_unten = self._wert_in_zahl_oder_none(objekt.get("sohleunten"))

        if (
            sohle_oben is not None
            and sohle_unten is not None
            and sohle_unten > sohle_oben
        ):
            startname = schunten
            endname = schoben
            linienpunkte = list(reversed(linienpunkte))

        return startname, endname, linienpunkte

    def _lese_schacht_koord(
        self, objekt: ExportZeile
    ) -> Tuple[Optional[float], Optional[float]]:
        """Liest Schachtkoordinaten aus einer per YAML geladenen Zeile."""
        x = self._wert_in_zahl_oder_none(objekt.get("xsch"))
        y = self._wert_in_zahl_oder_none(objekt.get("ysch"))
        if x is not None and y is not None:
            return x, y

        geometrie = objekt.get("__geometry")
        if geometrie is not None and not geometrie.isEmpty():
            punkt = geometrie.asPoint()
            if not punkt.isEmpty():
                return punkt.x(), punkt.y()

            linienpunkte = self._lade_linienpunkte(geometrie)
            if linienpunkte:
                return linienpunkte[0].x(), linienpunkte[0].y()

        return None, None

    def _lese_haltung_sohlen(
        self,
        objekt: ExportZeile,
        startname: str,
        endname: str,
    ) -> Tuple[object, object]:
        """Liest die zur Exportreihenfolge passenden Haltungssohlen.

        :param objekt: Geladene Haltungszeile.
        :param startname: Name des Exportstarts.
        :param endname: Name des Exportendes.
        :return: Sohlhöhen am Exportstart und Exportende.
        """
        schoben = str(objekt.get("schoben") or "")
        sohle_oben = objekt.get("sohleoben")
        sohle_unten = objekt.get("sohleunten")

        if startname == schoben:
            return sohle_oben, sohle_unten
        return sohle_unten, sohle_oben

    def _finde_haltung_durch_name(
        self, h_quelle: object, haltnam: str
    ) -> Optional[ExportObjekt]:
        """Sucht eine Haltung nach Namen in QGIS- oder YAML-Daten."""
        for objekt in self._objekte_iterieren(h_quelle):
            if str(self._objekt_wert(objekt, "haltnam") or "") == str(haltnam):
                return objekt
        return None

    def _berechne_station_haltung(
        self, haltungsgeom: QgsGeometry, anschlusspunkt: QgsPointXY
    ) -> float:
        """Berechnet HG007 entlang der exportorientierten Haltung.

        HG007 ist nach DWA-M 150 die Station im Objekt, an das die
        Anschlussleitung angeschlossen wird. Der Anschlusspunkt wird vor der
        Stationierung auf die Haltung projiziert.
        """
        if haltungsgeom is None or anschlusspunkt is None:
            return 0.0
        return max(
            0.0,
            float(
                haltungsgeom.lineLocatePoint(
                    QgsGeometry.fromPointXY(QgsPointXY(anschlusspunkt))
                )
            ),
        )

    def _setze_text_oder_leer(
        self,
        parent: _EinfachesXmlElement,
        tag: str,
        wert: object,
    ) -> None:
        """Schreibt einen XML-Wert oder ein leeres Element.

        DWA-M 150 verlangt in den gewählten Formatfolgen auch leere
        Datenfelder. Deshalb wird bei einer fehlenden QKan-Angabe nicht das
        gesamte XML-Element ausgelassen.

        :param parent: Übergeordnetes XML-Element.
        :param tag: Name des zu erzeugenden Elements.
        :param wert: Zu schreibender Wert.
        """
        if wert in (None, "", "NULL"):
            SubElement(parent, tag)
        else:
            SubElement(parent, tag).text = str(wert)

    def _text_in_ganzzahl(self, wert: object) -> Optional[str]:
        """Gibt einen numerischen Wert ohne Nachkommastellen als Text zurück.
        """
        number = self._wert_in_zahl_oder_none(wert)
        if number is None:
            return None
        return str(int(number))

    def _erzeuge_gp_block(
        self,
        parent: _EinfachesXmlElement,
        punktkennung: str,
        x: float,
        y: float,
        z_text: str,
        gp999: Optional[str] = None,
    ) -> _EinfachesXmlElement:
        """Erzeugt einen GP-Block mit Koordinaten.

        GP005/GP006 tragen Ost-/Nordkoordinate, GP007 die Höhe und GP010 das
        Höhensystem. ``RA``/``RE`` in GP999 sind QKan-kompatible Rollenmarker
        im freien M150-Bemerkungsfeld und keine standardisierten Schlüssel.

        :param parent: Übergeordnetes GO-Element.
        :param punktkennung: Kennung des Geometriepunkts.
        :param x: Rechtswert.
        :param y: Hochwert.
        :param z_text: Bereits formatierte Höhenangabe.
        :param gp999: Optionale Rollenkennung wie ``RA`` oder ``RE``.
        :return: Erzeugtes GP-Element.
        """
        xml_gp = SubElement(parent, "GP")
        SubElement(xml_gp, "GP001").text = punktkennung
        SubElement(xml_gp, "GP002").text = "UTM"
        SubElement(xml_gp, "GP005").text = self._formatiere_zahlen_export(x)
        SubElement(xml_gp, "GP006").text = self._formatiere_zahlen_export(y)
        SubElement(xml_gp, "GP007").text = z_text
        SubElement(xml_gp, "GP010").text = "mNN"
        if gp999:
            SubElement(xml_gp, "GP999").text = gp999
        return xml_gp

    def _export_haltungen(
        self,
        xml_wurzel: _EinfachesXmlElement,
        h_objekte: List[ExportZeile],
    ) -> None:
        """Exportiert die über YAML-Abfragen geladenen Haltungen.

        Pro QKan-Haltung entsteht ein HG-Grunddatenblock mit HG313=A
        (Kanal) und genau ein GO-Linienobjekt. Die beiden Endpunkte erhalten
        zusätzlich die QKan-Rollenmarker RA/RE in GP999.
        """
        for objekt in h_objekte:
            geometrie = objekt.get("__geometry")
            if geometrie is None or geometrie.isEmpty():
                continue

            linienpunkte = self._lade_linienpunkte(geometrie)
            if len(linienpunkte) < 2:
                continue

            startname, endname, exportpunkte = (
                self._bestimme_fliessrichtung_haltung(
                    objekt, linienpunkte
                )
            )

            material_code = self._material_map_m150(objekt.get("material"))
            profil_code = self._profil_map_m150(objekt.get("profilnam"))
            innenmaterial_code = self._material_map_m150(
                objekt.get("innenmaterial")
            )
            profilauskleidung_code = self._profilauskleidung_map_m150(
                objekt.get("profilauskleidung")
            )
            z_start, z_end = self._lese_haltung_sohlen(
                objekt, startname, endname
            )

            xml_hg = SubElement(xml_wurzel, "HG")
            # HG001 identifiziert die Haltung; HG003/HG004 sind Anfang und
            # Ende in der oben bestimmten M150-Fließrichtung.
            SubElement(xml_hg, "HG001").text = str(objekt.get("haltnam") or "")
            SubElement(xml_hg, "HG003").text = startname
            SubElement(xml_hg, "HG004").text = endname
            self._setze_text_oder_leer(
                xml_hg,
                "HG301",
                self._kanalart_aus_abflussart_map_m150(
                    objekt.get("abflussart")
                ),
            )
            SubElement(xml_hg, "HG302").text = self._entwart_map_in_m150(
                objekt.get("entwart")
            )
            self._setze_text_oder_leer(
                xml_hg,
                "HG303",
                self._text_in_ganzzahl(objekt.get("baujahr")),
            )
            self._setze_text_oder_leer(xml_hg, "HG304", material_code)
            self._setze_text_oder_leer(xml_hg, "HG305", profil_code)
            self._setze_text_oder_leer(
                xml_hg,
                "HG306",
                self._text_in_ganzzahl(objekt.get("breite")),
            )
            self._setze_text_oder_leer(
                xml_hg,
                "HG307",
                self._text_in_ganzzahl(objekt.get("hoehe")),
            )
            self._setze_text_oder_leer(
                xml_hg, "HG308", profilauskleidung_code
            )
            self._setze_text_oder_leer(
                xml_hg, "HG309", innenmaterial_code
            )
            SubElement(xml_hg, "HG310").text = self._formatiere_zahlen_export(
                objekt.get("laenge")
            )
            SubElement(xml_hg, "HG313").text = "A"

            xml_go = SubElement(xml_hg, "GO")
            # Referenztabellen 300/301: H = Haltung, L = Linie.
            SubElement(xml_go, "GO002").text = "H"
            SubElement(xml_go, "GO003").text = "L"

            self._erzeuge_gp_block(
                xml_go,
                startname,
                exportpunkte[0].x(),
                exportpunkte[0].y(),
                self._formatiere_zahlen_export(z_start),
                gp999="RA",
            )
            self._erzeuge_gp_block(
                xml_go,
                endname,
                exportpunkte[-1].x(),
                exportpunkte[-1].y(),
                self._formatiere_zahlen_export(z_end),
                gp999="RE",
            )

    def _export_schaechte(
        self,
        xml_wurzel: _EinfachesXmlElement,
        s_objekte: List[ExportZeile],
    ) -> None:
        """Exportiert die über YAML-Abfragen geladenen Schächte.

        Pro QKan-Schacht entsteht ein KG-Grunddatenblock und ein
        GO-Punktobjekt. Kann der QKan-Knotentyp nicht zugeordnet werden, wird
        KG305=S (Schacht) als fachlich engster Rückfall verwendet.
        """
        for objekt in s_objekte:
            x, y = self._lese_schacht_koord(objekt)
            if x is None or y is None:
                continue

            entwart_code = self._entwart_map_in_m150(objekt.get("entwart"))
            kg305 = self._knotenart_map_m150(objekt.get("knotentyp"))
            if not kg305:
                kg305 = self._knotenart_map_m150(objekt.get("schachttyp"))
            if not kg305:
                kg305 = "S"

            xml_kg = SubElement(xml_wurzel, "KG")
            SubElement(xml_kg, "KG001").text = str(objekt.get("schnam") or "")
            if entwart_code:
                SubElement(xml_kg, "KG302").text = entwart_code
            SubElement(xml_kg, "KG305").text = kg305

            durchm_wert = self._wert_in_zahl_oder_none(objekt.get("durchm"))
            if durchm_wert is not None:
                # QKan speichert den Schachtdurchmesser in Metern. Die
                # Multiplikation für KG308/KG309 ist die ausdrücklich
                # verwendete Millimeterkonvention dieses Exports.
                durchm = str(int(durchm_wert * 1000))
                SubElement(xml_kg, "KG308").text = durchm
                SubElement(xml_kg, "KG309").text = durchm

            druckdicht = self._wert_in_zahl_oder_none(
                objekt.get("druckdicht")
            )
            if druckdicht in (0.0, 1.0):
                SubElement(xml_kg, "KG315").text = str(int(druckdicht))

            xml_go = SubElement(xml_kg, "GO")
            SubElement(xml_go, "GO001").text = str(objekt.get("schnam") or "")
            SubElement(xml_go, "GO002").text = "G"
            SubElement(xml_go, "GO003").text = "Pkt"

            self._erzeuge_gp_block(
                xml_go,
                str(objekt.get("schnam") or ""),
                x,
                y,
                self._formatiere_zahlen_export(objekt.get("sohlhoehe")),
            )

    def _export_anschlussleitungen(
        self,
        xml_wurzel: _EinfachesXmlElement,
        a_objekte: List[ExportZeile],
        h_objekte: List[ExportZeile],
        s_objekte: List[ExportZeile],
        as_objekte: List[ExportZeile],
    ) -> None:
        """Exportiert ausgewählte Anschlussleitungen in das XML-Dokument.

        Anschlussleitungen werden ebenfalls als HG geführt, aber durch
        HG313=B und die Zusatzfelder HG005-HG012 von Haltungen unterschieden.
        Die Elternhaltung wird vorrangig über ``haltnam`` und ersatzweise
        über die Geometrie ermittelt.

        :param xml_wurzel: Wurzelelement des Exportdokuments.
        :param a_objekte: Geladene Anschlussleitungen.
        :param h_objekte: Geladene Haltungen.
        :param s_objekte: Geladene Schächte.
        :param as_objekte: Geladene Anschlussschächte.
        """
        haltung_index = {
            str(objekt.get("haltnam")): objekt
            for objekt in h_objekte
            if objekt.get("haltnam")
        }
        verwendete_knotennamen = {
            str(objekt.get("schnam")).strip()
            for objekt in list(s_objekte) + list(as_objekte)
            if objekt.get("schnam") and str(objekt.get("schnam")).strip()
        }
        anschlussknoten_name_nach_pk: Dict[object, str] = {}
        exportierte_anschlussknoten: Set[object] = set()

        for objekt in a_objekte:
            geometrie = objekt.get("__geometry")
            if geometrie is None or geometrie.isEmpty():
                continue

            linienpunkte = self._lade_linienpunkte(geometrie)
            if len(linienpunkte) < 2:
                continue

            verbundene_haltung = self._finde_haltung_von_anschluss(
                objekt,
                h_objekte,
                haltungskandidaten=haltung_index,
            )
            if verbundene_haltung is None:
                continue

            haltung_geometrie = verbundene_haltung.get("__geometry")
            if haltung_geometrie is None or haltung_geometrie.isEmpty():
                continue

            hal_punkte = self._lade_linienpunkte(haltung_geometrie)
            if len(hal_punkte) < 2:
                continue

            startname, endname, export_h_pts = (
                self._bestimme_fliessrichtung_haltung(
                    verbundene_haltung, hal_punkte
                )
            )
            h_geom_oriented = QgsGeometry.fromPolylineXY(
                [QgsPointXY(p) for p in export_h_pts]
            )

            (
                ausgerichtete_linienpunkte,
                anschlusspunkt,
                freies_ende,
                _anschluss_start,
            ) = self._orient_anschlussleitung_zu_haltung(
                linienpunkte,
                h_geom_oriented,
            )
            if (
                not ausgerichtete_linienpunkte
                or anschlusspunkt is None
                or freies_ende is None
            ):
                continue

            station = self._wert_in_zahl_oder_none(objekt.get("urstation"))
            material_code = self._material_map_m150(objekt.get("material"))
            leitnam = str(objekt.get("leitnam") or "").strip()

            freies_ende_schacht = self._finde_schacht_nach_punkt(
                freies_ende, s_objekte
            )
            freies_ende_anschlussschacht = None
            freies_ende_name = (
                str(freies_ende_schacht.get("schnam"))
                if freies_ende_schacht is not None
                and freies_ende_schacht.get("schnam")
                else None
            )
            endpunkt_typ = "F"

            if freies_ende_name and freies_ende_schacht is not None:
                endpunkt_typ = self._knotenart_map_m150(
                    freies_ende_schacht.get("knotentyp")
                )
                if not endpunkt_typ:
                    endpunkt_typ = self._knotenart_map_m150(
                        freies_ende_schacht.get("schachttyp")
                    )
                if not endpunkt_typ:
                    endpunkt_typ = "S"
            else:
                freies_ende_anschlussschacht = (
                    self._finde_anschlussschacht_nach_punkt(
                        freies_ende,
                        as_objekte,
                        haltnam=verbundene_haltung.get("haltnam"),
                        urstation=station,
                    )
                )
                if freies_ende_anschlussschacht is not None:
                    anschluss_pk = freies_ende_anschlussschacht.get("pk")
                    gespeicherter_name = str(
                        freies_ende_anschlussschacht.get("schnam") or ""
                    ).strip()
                    if gespeicherter_name:
                        freies_ende_name = gespeicherter_name
                    elif anschluss_pk in anschlussknoten_name_nach_pk:
                        freies_ende_name = anschlussknoten_name_nach_pk[
                            anschluss_pk
                        ]
                    else:
                        freies_ende_name = (
                            self._anschlussknoten_exportname_erzeugen(
                                leitnam, verwendete_knotennamen
                            )
                        )
                        anschlussknoten_name_nach_pk[
                            anschluss_pk
                        ] = freies_ende_name

                    knotentyp = freies_ende_anschlussschacht.get(
                        "knotentyp"
                    )
                    endpunkt_typ = self._knotenart_map_m150(knotentyp)
                    if not endpunkt_typ:
                        endpunkt_typ = (
                            "Z" if str(knotentyp or "").strip() else "F"
                        )
                else:
                    freies_ende_name = (
                        self._anschlussknoten_exportname_erzeugen(
                            leitnam, verwendete_knotennamen
                        )
                    )

            profil_code = self._profil_map_m150(objekt.get("profilnam"))
            innenmaterial_code = self._material_map_m150(
                objekt.get("innenmaterial")
            )
            profilauskleidung_code = self._profilauskleidung_map_m150(
                objekt.get("profilauskleidung")
            )

            haltnam_clean = str(verbundene_haltung.get("haltnam") or "")
            ziel_id = freies_ende_name or leitnam
            hg005 = ziel_id
            hg011 = leitnam

            hg012 = self._finde_eltern_anschlussleitung_nach_endpunkten(
                objekt,
                a_objekte,
                h_geom_oriented,
                self.ANSCHLUSS_ENDPOINT_TOLERANZ_M,
            )

            # HG006/HG007 beziehen sich auf das Objekt, von dem verzweigt
            # bzw. an das angeschlossen wird. Bei direktem Anschluss ist das
            # die Haltung (H). Bei einer Verzweigung von einer anderen
            # Anschlussleitung ist es eine Abwasserleitung (L), und die
            # Station wird auf dieser Elternleitung geführt.
            hg006 = "H"
            if hg012:
                hg006 = "L"
                eltern_objekt = next(
                    (
                        kandidat
                        for kandidat in a_objekte
                        if str(kandidat.get("leitnam") or "").strip() == hg012
                    ),
                    None,
                )
                eltern_geometrie = (
                    eltern_objekt.get("__geometry")
                    if eltern_objekt is not None
                    else None
                )
                if (
                    station is None
                    and eltern_geometrie is not None
                    and not eltern_geometrie.isEmpty()
                ):
                    endpunkte = self._anschluss_endpunkte_lesen(objekt)
                    if endpunkte:
                        verbindungspunkt = min(
                            endpunkte,
                            key=lambda punkt: eltern_geometrie.distance(
                                QgsGeometry.fromPointXY(QgsPointXY(punkt))
                            ),
                        )
                        projektionspunkt = self._proj_punkt_auf_linie(
                            eltern_geometrie, verbindungspunkt
                        )
                        if projektionspunkt is not None:
                            station = self._berechne_station_haltung(
                                eltern_geometrie, projektionspunkt
                            )

            if station is None and hg006 == "H":
                station = self._berechne_station_haltung(
                    h_geom_oriented, anschlusspunkt
                )

            entwart_code = self._entwart_map_in_m150(objekt.get("entwart"))
            hg008, hg009 = self._anschluss_codewerte(objekt)

            z_start = objekt.get("sohleoben")
            z_end = objekt.get("sohleunten")

            xml_hg = SubElement(xml_wurzel, "HG")
            # Bedeutung der Anschlussfelder nach DWA-M 150:
            # HG005 Endobjekt, HG006 Typ des Elternobjekts, HG007 Station,
            # HG008 Stationierungsrichtung, HG009 Uhrlage, HG010 Endpunkttyp,
            # HG011 Leitungsname und HG012 direkte Elternleitung.
            SubElement(xml_hg, "HG001").text = haltnam_clean
            SubElement(xml_hg, "HG003").text = startname
            SubElement(xml_hg, "HG004").text = endname
            SubElement(xml_hg, "HG005").text = hg005
            SubElement(xml_hg, "HG006").text = hg006
            SubElement(xml_hg, "HG007").text = self._formatiere_zahlen_export(
                station, nachkommastellen=2
            )
            SubElement(xml_hg, "HG008").text = hg008
            SubElement(xml_hg, "HG009").text = hg009
            SubElement(xml_hg, "HG010").text = endpunkt_typ
            SubElement(xml_hg, "HG011").text = hg011
            self._setze_text_oder_leer(xml_hg, "HG012", hg012)
            # Anschlussleitungen besitzen in QKan kein eigenes Feld
            # ``abflussart``. Für HG301 wird deshalb die Abflussart der
            # zugeordneten Haltung übernommen.
            self._setze_text_oder_leer(
                xml_hg,
                "HG301",
                self._kanalart_aus_abflussart_map_m150(
                    verbundene_haltung.get("abflussart")
                ),
            )
            SubElement(xml_hg, "HG302").text = entwart_code
            self._setze_text_oder_leer(
                xml_hg,
                "HG303",
                self._text_in_ganzzahl(objekt.get("baujahr")),
            )
            self._setze_text_oder_leer(xml_hg, "HG304", material_code)
            self._setze_text_oder_leer(xml_hg, "HG305", profil_code)
            self._setze_text_oder_leer(
                xml_hg,
                "HG306",
                self._text_in_ganzzahl(objekt.get("breite")),
            )
            self._setze_text_oder_leer(
                xml_hg,
                "HG307",
                self._text_in_ganzzahl(objekt.get("hoehe")),
            )
            self._setze_text_oder_leer(
                xml_hg, "HG308", profilauskleidung_code
            )
            self._setze_text_oder_leer(
                xml_hg, "HG309", innenmaterial_code
            )
            SubElement(xml_hg, "HG310").text = self._formatiere_zahlen_export(
                objekt.get("laenge")
            )
            SubElement(xml_hg, "HG313").text = "B"

            xml_go = SubElement(xml_hg, "GO")
            # Das GO beschreibt die Anschlussleitung als Linie. GO001 verweist
            # auf das reale oder weiter unten erzeugte fiktive Endobjekt.
            SubElement(xml_go, "GO001").text = ziel_id
            SubElement(xml_go, "GO002").text = "H"
            SubElement(xml_go, "GO003").text = "L"

            # Für GO wird die gespeicherte QKan-Punktreihenfolge übernommen.
            # Damit die M150-Forderung "in Fließrichtung" erfüllt ist, muss
            # der QKan-Bestand Anschlussleitungen entsprechend orientiert
            # führen. Die oben erzeugte Arbeitsorientierung dient nur der
            # Ermittlung von Anschluss- und freiem Endpunkt.
            exportpunkte = list(linienpunkte)
            for index, linienpunkt in enumerate(exportpunkte):
                if index == 0:
                    punktkennung = f"{leitnam}-A"
                elif index == len(exportpunkte) - 1:
                    punktkennung = f"{leitnam}-E"
                else:
                    punktkennung = f"{leitnam}-{index}"

                xml_gp = SubElement(xml_go, "GP")
                SubElement(xml_gp, "GP001").text = punktkennung
                SubElement(xml_gp, "GP002").text = "UTM"
                SubElement(xml_gp, "GP005").text = (
                    self._formatiere_zahlen_export(linienpunkt.x())
                )
                SubElement(xml_gp, "GP006").text = (
                    self._formatiere_zahlen_export(linienpunkt.y())
                )
                if index == 0:
                    SubElement(xml_gp, "GP007").text = (
                        self._formatiere_zahl_oder_leer(z_start)
                    )
                elif index == len(exportpunkte) - 1:
                    SubElement(xml_gp, "GP007").text = (
                        self._formatiere_zahl_oder_leer(z_end)
                    )
                else:
                    SubElement(xml_gp, "GP007")
                # Referenztabellen 101/102: G kennzeichnet Lage und Höhe als
                # geschätzt, weil hierfür keine Genauigkeitsattribute aus
                # QKan vorliegen.
                SubElement(xml_gp, "GP008").text = "G"
                SubElement(xml_gp, "GP009").text = "G"
                SubElement(xml_gp, "GP010").text = "mNN"

            if freies_ende_schacht is None:
                if freies_ende_anschlussschacht is not None:
                    anschluss_pk = freies_ende_anschlussschacht.get("pk")
                    export_schluessel = (
                        ("pk", anschluss_pk)
                        if anschluss_pk is not None
                        else ("name", ziel_id)
                    )
                    if export_schluessel not in exportierte_anschlussknoten:
                        self._export_anschlussschacht_kg(
                            xml_wurzel,
                            freies_ende_anschlussschacht,
                            ziel_id,
                            entwart_code,
                            freies_ende,
                            z_end,
                        )
                        exportierte_anschlussknoten.add(export_schluessel)
                else:
                    self._export_anschlusspunkt_kg(
                        xml_wurzel,
                        ziel_id,
                        entwart_code,
                        freies_ende,
                        z_end,
                    )

    def _waehle_speicherort(self) -> None:
        """Öffnet die Dateiauswahl für den XML-Exportpfad."""
        from datetime import datetime

        vorgeschlagener_dateiname = (
            f"m150_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        )
        dateipfad, _ = QFileDialog.getSaveFileName(
            self, "XML speichern", vorgeschlagener_dateiname, "XML (*.xml)"
        )
        if dateipfad:
            if not dateipfad.endswith(".xml"):
                dateipfad += ".xml"
            self.tf_export.setText(dateipfad)

    def _export_xml(self) -> None:
        """Erzeugt die M150-XML aus dem gespeicherten QKan-Datenstand."""
        dateipfad = self.tf_export.text()
        if not dateipfad:
            return

        if not (
            self.ausgewaehlte_haltungen
            or self.ausgewaehlte_schaechte
            or self.ausgewaehlte_anschlussleitungen
        ):
            QMessageBox.warning(
                self,
                "M150-Export",
                "Es sind keine Objekte für den Export ausgewählt.",
            )
            return

        erforderliche_tabellen = {"schaechte"}
        if self.ausgewaehlte_haltungen:
            erforderliche_tabellen.add("haltungen")
        if self.ausgewaehlte_anschlussleitungen:
            erforderliche_tabellen.add("anschlussleitungen")
            erforderliche_tabellen.add("anschlussschaechte")
        if not self._datenquelle_waehlen(erforderliche_tabellen):
            return

        geaenderte_layer = self._ungespeicherte_exportaenderungen()
        if geaenderte_layer:
            QMessageBox.warning(
                self,
                "M150-Export",
                "Der Export verwendet ausschließlich gespeicherte Daten.\n\n"
                "Bitte zuerst diese Layer speichern:\n- "
                + "\n- ".join(geaenderte_layer),
            )
            return

        self._material_ref_m150.clear()
        self._material_codes_m150.clear()
        self._profil_ref_m150.clear()
        self._profil_codes_m150.clear()
        self._profilauskleidung_ref_m150.clear()
        self._knotenart_ref_m150.clear()
        self._entwart_ref_m150.clear()
        self._export_ref_warnungen.clear()

        try:
            with datenbank_oeffnen(self._datenquelle) as db_qkan:
                if not db_qkan.connected:
                    QMessageBox.critical(
                        self,
                        "M150-Export",
                        "Die gewählte QKan-Datenquelle konnte nicht geöffnet "
                        "werden.",
                    )
                    return

                db_qkan.loadmodule("inspektion")

                h_objekte = self._sql_auswahl_zeilen_laden(
                    db_qkan,
                    "inspektion_export_haltungen_auswahl",
                    self.ausgewaehlte_haltungen,
                )
                a_objekte = self._sql_auswahl_zeilen_laden(
                    db_qkan,
                    "inspektion_export_anschlussleitungen_auswahl",
                    self.ausgewaehlte_anschlussleitungen,
                )

                schacht_namen = set(self.ausgewaehlte_schaechte)
                for objekt in h_objekte:
                    if objekt.get("schoben"):
                        schacht_namen.add(str(objekt["schoben"]))
                    if objekt.get("schunten"):
                        schacht_namen.add(str(objekt["schunten"]))
                for objekt in a_objekte:
                    if objekt.get("schoben"):
                        schacht_namen.add(str(objekt["schoben"]))
                    if objekt.get("schunten"):
                        schacht_namen.add(str(objekt["schunten"]))

                s_objekte = self._sql_auswahl_zeilen_laden(
                    db_qkan,
                    "inspektion_export_schaechte_auswahl",
                    schacht_namen,
                )

                # Keine Vorfilterung nach haltnam: Die Geometrie innerhalb
                # von 5 cm ist zwingend. haltnam und urstation dienen nur
                # zur Rangfolge mehrerer geometrischer Treffer.
                as_objekte = self._sql_zeilen_laden(
                    db_qkan,
                    "inspektion_export_anschlussschaechte_haltungen",
                )

                self._referenzen_laden(db_qkan)

                xml_wurzel = Element(
                    "DATA",
                    {
                        "xmlns:xsi": (
                            "http://www.w3.org/2001/XMLSchema-instance"
                        )
                    },
                )
                fd = SubElement(xml_wurzel, "FD")
                # Das QKan-Austauschprofil verwendet eine individuelle
                # Auswahl der M150-Felder und wird deshalb als Typ Z geführt.
                SubElement(fd, "FD001").text = "04-2010"
                SubElement(fd, "FD002").text = "Z"

                self._export_haltungen(
                    xml_wurzel,
                    h_objekte,
                )

                if a_objekte:
                    self._export_anschlussleitungen(
                        xml_wurzel,
                        a_objekte,
                        h_objekte,
                        s_objekte,
                        as_objekte,
                    )

                self._export_schaechte(xml_wurzel, s_objekte)

                indent(xml_wurzel, space="  ")
                xml_daten = tostring(
                    xml_wurzel,
                    encoding="ISO-8859-1",
                    xml_declaration=True,
                    standalone=False,
                )
                if not isinstance(xml_daten, bytes):
                    raise TypeError(
                        "Die XML-Serialisierung lieferte keine Binärdaten."
                    )

                with open(dateipfad, "wb") as datei:
                    datei.write(xml_daten)
        except (
            LookupError,
            OSError,
            QkanDbError,
            RuntimeError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as err:
            QMessageBox.critical(
                self,
                "M150-Export",
                "Der M150-Export konnte nicht vollständig durchgeführt "
                f"werden.\n\n{err}",
            )
            return

        QMessageBox.information(
            self, "M150-Export", "M150-Export erfolgreich abgeschlossen."
        )
        self._auswahl_zuruecksetzen()
        self.tf_export.clear()


def run_m150_export(iface: QgisInterface) -> None:
    """Öffnet den M150-Exportdialog."""
    dlg = BefahrungExportDialog(iface)
    dlg.exec_()
