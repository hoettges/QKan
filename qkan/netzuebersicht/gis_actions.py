# netzuebersicht/gis_actions.py
import os
import math
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QPushButton, QMessageBox, QLabel, QLayout, QHBoxLayout, QFrame, QVBoxLayout, QInputDialog, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QLocale, QVariant
from qgis.core import (
    QgsProject,
    QgsSymbol,
    QgsSymbolLayer,
    QgsFeatureRequest,
    QgsDataSourceUri,
    QgsVectorLayer,
    QgsGeometry, 
    QgsPointXY,
    QgsPoint,
    QgsFeature,
    QgsWkbTypes,
    edit,
    Qgis,
    QgsFillSymbol,
    QgsSingleSymbolRenderer,
    QgsRuleBasedRenderer,
    QgsMarkerSymbol,
    QgsVectorLayerSimpleLabeling,
    QgsPalLayerSettings,
    QgsTextFormat,
    QgsTextBufferSettings,
    QgsLineSymbol,
    QgsProperty
)
from qgis.gui import QgsMapToolEmitPoint, QgsMapToolIdentify
from qgis.utils import iface
from PyQt6.QtGui import QCursor, QDoubleValidator, QColor, QFont
from qgis.PyQt.QtCore import NULL

# =============================================================================
# HELPER & MAPPING
# =============================================================================

# def erzeuge_schacht_direct(parent):
#     """
#     Schacht erstellen ohne Netzübersicht-Tabellenmodelle:
#     - DB-Typ wird über get_db_type() ermittelt.
#     - SpatiaLite: direkter sqlite3-INSERT in 'schaechte' (nur geop, geom bleibt unberührt).
#     - Postgres: hier nur Hinweis.
#     """
#     from qgis.core import QgsProject, QgsGeometry, QgsPointXY, Qgis
#     from PyQt5.QtWidgets import QMessageBox, QDialog
#     import sqlite3
#     from .db_backend import get_db_type, get_backend

#     # DB-Typ und Backend
#     db_type = get_db_type()
#     backend = get_backend(db_type)

#     conn, cursor, config = backend.load_native_connection(parent)
#     if conn is None:
#         QMessageBox.critical(parent, "Fehler", "Keine native DB-Verbindung.")
#         return

#     is_spatialite = (db_type == "spatialite")

#     # Methodenauswahl
#     msg = QMessageBox(parent)
#     msg.setIcon(QMessageBox.Question)
#     msg.setWindowTitle("Schacht erstellen")
#     msg.setText("Wie soll der Schacht erstellt werden?")

#     btn_zeichnen = msg.addButton("🖊️ Punkt zeichnen", QMessageBox.AcceptRole)
#     btn_koordinaten = msg.addButton("📍 X/Y-Koordinaten", QMessageBox.ActionRole)
#     btn_linie = msg.addButton("📏 Position auf Haltung", QMessageBox.ActionRole)
#     btn_kreise = msg.addButton("⭕ Schnittpunkt Hilfskreise", QMessageBox.ActionRole)
#     btn_cancel = msg.addButton(QMessageBox.Cancel)

#     msg.exec_()

#     if msg.clickedButton() == btn_cancel:
#         return

#     if msg.clickedButton() == btn_zeichnen:
#         methode = "zeichnen"
#     elif msg.clickedButton() == btn_koordinaten:
#         methode = "koordinaten"
#     elif msg.clickedButton() == btn_linie:
#         methode = "linie"
#     elif msg.clickedButton() == btn_kreise:
#         methode = "kreise"
#     else:
#         return

#     # Attributdialog (ohne Model)
#     dlg = SchachtDialogDirect(parent)
#     if dlg.exec_() == QDialog.Rejected:
#         return

#     # Koordinate bestimmen
#     if methode == "zeichnen":
#         point = methode_punkt_zeichnen(parent)
#     elif methode == "koordinaten":
#         point = methode_koordinaten_eingabe(parent)
#     elif methode == "linie":
#         point = methode_position_auf_linie(parent)
#     elif methode == "kreise":
#         point = methode_schnittpunkt_kreise(parent)
#     else:
#         point = None

#     if point is None:
#         return

#     xsch_value = f"{point.x():.3f}"
#     ysch_value = f"{point.y():.3f}"

#     # Attribute sammeln
#     schnam = dlg.edits.get("schnam").text().strip() if "schnam" in dlg.edits else ""

#     if not is_spatialite:
#         QMessageBox.information(
#             parent,
#             "Info",
#             "Direkter Schacht-Insert ist aktuell nur für SpatiaLite implementiert.\n"
#             "Für PostgreSQL nutze bitte weiter die Netzübersicht.",
#         )
#         return

#     # SpatiaLite: direkter INSERT
#     try:
#         cursor.execute("PRAGMA busy_timeout = 5000")

#         cols = []
#         vals = []
#         params = []

#         for name, edit in dlg.edits.items():
#             if name.lower() in ["pk", "geop", "geom", "ogc_fid", "rowid"]:
#                 continue
#             val = edit.text().strip()
#             val = val.replace(",", ".")
#             if val == "":
#                 val = None
#             cols.append(name)
#             vals.append("?")
#             params.append(val)

#         if "xsch" not in cols:
#             cols.append("xsch")
#             vals.append("?")
#             params.append(xsch_value)
#         if "ysch" not in cols:
#             cols.append("ysch")
#             vals.append("?")
#             params.append(ysch_value)

#         geom = QgsGeometry.fromPointXY(point)
#         cols.append("geop")
#         vals.append("GeomFromText(?, 25832)")
#         params.append(geom.asWkt())

#         sql = f"INSERT INTO schaechte ({', '.join(cols)}) VALUES ({', '.join(vals)})"

#         try:
#             cursor.execute(sql, params)
#             conn.commit()
#         except sqlite3.OperationalError as e:
#             msg_txt = str(e).lower()
#             if "database is locked" in msg_txt or "database is busy" in msg_txt:
#                 QMessageBox.warning(
#                     parent,
#                     "Datenbank gesperrt",
#                     "Beim Einfügen des Schachtes ist die SpatiaLite-Datenbank gesperrt.\n\n"
#                     "Bitte schließen Sie andere Zugriffe (z.B. DB-Viewer, andere Dialoge) und "
#                     "versuchen Sie es erneut.",
#                 )
#                 try:
#                     conn.rollback()
#                 except Exception:
#                     pass
#                 return
#             else:
#                 raise

#         # Layer-Refresh nur für Anzeige (wenn vorhanden)
#         try:
#             layers = QgsProject.instance().mapLayersByName("Schächte")
#             if layers:
#                 l = layers[0]
#                 l.dataProvider().forceReload()
#                 l.triggerRepaint()
#                 l.updateExtents()
#         except Exception:
#             pass

#         iface.messageBar().pushMessage(
#             "✅ Erfolg", "Schacht gespeichert (SpatiaLite, direkter Insert)!", Qgis.Success
#         )

#     except Exception as e:
#         try:
#             conn.rollback()
#         except Exception:
#             pass
#         QMessageBox.critical(parent, "Fehler (SpatiaLite)", str(e))
#     finally:
#         try:
#             conn.close()
#         except Exception:
#             pass

# Mapping-Helper (Zentral definiert für alle Methoden)
def get_layer_mapping(tab_index):
    mapping = {
        0: {
            "layer": "Haltungen",
            "col": "haltnam",
            "tables": ["haltungen"],
            "geoms": ["geom"],
            "qml": "Haltungen.qml",
            "pk": "pk",
        },
        1: {
            "layer": "Schächte",
            "col": "schnam",
            "tables": ["schaechte", "schächte"],
            "geoms": ["geop", "geom"],
            "qml": "Schächte.qml",
            "pk": "pk",
        },
        2: {
            "layer": "Anschlussleitungen",
            "col": "leitnam",
            "tables": ["anschlussleitungen"],
            "geoms": ["geom"],
            "qml": "HA-Leitungen.qml",
            "pk": "pk",
        },
        3: {
            "layer": "Sinkkästen",
            "col": "Name",
            "tables": ["Sinkkästen", "Sinkkaesten", "sinkkaesten"],
            "geoms": ["geom", "geop"],
            "qml": "Sinkkästen.qml",
            "pk": "Name",
        },
        4: {
            "layer": "Rinnen",
            "col": "Name",
            "tables": ["entwaesserungsrinnen", "entwässerungsrinnen"],
            "geoms": ["geom_point", "geompoint", "geom_line", "geop"],
            "qml": "Rinnen.qml",
            "pk": "Name",
        },
        5: {
            "layer": "Sonderbauwerke",
            "col": "name",
            "tables": ["sonderbauwerke_view", "sonderbauwerkeview"],
            "geoms": ["geop", "geom"],
            "qml": "Sonderbauwerke.qml",
            "pk": "id",
        },
    }
    return mapping.get(tab_index)

def get_layer_source(self, table, geomcol, pkcol="pk"):
    from qgis.core import QgsDataSourceUri
    uri = QgsDataSourceUri()

    # DB-Pfad direkt aus bestehender Verbindung holen
    db_path = None
    if hasattr(self, "backend") and hasattr(self.backend, "config"):
        db_path = self.backend.config.get("path")
    if not db_path and hasattr(self, "db"):
        db_path = self.db.databaseName()
    if not db_path:
        return None

    uri.setDatabase(db_path)
    # kein Schema, kein SQL-Filter
    uri.setDataSource("", table, geomcol, "", pkcol)
    return uri.uri(False), "spatialite"

# =============================================================================
# NAVIGATION FUNCTIONS (Zoom, Select, Import)
# =============================================================================

def zoom_to_selected_features(self, retry=False):
    """Zoomt auf selektierte Features (Postgres & Spatialite kompatibel)."""
    current_index = self.tab_Overview.currentIndex()
    info = get_layer_mapping(current_index)

    if not info:
        QMessageBox.warning(self, "Ungültiger Tab", "Dieser Tab wird nicht unterstützt.")
        return

    if current_index == 0:
        table_view, model, proxy = (
            self.tableView_Haltungen,
            self.model_haltungen,
            self.proxy_model_haltungen,
        )
    elif current_index == 1:
        table_view, model, proxy = (
            self.tableView_Schaechte,
            self.model_schaechte,
            self.proxy_model_schaechte,
        )
    elif current_index == 2:
        table_view, model, proxy = (
            self.tableView_GAL,
            self.model_anschlussleitungen,
            self.proxy_model_anschlussleitungen,
        )
    elif current_index == 3:
        table_view, model, proxy = (
            self.tableView_Sinkkaesten,
            self.model_sinkkaesten,
            self.proxy_model_sinkkaesten,
        )
    elif current_index == 4:
        table_view, model, proxy = (
            self.tableView_Rinnen,
            self.model_rinnen,
            self.proxy_model_rinnen,
        )
    elif current_index == 5:
        table_view, model, proxy = (
            self.tableView_Sonderbauwerke,
            self.model_sonderbauwerke,
            self.proxy_model_sonderbauwerke,
        )
    else:
        QMessageBox.warning(self, "Ungültiger Tab", "Dieser Tab wird nicht unterstützt.")
        return

    layer_name = info["layer"]
    column_name = info["col"]

    selection_model = table_view.selectionModel()
    if not selection_model or not selection_model.hasSelection():
        QMessageBox.warning(self, "Keine Auswahl", "Bitte wählen Sie Einträge aus.")
        return

    if hasattr(model, "record"):
        col_idx = model.record().indexOf(column_name)
    else:
        col_idx = model.fieldIndex(column_name)

    if col_idx < 0:
        QMessageBox.warning(
            self, "Fehler", f"Spalte '{column_name}' im Datenmodell nicht gefunden."
        )
        return

    selected_indexes = selection_model.selection().indexes()
    unique_rows = set(idx.row() for idx in selected_indexes)

    values = []
    for row_num in unique_rows:
        proxy_idx = proxy.index(row_num, 0)
        source_idx = proxy.mapToSource(proxy_idx)
        target_idx = source_idx.sibling(source_idx.row(), col_idx)
        val = model.data(target_idx, Qt.DisplayRole)

        if val is not None:
            safe_val = str(val).replace("'", "''")
            values.append(f"'{safe_val}'")

    if not values:
        QMessageBox.warning(
            self, "Info", "Keine gültigen Werte in der Auswahl gefunden."
        )
        return

    layer_list = QgsProject.instance().mapLayersByName(layer_name)
    if not layer_list:
        if not retry:
            if (
                QMessageBox.question(
                    self,
                    "Laden?",
                    f"Layer '{layer_name}' laden?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                == QMessageBox.Yes
            ):
                # NEU: Tabellen-/Geometrievariante wie im Import ermitteln
                table_candidates = info.get("tables", [])
                geom_candidates = info.get("geoms", [])
                pk_name = info.get("pk", "pk")

                found_table = None
                found_geom = None

                for table_name in table_candidates:
                    if not self.backend.table_exists(self.cursor, table_name):
                        continue

                    cols = self.backend.get_column_names(self.cursor, table_name)
                    for geom_name in geom_candidates:
                        if geom_name in cols:
                            found_table = table_name
                            found_geom = geom_name
                            break

                    if found_table and found_geom:
                        break

                if not found_table or not found_geom:
                    QMessageBox.critical(
                        self,
                        "Fehler",
                        "Keine passende Tabellen-/Geometrievariante gefunden.",
                    )
                    return

                res = get_layer_source(self, found_table, found_geom, pk_name)
                if not res:
                    QMessageBox.critical(
                        self, "Fehler", "Verbindungsdaten unvollständig."
                    )
                    return

                uri, provider = res
                vlayer = QgsVectorLayer(uri, layer_name, provider)

                if vlayer.isValid():
                    plugin_dir = os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__))
                    )
                    qml_path = os.path.join(
                        plugin_dir, "templates", "qml", info["qml"]
                    )
                    if os.path.exists(qml_path):
                        vlayer.loadNamedStyle(qml_path)

                    QgsProject.instance().addMapLayer(vlayer)
                    # wichtig: eigene Methode erneut aufrufen, aber mit retry=True
                    zoom_to_selected_features(self, retry=True)
                    return
                else:
                    QMessageBox.critical(
                        self, "Fehler", f"Layer {layer_name} ungültig."
                    )
                    return
            return
        else:
            QMessageBox.critical(self, "Fehler", "Layer konnte nicht geladen werden.")
            return

    layer = layer_list[0]

    expr = f'"{column_name}" IN ({",".join(values)})'
    features = list(layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr)))

    if not features:
        QMessageBox.warning(
            self,
            "Info",
            "Keine Features im Layer gefunden (ggf. Filter aktiv?).",
        )
        return

    extent = features[0].geometry().boundingBox()
    for f in features[1:]:
        extent.combineExtentWith(f.geometry().boundingBox())

    layer.selectByIds([f.id() for f in features])
    iface.mapCanvas().zoomToFeatureExtent(extent)
    iface.mapCanvas().refresh()

def select_feature(self):
    """Selektiert Features im Layer (ohne Zoom)."""
    current_index = self.tab_Overview.currentIndex()
    info = get_layer_mapping(current_index)
    if not info:
        return

    if current_index == 0:
        table_view, model, proxy = self.tableView_Haltungen, self.model_haltungen, self.proxy_model_haltungen
    elif current_index == 1:
        table_view, model, proxy = self.tableView_Schaechte, self.model_schaechte, self.proxy_model_schaechte
    elif current_index == 2:
        table_view, model, proxy = self.tableView_GAL, self.model_anschlussleitungen, self.proxy_model_anschlussleitungen
    elif current_index == 3:
        table_view, model, proxy = self.tableView_Sinkkaesten, self.model_sinkkaesten, self.proxy_model_sinkkaesten
    elif current_index == 4:
        table_view, model, proxy = self.tableView_Rinnen, self.model_rinnen, self.proxy_model_rinnen
    elif current_index == 5:
        table_view, model, proxy = self.tableView_Sonderbauwerke, self.model_sonderbauwerke, self.proxy_model_sonderbauwerke
    else:
        return

    column_name = info['col']
    layer_name = info['layer']

    selected_rows = table_view.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.warning(self, "Info", "Keine Auswahl.")
        return

    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        QMessageBox.warning(self, "Fehler", f"Layer {layer_name} nicht geladen.")
        return
    layer = layers[0]
    iface.setActiveLayer(layer)

    if hasattr(model, "record"):
        col_idx = model.record().indexOf(column_name)
    else:
        col_idx = model.fieldIndex(column_name)

    if col_idx < 0:
        QMessageBox.warning(self, "Fehler", f"Spalte '{column_name}' nicht gefunden.")
        return

    values = []
    for row in selected_rows:
        idx = proxy.mapToSource(row)
        val = model.data(model.index(idx.row(), col_idx), Qt.DisplayRole)
        if val is not None:
            safe_val = str(val).replace("'", "''")
            values.append(f"'{safe_val}'")

    if not values:
        return

    expr = f'"{column_name}" IN ({",".join(values)})'
    layer.removeSelection()
    layer.selectByExpression(expr)


def layer_import_aktuell(self):
    """Importiert Layer für den aktuellen Tab (DB-Typ-Aware + Varianten)."""
    tab_index = self.tab_Overview.currentIndex()
    info = get_layer_mapping(tab_index)

    if not info:
        QMessageBox.warning(self, "Warnung", "Unbekannter Tab.")
        return

    layer_name = info["layer"]
    table_candidates = info.get("tables", [])
    geom_candidates = info.get("geoms", [])
    pk_name = info.get("pk", "pk")

    if not table_candidates or not geom_candidates:
        QMessageBox.critical(
            self,
            "Fehler",
            f"Für {layer_name} sind keine Tabellen-/Geometrievarianten definiert."
        )
        return

    found_table = None
    found_geom = None

    # 1. Tabellen- und Geometrievariante ermitteln
    for table_name in table_candidates:
        if not self.backend.table_exists(self.cursor, table_name):
            continue

        cols = self.backend.get_column_names(self.cursor, table_name)
        for geom_name in geom_candidates:
            if geom_name in cols:
                found_table = table_name
                found_geom = geom_name
                break

        if found_table and found_geom:
            break

    if not found_table or not found_geom:
        QMessageBox.critical(
            self,
            "Fehler",
            f"Keine passende Tabellen-/Geometrievariante gefunden für:\n"
            f"{layer_name}\n\n"
            f"Tabellen: {table_candidates}\n"
            f"Geometrien: {geom_candidates}"
        )
        return

    # 2. URI bauen und Layer laden
    res = get_layer_source(self, found_table, found_geom, pk_name)
    if not res:
        QMessageBox.critical(
            self,
            "Fehler",
            "DB-Verbindung unvollständig (siehe Settings)."
        )
        return

    uri_str, provider = res
    layer = QgsVectorLayer(uri_str, layer_name, provider)

    if not layer.isValid():
        err = layer.error().message() if layer.error().message() else "Unbekannter Fehler"
        QMessageBox.critical(
            self,
            "Fehler",
            f"Layer {layer_name} ungültig:\n"
            f"Tabelle: {found_table}\n"
            f"Geometrie: {found_geom}\n"
            f"{err}"
        )
        return

    if layer.featureCount() == 0:
        QMessageBox.warning(
            self,
            "Info",
            f"Layer {layer_name} ist leer.\n"
            f"Tabelle: {found_table}"
        )
        return

    # 3. QML-Stil aus Mapping laden
    plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qml_file = info.get("qml", "")
    qml_path = os.path.join(plugin_dir, "templates", "qml", qml_file)

    if qml_file and os.path.exists(qml_path):
        layer.loadNamedStyle(qml_path)
    elif qml_file:
        QMessageBox.warning(
            self,
            "QML nicht gefunden",
            f"Style-Datei nicht gefunden:\n{qml_path}"
        )

    # 4. Layer ins Projekt übernehmen
    QgsProject.instance().addMapLayer(layer)

    QMessageBox.information(
        self,
        "Erfolg",
        f"{layer_name} geladen ({layer.featureCount()} Features).\n"
        f"Tabelle: {found_table}\n"
        f"Geometrie: {found_geom}"
    )
# =============================================================================
# SCHACHTERZEUGUNG (Tools & Dialogs)
# =============================================================================

class SchachtPointTool(QgsMapToolEmitPoint):
    """MapTool zum Erfassen eines einzelnen Punkts per Klick."""
    pointCaptured = pyqtSignal('QgsPointXY', int)

    def __init__(self, canvas):
        super().__init__(canvas)
        self.setCursor(QCursor(Qt.CrossCursor))

    def canvasClicked(self, point, button):
        """Signal mit Klick‑Punkt emittieren."""
        self.pointCaptured.emit(point, button)
        
        # NEU: Koordinaten direkt in QLineEdits setzen (vor Tool-Deaktivierung)
        canvas = iface.mapCanvas()
        canvas.unsetMapTool(self)
        
        # Automatisch xsch und ysch füllen (wenn Dialog offen ist)
        dlg = SchachtDialog.get_open_dialog()  # Hilfsfunktion unten
        if dlg and hasattr(dlg, 'edits'):
            if 'xsch' in dlg.edits: dlg.edits['xsch'].setText(f"{point.x():.3f}")
            if 'ysch' in dlg.edits: dlg.edits['ysch'].setText(f"{point.y():.3f}")
            iface.messageBar().pushMessage("Koordinaten", f"X={point.x():.3f}, Y={point.y():.3f} gesetzt.", Qgis.Success)


class SchachtDialog(QDialog):
    _active_instance = None # Statische Referenz

    @staticmethod
    def get_open_dialog():
        return SchachtDialog._active_instance

    def __init__(self, parent, model_schaechte):
        super().__init__(parent)
        SchachtDialog._active_instance = self
        self.setWindowTitle("Schacht-Attribute eingeben")
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

        # GRÖßEN-FESTLEGUNG
        self.setMinimumSize(450, 350)
        self.resize(500, 400)
        
        self.model = model_schaechte
        self.edits = {}
        self.current_tool = None
        layout = QFormLayout(self)

        # Felder dynamisch aus Model holen
        record = self.model.record()
        for i in range(record.count()):
            field = record.field(i)
            name = field.name()
            
            # PK und generierte Spalten überspringen
            if name.lower() in ["pk", "id", "ogc_fid", "rowid"]:
                continue
                
            if name == "geop" or name == "geom":
                layout.addRow(name, QLabel("Geometrie wird automatisch gesetzt"))
                continue

            edit = QLineEdit(self)
            
            # NUMERISCHE FELDER
            if field.type() in (QVariant.Double, QVariant.Int, QVariant.LongLong):
                validator = QDoubleValidator(parent)
                validator.setLocale(QLocale(QLocale.English))  # Punkt statt Komma
                edit.setValidator(validator)
                edit.setPlaceholderText(f"z.B. {field.name()} = 0.5")
            
            self.edits[name] = edit
            layout.addRow(name, edit)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        
    def closeEvent(self, event):
        SchachtDialog._active_instance = None
        super().closeEvent(event)

    def reject(self):
        """Dialog schließen → Tool deaktivieren."""
        if hasattr(self, 'current_tool') and self.current_tool:
            iface.mapCanvas().unsetMapTool(self.current_tool)
        SchachtDialog._active_instance = None
        super().reject()


def erzeuge_schacht(parent, on_success_callback=None):
    """
    Schacht erstellen - Hybrid-Lösung.
    - PostgreSQL: Nutzt den bewährten QSqlTableModel Ansatz.
    - SpatiaLite: Prüft vor dem INSERT aktiv, ob ein Schreiblock erreichbar ist
      (BEGIN IMMEDIATE mit busy_timeout=0). Wenn die DB bereits gelockt ist,
      wird mit klarer Meldung abgebrochen. Nur bei freier DB wird der INSERT
      ausgeführt (Geometrie nur in 'geop').
    """
    from qgis.core import QgsProject, QgsGeometry, Qgis
    from PyQt6.QtWidgets import QMessageBox
    import sqlite3

    if not hasattr(parent, "model_schaechte"):
        iface.messageBar().pushMessage("Schächte", "Kein Model.", Qgis.Critical)
        return

    model = parent.model_schaechte

    # ========================================
    # METHODEN-AUSWAHL DIALOG
    # ========================================
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Schacht erstellen")
    msg.setText("Wie soll der Schacht erstellt werden?")

    btn_zeichnen = msg.addButton("🖊️ Punkt zeichnen", QMessageBox.AcceptRole)
    btn_koordinaten = msg.addButton("📍 X/Y-Koordinaten", QMessageBox.ActionRole)
    btn_linie = msg.addButton("📏 Position auf Haltung", QMessageBox.ActionRole)
    btn_kreise = msg.addButton("⭕ Schnittpunkt Hilfskreise", QMessageBox.ActionRole)
    btn_cancel = msg.addButton(QMessageBox.Cancel)

    msg.exec_()

    if msg.clickedButton() == btn_cancel:
        return

    # Methode bestimmen
    methode = ""
    if msg.clickedButton() == btn_zeichnen:
        methode = "zeichnen"
    elif msg.clickedButton() == btn_koordinaten:
        methode = "koordinaten"
    elif msg.clickedButton() == btn_linie:
        methode = "linie"
    elif msg.clickedButton() == btn_kreise:
        methode = "kreise"
    else:
        return

    # ========================================
    # HAUPTSCHLEIFE (Duplikat-Check)
    # ========================================
    while True:
        dlg = SchachtDialog(parent, model)
        result = dlg.exec_()

        if result == QDialog.Rejected:
            return

        # DUPLIKAT-CHECK
        schnam = dlg.edits["schnam"].text().strip()
        if schnam and any(
            model.data(model.index(i, model.record().indexOf("schnam"))) == schnam
            for i in range(model.rowCount())
        ):
            QMessageBox.warning(
                dlg,
                "⚠️ Duplikat!",
                f"Schnam '{schnam}' existiert bereits!\n→ Neuer Name:",
                QMessageBox.Ok,
            )
            continue

        # ========================================
        # KOORDINATEN ERMITTELN (je nach Methode)
        # ========================================
        point = None

        if methode == "zeichnen":
            point = methode_punkt_zeichnen(parent)
        elif methode == "koordinaten":
            point = methode_koordinaten_eingabe(parent)
        elif methode == "linie":
            point = methode_position_auf_linie(parent)
        elif methode == "kreise":
            point = methode_schnittpunkt_kreise(parent)

        if point is None:
            return  # User hat abgebrochen

        # Werte vorbereiten
        xsch_value = f"{point.x():.3f}"
        ysch_value = f"{point.y():.3f}"

        # Prüfen, welche Datenbank läuft
        is_spatialite = getattr(parent, "db_type", "") == "spatialite"

        # ============================================================
        # PFAD A: POSTGRESQL (QSqlTableModel)
        # ============================================================
        if not is_spatialite:
            row = model.rowCount()
            if not model.insertRow(row):
                iface.messageBar().pushMessage("Fehler", "insertRow fehlgeschlagen!", Qgis.Critical)
                return

            record = model.record()

            for name, edit in dlg.edits.items():
                idx = record.indexOf(name)
                value = edit.text().strip()
                if "," in value and "." not in value:
                    value = value.replace(",", ".")
                model.setData(model.index(row, idx), None if value == "" else value)

            idx_xsch = record.indexOf("xsch")
            idx_ysch = record.indexOf("ysch")
            if idx_xsch >= 0:
                model.setData(model.index(row, idx_xsch), xsch_value)
            if idx_ysch >= 0:
                model.setData(model.index(row, idx_ysch), ysch_value)

            idx_geom = record.indexOf("geop")
            geom = QgsGeometry.fromPointXY(point)
            wkt = geom.asWkt()
            if idx_geom >= 0:
                model.setData(model.index(row, idx_geom), wkt)

            if model.submitAll():
                try:
                    schaechte_layer = QgsProject.instance().mapLayersByName("Schächte")[0]
                    schaechte_layer.dataProvider().reloadData()
                    schaechte_layer.triggerRepaint()
                except Exception:
                    pass

                model.select()
                iface.messageBar().pushMessage("✅ Erfolg", "Schacht gespeichert!", Qgis.Success)

                if on_success_callback:
                    schacht_attrs = {
                        "schnam": dlg.edits.get("schnam", None).text().strip()
                        if "schnam" in dlg.edits
                        else "",
                        "sohlhoehe": dlg.edits.get("sohlhoehe", None).text().strip()
                        if "sohlhoehe" in dlg.edits
                        else None,
                        "xsch": xsch_value,
                        "ysch": ysch_value,
                    }
                    on_success_callback(schacht_attrs, point)

                break  # Erfolgreich gespeichert

            else:
                err = model.lastError().text()
                iface.messageBar().pushMessage("❌ Fehler", err, Qgis.Critical)
                model.revertAll()
                return

        # ============================================================
        # PFAD B: SPATIALITE – Lock-Probe + SQL-INSERT in 'schaechte'
        # ============================================================
        else:
            import sqlite3

            if not (hasattr(parent, "conn") and hasattr(parent, "cursor")):
                QMessageBox.critical(
                    parent,
                    "Fehler (SpatiaLite)",
                    "Keine native SpatiaLite-Verbindung (conn/cursor) vorhanden.",
                )
                return

            # 1) Lock-Probe: busy_timeout = 0 + BEGIN IMMEDIATE
            locked = False
            try:
                parent.cursor.execute("PRAGMA busy_timeout = 0")
                try:
                    parent.cursor.execute("BEGIN IMMEDIATE")
                    parent.cursor.execute("ROLLBACK")
                except sqlite3.OperationalError as e:
                    msg = str(e).lower()
                    if "database is locked" in msg or "database is busy" in msg:
                        locked = True
                        try:
                            parent.cursor.execute("ROLLBACK")
                        except Exception:
                            pass
                    else:
                        # anderer Fehler in der Probe
                        raise
            except Exception as e:
                # Unerwarteter Fehler in der Probe → lieber melden und abbrechen
                QMessageBox.critical(
                    parent,
                    "Fehler (SpatiaLite)",
                    f"Lock-Probe fehlgeschlagen:\n{e}",
                )
                return

            if locked:
                QMessageBox.warning(
                    parent,
                    "Datenbank gesperrt",
                    "Die SpatiaLite-Datenbank ist momentan für Schreibzugriffe gesperrt.\n\n"
                    "Mögliche Ursachen:\n"
                    "- andere QGIS-Layer oder Werkzeuge greifen gerade auf die DB zu\n"
                    "- ein paralleles Tool (DB-Viewer, externes Skript) hält einen Lock\n\n"
                    "Bitte schließen Sie andere Zugriffe oder versuchen Sie es später erneut.",
                )
                return

            # 2) Eigentlichen INSERT ausführen, database-is-locked hier noch einmal abfangen
            try:
                parent.cursor.execute("PRAGMA busy_timeout = 5000")

                cols = []
                vals = []
                params = []

                for name, edit in dlg.edits.items():
                    val = edit.text().strip().replace(",", ".")
                    if val == "":
                        val = None
                    if name.lower() in ["pk", "geom", "ogc_fid", "rowid", "geop"]:
                        continue

                    cols.append(name)
                    vals.append("?")
                    params.append(val)

                if "xsch" not in cols:
                    cols.append("xsch")
                    vals.append("?")
                    params.append(xsch_value)
                if "ysch" not in cols:
                    cols.append("ysch")
                    vals.append("?")
                    params.append(ysch_value)

                geom = QgsGeometry.fromPointXY(point)
                cols.append("geop")
                vals.append("GeomFromText(?, 25832)")
                params.append(geom.asWkt())

                query = f"INSERT INTO schaechte ({', '.join(cols)}) VALUES ({', '.join(vals)})"

                try:
                    parent.cursor.execute(query, params)
                    parent.conn.commit()
                except sqlite3.OperationalError as e:
                    msg = str(e).lower()
                    if "database is locked" in msg or "database is busy" in msg:
                        # Hier ganz gezielt Meldung für den Insert
                        QMessageBox.warning(
                            parent,
                            "Datenbank gesperrt (INSERT)",
                            "Beim Einfügen des Schachtes ist die SpatiaLite-Datenbank gesperrt.\n\n"
                            "Typischerweise halten andere QGIS-Werkzeuge oder Layer noch einen Lock.\n"
                            "Bitte schließen Sie andere Zugriffe (z.B. DB-Viewer, andere Dialoge) und\n"
                            "versuchen Sie es erneut.",
                        )
                        try:
                            parent.conn.rollback()
                        except Exception:
                            pass
                        return
                    else:
                        raise

                # Refresh Model + Layer
                model.select()
                layers = QgsProject.instance().mapLayersByName("Schächte")
                if layers:
                    l = layers[0]
                    l.dataProvider().forceReload()
                    l.triggerRepaint()
                    l.updateExtents()

                iface.messageBar().pushMessage(
                    "✅ Erfolg", "Schacht gespeichert (SpatiaLite)!", Qgis.Success
                )

                if on_success_callback:
                    schacht_attrs = {
                        "schnam": schnam,
                        "xsch": xsch_value,
                        "ysch": ysch_value,
                        "sohlhoehe": dlg.edits.get("sohlhoehe").text()
                        if "sohlhoehe" in dlg.edits
                        else None,
                    }
                    on_success_callback(schacht_attrs, point)

                break  # Success

            except Exception as e:
                try:
                    parent.conn.rollback()
                except Exception:
                    pass
                QMessageBox.critical(parent, "Fehler (SpatiaLite)", str(e))
                return

# --- Hilfsmethoden für Geometrie

def methode_punkt_zeichnen(parent):
    """Memory Layer + Zeichnen"""
    temp_layer = QgsVectorLayer("Point?crs=EPSG:25832", "Schacht-Punkt zeichnen", "memory")
    QgsProject.instance().addMapLayer(temp_layer)
    temp_layer.startEditing()
    
    iface.messageBar().pushMessage("Punkt zeichnen", "Punkt zeichnen → Übernehmen", Qgis.Info, 15)
    
    uebernehmen_btn = QPushButton("✅ Punkt übernehmen", parent)
    uebernehmen_btn.setMinimumWidth(150)
    uebernehmen_btn.move(50, 0)
    uebernehmen_btn.show()
    
    schliessen_btn = QPushButton("❌ Abbrechen", parent)
    schliessen_btn.setMinimumWidth(120)
    schliessen_btn.move(uebernehmen_btn.x() + uebernehmen_btn.width() + 10, 0)
    schliessen_btn.show()
    
    result_point = [None]  # Closure-Trick für Rückgabewert
    
    def uebernehmen():
        features = list(temp_layer.getFeatures())
        if len(features) != 1:
            iface.messageBar().pushMessage("Fehler", f"{len(features)} Punkte!", Qgis.Critical)
            return
        
        geom = features[0].geometry()
        if geom.isEmpty():
            iface.messageBar().pushMessage("Fehler", "Leere Geometrie!", Qgis.Critical)
            return
        
        result_point[0] = geom.asPoint()
        cleanup()
    
    def schliessen():
        cleanup()
    
    def cleanup():
        QgsProject.instance().removeMapLayer(temp_layer)
        uebernehmen_btn.hide()
        schliessen_btn.hide()
    
    uebernehmen_btn.clicked.connect(uebernehmen)
    schliessen_btn.clicked.connect(schliessen)
    
    # Event-Loop blockieren (synchron warten)
    from PyQt5.QtWidgets import QApplication
    while result_point[0] is None and temp_layer.isValid():
        QApplication.processEvents()
    
    return result_point[0]

def methode_koordinaten_eingabe(parent):
    """Dialog für manuelle X/Y-Eingabe"""
    from PyQt5.QtWidgets import QInputDialog, QLineEdit
    
    x_str, ok = QInputDialog.getText(parent, "X-Koordinate", "X-Koordinate (z.B. 123456.78):", QLineEdit.Normal, "")
    if not ok or not x_str.strip():
        return None
    
    y_str, ok = QInputDialog.getText(parent, "Y-Koordinate", "Y-Koordinate (z.B. 987654.32):", QLineEdit.Normal, "")
    if not ok or not y_str.strip():
        return None
    
    try:
        x = float(x_str.replace(',', '.'))
        y = float(y_str.replace(',', '.'))
        
        # Validierung (optional - EPSG:25832 Bereich prüfen)
        if not (280000 < x < 920000 and 5200000 < y < 6100000):
            QMessageBox.warning(parent, "Warnung", "Koordinaten außerhalb EPSG:25832 Bereich!")
        
        return QgsPointXY(x, y)
        
    except ValueError:
        QMessageBox.critical(parent, "Fehler", "Ungültige Koordinaten!")
        return None

def methode_position_auf_linie(parent):
    """Punkt auf Haltung mittels Stationierung (m entlang Linie)"""
    from PyQt5.QtWidgets import QInputDialog
    
    # 1. Haltung auswählen
    layers = QgsProject.instance().mapLayersByName("Haltungen")
    if not layers:
        iface.messageBar().pushMessage("Fehler", "Layer 'Haltungen' nicht gefunden!", Qgis.Critical)
        return None
    
    halt_layer = layers[0]
    
    # Tool zum Anklicken der Haltung
    canvas = iface.mapCanvas()
    tool = SelectHaltungTool(canvas, halt_layer)
    canvas.setMapTool(tool)
    iface.messageBar().pushMessage("Haltung wählen", "Bitte Haltung anklicken.", Qgis.Info, 10)
    
    selected_geom = [None]
    
    def on_haltung_picked(geom):
        selected_geom[0] = geom
        canvas.unsetMapTool(tool)
    
    tool.haltungSelected.connect(on_haltung_picked)
    
    # Event-Loop blockieren
    from PyQt5.QtWidgets import QApplication
    while selected_geom[0] is None:
        QApplication.processEvents()
    
    geom = selected_geom[0]
    total_length = geom.length()
    
    # 2. Stationierung abfragen
    dist_str, ok = QInputDialog.getText(
        parent, 
        "Stationierung", 
        f"Position in m entlang Haltung (0 - {total_length:.2f}):", 
        QLineEdit.Normal, 
        ""
    )
    if not ok or not dist_str.strip():
        return None
    
    try:
        distance = float(dist_str.replace(',', '.'))
        
        if distance < 0 or distance > total_length:
            QMessageBox.warning(parent, "Fehler", f"Abstand muss zwischen 0 und {total_length:.2f}m liegen!")
            return None
        
        # Punkt auf Linie interpolieren
        point_geom = geom.interpolate(distance)
        if point_geom.isEmpty():
            QMessageBox.critical(parent, "Fehler", "Punkt konnte nicht berechnet werden!")
            return None
        
        return point_geom.asPoint()
        
    except ValueError:
        QMessageBox.critical(parent, "Fehler", "Ungültige Distanz!")
        return None

def methode_schnittpunkt_kreise(parent):
    """Schnittpunkt mit visuellen Hilfskreisen, Labels UND unterschiedlichen Farben (Robust)"""
    canvas = iface.mapCanvas()
    
    # 1. Mittelpunkte Layer
    point_layer = QgsVectorLayer("Point?crs=EPSG:25832", "Mittelpunkte", "memory")
    QgsProject.instance().addMapLayer(point_layer)
    point_layer.startEditing()
    
    # 2. Hilfskreise Layer
    circle_layer = QgsVectorLayer("Polygon?crs=EPSG:25832", "Hilfskreise", "memory")
    QgsProject.instance().addMapLayer(circle_layer)
    circle_layer.startEditing()
    
    try:
        circle_symbol = QgsFillSymbol.createSimple({'color': '255,0,0,80', 'outline_color': '255,0,0', 'outline_width': '3'})
        circle_layer.setRenderer(QgsSingleSymbolRenderer(circle_symbol))
    except: pass
    circle_layer.triggerRepaint()
    
    # 3. Schnittpunkte Layer (mit Farbfeld!)
    schnitt_layer = QgsVectorLayer(
        "Point?crs=EPSG:25832&field=id:string(10)&field=color:string(20)", 
        "Schnittpunkte", 
        "memory"
    )
    QgsProject.instance().addMapLayer(schnitt_layer)
    schnitt_layer.startEditing()
    
    # Styling: Basis-Symbol erstellen
    marker_symbol = QgsMarkerSymbol.createSimple({'size': '10', 'outline_color': 'white', 'outline_width': '1'})
    
    # --- ROBUSTE DATA-DEFINED OVERRIDE (Fix) ---
    prop = QgsProperty.fromField("color")
    
    # Property muss auf dem SymbolLayer gesetzt werden (nicht auf dem Symbol direkt)
    sl = marker_symbol.symbolLayer(0)
    
    # Versuche moderne API, fallback auf alte API
    try:
        # QGIS 3.20+
        sl.setDataDefinedProperty(QgsSymbolLayer.Property.FillColor, prop)
    except AttributeError:
        try:
            # Ältere QGIS Versionen
            sl.setDataDefinedProperty(QgsSymbolLayer.PropertyFillColor, prop)
        except AttributeError:
            # Ganz alte API (nur zur Sicherheit)
            sl.setDataDefinedProperty(34, prop) # 34 ist oft PropertyFillColor

    schnitt_layer.setRenderer(QgsSingleSymbolRenderer(marker_symbol))
    
    iface.messageBar().pushMessage("Hilfskreise", "1. Mittelpunkt 1 klicken\n2. Mittelpunkt 2 klicken\n3. Radien eingeben", Qgis.Info, 20)
    
    uebernehmen_btn = QPushButton("✅ Kreise fertig", parent)
    uebernehmen_btn.setMinimumWidth(150)
    uebernehmen_btn.move(50, 0)
    uebernehmen_btn.show()
    
    schliessen_btn = QPushButton("❌ Abbrechen", parent)
    schliessen_btn.setMinimumWidth(120)
    schliessen_btn.move(uebernehmen_btn.x() + uebernehmen_btn.width() + 10, 0)
    schliessen_btn.show()
    
    result_point = [None]
    centers = []
    
    def on_canvas_clicked(point):
        centers.append(point)
        feat = QgsFeature(point_layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(point))
        point_layer.addFeature(feat)
        point_layer.triggerRepaint()
        
        if len(centers) == 1:
            iface.messageBar().pushMessage("Hilfskreise", "Mittelpunkt 1 OK → Mittelpunkt 2 klicken.", Qgis.Info, 10)
        elif len(centers) == 2:
            iface.messageBar().pushMessage("Hilfskreise", "Mittelpunkte OK → Radien eingeben.", Qgis.Success, 10)
    
    class ClickTool(QgsMapToolEmitPoint):
        def canvasReleaseEvent(self, event):
            point = self.toMapCoordinates(event.pos())
            on_canvas_clicked(point)
    
    tool = ClickTool(canvas)
    canvas.setMapTool(tool)
    
    def uebernehmen():
        if len(centers) != 2:
            iface.messageBar().pushMessage("Fehler", "Genau 2 Mittelpunkte benötigt!", Qgis.Critical)
            return
        
        r1_s, ok = QInputDialog.getText(
            parent, "Radius Kreis 1", 
            f"Radius Kreis 1 (Mittelpunkt {centers[0].x():.1f}, {centers[0].y():.1f}):\nRadius in m:"
        )
        if not ok: return
        
        r2_s, ok = QInputDialog.getText(
            parent, "Radius Kreis 2", 
            f"Radius Kreis 2 (Mittelpunkt {centers[1].x():.1f}, {centers[1].y():.1f}):\nRadius in m:"
        )
        if not ok: return
        
        try:
            r1 = float(r1_s.replace(',', '.'))
            r2 = float(r2_s.replace(',', '.'))
        except:
            QMessageBox.critical(parent, "Fehler", "Ungültige Radien!")
            return
        
        # Kreise zeichnen
        draw_circle_buffer(centers[0], r1, circle_layer)
        draw_circle_buffer(centers[1], r2, circle_layer)
        circle_layer.triggerRepaint()
        
        # Schnittpunkte
        intersections = calculate_circle_intersections(centers[0], r1, centers[1], r2)
        if not intersections:
            QMessageBox.warning(parent, "Keine Schnittpunkte", "Kreise schneiden sich nicht!")
            cleanup()
            return
        
        # **FEATURES ERSTELLEN (mit FARBEN)**
        colors = ["blue", "magenta"]  # Punkt 1 = Blau, Punkt 2 = Magenta
        
        for i, point in enumerate(intersections):
            feat = QgsFeature(schnitt_layer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(point))
            feat.setAttribute("id", str(i + 1))
            feat.setAttribute("color", colors[i] if i < len(colors) else "green") # Farbe setzen
            schnitt_layer.addFeature(feat)
        
        schnitt_layer.commitChanges()
        schnitt_layer.startEditing()
        
        # Labeling (Fallback)
        settings = QgsPalLayerSettings()
        settings.fieldName = '"id"'
        settings.enabled = True
        fmt = QgsTextFormat()
        fmt.setSize(14)
        fmt.setColor(QColor("white"))
        fmt.setFont(QFont("Arial", weight=QFont.Bold))
        buf = QgsTextBufferSettings()
        buf.setEnabled(True)
        buf.setColor(QColor("black"))
        fmt.setBuffer(buf)
        settings.setFormat(fmt)
        settings.placement = QgsPalLayerSettings.OrderedPositionsAroundPoint
        settings.predefinedPositionOrder = [QgsPalLayerSettings.TopMiddle]
        
        labeling = QgsVectorLayerSimpleLabeling(settings)
        schnitt_layer.setLabeling(labeling)
        schnitt_layer.setLabelsEnabled(True)
        schnitt_layer.triggerRepaint()
        iface.mapCanvas().refresh()
        
        # Auswahl Dialog
        if len(intersections) == 1:
            result_point[0] = intersections[0]
            QMessageBox.information(parent, "Auswahl", f"Punkt 1 (Blau) gewählt: ({intersections[0].x():.2f}, {intersections[0].y():.2f})")
        else:
            msg = QMessageBox(parent)
            msg.setWindowTitle("📍 Schnittpunkt wählen")
            msg.setText("Wähle basierend auf Farbe oder Nummer:")
            
            # Buttons mit Farbinformation
            btn1 = msg.addButton(f"🔵 Punkt 1 (Blau)\n({intersections[0].x():.2f}, {intersections[0].y():.2f})", QMessageBox.AcceptRole)
            btn2 = msg.addButton(f"🟣 Punkt 2 (Magenta)\n({intersections[1].x():.2f}, {intersections[1].y():.2f})", QMessageBox.ActionRole)
            
            msg.exec_()
            
            if msg.clickedButton() == btn1:
                result_point[0] = intersections[0]
            elif msg.clickedButton() == btn2:
                result_point[0] = intersections[1]
        
        cleanup()
    
    def cleanup():
        try:
            QgsProject.instance().removeMapLayer(point_layer)
            QgsProject.instance().removeMapLayer(circle_layer)
            QgsProject.instance().removeMapLayer(schnitt_layer)
        except: pass
        uebernehmen_btn.hide()
        schliessen_btn.hide()
        canvas.unsetMapTool(tool)
    
    uebernehmen_btn.clicked.connect(uebernehmen)
    schliessen_btn.clicked.connect(cleanup)
    
    from PyQt5.QtWidgets import QApplication
    while result_point[0] is None:
        QApplication.processEvents()
    
    return result_point[0]


def draw_circle_buffer(center, radius, layer):
    """Perfekter Kreis als Buffer"""
    point_geom = QgsGeometry.fromPointXY(center)
    circle_geom = point_geom.buffer(radius, 64)  # 64 Segmente
    feature = QgsFeature(layer.fields())
    feature.setGeometry(circle_geom)
    layer.addFeature(feature)

def calculate_circle_intersections(p1, r1, p2, r2):
    """
    Berechnet Schnittpunkte zweier Kreise.
    Returns: Liste von QgsPointXY (0, 1 oder 2 Punkte)
    """
    import math
    
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    d = math.sqrt(dx**2 + dy**2)
    
    # Keine Schnittpunkte
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return []
    
    # Ein Schnittpunkt (Kreise berühren sich)
    if abs(d - (r1 + r2)) < 1e-6 or abs(d - abs(r1 - r2)) < 1e-6:
        a = r1
        h = 0
    else:
        a = (r1**2 - r2**2 + d**2) / (2 * d)
        h = math.sqrt(r1**2 - a**2)
    
    # Mittelpunkt der Schnittpunkte
    px = p1.x() + a * dx / d
    py = p1.y() + a * dy / d
    
    if h == 0:
        return [QgsPointXY(px, py)]
    
    # Zwei Schnittpunkte
    return [
        QgsPointXY(px + h * dy / d, py - h * dx / d),
        QgsPointXY(px - h * dy / d, py + h * dx / d)
    ]

# =============================================================================
# HALTUNGSERZEUGUNG (Tools & Dialogs)
# =============================================================================

class HaltungsDialog(QDialog):
    def __init__(self, parent, model_haltungen):
        super().__init__(parent)
        self.setWindowTitle("Haltung anlegen")
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.resize(550, 700)  # Startgröße
        self.setMinimumSize(500, 600)  # Mindestgröße

        self.model = model_haltungen
        self.edits = {}
        self.current_tool = None

        # Haupt-Layout (Vertikal)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. HEADER-BEREICH (Buttons für Datenübernahme)
        btn_group = QFrame()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(15)
        
        self.btn_oben = QPushButton("🔍 Schacht OBEN")
        self.btn_oben.setMinimumHeight(20)
        self.btn_oben.clicked.connect(lambda: self.pick_schacht("oben"))
        btn_layout.addWidget(self.btn_oben)
        
        self.btn_unten = QPushButton("🔍 Schacht UNTEN")
        self.btn_unten.setMinimumHeight(20)
        self.btn_unten.clicked.connect(lambda: self.pick_schacht("unten"))
        btn_layout.addWidget(self.btn_unten)
        
        main_layout.addWidget(QLabel("<b>Datenübernahme aus Schacht-Layer:</b>"))
        main_layout.addWidget(btn_group)
        
        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 2. SCROLL AREA
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QFrame()
        form_layout = QFormLayout(scroll_content)
        form_layout.setContentsMargins(10, 10, 20, 10)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # 3. FELDER GENERIEREN
        record = self.model.record()
        for i in range(record.count()):
            field = record.field(i)
            name = field.name()
            
            # PK und interne Spalten überspringen
            if name.lower() in ["pk", "ogc_fid", "rowid", "id"]: continue
            if name == "geom":
                lbl = QLabel("<i>Linie wird im nächsten Schritt gezeichnet</i>")
                lbl.setStyleSheet("color: gray;")
                form_layout.addRow("Geometrie:", lbl)
                continue

            # Eingabefeld
            edit = QLineEdit()
            edit.setMinimumHeight(20)
            
            # Numerische Felder erkennen
            if field.type() in (QVariant.Double, QVariant.Int, QVariant.LongLong):
                validator = QDoubleValidator(scroll_content)
                validator.setLocale(QLocale(QLocale.English))
                edit.setValidator(validator)
                edit.setPlaceholderText(f"z.B. 0.5")
            
            self.edits[name] = edit
            
            label_text = f"{name}:"
            form_layout.addRow(label_text, edit)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # 4. DIALOG BUTTONS
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        main_layout.addWidget(self.buttonBox)

    # --- Methoden ---
    def pick_schacht(self, modus):
        """Startet das Tool und minimiert das Fenster."""
        layer = QgsProject.instance().mapLayersByName("Schächte")
        if not layer:
            iface.messageBar().pushMessage("Fehler", "Layer 'Schächte' nicht gefunden!", Qgis.Critical)
            return

        canvas = iface.mapCanvas()
        self.current_tool = SelectSchachtTool(canvas)
        self.current_tool.schachtSelected.connect(lambda data: self.fill_schacht_data(data, modus))
        
        canvas.setMapTool(self.current_tool)
        iface.messageBar().pushMessage("Auswahl", f"Bitte auf Schacht {modus.upper()} klicken...", Qgis.Info)
        
        # FENSTER MINIMIEREN (Damit man die Karte sieht)
        self.showMinimized()

    def fill_schacht_data(self, data, modus):
        """Füllt Daten und stellt Fenster wieder her."""
        try:
            # SICHERE QVariant-Konvertierung
            def safe_float(qvar):
                if qvar is None or qvar == "":
                    return "0.00"
                try:
                    # QVariant → Python float → String
                    if hasattr(qvar, 'toFloat'):
                        return f"{qvar.toFloat()[0]:.2f}"
                    elif hasattr(qvar, 'toDouble'):
                        return f"{qvar.toDouble()[0]:.2f}"
                    else:
                        return f"{float(qvar):.2f}"
                except:
                    return "0.00"

            def safe_str(qvar):
                if qvar is None:
                    return ""
                try:
                    return str(qvar)
                except:
                    return ""

            # Daten extrahieren
            schnam = safe_str(data.get("schnam"))
            sohle = safe_float(data.get("sohlhoehe"))
            xsch = safe_float(data.get("xsch"))
            ysch = safe_float(data.get("ysch"))
            
            if modus == "oben":
                if "schoben" in self.edits: self.edits["schoben"].setText(schnam)
                if "sohleoben" in self.edits: self.edits["sohleoben"].setText(sohle)
                if "yschob" in self.edits: self.edits["yschob"].setText(ysch)
                if "xschob" in self.edits: self.edits["xschob"].setText(xsch)
                iface.messageBar().pushMessage("Erfolg", f"Schacht OBEN ({schnam}) übernommen.", Qgis.Success)
                
            elif modus == "unten":
                if "schunten" in self.edits: self.edits["schunten"].setText(schnam)
                if "sohleunten" in self.edits: self.edits["sohleunten"].setText(sohle)
                if "yschun" in self.edits: self.edits["yschun"].setText(ysch)  # Oder yschunten?
                if "xschun" in self.edits: self.edits["xschun"].setText(xsch)
                iface.messageBar().pushMessage("Erfolg", f"Schacht UNTEN ({schnam}) übernommen.", Qgis.Success)
            
            self.showNormal()
            self.activateWindow()
            self.raise_()
            
        except Exception as e:
            iface.messageBar().pushMessage("Fehler", f"Fehler beim Füllen: {e}", Qgis.Critical)
            self.showNormal()

    def reject(self):
        """Abbrechen und Tool aufräumen."""
        if self.current_tool:
            iface.mapCanvas().unsetMapTool(self.current_tool)
            self.current_tool = None
            if self.isMinimized():
                self.showNormal()
                return 
        super().reject()

def erzeuge_haltung(parent):
    """Haltungen – Duplikat-Check und Zeichnen (DB-Typ sicher)."""
    if not hasattr(parent, "model_haltungen"):
        iface.messageBar().pushMessage("Haltungen", "Kein Model.", Qgis.Critical)
        return

    model = parent.model_haltungen
    dlg = HaltungsDialog(parent, model)
    
    # 1. OK-Button vom automatischen Schließen TRENNEN
    btn_ok = dlg.buttonBox.button(QDialogButtonBox.Ok)
    try:
        dlg.buttonBox.accepted.disconnect() 
    except: pass
    
    btn_ok.clicked.connect(lambda: on_ok_clicked())
    dlg.buttonBox.rejected.connect(dlg.close)

    # 2. ZEIGEN (Modeless für Minimieren!)
    dlg.show()

    def on_ok_clicked():
        # **DUPLIKAT-CHECK** (Dialog ist OFFEN)
        # Für große DBs ist SQL-Query besser als model iteration, aber für hier ok
        haltnam = dlg.edits["haltnam"].text().strip()
        if haltnam:
            match = model.match(model.index(0, model.fieldIndex("haltnam")), Qt.DisplayRole, haltnam, 1, Qt.MatchExactly)
            if match:
                QMessageBox.warning(dlg, "⚠️ Duplikat!", f"Haltnam '{haltnam}' existiert bereits!\\n→ Neuer Name:", QMessageBox.Ok)
                dlg.edits["haltnam"].setFocus()
                dlg.edits["haltnam"].selectAll()
                return 
        
        # **Kein Duplikat → Erst jetzt schließen & weitermachen**
        dlg.hide() 
        start_memory_layer_logic()

    def start_memory_layer_logic():        # Snapping aktivieren für das Zeichnen
        from qgis.core import QgsSnappingConfig, QgsTolerance
        
        # Aktuelle Config holen
        snapping_config = QgsProject.instance().snappingConfig()
        
        # Falls aus, einschalten
        if not snapping_config.enabled():
            snapping_config.setEnabled(True)
            snapping_config.setMode(QgsSnappingConfig.AllLayers) # Auf alle Layer fangen
            snapping_config.setTolerance(10)
            snapping_config.setUnits(QgsTolerance.Pixels)
            QgsProject.instance().setSnappingConfig(snapping_config)

        # 3. LINIEN Memory Layer
        temp_layer = QgsVectorLayer("LineString?crs=EPSG:25832", "Haltung-Linie zeichnen", "memory")
        QgsProject.instance().addMapLayer(temp_layer)
        temp_layer.startEditing()
        
        iface.messageBar().pushMessage("Haltung zeichnen", "1. Linie zeichnen...", Qgis.Info, 15)

        # Buttons erstellen
        uebernehmen_btn = QPushButton("✅ Linie übernehmen", parent)
        uebernehmen_btn.setMinimumWidth(150)
        uebernehmen_btn.adjustSize()
        uebernehmen_btn.move(50, 0)
        uebernehmen_btn.show()

        schliessen_btn = QPushButton("❌ Abbrechen", parent)
        schliessen_btn.setMinimumWidth(120)
        schliessen_btn.adjustSize()
        schliessen_btn.move(uebernehmen_btn.x() + uebernehmen_btn.width() + 10, 0)
        schliessen_btn.show()

        def uebernehmen():
            features = list(temp_layer.getFeatures())
            if len(features) != 1:
                iface.messageBar().pushMessage("Fehler", f"{len(features)} Linien!", Qgis.Critical)
                return
            
            geom = features[0].geometry()
            if geom.isEmpty(): return
            
            # Länge
            laenge = geom.length()
            laenge_str = f"{laenge:.2f}"
            
            # Frage
            msg_box = QMessageBox(parent)
            msg_box.setText(f"Länge: {laenge_str} m")
            msg_box.setInformativeText("Übernehmen?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            laenge_uebernehmen = msg_box.exec_() == QMessageBox.Yes

            # --- DB-TYP SICHERES INSERT ---
            data_map = {}
            for name, edit in dlg.edits.items():
                val = edit.text().strip().replace(',', '.')
                data_map[name] = val if val else None

            if laenge_uebernehmen:
                data_map["laenge"] = laenge_str

            # Speichern über Backend (INSERT statt QSqlTableModel)
            try:
                backend = parent.backend
                is_spatialite = (parent.db_type == "spatialite")
                
                # SQL Query bauen
                cols_sql = []
                vals_sql = []
                params = []
                
                for col, val in data_map.items():
                    cols_sql.append(f'"{col}"' if not is_spatialite else col)
                    vals_sql.append('%s' if not is_spatialite else '?')
                    params.append(val)
                
                # Geometrie
                geom_col = "geom"
                cols_sql.append(f'"{geom_col}"' if not is_spatialite else geom_col)
                wkt = geom.asWkt()
                if is_spatialite:
                    vals_sql.append("GeomFromText(?, 25832)")
                else:
                    vals_sql.append("ST_GeomFromText(%s, 25832)")
                params.append(wkt)
                
                table_name = '"haltungen"' if not is_spatialite else 'haltungen'
                query = f"INSERT INTO {table_name} ({', '.join(cols_sql)}) VALUES ({', '.join(vals_sql)})"
                
                parent.cursor.execute(query, params)
                parent.conn.commit()
                
                # Refresh
                model.select()
                try:
                    l = QgsProject.instance().mapLayersByName("Haltungen")[0]
                    l.triggerRepaint()
                except: pass
                
                iface.messageBar().pushMessage("✅ Erfolg", "Haltung gespeichert!", Qgis.Success)
                
                uebernehmen_btn.hide()
                schliessen_btn.hide()
                QgsProject.instance().removeMapLayer(temp_layer)
                dlg.close()

            except Exception as e:
                parent.conn.rollback()
                iface.messageBar().pushMessage("❌ Fehler", str(e), Qgis.Critical)

        def schliessen():
            QgsProject.instance().removeMapLayer(temp_layer)
            uebernehmen_btn.hide()
            schliessen_btn.hide()
            dlg.close()

        uebernehmen_btn.clicked.connect(uebernehmen)
        schliessen_btn.clicked.connect(schliessen)


def get_selected_haltung():
    """Hilfsfunktion: Selektierte Haltung holen."""
    layers = QgsProject.instance().mapLayersByName("Haltungen")
    if not layers:
        iface.messageBar().pushMessage("Fehler", "Layer 'Haltungen' nicht gefunden!", Qgis.Critical)
        return None, None

    layer = layers[0]
    selected = layer.selectedFeatures()
    if len(selected) != 1:
        iface.messageBar().pushMessage("Fehler", "Bitte genau eine Haltung selektieren.", Qgis.Warning)
        return None, None

    return layer, selected[0]

def split_line_at_point(line_geom: QgsGeometry, pt: QgsPointXY):
    """
    Teilt Linie an Punkt.
    """
    if line_geom.isMultipart() or line_geom.isEmpty():
        return []
    
    if line_geom.type() != QgsWkbTypes.LineGeometry:
        return []

    # Distanz entlang Linie
    pt_geom = QgsGeometry.fromPointXY(pt)
    dist_along_line = line_geom.lineLocatePoint(pt_geom)
    total_length = line_geom.length()
    
    EPSILON = 0.01
    if dist_along_line < EPSILON or dist_along_line > (total_length - EPSILON):
        return []

    # Punkte holen (QgsPointXY)
    points_xy = line_geom.asPolyline()
    if len(points_xy) < 2:
        return []

    # Konvertierung für QGIS < 3.x Kompatibilität (QgsPoint vs QgsPointXY)
    points = [QgsPoint(p.x(), p.y()) for p in points_xy]
    pt_point = QgsPoint(pt.x(), pt.y())
    
    # Split-Index finden
    split_idx = max(0, min(int(dist_along_line / total_length * (len(points) - 1)), len(points) - 2))
    
    # Zwei Teillinien
    new_points_1 = points[:split_idx + 1] + [pt_point]
    new_points_2 = [pt_point] + points[split_idx + 1:]
    
    part1 = QgsGeometry.fromPolyline(new_points_1)
    part2 = QgsGeometry.fromPolyline(new_points_2)
    
    if part1.isEmpty() or part2.isEmpty():
        return []
    
    return [part1, part2]


def perform_haltung_split(parent, halt_layer, h_feature, geom, schacht_attrs, schacht_point):
    """
    Führt den eigentlichen Split durch. 
    Arbeitet auf dem QGIS Vector Layer, daher DB-Typ unabhängig (QGIS abstrahiert das).
    """
    print("✅ DEBUG: Start Split-Logik")
    
    try:
        # 1. Geometrie teilen
        parts = split_line_at_point(geom, schacht_point)
        if len(parts) != 2:
            iface.messageBar().pushMessage("Fehler", f"Split fehlgeschlagen: {len(parts)} Teile", Qgis.Critical)
            return

        fields = halt_layer.fields()
        attrs_orig = h_feature.attributes()
        
        idx_haltnam = fields.indexOf("haltnam")
        haltnam_alt = attrs_orig[idx_haltnam] if idx_haltnam >= 0 else "Unnamed"

        # Daten von Schacht C
        c_name  = str(schacht_attrs.get("schnam", "") or "")
        # Werte sicher in String wandeln oder None
        c_sohle = schacht_attrs.get("sohlhoehe")
        c_x     = schacht_attrs.get("xsch")
        c_y     = schacht_attrs.get("ysch")

        # Abfrage: Alte Haltung behalten?
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Alte Haltung?")
        msg.setText(f"'{haltnam_alt}' behalten?")
        msg.setInformativeText("Ja = behalten, Nein = löschen, Cancel = abbrechen")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        behalten = msg.exec_()
        
        if behalten == QMessageBox.Cancel:
            if hasattr(parent, 'split_tool') and parent.split_tool:
                iface.mapCanvas().unsetMapTool(parent.split_tool)
            return

        # Abfrage: Neue Namen?
        haltnam_ac = None
        haltnam_cb = None
        
        msg_names = QMessageBox(parent)
        msg_names.setIcon(QMessageBox.Question)
        msg_names.setWindowTitle("Neue Namen?")
        msg_names.setText("Neue Namen für die beiden neuen Haltungen vergeben?")
        msg_names.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        want_new_names = msg_names.exec_() == QMessageBox.Yes
        
        if want_new_names and idx_haltnam >= 0:
            from PyQt5.QtWidgets import QInputDialog
            default_ac = f"{haltnam_alt}_1" if haltnam_alt != "Unnamed" else ""
            default_cb = f"{haltnam_alt}_2" if haltnam_alt != "Unnamed" else ""
            
            text_ac, ok_ac = QInputDialog.getText(parent, "Haltnam A→C", "Neuer Name A→C:", text=default_ac)
            if not ok_ac: return
            haltnam_ac = text_ac.strip()
            
            text_cb, ok_cb = QInputDialog.getText(parent, "Haltnam C→B", "Neuer Name C→B:", text=default_cb)
            if not ok_cb: return
            haltnam_cb = text_cb.strip()

        halt_layer.startEditing()
        if behalten == QMessageBox.No:
            halt_layer.deleteFeature(h_feature.id())

        # Indizes
        idx_pk = fields.indexOf("pk") # PK wird beim Insert neu vergeben
        idx_laenge = fields.indexOf("laenge")
        idx_schoben, idx_schunten = fields.indexOf("schoben"), fields.indexOf("schunten")
        idx_sohleoben, idx_sohleunten = fields.indexOf("sohleoben"), fields.indexOf("sohleunten")
        idx_xschob, idx_xschun = fields.indexOf("xschob"), fields.indexOf("xschun")
        idx_yschob, idx_yschun = fields.indexOf("yschob"), fields.indexOf("yschun")

        # Helper zum Setzen von Attributen
        def set_val(feat, idx, val):
            if idx >= 0: feat.setAttribute(idx, val)

        # --- Haltung 1: A -> C ---
        f_AC = QgsFeature(fields)
        f_AC.setAttributes(list(attrs_orig)) # Kopie der Attribute
        f_AC.setGeometry(parts[0])
        
        set_val(f_AC, idx_pk, NULL) # Neuen PK erzwingen
        
        # UNTEN überschreiben mit Schacht C Daten
        set_val(f_AC, idx_schunten, c_name)
        set_val(f_AC, idx_sohleunten, c_sohle)
        set_val(f_AC, idx_xschun, c_x)
        set_val(f_AC, idx_yschun, c_y)
        
        set_val(f_AC, idx_laenge, f"{parts[0].length():.2f}")
        if haltnam_ac: set_val(f_AC, idx_haltnam, haltnam_ac)

        if not halt_layer.addFeature(f_AC): raise Exception("Fehler addFeature A-C")

        # --- Haltung 2: C -> B ---
        f_CB = QgsFeature(fields)
        f_CB.setAttributes(list(attrs_orig))
        f_CB.setGeometry(parts[1])
        
        set_val(f_CB, idx_pk, NULL)
        
        # OBEN überschreiben mit Schacht C Daten
        set_val(f_CB, idx_schoben, c_name)
        set_val(f_CB, idx_sohleoben, c_sohle)
        set_val(f_CB, idx_xschob, c_x)
        set_val(f_CB, idx_yschob, c_y)

        set_val(f_CB, idx_laenge, f"{parts[1].length():.2f}")
        if haltnam_cb: set_val(f_CB, idx_haltnam, haltnam_cb)

        if not halt_layer.addFeature(f_CB): raise Exception("Fehler addFeature C-B")

        # Speichern
        if halt_layer.commitChanges():
            iface.messageBar().pushMessage("✅ Erfolg", f"Haltung an {c_name} geteilt!", Qgis.Success)
        else:
            err = halt_layer.commitErrors()
            halt_layer.rollBack()
            iface.messageBar().pushMessage("Fehler", f"Datenbank-Fehler: {err}", Qgis.Critical)

        if hasattr(parent, "model_haltungen"): parent.model_haltungen.select()
        halt_layer.triggerRepaint()
        
        # Tool aufräumen
        if hasattr(parent, 'split_tool') and parent.split_tool:
            iface.mapCanvas().unsetMapTool(parent.split_tool)

    except Exception as e:
        print(f"❌ {e}")
        QMessageBox.critical(parent, "Split Exception", str(e))
        if halt_layer.isEditable(): halt_layer.rollBack()

def teile_haltung(parent):
    halt_layer, h_feature = get_selected_haltung()
    if not halt_layer or not h_feature:
        return

    geom = h_feature.geometry()
    if geom.isEmpty():
        iface.messageBar().pushMessage("Fehler", "Keine Geometrie.", Qgis.Critical)
        return

    canvas = iface.mapCanvas()

    # ABFRAGE: Bestehender oder neuer Schacht?
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Haltung teilen")
    msg.setText("Schacht auswählen oder neu erstellen?")
    btn_bestehend = msg.addButton("Bestehender Schacht", QMessageBox.AcceptRole)
    btn_neu = msg.addButton("Neuer Schacht", QMessageBox.ActionRole)
    btn_cancel = msg.addButton(QMessageBox.Cancel)
    msg.exec_()
    
    if msg.clickedButton() == btn_cancel:
        return

    if msg.clickedButton() == btn_bestehend:
        # Fall 1: Bestehender Schacht
        parent.split_tool = SelectSchachtTool(canvas)
        canvas.setMapTool(parent.split_tool)
        iface.messageBar().pushMessage("Haltung teilen", "Bestehenden Schacht anklicken.", Qgis.Info, 10)
        
        parent.split_tool.schachtSelectedWithPoint.connect(
            lambda attrs, pt: perform_haltung_split(parent, halt_layer, h_feature, geom, attrs, pt)
        )
        
    elif msg.clickedButton() == btn_neu:
        # Fall 2: Neuer Schacht - mit Callback
        def on_schacht_created(schacht_attrs, schacht_point):
            print(f"✅ Callback empfangen: {schacht_attrs.get('schnam')}")
            # Kurze Verzögerung, damit Schacht-Dialog sauber schließt
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(200, lambda: perform_haltung_split(parent, halt_layer, h_feature, geom, schacht_attrs, schacht_point))
        
        # erzeuge_schacht mit Callback aufrufen
        erzeuge_schacht(parent, on_success_callback=on_schacht_created)

class SelectSchachtTool(QgsMapToolIdentify):
    """Klickt auf einen Schacht und sendet dessen Attribute zurück."""
    schachtSelected = pyqtSignal(dict)          # für Datenübernahme
    schachtSelectedWithPoint = pyqtSignal(dict, QgsPointXY)  # für Split

    def __init__(self, canvas):
        super().__init__(canvas)
        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        layer = self.get_schacht_layer()
        if not layer:
            iface.messageBar().pushMessage("Fehler", "Layer 'Schächte' nicht gefunden!", Qgis.Critical)
            return

        found_features = self.identify(
            event.x(), event.y(), [layer],
            QgsMapToolIdentify.TopDownStopAtFirst
        )
        
        if not found_features:
            iface.messageBar().pushMessage("Info", "Kein Schacht gefunden.", Qgis.Warning)
            return

        feature = found_features[0].mFeature
        geom = feature.geometry()
        if geom.isEmpty() or geom.type() != QgsWkbTypes.PointGeometry:
            iface.messageBar().pushMessage("Fehler", "Getroffenes Objekt ist kein Punkt.", Qgis.Critical)
            return

        pt = QgsPointXY(geom.asPoint())
        attrs = {
            "schnam": feature["schnam"],       
            "sohlhoehe": feature["sohlhoehe"],
            "xsch": feature["xsch"],           
            "ysch": feature["ysch"]            
        }
        
        self.schachtSelected.emit(attrs)
        self.schachtSelectedWithPoint.emit(attrs, pt)

        iface.mapCanvas().unsetMapTool(self)
        iface.mapCanvas().setCursor(Qt.ArrowCursor)

    def get_schacht_layer(self):
        layers = QgsProject.instance().mapLayersByName("Schächte")
        return layers[0] if layers else None

class SelectHaltungTool(QgsMapToolIdentify):
    """Klick auf Haltung -> liefert Geometrie"""
    haltungSelected = pyqtSignal(QgsGeometry)
    
    def __init__(self, canvas, layer):
        super().__init__(canvas)
        self.layer = layer
        self.setCursor(Qt.CrossCursor)
    
    def canvasReleaseEvent(self, event):
        results = self.identify(event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownStopAtFirst)
        if not results:
            iface.messageBar().pushMessage("Info", "Keine Haltung getroffen.", Qgis.Warning)
            return
        
        f = results[0].mFeature
        geom = f.geometry()
        if geom.isEmpty() or geom.type() != QgsWkbTypes.LineGeometry:
            iface.messageBar().pushMessage("Fehler", "Objekt ist keine Linie.", Qgis.Critical)
            return
        
        self.haltungSelected.emit(geom)

# =============================================================================
# SINKKASTENERZEUGUNG (Tools & Dialogs)
# =============================================================================
class SinkkastenDialog(QDialog):
    _active_instance = None  # Statische Referenz

    @staticmethod
    def get_open_dialog():
        return SinkkastenDialog._active_instance

    def __init__(self, parent, model_sinkkaesten):
        super().__init__(parent)
        SinkkastenDialog._active_instance = self
        self.setWindowTitle("Sinkkasten-Attribute eingeben")
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

        # Größen-Festlegung
        self.setMinimumSize(450, 350)
        self.resize(500, 400)

        self.model = model_sinkkaesten
        self.edits = {}
        self.current_tool = None
        layout = QFormLayout(self)

        # Felder dynamisch aus Model holen
        record = self.model.record()
        for i in range(record.count()):
            field = record.field(i)
            name = field.name()

            # PK und generierte Spalten überspringen
            if name.lower() in ["pk", "id", "ogc_fid", "rowid"]:
                continue

            # Geometrie-Spalten nur Info-Label
            if name in ("geop", "geom"):
                layout.addRow(name, QLabel("Geometrie wird automatisch gesetzt"))
                continue

            edit = QLineEdit(self)

            # Numerische Felder
            if field.type() in (QVariant.Double, QVariant.Int, QVariant.LongLong):
                validator = QDoubleValidator(parent)
                validator.setLocale(QLocale(QLocale.English))  # Punkt statt Komma
                edit.setValidator(validator)
                edit.setPlaceholderText(f"z.B. {field.name()} = 0.5")

            self.edits[name] = edit
            layout.addRow(name, edit)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)
        layout.setSizeConstraint(QLayout.SetMinimumSize)

    def closeEvent(self, event):
        SinkkastenDialog._active_instance = None
        super().closeEvent(event)

    def reject(self):
        """Dialog schließen → Tool deaktivieren."""
        if hasattr(self, 'current_tool') and self.current_tool:
            iface.mapCanvas().unsetMapTool(self.current_tool)
        SinkkastenDialog._active_instance = None
        super().reject()

def erzeuge_sinkkasten(parent):
    if not hasattr(parent, "model_sinkkaesten"):
        iface.messageBar().pushMessage("Sinkkästen", "Kein Model.", Qgis.Critical)
        return

    model = parent.model_sinkkaesten

    # ==========================
    # Methoden-Auswahl
    # ==========================
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Sinkkasten erstellen")
    msg.setText("Wie soll der Sinkkasten erstellt werden?")

    btn_zeichnen    = msg.addButton("🖊️ Punkt zeichnen", QMessageBox.AcceptRole)
    btn_koordinaten = msg.addButton("📍 X/Y-Koordinaten", QMessageBox.ActionRole)
    btn_cancel      = msg.addButton(QMessageBox.Cancel)

    msg.exec_()
    if msg.clickedButton() == btn_cancel:
        return

    methode = ""
    if msg.clickedButton() == btn_zeichnen:
        methode = "zeichnen"
    elif msg.clickedButton() == btn_koordinaten:
        methode = "koordinaten"
    else:
        return

    # ==========================
    # Eingabedialog für Attribute
    # (du kannst hier auch einen eigenen Dialog wie SchachtDialog nutzen)
    # ==========================

    dlg = SinkkastenDialog(parent, model)            # oder ein simples QDialog
    if dlg.exec_() == dlg.Rejected:
        return

    # Duplikat-Check auf Name (an Feldnamen anpassen)
    name_field = "Name"
    sk_name = dlg.edits[name_field].text().strip()
    if sk_name and any(
        model.data(model.index(i, model.record().indexOf(name_field))) == sk_name
        for i in range(model.rowCount())
    ):
        QMessageBox.warning(dlg, "⚠️ Duplikat!", f"Name '{sk_name}' existiert bereits!")
        return

    # ==========================
    # Punkt bestimmen
    # ==========================
    if methode == "zeichnen":
        point = methode_punkt_zeichnen(parent)
    else:
        point = methode_koordinaten_eingabe(parent)

    if point is None:
        return

    x_value = f"{point.x():.3f}"
    y_value = f"{point.y():.3f}"

    is_spatialite = getattr(parent, 'db_type', '') == 'spatialite'

    if not is_spatialite:
        # =====================================
        # PostgreSQL über QSqlTableModel
        # =====================================
        row = model.rowCount()
        if not model.insertRow(row):
            iface.messageBar().pushMessage("Fehler", "insertRow fehlgeschlagen!", Qgis.Critical)
            return

        record = model.record()

        # Attribute aus Dialog übernehmen
        for name, edit in dlg.edits.items():
            idx = record.indexOf(name)
            if idx < 0:
                continue
            value = edit.text().strip()
            if ',' in value and '.' not in value:
                value = value.replace(',', '.')
            model.setData(model.index(row, idx), None if value == "" else value)

        # Koordinatenfelder (anpassen)
        idx_x = record.indexOf("xsk")
        idx_y = record.indexOf("ysk")
        if idx_x >= 0:
            model.setData(model.index(row, idx_x), x_value)
        if idx_y >= 0:
            model.setData(model.index(row, idx_y), y_value)

        # Geometrie
        idx_geom = record.indexOf("geom")
        if idx_geom >= 0:
            geom = QgsGeometry.fromPointXY(point)
            model.setData(model.index(row, idx_geom), geom.asWkt())

        if model.submitAll():
            try:
                layer = QgsProject.instance().mapLayersByName("Sinkkästen")[0]
                layer.dataProvider().reloadData()
                layer.triggerRepaint()
            except Exception:
                pass

            model.select()
            iface.messageBar().pushMessage("✅ Erfolg", "Sinkkasten gespeichert!", Qgis.Success)
        else:
            err = model.lastError().text()
            iface.messageBar().pushMessage("❌ Fehler", err, Qgis.Critical)
            model.revertAll()
            return

    else:
        # =====================================
        # SpatiaLite per SQL INSERT
        # =====================================
        try:
            cols = []
            vals = []
            params = []

            for name, edit in dlg.edits.items():
                val = edit.text().strip().replace(',', '.')
                if val == "":
                    val = None
                if name.lower() in ['pk', 'geom', 'ogc_fid', 'rowid']:
                    continue
                cols.append(name)
                vals.append('?')
                params.append(val)

            if 'xsk' not in cols:
                cols.append('xsk')
                vals.append('?')
                params.append(x_value)
            if 'ysk' not in cols:
                cols.append('ysk')
                vals.append('?')
                params.append(y_value)

            cols.append("geop")
            vals.append("GeomFromText(?, 25832)")
            params.append(QgsGeometry.fromPointXY(point).asWkt())

            query = f"INSERT INTO sinkkaesten ({', '.join(cols)}) VALUES ({', '.join(vals)})"
            parent.cursor.execute(query, params)
            parent.conn.commit()

            model.select()
            layers = QgsProject.instance().mapLayersByName("Sinkkästen")
            if layers:
                l = layers[0]
                l.dataProvider().forceReload()
                l.triggerRepaint()
                l.updateExtents()
                iface.mapCanvas().refresh()

            iface.messageBar().pushMessage("✅ Erfolg", "Sinkkasten gespeichert (SpatiaLite)!", Qgis.Success)
        except Exception as e:
            parent.conn.rollback()
            QMessageBox.critical(parent, "Fehler (SpatiaLite)", str(e))
            return

class SchachtDialogDirect(QDialog):
    """
    Minimaler Dialog für Schacht-Attribute ohne QSqlTableModel.
    Felder sind fest auf die wichtigsten Spalten der Tabelle 'schaechte' ausgelegt.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Schacht-Attribute eingeben (direkt)")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.edits = {}
        layout = QFormLayout(self)

        # Liste der Felder, die du direkt befüllen willst
        feldnamen = [
            "schnam",
            "sohlhoehe",
            "deckelhoehe",
            "durchm",
            "druckdicht",
            "ueberstauflaeche",
            "entwart",
            "strasse",
            "baujahr",
            "eigentum",
            "teilgebiet",
            "knotentyp",
            "auslasstyp",
            "schachttyp",
            "simstatus",
            "material",
            "kommentar",
        ]

        for name in feldnamen:
            edit = QLineEdit(self)

            # einfache Heuristik für numerische Felder
            if name in ["sohlhoehe", "deckelhoehe", "durchm", "ueberstauflaeche"]:
                validator = QDoubleValidator(self)
                validator.setLocale(QLocale(QLocale.English))
                edit.setValidator(validator)
                edit.setPlaceholderText("Zahl (Punkt als Dezimaltrenner)")

            self.edits[name] = edit
            layout.addRow(name, edit)

        # OK/Cancel
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)