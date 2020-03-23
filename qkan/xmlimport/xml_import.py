# -*- coding: utf-8 -*-

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import *
from qgis.utils import iface
import re
import xml.etree.ElementTree as et

import math
import string
import tempfile
import os
import logging

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, meldung
import logging
from qgis.gui import QgsMessageBar
import locale
locale.setlocale(locale.LC_ALL, '')

from xml.etree.ElementTree import Element, SubElement, Comment, tostring

logger = logging.getLogger('QKan')

class M150XmlException(Exception):

    def __init_(self, value):
        self._value = value

    def str(self):
        return self._value


class Schacht(object):
    def __init__(
            self,
            schnam='',
            xsch=0.0,
            ysch=0.0,
            sohlhoehe=0.0,
            deckelhoehe=0.0,
            durchm=0.0,
            entwart='',
            knotentyp=0,
            simstatus=0,
            kommentar='',
            ):
        
        self._schnam = schnam
        self._xsch = xsch
        self._ysch = ysch
        self._sohlhoehe = sohlhoehe
        self._deckelhoehe = deckelhoehe
        self._entwart = entwart
        self._knotentyp = knotentyp
        self._durchm = durchm
        self._simstatus = simstatus
        self._kommentar = kommentar
        
    def schnam(self):
        return self._schnam

    def xsch(self):
        return self._xsch

    def ysch(self):
        return self._ysch

    def sohlhoehe(self):
        return self._sohlhoehe

    def deckelhoehe(self):
        return self._deckelhoehe

    def entwart(self):
        return self._entwart

    def knotentyp(self):
        return self._knotentyp

    def durchm(self):
        return self._durchm

    def simstatus(self):
        return self._simstatus

    def kommentar(self):
        return self._kommentar


class Haltung(object):
    def __init__(
            self,
            haltnam='',
            schoben='',
            schunten='',
            hoehe=0.0,
            breite=0.0,
            laenge=0.0,
            sohleoben=0.0,
            sohleunten=0.0,
            deckeloben=0.0,
            deckelunten=0.0,
            profilnam='',
            entwart='',
            ks=1.5,
            simstatus=0,
            kommentar='',
            xschob=0.0,
            yschob=0.0,
            xschun=0.0,
            yschun=0.0,
            ):

        self._haltnam = haltnam
        self._schoben = schoben
        self._schunten = schunten
        self._hoehe = hoehe
        self._breite = breite
        self._laenge = laenge
        self._sohleoben = sohleoben
        self._sohleunten = sohleunten
        self._deckeloben = deckeloben
        self._deckelunten = deckelunten
        self._profilnam = profilnam
        self._entwart = entwart
        self._ks = ks
        self._simstatus = simstatus
        self._kommentar = kommentar
        self._xschob = xschob
        self._yschob = yschob
        self._xschun = xschun
        self._yschun = yschun
        
    def haltnam(self):
        return self._haltnam

    def schoben(self):
        return self._schoben

    def schunten(self):
        return self._schunten

    def hoehe(self):
        return self._hoehe

    def breite(self):
        return self._breite

    def laenge(self):
        return self._laenge

    def sohleoben(self):
        return self._sohleoben

    def sohleunten(self):
        return self._sohleunten

    def deckeloben(self):
        return self._deckeloben

    def deckelunten(self):
        return self._deckelunten

    def profilnam(self):
        return self._profilnam

    def entwart(self):
        return self._entwart

    def ks(self):
        return self._ks

    def simstatus(self):
        return self._simstatus

    def kommentar(self):
        return self._kommentar

    def xschob(self):
        return self._xschob

    def yschob(self):
        return self._yschob

    def xschun(self):
        return self._xschun

    def yschun(self):
        return self._yschun


class Wehr(object):
    def __init__(
            self,
            wnam='',
            schoben='',
            schunten='',
            wehrtyp='',
            schwellenhoehe=0.0,
            kammerhoehe=0.0,
            laenge=0.0,
            uebeiwert=0.0,
            simstatus=0,
            kommentar='',
            xsch=0.0,
            ysch=0.0,
            ):
        
        self._wnam = wnam
        self._schoben = schoben
        self._schunten = schunten
        self._wehrtyp = wehrtyp
        self._schwellenhoehe = schwellenhoehe
        self._kammerhoehe = kammerhoehe
        self._laenge = laenge
        self._uebeiwert = uebeiwert
        self._simstatus = simstatus
        self._kommentar = kommentar
        self._xsch = xsch
        self._ysch = ysch
        
    def wnam(self):
        return self._wnam

    def schoben(self):
        return self._schoben

    def schunten(self):
        return self._schunten

    def wehrtyp(self):
        return self._wehrtyp

    def schwellenhoehe(self):
        return self._schwellenhoehe

    def kammerhoehe(self):
        return self._kammerhoehe

    def laenge(self):
        return self._laenge

    def uebeiwert(self):
        return self._uebeiwert

    def simstatus(self):
        return self._simstatus

    def kommentar(self):
        return self._kommentar

    def xsch(self):
        return self._xsch

    def ysch(self):
        return self._ysch


class Pumpe(object):
    def __init__(
            self,
            pnam='',
            schoben='',
            schunten='',
            pumpentyp=0,
            volanf=0.0,
            volges=0.0,
            sohle=0.0,
            steuersch='',
            einschalthoehe=0.0,
            ausschalthoehe=0.0,
            simstatus=0,
            kommentar='',
            xsch=0.0,
            ysch=0.0
            ):
        
        self._pnam = pnam
        self._schoben = schoben
        self._schunten = schunten
        self._pumpentyp = pumpentyp
        self._volanf = volanf
        self._volges = volges
        self._sohle = sohle
        self._steuersch = steuersch
        self._einschalthoehe = einschalthoehe
        self._ausschalthoehe = ausschalthoehe
        self._simstatus = simstatus
        self._kommentar = kommentar
        self._xsch = xsch
        self._ysch = ysch
        
    def pnam(self):
        return self._pnam

    def schoben(self):
        return self._schoben

    def schunten(self):
        return self._schunten

    def pumpentyp(self):
        return self._pumpentyp

    def volanf(self):
        return self._volanf

    def volges(self):
        return self._volges

    def sohle(self):
        return self._sohle

    def steuersch(self):
        return self._steuersch

    def einschalthoehe(self):
        return self._einschalthoehe

    def ausschalthoehe(self):
        return self._ausschalthoehe

    def simstatus(self):
        return self._simstatus

    def kommentar(self):
        return self._kommentar

    def xsch(self):
        return self._xsch

    def ysch(self):
        return self._ysch


class M150Xml(object):
    def __init__(self, file, dbQK, epsg, dbtyp='SpatiaLite'):
        """ Hier wird die Xml-Datei eingelesen und die Datenbank geöffnet

        :file:                  Übergebende Xml Datei
        :type file:             Xml

        :dbQK:                  Datenbankobjekt
        :type database:         DBConnection

        :xmlExportFile:         zu schreibende Xml Datei
        :type xmlExportFile:    Xml

        :epsg:                  EPSG-Nummer
        :type epsg:             String

        :dbtyp:                 Typ der Datenbank (SpatiaLite, PostGIS)
        :type dbtyp:            String

        """


        self.dbQK = dbQK
        self.epsg = epsg
        self.dbtyp = dbtyp
        self.namespaces = {'d': "http://www.ofd-hannover.la/Identifikation"}

        self.success = True

        file = unicode(file)


        data = et.ElementTree()
        data.parse(file)
        self._data = data

        root = data.getroot()

        # Referenztabellen laden. 

        # Entwässerungssystem. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
        self._ref_entwart = {}
        sql = u'SELECT he_nr, bezeichnung FROM entwaesserungsarten'
        if not self.dbQK.sql(sql, u'xml_import (1)'):
            return None
        daten = self.dbQK.fetchall()
        for el in daten:
            self._ref_entwart[el[0]] = el[1]

        # Pumpentypen. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
        self._ref_pumpentyp = {}
        sql = u'SELECT he_nr, bezeichnung FROM pumpentypen'
        if not self.dbQK.sql(sql, u'xml_import (2)'):
            return None
        daten = self.dbQK.fetchall()
        for el in daten:
            self._ref_pumpentyp[el[0]] = el[1]

        # Profile. Attribut [profilnam] enthält die Bezeichnung des Benutzers. Dies kann auch ein Kürzel sein.
        self._ref_profil = {}
        sql = u'SELECT he_nr, profilnam FROM profile'
        if not self.dbQK.sql(sql, u'xml_import (3)'):
            return None
        daten = self.dbQK.fetchall()
        for el in daten:
            self._ref_profil[el[0]] = el[1]

        # Auslasstypen.
        self._ref_auslasstypen = {}
        sql = u'SELECT he_nr, bezeichnung FROM auslasstypen'
        if not self.dbQK.sql(sql, u'xml_import (4)'):
            return None
        daten = self.dbQK.fetchall()
        for el in daten:
            self._ref_auslasstypen[el[0]] = el[1]

        # Simulationsstatus
        self.ref_simulationsstatus = {}
        sql = u'SELECT he_nr, bezeichnung FROM simulationsstatus'
        if not self.dbQK.sql(sql, u'xml_import (5)'):
            return None
        daten = self.dbQK.fetchall()
        for el in daten:
            self.ref_simulationsstatus[el[0]] = el[1]


    def schaechte(self):
        """Hier werden die Schacht Daten aus der Xml Datei ausgelesen"""

        schnam = ''
        xsch = 0.0
        ysch = 0.0
        sohlhoehe = 0.0
        deckelhoehe = 0.0
        durchm = 1.0
        entwart = ''
        knotentyp = 0
        simstatus = 0
        kommentar = ''


        schBlocks = self._data.findall(
            'd:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/d:Knoten/d:Schacht/../..', self.namespaces)
        # .//Schacht/../.. nimmt AbwassertechnischeAnlage

        meldung(u"",
                    u'Anzahl Schaechte: {:d}'.format(len(schBlocks)))
        # iface.messageBar().pushMessage(u"",
                                        # u'Anzahl Schaechte: {:d}'.format(len(schBlocks)), level=QgsMessageBar.INFO)

        for p in schBlocks:

            schnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)
            simstatus = p.findtext('d:Status', 'not found', self.namespaces)
            entwart = p.findtext('d:Entwaesserungsart', 'not found', self.namespaces)
            kommentar = p.findtext('d:Kommentar', 'not found', self.namespaces)

            schaechte1 = p.findall('d:Knoten', self.namespaces)
            for x in schaechte1:
                knotentyp = x.findtext('d:KnotenTyp', 'not found', self.namespaces)

            deckelhoehe = p.findtext("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe", '0', self.namespaces)

            schachtmittelpunkte = p.findall("d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='SMP']", self.namespaces)
            for smp in schachtmittelpunkte:
        
                cs = smp.findtext('d:Rechtswert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    xsch = float(cs)
                
                cs = smp.findtext('d:Hochwert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    ysch = float(cs)

                cs = smp.findtext('d:Punkthoehe', '0.0', self.namespaces)
                if not cs.strip() == '':
                    sohlhoehe = float(cs)

                break               # nur ein Datensatz
            else:
                fehlermeldung(u'Fehler in xml_import.schaechte', u'Keine Geometrie "SMP" für Schacht {}'.format(schnam))

            schacht = Schacht(schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, knotentyp, simstatus, kommentar)

            yield schacht


    def importSchaechte(self):
        """Hier werden die Schacht Daten in die Datenbank geschrieben"""

        for schacht in self.schaechte():
            schnam = schacht.schnam()
            xsch = schacht.xsch()
            ysch = schacht.ysch()
            sohlhoehe = schacht.sohlhoehe()
            deckelhoehe = schacht.deckelhoehe()
            entwart_imp = schacht.entwart()
            knotentyp = schacht.knotentyp()
            durchm = schacht.durchm()
            simstat_imp = schacht.simstatus()
            kommentar = schacht.kommentar()


            # Schachtdaten aufbereiten und in die QKan-DB schreiben

            # Entwasserungsarten

            if entwart_imp in self._ref_entwart:
                entwart = self._ref_entwart[entwart_imp]
            else:
                # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergänzen
                sql = u"INSERT INTO entwaesserungsarten (bezeichnung, kuerzel) Values ('{entwart_imp}', '{entwart_imp}')".format(
                    entwart_imp=entwart_imp)
                self._ref_entwart[entwart_imp] = entwart_imp
                entwart = u'{:}'.format(entwart_imp)
                if not self.dbQK.sql(sql, u'xml_import (6)'):
                    return None

            # Simstatus-Nr aus HE ersetzten
            if simstat_imp in self.ref_simulationsstatus:
                simstatus = self.ref_simulationsstatus[simstat_imp]
            else:
                # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergaenzen
                simstatus = u'{}_he'.format(simstat_imp)
                sql = u"INSERT INTO simulationsstatus (bezeichnung) Values ('{simstat_imp}')".format( \
                    simstat_imp=simstat_imp)
                self.ref_simulationsstatus[simstat_imp] = simstatus
                if not self.dbQK.sql(sql, u'xml_import (7)'):
                    return None


            # Geo-Objekte erzeugen

            if self.dbtyp == 'SpatiaLite':
                geop = u'MakePoint({0:},{1:},{2:})'.format(xsch,ysch,self.epsg)
                geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch,
                                                   float(durchm) / 1000., self.epsg)


            elif self.dbtyp == 'postgis':
                geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch,ysch,self.epsg)
            else:
                fehlermeldung('Programmfehler!', 
                    'Datenbanktyp ist fehlerhaft {0:s}\nAbbruch!'.format(self.dbtyp))
                return None

            # Datensatz in die QKan-DB schreiben

            try:
                sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, 
                                  schachttyp, simstatus, kommentar, geop, geom)
                VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, {durchm}, '{entwart}', 
                         '{schachttyp}', '{simstatus}', '{kommentar}', {geop}, {geom})""".format( \
                         schnam=schnam, xsch=xsch, ysch=ysch, sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe, 
                         durchm=durchm, entwart=entwart, schachttyp = 'Schacht', simstatus=simstatus,
                         kommentar=kommentar, geop=geop, geom=geom)
                if not self.dbQK.sql(sql, 'xml_import (8)'):
                    return None
            except BaseException as e:
                fehlermeldung('SQL-Fehler', str(e))
                fehlermeldung("Fehler in <", u"\nSchächte: in sql: \n" + sql + '\n\n')
                return None

        self.dbQK.commit()

        return True


    def auslaesse(self):
        """Hier werden die Auslass Daten aus der XML Datei ausgelesen"""

        schnam = ''
        xsch = 0.0
        ysch = 0.0
        sohlhoehe = 0.0
        deckelhoehe = 0.0
        durchm = 0.5
        entwart = ''
        knotentyp = 0
        simstatus = 0
        kommentar = ''


        auslBlocks = self._data.findall(
            'd:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/d:Knoten/d:Bauwerk/d:Auslaufbauwerk/../../..', 
            self.namespaces)
        # .//Auslaufbauwerk/../../.. nimmt AbwassertechnischeAnlage

        meldung(u"",
                    u'Anzahl Auslaeufe: {:d}'.format(len(auslBlocks)))
        # iface.messageBar().pushMessage(u"",
                                        # u'Anzahl Schaechte: {:d}'.format(len(auslBlocks)), level=QgsMessageBar.INFO)

        for p in auslBlocks:

            schnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)
            simstatus = p.findtext('d:Status', 'not found', self.namespaces)
            kommentar = p.findtext('d:Kommentar', 'not found', self.namespaces)

            schaechte1 = p.findall('d:Knoten', self.namespaces)
            for x in schaechte1:
                knotentyp = x.findtext('d:KnotenTyp', 'not found', self.namespaces)

            deckelhoehe = p.findtext(
                "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='GOK']/d:Punkthoehe", 
                '0', self.namespaces)

            schachtmittelpunkte = p.findall(
                "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='SMP']", self.namespaces)

            for smp in schachtmittelpunkte:
        
                cs = smp.findtext('d:Rechtswert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    xsch = float(cs)
                
                cs = smp.findtext('d:Hochwert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    ysch = float(cs)

                cs = smp.findtext('d:Punkthoehe', '0.0', self.namespaces)
                if not cs.strip() == '':
                    sohlhoehe = float(cs)

                break               # nur ein Datensatz
            else:
                fehlermeldung(u'Fehler in xml_import.auslaesse', u'Keine Geometrie "SMP" für Auslass {}'.format(schnam))

            schacht = Schacht(schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, knotentyp, simstatus, kommentar)

            yield schacht


    def importAuslaesse(self):
        """Hier werden die Auslass Daten in die Datenbank geschrieben"""

        for auslass in self.auslaesse():
            schnam = auslass.schnam()
            xsch = auslass.xsch()
            ysch = auslass.ysch()
            sohlhoehe = auslass.sohlhoehe()
            deckelhoehe = auslass.deckelhoehe()
            entwart = auslass.entwart()
            knotentyp = auslass.knotentyp()
            durchm = auslass.durchm()
            simstat_imp = auslass.simstatus()
            kommentar = auslass.kommentar()

            # Simstatus-Nr aus HE ersetzten
            if simstat_imp in self.ref_simulationsstatus:
                simstatus = self.ref_simulationsstatus[simstat_imp]
            else:
                # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergaenzen
                simstatus = u'{}_he'.format(simstat_imp)
                sql = u"INSERT INTO simulationsstatus (bezeichnung) Values ('{simstat_imp}')".format( \
                    simstat_imp=simstat_imp)
                self.ref_simulationsstatus[simstat_imp] = simstatus
                if not self.dbQK.sql(sql, u'xml_import (7)'):
                    return None


            # Geo-Objekte erzeugen

            if self.dbtyp == 'SpatiaLite':
                geop = u'MakePoint({0:},{1:},{2:})'.format(xsch,ysch,self.epsg)
                geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch,
                                                   float(durchm) / 1000., self.epsg)


            elif self.dbtyp == 'postgis':
                geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch,ysch,self.epsg)
            else:
                fehlermeldung('Programmfehler!', 
                    'Datenbanktyp ist fehlerhaft {0:s}\nAbbruch!'.format(self.dbtyp))
                return None

            # Datensatz in die QKan-DB schreiben

            try:
                sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, 
                                  schachttyp, simstatus, kommentar, geop, geom)
                VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, {durchm}, '{entwart}', 
                         '{schachttyp}', '{simstatus}', '{kommentar}', {geop}, {geom})""".format( \
                         schnam=schnam, xsch=xsch, ysch=ysch, sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe, 
                         durchm=durchm, entwart=entwart, schachttyp = 'Auslass', simstatus=simstatus,
                         kommentar=kommentar, geop=geop, geom=geom)
                if not self.dbQK.sql(sql, 'xml_import (8)'):
                    return None
            except BaseException as e:
                fehlermeldung('SQL-Fehler', str(e))
                fehlermeldung("Fehler in <", u"\nAuslässe: in sql: \n" + sql + '\n\n')
                return None

        self.dbQK.commit()

        return True



    def speicher(self):
        """Hier werden die Speicher Daten aus der XML Datei ausgelesen"""

        schnam = ''
        xsch = 0.0
        ysch = 0.0
        sohlhoehe = 0.0
        deckelhoehe = 0.0
        durchm = 0.5
        entwart = ''
        knotentyp = 0
        simstatus = 0
        kommentar = ''


        auslBlocks = self._data.findall(
            'd:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/d:Knoten/d:Bauwerk/d:Becken/../../..', 
            self.namespaces)
        # .//Becken/../../.. nimmt AbwassertechnischeAnlage

        meldung(u"",
                    u'Anzahl Becken: {:d}'.format(len(auslBlocks)))
        # iface.messageBar().pushMessage(u"",
                                        # u'Anzahl Schaechte: {:d}'.format(len(auslBlocks)), level=QgsMessageBar.INFO)

        for p in auslBlocks:

            schnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)
            simstatus = p.findtext('d:Status', 'not found', self.namespaces)
            kommentar = p.findtext('d:Kommentar', 'not found', self.namespaces)

            schaechte1 = p.findall('d:Knoten', self.namespaces)
            for x in schaechte1:
                knotentyp = x.findtext('d:KnotenTyp', 'not found', self.namespaces)

            deckelhoehe = p.findtext(
                "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='DMP']/d:Punkthoehe", 
                '0', self.namespaces)

            schachtmittelpunkte = p.findall(
                "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='KOP']", self.namespaces)

            for smp in schachtmittelpunkte:
        
                cs = smp.findtext('d:Rechtswert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    xsch = float(cs)
                
                cs = smp.findtext('d:Hochwert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    ysch = float(cs)

                cs = smp.findtext('d:Punkthoehe', '0.0', self.namespaces)
                if not cs.strip() == '':
                    sohlhoehe = float(cs)

                break               # nur ein Datensatz
            else:
                fehlermeldung(u'Fehler in xml_import.speicher', u'Keine Geometrie "KOP" für Becken {}'.format(schnam))

            schacht = Schacht(schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, knotentyp, simstatus, kommentar)

            yield schacht


    def importSpeicher(self):
        """Hier werden die Speicher Daten in die Datenbank geschrieben"""

        for speichbw in self.speicher():
            schnam = speichbw.schnam()
            xsch = speichbw.xsch()
            ysch = speichbw.ysch()
            sohlhoehe = speichbw.sohlhoehe()
            deckelhoehe = speichbw.deckelhoehe()
            entwart = speichbw.entwart()
            knotentyp = speichbw.knotentyp()
            durchm = speichbw.durchm()
            simstat_imp = speichbw.simstatus()
            kommentar = speichbw.kommentar()

            # Simstatus-Nr aus HE ersetzten
            if simstat_imp in self.ref_simulationsstatus:
                simstatus = self.ref_simulationsstatus[simstat_imp]
            else:
                # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergaenzen
                simstatus = u'{}_he'.format(simstat_imp)
                sql = u"INSERT INTO simulationsstatus (bezeichnung) Values ('{simstat_imp}')".format( \
                    simstat_imp=simstat_imp)
                self.ref_simulationsstatus[simstat_imp] = simstatus
                if not self.dbQK.sql(sql, u'xml_import (7)'):
                    return None


            # Geo-Objekte erzeugen

            if self.dbtyp == 'SpatiaLite':
                geop = u'MakePoint({0:},{1:},{2:})'.format(xsch,ysch,self.epsg)
                geom = u'CastToMultiPolygon(MakePolygon(MakeCircle({0:},{1:},{2:},{3:})))'.format(xsch, ysch,
                                                   float(durchm) / 1000., self.epsg)


            elif self.dbtyp == 'postgis':
                geop = u'ST_SetSRID(ST_MakePoint({0:},{1:}),{2:})'.format(xsch,ysch,self.epsg)
            else:
                fehlermeldung('Programmfehler!', 
                    'Datenbanktyp ist fehlerhaft {0:s}\nAbbruch!'.format(self.dbtyp))
                return None

            # Datensatz in die QKan-DB schreiben

            try:
                sql = u"""INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, entwart, 
                                  schachttyp, simstatus, kommentar, geop, geom)
                VALUES ('{schnam}', {xsch}, {ysch}, {sohlhoehe}, {deckelhoehe}, {durchm}, '{entwart}', 
                         '{schachttyp}', '{simstatus}', '{kommentar}', {geop}, {geom})""".format( \
                         schnam=schnam, xsch=xsch, ysch=ysch, sohlhoehe=sohlhoehe, deckelhoehe=deckelhoehe, 
                         durchm=durchm, entwart=entwart, schachttyp = 'Speicher', simstatus=simstatus,
                         kommentar=kommentar, geop=geop, geom=geom)
                if not self.dbQK.sql(sql, 'xml_import (8)'):
                    return None
            except BaseException as e:
                fehlermeldung('SQL-Fehler', str(e))
                fehlermeldung("Fehler in <", u"\nSpeicher: in sql: \n" + sql + '\n\n')
                return None

        self.dbQK.commit()

        return True



    def haltungen(self):
        """Hier werden die Haltungs Daten aus der XML Datei ausgelesen"""

        haltnam = ''
        schoben = ''
        schunten = ''
        hoehe = 0.0
        breite = 0.0
        laenge = 0.0                    # in Hydraulikdaten enthalten. 
        sohleoben = 0.0
        sohleunten = 0.0
        deckeloben = 0.0
        deckelunten = 0.0
        profilnam = ''
        entwart = ''
        ks = 1.5                        # in Hydraulikdaten enthalten. 
        simstatus = 0
        kommentar = ''
        xschob = 0.0
        yschob = 0.0
        xschun = 0.0
        yschun = 0.0

        halBlocks = self._data.findall('d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/d:Kante/d:Haltung/../..', self.namespaces)
        meldung(u"",
                    u'Anzahl Haltungen: {:d}'.format(len(halBlocks)))
        # iface.messageBar().pushMessage(u"",
                                        # u'Anzahl Haltungen: {:d}'.format(len(halBlocks)), level=QgsMessageBar.INFO)

        for p in halBlocks:
            
            haltnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)

            simstat_imp = p.findtext('d:Status', 'not found', self.namespaces)

            # Simstatus-Nr aus HE ersetzten
            if simstat_imp in self.ref_simulationsstatus:
                simstatus = self.ref_simulationsstatus[simstat_imp]
            else:
                # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergaenzen
                simstatus = u'{}_he'.format(simstat_imp)
                sql = u"INSERT INTO simulationsstatus (bezeichnung) Values ('{simstat_imp}')".format( \
                    simstat_imp=simstat_imp)
                self.ref_simulationsstatus[simstat_imp] = simstatus
                if not self.dbQK.sql(sql, u'xml_import (10)'):
                    break

            entwart_imp = p.findtext('d:Entwaesserungsart', 'not found', self.namespaces)

            # Entwasserungsart aus HE ersetzen
            if entwart_imp in self._ref_entwart:
                entwart = self._ref_entwart[entwart_imp]
            else:
                # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergänzen
                sql = u"INSERT INTO entwaesserungsarten (bezeichnung, kuerzel) Values ('{entwart_imp}', '{entwart_imp}')".format(
                    entwart_imp=entwart_imp)
                self._ref_entwart[entwart_imp] = entwart_imp
                entwart = u'{:}'.format(entwart_imp)
                if not self.dbQK.sql(sql, u'xml_import (9)'):
                    break


            kommentar =p.findtext('d:Kommentar', 'not found', self.namespaces)

            
            haltungen0 = p.findall('d:Kante/d:KantenTyp/..', self.namespaces)
            for x in haltungen0:
            
                schoben = x.findtext('d:KnotenZulauf', 'not found', self.namespaces)
                schunten = x.findtext('d:KnotenAblauf', 'not found', self.namespaces)

                
                cs = x.findtext('d:SohlhoeheZulauf', '0.0', self.namespaces)
                if not cs.strip() == '':
                    sohleoben = float(cs)
                    
                cs = x.findtext('d:SohlhoeheAblauf', '0.0', self.namespaces)
                if not cs.strip() == '':
                    sohleunten = float(cs)


                cs = x.findtext('d:Laenge', '0.0', self.namespaces)
                if not cs.strip() == '':
                    laenge = float(cs)


                haltungen1 = x.findall('d:Profil', self.namespaces)
                for x in haltungen1:
            
                    profilnam = x.findtext('d:Profilart', 'not found', self.namespaces)
            
                    cs = x.findtext('d:Profilhoehe', '0.0', self.namespaces)
                    if not cs.strip() == '':
                        hoehe = float(cs)/1000.
                    
                    cs = x.findtext('d:Profilbreite', '0.0', self.namespaces)
                    if not cs.strip() == '':
                        breite = float(cs)/1000.


            haltungen3 = p.findall('d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Start', self.namespaces)
            for x in haltungen3:
                
                cs = x.findtext('d:Rechtswert', '0.0', self.namespaces)
                if not cs.strip() == '':
                       xschob = float(cs)
                
                cs = x.findtext('d:Hochwert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    yschob = float(cs)
                    
                cs = x.findtext('d:Punkthoehe', '0.0', self.namespaces)
                if not cs.strip() == '':
                    deckeloben = float(cs)


            haltungen4 = p.findall('d:Geometrie/d:Geometriedaten/d:Kanten/d:Kante/d:Ende', self.namespaces)
            for x in haltungen4:
                
                cs = x.findtext('d:Rechtswert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    xschun = float(cs)
                
                cs = x.findtext('d:Hochwert', '0.0', self.namespaces)
                if not cs.strip() == '':
                    yschun = float(cs)
                    
                cs = x.findtext('d:Punkthoehe', '0.0', self.namespaces)
                if not cs.strip() == '':
                    deckelunten = float(cs)

            haltung = Haltung(haltnam, schoben, schunten, hoehe, breite, laenge, sohleoben, 
                              sohleunten, deckeloben, deckelunten, profilnam, entwart, ks, 
                              simstatus, kommentar, xschob, yschob, xschun, yschun)
            yield haltung


    def haltungen_hydraulik(self):
        """Hier werden die hydraulischen Haltungs Daten aus der Xml Datei ausgelesen"""

        haltnam = ''
        schoben = ''                    # in Haltungsdaten enthalten
        schunten = ''                   # in Haltungsdaten enthalten
        hoehe = 0.0                     # in Haltungsdaten enthalten
        breite = 0.0                    # in Haltungsdaten enthalten
        laenge = 0.0
        sohleoben = 0.0                 # in Haltungsdaten enthalten
        sohleunten = 0.0                # in Haltungsdaten enthalten
        deckeloben = 0.0                # in Haltungsdaten enthalten
        deckelunten = 0.0               # in Haltungsdaten enthalten
        profilnam = ''                  # in Haltungsdaten enthalten
        entwart = ''                    # in Haltungsdaten enthalten
        ks = 1.5
        simstatus = 0                   # in Haltungsdaten enthalten
        kommentar = ''                  # in Haltungsdaten enthalten
        xschob = 0.0                    # in Haltungsdaten enthalten
        yschob = 0.0                    # in Haltungsdaten enthalten
        xschun = 0.0                    # in Haltungsdaten enthalten
        yschun = 0.0                    # in Haltungsdaten enthalten

        hydBlocks = self._data.findall('d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/d:HydraulikObjekte/d:HydraulikObjekt/d:Haltung/..', self.namespaces)
        meldung(u"",
                      u'Anzahl HydraulikObjekte_Haltungen: {:d}'.format(len(hydBlocks)))

        # iface.messageBar().pushMessage(u"",
                                       # u'Anzahl HydraulikObjekt_Haltungen: {:d}'.format(len(hydBlocks)), level=QgsMessageBar.INFO)

        for p in hydBlocks:

            haltnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)

            #RauigkeitsbeiwertKst nach Manning-Strickler oder RauigkeitsbeiwertKb nach Prandtl-Colebrook?
            halt = p.findall('d:Haltung', self.namespaces)
            for x in halt:

                cs1 = x.findtext('d:Rauigkeitsansatz', '0', self.namespaces)
                if cs1 == '1':
                    cs2 = x.findtext('d:RauigkeitsbeiwertKb', '0.0', self.namespaces)
                elif cs1 == '2':
                    cs2 = x.findtext('d:RauigkeitsbeiwertKst', '0.0', self.namespaces)
                else:
                    fehlermeldung(u'Fehler in xml_import.haltungen_hydraulik', 
                                  u'Ungültiger Wert für Rauigkeitsansatz: {}'.format(cs1))

                    cs2 = '0.0'
                if not cs2.strip() == '':
                    ks = float(cs2)

                cs = x.findtext('d:Berechnungslaenge', '0.0', self.namespaces)   #Modelllänge des Objektes in hydraulischen Berechnungsprogrammen
                if not cs.strip() == '':
                    laenge = float(cs)

            haltung = Haltung(haltnam, schoben, schunten, hoehe, breite, laenge, sohleoben, 
                              sohleunten, deckeloben, deckelunten, profilnam, entwart, ks, 
                              simstatus, kommentar, xschob, yschob, xschun, yschun)
            yield haltung


    def importHaltungen(self):
        """Hier werden die Haltungs Daten in die Datenbank geschrieben"""

        # 1. Teil: Hier werden die Stammdaten zu den Haltungen in die Datenbank geschrieben

        for haltung in self.haltungen():
            haltnam = haltung.haltnam()
            schoben = haltung.schoben()
            schunten = haltung.schunten()
            hoehe = haltung.hoehe()
            breite = haltung.breite()
            laenge = haltung.laenge()                                   # in Hydraulikdaten + Stammdaten enthalten.
            sohleoben = haltung.sohleoben()
            sohleunten = haltung.sohleunten()
            deckeloben = haltung.deckeloben()
            deckelunten = haltung.deckelunten()
            profilnam = haltung.profilnam()
            entwart = haltung.entwart()
            ks = 0                                          # in Hydraulikdaten enthalten.
            simstatus = haltung.simstatus()
            kommentar = haltung.kommentar()
            xschob = haltung.xschob()
            yschob = haltung.yschob()
            xschun = haltung.xschun()
            yschun = haltung.yschun()

            # Haltungsdaten aufbereiten und in die QKan-DB schreiben

            # Geo-Objekt erzeugen

            if self.dbtyp == 'SpatiaLite':
                geom = u'MakeLine(MakePoint({0:},{1:},{4:s}),MakePoint({2:},{3:},{4:}))'.format(xschob, yschob, xschun, yschun, self.epsg)
            elif self.dbtyp == 'postgis':
                geom = u'ST_MakeLine(ST_SetSRID(ST_MakePoint({0:},{1:},{4:s}),ST_SetSRID(ST_MakePoint({2:},{3:}),{4:}))'.format(
                    xschob, yschob, xschun, yschun, self.epsg)
            else:
                fehlermeldung('Programmfehler!', 
                    'Datenbanktyp ist fehlerhaft {0:s}\nAbbruch!'.format(self.dbtyp))
                return None

            # Datensatz aufbereiten in die QKan-DB schreiben

            try:
                sql = u"""INSERT INTO haltungen 
                    (geom, haltnam, schoben, schunten, 
                    hoehe, breite, laenge, sohleoben, sohleunten, deckeloben, deckelunten, 
                    profilnam, entwart, ks, simstatus, kommentar, xschob, xschun, yschob, yschun) VALUES (
                    {geom}, '{haltnam}', '{schoben}', '{schunten}', {hoehe}, {breite}, {laenge}, {sohleoben}, {sohleunten}, 
                    {deckeloben}, {deckelunten}, '{profilnam}', '{entwart}', {ks}, '{simstatus}', '{kommentar}', 
                    '{xschob}', '{xschun}', '{yschob}', '{yschun}')""".format(
                    geom=geom, haltnam=haltnam, schoben=schoben, schunten=schunten, hoehe=hoehe,
                    breite=breite, laenge=laenge, sohleoben=sohleoben, sohleunten=sohleunten,
                    deckeloben=deckeloben, deckelunten=deckelunten, profilnam=profilnam, entwart=entwart, ks=ks,
                    simstatus=simstatus, kommentar=kommentar, xschob=xschob, xschun=xschun, yschob=yschob, yschun=yschun)

                if not self.dbQK.sql(sql, 'xml_import (11)'):
                    return None

            except BaseException as err:
                fehlermeldung(u'SQL-Fehler', repr(err))
                fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql INSERT INTO haltungen: \n" + \
                              str((geom, haltnam, schoben, schunten,
                                   hoehe, breite, laenge, sohleoben, sohleunten,
                                   deckeloben, deckelunten, profilnam, entwart, ks, simstatus)) + u'\n\n')
                return None

        self.dbQK.commit()

        return True


        # 2. Teil: Hier werden die hydraulischen Haltungs Daten in die Datenbank geschrieben

        for haltung in self.haltungen_hydraulik():
            haltnam = haltung.haltnam()
            ks = haltung.ks()
            laenge = haltung.laenge()

            try:
                sql = u"""UPDATE haltungen
                            SET ks = {ks},
                            laenge = {laenge}
                            WHERE haltnam = '{haltnam}'
                            """.format(ks=ks, laenge=laenge, haltnam=haltnam)

                if not self.dbQK.sql(sql, 'xml_import (13)'):
                    return None

            except BaseException as err:
                fehlermeldung(u'SQL-Fehler', repr(err))
                fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql INSERT INTO haltungen: \n" + \
                              str(( ks, laenge, haltnam)) + u'\n\n')
                return None

            if not self.dbQK.sql(sql, u'xml_import (14)'):
                return None

        self.dbQK.commit()

        return True



    def wehre_hydraulik(self):
        """Hier werden die hydraulischen Wehr Daten aus der Xml Datei ausgelesen"""

        wnam = ''
        schoben = ''
        schunten = ''
        wehrtyp = ''
        schwellenhoehe = 0.0
        kammerhoehe = 0.0
        laenge = 0.0
        uebeiwert = 0.0
        simstatus = 0
        kommentar = ''

        hydBlocks = self._data.findall('d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/d:HydraulikObjekte/d:HydraulikObjekt/d:Wehr/..', self.namespaces)
        meldung(u"",
                u'Anzahl HydraulikObjekte_Wehre: {:d}'.format(len(hydBlocks)))

        # iface.messageBar().pushMessage(u"",
                                       # u'Anzahl HydraulikObjekt_Wehre: {:d}'.format(len(hydBlocks)), level=QgsMessageBar.INFO)

        for p in hydBlocks:
            wnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)

            wehr1 = p.findall('d:Wehr', self.namespaces)
            for x in wehr1:
                schoben = x.findtext('d:SchachtZulauf', 'not found', self.namespaces)
                schunten = x.findtext('d:SchachtAblauf', 'not found', self.namespaces)
                wehrtyp = x.findtext('d:WehrTyp', 'not found', self.namespaces)

                cs = x.findtext('d:Schwellenhoehe', '0.0',self.namespaces)
                if not cs.strip() == '':
                    schwellenhoehe = float(cs)

                cs = x.findtext('d:LaengeWehrschwelle', '0.0',self.namespaces)
                if not cs.strip() == '':
                    laenge = float(cs)

                cs = x.findtext('d:Kammerhoehe', '0.0',self.namespaces)
                if not cs.strip() == '':
                    kammerhoehe = float(cs)

                cs = x.findtext('d:Ueberfallbeiwert', '0.0',self.namespaces)        #Überfallbeiwert der Wehr Kante (abhängig von Form der Kante)
                if not cs.strip() == '':
                    uebeiwert = float(cs)


            wehr = Wehr(wnam, schoben, schunten, wehrtyp, schwellenhoehe, kammerhoehe, laenge, uebeiwert,
                        simstatus, kommentar)
            yield wehr


    def importWehre(self):
        """Hier werden die Wehr Daten in die Datenbank geschrieben"""

        # Hier werden die Hydraulikdaten zu den Wehren in die Datenbank geschrieben. 
        # Bei Wehren stehen alle wesentlichen Daten im Hydraulikdatenkollektiv, weshalb im Gegensatz zu den 
        # Haltungsdaten keine Stammdaten verarbeitet werden. 

        for wehr in self.wehre_hydraulik():
            wnam = wehr.wnam()
            schoben = wehr.schoben()
            schunten = wehr.schunten()
            wehrtyp = wehr.wehrtyp()
            schwellenhoehe = wehr.schwellenhoehe()
            kammerhoehe = wehr.kammerhoehe()
            laenge = wehr.laenge()
            uebeiwert = wehr.uebeiwert()
            simstatus = 0
            kommentar = ''

            # Abhängig von der Datenbank unterscheidet sich die Syntax zur Erzeugung des Geo-Objektes

            if self.dbtyp == 'SpatiaLite':
                geom = u'''MakeLine(MakePoint(SCHOB.xsch, SCHOB.ysch, {epsg}), MakePoint(SCHUN.xsch, SCHUN.ysch, {epsg}))'''.format(
                    epsg=self.epsg)
            elif self.dbtyp == 'postgis':
                geom = u'''ST_MakeLine(ST_SetSRID(ST_MakePoint(SCHOB.xsch, SCHOB.ysch, {epsg}),
                                           ST_SetSRID(ST_MakePoint(SCHUN.xsch, SCHUN.ysch, {epsg}))'''.format(
                    self.epsg)
            else:
                fehlermeldung('Programmfehler!', 
                    'Datenbanktyp ist fehlerhaft {0:s}\nAbbruch!'.format(self.dbtyp))
                return None

            # Bei den Wehren muessen im Gegensatz zu den Haltungen die Koordinaten aus den Schachtdaten entnommen werden. 
            # Dies ist in QKan einfach, da auch Auslaesse und Speicher in der Tabelle "schaechte" gespeichert werden. 

            try:
                sql = u"""  INSERT INTO wehre 
                                (wnam, schoben, schunten, wehrtyp, schwellenhoehe, kammerhoehe, laenge, uebeiwert, geom)
                            SELECT '{wnam}', '{schoben}', '{schunten}', '{wehrtyp}', {schwellenhoehe}, 
                                {kammerhoehe}, {laenge}, {uebeiwert}, {geom}
                            FROM schaechte AS SCHOB,
                                schaechte AS SCHUN
                            WHERE SCHOB.schnam = '{schoben}' AND SCHUN.schnam = '{schunten}'""".format(
                                            wnam=wnam, schoben=schoben, schunten=schunten, wehrtyp=wehrtyp, 
                                            schwellenhoehe=schwellenhoehe, kammerhoehe=kammerhoehe, 
                                            laenge=laenge, uebeiwert=uebeiwert, geom=geom)

                if not self.dbQK.sql(sql, 'xml_import (15)'):
                    return None

            except BaseException as err:
                fehlermeldung(u'SQL-Fehler', repr(err))
                fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql INSERT INTO wehre: \n" + \
                              str((uebeiwert, laenge, wnam, schoben, schunten, kammerhoehe, schwellenhoehe)) + u'\n\n')
                return None

        self.dbQK.commit()

        return True


    def pumpen_hydraulik(self):
        """Hier werden die hydraulischen Pumpen Daten aus der Xml Datei ausgelesen"""

        pnam = ''
        schoben = ''
        schunten = ''
        pumpentyp = 0
        volanf = 0.0
        volges = 0.0
        sohle = 0.0
        steuersch = ''
        einschalthoehe = 0.0
        ausschalthoehe = 0.0
        simstatus = 0
        kommentar = ''
        #xsch = 0.0  # (nicht in ISYBAU enthalten: muss aus Mittelwert von schoben und schunten berechnet werden)
        #ysch = 0.0

        hydBlocks = self._data.findall('d:Datenkollektive/d:Hydraulikdatenkollektiv/d:Rechennetz/d:HydraulikObjekte/d:HydraulikObjekt/d:Pumpe/..', self.namespaces)
        meldung(u"",
                u'Anzahl HydraulikObjekte_Pumpen: {:d}'.format(len(hydBlocks)))

        # iface.messageBar().pushMessage(u"",
                                       # u'Anzahl HydraulikObjekt_Pumpen: {:d}'.format(len(hydBlocks)),
                                       # level=QgsMessageBar.INFO)

        for p in hydBlocks:
            pnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)

            hyd = p.findall('d:Pumpe', self.namespaces)
            for x in hyd:
                pumpentyp_imp = x.findtext('d:PumpenTyp', 'not found', self.namespaces)

                # Pumpentyp-Nr aus HE ersetzten
                if pumpentyp_imp in self._ref_pumpentyp:
                    pumpentyp = self._ref_pumpentyp[pumpentyp_imp]
                else:
                    # Noch nicht in Tabelle [pumpentyp] enthalten, also ergaenzen
                    pumpentyp = u'{}_he'.format(pumpentyp_imp)
                    sql = u"INSERT INTO pumpentypen (bezeichnung) Values ('{pumpentyp_imp}')".format( \
                        pumpentyp_imp=pumpentyp_imp)
                    self._ref_pumpentyp[pumpentyp_imp] = pumpentyp
                    if not self.dbQK.sql(sql, u'xml_import (21)'):
                        break

                schoben = x.findtext('d:SchachtZulauf', 'not found', self.namespaces)
                schunten = x.findtext('d:SchachtAblauf', 'not found', self.namespaces)
                steuersch = x.findtext('d:Steuerschacht', 'not found', self.namespaces)
                sohle = x.findtext('d:Sohlhoehe', '0.0', self.namespaces)
                volanf = x.findtext('d:Anfangsvolumen', '0.0', self.namespaces)
                volges = x.findtext('d:Gesamtvolumen', '0.0', self.namespaces)

            pumpe = Pumpe(pnam, schoben, schunten, pumpentyp, volanf, volges, sohle, steuersch, einschalthoehe,
                          ausschalthoehe, simstatus, kommentar)
            yield pumpe


    def pumpen(self):
        """Hier werden die Pumpen Daten aus der Xml Datei ausgelesen"""

        pnam = ''                           # //HydraulikObjekt[Pumpe]/Objektbezeichnung (Redundant: //HydraulikObjekt[HydObjektTyp='4'])
        schoben = ''                        # //HydraulikObjekt/Pumpe/SchachtZulauf
        schunten = ''                       # //HydraulikObjekt/Pumpe/SchachtAblauf
        pumpentyp = ''                      # //HydraulikObjekt/Pumpe/PumpenTyp
        volanf = 0.0                        # //HydraulikObjekt/Pumpe/Anfangsvolumen
        volges = 0.0                        # //HydraulikObjekt/Pumpe/Gesamtvolumen
        sohle = 0.0                         # //HydraulikObjekt/Pumpe/Sohlhoehe
        steuersch = ''                      # //HydraulikObjekt/Pumpe/Steuerschacht
        einschalthoehe = 0.0                # (nicht in ISYBAU enthalten)   bitte prüfen, ob in XSD doch drin
        ausschalthoehe = 0.0                # (nicht in ISYBAU enthalten)   bitte prüfen, ob in XSD doch drin
        simstatus = 0                       # //AbwassertechnischeAnlage[Knoten/Bauwerk/Pumpe]/Status
        kommentar = ''                      # //HydraulikObjekt[Pumpe]/Kommentar


        pumpBlocks = self._data.findall('d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/d:Knoten/d:Bauwerk/d:Pumpe/../../..', self.namespaces)
        meldung(u"", u'Anzahl Pumpen: {:d}'.format(len(pumpBlocks)))
        # iface.messageBar().pushMessage(u"",
                                        # u'Anzahl Pumpen: {:d}'.format(len(pumpBlocks)), 
                                        # level=QgsMessageBar.INFO)

        for p in pumpBlocks:
            pnam = p.findtext('d:Objektbezeichnung', 'not found', self.namespaces)
            simstat_imp = p.findtext('d:Status', 'not found', self.namespaces)

            # Simstatus-Nr aus HE ersetzten
            if simstat_imp in self.ref_simulationsstatus:
                simstatus = self.ref_simulationsstatus[simstat_imp]
            else:
                # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergaenzen
                simstatus = u'{}_he'.format(simstat_imp)
                sql = u"INSERT INTO simulationsstatus (bezeichnung) Values ('{simstat_imp}')".format( \
                    simstat_imp=simstat_imp)
                self.ref_simulationsstatus[simstat_imp] = simstatus
                if not self.dbQK.sql(sql, u'xml_import (20)'):
                    break


            kommentar = p.findtext('d:Kommentar', 'not found', self.namespaces)

            #pumpen0 = p.findall('d:Pumpe', self.namespaces)
            #for x in pumpen0:
            #    pumpentyp_imp = x.findtext('d:PumpenTyp', 'not found', self.namespaces)

                # Pumpentyp-Nr aus HE ersetzten
            #    if pumpentyp_imp in self._ref_pumpentyp:
            #        pumpentyp = self._ref_pumpentyp[pumpentyp_imp]
            #    else:
                    # Noch nicht in Tabelle [pumpentyp] enthalten, also ergaenzen
            #        pumpentyp = u'{}_he'.format(pumpentyp_imp)
            #        sql = u"INSERT INTO pumpentypen (bezeichnung) Values ('{pumpentyp_imp}')".format( \
            #            pumpentyp_imp=pumpentyp_imp)
            #        self._ref_pumpentyp[pumpentyp_imp] = pumpentyp
            #        if not self.dbQK.sql(sql, u'xml_import (21)'):
            #            break

            pumpe = Pumpe(pnam, schoben, schunten, pumpentyp, volanf, volges, sohle, steuersch, einschalthoehe,
                          ausschalthoehe, simstatus, kommentar)
            yield pumpe


    def importPumpen(self):
        """Hier werden die Pumpen Daten in die Datenbank geschrieben"""

        """1. Teil: Hier werden die hydraulischen Pumpen Daten in die Datenbank geschrieben"""

        for pumpe in self.pumpen_hydraulik():
            pnam = pumpe.pnam()
            schoben = pumpe.schoben()
            schunten = pumpe.schunten()
            pumpentyp = pumpe.pumpentyp
            volanf = pumpe.volanf()
            volges = pumpe.volges()
            sohle = pumpe.sohle()
            steuersch = pumpe.steuersch()
            einschalthoehe = pumpe.einschalthoehe()
            ausschalthoehe = pumpe.ausschalthoehe()
            simstat_imp = pumpe.simstatus()
            kommentar = pumpe.kommentar()


            # Pumpendaten aufbereiten und in die QKan-DB schreiben


            # Abhängig von der Datenbank unterscheidet sich die Syntax zur Erzeugung des Geo-Objektes

            if self.dbtyp == 'SpatiaLite':
                geom = u'''MakeLine(MakePoint(SCHOB.xsch, SCHOB.ysch, {epsg}), MakePoint(SCHUN.xsch, SCHUN.ysch, {epsg}))'''.format(
                    epsg=self.epsg)
            elif self.dbtyp == 'postgis':
                geom = u'''ST_MakeLine(ST_SetSRID(ST_MakePoint(SCHOB.xsch, SCHOB.ysch, {epsg}),
                                           ST_SetSRID(ST_MakePoint(SCHUN.xsch, SCHUN.ysch, {epsg}))'''.format(
                    self.epsg)
            else:
                fehlermeldung('Programmfehler!', 
                    'Datenbanktyp ist fehlerhaft {0:s}\nAbbruch!'.format(self.dbtyp))
                return None

            # Bei den Pumpen muessen im Gegensatz zu den Haltungen die Koordinaten aus den Schachtdaten entnommen werden. 
            # Dies ist in QKan einfach, da auch Auslaesse und Speicher in der Tabelle "schaechte" gespeichert werden. 

            try:
                sql = u"""  INSERT INTO pumpen 
                                (pnam, volanf, volges, sohle, schoben, schunten, pumpentyp, steuersch, geom)
                            SELECT '{pnam}', {volanf}, {volges}, {sohle}, '{schoben}', '{schunten}', 
                                '{pumpentyp}', '{steuersch}', {geom}
                            FROM schaechte AS SCHOB,
                                schaechte AS SCHUN
                            WHERE SCHOB.schnam = '{schoben}' AND SCHUN.schnam = '{schunten}'""".format(
                                            pnam=pnam,
                                            volanf=volanf, volges=volges, sohle=sohle,
                                            schoben=schoben, schunten=schunten, pumpentyp=pumpentyp, steuersch=steuersch,
                                            einschalthoehe=einschalthoehe, ausschalthoehe=ausschalthoehe, geom=geom )

                if not self.dbQK.sql(sql, 'xml_import (19)'):
                    return None

            except BaseException as err:
                fehlermeldung(u'SQL-Fehler', repr(err))
                fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql INSERT INTO pumpen: \n" + \
                              str((volanf, volges, sohle, steuersch, einschalthoehe, ausschalthoehe, pnam)) + u'\n\n')
                return None

        self.dbQK.commit()

        for pumpe in self.pumpen():
            pnam = pumpe.pnam()
            schoben = pumpe.schoben()
            schunten = pumpe.schunten()
            pumpentyp = pumpe.pumpentyp()
            volanf = pumpe.volanf()
            volges = pumpe.volges()
            sohle = pumpe.sohle()
            steuersch = pumpe.steuersch()
            einschalthoehe = pumpe.einschalthoehe()
            ausschalthoehe = pumpe.ausschalthoehe()
            simstatus = pumpe.simstatus()
            kommentar = pumpe.kommentar()


            # Pumpendaten aufbereiten und in die QKan-DB schreiben

            # Datensatz aufbereiten in die QKan-DB schreiben

            try:
                sql = u"""UPDATE pumpen
                            SET 
                            simstatus = '{simstatus}',
                            kommentar = '{kommentar}'
                            WHERE pnam = '{pnam}'""".format(pnam=pnam, simstatus=simstatus, kommentar=kommentar)

                if not self.dbQK.sql(sql, 'xml_import (22)'):
                    return None

            except BaseException as err:
                fehlermeldung(u'SQL-Fehler', repr(err))
                fehlermeldung(u"Fehler in QKan_Import_from_HE", u"\nFehler in sql INSERT INTO pumpen: \n" + \
                              str(( pnam, schoben, schunten, simstatus, kommentar)) + u'\n\n')
                return None

        self.dbQK.commit()

        return True

