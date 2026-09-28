"""
visualization.py - Kanalvisualisierungs-Klasse für QGIS-Plugin Datenbankviewer
Enthält CanalVisualizationWindow mit Grafik-Rendering.
"""

from PyQt6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton, QApplication, QGraphicsSimpleTextItem, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QRectF, QUrl
from PyQt6.QtGui import QTransform, QPen, QBrush, QColor, QDesktopServices, QPainter, QTextDocument, QFont, QPixmap, QPdfWriter, QImage
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsLineItem, QTableWidgetItem
from PyQt6 import QtGui
from PyQt6.QtPrintSupport import QPrinter
import sys
import os
import subprocess
from collections import defaultdict


class CanalVisualizationWindow(QMainWindow):
    """Fenster zur Visualisierung von Kanalbefahrungen als Grafik."""
    
    def __init__(self, laenge, selecteddata, tablewidget, ui_values=None):
        super().__init__()
        self.setWindowTitle("Haltungsgrafik")
        self.setGeometry(100, 100, 800, 600)
        # self.setStyleSheet('background-color: white')
        # QGIS-Theme übernehmen, ABER Grafik weiß
        app = QApplication.instance()
        if app:
            qgis_stylesheet = app.styleSheet()
            self.setStyleSheet(qgis_stylesheet + """
                QGraphicsView {
                    background-color: white !important;
                    border: 1px solid #ccc;
                }
            """)
        self.zoom_factor = 1.0
        self.Laenge = float(laenge)
        self.selected_data = selecteddata
        self.tableWidget = tablewidget
        # UI-Werte übergeben (aus databaseviewer)
        self.ui_values = ui_values or {}
        self.initUI()
        # GraphicsView konfigurieren
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.NoAnchor)
        
        # Scroll-Handler
        self.setup_scroll_view()

    def initUI(self):
        # === CENTRAL WIDGET MIT INFO-HEADER + GRAFIK ===
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # === 1. INFO-HEADER ===
        self.info_frame = QLabel()
        self.info_frame.setObjectName("info_frame")
        self.info_frame.setWordWrap(True)
        self.info_frame.setMinimumHeight(85)
        
        # Infos setzen
        info_text = self._format_info_header()
        self.info_frame.setText(info_text)
        
        # Info-Styling (QGIS-kompatibel)
        self.info_frame.setStyleSheet("""
            QLabel#info_frame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e8f4fd, stop:1 #b8dff9);
                border: 1px solid #7abaff;
                border-radius: 8px;
                padding: 15px;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        main_layout.addWidget(self.info_frame)
        
        # === 2. GRAFIK-VIEW ===
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        
        # Scrollbars immer sichtbar
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Zoom-Setup (QGIS-Style)
        self.zoom_factor = 1.0
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Weißer Hintergrund für Grafik
        self.view.setStyleSheet("""
            QGraphicsView {
                background-color: #ffffff !important;
                border: 2px solid #cccccc !important;
                border-radius: 6px;
            }
        """)
        
        main_layout.addWidget(self.view, 1)  # Stretches
        
        # === 3. BUTTONS ===
        button_layout = QHBoxLayout()
        
        self.draw_button = QPushButton("🖌️ Zeichnen")
        self.draw_button.clicked.connect(self.drawDamages)
        self.draw_button.setToolTip("Grafik neu zeichnen")

        self.pdf_button = QPushButton("📄 PDF exportieren")  # ← NEU!
        self.pdf_button.clicked.connect(self.export_to_pdf)
        
        self.zoom_in_button = QPushButton("🔍 +")
        self.zoom_in_button.clicked.connect(self.zoomIn)
        self.zoom_in_button.setFixedWidth(60)
        self.zoom_in_button.setToolTip("Hereinzoomen")
        
        self.zoom_out_button = QPushButton("🔍 -")
        self.zoom_out_button.clicked.connect(self.zoomOut)
        self.zoom_out_button.setFixedWidth(60)
        self.zoom_out_button.setToolTip("Herauszoomen")
        
        button_layout.addWidget(self.draw_button)
        button_layout.addWidget(self.pdf_button)  # ← NEU!
        button_layout.addStretch(1)
        button_layout.addWidget(self.zoom_in_button)
        button_layout.addWidget(self.zoom_out_button)
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        main_layout.addWidget(button_widget)
        
        # === FERTIG ===
        self.setCentralWidget(central_widget)
        self.view.setScene(self.scene)

        # === Export-Funktionen ===

    def export_to_pdf(self):
        """Exportiert mit QPrinter (QGIS-kompatibel)"""
        from PyQt6.QtPrintSupport import QPrinter
        from PyQt6.QtGui import QPainter, QImage
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtCore import Qt
        import os
        
        include_images = self.ask_include_images()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF speichern unter",
            f"Haltungsgrafik_{self.ui_values.get('Haltungsname', 'export')}.pdf",
            "PDF-Dateien (*.pdf)"
        )
        
        if not file_path:
            return
        
        # === QPrinter mit komprimierten Einstellungen ===
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        printer.setPageSize(QPrinter.A4)  # ✅ Das funktioniert!
        printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
        
        painter = QPainter()
        painter.begin(printer)
        
        try:
            self._draw_header_and_graphic(painter, printer)
            
            if include_images:
                images_data = self.get_damage_images_data()
                if images_data:
                    printer.newPage()
                    self._draw_images_pages(painter, printer, images_data)
            
            painter.end()
            
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            msg = f"✓ PDF gespeichert: {os.path.basename(file_path)}\n\n"
            msg += f"Größe: {file_size_mb:.1f} MB"
            if include_images and images_data:
                msg += f"\nBilder: {len(images_data)}"
            QMessageBox.information(self, "Erfolg", msg)
            
        except Exception as e:
            QMessageBox.critical(self, "✗ Fehler", str(e))
            if painter.isActive():
                painter.end()

    def _format_info_header_pdf(self):
        """PDF-Export: 3er-Pakete nebeneinander – GROSSE Schrift"""
        values = getattr(self, 'ui_values', {})
        
        def make_cell(label, value):
            return f'''<td style="
                padding:24px 48px; 
                vertical-align:top; 
                font-size:136px; 
                color:#000000;
                line-height:1.5;
            "><b>{label}:</b> {value}</td>'''
        
        row1 = (make_cell("Haltung", values.get('Haltungsname', '—')) +
                make_cell("Straße", values.get('Strassenname', '—')) +
                make_cell("Länge", f"{values.get('Laenge', '—')} m"))
        
        row2 = (make_cell("Schacht oben", values.get('Schacht_oben', '—')) +
                make_cell("Material", values.get('Material', '—')) +
                make_cell("Baujahr", values.get('Baujahr', '—')))
        
        row3 = (make_cell("Schacht unten", values.get('Schacht_unten', '—')) + 
                make_cell("Gefälle", f"{values.get('Gefaelle', '—')} ‰") +
                make_cell("Dimension", values.get('Dimension', '—')))
        
        html_table = f"""
        <table style="width:100%; border-collapse:collapse; font-family:Arial; font-size:12px;">
            <tr>{row1}</tr>
            <tr>{row2}</tr>
            <tr>{row3}</tr>
        </table>
        """
        
        return html_table

    def _format_info_header(self):
        """3er-Pakete nebeneinander – Titel + Wert HORIZONTAL"""
        values = getattr(self, 'ui_values', {})
        
        def make_cell(label, value):
            return f'<td style="padding:8px; vertical-align:top;"><b>{label}:</b> {value}</td>'
        
        # 3er-Gruppen (horizontal!)
        row1 = (make_cell("Haltung", values.get('Haltungsname', '—')) +
                make_cell("Straße", values.get('Strassenname', '—')) +
                make_cell("Länge", f"{values.get('Laenge', '—')} m"))
        
        row2 = (make_cell("Schacht oben", values.get('Schacht_oben', '—')) +
                make_cell("Material", values.get('Material', '—')) +
                make_cell("Baujahr", values.get('Baujahr', '—')))
        
        row3 = (make_cell("Schacht unten", values.get('Schacht_unten', '—')) + 
                make_cell("Gefälle", f"{values.get('Gefaelle', '—')} ‰") +
                make_cell("Dimension", values.get('Dimension', '—')))
        
        html_table = f"""
        <table style="width:100%; border-collapse:collapse;">
            <tr>{row1}</tr>
            <tr>{row2}</tr>
            <tr>{row3}</tr>
        </table>
        """
        
        return html_table

    def ask_include_images(self):
        """Dialog: Sollen Schadensbilder mit in PDF?"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Schadensbilder in PDF?",
            "Möchten Sie die Schadensbilder in der PDF-Ausgabe einbinden?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Standard: Nein
        )
        return reply == QMessageBox.Yes

    def get_damage_images_data(self):
        """Sammelt Schadensbilder mit Text aus selected_data (wie drawDamages!)"""
        base_image_dir = r"K:\Schadensbilder"
        
        # Header-Index (wie in drawDamages)
        header_names = []
        for col in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(col)
            header_names.append(header_item.text() if header_item else "")
        
        try:
            idx_foto = header_names.index("foto_dateiname")
        except ValueError:
            idx_foto = -1
        
        images_data = []
        
        # Gleiche Logik wie drawDamages!
        for row_data in self.selected_data:
            if len(row_data) > 13 and row_data[1]:
                try:
                    position = float(self.parse_decimal(row_data[1]))
                    kuerzel = row_data[2]
                    langtext = row_data[3]
                    
                    # Bildpfad (exakt deine Logik!)
                    image_path = None
                    if idx_foto != -1 and idx_foto < len(row_data):
                        raw_path = row_data[idx_foto]
                        if raw_path:
                            full_path = os.path.normpath(raw_path)
                            if os.path.exists(full_path):
                                image_path = full_path
                            else:
                                filename = os.path.basename(raw_path)
                                image_path = os.path.join(base_image_dir, filename)
                                if not os.path.exists(image_path):
                                    image_path = None
                    
                    # Nur Schäden MIT Bild hinzufügen
                    if image_path:
                        label = f"{position:.1f}m | {kuerzel} | {langtext}"
                        images_data.append({
                            'label': label,
                            'image_path': image_path,
                            'position': position
                        })
                        print(f"✓ Bild für PDF: {label}")
                
                except ValueError:
                    continue
        
        print(f"✓ {len(images_data)} Bilder für PDF gefunden")
        return images_data

    def get_damage_images_from_scene(self):
        """Extrahiert alle Bilder aus der Scene mit ihren Labels"""
        images_data = []
        
        for item in self.scene.items():
            # Prüfe ob Element ein QGraphicsPixmapItem mit Label ist
            if hasattr(item, 'pixmap') and not item.pixmap().isNull():
                # Label/Titel des Bildes (z.B. aus dem QGraphicsTextItem darüber)
                label = ""
                
                # Versuche, den Label aus einem nahegelegenen TextItem zu finden
                for text_item in self.scene.items():
                    if hasattr(text_item, 'toPlainText'):
                        # Wenn TextItem in der Nähe des Bildes
                        if abs(text_item.pos().y() - item.pos().y()) < 50:
                            label = text_item.toPlainText()
                            break
                
                # Fallback: Verwende generischen Namen
                if not label:
                    label = f"Schaden {len(images_data) + 1}"
                
                images_data.append({
                    'label': label,
                    'pixmap': item.pixmap(),
                    'pos': item.pos()
                })
        
        return images_data

    def _draw_header_and_graphic(self, painter, printer):
        """Zeichnet Header und Grafik auf erste Seite"""
        from PyQt6.QtGui import QTextDocument, QFont
        from PyQt6.QtCore import Qt
        
        # === HEADER ===
        header_html = self._format_info_header_pdf()
        doc = QTextDocument()
        font = QFont("Segoe UI", 11)
        doc.setDefaultFont(font)
        doc.setHtml(header_html)
        doc.setTextWidth(printer.width() - 30)
        
        painter.translate(15, 15)
        doc.drawContents(painter)
        
        # Trennlinie
        y_pos = doc.size().height() + 20
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(0, int(y_pos), printer.width() - 30, int(y_pos))
        
        # === GRAFIK ===
        y_pos += 25
        scene_rect = self.scene.itemsBoundingRect()
        
        if scene_rect.width() > 0 and scene_rect.height() > 0:
            target_width = printer.width() - 40
            target_height = printer.height() - y_pos - 30
            
            scale_x = target_width / scene_rect.width()
            scale_y = target_height / scene_rect.height()
            scale = min(scale_x, scale_y, 1.0)
        else:
            scale = 1.0
        
        painter.translate(20, y_pos)
        painter.scale(scale, scale)
        self.scene.render(painter)

    def _draw_images_pages(self, painter, printer, images_data):
        """Bilder KOMPRIMIERT mit QImage einbetten"""
        margin = 20
        page_width = printer.width() - 2 * margin
        
        y_pos = margin
        
        for i, img_data in enumerate(images_data):
            try:
                # === TITEL ===
                painter.resetTransform()
                painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
                painter.setPen(Qt.black)
                
                title_height = painter.fontMetrics().height() + 10
                
                # === BILD ALS QImage laden (KOMPRIMIERT!) ===
                image = QImage(img_data['image_path'])
                
                if not image.isNull():
                    # Qualität optimieren: Max 1920px Breite
                    if image.width() > 1920:
                        image = image.scaledToWidth(1920, Qt.SmoothTransformation)
                    
                    # Seitenbreite-Skalierung
                    scale = page_width / image.width()
                    img_height = int(image.height() * scale)
                    
                    # Zu hoch? Begrenzen
                    max_img_height = printer.height() - 150
                    if img_height > max_img_height:
                        img_height = max_img_height
                    
                    # Neue Seite?
                    if y_pos + title_height + img_height > printer.height() - margin:
                        printer.newPage()
                        y_pos = margin
                    
                    # === ZEICHNEN ===
                    painter.drawText(margin, int(y_pos + title_height - 5), img_data['label'])
                    y_pos += title_height
                    
                    target_rect = QRectF(margin, y_pos, page_width, img_height)
                    painter.drawImage(target_rect, image)
                    
                    y_pos += img_height + 40
                    
                else:
                    if y_pos + 50 > printer.height():
                        printer.newPage()
                        y_pos = margin
                    painter.drawText(margin, int(y_pos + 20), f"Bild fehlerhaft: {img_data['label']}")
                    y_pos += 50
                    
            except Exception as e:
                print(f"✗ Bild {img_data['image_path']}: {e}")

        # === Grafik-Funktionen ===

    def drawDamages(self):
        self.scene.clear()

        # Maximalen Stationswert ermitteln
        station_werte = []
        for row_data in self.selected_data:
            if len(row_data) > 1 and row_data[1]:
                try:
                    station_werte.append(float(self.parse_decimal(row_data[1])))
                except ValueError:
                    pass

        max_station = max(station_werte) if station_werte else 0.0
        print(f"max_station={max_station}, Laenge={self.Laenge}")

        # Abweichung > 2m → Laenge anpassen
        if max_station > 0 and abs(self.Laenge - max_station) > 2.0:
            print("→ Laenge auf max_station angepasst!")
            effektive_laenge = max_station
        else:
            effektive_laenge = self.Laenge

        self.effektive_laenge = effektive_laenge
        self.drawCanal()
        self.occupied_positions = []
        max_y_position = 0

        # Basisverzeichnis für Bilder
        base_image_dir = r"K:\Schadensbilder"

        # Index der Bildspalte ermitteln
        header_names = []
        for col in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(col)
            header_names.append(header_item.text() if header_item else "")

        try:
            idx_foto = header_names.index("foto_dateiname")
        except ValueError:
            idx_foto = -1

        # Daten nach Station sortieren
        self.selected_data.sort(key=lambda x: self.safe_position(x))

        for row_data in self.selected_data:
            if len(row_data) > 13 and row_data[1]:
                try:
                    schadens_position = float(self.parse_decimal(row_data[1]))

                    # === BILD-PFAD KONSTRUIEREN ===
                    image_path = None
                    if idx_foto != -1 and idx_foto < len(row_data):
                        raw_path = row_data[idx_foto]
                        if raw_path:
                            # Vollständigen Pfad testen
                            full_path = os.path.normpath(raw_path)
                            if os.path.exists(full_path):
                                image_path = full_path
                                print(f"✓ Vollständiger Pfad gefunden: {image_path}")
                            else:
                                # Unterordner testen
                                filename = os.path.basename(raw_path)
                                image_path = os.path.join(base_image_dir, filename)
                                if os.path.exists(image_path):
                                    print(f"✓ Fallback im Base-Verzeichnis: {image_path}")
                                else:
                                    print(f"✗ Bild nicht gefunden: '{raw_path}' → '{image_path}'")

                    text_y = self.drawDamage(
                        schadens_position,
                        row_data[2],   # kuerzel
                        row_data[3],   # langtext
                        row_data[11],  # zd
                        row_data[12],  # zs
                        row_data[13],  # zb
                        row_data[9],   # pos_von
                        image_path=image_path
                    )
                    max_y_position = max(max_y_position, text_y)
                except ValueError as e:
                    print(f"Fehler bei Zeile: {e}")
                    continue

        print(f"Max Y: {max_y_position}")
        # === SCROLL-PROBLEM BEHEBEN ===
        # Weiterer Platz rechts für lange Texte
        right_margin = 400  # Extra Platz für lange Texte
        
        scene_rect = QRectF(
            0,
            0,
            self.scene_width + right_margin,  # ✅ Mehr Platz rechts!
            max(max_y_position + 100, self.scene_height)
        )
        
        self.scene.setSceneRect(scene_rect)
        self.view.fitInView(scene_rect, Qt.KeepAspectRatio)
        
        # Scroll-Setup nachzeichnen
        self.setup_scroll_view()

    def setup_scroll_view(self):
        """Richtet vollständigen Scroll für QGraphicsView ein"""
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Immer sichtbar
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)    # Immer sichtbar
        
        # Drag-Modus für besseres Scrollen
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Scroll-Speeds erhöhen
        self.view.horizontalScrollBar().setSingleStep(20)
        self.view.verticalScrollBar().setSingleStep(20)
        
        # Minimum/Maximum Scroll-Ranges setzen
        self.update_scene_rect()

    def update_scene_rect(self):
        """Aktualisiert Scene-Rect für vollen Scroll-Bereich"""
        scene_rect = self.scene.itemsBoundingRect()
        
        # Mindestgröße + Puffer für Scroll
        min_width = 1200
        min_height = 800
        
        # Puffer für Scroll
        padding_x = 200
        padding_y = 100
        
        final_rect = QRectF(
            0,
            0,
            max(scene_rect.width() + padding_x, min_width),
            max(scene_rect.height() + padding_y, min_height)
        )
        
        self.scene.setSceneRect(final_rect)
        self.view.ensureVisible(final_rect)


    def safe_position(self, row_data):
        """Sichere Positions-Extraktion für Sortierung (Index 1 = station)"""
        try:
            pos_str = self.parse_decimal(row_data[1]) if len(row_data) > 1 and row_data[1] else "0"
            return float(pos_str)
        except (ValueError, TypeError):
            return float('inf')  # Ungültige ans Ende

    def parse_decimal(self, string):
        return string.replace(",", ".")

    def drawCanal(self):
        scale_factor = 50  # 50 Pixel pro Meter
        padding = 100

        laenge = getattr(self, "effektive_laenge", self.Laenge)  # angepasste Länge

        self.scene_width = 800
        self.scene_height = laenge * scale_factor + padding
        self.x_center = self.scene_width // 2

        self.scene.setSceneRect(0, 0, self.scene_width, self.scene_height)

        # Kanallinie
        self.scene.addLine(
            self.x_center,
            padding // 2,
            self.x_center,
            self.scene_height - padding // 2,
            QtGui.QPen(Qt.black, 3)
        )

        # Schächte (oben/unten)
        shaft_size = 20
        self.scene.addEllipse(
            self.x_center - shaft_size // 2,
            padding // 2 - shaft_size // 2,
            shaft_size,
            shaft_size,
            QtGui.QPen(Qt.black),
            QtGui.QBrush(Qt.white)
        )
        self.scene.addEllipse(
            self.x_center - shaft_size // 2,
            self.scene_height - padding // 2 - shaft_size // 2,
            shaft_size,
            shaft_size,
            QtGui.QPen(Qt.black),
            QtGui.QBrush(Qt.white)
        )

    def drawDamage(self, position, kuerzel, langtext, zd, zs, zb, pos_von, image_path=None):
        """
        Zeichnet Schaden mit klickbarem Text.
        
        Args:
            position, kuerzel, langtext, zd, zs, zb, pos_von: wie bisher
            image_path: Optionaler Pfad zum Bild (für Klick)
        """
        scale_factor = 50
        padding = 100
        text_spacing = 30
        
        y = padding // 2 + position * scale_factor
        x = self.x_center + 20  # Text immer rechts (unverändert!)

        # Farbe bestimmen (unverändert)
        try:
            zd_int = int(float(str(zd).strip())) if zd else 5
            zs_int = int(float(str(zs).strip())) if zs else 5
            zb_int = int(float(str(zb).strip())) if zb else 5
            z_werte = [v for v in [zd_int, zs_int, zb_int] if 1 <= v <= 4]
            min_value = min(z_werte) if z_werte else 5
        except:
            min_value = 5

        farben = {0: QtGui.QColor("red"), 1: QtGui.QColor("yellow"), 2: QtGui.QColor("blue"),
                3: QtGui.QColor("lightgreen"), 4: QtGui.QColor("green"), 5: QtGui.QColor("black")}
        color = farben[min_value]

        # BCA-Anschluss (unverändert)
        if kuerzel.strip().upper() == 'BCA':
            pos_von_int = int(float(str(pos_von).strip())) if pos_von else 6
            
            if 1 <= pos_von_int <= 5:                    # Rechts
                anschluss_end_x = x + 3
            elif 7 <= pos_von_int <= 11:                 # Links
                anschluss_end_x = self.x_center - 30
            else:                                        # 6/12: Nur Kanalpunkt
                anschluss_end_x = self.x_center
            
            self.scene.addLine(
                self.x_center, y,     # Immer Kanal-Start
                anschluss_end_x, y,   # Dynamisches Ende
                QPen(Qt.red, 3)
            )
            print(f"  -> BCA pos_von={pos_von_int}: Linie nach X={anschluss_end_x}")

        # Text-Position mit Kollisionsvermeidung (unverändert)
        final_y = y
        while any(abs(final_y - pos) < text_spacing for pos in self.occupied_positions):
            final_y += text_spacing
        self.occupied_positions.append(final_y)
        self.occupied_positions.sort()

        # === KLICKBAREN TEXT mit Bildpfad ===
        text = f"{position:.1f}m | {kuerzel} | {langtext}"
        text_item = DamageTextItem(text, image_path=image_path)
        text_item.setPos(x + 5, final_y - 10)
        text_item.setBrush(color)
        text_item.setCursor(Qt.PointingHandCursor)  # Hand-Cursor
        self.scene.addItem(text_item)

        # Callout-Linie (unverändert)
        self.scene.addLine(x - 20, y, x, final_y, QPen(color))

        return final_y + text_item.boundingRect().height()

    def zoomIn(self):
        self.zoom_factor = getattr(self, 'zoom_factor', 1.0) * 1.25
        self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))

    def zoomOut(self):
        self.zoom_factor = getattr(self, 'zoom_factor', 1.0) / 1.25
        self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))

    def keyPressEvent(self, event):
        """Tastatur-Shortcuts für Scroll"""
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.view.scale(1.1, 1.1)
        elif event.key() == Qt.Key_Minus:
            self.view.scale(0.9, 0.9)
        elif event.key() == Qt.Key_0:
            self.view.resetTransform()
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        else:
            super().keyPressEvent(event)

class DamageTextItem(QGraphicsSimpleTextItem):
    def __init__(self, text, image_path=None, parent=None):
        super().__init__(text, parent)
        self.image_path = image_path

    def mousePressEvent(self, event):
        if self.image_path and os.path.exists(self.image_path):
            try:
                if os.name == "nt":  # Windows
                    os.startfile(self.image_path)
                else:  # Linux/Mac
                    QDesktopServices.openUrl(QUrl.fromLocalFile(self.image_path))
                print(f"✓ Bild geöffnet: {self.image_path}")
            except Exception as e:
                print(f"✗ Fehler beim Öffnen '{self.image_path}': {e}")
        else:
            print(f"✗ Bildpfad fehlt oder existiert nicht: {self.image_path}")
        super().mousePressEvent(event)
