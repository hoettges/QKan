import logging
import os
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor

import typing
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QPushButton,
)
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
        self.db_name: typing.Optional[str] = None
        self.cursor: typing.Optional[Cursor] = None

    def reload_database(self):
        db_name = self.tf_qkanDB.text()
        if not Path(db_name).exists() or db_name == self.db_name:
            return

        logger.info("Reloading database, switching to %s", db_name)

        if self.other_db:
            self.cursor.close()
            self.other_db.close()

        try:
            self.other_db = spatialite_connect(
                database=db_name, check_same_thread=False
            )
            self.cursor = self.other_db.cursor()
            self.db_name = db_name
        except sqlite3.DatabaseError:
            # TODO: Show tooltip and mark field red
            logger.exception("Failed to open database")
            return

        compatible: typing.Dict[str, typing.List[str]] = {
            _: [] for _ in REQUIRED_FIELDS.keys()
        }

        # Get all tables
        self.cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type="table" AND name NOT LIKE "sqlite_%";
            """
        )

        data = self.cursor.fetchall()
        table_names = [_[0] for _ in data]

        # Get all columns
        table_columns = {}
        for name in table_names:
            self.cursor.execute(f'SELECT name FROM PRAGMA_TABLE_INFO("{name}");')
            data = self.cursor.fetchall()
            table_columns[name] = [_[0] for _ in data]

        # Filter available tables
        for name, fields in table_columns.items():
            for table_name, table_fields in REQUIRED_FIELDS.items():
                # Skip table
                if any(required not in fields for required in table_fields):
                    continue

                compatible.get(table_name, []).append(name)

        # Fill dropdowns
        for dropdown, layers in compatible.items():
            target = self.get_target(dropdown)
            target.clear()
            for idx, layer in enumerate(layers):
                target.addItem(layer)
                # TODO: Add tooltip
                # target.setItemData(idx, layer.source(), Qt.ToolTipRole)

    def get_target(self, name: str):
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
        TODO: Paste -> Insert table into temporary table in current database
              or temporary DB
             `CREATE TEMPORARY TABLE temp_table1( name TEXT );`
        """
        self.tf_qkanDB.setText(QKan.config.database.qkan)

        self.show()
        if self.exec_():
            # TODO: Write the actual import queries
            print("Import here")
