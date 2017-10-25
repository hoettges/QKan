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

logger = logging.getLogger('QKan')


# Fortschritts- und Fehlermeldungen

def fortschritt(text, prozent):
    logger.debug(u'{:s} ({:.0f}%)'.format(text, prozent * 100))
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text, prozent * 100), u'Link Flächen: ', QgsMessageLog.INFO)


def fehlermeldung(title, text):
    logger.debug(u'{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)


# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Flächen

def createlinkfl(dbQK, liste_flaechen_abflussparam, liste_hal_entw,
                liste_teilgebiete, suchradius=50, schreibe_haltungen=True, bezug_abstand='kante', 
                epsg='25832', fangradius=0.1, dbtyp='SpatiaLite'):
    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :liste_flaechen_abflussparam: Liste der ausgewählten Abflussparameter für die Flächen
    :type liste_flaechen_abflussparam: String

    :liste_hal_entw: Liste der ausgewählten Entwässerungsarten für die Haltungen
    :type liste_hal_entw: list of String

    :liste_teilgebiete: Liste der ausgewählten Teilgebiete
    :type liste_teilgebiete: list of String

    :suchradius: Suchradius in der SQL-Abfrage
    :type suchradius: Real

    :bezug_abstand: Bestimmt, ob in der SQL-Abfrage der Mittelpunkt oder die nächste Kante der Fläche
                    berücksichtigt wird
    :type fangradius: Real

    :fangradius: Suchradius für den Endpunkt in der SQL-Abfrage
    :type fangradius: Real

    :epsg: Nummer des Projektionssystems
    :type epsg: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Die Bearbeitung erfolgt in einer zusätzlichen Tabelle 'linkfl'
    # Sie wird zunächst aus der Tabelle "flaechen" erstellt, und enthält zusätzlich
    # zwei weitere Geo-Attribute: 
    #  gbuf  - Buffer sind die mit einem Buffer erweiterten Flächen
    #  glink - linkfl sind Verbindungslinien, die von der Fläche zur Haltung zeigen
    # zusätzlich wird die zugeordnete Haltung im entsprechenden Attribut verwaltet. 
    #
    # Flächen, bei denen im Feld "haltungen" bereits eine Eintragung vorhanden ist, 
    # werden nicht bearbeitet. Damit ist eine manuelle Zuordnung möglich. 


    # Kopieren der Flaechenobjekte in die Tabelle linkfl
    if len(liste_flaechen_abflussparam) == 0:
        auswahl = ''
        # logger.debug(u'Warnung in Link Flaechen: Keine Auswahl bei Flächen...')
    else:
        auswahl = " and flaechen.abflussparameter in ('{}')".format("', '".join(liste_flaechen_abflussparam))

    if len(liste_teilgebiete) != 0:
        auswahl += " and flaechen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

    # Sowohl Flächen, die nicht als auch die, die verschnitten werden müssen

    # SpatialIndex anlegen
    sqlindex = "SELECT CreateSpatialIndex('tezg','geom')"
    try:
        dbQK.sql(sqlindex)
    except BaseException as err:
        fehlermeldung('In der Tabelle "tezg" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
        del dbQK
        return False

    sql = u"""WITH flges AS (
                SELECT
                    flaechen.flnam, flaechen.aufteilen, flaechen.teilgebiet, 
                    flaechen.geom
                FROM flaechen
                WHERE (flaechen.aufteilen <> 'ja' or flaechen.aufteilen IS NULL){auswahl}
                UNION
                SELECT
                    flaechen.flnam, flaechen.aufteilen, flaechen.teilgebiet, 
                    CastToMultiPolygon(intersection(flaechen.geom,tezg.geom)) AS geom
                FROM flaechen
                INNER JOIN tezg
                ON intersects(flaechen.geom,tezg.geom)
                WHERE tezg.ROWID IN (
                    SELECT ROWID FROM SpatialIndex
                    WHERE f_table_name = 'tezg' AND
                        search_frame = flaechen.geom) AND 
                flaechen.aufteilen = 'ja'{auswahl})
            INSERT INTO linkfl (flnam, aufteilen, teilgebiet, geom)
            SELECT flges.flnam, flges.aufteilen, flges.teilgebiet, flges.geom
            FROM flges
            LEFT JOIN linkfl
            ON within(StartPoint(linkfl.glink),flges.geom)
            WHERE linkfl.pk IS NULL""".format(auswahl=auswahl)

    logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkFlaechen (4a) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Jetzt werden die Flächenobjekte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = u"""UPDATE linkfl SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linkfl.glink IS NULL""".format(
        suchradius)
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkFlaechen (2) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche. 
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen 
    # in tlink gefiltert wurden. 

    if len(liste_hal_entw) == 0:
        auswahl = ''
        # logger.debug(u'Warnung in Link Flaechen: Keine Auswahl bei Haltungen...')
    else:
        auswahl = " AND hal.entwart in ('{}')".format("', '".join(liste_hal_entw))

    if len(liste_teilgebiete) != 0:
        auswahl += " AND  hal.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        auswlin = " AND  linkfl.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

    if bezug_abstand == 'mittelpunkt':
        bezug = 'fl.geom'
    else:
        bezug = 'PointonSurface(fl.geom)'

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # tlink enthält alle potenziellen Verbindungen zwischen Flächen und Haltungen mit der jeweiligen Entfernung
    # t2 enthält von diesen Verbindungen nur die Fläche (als pk) und den minimalen Abstand, 
    # so dass in der Abfrage nach "update" nur die jeweils nächste Verbindung gefiltert wird. 
    # Da diese Abfrage nur für neu zu erstellende Verknüpfungen gelten soll (also noch kein Eintrag
    # im Feld "flaechen.haltnam" -> fl.haltnam -> tlink.linkhal -> t1.linkhal). 

    # SpatialIndex anlegen
    sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
    try:
        dbQK.sql(sqlindex)
    except BaseException as err:
        fehlermeldung('In der Tabelle "tezg" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
        del dbQK
        return False

    sql = u"""WITH tlink AS
            (	SELECT fl.pk AS pk,
                    Distance(hal.geom,{bezug}) AS dist, 
                    hal.geom AS geohal, fl.geom AS geofl
                FROM
                    haltungen AS hal
                INNER JOIN
                    linkfl AS fl
                ON Intersects(hal.geom,fl.gbuf)
                WHERE fl.glink IS NULL AND hal.ROWID IN
                (   SELECT ROWID FROM SpatialIndex WHERE
                    f_table_name = 'haltungen' AND
                    search_frame = fl.gbuf){auswahl})
            UPDATE linkfl SET glink =  
            (SELECT MakeLine(PointOnSurface(t1.geofl),Centroid(t1.geohal))
            FROM tlink AS t1
            INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
            WHERE linkfl.pk = t1.pk)
            WHERE linkfl.glink IS NULL{auswlin}""".format(bezug=bezug, auswahl=auswahl, auswlin=auswlin)

    logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkFlaechen (5) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Löschen der Datensätze in linkfl, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linkfl WHERE glink IS NULL"""

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkFlaechen (7) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    if schreibe_haltungen:
        # Nur wenn aktiviert, weil die beiden nachfolgenden Abfragen etwas länger dauern.

        # Haltungsname in Tabelle eintragen. Dabei findet keine Prüfung statt, 
        # ob Anfang der Verknüpfungslinie noch in zugehöriger Fläche liegt.
        # Dabei wird in zwei Schritten vorgegangen: Zuerst wird die Haltung in linkfl 
        # eingetragen, anschließend in der Fläche. Falls bei der Fläche das Attribut 
        # "aufteilen" auf 'ja' steht, wird kein Eintrag vorgenommen. 

        # 1. Schritt: Haltungsnamen in linkfl eintragen

        # SpatialIndex anlegen
        sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
        try:
            dbQK.sql(sqlindex)
        except BaseException as err:
            fehlermeldung('In der Tabelle "haltungen" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
            del dbQK
            return False

        if len(liste_teilgebiete) != 0:
            auswahl = " AND  haltungen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
            ausw_linkfl = " WHERE  linkfl.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ''
            ausw_linksw = ''

        sql = u"""WITH linkflbuf AS
                (   SELECT pk, buffer(EndPoint(linkfl.glink),{fangradius}) AS geob
                    FROM linkfl{ausw_linkfl}
                )
                UPDATE linkfl SET haltnam = 
                (   SELECT haltungen.haltnam
                    FROM linkflbuf
                    INNER JOIN haltungen
                    ON intersects(linkflbuf.geob,haltungen.geom)
                    WHERE haltungen.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'haltungen' AND
                        search_frame = linkflbuf.geob){auswahl} AND 
                    linkflbuf.pk = linkfl.pk
                )
                WHERE linkfl.pk in 
                (   SELECT linkflbuf.pk
                    FROM linkflbuf
                    INNER JOIN haltungen
                    ON intersects(linkflbuf.geob,haltungen.geom)
                    WHERE haltungen.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'haltungen' AND
                        search_frame = linkflbuf.geob){auswahl}
                )
            """.format(fangradius=fangradius, auswahl=auswahl, ausw_linkfl=ausw_linkfl)

        logger.debug(u'\nSQL-4a:\n{}\n'.format(sql))

        try:
            dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen (11) SQL-Fehler in SpatiaLite: \n", sql)
            del dbQK
            return False

        # 2. Schritt: Haltungsnamen von linkfl in Fläche übertragen. allerdings nur bei 
        # Flächen, die nicht aufgeteilt werden. 

        # SpatialIndex anlegen
        sqlindex = "SELECT CreateSpatialIndex('flaechen','geom')"
        try:
            dbQK.sql(sqlindex)
        except BaseException as err:
            fehlermeldung('In der Tabelle "flaechen" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
            del dbQK
            return False

        if len(liste_teilgebiete) != 0:
            ausw_linkfl = " WHERE linkfl.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
            ausw_fl = " AND fl.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
            ausw_flaechen = "flaechen.teilgebiet in ('{}') AND".format("', '".join(liste_teilgebiete))

        sql = u"""WITH linkflbuf AS
                (   SELECT pk, haltnam, StartPoint(linkfl.glink) AS geos
                    FROM linkfl{ausw_linkfl}
                )
                UPDATE flaechen SET haltnam = 
                (   SELECT linkflbuf.haltnam
                    FROM linkflbuf
                    INNER JOIN flaechen AS fl
                    ON within(linkflbuf.geos,fl.geom)
                    WHERE fl.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'flaechen' AND
                        search_frame = linkflbuf.geos){ausw_fl} AND 
                    fl.pk = flaechen.pk
                )
                WHERE {ausw_flaechen} (flaechen.aufteilen <> 'ja' or flaechen.aufteilen IS NULL) AND 
                flaechen.pk in 
                (   SELECT fl.pk
                    FROM linkflbuf
                    INNER JOIN flaechen AS fl
                    ON within(linkflbuf.geos,fl.geom)
                    WHERE fl.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'flaechen' AND
                        search_frame = linkflbuf.geos){ausw_fl}
                )""".format(ausw_fl=ausw_fl,
                      ausw_linkfl=ausw_linkfl, ausw_flaechen=ausw_flaechen)

        logger.debug(u'\nSQL-4b:\n{}\n'.format(sql))

        try:
            dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen (3) SQL-Fehler in SpatiaLite: \n", sql)
            del dbQK
            return False
        logger.debug(u'\nSQL-5:\n{}\n'.format(sql))

    dbQK.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True



# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Direkteinleitungen

def createlinkew(dbQK, liste_teilgebiete, suchradius=50, schreibe_haltungen=True, epsg='25832', fangradius=0.1,
                 dbtyp='SpatiaLite'):
    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :liste_teilgebiete: Liste der ausgewählten Teilgebiete
    :type liste_teilgebiete: list of String

    :suchradius: Suchradius in der SQL-Abfrage
    :type suchradius: Real

    :fangradius: Suchradius für den Endpunkt in der SQL-Abfrage
    :type fangradius: Real

    :epsg: Nummer des Projektionssystems
    :type epsg: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Die Bearbeitung erfolgt analog zu createlinkfl, mit folgenden Änderungen:
    # - Es gibt keine Auswahl nach Abflussparametern und Entwässerungssystem
    # - Es handelt sich um Punktobjekte anstelle von Flächen. 
    #   - Daher entfällt die Option, ob der Abstand auf die Kante oder den 
    #     Mittelpunkt bezogen werden soll
    #   - es gibt keine Verschneidung

    # Kopieren der EW-bezogenen-Einleitungen-Punkte in die Tabelle linkew. Dabei wird aus dem Punktobjekt
    # aus einwohner ein Flächenobjekt, damit ein Spatialindex verwendet werden kann 
    # (für POINT gibt es keinen MBR?)
    
    if len(liste_teilgebiete) != 0:
        auswahl = " AND einwohner.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
    else:
        auswahl = ''

    sql = u"""INSERT INTO linkew (pkewref, teilgebiet, geom)
            SELECT einwohner.pk, einwohner.teilgebiet,buffer(einwohner.geom,{radius})
            FROM einwohner
            LEFT JOIN linkew
            ON linkew.pkewref = einwohner.pk
            WHERE linkew.pk IS NULL{auswahl}""".format(auswahl=auswahl, radius = 0.5)

    logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_Link.createlinkew (4a) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Jetzt werden die EW-bezogenen Einleitungen-Punkte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = u"""UPDATE linkew SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linkew.glink IS NULL""".format(
        suchradius)
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_Link.createlinkew (2) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche. 
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen 
    # in tlink gefiltert wurden. 


    if len(liste_teilgebiete) != 0:
        auswahl = " AND hal.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        auswlin = " AND linkew.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
    else:
        auswahl = ''
        auswlin = ''

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # tlink enthält alle potenziellen Verbindungen zwischen Flächen und Haltungen mit der jeweiligen Entfernung
    # t2 enthält von diesen Verbindungen nur die Fläche (als pk) und den minimalen Abstand, 
    # so dass in der Abfrage nach "update" nur die jeweils nächste Verbindung gefiltert wird. 
    # Da diese Abfrage nur für neu zu erstellende Verknüpfungen gelten soll (also noch kein Eintrag
    # im Feld "einwohner.haltnam" -> ew.haltnam -> tlink.linkhal -> t1.linkhal). 

    # SpatialIndex anlegen
    sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
    try:
        dbQK.sql(sqlindex)
    except BaseException as err:
        fehlermeldung('In der Tabelle "tezg" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
        del dbQK
        return False

    sql = u"""WITH tlink AS
            (	SELECT ew.pk AS pk,
                    Distance(hal.geom,ew.geom) AS dist, 
                    hal.geom AS geohal, ew.geom AS geoew
                FROM
                    haltungen AS hal
                INNER JOIN
                    linkew AS ew
                ON Intersects(hal.geom,ew.gbuf)
                WHERE ew.glink IS NULL AND hal.ROWID IN
                (   SELECT ROWID FROM SpatialIndex WHERE
                    f_table_name = 'haltungen' AND
                    search_frame = ew.gbuf){auswahl})
            UPDATE linkew SET glink =  
            (SELECT MakeLine(PointOnSurface(t1.geoew),Centroid(t1.geohal))
            FROM tlink AS t1
            INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
            WHERE linkew.pk = t1.pk)
            WHERE linkew.glink IS NULL{auswlin}""".format(auswahl=auswahl, auswlin=auswlin)

    logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_Link.createlinkew (5) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Löschen der Datensätze in linkew, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linkew WHERE glink IS NULL"""

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_Link.createlinkew (7) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    if schreibe_haltungen:
        # Nur wenn aktiviert, weil die beiden nachfolgenden Abfragen etwas länger dauern.

        # Haltungsname in Tabelle eintragen. Dabei findet keine Prüfung statt, 
        # ob Anfang der Verknüpfungslinie noch in zugehöriger Fläche liegt.
        # Dabei wird in zwei Schritten vorgegangen: Zuerst wird die Haltung in linkfl 
        # eingetragen, anschließend in der Fläche. Falls bei der Fläche das Attribut 
        # "aufteilen" auf 'ja' steht, wird kein Eintrag vorgenommen. 

        # 1. Schritt: Haltungsnamen in linkfl eintragen

        # SpatialIndex anlegen
        sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
        try:
            dbQK.sql(sqlindex)
        except BaseException as err:
            fehlermeldung('In der Tabelle "haltungen" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
            del dbQK
            return False

        if len(liste_teilgebiete) != 0:
            auswahl = " AND  haltungen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
            ausw_linkew = " WHERE linkew.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ''
            ausw_linkew = ''

        sql = u"""WITH linkewbuf AS
                (   SELECT pk, 
                        MakeCircle(x(EndPoint(linkew.glink)),y(EndPoint(linkew.glink)),{fangradius}) AS geob
                    FROM linkew{ausw_linkew}
                )
                UPDATE linkew SET haltnam = 
                (   SELECT haltungen.haltnam
                    FROM linkewbuf
                    INNER JOIN haltungen
                    ON intersects(linkewbuf.geob,haltungen.geom)
                    WHERE haltungen.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'haltungen' AND
                        search_frame = linkewbuf.geob){auswahl} AND
                    linkewbuf.pk = linkew.pk
                )
                WHERE linkew.pk in 
                (   SELECT linkewbuf.pk
                    FROM linkewbuf
                    INNER JOIN haltungen
                    ON intersects(linkewbuf.geob,haltungen.geom)
                    WHERE haltungen.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'haltungen' AND
                        search_frame = linkewbuf.geob){auswahl}
                )""".format(fangradius=fangradius, ausw_linkew=ausw_linkew, auswahl=auswahl)

        logger.debug(u'\nSQL-4a:\n{}\n'.format(sql))

        try:
            dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_Link.createlinkew (3) SQL-Fehler in SpatiaLite: \n", sql)
            del dbQK
            return False

        # Abfrage ist identisch in k_qkhe.py vorhanden

        # SpatialIndex anlegen
        sqlindex = "SELECT CreateSpatialIndex('einwohner','geom')"
        try:
            dbQK.sql(sqlindex)
        except BaseException as err:
            fehlermeldung('In der Tabelle "einwohner" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
            del dbQK
            return False

        if len(liste_teilgebiete) != 0:
            ausw_ew = " AND ew.teilgebiet in ('{0:}') AND linkew.teilgebiet in ('{0:}')".format("', '".join(liste_teilgebiete))
            ausw_einwohner = "einwohner.teilgebiet in ('{}') AND".format("', '".join(liste_teilgebiete))
        else:
            ausw_ew = ""
            ausw_einwohner = ""

        sql = u"""UPDATE einwohner SET haltnam = 
                (   SELECT linkew.haltnam
                    FROM linkew
                    INNER JOIN einwohner AS ew
                    ON within(ew.geom,linkew.geom)
                    WHERE ew.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'einwohner' AND
                        search_frame = linkew.geom){ausw_ew} AND
                    ew.pk = einwohner.pk
                )
                WHERE {ausw_einwohner} einwohner.pk in 
                (   SELECT ew.pk
                    FROM linkew
                    INNER JOIN einwohner AS ew
                    ON within(ew.geom,linkew.geom)
                    WHERE ew.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'einwohner' AND
                        search_frame = linkew.geom){ausw_ew}
                )""".format(ausw_ew=ausw_ew, ausw_einwohner=ausw_einwohner)

        logger.debug(u'\nSQL-4b:\n{}\n'.format(sql))

        try:
            dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_Link.createlinkew (3) SQL-Fehler in SpatiaLite: \n", sql)
            del dbQK
            return False
        # logger.debug(u'\nSQL-5:\n{}\n'.format(sql))

    dbQK.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True


# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Direkteinleitungen

def createlinksw(dbQK, liste_teilgebiete, suchradius=50, schreibe_haltungen=True, epsg='25832', fangradius=0.1,
                 dbtyp='SpatiaLite'):
    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :liste_teilgebiete: Liste der ausgewählten Teilgebiete
    :type liste_teilgebiete: list of String

    :suchradius: Suchradius in der SQL-Abfrage
    :type suchradius: Real

    :fangradius: Suchradius für den Endpunkt in der SQL-Abfrage
    :type fangradius: Real

    :epsg: Nummer des Projektionssystems
    :type epsg: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Die Bearbeitung erfolgt analog zu createlinkfl, mit folgenden Änderungen:
    # - Es gibt keine Auswahl nach Abflussparametern und Entwässerungssystem
    # - Es handelt sich um Punktobjekte anstelle von Flächen. 
    #   - Daher entfällt die Option, ob der Abstand auf die Kante oder den 
    #     Mittelpunkt bezogen werden soll
    #   - es gibt keine Verschneidung

    # Kopieren der Direkteinleitungen-Punkte in die Tabelle linksw. Dabei wird aus dem Punktobjekt
    # aus einleit ein Flächenobjekt, damit ein Spatialindex verwendet werden kann 
    # (für POINT gibt es keinen MBR?)
    
    if len(liste_teilgebiete) != 0:
        auswahl = " AND einleit.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
    else:
        auswahl = ''

    sql = u"""INSERT INTO linksw (pkswref, teilgebiet, geom)
            SELECT einleit.pk, einleit.teilgebiet,buffer(einleit.geom,{radius})
            FROM einleit
            LEFT JOIN linksw
            ON linksw.pkswref = einleit.pk
            WHERE linksw.pk IS NULL{auswahl}""".format(auswahl=auswahl, radius = 0.5)

    logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkSW (4a) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Jetzt werden die Direkteinleitungen-Punkte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = u"""UPDATE linksw SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linksw.glink IS NULL""".format(
        suchradius)
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkSW (2) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche. 
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen 
    # in tlink gefiltert wurden. 


    if len(liste_teilgebiete) != 0:
        auswahl = " AND  hal.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        auswlin = " AND  linksw.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
    else:
        auswahl = ''

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # tlink enthält alle potenziellen Verbindungen zwischen Flächen und Haltungen mit der jeweiligen Entfernung
    # t2 enthält von diesen Verbindungen nur die Fläche (als pk) und den minimalen Abstand, 
    # so dass in der Abfrage nach "update" nur die jeweils nächste Verbindung gefiltert wird. 
    # Da diese Abfrage nur für neu zu erstellende Verknüpfungen gelten soll (also noch kein Eintrag
    # im Feld "einleit.haltnam" -> sw.haltnam -> tlink.linkhal -> t1.linkhal). 

    # SpatialIndex anlegen
    sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
    try:
        dbQK.sql(sqlindex)
    except BaseException as err:
        fehlermeldung('In der Tabelle "tezg" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
        del dbQK
        return False

    sql = u"""WITH tlink AS
            (	SELECT sw.pk AS pk,
                    Distance(hal.geom,sw.geom) AS dist, 
                    hal.geom AS geohal, sw.geom AS geosw
                FROM
                    haltungen AS hal
                INNER JOIN
                    linksw AS sw
                ON Intersects(hal.geom,sw.gbuf)
                WHERE sw.glink IS NULL AND hal.ROWID IN
                (   SELECT ROWID FROM SpatialIndex WHERE
                    f_table_name = 'haltungen' AND
                    search_frame = sw.gbuf){auswahl})
            UPDATE linksw SET glink =  
            (SELECT MakeLine(PointOnSurface(t1.geosw),Centroid(t1.geohal))
            FROM tlink AS t1
            INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
            WHERE linksw.pk = t1.pk)
            WHERE linksw.glink IS NULL{auswlin}""".format(auswahl=auswahl, auswlin=auswlin)

    logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkSW (5) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    # Löschen der Datensätze in linksw, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linksw WHERE glink IS NULL"""

    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkSW (7) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    if schreibe_haltungen:
        # Nur wenn aktiviert, weil die beiden nachfolgenden Abfragen etwas länger dauern.

        # Haltungsname in Tabelle eintragen. Dabei findet keine Prüfung statt, 
        # ob Anfang der Verknüpfungslinie noch in zugehöriger Fläche liegt.
        # Dabei wird in zwei Schritten vorgegangen: Zuerst wird die Haltung in linkfl 
        # eingetragen, anschließend in der Fläche. Falls bei der Fläche das Attribut 
        # "aufteilen" auf 'ja' steht, wird kein Eintrag vorgenommen. 

        # 1. Schritt: Haltungsnamen in linkfl eintragen

        # SpatialIndex anlegen
        sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
        try:
            dbQK.sql(sqlindex)
        except BaseException as err:
            fehlermeldung('In der Tabelle "haltungen" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
            del dbQK
            return False

        if len(liste_teilgebiete) != 0:
            auswahl = " AND  haltungen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
            ausw_linksw = " WHERE linksw.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ''
            ausw_linksw = ''

        sql = u"""WITH linkswbuf AS
                (   SELECT pk, 
                        MakeCircle(x(EndPoint(linksw.glink)),y(EndPoint(linksw.glink)),{fangradius}) AS geob
                    FROM linksw{ausw_linksw}
                )
                UPDATE linksw SET haltnam = 
                (   SELECT haltungen.haltnam
                    FROM linkswbuf
                    INNER JOIN haltungen
                    ON intersects(linkswbuf.geob,haltungen.geom)
                    WHERE haltungen.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'haltungen' AND
                        search_frame = linkswbuf.geob){auswahl} AND
                    linkswbuf.pk = linksw.pk
                )
                WHERE linksw.pk in 
                (   SELECT linkswbuf.pk
                    FROM linkswbuf
                    INNER JOIN haltungen
                    ON intersects(linkswbuf.geob,haltungen.geom)
                    WHERE haltungen.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'haltungen' AND
                        search_frame = linkswbuf.geob){auswahl}
                )""".format(fangradius=fangradius, ausw_linksw=ausw_linksw, auswahl=auswahl)

        logger.debug(u'\nSQL-4a:\n{}\n'.format(sql))

        try:
            dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkSW (3) SQL-Fehler in SpatiaLite: \n", sql)
            del dbQK
            return False

        # Abfrage ist identisch in k_qkhe.py vorhanden

        # SpatialIndex anlegen
        sqlindex = "SELECT CreateSpatialIndex('einleit','geom')"
        try:
            dbQK.sql(sqlindex)
        except BaseException as err:
            fehlermeldung('In der Tabelle "einleit" konnte CreateSpatialIndex auf "geom" nicht durchgeführt werden', str(err))
            del dbQK
            return False

        if len(liste_teilgebiete) != 0:
            ausw_sw = " AND sw.teilgebiet in ('{0:}') AND linksw.teilgebiet in ('{0:}')".format("', '".join(liste_teilgebiete))
            ausw_einleit = "einleit.teilgebiet in ('{}') AND".format("', '".join(liste_teilgebiete))
        else:
            ausw_sw = ""
            ausw_einleit = ""

        sql = u"""UPDATE einleit SET haltnam = 
                (   SELECT linksw.haltnam
                    FROM linksw
                    INNER JOIN einleit AS sw
                    ON within(sw.geom,linksw.geom)
                    WHERE sw.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'einleit' AND
                        search_frame = linksw.geom){ausw_sw} AND
                    sw.pk = einleit.pk
                )
                WHERE {ausw_einleit} einleit.pk in 
                (   SELECT sw.pk
                    FROM linksw
                    INNER JOIN einleit AS sw
                    ON within(sw.geom,linksw.geom)
                    WHERE sw.ROWID IN 
                    (   SELECT ROWID FROM SpatialIndex WHERE
                        f_table_name = 'einleit' AND
                        search_frame = linksw.geom){ausw_sw}
                )""".format(ausw_sw=ausw_sw, ausw_einleit=ausw_einleit)

        logger.debug(u'\nSQL-4b:\n{}\n'.format(sql))

        try:
            dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkSW (3) SQL-Fehler in SpatiaLite: \n", sql)
            del dbQK
            return False
        # logger.debug(u'\nSQL-5:\n{}\n'.format(sql))

    dbQK.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True



# -------------------------------------------------------------------------------------------------------------

def assigntezg(dbQK, auswahltyp, liste_teilgebiete, tablist, dbtyp = 'SpatiaLite'):
    '''Ordnet alle Objete aus den in "tablist" enthaltenen Tabellen einer der in "liste_teilgebiete" enthaltenen
       Teilgebiete zu. Falls sich mehrere dieser Teilgebiete überlappen, ist das Resultat zufällig eines von diesen. 

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :liste_teilgebiete: Name des auf die gewählten Tabellen zu übertragenden Teilgebietes
    :type liste_teilgebiete: list of String

    :tablist: Liste der Tabellen, auf die die Teilgebiet "liste_teilgebiete" zu übertragen sind.
    :type tablist: list of String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    if auswahltyp == 'within':
        spatialrelation = 'within'
    elif auswahltyp == 'overlaps':
        spatialrelation = 'intersects'
    if len(liste_teilgebiete) != 0:
        tgnames = "', '".join(liste_teilgebiete)
        for table in tablist:
            sql = u"""
            UPDATE {table} SET teilgebiet = 
            (	SELECT teilgebiete.tgnam
                FROM teilgebiete
                INNER JOIN {table} AS tt
                ON {spatialrelation}(tt.geom,teilgebiete.geom)
                WHERE tt.pk = {table}.pk AND
                       teilgebiete.tgnam in ('{tgnames}'))
            WHERE {table}.pk IN
            (	SELECT {table}.pk
                FROM teilgebiete
                INNER JOIN {table}
                ON {spatialrelation}({table}.geom,teilgebiete.geom)
                WHERE teilgebiete.tgnam in ('{tgnames}'))
            """.format(table=table, tgnames=tgnames, spatialrelation=spatialrelation)

            logger.debug(u'\nSQL:\n{}\n'.format(sql))

            try:
                dbQK.sql(sql)
            except:
                fehlermeldung(u"QKan_LinkFlaechen (8) SQL-Fehler in SpatiaLite: \n", sql)
                del dbQK
                return False

        dbQK.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Zuordnung von Haltungen und Flächen ist fertig!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nZuordnung von Haltungen und Flächen ist fertig!", level=QgsMessageLog.INFO)

    return True


# -------------------------------------------------------------------------------------------------------------

def reloadgroup(dbQK, gruppenname, dbtyp = 'SpatiaLite'):
    '''Lädt die unter einem Gruppennamen gespeicherten Teilgebietszuordnungen zurück in die Tabellen 
       "haltungen", "schaechte", "flaechen", "tezg", "linkfl", "linksw", "einleit", "einwohner"

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :gruppenname: Bezeichnung der Gruppe, unter der die Teilgebietszuordnungen abgelegt wurden.
    :type gruppenname: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    tablist = ["haltungen", "schaechte", "flaechen", "linkfl", "tezg", "einleit", "einwohner"]

    for table in tablist:
        sql = u"""
        UPDATE {table}
        SET teilgebiet = 
        (   SELECT g.teilgebiet
            FROM gruppen AS g
            WHERE g.grnam = '{gruppenname}' AND
            g.tabelle = '{table}' AND
            {table}.pk = g.pktab)
        WHERE {table}.pk IN
        (   SELECT g.teilgebiet
            FROM gruppen AS g
            WHERE g.grnam = '{gruppenname}' AND
            g.tabelle = '{table}')""".format(table=table, gruppenname=gruppenname)
        # logger.debug(u'reloadgroup.sql: \n{}'.format(sql))
        try:
            dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen.reloadgroup (9) SQL-Fehler in SpatiaLite: \n", sql)
            del dbQK
            return False

    dbQK.commit()

    return True



# -------------------------------------------------------------------------------------------------------------

def storegroup(dbQK, gruppenname, kommentar, dbtyp = 'SpatiaLite'):
    '''Speichert die aktuellen Teilgebietszuordnungen der Tabellen 
       "haltungen", "schaechte", "flaechen", "tezg", "linkfl", "linksw", "einleit", "einwohner"
       unter einem neuen Gruppennamen

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :gruppenname: Bezeichnung der Gruppe, unter der die Teilgebietszuordnungen abgelegt werden.
    :type gruppenname: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    tablist = ["haltungen", "schaechte", "flaechen", "linkfl", "tezg", "einleit", "einwohner"]

    # Abfrage setzt sich aus den mit UNION verbundenen Tabellen aus tablist zusammen...
    sql = u"""
    INSERT INTO gruppen
    (grnam, pktab, teilgebiet, tabelle, kommentar)
    SELECT 
      '{gruppenname}' AS grnam,
      pk AS pktab, 
      teilgebiet AS teilgebiet, 
      'haltungen' AS tabelle, 
      '{kommentar}' AS kommentar
    FROM
      haltungen
    WHERE teilgebiet <> '' And teilgebiet IS NOT NULL
    """.format(gruppenname=gruppenname, kommentar=kommentar)

    for table in tablist[1:]:
        sql += u"""UNION
        SELECT 
          '{gruppenname}' AS grnam,
          pk AS pktab, 
          teilgebiet AS teilgebiet, 
          '{table}' AS tabelle, 
          '{kommentar}' AS kommentar
        FROM
          {table}
        WHERE teilgebiet <> '' And teilgebiet IS NOT NULL
        """.format(gruppenname=gruppenname, kommentar=kommentar,table=table)

    # logger.debug(u'\nSQL-4:\n{}\n'.format(sql))
    # Zusammengesetzte SQL-Abfrage ausführen...
    try:
        dbQK.sql(sql)
    except:
        fehlermeldung(u"QKan_LinkFlaechen.savegroup (10) SQL-Fehler in SpatiaLite: \n", sql)
        del dbQK
        return False

    dbQK.commit()

    return True
