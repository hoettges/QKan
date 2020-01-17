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

__author__ = "Joerg Hoettges"
__date__ = "February 2018"
__copyright__ = "(C) 2018, Joerg Hoettges"

import logging

from qkan.database.qkan_utils import check_flaechenbilanz, checknames, fortschritt

logger = logging.getLogger(u"QKan.linkflaechen.updatelinks")

# progress_bar = None


def updatelinkfl(
    dbQK, radiusHal=u"0.1", flaechen_bereinigen=False, deletelinkGeomNone=True
):
    """Aktualisierung des logischen Cache für die Tabelle "linkfl"

    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:             DBConnection

    :radiusHal:             Fangradius für das Verknüpfungsende auf der Haltung
    :type radiusHal:        Float

    :flaechen_bereinigen: Vor der Bearbeitung werden die Tabellen "flaechen" und "tezg" mit MakeValid korrigiert
    :type flaechen_bereinigen: Boolean

    Für den Benutzer maßgebend ist ausschließlich die graphische
    Verknüpfung von linkfl. Der Export basiert aber aus Performancegründen
    ausschließlich auf der logischen Verknüpfung ("logischer Cache").
    Deshalb erfolgt hier die Anpassung bzw. Korrektur der logischen Verknüpfungen.
    Aus Performancegründen wird in den nachfolgenden Abfragen zunächst immer 
    eine Auswahl der Datensätze aus "linkfl" vorgenommen, bei denen die logische 
    Verknüpfung mit der graphischen übereinstimmt (Unterabfrage "linksvalid") 
    und die Korrektur nur für die darin nicht enthaltenen Datensätze durchgeführt.
    """

    # Statusmeldung in der Anzeige
    # global progress_bar
    # progress_bar = QProgressBar(iface.messageBar())
    # progress_bar.setRange(0, 100)
    # status_message = iface.messageBar().createMessage(u"",
    # u"Bereinigung Flächenverknüpfungen in Arbeit. Bitte warten.")
    # status_message.layout().addWidget(progress_bar)
    # iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # progress_bar.setValue(1)

    # MakeValid auf Tabellen "flaechen" und "tezg".
    if flaechen_bereinigen:
        sql = """UPDATE flaechen SET geom=MakeValid(geom)"""
        if not dbQK.sql(sql, u"k_link.createlinkfl (1)"):
            del dbQK
            # progress_bar.reset()
            return False
        sql = """UPDATE tezg SET geom=MakeValid(geom)"""
        if not dbQK.sql(sql, u"k_link.createlinkfl (2)"):
            del dbQK
            # progress_bar.reset()
            return False
        # Flächen prüfen und ggfs. Meldung anzeigen
        check_flaechenbilanz(dbQK)

    # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
    if not checknames(dbQK, u"flaechen", u"flnam", u"f_", True):
        del dbQK
        return False

    # Löschen von Datensätzen ohne Linienobjekt
    if deletelinkGeomNone:
        sql = u"""DELETE FROM linkfl WHERE glink IS NULL"""

        if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkfl (1)"):
            return False

    # 1. Flächen in "linkfl" eintragen (ohne Einschränkung auf auswahl)
    # In der Unterabfrage "linksbroken" wird eine Liste aller nicht korrekter Verknüpfungen
    # aus linkfl erstellt,
    # so dass im UPDATE-Teil nur noch alle darin enthaltenen Verknüpfungen bearbeitet werden

    sql = u"""WITH linksbroken  AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            INNER JOIN flaechen AS fl
            ON lf.flnam = fl.flnam
            WHERE fl.geom IS NOT NULL AND NOT within(StartPoint(lf.glink),fl.geom))
        UPDATE linkfl SET flnam =
        (   SELECT flnam
            FROM flaechen AS fl
            WHERE within(StartPoint(linkfl.glink),fl.geom) AND fl.geom IS NOT NULL)
        WHERE linkfl.pk IN linksbroken """.format(
        eps=radiusHal
    )

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkfl (2)"):
        return False

    # progress_bar.setValue(30)

    # 2. Haltungen in "linkfl" eintragen (ohne Einschränkung auf auswahl)
    # Logik wie vor

    sql = u"""WITH linksbroken AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            INNER JOIN haltungen AS ha
            ON lf.haltnam = ha.haltnam
            WHERE ha.geom IS NOT NULL AND Distance(EndPoint(lf.glink),ha.geom) >= {eps})
        UPDATE linkfl SET haltnam =
        (   SELECT haltnam
            FROM haltungen AS ha
            WHERE Distance(EndPoint(linkfl.glink),ha.geom) < {eps})
        WHERE linkfl.pk IN linksbroken""".format(
        eps=radiusHal
    )

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkfl (3)"):
        return False

    # progress_bar.setValue(65)

    # 3. TEZG-Flächen in "linkfl" eintragen (ohne Einschränkung auf auswahl), nur für aufteilen = 'ja'
    # Gleiche Logik wie zuvor. Zusätzlich sind alle Flächen, die nicht aufgeteilt werden müssen, in
    # linksvalid enthalten, da Sie auf keinen Fall einen Eintrag in "tezgnam" erhalten sollen.

    sql = u"""WITH linksvalid AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            INNER JOIN tezg AS tg
            ON lf.tezgnam = tg.flnam
            INNER JOIN flaechen AS fl
            ON lf.flnam = fl.flnam
            WHERE (fl.aufteilen <> 'ja' OR fl.aufteilen IS NULL) OR 
                  (tg.geom IS NOT NULL AND within(StartPoint(lf.glink),buffer(tg.geom,{eps}))))
        UPDATE linkfl SET tezgnam =
        (   SELECT flnam
            FROM tezg AS tg
            WHERE within(StartPoint(linkfl.glink),tg.geom))
        WHERE linkfl.pk NOT IN linksvalid""".format(
        eps=radiusHal
    )

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkfl (4)"):
        return False

    dbQK.commit()

    fortschritt(u"Ende...", 1)
    # progress_bar.setValue(100)
    # status_message.setText(u"Bereinigung Flächenverknüpfungen abgeschlossen.")
    # status_message.setLevel(QgsMessageBar.SUCCESS)

    return True


def updatelinksw(dbQK, radiusHal=u"0.1", deletelinkGeomNone=True):
    # Datenvorbereitung: Verknüpfung von Einleitpunkt zu Haltung wird durch Tabelle "linksw"
    # repräsentiert. Diese Zuordnung wird zunächst in "einleit.haltnam" übertragen.

    # Statusmeldung in der Anzeige
    # global progress_bar
    # progress_bar = QProgressBar(iface.messageBar())
    # progress_bar.setRange(0, 100)
    # status_message = iface.messageBar().createMessage(u"",
    # u"Bereinigung Einzeleinleiter-Verknüpfungen in Arbeit. Bitte warten.")
    # status_message.layout().addWidget(progress_bar)
    # iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # progress_bar.setValue(1)

    # Löschen von Datensätzen ohne Linienobjekt
    if deletelinkGeomNone:
        sql = u"""DELETE FROM linksw WHERE glink IS NULL"""

        if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinksw (2)"):
            return False

    # 1. einleit-Punkt in "linksw" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH linksbroken AS
        (   SELECT lf.pk
            FROM linksw AS lf
            INNER JOIN einleit AS el
            ON lf.elnam = el.elnam
            WHERE el.geom IS NOT NULL AND Distance(StartPoint(lf.glink),el.geom) >= {eps})
        UPDATE linksw SET elnam =
        (   SELECT elnam
            FROM einleit AS el
            WHERE contains(buffer(StartPoint(linksw.glink),{eps}),el.geom))
        WHERE linksw.pk IN linksbroken""".format(
        eps=radiusHal
    )

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinksw (3)"):
        return False

    # progress_bar.setValue(30)

    # 2. Haltungen in "linksw" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH linksbroken AS
        (   SELECT lf.pk
            FROM linksw AS lf
            INNER JOIN haltungen AS ha
            ON lf.haltnam = ha.haltnam
            WHERE ha.geom IS NOT NULL AND Distance(EndPoint(lf.glink),ha.geom) >= {eps})
        UPDATE linksw SET haltnam =
        (   SELECT haltnam
            FROM haltungen AS ha
            WHERE Distance(EndPoint(linksw.glink),ha.geom) < {eps})
        WHERE linksw.pk IN linksbroken""".format(
        eps=radiusHal
    )

    logger.debug(u"\nSQL-4b:\n{}\n".format(sql))

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinksw (4)"):
        return False

    # progress_bar.setValue(60)

    # 3. Haltungen in "einleit" eintragen (ohne Einschränkung auf auswahl)

    # 3.2 Eintrag vornehmen

    sql = u"""WITH linksvalid AS
        (   SELECT el.pk
            FROM einleit AS el
            INNER JOIN linksw AS lf
            ON el.elnam = lf.elnam
            WHERE el.haltnam <> lf.haltnam)
        UPDATE einleit SET haltnam =
        (   SELECT haltnam
            FROM linksw AS lf
            WHERE einleit.elnam = lf.elnam)
        WHERE einleit.pk IN linksvalid"""

    logger.debug(u"\nSQL-4d:\n{}\n".format(sql))

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinksw (6)"):
        return False

    dbQK.commit()

    fortschritt(u"Ende...", 1)
    # progress_bar.setValue(100)
    # status_message.setText(u"Bereinigung Einzeleinleiter-Verknüpfungen abgeschlossen.")
    # status_message.setLevel(Qgis.Success)

    return True


def updatelinkageb(dbQK, radiusHal=u"0.1", deletelinkGeomNone=True):
    # Datenvorbereitung: Verknüpfung von Aussengebiet zu Schacht wird durch Tabelle "linkageb"
    # repräsentiert. Diese Zuordnung wird zunächst in "aussengebiete.schnam" übertragen.

    # Löschen von Datensätzen ohne Linienobjekt
    if deletelinkGeomNone:
        sql = u"""DELETE FROM linkageb WHERE glink IS NULL"""

        if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkageb (2)"):
            return False

    # 1. Aussengebiet in "linkageb" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH linksvalid AS
        (   SELECT lg.pk
            FROM linkageb AS lg
            LEFT JOIN aussengebiete AS ag
            ON lg.gebnam = ag.gebnam
            WHERE ag.pk IS NOT NULL AND within(StartPoint(lg.glink), ag.geom))
        UPDATE linkageb SET gebnam =
        (   SELECT gebnam
            FROM aussengebiete AS ag
            WHERE within(StartPoint(linkageb.glink),ag.geom))
        WHERE linkageb.pk NOT IN linksvalid""".format(
        eps=radiusHal
    )

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkageb (3)"):
        return False

    # progress_bar.setValue(30)

    # 2. Schächte in "linkageb" eintragen (ohne Einschränkung auf auswahl)

    sql = u"""WITH linksvalid AS
        (   SELECT lg.pk
            FROM linkageb AS lg
            LEFT JOIN schaechte AS sc
            ON lg.schnam = sc.schnam
            WHERE sc.pk IS NOT NULL AND contains(buffer(EndPoint(lg.glink),{eps}),sc.geom))
        UPDATE linkageb SET schnam =
        (   SELECT schnam
            FROM schaechte AS sc
            WHERE contains(buffer(EndPoint(linkageb.glink),{eps}),sc.geom))
        WHERE linkageb.pk NOT IN linksvalid""".format(
        eps=radiusHal
    )

    logger.debug(u"\nSQL-4b:\n{}\n".format(sql))

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkageb (4)"):
        return False

    # progress_bar.setValue(60)

    # 3. Schächte in "aussengebiete" eintragen (ohne Einschränkung auf auswahl)

    # 3.2 Eintrag vornehmen

    sql = u"""WITH linksvalid AS
        (   SELECT ag.pk
            FROM aussengebiete AS ag
            INNER JOIN linkageb AS lg
            ON ag.gebnam = lg.gebnam
            WHERE ag.schnam == lg.schnam)
        UPDATE aussengebiete SET schnam =
        (   SELECT schnam
            FROM linkageb AS lg
            WHERE aussengebiete.gebnam = lg.gebnam)
        WHERE aussengebiete.pk NOT IN linksvalid"""

    logger.debug(u"\nSQL-4d:\n{}\n".format(sql))

    if not dbQK.sql(sql, u"dbQK: linkflaechen.updatelinks.updatelinkageb (6)"):
        return False

    dbQK.commit()

    fortschritt(u"Ende...", 1)
    # progress_bar.setValue(100)
    # status_message.setText(u"Bereinigung Aussengebiete-Verknüpfungen abgeschlossen.")
    # status_message.setLevel(Qgis.Success)

    return True
