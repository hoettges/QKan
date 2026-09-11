"""In das QKan-Inspektionsmodul integrierte Befahrungsmedienansicht.

Das Plugin liest Befahrungs- und Mediendaten aus einer QKan-SQLite-Datenbank.
Die verbindlichen Foto- und Video-Stammordner werden aus der laufenden
QKan-Konfiguration oder aus QKans eigener Datei ``qkan.json`` gelesen. Änderungen an Einzelschäden und der
Gesamtbewertung werden erst über den Button „Speichern“ übernommen.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import site
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QObject,
    QRectF,
    QSizeF,
    QStandardPaths,
    Qt,
    QThread,
    QTimer,
    QUrl,
    pyqtSignal,
    pyqtSlot,
)
from qgis.PyQt.QtGui import (
    QColor,
    QDesktopServices,
    QFont,
    QIcon,
    QPageSize,
    QPainter,
    QPdfWriter,
    QPen,
    QPixmap,
)
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from qgis.core import (
    Qgis,
    QgsFeature,
    QgsGeometry,
    QgsMessageLog,
    QgsPoint,
    QgsPointXY,
    QgsProject,
    QgsMapLayerType,
    QgsVectorLayer,
)
from qgis.gui import QgsMapToolIdentify

from .inspektionsgrafik import Inspektionsgrafik


PLUGIN_GROUP = "QKanMediaInspector"
IMAGE_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}
ACTIVE_MEDIA_THREADS: list[QThread] = []

VIDEO_EXTENSIONS = {
    ".3gp",
    ".avi",
    ".m2ts",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".mts",
    ".ts",
    ".vob",
    ".webm",
    ".wmv",
}

OBJECT_CONFIG = {
    "Haltung": {
        "detail_table": "untersuchdat_haltung",
        "object_column": "untersuchhal",
        "overall_table": "haltungen_untersucht",
        "overall_object_column": "haltnam",
        "length_column": "laenge",
    },
    "Anschlussleitung": {
        "detail_table": "untersuchdat_anschlussleitung",
        "object_column": "untersuchleit",
        "overall_table": "anschlussleitungen_untersucht",
        "overall_object_column": "leitnam",
        "length_column": "laenge",
    },
    "Schacht": {
        "detail_table": "untersuchdat_schacht",
        "object_column": "untersuchsch",
        "overall_table": "schaechte_untersucht",
        "overall_object_column": "schnam",
        "length_column": "durchm",
    },
}


@dataclass(frozen=True)
class Medientreffer:
    """Ein aufgelöster Kandidat für eine Mediendatei."""

    reference_id: Optional[int]
    media_file_id: Optional[int]
    full_path: str
    method: str
    score: int
    ambiguous: bool


@dataclass(frozen=True)
class Medieneintrag:
    """Ein Foto- oder Videoeintrag, der einer Schadenszeile zugeordnet ist."""

    damage_index: int
    media_type: str
    stored_path: str
    candidates: tuple[Medientreffer, ...]
    caption: str
    start_seconds: float = 0.0
    resolution_status: str = ""


def _loggen(message: str, level: Qgis.MessageLevel = Qgis.Info) -> None:
    """Schreibt eine Meldung in das QGIS-Protokoll."""
    QgsMessageLog.logMessage(message, "QKan Medieninspektor", level)


def _sql_bezeichner_quotieren(identifier: str) -> str:
    """Maskiert einen SQLite-Bezeichner."""
    return '"' + identifier.replace('"', '""') + '"'


def _pfadtext_normalisieren(value: Any) -> str:
    """Normalisiert Pfadtext für Vergleiche ohne Beachtung der Groß-/Kleinschreibung."""
    text = "" if value is None else str(value)
    text = text.strip().strip('"').strip("'")
    text = text.replace("\\", "/")
    text = re.sub(r"/+", "/", text)
    while text.startswith("./"):
        text = text[2:]
    return text.casefold().strip()


def _dateiname_aus_pfad(value: Any) -> str:
    """Liefert einen Dateinamen unabhängig von der verwendeten Pfadtrennung."""
    normalized = _pfadtext_normalisieren(value)
    return normalized.rsplit("/", 1)[-1] if normalized else ""


def _dateistamm_aus_pfad(value: Any) -> str:
    """Liefert den Dateistamm in Kleinschreibung."""
    filename = _dateiname_aus_pfad(value)
    return filename.rsplit(".", 1)[0] if "." in filename else filename


def _aufzeichnungscode_aus_dateiname(value: Any) -> str:
    """Liest den führenden historischen Aufzeichnungscode aus einem Mediendateinamen."""
    match = re.match(r"[^0-9]*(\d{6,})", Path(_dateiname_aus_pfad(value)).stem)
    return match.group(1) if match else ""


def _aufzeichnungscode_in_sekunden(code: str) -> Optional[int]:
    """Interpretiert die letzten fünf Codeziffern historischer TV-Daten als M[M]MSS."""
    if not code or len(code) < 5 or not code[-5:].isdigit():
        return None
    clock = code[-5:]
    minutes = int(clock[:-2])
    seconds = int(clock[-2:])
    if seconds >= 60:
        return None
    return minutes * 60 + seconds


def _qkan_medienstammpfade_laden() -> tuple[str, str]:
    """Liest die Foto- und Video-Stammordner aus derselben QKan-Konfiguration. QKan
    speichert diese Werte als ``fotoRootPath`` und ``videoRootPath`` in
    ``qkan.json``. Wenn die laufende QKan-Instanz verfügbar ist, wird deren bereits
    geladene Konfiguration verwendet.
    """
    foto_root = ""
    video_root = ""

    try:
        from qkan import QKan  # type: ignore

        qkan_config = getattr(QKan, "config", None)
        if qkan_config is not None:
            foto_root = _text_sicher_lesen(
                getattr(qkan_config, "fotoRootPath", "")
            ).strip()
            video_root = _text_sicher_lesen(
                getattr(qkan_config, "videoRootPath", "")
            ).strip()
    except Exception as error:
        _loggen(
            f"Laufende QKan-Konfiguration konnte nicht gelesen werden: {error}",
            Qgis.Info,
        )

    if not foto_root or not video_root:
        config_path = Path(site.getuserbase()) / "qkan" / "qkan.json"
        if config_path.is_file():
            try:
                config_data = json.loads(config_path.read_text(encoding="utf-8"))
                if not foto_root:
                    foto_root = _text_sicher_lesen(
                        config_data.get("fotoRootPath", "")
                    ).strip()
                if not video_root:
                    video_root = _text_sicher_lesen(
                        config_data.get("videoRootPath", "")
                    ).strip()
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                _loggen(
                    f"QKan-Konfigurationsdatei konnte nicht gelesen werden: "
                    f"{config_path}: {error}",
                    Qgis.Warning,
                )

    def bereinigen(value: str) -> str:
        if not value:
            return ""
        return os.path.normpath(
            os.path.expandvars(os.path.expanduser(value.strip().strip('"').strip("'")))
        )

    return bereinigen(foto_root), bereinigen(video_root)


def _pfad_innerhalb_stammordner(path: str, root: str) -> bool:
    """Prüft, ob ein Pfad innerhalb des verbindlichen QKan-Stammordners liegt."""
    if not path or not root:
        return False
    try:
        normalized_path = os.path.normcase(os.path.abspath(os.path.normpath(path)))
        normalized_root = os.path.normcase(os.path.abspath(os.path.normpath(root)))
        return os.path.commonpath([normalized_path, normalized_root]) == normalized_root
    except (OSError, ValueError):
        return False


def _medien_suchwurzeln(media_type: str, media_root_path: str) -> list[Path]:
    """Liefert die festgelegten Suchwurzeln innerhalb des verbindlichen
    QKan-Medienstammordners.
    """
    if not media_root_path:
        return []
    media_root = Path(media_root_path)
    roots = [media_root]
    preferred_subdir = "Bilder" if media_type == "Bild" else "Video"
    preferred_root = media_root / preferred_subdir
    if preferred_root.is_dir():
        roots.insert(0, preferred_root)
    return roots


def _video_bandordner(media_root: Path, code: str) -> Optional[Path]:
    """Ermittelt einen historischen Bandordner innerhalb des verbindlichen
    QKan-Video-Stammordners.
    """
    if len(code) <= 5:
        return None
    folder_name = f"band{code[:-5].zfill(5)}"
    for root in _medien_suchwurzeln("Video", str(media_root)):
        folder = root / folder_name
        if folder.is_dir():
            return folder
    return None


def _direkte_medientreffer(
    media_type: str, stored_path: str, media_root_path: str
) -> tuple[Medientreffer, ...]:
    """Löst historische QKan-Medienpfade ohne vollständige Archivsuche auf. Für Fotos
    werden die bewährten direkten Pfade geprüft. Für Videos wird zusätzlich aus dem
    führenden Aufzeichnungscode genau ein Bandordner abgeleitet und geprüft.
    """
    normalized = _pfadtext_normalisieren(stored_path)
    filename = _dateiname_aus_pfad(stored_path)
    if not normalized or not filename:
        return ()

    if not media_root_path:
        return ()
    media_root = Path(media_root_path)
    if not media_root.is_dir():
        return ()

    # Der in QKan konfigurierte Stammordner ist verbindlich. Ein festes Unterverzeichnis Bilder/Video
    # ist nur zulässig, weil es innerhalb desselben Stammordners bleibt.
    roots = _medien_suchwurzeln(media_type, media_root_path)

    parts = [part for part in normalized.split("/") if part not in ("", ".", "..")]
    paths: list[tuple[Path, str, int]] = []

    for candidate_root in roots:
        if parts:
            paths.append((candidate_root.joinpath(*parts), "direkter bereinigter QKan-Pfad", 100))
        paths.append((candidate_root / filename, "Dateiname im Medienordner", 85))

    band_match = re.search(r"(?:^|/)band(\d{1,5})(?:/|$)", normalized)
    if band_match:
        band_number = band_match.group(1).zfill(5)
        for candidate_root in roots:
            paths.append((candidate_root / f"band{band_number}" / filename, "bereinigter Bandpfad", 98))

    # Bei historischen Videos besteht der führende Code aus der Bandnummer gefolgt
    # von einem fünfstelligen Aufzeichnungszähler: 17300000 -> band00173,
    # 240971358 -> band02409. Es wird ausschließlich dieser eine Ordner geprüft.
    prefix_candidate: Optional[Path] = None
    if media_type == "Video":
        number_match = re.match(r"[^0-9]*(\d{6,})", Path(filename).stem)
        if number_match:
            recording_code = number_match.group(1)
            band_digits = recording_code[:-5]
            if band_digits:
                band_folder = media_root / f"band{band_digits.zfill(5)}"
                if not band_folder.is_dir() and len(roots) > 1:
                    band_folder = roots[0] / f"band{band_digits.zfill(5)}"
                if band_folder.is_dir():
                    wanted = recording_code.casefold()
                    try:
                        for entry in os.scandir(band_folder):
                            if not entry.is_file():
                                continue
                            entry_path = Path(entry.path)
                            if entry_path.suffix.casefold() not in VIDEO_EXTENSIONS:
                                continue
                            if entry.name.casefold().startswith(wanted):
                                prefix_candidate = entry_path
                                break
                    except OSError as error:
                        _loggen(f"Videoordner konnte nicht gelesen werden: {band_folder}: {error}", Qgis.Warning)

    seen: set[str] = set()
    found: list[Medientreffer] = []
    if prefix_candidate is not None:
        paths.append((prefix_candidate, "Videocode im abgeleiteten Bandordner", 97))

    for path, method, score in paths:
        key = _pfadtext_normalisieren(path)
        if key in seen or not path.is_file():
            continue
        if media_type == "Bild" and path.suffix.casefold() not in IMAGE_EXTENSIONS:
            continue
        if media_type == "Video" and path.suffix.casefold() not in VIDEO_EXTENSIONS:
            continue
        seen.add(key)
        found.append(Medientreffer(None, None, str(path), method, score, False))
    return tuple(found)


class MediensucheArbeiter(QObject):
    """Löst Mediendateien außerhalb des QGIS-GUI-Threads auf."""

    finished = pyqtSignal(object, object, object)
    failed = pyqtSignal(str)

    def __init__(
        self,
        damage_rows: list[dict[str, Any]],
        object_column: str,
        foto_root_path: str,
        video_root_path: str,
    ) -> None:
        super().__init__()
        self.damage_rows = damage_rows
        self.object_column = object_column
        self.foto_root_path = foto_root_path
        self.video_root_path = video_root_path

    @pyqtSlot()
    def ausfuehren(self) -> None:
        try:
            photos: list[Medieneintrag] = []
            videos: list[Medieneintrag] = []
            video_timeline_cache: dict[str, list[tuple[str, int, Path]]] = {}
            video_root = Path(self.video_root_path) if self.video_root_path else None

            def zeitachse_fuer_ordner(folder: Path) -> list[tuple[str, int, Path]]:
                """Liefert sortierte Videostarts für einen historischen Bandordner."""
                cache_key = _pfadtext_normalisieren(folder)
                cached = video_timeline_cache.get(cache_key)
                if cached is not None:
                    return cached
                timeline: list[tuple[str, int, Path]] = []
                try:
                    for entry in os.scandir(folder):
                        if QThread.currentThread().isInterruptionRequested():
                            return []
                        if not entry.is_file():
                            continue
                        path = Path(entry.path)
                        if path.suffix.casefold() not in VIDEO_EXTENSIONS:
                            continue
                        code = _aufzeichnungscode_aus_dateiname(entry.name)
                        clock = _aufzeichnungscode_in_sekunden(code)
                        if code and clock is not None:
                            timeline.append((code, clock, path))
                except OSError as error:
                    _loggen(f"Videoordner konnte nicht gelesen werden: {folder}: {error}", Qgis.Warning)
                timeline.sort(key=lambda value: value[1])
                video_timeline_cache[cache_key] = timeline
                return timeline

            for damage_index, row in enumerate(self.damage_rows):
                if QThread.currentThread().isInterruptionRequested():
                    return
                caption_base = (
                    f"{_text_sicher_lesen(row.get(self.object_column))} · "
                    f"{_text_sicher_lesen(row.get('untersuchtag'))} · "
                    f"{_text_sicher_lesen(row.get('kuerzel'))} · "
                    f"Station {_gleitkommazahl_sicher_lesen(row.get('station'), 0.0):.2f} m"
                )
                for field_name, media_type in (("foto_dateiname", "Bild"), ("film_dateiname", "Video")):
                    if QThread.currentThread().isInterruptionRequested():
                        return
                    stored_path = _text_sicher_lesen(row.get(field_name)).strip()
                    if not stored_path:
                        continue
                    candidates: tuple[Medientreffer, ...] = ()
                    explicit_start = _timecode_lesen(row.get("timecode"), row.get("video_offset"))
                    start_seconds = explicit_start
                    resolution_status = ""
                    normalized_name = _dateiname_aus_pfad(stored_path)

                    if media_type == "Video" and "nicht erfasst" in normalized_name.casefold():
                        resolution_status = "Video nicht erfasst"
                    else:
                        configured_root = (
                            self.foto_root_path
                            if media_type == "Bild"
                            else self.video_root_path
                        )
                        candidates = _direkte_medientreffer(
                            media_type, stored_path, configured_root
                        )

                        if media_type == "Video" and not candidates and video_root is not None:
                            damage_code = _aufzeichnungscode_aus_dateiname(stored_path)
                            band_folder = _video_bandordner(video_root, damage_code)
                            if band_folder is not None:
                                timeline = zeitachse_fuer_ordner(band_folder)

                                damage_clock = _aufzeichnungscode_in_sekunden(damage_code)
                                if damage_clock is not None:
                                    previous = [value for value in timeline if value[1] <= damage_clock]
                                    if previous:
                                        start_code, start_clock, video_path = previous[-1]
                                        # Ein späterer Schadenscode gehört zum zuletzt gestarteten Video des Bandes.
                                        start_seconds = max(float(damage_clock - start_clock), 0.0)
                                        candidates = (Medientreffer(
                                            None, None, str(video_path),
                                            "Video der Befahrung im Bandordner", 96, False
                                        ),)
                                        resolution_status = (
                                            "Video gefunden" if start_seconds == 0
                                            else f"Video gefunden · Schadensposition {start_seconds:.0f} s"
                                        )

                    if not resolution_status:
                        if media_type == "Bild" and (
                            "band00000" in _pfadtext_normalisieren(stored_path)
                            or _dateiname_aus_pfad(stored_path).startswith("00000000.")
                        ):
                            resolution_status = "Ungültiger Bild-Platzhalter"
                        elif candidates:
                            resolution_status = candidates[0].method
                            if media_type == "Video" and explicit_start <= 0 and start_seconds <= 0:
                                resolution_status += " · keine Zeitposition gespeichert"
                        else:
                            resolution_status = (
                                "Bilddatei nicht vorhanden"
                                if media_type == "Bild"
                                else "Videodatei nicht gefunden"
                            )

                    item = Medieneintrag(
                        damage_index=damage_index, media_type=media_type,
                        stored_path=stored_path, candidates=candidates,
                        caption=caption_base, start_seconds=start_seconds,
                        resolution_status=resolution_status,
                    )
                    (photos if media_type == "Bild" else videos).append(item)
            inspection_video: Optional[Medieneintrag] = None

            # Eine bereits aufgelöste Videoreferenz aus der Inspektion hat Vorrang.
            for video in videos:
                if video.candidates:
                    inspection_video = Medieneintrag(
                        damage_index=video.damage_index,
                        media_type="Video",
                        stored_path=video.stored_path,
                        candidates=video.candidates,
                        caption="Befahrungsvideo",
                        start_seconds=0.0,
                        resolution_status="Befahrungsvideo verlinkt",
                    )
                    break

            # Manche QKan-Datensätze enthalten in den Schadenszeilen keinen film_dateiname.
            # In diesem Fall wird das Befahrungsvideo aus dem ermittelten Band und den
            # Aufzeichnungszähler-Informationen der Fotoreferenzen abgeleitet.
            if inspection_video is None:
                for damage_index, row in enumerate(self.damage_rows):
                    code = _aufzeichnungscode_aus_dateiname(row.get("foto_dateiname"))
                    if not code:
                        band = re.sub(r"[^0-9]", "", _text_sicher_lesen(row.get("bandnr")))
                        counter = re.sub(r"[^0-9]", "", _text_sicher_lesen(row.get("videozaehler")))
                        if band and counter:
                            code = f"{int(band)}{counter.zfill(5)}"
                    band_folder = (
                        _video_bandordner(video_root, code)
                        if video_root is not None
                        else None
                    )
                    damage_clock = _aufzeichnungscode_in_sekunden(code)
                    if band_folder is None or damage_clock is None:
                        continue
                    timeline = zeitachse_fuer_ordner(band_folder)
                    previous = [value for value in timeline if value[1] <= damage_clock]
                    selected = previous[-1] if previous else (timeline[0] if timeline else None)
                    if selected is None:
                        continue
                    _start_code, _start_clock, video_path = selected
                    inspection_video = Medieneintrag(
                        damage_index=damage_index,
                        media_type="Video",
                        stored_path=str(video_path),
                        candidates=(Medientreffer(
                            None, None, str(video_path),
                            "Befahrungsvideo im Bandordner", 95, False
                        ),),
                        caption="Befahrungsvideo",
                        start_seconds=0.0,
                        resolution_status="Befahrungsvideo verlinkt",
                    )
                    break

            # Ist das Befahrungsvideo bekannt, enthalten die Schadenszeilen aber keine
            # ausdrückliche Filmreferenz, werden die Videopositionen aus dem historischen
            # Aufzeichnungscode des Fotodateinamens oder aus
            # ``bandnr`` + ``videozaehler`` abgeleitet. Direkte Videozeilen bleiben unverändert
            # und haben immer Vorrang.
            # Nur eine tatsächlich aufgelöste Videozeile verhindert den Rückfall. Historische
            # Datensätze können für jeden Schaden einen nicht auflösbaren ``film_dateiname``
            # enthalten, obwohl im Bandordner ein gültiges Befahrungsvideo vorhanden ist.
            # Diese nicht aufgelösten Zeilen müssen durch berechnete Positionen ersetzt
            # werden, statt den Rückfall zu unterdrücken.
            resolved_video_damage_indexes = {
                video.damage_index for video in videos if video.candidates
            }
            for damage_index, row in enumerate(self.damage_rows):
                if QThread.currentThread().isInterruptionRequested():
                    return
                if damage_index in resolved_video_damage_indexes:
                    continue

                damage_code = _aufzeichnungscode_aus_dateiname(row.get("foto_dateiname"))
                if not damage_code:
                    band = re.sub(r"[^0-9]", "", _text_sicher_lesen(row.get("bandnr")))
                    counter = re.sub(r"[^0-9]", "", _text_sicher_lesen(row.get("videozaehler")))
                    if band and counter:
                        damage_code = f"{int(band)}{counter.zfill(5)}"

                damage_clock = _aufzeichnungscode_in_sekunden(damage_code)
                band_folder = (
                    _video_bandordner(video_root, damage_code)
                    if video_root is not None
                    else None
                )
                if damage_clock is None or band_folder is None:
                    continue

                timeline = zeitachse_fuer_ordner(band_folder)
                previous = [value for value in timeline if value[1] <= damage_clock]
                if not previous:
                    continue

                _start_code, start_clock, video_path = previous[-1]
                start_seconds = float(damage_clock - start_clock)
                caption = (
                    f"{_text_sicher_lesen(row.get(self.object_column))} · "
                    f"{_text_sicher_lesen(row.get('untersuchtag'))} · "
                    f"{_text_sicher_lesen(row.get('kuerzel'))} · "
                    f"Station {_gleitkommazahl_sicher_lesen(row.get('station'), 0.0):.2f} m"
                )
                # Nur nicht aufgelöste Einträge dieses Schadens entfernen. Bereits aufgelöste
                # direkte Zuordnungen behalten Vorrang und wurden oben übersprungen.
                videos = [
                    video for video in videos
                    if video.damage_index != damage_index or video.candidates
                ]
                videos.append(Medieneintrag(
                    damage_index=damage_index,
                    media_type="Video",
                    stored_path=str(video_path),
                    candidates=(Medientreffer(
                        None, None, str(video_path),
                        "Videoposition aus Bandnummer und Videozähler berechnet",
                        94, False,
                    ),),
                    caption=caption,
                    start_seconds=start_seconds,
                    resolution_status=(
                        "Videostelle aus Aufzeichnungszähler berechnet · "
                        f"{start_seconds:.0f} s"
                    ),
                ))

            videos.sort(key=lambda item: item.damage_index)
            self.finished.emit(photos, videos, inspection_video)
        except Exception as error:  # Die QGIS-Oberfläche bei unerwarteten Ein-/Ausgabefehlern funktionsfähig halten
            self.failed.emit(str(error))

def _text_sicher_lesen(value: Any) -> str:
    """Wandelt einen Datenbankwert sicher in Anzeigetext um."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.decode("latin-1", errors="replace")
    return str(value)


def _gleitkommazahl_sicher_lesen(value: Any, default: float = 0.0) -> float:
    """Wandelt übliche Datenbankwerte sicher in eine Gleitkommazahl um."""
    if value in (None, "", "NULL"):
        return default
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def _befahrungsdatum_sortierwert(value: Any) -> tuple[int, str]:
    """Erzeugt einen Sortierwert für historische Befahrungsdatumsformate mit neuestem
    Datum zuerst.
    """
    text = _text_sicher_lesen(value).strip()
    for date_format in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ):
        try:
            parsed = datetime.strptime(text, date_format)
            return int(parsed.strftime("%Y%m%d%H%M%S")), text
        except ValueError:
            continue
    return 0, text.casefold()


def _timecode_lesen(value: Any, offset: Any = 0.0) -> float:
    """Wandelt QKan-/M150-Timecodes und Versätze in Sekunden um. Unterstützt werden
    unter anderem ``HH:MM:SS``, Dezimalsekunden sowie kompakte M150-Formate wie
    ``HHMMSSCC``, ``HHMMSS`` und ``MMSS``.
    """
    result = _gleitkommazahl_sicher_lesen(offset, 0.0)
    text = _text_sicher_lesen(value).strip()
    if not text or text.upper() == "NULL":
        return max(result, 0.0)

    if ":" in text:
        parts = text.replace(",", ".").split(":")
        try:
            numbers = [float(part) for part in parts]
        except ValueError:
            return max(result, 0.0)
        if len(numbers) == 3:
            result += numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
        elif len(numbers) == 2:
            result += numbers[0] * 60 + numbers[1]
        elif len(numbers) == 1:
            result += numbers[0]
        return max(result, 0.0)

    compact = re.sub(r"[^0-9]", "", text)
    if not compact:
        return max(result, 0.0)

    try:
        if len(compact) >= 8:
            compact = compact[-8:]
            hours = int(compact[0:2])
            minutes = int(compact[2:4])
            seconds = int(compact[4:6])
            centiseconds = int(compact[6:8])
            result += hours * 3600 + minutes * 60 + seconds + centiseconds / 100
        elif len(compact) == 6:
            result += int(compact[0:2]) * 3600
            result += int(compact[2:4]) * 60
            result += int(compact[4:6])
        elif len(compact) in (4, 5):
            result += int(compact[:-2]) * 60 + int(compact[-2:])
        else:
            result += float(text.replace(",", "."))
    except ValueError:
        pass
    return max(result, 0.0)


def _sqlite_verbindung(path: str, query_only: bool = False) -> sqlite3.Connection:
    """Öffnet SQLite mit benannten Spalten und optionalem Nur-Lese-Schutz."""
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")
    if query_only:
        connection.execute("PRAGMA query_only = ON")
    return connection


def _tabellennamen_lesen(connection: sqlite3.Connection) -> set[str]:
    """Liefert die Namen aller regulären Tabellen."""
    return {
        _text_sicher_lesen(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def _tabellenspalten_lesen(connection: sqlite3.Connection, table: str) -> set[str]:
    """Liefert die Spalten einer SQLite-Tabelle."""
    return {
        _text_sicher_lesen(row[1])
        for row in connection.execute(
            f"PRAGMA table_info({_sql_bezeichner_quotieren(table)})"
        ).fetchall()
    }


def _dialog_ausfuehren(dialog: QDialog) -> int:
    """Führt einen Dialog sowohl mit Qt 5 als auch Qt 6 aus."""
    execute = getattr(dialog, "exec", None)
    if callable(execute):
        return int(execute())
    return int(dialog.exec_())


class ObjektauswahlWerkzeug(QgsMapToolIdentify):
    """Wählt ein angeklicktes QKan-Objekt aus und hält den Auswahlmodus aktiv."""

    object_picked = pyqtSignal(str, str)
    selection_cancelled = pyqtSignal()

    # ``leitnam`` muss vor ``haltnam`` geprüft werden, weil QKan-
    # Anschlussleitungs-Layer ebenfalls einen Verweis auf eine Haltung enthalten können.
    FIELD_CONFIG = (
        ("Anschlussleitung", "leitnam"),
        ("Schacht", "schnam"),
        ("Haltung", "haltnam"),
    )

    LAYER_HINTS = (
        ("Anschlussleitung", "leitnam", ("anschlussleitung", "anschlussleitungen")),
        ("Schacht", "schnam", ("schacht", "schaechte", "schächte")),
        ("Haltung", "haltnam", ("haltung", "haltungen")),
    )

    @classmethod
    def _objektart_aus_layer(cls, layer: Any, feature: QgsFeature) -> Optional[tuple[str, str]]:
        """Bestimmt die Objektart zuerst über Layer bzw. Tabelle und erst danach über
        Feldnamen.
        """
        field_names = {field.name().casefold(): field.name() for field in layer.fields()}
        layer_text = f"{layer.name()} {layer.source()}".casefold()

        for object_type, expected_field, hints in cls.LAYER_HINTS:
            actual_field = field_names.get(expected_field.casefold())
            if actual_field is None or not any(hint in layer_text for hint in hints):
                continue
            object_name = _text_sicher_lesen(feature[actual_field]).strip()
            if object_name:
                return object_type, object_name

        for object_type, expected_field in cls.FIELD_CONFIG:
            actual_field = field_names.get(expected_field.casefold())
            if actual_field is None:
                continue
            object_name = _text_sicher_lesen(feature[actual_field]).strip()
            if object_name:
                return object_type, object_name
        return None

    def canvasReleaseEvent(self, event: Any) -> None:
        """Ermittelt das nächstgelegene angeklickte QKan-Objekt; Rechtsklick beendet
        den Modus.
        """
        if event.button() == Qt.RightButton:
            self.selection_cancelled.emit()
            return

        results = self.identify(
            event.x(),
            event.y(),
            self.TopDownAll,
            self.VectorLayer,
        )
        matches: list[tuple[float, int, str, str, str]] = []
        try:
            map_point = event.mapPoint()
        except AttributeError:
            map_point = self.toMapCoordinates(event.pos())

        for result_index, result in enumerate(results):
            layer = result.mLayer
            feature = result.mFeature
            if layer is None or layer.type() != QgsMapLayerType.VectorLayer:
                continue
            resolved = self._objektart_aus_layer(layer, feature)
            if resolved is None:
                continue
            object_type, object_name = resolved

            distance = float("inf")
            geometry = feature.geometry()
            if geometry is not None and not geometry.isEmpty():
                try:
                    layer_point = self.canvas().mapSettings().mapToLayerCoordinates(layer, map_point)
                    distance = geometry.distance(QgsGeometry.fromPointXY(layer_point))
                except Exception:
                    distance = float(result_index)
            matches.append((distance, result_index, object_type, object_name, layer.name()))

        if not matches:
            QMessageBox.warning(
                self.canvas(),
                "Kein QKan-Objekt erkannt",
                "An der angeklickten Stelle wurde keine Haltung, Anschlussleitung "
                "oder kein Schacht mit haltnam, leitnam beziehungsweise schnam gefunden.",
            )
            return

        matches.sort(key=lambda item: (item[0], item[1]))
        _distance, _result_index, object_type, object_name, _layer_name = matches[0]
        self.object_picked.emit(object_type, object_name)


class BefahrungsmedienDialog(QDialog):
    """Foto-, Video- und Schadensansicht für QKan-Inspektionsdaten."""

    def __init__(self, iface: Any, parent: Optional[QWidget] = None, viewer_only: bool = False) -> None:
        super().__init__(parent or iface.mainWindow())
        self.iface = iface
        self.viewer_only = viewer_only
        self.setWindowTitle("QKan Medieninspektor – Objektansicht" if viewer_only else "QKan Medieninspektor")

        self.qkan_database = ""
        self.damage_rows: list[dict[str, Any]] = []
        self.photo_items: list[Medieneintrag] = []
        self.video_items: list[Medieneintrag] = []
        self.inspection_video: Optional[Medieneintrag] = None
        self.current_photo_index = -1
        self.current_object_length = 1.0
        self.current_overall: Optional[dict[str, Any]] = None
        self.current_connections: list[dict[str, Any]] = []
        self.current_date_value = ""
        self.current_all_dates = False
        self.foto_root_path = ""
        self.video_root_path = ""
        self._deleted_damage_rowids: set[int] = set()
        self._table_dirty = False
        self._rating_dirty = False
        self._filling_damage_table = False
        self._media_thread: Optional[QThread] = None
        self._media_worker: Optional[MediensucheArbeiter] = None
        self._media_run_id = 0
        self._last_media_path_error = ""
        self._media_timeout = QTimer(self)
        self._media_timeout.setSingleShot(True)
        self._media_timeout.timeout.connect(self._medienaufloesung_zeitueberschritten)

        self._oberflaeche_aufbauen()
        self._signale_verbinden()
        self._projekteinstellungen_laden()
        QTimer.singleShot(0, self._datenquellen_initialisieren)

    def _oberflaeche_aufbauen(self) -> None:
        """Lädt alle statischen Widgets und Layouts aus der Qt-Designer-UI-Datei."""
        ui_path = Path(__file__).parent / "res" / "befahrungsmedien.ui"
        if not ui_path.is_file():
            raise FileNotFoundError(f"UI-Datei nicht gefunden: {ui_path}")

        uic.loadUi(str(ui_path), self)
        self.setWindowTitle(
            "QKan Medieninspektor – Objektansicht"
            if self.viewer_only
            else "QKan Medieninspektor"
        )

        # In Python verbleibt nur laufzeitabhängiges Verhalten. Alle Widgets,
        # Texte, Layouts, Registerkarten und Buttonzeilen sind in der .ui-Datei definiert.
        self.cb_objekt.setInsertPolicy(QComboBox.NoInsert)
        self.tw_schaeden.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )
        self.tw_schaeden.verticalHeader().setVisible(False)
        self.tw_schaeden.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.Stretch
        )
        for column in (0, 1, 2, 3, 5, 6, 7, 8, 9, 10):
            self.tw_schaeden.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeToContents
            )

        self.tw_videos.verticalHeader().setVisible(False)
        self.tw_videos.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.Stretch
        )
        for column in range(5):
            self.tw_videos.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeToContents
            )

        self.main_splitter.setStretchFactor(0, 3)
        self.main_splitter.setStretchFactor(1, 2)
        if self.viewer_only:
            self.sources_group.hide()

    def _signale_verbinden(self) -> None:
        """Verbindet alle Benutzeraktionen mit ihren Funktionen."""
        self.pb_datenbank_waehlen.clicked.connect(self._datenbank_waehlen)
        self.cb_objektart.currentTextChanged.connect(self._objekte_laden)
        self.cb_objekt.currentTextChanged.connect(self._befahrungen_laden)
        self.cb_befahrung.currentTextChanged.connect(self._ansicht_laden)
        self.tw_schaeden.currentCellChanged.connect(self._schadensauswahl_geaendert)
        self.tw_schaeden.itemChanged.connect(self._schadenseintrag_geaendert)
        self.pb_eintrag_hinzufuegen.clicked.connect(self._schadenseintrag_hinzufuegen)
        self.pb_eintrag_loeschen.clicked.connect(self._schadenseintrag_loeschen)
        self.pb_speichern.clicked.connect(self._schadensaenderungen_speichern)
        self.pb_neu_bewerten.clicked.connect(self._bewertung_neu_berechnen)
        self.pb_grafik_exportieren.clicked.connect(self._grafik_exportieren)
        self.inspektionsgrafik.damage_clicked.connect(self._schadenszeile_auswaehlen)
        self.pb_foto_vorheriges.clicked.connect(lambda: self._foto_wechseln(-1))
        self.pb_foto_naechstes.clicked.connect(lambda: self._foto_wechseln(1))
        self.pb_foto_extern_oeffnen.clicked.connect(self._foto_extern_oeffnen)
        self.pb_foto_ordner_oeffnen.clicked.connect(self._fotoordner_oeffnen)
        self.tw_videos.currentCellChanged.connect(self._videoauswahl_geaendert)
        self.pb_schadensvideo_oeffnen.clicked.connect(self._ausgewaehltes_video_oeffnen)
        self.pb_befahrungsvideo_oeffnen.clicked.connect(self._befahrungsvideo_oeffnen)
        self.pb_video_ordner_oeffnen.clicked.connect(self._videoordner_oeffnen)
        self.pb_panoramo_oeffnen.clicked.connect(self._panoramo_oeffnen)
        self.pb_panoramo_ordner_oeffnen.clicked.connect(self._panoramoordner_oeffnen)

    def _projekteinstellungen_laden(self) -> None:
        """Stellt den projektspezifischen QKan-Datenbankpfad wieder her."""
        project = QgsProject.instance()
        self.qkan_database = self._gespeicherten_pfad_aufloesen(
            _text_sicher_lesen(project.readEntry(PLUGIN_GROUP, "qkanDatabase", "")[0]),
            _text_sicher_lesen(project.readEntry(PLUGIN_GROUP, "qkanDatabaseRelative", "")[0]),
        )
        self.le_datenbank.setText(self.qkan_database)

    def _gespeicherten_pfad_aufloesen(self, absolute: str, relative: str) -> str:
        """Löst zuerst einen projekt-relativen und danach den gespeicherten absoluten
        Pfad auf.
        """
        project_directory = QgsProject.instance().absolutePath()
        if relative and project_directory:
            candidate = Path(project_directory) / relative
            if candidate.is_file():
                return str(candidate)
        return absolute

    def _projektpfad_speichern(self, key: str, path: str) -> None:
        """Speichert absolute und projekt-relative Pfade im QGIS-Projekt."""
        project = QgsProject.instance()
        project.writeEntry(PLUGIN_GROUP, key, path)
        relative = ""
        project_directory = project.absolutePath()
        if project_directory and path:
            try:
                relative = os.path.relpath(path, project_directory)
            except ValueError:
                relative = ""
        project.writeEntry(PLUGIN_GROUP, key + "Relative", relative)
        project.setDirty(True)

    def _datenquellen_initialisieren(self) -> None:
        """Ermittelt die QKan-Datenbank; die kompakte Ansicht wartet auf das
        angeklickte Objekt.
        """
        if not self.qkan_database or not Path(self.qkan_database).is_file():
            inferred = self._qkan_datenbank_ermitteln()
            if inferred:
                self._datenbank_setzen(inferred, objekte_laden=not self.viewer_only)
                return
        if (
            not self.viewer_only
            and self.qkan_database
            and Path(self.qkan_database).is_file()
        ):
            self._objekte_laden()

    def _qkan_datenbank_ermitteln(self) -> str:
        """Sucht in den geladenen Projektlayern nach einem QKan-SQLite-Pfad."""
        pattern = re.compile(r"([A-Za-z]:[/\\][^|\"']+\.(?:sqlite|db|gpkg))", re.I)
        for layer in QgsProject.instance().mapLayers().values():
            source = _text_sicher_lesen(layer.source())
            plain = source.split("|", 1)[0].strip('"').strip("'")
            candidates = [plain]
            match = pattern.search(source)
            if match:
                candidates.append(match.group(1))
            for candidate in candidates:
                if candidate and Path(candidate).is_file() and self._ist_qkan_datenbank(candidate):
                    return candidate
        return ""

    @staticmethod
    def _ist_qkan_datenbank(path: str) -> bool:
        """Prüft auf die drei unterstützten Inspektionsdetailtabellen."""
        try:
            connection = _sqlite_verbindung(path, query_only=True)
            try:
                existing = _tabellennamen_lesen(connection)
                return any(
                    config["detail_table"] in existing
                    for config in OBJECT_CONFIG.values()
                )
            finally:
                connection.close()
        except sqlite3.Error:
            return False


    def _datenbank_setzen(self, path: str, objekte_laden: bool = True) -> None:
        """Prüft und speichert die ausgewählte QKan-Datenbank."""
        if not self._ist_qkan_datenbank(path):
            raise RuntimeError("Die Datei enthält keine unterstützten QKan-Inspektionstabellen.")
        self.qkan_database = path
        self.le_datenbank.setText(path)
        self._projektpfad_speichern("qkanDatabase", path)
        if objekte_laden:
            self._objekte_laden()

    def _datenbank_waehlen(self) -> None:
        """Wählt eine QKan-SQLite-Datenbank aus."""
        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "QKan-SQLite auswählen",
            str(Path(self.qkan_database).parent) if self.qkan_database else "",
            "SQLite-Datenbanken (*.sqlite *.sqlite3 *.db *.gpkg);;Alle Dateien (*)",
        )
        if not path:
            return
        try:
            self._datenbank_setzen(path)
        except Exception as error:
            QMessageBox.critical(self, "Ungültige QKan-Datenbank", _text_sicher_lesen(error))


    def _objekt_auswaehlen(self, object_type: str, object_name: str) -> None:
        """Öffnet genau das auf der Karte ausgewählte Objekt, ohne vorher einen fremden
        Listeneintrag zu laden.
        """
        if object_type not in OBJECT_CONFIG:
            raise ValueError(f"Unbekannte Objektart: {object_type}")

        if not self.qkan_database or not Path(self.qkan_database).is_file():
            inferred = self._qkan_datenbank_ermitteln()
            if inferred:
                self._datenbank_setzen(inferred, objekte_laden=False)
        if not self.qkan_database or not Path(self.qkan_database).is_file():
            self._ansicht_leeren()
            QMessageBox.warning(
                self,
                "Keine QKan-Datenbank",
                "Die QKan-Datenbank konnte aus dem aktuellen Projekt nicht ermittelt werden.",
            )
            return

        type_index = self.cb_objektart.findText(object_type)
        if type_index >= 0:
            previous_block = self.cb_objektart.blockSignals(True)
            try:
                self.cb_objektart.setCurrentIndex(type_index)
            finally:
                self.cb_objektart.blockSignals(previous_block)

        # Hier nur füllen. Das Laden des ersten ComboBox-Eintrags würde bereits eine
        # Mediensuche für ein fremdes Objekt starten, bevor das angeklickte Objekt feststeht.
        self._objekte_laden(ansicht_laden=False)
        object_index = self.cb_objekt.findText(object_name, Qt.MatchFixedString)
        if object_index < 0:
            previous_block = self.cb_objekt.blockSignals(True)
            try:
                self.cb_objekt.setCurrentIndex(-1)
            finally:
                self.cb_objekt.blockSignals(previous_block)
            self._ansicht_leeren()
            self.lbl_status.setText(
                f"Für {object_type} {object_name} sind keine Befahrungsdaten vorhanden."
            )
            QMessageBox.information(
                self,
                "Keine Befahrungsdaten",
                f"Für {object_type} {object_name} wurden in der gewählten QKan-Datenbank "
                "keine Inspektionsdaten gefunden.",
            )
            return

        previous_block = self.cb_objekt.blockSignals(True)
        try:
            self.cb_objekt.setCurrentIndex(object_index)
        finally:
            self.cb_objekt.blockSignals(previous_block)

        self._befahrungen_laden(ansicht_laden=False)
        if self.cb_befahrung.count() <= 2:
            self._ansicht_leeren()
            self.lbl_status.setText(
                f"Für {object_type} {object_name} ist kein Befahrungsdatum vorhanden."
            )
            QMessageBox.information(
                self,
                "Keine Befahrungsdaten",
                f"Für {object_type} {object_name} ist kein Befahrungsdatum hinterlegt.",
            )
            return

        previous_block = self.cb_befahrung.blockSignals(True)
        try:
            self.cb_befahrung.setCurrentIndex(0)
        finally:
            self.cb_befahrung.blockSignals(previous_block)
        self._ansicht_laden()

    def _objekte_laden(self, _value: str = "", ansicht_laden: bool = True) -> None:
        """Lädt die Objektnamen für die ausgewählte Inspektionsart."""
        self.cb_objekt.blockSignals(True)
        self.cb_objekt.clear()
        self.cb_objekt.blockSignals(False)
        self.cb_befahrung.clear()
        self._ansicht_leeren()
        if not self.qkan_database or not Path(self.qkan_database).is_file():
            return
        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        connection = _sqlite_verbindung(self.qkan_database, query_only=True)
        try:
            if config["detail_table"] not in _tabellennamen_lesen(connection):
                self.lbl_status.setText(
                    f"Tabelle {config['detail_table']} ist in dieser Datenbank nicht vorhanden."
                )
                return
            rows = connection.execute(
                f"""
                SELECT DISTINCT {_sql_bezeichner_quotieren(config['object_column'])}
                FROM {_sql_bezeichner_quotieren(config['detail_table'])}
                WHERE TRIM(COALESCE({_sql_bezeichner_quotieren(config['object_column'])}, '')) <> ''
                ORDER BY {_sql_bezeichner_quotieren(config['object_column'])}
                """
            ).fetchall()
            self.cb_objekt.blockSignals(True)
            self.cb_objekt.addItems([_text_sicher_lesen(row[0]) for row in rows])
            self.cb_objekt.blockSignals(False)
            self.lbl_status.setText(f"{len(rows):,} Objekte geladen.")
        finally:
            connection.close()
        if ansicht_laden:
            self._befahrungen_laden()

    def _befahrungen_laden(self, _value: str = "", ansicht_laden: bool = True) -> None:
        """Lädt die verfügbaren Inspektionsdaten für das ausgewählte Objekt."""
        self.cb_befahrung.blockSignals(True)
        self.cb_befahrung.clear()
        self.cb_befahrung.addItem("Aktuellste Befahrung")
        self.cb_befahrung.addItem("Alle Befahrungen")
        self.cb_befahrung.blockSignals(False)
        object_name = self.cb_objekt.currentText().strip()
        if not object_name or not self.qkan_database:
            self._ansicht_leeren()
            return
        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        connection = _sqlite_verbindung(self.qkan_database, query_only=True)
        try:
            rows = connection.execute(
                f"""
                SELECT DISTINCT untersuchtag
                FROM {_sql_bezeichner_quotieren(config['detail_table'])}
                WHERE {_sql_bezeichner_quotieren(config['object_column'])} = ?
                  AND TRIM(COALESCE(untersuchtag, '')) <> ''
                """,
                (object_name,),
            ).fetchall()
            date_values = sorted(
                (_text_sicher_lesen(row[0]) for row in rows),
                key=_befahrungsdatum_sortierwert,
                reverse=True,
            )
            self.cb_befahrung.blockSignals(True)
            for date_value in date_values:
                self.cb_befahrung.addItem(date_value)
            self.cb_befahrung.blockSignals(False)
        finally:
            connection.close()
        if ansicht_laden:
            self._ansicht_laden()

    def _ausgewaehltes_datum(self, connection: sqlite3.Connection) -> tuple[str, bool]:
        """Löst die aktuelle Datumsauswahl in ein ISO-Datum und ein Kennzeichen für
        alle Daten auf.
        """
        selection = self.cb_befahrung.currentText()
        if selection == "Alle Befahrungen":
            return "", True
        if selection != "Aktuellste Befahrung":
            return selection, False
        if self.cb_befahrung.count() > 2:
            return self.cb_befahrung.itemText(2), False
        return "", False

    def _ansicht_laden(self, _value: str = "") -> None:
        """Lädt Schäden, Gesamtbewertung, Schema und Medienlisten."""
        object_name = self.cb_objekt.currentText().strip()
        if not object_name or not self.qkan_database or not Path(self.qkan_database).is_file():
            self._ansicht_leeren()
            return
        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        connection = _sqlite_verbindung(self.qkan_database, query_only=True)
        try:
            date_value, all_dates = self._ausgewaehltes_datum(connection)
            where = f"{_sql_bezeichner_quotieren(config['object_column'])} = ?"
            parameters: list[Any] = [object_name]
            if not all_dates:
                where += " AND untersuchtag = ?"
                parameters.append(date_value)
            detail_columns = _tabellenspalten_lesen(connection, config["detail_table"])
            if "station" in detail_columns:
                position_order = "COALESCE(station, 0)"
            elif "vertikale_lage" in detail_columns:
                position_order = "COALESCE(vertikale_lage, 0)"
            else:
                position_order = "rowid"
            query = (
                f"SELECT rowid AS source_rowid, * "
                f"FROM {_sql_bezeichner_quotieren(config['detail_table'])} "
                f"WHERE {where} "
                f"ORDER BY untersuchtag DESC, {position_order}, rowid"
            )
            self.damage_rows = [dict(row) for row in connection.execute(query, parameters)]
            overall = self._gesamtbewertung_laden(connection, object_name, date_value, all_dates)
        finally:
            connection.close()

        self.current_date_value = date_value
        self.current_all_dates = all_dates
        self.current_overall = overall
        self._deleted_damage_rowids.clear()
        self._table_dirty = False
        self._rating_dirty = False
        self._schadenstabelle_fuellen()
        self.current_object_length = self._objektlaenge_bestimmen(overall)
        self.current_connections = self._anschlussinformationen_laden(
            object_name, date_value, all_dates, overall
        )
        self.inspektionsgrafik.daten_setzen(
            self.damage_rows,
            self.cb_objektart.currentText(),
            self.current_object_length,
            self.current_connections,
        )
        self._gesamtbewertung_anzeigen(object_name, date_value, all_dates, overall)
        self._medienlisten_erstellen()

    def _gesamtbewertung_laden(
        self,
        connection: sqlite3.Connection,
        object_name: str,
        date_value: str,
        all_dates: bool,
    ) -> Optional[dict[str, Any]]:
        """Liest die Gesamtbewertung des aktuellen Objekts und der aktuellen
        Inspektion.
        """
        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        existing = _tabellennamen_lesen(connection)
        if config["overall_table"] not in existing:
            return None
        where = f"{_sql_bezeichner_quotieren(config['overall_object_column'])} = ?"
        parameters: list[Any] = [object_name]
        if not all_dates and date_value:
            where += " AND untersuchtag = ?"
            parameters.append(date_value)
        row = connection.execute(
            f"""
            SELECT rowid AS source_rowid, *
            FROM {_sql_bezeichner_quotieren(config['overall_table'])}
            WHERE {where}
            ORDER BY untersuchtag DESC, rowid DESC
            LIMIT 1
            """,
            parameters,
        ).fetchone()
        return dict(row) if row is not None else None

    def _objektlaenge_bestimmen(self, overall: Optional[dict[str, Any]]) -> float:
        """Bestimmt die Darstellungsstrecke aus Gesamt- oder Schadensdaten."""
        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        if overall is not None:
            length = _gleitkommazahl_sicher_lesen(overall.get(config["length_column"]), 0.0)
            if length > 0:
                return length
        candidates = [
            _gleitkommazahl_sicher_lesen(row.get("inspektionslaenge"), 0.0)
            for row in self.damage_rows
        ]
        candidates.extend(
            _gleitkommazahl_sicher_lesen(row.get("station"), 0.0)
            for row in self.damage_rows
        )
        candidates.extend(
            _gleitkommazahl_sicher_lesen(row.get("vertikale_lage"), 0.0)
            for row in self.damage_rows
        )
        return max(candidates + [1.0])

    def _gesamtbewertung_anzeigen(
        self,
        object_name: str,
        date_value: str,
        all_dates: bool,
        overall: Optional[dict[str, Any]],
    ) -> None:
        """Zeigt die Felder der Gesamtbewertung an."""
        self.rating_object_label.setText(f"Objekt: {object_name}")
        shown_date = "alle" if all_dates else date_value or "–"
        self.rating_date_label.setText(f"Befahrung: {shown_date}")
        if overall is None:
            self.rating_zd_label.setText("ZD: –")
            self.rating_zb_label.setText("ZB: –")
            self.rating_zs_label.setText("ZS: –")
            self.rating_info_label.setText(
                f"Länge/Abmessung: {self.current_object_length:.2f}"
            )
            return
        self.rating_zd_label.setText(f"ZD: {_text_sicher_lesen(overall.get('max_ZD')) or '–'}")
        self.rating_zb_label.setText(f"ZB: {_text_sicher_lesen(overall.get('max_ZB')) or '–'}")
        self.rating_zs_label.setText(f"ZS: {_text_sicher_lesen(overall.get('max_ZS')) or '–'}")
        self.rating_info_label.setText(
            f"Länge/Abmessung: {self._objektlaenge_bestimmen(overall):.2f}"
        )

    @staticmethod
    def _wert_fuer_vergleich(value: Any) -> str:
        """Normalisiert QGIS-Datums- und Textwerte für stabile Feature-Vergleiche."""
        if value is None:
            return ""
        to_string = getattr(value, "toString", None)
        if callable(to_string):
            try:
                text = to_string("yyyy-MM-dd")
            except TypeError:
                text = to_string()
            if text:
                return str(text).strip()
        return _text_sicher_lesen(value).strip()

    @staticmethod
    def _linien_endpunkte(
        geometry: Optional[QgsGeometry],
    ) -> Optional[tuple[QgsPointXY, QgsPointXY]]:
        """Liefert ersten und letzten Punkt des ersten nutzbaren Linienteils."""
        if geometry is None or geometry.isEmpty():
            return None
        points: list[Any] = []
        if geometry.isMultipart():
            parts = geometry.asMultiPolyline()
            points = next((part for part in parts if len(part) >= 2), [])
        else:
            points = geometry.asPolyline()
        if len(points) < 2:
            points = list(geometry.vertices())
        if len(points) < 2:
            return None
        return QgsPointXY(points[0]), QgsPointXY(points[-1])

    def _gesamtobjekt_daten_laden(
        self,
        object_type: str,
        object_name: str,
        date_value: str,
        base_fallback: bool = False,
    ) -> Optional[dict[str, Any]]:
        """Lädt Attribute und Geometrie eines untersuchten Objekts über QGIS/OGR."""
        config = OBJECT_CONFIG[object_type]
        table_name = config["overall_table"]
        object_column = config["overall_object_column"]
        layer = QgsVectorLayer(f"{self.qkan_database}|layername={table_name}", table_name, "ogr")
        candidates: list[QgsFeature] = []
        if layer.isValid():
            for feature in layer.getFeatures():
                if self._wert_fuer_vergleich(feature[object_column]) != object_name:
                    continue
                if date_value and self._wert_fuer_vergleich(feature["untersuchtag"]) != date_value:
                    continue
                candidates.append(feature)
        if candidates:
            feature = max(candidates, key=lambda value: int(value.id()))
            return {
                "attributes": {name: feature[name] for name in feature.fields().names()},
                "geometry": QgsGeometry(feature.geometry()) if feature.hasGeometry() else None,
                "feature_id": int(feature.id()),
                "table": table_name,
            }

        if not base_fallback:
            return None
        base_config = {
            "Haltung": ("haltungen", "haltnam"),
            "Anschlussleitung": ("anschlussleitungen", "leitnam"),
            "Schacht": ("schaechte", "schnam"),
        }
        base_table, base_column = base_config[object_type]
        base_layer = QgsVectorLayer(
            f"{self.qkan_database}|layername={base_table}", base_table, "ogr"
        )
        if not base_layer.isValid():
            return None
        for feature in base_layer.getFeatures():
            if self._wert_fuer_vergleich(feature[base_column]) == object_name:
                return {
                    "attributes": {name: feature[name] for name in feature.fields().names()},
                    "geometry": QgsGeometry(feature.geometry()) if feature.hasGeometry() else None,
                    "feature_id": int(feature.id()),
                    "table": base_table,
                }
        return None

    @staticmethod
    def _lokale_normalenbasis(
        line_geometry: QgsGeometry, geom_station: float
    ) -> Optional[tuple[QgsPointXY, float, float]]:
        """Liefert Stationspunkt und rechten Normalenvektor einer Liniengeometrie."""
        if line_geometry is None or line_geometry.isEmpty():
            return None
        total_length = line_geometry.length()
        if total_length <= 0.000001:
            return None
        point_geometry = line_geometry.interpolate(max(0.0, min(total_length, geom_station)))
        if point_geometry is None or point_geometry.isEmpty():
            return None
        point = QgsPointXY(point_geometry.asPoint())
        delta = min(0.25, max(total_length / 100.0, 0.05))
        station_a = max(0.0, geom_station - delta)
        station_b = min(total_length, geom_station + delta)
        if abs(station_b - station_a) < 0.000001:
            return None
        geom_a = line_geometry.interpolate(station_a)
        geom_b = line_geometry.interpolate(station_b)
        if geom_a is None or geom_a.isEmpty() or geom_b is None or geom_b.isEmpty():
            return None
        point_a = geom_a.asPoint()
        point_b = geom_b.asPoint()
        dx = point_b.x() - point_a.x()
        dy = point_b.y() - point_a.y()
        chord = math.hypot(dx, dy)
        if chord <= 0.000001:
            return None
        return point, dy / chord, -dx / chord

    @staticmethod
    def _seitenfaktor_aus_uhrposition(value: Any, reversed_direction: bool) -> int:
        """Ordnet die QKan-Uhrposition links oder rechts in Inspektionsrichtung zu."""
        try:
            clock = int(float(str(value).replace(",", ".")))
        except (TypeError, ValueError):
            clock = 3
        factor = -1 if clock in (7, 8, 9, 10, 11) else 1
        return -factor if reversed_direction else factor

    def _anschlussinformationen_laden(
        self,
        object_name: str,
        date_value: str,
        all_dates: bool,
        overall: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Lädt verbundene Anschlussleitungen mit Station und tatsächlicher
        Inspektionsseite.
        """
        if self.cb_objektart.currentText() != "Haltung" or all_dates or not date_value:
            return []
        overall_data = self._gesamtobjekt_daten_laden(
            "Haltung", object_name, date_value, base_fallback=True
        )
        if overall_data is None:
            return []
        holding_geometry = overall_data.get("geometry")
        if holding_geometry is None or holding_geometry.isEmpty():
            return []
        direction = _text_sicher_lesen(
            (overall or {}).get("untersuchrichtung")
            or overall_data.get("attributes", {}).get("untersuchrichtung")
        ).strip()
        reversed_direction = direction == "gegen Fließrichtung"
        total_length = holding_geometry.length()
        if total_length <= 0.000001:
            return []

        layer = QgsVectorLayer(
            f"{self.qkan_database}|layername=anschlussleitungen",
            "anschlussleitungen",
            "ogr",
        )
        if not layer.isValid() or "haltnam" not in layer.fields().names():
            return []

        result: list[dict[str, Any]] = []
        for feature in layer.getFeatures():
            if self._wert_fuer_vergleich(feature["haltnam"]) != object_name:
                continue
            geom_station: Optional[float] = None
            side: Optional[int] = None
            geometry = feature.geometry() if feature.hasGeometry() else None
            endpoints = self._linien_endpunkte(geometry)
            if endpoints is not None:
                endpoint_data: list[tuple[float, QgsPointXY, QgsPointXY, QgsPointXY]] = []
                for connection_point, other_point in (
                    (endpoints[0], endpoints[1]),
                    (endpoints[1], endpoints[0]),
                ):
                    point_geometry = QgsGeometry.fromPointXY(connection_point)
                    nearest = holding_geometry.nearestPoint(point_geometry)
                    distance = holding_geometry.distance(point_geometry)
                    if nearest is not None and not nearest.isEmpty():
                        endpoint_data.append(
                            (float(distance), connection_point, other_point, QgsPointXY(nearest.asPoint()))
                        )
                if endpoint_data:
                    _distance, _connection_point, outer_point, nearest_point = min(
                        endpoint_data, key=lambda item: item[0]
                    )
                    geom_station_value = holding_geometry.lineLocatePoint(
                        QgsGeometry.fromPointXY(nearest_point)
                    )
                    if geom_station_value is not None and geom_station_value >= 0:
                        geom_station = float(geom_station_value)
                        basis = self._lokale_normalenbasis(holding_geometry, geom_station)
                        if basis is not None:
                            station_point, nx, ny = basis
                            dot = (
                                (outer_point.x() - station_point.x()) * nx
                                + (outer_point.y() - station_point.y()) * ny
                            )
                            if abs(dot) > 0.000001:
                                side = 1 if dot > 0 else -1
                                if reversed_direction:
                                    side *= -1

            field_names = feature.fields().names()
            if geom_station is None and "urstation" in field_names:
                urstation = _gleitkommazahl_sicher_lesen(feature["urstation"], -1.0)
                if urstation >= 0:
                    geom_station = max(0.0, min(total_length, total_length - urstation))
            if side is None:
                side = self._seitenfaktor_aus_uhrposition(
                    feature["lageanschluss"] if "lageanschluss" in field_names else None,
                    reversed_direction,
                )
            if geom_station is None:
                continue
            station = total_length - geom_station if reversed_direction else geom_station
            result.append(
                {
                    "station": max(0.0, min(total_length, float(station))),
                    "seite": -1 if side < 0 else 1,
                    "leitnam": _text_sicher_lesen(feature["leitnam"]) if "leitnam" in field_names else "",
                }
            )
        result.sort(key=lambda item: (item["station"], item["seite"], item["leitnam"]))
        return result

    @staticmethod
    def _bewertungswert_lesen(value: Any) -> Optional[int]:
        """Liest einen ganzzahligen Bewertungswert; Null ist ausdrücklich gültig."""
        if value is None or _text_sicher_lesen(value).strip() == "":
            return None
        try:
            return int(float(_text_sicher_lesen(value).replace(",", ".")))
        except (TypeError, ValueError):
            return None

    def _gesamtbewertung_aus_schaeden(self) -> dict[str, Optional[int]]:
        """Berechnet die Minima für ZD/ZB/ZS und schließt dabei nur den Kode K aus."""
        result: dict[str, Optional[int]] = {}
        relevant_rows = [
            row
            for row in self.damage_rows
            if _text_sicher_lesen(row.get("kuerzel")).strip().upper() != "K"
        ]
        for field in ("ZD", "ZB", "ZS"):
            values = [
                value
                for value in (self._bewertungswert_lesen(row.get(field)) for row in relevant_rows)
                if value is not None
            ]
            result[field] = min(values) if values else None
        return result

    def _bewertung_neu_berechnen(self, _checked: bool = False, show_message: bool = True) -> bool:
        """Berechnet die vorgemerkte Gesamtbewertung neu, ohne in die Datenbank zu
        schreiben.
        """
        if self.current_all_dates or not self.current_date_value:
            if show_message:
                QMessageBox.information(
                    self,
                    "Neu bewerten",
                    "Bitte eine konkrete Befahrung auswählen. Die Gesamtbewertung gilt immer pro Datum.",
                )
            return False
        self._tabelle_in_schadensdaten_uebernehmen()
        rating = self._gesamtbewertung_aus_schaeden()
        self.rating_zd_label.setText(f"ZD: {rating['ZD'] if rating['ZD'] is not None else '–'}")
        self.rating_zb_label.setText(f"ZB: {rating['ZB'] if rating['ZB'] is not None else '–'}")
        self.rating_zs_label.setText(f"ZS: {rating['ZS'] if rating['ZS'] is not None else '–'}")
        self._rating_dirty = True
        self.lbl_status.setText(
            "Gesamtbewertung neu berechnet; Übernahme erst mit „Speichern“."
        )
        return True

    def _schadenstabelle_fuellen(self) -> None:
        """Füllt die bearbeitbare Schadenstabelle, ohne in die Datenbank zu schreiben."""
        self._filling_damage_table = True
        self.tw_schaeden.blockSignals(True)
        try:
            self.tw_schaeden.setRowCount(len(self.damage_rows))
            for row_index, row in enumerate(self.damage_rows):
                position = row.get("station")
                if self.cb_objektart.currentText() == "Schacht":
                    position = row.get("vertikale_lage") or position
                values = [
                    _text_sicher_lesen(row.get("untersuchtag")),
                    f"{_gleitkommazahl_sicher_lesen(position, 0.0):.2f}",
                    _text_sicher_lesen(row.get("id")),
                    _text_sicher_lesen(row.get("kuerzel")),
                    _text_sicher_lesen(row.get("langtext")),
                    _text_sicher_lesen(row.get("ZD")),
                    _text_sicher_lesen(row.get("ZB")),
                    _text_sicher_lesen(row.get("ZS")),
                    "ja" if _text_sicher_lesen(row.get("foto_dateiname")).strip() else "",
                    "ja" if _text_sicher_lesen(row.get("film_dateiname")).strip() else "",
                    _text_sicher_lesen(row.get("timecode")),
                ]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if column in (1, 2, 5, 6, 7):
                        item.setTextAlignment(Qt.AlignCenter)
                    if column in (8, 9):
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.tw_schaeden.setItem(row_index, column, item)
        finally:
            self.tw_schaeden.blockSignals(False)
            self._filling_damage_table = False

    def _schadenseintrag_geaendert(self, item: QTableWidgetItem) -> None:
        """Markiert vorgemerkte Änderungen und berechnet bei relevanten Werten die
        Bewertung neu.
        """
        if self._filling_damage_table:
            return
        self._table_dirty = True
        if item.column() in (3, 5, 6, 7):
            self._bewertung_neu_berechnen(show_message=False)

    def _stationsspalte_bestimmen(self) -> str:
        """Liefert das bearbeitbare Positionsfeld der aktuellen Objektart."""
        return "vertikale_lage" if self.cb_objektart.currentText() == "Schacht" else "station"

    def _tabelle_in_schadensdaten_uebernehmen(self) -> None:
        """Übernimmt sichtbare bearbeitbare Werte nur in die Daten im Arbeitsspeicher."""
        position_column = self._stationsspalte_bestimmen()
        mappings = {
            0: "untersuchtag",
            1: position_column,
            2: "id",
            3: "kuerzel",
            4: "langtext",
            5: "ZD",
            6: "ZB",
            7: "ZS",
            10: "timecode",
        }
        for row_index, row in enumerate(self.damage_rows):
            if row_index >= self.tw_schaeden.rowCount():
                break
            for column, field in mappings.items():
                item = self.tw_schaeden.item(row_index, column)
                text = item.text().strip() if item is not None else ""
                if field == position_column:
                    row[field] = _gleitkommazahl_sicher_lesen(text, 0.0)
                else:
                    row[field] = text or None

    def _verfuegbare_schadenscodes_laden(self) -> list[str]:
        """Lädt vorhandene QKan-Schadenskodes, ohne daraus Langtexte abzuleiten."""
        if not self.qkan_database or not Path(self.qkan_database).is_file():
            return []
        connection = _sqlite_verbindung(self.qkan_database, query_only=True)
        try:
            existing = _tabellennamen_lesen(connection)
            codes: set[str] = set()
            for table_name in (
                "reflist_zustand",
                "untersuchdat_haltung",
                "untersuchdat_anschlussleitung",
                "untersuchdat_schacht",
            ):
                if table_name not in existing:
                    continue
                columns = _tabellenspalten_lesen(connection, table_name)
                code_column = "hauptcode" if "hauptcode" in columns else "kuerzel" if "kuerzel" in columns else ""
                if not code_column:
                    continue
                rows = connection.execute(
                    f"SELECT DISTINCT {_sql_bezeichner_quotieren(code_column)} "
                    f"FROM {_sql_bezeichner_quotieren(table_name)} "
                    f"WHERE TRIM(COALESCE({_sql_bezeichner_quotieren(code_column)}, '')) <> ''"
                ).fetchall()
                codes.update(_text_sicher_lesen(row[0]).strip().upper() for row in rows if _text_sicher_lesen(row[0]).strip())
            return sorted(codes)
        finally:
            connection.close()

    def _schadenseintrag_hinzufuegen(self) -> None:
        """Öffnet die Eingabemaske und fügt den Eintrag erst nach »Übernehmen« hinzu."""
        self._tabelle_in_schadensdaten_uebernehmen()
        dialog = QDialog(self)
        ui_path = Path(__file__).parent / "res" / "einzelschaden_dialog.ui"
        if not ui_path.is_file():
            QMessageBox.critical(self, "Eintrag hinzufügen", f"Eingabemaske nicht gefunden:\n{ui_path}")
            return
        uic.loadUi(str(ui_path), dialog)
        dialog.setWindowTitle("Einzelschaden hinzufügen")

        dialog.position_label.setText(
            "Vertikale Lage [m]" if self.cb_objektart.currentText() == "Schacht" else "Station [m]"
        )
        dialog.cb_kuerzel.clear()
        dialog.cb_kuerzel.addItem("")
        dialog.cb_kuerzel.addItems(self._verfuegbare_schadenscodes_laden())
        dialog.cb_kuerzel.setCurrentIndex(0)
        for combo in (dialog.cb_zd, dialog.cb_zb, dialog.cb_zs):
            combo.clear()
            combo.addItems(["", "0", "1", "2", "3", "4", "5"])
        dialog.dsb_station.setMaximum(max(self.current_object_length, 0.0))
        if self.current_overall is not None:
            dialog.le_id.setText(_text_sicher_lesen(self.current_overall.get("id")))
        dialog.bb_dialog.button(QDialogButtonBox.Ok).setText("Übernehmen")

        if dialog.exec_() != QDialog.Accepted:
            return

        date_value = ""
        selection = self.cb_befahrung.currentText()
        if selection not in ("Aktuellste Befahrung", "Alle Befahrungen"):
            date_value = selection
        elif self.damage_rows:
            date_value = _text_sicher_lesen(self.damage_rows[0].get("untersuchtag"))
        elif self.cb_befahrung.count() > 2:
            date_value = self.cb_befahrung.itemText(2)

        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        position_column = self._stationsspalte_bestimmen()
        overall_values = self.current_overall or {}
        new_row: dict[str, Any] = {
            "source_rowid": None,
            config["object_column"]: self.cb_objekt.currentText().strip(),
            "untersuchtag": date_value or datetime.now().strftime("%Y-%m-%d"),
            position_column: dialog.dsb_station.value(),
            "id": dialog.le_id.text().strip() or overall_values.get("id"),
            "schoben": overall_values.get("schoben"),
            "schunten": overall_values.get("schunten"),
            "untersuchrichtung": overall_values.get("untersuchrichtung"),
            "inspektionslaenge": self.current_object_length,
            "kuerzel": dialog.cb_kuerzel.currentText().strip().upper() or None,
            "langtext": dialog.pte_langtext.toPlainText().strip() or None,
            "ZD": dialog.cb_zd.currentText().strip() or None,
            "ZB": dialog.cb_zb.currentText().strip() or None,
            "ZS": dialog.cb_zs.currentText().strip() or None,
            "foto_dateiname": None,
            "film_dateiname": None,
            "timecode": dialog.le_timecode.text().strip() or None,
            "_new": True,
        }
        self.damage_rows.append(new_row)
        self._table_dirty = True
        self._schadenstabelle_fuellen()
        row_index = len(self.damage_rows) - 1
        self.tw_schaeden.selectRow(row_index)
        self.tw_schaeden.scrollToItem(self.tw_schaeden.item(row_index, 0))
        self._bewertung_neu_berechnen(show_message=False)
        self._schadensvorschau_aktualisieren()

    def _schadenseintrag_loeschen(self) -> None:
        """Entfernt die ausgewählte Zeile zunächst nur im Arbeitsspeicher; gelöscht
        wird erst beim Speichern.
        """
        row_index = self.tw_schaeden.currentRow()
        if not 0 <= row_index < len(self.damage_rows):
            QMessageBox.information(self, "Eintrag löschen", "Bitte zuerst einen Eintrag auswählen.")
            return
        self._tabelle_in_schadensdaten_uebernehmen()
        row = self.damage_rows.pop(row_index)
        source_rowid = row.get("source_rowid")
        if source_rowid not in (None, ""):
            self._deleted_damage_rowids.add(int(source_rowid))
        self._table_dirty = True
        self._schadenstabelle_fuellen()
        if self.damage_rows:
            self.tw_schaeden.selectRow(min(row_index, len(self.damage_rows) - 1))
        self._bewertung_neu_berechnen(show_message=False)
        self._schadensvorschau_aktualisieren()

    def _schadensvorschau_aktualisieren(self) -> None:
        """Aktualisiert Schema und Medienvorschau aus den vorgemerkten Daten im
        Arbeitsspeicher.
        """
        self.current_object_length = self._objektlaenge_bestimmen(None)
        self.inspektionsgrafik.daten_setzen(
            self.damage_rows,
            self.cb_objektart.currentText(),
            self.current_object_length,
            self.current_connections,
        )
        self._medienlisten_erstellen()

    def _schadensgeometrien_berechnen(self) -> dict[int, QgsGeometry]:
        """Berechnet die Schadensbeschriftungsgeometrien nach den M150-/STRAKAT-Regeln."""
        object_type = self.cb_objektart.currentText()
        object_name = self.cb_objekt.currentText().strip()
        groups: dict[str, list[tuple[int, dict[str, Any]]]] = {}
        for index, row in enumerate(self.damage_rows):
            date_value = _text_sicher_lesen(row.get("untersuchtag")).strip()
            groups.setdefault(date_value, []).append((index, row))

        result: dict[int, QgsGeometry] = {}
        for date_value, entries in groups.items():
            overall_data = self._gesamtobjekt_daten_laden(
                object_type, object_name, date_value, base_fallback=True
            )
            if overall_data is None:
                raise RuntimeError(
                    f"Für {object_type} {object_name} am {date_value or 'unbekannten Datum'} "
                    "wurde keine Objektgeometrie gefunden."
                )
            geometry = overall_data.get("geometry")
            if geometry is None or geometry.isEmpty():
                raise RuntimeError(
                    f"Für {object_type} {object_name} am {date_value or 'unbekannten Datum'} "
                    "ist keine gültige Objektgeometrie vorhanden."
                )
            attributes = overall_data.get("attributes", {})
            if object_type == "Schacht":
                result.update(self._schadensgeometrien_schacht(entries, geometry))
            else:
                direction = _text_sicher_lesen(attributes.get("untersuchrichtung")).strip()
                if not direction and entries:
                    direction = _text_sicher_lesen(entries[0][1].get("untersuchrichtung")).strip()
                if object_type == "Anschlussleitung":
                    result.update(
                        self._schadensgeometrien_anschlussleitung(entries, geometry, direction)
                    )
                else:
                    result.update(self._schadensgeometrien_haltung(entries, geometry, direction))
        return result

    @staticmethod
    def _beschriftungsstationen_berechnen(
        stations: list[float], total_length: float, connection_offset: float = 0.0,
        prefer_end_first: bool = False,
    ) -> list[float]:
        """Entzerrt dichte Positionen wie die M150-/STRAKAT-Importlogik."""
        if not stations:
            return []
        text_distance = 0.35
        block_distance = 0.45 - text_distance
        count = len(stations)
        forward_positions = [0.0] * count
        backward_positions = [0.0] * count
        forward_possible = [False] * count
        backward_possible = [False] * count
        output = [0.0] * count

        previous_position = stations[0] if connection_offset else 0.0
        forward_ok = True
        previous_station: Optional[float] = None
        for index, station in enumerate(stations):
            if index == 0:
                distance = 0.0
                if connection_offset:
                    previous_position = station
            else:
                distance = (
                    (text_distance + block_distance)
                    if abs(station - (previous_station if previous_station is not None else station)) > 0.0001
                    else text_distance
                )
            forward_ok = bool(forward_ok and previous_position + distance > station - 0.0001)
            forward_possible[index] = forward_ok
            previous_position = max(station, previous_position + distance)
            forward_positions[index] = previous_position
            previous_station = station

        previous_position = total_length - (text_distance + block_distance) - connection_offset
        backward_ok = True
        previous_station = None
        for index in range(count - 1, -1, -1):
            station = stations[index]
            distance = 0.0 if index == count - 1 else (
                (text_distance + block_distance)
                if abs(station - (previous_station if previous_station is not None else station)) > 0.0001
                else text_distance
            )
            backward_ok = bool(backward_ok and previous_position - distance < station + 0.0001)
            backward_possible[index] = backward_ok
            previous_position = min(station, previous_position - distance)
            backward_positions[index] = previous_position
            previous_station = station

        for index in range(count):
            if prefer_end_first:
                if backward_possible[index]:
                    output[index] = backward_positions[index]
                elif forward_possible[index]:
                    output[index] = forward_positions[index]
                else:
                    output[index] = (forward_positions[index] + backward_positions[index]) / 2.0
            else:
                if forward_possible[index]:
                    output[index] = forward_positions[index]
                elif backward_possible[index]:
                    output[index] = backward_positions[index]
                else:
                    output[index] = (forward_positions[index] + backward_positions[index]) / 2.0
        return output

    def _schadensgeometrien_haltung(
        self,
        entries: list[tuple[int, dict[str, Any]]],
        geometry: QgsGeometry,
        direction: str,
    ) -> dict[int, QgsGeometry]:
        endpoints = self._linien_endpunkte(geometry)
        if endpoints is None:
            raise RuntimeError("Die Geometrie der untersuchten Haltung ist keine gültige Linie.")
        start, end = endpoints
        geometry_length = geometry.length()
        prepared: list[tuple[int, dict[str, Any], float]] = []
        for original_index, row in entries:
            station = _gleitkommazahl_sicher_lesen(row.get("station"), 0.0)
            if direction == "gegen Fließrichtung":
                station = geometry_length - station
            prepared.append((original_index, row, station))
        prepared.sort(key=lambda item: (item[2], item[0]))

        chord_length = math.hypot(end.x() - start.x(), end.y() - start.y())
        if chord_length <= 0.045:
            raise RuntimeError("Die Geometrie der untersuchten Haltung ist zu kurz.")
        stations = [item[2] for item in prepared]
        label_stations = self._beschriftungsstationen_berechnen(stations, chord_length)
        ux = (end.x() - start.x()) / chord_length
        uy = (end.y() - start.y()) / chord_length
        vx, vy = uy, -ux
        offsets = (0.0, 1.0, 1.5, 4.0)
        result: dict[int, QgsGeometry] = {}
        for (original_index, _row, station), label_station in zip(prepared, label_stations):
            result[original_index] = QgsGeometry.fromPolyline(
                [
                    QgsPoint(start.x() + ux * station + vx * offsets[0], start.y() + uy * station + vy * offsets[0]),
                    QgsPoint(start.x() + ux * station + vx * offsets[1], start.y() + uy * station + vy * offsets[1]),
                    QgsPoint(start.x() + ux * label_station + vx * offsets[2], start.y() + uy * label_station + vy * offsets[2]),
                    QgsPoint(start.x() + ux * label_station + vx * offsets[3], start.y() + uy * label_station + vy * offsets[3]),
                ]
            )
        return result

    def _schadensgeometrien_anschlussleitung(
        self,
        entries: list[tuple[int, dict[str, Any]]],
        geometry: QgsGeometry,
        direction: str,
    ) -> dict[int, QgsGeometry]:
        endpoints = self._linien_endpunkte(geometry)
        if endpoints is None:
            raise RuntimeError("Die Geometrie der untersuchten Anschlussleitung ist keine gültige Linie.")
        start, end = endpoints
        geometry_length = geometry.length()
        prepared: list[tuple[int, dict[str, Any], float]] = []
        for original_index, row in entries:
            station = _gleitkommazahl_sicher_lesen(row.get("station"), 0.0)
            if direction == "gegen Fließrichtung":
                station = geometry_length - station
            prepared.append((original_index, row, station))
        prepared.sort(key=lambda item: (item[2], item[0]))

        chord_length = math.hypot(end.x() - start.x(), end.y() - start.y())
        if chord_length <= 0.000001:
            raise RuntimeError("Die Geometrie der untersuchten Anschlussleitung ist zu kurz.")
        stations = [item[2] for item in prepared]
        label_stations = self._beschriftungsstationen_berechnen(
            stations, geometry_length, connection_offset=1.0, prefer_end_first=True
        )
        ux = (end.x() - start.x()) / chord_length
        uy = (end.y() - start.y()) / chord_length
        vx, vy = uy, -ux
        offsets = (0.0, 1.0, 1.5, 4.0)
        result: dict[int, QgsGeometry] = {}
        for (original_index, _row, station), label_station in zip(prepared, label_stations):
            interpolated = geometry.interpolate(max(0.0, min(geometry_length, station)))
            if interpolated is not None and not interpolated.isEmpty():
                first_point = QgsPoint(interpolated.asPoint())
            else:
                first_point = QgsPoint(start.x() + ux * station, start.y() + uy * station)
            result[original_index] = QgsGeometry.fromPolyline(
                [
                    first_point,
                    QgsPoint(start.x() + ux * station + vx * offsets[1], start.y() + uy * station + vy * offsets[1]),
                    QgsPoint(start.x() + ux * label_station + vx * offsets[2], start.y() + uy * label_station + vy * offsets[2]),
                    QgsPoint(start.x() + ux * label_station + vx * offsets[3], start.y() + uy * label_station + vy * offsets[3]),
                ]
            )
        return result

    def _schadensgeometrien_schacht(
        self,
        entries: list[tuple[int, dict[str, Any]]],
        geometry: QgsGeometry,
    ) -> dict[int, QgsGeometry]:
        if geometry.isMultipart():
            points = geometry.asMultiPoint()
            point = QgsPointXY(points[0]) if points else None
        else:
            try:
                point = QgsPointXY(geometry.asPoint())
            except (TypeError, ValueError):
                point = None
        if point is None:
            raise RuntimeError("Die Geometrie des untersuchten Schachts ist kein gültiger Punkt.")
        offsets = (0.0, 5.0, 5.5, 8.0)
        result: dict[int, QgsGeometry] = {}
        for position, (original_index, _row) in enumerate(entries):
            label_station = position * 0.35
            result[original_index] = QgsGeometry.fromPolyline(
                [
                    QgsPoint(point.x() + offsets[0], point.y()),
                    QgsPoint(point.x() + offsets[1], point.y()),
                    QgsPoint(point.x() + offsets[2], point.y() - label_station),
                    QgsPoint(point.x() + offsets[3], point.y() - label_station),
                ]
            )
        return result

    def _gesamtbewertung_speichern(self, bewertung_speichern: bool) -> None:
        """Speichert vorgemerkte Gesamtwerte und kennzeichnet den Gesamtdatensatz als
        bearbeitet.
        """
        if self.current_all_dates or not self.current_date_value:
            raise RuntimeError("Für „Alle Befahrungen“ kann keine einzelne Gesamtbewertung gespeichert werden.")
        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        layer = QgsVectorLayer(
            f"{self.qkan_database}|layername={config['overall_table']}",
            config["overall_table"],
            "ogr",
        )
        if not layer.isValid():
            raise RuntimeError(
                f"Die Tabelle {config['overall_table']} konnte nicht geöffnet werden."
            )
        target: Optional[QgsFeature] = None
        object_name = self.cb_objekt.currentText().strip()
        for feature in layer.getFeatures():
            if self._wert_fuer_vergleich(feature[config["overall_object_column"]]) != object_name:
                continue
            if self._wert_fuer_vergleich(feature["untersuchtag"]) != self.current_date_value:
                continue
            if target is None or int(feature.id()) > int(target.id()):
                target = feature
        if target is None:
            raise RuntimeError(
                f"Für {object_name} am {self.current_date_value} wurde kein Eintrag in "
                f"{config['overall_table']} gefunden."
            )
        if not layer.startEditing():
            raise RuntimeError("Die Gesamtbewertung konnte nicht zur Bearbeitung geöffnet werden.")
        try:
            if bewertung_speichern:
                rating = self._gesamtbewertung_aus_schaeden()
                for field, key in (("max_ZD", "ZD"), ("max_ZB", "ZB"), ("max_ZS", "ZS")):
                    field_index = layer.fields().indexFromName(field)
                    if field_index < 0:
                        raise RuntimeError(f"Das Feld {field} fehlt in {config['overall_table']}.")
                    if not layer.changeAttributeValue(target.id(), field_index, rating[key]):
                        raise RuntimeError(f"Das Feld {field} konnte nicht aktualisiert werden.")

            # Das QKan-Datenbankfeld heißt "createdat"; "bearbeitet" ist nur
            # der in QGIS angezeigte Alias und darf nicht für den Feldzugriff
            # verwendet werden.
            bearbeitet_index = layer.fields().indexFromName("createdat")
            if bearbeitet_index < 0:
                raise RuntimeError(
                    f"Das Feld createdat (Alias: bearbeitet) fehlt in {config['overall_table']}."
                )
            bearbeitet = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            if not layer.changeAttributeValue(target.id(), bearbeitet_index, bearbeitet):
                raise RuntimeError(
                    "Das Feld createdat (Alias: bearbeitet) konnte nicht aktualisiert werden."
                )

            if not layer.commitChanges():
                raise RuntimeError("; ".join(layer.commitErrors()) or "Unbekannter Providerfehler")
        except Exception:
            if layer.isEditable():
                layer.rollBack()
            raise

    def _schadensaenderungen_speichern(self) -> None:
        """Speichert vorgemerkte Änderungen an Schäden, Geometrien und Gesamtbewertung."""
        if not self._table_dirty and not self._deleted_damage_rowids and not self._rating_dirty:
            QMessageBox.information(self, "Speichern", "Es gibt keine ungespeicherten Änderungen.")
            return
        if not self.qkan_database or not Path(self.qkan_database).is_file():
            QMessageBox.warning(self, "Speichern", "Die QKan-Datenbank ist nicht verfügbar.")
            return

        self._tabelle_in_schadensdaten_uebernehmen()
        details_changed = self._table_dirty or bool(self._deleted_damage_rowids)
        details_saved = False

        if details_changed:
            config = OBJECT_CONFIG[self.cb_objektart.currentText()]
            table_name = config["detail_table"]
            object_column = config["object_column"]
            try:
                geometries = self._schadensgeometrien_berechnen()
            except Exception as error:
                _loggen(f"Schadensgeometrien konnten nicht berechnet werden: {error}", Qgis.Critical)
                QMessageBox.critical(
                    self,
                    "Speichern fehlgeschlagen",
                    "Die Änderungen wurden nicht gespeichert, weil die Schadensgeometrien "
                    f"nicht erzeugt werden konnten.\n\n{error}",
                )
                return

            layer = QgsVectorLayer(
                f"{self.qkan_database}|layername={table_name}",
                table_name,
                "ogr",
            )
            if not layer.isValid():
                QMessageBox.critical(
                    self,
                    "Speichern fehlgeschlagen",
                    f"Die QKan-Tabelle {table_name} konnte nicht über den QGIS-Provider geöffnet werden.",
                )
                return
            if not layer.startEditing():
                QMessageBox.critical(
                    self,
                    "Speichern fehlgeschlagen",
                    "Für die QKan-Tabelle konnte keine Bearbeitungssitzung gestartet werden.",
                )
                return

            fields = layer.fields()
            editable_fields = [
                "untersuchtag",
                self._stationsspalte_bestimmen(),
                "id",
                "kuerzel",
                "langtext",
                "ZD",
                "ZB",
                "ZS",
                "timecode",
            ]
            editable_fields = [field for field in editable_fields if fields.indexFromName(field) >= 0]
            insert_fields = [
                object_column,
                "untersuchtag",
                self._stationsspalte_bestimmen(),
                "id",
                "schoben",
                "schunten",
                "untersuchrichtung",
                "inspektionslaenge",
                "kuerzel",
                "langtext",
                "ZD",
                "ZB",
                "ZS",
                "timecode",
                "foto_dateiname",
                "film_dateiname",
            ]
            insert_fields = [field for field in insert_fields if fields.indexFromName(field) >= 0]

            try:
                for source_rowid in sorted(self._deleted_damage_rowids):
                    if not layer.deleteFeature(int(source_rowid)):
                        raise RuntimeError(f"Eintrag {source_rowid} konnte nicht gelöscht werden.")

                for row_index, row in enumerate(self.damage_rows):
                    source_rowid = row.get("source_rowid")
                    geometry = geometries.get(row_index)
                    if layer.isSpatial() and (geometry is None or geometry.isEmpty()):
                        raise RuntimeError(
                            f"Für den Einzelschaden in Zeile {row_index + 1} konnte keine Geometrie erzeugt werden."
                        )
                    if source_rowid in (None, ""):
                        feature = QgsFeature(fields)
                        if layer.isSpatial() and geometry is not None:
                            feature.setGeometry(geometry)
                        for field in insert_fields:
                            value = (
                                self.cb_objekt.currentText().strip()
                                if field == object_column
                                else row.get(field)
                            )
                            feature.setAttribute(fields.indexFromName(field), value)
                        if not layer.addFeature(feature):
                            raise RuntimeError("Ein neuer Eintrag konnte nicht angelegt werden.")
                    else:
                        feature_id = int(source_rowid)
                        for field in editable_fields:
                            field_index = fields.indexFromName(field)
                            if not layer.changeAttributeValue(feature_id, field_index, row.get(field)):
                                raise RuntimeError(
                                    f"Eintrag {source_rowid}, Feld {field}, konnte nicht geändert werden."
                                )
                        if layer.isSpatial() and geometry is not None:
                            if not layer.changeGeometry(feature_id, geometry):
                                raise RuntimeError(
                                    f"Die Geometrie von Eintrag {source_rowid} konnte nicht aktualisiert werden."
                                )

                if not layer.commitChanges():
                    raise RuntimeError("; ".join(layer.commitErrors()) or "Unbekannter Providerfehler")
                details_saved = True
            except Exception as error:
                if layer.isEditable():
                    layer.rollBack()
                _loggen(f"Schadensänderungen konnten nicht gespeichert werden: {error}", Qgis.Critical)
                QMessageBox.critical(
                    self,
                    "Speichern fehlgeschlagen",
                    f"Die Änderungen wurden nicht gespeichert.\n\n{error}",
                )
                return

        if details_changed or self._rating_dirty:
            try:
                self._gesamtbewertung_speichern(
                    bewertung_speichern=self._rating_dirty
                )
            except Exception as error:
                _loggen(
                    f"Gesamtbewertung oder Bearbeitungszeitpunkt konnte nicht gespeichert werden: {error}",
                    Qgis.Critical,
                )
                if details_saved:
                    self._table_dirty = False
                    self._deleted_damage_rowids.clear()
                    prefix = (
                        "Die Einzelschäden wurden gespeichert, die Gesamtbewertung "
                        "beziehungsweise der Bearbeitungszeitpunkt jedoch nicht."
                    )
                else:
                    prefix = (
                        "Die Gesamtbewertung beziehungsweise der Bearbeitungszeitpunkt "
                        "wurde nicht gespeichert."
                    )
                QMessageBox.critical(
                    self,
                    "Speichern teilweise fehlgeschlagen",
                    f"{prefix}\n\n{error}",
                )
                return

        self._table_dirty = False
        self._rating_dirty = False
        self._deleted_damage_rowids.clear()
        QMessageBox.information(
            self,
            "Gespeichert",
            "Die Änderungen wurden in der QKan-Datenbank gespeichert.",
        )
        self._ansicht_laden()

    def _grafik_exportieren(self) -> None:
        """Exportiert die ausgewählte Inspektion als grafisches A4-PDF in den
        Download-Ordner.
        """
        if not self.damage_rows:
            QMessageBox.information(self, "Grafik exportieren", "Für die aktuelle Auswahl sind keine Befahrungsdaten vorhanden.")
            return
        self._tabelle_in_schadensdaten_uebernehmen()
        downloads = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        target_directory = Path(downloads) if downloads else Path.home() / "Downloads"
        target_directory.mkdir(parents=True, exist_ok=True)
        object_type = self.cb_objektart.currentText()
        object_name = self.cb_objekt.currentText().strip() or "Objekt"
        date_value = self.cb_befahrung.currentText()
        if date_value == "Aktuellste Befahrung" and self.damage_rows:
            date_value = _text_sicher_lesen(self.damage_rows[0].get("untersuchtag"))
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", f"Befahrungsgrafik_{object_type}_{object_name}_{date_value}").strip("_")
        target = target_directory / f"{safe_name}.pdf"
        counter = 2
        while target.exists():
            target = target_directory / f"{safe_name}_{counter}.pdf"
            counter += 1

        try:
            self._grafik_pdf_schreiben(target, object_type, object_name, date_value)
        except Exception as error:
            _loggen(f"PDF-Export fehlgeschlagen: {error}", Qgis.Critical)
            QMessageBox.critical(self, "Grafik exportieren", f"Das PDF konnte nicht erzeugt werden.\n\n{error}")
            return

        answer = QMessageBox.question(
            self,
            "Grafik exportiert",
            f"Das PDF wurde gespeichert:\n{target}\n\nJetzt öffnen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _grafik_pdf_schreiben(self, target: Path, object_type: str, object_name: str, date_value: str) -> None:
        """Zeichnet eine lesbare Stationsgrafik mit lokal entzerrten dichten Bereichen."""
        position_column = self._stationsspalte_bestimmen()
        length = max(self.current_object_length, 1.0)

        # Die ursprüngliche Stationsreihenfolge beibehalten. Positionen bleiben proportional,
        # solange genügend Platz vorhanden ist; dichte Gruppen werden nur um den minimalen
        # Beschriftungsabstand auseinandergezogen. Das behandelt auch mehrere Schäden an derselben Station.
        ordered_rows = sorted(
            enumerate(self.damage_rows),
            key=lambda item: (
                max(0.0, min(length, _gleitkommazahl_sicher_lesen(item[1].get(position_column), 0.0))),
                item[0],
            ),
        )
        min_gap_px = 118
        base_line_height_px = 2450
        display_positions: list[tuple[dict[str, Any], float, int]] = []
        previous_y: Optional[int] = None
        for _original_index, row in ordered_rows:
            station = max(0.0, min(length, _gleitkommazahl_sicher_lesen(row.get(position_column), 0.0)))
            proportional_y = int(round(base_line_height_px * station / length))
            display_y = proportional_y if previous_y is None else max(proportional_y, previous_y + min_gap_px)
            display_positions.append((row, station, display_y))
            previous_y = display_y

        required_line_height_px = max(
            base_line_height_px,
            (display_positions[-1][2] if display_positions else base_line_height_px),
        )

        # Beliebige Stationen, beispielsweise angeschlossene Leitungen, auf dieselbe
        # lokal entzerrte Skala wie die Schadensmarkierungen abbilden. Doppelte Stationen verwenden
        # die Mitte ihrer dargestellten Gruppe.
        station_groups: dict[float, list[int]] = {}
        for _row, station, display_y in display_positions:
            station_groups.setdefault(round(station, 6), []).append(display_y)
        station_anchors: list[tuple[float, float]] = [(0.0, 0.0)]
        station_anchors.extend(
            (station, sum(values) / len(values))
            for station, values in sorted(station_groups.items())
        )
        station_anchors.append((length, float(required_line_height_px)))
        normalized_anchors: list[tuple[float, float]] = []
        for station, display_y in station_anchors:
            if normalized_anchors and abs(station - normalized_anchors[-1][0]) <= 0.000001:
                normalized_anchors[-1] = (
                    station,
                    max(normalized_anchors[-1][1], display_y),
                )
            else:
                normalized_anchors.append((station, display_y))

        def anzeige_y_fuer_station(station: float) -> float:
            station = max(0.0, min(length, station))
            for anchor_index in range(1, len(normalized_anchors)):
                station_a, y_a = normalized_anchors[anchor_index - 1]
                station_b, y_b = normalized_anchors[anchor_index]
                if station <= station_b or anchor_index == len(normalized_anchors) - 1:
                    if abs(station_b - station_a) <= 0.000001:
                        return y_b
                    ratio = (station - station_a) / (station_b - station_a)
                    return y_a + ratio * (y_b - y_a)
            return float(required_line_height_px)

        # Bei Bedarf eine höhere PDF-Seite verwenden, statt Beschriftungen zusammenzudrücken.
        # 300 dpi entsprechen etwa 11,81 Pixeln pro Millimeter.
        px_per_mm = 300.0 / 25.4
        header_px = 600
        footer_px = 190
        top_bottom_margin_px = 260
        required_height_px = header_px + required_line_height_px + footer_px + 2 * top_bottom_margin_px
        page_height_mm = max(297.0, required_height_px / px_per_mm)

        writer = QPdfWriter(str(target))
        writer.setPageSize(QPageSize(QSizeF(210.0, page_height_mm), QPageSize.Millimeter, "Befahrungsgrafik"))
        writer.setResolution(300)
        writer.setTitle(f"Befahrungsgrafik {object_type} {object_name}")
        writer.setCreator("EV-A-Kan TV Media")
        painter = QPainter(writer)
        if not painter.isActive():
            raise RuntimeError("PDF-Zeichner konnte nicht gestartet werden.")

        page_width = writer.width()
        page_height = writer.height()
        margin = int(page_width * 0.045)
        header_height = header_px
        footer_height = footer_px
        top = margin + header_height
        bottom = top + required_line_height_px
        center_x = page_width // 2

        title_font = QFont("Arial", 14, QFont.Bold)
        heading_font = QFont("Arial", 9, QFont.Bold)
        body_font = QFont("Arial", 7)
        small_font = QFont("Arial", 7)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.black)
        painter.setFont(title_font)
        painter.drawText(QRectF(margin, margin, page_width - 2 * margin, 120), Qt.AlignLeft | Qt.AlignVCenter, "Befahrungsgrafik")
        painter.setFont(heading_font)
        info = (
            f"{object_type}: {object_name}    Befahrung: {date_value or '-'}    "
            f"Länge/Abmessung: {length:.2f} m    "
            f"ZD: {self.rating_zd_label.text().replace('ZD: ', '')}    "
            f"ZB: {self.rating_zb_label.text().replace('ZB: ', '')}    "
            f"ZS: {self.rating_zs_label.text().replace('ZS: ', '')}"
        )
        painter.drawText(QRectF(margin, margin + 120, page_width - 2 * margin, header_height - 170), Qt.TextWordWrap, info)
        painter.drawLine(margin, margin + header_height - 35, page_width - margin, margin + header_height - 35)

        # Dieselben Farben wie in der Grafik der Oberfläche verwenden.
        painter.setPen(QPen(QColor("#475569"), 16, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(center_x, top, center_x, bottom)
        painter.setPen(QPen(QColor("#334155"), 3))
        painter.drawLine(center_x, top, center_x, bottom)
        painter.drawLine(center_x, bottom, center_x - 30, bottom - 58)
        painter.drawLine(center_x, bottom, center_x + 30, bottom - 58)

        if object_type == "Haltung":
            painter.setPen(QPen(QColor("#2563eb"), 7, Qt.SolidLine, Qt.RoundCap))
            for connection in self.current_connections:
                station = _gleitkommazahl_sicher_lesen(connection.get("station"), 0.0)
                y = top + int(round(anzeige_y_fuer_station(station)))
                side = -1 if int(connection.get("seite", 1)) < 0 else 1
                painter.drawLine(center_x, y, center_x + side * 72, y)

        left_width = center_x - margin - 105
        right_width = page_width - margin - (center_x + 105)
        label_height = min_gap_px - 10

        for index, (row, station, relative_y) in enumerate(display_positions):
            y = top + relative_y
            side_left = index % 2 == 0

            painter.setPen(QPen(QColor("#0f172a"), 4))
            painter.setBrush(Inspektionsgrafik.schadensfarbe_bestimmen(row))
            painter.drawEllipse(center_x - 16, y - 16, 32, 32)

            if side_left:
                line_end_x = center_x - 95
                painter.drawLine(center_x - 16, y, line_end_x, y)
                text_rect = QRectF(margin, y - label_height / 2, left_width, label_height)
                alignment = Qt.AlignRight | Qt.AlignVCenter | Qt.TextWordWrap
            else:
                line_end_x = center_x + 95
                painter.drawLine(center_x + 16, y, line_end_x, y)
                text_rect = QRectF(center_x + 105, y - label_height / 2, right_width, label_height)
                alignment = Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap

            painter.setFont(body_font)
            label = f"{station:.2f} m  {_text_sicher_lesen(row.get('kuerzel'))}  {_text_sicher_lesen(row.get('langtext'))}".strip()
            painter.drawText(text_rect, alignment, label)

        painter.setFont(small_font)
        footer = f"{len(self.damage_rows)} Einzelschäden | Erstellt mit EV-A-Kan TV Media"
        painter.setPen(Qt.black)
        painter.drawText(
            QRectF(margin, page_height - margin - footer_height, page_width - 2 * margin, footer_height),
            Qt.AlignCenter,
            footer,
        )
        painter.end()

    def _medienlisten_erstellen(self) -> None:
        """Löst Medien in einem Arbeitsthread auf, damit die Oberfläche nicht
        blockiert.
        """
        self.photo_items = []
        self.video_items = []
        self.inspection_video = None
        self._befahrungsvideo_status_aktualisieren()
        self._mediensuche_abbrechen()

        self._media_run_id += 1
        run_id = self._media_run_id
        config = OBJECT_CONFIG[self.cb_objektart.currentText()]
        foto_root_path, video_root_path = _qkan_medienstammpfade_laden()
        self.foto_root_path = foto_root_path
        self.video_root_path = video_root_path
        errors: list[str] = []
        if not foto_root_path:
            errors.append("In QKan ist kein Foto-Stammordner (fotoRootPath) eingestellt.")
        elif not Path(foto_root_path).is_dir():
            errors.append(f"Der in QKan eingestellte Foto-Stammordner ist nicht erreichbar:\n{foto_root_path}")
        if not video_root_path:
            errors.append("In QKan ist kein Video-Stammordner (videoRootPath) eingestellt.")
        elif not Path(video_root_path).is_dir():
            errors.append(f"Der in QKan eingestellte Video-Stammordner ist nicht erreichbar:\n{video_root_path}")
        if errors:
            message = "\n\n".join(errors)
            _loggen(message.replace("\n", " "), Qgis.Warning)
            self.lbl_status.setText("Medienprüfung abgebrochen: QKan-Medienpfade fehlen oder sind nicht erreichbar.")
            self.pb_foto_ordner_oeffnen.setEnabled(False)
            self.pb_video_ordner_oeffnen.setEnabled(False)
            self.pb_panoramo_ordner_oeffnen.setEnabled(False)
            self.lbl_fotovorschau.setText("QKan-Fotopfad fehlt oder ist nicht erreichbar")
            self.photo_caption.setText("")
            self.tw_videos.setRowCount(0)
            self.video_details.setText("")
            self._befahrungsvideo_status_aktualisieren()
            if message != self._last_media_path_error:
                QMessageBox.critical(
                    self,
                    "QKan-Medienpfade fehlen",
                    message + "\n\nBitte die Pfade in den QKan-Einstellungen festlegen.",
                )
            self._last_media_path_error = message
            return
        self._last_media_path_error = ""
        thread = QThread()
        worker = MediensucheArbeiter(
            [dict(row) for row in self.damage_rows],
            config["object_column"],
            foto_root_path,
            video_root_path,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.ausfuehren)
        worker.finished.connect(
            lambda photos, videos, inspection_video, current_run_id=run_id: self._medienaufloesung_beendet(
                photos, videos, inspection_video, current_run_id
            )
        )
        worker.failed.connect(
            lambda message, current_run_id=run_id: self._medienaufloesung_fehlgeschlagen(
                message, current_run_id
            )
        )
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda current_thread=thread: self._mediensuche_beendet(current_thread))
        thread.finished.connect(thread.deleteLater)
        ACTIVE_MEDIA_THREADS.append(thread)
        self._media_thread = thread
        self._media_worker = worker
        self.lbl_status.setText("Medien werden geprüft …")
        self._media_timeout.start(180000)
        thread.start()

    def _mediensuche_abbrechen(self) -> None:
        """Fordert den Abbruch an, ohne auf einen bereits gelöschten Qt-Wrapper
        zuzugreifen.
        """
        thread = self._media_thread
        if thread is None:
            return
        try:
            if thread.isRunning():
                thread.requestInterruption()
        except RuntimeError:
            # Qt kann den C++-QThread bereits gelöscht haben, während das Python-
            # Attribut noch auf dessen Wrapper verweist.
            self._media_thread = None
            self._media_worker = None

    def _mediensuche_beendet(self, thread: QThread) -> None:
        """Entfernt Verweise auf einen abgeschlossenen Medienthread sicher."""
        if thread in ACTIVE_MEDIA_THREADS:
            ACTIVE_MEDIA_THREADS.remove(thread)
        if self._media_thread is thread:
            self._media_thread = None
            self._media_worker = None

    def _medienzeitueberschreitung_stoppen(self) -> bool:
        """Stoppt den Zeitüberschreitungs-Timer, sofern Qt den Dialog noch nicht
        zerstört hat.
        """
        try:
            self._media_timeout.stop()
        except RuntimeError:
            # Ein verspätetes Ergebnis des Arbeitsthreads kann eintreffen, während der Dialog und sein
            # QTimer bereits zerstört werden. In diesem Fall darf kein Ergebnis mehr
            # auf die Oberfläche angewendet werden.
            return False
        return True

    @pyqtSlot(object, object, object, int)
    def _medienaufloesung_beendet(
        self, photos: object, videos: object, inspection_video: object, run_id: int
    ) -> None:
        """Übernimmt Ergebnisse nur, wenn sie zur aktuellen Medienanfrage gehören."""
        if run_id != self._media_run_id:
            _loggen(
                f"Veraltetes Medienergebnis verworfen (Lauf {run_id}, aktuell {self._media_run_id})."
            )
            return
        if not self._medienzeitueberschreitung_stoppen():
            return
        resolved_photos = list(photos)
        resolved_videos = list(videos)
        self.photo_items = [
            item
            for item in resolved_photos
            if isinstance(item, Medieneintrag)
            and 0 <= item.damage_index < len(self.damage_rows)
        ]
        self.video_items = [
            item
            for item in resolved_videos
            if isinstance(item, Medieneintrag)
            and 0 <= item.damage_index < len(self.damage_rows)
        ]
        if (
            isinstance(inspection_video, Medieneintrag)
            and 0 <= inspection_video.damage_index < len(self.damage_rows)
        ):
            self.inspection_video = inspection_video
        else:
            self.inspection_video = None
        if len(self.photo_items) != len(resolved_photos) or len(self.video_items) != len(resolved_videos):
            _loggen(
                "Veraltete Medientreffer ohne passende Schadenszeile wurden verworfen.",
                Qgis.Warning,
            )
        self._befahrungsvideo_status_aktualisieren()
        self._videotabelle_fuellen()
        self.current_photo_index = 0 if self.photo_items else -1
        self._aktuelles_foto_anzeigen()
        if self.damage_rows:
            self.tw_schaeden.selectRow(0)
        self.lbl_status.setText(
            f"{len(self.damage_rows):,} Einzelschäden · "
            f"{len(self.photo_items):,} Fotoeinträge · "
            f"{len(self.video_items):,} Videostellen"
        )

    @pyqtSlot(str, int)
    def _medienaufloesung_fehlgeschlagen(self, message: str, run_id: int) -> None:
        """Behandelt einen Fehler nur, wenn er zur aktuellen Medienanfrage gehört."""
        if run_id != self._media_run_id:
            _loggen(
                f"Veralteter Medienfehler verworfen (Lauf {run_id}, aktuell {self._media_run_id})."
            )
            return
        if not self._medienzeitueberschreitung_stoppen():
            return
        _loggen(f"Medienprüfung abgebrochen: {message}", Qgis.Warning)
        self.close()

    def _medienaufloesung_zeitueberschritten(self) -> None:
        """Verwirft die aktuelle Anfrage und schließt nach drei Minuten."""
        self._media_run_id += 1
        self._mediensuche_abbrechen()
        self.iface.messageBar().pushMessage(
            "QKan Medieninspektor",
            "Die Medienprüfung dauerte länger als 3 Minuten; die Ansicht wurde geschlossen.",
            level=Qgis.Warning,
            duration=8,
        )
        self.close()

    def _videotabelle_fuellen(self) -> None:
        """Füllt die Videopositionen und verwirft veraltete Einträge defensiv."""
        valid_items = [
            media
            for media in self.video_items
            if 0 <= media.damage_index < len(self.damage_rows)
        ]
        if len(valid_items) != len(self.video_items):
            _loggen(
                "Veraltete Videotreffer ohne passende Schadenszeile wurden verworfen.",
                Qgis.Warning,
            )
        self.video_items = valid_items
        self.tw_videos.setRowCount(len(self.video_items))
        for row_index, media in enumerate(self.video_items):
            damage = self.damage_rows[media.damage_index]
            status = media.resolution_status or self._trefferstatus_bestimmen(media.candidates)
            filename = (
                Path(media.candidates[0].full_path).name
                if media.candidates
                else _dateiname_aus_pfad(media.stored_path)
            )
            values = [
                _text_sicher_lesen(damage.get("untersuchtag")),
                f"{_gleitkommazahl_sicher_lesen(damage.get('station'), 0.0):.2f}",
                _text_sicher_lesen(damage.get("kuerzel")),
                _text_sicher_lesen(damage.get("timecode")),
                status,
                filename,
            ]
            for column, value in enumerate(values):
                self.tw_videos.setItem(row_index, column, QTableWidgetItem(value))
        if self.video_items:
            self.tw_videos.selectRow(0)
        else:
            self.pb_video_ordner_oeffnen.setEnabled(False)
            self.video_details.setText("Keine Videostellen für diese Auswahl.")

    @staticmethod
    def _trefferstatus_bestimmen(candidates: Iterable[Medientreffer]) -> str:
        """Liefert einen kurzen Status der Medienauflösung."""
        candidates_tuple = tuple(candidates)
        if not candidates_tuple:
            return "nicht gefunden"
        if len(candidates_tuple) > 1 or any(item.ambiguous for item in candidates_tuple):
            return f"mehrdeutig ({len(candidates_tuple)})"
        return candidates_tuple[0].method

    def _schadensauswahl_geaendert(
        self,
        current_row: int,
        _current_column: int,
        _previous_row: int,
        _previous_column: int,
    ) -> None:
        """Synchronisiert Tabelle, Grafik, Fotos und Videos."""
        if current_row < 0 or current_row >= len(self.damage_rows):
            return
        self.inspektionsgrafik.auswahl_setzen(current_row)
        for photo_index, photo in enumerate(self.photo_items):
            if photo.damage_index == current_row:
                self.current_photo_index = photo_index
                self._aktuelles_foto_anzeigen()
                break
        for video_index, video in enumerate(self.video_items):
            if video.damage_index == current_row:
                self.tw_videos.selectRow(video_index)
                break

    def _schadenszeile_auswaehlen(self, index: int) -> None:
        """Wählt aus dem Schema eine Schadenstabellenzeile aus."""
        if 0 <= index < self.tw_schaeden.rowCount():
            self.tw_schaeden.selectRow(index)
            self.tw_schaeden.scrollToItem(self.tw_schaeden.item(index, 0))

    def _foto_wechseln(self, offset: int) -> None:
        """Wechselt zum vorherigen oder nächsten Fotoeintrag."""
        if not self.photo_items:
            return
        self.current_photo_index = (self.current_photo_index + offset) % len(self.photo_items)
        self._aktuelles_foto_anzeigen()
        damage_index = self.photo_items[self.current_photo_index].damage_index
        self.tw_schaeden.selectRow(damage_index)

    def _aktuelles_foto(self) -> Optional[Medieneintrag]:
        """Liefert den aktuell ausgewählten Fotoeintrag."""
        if 0 <= self.current_photo_index < len(self.photo_items):
            return self.photo_items[self.current_photo_index]
        return None

    def _aktuelles_foto_anzeigen(self) -> None:
        """Lädt das ausgewählte indizierte Foto in die Vorschau."""
        item = self._aktuelles_foto()
        if item is None:
            self.pb_foto_ordner_oeffnen.setEnabled(False)
            self.lbl_fotovorschau.setPixmap(QPixmap())
            self.lbl_fotovorschau.setText("Keine Fotos für diese Auswahl.")
            self.photo_caption.setText("")
            return
        self.pb_foto_ordner_oeffnen.setEnabled(bool(self.foto_root_path))
        candidate = item.candidates[0] if item.candidates else None
        status = item.resolution_status or self._trefferstatus_bestimmen(item.candidates)
        self.photo_caption.setText(
            f"{self.current_photo_index + 1} von {len(self.photo_items)} · "
            f"{item.caption}\nGespeichert: {item.stored_path}\nStatus: {status}"
        )
        if candidate is None:
            self.lbl_fotovorschau.setPixmap(QPixmap())
            self.lbl_fotovorschau.setText(
                "Keine passende Bilddatei gefunden."
            )
            return
        pixmap = QPixmap(candidate.full_path)
        if pixmap.isNull():
            self.lbl_fotovorschau.setPixmap(QPixmap())
            self.lbl_fotovorschau.setText(
                "Die indexierte Bilddatei kann aktuell nicht geladen werden:\n"
                + candidate.full_path
            )
            return
        self.lbl_fotovorschau.setText("")
        self.lbl_fotovorschau.setPixmap(
            pixmap.scaled(
                self.lbl_fotovorschau.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def resizeEvent(self, event: Any) -> None:
        """Skaliert ein geöffnetes Foto bei Änderung der Dialoggröße neu."""
        super().resizeEvent(event)
        if self._aktuelles_foto() is not None:
            QTimer.singleShot(0, self._aktuelles_foto_anzeigen)


    def _medienordner_bestimmen(
        self, item: Optional[Medieneintrag], media_type: str, root_path: str
    ) -> Optional[Path]:
        """Liefert den vorhandenen Dateiordner oder den erwarteten Ordner unterhalb des
        QKan-Stammordners.
        """
        if not root_path or not Path(root_path).is_dir():
            return None
        if item is not None:
            for candidate in item.candidates:
                if _pfad_innerhalb_stammordner(candidate.full_path, root_path):
                    candidate_path = Path(candidate.full_path)
                    folder = candidate_path.parent
                    if folder.is_dir():
                        return folder
            raw_stored_path = _text_sicher_lesen(item.stored_path).strip().strip('"').strip("'")
            if raw_stored_path and os.path.isabs(raw_stored_path):
                absolute_folder = Path(raw_stored_path).parent
                if (
                    _pfad_innerhalb_stammordner(str(absolute_folder), root_path)
                    and absolute_folder.is_dir()
                ):
                    return absolute_folder
            normalized = _pfadtext_normalisieren(item.stored_path)
            parts = [part for part in normalized.split("/") if part not in ("", ".", "..")]
            if parts:
                relative_folder_parts = parts[:-1]
                for search_root in _medien_suchwurzeln(media_type, root_path):
                    expected = search_root.joinpath(*relative_folder_parts)
                    if expected.is_dir():
                        return expected
        roots = _medien_suchwurzeln(media_type, root_path)
        return next((root for root in roots if root.is_dir()), Path(root_path))

    def _ordner_oeffnen(
        self, item: Optional[Medieneintrag], media_type: str, root_path: str, title: str
    ) -> None:
        """Öffnet einen Medienordner, ohne den konfigurierten QKan-Stammordner zu
        verlassen.
        """
        folder = self._medienordner_bestimmen(item, media_type, root_path)
        if folder is None or not folder.is_dir():
            QMessageBox.warning(
                self,
                title,
                "Der in QKan eingestellte Medienordner ist nicht erreichbar.",
            )
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _fotoordner_oeffnen(self) -> None:
        """Öffnet den Ordner des aktuellen Fotos oder dessen erwarteten QKan-Ordner."""
        self._ordner_oeffnen(
            self._aktuelles_foto(), "Bild", self.foto_root_path, "Fotoordner öffnen"
        )

    def _foto_extern_oeffnen(self) -> None:
        """Öffnet das aktuelle Foto mit dem Betriebssystem."""
        item = self._aktuelles_foto()
        if item is None:
            return
        candidate = item.candidates[0] if item.candidates else None
        if candidate is None:
            QMessageBox.warning(
                self,
                "Keine Bilddatei gefunden",
                "Für diesen Eintrag wurde keine erreichbare Bilddatei gefunden.",
            )
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(candidate.full_path))

    def _videoauswahl_geaendert(
        self,
        current_row: int,
        _current_column: int,
        _previous_row: int,
        _previous_column: int,
    ) -> None:
        """Zeigt Details an und synchronisiert die Schadensauswahl."""
        if not (0 <= current_row < len(self.video_items)):
            self.pb_video_ordner_oeffnen.setEnabled(False)
            return
        self.pb_video_ordner_oeffnen.setEnabled(bool(self.video_root_path))
        item = self.video_items[current_row]
        self.tw_schaeden.selectRow(item.damage_index)
        paths = "\n".join(candidate.full_path for candidate in item.candidates[:5])
        if len(item.candidates) > 5:
            paths += f"\n… und {len(item.candidates) - 5} weitere"
        self.video_details.setText(
            f"{item.caption}\nStartzeit: {item.start_seconds:.2f} s\n"
            f"Gespeichert: {item.stored_path}\n"
            f"Status: {item.resolution_status or self._trefferstatus_bestimmen(item.candidates)}"
            + (f"\n{paths}" if paths else "")
        )

    def _befahrungsvideo_status_aktualisieren(self) -> None:
        """Zeigt an, ob ein vollständiges Befahrungsvideo verknüpft ist."""
        item = self.inspection_video
        linked = bool(item and item.candidates)
        self.pb_befahrungsvideo_oeffnen.setEnabled(linked)
        self.pb_panoramo_oeffnen.setEnabled(linked)
        self.pb_panoramo_ordner_oeffnen.setEnabled(linked)
        if linked:
            candidate = item.candidates[0]
            filename = Path(candidate.full_path).name
            self.inspection_video_status.setText(
                f"Befahrungsvideo verlinkt: Ja · {filename}"
            )
            self.panoramo_info.setText(
                "Panoramo verwendet das verlinkte Befahrungsvideo und öffnet es "
                f"mit dem Windows-Standardprogramm.\n\n{filename}"
            )
        else:
            self.inspection_video_status.setText("Befahrungsvideo verlinkt: Nein")
            self.panoramo_info.setText("Kein Panoramo-Befahrungsvideo verlinkt")

    def _videoordner_oeffnen(self) -> None:
        """Öffnet den Ordner des aktuell ausgewählten Schadensvideos."""
        self._ordner_oeffnen(
            self._aktuelles_video(), "Video", self.video_root_path, "Videoordner öffnen"
        )

    def _panoramoordner_oeffnen(self) -> None:
        """Öffnet den Ordner des verknüpften Befahrungs-/Panoramo-Videos."""
        self._ordner_oeffnen(
            self.inspection_video,
            "Video",
            self.video_root_path,
            "Panoramo-Ordner öffnen",
        )

    def _befahrungsvideo_oeffnen(self) -> None:
        """Öffnet das verknüpfte vollständige Befahrungsvideo von Beginn an."""
        if self.inspection_video is None:
            return
        self._videoeintrag_oeffnen(self.inspection_video, start_at_damage=False)

    def _panoramo_oeffnen(self) -> None:
        """Öffnet die verknüpfte Panoramo-Inspektionsdatei mit dem Standardprogramm des
        Betriebssystems. Das entspricht dem QKan-Verhalten von
        ``ShowVideo.show_panoramo``: Die vollständige Inspektionsdatei wird extern
        ohne Timecode-Sprung geöffnet.
        """
        item = self.inspection_video
        if item is None:
            return
        candidate = item.candidates[0] if item.candidates else None
        if candidate is None:
            QMessageBox.warning(
                self,
                "Keine Panoramo-Datei gefunden",
                "Für diese Befahrung wurde keine erreichbare Panoramo-Datei gefunden.",
            )
            return
        path = Path(candidate.full_path)
        if not path.is_file():
            QMessageBox.warning(
                self,
                "Panoramo-Datei nicht erreichbar",
                "Die verlinkte Datei ist aktuell nicht erreichbar:\n\n" + str(path),
            )
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _aktuelles_video(self) -> Optional[Medieneintrag]:
        """Liefert den aktuell ausgewählten Videoeintrag."""
        row = self.tw_videos.currentRow()
        if 0 <= row < len(self.video_items):
            return self.video_items[row]
        return None


    @staticmethod
    def _vlc_finden() -> str:
        """Sucht eine installierte externe VLC-Anwendung."""
        configured = _text_sicher_lesen(
            QgsProject.instance().readEntry(PLUGIN_GROUP, "vlcPath", "")[0]
        )
        candidates = [
            configured,
            shutil.which("vlc") or "",
            str(Path(os.environ.get("ProgramFiles", "")) / "VideoLAN" / "VLC" / "vlc.exe"),
            str(Path(os.environ.get("ProgramFiles(x86)", "")) / "VideoLAN" / "VLC" / "vlc.exe"),
        ]
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return candidate
        return ""

    def _ausgewaehltes_video_oeffnen(self) -> None:
        """Öffnet das ausgewählte Video direkt am Schadens-Timecode."""
        item = self._aktuelles_video()
        if item is None:
            return
        self._videoeintrag_oeffnen(item, start_at_damage=True)

    def _videoeintrag_oeffnen(self, item: Medieneintrag, start_at_damage: bool) -> None:
        """Öffnet ein aufgelöstes Video entweder am Schaden oder am Anfang."""
        candidate = item.candidates[0] if item.candidates else None
        if candidate is None:
            QMessageBox.warning(
                self,
                "Keine Videodatei gefunden",
                "Für diesen Eintrag wurde keine erreichbare Videodatei gefunden.",
            )
            return
        if not Path(candidate.full_path).is_file():
            QMessageBox.warning(
                self,
                "Videodatei nicht erreichbar",
                "Die gefundene Datei ist aktuell nicht erreichbar:\n\n"
                + candidate.full_path,
            )
            return
        vlc = self._vlc_finden()
        if not vlc:
            answer = QMessageBox.question(
                self,
                "VLC nicht gefunden",
                "VLC wurde nicht automatisch gefunden. Soll die VLC-Datei jetzt gewählt werden?\n\n"
                "Ohne VLC kann das Video nur im Standardprogramm und möglicherweise nicht am Timecode geöffnet werden.",
                QMessageBox.Yes | QMessageBox.No,
            )
            if answer == QMessageBox.Yes:
                vlc, _selected_filter = QFileDialog.getOpenFileName(
                    self,
                    "vlc.exe auswählen",
                    r"C:\Program Files\VideoLAN\VLC",
                    "VLC (vlc.exe);;Programme (*.exe);;Alle Dateien (*)",
                )
                if vlc:
                    QgsProject.instance().writeEntry(PLUGIN_GROUP, "vlcPath", vlc)
                    QgsProject.instance().setDirty(True)
            if not vlc:
                QDesktopServices.openUrl(QUrl.fromLocalFile(candidate.full_path))
                return
        try:
            subprocess.Popen(
                [
                    vlc,
                    f"--start-time={item.start_seconds if start_at_damage else 0.0:.3f}",
                    candidate.full_path,
                ],
                close_fds=True,
            )
        except OSError as error:
            QMessageBox.critical(self, "VLC konnte nicht gestartet werden", _text_sicher_lesen(error))

    def _ansicht_leeren(self) -> None:
        """Leert alle inspektionsabhängigen Widgets und verwirft ausstehende
        Medienarbeiten.
        """
        self._media_run_id += 1
        self._mediensuche_abbrechen()
        self._medienzeitueberschreitung_stoppen()
        self.damage_rows = []
        self.photo_items = []
        self.video_items = []
        self.inspection_video = None
        self.current_photo_index = -1
        self.current_overall = None
        self.current_connections = []
        self.current_date_value = ""
        self.current_all_dates = False
        self._table_dirty = False
        self._rating_dirty = False
        self._deleted_damage_rowids.clear()
        self.tw_schaeden.setRowCount(0)
        self.tw_videos.setRowCount(0)
        self.inspektionsgrafik.daten_setzen([], self.cb_objektart.currentText(), 1.0, [])
        self.pb_foto_ordner_oeffnen.setEnabled(False)
        self.pb_video_ordner_oeffnen.setEnabled(False)
        self.pb_panoramo_ordner_oeffnen.setEnabled(False)
        self.lbl_fotovorschau.setPixmap(QPixmap())
        self.lbl_fotovorschau.setText("Keine Auswahl")
        self.photo_caption.setText("")
        self.video_details.setText("")
        self._befahrungsvideo_status_aktualisieren()
        self.rating_object_label.setText("Objekt: –")
        self.rating_date_label.setText("Befahrung: –")
        self.rating_zd_label.setText("ZD: –")
        self.rating_zb_label.setText("ZB: –")
        self.rating_zs_label.setText("ZS: –")
        self.rating_info_label.setText("Länge/Abmessung: –")


class BefahrungsmedienPlugin:
    """In QKan integrierte Steuerung der TV-Befahrungsmedien."""

    def __init__(self, iface: Any) -> None:
        self.iface = iface
        self.action: Optional[QAction] = None
        self.pick_action: Optional[QAction] = None
        self.dialog: Optional[BefahrungsmedienDialog] = None
        self.viewer_dialog: Optional[BefahrungsmedienDialog] = None
        self.identify_tool: Optional[ObjektauswahlWerkzeug] = None
        self.previous_map_tool: Any = None

    def initGui(self) -> None:
        """Registriert den TV-Befahrungsbutton in QKan-Inspektion."""
        if self.pick_action is not None:
            return

        from qkan import QKan

        icon_path = str(Path(__file__).parent / "res" / "tv_befahrung.png")
        self.pick_action = QKan.instance.add_action(
            icon_path=icon_path,
            text="Befahrungsmedien",
            toolbar="QKan-Inspektion",
            callback=self._qkan_aktion_ausgeloest,
            checkable=True,
            parent=self.iface.mainWindow(),
        )
        self.pick_action.setObjectName("qkan_inspektion_tv_befahrung")
        self.pick_action.setToolTip(
            "Fotos, Videos und Schäden einer Befahrung gemeinsam anzeigen"
        )
        self.pick_action.toggled.connect(self._objektauswahl_umschalten)
        self.iface.action_tv_befahrung = self.pick_action

    def _qkan_aktion_ausgeloest(self, _checked: bool = False) -> None:
        """QKan registriert Aktionen über ``triggered``; die Logik nutzt ``toggled``.

        Die eigentliche Umschaltung erfolgt über ``toggled``, damit auch ein
        programmgesteuertes Zurücksetzen des Buttons den Auswahlmodus beendet.
        """

    def unload(self) -> None:
        """Bereinigt Kartenwerkzeug und Dialoge beim Entladen von QKan."""
        if self.identify_tool is not None:
            try:
                if self.iface.mapCanvas().mapTool() is self.identify_tool:
                    self.iface.mapCanvas().unsetMapTool(self.identify_tool)
            except RuntimeError:
                pass
            try:
                self.identify_tool.deleteLater()
            except RuntimeError:
                pass
            self.identify_tool = None

        if self.dialog is not None:
            try:
                self.dialog.close()
                self.dialog.deleteLater()
            except RuntimeError:
                pass
            self.dialog = None

        if self.viewer_dialog is not None:
            try:
                self.viewer_dialog.close()
                self.viewer_dialog.deleteLater()
            except RuntimeError:
                pass
            self.viewer_dialog = None

        if self.pick_action is not None:
            try:
                self.pick_action.toggled.disconnect(
                    self._objektauswahl_umschalten
                )
            except (TypeError, RuntimeError):
                pass
            self.pick_action = None

        self.action = None
        self.previous_map_tool = None

    def _objektauswahl_umschalten(self, aktiviert: bool) -> None:
        """Schaltet den dauerhaften Kartenauswahlmodus über die QKan-Aktion um."""
        if aktiviert:
            self._objektauswahl_starten()
        else:
            self._objektauswahl_beenden()

    def _objektauswahl_starten(self) -> None:
        """Aktiviert das dauerhafte QKan-Kartenauswahlwerkzeug."""
        canvas = self.iface.mapCanvas()
        if self.identify_tool is None:
            self.identify_tool = ObjektauswahlWerkzeug(canvas)
            self.identify_tool.object_picked.connect(
                self._ausgewaehltes_objekt_oeffnen
            )
            self.identify_tool.selection_cancelled.connect(
                self._objektauswahl_abbrechen
            )
            try:
                self.identify_tool.deactivated.connect(
                    self._objektauswahl_extern_beendet
                )
            except AttributeError:
                pass

        if canvas.mapTool() is not self.identify_tool:
            self.previous_map_tool = canvas.mapTool()
            canvas.setMapTool(self.identify_tool)
        self.iface.messageBar().pushMessage(
            "QKan Befahrungsmedien",
            "Auswahlmodus aktiv: Objekte nacheinander anklicken. "
            "Rechtsklick oder TV-Button beendet den Modus.",
            level=Qgis.Info,
            duration=8,
        )

    def _objektauswahl_beenden(self) -> None:
        """Beendet den Auswahlmodus und stellt das vorherige Kartenwerkzeug wieder her."""
        canvas = self.iface.mapCanvas()
        if (
            self.identify_tool is not None
            and canvas.mapTool() is self.identify_tool
        ):
            previous = self.previous_map_tool
            if previous is not None and previous is not self.identify_tool:
                canvas.setMapTool(previous)
            else:
                canvas.unsetMapTool(self.identify_tool)
        self.previous_map_tool = None

    def _objektauswahl_abbrechen(self) -> None:
        """Beendet den Auswahlmodus per Rechtsklick."""
        if self.pick_action is not None and self.pick_action.isChecked():
            self.pick_action.setChecked(False)
        else:
            self._objektauswahl_beenden()

    def _objektauswahl_extern_beendet(self) -> None:
        """Synchronisiert die QKan-Aktion, wenn ein anderes Kartenwerkzeug übernimmt."""
        if self.pick_action is not None:
            try:
                if self.pick_action.isChecked():
                    previous_block = self.pick_action.blockSignals(True)
                    try:
                        self.pick_action.setChecked(False)
                    finally:
                        self.pick_action.blockSignals(previous_block)
            except RuntimeError:
                self.pick_action = None
        self.previous_map_tool = None

    def _ausgewaehltes_objekt_oeffnen(
        self,
        object_type: str,
        object_name: str,
    ) -> None:
        """Öffnet die kompakte Objektansicht und lässt den Auswahlmodus aktiv."""
        if self.viewer_dialog is None:
            self.viewer_dialog = BefahrungsmedienDialog(
                self.iface,
                viewer_only=True,
            )
            self.viewer_dialog.finished.connect(
                self._objektansicht_geschlossen
            )
        self.viewer_dialog.show()
        self.viewer_dialog.raise_()
        self.viewer_dialog.activateWindow()
        QTimer.singleShot(
            0,
            lambda: (
                self.viewer_dialog
                and self.viewer_dialog._objekt_auswaehlen(
                    object_type,
                    object_name,
                )
            ),
        )

    def anzeigen(self) -> None:
        """Öffnet die vollständige Medienansicht oder bringt sie in den Vordergrund."""
        if self.dialog is None:
            self.dialog = BefahrungsmedienDialog(self.iface)
            self.dialog.finished.connect(self._dialog_geschlossen)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def _dialog_geschlossen(self, _result: int) -> None:
        """Gibt den geschlossenen Dialog frei."""
        if self.dialog is not None:
            self.dialog.deleteLater()
            self.dialog = None

    def _objektansicht_geschlossen(self, _result: int) -> None:
        """Gibt die geschlossene kompakte Objektansicht frei, während der Kartenmodus
        aktiv bleibt.
        """
        if self.viewer_dialog is not None:
            self.viewer_dialog.deleteLater()
            self.viewer_dialog = None
