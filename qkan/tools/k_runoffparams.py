# -*- coding: utf-8 -*-

'''

  Set runoff parameters
  =====================
  
  Berechnet für die Flächenobjekte die Oberflächenabflussparameter nach HYSTEM/EXTRAN 7 oder DYNA.
  
  | Dateiname            : k_runoffparams.py
  | Date                 : Juli 2018
  | Copyright            : (C) 2018 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$
  
  This program is free software; you can redistribute it and/or modify   
  it under the terms of the GNU General Public License as published by   
  the Free Software Foundation; either version 2 of the License, or      
  (at your option) any later version.

'''

__author__ = 'Joerg Hoettges'
__date__ = 'July 2018'
__copyright__ = '(C) 2018, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import logging

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from qgis.PyQt.QtGui import QProgressBar

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fortschritt, fehlermeldung, sqlconditions

logger = logging.getLogger(u'QKan')

progress_bar = None

# Fortschritts- und Fehlermeldungen


# ------------------------------------------------------------------------------
# Hauptprogramm

def setRunoffparams(dbQK, runoffparamstype_choice, runoffmodelltype_choice, runoffparamsfunctions,
                    liste_teilgebiete, liste_abflussparameter, datenbanktyp):
    '''Berechnet Oberlächenabflussparameter für HYSTEM/EXTRAN 7 und DYNA/Kanal++.

    :dbQK:                          Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:                     DBConnection (geerbt von dbapi...)

    :runoffparamstype_choice:       Simulationsprogramm, für das die Paremter berechnet werden sollen. 
    :type runoffparamstype_choice:  string

    :liste_teilgebiete:             Liste der bei der Bearbeitung zu berücksichtigenden Teilgebiete (Tabelle tezg)
    :type:                          list

    :dbtyp:                         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:                    String

    :returns:                       void

    Für alle TEZG-Flächen wird, falls nicht schon vorhanden, ein unbefestigtes Flächenobjekt erzeugt. 
    Dazu können in der Auswahlmaske zunächst die Kombinationen aus Abflussparameter und Teilgebiet 
    gewählt werden, die in der Tabelle "tezg" vorkommen und die nachfolgenden Voraussetzungen erfüllen:

    - Im Feld "abflussparameter" muss auf einen Abflussparameter verwiesen werden, der für unbefestigte 
      Flächen erzeugt wurde (infiltrationsparameter > 0)
    '''

    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"Info", u"Oberflächenabflussparameter werden berechnet... Bitte warten.")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    # status_message.setText(u"Erzeugung von unbefestigten Flächen ist in Arbeit.")
    progress_bar.setValue(1)

    funlis = runoffparamsfunctions[runoffparamstype_choice]        # Beide Funktionen werden in einer for-Schleife abgearbeitet
    # logger.debug(u"\nfunlis:\n{}".format(funlis))
    kriterienlis = ['IS NULL', 'IS NOT NULL']

    # Auswahl der zu bearbeitenden Flächen
    auswahl = sqlconditions('AND', ('fl.teilgebiet', 'fl.abflussparameter'), (liste_teilgebiete, liste_abflussparameter))

    if runoffmodelltype_choice == 'Speicherkaskade':

        # Es werden sowohl aufzuteilende und nicht aufzuteilende Flächen berücksichtigt
        # Schleife über befestigte und durchlässige Flächen (Kriterium: bodenklasse IS NULL)
        # dabei werden aus funlis und kriterienlis nacheinander zuerst die relevanten Inhalte für befestigte und anschließend
        # für durchlässige Flächen genommen. 

        for fun, kriterium in zip(funlis[:2], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.flnam AS flnam, 
                        fl.neigkl AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, speicherzahl, speicherkonst) = (
                    SELECT 'Speicherkaskade', 3, ({fun})/3
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(auswahl=auswahl, fun=fun, kriterium=kriterium)
            if not dbQK.sql(sql, u'QKan.tools.setRunoffparams (3)'):
                return False

    elif runoffmodelltype_choice == 'Fliesszeiten':
         # Fließzeit Kanal
        for fun, kriterium in zip(funlis[2:4], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.flnam AS flnam, 
                        fl.neigkl AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, fliesszeitkanal) = (
                    SELECT 'Fliesszeiten', {fun}
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(auswahl=auswahl, fun=fun, kriterium=kriterium)
            if not dbQK.sql(sql, u'QKan.tools.setRunoffparams (3)'):
                return False

           # Fließzeit Oberfläche
        for fun, kriterium in zip(funlis[4:6], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.flnam AS flnam, 
                        fl.neigkl AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, fliesszeitflaeche) = (
                    SELECT 'Fliesszeiten', {fun}
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(auswahl=auswahl, fun=fun, kriterium=kriterium)
            if not dbQK.sql(sql, u'QKan.tools.setRunoffparams (3)'):
                return False

    elif runoffmodelltype_choice == 'Schwerpunktlaufzeit':
        for fun, kriterium in zip(funlis[:2], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.flnam AS flnam, 
                        fl.neigkl AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, fliesszeitflaeche) = (
                    SELECT 'Schwerpunktlaufzeit', {fun}
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.flnam = fl.flnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(auswahl=auswahl, fun=fun, kriterium=kriterium)
            if not dbQK.sql(sql, u'QKan.tools.setRunoffparams (3)'):
                return False

    # status_message.setText(u"Erzeugung von unbefestigten Flächen")
    progress_bar.setValue(90)

    dbQK.commit()
    del dbQK

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage(u"Information", u"Oberflächenabflussparameter sind berechnet und eingetragen!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nOberflächenabflussparameter sind berechnet und eingetragen!", level=QgsMessageLog.INFO)

    progress_bar.setValue(100)
    status_message.setText(u"Oberflächenabflussparameter sind berechnet und eingetragen!")
    status_message.setLevel(QgsMessageBar.SUCCESS)
