# netzuebersicht/sonderbauwerke.py
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QHBoxLayout, QWidget, QVBoxLayout, QInputDialog, QMessageBox
)
# db_postgres nur noch als Fallback importieren, falls nötig
try:
    from . import db_postgres
except ImportError:
    db_postgres = None

from .table_models import (
    load_data_into_tables,
)

def _get_db_utils(conn):
    """
    Hilfsfunktion: Ermittelt Datenbank-Typ und Platzhalter.
    Rückgabe: (is_sqlite, placeholder_string)
    """
    conn_type = str(type(conn)).lower()
    is_sqlite = 'sqlite' in conn_type or 'spatialite' in conn_type
    ph = "?" if is_sqlite else "%s"
    return is_sqlite, ph

def _get_columns_for_table(conn, table_name):
    """
    Liefert (column_name, data_type) kompatibel für PG und SQLite.
    """
    is_sqlite, _ = _get_db_utils(conn)
    cur = conn.cursor()
    cols = []

    if is_sqlite:
        # SQLite / Spatialite Weg
        try:
            cur.execute(f"PRAGMA table_info({table_name})")
            rows = cur.fetchall()
            # PRAGMA liefert: (cid, name, type, notnull, dflt_value, pk)
            # Wir brauchen nur (name, type)
            cols = [(r[1], r[2].lower()) for r in rows]
        except Exception as e:
            print(f"Fehler beim Lesen der Spalten (SQLite): {e}")
    else:
        # PostgreSQL Weg
        try:
            # Schema 'public' ist Standard, aber wir filtern sicherheitshalber
            query = """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """
            cur.execute(query, (table_name,))
            cols = cur.fetchall()
        except Exception as e:
            print(f"Fehler beim Lesen der Spalten (PG): {e}")

    cur.close()
    return cols


def _build_dynamic_dialog(parent, table_name, columns, max_columns=3):
    """
    Erzeugt einen QDialog mit dynamischem Formular.
    """
    dlg = QDialog(parent)
    dlg.setWindowTitle(f"{table_name} – Bearbeiten/Neu")
    dlg.resize(600, 400) # Etwas größer starten

    main_layout = QVBoxLayout(dlg)

    # horizontales Layout für die Spalten
    columns_layout = QHBoxLayout()
    main_layout.addLayout(columns_layout)

    n_fields = len(columns)
    n_cols = min(max_columns, max(1, (n_fields + 9) // 10))

    form_layouts = []
    for _ in range(n_cols):
        col_widget = QWidget()
        fl = QFormLayout(col_widget)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(4)
        columns_layout.addWidget(col_widget)
        form_layouts.append(fl)

    widgets = {}

    for idx, (col_name, data_type) in enumerate(columns):
        target_form = form_layouts[idx % n_cols]
        edit = QLineEdit()
        edit.setObjectName(col_name)
        
        # Datentyp-Check etwas toleranter machen (wg. SQLite vs Postgres)
        dt = data_type.lower()
        if any(x in dt for x in ["int", "numeric", "real", "double", "float"]):
            edit.setPlaceholderText(f"{col_name} (Zahl)")
        elif any(x in dt for x in ["date", "time", "timestamp"]):
            edit.setPlaceholderText(f"{col_name} (YYYY-MM-DD)")
        else:
            edit.setPlaceholderText(col_name)

        widgets[col_name] = edit
        target_form.addRow(f"{col_name}:", edit)

    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.accepted.connect(dlg.accept)
    buttons.rejected.connect(dlg.reject)
    main_layout.addWidget(buttons)

    return dlg, widgets


def sonderbauwerk_anlegen(parent):
    typen = [
        "Pumpwerk (PW)", "Retentionsbodenfilter (RBF)", "Regenklärbecken (RKB)",
        "Regenrückhaltebecken (RRB)", "Regenüberlauf (RUE)", "Regenüberlaufbecken (RÜB)",
        "Verbindungssammler (VS)", "Versickerungsanlage (RV)",
    ]
    typ_map = {
        "Pumpwerk (PW)": "bauwerke_pw", "Retentionsbodenfilter (RBF)": "bauwerke_rbf",
        "Regenklärbecken (RKB)": "bauwerke_rkb", "Regenrückhaltebecken (RRB)": "bauwerke_rrb",
        "Regenüberlauf (RUE)": "bauwerke_rue", "Regenüberlaufbecken (RÜB)": "bauwerke_rueb",
        "Verbindungssammler (VS)": "bauwerke_vs", "Versickerungsanlage (RV)": "bauwerke_rv",
    }

    item, ok = QInputDialog.getItem(parent, "Neues Sonderbauwerk", "Bitte Typ auswählen:", typen, 0, False)
    if not ok or not item:
        return

    table_name = typ_map[item]

    # 1. Verbindung holen (flexibel)
    conn = getattr(parent, 'conn', None)
    if conn is None and db_postgres:
        conn = db_postgres.load_postgres_connection(parent)
    
    if conn is None:
        QMessageBox.critical(parent, "Fehler", "Keine Datenbankverbindung gefunden.")
        return

    is_sqlite, ph = _get_db_utils(conn)

    try:
        # 2. Spalten ermitteln
        all_cols = _get_columns_for_table(conn, table_name)
        
        skip_cols = {"geol", "geom", "geop", "ogc_fid", "fid", "pk_uid"} # Erweitert für SQLite PKs
        input_cols = [
            (c, t) for c, t in all_cols
            if c.lower() not in skip_cols and not c.lower().endswith("_id")
        ]

        if not input_cols:
            QMessageBox.warning(parent, "Fehler", f"Keine editierbaren Spalten in {table_name}.")
            return

        # 3. Dialog
        dlg, widgets = _build_dynamic_dialog(parent, table_name, input_cols)
        if dlg.exec_() != QDialog.Accepted:
            return

        # 4. Werte sammeln
        daten = {}
        for col_name, data_type in input_cols:
            text = widgets[col_name].text().strip()
            dt = data_type.lower()
            
            if text == "":
                daten[col_name] = None
            else:
                try:
                    if "int" in dt:
                        daten[col_name] = int(text)
                    elif any(x in dt for x in ["numeric", "real", "double", "float"]):
                        daten[col_name] = float(text.replace(",", "."))
                    else:
                        daten[col_name] = text
                except ValueError:
                     QMessageBox.warning(parent, "Fehler", f"Ungültiger Wert für {col_name}")
                     return

        # 5. INSERT
        cur = conn.cursor()
        spalten = ", ".join(daten.keys())
        platzhalter = ", ".join([ph] * len(daten)) # Dynamischer Platzhalter (? oder %s)
        
        sql = f"INSERT INTO {table_name} ({spalten}) VALUES ({platzhalter})"
        
        cur.execute(sql, list(daten.values()))
        conn.commit()

        # Refresh
        try:
            load_data_into_tables(parent)
            _nach_sonderbauwerk_geometrie(parent, table_name)
        except Exception as e:
            print(f"Refresh Fehler: {e}")

        QMessageBox.information(parent, "Erfolg", f"Sonderbauwerk in {table_name} angelegt.")

    except Exception as e:
        conn.rollback()
        QMessageBox.critical(parent, "Fehler", f"Speichern fehlgeschlagen:\n{e}")
    # finally: conn.close() -> NICHT schließen, wenn es parent.conn ist!


def sonderbauwerk_loeschen(self):
    """Löscht den selektierten Eintrag."""
    if not hasattr(self, 'tableView_Sonderbauwerke'):
        return
    
    selection = self.tableView_Sonderbauwerke.selectionModel().selection()
    if selection.isEmpty():
        QMessageBox.warning(self, "Info", "Bitte ein Sonderbauwerk auswählen.")
        return
    
    proxy_index = selection.indexes()[0]
    model_index = self.proxy_model_sonderbauwerke.mapToSource(proxy_index)
    
    # Spaltenindizes prüfen! (Annahme: 0=Name, 4=Tabelle)
    name = self.model_sonderbauwerke.data(model_index.sibling(model_index.row(), 0))
    quelle = self.model_sonderbauwerke.data(model_index.sibling(model_index.row(), 4))
    
    if not name or not quelle:
        QMessageBox.warning(self, "Fehler", "Konnte Name/Quelle nicht aus Tabelle lesen.")
        return

    reply = QMessageBox.question(self, "Löschen", f"'{name}' aus '{quelle}' löschen?", QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes: return

    conn = getattr(self, 'conn', None)
    if conn is None and db_postgres: conn = db_postgres.load_postgres_connection(self)
    if not conn: return

    is_sqlite, ph = _get_db_utils(conn)

    try:
        cur = conn.cursor()
        # Bei SQL DELETE ist Name oft unique genug für Sonderbauwerke
        sql = f"DELETE FROM {quelle} WHERE name = {ph}"
        cur.execute(sql, (name,))
        
        if cur.rowcount > 0:
            conn.commit()
            load_data_into_tables(self)
            QMessageBox.information(self, "Erfolg", "Gelöscht.")
        else:
            QMessageBox.warning(self, "Fehler", "Datensatz in DB nicht gefunden (Name geändert?).")
            
    except Exception as e:
        conn.rollback()
        QMessageBox.critical(self, "Fehler", str(e))


def sonderbauwerk_bearbeiten(self):
    """
    Bearbeiten mit Support für PG und SQLite
    """
    if not hasattr(self, 'tableView_Sonderbauwerke'): return
    
    selection = self.tableView_Sonderbauwerke.selectionModel().selection()
    if selection.isEmpty():
        QMessageBox.warning(self, "Info", "Bitte auswählen.")
        return
    
    proxy_index = selection.indexes()[0]
    source_index = self.proxy_model_sonderbauwerke.mapToSource(proxy_index)
    
    name = self.model_sonderbauwerke.data(source_index.sibling(source_index.row(), 0))
    quelle = self.model_sonderbauwerke.data(source_index.sibling(source_index.row(), 4))
    
    conn = getattr(self, 'conn', None)
    if conn is None and db_postgres: conn = db_postgres.load_postgres_connection(self)
    if not conn: return

    is_sqlite, ph = _get_db_utils(conn)

    try:
        cur = conn.cursor()
        
        # ID Spalte identifizieren
        id_map = {
            'bauwerke_pw': 'pw_id', 'bauwerke_rbf': 'rbf_id', 'bauwerke_rkb': 'rkb_id',
            'bauwerke_rrb': 'rrb_id', 'bauwerke_rue': 'rue_id', 'bauwerke_rueb': 'rueb_id',
            'bauwerke_vs': 'vs_id', 'bauwerke_rv': 'rv_id'
        }
        id_col = id_map.get(quelle)
        
        if not id_col:
            QMessageBox.warning(self, "Fehler", f"Keine ID-Spalte für {quelle} definiert.")
            return

        # ID holen
        cur.execute(f"SELECT {id_col} FROM {quelle} WHERE name = {ph} LIMIT 1", (name,))
        res = cur.fetchone()
        if not res:
            QMessageBox.warning(self, "Fehler", "Objekt in DB nicht gefunden.")
            return
        obj_id = res[0]

        # Spalten laden
        all_cols = _get_columns_for_table(conn, quelle)
        skip = {"geol", "geom", "geop", "ogc_fid", "fid", "pk_uid"}
        input_cols = [(c, t) for c, t in all_cols if c.lower() not in skip and not c.lower().endswith("_id")]

        # Daten laden
        cur.execute(f"SELECT * FROM {quelle} WHERE {id_col} = {ph}", (obj_id,))
        row = cur.fetchone()
        # Beschreibung der Spalten holen (bei SQLite anders als bei PG)
        if cur.description:
            colnames = [d[0] for d in cur.description]
            daten = dict(zip(colnames, row))
        else:
            # Fallback falls description leer (sollte nicht passieren)
            daten = {} 

        # Dialog bauen
        dlg, widgets = _build_dynamic_dialog(self, quelle, input_cols)
        dlg.setWindowTitle(f"Bearbeiten: {name}")

        # Füllen
        for c, _ in input_cols:
            val = daten.get(c)
            if val is not None:
                widgets[c].setText(str(val))

        if dlg.exec_() != QDialog.Accepted:
            return

        # Update bauen
        updated = {}
        for c, t in input_cols:
            txt = widgets[c].text().strip()
            dt = t.lower()
            
            if txt == "":
                updated[c] = None
            else:
                try:
                    if "int" in dt: updated[c] = int(txt)
                    elif any(x in dt for x in ["num", "real", "double", "float"]): 
                        updated[c] = float(txt.replace(",", "."))
                    else: updated[c] = txt
                except:
                    QMessageBox.warning(self, "Fehler", f"Falsches Format bei {c}")
                    return

        if updated:
            set_clauses = ", ".join([f"{k} = {ph}" for k in updated.keys()])
            values = list(updated.values()) + [obj_id]
            sql = f"UPDATE {quelle} SET {set_clauses} WHERE {id_col} = {ph}"
            
            cur.execute(sql, values)
            conn.commit()
            load_data_into_tables(self)
            QMessageBox.information(self, "OK", "Gespeichert.")

    except Exception as e:
        conn.rollback()
        QMessageBox.critical(self, "Fehler", str(e))

def _nach_sonderbauwerk_geometrie(parent, table_name):
    try:
        from .geometry_tools import frage_nach_geometrie
        frage_nach_geometrie(parent, None, table_name)
    except ImportError:
        pass
    except Exception as e:
        print(f"Geo-Fehler: {e}")
