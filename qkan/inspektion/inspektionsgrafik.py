"""Schematische Inspektionsgrafik: interaktives Qt-Widget und PDF-Ausgabe."""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Optional

from qgis.PyQt.QtCore import QRect, QRectF, QSizeF, Qt, pyqtSignal
from qgis.PyQt.QtGui import (
    QBrush, QColor, QFont, QFontMetrics, QPageSize, QPainter, QPdfWriter, QPen,
)
from qgis.PyQt.QtWidgets import QWidget


def _gleitkommazahl_sicher_lesen(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


# Eine gemeinsame Farbdefinition für Bildschirmansicht und PDF-Export.
ZUSTANDSKLASSEN_FARBEN = {
    0: "#ff0000",
    1: "#ff7f00",
    2: "#ffff00",
    3: "#8fcf4f",
    4: "#00af4f",
    5: "#007fff",
}
UNBEWERTET_FARBE = "#64748b"
ANSCHLUSS_FARBE = "#2563eb"


class Inspektionsgrafik(QWidget):
    """Einfache anklickbare Inspektionsgrafik für Leitungs- und Schachtinspektionen."""

    damage_clicked = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(190)
        self._damages: list[dict[str, Any]] = []
        self._connections: list[dict[str, Any]] = []
        self._object_type = "Haltung"
        self._length = 1.0
        self._selected_index = -1
        self._marker_positions: list[tuple[int, float, float]] = []

    def daten_setzen(
        self,
        damages: list[dict[str, Any]],
        object_type: str,
        length: float,
        connections: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """Ersetzt den Inhalt der Grafik."""
        self._damages = damages
        self._connections = list(connections or [])
        self._object_type = object_type
        self._length = max(length, 0.001)
        self._selected_index = -1
        self.update()

    def auswahl_setzen(self, index: int) -> None:
        """Hebt eine Schadensmarkierung hervor."""
        self._selected_index = index
        self.update()

    @staticmethod
    def schadensfarbe_bestimmen(row: dict[str, Any]) -> QColor:
        """Verwendet für ZD/ZB/ZS die QKan-Farben der maßgeblichen Zustandsklasse."""
        values = []
        for field_name in ("ZD", "ZB", "ZS"):
            raw_value = row.get(field_name)
            if raw_value in (None, ""):
                continue
            value = int(_gleitkommazahl_sicher_lesen(raw_value, -1))
            if 0 <= value <= 5:
                values.append(value)

        rating = min(values) if values else None
        return QColor(ZUSTANDSKLASSEN_FARBEN.get(rating, UNBEWERTET_FARBE))

    def paintEvent(self, _event: Any) -> None:
        """Zeichnet das Schema und die Schadensmarkierungen."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.font())
        painter.fillRect(self.rect(), QColor("#ffffff"))
        painter.setPen(QPen(QColor("#334155"), 2))
        self._marker_positions = []

        width = max(self.width(), 200)
        height = max(self.height(), 160)
        margin = 48

        if self._object_type == "Schacht":
            x = width / 2
            top = 28
            bottom = height - 34
            painter.setPen(QPen(QColor("#475569"), 10))
            painter.drawLine(int(x), top, int(x), bottom)
            painter.setPen(QPen(QColor("#334155"), 1))
            painter.drawText(8, 20, "Schacht – schematische vertikale Lage")

            positions = []
            for row in self._damages:
                position = row.get("vertikale_lage")
                if position in (None, ""):
                    position = row.get("station")
                positions.append(_gleitkommazahl_sicher_lesen(position, 0.0))
            scale_max = max(positions + [self._length, 1.0])

            for index, row in enumerate(self._damages):
                position = positions[index]
                ratio = min(max(position / scale_max, 0.0), 1.0)
                y = top + ratio * (bottom - top)
                radius = 8 if index == self._selected_index else 6
                painter.setBrush(QBrush(self.schadensfarbe_bestimmen(row)))
                painter.setPen(QPen(QColor("#0f172a"), 2 if index == self._selected_index else 1))
                painter.drawEllipse(int(x - radius), int(y - radius), radius * 2, radius * 2)
                self._marker_positions.append((index, x, y))
        else:
            left = margin
            right = width - margin
            y = height / 2
            painter.setPen(QPen(QColor("#475569"), 10))
            painter.drawLine(left, int(y), right, int(y))
            painter.setPen(QPen(QColor("#334155"), 1))
            painter.drawText(8, 20, f"{self._object_type} – Stationierung")
            painter.drawText(left - 10, int(y + 30), "0 m")
            painter.drawText(right - 35, int(y + 30), f"{self._length:.1f} m")

            # Angeschlossene Leitungen werden an ihrer tatsächlichen Station dargestellt. Oben bedeutet
            # links und unten bedeutet rechts in der ausgewählten Inspektionsrichtung.
            if self._object_type == "Haltung":
                painter.setPen(QPen(QColor(ANSCHLUSS_FARBE), 3, Qt.SolidLine, Qt.RoundCap))
                for connection in self._connections:
                    station = _gleitkommazahl_sicher_lesen(connection.get("station"), 0.0)
                    ratio = min(max(station / self._length, 0.0), 1.0)
                    x = left + ratio * (right - left)
                    side = -1 if int(connection.get("seite", 1)) < 0 else 1
                    branch_y = y + side * 18
                    painter.drawLine(int(x), int(y), int(x), int(branch_y))

            for index, row in enumerate(self._damages):
                station = _gleitkommazahl_sicher_lesen(row.get("station"), 0.0)
                ratio = min(max(station / self._length, 0.0), 1.0)
                x = left + ratio * (right - left)
                radius = 8 if index == self._selected_index else 6
                painter.setBrush(QBrush(self.schadensfarbe_bestimmen(row)))
                painter.setPen(QPen(QColor("#0f172a"), 2 if index == self._selected_index else 1))
                painter.drawEllipse(int(x - radius), int(y - radius), radius * 2, radius * 2)
                self._marker_positions.append((index, x, y))

        if not self._damages:
            painter.setPen(QColor("#64748b"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Keine Einzelschäden für diese Auswahl")
        painter.end()

    def mousePressEvent(self, event: Any) -> None:
        """Wählt beim Anklicken die nächstgelegene Markierung aus."""
        point = event.position() if hasattr(event, "position") else event.pos()
        x = float(point.x())
        y = float(point.y())
        nearest: Optional[tuple[float, int]] = None
        for index, marker_x, marker_y in self._marker_positions:
            distance = math.hypot(x - marker_x, y - marker_y)
            if nearest is None or distance < nearest[0]:
                nearest = (distance, index)
        if nearest is not None and nearest[0] <= 16:
            self.damage_clicked.emit(nearest[1])



def _pdf_text(value: Any) -> str:
    """Formatierbarer Text, wobei fehlende Werte nicht als 'None' erscheinen."""
    return "" if value is None else str(value)


def _pdf_datum(value: str) -> str:
    text = _pdf_text(value).strip()
    for date_format in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, date_format).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return text or "–"


def inspektionsgrafik_pdf_schreiben(
    *,
    ziel: Path,
    objektart: str,
    objektname: str,
    datum: str,
    schaeden: list[dict[str, Any]],
    anschluesse: list[dict[str, Any]],
    objektlaenge: float,
    gesamtdaten: Mapping[str, Any],
    gesamtbewertungen: Mapping[str, Any],
    stationsfeld: str,
) -> None:
    """Erzeugt die Befahrungsgrafik als PDF ohne Abhängigkeit vom Medien-Dialog.

    Die tatsächlichen Stationswerte bleiben erhalten. Dichte Bereiche und die
    zugehörigen Beschriftungen werden lediglich für die Lesbarkeit entzerrt.
    """
    laenge = max(_gleitkommazahl_sicher_lesen(objektlaenge, 1.0), 1.0)
    geordnet = sorted(
        enumerate(schaeden),
        key=lambda item: (
            max(0.0, min(laenge, _gleitkommazahl_sicher_lesen(
                item[1].get(stationsfeld), 0.0
            ))),
            item[0],
        ),
    )

    writer = QPdfWriter(str(ziel))
    writer.setResolution(300)
    writer.setPageSize(QPageSize(QSizeF(210.0, 297.0), QPageSize.Millimeter))
    writer.setTitle(f"Befahrungsgrafik {objektart} {objektname}")

    page_width = writer.width()
    margin = int(page_width * 0.045)
    center_x = page_width // 2
    label_padding = 115
    label_width = max(120, center_x - margin - label_padding)

    title_font = QFont("Arial", 14, QFont.Bold)
    heading_font = QFont("Arial", 9, QFont.Bold)
    entry_font = QFont("Arial", 7, QFont.Bold)
    body_font = QFont("Arial", 7)
    small_font = QFont("Arial", 7)
    note_font = QFont("Arial", 7)
    note_font.setItalic(True)

    # Die Schriftmetriken des PDF-Geräts statt der Bildschirmauflösung nutzen.
    entry_metrics = QFontMetrics(entry_font, writer)
    body_metrics = QFontMetrics(body_font, writer)
    heading_height = entry_metrics.height() + 6
    padding_y = 10
    base_line_height = 2450
    minimum_marker_gap = 52
    side_bottoms = [-40.0, -40.0]
    previous_marker_y = -minimum_marker_gap
    positionen: list[dict[str, Any]] = []

    for index, (_source_index, row) in enumerate(geordnet):
        station = max(0.0, min(
            laenge, _gleitkommazahl_sicher_lesen(row.get(stationsfeld), 0.0)
        ))
        code = _pdf_text(row.get("kuerzel")).strip()
        station_text = f"{station:.2f}".replace(".", ",")
        hauptzeile = f"{station_text} m  {code}".strip()
        zustandswerte = "   ".join(
            f"{feld}: {_pdf_text(row.get(feld)).strip() or '–'}"
            for feld in ("ZD", "ZB", "ZS")
        )
        gemeinsame_kopfzeile = f"{hauptzeile}    {zustandswerte}"
        umbruch_kopf = entry_metrics.horizontalAdvance(gemeinsame_kopfzeile) > label_width
        langtext = _pdf_text(row.get("langtext")).strip()
        body_height = (
            max(body_metrics.height(), body_metrics.boundingRect(
                QRect(0, 0, label_width, 50000), Qt.TextWordWrap, langtext
            ).height())
            if langtext else 0
        )
        kopfhoehe = heading_height + (body_metrics.height() + 5 if umbruch_kopf else 0)
        label_height = kopfhoehe + (body_height + 8 if langtext else 0) + 2 * padding_y
        side = index % 2
        ideal_y = base_line_height * station / laenge
        y = max(
            ideal_y,
            previous_marker_y + minimum_marker_gap,
            side_bottoms[side] + label_height / 2 + 20,
            label_height / 2 + 16,
        )
        side_bottoms[side] = y + label_height / 2
        previous_marker_y = y
        positionen.append({
            "row": row,
            "station": station,
            "y": y,
            "side": side,
            "label_height": label_height,
            "kopfhoehe": kopfhoehe,
            "hauptzeile": hauptzeile,
            "zustandswerte": zustandswerte,
            "gemeinsame_kopfzeile": gemeinsame_kopfzeile,
            "umbruch_kopf": umbruch_kopf,
            "langtext": langtext,
        })

    linienhoehe = max(
        base_line_height,
        max((entry["y"] + entry["label_height"] / 2 + 65 for entry in positionen),
            default=base_line_height),
    )

    # Auf die entzerrte Stationierung werden auch die Anschlüsse übertragen.
    gruppen: dict[float, list[float]] = {}
    for entry in positionen:
        gruppen.setdefault(round(entry["station"], 6), []).append(entry["y"])
    anker = [(0.0, 0.0)] + [
        (station, sum(werte) / len(werte))
        for station, werte in sorted(gruppen.items())
    ] + [(laenge, linienhoehe)]
    normierte_anker: list[tuple[float, float]] = []
    for station, y in anker:
        if normierte_anker and abs(station - normierte_anker[-1][0]) < 1e-6:
            normierte_anker[-1] = (station, max(normierte_anker[-1][1], y))
        else:
            normierte_anker.append((station, y))

    def y_fuer_station(value: Any) -> float:
        station = max(0.0, min(laenge, _gleitkommazahl_sicher_lesen(value)))
        for index in range(1, len(normierte_anker)):
            station_a, y_a = normierte_anker[index - 1]
            station_b, y_b = normierte_anker[index]
            if station <= station_b or index == len(normierte_anker) - 1:
                if abs(station_b - station_a) < 1e-6:
                    return y_b
                ratio = (station - station_a) / (station_b - station_a)
                return y_a + (y_b - y_a) * ratio
        return linienhoehe

    header_height = 735
    top_padding = 120
    bottom_margin = 280
    required_height = margin + header_height + top_padding + linienhoehe + bottom_margin
    page_height_mm = max(297.0, required_height * 25.4 / 300.0)
    writer.setPageSize(QPageSize(
        QSizeF(210.0, page_height_mm), QPageSize.Millimeter, "Befahrungsgrafik"
    ))
    painter = QPainter(writer)
    if not painter.isActive():
        raise RuntimeError("PDF-Zeichner konnte nicht gestartet werden.")

    def zahl(value: Any, stellen: int = 2) -> str:
        return f"{_gleitkommazahl_sicher_lesen(value, 0.0):.{stellen}f}".replace(".", ",")

    try:
        painter.setRenderHint(QPainter.Antialiasing)
        top = margin + header_height + top_padding
        bottom = top + int(linienhoehe)
        painter.setPen(QColor("#0f172a"))
        painter.setFont(title_font)
        painter.drawText(
            QRectF(margin, margin, page_width - 2 * margin, 120),
            Qt.AlignVCenter | Qt.AlignLeft,
            f"Befahrungsgrafik {objektart}: {objektname} – {_pdf_datum(datum)}",
        )

        infos: list[str] = []
        erste_zeile: list[str] = []
        if objektart == "Schacht":
            durchmesser = _gleitkommazahl_sicher_lesen(gesamtdaten.get("durchm"))
            if durchmesser > 0:
                erste_zeile.append(f"Durchmesser: {zahl(durchmesser)} m")
        else:
            erste_zeile.append(f"Länge: {zahl(laenge)} m")
            hoehe = _gleitkommazahl_sicher_lesen(gesamtdaten.get("hoehe"))
            breite = _gleitkommazahl_sicher_lesen(gesamtdaten.get("breite"))
            if hoehe > 0 and breite > 0:
                erste_zeile.append(f"Abmessung: {zahl(hoehe, 0)} × {zahl(breite, 0)} mm")
        baujahr = int(_gleitkommazahl_sicher_lesen(gesamtdaten.get("baujahr")))
        if baujahr > 0:
            erste_zeile.append(f"Baujahr: {baujahr}")
        if erste_zeile:
            infos.append("    ".join(erste_zeile))

        zusatz: list[str] = []
        auftrag = _pdf_text(gesamtdaten.get("auftragsbezeichnung")).strip()
        strasse = _pdf_text(gesamtdaten.get("strasse")).strip()
        if auftrag:
            zusatz.append(f"Auftrag: {auftrag}")
        if strasse:
            zusatz.append(f"Straße: {strasse}")
        if zusatz:
            infos.append("    ".join(zusatz))
        infos.append(
            f"Inspektionseinträge: {len(schaeden)}    Gesamtbewertung:    "
            + "    ".join(
                f"{feld}: {_pdf_text(gesamtbewertungen.get(feld)).strip() or '–'}"
                for feld in ("ZD", "ZB", "ZS")
            )
        )
        painter.setFont(heading_font)
        painter.setPen(QColor("#334155"))
        painter.drawText(
            QRectF(margin, margin + 125, page_width - 2 * margin, 270),
            Qt.AlignLeft | Qt.TextWordWrap,
            "\n".join(infos),
        )

        # Eine gemeinsame, bewusst knappe Legende für beide Grafikformate.
        legende_y = margin + 427
        painter.setPen(QPen(QColor("#cbd5e1"), 2))
        painter.drawLine(margin, legende_y - 25, page_width - margin, legende_y - 25)
        painter.setFont(heading_font)
        painter.setPen(QColor("#334155"))
        painter.drawText(
            QRectF(margin, legende_y, 790, 56), Qt.AlignVCenter,
            "Punktfarbe (Zustandsklasse):",
        )
        symbol_start = margin + 820
        symbol_step = 180
        painter.setFont(small_font)
        for i, klassenzahl in enumerate((*range(6), None)):
            x = symbol_start + i * symbol_step
            color = (ZUSTANDSKLASSEN_FARBEN[klassenzahl]
                     if klassenzahl is not None else UNBEWERTET_FARBE)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor("#334155"), 2))
            painter.drawEllipse(x, legende_y + 13, 26, 26)
            painter.setPen(QColor("#334155"))
            painter.drawText(
                QRectF(x + 35, legende_y, 95, 55),
                Qt.AlignVCenter, str(klassenzahl) if klassenzahl is not None else "–",
            )
        painter.setBrush(Qt.NoBrush)
        painter.setFont(small_font)
        painter.setPen(QColor("#475569"))
        painter.drawText(
            QRectF(margin, legende_y + 70, 1200, 58), Qt.AlignVCenter,
            "0 = schlechteste Klasse  ·  – = ohne Bewertung",
        )
        if objektart == "Haltung":
            x = margin + 1310
            painter.setPen(QPen(QColor("#475569"), 10, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(x, legende_y + 95, x + 65, legende_y + 95)
            painter.setPen(QPen(QColor(ANSCHLUSS_FARBE), 7, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(x + 33, legende_y + 95, x + 33, legende_y + 65)
            painter.setPen(QColor("#475569"))
            painter.drawText(
                QRectF(x + 95, legende_y + 65, 600, 58), Qt.AlignVCenter,
                "Blau: Anschlussleitung",
            )
        painter.setFont(note_font)
        painter.setPen(QColor("#64748b"))
        painter.drawText(
            QRectF(margin, legende_y + 142, page_width - 2 * margin, 60),
            Qt.AlignVCenter,
            "Schematische Darstellung – Schäden und Abstände nicht maßstabsgetreu.",
        )
        painter.setPen(QPen(QColor("#cbd5e1"), 3))
        painter.drawLine(
            margin, margin + header_height - 22,
            page_width - margin, margin + header_height - 22,
        )

        painter.setPen(QPen(QColor("#475569"), 16, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(center_x, top, center_x, bottom)
        painter.setPen(QPen(QColor("#334155"), 3))
        painter.drawLine(center_x, top, center_x, bottom)
        painter.drawLine(center_x, bottom, center_x - 30, bottom - 58)
        painter.drawLine(center_x, bottom, center_x + 30, bottom - 58)

        if objektart == "Haltung":
            painter.setPen(QPen(QColor(ANSCHLUSS_FARBE), 7, Qt.SolidLine, Qt.RoundCap))
            for anschluss in anschluesse:
                station_y = top + int(round(y_fuer_station(anschluss.get("station"))))
                seite = -1 if int(anschluss.get("seite", 1)) < 0 else 1
                painter.drawLine(center_x, station_y, center_x + seite * 72, station_y)

        for entry in positionen:
            y = top + int(round(entry["y"]))
            painter.setPen(QPen(QColor("#0f172a"), 4))
            painter.setBrush(QBrush(Inspektionsgrafik.schadensfarbe_bestimmen(entry["row"])))
            painter.drawEllipse(center_x - 16, y - 16, 32, 32)
            painter.setBrush(Qt.NoBrush)
            if entry["side"] == 0:
                painter.drawLine(center_x - 16, y, center_x - 95, y)
                x = margin
                ausrichtung = Qt.AlignRight
            else:
                painter.drawLine(center_x + 16, y, center_x + 95, y)
                x = center_x + 115
                ausrichtung = Qt.AlignLeft

            y_text = y - entry["label_height"] / 2 + padding_y
            painter.setFont(entry_font)
            painter.setPen(QColor("#0f172a"))
            painter.drawText(
                QRectF(x, y_text, label_width, heading_height),
                ausrichtung | Qt.AlignVCenter,
                entry["hauptzeile"] if entry["umbruch_kopf"] else entry["gemeinsame_kopfzeile"],
            )
            y_text += heading_height
            if entry["umbruch_kopf"]:
                painter.setPen(QColor("#475569"))
                painter.setFont(body_font)
                painter.drawText(
                    QRectF(x, y_text, label_width, body_metrics.height() + 5),
                    ausrichtung | Qt.AlignVCenter, entry["zustandswerte"],
                )
                y_text += body_metrics.height() + 5
            if entry["langtext"]:
                painter.setPen(QColor("#475569"))
                painter.setFont(body_font)
                painter.drawText(
                    QRectF(x, y_text + 5, label_width, entry["label_height"] - entry["kopfhoehe"] - 2 * padding_y),
                    ausrichtung | Qt.AlignTop | Qt.TextWordWrap,
                    entry["langtext"],
                )
    finally:
        painter.end()
