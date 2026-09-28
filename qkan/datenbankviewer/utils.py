"""
utils.py - Hilfsfunktionen für QGIS-Plugin Datenbankviewer
Enthält allgemeine Utility-Funktionen und Konstanten.
"""

# =========================================================
# Importe
# =========================================================

import os
import json
from collections import defaultdict

from PyQt6.QtWidgets import QTableWidget, QWidget
from PyQt6.QtCore import Qt


# =========================================================
# Hilfspfade
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "json")


# =========================================================
# Konstanten
# =========================================================

TABLENNAMES = {
    "Haltungen": "untersuchdathaltung",
    "Schächte": "untersuchdatschacht",
    "GAL": "untersuchdatanschlussleitung",
}

COLUMNS = {
    "Haltungen": [
        "station",
        "kuerzel",
        "langtext",
        "kommentar",
        "charakt1",
        "charakt2",
        "quantnr1",
        "quantnr2",
        "posvon",
        "posbis",
        "zd",
        "zs",
        "zb",
        "bandnr",
        "untersuchtag",
        "videozaehler",
        "fotodateiname",
        "filmdateiname",
    ],
    "Schächte": [
        "vertikalelage",
        "kuerzel",
        "langtext",
        "kommentar",
        "charakt1",
        "charakt2",
        "quantnr1",
        "quantnr2",
        "posvon",
        "posbis",
        "zd",
        "zs",
        "zb",
        "bandnr",
        "untersuchtag",
        "videozaehler",
        "fotodateiname",
    ],
    "GAL": [
        "station",
        "kuerzel",
        "langtext",
        "kommentar",
        "charakt1",
        "charakt2",
        "quantnr1",
        "quantnr2",
        "posvon",
        "posbis",
        "zd",
        "zs",
        "zb",
        "bandnr",
        "untersuchtag",
        "videozaehler",
        "fotodateiname",
        "filmdateiname",
    ],
}

FARBEN = {
    0: "red",
    1: "yellow",
    2: "blue",
    3: "lightgreen",
    4: "green",
}

SPALTEN_OHNE_COLLATE = [
    "station",
    "vertikalelage",
    "posvon",
    "posbis",
    "quantnr1",
    "quantnr2",
    "videozaehler",
    "bandnr",
]

DOCUMENT_BASE_PATH = os.path.join(BASE_DIR, "..", "documents")
PANORAMA_PATH = os.path.join(BASE_DIR, "..", "panorama")
PANORAMA_SI_PATH = os.path.join(BASE_DIR, "..", "panorama_si")

HEADER_JSON_PATHS = {
    "haltungen": os.path.join(JSON_DIR, "selected_items_haltungen.json"),
    "schaechte": os.path.join(JSON_DIR, "selected_items_schaechte.json"),
    "gal": os.path.join(JSON_DIR, "selected_items_gal.json"),
}


# =========================================================
# Widget-Hilfsfunktionen
# =========================================================

def findinnertablewidget(widget):
    """
    Findet rekursiv ein QTableWidget in einer Widget-Hierarchie.

    Args:
        widget: Start-QWidget

    Returns:
        QTableWidget oder None
    """
    if isinstance(widget, QTableWidget):
        return widget

    for childwidget in widget.findChildren(QWidget):
        tablewidget = findinnertablewidget(childwidget)
        if tablewidget:
            return tablewidget

    return None


# =========================================================
# String- / Zahlen-Helfer
# =========================================================

def parsedecimal(string):
    """
    Ersetzt Kommas durch Punkte für Dezimalzahlen
    (deutsche Notation -> englische Notation).

    Args:
        string: Eingabe-String

    Returns:
        String mit Punkten statt Kommas
    """
    return string.replace(",", ".") if string else ""


def safeposition(rowdata):
    """
    Sichere Extraktion einer Positionsnummer für Sortierungen.

    Erwartet die relevante Positionsangabe an Index 1.

    Args:
        rowdata: Liste mit Tabellendaten

    Returns:
        float-Position oder inf bei Fehler
    """
    try:
        posstr = parsedecimal(rowdata[1]) if len(rowdata) > 1 and rowdata[1] else "0"
        return float(posstr)
    except (ValueError, TypeError):
        return float("inf")


# =========================================================
# JSON / Header laden
# =========================================================

def load_headers(tabtype):
    """
    Lädt Header-Konfiguration aus einer lokalen JSON-Datei.

    Args:
        tabtype: 'haltungen', 'schaechte' oder 'gal'

    Returns:
        Dict/List mit Headern oder leeres Dict bei Fehler
    """
    filepath = HEADER_JSON_PATHS.get(tabtype)
    if not filepath or not os.path.exists(filepath):
        print(f"Header-Datei nicht gefunden: {filepath}")
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Fehlerhaftes JSON in Header-Datei {tabtype}: {e}")
        return {}
    except Exception as e:
        print(f"Fehler beim Laden der Header {tabtype}: {e}")
        return {}


# =========================================================
# UI-Helfer
# =========================================================

def clearfields(self):
    """Leert zentrale QLineEdit-/UI-Felder."""
    fields = [
        self.Haltungsname,
        self.Strassenname,
        self.Schacht_oben,
        self.Entwaesserungssystem,
        self.Schacht_unten,
        self.Material,
        self.Laenge,
        self.Gefaelle,
        self.Baujahr,
        self.Dimension,
        self.StrakatID,
    ]

    for field in fields:
        field.clear()


# =========================================================
# Feature-Attribute
# =========================================================

def get_feature_attributes(feature):
    """
    Extrahiert und formatiert Attributwerte aus einem QGIS-Feature.

    Args:
        feature: QgsFeature

    Returns:
        Dict mit formatierten Attributen
    """
    attributes = [
        "haltnam",
        "leitnam",
        "strasse",
        "schoben",
        "entwart",
        "schunten",
        "material",
        "laenge",
        "gefaelle",
        "baujahr",
        "breite",
        "hoehe",
        "strakatid",
        "sohleoben",
        "sohleunten",
        "posvon",
        "posbis",
    ]

    existingattributes = feature.fields().names()
    attributevalues = {}

    for attr in attributes:
        if attr in existingattributes and feature.attribute(attr) is not None:
            attributevalues[attr] = str(feature.attribute(attr))
        else:
            attributevalues[attr] = ""

    # Länge formatieren
    laenge = attributevalues.get("laenge", "")
    try:
        laenge = f"{float(laenge):.2f}"
    except ValueError:
        pass

    # Breite / Höhe formatieren
    breite = attributevalues.get("breite", "")
    hoehe = attributevalues.get("hoehe", "")
    try:
        breite = int(float(breite)) if breite else ""
        hoehe = int(float(hoehe)) if hoehe else ""
    except ValueError:
        breite, hoehe = "", ""

    # Dimension aufbereiten
    if breite == hoehe and breite:
        dimensiontext = str(breite)
    else:
        dimensiontext = f"{breite}x{hoehe}" if breite and hoehe else ""

    # Gefälle ggf. aus Sohlhöhen und Länge neu berechnen
    sohleoben = attributevalues.get("sohleoben", "")
    sohleunten = attributevalues.get("sohleunten", "")
    try:
        sohleoben = float(sohleoben) if sohleoben else None
        sohleunten = float(sohleunten) if sohleunten else None
        laenge_float = float(laenge) if laenge else None

        if sohleoben is not None and sohleunten is not None and laenge_float:
            gefaelle = (sohleoben - sohleunten) / laenge_float * 1000
            attributevalues["gefaelle"] = f"{gefaelle:.1f}"
    except ValueError:
        pass

    attributevalues.update(
        {
            "dimension": dimensiontext,
            "laenge": laenge,
        }
    )

    return attributevalues