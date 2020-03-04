# -*- coding: utf-8 -*-

"""

  Import from SWMM
  ==============

  Aus einer SWMM-INP-Datei werden Kanaldaten in eine QKan-Datenbank importiert. 
  Dazu wird eine Projektdatei erstellt, die verschiedene thematische Layer 
  erzeugt, u.a. eine Klassifizierung der Schachttypen.

  | Dateiname            : importswmm.py
  | Date                 : März 2020
  | Copyright            : (C) 2020 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

"""

import os

__author__ = "Joerg Hoettges"
__date__ = "März 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

class SWMM():
    def __init__(self, inpfile, sqlobject, epsg=25832, dbtyp='SpatiaLite'):
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

        # self.dbQK = dbQK
        self.epsg = epsg
        self.dbtyp = dbtyp
        self.inpobject = open(inpfile)
        self.sqlobject = open(sqlcommandfile, 'w')
        self.zeile = ''

    def __del__(self):
        self.inpobject.close()
        self.sqlobject.close()

    def readError(self, meldung):
        self.sqlobject.write(f'Fehler: {meldung}')

    def readInpfile(self) -> bool:
        while True:
            self.zeile = self.inpobject.readline().strip()
            if not(self.zeile[0] == ';' or self.zeile == '\p'):
                # Kommentar- oder Leerzeile
                break

    def readTITLE(self):
        """Block TITLE lesen. Da Dateianfang, wird der Header mitgelesen"""
        self.readInpfile()
        if self.zeile != '[TITLE]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True

    def readOPTIONS(self):
        if self.zeile != '[OPTIONS]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True

    def readEVAPORATION(self):
        if self.zeile != '[EVAPORATION]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True


    def readRAINGAGES(self):
        if self.zeile != '[RAINGAGES]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True


    def readSUBCATCHMENTS(self):
        if self.zeile != '[SUBCATCHMENTS]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True


    def readSUBAREAS(self):
        if self.zeile != '[SUBAREAS]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True


    def readINFILTRATION(self):
        if self.zeile != '[INFILTRATION]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True


    def readJUNCTIONS(self):
        """Haltungsdaten                                    Attributnamen bitte in qkan/database/qkan_database.py nachsehen"""

        if self.zeile != '[JUNCTIONS]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True

            haltnam = self.zeile[0:17].strip()
            schoben = self.zeile[17:34].strip()
            schunten = self.zeile[34:51].strip()
            laenge = float(self.zeile[51:63].strip())/1000.
        
            sql = f"""
                INSERT into haltungen (haltnam, schoben, schunten, laenge)
                VALUES ('{haltnam}', '{schoben}', '{schunten}', {laenge})
            """
            
            self.sqlobject.write(sql + '\n')

    def readOUTFALLS(self):
        if self.zeile != '[OUTFALLS]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True

    def readCONDUITS(self):
        """Schachtdaten                                    Attributnamen bitte in qkan/database/qkan_database.py nachsehen"""
        if self.zeile != '[CONDUITS]':
            return False

        while True:
            self.readInpfile()
            if self.zeile[0] == '[':
                return True


def readKanaldaten(inpfile: str, sqlcommandfile: str):
    """Ruft die Klasse SWMM zur Verarbeitung der Daten auf"""

    if not os.path.exists(inpfile):
        return False
    
    
    data = SWMM(inpfile, sqlcommandfile)

    if not data.readTITLE():
        data.readError('\nBlock TITLE konnte nicht gelesen werden')
        return False

    if not data.readEVAPORATION():
        data.readError('\nBlock EVAPORATION konnte nicht gelesen werden')
        return False

    if not data.readRAINGAGES():
        data.readError('\nBlock RAINGAGES konnte nicht gelesen werden')
        return False

    if not data.readSUBCATCHMENTS():
        data.readError('\nBlock SUBCATCHMENTS konnte nicht gelesen werden')
        return False

    if not data.readSUBAREAS():
        data.readError('\nBlock SUBAREAS konnte nicht gelesen werden')
        return False

    if not data.readNFILTRATION():
        data.readError('\nBlock NFILTRATION konnte nicht gelesen werden')
        return False

    if not data.readJUNCTIONS():
        data.readError('\nBlock JUNCTIONS konnte nicht gelesen werden')
        return False

    if not data.readOUTFALLS():
        data.readError('\nBlock OUTFALLS konnte nicht gelesen werden')
        return False

    if not data.readCONDUITS():
        data.readError('\nBlock CONDUITS konnte nicht gelesen werden')
        return False

    if not data.readXSECTIONS():
        data.readError('\nBlock XSECTIONS konnte nicht gelesen werden')
        return False

    if not data.readPOLLUTANTS():
        data.readError('\nBlock POLLUTANTS konnte nicht gelesen werden')
        return False

    if not data.readLANDUSES():
        data.readError('\nBlock LANDUSES konnte nicht gelesen werden')
        return False

    if not data.readCOVERAGES():
        data.readError('\nBlock COVERAGES konnte nicht gelesen werden')
        return False

    if not data.readLOADINGS():
        data.readError('\nBlock LOADINGS konnte nicht gelesen werden')
        return False

    if not data.readBUILDUP():
        data.readError('\nBlock BUILDUP konnte nicht gelesen werden')
        return False

    if not data.readWASHOFF():
        data.readError('\nBlock WASHOFF konnte nicht gelesen werden')
        return False

    if not data.readTIMESERIES():
        data.readError('\nBlock TIMESERIES konnte nicht gelesen werden')
        return False

    if not data.readREPORT():
        data.readError('\nBlock REPORT konnte nicht gelesen werden')
        return False

    if not data.readTAGS():
        data.readError('\nBlock TAGS konnte nicht gelesen werden')
        return False

    if not data.readMAP():
        data.readError('\nBlock MAP konnte nicht gelesen werden')
        return False

    if not data.readCOORDINATES():
        data.readError('\nBlock COORDINATES konnte nicht gelesen werden')
        return False

    if not data.readVERTICES():
        data.readError('\nBlock VERTICES konnte nicht gelesen werden')
        return False

    if not data.readPolygons():
        data.readError('\nBlock Polygons konnte nicht gelesen werden')
        return False

    if not data.readSYMBOLS():
        data.readError('\nBlock SYMBOLS konnte nicht gelesen werden')
        return False

    del data




if __name__ in ('console', '__main__'):

    inpfile = 'tutorial.inp'
    sqlcommandfile = 'sqlcommands.sql'
    readKanaldaten(inpfile, sqlcommandfile)
