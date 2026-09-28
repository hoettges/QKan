"""
data_queries.py - Datenabfragen und Tabellen-Handling für QGIS-Plugin Datenbankviewer
Enthält SQL-Abfragen, Edit-Modus, Speichern von Änderungen und Tab-Management.
"""

import psycopg2
import sqlite3
from collections import defaultdict
from PyQt6.QtWidgets import QMessageBox, QTableWidget, QTabWidget, QWidget, QTableWidgetItem, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from qgis.utils import iface

# --- HILFSFUNKTIONEN FÜR DATENBANK-ABSTRAKTION ---

def get_db_context(parent_dialog):
    """Liefert connection, cursor und den passenden Platzhalter ('%s' oder '?') zurück."""
    db_type = getattr(parent_dialog, 'db_type', 'postgres')
    
    if db_type == 'postgres':
        # ✅ HIER IMPORTIEREN
        from .db_connection import loadpostgresconnection
        conn = loadpostgresconnection(parent_dialog)
        if conn is None:
            return None, None, None
        cursor = conn.cursor()
        try:
            cursor.execute("SET search_path TO public;")
        except Exception:
            pass
        return conn, cursor, "%s"
        
    else: # spatialite
        # ✅ HIER IMPORTIEREN
        from ..netzuebersicht.db_backend import get_backend
        backend = get_backend('spatialite')
        conn, cursor, _ = backend.load_native_connection(parent=parent_dialog)
        if conn is None:
            return None, None, None
        conn.row_factory = sqlite3.Row
        return conn, cursor, "?"

def get_untersuch_columns(self, dbtable):
    conn, cursor, param_style = get_db_context(self)
    if not conn:
        return []

    try:
        # Dummy-Select, um Spaltennamen zu bekommen
        cursor.execute(f"SELECT * FROM {dbtable} LIMIT 1")
        cols = [desc[0] for desc in cursor.description]
        return cols
    except Exception:
        return []
    finally:
        cursor.close()
        if getattr(self, 'db_type', 'postgres') == 'postgres':
            conn.close()


# --- ABFRAGE & GUI-AUFBAU ---

def SQLAbfrage(self):
    """Führt SQL-Abfragen aus (DB-agnostisch, intern + extern) und befüllt Tabellen."""
    conn, cursor, param_style = get_db_context(self)
    if not conn:
        return

    tablenames = {
        'Haltungen': 'untersuchdat_haltung',
        'Schächte': 'untersuchdat_schacht', 
        'GAL': 'untersuchdat_anschlussleitung'
    }
    
    columns = {
        'Haltungen': ["station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                    "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
                    "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"],
        'Schächte': ["vertikale_lage", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                    "quantnr1", "quantnr2", "pos_von", "pos_bis", "bereich", "zd", "zs", "zb",
                    "bandnr", "untersuchtag", "videozaehler", "foto_dateiname"],
        'GAL': ["station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
                "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"]
    }
    
    # ✅ EXTERNAL MODE + INTERN MODE in EINER Funktion!
    is_external = getattr(self, 'external_mode', False)
    
    if is_external:
        # External: Dict aus get_external_feature verwenden
        feature = self.get_external_feature()
        if feature is None:
            cursor.close()
            conn.close()
            return
        haltnam_value = feature.get('haltnam')
        schoben_value = feature.get('schoben')
        leitnam_value = feature.get('leitnam')
    else:
        # Intern: QGIS Layer verwenden
        layer = iface.activeLayer()
        if layer is None or len(layer.selectedFeatureIds()) == 0:
            QMessageBox.warning(self, "Auswahlfehler", "Bitte wählen Sie ein passendes Feature aus.")
            cursor.close()
            conn.close()
            return
        
        qgis_feature = layer.getFeature(layer.selectedFeatureIds()[0])
        field_names = qgis_feature.fields().names()
        haltnam_value = qgis_feature['haltnam'] if 'haltnam' in field_names else None
        schoben_value = qgis_feature['schoben'] if 'schoben' in field_names else None
        leitnam_value = qgis_feature['leitnam'] if 'leitnam' in field_names else None
    
    date_tabs = {'Haltungen': defaultdict(list), 'Schächte': defaultdict(list), 'GAL': defaultdict(list)}
    
    for tab_name, table in tablenames.items():
        if tab_name == 'Haltungen' and haltnam_value:
            column, value, orderby = 'untersuchhal', haltnam_value, 'station'
        elif tab_name == 'Schächte' and schoben_value:
            column, value, orderby = 'untersuchsch', schoben_value, 'vertikale_lage'
        elif tab_name == 'GAL' and leitnam_value:
            column, value, orderby = 'untersuchleit', leitnam_value, 'station'
        else:
            continue
        
        cols = ['pk'] + columns[tab_name]
        
        # COLLATE "C" nur für Postgres Strings
        if getattr(self, 'db_type', 'postgres') == 'postgres' and orderby not in ['station', 'vertikale_lage', 'pos_von', 'pos_bis', 'quantnr1', 'quantnr2', 'videozaehler', 'bandnr']:
            orderclause = f"ORDER BY {orderby} COLLATE \"C\""
        else:
            orderclause = f"ORDER BY {orderby}"
        
        query = f"SELECT {', '.join(cols)} FROM {table} WHERE {column} = {param_style}"
        if tab_name == 'Haltungen':
            query += " AND (kuerzel != 'K' OR kuerzel IS NULL)"
        query += f" {orderclause}"
        
        try:
            cursor.execute(query, (value,))
            rows_raw = cursor.fetchall()
            
            # Einheitliche Dict-Konvertierung (case-insensitive)
            col_names = [desc[0].lower() for desc in cursor.description]
            for row_tuple in rows_raw:
                if isinstance(row_tuple, dict):
                    row_dict = {k.lower(): v for k, v in row_tuple.items()}
                elif hasattr(row_tuple, 'keys'):  # sqlite3.Row
                    row_dict = {k.lower(): row_tuple[k] for k in row_tuple.keys()}
                else:  # tuple
                    row_dict = dict(zip(col_names, row_tuple))
                
                date_tabs[tab_name][row_dict.get('untersuchtag')].append(row_dict)
                
        except Exception as e:
            QMessageBox.warning(self, "Datenbankfehler", f"Fehler in {table}: {e}")
            cursor.close()
            conn.close()
            return
    
    cursor.close()
    conn.close()
    
    # --- GUI AUFBAU (100% DB-agnostisch, identisch für intern+extern) ---
    self.tabWidget.clear()
    farben = {0: 'red', 1: 'yellow', 2: 'blue', 3: 'lightgreen', 4: 'green'}
    
    for tab_name, tab_data in date_tabs.items():
        schacht_tab = QTabWidget()
        cols = columns[tab_name]
        idx_zd = cols.index("zd") if "zd" in cols else -1
        idx_zs = cols.index("zs") if "zs" in cols else -1
        idx_zb = cols.index("zb") if "zb" in cols else -1
        idx_kuerzel = cols.index("kuerzel")

        for date, rows in sorted(tab_data.items(), reverse=True):
            date_table = QTableWidget()
            date_table.setUpdatesEnabled(False)
            date_table.setColumnCount(len(cols) + 2)
            date_table.setHorizontalHeaderLabels(["pk"] + cols + ["Videoname"])
            date_table.setRowCount(len(rows))
            date_table.setColumnHidden(0, True)

            for i, row in enumerate(rows):
                pk_item = QTableWidgetItem()
                pk_item.setData(Qt.UserRole, row.get('pk'))
                date_table.setItem(i, 0, pk_item)

                for j, col_name in enumerate(cols):
                    val = row.get(col_name)
                    date_table.setItem(i, j + 1, QTableWidgetItem(str(val) if val is not None else ""))

                band_str = str(row.get('bandnr') or 0).zfill(5)
                vid_str = str(row.get('videozaehler') or 0).zfill(5)
                date_table.setItem(i, len(cols) + 1, QTableWidgetItem(band_str + vid_str))

                # Farblogik
                z_werte = []
                for col_idx in (idx_zd, idx_zs, idx_zb):
                    if 0 <= col_idx < len(cols):
                        val = row.get(cols[col_idx])
                        try:
                            val_int = int(val) if val is not None else None
                            if val_int is not None and val_int in farben:
                                z_werte.append(val_int)
                        except (ValueError, TypeError): pass
                
                min_z = min(z_werte) if z_werte else None
                kuerzel_item = date_table.item(i, idx_kuerzel + 1)
                if min_z is not None and min_z in farben and kuerzel_item:
                    kuerzel_item.setForeground(QColor(farben[min_z]))
                
                for col_idx in (idx_zd, idx_zs, idx_zb):
                    if 0 <= col_idx < len(cols):
                        val = row.get(cols[col_idx])
                        item = date_table.item(i, col_idx + 1)
                        if item:
                            try:
                                val_int = int(val) if val is not None else None
                                if val_int is not None and val_int in farben:
                                    item.setForeground(QColor(farben[val_int]))
                                elif val is None:
                                    item.setForeground(QColor("black"))
                            except (ValueError, TypeError): pass

            date_table.setSelectionBehavior(QTableWidget.SelectRows)
            date_table.setSelectionMode(QTableWidget.SingleSelection)
            date_table.setEditTriggers(QTableWidget.AllEditTriggers)
            date_table.setUpdatesEnabled(True)
            schacht_tab.addTab(date_table, str(date))

        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.addWidget(schacht_tab)
        self.tabWidget.addTab(tab_widget, tab_name)


# --- SAVE & DELETE (DB-agnostisch) ---

def save_changes_to_database(self, tablewidget):
    """Speichert: INSERT (PK=None) + UPDATE (DB-agnostisch)."""
    reply = QMessageBox.question(self, "Änderungen speichern", "Speichern?", QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes:
        return

    maintabname = self.tabWidget.tabText(self.tabWidget.currentIndex())
    tablenames = {'Haltungen': 'untersuchdat_haltung', 'Schächte': 'untersuchdat_schacht', 'GAL': 'untersuchdat_anschlussleitung'}
    dbtable = tablenames.get(maintabname)
    if not dbtable:
        return

    headers = [tablewidget.horizontalHeaderItem(i).text() for i in range(tablewidget.columnCount())]
    dbcols = headers[1:-1]
    
    conn, cursor, param_style = get_db_context(self)
    if not conn:
        return

    new_rows = updated_rows = 0
    is_postgres = getattr(self, 'db_type', 'postgres') == 'postgres'

    try:
        for row in range(tablewidget.rowCount()):
            pkitem = tablewidget.item(row, 0)
            pkvalue = pkitem.data(Qt.UserRole)

            update_items = {col: tablewidget.item(row, i+1).text().strip() or None 
                          for i, col in enumerate(dbcols) if tablewidget.item(row, i+1)}
            update_items = {k: v for k, v in update_items.items() if v is not None}
            
            if not update_items:
                continue

            if pkvalue is None:
                # INSERT
                key_col_map = {'Haltungen': 'haltnam', 'Schächte': 'schoben', 'GAL': 'leitnam'}
                key_col = key_col_map[maintabname]
                untersuch_col = {'Haltungen': 'untersuchhal', 'Schächte': 'untersuchsch', 'GAL': 'untersuchleit'}[maintabname]

                if getattr(self, 'external_mode', False):
                    feature = self.get_external_feature()
                    key_value = str(feature.get(key_col)) if feature and feature.get(key_col) else None
                else:
                    layer = iface.activeLayer()
                    if not layer or not layer.selectedFeatureIds(): continue
                    feature = layer.getFeature(layer.selectedFeatureIds()[0])
                    key_value = str(feature[key_col]) if key_col in feature.fields().names() and feature[key_col] else None

                if not key_value: continue

                safe_cols = [untersuch_col] + list(update_items.keys())
                safe_vals = [key_value] + list(update_items.values())
                placeholders = ', '.join([param_style] * len(safe_cols))
                
                if is_postgres:
                    query = f"INSERT INTO {dbtable} ({', '.join(safe_cols)}) VALUES ({placeholders}) RETURNING pk"
                    cursor.execute(query, safe_vals)
                    pkitem.setData(Qt.UserRole, cursor.fetchone()[0])
                else:
                    query = f"INSERT INTO {dbtable} ({', '.join(safe_cols)}) VALUES ({placeholders})"
                    cursor.execute(query, safe_vals)
                    pkitem.setData(Qt.UserRole, cursor.lastrowid)
                new_rows += 1

            else:
                # UPDATE
                setclause = ', '.join([f"{col}={param_style}" for col in update_items])
                query = f"UPDATE {dbtable} SET {setclause} WHERE pk={param_style}"
                params = list(update_items.values()) + [pkvalue]
                cursor.execute(query, params)
                if cursor.rowcount > 0:
                    updated_rows += 1

        conn.commit()
        QMessageBox.information(self, "✓ Erfolg", f"{new_rows} neu + {updated_rows} aktualisiert!")

    except Exception as e:
        conn.rollback()
        QMessageBox.critical(self, "✗ Fehler", f"{type(e).__name__}: {e}")
    finally:
        cursor.close()
        if is_postgres: conn.close()

def delete_record_from_db(pk_value, tablewidget, parent_dialog):
    """Löscht DB-Record per PK (DB-agnostisch)."""
    maintabname = parent_dialog.tabWidget.tabText(parent_dialog.tabWidget.currentIndex())
    dbtable = {'Haltungen': 'untersuchdat_haltung', 'Schächte': 'untersuchdat_schacht', 'GAL': 'untersuchdat_anschlussleitung'}.get(maintabname)
    if not dbtable: return

    conn, cursor, param_style = get_db_context(parent_dialog)
    if not conn: return

    try:
        cursor.execute(f"DELETE FROM {dbtable} WHERE pk = {param_style}", (pk_value,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        QMessageBox.warning(parent_dialog, "DB-Fehler", f"Löschen fehlgeschlagen:\n{str(e)}")
    finally:
        cursor.close()
        if getattr(parent_dialog, 'db_type', 'postgres') == 'postgres': conn.close()

# --- HELPER / UI EVENTS ---

def toggleeditmode(self):
    currenttabwidget = self.tabWidget.currentWidget()
    innertabwidget = currenttabwidget.findChild(QTabWidget)
    tablewidget = find_inner_table_widget(innertabwidget.currentWidget()) if innertabwidget and innertabwidget.currentWidget() else None
    
    if not tablewidget:
        QMessageBox.warning(self, "Fehler", "Konnte die Tabelle nicht finden.")
        return
    
    self.editmode = not getattr(self, 'editmode', False)
    if self.editmode:
        self.edit_button.setText("Änderungen speichern")
        tablewidget.setEditTriggers(QTableWidget.AllEditTriggers)
    else:
        self.edit_button.setText("Bearbeiten aktivieren")
        tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
        save_changes_to_database(self, tablewidget)

def find_inner_table_widget(widget):
    if isinstance(widget, QTableWidget): return widget
    if isinstance(widget, QTabWidget) and widget.currentWidget(): return find_inner_table_widget(widget.currentWidget())
    tables = widget.findChildren(QTableWidget) if widget else []
    return next((t for t in tables if t.isVisible()), tables[0] if tables else None)

def add_row_to_table(tablewidget, columns, parent_dialog=None):
    row_count = tablewidget.rowCount()
    tablewidget.insertRow(row_count)
    pk_item = QTableWidgetItem()
    pk_item.setData(Qt.UserRole, None)
    tablewidget.setItem(row_count, 0, pk_item)
    
    if row_count > 0:
        for col_name, val in [('untersuchtag', ''), ('film_dateiname', '')]:
            if col_name in columns:
                idx = columns.index(col_name) + 1
                template = tablewidget.item(0, idx)
                if template and template.text(): tablewidget.setItem(row_count, idx, QTableWidgetItem(template.text()))
        if 'kuerzel' in columns:
            tablewidget.setItem(row_count, columns.index('kuerzel') + 1, QTableWidgetItem('BCA'))
    
    for j in range(1, tablewidget.columnCount()):
        if tablewidget.item(row_count, j) is None: tablewidget.setItem(row_count, j, QTableWidgetItem(""))
    tablewidget.scrollToBottom()

def delete_selected_rows(tablewidget, parent_dialog):
    selected_items = tablewidget.selectedItems()
    if not selected_items:
        QMessageBox.warning(parent_dialog, "Fehler", "Keine Zeile selektiert.")
        return
    
    selected_rows = list(set(item.row() for item in selected_items))
    if QMessageBox.question(parent_dialog, "Löschen", f"{len(selected_rows)} Zeile(n) löschen?", QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
        return
    
    for row_idx in sorted(selected_rows, reverse=True):
        pk_item = tablewidget.item(row_idx, 0)
        if pk_item and pk_item.data(Qt.UserRole):
            delete_record_from_db(pk_item.data(Qt.UserRole), tablewidget, parent_dialog)
        tablewidget.removeRow(row_idx)
    QMessageBox.information(parent_dialog, "✓ Erfolg", f"{len(selected_rows)} Zeile(n) entfernt.")




# def SQLAbfrage(self):
#     """Router: führt je nach DB-Typ die passende SQL-Abfrage aus."""
#     if getattr(self, 'db_type', 'postgres') == 'postgres':
#         return SQLAbfrage_postgres(self)
#     else:
#         return SQLAbfrage_spatialite(self)
    
# def SQLAbfrage_postgres(self):
#     """Führt SQL-Abfragen für ausgewählte Features aus (PostgreSQL) und befüllt Tabellen."""
#     conn = loadpostgresconnection(self)
#     if conn is None:
#         return
    
#     cursor = conn.cursor()
    
#     tablenames = {
#         'Haltungen': 'untersuchdat_haltung',
#         'Schächte': 'untersuchdat_schacht', 
#         'GAL': 'untersuchdat_anschlussleitung'
#     }
    
#     columns = {
#         'Haltungen': ["station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
#                     "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
#                     "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"],
#         'Schächte': ["vertikale_lage", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
#                     "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
#                     "bandnr", "untersuchtag", "videozaehler", "foto_dateiname"],
#         'GAL': ["station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
#                 "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
#                 "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"]
#     }
    
#     layer = iface.activeLayer()
#     if layer is None or len(layer.selectedFeatureIds()) == 0:
#         QMessageBox.warning(self, "Auswahlfehler", "Bitte wählen Sie ein passendes Feature aus.")
#         cursor.close()
#         conn.close()
#         return
    
#     feature = layer.getFeature(layer.selectedFeatureIds()[0])
#     haltnam_value = feature['haltnam'] if 'haltnam' in feature.fields().names() else None
#     schoben_value = feature['schoben'] if 'schoben' in feature.fields().names() else None
#     leitnam_value = feature['leitnam'] if 'leitnam' in feature.fields().names() else None
    
#     from collections import defaultdict
#     date_tabs = {'Haltungen': defaultdict(list), 'Schächte': defaultdict(list), 'GAL': defaultdict(list)}
    
#     try:
#         cursor.execute("SET search_path TO public;")
#     except Exception as e:
#         QMessageBox.warning(self, "Datenbankfehler", f"Fehler beim Setzen des search_path: {e}")
    
#     for tab_name, table in tablenames.items():
#         if tab_name == 'Haltungen' and haltnam_value:
#             column = 'untersuchhal'
#             value = haltnam_value
#             orderby = 'station'
#         elif tab_name == 'Schächte' and schoben_value:
#             column = 'untersuchsch'
#             value = schoben_value
#             orderby = 'vertikale_lage'
#         elif tab_name == 'GAL' and leitnam_value:
#             column = 'untersuchleit'
#             value = leitnam_value
#             orderby = 'station'
#         else:
#             continue
        
#         cols = ['pk'] + columns[tab_name]
#         spaltenohnecollate = ['station', 'vertikale_lage', 'pos_von', 'pos_bis', 'quantnr1', 'quantnr2', 'videozaehler', 'bandnr']
        
#         if orderby in spaltenohnecollate:
#             orderclause = f"ORDER BY {orderby}"
#         else:
#             orderclause = f"ORDER BY {orderby} COLLATE \"C\""
        
#         if tab_name == 'Haltungen':
#             query = f"SELECT {', '.join(cols)} FROM {table} WHERE {column} = %s AND (kuerzel != 'K' OR kuerzel IS NULL) {orderclause}"
#         else:
#             query = f"SELECT {', '.join(cols)} FROM {table} WHERE {column} = %s {orderclause}"
        
#         try:
#             cursor.execute(query, (value,))
#             rows_raw = cursor.fetchall()
#             column_names = [desc[0] for desc in cursor.description]
#             rows = [dict(zip(column_names, row_tuple)) for row_tuple in rows_raw]
            
#             for row in rows:
#                 date_tabs[tab_name][row['untersuchtag']].append(row)
                
#         except psycopg2.errors.UndefinedTable as e:
#             QMessageBox.critical(self, "Datenbankfehler",
#                                f"Die Tabelle {table} existiert nicht. "
#                                f"Bitte prüfen Sie, ob die Datenbank importiert oder korrekt angelegt wurde. {e}")
#             cursor.close()
#             conn.close()
#             return
#         except Exception as e:
#             QMessageBox.warning(self, "Datenbankfehler", f"Fehler beim Abrufen der Daten aus {table}: {e}")
#             cursor.close()
#             conn.close()
#             return
    
#     cursor.close()
#     conn.close()
    
#     # Tabs befüllen (unverändert)
#     self.tabWidget.clear()
#     farben = {0: 'red', 1: 'yellow', 2: 'blue', 3: 'lightgreen', 4: 'green'}
    
#     for tab_name, tab_data in date_tabs.items():
#         schacht_tab = QTabWidget()
#         cols = columns[tab_name]
#         idx_bandnr = cols.index("bandnr")
#         idx_videozaehler = cols.index("videozaehler")
#         idx_zd = cols.index("zd") if "zd" in cols else -1
#         idx_zs = cols.index("zs") if "zs" in cols else -1
#         idx_zb = cols.index("zb") if "zb" in cols else -1
#         idx_kuerzel = cols.index("kuerzel")

#         for date, rows in sorted(tab_data.items(), reverse=True):
#             date_table = QTableWidget()
#             date_table.setUpdatesEnabled(False)
#             date_table.setColumnCount(len(cols) + 2)
#             date_table.setHorizontalHeaderLabels(["pk"] + cols + ["Videoname"])
#             date_table.setRowCount(len(rows))
#             date_table.setColumnHidden(0, True)

#             for i, row in enumerate(rows):
#                 pk_value = row['pk']
#                 pk_item = QTableWidgetItem()
#                 pk_item.setData(Qt.UserRole, pk_value)
#                 date_table.setItem(i, 0, pk_item)

#                 for j, col_name in enumerate(cols):
#                     val = row[col_name]
#                     item = QTableWidgetItem(str(val) if val is not None else "")
#                     date_table.setItem(i, j + 1, item)

#                 bandnr = str(row['bandnr']).zfill(5) if row['bandnr'] is not None else "00000"
#                 videozaehler = str(row['videozaehler']).zfill(5) if row['videozaehler'] is not None else "00000"
#                 videoname_item = QTableWidgetItem(bandnr + videozaehler)
#                 date_table.setItem(i, len(cols) + 1, videoname_item)

#             for i, row in enumerate(rows):
#                 z_werte = []
#                 for col_idx in (idx_zd, idx_zs, idx_zb):
#                     if 0 <= col_idx < len(cols):
#                         val = row[cols[col_idx]]
#                         if val is not None and val in farben:
#                             z_werte.append(val)
                
#                 min_z = min(z_werte) if z_werte else None
#                 kuerzel_item = date_table.item(i, idx_kuerzel + 1)
#                 if min_z is not None and min_z in farben:
#                     color = QColor(farben[min_z])
#                     kuerzel_item.setForeground(color)
                
#                 for col_idx in (idx_zd, idx_zs, idx_zb):
#                     if 0 <= col_idx < len(cols):
#                         val = row[cols[col_idx]]
#                         item = date_table.item(i, col_idx + 1)
#                         if val in farben:
#                             item.setForeground(QColor(farben[val]))
#                         elif val is None:
#                             item.setForeground(QColor("black"))

#             date_table.setSelectionBehavior(QTableWidget.SelectRows)
#             date_table.setSelectionMode(QTableWidget.SingleSelection)
#             date_table.setEditTriggers(QTableWidget.AllEditTriggers)
#             date_table.setUpdatesEnabled(True)
#             schacht_tab.addTab(date_table, str(date))

#         tab_widget = QWidget()
#         layout = QVBoxLayout(tab_widget)
#         layout.addWidget(schacht_tab)
#         self.tabWidget.addTab(tab_widget, tab_name)


# def toggleeditmode(self):
#     """Schaltet Edit-Modus für aktuelle Tabelle ein/aus."""
#     currenttabwidget = self.tabWidget.currentWidget()
#     innertabwidget = currenttabwidget.findChild(QTabWidget)
    
#     tablewidget = None
#     if innertabwidget:
#         selectedinnertab = innertabwidget.currentWidget()
#         if selectedinnertab:
#             tablewidget = find_inner_table_widget(selectedinnertab)
    
#     if not tablewidget:
#         QMessageBox.warning(self, "Fehler", "Konnte die Tabelle nicht finden.")
#         return
    
#     if not hasattr(self, 'editmode'):
#         self.editmode = False
    
#     if not self.editmode:
#         self.editmode = True
#         self.edit_button.setText("Änderungen speichern")
#         tablewidget.setEditTriggers(QTableWidget.AllEditTriggers)
#     else:
#         self.editmode = False
#         self.edit_button.setText("Bearbeiten aktivieren")
#         tablewidget.setEditTriggers(QTableWidget.NoEditTriggers)
#         save_changes_to_database(self, tablewidget)

# def SQLAbfrage_spatialite(self):
#     """Führt SQL-Abfragen für ausgewählte Features aus (SpatiaLite) und befüllt Tabellen."""
#     import sqlite3
#     from collections import defaultdict
#     from PyQt5.QtWidgets import QMessageBox, QTableWidget, QTabWidget, QWidget, QTableWidgetItem, QVBoxLayout
#     from PyQt5.QtCore import Qt
#     from PyQt5.QtGui import QColor
#     from qgis.utils import iface
#     from ..netzuebersicht.db_backend import get_backend

#     backend = get_backend('spatialite')
#     conn, cursor, _ = backend.load_native_connection(parent=self)
#     if conn is None:
#         return

#     try:
#         tablenames = {
#             'Haltungen': 'untersuchdat_haltung',
#             'Schächte': 'untersuchdat_schacht',
#             'GAL': 'untersuchdat_anschlussleitung'
#         }

#         columns = {
#             'Haltungen': ["station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
#                           "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
#                           "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"],
#             'Schächte': ["vertikale_lage", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
#                          "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
#                          "bandnr", "untersuchtag", "videozaehler", "foto_dateiname"],
#             'GAL': ["station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
#                     "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
#                     "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"]
#         }

#         layer = iface.activeLayer()
#         if layer is None or len(layer.selectedFeatureIds()) == 0:
#             QMessageBox.warning(self, "Auswahlfehler", "Bitte wählen Sie ein passendes Feature aus.")
#             return

#         feature = layer.getFeature(layer.selectedFeatureIds()[0])
#         field_names = feature.fields().names()
#         haltnam_value = feature['haltnam'] if 'haltnam' in field_names else None
#         schoben_value = feature['schoben'] if 'schoben' in field_names else None
#         leitnam_value = feature['leitnam'] if 'leitnam' in field_names else None

#         date_tabs = {
#             'Haltungen': defaultdict(list),
#             'Schächte': defaultdict(list),
#             'GAL': defaultdict(list)
#         }

#         for tab_name, table in tablenames.items():
#             if tab_name == 'Haltungen' and haltnam_value:
#                 column = 'untersuchhal'
#                 value = haltnam_value
#                 orderby = 'station'
#             elif tab_name == 'Schächte' and schoben_value:
#                 column = 'untersuchsch'
#                 value = schoben_value
#                 orderby = 'vertikale_lage'
#             elif tab_name == 'GAL' and leitnam_value:
#                 column = 'untersuchleit'
#                 value = leitnam_value
#                 orderby = 'station'
#             else:
#                 continue

#             cols = ['pk'] + columns[tab_name]
#             orderclause = f"ORDER BY {orderby}"

#             if tab_name == 'Haltungen':
#                 query = f"""
#                     SELECT {', '.join(cols)}
#                     FROM {table}
#                     WHERE {column} = ? AND (kuerzel != 'K' OR kuerzel IS NULL)
#                     {orderclause}
#                 """
#             else:
#                 query = f"""
#                     SELECT {', '.join(cols)}
#                     FROM {table}
#                     WHERE {column} = ?
#                     {orderclause}
#                 """

#             try:
#                 cursor.execute(query, (value,))
#                 rows_raw = cursor.fetchall()

#                 # ✅ Kein row_factory nötig: manuell via cursor.description konvertieren
#                 # Spaltennamen lowercase → ZD, ZS, ZB werden zu zd, zs, zb
#                 col_names = [desc[0].lower() for desc in cursor.description]
#                 for row_tuple in rows_raw:
#                     row_dict = dict(zip(col_names, row_tuple))
#                     untersuchtag = row_dict.get('untersuchtag')
#                     date_tabs[tab_name][untersuchtag].append(row_dict)

#             except sqlite3.OperationalError as e:
#                 QMessageBox.critical(self, "Datenbankfehler", f"Fehler beim Abrufen der Daten aus {table}:\n{e}")
#                 return
#             except Exception as e:
#                 QMessageBox.warning(self, "Datenbankfehler", f"Fehler beim Abrufen der Daten aus {table}: {e}")
#                 return

#         # Tabs befüllen
#         self.tabWidget.clear()
#         farben = {0: 'red', 1: 'yellow', 2: 'blue', 3: 'lightgreen', 4: 'green'}

#         for tab_name, tab_data in date_tabs.items():
#             schacht_tab = QTabWidget()
#             cols = columns[tab_name]
#             idx_zd = cols.index("zd") if "zd" in cols else -1
#             idx_zs = cols.index("zs") if "zs" in cols else -1
#             idx_zb = cols.index("zb") if "zb" in cols else -1
#             idx_kuerzel = cols.index("kuerzel")

#             for date, rows in sorted(tab_data.items(), reverse=True):
#                 date_table = QTableWidget()
#                 date_table.setUpdatesEnabled(False)
#                 date_table.setColumnCount(len(cols) + 2)
#                 date_table.setHorizontalHeaderLabels(["pk"] + cols + ["Videoname"])
#                 date_table.setRowCount(len(rows))
#                 date_table.setColumnHidden(0, True)


#                 for i, row in enumerate(rows):
#                     pk_value = row.get('pk')
#                     pk_item = QTableWidgetItem()
#                     pk_item.setData(Qt.UserRole, pk_value)
#                     date_table.setItem(i, 0, pk_item)

#                     for j, col_name in enumerate(cols):
#                         val = row.get(col_name)
#                         item = QTableWidgetItem(str(val) if val is not None else "")
#                         date_table.setItem(i, j + 1, item)

#                     bandnr = row.get('bandnr')
#                     videozaehler = row.get('videozaehler')
#                     band_str = str(bandnr).zfill(5) if bandnr is not None else "00000"
#                     vid_str = str(videozaehler).zfill(5) if videozaehler is not None else "00000"
#                     date_table.setItem(i, len(cols) + 1, QTableWidgetItem(band_str + vid_str))

#                 for i, row in enumerate(rows):
#                     z_werte = []
#                     for col_idx in (idx_zd, idx_zs, idx_zb):
#                         if 0 <= col_idx < len(cols):
#                             val = row.get(cols[col_idx])
#                             try:
#                                 val_int = int(val) if val is not None else None
#                             except (ValueError, TypeError):
#                                 val_int = None
#                             if val_int is not None and val_int in farben:
#                                 z_werte.append(val_int)

#                     min_z = min(z_werte) if z_werte else None
#                     kuerzel_item = date_table.item(i, idx_kuerzel + 1)
#                     if min_z is not None and min_z in farben and kuerzel_item:
#                         kuerzel_item.setForeground(QColor(farben[min_z]))

#                     for col_idx in (idx_zd, idx_zs, idx_zb):
#                         if 0 <= col_idx < len(cols):
#                             val = row.get(cols[col_idx])
#                             item = date_table.item(i, col_idx + 1)
#                             if item:
#                                 try:
#                                     val_int = int(val) if val is not None else None
#                                 except (ValueError, TypeError):
#                                     val_int = None
#                                 if val_int is not None and val_int in farben:
#                                     item.setForeground(QColor(farben[val_int]))
#                                 elif val is None:
#                                     item.setForeground(QColor("black"))

#                 date_table.setSelectionBehavior(QTableWidget.SelectRows)
#                 date_table.setSelectionMode(QTableWidget.SingleSelection)
#                 date_table.setEditTriggers(QTableWidget.AllEditTriggers)
#                 date_table.setUpdatesEnabled(True)
#                 schacht_tab.addTab(date_table, str(date))

#             tab_widget = QWidget()
#             layout = QVBoxLayout(tab_widget)
#             layout.addWidget(schacht_tab)
#             self.tabWidget.addTab(tab_widget, tab_name)

#     finally:
#         cursor.close()
#         conn.close()


# def save_changes_to_database(self, tablewidget):
#     """Router: Insert/Update je nach DB-Typ."""
#     if getattr(self, 'db_type', 'postgres') == 'postgres':
#         return save_changes_postgres(self, tablewidget)
#     else:
#         return save_changes_spatialite(self, tablewidget)

# def save_changes_spatialite(self, tablewidget):
#     """Speichert: INSERT (PK=None) + UPDATE in SpatiaLite."""
#     import sqlite3
#     from PyQt5.QtWidgets import QMessageBox
#     from PyQt5.QtCore import Qt
#     from qgis.utils import iface
#     from ..netzuebersicht.db_backend import get_backend

#     reply = QMessageBox.question(self, "Änderungen speichern", "Speichern?",
#                                  QMessageBox.Yes | QMessageBox.No)
#     if reply != QMessageBox.Yes:
#         return

#     maintabname = self.tabWidget.tabText(self.tabWidget.currentIndex())

#     tablenames = {
#         'Haltungen': 'untersuchdat_haltung',
#         'Schächte': 'untersuchdat_schacht',
#         'GAL': 'untersuchdat_anschlussleitung'
#     }
#     dbtable = tablenames.get(maintabname)
#     if not dbtable:
#         print("❌ No table mapping")
#         return

#     headers = [tablewidget.horizontalHeaderItem(i).text() for i in range(tablewidget.columnCount())]
#     dbcols = headers[1:-1]

#     backend = get_backend('spatialite')
#     conn, cursor, _ = backend.load_native_connection(parent=self)
#     if conn is None:
#         print("❌ No spatialite connection")
#         return

#     new_rows = updated_rows = 0

#     try:
#         for row in range(tablewidget.rowCount()):
#             pkitem = tablewidget.item(row, 0)
#             pkvalue = pkitem.data(Qt.UserRole)

#             updatedict = {}
#             for colidx, colname in enumerate(dbcols):
#                 item = tablewidget.item(row, colidx + 1)
#                 val = item.text().strip() if item and item.text().strip() else None
#                 updatedict[colname] = val

#             update_items = {k: v for k, v in updatedict.items() if v is not None}
#             if not update_items:
#                 continue

#             if pkvalue is None:
#                 key_col_map = {'Haltungen': 'haltnam', 'Schächte': 'schoben', 'GAL': 'leitnam'}
#                 key_col = key_col_map[maintabname]
#                 untersuch_col = {
#                     'Haltungen': 'untersuchhal',
#                     'Schächte': 'untersuchsch',
#                     'GAL': 'untersuchleit'
#                 }[maintabname]

#                 if getattr(self, 'external_mode', False):
#                     feature = self.get_external_feature()
#                     key_value = str(feature.get(key_col)) if feature and feature.get(key_col) else None
#                 else:
#                     layer = iface.activeLayer()
#                     if not layer or not layer.selectedFeatureIds():
#                         continue
#                     feature = layer.getFeature(layer.selectedFeatureIds()[0])
#                     if key_col in feature.fields().names() and feature[key_col]:
#                         key_value = str(feature[key_col])
#                     else:
#                         key_value = None

#                 if not key_value:
#                     continue

#                 safe_cols = [untersuch_col] + list(update_items.keys())
#                 safe_vals = [key_value] + list(update_items.values())
#                 placeholders = ', '.join(['?'] * len(safe_cols))
#                 query = f"INSERT INTO {dbtable} ({', '.join(safe_cols)}) VALUES ({placeholders})"

#                 cursor.execute(query, safe_vals)
#                 new_pk = cursor.lastrowid
#                 pkitem.setData(Qt.UserRole, new_pk)
#                 new_rows += 1

#             else:
#                 setclause = ', '.join([f"{col}=?" for col in update_items])
#                 query = f"UPDATE {dbtable} SET {setclause} WHERE pk=?"
#                 params = list(update_items.values()) + [pkvalue]
#                 cursor.execute(query, params)
#                 if cursor.rowcount > 0:
#                     updated_rows += 1

#         conn.commit()
#         QMessageBox.information(self, "✓ Erfolg", f"{new_rows} neu + {updated_rows} aktualisiert!")

#     except Exception as e:
#         conn.rollback()
#         QMessageBox.critical(self, "✗ Fehler", f"{type(e).__name__}: {e}")

#     finally:
#         cursor.close()
#         conn.close()

# def save_changes_postgres(self, tablewidget):
#     """Speichert: INSERT (PK=None) + UPDATE in PostgreSQL. Voll-Debug."""
#     reply = QMessageBox.question(self, "Änderungen speichern", "Speichern?", QMessageBox.Yes | QMessageBox.No)
#     if reply != QMessageBox.Yes:
#         return
    
#     print("🚀 SAVE START")
#     maintabname = self.tabWidget.tabText(self.tabWidget.currentIndex())
#     print(f"  Tab: {maintabname}")
    
#     tablenames = {'Haltungen': 'untersuchdat_haltung', 'Schächte': 'untersuchdat_schacht', 'GAL': 'untersuchdat_anschlussleitung'}
#     dbtable = tablenames.get(maintabname)
#     if not dbtable:
#         print("❌ No table mapping")
#         return
    
#     print(f"  DB-Table: {dbtable}")
#     headers = [tablewidget.horizontalHeaderItem(i).text() for i in range(tablewidget.columnCount())]
#     dbcols = headers[1:-1]
#     print(f"  DB-Columns: {dbcols}")
    
#     conn = loadpostgresconnection(self)
#     if conn is None:
#         print("❌ No connection")
#         return
    
#     cursor = conn.cursor()
#     cursor.execute("SET statement_timeout = 30000;")
#     cursor.execute("BEGIN;")
    
#     new_rows = updated_rows = 0
    
#     try:
#         for row in range(tablewidget.rowCount()):
#             print(f"\n🔄 Row {row}/{tablewidget.rowCount()}")
            
#             pkitem = tablewidget.item(row, 0)
#             pkvalue = pkitem.data(Qt.UserRole)
#             print(f"  PK: {pkvalue}")
            
#             updatedict = {}
#             for colidx, colname in enumerate(dbcols):
#                 item = tablewidget.item(row, colidx + 1)
#                 val = item.text().strip() if item and item.text().strip() else None
#                 updatedict[colname] = val
#                 print(f"    {colname}: '{val}'")
            
#             update_items = {k: v for k, v in updatedict.items() if v is not None}
#             print(f"  Update-Items: {len(update_items)} = {dict(list(update_items.items())[:3])}...")
            
#             if not update_items:
#                 print("  Skip: Keine Daten")
#                 continue
            
#             if pkvalue is None:
#                 print("  → INSERT")
#                 key_col_map = {'Haltungen': 'haltnam', 'Schächte': 'schoben', 'GAL': 'leitnam'}
#                 key_col = key_col_map[maintabname]
#                 untersuch_col = {'Haltungen': 'untersuchhal', 'Schächte': 'untersuchsch', 'GAL': 'untersuchleit'}[maintabname]
                
#                 print(f"  Key-Field: {key_col} → {untersuch_col}")
                
#                 if hasattr(self, 'external_mode') and self.external_mode:
#                     print("  External Mode")
#                     feature = self.get_external_feature()
#                     key_value = str(feature.get(key_col)) if feature and feature.get(key_col) else None
#                 else:
#                     print("  Internal Mode")
#                     layer = iface.activeLayer()
#                     if not layer or not layer.selectedFeatureIds():
#                         print("  ⚠️ Skip: No layer/feature")
#                         continue
#                     feature = layer.getFeature(layer.selectedFeatureIds()[0])
#                     key_value = str(feature[key_col]) if key_col in feature.fields().names() and feature[key_col] else None
                
#                 print(f"  Key-Value: '{key_value}'")
#                 if not key_value:
#                     print("  ⚠️ Skip: No key")
#                     continue
                
#                 safe_cols = [untersuch_col]
#                 safe_vals = [key_value]
#                 for col, val in update_items.items():
#                     safe_cols.append(col)
#                     safe_vals.append(val)
                
#                 print(f"  Insert-cols: {len(safe_cols)} = {safe_cols}")
#                 print(f"  Insert-vals: {len(safe_vals)} = {safe_vals}")
                
#                 if len(safe_cols) != len(safe_vals):
#                     print("❌ MISMATCH cols/vals!")
#                     continue
                
#                 placeholders = ', '.join(['%s'] * len(safe_cols))
#                 query = f"INSERT INTO {dbtable} ({', '.join(safe_cols)}) VALUES ({placeholders}) RETURNING pk"
                
#                 print(f"  EXECUTE: {query}")
#                 print(f"  PARAMS:  {safe_vals}")
                
#                 cursor.execute(query, safe_vals)
#                 new_pk = cursor.fetchone()[0]
#                 pkitem.setData(Qt.UserRole, new_pk)
#                 new_rows += 1
#                 print(f"  ✅ INSERT PK={new_pk}")
                
#             else:
#                 print("  → UPDATE")
#                 setclause = ', '.join([f"{col}=%s" for col in update_items])
#                 query = f"UPDATE {dbtable} SET {setclause} WHERE pk=%s"
#                 params = list(update_items.values()) + [pkvalue]
                
#                 print(f"  UPDATE: {query}")
#                 print(f"  PARAMS: {params}")
                
#                 cursor.execute(query, params)
#                 if cursor.rowcount > 0:
#                     updated_rows += 1
#                     print(f"  ✅ UPDATE rowcount={cursor.rowcount}")
        
#         print("\n💾 COMMIT...")
#         conn.commit()
#         print("✅ COMMIT DONE!")
        
#         QMessageBox.information(self, "✓ Erfolg", f"{new_rows} neu + {updated_rows} aktualisiert!")
        
#     except Exception as e:
#         print(f"\n❌ EXCEPTION: {e}")
#         import traceback
#         traceback.print_exc()
#         conn.rollback()
#         QMessageBox.critical(self, "✗ Fehler", f"{type(e).__name__}: {e}")
    
#     finally:
#         cursor.close()
#         conn.close()
#         print("🏁 SAVE ENDE")

# def find_inner_table_widget(widget):
#     """Sucht gezielt das sichtbare QTableWidget im aktuellen Tab."""
#     # 1. Direkter Treffer
#     if isinstance(widget, QTableWidget):
#         return widget
    
#     # 2. Wenn das Widget ein QTabWidget ist, suche im AKTUELLEN Tab weiter!
#     if isinstance(widget, QTabWidget):
#         current_tab = widget.currentWidget()
#         if current_tab:
#             return find_inner_table_widget(current_tab)
            
#     # 3. Wenn es ein QWidget (oder Layout-Container) ist, suche alle QTableWidgets
#     tables = widget.findChildren(QTableWidget)
#     if tables:
#         # Finde dasjenige, das auch wirklich sichtbar/aktiv ist
#         for t in tables:
#             if t.isVisible():
#                 return t
#         # Fallback: gib einfach das erste zurück
#         return tables[0]
        
#     return None


# def add_row_to_table(tablewidget, columns, parent_dialog=None):
#     """Neue Zeile + Defaults (untersuchtag, film_dateiname aus Zeile 0)."""
#     row_count = tablewidget.rowCount()
#     tablewidget.insertRow(row_count)
    
#     # PK=None → INSERT triggern
#     pk_item = QTableWidgetItem()
#     pk_item.setData(Qt.UserRole, None)
#     tablewidget.setItem(row_count, 0, pk_item)
    
#     # Defaults aus ERSTER Zeile kopieren
#     if row_count > 0:
#         template_row = 0
        
#         # untersuchtag
#         if 'untersuchtag' in columns:
#             tag_idx = columns.index('untersuchtag') + 1
#             template_tag = tablewidget.item(template_row, tag_idx)
#             if template_tag and template_tag.text():
#                 tablewidget.setItem(row_count, tag_idx, QTableWidgetItem(template_tag.text()))
        
#         # film_dateiname
#         if 'film_dateiname' in columns:
#             film_idx = columns.index('film_dateiname') + 1
#             template_film = tablewidget.item(template_row, film_idx)
#             if template_film and template_film.text():
#                 tablewidget.setItem(row_count, film_idx, QTableWidgetItem(template_film.text()))
        
#         # kuerzel='K' (sichtbar)
#         if 'kuerzel' in columns:
#             kuerzel_idx = columns.index('kuerzel') + 1
#             tablewidget.setItem(row_count, kuerzel_idx, QTableWidgetItem('BCA'))
    
#     # Rest leer
#     for j in range(1, tablewidget.columnCount() - 1):
#         if tablewidget.item(row_count, j) is None:
#             tablewidget.setItem(row_count, j, QTableWidgetItem(""))
    
#     tablewidget.setItem(row_count, tablewidget.columnCount() - 1, QTableWidgetItem(""))
#     tablewidget.scrollToBottom()
    
#     print(f"➕ Neue Zeile {row_count} bereit für INSERT")


# def delete_selected_rows(tablewidget, parent_dialog):
#     """Löscht selektierte Zeilen (bestätigen)."""
#     print("DEBUG: tablewidget =", tablewidget)
#     print("DEBUG: rowCount =", tablewidget.rowCount())
#     print("DEBUG: currentIndex =", tablewidget.currentIndex())
#     selected_items = tablewidget.selectedItems()
#     print("DEBUG: selected_items count =", len(selected_items))
    
#     if not selected_items:
#         QMessageBox.warning(parent_dialog, "Fehler", "Keine Zeile selektiert.")
#         return
    
#     # Unique Rows aus Items ermitteln
#     selected_rows = list(set(item.row() for item in selected_items))
#     print("DEBUG: selected_rows =", selected_rows)
    
#     reply = QMessageBox.question(parent_dialog, "Löschen", 
#                                  f"{len(selected_rows)} Zeile(n) löschen?",
#                                  QMessageBox.Yes | QMessageBox.No)
#     if reply != QMessageBox.Yes:
#         return
    
#     # Rückwärts löschen
#     for row_idx in sorted(selected_rows, reverse=True):
#         pk_item = tablewidget.item(row_idx, 0)
#         if pk_item and pk_item.data(Qt.UserRole):  # Nur existierende Records
#             delete_record_from_db(pk_item.data(Qt.UserRole), tablewidget, parent_dialog)
#         tablewidget.removeRow(row_idx)
    
#     QMessageBox.information(parent_dialog, "✓ Erfolg", f"{len(selected_rows)} Zeile(n) entfernt.")


# def delete_record_from_db(pk_value, tablewidget, parent_dialog):
#     """Löscht DB-Record per PK – abhängig vom DB-Typ."""
#     from PyQt5.QtWidgets import QMessageBox
#     from .db_connection import loadpostgresconnection
#     from ..netzuebersicht.db_backend import get_backend
    
#     headers = [tablewidget.horizontalHeaderItem(i).text() for i in range(tablewidget.columnCount())]
#     maintabname = parent_dialog.tabWidget.tabText(parent_dialog.tabWidget.currentIndex())
    
#     tablenames = {
#         'Haltungen': 'untersuchdat_haltung',
#         'Schächte': 'untersuchdat_schacht',
#         'GAL': 'untersuchdat_anschlussleitung'
#     }
#     dbtable = tablenames.get(maintabname)
#     if not dbtable:
#         print("⚠️ Keine Tabelle gefunden.")
#         return
    
#     if getattr(parent_dialog, 'db_type', 'postgres') == 'postgres':
#         conn = loadpostgresconnection(parent_dialog)
#         if conn is None:
#             return
#         cursor = conn.cursor()
#         try:
#             cursor.execute(f"DELETE FROM {dbtable} WHERE pk = %s", (pk_value,))
#             conn.commit()
#             print(f"🗑️ Deleted PK {pk_value} from {dbtable} (Postgres)")
#         except Exception as e:
#             conn.rollback()
#             QMessageBox.warning(parent_dialog, "DB-Fehler", f"Löschen fehlgeschlagen:\n{str(e)}")
#         finally:
#             cursor.close()
#             conn.close()
#     else:  # spatialite
#         # 1. Frische Verbindung holen
#         backend = get_backend('spatialite')
#         conn, cursor, _ = backend.load_native_connection(parent=parent_dialog)
#         if conn is None:
#             return
        
#         try:
#             cursor.execute(f"DELETE FROM {dbtable} WHERE pk = ?", (pk_value,))
#             conn.commit()
#             print(f"🗑️ Deleted PK {pk_value} from {dbtable} (Spatialite)")
#         except Exception as e:
#             conn.rollback()
#             QMessageBox.warning(parent_dialog, "DB-Fehler", f"Löschen fehlgeschlagen:\n{str(e)}")
#         finally:
#             cursor.close()
#             conn.close()


