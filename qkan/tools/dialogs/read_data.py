import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast, Any, Callable
from fnmatch import fnmatch

from qgis.core import QgsApplication, QgsProject, QgsMessageLog
from qgis.PyQt.QtWidgets import QWidget
from qkan.database.dbfunc import DBConnection
from qgis.core import Qgis

from qkan import QKan
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan, get_qkanlayer_attributes

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

logger = logging.getLogger("QKan.tools.dialogs.read_data")


class ReadData():  # type: ignore

    def __init__(self, plugin: "QKanTools", proceed: bool = False, parent: Optional[QWidget] = None):
        super().__init__()

        self.iface = plugin.iface

        # Set up the database loader
        # self.tf_qkanDB.textChanged.connect(self.reload_database)

        self.db_qkan: Optional[DBConnection] = None
        self.db_name: Optional[str] = None

        self.required_fields = QKan.config.tools.Clipboard.required_fields
        self.schacht_types = QKan.config.tools.Clipboard.schacht_types
        self.qkan_patterns = QKan.config.tools.Clipboard.qkan_patterns

        self.proceed = proceed

    def run(self) -> None:
        """Immediately run paste procedure, when proceed == True, otherwise only print mapping list"""

        self.table_name: str    # Mit ausgewähltem Layer verknüpfter Tabellenname
        self.table_geom: str    # Mit ausgewähltem Layer verknüpfte Geometriespalte
        self.table_sql: str     # Mit ausgewähltem Layer verknüpfter Filterausdruck
        self.layer_name: str    # Ausgewählter Layer

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
        self.layer_name = layer.name()
        self.epsg = layer.crs().postgisSrid()
        dbname, self.table_name, self.table_geom, self.table_sql = get_qkanlayer_attributes(datasource)
        if layer.providerType() == 'spatialite':
            self.db_qkan = DBConnection(dbname)
            self.read_clipboard()
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

    def read_clipboard(self) -> None:
        """Reads QKan data from clipboard and inserts proper columns into table 'table_name'"""
        # Fetch data from clipboard
        data = QgsApplication.clipboard().text()

        if data:
            # read data from clipboard
            lines = data.splitlines()
            if len(lines) <= 1:
                return
            head_clipboard = lines[0].split("\t")                   # attribute name from Clipboard
            head_match: List[str] = [None] * len(head_clipboard)     # attribute names from QKan table
                                                                    # corresponding to head_clipboard
            # replace column names by QKan-names using qkan_patterns
            if self.table_name in self.qkan_patterns:
                patternLis: Dict[str, List[str]] = self.qkan_patterns[self.table_name].copy()
            else:
                QgsMessageLog.logMessage(f'In die Tabelle "{self.table_name}" kann QKan (noch) nicht einfügen.',
                                         'QKan Clipboard',
                                         level=Qgis.Info, notifyUser=True)
                self.iface.openMessageLog()
                return False

            # target table replaced by view (+ '_data') if in required_fields
            if 'wkt_geom' in head_clipboard or 'geom' in head_clipboard or 'geop' in head_clipboard:
                # geometry column exists
                tabnam_db = self.table_name
            elif self.required_fields.get(self.table_name, None):
                if self.schacht_types.get(self.layer_name, None):
                    # "Schächte", "Auslauf" and "Speicher" data stored in table "schaechte"
                    tabnam_db = 'schaechte_data'
                else:
                    tabnam_db = self.table_name + '_data'
            else:
                tabnam_db = self.table_name

            if not self.db_qkan.sql(
                    "SELECT name, type FROM PRAGMA_TABLE_INFO(?);",
                    mute_logger = True,
                    parameters = (tabnam_db,),
            ):
                del self.db_qkan
                return
            qkan_tableinfo = self.db_qkan.fetchall()
            head_qkan = [el[0] for el in qkan_tableinfo]

            # look for matches
            for icol, colClip in enumerate(head_clipboard):
                if colClip in ('pk'):
                    continue
                if colClip in head_qkan:
                    # 1. test if full match found
                    head_match[icol] = colClip
                else:
                    # 2. test if match in patternLis (see: config.py)
                    found = False                                   # Suche kann beendet werden
                    for colnamQKan in patternLis.keys():
                        for patt in patternLis[colnamQKan]:
                            if fnmatch(colClip, patt):
                                head_match[icol] = colnamQKan
                                found = True
                                break
                        if found:
                            break

            # Dict mit relevanten Spalten, name: Spaltenindex
            qkan_columntypes: dict[str, str] = {}
            qkan_cols: dict[str, int] = {}
            for (name, _type) in qkan_tableinfo:
                if name in head_match:
                    qkan_cols[name] = head_match.index(name)  # Spaltennamen der einzufügenden Daten
                    qkan_columntypes[name] = _type
                # elif name in head_clipboard:
                #     head_match[]
                #     qkan_cols[name] = head_clipboard.index(name)  # Spaltennamen der einzufügenden Daten
                #     qkan_columntypes[name] = _type

            # Check required column[ name]s
            for column in self.required_fields[self.table_name]:
                if column in qkan_cols:
                    continue
                logger.warning(f'self.table_name: {self.table_name}')
                logger.warning(f'Notwendige Spalte fehlt. column: {column}')
                logger.warning(f'qkan_cols: {qkan_cols}')
                self.iface.messageBar().pushMessage(
                    "Fehler in kopierten Daten",
                    f'Notwendige Spalte fehlt: {column}',
                    level=Qgis.Warning,
                )
                QgsMessageLog.logMessage( f'In den kopierten Daten fehlt folgende notwendig Spalte: {column}',
                                          'QKan Clipboard',
                                          level=Qgis.Info,
                                          notifyUser=True)
                self.iface.openMessageLog()
                return

            # Schaechte, Speicher und Auslaesse werden in der Tabelle "schaechte" gespeichert,
            # aber durch "schachttyp" unterschieden
            schtyp_added: bool = False                    # Spalte 'schachttyp' wurde hinzugefügt. Default: falsch
            logger.debug(f'tabnam_db: {tabnam_db}')
            if tabnam_db == 'schaechte_data':
                if 'schachttyp' not in qkan_cols:
                    col_schachttyp: int = len(head_match)
                    qkan_cols['schachttyp'] = col_schachttyp  # dazu gibt es keine Spalte in den Clipboard-Daten
                    schtyp_added = True
                    logger.debug(f'Spalte "schachttyp" hinzugefügt.')

            # parse all data lines
            qkan_colnames: list[str] = list(qkan_cols.keys())

            logger.info(f'Es wurden folgende Spaltennamen zugeordnet: ')
            for column in qkan_colnames:
                logger.info(f'{qkan_cols[column]} -> {column}')
            logger.info(f'Umgewandelte Spaltennamen: {head_match}')

            if schtyp_added:
                meldung = " | ".join([f'{head_clipboard[col]} > {head_match[col]}' for col in list(qkan_cols.values())[:-1]])
            else:
                meldung = " | ".join([f'{head_clipboard[col]} > {head_match[col]}' for col in list(qkan_cols.values())])
            # meldung = f'\nhead_match: {head_match}\nhead_clipboard: {head_clipboard}\nqkan_cols: {qkan_cols}\nqkan_colnames: {qkan_colnames}'
            self.iface.messageBar().pushMessage(
                "Info",
                f'Folgende Spalten konnten erkannt werden: {meldung}',
                level=Qgis.Info,
            )

            # decision: datacheck only or start paste procedure
            if not self.proceed:
                QgsMessageLog.logMessage( f'Folgende Spalten konnten erkannt werden: {meldung}', 'QKan Clipboard',
                                         level=Qgis.Info, notifyUser=True)
                self.iface.openMessageLog()

            else:
                for nrow, line in enumerate(lines[1:]):
                    parsed_dataset = {}
                    values = line.split("\t")
                    if len(values) != len(head_match):
                        fehlermeldung(
                            "Fehler in den einzufügenden Daten: Spaltenzahl stimmt nicht mit Kopfzeile überein",
                            line)
                        continue
                    for column in qkan_colnames:
                        if (not schtyp_added) or column != 'schachttyp':
                            value = values[qkan_cols.get(column, None)]
                            _type = qkan_columntypes.get(column, None)          # Typ aus DB-Tabelle
                            if not _type:
                                continue
                            if _type.lower() == "integer":
                                field = f"{self.convert(int, nrow, column, value)}"
                            elif _type.lower() == "real":
                                field = f"{self.convert(float, nrow, column, value)}"
                            elif _type.lower() == "text":
                                # no conversion necessary
                                field = f"'{value}'"
                            elif _type.lower() in ('point', 'linestring', 'polygon', 'multipolygon'):
                                field = f"GeomFromText('{value}',{self.epsg})"
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
                        parsed_dataset['schachttyp'] = self.schacht_types[self.layer_name]

                    if self.schacht_types.get(self.layer_name, None):
                        if 'durchm' in qkan_cols:
                            if float(parsed_dataset['durchm']) > 10.:
                                parsed_dataset['durchm'] = "{erg}".format(erg=float(parsed_dataset['durchm'])/1000.)

                    sql = f"INSERT INTO {tabnam_db} ({', '.join(qkan_colnames)}) " \
                          f"VALUES ({', '.join(list(parsed_dataset.values()))})"
                    if not self.db_qkan.sql(
                        sql,
                        mute_logger=True,
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
                    f'Daten in Layer "{self.layer_name}" (Datenbanktabelle "{tabnam_db}") eingefügt.',
                    level=Qgis.Info,
                )
