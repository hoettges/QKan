from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QGroupBox, QFormLayout,
    QLineEdit, QDateEdit, QDialogButtonBox, QVBoxLayout,
    QLabel, QTextEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QDate
from .dwa_kurzcode_mapping import DWA_DATA
from .zustandsklassen_mapping import ZUSTAND

import json
import os

MAPPING_JSON = os.path.join(os.path.dirname(__file__), "schacht_mapping.json")
MAPPING_LEITUNG = os.path.join(os.path.dirname(__file__), "leitung_mapping.json")

BEREICH_CHOICES = [
    ("",  "–"),
    ("A", "Abdeckung und Rahmen"),
    ("B", "Auflageringe"),
    ("C", "Schachtaufbau"),
    ("D", "Konus"),
    ("E", "Übergangsplatte"),
    ("F", "untere Schachtzone"),
    ("G", "Podest"),
    ("H", "Auftritt"),
    ("I", "Gerinne"),
    ("J", "Sohle"),
]

class NewUntersuchungDialog(QDialog):
    def __init__(self, maintabname, parent=None, preset_values=None, material=None, dimension=None):
        super().__init__(parent)
        self.setWindowTitle("Neuer Untersuchungs-Eintrag")
        self._widgets = {}
        self._preset = preset_values or {}
        # Material aus Stammdaten merken (string oder None)
        self._material_raw = (material or "").strip()
        self._dimension_raw = (dimension or "").strip()
        self._maintabname = maintabname

        self.tab_widget = QTabWidget(self)

        # === Tab 1: Stammdaten ===
        stammdaten_tab = QWidget(self)
        stammdaten_layout = QVBoxLayout(stammdaten_tab)

        gb_allg = QGroupBox("Stammdaten", self)
        btn_calc = QPushButton("Zustandsklassen ermitteln", self)
        btn_calc.clicked.connect(self._calc_zustandsklassen)
        stammdaten_layout.addWidget(btn_calc)

        allg_form = QFormLayout(gb_allg)

        # untersuchtag
        self._add_date_field(allg_form, "untersuchtag")

        # station / vertikale_lage
        if maintabname in ("Haltungen", "GAL"):
            self._add_field(allg_form, "station")
        elif maintabname == "Schächte":
            self._add_field(allg_form, "vertikale_lage")
            # NEU: Bereich-Combo für Schächte
            self._add_bereich_combobox(allg_form)

        # kuerzel als ComboBox
        self._add_kuerzel_combobox(allg_form)

        # langtext als read-only
        self._add_langtext_field(allg_form)

        # Merkmalsfelder als Comboboxen / LineEdit
        self._add_charakt_comboboxes(allg_form)

        # kommentar, bandnr
        self._add_field(allg_form, "kommentar", multiline=True)
        self._add_field(allg_form, "bandnr")

        # NEU: Quantifizierungen & Positionen
        self._add_field(allg_form, "quantnr1")
        self._add_field(allg_form, "quantnr2")
        self._add_field(allg_form, "pos_von")
        self._add_field(allg_form, "pos_bis")
        self._add_field(allg_form, "zd")
        self._add_field(allg_form, "zs")
        self._add_field(allg_form, "zb")

        gb_allg.setLayout(allg_form)
        stammdaten_layout.addWidget(gb_allg)

        stammdaten_tab.setLayout(stammdaten_layout)
        self.tab_widget.addTab(stammdaten_tab, "Stammdaten")

        # === Tab 2: Medien ===
        medien_tab = QWidget(self)
        medien_layout = QVBoxLayout(medien_tab)

        gb_medien = QGroupBox("Medien", self)
        med_form = QFormLayout(gb_medien)

        self._add_field(med_form, "videozaehler")
        self._add_field(med_form, "foto_dateiname")
        if maintabname in ("Haltungen", "GAL"):
            self._add_field(med_form, "film_dateiname")

        gb_medien.setLayout(med_form)
        medien_layout.addWidget(gb_medien)

        medien_tab.setLayout(medien_layout)
        self.tab_widget.addTab(medien_tab, "Medien")

        # === Tab 3: Einstellungen ===
        settings_tab = QWidget(self)
        settings_layout = QVBoxLayout(settings_tab)

        gb_settings = QGroupBox("Einstellungen", self)
        settings_form = QVBoxLayout(gb_settings)

        btn_mapping_s = QPushButton("Schacht-Mapping bearbeiten", self)
        btn_mapping_s.clicked.connect(self._open_mapping_editor_schacht)
        settings_form.addWidget(btn_mapping_s)

        btn_mapping_l = QPushButton("Leitungs-Mapping (Haltungen/GAL) bearbeiten", self)
        btn_mapping_l.clicked.connect(self._open_mapping_editor_leitung)
        settings_form.addWidget(btn_mapping_l)

        gb_settings.setLayout(settings_form)
        settings_layout.addWidget(gb_settings)

        settings_tab.setLayout(settings_layout)
        self.tab_widget.addTab(settings_tab, "Einstellungen")

        # === Buttons ===
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

        # Nach Konstruktion Kürzel/Charakteristika aus Presets setzen
        self._apply_presets_for_dwa()

    # --- DWA-spezifische Widgets ---

    def _add_kuerzel_combobox(self, form):
        label = QLabel("kuerzel", self)
        cb = QComboBox(self)
        cb.addItem("")  # leer
        for k in sorted(DWA_DATA.get(self._maintabname, {}).keys()):
            cb.addItem(k)
        cb.currentTextChanged.connect(self._on_kuerzel_changed)
        self._widgets["kuerzel"] = cb
        form.addRow(label, cb)

    def _add_charakt_comboboxes(self, form):
        # charakt1
        label1 = QLabel("charakt1", self)
        cb1 = QComboBox(self)
        cb1.addItem("")
        cb1.currentTextChanged.connect(self._on_charakt_changed)
        self._widgets["charakt1"] = cb1
        form.addRow(label1, cb1)

        # charakt2
        label2 = QLabel("charakt2", self)
        cb2 = QComboBox(self)
        cb2.addItem("")
        cb2.currentTextChanged.connect(self._on_charakt_changed)
        self._widgets["charakt2"] = cb2
        form.addRow(label2, cb2)

    def _add_langtext_field(self, form):
        label = QLabel("langtext", self)
        te = QTextEdit(self)
        te.setReadOnly(True)
        self._widgets["langtext"] = te
        form.addRow(label, te)

    def _on_kuerzel_changed(self, kuerzel):
        cb1 = self._widgets["charakt1"]
        cb2 = self._widgets["charakt2"]
        cb1.blockSignals(True)
        cb2.blockSignals(True)
        cb1.clear()
        cb2.clear()
        cb1.addItem("")
        cb2.addItem("")

        mapping = DWA_DATA.get(self._maintabname, {}).get(kuerzel, {})

        # charakt1: alle vorhandenen CH1-Werte
        char1_vals = set()
        for (c1, c2) in mapping.keys():
            if c1:
                char1_vals.add(c1)
        for v in sorted(char1_vals):
            cb1.addItem(v)

        # charakt2 vorerst nur global verfügbar (für Fälle ohne c1),
        # wird bei Wahl von charakt1 in _on_charakt_changed eingeschränkt
        char2_vals = set()
        for (c1, c2) in mapping.keys():
            if c2:
                char2_vals.add(c2)
        for v in sorted(char2_vals):
            cb2.addItem(v)

        cb1.blockSignals(False)
        cb2.blockSignals(False)

        self._update_langtext()

    def _on_charakt_changed(self, _):
        """
        Aktualisiert charakt2-Optionen abhängig von gewähltem charakt1
        und hält nur CH2-Werte im Mapping zu (c1, *) vor.
        """
        kuerzel = self._widgets["kuerzel"].currentText()
        c1 = self._widgets["charakt1"].currentText() or ""
        cb2 = self._widgets["charakt2"]

        mapping = DWA_DATA.get(self._maintabname, {}).get(kuerzel, {})

        # erlaubte CH2-Werte für das gewählte c1 bestimmen
        allowed_c2 = set()
        for (mc1, mc2) in mapping.keys():
            if mc1 == c1 and mc2:
                allowed_c2.add(mc2)

        current_c2 = cb2.currentText()

        cb2.blockSignals(True)
        cb2.clear()
        cb2.addItem("")

        for v in sorted(allowed_c2):
            cb2.addItem(v)

        # aktuellen Wert nur wieder setzen, wenn er noch erlaubt ist
        if current_c2 and current_c2 in allowed_c2:
            idx = cb2.findText(current_c2)
            if idx >= 0:
                cb2.setCurrentIndex(idx)
        cb2.blockSignals(False)

        self._update_langtext()

    def _update_langtext(self):
        kuerzel = self._widgets["kuerzel"].currentText()
        c1 = self._widgets["charakt1"].currentText()
        c2 = self._widgets["charakt2"].currentText()

        kuerzel_mapping = DWA_DATA.get(self._maintabname, {}).get(kuerzel, {})

        # Basistext des Kürzels (ohne Charakterisierung)
        basis = kuerzel_mapping.get(("", ""), "")  # z.B. "Schadhafter Anschluss"

        # Spezifischer Text zur gewählten Charakterisierung
        spez = (
            kuerzel_mapping.get((c1, c2))
            or kuerzel_mapping.get((c1, ""))
            or kuerzel_mapping.get(("", c2))
            or ""
        )

        if not basis:
            # Fallback: wie bisher nur den spez. Text
            text = spez
        elif not spez or spez == basis:
            # Nur Basistext anzeigen, wenn es keinen spezifischen Text gibt
            text = basis
        else:
            # Gewünschtes Format: "Basis: Spezifik"
            text = f"{basis}: {spez}"

        self._widgets["langtext"].setPlainText(text)

    def _add_field(self, form, col_name, multiline=False):
        label = QLabel(col_name, self)

        if multiline:
            w = QTextEdit(self)
        else:
            w = QLineEdit(self)

        if col_name in self._preset:
            val = self._preset[col_name]
            if isinstance(w, QTextEdit):
                w.setPlainText(str(val))
            else:
                w.setText(str(val))

        self._widgets[col_name] = w
        form.addRow(label, w)

    def _add_date_field(self, form, col_name):
        label = QLabel(col_name, self)
        w = QDateEdit(self)
        w.setCalendarPopup(True)
        w.setDate(QDate.currentDate())
        if col_name in self._preset:
            val = self._preset[col_name]
            if isinstance(val, str):
                try:
                    y, m, d = map(int, val.split("-"))
                    w.setDate(QDate(y, m, d))
                except Exception:
                    pass
        self._widgets[col_name] = w
        form.addRow(label, w)


    def _apply_presets_for_dwa(self):
        # Kürzel/Charakt-Defaults aus preset setzen und Langtext nachziehen
        if "kuerzel" in self._preset:
            idx = self._widgets["kuerzel"].findText(self._preset["kuerzel"])
            if idx >= 0:
                self._widgets["kuerzel"].setCurrentIndex(idx)
        if "charakt1" in self._preset:
            # wird nach kuerzel gefüllt – daher erst später sinnvoll
            pass
        if "charakt2" in self._preset:
            pass
        # Nach initialem Setzen einmal update_langtext aufrufen
        self._update_langtext()

    def get_values(self):
        data = {}
        for col, w in self._widgets.items():
            # Datum
            if isinstance(w, QDateEdit):
                data[col] = w.date().toString("yyyy-MM-dd")

            # mehrzeiliger Text (langtext, kommentar)
            elif isinstance(w, QTextEdit):
                text = w.toPlainText().strip()
                data[col] = text if text != "" else None

            # Combobox (kuerzel, charakt1, charakt2, bereich, ...)
            elif isinstance(w, QComboBox):
                if col == "bereich":
                    # Nur den Buchstaben speichern (ItemData)
                    code = w.currentData()
                    if not code:
                        # Fallback: ersten Buchstaben des Textes
                        text = w.currentText().strip()
                        code = text.split(" ", 1)[0] if text else ""
                    data[col] = code or None
                else:
                    text = w.currentText().strip()
                    data[col] = text if text != "" else None

            # normale LineEdits
            elif isinstance(w, QLineEdit):
                raw = w.text().strip()
                if raw == "":
                    data[col] = None
                elif col in ("station", "vertikale_lage"):
                    data[col] = self._normalize_decimal(raw)
                else:
                    data[col] = raw

            # Fallback
            else:
                try:
                    text = w.text().strip()
                    data[col] = text if text != "" else None
                except AttributeError:
                    data[col] = None

        return data


    def _normalize_decimal(self, text: str):
        """
        Erlaubt Eingabe mit Komma oder Punkt und gibt String
        mit Punkt als Dezimaltrenner zurück.
        """
        if text is None:
            return None
        text = text.strip()
        if not text:
            return None
        return text.replace(",", ".")

    def _calc_zustandsklassen(self):
        gruppe = self._maintabname  # "Haltungen", "Schächte", "GAL"
        kuerzel = self._widgets["kuerzel"].currentText() or ""
        c1 = self._widgets["charakt1"].currentText() or ""
        c2 = self._widgets["charakt2"].currentText() or ""
        q1_raw = (self._widgets.get("quantnr1").text() or "").strip()

        try:
            if q1_raw == "":
                q1 = 0.0   # NEU: fehlende Eingabe -> 0
            else:
                q1 = float(q1_raw.replace(",", "."))
        except ValueError:
            q1 = 0.0       # bei Fehler auch 0 als Fallback


        material_klasse = self._material_klassifikation()

        # NEU: Bereich für Schächte holen (Buchstabe A–J)
        if gruppe == "Schächte" and "bereich" in self._widgets:
            bereich = (self._widgets["bereich"].currentData()
                       if isinstance(self._widgets["bereich"], QComboBox)
                       else self._widgets["bereich"].text()).strip().upper()
        else:
            bereich = ""

        print(f"[ZK] Eingabe: gruppe={gruppe}, kuerzel={kuerzel}, "
              f"c1={c1}, c2={c2}, q1_raw='{q1_raw}', q1={q1}, "
              f"material_klasse={material_klasse}, bereich={bereich}")

        bew = self._lookup_zustandsklassen(
            gruppe, kuerzel, c1, c2, q1, material_klasse, bereich
        )

        print(f"[ZK] Ergebnis Zustandsklassen: D={bew.get('D')}, "
              f"S={bew.get('S')}, B={bew.get('B')}")

        self._widgets["zd"].setText(str(bew.get("D", 0)))
        self._widgets["zs"].setText(str(bew.get("S", 0)))
        self._widgets["zb"].setText(str(bew.get("B", 0)))


    def _lookup_zustandsklassen(self, gruppe, kuerzel, c1, c2, q1,
                                material_klasse=None, bereich=""):
        """
        Gibt für ein Kürzel/Char1/Char2/Quant1 (+ ggf. Bereich) die
        Zustandsklassen für D,S,B zurück (0..5).
        """
        bereich = (bereich or "").upper()

        print("\n[ZK] ==== _lookup_zustandsklassen ====")
        print(f"[ZK] Eingabe: gruppe={gruppe}, kuerzel={kuerzel}, "
              f"c1={c1}, c2={c2}, q1={q1}, "
              f"material_klasse={material_klasse}, bereich={bereich}")

        g_map = ZUSTAND.get(gruppe, {})
        k_map = g_map.get(kuerzel, {})

        print(f"[ZK] Verfügbare Kürzel in Gruppe '{gruppe}': {list(g_map.keys())}")
        print(f"[ZK] Rohes k_map für kuerzel '{kuerzel}': {type(k_map)}")

        # BAA: Unterstruktur nach Material
        if kuerzel == "BAA":
            print("[ZK] Kürzel ist BAA, Materialpfad wird benutzt")
            mat_klass = material_klasse or self._material_klassifikation()
            print(f"[ZK] Verwendete Material-Klassifikation: {mat_klass}")
            if isinstance(k_map, dict):
                print(f"[ZK] BAA: verfügbare Material-Schlüssel: {list(k_map.keys())}")
                k_map = k_map.get(mat_klass, {}) or {}
            print(f"[ZK] BAA: k_map nach Material-Auswahl: {list(k_map.keys())}")

        # BAJ: differenziert nach A/B/C (bestehende Speziallogik)
        if kuerzel == "BAJ":
            print("[ZK] Kürzel ist BAJ, spezielle BAJ-Logik")

            if c1 == "A":
                if isinstance(k_map, dict):
                    dn_bereich = self._dimension_klassifikation_baj()
                    print(f"[ZK] Ergebnis _dimension_klassifikation_baj (A): {dn_bereich}")
                    if dn_bereich == "gross":
                        print("[ZK] BAJ/A: benutze DN-Bereich 'gross'")
                        k_map = k_map.get("gross", {}) or {}
                    else:
                        print("[ZK] BAJ/A: DN <= 800, benutze pauschalen Teilbaum 'A_pauschal'")
                        k_map = k_map.get("A_pauschal", {}) or {}

            elif c1 == "B":
                print("[ZK] BAJ/B: DN wird ignoriert, k_map bleibt wie definiert")

            elif c1 == "C":
                if isinstance(k_map, dict):
                    dn_c = self._dimension_klassifikation_baj_c()
                    print(f"[ZK] Ergebnis _dimension_klassifikation_baj_c: {dn_c}")
                    if dn_c:
                        print(f"[ZK] BAJ/C: verfügbare DN-C-Bereiche: {list(k_map.keys())}")
                        print(f"[ZK] BAJ/C: benutze DN-C-Bereich '{dn_c}'")
                        k_map = k_map.get(dn_c, {}) or {}
                        print(f"[ZK] BAJ/C: k_map nach DN-C-Auswahl: {list(k_map.keys())}")
                    else:
                        print("[ZK] BAJ/C: kein DN-C-Bereich ableitbar, fallback auf flaches Mapping")

        key_used = None

        # --- Spezielle Logik für Schächte-Schäden (alle Kürzel, die mit 'D' beginnen) ---
        if gruppe == "Schächte" and kuerzel.startswith("D"):
            print("[ZK] Spezielle Schacht-Logik mit Bereichsdifferenzierung")

            # 1. passenden (c1,c2)-Block suchen
            bereich_map = None
            for cand in ((c1, c2), (c1, ""), ("", c2), ("", "")):
                if cand in k_map:
                    bereich_map = k_map[cand]
                    key_used = cand
                    break

            print(f"[ZK] Gewählter (c1,c2)-Key: {key_used}")
            print(f"[ZK] bereich_map: {bereich_map}")

            if not isinstance(bereich_map, dict):
                print("[ZK] Kein Bereich-Map gefunden, alle Zustandsklassen = 0")
                print("[ZK] ==== _lookup_zustandsklassen ENDE ====")
                return {"D": 0, "S": 0, "B": 0}

            # Hilfsfunktion: für EIN Schutzziel passenden Bereichseintrag holen
            def eintrag_fuer_schutz(schutz):
                # 1. expliziten Bereich mit nicht leerem schutz-Teil suchen
                if bereich:
                    for grp_key, s_map in bereich_map.items():
                        if grp_key != "ALL" and bereich in grp_key:
                            if s_map.get(schutz):
                                print(f"[ZK] Schutz '{schutz}': Bereich '{bereich}' fällt in Gruppe '{grp_key}'")
                                return s_map
                # 2. Fallback ALL, falls vorhanden
                if "ALL" in bereich_map and bereich_map["ALL"].get(schutz):
                    print(f"[ZK] Schutz '{schutz}': Fallback auf ALL")
                    return bereich_map["ALL"]
                # 3. gar nichts gefunden
                print(f"[ZK] Schutz '{schutz}': kein passender Bereichseintrag, nutze leer")
                return {"D": {}, "S": {}, "B": {}}

            def klasse_fuer_schutz(schutz):
                s_map_container = eintrag_fuer_schutz(schutz)
                s_map = s_map_container.get(schutz)
                print(f"[ZK]  Schutz '{schutz}': s_map={s_map}")
                if not s_map:
                    print(f"[ZK]   -> kein Mapping für Schutz '{schutz}', Klasse 0")
                    return 0
                if "pauschal" in s_map:
                    print(f"[ZK]   -> pauschal {s_map['pauschal']}")
                    return s_map["pauschal"]
                if q1 is None:
                    print("[ZK]   -> q1 ist None, Klasse 0")
                    return 0
                for (min_v, max_v, k) in s_map.get("intervalle", []):
                    print(f"[ZK]   Test Intervall {min_v} <= {q1} < {max_v} -> Klasse {k}")
                    if (min_v is None or q1 >= min_v) and (max_v is None or q1 < max_v):
                        print(f"[ZK]   -> getroffen, Klasse {k}")
                        return k
                print("[ZK]   -> kein Intervall getroffen, Klasse 0")
                return 0

            d = klasse_fuer_schutz("D")
            s = klasse_fuer_schutz("S")
            b = klasse_fuer_schutz("B")
            print(f"[ZK] Rückgabe: D={d}, S={s}, B={b}")
            print("[ZK] ==== _lookup_zustandsklassen ENDE ====")
            return {"D": d, "S": s, "B": b}

        # --- Standard-Logik für alle anderen Fälle (Haltungen, GAL, nicht-D-Schächte) ---
        eintrag = None
        if (c1, c2) in k_map:
            eintrag = k_map[(c1, c2)]
            key_used = (c1, c2)
        elif (c1, "") in k_map:
            eintrag = k_map[(c1, "")]
            key_used = (c1, "")
        elif ("", c2) in k_map:
            eintrag = k_map[("", c2)]
            key_used = ("", c2)
        elif ("", "") in k_map:
            eintrag = k_map[("", "")]
            key_used = ("", "")
        else:
            eintrag = None

        print(f"[ZK] Gewählter Eintrag-Key: {key_used}")
        print(f"[ZK] Gefundener Eintrag: {eintrag}")

        if not eintrag:
            print("[ZK] Kein Eintrag gefunden, alle Zustandsklassen = 0")
            print("[ZK] ==== _lookup_zustandsklassen ENDE ====")
            return {"D": 0, "S": 0, "B": 0}

        def klasse_fuer_schutz(schutz):
            s_map = eintrag.get(schutz)
            print(f"[ZK]  Schutz '{schutz}': s_map={s_map}")
            if not s_map:
                print(f"[ZK]   -> kein Mapping für Schutz '{schutz}', Klasse 0")
                return 0
            if "pauschal" in s_map:
                print(f"[ZK]   -> pauschal {s_map['pauschal']}")
                return s_map["pauschal"]
            if q1 is None:
                print("[ZK]   -> q1 ist None, Klasse 0")
                return 0
            for (min_v, max_v, k) in s_map.get("intervalle", []):
                print(f"[ZK]   Test Intervall {min_v} <= {q1} < {max_v} -> Klasse {k}")
                if (min_v is None or q1 >= min_v) and (max_v is None or q1 < max_v):
                    print(f"[ZK]   -> getroffen, Klasse {k}")
                    return k
            print("[ZK]   -> kein Intervall getroffen, Klasse 0")
            return 0

        d = klasse_fuer_schutz("D")
        s = klasse_fuer_schutz("S")
        b = klasse_fuer_schutz("B")
        print(f"[ZK] Rückgabe: D={d}, S={s}, B={b}")
        print("[ZK] ==== _lookup_zustandsklassen ENDE ====")
        return {"D": d, "S": s, "B": b}

    
    def _material_klassifikation(self) -> str:
        """
        Liefert 'biegeweich' oder 'biegesteif' anhand des Material-Codes
        aus den Stammdaten (self._material_raw).
        """
        mat = (self._material_raw or "").strip().upper()
        print(f"[ZK] Material-Rohwert (Stammdaten): '{mat}'")

        biegeweich_codes = {
            "PP", "PE", "PEHD", "HDPE", "PVC", "PVC-U", "PVCU",
            "GRP", "GFK", "PP-H", "PPH", "PP-MD"
        }

        if mat in biegeweich_codes:
            return "biegeweich"

        return "biegesteif"

    def _dimension_klassifikation_baj_c(self):
        """
        Liefert für BAJ/C den Bereichs-Key 'DN<=200', '200<DN<=500' oder 'DN>500'
        anhand self._dimension_raw.
        """
        dim = (self._dimension_raw or "").strip()
        if not dim:
            print("[ZK] Keine Dimension vorhanden, BAJ-C-DN-Bereich unbekannt")
            return None

        try:
            if "/" in dim:
                _, h_str = dim.split("/", 1)
                dn = float(h_str.replace(",", "."))
            else:
                dn = float(dim.replace(",", "."))
        except ValueError:
            print(f"[ZK] Dimension für BAJ/C nicht interpretierbar: '{dim}'")
            return None

        print(f"[ZK] Abgeleitete DN für BAJ/C: {dn}")

        if dn <= 200:
            return "DN<=200"
        elif dn <= 500:
            return "200<DN<=500"
        else:
            return "DN>500"

    def _dimension_klassifikation_baj(self):
        """
        Liefert für BAJ/A den Bereichs-Key 'gross' oder 'A_pauschal'
        anhand self._dimension_raw.

        - Rundprofile: '200', '800', ...
        - Ei-/Drachenprofile: '250/375' -> es gilt der Wert hinter dem '/' (hier 375).
        """
        dim = (self._dimension_raw or "").strip()
        if not dim:
            print("[ZK] Keine Dimension vorhanden, BAJ-A-DN-Bereich unbekannt")
            return None

        try:
            if "/" in dim:
                _, h_str = dim.split("/", 1)
                dn = float(h_str.replace(",", "."))
            else:
                dn = float(dim.replace(",", "."))
        except ValueError:
            print(f"[ZK] Dimension für BAJ/A nicht interpretierbar: '{dim}'")
            return None

        print(f"[ZK] Abgeleitete DN für BAJ/A: {dn}")

        # Nur DN > 800 nach Intervallen, sonst pauschal
        if dn > 800:
            return "gross"
        else:
            return "A_pauschal"

    def _add_bereich_combobox(self, form):
        """Bereich-ComboBox für Schächte: Anzeige 'A – Abdeckung...', Wert nur der Buchstabe."""
        label = QLabel("bereich", self)
        cb = QComboBox(self)

        # Einträge hinzufügen
        for code, desc in BEREICH_CHOICES:
            if code:
                display = f"{code} – {desc}"
            else:
                display = " "  # leerer Eintrag
            cb.addItem(display, code)

        # Preset berücksichtigen (ggf. Buchstabe aus _preset['bereich'] setzen)
        preset_code = (self._preset.get("bereich") or "").strip().upper()
        if preset_code:
            for i in range(cb.count()):
                if cb.itemData(i) == preset_code:
                    cb.setCurrentIndex(i)
                    break

        # Im Widget-Registry als 'bereich' speichern
        self._widgets["bereich"] = cb
        form.addRow(label, cb)

    def _open_mapping_editor(self):
        """Öffnet den Tabellen-Editor für Schacht-Mappings."""
        dlg = MappingEditorDialog(self)
        dlg.exec_()

    def _open_mapping_editor_schacht(self):
        dlg = MappingEditorDialog(self, mode="schacht")
        dlg.exec_()

    def _open_mapping_editor_leitung(self):
        dlg = MappingEditorDialog(self, mode="leitung")
        dlg.exec_()

class MappingEditorDialog(QDialog):
    """
    Tabellen-Editor für Mapping.

    mode = "schacht":
        schacht_mapping.json, Spalten:
        kuerzel, ch1, ch2, bereich, schutz, typ, v_min, v_max, klasse

    mode = "leitung":
        leitung_mapping.json, Spalten:
        gruppe, kuerzel, material, ch1, ch2, schutz, typ, v_min, v_max, klasse
    """

    HEADERS_SCHACHT = [
        "kuerzel", "ch1", "ch2", "bereich",
        "schutz", "typ", "v_min", "v_max", "klasse",
    ]

    HEADERS_LEITUNG = [
        "gruppe", "kuerzel", "material", "ch1", "ch2",
        "schutz", "typ", "v_min", "v_max", "klasse",
    ]

    def __init__(self, parent=None, mode="schacht"):
        super().__init__(parent)
        self.mode = mode

        from .zustandsklassen_mapping import (
            MAPPING_JSON,      # schacht_mapping.json
            MAPPING_LEITUNG,   # leitung_mapping.json
        )

        if self.mode == "schacht":
            self._json_path = MAPPING_JSON
            self.HEADERS = self.HEADERS_SCHACHT
            self.setWindowTitle("Schacht-Mapping bearbeiten")
        else:
            self._json_path = MAPPING_LEITUNG
            self.HEADERS = self.HEADERS_LEITUNG
            self.setWindowTitle("Leitungs-Mapping (Haltungen/GAL) bearbeiten")

        # Spaltenindizes dynamisch bestimmen
        self.COL_SCHUTZ = self.HEADERS.index("schutz")
        self.COL_TYP = self.HEADERS.index("typ")

        self.table = QTableWidget(self)
        self.table.setColumnCount(len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)

        # Sortierung erlauben
        self.table.setSortingEnabled(True)
        self.table.sortItems(0)

        btn_add = QPushButton("Zeile hinzufügen", self)
        btn_del = QPushButton("Zeile löschen", self)
        btn_dup = QPushButton("Zeile duplizieren", self)
        btn_load = QPushButton("Laden", self)
        btn_save = QPushButton("Speichern", self)

        btn_add.clicked.connect(self._add_row)
        btn_del.clicked.connect(self._delete_row)
        btn_dup.clicked.connect(self._duplicate_row)
        btn_load.clicked.connect(self._load_json)
        btn_save.clicked.connect(self._save_json)

        btn_box = QDialogButtonBox(QDialogButtonBox.Close, parent=self)
        btn_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(btn_add)
        layout.addWidget(btn_del)
        layout.addWidget(btn_dup)
        layout.addWidget(btn_load)
        layout.addWidget(btn_save)
        layout.addWidget(btn_box)
        self.setLayout(layout)

        # Spaltenbreiten – angepasst an Anzahl Spalten je Modus
        if self.mode == "schacht":
            col_widths = [80, 60, 60, 120, 60, 80, 70, 70, 60]
        else:  # leitung: eine Spalte mehr
            col_widths = [80, 80, 80, 60, 60, 60, 80, 70, 70, 60]
        for i, w in enumerate(col_widths):
            if i < self.table.columnCount():
                self.table.setColumnWidth(i, w)

        self._fix_size_for_columns()

        self.table.setSortingEnabled(True)
        self._load_json(initial=True)
        self.table.sortItems(0)

    # --- Zellenhilfen -------------------------------------------------

    def _make_schutz_cell(self, value: str):
        cb = QComboBox(self.table)
        cb.addItem("", "")      # leer
        cb.addItem("D", "D")
        cb.addItem("S", "S")
        cb.addItem("B", "B")
        idx = cb.findData((value or "").upper())
        if idx >= 0:
            cb.setCurrentIndex(idx)
        return cb

    def _make_typ_cell(self, value: str):
        cb = QComboBox(self.table)
        cb.addItem("", "")             # leer
        cb.addItem("pauschal", "pauschal")
        cb.addItem("intervall", "intervall")
        txt = (value or "").lower()
        idx = cb.findData(txt)
        if idx >= 0:
            cb.setCurrentIndex(idx)
        return cb

    def _fix_size_for_columns(self):
        total_width = sum(self.table.columnWidth(c) for c in range(self.table.columnCount()))
        total_width += self.table.verticalHeader().width()
        total_width += 40  # Ränder/Scrollbars

        header_h = self.table.horizontalHeader().height()
        row_h = self.table.verticalHeader().defaultSectionSize()
        visible_rows = 10
        total_height = header_h + row_h * visible_rows + 150  # + Buttons

        self.resize(total_width, total_height)
        self.setMinimumSize(total_width, total_height)

    # --- Zeilenoperationen --------------------------------------------

    def _add_row(self):
        was_sorting = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)

        row = self.table.rowCount()
        self.table.insertRow(row)

        for c, header in enumerate(self.HEADERS):
            if c == self.COL_SCHUTZ:
                cb = self._make_schutz_cell("")
                self.table.setCellWidget(row, c, cb)
            elif c == self.COL_TYP:
                cb = self._make_typ_cell("")
                self.table.setCellWidget(row, c, cb)
            else:
                self.table.setItem(row, c, QTableWidgetItem(""))

        self.table.setSortingEnabled(was_sorting)
        if was_sorting:
            self.table.sortItems(0)

    def _duplicate_row(self):
        row = self.table.currentRow()
        if row < 0:
            return

        was_sorting = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)

        new_row = self.table.rowCount()
        self.table.insertRow(new_row)

        for c in range(self.table.columnCount()):
            w = self.table.cellWidget(row, c)
            if isinstance(w, QComboBox):
                new_cb = QComboBox(self.table)
                for i in range(w.count()):
                    new_cb.addItem(w.itemText(i), w.itemData(i))
                new_cb.setCurrentIndex(w.currentIndex())
                self.table.setCellWidget(new_row, c, new_cb)
            else:
                src_item = self.table.item(row, c)
                text = src_item.text() if src_item else ""
                self.table.setItem(new_row, c, QTableWidgetItem(text))

        self.table.setSortingEnabled(was_sorting)
        if was_sorting:
            self.table.sortItems(0)

        self._save_json(silent=True)

    def _delete_row(self):
        cr = self.table.currentRow()
        if cr < 0:
            return

        was_sorting = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)

        self.table.removeRow(cr)

        self.table.setSortingEnabled(was_sorting)
        if was_sorting:
            self.table.sortItems(0)

        self._save_json()

    # --- Laden/Speichern ----------------------------------------------

    def _load_json(self, initial=False):
        path = self._json_path
        if not os.path.exists(path):
            if not initial:
                QMessageBox.information(self, "Info",
                                        f"Keine Mapping-Datei gefunden:\n{path}")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"JSON laden fehlgeschlagen:\n{e}")
            return

        rows = data.get("rows", [])

        was_sorting = self.table.isSortingEnabled()
        self.table.setSortingEnabled(False)

        self.table.setRowCount(0)
        for rowdata in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for c, header in enumerate(self.HEADERS):
                val = rowdata.get(header, "")
                if c == self.COL_SCHUTZ:
                    cb = self._make_schutz_cell(val)
                    self.table.setCellWidget(row, c, cb)
                elif c == self.COL_TYP:
                    cb = self._make_typ_cell(val)
                    self.table.setCellWidget(row, c, cb)
                else:
                    item = QTableWidgetItem("" if val is None else str(val))
                    self.table.setItem(row, c, item)

        self.table.setSortingEnabled(was_sorting)
        if was_sorting:
            self.table.sortItems(0)

    def _save_json(self, silent=False):
        from .zustandsklassen_mapping import (
            reload_schacht_mapping,
            reload_leitung_mapping,
        )

        rows = []
        for r in range(self.table.rowCount()):
            rowdata = {}
            for c, header in enumerate(self.HEADERS):
                if c in (self.COL_SCHUTZ, self.COL_TYP):
                    w = self.table.cellWidget(r, c)
                    if isinstance(w, QComboBox):
                        text = (w.currentData() or "").strip()
                    else:
                        text = ""
                else:
                    item = self.table.item(r, c)
                    text = item.text().strip() if item else ""
                rowdata[header] = text or ""
            rows.append(rowdata)

        data = {"rows": rows}
        path = self._json_path
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "Fehler", f"JSON speichern fehlgeschlagen:\n{e}")
            return

        # Mapping im Speicher aktualisieren
        if self.mode == "schacht":
            reload_schacht_mapping()
        else:
            reload_leitung_mapping()

        if not silent:
            QMessageBox.information(self, "OK", f"Mapping gespeichert nach:\n{path}")

