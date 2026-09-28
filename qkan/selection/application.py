from qgis.gui import QgisInterface
from PyQt6.QtWidgets import QToolBar, QToolButton, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin
from qkan.utils import QkanUserError, QkanAbortError

from qkan.utils import get_logger
from qkan.tools.qkan_utils import get_database_QKan
logger = get_logger("QKan")

from ._selection import Select
from .application_dialog import SelectionDialog

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401

class Selection(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.select_dlg = SelectionDialog(default_dir=self.default_dir, tr=self.tr)

        self.toolbar = None
        self.auswahl = []


    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_import = ":/plugins/qkan/selection/res/icon_selection.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Auswahl erweitern / Netzverfolgung"),
            toolbar='QKan-Allgemein',
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        toolbar_name = 'QKan-Allgemein'
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, toolbar_name)
        # Abbruch für automatisierte Tests
        if self.toolbar is None:
            return

        action_to_remove = None
        for action in self.toolbar.actions():
            if action.text() == "Auswahl erweitern / Netzverfolgung":
                action_to_remove = action
                break

        if action_to_remove:
            self.toolbar.removeAction(action_to_remove)

        dropdown_button = QToolButton()
        icon = QIcon(icon_import)
        dropdown_button.setIcon(icon)
        # dropdown_button.setText("Mein Button")  # Text des Buttons
        dropdown_button.setToolTip("Auswahl erweitern / Netzverfolgung")  # Tooltip
        dropdown_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        dropdown_button.setMenu(QMenu())

        dropdown_menu = dropdown_button.menu()

        action = QAction("Objekte oberhalb", dropdown_menu)
        action.setStatusTip("Bitte einen Schacht auswählen")
        action.triggered.connect(self.oberhalb_clicked)
        dropdown_menu.addAction(action)

        action1 = QAction("Objekte unterhalb", dropdown_menu)
        action1.setStatusTip("Bitte einen Schacht auswählen")
        action1.triggered.connect(self.unterhalb_clicked)
        dropdown_menu.addAction(action1)

        action2 = QAction("längster Fließweg oberhalb", dropdown_menu)
        action2.setStatusTip("Bitte einen Schacht auswählen")
        action2.triggered.connect(self.laengster_clicked)
        dropdown_menu.addAction(action2)

        action3 = QAction("kürzester Weg", dropdown_menu)
        action3.setStatusTip("Bitte zwei Haltungen oder zwei Schächte wählen")
        action3.triggered.connect(self.kuerzester_clicked)
        dropdown_menu.addAction(action3)

        action4 = QAction("Objekte innerhalb Teilgebiet", dropdown_menu)
        action4.setStatusTip("Bitte Teilgebiete wählen")
        action4.triggered.connect(self.teilgebiet_clicked)
        dropdown_menu.addAction(action4)

        self.toolbar.addWidget(dropdown_button)

    def oberhalb_clicked(self):
        self.auswahl = []
        self.auswahl.append("Objekte oberhalb")
        self.run()

    def unterhalb_clicked(self):
        self.auswahl = []
        self.auswahl.append("Objekte unterhalb")
        self.run()
        print('Test')

    def laengster_clicked(self):
        self.auswahl = []
        self.auswahl.append("längster Fließweg oberhalb")
        self.run()

    def kuerzester_clicked(self):
        self.auswahl = []
        self.auswahl.append("kürzester Weg")
        self.run()

    def teilgebiet_clicked(self):
        self.auswahl = []
        self.auswahl.append("Objekte innerhalb Teilgebiet")
        self.run()


    def unload(self) -> None:
        self.select_dlg.close()


    def run(self) -> None:
        get_database_QKan()
        database_qkan, epsg = QKan.config.database.qkan, QKan.config.epsg
        if not database_qkan:
            logger.error_data(
                "selection.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            raise QkanAbortError

        with DBConnection(
                dbname=database_qkan, epsg=epsg
        ) as db_qkan:
            if not db_qkan.connected:
                logger.error_code(
                    "selection.application: Datenbank konnte nicht geöffnet werden. Abbruch!"
                )
                raise QkanAbortError

            imp = Select(
                db_qkan, self.auswahl[0])
            try:
                imp.run()
            except QkanUserError as e:
                # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
                logger.debug(f"Anwenderfehler bei Tool Auswahl erweitern/Netzverfolgung: {e}")
            except Exception as e:
                logger.error_code(f"Fehler bei Tool Auswahl erweitern/Netzverfolgung: {e}")
                raise QkanAbortError

