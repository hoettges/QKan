"""
media_player.py - VLC MediaPlayer für QGIS-Plugin Datenbankviewer
Modularisierte Version des Video-Players.
"""

# =========================================================
# Importe
# =========================================================

import os
import sys
import json
import re
from pathlib import Path

from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from qgis.PyQt import uic
from qgis.utils import iface
from qgis.gui import QgsMapToolIdentifyFeature
from qgis.core import QgsProject

from qkan.tools.vlc_error import VlcLoadError
from qkan.utils import get_logger

LOGGER = get_logger(__name__)

# =========================================================
# VLC-Import
# =========================================================

try:
    from ..external.vlc import vlc
except OSError:
    LOGGER.info("Could not open/find VLC. Is it installed?", exc_info=True)
    vlc = None


# =========================================================
# Optionale lokale Imports
# =========================================================

try:
    from ..settings.VideoSettingsDialog_qkan import VideoSettingsDialog_qkan
except ImportError:
    VideoSettingsDialog_qkan = None


# =========================================================
# UI laden
# =========================================================

FORM_CLASS_MediaPlayer, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "tools", "res", "videoplayer.ui")
)


# =========================================================
# Hauptklasse MediaPlayer
# =========================================================

class MediaPlayer(QDialog, FORM_CLASS_MediaPlayer):
    """VLC-basierter Video-Player für Befahrungs-Videos."""

    def __init__(self, film_dateiname=None, parent=None):
        super().__init__(parent)
        self.film_dateiname_value = film_dateiname.text() if film_dateiname else ""
        self.setupUi(self)

        # Video-Settings (optional)
        self.video_settings_dialog = (
            VideoSettingsDialog_qkan() if VideoSettingsDialog_qkan else None
        )

        if vlc is None:
            raise VlcLoadError

        # VLC initialisieren
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.set_video_window()

        # Video-Pfad laden (Standard: aus lokaler JSON-Datei)
        self.base_path = self.load_video_path()

        # Optional: Pfadkontrolle über Projektordner
        self.apply_project_video_path_if_enabled()

        # Debug-Ausgabe
        print(f"Verwendeter Video-Basis-Pfad: {self.base_path}")

        # UI-Verbindungen
        self.playpause.clicked.connect(self.play_pause)
        self.playpause.clicked.connect(self.update_time)
        self.screenshot.clicked.connect(self.take_screenshot)
        self.rateup.clicked.connect(self.playbackspeed_up)
        self.ratedown.clicked.connect(self.playbackspeed_down)
        self.horizontalSlider.sliderMoved.connect(self.set_position)
        self.horizontalSlider.sliderMoved.connect(self.update_time)

        # Initialisierung
        self.horizontalSlider.setMaximum(1000)
        self.timelabel.setText("00:00:00")
        self.isPaused = False

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui2)
        self.timer.timeout.connect(self.update_time)

        self.iface = iface
        self.identify_tool = QgsMapToolIdentifyFeature(self.iface.mapCanvas())

        # Feature-Info laden
        self.load_feature_info()

        # Fenster-Flags
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )

    # =========================================================
    # Lokale JSON-Pfade
    # =========================================================

    def _json_dir(self):
        """Gibt den lokalen json-Unterordner relativ zu dieser Datei zurück."""
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(tool_dir, "json")

    def _video_path_json(self):
        """Pfad zur lokalen videopfad.json."""
        return os.path.join(self._json_dir(), "videopfad.json")

    # =========================================================
    # Pfadlogik
    # =========================================================

    def apply_project_video_path_if_enabled(self):
        """
        Wenn die Checkbox 'Pfadkontrolle' im Settings-Dialog gesetzt ist,
        nutze stattdessen den Ordner 'Videos' im Verzeichnis des aktuellen
        QGIS-Projekts als Basis-Pfad.
        """
        if not self.video_settings_dialog:
            return

        cb = getattr(self.video_settings_dialog, "checkBox_Pfadkontrolle", None)
        if cb is None:
            return

        if cb.isChecked():
            proj = QgsProject.instance()
            project_path = proj.fileName()
            if project_path:
                project_dir = Path(project_path).parent
                videos_dir = project_dir / "Videos"
                self.base_path = os.path.normpath(str(videos_dir))
                print(
                    f"Pfadkontrolle aktiv: nutze Projekt-Videos-Ordner: {self.base_path}"
                )
            else:
                print(
                    "Pfadkontrolle aktiv, aber Projekt ist noch nicht gespeichert – "
                    "bleibe bei JSON-Pfad."
                )
        else:
            print("Pfadkontrolle nicht aktiv – nutze Pfad aus lokaler videopfad.json.")

    def load_video_path(self):
        """Lädt Video-Basis-Pfad aus lokaler JSON-Datei."""
        json_file = self._video_path_json()

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("videopfad", "")
        except FileNotFoundError:
            print(f"videopfad.json nicht gefunden: {json_file}")
            return ""
        except json.JSONDecodeError as e:
            print(f"videopfad.json enthält ungültiges JSON: {e}")
            return ""
        except Exception as e:
            print(f"Video-Pfad laden fehlgeschlagen: {e}")
            return ""

    # =========================================================
    # VLC-Fenster
    # =========================================================

    def set_video_window(self):
        """Setzt VLC-Video-Output auf QFrame."""
        if sys.platform.startswith("linux"):
            self.mediaplayer.set_xwindow(self.frame.winId())
        elif sys.platform == "win32":
            self.mediaplayer.set_hwnd(self.frame.winId())
        elif sys.platform == "darwin":
            self.mediaplayer.set_nsobject(self.frame.winId())

    # =========================================================
    # Feature-Info
    # =========================================================

    def load_feature_info(self):
        """Lädt Layer-/Feature-Informationen in die UI."""
        layer = self.iface.activeLayer()
        if not layer:
            self.Haltungsname.setText("No active layer.")
            self.film_dateiname.setText("")
            return

        selected_ids = layer.selectedFeatureIds()
        if len(selected_ids) == 0:
            self.Haltungsname.setText("No feature selected.")
            self.film_dateiname.setText("")
            return

        feature = layer.getFeature(selected_ids[0])
        haltnam = feature.attribute("haltnam") or ""
        self.Haltungsname.setText(str(haltnam))
        self.film_dateiname.setText(self.film_dateiname_value or "")

    # =========================================================
    # Wiedergabesteuerung
    # =========================================================

    def play_pause(self):
        """Play/Pause Toggle."""
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playpause.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return
            self.playpause.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def stop(self):
        """Stoppt den Player."""
        self.mediaplayer.stop()
        self.playpause.setText("Play")

    def set_position(self):
        """Setzt die Position per Slider."""
        pos = self.horizontalSlider.value()
        self.mediaplayer.set_position(pos / 1000.0)

    def playbackspeed_up(self):
        """Erhöht die Abspielgeschwindigkeit."""
        current_speed = self.mediaplayer.get_rate()
        self.mediaplayer.set_rate(current_speed * 2)

    def playbackspeed_down(self):
        """Verringert die Abspielgeschwindigkeit."""
        current_speed = self.mediaplayer.get_rate()
        self.mediaplayer.set_rate(current_speed / 2)

    # =========================================================
    # Dateilogik
    # =========================================================

    def open_file(self):
        """Öffnet und lädt eine Video-Datei anhand des Dateinamens aus dem UI."""
        if vlc is None:
            raise VlcLoadError

        video = self.film_dateiname.text()
        if not video:
            return

        # 1. Problematische / direkt vor der Dateiendung in _ umwandeln
        # Beispiel: "... 43-E/56-E.mpg" -> "... 43-E_56-E.mpg"
        video = re.sub(r"/([^/]*\.[^.]+)$", r"_\1", video)

        # 2. Alle / im Namen in _ umwandeln
        video = video.replace("/", "_")

        print(f"Verwendeter Pfad (Dateiname): {video}")

        if not self.base_path:
            QMessageBox.warning(
                self,
                "Kein Video-Basis-Pfad",
                "Es ist kein Basis-Pfad für Videos definiert.",
            )
            return

        self.base_path = os.path.normpath(self.base_path)
        print(f"Verwendeter Video-Basis-Pfad: {self.base_path}")

        full_video_path = os.path.normpath(os.path.join(self.base_path, video))
        print(f"Prüfe direkten Pfad: {full_video_path}")
        file_path = Path(full_video_path)

        filename = None

        # 1. Direkte Übereinstimmung prüfen
        if file_path.is_file():
            filename = full_video_path
            print(f"Direkte Datei gefunden: {filename}")

        else:
            print("Direkte Datei nicht gefunden, prüfe Variante mit führender 0.")

            # 2. Fallback: führende Zahlenkombination um genau eine 0 ergänzen
            basename = os.path.basename(video)
            match_leading_number = re.match(r"^(\d+)(.*)$", basename)

            if match_leading_number:
                original_number = match_leading_number.group(1)
                rest_name = match_leading_number.group(2)
                alt_basename = f"0{original_number}{rest_name}"
                alt_full_path = os.path.normpath(
                    os.path.join(self.base_path, alt_basename)
                )

                print(f"Prüfe Alternative mit führender 0: {alt_full_path}")

                if Path(alt_full_path).is_file():
                    filename = alt_full_path
                    print(f"Datei mit führender 0 gefunden: {filename}")

            if not filename:
                print(
                    "Alternative mit führender 0 nicht gefunden, starte Präfix-Suche."
                )

                match = re.match(r"^(\d+)", os.path.basename(video))
                prefix = match.group(1) if match else ""
                print(f"Ermitteltes Präfix: '{prefix}'")

                if prefix:
                    alt_prefix = f"0{prefix}"

                    if not os.path.isdir(self.base_path):
                        QMessageBox.warning(
                            self,
                            "Videos-Ordner nicht gefunden",
                            f"Der Ordner für die Videos existiert nicht:\n{self.base_path}",
                        )
                        return

                    print(f"Suche im Verzeichnis: {self.base_path}")
                    candidates = []

                    for item in os.listdir(self.base_path):
                        if item.startswith(prefix) or item.startswith(alt_prefix):
                            full_candidate = os.path.join(self.base_path, item)
                            if os.path.isfile(full_candidate):
                                candidates.append(full_candidate)
                                print(f"Kandidat gefunden: {full_candidate}")

                    if len(candidates) == 1:
                        filename = candidates[0]
                        print(f"Verwende eindeutigen Kandidaten: {filename}")
                    elif len(candidates) > 1:
                        print("Mehrere Kandidaten gefunden:")
                        for c in candidates:
                            print(f"  {c}")
                        filename = candidates[0]
                        print(f"Verwende ersten Kandidaten: {filename}")
                    else:
                        print("Keine Datei mit diesem Präfix gefunden.")
                else:
                    print(f"Kein numerisches Präfix in '{video}' gefunden.")

        if not filename:
            QMessageBox.information(self, "Keine Datei", "Keine passende Datei gefunden.")
            return

        filename = os.path.normpath(filename)
        print(f"Finaler Video-Pfad: {filename}")

        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)
        self.media.parse()
        self.setWindowTitle(self.media.get_meta(0))

        try:
            events = self.mediaplayer.event_manager()
            events.event_attach(
                vlc.EventType.MediaPlayerPositionChanged,
                self._on_vlc_position_changed,
            )
        except Exception as e:
            print(f"VLC-Event konnte nicht registriert werden: {e}")

        self.play_pause()

    # =========================================================
    # VLC-Events / UI-Updates
    # =========================================================

    def _on_vlc_position_changed(self, event):
        try:
            self.update_ui()
        except Exception as e:
            print(f"Fehler in update_ui: {e}")

    def update_ui(self, event=None):
        """UI-Update bei Positionsänderung."""
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.horizontalSlider.setValue(media_pos)
        if media_pos >= 0 and self.mediaplayer.is_playing():
            self.update_time()

    def update_ui2(self):
        """Zusätzlicher UI-Update über Timer."""
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.horizontalSlider.setValue(media_pos)
        if not self.mediaplayer.is_playing():
            self.timer.stop()

    def update_time(self):
        """Aktualisiert die Zeit-Anzeige."""
        mtime = QTime(0, 0, 0, 0)
        time_ms = self.mediaplayer.get_time()
        self.time = mtime.addMSecs(time_ms)
        self.timelabel.setText(self.time.toString())

    # =========================================================
    # Screenshot
    # =========================================================

    def take_screenshot(self):
        """Erstellt einen Screenshot des aktuellen Frames."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Screenshot speichern",
            "*.jpg",
        )
        if filename:
            self.mediaplayer.video_take_snapshot(0, filename, 640, 360)

    # =========================================================
    # Fenster schließen
    # =========================================================

    def closeEvent(self, event):
        """Räumt Timer und Player beim Schließen auf."""
        self.timer.stop()
        try:
            self.mediaplayer.stop()
        except Exception:
            pass
        super().closeEvent(event)
