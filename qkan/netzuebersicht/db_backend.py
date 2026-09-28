# qkan/netzuebersicht/db_backend.py
import os
import re
import sqlite3
import uuid

from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import QMessageBox
from qgis.utils import plugins


def get_qkan_instance():
    """
    Liefert die laufende QKan-Instanz aus den geladenen QGIS-Plugins.
    """
    return plugins.get("qkan")


def extract_sqlite_path_from_qkan_source(dbsource):
    """
    Extrahiert den SQLite-Dateipfad aus einem QGIS-Data-Source-String wie:
    dbname='C:/.../projekt.sqlite' table="schaechte" (geop) sql=...

    Falls dbsource bereits direkt ein Dateipfad ist, wird dieser unverändert zurückgegeben.
    """
    if not dbsource:
        return None

    dbsource = str(dbsource).strip()

    print(f"[db_backend] raw dbsource = {dbsource}")

    # Fall 1: Es ist bereits direkt ein Dateipfad
    if os.path.isfile(dbsource):
        print(f"[db_backend] dbsource ist bereits ein Dateipfad: {dbsource}")
        return dbsource

    # Fall 2: QGIS-Data-Source-String mit dbname='...'
    match = re.search(r"dbname='([^']+)'", dbsource)
    if match:
        path = match.group(1)
        print(f"[db_backend] extrahierter Pfad aus dbname='...': {path}")
        return path

    # Fall 3: Alternative Schreibweise mit doppelten Quotes
    match = re.search(r'dbname="([^"]+)"', dbsource)
    if match:
        path = match.group(1)
        print(f'[db_backend] extrahierter Pfad aus dbname="...": {path}')
        return path

    print("[db_backend] Kein SQLite-Pfad aus dbsource extrahierbar")
    return None


def get_db_type():
    """
    Aktuell wird ausschließlich die aktive QKan-SpatiaLite/SQLite-Datenbank verwendet.
    """
    return "spatialite"


def get_backend(db_type=None):
    """
    Derzeit gibt es absichtlich nur den SpatiaLite-Backendpfad.
    """
    return SpatialiteBackend()


class SpatialiteBackend:
    """
    Nutzt ausschließlich die aktuell von QKan bereitgestellte Datenquelle.
    Kein PostgreSQL-Fallback, kein JSON-Fallback.
    """

    def load_native_connection(self, parent):
        """
        Baut eine native sqlite3-Verbindung ausschließlich aus der aktiven QKan-Datenquelle auf.
        """
        qkan_instance = get_qkan_instance()
        raw_dbsource = getattr(qkan_instance, "dbsource", None) if qkan_instance else None
        db_path = extract_sqlite_path_from_qkan_source(raw_dbsource)

        print("[db_backend] load_native_connection()")
        print(f"[db_backend] qkan_instance = {qkan_instance}")
        print(f"[db_backend] QKan dbsource = {raw_dbsource}")
        print(f"[db_backend] extracted db_path = {db_path}")

        if not raw_dbsource:
            QMessageBox.critical(
                parent,
                "Keine QKan-Datenbank",
                "Es ist keine aktive QKan-Datenbank verfügbar.\n"
                "Bitte öffne zuerst eine QKan-Datenbank und starte danach die Netzübersicht erneut.",
            )
            return None, None, None

        if not db_path:
            QMessageBox.critical(
                parent,
                "QKan-Datenquelle ungültig",
                f"Der SQLite-Pfad konnte nicht aus der QKan-Datenquelle extrahiert werden:\n{raw_dbsource}",
            )
            return None, None, None

        if not os.path.exists(db_path):
            QMessageBox.critical(
                parent,
                "QKan-Datenbank nicht gefunden",
                f"Die von QKan verwendete Datenbankdatei existiert nicht:\n{db_path}",
            )
            return None, None, None

        try:
            conn = sqlite3.connect(db_path)
            self._init_spatialite(conn)
            cursor = conn.cursor()

            config = {
                "path": db_path,
                "database": db_path,
                "driver": "QSQLITE",
                "raw_dbsource": raw_dbsource,
            }

            print(f"[db_backend] sqlite native connection geöffnet: {db_path}")
            return conn, cursor, config

        except Exception as e:
            QMessageBox.critical(
                parent,
                "Fehler beim Öffnen der QKan-Datenbank",
                f"Die QKan-Datenbank konnte nicht geöffnet werden:\n{e}",
            )
            return None, None, None

    def load_native_connection_from_qkan(self, parent, dbsource):
        """
        Kompatibilitätsmethode: nutzt ebenfalls ausschließlich den übergebenen QKan-Source-String.
        """
        print("[db_backend] load_native_connection_from_qkan()")
        print(f"[db_backend] übergebener dbsource = {dbsource}")

        if not dbsource:
            return self.load_native_connection(parent)

        db_path = extract_sqlite_path_from_qkan_source(dbsource)
        print(f"[db_backend] extrahierter db_path = {db_path}")

        if not db_path:
            QMessageBox.critical(
                parent,
                "QKan-Datenquelle ungültig",
                f"Der SQLite-Pfad konnte nicht aus der QKan-Datenquelle extrahiert werden:\n{dbsource}",
            )
            return None, None, None

        if not os.path.exists(db_path):
            QMessageBox.critical(
                parent,
                "QKan-Datenbank nicht gefunden",
                f"Die von QKan übergebene Datenbankdatei existiert nicht:\n{db_path}",
            )
            return None, None, None

        try:
            conn = sqlite3.connect(db_path)
            self._init_spatialite(conn)
            cursor = conn.cursor()

            config = {
                "path": db_path,
                "database": db_path,
                "driver": "QSQLITE",
                "raw_dbsource": dbsource,
            }

            print(f"[db_backend] sqlite native connection aus dbsource geöffnet: {db_path}")
            return conn, cursor, config

        except Exception as e:
            QMessageBox.critical(
                parent,
                "Fehler beim Öffnen der QKan-Datenbank",
                f"Die QKan-Datenbank konnte nicht geöffnet werden:\n{e}",
            )
            return None, None, None

    def _init_spatialite(self, conn):
        """
        Aktiviert SpatiaLite-Funktionen für eine native sqlite3-Verbindung
        und testet anschließend, ob GeomFromText verfügbar ist.
        """
        print("[db_backend] _init_spatialite()")

        try:
            conn.enable_load_extension(True)
            print("[db_backend] enable_load_extension(True) erfolgreich")
        except Exception as e:
            print(f"[db_backend] enable_load_extension fehlgeschlagen: {e}")
            return False

        candidates = [
            "mod_spatialite",
            "mod_spatialite.dll",
            "libspatialite",
            "libspatialite.dll",
        ]

        loaded_ext = None
        last_error = None

        for ext in candidates:
            try:
                conn.load_extension(ext)
                loaded_ext = ext
                print(f"[db_backend] SpatiaLite-Erweiterung geladen: {ext}")
                break
            except Exception as e:
                last_error = e
                print(f"[db_backend] load_extension('{ext}') fehlgeschlagen: {e}")

        if not loaded_ext:
            print(f"[db_backend] Keine SpatiaLite-Erweiterung ladbar. Letzter Fehler: {last_error}")
            return False

        # Optional: InitSpatialMetaData nicht blind ausführen, nur Funktionstest
        try:
            test_cur = conn.cursor()
            test_cur.execute("SELECT GeomFromText('POINT(0 0)', 25832)")
            result = test_cur.fetchone()
            print(f"[db_backend] GeomFromText verfügbar, Testresultat: {result is not None}")
            test_cur.close()
            return True
        except Exception as e:
            print(f"[db_backend] GeomFromText NICHT verfügbar: {e}")
            return False

    def build_connection_name(self, prefix="netzuebersicht"):
        return f"{prefix}_{uuid.uuid4().hex}"

    def setup_qt_connection(self, config, parent, connection_name=None):
        """
        Baut die Qt-SQL-Verbindung auf dieselbe SQLite-Datei auf wie die native Verbindung.
        """
        db_path = config.get("path") or config.get("database")

        print("[db_backend] setup_qt_connection()")
        print(f"[db_backend] db_path = {db_path}")

        if not db_path:
            QMessageBox.critical(
                parent,
                "Fehlende QKan-Datenbank",
                "Kein Datenbankpfad für die Qt-SQL-Verbindung vorhanden.",
            )
            return None

        if not connection_name:
            connection_name = self.build_connection_name()

        try:
            if QSqlDatabase.contains(connection_name):
                print(f"[db_backend] vorhandene Qt-Connection wird entfernt: {connection_name}")
                QSqlDatabase.removeDatabase(connection_name)
        except Exception as e:
            print(f"[db_backend] removeDatabase warning: {e}")

        db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
        db.setDatabaseName(db_path)

        opened = db.open()
        print(f"[db_backend] Qt QSQLITE open() -> {opened}")
        print(f"[db_backend] Qt connectionName = {connection_name}")

        if not opened:
            QMessageBox.critical(
                parent,
                "Qt-SQL-Verbindung fehlgeschlagen",
                f"SQLite-Verbindung konnte nicht geöffnet werden:\n{db.lastError().text()}",
            )
            return None

        print(f"[db_backend] Qt SQLite-Verbindung geöffnet: {db.databaseName()}")
        return db

    def ensure_schema(self, conn, cursor, parent):
        """
        Stellt nur die für die Netzübersicht nötigen Tabellen/View sicher.
        Alles auf der aktiven QKan-Datenbank.
        """
        print("[db_backend] ensure_schema()")

        try:
            self.ensure_sinkkaesten_table(conn, cursor, parent)
            self.ensure_entwaesserungsrinnen_table(conn, cursor, parent)
            self.ensure_sonderbauwerke_tables(conn, cursor, parent)
            self.ensure_sonderbauwerke_view(conn, cursor, parent)
            conn.commit()
            print("[db_backend] ensure_schema() erfolgreich")
            return True
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(
                parent,
                "Schema-Fehler",
                f"Schema konnte nicht vorbereitet werden:\n{e}",
            )
            return False

    def table_exists(self, *args):
        """
        Prüft, ob eine Tabelle oder View existiert.

        Unterstützt beide Aufrufarten:
        - table_exists(cursor, table_name)  # neue Verwendung
        - table_exists(table_name)         # alte Verwendung (nutzt self.cursor)
        """
        if len(args) == 2:
            cursor, table_name = args
        elif len(args) == 1:
            table_name = args[0]
            cursor = getattr(self, "cursor", None)
            if cursor is None:
                print("[db_backend] table_exists: kein Cursor verfügbar")
                return False
        else:
            raise TypeError("table_exists erwartet (cursor, table_name) oder (table_name)")

        try:
            clean_name = str(table_name).replace('"', "")
        except Exception as e:
            print(f"[db_backend] table_exists: unerwarteter table_name-Typ {type(table_name)}: {e}")
            return False

        try:
            cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type IN ('table','view') AND name=?",
                (clean_name,),
            )
            row = cursor.fetchone()
            exists = row is not None
            print(f"[db_backend] table_exists('{clean_name}') -> {exists}")
            return exists
        except Exception as e:
            print(f"[db_backend] table_exists('{clean_name}') Fehler: {e}")
            return False

    def get_column_names(self, cursor, table_name):
        """
        Liefert alle Spaltennamen einer Tabelle (für Geometriespalten-Suche).
        """
        try:
            clean_name = table_name.replace('"', "")
        except Exception as e:
            print(f"[db_backend] get_column_names: unerwarteter table_name-Typ {type(table_name)}: {e}")
            return []

        try:
            cursor.execute(f'PRAGMA table_info("{clean_name}")')
            rows = cursor.fetchall()
            cols = [row[1] for row in rows]
            print(f"[db_backend] get_column_names('{clean_name}') -> {cols}")
            return cols
        except Exception as e:
            print(f"[db_backend] get_column_names('{clean_name}') Fehler: {e}")
            return []

    def ensure_sinkkaesten_table(self, conn, cursor, parent):
        table_name = "Sinkkästen"

        if self.table_exists(cursor, table_name):
            print(f'✅ Tabelle "{table_name}" existiert bereits')
            return True

        print(f'➕ Erzeuge Tabelle "{table_name}"')

        cursor.execute(
            '''
            CREATE TABLE "Sinkkästen" (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                Strasse TEXT,
                Bemerkung TEXT,
                geop TEXT
            )
            '''
        )
        return True

    def ensure_entwaesserungsrinnen_table(self, conn, cursor, parent):
        table_name = "entwaesserungsrinnen"

        if self.table_exists(cursor, table_name):
            print(f'✅ Tabelle "{table_name}" existiert bereits')
            return True

        print(f'➕ Erzeuge Tabelle "{table_name}"')

        cursor.execute(
            """
            CREATE TABLE entwaesserungsrinnen (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                geom_point TEXT,
                geom_line TEXT
            )
            """
        )
        return True

    def ensure_sonderbauwerke_tables(self, conn, cursor, parent):
        tables = [
            "bauwerke_pw",
            "bauwerke_rbf",
            "bauwerke_rkb",
            "bauwerke_rrb",
            "bauwerke_rue",
            "bauwerke_rueb",
            "bauwerke_vs",
            "bauwerke_rv",
        ]

        for table_name in tables:
            if self.table_exists(cursor, table_name):
                print(f"✅ Tabelle {table_name} existiert bereits")
                continue

            print(f"➕ Erzeuge Tabelle {table_name}")
            cursor.execute(
                f"""
                CREATE TABLE {table_name} (
                    pk INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    system TEXT,
                    strasse TEXT
                )
                """
            )

        return True

    def ensure_sonderbauwerke_view(self, conn, cursor, parent):
        view_name = "sonderbauwerke_view"

        tables = [
            "bauwerke_pw",
            "bauwerke_rbf",
            "bauwerke_rkb",
            "bauwerke_rrb",
            "bauwerke_rue",
            "bauwerke_rueb",
            "bauwerke_vs",
            "bauwerke_rv",
        ]

        print(f"➕ Erzeuge/aktualisiere View {view_name}")

        cursor.execute(f'DROP VIEW IF EXISTS "{view_name}"')

        union_sql = " UNION ALL ".join(
            [
                f"""
                SELECT
                    '{t}' AS source_table,
                    '{t}' || '_' || rowid AS original_id,
                    name,
                    '{t}' AS typ,
                    system,
                    strasse,
                    geop
                FROM "{t}"
                """
                for t in tables
            ]
        )

        cursor.execute(f'CREATE VIEW "{view_name}" AS {union_sql}')

        try:
            cursor.execute(
                "DELETE FROM views_geometry_columns WHERE view_name = ?",
                (view_name,),
            )
        except Exception as e:
            print(f"[sonderbauwerke_view] cleanup views_geometry_columns fehlgeschlagen: {e}")

        try:
            cursor.execute(
                """
                INSERT INTO views_geometry_columns
                (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (view_name, "geop", "original_id", "bauwerke_pw", "geop", 1),
            )
            print(f"✅ Spatial View {view_name} registriert")
        except Exception as e:
            print(f"❌ Registrierung Spatial View fehlgeschlagen: {e}")

        conn.commit()
        return True

    def get_sinkkaesten_table_name(self):
        return "Sinkkästen"

    def get_sonderbauwerke_union_part(self, table_name):
        return (
            f"SELECT name, '{table_name}' AS typ, system, strasse, '{table_name}' AS quelle "
            f'FROM "{table_name}"'
        )

    def load_data_into_tables(self, widget):
        from .table_models import load_data_into_tables
        return load_data_into_tables(widget)

    def load_data_for_tab(self, widget, idx):
        from .table_models import load_data_for_tab
        return load_data_for_tab(widget, idx)

    def update_object(self, table_name, key_field, key_value, changes, cursor, conn, model=None):
        """
        Generisches SQLite-Update.
        """
        clean_table = table_name.replace('"', "")

        fields = []
        values = []

        for field, value in changes.items():
            if field == key_field:
                continue

            fields.append(f'"{field}" = ?')

            if value is None:
                values.append(None)
            elif isinstance(value, str):
                v = value.strip()
                values.append(None if v == "" or v.upper() == "NULL" else v)
            else:
                values.append(value)

        if not fields:
            return

        sql = f'UPDATE "{clean_table}" SET {", ".join(fields)} WHERE "{key_field}" = ?'
        values.append(key_value)

        print(f"[db_backend] update_object SQL = {sql}")
        print(f"[db_backend] update_object values = {values}")

        cursor.execute(sql, values)
        conn.commit()

        if model is not None:
            try:
                model.select()
            except Exception:
                pass

    def delete_rows(self, sql_model, source_rows):
        """
        Löscht Zeilen über das Qt-Modell.
        """
        for row in sorted(set(source_rows), reverse=True):
            sql_model.removeRow(row)

        if not sql_model.submitAll():
            err = sql_model.lastError().text()
            sql_model.revertAll()
            raise RuntimeError(err)

    def cleanup(self, widget):
        """
        Schließt Qt- und Native-Verbindungen sauber.
        """
        print("[db_backend] cleanup()")

        try:
            if hasattr(widget, "db") and widget.db is not None:
                connection_name = widget.db.connectionName()
                print(f"[db_backend] schließe Qt-Verbindung: {connection_name}")
                widget.db.close()
                widget.db = None
                try:
                    QSqlDatabase.removeDatabase(connection_name)
                except Exception as e:
                    print(f"[db_backend] removeDatabase warning: {e}")
        except Exception as e:
            print(f"[db_backend] Qt cleanup error: {e}")

        try:
            if hasattr(widget, "cursor") and widget.cursor is not None:
                widget.cursor.close()
                widget.cursor = None
        except Exception as e:
            print(f"[db_backend] cursor cleanup error: {e}")

        try:
            if hasattr(widget, "conn") and widget.conn is not None:
                widget.conn.close()
                widget.conn = None
        except Exception as e:
            print(f"[db_backend] native connection cleanup error: {e}")