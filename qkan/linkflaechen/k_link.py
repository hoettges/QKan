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

# Progress bar
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qkan.database.qgis_utils import fehlermeldung, checknames

logger = logging.getLogger('QKan')


# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Flächen

def createlinkfl(dbQK, liste_flaechen_abflussparam, liste_hal_entw,
                liste_teilgebiete, suchradius=50, bezug_abstand='kante', 
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

    # Progress Bar
    bar = QProgressDialog()
    bar.setRange(0,0)
    bar.show()

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

    if not dbQK.sql(sqlindex, 'CreateSpatialIndex in der Tabelle "tezg" auf "geom"'):
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

    # logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan_LinkFlaechen (4a) SQL-Fehler in SpatiaLite"):
        return False

    # Jetzt werden die Flächenobjekte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = u"""UPDATE linkfl SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linkfl.glink IS NULL""".format(
        suchradius)
    if not dbQK.sql(sql, u"createlinkfl (2)"):
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche. 
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen 
    # in tlink gefiltert wurden. 

    if len(liste_hal_entw) == 0:
        auswha = ''
    else:
        auswha = " AND ha.entwart in ('{}')".format("', '".join(liste_hal_entw))

    if len(liste_teilgebiete) != 0:
        auswha += " AND  ha.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        auswlinkfl = " AND  linkfl.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

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

    if not dbQK.sql(sqlindex, 'CreateSpatialIndex in der Tabelle "tezg" auf "geom"'):
        return False

    sql = u"""WITH tlink AS
            (	SELECT fl.pk AS pk,
                    Distance(ha.geom,{bezug}) AS dist, 
                    ha.geom AS geohal, fl.geom AS geofl
                FROM
                    haltungen AS ha
                INNER JOIN
                    linkfl AS fl
                ON Intersects(ha.geom,fl.gbuf)
                WHERE fl.glink IS NULL AND ha.ROWID IN
                (   SELECT ROWID FROM SpatialIndex WHERE
                    f_table_name = 'haltungen' AND
                    search_frame = fl.gbuf){auswha})
            UPDATE linkfl SET glink =  
            (SELECT MakeLine(PointOnSurface(t1.geofl),Centroid(t1.geohal))
            FROM tlink AS t1
            INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
            WHERE linkfl.pk = t1.pk)
            WHERE linkfl.glink IS NULL{auswlinkfl}""".format(bezug=bezug, auswha=auswha, auswlinkfl=auswlinkfl)

    # logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"createlinkfl (5)"):
        return False

    # Löschen der Datensätze in linkfl, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linkfl WHERE glink IS NULL"""

    if not dbQK.sql(sql, u"QKan_LinkFlaechen (7) SQL-Fehler in SpatiaLite"):
        return False

    # Verknüpfen von linkfl mit Haltungen, Flächen und tezg-Flächen. Dabei wird die Auswahl berücksichtigt, 
    # um die Abfrage zu beschleunigen. 

    # 1. Flächen in "linkfl" eintragen

    # Nur ausgewählte Flächen
    if len(liste_hal_entw) == 0:
        auswfl = ''
    else:
        auswfl = "fl.teilgebiet in ('{}') AND ".format("', '".join(liste_teilgebiete))

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            LEFT JOIN flaechen AS fl
            ON lf.flnam = fl.flnam
            WHERE {auswfl}(fl.pk IS NULL OR NOT within(StartPoint(linkfl.glink),fl.geom)))
        UPDATE linkfl SET flnam =
        (   SELECT flnam
            FROM flaechen AS fl
            WHERE within(StartPoint(linkfl.glink),fl.geom))
        WHERE linkfl.pk IN missing"""
    # logger.debug(u'Eintragen der verknüpften Flächen in linkfl: \n{}'.format(sql))

    if not dbQK.sql(sql, u"QKan_Export (24)"):
        return False

    # 2. Haltungen in "linkfl" eintragen

    # Nur ausgewählte Haltungen
    if len(liste_hal_entw) == 0:
        auswha = ''
    else:
        auswha = "ha.teilgebiet in ('{}') AND ".format("', '".join(liste_teilgebiete))

    if len(liste_hal_entw) <> 0:
        auswha += "ha.entwart in ('{}') AND ".format("', '".join(liste_hal_entw))

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            LEFT JOIN haltungen AS ha
            ON lf.haltnam = ha.haltnam
            WHERE {auswha}(ha.pk IS NULL OR NOT intersects(buffer(EndPoint(linkfl.glink),0.1),ha.geom)))
        UPDATE linkfl SET haltnam =
        (   SELECT haltnam
            FROM haltungen AS ha
            WHERE intersects(buffer(EndPoint(linkfl.glink),0.1),ha.geom))
        WHERE linkfl.pk IN missing"""
    # logger.debug(u'Eintragen der verknüpften Haltungen in linkfl: \n{}'.format(sql))

    if not dbQK.sql(sql, u"QKan_Export (25)"):
        return False

        # 3. TEZG-Flächen in "linkfl" eintragen, nur für aufteilen = 'ja'

    # Nur ausgewählte tezg-Flächen
    if len(liste_hal_entw) == 0:
        auswtg = ''
    else:
        auswtg = "tg.teilgebiet in ('{}') AND ".format("', '".join(liste_teilgebiete))

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkfl AS lf
            LEFT JOIN tezg AS tg
            ON lf.flnam = tg.flnam
            WHERE {auswtg}(tg.pk IS NULL OR NOT within(StartPoint(linkfl.glink),tg.geom)))
        UPDATE linkfl SET tezgnam =
        (   SELECT tg.flnam
            FROM tezg AS tg
            INNER JOIN (SELECT flnam FROM flaechen WHERE fl.aufteilen = 'ja') as fl
            ON linkfl.flnam = fl.flnam
            WHERE within(StartPoint(linkfl.glink),tg.geom))
        WHERE linkfl.pk IN missing"""
    # logger.debug(u'Eintragen der verknüpften Haltungen in linkfl: \n{}'.format(sql))

    if not dbQK.sql(sql, u"QKan_Export (26)"):
        return False

    dbQK.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True



# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Direkteinleitungen

def createlinkew(dbQK, liste_teilgebiete, suchradius=50, epsg='25832', fangradius=0.1,
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
    
    # Progress Bar
    bar = QProgressDialog()
    bar.setRange(0,0)
    bar.show()

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

    # logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan_Link.createlinkew (4a) SQL-Fehler in SpatiaLite"):
        return False

    # Jetzt werden die EW-bezogenen Einleitungen-Punkte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = u"""UPDATE linkew SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linkew.glink IS NULL""".format(
        suchradius)

    if not dbQK.sql(sql, u"QKan_Link.createlinkew (2) SQL-Fehler in SpatiaLite"):
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

    if not dbQK.sql(sqlindex, u'CreateSpatialIndex in der Tabelle "tezg" auf "geom"'):
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

    # logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan_Link.createlinkew (5) SQL-Fehler in SpatiaLite"):
        return False

    # Löschen der Datensätze in linkew, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linkew WHERE glink IS NULL"""

    if not dbQK.sql(sql, u"QKan_Link.createlinkew (7) SQL-Fehler in SpatiaLite"):
        return False

    # 1. einwohner-Punkt in "linkew" eintragen

    # Nur ausgewählte Haltungen
    if len(liste_hal_entw) == 0:
        auswew = ''
    else:
        auswew = "el.teilgebiet in ('{}') AND ".format("', '".join(liste_teilgebiete))

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkew AS lf
            LEFT JOIN einwohner AS el
            ON lf.elnam = el.elnam
            WHERE {auswew}(el.pk IS NULL OR NOT contains(buffer(StartPoint(lf.glink),0.1),el.geom)))
        UPDATE linkew SET elnam =
        (   SELECT elnam
            FROM einwohner AS el
            WHERE contains(buffer(StartPoint(linkew.glink),0.1),el.geom))
        WHERE linkew.pk IN missing"""

    # logger.debug(u'\nSQL-4a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan.k_qkhe (4a) SQL-Fehler in SpatiaLite"):
        return False

    # 2. Haltungen in "linkew" eintragen

    # Nur ausgewählte Haltungen

    if len(liste_hal_entw) == 0:
        auswha = ''
    else:
        auswha = "ha.teilgebiet in ('{}') AND ".format("', '".join(liste_teilgebiete))

    if len(liste_hal_entw) <> 0:
        auswha += "ha.entwart in ('{}') AND ".format("', '".join(liste_hal_entw))

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linkew AS lf
            LEFT JOIN haltungen AS ha
            ON lf.haltnam = ha.haltnam
            WHERE {auswha}(ha.pk IS NULL OR NOT intersects(buffer(EndPoint(lf.glink),0.1),ha.geom)))
        UPDATE linkew SET haltnam =
        (   SELECT haltnam
            FROM haltungen AS ha
            WHERE intersects(buffer(EndPoint(linkew.glink),0.1),ha.geom))
        WHERE linkew.pk IN missing"""

    # logger.debug(u'\nSQL-4b:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan.k_qkhe (4b) SQL-Fehler in SpatiaLite"):
        return False

    dbQK.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True


# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Direkteinleitungen

def createlinksw(dbQK, liste_teilgebiete, suchradius=50, epsg='25832', fangradius=0.1,
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
    
    # Progress Bar
    bar = QProgressDialog()
    bar.setRange(0,0)
    bar.show()

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

    # logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan_LinkSW (4a) SQL-Fehler in SpatiaLite"):
        return False

    # Jetzt werden die Direkteinleitungen-Punkte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = u"""UPDATE linksw SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linksw.glink IS NULL""".format(
        suchradius)

    if not dbQK.sql(sql, u"QKan_LinkSW (2) SQL-Fehler in SpatiaLite"):
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

    if not dbQK.sql(sqlindex, u'CreateSpatialIndex in der Tabelle "tezg" auf "geom"'):
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

    # logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan_LinkSW (5) SQL-Fehler in SpatiaLite"):
        return False

    # Löschen der Datensätze in linksw, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linksw WHERE glink IS NULL"""

    if not dbQK.sql(sql, u"QKan_LinkSW (7) SQL-Fehler in SpatiaLite"):
        return False

    # 1. einleit-Punkt in "linksw" eintragen (ohne Einschränkung auf auswahl)

    # Nur ausgewählte Haltungen
    if len(liste_hal_entw) == 0:
        auswel = ''
    else:
        auswel = "el.teilgebiet in ('{}') AND ".format("', '".join(liste_teilgebiete))

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linksw AS lf
            LEFT JOIN einleit AS el
            ON lf.elnam = el.elnam
            WHERE {auswel}(el.pk IS NULL OR NOT contains(buffer(StartPoint(lf.glink),0.1),el.geom)))
        UPDATE linksw SET elnam =
        (   SELECT elnam
            FROM einleit AS el
            WHERE contains(buffer(StartPoint(linksw.glink),0.1),el.geom))
        WHERE linksw.pk IN missing"""

    # logger.debug(u'\nSQL-4a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan.k_qkhe (4a) SQL-Fehler in SpatiaLite"):
        return False

    # 2. Haltungen in "linksw" eintragen (ohne Einschränkung auf auswahl)

    # Nur ausgewählte Haltungen

    if len(liste_hal_entw) == 0:
        auswha = ''
    else:
        auswha = "ha.teilgebiet in ('{}') AND ".format("', '".join(liste_teilgebiete))

    if len(liste_hal_entw) <> 0:
        auswha += "ha.entwart in ('{}') AND ".format("', '".join(liste_hal_entw))

    sql = u"""WITH missing AS
        (   SELECT lf.pk
            FROM linksw AS lf
            LEFT JOIN haltungen AS ha
            ON lf.haltnam = ha.haltnam
            WHERE {auswha}(ha.pk IS NULL OR NOT intersects(buffer(EndPoint(lf.glink),0.1),ha.geom)))
        UPDATE linksw SET haltnam =
        (   SELECT haltnam
            FROM haltungen AS ha
            WHERE intersects(buffer(EndPoint(linksw.glink),0.1),ha.geom))
        WHERE linksw.pk IN missing"""

    # logger.debug(u'\nSQL-4b:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan.k_qkhe (4b) SQL-Fehler in SpatiaLite"):
        return False

    dbQK.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True



# -------------------------------------------------------------------------------------------------------------

def assigntgeb(dbQK, auswahltyp, liste_teilgebiete, tablist, autokorrektur, bufferradius='0', dbtyp = 'SpatiaLite'):
    '''Ordnet alle Objete aus den in "tablist" enthaltenen Tabellen einer der in "liste_teilgebiete" enthaltenen
       Teilgebiete zu. Falls sich mehrere dieser Teilgebiete überlappen, ist das Resultat zufällig eines von diesen. 

    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database:         DBConnection (geerbt von dbapi...)

    :liste_teilgebiete:     Name des auf die gewählten Tabellen zu übertragenden Teilgebietes
    :type liste_teilgebiete:list of String

    :tablist:               Liste der Tabellen, auf die die Teilgebiet "liste_teilgebiete" zu übertragen sind.
    :type tablist:          list of String

    :autokorrektur:         Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                            werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                            abgebrochen.
    :type autokorrektur:    String
    
    :dbtyp:                 Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:            String
    
    :returns:               void
    '''

    # Progress Bar
    bar = QProgressDialog()
    bar.setRange(0,0)
    bar.show()

    # logger.debug(u'\nbetroffene Tabellen (1):\n{}\n'.format(str(tablist)))

    if not checknames(dbQK, 'teilgebiete', 'tgnam', 'tg_', autokorrektur):
        return False

    if len(liste_teilgebiete) != 0:
        tgnames = "', '".join(liste_teilgebiete)
        for table in tablist:

            if auswahltyp == 'within':
                if bufferradius == '0' or bufferradius.strip == '':
                    sql = u"""
                    UPDATE {table} SET teilgebiet = 
                    (	SELECT teilgebiete.tgnam
                        FROM teilgebiete
                        INNER JOIN {table} AS tt
                        ON within(tt.geom, teilgebiete.geom)
                        WHERE tt.pk = {table}.pk AND
                               teilgebiete.tgnam in ('{tgnames}'))
                    WHERE {table}.pk IN
                    (	SELECT {table}.pk
                        FROM teilgebiete
                        INNER JOIN {table}
                        ON within({table}.geom, teilgebiete.geom)
                        WHERE teilgebiete.tgnam in ('{tgnames}'))
                    """.format(table=table, tgnames=tgnames, bufferradius=bufferradius)
                else:
                    sql = u"""
                    UPDATE {table} SET teilgebiet = 
                    (	SELECT teilgebiete.tgnam
                        FROM teilgebiete
                        INNER JOIN {table} AS tt
                        ON within(tt.geom, buffer(teilgebiete.geom, {bufferradius}))
                        WHERE tt.pk = {table}.pk AND
                               teilgebiete.tgnam in ('{tgnames}'))
                    WHERE {table}.pk IN
                    (	SELECT {table}.pk
                        FROM teilgebiete
                        INNER JOIN {table}
                        ON within({table}.geom, buffer(teilgebiete.geom, {bufferradius}))
                        WHERE teilgebiete.tgnam in ('{tgnames}'))
                    """.format(table=table, tgnames=tgnames, bufferradius=bufferradius)
            elif auswahltyp == 'overlaps':
                sql = u"""
                UPDATE {table} SET teilgebiet = 
                (	SELECT teilgebiete.tgnam
                    FROM teilgebiete
                    INNER JOIN {table} AS tt
                    ON intersects(tt.geom,teilgebiete.geom)
                    WHERE tt.pk = {table}.pk AND
                           teilgebiete.tgnam in ('{tgnames}'))
                WHERE {table}.pk IN
                (	SELECT {table}.pk
                    FROM teilgebiete
                    INNER JOIN {table}
                    ON intersects({table}.geom,teilgebiete.geom)
                    WHERE teilgebiete.tgnam in ('{tgnames}'))
                """.format(table=table, tgnames=tgnames)
            else:
                fehlermeldung('Programmfehler', 'k_link.assigntgeb: auswahltyp hat unbekannten Fall {}'.format(str(auswahltyp)))
                del dbQK
                return False

            # logger.debug(u'\nSQL:\n{}\n'.format(sql))
            if not dbQK.sql(sql, u"QKan.k_link.assigntgeb (8)"):
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

    # Progress Bar
    bar = QProgressDialog()
    bar.setRange(0,0)
    bar.show()

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

        if dbQK.sql(sql, u"QKan_LinkFlaechen.reloadgroup (9) SQL-Fehler in SpatiaLite: \n"):
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

    if not dbQK.sql(sql, u"QKan_LinkFlaechen.savegroup (10) SQL-Fehler in SpatiaLite"):
        return False

    dbQK.commit()

    return True
