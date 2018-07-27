# -*- coding: utf-8 -*-

import logging
import re

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger(u'QKan')


# Versionscheck

def versionolder(versliste, verslisref, depth=3):
    """Gibt wahr zurück, wenn eine Versionsliste älter als eine Referenz-Versionsliste ist, 
       falsch, wenn diese gleich oder größer ist. 

    :param versliste:   Liste von Versionsnummern, höchstwertige zuerst
    :type versliste:    list

    :param verslisref:  Liste von Versionsnummern zum Vergleich, höchstwertige zuerst
    :type verslisref:   list

    :param depth:       Untersuchungstiefe
    :type depth:        integer
    """
    for v1, v2 in zip(versliste[:depth], verslisref[:depth]):
        if v1 < v2:
            return True
        elif v1 > v2:
            return False
    return False


# Fortschritts- und Fehlermeldungen

def meldung(title, text):
    logger.info(u'{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.INFO)
    iface.messageBar().pushMessage(title, text, level=QgsMessageBar.INFO)

    
def fortschritt(text, prozent=0):
    logger.debug(u'{:s} ({:.0f}%)'.format(text, prozent * 100))
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text, prozent * 100), u'Link Flächen: ', QgsMessageLog.INFO)


def fehlermeldung(title, text=''):
    logger.error(u'{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)
    iface.messageBar().pushMessage(title, text, level=QgsMessageBar.CRITICAL)

    # Protokolldatei anzeigen

    # dnam = dt.today().strftime(u"%Y%m%d")
    # fnam = os.path.join(tempfile.gettempdir(), u'QKan{}.log'.format(dnam))
    # os.startfile(fnam)

# Allgemeine Funktionen

def get_database_QKan(silent = False):
    """Ermittlung der aktuellen QpatiaLite-Datenbank aus den geladenen Layern"""
    database_QKan = u''
    epsg = u''
    layers = iface.legendInterface().layers()
    # logger.debug(u'Layerliste erstellt')
    logger.error(u'Keine Layer vorhanden...')
    if len(layers) == 0 and not silent:
        iface.mainWindow().statusBar().clearMessage()
        iface.messageBar().pushMessage(u"Fehler: ", u"Kein QKan-Projekt geladen!", level=QgsMessageBar.CRITICAL)
        QgsMessageLog.logMessage(u"\nKein QKan-Projekt geladen!", level=QgsMessageLog.CRITICAL)

        return False, False

    # Über Layer iterieren
    for lay in layers:
        lyattr = {}

        # Attributstring für Layer splitten
        split = re.compile("['\"] ").split(lay.source())
        for le in split:
            if '=' in le:
                key, value = le.split('=', 1)
                lyattr[key] = value.strip('"').strip('\'')

        # Falls Abschnitte 'table' und 'dbname' existieren, handelt es sich um einen Datenbank-Layer
        if 'table' in lyattr and 'dbname' in lyattr:
            if lyattr['table'] == 'flaechen':
                if database_QKan == '':
                    database_QKan = lyattr['dbname']
                    epsg = str(int(lay.crs().postgisSrid()))
                elif database_QKan != lyattr['dbname']:
                    logger.warning(u'Abweichende Datenbankanbindung gefunden: {}'.format(lyattr['dbname']))
                    return False, False  # Im Projekt sind mehrere Sqlite-Datenbanken eingebungen...
    return database_QKan, epsg


def get_editable_layers():
    """Liste der Tabellen, für die in der Layerliste der Status editable aktiviert ist.
        Dient dazu, sicherzustellen, dass keine Datenbankoperationen auf editierbare
        Layer zugreifen."""

    elayers = set([])  # Zuerst leere Liste anlegen

    layers = iface.legendInterface().layers()
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


def checknames(dbQK, tab, attr, prefix, autokorrektur, dbtyp = u'SpatiaLite'):
    """Prüft, ob in der Tabelle {tab} im Attribut {attr} eindeutige Namen enthalten sind. 
    Falls nicht, werden Namen vergeben, die sich aus {prefix} und ROWID zusammensetzen

    :dbQK:              Typ der Datenbank (SpatiaLite, PostGIS)
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
    
    :dbtyp:             Typ der Datenbank (SpatiaLite, PostGIS)
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
                u'In der Tabelle "{tab}" gibt es leere Namen im Feld "{attr}". Abbruch!'.format(tab=tab, attr=attr))
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
                u'In der Tabelle "{tab}" gibt es doppelte Namen im Feld "{attr}". Abbruch!'.format(tab=tab, attr=attr))
            return False

    return True


def checkgeom(dbQK, tab, attrgeo, autokorrektur, liste_teilgebiete = [], dbtyp = u'SpatiaLite'):
    """Prüft, ob in der Tabelle {tab} im Attribut {attrgeo} ein Geoobjekt vorhanden ist. 

    :dbQK:              Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbQK:         Class FBConnection
    
    :tab:               Name der Tabelle
    :type tab:          String
    
    :attrgeo:           Name des Geo-Attributs, das auf Existenz geprüft werden soll
    :type attr:         String

    :autokorrektur:        Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                        werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                        abgebrochen.
    :type autokorrektur:   String
    
    :dbtyp:             Typ der Datenbank (SpatiaLite, PostGIS)
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
            WHERE {tab}.{attrgeo} IS NULL{auswahl}""".format(tab=tab, attrgeo=attrgeo, auswahl = auswahl)
    if not dbQK.sql(sql, u"QKan.qgis_utils.checkgeom (1)"):
        return False

    daten = dbQK.fetchone()

    if daten[0] > 0:
        if autokorrektur:
            meldung(u'Automatische Korrektur von Daten: ', 
                u'In der Tabelle "{tab}" wurden leere Geo-Objekte gefunden. Diese Datensätze wurden gelöscht'.format(tab=tab, attrgeo=attrgeo))

            sql = u"""DELETE
                FROM {tab}
                WHERE {attrgeo} IS NULL{auswahl}""".format(tab=tab, attrgeo=attrgeo, auswahl = auswahl)

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
    
    Example: sqlconditions('WHERE', ('flaechen.teilgebiet', 'flaechen.abflussparameter'), (liste_teilegebiete, liste_abflussparamerer)
    """

    # Falls keine Wertelisten gegeben oder alle Wertelisten leer sind, wird ein Leerstring zurückgeben
    for el in valuelis2:
        if len(el) > 0:
            break
    else:
        return ''

    if len(attrlis) != len(valuelis2):
        fehlermeldung(u'Fehler in qkan_utils.sqlconditions:', 
                u'Anzahl an Attributen und Wertlisten stimmt nicht ueberein: \n' + \
                u'attrlis= {}\n'.format(attrlis) + \
                u'valuelis2= {}\n'.format(valuelis2))

    condlis = []        # Liste der einzelnen SQL-Conditions

    for attr, valuelis in zip(attrlis, valuelis2):
        if len(valuelis) != 0:
            condlis.append("{attr} in ('{values}')".format(attr=attr, 
                                                           values = "', '".join(valuelis)))
    if len(condlis) != 0:
        auswahl = ' {keyword} {conds}'.format(keyword=keyword, conds=' AND '.join(condlis))
    else:
        auswahl = ''

    return auswahl

