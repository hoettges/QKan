# planauskunft/berichte/schachtgrafik.py
"""
Schachtgrafik als Vektorgrafik (SVG), angelehnt an die übliche Schachtaufbau-Zeichnung
(DIN EN 1917 / DIN V 4034-1):

  links oben   Schnitt A–A: Abdeckung, Auflagering, Konus (exzentrisch), Schachtringe,
               Schachtunterteil mit Gerinne/Auftritt; Rohre als Rohrstutzen mit ihrem
               Durchmesser auf der richtigen Höhe; Befunde positionsgetreu an der Wand
  links unten  Draufsicht: Schachtring, Gerinne, Zu-/Abläufe und Anschlüsse in ihrer
               Uhrlage, Befunde als nummerierte Punkte
  rechts       Befundtexte (wie bei der Haltungsgrafik), Führungslinien zur Höhe

Bezüge / Annahmen:
  * Höhen: vertikale_lage = Höhe über der Schachtsohle (m) – 0 = Sohle, größter Wert = Deckel.
    Intern wird daraus die Tiefe unter dem Deckel berechnet (Tiefe = Schachttiefe − Höhe).
  * Uhrlage: Draufsicht im Uhrzeigersinn, 12 Uhr = Hauptablauf
  * Rohre/Anschlüsse: siehe rohre_am_schacht() – DCA/DCG aus der Befahrung, 12 Uhr =
    Hauptablauf, Zu-/Ablauf über Kürzel bzw. Haltungsdaten; die vertikale Lage wird als
    Rohrsohle gezeichnet.
"""

import math

from qgis.PyQt.QtCore import Qt, QRectF, QPointF, QSize, QRect
from qgis.PyQt.QtGui import QPainter, QPen, QColor, QFont, QFontMetricsF, QBrush, QPolygonF, QPainterPath

from .daten import ZK_FARBEN, zahl

E = 10.0                       # Zeicheneinheiten je mm
GRAU_WAND = QColor("#c8c8c8")
GRAU_ROHR = QColor("#dcdcdc")
WASSER = QColor("#cfe3f7")
LINIE = QColor("#222222")


def _font(pt, fett=False):
    f = QFont("Arial")
    f.setPixelSize(max(1, int(round(pt * 0.3528 * E))))
    f.setBold(fett)
    return f


def _uhr(wert):
    z = zahl(wert)
    if z is None:
        return None
    u = int(round(z)) % 12
    return 12 if u == 0 and z > 0 else (u if u else None)


def _dn(wert, standard=150.0):
    z = zahl(wert)
    if not z or z <= 0:
        return standard
    return z * 1000 if z < 10 else z


# ======================================================================
# Rohre zusammenstellen
# ======================================================================

def tiefe_von(od, hoehe):
    """Höhe über Sohle (vertikale_lage) -> Tiefe unter Deckel (m)."""
    t = od.laenge
    if hoehe is None:
        return t
    return t - min(max(hoehe, 0.0), t)


def _dn_aus_text(txt):
    """Dimension aus dem Langtext (z.B. „... Rohrhöhe 300 mm Rohrbreite 300 mm“, „DN 300“,
    „Durchmesser 300 mm“). Bei Höhe und Breite gilt die Breite. Rückgabe mm oder None."""
    import re
    t = str(txt or "")
    werte = {}
    for name, muster in (("breite", r"(?:rohr)?breite\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm|m)?"),
                         ("hoehe", r"(?:rohr)?h(?:ö|oe)he\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm|m)?"),
                         ("dn", r"\bDN\s*[:=]?\s*(\d+)"),
                         ("durchm", r"durchmesser\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm|m)?")):
        m = re.search(muster, t, re.IGNORECASE)
        if m:
            wert = float(m.group(1).replace(",", "."))
            einheit = (m.group(2) if m.lastindex and m.lastindex >= 2 else "mm") or "mm"
            wert *= {"mm": 1, "cm": 10, "m": 1000}.get(einheit.lower(), 1)
            werte[name] = wert
    for name in ("dn", "durchm", "breite", "hoehe"):
        if werte.get(name) and 50 <= werte[name] <= 5000:
            return werte[name]
    m = re.search(r"(\d{2,4})\s*mm", t)
    return float(m.group(1)) if m and 50 <= float(m.group(1)) <= 5000 else None


def _uhr_abstand(a, b):
    d = abs(a - b) % 12
    return min(d, 12 - d)


def rohre_am_schacht(od):
    """Rohre am Schacht: dict(uhr, dn, tiefe (Sohle, m unter Deckel), art, quelle, herkunft).

    Logik (in dieser Reihenfolge):
      1. Rohre aus der Befahrung: DCG (Anschlussleitung) und DCA (Anschluss). DCA und DCG
         mit gleicher Uhrlage und ähnlicher Höhe beschreiben dasselbe Rohr und werden
         zusammengefasst (Daten aus DCG bevorzugt).
      2. Dimension: aus dem Langtext von DCG (Rohrbreite/-höhe, DN, Durchmesser), sonst
         quantnr1, sonst DN der zugeordneten Haltung, sonst DN 150.
      3. Zu-/Ablauf:
         a) 12 Uhr ist immer der Hauptablauf.
         b) DCG-Charakterisierung 2, falls erfasst: A = entwässert in den Schacht (Zulauf),
            B = entwässert aus dem Schacht (Ablauf), C = verschlossen.
         c) Zuordnung zu einer Haltung am Schacht über die Uhrlage (aus der Geometrie,
            max. 1,5 h Abweichung): Schacht = Schacht oben -> Ablauf, = Schacht unten -> Zulauf.
         d) sonst Zulauf (Regelfall).
      4. Haltungen am Schacht, zu denen es kein Rohr in der Befahrung gibt, werden ergänzt.
    """
    tiefe_sohle = od.laenge
    haltungen = [r for r in od.zusatz.get("rohre", []) if r.get("uhr") is not None]

    # 1) Befahrung: DCA/DCG je Rohr zusammenfassen
    gruppen = []
    for b in od.befunde:
        k = b.kuerzel.upper()
        if not (k.startswith("DCA") or k.startswith("DCG")):
            continue
        uhr = _uhr(b.werte.get("pos_von")) or _uhr(b.werte.get("pos_bis"))
        hoehe = b.station
        gruppe = next((g for g in gruppen
                       if g["uhr"] is not None and uhr is not None and _uhr_abstand(g["uhr"], uhr) < 0.5
                       and (g["hoehe"] is None or hoehe is None or abs(g["hoehe"] - hoehe) <= 0.3)), None)
        if gruppe is None:
            gruppe = {"uhr": uhr, "hoehe": hoehe, "dcg": None, "dca": None}
            gruppen.append(gruppe)
        gruppe["dcg" if k.startswith("DCG") else "dca"] = gruppe.get("dcg" if k.startswith("DCG") else "dca") or b
        if gruppe["hoehe"] is None:
            gruppe["hoehe"] = hoehe

    rohre, benutzt = [], set()
    for g in gruppen:
        b = g["dcg"] or g["dca"]
        uhr = g["uhr"]
        # zugeordnete Haltung über die Uhrlage
        haltung = None
        if uhr is not None and haltungen:
            kand = sorted(((i, _uhr_abstand(h["uhr"], uhr)) for i, h in enumerate(haltungen) if i not in benutzt),
                          key=lambda x: x[1])
            if kand and kand[0][1] <= 1.5:
                haltung = haltungen[kand[0][0]]
                benutzt.add(kand[0][0])
        # Dimension
        dn = None
        if g["dcg"] is not None:
            dn = _dn_aus_text(g["dcg"].langtext) or _dn_aus_text(g["dcg"].wert("kommentar"))
        if not dn:
            q = zahl(b.werte.get("quantnr1"))
            dn = (q * 1000 if q and q < 10 else q) if q else None
        if not dn and haltung:
            dn = haltung.get("dn")
        dn = dn or 150.0
        # Zu-/Ablauf
        c2 = (g["dcg"].wert("charakt2") or "").upper() if g["dcg"] is not None else ""
        if uhr == 12:
            art, herkunft = "Hauptablauf", "12 Uhr"
        elif c2 in ("A", "B", "C"):
            art, herkunft = {"A": "Zulauf", "B": "Ablauf", "C": "verschlossen"}[c2], "Kürzel"
        elif haltung is not None:
            art, herkunft = haltung["rolle"], "Haltung"
        else:
            art, herkunft = "Zulauf", "Regelfall"
        rohre.append({"uhr": uhr, "dn": dn, "tiefe": tiefe_von(od, g["hoehe"]), "art": art,
                      "quelle": haltung.get("haltnam", "") if haltung else "", "herkunft": herkunft})

    # 4) Haltungen ohne Gegenstück in der Befahrung ergänzen
    for i, h in enumerate(haltungen):
        if i in benutzt:
            continue
        if any(r["uhr"] is not None and _uhr_abstand(r["uhr"], h["uhr"]) <= 1 for r in rohre):
            continue
        art = "Hauptablauf" if h["uhr"] == 12 else h["rolle"]
        rohre.append({"uhr": h["uhr"], "dn": h.get("dn") or 300.0, "tiefe": tiefe_sohle, "art": art,
                      "quelle": h.get("haltnam", ""), "herkunft": "Haltung"})
    return rohre


MIN_MEHRBREITE = 250.0      # Schacht mind. 250 mm breiter als das größte Rohr
GRENZE_MEHRBREITE = 200.0   # ... wenn das Rohr nur bis zu 200 mm kleiner ist als der Schacht


def schacht_durchmesser(od, rohre=None):
    """Schachtdurchmesser in mm und Hinweis.

    * Spalte durchm der Schachttabelle (Werte < 10 sind Meter: 1 = 1,00 m), sonst 1,00 m.
    * Ist das größte Zu-/Ablaufrohr höchstens 200 mm kleiner als dieser Wert, ist der
      Wert unplausibel (z.B. 1,00 m als Standard aus dem Strakat-Import bei DN 800/1000).
      Dann wird der Schacht mindestens 250 mm breiter als das Rohr angenommen, aber
      mindestens 250 mm breiter als der Tabellenwert; auf 50 mm aufgerundet.
    Rückgabe: (mm, tabellenwert_mm oder None, angenommen: bool)"""
    roh = zahl(od.s("durchm", "durchmesser"))
    tabelle = (roh * 1000 if roh < 10 else roh) if roh and roh > 0 else None
    dn = tabelle or 1000.0
    if rohre is None:
        rohre = rohre_am_schacht(od)
    groesstes = max([r["dn"] for r in rohre if r.get("dn")] + [0.0])
    if groesstes and dn - groesstes <= GRENZE_MEHRBREITE:
        neu = max(groesstes + MIN_MEHRBREITE, dn + MIN_MEHRBREITE)
        neu = math.ceil(neu / 50.0) * 50.0
        return neu, tabelle, True
    return dn, tabelle, False


def durchmesser_text(od, rohre=None):
    mm, tabelle, angenommen = schacht_durchmesser(od, rohre)
    txt = f"{mm / 1000:.2f} m".replace(".", ",")
    if angenommen:
        tab = f"{tabelle / 1000:.2f} m".replace(".", ",") if tabelle else "–"
        txt += f" (angenommen, Tabelle {tab})"
    elif not tabelle:
        txt += " (Standard)"
    return txt


def _haupt_dn(rohre):
    for r in rohre:
        if r["uhr"] == 12:
            return r["dn"]
    return max([r["dn"] for r in rohre] + [300.0])


# ======================================================================
# Zeichnen
# ======================================================================

def zeichne_schachtgrafik(pfad, od, breite_mm=175.0, hoehe_mm=225.0, schrift_pt=6.5, regionen=None):
    from qgis.PyQt.QtSvg import QSvgGenerator
    from .grafik import befund_text, _umbrechen

    W, H = breite_mm * E, hoehe_mm * E
    links_b = W * 0.52                    # Zeichnungsbereich links
    text_x = links_b + 6 * E
    text_b = W - text_x - 1 * E
    legende_h = 7 * E

    tiefe = max(od.laenge, 0.8)
    rohre = rohre_am_schacht(od)
    dn_mm, _, dn_angenommen = schacht_durchmesser(od, rohre)
    dn_schacht = dn_mm / 1000.0                                          # m
    dn_haupt = _haupt_dn(rohre) / 1000.0

    # --- Aufteilung links: Schnitt oben, Draufsicht unten ---
    schnitt_oben = 6 * E
    plan_h = min(links_b * 0.95, (H - legende_h) * 0.40)
    schnitt_h = H - legende_h - plan_h - schnitt_oben - 8 * E
    stutzen = 16 * E                      # Länge der Rohrstutzen im Schnitt
    s = min((schnitt_h - 4 * E) / (tiefe + 0.25),                    # mm je m (in E)
            (links_b - 2 * stutzen - 14 * E) / (dn_schacht + 0.30))
    cx = 9 * E + (links_b - 9 * E) / 2
    y_top = schnitt_oben + 2 * E

    def yd(d):                            # Tiefe (m) -> y
        return y_top + d * s

    R = dn_schacht / 2 * s                # Innenradius
    t = max(0.12 * s, 1.2 * E)            # Wanddicke

    # --- Texte setzen (Schrift ggf. verkleinern) ---
    def texte(pt):
        f1, f2 = _font(pt, True), _font(pt)
        fm1, fm2 = QFontMetricsF(f1), QFontMetricsF(f2)
        zh = fm2.height() * 1.05
        e = []
        for nr, b in enumerate(od.befunde, 1):
            kopf, lang = befund_text(b)
            if b.wert("bereich"):
                lang += f" [Bereich {b.wert('bereich')}]"
            zl = _umbrechen(fm2, lang, text_b - 7 * E)
            e.append((nr, b, f"{nr}.  {kopf}", zl, fm1.height() * 1.05 + len(zl) * zh + 1.2 * E))
        return f1, f2, fm1, fm2, zh, e

    text_oben, text_unten = schnitt_oben, H - legende_h - 2 * E
    pt = schrift_pt
    while True:
        f1, f2, fm1, fm2, zh, eintraege = texte(pt)
        if sum(e[4] for e in eintraege) <= text_unten - text_oben or pt <= 4.6:
            break
        pt -= 0.4
    eintraege.sort(key=lambda e: tiefe_von(od, e[1].station))
    pos, frei = [], text_oben
    for nr, b, kopf, zl, h in eintraege:
        y = max(yd(tiefe_von(od, b.station)) - fm1.ascent() * 0.6, frei)
        pos.append(y)
        frei = y + h
    grenze = text_unten
    for i in range(len(pos) - 1, -1, -1):
        if pos[i] + eintraege[i][4] > grenze:
            pos[i] = grenze - eintraege[i][4]
        grenze = pos[i]
    frei = text_oben
    for i in range(len(pos)):
        pos[i] = max(pos[i], frei)
        frei = pos[i] + eintraege[i][4]
    benoetigt = max(H, frei + legende_h + 2 * E)

    gen = QSvgGenerator()
    gen.setFileName(pfad)
    gen.setResolution(int(25.4 * E))
    gen.setSize(QSize(int(W), int(benoetigt)))
    gen.setViewBox(QRect(0, 0, int(W), int(benoetigt)))
    gen.setTitle(f"Schachtgrafik {od.name}")
    p = QPainter()
    if not p.begin(gen):
        raise RuntimeError("Schachtgrafik konnte nicht erzeugt werden.")
    try:
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setFont(_font(7, True))
        p.setPen(LINIE)
        p.drawText(QRectF(0, 0, links_b, 5 * E), Qt.AlignLeft | Qt.AlignVCenter, "Schnitt A–A")

        marken = _schnitt(p, od, rohre, s, cx, yd, R, t, tiefe, dn_haupt, stutzen, links_b)
        p.setFont(_font(5.2))
        p.setPen(QColor("#333333"))
        p.drawText(QRectF(cx - R, yd(tiefe) + 0.25 * s + 0.8 * E, 2 * R, 3 * E), Qt.AlignCenter,
                   f"Schacht DN {dn_mm:.0f}" + (" (angenommen)" if dn_angenommen else ""))

        # Draufsicht
        plan_y = schnitt_oben + schnitt_h + 6 * E
        p.setFont(_font(7, True))
        p.setPen(LINIE)
        p.drawText(QRectF(0, plan_y - 5 * E, links_b, 5 * E), Qt.AlignLeft | Qt.AlignVCenter, "Draufsicht")
        plan_marken = _draufsicht(p, od, rohre, cx, plan_y + plan_h / 2, plan_h / 2, dn_schacht, dn_haupt)

        # Befunde: Markierung an der Wand, Führungslinie, Text
        for (nr, b, kopf, zl, h), ty in zip(eintraege, pos):
            farbe = QColor(ZK_FARBEN.get(b.klasse, ZK_FARBEN[5])) if b.klasse is not None else QColor("#444444")
            linie = farbe.darker(160) if b.klasse == 5 else farbe
            y = yd(tiefe_von(od, b.station))
            xw = marken["wand_x"](b, y)
            p.setPen(QPen(linie, 0.7 * E))
            p.drawLine(QPointF(xw - 1.4 * E, y), QPointF(xw + 1.4 * E, y))
            p.setPen(QPen(QColor("#9aa0a6"), 0.15 * E))
            mitte = ty + fm1.ascent() * 0.6
            p.drawLine(QPointF(xw + 1.6 * E, y), QPointF(text_x - 4 * E, mitte))
            p.drawLine(QPointF(text_x - 4 * E, mitte), QPointF(text_x - 1 * E, mitte))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(farbe))
            p.drawRect(QRectF(text_x, ty, 4.5 * E, fm1.height()))
            if b.klasse is not None:
                p.setPen(QColor("white") if b.klasse in (0, 2, 4) else QColor("black"))
                p.setFont(_font(max(pt - 0.5, 4), True))
                p.drawText(QRectF(text_x, ty, 4.5 * E, fm1.height()), Qt.AlignCenter, str(b.klasse))
            p.setPen(QColor("#111111"))
            p.setFont(f1)
            p.drawText(QPointF(text_x + 6 * E, ty + fm1.ascent()), kopf)
            p.setFont(f2)
            yy = ty + fm1.height() * 1.05
            for z in zl:
                p.drawText(QPointF(text_x + 6 * E, yy + fm2.ascent()), z)
                yy += zh
            if regionen is not None:
                regionen.append((QRectF(text_x / E, ty / E, (W - text_x) / E, h / E), b))
                regionen.append((QRectF(xw / E - 2.5, y / E - 1.5, 5.0, 3.0), b))
                if nr in plan_marken:
                    px, py = plan_marken[nr]
                    regionen.append((QRectF(px / E - 2.0, py / E - 2.0, 4.0, 4.0), b))

        if not od.befunde:
            p.setPen(QColor("#555555"))
            p.setFont(_font(8))
            p.drawText(QRectF(text_x, schnitt_oben, text_b, 10 * E), Qt.AlignLeft | Qt.AlignVCenter,
                       "Keine Befunde vorhanden.")

        # Legende
        p.setFont(_font(5.5))
        x, yl = 0.0, benoetigt - legende_h + 2 * E
        for k in range(6):
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(ZK_FARBEN[k])))
            p.drawRect(QRectF(x, yl, 3 * E, 3 * E))
            p.setPen(QColor("#333333"))
            p.drawText(QRectF(x + 3.6 * E, yl - 0.5 * E, 20 * E, 4 * E), Qt.AlignLeft | Qt.AlignVCenter, f"ZK {k}")
            x += 14 * E
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(WASSER))
        p.drawRect(QRectF(x, yl, 3 * E, 3 * E))
        p.setPen(QColor("#333333"))
        p.drawText(QRectF(x + 3.6 * E, yl - 0.5 * E, 14 * E, 4 * E), Qt.AlignLeft | Qt.AlignVCenter, "Gerinne")
        x += 16 * E
        p.drawText(QRectF(x, yl - 0.5 * E, W - x, 4 * E), Qt.AlignLeft | Qt.AlignVCenter,
                   "Schematisch · Höhen über Sohle (0 = Sohle) · 12 Uhr = Hauptablauf")
    finally:
        p.end()
    return benoetigt / E


def _schnitt(p, od, rohre, s, cx, yd, R, t, tiefe, dn_haupt, stutzen, links_b):
    """Schnitt A–A durch Hauptablauf (links, 12 Uhr) und Zulaufseite (rechts, 6 Uhr)."""
    # Bauteilhöhen (m); bei flachen Schächten Abdeckplatte statt Konus
    h_abd, h_ring_auf = 0.15, 0.10
    h_unterteil = max(0.8, dn_haupt + 0.45)
    flach = tiefe < h_abd + h_ring_auf + 0.6 + h_unterteil * 0.6
    h_konus = 0.0 if flach else 0.6
    d_konus_oben = h_abd + h_ring_auf
    d_konus_unten = d_konus_oben + (h_konus if not flach else 0.2)
    d_unterteil = max(d_konus_unten, tiefe - h_unterteil)
    oeffnung = min(0.625, R * 2 / s * 0.9) * s

    pen = QPen(LINIE, 0.25 * E)
    p.setPen(pen)

    # Abdeckung und Auflagering
    p.setBrush(QBrush(QColor("#9e9e9e")))
    p.drawRect(QRectF(cx + R - oeffnung - 1.5 * E, yd(0), oeffnung + 3 * E, h_abd * s))
    p.setBrush(QBrush(GRAU_WAND))
    p.drawRect(QRectF(cx + R - oeffnung - 1.0 * E, yd(h_abd), oeffnung + 2 * E, h_ring_auf * s))

    links_aussen, rechts_aussen = cx - R - t, cx + R + t
    if flach:
        # Abdeckplatte über den ganzen Schacht
        p.drawRect(QRectF(links_aussen, yd(d_konus_oben), rechts_aussen - links_aussen,
                          (d_konus_unten - d_konus_oben) * s))
    else:
        # Konus exzentrisch: rechte Wand senkrecht, linke Wand geneigt
        x_o_l = cx + R - oeffnung
        konus_l = QPolygonF([QPointF(x_o_l - t, yd(d_konus_oben)), QPointF(x_o_l, yd(d_konus_oben)),
                             QPointF(cx - R, yd(d_konus_unten)), QPointF(links_aussen, yd(d_konus_unten))])
        p.drawPolygon(konus_l)
        p.drawRect(QRectF(cx + R, yd(d_konus_oben), t, (d_konus_unten - d_konus_oben) * s))
        # Steigeisen an der senkrechten Wand
        p.setPen(QPen(LINIE, 0.2 * E))
        d = d_konus_oben + 0.25
        while d < tiefe - 0.3:
            p.drawLine(QPointF(cx + R, yd(d)), QPointF(cx + R - 0.12 * s, yd(d)))
            d += 0.25
        p.setPen(pen)

    # Schachtringe
    p.setBrush(QBrush(GRAU_WAND))
    d = d_konus_unten
    while d < d_unterteil - 0.05:
        h = min(1.0 if d_unterteil - d >= 1.0 else 0.5, d_unterteil - d)
        p.drawRect(QRectF(links_aussen, yd(d), t, h * s))
        p.drawRect(QRectF(cx + R, yd(d), t, h * s))
        d += h

    # Schachtunterteil (etwas breitere Wand) mit Bodenplatte
    t2 = t * 1.4
    boden = 0.2
    pfad = QPainterPath()
    pfad.addRect(QRectF(cx - R - t2, yd(d_unterteil), R * 2 + 2 * t2, (tiefe - d_unterteil + boden) * s))
    innen = QPainterPath()
    innen.addRect(QRectF(cx - R, yd(d_unterteil) - 1, R * 2, (tiefe - d_unterteil) * s + 1))
    p.drawPath(pfad.subtracted(innen))

    # Gerinne / Auftritt
    y_sohle = yd(tiefe)
    y_auftritt = yd(tiefe - dn_haupt * 0.75)
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(WASSER))
    h_gerinne = min(dn_haupt * 0.5, 0.25) * s          # Gerinne/Wasser in der Sohle (schematisch)
    p.drawRect(QRectF(cx - R, y_sohle - h_gerinne, R * 2, h_gerinne))
    if h_gerinne >= 2.2 * E:
        p.setFont(_font(5))
        p.setPen(QColor("#1f5f9f"))
        p.drawText(QRectF(cx - R, y_sohle - h_gerinne, R * 2, h_gerinne), Qt.AlignCenter, "Gerinne")
    p.setPen(QPen(LINIE, 0.2 * E))
    p.drawLine(QPointF(cx - R, y_auftritt), QPointF(cx + R, y_auftritt))
    p.setFont(_font(5))
    p.setPen(QColor("#555555"))
    p.drawText(QRectF(cx - R, y_auftritt - 3.2 * E, R * 2, 3 * E), Qt.AlignCenter, "Auftritt / Bankett")

    # Mittelachse
    p.setPen(QPen(QColor("#777777"), 0.15 * E, Qt.DashDotLine))
    p.drawLine(QPointF(cx, yd(0) - 1 * E), QPointF(cx, y_sohle + boden * s + 1 * E))

    # Rohre
    p.setFont(_font(5.2))
    for r in rohre:
        uhr = r["uhr"] or 6
        th = math.radians(uhr * 30.0)
        cos_t = math.cos(th)                      # 12 Uhr -> links, 6 Uhr -> rechts
        dn = r["dn"] / 1000.0 * s
        y_unten = yd(r["tiefe"])
        beschr = f"DN {r['dn']:.0f} · {uhr} Uhr · {r['art']}" + (f" ({r['quelle']})" if r.get("quelle") else "")
        if abs(cos_t) >= 0.5:
            seite = -1 if cos_t > 0 else 1
            x_wand = cx + seite * (R + (t2 if r["tiefe"] > d_unterteil else t))
            x_ende = x_wand + seite * stutzen
            rect = QRectF(min(x_wand, x_ende), y_unten - dn, abs(x_ende - x_wand), dn)
            p.setPen(QPen(LINIE, 0.25 * E))
            p.setBrush(QBrush(GRAU_ROHR))
            p.drawRect(rect)
            # Öffnung in der Wand
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("white")))
            p.drawRect(QRectF(min(cx + seite * R, x_wand), y_unten - dn + 0.2 * E,
                              abs(x_wand - (cx + seite * R)), dn - 0.4 * E))
            p.setPen(QPen(QColor("#777777"), 0.12 * E, Qt.DashDotLine))
            p.drawLine(QPointF(x_wand, y_unten - dn / 2), QPointF(x_ende, y_unten - dn / 2))
            p.setPen(QColor("#333333"))
            # zweizeilig: DN/Uhrlage über dem Rohr, Zu-/Ablauf (Haltung) darunter;
            # linksbündig ab dem äußeren Ende, damit nichts über den Rand hinausläuft
            x_txt = min(x_wand, x_ende)
            breite = abs(x_ende - x_wand) + 14 * E
            p.drawText(QRectF(x_txt, y_unten - dn - 3.2 * E, breite, 3 * E), Qt.AlignLeft | Qt.AlignBottom,
                       f"DN {r['dn']:.0f} · {uhr} Uhr")
            p.drawText(QRectF(x_txt, y_unten + 0.2 * E, breite, 3 * E), Qt.AlignLeft | Qt.AlignTop,
                       r["art"] + (f" ({r['quelle']})" if r.get("quelle") else ""))
        else:
            # Rohr quer zur Schnittebene: als Kreis auf der Wand (3 bzw. 9 Uhr)
            x = cx - cos_t * R * 0.9
            p.setPen(QPen(LINIE, 0.25 * E, Qt.SolidLine if uhr in (3, 4, 2) else Qt.DashLine))
            p.setBrush(QBrush(GRAU_ROHR) if uhr in (3, 4, 2) else Qt.NoBrush)
            p.drawEllipse(QPointF(x, y_unten - dn / 2), dn / 2, dn / 2)
            p.setPen(QColor("#333333"))
            p.drawText(QRectF(x - 14 * E, y_unten - dn - 3.4 * E, 28 * E, 3 * E),
                       Qt.AlignHCenter | Qt.AlignBottom, beschr)

    # Höhenangaben links
    p.setFont(_font(5.2))
    p.setPen(QColor("#333333"))
    deckel, sohle = od.s("deckelhoehe"), od.s("sohlhoehe")
    p.drawText(QRectF(0, yd(0) - 1.5 * E, cx - R - t - 1.5 * E - 2 * E, 3 * E), Qt.AlignRight | Qt.AlignVCenter,
               f"DH {deckel}" if deckel else "Deckel")
    p.drawText(QRectF(0, y_sohle - 1.5 * E, 8.5 * E, 3 * E), Qt.AlignLeft | Qt.AlignVCenter,
               f"SH {sohle}" if sohle else f"{tiefe:.2f} m".replace(".", ","))
    # Höhenachse ganz links (0 = Sohle)
    p.setPen(QPen(QColor("#888888"), 0.15 * E))
    p.drawLine(QPointF(1 * E, yd(0)), QPointF(1 * E, y_sohle))
    schritt = 0.5 if tiefe <= 4 else 1.0
    h = 0.0
    p.setFont(_font(4.8))
    while h <= tiefe + 1e-6:              # Höhe über Sohle, von unten gezählt
        d = tiefe - h
        p.drawLine(QPointF(0.4 * E, yd(d)), QPointF(1.6 * E, yd(d)))
        if h > 0.05 and d > 0.2:
            p.drawText(QRectF(2 * E, yd(d) - 1.4 * E, 8 * E, 2.8 * E), Qt.AlignLeft | Qt.AlignVCenter,
                       f"{h:.1f}".replace(".", ","))
        h += schritt

    def wand_x(b, y):
        """Befund an der linken (Uhrlage 9–3 über 12) oder rechten Wand; Standard rechts."""
        uhr = _uhr(b.werte.get("pos_von"))
        dicke = t2 if tiefe_von(od, b.station) > d_unterteil else t
        if uhr is not None and math.cos(math.radians(uhr * 30.0)) > 0.3:
            return cx - R - dicke / 2
        return cx + R + dicke / 2

    return {"wand_x": wand_x}


def _draufsicht(p, od, rohre, cx, cy, platz, dn_schacht, dn_haupt):
    """Draufsicht mit Zu-/Abläufen in Uhrlage (12 Uhr oben = Hauptablauf)."""
    # Platz für Stutzen (Rohrlänge) und Beschriftung außen herum freihalten
    stutzen = platz * 0.24
    aussen = stutzen + 6.5 * E
    R = max(min(platz, cx - 13 * E) - aussen, 8 * E)
    sp = R / (dn_schacht / 2)
    t = max(0.12 * sp, 1.0 * E)
    R -= t
    sp = R / (dn_schacht / 2)

    def punkt(uhr, radius):
        th = math.radians(uhr * 30.0)
        return QPointF(cx + radius * math.sin(th), cy - radius * math.cos(th))

    # Gerinne: von jedem Zulauf (auf Sohlhöhe) zur Mitte, von der Mitte zum Hauptablauf.
    # Breite = Rohrdurchmesser, höchstens 40 % des Schachts; nur innerhalb des Schachts.
    p.save()
    innen_kreis = QPainterPath()
    innen_kreis.addEllipse(QPointF(cx, cy), R, R)
    p.setClipPath(innen_kreis)
    for r in rohre:
        if not r["uhr"] or r["tiefe"] < od.laenge - 0.25:
            continue
        if r["art"] not in ("Zulauf", "Hauptablauf", "Ablauf"):
            continue
        breite = min(max(r["dn"] / 1000.0 * sp, 1.2 * E), R * 0.8)
        p.setPen(QPen(WASSER, breite, Qt.SolidLine, Qt.FlatCap, Qt.RoundJoin))
        p.drawLine(punkt(r["uhr"], R), QPointF(cx, cy))
    p.restore()

    # Rohre
    p.setFont(_font(5))
    je_uhr = {}
    for r in rohre:
        uhr = r["uhr"]
        if not uhr:
            continue
        n_gleich = je_uhr.get(uhr, 0)
        je_uhr[uhr] = n_gleich + 1
        dn = max(r["dn"] / 1000.0 * sp, 1.0 * E)
        p.save()
        p.translate(cx, cy)
        p.rotate(uhr * 30.0)
        p.setPen(QPen(LINIE, 0.22 * E))
        p.setBrush(QBrush(GRAU_ROHR))
        p.drawRect(QRectF(-dn / 2, -(R + t + stutzen), dn, stutzen + t * 0.5))
        p.restore()
        a = punkt(uhr, R + t + stutzen + 3.2 * E + n_gleich * 3.4 * E)   # gleiche Uhrlage: weiter außen
        p.setPen(QColor("#333333"))
        p.drawText(QRectF(a.x() - 13 * E, a.y() - 1.6 * E, 26 * E, 3.2 * E), Qt.AlignCenter,
                   f"{uhr} Uhr · DN {r['dn']:.0f}")
        # Fließpfeil
        innen, aussen = punkt(uhr, R * 0.55), punkt(uhr, R * 0.85)
        start, ende = (aussen, innen) if r["art"] == "Zulauf" else (innen, aussen)
        if r["art"] != "verschlossen":
            p.setPen(QPen(QColor("#1f6fd1"), 0.3 * E))
            p.drawLine(start, ende)
            winkel = math.atan2(ende.y() - start.y(), ende.x() - start.x())
            for d in (2.6, -2.6):
                p.drawLine(ende, QPointF(ende.x() - 1.4 * E * math.cos(winkel + d / 2.2),
                                         ende.y() - 1.4 * E * math.sin(winkel + d / 2.2)))

    # Schachtwand
    p.setPen(QPen(LINIE, 0.25 * E))
    p.setBrush(Qt.NoBrush)
    ring = QPainterPath()
    ring.addEllipse(QPointF(cx, cy), R + t, R + t)
    loch = QPainterPath()
    loch.addEllipse(QPointF(cx, cy), R, R)
    p.setBrush(QBrush(GRAU_WAND))
    p.drawPath(ring.subtracted(loch))
    # Einstiegsöffnung (exzentrisch zur senkrechten Wand, gestrichelt)
    p.setPen(QPen(QColor("#777777"), 0.15 * E, Qt.DashLine))
    p.setBrush(Qt.NoBrush)
    r_oeff = min(0.625 / 2 * sp, R * 0.6)
    p.drawEllipse(punkt(6, R - r_oeff), r_oeff, r_oeff)

    # Uhr-Markierungen
    p.setFont(_font(4.8))
    p.setPen(QColor("#888888"))
    for u in (12, 3, 6, 9):
        a = punkt(u, R - 2.5 * E)
        p.drawText(QRectF(a.x() - 3 * E, a.y() - 1.5 * E, 6 * E, 3 * E), Qt.AlignCenter, str(u))
    # Schnittlinie A–A
    p.setPen(QPen(QColor("#555555"), 0.2 * E, Qt.DashDotLine))
    p.drawLine(punkt(12, R + t + 1 * E), punkt(6, R + t + 1 * E))
    p.setFont(_font(5.5, True))
    p.setPen(LINIE)
    for u in (12, 6):
        a = punkt(u, R + t + stutzen * 0.45)
        p.drawText(QRectF(a.x() + 1.5 * E, a.y() - 1.5 * E, 4 * E, 3 * E), Qt.AlignLeft | Qt.AlignVCenter, "A")

    # Befunde mit Uhrlage als nummerierte Punkte an der Wand
    marken = {}
    p.setFont(_font(4.6, True))
    for nr, b in enumerate(od.befunde, 1):
        k = b.kuerzel.upper()
        if k.startswith("DCA") or k.startswith("DCG"):
            continue
        uhr = _uhr(b.werte.get("pos_von"))
        if uhr is None:
            continue
        farbe = QColor(ZK_FARBEN.get(b.klasse, ZK_FARBEN[5])) if b.klasse is not None else QColor("#444444")
        q = punkt(uhr, R - 5.5 * E - (nr % 3) * 2.2 * E)
        p.setPen(QPen(farbe.darker(150), 0.15 * E))
        p.setBrush(QBrush(farbe))
        p.drawEllipse(q, 1.6 * E, 1.6 * E)
        p.setPen(QColor("white") if b.klasse in (0, 2, 4) else QColor("black"))
        p.drawText(QRectF(q.x() - 2 * E, q.y() - 1.6 * E, 4 * E, 3.2 * E), Qt.AlignCenter, str(nr))
        marken[nr] = (q.x(), q.y())
    return marken
