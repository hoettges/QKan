# -*- coding: utf-8 -*-

from qgis.utils import iface
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
import logging

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger('QKan')

def get_database_QKan():
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
    for lay in layers:
        # logger.debug('Verbindungsstring: {}'.format(lay.source()))
        lyattr = {}
        for le in lay.source().split(' '):
            if '=' in le:
                key, value = le.split('=')
                lyattr[key] = value.strip('"').strip("'")
                # logger.debug('Verbindung gefunden: {}: {}'.format(key,value))
        if 'table' in lyattr and 'dbname' in lyattr:
            # logger.debug('table und dbname in keys enthalten')
            if lyattr['table'] == 'flaechen':
                # logger.debug('table ist "haltungen" oder "schaechte"')
                if database_QKan == '':
                    database_QKan = lyattr['dbname']
                    # logger.debug('Datenbank erstmals gesetzt: {}'.format(database_QKan))
                    epsg = str(int(lay.crs().postgisSrid()))
                elif database_QKan != lyattr['dbname']:
                    database_QKan = ''
                    logger.warning('Abweichende Datenbankanbindung gefunden: {}'.format(lyattr['dbname']))
                    return False, False   # Im Projekt sind mehrere Sqlite-Datenbanken eingebungen...
    return database_QKan, epsg
