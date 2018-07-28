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

def setRunoffparams(dbQK, runoffparamstype_choice, liste_teilgebiete, liste_abflussparameter, datenbanktyp):
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

    # Auswahl der zu bearbeitenden Flächen
    auswahl = sqlconditions('AND', ('teilgebiet', 'abflussparameter'), (liste_teilgebiete, liste_abflussparameter))

    if runoffparamstype_choice == 'itwh':
        # befestigte Flächen
        sql = u"""UPDATE flaechen
            SET 
                speicherkonst = max(0.003,round(0.8693 / 3*log(area(geom))+ 5.6317 / 3, 5)),
                fliesszeit = max(1,round(0.8693*log(area(geom))+ 5.6317, 5))
            WHERE abflussparameter IN
            (   SELECT apnam 
                FROM abflussparameter
                WHERE bodenklasse IS NULL
                GROUP BY apnam){auswahl}""".format(auswahl=auswahl)
        if not dbQK.sql(sql, u'QKan.tools.setRunoffparams'):
            return False

        # durchlässige Flächen
        sql = u"""UPDATE flaechen
            SET 
                speicherkonst = pow(18.904*pow(neigkl,0.686)/3*area(geom), 0.2535*pow(neigkl,0.244)),
                fliesszeit =    pow(18.904*pow(neigkl,0.686)*area(geom), 0.2535*pow(neigkl,0.244))
            WHERE abflussparameter IN
            (   SELECT apnam 
                FROM abflussparameter
                WHERE bodenklasse IS NOT NULL
                GROUP BY apnam){auswahl}""".format(auswahl=auswahl)
        if not dbQK.sql(sql, u'QKan.tools.setRunoffparams'):
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
