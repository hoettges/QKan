# -*- coding: utf-8 -*-

import logging
import math
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple
from xml.etree.ElementTree import ElementTree

from qgis.core import Qgis, QgsMessageLog, QgsProject
from qgis.utils import iface
from qkan import QKan

if TYPE_CHECKING:
    from .dbfunc import DBConnection
    from .fbfunc import FBConnection

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.database.qkan_utils")


# Fortschritts- und Fehlermeldungen


def meldung(title: str, text: str) -> None:
    logger.info("{:s} {:s}".format(title, text))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(message="{:s} {:s}".format(title, text), level=Qgis.Info)
    QKan.instance.iface.messageBar().pushMessage(title, text, level=Qgis.Info)


def warnung(title: str, text: str) -> None:
    logger.warning("{:s} {:s}".format(title, text))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="{:s} {:s}".format(title, text), level=Qgis.Warning
    )
    QKan.instance.iface.messageBar().pushMessage(title, text, level=Qgis.Warning)


def fortschritt(text: str, prozent: float = 0) -> None:
    logger.debug("{:s} ({:.0f}%)".format(text, prozent * 100))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="{:s} ({:.0f}%)".format(text, prozent * 100),
        tag="Link Flächen: ",
        level=Qgis.Info,
    )


def fehlermeldung(title: str, text: str = "") -> None:
    logger.error("{:s} {:s}".format(title, text))
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="{:s} {:s}".format(title, text), level=Qgis.Critical
    )
    QKan.instance.iface.messageBar().pushMessage(title, text, level=Qgis.Critical)

    # Protokolldatei anzeigen

    # dnam = dt.today().strftime("%Y%m%d")
    # fnam = os.path.join(tempfile.gettempdir(), u'QKan{}.log'.format(dnam))
    # os.startfile(fnam)


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
    tag_group = "layer-tree-group/layer-tree-group"
    qgs_groups = qgsxml.findall(tag_group)
    qkan_layers = {}
    for group in qgs_groups:
        group_name = group.attrib["name"]
        group_layers = group.findall("layer-tree-layer")
        for layer in group_layers:
            layer_name = layer.attrib["name"]
            layer_source = layer.attrib["source"]
            dbname, table, geom, sql = get_qkanlayer_attributes(layer_source)
            qkan_layers[layer_name] = [table, geom, sql, group_name]
    logger.debug("qkan_layers: \n{}".format(qkan_layers))
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


# todo: nachfolgende Funktion ist deprecated und kann durch listQkanLayers ersetzt werden...


def get_qkanlayer_attributes(source: str) -> Tuple[str, str, str, str]:
    """Ermittelt die Attribute eines QKan-Layers in einer SpatiaLite-Datenbank

    :param source:  Source-String des QGIS-Layers
    :returns:       database name, table name, geom, sql
    """

    parts = source.split(" ")

    elem = [elem.split("dbname=")[1] for elem in parts if elem[:6] == "dbname"]
    if len(elem) == 1:
        dbname = elem[0][1:-1]
    else:
        dbname = ""
    elem = [elem.split("table=")[1] for elem in parts if elem[:5] == "table"]
    if len(elem) == 1:
        table = elem[0][1:-1]
    else:
        table = ""
    elem = [elem for elem in parts if elem[:1] == "("]
    if len(elem) == 1:
        geom = elem[0][1:-1]
    else:
        geom = ""

    pos_sql = source.find("sql=")
    if pos_sql >= 0:
        sql = source[pos_sql + 4 :]
    else:
        sql = ""

    return dbname, table, geom, sql


def get_database_QKan(silent: bool = False) -> Tuple[Optional[str], Optional[int]]:
    """Ermittlung der aktuellen SpatiaLite-Datenbank aus den geladenen Layern"""

    # noinspection PyArgumentList
    project = QgsProject.instance()

    layerobjects = project.mapLayersByName("Schächte")
    logger.debug(
        f"qkan.database.qkan_utils.get_database_QKan: \nlayerobjects: {layerobjects}"
    )
    if len(layerobjects) > 0:
        lay = layerobjects[0]
        dbname_s: Optional[str] = get_qkanlayer_attributes(lay.source())[0]
        epsg_s = int(lay.crs().postgisSrid())
    else:
        dbname_s = None
        epsg_s = 0

    layerobjects = project.mapLayersByName("Flächen")
    if len(layerobjects) > 0:
        lay = layerobjects[0]
        dbname_f: Optional[str] = get_qkanlayer_attributes(lay.source())[0]
        epsg_f = int(lay.crs().postgisSrid())
    else:
        dbname_f = None
        epsg_f = 0

    if dbname_s == dbname_f and dbname_s is not None:
        return dbname_s, epsg_s
    elif dbname_s is None and dbname_f is None:
        if not silent:
            fehlermeldung(
                "Fehler in Layerliste:",
                'Layer "Schächte und Flächen existieren nicht"',
            )
        return None, None
    elif dbname_f is not None:
        if not silent:
            warnung("Fehler in Layerliste:", 'Layer "Schächte existiert nicht"')
        return dbname_f, epsg_f
    elif dbname_s is not None:
        if not silent:
            warnung("Fehler in Layerliste:", 'Layer "Flächen existiert nicht"')
        return dbname_s, epsg_s
    else:
        if not silent:
            fehlermeldung(
                "Fehler in Layerliste:",
                f"""Layer "Schächte" und "Flächen" sind mit abweichenden Datenbanken verknüpft:
            Schächte: {dbname_s}
            Flächen:  {dbname_f}""",
            )
        return None, None


def get_editable_layers() -> Set[str]:
    """Liste der Tabellen, für die in der Layerliste der Status editable aktiviert ist.
        Dient dazu, sicherzustellen, dass keine Datenbankoperationen auf editierbare
        Layer zugreifen."""

    elayers = set([])  # Zuerst leere Liste anlegen

    layers = [x.layer() for x in iface.layerTreeCanvasBridge().rootGroup().findLayers()]
    # logger.debug(u'Layerliste erstellt')
    if len(layers) > 0:
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
                    elayers.add(lyattr["table"])
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

    sql = f"""
    SELECT {attr}
    FROM {tab}
    WHERE {attr} IS NULL or trim({attr}) = ''
    """

    if not db_qkan.sql(sql, "QKan.qgis_utils.checknames (1)"):
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

            sql = f"""
                UPDATE {tab}
                SET {attr} = printf('{prefix}%d', ROWID)
                WHERE {attr} IS NULL or trim({attr}) = ''
            """

            if not db_qkan.sql(sql, "QKan.qgis_utils.checknames (2)"):
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

    sql = f"""
        SELECT {attr}, count(*) AS anzahl
        FROM {tab}
        GROUP BY {attr}
        HAVING anzahl > 1 OR {attr} IS NULL
    """
    if not db_qkan.sql(sql, "QKan.qgis_utils.checknames (3)"):
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

            sql = f"""
            WITH doppelte AS
                (
                    SELECT {attr}, count(*) AS anzahl
                    FROM {tab}
                    GROUP BY {attr}
                    HAVING anzahl > 1 OR {attr} IS NULL
                )
            UPDATE {tab}
            SET {attr} = printf('{prefix}%d', ROWID)
            WHERE {attr} IN (SELECT {attr} FROM doppelte)
            """

            if not db_qkan.sql(sql, "QKan.qgis_utils.checknames (4)"):
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


def checkgeom(
    db_qkan: "DBConnection",
    tab: str,
    attrgeo: str,
    autokorrektur: bool,
    liste_teilgebiete: List[str],
) -> bool:
    """
    Prüft, ob in der Tabelle {tab} im Attribut {attrgeo} ein Geoobjekt vorhanden ist.

    :param db_qkan:         Typ der Datenbank (spatialite, postgis)
    :param tab:             Name der Tabelle
    :param attrgeo:         Name des Geo-Attributs, das auf Existenz geprüft werden soll
    :param  autokorrektur:  Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                            werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                            abgebrochen.
    :param liste_teilgebiete:
    """

    # ----------------------------------------------------------------------------------------------------------------
    # Prüfung, ob das Geoobjekt in Spalte attrgeo existiert

    # Einschränkung auf ausgewählte Teilgebiete
    if len(liste_teilgebiete) != 0:
        auswahl = " AND {tab}.teilgebiet in ('{lis}')".format(
            lis="', '".join(liste_teilgebiete), tab=tab
        )
    else:
        auswahl = ""

    sql = f"""
        SELECT count(*) AS anzahl
        FROM {tab}
        WHERE {tab}.{attrgeo} IS NULL{auswahl}
    """
    if not db_qkan.sql(sql, "QKan.qgis_utils.checkgeom (1)"):
        return False

    daten = db_qkan.fetchone()

    if daten[0] > 0:
        if autokorrektur:
            meldung(
                "Automatische Korrektur von Daten: ",
                (
                    f'In der Tabelle "{tab}" wurden leere Geo-Objekte gefunden. '
                    "Diese Datensätze wurden gelöscht"
                ),
            )

            sql = f"""
                DELETE
                FROM {tab}
                WHERE {attrgeo} IS NULL {auswahl}
                """

            if not db_qkan.sql(sql, "QKan.qgis_utils.checkgeom (2)"):
                return False
        else:
            fehlermeldung(
                "Datenfehler",
                f'In der Tabelle "{tab}" gibt es leere Geoobjekte. Abbruch!',
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
        fehlermeldung(
            "Fehler in qkan_utils.sqlconditions:",
            "Anzahl an Attributen und Wertlisten stimmt nicht ueberein: \n"
            + "attrlis= {}\n".format(attrlis)
            + "valuelis2= {}\n".format(valuelis2),
        )

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
    Stellt Attribut- und Wertelisten zu einem SQL-String zusammen.

    :param db_qkan:     Typ der Datenbank (spatialite, postgis)
    """

    sql = """SELECT * FROM v_flaechen_check"""

    if not db_qkan.sql(sql, "qkan_utils.check_flaechenbilanz (1)"):
        return False

    daten = db_qkan.fetchone()
    if daten is not None:
        meldung(
            "Differenz in Flächenbilanz!",
            'Öffnen Sie den Layer "Prüfung Flächenbilanz"',
        )

    sql = """SELECT * FROM v_tezg_check"""

    if not db_qkan.sql(sql, "qkan_utils.check_flaechenbilanz (2)"):
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
    sql_typ_anf = """
        UPDATE schaechte SET knotentyp = 'Anfangsschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte AS t_sch 
        LEFT JOIN haltungen AS t_hob
        ON t_sch.schnam = t_hob.schoben
        LEFT JOIN haltungen AS t_hun
        ON t_sch.schnam = t_hun.schunten
        WHERE t_hun.pk IS NULL)"""

    # -- Endschächte: Schächte ohne Haltung unten
    sql_typ_end = """
        UPDATE schaechte SET knotentyp = 'Endschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte AS t_sch 
        LEFT JOIN haltungen AS t_hob
        ON t_sch.schnam = t_hob.schunten
        LEFT JOIN haltungen AS t_hun
        ON t_sch.schnam = t_hun.schoben
        WHERE t_hun.pk IS NULL)"""

    # -- Hochpunkt:
    sql_typ_hoch = """
        UPDATE schaechte SET knotentyp = 'Hochpunkt' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          JOIN schaechte AS t_sun
          ON t_sun.schnam = t_hun.schunten
          JOIN schaechte AS t_sob
          ON t_sob.schnam = t_hob.schunten
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)>ifnull(t_hob.sohleoben,t_sob.sohlhoehe) AND 
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)>ifnull(t_hun.sohleunten,t_sun.sohlhoehe))"""

    # -- Tiefpunkt:
    sql_typ_tief = """
        UPDATE schaechte SET knotentyp = 'Tiefpunkt' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          JOIN schaechte AS t_sun
          ON t_sun.schnam = t_hun.schunten
          JOIN schaechte AS t_sob
          ON t_sob.schnam = t_hob.schunten
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)<ifnull(t_hob.sohleoben,t_sob.sohlhoehe) AND 
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)<ifnull(t_hun.sohleunten,t_sun.sohlhoehe))"""

    # -- Verzweigung:
    sql_typ_zweig = """
        UPDATE schaechte SET knotentyp = 'Verzweigung' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          GROUP BY t_sch.pk
          HAVING count(*) > 1)"""

    # -- Einzelschacht:
    sql_typ_einzel = """
        UPDATE schaechte SET knotentyp = 'Einzelschacht' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam 
          FROM schaechte AS t_sch 
          LEFT JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          LEFT JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          WHERE t_hun.pk IS NULL AND t_hob.pk IS NULL)"""

    if not db_qkan.sql(sql_typ_anf, "importkanaldaten_he (39)"):
        return

    if not db_qkan.sql(sql_typ_end, "importkanaldaten_he (40)"):
        return

    if not db_qkan.sql(sql_typ_hoch, "importkanaldaten_he (41)"):
        return

    if not db_qkan.sql(sql_typ_tief, "importkanaldaten_he (42)"):
        return

    if not db_qkan.sql(sql_typ_zweig, "importkanaldaten_he (43)"):
        return

    if not db_qkan.sql(sql_typ_einzel, "importkanaldaten_he (44)"):
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


def fzahl(text: str, n: float = 0.0, default: float = 0.0) -> float:
    """
    Wandelt einen Text in eine Zahl um. Falls kein Dezimalzeichen
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
