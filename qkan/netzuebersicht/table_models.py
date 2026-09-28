# qkan/netzuebersicht/table_models.py
from PyQt6.QtSql import QSqlTableModel, QSqlQueryModel
from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QHeaderView, QAbstractItemView


def _check_exists(widget, table_name):
    """
    Prüft Tabellen-/View-Existenz über widget.backend + widget.cursor.
    """
    clean_name = table_name.replace('"', "")
    try:
        # cursor zuerst, dann Tabellenname
        exists = widget.backend.table_exists(widget.cursor, clean_name)
        print(f"[table_models] table_exists('{clean_name}') -> {exists}")
        return exists
    except Exception as e:
        print(f"[table_models] table_exists('{clean_name}') ERROR -> {e}")
        return False


def _debug_native_count(widget, table_name):
    """
    Prüft mit dem nativen Cursor, ob Daten in der Tabelle vorhanden sind.
    """
    try:
        widget.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row = widget.cursor.fetchone()
        count = row[0] if row else None
        print(f"[table_models] native COUNT({table_name}) -> {count}")
    except Exception as e:
        print(f"[table_models] native COUNT({table_name}) ERROR -> {e}")


def _debug_model_state(model, table_name):
    """
    Gibt Statusinformationen zu einem QSqlTableModel/QSqlQueryModel aus.
    """
    try:
        print(f"[table_models] MODEL DEBUG für {table_name}")
        print(f"  rowCount = {model.rowCount()}")
        print(f"  columnCount = {model.columnCount()}")
        print(f"  lastError = {model.lastError().text()}")

        headers = []
        for i in range(model.columnCount()):
            headers.append(str(model.headerData(i, Qt.Horizontal)))
        print(f"  headers = {headers}")

        if model.rowCount() > 0 and model.columnCount() > 0:
            row0 = []
            for col in range(min(model.columnCount(), 10)):
                try:
                    row0.append(str(model.data(model.index(0, col))))
                except Exception as e:
                    row0.append(f"<ERR {e}>")
            print(f"  erste Zeile = {row0}")
    except Exception as e:
        print(f"[table_models] _debug_model_state ERROR für {table_name}: {e}")


def _setup_table_view(table_view, proxy_model):
    table_view.setModel(proxy_model)
    table_view.setEditTriggers(QAbstractItemView.AllEditTriggers)
    table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
    table_view.setSelectionMode(QAbstractItemView.ExtendedSelection)


def _load_sql_table_model(widget, table_name, table_view, model_attr, proxy_attr):
    """
    Hilfsfunktion zum Laden einer Tabelle in QSqlTableModel + Proxy.
    """
    print(f"[table_models] lade Tabelle '{table_name}'")

    _debug_native_count(widget, table_name)

    model = QSqlTableModel(widget, widget.db)
    setattr(widget, model_attr, model)

    model.setTable(table_name)
    model.setEditStrategy(QSqlTableModel.OnManualSubmit)

    selected = model.select()
    print(f"[table_models] select('{table_name}') -> {selected}")

    if not selected:
        print(f"[table_models] select FEHLER '{table_name}': {model.lastError().text()}")

    while model.canFetchMore():
        print(f"[table_models] fetchMore() für '{table_name}'")
        model.fetchMore()

    _debug_model_state(model, table_name)

    proxy = QSortFilterProxyModel(widget)
    proxy.setSourceModel(model)
    proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)

    setattr(widget, proxy_attr, proxy)
    _setup_table_view(table_view, proxy)

    return model, proxy


def load_data_into_tables(widget):
    """
    Lädt Daten aus allen Tabellen/Views in die entsprechenden TableViews.
    Nutzt ausschließlich die bereits im Dialog aufgebaute QKan-/Backend-Verbindung.
    """
    print("========== [table_models] load_data_into_tables START ==========")

    try:
        print(f"[table_models] widget.db vorhanden = {hasattr(widget, 'db') and widget.db is not None}")
        print(f"[table_models] widget.cursor vorhanden = {hasattr(widget, 'cursor') and widget.cursor is not None}")
        print(f"[table_models] widget.backend = {type(getattr(widget, 'backend', None)).__name__}")

        if hasattr(widget, "db") and widget.db is not None:
            try:
                print(f"[table_models] db.isValid = {widget.db.isValid()}")
                print(f"[table_models] db.isOpen = {widget.db.isOpen()}")
                print(f"[table_models] db.connectionName = {widget.db.connectionName()}")
                print(f"[table_models] db.driverName = {widget.db.driverName()}")
                print(f"[table_models] db.databaseName = {widget.db.databaseName()}")
                print(f"[table_models] db.hostName = {widget.db.hostName()}")
                print(f"[table_models] db.userName = {widget.db.userName()}")
                print(f"[table_models] db.lastError = {widget.db.lastError().text()}")
            except Exception as e:
                print(f"[table_models] DB DEBUG ERROR -> {e}")

        # ============================================================
        # HALTUNGEN, SCHÄCHTE, ANSCHLUSSLEITUNGEN
        # ============================================================
        tables_config = [
            ("haltungen", "tableView_Haltungen", "model_haltungen", "proxy_model_haltungen"),
            ("schaechte", "tableView_Schaechte", "model_schaechte", "proxy_model_schaechte"),
            ("anschlussleitungen", "tableView_GAL", "model_anschlussleitungen", "proxy_model_anschlussleitungen"),
        ]

        for table_name, tableview_attr, model_attr, proxy_attr in tables_config:
            print(f"[table_models] Prüfe Standardtabelle: {table_name}")

            if _check_exists(widget, table_name):
                table_view = getattr(widget, tableview_attr)
                _load_sql_table_model(
                    widget=widget,
                    table_name=table_name,
                    table_view=table_view,
                    model_attr=model_attr,
                    proxy_attr=proxy_attr,
                )
            else:
                print(f"[table_models] Tabelle '{table_name}' existiert nicht!")

        # ============================================================
        # SINKKÄSTEN
        # ============================================================
        if hasattr(widget, "tableView_Sinkkaesten"):
            sink_table = widget.backend.get_sinkkaesten_table_name()
            print(f"[table_models] bevorzugte Sinkkästen-Tabelle = {sink_table}")

            candidates = [
                sink_table,
                '"Sinkkästen"',
                "Sinkkästen",
                '"Sinkkaesten"',
                "Sinkkaesten",
                "sinkkaesten",
            ]

            found_table = None
            for cand in candidates:
                if not cand:
                    continue
                if _check_exists(widget, cand):
                    found_table = cand
                    break

            print(f"[table_models] gefundene Sinkkästen-Tabelle = {found_table}")

            if found_table:
                model, proxy = _load_sql_table_model(
                    widget=widget,
                    table_name=found_table,
                    table_view=widget.tableView_Sinkkaesten,
                    model_attr="model_sinkkaesten",
                    proxy_attr="proxy_model_sinkkaesten",
                )

                for g_col in ["geom", "geop", "geometry"]:
                    geom_index = model.fieldIndex(g_col)
                    if geom_index >= 0:
                        widget.tableView_Sinkkaesten.setColumnHidden(geom_index, True)
                        print(f"[table_models] Sinkkästen Geometriespalte ausgeblendet: {g_col} ({geom_index})")
            else:
                print("[table_models] Keine Sinkkästen-Tabelle gefunden!")

        # ============================================================
        # ENTWÄSSERUNGSRINNEN
        # ============================================================
        if hasattr(widget, "tableView_Rinnen"):
            candidates = [
                "entwaesserungsrinnen",
                "Entwaesserungsrinnen",
                '"entwaesserungsrinnen"',
                '"Entwaesserungsrinnen"',
            ]

            found_table = None
            for cand in candidates:
                if _check_exists(widget, cand):
                    found_table = cand
                    break

            print(f"[table_models] gefundene Entwässerungsrinnen-Tabelle = {found_table}")

            if found_table:
                model, proxy = _load_sql_table_model(
                    widget=widget,
                    table_name=found_table,
                    table_view=widget.tableView_Rinnen,
                    model_attr="model_rinnen",
                    proxy_attr="proxy_model_rinnen",
                )

                for g_col in ["geom_point", "geom_line", "geom", "geometry"]:
                    geom_index = model.fieldIndex(g_col)
                    if geom_index >= 0:
                        widget.tableView_Rinnen.setColumnHidden(geom_index, True)
                        print(f"[table_models] Rinnen Geometriespalte ausgeblendet: {g_col} ({geom_index})")

                header = widget.tableView_Rinnen.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.Fixed)

                fm = header.fontMetrics()
                for col in range(proxy.columnCount()):
                    if widget.tableView_Rinnen.isColumnHidden(col):
                        continue
                    header_text = str(proxy.headerData(col, Qt.Horizontal) or "")
                    width = fm.horizontalAdvance(header_text) + 20
                    widget.tableView_Rinnen.setColumnWidth(col, width)

                widget.tableView_Rinnen.verticalHeader().setVisible(True)
                widget.tableView_Rinnen.setAlternatingRowColors(True)
            else:
                print("[table_models] Keine Tabelle 'entwaesserungsrinnen' gefunden!")

        # ============================================================
        # SONDERBAUWERKE
        # ============================================================
        if hasattr(widget, "tableView_Sonderbauwerke"):
            try:
                print("=== [table_models] SONDERBAUWERKE DEBUG ===")

                tables = [
                    "bauwerke_pw",
                    "bauwerke_rbf",
                    "bauwerke_rkb",
                    "bauwerke_rrb",
                    "bauwerke_rue",
                    "bauwerke_rueb",
                    "bauwerke_vs",
                    "bauwerke_rv",
                ]

                existing_tables = [t for t in tables if _check_exists(widget, t)]
                print(f"[table_models] vorhandene Sonderbauwerke-Tabellen: {existing_tables}")

                for t in existing_tables:
                    _debug_native_count(widget, t)

                if existing_tables:
                    union_parts = [
                        widget.backend.get_sonderbauwerke_union_part(t)
                        for t in existing_tables
                    ]
                    union_sql = " UNION ALL ".join(union_parts)
                else:
                    union_sql = (
                        "SELECT 'Keine Daten' AS name, "
                        "'N/A' AS typ, "
                        "'N/A' AS system, "
                        "'N/A' AS strasse, "
                        "'N/A' AS quelle"
                    )

                print(f"[table_models] Sonderbauwerke SQL = {union_sql}")

                widget.model_sonderbauwerke = QSqlQueryModel(widget)
                widget.model_sonderbauwerke.setQuery(union_sql, widget.db)

                print(
                    f"[table_models] Sonderbauwerke lastError = "
                    f"{widget.model_sonderbauwerke.lastError().text()}"
                )

                _debug_model_state(widget.model_sonderbauwerke, "sonderbauwerke_union")

                widget.model_sonderbauwerke.setHeaderData(0, Qt.Horizontal, "Name")
                widget.model_sonderbauwerke.setHeaderData(1, Qt.Horizontal, "Typ")
                widget.model_sonderbauwerke.setHeaderData(2, Qt.Horizontal, "System")
                widget.model_sonderbauwerke.setHeaderData(3, Qt.Horizontal, "Straße")
                widget.model_sonderbauwerke.setHeaderData(4, Qt.Horizontal, "Quelle")

                widget.proxy_model_sonderbauwerke = QSortFilterProxyModel(widget)
                widget.proxy_model_sonderbauwerke.setSourceModel(widget.model_sonderbauwerke)
                widget.proxy_model_sonderbauwerke.setFilterCaseSensitivity(Qt.CaseInsensitive)

                widget.tableView_Sonderbauwerke.setModel(widget.proxy_model_sonderbauwerke)
                widget.tableView_Sonderbauwerke.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                widget.tableView_Sonderbauwerke.verticalHeader().setVisible(False)
                widget.tableView_Sonderbauwerke.setAlternatingRowColors(True)

                print("=== [table_models] SONDERBAUWERKE ENDE ===")

            except Exception as e:
                print(f"[table_models] Sonderbauwerke EXCEPTION: {str(e)}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"[table_models] load_data_into_tables GLOBAL ERROR -> {e}")
        import traceback
        traceback.print_exc()

    print("========== [table_models] load_data_into_tables ENDE ==========")


def load_data_for_tab(widget, index):
    """
    Optionaler Refresh beim Tabwechsel.
    """
    print(f"[table_models] load_data_for_tab(index={index})")

    try:
        if index == 0 and hasattr(widget, "model_haltungen"):
            widget.model_haltungen.select()
            while widget.model_haltungen.canFetchMore():
                widget.model_haltungen.fetchMore()
            _debug_model_state(widget.model_haltungen, "haltungen")

        elif index == 1 and hasattr(widget, "model_schaechte"):
            widget.model_schaechte.select()
            while widget.model_schaechte.canFetchMore():
                widget.model_schaechte.fetchMore()
            _debug_model_state(widget.model_schaechte, "schaechte")

        elif index == 2 and hasattr(widget, "model_anschlussleitungen"):
            widget.model_anschlussleitungen.select()
            while widget.model_anschlussleitungen.canFetchMore():
                widget.model_anschlussleitungen.fetchMore()
            _debug_model_state(widget.model_anschlussleitungen, "anschlussleitungen")

        elif index == 3 and hasattr(widget, "model_sinkkaesten"):
            widget.model_sinkkaesten.select()
            while widget.model_sinkkaesten.canFetchMore():
                widget.model_sinkkaesten.fetchMore()
            _debug_model_state(widget.model_sinkkaesten, "sinkkaesten")

        elif index == 4 and hasattr(widget, "model_rinnen"):
            widget.model_rinnen.select()
            while widget.model_rinnen.canFetchMore():
                widget.model_rinnen.fetchMore()
            _debug_model_state(widget.model_rinnen, "entwaesserungsrinnen")

        elif index == 5 and hasattr(widget, "model_sonderbauwerke"):
            _debug_model_state(widget.model_sonderbauwerke, "sonderbauwerke_union")

    except Exception as e:
        print(f"[table_models] load_data_for_tab ERROR -> {e}")
        import traceback
        traceback.print_exc()


def update_filter_current_tab(widget):
    """
    Filtert nur den aktuellen Tab nach Text + Spalte.
    """
    filter_text = widget.Search_LineEdit.text()
    selected_column = widget.comboBox_Spalten.currentData()
    if selected_column is None:
        selected_column = -1

    current_index = widget.tab_Overview.currentIndex()

    tab_to_proxy = {
        0: getattr(widget, "proxy_model_haltungen", None),
        1: getattr(widget, "proxy_model_schaechte", None),
        2: getattr(widget, "proxy_model_anschlussleitungen", None),
        3: getattr(widget, "proxy_model_sinkkaesten", None),
        4: getattr(widget, "proxy_model_rinnen", None),
        5: getattr(widget, "proxy_model_sonderbauwerke", None),
    }

    proxy_model = tab_to_proxy.get(current_index)

    print(
        f"[table_models] update_filter_current_tab: "
        f"tab={current_index}, text='{filter_text}', column={selected_column}, proxy={proxy_model}"
    )

    if proxy_model is not None:
        proxy_model.setFilterKeyColumn(selected_column)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterFixedString(filter_text)

        try:
            print(f"[table_models] gefilterte Zeilen = {proxy_model.rowCount()}")
        except Exception as e:
            print(f"[table_models] proxy rowCount ERROR -> {e}")


def filter_data(widget):
    """
    Kompatibilität: alter Slot-Name.
    """
    update_filter_current_tab(widget)


def fill_column_combobox(widget):
    print("[table_models] fill_column_combobox()")

    widget.comboBox_Spalten.clear()
    widget.comboBox_Spalten.addItem("Alle Spalten", -1)

    current_index = widget.tab_Overview.currentIndex()

    if current_index == 0 and hasattr(widget, "model_haltungen"):
        model = widget.model_haltungen
    elif current_index == 1 and hasattr(widget, "model_schaechte"):
        model = widget.model_schaechte
    elif current_index == 2 and hasattr(widget, "model_anschlussleitungen"):
        model = widget.model_anschlussleitungen
    elif current_index == 3 and hasattr(widget, "model_sinkkaesten"):
        model = widget.model_sinkkaesten
    elif current_index == 4 and hasattr(widget, "model_rinnen"):
        model = widget.model_rinnen
    elif current_index == 5 and hasattr(widget, "model_sonderbauwerke"):
        model = widget.model_sonderbauwerke
    else:
        print("[table_models] kein passendes Modell für aktuellen Tab")
        return

    try:
        print(f"[table_models] combobox Modell columnCount = {model.columnCount()}")
        for col in range(model.columnCount()):
            header = model.headerData(col, Qt.Horizontal)
            widget.comboBox_Spalten.addItem(str(header), col)
            print(f"[table_models] combobox add: col={col}, header={header}")
    except Exception as e:
        print(f"[table_models] fill_column_combobox ERROR -> {e}")