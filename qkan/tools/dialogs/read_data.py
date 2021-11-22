import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast, Any, Callable
from fnmatch import fnmatch

from qgis.core import QgsApplication, QgsProject
from qgis.PyQt.QtWidgets import QWidget
from qkan.database.dbfunc import DBConnection
from qgis.core import Qgis

from qkan import QKan
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan, get_qkanlayer_attributes

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

logger = logging.getLogger("QKan.tools.dialogs.read_data")


class ReadData():  # type: ignore

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__()

        self.iface = plugin.iface

        # Set up the database loader
        # self.tf_qkanDB.textChanged.connect(self.reload_database)

        self.db_qkan: Optional[DBConnection] = None
        self.db_name: Optional[str] = None

        self.required_fields = QKan.config.tools.Clipboard.required_fields
        self.schacht_types = QKan.config.tools.Clipboard.schacht_types
        self.qkan_patterns = QKan.config.tools.Clipboard.qkan_patterns

    def run(self) -> None:
        """Immediately run paste procedure"""

        layer = self.iface.activeLayer()
        if layer is None:
            self.iface.messageBar().pushMessage(
                "Bedienerfehler",
                'Kein Layer zum Einfügen der Daten ausgewählt',
                level=Qgis.Critical,)
            return
        elif layer.isEditable():
            self.iface.messageBar().pushMessage(
                "Bedienerfehler",
                'Der gewählte Layer darf nicht im Bearbeitungsstatus "editierbar" sein',
                level=Qgis.Critical,)
            return

        datasource = layer.source()
        layername = layer.name()
        dbname, table, geom, sql = get_qkanlayer_attributes(datasource)
        if layer.providerType() == 'spatialite':
            self.db_qkan = DBConnection(dbname)
            self.read_clipboard(table, layername)
        else:
            return

    def convert(self,
                func: Callable[[Union[str, float, int]], Any],
                nrow: int,
                column: str,
                value: str
                ) -> Any:
        """Typkonvertierung mit Fehlermeldung"""
        if not value:
            logger.error(f'Zeile {nrow}, Spalte {column}: Feldwert ist leer')
            return None
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

    def read_clipboard(self, table_name: str, layer_name: str) -> None:
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

            if self.required_fields.get(table_name, None):
                if self.schacht_types.get(layer_name, None):
                    tabnam_db = 'schaechte_data'
                else:
                    tabnam_db = table_name + '_data'
            else:
                tabnam_db = table_name

            # replace column names by QKan-names using qkan_patterns
            head_qk = [None] * len(headers)
            patternLis = self.qkan_patterns[table_name].copy()
            for icol, colUser in enumerate(headers):
                found = False                                   # Suche kann beendet werden
                for colQ in patternLis.keys():
                    for patt in patternLis[colQ]:
                        if fnmatch(colUser, patt):
                            head_qk[icol] = colQ
                            found = True
                            break
                    if found:
                        break

            if not self.db_qkan.sql(
                    "SELECT name, type FROM PRAGMA_TABLE_INFO(?);",
                    mute_logger = True,
                    parameters = (tabnam_db,),
            ):
                del self.db_qkan
                return

            # Dict mit relevanten Spalten, name: Spaltenindex
            qkan_cols = {}
            for (name, _type) in self.db_qkan.fetchall():
                if name in head_qk:
                    # Nur Spalten übernehmen, die auch in den Clipboard-Daten vorkommen
                    qkan_columntypes[name] = _type
                    qkan_cols[name] = head_qk.index(name)       # Spaltennamen der einzufügenden Daten

            # Check required column[ name]s
            for column in self.required_fields[table_name]:
                if column in qkan_cols:
                    continue
                logger.error(f'table_name: {table_name}')
                logger.error(f'Notwendige Spalte fehlt. column: {column}')
                logger.error(f'qkan_cols: {qkan_cols}')
                self.iface.messageBar().pushMessage(
                    "Fehler in kopierten Daten",
                    f'Notwendige Spalte fehlt: {column}',
                    level=Qgis.Critical,
                )
                return

            # Schaechte, Speicher und Auslaesse werden in der Tabelle "schaechte" gespeichert,
            # aber durch "schachttyp" unterschieden
            schtyp_added = False                    # Spalte 'schachttyp' wurde hinzugefügt. Default: falsch
            if tabnam_db == 'schaechte':
                if 'schachttyp' not in qkan_cols:
                    qkan_cols['schachttyp'] = None  # dazu gibt es keine Spalte in den Clipboard-Daten
                    schtyp_added = True

            # parse all data lines
            qkan_colnames = list(qkan_cols.keys())
            data_colnames = [headers[qkan_cols[column]] for column in qkan_colnames]

            logger.info(f'Es wurden folgende Spaltennamen zugeordnet: ')
            for column in qkan_colnames:
                logger.info(f'{headers[qkan_cols[column]]} -> {column}')
            logger.info(f'Umgewandelte Spaltennamen: {head_qk}')

            meldung = ", ".join([f'"{el[0]}" ({el[1]})' for el in zip(data_colnames, qkan_colnames)])
            self.iface.messageBar().pushMessage(
                "Info",
                f'Folgende Spalten konnten erkannt werden: {meldung}',
                level=Qgis.Info,
            )

            for nrow, line in enumerate(lines[1:]):
                parsed_dataset = {}
                values = line.split("\t")
                if len(values) != len(head_qk):
                    fehlermeldung(
                        "Fehler in den einzufügenden Daten: Spaltenzahl stimmt nicht mit Kopfzeile überein",
                        line)
                    continue
                for column in qkan_colnames:
                    value = values[qkan_cols.get(column, None)]
                    _type = qkan_columntypes.get(column, None)          # Typ aus DB-Tabelle
                    if not _type:
                        continue
                    if _type.lower() == "integer":
                        field = self.convert(int, nrow, column, value)
                    elif _type.lower() == "real":
                        field = self.convert(float, nrow, column, value)
                    elif _type.lower() == "text":
                        # no conversion necessary
                        field = value
                    else:
                    #     logger.error(f'Feldtyp Spalte {column} fehlerhaft: {_type}')
                    # if not field:
                        self.iface.messageBar().pushMessage(
                            "Datenfehler",
                            'Datentyp konnte nicht erkannt werden. '
                            f'Spalte: {column}, Wert: {value}'
                            f'Typ: {type(value)}',
                            level=Qgis.Critical, )
                        # return
                    parsed_dataset[column] = field

                # Falls Spalte 'schachttyp' ergänzt wurde (s.o.)
                if schtyp_added:
                    parsed_dataset['schachttyp'] = self.schacht_types[layer_name]

                if self.schacht_types.get(layer_name, None):
                    if 'durchm' in qkan_cols:
                        if parsed_dataset['durchm'] > 10.:
                            parsed_dataset['durchm'] /= 1000.

                sql = f"INSERT INTO {tabnam_db} ({', '.join(qkan_colnames)}) " \
                      f"VALUES ({', '.join(['?'] * len(qkan_colnames))})"
                if not self.db_qkan.sql(
                    sql,
                    mute_logger=True,
                    parameters=list(parsed_dataset.values()),
                ):
                    del self.db_qkan
                    return

            self.db_qkan.commit()
            del self.db_qkan

            # Redraw map
            project = QgsProject.instance()
            project.reloadAllLayers()

            self.iface.messageBar().pushMessage(
                "Info",
                f'Daten in Layer "{layer_name}" (Datenbanktabelle "{tabnam_db}") eingefügt.',
                level=Qgis.Info,
            )
