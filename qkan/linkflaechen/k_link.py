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

from qgis.PyQt.QtGui import QProgressBar

from qkan.database.qgis_utils import fehlermeldung, checknames
from qkan.linkflaechen.updatelinks import updatelinkfl, updatelinksw

logger = logging.getLogger(u'QKan')

progress_bar = None

# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Flächen

def createlinkfl(dbQK, liste_flaechen_abflussparam, liste_hal_entw,
                liste_teilgebiete, linksw_in_tezg=False, autokorrektur=True, suchradius=50, 
                mindestflaeche=0.5, fangradius=0.1, bezug_abstand=u'kante', 
                epsg=u'25832', dbtyp=u'SpatiaLite'):
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

    :mindestflaeche: Mindestflächengröße bei Einzelflächen und Teilflächenstücken
    :type mindestflaeche: Real
    
    :bezug_abstand: Bestimmt, ob in der SQL-Abfrage der Mittelpunkt oder die 
                    nächste Kante der Fläche berücksichtigt wird
    :type bezug_abstand: String

    :epsg: Nummer des Projektionssystems
    :type epsg: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void

    Die Bearbeitung erfolgt in einer zusätzlichen Tabelle 'linkfl'
    Sie wird zunächst aus der Tabelle "flaechen" erstellt, und enthält zusätzlich
    zwei weitere Geo-Attribute: 
     gbuf  - Buffer sind die mit einem Buffer erweiterten Flächen
     glink - linkfl sind Verbindungslinien, die von der Fläche zur Haltung zeigen
    zusätzlich wird die zugeordnete Haltung im entsprechenden Attribut verwaltet. 
    
    Änderungen an der Zuordnung erfolgen ausschließlich über die Bearbeitung des 
    Grafikobjektes, d.h. über die Verbindungslinie. Beim Export werden alle 
    Verknüpfungen über die Attributfelder (!) geprüft und alle Unstimmigkeiten, die 
    z. B. durch spätere Änderungen der Verbindungslinie entstanden sind, in den 
    Attributfeldern aktualisiert. Grund dafür ist, dass nur in dieser Reihenfolge 
    ein schneller Export möglich ist. Der "erste" Export kann dagegen viel mehr 
    Zeit benötigen, wenn bei vielen (allen?) Verbindungslinien die Attribute erst 
    eingetragen werden müssen. 
    
    Die Tabelle linkfl hat außer dem Primärschlüssel "pk" kein eindeutiges 
    Primärschlüsselfeld. 
    
    Das Feld tezg.flnam enthält immer den Namen der betreffenden Haltungsfläche, 
    unabhängig davon, ob es sich um eine aufzuteilende Fläche handelt.
    '''

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"", 
            u"Verknüpfungen zwischen Flächen und Haltungen werden hergestellt. Bitte warten...")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
    if not checknames(dbQK, u'flaechen', u'flnam', u'f_', autokorrektur):
        del dbQK
        return False

    progress_bar.setValue(5)

    # Aktualisierung des logischen Cache

    if not updatelinkfl(dbQK, deletelinkGeomNone = False):
        fehlermeldung(u'Fehler beim Update der Flächen-Verknüpfungen', 
                      u'Der logische Cache konnte nicht aktualisiert werden.')
        return False

    progress_bar.setValue(20)

    # Kopieren der Flaechenobjekte in die Tabelle linkfl

    lis_einf = ['']      # einfache Flächen. Erstes Element leer, damit beim join ' and ' schon am Anfang eingefügt wird
    lis_teil = ['']      # aufzuteilende Flächen. Erstes Element leer, damit beim join ' and ' schon am Anfang eingefügt wird

    if len(liste_flaechen_abflussparam) == 0:
        pass
        # logger.debug(u'Warnung in Link Flaechen: Keine Auswahl bei Flächen...')
    else:
        lis_einf.append(u"flaechen.abflussparameter in ('{}')".format(u"', '".join(liste_flaechen_abflussparam)))
        lis_teil = lis_einf[:]          # hier ist ein deepcopy notwendig!

    if len(liste_teilgebiete) != 0:
        lis_einf.append(u"flaechen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete)))
        lis_teil.append(u"tezg.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete)))

    ausw_einf = ' and '.join(lis_einf)
    ausw_teil = ' and '.join(lis_teil)

    # Sowohl Flächen, die nicht als auch die, die verschnitten werden müssen

    # SpatialIndex anlegen
    sqlindex = u"SELECT CreateSpatialIndex('tezg','geom')"

    if not dbQK.sql(sqlindex, u'CreateSpatialIndex in der Tabelle "tezg" auf "geom"'):
        return False

    # if not checkgeom(dbQK, 'tezg', 'geom', autokorrektur, liste_teilgebiete):
        # del dbQK
        # progress_bar.reset()
        # return False

    # if not checkgeom(dbQK, 'flaechen', 'geom', autokorrektur, liste_teilgebiete):
        # del dbQK
        # progress_bar.reset()
        # return False

    sql = u"""WITH linkadd AS (
                SELECT
                    linkfl.pk AS lpk, tezg.flnam AS tezgnam, flaechen.flnam, flaechen.aufteilen, flaechen.teilgebiet, 
                    flaechen.geom
                FROM flaechen
                INNER JOIN tezg
                ON within(centroid(flaechen.geom),tezg.geom)
                LEFT JOIN linkfl
                ON linkfl.flnam = flaechen.flnam
                WHERE ((flaechen.aufteilen <> 'ja' or flaechen.aufteilen IS NULL) 
                    and flaechen.geom IS NOT NULL and tezg.geom IS NOT NULL){ausw_einf}
                UNION
                SELECT
                    linkfl.pk AS lpk, tezg.flnam AS tezgnam, flaechen.flnam, flaechen.aufteilen, tezg.teilgebiet, 
                    CastToMultiPolygon(intersection(flaechen.geom,tezg.geom)) AS geom
                FROM flaechen
                INNER JOIN tezg
                ON intersects(flaechen.geom,tezg.geom)
                LEFT JOIN linkfl
                ON linkfl.flnam = flaechen.flnam AND linkfl.tezgnam = tezg.flnam
                WHERE (flaechen.aufteilen = 'ja'
                    and flaechen.geom IS NOT NULL and tezg.geom IS NOT NULL){ausw_teil})
            INSERT INTO linkfl (flnam, tezgnam, aufteilen, teilgebiet, geom)
            SELECT flnam, tezgnam, aufteilen, teilgebiet, geom
            FROM linkadd
            WHERE lpk IS NULL AND geom > {minfl}""".format(ausw_einf=ausw_einf, ausw_teil=ausw_teil, minfl=mindestflaeche)

    if not dbQK.sql(sql, u"QKan_LinkFlaechen (4a)"):
        del dbQK
        progress_bar.reset()
        return False

    progress_bar.setValue(60)

    # Jetzt werden die Flächenobjekte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.

    sql = u"""UPDATE linkfl SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linkfl.glink IS NULL""".format(
        suchradius)
    if not dbQK.sql(sql, u"createlinkfl (2)"):
        del dbQK
        progress_bar.reset()
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche. 
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen 
    # in tlink gefiltert wurden. 

    if len(liste_hal_entw) == 0:
        auswha = ''
    else:
        auswha = u" AND ha.entwart in ('{}')".format(u"', '".join(liste_hal_entw))

    if len(liste_teilgebiete) == 0:
        auswlinkfl = u""
    else:
        auswha += u" AND  ha.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        auswlinkfl = u" AND  linkfl.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))

    if bezug_abstand == 'mittelpunkt':
        bezug = u'lf.geom'
    else:
        bezug = u'PointonSurface(lf.geom)'

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # tlink enthält alle potenziellen Verbindungen zwischen Flächen und Haltungen mit der jeweiligen Entfernung
    # t2 enthält von diesen Verbindungen nur die Fläche (als pk) und den minimalen Abstand, 
    # so dass in der Abfrage nach "update" nur die jeweils nächste Verbindung gefiltert wird. 
    # Da diese Abfrage nur für neu zu erstellende Verknüpfungen gelten soll (also noch kein Eintrag
    # im Feld "flaechen.haltnam" -> fl.haltnam -> tlink.linkhal -> t1.linkhal). 

    # SpatialIndex anlegen
    sqlindex = u"SELECT CreateSpatialIndex('haltungen','geom')"

    if not dbQK.sql(sqlindex, u'CreateSpatialIndex in der Tabelle "tezg" auf "geom"'):
        del dbQK
        progress_bar.reset()
        return False

    # Varianten ohne und mit Beschränkung der Anbindungslinien auf die Haltungsfläche

    # Tipp: within und intersects schließt Datensätze ohne Geoobjekt ein. Deshalb müssen 
    # sie ausgeschlossen werden.
    

    if linksw_in_tezg:
        sql = u"""WITH tlink AS
            (	SELECT lf.pk AS pk,
                    ha.haltnam, 
                    Distance(ha.geom,{bezug}) AS dist, 
                    ha.geom AS geohal, lf.geom AS geolf
                FROM haltungen AS ha
                INNER JOIN linkfl AS lf
                ON Intersects(ha.geom,lf.gbuf)
                INNER JOIN tezg AS tg
                ON tg.flnam = lf.tezgnam
                WHERE (within(centroid(ha.geom),tg.geom) and lf.glink IS NULL 
                    and ha.geom IS NOT NULL and lf.gbuf IS NOT NULL and tg.geom IS NOT NULL){auswha})
            UPDATE linkfl SET (glink, haltnam) = 
            (   SELECT MakeLine(PointOnSurface(Buffer(t1.geolf, -1.1*{fangradius})),Centroid(t1.geohal)), t1.haltnam
                FROM tlink AS t1
                INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
                ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
                WHERE linkfl.pk = t1.pk AND area(Buffer(t1.geolf, -1.1*{fangradius})) IS NOT NULL)
            WHERE linkfl.glink IS NULL{auswlinkfl}""".format(bezug=bezug, fangradius=fangradius, 
                auswha=auswha, auswlinkfl=auswlinkfl)
    else:
        sql = u"""WITH tlink AS
            (	SELECT lf.pk AS pk,
                    ha.haltnam, 
                    Distance(ha.geom,{bezug}) AS dist, 
                    ha.geom AS geohal, lf.geom AS geolf
                FROM haltungen AS ha
                INNER JOIN linkfl AS lf
                ON Intersects(ha.geom,lf.gbuf)
                WHERE lf.glink IS NULL
                    and ha.geom IS NOT NULL and lf.gbuf IS NOT NULL{auswha})
            UPDATE linkfl SET (glink, haltnam) =  
            (   SELECT MakeLine(PointOnSurface(Buffer(t1.geolf, -1.1*{fangradius})),Centroid(t1.geohal)), t1.haltnam
                FROM tlink AS t1
                INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
                ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
                WHERE linkfl.pk = t1.pk AND area(Buffer(t1.geolf, -1.1*{fangradius})) IS NOT NULL)
            WHERE linkfl.glink IS NULL{auswlinkfl}""".format(bezug=bezug, fangradius=fangradius, 
                auswha=auswha, auswlinkfl=auswlinkfl)


    logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"createlinkfl (5)"):
        del dbQK
        progress_bar.reset()
        return False

    progress_bar.setValue(80)

    # Löschen der Datensätze in linkfl, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linkfl WHERE glink IS NULL"""

    if not dbQK.sql(sql, u"QKan_LinkFlaechen (7)"):
        del dbQK
        progress_bar.reset()
        return False

    dbQK.commit()

    # Aktualisierung des logischen Cache

    if not updatelinkfl(dbQK, deletelinkGeomNone = False):
        fehlermeldung(u'Fehler beim Update der Flächen-Verknüpfungen', 
                      u'Der logische Cache konnte nicht aktualisiert werden.')
        del dbQK
        progress_bar.reset()
        return False
        
    progress_bar.setValue(100)
    status_message.setText(u"Fertig!")
    status_message.setLevel(QgsMessageBar.SUCCESS)

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True


# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Direkteinleitungen

def createlinksw(dbQK, liste_teilgebiete, suchradius=50, epsg=u'25832',
                 dbtyp=u'SpatiaLite'):
    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :liste_teilgebiete: Liste der ausgewählten Teilgebiete
    :type liste_teilgebiete: list of String

    :suchradius: Suchradius in der SQL-Abfrage
    :type suchradius: Real

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

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"", 
            u"Verknüpfungen zwischen Einleitpunkten und Haltungen werden hergestellt. Bitte warten...")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    # Aktualisierung des logischen Cache

    if not updatelinksw(dbQK, deletelinkGeomNone = False):
        fehlermeldung(u'Fehler beim Update der Einzeleinleiter-Verknüpfungen', 
                      u'Der logische Cache konnte nicht aktualisiert werden.')
        return False

    if len(liste_teilgebiete) != 0:
        auswahl = u" AND einleit.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
    else:
        auswahl = ''

    sql = u"""INSERT INTO linksw (elnam, teilgebiet, geom)
            SELECT einleit.elnam, einleit.teilgebiet,buffer(einleit.geom,{radius})
            FROM einleit
            LEFT JOIN linksw
            ON linksw.elnam = einleit.elnam
            WHERE linksw.pk IS NULL{auswahl}""".format(auswahl=auswahl, radius = 0.5)

    # logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan_LinkSW (4a)"):
        return False

    progress_bar.setValue(25)

    # Jetzt werden die Direkteinleitungen-Punkte mit einem Buffer erweitert und jeweils neu 
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = u"""UPDATE linksw SET gbuf = CastToMultiPolygon(buffer(geom,{})) WHERE linksw.glink IS NULL""".format(
        suchradius)

    if not dbQK.sql(sql, u"QKan_LinkSW (2)"):
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche. 
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen 
    # in tlink gefiltert wurden. 


    if len(liste_teilgebiete) != 0:
        auswahl = u" AND  hal.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        auswlin = u" AND  linksw.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
    else:
        auswahl = ''

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # tlink enthält alle potenziellen Verbindungen zwischen Flächen und Haltungen mit der jeweiligen Entfernung
    # t2 enthält von diesen Verbindungen nur die Fläche (als pk) und den minimalen Abstand, 
    # so dass in der Abfrage nach "update" nur die jeweils nächste Verbindung gefiltert wird. 
    # Da diese Abfrage nur für neu zu erstellende Verknüpfungen gelten soll (also noch kein Eintrag
    # im Feld "einleit.haltnam" -> sw.haltnam -> tlink.linkhal -> t1.linkhal). 

    # SpatialIndex anlegen
    sqlindex = u"SELECT CreateSpatialIndex('haltungen','geom')"

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
                    search_frame = sw.gbuf)
                    and hal.geom IS NOT NULL and sw.gbuf IS NOT NULL{auswahl})
            UPDATE linksw SET glink =  
            (SELECT MakeLine(PointOnSurface(t1.geosw),Centroid(t1.geohal))
            FROM tlink AS t1
            INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
            WHERE linksw.pk = t1.pk)
            WHERE linksw.glink IS NULL{auswlin}""".format(auswahl=auswahl, auswlin=auswlin)

    # logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    if not dbQK.sql(sql, u"QKan_LinkSW (5)"):
        return False

    progress_bar.setValue(50)

    # Löschen der Datensätze in linksw, bei denen keine Verbindung erstellt wurde, weil die 
    # nächste Haltung zu weit entfernt ist.

    sql = u"""DELETE FROM linksw WHERE glink IS NULL"""

    if not dbQK.sql(sql, u"QKan_LinkSW (7)"):
        return False

    # Aktualisierung des logischen Cache

    if not updatelinksw(dbQK, deletelinkGeomNone = False):
        fehlermeldung(u'Fehler beim Update der Einzeleinleiter-Verknüpfungen', 
                      u'Der logische Cache konnte nicht aktualisiert werden.')
        return False

    progress_bar.setValue(100)
    status_message.setText(u"Fertig!")
    status_message.setLevel(QgsMessageBar.SUCCESS)

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage(u"Information", u"Verknüpfungen sind erstellt!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nVerknüpfungen sind erstellt!", level=QgsMessageLog.INFO)

    return True



# -------------------------------------------------------------------------------------------------------------

def assigntgeb(dbQK, auswahltyp, liste_teilgebiete, tablist, autokorrektur, bufferradius=u'0', dbtyp=u'SpatiaLite'):
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

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"", 
            u"Teilgebiete werden zugeordnet. Bitte warten...")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    logger.debug(u'\nbetroffene Tabellen (1):\n{}\n'.format(str(tablist)))
    logger.debug(u'\nbetroffene Teilgebiete (2):\n{}\n'.format(str(liste_teilgebiete)))

    if not checknames(dbQK, u'teilgebiete', u'tgnam', u'tg_', autokorrektur):
        return False

    if len(liste_teilgebiete) != 0:
        tgnames = u"', '".join(liste_teilgebiete)
        auswahl_1 = u" AND teilgebiete.tgnam in ('{tgnames}')".format(tgnames=tgnames)
        auswahl_2 = u" WHERE teilgebiete.tgnam in ('{tgnames}')".format(tgnames=tgnames)
    else:
        auswahl_1 = ''
        auswahl_2 = ''

    for table in tablist:

        if auswahltyp == 'within':
            if bufferradius == '0' or bufferradius.strip == '':
                sql = u"""
                UPDATE {table} SET teilgebiet = 
                (	SELECT teilgebiete.tgnam
                    FROM teilgebiete
                    INNER JOIN {table} AS tt
                    ON within(tt.geom, teilgebiete.geom)
                    WHERE tt.pk = {table}.pk
                        and tt.geom IS NOT NULL and teilgebiete.geom IS NOT NULL {auswahl_1})
                WHERE {table}.pk IN
                (	SELECT {table}.pk
                    FROM teilgebiete
                    INNER JOIN {table}
                    ON within({table}.geom, teilgebiete.geom)
                    WHERE {table}.geom IS NOT NULL and teilgebiete.geom IS NOT NULL {auswahl_1})
                """.format(table=table, bufferradius=bufferradius, auswahl_1=auswahl_1)
            else:
                sql = u"""
                UPDATE {table} SET teilgebiet = 
                (	SELECT teilgebiete.tgnam
                    FROM teilgebiete
                    INNER JOIN {table} AS tt
                    ON within(tt.geom, buffer(teilgebiete.geom, {bufferradius}))
                    WHERE tt.pk = {table}.pk
                        and tt.geom IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
                WHERE {table}.pk IN
                (	SELECT {table}.pk
                    FROM teilgebiete
                    INNER JOIN {table}
                    ON within({table}.geom, buffer(teilgebiete.geom, {bufferradius}))
                    WHERE {table}.geom IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
                """.format(table=table, bufferradius=bufferradius, auswahl_1=auswahl_1)
        elif auswahltyp == 'overlaps':
            sql = u"""
            UPDATE {table} SET teilgebiet = 
            (	SELECT teilgebiete.tgnam
                FROM teilgebiete
                INNER JOIN {table} AS tt
                ON intersects(tt.geom,teilgebiete.geom)
                WHERE tt.pk = {table}.pk
                    and tt.geom IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
            WHERE {table}.pk IN
            (	SELECT {table}.pk
                FROM teilgebiete
                INNER JOIN {table}
                ON intersects({table}.geom,teilgebiete.geom)
                WHERE {table}.geom IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
            """.format(table=table, auswahl_1=auswahl_1)
        else:
            fehlermeldung(u'Programmfehler', u'k_link.assigntgeb: auswahltyp hat unbekannten Fall {}'.format(str(auswahltyp)))
            del dbQK
            return False

        # logger.debug(u'\nSQL:\n{}\n'.format(sql))
        if not dbQK.sql(sql, u"QKan.k_link.assigntgeb (8)"):
            return False

        dbQK.commit()

    progress_bar.setValue(100)
    status_message.setText(u"Fertig!")
    status_message.setLevel(QgsMessageBar.SUCCESS)

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage(u"Information", u"Zuordnung von Haltungen und Flächen ist fertig!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nZuordnung von Haltungen und Flächen ist fertig!", level=QgsMessageLog.INFO)

    return True


# -------------------------------------------------------------------------------------------------------------

def reloadgroup(dbQK, gruppenname, dbtyp = u'SpatiaLite'):
    '''Lädt die unter einem Gruppennamen gespeicherten Teilgebietszuordnungen zurück in die Tabellen 
       "haltungen", "schaechte", "flaechen", "tezg", "linkfl", "linksw", "einleit"

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :gruppenname: Bezeichnung der Gruppe, unter der die Teilgebietszuordnungen abgelegt wurden.
    :type gruppenname: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"", 
            u"Teilgebiete werden aus der gewählten Gruppe wiederhergestellt. Bitte warten...")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    tablist = [u"haltungen", u"schaechte", u"flaechen", u"linkfl", u"linksw", u"tezg", u"einleit"]

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

        if not dbQK.sql(sql, u"QKan_LinkFlaechen.reloadgroup (9): \n"):
            return False

    dbQK.commit()

    progress_bar.setValue(100)
    status_message.setText(u"Fertig!")
    status_message.setLevel(QgsMessageBar.SUCCESS)

    return True



# -------------------------------------------------------------------------------------------------------------

def storegroup(dbQK, gruppenname, kommentar, dbtyp = u'SpatiaLite'):
    '''Speichert die aktuellen Teilgebietszuordnungen der Tabellen 
       "haltungen", "schaechte", "flaechen", "tezg", "linkfl", "linksw", "einleit"
       unter einem neuen Gruppennamen

    :dbQK: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :gruppenname: Bezeichnung der Gruppe, unter der die Teilgebietszuordnungen abgelegt werden.
    :type gruppenname: String

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"", 
            u"Teilgebiete werden in der angegebenen Gruppe gespeichert. Bitte warten...")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    tablist = [u"haltungen", u"schaechte", u"flaechen", u"linkfl", u"linksw", u"tezg", u"einleit"]

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

    if not dbQK.sql(sql, u"QKan_LinkFlaechen.savegroup (10)"):
        return False

    dbQK.commit()

    progress_bar.setValue(100)
    status_message.setText(u"Fertig!")
    status_message.setLevel(QgsMessageBar.SUCCESS)

    return True
