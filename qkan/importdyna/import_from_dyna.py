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


import os, time, sys

import glob, shutil

from qgis.core import QgsFeature, QgsGeometry, QgsMessageLog, QgsProject, QgsCoordinateReferenceSystem
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QAction, QIcon

from qgis.utils import iface, pluginDirectory
from qgis.gui import QgsMessageBar, QgsMapCanvas, QgsLayerTreeMapCanvasBridge
import codecs
import pyspatialite.dbapi2 as splite
import xml.etree.ElementTree as ET
import logging

from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import fortschritt, fehlermeldung

logger = logging.getLogger('QKan')


# Hilfsfunktionen --------------------------------------------------------------------------
class rahmen():
    '''Koordinatengrenzen in 2D'''
    def __init__(self):
        self.xmin = self.ymin = self.xmax = self.ymax = 0

    def reset(self, x, y):
        self.xmin = self.xmax = x
        self.ymin = self.ymax = y

    def p(self, x, y):
        self.xmin = min(self.xmin, x)
        self.ymin = min(self.ymin, y)
        self.xmax = max(self.xmax, x)
        self.ymax = max(self.ymax, y)

    def line(self, x1, y1, x2, y2):
        self.xmin = min(self.xmin, x1, x2)
        self.ymin = min(self.ymin, y1, y2)
        self.xmax = max(self.xmax, x1, x2)
        self.ymax = max(self.ymax, y1, y2)

    def ppr(self, x1, y1, x2, y2, r):
        d = ((x2-x1)**2 + (y2-y1)**2)**0.5
        if abs(r-d/2) < (r+d/2) / 10000000.:
            h = 0
        elif r > d/2:
            h = (r**2 - d**2/4.)**0.5
        else:
            return None
        xm = (x1+x2)/2. - h/d*(y2-y1)
        ym = (y1+y2)/2. + h/d*(x2-x1)

        # Anpassen der Koordinatengrenzen

        self.xmin = min(self.xmin, x1, x2)
        self.ymin = min(self.ymin, y1, y2)
        self.xmax = max(self.xmax, x1, x2)
        self.ymax = max(self.ymax, y1, y2)

        # Berücksichtung des äußeren Punktes der verbindenden Bogens

        xob, yob = xm, ym + r
        xli, yli = xm - r, ym
        xun, yun = xm, ym - r
        xre, yre = xm + r, ym

        # Nordpol
        if (xob - x1) * (y2 - yob) > (yob - y1) * (x2 - xob):
            self.ymax = max(self.ymax, yob)

        # Westen
        if (xli - x1) * (y2 - yli) > (yli - y1) * (x2 - xli):
            self.xmin = min(self.xmin, xli)

        # Süden
        if (xun - x1) * (y2 - yun) > (yun - y1) * (x2 - xun):
            self.ymin = min(self.ymin, yun)

        # Osten
        if (xre - x1) * (y2 - yre) > (yre - y1) * (x2 - xre):
            self.xmax = max(self.xmax, xre)

        # Berücksichtung des äußeren Punktes der verbindenden Bogens

        # if min(y1, y2) < ym < max(y1, y2):
        #     # Bogen geht linken oder rechten Äquator
        #     if x1 + x2 < 0:
        #         self.xmin = min(self.xmin, xm + r)          # Bogen geht über rechten Äquator
        #     else:
        #         self.xmax = max(self.xmax, xm - r)          # Bogen geht über linken Äquator
        #
        # if min(y1, y2) < ym < max(y1, y2):
        #     # Bogen geht Nord- oder Südpol
        #     if y1 + y2 > 0:
        #         self.ymax = max(self.ymax, ym + r)                    # Bogen geht über Nordpol
        #     else:
        #         self.ymin = min(self.ymin, ym - r)                    # Bogen geht über Südpol

    def ppp(self, x1, y1, x0, y0, x2, y2):
        '''Kreisbogen wird durch 3 Punkte definiert'''
        det=(x1-x0)*(y2-y0)-(x2-x0)*(y1-y0)
        dist=(((x1-x0)**2+(y1-y0)**2)+
              ((x0-x2)**2+(y0-y2)**2)+
              ((x2-x1)**2+(y2-y1)**2))/3.

        if (abs(det) > dist/10000.):
            # Determinante darf nicht sehr klein sein. 
            xm=(((x1-x0)*(x1+x0)+(y1-y0)*(y1+y0))*(y2-y0)-
                ((x2-x0)*(x2+x0)+(y2-y0)*(y2+y0))*(y1-y0))/2./det
            ym=(((x2-x0)*(x2+x0)+(y2-y0)*(y2+y0))*(x1-x0)-
                ((x1-x0)*(x1+x0)+(y1-y0)*(y1+y0))*(x2-x0))/2./det
            r = ((xm - x1)**2 + (ym - y1)**2)**0.5
        else:
            return None

        # Anpassen der Koordinatengrenzen

        self.xmin = min(self.xmin, x1, x2)
        self.ymin = min(self.ymin, y1, y2)
        self.xmax = max(self.xmax, x1, x2)
        self.ymax = max(self.ymax, y1, y2)

        # Berücksichtung des äußeren Punktes der verbindenden Bogens

        xob, yob = xm, ym + r
        xli, yli = xm - r, ym
        xun, yun = xm, ym - r
        xre, yre = xm + r, ym

        # Nordpol
        if (xob - x1) * (y0 - yob) > (yob - y1) * (x0 - xob) or \
           (xob - x0) * (y2 - yob) > (yob - y0) * (x2 - xob):
            self.ymax = max(self.ymax, yob)

        # Westen
        if (xli - x1) * (y0 - yli) > (yli - y1) * (x0 - xli) or \
           (xli - x0) * (y2 - yli) > (yli - y0) * (x2 - xli):
            self.xmin = min(self.xmin, xli)
                
        # Süden
        if (xun - x1) * (y0 - yun) > (yun - y1) * (x0 - xun) or \
           (xun - x0) * (y2 - yun) > (yun - y0) * (x2 - xun):
            self.ymin = min(self.ymin, yun)

        # Osten
        if (xre - x1) * (y0 - yre) > (yre - y1) * (x0 - xre) or \
           (xre - x0) * (y2 - yre) > (yre - y0) * (x2 - xre):
            self.xmax = max(self.xmax, xre)


# ------------------------------------------------------------------------------
# Hauptprogramm

def importKanaldaten(dynafile, database_QKan, projectfile, epsg, check_copy_forms, check_tabinit, dbtyp = 'SpatiaLite'):

    '''Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :dynafile:              Datei mit den DYNA-Daten (*.EIN)
    :type database:         DBConnection (geerbt von firebirdsql...)

    :database_QKan:         Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database:         DBConnection (geerbt von dbapi...)

    :projectfile:           Pfad der Projektdatei zum Schreiben. Die Vorlage "projekt.qgs" aus dem 
                            template-Verzeichnis wird auf das in diesem Modul zu importierende Projekt 
                            angepasst und unter dem angegebenen Pfad gespeichert.
    :type projectfile:      String

    :epsg:                  EPSG-Nummer 
    :type epsg:             String

    :check_copy_forms:      Gibt an, ob das Verzeichnis "eingabemasken" aus dem template-Verzeichnis in das 
                            aktuelle Verzeichnis kopiert werden soll.
    :type check_copy_forms: Boolean

    :check_tabinit:         Gibt an, ob die QKan-Tabellen zu Beginn geleert werden sollen. 
    :type check_tabinit:    Boolean

    :dbtyp:                 Typ der Datenbank (SpatiaLite, PostGIS)
    :type dbtyp:            String

    :returns: void
    '''

    # Hilfsfunktionen
    # ------------------------------------------------------------------------------
    def zahl(text, n=0., default=0.):
        """Wandelt einen Text in eine Zahl um. Falls kein Dezimalzeichen
           enthalten ist, werden n Nachkommastellen angenommen"""
        zahl = text.strip()
        if zahl == '':
            return default
        elif '.' in zahl:
            try:
                return float(zahl)
            except BaseException as err:
                logger.error('10: {}'.format(err))
                return None
        else:
            return float(zahl) / 10. ** n


    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    dbQK = DBConnection(dbname=database_QKan, epsg=epsg)      # Datenbankobjekt der QKan-Datenbank zum Schreiben

    if dbQK is None:
        fehlermeldung(u"Fehler in QKan_Import_from_KP", 
                      u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        iface.messageBar().pushMessage(u"Fehler in QKan_Import_from_KP", 
                    u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
            database_QKan), level=QgsMessageBar.CRITICAL)
        return None

    # # Referenztabellen laden. 

    # # Profile. Attribut [profilnam] enthält die Bezeichnung des Benutzers. Dies kann auch ein Kürzel sein.
    # sql = u'SELECT kp_key, profilnam FROM profile'
    # if not dbQK.sql(sql, u'importkanaldaten_dyna (3)'):
        # return None
    # daten = dbQK.fetchall()
    # ref_profil = {}
    # for el in daten:
        # ref_profil[el[0]] = el[1]

    # # Entwässerungssystem. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
    # sql = u'SELECT kp_nr, bezeichnung FROM entwaesserungsarten'
    # if not dbQK.sql(sql, u'importkanaldaten_dyna (4)'):
        # return None
    # daten = dbQK.fetchall()
    # ref_entwart = {}
    # for el in daten:
        # ref_entwart[el[0]] = el[1]

    # # Simulationsstatus der Haltungen in Kanal++. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
    # sql = u'SELECT kp_nr, bezeichnung FROM simulationsstatus'
    # if not dbQK.sql(sql, u'importkanaldaten_dyna (5)'):
        # return None
    # daten = dbQK.fetchall()
    # ref_simstat = {}
    # for el in daten:
        # ref_simstat[el[0]] = el[1]

    # ref_kb = {}                # Wird aus der dyna-Datei gelesen

    # abflspendelis = {}             # Wird aus der dyna-Datei gelesen


    # ------------------------------------------------------------------------------
    # Vorverarbeitung der überhaupt nicht Datenbank kopatiblen Datenstruktur aus DYNA...

    # Einlesen der DYNA-Datei

    status_einw = False

    sqllist = [
        u"""CREATE TABLE IF NOT EXISTS dyna12 (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           ID INTEGER,
           IDob INTEGER,
           IDun INTEGER,
           kanalnummer TEXT,
           haltungsnummer TEXT,
           laenge REAL,
           deckeloben REAL,
           sohleoben REAL,
           sohleunten REAL,
           schdmoben REAL,
           material INTEGER,
           profil_key TEXT,
           hoehe REAL,
           ks_key INTEGER,
           flaeche REAL,
           flaecheund TEXT,
           flaechenid TEXT,
           neigkl INTEGER,
           entwart_nr INTEGER,
           simstatus_nr INTEGER,
           haeufigkeit INTEGER,
           typ INTEGER,
           schoben TEXT,
           schunten TEXT,
           xob REAL,
           yob REAL,
           strschluessel TEXT)""",
        u"""CREATE TABLE IF NOT EXISTS dyna41 (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           schnam TEXT,
           deckelhoehe REAL,
           xkoor REAL,
           ykoor REAL,
           kanalnummer TEXT,
           haltungsnummer TEXT)""",
        u"""CREATE TABLE IF NOT EXISTS dynarauheit (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           ks_key TEXT,
           ks REAL)""",
        u"""CREATE TABLE IF NOT EXISTS dynaprofil (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           profil_key TEXT,
           profilnam TEXT,
           breite REAL,
           hoehe REAL)"""]

    
    for sql in sqllist:
        if not dbQK.sql(sql, u'importkanaldaten_dyna create tab_typ12'):
            return None

    # Initialisierung von Parametern für die nachfolgende Leseschleife

    kanalnummer_vor = ''            # um bei doppelten Haltungsdatensätzen diese nur einmal zu lesen. 
    haltungnummer_vor = ''          # Erläuterung: Die doppelten Haltungsdatensätze tauchen in DYNA immer dann
                                    # auf, wenn mehrere Zuflüsse angegeben werden müssen. 

    # Initialisierungen für Profile
    profilmodus = -1       # -1: Nicht im Profilblock, Nächste Zeile ist bei:
                           #  0: Bezeichnung des gesamten Profile-Blocks. 
                           #  1: Profilname, Koordinaten, nächster Block oder Ende
                           #  2: Profilnr.
                           #  3: Erste Koordinaten des Querprofils

    x1 = y1 = None   # markiert, dass noch kein Profil eingelesen wurde (s. u.)

    for zeile in open(dynafile):
        if zeile[0:2] == '##':
            continue                # Kommentarzeile wird übersprungen

        # Zuerst werden Abschnitte mit besonderen Daten bearbeitet (Profildaten etc.)
        if profilmodus >= 0:
            if profilmodus == 0:
                # Bezeichnung des gesamten Profile-Blocks. Wird nicht weiter verwendet
                profilmodus = 1
                grenzen = rahmen()              # Grenzen-Objekt erstellen
                continue
            elif profilmodus == 2:
                # Profilnr.

                profil_key = zeile.strip()
                profilmodus = 3
                continue
            elif profilmodus == 3:
                # Erster Profilpunkt
                werte = zeile.strip()[1:-2].replace(')(',',').replace(')',',').split(',')
                if len(werte) != 2:
                    logger.error('Erste Zeile von Profil {} ist keine Punktkoordinate: {}'.format(
                        profilnam, zeile))
                xp, yp = [float(w) for w in werte]
                grenzen.reset(xp, yp)

                plmodus = 'Linie'  # Alternative: 'Kreis'
                profilmodus = 1
                x1, y1 = xp, yp             # Punkt als Startpunkt für nächstes Teilstück speichern
                continue
            elif profilmodus == 1:
                # weitere Profilpunkte, nächstes Profil oder Ende der Profile
                if zeile[0:1] == '(':
                    # profilmodus == 1, weitere Profilpunkte
                    werte = zeile.strip()[1:-2].replace(')(',',').replace(')',',').split(',')
                    nargs = len(werte)

                    if nargs == 2:
                        # Geradensegment
                        xp, yp = [float(w) for w in werte]
                        grenzen.line(x1, y1, xp, yp)            # Grenzen aktualisieren
                        x1, y1 = xp, yp                         # Punkt als Startpunkt für nächstes Teilstück speichern

                    elif nargs == 3:
                        # Polyliniensegment mit Radius und Endpunkt
                        xp, yp, radius = [float(w) for w in werte]
                        grenzen.line(x1, y1, xp, yp)            # Grenzen mit Stützstellen aktualisieren
                        grenzen.ppr(x1, y1, xp, yp, radius)     # Grenzen für äußeren Punkt des Bogens aktualisieren
                        x1, y1 = xp, yp                         # Punkt als Startpunkt für nächstes Teilstück speichern

                    elif nargs == 4:
                        # Polyliniensegment mit Punkt auf Bogen und Endpunkt
                        xm, ym, xp, yp = [float(w) for w in werte]
                        grenzen.line(x1, y1, xm, ym)            # Grenzen mit Stützstellen aktualisieren
                        grenzen.p(xp, yp)                       # Grenzen mit Stützstellen aktualisieren
                        grenzen.ppp(x1, y1, xm, ym, xp, yp)     # Grenzen für äußere Punkte des Bogens aktualisieren
                        x1, y1 = xp, yp                         # Punkt als Startpunkt für nächstes Teilstück speichern

                    continue
                else:
                    # Nächstes Profil oder Ende Querprofile (=Ende des aktuellen Profils)

                    # Beschriftung des Profils. Grund: Berechnung von Breite und Höhe ist erst nach
                    # Einlesen aller Profilzeilen möglich.

                    # Erst wenn das erste Profil eingelesen wurde
                    if x1 is not None:
                        # Höhe zu Breite-Verhältnis berechnen
                        breite = (grenzen.xmax - grenzen.xmin)/1000.
                        hoehe = (grenzen.ymax - grenzen.ymin)/1000.
                        sql = u'''INSERT INTO dynaprofil (profil_key, profilnam, breite, hoehe) 
                                      VALUES ('{key}', '{nam}', {br}, {ho})'''.format(
                                      key=profil_key, nam=profilnam, br=breite, ho=hoehe)
                        logger.debug(u'sql = {}'.format(sql))
                        if not dbQK.sql(sql, u'importkanaldaten_kp (1)'):
                            return None

                    if zeile[0:2] != '++':
                        # Profilname
                        profilnam = zeile.strip()
                        profilmodus = 2
                        continue
                    else:
                        # Ende Block Querprofile (es sind mehrere möglich!)
                        profilmodus = -1
                        x1 = y1 = None

        # Optionen und Daten
        if zeile[0:6] == u'++QUER':
            profilmodus = 0

        elif zeile[0:6] == u'++KANA' and not status_einw:
            status_einw = (u'EINW' in zeile)

        elif zeile[0:2] == u'05':
            ks_key = zeile[3:4].strip()
            abflspende = float('0'+zeile[10:20].strip())
            ks = float('0'+zeile[20:30].strip())

            sql = u'''INSERT INTO dynarauheit (ks_key, ks) 
                      Values ('{ks_key}', {ks})'''.format(
                      ks_key=ks_key, ks=ks)
            if not dbQK.sql(sql, u'importkanaldaten_kp (2)'):
                return None

        elif zeile[0:2] == u'12':

            n = 1
            kanalnummer = zeile[6:14].lstrip('0 ').replace(' ', '0');  n = 3  # wegen der merkwürdigen DYNA-Logik für Kanalnamen
            haltungsnummer = str(int('0' + zeile[14:17].strip()));  n = 4
            if (kanalnummer, haltungsnummer) != (kanalnummer_vor, haltungnummer_vor):
                kanalnummer_vor, haltungnummer_vor = kanalnummer, haltungsnummer        # doppelte Haltungen werden übersprungen, weil Flächen-
                                                                                        # daten z.Zt. nicht eingelesen werden. 
                try:
                    strschluessel = zeile[2:6].strip();  n = 2
                    laenge = zahl(zeile[17:24], 2);  n = 5
                    deckeloben = zahl(zeile[24:31], 3);  n = 6
                    sohleoben = zahl(zeile[31:38], 3);  n = 7
                    sohleunten = zahl(zeile[38:45], 3);  n = 8
                    material = zeile[45:46];  n = 9
                    profil_key = zeile[46:48].strip();  n = 10
                    hoehe = zahl(zeile[48:52], 0)/1000.;  n = 11
                    ks_key = zeile[52:53].strip();  n = 12
                    flaeche = zahl(zeile[71:76], 2) * 10000.;  n = 20
                    flaecheund = round(zahl(zeile[53:55]) / 100. * flaeche, 1);  n = 13
                    qgewerbeind = zeile[55:56].strip();  n = 14
                    qfremdind = zeile[56:57].strip();  n = 15
                    zuflussid = zeile[57:58];  n = 16
                    qzu = zahl(zeile[58:63], 1);  n = 17
                    if status_einw:
                        ew = zahl(zeile[63:66]);    n = 18
                    else:
                        ew = zahl(zeile[63:66]) * flaeche / 10000.
                    flaechenid = zeile[66:71];  n = 19
                    neigkl = int('0' + zeile[76:77].strip());  n = 21
                    entwart_nr = int('0' + zeile[77:78].strip());  n = 22
                    simstatus_nr = int('0' + zeile[78:79].strip());  n = 23
                    haeufigkeit = int('0' + zeile[80:81].strip());  n = 24
                    schoben = zeile[81:93].strip();  n = 25
                    schunten = zeile[94:106].strip();  n = 26
                    xob = zahl(zeile[106:120]);  n = 27
                    yob = zahl(zeile[120:134]);  n = 28
                    schdmoben = zahl(zeile[180:187])
                except BaseException as err:
                    fehlermeldung(u"Programmfehler",u"import_from_dyna.importKanaldaten (1)")
                    logger.error(u'12er: Wert Nr. {} - {}\nZeile: {}'.format(n, err, zeile))
                    del dbQK
                    return None

                try:
                    sql = u"""INSERT INTO dyna12
                    ( kanalnummer, haltungsnummer, schoben, schunten,
                      xob, yob, laenge, deckeloben, sohleoben, sohleunten,
                      material, profil_key, hoehe, ks_key, flaeche, flaecheund, neigkl,
                      entwart_nr, simstatus_nr, 
                      flaechenid, strschluessel, haeufigkeit, schdmoben)
                    VALUES ('{kanalnummer}', '{haltungsnummer}', '{schoben}', '{schunten}',
                      {xob}, {yob}, {laenge}, {deckeloben}, {sohleoben}, {sohleunten},
                      '{material}', '{profil_key}', {hoehe}, '{ks_key}', {flaeche}, {flaecheund}, {neigkl},
                      {entwart_nr}, {simstatus_nr},
                      '{flaechenid}', '{strschluessel}', {haeufigkeit}, {schdmoben})""".format(
                        kanalnummer=kanalnummer, haltungsnummer=haltungsnummer,
                        schoben=schoben, schunten=schunten, xob=xob, yob=yob,
                        laenge=laenge, deckeloben=deckeloben, sohleoben=sohleoben,
                        sohleunten=sohleunten, material=material, profil_key=profil_key,
                        hoehe=hoehe, ks_key=ks_key, flaeche=flaeche, flaecheund=flaecheund,
                        neigkl=neigkl, entwart_nr=entwart_nr, simstatus_nr=simstatus_nr,
                        flaechenid=flaechenid, strschluessel=strschluessel,
                        haeufigkeit=haeufigkeit, schdmoben=schdmoben)

                except BaseException as err:
                    logger.error('12er: {}\n{}'.format(err, zeile))
                if not dbQK.sql(sql, u'importkanaldaten_dyna import typ12'):
                    return None


        elif zeile[0:2] == u'41':

            try:
                n = 1
                kanalnummer = zeile[6:14].lstrip('0 ').replace(' ', '0');    n = 2  # wegen der eigenwilligen DYNA-Logik für Kanalnamen;
                haltungsnummer = zeile[14:17];    n = 3
                deckelhoehe = zahl(zeile[24:31],3);    n = 4
                xkoor = zahl(zeile[31:45],0);    n = 5
                ykoor = zahl(zeile[45:59],0);    n = 6
                schnam = zeile[59:71].strip();    n = 7
            except BaseException as err:
                logger.error(u'16er: Wert Nr. {} - {}\nZeile: {}'.format(n, err, zeile))
                return False

            try:
                sql = u"""INSERT INTO dyna41
                ( schnam, deckelhoehe, xkoor, ykoor, kanalnummer, haltungsnummer)
                VALUES ('{schnam}', {deckelhoehe}, {xkoor}, {ykoor}, 
                  '{kanalnummer}', '{haltungsnummer}')""".format(
                    schnam=schnam, deckelhoehe=deckelhoehe, xkoor=xkoor, ykoor=ykoor, 
                    kanalnummer=kanalnummer, haltungsnummer=haltungsnummer)

            except BaseException as err:
                logger.error(u'16er: {}\n{}'.format(err, zeile))
            if not dbQK.sql(sql, u'importkanaldaten_dyna typ16'):
                return None


    # ------------------------------------------------------------------------------
    # Profile aus DYNA-Datei in Tabelle profile ergänzen
    # 1. Bei Namenskonflikten mit bereits gespeicherten Profilen wird die kp_key auf NULL gesetzt

    sql = u'''UPDATE profile 
        SET kp_key = NULL
        WHERE profilnam IN 
        (   SELECT profilnam
            FROM dynaprofil
            WHERE profile.profilnam = dynaprofil.profilnam and profile.kp_key <> dynaprofil.profil_key)'''

    if not dbQK.sql(sql, 'importkanaldaten_dyna profile-1'):
        return None

    # 2. Neue Profile aus DYNA hinzufügen

    sql = u'''INSERT INTO profile 
        (profilnam, kp_key)
        SELECT profilnam, profil_key
        FROM dynaprofil
        WHERE profil_key not in 
        (   SELECT kp_key 
            FROM profile)'''

    if not dbQK.sql(sql, 'importkanaldaten_dyna profile-2'):
        return None


    # ------------------------------------------------------------------------------
    # Haltungsdaten

    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = """DELETE FROM haltungen"""
        if not dbQK.sql(sql, 'importkanaldaten_dyna (6)'):
            return None

    # Daten aUS temporären DYNA-Tabellen abfragen
    sql = u'''
        SELECT 
            printf('%s-%s', dyna12.kanalnummer, dyna12.haltungsnummer) AS haltnam, 
            dyna12.schoben AS schoben, 
            dyna12.schunten AS schunten, 
            dyna12.hoehe AS hoehe, 
            dyna12.hoehe*dynaprofil.breite/dynaprofil.hoehe AS breite, 
            dyna12.laenge AS laenge, 
            dyna12.sohleoben AS sohleoben, 
            dyna12.sohleunten AS sohleunten, 
            dyna12.deckeloben AS deckeloben, 
            coalesce(dy12un.deckeloben, dyna41.deckelhoehe) as deckelunten, 
            NULL as teilgebiet, 
            dynaprofil.profilnam as profilnam, 
            entwaesserungsarten.bezeichnung as entwart, 
            dynarauheit.ks as ks, 
            simulationsstatus.bezeichnung as simstatus, 
            'DYNA-Import' AS kommentar, 
            dyna12.xob as xob, 
            dyna12.yob as yob, 
            coalesce(dy12un.xob, dyna41.xkoor) as xun, 
            coalesce(dy12un.yob, dyna41.ykoor) as yun
        FROM dyna12
        LEFT JOIN dyna12 AS dy12un
        ON dyna12.schunten = dy12un.schoben
        LEFT JOIN dyna41
        ON dyna12.schunten = dyna41.schnam
        LEFT JOIN dynarauheit
        ON dyna12.ks_key = dynarauheit.ks_key
        LEFT JOIN dynaprofil
        ON dyna12.profil_key = dynaprofil.profil_key
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN entwaesserungsarten
        ON dyna12.entwart_nr = entwaesserungsarten.kp_nr
        GROUP BY dyna12.kanalnummer, dyna12.haltungsnummer'''

    if not dbQK.sql(sql, 'importkanaldaten_dyna (7)'):
        return None
    daten = dbQK.fetchall()

    # Haltungsdaten in die QKan-DB schreiben

    for attr in daten:
        (haltnam_ansi, schoben_ansi, schunten_ansi, hoehe, breite, laenge, sohleoben, sohleunten, 
        deckeloben, deckelunten, teilgebiet, profilnam, 
        entwart, ks, simstatus, kommentar, xob, yob, xun, yun) = \
            ['NULL' if el is None else el for el in attr]

        (haltnam, schoben, schunten) = \
          [tt.decode('iso-8859-1') for tt in (haltnam_ansi, schoben_ansi, schunten_ansi)]


        # Geo-Objekt erzeugen

        if dbtyp == 'SpatiaLite':
            geom = u'MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:}))'.format(xob, yob, xun, yun, epsg)
            logger.debug(u'geom = {}'.format(geom))
        elif dbtyp == 'postgis':
            geom = u'ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:}),{4:s}),ST_SetSRID(ST_MakePoint({2:},{3:}),{4:}))'.format(xob, yob, xun, yun, epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz aufbereiten in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO haltungen 
                (geom, haltnam, schoben, schunten, 
                hoehe, breite, laenge, sohleoben, sohleunten, 
                deckeloben, deckelunten, teilgebiet, profilnam, entwart, ks, simstatus, kommentar) VALUES (
                {geom}, '{haltnam}', '{schoben}', '{schunten}', {hoehe}, {breite}, {laenge}, 
                {sohleoben}, {sohleunten}, {deckeloben}, {deckelunten}, '{teilgebiet}', '{profilnam}', 
                '{entwart}', {ks}, '{simstatus}', '{kommentar}')""".format( \
                    geom=geom, haltnam=haltnam, schoben=schoben, schunten=schunten, hoehe=hoehe, 
                    breite=breite, laenge=laenge, sohleoben=sohleoben, sohleunten=sohleunten, 
                    deckeloben=deckeloben, deckelunten=deckelunten, teilgebiet=teilgebiet, 
                    profilnam=profilnam, entwart=entwart, ks=ks, simstatus=simstatus, kommentar=kommentar)
        except BaseException as e:
            fehlermeldung('SQL-Fehler', str(e))
            fehlermeldung("Fehler in QKan_Import_from_KP", u"\nFehler in sql INSERT INTO haltungen: \n" + \
                str((geom, haltnam, schoben, schunten, 
                hoehe, breite, laenge, sohleoben, sohleunten, 
                deckeloben, deckelunten, teilgebiet, profilnam, entwart, ks, simstatus)) + '\n\n')

        if not dbQK.sql(sql, 'importkanaldaten_dyna (9a)'):
            return None

    dbQK.commit()


    # ------------------------------------------------------------------------------
    # Schachtdaten


    # Tabelle in QKan-Datenbank leeren
    if check_tabinit:
        sql = u'DELETE FROM schaechte'
        if not dbQK.sql(sql, 'importkanaldaten_dyna (10)'):
            return None

    # Daten aus temporären DYNA-Tabellen abfragen
    sql = u'''
        SELECT 
            dyna12.schoben as schnam,
            dyna12.xob as xsch, 
            dyna12.yob as ysch, 
            dyna12.sohleoben as sohlhoehe, 
            dyna12.deckeloben as deckelhoehe, 
            1000 as durchm, 
            0 as druckdicht, 
            entwaesserungsarten.bezeichnung as entwart, 
            simulationsstatus.bezeichnung AS simstat, 
            'Importiert mit QKan' AS kommentar
        FROM dyna12
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN entwaesserungsarten
        ON dyna12.entwart_nr = entwaesserungsarten.kp_nr
        GROUP BY dyna12.schoben'''

    dbQK.sql(sql)
    daten = dbQK.fetchall()

    # Schachtdaten aufbereiten und in die QKan-DB schreiben

    for attr in daten:
        (schnam_ansi, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
            simstat, kommentar) = ['NULL' if el is None else el for el in attr]

        schnam = schnam_ansi.decode('iso-8859-1')

        # # Entwasserungsarten
        # if entwart_kp in ref_entwart:
            # entwart = ref_entwart[entwart_kp]
        # else:
            # # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergänzen
            # sql = u"INSERT INTO entwaesserungsarten (bezeichnung, kp_nr) Values ('({0:})', {0:d})".format(entwart_kp)
            # entwart = u'({:})'.format(entwart_kp)
            # if not dbQK.sql(sql, 'importkanaldaten_dyna (11)'):
                # return None

        # # Simstatus-Nr aus EIN-Datei ersetzten
        # if simstat_kp in ref_simstat:
            # simstatus = ref_simstat[simstat_kp]
        # else:
            # # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            # simstatus = u'({}_kp)'.format(simstat_kp)
            # sql = u"INSERT INTO simulationsstatus (bezeichnung, kp_nr) Values ('{simstatus}', {kp_nr})".format( \
                      # simstatus=simstatus, kp_nr=simstat_kp)
            # ref_simstat[simstat_kp] = simstatus
            # if not dbQK.sql(sql, 'importkanaldaten_dyna (12)'):
                # return None

        # Geo-Objekte erzeugen

        if dbtyp == 'SpatiaLite':
            geop = u'MakePoint({0:},{1:},{2:})'.format(xsch,ysch,epsg)
            geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch, 
                                             (1. if durchm == 'NULL' else durchm/ 1000.) , epsg)
        elif dbtyp == 'postgis':
            geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch,ysch,epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                              schachttyp, simstatus, kommentar, geop, geom)
            VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, {durchm}, {druckdicht}, '{entwart}', 
                     '{schachttyp}', '{simstatus}', '{kommentar}', 
                     {geop}, {geom})""".format( \
                     schnam=schnam, xsch=xsch, ysch=ysch, sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe, 
                     durchm=durchm, druckdicht=druckdicht, entwart=entwart, 
                     schachttyp = 'Schacht', simstatus=simstatus, 
                     kommentar=kommentar, geop=geop, geom=geom)
            if not dbQK.sql(sql, 'importkanaldaten_dyna (13)'):
                return None
        except BaseException as e:
            fehlermeldung('SQL-Fehler', str(e))
            fehlermeldung("Fehler in QKan_Import_from_KP", u"\nSchächte: in sql: \n" + sql + '\n\n')

    dbQK.commit()


    # ------------------------------------------------------------------------------
    # Auslässe


    # Daten aus temporären DYNA-Tabellen abfragen
    sql = u'''
        SELECT
            dyna41.schnam as schnam,
            dyna41.xkoor as xsch, 
            dyna41.ykoor as ysch, 
            dyna12.sohleunten as sohlhoehe, 
            dyna41.deckelhoehe as deckelhoehe, 
            1000 as durchm, 
            0 as druckdicht, 
            entwaesserungsarten.bezeichnung as entwart, 
            simulationsstatus.bezeichnung AS simstat, 
            'Importiert mit QKan' AS kommentar
        FROM dyna41
        LEFT JOIN dyna12
        ON dyna41.schnam = dyna12.schunten
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN entwaesserungsarten
        ON dyna12.entwart_nr = entwaesserungsarten.kp_nr'''

    dbQK.sql(sql)
    daten = dbQK.fetchall()

    # Auslassdaten aufbereiten und in die QKan-DB schreiben

    for attr in daten:
        (schnam_ansi, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
            simstat, kommentar) = ['NULL' if el is None else el for el in attr]

        schnam = schnam_ansi.decode('iso-8859-1')

        # # Entwasserungsarten
        # if entwart_kp in ref_entwart:
            # entwart = ref_entwart[entwart_kp]
        # else:
            # # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergänzen
            # sql = u"INSERT INTO entwaesserungsarten (bezeichnung, kp_nr) Values ('({0:})', {0:d})".format(entwart_kp)
            # entwart = u'({:})'.format(entwart_kp)
            # if not dbQK.sql(sql, 'importkanaldaten_dyna (14)'):
                # return None

        # # Simstatus-Nr aus EIN-Datei ersetzten
        # if simstat_kp in ref_simstat:
            # simstatus = ref_simstat[simstat_kp]
        # else:
            # # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
            # simstatus = u'({}_kp)'.format(simstat_kp)
            # sql = u"INSERT INTO simulationsstatus (bezeichnung, kp_nr) Values ('{simstatus}', {kp_nr})".format( \
                      # simstatus=simstatus, kp_nr=simstat_kp)
            # ref_simstat[simstat_kp] = simstatus
            # if not dbQK.sql(sql, 'importkanaldaten_dyna (15)'):
                # return None

        # Geo-Objekte erzeugen

        if dbtyp == 'SpatiaLite':
            geop = u'MakePoint({0:},{1:},{2:})'.format(xsch,ysch,epsg)
            geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch, 
                                             (1. if durchm == 'NULL' else durchm/ 1000.) , epsg)
        elif dbtyp == 'postgis':
            geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch,ysch,epsg)
        else:
            fehlermeldung('Programmfehler!', 
                'Datenbanktyp ist fehlerhaft {0:s}, Endung: {1:s}!\nAbbruch!'.format(dbtyp,dbdatabase[-7:].lower()))

        # Datensatz in die QKan-DB schreiben

        try:
            sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                              schachttyp, simstatus, kommentar, geop, geom)
            VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, {durchm}, {druckdicht}, '{entwart}', 
                     '{schachttyp}', '{simstatus}', '{kommentar}', 
                     {geop}, {geom})""".format( \
                     schnam=schnam, xsch=xsch, ysch=ysch, sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe, 
                     durchm=durchm, druckdicht=druckdicht, entwart=entwart, 
                     schachttyp = 'Auslass', simstatus=simstatus, 
                     kommentar=kommentar, geop=geop, geom=geom)
            if not dbQK.sql(sql, 'importkanaldaten_dyna (16)'):
                return None
        except BaseException as e:
            fehlermeldung('SQL-Fehler', str(e))
            fehlermeldung("Fehler in QKan_Import_from_KP", u"\nSchächte: in sql: \n" + sql + '\n\n')

    dbQK.commit()


    # ------------------------------------------------------------------------------
    # Schachttypen auswerten. Dies geschieht ausschließlich mit SQL-Abfragen

    # -- Anfangsschächte: Schächte ohne Haltung oben
    sql_typAnf = u'''
        UPDATE schaechte SET knotentyp = 'Anfangsschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte as t_sch 
        LEFT JOIN haltungen as t_hob
        ON t_sch.schnam = t_hob.schoben
        LEFT JOIN haltungen as t_hun
        ON t_sch.schnam = t_hun.schunten
        WHERE t_hun.pk IS NULL)'''

    # -- Endschächte: Schächte ohne Haltung unten
    sql_typEnd = u'''
        UPDATE schaechte SET knotentyp = 'Endschacht' WHERE schaechte.schnam IN
        (SELECT t_sch.schnam
        FROM schaechte as t_sch 
        LEFT JOIN haltungen as t_hob
        ON t_sch.schnam = t_hob.schunten
        LEFT JOIN haltungen as t_hun
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
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)>ifnull(t_hob.sohleoben,t_sob.sohlhoehe) and 
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
          WHERE ifnull(t_hob.sohleunten,t_sch.sohlhoehe)<ifnull(t_hob.sohleoben,t_sob.sohlhoehe) and 
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

    if not dbQK.sql(sql_typAnf, u'importkanaldaten_dyna (31)'):
        return None

    if not dbQK.sql(sql_typEnd, u'importkanaldaten_dyna (32)'):
        return None

    if not dbQK.sql(sql_typHoch, u'importkanaldaten_dyna (33)'):
        return None

    if not dbQK.sql(sql_typTief, u'importkanaldaten_dyna (34)'):
        return None

    if not dbQK.sql(sql_typZweig, u'importkanaldaten_dyna (35)'):
        return None

    if not dbQK.sql(sql_typEinzel, u'importkanaldaten_dyna (36)'):
        return None

    dbQK.commit()
    

    # --------------------------------------------------------------------------
    # Zoom-Bereich für die Projektdatei vorbereiten
    sql = u'''SELECT min(xsch) AS xmin, 
                    max(xsch) AS xmax, 
                    min(ysch) AS ymin, 
                    max(ysch) AS ymax
             FROM schaechte'''
    try:
        dbQK.sql(sql)
    except BaseException as e:
        fehlermeldung('SQL-Fehler', str(e))
        fehlermeldung("Fehler in QKan_Import_from_KP", u"\nFehler in sql_zoom: \n" + sql + '\n\n')

    daten = dbQK.fetchone()
    try:
        zoomxmin, zoomxmax, zoomymin, zoomymax = daten
    except BaseException as e:
        fehlermeldung('SQL-Fehler', str(e))
        fehlermeldung("Fehler in QKan_Import_from_KP", u"\nFehler in sql_zoom; daten= " + str(daten) + '\n')

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten
    sql = """SELECT srid
            FROM geom_cols_ref_sys
            WHERE Lower(f_table_name) = Lower('schaechte')
            AND Lower(f_geometry_column) = Lower('geom')"""
    if not dbQK.sql(sql, 'importkanaldaten_dyna (37)'):
        return None

    srid = dbQK.fetchone()[0]
    try:
        crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
        srsid = crs.srsid()
        proj4text = crs.toProj4()
        description = crs.description()
        projectionacronym = crs.projectionAcronym()
        if 'ellipsoidacronym' in dir(crs):
            ellipsoidacronym = crs.ellipsoidacronym()
        else:
            ellipsoidacronym = None
    except BaseException as e:
        srid, srsid, proj4text, description, projectionacronym, ellipsoidacronym = \
            'dummy', 'dummy', 'dummy', 'dummy', 'dummy', 'dummy'

        fehlermeldung('\nFehler in "daten"', str(e))
        fehlermeldung("Fehler in QKan_Import_from_KP", u"\nFehler bei der Ermittlung der srid: \n" + str(daten))


    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

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
        tabliste = ['schaechte', u'haltungen', u'pumpen', u'teilgebiete', u'einzugsgebiete', u'wehre', 
                     u'flaechen', u'tezg']

        # Lesen der Projektdatei ------------------------------------------------------------------
        qgsxml = ET.parse(projecttemplate)
        root = qgsxml.getroot()

        for tag_maplayer in root.findall(u".//projectlayers/maplayer"):

            # Nur QKan-Tabellen bearbeiten
            tag_datasource = tag_maplayer.find(u"./datasource")
            tex = tag_datasource.text
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

        for tag_extent in root.findall(u".//mapcanvas/extent"):
            elem = tag_extent.find(u"./xmin")
            elem.text = u'{:.3f}'.format(zoomxmin)
            elem = tag_extent.find(u"./ymin")
            elem.text = u'{:.3f}'.format(zoomymin)
            elem = tag_extent.find(u"./xmax")
            elem.text = u'{:.3f}'.format(zoomxmax)
            elem = tag_extent.find(u"./ymax")
            elem.text = u'{:.3f}'.format(zoomymax)

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

        for tag_datasource in root.findall(u".//projectlayers/maplayer/datasource"):
            text = tag_datasource.text
            tag_datasource.text = u"dbname='" + datasource + u"' " + text[text.find(u'table='):]

        qgsxml.write(projectfile)  # writing modified project file
        logger.debug(u'Projektdatei: {}'.format(projectfile))
        # logger.debug(u'encoded string: {}'.format(tex))

        if check_copy_forms:
            if u'eingabemasken' not in os.listdir(projectpath):
                os.mkdir(os.path.join(projectpath, u'eingabemasken'))
            formpath = os.path.join(projectpath, u'eingabemasken')
            formlist = os.listdir(formpath)
            templatepath = os.path.join(pluginDirectory('qkan'), u"database/templates")

            logger.debug(u"Eingabeformulare kopieren: {} -> {}".format(formpath, templatepath))

            for formfile in glob.iglob(os.path.join(templatepath, u'*.ui')):
                # Wenn Datei im Verzeichnis 'eingabemasken' noch nicht vorhanden ist
                if formfile not in formlist:
                    shutil.copy2(formfile, formpath)

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    
    
    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage("Information", "Datenimport ist fertig!", level=QgsMessageBar.INFO)
    QgsMessageLog.logMessage("\nFertig: Datenimport erfolgreich!", level=QgsMessageLog.INFO)

    # Importiertes Projekt laden
    project = QgsProject.instance()
    # project.read(QFileInfo(projectfile))
    project.read(QFileInfo(projectfile))         # read the new project file
    logger.debug('Geladene Projektdatei: {}'.format(project.fileName()))

