"""Benutzerdefiniertes Inspektionsgrafik-Widget für die Qt-Designer-Oberfläche."""

from __future__ import annotations

import math
from typing import Any, Optional

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QBrush, QColor, QPainter, QPen
from qgis.PyQt.QtWidgets import QWidget


def _gleitkommazahl_sicher_lesen(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


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
        """Ordnet Bewertungswerte einer zurückhaltenden Markierungsfarbe zu."""
        values = [
            int(_gleitkommazahl_sicher_lesen(row.get("ZD"), 0)),
            int(_gleitkommazahl_sicher_lesen(row.get("ZB"), 0)),
            int(_gleitkommazahl_sicher_lesen(row.get("ZS"), 0)),
        ]
        positive = [value for value in values if 1 <= value <= 5]
        rating = min(positive) if positive else 0
        return {
            1: QColor("#b91c1c"),
            2: QColor("#ea580c"),
            3: QColor("#eab308"),
            4: QColor("#65a30d"),
            5: QColor("#15803d"),
        }.get(rating, QColor("#64748b"))

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
                painter.setPen(QPen(QColor("#2563eb"), 3, Qt.SolidLine, Qt.RoundCap))
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

