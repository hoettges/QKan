"""
__init__.py - Hauptmodul des QGIS-Plugins Datenbankviewer
Enthält die zentrale Dialog-Klasse databaseviewer.
"""

import os
import sys

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QMessageBox,
    QTableWidget,
    QTabWidget,
    QWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from qgis.PyQt.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor

from qgis.utils import iface

# Lokale Imports
from .db_connection import load_qkan_connection
from .data_queries import (
    SQLAbfrage,
    toggleeditmode,
    save_changes_to_database,
    find_inner_table_widget,
    delete_selected_rows,
    get_db_context,
)
from .ui_handlers import (
    start_video_clicked,
    open_sanierungstool,
    Bauwerkszeichnung_oeffnen,
    Panoramo_oeffnen,
    PanoramoSI_oeffnen,
    display_selected_feature,
    opendocumentmanagement,
    showVisualization,
)
from .utils import clearfields
from .neuer_schaden_helper import NewUntersuchungDialog

# UI-Datei laden
FORMCLASSdatabaseviewerui, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "database_viewer.ui")
)


class databaseviewer(QDialog, FORMCLASSdatabaseviewerui):
    """Haupt-Dialog für Datenbankviewer (QKan / SpatiaLite)."""

    informationsignal = pyqtSignal(str)

    # =========================================================
    # Initialisierung
    # =========================================================
    def __init__(
        self,
        parent=None,
        layer_name=None,
        key_values=None,
        table_type=None,
        date_tabs=None,
        stammdaten=None,
        db_type="spatialite",
        spatialite_conn=None,
    ):
        super(databaseviewer, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.db_type = "spatialite"
        self.spatialite_conn = spatialite_conn
        self.external_mode = (layer_name is not None and key_values is not None)
        self.preloaded_data = date_tabs

        # -----------------------------------------------------
        # Verbindungsaufbau
        # -----------------------------------------------------
        if not self.preloaded_data:
            if self.spatialite_conn is not None:
                self.conn = self.spatialite_conn
            else:
                self.conn = load_qkan_connection(self)

            if self.conn is None:
                return
        else:
            self.conn = None

        # -----------------------------------------------------
        # UI vorbereiten
        # -----------------------------------------------------
        clearfields(self)

        # -----------------------------------------------------
        # Signal-Verbindungen
        # -----------------------------------------------------
        self.start_video_button.clicked.connect(lambda: start_video_clicked(self))
        self.get_info_button.clicked.connect(lambda: SQLAbfrage(self))
        self.Sanierungsverfahren.clicked.connect(lambda: open_sanierungstool(self))
        self.Bauwerkszeichnung.clicked.connect(lambda: Bauwerkszeichnung_oeffnen(self))
        self.Panoramo.clicked.connect(lambda: Panoramo_oeffnen(self))
        self.PanoramoSI.clicked.connect(lambda: PanoramoSI_oeffnen(self))
        self.layout_button.clicked.connect(lambda: display_selected_feature(self))
        self.document_management_button.clicked.connect(lambda: opendocumentmanagement(self))
        self.edit_button.clicked.connect(lambda: toggleeditmode(self))
        self.Grafik.clicked.connect(lambda: showVisualization(self))

        self.neuer_bericht_button.clicked.connect(lambda: self.neuer_untersuchungsbericht())
        self.change_row_button.clicked.connect(self.change_row_in_current_table)
        self.add_row_button.clicked.connect(lambda: self.add_row_to_current_table())
        self.delete_row_button.clicked.connect(lambda: self.delete_row_from_current_table())

        # -----------------------------------------------------
        # Fensterverhalten
        # -----------------------------------------------------
        self.setWindowModality(Qt.NonModal)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )

        # -----------------------------------------------------
        # Externer Modus
        # -----------------------------------------------------
        if self.external_mode:
            self.external_layer_name = layer_name
            self.external_key_values = key_values
            self.external_table_type = table_type or layer_name

            if self.preloaded_data:
                if stammdaten:
                    self.fill_stammdaten_from_dict(stammdaten)
                self.build_ui_from_data(self.preloaded_data)
            else:
                if stammdaten:
                    self.fill_stammdaten_from_dict(stammdaten)
                else:
                    self.fill_stammdaten_external(key_values[0])

                SQLAbfrage(self)

            return

        # -----------------------------------------------------
        # Interner Modus
        # -----------------------------------------------------
        layer = self.iface.activeLayer()
        if layer is None:
            QMessageBox.warning(self, "Kein Layer", "Bitte wählen Sie einen passenden Layer aus.")
            return

        selectedids = layer.selectedFeatureIds()
        if len(selectedids) == 0:
            QMessageBox.warning(self, "Kein Feature", "Bitte wählen Sie ein passendes Feature aus.")
            return

        feature = layer.getFeature(selectedids[0])
        SQLAbfrage(self)
        self.fill_attributes(feature)

    # =========================================================
    # Stammdaten aus Dictionary
    # =========================================================
    def fill_stammdaten_from_dict(self, data):
        """Füllt die QLineEdit-Felder aus einem Dictionary (Case-Insensitive Keys)."""

        def get_val(keys_wanted):
            if isinstance(keys_wanted, str):
                keys_wanted = [keys_wanted]

            data_keys_lower = {k.lower(): v for k, v in data.items()}

            for kw in keys_wanted:
                val = data_keys_lower.get(kw.lower())
                if val is not None:
                    return str(val)
            return ""

        self.Haltungsname.setText(get_val(["haltnam", "leitnam", "schnam"]))
        self.Strassenname.setText(get_val("strasse"))
        self.Schacht_oben.setText(get_val("schoben"))
        self.Schacht_unten.setText(get_val("schunten"))
        self.Entwaesserungssystem.setText(get_val("entwart"))
        self.Material.setText(get_val("material"))
        self.Baujahr.setText(get_val("baujahr"))
        self.StrakatID.setText(get_val("strakatid"))

        l_str = get_val("laenge")
        try:
            if l_str:
                self.Laenge.setText(f"{float(l_str.replace(',', '.')):.2f}")
            else:
                self.Laenge.setText("")
        except Exception:
            self.Laenge.setText(l_str)

        b = get_val("breite")
        h = get_val("hoehe")
        try:
            b_int = int(float(b.replace(",", "."))) if b else ""
            h_int = int(float(h.replace(",", "."))) if h else ""
            if b_int == h_int and b_int:
                self.Dimension.setText(str(b_int))
            elif b_int and h_int:
                self.Dimension.setText(f"{b_int}/{h_int}")
            else:
                self.Dimension.setText(get_val("dimension"))
        except Exception:
            self.Dimension.setText(f"{b}/{h}" if b and h else "")

        g_str = get_val("gefaelle")
        so_str = get_val("sohleoben")
        su_str = get_val("sohleunten")
        l_val = get_val("laenge")

        if so_str and su_str and l_val:
            try:
                so = float(so_str.replace(",", "."))
                su = float(su_str.replace(",", "."))
                l = float(l_val.replace(",", "."))
                if l > 0:
                    calc_g = ((so - su) / l) * 1000
                    self.Gefaelle.setText(f"{calc_g:.1f}")
                else:
                    self.Gefaelle.setText(g_str)
            except Exception:
                self.Gefaelle.setText(g_str)
        else:
            self.Gefaelle.setText(g_str)

    # =========================================================
    # Stammdaten aus Feature
    # =========================================================
    def fill_attributes(self, feature):
        """Füllt UI-Felder mit Feature-Attributen und nutzt Fallbacks für unterschiedliche Spaltennamen."""

        existing_attributes = feature.fields().names()
        attribute_values = {
            attr.lower(): str(feature.attribute(attr))
            for attr in existing_attributes
            if feature.attribute(attr) is not None
        }

        def get_val(keys_wanted):
            if isinstance(keys_wanted, str):
                keys_wanted = [keys_wanted]
            for kw in keys_wanted:
                val = attribute_values.get(kw.lower())
                if val:
                    return val
            return ""

        self.Haltungsname.setText(get_val(["haltnam", "leitnam", "schnam", "schoben"]))
        self.Schacht_oben.setText(get_val(["schoben", "schnam"]))
        self.Strassenname.setText(get_val("strasse"))
        self.Entwaesserungssystem.setText(get_val("entwart"))
        self.Schacht_unten.setText(get_val("schunten"))
        self.Material.setText(get_val("material"))
        self.Baujahr.setText(get_val("baujahr"))
        self.StrakatID.setText(get_val("strakatid"))

        laenge = get_val("laenge")
        if laenge:
            try:
                self.Laenge.setText(f"{float(laenge.replace(',', '.')):.2f}")
            except ValueError:
                self.Laenge.setText(laenge)
        else:
            self.Laenge.setText("")

        breite_str = get_val("breite")
        hoehe_str = get_val("hoehe")

        try:
            b_int = int(float(breite_str.replace(",", "."))) if breite_str else ""
            h_int = int(float(hoehe_str.replace(",", "."))) if hoehe_str else ""

            if b_int == h_int and b_int:
                self.Dimension.setText(str(b_int))
            elif b_int and h_int:
                self.Dimension.setText(f"{b_int}/{h_int}")
            else:
                self.Dimension.setText(get_val("dimension"))
        except ValueError:
            self.Dimension.setText(
                f"{breite_str}/{hoehe_str}" if breite_str and hoehe_str else get_val("dimension")
            )

        sohleoben = get_val("sohleoben")
        sohleunten = get_val("sohleunten")

        if sohleoben and sohleunten and laenge:
            try:
                so = float(sohleoben.replace(",", "."))
                su = float(sohleunten.replace(",", "."))
                l = float(laenge.replace(",", "."))
                if l > 0:
                    gefaelle = ((so - su) / l) * 1000
                    self.Gefaelle.setText(f"{gefaelle:.1f}")
                else:
                    self.Gefaelle.setText(get_val("gefaelle"))
            except ValueError:
                self.Gefaelle.setText(get_val("gefaelle"))
        else:
            self.Gefaelle.setText(get_val("gefaelle"))

    # =========================================================
    # Fallback-Methoden
    # =========================================================
    def toggleeditmode(self):
        """Fallback für Edit-Modus."""
        toggleeditmode(self)

    def SQLAbfrage(self):
        """Fallback für SQL-Abfrage."""
        SQLAbfrage(self)

    # =========================================================
    # Stammdaten extern laden
    # =========================================================
    def fill_stammdaten_external(self, key_value):
        """Füllt Stammdaten-Felder aus der DB für externen Aufruf."""
        conn, cursor, param_style = get_db_context(self)
        if conn is None:
            return

        try:
            table_map = {
                "Haltungen": "haltungen",
                "GAL": "haltungen",
                "Schächte": "schaechte",
            }
            table = table_map.get(self.external_layer_name, "haltungen")

            column_map = {
                "Haltungen": "haltnam",
                "GAL": "leitnam",
                "Schächte": "schnam",
            }
            column = column_map.get(self.external_layer_name, "haltnam")

            cursor.execute(
                f"SELECT * FROM {table} WHERE {column} = {param_style}",
                (key_value,)
            )
            result = cursor.fetchone()
            if not result:
                return

            spaltennamen_lower = [desc[0].lower() for desc in cursor.description]
            result_dict = {
                spaltennamen_lower[i]: result[i]
                for i in range(len(spaltennamen_lower))
                if result[i] is not None
            }

            def get_val(keys_wanted, default=""):
                if isinstance(keys_wanted, str):
                    keys_wanted = [keys_wanted]
                for kw in keys_wanted:
                    val = result_dict.get(kw.lower())
                    if val is not None:
                        return str(val)
                return default

            self.Haltungsname.setText(get_val(["haltnam", "leitnam", "schnam", "schoben"]))
            self.Strassenname.setText(get_val("strasse"))
            self.Schacht_oben.setText(get_val(["schoben", "schnam"]))
            self.Schacht_unten.setText(get_val("schunten"))
            self.Entwaesserungssystem.setText(get_val("entwart"))
            self.Material.setText(get_val("material"))
            self.Baujahr.setText(get_val("baujahr"))
            self.StrakatID.setText(get_val("strakatid"))

            laenge_str = get_val("laenge")
            if laenge_str:
                try:
                    self.Laenge.setText(f"{float(laenge_str.replace(',', '.')):.2f}")
                except ValueError:
                    self.Laenge.setText(laenge_str)
            else:
                self.Laenge.setText("")

            breite_str = get_val("breite")
            hoehe_str = get_val("hoehe")
            try:
                b_int = int(float(breite_str.replace(",", "."))) if breite_str else ""
                h_int = int(float(hoehe_str.replace(",", "."))) if hoehe_str else ""

                if b_int == h_int and b_int:
                    self.Dimension.setText(str(b_int))
                elif b_int and h_int:
                    self.Dimension.setText(f"{b_int}/{h_int}")
                else:
                    self.Dimension.setText(get_val("dimension"))
            except ValueError:
                self.Dimension.setText(
                    f"{breite_str}/{hoehe_str}" if breite_str and hoehe_str else get_val("dimension")
                )

            sohleoben_str = get_val("sohleoben")
            sohleunten_str = get_val("sohleunten")
            if sohleoben_str and sohleunten_str and laenge_str:
                try:
                    so = float(sohleoben_str.replace(",", "."))
                    su = float(sohleunten_str.replace(",", "."))
                    l = float(laenge_str.replace(",", "."))
                    if l > 0:
                        gefaelle = ((so - su) / l) * 1000
                        self.Gefaelle.setText(f"{gefaelle:.1f}")
                    else:
                        self.Gefaelle.setText(get_val("gefaelle"))
                except ValueError:
                    self.Gefaelle.setText(get_val("gefaelle"))
            else:
                self.Gefaelle.setText(get_val("gefaelle"))

        except Exception as e:
            QMessageBox.warning(self, "Datenbankfehler", f"Stammdaten laden fehlgeschlagen: {e}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                if conn is not self.conn:
                    conn.close()
            except Exception:
                pass

    # =========================================================
    # Externes Feature ableiten
    # =========================================================
    def get_external_feature(self):
        """Erzeugt ein Dictionary (Feature-Simulation) mit Fallbacks."""
        key_value = self.external_key_values[0]
        feature_attrs = {}

        if self.external_layer_name == "Haltungen":
            feature_attrs["haltnam"] = key_value
        elif self.external_layer_name == "Schächte":
            feature_attrs["schnam"] = key_value
            feature_attrs["schoben"] = key_value
        elif self.external_layer_name == "GAL":
            feature_attrs["leitnam"] = key_value
            feature_attrs["haltnam"] = key_value

        conn, cursor, param_style = get_db_context(self)

        if conn:
            try:
                if self.external_layer_name == "Haltungen":
                    cursor.execute(
                        f"SELECT schoben FROM haltungen WHERE haltnam = {param_style}",
                        (key_value,)
                    )
                    res = cursor.fetchone()
                    if res:
                        feature_attrs["schoben"] = res[0]

                elif self.external_layer_name == "Schächte":
                    cursor.execute(
                        f"""
                        SELECT haltnam FROM haltungen
                        WHERE schoben = {param_style} OR schunten = {param_style}
                        LIMIT 1
                        """,
                        (key_value, key_value)
                    )
                    res = cursor.fetchone()
                    if res:
                        feature_attrs["haltnam"] = res[0]

                elif self.external_layer_name == "GAL":
                    try:
                        cursor.execute(
                            f"SELECT haltnam FROM anschlussleitungen WHERE leitnam = {param_style}",
                            (key_value,)
                        )
                        res = cursor.fetchone()
                        if res:
                            feature_attrs["haltnam"] = res[0]
                    except Exception:
                        pass

            except Exception as e:
                try:
                    conn.rollback()
                except Exception:
                    pass
                print(f"⚠️ Feature-Erweiterung fehlgeschlagen: {e}")
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    if conn is not self.conn:
                        conn.close()
                except Exception:
                    pass

        print(f"DEBUG get_external_feature: {feature_attrs}")
        return feature_attrs

    # =========================================================
    # Neuer Untersuchungsbericht
    # =========================================================
    def neuer_untersuchungsbericht(self):
        """Legt neuen Untersuchungsbericht mit aktuellem Datum an."""
        from datetime import date
        from ..netzuebersicht.db_backend import get_backend

        heute = date.today().strftime("%Y-%m-%d")

        main_tab_idx = self.tabWidget.currentIndex()
        if main_tab_idx < 0:
            QMessageBox.warning(self, "Fehler", "Wählen Sie einen Tab (Haltungen/Schächte/GAL).")
            return

        tab_names = {0: "Haltungen", 1: "Schächte", 2: "GAL"}
        tab_name = tab_names.get(main_tab_idx, "Haltungen")

        table_map = {
            "Haltungen": "untersuchdat_haltung",
            "Schächte": "untersuchdat_schacht",
            "GAL": "untersuchdat_anschlussleitung",
        }
        db_table = table_map[tab_name]

        column_map = {
            "Haltungen": "untersuchhal",
            "Schächte": "untersuchsch",
            "GAL": "untersuchleit",
        }
        column = column_map[tab_name]

        if getattr(self, "external_mode", False):
            feature = self.get_external_feature()
            key_value = next(
                (feature.get(k) for k in ["haltnam", "schnam", "leitnam"] if feature.get(k)),
                None
            )
        else:
            layer = self.iface.activeLayer()
            if not layer or not layer.selectedFeatureIds():
                QMessageBox.warning(self, "Fehler", "Kein Feature ausgewählt.")
                return
            feature = layer.getFeature(layer.selectedFeatureIds()[0])
            key_value = (
                feature["haltnam"] if tab_name == "Haltungen"
                else feature["schoben"] if tab_name == "Schächte"
                else feature["leitnam"]
            )

        if not key_value:
            QMessageBox.warning(self, "Fehler", "Kein Key-Wert gefunden.")
            return

        owns_connection = False
        conn = getattr(self, "spatialite_conn", None)

        if conn is None:
            backend = get_backend("spatialite")
            conn, _, _ = backend.load_native_connection(parent=self)
            if conn is None:
                QMessageBox.warning(self, "Fehler", "Keine SpatiaLite-Verbindung verfügbar.")
                return
            owns_connection = True

        cursor = conn.cursor()

        try:
            query = f"""
                INSERT INTO {db_table} (untersuchtag, {column})
                VALUES (?, ?)
            """
            cursor.execute(query, (heute, key_value))
            new_pk = cursor.lastrowid

            conn.commit()
            QMessageBox.information(
                self,
                "✓ Erfolg",
                f"Neuer Bericht '{heute}' in {db_table}\n(PK: {new_pk})\n→ Klicken Sie 'Aktualisieren'."
            )

            reply = QMessageBox.question(
                self,
                "Reload?",
                "Tabs neu laden?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.SQLAbfrage()

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            QMessageBox.critical(self, "✗ Fehler", f"INSERT fehlgeschlagen:\n{str(e)}")

        finally:
            try:
                cursor.close()
            except Exception:
                pass

            if owns_connection:
                try:
                    conn.close()
                except Exception:
                    pass

    # =========================================================
    # Tabellenfunktionen
    # =========================================================
    def add_row_to_current_table(self):
        """Add-Button Handler mit Eingabedialog und gruppiertem UI."""
        from datetime import date
        from qgis.PyQt.QtCore import Qt
        from qgis.PyQt.QtWidgets import QTableWidgetItem

        table = find_inner_table_widget(self.tabWidget.currentWidget())
        if not table:
            QMessageBox.warning(self, "Fehler", "Keine aktive Tabelle gefunden.")
            return

        maintabname = self.tabWidget.tabText(self.tabWidget.currentIndex())

        preset = {"untersuchtag": date.today().strftime("%Y-%m-%d")}
        if maintabname in ("Haltungen", "GAL"):
            preset.setdefault("kuerzel", "BCA")

        material = self.Material.text() if hasattr(self, "Material") else ""
        dimension = self.Dimension.text() if hasattr(self, "Dimension") else ""

        dlg = NewUntersuchungDialog(
            maintabname,
            parent=self,
            preset_values=preset,
            material=material,
            dimension=dimension,
        )

        if dlg.exec_() != dlg.Accepted:
            return

        values = dlg.get_values()

        row_count = table.rowCount()
        table.insertRow(row_count)

        pk_item = QTableWidgetItem()
        pk_item.setData(Qt.UserRole, None)
        table.setItem(row_count, 0, pk_item)

        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        dbcols = headers[1:-1]

        for i, col in enumerate(dbcols, start=1):
            val = values.get(col, "")
            item = QTableWidgetItem("" if val is None else str(val))
            table.setItem(row_count, i, item)

        last_col = table.columnCount() - 1
        if table.item(row_count, last_col) is None:
            table.setItem(row_count, last_col, QTableWidgetItem(""))

        table.scrollToBottom()

    def change_row_in_current_table(self):
        from qgis.PyQt.QtCore import Qt
        from .data_queries import save_changes_to_database

        table = find_inner_table_widget(self.tabWidget.currentWidget())
        if not table:
            QMessageBox.warning(self, "Fehler", "Keine aktive Tabelle gefunden.")
            return

        selected_ranges = table.selectedRanges()
        if not selected_ranges:
            QMessageBox.warning(self, "Fehler", "Keine Zeile selektiert.")
            return

        row = selected_ranges[0].topRow()

        maintabname = self.tabWidget.tabText(self.tabWidget.currentIndex())
        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        dbcols = headers[1:-1]

        current_values = {}
        for i, col in enumerate(dbcols, start=1):
            item = table.item(row, i)
            current_values[col] = item.text().strip() if item else ""

        material = self.Material.text() if hasattr(self, "Material") else ""
        dimension = self.Dimension.text() if hasattr(self, "Dimension") else ""

        dlg = NewUntersuchungDialog(
            maintabname,
            parent=self,
            preset_values=current_values,
            material=material,
            dimension=dimension,
        )

        if dlg.exec_() != dlg.Accepted:
            return

        new_values = dlg.get_values()

        reply = QMessageBox.question(
            self,
            "Änderungen übernehmen",
            "Änderungen in Datenbank speichern?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        for i, col in enumerate(dbcols, start=1):
            val = new_values.get(col, "")
            item = QTableWidgetItem("" if val is None else str(val))
            table.setItem(row, i, item)

        pk_item = table.item(row, 0)
        if pk_item is None:
            pk_item = QTableWidgetItem()
            pk_item.setData(Qt.UserRole, None)
            table.setItem(row, 0, pk_item)

        save_changes_to_database(self, table)

    def delete_row_from_current_table(self):
        """Delete-Button Handler."""
        table = find_inner_table_widget(self.tabWidget.currentWidget())
        if table:
            delete_selected_rows(table, self)
        else:
            QMessageBox.warning(self, "Fehler", "Keine aktive Tabelle gefunden.")

    # =========================================================
    # Spaltenlisten
    # =========================================================
    def get_current_columns(self):
        """Spalten pro Tab."""
        maintabname = self.tabWidget.tabText(self.tabWidget.currentIndex())
        return {
            "Haltungen": [
                "station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
                "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"
            ],
            "Schächte": [
                "vertikale_lage", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                "quantnr1", "quantnr2", "pos_von", "pos_bis", "bereich", "zd", "zs", "zb",
                "bandnr", "untersuchtag", "videozaehler", "foto_dateiname"
            ],
            "GAL": [
                "station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
                "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"
            ],
        }[maintabname]

    # =========================================================
    # UI-Aufbau aus date_tabs
    # =========================================================
    def build_ui_from_data(self, date_tabs):
        """Baut das UI aus übergebenen date_tabs."""
        self.tabWidget.clear()
        farben = {0: "red", 1: "yellow", 2: "blue", 3: "lightgreen", 4: "green"}

        columns_ref = {
            "Haltungen": [
                "station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
                "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"
            ],
            "Schächte": [
                "vertikale_lage", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                "quantnr1", "quantnr2", "pos_von", "pos_bis", "bereich", "zd", "zs", "zb",
                "bandnr", "untersuchtag", "videozaehler", "foto_dateiname"
            ],
            "Anschlussleitungen": [
                "station", "kuerzel", "langtext", "kommentar", "charakt1", "charakt2",
                "quantnr1", "quantnr2", "pos_von", "pos_bis", "zd", "zs", "zb",
                "bandnr", "untersuchtag", "videozaehler", "foto_dateiname", "film_dateiname"
            ],
        }

        if "GAL" not in columns_ref and "Anschlussleitungen" in columns_ref:
            columns_ref["GAL"] = columns_ref["Anschlussleitungen"]

        for tab_name, tab_data in date_tabs.items():
            if not tab_data:
                continue

            ref_cols = columns_ref.get(tab_name, columns_ref.get("Haltungen"))
            schacht_tab = QTabWidget()

            first_date = next(iter(tab_data))
            first_rows = tab_data[first_date]
            if not first_rows:
                continue

            first_row_keys = list(first_rows[0].keys())

            col_map = {}
            for ref_col in ref_cols:
                match = next((k for k in first_row_keys if k.lower() == ref_col.lower()), None)
                col_map[ref_col] = match if match else ref_col

            try:
                idx_bandnr = ref_cols.index("bandnr")
            except Exception:
                idx_bandnr = -1
            try:
                idx_videozaehler = ref_cols.index("videozaehler")
            except Exception:
                idx_videozaehler = -1
            try:
                idx_zd = ref_cols.index("zd")
            except Exception:
                idx_zd = -1
            try:
                idx_zs = ref_cols.index("zs")
            except Exception:
                idx_zs = -1
            try:
                idx_zb = ref_cols.index("zb")
            except Exception:
                idx_zb = -1
            try:
                idx_kuerzel = ref_cols.index("kuerzel")
            except Exception:
                idx_kuerzel = -1

            for date, rows in sorted(tab_data.items(), reverse=True):
                if not date:
                    date = "Unbekannt"

                date_table = QTableWidget()
                date_table.setUpdatesEnabled(False)
                date_table.setColumnCount(len(ref_cols) + 2)
                date_table.setHorizontalHeaderLabels(["pk"] + ref_cols + ["Videoname"])
                date_table.setRowCount(len(rows))
                date_table.setColumnHidden(0, True)

                for i, row in enumerate(rows):
                    pk = row.get("pk") or row.get("PK")
                    pk_item = QTableWidgetItem()
                    pk_item.setData(Qt.UserRole, pk)
                    date_table.setItem(i, 0, pk_item)

                    for j, ref_col in enumerate(ref_cols):
                        real_key = col_map.get(ref_col, ref_col)
                        val = row.get(real_key)
                        date_table.setItem(i, j + 1, QTableWidgetItem(str(val) if val is not None else ""))

                    band_key = col_map.get("bandnr", "bandnr")
                    vid_key = col_map.get("videozaehler", "videozaehler")
                    band = row.get(band_key)
                    vid = row.get(vid_key)
                    band_str = str(band).zfill(5) if band is not None else "00000"
                    vid_str = str(vid).zfill(5) if vid is not None else "00000"
                    date_table.setItem(i, len(ref_cols) + 1, QTableWidgetItem(band_str + vid_str))

                for i, row in enumerate(rows):
                    z_werte = []

                    for idx in (idx_zd, idx_zs, idx_zb):
                        if idx >= 0:
                            ref_col = ref_cols[idx]
                            real_key = col_map.get(ref_col, ref_col)
                            val = row.get(real_key)
                            try:
                                val_int = int(val) if val is not None else None
                            except Exception:
                                val_int = None

                            if val_int in farben:
                                z_werte.append(val_int)

                    if idx_kuerzel >= 0:
                        min_z = min(z_werte) if z_werte else None
                        kuerzel_item = date_table.item(i, idx_kuerzel + 1)
                        if min_z is not None and min_z in farben and kuerzel_item:
                            kuerzel_item.setForeground(QColor(farben[min_z]))

                    for idx in (idx_zd, idx_zs, idx_zb):
                        if idx >= 0:
                            ref_col = ref_cols[idx]
                            real_key = col_map.get(ref_col, ref_col)
                            val = row.get(real_key)

                            try:
                                val_int = int(val) if val is not None else None
                            except Exception:
                                val_int = None

                            item = date_table.item(i, idx + 1)
                            if item:
                                if val_int in farben:
                                    item.setForeground(QColor(farben[val_int]))
                                elif val is None:
                                    item.setForeground(QColor("black"))

                date_table.setEditTriggers(QTableWidget.AllEditTriggers)
                date_table.setUpdatesEnabled(True)
                schacht_tab.addTab(date_table, str(date))

            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.addWidget(schacht_tab)
            self.tabWidget.addTab(tab_widget, tab_name)


def show_dialog():
    """Zeigt den Haupt-Dialog (für Plugin-Aufruf)."""
    dialog = databaseviewer(iface.mainWindow())
    dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = databaseviewer()
    dialog.show()
    sys.exit(app.exec_())