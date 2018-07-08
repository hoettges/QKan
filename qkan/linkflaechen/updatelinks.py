# -*- coding: utf-8 -*-
"""

  Aktualisierung der Verknüpfungen für Flächen und SW-Einleiter
  =============================================================

  Für den Benutzer ist bei den Verknüpfungen der Flächen bzw. SW-Einleitern 
  mit den Haltungen ausschließlich die graphische maßgebend. Vor Nutzung 
  der verschiedenen Funktionen müssen diese Verknüpfung in die logischen
  übertragen werden. 

  | Dateiname            : updatelinks.py
  | Date                 : February 2018
  | Copyright            : (C) 2018 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de

  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.

"""

__author__ = 'Joerg Hoettges'
__date__ = 'February 2018'
__copyright__ = '(C) 2018, Joerg Hoettges'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = ':%H$'

import logging
import os

from qgis.PyQt.QtGui import QProgressBar

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from qkan.database.qkan_utils import fortschritt, fehlermeldung, checknames

logger = logging.getLogger(u'QKan')

# progress_bar = None

def updatelinkfl(dbQK, radiusHal = u'0.1', deletelinkGeomNone = True):
    """Aktualisierung des logischen Cache für die Tabelle "linkfl"

    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:             DBConnection

    :radiusHal:             Fangradius für das Verknüpfungsende auf der Haltung
    :type radiusHal:        Float

    Für den Benutzer maßgebend ist ausschließlich die graphische
    Verknüpfung von linkfl. Der Export basiert aber aus Performancegründen
    ausschließlich auf der logischen Verknüpfung ("logischer Cache").
    Deshalb erfolgt hier die Anpassung bzw. Korrektur der logischen Verknüpfungen.
    Aus Performancegründen wird in den nachfolgenden Abfragen zunächst immer 
    eine Auswahl der Datensätze aus "linkfl" vorgenommen, bei denen die logische 
    Verknüpfung nicht mit der graphischen übereinstimmt (Unterabfrage "missing") 
    und die Korrektur nur für diese Datensätze durchgeführt.
    """

    # Statusmeldung in der Anzeige
    # global progress_bar
    # progress_bar = QProgressBar(iface.messageBar())
    # progress_bar.setRange(0, 100)
    # status_message = iface.messageBar().createMessage(u"", 
                    # u"Bereinigung Flächenverknüpfungen in Arbeit. Bitte warten.")
    # status_message.layout().addWidget(progress_bar)
    # iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    # progress_bar.setValue(1)

    # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
    if not checknames(dbQK, u'flaechen', u'flnam', u'f_', True):
        del dbQK
        return False

    # Löschen von Datensätzen ohne Linienobjekt
    if deletelinkGeomNone:
        sql = u"""DELETE FROM linkfl WHERE glink IS NULL"""

        if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkfl (1)'):
            return False

    # 1. Flächen in "linkfl" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            LEFT JOIN flaechen AS fl
            ON lf.flnam = fl.flnam
            WHERE fl.pk IS NULL OR NOT within(StartPoint(lf.glink),buffer(fl.geom,{eps})))
        UPDATE linkfl SET flnam =
        (   SELECT flnam
            FROM flaechen AS fl
            WHERE within(StartPoint(linkfl.glink),fl.geom) AND fl.geom IS NOT NULL)
        WHERE linkfl.pk IN missing""".format(eps=radiusHal)

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkfl (2)'):
        return False

    # progress_bar.setValue(30)

    # 2. Haltungen in "linkfl" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            LEFT JOIN haltungen AS ha
            ON lf.haltnam = ha.haltnam
            WHERE ha.pk IS NULL OR NOT intersects(buffer(EndPoint(lf.glink),{eps}),ha.geom))
        UPDATE linkfl SET haltnam =
        (   SELECT haltnam
            FROM haltungen AS ha
            WHERE intersects(buffer(EndPoint(linkfl.glink),{eps}),ha.geom))
        WHERE linkfl.pk IN missing""".format(eps=radiusHal)

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkfl (3)'):
        return False

    # progress_bar.setValue(65)

    # 3. TEZG-Flächen in "linkfl" eintragen (ohne Einschränkung auf auswahl), nur für aufteilen = 'ja'

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            LEFT JOIN tezg AS tg
            ON lf.flnam = tg.flnam
            WHERE tg.pk IS NULL OR NOT within(StartPoint(lf.glink),buffer(lf.geom,{eps})))
        UPDATE linkfl SET tezgnam =
        (   SELECT tg.flnam
            FROM tezg AS tg
            INNER JOIN (SELECT flnam FROM flaechen AS fl) as fl
            ON linkfl.flnam = fl.flnam
            WHERE within(StartPoint(linkfl.glink),tg.geom) AND tg.geom IS NOT NULL)
        WHERE linkfl.pk IN missing""".format(eps=radiusHal)

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkfl (4)'):
        return False

    dbQK.commit()

    fortschritt(u'Ende...', 1)
    # progress_bar.setValue(100)
    # status_message.setText(u"Bereinigung Flächenverknüpfungen abgeschlossen.")
    # status_message.setLevel(QgsMessageBar.SUCCESS)

    return True


def updatelinksw(dbQK, radiusHal = u'0.1', deletelinkGeomNone = True):
    # Datenvorbereitung: Verknüpfung von Einleitpunkt zu Haltung wird durch Tabelle "linksw"
    # repräsentiert. Diese Zuordnung wird zunächst in "einleit.haltnam" übertragen.

    # Statusmeldung in der Anzeige
    # global progress_bar
    # progress_bar = QProgressBar(iface.messageBar())
    # progress_bar.setRange(0, 100)
    # status_message = iface.messageBar().createMessage(u"", 
                # u"Bereinigung Einzeleinleiter-Verknüpfungen in Arbeit. Bitte warten.")
    # status_message.layout().addWidget(progress_bar)
    # iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    # progress_bar.setValue(1)

    # Löschen von Datensätzen ohne Linienobjekt
    if deletelinkGeomNone:
        sql = u"""DELETE FROM linksw WHERE glink IS NULL"""

        if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinksw (2)'):
            return False

    # 1. einleit-Punkt in "linksw" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linksw AS lf
            LEFT JOIN einleit AS el
            ON lf.elnam = el.elnam
            WHERE el.pk IS NULL OR NOT contains(buffer(StartPoint(lf.glink),{eps}),el.geom))
        UPDATE linksw SET elnam =
        (   SELECT elnam
            FROM einleit AS el
            WHERE contains(buffer(StartPoint(linksw.glink),{eps}),el.geom))
        WHERE linksw.pk IN missing""".format(eps=radiusHal)

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinksw (3)'):
        return False

    # progress_bar.setValue(30)

    # 2. Haltungen in "linksw" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linksw AS lf
            LEFT JOIN haltungen AS ha
            ON lf.haltnam = ha.haltnam
            WHERE ha.pk IS NULL OR NOT intersects(buffer(EndPoint(lf.glink),{eps}),ha.geom))
        UPDATE linksw SET haltnam =
        (   SELECT haltnam
            FROM haltungen AS ha
            WHERE intersects(buffer(EndPoint(linksw.glink),{eps}),ha.geom))
        WHERE linksw.pk IN missing""".format(eps=radiusHal)

    logger.debug(u'\nSQL-4b:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinksw (4)'):
        return False

    # progress_bar.setValue(60)

    # 3. Haltungen in "einleit" eintragen (ohne Einschränkung auf auswahl)

    # 3.2 Eintrag vornehmen

    sql = u"""WITH missing AS
        (   SELECT el.pk
            FROM einleit AS el
            INNER JOIN linksw AS lf
            ON el.elnam = lf.elnam
            WHERE (el.haltnam IS NULL AND lf.haltnam IS NOT NULL) OR el.haltnam <> lf.haltnam)
        UPDATE einleit SET haltnam =
        (   SELECT haltnam
            FROM linksw AS lf
            WHERE einleit.elnam = lf.elnam)
        WHERE einleit.pk IN missing"""

    logger.debug(u'\nSQL-4d:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinksw (6)'):
        return False

    dbQK.commit()

    fortschritt(u'Ende...', 1)
    # progress_bar.setValue(100)
    # status_message.setText(u"Bereinigung Einzeleinleiter-Verknüpfungen abgeschlossen.")
    # status_message.setLevel(QgsMessageBar.SUCCESS)

    return True


def updatelinkageb(dbQK, radiusHal = u'0.1', deletelinkGeomNone = True):
    # Datenvorbereitung: Verknüpfung von Aussengebiet zu Schacht wird durch Tabelle "linkageb"
    # repräsentiert. Diese Zuordnung wird zunächst in "aussengebiete.schnam" übertragen.

    # Löschen von Datensätzen ohne Linienobjekt
    if deletelinkGeomNone:
        sql = u"""DELETE FROM linkageb WHERE glink IS NULL"""

        if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkageb (2)'):
            return False

    # 1. Aussengebiet in "linkageb" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH missing AS
        (   SELECT lg.pk
            FROM linkageb AS lg
            LEFT JOIN aussengebiete AS ag
            ON lg.gebnam = ag.gebnam
            WHERE ag.pk IS NULL OR NOT within(StartPoint(lg.glink), ag.geom))
        UPDATE linkageb SET gebnam =
        (   SELECT gebnam
            FROM aussengebiete AS ag
            WHERE within(StartPoint(linkageb.glink),ag.geom))
        WHERE linkageb.pk IN missing""".format(eps=radiusHal)

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkageb (3)'):
        return False

    # progress_bar.setValue(30)

    # 2. Schächte in "linkageb" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH missing AS
        (   SELECT lg.pk
            FROM linkageb AS lg
            LEFT JOIN schaechte AS sc
            ON lg.schnam = sc.schnam
            WHERE sc.pk IS NULL OR NOT contains(buffer(EndPoint(lg.glink),{eps}),sc.geom))
        UPDATE linkageb SET schnam =
        (   SELECT schnam
            FROM schaechte AS sc
            WHERE contains(buffer(EndPoint(linkageb.glink),{eps}),sc.geom))
        WHERE linkageb.pk IN missing""".format(eps=radiusHal)

    logger.debug(u'\nSQL-4b:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkageb (4)'):
        return False

    # progress_bar.setValue(60)

    # 3. Schächte in "aussengebiete" eintragen (ohne Einschränkung auf auswahl)

    # 3.2 Eintrag vornehmen

    sql = u"""WITH missing AS
        (   SELECT ag.pk
            FROM aussengebiete AS ag
            INNER JOIN linkageb AS lg
            ON ag.gebnam = lg.gebnam
            WHERE (ag.schnam IS NULL AND lg.schnam IS NOT NULL) OR ag.schnam <> lg.schnam)
        UPDATE aussengebiete SET schnam =
        (   SELECT schnam
            FROM linkageb AS lg
            WHERE aussengebiete.gebnam = lg.gebnam)
        WHERE aussengebiete.pk IN missing"""

    logger.debug(u'\nSQL-4d:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u'dbQK: linkflaechen.updatelinks.updatelinkageb (6)'):
        return False

    dbQK.commit()

    fortschritt(u'Ende...', 1)
    # progress_bar.setValue(100)
    # status_message.setText(u"Bereinigung Aussengebiete-Verknüpfungen abgeschlossen.")
    # status_message.setLevel(QgsMessageBar.SUCCESS)

    return True
