# netzuebersicht/untersuchungs_viewer.py

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from qgis.core import QgsProject
from qgis.utils import iface

from qkan.datenbankviewer import databaseviewer


def show_object_untersuchung(self):
    """Öffnet den Datenbankviewer aus der Netzübersicht für die aktuelle Auswahl."""

    current_index = self.tab_Overview.currentIndex()

    if current_index == 0:
        layer_name = "Haltungen"
        column_name = "haltnam"
        table_view = self.tableView_Haltungen
        model = self.model_haltungen
        proxy_model = self.proxy_model_haltungen
    elif current_index == 1:
        layer_name = "Schächte"
        column_name = "schnam"
        table_view = self.tableView_Schaechte
        model = self.model_schaechte
        proxy_model = self.proxy_model_schaechte
    elif current_index == 2:
        layer_name = "Anschlussleitungen"
        column_name = "leitnam"
        table_view = self.tableView_GAL
        model = self.model_anschlussleitungen
        proxy_model = self.proxy_model_anschlussleitungen
    else:
        QMessageBox.warning(self, "Ungültiger Tab", "Dieser Tab wird nicht unterstützt.")
        return

    # 1) Auswahl im TableView prüfen
    selection_model = table_view.selectionModel()
    if not selection_model or not selection_model.hasSelection():
        QMessageBox.warning(
            self,
            "Keine Auswahl",
            "Bitte wählen Sie einen oder mehrere Einträge aus."
        )
        return

    # 2) Spaltenindex bestimmen
    column_index = model.record().indexOf(column_name)
    if column_index < 0:
        QMessageBox.warning(
            self,
            "Fehler",
            f"Die Schlüsselspalte '{column_name}' wurde im Modell nicht gefunden."
        )
        return

    # 3) Stammdaten aus erster Zeile holen
    selected_rows = selection_model.selectedRows()
    first_row_proxy = selected_rows[0]
    first_row_source = proxy_model.mapToSource(first_row_proxy)
    record = model.record(first_row_source.row())

    stammdaten_dict = {}
    for i in range(record.count()):
        field_name = record.fieldName(i)
        val = record.value(i)
        stammdaten_dict[field_name] = str(val) if val is not None else ""

    # 4) Key-Werte aus allen ausgewählten Zeilen
    values = []
    for row in selected_rows:
        source_index = proxy_model.mapToSource(row)
        value = model.data(
            source_index.sibling(source_index.row(), column_index),
            Qt.DisplayRole
        )
        if value not in (None, ""):
            values.append(value)

    values = list(dict.fromkeys(values))

    if not values:
        QMessageBox.warning(
            self,
            "Keine Werte",
            "Keine Schlüsselwerte ermittelt."
        )
        return

    # 5) SICHERSTELLEN: passender Layer geladen + selektiert + aktiv

    # Für Anschlussleitungen zusätzliche Layernamen zulassen
    if layer_name == "Anschlussleitungen":
        possible_layer_names = ["Anschlussleitungen", "HA-Leitungen", "GAL"]
    else:
        possible_layer_names = [layer_name]

    # a) Layer suchen
    layers = []
    for name in possible_layer_names:
        found_layers = QgsProject.instance().mapLayersByName(name)
        if found_layers:
            layers = found_layers
            break

    # b) Layer laden, falls noch nicht vorhanden
    if not layers:
        self.layer_import_aktuell()

        for name in possible_layer_names:
            found_layers = QgsProject.instance().mapLayersByName(name)
            if found_layers:
                layers = found_layers
                break

    if not layers:
        QMessageBox.critical(
            self,
            "Fehler",
            f"Layer konnte nicht geladen werden.\nGesucht wurde nach: {', '.join(possible_layer_names)}"
        )
        return

    layer = layers[0]
    iface.setActiveLayer(layer)

    # c) Auswahl im Layer setzen (ohne Zoom)
    escaped_values = [str(v).replace("'", "''") for v in values]
    expr_values = ["'{}'".format(v) for v in escaped_values]
    expr = f'"{column_name}" IN ({",".join(expr_values)})'

    layer.removeSelection()
    layer.selectByExpression(expr)

    # 6) Layername für Viewer anpassen
    viewer_layer_name = "GAL" if layer_name == "Anschlussleitungen" else layer_name

    # 7) Viewer öffnen
    try:
        self.viewer_dialog = databaseviewer(
            parent=self,
            layer_name=viewer_layer_name,
            key_values=values,
            table_type=layer_name,
            date_tabs=None,
            stammdaten=stammdaten_dict,
            db_type="spatialite",
            spatialite_conn=self.conn,
        )

        self.viewer_dialog.show()
        self.viewer_dialog.raise_()
        self.viewer_dialog.activateWindow()

    except Exception as e:
        QMessageBox.critical(
            self,
            "Datenbankfehler",
            f"Datenbankviewer konnte nicht geöffnet werden:\n{str(e)}"
        )