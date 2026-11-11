"""Sichtbarkeit und Reihenfolge der QKan-Werkzeugleisten.

Bei normalen Aktionen entfernt die Verwaltung nur den Toolbar-Eintrag:
Die gleiche QAction bleibt im Hauptmenue benutzbar. QWidgetAction (z. B.
die Netzverfolgungs-Dropdown-Schaltflaeche) wird dagegen via setVisible
versteckt, damit ihr Widget beim Entfernen nicht zerstoert wird.
"""
from qgis.PyQt.QtCore import Qt, QSettings, QSignalBlocker, QObject, QEvent, QTimer
from qgis.PyQt.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QMenu, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidgetAction,
)


class PersistentCheckMenu(QMenu):
    """Laesst nur Toolbar-Sichtbarkeitsschalter nach einem Klick offen.

    QMenu schliesst beim normalen Klick auf eine Aktion. Hier wird ausschliesslich
    bei Checkboxen und gekennzeichneten Sammelschaltern der Klick selbst
    behandelt. Alle anderen Befehle behalten das Standardverhalten von QMenu.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pressed_action = None

    @staticmethod
    def _keeps_open(action):
        return bool(action and action.isEnabled() and not action.isSeparator()
                    and action.menu() is None
                    and (action.isCheckable() or action.property("qkan_keep_open")))

    def mousePressEvent(self, event):
        self._pressed_action = (self.actionAt(event.pos())
                                if event.button() == Qt.LeftButton else None)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        action = self.actionAt(event.pos())
        pressed = self._pressed_action
        self._pressed_action = None
        if (event.button() == Qt.LeftButton and self._keeps_open(action)
                and (pressed is None or pressed is action)):
            # Ohne QMenu.mouseReleaseEvent schliesst Qt die Menue-Kette nicht.
            # QAction.trigger() aktualisiert checkable/toggled und ruft Slots auf.
            action.trigger()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            action = self.activeAction()
            if self._keeps_open(action):
                action.trigger()
                event.accept()
                return
        super().keyPressEvent(event)


class ToolbarManager(QObject):
    PREFIX = "QKan"

    def __init__(self, qkan):
        parent = qkan.iface.mainWindow()
        super().__init__(parent)
        self.parent = parent
        self.qkan = qkan
        self.toolbars = {bar.objectName(): bar for bar in (
            getattr(qkan, name, None) for name in
            ("toolbar", "toolbar_2", "toolbar_3", "toolbar_4", "toolbar_5", "toolbar_6")
        ) if bar is not None}
        self._ready = False
        self._created_bars = set()
        self.settings = QSettings()
        self._dirty = True
        self._watched = set()
        self._new_action_check_pending = False
        self._other_menu = None
        self._other_actions = {}  # Aktionen, die QKan bisher keinem Hauptmenue zuordnet
        self.entries = {}  # toolbar objectName -> ALLE Aktionen, auch ausgeblendete
        self.titles = {}   # Tooltip der QWidgetAction geht beim Ausblenden nicht verloren
        self.menu = None
        self.menu_toggles = []
        self.group_toggles = []
        self._group_menus = []
        # Nur von UNS wegen fehlender Icons ausgeblendete Leisten wieder anzeigen.
        # Manuell in QGIS ausgeblendete Werkzeugleisten bleiben unangetastet.
        self._hidden_empty_toolbars = set()

    def _name(self, bar):
        return bar.objectName()

    def title(self, bar, action):
        if action in self.titles:
            return self.titles[action]
        widget = bar.widgetForAction(action)
        title = (action.text() or (widget.toolTip() if widget else "")
                 or action.toolTip() or action.objectName() or "Unbenanntes Werkzeug")
        self.titles[action] = title
        return title

    def _key(self, bar, action):
        return f"{self.PREFIX}/toolbarButtons/{self._name(bar)}/{self.title(bar, action)}"

    def _ordered_key(self, bar):
        return f"{self.PREFIX}/toolbarOrder/{self._name(bar)}"

    def _enabled(self, bar, action):
        return self.settings.value(self._key(bar, action), True, type=bool)

    def _action_is_visible(self, bar, action):
        if isinstance(action, QWidgetAction):
            return action.isVisible()
        return action in bar.actions()

    def _set_visible(self, bar, action, enabled, save=True, sync_toolbar=True):
        """Tatsaechlich die Toolbar aendern, nicht nur das dazugehoerige Widget."""
        enabled = bool(enabled)
        if isinstance(action, QWidgetAction):
            # addWidget -> QWidgetAction; QWidget.setVisible ist laut Qt wirkungslos.
            action.setVisible(enabled)
        elif enabled and action not in bar.actions():
            # In der festgelegten Reihenfolge vor der naechsten sichtbaren Aktion.
            items = self.entries[self._name(bar)]
            idx = items.index(action)
            next_visible = next((a for a in items[idx + 1:] if a in bar.actions()), None)
            if next_visible is None:
                bar.addAction(action)
            else:
                bar.insertAction(next_visible, action)
        elif not enabled and action in bar.actions():
            # Entfernt nur die Darstellung in der Leiste; Menue-Aktion bleibt aktiv.
            bar.removeAction(action)
        if save:
            self.settings.setValue(self._key(bar, action), enabled)
        if sync_toolbar:
            self._sync_toolbar_visibility(bar)

    def _sync_toolbar_visibility(self, bar):
        """Blendet eine QKan-Leiste ohne aktivierte Buttons samt Griff aus.

        Maßgeblich ist der gespeicherte Schalterzustand, nicht isVisible():
        Ein bereits ausgeblendetes QToolBar darf die Statusberechnung nicht
        selbst beeinflussen. Manuell in QGIS versteckte Leisten werden nicht
        ungefragt wieder eingeblendet.
        """
        entries = self.entries.get(self._name(bar), ())
        has_buttons = any(self._enabled(bar, action) for action in entries)
        if not has_buttons:
            # Auch bereits vom QGIS-Layout versteckte leere Leisten merken:
            # Beim spaeteren Aktivieren eines Icons muss die Gruppe erscheinen.
            self._hidden_empty_toolbars.add(bar)
            if bar.isVisible():
                bar.hide()
        elif bar in self._hidden_empty_toolbars:
            self._hidden_empty_toolbars.discard(bar)
            bar.show()

    def eventFilter(self, obj, event):
        # Spezial-Buttons kommen in QKan auch per toolbar.addWidget() hinzu.
        if event.type() == QEvent.ActionAdded and obj in self.toolbars.values():
            if not self._new_action_check_pending:
                self._new_action_check_pending = True
                QTimer.singleShot(0, self._on_toolbar_changed)
        return False

    def _on_toolbar_changed(self):
        self._new_action_check_pending = False
        self.discover()

    def _watch_toolbar(self, bar):
        if bar not in self._watched:
            bar.installEventFilter(self)
            self._watched.add(bar)

    def register_action(self, action, toolbar_name=None,
                        add_to_menu=True, add_to_toolbar=True):
        """QKan.add_action bleibt unveraendert nutzbar; alle Gruppen automatisch.

        Bekannte Leisten sind bereits durch QKan gefuellt. Falls ein neues
        Modul einen neuen Toolbar-Namen verwendet, legt nur dieser Manager
        die fehlende Leiste an. Ein zweiter Registrierungsschritt entfällt.
        """
        if add_to_toolbar and toolbar_name:
            bar = self.toolbars.get(toolbar_name)
            if bar is None:
                bar = self.qkan.iface.addToolBar(toolbar_name)
                bar.setObjectName(toolbar_name)
                self.toolbars[toolbar_name] = bar
                self._created_bars.add(bar)
            self._watch_toolbar(bar)
            if action not in bar.actions():
                bar.addAction(action)
            self._register_new(bar, action)
            if self._ready:
                self._sync_toolbar_visibility(bar)

        # Nach der ersten Menue-Sortierung werden spaet hinzukommende Aktionen
        # unter Weitere Werkzeuge / Toolbar-Gruppe eingeordnet.
        if self._ready and add_to_menu and self.qkan.menu is not None:
            if action in self.qkan.menu.actions():
                self.qkan.menu.removeAction(action)
            self.attach_missing_actions(self.qkan.menu, [action])

    def activate(self):
        """Nach dem bestehenden QKan.sort_actions() genau einmal aktivieren."""
        if self._ready:
            return
        self._ready = True
        self.discover()
        self.add_menu(self.qkan.menu)
        self.attach_missing_actions(self.qkan.menu, self.qkan.actions)
        self.qkan.menu.aboutToShow.connect(self._refresh_missing_actions)

    def _refresh_missing_actions(self):
        # Keine manuellen Modul-Listen: auch Aktionen aus PLUGIN_LIST erfasst.
        self.attach_missing_actions(self.qkan.menu, self.qkan.actions)

    def _register_new(self, bar, action):
        key = self._name(bar)
        entries = self.entries.setdefault(key, [])
        if action.isSeparator() or action in entries:
            return False
        self.title(bar, action)
        entries.append(action)
        self._dirty = True
        self._apply_saved_order(bar)
        self._set_visible(bar, action, self._enabled(bar, action),
                          save=False, sync_toolbar=False)
        return True

    def discover(self):
        """Neue registrierte Aktionen erfassen; keine Menues neu zeichnen."""
        for bar in list(self.toolbars.values()):
            self._watch_toolbar(bar)
            for action in list(bar.actions()):
                self._register_new(bar, action)
            self._sync_toolbar_visibility(bar)

    def _apply_saved_order(self, bar):
        entries = self.entries[self._name(bar)]
        wanted = self.settings.value(self._ordered_key(bar), [])
        if isinstance(wanted, str):
            wanted = [wanted]
        if not isinstance(wanted, (list, tuple)) or not wanted:
            return
        entries.sort(key=lambda a: wanted.index(self.title(bar, a))
                     if self.title(bar, a) in wanted else len(wanted))
        self._reposition(bar)

    def _reposition(self, bar):
        """Normale QAction umstellen; Custom-Widget-Instanzen nicht entfernen."""
        entries = self.entries[self._name(bar)]
        for idx in range(len(entries) - 1, -1, -1):
            action = entries[idx]
            if isinstance(action, QWidgetAction) or action not in bar.actions():
                continue
            following = next((a for a in entries[idx + 1:] if a in bar.actions()), None)
            if following is not None:
                # Positioniert die Aktion direkt vor dem naechsten Wunsch-Element.
                bar.insertAction(following, action)
            elif bar.actions() and bar.actions()[-1] is not action:
                # Nur regulaere QAction entfernen: kein Widget-Verlust.
                bar.removeAction(action)
                bar.addAction(action)

    def _all(self):
        self.discover()
        for bar in list(self.toolbars.values()):
            for action in self.entries.get(self._name(bar), []):
                yield bar, action

    def set_all(self, enabled, bar_only=None):
        # Gruppen nur einmal nach dem Umschalten aktualisieren; kein Flackern.
        affected = set()
        for bar, action in self._all():
            if bar_only is None or bar is bar_only:
                self._set_visible(bar, action, enabled, sync_toolbar=False)
                affected.add(bar)
        for bar in affected:
            self._sync_toolbar_visibility(bar)
        self._sync_menu_checks()

    def _toggle_one(self, bar, action, enabled):
        self._set_visible(bar, action, enabled)
        self._sync_menu_checks()

    def _sync_menu_checks(self):
        """Live-Checkboxen pflegen, ohne toggled-Signale erneut auszufuehren."""
        for bar, action, toggle in self.menu_toggles:
            with QSignalBlocker(toggle):
                toggle.setChecked(self._enabled(bar, action))
        for bar, toggle in self.group_toggles:
            entries = self.entries.get(self._name(bar), [])
            with QSignalBlocker(toggle):
                toggle.setChecked(bool(entries) and all(
                    self._enabled(bar, action) for action in entries))

    def close(self):
        """Eventfilter der Toolbar-Verwaltung beim Entladen entfernen."""
        for bar in list(self._watched):
            try:
                bar.removeEventFilter(self)
            except RuntimeError:
                pass
        self._watched.clear()
        self._hidden_empty_toolbars.clear()
        for bar in list(self._created_bars):
            self.qkan.iface.mainWindow().removeToolBar(bar)
            bar.deleteLater()
        self._created_bars.clear()

    def add_menu(self, root_menu):
        self.menu = PersistentCheckMenu("Werkzeugleisten anpassen", root_menu)
        root_menu.addMenu(self.menu)
        self.menu.aboutToShow.connect(self.refresh_menu)
        self.refresh_menu()
        return self.menu

    def refresh_menu(self):
        # Kein periodischer / redundanter Menue-Neuaufbau.
        self.discover()
        if not self._dirty:
            self._sync_menu_checks()
            return
        self._dirty = False
        menu = self.menu
        # Qt gibt extern angelegte Untermenues bei QMenu.clear() nicht frei.
        for old_group in self._group_menus:
            old_group.deleteLater()
        self._group_menus.clear()
        if self._other_menu is not None:
            self._other_menu.deleteLater()
            self._other_menu = None
        menu.clear()
        self.menu_toggles.clear()
        self.group_toggles.clear()
        menu.addAction("Mehrere Werkzeuge auswählen…", lambda checked=False: self.open_dialog())
        menu.addSeparator()
        for label, state in (("Alle Icons anzeigen", True),
                             ("Alle Icons ausblenden", False)):
            bulk_action = menu.addAction(label, lambda checked=False, value=state: self.set_all(value))
            bulk_action.setProperty("qkan_keep_open", True)
        menu.addSeparator()
        for bar in list(self.toolbars.values()):
            entries = self.entries.get(self._name(bar), [])
            if not entries:
                continue
            group = PersistentCheckMenu(bar.windowTitle().replace("QKan-", ""), menu)
            menu.addMenu(group)
            self._group_menus.append(group)
            all_enabled = all(self._enabled(bar, a) for a in entries)
            group_toggle = group.addAction("Ganze Gruppe anzeigen")
            group_toggle.setCheckable(True)
            group_toggle.setChecked(all_enabled)
            self.group_toggles.append((bar, group_toggle))
            group_toggle.toggled.connect(lambda state, b=bar: self.set_all(state, b))
            group.addAction("Reihenfolge ändern…", lambda checked=False, b=bar: self.reorder(b))
            group.addSeparator()
            for action in entries:
                toggle = group.addAction(self.title(bar, action))
                toggle.setIcon(action.icon())
                toggle.setCheckable(True)
                toggle.setChecked(self._enabled(bar, action))
                self.menu_toggles.append((bar, action, toggle))
                toggle.toggled.connect(lambda state, b=bar, a=action:
                                       self._toggle_one(b, a, state))

        # Neue, noch nicht von sort_actions() einsortierte Werkzeuge werden
        # ausschliesslich im bestehenden Menue "Werkzeugleisten anpassen" gezeigt.
        if self._other_actions:
            self._other_menu = menu.addMenu("Weitere Werkzeuge")
            groups = {}
            for action, group_name in self._other_actions.items():
                group = groups.get(group_name)
                if group is None:
                    group = self._other_menu.addMenu(group_name)
                    groups[group_name] = group
                group.addAction(action)

    def attach_missing_actions(self, root_menu, actions):
        """Unbekannte neue Modulaktionen automatisch im QKan-Menue anbieten.

        Die bisherige sort_actions()-Zuordnung bleibt unangetastet.
        Neue Eintraege erscheinen unter Werkzeugleisten anpassen /
        Weitere Werkzeuge / Toolbar-Gruppe.
        """
        def known(menu):
            result = set()
            for item in menu.actions():
                result.add(item)
                nested = item.menu()
                if nested is not None:
                    result.update(known(nested))
            return result

        # Bei der ersten Benutzung werden nur fehlende Elemente angelegt.
        seen = known(root_menu)
        # Bereits in einer Werkzeugleiste verwaltete Aktionen nicht doppelt
        # unter "Weitere Werkzeuge" als Menuebefehl anzeigen.
        toolbar_actions = {a for items in self.entries.values() for a in items}
        to_add = [a for a in actions
                  if a not in seen
                  and a not in toolbar_actions
                  and a.property("_qkan_menu_enabled") is not False]
        if not to_add:
            return
        for action in to_add:
            bar = next((bar for bar in self.toolbars.values()
                        if action in self.entries.get(self._name(bar), [])), None)
            group_name = (bar.windowTitle().replace("QKan-", "")
                          if bar is not None else "Weitere")
            self._other_actions[action] = group_name
        # Den Eintrag in der bestehenden Menueverwaltung neu aufbauen.
        # Es wird dabei kein weiterer QKan-Hauptmenuepunkt angelegt.
        self._dirty = True
        self.refresh_menu()

    def open_dialog(self):
        """Checkboxen fuer viele Werkzeuge auf einmal, Gruppen mit 3-Zustand."""
        self.discover()
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("QKan – Werkzeugleisten anpassen")
        dialog.resize(620, 600)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Werkzeuge und ganze Gruppen an- oder abwählen."
                                " Mit Übernehmen werden alle Änderungen ausgeführt."))
        tree = QTreeWidget(dialog)
        tree.setHeaderLabels(["Werkzeugleiste / Werkzeug"])
        tree.setAlternatingRowColors(True)
        layout.addWidget(tree)
        mapping = []
        for bar in list(self.toolbars.values()):
            entries = self.entries.get(self._name(bar), [])
            if not entries:
                continue
            group = QTreeWidgetItem(tree, [bar.windowTitle().replace("QKan-", "")])
            group.setFlags(group.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            for action in entries:
                child = QTreeWidgetItem(group, [self.title(bar, action)])
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0, Qt.Checked if self._enabled(bar, action) else Qt.Unchecked)
                mapping.append((bar, action, child))
            group.setExpanded(True)

        buttons_row = QHBoxLayout()
        show = QPushButton("Alle auswählen", dialog)
        hide = QPushButton("Alle abwählen", dialog)
        buttons_row.addWidget(show)
        buttons_row.addWidget(hide)
        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)

        def check_all(state):
            for i in range(tree.topLevelItemCount()):
                tree.topLevelItem(i).setCheckState(0, state)

        show.clicked.connect(lambda: check_all(Qt.Checked))
        hide.clicked.connect(lambda: check_all(Qt.Unchecked))

        def apply():
            affected = set()
            for bar, action, child in mapping:
                enabled = child.checkState(0) == Qt.Checked
                if self._enabled(bar, action) != enabled or self._action_is_visible(bar, action) != enabled:
                    self._set_visible(bar, action, enabled, sync_toolbar=False)
                    affected.add(bar)
            for bar in affected:
                self._sync_toolbar_visibility(bar)
            self.settings.sync()
            self._sync_menu_checks()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel |
                                   QDialogButtonBox.Apply, parent=dialog)
        buttons.accepted.connect(lambda: (apply(), dialog.accept()))
        buttons.rejected.connect(dialog.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(apply)
        layout.addWidget(buttons)
        dialog.exec_()

    def reorder(self, bar):
        self.discover()
        entries = self.entries.get(self._name(bar), [])
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(f"Reihenfolge – {bar.windowTitle()}")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Werkzeuge ziehen, um die Reihenfolge zu ändern:"))
        listing = QListWidget(dialog)
        listing.setDragDropMode(QAbstractItemView.InternalMove)
        for idx, action in enumerate(entries):
            item = QListWidgetItem(self.title(bar, action))
            item.setData(Qt.UserRole, idx)
            listing.addItem(item)
        layout.addWidget(listing)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                   parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec_() != QDialog.Accepted:
            return
        ordered = [entries[listing.item(i).data(Qt.UserRole)] for i in range(listing.count())]
        self.entries[self._name(bar)] = ordered
        self._reposition(bar)
        self.settings.setValue(self._ordered_key(bar), [self.title(bar, a) for a in ordered])
