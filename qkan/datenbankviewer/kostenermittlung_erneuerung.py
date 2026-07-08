"""
cost_calculation.py - Kostenermittlung für Erneuerungen im QGIS-Plugin Datenbankviewer
Modularisierte Version der Kostenermittlung_Erneuerung.
"""

# =========================================================
# Importe
# =========================================================

import os
import json

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt

from qgis.core import QgsProject, QgsFeatureRequest

from .erneuerung_price_editor import ErneuerungPriceEditor


# =========================================================
# UI laden
# =========================================================

FORM_CLASS_Erneuerungstool, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "Kostenermittlung_Erneuerung.ui")
)


# =========================================================
# Hauptklasse
# =========================================================

class Kostenermittlung_Erneuerung(QDialog, FORM_CLASS_Erneuerungstool):
    """Dialog zur Berechnung von Erneuerungskosten (Aushub, Material, Schichten)."""

    PARAMS = {}

    def __init__(self, parent=None, dimension="", laenge="", anzahl_stutzen=""):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModal)

        self._load_params()

        # Setze den übergebenen Wert im Zielfeld
        self.Durchmesser.setText(dimension)
        self.Laenge.setText(laenge)
        self.Anzahl_Anschluesse.setText(anzahl_stutzen)
        self.berechne_mittlere_tiefe()
        self.Anzahl_Schaechte.setText("2")

        schachtdurchmesser = ["600", "800", "1000", "1200", "1500", "2000"]
        schachtmaterial = ["Beton", "PP", "PE-HD", "GFK"]
        materialien = ["Beton", "PP", "PE-HD", "Steinzeug"]

        self.comboBox_material.addItems(materialien)
        self.comboBox_schachtdurchmesser.addItems(schachtdurchmesser)
        self.comboBox_schachtmaterial.addItems(schachtmaterial)
        self._init_aufbau_combobox()

        self.berechne_mindestgrabenbreite()
        self.Berechnung.clicked.connect(self.alle_Berechnungen)
        self.einstellungen_erneuerung.clicked.connect(self.einstellungen_oeffnen)

        # Verbinde Aufbau-Änderungen mit Berechnung
        self.comboBox_aufbau.currentTextChanged.connect(self.alle_Berechnungen)
        self.comboBox_aufbau.currentTextChanged.connect(self.alle_Berechnungen)
        self.comboBox_material.currentTextChanged.connect(self.alle_Berechnungen)
        self.berechne_schichten()

        # Verbinde alle relevanten Felder mit der Aushubberechnung
        felder = [
            self.Laenge,
            self.Durchmesser,
            self.Mindestgrabenbreite,
            self.mittlere_Tiefe,
            self.Tragausgleichsschicht,
            self.Fahrbahnbreite,
            self.Gehwegbreite,
            self.Anschlusslaenge,
            self.Anzahl_Schaechte,
        ]
        for feld in felder:
            feld.textChanged.connect(self.alle_Berechnungen)

        self.Berechnung.clicked.connect(self.alle_Berechnungen)
        self.alle_Berechnungen()

    # =========================================================
    # Pfade zu lokalen JSON-Dateien
    # =========================================================

    def _json_dir(self):
        """Gibt den lokalen json-Unterordner relativ zu dieser Datei zurück."""
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(tool_dir, "json")

    def _params_path(self):
        """Pfad zur Datei erneuerung_parametrierung.json."""
        return os.path.join(self._json_dir(), "erneuerung_parametrierung.json")

    def _preise_path(self):
        """Pfad zur Datei preisliste_erneuerung.json."""
        return os.path.join(self._json_dir(), "preisliste_erneuerung.json")

    # =========================================================
    # Laden der Parametrierung
    # =========================================================

    def _load_params(self):
        """Lädt Erneuerungs-Parametrierung aus lokaler JSON-Datei."""
        path = self._params_path()
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.PARAMS = json.load(f)
        except FileNotFoundError:
            self.PARAMS = {
                "AUSSENDURCHMESSER": {},
                "AUFBAUVARIANTEN": {},
            }
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Die Datei 'erneuerung_parametrierung.json' enthält ungültiges JSON:\n"
                f"{path}\n\nFehler: {e}\n"
                f"Es wird eine leere Parametrierung verwendet.",
            )
            self.PARAMS = {
                "AUSSENDURCHMESSER": {},
                "AUFBAUVARIANTEN": {},
            }
        except Exception as e:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Fehler beim Laden der Erneuerungs-Parametrierung:\n"
                f"{path}\n\n{e}\n"
                f"Es wird eine leere Parametrierung verwendet.",
            )
            self.PARAMS = {
                "AUSSENDURCHMESSER": {},
                "AUFBAUVARIANTEN": {},
            }

    @property
    def AUSSENDURCHMESSER(self):
        return self.PARAMS.get("AUSSENDURCHMESSER", {})

    @property
    def AUFBAUVARIANTEN(self):
        return self.PARAMS.get("AUFBAUVARIANTEN", {})

    # =========================================================
    # Einstellungen / Editor
    # =========================================================

    def einstellungen_oeffnen(self):
        dlg = ErneuerungPriceEditor(self)
        if dlg.exec():
            # Preise geändert → Parameter neu laden und Kosten neu berechnen
            self._load_params()
            self._init_aufbau_combobox()
            self.berechne_kosten()

    # =========================================================
    # Gesamtberechnung
    # =========================================================

    def alle_Berechnungen(self):
        self.berechne_aushub()
        self.berechne_leitungszone()
        self.berechne_fuellkies()
        self.berechne_kosten()
        self.berechne_schichten()
        self.berechne_mindestgrabenbreite()

    # =========================================================
    # Aufbauvarianten
    # =========================================================

    def _init_aufbau_combobox(self):
        self.comboBox_aufbau.clear()

        for belastungsklasse, data in self.AUFBAUVARIANTEN.items():
            for variant_key, variante in data.get("varianten", {}).items():
                display_text = (
                    f"{data.get('name', belastungsklasse)} - "
                    f"{variante.get('name', variant_key)}"
                )
                self.comboBox_aufbau.addItem(
                    display_text,
                    userData=variante.get("schichten", {}),
                )

        self.comboBox_aufbau.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.comboBox_aufbau.setMaxVisibleItems(10)

        if self.comboBox_aufbau.count() == 0:
            return

        view = self.comboBox_aufbau.view()
        fm = self.comboBox_aufbau.fontMetrics()
        texts = [
            self.comboBox_aufbau.itemText(i)
            for i in range(self.comboBox_aufbau.count())
        ]
        max_width = max(fm.width(t) for t in texts if t)

        view.setMinimumWidth(max_width + 100)

    # =========================================================
    # Füllkies
    # =========================================================

    def berechne_fuellkies(self):
        """Berechnet Füllkies-Volumen mit korrekter Schachtberücksichtigung."""
        try:
            mittlere_tiefe = (
                float(self.mittlere_Tiefe.text().replace(",", "."))
                if self.mittlere_Tiefe.text()
                else 0.0
            )
            laenge = (
                float(self.Laenge.text().replace(",", "."))
                if self.Laenge.text()
                else 0.0
            )
            breite = (
                float(self.Mindestgrabenbreite.text().replace(",", "."))
                if self.Mindestgrabenbreite.text()
                else 0.0
            )

            material = self.comboBox_material.currentText()
            dim_text = (
                self.Durchmesser.text().replace(",", ".")
                if self.Durchmesser.text()
                else "0"
            )
            try:
                dim_key = str(int(dim_text))
            except ValueError:
                dim_key = "0"

            od = self.AUSSENDURCHMESSER.get(material, {}).get(dim_key, 0) / 1000

            schichten = self.comboBox_aufbau.currentData() or {}
            schichtdicken = sum(schichten.values())

            leitungszone_hoehe = 0.15 + 0.3 + od
            fuellkies_hoehe = mittlere_tiefe + 0.15 - leitungszone_hoehe - schichtdicken
            fuellkies_hoehe = max(fuellkies_hoehe, 0)

            graben_volumen = laenge * breite * fuellkies_hoehe

            schacht_gesamt_volumen = 0.0
            if self.checkBox_Schachterneuerung.isChecked():
                anzahl = int(self.Anzahl_Schaechte.text()) if self.Anzahl_Schaechte.text() else 0
                durchmesser_mm = float(
                    self.comboBox_schachtdurchmesser.currentText().replace(",", ".")
                )
                d = durchmesser_mm / 1000

                schachtgraben_volumen = (d + 0.6) ** 2 * (
                    fuellkies_hoehe + leitungszone_hoehe
                ) * anzahl
                schachtkoerper_volumen = d ** 2 * (
                    fuellkies_hoehe + leitungszone_hoehe
                ) * anzahl

                schacht_gesamt_volumen = schachtgraben_volumen - schachtkoerper_volumen

            gesamt_volumen = graben_volumen + schacht_gesamt_volumen
            self.Fuellkies.setText(f"{max(gesamt_volumen, 0):.3f}".replace(".", ","))

        except Exception as e:
            print(f"Fehler bei Füllkiesberechnung: {str(e)}")
            self.Fuellkies.clear()

    # =========================================================
    # Aushub
    # =========================================================

    def berechne_aushub(self):
        try:
            laenge = float(self.Laenge.text().replace(",", ".")) if self.Laenge.text() else 0.0
            breite = (
                float(self.Mindestgrabenbreite.text().replace(",", "."))
                if self.Mindestgrabenbreite.text()
                else 0.0
            )
            tiefe = (
                float(self.mittlere_Tiefe.text().replace(",", "."))
                if self.mittlere_Tiefe.text()
                else 0.0
            )

            tragausgleich_str = self.Tragausgleichsschicht.text().strip()
            tragausgleich = (
                float(tragausgleich_str.replace(",", "."))
                if tragausgleich_str
                else 0.0
            )

            aushub_volumen_kanalgraben = laenge * breite * (tiefe + tragausgleich)

            aushub_volumen_strasse = 0.0
            if self.checkBox_Fahrbahn.isChecked():
                if self.Fahrbahnbreite.text():
                    breite_fahrbahn = float(
                        self.Fahrbahnbreite.text().replace(",", ".")
                    ) - breite
                    if breite_fahrbahn > 0:
                        schichten = self.comboBox_aufbau.currentData() or {}
                        schichtdicke_gesamt = sum(schichten.values())
                        aushub_volumen_strasse = (
                            laenge * breite_fahrbahn * schichtdicke_gesamt
                        )

            aushub_volumen_schacht = 0.0
            if self.checkBox_Schachterneuerung.isChecked():
                anzahl = int(self.Anzahl_Schaechte.text()) if self.Anzahl_Schaechte.text() else 0
                durchmesser_mm = float(
                    self.comboBox_schachtdurchmesser.currentText().replace(",", ".")
                )
                durchmesser = durchmesser_mm / 1000

                schacht_volumen = (durchmesser + 0.6) ** 2 * (tiefe + tragausgleich)
                aushub_volumen_schacht = schacht_volumen * anzahl
                print(aushub_volumen_schacht)

            aushub_volumen = (
                aushub_volumen_kanalgraben
                + aushub_volumen_strasse
                + aushub_volumen_schacht
            )

            print(aushub_volumen)
            self.Aushub.setText(f"{aushub_volumen:.3f}".replace(".", ","))

        except ValueError as e:
            print("Fehler bei der Umrechnung:", e)
            self.Aushub.clear()
        except Exception as e:
            print("Unbekannter Fehler:", e)
            self.Aushub.clear()

    # =========================================================
    # Schichten
    # =========================================================

    def berechne_schichten(self):
        """Berechnet Schichtvolumen mit Flächenabzug für Schächte in Graben und Fahrbahn."""
        try:
            laenge = float(self.Laenge.text().replace(",", ".")) if self.Laenge.text() else 0.0
            breite_graben = (
                float(self.Mindestgrabenbreite.text().replace(",", "."))
                if self.Mindestgrabenbreite.text()
                else 0.0
            )
            schichten = self.comboBox_aufbau.currentData() or {}

            schacht_flaeche = 0.0
            if self.checkBox_Schachterneuerung.isChecked():
                anzahl = int(self.Anzahl_Schaechte.text()) if self.Anzahl_Schaechte.text() else 0
                durchmesser_mm = float(
                    self.comboBox_schachtdurchmesser.currentText().replace(",", ".")
                )
                durchmesser = durchmesser_mm / 1000
                schacht_flaeche = (durchmesser + 0.6) ** 2 * anzahl

            breite_fahrbahn = 0.0
            if self.checkBox_Fahrbahn.isChecked() and self.Fahrbahnbreite.text():
                breite_fahrbahn = float(self.Fahrbahnbreite.text().replace(",", ".")) - breite_graben
                breite_fahrbahn = max(breite_fahrbahn, 0.0)

            graben_flaeche = laenge * breite_graben
            fahrbahn_flaeche = laenge * breite_fahrbahn

            korrigierte_graben_flaeche = max(graben_flaeche, 0)
            korrigierte_fahrbahn_flaeche = max(fahrbahn_flaeche - schacht_flaeche, 0)

            for feld in [
                self.Frostschutzschicht,
                self.Schottertragschicht,
                self.Asphalttragschicht,
                self.Asphaltbinderschicht,
                self.Asphaltdeckschicht,
            ]:
                feld.clear()

            for schichtname, dicke in schichten.items():
                volumen_graben = korrigierte_graben_flaeche * dicke
                volumen_fahrbahn = korrigierte_fahrbahn_flaeche * dicke
                volumen_schacht = schacht_flaeche * dicke

                gesamtvolumen = volumen_graben + volumen_fahrbahn + volumen_schacht

                volumen_str = f"{gesamtvolumen:.3f}".replace(".", ",")
                feld = getattr(self, schichtname, None)
                if feld:
                    feld.setText(volumen_str)

        except Exception as e:
            print(f"Fehler bei Schichtberechnung: {str(e)}")
            for feld in [
                self.Frostschutzschicht,
                self.Schottertragschicht,
                self.Asphalttragschicht,
                self.Asphaltbinderschicht,
                self.Asphaltdeckschicht,
            ]:
                feld.clear()

    # =========================================================
    # Mindestgrabenbreite
    # =========================================================

    def berechne_mindestgrabenbreite(self):
        """Berechnet die Mindestgrabenbreite nach DIN 1610."""
        try:
            material = self.comboBox_material.currentText()
            dim_text = self.Durchmesser.text().replace(",", ".")
            try:
                dim_key = str(int(dim_text))
            except ValueError:
                dim_key = "0"

            od = self.AUSSENDURCHMESSER.get(material, {}).get(dim_key, 0) / 1000

            t = float(self.mittlere_Tiefe.text().replace(",", "."))

            if t < 1.0:
                breite_tiefe = 0.0
            elif 1.0 <= t <= 1.75:
                breite_tiefe = 0.8
            elif 1.75 < t <= 4.0:
                breite_tiefe = 0.9
            else:
                breite_tiefe = 1.0

            if od <= 0.225:
                breite_od = od + 0.4
            elif 0.225 < od <= 0.35:
                breite_od = od + 0.5
            elif 0.35 < od <= 0.7:
                breite_od = od + 0.7
            elif 0.7 < od <= 1.2:
                breite_od = od + 0.85
            else:
                breite_od = od + 1.0

            mindestbreite = max(breite_tiefe, breite_od) + 0.2
            self.Mindestgrabenbreite.setText(f"{mindestbreite:.2f}")

        except Exception as e:
            print(f"Fehler bei Breitenberechnung: {str(e)}")
            self.Mindestgrabenbreite.clear()

    # =========================================================
    # Leitungszone
    # =========================================================

    def berechne_leitungszone(self):
        try:
            laenge = float(self.Laenge.text().replace(",", ".")) if self.Laenge.text() else 0.0
            breite = (
                float(self.Mindestgrabenbreite.text().replace(",", "."))
                if self.Mindestgrabenbreite.text()
                else 0.0
            )

            material = self.comboBox_material.currentText()
            try:
                dim_key = (
                    str(int(self.Durchmesser.text().replace(",", ".")))
                    if self.Durchmesser.text()
                    else "0"
                )
            except ValueError:
                dim_key = "0"

            aussendurchmesser = self.AUSSENDURCHMESSER.get(material, {}).get(dim_key, 0) / 1000

            leitungszone_volumen = (0.15 + 0.3 + aussendurchmesser) * laenge * breite
            self.Leitungszone.setText(f"{leitungszone_volumen:.3f}".replace(".", ","))

        except Exception as e:
            print("Fehler bei der Berechnung der Leitungszone:", e)
            self.Leitungszone.clear()

    # =========================================================
    # Kosten
    # =========================================================

    def berechne_kosten(self):
        """Berechnet die Kosten auf Basis der lokalen Preisliste."""
        json_file_path = self._preise_path()

        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                preise = json.load(f)
        except FileNotFoundError as e:
            print("Fehler beim Laden der Preisliste (Datei fehlt):", e)
            self.Kosten_netto.setText("")
            self.Kosten_brutto.setText("")
            return
        except json.JSONDecodeError as e:
            print("Fehler beim Laden der Preisliste (ungültiges JSON):", e)
            self.Kosten_netto.setText("")
            self.Kosten_brutto.setText("")
            return
        except Exception as e:
            print("Fehler beim Laden der Preisliste:", e)
            self.Kosten_netto.setText("")
            self.Kosten_brutto.setText("")
            return

        try:
            laenge = float(self.Laenge.text().replace(",", ".")) if self.Laenge.text() else 0.0
            material = self.comboBox_material.currentText()

            try:
                dim_key = str(int(self.Durchmesser.text().replace(",", ".")))
            except (ValueError, AttributeError):
                dim_key = "0"

            rohr_preis = 0
            try:
                rohr_preis = preise["Rohr"][material][dim_key]
            except KeyError:
                pass

            verbau = laenge * 2
            rohr_kosten = laenge * rohr_preis
            schnitt = laenge * 2

            aushub = float(self.Aushub.text().replace(",", ".")) if self.Aushub.text() else 0.0
            frostschutz = (
                float(self.Frostschutzschicht.text().replace(",", "."))
                if self.Frostschutzschicht.text()
                else 0.0
            )
            schotter = (
                float(self.Schottertragschicht.text().replace(",", "."))
                if self.Schottertragschicht.text()
                else 0.0
            )
            asphalt_trag = (
                float(self.Asphalttragschicht.text().replace(",", "."))
                if self.Asphalttragschicht.text()
                else 0.0
            )
            asphalt_binder = (
                float(self.Asphaltbinderschicht.text().replace(",", "."))
                if self.Asphaltbinderschicht.text()
                else 0.0
            )
            asphalt_deck = (
                float(self.Asphaltdeckschicht.text().replace(",", "."))
                if self.Asphaltdeckschicht.text()
                else 0.0
            )
            leitungszone = (
                float(self.Leitungszone.text().replace(",", "."))
                if self.Leitungszone.text()
                else 0.0
            )
            fuellkies = (
                float(self.Fuellkies.text().replace(",", "."))
                if self.Fuellkies.text()
                else 0.0
            )
            tragausgleich = (
                float(self.Tragausgleichsschicht.text().replace(",", "."))
                if self.Tragausgleichsschicht.text()
                else 0.0
            )

            kosten = (
                aushub * preise.get("Aushub", 0)
                + frostschutz * preise.get("Frostschutzschicht", 0)
                + schotter * preise.get("Schottertragschicht", 0)
                + asphalt_trag * preise.get("Asphalttragschicht", 0)
                + asphalt_binder * preise.get("Asphaltbinderschicht", 0)
                + asphalt_deck * preise.get("Asphaltdeckschicht", 0)
                + leitungszone * preise.get("Leitungszone", 0)
                + fuellkies * preise.get("Fuellkies", 0)
                + tragausgleich * preise.get("Tragausgleichsschicht", 0)
                + rohr_kosten
                + verbau * preise.get("Verbau", 0)
                + schnitt * preise.get("Schnitt", 0)
            )

            self.Kosten_netto.setText(f"{kosten:.2f} €".replace(".", ","))
            self.Kosten_brutto.setText(f"{kosten * 1.19:.2f} €".replace(".", ","))

        except Exception as e:
            print("Fehler in der Kostenberechnung:", e)
            self.Kosten_netto.setText("")
            self.Kosten_brutto.setText("")

    # =========================================================
    # Mittlere Tiefe
    # =========================================================

    def berechne_mittlere_tiefe(self):
        haltungen_layer = QgsProject.instance().mapLayersByName("Haltungen")[0]
        schaechte_layer = QgsProject.instance().mapLayersByName("Schächte")[0]

        if not haltungen_layer or not schaechte_layer:
            QMessageBox.warning(self, "Fehler", "Layer nicht gefunden!")
            return

        selected_haltungen = haltungen_layer.selectedFeatures()

        if not selected_haltungen:
            return

        for haltung in selected_haltungen:
            try:
                schoben_id = haltung["schoben"]
                schunten_id = haltung["schunten"]
                print(schoben_id)

                schoben_schacht = next(
                    schaechte_layer.getFeatures(
                        QgsFeatureRequest().setFilterExpression(f"schnam = '{schoben_id}'")
                    )
                )
                schunten_schacht = next(
                    schaechte_layer.getFeatures(
                        QgsFeatureRequest().setFilterExpression(f"schnam = '{schunten_id}'")
                    )
                )

                tiefe_schoben = schoben_schacht["deckelhoehe"] - schoben_schacht["sohlhoehe"]
                tiefe_schunten = schunten_schacht["deckelhoehe"] - schunten_schacht["sohlhoehe"]

                mittlere_tiefe = (tiefe_schoben + tiefe_schunten) / 2
                self.mittlere_Tiefe.setText(f"{mittlere_tiefe:.2f}")

            except StopIteration:
                QMessageBox.warning(self, "Fehler", "Schacht nicht gefunden!")
            except KeyError:
                QMessageBox.warning(self, "Fehler", "Feldname nicht vorhanden!")