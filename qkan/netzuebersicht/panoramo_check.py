# netzuebersicht/panoramo_check.py
from PyQt5.QtWidgets import QMessageBox
from qgis.utils import iface
from .PanoramoPruefer import FehlendeDateienDialog


def zeige_datei_pruefung(self):
    layer = iface.activeLayer()
    if layer is None or "haltnam" not in layer.fields().names():
        QMessageBox.information(self, "Panoramo-Prüfung", "Bitte einen Haltungen-Layer auswählen.")
        return
    selected_features = layer.selectedFeatures()
    haltnam_liste = [f["haltnam"] for f in selected_features if f["haltnam"]]

    if not haltnam_liste:
        QMessageBox.information(
            self, "Info", "Keine Objekte mit 'haltnam' ausgewählt."
        )
        return

    result = self.panoramo_pruefer.check_files_for_names(haltnam_liste, parent=self)
    if result is None:
        return

    anzahl_selektiert = len(haltnam_liste)

    vorhanden_panoramo = [
        name for name, v in result.items() if v["exists_panoramo"]
    ]
    vorhanden_panoramoSI = [
        name for name, v in result.items() if v["exists_panoramoSI"]
    ]
    fehlend_panoramo = [
        name for name, v in result.items() if not v["exists_panoramo"]
    ]
    fehlend_panoramoSI = [
        name for name, v in result.items() if not v["exists_panoramoSI"]
    ]

    text = (
        f"Anzahl selektierter Objekte: {anzahl_selektiert}\n"
        f"Anzahl vorhandener Panoramo-Dateien: {len(vorhanden_panoramo)}\n"
        f"Anzahl vorhandener PanoramoSI-Dateien: {len(vorhanden_panoramoSI)}"
    )
    QMessageBox.information(self, "Dateiprüfung Ergebnis", text)

    if fehlend_panoramo:
        dlg1 = FehlendeDateienDialog(fehlend_panoramo, self)
        dlg1.setWindowTitle("Fehlende Panoramo-Dateien")
        dlg1.exec_()
    if fehlend_panoramoSI:
        dlg2 = FehlendeDateienDialog(fehlend_panoramoSI, self)
        dlg2.setWindowTitle("Fehlende PanoramoSI-Dateien")
        dlg2.exec_()
