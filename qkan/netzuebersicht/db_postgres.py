# netzuebersicht/db_postgres.py
import os
import json
import psycopg2
from ..settings.helpers import json_path

from PyQt6.QtWidgets import QMessageBox


def load_postgres_connection(parent):
    config_path = json_path("database.json")
    print("Lade Config-Datei:", os.path.abspath(config_path))

    try:
        with open(config_path, "rb") as f:
            _ = f.read(150)
    except Exception as e:
        print(f"Fehler beim Lesen der Datei im Binärmodus zum Debugging: {e}")

    if not os.path.exists(config_path):
        QMessageBox.critical(
            parent,
            "Fehlende Zugangsdaten",
            "Die Datei database.json existiert nicht. Bitte tragen Sie die Zugangsdaten der Datenbank ein.",
        )
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except UnicodeDecodeError as e_utf8:
        QMessageBox.critical(
            parent,
            "Encoding-Fehler",
            "Die Datei database.json ist nicht korrekt als UTF-8 kodiert.",
        )
        return None
    except json.JSONDecodeError as e_json:
        QMessageBox.critical(
            parent,
            "JSON-Fehler",
            f"Die Datei database.json enthält fehlerhafte JSON-Daten:\n{e_json}",
        )
        return None
    except Exception as e:
        QMessageBox.critical(
            parent,
            "Fehler",
            f"Fehler beim Laden der Datei database.json:\n{e}",
        )
        return None

    db_host = data.get("db_host")
    db_database = "Kanaldatenbank"
    db_user = data.get("db_username")
    db_password = data.get("db_password")

    if not all([db_host, db_database, db_user, db_password]):
        QMessageBox.critical(
            parent,
            "Fehlerhafte Zugangsdaten",
            "Die Datenbankkonfiguration ist unvollständig. Bitte prüfen Sie die Datei.",
        )
        return None

    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_database,
            user=db_user,
            password=db_password,
        )
        return conn
    except psycopg2.OperationalError as e:
        QMessageBox.critical(
            parent,
            "Verbindungsfehler",
            f"Es konnte keine Verbindung zur Datenbank hergestellt werden:\n{e}",
        )
        return None
    except Exception as e:
        QMessageBox.critical(
            parent, "Unbekannter Fehler", f"Unbekannter Fehler:\n{e}"
        )
        return None


def get_postgres_params():
    config_path = json_path("database.json")
    with open(config_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return {
        "host": data.get("db_host"),
        "database": "Kanaldatenbank",
        "user": data.get("db_username"),
        "password": data.get("db_password"),
    }

def table_exists(conn, table_name, schema='public'):
    """Prüft Tabellen-Existenz ohne Berechtigungsfehler."""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            );
        """, (schema, table_name))
        exists = cur.fetchone()[0]
        cur.close()
        return exists
    except Exception:
        return False

def ensure_postgis_tables(conn, cursor, parent):
    try:
        # PostGIS-Extension: nur Superuser / Admin, einmalig einrichten
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            conn.commit()
        except psycopg2.errors.InsufficientPrivilege as e:
            conn.rollback()
            QMessageBox.warning(
                parent,
                "PostGIS-Berechtigung",
                "Die PostGIS-Extension konnte nicht erstellt werden.\n"
                "Dies muss einmalig von einem DB-Admin/Superuser erledigt werden:\n\n"
                "  CREATE EXTENSION postgis;\n\n"
                f"Fehler: {e}"
            )
            # Geht trotzdem weiter, falls PostGIS bereits existiert

        # -------------------------------------------------
        # Tabelle "Sinkkästen" prüfen
        # -------------------------------------------------
        if table_exists(conn, 'Sinkkästen', 'public'):
            print('✅ Tabelle "Sinkkästen" existiert bereits')
        else:
            try:
                cursor.execute(
                    """
                    CREATE TABLE "Sinkkästen" (
                        "Name" TEXT PRIMARY KEY,
                        "Schacht_oben" TEXT,
                        "Schacht_unten" TEXT,
                        "Entwässerungssystem" TEXT,
                        "Baujahr" INTEGER,
                        "Straßenname" TEXT,
                        "Typ" TEXT,
                        "Tiefe" REAL,
                        "Schmutzfänger" TEXT,
                        "Material" TEXT,
                        "Bemerkung" TEXT,
                        "aktuellste_Reinigung" TEXT,
                        "vorherige_Reinigung" TEXT,
                        geom geometry(Point, 25832)
                    );
                    """
                )
                conn.commit()
                print('✅ Tabelle "Sinkkästen" angelegt')
            except psycopg2.errors.InsufficientPrivilege as e:
                conn.rollback()
                QMessageBox.warning(
                    parent,
                    "Berechtigung",
                    'Tabelle "Sinkkästen" existiert nicht und konnte nicht erstellt werden.\n'
                    "Bitte DB-Admin bitten, das Schema-Setup auszuführen.\n\n"
                    f"Fehler: {e}"
                )
                return False

        # Import aus symbole -> Sinkkästen
        try:
            cursor.execute(
                """
                SELECT COUNT(*) FROM symbole
                WHERE art IN ('21 Straßeneinlauf', '22 Straßeneinlauf-SF', '23 Straßeneinlauf-SV')
                """
            )
            count_source = cursor.fetchone()[0]
            if count_source > 0:
                cursor.execute(
                    """
                    INSERT INTO "Sinkkästen" ("Name", geom)
                    SELECT
                        bezeichnung,
                        geom
                    FROM symbole
                    WHERE art IN ('21 Straßeneinlauf', '22 Straßeneinlauf-SF', '23 Straßeneinlauf-SV')
                      AND bezeichnung NOT IN (SELECT "Name" FROM "Sinkkästen");
                    """
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.warning(
                parent, "Importfehler", f'Import in Tabelle "Sinkkästen" aus symbole fehlgeschlagen:\n{e}'
            )

        # -------------------------------------------------
        # Tabelle "entwaesserungsrinnen" prüfen
        # -------------------------------------------------
        if table_exists(conn, 'entwaesserungsrinnen', 'public'):
            print('✅ Tabelle "entwaesserungsrinnen" existiert bereits')
        else:
            try:
                cursor.execute(
                    """
                    CREATE TABLE "entwaesserungsrinnen" (
                        "Name" TEXT PRIMARY KEY,
                        "Schacht_oben" TEXT,
                        "Schacht_unten" TEXT,
                        "Entwässerungssystem" TEXT,
                        "Baujahr" INTEGER,
                        "Straßenname" TEXT,
                        "Typ" TEXT,
                        "Material" TEXT,
                        "Länge" REAL,
                        "Bemerkung" TEXT,
                        geom_point geometry(Point, 25832),
                        geom_line geometry(LineString, 25832)
                    );
                    """
                )
                conn.commit()
                print('✅ Tabelle "entwaesserungsrinnen" angelegt')
            except psycopg2.errors.InsufficientPrivilege as e:
                conn.rollback()
                QMessageBox.warning(
                    parent,
                    "Berechtigung",
                    'Tabelle "entwaesserungsrinnen" existiert nicht und konnte nicht erstellt werden.\n'
                    "Bitte DB-Admin bitten, das Schema-Setup auszuführen.\n\n"
                    f"Fehler: {e}"
                )
                return False

        # Import aus symbole -> entwaesserungsrinnen
        try:
            cursor.execute(
                """
                SELECT COUNT(*) FROM symbole
                WHERE art = '26 Entwässerungsrinne'
                """
            )
            count_source = cursor.fetchone()[0]
            if count_source > 0:
                cursor.execute(
                    """
                    INSERT INTO "entwaesserungsrinnen" ("Name", geom_point)
                    SELECT
                        bezeichnung,
                        geom
                    FROM symbole
                    WHERE art = '26 Entwässerungsrinne'
                      AND bezeichnung NOT IN (
                          SELECT "Name" FROM "entwaesserungsrinnen"
                      );
                    """
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.warning(
                parent, "Importfehler",
                f'Import in Tabelle "entwaesserungsrinnen" aus symbole fehlgeschlagen:\n{e}'
            )

        return True

    except Exception as e:
        QMessageBox.critical(
            parent,
            "Fehler",
            f"Fehler bei Tabellenprüfung/-erstellung:\n{e}",
        )
        conn.rollback()
        return False


def ensure_sonderbauwerke_tables(conn, cursor, parent):
    """
    Erstellt alle benötigten Sonderbauwerks-Tabellen,
    falls sie noch nicht existieren.
    """
    try:
        # Hilfsfunktion für einzelne Tabelle
        def ensure_table(sql_create, table_name):
            if table_exists(conn, table_name, 'public'):
                print(f"✅ Tabelle {table_name} existiert bereits")
                return True
            try:
                cursor.execute(sql_create)
                print(f"✅ Tabelle {table_name} angelegt")
                return True
            except psycopg2.errors.InsufficientPrivilege as e:
                conn.rollback()
                QMessageBox.warning(
                    parent,
                    "Berechtigung",
                    f"Tabelle '{table_name}' existiert nicht und konnte nicht erstellt werden.\n"
                    f"Bitte DB-Admin bitten, das Schema-Setup auszuführen.\n\n"
                    f"Fehler: {e}"
                )
                return False

        # bauwerke_pw
        if not ensure_table(
            """
            CREATE TABLE bauwerke_pw (
                pw_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                betriebszustand varchar(50),
                in_betrieb_seit date,
                anzahl_pumpen integer,
                fabrikat varchar(100),
                pumpe_aufstellung varchar(50),
                foerderhoehe numeric(10,2),
                foerdermenge_pro_pumpe numeric(10,2),
                max_menge numeric(10,2),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_pw",
        ):
            return False

        # bauwerke_rbf
        if not ensure_table(
            """
            CREATE TABLE bauwerke_rbf (
                rbf_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                betriebszustand varchar(50),
                bauform varchar(50),
                bauart varchar(50),
                volumen numeric(10,2),
                filterflaeche numeric(10,2),
                volumen_lamelle numeric(10,2),
                drosselabfluss numeric(10,2),
                maximaler_drosselabfluss numeric(10,2),
                abfluss_lamelle numeric(10,2),
                volumen_behandlungsmenge numeric(10,2),
                afs_belastung numeric(10,2),
                hauptabflussziel varchar(100),
                ueberlaufabflussziel varchar(100),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                jaehrliche_einstaudauer_ist numeric(10,0),
                jaehrliche_einstaudauer_prog numeric(10,0),
                absetzwirkungsgrad_ist numeric(10,0),
                absetzwirkungsgrad_prog numeric(10,0),
                afs_belastung_ablauf_prog numeric(10,0),
                anrechenbares_volumen numeric(10,0),
                abk_massnahme varchar(10),
                abk_nummer varchar(50),
                afs_belastung_zulauf_ist numeric(10,0),
                afs_belastung_zulauf_prog numeric(10,0),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_rbf",
        ):
            return False

        # bauwerke_rkb
        if not ensure_table(
            """
            CREATE TABLE bauwerke_rkb (
                rkb_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                betriebszustand varchar(50),
                volumen numeric(10,2),
                maximaler_drosselabfluss numeric(10,2),
                hauptabflussziel varchar(100),
                ueberlaufabflussziel varchar(100),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                absetzwirkungsgrad_ist numeric(10,0),
                absetzwirkungsgrad_prog numeric(10,0),
                bautyp varchar(10),
                anrechenbares_volumen numeric(10,0),
                drosselabfluss numeric(10,0),
                abk_massnahme varchar(10),
                abk_nummer varchar(50),
                notentlastung varchar(10),
                schwellenhoehe numeric(10,0),
                schwellenlaenge numeric(10,0),
                hoehensystem varchar(10),
                angeschlossene_versiegelte_flaeche_ist numeric(10,0),
                angeschlossene_versiegelte_flaeche_prog numeric(10,0),
                jaehrliche_einstaudauer_ist numeric(10,0),
                jaehrliche_einstaudauer_prog numeric(10,0),
                afs_belastung_ablauf_ist numeric(10,0),
                afs_belastung_ablauf_prog numeric(10,0),
                ueberlaufmenge_ist numeric(10,0),
                ueberlaufmenge_prog numeric(10,0),
                max_ueberlaufmenge_ist numeric(10,0),
                max_ueberlaufmenge_prog numeric(10,0),
                entlastungshaeufigkeit_ist numeric(10,0),
                entlastungshaeufigkeit_prog numeric(10,0),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_rkb",
        ):
            return False

        # bauwerke_rrb
        if not ensure_table(
            """
            CREATE TABLE bauwerke_rrb (
                rrb_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                betriebszustand varchar(50),
                beckentyp varchar(50),
                bauart varchar(50),
                volumen numeric(10,2),
                maximaler_drosselabfluss numeric(10,2),
                abwasserart varchar(50),
                schwellenhoehe numeric(10,2),
                schwellenlaenge numeric(10,2),
                hauptabflussziel varchar(100),
                ueberlaufabflussziel varchar(100),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                absetzwirkungsgrad_ist numeric(10,0),
                absetzwirkungsgrad_prog numeric(10,0),
                anrechenbares_volumen numeric(10,0),
                drosselabfluss numeric(10,0),
                schwellenhoehe_klue numeric(10,0),
                schwellenlaenge_klue numeric(10,0),
                hoehensystem varchar(100),
                angeschlossene_versiegelte_flaeche_ist numeric(10,0),
                angeschlossene_versiegelte_flaeche_prog numeric(10,0),
                jaehrliche_einstaudauer_ist numeric(10,0),
                jaehrliche_einstaudauer_prog numeric(10,0),
                afs_belastung_ablauf_ist numeric(10,0),
                afs_belastung_ablauf_prog numeric(10,0),
                ueberlaufmenge_ist numeric(10,0),
                ueberlaufmenge_prog numeric(10,0),
                max_ueberlaufmenge_ist numeric(10,0),
                max_ueberlaufmenge_prog numeric(10,0),
                entlastungshaeufigkeit_ist numeric(10,0),
                entlastungshaeufigkeit_prog numeric(10,0),
                abk_massnahme varchar(50),
                abk_nummer varchar(50),
                notentlastung varchar(50),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_rrb",
        ):
            return False

        # bauwerke_rue
        if not ensure_table(
            """
            CREATE TABLE bauwerke_rue (
                rue_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                betriebszustand varchar(50),
                drosselmenge numeric(10,2),
                entlastungsrate numeric(10,2),
                maximaler_stauraum_frage numeric(10,2),
                hauptabflussziel varchar(100),
                nebenabflussziel varchar(100),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                bauart varchar(10),
                anrechenbares_volumen numeric(10,0),
                maximaler_drosselabfluss numeric(10,0),
                abk_massnahme varchar(10),
                abk_nummer varchar(50),
                schwellenhoehe numeric(10,0),
                schwellenlaenge numeric(10,0),
                hoehensystem varchar(10),
                angeschlossene_versiegelte_flaeche_ist numeric(10,0),
                angeschlossene_versiegelte_flaeche_prog numeric(10,0),
                entlastungsrate_prog numeric(10,0),
                trockenwetterzufluss_ist numeric(10,0),
                trockenwetterzufluss_prog numeric(10,0),
                afs_belastung_ablauf_ist numeric(10,0),
                afs_belastung_ablauf_prog numeric(10,0),
                ueberlaufmenge_ist numeric(10,0),
                ueberlaufmenge_prog numeric(10,0),
                max_ueberlaufmenge_ist numeric(10,0),
                max_ueberlaufmenge_prog numeric(10,0),
                entlastungshaeufigkeit_ist numeric(10,0),
                entlastungshaeufigkeit_prog numeric(10,0),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_rue",
        ):
            return False

        # bauwerke_rueb
        if not ensure_table(
            """
            CREATE TABLE bauwerke_rueb (
                rueb_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                betriebszustand varchar(50),
                bauform varchar(50),
                bauart varchar(50),
                beckenvolumen numeric(10,2),
                anrechenbares_volumen numeric(10,2),
                angeschlossene_versiegelte_flaeche numeric(10,2),
                schwellenhoehe numeric(10,2),
                maximaler_drosselabfluss numeric(10,2),
                entlastungsrate numeric(10,2),
                drosselwassermenge numeric(10,2),
                mischungsverhaeltnis_prognose numeric(10,2),
                trockenwetterzufluss numeric(10,2),
                hauptabflussziel varchar(100),
                ueberlaufabflussziel varchar(100),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                absetzwirkungsgrad_ist numeric(10,0),
                absetzwirkungsgrad_prog numeric(10,0),
                afs_belastung_ablauf_ist numeric(10,0),
                afs_belastung_ablauf_prog numeric(10,0),
                abk_massnahme varchar(10),
                abk_nummer varchar(50),
                notentlastung varchar(10),
                schwellenhoehe_klue numeric(10,0),
                schwellenlaenge_bue numeric(10,0),
                schwellenlaenge_klue numeric(10,0),
                hoehensystem varchar(100),
                entlastungsrate_prog numeric(10,0),
                trockenwetterzufluss_prog numeric(10,0),
                ang_versiegelte_flaeche_prog numeric(10,0),
                mischungsverhaeltnis_ist numeric(10,0),
                ueberlaufmenge_ist numeric(10,0),
                ueberlaufmenge_prog numeric(10,0),
                max_ueberlaufmenge_ist numeric(10,0),
                max_ueberlaufmenge_prog numeric(10,0),
                entlastungshaeufigkeit_ist numeric(10,0),
                entlastungshaeufigkeit_prog numeric(10,0),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_rueb",
        ):
            return False

        # bauwerke_vs
        if not ensure_table(
            """
            CREATE TABLE bauwerke_vs (
                vs_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                durchfluss numeric(10,2),
                maximaler_durchfluss numeric(10,2),
                durchmesser_min numeric(10,2),
                durchmesser_max numeric(10,2),
                profilform varchar(50),
                laenge numeric(10,2),
                mittleres_gefaelle numeric(10,2),
                hauptabflussziel varchar(100),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_vs",
        ):
            return False

        # bauwerke_rv
        if not ensure_table(
            """
            CREATE TABLE bauwerke_rv (
                rv_id bigserial PRIMARY KEY,
                name TEXT,
                strasse TEXT,
                typ TEXT,
                system TEXT,
                baujahr integer,
                uebernahme_ev_jahr date,
                betriebszustand varchar(50),
                bauform varchar(50),
                volumen numeric(10,2),
                flaeche numeric(10,2),
                vorbehandlung varchar(100),
                bemerkung varchar(1000),
                betriebsstelle_id integer,
                kennung integer,
                ortsname varchar(100),
                anrechenbares_volumen numeric(10,0),
                drosselabfluss_gw numeric(10,0),
                drosselabfluss_kanalnetz numeric(10,0),
                max_drosselabfluss_gw numeric(10,0),
                hauptabflussziel varchar(10),
                ueberlaufabflussziel varchar(10),
                abk_massnahme varchar(10),
                abk_nummer varchar(50),
                notentlastung_gewaesser varchar(10),
                angeschlossene_versiegelte_flaeche_ist varchar(10),
                angeschlossene_versiegelte_flaeche_prog varchar(10),
                jaehrliche_einstaudauer_ist numeric(10,0),
                jaehrliche_einstaudauer_prog numeric(10,0),
                afs_belastung_ablauf_ist numeric(10,0),
                afs_belastung_ablauf_prog numeric(10,0),
                geol geometry(LineString, 25832),
                geom geometry(MultiPolygon, 25832),
                geop geometry(Point, 25832)
            );
            """,
            "bauwerke_rv",
        ):
            return False

        conn.commit()
        return True

    except Exception as e:
        QMessageBox.critical(
            parent,
            "Fehler",
            f"Fehler beim Erstellen der Sonderbauwerks-Tabellen:\n{e}",
        )
        conn.rollback()
        return False

def view_exists(conn, view_name, schema='public'):
    """Prüft, ob ein View existiert (information_schema.views)."""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.views
                WHERE table_schema = %s
                  AND table_name   = %s
            );
        """, (schema, view_name))
        exists = cur.fetchone()[0]
        cur.close()
        return exists
    except Exception:
        return False


def ensure_sonderbauwerke_view(conn, cursor, parent):
    """
    Erzeugt den View sonderbauwerke_view, der alle bauwerke_*
    Tabellen vereinigt und eine einheitliche Geometriespalte geop bereitstellt,
    nur wenn er noch nicht existiert.

    Szenarien:
    - Admin (mit CREATE-Rechten) ruft es beim Erst-Setup auf → View wird erstellt.
    - Normaler User ohne CREATE:
        - View existiert → OK, kein CREATE-Versuch.
        - View existiert NICHT → Hinweis, dass Admin-Setup nötig ist (kein harter Fehler).
    """
    try:
        # 1. Existenzprüfung
        exists = view_exists(conn, 'sonderbauwerke_view', 'public')
        print(f"DEBUG sonderbauwerke_view exists? {exists}")
        if exists:
            print("✅ View sonderbauwerke_view existiert bereits")
            return True

        # 2. View existiert NICHT → versuchen zu erstellen
        try:
            cursor.execute("""
                CREATE VIEW public.sonderbauwerke_view AS
                SELECT
                    'bauwerke_pw'::text AS quelle,
                    ('pw_' || pw_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_pw

                UNION ALL
                SELECT
                    'bauwerke_rbf'::text AS quelle,
                    ('rbf_' || rbf_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_rbf

                UNION ALL
                SELECT
                    'bauwerke_rkb'::text AS quelle,
                    ('rkb_' || rkb_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_rkb

                UNION ALL
                SELECT
                    'bauwerke_rrb'::text AS quelle,
                    ('rrb_' || rrb_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_rrb

                UNION ALL
                SELECT
                    'bauwerke_rue'::text AS quelle,
                    ('rue_' || rue_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_rue

                UNION ALL
                SELECT
                    'bauwerke_rueb'::text AS quelle,
                    ('rueb_' || rueb_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_rueb

                UNION ALL
                SELECT
                    'bauwerke_vs'::text AS quelle,
                    ('vs_' || vs_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_vs

                UNION ALL
                SELECT
                    'bauwerke_rv'::text AS quelle,
                    ('rv_' || rv_id::text) AS id,
                    name,
                    typ,
                    system,
                    strasse,
                    ST_SetSRID(geop::geometry(Point), 25832) AS geop
                FROM public.bauwerke_rv;
            """)
            conn.commit()
            print("✅ View sonderbauwerke_view neu erstellt")
            return True

        except psycopg2.errors.InsufficientPrivilege as e:
            conn.rollback()
            # WICHTIG: Nur meckern, wenn der View wirklich nicht existiert
            # (kann z.B. im Rennen mit einem parallelen Admin-Setup passieren).
            if view_exists(conn, 'sonderbauwerke_view', 'public'):
                print("ℹ️ View wurde parallel von einem anderen Benutzer angelegt")
                return True

            QMessageBox.warning(
                parent,
                "Berechtigung",
                "Der View 'sonderbauwerke_view' konnte nicht erstellt werden.\n"
                "Der Benutzer benötigt CREATE-Rechte auf Schema public.\n\n"
                "Typischer Ablauf:\n"
                "  1. Admin führt das Setup-Skript einmalig aus\n"
                "  2. Plugin-Nutzer nutzen nur noch den bestehenden View\n\n"
                f"Fehler: {e}"
            )
            return False

    except Exception as e:
        conn.rollback()
        QMessageBox.critical(
            parent,
            "Fehler",
            f"Fehler beim Erstellen/Prüfen des Views 'sonderbauwerke_view':\n{e}",
        )
        return False
