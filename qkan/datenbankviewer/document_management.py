"""
document_management.py - Dokumentenmanagement für QGIS-Plugin Datenbankviewer
Modularisierte Version der DocumentManagementWindow.
"""

import os
import shutil
import json
from PyQt5.QtWidgets import (QDialog, QPushButton, QFileDialog, QTreeWidgetItem, 
                            QMessageBox, QLineEdit, QTreeWidget, QCheckBox)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5 import uic
import psycopg2

# Lokale Imports
from .db_connection import loadpostgresconnection
from .utils import DOCUMENT_BASE_PATH


FORMCLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'res', 'dokumentenablage.ui')
)


class DocumentManagementWindow(QDialog, FORMCLASS):
    """Dialog für Dokumentenmanagement (Hinzufügen/Löschen/Öffnen)."""
    
    def __init__(self, haltungsname, street_name, strakatid, parent=None):
        super().__init__(parent)
        self.haltungsname = haltungsname
        self.street_name = street_name
        self.strakatid = strakatid
        
        # Konfiguration laden
        self.base_path = self.load_config()
        if not self.base_path:
            return
        
        # DB-Verbindung
        self.conn = loadpostgresconnection(self.parent())  # Parent hat Verbindung
        if not self.conn:
            return
        
        self.cur = self.conn.cursor()
        self.check_and_create_documents_table()
        
        # UI initialisieren
        self.setupUi(self)
        self.init_widgets()
        self.connect_signals()
        self.loadExistingFiles()
    
    def load_config(self):
        """Lädt Dokumentenpfad aus lokaler JSON-Konfig im Toolordner."""
        # Basisverzeichnis dieses Moduls
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        # JSON liegt jetzt in einem Unterordner 'json' im Toolordner
        config_file_path = os.path.join(tool_dir, "json", "dokumentenablage.json")

        try:
            with open(config_file_path, "r", encoding="utf-8") as json_file:
                config = json.load(json_file)
                # Fallback auf DOCUMENT_BASE_PATH, falls Key fehlt
                return config.get("dokumentenmanagement", DOCUMENT_BASE_PATH)
        except FileNotFoundError as e:
            QMessageBox.warning(
                self,
                "Config-Fehler",
                f"Konfigurationsdatei 'dokumentenablage.json' wurde nicht gefunden:\n"
                f"{config_file_path}\n\n"
                f"Es wird der Standardpfad verwendet:\n{DOCUMENT_BASE_PATH}",
            )
            return DOCUMENT_BASE_PATH
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "Config-Fehler",
                f"Die Datei 'dokumentenablage.json' enthält ungültiges JSON:\n"
                f"{config_file_path}\n\nFehler: {e}\n"
                f"Es wird der Standardpfad verwendet:\n{DOCUMENT_BASE_PATH}",
            )
            return DOCUMENT_BASE_PATH
        except Exception as e:
            QMessageBox.warning(
                self,
                "Config-Fehler",
                f"Fehler beim Lesen der Konfiguration:\n{config_file_path}\n\n{e}\n"
                f"Es wird der Standardpfad verwendet:\n{DOCUMENT_BASE_PATH}",
            )
            return DOCUMENT_BASE_PATH
    
    def init_widgets(self):
        """Initialisiert und füllt Widgets."""
        self.streetNameInput = self.findChild(QLineEdit, 'strassenname_line')
        self.haltungsnameInput = self.findChild(QLineEdit, 'haltungsname_line')
        self.yearInput = self.findChild(QLineEdit, 'jahr_line')
        self.houseNumberInput = self.findChild(QLineEdit, 'hausnummer_line')
        self.saveButton = self.findChild(QPushButton, 'save_document_button')
        self.deleteButton = self.findChild(QPushButton, 'delete_document_button')
        self.fileTree = self.findChild(QTreeWidget, 'dokumentenablage_tree')
        self.strakatidInput = self.findChild(QLineEdit, 'strakatid_line')
        self.checkBoxGal = self.findChild(QCheckBox, 'checkBox_gal')
        self.checkBoxSinkkasten = self.findChild(QCheckBox, 'checkBox_sinkkasten')
        
        # Werte setzen
        self.streetNameInput.setText(self.street_name)
        self.haltungsnameInput.setText(self.haltungsname)
        self.strakatidInput.setText(self.strakatid)
        
        # Tree initialisieren
        self.fileTree.setColumnCount(1)
        self.fileTree.setHeaderLabels(["Dateien nach Kategorie und Jahr"])
    
    def connect_signals(self):
        """Verbindet Signale mit Slots."""
        self.saveButton.clicked.connect(self.showFileDialog)
        self.deleteButton.clicked.connect(self.deleteSelectedFile)
        self.fileTree.itemDoubleClicked.connect(self.openFile)
        self.open_document_button.clicked.connect(self.openDocumentFolder)
    
    def table_exists(self, table_name, schema='public'):
        """Prüft Existenz ohne Berechtigungsfehler"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = %s
                );
            """, (schema, table_name))
            exists = cursor.fetchone()[0]
            cursor.close()
            return exists
        except Exception:
            return False

    def check_and_create_documents_table(self):
        """Prüft/Erstellt documents-Tabelle."""
        if self.table_exists('documents'):
            print("✅ Tabelle documents existiert bereits")
            
            # Spalte strakatid hinzufügen falls fehlt
            try:
                self.cur.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'documents' AND column_name = 'strakatid';
                """)
                if not self.cur.fetchone():
                    self.cur.execute("ALTER TABLE documents ADD COLUMN strakatid TEXT;")
                    self.conn.commit()
                    print("✅ Spalte strakatid zu documents hinzugefügt")
            except psycopg2.errors.InsufficientPrivilege as e:
                print(f"ℹ️ Keine Rechte zum Hinzufügen von Spalten: {e}")
            except Exception as e:
                self.conn.rollback()
                raise
            return
        
        # Tabelle neu erstellen (nur wenn User CREATE-Rechte hat)
        try:
            self.cur.execute("""
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    category TEXT,
                    street_name TEXT,
                    house_number TEXT,
                    year TEXT,
                    haltungsname TEXT,
                    strakatid TEXT,
                    file_path TEXT
                );
            """)
            self.conn.commit()
            print("✅ Tabelle documents angelegt")
        except psycopg2.errors.InsufficientPrivilege as e:
            self.conn.rollback()
            QtWidgets.QMessageBox.warning(
                self.dlg if hasattr(self, 'dlg') else None,
                "Setup benötigt", 
                f"Tabelle 'documents' fehlt.\n"
                f"Bitte Administrator bitten, das Schema-Setup auszuführen.\n\n"
                f"Fehler: {str(e)}"
            )
            return
        except Exception as e:
            self.conn.rollback()
            raise
    
    def showFileDialog(self):
        """Öffnet Dateiauswahldialog."""
        options = QFileDialog.Options()
        self.files, _ = QFileDialog.getOpenFileNames(
            self, "Dokument auswählen", "", "All Files (*);;PDF Files (*.pdf)", options=options
        )
        if self.files:
            self.saveFiles()
    
    def saveFiles(self):
        """Speichert ausgewählte Dateien und DB-Einträge."""
        street_name = self.streetNameInput.text()
        year = self.yearInput.text()
        haltungsname = self.haltungsnameInput.text()
        house_number = self.houseNumberInput.text()
        
        if self.checkBoxGal.isChecked():
            category = 'GAL'
            folder_path = os.path.join(self.base_path, category, street_name, house_number, year)
        elif self.checkBoxSinkkasten.isChecked():
            category = 'Sinkkästen'
            folder_path = os.path.join(self.base_path, category, haltungsname, year)
        else:
            category = 'Haltungen'
            folder_path = os.path.join(self.base_path, category, street_name, year, haltungsname)
        
        os.makedirs(folder_path, exist_ok=True)
        
        for file in self.files:
            file_name = os.path.basename(file)
            target_path = os.path.join(folder_path, file_name)
            shutil.copy(file, target_path)
            
            # DB-Eintrag (mit strakatid)
            self.cur.execute("""
                INSERT INTO documents (category, street_name, house_number, year, haltungsname, strakatid, file_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (category, street_name, house_number, year, haltungsname, self.strakatid, target_path))
        
        self.conn.commit()
        print(f"Files saved to {folder_path}")
        self.loadExistingFiles()
    
    def loadExistingFiles(self):
        """Lädt Dateien aus DB in TreeWidget."""
        self.cur.execute("""
            SELECT category, street_name, house_number, year, haltungsname, strakatid, file_path
            FROM documents WHERE haltungsname = %s OR strakatid = %s
        """, (self.haltungsname, self.strakatid))
        files = self.cur.fetchall()
        
        self.fileTree.clear()
        categories = {}
        
        for file in files:
            category, street_name_db, house_number, year, haltungsname_db, _, file_path = file
            file_name = os.path.basename(file_path)
            
            category_item = categories.get(category) or QTreeWidgetItem([category])
            if category not in categories:
                self.fileTree.addTopLevelItem(category_item)
                categories[category] = category_item
            
            if category == 'GAL':
                street_item = self.get_or_create_item(category_item, street_name_db)
                house_item = self.get_or_create_item(street_item, house_number)
                year_item = self.get_or_create_item(house_item, year)
            elif category == 'Sinkkästen':
                haltungs_item = self.get_or_create_item(category_item, haltungsname_db)
                year_item = self.get_or_create_item(haltungs_item, year)
            else:  # Haltungen
                street_item = self.get_or_create_item(category_item, street_name_db)
                year_item = self.get_or_create_item(street_item, year)
            
            file_item = QTreeWidgetItem([file_name])
            file_item.setData(0, Qt.UserRole, file_path)
            year_item.addChild(file_item)
        
        self.fileTree.sortItems(0, Qt.AscendingOrder)
    
    def get_or_create_item(self, parent_item, text):
        """Erstellt oder findet Child-Item."""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.text(0) == text:
                return child
        new_item = QTreeWidgetItem([text])
        parent_item.addChild(new_item)
        return new_item
    
    def openFile(self, item):
        """Öffnet Datei mit Standardprogramm."""
        file_path = item.data(0, Qt.UserRole)
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Fehler", f"Datei nicht gefunden: {file_path}")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
    
    def deleteSelectedFile(self):
        """Löscht ausgewählte Datei (Datei + DB)."""
        selected_item = self.fileTree.currentItem()
        if not selected_item or not selected_item.parent():
            QMessageBox.warning(self, "Hinweis", "Bitte wählen Sie eine Datei aus.")
            return
        
        file_path = selected_item.data(0, Qt.UserRole)
        reply = QMessageBox.question(self, 'Bestätigung', 
                                   f'Möchten Sie "{os.path.basename(file_path)}" wirklich löschen?',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            self.cur.execute("DELETE FROM documents WHERE file_path = %s", (file_path,))
            self.conn.commit()
            
            # Leere Ordner löschen
            folder_path = os.path.dirname(file_path)
            while folder_path.startswith(self.base_path) and folder_path != self.base_path:
                try:
                    if not os.listdir(folder_path):
                        os.rmdir(folder_path)
                    else:
                        break
                except:
                    break
            
            parent = selected_item.parent()
            parent.removeChild(selected_item)
            
        except Exception as e:
            QMessageBox.critical(self, 'Fehler', f'Löschen fehlgeschlagen: {e}')
    
    def openDocumentFolder(self):
        """Öffnet Ordner der ausgewählten Datei."""
        selected_item = self.fileTree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Hinweis", "Bitte wählen Sie eine Datei aus.")
            return
        
        file_path = selected_item.data(0, Qt.UserRole)
        if not file_path:
            QMessageBox.warning(self, "Hinweis", "Bitte wählen Sie einen Datei-Eintrag aus.")
            return
        
        folder_path = os.path.dirname(file_path)
        if os.path.exists(folder_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        else:
            QMessageBox.warning(self, "Fehler", f"Ordner existiert nicht: {folder_path}")
    
    def closeEvent(self, event):
        """Räumt DB-Verbindung auf."""
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        super().closeEvent(event)
