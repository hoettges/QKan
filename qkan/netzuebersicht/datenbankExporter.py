# qkan/netzuebersicht/datenbankExporter.py
"""
Hilfsklassen für den Export von Untersuchungsdaten (export_investigations.py):

- DatenbankExporter           Excel-Export (bereinigt Steuerzeichen)
- ColumnSelectionOrderDialog  Spaltenauswahl und -reihenfolge, als JSON speicher-/ladbar
- DataTypeSelectionDialog     Auswahl Haltungen / Schächte / GAL

Das SQL für get_latest_investigations kommt wie im übrigen Modul aus
sqlite.yml bzw. postgres.yml (Schlüssel nz_export_aktuell).
"""
import json
import re

import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QWidget,
    QListWidget, QLabel, QScrollArea, QGridLayout, QFileDialog, QMessageBox,
    QRadioButton, QDialogButtonBox
)

from . import db_sql


class DatenbankExporter:
    def __init__(self, connection):
        """
        Initialisiert den Exporter mit einer bestehenden Datenbankverbindung.

        Args:
            connection: Ein offenes Verbindungsobjekt (sqlite3/SpatiaLite oder psycopg2)
        """
        self.conn = connection
        self.db_type = db_sql.normalize_dbtype(conn=connection)
        self.is_sqlite = self.db_type == db_sql.DBTYPE_SPATIALITE

    def get_latest_investigations(self, table, name_column, names):
        """
        Holt alle Datensätze mit dem jeweils aktuellsten untersuchtag pro Name
        (SQL: nz_export_aktuell aus sqlite.yml / postgres.yml).

        Args:
            table (str): Name der Tabelle
            name_column (str): Spaltenname für die ID/den Namen
            names (list): Liste der IDs/Namen, nach denen gefiltert werden soll
        """
        if not names:
            return []

        # Alle Namen als Text übergeben (verhindert in PostgreSQL
        # "Operator existiert nicht: character varying = integer")
        names = [str(n) for n in names]

        sql = db_sql.get_sql(
            self.db_type,
            "nz_export_aktuell",
            lambda s: s.format(
                tabelle=db_sql.ident(table),
                spalte=db_sql.ident(name_column),
                platzhalter=db_sql.platzhalter(self.db_type, len(names)),
            ),
        )

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, names)
            rows = cursor.fetchall()
            if not cursor.description:
                return []
            colnames = [desc[0] for desc in cursor.description]
            return [dict(zip(colnames, row)) for row in rows]
        except Exception as e:
            print(f"Fehler im DatenbankExporter SQL: {e}")
            raise
        finally:
            cursor.close()

    def export_to_excel(self, records, output_path):
        """
        Exportiert eine Liste von Dictionaries in eine Excel-Datei.
        Bereinigt dabei automatisch ungültige Steuerzeichen.
        """
        if not records:
            raise ValueError("Keine Daten zum Exportieren.")

        cleaned_records = self._clean_data_for_excel(records)
        df = pd.DataFrame(cleaned_records)

        try:
            df.to_excel(output_path, index=False)
        except Exception as e:
            raise RuntimeError(f"Fehler beim Schreiben der Excel-Datei: {e}")

    def _clean_data_for_excel(self, records):
        """
        Entfernt Steuerzeichen, die Excel/openpyxl nicht verarbeiten kann
        (ASCII 0-8, 11-12, 14-31; Tab, LF und CR bleiben erhalten).
        """
        illegal_chars_re = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

        def clean_value(v):
            if isinstance(v, str):
                return illegal_chars_re.sub('', v)
            return v

        return [{k: clean_value(v) for k, v in rec.items()} for rec in records]


class ColumnSelectionOrderDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spalten auswählen und Reihenfolge festlegen")
        self.resize(500, 600)

        main_layout = QVBoxLayout(self)

        # ScrollArea für Checkboxen
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        checkbox_container = QWidget()
        scroll.setWidget(checkbox_container)

        # GridLayout für die Checkboxen mit 3 Spalten
        self.checkbox_layout = QGridLayout(checkbox_container)

        self.checkboxes = {}
        columns_per_row = 3

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

        # Reihenfolge-Liste (Drag & Drop)
        main_layout.addWidget(QLabel("Reihenfolge anpassen (Drag & Drop):"))
        self.order_list = QListWidget(self)
        self.order_list.setFlow(QListWidget.LeftToRight)
        self.order_list.setWrapping(True)
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

        # Nicht mehr ausgewählte Einträge entfernen
        for i in reversed(range(self.order_list.count())):
            if self.order_list.item(i).text() not in selected:
                self.order_list.takeItem(i)

        # Neu ausgewählte Einträge anhängen
        for col in selected:
            if col not in current_items:
                self.order_list.addItem(col)

    def get_selected_columns(self):
        return [self.order_list.item(i).text() for i in range(self.order_list.count())]

    def save_configuration(self):
        config = self.get_selected_columns()
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
        existing_cols = self.checkboxes.keys()

        # Checkboxen setzen, ohne update_order_list je Box auszulösen
        for col, cb in self.checkboxes.items():
            cb.blockSignals(True)
            cb.setChecked(col in selected_columns)
            cb.blockSignals(False)

        # Reihenfolge aus der Konfiguration übernehmen
        self.order_list.clear()
        for col in selected_columns:
            if col in existing_cols:
                self.order_list.addItem(col)

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
