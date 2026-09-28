# netzuebersicht/db_spatialite.py
import os
import json
import sqlite3

from PyQt6.QtWidgets import QMessageBox
from qgis.core import QgsVectorLayer, QgsProject, QgsFeatureRequest

from ..settings.helpers import json_path


def load_spatialite_connection(parent):
    """
    Lädt Spatialite-Verbindung.
    Liest Pfad aus 'settings/spatialite.json' und gibt (conn, db_file) zurück.
    Wird von SpatialiteBackend.load_native_connection() verwendet.
    """
    config_path = json_path("spatialite.json")

    if not os.path.exists(config_path):
        QMessageBox.critical(
            parent,
            "Fehlende Konfiguration",
            "Die Datei settings/spatialite.json existiert nicht.",
        )
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except Exception as e:
        QMessageBox.critical(
            parent,
            "Fehler",
            f"Fehler beim Laden der Datei spatialite.json:\n{e}",
        )
        return None

    db_file = data.get("spatialite")

    if not db_file or not os.path.exists(db_file):
        QMessageBox.critical(
            parent,
            "Datenbank nicht gefunden",
            f"Die Spatialite-Datei wurde nicht gefunden:\n'{db_file}'\n\nBitte prüfen Sie die Einstellungen.",
        )
        return None

    try:
        conn = sqlite3.connect(db_file)
        conn.enable_load_extension(True)
        try:
            conn.load_extension("mod_spatialite")
        except Exception:
            # Für reine Tabellenoperationen meist nicht kritisch
            pass

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT InitSpatialMetadata(1)")
        except Exception:
            # Vermutlich bereits initialisiert
            pass
        conn.commit()

        return conn, db_file

    except Exception as e:
        QMessageBox.critical(
            parent,
            "Verbindungsfehler",
            f"Spatialite-Verbindung fehlgeschlagen:\n{e}",
        )
        return None

def ensure_spatialite_entwaesserungsrinnen(conn, cursor, parent):
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entwaesserungsrinnen (
                Name TEXT PRIMARY KEY,
                Schacht_oben TEXT,
                Schacht_unten TEXT,
                "Entwässerungssystem" TEXT,
                Baujahr INTEGER,
                "Straßenname" TEXT,
                Typ TEXT,
                Material TEXT,
                "Länge" REAL,
                Bemerkung TEXT
            );
        """)

        try:
            cursor.execute("""
                SELECT AddGeometryColumn(
                    'entwaesserungsrinnen',
                    'geom_point',
                    25832,
                    'POINT',
                    'XY'
                );
            """)
        except Exception:
            pass

        try:
            cursor.execute("""
                SELECT AddGeometryColumn(
                    'entwaesserungsrinnen',
                    'geom_line',
                    25832,
                    'LINESTRING',
                    'XY'
                );
            """)
        except Exception:
            pass

        try:
            cursor.execute(
                "SELECT CreateSpatialIndex('entwaesserungsrinnen', 'geom_point');"
            )
        except Exception:
            pass

        try:
            cursor.execute(
                "SELECT CreateSpatialIndex('entwaesserungsrinnen', 'geom_line');"
            )
        except Exception:
            pass

        try:
            cursor.execute("""
                INSERT INTO entwaesserungsrinnen (Name, geom_point)
                SELECT
                    bezeichnung,
                    geom
                FROM symbole
                WHERE art = '26 Entwässerungsrinne'
                  AND bezeichnung NOT IN (
                      SELECT Name FROM entwaesserungsrinnen
                  );
            """)
        except Exception as e:
            QMessageBox.warning(
                parent,
                "Importfehler",
                f'Import in Tabelle "entwaesserungsrinnen" aus symbole fehlgeschlagen:\n{e}'
            )

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        QMessageBox.critical(
            parent,
            "Fehler",
            f"Fehler beim Erstellen der Tabelle entwaesserungsrinnen:\n{e}",
        )
        return False

def ensure_spatialite_tables(conn, cursor, parent):
    """Erstellt Spatialite-Tabellen (korrigierte Syntax)."""
    try:
        # 1. Sinkkaesten-Tabelle (ohne Geometrie im CREATE)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sinkkästen (
                Name TEXT PRIMARY KEY,
                Schacht_oben TEXT,
                Schacht_unten TEXT,
                Entwaesserungssystem TEXT,
                Baujahr INTEGER,
                Strassenname TEXT,
                Typ TEXT,
                Tiefe REAL,
                Schmutzfaenger TEXT,
                Material TEXT,
                Bemerkung TEXT,
                aktuellste_Reinigung TEXT,
                vorherige_Reinigung TEXT
            )
        """)

        # 2. Geometriespalte 'geom' sicherstellen
        try:
            cursor.execute("SELECT geom FROM Sinkkästen LIMIT 1")
        except Exception:
            cursor.execute("SELECT InitSpatialMetadata(1)")
            cursor.execute("""
                SELECT AddGeometryColumn('Sinkkästen', 'geom', 25832, 'POINT', 'XY')
            """)

        # 3. Spatial Index
        cursor.execute("SELECT CreateSpatialIndex('Sinkkästen', 'geom')")

        # 4. Import aus 'symbole' (optional)
        try:
            cursor.execute("""
                SELECT count(*) FROM sqlite_master
                WHERE type='table' AND name='symbole'
            """)
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    SELECT COUNT(*) FROM symbole
                    WHERE art IN ('21 Straßeneinlauf', '22 Straßeneinlauf-SF', '23 Straßeneinlauf-SV')
                """)
                if cursor.fetchone()[0] > 0:
                    cursor.execute("""
                        INSERT OR IGNORE INTO Sinkkästen (Name, geom)
                        SELECT bezeichnung, geom
                        FROM symbole
                        WHERE art IN ('21 Straßeneinlauf', '22 Straßeneinlauf-SF', '23 Straßeneinlauf-SV')
                    """)
                    conn.commit()
        except Exception as e:
            print(f"Import Warnung: {e}")

        conn.commit()
        return True

    except Exception as e:
        QMessageBox.critical(parent, "Fehler", f"Fehler bei Spatialite-Tabellen:\n{e}")
        return False


def ensure_sonderbauwerke_tables(conn, cursor, parent):
    """Erstellt alle bauwerke_* Tabellen und Geometry-Spalten in SpatiaLite."""
    try:
        try:
            cursor.execute("SELECT InitSpatialMetadata(1)")
        except Exception:
            pass

        tables_def = {
            "bauwerke_pw": """
                pw_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, betriebszustand VARCHAR(50), in_betrieb_seit DATE,
                anzahl_pumpen INTEGER, fabrikat VARCHAR(100), pumpe_aufstellung VARCHAR(50),
                foerderhoehe REAL, foerdermenge_pro_pumpe REAL, max_menge REAL,
                bemerkung VARCHAR(1000), betriebsstelle_id INTEGER, kennung INTEGER, ortsname VARCHAR(100)
            """,
            "bauwerke_rbf": """
                rbf_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, betriebszustand VARCHAR(50), bauform VARCHAR(50), bauart VARCHAR(50),
                volumen REAL, filterflaeche REAL, volumen_lamelle REAL, drosselabfluss REAL,
                maximaler_drosselabfluss REAL, abfluss_lamelle REAL, volumen_behandlungsmenge REAL,
                afs_belastung REAL, hauptabflussziel VARCHAR(100), ueberlaufabflussziel VARCHAR(100),
                bemerkung VARCHAR(1000), betriebsstelle_id INTEGER, kennung INTEGER, ortsname VARCHAR(100),
                jaehrliche_einstaudauer_ist REAL, jaehrliche_einstaudauer_prog REAL,
                absetzwirkungsgrad_ist REAL, absetzwirkungsgrad_prog REAL,
                afs_belastung_ablauf_prog REAL, anrechenbares_volumen REAL,
                abk_massnahme VARCHAR(10), abk_nummer VARCHAR(50),
                afs_belastung_zulauf_ist REAL, afs_belastung_zulauf_prog REAL
            """,
            "bauwerke_rkb": """
                rkb_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, betriebszustand VARCHAR(50), volumen REAL,
                maximaler_drosselabfluss REAL, hauptabflussziel VARCHAR(100), ueberlaufabflussziel VARCHAR(100),
                bemerkung VARCHAR(1000), betriebsstelle_id INTEGER, kennung INTEGER, ortsname VARCHAR(100),
                absetzwirkungsgrad_ist REAL, absetzwirkungsgrad_prog REAL, bautyp VARCHAR(10),
                anrechenbares_volumen REAL, drosselabfluss REAL, abk_massnahme VARCHAR(10),
                abk_nummer VARCHAR(50), notentlastung VARCHAR(10), schwellenhoehe REAL,
                schwellenlaenge REAL, hoehensystem VARCHAR(10),
                angeschlossene_versiegelte_flaeche_ist REAL, angeschlossene_versiegelte_flaeche_prog REAL,
                jaehrliche_einstaudauer_ist REAL, jaehrliche_einstaudauer_prog REAL,
                afs_belastung_ablauf_ist REAL, afs_belastung_ablauf_prog REAL,
                ueberlaufmenge_ist REAL, ueberlaufmenge_prog REAL,
                max_ueberlaufmenge_ist REAL, max_ueberlaufmenge_prog REAL,
                entlastungshaeufigkeit_ist REAL, entlastungshaeufigkeit_prog REAL
            """,
            "bauwerke_rrb": """
                rrb_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, betriebszustand VARCHAR(50), beckentyp VARCHAR(50), bauart VARCHAR(50),
                volumen REAL, maximaler_drosselabfluss REAL, abwasserart VARCHAR(50),
                schwellenhoehe REAL, schwellenlaenge REAL, hauptabflussziel VARCHAR(100),
                ueberlaufabflussziel VARCHAR(100), bemerkung VARCHAR(1000), betriebsstelle_id INTEGER,
                kennung INTEGER, ortsname VARCHAR(100), absetzwirkungsgrad_ist REAL, absetzwirkungsgrad_prog REAL,
                anrechenbares_volumen REAL, drosselabfluss REAL, schwellenhoehe_klue REAL,
                schwellenlaenge_klue REAL, hoehensystem VARCHAR(100),
                angeschlossene_versiegelte_flaeche_ist REAL, angeschlossene_versiegelte_flaeche_prog REAL,
                jaehrliche_einstaudauer_ist REAL, jaehrliche_einstaudauer_prog REAL,
                afs_belastung_ablauf_ist REAL, afs_belastung_ablauf_prog REAL,
                ueberlaufmenge_ist REAL, ueberlaufmenge_prog REAL,
                max_ueberlaufmenge_ist REAL, max_ueberlaufmenge_prog REAL,
                entlastungshaeufigkeit_ist REAL, entlastungshaeufigkeit_prog REAL,
                abk_massnahme VARCHAR(50), abk_nummer VARCHAR(50), notentlastung VARCHAR(50)
            """,
            "bauwerke_rue": """
                rue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, betriebszustand VARCHAR(50), drosselmenge REAL, entlastungsrate REAL,
                maximaler_stauraum_frage REAL, hauptabflussziel VARCHAR(100), nebenabflussziel VARCHAR(100),
                bemerkung VARCHAR(1000), betriebsstelle_id INTEGER, kennung INTEGER, ortsname VARCHAR(100),
                bauart VARCHAR(10), anrechenbares_volumen REAL, maximaler_drosselabfluss REAL,
                abk_massnahme VARCHAR(10), abk_nummer VARCHAR(50), schwellenhoehe REAL,
                schwellenlaenge REAL, hoehensystem VARCHAR(10),
                angeschlossene_versiegelte_flaeche_ist REAL, angeschlossene_versiegelte_flaeche_prog REAL,
                entlastungsrate_prog REAL, trockenwetterzufluss_ist REAL, trockenwetterzufluss_prog REAL,
                afs_belastung_ablauf_ist REAL, afs_belastung_ablauf_prog REAL,
                ueberlaufmenge_ist REAL, ueberlaufmenge_prog REAL,
                max_ueberlaufmenge_ist REAL, max_ueberlaufmenge_prog REAL,
                entlastungshaeufigkeit_ist REAL, entlastungshaeufigkeit_prog REAL
            """,
            "bauwerke_rueb": """
                rueb_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, betriebszustand VARCHAR(50), bauform VARCHAR(50), bauart VARCHAR(50),
                beckenvolumen REAL, anrechenbares_volumen REAL, angeschlossene_versiegelte_flaeche REAL,
                schwellenhoehe REAL, maximaler_drosselabfluss REAL, entlastungsrate REAL, drosselwassermenge REAL,
                mischungsverhaeltnis_prognose REAL, trockenwetterzufluss REAL, hauptabflussziel VARCHAR(100),
                ueberlaufabflussziel VARCHAR(100), bemerkung VARCHAR(1000), betriebsstelle_id INTEGER,
                kennung INTEGER, ortsname VARCHAR(100), absetzwirkungsgrad_ist REAL, absetzwirkungsgrad_prog REAL,
                afs_belastung_ablauf_ist REAL, afs_belastung_ablauf_prog REAL,
                abk_massnahme VARCHAR(10), abk_nummer VARCHAR(50), notentlastung_gewaesser VARCHAR(10),
                schwellenhoehe_klue REAL, schwellenlaenge_bue REAL, schwellenlaenge_klue REAL,
                hoehensystem VARCHAR(100), entlastungsrate_prog REAL, trockenwetterzufluss_prog REAL,
                ang_versiegelte_flaeche_prog REAL, mischungsverhaeltnis_ist REAL,
                ueberlaufmenge_ist REAL, ueberlaufmenge_prog REAL,
                max_ueberlaufmenge_ist REAL, max_ueberlaufmenge_prog REAL,
                entlastungshaeufigkeit_ist REAL, entlastungshaeufigkeit_prog REAL
            """,
            "bauwerke_vs": """
                vs_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, durchfluss REAL, maximaler_durchfluss REAL,
                durchmesser_min REAL, durchmesser_max REAL, profilform VARCHAR(50),
                laenge REAL, mittleres_gefaelle REAL, hauptabflussziel VARCHAR(100),
                bemerkung VARCHAR(1000), betriebsstelle_id INTEGER, kennung INTEGER, ortsname VARCHAR(100)
            """,
            "bauwerke_rv": """
                rv_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, strasse TEXT, typ TEXT, system TEXT, baujahr INTEGER,
                uebernahme_ev_jahr DATE, betriebszustand VARCHAR(50), bauform VARCHAR(50),
                volumen REAL, flaeche REAL, vorbehandlung VARCHAR(100), bemerkung VARCHAR(1000),
                betriebsstelle_id INTEGER, kennung INTEGER, ortsname VARCHAR(100),
                anrechenbares_volumen REAL, drosselabfluss_gw REAL, drosselabfluss_kanalnetz REAL,
                max_drosselabfluss_gw REAL, hauptabflussziel VARCHAR(10), ueberlaufabflussziel VARCHAR(10),
                abk_massnahme VARCHAR(10), abk_nummer VARCHAR(50), notentlastung_gewaesser VARCHAR(10),
                angeschlossene_versiegelte_flaeche_ist REAL, angeschlossene_versiegelte_flaeche_prog REAL,
                jaehrliche_einstaudauer_ist REAL, jaehrliche_einstaudauer_prog REAL,
                afs_belastung_ablauf_ist REAL, afs_belastung_ablauf_prog REAL
            """
        }

        # Tabellen
        for table_name, columns in tables_def.items():
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

        # Geometry-Spalten
        for table_name in tables_def.keys():
            for col_name, geom_type in (
                ("geol", "LINESTRING"),
                ("geom", "MULTIPOLYGON"),
                ("geop", "POINT"),
            ):
                try:
                    cursor.execute(
                        f"SELECT AddGeometryColumn('{table_name}', '{col_name}', 25832, '{geom_type}', 'XY')"
                    )
                except Exception:
                    pass

        # Spatial Indizes
        for table_name in tables_def.keys():
            for col_name in ("geol", "geom", "geop"):
                try:
                    cursor.execute(
                        f"SELECT CreateSpatialIndex('{table_name}', '{col_name}')"
                    )
                except Exception:
                    pass

        conn.commit()
        return True

    except Exception as e:
        QMessageBox.critical(parent, "Fehler", f"Fehler beim Erstellen der Sonderbauwerks-Tabellen:\n{e}")
        return False


def ensure_sonderbauwerke_view(conn, cursor, parent):
    """Erstellt den VIEW für Sonderbauwerke."""
    try:
        cursor.execute("DROP VIEW IF EXISTS sonderbauwerke_view")

        table_mapping = {
            'bauwerke_pw': 'pw_id',
            'bauwerke_rbf': 'rbf_id',
            'bauwerke_rkb': 'rkb_id',
            'bauwerke_rrb': 'rrb_id',
            'bauwerke_rue': 'rue_id',
            'bauwerke_rueb': 'rueb_id',
            'bauwerke_vs': 'vs_id',
            'bauwerke_rv': 'rv_id'
        }

        union_parts = []
        for table, id_col in table_mapping.items():
            try:
                cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
                part = f"""
                    SELECT 
                        '{table}' AS source_table,
                        {id_col} AS original_id,
                        name, typ, system, strasse,
                        geop
                    FROM {table}
                """
                union_parts.append(part)
            except Exception:
                continue

        if not union_parts:
            return True

        full_query = " UNION ALL ".join(union_parts)
        create_view_sql = f"CREATE VIEW sonderbauwerke_view AS {full_query}"

        cursor.execute(create_view_sql)
        conn.commit()
        return True

    except Exception as e:
        QMessageBox.critical(parent, "Fehler", f"Fehler beim Erstellen des Views:\n{e}")
        return False
