import locale
from pathlib import Path

from qgis.utils import iface
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QHeaderView, QLineEdit
from qgis.PyQt.QtCore import Qt

from qkan import QKan

from .tab_einstellungen import EinstellungenManager
from .tab_auftraege import AuftraegeManager
from .tab_kosten import KostenManager
from .tab_budget import BudgetManager
from .pdf_template_editor import PdfTemplateEditor


# ======================================================================
# UI-KLASSE LADEN
# ======================================================================

FORM_CLASS, _ = uic.loadUiType(
    str(Path(__file__).with_name("KostenermittlungTool.ui"))
)


class KostenermittlungTool(QDialog, FORM_CLASS):
    """
    Hauptdialog für das Kanaluntersuchungs- und Kostenermittlungstool.

    - Lädt das UI aus der .ui-Datei
    - Nutzt bevorzugt den aktiven QKan-Datenbankkontext
    - Initialisiert DB-Verbindung und Manager (Einstellungen, Aufträge, Kosten, Budget)
    - Verknüpft die UI-Elemente mit der Fachlogik
    """

    # ==================================================================
    # INITIALISIERUNG
    # ==================================================================

    def __init__(self, parent=None):
        parent_widget = (
            parent.iface.mainWindow()
            if parent is not None and hasattr(parent, "iface")
            else None
        )
        super().__init__(parent_widget)

        self.parent_plugin = parent
        self.iface = parent.iface if hasattr(parent, "iface") else iface

        self.setupUi(self)

        self._load_database_connection()
        self._init_locale()
        self._init_managers()
        self._init_runtime_ui()
        self._connect_signals()
        self._load_initial_data()
        self._configure_window()

    # ==================================================================
    # BASIS: DB / LOCALE / MANAGER
    # ==================================================================

    def _load_database_connection(self):
        """
        Stellt die DB-Verbindung über das gemeinsame db_backend her.

        Bevorzugt:
        1. Aktiven QKan-Kontext (QKan.dbsource / QKan.dbtype)
        2. Fallback über die bisherige Backend-Logik
        """
        try:
            from ..netzuebersicht.db_backend import get_db_type, get_backend

            self.conn = None
            self.cur = None
            self.db_config = {}

            qkan_dbtype = getattr(QKan, "dbtype", None)
            qkan_dbsource = getattr(QKan, "dbsource", None)

            self.db_type = qkan_dbtype or get_db_type()
            self.backend = get_backend(self.db_type)

            print("[KostenermittlungTool] Starte DB-Verbindungsaufbau")
            print(f"[KostenermittlungTool] QKan.dbtype   = {qkan_dbtype}")
            print(f"[KostenermittlungTool] QKan.dbsource = {qkan_dbsource}")
            print(f"[KostenermittlungTool] backend       = {type(self.backend).__name__}")

            # 1. Bevorzugt: aktive QKan-DB übernehmen
            if qkan_dbsource and hasattr(self.backend, "load_native_connection_from_qkan"):
                try:
                    print("[KostenermittlungTool] Versuche Verbindung aus QKan-Kontext")
                    self.conn, self.cur, self.db_config = (
                        self.backend.load_native_connection_from_qkan(
                            self, qkan_dbsource
                        )
                    )
                except Exception as e:
                    print(
                        "[KostenermittlungTool] load_native_connection_from_qkan fehlgeschlagen: "
                        f"{e}"
                    )
                    self.conn, self.cur, self.db_config = None, None, {}

            # 2. Fallback: bisheriges Verhalten
            if self.conn is None or self.cur is None:
                print("[KostenermittlungTool] Fallback auf load_native_connection(...)")
                self.conn, self.cur, self.db_config = self.backend.load_native_connection(
                    self.parent_plugin
                )

            if self.conn is None or self.cur is None:
                raise Exception(
                    "Das Backend konnte keine gültige Datenbankverbindung herstellen."
                )

            self.is_spatialite = self.db_type == "spatialite"

            print(f"[KostenermittlungTool] Verbindung erfolgreich: conn={self.conn}")
            print(f"[KostenermittlungTool] Cursor erfolgreich: cur={self.cur}")
            print(f"[KostenermittlungTool] db_config={self.db_config}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Datenbankfehler",
                f"Fehler bei der DB-Verbindung:\n{e}",
            )
            self.conn, self.cur = None, None
            self.db_config = {}
            self.is_spatialite = False

    def _init_locale(self):
        """Setzt das Zahlenformat auf deutsches Locale, falls möglich."""
        try:
            locale.setlocale(locale.LC_NUMERIC, "de_DE.UTF-8")
        except Exception:
            locale.setlocale(locale.LC_NUMERIC, "")

    def _init_managers(self):
        """Initialisiert die ausgelagerte Fachlogik."""
        self.logic_einstellungen = EinstellungenManager(self)
        self.logic_auftraege = AuftraegeManager(self, self.logic_einstellungen)
        self.logic_kosten = KostenManager(self)
        self.logic_budget = BudgetManager(self)

    # ==================================================================
    # RUNTIME-UI (NACH setupUi)
    # ==================================================================

    def _init_runtime_ui(self):
        """Ergänzt alles, was nicht sinnvoll statisch im Designer gepflegt wird."""
        self._setup_pdf_editors()
        self._setup_budget_years()
        self._setup_tables()
        self._setup_cost_fields()
        self._setup_misc_widgets()

    # ------------------------------------------------------------------
    # PDF-EDITOR-PLATZHALTER ERSETZEN
    # ------------------------------------------------------------------

    def _setup_pdf_editors(self):
        """
        Ersetzt die Platzhalter-Widgets aus der .ui-Datei durch echte PdfTemplateEditor.
        Erwartet in der UI:
        - QWidget mit objectName 'pdf_info_editor'
        - QWidget mit objectName 'pdf_beauf_editor'
        """
        self.pdf_info_editor = self._replace_placeholder_with_widget(
            "pdf_info_editor", PdfTemplateEditor(self)
        )
        self.pdf_beauf_editor = self._replace_placeholder_with_widget(
            "pdf_beauf_editor", PdfTemplateEditor(self)
        )

    def _replace_placeholder_with_widget(self, object_name, new_widget):
        """Hilfsfunktion zum Austausch eines Platzhalter-Widgets im Layout."""
        placeholder = getattr(self, object_name, None)
        if placeholder is None:
            raise RuntimeError(
                f"Platzhalter-Widget '{object_name}' wurde in der UI nicht gefunden."
            )

        parent = placeholder.parentWidget()
        layout = parent.layout()
        if layout is None:
            raise RuntimeError(
                f"Eltern-Widget von '{object_name}' besitzt kein Layout."
            )

        index = layout.indexOf(placeholder)
        layout.removeWidget(placeholder)
        placeholder.deleteLater()

        new_widget.setObjectName(object_name)
        layout.insertWidget(index, new_widget)
        return new_widget

    # ------------------------------------------------------------------
    # TABELLENKONFIGURATION
    # ------------------------------------------------------------------

    def _setup_budget_years(self):
        """Befüllt die Budget-Jahres-Comboboxen mit einem Fenster von +/- 2 Jahren."""
        import datetime

        akt_jahr = str(datetime.datetime.now().year)
        jahre = [str(datetime.datetime.now().year + i) for i in range(-2, 3)]

        self.budget_jahr_filter.clear()
        self.budget_jahr_filter.addItems(jahre)
        self.budget_jahr_filter.setCurrentText(akt_jahr)

        self.budget_jahr.clear()
        self.budget_jahr.addItems(jahre)
        self.budget_jahr.setCurrentText(akt_jahr)

    def _setup_tables(self):
        """Konfiguriert Spaltenbreiten und Resize-Modi der Tabellen."""
        # Aufträge
        self.auftraege_table.setColumnCount(7)
        self.auftraege_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        for i in range(1, 6):
            self.auftraege_table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeToContents
            )
        self.auftraege_table.horizontalHeader().setSectionResizeMode(
            6, QHeaderView.Fixed
        )
        self.auftraege_table.setColumnWidth(6, 220)

        # Budget
        self.budget_table.setColumnCount(6)
        self.budget_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # Haltungen
        self.Liste_Haltungen.setColumnCount(10)
        self.Liste_Haltungen.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )

        # Preisverwaltung
        self.preise_table.setColumnCount(2)
        self.preise_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self.preise_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )

    # ------------------------------------------------------------------
    # KOSTEN-ANZEIGEFELDER
    # ------------------------------------------------------------------

    def _setup_cost_fields(self):
        """Setzt die Eigenschaft der Summenfelder."""
        field_names = [
            "Reinigung_netto_MW",
            "Reinigung_brutto_MW",
            "Reinigung_netto_RW",
            "Reinigung_brutto_RW",
            "Reinigung_netto_SW",
            "Reinigung_brutto_SW",
            "Reinigung_befahrung_netto_MW",
            "Reinigung_befahrung_brutto_MW",
            "Reinigung_befahrung_netto_RW",
            "Reinigung_befahrung_brutto_RW",
            "Reinigung_befahrung_netto_SW",
            "Reinigung_befahrung_brutto_SW",
            "Befahrung_netto_MW",
            "Befahrung_brutto_MW",
            "Befahrung_netto_RW",
            "Befahrung_brutto_RW",
            "Befahrung_netto_SW",
            "Befahrung_brutto_SW",
        ]

        for name in field_names:
            widget = getattr(self, name, None)
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(True)
                widget.setAlignment(Qt.AlignRight)
                widget.setMaximumWidth(120)
                if not widget.text():
                    widget.setText("0.00 €")

    # ------------------------------------------------------------------
    # SONSTIGE UI-ANPASSUNGEN
    # ------------------------------------------------------------------

    def _setup_misc_widgets(self):
        """Optische Feinheiten und Standardwerte für einzelne Widgets."""
        self.btn_neu_auftrag.setStyleSheet(
            "QPushButton { font-size: 13px; font-weight: bold; }"
        )

        self.btn_excel_import.hide()
        self.label_weitere.setStyleSheet("font-size: 16px; color: gray;")

        self.einst_kategorie.clear()
        self.einst_kategorie.addItems(
            [
                "Straße",
                "Sachbearbeiter",
                "Grund der Untersuchung",
                "Firmen",
                "Verteiler",
                "KST_Reinigung",
                "KST_TV",
                "KST_GAL",
                "SK_Normal_RW",
                "SK_Normal_SW",
                "SK_Normal_MW",
            ]
        )

    # ==================================================================
    # SIGNALVERKNÜPFUNG
    # ==================================================================

    def _connect_signals(self):
        """Verdrahtet alle relevanten UI-Elemente mit der Logik."""

        # Aufträge
        self.btn_neu_auftrag.clicked.connect(
            lambda: self.logic_auftraege.create_new_project()
        )
        self.suche_auftraege.textChanged.connect(self.filter_auftraege_table)

        # Budget
        self.budget_jahr_filter.currentTextChanged.connect(
            lambda: self.logic_budget.refresh_budget_table()
        )
        self.btn_refresh_budget.clicked.connect(
            lambda: self.logic_budget.refresh_budget_table()
        )
        self.btn_budget_save.clicked.connect(
            lambda: self.logic_budget.add_budget()
        )

        # Kostenermittlung
        self.btn_auslesung_1.clicked.connect(
            lambda: self.logic_kosten.showSelectedFeatures()
        )
        self.btn_auslesung_2.clicked.connect(
            lambda: self.logic_kosten.showSelectedFeatures()
        )
        self.checkBox_Panoramo.stateChanged.connect(
            lambda: self.logic_kosten.on_checkbox_changed()
        )
        self.checkBox_GAL.stateChanged.connect(
            lambda: self.logic_kosten.on_checkbox_changed()
        )
        self.btn_berechnung_reinigung.clicked.connect(
            lambda: self.logic_kosten.calculateCleaningCost()
        )
        self.btn_berechnung_tv.clicked.connect(
            lambda: self.logic_kosten.calculateCleaningTVCost()
        )
        self.btn_excel_export.clicked.connect(
            lambda: self.logic_kosten.export_excel()
        )

        # Preisverwaltung
        self.preis_kategorie_combo.currentTextChanged.connect(
            lambda: self.logic_einstellungen.load_prices_into_table()
        )
        self.btn_preis_neu.clicked.connect(
            lambda: self.logic_einstellungen.add_price_row()
        )
        self.btn_preis_loeschen.clicked.connect(
            lambda: self.logic_einstellungen.delete_selected_price_row()
        )
        self.btn_preise_aus_json.clicked.connect(
            lambda: self.logic_einstellungen.reload_prices_from_json()
        )
        self.btn_preise_speichern.clicked.connect(
            lambda: self.logic_einstellungen.save_prices_from_table()
        )

        # Einstellungen
        self.einst_kategorie.currentTextChanged.connect(
            lambda: self.logic_einstellungen.on_kategorie_changed()
        )
        self.btn_excel_import.clicked.connect(
            lambda: self.logic_einstellungen.import_excel()
        )
        self.einst_liste.itemClicked.connect(
            lambda: self.logic_einstellungen.on_list_item_clicked()
        )
        self.btn_add.clicked.connect(
            lambda: self.logic_einstellungen.save_item()
        )
        self.btn_del.clicked.connect(
            lambda: self.logic_einstellungen.delete_item()
        )
        self.btn_plan_browse.clicked.connect(
            lambda: self.logic_einstellungen.on_choose_plan_path()
        )
        self.btn_plan_clear.clicked.connect(
            lambda: self.logic_einstellungen.on_clear_plan_path()
        )

        # PDF-Vorlagen
        self.btn_save_pdf_templates.clicked.connect(self._save_pdf_templates)

    # ==================================================================
    # INITIALDATEN LADEN
    # ==================================================================

    def _load_initial_data(self):
        """
        Lädt initiale Inhalte:
        - Preisverwaltung
        - Auftragsliste
        - PDF-Templates in den Editoren
        - Einstellungs-Listen
        - Budgettabelle
        """
        self.logic_einstellungen.init_preisverwaltung()

        self.logic_auftraege.init_pdf_template_editors()
        self.logic_auftraege.refresh_projects_table()

        self.logic_einstellungen.init_pdf_template_editors()
        self.logic_einstellungen.load_list()

        self.logic_budget.refresh_budget_table()

        self.einst_kategorie.setCurrentText("Straße")
        self.logic_einstellungen.on_kategorie_changed()

        saved_path = self.logic_einstellungen.get_single_value("Plan_Basis_Pfad")
        self.plan_path_line.setText(saved_path)

    # ==================================================================
    # HILFSMETHODEN / FENSTER / EVENTS
    # ==================================================================

    def _save_pdf_templates(self):
        """Speichert die aktuell bearbeiteten PDF-Vorlagen."""
        self.logic_einstellungen.save_pdf_templates()
        QMessageBox.information(
            self,
            "PDF-Vorlagen",
            "Die PDF-Vorlagen wurden gespeichert.",
        )

    def _configure_window(self):
        """Setzt Titel, Fensterflags und Startgröße."""
        self.setWindowTitle("Kanaluntersuchungs- und Kostenermittlungstool")
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )
        self.resize(1100, 850)

    def filter_auftraege_table(self, text: str):
        """Live-Filter für die Auftrags-Tabelle über die ersten fünf Textspalten."""
        search_text = text.lower()
        for row in range(self.auftraege_table.rowCount()):
            row_visible = False
            for col in range(5):
                item = self.auftraege_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.auftraege_table.setRowHidden(row, not row_visible)

    def closeEvent(self, event):
        """
        Schließt den Dialog, aber NICHT die DB-Verbindung.

        Begründung:
        Die Verbindung stammt bevorzugt aus dem gemeinsamen QKan-Kontext
        bzw. wird im Plugin-Kontext länger genutzt. Ein Schließen an dieser
        Stelle kann dazu führen, dass Manager oder wiederverwendete Dialog-
        Instanzen mit einer bereits geschlossenen Verbindung weiterarbeiten.
        """
        try:
            print("[KostenermittlungTool] closeEvent: Dialog wird geschlossen")
            print("[KostenermittlungTool] DB-Verbindung bleibt bewusst offen")
        except Exception as e:
            print(f"[KostenermittlungTool] Fehler im closeEvent: {e}")

        if hasattr(self, "parent_plugin") and hasattr(self.parent_plugin, "calc_dialog"):
            self.parent_plugin.calc_dialog = None

        event.accept()
