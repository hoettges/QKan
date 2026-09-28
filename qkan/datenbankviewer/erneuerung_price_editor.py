# erneuerung_price_editor.py

import json
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QWidget, QSizePolicy, QTabWidget
)
from PyQt6.QtCore import Qt


class ErneuerungPriceEditor(QDialog):
    """
    Dialog zur Verwaltung der Einheitspreise und Rohrpreise
    aus preisliste_erneuerung.json.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preise Erneuerung verwalten")
        self.resize(700, 500)

        # Basisverzeichnis dieses Moduls
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        json_dir = os.path.join(tool_dir, "json")

        # JSON-Dateien im lokalen json-Unterordner
        self.json_file_path = os.path.join(json_dir, "preisliste_erneuerung.json")
        self.params_file_path = os.path.join(json_dir, "erneuerung_parametrierung.json")

        self.params = {}

        self.data = {}
        self._load_json()
        self._load_params()
        self._build_ui()
        self._fill_unit_prices()
        self._fill_rohr_table()

    # ---------------- JSON I/O ----------------

    def _load_json(self):
        # Robust laden, ggf. Dummy-Struktur anlegen
        if not os.path.exists(self.json_file_path):
            self.data = {
                "Aushub": 0.0,
                "Frostschutzschicht": 0.0,
                "Schottertragschicht": 0.0,
                "Asphalttragschicht": 0.0,
                "Asphaltbinderschicht": 0.0,
                "Asphaltdeckschicht": 0.0,
                "Leitungszone": 0.0,
                "Tragausgleichsschicht": 0.0,
                "Fuellkies": 0.0,
                "Schnitt": 0.0,
                "Verbau": 0.0,
                "Rohr": {}
            }
            return

        try:
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Preisliste:\n{e}")
            self.data = {
                "Aushub": 0.0,
                "Frostschutzschicht": 0.0,
                "Schottertragschicht": 0.0,
                "Asphalttragschicht": 0.0,
                "Asphaltbinderschicht": 0.0,
                "Asphaltdeckschicht": 0.0,
                "Leitungszone": 0.0,
                "Tragausgleichsschicht": 0.0,
                "Fuellkies": 0.0,
                "Schnitt": 0.0,
                "Verbau": 0.0,
                "Rohr": {}
            }

    def _save_json(self):
        try:
            # Verzeichnis sicherstellen
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Gespeichert", "Preisliste Erneuerung wurde gespeichert.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Preisliste:\n{e}")

    def _load_params(self):
        if not os.path.exists(self.params_file_path):
            self.params = {
                "AUSSENDURCHMESSER": {},
                "AUFBAUVARIANTEN": {}
            }
            return
        try:
            with open(self.params_file_path, "r", encoding="utf-8") as f:
                self.params = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Erneuerungs-Parametrierung:\n{e}")
            self.params = {
                "AUSSENDURCHMESSER": {},
                "AUFBAUVARIANTEN": {}
            }

    def _save_params(self):
        try:
            os.makedirs(os.path.dirname(self.params_file_path), exist_ok=True)
            with open(self.params_file_path, "w", encoding="utf-8") as f:
                json.dump(self.params, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Erneuerungs-Parametrierung:\n{e}")


    # ---------------- UI Aufbau ----------------

    def _build_ui(self):
        from PyQt6.QtWidgets import QTabWidget

        main_layout = QVBoxLayout(self)

        # Tab-Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ---------------- Tab 1: Preise & Rohrparameter ----------------
        tab_preise = QWidget()
        layout_preise = QVBoxLayout(tab_preise)

        # --- Abschnitt 1: einfache Einheitspreise (Aushub, Schichten, etc.) ---
        unit_box = QWidget(tab_preise)
        unit_layout = QVBoxLayout(unit_box)
        unit_layout.setContentsMargins(0, 0, 0, 0)

        unit_layout.addWidget(QLabel("Allgemeine Einheitspreise (€/m³ oder €/m bzw. wie definiert):"))

        self.unit_fields = {}  # key -> QLineEdit

        unit_keys = [
            "Aushub",
            "Frostschutzschicht",
            "Schottertragschicht",
            "Asphalttragschicht",
            "Asphaltbinderschicht",
            "Asphaltdeckschicht",
            "Leitungszone",
            "Tragausgleichsschicht",
            "Fuellkies",
            "Verbau",
            "Schnitt",
        ]

        row_container = QWidget(tab_preise)
        row_layout = QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)

        left_col = QVBoxLayout()
        right_col = QVBoxLayout()

        half = (len(unit_keys) + 1) // 2
        left_keys = unit_keys[:half]
        right_keys = unit_keys[half:]

        for key in left_keys:
            h = QHBoxLayout()
            lbl = QLabel(key + ":")
            edit = QLineEdit()
            edit.setPlaceholderText("Preis")
            edit.setMaximumWidth(150)
            h.addWidget(lbl)
            h.addWidget(edit)
            h.addStretch(1)
            left_col.addLayout(h)
            self.unit_fields[key] = edit

        for key in right_keys:
            h = QHBoxLayout()
            lbl = QLabel(key + ":")
            edit = QLineEdit()
            edit.setPlaceholderText("Preis")
            edit.setMaximumWidth(150)
            h.addWidget(lbl)
            h.addWidget(edit)
            h.addStretch(1)
            right_col.addLayout(h)
            self.unit_fields[key] = edit

        row_layout.addLayout(left_col)
        row_layout.addLayout(right_col)
        unit_layout.addWidget(row_container)

        layout_preise.addWidget(unit_box)

        # --- Abschnitt 2: Rohrparameter (Preis + Außendurchmesser) ---
        layout_preise.addWidget(QLabel(""))
        layout_preise.addWidget(QLabel("Rohrparameter: Preis (€/m) und Außendurchmesser (mm) nach Material und Dimension:"))

        rohr_top_row = QHBoxLayout()
        rohr_top_row.addWidget(QLabel("Material:"))

        self.combo_material = QComboBox()
        self.combo_material.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        rohr_top_row.addWidget(self.combo_material)

        self.btn_new_material = QPushButton("Material hinzufügen")
        self.btn_delete_material = QPushButton("Material löschen")
        rohr_top_row.addWidget(self.btn_new_material)
        rohr_top_row.addWidget(self.btn_delete_material)
        rohr_top_row.addStretch(1)

        layout_preise.addLayout(rohr_top_row)

        self.table_rohr = QTableWidget()
        self.table_rohr.setColumnCount(3)
        self.table_rohr.setHorizontalHeaderLabels(["Dimension (mm)", "Preis (€/m)", "Außendurchmesser (mm)"])
        self.table_rohr.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_rohr.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_rohr.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_rohr.verticalHeader().setVisible(False)
        self.table_rohr.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_rohr.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)

        layout_preise.addWidget(self.table_rohr)

        btn_row = QHBoxLayout()
        self.btn_add_row = QPushButton("Dimension hinzufügen")
        self.btn_delete_row = QPushButton("Ausgewählte Dimension löschen")
        btn_row.addWidget(self.btn_add_row)
        btn_row.addWidget(self.btn_delete_row)
        btn_row.addStretch(1)
        layout_preise.addLayout(btn_row)

        self.tabs.addTab(tab_preise, "Preise")

        # ---------------- Tab 2: Aufbauvarianten ----------------
        tab_aufbau = QWidget()
        layout_aufbau = QVBoxLayout(tab_aufbau)

        layout_aufbau.addWidget(QLabel("Aufbauvarianten (Belastungsklasse, Variante, Schichten):"))

        self.table_aufbau = QTableWidget()
        self.table_aufbau.setColumnCount(5)
        self.table_aufbau.setHorizontalHeaderLabels(
            ["Belastungsklasse", "Variantenschlüssel", "Variantenname", "Schichtname", "Dicke (m)"]
        )
        self.table_aufbau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_aufbau.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_aufbau.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_aufbau.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_aufbau.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_aufbau.verticalHeader().setVisible(False)
        self.table_aufbau.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_aufbau.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)

        layout_aufbau.addWidget(self.table_aufbau)

        aufbau_btn_row = QHBoxLayout()
        self.btn_aufbau_add = QPushButton("Aufbauzeile hinzufügen")
        self.btn_aufbau_del = QPushButton("Ausgewählte Zeile löschen")
        aufbau_btn_row.addWidget(self.btn_aufbau_add)
        aufbau_btn_row.addWidget(self.btn_aufbau_del)
        aufbau_btn_row.addStretch(1)
        layout_aufbau.addLayout(aufbau_btn_row)

        self.tabs.addTab(tab_aufbau, "Aufbau")

        # ---------------- OK / Abbrechen ----------------
        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        self.btn_save = QPushButton("Speichern")
        self.btn_cancel = QPushButton("Abbrechen")
        bottom_row.addWidget(self.btn_save)
        bottom_row.addWidget(self.btn_cancel)
        main_layout.addLayout(bottom_row)

        # ---------------- Signals ----------------
        # Rohr
        self.combo_material.currentTextChanged.connect(self._fill_rohr_table)
        self.btn_add_row.clicked.connect(self._add_rohr_row)
        self.btn_delete_row.clicked.connect(self._delete_rohr_row)
        self.btn_new_material.clicked.connect(self._add_material)
        self.btn_delete_material.clicked.connect(self._delete_material)

        # Aufbau
        self.btn_aufbau_add.clicked.connect(self._add_aufbau_row)
        self.btn_aufbau_del.clicked.connect(self._delete_aufbau_row)

        # Save / Cancel
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject)

        # Initial füllen
        self._fill_aufbau_table()


    # ---------------- Unit-Preis-Logik ----------------

    def _fill_unit_prices(self):
        for key, edit in self.unit_fields.items():
            value = self.data.get(key, 0.0)
            try:
                edit.setText(f"{float(value):.2f}".replace('.', ','))
            except Exception:
                edit.setText("")

    def _collect_unit_prices(self):
        for key, edit in self.unit_fields.items():
            text = edit.text().strip().replace(',', '.')
            if not text:
                self.data[key] = 0.0
                continue
            try:
                self.data[key] = float(text)
            except ValueError:
                raise ValueError(f"Ungültiger Zahlenwert für '{key}': {edit.text()}")

    # ---------------- Rohrpreis-Logik ----------------

    def _ensure_rohr_structure(self):
        if "Rohr" not in self.data or not isinstance(self.data["Rohr"], dict):
            self.data["Rohr"] = {}
        if "AUSSENDURCHMESSER" not in self.params or not isinstance(self.params["AUSSENDURCHMESSER"], dict):
            self.params["AUSSENDURCHMESSER"] = {}

    def _fill_rohr_table(self):
        self._ensure_rohr_structure()
        self.table_rohr.setRowCount(0)
        material = self.combo_material.currentText()
        if not material:
            self.combo_material.blockSignals(True)
            self.combo_material.clear()
            # Materialquellen: Preise und Außendurchmesser zusammenführen
            mats = set(self.data["Rohr"].keys()) | set(self.params["AUSSENDURCHMESSER"].keys())
            for mat in sorted(mats):
                self.combo_material.addItem(mat)
            self.combo_material.blockSignals(False)
            material = self.combo_material.currentText()

        if not material:
            return

        dim_prices = self.data["Rohr"].get(material, {})
        dim_od = self.params["AUSSENDURCHMESSER"].get(material, {})

        # dimensionen vereinigen
        dims = sorted({*dim_prices.keys(), *dim_od.keys()}, key=lambda x: float(x))
        self.table_rohr.setRowCount(len(dims))

        for row, dim in enumerate(dims):
            price = dim_prices.get(dim, "")
            od = dim_od.get(dim, "")

            self.table_rohr.setItem(row, 0, QTableWidgetItem(str(dim)))
            self.table_rohr.setItem(row, 1, QTableWidgetItem(str(price)))
            self.table_rohr.setItem(row, 2, QTableWidgetItem(str(od)))

    def _collect_rohr_prices(self):
        self._ensure_rohr_structure()

        for idx in range(self.combo_material.count()):
            material = self.combo_material.itemText(idx)
            self.data["Rohr"].setdefault(material, {})
            self.params["AUSSENDURCHMESSER"].setdefault(material, {})

        current_material = self.combo_material.currentText()
        if not current_material:
            return

        dim_prices = {}
        dim_od = {}

        for row in range(self.table_rohr.rowCount()):
            dim_item = self.table_rohr.item(row, 0)
            price_item = self.table_rohr.item(row, 1)
            od_item = self.table_rohr.item(row, 2)

            if not dim_item or not dim_item.text().strip():
                continue

            dim_text = dim_item.text().strip()

            # Preis
            price_val = None
            if price_item and price_item.text().strip():
                price_text = price_item.text().strip().replace(',', '.')
                try:
                    price_val = float(price_text)
                except ValueError:
                    raise ValueError(
                        f"Ungültiger Preis für Rohr {current_material} DN {dim_text}: {price_item.text()}"
                    )

            # Außendurchmesser
            od_val = None
            if od_item and od_item.text().strip():
                od_text = od_item.text().strip().replace(',', '.')
                try:
                    od_val = float(od_text)
                except ValueError:
                    raise ValueError(
                        f"Ungültiger Außendurchmesser für Rohr {current_material} DN {dim_text}: {od_item.text()}"
                    )

            if price_val is not None:
                dim_prices[dim_text] = price_val
            if od_val is not None:
                dim_od[dim_text] = od_val

        self.data["Rohr"][current_material] = dim_prices
        self.params["AUSSENDURCHMESSER"][current_material] = dim_od

    def _add_rohr_row(self):
        row = self.table_rohr.rowCount()
        self.table_rohr.insertRow(row)
        self.table_rohr.setItem(row, 0, QTableWidgetItem(""))
        self.table_rohr.setItem(row, 1, QTableWidgetItem(""))

    def _delete_rohr_row(self):
        rows = sorted({idx.row() for idx in self.table_rohr.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table_rohr.removeRow(r)

    def _add_material(self):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Neues Material", "Materialname:")
        if not ok or not text.strip():
            return
        name = text.strip()
        self._ensure_rohr_structure()
        if name in self.data["Rohr"] or name in self.params["AUSSENDURCHMESSER"]:
            QMessageBox.warning(self, "Hinweis", f"Material '{name}' existiert bereits.")
            return
        self.data["Rohr"][name] = {}
        self.params["AUSSENDURCHMESSER"][name] = {}
        self.combo_material.addItem(name)
        self.combo_material.setCurrentText(name)
        self._fill_rohr_table()

    def _delete_material(self):
        material = self.combo_material.currentText()
        if not material:
            return
        reply = QMessageBox.question(
            self,
            "Material löschen",
            f"Soll das Material '{material}' mit allen Dimensionen wirklich gelöscht werden?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._ensure_rohr_structure()
        self.data["Rohr"].pop(material, None)
        self.params["AUSSENDURCHMESSER"].pop(material, None)
        idx = self.combo_material.currentIndex()
        self.combo_material.removeItem(idx)
        self._fill_rohr_table()

    # ---------------- Aufbauvarianten ----------------

    def _ensure_aufbau_structure(self):
        if "AUFBAUVARIANTEN" not in self.params or not isinstance(self.params["AUFBAUVARIANTEN"], dict):
            self.params["AUFBAUVARIANTEN"] = {}

    def _fill_aufbau_table(self):
        self._ensure_aufbau_structure()
        self.table_aufbau.setRowCount(0)

        for belastung, bdata in self.params["AUFBAUVARIANTEN"].items():
            bname = bdata.get("name", "")
            for vkey, vdata in bdata.get("varianten", {}).items():
                vname = vdata.get("name", "")
                schichten = vdata.get("schichten", {})
                for schichtname, dicke in schichten.items():
                    row = self.table_aufbau.rowCount()
                    self.table_aufbau.insertRow(row)
                    self.table_aufbau.setItem(row, 0, QTableWidgetItem(str(belastung)))
                    self.table_aufbau.setItem(row, 1, QTableWidgetItem(str(vkey)))
                    # Variantenname: wenn leer, Standard aus JSON oder Klassenname
                    self.table_aufbau.setItem(row, 2, QTableWidgetItem(str(vname or bname)))
                    self.table_aufbau.setItem(row, 3, QTableWidgetItem(str(schichtname)))
                    self.table_aufbau.setItem(row, 4, QTableWidgetItem(str(dicke)))

    def _collect_aufbau(self):
        self._ensure_aufbau_structure()
        aufbau = {}

        for row in range(self.table_aufbau.rowCount()):
            b_item = self.table_aufbau.item(row, 0)
            vkey_item = self.table_aufbau.item(row, 1)
            vname_item = self.table_aufbau.item(row, 2)
            schicht_item = self.table_aufbau.item(row, 3)
            dicke_item = self.table_aufbau.item(row, 4)

            if not (b_item and vkey_item and schicht_item and dicke_item):
                continue

            belastung = b_item.text().strip()
            vkey = vkey_item.text().strip()
            vname = vname_item.text().strip() if vname_item else ""
            schichtname = schicht_item.text().strip()
            dicke_text = dicke_item.text().strip().replace(',', '.')

            if not belastung or not vkey or not schichtname or not dicke_text:
                continue

            try:
                dicke_val = float(dicke_text)
            except ValueError:
                raise ValueError(
                    f"Ungültige Dicke in Aufbauzeile (Belastung {belastung}, Variante {vkey}, Schicht {schichtname}): {dicke_item.text()}"
                )

            # Struktur aufbauen
            b = aufbau.setdefault(belastung, {"name": belastung, "varianten": {}})
            v = b["varianten"].setdefault(vkey, {"name": vname or vkey, "schichten": {}})
            v["schichten"][schichtname] = dicke_val

        self.params["AUFBAUVARIANTEN"] = aufbau

    def _add_aufbau_row(self):
        row = self.table_aufbau.rowCount()
        self.table_aufbau.insertRow(row)
        # leere Items, damit direkt editierbar
        for col in range(5):
            self.table_aufbau.setItem(row, col, QTableWidgetItem(""))

    def _delete_aufbau_row(self):
        rows = sorted({idx.row() for idx in self.table_aufbau.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table_aufbau.removeRow(r)

    # ---------------- Save / Cancel ----------------

    def _on_save(self):
        try:
            self._collect_unit_prices()
            self._collect_rohr_prices()
            self._collect_aufbau()
        except ValueError as e:
            QMessageBox.warning(self, "Fehler", str(e))
            return

        self._save_json()    # Preise
        self._save_params()  # AUSSENDURCHMESSER + AUFBAUVARIANTEN
        self.accept()


