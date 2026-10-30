# netzuebersicht/excel_import_sinkkaesten.py
import os
import json
import pandas as pd
import psycopg2
from PyQt5.QtWidgets import (
    QMessageBox,
    QFileDialog,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDialogButtonBox,
)


def _py(value):
    """numpy-/pandas-Werte in einfache Python-Werte umwandeln (für die DB-Treiber)."""
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return value
    return value


def excel_import_sinkkaesten(self):
    """Excel-Import für Sinkkästen (Postgres & Spatialite kompatibel)."""
    import pandas as pd # Sicherstellen, dass pandas importiert ist
    
    # 1. Verbindung prüfen (Existierende Plugin-Connection nutzen!)
    # Wir bauen KEINE neue Verbindung auf, sondern nutzen self.conn
    if not hasattr(self, 'conn') or self.conn is None:
            QMessageBox.critical(self, "Fehler", "Keine aktive Datenbankverbindung im Plugin.")
            return
            
    # SQL kommt aus sqlite.yml / postgres.yml (über das Backend)
    backend = self.backend

    # 2. Excel-Datei auswählen
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel-Datei auswählen", "", "Excel-Dateien (*.xlsx *.xls);;Alle Dateien (*)"
        )

        if not file_path: return

        df = pd.read_excel(file_path)
        excel_columns = df.columns.tolist()

        # Tiefe bereinigen
        if "Tiefe" in df.columns:
            df["Tiefe"] = df["Tiefe"].astype(str).str.replace(",", ".")
            df["Tiefe"] = pd.to_numeric(df["Tiefe"], errors="coerce")

        # DB-Spalten (Hardcoded Ziel-Spalten)
        db_columns = [
            "Schacht_oben", "Schacht_unten", "Entwässerungssystem", "Baujahr",
            "Straßenname", "Typ", "Tiefe", "Schmutzfänger", "Material",
            "Bemerkung", "aktuellste_Reinigung", "vorherige_Reinigung",
        ]

        # 3. Mapping-Dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Spaltenzuordnung")
        layout = QVBoxLayout(dialog)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name-Spalte (Pflichtfeld):"))
        name_combo = QComboBox()
        name_combo.addItems([""] + excel_columns)
        name_layout.addWidget(name_combo)
        layout.addLayout(name_layout)

        mappings = {}
        for col in db_columns:
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(f"{col}:"))
            combo = QComboBox()
            combo.addItems(["- Nicht importieren -"] + excel_columns)
            mappings[col] = combo
            row_layout.addWidget(combo)
            layout.addLayout(row_layout)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        if dialog.exec_() != QDialog.Accepted: return

        name_col = name_combo.currentText()
        if not name_col:
            QMessageBox.critical(self, "Fehler", "Name-Spalte muss zugeordnet werden!")
            return

        column_mapping = {col: combo.currentText() for col, combo in mappings.items() if combo.currentText() != "- Nicht importieren -"}

        # 4. Import-Logik
        cursor = self.conn.cursor() # Plugin-Cursor nutzen
        
        # Autocommit Handling ist DB-abhängig, wir nutzen Transaktion manuell
        try:
            # Versuchen Transaktion zu starten (falls nicht eh schon in einer)
            pass 
        except: pass

        updated_rows = 0
        skipped_rows = []
        
        # Tabellen-/Spaltennamen in "..." (SQLite und PostgreSQL)
        table_name = backend.ident(backend.get_sinkkaesten_table_name())
        col_name = backend.ident("Name")            # Schlüsselspalte

        for index, row in df.iterrows():
            name_value = _py(row[name_col])
            if pd.isna(name_value):
                skipped_rows.append(index + 2)
                continue

            # Existenz-Check
            backend.execute(cursor, "nz_sk_existiert", (name_value,),
                            tabelle=table_name, schluessel=col_name)
            exists = cursor.fetchone()
            
            if not exists:
                skipped_rows.append(index + 2)
                continue

            # Typ-Logik (X -> Nassschlamm etc.)
            typen = []
            for typ_col in ["Nassschlamm", "Trockenschlamm", "Bergeinlauf"]:
                if typ_col in df.columns and not pd.isna(row[typ_col]):
                    if str(row[typ_col]).strip().upper() == "X":
                        typen.append(typ_col)
            typ_wert = "-".join(typen) if typen else None

            # Werte vorbereiten
            temp_mapping = column_mapping.copy()
            if "Typ" in temp_mapping: temp_mapping["Typ"] = None # Wird manuell gesetzt

            # Reiningungs-Logik (Datum verschieben)
            akt_rein_col = column_mapping.get("aktuellste_Reinigung")
            neue_akt_rein = None
            
            if akt_rein_col:
                cell = row[akt_rein_col]
                if not pd.isna(cell) and str(cell).strip() != "":
                    if hasattr(cell, 'strftime'): neue_akt_rein = cell.strftime("%Y-%m-%d")
                    else: neue_akt_rein = str(cell).strip()

            if neue_akt_rein:
                # Datum verschieben
                col_akt = backend.ident("aktuellste_Reinigung")
                col_vor = backend.ident("vorherige_Reinigung")

                backend.execute(cursor, "nz_sk_wert_lesen", (name_value,),
                                tabelle=table_name, spalte=col_akt, schluessel=col_name)
                res = cursor.fetchone()
                bisherige_rein = res[0] if res else None

                if bisherige_rein and str(bisherige_rein) != neue_akt_rein:
                    backend.execute(cursor, "nz_sk_reinigung_verschieben",
                                    (bisherige_rein, neue_akt_rein, name_value),
                                    tabelle=table_name, spalte_vor=col_vor,
                                    spalte_akt=col_akt, schluessel=col_name)
                    if cursor.rowcount > 0: updated_rows += 1

            # Haupt-Update
            set_spalten = []
            values = []
            
            for db_col, excel_col in temp_mapping.items():
                val = None
                
                if db_col == "Typ":
                    val = typ_wert
                elif db_col in ["aktuellste_Reinigung", "vorherige_Reinigung"]:
                    # Schon oben behandelt oder einfacher Wert
                    cell = row[excel_col] if excel_col else None
                    if not pd.isna(cell) and str(cell).strip() != "":
                            if hasattr(cell, 'strftime'): val = cell.strftime("%Y-%m-%d")
                            else: val = str(cell).strip()
                elif db_col == "Tiefe" and excel_col:
                        cell = row[excel_col]
                        if not pd.isna(cell):
                            try: val = float(str(cell).replace(",", "."))
                            except: val = None
                else:
                    if excel_col:
                        val = row[excel_col] if not pd.isna(row[excel_col]) else None

                # Clause bauen
                if excel_col is not None or db_col == "Typ":
                        set_spalten.append(db_col)
                        values.append(val)

            if set_spalten:
                values = [_py(v) for v in values]
                values.append(name_value)
                backend.execute(cursor, "nz_update_objekt", values,
                                tabelle=table_name,
                                zuweisungen=backend.zuweisungen(set_spalten),
                                schluessel=col_name)
                if cursor.rowcount > 0: updated_rows += 1

        self.conn.commit()

        msg = f"Import fertig.\nAktualisiert: {updated_rows}\nÜbersprungen: {len(skipped_rows)}"
        QMessageBox.information(self, "Erfolg", msg)

        if hasattr(self, "model_sinkkaesten"):
            from .table_models import modell_vollstaendig_laden
            modell_vollstaendig_laden(self.model_sinkkaesten)

    except Exception as e:
        if hasattr(self, 'conn'): self.conn.rollback()
        QMessageBox.critical(self, "Fehler", f"Import fehlgeschlagen:\n{str(e)}")

