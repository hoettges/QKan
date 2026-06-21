import math
import os
import warnings
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union
from xml.etree.ElementTree import ElementTree
import yaml
from fnmatch import fnmatch
import re

from qgis.PyQt.QtCore import QStandardPaths
from qgis.PyQt.QtWidgets import QListWidget
from pathlib import Path

from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsDataSourceUri, QgsVectorLayer
from qgis.utils import iface, pluginDirectory
from math import ceil
from qkan import QKan, enums
from ..utils import get_logger, QkanUserError

if TYPE_CHECKING:
    from ..database.dbfunc import DBConnection

# Anbindung an Logging-System (Initialisierung in __init__)
logger = get_logger("QKan.database.qkan_utils")


# Fortschritts- und Fehlermeldungen
def meldung(title: str, text: str) -> None:
    warnings.warn("deprecated, use logger.notice instead", DeprecationWarning)

    logger.info("{:s} {:s}".format(title, text))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="{:s} {:s}".format(title, text), tag="QKan", level=Qgis.MessageLevel.Info
    )
    # QKan.instance.iface.messageBar().pushMessage(title, text, level=Qgis.MessageLevel.Info)


def warnung(title: str, text: str, duration: int = -1) -> None:
    warnings.warn("deprecated, use logger.warning instead", DeprecationWarning)

    logger.warning("{:s} {:s}".format(title, text))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="{:s} {:s}".format(title, text), tag="QKan", level=Qgis.MessageLevel.Warning
    )
    # QKan.instance.iface.openMessageLog()
    # QKan.instance.iface.messageBar().pushMessage(
    #     title, text, duration=duration, level=Qgis.MessageLevel.Warning
    # )


def fortschritt(text: str, prozent: float = 0) -> None:
    logger.debug("{:s} ({:.0f}%)".format(text, prozent * 100))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="{:s} ({:.0f}%)".format(text, prozent * 100),
        tag="QKan",
        level=Qgis.MessageLevel.Info,
    )


def fehlermeldung(title: str, text: str = "") -> None:
    warnings.warn("deprecated, use logger.error instead", DeprecationWarning)

    logger.error("{:s} {:s}".format(title, text))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="{:s} {:s}".format(title, text), tag="QKan", level=Qgis.MessageLevel.Critical
    )
    # QKan.instance.iface.messageBar().pushMessage(title, text, level=Qgis.MessageLevel.Critical)


# Allgemeine Funktionen

def get_layer_config_from_qgs_template(
    qgsxml: ElementTree, layername: str
) -> Tuple[Dict[str, Tuple[str, dict]], str]:
    """Liefert Parameter für QgsEditorWidgetSetup aus Qgs-Datei für alle Attribute in einem Layer

    :qgsxml:            XML-Struktur der Projektdatei
    :layername:         Name des Layers

    :returns:           Dictionary of attributnames: edit_widget_type, Dictionary of Options
    :type:              dict of string: tuple of String, dict of Strings
    """

    lntext = "projectlayers/maplayer[layername='{ln}']".format(ln=layername)
    node_maplayer = qgsxml.find(lntext)
    if node_maplayer:
        fieldnodes = node_maplayer.findall("./fieldConfiguration/field")
        display_expression = node_maplayer.findtext("previewExpression") or ""
    else:
        fieldnodes = []
        display_expression = ""

    dict_of_edit_widgets: Dict[
        str, Tuple[str, dict]
    ] = {}  # return: dictOfEditWidgets: init
    for field in fieldnodes:
        attr = field.attrib
        # logger.debug('editWidget: {}'.format(attr))
        fieldname: str = attr["name"]  # return: fieldname
        ew_node = field.find("./editWidget")
        if not ew_node:
            continue

        attr = ew_node.attrib
        edit_widget_type = attr["type"]  # return: edit_widget_type
        if edit_widget_type in ("TextEdit", "ValueRelation"):
            option_nodes = ew_node.findall("./config/Option/Option")
            edit_widget_options = {}  # return: editWidgetOptions: init
            for optionNode in option_nodes:
                attr = optionNode.attrib
                option_name = attr["name"]
                option_value = attr["value"]
                # logger.debug("option: '{key}': {attr}".format(key=optionName, attr=optionValue))    # print
                edit_widget_options[
                    option_name
                ] = option_value  # return: editWidgetOptions
            dict_of_edit_widgets[fieldname] = (edit_widget_type, edit_widget_options)
            # logger.debug('dictOfEditWidgets: {}'.format(dictOfEditWidgets))
        elif edit_widget_type == "ValueMap":
            option_nodes = ew_node.findall("./config/Option/Option/Option")
            edit_widget_options = {}  # return: editWidgetOptions: init
            for optionNode in option_nodes:
                attr = optionNode.attrib
                option_name = attr["name"]
                option_value = attr["value"]
                # logger.debug("option: '{key}': {attr}".format(key=optionName, attr=optionValue))    # print
                edit_widget_options[
                    option_name
                ] = option_value  # return: editWidgetOptions
            dict_of_edit_widgets[fieldname] = (
                edit_widget_type,
                {"map": edit_widget_options},
            )
            # logger.debug('dictOfEditWidgets: {}'.format(dictOfEditWidgets))

    return dict_of_edit_widgets, display_expression


def list_qkan_layers(qgs_template: str = None) -> Dict[str, List]:
    """Dictionary mit den Namen aller QKan-Layer und einer Liste mit:
        Tabellenname, Geometriespalte, SQL-Where-Bedingung, Gruppenname

    Die Zusammenstellung wird aus der Template-QKanprojektdatei gelesen
    """
    if not qgs_template:
        return {}
        # templateDir = os.path.join(pluginDirectory('qkan'), "templates")
        # qgsTemplate = os.path.join(templateDir, 'Projekt.qgs')

    qgsxml = ElementTree()
    qgsxml.parse(qgs_template)

    # Search all levels of nested groups
    tag_group = "layer-tree-group/layer-tree-group/[@name='QKan']"
    qgs_groups = []
    while True:
        qqsgroup = qgsxml.findall(tag_group)
        if not qqsgroup:
            break
        qgs_groups += qqsgroup
        tag_group += '/layer-tree-group'
    qkan_layers = {}
    for group in qgs_groups:
        group_name = group.attrib["name"]
        group_layers = group.findall("layer-tree-layer")
        for layer in group_layers:
            layer_name = layer.attrib.get("name", None)
            if layer_name:
                # only when group level has layers ...
                layer_source = layer.attrib["source"]
                dbname, table, geom, sql = get_qkanlayer_attributes(layer_source)
                qkan_layers[layer_name] = [table, geom, sql, group_name]
    # logger.debug("qkan_layers: \n{}".format(qkan_layers))
    return qkan_layers


def is_qkan_layer(layername: str, source: str) -> bool:
    """Ermittelt, ob eine Layerquelle auf eine QKan-Tabelle verweist

    :layername:      Name des Layers
    :source:        Pfad zur QKan-Datenbank

    :returns:       Ergebnis der Prüfung
    """

    dbname, table, geom, sql = get_qkanlayer_attributes(source)

    qkan_layers = list_qkan_layers()
    if layername in qkan_layers:
        if (
            table == qkan_layers[layername][0]
            and geom == qkan_layers[layername][1]
            and sql == qkan_layers[layername][2]
        ):
            ve = geom != ""  # Vectorlayer?
            return True
    return False


def get_qkanlayer_attributes(source: str) -> Tuple[str, str, str, str]:
    """Ermittelt die Attribute eines QKan-Layers in einer SpatiaLite-Datenbank

    :param source:  Source-String des QGIS-Layers
    :returns:       database name, table name, geom, sql
    """

    pos = source.find("sql=")
    if pos >= 0:
        sql = source[pos + 4 :]
        source = source[: pos - 1]
    else:
        sql = ""

    pos = -1
    while source.find("(", pos + 1) >= 0:
        pos = source.find("(", pos + 1)
    if pos >= 0:
        geom = source[pos + 1 : -1]
        source = source[: pos - 1]
    else:
        geom = ""

    pos = source.find("table=")
    if pos >= 0:
        table = source[pos + 7 : -1]
        source = source[: pos - 1]
    else:
        table = ""

    pos = source.find("dbname=")
    if pos >= 0:
        dbname = source[pos + 8 : -1]
        source = source[: pos - 1]
    else:
        dbname = ""

    return dbname, table, geom, sql


def set_qkanlayer_dbname(oldsource: str, newdb: str) -> str:
    """Ersetzt Pfad in QgsConnectionstring"""

    dbname_o, table, geom, sql = get_qkanlayer_attributes(oldsource)
    dbname_t = f"dbname='{newdb}'"                      # obligatory in QKan
    table_t = f' table="{table}"'                       # obligatory in QKan
    geom_t = f' ({geom})' if geom != '' else ''
    sql_t = f' sql={sql}' if sql != '' else ''
    newsource = dbname_t + table_t + geom_t + sql_t
    return newsource


def get_database_QKan(silent: bool = False) -> None:
    """Ermittlung der aktuellen Datenbank aus den geladenen Layern. Ergebnisse werden in QKan.config gespeichert"""

    # noinspection PyArgumentList

    project = QgsProject.instance()
    qkanlayers = [enums.LAYERBEZ.SCHAECHTE.value, enums.LAYERBEZ.HALTUNGEN.value, enums.LAYERBEZ.EINZELFLAECHEN.value]
    for lnam in qkanlayers:
        layerobjects = project.mapLayersByName(lnam)
        if len(layerobjects) > 0:
            break
    else:
        return

    layer = layerobjects[0]
    # only once for loaded project
    if not QKan.dbsource or layer.publicSource() != QKan.dbsource:
        QKan.dbsource = layer.publicSource()

        provider = layer.dataProvider()
        if provider.name() == 'postgres':
            QKan.dbtype = enums.QKanDBChoice.POSTGIS
        elif provider.name() == 'spatialite':
            QKan.dbtype = enums.QKanDBChoice.SPATIALITE
            data_source_uri = QgsDataSourceUri(provider.dataSourceUri())
            QKan.config.database.qkan = data_source_uri.database()
            QKan.config.epsg = provider.crs().postgisSrid()
        else:
            logger.error_code(f"no or wrong dataProvider {provider.name()}")


def get_editable_layers() -> Set[str]:
    """Liste der aktuell editierbaren Layer.
    Dient dazu, sicherzustellen, dass keine Datenbankoperationen auf editierbare
    Layer zugreifen.

    :returns:   Set mit allen editierbaren Layern.
    """

    elayers = set([])  # Zuerst leere Liste anlegen

    layers = [x.layer() for x in iface.layerTreeCanvasBridge().rootGroup().findLayers()]
    # über Layer iterieren
    for lay in layers:
        lyattr = {}

        # Attributstring für Layer splitten
        for le in lay.source().split(" "):
            if "=" in le:
                key, value = le.split("=", 1)
                lyattr[key] = value.strip('"').strip("'")

        # Falls Abschnitte 'table' und 'dbname' existieren, handelt es sich um einen Datenbank-Layer
        if "table" in lyattr and "dbname" in lyattr:
            if lay.isEditable():
                elayers.add(lay.name())
    return elayers


def checknames(
    db_qkan: "DBConnection", tab: str, attr: str, prefix: str, autokorrektur: bool
) -> bool:
    """Prüft, ob in der Tabelle {tab} im Attribut {attr} eindeutige Namen enthalten sind.
    Falls nicht, werden Namen vergeben, die sich aus {prefix} und ROWID zusammensetzen

    :param db_qkan:         Typ der Datenbank (spatialite, postgis)
    :param tab:             Name der Tabelle
    :param attr:            Name des Attributs, das die eindeutige Bezeichnung enthalten soll
    :param prefix:          Kürzel, das bei fehlenden oder nicht eindeutigen Bezeichnungen vor
                            die ROWID gesetzt wird
    :param autokorrektur:   Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                            werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                            abgebrochen.

    :returns:               Ergebnis der Prüfung bzw. Korrektur
    """

    # ----------------------------------------------------------------------------------------------------------------
    # Prüfung, ob Objektnamen leer oder NULL sind:

    db_qkan.loadmodule('database')
    if not db_qkan.sqlyml(
        'database_checknames',
        "QKan.qgis_utils.checknames (1)",
        replacefun=lambda sqltext: sqltext.format(attr=attr, tab=tab)
    ):
        return False

    daten = db_qkan.fetchall()

    if len(daten) > 0:
        if autokorrektur:
            meldung(
                "Automatische Korrektur von Daten: ",
                'In der Tabelle "{tab}" wurden leere Namen im Feld "{attr}" aufgefüllt'.format(
                    tab=tab, attr=attr
                ),
            )

            if not db_qkan.sqlyml(
                'database_correct_names',
                "QKan.qgis_utils.checknames (2)",
                replacefun=lambda sqltext: sqltext.format(tab=tab, attr=attr, prefix=prefix)
            ):
                return False
        else:
            fehlermeldung(
                "Datenfehler",
                'In der Tabelle "{tab}" gibt es leere Namen im Feld "{attr}". Abbruch!'.format(
                    tab=tab, attr=attr
                ),
            )
            return False

    # ----------------------------------------------------------------------------------------------------------------
    # Prüfung, ob Objektnamen mehrfach vergeben sind.

    if not db_qkan.sqlyml(
        'database_checkmultiple',
        "QKan.qgis_utils.checknames (3)",
        replacefun=lambda sqltext: sqltext.format(attr=attr, tab=tab)
    ):
        return False

    daten = db_qkan.fetchall()

    if len(daten) > 0:
        if autokorrektur:
            meldung(
                "Automatische Korrektur von Daten: ",
                'In der Tabelle "{tab}" gibt es doppelte Namen im Feld "{attr}"'.format(
                    tab=tab, attr=attr
                ),
            )

            if not db_qkan.sqlyml(
                'database_correct_multiple',
                "QKan.qgis_utils.checknames (4)",
                replacefun=lambda sqltext: sqltext.format(attr=attr, tab=tab, prefix=prefix)
            ):
                return False
        else:
            fehlermeldung(
                "Datenfehler",
                'In der Tabelle "{tab}" gibt es doppelte Namen im Feld "{attr}". Abbruch!'.format(
                    tab=tab, attr=attr
                ),
            )
            return False

    return True


def sqlconditions(keyword: str, attrlis: List[str], valuelis2: List[List[str]]) -> str:
    """
    Stellt Attribut- und Wertelisten zu einem SQL-String zusammen.

    :param keyword:     logischer Operator, mit dem der SQL-Text an den vorhandenen
                        SQL-Text angehängt werden soll
    :param attrlis:     Liste von Attribunten, ggfs. mit Tabellennamen. Anzahl muss mit
                        valuelis2 korrespondieren
    :param valuelis2:   Liste aus Listen mit Werten. Anzahl muss mit attrlis korrespondieren

    :returns:           Anhang zu einem SQL-Statement mit führendem Leerzeichen

    Example: sqlconditions('WHERE', ('flaechen.teilgebiet', 'flaechen.abflussparameter'),
                                    (liste_teilegebiete, liste_abflussparamerer))
    """

    # Falls keine Wertelisten gegeben oder alle Wertelisten leer sind, wird ein Leerstring zurückgeben
    for el in valuelis2:
        if len(el) > 0:
            break
    else:
        return ""

    if len(attrlis) != len(valuelis2):
        fehlermeldung=(
            "Fehler in qkan_utils.sqlconditions:\n"
            "Anzahl an Attributen und Wertlisten stimmt nicht ueberein: \n"
            f"attrlis= {attrlis}\n"
            f"valuelis2= {valuelis2}\n"
        )
        logger.error_code(fehlermeldung)

    condlis = []  # Liste der einzelnen SQL-Conditions

    for attr, valuelis in zip(attrlis, valuelis2):
        if len(valuelis) != 0:
            condlis.append(
                "{attr} in ('{values}')".format(attr=attr, values="', '".join(valuelis))
            )
    if len(condlis) != 0:
        auswahl = " {keyword} {conds}".format(
            keyword=keyword, conds=" AND ".join(condlis)
        )
    else:
        auswahl = ""

    return auswahl


def check_flaechenbilanz(db_qkan: "DBConnection") -> bool:
    """
    Prüft Übereinstimmung der Flächensumme der Flächen und der verschnittenen Flächen.
    Wird für die Erstellung der Flächenverknüpfungen benötigt.

    :param db_qkan:     Typ der Datenbank (spatialite, postgis)
    """

    db_qkan.loadmodule('database')
    if not db_qkan.sqlyml(
        'database_checkflaechenbilanz',
        "qkan_utils.check_flaechenbilanz (1)"
    ):
        return False

    daten = db_qkan.fetchone()
    if daten is not None:
        meldung(
            "Differenz in Flächenbilanz!",
            'Öffnen Sie den Layer "Prüfung Flächenbilanz"',
        )

    if not db_qkan.sqlyml(
        'database_checktezgbilanz',
        "qkan_utils.check_flaechenbilanz (2)"
    ):
        return False

    daten = db_qkan.fetchone()
    if daten is not None:
        meldung(
            "Differenz in Bilanz der Haltungsflächen!",
            'Öffnen Sie den Layer "Prüfung Haltungsflächenbilanz"',
        )
    return True


def eval_node_types(db_qkan: "DBConnection") -> None:
    """Schachttypen auswerten. Dies geschieht ausschließlich mit SQL-Abfragen"""

    # -- Anfangsschächte: Schächte ohne Haltung oben
    db_qkan.loadmodule('database')
    if not db_qkan.sqlyml('tools_knotentyp_anf', "importkanaldaten_he (39)"):
        return

    # -- Endschächte: Schächte ohne Haltung unten
    if not db_qkan.sqlyml('tools_knotentyp_end', "importkanaldaten_he (40)"):
        return

    # -- Hochpunkt:
    if not db_qkan.sqlyml('tools_knotentyp_hoch', "importkanaldaten_he (41)"):
        return

    # -- Tiefpunkt:
    if not db_qkan.sqlyml('tools_knotentyp_tief', "importkanaldaten_he (42)"):
        return

    # -- Verzweigung:
    if not db_qkan.sqlyml('tools_knotentyp_zweig', "importkanaldaten_he (43)"):
        return

    # -- Einzelschacht:
    if not db_qkan.sqlyml('tools_knotentyp_einzel', "importkanaldaten_he (44)"):
        return

    db_qkan.commit()


# Funktionen zur formatierten Ein- und Ausgabe von Fließkommazahlen


def formf(zahl: Optional[float], anz: Optional[int]) -> str:
    """Formatiert eine Fließkommazahl so, dass sie in einer vorgegebenen Anzahl von Zeichen
    mit maximaler Genauigkeit dargestellt werden kann.
    """
    if anz == 0 or anz is None:
        return ""
    if zahl is None:
        if anz == 1:
            erg = "."
        else:
            erg = "{}0.".format(" " * (anz - 2))
        return erg
    elif zahl == 0:
        return " " * (anz - 1) + "0"
    elif zahl < 0:
        logger.error(
            "Fehler in k_qkkp.formf (2): Zahl ist negativ\nzahl = {}\nanz = {}\n".format(
                zahl, anz
            )
        )
        return ""

    # try:
    nv = int(math.log10(zahl))  # Anzahl Stellen vor dem Komma.
    # except BaseException as err:
    # fehlermeldung(u'Fehler in k_qkkp.formf (1): {}'.format(err),
    # u'zahl = {}, anz = {}'.format(zahl, anz))

    dez = True  # In der Zahl kommt ein Dezimalkomma vor. Wird benötigt wenn
    # Nullen am Ende gelöscht werden sollen

    # Prüfung, ob Zahl (auch nach Rundung!) kleiner 1 ist, so dass die führende Null weggelassen
    # werden kann

    if round(zahl, anz - 1) < 1:
        fmt = "{0:" + "{:d}.{:d}f".format(anz + 1, anz - 1) + "}"
        erg = fmt.format(zahl)[1:]
    else:
        if int(math.log10(round(zahl, 0))) + 1 > anz:
            logger.error(
                "Fehler in k_qkkp.formf (3): Zahl ist zu groß!\nzahl = {}\nanz = {}\n".format(
                    zahl, anz
                )
            )
            return ""
        # Korrektur von nv, für den Fall, dass zahl nahe an nächster 10-Potenz
        nv = int(math.log10(round(zahl, max(0, anz - 2 - nv))))
        if nv + 1 == anz:
            # Genau soviel Platz wie Vorkommastellen
            fmt = "{0:" + "{:d}.{:d}f".format(anz, anz - 1 - nv) + "}"
            dez = False  # Nullen am Ende dürfen nicht gelöscht werden
        elif nv + 1 == anz - 1:
            # Platz für alle Vorkommastellen und das Dezimalzeichen (dieses muss ergänzt werden)
            fmt = "{0:" + "{:d}.{:d}f".format(anz, anz - 2 - nv) + "}."
            dez = False  # obsolet, weil Dezimalpunkt am Ende
        elif nv + 1 < anz - 1:
            # Platz für mindestens eine Nachkommastelle
            fmt = "{0:" + "{:d}.{:d}f".format(anz, anz - 2 - nv) + "}"
        else:
            logger.error(
                "Fehler in k_qkkp.formf (2):\nzahl = {}\nanz = {}\n".format(zahl, anz)
            )
            return ""
        erg = fmt.format(zahl)

        # Nullen am Ende löschen
        if dez:
            fmt = "{0:>" + "{:d}s".format(anz) + "}"
            erg = fmt.format(erg.rstrip("0"))
    return erg

def round_up( n, decimals=2):
    expoN = n * 10 ** decimals
    return ceil(expoN) / 10 ** decimals


def fzahl(text: str, n: float = 0.0, default: float = 0.0) -> float:
    """Wandelt einen Text in eine Zahl um. Falls kein Dezimalzeichen
enthalten ist, werden n Nachkommastellen angenommen
    """
    zahl = text.strip()
    if zahl == "":
        return default
    elif "." in zahl:
        try:
            return float(zahl)
        except BaseException as err:
            logger.error("10: {}".format(err))
            return default
    else:
        return float(zahl) / 10.0 ** n


def ffloat(zahl: float, n: int) -> str:
    """Formatiert eine Zahl mit n Nachkommastellen und gibt sie als Text zurück
    :type zahl: float
    :type n:    int
    """
    if zahl:
        return f'{zahl:.2f}'
    else:
        return ''


def read_qml(qmlfiles: dict[str, str]):
    """Liest qml-Datei(en) für QKan-Layer"""

    qmldir = qmlfiles.get('specificqmlpath', 'qml')
    layer_tree_root = QgsProject.instance().layerTreeRoot()
    group = layer_tree_root.findGroup('QKan')
    for layer in group.findLayers():
        for laynam in qmlfiles.keys():
            if laynam == layer.name():
                style_file = os.path.join(QKan.template_dir, qmldir, qmlfiles[laynam])
                if style_file:
                    l = layer.layer()
                    l.loadNamedStyle(style_file)
                    l.triggerRepaint()

def loadLayer(
        layerbez,
        table,
        geom_column,
        qmlfile,
        filter = '',
        uifile = None,
        group: Union[List, str] = 'QKan',
        exclusive: bool = False,
        gpos=0,
        qkan_db: str = None
) -> bool:
    """Lädt einen Layer aus einer qml-Datei in eine bestimmte Gruppe an eine bestimmte Position
    :layerbez:              Bezeichnung des Layers
    :type layerbez:         String

    :table:                 Name der Tabelle in der QKan-Datenbank
    :type table:            String

    :geom_column:           Attributname des Geo-Objekts
    :type geom_column:      String

    :qmlfile:               Name der Stildatei
    :type qmlfile:          String

    :filter:                Filter auf Datensätze
    :type qmlfile:          String

    :uifile:                Name der Formulardatei
    :type uifile:           String

    :group:                 Bezeichnung der Gruppe, in der der Layer eingefügt werden soll
    :type group:            List, String

    :exclusive:             Layer in Gruppe sollen exklusiv angezeigt werden
    :type exclusive:        Bool

    :gpos:                  Index der Position innerhalb der Gruppe
    :type gpos:             int

    :qkan_db:               andere als die Standard-QKan-DB
    :type qkan_db:          str

    :returns:               bool
    """

    project = QgsProject.instance()

    dlayers = project.mapLayersByName(layerbez)
    for dlayer in dlayers:
        project.removeMapLayer(dlayer)

    uri = QgsDataSourceUri()
    if qkan_db is None:
        uri.setDatabase(QKan.config.database.qkan)
    else:
        uri.setDatabase(qkan_db)
    logger.debug(f'{uri=}')
    schema = ''
    uri.setDataSource(schema, table, geom_column, filter)
    layer = QgsVectorLayer(uri.uri(), layerbez, 'spatialite')

    templatepath = os.path.join(pluginDirectory("qkan"), "templates")
    qmlpath = os.path.join(templatepath, "qml", qmlfile)
    formsDir = os.path.join(pluginDirectory("qkan"), "forms")

    try:
        layer.loadNamedStyle(qmlpath)
        layer.triggerRepaint()
    except:
        logger.error_code(f'Stildatei "{qmlfile}" wurde nicht gefunden!\nAbbruch!')
        return False

    # Adapt path to forms directory
    if uifile is not None:
        editFormConfig = layer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(formsDir, uifile))
        layer.setEditFormConfig(editFormConfig)

    project.addMapLayer(layer, False)

    layersRoot = project.layerTreeRoot()
    if isinstance(group, str):
        logger.debug(f"Einfache Gruppe: {group}")
        actGroup = layersRoot.findGroup(group)
        if actGroup is None:
            actGroup = layersRoot.addGroup(group)
        actGroup.insertLayer(gpos, layer)
    elif isinstance(group, List):
        logger.debug((f"Verkettete Gruppe..."))
        actGroup = layersRoot           # Start ist root
        for subgroup in group:
            logger.debug(f"Haupt- oder Untergruppe: {subgroup}")
            newGroup = layersRoot.findGroup(subgroup)
            if newGroup is None:
                actGroup = actGroup.addGroup(subgroup)
                if exclusive:
                    # Gruppe zeigt Elemente exklusiv an
                    actGroup.setIsMutuallyExclusive(True)
                actGroup.setExpanded(False)
            else:
                actGroup = newGroup
        actGroup.insertLayer(gpos, layer)
    else:
        logger.error_code(f"Fehler in der Bezeichnung beim Anlegen des Layers"
                          f" oder der Layerliste {group=}")

    return True

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
        # noinspection PyArgumentList
        return str(
            Path(
                QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[-1]
            ).absolute()
        )


def list_selected_items(list_widget: QListWidget) -> List[str]:
    """
    Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

    :param list_widget: Liste aller Widgets
    """

    return [_.text() for _ in list_widget.selectedItems()]

def zoomAll():
    """
    Zoomt Karte auf Schächte oder Haltungen
    :return: None
    """
    canvas = iface.mapCanvas()
    canvas.refreshAllLayers()

    layers = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)
    if len(layers) > 0:
        layer = layers[0]
        layer.updateExtents()
        canvas.refreshAllLayers()
        if not (10.0 < (breite := layer.extent().width()) < 100000.0):
            logger.debug(f"Layer Schächte nicht gefunden oder {breite=} unplausibel")
            layers = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)
            if len(layers) > 0:
                layer = layers[0]
                layer.updateExtents()
                canvas.refreshAllLayers()
                if not (10.0 < (breite := layer.extent().width()) < 100000.0):
                    logger.debug('Zoom nicht möglich, weil Zoombereich von Haltungslayer {breite=} ebenfalls unplausibel')
                    return
    else:
        logger.debug('Layer Schächte und Haltungen sind nicht vorhanden. Möglicherweise wurde kein Projekt geladen')
        return

    canvas.setExtent(layer.extent())
    canvas.refresh()

def cleanquot(text: str = ''):
    """Bereinigt einen String von mehr als 2 Hochkommata in Folge zur Vermeidung von SQL-Injection"""

    return re.sub('''"""+''', '"', text)

def cleanname(text: str = ''):
    """Bereinigt einen String von Nicht-Unicode-Zeichen zur Vermeidung von SQL-Injection"""

    return re.sub(r"[^\w]", "_", text)


class Patterns():
    """Management of pattern lists in yaml-Files

    pats = Patterns(ymlfile)
    theme in pats.patterns        # Test, ob Thema vorhanden
    pats.find(theme, key)         # gibt gefundene QKan-Bezeichnung zurück
    """

    def __init__(self, filepath):
        with open(filepath) as fr:
            self.patterns = yaml.safe_load(fr.read())

    def find(self, theme: str, key):
        """Zugeorndeten QKan-Wert finden"""
        patts = self.patterns[theme]
        for qkan_name in patts:
            for patt in patts[qkan_name]:
                if fnmatch(key.strip().lower(), patt.lower()):
                    return qkan_name
        return None
