"""
Ergänzung für ui_handlers.py - Vollständige Implementierungen der Handler-Methoden
"""

# =========================================================
# Importe
# =========================================================

import os
import json
import subprocess

from PyQt5.QtWidgets import (
    QMessageBox,
    QTabWidget,
    QListWidget,
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
)
from qgis.core import QgsProject, QgsPrintLayout, QgsLayoutItemMap
from qgis.gui import *
from qgis.utils import iface

from qkan.tools.vlc_error import VlcLoadError
from qkan.utils import get_logger

from .data_queries import find_inner_table_widget
from .media_player import MediaPlayer
from .document_management import DocumentManagementWindow
from .visualization import CanalVisualizationWindow
from .sanierung_tool import Sanierungstool

LOGGER = get_logger(__name__)


# =========================================================
# Hilfsfunktion: lokaler json-Ordner
# =========================================================

def _json_dir():
    """Gibt den lokalen json-Unterordner relativ zu dieser Datei zurück."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "json")


# =========================================================
# Video-Start-Handler
# =========================================================

def start_video_clicked(self):
    current_tab_widget = self.tabWidget.currentWidget()
    inner_tab_widget = current_tab_widget.findChild(QTabWidget)
    if not inner_tab_widget:
        print("Kein inneres Tab-Widget gefunden.")
        return

    selected_inner_tab = inner_tab_widget.currentWidget()
    if not selected_inner_tab:
        print("Kein innerer Tab ausgewählt.")
        return

    table_widget = find_inner_table_widget(selected_inner_tab)
    if not table_widget:
        print("Kein QTableWidget im ausgewählten inneren Tab gefunden.")
        return

    # Spaltenindex bestimmen
    column_count = table_widget.columnCount()
    target_column = -1

    # 1. Versuch: Spalte "film_dateiname" finden
    for col in range(column_count):
        header = table_widget.horizontalHeaderItem(col)
        if header and header.text().strip() == "film_dateiname":
            target_column = col
            break

    # 2. Fallback: Vorletzte Spalte, wenn "film_dateiname" nicht existiert
    if target_column == -1:
        if column_count >= 2:
            target_column = column_count - 2
            print("Verwende vorletzte Spalte als Fallback.")
        else:
            print("Nicht genug Spalten vorhanden.")
            return

    # Wert aus der ersten Zeile der Zielspalte holen
    first_row_item = table_widget.item(0, target_column)
    if not first_row_item or not first_row_item.text():
        print("Die Zelle ist leer.")
        return

    video_path = first_row_item.text()
    print("Verwendeter Pfad:", video_path)

    # QLineEdit erstellen und an MediaPlayer übergeben
    film_dateiname = QLineEdit()
    film_dateiname.setText(video_path)

    try:
        media_player = MediaPlayer(film_dateiname=film_dateiname)
        media_player.show()
        media_player.exec()
    except VlcLoadError:
        LOGGER.error_user("Could not open/find VLC. Is it installed?")




# =========================================================
# Sanierungstool öffnen
# =========================================================

def open_sanierungstool(self):
    """Öffnet das Sanierungstool mit Haltungs-, Schacht- und GAL-Daten."""
    json_base = _json_dir()
    json_file_path_haltungen = os.path.join(json_base, "selected_items_haltungen.json")
    json_file_path_schaechte = os.path.join(json_base, "selected_items_schaechte.json")
    json_file_path_gal = os.path.join(json_base, "selected_items_gal.json")

    # Header-Listen laden
    with open(json_file_path_haltungen, "r", encoding="utf-8") as file:
        headers_haltungen = json.load(file)

    with open(json_file_path_schaechte, "r", encoding="utf-8") as file:
        headers_schacht = json.load(file)

    with open(json_file_path_gal, "r", encoding="utf-8") as file:
        headers_gal = json.load(file)

    # Haltungsname aus QLineEdit
    untersuchhal = self.Haltungsname.text().strip()

    # Haupttab und innere Tabs sammeln
    tab_dict = {}
    for i in range(self.tabWidget.count()):
        current_tab_widget = self.tabWidget.widget(i)
        main_tab_name = self.tabWidget.tabText(i)

        inner_tab_widget = current_tab_widget.findChild(QTabWidget)
        if inner_tab_widget:
            inner_tabs = []
            for j in range(inner_tab_widget.count()):
                inner_tab_name = inner_tab_widget.tabText(j)
                inner_tabs.append(inner_tab_name)
            tab_dict[main_tab_name] = inner_tabs

    # Tab-Auswahl fürs Haltungs-Sanierungstool
    dialog = TabSelectionDialog(tab_dict)
    if dialog.exec() == QDialog.Accepted and dialog.selected_tab:
        main_tab_name, inner_tab_name = dialog.selected_tab.split(" -> ")
        untersuchtag = inner_tab_name

        # Haupttab und inneren Tab finden
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == main_tab_name:
                current_tab_widget = self.tabWidget.widget(i)
                inner_tab_widget = current_tab_widget.findChild(QTabWidget)

                if inner_tab_widget:
                    for j in range(inner_tab_widget.count()):
                        if inner_tab_widget.tabText(j) == inner_tab_name:
                            selected_inner_tab = inner_tab_widget.widget(j)

                            table_widget = find_inner_table_widget(selected_inner_tab)
                            if table_widget:
                                row_count = table_widget.rowCount()
                                column_count = table_widget.columnCount()
                                data = []

                                for i_row in range(row_count):
                                    row = []
                                    for j_col in range(column_count):
                                        header_item = table_widget.horizontalHeaderItem(
                                            j_col
                                        )
                                        if not header_item:
                                            continue

                                        header_text = header_item.text()

                                        if (
                                            main_tab_name == "Haltungen"
                                            and header_text in headers_haltungen
                                        ):
                                            item = table_widget.item(i_row, j_col)
                                            row.append(item.text() if item else "")
                                        elif (
                                            main_tab_name == "Schächte"
                                            and header_text in headers_schacht
                                        ):
                                            item = table_widget.item(i_row, j_col)
                                            row.append(item.text() if item else "")
                                        elif (
                                            main_tab_name == "GAL"
                                            and header_text in headers_gal
                                        ):
                                            item = table_widget.item(i_row, j_col)
                                            row.append(item.text() if item else "")
                                    data.append(row)

                                # Schachtuntersuchung optional
                                confirm_schacht = QMessageBox.question(
                                    self,
                                    "Schachtuntersuchung",
                                    "Möchten Sie auch eine Schachtuntersuchung auswählen?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No,
                                )

                                data_schacht = []
                                untersuchtag_schacht = ""

                                if confirm_schacht == QMessageBox.Yes:
                                    dialog_schacht = TabSelectionDialog(tab_dict)
                                    if (
                                        dialog_schacht.exec() == QDialog.Accepted
                                        and dialog_schacht.selected_tab
                                    ):
                                        (
                                            main_tab_name_schacht,
                                            inner_tab_name_schacht,
                                        ) = dialog_schacht.selected_tab.split(" -> ")
                                        untersuchtag_schacht = inner_tab_name_schacht

                                        for i2 in range(self.tabWidget.count()):
                                            if (
                                                self.tabWidget.tabText(i2)
                                                == main_tab_name_schacht
                                            ):
                                                current_tab_widget_schacht = (
                                                    self.tabWidget.widget(i2)
                                                )
                                                inner_tab_widget_schacht = (
                                                    current_tab_widget_schacht.findChild(
                                                        QTabWidget
                                                    )
                                                )

                                                if inner_tab_widget_schacht:
                                                    for j2 in range(
                                                        inner_tab_widget_schacht.count()
                                                    ):
                                                        if inner_tab_widget_schacht.tabText(
                                                            j2
                                                        ) == inner_tab_name_schacht:
                                                            selected_inner_tab_schacht = (
                                                                inner_tab_widget_schacht.widget(
                                                                    j2
                                                                )
                                                            )

                                                            table_widget_schacht = (
                                                                find_inner_table_widget(
                                                                    selected_inner_tab_schacht
                                                                )
                                                            )

                                                            if table_widget_schacht:
                                                                row_count_schacht = (
                                                                    table_widget_schacht.rowCount()
                                                                )
                                                                column_count_schacht = (
                                                                    table_widget_schacht.columnCount()
                                                                )
                                                                print(
                                                                    f"Spaltenanzahl (Schacht): {column_count_schacht}"
                                                                )

                                                                data_schacht = []
                                                                for i3 in range(
                                                                    row_count_schacht
                                                                ):
                                                                    row_s = []
                                                                    for j3 in range(
                                                                        column_count_schacht
                                                                    ):
                                                                        header_item = table_widget_schacht.horizontalHeaderItem(
                                                                            j3
                                                                        )
                                                                        if not header_item:
                                                                            continue
                                                                        header_text = (
                                                                            header_item.text()
                                                                        )

                                                                        if (
                                                                            header_text
                                                                            in headers_schacht
                                                                        ):
                                                                            item = table_widget_schacht.item(
                                                                                i3, j3
                                                                            )
                                                                            row_s.append(
                                                                                item.text()
                                                                                if item
                                                                                else ""
                                                                            )
                                                                    data_schacht.append(
                                                                        row_s
                                                                    )

                                sanierung_dialog = Sanierungstool(
                                    data=data,
                                    data_schacht=data_schacht,
                                    headers_haltungen=headers_haltungen,
                                    headers_schacht=headers_schacht,
                                    untersuchhal=untersuchhal,
                                    untersuchtag=untersuchtag,
                                    untersuchtag_schacht=untersuchtag_schacht,
                                    headers_gal=headers_gal,
                                    data_gal=None,
                                    parent=self,
                                )
                                sanierung_dialog.setModal(False)
                                sanierung_dialog.show()
                                sanierung_dialog.raise_()
                                sanierung_dialog.activateWindow()
                                return
    else:
        print("Keine Auswahl getroffen.")


# =========================================================
# Bauwerkszeichnung öffnen
# =========================================================

def Bauwerkszeichnung_oeffnen(self):
    """Öffnet die Bauwerkszeichnung (PDF) anhand von Schachtname und Konfiguration."""
    json_base = _json_dir()
    bauwerkszeichnung_file_path = os.path.join(
        json_base, "bauwerkszeichnungpfad.json"
    )

    try:
        with open(bauwerkszeichnung_file_path, "r", encoding="utf-8") as file:
            bauwerkszeichnung_data = json.load(file)

        if "bauwerkszeichnungpfad" in bauwerkszeichnung_data:
            pdf_directory = bauwerkszeichnung_data["bauwerkszeichnungpfad"]
        else:
            pdf_directory = "C:/Standard/Pfad/Zu/Deinem/PDF-Verzeichnis"

        pdf_file_name = self.Schacht_oben.text().strip()
        print(f"Suche PDF: {pdf_file_name}.pdf")

        pdf_file_path = os.path.join(pdf_directory, pdf_file_name + ".pdf")

        if os.path.exists(pdf_file_path):
            try:
                subprocess.Popen(["start", "", pdf_file_path], shell=True)
                print(f"✓ PDF geöffnet: {pdf_file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "PDF-Fehler",
                    f"PDF konnte nicht geöffnet werden:\n{e}",
                )
                print("Error:", e)
        else:
            QMessageBox.warning(
                self,
                "PDF nicht gefunden",
                f"Bauwerkszeichnung nicht gefunden:\n\n"
                f"<b>{pdf_file_name}.pdf</b>\n\n"
                f"Pfad: {pdf_file_path}\n\n"
                f"Prüfen Sie:\n"
                f"• JSON-Pfad in json/bauwerkszeichnungpfad.json\n"
                f"• PDF-Datei im Verzeichnis",
            )
            print(f"✗ PDF nicht gefunden: {pdf_file_path}")

    except FileNotFoundError:
        QMessageBox.critical(
            self,
            "JSON-Fehler",
            f"Settings-Datei fehlt:\n{bauwerkszeichnung_file_path}",
        )
    except json.JSONDecodeError as e:
        QMessageBox.critical(
            self,
            "JSON-Fehler",
            f"JSON-Datei fehlerhaft:\n{bauwerkszeichnung_file_path}\n\n{e}",
        )
    except Exception as e:
        QMessageBox.critical(self, "Allgemeiner Fehler", f"Unerwarteter Fehler:\n{e}")


# =========================================================
# Panoramo öffnen
# =========================================================

def Panoramo_oeffnen(self):
    """Öffnet eine Panoramo-IPF-Datei im externen PanoramoViewer (Haltungen)."""
    json_base = _json_dir()
    panoramo_file_path = os.path.join(json_base, "panoramopfad.json")

    with open(panoramo_file_path, "r", encoding="utf-8") as file:
        panoramo_data = json.load(file)
        print(panoramo_data)

    if "panoramopfad" in panoramo_data:
        ipf_directory = panoramo_data["panoramopfad"]
    else:
        ipf_directory = "C:/Standard/Pfad/Zu/Deinem/PDF-Verzeichnis"

    ipf_file_name = self.Haltungsname.text()
    ipf_file_path = os.path.join(ipf_directory, ipf_file_name + ".ipf")
    print(ipf_file_path)

    path_option_1 = "C:/IBAK/PanoPlayer/PanoramoViewer.exe"
    path_option_2 = "C:/IBAK/PanoPlayer 4K/PanoramoViewer.exe"

    if os.path.exists(path_option_1):
        viewer_path = path_option_1
    elif os.path.exists(path_option_2):
        viewer_path = path_option_2
    else:
        print("Keiner der Pfade wurde gefunden.")
        return

    cmd_command = [viewer_path, ipf_file_path]

    try:
        subprocess.Popen(cmd_command)
    except Exception as e:
        print("Error:", e)


# =========================================================
# Panoramo-Schachtinspektion öffnen
# =========================================================

def PanoramoSI_oeffnen(self):
    """Öffnet eine Panoramo-IPF-Datei im externen Viewer (Schachtinspektion)."""
    json_base = _json_dir()
    panoramoSI_file_path = os.path.join(json_base, "panoramoSIpfad.json")

    with open(panoramoSI_file_path, "r", encoding="utf-8") as file:
        panoramoSI_data = json.load(file)
        print(panoramoSI_data)

    if "panoramoSIpfad" in panoramoSI_data:
        ipf_directory = panoramoSI_data["panoramoSIpfad"]
    else:
        ipf_directory = "C:/Standard/Pfad/Zu/Deinem/PDF-Verzeichnis"

    ipf_file_name = self.Schacht_oben.text()
    ipf_file_path = os.path.join(ipf_directory, ipf_file_name + ".ipf")
    print(ipf_file_path)

    path_option_1 = "C:/IBAK/PanoPlayer/PanoramoViewer.exe"
    path_option_2 = "C:/IBAK/PanoPlayer 4K/PanoramoViewer.exe"

    if os.path.exists(path_option_1):
        viewer_path = path_option_1
    elif os.path.exists(path_option_2):
        viewer_path = path_option_2
    else:
        print("Keiner der Pfade wurde gefunden.")
        return

    cmd_command = [viewer_path, ipf_file_path]

    try:
        subprocess.Popen(cmd_command)
    except Exception as e:
        print("Error:", e)


# =========================================================
# Layout / Plot aus ausgewähltem Feature
# =========================================================

def display_selected_feature(self):
    """Zeigt das ausgewählte Feature in einem A3-Layout und öffnet den Layout-Designer."""
    project = QgsProject.instance()

    layer = iface.activeLayer()
    if layer is None:
        print("Kein aktiver Layer ausgewählt.")
        return

    selected_features = layer.selectedFeatures()
    if len(selected_features) == 0:
        print("Kein Feature ausgewählt.")
        return
    feature = selected_features[0]

    feature_extent = feature.geometry().boundingBox()
    expansion_factor = 0.2
    expanded_extent = feature_extent.buffered(feature_extent.width() * expansion_factor)

    layout_width_mm = 297
    layout_height_mm = 420

    layout_manager = project.layoutManager()
    layout_name = layer.name()
    layout = layout_manager.layoutByName(layout_name)
    if layout is None:
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layout_name)
        layout_manager.addLayout(layout)

    map_item = QgsLayoutItemMap(layout)

    x_coord = 21
    y_coord = 5
    width = 214
    height = 287
    map_item.setRect(x_coord, y_coord, width, height)

    map_item.setExtent(expanded_extent)

    layout.addItem(map_item)
    layout.refresh()
    iface.openLayoutDesigner(layout)

    def onLayoutRemoved(layoutId):
        if layoutId == layout.id():
            layout_manager.layoutRemoved.disconnect(onLayoutRemoved)
            layout_manager.removeLayout(layout)

    layout_manager.layoutRemoved.connect(onLayoutRemoved)


# =========================================================
# Dokumentenmanagement öffnen
# =========================================================

def opendocumentmanagement(self):
    """Öffnet das Dokumentenmanagement-Fenster für die aktuelle Haltung."""
    haltungsname = self.Haltungsname.text()
    streetname = self.Strassenname.text()
    strakatid = self.StrakatID.text()

    self.documentmanagementwindow = DocumentManagementWindow(
        haltungsname, streetname, strakatid, self
    )
    self.documentmanagementwindow.show()


# =========================================================
# Kanal-Visualisierung
# =========================================================

def showVisualization(self):
    """Zeigt eine Kanal-Visualisierung basierend auf den Tabellen- und UI-Werten."""
    currenttabwidget = self.tabWidget.currentWidget()
    innertabwidget = currenttabwidget.findChild(QTabWidget)

    ui_values = {
        "Haltungsname": self.Haltungsname.text(),
        "Strassenname": self.Strassenname.text(),
        "Schacht_oben": self.Schacht_oben.text(),
        "Schacht_unten": self.Schacht_unten.text(),
        "Material": self.Material.text(),
        "Laenge": self.Laenge.text(),
        "Gefaelle": self.Gefaelle.text(),
        "Baujahr": self.Baujahr.text(),
        "Dimension": self.Dimension.text(),
    }

    if not innertabwidget:
        print("Kein QTabWidget im aktuellen Tab gefunden.")
        return

    selectedinnertab = innertabwidget.currentWidget()
    if not selectedinnertab:
        print("Kein ausgewählter innerer Tab gefunden.")
        return

    tablewidget = find_inner_table_widget(selectedinnertab)
    if not tablewidget:
        print("Kein QTableWidget im ausgewählten inneren Tab gefunden.")
        return

    rowcount = tablewidget.rowCount()
    columncount = tablewidget.columnCount()
    selecteddata = []

    for row in range(rowcount):
        rowdata = []
        for column in range(columncount):
            item = tablewidget.item(row, column)
            rowdata.append(item.text() if item else "")
        selecteddata.append(rowdata)

    if not selecteddata:
        print("Keine Daten im QTableWidget vorhanden.")
        return

    self.visualizationwindow = CanalVisualizationWindow(
        self.Laenge.text(),
        selecteddata,
        tablewidget,
        ui_values=ui_values,
    )
    self.visualizationwindow.show()


# =========================================================
# Tab-Auswahldialog
# =========================================================

class TabSelectionDialog(QDialog):
    """Dialog zur Auswahl eines (Haupttab -> Innentab)-Paares."""

    def __init__(self, tab_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Befahrung auswählen")

        self.selected_tab = None

        layout = QVBoxLayout(self)

        # Liste der Tabs erstellen
        self.list_widget = QListWidget(self)
        for main_tab_name, inner_tabs in tab_dict.items():
            for inner_tab_name in inner_tabs:
                self.list_widget.addItem(f"{main_tab_name} -> {inner_tab_name}")
        layout.addWidget(self.list_widget)

        # OK und Abbrechen-Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            self.selected_tab = selected_item.text()
        super().accept()
