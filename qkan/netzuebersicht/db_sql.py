# qkan/netzuebersicht/db_sql.py
"""
SQL-Verwaltung der Netzübersicht.

Wie in den übrigen QKan-Modulen liegen die SQL-Statements nicht im
Python-Code, sondern in den Dateien

    sqlite.yml    -> SpatiaLite/SQLite (derzeit aktiv)
    postgres.yml  -> PostgreSQL/PostGIS (vorbereitet)

im Modulverzeichnis. Beide Dateien haben dieselben Schlüssel. Der Code ruft
die Statements nur über ihren Namen auf (siehe db_backend.BaseBackend.execute).

Konventionen der yml-Dateien:
- Schlüssel beginnen mit 'nz_' (Modulpräfix Netzübersicht)
- Parameter-Platzhalter: sqlite '?', postgres '%s'
- Variable Teile (Tabellen-/Spaltennamen, IN-Listen, SET-Klauseln) werden als
  {name} notiert und zur Laufzeit per str.format ersetzt (replacefun)
- Ein Eintrag mit dem Wert null (~) bedeutet: Für diesen Datenbanktyp gibt
  es kein Statement, der Schritt wird übersprungen.
- Keine '--'-Kommentare verwenden, da YAML Zeilenumbrüche in doppelt-
  quotierten Strings zu Leerzeichen zusammenfasst. Kommentare nur als /* */.
"""

import os
import sqlite3

import yaml

MODULE_DIR = os.path.dirname(__file__)

DBTYPE_SPATIALITE = "spatialite"
DBTYPE_POSTGIS = "postgis"

_YML_DATEIEN = {
    DBTYPE_SPATIALITE: "sqlite.yml",
    DBTYPE_POSTGIS: "postgres.yml",
}

_PLATZHALTER = {
    DBTYPE_SPATIALITE: "?",
    DBTYPE_POSTGIS: "%s",
}

_cache = {}


def normalize_dbtype(value=None, conn=None):
    """
    Liefert 'spatialite' oder 'postgis'.

    Maßgeblich ist – sofern übergeben – die tatsächlich geöffnete Verbindung
    (sqlite3.Connection -> spatialite, sonst postgis). Andernfalls wird der
    Wert ausgewertet; Strings und das QKan-Enum QKanDBChoice werden
    akzeptiert ('postgis', 'postgres', 'postgresql' -> postgis).
    """
    if conn is not None:
        return DBTYPE_SPATIALITE if isinstance(conn, sqlite3.Connection) else DBTYPE_POSTGIS

    raw = getattr(value, "value", value)
    raw = str(raw or "").strip().lower()
    if raw in ("postgis", "postgres", "postgresql", "pg"):
        return DBTYPE_POSTGIS
    return DBTYPE_SPATIALITE


def load_sqls(dbtype):
    """Lädt (gecacht) die SQL-Statements für den angegebenen Datenbanktyp."""
    dbtype = normalize_dbtype(dbtype)
    if dbtype not in _cache:
        filename = os.path.join(MODULE_DIR, _YML_DATEIEN[dbtype])
        with open(filename, encoding="utf-8") as fr:
            _cache[dbtype] = yaml.safe_load(fr.read()) or {}
    return _cache[dbtype]


def reload_sqls():
    """Leert den Cache (z.B. nach Änderungen an den yml-Dateien)."""
    _cache.clear()


def get_sql(dbtype, sqlnam, replacefun=None):
    """
    Liefert den SQL-Text zu sqlnam (ggf. mit ersetzten {Platzhaltern}).
    Gibt None zurück, wenn der Eintrag für diesen Datenbanktyp null ist.
    """
    sqls = load_sqls(dbtype)
    if sqlnam not in sqls:
        raise KeyError(
            f"SQL '{sqlnam}' nicht in {_YML_DATEIEN[normalize_dbtype(dbtype)]} gefunden"
        )
    sql = sqls[sqlnam]
    if sql is None:
        return None
    if isinstance(sql, str):
        sql = sql.replace("*/ ", "*/\n").strip()
        if replacefun is not None:
            sql = replacefun(sql)
    return sql


def platzhalter(dbtype, anzahl=1):
    """Kommagetrennte Parameter-Platzhalter, z.B. für IN-Listen: '?,?,?'."""
    ph = _PLATZHALTER[normalize_dbtype(dbtype)]
    return ",".join([ph] * max(int(anzahl), 1))


def ident(name):
    """
    Setzt einen Tabellen- oder Spaltennamen in doppelte Anführungszeichen.
    Funktioniert in SQLite und PostgreSQL gleichermaßen (Groß-/Kleinschreibung
    und Umlaute wie "Sinkkästen" bleiben erhalten).
    """
    clean = str(name).strip().replace('"', "")
    return f'"{clean}"'
