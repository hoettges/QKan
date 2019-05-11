# -*- coding: utf-8 -*-

import logging

from qgis.core import QgsMessageLog, Qgis
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger(u'QKan.database.qkan_utils')


# Fortschritts- und Fehlermeldungen

def meldung(title, text):
    logger.info('{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(message='{:s} {:s}'.format(title, text), level=Qgis.Info)
    iface.messageBar().pushMessage(title, text, level=Qgis.Info)


def warnung(title, text):
    logger.warning('{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(message='{:s} {:s}'.format(title, text), level=Qgis.Warning)
    iface.messageBar().pushMessage(title, text, level=Qgis.Warning)


def fortschritt(text, prozent=0):
    logger.debug('{:s} ({:.0f}%)'.format(text, prozent * 100))
    QgsMessageLog.logMessage(message='{:s} ({:.0f}%)'.format(text, prozent * 100), tag=u'Link Flächen: ',
                             level=Qgis.Info)


def fehlermeldung(title, text=u''):
    logger.error('{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(message='{:s} {:s}'.format(title, text), level=Qgis.Critical)
    iface.messageBar().pushMessage(title, text, level=Qgis.Critical)

    # Protokolldatei anzeigen

    # dnam = dt.today().strftime(u"%Y%m%d")
    # fnam = os.path.join(tempfile.gettempdir(), u'QKan{}.log'.format(dnam))
    # os.startfile(fnam)


# Allgemeine Funktionen

def listQkanLayers(qgsTemplate = None):
    '''Dictionary mit den Namen aller QKan-Layer und einer Liste mit: 
            Tabellenname, Geometriespalte, SQL-Where-Bedingung, Gruppenname

        Die Zusammenstellung wird aus der Template-QKanprojektdatei gelesen
    '''
    import os
    from qgis.utils import pluginDirectory
    import xml.etree.ElementTree as et

    if not qgsTemplate:
        return {}
        # templateDir = os.path.join(pluginDirectory('qkan'), u"templates")
        # qgsTemplate = os.path.join(templateDir, 'Projekt.qgs')

    qgsxml = et.ElementTree()
    qgsxml.parse(qgsTemplate)
    tagGroup = u'layer-tree-group/layer-tree-group'
    qgsGroups = qgsxml.findall(tagGroup)
    qkanLayers = {}
    for group in qgsGroups:
        groupName = group.attrib['name']
        groupLayers = group.findall('layer-tree-layer')
        for layer in groupLayers:
            layerName = layer.attrib['name']
            layerSource = layer.attrib['source']
            dbname, table, geom, sql = get_qkanlayerAttributes(layerSource)
            qkanLayers[layerName] = [table, geom, sql, groupName]
    logger.debug(u'qkanLayers: \n{}'.format(qkanLayers))
    return qkanLayers


def isQkanLayer(layername, source):
    """Ermittelt, ob eine Layerquelle auf eine QKan-Tabelle verweist

    :database_QKan: Pfad zur Datenbank
    :type database: String

    :source:        Pfad zur QKan-Datenbank
    :type source:   String

    :returns:       Ergebnis der Prüfung
    :rtype:         boolean
    """

    dbname, table, geom, sql = get_qkanlayerAttributes(source)

    qkanLayers = listQkanLayers()
    if layername in qkanLayers:
        if table == qkanLayers[layername][0] and geom == qkanLayers[layername][1] and sql == qkanLayers[layername][2]:
            ve = (geom != '')  # Vectorlayer?
            return True, ve
    return False, False


# todo: nachfolgende Funktion ist depricated und kann durch listQkanLayers ersetzt werden...

def get_qkanlayerAttributes(source):
    """Ermittelt die Attribute eines QKan-Layers in einer SpatiaLite-Datenbank

    :param source:  Source-String des QGIS-Layers
    :type source:   string

    :returns:       Attribute des Layers
    :rtype:         tuple
    """

    posDbname = source.find(u'dbname=')
    posTable = source.find(u' table=', posDbname + 1)
    posGeomStart = source.find(u' (', posTable + 6)
    posGeomEnd = source.find(u') ', posGeomStart + 2)
    posSql = source.find(u' sql=', posGeomEnd + 1)

    if posSql < 0:
        return '', '', '', ''

    dbname = source[posDbname + 8: posTable - 1].strip()

    if posGeomStart < 0 or posGeomStart > posSql:
        geom = ''
        posGeomStart = posSql
    else:
        geom = source[posGeomStart + 2: posGeomEnd].strip()

    table = source[posTable + 8: posGeomStart - 1].strip()

    if posSql < 0:
        sql = ''
    else:
        sql = source[posSql + 5:].strip()

    return dbname, table, geom, sql


def get_database_QKan(silent=False):
    """Ermittlung der aktuellen SpatiaLite-Datenbank aus den geladenen Layern"""
    database_QKan = u''
    epsg = u''
    layers = [x.layer() for x in iface.layerTreeCanvasBridge().rootGroup().findLayers()]
    # logger.debug(u'Layerliste erstellt')
    logger.error(u'Keine Layer vorhanden...')
    if len(layers) == 0 and not silent:
        meldung(u"Fehler: ", u"Kein QKan-Projekt geladen!")

        return False, False

    # Über Layer iterieren
    for lay in layers:
        dbname, table, geom, sql = get_qkanlayerAttributes(lay.source())
        if ((table == 'flaechen' and geom == 'geom') or
                (table == 'schaechte' and geom == 'geom') or
                (table == 'haltungen' and geom == 'geom')):
            # nur, wenn es sich um eine der drei QKan-Tabellen 'haltungen', 'schaechte' oder 'flaechen' handelt...

            if database_QKan == '':
                # Datenbank wurde noch nicht festgelegt
                database_QKan = dbname
                epsg = str(int(lay.crs().postgisSrid()))
            elif database_QKan != dbname:
                # Datenbank wurde bereits festgelegt, weicht aber für einen weiteren QKan-Layer ab...
                logger.warning(u'Abweichende Datenbankanbindung gefunden: {}'.format(dbname))
                return False, False  # Im Projekt sind mehrere Sqlite-Datenbanken eingebungen...
    return database_QKan, epsg


def get_editable_layers():
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
            for le in lay.source().split(u' '):
                if u'=' in le:
                    key, value = le.split(u'=', 1)
                    lyattr[key] = value.strip(u'"').strip(u"'")

            # Falls Abschnitte 'table' und 'dbname' existieren, handelt es sich um einen Datenbank-Layer
            if u'table' in lyattr and u'dbname' in lyattr:
                if lay.isEditable():
                    elayers.add(lyattr['table'])
    return elayers


def checknames(dbQK, tab, attr, prefix, autokorrektur, dbtyp=u'spatialite'):
    """Prüft, ob in der Tabelle {tab} im Attribut {attr} eindeutige Namen enthalten sind. 
    Falls nicht, werden Namen vergeben, die sich aus {prefix} und ROWID zusammensetzen

    :dbQK:              Typ der Datenbank (spatialite, postgis)
    :type dbQK:         Class FBConnection
    
    :tab:               Name der Tabelle
    :type tab:          String
    
    :attr:              Name des Attributs, das die eindeutige Bezeichnung enthalten soll
    :type attr:         String
    
    :prefix:            Kürzel, das bei fehlenden oder nicht eindeutigen Bezeichnungen vor 
                        die ROWID gesetzt wird
    :type prefix:       String
    
    :autokorrektur:        Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                        werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                        abgebrochen.
    :type autokorrektur:   String
    
    :dbtyp:             Typ der Datenbank (spatialite, postgis)
    :type dbtyp:        String
    
    :returns:           Ergebnis der Prüfung bzw. Korrektur
    :type returns:      Boolean
    """

    # ----------------------------------------------------------------------------------------------------------------
    # Prüfung, ob Objektnamen leer oder NULL sind:

    sql = u"""SELECT {attr}
            FROM {tab}
            WHERE {attr} IS NULL or trim({attr}) = ''""".format(tab=tab, attr=attr)

    if not dbQK.sql(sql, u"QKan.qgis_utils.checknames (1)"):
        return False

    daten = dbQK.fetchall()

    if len(daten) > 0:
        if autokorrektur:
            meldung(u'Automatische Korrektur von Daten: ',
                    u'In der Tabelle "{tab}" wurden leere Namen im Feld "{attr}" aufgefüllt'.format(tab=tab, attr=attr))

            sql = u"""UPDATE {tab}
                SET {attr} = printf('{prefix}%d', ROWID)
                WHERE {attr} IS NULL or trim({attr}) = ''""".format(tab=tab, attr=attr, prefix=prefix)

            if not dbQK.sql(sql, u"QKan.qgis_utils.checknames (2)"):
                return False
        else:
            fehlermeldung(u'Datenfehler',
                          u'In der Tabelle "{tab}" gibt es leere Namen im Feld "{attr}". Abbruch!'.format(tab=tab,
                                                                                                          attr=attr))
            return False

    # ----------------------------------------------------------------------------------------------------------------
    # Prüfung, ob Objektnamen mehrfach vergeben sind. 

    sql = u"""SELECT {attr}, count(*) AS anzahl
            FROM {tab}
            GROUP BY {attr}
            HAVING anzahl > 1 OR {attr} IS NULL""".format(tab=tab, attr=attr)
    if not dbQK.sql(sql, u"QKan.qgis_utils.checknames (3)"):
        return False

    daten = dbQK.fetchall()

    if len(daten) > 0:
        if autokorrektur:
            meldung(u'Automatische Korrektur von Daten: ',
                    u'In der Tabelle "{tab}" gibt es doppelte Namen im Feld "{attr}"'.format(tab=tab, attr=attr))

            sql = u"""WITH doppelte AS
                (   SELECT {attr}, count(*) AS anzahl
                    FROM {tab}
                    GROUP BY {attr}
                    HAVING anzahl > 1 OR {attr} IS NULL)
                UPDATE {tab}
                SET {attr} = printf('{prefix}%d', ROWID)
                WHERE {attr} IN (SELECT {attr} FROM doppelte)""".format(tab=tab, attr=attr, prefix=prefix)

            if not dbQK.sql(sql, u"QKan.qgis_utils.checknames (4)"):
                return False
        else:
            fehlermeldung(u'Datenfehler',
                          u'In der Tabelle "{tab}" gibt es doppelte Namen im Feld "{attr}". Abbruch!'.format(tab=tab,
                                                                                                             attr=attr))
            return False

    return True


def checkgeom(dbQK, tab, attrgeo, autokorrektur, liste_teilgebiete=[], dbtyp=u'spatialite'):
    """Prüft, ob in der Tabelle {tab} im Attribut {attrgeo} ein Geoobjekt vorhanden ist. 

    :dbQK:              Typ der Datenbank (spatialite, postgis)
    :type dbQK:         Class FBConnection
    
    :tab:               Name der Tabelle
    :type tab:          String
    
    :attrgeo:           Name des Geo-Attributs, das auf Existenz geprüft werden soll
    :type attr:         String

    :autokorrektur:        Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                        werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                        abgebrochen.
    :type autokorrektur:   String
    
    :dbtyp:             Typ der Datenbank (spatialite, postgis)
    :type dbtyp:        String
    
    :returns:           Ergebnis der Prüfung bzw. Korrektur
    :type returns:      Boolean
    """

    # ----------------------------------------------------------------------------------------------------------------
    # Prüfung, ob das Geoobjekt in Spalte attrgeo existiert

    # Einschränkung auf ausgewähtle Teilgebiete
    if len(liste_teilgebiete) != 0:
        auswahl = u" AND {tab}.teilgebiet in ('{lis}')".format(lis=u"', '".join(liste_teilgebiete), tab=tab)
    else:
        auswahl = ''

    sql = u"""SELECT count(*) AS anzahl
            FROM {tab}
            WHERE {tab}.{attrgeo} IS NULL{auswahl}""".format(tab=tab, attrgeo=attrgeo, auswahl=auswahl)
    if not dbQK.sql(sql, u"QKan.qgis_utils.checkgeom (1)"):
        return False

    daten = dbQK.fetchone()

    if daten[0] > 0:
        if autokorrektur:
            meldung(u'Automatische Korrektur von Daten: ',
                    (u'In der Tabelle "{tab}" wurden leere Geo-Objekte gefunden. '
                     u'Diese Datensätze wurden gelöscht').format(
                        tab=tab, attrgeo=attrgeo))

            sql = u"""DELETE
                FROM {tab}
                WHERE {attrgeo} IS NULL{auswahl}""".format(tab=tab, attrgeo=attrgeo, auswahl=auswahl)

            if not dbQK.sql(sql, u"QKan.qgis_utils.checkgeom (2)"):
                return False
        else:
            fehlermeldung(u'Datenfehler',
                          u'In der Tabelle "{tab}" gibt es leere Geoobjekte. Abbruch!'.format(tab=tab, attrgeo=attrgeo))
            return False

    return True


def sqlconditions(keyword, attrlis, valuelis2):
    """stellt Attribut- und Wertelisten zu einem SQL-String zusammen.
    
    :keywort:       logischer Operator, mit dem der SQL-Text an den vorhandenen
                    SQL-Text angehängt werden soll
    :type keyword:  string

    :attrlis:       Liste von Attribunten, ggfs. mit Tabellennamen. Anzahl muss mit 
                    valuelis2 korrespondieren
    :type attrlis:  list of strings

    :valuelis2:     Liste aus Listen mit Werten. Anzahl muss mit attrlis korrespondieren
    :type valuelis2:list of lists

    :returns:       Anhang zu einem SQL-Statement mit führendem Leerzeichen
    
    Example: sqlconditions('WHERE', ('flaechen.teilgebiet', 'flaechen.abflussparameter'),
                                    (liste_teilegebiete, liste_abflussparamerer))
    """

    # Falls keine Wertelisten gegeben oder alle Wertelisten leer sind, wird ein Leerstring zurückgeben
    for el in valuelis2:
        if len(el) > 0:
            break
    else:
        return ''

    if len(attrlis) != len(valuelis2):
        fehlermeldung(u'Fehler in qkan_utils.sqlconditions:',
                      u'Anzahl an Attributen und Wertlisten stimmt nicht ueberein: \n' +
                      u'attrlis= {}\n'.format(attrlis) +
                      u'valuelis2= {}\n'.format(valuelis2))

    condlis = []  # Liste der einzelnen SQL-Conditions

    for attr, valuelis in zip(attrlis, valuelis2):
        if len(valuelis) != 0:
            condlis.append(u"{attr} in ('{values}')".format(attr=attr,
                                                            values=u"', '".join(valuelis)))
    if len(condlis) != 0:
        auswahl = u' {keyword} {conds}'.format(keyword=keyword, conds=' AND '.join(condlis))
    else:
        auswahl = ''

    return auswahl


def evalNodeTypes(dbQK):
    """Schachttypen auswerten. Dies geschieht ausschließlich mit SQL-Abfragen"""

    # -- Anfangsschächte: Schächte ohne Haltung oben
    sql_typAnf = u'''
        UPDATE schaechte SET knotentyp = 'Anfangsschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte AS t_sch 
        LEFT JOIN haltungen AS t_hob
        ON t_sch.schnam = t_hob.schoben
        LEFT JOIN haltungen AS t_hun
        ON t_sch.schnam = t_hun.schunten
        WHERE t_hun.pk IS NULL)'''

    # -- Endschächte: Schächte ohne Haltung unten
    sql_typEnd = u'''
        UPDATE schaechte SET knotentyp = 'Endschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte AS t_sch 
        LEFT JOIN haltungen AS t_hob
        ON t_sch.schnam = t_hob.schunten
        LEFT JOIN haltungen AS t_hun
        ON t_sch.schnam = t_hun.schoben
        WHERE t_hun.pk IS NULL)'''

    # -- Hochpunkt: 
    sql_typHoch = u'''
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
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)>ifnull(t_hun.sohleunten,t_sun.sohlhoehe))'''

    # -- Tiefpunkt:
    sql_typTief = u'''
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
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)<ifnull(t_hun.sohleunten,t_sun.sohlhoehe))'''

    # -- Verzweigung:
    sql_typZweig = u'''
        UPDATE schaechte SET knotentyp = 'Verzweigung' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          GROUP BY t_sch.pk
          HAVING count(*) > 1)'''

    # -- Einzelschacht:
    sql_typEinzel = u'''
        UPDATE schaechte SET knotentyp = 'Einzelschacht' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam 
          FROM schaechte AS t_sch 
          LEFT JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          LEFT JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          WHERE t_hun.pk IS NULL AND t_hob.pk IS NULL)'''

    if not dbQK.sql(sql_typAnf, u'importkanaldaten_he (39)'):
        return None

    if not dbQK.sql(sql_typEnd, u'importkanaldaten_he (40)'):
        return None

    if not dbQK.sql(sql_typHoch, u'importkanaldaten_he (41)'):
        return None

    if not dbQK.sql(sql_typTief, u'importkanaldaten_he (42)'):
        return None

    if not dbQK.sql(sql_typZweig, u'importkanaldaten_he (43)'):
        return None

    if not dbQK.sql(sql_typEinzel, u'importkanaldaten_he (44)'):
        return None

    dbQK.commit()
