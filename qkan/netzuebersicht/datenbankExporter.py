import pandas as pd
import json
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QWidget,
    QListWidget, QLabel, QScrollArea, QGridLayout, QFileDialog, QMessageBox,
    QRadioButton, QDialogButtonBox
)
from PyQt5.QtCore import Qt

class DatenbankExporter:
    def __init__(self, connection):
        """
        Initialisiert den Exporter mit einer bestehenden Datenbankverbindung.
        
        Args:
            connection: Ein offenes Verbindungsobjekt (psycopg2 oder sqlite3/spatialite)
        """
        self.conn = connection
        
        # Bestimmen, ob es sich um SQLite/Spatialite handelt
        # Dies ist wichtig für die unterschiedliche SQL-Syntax (? vs %s)
        conn_type = str(type(self.conn)).lower()
        self.is_sqlite = 'sqlite' in conn_type or 'spatialite' in conn_type

    def get_latest_investigations(self, table, name_column, names):
        """
        Holt alle Datensätze mit dem jeweils aktuellsten untersuchtag pro Name.
        Kompatibel mit PostgreSQL und SQLite.
        
        Args:
            table (str): Name der Tabelle
            name_column (str): Spaltenname für die ID/den Namen
            names (list): Liste der IDs/Namen, nach denen gefiltert werden soll
        """
        if not names:
            return []
        
        # WICHTIG: Alle Namen explizit in Strings umwandeln.
        # Das verhindert den Fehler "Operator existiert nicht: character varying = integer"
        names = [str(n) for n in names]

        cursor = self.conn.cursor()
        records = []
        
        try:
            if self.is_sqlite:
                # --- SQLite / Spatialite Logik ---
                # SQLite nutzt '?' als Platzhalter und unterstützt keine Listen direkt im SQL.
                # Wir müssen den String "IN (?,?,?)" dynamisch bauen.
                
                placeholders = ",".join(["?"] * len(names))
                
                # Query: Wähle die Zeile mit dem neuesten Datum pro ID
                # (ROW_NUMBER() wird von modernen SQLite-Versionen unterstützt)
                sql = f"""
                    SELECT * FROM (
                        SELECT *, ROW_NUMBER() OVER (PARTITION BY {name_column} ORDER BY untersuchtag DESC) as rn
                        FROM {table}
                        WHERE {name_column} IN ({placeholders})
                    ) t WHERE rn = 1
                """
                # Bei SQLite übergeben wir die Liste der Parameter direkt für die Platzhalter
                cursor.execute(sql, names)
                
            else:
                # --- PostgreSQL Logik ---
                # Postgres nutzt '%s' und kann Listen (Tuples) verarbeiten via ANY(%s)
                
                sql = f"""
                    SELECT t.*
                    FROM {table} t
                    JOIN (
                        SELECT {name_column}, MAX(untersuchtag) AS max_tag
                        FROM {table}
                        WHERE {name_column} = ANY(%s)
                        GROUP BY {name_column}
                    ) max_dates
                    ON t.{name_column} = max_dates.{name_column} AND t.untersuchtag = max_dates.max_tag
                    WHERE t.{name_column} = ANY(%s)
                    ORDER BY t.{name_column}, t.untersuchtag DESC
                """
                # Postgres braucht die Parameter als Liste/Tuple für das %s
                # Wir übergeben 'names' zweimal, da es zwei Platzhalter im SQL gibt
                cursor.execute(sql, (names, names))

            # Ergebnisse holen und in Dictionaries umwandeln
            rows = cursor.fetchall()
            if cursor.description:
                colnames = [desc[0] for desc in cursor.description]
                records = [dict(zip(colnames, row)) for row in rows]
            
            return records
            
        except Exception as e:
            # Fehler protokollieren und weiterwerfen, damit das UI reagieren kann
            print(f"Fehler im DatenbankExporter SQL: {e}")
            raise e

    def export_to_excel(self, records, output_path):
        """
        Exportiert eine Liste von Dictionaries in eine Excel-Datei.
        Bereinigt dabei automatisch ungültige Steuerzeichen.
        """
        if not records:
            # Leere Liste ist kein Fehler, wir erstellen einfach keine Datei oder warnen
            raise ValueError("Keine Daten zum Exportieren.")
        
        # 1. Daten bereinigen (Steuerzeichen entfernen)
        cleaned_records = self._clean_data_for_excel(records)
        
        # 2. DataFrame erstellen
        df = pd.DataFrame(cleaned_records)
        
        # 3. Excel schreiben
        try:
            df.to_excel(output_path, index=False)
        except Exception as e:
            raise RuntimeError(f"Fehler beim Schreiben der Excel-Datei: {e}")

    def _clean_data_for_excel(self, records):
        """
        Interne Hilfsmethode: Entfernt Steuerzeichen, die Excel crashen lassen (z.B. ASCII 1).
        """
        # Regex für ungültige XML-Zeichen in Excel (OpenPyXL kompatibel)
        # Entfernt ASCII 0-8, 11-12, 14-31 (Alles außer Tab, LF, CR)
        illegal_chars_re = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

        def clean_value(v):
            if isinstance(v, str):
                return illegal_chars_re.sub('', v)
            return v

        new_records = []
        for rec in records:
            # Neues Dict erstellen mit bereinigten Werten
            new_rec = {k: clean_value(v) for k, v in rec.items()}
            new_records.append(new_rec)
        
        return new_records


class ColumnSelectionOrderDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spalten auswählen und Reihenfolge festlegen")
        self.resize(500, 600) # Etwas mehr Platz

        main_layout = QVBoxLayout(self)

        # ScrollArea für Checkboxen
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        checkbox_container = QWidget()
        scroll.setWidget(checkbox_container)

        # GridLayout für die Checkboxen mit 3 Spalten
        self.checkbox_layout = QGridLayout(checkbox_container)

        self.checkboxes = {}
        columns_per_row = 3  # Anzahl der Checkbox-Spalten

        for idx, col in enumerate(columns):
            row = idx // columns_per_row
            col_pos = idx % columns_per_row
            cb = QCheckBox(col)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_order_list)
            self.checkboxes[col] = cb
            self.checkbox_layout.addWidget(cb, row, col_pos)

        main_layout.addWidget(QLabel("Spalten auswählen:"))
        main_layout.addWidget(scroll)

        # Die untere Reihenfolge-Liste horizontal, drag&drop-fähig
        main_layout.addWidget(QLabel("Reihenfolge anpassen (Drag & Drop):"))
        self.order_list = QListWidget(self)
        self.order_list.setFlow(QListWidget.LeftToRight)
        self.order_list.setWrapping(True) # Wrapping erlaubt mehrzeilige Anzeige bei vielen Spalten
        self.order_list.setDragDropMode(QListWidget.InternalMove)
        self.order_list.setMinimumHeight(100)
        main_layout.addWidget(self.order_list)

        # Buttons OK / Abbrechen
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Abbrechen")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        # Buttons Speichern/Laden
        config_layout = QHBoxLayout()
        save_btn = QPushButton("Konfiguration Speichern")
        load_btn = QPushButton("Konfiguration Laden")

        save_btn.clicked.connect(self.save_configuration)
        load_btn.clicked.connect(self.load_configuration)

        config_layout.addWidget(save_btn)
        config_layout.addWidget(load_btn)

        main_layout.addLayout(btn_layout)
        main_layout.addLayout(config_layout)

        self.update_order_list()

    def update_order_list(self):
        selected = [col for col, cb in self.checkboxes.items() if cb.isChecked()]
        current_items = [self.order_list.item(i).text() for i in range(self.order_list.count())]

        # Entferne Items, die nicht mehr ausgewählt sind
        for i in reversed(range(self.order_list.count())):
            item = self.order_list.item(i)
            if item.text() not in selected:
                self.order_list.takeItem(i)

        # Füge neue hinzu, die ausgewählt sind, aber noch nicht in der Reihenfolge-Liste
        for col in selected:
            if col not in current_items:
                self.order_list.addItem(col)

    def get_selected_columns(self):
        return [self.order_list.item(i).text() for i in range(self.order_list.count())]

    def save_configuration(self):
        config = self.get_selected_columns()  # Die tatsächlich ausgewählten Spalten in Reihenfolge
        fname, _ = QFileDialog.getSaveFileName(self, "Konfiguration speichern", "", "JSON-Datei (*.json)")
        if not fname:
            return
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            QMessageBox.information(self, "Gespeichert", f"Konfiguration erfolgreich gespeichert:\n{fname}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")

    def load_configuration(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Konfiguration laden", "", "JSON-Datei (*.json)")
        if not fname:
            return
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self._apply_configuration(config)
            QMessageBox.information(self, "Geladen", f"Konfiguration erfolgreich geladen:\n{fname}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden: {e}")

    def _apply_configuration(self, selected_columns):
        # Alle Checkboxen erst mal deaktivieren (oder prüfen ob sie existieren)
        existing_cols = self.checkboxes.keys()
        
        # Checkboxen setzen
        for col, cb in self.checkboxes.items():
            cb.blockSignals(True)  # Signale blockieren
            cb.setChecked(col in selected_columns)
            cb.blockSignals(False)

        # Reihenfolgen-Liste aktualisieren
        self.order_list.clear()
        for col in selected_columns:
            if col in existing_cols:
                self.order_list.addItem(col)
        
        # Falls in der Config Spalten fehlen, die aber aktuell in den Daten sind,
        # fügen wir sie am Ende hinzu (oder lassen sie weg, je nach Wunsch. Hier: weg lassen = unchecked)
        self.update_order_list()


class DataTypeSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datentyp für Export wählen")

        layout = QVBoxLayout(self)
        self.rb_haltungen = QRadioButton("Haltungen")
        self.rb_schachte = QRadioButton("Schächte")
        self.rb_gal = QRadioButton("GAL")
        self.rb_haltungen.setChecked(True)

        layout.addWidget(self.rb_haltungen)
        layout.addWidget(self.rb_schachte)
        layout.addWidget(self.rb_gal)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selection(self):
        if self.rb_haltungen.isChecked():
            return "Haltungen"
        elif self.rb_schachte.isChecked():
            return "Schächte"
        elif self.rb_gal.isChecked():
            return "GAL"
