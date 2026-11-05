# qkan/netzuebersicht/db_backend.py
"""
Datenbank-Backend der Netzübersicht (wird auch von anderen QKan-Modulen
genutzt, z.B. Untersuchungsverwaltung, Datenbankviewer, Sanierungsmanagement).

Aufbau:
- BaseBackend       gemeinsame Logik; alle SQL-Statements kommen aus
                    sqlite.yml bzw. postgres.yml (siehe db_sql.py)
- SpatialiteBackend Verbindung zur aktiven QKan-SpatiaLite-Datenbank (aktiv)
- PostgresBackend   Verbindung zu einer QKan-PostgreSQL-Datenbank
                    (vorbereitet für die spätere PostgreSQL-Unterstützung)

get_backend() wählt das Backend anhand des Datenbanktyps; ohne Angabe wird
QKan.dbtype ausgewertet.
"""
import os
import re
import sqlite3
import uuid

from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QMessageBox
from qgis.utils import plugins

from . import db_sql


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
    Liefert den Datenbanktyp des aktiven QKan-Projekts ('spatialite' oder
    'postgis'). Grundlage ist QKan.dbtype; ohne Angabe 'spatialite'.
    """
    try:
        from qkan import QKan
        return db_sql.normalize_dbtype(getattr(QKan, "dbtype", None))
    except Exception:
        return db_sql.DBTYPE_SPATIALITE


def get_backend(db_type=None):
    """
    Liefert das passende Backend.

    :param db_type: 'spatialite' / 'postgis' (auch QKan-Enum). Ohne Angabe
                    wird get_db_type() verwendet.
    """
    if db_type is None:
        db_type = get_db_type()
    if db_sql.normalize_dbtype(db_type) == db_sql.DBTYPE_POSTGIS:
        return PostgresBackend()
    return SpatialiteBackend()


# ======================================================================
# GEMEINSAME LOGIK
# ======================================================================

class BaseBackend:
    """Gemeinsame, datenbankunabhängige Logik. SQL ausschließlich aus yml."""

    db_type = db_sql.DBTYPE_SPATIALITE

    # View sonderbauwerke_view bei jedem Start neu erzeugen?
    VIEW_NEU_ERSTELLEN = True

    SONDERBAUWERKE_TABELLEN = [
        "bauwerke_pw",
        "bauwerke_rbf",
        "bauwerke_rkb",
        "bauwerke_rrb",
        "bauwerke_rue",
        "bauwerke_rueb",
        "bauwerke_vs",
        "bauwerke_rv",
    ]

    SINKKAESTEN_TABELLE = "Sinkkästen"
    RINNEN_TABELLE = "entwaesserungsrinnen"
    SONDERBAUWERKE_VIEW = "sonderbauwerke_view"

    def __init__(self):
        self.config = {}

    # ------------------------------------------------------------------
    # SQL-Zugriff
    # ------------------------------------------------------------------

    @property
    def sqls(self):
        return db_sql.load_sqls(self.db_type)

    def get_sql(self, sqlnam, replacefun=None, **platzhalter):
        """
        SQL-Text zu sqlnam aus der yml-Datei des Backends.
        {Platzhalter} können als Schlüsselwörter übergeben werden.
        Liefert None, wenn der Eintrag für diesen Datenbanktyp null ist.
        """
        if platzhalter and replacefun is None:
            replacefun = lambda sql: sql.format(**platzhalter)  # noqa: E731
        return db_sql.get_sql(self.db_type, sqlnam, replacefun)

    def hat_sql(self, sqlnam):
        """True, wenn für diesen Datenbanktyp ein Statement hinterlegt ist."""
        return self.sqls.get(sqlnam) is not None

    def execute(self, cursor, sqlnam, parameters=(), replacefun=None, **platzhalter):
        """
        Führt sqlnam auf cursor aus.
        Gibt False zurück (ohne Ausführung), wenn der Eintrag null ist.
        """
        sql = self.get_sql(sqlnam, replacefun, **platzhalter)
        if sql is None:
            return False
        if isinstance(parameters, list):
            parameters = tuple(parameters)
        cursor.execute(sql, parameters)
        return True

    def platzhalter(self, anzahl=1):
        """Kommagetrennte Parameter-Platzhalter ('?,?' bzw. '%s,%s')."""
        return db_sql.platzhalter(self.db_type, anzahl)

    @staticmethod
    def ident(name):
        """Tabellen-/Spaltenname in doppelten Anführungszeichen."""
        return db_sql.ident(name)

    def geom_aus_wkt(self):
        """Werte-Fragment für eine Geometrie aus WKT (EPSG 25832)."""
        return self.get_sql("nz_geom_aus_wkt")

    # ------------------------------------------------------------------
    # Metadaten
    # ------------------------------------------------------------------

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
            self.execute(cursor, "nz_objekt_existiert", (clean_name,))
            exists = cursor.fetchone() is not None
            print(f"[db_backend] table_exists('{clean_name}') -> {exists}")
            return exists
        except Exception as e:
            print(f"[db_backend] table_exists('{clean_name}') Fehler: {e}")
            self._rollback_still(cursor)
            return False

    def get_columns(self, cursor, table_name):
        """Liefert [(spaltenname, datentyp_klein), ...] einer Tabelle."""
        clean_name = str(table_name).replace('"', "")
        try:
            self.execute(cursor, "nz_spalten", (clean_name,))
            return [(row[1], str(row[2] or "").lower()) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[db_backend] get_columns('{clean_name}') Fehler: {e}")
            self._rollback_still(cursor)
            return []

    def get_column_names(self, cursor, table_name):
        """Liefert alle Spaltennamen einer Tabelle (für Geometriespalten-Suche)."""
        cols = [name for name, _ in self.get_columns(cursor, table_name)]
        print(f"[db_backend] get_column_names('{table_name}') -> {cols}")
        return cols

    def count_rows(self, cursor, table_name):
        """Anzahl der Datensätze (für Diagnoseausgaben); None bei Fehler."""
        try:
            self.execute(cursor, "nz_anzahl", tabelle=self.ident(table_name))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"[db_backend] count_rows('{table_name}') Fehler: {e}")
            self._rollback_still(cursor)
            return None

    def _rollback_still(self, cursor):
        """Rollback nach Fehlern (in PostgreSQL nötig, um weiterarbeiten zu können)."""
        try:
            conn = getattr(cursor, "connection", None)
            if conn is not None and self.db_type == db_sql.DBTYPE_POSTGIS:
                conn.rollback()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def ensure_schema(self, conn, cursor, parent):
        """
        Stellt die für die Netzübersicht nötigen Tabellen/View sicher.
        Alles auf der aktiven QKan-Datenbank.
        """
        print("[db_backend] ensure_schema()")

        try:
            self._optionaler_schritt(conn, cursor, parent, "nz_postgis_extension",
                                     "PostGIS-Extension")
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

    def _optionaler_schritt(self, conn, cursor, parent, sqlnam, titel, **platzhalter):
        """Führt ein optionales Statement aus; Fehler werden nur als Hinweis gemeldet."""
        if not self.hat_sql(sqlnam):
            return False
        try:
            self.execute(cursor, sqlnam, **platzhalter)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[db_backend] {titel} übersprungen: {e}")
            QMessageBox.warning(
                parent,
                titel,
                f"{titel}: Schritt konnte nicht ausgeführt werden.\n"
                f"Ggf. muss dies einmalig ein Datenbank-Administrator erledigen.\n\n{e}",
            )
            return False

    def _tabelle_anlegen(self, conn, cursor, parent, table_name, sqlnam):
        if self.table_exists(cursor, table_name):
            print(f'✅ Tabelle "{table_name}" existiert bereits')
            return False
        print(f'➕ Erzeuge Tabelle "{table_name}"')
        self.execute(cursor, sqlnam, tabelle=self.ident(table_name))
        conn.commit()
        return True

    def ensure_sinkkaesten_table(self, conn, cursor, parent):
        self._tabelle_anlegen(conn, cursor, parent, self.SINKKAESTEN_TABELLE,
                              "nz_sinkkaesten_create")
        if self.table_exists(cursor, "symbole"):
            self._optionaler_schritt(conn, cursor, parent, "nz_sinkkaesten_import_symbole",
                                     "Import Sinkkästen aus symbole")
        return True

    def ensure_entwaesserungsrinnen_table(self, conn, cursor, parent):
        self._tabelle_anlegen(conn, cursor, parent, self.RINNEN_TABELLE,
                              "nz_rinnen_create")
        if self.table_exists(cursor, "symbole"):
            self._optionaler_schritt(conn, cursor, parent, "nz_rinnen_import_symbole",
                                     "Import Entwässerungsrinnen aus symbole")
        return True

    def ensure_sonderbauwerke_tables(self, conn, cursor, parent):
        for table_name in self.SONDERBAUWERKE_TABELLEN:
            self._tabelle_anlegen(conn, cursor, parent, table_name,
                                  f"nz_sbw_create_{table_name}")
        return True

    def ensure_sonderbauwerke_view(self, conn, cursor, parent):
        view_name = self.SONDERBAUWERKE_VIEW

        if not self.VIEW_NEU_ERSTELLEN and self.table_exists(cursor, view_name):
            print(f"✅ View {view_name} existiert bereits")
            return True

        print(f"➕ Erzeuge/aktualisiere View {view_name}")
        self.execute(cursor, "nz_sbw_view_loeschen")

        teile = [
            self.get_sql(
                "nz_sbw_view_teil",
                tabelle=self.ident(t),
                tabelle_name=t,
                kuerzel=self.sbw_kuerzel(t),
            )
            for t in self.SONDERBAUWERKE_TABELLEN
        ]
        self.execute(cursor, "nz_sbw_view_erstellen", union=" UNION ALL ".join(teile))

        try:
            self.execute(cursor, "nz_sbw_view_registrierung_loeschen", (view_name,))
        except Exception as e:
            print(f"[sonderbauwerke_view] cleanup views_geometry_columns fehlgeschlagen: {e}")

        if self.hat_sql("nz_sbw_view_registrieren"):
            try:
                self.execute(
                    cursor,
                    "nz_sbw_view_registrieren",
                    (view_name, "geop", "original_id", "bauwerke_pw", "geop", 1),
                )
                print(f"✅ Spatial View {view_name} registriert")
            except Exception as e:
                print(f"❌ Registrierung Spatial View fehlgeschlagen: {e}")

        conn.commit()
        return True

    # ------------------------------------------------------------------
    # Sonderbauwerke / Tabellenanzeige
    # ------------------------------------------------------------------

    @staticmethod
    def sbw_kuerzel(table_name):
        """'bauwerke_pw' -> 'pw'"""
        return str(table_name).replace('"', "").replace("bauwerke_", "")

    def sbw_id_spalte(self, table_name):
        """ID-Spalte einer bauwerke_*-Tabelle (PostgreSQL: z.B. pw_id)."""
        return self.ident(f"{self.sbw_kuerzel(table_name)}_id")

    def get_sinkkaesten_table_name(self):
        return self.SINKKAESTEN_TABELLE

    def get_sonderbauwerke_union_part(self, table_name):
        clean = str(table_name).replace('"', "")
        return self.get_sql("nz_sbw_union_teil", tabelle=self.ident(clean), tabelle_name=clean)

    def get_sonderbauwerke_union_sql(self, vorhandene_tabellen):
        """Gesamte Abfrage für die Sonderbauwerke-Tabelle der Netzübersicht."""
        if not vorhandene_tabellen:
            return self.get_sql("nz_sbw_union_leer")
        return " UNION ALL ".join(
            self.get_sonderbauwerke_union_part(t) for t in vorhandene_tabellen
        )

    def load_data_into_tables(self, widget):
        from .table_models import load_data_into_tables
        return load_data_into_tables(widget)

    def load_data_for_tab(self, widget, idx):
        from .table_models import load_data_for_tab
        return load_data_for_tab(widget, idx)

    # ------------------------------------------------------------------
    # Schreibzugriffe
    # ------------------------------------------------------------------

    def zuweisungen(self, spalten):
        """'"a" = ?, "b" = ?' für eine Spaltenliste."""
        ph = self.platzhalter(1)
        return ", ".join(f"{self.ident(c)} = {ph}" for c in spalten)

    QUELL_EPSG = 25832  # KBS der in der Netzübersicht gezeichneten/eingegebenen Geometrien

    def geometrie_srid(self, cursor, table_name, geom_spalte):
        """SRID einer Geometriespalte laut geometry_columns (None, wenn unbekannt)."""
        try:
            self.execute(cursor, "nz_geometrie_srid",
                         (str(table_name).replace('"', ""), str(geom_spalte).replace('"', "")))
            row = cursor.fetchone()
            return int(row[0]) if row and row[0] is not None else None
        except Exception as e:
            print(f"[db_backend] geometrie_srid({table_name}.{geom_spalte}) Fehler: {e}")
            self._rollback_still(cursor)
            return None

    def geometrie_vorbereiten(self, geom, ziel_srid):
        """
        Bereitet eine QgsGeometry zum Speichern vor:
        - Z/M-Werte entfernen (QKan-Spalten sind 2D, sonst greift die
          Geometrie-Prüfung von SpatiaLite)
        - bei abweichendem SRID von EPSG:25832 in das Ziel-KBS transformieren
        Rückgabe: WKB (bytes)
        """
        from qgis.core import (
            QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject,
        )

        if isinstance(geom, str):
            geom = QgsGeometry.fromWkt(geom)
        geom = QgsGeometry(geom)
        abstract = geom.get()
        if abstract is not None:
            abstract.dropZValue()
            abstract.dropMValue()

        if ziel_srid and int(ziel_srid) != self.QUELL_EPSG:
            transform = QgsCoordinateTransform(
                QgsCoordinateReferenceSystem.fromEpsgId(self.QUELL_EPSG),
                QgsCoordinateReferenceSystem.fromEpsgId(int(ziel_srid)),
                QgsProject.instance(),
            )
            geom.transform(transform)

        return bytes(geom.asWkb())

    def insert_row(self, cursor, table_name, daten, geometrie=None):
        """
        INSERT eines Datensatzes.

        :param daten:      {spalte: wert}; leere Werte (None) werden NICHT
                           eingefügt, damit die DEFAULT-Werte der Tabelle greifen
                           (z.B. schaechte.schachttyp = 'Schacht').
        :param geometrie:  optional (geometriespalte, QgsGeometry oder WKT).
                           Gespeichert wird als WKB im SRID der Zielspalte.
        """
        daten = {k: v for k, v in daten.items() if v is not None}
        spalten = [self.ident(c) for c in daten.keys()]
        werte = [self.platzhalter(1)] * len(daten)
        params = list(daten.values())

        if geometrie is not None:
            geom_spalte, geom = geometrie
            srid = self.geometrie_srid(cursor, table_name, geom_spalte) or self.QUELL_EPSG
            spalten.append(self.ident(geom_spalte))
            werte.append(self.get_sql("nz_geom_aus_wkb", srid=int(srid)))
            params.append(self.geometrie_vorbereiten(geom, srid))

        self.execute(
            cursor,
            "nz_insert",
            params,
            tabelle=self.ident(table_name),
            spalten=", ".join(spalten),
            werte=", ".join(werte),
        )

    def update_object(self, table_name, key_field, key_value, changes, cursor, conn, model=None):
        """Generisches Update eines Datensatzes über sein Schlüsselfeld."""
        fields = []
        values = []

        for field, value in changes.items():
            if field == key_field:
                continue

            fields.append(field)

            if value is None:
                values.append(None)
            elif isinstance(value, str):
                v = value.strip()
                values.append(None if v == "" or v.upper() == "NULL" else v)
            else:
                values.append(value)

        if not fields:
            return

        values.append(key_value)
        sql_args = dict(
            tabelle=self.ident(table_name),
            zuweisungen=self.zuweisungen(fields),
            schluessel=self.ident(key_field),
        )
        print(f"[db_backend] update_object SQL = {self.get_sql('nz_update_objekt', **sql_args)}")
        print(f"[db_backend] update_object values = {values}")

        self.execute(cursor, "nz_update_objekt", values, **sql_args)
        conn.commit()

        if model is not None:
            from .table_models import modell_vollstaendig_laden
            modell_vollstaendig_laden(model)

    def ist_schreibgesperrt(self, cursor):
        """
        Prüft vor Schreibzugriffen, ob die Datenbank gesperrt ist
        (nur SQLite; für PostgreSQL immer False).
        """
        if not self.hat_sql("nz_sperre_beginn"):
            return False

        self.execute(cursor, "nz_sperre_wartezeit_aus")
        try:
            self.execute(cursor, "nz_sperre_beginn")
            self.execute(cursor, "nz_sperre_ende")
            return False
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "database is locked" in msg or "database is busy" in msg:
                try:
                    self.execute(cursor, "nz_sperre_ende")
                except Exception:
                    pass
                return True
            raise

    def schreib_wartezeit_setzen(self, cursor):
        """Wartezeit für Schreibzugriffe (nur SQLite)."""
        self.execute(cursor, "nz_sperre_wartezeit_an")

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


# ======================================================================
# SPATIALITE
# ======================================================================

class SpatialiteBackend(BaseBackend):
    """
    Nutzt ausschließlich die aktuell von QKan bereitgestellte Datenquelle.
    Kein PostgreSQL-Fallback, kein JSON-Fallback.
    """

    db_type = db_sql.DBTYPE_SPATIALITE
    VIEW_NEU_ERSTELLEN = True

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

            self.config = config
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

            self.config = config
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
            test_cur.execute(self.get_sql("nz_verbindungstest"))
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
        # bei kurzzeitigen Sperren bis zu 5 s warten statt sofort abzubrechen
        db.setConnectOptions("QSQLITE_BUSY_TIMEOUT=5000")

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

    def layer_source(self, config, table, geomcol, pkcol="pk", fallback_path=None):
        """Datenquelle für einen QGIS-Layer: (uri, provider) oder None."""
        from qgis.core import QgsDataSourceUri

        db_path = (config or {}).get("path") or fallback_path
        if not db_path:
            return None
        uri = QgsDataSourceUri()
        uri.setDatabase(db_path)
        uri.setDataSource("", str(table).replace('"', ""), geomcol, "", pkcol)
        return uri.uri(False), "spatialite"


# ======================================================================
# POSTGRESQL (vorbereitet)
# ======================================================================

class PostgresBackend(BaseBackend):
    """
    Backend für eine QKan-PostgreSQL/PostGIS-Datenbank.

    Vorbereitet für die spätere PostgreSQL-Unterstützung in QKan:
    Die Verbindungsdaten werden aus der QKan-Datenquelle (QKan.dbsource,
    QGIS-URI eines postgres-Layers) gelesen. Alle SQL-Statements stammen aus
    postgres.yml. Noch nicht mit einer produktiven Datenbank getestet.
    """

    db_type = db_sql.DBTYPE_POSTGIS
    VIEW_NEU_ERSTELLEN = False

    def _config_aus_dbsource(self, dbsource):
        from qgis.core import QgsDataSourceUri

        uri = QgsDataSourceUri(str(dbsource or ""))
        return {
            "host": uri.host(),
            "port": uri.port() or "5432",
            "database": uri.database(),
            "user": uri.username(),
            "password": uri.password(),
            "service": uri.service(),
            "sslmode": uri.param("sslmode") if uri.hasParam("sslmode") else "",
            "schema": uri.schema() or "public",
            "driver": "QPSQL",
            "raw_dbsource": dbsource,
        }

    def load_native_connection_from_qkan(self, parent, dbsource):
        """psycopg2-Verbindung aus der QKan-Datenquelle."""
        if not dbsource:
            return self.load_native_connection(parent)

        try:
            import psycopg2
        except ImportError:
            QMessageBox.critical(
                parent,
                "PostgreSQL",
                "Das Python-Paket psycopg2 ist nicht installiert.",
            )
            return None, None, None

        config = self._config_aus_dbsource(dbsource)
        params = {}
        if config["service"]:
            params["service"] = config["service"]
        for key, pg_key in (("host", "host"), ("port", "port"), ("database", "dbname"),
                            ("user", "user"), ("password", "password"), ("sslmode", "sslmode")):
            if config.get(key):
                params[pg_key] = config[key]

        try:
            conn = psycopg2.connect(**params)
            cursor = conn.cursor()
            self.execute(cursor, "nz_suchpfad", schema=self.ident(config["schema"]))
            conn.commit()
            self.config = config
            print(f"[db_backend] PostgreSQL-Verbindung geöffnet: {config['database']} "
                  f"(Schema {config['schema']})")
            return conn, cursor, config
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Fehler beim Öffnen der QKan-Datenbank",
                f"Die PostgreSQL-Datenbank konnte nicht geöffnet werden:\n{e}",
            )
            return None, None, None

    def load_native_connection(self, parent):
        qkan_instance = get_qkan_instance()
        raw_dbsource = getattr(qkan_instance, "dbsource", None) if qkan_instance else None
        if not raw_dbsource:
            try:
                from qkan import QKan
                raw_dbsource = getattr(QKan, "dbsource", None)
            except Exception:
                raw_dbsource = None
        if not raw_dbsource:
            QMessageBox.critical(
                parent,
                "Keine QKan-Datenbank",
                "Es ist keine aktive QKan-Datenbank verfügbar.",
            )
            return None, None, None
        return self.load_native_connection_from_qkan(parent, raw_dbsource)

    def build_connection_name(self, prefix="netzuebersicht"):
        return f"{prefix}_{uuid.uuid4().hex}"

    def setup_qt_connection(self, config, parent, connection_name=None):
        """Qt-SQL-Verbindung (QPSQL) mit denselben Verbindungsdaten."""
        if not connection_name:
            connection_name = self.build_connection_name()
        try:
            if QSqlDatabase.contains(connection_name):
                QSqlDatabase.removeDatabase(connection_name)
        except Exception as e:
            print(f"[db_backend] removeDatabase warning: {e}")

        db = QSqlDatabase.addDatabase("QPSQL", connection_name)
        if config.get("host"):
            db.setHostName(config["host"])
        if config.get("port"):
            try:
                db.setPort(int(config["port"]))
            except (TypeError, ValueError):
                pass
        db.setDatabaseName(config.get("database") or "")
        db.setUserName(config.get("user") or "")
        db.setPassword(config.get("password") or "")
        optionen = [f"options=-csearch_path={config.get('schema') or 'public'},public"]
        if config.get("service"):
            optionen.append(f"service={config['service']}")
        db.setConnectOptions(";".join(optionen))

        if not db.open():
            QMessageBox.critical(
                parent,
                "Qt-SQL-Verbindung fehlgeschlagen",
                f"PostgreSQL-Verbindung konnte nicht geöffnet werden:\n{db.lastError().text()}",
            )
            return None
        return db

    def layer_source(self, config, table, geomcol, pkcol="pk", fallback_path=None):
        """Datenquelle für einen QGIS-Layer: (uri, provider) oder None."""
        from qgis.core import QgsDataSourceUri

        config = config or self.config
        if not config:
            return None
        uri = QgsDataSourceUri(str(config.get("raw_dbsource") or ""))
        uri.setDataSource(config.get("schema") or "public",
                          str(table).replace('"', ""), geomcol, "", pkcol)
        return uri.uri(False), "postgres"
