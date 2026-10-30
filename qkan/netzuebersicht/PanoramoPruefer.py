import os
import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QSizePolicy, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt, QSettings
from qgis.utils import iface

class PanoramoPruefer:
    """Sammelprüfung auf <haltnam>.ipf, unabhängig vom Datenbankviewer.

    Die Ordner werden pro QGIS-Nutzer in QSettings gespeichert, nicht im
    installierten QKan-Plugin und nicht als lokale Pfade im Repository.
    """
    def __init__(self, base_path=None):
        self.settings = QSettings()
        self.panoramo_dirs = self._gespeicherte_ordner("Panoramo")
        self.panoramoSI_dirs = self._gespeicherte_ordner("PanoramoSI")

    def _gespeicherte_ordner(self, typ):
        value = self.settings.value(f"QKan/Netzuebersicht/{typ}Ordner", [])
        if isinstance(value, str):
            value = [value] if value else []
        return [os.path.abspath(str(d)) for d in (value or []) if str(d).strip()]

    def _gueltige_ordner(self, typ, bisher, parent):
        gueltig = [d for d in bisher if os.path.isdir(d)]
        if not gueltig:
            directory = QFileDialog.getExistingDirectory(
                parent, f"{typ}-Ordner für die Dateiprüfung auswählen"
            )
            if not directory:
                return None
            gueltig = [os.path.abspath(directory)]
        self.settings.setValue(f"QKan/Netzuebersicht/{typ}Ordner", gueltig)
        return gueltig

    def check_files_for_names(self, names, extension=".ipf", parent=None):
        self.panoramo_dirs = self._gueltige_ordner(
            "Panoramo", self.panoramo_dirs, parent
        )
        if self.panoramo_dirs is None:
            return None
        self.panoramoSI_dirs = self._gueltige_ordner(
            "PanoramoSI", self.panoramoSI_dirs, parent
        )
        if self.panoramoSI_dirs is None:
            return None

        results = {}
        for name in names:
            filename = f"{name}{extension}"
            found_in_panoramo = [
                os.path.join(d, filename)
                for d in self.panoramo_dirs
                if os.path.isfile(os.path.join(d, filename))
            ]
            found_in_panoramoSI = [
                os.path.join(d, filename)
                for d in self.panoramoSI_dirs
                if os.path.isfile(os.path.join(d, filename))
            ]
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

        # Button-Leiste mit "Kopieren" und "Schließen"
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
        from PyQt5.QtWidgets import QApplication, QMessageBox

        texte = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        gesamter_text = "\n".join(texte)

        clipboard = QApplication.clipboard()
        clipboard.setText(gesamter_text)

        msg = QMessageBox(self)
        msg.setWindowTitle("Kopieren")
        msg.setText("Die fehlenden Dateinamen wurden in die Zwischenablage kopiert.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
