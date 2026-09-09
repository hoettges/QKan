"""Importiert M150-Stamm-, Zustands- und Schadensdaten nach QKan.

Die für diesen Import wesentliche M150-Hierarchie lautet::

    DATA
    ├── FD                         Formatangaben
    ├── HG                         Haltung/Leitung
    │   ├── GO ── GP              Geometrie und Geometriepunkte
    │   └── HI ── HZ              Inspektion und Zustände
    └── KG                         Knoten
        ├── GO ── GP              Geometrie und Geometriepunkte
        └── KI ── KZ              Inspektion und Zustände

``HI``/``HZ`` und ``KI``/``KZ`` bleiben beim Lesen hierarchisch. Beim
Schreiben nach QKan werden sie auf je einen Gesamtzustands- und einen
Einzelschadens-Layer abgebildet. Feldkennungen wie ``HG313`` oder ``HZ001``
beziehen sich auf DWA-M 150, Ausgabe April 2010. Regeln für die Darstellung
von Schadenslinien und für künstliche BCA-Anschlussstummel sind dagegen
QKan-spezifisch und werden an den betreffenden Stellen ausdrücklich so
gekennzeichnet.
"""

from __future__ import annotations

import logging
import os
import re
from typing import (
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QFile, QIODevice, QXmlStreamReader
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QListWidgetItem,
    QMessageBox,
)

from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPoint,
    QgsPointXY,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
    Qgis,
)

from qgis.gui import QgisInterface

from .datenquelle import (
    Datenquelle,
    datenbank_oeffnen,
    datenquelle_waehlen,
    layer_finden,
)


LOGGER = logging.getLogger(__name__)


ImportZeile = Dict[str, object]
ImportQuelle = Union[QgsFeature, Mapping[str, object]]
ImportZiel = Union[int, QgsFeature]


class XmlElement:
    """Minimales XML-Element für den M150-Import ohne Python-XML-Parser."""

    def __init__(
        self, tag: str, attrib: Optional[Dict[str, str]] = None
    ) -> None:
        """Initialisiert ein internes XML-Element.

        :param tag: Name des XML-Elements.
        :param attrib: Optionale XML-Attribute.
        """
        self.tag = _xml_tagname_sicher(tag)
        self.attrib = attrib or {}
        self.text: Optional[str] = None
        self._children: List["XmlElement"] = []

    def append(self, child: "XmlElement") -> None:
        """Hängt ein Kind an das XML-Element an.

        :param child: Hinzuzufügendes Kind-Element.
        """
        self._children.append(child)

    def find(self, path: str) -> Optional["XmlElement"]:
        """Sucht das erste Kind entlang eines einfachen XML-Pfads.

        :param path: Mit Schrägstrichen getrennter Elementpfad.
        :return: Erstes passendes Element oder ``None``.
        """
        treffer = self.findall(path)
        return treffer[0] if treffer else None

    def findtext(self, path: str, default: object = None) -> object:
        """Liest den Text des ersten Elements entlang eines XML-Pfads.

        :param path: Mit Schrägstrichen getrennter Elementpfad.
        :param default: Rückgabewert, wenn kein Text gefunden wird.
        :return: Elementtext oder der angegebene Standardwert.
        """
        element = self.find(path)
        if element is None or element.text is None:
            return default
        return element.text

    def findall(self, path: str) -> List["XmlElement"]:
        """Sucht alle Elemente entlang eines einfachen XML-Pfads.

        :param path: Mit Schrägstrichen getrennter Elementpfad.
        :return: Liste der passenden Elemente.
        """
        teile = [teil for teil in path.split("/") if teil]
        if not teile:
            return []

        aktuelle_elemente: List["XmlElement"] = [self]
        for teil in teile:
            naechste_elemente: List["XmlElement"] = []
            ziel_tag = _xml_tagname_sicher(teil)
            for element in aktuelle_elemente:
                naechste_elemente.extend(
                    child
                    for child in element._children
                    if child.tag == ziel_tag
                )
            aktuelle_elemente = naechste_elemente

        return aktuelle_elemente


def _xml_tagname_sicher(name: object) -> str:
    """Entfernt Namespace-Anteile aus XML-Tagnamen."""
    text = str(name)
    if "}" in text:
        text = text.split("}", 1)[1]
    if ":" in text:
        text = text.split(":", 1)[1]
    return text


def _qxml_token(name: str) -> object:
    """Liefert QXmlStreamReader-Token kompatibel für Qt5/Qt6."""
    tokentyp = getattr(QXmlStreamReader, "TokenType", None)
    if tokentyp is not None and hasattr(tokentyp, name):
        return getattr(tokentyp, name)
    return getattr(QXmlStreamReader, name, None)


def m150_xml_sicher_lesen(xml_pfad: str) -> XmlElement:
    """Liest eine lokale M150-XML-Datei sicher ein.

    :param xml_pfad: Pfad zur einzulesenden XML-Datei.
    :return: Internes Wurzelelement des M150-Dokuments.
    :raises ValueError: Bei ungültiger Endung, Größe, Struktur, DTD, ENTITY
        oder XML-Syntax.
    """
    if not xml_pfad:
        raise ValueError("Kein XML-Pfad angegeben.")

    if not xml_pfad.lower().endswith(".xml"):
        raise ValueError("Nur XML-Dateien können importiert werden.")

    maximale_groesse = 50 * 1024 * 1024  # 50 MB
    maximale_tiefe = 256

    datei = QFile(xml_pfad)
    if not datei.open(QIODevice.ReadOnly):
        raise ValueError("Die XML-Datei konnte nicht geöffnet werden.")

    elementstapel: List[XmlElement] = []
    xml_wurzel: Optional[XmlElement] = None

    try:
        if datei.size() > maximale_groesse:
            raise ValueError("Die XML-Datei ist zu groß.")

        xml_leser = QXmlStreamReader(datei)
        dtd_token = _qxml_token("DTD")
        entity_token = _qxml_token("EntityReference")

        while not xml_leser.atEnd():
            xml_token = xml_leser.readNext()

            if dtd_token is not None and xml_token == dtd_token:
                raise ValueError(
                    "XML-Dateien mit DTD sind aus Sicherheitsgründen "
                    "nicht erlaubt."
                )

            if entity_token is not None and xml_token == entity_token:
                raise ValueError(
                    "XML-Dateien mit ENTITY sind aus Sicherheitsgründen "
                    "nicht erlaubt."
                )

            if xml_leser.isStartElement():
                if len(elementstapel) >= maximale_tiefe:
                    raise ValueError(
                        "Die XML-Datei ist zu tief verschachtelt."
                    )

                attribute: Dict[str, str] = {}
                for attribut in xml_leser.attributes():
                    attribute[_xml_tagname_sicher(attribut.name())] = str(
                        attribut.value()
                    )

                element = XmlElement(xml_leser.name(), attribute)
                if elementstapel:
                    elementstapel[-1].append(element)
                else:
                    xml_wurzel = element
                elementstapel.append(element)

            elif xml_leser.isEndElement():
                if elementstapel:
                    elementstapel.pop()

            elif xml_leser.isCharacters() and elementstapel:
                text = str(xml_leser.text())
                if text:
                    aktueller_text = elementstapel[-1].text or ""
                    elementstapel[-1].text = aktueller_text + text

        if xml_leser.hasError():
            raise ValueError(
                f"XML konnte nicht gelesen werden: {xml_leser.errorString()}"
            )

    finally:
        datei.close()

    if xml_wurzel is None:
        raise ValueError("Die XML-Datei enthält kein Wurzelelement.")

    if xml_wurzel.tag != "DATA":
        raise ValueError(
            "Die XML-Datei ist keine unterstützte M150-DATA-Datei."
        )

    return xml_wurzel


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "m150_import.ui")
)


class BefahrungImportDialog(QDialog, FORM_CLASS):
    """Dialog für den Import von M150-Stamm- und Inspektionsdaten.

    Der Import verarbeitet die für Format B relevanten Grund-, Geometrie-,
    Inspektions- und Zustandsblöcke und überführt sie in das
    QKan-Datenmodell.
    """

    # Der gerundete Vergleich verhindert reine Serialisierungsänderungen an
    # Geometrien. Die Genauigkeit ist eine QKan-Importentscheidung und keine
    # Vorgabe von DWA-M 150.
    GEOM_VERGLEICH_STELLEN = 3
    ANSCHLUSS_HALTUNG_TOLERANZ_M = 0.25
    ANSCHLUSSSCHACHT_ENDPOINT_TOLERANZ_M = 0.05

    # M150-Schlüsselfelder, deren Bedeutung über eine Referenztabelle
    # bestimmt wird. Die Nummern entsprechen der Spalte "Referenztabelle"
    # im DWA-M-150-Format. KG305/RT116 bleibt von der dynamischen Auflösung
    # bewusst ausgenommen, da Knotenarten separat behandelt werden.
    M150_FELD_REFERENZTABELLEN = {
        "GO002": "300",
        "GO003": "301",
        "GP002": "302",
        "GP008": "101",
        "GP009": "102",
        "GP010": "303",
        "HG006": "128",
        "HG010": "116",
        "HG301": "103",
        "HG302": "104",
        "HG304": "105",
        "HG305": "106",
        "HG308": "107",
        "HG309": "105",
        "HG313": "108",
        "KG302": "104",
        "KG304": "105",
        "KG401": "109",
        "HI004": "201",
        "HI005": "202",
        "HI103": "203",
        "HI106": "204",
        "HI107": "205",
        "HI109": "206",
        "HI114": "207",
        "HI117": "208",
        "KI004": "201",
        "KI005": "202",
        "KI103": "203",
        "KI106": "204",
        "KI107": "205",
        "KI109": "206",
        "KI114": "207",
        "KI117": "208",
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

    # Fachliche Schlüssel für einen wiederholbaren Import. M150 besitzt für
    # HZ/KZ keinen eigenen technischen Primärschlüssel; Einzelschäden werden
    # deshalb zusätzlich über ihre Reihenfolge (``id``) innerhalb der
    # Inspektionsdaten identifiziert.
    IMPORT_INDEXE = {
        "schaechte": (
            "inspektion_import_index_schaechte",
            ("schnam",),
        ),
        "haltungen": (
            "inspektion_import_index_haltungen",
            ("haltnam",),
        ),
        "anschlussleitungen": (
            "inspektion_import_index_anschlussleitungen",
            ("leitnam",),
        ),
        "schaechte_untersucht": (
            "inspektion_import_index_schaechte_untersucht",
            ("schnam", "untersuchtag"),
        ),
        "untersuchdat_schacht": (
            "inspektion_import_index_untersuchdat_schacht",
            ("untersuchsch", "untersuchtag", "id"),
        ),
        "haltungen_untersucht": (
            "inspektion_import_index_haltungen_untersucht",
            ("haltnam", "untersuchtag"),
        ),
        "untersuchdat_haltung": (
            "inspektion_import_index_untersuchdat_haltung",
            ("untersuchhal", "untersuchtag", "id"),
        ),
        "anschlussleitungen_untersucht": (
            "inspektion_import_index_anschlussleitungen_untersucht",
            ("leitnam", "untersuchtag"),
        ),
        "untersuchdat_anschlussleitung": (
            "inspektion_import_index_untersuchdat_anschlussleitung",
            ("untersuchleit", "untersuchtag", "id"),
        ),
    }

    IMPORT_TABELLEN = {
        "haltungen",
        "schaechte",
        "anschlussleitungen",
        "anschlussschaechte",
        "schaechte_untersucht",
        "untersuchdat_schacht",
        "haltungen_untersucht",
        "untersuchdat_haltung",
        "anschlussleitungen_untersucht",
        "untersuchdat_anschlussleitung",
    }

    def __init__(self, iface: QgisInterface) -> None:
        """Richtet den Importdialog ein, verbindet Dateiauswahl und Import."""
        super().__init__(iface.mainWindow())
        self.iface = iface

        self._material_ref_m150: Dict[str, str] = {}
        self._material_codes_m150: set[str] = set()
        self._profil_ref_m150: Dict[str, str] = {}
        self._profil_basis_ref_m150: Dict[str, str] = {}
        self._profilauskleidung_ref_m150: Dict[str, str] = {}
        self._knotenart_ref_m150: Dict[str, Dict[str, str]] = {}
        self._entwart_basis_ref_m150: Dict[str, str] = {}
        self._entwart_langtext_ref_m150: Dict[str, str] = {}
        self._xml_rt_ref_m150: Dict[str, Dict[str, str]] = {}
        self._import_objekte: Dict[
            str, Dict[Tuple[str, ...], ImportZiel]
        ] = {}
        self._datenquelle: Optional[Datenquelle] = None

        self.setupUi(self)

        self.pb_import.clicked.connect(self._datei_waehlen)
        self.import_2.clicked.connect(self._xml_import)
        self.logbuch.setFont(QFont("Arial", 10))

    # Benutzeroberfläche und Protokoll
    def _log_hinzufuegen(self, textwert: str) -> None:
        """Schreibt dieselbe Meldung ins UI und in die Projekt-Logdatei."""
        eintrag = QListWidgetItem(textwert)
        self.logbuch.addItem(eintrag)
        self.logbuch.scrollToBottom()

        projektdatei = QgsProject.instance().fileName()
        if not projektdatei:
            return

        log_pfad = os.path.join(
            os.path.dirname(projektdatei),
            "M150_Import_Log.txt",
        )
        try:
            with open(log_pfad, "a", encoding="utf-8") as log_datei:
                log_datei.write(str(textwert) + "\n")
        except OSError:
            # Das UI-Log darf durch einen Dateifehler nicht verändert werden.
            LOGGER.warning(
                "M150-Import-Logdatei konnte nicht geschrieben werden: %s",
                log_pfad,
                exc_info=True,
            )

    def _datei_waehlen(self) -> None:
        """Öffnet die Dateiauswahl für die zu importierende XML-Datei."""
        dateipfad, _ = QFileDialog.getOpenFileName(
            self, "XML auswählen", "", "XML (*.xml)"
        )
        if dateipfad:
            self.tf_import.setText(dateipfad)

    # Hilfsfunktionen
    def _nullify(self, wert: object) -> object:
        """Wandelt None, Leerstrings und den Text NULL in None um."""
        if wert is None:
            return None
        if isinstance(wert, str):
            textwert = wert.strip()
            if textwert == "" or textwert.upper() == "NULL":
                return None
            return textwert
        return wert

    def _zahl_lesen(self, wert: object) -> Optional[float]:
        """Konvertiert Zahlen und Dezimaltexte mit Punkt oder Komma; ungültige
        Werte ergeben None.
        """
        wert = self._nullify(wert)
        if wert is None:
            return None

        if isinstance(wert, (int, float)):
            return float(wert)

        textwert = str(wert).strip().replace(",", ".")
        if not re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)", textwert):
            return None

        return float(textwert)

    def _zahl_ohne_null(self, wert: object) -> Optional[float]:
        """Konvertiert einen Zahlenwert und behandelt Beträge unter 0,000001
        als fehlende Angabe.
        """
        zahl = self._zahl_lesen(wert)
        if zahl is None:
            return None
        if abs(zahl) < 0.000001:
            return None
        return zahl

    def _ganzzahl_lesen(self, wert: object) -> Optional[int]:
        """Konvertiert einen gültigen Zahlenwert mit int() in eine Ganzzahl."""
        zahl = self._zahl_lesen(wert)
        if zahl is None:
            return None
        return int(zahl)

    def _ganzzahl_ohne_null(self, wert: object) -> Optional[int]:
        """Liest eine Ganzzahl und behandelt 0 als fehlende Angabe."""
        zahl = self._zahl_ohne_null(wert)
        if zahl is None:
            return None
        return int(zahl)

    def _als_text(self, wert: object) -> str:
        """Gibt den bereinigten Wert als Text zurück; fehlende Werte ergeben
        einen Leerstring.
        """
        wert = self._nullify(wert)
        return "" if wert is None else str(wert)

    def _kommentar_anhaengen(
        self, alter_wert: object, neuer_wert: object
    ) -> object:
        """Hängt eine neue Kommentarzeile an, sofern sie nicht leer oder
        bereits vorhanden ist.
        """
        alt = self._als_text(alter_wert).strip()
        neu = self._als_text(neuer_wert).strip()

        if not neu:
            return alter_wert
        if not alt:
            return neu

        vorhandene_zeilen = {zeile.strip() for zeile in alt.splitlines()}
        if neu in vorhandene_zeilen:
            return alt

        return alt + "\n" + neu

    def _normalisiere_refwert(self, wert: object) -> str:
        """Normalisiert Referenzwerte für den Vergleich mit YAML-Daten."""
        return "".join(
            zeichen
            for zeichen in self._als_text(wert).upper()
            if zeichen.isalnum()
        )

    def _entwart_basis_lesen(self, wert: object) -> Optional[str]:
        """Ermittelt den Basiscode über die Abfragen der Datenquelle."""
        vergleichswert = self._normalisiere_refwert(wert)
        if not vergleichswert:
            return None
        return self._entwart_basis_ref_m150.get(vergleichswert)

    def _entwart_langtext_aus_basis(
        self, basis: Optional[str]
    ) -> Optional[str]:
        """Liest den QKan-Langtext aus den Referenzabfragen."""
        if not basis:
            return None
        return self._entwart_langtext_ref_m150.get(
            self._als_text(basis).upper()
        )

    def _m150_kanalart_zu_qkan(
        self, xml_wert: object, aktueller_wert: object
    ) -> object:
        """Überführt HG301 in das QKan-Feld ``abflussart``.

        Reihenfolge: externe RT103, bestehende QKan-Zuordnung,
        DWA-Standard, schließlich Rohwert mit Warnung.
        """
        xml_langtext = self._xml_rt_langtext_lesen("103", xml_wert)
        if xml_langtext is not None:
            if (
                self._vergleichstext(aktueller_wert)
                == self._vergleichstext(xml_langtext)
                and self._nullify(aktueller_wert) is not None
            ):
                return aktueller_wert
            return xml_langtext

        zielwerte = {
            "K": "Freispiegel",
            "D": "Druckleitung",
            "F": "Offene Freispiegelleitung (Gerinne)",
            "G": "Dränageleitung",
        }

        def basis(wert: object) -> Optional[str]:
            text = self._normalisiere_refwert(wert)
            if text in {"K", "FREISPIEGEL", "GESCHLOSSENEFREISPIEGELLEITUNG"}:
                return "K"
            if text in {"D", "DRUCKLEITUNG", "DRUCKROHRLEITUNG"}:
                return "D"
            if text in {"F", "OFFENEFREISPIEGELLEITUNGGERINNE", "OFFENEFREISPIEGELLEITUNG"}:
                return "F"
            if text in {"G", "DRÄNAGELEITUNG", "DRAENAGELEITUNG"}:
                return "G"
            return None

        neu = basis(xml_wert)
        if neu is not None:
            alt = basis(aktueller_wert)
            if alt == neu and self._nullify(aktueller_wert) is not None:
                return aktueller_wert
            return zielwerte[neu]

        standard = self._standard_rt_langtext_lesen("103", xml_wert)
        if standard is not None:
            return standard

        rohwert = self._als_text(xml_wert)
        if rohwert:
            self._log_hinzufuegen(
                f"⚠ Kanalart-Code '{rohwert}' konnte nicht zugeordnet "
                "werden – Rohwert wird übernommen"
            )
            return rohwert
        return aktueller_wert

    def _m150_entwart_zu_qkan(
        self, xml_wert: object, aktueller_wert: object
    ) -> object:
        """Überführt eine M150-Kanalnutzung in den passenden QKan-Wert.

        Reihenfolge: externe RT104, bestehende QKan/YAML-Zuordnung,
        DWA-Standard, schließlich Rohwert mit Warnung.
        """
        xml_langtext = self._xml_rt_langtext_lesen("104", xml_wert)
        if xml_langtext is not None:
            if (
                self._vergleichstext(aktueller_wert)
                == self._vergleichstext(xml_langtext)
                and self._nullify(aktueller_wert) is not None
            ):
                return aktueller_wert
            return xml_langtext

        neuer_basis = self._entwart_basis_lesen(xml_wert)
        if neuer_basis is not None:
            aktueller_basis = self._entwart_basis_lesen(aktueller_wert)
            if (
                aktueller_basis == neuer_basis
                and self._nullify(aktueller_wert) is not None
            ):
                return aktueller_wert

            zielwert = self._entwart_langtext_aus_basis(neuer_basis)
            if zielwert is not None:
                return zielwert

        standard = self._standard_rt_langtext_lesen("104", xml_wert)
        if standard is not None:
            return standard

        rohwert = self._als_text(xml_wert)
        if rohwert:
            self._log_hinzufuegen(
                f"⚠ Kanalnutzung-Code '{rohwert}' konnte nicht zugeordnet "
                "werden – Rohwert wird übernommen"
            )
            return rohwert
        return aktueller_wert

    def _layer_holen(self, tabellenname: str) -> Optional[QgsVectorLayer]:
        """Liefert nur den Layer aus der gewählten QKan-Datenquelle."""
        if self._datenquelle is None:
            return None
        return layer_finden(
            QgsProject.instance(),
            tabellenname,
            self._datenquelle,
        )

    def _sql_zeilen_laden(
        self, db_qkan: object, sqlnam: str
    ) -> List[ImportZeile]:
        """Lädt eine benannte Datenbankabfrage als Wörterbuchzeilen."""
        if not db_qkan.sqlyml(
            sqlnam,
            stmt_category=f"Inspektion: {sqlnam}",
        ):
            raise RuntimeError(
                f"Die YAML-Abfrage '{sqlnam}' konnte nicht ausgeführt "
                "werden."
            )

        beschreibung = db_qkan.cursl.description or ()
        spalten = [eintrag[0] for eintrag in beschreibung]
        return [
            dict(zip(spalten, zeile))
            for zeile in db_qkan.fetchall()
        ]

    def _wert_aus_quelle(
        self, quelle: ImportQuelle, feld: str
    ) -> object:
        """Liest einen Feldwert aus einem Wörterbuch oder QgsFeature."""
        if isinstance(quelle, dict):
            return quelle.get(feld)
        try:
            return quelle[feld]
        except (KeyError, TypeError):
            return None

    def _import_schluessel(
        self,
        schluesselfelder: Tuple[str, ...],
        quelle: ImportQuelle,
    ) -> Tuple[str, ...]:
        """Erzeugt einen stabilen Schlüssel für Importziele."""
        return tuple(
            self._als_text(self._wert_aus_quelle(quelle, feld))
            for feld in schluesselfelder
        )

    def _import_indexe_laden(self, db_qkan: object) -> None:
        """Lädt gespeicherte Importziele als schlanke YAML-Indizes."""
        self._import_objekte = {}
        for tabelle, (sqlnam, schluesselfelder) in self.IMPORT_INDEXE.items():
            objektindex: Dict[Tuple[str, ...], ImportZiel] = {}
            for daten in self._sql_zeilen_laden(db_qkan, sqlnam):
                pk = daten.get("pk")
                if pk is None:
                    continue
                schluessel = self._import_schluessel(
                    schluesselfelder, daten
                )
                objektindex.setdefault(schluessel, int(pk))
            self._import_objekte[tabelle] = objektindex

    def _import_editpuffer_uebernehmen(
        self,
        tabelle: str,
        layer: Optional[QgsVectorLayer],
    ) -> None:
        """Ersetzt einen YAML-Index durch den aktuellen QGIS-Editierstand."""
        if layer is None or not layer.isModified():
            return

        _sqlnam, schluesselfelder = self.IMPORT_INDEXE[tabelle]
        self._import_objekte[tabelle] = {
            self._import_schluessel(schluesselfelder, objekt): objekt
            for objekt in layer.getFeatures()
        }

    def _objekt_nach_pk_laden(
        self,
        layer: QgsVectorLayer,
        pk: int,
    ) -> Optional[QgsFeature]:
        """Holt genau das über YAML gefundene Objekt aus dem QGIS-Layer."""
        abfrage = QgsFeatureRequest().setFilterExpression(
            f'"pk" = {int(pk)}'
        )
        for objekt in layer.getFeatures(abfrage):
            return objekt
        return None

    def _import_objekt_finden(
        self,
        tabelle: str,
        layer: Optional[QgsVectorLayer],
        schluesselfelder: Tuple[str, ...],
        quelle: ImportQuelle,
    ) -> Optional[QgsFeature]:
        """Sucht ein Importziel im vorgeladenen Index.

        :param tabelle: Logischer Tabellenname des Importindexes.
        :param layer: Ziel-Layer in QGIS.
        :param schluesselfelder: Felder des eindeutigen Importsschlüssels.
        :param quelle: Quelldaten, aus denen der Schlüssel gebildet wird.
        :return: Gefundenes Feature oder ``None``.
        :raises RuntimeError: Wenn der Index auf ein fehlendes Feature
            verweist.
        """
        if layer is None:
            return None

        schluessel = self._import_schluessel(schluesselfelder, quelle)
        treffer = self._import_objekte.get(tabelle, {}).get(schluessel)
        if treffer is None:
            return None
        if isinstance(treffer, QgsFeature):
            return treffer

        objekt = self._objekt_nach_pk_laden(layer, int(treffer))
        if objekt is None:
            raise RuntimeError(
                f"YAML-Index verweist auf fehlendes Objekt in "
                f"'{layer.name()}': pk={treffer}."
            )

        self._import_objekte.setdefault(tabelle, {})[schluessel] = objekt
        return objekt

    def _import_objekt_registrieren(
        self,
        tabelle: str,
        schluesselfelder: Tuple[str, ...],
        quelle: ImportQuelle,
        objekt: QgsFeature,
    ) -> None:
        """Registriert ein neu angelegtes Objekt im Importindex.

        :param tabelle: Logischer Tabellenname des Importindexes.
        :param schluesselfelder: Felder des eindeutigen Importsschlüssels.
        :param quelle: Quelldaten, aus denen der Schlüssel gebildet wird.
        :param objekt: Neu angelegtes QGIS-Feature.
        """
        schluessel = self._import_schluessel(schluesselfelder, quelle)
        self._import_objekte.setdefault(tabelle, {})[schluessel] = objekt

    def _yaml_importdaten_laden(self, db_qkan: object) -> None:
        """Lädt Importreferenzen und Existenzindizes aus YAML-Abfragen."""
        material_zeilen = self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_material_m150"
        )
        self._material_ref_m150 = {}
        self._material_codes_m150 = set()
        for zeile in material_zeilen:
            code = self._als_text(zeile.get("m150_code")).upper()
            if not code:
                continue
            self._material_codes_m150.add(code)
            if zeile.get("quelle") != "tabelle":
                continue
            bezeichnung = self._als_text(zeile.get("bezeichnung"))
            if bezeichnung:
                self._material_ref_m150.setdefault(code, bezeichnung)

        profil_zeilen = self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_profile_m150"
        )
        self._profil_ref_m150 = {}
        self._profil_basis_ref_m150 = {}
        for zeile in profil_zeilen:
            code = self._als_text(zeile.get("m150_code")).upper()
            profilnam = self._als_text(zeile.get("profilnam"))
            if not code:
                continue
            self._profil_basis_ref_m150.setdefault(
                self._normalisiere_refwert(code), code
            )
            if profilnam:
                self._profil_ref_m150.setdefault(code, profilnam)
                self._profil_basis_ref_m150.setdefault(
                    self._normalisiere_refwert(profilnam), code
                )

        self._profilauskleidung_ref_m150 = {}
        for zeile in self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_profilauskleidung_m150"
        ):
            code = self._als_text(zeile.get("m150_code")).upper()
            bezeichnung = self._als_text(zeile.get("bezeichnung"))
            if code and bezeichnung:
                self._profilauskleidung_ref_m150.setdefault(
                    code, bezeichnung
                )

        self._knotenart_ref_m150 = {}
        for zeile in self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_knotenart_m150"
        ):
            code = self._als_text(zeile.get("m150_code")).upper()
            schachttyp = self._als_text(zeile.get("schachttyp"))
            knotentyp = self._als_text(zeile.get("knotentyp"))
            if code and schachttyp and knotentyp:
                self._knotenart_ref_m150.setdefault(
                    code,
                    {
                        "schachttyp": schachttyp,
                        "knotentyp": knotentyp,
                    },
                )

        entwart_zeilen = self._sql_zeilen_laden(
            db_qkan, "inspektion_ref_entwaesserungsarten_m150"
        )
        self._entwart_basis_ref_m150 = {}
        self._entwart_langtext_ref_m150 = {}
        for zeile in entwart_zeilen:
            vergleichswert = self._normalisiere_refwert(
                zeile.get("vergleichswert")
            )
            code = self._als_text(zeile.get("m150_code")).upper()
            langtext = self._als_text(zeile.get("langtext"))
            if vergleichswert and code:
                self._entwart_basis_ref_m150[vergleichswert] = code
            if code and langtext:
                self._entwart_langtext_ref_m150.setdefault(code, langtext)

        self._import_indexe_laden(db_qkan)

    def _xml_referenztabellen_laden(self, xml_root: XmlElement) -> None:
        """Liest die mit der M150-XML übergebenen RT-Blöcke ein.

        RT001 bezeichnet die Referenztabelle, RT002 den Schlüssel und RT004
        den zu verwendenden Langtext. Nur vollständig gefüllte Einträge
        werden übernommen.
        """
        self._xml_rt_ref_m150 = {}
        anzahl_eintraege = 0

        for rt in xml_root.findall("RT"):
            tabelle = self._als_text(rt.findtext("RT001"))
            schluessel = self._als_text(rt.findtext("RT002"))
            langtext = self._als_text(rt.findtext("RT004"))
            if not tabelle or not schluessel or not langtext:
                continue

            tabelle = tabelle.zfill(3)
            schluessel_norm = schluessel.upper()
            tabelle_werte = self._xml_rt_ref_m150.setdefault(tabelle, {})
            vorhandener_wert = tabelle_werte.get(schluessel_norm)
            if vorhandener_wert is not None:
                if vorhandener_wert != langtext:
                    self._log_hinzufuegen(
                        f"⚠ RT {tabelle}, Schlüssel '{schluessel}': "
                        "mehrere Langtexte vorhanden – erster Wert wird "
                        "verwendet"
                    )
                continue

            tabelle_werte[schluessel_norm] = langtext
            anzahl_eintraege += 1

        # Externe Materialcodes werden beim Vergleich genauso als Codes
        # erkannt wie die über YAML geladenen Standardcodes.
        self._material_codes_m150.update(
            self._xml_rt_ref_m150.get("105", {}).keys()
        )
        for code, langtext in self._xml_rt_ref_m150.get("106", {}).items():
            self._profil_basis_ref_m150[
                self._normalisiere_refwert(code)
            ] = code
            self._profil_basis_ref_m150[
                self._normalisiere_refwert(langtext)
            ] = code

        if anzahl_eintraege:
            self._log_hinzufuegen(
                "XML-Referenztabellen eingelesen: "
                f"{len(self._xml_rt_ref_m150)} Tabelle(n), "
                f"{anzahl_eintraege} Eintrag/Einträge"
            )

    def _xml_rt_langtext_lesen(
        self, referenztabelle: str, schluessel: object
    ) -> Optional[str]:
        """Liefert RT004 für Tabelle und Schlüssel aus der Import-XML."""
        code = self._als_text(schluessel).upper()
        if not code:
            return None
        return self._xml_rt_ref_m150.get(
            self._als_text(referenztabelle).zfill(3), {}
        ).get(code)

    def _xml_rt_langtext_fuer_feld(
        self, feld: str, schluessel: object
    ) -> Optional[str]:
        """Löst ein M150-Feld über seine fest zugehörige RT-Tabelle auf."""
        referenztabelle = self.M150_FELD_REFERENZTABELLEN.get(feld)
        if referenztabelle is None:
            return None
        return self._xml_rt_langtext_lesen(referenztabelle, schluessel)

    def _standard_rt_langtext_lesen(
        self, referenztabelle: str, schluessel: object
    ) -> Optional[str]:
        """Liest den DWA-Standardlangtext eines bekannten RT-Schlüssels."""
        code = self._als_text(schluessel).upper()
        if not code:
            return None
        return self.M150_STANDARD_RT.get(
            self._als_text(referenztabelle).zfill(3), {}
        ).get(code)

    def _referenz_langtext_fuer_feld(
        self, feld: str, schluessel: object
    ) -> Optional[str]:
        """Löst zuerst eine externe XML-RT und danach den DWA-Standard auf."""
        xml_langtext = self._xml_rt_langtext_fuer_feld(feld, schluessel)
        if xml_langtext is not None:
            return xml_langtext
        referenztabelle = self.M150_FELD_REFERENZTABELLEN.get(feld)
        if referenztabelle is None:
            return None
        return self._standard_rt_langtext_lesen(
            referenztabelle, schluessel
        )

    def _vergleichstext(self, wert: object) -> str:
        """Normalisiert einen Wert für fachliche Textvergleiche."""
        return re.sub(r"\s+", " ", self._als_text(wert).strip()).upper()

    def _materialtext_ohne_m150_code(self, wert: object) -> str:
        """Entfernt ein vorhandenes M150-Codepräfix aus Materialtexten."""
        text = re.sub(r"\s+", " ", self._als_text(wert).strip())
        if not text:
            return ""

        teile = text.split(" ", 1)
        if (
            len(teile) == 2
            and teile[0].upper() in self._material_codes_m150
        ):
            text = teile[1].strip()

        return self._vergleichstext(text)

    def _materialwerte_gleichwertig(
        self, alter_wert: object, neuer_wert: object
    ) -> bool:
        """Vergleicht Materialwerte unabhängig vom M150-Codepräfix."""
        alt = self._materialtext_ohne_m150_code(alter_wert)
        neu = self._materialtext_ohne_m150_code(neuer_wert)
        return bool(alt and neu and alt == neu)

    def _materialwert_mit_code(
        self, code: object, materialwert: object
    ) -> object:
        """Ergänzt ein M150-Codepräfix vor einer Materialbezeichnung."""
        code_text = self._als_text(code).upper()
        wert_text = self._als_text(materialwert)
        if not code_text or not wert_text:
            return materialwert
        if wert_text.upper() == code_text:
            return wert_text
        if wert_text.upper().startswith(code_text + " "):
            return wert_text
        return f"{code_text} {wert_text}"

    def _material_aus_m150_lesen(
        self, code: object, bezeichnung: str
    ) -> object:
        """Löst M150-Materialcodes über YAML-Abfragen auf."""
        code_text = self._als_text(code).upper()
        if not code_text:
            return None

        xml_langtext = self._xml_rt_langtext_lesen("105", code_text)
        if xml_langtext is not None:
            return xml_langtext

        zielwert = self._material_ref_m150.get(code_text)
        if zielwert is not None:
            return self._materialwert_mit_code(code_text, zielwert)

        standard = self._standard_rt_langtext_lesen("105", code_text)
        if standard is not None:
            return standard

        self._log_hinzufuegen(
            f"⚠ {bezeichnung}-Code '{code_text}' konnte nicht "
            "zugeordnet werden – Rohwert wird übernommen"
        )
        return self._als_text(code)

    def _profil_aus_m150_lesen(self, code: object) -> Optional[str]:
        """Löst einen M150-Profilcode über XML-RT oder YAML auf."""
        code_text = self._als_text(code).upper()
        if not code_text:
            return None
        xml_langtext = self._xml_rt_langtext_lesen("106", code_text)
        if xml_langtext is not None:
            return xml_langtext
        wert = self._profil_ref_m150.get(code_text)
        if wert is not None:
            return wert

        # Neben dem RT106-Schlüssel werden bekannte Langtexte/Aliase wie
        # "Kreisquerschnitt" akzeptiert. Sie sind fachlich derselbe
        # Profiltyp und dürfen nicht als unbekannter Rohwert geloggt werden.
        basis = self._profil_basis_lesen(code)
        if basis is not None:
            return self._als_text(code)

        standard = self._standard_rt_langtext_lesen("106", code_text)
        if standard is not None:
            return standard

        self._log_hinzufuegen(
            f"⚠ Profil-Code '{code_text}' konnte nicht zugeordnet werden – "
            "Rohwert wird übernommen"
        )
        return self._als_text(code)

    def _profil_basis_lesen(self, wert: object) -> Optional[str]:
        """Liest den M150-Basiscode eines Profilnamens aus YAML-Abfragen."""
        vergleichswert = self._normalisiere_refwert(wert)
        if not vergleichswert:
            return None
        return self._profil_basis_ref_m150.get(vergleichswert)

    def _profilwerte_gleichwertig(
        self, alter_wert: object, neuer_wert: object
    ) -> bool:
        """Vergleicht Profilnamen anhand ihres gemeinsamen M150-Codes."""
        alter_basis = self._profil_basis_lesen(alter_wert)
        neuer_basis = self._profil_basis_lesen(neuer_wert)
        return bool(
            alter_basis
            and neuer_basis
            and alter_basis == neuer_basis
        )

    def _profilauskleidung_aus_m150_lesen(
        self, code: object
    ) -> Optional[str]:
        """Löst einen M150-Auskleidungscode über XML-RT oder YAML auf."""
        code_text = self._als_text(code).upper()
        if not code_text:
            return None
        xml_langtext = self._xml_rt_langtext_lesen("107", code_text)
        if xml_langtext is not None:
            return xml_langtext
        wert = self._profilauskleidung_ref_m150.get(code_text)
        if wert is not None:
            return wert

        standard = self._standard_rt_langtext_lesen("107", code_text)
        if standard is not None:
            return standard

        self._log_hinzufuegen(
            f"⚠ Profilauskleidung-Code '{code_text}' konnte nicht "
            "zugeordnet werden – Rohwert wird übernommen"
        )
        return self._als_text(code)

    def _knotenart_aus_m150_lesen(
        self, code: object
    ) -> Optional[Dict[str, str]]:
        """Löst die M150-Knotenart über XML-RT, YAML und Standardwerte auf."""
        code_roh = self._als_text(code).strip()
        code_text = code_roh.upper()
        if not code_text:
            return None

        zuordnung = self._knotenart_ref_m150.get(code_text)
        if zuordnung is not None:
            ergebnis = dict(zuordnung)
            xml_langtext = self._xml_rt_langtext_lesen("116", code_text)
            if xml_langtext is not None:
                ergebnis["knotentyp"] = xml_langtext
            return ergebnis

        vergleichswert = self._normalisiere_refwert(code_roh)
        for standard_code, langtext in self.M150_STANDARD_RT.get(
            "116", {}
        ).items():
            if self._normalisiere_refwert(langtext) != vergleichswert:
                continue
            standard_zuordnung = self._knotenart_ref_m150.get(standard_code)
            if standard_zuordnung is not None:
                return dict(standard_zuordnung)

        xml_langtext = self._xml_rt_langtext_lesen("116", code_text)
        if xml_langtext is not None:
            return {"schachttyp": "Symbol", "knotentyp": xml_langtext}

        self._log_hinzufuegen(
            f"⚠ Knotenart-Code '{code_roh}' konnte nicht zugeordnet "
            "werden – Rohwert wird übernommen"
        )
        return {"schachttyp": "Symbol", "knotentyp": code_roh}

    def _feldnamen_lesen(self, layer: Optional[QgsVectorLayer]) -> List[str]:
        """Gibt die Feldnamen des Layers oder bei fehlendem Layer eine leere
        Liste zurück.
        """
        return [feld.name() for feld in layer.fields()] if layer else []

    def _bearbeitung_starten(self, layer: Optional[QgsVectorLayer]) -> None:
        """Startet den Bearbeitungsmodus, wenn der Layer vorhanden und noch
        nicht editierbar ist.
        """
        if layer and not layer.isEditable():
            layer.startEditing()

    def _layer_speichern(self, layer: Optional[QgsVectorLayer]) -> None:
        """Speichert einen editierbaren Layer und löst bei einem
        fehlgeschlagenen Commit einen RuntimeError aus.
        """
        if not layer:
            return
        if layer.isEditable():
            if not layer.commitChanges():
                fehler = (
                    "; ".join(layer.commitErrors())
                    if hasattr(layer, "commitErrors")
                    else "unbekannter Fehler"
                )
                raise RuntimeError(
                    f"Fehler beim Speichern von Layer '{layer.name()}': "
                    f"{fehler}"
                )

    def _attribut_sicher_aendern(
        self,
        objekt: QgsFeature,
        feld: str,
        neuer_wert: object,
        aenderungen: List[str],
    ) -> None:
        """Übernimmt einen fachlich zulässigen Attributwert.

        Fehlende M150-Werte löschen keine vorhandenen Bestandsinformationen.
        Referenzwerte werden vor dem Vergleich auf ihre fachliche Bedeutung
        normalisiert, damit Kürzel und QKan-Langtext nicht als Änderung
        gelten.

        :param objekt: Zu änderndes QGIS-Feature.
        :param feld: Name des Zielfelds.
        :param neuer_wert: Aus der XML gelesener Wert.
        :param aenderungen: Liste für die protokollierten Änderungen.
        """
        if feld not in objekt.fields().names():
            return

        alter_wert = self._nullify(objekt[feld])
        neuer_wert = self._nullify(neuer_wert)

        # Leere optionale XML-Felder bedeuten "keine Angabe". Sie dürfen bei
        # einer Aktualisierung keinen bereits gepflegten QKan-Wert entfernen.
        if neuer_wert is None:
            return

        if feld == "kommentar":
            neuer_wert = self._kommentar_anhaengen(alter_wert, neuer_wert)
            if self._als_text(alter_wert) == self._als_text(neuer_wert):
                return

        if feld == "entwart":
            # Bekannte QKan-/M150-Werte werden wie bisher fachlich verglichen.
            # Ein bereits aufgelöster externer/standardisierter Langtext oder
            # ein unbekannter Rohwert darf dagegen nicht verworfen werden.
            neuer_basis = self._entwart_basis_lesen(neuer_wert)
            if neuer_basis is not None:
                alter_basis = self._entwart_basis_lesen(alter_wert)
                if alter_basis == neuer_basis and alter_wert is not None:
                    return
                zielwert = self._entwart_langtext_aus_basis(neuer_basis)
                if zielwert is not None:
                    neuer_wert = zielwert

        if feld == "abflussart":
            neuer_wert = self._m150_kanalart_zu_qkan(neuer_wert, alter_wert)
            if self._nullify(neuer_wert) is None:
                return
            if self._als_text(neuer_wert) == self._als_text(alter_wert):
                return

        if feld in ("material", "innenmaterial") and alter_wert is not None:
            if self._materialwerte_gleichwertig(alter_wert, neuer_wert):
                return

        if feld == "profilnam" and alter_wert is not None:
            if self._profilwerte_gleichwertig(alter_wert, neuer_wert):
                return

        if feld in ("schachttyp", "knotentyp") and alter_wert is not None:
            # Ein vorhandener QKan-Knotentyp ist oft detaillierter als KG305
            # und wird daher durch den allgemeineren M150-Code nicht ersetzt.
            return

        if feld in ("sohleoben", "sohleunten", "sohlhoehe", "baujahr"):
            # Manche Austauschdateien verwenden 0 als Platzhalter für eine
            # fehlende Höhe. Diese Kompatibilitätsregel ist QKan-spezifisch.
            zahl = self._zahl_lesen(neuer_wert)
            if zahl is not None and abs(zahl) < 0.000001:
                return

        if feld == "laenge":
            # Millimeterdifferenzen entstehen häufig nur durch
            # unterschiedliche Rundung der Geometrie- und Attributlänge.
            alte_zahl = self._zahl_lesen(alter_wert)
            neue_zahl = self._zahl_lesen(neuer_wert)
            if alte_zahl is not None and neue_zahl is not None:
                if abs(alte_zahl - neue_zahl) <= 0.005:
                    return

        if feld == "urstation":
            # Stationen werden in M150 und QKan unterschiedlich gerundet; erst
            # Abweichungen über einem Zentimeter gelten als echte Änderung.
            alte_zahl = self._zahl_lesen(alter_wert)
            neue_zahl = self._zahl_lesen(neuer_wert)
            if alte_zahl is not None and neue_zahl is not None:
                if abs(alte_zahl - neue_zahl) <= 0.01:
                    return

        alter_vergleich = "" if alter_wert is None else str(alter_wert)
        neuer_vergleich = str(neuer_wert)

        if alter_vergleich != neuer_vergleich:
            objekt[feld] = neuer_wert
            aenderungen.append(
                f"{feld}: {alter_vergleich} -> {neuer_vergleich}"
            )

    def _punkt_aus_gp_lesen(self, gp: XmlElement) -> Optional[QgsPointXY]:
        """Liest die Koordinaten aus einem M150-GP-Block.

        GP005/GP006 sind Ost-/Nordkoordinate. Ältere oder anders konfigurierte
        Exporte können stattdessen GP003/GP004 (Rechts-/Hochwert) befüllen;
        diese werden deshalb als kompatibler Rückfall akzeptiert.
        """
        x = self._zahl_lesen(gp.findtext("GP005"))
        y = self._zahl_lesen(gp.findtext("GP006"))
        if x is None or y is None:
            x = self._zahl_lesen(gp.findtext("GP003"))
            y = self._zahl_lesen(gp.findtext("GP004"))
        if x is None or y is None:
            return None
        return QgsPointXY(x, y)

    def _linienpunkte_aus_go_lesen(
        self, block: XmlElement
    ) -> List[QgsPointXY]:
        """Liest alle gültigen GP-Koordinaten eines GO-Blocks in ihrer
        XML-Reihenfolge.

        DWA-M 150 fordert Linien von Haltungen und Leitungen in Fließrichtung.
        Der Import übernimmt diese Reihenfolge unverändert und korrigiert sie
        nicht anhand der Höhen.
        """
        linienpunkte: List[QgsPointXY] = []
        for gp in block.findall("GO/GP"):
            punkt = self._punkt_aus_gp_lesen(gp)
            if punkt is not None:
                linienpunkte.append(punkt)
        return linienpunkte

    def _haltung_name_aus_anschluss_hg_lesen(
        self, hg: XmlElement
    ) -> Optional[str]:
        """Liest den Haltungsnamen aus HG001 oder entfernt ein vierstelliges
        Suffix aus HG005 beziehungsweise ein sechsstelliges Suffix aus HG011.
        """
        hg001 = self._als_text(hg.findtext("HG001"))
        if hg001:
            return hg001

        hg005 = self._als_text(hg.findtext("HG005"))
        if hg005 and re.match(r"^.+_\d{4}$", hg005):
            return hg005[:-5]

        hg011 = self._als_text(hg.findtext("HG011"))
        if hg011 and re.match(r"^.+_\d{6}$", hg011):
            return hg011[:-7]

        return None

    def _naechsten_haltungsnamen_finden(
        self, punkt: Optional[QgsPointXY], layer: Optional[QgsVectorLayer]
    ) -> Optional[str]:
        """Liefert nur innerhalb der Anschluss-Toleranz eine Haltung."""
        if punkt is None or layer is None:
            return None
        objekt, abstand, _ = self._naechste_haltung_finden(
            punkt, layer, self.ANSCHLUSS_HALTUNG_TOLERANZ_M
        )
        if objekt is None or abstand is None:
            return None
        return (
            self._als_text(objekt["haltnam"])
            if "haltnam" in objekt.fields().names()
            else None
        )

    def _naechste_haltung_finden(
        self,
        punkt: QgsPointXY,
        layer: QgsVectorLayer,
        toleranz: Optional[float] = None,
    ) -> Tuple[Optional[QgsFeature], Optional[float], Optional[QgsPointXY]]:
        """Ermittelt die nächste Haltung, optional nur innerhalb Toleranz."""
        punkt_geometrie = QgsGeometry.fromPointXY(punkt)
        bestes_objekt = None
        kleinste_distanz = None
        bester_snap = None

        for objekt in layer.getFeatures():
            geometrie = objekt.geometry()
            if not geometrie or geometrie.isEmpty():
                continue
            abstand = geometrie.distance(punkt_geometrie)
            if kleinste_distanz is None or abstand < kleinste_distanz:
                kleinste_distanz = abstand
                bestes_objekt = objekt
                snap_punkt = geometrie.nearestPoint(punkt_geometrie)
                bester_snap = (
                    snap_punkt.asPoint()
                    if snap_punkt and not snap_punkt.isEmpty()
                    else None
                )

        if (
            toleranz is not None
            and kleinste_distanz is not None
            and kleinste_distanz > toleranz
        ):
            return None, kleinste_distanz, None
        return bestes_objekt, kleinste_distanz, bester_snap

    def _objekt_finden(
        self,
        tabelle: str,
        layer: QgsVectorLayer,
        schluesselfeld: str,
        schluesselwert: str,
    ) -> Optional[QgsFeature]:
        """Sucht ein Objekt über den vorgeladenen Importindex.

        :param tabelle: Logischer Tabellenname.
        :param layer: Ziel-Layer.
        :param schluesselfeld: Feld des eindeutigen Schlüssels.
        :param schluesselwert: Gesuchter Schlüsselwert.
        :return: Gefundenes Feature oder ``None``.
        """
        return self._import_objekt_finden(
            tabelle,
            layer,
            (schluesselfeld,),
            {schluesselfeld: schluesselwert},
        )

    def _anschluss_leitnam_lesen(self, hg: XmlElement) -> str:
        """Liest HG011 als Namen der Anschlussleitung.

        Die Felder HG005 bis HG012 sind nach DWA-M 150 ausschließlich für
        Anschlussleitungen vorgesehen; HG011 trägt deren eigene Bezeichnung.
        """
        return self._als_text(hg.findtext("HG011"))

    def _ist_anschluss_hg_fuer_zustand(self, hg: XmlElement) -> bool:
        """Erkennt eine Anschlussleitung am M150-Haltungsartcode ``B``."""
        return self._als_text(hg.findtext("HG313")).upper() == "B"

    def _ist_haltung_hg_fuer_zustand(self, hg: XmlElement) -> bool:
        """Erkennt die in QKan als Haltung importierbaren HG-Arten.

        Nach Referenztabelle 108 steht ``A`` für Kanal, ``C`` für
        Entlastungsleitung und ``Z`` für eine sonstige Haltungsart.
        """
        return self._als_text(hg.findtext("HG313")).upper() in {"A", "C", "Z"}

    def _untersuchungsrichtung_und_bezugspunkt_lesen(
        self, hi: XmlElement
    ) -> Tuple[Optional[str], Optional[str]]:
        """Übersetzt HI101 und HI102 in Richtung und Bezugspunkt.

        HI101 ``I``/``G`` bestimmt die Inspektionsrichtung. HI102 ``A`` oder
        leer ergibt Rohranfang; die übrigen M150-Bezugspunkte werden auf den
        vorhandenen QKan-Wert ``Gerinnemittelpunkt`` zusammengeführt.
        """
        hi101 = self._als_text(hi.findtext("HI101")).upper()
        if hi101 == "I":
            richtung = "in Fließrichtung"
        elif hi101 == "G":
            richtung = "gegen Fließrichtung"
        else:
            richtung = None

        hi102 = self._als_text(hi.findtext("HI102")).upper()
        if hi102 == "A" or not hi102:
            bezugspunkt = "Rohranfang"
        else:
            bezugspunkt = "Gerinnemittelpunkt"

        return richtung, bezugspunkt

    def _streckenschaden_hz_aufteilen(
        self, wert: object
    ) -> Tuple[Optional[str], Optional[int]]:
        """Zerlegt HZ005 in die beiden von QKan verwendeten Felder.

        M150 transportiert den Streckenschaden in einem Feld gemäß dem
        gewählten Kodiersystem. QKan speichert Kennzeichen und laufende Nummer
        getrennt; deshalb werden das erste Zeichen und die erste Zahl gelesen.
        """
        textwert = self._als_text(wert)
        if not textwert:
            return None, None

        streckenschaden = textwert[0]
        zahlen = re.findall(r"\d+", textwert)
        streckenschaden_lfdnr = int(zahlen[0]) if zahlen else 0
        return streckenschaden, streckenschaden_lfdnr

    def _punktabstand_berechnen(
        self, p1: Optional[QgsPointXY], p2: Optional[QgsPointXY]
    ) -> Optional[float]:
        """Berechnet die euklidische Distanz zwischen zwei Kartenpunkten."""
        if p1 is None or p2 is None:
            return None
        dx = p1.x() - p2.x()
        dy = p1.y() - p2.y()
        return (dx * dx + dy * dy) ** 0.5

    def _gerundete_punktsignatur(
        self,
        punkt: Union[QgsPoint, QgsPointXY],
        decimals: Optional[int] = None,
    ) -> Optional[Tuple[float, float]]:
        """Gibt die gerundeten X- und Y-Koordinaten als Tupel zurück."""
        if punkt is None:
            return None
        if decimals is None:
            decimals = self.GEOM_VERGLEICH_STELLEN
        return (
            round(float(punkt.x()), decimals),
            round(float(punkt.y()), decimals),
        )

    def _gerundete_geometriesignatur(
        self, geometrie: Optional[QgsGeometry], decimals: Optional[int] = None
    ) -> object:
        """Erzeugt für Punkt- und Liniengeometrien eine gerundete
        Koordinatensignatur und für andere Geometrietypen eine WKB-Signatur.
        """
        if geometrie is None:
            return None
        if decimals is None:
            decimals = self.GEOM_VERGLEICH_STELLEN

        if geometrie.isEmpty():
            return None

        geometrie_typ = geometrie.type()

        if geometrie_typ == Qgis.GeometryType.Point:
            if geometrie.isMultipart():
                punkte = geometrie.asMultiPoint()
                return (
                    "multipoint",
                    tuple(
                        self._gerundete_punktsignatur(p, decimals)
                        for p in punkte
                    ),
                )

            punkt = geometrie.asPoint()
            return ("point", self._gerundete_punktsignatur(punkt, decimals))

        if geometrie_typ == Qgis.GeometryType.Line:
            if geometrie.isMultipart():
                teile = geometrie.asMultiPolyline()
                return (
                    "multiline",
                    tuple(
                        tuple(
                            self._gerundete_punktsignatur(p, decimals)
                            for p in teil
                        )
                        for teil in teile
                    ),
                )

            linienpunkte = geometrie.asPolyline()
            return (
                "line",
                tuple(
                    self._gerundete_punktsignatur(p, decimals)
                    for p in linienpunkte
                ),
            )

        return ("wkb", bytes(geometrie.asWkb()))

    def _geometrie_gleich_fuer_import(
        self,
        alte_geometrie: Optional[QgsGeometry],
        neue_geometrie: Optional[QgsGeometry],
    ) -> bool:
        """Vergleicht zwei Geometrien anhand ihrer gerundeten
        Geometriesignaturen.
        """
        if alte_geometrie is None and neue_geometrie is None:
            return True
        if alte_geometrie is None or neue_geometrie is None:
            return False
        return self._gerundete_geometriesignatur(
            alte_geometrie
        ) == self._gerundete_geometriesignatur(neue_geometrie)

    def _kg_ist_schacht(self, xml_root: XmlElement, name: str) -> bool:
        """Sucht den KG-Block mit passendem KG001 und akzeptiert nur KG305 S
        oder G.
        """
        for kg in xml_root.findall("KG"):
            if self._als_text(kg.findtext("KG001")) == self._als_text(name):
                return self._als_text(kg.findtext("KG305")).upper() == "S"
        return False

    def _station_auf_haltung_berechnen(
        self,
        punkt: Optional[QgsPointXY],
        h_layer: Optional[QgsVectorLayer],
        haltnam: Optional[str] = None,
    ) -> Optional[float]:
        """Berechnet die Station auf einer benannten oder nahen Haltung."""
        if punkt is None or h_layer is None:
            return None

        punkt_geometrie = QgsGeometry.fromPointXY(punkt)
        if haltnam:
            bestes_objekt = self._haltung_feature_finden(h_layer, haltnam)
        else:
            bestes_objekt, _abstand, _snap = self._naechste_haltung_finden(
                punkt, h_layer, self.ANSCHLUSS_HALTUNG_TOLERANZ_M
            )
        if bestes_objekt is None:
            return None
        geometrie = bestes_objekt.geometry()
        if geometrie is None or geometrie.isEmpty():
            return None
        naechster_punkt = geometrie.nearestPoint(punkt_geometrie)
        if naechster_punkt is None or naechster_punkt.isEmpty():
            return None
        station = geometrie.lineLocatePoint(naechster_punkt)
        if station is None or station < 0:
            return None
        return float(station)

    def _anschluss_match_finden(
        self,
        a_layer: QgsVectorLayer,
        leitnam: str,
    ) -> Optional[QgsFeature]:
        # Anschlussleitungen ausschließlich über leitnam zuordnen,
        # damit keine andere Leitung überschrieben wird.
        """Sucht eine bestehende Anschlussleitung ausschließlich anhand von
        leitnam.
        """
        if not leitnam:
            return None
        return self._objekt_finden(
            "anschlussleitungen", a_layer, "leitnam", leitnam
        )

    def _erstellen_oder_aktualisieren(
        self,
        tabelle: str,
        layer: Optional[QgsVectorLayer],
        schluesselfeld: str,
        schluesselwert: str,
        attribute: Mapping[str, object],
        geometrie: Optional[QgsGeometry],
        bezeichnung: str,
    ) -> None:
        """Legt ein Stammobjekt an oder aktualisiert es.

        :param tabelle: Logischer Tabellenname des Importindexes.
        :param layer: Ziel-Layer.
        :param schluesselfeld: Feld des eindeutigen Objektschlüssels.
        :param schluesselwert: Wert des Objektschlüssels.
        :param attribute: Zu übernehmende Attribute.
        :param geometrie: Optionale neue Geometrie.
        :param bezeichnung: Bezeichnung für Protokollmeldungen.
        """
        if not layer:
            self._log_hinzufuegen(f"⚠ Layer für {bezeichnung} nicht gefunden")
            return

        self._bearbeitung_starten(layer)

        suchdaten = dict(attribute)
        suchdaten[schluesselfeld] = schluesselwert
        objekt = self._import_objekt_finden(
            tabelle,
            layer,
            (schluesselfeld,),
            suchdaten,
        )
        feldnamen = self._feldnamen_lesen(layer)

        if objekt is None:
            neues_objekt = QgsFeature(layer.fields())
            if geometrie is not None and layer.isSpatial():
                neues_objekt.setGeometry(geometrie)
            for feld, wert in attribute.items():
                if feld in feldnamen:
                    neues_objekt[feld] = self._nullify(wert)
            if not layer.addFeature(neues_objekt):
                self._log_hinzufuegen(
                    f"✖ {bezeichnung} '{schluesselwert}' konnte nicht "
                    "neu angelegt werden"
                )
                return
            self._import_objekt_registrieren(
                tabelle,
                (schluesselfeld,),
                suchdaten,
                neues_objekt,
            )
            self._log_hinzufuegen(
                f"➕ {bezeichnung} '{schluesselwert}' neu angelegt"
            )
            return

        aenderungen: List[str] = []
        for feld, wert in attribute.items():
            self._attribut_sicher_aendern(objekt, feld, wert, aenderungen)

        if geometrie is not None and layer.isSpatial():
            alte_geometrie = objekt.geometry()
            if not self._geometrie_gleich_fuer_import(
                alte_geometrie, geometrie
            ):
                objekt.setGeometry(geometrie)
                aenderungen.append("Geometrie aktualisiert")

        if aenderungen:
            if not layer.updateFeature(objekt):
                self._log_hinzufuegen(
                    f"✖ {bezeichnung} '{schluesselwert}' konnte nicht "
                    "aktualisiert werden"
                )
                return
            self._log_hinzufuegen(
                f"✎ {bezeichnung} '{schluesselwert}': "
                + "; ".join(aenderungen)
            )

    def _untersuchungsdatensatz_erstellen_oder_aktualisieren(
        self,
        tabelle: str,
        layer: Optional[QgsVectorLayer],
        schluesselfelder: List[str],
        attribute: Mapping[str, object],
        geometrie: Optional[QgsGeometry],
    ) -> str:
        """Legt einen Untersuchungsdatensatz an oder aktualisiert ihn.

        Diese Upsert-Logik macht den Import derselben Austauschdatei
        wiederholbar: Der fachliche Schlüssel wird vorab aus QKan geladen,
        bestehende Kommentare werden nur ergänzt und identische Geometrien
        werden nicht erneut geschrieben.

        :param tabelle: Logischer Tabellenname des Importindexes.
        :param layer: Ziel-Layer.
        :param schluesselfelder: Felder des eindeutigen
            Untersuchungsschlüssels.
        :param attribute: Zu übernehmende Untersuchungsattribute.
        :param geometrie: Optionale Geometrie des Datensatzes.
        :return: Status ``erstellt``, ``aktualisiert``, ``unveraendert``,
            ``fehler`` oder ``kein_layer``.
        """
        if not layer:
            return "kein_layer"

        self._bearbeitung_starten(layer)
        feldnamen = self._feldnamen_lesen(layer)
        schluessel = tuple(schluesselfelder)
        zielobjekt = self._import_objekt_finden(
            tabelle,
            layer,
            schluessel,
            attribute,
        )

        if zielobjekt is None:
            objekt = QgsFeature(layer.fields())
            if geometrie is not None and layer.isSpatial():
                objekt.setGeometry(geometrie)
            for feld, wert in attribute.items():
                if feld in feldnamen:
                    objekt[feld] = self._nullify(wert)
            if not layer.addFeature(objekt):
                return "fehler"
            self._import_objekt_registrieren(
                tabelle,
                schluessel,
                attribute,
                objekt,
            )
            return "erstellt"

        geaendert = False
        for feld, wert in attribute.items():
            if feld in feldnamen:
                alt = self._nullify(zielobjekt[feld])
                neu = self._nullify(wert)

                if neu is None:
                    continue

                if feld == "kommentar":
                    if neu is None:
                        continue
                    neu = self._kommentar_anhaengen(alt, neu)

                if self._als_text(alt) != self._als_text(neu):
                    zielobjekt[feld] = neu
                    geaendert = True

        if geometrie is not None and layer.isSpatial():
            alte_geometrie = zielobjekt.geometry()
            if not self._geometrie_gleich_fuer_import(
                alte_geometrie, geometrie
            ):
                zielobjekt.setGeometry(geometrie)
                geaendert = True

        if geaendert:
            if not layer.updateFeature(zielobjekt):
                return "fehler"
            return "aktualisiert"

        return "unveraendert"
    # Die folgenden Darstellungsparameter gehören nicht zum M150-Format. Sie

    # erzeugen in QGIS kollisionsarme Beschriftungslinien nach der bisherigen
    # QKan-/STRAKAT-Darstellungslogik.
    ZUSTAND_TEXT_ABSTAND = 0.35
    ZUSTAND_BLOCK_ABSTAND = 0.45
    ZUSTAND_KNOTEN_ABSTAENDE = (0.0, 1.0, 1.5, 4.0)
    ZUSTAND_ANSCHLUSS_VERSATZ = 1.0

    # BCA wird als HZ002-Code des gewählten Kodiersystems transportiert. M150
    # definiert den Transport, aber weder eine 2D-Stummellänge noch
    # Abgleichstoleranzen. Diese Werte sind daher reine QKan-Importregeln.
    BCA_STANDARDLAENGE_M = 0.6
    BCA_STATION_TOLERANZ_M = 0.30
    BCA_GEOMETRIE_TOLERANZ_M = 0.75

    def _objekt_sortwert(self, objekt: QgsFeature) -> int:
        """Verwendet pk und ersatzweise die QGIS-Feature-ID als Sortierwert."""
        if "pk" in objekt.fields().names():
            pk = self._ganzzahl_lesen(objekt["pk"])
            if pk is not None:
                return pk
        return int(objekt.id())

    def _schluesselwert_normalisieren(self, wert: object) -> str:
        """Normalisiert QGIS-Datumswerte und Texte für stabile Schlüssel."""
        if wert is None:
            return ""

        to_string = getattr(wert, "toString", None)
        if callable(to_string):
            try:
                text = to_string("yyyy-MM-dd")
            except TypeError:
                text = to_string()
            text = str(text).strip()
            if text:
                return text

        return self._als_text(wert)

    def _objekt_schluessel(
        self,
        objekt: QgsFeature,
        felder: List[str],
    ) -> Tuple[str, ...]:
        """Liest Felder als normalisiertes Schlüsseltupel."""
        feldnamen = objekt.fields().names()
        return tuple(
            self._schluesselwert_normalisieren(objekt[feld])
            if feld in feldnamen
            else ""
            for feld in felder
        )

    def _linien_endpunkte(
        self, geometrie: Optional[QgsGeometry]
    ) -> Optional[Tuple[QgsPointXY, QgsPointXY]]:
        """Gibt den ersten und letzten Punkt des ersten Linienteils zurück."""
        if geometrie is None or geometrie.isEmpty():
            return None

        if geometrie.isMultipart():
            teile = geometrie.asMultiPolyline()
            if not teile:
                return None
            punkte = teile[0]
        else:
            punkte = geometrie.asPolyline()

        if len(punkte) < 2:
            return None
        return QgsPointXY(punkte[0]), QgsPointXY(punkte[-1])

    def _punktgeometrie_aus_feature(
        self, objekt: QgsFeature
    ) -> Optional[QgsPointXY]:
        """Gibt bei Multipart-Geometrien den ersten Punkt, sonst den einzelnen
        Feature-Punkt zurück.
        """
        geometrie = objekt.geometry()
        if geometrie is None or geometrie.isEmpty():
            return None
        if geometrie.isMultipart():
            punkte = geometrie.asMultiPoint()
            if not punkte:
                return None
            return QgsPointXY(punkte[0])
        return QgsPointXY(geometrie.asPoint())

    def _liniengeometrie_aus_punkten(
        self, punkte: List[QgsPoint]
    ) -> QgsGeometry:
        """Erzeugt mit QgsGeometry.fromPolyline eine Linie aus den übergebenen
        Punkten.
        """
        return QgsGeometry.fromPolyline(punkte)

    def _schadenslinie_setzen(
        self,
        layer: Optional[QgsVectorLayer],
        objekt: QgsFeature,
        geometrie: QgsGeometry,
    ) -> bool:
        """Speichert eine geänderte Schadenslinie.

        :param layer: Layer der Einzelschäden.
        :param objekt: Zu änderndes Schadens-Feature.
        :param geometrie: Neu berechnete Liniengeometrie.
        :return: ``True``, wenn eine Änderung gespeichert wurde.
        """
        if layer is None or not layer.isSpatial():
            return False

        alte_geometrie = objekt.geometry()
        if self._geometrie_gleich_fuer_import(alte_geometrie, geometrie):
            return False

        self._bearbeitung_starten(layer)
        objekt.setGeometry(geometrie)
        return layer.updateFeature(objekt)

    def _schadenslinien_haltung_berechnen(
        self,
        gesamt_layer: Optional[QgsVectorLayer],
        schaden_layer: Optional[QgsVectorLayer],
        zielschluessel: Optional[set[Tuple[str, ...]]] = None,
    ) -> int:
        """Berechnet Beschriftungslinien für Haltungsschäden.

        Die M150-Schadensstation wird nur als Anker auf der Haltung verwendet.
        Form und Abstand der vierteiligen Beschriftungslinie sind eine reine
        QKan-Darstellung und nicht Bestandteil des Austauschstandards.

        :param gesamt_layer: Layer der untersuchten Haltungen.
        :param schaden_layer: Layer der Haltungseinzelschäden.
        :param zielschluessel: Optional auf den aktuellen Import begrenzte
            Untersuchungen.
        :return: Anzahl der geänderten Schadensgeometrien.
        """
        if gesamt_layer is None or schaden_layer is None:
            return 0
        if zielschluessel is not None and not zielschluessel:
            return 0

        self._bearbeitung_starten(schaden_layer)
        tdist = self.ZUSTAND_TEXT_ABSTAND
        bdist = self.ZUSTAND_BLOCK_ABSTAND - self.ZUSTAND_TEXT_ABSTAND
        abst = self.ZUSTAND_KNOTEN_ABSTAENDE

        untersuchte = {}
        untersuchte_nach_id = {}
        for objekt in gesamt_layer.getFeatures():
            zielidentitaet = self._objekt_schluessel(
                objekt, ["haltnam", "untersuchtag"]
            )
            if (
                zielschluessel is not None
                and zielidentitaet not in zielschluessel
            ):
                continue
            schluessel = self._objekt_schluessel(
                objekt, ["haltnam", "schoben", "schunten", "untersuchtag"]
            )
            endpunkte = self._linien_endpunkte(objekt.geometry())
            if not schluessel[0] or not schluessel[3] or endpunkte is None:
                continue
            pa, pe = endpunkte
            blockdaten = {
                "id": self._objekt_sortwert(objekt),
                "xa": pa.x(),
                "ya": pa.y(),
                "xe": pe.x(),
                "ye": pe.y(),
                "richtung": self._als_text(objekt["untersuchrichtung"])
                if "untersuchrichtung" in objekt.fields().names()
                else "",
                "laenge": objekt.geometry().length(),
            }
            untersuchte[schluessel] = blockdaten
            untersuchte_nach_id[blockdaten["id"]] = blockdaten

        # Schäden werden ihrer konkreten Untersuchung zugeordnet. Gleiche
        # Station und gleiches Kürzel werden nur einmal gezeichnet, damit
        # wiederholte oder überlappende Datensätze keine doppelten Linien
        # erzeugen.
        gruppen: Dict[int, List[Tuple[QgsFeature, float]]] = {}
        eindeutige = set()
        for objekt in sorted(
            schaden_layer.getFeatures(),
            key=self._objekt_sortwert,
        ):
            zielidentitaet = self._objekt_schluessel(
                objekt, ["untersuchhal", "untersuchtag"]
            )
            if (
                zielschluessel is not None
                and zielidentitaet not in zielschluessel
            ):
                continue
            schluessel = self._objekt_schluessel(
                objekt,
                ["untersuchhal", "schoben", "schunten", "untersuchtag"],
            )
            blockdaten = untersuchte.get(schluessel)
            if blockdaten is None:
                continue
            station = self._zahl_lesen(objekt["station"])
            if station is None or abs(station) >= 10000:
                continue
            if blockdaten["richtung"] == "gegen Fließrichtung":
                # HZ001 wird ab Inspektionsstart angegeben. Für die
                # QGIS-Geometrie muss eine Gegeninspektion gespiegelt werden.
                station = blockdaten["laenge"] - station
            gruppen_key = (
                blockdaten["id"],
                round(station, 3),
                self._als_text(objekt["kuerzel"])
                if "kuerzel" in objekt.fields().names()
                else "",
            )
            if gruppen_key in eindeutige:
                continue
            eindeutige.add(gruppen_key)
            gruppen.setdefault(blockdaten["id"], []).append((objekt, station))

        anzahl = 0
        for blockkennung in sorted(gruppen):
            daten = sorted(
                gruppen[blockkennung],
                key=lambda eintrag: eintrag[1],
            )
            if not daten:
                continue
            blockdaten = untersuchte_nach_id[blockkennung]
            xa, ya, xe, ye = (
                blockdaten["xa"],
                blockdaten["ya"],
                blockdaten["xe"],
                blockdaten["ye"],
            )
            laenge = ((xe - xa) ** 2 + (ye - ya) ** 2) ** 0.5
            if laenge <= 0.045:
                continue

            n = len(daten)
            pa_lis = [0.0] * n
            pe_lis = [0.0] * n
            ma_lis = [False] * n
            me_lis = [False] * n
            po_lis = [0.0] * n

            pavor = 0.0
            mavor = True
            stvor = None
            # Vorwärtslauf: frühestmögliche kollisionsfreie Textpositionen.
            for i, (_objekt, station) in enumerate(daten):
                abstand = 0.0 if i == 0 else (
                    (abs(station - stvor) > 0.0001) * bdist + tdist
                )
                mavor = bool(mavor and (pavor + abstand > station - 0.0001))
                ma_lis[i] = mavor
                pavor = max(station, pavor + abstand)
                pa_lis[i] = pavor
                stvor = station

            pevor = laenge - (tdist + bdist)
            mevor = True
            stvor = None
            # Rückwärtslauf: spätestmögliche kollisionsfreie
            # Textpositionen.
            for i in range(n - 1, -1, -1):
                station = daten[i][1]
                abstand = 0.0 if i == n - 1 else (
                    (abs(station - stvor) > 0.0001) * bdist + tdist
                )
                mevor = bool(mevor and (pevor - abstand < station + 0.0001))
                me_lis[i] = mevor
                pevor = min(station, pevor - abstand)
                pe_lis[i] = pevor
                stvor = station

            for i in range(n):
                # Ist nur eine Richtung konfliktfrei, wird sie bevorzugt;
                # andernfalls liegt die Beschriftung mittig zwischen beiden
                # berechneten Grenzen.
                if ma_lis[i]:
                    po_lis[i] = pa_lis[i]
                elif me_lis[i]:
                    po_lis[i] = pe_lis[i]
                else:
                    po_lis[i] = (pa_lis[i] + pe_lis[i]) / 2.0

            xu = (xe - xa) / laenge
            yu = (ye - ya) / laenge
            # (xu, yu) folgt der Haltung, (xv, yv) steht senkrecht dazu. Aus
            # beiden Basen entsteht die vierpunktige Verbindung zum Text.
            xv = yu
            yv = -xu

            for i, (objekt, station) in enumerate(daten):
                st0 = station
                st1 = po_lis[i]
                liniengeom = self._liniengeometrie_aus_punkten(
                    [
                        QgsPoint(
                            xa + xu * st0 + xv * abst[0],
                            ya + yu * st0 + yv * abst[0],
                        ),
                        QgsPoint(
                            xa + xu * st0 + xv * abst[1],
                            ya + yu * st0 + yv * abst[1],
                        ),
                        QgsPoint(
                            xa + xu * st1 + xv * abst[2],
                            ya + yu * st1 + yv * abst[2],
                        ),
                        QgsPoint(
                            xa + xu * st1 + xv * abst[3],
                            ya + yu * st1 + yv * abst[3],
                        ),
                    ]
                )
                if self._schadenslinie_setzen(
                    schaden_layer, objekt, liniengeom
                ):
                    anzahl += 1

        return anzahl

    def _schadenslinien_schacht_berechnen(
        self,
        gesamt_layer: Optional[QgsVectorLayer],
        schaden_layer: Optional[QgsVectorLayer],
        zielschluessel: Optional[set[Tuple[str, ...]]] = None,
    ) -> int:
        """Berechnet Beschriftungslinien für Schachtschäden.

        KZ enthält Tiefe und Umfangslage, aber keine Lageplan-Geometrie für
        die Beschriftung. QKan ordnet die Texte deshalb entlang einer
        gedachten, senkrechten Hilfslinie am Schacht an.

        :param gesamt_layer: Layer der untersuchten Schächte.
        :param schaden_layer: Layer der Schachteinzelschäden.
        :param zielschluessel: Optional auf den aktuellen Import begrenzte
            Untersuchungen.
        :return: Anzahl der geänderten Schadensgeometrien.
        """
        if gesamt_layer is None or schaden_layer is None:
            return 0
        if zielschluessel is not None and not zielschluessel:
            return 0

        self._bearbeitung_starten(schaden_layer)
        tdist = self.ZUSTAND_TEXT_ABSTAND
        abst = (
            self.ZUSTAND_KNOTEN_ABSTAENDE[0],
            (
                self.ZUSTAND_KNOTEN_ABSTAENDE[3]
                + self.ZUSTAND_KNOTEN_ABSTAENDE[1]
            ),
            (
                self.ZUSTAND_KNOTEN_ABSTAENDE[3]
                + self.ZUSTAND_KNOTEN_ABSTAENDE[2]
            ),
            (
                self.ZUSTAND_KNOTEN_ABSTAENDE[3]
                + self.ZUSTAND_KNOTEN_ABSTAENDE[3]
            ),
        )

        untersuchte = {}
        untersuchte_nach_id = {}
        for objekt in gesamt_layer.getFeatures():
            schluessel = self._objekt_schluessel(
                objekt, ["schnam", "untersuchtag"]
            )
            if (
                zielschluessel is not None
                and schluessel not in zielschluessel
            ):
                continue
            punkt = self._punktgeometrie_aus_feature(objekt)
            if not schluessel[0] or not schluessel[1] or punkt is None:
                continue
            blockdaten = {
                "id": self._objekt_sortwert(objekt),
                "x": punkt.x(),
                "y": punkt.y(),
            }
            untersuchte[schluessel] = blockdaten
            untersuchte_nach_id[blockdaten["id"]] = blockdaten

        gruppen: Dict[int, List[QgsFeature]] = {}
        eindeutige = set()
        for objekt in sorted(
            schaden_layer.getFeatures(),
            key=self._objekt_sortwert,
        ):
            schluessel = self._objekt_schluessel(
                objekt, ["untersuchsch", "untersuchtag"]
            )
            if (
                zielschluessel is not None
                and schluessel not in zielschluessel
            ):
                continue
            blockdaten = untersuchte.get(schluessel)
            if blockdaten is None:
                continue
            gruppen_key = (
                blockdaten["id"],
                self._als_text(objekt["kuerzel"])
                if "kuerzel" in objekt.fields().names()
                else "",
            )
            if gruppen_key in eindeutige:
                continue
            eindeutige.add(gruppen_key)
            gruppen.setdefault(blockdaten["id"], []).append(objekt)

        anzahl = 0
        for blockkennung in sorted(gruppen):
            daten = gruppen[blockkennung]
            blockdaten = untersuchte_nach_id[blockkennung]
            xa, ya = blockdaten["x"], blockdaten["y"]

            # Entspricht der STRAKAT-/QKan-Logik: gedachte senkrechte Linie
            # vom Schacht nach unten, Textverbindungen rechts davon.
            laenge = 20.0
            xe, ye = xa, ya - laenge
            xu = (xe - xa) / laenge
            yu = (ye - ya) / laenge
            xv = -yu
            yv = xu

            ypos = 0.0
            for objekt in daten:
                st0 = 0.0
                st1 = ypos
                liniengeom = self._liniengeometrie_aus_punkten(
                    [
                        QgsPoint(
                            xa + xu * st0 + xv * abst[0],
                            ya + yu * st0 + yv * abst[0],
                        ),
                        QgsPoint(
                            xa + xu * st0 + xv * abst[1],
                            ya + yu * st0 + yv * abst[1],
                        ),
                        QgsPoint(
                            xa + xu * st1 + xv * abst[2],
                            ya + yu * st1 + yv * abst[2],
                        ),
                        QgsPoint(
                            xa + xu * st1 + xv * abst[3],
                            ya + yu * st1 + yv * abst[3],
                        ),
                    ]
                )
                ypos += tdist
                if self._schadenslinie_setzen(
                    schaden_layer, objekt, liniengeom
                ):
                    anzahl += 1

        return anzahl

    def _schadenslinien_anschlussleitung_berechnen(
        self,
        gesamt_layer: Optional[QgsVectorLayer],
        schaden_layer: Optional[QgsVectorLayer],
        zielschluessel: Optional[set[Tuple[str, ...]]] = None,
    ) -> int:
        """Berechnet Beschriftungslinien für Anschlussleitungsschäden.

        Wie bei Haltungen ist HZ001 der fachliche Anker. Die erzeugte
        Beschriftungsgeometrie und der zusätzliche Endversatz sind
        QKan-spezifisch.

        :param gesamt_layer: Layer der untersuchten Anschlussleitungen.
        :param schaden_layer: Layer der Anschlussleitungseinzelschäden.
        :param zielschluessel: Optional auf den aktuellen Import begrenzte
            Untersuchungen.
        :return: Anzahl der geänderten Schadensgeometrien.
        """
        if gesamt_layer is None or schaden_layer is None:
            return 0
        if zielschluessel is not None and not zielschluessel:
            return 0

        self._bearbeitung_starten(schaden_layer)
        tdist = self.ZUSTAND_TEXT_ABSTAND
        bdist = self.ZUSTAND_BLOCK_ABSTAND - self.ZUSTAND_TEXT_ABSTAND
        abst = self.ZUSTAND_KNOTEN_ABSTAENDE
        versatz = self.ZUSTAND_ANSCHLUSS_VERSATZ

        untersuchte = {}
        untersuchte_nach_id = {}
        for objekt in gesamt_layer.getFeatures():
            zielidentitaet = self._objekt_schluessel(
                objekt, ["leitnam", "untersuchtag"]
            )
            if (
                zielschluessel is not None
                and zielidentitaet not in zielschluessel
            ):
                continue
            schluessel = self._objekt_schluessel(
                objekt, ["leitnam", "schoben", "schunten", "untersuchtag"]
            )
            geometrie = objekt.geometry()
            endpunkte = self._linien_endpunkte(geometrie)
            if (
                not schluessel[0]
                or not schluessel[3]
                or geometrie is None
                or geometrie.isEmpty()
                or endpunkte is None
            ):
                continue
            pa, pe = endpunkte
            blockdaten = {
                "id": self._objekt_sortwert(objekt),
                "xa": pa.x(),
                "ya": pa.y(),
                "xe": pe.x(),
                "ye": pe.y(),
                "richtung": self._als_text(objekt["untersuchrichtung"])
                if "untersuchrichtung" in objekt.fields().names()
                else "",
                "laenge": geometrie.length(),
                "geometrie": QgsGeometry(geometrie),
            }
            untersuchte[schluessel] = blockdaten
            untersuchte_nach_id[blockdaten["id"]] = blockdaten

        # Eindeutigkeit gilt innerhalb genau einer Untersuchung; verschiedene
        # Inspektionsdaten desselben Objekts bleiben getrennt erhalten.
        gruppen: Dict[int, List[Tuple[QgsFeature, float]]] = {}
        eindeutige = set()
        for objekt in sorted(
            schaden_layer.getFeatures(),
            key=self._objekt_sortwert,
        ):
            zielidentitaet = self._objekt_schluessel(
                objekt, ["untersuchleit", "untersuchtag"]
            )
            if (
                zielschluessel is not None
                and zielidentitaet not in zielschluessel
            ):
                continue
            schluessel = self._objekt_schluessel(
                objekt,
                ["untersuchleit", "schoben", "schunten", "untersuchtag"],
            )
            blockdaten = untersuchte.get(schluessel)
            if blockdaten is None:
                continue
            station = self._zahl_lesen(objekt["station"])
            if station is None or abs(station) >= 10000:
                continue
            if blockdaten["richtung"] == "gegen Fließrichtung":
                station = blockdaten["laenge"] - station
            gruppen_key = (
                blockdaten["id"],
                round(station, 3),
                self._als_text(objekt["kuerzel"])
                if "kuerzel" in objekt.fields().names()
                else "",
            )
            if gruppen_key in eindeutige:
                continue
            eindeutige.add(gruppen_key)
            gruppen.setdefault(blockdaten["id"], []).append((objekt, station))

        anzahl = 0
        for blockkennung in sorted(gruppen):
            daten = sorted(
                gruppen[blockkennung],
                key=lambda eintrag: eintrag[1],
            )
            if not daten:
                continue
            blockdaten = untersuchte_nach_id[blockkennung]
            xa, ya, xe, ye = (
                blockdaten["xa"],
                blockdaten["ya"],
                blockdaten["xe"],
                blockdaten["ye"],
            )
            laeng_ = blockdaten["laenge"]
            laenge = max(laeng_, daten[-1][1] - daten[0][1])
            if laenge <= 0.045:
                continue

            n = len(daten)
            pa_lis = [0.0] * n
            pe_lis = [0.0] * n
            ma_lis = [False] * n
            me_lis = [False] * n
            po_lis = [0.0] * n

            pavor = None
            mavor = True
            stvor = None
            # Vorwärts- und Rückwärtslauf bestimmen einen kollisionsarmen
            # Korridor für jede Textposition (analog zu Haltungsschäden).
            for i, (_objekt, station) in enumerate(daten):
                if i == 0:
                    abstand = 0.0
                    pavor = station
                else:
                    abstand = (abs(station - stvor) > 0.0001) * bdist + tdist
                mavor = bool(mavor and (pavor + abstand > station - 0.0001))
                ma_lis[i] = mavor
                pavor = max(station, pavor + abstand)
                pa_lis[i] = pavor
                stvor = station

            pevor = laeng_ - (tdist + bdist) - versatz
            mevor = True
            stvor = None
            for i in range(n - 1, -1, -1):
                station = daten[i][1]
                abstand = 0.0 if i == n - 1 else (
                    (abs(station - stvor) > 0.0001) * bdist + tdist
                )
                mevor = bool(mevor and (pevor - abstand < station + 0.0001))
                me_lis[i] = mevor
                pevor = min(station, pevor - abstand)
                pe_lis[i] = pevor
                stvor = station

            for i in range(n):
                # Anschlussleitungen bevorzugen wegen des reservierten
                # Endversatzes zunächst die rückwärts berechnete Position.
                if me_lis[i]:
                    po_lis[i] = pe_lis[i]
                elif ma_lis[i]:
                    po_lis[i] = pa_lis[i]
                else:
                    po_lis[i] = (pa_lis[i] + pe_lis[i]) / 2.0

            laeng_chord = ((xe - xa) ** 2 + (ye - ya) ** 2) ** 0.5
            if laeng_chord <= 0.000001:
                continue
            xu = (xe - xa) / laeng_chord
            yu = (ye - ya) / laeng_chord
            xv = yu
            yv = -xu

            for i, (objekt, station) in enumerate(daten):
                st0 = station
                st1 = po_lis[i]
                interpoliert = blockdaten["geometrie"].interpolate(st0)
                # Der erste Linienpunkt liegt auf der echten, ggf. geknickten
                # Leitung. Die restlichen Punkte folgen der stabilen Sehne,
                # damit die Beschriftungen parallel ausgerichtet bleiben.
                if interpoliert is not None and not interpoliert.isEmpty():
                    p1 = QgsPoint(interpoliert.asPoint())
                else:
                    p1 = QgsPoint(
                        xa + xu * st0 + xv * abst[0],
                        ya + yu * st0 + yv * abst[0],
                    )

                liniengeom = self._liniengeometrie_aus_punkten(
                    [
                        p1,
                        QgsPoint(
                            xa + xu * st0 + xv * abst[1],
                            ya + yu * st0 + yv * abst[1],
                        ),
                        QgsPoint(
                            xa + xu * st1 + xv * abst[2],
                            ya + yu * st1 + yv * abst[2],
                        ),
                        QgsPoint(
                            xa + xu * st1 + xv * abst[3],
                            ya + yu * st1 + yv * abst[3],
                        ),
                    ]
                )
                if self._schadenslinie_setzen(
                    schaden_layer, objekt, liniengeom
                ):
                    anzahl += 1

        return anzahl

    def _schadenslinien_aktualisieren(
        self,
        schacht_schluessel: set[Tuple[str, ...]],
        haltungs_schluessel: set[Tuple[str, ...]],
        anschluss_schluessel: set[Tuple[str, ...]],
    ) -> None:
        """Aktualisiert Schadenslinien der importierten Untersuchungen.

        :param schacht_schluessel: Importierte Schachtuntersuchungen.
        :param haltungs_schluessel: Importierte Haltungsuntersuchungen.
        :param anschluss_schluessel: Importierte
            Anschlussleitungsuntersuchungen.
        """
        if schacht_schluessel:
            self._schadenslinien_schacht_berechnen(
                self._layer_holen("schaechte_untersucht"),
                self._layer_holen("untersuchdat_schacht"),
                schacht_schluessel,
            )

        if haltungs_schluessel:
            self._schadenslinien_haltung_berechnen(
                self._layer_holen("haltungen_untersucht"),
                self._layer_holen("untersuchdat_haltung"),
                haltungs_schluessel,
            )

        if anschluss_schluessel:
            self._schadenslinien_anschlussleitung_berechnen(
                self._layer_holen("anschlussleitungen_untersucht"),
                self._layer_holen("untersuchdat_anschlussleitung"),
                anschluss_schluessel,
            )

    def _logwert_anzeigen(self, tag: str, wert: object) -> str:
        """Zeigt externe RT-, sonst bekannte DWA-Standardlangtexte im Log."""
        textwert = self._als_text(wert)
        xml_langtext = self._xml_rt_langtext_fuer_feld(tag, textwert)
        if xml_langtext is not None:
            return xml_langtext
        if tag in ("HI107", "KI107"):
            if textwert.upper() == "J":
                return "Ja"
            if textwert.upper() == "N":
                return "Nein"
        standard = self._referenz_langtext_fuer_feld(tag, textwert)
        return standard if standard is not None else textwert

    def _logwert_zusammenfassung(
        self, bezeichnung: str, tag: str, werte: List[Tuple[str, str]]
    ) -> None:
        """Protokolliert einheitliche oder abweichende Metadatenwerte.

        :param bezeichnung: Lesbare Bezeichnung des Felds.
        :param tag: M150-Tag des Felds.
        :param werte: Objektkontexte mit ihren Feldwerten.
        """
        gefuellte_werte = [
            (kontext, wert) for kontext, wert in werte if self._als_text(wert)
        ]
        if not gefuellte_werte:
            return

        eindeutige_werte = sorted({wert for _kontext, wert in gefuellte_werte})
        if len(eindeutige_werte) == 1:
            self._log_hinzufuegen(
                f"{bezeichnung} ({tag}): {eindeutige_werte[0]}"
            )
            return

        self._log_hinzufuegen(
            f"⚠ Unterschiedliche Werte für {bezeichnung} ({tag})"
        )
        for kontext, wert in gefuellte_werte:
            self._log_hinzufuegen(f"  - {kontext}: {wert}")

    def _hg_kontext_lesen(self, hg: XmlElement) -> Tuple[str, str]:
        """Bezeichnet HG313 B als Anschlussleitung und alle übrigen HG-Blöcke
        als Haltung.
        """
        hg313 = self._als_text(hg.findtext("HG313")).upper()
        if hg313 == "B":
            return "Anschlussleitung", self._als_text(hg.findtext("HG011"))
        return "Haltung", self._als_text(hg.findtext("HG001"))

    def _gp_metadaten_loggen(self, xml_root: XmlElement) -> None:
        """Protokolliert GP002 und GP010 und ordnet abweichende Werte ihrem HG-
        oder KG-Objekt zu.
        """
        feldliste = [
            ("GP002", "Koordinatensystem"),
            ("GP010", "Höhensystem"),
        ]
        werte_nach_tag: Dict[str, List[Tuple[str, str]]] = {
            tag: [] for tag, _bezeichnung in feldliste
        }

        for block in (
            list(xml_root.findall("HG"))
            + list(xml_root.findall("KG"))
        ):
            if block.tag == "HG":
                objektart, objektname = self._hg_kontext_lesen(block)
            else:
                objektart = "Schacht"
                objektname = self._als_text(block.findtext("KG001"))

            for go in block.findall("GO"):
                go001 = self._als_text(go.findtext("GO001"))
                for gp in go.findall("GP"):
                    gp001 = self._als_text(gp.findtext("GP001"))
                    details = []
                    if go001:
                        details.append(f"GO001={go001}")
                    if gp001:
                        details.append(f"GP001={gp001}")
                    detailtext = ", ".join(details)
                    kontext = f"{objektart} '{objektname}'"
                    if detailtext:
                        kontext = f"{kontext}, {detailtext}"

                    for tag, _bezeichnung in feldliste:
                        wert = self._logwert_anzeigen(tag, gp.findtext(tag))
                        werte_nach_tag[tag].append((kontext, wert))

        for tag, bezeichnung in feldliste:
            self._logwert_zusammenfassung(
                bezeichnung, tag, werte_nach_tag[tag]
            )

    def _hi_metadaten_loggen(self, xml_root: XmlElement) -> None:
        """Protokolliert HI001, HI002, HI004, HI006, HI103, HI107, HI111,
        HI114 und HI115 und ordnet abweichende Werte ihrem HG-Objekt zu.
        """
        feldliste = [
            ("HI001", "Auftraggeber"),
            ("HI002", "Projektnummer"),
            ("HI004", "Inspektionsgrund"),
            ("HI006", "Kamerasystem"),
            ("HI103", "Inspektionsart"),
            ("HI107", "Reinigung"),
            ("HI111", "Firma"),
            ("HI114", "Videospeichermedium"),
            ("HI115", "Name Speichermedium"),
        ]
        werte_nach_tag: Dict[str, List[Tuple[str, str]]] = {
            tag: [] for tag, _bezeichnung in feldliste
        }

        for hg in xml_root.findall("HG"):
            objektart, objektname = self._hg_kontext_lesen(hg)
            for hi in hg.findall("HI"):
                kontext = f"{objektart} '{objektname}'"

                for tag, _bezeichnung in feldliste:
                    wert = self._logwert_anzeigen(tag, hi.findtext(tag))
                    werte_nach_tag[tag].append((kontext, wert))

        for tag, bezeichnung in feldliste:
            self._logwert_zusammenfassung(
                bezeichnung, tag, werte_nach_tag[tag]
            )

    def _ki_metadaten_loggen(self, xml_root: XmlElement) -> None:
        """Protokolliert die ausdrücklich ausgewählten KI-Metadaten.

        Geloggt werden nur KI002, KI004, KI006 und KI107. Andere KI-Felder
        werden hier bewusst nicht zusätzlich protokolliert.
        """
        feldliste = [
            ("KI002", "Projektnummer"),
            ("KI004", "Inspektionsgrund"),
            ("KI006", "Kamerasystem"),
            ("KI107", "Reinigung"),
        ]
        werte_nach_tag: Dict[str, List[Tuple[str, str]]] = {
            tag: [] for tag, _bezeichnung in feldliste
        }

        for kg in xml_root.findall("KG"):
            schnam = self._als_text(kg.findtext("KG001"))
            for ki in kg.findall("KI"):
                kontext = f"Schacht '{schnam}'"
                for tag, _bezeichnung in feldliste:
                    wert = self._logwert_anzeigen(tag, ki.findtext(tag))
                    werte_nach_tag[tag].append((kontext, wert))

        for tag, bezeichnung in feldliste:
            self._logwert_zusammenfassung(
                bezeichnung, tag, werte_nach_tag[tag]
            )

    def _m150_metadaten_loggen(self, xml_root: XmlElement) -> None:
        """Protokolliert FD001, FD002 sowie die ausgewählten GP-, HI- und
        KI-Metadaten.
        """
        fd001 = self._logwert_anzeigen("FD001", xml_root.findtext("FD/FD001"))
        fd002 = self._logwert_anzeigen("FD002", xml_root.findtext("FD/FD002"))

        if fd001:
            self._log_hinzufuegen(f"M150-Version (FD001): {fd001}")
        if fd002:
            self._log_hinzufuegen(f"M150-Formattyp (FD002): {fd002}")

        self._gp_metadaten_loggen(xml_root)
        self._hi_metadaten_loggen(xml_root)
        self._ki_metadaten_loggen(xml_root)
    # Import der XML-Blöcke

    def _import_schaechte(
        self, xml_root: XmlElement, layer: Optional[QgsVectorLayer]
    ) -> None:
        """Importiert KG-Blöcke mit KG305 S oder G und gültiger Punktgeometrie
        in den Schachtlayer.
        """
        if not layer:
            self._log_hinzufuegen("⚠ Layer 'Schächte' nicht gefunden")
            return

        for kg in xml_root.findall("KG"):
            name = self._als_text(kg.findtext("KG001"))
            # *_START und *_VIRT sind bekannte technische Hilfsknoten aus
            # Austauschdateien und keine eigenständigen QKan-Schächte.
            if not name or name.endswith("_START") or name.endswith("_VIRT"):
                continue

            typ = self._als_text(kg.findtext("KG305"))

            # Projektregel: In den QKan-Schachtlayer kommt nur KG305=S.
            if typ.upper() != "S":
                continue

            zuordnung = self._knotenart_aus_m150_lesen(typ)
            if zuordnung is None:
                continue

            gp = kg.find("GO/GP")
            punkt = self._punkt_aus_gp_lesen(gp) if gp is not None else None
            if punkt is None:
                self._log_hinzufuegen(
                    f"⚠ Schacht/Knoten '{name}' ohne Geometrie übersprungen"
                )
                continue

            geometrie = QgsGeometry.fromPointXY(punkt)

            # KG308/KG309 werden in M150 in Millimetern geführt. QKan
            # speichert für Schächte einen Durchmesser in Metern. Bei
            # befülltem KG308 wird dieser Wert verwendet; KG309 dient als
            # Rückfall, falls KG308 fehlt.
            durchmesser_mm = self._zahl_lesen(kg.findtext("KG308"))
            if durchmesser_mm is None:
                durchmesser_mm = self._zahl_lesen(kg.findtext("KG309"))
            durchmesser_m = (
                durchmesser_mm / 1000.0
                if durchmesser_mm is not None
                else None
            )

            attribute = {
                "schnam": name,
                "durchm": durchmesser_m,
                "sohlhoehe": (
                    self._zahl_ohne_null(gp.findtext("GP007"))
                    if gp is not None
                    else None
                ),
                "material": self._material_aus_m150_lesen(
                    kg.findtext("KG304"), "Schachtmaterial"
                ),
                "entwart": self._m150_entwart_zu_qkan(
                    kg.findtext("KG302"), None
                ),
                "simstatus": self._nullify(kg.findtext("KG401")),
                "schachttyp": zuordnung["schachttyp"],
                "knotentyp": zuordnung["knotentyp"],
                "kommentar": self._nullify(kg.findtext("KG999")),
            }
            self._erstellen_oder_aktualisieren(
                "schaechte",
                layer,
                "schnam",
                name,
                attribute,
                geometrie,
                "Schacht/Knoten",
            )

    def _anschlussschacht_hg_daten_lesen(
        self,
        xml_root: XmlElement,
        kg_name: str,
        a_layer: Optional[QgsVectorLayer],
    ) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """Liest Haltung, Urstation und Leitungsname zum Anschlussknoten."""
        for hg in xml_root.findall("HG"):
            if self._als_text(hg.findtext("HG313")).upper() != "B":
                continue
            if self._als_text(hg.findtext("HG005")) != kg_name:
                continue

            leitnam = self._anschluss_leitnam_lesen(hg)
            haltnam = self._haltung_name_aus_anschluss_hg_lesen(hg)
            urstation = self._zahl_lesen(hg.findtext("HG007"))

            if a_layer is not None and leitnam:
                leitungsobjekt = self._anschluss_match_finden(
                    a_layer, leitnam
                )
                if leitungsobjekt is not None:
                    feldnamen = leitungsobjekt.fields().names()
                    if "haltnam" in feldnamen:
                        haltnam = (
                            self._als_text(leitungsobjekt["haltnam"])
                            or haltnam
                        )
                    if "urstation" in feldnamen:
                        gespeicherte_station = self._zahl_lesen(
                            leitungsobjekt["urstation"]
                        )
                        if gespeicherte_station is not None:
                            urstation = gespeicherte_station

            return haltnam, urstation, leitnam or None

        return None, None, None

    def _anschlussschacht_nach_punkt_finden(
        self,
        layer: Optional[QgsVectorLayer],
        name: str,
        punkt: QgsPointXY,
        haltnam: Optional[str],
        urstation: Optional[float],
    ) -> Optional[QgsFeature]:
        """Findet einen vorhandenen Anschlussschacht am Importpunkt.

        Die Geometrie innerhalb der engen Endpunkttoleranz ist zwingend.
        Haltung und Urstation entscheiden nur zwischen mehreren
        geometrischen Treffern; der Name darf keinen räumlich abweichenden
        Datensatz erzwingen.
        """
        if layer is None or punkt is None:
            return None

        toleranz = self.ANSCHLUSSSCHACHT_ENDPOINT_TOLERANZ_M
        request = QgsFeatureRequest().setFilterRect(
            QgsRectangle(
                punkt.x() - toleranz,
                punkt.y() - toleranz,
                punkt.x() + toleranz,
                punkt.y() + toleranz,
            )
        )
        punkt_geometrie = QgsGeometry.fromPointXY(punkt)
        treffer = []

        for objekt in layer.getFeatures(request):
            geometrie = objekt.geometry()
            if geometrie is None or geometrie.isEmpty():
                continue
            abstand = geometrie.distance(punkt_geometrie)
            if abstand > toleranz:
                continue

            feldnamen = objekt.fields().names()
            objekt_haltnam = (
                self._als_text(objekt["haltnam"])
                if "haltnam" in feldnamen
                else ""
            )
            haltnam_abweichung = (
                0
                if haltnam and objekt_haltnam == self._als_text(haltnam)
                else 1
            )

            objekt_station = (
                self._zahl_lesen(objekt["urstation"])
                if "urstation" in feldnamen
                else None
            )
            if urstation is not None and objekt_station is not None:
                stationsabweichung = abs(objekt_station - urstation)
            else:
                stationsabweichung = float("inf")

            treffer.append((
                haltnam_abweichung,
                stationsabweichung,
                abstand,
                self._objekt_sortwert(objekt),
                objekt,
            ))

        if not treffer:
            return None
        treffer.sort(key=lambda eintrag: eintrag[:-1])
        return treffer[0][-1]

    def _anschlussschacht_erstellen_oder_aktualisieren(
        self,
        layer: Optional[QgsVectorLayer],
        name: str,
        attribute: Mapping[str, object],
        geometrie: QgsGeometry,
        haltnam: Optional[str],
        urstation: Optional[float],
    ) -> None:
        """Klassifiziert einen vorhandenen Anschlusspunkt oder legt ihn an."""
        if layer is None:
            self._log_hinzufuegen(
                "⚠ Layer 'Anschlussschächte' nicht gefunden"
            )
            return

        punkt = geometrie.asPoint()
        self._bearbeitung_starten(layer)
        objekt = self._anschlussschacht_nach_punkt_finden(
            layer,
            name,
            QgsPointXY(punkt),
            haltnam,
            urstation,
        )
        feldnamen = self._feldnamen_lesen(layer)

        if objekt is None:
            neues_objekt = QgsFeature(layer.fields())
            if layer.isSpatial():
                neues_objekt.setGeometry(geometrie)
            for feld, wert in attribute.items():
                if feld in feldnamen:
                    neues_objekt[feld] = self._nullify(wert)
            if not layer.addFeature(neues_objekt):
                self._log_hinzufuegen(
                    f"✖ Anschlussknoten '{name}' konnte nicht neu "
                    "angelegt werden"
                )
                return
            self._log_hinzufuegen(
                f"➕ Anschlussknoten '{name}' neu angelegt"
            )
            return

        aenderungen: List[str] = []
        for feld, wert in attribute.items():
            if feld not in feldnamen:
                continue
            if feld == "knotentyp":
                neu = self._nullify(wert)
                if neu is None:
                    continue
                alt = self._nullify(objekt[feld])
                if self._als_text(alt) != self._als_text(neu):
                    objekt[feld] = neu
                    aenderungen.append(
                        f"knotentyp: {self._als_text(alt)} -> "
                        f"{self._als_text(neu)}"
                    )
                continue
            self._attribut_sicher_aendern(
                objekt, feld, wert, aenderungen
            )

        if layer.isSpatial() and not self._geometrie_gleich_fuer_import(
            objekt.geometry(), geometrie
        ):
            objekt.setGeometry(geometrie)
            aenderungen.append("Geometrie aktualisiert")

        if aenderungen:
            if not layer.updateFeature(objekt):
                self._log_hinzufuegen(
                    f"✖ Anschlussknoten '{name}' konnte nicht "
                    "aktualisiert werden"
                )
                return
            self._log_hinzufuegen(
                f"✎ Anschlussknoten '{name}': " + "; ".join(aenderungen)
            )
        else:
            self._log_hinzufuegen(
                f"✔ Anschlussknoten '{name}' erkannt"
            )

    def _import_anschlussschaechte(
        self,
        xml_root: XmlElement,
        layer: Optional[QgsVectorLayer],
        a_layer: Optional[QgsVectorLayer],
    ) -> None:
        """Importiert alle nicht-fiktiven, nicht-Schacht-Knoten als
        Anschlussschächte und klassifiziert vorhandene Endpunkte neu.
        """
        if layer is None:
            self._log_hinzufuegen(
                "⚠ Layer 'Anschlussschächte' nicht gefunden"
            )
            return

        for kg in xml_root.findall("KG"):
            name = self._als_text(kg.findtext("KG001"))
            if not name or name.endswith("_START") or name.endswith("_VIRT"):
                continue

            typ = self._als_text(kg.findtext("KG305")).upper()
            if typ in {"", "S", "F"}:
                continue

            gp = kg.find("GO/GP")
            punkt = self._punkt_aus_gp_lesen(gp) if gp is not None else None
            if punkt is None:
                self._log_hinzufuegen(
                    f"⚠ Anschlussknoten '{name}' ohne Geometrie "
                    "übersprungen"
                )
                continue

            zuordnung = self._knotenart_aus_m150_lesen(typ)
            knotentyp = (
                zuordnung.get("knotentyp")
                if zuordnung is not None
                else typ
            )

            durchmesser_mm = self._zahl_lesen(kg.findtext("KG308"))
            if durchmesser_mm is None:
                durchmesser_mm = self._zahl_lesen(kg.findtext("KG309"))
            durchmesser_m = (
                durchmesser_mm / 1000.0
                if durchmesser_mm is not None
                else None
            )

            haltnam, urstation, _leitnam = (
                self._anschlussschacht_hg_daten_lesen(
                    xml_root, name, a_layer
                )
            )
            geometrie = QgsGeometry.fromPointXY(punkt)
            attribute = {
                "schnam": name,
                "sohlhoehe": self._zahl_lesen(gp.findtext("GP007")),
                "durchm": durchmesser_m,
                "entwart": self._m150_entwart_zu_qkan(
                    kg.findtext("KG302"), None
                ),
                "strasse": self._nullify(kg.findtext("KG102")),
                "baujahr": self._ganzzahl_lesen(kg.findtext("KG303")),
                "haltnam": haltnam,
                "urstation": urstation,
                "knotentyp": knotentyp,
                "simstatus": self._nullify(kg.findtext("KG401")),
                "material": self._material_aus_m150_lesen(
                    kg.findtext("KG304"), "Knotenmaterial"
                ),
                "xsch": punkt.x(),
                "ysch": punkt.y(),
                "kommentar": self._nullify(kg.findtext("KG999")),
            }
            self._anschlussschacht_erstellen_oder_aktualisieren(
                layer,
                name,
                attribute,
                geometrie,
                haltnam,
                urstation,
            )

    def _import_haltungen(
        self, xml_root: XmlElement, layer: Optional[QgsVectorLayer]
    ) -> None:
        """Importiert HG-Blöcke mit HG313 A, C oder Z und mindestens zwei
        Linienpunkten als Haltungen.
        """
        if not layer:
            self._log_hinzufuegen("⚠ Layer 'Haltungen' nicht gefunden")
            return

        for hg in xml_root.findall("HG"):
            # HG313 verweist auf M150-Referenztabelle 108. Anschlussleitungen
            # (B) werden getrennt importiert, da sie in QKan einen eigenen
            # Layer und einen anderen Objektschlüssel besitzen.
            hg313 = self._als_text(hg.findtext("HG313")).upper()
            if not hg313:
                hg001 = self._als_text(hg.findtext("HG001"))
                self._log_hinzufuegen(
                    f"⚠ HG-Block '{hg001}' ohne HG313 übersprungen"
                )
                continue
            if hg313 not in {"A", "C", "Z"}:
                continue

            name = self._als_text(hg.findtext("HG001"))
            if not name:
                continue

            linienpunkte = self._linienpunkte_aus_go_lesen(hg)
            if len(linienpunkte) < 2:
                self._log_hinzufuegen(
                    f"⚠ Haltung '{name}' ohne ausreichende Geometrie "
                    "übersprungen"
                )
                continue

            geometrie = QgsGeometry.fromPolyline(
                [QgsPoint(p.x(), p.y()) for p in linienpunkte]
            )

            sohleoben = None
            sohleunten = None
            for gp_element in hg.findall("GO/GP"):
                # RA/RE sind QKan-kompatible Rollenmarker im freien
                # Bemerkungsfeld GP999, keine standardisierten M150-Schlüssel.
                # Ohne Marker bleiben die Sohlhöhen bewusst leer, statt die
                # Endpunktrolle nur aus der XML-Reihenfolge zu erraten.
                gp_rolle = self._als_text(gp_element.findtext("GP999"))
                gp_z_wert = self._zahl_ohne_null(
                    gp_element.findtext("GP007")
                )
                if gp_rolle == "RA":
                    sohleoben = gp_z_wert
                elif gp_rolle == "RE":
                    sohleunten = gp_z_wert

            attribute = {
                "haltnam": name,
                "schoben": self._nullify(hg.findtext("HG003")),
                "schunten": self._nullify(hg.findtext("HG004")),
                "baujahr": self._ganzzahl_ohne_null(hg.findtext("HG303")),
                "material": self._material_aus_m150_lesen(
                    hg.findtext("HG304"), "Material"
                ),
                "breite": self._zahl_lesen(hg.findtext("HG306")),
                "hoehe": self._zahl_lesen(hg.findtext("HG307")),
                "durchm": self._zahl_lesen(hg.findtext("HG306")),
                "laenge": self._zahl_lesen(hg.findtext("HG310")),
                "sohleoben": sohleoben,
                "sohleunten": sohleunten,
                "profilnam": self._profil_aus_m150_lesen(hg.findtext("HG305")),
                "profilauskleidung": self._profilauskleidung_aus_m150_lesen(
                    hg.findtext("HG308")
                ),
                "innenmaterial": self._material_aus_m150_lesen(
                    hg.findtext("HG309"), "Innenmaterial"
                ),
                "haltungstyp": "Haltung",
                "abflussart": self._m150_kanalart_zu_qkan(
                    hg.findtext("HG301"), None
                ),
                "entwart": self._m150_entwart_zu_qkan(
                    hg.findtext("HG302"), None
                ),
                "kommentar": self._nullify(hg.findtext("HG999")),
            }
            self._erstellen_oder_aktualisieren(
                "haltungen",
                layer,
                "haltnam",
                name,
                attribute,
                geometrie,
                "Haltung",
            )

    def _haltung_feature_finden(
        self, h_layer: Optional[QgsVectorLayer], haltnam: str
    ) -> Optional[QgsFeature]:
        """Findet eine Haltung über haltnam."""
        if h_layer is None or not haltnam:
            return None
        feldnamen = self._feldnamen_lesen(h_layer)
        if "haltnam" not in feldnamen:
            return None
        return self._objekt_finden(
            "haltungen", h_layer, "haltnam", haltnam
        )

    def _uhrposition_als_int(self, wert: object) -> Optional[int]:
        """Liest eine Uhrposition aus HZ006/HZ007."""
        zahl = self._ganzzahl_lesen(wert)
        if zahl is None:
            return None
        if zahl < 0:
            return None
        if zahl == 0:
            return 0
        if zahl > 12:
            return None
        return zahl

    def _bca_station_fuer_geometrie(
        self,
        station: float,
        richtung: Optional[str],
        haltung_geometrie: QgsGeometry,
    ) -> float:
        """Wandelt eine M150-Inspektionsstation in eine Geometriestation um.

        HZ001 gilt vom Inspektionsstart aus. Für die hier unterstützte
        Linieninspektion wird dessen Richtung aus HI101 gelesen; HI102 wird
        getrennt in das QKan-Attribut ``bezugspunkt`` übernommen. Die
        QGIS-Geometrie wird in ihrer gespeicherten Punktreihenfolge
        stationiert. Bei einer Inspektion gegen Fließrichtung wird die Station
        deshalb an der Haltungslänge gespiegelt.

        :param station: Station aus dem HZ-Datensatz.
        :param richtung: Untersuchungsrichtung.
        :param haltung_geometrie: Geometrie der untersuchten Haltung.
        :return: Auf die Haltungslänge begrenzte Geometriestation.
        """
        laenge = haltung_geometrie.length()
        geomstation = station
        if richtung == "gegen Fließrichtung":
            geomstation = laenge - station
        if geomstation < 0:
            return 0.0
        if geomstation > laenge:
            return float(laenge)
        return float(geomstation)

    def _bca_urstation_fuer_qkan(
        self,
        station: float,
        richtung: Optional[str],
        haltung_geometrie: QgsGeometry,
    ) -> float:
        """Berechnet die QKan-Urstation eines BCA-Anschlusses.

        ``urstation`` folgt der in QKan vorhandenen Gegenstationierung vom
        Geometrieende und ist kein Feldname aus DWA-M 150.

        :param station: Station aus dem HZ-Datensatz.
        :param richtung: Untersuchungsrichtung.
        :param haltung_geometrie: Geometrie der untersuchten Haltung.
        :return: Auf die Haltungslänge begrenzte QKan-Urstation.
        """
        geomstation = self._bca_station_fuer_geometrie(
            station, richtung, haltung_geometrie
        )
        laenge = haltung_geometrie.length()
        urstation = laenge - geomstation
        if urstation < 0:
            return 0.0
        if urstation > laenge:
            return float(laenge)
        return float(urstation)

    def _seitfaktor_aus_uhrposition(
        self, uhr: Optional[int], richtung: Optional[str]
    ) -> int:
        """Überführt HZ006 in eine Seite der 2D-Haltungsgeometrie.

        HZ006 beschreibt die Umfangslage im Uhrzeigersinn. Die Reduktion auf
        links/rechts ist eine notwendige QKan-Darstellungsentscheidung.
        """
        # 3 Uhr = rechts, 9 Uhr = links bezogen auf Blick-/Inspektionsrichtung.
        # 12/6 Uhr sind im 2D-Lageplan nicht eindeutig darstellbar; dafür wird
        # bewusst ein kurzer rechter Stummel erzeugt.
        if uhr in (7, 8, 9, 10, 11):
            faktor = -1
        else:
            faktor = 1
        if richtung == "gegen Fließrichtung":
            faktor *= -1
        return faktor

    def _bca_lokale_normalenbasis(
        self, haltung_geometrie: QgsGeometry, geomstation: float
    ) -> Optional[Tuple[QgsPointXY, float, float]]:
        """Liefert Anschlusspunkt und rechten Normalenvektor der Haltung.

        Die lokale Richtung wird beidseits der Station abgetastet, damit auch
        geknickte oder gekrümmte Haltungen seitengerecht behandelt werden.
        """
        punktgeom = haltung_geometrie.interpolate(geomstation)
        if punktgeom is None or punktgeom.isEmpty():
            return None
        anschlusspunkt = QgsPointXY(punktgeom.asPoint())

        gesamtlaenge = haltung_geometrie.length()
        delta = min(0.25, max(gesamtlaenge / 100.0, 0.05))
        st_a = max(0.0, geomstation - delta)
        st_b = min(gesamtlaenge, geomstation + delta)
        if abs(st_b - st_a) < 0.000001:
            return None

        geom_a = haltung_geometrie.interpolate(st_a)
        geom_b = haltung_geometrie.interpolate(st_b)
        if geom_a is None or geom_a.isEmpty():
            return None
        if geom_b is None or geom_b.isEmpty():
            return None

        p_a = geom_a.asPoint()
        p_b = geom_b.asPoint()
        dx = p_b.x() - p_a.x()
        dy = p_b.y() - p_a.y()
        sehnenlaenge = (dx * dx + dy * dy) ** 0.5
        if sehnenlaenge <= 0.000001:
            return None

        # Rechter Normalenvektor zur Haltungsrichtung.
        return anschlusspunkt, dy / sehnenlaenge, -dx / sehnenlaenge

    def _bca_geometrieseite_bestimmen(
        self,
        geometrie: Optional[QgsGeometry],
        haltung_geometrie: QgsGeometry,
        station: float,
        richtung: Optional[str],
    ) -> Optional[int]:
        """Bestimmt die Seite einer Anschlussleitungsgeometrie.

        :param geometrie: Geometrie der vorhandenen Anschlussleitung.
        :param haltung_geometrie: Geometrie der zugehörigen Haltung.
        :param station: BCA-Station aus der Inspektion.
        :param richtung: Untersuchungsrichtung.
        :return: ``1`` für rechts, ``-1`` für links oder ``None``.
        """
        if geometrie is None or geometrie.isEmpty():
            return None
        geomstation = self._bca_station_fuer_geometrie(
            station, richtung, haltung_geometrie
        )
        basis = self._bca_lokale_normalenbasis(
            haltung_geometrie, geomstation
        )
        if basis is None:
            return None
        anschlusspunkt, nx, ny = basis

        endpunkte = self._linien_endpunkte(geometrie)
        if endpunkte is None:
            return None
        p1, p2 = endpunkte
        d1 = self._punktabstand_berechnen(anschlusspunkt, p1)
        d2 = self._punktabstand_berechnen(anschlusspunkt, p2)
        if d1 is None or d2 is None:
            return None
        aussenpunkt = p1 if d1 >= d2 else p2
        vx = aussenpunkt.x() - anschlusspunkt.x()
        vy = aussenpunkt.y() - anschlusspunkt.y()
        skalarprodukt = vx * nx + vy * ny
        if abs(skalarprodukt) < 0.000001:
            return None
        return 1 if skalarprodukt > 0 else -1

    def _bca_stummelgeometrie_erzeugen(
        self,
        haltung_geometrie: QgsGeometry,
        station: float,
        richtung: Optional[str],
        uhr: Optional[int],
        laenge: float,
    ) -> Optional[QgsGeometry]:
        """Erzeugt eine kurze Anschlussleitung aus einem BCA-Schaden.

        :param haltung_geometrie: Geometrie der untersuchten Haltung.
        :param station: BCA-Station aus der Inspektion.
        :param richtung: Untersuchungsrichtung.
        :param uhr: Uhrposition des Anschlusses.
        :param laenge: Länge der zu erzeugenden Leitung.
        :return: Erzeugte Liniengeometrie oder ``None``.
        """
        if haltung_geometrie is None or haltung_geometrie.isEmpty():
            return None
        if laenge <= 0:
            return None

        geomstation = self._bca_station_fuer_geometrie(
            station, richtung, haltung_geometrie
        )
        basis = self._bca_lokale_normalenbasis(
            haltung_geometrie, geomstation
        )
        if basis is None:
            return None
        anschlusspunkt, nx, ny = basis

        faktor = self._seitfaktor_aus_uhrposition(uhr, richtung)
        aussenpunkt = QgsPointXY(
            anschlusspunkt.x() + nx * faktor * laenge,
            anschlusspunkt.y() + ny * faktor * laenge,
        )

        # Leitungen werden in Fließrichtung geführt. Eine HA-Leitung fließt
        # fachlich zum Anschluss an der Haltung, deshalb beginnt der
        # Darstellungsstummel außen und endet am BCA-Punkt.
        return QgsGeometry.fromPolyline(
            [
                QgsPoint(aussenpunkt.x(), aussenpunkt.y()),
                QgsPoint(anschlusspunkt.x(), anschlusspunkt.y()),
            ]
        )

    def _bca_leitnam_basis(self, haltnam: str) -> str:
        """Liefert den Präfix für automatisch benannte HA-Leitungen."""
        return self._als_text(haltnam).strip()

    def _bca_naechsten_leitnam_erzeugen(
        self,
        haltnam: str,
        reservierte_namen: Optional[set] = None,
    ) -> str:
        """Erzeugt einen freien HA-Namen von <haltnam>_01 bis _99."""
        basis = self._bca_leitnam_basis(haltnam)
        vorhandene = set(reservierte_namen or set())

        for schluessel in self._import_objekte.get(
            "anschlussleitungen", {}
        ):
            if schluessel and schluessel[0]:
                vorhandene.add(schluessel[0])

        for nummer in range(1, 100):
            kandidat = f"{basis}_{nummer:02d}"
            if kandidat not in vorhandene:
                return kandidat

        return ""

    def _bca_station_passt_ueber_attribute(
        self,
        objekt: QgsFeature,
        feldnamen: List[str],
        stationskandidaten: set,
    ) -> bool:
        """Prüft eine vorhandene Leitung über Stationsattribute.

        :param objekt: Zu prüfende Anschlussleitung.
        :param feldnamen: Vorhandene Attributnamen des Layers.
        :param stationskandidaten: Zulässige Stationswerte.
        :return: ``True``, wenn ein Stationswert innerhalb der Toleranz liegt.
        """
        for feld in ("urstation", "station"):
            if feld not in feldnamen:
                continue
            objekt_station = self._zahl_lesen(objekt[feld])
            if objekt_station is None:
                continue
            for kandidat in stationskandidaten:
                if (
                    abs(objekt_station - kandidat)
                    <= self.BCA_STATION_TOLERANZ_M
                ):
                    return True
        return False

    def _bca_geometrie_trifft_anschlusspunkt(
        self,
        geometrie: Optional[QgsGeometry],
        anschlusspunkt: QgsPointXY,
    ) -> bool:
        """Prüft, ob eine vorhandene HA-Geometrie am BCA-Punkt anliegt."""
        if geometrie is None or geometrie.isEmpty():
            return False

        punktgeom = QgsGeometry.fromPointXY(anschlusspunkt)
        try:
            if geometrie.distance(punktgeom) <= self.BCA_GEOMETRIE_TOLERANZ_M:
                return True
        except Exception:
            LOGGER.debug(
                "Geometrieabstand am BCA-Punkt konnte nicht berechnet "
                "werden; Endpunkte werden ersatzweise geprüft.",
                exc_info=True,
            )

        endpunkte = self._linien_endpunkte(geometrie)
        if endpunkte is None:
            return False

        p1, p2 = endpunkte
        d1 = self._punktabstand_berechnen(anschlusspunkt, p1)
        d2 = self._punktabstand_berechnen(anschlusspunkt, p2)
        if d1 is not None and d1 <= self.BCA_GEOMETRIE_TOLERANZ_M:
            return True
        if d2 is not None and d2 <= self.BCA_GEOMETRIE_TOLERANZ_M:
            return True
        return False

    def _bca_objekt_seite_bestimmen(
        self,
        objekt: QgsFeature,
        feldnamen: List[str],
        richtung: Optional[str],
        haltung_geometrie: QgsGeometry,
        station: float,
    ) -> Optional[int]:
        """Bestimmt die Haltungsseite einer vorhandenen Anschlussleitung.

        :param objekt: Zu prüfende Anschlussleitung.
        :param feldnamen: Vorhandene Attributnamen des Layers.
        :param richtung: Untersuchungsrichtung.
        :param haltung_geometrie: Geometrie der zugehörigen Haltung.
        :param station: BCA-Station aus der Inspektion.
        :return: ``1`` für rechts, ``-1`` für links oder ``None``.
        """
        if "lageanschluss" in feldnamen:
            objekt_uhr = self._uhrposition_als_int(objekt["lageanschluss"])
            if objekt_uhr is not None:
                return self._seitfaktor_aus_uhrposition(objekt_uhr, richtung)

        return self._bca_geometrieseite_bestimmen(
            objekt.geometry(),
            haltung_geometrie,
            station,
            richtung,
        )

    def _bca_anschluss_match_finden(
        self,
        a_layer: QgsVectorLayer,
        haltnam: str,
        urstation: Optional[float],
        uhr: Optional[int],
        richtung: Optional[str],
        haltung_geometrie: QgsGeometry,
        station: float,
    ) -> Optional[QgsFeature]:
        """Sucht eine Anschlussleitung an gleicher Station und Seite.

        :param a_layer: Layer der Anschlussleitungen.
        :param haltnam: Name der zugehörigen Haltung.
        :param urstation: Berechnete QKan-Urstation.
        :param uhr: Uhrposition des Anschlusses.
        :param richtung: Untersuchungsrichtung.
        :param haltung_geometrie: Geometrie der untersuchten Haltung.
        :param station: BCA-Station aus der Inspektion.
        :return: Passende Anschlussleitung oder ``None``.
        """
        if urstation is None:
            return None
        if haltung_geometrie is None or haltung_geometrie.isEmpty():
            return None

        feldnamen = self._feldnamen_lesen(a_layer)
        laenge = haltung_geometrie.length()
        geomstation = self._bca_station_fuer_geometrie(
            station, richtung, haltung_geometrie
        )
        basis = self._bca_lokale_normalenbasis(
            haltung_geometrie, geomstation
        )
        if basis is None:
            return None

        anschlusspunkt, _nx, _ny = basis
        zielseite = self._seitfaktor_aus_uhrposition(uhr, richtung)

        # In Bestandsprojekten kommen sowohl M150-Stationen ab
        # Inspektionsstart als auch QKan-Urstationen ab Geometrieende vor. Alle
        # äquivalenten Varianten werden nur für den Dublettenabgleich
        # zugelassen; neu gespeichert wird ausschließlich ``urstation``.
        stationskandidaten = {
            round(float(urstation), 3),
            round(float(station), 3),
            round(float(max(0.0, laenge - station)), 3),
            round(float(geomstation), 3),
        }

        for objekt in a_layer.getFeatures():
            if "haltnam" in feldnamen:
                objekt_haltnam = self._als_text(objekt["haltnam"])
                if (
                    objekt_haltnam
                    and objekt_haltnam != self._als_text(haltnam)
                ):
                    continue

            station_passt = self._bca_station_passt_ueber_attribute(
                objekt, feldnamen, stationskandidaten
            )

            if not station_passt and a_layer.isSpatial():
                station_passt = self._bca_geometrie_trifft_anschlusspunkt(
                    objekt.geometry(),
                    anschlusspunkt,
                )

            if not station_passt:
                continue

            objekt_seite = self._bca_objekt_seite_bestimmen(
                objekt,
                feldnamen,
                richtung,
                haltung_geometrie,
                station,
            )

            # Eine Leitung auf der gegenüberliegenden Seite blockiert die
            # Erzeugung nicht.
            if objekt_seite is not None and objekt_seite != zielseite:
                continue

            # Wenn die Seite nicht bestimmbar ist, blocken wir nur bei
            # eindeutiger Positionsnähe. Das verhindert Dubletten bei
            # unvollständigen Bestandsdaten, ohne die Gegenseite zu sperren,
            # sobald die Seite aus Attributen oder Geometrie bestimmbar ist.
            return objekt

        return None

    def _bca_objekt_ist_auto_bca(
        self, objekt: QgsFeature, feldnamen: List[str]
    ) -> bool:
        """Prüft, ob ein vorhandenes Objekt ein automatisch erzeugter BCA ist.
        """
        if "anschlusstyp" in feldnamen:
            if self._als_text(objekt["anschlusstyp"]).upper() == "BCA":
                return True
        if "kommentar" in feldnamen:
            kommentar = self._als_text(objekt["kommentar"]).lower()
            if "automatisch aus bca" in kommentar:
                return True
        return False

    def _bca_anschlussleitungen_erzeugen(
        self,
        xml_root: XmlElement,
        a_layer: Optional[QgsVectorLayer],
        h_layer: Optional[QgsVectorLayer],
    ) -> None:
        """Erzeugt oder aktualisiert kurze Anschlussleitungen aus BCA-Schäden.

        Pro HZ-Datensatz mit HZ002=BCA werden HZ001 als Station, HZ003 als
        Nennweite und HZ006 als Uhrlage interpretiert. Eine vorhandene manuell
        gepflegte HA-Leitung an gleicher Station und Seite verhindert eine
        Dublette, wird aber nicht überschrieben. Nur zuvor automatisch aus BCA
        erzeugte Objekte dürfen durch einen erneuten Import aktualisiert
        werden.

        :param xml_root: Wurzelelement des M150-Dokuments.
        :param a_layer: Layer der Anschlussleitungen.
        :param h_layer: Layer der Haltungen.
        """
        if not a_layer:
            self._log_hinzufuegen(
                "⚠ BCA-Anschlüsse nicht erzeugt: Layer 'HA-Leitungen' fehlt"
            )
            return
        if not h_layer:
            self._log_hinzufuegen(
                "⚠ BCA-Anschlüsse nicht erzeugt: Layer 'Haltungen' fehlt"
            )
            return

        self._bearbeitung_starten(a_layer)
        feldnamen = self._feldnamen_lesen(a_layer)
        erzeugt = 0
        aktualisiert = 0
        erkannt = 0
        uebersprungen = 0
        verwendete_neue_namen = set()

        for hg in xml_root.findall("HG"):
            if not self._ist_haltung_hg_fuer_zustand(hg):
                continue

            haltnam = self._als_text(hg.findtext("HG001"))
            if not haltnam:
                haltnam = self._als_text(hg.findtext("HG002"))
            if not haltnam:
                uebersprungen += 1
                self._log_hinzufuegen("⚠ BCA ohne Haltungsname übersprungen")
                continue

            haltung_objekt = self._haltung_feature_finden(h_layer, haltnam)
            if haltung_objekt is None:
                uebersprungen += 1
                self._log_hinzufuegen(
                    f"⚠ BCA für Haltung '{haltnam}' übersprungen: "
                    "Haltung nicht im Layer gefunden"
                )
                continue
            haltung_geometrie = haltung_objekt.geometry()
            if haltung_geometrie is None or haltung_geometrie.isEmpty():
                uebersprungen += 1
                self._log_hinzufuegen(
                    f"⚠ BCA für Haltung '{haltnam}' übersprungen: "
                    "Haltung ohne Geometrie"
                )
                continue

            for hi in hg.findall("HI"):
                richtung, _bezugspunkt = (
                    self._untersuchungsrichtung_und_bezugspunkt_lesen(hi)
                )
                if richtung is None:
                    uebersprungen += 1
                    self._log_hinzufuegen(
                        f"⚠ BCA für Haltung '{haltnam}' ohne gültige "
                        "HI101-Untersuchungsrichtung übersprungen"
                    )
                    continue

                bca_liste = []
                for hz in hi.findall("HZ"):
                    # Der Zustandskode steht in HZ002. Seine fachliche
                    # Bedeutung ergibt sich aus dem in HI005 gewählten
                    # Kodiersystem, nicht aus der M150-Felddefinition selbst.
                    if self._als_text(hz.findtext("HZ002")).upper() != "BCA":
                        continue
                    station = self._zahl_lesen(hz.findtext("HZ001"))
                    if station is None:
                        uebersprungen += 1
                        self._log_hinzufuegen(
                            f"⚠ BCA für Haltung '{haltnam}' ohne Station "
                            "übersprungen"
                        )
                        continue
                    bca_liste.append((station, hz))

                for station, hz in sorted(
                    bca_liste, key=lambda eintrag: eintrag[0]
                ):
                    # Für den BCA-Code wird Quantifizierung 1 (HZ003) als DN
                    # verwendet; HZ006 liefert die Lage am Rohrumfang.
                    dn = self._zahl_lesen(hz.findtext("HZ003"))
                    uhr = self._uhrposition_als_int(hz.findtext("HZ006"))
                    laenge = self.BCA_STANDARDLAENGE_M
                    urstation = self._bca_urstation_fuer_qkan(
                        station, richtung, haltung_geometrie
                    )
                    geometrie = self._bca_stummelgeometrie_erzeugen(
                        haltung_geometrie, station, richtung, uhr, laenge
                    )
                    if geometrie is None:
                        uebersprungen += 1
                        self._log_hinzufuegen(
                            f"⚠ BCA für Haltung '{haltnam}' bei Station "
                            f"{station:.2f} ohne Geometrie übersprungen"
                        )
                        continue

                    objekt = self._bca_anschluss_match_finden(
                        a_layer,
                        haltnam,
                        urstation,
                        uhr,
                        richtung,
                        haltung_geometrie,
                        station,
                    )

                    leitnam = (
                        self._als_text(objekt["leitnam"])
                        if objekt is not None and "leitnam" in feldnamen
                        else ""
                    )
                    if not leitnam:
                        leitnam = self._bca_naechsten_leitnam_erzeugen(
                            haltnam,
                            verwendete_neue_namen,
                        )
                        if not leitnam:
                            uebersprungen += 1
                            self._log_hinzufuegen(
                                f"⚠ BCA für Haltung '{haltnam}' "
                                "übersprungen: keine freie Anschlussleitungs-"
                                "Nummer von _01 bis _99"
                            )
                            continue

                    kommentar = (
                        "Automatisch aus BCA erzeugt: "
                        f"Station {station:.3f} m, "
                        f"Richtung {richtung}, "
                        f"Uhrlage {uhr if uhr is not None else ''}, "
                        f"DN {dn if dn is not None else ''}"
                    )

                    attribute = {
                        "leitnam": leitnam,
                        "haltnam": haltnam,
                        "urstation": urstation,
                        "schoben": self._nullify(hg.findtext("HG003")),
                        "schunten": None,
                        "hoehe": dn,
                        "breite": dn,
                        "durchm": dn,
                        "laenge": laenge,
                        "profilnam": self._profil_aus_m150_lesen("DN"),
                        "entwart": self._m150_entwart_zu_qkan(
                            hg.findtext("HG302"), None
                        ),
                        "anschlusstyp": "BCA",
                        "lageanschluss": uhr,
                        "kommentar": kommentar,
                    }

                    if objekt is None:
                        neues_objekt = QgsFeature(a_layer.fields())
                        if a_layer.isSpatial():
                            neues_objekt.setGeometry(geometrie)
                        for feld, wert in attribute.items():
                            if feld in feldnamen:
                                neues_objekt[feld] = self._nullify(wert)
                        if not a_layer.addFeature(neues_objekt):
                            uebersprungen += 1
                            self._log_hinzufuegen(
                                f"✖ BCA-Anschluss '{leitnam}' konnte nicht "
                                "neu angelegt werden"
                            )
                            continue
                        self._import_objekt_registrieren(
                            "anschlussleitungen",
                            ("leitnam",),
                            attribute,
                            neues_objekt,
                        )
                        verwendete_neue_namen.add(leitnam)
                        erzeugt += 1
                        self._log_hinzufuegen(
                            f"➕ BCA-Anschluss '{leitnam}' aus Haltung "
                            f"'{haltnam}', Station {station:.2f} m erzeugt"
                        )
                        continue

                    aenderungen: List[str] = []
                    # Bei einem Positionsabgleich den vorhandenen leitnam
                    # beibehalten.
                    objekt_leitnam = (
                        self._als_text(objekt["leitnam"])
                        if "leitnam" in feldnamen
                        else ""
                    )
                    if not self._bca_objekt_ist_auto_bca(objekt, feldnamen):
                        erkannt += 1
                        self._log_hinzufuegen(
                            f"↔ BCA bei Haltung '{haltnam}', Station "
                            f"{station:.2f} m, Uhrlage "
                            f"{uhr if uhr is not None else ''}: "
                            "bestehende HA-Leitung auf gleicher Seite "
                            "erkannt – "
                            "kein neues Objekt erzeugt"
                        )
                        continue

                    if objekt_leitnam and objekt_leitnam != leitnam:
                        attribute.pop("leitnam", None)
                    for feld, wert in attribute.items():
                        self._attribut_sicher_aendern(
                            objekt, feld, wert, aenderungen
                        )

                    if a_layer.isSpatial():
                        alte_geometrie = objekt.geometry()
                        if not self._geometrie_gleich_fuer_import(
                            alte_geometrie, geometrie
                        ):
                            objekt.setGeometry(geometrie)
                            aenderungen.append("Geometrie aktualisiert")

                    if aenderungen:
                        if not a_layer.updateFeature(objekt):
                            uebersprungen += 1
                            self._log_hinzufuegen(
                                "✖ BCA-Anschluss "
                                f"'{objekt_leitnam or leitnam}' "
                                "konnte nicht aktualisiert werden"
                            )
                            continue
                        aktualisiert += 1
                        self._log_hinzufuegen(
                            f"✎ BCA-Anschluss '{objekt_leitnam or leitnam}': "
                            + "; ".join(aenderungen)
                        )
                    else:
                        erkannt += 1

        self._log_hinzufuegen(
            "BCA-Anschlüsse: "
            f"neu={erzeugt}, aktualisiert={aktualisiert}, "
            f"erkannt={erkannt}, übersprungen={uebersprungen}"
        )

    def _import_anschlussleitungen(
        self,
        xml_root: XmlElement,
        a_layer: Optional[QgsVectorLayer],
        h_layer: Optional[QgsVectorLayer],
    ) -> None:
        """Importiert Stammobjekte für Anschlussleitungen.

        :param xml_root: Wurzelelement des M150-Dokuments.
        :param a_layer: Ziel-Layer der Anschlussleitungen.
        :param h_layer: Haltungs-Layer für die Zuordnung und Stationierung.
        """
        if not a_layer:
            self._log_hinzufuegen("⚠ Layer 'HA-Leitungen' nicht gefunden")
            return

        self._bearbeitung_starten(a_layer)
        feldnamen = self._feldnamen_lesen(a_layer)

        for hg in xml_root.findall("HG"):
            # Nach M150-Referenztabelle 108 kennzeichnet HG313=B eine
            # Anschlussleitung. Ihre Zusatzfelder stehen in HG005-HG012.
            hg313 = self._als_text(hg.findtext("HG313")).upper()
            if not hg313:
                continue
            if hg313 != "B":
                continue

            leitnam = self._anschluss_leitnam_lesen(hg)
            if not leitnam:
                hg001 = self._als_text(hg.findtext("HG001"))
                self._log_hinzufuegen(
                    f"⚠ Anschlussleitung zu Haltung '{hg001}' ohne HG011 "
                    "übersprungen"
                )
                continue

            linienpunkte = self._linienpunkte_aus_go_lesen(hg)
            if len(linienpunkte) < 2:
                self._log_hinzufuegen(
                    f"⚠ Anschlussleitung '{leitnam}' ohne ausreichende "
                    "Geometrie übersprungen"
                )
                continue

            startpunkt = linienpunkte[0]
            endpunkt = linienpunkte[-1]
            geometrie = QgsGeometry.fromPolyline(
                [QgsPoint(p.x(), p.y()) for p in linienpunkte]
            )

            haltnam = self._haltung_name_aus_anschluss_hg_lesen(hg)
            # Ist die fachliche Elternhaltung nicht angegeben, dient nur die
            # Geometrie als Kompatibilitätsrückfall. Zuerst wird das gemäß
            # Fließrichtung letzte Leitungsende geprüft.
            if not haltnam:
                haltnam = self._naechsten_haltungsnamen_finden(
                    endpunkt, h_layer
                )
            if not haltnam:
                haltnam = self._naechsten_haltungsnamen_finden(
                    startpunkt, h_layer
                )

            urstation = self._zahl_lesen(hg.findtext("HG007"))
            # HG007 ist die Stationierung im übergeordneten Objekt. Fehlt sie,
            # wird der Leitungsendpunkt auf die gefundene Haltung projiziert.
            if urstation is None:
                urstation = self._station_auf_haltung_berechnen(
                    endpunkt, h_layer, haltnam
                )

            # HG003/HG004 sind Knoten der Elternhaltung und werden nicht
            # als Endknoten der Anschlussleitung übernommen.
            schunten = None

            gp_elemente = hg.findall("GO/GP")
            sohleoben = (
                self._zahl_ohne_null(
                    gp_elemente[0].findtext("GP007")
                )
                if gp_elemente
                else None
            )
            sohleunten = (
                self._zahl_ohne_null(
                    gp_elemente[-1].findtext("GP007")
                )
                if gp_elemente
                else None
            )

            attribute = {
                "leitnam": leitnam,
                "haltnam": haltnam,
                "urstation": urstation,
                "lageanschluss": self._ganzzahl_lesen(
                    hg.findtext("HG009")
                ),
                "schoben": None,
                "schunten": schunten,
                "baujahr": self._ganzzahl_ohne_null(hg.findtext("HG303")),
                "material": self._material_aus_m150_lesen(
                    hg.findtext("HG304"), "Material"
                ),
                "profilnam": self._profil_aus_m150_lesen(hg.findtext("HG305")),
                "profilauskleidung": self._profilauskleidung_aus_m150_lesen(
                    hg.findtext("HG308")
                ),
                "innenmaterial": self._material_aus_m150_lesen(
                    hg.findtext("HG309"), "Innenmaterial"
                ),
                "breite": self._zahl_lesen(hg.findtext("HG306")),
                "hoehe": self._zahl_lesen(hg.findtext("HG307")),
                "durchm": self._zahl_lesen(hg.findtext("HG306")),
                "laenge": self._zahl_lesen(hg.findtext("HG310")),
                "sohleoben": sohleoben,
                "sohleunten": sohleunten,
                "entwart": self._m150_entwart_zu_qkan(
                    hg.findtext("HG302"), None
                ),
                "kommentar": self._nullify(hg.findtext("HG999")),
            }

            objekt = self._anschluss_match_finden(
                a_layer, leitnam
            )

            if objekt is None:
                neues_objekt = QgsFeature(a_layer.fields())
                if geometrie is not None and a_layer.isSpatial():
                    neues_objekt.setGeometry(geometrie)
                for feld, wert in attribute.items():
                    if feld in feldnamen:
                        neues_objekt[feld] = self._nullify(wert)
                if not a_layer.addFeature(neues_objekt):
                    self._log_hinzufuegen(
                        f"✖ Anschlussleitung '{leitnam}' konnte nicht neu "
                        "angelegt werden"
                    )
                    continue
                self._import_objekt_registrieren(
                    "anschlussleitungen",
                    ("leitnam",),
                    attribute,
                    neues_objekt,
                )
                self._log_hinzufuegen(
                    f"➕ Anschlussleitung '{leitnam}' neu angelegt"
                )
                continue

            aenderungen: List[str] = []
            # Netzbeziehungen werden beim Aktualisieren nicht aus einer
            # unsicheren geometrischen Rückfallzuordnung überschrieben.
            geschuetzte_felder = {"haltnam", "schoben", "schunten"}
            for feld, wert in attribute.items():
                if feld in geschuetzte_felder:
                    continue
                self._attribut_sicher_aendern(objekt, feld, wert, aenderungen)

            if geometrie is not None and a_layer.isSpatial():
                alte_geometrie = objekt.geometry()
                if not self._geometrie_gleich_fuer_import(
                    alte_geometrie, geometrie
                ):
                    objekt.setGeometry(geometrie)
                    aenderungen.append("Geometrie aktualisiert")

            if aenderungen:
                if not a_layer.updateFeature(objekt):
                    self._log_hinzufuegen(
                        f"✖ Anschlussleitung '{leitnam}' konnte nicht "
                        "aktualisiert werden"
                    )
                    continue
                self._log_hinzufuegen(
                    f"✎ Anschlussleitung '{leitnam}': "
                    + "; ".join(aenderungen)
                )
            else:
                self._log_hinzufuegen(
                    f"✔ Anschlussleitung '{leitnam}' erkannt"
                )

    # Zustandsdaten
    def _import_schacht_zustand(
        self, xml_root: XmlElement
    ) -> set[Tuple[str, ...]]:
        """Importiert Schachtzustände und Einzelschäden.

        Jeder KI-Block wird zu einem QKan-Gesamtzustand; seine KZ-Kinder
        werden als zugehörige Einzelschäden gespeichert. Mehrere Inspektionen
        bleiben getrennt, sofern ihr in QKan verwendeter Schlüssel aus
        Knotenname und Inspektionsdatum verschieden ist.

        :param xml_root: Wurzelelement des M150-Dokuments.
        :return: Schlüssel der Untersuchungen, deren Schadenslinien neu zu
            berechnen sind.
        """
        gesamt_layer = self._layer_holen("schaechte_untersucht")
        einzelschaden_layer = self._layer_holen("untersuchdat_schacht")
        if einzelschaden_layer is None:
            self._log_hinzufuegen(
                "ℹ Layer für Schacht-Einzelschäden nicht gefunden – "
                "nur Gesamtzustand wird importiert"
            )

        importierte_objekte = []
        schadenslinien_schluessel: set[Tuple[str, ...]] = set()

        for kg in xml_root.findall("KG"):
            if self._als_text(kg.findtext("KG305")).upper() != "S":
                continue
            schnam = self._als_text(kg.findtext("KG001"))
            if (
                not schnam
                or schnam.endswith("_START")
                or schnam.endswith("_VIRT")
            ):
                continue

            gp = kg.find("GO/GP")
            punkt = self._punkt_aus_gp_lesen(gp) if gp is not None else None
            geometrie = (
                QgsGeometry.fromPointXY(punkt) if punkt is not None else None
            )

            for ki in kg.findall("KI"):
                kz_elemente = ki.findall("KZ")

                # KI206/207/208 bedeuten Dichtheit/Standsicherheit/
                # Betriebssicherheit. Die abweichende QKan-Reihenfolge
                # max_ZD/max_ZB/max_ZS ist deshalb bewusst 206/208/207.
                attribute = {
                    "schnam": schnam,
                    "id": self._ganzzahl_lesen(ki.findtext("KI003")),
                    "untersuchtag": self._nullify(ki.findtext("KI104")),
                    "untersucher": (
                        self._nullify(ki.findtext("KI111"))
                        or self._nullify(ki.findtext("KI112"))
                    ),
                    "wetter": self._ganzzahl_lesen(ki.findtext("KI106")),
                    "bewertungsart": self._referenz_langtext_fuer_feld(
                        "KI005", ki.findtext("KI005")
                    ) or self._nullify(ki.findtext("KI005")),
                    "bewertungstag": self._nullify(ki.findtext("KI204")),
                    "datenart": "DWA",
                    "max_ZD": self._ganzzahl_lesen(ki.findtext("KI206")),
                    "max_ZB": self._ganzzahl_lesen(ki.findtext("KI208")),
                    "max_ZS": self._ganzzahl_lesen(ki.findtext("KI207")),
                    "kommentar": self._nullify(ki.findtext("KI999")),
                }
                ergebnis = (
                    self._untersuchungsdatensatz_erstellen_oder_aktualisieren(
                        "schaechte_untersucht",
                        gesamt_layer,
                        ["schnam", "untersuchtag"],
                        attribute,
                        geometrie,
                    )
                )
                if ergebnis in ("erstellt", "aktualisiert"):
                    importierte_objekte.append(schnam)
                elif ergebnis == "kein_layer":
                    self._log_hinzufuegen(
                        f"⚠ Kein Layer für Schacht '{schnam}'"
                    )

                if kz_elemente:
                    schadenslinien_schluessel.add(
                        (
                            self._schluesselwert_normalisieren(schnam),
                            self._schluesselwert_normalisieren(
                                attribute["untersuchtag"]
                            ),
                        )
                    )

                for nummer, kz in enumerate(kz_elemente, start=1):
                    # KZ besitzt keine technische Schadens-ID. Die stabile
                    # XML-Reihenfolge bildet daher die QKan-ID innerhalb der
                    # durch Objekt und Inspektionsdatum bestimmten Inspektion.
                    einzelschaden_attribute = {
                        "untersuchsch": schnam,
                        "id": nummer,
                        "untersuchtag": self._nullify(ki.findtext("KI104")),
                        # Video gehört zur KI-Inspektion, Bild und Zähler zum
                        # einzelnen KZ-Zustand.
                        "videozaehler": self._nullify(kz.findtext("KZ008")),
                        "timecode": self._nullify(kz.findtext("KZ008")),
                        "kuerzel": self._nullify(kz.findtext("KZ002")),
                        "langtext": self._nullify(kz.findtext("KZ010")),
                        "kommentar": self._nullify(kz.findtext("KZ999")),
                        "charakt1": self._nullify(kz.findtext("KZ014")),
                        "charakt2": self._nullify(kz.findtext("KZ015")),
                        "quantnr1": self._zahl_lesen(kz.findtext("KZ003")),
                        "quantnr2": self._zahl_lesen(kz.findtext("KZ004")),
                        "streckenschaden": self._nullify(kz.findtext("KZ005")),
                        "pos_von": self._ganzzahl_lesen(kz.findtext("KZ006")),
                        "pos_bis": self._ganzzahl_lesen(kz.findtext("KZ007")),
                        "vertikale_lage": self._zahl_lesen(
                            kz.findtext("KZ001")
                        ),
                        "bereich": self._nullify(kz.findtext("KZ013")),
                        "foto_dateiname": self._nullify(kz.findtext("KZ009")),
                        "film_dateiname": self._nullify(ki.findtext("KI116")),
                        # KI114 wird derzeit bewusst nicht in QKan gespeichert:
                        # untersuchdat_schacht.filmtyp ist ein Integer-Feld,
                        # M150 liefert hier Referenzcodes wie "HD".
                        "ZD": self._ganzzahl_lesen(kz.findtext("KZ206")),
                        "ZB": self._ganzzahl_lesen(kz.findtext("KZ208")),
                        "ZS": self._ganzzahl_lesen(kz.findtext("KZ207")),
                    }
                    self._untersuchungsdatensatz_erstellen_oder_aktualisieren(
                        "untersuchdat_schacht",
                        einzelschaden_layer,
                        ["untersuchsch", "untersuchtag", "id"],
                        einzelschaden_attribute,
                        None,
                    )

        for schnam in sorted(set(importierte_objekte)):
            self._log_hinzufuegen(
                f"✔ Zustandsdaten importiert für Schacht '{schnam}'"
            )

        return schadenslinien_schluessel

    def _import_haltungs_zustand(
        self, xml_root: XmlElement
    ) -> set[Tuple[str, ...]]:
        """Importiert Haltungszustände und Einzelschäden.

        Ein HI-Block entspricht einer QKan-Untersuchung; die unmittelbar
        darunter liegenden HZ-Blöcke sind deren Einzelschäden. Diese
        Eltern-Kind-Zuordnung ist für mehrere Inspektionen je Haltung
        entscheidend. QKan identifiziert sie hier über Haltungsname und
        Inspektionsdatum.

        :param xml_root: Wurzelelement des M150-Dokuments.
        :return: Schlüssel der Untersuchungen, deren Schadenslinien neu zu
            berechnen sind.
        """
        gesamt_layer = self._layer_holen("haltungen_untersucht")
        einzelschaden_layer = self._layer_holen("untersuchdat_haltung")

        importierte_objekte = []
        schadenslinien_schluessel: set[Tuple[str, ...]] = set()

        for hg in xml_root.findall("HG"):
            if not self._ist_haltung_hg_fuer_zustand(hg):
                continue

            haltnam = self._als_text(hg.findtext("HG001"))
            if not haltnam:
                haltnam = self._als_text(hg.findtext("HG002"))
            if not haltnam:
                continue

            linienpunkte = self._linienpunkte_aus_go_lesen(hg)
            geometrie = (
                QgsGeometry.fromPolyline(
                    [QgsPoint(p.x(), p.y()) for p in linienpunkte]
                )
                if len(linienpunkte) >= 2
                else None
            )

            for hi in hg.findall("HI"):
                richtung, bezugspunkt = (
                    self._untersuchungsrichtung_und_bezugspunkt_lesen(hi)
                )
                if richtung is None:
                    self._log_hinzufuegen(
                        f"⚠ Haltung '{haltnam}' ohne gültige HI101-"
                        "Untersuchungsrichtung: Daten werden importiert; "
                        "richtungsabhängige Geometrie wird nicht erzeugt"
                    )

                hz_elemente = hi.findall("HZ")

                # HI206/207/208 werden fachlich als Dichtheit,
                # Standsicherheit und Betriebssicherheit auf QKan abgebildet.
                attribute = {
                    "haltnam": haltnam,
                    "schoben": self._nullify(hg.findtext("HG003")),
                    "schunten": self._nullify(hg.findtext("HG004")),
                    "breite": self._zahl_lesen(hg.findtext("HG306")),
                    "hoehe": self._zahl_lesen(hg.findtext("HG307")),
                    "durchm": self._zahl_lesen(hg.findtext("HG306")),
                    "laenge": self._zahl_lesen(hg.findtext("HG310")),
                    "id": self._ganzzahl_lesen(hi.findtext("HI003")),
                    "untersuchtag": self._nullify(hi.findtext("HI104")),
                    "untersucher": self._nullify(hi.findtext("HI112")),
                    "untersuchrichtung": richtung,
                    "bezugspunkt": bezugspunkt,
                    "wetter": self._ganzzahl_lesen(hi.findtext("HI106")),
                    "bewertungsart": self._referenz_langtext_fuer_feld(
                        "HI005", hi.findtext("HI005")
                    ) or self._nullify(hi.findtext("HI005")),
                    "bewertungstag": self._nullify(hi.findtext("HI204")),
                    "datenart": "DWA",
                    "max_ZD": self._ganzzahl_lesen(hi.findtext("HI206")),
                    "max_ZB": self._ganzzahl_lesen(hi.findtext("HI208")),
                    "max_ZS": self._ganzzahl_lesen(hi.findtext("HI207")),
                    "kommentar": self._nullify(hi.findtext("HI999")),
                }
                ergebnis = (
                    self._untersuchungsdatensatz_erstellen_oder_aktualisieren(
                        "haltungen_untersucht",
                        gesamt_layer,
                        ["haltnam", "untersuchtag"],
                        attribute,
                        geometrie,
                    )
                )
                if ergebnis in ("erstellt", "aktualisiert"):
                    importierte_objekte.append(haltnam)
                elif ergebnis == "kein_layer":
                    self._log_hinzufuegen(
                        f"⚠ Kein Layer für Haltung '{haltnam}'"
                    )

                if hz_elemente:
                    schadenslinien_schluessel.add(
                        (
                            self._schluesselwert_normalisieren(haltnam),
                            self._schluesselwert_normalisieren(
                                attribute["untersuchtag"]
                            ),
                        )
                    )

                for nummer, hz in enumerate(hz_elemente, start=1):
                    # M150 stellt keine eigene HZ-ID bereit. Die Reihenfolge
                    # innerhalb des aktuellen HI-Blocks wird als QKan-ID
                    # verwendet und macht einen Wiederholungsimport stabil.
                    streckenschaden, streckenschaden_lfdnr = (
                        self._streckenschaden_hz_aufteilen(
                            hz.findtext("HZ005")
                        )
                    )
                    einzelschaden_attribute = {
                        "untersuchhal": haltnam,
                        "id": nummer,
                        "untersuchtag": self._nullify(hi.findtext("HI104")),
                        "untersuchrichtung": richtung,
                        "schoben": self._nullify(hg.findtext("HG003")),
                        "schunten": self._nullify(hg.findtext("HG004")),
                        # HI116 gilt für die gesamte Inspektion; HZ008/HZ009
                        # verweisen auf die konkrete Stelle im Video bzw. Bild.
                        "videozaehler": self._nullify(hz.findtext("HZ008")),
                        "timecode": self._nullify(hz.findtext("HZ008")),
                        "station": self._zahl_lesen(hz.findtext("HZ001")),
                        "kuerzel": self._nullify(hz.findtext("HZ002")),
                        "langtext": self._nullify(hz.findtext("HZ010")),
                        "kommentar": self._nullify(hz.findtext("HZ999")),
                        "charakt1": self._nullify(hz.findtext("HZ014")),
                        "charakt2": self._nullify(hz.findtext("HZ015")),
                        "quantnr1": self._zahl_lesen(hz.findtext("HZ003")),
                        "quantnr2": self._zahl_lesen(hz.findtext("HZ004")),
                        "streckenschaden": streckenschaden,
                        "streckenschaden_lfdnr": streckenschaden_lfdnr,
                        "pos_von": self._ganzzahl_lesen(hz.findtext("HZ006")),
                        "pos_bis": self._ganzzahl_lesen(hz.findtext("HZ007")),
                        "foto_dateiname": self._nullify(hz.findtext("HZ009")),
                        "film_dateiname": self._nullify(hi.findtext("HI116")),
                        "ZD": self._ganzzahl_lesen(hz.findtext("HZ206")),
                        "ZB": self._ganzzahl_lesen(hz.findtext("HZ208")),
                        "ZS": self._ganzzahl_lesen(hz.findtext("HZ207")),
                    }
                    self._untersuchungsdatensatz_erstellen_oder_aktualisieren(
                        "untersuchdat_haltung",
                        einzelschaden_layer,
                        ["untersuchhal", "untersuchtag", "id"],
                        einzelschaden_attribute,
                        None,
                    )

        for haltnam in sorted(set(importierte_objekte)):
            self._log_hinzufuegen(
                f"✔ Zustandsdaten importiert für Haltung '{haltnam}'"
            )

        return schadenslinien_schluessel

    def _import_anschluss_zustand(
        self, xml_root: XmlElement
    ) -> set[Tuple[str, ...]]:
        """Importiert Anschlussleitungszustände und Einzelschäden.

        DWA-M 150 verwendet auch für Anschlussleitungen die Hierarchie
        HG/HI/HZ; HG313=B und HG011 bestimmen dabei das QKan-Zielobjekt.

        :param xml_root: Wurzelelement des M150-Dokuments.
        :return: Schlüssel der Untersuchungen, deren Schadenslinien neu zu
            berechnen sind.
        """
        gesamt_layer = self._layer_holen(
            "anschlussleitungen_untersucht"
        )
        einzelschaden_layer = self._layer_holen(
            "untersuchdat_anschlussleitung"
        )
        if einzelschaden_layer is None:
            self._log_hinzufuegen(
                "ℹ Layer für HA-Einzelschäden nicht gefunden – "
                "nur Gesamtzustand wird importiert"
            )

        importierte_objekte = []
        schadenslinien_schluessel: set[Tuple[str, ...]] = set()

        for hg in xml_root.findall("HG"):
            if not self._ist_anschluss_hg_fuer_zustand(hg):
                continue

            leitnam = self._anschluss_leitnam_lesen(hg)
            if not leitnam:
                continue

            linienpunkte = self._linienpunkte_aus_go_lesen(hg)
            geometrie = (
                QgsGeometry.fromPolyline(
                    [QgsPoint(p.x(), p.y()) for p in linienpunkte]
                )
                if len(linienpunkte) >= 2
                else None
            )

            for hi in hg.findall("HI"):
                richtung, bezugspunkt = (
                    self._untersuchungsrichtung_und_bezugspunkt_lesen(hi)
                )
                if richtung is None:
                    self._log_hinzufuegen(
                        f"⚠ Anschlussleitung '{leitnam}' ohne gültige HI101-"
                        "Untersuchungsrichtung: Daten werden importiert; "
                        "richtungsabhängige Geometrie wird nicht erzeugt"
                    )

                hz_elemente = hi.findall("HZ")

                # Die Gesamtbewertung steht am HI-Block, nicht an einem
                # einzelnen HZ-Schaden.
                attribute = {
                    "leitnam": leitnam,
                    "schoben": None,
                    "schunten": None,
                    "breite": self._zahl_lesen(hg.findtext("HG306")),
                    "hoehe": self._zahl_lesen(hg.findtext("HG307")),
                    "durchm": self._zahl_lesen(hg.findtext("HG306")),
                    "laenge": self._zahl_lesen(hg.findtext("HG310")),
                    "id": self._ganzzahl_lesen(hi.findtext("HI003")),
                    "untersuchtag": self._nullify(hi.findtext("HI104")),
                    "untersucher": self._nullify(hi.findtext("HI112")),
                    "untersuchrichtung": richtung,
                    "bezugspunkt": bezugspunkt,
                    "wetter": self._ganzzahl_lesen(hi.findtext("HI106")),
                    "bewertungsart": self._referenz_langtext_fuer_feld(
                        "HI005", hi.findtext("HI005")
                    ) or self._nullify(hi.findtext("HI005")),
                    "bewertungstag": self._nullify(hi.findtext("HI204")),
                    "datenart": "DWA",
                    "max_ZD": self._ganzzahl_lesen(hi.findtext("HI206")),
                    "max_ZB": self._ganzzahl_lesen(hi.findtext("HI208")),
                    "max_ZS": self._ganzzahl_lesen(hi.findtext("HI207")),
                    "kommentar": self._nullify(hi.findtext("HI999")),
                }
                ergebnis = (
                    self._untersuchungsdatensatz_erstellen_oder_aktualisieren(
                        "anschlussleitungen_untersucht",
                        gesamt_layer,
                        ["leitnam", "untersuchtag"],
                        attribute,
                        geometrie,
                    )
                )
                if ergebnis in ("erstellt", "aktualisiert"):
                    importierte_objekte.append(leitnam)
                elif ergebnis == "kein_layer":
                    self._log_hinzufuegen(
                        f"⚠ Kein Layer für Anschlussleitung '{leitnam}'"
                    )

                if hz_elemente:
                    schadenslinien_schluessel.add(
                        (
                            self._schluesselwert_normalisieren(leitnam),
                            self._schluesselwert_normalisieren(
                                attribute["untersuchtag"]
                            ),
                        )
                    )

                for nummer, hz in enumerate(hz_elemente, start=1):
                    # Die laufende Nummer ersetzt die in M150 nicht vorhandene
                    # technische HZ-ID innerhalb dieser Inspektion.
                    streckenschaden, streckenschaden_lfdnr = (
                        self._streckenschaden_hz_aufteilen(
                            hz.findtext("HZ005")
                        )
                    )
                    einzelschaden_attribute = {
                        "untersuchleit": leitnam,
                        "id": nummer,
                        "untersuchtag": self._nullify(hi.findtext("HI104")),
                        "untersuchrichtung": richtung,
                        "schoben": None,
                        "schunten": None,
                        "videozaehler": self._nullify(hz.findtext("HZ008")),
                        "timecode": self._nullify(hz.findtext("HZ008")),
                        "station": self._zahl_lesen(hz.findtext("HZ001")),
                        "kuerzel": self._nullify(hz.findtext("HZ002")),
                        "langtext": self._nullify(hz.findtext("HZ010")),
                        "kommentar": self._nullify(hz.findtext("HZ999")),
                        "charakt1": self._nullify(hz.findtext("HZ014")),
                        "charakt2": self._nullify(hz.findtext("HZ015")),
                        "quantnr1": self._zahl_lesen(hz.findtext("HZ003")),
                        "quantnr2": self._zahl_lesen(hz.findtext("HZ004")),
                        "streckenschaden": streckenschaden,
                        "streckenschaden_lfdnr": streckenschaden_lfdnr,
                        "pos_von": self._ganzzahl_lesen(hz.findtext("HZ006")),
                        "pos_bis": self._ganzzahl_lesen(hz.findtext("HZ007")),
                        "foto_dateiname": self._nullify(hz.findtext("HZ009")),
                        "film_dateiname": self._nullify(hi.findtext("HI116")),
                        "ZD": self._ganzzahl_lesen(hz.findtext("HZ206")),
                        "ZB": self._ganzzahl_lesen(hz.findtext("HZ208")),
                        "ZS": self._ganzzahl_lesen(hz.findtext("HZ207")),
                    }
                    self._untersuchungsdatensatz_erstellen_oder_aktualisieren(
                        "untersuchdat_anschlussleitung",
                        einzelschaden_layer,
                        ["untersuchleit", "untersuchtag", "id"],
                        einzelschaden_attribute,
                        None,
                    )

        for leitnam in sorted(set(importierte_objekte)):
            self._log_hinzufuegen(
                f"✔ Zustandsdaten importiert für Anschlussleitung '{leitnam}'"
            )

        return schadenslinien_schluessel

    # Importsteuerung
    def _xml_import(self) -> None:
        """Prüft Datei und Importauswahl, lädt die YAML-Referenzen und Indizes,
        führt die gewählten Stamm-, Zustands- und BCA-Importe aus und speichert
        anschließend alle beteiligten Layer.
        """
        xml_pfad = self.tf_import.text().strip()
        if not xml_pfad:
            QMessageBox.warning(
                self, "M150-Import", "Bitte zuerst eine XML-Datei auswählen."
            )
            return

        if not os.path.exists(xml_pfad):
            QMessageBox.warning(
                self, "M150-Import", "Die ausgewählte Datei existiert nicht."
            )
            return

        stammdaten_importieren = self.cb_stammdaten.isChecked()
        inspektionsdaten_importieren = self.cb_inspektionsdaten.isChecked()
        bca_erzeugen = (
            hasattr(self, "cb_bca_erzeugen")
            and self.cb_bca_erzeugen.isChecked()
        )

        if (
            not stammdaten_importieren
            and not inspektionsdaten_importieren
            and not bca_erzeugen
        ):
            QMessageBox.warning(
                self,
                "M150-Import",
                "Bitte Stammdaten und/oder Inspektionsdaten auswählen.",
            )
            return

        self._log_hinzufuegen("")
        self._log_hinzufuegen("----- Neuer M150-Import -----")
        self._log_hinzufuegen(
            f"Stammdaten aktiv: {'Ja' if stammdaten_importieren else 'Nein'}"
        )
        self._log_hinzufuegen(
            "Inspektionsdaten aktiv: "
            f"{'Ja' if inspektionsdaten_importieren else 'Nein'}"
        )
        self._log_hinzufuegen(
            "BCA-Anschlüsse erzeugen: "
            f"{'Ja' if bca_erzeugen else 'Nein'}"
        )
        self._log_hinzufuegen("------------------------")

        try:
            # XML-Struktur und Sicherheitsgrenzen werden vollständig geprüft,
            # bevor ein QGIS-Layer in den Bearbeitungsmodus wechselt.
            xml_root = m150_xml_sicher_lesen(xml_pfad)
        except (OSError, ValueError) as err:
            self._log_hinzufuegen(
                f"✖ XML-Datei konnte nicht gelesen werden: {err}"
            )
            QMessageBox.critical(
                self,
                "M150-Import",
                "Die XML-Datei konnte nicht sicher gelesen werden. "
                "Der Import wurde vor Änderungen abgebrochen.\n\n"
                f"{err}",
            )
            return

        erforderliche_tabellen = set()
        if stammdaten_importieren:
            erforderliche_tabellen.update(
                {
                    "haltungen",
                    "schaechte",
                    "anschlussleitungen",
                    "anschlussschaechte",
                }
            )
        if bca_erzeugen:
            erforderliche_tabellen.update(
                {"haltungen", "anschlussleitungen"}
            )
        if inspektionsdaten_importieren:
            erforderliche_tabellen.update(
                {
                    "schaechte_untersucht",
                    "untersuchdat_schacht",
                    "haltungen_untersucht",
                    "untersuchdat_haltung",
                    "anschlussleitungen_untersucht",
                    "untersuchdat_anschlussleitung",
                }
            )

        self._datenquelle = datenquelle_waehlen(
            QgsProject.instance(),
            erforderliche_tabellen,
            self,
            "M150-Import – QKan-Datenquelle",
        )
        if self._datenquelle is None:
            meldung = (
                "Es wurde keine vollständige QKan-Datenquelle für die "
                "gewählten Importoptionen gefunden oder die Auswahl wurde "
                "abgebrochen. Benötigt werden die exakt benannten QKan-"
                "Layer aus einer gemeinsamen SpatiaLite- oder PostgreSQL-"
                "Datenquelle."
            )
            QMessageBox.critical(self, "M150-Import", meldung)
            return

        h_layer = self._layer_holen("haltungen")
        s_layer = self._layer_holen("schaechte")
        a_layer = self._layer_holen("anschlussleitungen")
        as_layer = self._layer_holen("anschlussschaechte")

        layer_nach_tabelle = {
            "haltungen": h_layer,
            "schaechte": s_layer,
            "anschlussleitungen": a_layer,
            "anschlussschaechte": as_layer,
            "schaechte_untersucht": self._layer_holen(
                "schaechte_untersucht"
            ),
            "untersuchdat_schacht": self._layer_holen(
                "untersuchdat_schacht"
            ),
            "haltungen_untersucht": self._layer_holen(
                "haltungen_untersucht"
            ),
            "untersuchdat_haltung": self._layer_holen(
                "untersuchdat_haltung"
            ),
            "anschlussleitungen_untersucht": self._layer_holen(
                "anschlussleitungen_untersucht"
            ),
            "untersuchdat_anschlussleitung": self._layer_holen(
                "untersuchdat_anschlussleitung"
            ),
        }
        import_layer = list(layer_nach_tabelle.values())

        try:
            with datenbank_oeffnen(self._datenquelle) as db_qkan:
                if not db_qkan.connected:
                    QMessageBox.critical(
                        self,
                        "M150-Import",
                        "Die gewählte QKan-Datenquelle konnte nicht geöffnet "
                        "werden.",
                    )
                    return
                db_qkan.loadmodule("inspektion")
                self._yaml_importdaten_laden(db_qkan)
                self._xml_referenztabellen_laden(xml_root)
        except Exception as err:
            self._log_hinzufuegen(
                f"✖ YAML-Importabfragen fehlgeschlagen: {err}"
            )
            QMessageBox.critical(
                self,
                "M150-Import",
                "Die Importdaten konnten nicht über die YAML-Abfragen geladen "
                "werden. Der Import wurde vor Änderungen abgebrochen.\n\n"
                f"{err}",
            )
            return

        for tabelle, layer in layer_nach_tabelle.items():
            # Bereits ungespeicherte QGIS-Änderungen haben Vorrang vor den aus
            # der Datenbank geladenen Indizes und werden in den Abgleich
            # einbezogen. Anschlussschächte werden bewusst räumlich sowie
            # über Haltung/Urstation zugeordnet und besitzen daher keinen
            # einfachen Namensindex.
            if tabelle in self.IMPORT_INDEXE:
                self._import_editpuffer_uebernehmen(tabelle, layer)

        self._log_hinzufuegen("Import gestartet")
        self._m150_metadaten_loggen(xml_root)

        if stammdaten_importieren:
            # Knoten und Haltungen werden vor Anschlussleitungen importiert,
            # damit deren Namen und Geometrien für die Zuordnung verfügbar
            # sind.
            self._log_hinzufuegen("Stammdatenimport gestartet")
            self._import_schaechte(xml_root, s_layer)
            self._import_haltungen(xml_root, h_layer)
            self._import_anschlussleitungen(xml_root, a_layer, h_layer)
            self._import_anschlussschaechte(
                xml_root, as_layer, a_layer
            )
            self._log_hinzufuegen("Stammdatenimport abgeschlossen")
        else:
            self._log_hinzufuegen("Stammdatenimport übersprungen")

        if bca_erzeugen:
            # Die BCA-Erzeugung benötigt nur HG/HI/HZ und kann unabhängig vom
            # vollständigen Zustandsimport aktiviert werden.
            self._log_hinzufuegen("BCA-Anschlusserzeugung gestartet")
            self._bca_anschlussleitungen_erzeugen(
                xml_root, a_layer, h_layer
            )
            self._log_hinzufuegen("BCA-Anschlusserzeugung abgeschlossen")
        else:
            self._log_hinzufuegen("BCA-Anschlusserzeugung übersprungen")

        if inspektionsdaten_importieren:
            # Erst nach dem Import aller Gesamt- und Einzeldaten werden die
            # QKan-spezifischen Beschriftungsgeometrien gemeinsam berechnet.
            self._log_hinzufuegen("Inspektionsdatenimport gestartet")
            schacht_schluessel = self._import_schacht_zustand(xml_root)
            haltungs_schluessel = self._import_haltungs_zustand(xml_root)
            anschluss_schluessel = self._import_anschluss_zustand(xml_root)
            self._schadenslinien_aktualisieren(
                schacht_schluessel,
                haltungs_schluessel,
                anschluss_schluessel,
            )
            self._log_hinzufuegen("Inspektionsdatenimport abgeschlossen")
        else:
            self._log_hinzufuegen("Inspektionsdatenimport übersprungen")

        for layer in import_layer:
            self._layer_speichern(layer)

        self._log_hinzufuegen("Import abgeschlossen")
        QMessageBox.information(
            self, "M150-Import", "M150-Import erfolgreich abgeschlossen."
        )


def run_m150_import(iface: QgisInterface) -> None:
    """Öffnet den M150-Importdialog und startet ihn modal."""
    dlg = BefahrungImportDialog(iface)
    dlg.exec_()
