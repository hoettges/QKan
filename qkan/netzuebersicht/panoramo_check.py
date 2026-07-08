# netzuebersicht/panoramo_check.py
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsFeatureRequest
from qgis.utils import iface
from .PanoramoPruefer import FehlendeDateienDialog


def zeige_datei_pruefung(self):
    """Prüft Panoramo-/PanoramoSI-Dateien für ausgewählte Haltungen.

    Der Nutzer kann wählen, ob die Haltungsnamen aus der Tabellen-Auswahl
    oder aus der Selektion des aktuell aktiven QGIS-Layers gelesen werden.

    Falls beim Lesen aus dem Layer der aktive Layer keine Spalte 'haltnam'
    enthält, wird automatisch auf den Layer 'Haltungen' gewechselt und
    die aktuelle Tabellen-Selektion - sofern vorhanden - auf den Layer übertragen.
    """

    print("========== PANORAMO CHECK START ==========")

    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Panoramo-Check")
    msg.setText("Wo sollen die Haltungsnamen ausgelesen werden?")
    msg.setInformativeText("Bitte wählen Sie die Quelle für den Panoramo-Check.")

    btn_table = msg.addButton("Aus Tabelle", QMessageBox.AcceptRole)
    btn_layer = msg.addButton("Aus aktivem Layer", QMessageBox.ActionRole)
    btn_cancel = msg.addButton("Abbrechen", QMessageBox.RejectRole)

    msg.setDefaultButton(btn_table)
    msg.exec_()

    clicked = msg.clickedButton()
    print(f"[PanoramoCheck] clickedButton = {clicked}")

    if clicked == btn_cancel or clicked is None:
        print("[PanoramoCheck] Abbruch durch Benutzer")
        print("========== PANORAMO CHECK ENDE ==========")
        return

    haltnam_liste = []

    def debug_print_layer(layer, prefix):
        if layer is None:
            print(f"{prefix} layer = None")
            return

        print(f"{prefix} layer.name() = {layer.name()}")
        try:
            print(f"{prefix} layer.id() = {layer.id()}")
        except Exception as e:
            print(f"{prefix} layer.id() Fehler: {e}")

        try:
            print(f"{prefix} layer.providerType() = {layer.providerType()}")
        except Exception as e:
            print(f"{prefix} layer.providerType() Fehler: {e}")

        try:
            print(f"{prefix} layer.source() = {layer.source()}")
        except Exception as e:
            print(f"{prefix} layer.source() Fehler: {e}")

        try:
            print(f"{prefix} fields = {layer.fields().names()}")
        except Exception as e:
            print(f"{prefix} fields Fehler: {e}")

        try:
            print(f"{prefix} selectedFeatureCount = {layer.selectedFeatureCount()}")
        except Exception as e:
            print(f"{prefix} selectedFeatureCount Fehler: {e}")

    def get_haltnam_liste_from_table():
        """Liest haltnam-Werte aus der Selektion der Tabelle Haltungen."""
        print("[PanoramoCheck][Tabelle] Lese Auswahl aus tableView_Haltungen")

        if not hasattr(self, "tableView_Haltungen") or self.tableView_Haltungen is None:
            raise RuntimeError("Die Tabellenansicht für Haltungen ist nicht verfügbar.")

        if not hasattr(self, "proxy_model_haltungen") or self.proxy_model_haltungen is None:
            raise RuntimeError("Das Proxy-Modell für Haltungen ist nicht verfügbar.")

        if not hasattr(self, "model_haltungen") or self.model_haltungen is None:
            raise RuntimeError("Das Datenmodell für Haltungen ist nicht verfügbar.")

        table_view = self.tableView_Haltungen
        model = self.model_haltungen
        proxy = self.proxy_model_haltungen

        selection_model = table_view.selectionModel()
        print(f"[PanoramoCheck][Tabelle] selection_model vorhanden = {selection_model is not None}")
        if not selection_model or not selection_model.hasSelection():
            print("[PanoramoCheck][Tabelle] Keine Auswahl in der Tabelle vorhanden")
            return []

        if hasattr(model, "record"):
            col_idx = model.record().indexOf("haltnam")
        else:
            col_idx = model.fieldIndex("haltnam")

        print(f"[PanoramoCheck][Tabelle] Spaltenindex 'haltnam' = {col_idx}")
        if col_idx < 0:
            raise RuntimeError("Die Spalte 'haltnam' wurde im Datenmodell nicht gefunden.")

        selected_indexes = selection_model.selection().indexes()
        unique_rows = set(idx.row() for idx in selected_indexes)
        print(f"[PanoramoCheck][Tabelle] Anzahl selektierter Zeilen = {len(unique_rows)}")

        values = []
        for row_num in unique_rows:
            proxy_idx = proxy.index(row_num, 0)
            source_idx = proxy.mapToSource(proxy_idx)
            target_idx = source_idx.sibling(source_idx.row(), col_idx)
            val = model.data(target_idx, Qt.DisplayRole)

            print(f"[PanoramoCheck][Tabelle] row={row_num}, haltnam roh = {val}")

            if val is not None:
                val_str = str(val).strip()
                if val_str:
                    values.append(val_str)

        values = list(dict.fromkeys(values))
        print(f"[PanoramoCheck][Tabelle] haltnam_liste = {values}")
        return values

    def ensure_haltungen_layer_active():
        """Sorgt dafür, dass ein Layer mit Feld 'haltnam' aktiv ist.
        Wenn der aktuelle Layer das Feld nicht hat, wird nach 'Haltungen' gesucht.
        """
        print("[PanoramoCheck][Layer] Prüfe aktiven Layer")
        layer = iface.activeLayer()
        debug_print_layer(layer, "[PanoramoCheck][Layer][active]")

        if layer is not None:
            try:
                field_names = layer.fields().names()
                print(f"[PanoramoCheck][Layer] Feldnamen aktiver Layer = {field_names}")
                if "haltnam" in field_names:
                    print("[PanoramoCheck][Layer] Aktiver Layer enthält 'haltnam' -> kein Wechsel nötig")
                    return layer, False
                else:
                    print("[PanoramoCheck][Layer] Aktiver Layer enthält KEIN 'haltnam'")
            except Exception as e:
                print(f"[PanoramoCheck][Layer] Fehler beim Lesen der Feldnamen des aktiven Layers: {e}")

        print("[PanoramoCheck][Layer] Suche nach Layername 'Haltungen'")
        project_layers = list(QgsProject.instance().mapLayers().values())
        print(f"[PanoramoCheck][Layer] Projekt enthält {len(project_layers)} Layer")

        for i, lyr in enumerate(project_layers):
            try:
                print(
                    f"[PanoramoCheck][Layer] Projektlayer {i}: "
                    f"name={lyr.name()}, provider={lyr.providerType()}, source={lyr.source()}"
                )
            except Exception as e:
                print(f"[PanoramoCheck][Layer] Projektlayer {i}: Debug-Fehler: {e}")

        layer_list = QgsProject.instance().mapLayersByName("Haltungen")
        print(f"[PanoramoCheck][Layer] mapLayersByName('Haltungen') Treffer = {len(layer_list)}")

        if not layer_list:
            raise RuntimeError(
                "Der aktive Layer enthält keine Spalte 'haltnam' und der Layer 'Haltungen' wurde nicht gefunden."
            )

        layer = layer_list[0]
        print(f"[PanoramoCheck][Layer] Verwende gefundenen Layer: {layer.name()}")
        debug_print_layer(layer, "[PanoramoCheck][Layer][found]")

        iface.setActiveLayer(layer)
        print("[PanoramoCheck][Layer] iface.setActiveLayer(layer) ausgeführt")

        active_after = iface.activeLayer()
        debug_print_layer(active_after, "[PanoramoCheck][Layer][after setActiveLayer]")

        try:
            field_names = layer.fields().names()
            print(f"[PanoramoCheck][Layer] Feldnamen gefundener Layer = {field_names}")
        except Exception as e:
            raise RuntimeError(f"Der gefundene Layer 'Haltungen' besitzt keine lesbaren Felder: {e}")

        if "haltnam" not in field_names:
            raise RuntimeError("Auch der Layer 'Haltungen' enthält keine Spalte 'haltnam'.")

        return layer, True

    def transfer_table_selection_to_layer(layer):
        """Überträgt die Tabellen-Selektion auf den Layer 'Haltungen'."""
        print("[PanoramoCheck][Transfer] Übertrage Tabellen-Selektion auf Layer")
        debug_print_layer(layer, "[PanoramoCheck][Transfer][layer before]")

        haltnam_values = get_haltnam_liste_from_table()
        print(f"[PanoramoCheck][Transfer] haltnam_values aus Tabelle = {haltnam_values}")

        if not haltnam_values:
            print("[PanoramoCheck][Transfer] Keine Tabellen-Auswahl vorhanden -> keine Übertragung")
            return []

        safe_values = ["'{}'".format(str(v).replace("'", "''")) for v in haltnam_values]
        expr = f"\"haltnam\" IN ({','.join(safe_values)})"
        print(f"[PanoramoCheck][Transfer] QGIS-Ausdruck = {expr}")

        features = list(layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr)))
        feature_ids = [f.id() for f in features]

        print(f"[PanoramoCheck][Transfer] Gefundene Feature-IDs = {feature_ids}")

        layer.removeSelection()
        print("[PanoramoCheck][Transfer] Vorhandene Layer-Selektion entfernt")

        if feature_ids:
            print("[PanoramoCheck][Transfer] Verwende layer.selectByIds(...)")
            layer.selectByIds(feature_ids)
        else:
            print("[PanoramoCheck][Transfer] Keine passenden Features im Layer gefunden")

        debug_print_layer(layer, "[PanoramoCheck][Transfer][layer after]")
        return haltnam_values

    try:
        if clicked == btn_table:
            print("[PanoramoCheck] Quelle = Tabelle")
            haltnam_liste = get_haltnam_liste_from_table()

            if not haltnam_liste:
                QMessageBox.information(
                    self,
                    "Panoramo-Check",
                    "In der Tabelle 'Haltungen' sind keine Zeilen ausgewählt.",
                )
                print("[PanoramoCheck] Keine Zeilen in Tabelle selektiert")
                print("========== PANORAMO CHECK ENDE ==========")
                return

        elif clicked == btn_layer:
            print("[PanoramoCheck] Quelle = aktiver Layer")
            layer, switched_to_haltungen = ensure_haltungen_layer_active()
            print(f"[PanoramoCheck] switched_to_haltungen = {switched_to_haltungen}")

            if switched_to_haltungen:
                print("[PanoramoCheck] Layer wurde auf 'Haltungen' gewechselt")
                try:
                    table_haltnam = transfer_table_selection_to_layer(layer)
                    print(f"[PanoramoCheck] Übertragene Tabellenwerte = {table_haltnam}")
                except Exception as transfer_err:
                    print(f"[PanoramoCheck] Fehler beim Übertragen der Tabellen-Selektion: {transfer_err}")
                    QMessageBox.warning(
                        self,
                        "Panoramo-Check",
                        f"Layer 'Haltungen' wurde aktiviert, aber die Tabellen-Selektion "
                        f"konnte nicht auf den Layer übertragen werden:\n{transfer_err}",
                    )
                    table_haltnam = []

                if table_haltnam:
                    haltnam_liste = table_haltnam

            selected_features = layer.selectedFeatures()
            print(f"[PanoramoCheck] Anzahl selected_features im Layer = {len(selected_features)}")

            if not selected_features:
                QMessageBox.information(
                    self,
                    "Panoramo-Check",
                    "Im aktiven Layer 'Haltungen' sind keine Features ausgewählt.",
                )
                print("[PanoramoCheck] Keine Features im Layer selektiert")
                print("========== PANORAMO CHECK ENDE ==========")
                return

            haltnam_from_layer = []
            for i, feat in enumerate(selected_features):
                try:
                    value = feat["haltnam"]
                    print(f"[PanoramoCheck] selected_feature {i}: haltnam = {value}")
                except Exception as e:
                    print(f"[PanoramoCheck] selected_feature {i}: Fehler beim Lesen von 'haltnam': {e}")
                    continue

                if value is None:
                    continue

                value_str = str(value).strip()
                if value_str:
                    haltnam_from_layer.append(value_str)

            haltnam_from_layer = list(dict.fromkeys(haltnam_from_layer))
            print(f"[PanoramoCheck] haltnam_from_layer dedupliziert = {haltnam_from_layer}")

            if haltnam_from_layer:
                haltnam_liste = haltnam_from_layer

    except Exception as e:
        print(f"[PanoramoCheck] FEHLER beim Ermitteln der Auswahl: {type(e).__name__}: {e}")
        QMessageBox.critical(
            self,
            "Panoramo-Check",
            f"Fehler beim Ermitteln der Auswahl:\n{type(e).__name__}: {e}",
        )
        print("========== PANORAMO CHECK ENDE ==========")
        return

    haltnam_liste = list(dict.fromkeys(haltnam_liste))
    print(f"[PanoramoCheck] finale haltnam_liste = {haltnam_liste}")

    if not haltnam_liste:
        QMessageBox.information(
            self,
            "Panoramo-Check",
            "Es konnten keine gültigen 'haltnam'-Werte ermittelt werden.",
        )
        print("[PanoramoCheck] finale haltnam_liste leer")
        print("========== PANORAMO CHECK ENDE ==========")
        return

    try:
        print("[PanoramoCheck] Starte check_files_for_names(...)")
        result = self.panoramo_pruefer.check_files_for_names(haltnam_liste)
        print(f"[PanoramoCheck] Ergebnis-Typ = {type(result).__name__}")
        print(f"[PanoramoCheck] Ergebnis-Inhalt = {result}")
    except Exception as e:
        print(f"[PanoramoCheck] FEHLER bei der Dateiprüfung: {type(e).__name__}: {e}")
        QMessageBox.critical(
            self,
            "Panoramo-Check",
            f"Fehler bei der Dateiprüfung:\n{type(e).__name__}: {e}",
        )
        print("========== PANORAMO CHECK ENDE ==========")
        return

    if not isinstance(result, dict):
        QMessageBox.critical(
            self,
            "Panoramo-Check",
            "Die Dateiprüfung hat kein gültiges Ergebnis geliefert.",
        )
        print("[PanoramoCheck] Ergebnis ist kein dict")
        print("========== PANORAMO CHECK ENDE ==========")
        return

    anzahl_selektiert = len(haltnam_liste)

    vorhanden_panoramo = [
        name for name, v in result.items()
        if isinstance(v, dict) and v.get("exists_panoramo")
    ]
    vorhanden_panoramoSI = [
        name for name, v in result.items()
        if isinstance(v, dict) and v.get("exists_panoramoSI")
    ]
    fehlend_panoramo = [
        name for name, v in result.items()
        if isinstance(v, dict) and not v.get("exists_panoramo")
    ]
    fehlend_panoramoSI = [
        name for name, v in result.items()
        if isinstance(v, dict) and not v.get("exists_panoramoSI")
    ]

    print(f"[PanoramoCheck] vorhanden_panoramo = {vorhanden_panoramo}")
    print(f"[PanoramoCheck] vorhanden_panoramoSI = {vorhanden_panoramoSI}")
    print(f"[PanoramoCheck] fehlend_panoramo = {fehlend_panoramo}")
    print(f"[PanoramoCheck] fehlend_panoramoSI = {fehlend_panoramoSI}")

    text = (
        f"Anzahl ausgewählter Haltungen: {anzahl_selektiert}\n"
        f"Vorhandene Panoramo-Dateien: {len(vorhanden_panoramo)}\n"
        f"Vorhandene PanoramoSI-Dateien: {len(vorhanden_panoramoSI)}\n"
        f"Fehlende Panoramo-Dateien: {len(fehlend_panoramo)}\n"
        f"Fehlende PanoramoSI-Dateien: {len(fehlend_panoramoSI)}"
    )
    QMessageBox.information(self, "Dateiprüfung Ergebnis", text)

    if fehlend_panoramo:
        print("[PanoramoCheck] Öffne Dialog für fehlende Panoramo-Dateien")
        dlg1 = FehlendeDateienDialog(fehlend_panoramo, self)
        dlg1.setWindowTitle("Fehlende Panoramo-Dateien")
        dlg1.exec_()

    if fehlend_panoramoSI:
        print("[PanoramoCheck] Öffne Dialog für fehlende PanoramoSI-Dateien")
        dlg2 = FehlendeDateienDialog(fehlend_panoramoSI, self)
        dlg2.setWindowTitle("Fehlende PanoramoSI-Dateien")
        dlg2.exec_()

    print("========== PANORAMO CHECK ENDE ==========")