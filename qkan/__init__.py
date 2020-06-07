# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import tempfile
import typing
from pathlib import Path

import qgis
from PyQt5.QtCore import QCoreApplication, QSettings, QStandardPaths, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QListWidget, QMenu, QWidget
from qgis.core import QgsProject
from qgis.utils import pluginDirectory

from .config import Config


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    qkan = QKan(iface)
    return qkan


# TODO: getOpenFilename/getSaveFilename(dialog, title, dir=self.default_dir, extensions)
class QKan:
    instance = None  # type: QKan
    config: typing.Optional[Config] = None
    template_dir: str = None

    def __init__(self, iface: qgis.gui.QgisInterface):
        QKan.instance = self

        # Init logging
        self.logger = logging.getLogger("QKan")
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.log_path = Path(tempfile.gettempdir()) / "QKan_{}.log".format(
            datetime.datetime.today().strftime("%Y-%m-%d")
        )
        file_handler = logging.FileHandler(self.log_path)
        # stream_handler = logging.StreamHandler()

        file_handler.setFormatter(formatter)
        # stream_handler.setFormatter(formatter)

        file_handler.setLevel(logging.DEBUG)
        # stream_handler.setLevel(logging.DEBUG)

        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        # self.logger.addHandler(stream_handler)

        # Init config
        try:
            QKan.config = Config.load()
        except (json.JSONDecodeError, OSError):
            self.logger.error("Failed to read config file.", exc_info=True)
            QKan.config = Config()
            QKan.config.save()

        # QGIS
        self.iface = iface
        self.actions = []

        # Set default template directory
        QKan.template_dir = os.path.join(pluginDirectory("qkan"), "templates")

        # Plugins
        self.instances = []

        # Translations
        self.translator = QTranslator()
        locale = (QSettings().value("locale/userLocale") or "en")[0:2]
        for _file in (Path(__file__).parent / "i18n").iterdir():
            if _file.name.endswith("_{}.qm".format(locale)):
                self.translator.load(str(_file))
        QCoreApplication.installTranslator(self.translator)

        from .createunbeffl import CreateUnbefFl
        from .importdyna import ImportFromDyna
        from .swmmporter import ImportFromSWMM
        from .exportdyna import ExportToKP
        from .linkflaechen import LinkFl
        from .tools import QKanTools
        from .exporthe8 import ExportToHE8
        from .xmlporter import XmlPorter

        # from .surfaceTools import SurfaceTools

        self.plugins = [
            CreateUnbefFl(iface),
            ImportFromDyna(iface),
            ImportFromSWMM(iface),
            ExportToKP(iface),
            LinkFl(iface),
            QKanTools(iface),
            ExportToHE8(iface),
            XmlPorter(iface),
            # SurfaceTools(iface),
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

    # noinspection PyPep8Naming
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

    def register(self, instance: typing.ClassVar):
        self.instances.append(instance)

        self.plugins += instance.plugins

    def unregister(self, instance: typing.ClassVar):
        self.instances.remove(instance)

        for plugin in instance.plugins:
            self.plugins.remove(plugin)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: typing.Callable,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str = None,
        whats_this: str = None,
        parent: QWidget = None,
    ) -> QAction:
        """Add a toolbar icon to the toolbar/menu.

        :param icon_path:       Path to the icon for this action. Can be a resource
                                path (e.g. ':/plugins/foo/bar.png') or a normal
                                file system path.
        :param text:            Text that should be shown in menu items for this action.
        :param callback:        Function to be called when the action is triggered.
        :param enabled_flag:    A flag indicating if the action should be enabled
                                by default. Defaults to True.
        :param add_to_menu:     Flag indicating whether the action should also
                                be added to the menu. Defaults to True.
        :param add_to_toolbar:  Flag indicating whether the action should also
                                be added to the toolbar. Defaults to True.
        :param status_tip:      Optional text to show in a popup when mouse pointer
                                hovers over the action.
        :param whats_this:      Optional text to show in the status bar when the
                                mouse pointer hovers over the action.
        :param parent:          Parent widget for the new action. Defaults None.
        :returns:               The action that was created. Note that the action is also
                                added to self.actions.
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


def get_default_dir() -> str:
    """
    A helper method that returns the path of the currently opened project
    *or* the user's default directory
    """

    # noinspection PyArgumentList
    project_path = QgsProject.instance().fileName()
    if project_path:
        return str(Path(project_path).parent.absolute())
    else:
        return str(
            Path(
                QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[-1]
            ).absolute()
        )


def list_selected_items(list_widget: QListWidget) -> typing.List[str]:
    """
    Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

    :param list_widget: Liste aller Widgets
    """

    return [_.text() for _ in list_widget.selectedItems()]
