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

# import tempfile
import glob
import logging
import os
import shutil
import xml.etree.ElementTree as ET

from PyQt4.QtCore import QFileInfo
from qgis.core import QgsMessageLog, QgsProject, QgsCoordinateReferenceSystem
from qgis.gui import QgsMessageBar
from qgis.utils import iface, pluginDirectory

from qkan.database.dbfunc import DBConnection
from qkan.database.fbfunc import FBConnection

from qkan.database.qkan_utils import fortschritt, fehlermeldung

logger = logging.getLogger(u'QKan')


# ------------------------------------------------------------------------------
# Hauptprogramm

def importKanaldaten(database_HE, database_QKan, projectfile, epsg, check_tabinit,
                     dbtyp=u'SpatiaLite'):
    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :database_HE:   Datenbankobjekt, das die Verknüpfung zur HE-Firebird-Datenbank verwaltet
    :type database: DBConnection (geerbt von firebirdsql...)

    :database_QKan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database: DBConnection (geerbt von dbapi...)

    :dbtyp:         Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:    String
    
    :returns: void
    '''

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbHE = FBConnection(database_HE)  # Datenbankobjekt der HE-Datenbank zum Lesen

    if dbHE is None:
        fehlermeldung(u"Fehler in QKan_Import_from_HE",
                      u'ITWH-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_HE))
        return None

    dbQK = DBConnection(dbname=database_QKan, epsg=epsg)  # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        fehlermeldung(u"Fehler in QKan_Import_from_HE",
                      u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        return None

    # Referenztabellen laden. 

    # Entwässerungssystem. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
    sql = u'SELECT he_nr, bezeichnung FROM entwaesserungsarten'
    if not dbQK.sql(sql, u'importkanaldaten_he (1)'):
        return None
    daten = dbQK.fetchall()
    ref_entwart = {}
    for el in daten:
        ref_entwart[el[0]] = el[1]

    # Pumpentypen. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
    sql = u'SELECT he_nr, bezeichnung FROM pumpentypen'
    if not dbQK.sql(sql, u'importkanaldaten_he (2)'):
        return None
    daten = dbQK.fetchall()
    ref_pumpentyp = {}
    for el in daten:
        ref_pumpentyp[el[0]] = el[1]

    # Profile. Attribut [profilnam] enthält die Bezeichnung des Benutzers. Dies kann auch ein Kürzel sein.
    sql = u'SELECT he_nr, profilnam FROM profile'
    if not dbQK.sql(sql, u'importkanaldaten_he (3)'):
        return None
    daten = dbQK.fetchall()
    ref_profil = {}
    for el in daten:
        ref_profil[el[0]] = el[1]

    # Auslasstypen.
    sql = u'SELECT he_nr, bezeichnung FROM auslasstypen'
    if not dbQK.sql(sql, u'importkanaldaten_he (4)'):
        return None
    daten = dbQK.fetchall()
    ref_auslasstypen = {}
    for el in daten:
        ref_auslasstypen[el[0]] = el[1]

    # Simulationsstatus
    sql = u'SELECT he_nr, bezeichnung FROM simulationsstatus'
    if not dbQK.sql(sql, u'importkanaldaten_he (5)'):
        return None
    daten = dbQK.fetchall()
    ref_simulationsstatus = {}
    for el in daten:
        ref_simulationsstatus[el[0]] = el[1]

    # ------------------------------------------------------------------------------
    # Daten aus den Referenztabellen der HE-Datenbank übernehmen

    #    todo...


    # ------------------------------------------------------------------------------
    # Haltungsdaten
    # Feld [abflussart] entspricht dem Eingabefeld "System", das in einem Nachschlagefeld die 
    # Werte 'Freispiegel', 'Druckabfluss', 'Abfluss im offenen Profil' anbietet

    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM haltungen'
        if not dbQK.sql(sql, u'importkanaldaten_he (6)'):
            return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
    SELECT 
        ROHR.NAME AS haltnam, 
        ROHR.SCHACHTOBEN AS schoben, 
        ROHR.SCHACHTUNTEN AS schunten, 
        ROHR.GEOMETRIE1 AS hoehe, 
        ROHR.GEOMETRIE2 AS breite, 
        ROHR.LAENGE AS laenge, 
        ROHR.SOHLHOEHEOBEN AS sohleoben, 
        ROHR.SOHLHOEHEUNTEN AS sohleunten, 
        SO.DECKELHOEHE AS deckeloben, 
        SU.DECKELHOEHE AS deckelunten, 
        ROHR.TEILEINZUGSGEBIET AS teilgebiet, 
        ROHR.PROFILTYP AS profiltyp_he, 
        ROHR.SONDERPROFILBEZEICHNUNG AS profilnam, 
        ROHR.KANALART AS entwaesserungsart_he, 
        ROHR.RAUIGKEITSBEIWERT AS ks, 
        ROHR.PLANUNGSSTATUS AS simstat_he, 
        ROHR.KOMMENTAR AS kommentar, 
        ROHR.LASTMODIFIED AS createdat, 
        SO.XKOORDINATE AS xob, 
        SO.YKOORDINATE AS yob, 
        SU.XKOORDINATE AS xun, 
        SU.YKOORDINATE AS yun
    FROM ROHR 
    INNER JOIN (SELECT NAME, DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SCHACHT
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SPEICHERSCHACHT) AS SO ON ROHR.SCHACHTOBEN = SO.NAME 
    INNER JOIN (SELECT NAME, DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SCHACHT
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM AUSLASS
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SPEICHERSCHACHT) AS SU
    ON ROHR.SCHACHTUNTEN = SU.NAME'''
    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Haltungsdaten in die QKan-DB schreiben

    for attr in daten:
        (haltnam_ansi, schoben_ansi, schunten_ansi, hoehe, breite, laenge, sohleoben, sohleunten,
         deckeloben, deckelunten, teilgebiet, profiltyp_he, profilnam_ansi,
         entwaesserungsart_he, ks, simstat_he, kommentar_ansi, createdat, xob, yob, xun, yun) = \
            ['NULL' if el is None else el for el in attr]

        (haltnam, schoben, schunten, profilnam, kommentar) = \
            [tt.decode('iso-8859-1') for tt in (haltnam_ansi, schoben_ansi, schunten_ansi,
                                                profilnam_ansi, kommentar_ansi)]

        # Anwendung der Referenzlisten HE -> QKan

        # Rohrprofile. In HE werden primär Profilnummern verwendet. Bei Sonderprofilen ist die Profilnummer = 68
        # und zur eindeutigen Identifikation dient stattdessen der Profilname. 
        # In QKan wird ausschließlich der Profilname verwendet, so dass sichergestellt sein muss, dass die
        # Standardbezeichnungen für die HE-Profile nicht auch als Namen für ein Sonderprofil verwendet werden. 

        if profiltyp_he in ref_profil:
            profilnam = ref_profil[profiltyp_he]
        else:
            # Noch nicht in Tabelle [profile] enthalten, also ergqenzen
            if profilnam == u'NULL':
                # In HE ist nur die Profilnummer enthalten. Dann muss ein Profilname erzeugt werden, z.B. (12)
                profilnam = u'({profiltyp_he})'.format(profiltyp_he=profiltyp_he)

            # In Referenztabelle in dieser Funktion sowie in der QKan-Tabelle profile einfügen
            ref_profil[profiltyp_he] = profilnam
            sql = u"INSERT INTO profile (profilnam, he_nr) Values ('{profilnam}', {profiltyp_he})".format( \
                profilnam=profilnam, profiltyp_he=profiltyp_he)
            if not dbQK.sql(sql, u'importkanaldaten_he (7)'):
                return None

        # Entwasserungsarten. Hier ist es einfacher als bei den Profilen...
        if entwaesserungsart_he in ref_entwart:
            entwart = ref_entwart[entwaesserungsart_he]
        else:
            # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergqenzen
            entwart = u'({})'.format(entwaesserungsart_he)
            sql = u"INSERT INTO entwaesserungsarten (bezeichnung, he_nr) Values ('{entwart}', {he_nr})".format( \
                entwart=entwart, he_nr=entwaesserungsart_he)
            ref_entwart[entwaesserungsart_he] = entwart
            if not dbQK.sql(sql, u'importkanaldaten_he (8)'):
                return None

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            if not dbQK.sql(sql, u'importkanaldaten_he (9)'):
                return None

        # Geo-Objekt erzeugen

        if dbtyp == u'SpatiaLite':
            geom = u'MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:}))'.format(xob, yob, xun, yun, epsg)
        elif dbtyp == u'postgis':
            geom = u'ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:}),{4:s}),ST_SetSRID(ST_MakePoint({2:},{3:}),{4:}))'.format(
                xob, yob, xun, yun, epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz aufbereiten in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO haltungen 
                (geom, haltnam, schoben, schunten, 
                hoehe, breite, laenge, sohleoben, sohleunten, 
                deckeloben, deckelunten, teilgebiet, profilnam, entwart, ks, simstatus, kommentar, createdat) VALUES (
                {geom}, '{haltnam}', '{schoben}', '{schunten}', {hoehe}, {breite}, {laenge}, 
                {sohleoben}, {sohleunten}, {deckeloben}, {deckelunten}, '{teilgebiet}', '{profilnam}', 
                '{entwart}', {ks}, '{simstatus}', '{kommentar}', '{createdat}')""".format( \
                geom=geom, haltnam=haltnam, schoben=schoben, schunten=schunten, hoehe=hoehe,
                breite=breite, laenge=laenge, sohleoben=sohleoben, sohleunten=sohleunten,
                deckeloben=deckeloben, deckelunten=deckelunten, teilgebiet=teilgebiet,
                profilnam=profilnam, entwart=entwart, ks=ks, simstatus=simstatus, kommentar=kommentar,
                createdat=createdat)
        except BaseException as err:
            fehlermeldung(u'SQL-Fehler', repr(err))
            fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql INSERT INTO haltungen: \n" + \
                          str((geom, haltnam, schoben, schunten,
                               hoehe, breite, laenge, sohleoben, sohleunten,
                               deckeloben, deckelunten, teilgebiet, profilnam, entwart, ks, simstatus)) + u'\n\n')

        if not dbQK.sql(sql, u'importkanaldaten_he (10)'):
            return None

    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Schachtdaten
    # Das Feld [KANALART] enthält das Entwasserungssystem (Schmutz-, Regen- oder Mischwasser)
    # Das Feld [ART] enthält die Information, ob es sich um einen Startknoten oder einen Inneren Knoten handelt.
    # oder: um was für eine #Verzweigung es sich handelt (Wunsch von Herrn Wippermann)...???


    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM schaechte'
        if not dbQK.sql(sql, u'importkanaldaten_he (11)'):
            return None

    # Daten aus ITWH-Datenbank abfragen
    sql = u'''
    SELECT 
        NAME AS schnam,
        XKOORDINATE AS xsch, 
        YKOORDINATE AS ysch, 
        SOHLHOEHE AS sohlhoehe, 
        DECKELHOEHE AS deckelhoehe, 
        DURCHMESSER AS durchm, 
        DRUCKDICHTERDECKEL AS druckdicht, 
        KANALART AS entwaesserungsart_he, 
        PLANUNGSSTATUS AS simstat_he, 
        KOMMENTAR AS kommentar, 
        LASTMODIFIED AS createdat
        FROM SCHACHT'''

    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Schachtdaten aufbereiten und in die QKan-DB schreiben

    for attr in daten:
        (schnam_ansi, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwaesserungsart_he,
         simstat_he, kommentar_ansi, createdat) = ['NULL' if el is None else el for el in attr]

        (schnam, kommentar) = [tt.decode('iso-8859-1') for tt in (schnam_ansi, kommentar_ansi)]

        # Entwasserungsarten
        if entwaesserungsart_he in ref_entwart:
            entwart = ref_entwart[entwaesserungsart_he]
        else:
            # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergänzen
            sql = u"INSERT INTO entwaesserungsarten (bezeichnung, he_nr) Values ('({0:})', {0:d})".format(
                entwaesserungsart_he)
            entwart = u'({:})'.format(entwaesserungsart_he)
            if not dbQK.sql(sql, u'importkanaldaten_he (12)'):
                return None

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            if not dbQK.sql(sql, u'importkanaldaten_he (13)'):
                return None

        # Geo-Objekte erzeugen

        if dbtyp == u'SpatiaLite':
            geop = u'MakePoint({0:},{1:},{2:})'.format(xsch, ysch, epsg)
            geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch, 
                                             (1. if durchm == 'NULL' else durchm/ 1000.) , epsg)
        elif dbtyp == u'postgis':
            geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch, ysch, epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                                        schachttyp, simstatus, kommentar, createdat, geop, geom)
            VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, {durchm}, {druckdicht}, '{entwart}', 
                     '{schachttyp}', '{simstatus}', '{kommentar}', '{createdat}', 
                     {geop}, {geom})""".format( \
                schnam=schnam, xsch=xsch, ysch=ysch, sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe,
                durchm=durchm, druckdicht=druckdicht, entwart=entwart,
                schachttyp=u'Schacht', simstatus=simstatus,
                kommentar=kommentar, createdat=createdat, geop=geop, geom=geom)
            if not dbQK.sql(sql, u'importkanaldaten_he (14)'):
                return None
        except BaseException as err:
            fehlermeldung(u'SQL-Fehler', repr(err))
            fehlermeldung(u"Fehler in QKan_Import_from_HE (14)", u"\nSchächte: in sql: \n" + sql + u'\n\n')

    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Speicherschachtdaten


    # Tabelle in QKan-Datenbank leeren
    # if check_tabinit:
        # sql = u'DELETE FROM speicherschaechte'
        # if not dbQK.sql(sql, u'importkanaldaten_he (15)'):
            # return None

    # Daten aus ITWH-Datenbank abfragen
    sql = u'''
    SELECT NAME AS schnam, 
        GELAENDEHOEHE AS deckelhoehe, 
        SOHLHOEHE AS sohlhoehe, 
        XKOORDINATE AS xsch, 
        YKOORDINATE AS ysch, 
        UEBERSTAUFLAECHE AS ueberstauflaeche, 
        PLANUNGSSTATUS AS simstat_he, 
        KOMMENTAR AS kommentar, 
        LASTMODIFIED AS createdat 
        FROM SPEICHERSCHACHT'''

    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Speicherschachtdaten aufbereiten und in die QKan-DB schreiben

    logger.debug(u'simstatus[0]: {}'.format(ref_simulationsstatus[0]))
    for attr in daten:
        (schnam_ansi, deckelhoehe, sohlhoehe, xsch, ysch, ueberstauflaeche, simstat_he, kommentar_ansi,
         createdat) = ['NULL' if el is None else el for el in attr]

        (schnam, kommentar) = [tt.decode('iso-8859-1') for tt in (schnam_ansi, kommentar_ansi)]

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            if not dbQK.sql(sql, u'importkanaldaten_he (16)'):
                return None

        # Geo-Objekte erzeugen

        if dbtyp == u'SpatiaLite':
            geop = u'MakePoint({0:},{1:},{2:})'.format(xsch, ysch, epsg)
            geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch, 
                                             (1. if durchm == 'NULL' else durchm/ 1000.) , epsg)
        elif dbtyp == u'postgis':
            geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch, ysch, epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        sql = u"""INSERT INTO schaechte (schnam, deckelhoehe, sohlhoehe, xsch, ysch, ueberstauflaeche, 
                    schachttyp, simstatus, kommentar, createdat, geop, geom)
            VALUES ('{schnam}', {deckelhoehe}, {sohlhoehe}, {xsch}, {ysch}, {ueberstauflaeche}, 
                    '{schachttyp}', '{simstatus}', '{kommentar}', '{createdat}', 
                    {geop}, {geom})""".format( \
            schnam=schnam, deckelhoehe=deckelhoehe, sohlhoehe=sohlhoehe,
            xsch=xsch, ysch=ysch, ueberstauflaeche=ueberstauflaeche,
            schachttyp=u'Speicher', simstatus=simstatus, kommentar=kommentar,
            createdat=createdat, geop=geop, geom=geom)

        if not dbQK.sql(sql, u'importkanaldaten_he (17)'):
            return None

    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Auslässe
    # Das Feld [TYP] enthält den Auslasstyp (0=Frei, 1=Normal, 2= Konstant, 3=Tide, 4=Zeitreihe)


    # Tabelle in QKan-Datenbank leeren
    # if check_tabinit:
        # sql = u'DELETE FROM auslaesse'
        # if not dbQK.sql(sql, u'importkanaldaten_he (18)'):
            # return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
    SELECT NAME AS schnam, 
        XKOORDINATE AS xsch, 
        YKOORDINATE AS ysch, 
        SOHLHOEHE AS sohlhoehe, 
        GELAENDEHOEHE AS deckelhoehe, 
        TYP AS typ_he, 
        PLANUNGSSTATUS AS simstat_he, 
        KOMMENTAR AS kommentar, 
        LASTMODIFIED AS createdat 
        FROM AUSLASS'''

    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Daten aufbereiten und in die QKan-DB schreiben

    for attr in daten:
        (schnam_ansi, xsch, ysch, sohlhoehe, deckelhoehe, typ_he, simstat_he, kommentar_ansi, createdat) = \
            ['NULL' if el is None else el for el in attr]

        (schnam, kommentar) = [tt.decode('iso-8859-1') for tt in (schnam_ansi, kommentar_ansi)]

        # Auslasstyp-Nr aus HE ersetzten
        if typ_he in ref_auslasstypen:
            auslasstyp = ref_auslasstypen[typ_he]
        else:
            # Noch nicht in Tabelle [auslasstypen] enthalten, also ergqenzen
            auslasstyp = u'({}_he)'.format(typ_he)
            sql = u"INSERT INTO auslasstypen (bezeichnung, he_nr) Values ('{auslasstyp}', {he_nr})".format( \
                auslasstyp=auslasstyp, he_nr=typ_he)
            ref_auslasstypen[typ_he] = auslasstyp
            if not dbQK.sql(sql, u'importkanaldaten_he (19)'):
                return None

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            if not dbQK.sql(sql, u'importkanaldaten_he (20)'):
                return None

        # Geo-Objekte erzeugen

        if dbtyp == u'SpatiaLite':
            geop = u'MakePoint({0:},{1:},{2:})'.format(xsch, ysch, epsg)
            geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch, 1., epsg)
        elif dbtyp == u'postgis':
            geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch, ysch, epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, 
                    auslasstyp, schachttyp, simstatus, kommentar, createdat, geop, geom)
            VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, '{auslasstyp}', 
                    '{schachttyp}', '{simstatus}', '{kommentar}', 
                    '{createdat}', {geop}, {geom})""".format(schnam=schnam, xsch=xsch, ysch=ysch,
                                                             sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe,
                                                             auslasstyp=auslasstyp,
                                                             schachttyp=u'Auslass', simstatus=simstatus,
                                                             kommentar=kommentar, createdat=createdat, geop=geop,
                                                             geom=geom)
        if not dbQK.sql(sql, u'importkanaldaten_he (21)'):
            return None

    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Pumpen

    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM pumpen'
        if not dbQK.sql(sql, u'importkanaldaten_he (22)'):
            return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
    SELECT 
        PUMPE.NAME AS pnam, 
        PUMPE.SCHACHTOBEN AS schoben, 
        PUMPE.SCHACHTUNTEN AS schunten, 
        PUMPE.TYP AS typ_he, 
        PUMPE.STEUERSCHACHT AS steuersch, 
        PUMPE.EINSCHALTHOEHE AS einschalthoehe, 
        PUMPE.AUSSCHALTHOEHE AS ausschalthoehe,
        SO.XKOORDINATE AS xob, 
        SO.YKOORDINATE AS yob, 
        SU.XKOORDINATE AS xun, 
        SU.YKOORDINATE AS yun, 
        PUMPE.PLANUNGSSTATUS AS simstat_he, 
        PUMPE.KOMMENTAR AS kommentar, 
        PUMPE.LASTMODIFIED AS createdat
    FROM PUMPE
    LEFT JOIN (SELECT NAME, DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SCHACHT
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SPEICHERSCHACHT) AS SO ON PUMPE.SCHACHTOBEN = SO.NAME 
    LEFT JOIN (SELECT NAME, DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SCHACHT
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM AUSLASS
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SPEICHERSCHACHT) AS SU
    ON PUMPE.SCHACHTUNTEN = SU.NAME'''
    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Pumpendaten in die QKan-DB schreiben

    for attr in daten:
        (pnam_ansi, schoben_ansi, schunten_ansi, typ_he, steuersch, einschalthoehe, ausschalthoehe,
         xob, yob, xun, yun, simstat_he, kommentar_ansi, createdat) = ['NULL' if el is None else el for el in attr]

        (pnam, schoben, schunten, kommentar) = [tt.decode('iso-8859-1') for tt in (pnam_ansi, schoben_ansi,
                                                                                   schunten_ansi, kommentar_ansi)]

        # Pumpentyp-Nr aus HE ersetzten
        if typ_he in ref_pumpentyp:
            pumpentyp = ref_pumpentyp[typ_he]
        else:
            # Noch nicht in Tabelle [pumpentypen] enthalten, also ergqenzen
            pumpentyp = u'({}_he)'.format(typ_he)
            sql = u"INSERT INTO pumpentypen (bezeichnung, he_nr) Values ('{pumpentyp}', {he_nr})".format( \
                pumpentyp=pumpentyp, he_nr=typ_he)
            ref_pumpentyp[typ_he] = pumpentyp
            if not dbQK.sql(sql, u'importkanaldaten_he (23)'):
                return None

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            if not dbQK.sql(sql, u'importkanaldaten_he (24)'):
                return None

        # Geo-Objekt erzeugen

        if xun == u'NULL' or yun == u'NULL':
            # Es gibt keinen Schacht unten. Dann wird die Pumpe grafisch nach rechs oben
            # erzeugt
            xun = u'{:.3f}'.format(float(xob) + 10.)
            yun = u'{:.3f}'.format(float(yob) + 10.)

        if dbtyp == u'SpatiaLite':
            geom = u'MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:}))'.format(xob, yob, xun, yun, epsg)
        elif dbtyp == u'postgis':
            geom = u'''ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:}),{4:}),
                      ST_SetSRID(ST_MakePoint({2:},{3:}),{4:}))'''.format(xob, yob, xun, yun, epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz aufbereiten und in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO pumpen 
                (pnam, schoben, schunten, pumpentyp, steuersch, einschalthoehe, ausschalthoehe, 
                simstatus, kommentar, createdat, geom) 
                VALUES ('{pnam}', '{schoben}', '{schunten}', '{pumpentyp}', '{steuersch}', 
                {einschalthoehe}, {ausschalthoehe}, '{simstatus}', '{kommentar}', '{createdat}', {geom})""".format( \
                pnam=pnam, schoben=schoben, schunten=schunten, pumpentyp=pumpentyp, steuersch=steuersch,
                einschalthoehe=einschalthoehe, ausschalthoehe=ausschalthoehe, simstatus=simstatus,
                kommentar=kommentar, createdat=createdat, geom=geom)

        except BaseException as err:
            fehlermeldung(u'SQL-Fehler', repr(err))
            fehlermeldung(u"Fehler in QKan_Import_from_HE",
                          u"\nFehler in sql INSERT INTO pumpen: \n" + str((pnam, schoben, \
                                                                           schunten, pumpentyp, steuersch,
                                                                           einschalthoehe, ausschalthoehe,
                                                                           geom)) + u'\n\n')

        if not dbQK.sql(sql, u'importkanaldaten_he (25)'):
            return None
    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Wehre

    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM wehre'
        if not dbQK.sql(sql, u'importkanaldaten_he (26)'):
            return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
    SELECT 
        WEHR.NAME AS wnam,
        WEHR.SCHACHTOBEN AS schoben, 
        WEHR.SCHACHTUNTEN AS schunten, 
        WEHR.TYP AS typ_he, 
        WEHR.SCHWELLENHOEHE AS schwellenhoehe, 
        WEHR.GEOMETRIE1 AS kammerhoehe, 
        WEHR.GEOMETRIE2 AS laenge,
        WEHR.UEBERFALLBEIWERT AS uebeiwert,
        SO.XKOORDINATE AS xob, 
        SO.YKOORDINATE AS yob, 
        SU.XKOORDINATE AS xun, 
        SU.YKOORDINATE AS yun, 
        WEHR.PLANUNGSSTATUS AS simstat_he, 
        WEHR.KOMMENTAR AS kommentar, 
        WEHR.LASTMODIFIED AS createdat
    FROM WEHR
    LEFT JOIN (SELECT NAME, DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SCHACHT
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SPEICHERSCHACHT) AS SO ON WEHR.SCHACHTOBEN = SO.NAME 
    LEFT JOIN (SELECT NAME, DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SCHACHT
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM AUSLASS
         UNION SELECT NAME, GELAENDEHOEHE AS DECKELHOEHE, XKOORDINATE, YKOORDINATE FROM SPEICHERSCHACHT) AS SU
    ON WEHR.SCHACHTUNTEN = SU.NAME'''
    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Wehrdaten in die QKan-DB schreiben

    for attr in daten:
        (wnam_ansi, schoben_ansi, schunten_ansi, typ_he, schwellenhoehe, kammerhoehe, laenge, uebeiwert,
         xob, yob, xun, yun, simstat_he, kommentar_ansi, createdat) = ['NULL' if el is None else el for el in attr]

        (wnam, schoben, schunten, kommentar) = [tt.decode('iso-8859-1') for tt in (wnam_ansi, schoben_ansi,
                                                                                   schunten_ansi, kommentar_ansi)]

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            if not dbQK.sql(sql, u'importkanaldaten_he (27)'):
                return None

        # Geo-Objekt erzeugen

        if xun == u'NULL' or yun == u'NULL':
            # Es gibt keinen Schacht unten. Dann wird die Pumpe grafisch nach rechs oben
            # erzeugt
            xun = u'{:.3f}'.format(float(xob) + 10.)
            yun = u'{:.3f}'.format(float(yob) + 10.)

        if dbtyp == u'SpatiaLite':
            geom = u'MakeLine(MakePoint({0:},{1:},{4:}),MakePoint({2:},{3:},{4:}))'.format(xob, yob, xun, yun, epsg)
        elif dbtyp == u'postgis':
            geom = u'ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:}),{4:}),ST_SetSRID(ST_MakePoint({2:},{3:}),{4:}))'.format(
                xob, yob, xun, yun, epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz aufbereiten und in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO wehre (wnam, schoben, schunten, schwellenhoehe, kammerhoehe,
                 laenge, uebeiwert, simstatus, kommentar, createdat, geom) 
                 VALUES ('{wnam}', '{schoben}', '{schunten}', {schwellenhoehe},
                {kammerhoehe}, {laenge}, {uebeiwert}, '{simstatus}', '{kommentar}', '{createdat}', 
                {geom})""".format(wnam=wnam,
                                  schoben=schoben, schunten=schunten, schwellenhoehe=schwellenhoehe,
                                  kammerhoehe=kammerhoehe, laenge=laenge, uebeiwert=uebeiwert, simstatus=simstatus,
                                  kommentar=kommentar, createdat=createdat, geom=geom)
            ok = True
        except BaseException as err:
            fehlermeldung(u'Fehler', repr(err))
            ok = False
            fehlermeldung(u"Fehler in QKan_Import_from_HE",
                          u"\nFehler in sql INSERT INTO wehre: \n" + str((wnam, schoben, schunten,
                                                                          schwellenhoehe, kammerhoehe, laenge,
                                                                          uebeiwert, geom)) + u'\n\n')

        if ok:
            if not dbQK.sql(sql, u'importkanaldaten_he (28)'):
                return None
    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Einzugsgebiete

    # Tabelle in QKan-Datenbank bleibt bestehen, damit gegebenenfalls erstellte 
    # Teileinzugsgebiete, deren Geo-Objekte ja in HYSTEM-EXTRAN nicht verwaltet
    # werden können, erhalten bleiben. Deshalb wird beim Import geprüft, ob das
    # jeweilige Objekt schon vorhanden ist.
    # sql = u'DELETE FROM einzugsgebiete'
    # if not dbQK.sql(sql, u'importkanaldaten_he (29)'):
    #     return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
    SELECT 
        NAME AS tgnam,
        EINWOHNERDICHTE AS ewdichte,
        WASSERVERBRAUCH AS wverbrauch,
        STUNDENMITTEL AS stdmittel,
        FREMDWASSERANTEIL AS fremdwas,
        FLAECHE AS flaeche,
        KOMMENTAR AS kommentar,
        LASTMODIFIED AS createdat
    FROM
        teileinzugsgebiet'''

    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Teileinzugsgebietsdaten in die QKan-DB schreiben

    for attr in daten:
        (tgnam_ansi, ewdichte, wverbrauch, stdmittel, fremdwas, flaeche, kommentar_ansi, createdat) = [
            u'NULL' if el is None else el for el in attr]

        (tgnam, kommentar) = [tt.decode('iso-8859-1') for tt in (tgnam_ansi, kommentar_ansi)]

        # Datensatz aufbereiten und in die QKan-DB schreiben

        try:
            sql = u"""
              INSERT INTO einzugsgebiete (tgnam, ewdichte, wverbrauch, stdmittel,
                fremdwas, kommentar, createdat) 
              VALUES ('{tgnam}', {ewdichte}, {wverbrauch}, {stdmittel}, {fremdwas},
                '{kommentar}', '{createdat}')
                 """.format(tgnam=tgnam, ewdichte=ewdichte, wverbrauch=wverbrauch, stdmittel=stdmittel,
                            fremdwas=fremdwas, kommentar=kommentar, createdat=createdat)
            ok = True
        except BaseException as err:
            fehlermeldung(u'SQL-Fehler', repr(err))
            fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql INSERT INTO einzugsgebiete: \n" + \
                          repr((tgnam, ewdichte, wverbrauch, stdmittel,
                               fremdwas, kommentar, createdat)) + u'\n\n')
            ok = False

        if ok:
            if not dbQK.sql(sql, u'importkanaldaten_he (30)'):
                return None
    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Speicherkennlinien

    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM speicherkennlinien'
        if not dbQK.sql(sql, u'importkanaldaten_he (31)'):
            return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
        SELECT 
            NAME AS schnam, 
            KEYWERT + SOHLHOEHE AS wspiegel, 
            WERT AS oberfl 
        FROM TABELLENINHALTE 
        JOIN SPEICHERSCHACHT 
        ON TABELLENINHALTE.ID = SPEICHERSCHACHT.ID 
        ORDER BY SPEICHERSCHACHT.ID, TABELLENINHALTE.REIHENFOLGE'''

    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Speicherdaten in die QKan-DB schreiben

    for attr in daten:
        (schnam_ansi, wspiegel, oberfl) = ['NULL' if el is None else el for el in attr]

        schnam = schnam_ansi.decode('iso-8859-1')

        # Datensatz aufbereiten und in die QKan-DB schreiben

        sql = u"""INSERT INTO speicherkennlinien (schnam, wspiegel, oberfl) 
             VALUES ('{schnam}', {wspiegel}, {oberfl})""".format(schnam=schnam,
                                                                 wspiegel=wspiegel, oberfl=oberfl)

        if not dbQK.sql(sql, u'importkanaldaten_he (32)'):
            return None
    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Sonderprofildaten

    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM profildaten'
        if not dbQK.sql(sql, u'importkanaldaten_he (33)'):
            return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
        SELECT 
            NAME AS profilnam, 
            KEYWERT AS wspiegel, 
            WERT AS wbreite 
        FROM TABELLENINHALTE 
        JOIN SONDERPROFIL 
        ON TABELLENINHALTE.ID = SONDERPROFIL.ID 
        ORDER BY SONDERPROFIL.ID, TABELLENINHALTE.REIHENFOLGE'''

    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Profil in die QKan-DB schreiben

    for attr in daten:
        (profilnam_ansi, wspiegel, wbreite) = ['NULL' if el is None else el for el in attr]

        profilnam = profilnam_ansi.decode('iso-8859-1')

        # Datensatz aufbereiten und in die QKan-DB schreiben

        sql = u"""INSERT INTO profildaten (profilnam, wspiegel, wbreite) 
             VALUES ('{profilnam}', {wspiegel}, {wbreite})""".format(profilnam=profilnam,
                                                                     wspiegel=wspiegel, wbreite=wbreite)

        if not dbQK.sql(sql, u'importkanaldaten_he (34)'):
            return None
    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Abflussparameter

    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM abflussparameter'
        if not dbQK.sql(sql, u'importkanaldaten_he (35)'):
            return None

    # Daten aUS ITWH-Datenbank abfragen
    sql = u'''
        SELECT 
            NAME AS apnam_ansi,
            ABFLUSSBEIWERTANFANG AS anfangsabflussbeiwert,
            ABFLUSSBEIWERTENDE AS endabflussbeiwert,
            MULDENVERLUST AS muldenverlust,
            BENETZUNGSVERLUST AS benetzungsverlust,
            BENETZUNGSPEICHERSTART AS benetzung_startwert,
            MULDENAUFFUELLGRADSTART AS mulden_startwert,
            TYP AS aptyp,
            BODENKLASSE AS bodenklasse_ansi,
            LASTMODIFIED AS createdat,
            KOMMENTAR AS kommentar_ansi
        FROM ABFLUSSPARAMETER'''

    dbHE.sql(sql)
    daten = dbHE.fetchall()

    # Abflussparameter in die QKan-DB schreiben

    # Zuerst sicherstellen, dass die Datensätze nicht schon vorhanden sind. Falls doch, werden sie überschrieben
    sql = u'SELECT apnam FROM abflussparameter'
    if not dbQK.sql(sql, u'importkanaldaten_he (36)'):
        return None
    datqk = [el[0] for el in dbQK.fetchall()]

    for attr in daten:
        (apnam_ansi, anfangsabflussbeiwert, endabflussbeiwert, muldenverlust, benetzungsverlust,
         benetzung_startwert, mulden_startwert, aptyp, bodenklasse_ansi, createdat, kommentar_ansi) = \
            ['NULL' if el is None else el for el in attr]

        (apnam, bodenklasse, kommentar) = [tt.decode('iso-8859-1') for tt in
                                           (apnam_ansi, bodenklasse_ansi, kommentar_ansi)]

        if aptyp == 0:
            bodenklasse = u'Undurchlaessig'  # in QKan default für befestigte Flächen

        # Datensatz in die QKan-DB schreiben

        # Falls Datensatz bereits vorhanden: löschen
        if apnam in datqk:
            sql = u"DELETE FROM abflussparameter WHERE apnam = '{}'".format(apnam)
            if not dbQK.sql(sql, u'importkanaldaten_he (37)'):
                return None

        sql = u"""INSERT INTO abflussparameter
              ( apnam, anfangsabflussbeiwert, endabflussbeiwert, 
                benetzungsverlust, muldenverlust, 
                benetzung_startwert, mulden_startwert, 
                bodenklasse, kommentar, createdat) 
              VALUES 
              ( '{apnam}', {anfangsabflussbeiwert}, {endabflussbeiwert}, 
                {benetzungsverlust}, {muldenverlust}, 
                {benetzung_startwert}, {mulden_startwert}, 
                '{bodenklasse}', '{kommentar}', '{createdat}')""".format(apnam=apnam,
                                                                         anfangsabflussbeiwert=anfangsabflussbeiwert,
                                                                         endabflussbeiwert=endabflussbeiwert,
                                                                         benetzungsverlust=benetzungsverlust,
                                                                         muldenverlust=muldenverlust,
                                                                         benetzung_startwert=benetzung_startwert,
                                                                         mulden_startwert=mulden_startwert,
                                                                         bodenklasse=bodenklasse, kommentar=kommentar,
                                                                         createdat=createdat)

        if not dbQK.sql(sql, u'importkanaldaten_he (38)'):
            return None
    dbQK.commit()

    # ------------------------------------------------------------------------------
    # Schachttypen auswerten. Dies geschieht ausschließlich mit SQL-Abfragen

    # -- Anfangsschächte: Schächte ohne Haltung oben
    sql_typAnf = u'''
        UPDATE schaechte SET knotentyp = 'Anfangsschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte AS t_sch 
        LEFT JOIN haltungen AS t_hob
        ON t_sch.schnam = t_hob.schoben
        LEFT JOIN haltungen AS t_hun
        ON t_sch.schnam = t_hun.schunten
        WHERE t_hun.pk IS NULL)'''

    # -- Endschächte: Schächte ohne Haltung unten
    sql_typEnd = u'''
        UPDATE schaechte SET knotentyp = 'Endschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte AS t_sch 
        LEFT JOIN haltungen AS t_hob
        ON t_sch.schnam = t_hob.schunten
        LEFT JOIN haltungen AS t_hun
        ON t_sch.schnam = t_hun.schoben
        WHERE t_hun.pk IS NULL)'''

    # -- Hochpunkt: 
    sql_typHoch = u'''
        UPDATE schaechte SET knotentyp = 'Hochpunkt' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          JOIN schaechte AS t_sun
          ON t_sun.schnam = t_hun.schunten
          JOIN schaechte AS t_sob
          ON t_sob.schnam = t_hob.schunten
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)>ifnull(t_hob.sohleoben,t_sob.sohlhoehe) AND 
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)>ifnull(t_hun.sohleunten,t_sun.sohlhoehe))'''

    # -- Tiefpunkt:
    sql_typTief = u'''
        UPDATE schaechte SET knotentyp = 'Tiefpunkt' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          JOIN schaechte AS t_sun
          ON t_sun.schnam = t_hun.schunten
          JOIN schaechte AS t_sob
          ON t_sob.schnam = t_hob.schunten
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)<ifnull(t_hob.sohleoben,t_sob.sohlhoehe) AND 
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)<ifnull(t_hun.sohleunten,t_sun.sohlhoehe))'''

    # -- Verzweigung:
    sql_typZweig = u'''
        UPDATE schaechte SET knotentyp = 'Verzweigung' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          GROUP BY t_sch.pk
          HAVING count(*) > 1)'''

    # -- Einzelschacht:
    sql_typEinzel = u'''
        UPDATE schaechte SET knotentyp = 'Einzelschacht' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam 
          FROM schaechte AS t_sch 
          LEFT JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          LEFT JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          WHERE t_hun.pk IS NULL AND t_hob.pk IS NULL)'''

    if not dbQK.sql(sql_typAnf, u'importkanaldaten_he (39)'):
        return None

    if not dbQK.sql(sql_typEnd, u'importkanaldaten_he (40)'):
        return None

    if not dbQK.sql(sql_typHoch, u'importkanaldaten_he (41)'):
        return None

    if not dbQK.sql(sql_typTief, u'importkanaldaten_he (42)'):
        return None

    if not dbQK.sql(sql_typZweig, u'importkanaldaten_he (43)'):
        return None

    if not dbQK.sql(sql_typEinzel, u'importkanaldaten_he (44)'):
        return None

    dbQK.commit()

    # --------------------------------------------------------------------------
    # Zoom-Bereich für die Projektdatei vorbereiten
    sql = u'''SELECT min(xkoordinate) AS xmin, 
                    max(xkoordinate) AS xmax, 
                    min(ykoordinate) AS ymin, 
                    max(ykoordinate) AS ymax
             FROM SCHACHT'''
    try:
        dbHE.sql(sql)
    except BaseException as err:
        fehlermeldung(u'SQL-Fehler', repr(err))
        fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql_zoom: \n" + sql + u'\n\n')

    daten = dbHE.fetchone()
    try:
        zoomxmin, zoomxmax, zoomymin, zoomymax = daten
    except BaseException as err:
        fehlermeldung(u'SQL-Fehler', repr(err))
        fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql_zoom; daten= " + str(daten) + u'\n')

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten
    sql = u"""SELECT srid
            FROM geom_cols_ref_sys
            WHERE Lower(f_table_name) = Lower('schaechte')
            AND Lower(f_geometry_column) = Lower('geom')"""
    if not dbQK.sql(sql, u'importkanaldaten_he (45)'):
        return None

    srid = dbQK.fetchone()[0]
    try:
        crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
        srsid = crs.srsid()
        proj4text = crs.toProj4()
        description = crs.description()
        projectionacronym = crs.projectionAcronym()
        if u'ellipsoidacronym' in dir(crs):
            ellipsoidacronym = crs.ellipsoidacronym()
        else:
            ellipsoidacronym = None
    except BaseException as err:
        srid, srsid, proj4text, description, projectionacronym, ellipsoidacronym = \
            u'dummy', u'dummy', u'dummy', u'dummy', u'dummy', u'dummy'

        fehlermeldung(u'\nFehler in "daten"', repr(err))
        fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler bei der Ermittlung der srid: \n" + str(daten))

    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

    del dbHE
    del dbQK

    # --------------------------------------------------------------------------
    # Projektdatei schreiben, falls ausgewählt

    if projectfile is not None and projectfile != u'':
        templatepath = os.path.join(pluginDirectory('qkan'), u"database/templates")
        projecttemplate = os.path.join(templatepath, u"projekt.qgs")
        projectpath = os.path.dirname(projectfile)
        if os.path.dirname(database_QKan) == projectpath:
            datasource = database_QKan.replace(os.path.dirname(database_QKan), u'.')
        else:
            datasource = database_QKan

        # Liste der Geotabellen aus QKan, um andere Tabellen von der Bearbeitung auszuschliessen
        # Liste steht in 3 Modulen: tools.k_tools, importdyna.import_from_dyna, importhe.import_from_he
        tabliste = [u'einleit', u'einzugsgebiete', u'flaechen', u'haltungen', u'linkfl', u'linksw', 
                    u'pumpen', u'schaechte', u'teilgebiete', u'tezg', u'wehre']

        # Liste der QKan-Formulare, um individuell erstellte Formulare von der Bearbeitung auszuschliessen
        formsliste = ['qkan_abflussparameter.ui', 'qkan_anbindungageb.ui', 'qkan_anbindungeinleit.ui', 
                      'qkan_anbindungflaechen.ui', 'qkan_auslaesse.ui', 'qkan_auslasstypen.ui', 
                      'qkan_aussengebiete.ui', 'qkan_bodenklassen.ui', 'qkan_einleit.ui', 
                      'qkan_einzugsgebiete.ui', 'qkan_entwaesserungsarten.ui', 'qkan_flaechen.ui', 
                      'qkan_haltungen.ui', 'qkan_profildaten.ui', 'qkan_profile.ui', 'qkan_pumpen.ui', 
                      'qkan_pumpentypen.ui', 'qkan_schaechte.ui', 'qkan_simulationsstatus.ui', 
                      'qkan_speicher.ui', 'qkan_speicherkennlinien.ui', 'qkan_swref.ui', 
                      'qkan_teilgebiete.ui', 'qkan_tezg.ui', 'qkan_wehre.ui']

        # Lesen der Projektdatei ------------------------------------------------------------------
        qgsxml = ET.parse(projecttemplate)
        root = qgsxml.getroot()

        # Projektionssystem anpassen --------------------------------------------------------------

        for tag_maplayer in root.findall(u".//projectlayers/maplayer"):
            tag_datasource = tag_maplayer.find(u"./datasource")
            tex = tag_datasource.text
            # Nur QKan-Tabellen bearbeiten
            if tex[tex.index(u'table="') + 7:].split(u'" ')[0] in tabliste:

                # <extend> löschen
                for tag_extent in tag_maplayer.findall(u"./extent"):
                    tag_maplayer.remove(tag_extent)

                for tag_spatialrefsys in tag_maplayer.findall(u"./srs/spatialrefsys"):
                    tag_spatialrefsys.clear()

                    elem = ET.SubElement(tag_spatialrefsys, u'proj4')
                    elem.text = proj4text
                    elem = ET.SubElement(tag_spatialrefsys, u'srsid')
                    elem.text = u'{}'.format(srsid)
                    elem = ET.SubElement(tag_spatialrefsys, u'srid')
                    elem.text = u'{}'.format(srid)
                    elem = ET.SubElement(tag_spatialrefsys, u'authid')
                    elem.text = u'EPSG: {}'.format(srid)
                    elem = ET.SubElement(tag_spatialrefsys, u'description')
                    elem.text = description
                    elem = ET.SubElement(tag_spatialrefsys, u'projectionacronym')
                    elem.text = projectionacronym
                    if ellipsoidacronym is not None:
                        elem = ET.SubElement(tag_spatialrefsys, u'ellipsoidacronym')
                        elem.text = ellipsoidacronym

        # Pfad zu Formularen auf plugin-Verzeichnis setzen -----------------------------------------

        formspath =  os.path.join(pluginDirectory('qkan'), u"forms")
        for tag_maplayer in root.findall(u".//projectlayers/maplayer"):
            tag_editform = tag_maplayer.find(u"./editform")
            dateiname = os.path.basename(tag_editform.text)
            if dateiname in formsliste:
                # Nur QKan-Tabellen bearbeiten
                tag_editform.text = os.path.join(formspath,dateiname)

        # Zoom für Kartenfenster einstellen -------------------------------------------------------

        for tag_extent in root.findall(u".//mapcanvas/extent"):
            elem = tag_extent.find(u"./xmin")
            elem.text = u'{:.3f}'.format(zoomxmin)
            elem = tag_extent.find(u"./ymin")
            elem.text = u'{:.3f}'.format(zoomymin)
            elem = tag_extent.find(u"./xmax")
            elem.text = u'{:.3f}'.format(zoomxmax)
            elem = tag_extent.find(u"./ymax")
            elem.text = u'{:.3f}'.format(zoomymax)

        # Projektionssystem anpassen --------------------------------------------------------------

        for tag_spatialrefsys in root.findall(u".//mapcanvas/destinationsrs/spatialrefsys"):
            tag_spatialrefsys.clear()

            elem = ET.SubElement(tag_spatialrefsys, u'proj4')
            elem.text = proj4text
            elem = ET.SubElement(tag_spatialrefsys, u'srid')
            elem.text = u'{}'.format(srid)
            elem = ET.SubElement(tag_spatialrefsys, u'authid')
            elem.text = u'EPSG: {}'.format(srid)
            elem = ET.SubElement(tag_spatialrefsys, u'description')
            elem.text = description
            elem = ET.SubElement(tag_spatialrefsys, u'projectionacronym')
            elem.text = projectionacronym
            if ellipsoidacronym is not None:
                elem = ET.SubElement(tag_spatialrefsys, u'ellipsoidacronym')
                elem.text = ellipsoidacronym

        # Pfad zur QKan-Datenbank anpassen

        for tag_datasource in root.findall(u".//projectlayers/maplayer/datasource"):
            text = tag_datasource.text
            tag_datasource.text = u"dbname='" + datasource + u"' " + text[text.find(u'table='):]

        qgsxml.write(projectfile)  # writing modified project file
        logger.debug(u'Projektdatei: {}'.format(projectfile))
        # logger.debug(u'encoded string: {}'.format(tex))

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen



    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(u"Information", u"Datenimport ist fertig!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage(u"\nFertig: Datenimport erfolgreich!", level=QgsMessageLog.INFO)

    # Importiertes Projekt laden
    project = QgsProject.instance()
    # project.read(QFileInfo(projectfile))
    project.read(QFileInfo(projectfile))  # read the new project file
    logger.debug(u'Geladene Projektdatei: {}'.format(project.fileName()))


# ----------------------------------------------------------------------------------------------------------------------

# Verzeichnis der Testdaten
pfad = u'C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/linges_deng'

database_HE = os.path.join(pfad, u'21.04.2017-2pumpen.idbf')
database_QKan = os.path.join(pfad, u'netz.sqlite')
projectfile = os.path.join(pfad, u'plan.qgs')
epsg = u'31466'

if __name__ == '__main__':
    importKanaldaten(database_HE, database_QKan, projectfile, epsg)
elif __name__ == '__console__':
    # QMessageBox.information(None, u"Info", u"Das Programm wurde aus der QGIS-Konsole aufgerufen")
    importKanaldaten(database_HE, database_QKan, projectfile, epsg)
elif __name__ == '__builtin__':
    # QMessageBox.information(None, u"Info", u"Das Programm wurde aus der QGIS-Toolbox aufgerufen")
    importKanaldaten(database_HE, database_QKan, projectfile, epsg)
# else:
# QMessageBox.information(None, u"Info", u"Die Variable __name__ enthält: {0:s}".format(__name__))
