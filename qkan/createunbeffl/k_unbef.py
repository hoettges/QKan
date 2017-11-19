# -*- coding: utf-8 -*-

'''

  Import from HE
  ==============
  
  Aus einer Hystem-Extran-Datenbank im Firebird-Format werden Kanaldaten
  in die QKan-Datenbank importiert. Dazu wird eine Projektdatei erstellt,
  die verschiedene thematische Layer erzeugt, u.a. eine Klassifizierung
  der Schachttypen.
  
  | Dateiname            : import_from_he.py
  | Date                 : September 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$
  
  This program is free software; you can redistribute it and/or modify   
  it under the terms of the GNU General Public License as published by   
  the Free Software Foundation; either version 2 of the License, or      
  (at your option) any later version.

'''

__author__ = 'Joerg Hoettges'
__date__ = 'September 2016'
__copyright__ = '(C) 2016, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import logging

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import checknames, fortschritt, fehlermeldung

# import tempfile

logger = logging.getLogger('QKan')


# Fortschritts- und Fehlermeldungen


# ------------------------------------------------------------------------------
# Hauptprogramm

def createUnbefFlaechen(database_QKan, liste_tezg, autokorrektur, dbtyp='SpatiaLite'):
    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :database_QKan:         Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database:         DBConnection (geerbt von dbapi...)

    :liste_tezg:            Liste der bei der Bearbeitung zu berücksichtigenden Haltungsflächen (tezg)
    :type:                  list

    :autokorrektur:         Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                            werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                            abgebrochen.
    :type autokorrektur:    String
    
    :dbtyp:                 Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:            String
    
    :returns:               void
    '''

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        fehlermeldung("Fehler", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        return None

    # Kontrolle, ob tezg-Flächen eindeutig Namen haben:

    checknames(dbQK, 'tezg', 'flnam', 'ft_', autokorrektur)

    # Kontrolle, ob in Tabelle "abflussparameter" ein Datensatz für unbefestigte Flächen vorhanden ist
    # (Standard: apnam = '$Default_Unbef')

    sql = u"""SELECT apnam
        FROM abflussparameter
        WHERE bodenklasse IS NOT NULL OR trim(bodenklasse) = ''"""

    if not dbQK.sql(sql, 'QKan.k_unbef (1)'):
        return False

    data = dbQK.fetchone()

    if data is None:
        if autokorrektur:
            daten = ["'$Default_Unbef', u'von QKan ergänzt', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', '13.01.2011 08:44:50'"]

            for ds in daten:
                sql = u"""INSERT INTO abflussparameter
                         ( 'apnam', 'kommentar', 'anfangsabflussbeiwert', 'endabflussbeiwert', 'benetzungsverlust', 
                           'muldenverlust', 'benetzung_startwert', 'mulden_startwert', 'bodenklasse', 
                           'createdat') Values ({})""".format(ds)
                if not dbQK.sql(sql, 'QKan.k_unbef (2)'):
                    return False
        else:
            fehlermeldung('Datenfehler: ','Bitte ergänzen Sie in der Tabelle "abflussparameter" einen Datensatz für unbefestigte Flächen ("bodenklasse" darf nicht leer oder NULL sein)')


    # Für die Erzeugung der Restflächen reicht eine SQL-Abfrage aus. 

    if len(liste_tezg) == 0:
        auswahl = ''
    elif len(liste_tezg) == 1:
        auswahl = ' AND'
    elif len(liste_tezg) >= 2:
        auswahl = ' AND ('
    else:
        fehlermeldung("Interner Fehler", "Fehler in Fallunterscheidung!")

    # Anfang SQL-Krierien zur Auswahl der tezg-Flächen
    first = True
    for attr in liste_tezg:
        if attr[0] == u'None' or attr[1] == u'None':
            fehlermeldung('Datenfehler: ', u'In den ausgewählten Daten sind noch Datenfelder nicht definiert ("NULL").')
            return False
        if first:
            first = False
            auswahl += """ (tezg.abflussparameter = '{abflussparameter}' AND
                            tezg.teilgebiet = '{teilgebiet}')""".format(abflussparameter=attr[0], teilgebiet=attr[1])
        else:
            auswahl += """ OR\n      (tezg.abflussparameter = '{abflussparameter}' AND
                            tezg.teilgebiet = '{teilgebiet}')""".format(abflussparameter=attr[0], teilgebiet=attr[1])

        # Kontrolle, ob es sich bei den ausgewählten Datensätzen für "abflussparameter" um unbefestigte Flächen 
        # handelt (bodenklasse IS NOT NULL).

        sql = u"""SELECT apnam
            FROM abflussparameter
            WHERE apnam = '{abflussparameter}' AND 
                  bodenklasse IS NULL""".format(abflussparameter=attr[0])

    if len(liste_tezg) == 2:
        auswahl += """)"""
    # Ende SQL-Krierien zur Auswahl der tezg-Flächen

    sql = u"""WITH flbef AS (
            SELECT 'fd_' || ltrim(tezg.flnam, 'ft_') AS flnam, 
              tezg.haltnam AS haltnam, tezg.neigkl AS neigkl, 
              tezg.regenschreiber AS regenschreiber, tezg.teilgebiet AS teilgebiet,
              tezg.abflussparameter AS abflussparameter,
              'Erzeugt mit Plugin Erzeuge unbefestigte Flaechen' AS kommentar, 
              tezg.geom AS geot, 
              GUnion(CastToMultiPolygon(Intersection(flaechen.geom,tezg.geom))) AS geob
            FROM tezg
            INNER JOIN flaechen
            ON Intersects(tezg.geom,flaechen.geom)
            WHERE 'fd_' || ltrim(tezg.flnam, 'ft_') not in (SELECT flnam FROM flaechen)
              {auswahl}
            GROUP BY tezg.pk)
            INSERT INTO flaechen (flnam, haltnam, neigkl, regenschreiber, teilgebiet, abflussparameter, kommentar, geom) 
             SELECT flnam AS flnam, haltnam, neigkl, regenschreiber, teilgebiet, abflussparameter,
            kommentar, CastToMultiPolygon(Difference(geot,geob)) AS geom FROM flbef""".format(auswahl=auswahl)

    logger.debug(u'QKan.k_unbef (3) - liste_tezg = \n{}'.format(str(liste_tezg)))
    logger.debug(u'QKan.k_unbef (3) - SQL = \n{sql}'.format(sql=sql))
    if not dbQK.sql(sql, u"QKan_CreateUnbefFl (4)"):
        return False

    # Hinzufügen von Verknüpfungen in die Tabelle linkfl für die neu erstellten unbefestigten Flächen
    sql = u"""INSERT INTO linkfl (flnam, aufteilen, teilgebiet, geom, glink)
            SELECT
                fl.flnam AS flnam, 
                NULL AS aufteilen, 
                tg.teilgebiet AS teilgebiet, 
                NULL AS geom,
                MakeLine(PointOnSurface(fl.geom),Centroid(ha.geom)) AS glink
                FROM linkfl AS lf
                INNER JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                INNER JOIN haltungen AS ha
                ON lf.haltnam = ha.haltnam
                INNER JOIN tezg AS tg
                ON 'fd_' || tg.flnam = fl.flnam
                WHERE fl.flnam NOT IN
                (   SELECT flnam FROM linkfl)"""

    logger.debug(u'QKan.k_unbef (5) - SQL = \n{sql}'.format(sql=sql))
    if not dbQK.sql(sql, "QKan.k_unbef (5)"):
        return False

    dbQK.commit()
    del dbQK

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Restflächen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nRestflächen sind erstellt!", level=QgsMessageLog.INFO)
