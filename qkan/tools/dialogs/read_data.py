import logging
import os
from sqlite3 import Connection
from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast, Any, Callable

from qgis.core import QgsApplication, QgsProject
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget
from qkan.database.dbfunc import DBConnection
from qkan.tools.dialogs import QKanDBDialog
from qgis.core import Qgis

from qkan.database.qkan_utils import fehlermeldung, get_database_QKan, get_qkanlayer_attributes
from qkan import QKan
from . import QKanDBDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

logger = logging.getLogger("QKan.tools.dialogs.read_data")

FORM_CLASS_read_data, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_readData.ui")
)

REQUIRED_FIELDS = {
    "schaechte": ["schnam", "xsch", "ysch", "sohlhoehe"],
    "auslaesse": ["schnam", "xsch", "ysch", "sohlhoehe"],
    "speicher": ["schnam", "xsch", "ysch", "sohlhoehe"],
    "haltungen": ["haltnam", "schoben", "schunten"],
    "pumpen": ["pnam", "schoben", "schunten"],
    "wehre": ["wnam", "schoben", "schunten"],
}

SCHACHT_TYPES = {
    "schaechte": "Schacht",
    "speicher": "Speicher",
    "auslaesse": "Auslass"
}

class ReadData(QKanDBDialog, FORM_CLASS_read_data):  # type: ignore

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.iface = plugin.iface

        # Set up the database loader
        # self.tf_qkanDB.textChanged.connect(self.reload_database)

        self.db_qkan: Optional[Connection] = None
        self.db_name: Optional[str] = None

    def connectQKanDB(self, database_qkan=None):
        """Liest die verknüpfte QKan-DB aus dem geladenen Projekt
        Für Test muss database_qkan vorgegeben werden
        """

        # Verbindung zur Datenbank des geladenen Projekts herstellen
        if database_qkan:
            self.database_qkan = database_qkan
        else:
            self.database_qkan, _ = get_database_QKan()
        if self.database_qkan:
            self.db_qkan: DBConnection = DBConnection(dbname=self.database_qkan)
            if not self.db_qkan.connected:
                logger.error(
                    "Fehler in he8porter.application.connectQKanDB:\n"
                    f"QKan-Datenbank {self.database_qkan:s} wurde nicht"
                    " gefunden oder war nicht aktuell!\nAbbruch!"
                )
                return False
        else:
            fehlermeldung("Fehler: Für den Export muss ein Projekt geladen sein!")
            return False

        # self.export_dlg.connectQKanDB(self.db_qkan)               # deaktiviert jh, 17.04.2021
        return True

    def run(self) -> None:
        """Immediately run paste procedure"""

        layer = self.iface.activeLayer()
        if layer is None:
            self.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Kein Layer zum Einfügen der Daten ausgewählt',
                level=Qgis.Critical,
            )
            return
        datasource = layer.source()
        dbname, table, geom, sql = get_qkanlayer_attributes(datasource)
        if REQUIRED_FIELDS.get(table, None):
            self.connectQKanDB(dbname)
            self.read_clipboard(table, True)
        elif layer.providerType() == 'spatialite':
            self.connectQKanDB(dbname)
            self.read_clipboard(table, False)
        else:
            return

        self.iface.messageBar().pushMessage(f"Clipboard: ", "Daten wurden in Tabelle {table} eingefügt", level=Qgis.Info)


    def convert(self,
                func: Callable[[Union[str, float, int]], Any],
                nrow:int,
                column:str,
                value:str
                ) -> Any:
        """Typkonvertierung mit Fehlermeldung"""
        try:
            if isinstance(func(), float):
                result = float(value.replace(',', '.'))
            else:
                result = func(value)
        except:
            _type = func.__name__
            logger.error(f'read_data: Zeile {nrow}, Spalte {column}: {value} entspricht nicht Datentyp ({_type})')
            result = None
        return result

    def read_clipboard(self, table_name: str, has_trigger: bool) -> None:
        """Reads QKan data from clipboard and inserts proper columns into table 'table_name'"""
        # Fetch data from clipboard
        data = QgsApplication.clipboard().text()

        if data:
            # read data from clipboard
            lines = data.splitlines()
            if len(lines) <= 1:
                return
            headers = lines[0].split("\t")

            # cursor = self.qkan_db.cursor()
            # read names and types from qkan table
            qkan_columntypes = {}

            if not self.db_qkan.sql(
                    "SELECT name, type FROM PRAGMA_TABLE_INFO(?);",
                    mute_logger = True,
                    parameters = (table_name,),
            ):
                del self.db_qkan
                return

            for column in self.db_qkan.fetchall():
                name, type = column
                if name in headers:
                    # Nur Spalten übernehmen, die auch in den Clipboard-Daten vorkommen
                    qkan_columntypes[name] = type

            # Check required column[ name]s
            for column in REQUIRED_FIELDS[table_name]:
                if column in headers:
                    continue
                logger.error(f'Notwendige Spalte fehlt: {column}')
                return

            # parse all data lines
            parsed_data: List[List[Union[str, float, int]]] = []
            for nrow, line in enumerate(lines[1:]):
                parsed_dataset = []
                values = line.split("\t")
                if len(values) != len(headers):
                    fehlermeldung(
                        "Fehler in den einzufügenden Daten: Spaltenzahl stimmt nicht mit Kopfzeile überein",
                        line
                    )
                    continue
                for ncol, value in enumerate(values):
                    column = headers[ncol]
                    _type = qkan_columntypes.get(column, None)
                    if not _type:
                        continue
                    if _type.lower() == "integer":
                        parsed_dataset.append(self.convert(int, nrow, column, value))
                    if _type.lower() == "real":
                        parsed_dataset.append(self.convert(float, nrow, column, value))
                    elif _type.lower() == "text":
                        # no conversion necessary
                        parsed_dataset.append(value)

                # Schaechte, Speicher und Auslaesse werden in der Tabelle "schaechte" gespeichert,
                # aber durch "schachttyp" unterschieden
                if SCHACHT_TYPES.get(table_name, None):
                    parsed_dataset['schachttyp']=SCHACHT_TYPES[table_name]
                    if 'schachttyp' not in headers:
                        headers.append('schachttyp')

                parsed_data.append(parsed_dataset)

            # Insert table data
            # Replace table_name for 'Auslass', 'Speicher' (listed in SCHACHT_TYPES)
            if SCHACHT_TYPES.get(table_name, None):
                tabnam = 'schaechte_data'
            elif has_trigger:
                tabnam = table_name + '_data'
            else:
                tabnam = table_name

            for values in parsed_data:
                sql = f"INSERT INTO {tabnam} ({', '.join(headers)}) VALUES ({', '.join(['?'] * len(headers))})"
                if not self.db_qkan.sql(
                    sql,
                    mute_logger = True,
                    parameters = values,
                ):
                    del self.db_qkan
                    return

            self.db_qkan.commit()
            del self.db_qkan

            # Redraw map
            project = QgsProject.instance()
            project.reloadAllLayers()
