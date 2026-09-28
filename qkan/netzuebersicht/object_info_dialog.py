from PyQt6.QtWidgets import QDialog, QFormLayout, QGridLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QScrollArea, QVBoxLayout, QWidget
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtCore import Qt, QLocale
from qgis.gui import QgsMapToolEmitPoint, QgsMapToolIdentify
from qgis.utils import iface
from qgis.core import Qgis, QgsFeatureRequest

from .gis_actions import SelectSchachtTool

class ObjectInfoDialog(QDialog):
    def __init__(self, parent=None, field_data=None, headers=None):
        super().__init__(parent)
        self.setWindowTitle("Objekt bearbeiten")
        self.setMinimumWidth(600)  # Breite für 2 Spalten
        self.resize(700, 500)
        
        main_layout = QHBoxLayout(self)
        
        # ScrollArea für viele Felder
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)  # Automatisch 2 Spalten[web:44]
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignLeft)
        scroll.setWidget(self.form_widget)
        main_layout.addWidget(scroll)
        
        # Buttons unten
        btn_layout = QHBoxLayout()
        self.speichern_btn = QPushButton("💾 Speichern")
        self.abbrechen_btn = QPushButton("❌ Abbrechen")
        btn_layout.addStretch()
        btn_layout.addWidget(self.speichern_btn)
        btn_layout.addWidget(self.abbrechen_btn)
        
        main_container = QWidget()
        container_layout = QVBoxLayout(main_container)
        container_layout.addWidget(scroll)
        container_layout.addLayout(btn_layout)
        main_layout.addWidget(main_container)
        
        self.speichern_btn.clicked.connect(self.accept)
        self.abbrechen_btn.clicked.connect(self.reject)
        
        # Schacht-Übernahme Buttons (nur für Haltungen)
        self.schacht_oben_btn = QPushButton("🔗 Schacht oben übernehmen")
        self.schacht_unten_btn = QPushButton("🔗 Schacht unten übernehmen")
        self.laenge_btn = QPushButton("📏 Länge neu berechnen")
        self.schacht_oben_btn.setEnabled(False)  # Nur bei Haltungen
        self.schacht_unten_btn.setEnabled(False)

        btn_layout.addWidget(self.schacht_oben_btn)
        btn_layout.addWidget(self.schacht_unten_btn)
        btn_layout.addWidget(self.laenge_btn)

        self.schacht_oben_btn.clicked.connect(lambda: self.activate_schacht_tool("oben"))
        self.schacht_unten_btn.clicked.connect(lambda: self.activate_schacht_tool("unten"))
        
        self.current_schacht_modus = None  # "oben" oder "unten"

        if field_data and headers:
            self.load_data(field_data, headers)
    
    def load_data(self, data, headers):
        self.line_edits = {}
        
        for header in headers:
            raw_value = data.get(header)
            display_value = ""
            if raw_value is not None and str(raw_value).upper() != "NULL":
                display_value = str(raw_value)
            
            lbl = QLabel(str(header))
            edit = QLineEdit(display_value)
            self.line_edits[header] = edit
            
            # ✅ NUMERISCHE FELDER: Validator + Placeholder!
            header_lower = header.lower()
            if any(kw in header_lower for kw in ['hoehe', 'laenge', 'xsch', 'ysch', 'durchm']):
                # Double
                validator = QDoubleValidator()
                validator.setLocale(QLocale(QLocale.English))  # Punkt!
                edit.setValidator(validator)
                edit.setPlaceholderText(f"z.B. {header} = 1.25")
            elif any(kw in header_lower for kw in ['jahr', 'id']):
                # Integer
                validator = QIntValidator(0, 9999)
                edit.setValidator(validator)
                edit.setPlaceholderText(f"z.B. {header} = 2024")
            else:
                # Text: Kein Validator
                edit.setPlaceholderText(f"Freitext für {header}")
            
            self.form_layout.addRow(lbl, edit)
        
        # Spacer
        spacer_label = QLabel("")
        spacer_label.setMinimumHeight(20)
        self.form_layout.addRow(spacer_label)

  
    def get_data(self):
        return {header: edit.text() for header, edit in self.line_edits.items()}
    

    # In ObjectInfoDialog Klasse:

    def activate_schacht_tool(self, modus):
        """Startet Schacht-Auswahl Tool"""
        self.current_schacht_modus = modus
        
        # ✅ Tool als Instanzvariable speichern (verhindert Garbage Collection!)
        canvas = iface.mapCanvas()
        self.schacht_tool = SelectSchachtTool(canvas)
        self.schacht_tool.schachtSelected.connect(self.on_schacht_selected)
        
        # Tool aktivieren
        canvas.setMapTool(self.schacht_tool)
        
        iface.messageBar().pushMessage("Schacht auswählen", f"Klicke auf {modus} Schacht", Qgis.Info, 10)

    def on_schacht_selected(self, attrs):
        """Übernimmt Schacht-Daten in Felder"""
        if not self.current_schacht_modus: return
        
        # Felder füllen
        if self.current_schacht_modus == "oben":
            if "schoben" in self.line_edits: self.line_edits["schoben"].setText(attrs.get("schnam", ""))
            if "sohleoben" in self.line_edits: self.line_edits["sohleoben"].setText(str(attrs.get("sohlhoehe", "")))
            if "xschob" in self.line_edits: self.line_edits["xschob"].setText(str(attrs.get("xsch", "")))
            if "yschob" in self.line_edits: self.line_edits["yschob"].setText(str(attrs.get("ysch", "")))
        else:  # unten
            if "schunten" in self.line_edits: self.line_edits["schunten"].setText(attrs.get("schnam", ""))
            if "sohleunten" in self.line_edits: self.line_edits["sohleunten"].setText(str(attrs.get("sohlhoehe", "")))
            if "xschun" in self.line_edits: self.line_edits["xschun"].setText(str(attrs.get("xsch", "")))
            if "yschun" in self.line_edits: self.line_edits["yschun"].setText(str(attrs.get("ysch", "")))
        
        # UI in den Vordergrund holen
        self.raise_()
        self.activateWindow()
        
        iface.messageBar().pushMessage("✅", f"{self.current_schacht_modus} Schacht geladen!", Qgis.Success, 3)
        
        # Tool deaktivieren & aufräumen
        iface.mapCanvas().unsetMapTool(self.schacht_tool)
        self.schacht_tool = None # Referenz löschen
        self.current_schacht_modus = None



