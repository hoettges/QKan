# planauskunft/berichte/haltungsbericht.py
"""
Haltungsbericht (A4 hoch) als QGIS-Drucklayout:

  Seite 1   Kopf, Stammdaten, Befahrung, Zustand (ZD/ZS/ZB/gesamt), optional Bestandsplan
  Seite 2   Haltungsgrafik (Vektor)
  ab S. 3   Schadensliste (Tabelle, bei Bedarf über mehrere Seiten)
  danach    Schadensfotos (2 je Seite)

Mehrere Objekte werden wahlweise in eine Sammel-PDF (ein Layout, Objekte nacheinander)
oder je Objekt in eine eigene PDF geschrieben. Ein Wechsel auf Querformat o.ä. ist über
die Konstanten SEITE/RAND möglich.
"""

import os
import math
import datetime

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutItemPage, QgsLayoutItemLabel, QgsLayoutItemPicture,
    QgsLayoutItemMap, QgsLayoutItemShape, QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes,
    QgsLayoutMeasurement, QgsFillSymbol, QgsLineSymbol, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFeatureRequest, QgsExpression,
    QgsSingleSymbolRenderer, QgsRectangle,
)

from . import schrift
from .kompat import versuche
from .daten import ZK_FARBEN, ZK_TEXT, OBJEKTARTEN, text, datum_text
from .grafik import zeichne_haltungsgrafik, befund_text, uhrlage

SEITE = (210.0, 297.0)
RAND_L, RAND_R, RAND_O, RAND_U = 25.0, 10.0, 10.0, 10.0
X0, X1 = RAND_L, SEITE[0] - RAND_R
BREITE = X1 - X0
KOPF_H = 16.0
FUSS_H = 7.0
Y_INHALT = RAND_O + KOPF_H + 3.0
Y_ENDE = SEITE[1] - RAND_U - FUSS_H - 2.0

FARBE_TITEL = QColor("#0f3b63")
FARBE_GRAU = QColor("#555555")
FARBE_HELL = QColor("#eef2f7")

MASSSTAEBE = [100, 200, 250, 500, 750, 1000, 1500, 2000, 2500, 5000]


# ======================================================================
# Bausteine (mit Seitenangabe)
# ======================================================================

class _Seiten:
    """Verwaltet die Seiten eines Layouts; die erste (leere) Seite wird zuerst verwendet."""

    def __init__(self, layout):
        self.layout = layout
        self.benutzt = 0

    def neu(self):
        pc = self.layout.pageCollection()
        if self.benutzt < pc.pageCount():
            n = self.benutzt
        else:
            seite = QgsLayoutItemPage(self.layout)
            seite.setPageSize(QgsLayoutSize(SEITE[0], SEITE[1], QgsUnitTypes.LayoutMillimeters))
            pc.addPage(seite)
            n = pc.pageCount() - 1
        self.benutzt = n + 1
        return n


def _setze(item, seite, x, y, w=None, h=None):
    if w is not None:
        item.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    item.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters), True, False, seite)


def _text(layout, seite, x, y, w, h, inhalt, pt=8, fett=False, farbe=QColor("black"),
          halign=Qt.AlignLeft, valign=Qt.AlignVCenter, hintergrund=None):
    lbl = QgsLayoutItemLabel(layout)
    lbl.setText(inhalt)
    schrift._schrift(lbl, pt, fett, farbe)
    lbl.setHAlign(halign)
    lbl.setVAlign(valign)
    lbl.setMarginX(1.0)
    lbl.setMarginY(0.3)
    if hintergrund is not None:
        lbl.setBackgroundEnabled(True)
        lbl.setBackgroundColor(QColor(hintergrund))
    layout.addLayoutItem(lbl)
    _setze(lbl, seite, x, y, w, h)
    return lbl


def _rechteck(layout, seite, x, y, w, h, fuellung=None, linie="0,0,0,255", staerke=0.25):
    shp = QgsLayoutItemShape(layout)
    versuche(shp.setShapeType, "QgsLayoutItemShape.Shape.Rectangle", "QgsLayoutItemShape.Rectangle")
    f = QColor(fuellung) if fuellung else None
    shp.setSymbol(QgsFillSymbol.createSimple({
        "color": f"{f.red()},{f.green()},{f.blue()},255" if f else "255,255,255,0",
        "style": "solid" if f else "no",
        "outline_color": linie, "outline_width": str(staerke), "outline_width_unit": "MM",
        "outline_style": "solid" if staerke else "no",
    }))
    layout.addLayoutItem(shp)
    _setze(shp, seite, x, y, w, h)
    return shp


def _linie(layout, seite, x, y, w, farbe="#0f3b63", staerke=0.4):
    return _rechteck(layout, seite, x, y, w, staerke, fuellung=farbe, linie=farbe, staerke=0)


def _ueberschrift(layout, seite, y, inhalt):
    _text(layout, seite, X0, y, BREITE, 6, inhalt, 10, True, FARBE_TITEL, valign=Qt.AlignBottom)
    _linie(layout, seite, X0, y + 6.2, BREITE, "#0f3b63", 0.3)
    return y + 8.0


def _schrift_fuer_zk(k):
    return QColor("white") if k in (0, 2, 4) else QColor("black")


# ======================================================================
# Kopf / Fuß
# ======================================================================

def _kopf(layout, seite, od, opt):
    y = RAND_O
    logo = opt.get("logo") or ""
    x_text = X0
    if logo and os.path.isfile(logo):
        bild = QgsLayoutItemPicture(layout)
        bild.setPicturePath(logo)
        versuche(bild.setResizeMode, "QgsLayoutItemPicture.ResizeMode.Zoom", "QgsLayoutItemPicture.Zoom")
        layout.addLayoutItem(bild)
        _setze(bild, seite, X0, y, 32, KOPF_H - 2)
        x_text = X0 + 35
    _text(layout, seite, x_text, y, 90, 7, opt.get("auftraggeber", ""), 9, True, valign=Qt.AlignBottom)
    _text(layout, seite, x_text, y + 7, 90, 7, opt.get("dienststelle", ""), 7, farbe=FARBE_GRAU, valign=Qt.AlignTop)
    titel = OBJEKTARTEN[od.art].get("titel", "Bericht")
    _text(layout, seite, X1 - 75, y, 75, 8, titel, 13, True, FARBE_TITEL, halign=Qt.AlignRight,
          valign=Qt.AlignBottom)
    _text(layout, seite, X1 - 75, y + 8, 75, 7, od.name, 10, True, halign=Qt.AlignRight, valign=Qt.AlignTop)
    _linie(layout, seite, X0, RAND_O + KOPF_H, BREITE, "#0f3b63", 0.5)


def _fuss(layout, seite, od):
    y = SEITE[1] - RAND_U - FUSS_H
    _linie(layout, seite, X0, y, BREITE, "#9aa0a6", 0.2)
    bef = datum_text(od.befahrung) if od.befahrung is not None else "keine Befahrung"
    _text(layout, seite, X0, y + 0.5, BREITE * 0.7, FUSS_H - 1,
          f"{od.art} {od.name}  ·  Befahrung {bef}  ·  erstellt am {datetime.date.today():%d.%m.%Y}",
          6, farbe=FARBE_GRAU)
    return _text(layout, seite, X0 + BREITE * 0.6, y + 0.5, BREITE * 0.4, FUSS_H - 1, "", 6,
                 farbe=FARBE_GRAU, halign=Qt.AlignRight)


# ======================================================================
# Seite 1: Stammdaten, Befahrung, Zustand, Bestandsplan
# ======================================================================

def _feldgruppe(layout, seite, x, y, breite, paare, beschr_b=30.0, zeile=5.2):
    for i, (beschr, wert) in enumerate(paare):
        yy = y + i * zeile
        if i % 2 == 0:
            _rechteck(layout, seite, x, yy, breite, zeile, fuellung="#f4f6f9", linie="0,0,0,0", staerke=0)
        _text(layout, seite, x, yy, beschr_b, zeile, beschr, 6.5, farbe=FARBE_GRAU)
        _text(layout, seite, x + beschr_b, yy, breite - beschr_b, zeile, wert or "–", 8)
    return y + len(paare) * zeile


def _seite_stammdaten(layout, seiten, od, opt):
    s = seiten.neu()
    _kopf(layout, s, od, opt)
    fuss = [_fuss(layout, s, od)]
    y = _ueberschrift(layout, s, Y_INHALT, "Stammdaten")
    halb = (BREITE - 5) / 2
    if od.ist_schacht:
        return _stammdaten_schacht(layout, s, od, opt, y, halb, fuss)
    links = [("Bezeichnung", od.name), ("Straße", od.s("strasse")),
             ("Schacht oben", od.s("schoben")), ("Schacht unten", od.s("schunten")),
             ("Entwässerungsart", od.s("entwart")), ("Strakat-ID", od.s("strakatid"))]
    laenge = od.s("laenge")
    rechts = [("Material", od.s("material")), ("Profil / Abmessung", " ".join(
                  t for t in (od.s("profilnam"), od.dimension) if t)),
              ("Länge", f"{float(laenge.replace(',', '.')):.2f} m" if _ist_zahl(laenge) else laenge),
              ("Gefälle", od.gefaelle), ("Baujahr", od.s("baujahr")),
              ("Eigentum", od.s("eigentum", "eigentuemer"))]
    e1 = _feldgruppe(layout, s, X0, y, halb, links)
    e2 = _feldgruppe(layout, s, X0 + halb + 5, y, halb, rechts)
    y = max(e1, e2) + 4

    return _befahrung_zustand_plan(layout, s, od, opt, y, halb, fuss)


def _stammdaten_schacht(layout, s, od, opt, y, halb, fuss):
    tiefe = od.tiefe
    links = [("Bezeichnung", od.name), ("Straße", od.s("strasse")),
             ("Entwässerungsart", od.s("entwart")), ("Schachttyp", od.s("schachttyp", "knotentyp")),
             ("Strakat-ID", od.s("strakatid")), ("Eigentum", od.s("eigentum", "eigentuemer"))]
    rechts = [("Deckelhöhe", f"{od.s('deckelhoehe')} m NHN" if od.s("deckelhoehe") else ""),
              ("Sohlhöhe", f"{od.s('sohlhoehe')} m NHN" if od.s("sohlhoehe") else ""),
              ("Tiefe", f"{tiefe:.2f} m".replace(".", ",") if tiefe else ""),
              ("Durchmesser", od.dimension), ("Material", od.s("material")), ("Baujahr", od.s("baujahr"))]
    e1 = _feldgruppe(layout, s, X0, y, halb, links)
    e2 = _feldgruppe(layout, s, X0 + halb + 5, y, halb, rechts)
    return _befahrung_zustand_plan(layout, s, od, opt, max(e1, e2) + 4, halb, fuss)


def _befahrung_zustand_plan(layout, s, od, opt, y, halb, fuss):
    y = _ueberschrift(layout, s, y, "Befahrung")
    bef = [("Datum", datum_text(od.befahrung) if od.befahrung is not None else "keine Befahrung vorhanden"),
           ("Untersucher", od.s("untersucher", "firma", "auftragnehmer")),
           ("Auftrag", od.s("auftragsbezeichnung", "auftrag", "auftragsnr")),
           ("Inspektionsrichtung", od.inspektionsrichtung)]
    bef2 = [("Wetter", od.s("wetter")), ("Bewertung", od.s("bewertungsart")),
            ("Weitere Befahrungen", ", ".join(datum_text(b) for b in od.befahrungen if b != od.befahrung)[:120]),
            ("Befunde", str(len(od.befunde)))]
    e1 = _feldgruppe(layout, s, X0, y, halb, bef)
    e2 = _feldgruppe(layout, s, X0 + halb + 5, y, halb, bef2)
    y = max(e1, e2) + 4

    y = _ueberschrift(layout, s, y, "Zustand (DWA-M 149-3)")
    zd, zs, zb, ges = od.zustandsklassen()
    kb = (BREITE - 3 * 3) / 4
    for i, (beschr, k) in enumerate((("Dichtheit ZD", zd), ("Standsicherheit ZS", zs),
                                     ("Betriebssicherheit ZB", zb), ("Gesamt", ges))):
        x = X0 + i * (kb + 3)
        farbe = ZK_FARBEN.get(k, "#cccccc") if k is not None else "#cccccc"
        _rechteck(layout, s, x, y, kb, 13, fuellung=farbe, linie="0,0,0,0", staerke=0)
        sf = _schrift_fuer_zk(k) if k is not None else QColor("black")
        _text(layout, s, x, y + 0.5, kb, 5, beschr, 6.5, farbe=sf, halign=Qt.AlignHCenter)
        _text(layout, s, x, y + 5, kb, 7.5, f"ZK {k}" if k is not None else "–", 12, True, sf,
              halign=Qt.AlignHCenter)
    y += 15
    if ges is not None:
        _text(layout, s, X0, y, BREITE, 5, ZK_TEXT.get(ges, ""), 8, True)
        y += 6
    y += 2

    return fuss


def _ist_zahl(t):
    try:
        float(str(t).replace(",", "."))
        return True
    except (TypeError, ValueError):
        return False


def _seite_grafik(layout, seiten, od, opt, temp):
    s = seiten.neu()
    _kopf(layout, s, od, opt)
    fuss = [_fuss(layout, s, od)]
    y = _ueberschrift(layout, s, Y_INHALT, "Schachtgrafik" if od.ist_schacht else "Haltungsgrafik")
    hoehe = Y_ENDE - y
    pfad = os.path.join(temp, f"grafik_{abs(hash((od.art, od.name, str(od.befahrung))))}.svg")
    zeichne_haltungsgrafik(pfad, od, BREITE, hoehe)
    bild = QgsLayoutItemPicture(layout)
    bild.setPicturePath(pfad)
    versuche(bild.setResizeMode, "QgsLayoutItemPicture.ResizeMode.Zoom", "QgsLayoutItemPicture.Zoom")
    versuche(bild.setPictureAnchor, "QgsLayoutItem.ReferencePoint.UpperLeft", "QgsLayoutItem.UpperLeft")
    layout.addLayoutItem(bild)
    _setze(bild, s, X0, y, BREITE, hoehe)
    return fuss


ZELLRAND = 0.8          # Innenabstand je Zellseite (mm)
GITTER = 0.15
_FEST = [("Nr.", 6.5), ("Station", 12.0), ("Code", 15.0), ("Beschreibung", None), ("Lage", 15.0),
         ("ZD", 7.0), ("ZS", 7.0), ("ZB", 7.0)]


def _spalten():
    """Spaltenbreiten so, dass Tabelle inkl. Innenabständen und Gitter genau BREITE breit ist."""
    n = len(_FEST)
    nutzbar = BREITE - n * 2 * ZELLRAND - (n + 1) * GITTER - 0.5
    fest = sum(b for _, b in _FEST if b)
    return [(t, b if b else nutzbar - fest) for t, b in _FEST]


SPALTEN = _spalten()


def _zeilen_schaetzen(txt, breite_mm, pt=6.5):
    zeichen = max(6, int(breite_mm / (pt * 0.3528 * 0.52)))
    zeilen = 0
    for teil in str(txt).split("\n"):
        zeilen += max(1, math.ceil(len(teil) / zeichen))
    return zeilen


def _schadensliste(layout, seiten, od, opt):
    from qgis.core import QgsLayoutItemManualTable, QgsTableCell, QgsLayoutTableColumn, QgsLayoutFrame
    zeilen = []
    for i, b in enumerate(od.befunde, 1):
        kopf, lang = befund_text(b)
        code = b.kuerzel + "".join(x for x in (b.wert("charakt1"), b.wert("charakt2")) if x)
        zeilen.append([str(i), f"{b.station:.2f}".replace(".", ",") if b.station is not None else "",
                       code, lang, uhrlage(b), b.zd, b.zs, b.zb])

    fuesse = []
    if not zeilen:
        s = seiten.neu()
        _kopf(layout, s, od, opt)
        fuesse.append(_fuss(layout, s, od))
        y = _ueberschrift(layout, s, Y_INHALT, "Schadensliste")
        _text(layout, s, X0, y, BREITE, 8, "Keine Befunde vorhanden.", 8, farbe=FARBE_GRAU)
        return fuesse

    # Zeilen auf Seiten verteilen (Höhe grob abschätzen)
    zeilen_h, rand, kopf_h = 2.75, 1.8, 6.0
    verfuegbar = Y_ENDE - (Y_INHALT + 8.0) - kopf_h - 2 - (5 if od.ist_schacht else 0)
    stuecke, aktuell, hoehe = [], [], 0.0
    for z in zeilen:
        n = max(_zeilen_schaetzen(z[3], SPALTEN[3][1]), _zeilen_schaetzen(z[2], SPALTEN[2][1]))
        h = n * zeilen_h + rand
        if aktuell and hoehe + h > verfuegbar:
            stuecke.append(aktuell)
            aktuell, hoehe = [], 0.0
        aktuell.append(z)
        hoehe += h
    if aktuell:
        stuecke.append(aktuell)

    fmt_kopf = schrift._textformat(6.5, True, QColor("white"))
    fmt_inhalt = schrift._textformat(6.5)
    for nr, stueck in enumerate(stuecke):
        s = seiten.neu()
        _kopf(layout, s, od, opt)
        fuesse.append(_fuss(layout, s, od))
        titel = "Schadensliste" + (f" (Fortsetzung {nr + 1}/{len(stuecke)})" if len(stuecke) > 1 and nr else "")
        y = _ueberschrift(layout, s, Y_INHALT, titel)

        tab = QgsLayoutItemManualTable.create(layout)
        layout.addMultiFrame(tab)
        inhalt = []
        for z in stueck:
            zeile = []
            for j, wert in enumerate(z):
                if j in (5, 6, 7):
                    zelle = QgsTableCell(str(wert) if wert is not None else "")
                    if wert is not None:
                        zelle.setBackgroundColor(QColor(ZK_FARBEN.get(wert, "#ffffff")))
                        zelle.setTextFormat(schrift._textformat(6.5, True, _schrift_fuer_zk(wert)))
                    try:
                        zelle.setHorizontalAlignment(Qt.AlignHCenter)
                    except Exception:
                        pass
                else:
                    zelle = QgsTableCell(wert)
                zeile.append(zelle)
            inhalt.append(zeile)
        tab.setTableContents(inhalt)
        spalten = []
        for titel_sp, breite in SPALTEN:
            if titel_sp == "Station" and od.ist_schacht:
                titel_sp = "Höhe*"
            c = QgsLayoutTableColumn()
            c.setHeading(titel_sp)
            c.setWidth(breite)
            spalten.append(c)
        tab.setHeaders(spalten)
        tab.setIncludeTableHeader(True)
        try:
            tab.setColumnWidths([float(b) for _, b in SPALTEN])
        except Exception:
            pass
        versuche(tab.setWrapBehavior, "QgsLayoutTable.WrapBehavior.WrapText", "QgsLayoutTable.WrapText")
        try:
            tab.setHeaderTextFormat(fmt_kopf)
            tab.setContentTextFormat(fmt_inhalt)
        except Exception:
            pass
        tab.setCellMargin(ZELLRAND)
        tab.setGridStrokeWidth(GITTER)
        tab.setGridColor(QColor("#9aa0a6"))
        try:
            tab.setBackgroundColor(QColor("white"))
        except Exception:
            pass
        try:
            from qgis.core import QgsLayoutTableStyle
            stil = QgsLayoutTableStyle()
            stil.enabled = True
            stil.cellBackgroundColor = QColor("#0f3b63")
            versuche(lambda w: tab.setCellStyle(w, stil),
                     "QgsLayoutTable.CellStyleGroup.HeaderRow", "QgsLayoutTable.HeaderRow")
            zebra = QgsLayoutTableStyle()
            zebra.enabled = True
            zebra.cellBackgroundColor = QColor("#f4f6f9")
            versuche(lambda w: tab.setCellStyle(w, zebra),
                     "QgsLayoutTable.CellStyleGroup.EvenRows", "QgsLayoutTable.EvenRows")
        except Exception:
            pass
        rahmen = QgsLayoutFrame(layout, tab)
        rahmen.attemptResize(QgsLayoutSize(BREITE, Y_ENDE - y - (5 if od.ist_schacht else 0),
                                           QgsUnitTypes.LayoutMillimeters))
        rahmen.attemptMove(QgsLayoutPoint(X0, y, QgsUnitTypes.LayoutMillimeters), True, False, s)
        tab.addFrame(rahmen)
        tab.recalculateFrameSizes()
        if od.ist_schacht and nr == len(stuecke) - 1:
            _text(layout, s, X0, Y_ENDE - 4, BREITE, 4, "* Höhe über der Schachtsohle in m (0 = Sohle)",
                  6, farbe=FARBE_GRAU)
    return fuesse


def _fotoseiten(layout, seiten, od, opt):
    ordner = opt.get("bildordner") or ""
    fotos = []
    for i, b in enumerate(od.befunde, 1):
        p = opt["fotopfad"](b.wert("foto_dateiname"), ordner)
        if p:
            fotos.append((i, b, p))
    vorhanden = {pfad for _, _, pfad in fotos}
    for eintrag in od.zusatz.get("fotos", []):
        pfad = opt["fotopfad"](eintrag.get("datei"), ordner)
        if pfad and pfad not in vorhanden:
            fotos.append((None, None, pfad))
            vorhanden.add(pfad)
    fuesse = []
    if not fotos:
        return fuesse, 0
    je_seite = 2
    platz = Y_ENDE - (Y_INHALT + 8.0)
    slot = platz / je_seite
    for start in range(0, len(fotos), je_seite):
        s = seiten.neu()
        _kopf(layout, s, od, opt)
        fuesse.append(_fuss(layout, s, od))
        y = _ueberschrift(layout, s, Y_INHALT, "Schadensfotos")
        for k, (nr, b, p) in enumerate(fotos[start:start + je_seite]):
            yy = y + k * slot
            bild = QgsLayoutItemPicture(layout)
            bild.setPicturePath(p)
            versuche(bild.setResizeMode, "QgsLayoutItemPicture.ResizeMode.Zoom", "QgsLayoutItemPicture.Zoom")
            bild.setFrameEnabled(True)
            layout.addLayoutItem(bild)
            _setze(bild, s, X0, yy, BREITE, slot - 13)
            if b is None:
                _text(layout, s, X0, yy + slot - 12, BREITE, 6, os.path.basename(p), 8)
                continue
            kopf, lang = befund_text(b)
            farbe = ZK_FARBEN.get(b.klasse, "#cccccc") if b.klasse is not None else "#cccccc"
            _rechteck(layout, s, X0, yy + slot - 12, 9, 5, fuellung=farbe, linie="0,0,0,0", staerke=0)
            _text(layout, s, X0, yy + slot - 12, 9, 5, str(nr), 7, True,
                  _schrift_fuer_zk(b.klasse) if b.klasse is not None else QColor("black"), halign=Qt.AlignHCenter)
            _text(layout, s, X0 + 10, yy + slot - 12, BREITE - 10, 5, kopf, 8, True)
            _text(layout, s, X0 + 10, yy + slot - 7.2, BREITE - 10, 5, lang, 7, farbe=FARBE_GRAU, valign=Qt.AlignTop)
    return fuesse, len(fotos)


# ======================================================================
# Bericht erzeugen
# ======================================================================

def baue_bericht(layout, seiten, od, opt, temp):
    """Hängt den Bericht eines Objekts an das Layout an."""
    fuesse = _seite_stammdaten(layout, seiten, od, opt)
    if opt.get("grafik", True):
        fuesse += _seite_grafik(layout, seiten, od, opt, temp)
    if opt.get("liste", True):
        fuesse += _schadensliste(layout, seiten, od, opt)
    if opt.get("fotos", True):
        f, _ = _fotoseiten(layout, seiten, od, opt)
        fuesse += f
    for i, lbl in enumerate(fuesse, 1):
        lbl.setText(f"Seite {i} von {len(fuesse)}")
    return len(fuesse)


def _neues_layout(name):
    layout = QgsPrintLayout(QgsProject.instance())
    layout.initializeDefaults()
    layout.setName(name)
    layout.pageCollection().page(0).setPageSize(QgsLayoutSize(SEITE[0], SEITE[1], QgsUnitTypes.LayoutMillimeters))
    return layout


