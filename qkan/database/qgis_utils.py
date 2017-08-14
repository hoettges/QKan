# -*- coding: utf-8 -*-

import logging

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger('QKan')


def get_database_QKan():
    """Ermittlung der aktuellen QpatiaLite-Datenbank aus den geladenen Layern"""
    database_QKan = ''
    epsg = ''
    layers = iface.legendInterface().layers()
    # logger.debug('Layerliste erstellt')
    if len(layers) == 0:
        logger.error('Keine Layer vorhanden...')
        iface.mainWindow().statusBar().clearMessage()
        iface.messageBar().pushMessage(u"Fehler: ", u"Kein QKan-Projekt geladen!", level=QgsMessageBar.CRITICAL)
        QgsMessageLog.logMessage(u"\nKein QKan-Projekt geladen!", level=QgsMessageLog.CRITICAL)

        return False, False

    # �ber Layer iterieren
    for lay in layers:
        lyattr = {}

        # Attributstring f�r Layer splitten
        for le in lay.source().split(' '):
            if '=' in le:
                key, value = le.split('=', 1)
                lyattr[key] = value.strip('"').strip("'")

        # Falls Abschnitte 'table' und 'dbname' existieren, handelt es sich um einen Datenbank-Layer
        if 'table' in lyattr and 'dbname' in lyattr:
            if lyattr['table'] == 'flaechen':
                if database_QKan == '':
                    database_QKan = lyattr['dbname']
                    epsg = str(int(lay.crs().postgisSrid()))
                elif database_QKan != lyattr['dbname']:
                    database_QKan = ''
                    logger.warning('Abweichende Datenbankanbindung gefunden: {}'.format(lyattr['dbname']))
                    return False, False  # Im Projekt sind mehrere Sqlite-Datenbanken eingebungen...
    return database_QKan, epsg


def get_editable_layers():
    """Liste der Tabellen, f�r die in der Layerliste der Status editable aktiviert ist.
        Dient dazu, sicherzustellen, dass keine Datenbankoperationen auf editierbare
        Layer zugreifen."""

    elayers = set([])  # Zuerst leere Liste anlegen

    layers = iface.legendInterface().layers()
    # logger.debug('Layerliste erstellt')
    if len(layers) > 0:
        # �ber Layer iterieren
        for lay in layers:
            lyattr = {}

            # Attributstring f�r Layer splitten
            for le in lay.source().split(' '):
                if '=' in le:
                    key, value = le.split('=', 1)
                    lyattr[key] = value.strip('"').strip("'")

            # Falls Abschnitte 'table' und 'dbname' existieren, handelt es sich um einen Datenbank-Layer
            if 'table' in lyattr and 'dbname' in lyattr:
                if lay.isEditable():
                    elayers.add(lyattr['table'])
    return elayers
