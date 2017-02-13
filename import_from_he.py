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


import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__),'..\QKan_Database'))

from fbfunc import FBConnection
from dbfunc import DBConnection

import tempfile

# from qgis.core import *
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
from qgis.core import QgsFeature, QgsGeometry, QgsMessageLog
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon

from qgis.utils import iface
from qgis.gui import QgsMessageBar
import codecs
import pyspatialite.dbapi2 as splite
from xml.dom.minidom import parse as xmlparse
# import sqlite3


# ------------------------------------------------------------------------------
# Hauptprogramm

def importKanaldaten(database_HE, database_QKan, projectfile, epsg, dbtyp = 'SpatiaLite'):

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

    # ------------------------------------------------------------------------------
    # Interne Funktionen

    def setNodeValue(supnode, tagname, value):
        # Setzt ein XML-Tag-Wert oder fügt ihn ein, falls nicht vorhanden.

        node = supnode.getElementsByTagName(tagname)[0]
        if node.hasChildNodes():
            node.childNodes[0].nodeValue = value
        else:
            xnode = qgsxml.createTextNode(value)
            node.appendChild(xnode)


    # ------------------------------------------------------------------------------
    # Start

    protokoll = u""

    dbHE = FBConnection(database_HE)        # Datenbankobjekt der HE-Datenbank zum Lesen

    if dbHE is None:
        iface.messageBar().pushMessage("Fehler", 'ITWH-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
            database_HE), level=QgsMessageBar.CRITICAL)
        return None

    dbQK = DBConnection(database_QKan)      # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        iface.messageBar().pushMessage("Fehler", 'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
            database_QKan), level=QgsMessageBar.CRITICAL)
        return None
    
    # Referenztabellen laden. 

    # Entwässerungssystem. Attribut [kuerzel] enthält die Bezeichnung des Benutzers.
    sql = 'SELECT he_nr, kuerzel FROM entwaesserungsart'
    dbQK.sql(sql)
    daten = dbQK.fetchall()
    ref_entwart = {}
    for el in daten:
        ref_entwart[el[0]] = el[1]

    # Pumpentypen. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
    sql = 'SELECT he_nr, bezeichnung FROM pumpentypen'
    dbQK.sql(sql)
    daten = dbQK.fetchall()
    ref_pumpentyp = {}
    for el in daten:
        ref_pumpentyp[el[0]] = el[1]

    # Profile. Attribut [profilnam] enthält die Bezeichnung des Benutzers. Dies kann auch ein Kürzel sein.
    sql = 'SELECT he_nr, profilnam FROM profile'
    dbQK.sql(sql)
    daten = dbQK.fetchall()
    ref_profil = {}
    for el in daten:
        ref_profil[el[0]] = el[1]

    # Auslasstypen.
    sql = 'SELECT he_nr, bezeichnung FROM auslasstypen'
    dbQK.sql(sql)
    daten = dbQK.fetchall()
    ref_auslasstypen = {}
    for el in daten:
        ref_auslasstypen[el[0]] = el[1]

    # Simulationsstatus
    sql = 'SELECT he_nr, bezeichnung FROM simulationsstatus'
    dbQK.sql(sql)
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
    sql = 'DELETE FROM haltungen'
    dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
    SELECT 
        ROHR.NAME as haltnam, 
        ROHR.SCHACHTOBEN as schoben, 
        ROHR.SCHACHTUNTEN as schunten, 
        ROHR.GEOMETRIE1 as hoehe, 
        ROHR.GEOMETRIE2 as breite, 
        ROHR.LAENGE as laenge, 
        ROHR.SOHLHOEHEOBEN as sohleoben, 
        ROHR.SOHLHOEHEUNTEN as sohleunten, 
        SO.DECKELHOEHE as deckeloben, 
        SU.DECKELHOEHE as deckelunten, 
        ROHR.TEILEINZUGSGEBIET as teilgebiet, 
        ROHR.PROFILTYP as profiltyp_he, 
        ROHR.SONDERPROFILBEZEICHNUNG as profilnam, 
        ROHR.KANALART as entwaesserungsart_he, 
        ROHR.RAUIGKEITSBEIWERT as ks, 
        ROHR.PLANUNGSSTATUS as simstat_he, 
        ROHR.KOMMENTAR AS kommentar, 
        ROHR.LASTMODIFIED AS createdat, 
        SO.XKOORDINATE as xob, 
        SO.YKOORDINATE as yob, 
        SU.XKOORDINATE as xun, 
        SU.YKOORDINATE as yun
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
            if profilnam == 'NULL':
                # In HE ist nur die Profilnummer enthalten. Dann muss ein Profilname erzeugt werden, z.B. (12)
                profilnam = u'({profiltyp_he})'.format(profiltyp_he=profiltyp_he)

            # In Referenztabelle in dieser Funktion sowie in der QKan-Tabelle profile einfügen
            ref_profil[profiltyp_he]=profilnam
            sql = u"INSERT INTO profile (profilnam, he_nr) Values ('{profilnam}', {profiltyp_he})".format( \
                       profilnam=profilnam, profiltyp_he=profiltyp_he)
            dbQK.sql(sql)

        # Entwasserungsarten. Hier ist es einfacher als bei den Profilen...
        if entwaesserungsart_he in ref_entwart:
            entwart = ref_entwart[entwaesserungsart_he]
        else:
            # Noch nicht in Tabelle [entwaesserungsart] enthalten, also ergqenzen
            entwart = u'({})'.format(entwaesserungsart_he)
            sql = u"INSERT INTO entwaesserungsart (kuerzel, he_nr) Values ('{entwart}', {he_nr})".format( \
                      entwart=entwart, he_nr=entwaesserungsart_he)
            ref_entwart[entwaesserungsart_he] = entwart
            dbQK.sql(sql)

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                      simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            dbQK.sql(sql)


        # Geo-Objekt erzeugen

        if dbtyp == 'SpatiaLite':
            geom = 'MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:s}))'.format(xob, yob, xun, yun, epsg)
        elif dbtyp == 'postgis':
            geom = 'ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:}),{4:s}),ST_SetSRID(ST_MakePoint({2:},{3:}),{4:s}))'.format(xob, yob, xun, yun, epsg)
        else:
            raise RuntimeError('Fehler: Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

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
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += "\nFehler in sql INSERT INTO haltungen: \n" + str((geom, haltnam, schoben, schunten, 
                hoehe, breite, laenge, sohleoben, sohleunten, 
                deckeloben, deckelunten, teilgebiet, profilnam, entwart, ks, simstatus)) + '\n\n'

        try:
            dbQK.sql(sql)
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += "\nFehler in sql: \n" + sql + '\n\n'

    dbQK.commit()


# ------------------------------------------------------------------------------
# Schachtdaten
# Das Feld [KANALART] enthält das Entwasserungssystem (Schmutz-, Regen- oder Mischwasser)
# Das Feld [ART] enthält die Information, ob es sich um einen Startknoten oder einen Inneren Knoten handelt.
# oder: um was für eine #Verzweigung es sich handelt (Wunsch von Herrn Wippermann)...???


    # Tabelle in QKan-Datenbank leeren
    sql = 'DELETE FROM schaechte'
    dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
    SELECT 
        NAME as schnam,
        XKOORDINATE as xsch, 
        YKOORDINATE as ysch, 
        SOHLHOEHE as sohlhoehe, 
        DECKELHOEHE as deckelhoehe, 
        DURCHMESSER as durchm, 
        DRUCKDICHTERDECKEL as druckdicht, 
        KANALART as entwaesserungsart_he, 
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
            # Noch nicht in Tabelle [entwaesserungsart] enthalten, also ergänzen
            sql = u"INSERT INTO entwaesserungsart (kuerzel, he_nr) Values ('({0:})', {0:d})".format(entwaesserungsart_he)
            entwart = '({:})'.format(entwaesserungsart_he)
            dbQK.sql(sql)

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                      simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            dbQK.sql(sql)

        # Geo-Objekte erzeugen

        if dbtyp == 'SpatiaLite':
            geop = 'MakePoint({0:},{1:},{2:s})'.format(xsch,ysch,epsg)
            geom = 'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:s})))'.format(xsch,ysch,durchm/1000.,epsg)
        elif dbtyp == 'postgis':
            geop = 'ST_SetSRID(ST_MakePoint(avg(xsch),avg(ysch)),{0:s})'.format(xsch,ysch,epsg)
        else:
            raise RuntimeError('Fehler: Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,
            dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                                        schachttyp, simstatus, kommentar, createdat, geop, geom)
            VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, {durchm}, {druckdicht}, '{entwart}', 
                     '{schachttyp}', '{simstatus}', '{kommentar}', '{createdat}', 
                     {geop}, {geom})""".format( \
                     schnam=schnam, xsch=xsch, ysch=ysch, sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe, 
                     durchm=durchm, druckdicht=druckdicht, entwart=entwart, 
                     schachttyp = 'Schacht', simstatus=simstatus, 
                     kommentar=kommentar, createdat=createdat, geop=geop, geom=geom)
            dbQK.sql(sql)
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += "\nSchächte: in sql: \n" + sql + '\n\n'

    dbQK.commit()



# ------------------------------------------------------------------------------
# Speicherschachtdaten


    # Tabelle in QKan-Datenbank leeren
    # sql = 'DELETE FROM speicherschaechte'
    # dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
    SELECT NAME as schnam, 
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
            dbQK.sql(sql)

        # Geo-Objekte erzeugen

        if dbtyp == 'SpatiaLite':
            geop = 'MakePoint({0:},{1:},{2:s})'.format(xsch,ysch,epsg)
            geom = 'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:s})))'.format(xsch,ysch,durchm/1000.,epsg)
        elif dbtyp == 'postgis':
            geop = 'ST_SetSRID(ST_MakePoint(avg(xsch),avg(ysch)),{0:s})'.format(xsch,ysch,epsg)
        else:
            raise RuntimeError('Fehler: Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        sql = u"""INSERT INTO schaechte (schnam, deckelhoehe, sohlhoehe, xsch, ysch, ueberstauflaeche, 
                    schachttyp, simstatus, kommentar, createdat, geop, geom)
            VALUES ('{schnam}', {deckelhoehe}, {sohlhoehe}, {xsch}, {ysch}, {ueberstauflaeche}, 
                    '{schachttyp}', '{simstatus}', '{kommentar}', '{createdat}', 
                    {geop}, {geom})""".format( \
                    schnam=schnam, deckelhoehe=deckelhoehe, sohlhoehe=sohlhoehe, 
                    xsch=xsch, ysch=ysch, ueberstauflaeche=ueberstauflaeche, 
                    schachttyp = 'Speicher', simstatus=simstatus, kommentar=kommentar, 
                    createdat=createdat, geop=geop, geom=geom)
        try:
            dbQK.sql(sql)
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += "\nSpeicherschachtdaten in sql: \n" + sql + '\n\n'

    dbQK.commit()


# ------------------------------------------------------------------------------
# Auslässe
# Das Feld [TYP] enthält den Auslasstyp (0=Frei, 1=Normal, 2= Konstant, 3=Tide, 4=Zeitreihe)


    # Tabelle in QKan-Datenbank leeren
    # sql = 'DELETE FROM auslaesse'
    # dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
    SELECT NAME as schnam, 
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

    # Speicherschachtdaten aufbereiten und in die QKan-DB schreiben

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
            dbQK.sql(sql)

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                      simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            dbQK.sql(sql)

        # Geo-Objekte erzeugen

        if dbtyp == 'SpatiaLite':
            geop = 'MakePoint({0:},{1:},{2:s})'.format(xsch,ysch,epsg)
            geom = 'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:s})))'.format(xsch,ysch,1.,epsg)
        elif dbtyp == 'postgis':
            geop = 'ST_SetSRID(ST_MakePoint(avg(xsch),avg(ysch)),{0:s})'.format(xsch,ysch,epsg)
        else:
            raise RuntimeError('Fehler: Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, 
                    auslasstyp, schachttyp, simstatus, kommentar, createdat, geop, geom)
            VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, '{auslasstyp}', 
                    '{schachttyp}', '{simstatus}', '{kommentar}', 
                    '{createdat}', {geop}, {geom})""".format(schnam=schnam, xsch=xsch, ysch=ysch, 
                    sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe, auslasstyp=auslasstyp, 
                    schachttyp = 'Auslass', simstatus=simstatus, 
                    kommentar=kommentar, createdat=createdat, geop=geop, geom=geom)
        # protokoll += '\n' + sql
        try:
            dbQK.sql(sql)
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += "\nAuslässe: in sql: \n" + sql + '\n\n'

    dbQK.commit()


# ------------------------------------------------------------------------------
# Pumpen

    # Tabelle in QKan-Datenbank leeren
    sql = 'DELETE FROM pumpen'
    dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
    SELECT 
        PUMPE.NAME AS pname, 
        PUMPE.SCHACHTOBEN AS schoben, 
        PUMPE.SCHACHTUNTEN AS schunten, 
        PUMPE.TYP as typ_he, 
        PUMPE.STEUERSCHACHT AS steuersch, 
        PUMPE.EINSCHALTHOEHE AS einschalthoehe, 
        PUMPE.AUSSCHALTHOEHE AS ausschalthoehe,
        SO.XKOORDINATE as xob, 
        SO.YKOORDINATE as yob, 
        SU.XKOORDINATE as xun, 
        SU.YKOORDINATE as yun, 
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
        (pname_ansi, schoben_ansi, schunten_ansi, typ_he, steuersch, einschalthoehe, ausschalthoehe, 
         xob, yob, xun, yun, simstat_he, kommentar_ansi, createdat) = ['NULL' if el is None else el for el in attr]

        (pname, schoben, schunten, kommentar) = [tt.decode('iso-8859-1') for tt in (pname_ansi, schoben_ansi, 
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
            dbQK.sql(sql)

        # Simstatus-Nr aus HE ersetzten
        if simstat_he in ref_simulationsstatus:
            simstatus = ref_simulationsstatus[simstat_he]
        else:
            # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            simstatus = u'({}_he)'.format(simstat_he)
            sql = u"INSERT INTO simulationsstatus (bezeichnung, he_nr) Values ('{simstatus}', {he_nr})".format( \
                      simstatus=simstatus, he_nr=simstat_he)
            ref_simulationsstatus[simstat_he] = simstatus
            dbQK.sql(sql)

        # Geo-Objekt erzeugen

        if xun == 'NULL' or yun == 'NULL':
            # Es gibt keinen Schacht unten. Dann wird die Pumpe grafisch nach rechs oben
            # erzeugt
            xun = '{:.3f}'.format(float(xob) + 10.)
            yun = '{:.3f}'.format(float(yob) + 10.)

        if dbtyp == 'SpatiaLite':
            geom = 'MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:s}))'.format(xob, yob, xun, yun, epsg)
        elif dbtyp == 'postgis':
            geom = '''ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:}),{4:s}),
                      ST_SetSRID(ST_MakePoint({2:},{3:}),{4:s}))'''.format(xob, yob, xun, yun, epsg)
        else:
            raise RuntimeError('Fehler: Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,
            dbdatabase[-7:].lower()))

        # Datensatz aufbereiten und in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO pumpen 
                (pname, schoben, schunten, pumpentyp, steuersch, einschalthoehe, ausschalthoehe, 
                simstatus, kommentar, createdat, geom) 
                VALUES ('{pname}', '{schoben}', '{schunten}', '{pumpentyp}', '{steuersch}', 
                {einschalthoehe}, {ausschalthoehe}, '{simstatus}', '{kommentar}', '{createdat}', {geom})""".format( \
                    pname=pname, schoben=schoben, schunten=schunten, pumpentyp=pumpentyp, steuersch=steuersch, 
                    einschalthoehe=einschalthoehe, ausschalthoehe=ausschalthoehe, simstatus=simstatus, 
                    kommentar=kommentar, createdat=createdat, geom=geom)
            # Nur zum Test
            # protokoll += "Info zur sql-Abfrage pumpen: \n" + sql + '\n\n'
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += "\nFehler in sql INSERT INTO pumpen: \n" + str((pname, schoben, \
                schunten, pumpentyp, steuersch, einschalthoehe, ausschalthoehe, geom)) + '\n\n'

        try:
            dbQK.sql(sql)
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += "\nPumpen: in sql: \n" + sql + '\n\n'
    dbQK.commit()


# ------------------------------------------------------------------------------
# Wehre

    # Tabelle in QKan-Datenbank leeren
    sql = 'DELETE FROM wehre'
    dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
    SELECT 
        WEHR.NAME AS wname, 
        WEHR.SCHACHTOBEN AS schoben, 
        WEHR.SCHACHTUNTEN AS schunten, 
        WEHR.TYP as typ_he, 
        WEHR.SCHWELLENHOEHE AS schwellenhoehe, 
        WEHR.GEOMETRIE1 AS kammerhoehe, 
        WEHR.GEOMETRIE2 AS laenge,
        WEHR.UEBERFALLBEIWERT AS uebeiwert,
        SO.XKOORDINATE as xob, 
        SO.YKOORDINATE as yob, 
        SU.XKOORDINATE as xun, 
        SU.YKOORDINATE as yun, 
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
        (wname_ansi, schoben_ansi, schunten_ansi, typ_he, schwellenhoehe, kammerhoehe, laenge, uebeiwert,
         xob, yob, xun, yun, simstat_he, kommentar_ansi, createdat) = ['NULL' if el is None else el for el in attr]

        (wname, schoben, schunten, kommentar) = [tt.decode('iso-8859-1') for tt in (wname_ansi, schoben_ansi, 
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
            dbQK.sql(sql)

        # Geo-Objekt erzeugen

        if xun == 'NULL' or yun == 'NULL':
            # Es gibt keinen Schacht unten. Dann wird die Pumpe grafisch nach rechs oben
            # erzeugt
            xun = '{:.3f}'.format(float(xob) + 10.)
            yun = '{:.3f}'.format(float(yob) + 10.)

        if dbtyp == 'SpatiaLite':
            geom = 'MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:s}))'.format(xob, yob, xun, yun, epsg)
        elif dbtyp == 'postgis':
            geom = 'ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:}),{4:s}),ST_SetSRID(ST_MakePoint({2:},{3:}),{4:s}))'.format(xob, yob, xun, yun, epsg)
        else:
            raise RuntimeError('Fehler: Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz aufbereiten und in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO wehre (wname, schoben, schunten, schwellenhoehe, kammerhoehe, 
                 laenge, uebeiwert, simstatus, kommentar, createdat, geom) 
                 VALUES ('{wname}', '{schoben}', '{schunten}', {schwellenhoehe}, 
                {kammerhoehe}, {laenge}, {uebeiwert}, '{simstatus}', '{kommentar}', '{createdat}', 
                {geom})""".format(wname=wname, 
                    schoben=schoben, schunten=schunten, schwellenhoehe=schwellenhoehe, 
                    kammerhoehe=kammerhoehe, laenge=laenge, uebeiwert=uebeiwert, simstatus=simstatus, 
                    kommentar=kommentar, createdat=createdat, geom=geom)
            ok = True
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            ok = False
            protokoll += "\nFehler in sql INSERT INTO wehre: \n" + str((wname, schoben, schunten, 
            schwellenhoehe, kammerhoehe, laenge, uebeiwert, geom)) + '\n\n'

        if ok:
            try:
                dbQK.sql(sql)
            except BaseException as e:
                protokoll += '\n\n' + str(e)
                protokoll += u"\nWehre: Fehler in sql: \n" + sql + u'\n\n'
    dbQK.commit()


# ------------------------------------------------------------------------------
# Speicherkennlinie

    # Tabelle in QKan-Datenbank leeren
    sql = 'DELETE FROM speicherkennlinie'
    dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
        SELECT 
            NAME AS schnam, 
            KEYWERT + SOHLHOEHE as wspiegel, 
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

        sql = u"""INSERT INTO speicherkennlinie (schnam, wspiegel, oberfl) 
             VALUES ('{schnam}', {wspiegel}, {oberfl})""".format(schnam=schnam, 
             wspiegel=wspiegel, oberfl=oberfl)

        try:
            dbQK.sql(sql)
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += u"\nSpeicherkennlinie:Fehler in sql: \n" + sql + u'\n\n'
    dbQK.commit()


# ------------------------------------------------------------------------------
# Sonderprofildaten

    # Tabelle in QKan-Datenbank leeren
    sql = 'DELETE FROM profildaten'
    dbQK.sql(sql)

    # Daten aUS ITWH-Datenbank abfragen
    sql = '''
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

        try:
            dbQK.sql(sql)
        except BaseException as e:
            protokoll += '\n\n' + str(e)
            protokoll += u"\nSonderprofildaten: Fehler in sql: \n" + sql + u'\n\n'
    dbQK.commit()

        
    # ------------------------------------------------------------------------------
    # Schachttypen auswerten. Dies geschieht ausschließlich mit SQL-Abfragen

    # -- Anfangsschächte: Schächte ohne Haltung oben
    sql_typAnf = '''
        UPDATE schaechte SET knotentyp = 'Anfangsschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte as t_sch 
        LEFT JOIN haltungen as t_hob
        ON t_sch.schnam = t_hob.schoben
        LEFT JOIN haltungen as t_hun
        ON t_sch.schnam = t_hun.schunten
        WHERE t_hun.pk IS NULL)'''

    # -- Endschächte: Schächte ohne Haltung unten
    sql_typEnd = '''
        UPDATE schaechte SET knotentyp = 'Endschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte as t_sch 
        LEFT JOIN haltungen as t_hob
        ON t_sch.schnam = t_hob.schunten
        LEFT JOIN haltungen as t_hun
        ON t_sch.schnam = t_hun.schoben
        WHERE t_hun.pk IS NULL)'''

    # -- Hochpunkt: 
    sql_typHoch = '''
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
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)>ifnull(t_hob.sohleoben,t_sob.sohlhoehe) and 
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)>ifnull(t_hun.sohleunten,t_sun.sohlhoehe))'''

    # -- Tiefpunkt:
    sql_typTief = '''
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
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)<ifnull(t_hob.sohleoben,t_sob.sohlhoehe) and 
                ifnull(t_hun.sohleoben,t_sch.sohlhoehe)<ifnull(t_hun.sohleunten,t_sun.sohlhoehe))'''

    # -- Verzweigung:
    sql_typZweig = '''
        UPDATE schaechte SET knotentyp = 'Verzweigung' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam
          FROM schaechte AS t_sch 
          JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          GROUP BY t_sch.pk
          HAVING count(*) > 1)'''

    # -- Einzelschacht:
    sql_typEinzel = '''
        UPDATE schaechte SET knotentyp = 'Einzelschacht' WHERE schaechte.schnam IN
        ( SELECT t_sch.schnam 
          FROM schaechte AS t_sch 
          LEFT JOIN haltungen AS t_hun
          ON t_sch.schnam = t_hun.schoben
          LEFT JOIN haltungen AS t_hob
          ON t_sch.schnam = t_hob.schunten
          WHERE t_hun.pk IS NULL AND t_hob.pk IS NULL)'''

    try:
        dbQK.sql(sql_typAnf)
    except BaseException as e:
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_typAnf: \n" + sql_typAnf + '\n\n'

    try:
        dbQK.sql(sql_typEnd)
    except BaseException as e:
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_typEnd: \n" + sql_typEnd + '\n\n'

    try:
        dbQK.sql(sql_typHoch)
    except BaseException as e:
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_typHoch: \n" + sql_typHoch + '\n\n'

    try:
        dbQK.sql(sql_typTief)
    except BaseException as e:
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_typTief: \n" + sql_typTief + '\n\n'

    try:
        dbQK.sql(sql_typZweig)
    except BaseException as e:
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_typZweig: \n" + sql_typZweig + '\n\n'

    try:
        dbQK.sql(sql_typEinzel)
    except BaseException as e:
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_typEinzel: \n" + sql_typEinzel + '\n\n'

    dbQK.commit()
    

    # --------------------------------------------------------------------------
    # Zoom-Bereich für die Projektdatei vorbereiten
    sql = '''SELECT min(xkoordinate) AS xmin, 
                    max(xkoordinate) AS xmax, 
                    min(ykoordinate) AS ymin, 
                    max(ykoordinate) AS ymax
             FROM SCHACHT'''
    try:
        dbHE.sql(sql)
    except BaseException as e:
        iface.messageBar().pushMessage("Fehler in sql-Abfrage", sql, level=QgsMessageBar.CRITICAL)
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_zoom: \n" + sql + '\n\n'

    daten = dbHE.fetchone()
    try:
        zoomxmin, zoomxmax, zoomymin, zoomymax = daten
    except BaseException as e:
        protokoll += '\n' + str(e)
        protokoll += "\nFehler in sql_zoom; daten= " + str(daten) + '\n'

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten
    sql = """SELECT srid, proj4text, ref_sys_name
            FROM geom_cols_ref_sys
            WHERE Lower(f_table_name) = Lower('schaechte')
            AND Lower(f_geometry_column) = Lower('geom')"""
    try:
        dbQK.sql(sql)
    except BaseException as e:
        iface.messageBar().pushMessage("Fehler in sql-Abfrage", sql, level=QgsMessageBar.CRITICAL)
        protokoll += '\n\n' + str(e)
        protokoll += "\nFehler in sql_coordsys: \n" + sql + '\n\n'

    daten = dbQK.fetchone()
    try:
        srid, proj4text, ref_sys_name = daten
        projectionacronym = proj4text.split()[0].split('=')[1]
        ellipsoidacronym = proj4text.split()[6].split('=')[1]
    except BaseException as e:
        srid, proj4text, ref_sys_name = ('dummy','dummy','dummy')
        projectionacronym = 'dummy'
        ellipsoidacronym = 'dummy'

        iface.messageBar().pushMessage("Fehler in 'daten'", str(daten), level=QgsMessageBar.CRITICAL)
        protokoll += '\n\n' + str(e)
        # print(daten)
        protokoll += "\nFehler bei der Ermittlung der srid: \n" + str(daten) + '\n\n'


    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

    del dbHE
    del dbQK

    # --------------------------------------------------------------------------
    # Projektdatei schreiben, falls ausgewählt

    if projectfile is not None and projectfile != '':
        qgs_template = os.path.join(os.path.dirname(__file__), "templates","projekt.qgs").replace('\\','/')
        if os.path.dirname(database_QKan) == os.path.dirname(projectfile):
            datasource = database_QKan.replace(os.path.dirname(database_QKan),'.')
        else:
            datasource = database_QKan

        qgsxml = xmlparse(qgs_template)

        # ---------------------------------------------------------------------------
        # extend-Werte xmin, ymin, xmax, ymax ersetzten
        node_mapcanvas = qgsxml.getElementsByTagName("mapcanvas")[0]
        node_extent = node_mapcanvas.getElementsByTagName("extent")[0]
        node_xmin = node_extent.getElementsByTagName("xmin")[0]
        node_xmin.childNodes[0].nodeValue = zoomxmin
        node_ymin = node_extent.getElementsByTagName("ymin")[0]
        node_ymin.childNodes[0].nodeValue = zoomymin
        node_xmax = node_extent.getElementsByTagName("xmax")[0]
        node_xmax.childNodes[0].nodeValue = zoomxmax
        node_ymax = node_extent.getElementsByTagName("ymax")[0]
        node_ymax.childNodes[0].nodeValue = zoomymax

        # ---------------------------------------------------------------------------
        # spatialrefsys ersetzten
        node_destinationsrs = qgsxml.getElementsByTagName("destinationsrs")[0]
        node_spatialrefsys = node_destinationsrs.getElementsByTagName("spatialrefsys")[0]

        # node_proj4 = node_spatialrefsys.getElementsByTagName("proj4")[0]
        # node_proj4.childNodes[0].nodeValue = proj4text
        setNodeValue(node_spatialrefsys,"proj4",proj4text)

        # node_srid = node_spatialrefsys.getElementsByTagName("srid")[0]
        # node_srid.childNodes[0].nodeValue = srid
        setNodeValue(node_spatialrefsys,"srid",srid)

        # node_authid = node_spatialrefsys.getElementsByTagName("authid")[0]
        # node_authid.childNodes[0].nodeValue = 'EPSG: {}'.format(srid)
        setNodeValue(node_spatialrefsys,"authid", 'EPSG: {}'.format(srid))

        # node_description = node_spatialrefsys.getElementsByTagName("description")[0]
        # node_description.childNodes[0].nodeValue = ref_sys_name
        setNodeValue(node_spatialrefsys, "description", ref_sys_name)

        # node_projectionacronym = node_spatialrefsys.getElementsByTagName("projectionacronym")[0]
        # node_projectionacronym.childNodes[0].nodeValue = projectionacronym
        setNodeValue(node_spatialrefsys, "projectionacronym", projectionacronym)

        # node_ellipsoidacronym = node_spatialrefsys.getElementsByTagName("ellipsoidacronym")[0]
        # node_ellipsoidacronym.childNodes[0].nodeValue = ellipsoidacronym
        setNodeValue(node_spatialrefsys, "ellipsoidacronym", ellipsoidacronym)

        # ---------------------------------------------------------------------------
        # datasource ersetzten
        node_projectlayer = qgsxml.getElementsByTagName("projectlayers")[0]
        nodes_maplayer = node_projectlayer.getElementsByTagName("maplayer")
        for node_maplayer in nodes_maplayer:
            node_datasource = node_maplayer.getElementsByTagName("datasource")[0]
            node = node_datasource.childNodes[0]
            text = node.nodeValue
            node.nodeValue = "dbname='" + datasource + "' " + text[text.find('table='):]

        with codecs.open(projectfile,'w','utf-8') as xmldatei:
            qgsxml.writexml(xmldatei)

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    if protokoll != "":
        fd, tmpfil = tempfile.mkstemp(suffix='.log') 
        with codecs.open(tmpfil,'w','utf-8') as proto:
            proto.write(protokoll)
        QgsMessageLog.logMessage(protokoll, "\nFehler in sql: ", QgsMessageLog.INFO)
    
    
    
    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage("Information", "Datenimport ist fertig!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage("\nFertig: Datenimport erfolgreich!", level=QgsMessageLog.INFO)
    
# ----------------------------------------------------------------------------------------------------------------------

# Verzeichnis der Testdaten
pfad = 'C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/modelldb_itwh'

database_HE =   os.path.join(pfad,'muster-modelldatenbank.idbf')
database_QKan = os.path.join(pfad,'test1.sqlite')
projectfile =   os.path.join(pfad,'lageplan_test1.qgs')
epsg = '31467'

if __name__ == '__main__':
    importKanaldaten(database_HE, database_QKan, projectfile, epsg)
elif __name__ == '__console__':
    # QMessageBox.information(None, "Info", "Das Programm wurde aus der QGIS-Konsole aufgerufen")
    importKanaldaten(database_HE, database_QKan, projectfile, epsg)
elif __name__ == '__builtin__':
    # QMessageBox.information(None, "Info", "Das Programm wurde aus der QGIS-Toolbox aufgerufen")
    importKanaldaten(database_HE, database_QKan, projectfile, epsg)
# else:
    # QMessageBox.information(None, "Info", "Die Variable __name__ enthält: {0:s}".format(__name__))
