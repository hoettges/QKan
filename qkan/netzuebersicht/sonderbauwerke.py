# qkan/netzuebersicht/sonderbauwerke.py
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QHBoxLayout, QWidget, QVBoxLayout, QInputDialog, QMessageBox
)
from .table_models import (
    load_data_into_tables,
)

# Spalten, die in den Eingabedialogen nicht angeboten werden
SKIP_SPALTEN = {"geol", "geom", "geop", "ogc_fid", "fid", "pk_uid", "pk"}


def _get_db(parent):
    """
    Liefert (conn, backend) der Netzübersicht.
    Die SQL-Statements kommen aus sqlite.yml / postgres.yml (über das Backend).
    """
    conn = getattr(parent, "conn", None)
    backend = getattr(parent, "backend", None)
    if backend is None:
        from .db_backend import get_backend
        backend = get_backend(getattr(parent, "db_type", None))
    return conn, backend


def _get_columns_for_table(conn, backend, table_name):
    """Liefert [(column_name, data_type), ...] – für SQLite und PostgreSQL."""
    cur = conn.cursor()
    try:
        return backend.get_columns(cur, table_name)
    finally:
        cur.close()


def _eingabespalten(alle_spalten):
    return [
        (c, t) for c, t in alle_spalten
        if c.lower() not in SKIP_SPALTEN and not c.lower().endswith("_id")
    ]


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

    # 1. Verbindung der Netzübersicht verwenden
    conn, backend = _get_db(parent)
    if conn is None:
        QMessageBox.critical(parent, "Fehler", "Keine Datenbankverbindung gefunden.")
        return

    try:
        # 2. Spalten ermitteln
        all_cols = _get_columns_for_table(conn, backend, table_name)
        input_cols = _eingabespalten(all_cols)

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

        # 5. INSERT (nz_insert)
        cur = conn.cursor()
        backend.insert_row(cur, table_name, daten)
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

    conn, backend = _get_db(self)
    if not conn: return

    try:
        cur = conn.cursor()
        # Bei SQL DELETE ist Name oft unique genug für Sonderbauwerke (nz_sbw_loeschen)
        backend.execute(cur, "nz_sbw_loeschen", (name,), tabelle=backend.ident(quelle))
        
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
    
    conn, backend = _get_db(self)
    if not conn: return

    if quelle not in backend.SONDERBAUWERKE_TABELLEN:
        QMessageBox.warning(self, "Fehler", f"Unbekannte Sonderbauwerkstabelle: {quelle}")
        return

    # Tabellen-/ID-Angaben für die yml-Statements (SQLite: rowid, PostgreSQL: z.B. pw_id)
    sql_args = dict(tabelle=backend.ident(quelle), id_spalte=backend.sbw_id_spalte(quelle))

    try:
        cur = conn.cursor()

        # ID holen (nz_sbw_id)
        backend.execute(cur, "nz_sbw_id", (name,), **sql_args)
        res = cur.fetchone()
        if not res:
            QMessageBox.warning(self, "Fehler", "Objekt in DB nicht gefunden.")
            return
        obj_id = res[0]

        # Spalten laden
        all_cols = _get_columns_for_table(conn, backend, quelle)
        input_cols = _eingabespalten(all_cols)

        # Daten laden (nz_sbw_datensatz)
        backend.execute(cur, "nz_sbw_datensatz", (obj_id,), **sql_args)
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
            values = list(updated.values()) + [obj_id]
            # nz_sbw_update
            backend.execute(
                cur, "nz_sbw_update", values,
                zuweisungen=backend.zuweisungen(updated.keys()), **sql_args
            )
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
