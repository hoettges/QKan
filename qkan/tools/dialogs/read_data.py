import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast, Any, Callable
from fnmatch import fnmatch

from qgis.core import QgsApplication, QgsProject, QgsMessageLog, QgsGeometry
from qgis.PyQt.QtWidgets import QWidget
from qkan.database.dbfunc import DBConnection
from qgis.core import Qgis

from qkan import QKan
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_qkanlayer_attributes,
)

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

logger = logging.getLogger("QKan.tools.dialogs.read_data")

def wktmod(wkt_geom):
    """Wandelt einen WKT-Ausdruck in einen WKB-Ausdruck um, um das Dezimaltrennzeichenproblem
       zu umgehen"""
    pg = QgsGeometry.fromWkt(wkt_geom)
    bgeo = QgsGeometry.asWkb(pg).data().hex()
    return bgeo


class ReadData:  # type: ignore
    def __init__(
        self,
        plugin: "QKanTools",
        proceed: bool = False,
        parent: Optional[QWidget] = None,
    ):
        super().__init__()

        self.iface = plugin.iface

        # Set up the database loader
        # self.tf_qkanDB.textChanged.connect(self.reload_database)

        self.db_name: Optional[str] = None

        self.required_fields = QKan.config.tools.Clipboard.required_fields
        self.schacht_types = QKan.config.tools.Clipboard.schacht_types
        self.haltung_types = QKan.config.tools.Clipboard.haltung_types
        self.qkan_patterns = QKan.config.tools.Clipboard.qkan_patterns

        self.proceed = proceed

    def run(self) -> None:
        """Immediately run paste procedure, when proceed == True, otherwise only print mapping list"""

        self.table_name: str  # Mit ausgewähltem Layer verknüpfter Tabellenname
        self.table_geom: str  # Mit ausgewähltem Layer verknüpfte Geometriespalte
        self.table_sql: str  # Mit ausgewähltem Layer verknüpfter Filterausdruck
        self.layer_name: str  # Ausgewählter Layer

        layer = self.iface.activeLayer()
        if layer is None:
            self.iface.messageBar().pushMessage(
                "Bedienerfehler",
                "Kein Layer zum Einfügen der Daten ausgewählt",
                level=Qgis.Critical,
            )
            return
        elif layer.isEditable():
            self.iface.messageBar().pushMessage(
                "Bedienerfehler",
                'Der gewählte Layer darf nicht im Bearbeitungsstatus "editierbar" sein',
                level=Qgis.Critical,
            )
            return

        datasource = layer.source()
        self.layer_name = layer.name()
        self.epsg = layer.crs().postgisSrid()
        (
            dbname,
            self.table_name,
            self.table_geom,
            self.table_sql,
        ) = get_qkanlayer_attributes(datasource)

        self.db_name = dbname

        if layer.providerType() == "spatialite":
            self.read_clipboard()
        else:
            return

    def convert(
        self,
        func: Callable[[Union[str, float, int]], Any],
        nrow: int,
        column: str,
        value: str,
    ) -> Any:
        """Typkonvertierung mit Fehlermeldung"""
        if value is None:
            logger.error(f"Zeile {nrow}, Spalte {column}: Feldwert ist leer")
            return None
        elif value == '':
            return None

        try:
            if isinstance(func(), float) and isinstance(value, str):
                if '.' in value and ',' in value:
                    if value.index('.') < value.index(','):
                        result = float(value.replace(".", "").replace(",", "."))     # 1.234.567,89 -> 1234567.89
                    else:
                        result = float(value.replace(",", ""))                       # 1,234,567.89 -> 1234567.89
                else:
                    result = float(value.replace("'", "").replace(",", "."))         # 1'234'567,89 -> 1234567.89
            else:
                result = func(value)
        except:
            _type = func.__name__
            logger.error(
                f"read_data: Zeile {nrow}, Spalte {column}: {value} entspricht nicht Datentyp ({_type}), \n"
                f"sondern ist {type(value)}"
            )
            result = None
        return result

    def read_clipboard(self) -> None:
        """Reads QKan data from clipboard and inserts proper columns into table 'table_name'"""
        # Fetch data from clipboard
        data = QgsApplication.clipboard().text()
        if not data:
            return

        # read data from clipboard
        lines = data.splitlines()
        if len(lines) <= 1:
            return

        # find separator.
        clip_selis = ["\t", ";"]  # allowed separators for clipboard data.
        for clip_sep in clip_selis:
            head_clipboard = [
                el.strip() for el in lines[0].split(clip_sep)
            ]  # attribute name from Clipboard
            if len(head_clipboard) > 1:
                break

        head_match: List[str] = [None] * len(
            head_clipboard
        )  # attribute names from QKan table
        # corresponding to head_clipboard
        # replace column names by QKan-names using qkan_patterns
        if self.table_name in self.qkan_patterns:
            patternLis: Dict[str, List[str]] = self.qkan_patterns[
                self.table_name
            ].copy()
        else:
            QgsMessageLog.logMessage(
                f'In die Tabelle "{self.table_name}" kann QKan (noch) nicht einfügen.',
                "QKan Clipboard",
                level=Qgis.Info,
                notifyUser=True,
            )
            self.iface.openMessageLog()
            return

        if self.schacht_types.get(self.layer_name, None):
            # "Schächte", "Auslauf" and "Speicher" data stored in table "schaechte"
            tabnam_db = "schaechte"
        elif self.haltung_types.get(self.layer_name, None):
            # "Haltungen", "Pumpen", "Wehre", "Drosseln", "Schieber", "Grund-/Seitenauslässe",
            # "H-Regler", "Q-Regler" data stored in table "haltungen"
            tabnam_db = "haltungen"
        else:
            tabnam_db = self.table_name

        with DBConnection(self.db_name) as db_qkan:
            if not db_qkan.sql(
                "SELECT name, type FROM PRAGMA_TABLE_INFO(?);",
                mute_logger=True,
                parameters=(tabnam_db,),
            ):
                return
            qkan_tableinfo = db_qkan.fetchall()

        head_qkan = [el[0] for el in qkan_tableinfo]

        # look for matches
        for icol, colClip in enumerate(head_clipboard):
            if colClip == "pk":
                continue
            elif colClip in head_qkan:
                # 1. test if full match found
                head_match[icol] = colClip
            elif colClip == "wkt_geom":
                if self.layer_name in self.schacht_types and (
                    self.layer_name != "Knotenpunkte"
                ):
                    head_match[icol] = "geop"
                else:
                    head_match[icol] = "geom"
            else:
                # 2. test if match in patternLis (see: config.py)
                found = False  # Suche kann beendet werden
                for colnamQKan in patternLis.keys():
                    for patt in patternLis[colnamQKan]:
                        if fnmatch(colClip, patt):
                            if not head_match[icol]:
                                # only if not just matched
                                head_match[icol] = colnamQKan
                            found = True
                            break
                    if found:
                        break

        # Dict mit relevanten Spalten, name: Spaltenindex
        qkan_columntypes: Dict[str, str] = {}
        qkan_cols: Dict[str, int] = {}
        for (name, _type) in qkan_tableinfo:
            if name in head_match:
                qkan_cols[name] = head_match.index(
                    name
                )  # Spaltennamen der einzufügenden Daten
                qkan_columntypes[name] = _type
            # elif name in head_clipboard:
            #     head_match[]
            #     qkan_cols[name] = head_clipboard.index(name)  # Spaltennamen der einzufügenden Daten
            #     qkan_columntypes[name] = _type

        # Check required column[ name]s
        for column in self.required_fields.get(self.table_name, []):
            if column in qkan_cols:
                continue
            logger.warning(f"self.table_name: {self.table_name}")
            logger.warning(f"Notwendige Spalte fehlt. column: {column}")
            logger.warning(f"qkan_cols: {qkan_cols}")
            self.iface.messageBar().pushMessage(
                "Fehler in kopierten Daten",
                f"Notwendige Spalte fehlt: {column}",
                level=Qgis.Warning,
            )
            QgsMessageLog.logMessage(
                f"In den kopierten Daten fehlt folgende notwendig Spalte: {column}",
                "QKan Clipboard",
                level=Qgis.Info,
                notifyUser=True,
            )
            # vorab auch Info über erkannte Spalten
            meldung = " | ".join(
                [
                    f"{head_clipboard[col]} > {head_match[col]}"
                    for col in list(qkan_cols.values())
                ]
            )
            QgsMessageLog.logMessage(
                f"\nFolgende Spalten konnten erkannt werden: {meldung}",
                "QKan",
                level=Qgis.Info,
                notifyUser=True,
            )
            self.iface.openMessageLog()
            return

        # Schaechte, Speicher und Auslaesse werden in der Tabelle "schaechte" gespeichert,
        # aber durch "schachttyp" unterschieden
        schtyp_added: bool = (
            False  # Spalte 'schachttyp' wurde hinzugefügt. Default: falsch
        )
        haltyp_added: bool = (
            False  # Spalte 'haltungstyp' wurde hinzugefügt. Default: falsch
        )
        logger.debug(f"tabnam_db: {tabnam_db}")
        if tabnam_db == "schaechte":
            if "schachttyp" not in qkan_cols:
                col_schachttyp: int = len(head_match)
                qkan_cols[
                    "schachttyp"
                ] = col_schachttyp  # dazu gibt es keine Spalte in den Clipboard-Daten
                schtyp_added = True
                logger.debug(f'Spalte "schachttyp" hinzugefügt.')
            else:
                logger.debug(f'Spalte "schachttyp" schon vorhanden.')
        elif tabnam_db == "haltungen":
            if "haltungstyp" not in qkan_cols:
                col_haltungstyp: int = len(head_match)
                qkan_cols[
                    "haltungstyp"
                ] = col_haltungstyp  # dazu gibt es keine Spalte in den Clipboard-Daten
                haltyp_added = True
                logger.debug(f'Spalte "haltungstyp" hinzugefügt.')
            else:
                logger.debug(f'Spalte "haltungstyp" schon vorhanden.')

        # parse all data lines
        qkan_colnames: list[str] = list(qkan_cols.keys())

        logger.info(f"Es wurden folgende Spaltennamen zugeordnet: ")
        for column in qkan_colnames:
            logger.info(f"{qkan_cols[column]} -> {column}")
        logger.info(f"Umgewandelte Spaltennamen: {head_match}")

        if schtyp_added or haltyp_added:
            meldung = " | ".join(
                [
                    f"{head_clipboard[col]} > {head_match[col]}"
                    for col in list(qkan_cols.values())[:-1]
                ]
            )
        else:
            meldung = " | ".join(
                [
                    f"{head_clipboard[col]} > {head_match[col]}"
                    for col in list(qkan_cols.values())
                ]
            )
        self.iface.messageBar().pushMessage(
            "Info",
            f"Folgende Spalten konnten erkannt werden: {meldung}",
            level=Qgis.Info,
        )

        # decision: datacheck only or start paste procedure
        if not self.proceed:
            QgsMessageLog.logMessage(
                f"\nFolgende Spalten konnten erkannt werden: {meldung}",
                "QKan",
                level=Qgis.Info,
                notifyUser=True,
            )
            self.iface.openMessageLog()
            return

        logger.debug(f'Vor Aufruf _parsed_dataset:'
                     f'\n{qkan_colnames=}'
                     f'\n{qkan_cols=}'
                     )

        self._parsed_dataset(
            lines,
            clip_sep,
            head_match,
            qkan_colnames,
            schtyp_added,
            haltyp_added,
            qkan_cols,
            qkan_columntypes,
            tabnam_db
        )
        # Redraw map
        project = QgsProject.instance()
        project.reloadAllLayers()

        self.iface.messageBar().pushMessage(
            "Info",
            f'Daten in Layer "{self.layer_name}" (Datenbanktabelle "{tabnam_db}") eingefügt.',
            level=Qgis.Info,
        )

    def _parsed_dataset(
            self,
            lines: List[str],
            clip_sep: str,
            head_match: List[str],
            qkan_colnames: List[str],
            schtyp_added: bool,
            haltyp_added: bool,
            qkan_cols: Dict[str, int],
            qkan_columntypes: Dict[str, str],
            tabnam_db: str
    ) -> None:
        with DBConnection(self.db_name) as db_qkan:
            for nrow, line in enumerate(lines[1:]):
                parsed_dataset = {}
                values = line.split(clip_sep)
                if len(values) != len(head_match):
                    fehlermeldung(
                        f"Fehler in den einzufügenden Daten: Spaltenzahl {len(values)}"
                        f" stimmt nicht mit Kopfzeile {len(head_match)} überein",
                        f"Datenzeile: {line}",
                    )
                    continue
                for column in qkan_colnames:
                    if (
                            (column == "schachttyp" and schtyp_added)
                            or (column == "haltungstyp" and haltyp_added)
                    ):
                        continue  # Typerkennung überspringen

                    try:
                        _value = values[qkan_cols.get(column, None)]
                    except BaseException as err:
                        fehlermeldung(
                            "Programmfehler",
                            f"schtyp_added: {schtyp_added}\n"
                            f"haltyp_added: {haltyp_added}\n"
                            f"_value:       {_value}\n"
                            f"column:       {column}\n",
                        )
                        return

                    _type = qkan_columntypes.get(
                        column, None
                    )  # Typ aus DB-Tabelle

                    logger.debug(f"column: {column}" f"\n_value: {_value}")

                    if not _type:
                        continue

                    if _type.lower() == "integer":
                        field = self.convert(int, nrow, column, _value)
                    elif _type.lower() == "real":
                        field = self.convert(float, nrow, column, _value)
                    elif _type.lower() == "text":
                        # no conversion necessary
                        field = _value
                    elif _type.lower() in (
                            "point",
                            "linestring",
                            "polygon",
                            "multipolygon",
                    ):
                        field = wktmod(_value)
                        logger.debug(f'\n{__file__}: geom erkannt:'
                                     f'\n{_value=}'
                                     f'\n{column=}'
                                     )
                        # field = f"GeomFromText('{_value}',{self.epsg})"
                    else:
                        fehlermeldung(
                            "Fehler in Clipboard-Daten",
                            "Datentyp konnte nicht erkannt werden. "
                            f"Spalte: {column}, Wert: {_value}"
                            f"Typ: {type(_value)}",
                        )
                        continue

                    parsed_dataset[column] = field

                # Falls Spalte 'schachttyp' oder 'haltungstyp' ergänzt wurde (s.o.)
                if schtyp_added:
                    parsed_dataset["schachttyp"] = self.schacht_types[
                        self.layer_name
                    ]
                elif haltyp_added:
                    parsed_dataset["haltungstyp"] = self.haltung_types[
                        self.layer_name
                    ]
                parsed_dataset["epsg"] = self.epsg

                logger.debug(
                    f"read_data - insertdata:\ntabnam_db: {tabnam_db}\n"
                    f"parsed_dataset: {parsed_dataset}"
                )

                if not db_qkan.insertdata(
                        tabnam_db,
                        mute_logger=False,
                        **parsed_dataset
                ):
                    return

            db_qkan.commit()
