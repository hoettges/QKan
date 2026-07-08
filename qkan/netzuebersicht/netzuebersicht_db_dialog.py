# qkan/netzuebersicht/netzuebersicht_db_dialog.py
import os
import json


from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QDialog,
    QMessageBox,
    QFrame,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QApplication,
)
from qgis.core import Qgis, QgsFeatureRequest, QgsProject, QgsMapLayerType, QgsDataSourceUri
from qgis.utils import iface


from qkan.__init__ import QKan


# Tools aus QKan
from .PanoramoPruefer import PanoramoPruefer, FehlendeDateienDialog
from .sonderbauwerke import (
    sonderbauwerk_anlegen,
    sonderbauwerk_loeschen,
    sonderbauwerk_bearbeiten,
)


# DB-Backend (QKan-SpatiaLite/Postgres abstrahiert)
from .db_backend import get_db_type, get_backend


# Table-/GIS-/Funktionen (Backend-agnostisch)
from .table_models import (
    fill_column_combobox,
    update_filter_current_tab,
)
from .gis_actions import (
    zoom_to_selected_features,
    select_feature,
    layer_import_aktuell,
    erzeuge_schacht,
    erzeuge_haltung,
    teile_haltung,
    erzeuge_sinkkasten,
)
from .excel_import_sinkkaesten import excel_import_sinkkaesten
from .export_investigations import export_latest_investigations
from .panoramo_check import zeige_datei_pruefung
from .untersuchungs_viewer import show_object_untersuchung
from .kostenermittlung_wrapper import kostenermittlung_wrapper
from .ausgabe_reinigungslisten import LinePolygonAggregateDialog
from .object_info_dialog import ObjectInfoDialog



FORM_CLASS_netzuebersicht, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "Netzübersicht - Kopie.ui")
)



class Netzuebersicht_DB(QDialog, FORM_CLASS_netzuebersicht):
    """
    Netzübersicht-Dialog, der auf dem QKan-Datenbankkontext (SpatiaLite/Postgres)
    und dem gemeinsamen db_backend aufsetzt.
    """


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # --- NEU: lokale DB-Erkennung, falls QKan.dbsource noch leer ist ---
        print(f"[Netzuebersicht_DB] Start: QKan.dbsource = {getattr(QKan, 'dbsource', None)}")

        if getattr(QKan, "dbsource", None):
            print("[Netzuebersicht_DB] Verwende bestehende QKan-Verbindung")
        else:
            print("[Netzuebersicht_DB] Keine QKan-Verbindung vorhanden -> starte Fallback über Projektlayer")

            project = QgsProject.instance()
            for layer in project.mapLayers().values():
                try:
                    print(
                        f"[Netzuebersicht_DB] Prüfe Layer: "
                        f"name={layer.name()}, provider={layer.providerType()}, source={layer.source()}"
                    )

                    if layer.type() != QgsMapLayerType.VectorLayer:
                        print("[Netzuebersicht_DB]  -> übersprungen: kein Vektorlayer")
                        continue

                    if layer.providerType() != "spatialite":
                        print("[Netzuebersicht_DB]  -> übersprungen: provider != spatialite")
                        continue

                    uri = QgsDataSourceUri(layer.source())
                    db_path = uri.database()
                    table_name = (uri.table() or "").replace('"', "")

                    print(
                        f"[Netzuebersicht_DB]  -> db_path={db_path}, table_name={table_name}"
                    )

                    if not db_path:
                        print("[Netzuebersicht_DB]  -> übersprungen: kein db_path")
                        continue

                    if table_name not in {
                        "haltungen",
                        "schaechte",
                        "anschlussleitungen",
                        "entwaesserungsrinnen",
                        "sonderbauwerke_view",
                        "Sinkkästen",
                        "Sinkkaesten",
                    }:
                        print("[Netzuebersicht_DB]  -> übersprungen: kein bekannter QKan-Tabellenname")
                        continue

                    QKan.dbsource = layer.source()
                    print(
                        f"[Netzuebersicht_DB] Fallback erfolgreich -> "
                        f"QKan.dbsource aus Layer '{layer.name()}' übernommen"
                    )
                    break

                except Exception as e:
                    print(f"[Netzuebersicht_DB] Fallback-Fehler bei Layer '{layer.name()}': {e}")
                    continue

        print(f"[Netzuebersicht_DB] Ende DB-Erkennung: QKan.dbsource = {getattr(QKan, 'dbsource', None)}")

        if not getattr(QKan, "dbsource", None):
            print("[Netzuebersicht_DB] Weder QKan-Verbindung noch Fallback erfolgreich")
            QMessageBox.information(
                self,
                "QKan Netzübersicht",
                "Es ist keine aktive QKan-Datenbank verfügbar.\n"
                "Bitte öffne zuerst eine QKan-Datenbank (QKan-Menü → Allgemein)\n"
                "und starte dann die Netzübersicht erneut.",
            )
            self.reject()
            return
        
        self.setWindowModality(Qt.NonModal)
        self.setModal(False)


        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )


        # Debounce-Timer für Textfilter
        self.filter_timer = QTimer(self)
        self.filter_timer.setInterval(1000)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.apply_filter_debounced)


        # 0. DB-Typ und Backend
        self.db_type = "spatialite"
        self.backend = get_backend(self.db_type)

        # 1. Native Verbindung bevorzugt aus QKan.dbsource
        self.conn = None
        self.cursor = None
        self.config = {}

        dbsource = getattr(QKan, "dbsource", None)
        if dbsource:
            self.conn, self.cursor, self.config = self.backend.load_native_connection_from_qkan(
                self, dbsource
            )

        # Fallback (sollte selten gebraucht werden)
        if self.conn is None:
            self.conn, self.cursor, self.config = self.backend.load_native_connection(self)

        if self.conn is None:
            QMessageBox.critical(
                self,
                "QKan Netzübersicht",
                "Es konnte keine Verbindung zur QKan-Datenbank hergestellt werden.",
            )
            self.reject()
            return


        # 2. Konfiguration aus Backend
        self.db_host = self.config.get("host", "")
        self.db_database = self.config.get("database", "")
        self.db_user = self.config.get("user", "")
        self.db_password = self.config.get("password", "")


        # Validierung (insbesondere für Postgres)
        if self.db_type == "postgresql":
            if not all([self.db_host, self.db_database, self.db_user, self.db_password]):
                QMessageBox.critical(
                    self,
                    "Fehlerhafte Zugangsdaten",
                    "PostgreSQL-Konfiguration unvollständig.\n"
                    "Bitte prüfen Sie die settings/database.json bzw. die QKan-DB-Einstellungen.",
                )
                return


        # 3. Schema/Tabellen über Backend sicherstellen
        if not self.backend.ensure_schema(self.conn, self.cursor, self):
            return


        # 4. Qt-SQL-Verbindung über Backend
        self.qt_connection_name = self.backend.build_connection_name("netzuebersicht")
        self.db = self.backend.setup_qt_connection(
            self.config, self, connection_name=self.qt_connection_name
        )
        if self.db is None:
            return


        self.debug_database_state()


        # 5. Daten in Tabellen laden
        self.backend.load_data_into_tables(self)


        # 6. Spaltenfilter-Combo initialisieren
        fill_column_combobox(self)
        from .PanoramoPruefer import PanoramoPruefer
        self.panoramo_pruefer = PanoramoPruefer(parent=self)


        # 7. Signal-Slot-Verbindungen (Filter/Tabs)
        self.Search_LineEdit.textChanged.connect(self.start_filter_debounce)
        self.comboBox_Spalten.currentIndexChanged.connect(self.apply_filter_immediate)
        self.tab_Overview.currentChanged.connect(self.on_tab_changed)


        # 8. Aktionen/Buttons
        self.Show_Object.clicked.connect(lambda: zoom_to_selected_features(self))
        self.Show_Object_Untersuchung.clicked.connect(lambda: show_object_untersuchung(self))
        self.Show_Object_Untersuchung_2.clicked.connect(lambda: show_object_untersuchung(self))
        self.Show_Object_Untersuchung_3.clicked.connect(lambda: show_object_untersuchung(self))
        self.open_Kostenermittlung.clicked.connect(lambda: kostenermittlung_wrapper(self))
        self.excel_import.clicked.connect(lambda: excel_import_sinkkaesten(self))
        self.layer_importieren_sinkkaesten.clicked.connect(lambda: layer_import_aktuell(self))
        self.Untersuchungsdaten_exportieren.clicked.connect(
            lambda: export_latest_investigations(self)
        )
        self.PanoramoPruefer.clicked.connect(lambda: zeige_datei_pruefung(self))
        self.Reinigungsliste_ausgeben.clicked.connect(self.on_aggregate_layers_clicked)


        self.Schacht_erstellen.clicked.connect(lambda: erzeuge_schacht(self))
        self.Schacht_loeschen.clicked.connect(self.on_schacht_loeschen)
        self.Haltung_erstellen.clicked.connect(lambda: erzeuge_haltung(parent=self))
        self.Haltung_teilen.clicked.connect(lambda: teile_haltung(parent=self))
        self.Haltung_loeschen.clicked.connect(self.on_haltung_loeschen)


        self.Object_Info.clicked.connect(self.show_object_info)


        # Sonderbauwerke-Buttons
        self.sonderbauwerk_anlegen_btn.clicked.connect(self.sonderbauwerk_anlegen)
        self.sonderbauwerk_loeschen_btn.clicked.connect(self.sonderbauwerk_loeschen)
        self.sonderbauwerk_bearbeiten_btn.clicked.connect(self.sonderbauwerk_bearbeiten)


        print("[Netzuebersicht_DB] __init__ gestartet")
        print(f"[Netzuebersicht_DB] erkannter db_type = {self.db_type}")
        print(f"[Netzuebersicht_DB] QKan.dbsource = {getattr(QKan, 'dbsource', None)}")
        print(f"[Netzuebersicht_DB] backend = {type(self.backend).__name__}")


        print(f"[Netzuebersicht_DB] native conn = {self.conn}")
        print(f"[Netzuebersicht_DB] native cursor = {self.cursor}")
        print(f"[Netzuebersicht_DB] config = {self.config}")
    # ------------------------------------------------------------------
    # Filter / Tabs
    # ------------------------------------------------------------------
    def start_filter_debounce(self):
        self.filter_timer.start()


    def apply_filter_debounced(self):
        update_filter_current_tab(self)


    def apply_filter_immediate(self):
        self.filter_timer.stop()
        update_filter_current_tab(self)


    def on_tab_changed(self, idx):
        self.backend.load_data_for_tab(self, idx)
        fill_column_combobox(self)
        self.apply_filter_immediate()


    # ------------------------------------------------------------------
    # Objekt-Info-Dialog
    # ------------------------------------------------------------------
    def show_object_info(self):
        current_index = self.tab_Overview.currentIndex()
        is_spatialite = getattr(self, "db_type", "") == "spatialite"


        # Sonderbauwerke-Tab
        if current_index == 5:
            if hasattr(self, "sonderbauwerk_bearbeiten"):
                self.sonderbauwerk_bearbeiten()
            else:
                QMessageBox.information(self, "Info", "Sonderbauwerke-Funktion nicht gefunden.")
            return


        # Tabellen-Mapping
        table_map = {
            0: ("haltungen", self.proxy_model_haltungen, self.model_haltungen, self.tableView_Haltungen),
            1: ("schaechte", self.proxy_model_schaechte, self.model_schaechte, self.tableView_Schaechte),
            2: ("anschlussleitungen", self.proxy_model_anschlussleitungen, self.model_anschlussleitungen, self.tableView_GAL),
            3: ("Sinkkästen", self.proxy_model_sinkkaesten, self.model_sinkkaesten, self.tableView_Sinkkaesten),
            4: ("entwaesserungsrinnen", self.proxy_model_rinnen, self.model_rinnen, self.tableView_Rinnen),
        }


        if current_index not in table_map:
            return


        raw_table_name, proxy, model, table_view = table_map[current_index]


        # Tabellenname formatieren
        if is_spatialite:
            table_name = raw_table_name
        else:
            table_name = f'"{raw_table_name}"' if not raw_table_name.startswith('"') else raw_table_name


        # Auswahl prüfen
        selection_model = table_view.selectionModel()
        selected_rows = selection_model.selectedRows(0)
        if not selected_rows:
            QMessageBox.warning(self, "Fehler", "Wähle eine Zeile aus!")
            return


        proxy_index = selected_rows[0]
        source_index = proxy.mapToSource(proxy_index)
        record = model.record(source_index.row())


        # Schlüssel ermitteln
        if raw_table_name == "Sinkkästen":
            name_idx = record.indexOf("Name")
            key_value = record.value(name_idx)
            key_field = "Name"
        elif raw_table_name == "entwaesserungsrinnen":
            name_idx = record.indexOf("Name")
            key_value = record.value(name_idx)
            key_field = "Name"
        else:
            key_value = record.value(0)
            key_field = "pk"


        # Daten extrahieren
        headers = [model.headerData(i, Qt.Horizontal) or f"Col{i}" for i in range(model.columnCount())]
        data_dict = {}
        for i, header in enumerate(headers):
            val = record.value(i)
            if val is None:
                data_dict[header] = ""
            elif isinstance(val, str) and val.upper() == "NULL":
                data_dict[header] = ""
            else:
                data_dict[header] = str(val)


        # bestehenden Dialog schließen
        if hasattr(self, "object_info_dlg") and self.object_info_dlg is not None:
            self.object_info_dlg.close()


        self.object_info_dlg = ObjectInfoDialog(self, data_dict, headers)


        # Haltungen: Längenberechnung aktivieren
        if current_index == 0:
            self.object_info_dlg.schacht_oben_btn.setEnabled(True)
            self.object_info_dlg.schacht_unten_btn.setEnabled(True)
            self.object_info_dlg.laenge_btn.setEnabled(True)


            def calculate_length():
                try:
                    layer_list = QgsProject.instance().mapLayersByName("Haltungen")
                    if not layer_list:
                        return
                    layer = layer_list[0]


                    val_str = f"'{key_value}'" if isinstance(key_value, str) else str(key_value)
                    req = QgsFeatureRequest().setFilterExpression(f'"{key_field}" = {val_str}')
                    feat = next(layer.getFeatures(req), None)


                    if feat and feat.hasGeometry():
                        l_str = f"{feat.geometry().length():.2f}"
                        if "laenge" in self.object_info_dlg.line_edits:
                            self.object_info_dlg.line_edits["laenge"].setText(l_str)
                            QMessageBox.information(
                                self.object_info_dlg,
                                "Info",
                                f"Neue Länge: {l_str} m",
                            )
                except Exception as e:
                    QMessageBox.critical(self.object_info_dlg, "Fehler", f"Fehler: {e}")


            try:
                self.object_info_dlg.laenge_btn.clicked.disconnect()
            except Exception:
                pass
            self.object_info_dlg.laenge_btn.clicked.connect(calculate_length)
        else:
            self.object_info_dlg.schacht_oben_btn.setEnabled(False)
            self.object_info_dlg.schacht_unten_btn.setEnabled(False)
            self.object_info_dlg.laenge_btn.setEnabled(False)


        # Speichern-Logik
        try:
            self.object_info_dlg.speichern_btn.clicked.disconnect()
        except Exception:
            pass


        def on_save():
            raw_changes = self.object_info_dlg.get_data()


            # Geometriespalten herausfiltern
            changes = {}
            for k, v in raw_changes.items():
                if k.lower() in [
                    "geom",
                    "geop",
                    "geometry",
                    "ogc_fid",
                    "rowid",
                    "pk",
                    "geom_point",
                    "geom_line",
                ]:
                    continue
                changes[k] = v


            try:
                self.backend.update_object(
                    table_name=table_name,
                    key_field=key_field,
                    key_value=key_value,
                    changes=changes,
                    cursor=self.cursor,
                    conn=self.conn,
                    model=model,
                )
                QMessageBox.information(self.object_info_dlg, "✅ Erfolg", "Felder gespeichert!")
                model.select()


                # SpatiaLite-Layer refresh
                if is_spatialite:
                    try:
                        l_map = {
                            "haltungen": "Haltungen",
                            "schaechte": "Schächte",
                            "anschlussleitungen": "Anschlussleitungen",
                            "entwaesserungsrinnen": "Rinnen",
                        }
                        real_name = l_map.get(raw_table_name, raw_table_name)
                        ls = QgsProject.instance().mapLayersByName(real_name)
                        if ls:
                            ls[0].triggerRepaint()
                    except Exception:
                        pass


                self.object_info_dlg.accept()
            except Exception as e:
                QMessageBox.critical(self.object_info_dlg, "❌ Fehler", str(e))


        self.object_info_dlg.speichern_btn.clicked.connect(on_save)


        self.object_info_dlg.setWindowModality(Qt.NonModal)
        self.object_info_dlg.show()


    # ------------------------------------------------------------------
    # Lösch- und Aggregationsfunktionen
    # ------------------------------------------------------------------
    def on_schacht_loeschen(self):
        self.delete_selected_with_names(
            table_view=self.tableView_Schaechte,
            proxy_model=self.proxy_model_schaechte,
            sql_model=self.model_schaechte,
            name_column="schnam",
            title="Schächte löschen",
        )


    def on_haltung_loeschen(self):
        self.delete_selected_with_names(
            table_view=self.tableView_Haltungen,
            proxy_model=self.proxy_model_haltungen,
            sql_model=self.model_haltungen,
            name_column="haltnam",
            title="Haltungen löschen",
        )


    def delete_selected_with_names(
        self, table_view, proxy_model, sql_model, name_column, title
    ):
        sel = table_view.selectionModel().selectedRows()
        if not sel:
            QMessageBox.information(self, title, "Keine Zeilen ausgewählt.")
            return


        col_idx = sql_model.record().indexOf(name_column)
        if col_idx < 0:
            QMessageBox.critical(self, title, f"Spalte '{name_column}' nicht gefunden.")
            return


        names = []
        source_rows = []
        for proxy_idx in sel:
            src_idx = proxy_model.mapToSource(proxy_idx)
            source_rows.append(src_idx.row())
            name = sql_model.data(sql_model.index(src_idx.row(), col_idx), Qt.DisplayRole)
            names.append("" if name is None else str(name))


        seen = set()
        names_unique = []
        for n in names:
            if n not in seen:
                seen.add(n)
                names_unique.append(n)


        preview = "\n".join(f"- {n}" for n in names_unique[:15])
        more = ""
        if len(names_unique) > 15:
            more = f"\n… (+{len(names_unique) - 15} weitere)"


        msg = f"Folgende Objekte werden gelöscht:\n{preview}{more}\n\nFortfahren?"
        if (
            QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No)
            != QMessageBox.Yes
        ):
            return


        try:
            self.backend.delete_rows(sql_model, source_rows)
            sql_model.select()
        except Exception as e:
            QMessageBox.critical(self, title, f"Löschen fehlgeschlagen: {e}")


    def on_aggregate_layers_clicked(self):
        dialog = LinePolygonAggregateDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            iface.messageBar().pushMessage(
                "Erfolg", "Aggregierter Layer erstellt!", Qgis.Success
            )


    # ------------------------------------------------------------------
    # Sonderbauwerke
    # ------------------------------------------------------------------
    def sonderbauwerk_anlegen(self):
        sonderbauwerk_anlegen(self)


    def sonderbauwerk_loeschen(self):
        sonderbauwerk_loeschen(self)


    def sonderbauwerk_bearbeiten(self):
        sonderbauwerk_bearbeiten(self)


    def on_sinkkasten_erstellen(self):
        erzeuge_sinkkasten(self)


    def on_sinkkasten_loeschen(self):
        self.delete_selected_with_names(
            table_view=self.tableView_Sinkkaesten,
            proxy_model=self.proxy_model_sinkkaesten,
            sql_model=self.model_sinkkaesten,
            name_column="Name",
            title="Sinkkästen löschen",
        )


    def debug_database_state(self):
        print("========== NETZUEBERSICHT DB DEBUG ==========")
        print(f"db_type = {getattr(self, 'db_type', None)}")
        print(f"QKan.dbsource = {getattr(QKan, 'dbsource', None)}")
        print(f"backend = {type(getattr(self, 'backend', None)).__name__}")
        print(f"conn vorhanden = {self.conn is not None}")
        print(f"cursor vorhanden = {self.cursor is not None}")
        print(f"qt db vorhanden = {self.db is not None}")


        if self.db is not None:
            try:
                print(f"qt db isValid = {self.db.isValid()}")
                print(f"qt db isOpen = {self.db.isOpen()}")
                print(f"qt db connectionName = {self.db.connectionName()}")
                print(f"qt db driver = {self.db.driverName()}")
                print(f"qt db databaseName = {self.db.databaseName()}")
                print(f"qt db hostName = {self.db.hostName()}")
                print(f"qt db userName = {self.db.userName()}")
                print(f"qt db lastError = {self.db.lastError().text()}")
            except Exception as e:
                print(f"qt db debug error: {e}")


        for tbl in ["haltungen", "schaechte", "anschlussleitungen", "entwaesserungsrinnen"]:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
                count = self.cursor.fetchone()[0]
                print(f"[native] {tbl}: {count} Zeilen")
            except Exception as e:
                print(f"[native] {tbl}: FEHLER -> {e}")


        for tbl in ['"Sinkkästen"', 'Sinkkästen', 'Sinkkaesten', '"Sinkkaesten"']:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
                count = self.cursor.fetchone()[0]
                print(f"[native] {tbl}: {count} Zeilen")
            except Exception as e:
                print(f"[native] {tbl}: FEHLER -> {e}")


        print("=============================================")
    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        # KEIN backend.cleanup(self) hier mehr
        super().closeEvent(event)