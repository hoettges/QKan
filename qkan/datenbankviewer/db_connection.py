"""
db_connection.py - Verbindungslogik für den Datenbankviewer
Verwendet ausschließlich die aktuell in QKan geöffnete SpatiaLite-/SQLite-Datenbank.
"""

import os
import re
import sqlite3

from PyQt6.QtWidgets import QMessageBox
from qgis.utils import plugins


# =========================================================
# QKan-Instanz ermitteln
# =========================================================
def get_qkan_instance():
    """
    Liefert die laufende QKan-Instanz aus den geladenen QGIS-Plugins.
    """
    return plugins.get("qkan")


# =========================================================
# SQLite-Pfad aus QKan-Source extrahieren
# =========================================================
def extract_sqlite_path_from_qkan_source(dbsource):
    """
    Extrahiert den SQLite-Dateipfad aus einem QGIS-Data-Source-String wie:
    dbname='C:/.../projekt.sqlite' table="schaechte" (geop) sql=...

    Falls dbsource bereits direkt ein Dateipfad ist, wird dieser unverändert zurückgegeben.
    """
    if not dbsource:
        return None

    dbsource = str(dbsource).strip()
    print(f"[db_connection] raw dbsource = {dbsource}")

    # Fall 1: Bereits direkter Dateipfad
    if os.path.isfile(dbsource):
        print(f"[db_connection] dbsource ist bereits ein Dateipfad: {dbsource}")
        return dbsource

    # Fall 2: dbname='...'
    match = re.search(r"dbname='([^']+)'", dbsource)
    if match:
        path = match.group(1)
        print(f"[db_connection] extrahierter Pfad aus dbname='...': {path}")
        return path

    # Fall 3: dbname="..."
    match = re.search(r'dbname="([^"]+)"', dbsource)
    if match:
        path = match.group(1)
        print(f'[db_connection] extrahierter Pfad aus dbname="...": {path}')
        return path

    print("[db_connection] Kein SQLite-Pfad aus dbsource extrahierbar")
    return None


# =========================================================
# SpatiaLite initialisieren
# =========================================================
def init_spatialite(conn):
    """
    Aktiviert SpatiaLite-Funktionen für eine native sqlite3-Verbindung
    und testet anschließend, ob GeomFromText verfügbar ist.
    """
    print("[db_connection] init_spatialite()")

    try:
        conn.enable_load_extension(True)
        print("[db_connection] enable_load_extension(True) erfolgreich")
    except Exception as e:
        print(f"[db_connection] enable_load_extension fehlgeschlagen: {e}")
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
            print(f"[db_connection] SpatiaLite-Erweiterung geladen: {ext}")
            break
        except Exception as e:
            last_error = e
            print(f"[db_connection] load_extension('{ext}') fehlgeschlagen: {e}")

    if not loaded_ext:
        print(f"[db_connection] Keine SpatiaLite-Erweiterung ladbar. Letzter Fehler: {last_error}")
        return False

    try:
        test_cur = conn.cursor()
        test_cur.execute("SELECT GeomFromText('POINT(0 0)', 25832)")
        result = test_cur.fetchone()
        print(f"[db_connection] GeomFromText verfügbar: {result is not None}")
        test_cur.close()
        return True
    except Exception as e:
        print(f"[db_connection] GeomFromText NICHT verfügbar: {e}")
        return False


# =========================================================
# QKan-SpatiaLite-Verbindung laden
# =========================================================
def load_qkan_connection(parent=None):
    """
    Baut eine native sqlite3-Verbindung ausschließlich aus der aktiven
    QKan-Datenquelle auf.
    """
    qkan_instance = get_qkan_instance()
    raw_dbsource = getattr(qkan_instance, "dbsource", None) if qkan_instance else None
    db_path = extract_sqlite_path_from_qkan_source(raw_dbsource)

    print("[db_connection] load_qkan_connection()")
    print(f"[db_connection] qkan_instance = {qkan_instance}")
    print(f"[db_connection] raw_dbsource = {raw_dbsource}")
    print(f"[db_connection] db_path = {db_path}")

    if not raw_dbsource:
        QMessageBox.critical(
            parent,
            "Keine QKan-Datenbank",
            "Es ist keine aktive QKan-Datenbank verfügbar.\n"
            "Bitte öffne zuerst eine QKan-Datenbank und starte danach den Datenbankviewer erneut.",
        )
        return None

    if not db_path:
        QMessageBox.critical(
            parent,
            "QKan-Datenquelle ungültig",
            f"Der SQLite-Pfad konnte nicht aus der QKan-Datenquelle extrahiert werden:\n{raw_dbsource}",
        )
        return None

    if not os.path.exists(db_path):
        QMessageBox.critical(
            parent,
            "QKan-Datenbank nicht gefunden",
            f"Die von QKan verwendete Datenbankdatei existiert nicht:\n{db_path}",
        )
        return None

    try:
        conn = sqlite3.connect(db_path)
        init_spatialite(conn)
        print(f"[db_connection] SQLite-/SpatiaLite-Verbindung geöffnet: {db_path}")
        return conn
    except Exception as e:
        QMessageBox.critical(
            parent,
            "Fehler beim Öffnen der QKan-Datenbank",
            f"Die QKan-Datenbank konnte nicht geöffnet werden:\n{e}",
        )
        return None


# =========================================================
# Kompatibilitätsfunktion
# =========================================================
def loadpostgresconnection(self):
    """
    Kompatibilitätsfunktion:
    Der alte Name bleibt bestehen, liefert jetzt aber die aktive
    QKan-SpatiaLite-Verbindung statt einer PostgreSQL-Verbindung.
    """
    return load_qkan_connection(self)


# =========================================================
# Verbindungsparameter für Altcode
# =========================================================
def getpostgresparams(self=None):
    """
    Kompatibilitätsfunktion für Altcode.
    Gibt keine PostgreSQL-Daten mehr zurück, sondern Informationen
    zur aktuell aktiven QKan-Datenquelle.
    """
    qkan_instance = get_qkan_instance()
    raw_dbsource = getattr(qkan_instance, "dbsource", None) if qkan_instance else None
    db_path = extract_sqlite_path_from_qkan_source(raw_dbsource)

    return {
        "db_type": "spatialite",
        "database": db_path,
        "path": db_path,
        "raw_dbsource": raw_dbsource,
    }