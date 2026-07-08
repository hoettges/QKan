import os
import json
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)
from qgis.utils import iface


class PanoramoPruefer:
    """Prüft für gegebene Attribute (z.B. haltnam), ob jeweils eine passende Datei
    in vordefinierten Verzeichnissen existiert.

    Die in JSON-Dateien hinterlegten Ordner werden erst beim eigentlichen Prüfen
    validiert. Falls ein Pfad nicht existiert, kann der Nutzer einen neuen Ordner
    auswählen; dieser wird anschließend wieder in der JSON-Datei gespeichert.
    """

    def __init__(self, base_path=None, parent=None):
        if base_path is None:
            base_path = os.path.dirname(__file__)

        self.base_path = os.path.abspath(base_path)
        self.parent = parent if parent is not None else iface.mainWindow()

        # JSON-Dateien mit den hinterlegten Suchpfaden
        # Falls nötig an deine tatsächliche Ordnerstruktur anpassen.
        self.panoramo_json_rel = "../datenbankviewer/json/panoramopfad.json"
        self.panoramoSI_json_rel = "../datenbankviewer/json/panoramoSIpfad.json"

        # Werden absichtlich noch NICHT validiert/lazy geladen
        self.panoramo_dirs = None
        self.panoramoSI_dirs = None

    def _json_abs_path(self, relative_json_path):
        return os.path.abspath(os.path.join(self.base_path, relative_json_path))

    def _normalize_dirs_from_json(self, data):
        if isinstance(data, list):
            dirs = data
        elif isinstance(data, dict):
            dirs = list(data.values())
        elif isinstance(data, str):
            dirs = [data]
        else:
            dirs = []

        cleaned = []
        for d in dirs:
            if d is None:
                continue

            d = str(d).strip()
            if not d:
                continue

            if os.path.isabs(d):
                cleaned.append(os.path.abspath(d))
            else:
                cleaned.append(os.path.abspath(os.path.join(self.base_path, d)))

        return list(dict.fromkeys(cleaned))

    def _read_json_dirs(self, relative_json_path):
        json_path = self._json_abs_path(relative_json_path)
        print(f"[PanoramoPruefer] Lese JSON-Datei: {json_path}")

        if not os.path.exists(json_path):
            print(f"[PanoramoPruefer] JSON-Datei nicht gefunden: {json_path}")
            return [], json_path

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Fehler",
                f"Die Konfigurationsdatei konnte nicht gelesen werden:\n"
                f"{json_path}\n\n{type(e).__name__}: {e}",
            )
            print(f"[PanoramoPruefer] Fehler beim Lesen von {json_path}: {e}")
            return [], json_path

        dirs = self._normalize_dirs_from_json(data)
        print(f"[PanoramoPruefer] Gelesene Pfade aus {json_path}: {dirs}")
        return dirs, json_path

    def _write_json_dirs(self, json_path, dirs):
        print(f"[PanoramoPruefer] Schreibe JSON-Datei: {json_path}")
        print(f"[PanoramoPruefer] Zu speichernde Pfade: {dirs}")

        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dirs, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Fehler",
                f"Die Konfigurationsdatei konnte nicht gespeichert werden:\n"
                f"{json_path}\n\n{type(e).__name__}: {e}",
            )
            print(f"[PanoramoPruefer] Fehler beim Schreiben von {json_path}: {e}")
            return False

        return True

    def _ask_for_directory(self, title, start_dir=""):
        if not start_dir or not os.path.isdir(start_dir):
            start_dir = os.path.expanduser("~")

        print(
            f"[PanoramoPruefer] Öffne Verzeichnisdialog: "
            f"title={title}, start_dir={start_dir}"
        )

        directory = QFileDialog.getExistingDirectory(
            self.parent,
            title,
            start_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if directory:
            directory = os.path.abspath(directory)
            print(f"[PanoramoPruefer] Gewähltes Verzeichnis: {directory}")
        else:
            print("[PanoramoPruefer] Kein Verzeichnis gewählt")

        return directory

    def _load_and_validate_dirs(self, relative_json_path, bezeichnung="Pfad"):
        dirs, json_path = self._read_json_dirs(relative_json_path)

        if not dirs:
            print(f"[PanoramoPruefer] Keine Pfade vorhanden für {bezeichnung}")
            antwort = QMessageBox.question(
                self.parent,
                f"{bezeichnung}-Pfad fehlt",
                f"Für {bezeichnung} sind keine gültigen Pfade hinterlegt.\n"
                f"Möchten Sie jetzt einen Ordner auswählen?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if antwort == QMessageBox.Yes:
                new_dir = self._ask_for_directory(f"{bezeichnung}-Ordner auswählen")
                if new_dir:
                    dirs = [new_dir]
                    self._write_json_dirs(json_path, dirs)

            return dirs

        valid_dirs = []
        changed = False

        for d in dirs:
            print(f"[PanoramoPruefer] Prüfe Verzeichnis: {d}")

            if os.path.isdir(d):
                valid_dirs.append(d)
                continue

            changed = True
            antwort = QMessageBox.question(
                self.parent,
                f"{bezeichnung}-Pfad nicht gefunden",
                f"Der hinterlegte Pfad für {bezeichnung} existiert nicht mehr:\n\n"
                f"{d}\n\n"
                f"Möchten Sie einen neuen Ordner auswählen?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if antwort == QMessageBox.Yes:
                start_dir = os.path.dirname(d) if os.path.dirname(d) else os.path.expanduser("~")
                new_dir = self._ask_for_directory(
                    f"Neuen Ordner für {bezeichnung} auswählen",
                    start_dir=start_dir,
                )
                if new_dir and os.path.isdir(new_dir):
                    valid_dirs.append(new_dir)
                else:
                    QMessageBox.warning(
                        self.parent,
                        "Kein gültiger Ordner",
                        f"Für {bezeichnung} wurde kein gültiger Ordner ausgewählt.",
                    )
            else:
                print(
                    f"[PanoramoPruefer] Benutzer hat keinen neuen Pfad für "
                    f"{bezeichnung} gewählt"
                )

        valid_dirs = list(dict.fromkeys(valid_dirs))

        if changed:
            self._write_json_dirs(json_path, valid_dirs)

        print(f"[PanoramoPruefer] Finale gültige Pfade für {bezeichnung}: {valid_dirs}")
        return valid_dirs

    def ensure_valid_dirs(self):
        """Lädt und validiert die in den JSON-Dateien hinterlegten Verzeichnisse.

        Diese Methode wird absichtlich erst beim tatsächlichen Prüfvorgang aufgerufen,
        damit beim Laden der Netzübersicht noch keine Dialoge erscheinen.
        """
        print("[PanoramoPruefer] ensure_valid_dirs() gestartet")

        self.panoramo_dirs = self._load_and_validate_dirs(
            self.panoramo_json_rel,
            bezeichnung="Panoramo",
        )
        self.panoramoSI_dirs = self._load_and_validate_dirs(
            self.panoramoSI_json_rel,
            bezeichnung="PanoramoSI",
        )

        print(f"[PanoramoPruefer] Gültige Panoramo-Pfade: {self.panoramo_dirs}")
        print(f"[PanoramoPruefer] Gültige PanoramoSI-Pfade: {self.panoramoSI_dirs}")

    def check_files_for_names(self, names, extension=".ipf"):
        """Prüft, ob für die übergebenen Namen Dateien in den konfigurierten
        Panoramo- und PanoramoSI-Ordnern existieren.
        """
        self.ensure_valid_dirs()

        results = {}

        print(f"[PanoramoPruefer] Starte Dateiprüfung für {len(names)} Namen")
        print(f"[PanoramoPruefer] Panoramo-Verzeichnisse: {self.panoramo_dirs}")
        print(f"[PanoramoPruefer] PanoramoSI-Verzeichnisse: {self.panoramoSI_dirs}")

        for name in names:
            filename = f"{name}{extension}"
            found_in_panoramo = []
            found_in_panoramoSI = []

            for d in (self.panoramo_dirs or []):
                file_path = os.path.join(d, filename)
                if os.path.isfile(file_path):
                    found_in_panoramo.append(file_path)

            for d in (self.panoramoSI_dirs or []):
                file_path = os.path.join(d, filename)
                if os.path.isfile(file_path):
                    found_in_panoramoSI.append(file_path)

            results[name] = {
                "exists_panoramo": bool(found_in_panoramo),
                "exists_panoramoSI": bool(found_in_panoramoSI),
                "paths_panoramo": found_in_panoramo,
                "paths_panoramoSI": found_in_panoramoSI,
            }

        return results


class FehlendeDateienDialog(QDialog):
    def __init__(self, fehlende_dateien, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fehlende Dateien")

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(f"Anzahl fehlender Dateien: {len(fehlende_dateien)}")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.addItems(fehlende_dateien)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        copy_button = QPushButton("Kopieren")
        copy_button.clicked.connect(self.kopiere_in_zwischenablage)
        button_layout.addWidget(copy_button)

        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        self.resize(400, 300)

    def kopiere_in_zwischenablage(self):
        texte = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        gesamter_text = "\n".join(texte)

        clipboard = QApplication.clipboard()
        clipboard.setText(gesamter_text)

        msg = QMessageBox(self)
        msg.setWindowTitle("Kopieren")
        msg.setText("Die fehlenden Dateinamen wurden in die Zwischenablage kopiert.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()