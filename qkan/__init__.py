# -*- coding: utf-8 -*-
import os

# noinspection PyPep8Naming
from PyQt4.QtGui import QIcon, QAction, QMenu


def classFactory(iface):  # pylint: disable=invalid-name
    dummy = Dummy(iface)
    return dummy


class Dummy:
    instance = None

    def __init__(self, iface):
        from createunbeffl import application as createunbeffl
        from importhe import application as importhe
        from exporthe import application as exporthe
        from ganglinienhe import application as ganglinienhe
        from linkflaechen import application as linkflaechen
        self.plugins = [
            createunbeffl.CreateUnbefFl(iface),
            importhe.ImportFromHE(iface),
            exporthe.ExportToHE(iface),
            ganglinienhe.Application(iface),
            linkflaechen.LinkFl(iface)
        ]
        Dummy.instance = self

        # QGIS
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []

        actions = self.iface.mainWindow().menuBar().actions()
        self.menu = None
        for menu in actions:
            if menu.text() == 'QKan':
                self.menu = menu.menu()
                self.menu_action = menu
                break

        self.toolbar = self.iface.addToolBar('QKan')
        self.toolbar.setObjectName('QKan')

    def initGui(self):
        # Create and insert QKan menu after the 3rd menu
        if self.menu is None:
            self.menu = QMenu('QKan', self.iface.mainWindow().menuBar())

            actions = self.iface.mainWindow().menuBar().actions()
            prepend = actions[3]
            self.menu_action = self.iface.mainWindow().menuBar().insertMenu(prepend, self.menu)

        # Calls initGui on all known QKan plugins
        for plugin in self.plugins:
            plugin.initGui()

        # Finally sort all actions
        self.actions.sort(key=lambda x: x.text().lower())
        self.menu.clear()
        self.menu.addActions(self.actions)

    def unload(self):
        # Remove entries from own menu
        for action in self.menu.actions():
            self.menu.removeAction(action)

        # Remove entries from Plugin menu and toolbar
        for action in self.actions:
            self.iface.removeToolBarIcon(action)

        # Remove the toolbar
        del self.toolbar

        # Remove menu
        self.iface.mainWindow().menuBar().removeAction(self.menu_action)

        # Call unload on all loaded plugins
        for plugin in self.plugins:
            plugin.unload()

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.__actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.actions += [action]  # Append action
            self.menu.addAction(action)

        self.actions.append(action)

        return action
