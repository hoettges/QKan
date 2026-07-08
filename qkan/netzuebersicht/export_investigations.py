# netzuebersicht/export_investigations.py
import re
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from .datenbankExporter import (
    DatenbankExporter,
    ColumnSelectionOrderDialog,
    DataTypeSelectionDialog,
)
from qgis.utils import iface

def export_latest_investigations(self):
    try:
        # 1. DB-Verbindung prüfen
        if not hasattr(self, 'conn') or self.conn is None:
                QMessageBox.critical(self, "Fehler", "Keine Datenbankverbindung gefunden.")
                return
        
        # --- FIX: Automatische Erkennung des Datenbank-Typs ---
        conn_type_str = str(type(self.conn)).lower()
        is_spatialite = 'sqlite' in conn_type_str or 'spatialite' in conn_type_str
        # ------------------------------------------------------

        # 2. ABFRAGE: QUELLE DER AUSWAHL
        quellen = ["Selektierte Objekte im Layer (Karte)", "Markierte Zeilen in Tabelle (Liste)"]
        quelle, ok = QInputDialog.getItem(
            self, 
            "Auswahlbasis", 
            "Woher soll die Auswahl genommen werden?", 
            quellen, 
            0, 
            False
        )
        if not ok: return
        
        from_layer = (quelle == quellen[0])

        # 3. Datentyp auswählen (Haltungen, Schächte, GAL)
        dialog = DataTypeSelectionDialog(self)
        if dialog.exec_() != dialog.Accepted:
            return

        selection = dialog.get_selection()

        tabellen_mapping = {
            "Haltungen": (
                "untersuchdat_haltung", "untersuchhal", "haltnam", "haltungen", "haltnam", 
                getattr(self, "tableView_Haltungen", None)
            ),
            "Schächte": (
                "untersuchdat_schacht", "untersuchsch", "schoben", "schaechte", "schnam",
                getattr(self, "tableView_Schaechte", None)
            ),
            "GAL": (
                "untersuchdat_anschlussleitung", "untersuchleit", "leitnam", "anschlussleitungen", "leitnam",
                getattr(self, "tableView_GAL", None)
            ),
        }
        
        raw_table, column, layer_attr, raw_obj_table, obj_key, table_widget = tabellen_mapping[selection]
        
        # Tabellennamen vorbereiten
        table = raw_table if is_spatialite else f'"{raw_table}"'
        obj_table = raw_obj_table if is_spatialite else f'"{raw_obj_table}"'

        # 4. NAMEN EINSAMMELN
        names_for_untersuchung = []

        if from_layer:
            # --- VARIANTE A: LAYER ---
            layer = iface.activeLayer()
            if not layer:
                    QMessageBox.warning(self, "Fehler", "Kein aktiver Layer ausgewählt.")
                    return
                    
            selected_features = layer.selectedFeatures()
            if not selected_features:
                QMessageBox.warning(self, "Info", "Keine Objekte im Layer selektiert.")
                return

            for feat in selected_features:
                if layer_attr in feat.fields().names():
                    val = feat.attribute(layer_attr)
                    if val is not None and val != "":
                        val_str = str(val)
                        if val_str not in names_for_untersuchung:
                            names_for_untersuchung.append(val_str)
        else:
            # --- VARIANTE B: TABELLE ---
            if table_widget is None:
                QMessageBox.critical(self, "Fehler", f"Tabelle für {selection} nicht gefunden.")
                return
            
            selection_model = table_widget.selectionModel()
            if not selection_model.hasSelection():
                    QMessageBox.warning(self, "Info", "Keine Zeilen in der Tabelle markiert.")
                    return
                    
            selected_rows = selection_model.selectedRows()
            proxy_model = table_widget.model()
            
            # Spalte finden (Header-Suche)
            key_col_idx = -1
            check_model = proxy_model
            if hasattr(check_model, 'sourceModel'):
                check_model = check_model.sourceModel()

            possible_names = [obj_key, layer_attr, obj_key.lower(), layer_attr.lower()]
            
            for c in range(check_model.columnCount()):
                header_val = check_model.headerData(c, 1, 0)
                if str(header_val) in possible_names:
                    key_col_idx = c
                    break
            
            # Fallback über Record fields
            if key_col_idx == -1 and hasattr(check_model, 'record'):
                rec = check_model.record()
                idx = rec.indexOf(obj_key)
                if idx == -1: idx = rec.indexOf(layer_attr)
                if idx != -1: key_col_idx = idx

            if key_col_idx == -1:
                key_col_idx = 0 # Fallback auf erste Spalte

            for proxy_idx in selected_rows:
                if hasattr(proxy_model, 'mapToSource'):
                    source_idx = proxy_model.mapToSource(proxy_idx)
                    model = proxy_model.sourceModel()
                else:
                    source_idx = proxy_idx
                    model = proxy_model
                
                idx_name = source_idx.sibling(source_idx.row(), key_col_idx)
                val = model.data(idx_name)
                
                if val is not None and val != "":
                    val_str = str(val) 
                    if val_str not in names_for_untersuchung:
                        names_for_untersuchung.append(val_str)

        if not names_for_untersuchung:
            source_name = "Layer" if from_layer else "Tabelle"
            QMessageBox.warning(self, "Keine Auswahl", f"Konnte keine gültigen Namen aus {source_name} ermitteln.")
            return

        # 5. ABFRAGE: EXPORTMODUS (3 Optionen)
        modi = [
            "Vollständige Historie (Alle Berichte aller Jahre)",
            "Aktuellster Bericht (Alle Zeilen des neuesten Datums)",
            "Einzelner Eintrag (Nur eine Zeile pro Objekt vom neuesten Datum)"
        ]
        
        modus_text, ok = QInputDialog.getItem(
            self,
            "Exportmodus",
            "Welche Daten sollen exportiert werden?",
            modi,
            1, # Default: Aktuellster Bericht (Alle Zeilen)
            False,
        )
        if not ok: return

        # ---------------------------------------------------------
        # DB-ABFRAGE & EXPORT
        # ---------------------------------------------------------
        exporter = DatenbankExporter(self.conn) 
        cursor = self.conn.cursor()
        records = []
        
        # --- SQL Logik ---
        
        # 1. MODUS: Vollständige Historie
        if modus_text == modi[0]:
            if is_spatialite:
                    placeholders = ','.join(['?'] * len(names_for_untersuchung))
                    sql = f"SELECT * FROM {table} WHERE {column} IN ({placeholders})"
                    cursor.execute(sql, names_for_untersuchung)
            else:
                    sql = f"SELECT * FROM {table} WHERE {column} = ANY(%s)"
                    cursor.execute(sql, (names_for_untersuchung,))

        # 2. MODUS: Aktuellster Bericht (Alle Zeilen)
        elif modus_text == modi[1]:
            if is_spatialite:
                placeholders = ','.join(['?'] * len(names_for_untersuchung))
                sql = f"""
                    SELECT t1.* 
                    FROM {table} t1
                    JOIN (
                        SELECT {column}, MAX(untersuchtag) as maxtag
                        FROM {table}
                        WHERE {column} IN ({placeholders})
                        GROUP BY {column}
                    ) t2 ON t1.{column} = t2.{column} AND t1.untersuchtag = t2.maxtag
                """
                cursor.execute(sql, names_for_untersuchung * 2) # Parameter verdoppeln für Subquery und Join? Nein, hier nur für Subquery nötig, aber Join ist on values.
                # KORREKTUR für SQLite Parameter:
                # Im obigen SQL wird {placeholders} nur EINMAL verwendet (im Subquery).
                # Also reicht `names_for_untersuchung` einmal.
                cursor.execute(sql, names_for_untersuchung)
            else:
                # Postgres
                sql = f"""
                    SELECT t1.* 
                    FROM {table} t1
                    JOIN (
                        SELECT {column}, MAX(untersuchtag) as maxtag
                        FROM {table}
                        WHERE {column} = ANY(%s)
                        GROUP BY {column}
                    ) t2 ON t1.{column} = t2.{column} AND t1.untersuchtag = t2.maxtag
                """
                cursor.execute(sql, (names_for_untersuchung,))

        # 3. MODUS: Einzelner Eintrag (Nur 1 Zeile, Row Number = 1)
        else:
            if is_spatialite:
                placeholders = ','.join(['?'] * len(names_for_untersuchung))
                try:
                    sql = f"""
                        SELECT * FROM (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY {column} ORDER BY untersuchtag DESC) AS rn
                            FROM {table}
                            WHERE {column} IN ({placeholders})
                        ) t WHERE rn = 1
                    """
                    cursor.execute(sql, names_for_untersuchung)
                except:
                        # Fallback für sehr alte SQLite ohne Window Functions
                        # Trick: Group By wählt in SQLite einen beliebigen (oft den ersten) Datensatz
                        sql = f"""
                        SELECT * FROM {table}
                        WHERE {column} IN ({placeholders})
                        GROUP BY {column}
                        HAVING untersuchtag = MAX(untersuchtag)
                        """
                        cursor.execute(sql, names_for_untersuchung)
            else:
                # Postgres
                sql = f"""
                    SELECT * FROM (
                        SELECT *, ROW_NUMBER() OVER (PARTITION BY {column} ORDER BY untersuchtag DESC) AS rn
                        FROM {table}
                        WHERE {column} = ANY(%s)
                    ) t WHERE rn = 1
                """
                cursor.execute(sql, (names_for_untersuchung,))

        # --- Fetching ---
        rows = cursor.fetchall()
        if cursor.description:
            colnames = [desc[0] for desc in cursor.description]
            records = [dict(zip(colnames, row)) for row in rows]

        if not records:
            QMessageBox.warning(self, "Keine Daten", "Keine Daten für die Auswahl gefunden.")
            return

        # --- Zusatzdaten holen ---
        vorhandene_keys = set(rec[column] for rec in records if column in rec and rec[column] is not None)
        fehlende_keys = [k for k in names_for_untersuchung if k not in vorhandene_keys]
        zusatz_spalten = ["eigentum", "strasse", "material"]

        if names_for_untersuchung:
            # Spaltenprüfung
            if is_spatialite:
                    cursor.execute(f"PRAGMA table_info({raw_obj_table})")
                    cols_info = cursor.fetchall()
                    vorhandene_spalten = [c[1].lower() for c in cols_info]
            else:
                    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (raw_obj_table,))
                    vorhandene_spalten = [row[0].lower() for row in cursor.fetchall()]

            spalten_abruf = [sp for sp in zusatz_spalten if sp in vorhandene_spalten]

            if spalten_abruf:
                spalten_str = ", ".join(spalten_abruf)
                if is_spatialite:
                        placeholders = ','.join(['?'] * len(names_for_untersuchung))
                        sql_obj = f"SELECT {obj_key}, {spalten_str} FROM {obj_table} WHERE {obj_key} IN ({placeholders})"
                        params_obj = names_for_untersuchung
                else:
                        sql_obj = f"SELECT {obj_key}, {spalten_str} FROM {obj_table} WHERE {obj_key} = ANY(%s)"
                        params_obj = (names_for_untersuchung,)

                cursor.execute(sql_obj, params_obj)
                obj_daten = cursor.fetchall()
                col_names = [obj_key] + spalten_abruf
                obj_map = {row[0]: dict(zip(col_names[1:], row[1:])) for row in obj_daten}

                for rec in records:
                    key = rec.get(column)
                    if key in obj_map:
                        for sp in spalten_abruf:
                            rec[sp] = obj_map[key].get(sp, None)

                # Fehlende Keys auffüllen
                if fehlende_keys:
                    if is_spatialite:
                            ph_fehl = ','.join(['?'] * len(fehlende_keys))
                            sql_fehl = f"SELECT {obj_key}, {spalten_str} FROM {obj_table} WHERE {obj_key} IN ({ph_fehl})"
                            params_fehl = fehlende_keys
                    else:
                            sql_fehl = f"SELECT {obj_key}, {spalten_str} FROM {obj_table} WHERE {obj_key} = ANY(%s)"
                            params_fehl = (fehlende_keys,)
                    
                    cursor.execute(sql_fehl, params_fehl)
                    fehl_obj_daten = cursor.fetchall()
                    fehl_col_names = [obj_key] + spalten_abruf
                    fehl_obj_map = {row[0]: dict(zip(fehl_col_names[1:], row[1:])) for row in fehl_obj_daten}
                    
                    for fk in fehlende_keys:
                        ersatz = {column: fk}
                        if fk in fehl_obj_map:
                            ersatz.update(fehl_obj_map[fk])
                        records.append(ersatz)

        # --- Excel Export ---
        basis_spalten = [k for k in records[0].keys() if k not in zusatz_spalten]
        alle_spalten = basis_spalten + [sp for sp in zusatz_spalten if sp in records[0]]

        col_dialog = ColumnSelectionOrderDialog(alle_spalten, self)
        if col_dialog.exec_() != col_dialog.Accepted:
            return

        selected_columns = col_dialog.get_selected_columns()
        if not selected_columns: return

        filtered_records = [{k: r.get(k, None) for k in selected_columns} for r in records]

        out_path, _ = QFileDialog.getSaveFileName(self, "Excel speichern", "", "Excel-Datei (*.xlsx)")
        if out_path:
            exporter.export_to_excel(filtered_records, out_path)
            QMessageBox.information(self, "Export", f"Export erfolgreich nach {out_path}.")

        if fehlende_keys:
            fehlende_objekte_str = "\n".join(map(str, fehlende_keys))
            QMessageBox.information(self, "Info", f"Keine Untersuchungsdaten für:\n{fehlende_objekte_str}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        QMessageBox.critical(self, "Fehler", str(e))




