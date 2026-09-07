"""
Datenbankmanagement

Definition einer Klasse mit Methoden fuer den Zugriff auf eine SpatiaLite- oder PostgreSQL-Datenbank.
"""

import datetime
import os
import shutil
import sqlite3
import packaging.version
from typing import Any, List, Optional, Union, cast, Dict, Tuple
from fnmatch import fnmatch

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import spatialite_connect, pluginDirectory

from qkan import QKan, enums
from qkan.tools.qkan_utils import get_database_QKan, cleanname
import yaml

__author__ = "Joerg Hoettges"
__date__ = "November 2024"
__copyright__ = "(C) 2016-2024, Joerg Hoettges"

from qkan.utils import get_logger, QkanAbortError, QkanDbError, QkanUserError

logger = get_logger("QKan.dbfunc")


class DBConnection:
    """SpatiaLite Datenbankobjekt"""

    def __init__(
        self,
        dbname: Optional[str] = None,
        epsg: int = 25832,
        qkan_db_update: bool = False,
        writeDbBackup: bool = True,
        writeQgsBackup: bool = True,
    ):
        """Constructor. Überprüfung, ob die QKan-Datenbank die aktuelle Version hat,
           mit dem Attribut isCurrentDbVersion.

        :param dbname:          Pfad zur SpatiaLite-Datenbankdatei.
                                 - Falls angegeben und nicht vorhanden, wird es angelegt.
                                 - Falls nicht angegeben, wird die Datenbank aus den Layern "Schächte" und
                                   "Flächen" gelesen und verbunden
        :type dbname:           str

        :param epsg:            EPSG-Code aller Tabellen in einer neuen Datenbank
        :type epsg:             int

        :param qkan_db_update:  Bei veralteter Datenbankversion automatisch Update durchführen. Achtung:
                                Nach Durchführung muss k_layersadapt ausgeführt werden.
                                Diese Option ist insbesondere für die Testläufe notwendig
        :type qkan_db_update:   bool

        :param writeQgsBackup:  Soll beim Update der Datenbank eine Sicherungskopie der Projektdatei angelegt werden?
        :type writeQgsBackup:   bool

        :param writeDbBackup:   Soll beim Update der Datenbank eine Sicherungskopie der Datenbank angelegt werden?
        :type writeDbBackup:    bool


        public attributes:

        reload:             Update der Datenbank macht Neuladen des Projektes notwendig, weil Tabellenstrukturen
                            geändert wurden. Wird von self.updateversion() gesetzt

        connected:          Datenbankverbindung erfolgreich

        isCurrentDbVersion:   Datenbank ist auf dem aktuellen Stand
        """

        # Übernahme einiger Attribute in die Klasse
        self.dbname = dbname
        self.epsg: Optional[int] = epsg
        self.qkan_db_update = qkan_db_update
        self.writeDbBackup = writeDbBackup
        self.writeQgsBackup = writeQgsBackup
        self.isCurrentVersion = False                       # deprecated, aus Kompatibilitätsgründen

        # Die nachfolgenden Klassenobjekte dienen dazu, gleichartige (sqlidtext) SQL-Debug-Meldungen
        # nur einmal pro Sekunde zu erzeugen.
        self.sqltime = datetime.datetime.now()
        self.stmt_category = ""
        self.sqlcount = 0

        self.actDbVersion: packaging.version.Version = packaging.version.parse(QKan.dbVersion)

        # Verbindung hergestellt, d.h. weder fehlgeschlagen noch wegen reload geschlossen
        self.connected = True

        # zur Prüfung, ob eine Datenbankanbindung aktiv ist
        self.cursl = None

        # reload = True: Datenbank wurde aktualisiert und dabei sind gravierende Änderungen aufgetreten,
        # die ein Neuladen des Projektes erforderlich machen
        self.reload = False

        self.current_dbversion = packaging.version.parse("0.0.0")

        self.dbtype = None

        self.sqlnam = None
        self.sqls = {}

        self._connect()

    def __enter__(self) -> "DBConnection":
        """Allows use via context manager for easier connection handling"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes connection once we're out of context"""
        self._disconnect()

    def __del__(self) -> None:
        """Closes connection once object is deleted"""
        # warnings.warn(
        #     "Deleting the database object is deprecated. Use a context manager instead.",
        #     DeprecationWarning,
        # )
        self._disconnect()

    def loadmodule(self, module) -> None:
        """Lädt Modul spezifische SQL-Statements. Kann beliebig oft aufgerufen werden, da
        geprüft wird, ob ein Modul schon geladen wurde"""

        self.module = module
        # Bei Wechsel des Datenbanktyps QKan.sqls zurücksetzen
        if QKan.dbtype != self.dbtype:
            QKan.sqls = {}
        # Queries zu diesem Modul laden, wenn noch nicht geschehen oder Modul geändert und Modul-Sqls
        # noch nicht gelesen
        if not QKan.dbtype or not QKan.sqls.get(module):
            QKan.dbtype = self.dbtype
            if QKan.dbtype is None:
                logger.warning_user("Es wurde noch kein Projekt geladen!")
                raise QkanUserError
            elif QKan.dbtype == enums.QKanDBChoice.SPATIALITE:
                sqlfilename = os.path.join(pluginDirectory("qkan"), module, 'sqlite.yml')
            elif QKan.dbtype == enums.QKanDBChoice.POSTGIS:
                sqlfilename = os.path.join(pluginDirectory("qkan"), module, 'postgres.yml')
            else:
                logger.error_code(f'{self.__class__.__name__}: Datenbanktyp {QKan.dbtype} nicht zulässig!')
                raise QkanDbError

            try:
                with open(sqlfilename) as fr:
                    sql_yml = yaml.safe_load(fr.read())
                    logger.debug(f"{module=}: {QKan.sqls.get(module)=}")
                    if QKan.sqls.get(module) is None:
                        QKan.sqls[module] = sql_yml
                    else:
                        QKan.sqls[module].update(sql_yml)
                logger.debug(f'{self.__class__.__name__}: SQL-Liste aus Datei {sqlfilename=} geladen')
            except UnicodeDecodeError as err:
                logger.error_code(f'{self.__class__.__name__}, Fehler {err}: '
                                  f'Yaml-Datei {sqlfilename} konnte nicht gelesen werden, '
                                  f'weil sie nicht UTF-8-codiert ist. Bitte umwandeln')
                raise QkanAbortError
            except BaseException as err:
                logger.error_code(f'{self.__class__.__name__}, Fehler {err}: '
                                  f'Yaml-Datei {sqlfilename} konnte nicht gelesen werden')
                raise QkanAbortError

        # set sqls for active module
        self.sqls.update(QKan.sqls[module])

    def _connect(self) -> None:
        """Connects to SQLite3 or PostgreSAL database.

        Raises:
            DBConnectError: dbname is not set & could not be determined from project
        """

        if not self.dbname:
            get_database_QKan()
            self.dbname = QKan.config.database.qkan
            self.dbtype = QKan.dbtype
            if self.dbname is None:
                logger.warning_user("Fehler: Für die gewählte Funktion muss ein Projekt geladen sein!")
                raise QkanUserError
        else:
            self.dbtype = enums.QKanDBChoice.SPATIALITE

        # Bei Wechsel des Datenbanktyps QKan.sqls zurücksetzen
        if QKan.dbtype and QKan.dbtype != self.dbtype:
            QKan.sqls = {}
        # Queries zu diesem Modul laden, wenn noch nicht geschehen oder Modul geändert und Modul-Sqls
        # noch nicht gelesen

        try:
            self.loadmodule('database')
            self.loadmodule('tools')
        except QkanUserError:
            return

        # Load existing database
        if self.dbtype == enums.QKanDBChoice.SPATIALITE:
            if os.path.exists(self.dbname):
                self.consl = spatialite_connect(
                    database=self.dbname, check_same_thread=False
                )
                self.cursl = self.consl.cursor()

                self.epsg = self.getepsg()
                if self.epsg is None:
                    logger.error(
                        "dbqkan.DBConnection.__init__: EPSG konnte nicht ermittelt werden. \n"
                        + " QKan-DB: {}\n".format(self.dbname)
                    )

                logger.debug(
                    "dbqkan.DBConnection.__init__: Datenbank existiert und Verbindung hergestellt:\n"
                    + "{}".format(self.dbname)
                )

                # Versionsprüfung
                self.check_version()
                if not self.isCurrentDbVersion:
                    logger.debug("dbqkan: Datenbank ist nicht aktuell")
                    if self.qkan_db_update:
                        logger.debug(
                            "dbqkan: Update aktiviert. Deshalb wird Datenbank aktualisiert"
                        )

                        if self.writeDbBackup or self.writeQgsBackup:
                            pjVersion = self.current_dbversion.base_version
                            fpath, ext = os.path.splitext(self.dbname)
                            bakdir = os.path.join(f'{fpath}_backup', f'backup_{pjVersion}')
                            num = 0
                            bakdir_0 = bakdir
                            while os.path.exists(bakdir):
                                num += 1
                                bakdir = f'{bakdir_0}_{num}'
                            os.makedirs(bakdir)

                            if self.writeDbBackup:
                                shutil.copy(self.dbname, bakdir)

                            if self.writeQgsBackup:
                                projectfile = QgsProject.instance().fileName()
                                try:
                                    shutil.copy(projectfile, bakdir)
                                except:
                                    logger.error_code(f'Projektdatei {projectfile} konnte nicht auf {bakdir} kopiert werden')
                                    raise QkanAbortError

                        self.upgrade_database()
                    else:
                        logger.warning_user(
                            f"\n\nDie Datenbank hat die Versionsnummer {self.current_dbversion.base_version}. und entspricht \n"
                            f"nicht der aktuellen Versionsnummer {self.actDbVersion.base_version}. Bitte aktualisieren Sie "
                            f'die Datenbank mit dem Menü "QKan-Datenbank aktualisieren"!\n\n',
                        )
                        # logger.info(
                        #     f"Projekt muss aktualisiert werden. Die QKan-Version der "
                        #     f"Datenbank {self.current_dbversion.base_version} stimmt nicht \n"
                        #     f"mit der aktuellen QKan-Version {self.actDbVersion.base_version} überein und muss aktualisiert werden!"
                        # )
                        self.consl.close()
                        self.connected = False

                        return None
                else:
                    # nu aus Kompatibilitätsgründen
                    self.isCurrentVersion = True

            # Create new database
            else:
                QKan.instance.iface.messageBar().pushMessage(
                    "Information",
                    "SpatiaLite-Datenbank wird erstellt. Bitte warten...",
                    level=Qgis.MessageLevel.Info,
                )

                datenbank_qkan_template = os.path.join(QKan.template_dir, "qkan.sqlite")
                try:
                    shutil.copyfile(datenbank_qkan_template, self.dbname)

                    self.consl = spatialite_connect(database=self.dbname)
                    self.cursl = self.consl.cursor()

                    QKan.instance.iface.messageBar().pushMessage(
                        "Information",
                        "SpatiaLite-Datenbank ist erstellt!",
                        level=Qgis.MessageLevel.Info,
                    )
                except BaseException as err:
                    logger.debug(f"Datenbank ist nicht vorhanden: {self.dbname}")
                    errormsg=(
                        f"Fehler in dbqkan.DBConnection:\n{err}\n"
                        f"Kopieren von: {QKan.template_dir}\nnach: {self.dbname}\n nicht möglich"
                        )
                    self.connected = False
                    self.consl = None

                    logger.error(errormsg)
                    raise Exception(errormsg)

                # Erstellen der QKan-Datenbanktabellen inkl. Trigger und Views

                # Tabellen mit Geometrieobjekten
                tablisgeom = QKan.tablesgeom
                tablisgeop = QKan.tablesgeop
                tablisgbuf = QKan.tablesgbuf
                tablisglink = QKan.tablesglink
                tablisgeometry = QKan.tablesgeometry

                # Referenztabellen
                tablisattr = QKan.tablesattr

                # Erzeugen aller QKan-Tabellen
                tablis = set(tablisgeom) | \
                         set(tablisgeop) | \
                         set(tablisgbuf) | \
                         set(tablisglink) | \
                         set(tablisgeometry) | \
                         set(tablisattr)
                for tabnam in tablis:
                    sqlnam = f"database_create_{tabnam}"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 2. geom-Objekt hinzufügen

                for tabnam in tablisgeom:
                    sqlnam = f"database_add_{tabnam}_geom"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                            parameters={'epsg': self.epsg},
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                    sqlnam = f"database_createspatialindex_{tabnam}_geom"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 3. geop-Objekt hinzufügen

                for tabnam in tablisgeop:
                    sqlnam = f"database_add_{tabnam}_geop"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                            parameters={'epsg': self.epsg},
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                    sqlnam = f"database_createspatialindex_{tabnam}_geop"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                    # Anmerkung: Die nachfolgenden beiden Blöcke Waren bisher nur für 'schaechte' vorhanden.
                    # Deshalb erst mal weglassen

                    # sqlnam = f"database_drop_trigger_{tabnam}_geop_ggi"
                    # if not self.sqlyml(
                    #     sqlnam=sqlnam,
                    #     stmt_category= sqlnam,
                    # ):
                    #     logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                    # sqlnam = f"database_drop_trigger_{tabnam}_geop_ggu"
                    # if not self.sqlyml(
                    #     sqlnam=sqlnam,
                    #     stmt_category= sqlnam,
                    # ):
                    #     logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 4. gbuf-Objekt hinzufügen

                for tabnam in tablisgbuf:
                    sqlnam = f"database_add_{tabnam}_gbuf"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                            parameters={'epsg': self.epsg},
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                    sqlnam = f"database_createspatialindex_{tabnam}_gbuf"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 5. glink-Objekt hinzufügen

                for tabnam in tablisglink:
                    sqlnam = f"database_add_{tabnam}_glink"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                            parameters={'epsg': self.epsg},
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                    sqlnam = f"database_createspatialindex_{tabnam}_glink"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 6. Geometry-Objekt hinzufügen

                for tabnam in tablisgeometry:
                    sqlnam = f"database_add_{tabnam}_geometry"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                            parameters={'epsg': self.epsg},
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                    sqlnam = f"database_createspatialindex_{tabnam}_geometry"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 7. Trigger für Haltungen beim Fangen auf Schächte sowie
                # für Nachführung von Attributen in Haltungen bei Änderung in Referenztabellen

                tablis = [
                    "profile",
                    "entwart",
                    "simstatus",
                    "material",
                    "abflussparameter",
                ]
                for tabnam in tablis:
                    sqlnam = f"tools_create_trig_ref_{tabnam}"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 8. Standardisierte Referenztabellen füllen

                tablis = [
                    "auslasstypen",
                    "flaechentypen",
                    "abflusstypen",
                    "knotentypen",
                    "schachttypen",
                    "haltungstypen",
                    "untersuchrichtung",
                    "wetter",
                    "bewertungsart",
                    "pumpentypen",
                    "symbolkatalog",
                    "simulationsstatus",
                    "material",
                    "profile",
                    "entwaesserungsarten",
                ]

                for tabnam in tablis:
                    sqlnam = f"database_insert_{tabnam}"
                    if not self.sqlyml(
                            sqlnam=sqlnam,
                            stmt_category=sqlnam,
                            parameters={'epsg': self.epsg},
                    ):
                        logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 9. Referenztabelle mit Parametern
                sqlnam = f"database_insert_info"
                parameters = (str(self.actDbVersion.base_version),)
                if not self.sqlyml(
                        sqlnam=sqlnam,
                        stmt_category=sqlnam,
                        parameters=parameters
                ):
                    logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                # 10. Views
                sqlnam = f"database_createview_untersuchdat_aktuell"
                if not self.sqlyml(
                        sqlnam=sqlnam,
                        stmt_category=sqlnam,
                ):
                    logger.error_code(f"{self.__class__.__name__}: {sqlnam}")

                self.commit()
        elif self.dbtype == enums.QKanDBChoice.POSTGIS:
            self.consl = None
            self.isCurrentDbVersion = True
        else:
            logger.error_code(
                f'{self.__class__.__name__}: '
                f'Datenbanktyp {self.dbtype} unbekannt: Abbruch')


    def _disconnect(self) -> None:
        """Closes database connection."""
        try:
            if self.consl is not None:
                cast(sqlite3.Connection, self.consl).close()
            logger.debug(f"Verbindung zur Datenbank {self.dbname} wieder geloest.")
        except sqlite3.Error as err:
            fehlermeldung = (
                f"sqlite3-Fehler {err} in dbqkan.DBConnection: "
                f"Verbindung zur Datenbank {self.dbname} konnte nicht geloest werden.\n"
            )
            logger.debug(fehlermeldung)
            raise Exception(f"{self.__class__.__name__}: {fehlermeldung}")
        except:
            logger.debug('Fehler: Vermutlich ist kein Projekt geladen...')

    def attrlist(self, tabnam: str) -> Union[List[str]]:
        """Gibt Spaltenliste zurück."""

        tabnam = cleanname(tabnam)
        if not self.sqlyml(
            'database_tableinfo',
            f"dbqkan.DBConnection.attrlist fuer {tabnam}",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam)
        ):
            return []

        daten = self.cursl.fetchall()
        # lattr = [el[1] for el in daten if el[2]  == 'TEXT']
        lattr = [el[1] for el in daten]
        return lattr

    def getepsg(self) -> Optional[int]:
        """Feststellen des EPSG-Codes der Datenbank"""

        if not self.sqlyml('database_getepsg', "dbqkan.DBConnection.getepsg (1)"):
            return None

        data = self.fetchone()
        if data is None:
            fehlermeldung = (
                "Fehler in dbqkan.DBConnection.getepsg (2): "
                "Konnte EPSG nicht ermitteln",
            )
            logger.error(fehlermeldung)
            raise Exception(f"{self.__class__.__name__}: {fehlermeldung}")

        return data[0]

    def sqlyml(
            self,
            sqlnam: str,
            stmt_category: str = "allgemein",
            parameters: Union[Tuple, List, dict[str, Any]] = (),
            many: bool = False,
            mute_logger: bool = False,
            ignore: bool = False,
            replacefun: Union[callable, None] = None
    ) -> bool:
        """Wrapper for sql(). Reads sql from dict and optionaly replaces
           parameters using the format function replacefun.

           dict must first be read from module specific yaml file "sqlite.yml" / "postgres.yml"
           using db_qkan.loadmodule()

        :sqlnam:                Name of the SQL-statement in dict 'sqls'
        :type sqlnam:           String

        :stmt_category:         Category name. Allows suppression of sql-statement in logfile for
                                2 seconds appending on mute_logger
        :type stmt_category:    String

        :parameters:            parameters used in sql statement
        :type parameters:       Tuple, List or Dict

        :many:                  executes sql for every element in parameters -> must be a sequence of lists
        :type many:             Boolean

        :mute_logger:           suppress logging message for the same stmt_category for 2 seconds
        :type mute_logger:      Boolean

        :ignore:                ignore error and continue
        :type ignore:           Boolean

        :replacefun:            function which replaces variables in sql expression
        :type replacefun:       function

        :returns: void"""

        if sqlnam != self.sqlnam:
            self.sqlnam = sqlnam
            try:
                self.sql_txt = self.sqls[sqlnam].replace('*/ ', '*/\n').strip()
            except:
                logger.error_code(
                    f'{self.__class__.__name__}: '
                    f'SQL {sqlnam} nicht gefunden\n'
                    f'{stmt_category=}'
                    f'Möglicherweise wurde im Modulcode vergessen db_qkan.loadmodule aufzurufen.\n'
                    f'geladene SQLs:\n{self.sqls}'
                )

        # Die nachfolgende Funktion muss auch bei gleichem Abfragetyp durchgeführt werden, siehe _plausi.py
        if replacefun is not None:
            self.sqltext = replacefun(self.sql_txt)
            if '{' in self.sqltext:
                logger.error_code(
                    f'{self.__class__.__name__}: '
                    f'Fehler in yaml-Datei: sql enthält Parameter, obwohl keine ersetzen-Funktion'
                    f'im Aufruf geliefert wird.')
        else:
            self.sqltext = self.sql_txt

        try:
            erg = self.sql(
                sql=self.sqltext,
                stmt_category=stmt_category,
                parameters=parameters,
                many=many,
                mute_logger=mute_logger,
                ignore=ignore
            )
        except:
            logger.error_code(
                f'{self.__class__.__name__}: \n'
                f'SQL-Name: {sqlnam}'
            )
            raise QkanDbError
        return erg

    def sql(self,
            sql: str,
            stmt_category: str = "allgemein",
            parameters: Union[Tuple, List, dict[str, Any]] = (),
            many: bool = False,
            mute_logger: bool = False,
            ignore: bool = False,
            ) -> bool:
        """Execute a sql query on connected database"""
        try:
            # fürs logging:
            if isinstance(parameters, tuple):
                logparams = parameters[:5]      # Länge der Ausgabe beschränken...
            else:
                logparams = parameters

            if many:
                try:
                    self.cursl.executemany(sql, parameters)
                except ValueError as err:
                    raise ValueError(f"{err}\nTyp von parameters: {type(parameters)}")
                except BaseException as err:
                    logger.error(f"{err}\n: {sql=}")
                    raise ValueError(f"{err}\n: {sql=}")
            else:
                try:
                    self.cursl.execute(sql, parameters)
                except ValueError as err:
                    logger.error(f"{err}:\nTyp von parameters: {type(parameters)}")
                    raise ValueError(f"{err}:\nTyp von parameters: {type(parameters)}")
                except BaseException as err:
                    logger.error(f"{err}:\n {sql=}\n{parameters=}")
                    raise QkanDbError(f"{err}:\n {sql=}\n{parameters=}")

            if mute_logger:
                return True

            # Suppress log message for 2 seconds if category is identical to last query
            if self.stmt_category == stmt_category:
                self.sqlcount += 1
                if (self.sqltime.now() - self.sqltime).seconds < 2:
                    return True
            else:
                self.sqlcount = 0
                self.stmt_category = stmt_category

            # Log-Message if new category or same category for more than 2 seconds
            self.sqltime = self.sqltime.now()
            logger.debug(
                "dbqkan.DBConnection.sql (Nr. {}): {}\nsql: {}\nparameters: {}\n".format(
                    self.sqlcount+1, stmt_category, sql, logparams
                )
            )
            return True
        except sqlite3.Error as err:
            if ignore:
                logger.debug(f'Typ von parameters: {type(parameters)}')
                logger.warning(
                    f"dbqkan.DBConnection.sql: SQL-Fehler in {stmt_category}\n"
                    f"{err}\n{sql}\n{logparams}"
                )
            else:
                self._disconnect()
                logger.debug(f'Typ von parameters: {type(parameters)}')
                fehlermeldung = (f"dbqkan.DBConnection.sql: \nsql: {sql}\n"
                                 f"parameters: {logparams}\n"
                                 f"dbqkan.DBConnection.sql: SQL-Fehler {repr(err)} in {stmt_category}"
                )
                logger.error(fehlermeldung)
                raise Exception(f"{self.__class__.__name__}: {fehlermeldung}")
            return False


    def insertdata(
            self,
            tabnam: str,
            stmt_category: str = "allgemein",
            mute_logger: bool = False,
            ignore: bool = False,  # ignore error and continue
            parameters: dict[Union[str, Any], Union[Union[str, float, int], Any]] = None
    ) -> bool:
        """Fügt einen Datensatz mit Geo-Objekt hinzu

        :tabnam:            Tabelle zum Einfügen der Daten
        :stmt_category:     Erläuterung für Protokoll und Fehlermeldungen
        :mute_logger:       suppress logging message for the same stmt_category for 2 seconds
        :ignore:            ignore error and continue
        :parameters:        Parameter für das SQL-Statement, 2 Varainten:
                             - dict:  einzelner Datensatz wird eingefügt
                             - tuple: jeder Datensatz muss ein dict darstellen und wird mit "executemany" eingefügt
        """

        if isinstance(parameters, tuple):
            param1 = parameters[0]
        else:
            param1 = parameters

        if tabnam == "schaechte":
            parlis = [
                "schnam",
                "sohlhoehe",
                "deckelhoehe",
                "durchm",
                "druckdicht",
                "ueberstauflaeche",
                "entwart",
                "strasse",
                "baujahr",
                "teilgebiet",
                "knotentyp",
                "auslasstyp",
                "schachttyp",
                "simstatus",
                "material",
                "kommentar",
                "createdat",
                "xsch",
                "ysch",
                "geom",
                "geop",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_schaechte'

        elif tabnam == "haltungen":
            parlis = [
                "haltnam",
                "baujahr",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "laenge",
                "aussendurchmesser",
                "sohleoben",
                "sohleunten",
                "teilgebiet",
                "profilnam",
                "entwart",
                "strasse",
                "material",
                "profilauskleidung",
                "innenmaterial",
                "ks",
                "haltungstyp",
                "simstatus",
                "kommentar",
                "createdat",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_haltungen'

        elif tabnam == "haltungen_untersucht":
            parlis = [
                "haltnam",
                "bezugspunkt",
                "untersuchrichtung",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "breite",
                "laenge",
                "kommentar",
                "createdat",
                "baujahr",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "untersuchtag",
                "untersucher",
                "wetter",
                "auftragsbezeichnung",
                "strasse",
                "bewertungsart",
                "bewertungstag",
                "datenart",
                "max_ZD",
                "max_ZB",
                "max_ZS",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_haltungen_untersucht'

        elif tabnam == "untersuchdat_haltung":
            parlis = [
                "untersuchhal",
                "schoben",
                "schunten",
                "id",
                "untersuchtag",
                "untersuchrichtung",
                "bandnr",
                "videozaehler",
                "inspektionslaenge",
                "station",
                "timecode",
                "video_offset",
                "kuerzel",
                "langtext",
                "charakt1",
                "charakt2",
                "quantnr1",
                "quantnr2",
                "streckenschaden",
                "streckenschaden_lfdnr",
                "pos_von",
                "pos_bis",
                "foto_dateiname",
                "film_dateiname",
                "ordner_bild",
                "ordner_video",
                "ZD",
                "ZB",
                "ZS",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_untersuchdat_haltung'

        elif tabnam == "anschlussleitungen":
            parlis = [
                "leitnam",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "laenge",
                "aussendurchmesser",
                "sohleoben",
                "sohleunten",
                "baujahr",
                "haltnam",
                "urstation",
                "ursprung",
                "anschlusstyp",
                "lageanschluss",
                "teilgebiet",
                "strasse",
                "profilnam",
                "entwart",
                "material",
                "profilauskleidung",
                "innenmaterial",
                "ks",
                "simstatus",
                "kommentar",
                "createdat",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_anschlussleitungen'

            logger.debug(
                f"insert anschlussleitung - sql: {sqlnam}\n" f"parameter: {param1}"
            )

        elif tabnam == "anschlussleitungen_untersucht":
            parlis = [
                "leitnam",
                "bezugspunkt",
                "untersuchrichtung",
                "schoben",
                "schunten",
                "hoehe",
                "breite",
                "breite",
                "laenge",
                "kommentar",
                "createdat",
                "baujahr",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "untersuchtag",
                "untersucher",
                "wetter",
                "auftragsbezeichnung",
                "strasse",
                "bewertungsart",
                "bewertungstag",
                "datenart",
                "max_ZD",
                "max_ZB",
                "max_ZS",
                "xschob",
                "yschob",
                "xschun",
                "yschun",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_anschlussleitungen_untersucht'

            logger.debug(
                f"insert anschlussleitung - sql: {sqlnam}\n" f"parameter: {param1}"
            )

        elif tabnam == "untersuchdat_anschlussleitung":
            parlis = [
                "untersuchleit",
                "schoben",
                "schunten",
                "id",
                "untersuchtag",
                "bandnr",
                "videozaehler",
                "inspektionslaenge",
                "station",
                "timecode",
                "video_offset",
                "kuerzel",
                "langtext",
                "charakt1",
                "charakt2",
                "quantnr1",
                "quantnr2",
                "streckenschaden",
                "streckenschaden_lfdnr",
                "pos_von",
                "pos_bis",
                "foto_dateiname",
                "film_dateiname",
                "ordner_bild",
                "ordner_video",
                "ZD",
                "ZB",
                "ZS",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_untersuchdat_anschlussleitung'

        elif tabnam == "anschlussschaechte":
            parlis = [
                "schnam",
                "sohlhoehe",
                "deckelhoehe",
                "durchm",
                "druckdicht",
                "ueberstauflaeche",
                "entwart",
                "strasse",
                "baujahr",
                "teilgebiet",
                "knotentyp",
                "auslasstyp",
                "schachttyp",
                "simstatus",
                "material",
                "kommentar",
                "createdat",
                "xsch",
                "ysch",
                "geom",
                "epsg",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_anschlussschaechte'

        elif tabnam == "schaechte_untersucht":
            parlis = [
                "schnam",
                "durchm",
                "baujahr",
                "bezugspunkt",
                "id",
                "untersuchtag",
                "untersucher",
                "wetter",
                "auftragsbezeichnung",
                "strasse",
                "bewertungsart",
                "bewertungstag",
                "datenart",
                "max_ZD",
                "max_ZB",
                "max_ZS",
                "kommentar",
                "createdat",
                "xsch",
                "ysch",
                "geop",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_schaechte_untersucht'

        elif tabnam == "untersuchdat_schacht":
            parlis = [
                "untersuchsch",
                "id",
                "untersuchtag",
                "bandnr",
                "videozaehler",
                "timecode",
                "kuerzel",
                "langtext",
                "charakt1",
                "charakt2",
                "quantnr1",
                "quantnr2",
                "streckenschaden",
                "streckenschaden_lfdnr",
                "pos_von",
                "pos_bis",
                "vertikale_lage",
                "inspektionslaenge",
                "bereich",
                "foto_dateiname",
                "film_dateiname",
                "ordner_bild",
                "ordner_video",
                "ZD",
                "ZB",
                "ZS",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_untersuchdat_schacht'

        elif tabnam == "videos":
            parlis = [
                "name",
                "untersuchtag",
                "untersuchrichtung",
                "objekt",
                "datei",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_videos'

        elif tabnam == "fotos":
            parlis = [
                "name",
                "untersuchtag",
                "objekt",
                "datei",
                "createdat",
            ]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            sqlnam = 'database_insertdata_fotos'

        elif tabnam == 'tezg':
            parlis = ['flnam', 'regenschreiber', 'schnam', 'befgrad', 'neigung',
                       'createdat', 'haltnam', 'neigkl', 'schwerpunktlaufzeit', 'teilgebiet', 'abflussparameter',
                      'kommentar', 'geom', 'epsg']
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sqlnam = 'database_insertdata_tezg'

        elif tabnam == "flaechen":
            parlis = ['flnam', 'haltnam', 'schnam', 'neigkl', 'neigung',
                      'teilgebiet', 'regenschreiber', 'abflussparameter',
                      'aufteilen', 'kommentar', 'createdat',
                      'geom', 'epsg']
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sqlnam = 'database_insertdata_flaechen'

        elif tabnam == "teilgebiete":
            parlis = ["tgnam", "kommentar", "createdat", "geom", "epsg"]
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sqlnam = 'database_insertdata_teilgebiete'

        elif tabnam == 'symbole':
            parlis = ['bezeichnung', 'art', 'gruppe', 'kommentar', 'geom', 'epsg']
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sqlnam = 'database_insertdata_symbole'

        elif tabnam == 'kanalreinigung':
            parlis = ['reinigungsdatum', 'ablagerungen', 'reinigungszeit', 'fahrer', 'beifahrer', 'haltungsnummer',
                      'bemerkung', 'kontorlle', 'haltnam']
            for el in parlis:
                if param1.get(el, None) is None:
                    if isinstance(parameters, tuple):
                        for ds in parameters:
                            ds[el] = None
                    else:
                        parameters[el] = None

            # wkt_geom = param1.get("geom")
            sqlnam = 'database_insertdata_kanalreinigung'

        else:
            logger.warning(
                "dbqkan.DBConnection.insertdata: "
                f"Daten für diesen Layer {tabnam} können (noch) nicht "
                "über die QKan-Clipboardfunktion eingefügt werden"
            )
            return False

        if isinstance(parameters, dict):
            logger.debug(f'read_data.insertdata: einzelner Datensatz')
            result = self.sqlyml(
                sqlnam,
                stmt_category,
                parameters=parameters,
                many=False,
                mute_logger=mute_logger,
                ignore=ignore)
        else:
            logger.debug(f'read_data.insertdata: Tuple von Datensaetzen')
            result = self.sqlyml(
                sqlnam,
                stmt_category,
                parameters=parameters,
                many=True,
                mute_logger=mute_logger,
                ignore=ignore)

        return result

    def executefile(self, filenam, replacefun: Union[callable, None] = None) -> bool:
        """Liest eine Datei aus dem template-Verzeichnis und führt sie als SQL-Befehle aus.
        Dabei wird optional die Funktion replacefun zum Ersetzen von Variablen ausgeführt

        :filenam:               Filename with SQL-script
        :type sqlnam:           String

        :replacefun:            function which replaces variables in sql script
        :type replacefun:       function

        :returns: bool"""
        try:
            with open(filenam) as fr:
                sql_txt = fr.read()

            if replacefun is not None:
                sqltext = replacefun(sql_txt)
                if '{' in sqltext:
                    logger.error_code(
                        f'{self.__class__.__name__}: '
                        f'Fehler in yaml-Datei: sql enthält Parameter, obwohl keine ersetzen-Funktion'
                        f'im Aufruf geliefert wird.')
            else:
                sqltext = sql_txt

            self.cursl.executescript(sqltext)
            return True
        except sqlite3.Error as err:
            msg = f'{self.__class__.__name__}.dbqkan.DBConnection.sql: ' \
                  f'SQL-Fehler beim Ausführen der SQL-Datei\n{repr(err)}\n{filenam}'
            logger.error(msg)
            return False

    def fetchall(self) -> List[Any]:
        """Gibt alle Daten aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten: List[Any] = self.cursl.fetchall()
        return daten

    def fetchone(self) -> Any:
        """Gibt einen Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten = self.cursl.fetchone()
        return daten

    def fetchnext(self) -> Any:
        """Gibt den naechsten Datensatz aus der vorher ausgeführten SQL-Abfrage zurueck"""

        daten = self.cursl.fetchnext()
        return daten

    def commit(self) -> None:
        """Schliesst eine SQL-Abfrage ab"""

        self.consl.commit()

    # Versionskontrolle der QKan-Datenbank

    def rowcount(self) -> int:
        """Gibt die Anzahl zuletzt geänderte Datensätze zurück"""

        return cast(int, self.cursl.rowcount)

    def check_version(self) -> bool:
        """Prüft die Version der Datenbank.

        :returns: Anpassung erfolgreich: True = alles o.k.
        :rtype: logical

        Voraussetzungen:
         - Die aktuelle Datenbank ist bereits geöffnet.

        Die aktuelle Versionsnummer steht in der Datenbank: info.version
        Diese wird mit dem Attribut self.actDbVersion verglichen."""

        logger.debug("0 - actversion = {}".format(self.actDbVersion.base_version))

        # ---------------------------------------------------------------------------------------------
        # Aktuelle Version abfragen

        if not self.sqlyml(
            'database_getversion',
            "dbqkan.DBConnection.version (1)",
        ):
            return False

        data = self.cursl.fetchone()
        if data is not None:
            self.current_dbversion = packaging.version.parse(data[0])
            logger.debug(
                "dbqkan.DBConnection.version: Aktuelle Version der qkan-Datenbank ist {}".format(
                    self.current_dbversion.base_version
                )
            )
        else:
            logger.debug(
                "dbqkan.DBConnection.version: Keine Versionsnummer vorhanden. data = {}".format(
                    repr(data)
                )
            )
            if not self.sqlyml(
                'database_insertversion',
                "dbqkan.DBConnection.version (2)",
            ):
                return False

            self.current_dbversion = packaging.version.parse("1.9.9")

        logger.debug(f"0 - versiondbQK = {self.current_dbversion.base_version}")

        self.isCurrentDbVersion = (self.actDbVersion <= self.current_dbversion)
        self.isCurrentVersion = self.isCurrentDbVersion                    # nur aus Kompatibilitätsgründen

        # Warnung, falls geladene Datenbank neuer als die Datenbankversion zu diesem QKan-Plugin ist.
        # if self.actDbVersion > self.current_dbversion:
        #     logger.warning("Die QKan-Version ist älter als die QKan-Datenbank. "
        #                    "Bitte führen Sie ein Upgrade des QKan-Plugins aus")


    # Ändern der Attribute einer Tabelle

    def alter_table(
        self,
        tabnam: str,
        attributes_new: List[str],
        attributes_del: List[str] = None,
        geo_attrchange: str = None,
        geo_newtype: str = None,
        geo_modfun: str = None,
    ) -> bool:
        """Changes attribute columns in QKan tables except geom columns.

        :tabnam:                Name der Tabelle
        :attributes_new:        bestehende und neue Attribute, Syntax wie in Create-Befehl, ohne Primärschlüssel
                                und Geometrieobjekte.
                                Alle übrigen Attribute aus der alten Tabelle, die nicht entfernt werden sollen,
                                werden zufällig sortiert dahinter angeordnet übernommen.
        :attributes_del:        zu entfernende Attribute
        :geoattr_change:        Geometrieattribut, dessen Type geändert werden soll
        :geonewtype:            neuer Geotyp
        :geomodfun:             SQL-Expression zur Konvertierung der Geometrieobjekte

        Ändert die Tabelle so, dass sie die Attribute aus attributesNew in der gegebenen
        Reihenfolge sowie die in der bestehenden Tabelle vom Benutzer hinzugefügten Attribute
        enthält. Nur falls attributesDel Attribute enthält, werden diese nicht übernommen.
        Weiterhin kann der Type eines Geometrieattributs geändert werden. Dabei muss eine Konvertierungsfunktion
        als SQL-Expression angegeben werden,
        z. B. (geo_modfun = 'CastToMultiLineString(LinesFromRings(geom)) AS geom'

        example:
        alter_table(
            tabnam=         'flaechen',
            attributes_new= [
               'flnam TEXT',
               'haltnam TEXT',
               'neu1 REAL',
               'neu2 TEXT                              /* Kommentar */',
               "simstatus TEXT DEFAULT 'vorhanden'",
               'teilgebiet TEXT                        /* Kommentar */',
               "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
            ],
            attributes_del= ['entfernen1', 'entfernen2'],
            geo_attrchange= 'geom',
            geo_newtype=    'MULTILINESTRING',
            geo_modfun=     'CastToMultiLineString(LinesFromRings(geom)) AS geom',
            )
        """

        # Attributlisten
        # Schema:
        # - attrSet.. ist ein Set, das nur die Attributnamen enthält
        # - attrDict.. ist ein Dict, das als Key den Attributnamen und als Wert die SQL-Definitionszeile enthält
        # - ..Old enthält die Attribute der bestehenden Tabelle inkl. der Benutzerattribute,
        #     ohne Primärschlüssel sowie Geoobjekte
        # - ..New enthält die Attribute nach dem Update ohne Benutzerattribute, Primärschlüssel sowie Geoattribute
        # - ..Diff enthält die zu übertragenden Attribute inkl. Geoattribute

        # - attrPk:string enthält den Namen des Primärschlüssels

        geo_types = QKan.geotypes

        # No SQL injection:
        tabnam = cleanname(tabnam)

        # 1. bestehende Tabelle
        # Benutzerdefinierte Felder müssen übernommen werden

        if not self.sqlyml(
            'database_tableinfo',
            "dbqkan.DBConnection.alter_table (1)",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam)
        ):
            return False
        data = self.fetchall()
        attr_pk = [el[1] for el in data if el[5] == 1][0]
        attr_dict_old = dict(
            [
                (
                    el[1],
                    el[1]
                    + " "
                    + el[2]
                    + ("" if el[4] is None else f" DEFAULT {el[4]}"),
                )
                for el in data
                if el[5] == 0
            ]
        )
        attrs_old = attr_dict_old.keys()

        attrs_del = attributes_del if attributes_del is not None else []

        # Geometrieattribute
        if not self.sqlyml(
            'database_tableinfo_geometry_columns',
            "dbqkan.DBConnection.alter_table (2)",
            parameters=(tabnam,),
        ):
            return False
        data = self.fetchall()
        attr_dict_geo = dict(
            [
                (
                    el[0],
                    [
                        el[0],
                        geo_types[el[1]],
                        el[2],
                        el[3]]
                ) for el in data]
        )

        attrs_geo = list(attr_dict_geo.keys())

        attrs_new = [el.strip().split(" ", maxsplit=1)[0] for el in attributes_new]

        # Hinzufügen der Benutzerattribute
        # attr_set_new |= attr_set_old
        attrs_new += [el for el in attrs_old if el not in attrs_new]

        # Entfernen von Primärschlüssel, Geoattributen und zu Löschenden Attributen
        attrs_new = [el for el in attrs_new if el not in attrs_del + [attr_pk] + attrs_geo]

        # Attribute zur Datenübertragung zwischen alter und neuer Tabelle.
        # attr_set_both = set(attr_set_old) & set(attr_set_new)
        attrs_both = [el for el in attrs_old if el in attrs_new]

        # Austausch des zu ändernden Geoobjekts durch Umwandlungsausdruck geo_modfun
        attrs_geo_mod = attrs_geo.copy()
        if geo_attrchange is not None:
            # Alten durch neuen Geometrietyp ersetzen
            attr_dict_geo[geo_attrchange][1] = geo_newtype
            # Zu änderndes Geoobjekt durch Expression ersetzen
            attrs_geo_mod = attrs_geo.copy()
            posgeo = attrs_geo_mod.index(geo_attrchange)
            attrs_geo_mod[posgeo] = geo_modfun

        # ------------------------------------------------------------------
        # Zusammenstellen der Parameter für die SQL-Abfragen

        # Datenübertragung
        attr_text_both = ', '.join(attrs_both + attrs_geo) + '\n'
        logger.debug(f"dbqkan.DBConnection.alter_table - {attr_text_both=}")

        # Falls notwendig, Quelle für Datenübertragung mit Typumwandlung
        if geo_attrchange is None:
            attr_text_source = attr_text_both
        else:
            attr_text_source = ', '.join(attrs_both + attrs_geo_mod) + '\n'
        logger.debug(f"dbqkan.DBConnection.alter_table - {attr_text_source=}")

        # Parameter für Create-Anweisung
        # Primärschlüssel
        attr_dict_new = {attr_pk: f"{attr_pk} INTEGER PRIMARY KEY"}
        # Zusammenstellen aller Attribute in der neuen Tabelle inkl. Benutzerattributen
        for el in attributes_new:
            attr = el.strip().split(" ")[0].strip()
            typ = el.strip()
            attr_dict_new[attr] = typ
        # Hinzufügen aller Attribute der bisherigen Tabelle (dies umfasst auch die Benutzerattribute)
        for attr in attrs_old:
            if attr not in attr_dict_new:
                attr_dict_new[attr] = attr_dict_old[attr]
        # Entfernen der zu entfernenden Attribute:
        for attr in attrs_del:
            if attr in attr_dict_new:
                del attr_dict_new[attr]
        # Zur Sicherheit: Entfernen aller Geoattribute
        for attr in attrs_geo:
            if attr in attr_dict_new:
                del attr_dict_new[attr]

        logger.debug(f'{attr_dict_new=}')

        # Attribute der neuen Tabelle als String für SQL-Anweisung
        attr_text_create = "\n,".join(attr_dict_new.values())+"\n"
        logger.debug(f"dbqkan.DBConnection.alter_table - {attr_text_create=}")

        # 0. Foreign key constraint deaktivieren
        if not self.sqlyml(
            'database_foreign_key_off',
            "dbqkan.DBConnection.alter_table (3)",
        ):
            return False

        # ------------------------------------------------------------------
        # Transfer ausführen

        # 2.1. Temporäre Hilfstabelle erstellen

        if not self.sqlyml(
            'database_create_temp_table',
            "dbqkan.DBConnection.alter_table (6)",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam, attr_text_create=attr_text_create)
        ):
            logger.error_code(
                f'{self.__class__.__name__}: '
                f'Fehler in SQL=database_create_temp_table')

        # 2.2. Geo-Attribute in Tabelle ergänzen
        for attr in attrs_geo:
            gnam, geotype, epsg, nccords = attr_dict_geo[attr]
            if not self.sqlyml(
                'database_altertable_addgeometrycolumn',
                "dbqkan.DBConnection.alter_table (7)",
                parameters=(f'{tabnam}_t', gnam, epsg, geotype, nccords),
                ):
                return False

        # 3. Hilfstabelle entleeren
        if not self.sqlyml(
            'database_delete',
            "dbqkan.DBConnection.alter_table (8)",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam)
        ):
            return False

        # 4. Daten aus Originaltabelle übertragen, dabei nur gemeinsame Attribute berücksichtigen
        if not self.sqlyml(
            sqlnam='database_transfer_t',
            stmt_category="dbqkan.DBConnection.alter_table (9)",
            replacefun=lambda sqltext: sqltext.format(
                tabnam=tabnam,
                attr_text_aim=   attr_text_both,
                attr_text_source=attr_text_source,
            )
        ):
            return False

        # 5.1. Löschen der Geoobjektattribute
        for attr in attrs_geo:
            if not self.sqlyml(
                'database_altertable_discardgeometrycolumn',
                "dbqkan.DBConnection.alter_table (10)",
                parameters=(tabnam, attr),
                ):
                return False

        # 5.2. Löschen der Tabelle
        if not self.sqlyml(
            'database_drop_table',
            "dbqkan.DBConnection.alter_table (11)",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam)
        ):
            return False

        # 6.1 Geänderte Tabelle erstellen
        if not self.sqlyml(
            'database_create_table',
            "dbqkan.DBConnection.alter_table (12)",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam, attr_text_create=attr_text_create)
        ):
            return False

        # 6.2. Geo-Attribute in Tabelle ergänzen und Indizes erstellen
        for attr in attrs_geo:
            gnam, geotype, epsg, nccords = attr_dict_geo[attr]
            if not self.sqlyml(
                'database_altertable_addgeometrycolumn',
                "dbqkan.DBConnection.alter_table (13)",
                parameters=(tabnam, gnam, epsg, geotype, nccords),
                ):
                return False

            if not self.sqlyml(
                'database_altertable_createspatialindex',
                "dbqkan.DBConnection.alter_table (14)",
                parameters=(tabnam, attr),
                ):
                return False

        # 7. Daten aus Hilfstabelle übertragen, dabei nur gemeinsame Attribute berücksichtigen
        if not self.sqlyml(
            'database_transfer',
            "dbqkan.DBConnection.alter_table (15)",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam, attr_text_both=attr_text_both)
        ):
            return False

        # 8.1. Löschen der Geoobjektattribute der Hilfstabelle
        for attr in attrs_geo:
            if not self.sqlyml(
                'database_altertable_discardgeometrycolumn',
                "dbqkan.DBConnection.alter_table (16)",
                parameters=(f"{tabnam}_t", attr),
                ):
                return False

        # 9. Löschen der Hilfstabelle
        if not self.sqlyml(
            'database_drop_table_t',
            "dbqkan.DBConnection.alter_table (17)",
            replacefun=lambda sqltext: sqltext.format(tabnam=tabnam)
        ):
            return False

        # 9. Indizes und Trigger wiederherstellen
        # for sql in triggers:
        #     if not self.sql(sql, 'dbqkan.DBConnection.alter_table (18)'):
        #         return False

        # 10. Verify key constraints
        if not self.sqlyml(
            'database_foreign_check',
            "dbqkan.DBConnection.alter_table (19)",
        ):
            return False

        # 11. Transaktion abschließen
        self.commit()

        # 12. Foreign key constrain wieder aktivieren
        if not self.sqlyml(
            'database_foreign_on',
            "dbqkan.DBConnection.alter_table (20)",
        ):
            return False

        return True

    def upgrade_database(self) -> bool:
        """
        Ugprades the existing database to the current version.

        Each migration is run separately to ensure that we always end up at a
        consistent state, even if an upgrade fails.
        Once we are done, the user is told to reload the project as glitches
        may occur.
        """

        from .migrations import find_migrations

        # Database is already on the current version
        if self.check_version():
            return True

        logger.debug(
            "dbqkan.DBConnection.updateversion: versiondbQK = %s", self.current_dbversion.base_version
        )

        progress_bar = QProgressBar(QKan.instance.iface.messageBar())
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)

        migrations = find_migrations(self.current_dbversion)
        for i, migration in enumerate(migrations):
            if not migration.run(self):
                errormsg = f"Fehler beim Ausführen des Datenbankupdates {migration.name}."
                logger.error(errormsg)
                raise QkanAbortError(errormsg)

            if not self.sqlyml(
                'database_update_info',
                "dbqkan.DBConnection.version (aktuell)",
                parameters=(str(migration.version),),
            ):
                logger.error_code("Versionsnummer konnte nicht aktualisiert werden!")
                raise QkanAbortError

            # Update progress bar
            progress_bar.setValue(100 // len(migrations) * (i + 1))

        self.commit()

        if self.reload:
            # logger.info(
            #     "Achtung! Benutzerhinweis!\n" + \
            #     "Die Datenbank wurde geändert. Bitte QGIS-Projekt nach dem Speichern neu laden...",
            # )
            return False

        self.isCurrentDbVersion = True
        self.isCurrentVersion = True                    # nur aus Kompatibilitätsgründen

        return True

    def get_from_mapper(
        self,
            key: str,
            mapper: dict,
            table: str,
            reftable: str = None,
            attr_name: str = None,
            attr_key: str = None,
            attr_bem: str = None,
            attr_short: str = None,
            default: str = None
    ) -> Union[bool, str, None]:
        """Liefert Langbezeichnung für einen key mit Hilfe eines mappers.
    Wenn der key im mapper nicht vorhanden ist, wird der key sowohl
    im mapper als auch der zugehörigen Datenbanktabelle ergänzt.

    :param key:                 gelesener Schlüsselwert
    :param mapper:              Schlüsselwerte mit zugeodneten Feldwerten
    :param table:               Name der Tabelle, in die der Feldwert eingetragen werden soll. Nur für Fehlermeldung benötigt!
    :param reftable:            Name der Referenztabelle
    :param attr_name:           Referenztabelle: Attributname der Langbezeichnung
    :param attr_key:            Referenztabelle: Attributname des Schlüsselwertes
    :param attr_bem:            Referenztabelle: Attributname des Kommentarwertes
    :param attr_short:          Referenztabelle: Attributname der Kurzbezeichnung
    :param default:             optional: Defaultwert, falls key None ist
        """

        if key in mapper:
            result = mapper[key]
        elif key is None:
            result = default
        elif reftable is not None:
            # interne Mapper ausschließen
            result = key
            mapper[key] = key  # Ergänzung des Dict braucht nicht zurückgegeben werden

            if attr_short is None:
                params = (result, result, 'unbekannt')
                if not self.sqlyml(
                    'database_insert_into',
                    f"{table}: nicht zugeordneter Wert für {reftable}",
                    params,
                    replacefun=lambda sqltext: sqltext.format(
                        reftable=reftable,
                        attr_name=attr_name,
                        attr_key=attr_key,
                        attr_bem=attr_bem
                    )
                ):
                    return False
            else:
                params = (result, result, result, 'unbekannt')
                if not self.sqlyml(
                    'database_insert_short',
                    f"{table}: nicht zugeordneter Wert für {reftable}",
                    params,
                    replacefun=lambda sqltext: sqltext.format(
                        reftable=reftable,
                        attr_name=attr_name,
                        attr_key=attr_key,
                        attr_short=attr_short,
                        attr_bem=attr_bem
                    )
                ):
                    return False
        else:
            result = key
            mapper[key] = key  # Ergänzung des Dict braucht nicht zurückgegeben werden

        return result

    def consume_mapper(self, sql: str, subject: str, target: Dict[str, str]) -> None:
        if not self.sql(sql, subject):
            raise Exception(f"Failed to init {subject} mapper")
        for row in self.fetchall():
            target[row[0]] = row[1]

    def consume_mapper_yml(self, sqlnam: str, subject: str, target: Dict[str, str]) -> None:
        if not self.sqlyml(sqlnam, subject):
            raise Exception(f"Failed to init {subject} mapper (yml)")
        for row in self.fetchall():
            target[row[0]] = row[1]

    def _adapt_reftable(self, module: str, subject: str) -> None:
        """Ersetzt die importierten Bezeichnungen der Referenztabelle durch die QKan-Standards.
        Die Zuordnungen werden aus einer YAML-Datei "patterns.yml" im Modulverzeichnis gelesen.

        :param modul:   Modulname = Verzeichnisname
        :param subject: Bezeichnung der QKan-Tabelle oder interner Mapping-Tabelle
        :returns: None
           """

        filename = os.path.join(pluginDirectory("qkan"), module, 'patterns.yml')
        with open(filename) as fr:
            patternDict = yaml.safe_load(fr.read())
        patterns = patternDict[subject]

        if patterns is None:
            logger.error_code(f'Für {subject} konnten keine Einträge gefunden werden.')
            raise QkanAbortError

        if not self.sqlyml(
            sqlnam='database_get_bezeichnung',
            stmt_category= f'Anpassen der Referenzdaten zum Thema {module}.{subject} an den QKan-Standard (1)',
            parameters={'subject': subject}
        ):
            raise QkanDbError

        for data in self.fetchall():
            # data enthält nur Datensätze, bei denen die Zuordnung leer ist.
            bezext = data[0]
            for bezqkan in patterns.keys():
                # Schleife über alle QKan-Bezeichnungen
                for patt in patterns[bezqkan]:
                    # Schleife über die Matchliste
                    if fnmatch(bezext.strip().lower(), patt.lower()):
                        # Match gefunden
                        logger.debug(f'Match gefunden: {bezext=}, {patt=}')
                        if not self.sqlyml(
                            sqlnam='database_set_bezeichnung',
                            stmt_category=f'Anpassen der Referenzdaten an den QKan-Standard (2)',
                            parameters={'bezqkan': bezqkan, 'bezext': bezext, 'subject': subject},
                        ):
                            raise QkanDbError
                        break
                    logger.debug(f'Match passt nicht: {bezext=}, {patt=}')
        self.commit()

    def getSelection(self, selected: bool = True):
        """Übernahme der aktuellen Selektion in temporäre Tabellen.
           Falls selected == False: Nur Zählen der Gesamtzahlen"""

        n_haltungen, n_schaechte, n_flaechen = 0, 0, 0
        project = QgsProject.instance()

        if selected:
            # Tabellen neu anlegen und, falls schon vorhanden, zurücksetzen
            sqllis = [
                'database_create_sel_haltungen',
                'database_create_sel_schaechte',
                'database_create_sel_flaechen',
                'database_clear_sel_haltungen',
                'database_clear_sel_schaechte',
                'database_clear_sel_flaechen',]
            for sqlnam in sqllis:
                if not self.sqlyml(
                    sqlnam=sqlnam,
                    stmt_category= f'Erzeugen der temporären Selektionstabelle: {sqlnam}'
                ):
                    raise Exception(f"{self.__class__.__name__}: errno. 101")

        for layer in project.mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value):
            sel = layer.selectedFeatures()
            n_haltungen = len(sel)
            if selected:
                for feat in sel:
                    params = {'pk': feat[0]}
                    if not self.sqlyml('database_insert_sel_haltungen', 'insert selected haltungen', parameters=params):
                        raise Exception(f"{self.__class__.__name__}: errno. 102")
                    logger.debug(f'sel: Haltung hinzugefügt: {params}')
                break               # nur 1. gefundener Layer ;)
        for layer in project.mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value):
            sel = layer.selectedFeatures()
            n_schaechte = len(sel)
            if selected:
                for feat in sel:
                    params = {'pk': feat[0]}
                    if not self.sqlyml('database_insert_sel_schaechte', 'insert selected schaechte', parameters=params):
                        raise Exception(f"{self.__class__.__name__}: errno. 103")
                    logger.debug(f'sel: Schacht hinzugefügt: {params}')
                    n_schaechte += 1
                break               # nur 1. gefundener Layer ;)
        for layer in project.mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value):
            sel = layer.selectedFeatures()
            n_flaechen = len(sel)
            if selected:
                for feat in sel:
                    params = {'pk': feat[0]}
                    if not self.sqlyml('database_insert_sel_flaechen', 'insert selected flaechen', parameters=params):
                        raise Exception(f"{self.__class__.__name__}: errno. 104")
                    logger.debug(f'sel: Fläche hinzugefügt: {params}')
                    n_flaechen += 1
                break               # nur 1. gefundener Layer ;)

        self.commit()

        return n_haltungen, n_schaechte, n_flaechen
