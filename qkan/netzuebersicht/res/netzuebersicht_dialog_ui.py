# netzuebersicht/netzuebersicht_dialog_ui.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,  # ← WIEDER QDialog für Window-Flags!
    QVBoxLayout, QHBoxLayout, QTabWidget, QTableView, QPushButton,
    QLineEdit, QLabel, QFrame, QComboBox, QGroupBox, QSplitter,
    QHeaderView, QSizePolicy, QWidget, QLayout
)


class NetzuebersichtUI(QWidget):  # ← QDialog für Min/Max/Schließen!
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):

        # 🎯 HAUPT-LAYOUT: feste Abstände, aber resizable
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)  # 🎯 Fix Rand
        main_layout.setSpacing(12)  # 🎯 Fix Abstände zwischen Widgets

        # 1. SUCHZEILE (fest)
        search_frame = QFrame()
        search_frame.setFixedHeight(36)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(8, 6, 8, 6)
        search_layout.setSpacing(12)

        # Suche links
        lbl_search = QLabel("Suche:")
        self.Search_LineEdit = QLineEdit()
        self.Search_LineEdit.setMaximumWidth(220)
        self.Search_LineEdit.setMinimumHeight(24)
        self.Search_LineEdit.setPlaceholderText("Filtertext…")
        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.Search_LineEdit)
        search_layout.addStretch()

        # Filter rechts
        lbl_filter = QLabel("Filtern nach:")
        self.comboBox_Spalten = QComboBox()
        self.comboBox_Spalten.setMinimumWidth(160)
        self.comboBox_Spalten.setMinimumHeight(24)
        self.comboBox_Spalten.setPlaceholderText("Spalte wählen")
        search_layout.addStretch()
        search_layout.addWidget(lbl_filter)
        search_layout.addWidget(self.comboBox_Spalten)

        main_layout.addWidget(search_frame)

        # 2. TAB + IMMER-BUTTONS (expanding Tabs)
        tab_section = QWidget()
        tab_section_layout = QVBoxLayout(tab_section)
        tab_section_layout.setContentsMargins(0, 0, 0, 0)
        tab_section_layout.setSpacing(12)  # 🎯 Fix zwischen Tab + Buttons

        # TabWidget (expanding!)
        self.tab_Overview = QTabWidget()
        self.tab_Overview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._create_tab_with_tableview("Haltungen", "tableView_Haltungen")
        self._create_tab_with_tableview("Schächte", "tableView_Schaechte")
        self._create_tab_with_tableview("GAL", "tableView_GAL")
        self._create_tab_with_tableview("Sinkkästen", "tableView_Sinkkaesten")
        self._create_tab_with_tableview("Sonderbauwerke", "tableView_Sonderbauwerke")

        tab_section_layout.addWidget(self.tab_Overview)

        # Immer-Buttons (fest)
        always_buttons_frame = QFrame()
        always_buttons_frame.setFixedHeight(42)
        always_buttons_layout = QHBoxLayout(always_buttons_frame)
        always_buttons_layout.setContentsMargins(8, 6, 8, 6)
        always_buttons_layout.setSpacing(12)

        self.Show_Object = QPushButton("Objekt anzeigen")
        self.Show_Object.setMaximumWidth(180)
        always_buttons_layout.addWidget(self.Show_Object)

        self.excel_import = QPushButton("Excel-Import")
        self.excel_import.setMaximumWidth(180)
        always_buttons_layout.addWidget(self.excel_import)

        self.layer_importieren_sinkkaesten = QPushButton("Layer-Import")
        self.layer_importieren_sinkkaesten.setMaximumWidth(180)
        always_buttons_layout.addWidget(self.layer_importieren_sinkkaesten)

        self.Untersuchungsdaten_exportieren = QPushButton("Export Untersuchungen")
        self.Untersuchungsdaten_exportieren.setMaximumWidth(180)
        always_buttons_layout.addWidget(self.Untersuchungsdaten_exportieren)

        always_buttons_layout.addStretch()
        tab_section_layout.addWidget(always_buttons_frame)

        main_layout.addWidget(tab_section)  # ← Expanding!

        # 3. SPLITTER für tab-spezifische Buttons
        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizes([1100, 300])
        splitter.addWidget(tab_section)

        # 🎯 TAB-SPEZIFISCHE BUTTONS: obenbündig + fester Abstand
        specific_buttons_frame = QGroupBox("Tab-spezifische Aktionen")
        specific_buttons_frame.setFixedWidth(280)
        specific_buttons_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        specific_buttons_layout = QVBoxLayout(specific_buttons_frame)
        specific_buttons_layout.setSpacing(6)        # 🎯 Fester 6px zwischen Buttons
        specific_buttons_layout.setContentsMargins(12, 8, 12, 12)  # 🎯 Oben 8px (bündig!)

        self.open_Kostenermittlung = QPushButton("Kostenermittlung")
        self.open_Kostenermittlung.setMaximumWidth(220)
        specific_buttons_layout.addWidget(self.open_Kostenermittlung)

        self.Show_Object_Untersuchung = QPushButton("Untersuchung anzeigen")
        self.Show_Object_Untersuchung.setMaximumWidth(220)
        specific_buttons_layout.addWidget(self.Show_Object_Untersuchung)

        self.PanoramoPruefer = QPushButton("Panoramo prüfen")
        self.PanoramoPruefer.setMaximumWidth(220)
        specific_buttons_layout.addWidget(self.PanoramoPruefer)

        self.Sonderbauwerke = QPushButton("Sonderbauwerke ▶")
        self.Sonderbauwerke.setMaximumWidth(220)
        specific_buttons_layout.addWidget(self.Sonderbauwerke)

        splitter.addWidget(specific_buttons_frame)
        main_layout.addWidget(splitter)


        # # 4. Status (fest)
        # status_frame = QFrame()
        # status_frame.setFixedHeight(28)
        # status_layout = QHBoxLayout(status_frame)
        # status_layout.addStretch()
        # status_layout.addWidget(QLabel("Netzübersicht bereit."))
        # main_layout.addWidget(status_frame)



    def _create_tab_with_tableview(self, tab_name: str, tableview_attr: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        table = QTableView()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSortingEnabled(True)
        
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setMinimumSectionSize(50)
        header.setDefaultSectionSize(100)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        table.verticalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(table)
        self.tab_Overview.addTab(widget, tab_name)
        setattr(self, tableview_attr, table)
