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

def setRunoffparams(self.dbQK, runoffparamstype_choice, runoffmodelltype_choice, runoffparamsfunctions, 
                    manningrauheit_bef, manningrauheit_dur, 
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

    if runoffmodelltype_choice == 'Speicherkaskade':

        # Auswahl der zu bearbeitenden Flächen
        auswahl = sqlconditions('WHERE', ('fl.teilgebiet', 'fl.abflussparameter'), (liste_teilgebiete, liste_abflussparameter))

        # Abflusstyp
        sql = """
            UPDATE linkfl
            SET abflusstyp = 'Speicherkaskade'
            WHERE id IN (
                SELECT linkfl.id
                FROM linkfl AS lf
                INNER JOIN flaechen AS fl
                ON lf.flnam = fl.flnam{auswahl}
            )""".format(auswahl=auswahl)
        if not dbQK.sql(sql, u'QKan.tools.setRunoffparams (1)'):
            return False

        # Speicherzahl
        sql = """
            UPDATE linkfl 
            SET speicherzahl = 3
            WHERE id IN (
                SELECT linkfl.id
                FROM linkfl AS lf
                INNER JOIN flaechen AS fl
                ON lf.flnam = fl.flnam{auswahl}
            )""".format(auswahl=auswahl)
        if not dbQK.sql(sql, u'QKan.tools.setRunoffparams (2)'):
            return False

        # Speicherkennzahl

        # Auswahl der zu bearbeitenden Flächen
        auswahl = sqlconditions('AND', ('fl.teilgebiet', 'fl.abflussparameter'), (liste_teilgebiete, liste_abflussparameter))

        # Befestigte Flächen. Kriterium: bodenklasse IS NULL
        # Es werden sowohl aufzuteilende und nicht aufzuteilende Flächen berücksichtigt
        # Schleife über befestigte und durchlässige Flächen
        
        kriterienlis = ['IS NULL', 'IS NOT NULL']
        for fun, kriterium in zip(funlis, kriterienlis):
        sql = """
            WITH flintersect AS (
                SELECT
                    lf.flnam AS flnam 
                    fl.neigkl AS neigkl
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
                    ST_Distance(fi.geom,ha.geom) AS "abstand",
                    CASE WHEN Intersects(ha.geom,fi.geom) THEN
                        HausdorffDistance(fi.geom,Intersection(ha.geom,fi.geom))
                    ELSE 
                        MaxDistance(fi.geom,ClosestPoint(ha.geom,fi.geom))-ST_Distance(fi.geom,ha.geom)
                    END AS "fliesslaenge",
                   fi.neigkl AS "neigkl", 
                   CASE fi.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung",
                   lf.speicherzahl AS speicherzahl
                FROM linkfl AS lf
                INNER JOIN flintersect AS fi
                ON lf.flnam = fi.flnam
                INNER JOIN haltungen AS ha
                ON ha.haltnam = lf.haltnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam
                WHERE abflussparameter.bodenklasse {kriterium}{auswahl}
            )
            UPDATE linkfl 
            SET speicherkonst = (
                SELECT {fun}/speicherzahl
                FROM qdist
                WHERE qdist.pk = linkfl.pk)
            WHERE pk IN (
                SELECT linkfl.pk
                FROM linkfl AS lf
                INNER JOIN flintersect AS fi
                ON lf.flnam = fi.flnam
                INNER JOIN abflussparameter AS ap
                ON fi.abflussparameter = abflussparameter.apnam
                WHERE abflussparameter.bodenklasse IS NULL{auswahl}
            )""".format(auswahl=auswahl, fun=fun, kriterium=kriterium,
                        rauheit_bef=manningrauheit_bef, rauheit_dur=manningrauheit_dur)
        if not dbQK.sql(sql, u'QKan.tools.setRunoffparams (3)'):
            return False
        
    elif runoffmodelltype_choice == 'Fliesszeiten':
        pass
    elif runoffmodelltype_choice == 'Schwerpunktlaufzeit':
        pass

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
