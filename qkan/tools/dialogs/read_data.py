import logging
import os
import sqlite3
import time
import typing
from pathlib import Path
from sqlite3 import Connection

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QComboBox, QDialogButtonBox, QPushButton
from qgis.utils import spatialite_connect
from qkan import QKan

from . import QKanDBDialog

if typing.TYPE_CHECKING:
    from qkan.tools.application import QKanTools

logger = logging.getLogger("QKan.tools.dialogs.read_data")

FORM_CLASS_read_data, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_readData.ui")
)

REQUIRED_FIELDS = {
    "schaechte": ["schnam", "xsch", "ysch", "sohlhoehe"],
    "auslaesse": ["schnam", "xsch", "ysch", "sohlhoehe"],
    "speicher": ["schnam", "xsch", "ysch", "sohlhoehe"],
    "haltungen": ["haltnam", "xschob", "yschob", "xschun", "yschun"],
    "pumpen": ["pnam"],
    "wehre": ["wnam"],
}
IMPORT_TYPES = {
    "schnam": "TEXT",
    "xsch": "REAL",
    "ysch": "REAL",
    "sohlhoehe": "REAL",
    "xschob": "REAL",
    "yschob": "REAL",
    "xschun": "REAL",
    "yschun": "REAL",
    "pnam": "TEXT",
    "wnam": "TEXT",
}
CF_TEXT = 1


class ReadDataDialog(QKanDBDialog, FORM_CLASS_read_data):
    button_box: QDialogButtonBox
    cbLayerAuslaesse: QComboBox
    cbLayerHaltungen: QComboBox
    cbLayerPumpen: QComboBox
    cbLayerSchaechte: QComboBox
    cbLayerSpeicher: QComboBox
    cbLayerWehre: QComboBox

    pbPasteAuslaesse: QPushButton
    pbPasteHaltungen: QPushButton
    pbPastePumpen: QPushButton
    pbPasteSchaechte: QPushButton
    pbPasteSpeicher: QPushButton
    pbPasteWehre: QPushButton

    def __init__(self, plugin: "QKanTools", parent=None):
        super().__init__(plugin, parent)

        # Set up the database loader
        self.tf_qkanDB.textChanged.connect(self.reload_database)

        self.other_db: typing.Optional[Connection] = None
        self.temporary_db: typing.Optional[Connection] = None
        self.db_name: typing.Optional[str] = None

        self.pbPasteAuslaesse.clicked.connect(lambda: self.read_clipboard("auslaesse"))
        self.pbPasteHaltungen.clicked.connect(lambda: self.read_clipboard("haltungen"))
        self.pbPastePumpen.clicked.connect(lambda: self.read_clipboard("pumpen"))
        self.pbPasteSchaechte.clicked.connect(lambda: self.read_clipboard("schaechte"))
        self.pbPasteSpeicher.clicked.connect(lambda: self.read_clipboard("speicher"))
        self.pbPasteWehre.clicked.connect(lambda: self.read_clipboard("wehre"))

    def find_compatible_tables(self):
        cursors = []

        if self.other_db:
            cursors.append(self.other_db.cursor())
        if self.temporary_db:
            cursors.append(self.temporary_db.cursor())

        compatible: typing.Dict[str, typing.List[str]] = {
            _: [] for _ in REQUIRED_FIELDS.keys()
        }

        for cursor in cursors:
            # Get all tables
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type="table" AND name NOT LIKE "sqlite_%";
                """
            )

            data = cursor.fetchall()
            table_names = [_[0] for _ in data]

            # Get all columns
            table_columns = {}
            for name in table_names:
                cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO(?);", (name,))
                data = cursor.fetchall()
                table_columns[name] = [_[0] for _ in data]

            # Filter available tables
            for name, fields in table_columns.items():
                for table_name, table_fields in REQUIRED_FIELDS.items():
                    if (
                        name.startswith("idx_")
                        or name.startswith("views_")
                        or name.startswith("virts_")
                    ):
                        continue
                    # Skip table
                    if any(required not in fields for required in table_fields):
                        # logger.debug("Skipping %s for %s", name, table_name)
                        continue

                    compatible.get(table_name, []).append(name)

        # Fill dropdowns
        for dropdown, layers in compatible.items():
            target = self.get_target(dropdown)
            # TODO: Skip dropdowns if they shouldn't be updated

            # Reset dropdown
            target.clear()
            target.addItem("--")

            for idx, layer in enumerate(layers):
                target.addItem(layer)
                # TODO: Add tooltip
                # target.setItemData(idx, layer.source(), Qt.ToolTipRole)

        for cursor in cursors:
            try:
                cursor.close()
            except sqlite3.DatabaseError:
                pass

    def reload_database(self):
        db_name = self.tf_qkanDB.text()
        if not Path(db_name).exists() or db_name == self.db_name:
            return

        logger.info("Reloading database, switching to %s", db_name)

        if self.other_db:
            self.other_db.close()

        try:
            self.other_db = spatialite_connect(
                database=db_name, check_same_thread=False
            )
            self.db_name = db_name
        except sqlite3.DatabaseError:
            # TODO: Show tooltip and mark field red
            logger.exception("Failed to open database")
            return

        self.find_compatible_tables()

    def get_target(self, name: str) -> QComboBox:
        return {
            "auslaesse": self.cbLayerAuslaesse,
            "schaechte": self.cbLayerSchaechte,
            "speicher": self.cbLayerSpeicher,
            "haltungen": self.cbLayerHaltungen,
            "pumpen": self.cbLayerPumpen,
            "wehre": self.cbLayerWehre,
        }[name]

    def run(self):
        """
        TODO: Checkbox to list all tables in dropdowns
        """
        self.tf_qkanDB.setText(QKan.config.database.qkan)

        self.show()
        if self.exec_():
            # TODO: Write the actual import queries
            print("Import here")

    def read_clipboard(self, table_suffix: str):
        data = QgsApplication.clipboard().text()
        parsed_data = []
        if data:
            lines = data.splitlines()
            if len(lines) == 1:
                return

            headers = lines[0].split("\t")
            for header in headers:
                if header not in IMPORT_TYPES:
                    continue

            for row, line in enumerate(lines[1:]):
                parsed_data.append([])
                x = line.split("\t")
                for column, value in enumerate(x):
                    _type = IMPORT_TYPES.get(headers[column], None)
                    if not _type:
                        continue

                    if _type == "REAL":
                        parsed_data[row].append(float(value))
                    elif _type == "TEXT":
                        parsed_data[row].append(value)

            create_types = [
                f"{header} {IMPORT_TYPES.get(header, 'TEXT')}" for header in headers
            ]

            table_name = f"temp{int(time.time()) % 10000}_{table_suffix}"

            sql = f"CREATE TABLE {table_name} ({', '.join(create_types)});"

            if not self.temporary_db:
                self.temporary_db = spatialite_connect(
                    database=":memory:", check_same_thread=False
                )

            # Insert table
            cursor = self.temporary_db.cursor()
            cursor.execute(sql)

            # Insert table data
            for row in parsed_data:
                cursor.execute(
                    f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(create_types))})",
                    row,
                )

            cursor.close()

            self.find_compatible_tables()
