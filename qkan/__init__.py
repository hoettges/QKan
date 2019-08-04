# -*- coding: utf-8 -*-
import datetime
import logging
import os, site, json
import tempfile
from pathlib import Path

from PyQt5.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu


def classFactory(iface):  # pylint: disable=invalid-name
    qkan = QKan(iface)
    return qkan


class QKan:
    instance = None

    # --------------------------------------------------------------------------------------------------
    # Konfigurationsdatei qkan.json lesen
    #

    # Pfad zum Arbeitsverzeichnis sicherstellen
    wordir = os.path.join(site.getuserbase(), u'qkan')

    if not os.path.isdir(wordir):
        os.makedirs(wordir)

    configfil = os.path.join(wordir, u'qkan.json')
    if os.path.exists(configfil):
        with open(configfil, 'r') as fileconfig:
            config = json.loads(fileconfig.read())
    else:
        config = {'epsg': '25832'}  # Projektionssystem
        with open(configfil, 'w') as fileconfig:
            fileconfig.write(json.dumps(config))


    def __init__(self, iface):
        QKan.instance = self

        # Init logging
        self.logger = logging.getLogger('QKan')
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(
            Path(tempfile.gettempdir())
            / "QKan_{}.log".format(datetime.datetime.today().strftime("%Y-%m-%d"))
        )
        stream_handler = logging.StreamHandler()

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(stream_handler)

        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

        # QGIS
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []

        # Plugins
        self.instances = []

        # Translations
        self.translator = QTranslator()
        locale = (QSettings().value("locale/userLocale") or "en")[0:2]
        for _file in (Path(__file__).parent / "i18n").iterdir():
            if _file.name.endswith("_{}.qm".format(locale)):
                self.translator.load(str(_file))
        QCoreApplication.installTranslator(self.translator)

        from .createunbeffl import application as createunbeffl
        from .importdyna import application as importdyna
        from .exportdyna import application as exportdyna
        from .linkflaechen import application as linkflaechen
        from .tools import application as tools

        self.plugins = [
            createunbeffl.CreateUnbefFl(iface),
            importdyna.ImportFromDyna(iface),
            exportdyna.ExportToKP(iface),
            linkflaechen.LinkFl(iface),
            tools.QKanTools(iface),
        ]

        actions = self.iface.mainWindow().menuBar().actions()
        self.menu = None
        for menu in actions:
            if menu.text() == "QKan":
                self.menu = menu.menu()
                self.menu_action = menu
                break

        self.toolbar = self.iface.addToolBar("QKan")
        self.toolbar.setObjectName("QKan")


    def initGui(self):
        # Create and insert QKan menu after the 3rd menu
        if self.menu is None:
            self.menu = QMenu("QKan", self.iface.mainWindow().menuBar())

            actions = self.iface.mainWindow().menuBar().actions()
            prepend = actions[3] if len(actions) > 3 else None

            self.menu_action = (
                self.iface.mainWindow().menuBar().insertMenu(prepend, self.menu)
            )

        # Calls initGui on all known QKan plugins
        for plugin in self.plugins:
            plugin.initGui()

        self.sort_actions()

    def sort_actions(self):
        # Finally sort all actions
        self.actions.sort(key=lambda x: x.text().lower())
        self.menu.clear()
        self.menu.addActions(self.actions)

    def unload(self):
        from qgis.utils import unloadPlugin

        # Shutdown logger
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        # Unload all other instances
        for instance in self.instances:
            print("Unloading ", instance.name)
            if not unloadPlugin(instance.name):
                print("Failed to unload plugin!")

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

        # Unload translator
        QCoreApplication.removeTranslator(self.translator)

        # Call unload on all loaded plugins
        for plugin in self.plugins:
            plugin.unload()

    def register(self, instance):
        self.instances.append(instance)

        self.plugins += instance.plugins

    def unregister(self, instance):
        self.instances.remove(instance)

        for plugin in instance.plugins:
            self.plugins.remove(plugin)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
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
            self.menu.addAction(action)

        self.actions.append(action)

        return action

    def saveconfig(self):
        """Write config to json-File"""
        with open(QKan.configfil, 'w') as fileconfig:
            fileconfig.write(json.dumps(QKan.config))
        # self.logger.debug('QKan.saveconfig: id(QKan): {0:}\n\t\tQKan.config['epsg']: {1:}'.format(id(QKan), QKan.config['epsg']))
