# planauskunft/berichte/grafik.py
"""
Haltungsgrafik als Vektorgrafik (SVG): Haltung senkrecht mit Schächten, Stationsachse,
Befunde nach Station mit Zustandsklassen-Farbe und Beschriftung (Kollisionen werden
nach unten aufgelöst). Die SVG wird im Bericht als Bildelement eingebunden und bleibt
im PDF vektoriell.
"""

import math

from qgis.PyQt.QtCore import Qt, QRectF, QPointF, QSize, QRect
from qgis.PyQt.QtGui import QPainter, QPen, QColor, QFont, QFontMetricsF, QBrush

from .daten import ZK_FARBEN, zahl, text

E = 10.0           # Zeicheneinheiten je mm (0,1 mm)


def _pt(pt):
    return pt * 0.3528 * E


def _font(pt, fett=False):
    f = QFont("Arial")
    f.setPixelSize(max(1, int(round(_pt(pt)))))
    f.setBold(fett)
    return f


def _umbrechen(fm, txt, breite):
    zeilen, aktuell = [], ""
    for wort in str(txt).split():
        probe = (aktuell + " " + wort).strip()
        w = fm.horizontalAdvance(probe) if hasattr(fm, "horizontalAdvance") else fm.width(probe)
        if w <= breite or not aktuell:
            aktuell = probe
        else:
            zeilen.append(aktuell)
            aktuell = wort
    if aktuell:
        zeilen.append(aktuell)
    return zeilen or [""]


def _anschluss(p, b, y, rohr_x, rohr_b, gegen):
    """Anschluss als kurzer Strich links oder rechts der Haltung.

    Die Uhrlage gilt mit Blick in Inspektionsrichtung (3 Uhr = rechts vom Betrachter).
    Die Haltung ist in Fließrichtung von oben nach unten gezeichnet:
      * in Fließrichtung inspiziert: der Betrachter „läuft“ auf dem Blatt nach unten,
        sein rechts ist auf dem Blatt links  -> 1–5 Uhr links, 7–11 Uhr rechts
      * gegen Fließrichtung: er läuft nach oben -> 1–5 Uhr rechts, 7–11 Uhr links
    12 bzw. 6 Uhr (Scheitel/Sohle) werden als Kreis auf der Rohrachse dargestellt.
    Der Strich ist leicht nach oben (stromauf) geneigt – so münden Anschlüsse in Fließrichtung ein."""
    uhr = _uhr(b.werte.get("pos_von"))
    if uhr is None or not 1 <= uhr <= 12:
        uhr = _uhr(b.werte.get("pos_bis"))
    if uhr is None or not 1 <= uhr <= 12:
        return
    p.save()
    p.setPen(QPen(QColor("#333333"), 0.5 * E, Qt.SolidLine, Qt.RoundCap))
    if uhr in (12, 6):
        p.setBrush(QBrush(QColor("white") if uhr == 12 else QColor("#333333")))
        p.drawEllipse(QPointF(rohr_x, y), 1.1 * E, 1.1 * E)
    else:
        rechts_vom_betrachter = 1 <= uhr <= 5
        seite = (1 if rechts_vom_betrachter else -1) if gegen else (-1 if rechts_vom_betrachter else 1)
        x_wand = rohr_x + seite * rohr_b / 2
        p.drawLine(QPointF(x_wand, y), QPointF(x_wand + seite * 7 * E, y - 3.5 * E))
    p.restore()


def _schritt(laenge):
    for s in (1, 2, 5, 10, 20, 25, 50, 100):
        if laenge / s <= 14:
            return s
    return 200


def _uhr(wert):
    z = zahl(wert)
    return int(round(z)) if z is not None else None


def uhrlage(b):
    """'9 – 3 Uhr', '12 Uhr' oder '' (0 bzw. leer = keine Angabe)."""
    werte = []
    for name in ("pos_von", "pos_bis"):
        u = _uhr(b.werte.get(name))
        if u is not None and 1 <= u <= 12:
            werte.append(u)
    if not werte:
        return ""
    if len(werte) == 2 and werte[0] != werte[1]:
        return f"{werte[0]} – {werte[1]} Uhr"
    return f"{werte[0]} Uhr"


def befund_text(b):
    st = f"{b.station:.2f} m".replace(".", ",") if b.station is not None else "–"
    teile = [st, b.kuerzel]
    zusatz = [x for x in (b.wert("charakt1"), b.wert("charakt2")) if x]
    if zusatz:
        teile[-1] += " " + "".join(zusatz)
    lang = b.langtext
    q = [b.wert("quantnr1"), b.wert("quantnr2")]
    q = [x for x in q if x and x not in ("0", "0.0")]
    if q:
        lang += f" ({' / '.join(q)})"
    uhr = uhrlage(b)
    if uhr:
        lang += f", {uhr}"
    if b.wert("kommentar"):
        lang += f" – {b.wert('kommentar')}"
    return "  ".join(teile), lang


def zeichne_haltungsgrafik(pfad, od, breite_mm=175.0, hoehe_mm=225.0, schrift_pt=6.5, regionen=None):
    """Schreibt die Haltungsgrafik als SVG. Rückgabe: tatsächliche Höhe in mm.
    regionen: optionale Liste, in die (QRectF in mm, Befund) der Textblöcke geschrieben wird."""
    if od.ist_schacht:
        from .schachtgrafik import zeichne_schachtgrafik
        return zeichne_schachtgrafik(pfad, od, breite_mm, hoehe_mm, schrift_pt, regionen)
    from qgis.PyQt.QtSvg import QSvgGenerator

    W, H = breite_mm * E, hoehe_mm * E
    oben, unten = 14 * E, 16 * E
    rohr_x = (36 if od.ist_schacht else 28) * E      # Schacht ist breiter -> weiter rechts
    text_x = 52 * E
    text_b = W - text_x - 1 * E
    laenge = max(od.laenge, 0.1)

    # --- Texte vorbereiten und Platz ermitteln (Schrift ggf. verkleinern) ---
    def layout_texte(pt):
        f1, f2 = _font(pt, True), _font(pt)
        fm1, fm2 = QFontMetricsF(f1), QFontMetricsF(f2)
        zeilen_h = fm2.height() * 1.05
        eintraege = []
        for b in od.befunde:
            kopf, lang = befund_text(b)
            zl = _umbrechen(fm2, lang, text_b - 2 * E)
            hoehe = fm1.height() * 1.05 + len(zl) * zeilen_h + 1.2 * E
            eintraege.append((b, kopf, zl, hoehe))
        return f1, f2, fm1, zeilen_h, eintraege

    legende_h = 7 * E
    text_oben = oben - 3 * E
    text_unten = H - legende_h - 2 * E          # Texte enden oberhalb der Legende

    pt = schrift_pt
    while True:
        f1, f2, fm1, zeilen_h, eintraege = layout_texte(pt)
        gesamt = sum(e[3] for e in eintraege)
        if gesamt <= (text_unten - text_oben) or pt <= 4.6:
            break
        pt -= 0.4

    y0, y1 = oben, H - unten - legende_h      # Rohr von Schacht oben bis Schacht unten

    gegen = od.gegen_fliessrichtung

    def y_station(st):
        """Die Haltung ist immer in Fließrichtung gezeichnet (Schacht oben = oben).
        Bei Inspektion gegen die Fließrichtung liegt Station 0 deshalb unten."""
        st = min(max(st or 0.0, 0.0), laenge)
        if gegen:
            st = laenge - st
        return y0 + st / laenge * (y1 - y0)

    eintraege.sort(key=lambda e: y_station(e[0].station))

    # 1) Wunschlage (auf Höhe der Station), Überlappungen nach unten auflösen
    pos, frei_ab = [], text_oben
    for b, kopf, zl, h in eintraege:
        y = max(y_station(b.station) - fm1.ascent() * 0.6, frei_ab)
        pos.append(y)
        frei_ab = y + h
    # 2) Was unten übersteht, von unten nach oben zurückschieben
    grenze = text_unten
    for i in range(len(pos) - 1, -1, -1):
        h = eintraege[i][3]
        if pos[i] + h > grenze:
            pos[i] = grenze - h
        grenze = pos[i]
    # 3) Oben nicht über den Rand, Überlappungen erneut nach unten auflösen
    frei_ab = text_oben
    for i, (b, kopf, zl, h) in enumerate(eintraege):
        pos[i] = max(pos[i], frei_ab)
        frei_ab = pos[i] + h
    ende = frei_ab
    # Passt es auch mit kleinster Schrift nicht, wird die Grafik länger (im Bericht verkleinert)
    benoetigt = max(H, ende + legende_h + 2 * E)

    gen = QSvgGenerator()
    gen.setFileName(pfad)
    gen.setResolution(int(25.4 * E))
    gen.setSize(QSize(int(W), int(benoetigt)))
    gen.setViewBox(QRect(0, 0, int(W), int(benoetigt)))
    gen.setTitle(f"{'Schachtgrafik' if od.ist_schacht else 'Haltungsgrafik'} {od.name}")
    p = QPainter()
    if not p.begin(gen):
        raise RuntimeError("Haltungsgrafik konnte nicht erzeugt werden.")
    try:
        p.setRenderHint(QPainter.Antialiasing, True)

        # Stationsachse
        p.setPen(QPen(QColor("#888888"), 0.15 * E))
        p.setFont(_font(5.5))
        s = _schritt(laenge)
        st = 0.0
        while st <= laenge + 1e-6:
            y = y_station(st)
            p.drawLine(QPointF(rohr_x - 7 * E, y), QPointF(rohr_x - 5 * E, y))
            if laenge - st > s * 0.3:          # nicht doppelt zur Längenangabe am Ende
                p.drawText(QRectF(0, y - 2 * E, rohr_x - 8 * E, 4 * E), Qt.AlignRight | Qt.AlignVCenter,
                           f"{st:.0f} m")
            st += s
        p.drawLine(QPointF(rohr_x - 6 * E, y0), QPointF(rohr_x - 6 * E, y1))
        y_ende = y_station(laenge)
        p.drawText(QRectF(0, (y_ende + 0.5 * E) if not gegen else (y_ende - 4.5 * E), rohr_x - 8 * E, 4 * E),
                   Qt.AlignRight | (Qt.AlignTop if not gegen else Qt.AlignBottom),
                   f"{laenge:.2f} m".replace(".", ","))
        # Fließrichtungspfeil links neben der Achse
        if not od.ist_schacht:
            xa = 5.0 * E                      # ganz links, neben den Stationsbeschriftungen
            ym = (y0 + y1) / 2
            p.setPen(QPen(QColor("#1f6fd1"), 0.3 * E))
            p.drawLine(QPointF(xa, ym - 6 * E), QPointF(xa, ym + 6 * E))
            p.drawLine(QPointF(xa, ym + 6 * E), QPointF(xa - 1.2 * E, ym + 4 * E))
            p.drawLine(QPointF(xa, ym + 6 * E), QPointF(xa + 1.2 * E, ym + 4 * E))
            p.save()
            p.translate(xa - 1.6 * E, ym)
            p.rotate(-90)
            p.setFont(_font(5))
            p.setPen(QColor("#1f6fd1"))
            p.drawText(QRectF(-12 * E, -3 * E, 24 * E, 3 * E), Qt.AlignCenter, "Fließrichtung")
            p.restore()
            p.setPen(QPen(QColor("#888888"), 0.15 * E))

        # Rohr
        if od.ist_schacht:
            d = zahl(od.s("durchm", "durchmesser"), 1000) or 1000
            d = d * 1000 if d < 10 else d                     # m -> mm
            rohr_b = min(max(d / 120.0, 6.0), 12.0) * E      # Schacht deutlich breiter
        else:
            dn = zahl(od.s("breite"), 300) or 300
            rohr_b = min(max(dn / 100.0, 2.0), 6.0) * E
        p.setPen(QPen(QColor("#222222"), 0.25 * E))
        p.setBrush(QBrush(QColor("#e9edf2")))
        p.drawRect(QRectF(rohr_x - rohr_b / 2, y0, rohr_b, y1 - y0))

        # Schächte
        r = 3.2 * E
        p.setBrush(QBrush(QColor("white")))
        p.setPen(QPen(QColor("#222222"), 0.35 * E))
        p.setFont(_font(6.5, True))
        if od.ist_schacht:
            enden = ((y0, f"Deckel {od.s('deckelhoehe')}".strip(), True),
                     (y1, f"Sohle {od.s('sohlhoehe')}".strip(), False))
        else:
            enden = ((y0, od.s("schoben"), True), (y1, od.s("schunten"), False))
        for y, name, oberhalb in enden:
            p.setPen(QPen(QColor("#222222"), 0.35 * E))
            p.setBrush(QBrush(QColor("white")))
            if od.ist_schacht:
                # Deckel bzw. Sohle als waagerechter Balken
                p.drawRect(QRectF(rohr_x - rohr_b / 2 - 1.5 * E, y - 0.8 * E, rohr_b + 3 * E, 1.6 * E))
            else:
                p.drawEllipse(QPointF(rohr_x, y), r, r)
            # Schachtname über bzw. unter dem Schacht (nicht auf Höhe der Führungslinien)
            abst = 1.0 * E if od.ist_schacht else r
            ty_name = y - abst - 4.4 * E if oberhalb else y + abst + 0.4 * E
            p.setPen(QColor("#222222"))
            p.drawText(QRectF(rohr_x - 3 * E, ty_name, 24 * E, 4 * E), Qt.AlignLeft | Qt.AlignVCenter, name)
        p.setFont(_font(6))
        richtung = od.inspektionsrichtung
        if richtung:
            p.setPen(QColor("#555555"))
            p.drawText(QRectF(text_x, 0, W - text_x, 4 * E), Qt.AlignLeft | Qt.AlignVCenter,
                       f"Inspektionsrichtung: {richtung}")

        # Befunde
        for (b, kopf, zl, h), ty in zip(eintraege, pos):
            farbe = QColor(ZK_FARBEN.get(b.klasse, ZK_FARBEN[5])) if b.klasse is not None else QColor("#444444")
            y = y_station(b.station)
            linie = farbe.darker(160) if b.klasse == 5 else farbe
            # Markierung am Rohr
            p.setPen(QPen(linie, 0.6 * E))
            p.drawLine(QPointF(rohr_x - rohr_b / 2 - 1.2 * E, y), QPointF(rohr_x + rohr_b / 2 + 1.2 * E, y))
            # Anschluss (BCA) nach Uhrlage und Inspektionsrichtung
            if not od.ist_schacht and b.kuerzel.upper().startswith("BCA"):
                _anschluss(p, b, y, rohr_x, rohr_b, gegen)
            # Führungslinie
            p.setPen(QPen(QColor("#9aa0a6"), 0.15 * E))
            mitte = ty + fm1.ascent() * 0.6
            p.drawLine(QPointF(rohr_x + rohr_b / 2 + 1.5 * E, y), QPointF(text_x - 4 * E, mitte))
            p.drawLine(QPointF(text_x - 4 * E, mitte), QPointF(text_x - 1 * E, mitte))
            # Klassenkästchen
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(farbe))
            p.drawRect(QRectF(text_x, ty, 4.5 * E, fm1.height()))
            if b.klasse is not None:
                p.setPen(QColor("white") if b.klasse in (0, 2, 4) else QColor("black"))
                p.setFont(_font(max(pt - 0.5, 4), True))
                p.drawText(QRectF(text_x, ty, 4.5 * E, fm1.height()), Qt.AlignCenter, str(b.klasse))
            # Texte
            p.setPen(QColor("#111111"))
            p.setFont(f1)
            p.drawText(QPointF(text_x + 6 * E, ty + fm1.ascent()), kopf)
            p.setFont(f2)
            yy = ty + fm1.height() * 1.05
            fm2 = QFontMetricsF(f2)
            for z in zl:
                p.drawText(QPointF(text_x + 6 * E, yy + fm2.ascent()), z)
                yy += zeilen_h
            if regionen is not None:
                regionen.append((QRectF(text_x / E, ty / E, (W - text_x) / E, h / E), b))
                # auch die Markierung am Rohr ist anklickbar
                regionen.append((QRectF((rohr_x - rohr_b / 2) / E - 2.5, y / E - 1.5, rohr_b / E + 5.0, 3.0), b))

        if not od.befunde:
            p.setPen(QColor("#555555"))
            p.setFont(_font(8))
            p.drawText(QRectF(text_x, y0, text_b, 10 * E), Qt.AlignLeft | Qt.AlignVCenter,
                       "Keine Befunde vorhanden.")

        # Legende Zustandsklassen
        p.setFont(_font(5.5))
        x = 0.0
        yl = benoetigt - legende_h + 2 * E
        for k in range(6):
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(ZK_FARBEN[k])))
            p.drawRect(QRectF(x, yl, 3 * E, 3 * E))
            p.setPen(QColor("#333333"))
            p.drawText(QRectF(x + 3.6 * E, yl - 0.5 * E, 22 * E, 4 * E), Qt.AlignLeft | Qt.AlignVCenter, f"ZK {k}")
            x += 16 * E
        if not od.ist_schacht and any(b.kuerzel.upper().startswith("BCA") for b in od.befunde):
            p.setPen(QPen(QColor("#333333"), 0.45 * E))
            p.drawLine(QPointF(x + 0.5 * E, yl + 3 * E), QPointF(x + 4 * E, yl))
            p.setPen(QColor("#333333"))
            p.drawText(QRectF(x + 5.5 * E, yl - 0.5 * E, W - x - 5.5 * E, 4 * E), Qt.AlignLeft | Qt.AlignVCenter,
                       "Anschluss: Seite aus Uhrlage, Blick in Inspektionsrichtung")
    finally:
        p.end()
    return benoetigt / E
