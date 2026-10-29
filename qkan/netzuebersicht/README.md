# Netzübersicht

Modul des QGIS-Plugins **QKan** (`qkan/netzuebersicht`).
Die Netzübersicht zeigt die Objekte des Kanalnetzes der aktiven QKan-Datenbank
(Haltungen, Schächte, Anschlussleitungen, Sinkkästen, Entwässerungsrinnen,
Sonderbauwerke) in Tabellen an. Von dort aus lassen sich Objekte in der Karte
anzeigen, bearbeiten, neu anlegen, löschen und auswerten.

Stand: Oktober 2026. Die SQL-Statements liegen wie in den übrigen QKan-Modulen in
`sqlite.yml` und `postgres.yml`. Aktiv ist SpatiaLite. PostgreSQL ist vorbereitet,
aber noch nicht gegen eine echte Datenbank getestet.

---

## Inhalt

1. [Dateien im Modulordner](#1-dateien-im-modulordner)
2. [Start und Datenbankanbindung](#2-start-und-datenbankanbindung)
3. [Bedienung](#3-bedienung)
4. [Funktionen im Detail](#4-funktionen-im-detail)
5. [Datenmodell](#5-datenmodell)
6. [SQL-Verwaltung (sqlite.yml / postgres.yml)](#6-sql-verwaltung-sqliteyml--postgresyml)
7. [Backend-Schnittstelle (`db_backend.py`)](#7-backend-schnittstelle-db_backendpy)
8. [PostgreSQL-Unterstützung – Stand und nächste Schritte](#8-postgresql-unterstützung--stand-und-nächste-schritte)
9. [Code-Referenz](#9-code-referenz)
10. [Erweitern und Warten](#10-erweitern-und-warten)
11. [Hinweise und bekannte Punkte](#11-hinweise-und-bekannte-punkte)

---

## 1. Dateien im Modulordner

| Datei | Inhalt |
|---|---|
| `__init__.py` | Paketkennzeichnung |
| `application.py` | `NetzuebersichtPlugin`: registriert den Button „Netzübersicht“ in der Toolbar „QKan-Allgemein“, öffnet den Dialog und räumt beim Entladen die Verbindungen auf. Eingebunden in `qkan/__init__.py`. |
| `netzuebersicht_db_dialog.py` | Hauptdialog `Netzuebersicht_DB`: DB-Erkennung, Verbindungsaufbau, Tabellen, Filter, Buttons, Objektinfo, Löschen |
| `res/Netzübersicht.ui` | Qt-Designer-Datei des Hauptdialogs |
| `db_backend.py` | Datenbank-Backend (`BaseBackend`, `SpatialiteBackend`, `PostgresBackend`). Wird auch von anderen QKan-Modulen genutzt. |
| `db_sql.py` | Laden der SQL-Statements aus den yml-Dateien, Platzhalter- und Quoting-Hilfen |
| `sqlite.yml` | SQL-Statements für SpatiaLite/SQLite |
| `postgres.yml` | dieselben Statements für PostgreSQL/PostGIS |
| `table_models.py` | Laden der Tabellen in `QSqlTableModel`/`QSqlQueryModel`, Filter, Spaltenauswahl |
| `gis_actions.py` | Kartenfunktionen: Objekt anzeigen/selektieren, Layer importieren, Schacht/Haltung/Sinkkasten erzeugen, Haltung teilen, Kartenwerkzeuge |
| `object_info_dialog.py` | `ObjectInfoDialog`: Attribute eines Objekts bearbeiten |
| `sonderbauwerke.py` | Sonderbauwerke anlegen, bearbeiten, löschen (dynamische Formulare) |
| `geometry_tools.py` | Polygon- und Punktgeometrie für ein neu angelegtes Sonderbauwerk zeichnen und speichern |
| `excel_import_sinkkaesten.py` | Excel-Import von Sinkkasten-Attributen (inkl. Reinigungsdaten) |
| `export_investigations.py` | Export von Untersuchungsdaten nach Excel |
| `datenbankExporter.py` | Hilfsklassen für den Export: `DatenbankExporter` (Excel, Steuerzeichen bereinigen), `ColumnSelectionOrderDialog` (Spaltenauswahl/-reihenfolge, als JSON speicherbar), `DataTypeSelectionDialog` |
| `untersuchungs_viewer.py` | Öffnet den QKan-Medieninspektor für genau ein ausgewähltes Objekt |
| `PanoramoPruefer.py`, `panoramo_check.py` | Prüfung, ob zu den selektierten Haltungen Panoramo-Dateien (`.ipf`) vorhanden sind |
| `ausgabe_reinigungslisten.py` | `LinePolygonAggregateDialog`: Linien mit den Attributen überlagernder Polygone anreichern (Reinigungslisten) |
| `kostenermittlung_wrapper.py` | Öffnet die Kostenermittlung der Untersuchungsverwaltung für die Auswahl |
| `Netzübersicht.png` | Icon |
| `backup_…/` | Sicherung vor dem Umbau. Im Unterordner `bei_bereinigung_entfernt` liegen die nicht mehr benötigten Dateien (siehe Kapitel 11). Kann gelöscht werden, wenn alles läuft. |

---

## 2. Start und Datenbankanbindung

1. QGIS starten und ein **QKan-Projekt laden**.
2. In der Toolbar **QKan-Allgemein** auf **Netzübersicht** klicken. Jeder Klick erzeugt den Dialog neu; ein offener Dialog wird vorher geschlossen.

Ablauf in `Netzuebersicht_DB.__init__`:

1. **DB-Erkennung**: Ist `QKan.dbsource` leer, sucht der Dialog in den Projektlayern einen
   SpatiaLite- oder PostgreSQL-Layer einer bekannten QKan-Tabelle (`haltungen`, `schaechte`,
   `anschlussleitungen`, `entwaesserungsrinnen`, `sonderbauwerke_view`, `Sinkkästen`)
   und übernimmt dessen Datenquelle. Bei einem PostgreSQL-Layer wird zusätzlich `QKan.dbtype` auf PostGIS gesetzt.
2. **Backend**: `get_db_type()` wertet `QKan.dbtype` aus; `get_backend()` liefert
   `SpatialiteBackend` oder `PostgresBackend`.
3. **Native Verbindung** (`sqlite3` bzw. `psycopg2`) aus der QKan-Datenquelle; sie dient für SQL-Abfragen und Schreibzugriffe.
4. **Schema sicherstellen** (`ensure_schema`, Kapitel 5).
5. **Qt-SQL-Verbindung** (`QSQLITE` bzw. `QPSQL`) auf dieselbe Datenbank für die Tabellenmodelle.
6. Tabellen laden, Spaltenfilter füllen, Signale verbinden.

Beim Entladen des Plugins schließt `backend.cleanup()` beide Verbindungen.

---

## 3. Bedienung

### Tabs

| Tab | Tabelle | Schlüsselspalte | QGIS-Layer |
|---|---|---|---|
| Haltungen | `haltungen` | `haltnam` | Haltungen |
| Schächte | `schaechte` | `schnam` | Schächte |
| GAL | `anschlussleitungen` | `leitnam` | Anschlussleitungen |
| Sinkkästen | `Sinkkästen` (auch `Sinkkaesten`, `sinkkaesten`) | `Name` | Sinkkästen |
| Rinnen | `entwaesserungsrinnen` | `Name` | Rinnen |
| Sonderbauwerke | Vereinigung aller `bauwerke_*` | `name` | Sonderbauwerke (`sonderbauwerke_view`) |
| Einleitstellen, Kleinkläranlagen | in der UI vorhanden, noch ohne Funktion | | |

Die Tabellen der ersten fünf Tabs sind direkt editierbar (`QSqlTableModel`, manuelles Speichern).
Die Sonderbauwerke werden schreibgeschützt über eine UNION-Abfrage angezeigt.

### Suche und Filter

- **Suche**: Textfilter für den aktuellen Tab, wird 1 Sekunde nach der letzten Eingabe angewendet.
- **Spalte wählen**: Filter auf eine Spalte begrenzen („Alle Spalten“ = alle).
- Beim Tabwechsel werden Daten und Spaltenliste neu geladen.

### Buttons

| Button | Funktion | Tabs |
|---|---|---|
| Objekt anzeigen | Auswahl in der Karte selektieren und darauf zoomen; lädt den Layer bei Bedarf nach | alle |
| Layer importieren | QGIS-Layer des aktuellen Tabs aus der Datenbank laden (mit Stil aus `templates/qml`) | alle |
| Objektinformationen | Attribute des ausgewählten Objekts bearbeiten (Sonderbauwerke: Bearbeiten-Dialog) | alle |
| Untersuchungen anzeigen | QKan-Medieninspektor für ein Objekt öffnen | Haltungen, Schächte, GAL |
| Untersuchungsdaten exportieren | Untersuchungsdaten nach Excel exportieren | Haltungen, Schächte, GAL |
| Kostenermittlung TV | Auswahl in der Karte selektieren und die Kostenermittlung öffnen | Haltungen |
| Kontrolle Panoramodaten | fehlende Panoramo-Dateien der selektierten Haltungen auflisten | Haltungen |
| Reinigungsliste ausgeben | Linien mit Polygon-Attributen anreichern | Haltungen |
| Haltung erstellen / teilen / löschen | siehe Kapitel 4 | Haltungen |
| Schacht erstellen / löschen | siehe Kapitel 4 | Schächte |
| Excel-Import | Sinkkasten-Attribute aus Excel übernehmen | Sinkkästen |
| Sinkkasten erstellen / löschen | siehe Kapitel 4 | Sinkkästen |
| Sonderbauwerk anlegen / bearbeiten / löschen | siehe Kapitel 4 | Sonderbauwerke |

---

## 4. Funktionen im Detail

### Objekt anzeigen / selektieren (`gis_actions.zoom_to_selected_features`, `select_feature`)

Die Schlüsselwerte der markierten Zeilen werden als QGIS-Ausdruck
`"schluessel" IN ('…')` auf den Layer angewendet. Fehlt der Layer, wird er nach Rückfrage
geladen. Dabei sucht das Tool die passende Tabellen- und Geometrievariante
(z.B. `Sinkkästen.geom` oder `Sinkkästen.geop`).

### Layer importieren (`layer_import_aktuell`, `get_layer_source`)

Die Datenquelle liefert das Backend (`layer_source`): SpatiaLite-URI mit Dateipfad bzw.
PostgreSQL-URI aus der QKan-Datenquelle mit Schema. Wenn vorhanden, wird ein Stil aus `qkan/templates/qml/` angewendet.

### Objektinformationen (`Netzuebersicht_DB.show_object_info`, `ObjectInfoDialog`)

- Zeigt alle Attribute des markierten Objekts in einem zweispaltigen Formular.
- Haltungen: **Schacht oben/unten übernehmen** (Schacht in der Karte anklicken) und **Länge neu berechnen** (aus der Layergeometrie).
- **Speichern** schreibt die Änderungen über `backend.update_object` (`nz_update_objekt`).
  Geometrie- und Schlüsselspalten werden dabei nicht verändert. Leere Felder und „NULL“ werden als NULL gespeichert.

### Schacht erstellen (`erzeuge_schacht`)

1. Methode wählen: **Punkt zeichnen**, **X/Y-Koordinaten**, **Position auf Haltung**, **Schnittpunkt Hilfskreise**.
2. Attribute im Schacht-Dialog eingeben; der Schachtname wird auf Duplikate geprüft.
3. Lage bestimmen; `xsch`/`ysch` werden automatisch gesetzt.
4. SQLite: Vor dem Schreiben prüft `ist_schreibgesperrt`, ob die Datenbank gesperrt ist (z.B. durch andere Werkzeuge). Ist sie gesperrt, bricht das Tool mit einer Meldung ab.
5. INSERT in `schaechte` mit Geometrie in `geop` (`nz_insert` + `nz_geom_aus_wkt`). Danach werden Modell und Layer aktualisiert.

### Haltung erstellen (`erzeuge_haltung`)

Attribute im Haltungs-Dialog eingeben (Schacht oben/unten per Kartenklick übernehmbar),
Linie zeichnen (Snapping aktiv), Länge optional übernehmen. INSERT in `haltungen` mit Geometrie in `geom`.

### Haltung teilen (`teile_haltung`)

Haltung in der Karte selektieren, dann **bestehenden Schacht** anklicken oder einen **neuen Schacht** erzeugen.
Die Haltung wird am Schachtpunkt in zwei Haltungen geteilt (`perform_haltung_split`).
Dafür wird der QGIS-Layer bearbeitet, das funktioniert unabhängig vom Datenbanktyp.

### Sinkkasten erstellen (`erzeuge_sinkkasten`)

Punkt zeichnen oder Koordinaten eingeben, Attribute erfassen (Name wird auf Duplikate geprüft).
INSERT in die Sinkkästen-Tabelle des Modells. Die Geometriespalte (`geop` oder `geom`) wird automatisch erkannt,
`xsk`/`ysk` werden gesetzt, falls die Spalten vorhanden sind.

### Löschen (Haltung, Schacht, Sinkkasten)

Vorschau der betroffenen Namen (max. 15), nach Bestätigung Löschen über das Tabellenmodell (`backend.delete_rows`).

### Excel-Import Sinkkästen (`excel_import_sinkkaesten`)

1. Excel-Datei wählen, **Name-Spalte** (Pflicht) und die Zielspalten zuordnen:
   Schacht_oben, Schacht_unten, Entwässerungssystem, Baujahr, Straßenname, Typ, Tiefe,
   Schmutzfänger, Material, Bemerkung, aktuellste_Reinigung, vorherige_Reinigung.
2. Es werden nur **vorhandene** Sinkkästen aktualisiert (Abgleich über `Name`). Nicht gefundene Zeilen werden übersprungen und gezählt.
3. **Typ** wird aus den Excel-Spalten *Nassschlamm*, *Trockenschlamm*, *Bergeinlauf* gebildet (Eintrag „X“), z.B. `Nassschlamm-Bergeinlauf`.
4. **Reinigung**: Ist ein neues Datum angegeben und weicht es vom gespeicherten ab, wird das bisherige Datum nach `vorherige_Reinigung` verschoben.
5. Tiefe mit Komma wird als Zahl übernommen.

### Untersuchungsdaten exportieren (`export_latest_investigations`)

1. Auswahlbasis: **selektierte Objekte im Layer** oder **markierte Tabellenzeilen**.
2. Objektart: Haltungen (`untersuchdat_haltung`), Schächte (`untersuchdat_schacht`), GAL (`untersuchdat_anschlussleitung`).
3. Exportmodus:
   - **Vollständige Historie** – alle Zeilen (`nz_export_historie`)
   - **Aktuellster Bericht** – alle Zeilen des neuesten `untersuchtag` je Objekt (`nz_export_aktuell`)
   - **Einzelner Eintrag** – eine Zeile je Objekt vom neuesten Datum (`nz_export_einzeln`, Rückfall für alte SQLite-Versionen `nz_export_einzeln_alt`)
4. Zusatzspalten `eigentum`, `strasse`, `material` aus der Objekttabelle, soweit vorhanden. Objekte ohne Untersuchung erscheinen mit ihren Stammdaten.
5. Spaltenauswahl und -reihenfolge im Dialog, dann Speichern als `.xlsx` (über `datenbankExporter.py`).
   Am Ende werden die Objekte ohne Untersuchungsdaten aufgelistet.

### Sonderbauwerke (`sonderbauwerke.py`, `geometry_tools.py`)

- **Anlegen**: Typ wählen (PW, RBF, RKB, RRB, RUE, RÜB, VS, RV → Tabelle `bauwerke_*`). Das Formular wird aus den
  Tabellenspalten erzeugt (`nz_spalten`). Geometrie-, ID- und `pk`-Spalten werden ausgelassen.
  Zahlen und Datumswerte werden passend umgewandelt. Danach fragt das Tool, ob ein Polygon (`geom`) und ein Punkt (`geop`)
  gezeichnet werden sollen (`nz_sbw_geometrie_setzen`, betrifft den zuletzt angelegten Datensatz).
- **Bearbeiten**: Datensatz über den Namen suchen (`nz_sbw_id`), Werte laden (`nz_sbw_datensatz`), speichern (`nz_sbw_update`).
  SQLite spricht den Datensatz über `rowid` an, PostgreSQL über die ID-Spalte (`pw_id`, `rbf_id`, …).
- **Löschen**: über Name und Quelltabelle (`nz_sbw_loeschen`).

### Weitere Werkzeuge

- **Untersuchungen anzeigen** öffnet `qkan.inspektion.befahrungsmedien.BefahrungsmedienDialog` für genau ein ausgewähltes Objekt (Haltung, Schacht oder Anschlussleitung). Die Befahrungsdaten werden vom Medieninspektor aus seiner eigenen QKan-Datenquelle gelesen.
- **Kontrolle Panoramodaten**: Für jede selektierte Haltung wird `<haltnam>.ipf` in den Verzeichnissen aus
  den je QGIS-Benutzer hinterlegten Ordnern gesucht (`QSettings`: `QKan/Netzuebersicht/PanoramoOrdner` und `QKan/Netzuebersicht/PanoramoSIOrdner`). Beim ersten Check werden diese Ordner abgefragt.
  Fehlende Dateien werden aufgelistet und können in die Zwischenablage kopiert werden.
- **Reinigungsliste ausgeben**: Linien- und Polygonlayer wählen. Jede Linie bekommt im neuen Layer ein Feld
  `polygon_info` mit den Werten aller schneidenden Polygone. Als Alternative steht `native:joinbylocationsummary` bereit.
- **Kostenermittlung TV**: selektiert die markierten Haltungen und öffnet die Kostenermittlung der Untersuchungsverwaltung.

---

## 5. Datenmodell

Gelesen werden die QKan-Tabellen `haltungen`, `schaechte`, `anschlussleitungen`, `untersuchdat_*` und optional `symbole`.
Beim Start legt `ensure_schema` fehlende Zusatztabellen an:

| Objekt | SQLite (`sqlite.yml`) | PostgreSQL (`postgres.yml`) |
|---|---|---|
| `Sinkkästen` | `pk`, `Name`, `Strasse`, `Bemerkung`, `geop` | `Name` (PK), Schacht_oben/-unten, Entwässerungssystem, Baujahr, Straßenname, Typ, Tiefe, Schmutzfänger, Material, Bemerkung, aktuellste/vorherige_Reinigung, `geom` (Point) |
| `entwaesserungsrinnen` | `pk`, `Name`, `geom_point`, `geom_line` | `Name` (PK), Stammdaten, Länge, `geom_point`, `geom_line` |
| `bauwerke_pw` … `bauwerke_rv` | `pk`, `name`, `system`, `strasse` | vollständige Fachspalten je Typ, ID-Spalte `<kürzel>_id`, `geol`/`geom`/`geop` |
| `sonderbauwerke_view` | UNION aller Bauwerkstabellen mit `source_table`, `original_id` (Tabelle_rowid), `name`, `typ`, `system`, `strasse`, `geop`; wird bei jedem Start neu erstellt und in `views_geometry_columns` registriert | UNION mit `quelle`, `id` (`pw_1` …), `name`, `typ`, `system`, `strasse`, `geop`; wird nur angelegt, wenn er fehlt |

PostgreSQL zusätzlich:
- `CREATE EXTENSION postgis` (nur mit Admin-Rechten; sonst nur ein Hinweis)
- Übernahme der Straßeneinläufe (`21/22/23 Straßeneinlauf…`) und Entwässerungsrinnen (`26 Entwässerungsrinne`) aus `symbole`, sofern diese Tabelle existiert

Bestehende Tabellen werden nicht verändert.

---

## 6. SQL-Verwaltung (sqlite.yml / postgres.yml)

Alle SQL-Statements der Netzübersicht liegen in den beiden yml-Dateien.
**Beide Dateien haben dieselben Schlüssel**; der Python-Code ruft nur den Namen auf.

### Regeln

- Schlüssel beginnen mit `nz_`.
- Parameter: `?` (SQLite) bzw. `%s` (PostgreSQL); die Anzahl muss in beiden Dateien gleich sein.
- Variable Teile als `{name}`; die Werte setzt der Code ein (Tabellen- und Spaltennamen bereits in `"…"`).
- **`~` (null)** = für diesen Datenbanktyp nicht nötig, der Schritt wird übersprungen
  (z.B. Sperrprüfung nur SQLite, `symbole`-Import nur PostgreSQL).
- Keine `--`-Kommentare im SQL (YAML fasst die Zeilen zusammen), nur `/* … */`.
- In `sqlite.yml` verweisen die identischen Bauwerkstabellen per YAML-Anker (`&sbw_create` / `*sbw_create`) auf eine Definition.

### Aufruf im Code

```python
backend = self.backend                      # SpatialiteBackend oder PostgresBackend

# Statement mit Parametern
backend.execute(cur, "nz_sbw_loeschen", (name,), tabelle=backend.ident(quelle))

# IN-Liste
backend.execute(
    cur, "nz_export_historie", namen,
    tabelle=backend.ident("untersuchdat_haltung"),
    spalte=backend.ident("untersuchhal"),
    platzhalter=backend.platzhalter(len(namen)),
)

# Komfortfunktionen
backend.insert_row(cur, "schaechte", {"schnam": "S1"}, geometrie=("geop", wkt))
backend.update_object("schaechte", "pk", 17, {"schnam": "S2"}, cur, conn)
```

### Statement-Übersicht

| Gruppe | Schlüssel |
|---|---|
| Verbindung / Metadaten | `nz_verbindungstest`, `nz_suchpfad`, `nz_objekt_existiert`, `nz_spalten`, `nz_anzahl` |
| Schema | `nz_postgis_extension`, `nz_sinkkaesten_create`, `nz_sinkkaesten_import_symbole`, `nz_rinnen_create`, `nz_rinnen_import_symbole`, `nz_sbw_create_<tabelle>` (8×) |
| View | `nz_sbw_view_loeschen`, `nz_sbw_view_teil`, `nz_sbw_view_erstellen`, `nz_sbw_view_registrierung_loeschen`, `nz_sbw_view_registrieren` |
| Anzeige Sonderbauwerke | `nz_sbw_union_teil`, `nz_sbw_union_leer` |
| Schreiben allgemein | `nz_insert`, `nz_update_objekt`, `nz_geom_aus_wkt` |
| Sperrprüfung (SQLite) | `nz_sperre_wartezeit_aus`, `nz_sperre_beginn`, `nz_sperre_ende`, `nz_sperre_wartezeit_an` |
| Sonderbauwerke | `nz_sbw_loeschen`, `nz_sbw_id`, `nz_sbw_datensatz`, `nz_sbw_update`, `nz_sbw_geometrie_setzen` |
| Export | `nz_export_historie`, `nz_export_aktuell`, `nz_export_einzeln`, `nz_export_einzeln_alt`, `nz_export_objektdaten` |
| Excel-Import | `nz_sk_existiert`, `nz_sk_wert_lesen`, `nz_sk_reinigung_verschieben` |

Die Dateien werden beim ersten Zugriff gelesen und zwischengespeichert. Nach Änderungen QGIS bzw. das Plugin neu laden (oder `db_sql.reload_sqls()` aufrufen).

---

## 7. Backend-Schnittstelle (`db_backend.py`)

### Modulfunktionen

| Funktion | Zweck |
|---|---|
| `get_db_type()` | `'spatialite'` oder `'postgis'` aus `QKan.dbtype` |
| `get_backend(db_type=None)` | passendes Backend; akzeptiert Strings und das QKan-Enum |
| `get_qkan_instance()` | laufende QKan-Plugininstanz |
| `extract_sqlite_path_from_qkan_source(dbsource)` | SQLite-Pfad aus einer QGIS-Datenquelle |

### `BaseBackend` (gemeinsam)

| Methode | Zweck |
|---|---|
| `get_sql`, `hat_sql`, `execute`, `platzhalter`, `ident`, `geom_aus_wkt` | SQL aus yml holen und ausführen |
| `table_exists(cursor, name)` / `table_exists(name)` | Tabelle oder View vorhanden? |
| `get_columns`, `get_column_names` | Spalten (Name, Typ) einer Tabelle |
| `count_rows` | Anzahl Datensätze (Diagnose) |
| `ensure_schema` und `ensure_*` | Zusatztabellen und View anlegen |
| `get_sinkkaesten_table_name`, `get_sonderbauwerke_union_part`, `get_sonderbauwerke_union_sql`, `sbw_kuerzel`, `sbw_id_spalte` | Sonderbauwerke/Sinkkästen |
| `insert_row`, `update_object`, `zuweisungen` | Schreibzugriffe |
| `ist_schreibgesperrt`, `schreib_wartezeit_setzen` | Sperrprüfung (nur SQLite wirksam) |
| `load_data_into_tables`, `load_data_for_tab`, `delete_rows`, `cleanup` | Modelle laden/löschen, Verbindungen schließen |

### `SpatialiteBackend`

`load_native_connection`, `load_native_connection_from_qkan` (sqlite3 + SpatiaLite-Erweiterung),
`_init_spatialite`, `build_connection_name`, `setup_qt_connection` (QSQLITE), `layer_source`.

### `PostgresBackend` (vorbereitet)

`load_native_connection_from_qkan` (psycopg2, Verbindungsdaten aus der QGIS-URI inkl. `service`/`sslmode`,
setzt den Suchpfad auf das Schema der Datenquelle und `public`), `load_native_connection`,
`setup_qt_connection` (QPSQL mit gleichem Suchpfad), `layer_source` (Provider `postgres`).

Andere Module rufen das Backend so auf: `get_backend("spatialite")` bzw.
`get_backend(QKan.dbtype)` (Sanierungsmanagement, Untersuchungsverwaltung) und danach
`load_native_connection_from_qkan` / `load_native_connection`. Diese Schnittstelle ist unverändert.
