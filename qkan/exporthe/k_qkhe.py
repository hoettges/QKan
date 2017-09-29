# -*- coding: utf-8 -*-

"""
  Export Kanaldaten nach HYSTEM-EXTRAN
  ====================================

  Transfer von Kanaldaten aus einer QKan-Datenbank nach HYSTEM EXTRAN 7.6

  | Dateiname            : k_qkhe.py
  | Date                 : Februar 2017
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.                                  

"""

import logging
import math
import os
import shutil
# import pyspatialite.dbapi2 as splite
# import site, shutil
# import json
import time

from qgis.core import QgsMessageLog
# from qgis.core import QgsGeometry, QgsFeature
# import qgis.utils
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from qkan.database.dbfunc import DBConnection
from qkan.database.fbfunc import FBConnection

logger = logging.getLogger('QKan')


# Fortschritts- und Fehlermeldungen

def fortschritt(text, prozent=0.):
    logger.debug(u'{:s} ({:.0f}%)'.format(text, prozent * 100.))
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text, prozent * 100.), 'Export: ', QgsMessageLog.INFO)


def fehlermeldung(title, text, dauer=0):
    logger.debug(u'{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)
    iface.messageBar().pushMessage(title, text, level=QgsMessageBar.CRITICAL, duration=dauer)


def exportKanaldaten(iface, database_HE, dbtemplate_HE, database_QKan, liste_teilgebiete,
                     fangradius=0.1, datenbanktyp='spatialite', check_export={}):
    '''Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine HE-Firebird-Datenbank.

    :database_HE:        Datenbankobjekt, das die Verknüpfung zur HE-Firebird-Datenbank verwaltet
    :type database_HE:   string

    :dbtemplate_HE:      Vorlage für die zu erstellende Firebird-Datenbank
    :type dbtemplate_HE: string

    :database_QKan:      Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type database_QKan: string

    :datenbanktyp:       Typ der Datenbank (SpatiaLite, PostGIS)
    :type datenbanktyp:  String

    :liste_teilgebiete: Liste der ausgewählten Teilgebiete
    :type liste_teilgebiete: String

    :check_export:       Liste von Export-Optionen
    :type check_export:  Dictionary

    :returns: void
    '''

    # ITWH-Datenbank aus gewählter Vorlage kopieren
    if os.path.exists(database_HE):
        try:
            os.remove(database_HE)
        except BaseException as err:
            fehlermeldung(
                u'Fehler (33) in QKan_Export: Die HE-Datenbank ist schon vorhanden und kann nicht ersetzt werden: ',
                str(err))
            return False
    try:
        shutil.copyfile(dbtemplate_HE, database_HE)
    except BaseException as err:
        fehlermeldung(u'Fehler (34) in QKan_Export: Kopieren der Vorlage HE-Datenbank fehlgeschlagen: ',
                      str(err))
        return False
    fortschritt(u"Firebird-Datenbank aus Vorlage kopiert...", 0.01)

    # Verbindung zur Hystem-Extran-Datenbank

    dbHE = FBConnection(database_HE)  # Datenbankobjekt der HE-Datenbank zum Schreiben

    if dbHE is None:
        fehlermeldung(u"(1) Fehler",
                      'ITWH-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_HE))
        return None

    # Verbindung zur QKan-Datenbank

    dbQK = DBConnection(database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesenen

    if dbQK is None:
        fehlermeldung(u"(2) Fehler",
                      'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
        return None

    # --------------------------------------------------------------------------------------------------
    # Kontrolle der vorhandenen Profilquerschnitte. 

    fortschritt('Pruefung der Profiltypen...', 0.02)

    # --------------------------------------------------------------------------------------------------
    # Zur Abschaetzung der voraussichtlichen Laufzeit

    dbQK.sql("SELECT count(*) AS n FROM schaechte")
    anzdata = float(dbQK.fetchone()[0])
    fortschritt(u"Anzahl Schächte: {}".format(anzdata))
    # print('anz: {:}'.format(anzdata))
    dbQK.sql("SELECT count(*) AS n FROM haltungen")
    anzdata += float(dbQK.fetchone()[0])
    fortschritt(u"Anzahl Haltungen: {}".format(anzdata))
    # print('anz: {:}'.format(anzdata))
    dbQK.sql("SELECT count(*) AS n FROM flaechen")
    anzdata += float(dbQK.fetchone()[0]) * 2
    fortschritt(u"Anzahl Flächen: {}".format(anzdata))
    # print('anz: {:}'.format(anzdata))

    # --------------------------------------------------------------------------------------------
    # Besonderes Gimmick des ITWH-Programmiers: Die IDs der Tabellen muessen sequentiell
    # vergeben werden!!! Ein Grund ist, dass (u.a.?) die Tabelle "tabelleninhalte" mit verschiedenen
    # Tabellen verknuepft ist und dieser ID eindeutig sein muss.

    dbHE.sql("SELECT NEXTID FROM ITWH$PROGINFO")
    nextid = int(dbHE.fetchone()[0])

    # --------------------------------------------------------------------------------------------
    # Export der Schaechte

    if check_export['export_schaechte'] or check_export['modify_schaechte']:
        if check_export['init_schaechte']:
            dbHE.sql("DELETE FROM SCHACHT")

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND schaechte.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        sql = u"""
            SELECT
                schaechte.schnam AS schnam,
                schaechte.deckelhoehe AS deckelhoehe,
                schaechte.sohlhoehe AS sohlhoehe,
                schaechte.durchm AS durchmesser,
                schaechte.strasse AS strasse,
                schaechte.xsch AS xsch,
                schaechte.ysch AS ysch
            FROM schaechte
            WHERE schaechte.schachttyp = 'Schacht'{}
            """.format(auswahl)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(21) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        nr0 = nextid

        fortschritt('Export Schaechte Teil 1...', 0.1)
        createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

        for attr in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (schnam, deckelhoehe_t, sohlhoehe_t, durchmesser_t, strasse, xsch_t, ysch_t) = \
                ('NULL' if el is None else el for el in attr)

            # Formatierung der Zahlen
            (deckelhoehe, sohlhoehe, durchmesser, xsch, ysch) = \
                ('NULL' if tt == 'NULL' else '{:.3f}'.format(float(tt)) \
                 for tt in (deckelhoehe_t, sohlhoehe_t, durchmesser_t, xsch_t, ysch_t))

            # Ändern vorhandener Datensätze
            if check_export['modify_schaechte']:
                sql = u"""
                    UPDATE SCHACHT SET
                    DECKELHOEHE={deckelhoehe}, KANALART={kanalart}, DRUCKDICHTERDECKEL={druckdichterdeckel},
                    SOHLHOEHE={sohlhoehe}, XKOORDINATE={xkoordinate}, YKOORDINATE={ykoordinate},
                    KONSTANTERZUFLUSS={konstanterzufluss}, GELAENDEHOEHE={gelaendehoehe},
                    ART={art}, ANZAHLKANTEN={anzahlkanten}, SCHEITELHOEHE={scheitelhoehe},
                    PLANUNGSSTATUS='{planungsstatus}', NAME='{name}', LASTMODIFIED='{lastmodified}',
                    ID={id}, DURCHMESSER={durchmesser}
                    WHERE NAME = '{name}';
                """.format(deckelhoehe=deckelhoehe, kanalart='0', druckdichterdeckel='0',
                           sohlhoehe=sohlhoehe, xkoordinate=xsch, ykoordinate=ysch,
                           konstanterzufluss='0', gelaendehoehe=deckelhoehe, art='1', anzahlkanten='0',
                           scheitelhoehe='0', planungsstatus='0', name=schnam, lastmodified=createdat,
                           id=nextid, durchmesser=durchmesser)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(3a) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

            # Einfuegen in die Datenbank
            elif check_export['export_schaechte']:
                # Trick: In Firebird ist kein SELECT ohne Tabelle möglich. Tabelle "RDB$DATABASE" hat genau 1 Datensatz
                sql = u"""
                    INSERT INTO SCHACHT
                    ( DECKELHOEHE, KANALART, DRUCKDICHTERDECKEL, SOHLHOEHE, XKOORDINATE, YKOORDINATE,
                      KONSTANTERZUFLUSS, GELAENDEHOEHE, ART, ANZAHLKANTEN, SCHEITELHOEHE,
                      PLANUNGSSTATUS, NAME, LASTMODIFIED, ID, DURCHMESSER)
                    SELECT
                      {deckelhoehe}, {kanalart}, {druckdichterdeckel}, {sohlhoehe}, {xkoordinate},
                      {ykoordinate}, {konstanterzufluss}, {gelaendehoehe}, {art}, {anzahlkanten},
                      {scheitelhoehe}, '{planungsstatus}', '{name}', '{lastmodified}', {id}, {durchmesser}
                    FROM RDB$DATABASE
                    WHERE '{name}' NOT IN (SELECT NAME FROM SCHACHT);
                """.format(deckelhoehe=deckelhoehe, kanalart='0', druckdichterdeckel='0',
                           sohlhoehe=sohlhoehe, xkoordinate=xsch, ykoordinate=ysch,
                           konstanterzufluss='0', gelaendehoehe=deckelhoehe, art='1', anzahlkanten='0',
                           scheitelhoehe='0', planungsstatus='0', name=schnam, lastmodified=createdat,
                           id=nextid, durchmesser=durchmesser)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(3b) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                nextid += 1

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Schaechte eingefuegt'.format(nextid - nr0), 0.30)

    # --------------------------------------------------------------------------------------------
    # Export der Speicherbauwerke
    #
    # Beim Export werden die IDs mitgeschrieben, um bei den Speicherkennlinien
    # wiederverwertet zu werden.

    if check_export['export_speicher'] or check_export['modify_speicher']:
        if check_export['init_speicher']:
            # Zuerst Daten aus Detailtabelle mit Speicherkennlinie löschen
            dbHE.sql("DELETE FROM TABELLENINHALTE WHERE ID IN (SELECT ID FROM SPEICHERSCHACHT)")
            dbHE.sql("DELETE FROM SPEICHERSCHACHT")

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND schaechte.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        sql = u"""
            SELECT
                schaechte.schnam AS schnam,
                schaechte.deckelhoehe AS deckelhoehe,
                schaechte.sohlhoehe AS sohlhoehe,
                schaechte.durchm AS durchmesser,
                schaechte.strasse AS strasse,
                schaechte.xsch AS xsch,
                schaechte.ysch AS ysch,
                kommentar AS kommentar
            FROM schaechte
            WHERE schaechte.schachttyp = 'Speicher'{}
            """.format(auswahl)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(22) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        nr0 = nextid
        refid_speicher = {}

        createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())
        for attr in dbQK.fetchall():
            fortschritt('Export Speicherschaechte...', 0.15)

            # In allen Feldern None durch NULL ersetzen
            (schnam, deckelhoehe_t, sohlhoehe_t, durchmesser_t, strasse, xsch_t, ysch_t, kommentar) = \
                ('NULL' if el is None else el for el in attr)

            # Formatierung der Zahlen
            (deckelhoehe, sohlhoehe, durchmesser, xsch, ysch) = \
                ('NULL' if tt == 'NULL' else '{:.3f}'.format(float(tt)) \
                 for tt in (deckelhoehe_t, sohlhoehe_t, durchmesser_t, xsch_t, ysch_t))

            # Speichern der aktuellen ID zum Speicherbauwerk
            refid_speicher[schnam] = nextid

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export['modify_speicher']:
                sql = u"""
                    UPDATE SPEICHERSCHACHT SET
                    ID={id}, TYP={typ}, SOHLHOEHE={sohlhoehe},
                      XKOORDINATE={xkoordinate}, YKOORDINATE={ykoordinate},
                      GELAENDEHOEHE={gelaendehoehe}, ART={art}, ANZAHLKANTEN={anzahlkanten},
                      SCHEITELHOEHE={scheitelhoehe}, HOEHEVOLLFUELLUNG={hoehevollfuellung},
                      KONSTANTERZUFLUSS={konstanterzufluss}, ABSETZWIRKUNG={absetzwirkung}, 
                      PLANUNGSSTATUS='{planungsstatus}',
                      NAME='{name}', LASTMODIFIED='{lastmodified}', KOMMENTAR='{kommentar}'
                      WHERE NAME='{name}';
                """.format(id=nextid, typ='1', sohlhoehe=sohlhoehe,
                           xkoordinate=xsch, ykoordinate=ysch,
                           gelaendehoehe=deckelhoehe, art='1', anzahlkanten='0',
                           scheitelhoehe=deckelhoehe, hoehevollfuellung=deckelhoehe,
                           konstanterzufluss='0', absetzwirkung='0', planungsstatus='0',
                           name=schnam, lastmodified=createdat, kommentar=kommentar,
                           durchmesser=durchmesser)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(4a) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

            # Einfuegen in die Datenbank
            elif check_export['export_speicher']:
                # Trick: In Firebird ist kein SELECT ohne Tabelle möglich. Tabelle "RDB$DATABASE" hat genau 1 Datensatz
                sql = u"""
                    INSERT INTO SPEICHERSCHACHT
                    ( ID, TYP, SOHLHOEHE,
                      XKOORDINATE, YKOORDINATE,
                      GELAENDEHOEHE, ART, ANZAHLKANTEN,
                      SCHEITELHOEHE, HOEHEVOLLFUELLUNG,
                      KONSTANTERZUFLUSS, ABSETZWIRKUNG, PLANUNGSSTATUS,
                      NAME, LASTMODIFIED, KOMMENTAR)
                    SELECT
                      {id}, {typ}, {sohlhoehe},
                      {xkoordinate}, {ykoordinate},
                      {gelaendehoehe}, {art}, {anzahlkanten},
                      {scheitelhoehe}, {hoehevollfuellung},
                      {konstanterzufluss}, {absetzwirkung}, '{planungsstatus}',
                      '{name}', '{lastmodified}', '{kommentar}'
                    FROM RDB$DATABASE
                    WHERE '{name}' NOT IN (SELECT NAME FROM SPEICHERSCHACHT);
                """.format(id=nextid, typ='1', sohlhoehe=sohlhoehe,
                           xkoordinate=xsch, ykoordinate=ysch,
                           gelaendehoehe=deckelhoehe, art='1', anzahlkanten='0',
                           scheitelhoehe=deckelhoehe, hoehevollfuellung=deckelhoehe,
                           konstanterzufluss='0', absetzwirkung='0', planungsstatus='0',
                           name=schnam, lastmodified=createdat, kommentar=kommentar,
                           durchmesser=durchmesser)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(4b) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                nextid += 1

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Speicher eingefuegt'.format(nextid - nr0), 0.40)

        # --------------------------------------------------------------------------------------------
        # Export der Kennlinien der Speicherbauwerke - nur wenn auch Speicher exportiert werden

        if check_export['export_speicherkennlinien'] or check_export['modify_speicherkennlinien']:

            sql = u"""SELECT sl.schnam, sl.wspiegel - sc.sohlhoehe AS wtiefe, sl.oberfl
                      FROM speicherkennlinien AS sl
                      JOIN schaechte AS sc ON sl.schnam = sc.schnam
                      ORDER BY sc.schnam, sl.wspiegel"""

            try:
                dbQK.sql(sql)
            except BaseException as err:
                fehlermeldung(u"(32) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
                del dbQK
                del dbHE
                return False

            spnam = None  # Zähler für Speicherkennlinien

            for attr in dbQK.fetchall():

                # In allen Feldern None durch NULL ersetzen
                (schnam, wtiefe, oberfl) = ('NULL' if el is None else el for el in attr)

                # Einfuegen in die Datenbank

                if schnam in refid_speicher:
                    if spnam == 'NULL' or schnam != spnam:
                        spnam = schnam
                        reihenfolge = 1
                    else:
                        schnam = spnam
                        reihenfolge += 1

                    # Ändern vorhandener Datensätze entfällt bei Tabellendaten

                    # Einfuegen in die Datenbank
                    if check_export['export_speicherkennlinien']:
                        # Trick: In Firebird ist kein SELECT ohne Tabelle möglich. Tabelle "RDB$DATABASE" hat genau 1 Datensatz
                        sql = u"""
                            INSERT INTO TABELLENINHALTE
                            ( KEYWERT, WERT, REIHENFOLGE, ID)
                            SELECT
                              {wtiefe}, {oberfl}, {reihenfolge}, {id}
                            FROM RDB$DATABASE;
                        """.format(wtiefe=wtiefe, oberfl=oberfl, reihenfolge=reihenfolge, id=refid_speicher[schnam])
                        # print(sql)
                        try:
                            dbHE.sql(sql)
                        except BaseException as err:
                            fehlermeldung(u"(4d) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                            del dbQK
                            del dbHE
                            return False

            dbHE.commit()

            fortschritt('{} Speicher eingefuegt'.format(nextid - nr0), 0.40)

    # --------------------------------------------------------------------------------------------
    # Export der Auslaesse

    if check_export['export_auslaesse'] or check_export['modify_auslaesse']:
        if check_export['init_auslaesse']:
            dbHE.sql("DELETE FROM AUSLASS")

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND schaechte.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        sql = u"""
            SELECT
                schaechte.schnam AS schnam,
                schaechte.deckelhoehe AS deckelhoehe,
                schaechte.sohlhoehe AS sohlhoehe,
                schaechte.durchm AS durchmesser,
                schaechte.xsch AS xsch,
                schaechte.ysch AS ysch,
                kommentar AS kommentar
            FROM schaechte
            WHERE schaechte.schachttyp = 'Auslass'{}
            """.format(auswahl)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(22) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        nr0 = nextid

        createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

        fortschritt(u'Export Auslässe...', 0.20)

        for attr in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (schnam, deckelhoehe_t, sohlhoehe_t, durchmesser_t, xsch_t, ysch_t, kommentar) = \
                ('NULL' if el is None else el for el in attr)

            # Formatierung der Zahlen
            (deckelhoehe, sohlhoehe, durchmesser, xsch, ysch) = \
                ('NULL' if tt == 'NULL' else '{:.3f}'.format(float(tt)) \
                 for tt in (deckelhoehe_t, sohlhoehe_t, durchmesser_t, xsch_t, ysch_t))

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export['modify_auslaesse']:
                sql = u"""
                    UPDATE AUSLASS SET
                    ID={id}, TYP={typ}, RUECKSCHLAGKLAPPE={rueckschlagklappe},
                    SOHLHOEHE={sohlhoehe}, XKOORDINATE={xkoordinate}, YKOORDINATE={ykoordinate},
                    GELAENDEHOEHE={gelaendehoehe}, ART={art}, ANZAHLKANTEN={anzahlkanten},
                    SCHEITELHOEHE={scheitelhoehe}, KONSTANTERZUFLUSS={konstanterzufluss},
                    PLANUNGSSTATUS='{planungsstatus}', NAME='{name}',
                    LASTMODIFIED='{lastmodified}', KOMMENTAR='{kommentar}'
                    WHERE NAME = '{name}';
                """.format(id=nextid, typ='1', rueckschlagklappe=0, sohlhoehe=sohlhoehe,
                           xkoordinate=xsch, ykoordinate=ysch,
                           gelaendehoehe=deckelhoehe, art='3', anzahlkanten='0',
                           scheitelhoehe=deckelhoehe, konstanterzufluss=0, planungsstatus='0',
                           name=schnam, lastmodified=createdat, kommentar=kommentar,
                           durchmesser=durchmesser)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(31) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

            # Einfuegen in die Datenbank
            elif check_export['export_auslaesse']:
                sql = u"""
                    INSERT INTO AUSLASS
                    ( ID, TYP, RUECKSCHLAGKLAPPE, SOHLHOEHE,
                      XKOORDINATE, YKOORDINATE,
                      GELAENDEHOEHE, ART, ANZAHLKANTEN,
                      SCHEITELHOEHE, KONSTANTERZUFLUSS, PLANUNGSSTATUS,
                      NAME, LASTMODIFIED, KOMMENTAR)
                    SELECT
                      {id}, {typ}, {rueckschlagklappe}, {sohlhoehe},
                      {xkoordinate}, {ykoordinate},
                      {gelaendehoehe}, {art}, {anzahlkanten},
                      {scheitelhoehe}, {konstanterzufluss}, '{planungsstatus}',
                      '{name}', '{lastmodified}', '{kommentar}'
                    FROM RDB$DATABASE
                    WHERE '{name}' NOT IN (SELECT NAME FROM AUSLASS);
                """.format(id=nextid, typ='1', rueckschlagklappe=0, sohlhoehe=sohlhoehe,
                           xkoordinate=xsch, ykoordinate=ysch,
                           gelaendehoehe=deckelhoehe, art='3', anzahlkanten='0',
                           scheitelhoehe=deckelhoehe, konstanterzufluss=0, planungsstatus='0',
                           name=schnam, lastmodified=createdat, kommentar=kommentar,
                           durchmesser=durchmesser)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(31) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                nextid += 1

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt(u'{} Auslässe eingefuegt'.format(nextid - nr0), 0.40)

    # --------------------------------------------------------------------------------------------
    # Export der Haltungen
    #
    # Erläuterung zum Feld "GESAMTFLAECHE":
    # Die Haltungsfläche (area(tezg.geom)) wird in das Feld "GESAMTFLAECHE" eingetragen und erscheint damit
    # in HYSTEM-EXTRAN in der Karteikarte "Haltungen > Trockenwetter". Solange dort kein
    # Siedlungstyp zugeordnet ist, wird diese Fläche nicht wirksam und dient nur der Information!

    if check_export['export_haltungen'] or check_export['modify_haltungen']:
        if check_export['init_haltungen']:
            dbHE.sql("DELETE FROM ROHR")

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND haltungen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        sql = u"""
          SELECT
              haltungen.haltnam AS haltnam, haltungen.schoben AS schoben, haltungen.schunten AS schunten,
              coalesce(haltungen.laenge, glength(haltungen.geom)) AS laenge_t,
              coalesce(haltungen.sohleoben,n1.sohlhoehe) AS sohleoben_t,
              coalesce(haltungen.sohleunten,n2.sohlhoehe) AS sohleunten_t,
              haltungen.profilnam AS profilnam, profile.he_nr AS he_nr, haltungen.hoehe AS hoehe_t, haltungen.breite AS breite_t,
              entwaesserungsarten.he_nr AS entw_nr,
              haltungen.rohrtyp AS rohrtyp, haltungen.ks AS rauheit_t,
              haltungen.teilgebiet AS teilgebiet, haltungen.createdat AS createdat
            FROM
              (haltungen JOIN schaechte AS n1 ON haltungen.schoben = n1.schnam)
              JOIN schaechte AS n2 ON haltungen.schunten = n2.schnam
              LEFT JOIN profile ON haltungen.profilnam = profile.profilnam
              LEFT JOIN entwaesserungsarten ON haltungen.entwart = entwaesserungsarten.bezeichnung
              LEFT JOIN simulationsstatus AS st ON haltungen.simstatus = st.bezeichnung
              WHERE (st.he_nr = '0' or st.he_nr IS NULL){:}
        """.format(auswahl)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(5) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        fortschritt('Export Haltungen...', 0.35)

        nr0 = nextid

        for attr in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (haltnam, schoben, schunten, laenge_t, sohleoben_t, sohleunten_t, profilnam,
             he_nr, hoehe_t, breite_t, entw_nr, rohrtyp, rauheit_t, teilgebiet, createdat) = \
                ('NULL' if el is None else el for el in attr)

            createdat = createdat[:19]
            # Datenkorrekturen
            (laenge, sohleoben, sohleunten, hoehe, breite) = \
                ('NULL' if tt == 'NULL' else '{:.4f}'.format(float(tt)) \
                 for tt in (laenge_t, sohleoben_t, sohleunten_t, hoehe_t, breite_t))

            if rauheit_t == 'NULL':
                rauheit = '1.5'
            else:
                rauheit = '{:.3f}'.format(float(rauheit_t))

                h_profil = he_nr
            if h_profil == '68':
                h_sonderprofil = profilnam
            else:
                h_sonderprofil = ''

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export['modify_haltungen']:
                # Profile < 0 werden nicht uebertragen
                if int(h_profil) > 0:
                    sql = u"""
                      UPDATE ROHR SET
                      NAME='{name}', SCHACHTOBEN='{schachtoben}', SCHACHTUNTEN='{schachtunten}',
                      LAENGE={laenge}, SOHLHOEHEOBEN={sohlhoeheoben},
                      SOHLHOEHEUNTEN={sohlhoeheunten}, PROFILTYP='{profiltyp}', 
                      SONDERPROFILBEZEICHNUNG='{sonderprofilbezeichnung}',
                      GEOMETRIE1={geometrie1}, GEOMETRIE2={geometrie2}, KANALART='{kanalart}',
                      RAUIGKEITSBEIWERT={rauigkeitsbeiwert}, ANZAHL={anzahl},
                      TEILEINZUGSGEBIET='{teileinzugsgebiet}', RUECKSCHLAGKLAPPE={rueckschlagklappe},
                      KONSTANTERZUFLUSS={konstanterzufluss}, EINZUGSGEBIET={einzugsgebiet},
                      KONSTANTERZUFLUSSTEZG={konstanterzuflusstezg}, RAUIGKEITSANSATZ={rauigkeitsansatz},
                      GEFAELLE={gefaelle}, GESAMTFLAECHE={gesamtflaeche}, ABFLUSSART={abflussart},
                      INDIVIDUALKONZEPT={individualkonzept}, HYDRAULISCHERRADIUS={hydraulischerradius},
                      RAUHIGKEITANZEIGE={rauhigkeitanzeige}, PLANUNGSSTATUS={planungsstatus},
                      LASTMODIFIED='{lastmodified}', MATERIALART={materialart},
                      EREIGNISBILANZIERUNG={ereignisbilanzierung},
                      EREIGNISGRENZWERTENDE={ereignisgrenzwertende},
                      EREIGNISGRENZWERTANFANG={ereignisgrenzwertanfang},
                      EREIGNISTRENNDAUER={ereignistrenndauer}, EREIGNISINDIVIDUELL={ereignisindividuell},
                      ID={id}
                      WHERE NAME = '{name}';
                      """.format(name=haltnam, schachtoben=schoben, schachtunten=schunten,
                                 laenge=laenge, sohlhoeheoben=sohleoben,
                                 sohlhoeheunten=sohleunten, profiltyp=h_profil,
                                 sonderprofilbezeichnung=h_sonderprofil, geometrie1=hoehe,
                                 geometrie2=breite, kanalart=entw_nr,
                                 rauigkeitsbeiwert=1.5, anzahl=1, teileinzugsgebiet='',
                                 rueckschlagklappe=0, konstanterzufluss=0,
                                 einzugsgebiet=0, konstanterzuflusstezg=0,
                                 rauigkeitsansatz=1, gefaelle=0,
                                 gesamtflaeche=0, abflussart=0,
                                 individualkonzept=0, hydraulischerradius=0,
                                 rauhigkeitanzeige=1.5, planungsstatus=0,
                                 lastmodified=createdat, materialart=28,
                                 ereignisbilanzierung=0, ereignisgrenzwertende=0,
                                 ereignisgrenzwertanfang=0, ereignistrenndauer=0,
                                 ereignisindividuell=0, id=nextid)
                    try:
                        dbHE.sql(sql)
                    except BaseException as err:
                        fehlermeldung(u"(6b) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                        del dbQK
                        del dbHE
                        return False

            # Einfuegen in die Datenbank
            elif check_export['export_haltungen']:
                # Profile < 0 werden nicht uebertragen
                if int(h_profil) > 0:
                    sql = u"""
                      INSERT INTO ROHR
                      ( NAME, SCHACHTOBEN, SCHACHTUNTEN, LAENGE, SOHLHOEHEOBEN,
                        SOHLHOEHEUNTEN, PROFILTYP, SONDERPROFILBEZEICHNUNG, GEOMETRIE1,
                        GEOMETRIE2, KANALART, RAUIGKEITSBEIWERT, ANZAHL, TEILEINZUGSGEBIET,
                        RUECKSCHLAGKLAPPE, KONSTANTERZUFLUSS, EINZUGSGEBIET, KONSTANTERZUFLUSSTEZG,
                        RAUIGKEITSANSATZ, GEFAELLE, GESAMTFLAECHE, ABFLUSSART,
                        INDIVIDUALKONZEPT, HYDRAULISCHERRADIUS, RAUHIGKEITANZEIGE, PLANUNGSSTATUS,
                        LASTMODIFIED, MATERIALART, EREIGNISBILANZIERUNG, EREIGNISGRENZWERTENDE,
                        EREIGNISGRENZWERTANFANG, EREIGNISTRENNDAUER, EREIGNISINDIVIDUELL, ID)
                      SELECT
                        '{name}', '{schachtoben}', '{schachtunten}', {laenge}, {sohlhoeheoben},
                        {sohlhoeheunten}, '{profiltyp}', '{sonderprofilbezeichnung}', {geometrie1},
                        {geometrie2}, '{kanalart}', {rauigkeitsbeiwert}, {anzahl}, '{teileinzugsgebiet}',
                        {rueckschlagklappe}, {konstanterzufluss}, {einzugsgebiet}, {konstanterzuflusstezg},
                        {rauigkeitsansatz}, {gefaelle}, {gesamtflaeche}, {abflussart},
                        {individualkonzept}, {hydraulischerradius}, {rauhigkeitanzeige}, {planungsstatus},
                        '{lastmodified}', {materialart}, {ereignisbilanzierung}, {ereignisgrenzwertende},
                        {ereignisgrenzwertanfang}, {ereignistrenndauer}, {ereignisindividuell}, {id}
                      FROM RDB$DATABASE
                      WHERE '{name}' NOT IN (SELECT NAME FROM ROHR);
                      """.format(name=haltnam, schachtoben=schoben, schachtunten=schunten,
                                 laenge=laenge, sohlhoeheoben=sohleoben,
                                 sohlhoeheunten=sohleunten, profiltyp=h_profil,
                                 sonderprofilbezeichnung=h_sonderprofil, geometrie1=hoehe,
                                 geometrie2=breite, kanalart=entw_nr,
                                 rauigkeitsbeiwert=1.5, anzahl=1, teileinzugsgebiet='',
                                 rueckschlagklappe=0, konstanterzufluss=0,
                                 einzugsgebiet=0, konstanterzuflusstezg=0,
                                 rauigkeitsansatz=1, gefaelle=0,
                                 gesamtflaeche=0, abflussart=0,
                                 individualkonzept=0, hydraulischerradius=0,
                                 rauhigkeitanzeige=1.5, planungsstatus=0,
                                 lastmodified=createdat, materialart=28,
                                 ereignisbilanzierung=0, ereignisgrenzwertende=0,
                                 ereignisgrenzwertanfang=0, ereignistrenndauer=0,
                                 ereignisindividuell=0, id=nextid)
                    try:
                        dbHE.sql(sql)
                    except BaseException as err:
                        fehlermeldung(u"(6b) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                        del dbQK
                        del dbHE
                        return False

                    nextid += 1
        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Haltungen eingefuegt'.format(nextid - nr0), 0.60)

    # --------------------------------------------------------------------------------------------
    # Export der Bodenklassen

    if check_export['export_bodenklassen'] or check_export['modify_bodenklassen']:
        if check_export['init_bodenklassen']:
            dbHE.sql("DELETE FROM BODENKLASSE")

        sql = u"""
            SELECT
                bknam AS bknam,
                infiltrationsrateanfang AS infiltrationsrateanfang, 
                infiltrationsrateende AS infiltrationsrateende, 
                infiltrationsratestart AS infiltrationsratestart, 
                rueckgangskonstante AS rueckgangskonstante, 
                regenerationskonstante AS regenerationskonstante, 
                saettigungswassergehalt AS saettigungswassergehalt, 
                createdat AS createdat,
                kommentar AS kommentar
            FROM bodenklassen
            """.format(auswahl)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(22) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        nr0 = nextid

        for attr in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (bknam, infiltrationsrateanfang, infiltrationsrateende, infiltrationsratestart,
             rueckgangskonstante, regenerationskonstante, saettigungswassergehalt,
             createdat, kommentar) = \
                ('NULL' if el is None else el for el in attr)

            # Der leere Satz Bodenklasse ist nur für interne QKan-Zwecke da. 
            if bknam == 'NULL':
                continue

            if createdat == 'NULL':
                createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export['modify_bodenklassen']:
                sql = u"""
                    UPDATE BODENKLASSE SET
                    INFILTRATIONSRATEANFANG={infiltrationsrateanfang},
                    INFILTRATIONSRATEENDE={infiltrationsrateende},
                    INFILTRATIONSRATESTART={infiltrationsratestart},
                    RUECKGANGSKONSTANTE={rueckgangskonstante},
                    REGENERATIONSKONSTANTE={regenerationskonstante},
                    SAETTIGUNGSWASSERGEHALT={saettigungswassergehalt},
                    NAME='{name}', LASTMODIFIED='{lastmodified}',
                    KOMMENTAR='{kommentar}', ID={id}
                    WHERE NAME = '{name}';
                    """.format(infiltrationsrateanfang=infiltrationsrateanfang,
                               infiltrationsrateende=infiltrationsrateende,
                               infiltrationsratestart=infiltrationsratestart,
                               rueckgangskonstante=rueckgangskonstante,
                               regenerationskonstante=regenerationskonstante,
                               saettigungswassergehalt=saettigungswassergehalt,
                               name=bknam, lastmodified=createdat,
                               kommentar=kommentar, id=nextid)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(31) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

            # Einfuegen in die Datenbank
            elif check_export['export_bodenklassen']:
                sql = u"""
                  INSERT INTO BODENKLASSE
                  ( INFILTRATIONSRATEANFANG, INFILTRATIONSRATEENDE,
                    INFILTRATIONSRATESTART, RUECKGANGSKONSTANTE, REGENERATIONSKONSTANTE,
                    SAETTIGUNGSWASSERGEHALT, NAME, LASTMODIFIED, KOMMENTAR,  ID)
                  SELECT
                    {infiltrationsrateanfang}, {infiltrationsrateende},
                    {infiltrationsratestart}, {rueckgangskonstante}, {regenerationskonstante},
                    {saettigungswassergehalt}, '{name}', '{lastmodified}', '{kommentar}', {id}
                    FROM RDB$DATABASE
                    WHERE '{name}' NOT IN (SELECT NAME FROM BODENKLASSE);
                    """.format(infiltrationsrateanfang=infiltrationsrateanfang,
                               infiltrationsrateende=infiltrationsrateende,
                               infiltrationsratestart=infiltrationsratestart,
                               rueckgangskonstante=rueckgangskonstante,
                               regenerationskonstante=regenerationskonstante,
                               saettigungswassergehalt=saettigungswassergehalt,
                               name=bknam, lastmodified=createdat,
                               kommentar=kommentar, id=nextid)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(7) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                nextid += 1

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Bodenklassen eingefuegt'.format(nextid - nr0), 0.62)

    # --------------------------------------------------------------------------------------------
    # Export der Abflussparameter

    if check_export['export_abflussparameter'] or check_export['modify_abflussparameter']:
        if check_export['init_abflussparameter']:
            dbHE.sql("DELETE FROM ABFLUSSPARAMETER")

        sql = u"""
            SELECT
                apnam,
                anfangsabflussbeiwert AS anfangsabflussbeiwert_t,
                endabflussbeiwert AS endabflussbeiwert_t,
                benetzungsverlust AS benetzungsverlust_t,
                muldenverlust AS muldenverlust_t,
                benetzung_startwert AS benetzung_startwert_t,
                mulden_startwert AS mulden_startwert_t,
                bodenklasse, kommentar, createdat
            FROM abflussparameter
            """.format(auswahl)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(22) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        nr0 = nextid

        if createdat == 'NULL':
            createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

        fortschritt(u'Export Abflussparameter...', 70)

        for attr in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (apnam, anfangsabflussbeiwert_t, endabflussbeiwert_t,
             benetzungsverlust_t, muldenverlust_t, benetzung_startwert_t,
             mulden_startwert_t, bodenklasse, kommentar, createdat) = \
                ('NULL' if el is None else el for el in attr)

            # Formatierung der Zahlen
            (anfangsabflussbeiwert, endabflussbeiwert, benetzungsverlust,
             muldenverlust, benetzung_startwert, mulden_startwert) = \
                ('NULL' if tt == 'NULL' else '{:.2f}'.format(float(tt)) \
                 for tt in (anfangsabflussbeiwert_t, endabflussbeiwert_t,
                            benetzungsverlust_t, muldenverlust_t, benetzung_startwert_t,
                            mulden_startwert_t))

            if bodenklasse == 'NULL':
                typ = 0  # undurchlässig
                bodenklasse = ''
            else:
                typ = 1  # durchlässig

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export['modify_auslaesse']:
                sql = u"""
                  UPDATE ABFLUSSPARAMETER SET
                  NAME='{apnam}', ABFLUSSBEIWERTANFANG={anfangsabflussbeiwert},
                  ABFLUSSBEIWERTENDE={endabflussbeiwert}, BENETZUNGSVERLUST={benetzungsverlust},
                  MULDENVERLUST={muldenverlust}, BENETZUNGSPEICHERSTART={benetzung_startwert},
                  MULDENAUFFUELLGRADSTART={mulden_startwert},
                  SPEICHERKONSTANTEKONSTANT={speicherkonstantekonstant},
                  SPEICHERKONSTANTEMIN={speicherkonstantemin},
                  SPEICHERKONSTANTEMAX={speicherkonstantemax},
                  SPEICHERKONSTANTEKONSTANT2={speicherkonstantekonstant2},
                  SPEICHERKONSTANTEMIN2={speicherkonstantemin2}, SPEICHERKONSTANTEMAX2={speicherkonstantemax2},
                  BODENKLASSE='{bodenklasse}', CHARAKTERISTISCHEREGENSPENDE={charakteristischeregenspende},
                  CHARAKTERISTISCHEREGENSPENDE2={charakteristischeregenspende2},
                  TYP={typ}, JAHRESGANGVERLUSTE={jahresgangverluste}, LASTMODIFIED='{createdat}',
                  KOMMENTAR='{kommentar}', ID={id}
                  WHERE NAME = '{apnam}';
                """.format(apnam=apnam, anfangsabflussbeiwert=anfangsabflussbeiwert,
                           endabflussbeiwert=endabflussbeiwert, benetzungsverlust=benetzungsverlust,
                           muldenverlust=muldenverlust, benetzung_startwert=benetzung_startwert,
                           mulden_startwert=mulden_startwert, speicherkonstantekonstant=1,
                           speicherkonstantemin=0, speicherkonstantemax=0, speicherkonstantekonstant2=1,
                           speicherkonstantemin2=0, speicherkonstantemax2=0,
                           bodenklasse=bodenklasse, charakteristischeregenspende=0, charakteristischeregenspende2=0,
                           typ=typ, jahresgangverluste=0, createdat=createdat, kommentar=kommentar, id=nextid)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(8a) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

            # Einfuegen in die Datenbank
            elif check_export['export_auslaesse']:
                sql = u"""
                  INSERT INTO ABFLUSSPARAMETER
                  ( NAME, ABFLUSSBEIWERTANFANG, ABFLUSSBEIWERTENDE, BENETZUNGSVERLUST,
                    MULDENVERLUST, BENETZUNGSPEICHERSTART, MULDENAUFFUELLGRADSTART, SPEICHERKONSTANTEKONSTANT,
                    SPEICHERKONSTANTEMIN, SPEICHERKONSTANTEMAX, SPEICHERKONSTANTEKONSTANT2,
                    SPEICHERKONSTANTEMIN2, SPEICHERKONSTANTEMAX2,
                    BODENKLASSE, CHARAKTERISTISCHEREGENSPENDE, CHARAKTERISTISCHEREGENSPENDE2,
                    TYP, JAHRESGANGVERLUSTE, LASTMODIFIED, KOMMENTAR, ID)
                  SELECT
                    '{apnam}', {anfangsabflussbeiwert}, {endabflussbeiwert}, {benetzungsverlust},
                    {muldenverlust}, {benetzung_startwert}, {mulden_startwert}, {speicherkonstantekonstant},
                    {speicherkonstantemin}, {speicherkonstantemax}, {speicherkonstantekonstant2},
                    {speicherkonstantemin2}, {speicherkonstantemax2},
                    '{bodenklasse}', {charakteristischeregenspende}, {charakteristischeregenspende2},
                    {typ}, {jahresgangverluste}, '{createdat}', '{kommentar}', {id}
                  FROM RDB$DATABASE
                  WHERE '{apnam}' NOT IN (SELECT NAME FROM ABFLUSSPARAMETER);
                """.format(apnam=apnam, anfangsabflussbeiwert=anfangsabflussbeiwert,
                           endabflussbeiwert=endabflussbeiwert, benetzungsverlust=benetzungsverlust,
                           muldenverlust=muldenverlust, benetzung_startwert=benetzung_startwert,
                           mulden_startwert=mulden_startwert, speicherkonstantekonstant=1,
                           speicherkonstantemin=0, speicherkonstantemax=0, speicherkonstantekonstant2=1,
                           speicherkonstantemin2=0, speicherkonstantemax2=0,
                           bodenklasse=bodenklasse, charakteristischeregenspende=0, charakteristischeregenspende2=0,
                           typ=typ, jahresgangverluste=0, createdat=createdat, kommentar=kommentar, id=nextid)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(8b) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                nextid += 1

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Abflussparameter eingefuegt'.format(nextid - nr0), 0.65)

    # ------------------------------------------------------------------------------------------------
    # Export der Regenschreiber
    #
    # Wenn in QKan keine Regenschreiber eingetragen sind, wird als Name "Regenschreiber1" angenommen.

    if check_export['export_regenschreiber'] or check_export['modify_regenschreiber']:
        if check_export['init_regenschreiber']:
            dbHE.sql("DELETE FROM REGENSCHREIBER")

        # # Pruefung, ob Regenschreiber fuer Export vorhanden
        # if len(liste_teilgebiete) != 0:
        #     auswahl = " AND flaechen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        # else:
        #     auswahl = ""
        #
        # sql = u"SELECT regenschreiber FROM flaechen GROUP BY regenschreiber{}".format(auswahl)

        # Regenschreiber berücksichtigen nicht ausgewählte Teilgebiete
        sql = u"""SELECT regenschreiber FROM flaechen GROUP BY regenschreiber"""
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(5) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        attr = dbQK.fetchall()
        if attr == [(None,)]:
            reglis = tuple(['Regenschreiber1'])
            logger.debug(u'In QKan war kein Regenschreiber vorhanden. "Regenschreiber1" ergänzt')
        else:
            reglis = tuple([str(el[0]) for el in attr])
            logger.debug(u'In QKan wurden folgende Regenschreiber referenziert: {}'.format(str(reglis)))

        logger.debug('Regenschreiber - reglis: {}'.format(str(reglis)))

        # Liste der fehlenden Regenschreiber in der Ziel- (*.idbf-) Datenbank
        # Hier muss eine Besonderheit von tuple berücksichtigt werden. Ein Tuple mit einem Element
        # endet mit ",)", z.B. (1,), während ohne oder bei mehr als einem Element alles wie üblich
        # ist: () oder (1,2,3,4)
        if len(reglis) == 1:
            sql = u"""SELECT NAME FROM REGENSCHREIBER WHERE NAME NOT IN {})""".format(str(reglis)[:-2])
        else:
            sql = u"""SELECT NAME FROM REGENSCHREIBER WHERE NAME NOT IN {}""".format(str(reglis))
        dbHE.sql(sql)

        attr = dbHE.fetchall()
        logger.debug('Regenschreiber - attr: {}'.format(str(attr)))

        nr0 = nextid

        regschnr = 1
        for regenschreiber in reglis:
            if regenschreiber not in attr:
                sql = u"""
                  INSERT INTO REGENSCHREIBER
                  ( NUMMER, STATION,
                    XKOORDINATE, YKOORDINATE, ZKOORDINATE, NAME,
                    FLAECHEGESAMT, FLAECHEDURCHLAESSIG, FLAECHEUNDURCHLAESSIG,
                    ANZAHLHALTUNGEN, INTERNENUMMER,
                    LASTMODIFIED, KOMMENTAR, ID) SELECT
                      {nummer}, '{station}',
                      {xkoordinate}, {ykoordinate}, {zkoordinate}, '{name}',
                      {flaechegesamt}, {flaechedurchlaessig}, {flaecheundurchlaessig},
                      {anzahlhaltungen}, {internenummer},
                      '{lastmodified}', '{kommentar}', {id}
                    FROM RDB$DATABASE
                    WHERE '{name}' NOT IN (SELECT NAME FROM REGENSCHREIBER);
                  """.format(nummer=regschnr, station=10000 + regschnr,
                             xkoordinate=0, ykoordinate=0, zkoordinate=0, name=regenschreiber,
                             flaechegesamt=0, flaechedurchlaessig=0, flaecheundurchlaessig=0,
                             anzahlhaltungen=0, internenummer=0,
                             lastmodified=createdat, kommentar=u'Ergänzt durch QKan', id=nextid)

                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(17) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                logger.debug(u'In HE folgenden Regenschreiber ergänzt: {}'.format(sql))

                nextid += 1
        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Regenschreiber eingefuegt'.format(nextid - nr0), 0.68)

    # ------------------------------------------------------------------------------------------------------
    # Export der Flaechendaten
    #
    # Die Daten werden in max. drei Teilen nach HYSTEM-EXTRAN exportiert:
    # 1. Befestigte Flächen
    # 2.1 Bei gesetzter Option check_export['export_difftezg']:
    #     Fläche der tezg abzüglich der Summe aller (befestigter und unbefestigter!) Flächen
    # 2.2 Unbefestigte Flächen

    # Die Abflusseigenschaften werden über die Tabelle "abflussparameter" geregelt. Dort ist 
    # im attribut bodenklasse nur bei unbefestigten Flächen ein Eintrag. Dies ist das Kriterium
    # zur Unterscheidung

    # undurchlässigen Flächen -------------------------------------------------------------------------------

    # Es gibt in HYSTEM-EXTRAN 3 Flächentypen (BERECHNUNGSSPEICHERKONSTANTE):
    # verwendete Parameter:    Anz_Sp  SpKonst.  Fz_SschwP  Fz_Oberfl  Fz_Kanal
    # 0 - direkt                 x       x
    # 1 - Fließzeiten                                          x          x
    # 2 - Schwerpunktfließzeit                       x

    # In der QKan-Datenbank sind Fz_SschwP und Fz_oberfl zu einem Feld zusammengefasst (fliesszeit)

    # Befestigte Flächen
    if check_export['export_flaechenrw'] or check_export['modify_flaechenrw']:
        if check_export['init_flaechenrw']:
            dbHE.sql("DELETE FROM FLAECHE")

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND flaechen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        # Teil 1: Nicht zu verschneidende Flächen exportieren
        sql = u"""
          SELECT flaechen.flnam AS flnam, haltungen.haltnam AS haltnam, flaechen.neigkl AS neigkl,
            flaechen.he_typ AS he_typ, flaechen.speicherzahl AS speicherzahl, flaechen.speicherkonst AS speicherkonst,
            flaechen.fliesszeit AS fliesszeit, flaechen.fliesszeitkanal AS fliesszeitkanal,
            area(flaechen.geom)/10000 AS flaeche, flaechen.regenschreiber AS regenschreiber,
            flaechen.abflussparameter AS abflussparameter, flaechen.createdat AS createdat,
            flaechen.kommentar AS kommentar
          FROM flaechen
          LEFT JOIN abflussparameter
          ON flaechen.abflussparameter = abflussparameter.apnam
          INNER JOIN linkfl
          ON within(StartPoint(linkfl.glink),flaechen.geom)
          INNER JOIN haltungen
          ON intersects(buffer(EndPoint(linkfl.glink),{fangradius}),haltungen.geom)
          WHERE area(flaechen.geom)/10000 > 0.01 AND
                (flaechen.aufteilen <> 'ja' or flaechen.aufteilen IS NULL){auswahl}
        """.format(auswahl=auswahl, fangradius=fangradius)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"QKan_Export (23) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        fortschritt('Export befestigte Flaechen...', 0.70)

        nr0 = nextid

        for attr in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (flnam, haltnam, neigkl,
             he_typ, speicherzahl, speicherkonst,
             fliesszeit, fliesszeitkanal,
             flaeche, regenschreiber,
             abflussparameter, createdat,
             kommentar) = \
                ('NULL' if el is None else el for el in attr)

            # Datenkorrekturen
            if regenschreiber == 'NULL':
                regenschreiber = 'Regenschreiber1'

            if he_typ == 'NULL':
                he_typ = 0  # Flächentyp 'Direkt'

            if neigkl == 'NULL':
                neigkl = 1

            if speicherzahl == 'NULL':
                speicherzahl = 3

            if speicherkonst == 'NULL':
                speicherkonst = math.sqrt(flaeche) * 2.

            if fliesszeit == 'NULL':
                fliesszeit = math.sqrt(flaeche) * 6.

            if fliesszeitkanal == 'NULL':
                fliesszeitkanal = 0

            if createdat == 'NULL':
                createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

            if kommentar == 'NULL' or kommentar == '':
                kommentar = 'eingefuegt von k_qkhe'

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export['modify_flaechenrw']:
                sql = u"""
                  UPDATE FLAECHE SET
                  GROESSE={flaeche:.4f}, REGENSCHREIBER='{regenschreiber}', HALTUNG='{haltnam}',
                  BERECHNUNGSPEICHERKONSTANTE={he_typ}, TYP={fltyp}, ANZAHLSPEICHER={speicherzahl},
                  SPEICHERKONSTANTE={speicherkonst:.3f}, SCHWERPUNKTLAUFZEIT={fliesszeit1:.2f},
                  FLIESSZEITOBERFLAECHE={fliesszeit2:.2f}, LAENGSTEFLIESSZEITKANAL={fliesszeitkanal:.2f},
                  PARAMETERSATZ='{abflussparameter}', NEIGUNGSKLASSE={neigkl},
                  NAME='fbef_{flnam}-{haltnam}', LASTMODIFIED='{createdat}',
                  KOMMENTAR='{kommentar}', ID={nextid}, ZUORDNUNABHEZG={zuordnunabhezg}
                  WHERE NAME = 'fbef_{flnam}-{haltnam}';
                  """.format(flaeche=flaeche, regenschreiber=regenschreiber, haltnam=haltnam,
                             he_typ=he_typ, fltyp=0, speicherzahl=speicherzahl,
                             speicherkonst=speicherkonst, fliesszeit1=fliesszeit,
                             fliesszeit2=fliesszeit, fliesszeitkanal=fliesszeitkanal,
                             abflussparameter=abflussparameter, neigkl=neigkl,
                             flnam=flnam, createdat=createdat,
                             kommentar=kommentar, nextid=nextid, zuordnunabhezg=0)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(9a) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

            # Einfuegen in die Datenbank
            if check_export['export_flaechenrw']:
                sql = u"""
                  INSERT INTO FLAECHE
                  ( GROESSE, REGENSCHREIBER, HALTUNG,
                    BERECHNUNGSPEICHERKONSTANTE, TYP, ANZAHLSPEICHER,
                    SPEICHERKONSTANTE, SCHWERPUNKTLAUFZEIT,
                    FLIESSZEITOBERFLAECHE, LAENGSTEFLIESSZEITKANAL,
                    PARAMETERSATZ, NEIGUNGSKLASSE,
                    NAME, LASTMODIFIED,
                    KOMMENTAR, ID, ZUORDNUNABHEZG)
                  SELECT
                    {flaeche:.4f}, '{regenschreiber}', '{haltnam}',
                    {he_typ}, {fltyp}, {speicherzahl},
                    {speicherkonst:.3f}, {fliesszeit1:.2f},
                    {fliesszeit2:.2f}, {fliesszeitkanal:.2f},
                    '{abflussparameter}', {neigkl},
                    'fbef_{flnam}-{haltnam}', '{createdat}',
                    '{kommentar}', {nextid}, {zuordnunabhezg}
                  FROM RDB$DATABASE
                  WHERE 'fbef_{flnam}-{haltnam}' NOT IN (SELECT NAME FROM FLAECHE);
                  """.format(flaeche=flaeche, regenschreiber=regenschreiber, haltnam=haltnam,
                             he_typ=he_typ, fltyp=0, speicherzahl=speicherzahl,
                             speicherkonst=speicherkonst, fliesszeit1=fliesszeit,
                             fliesszeit2=fliesszeit, fliesszeitkanal=fliesszeitkanal,
                             abflussparameter=abflussparameter, neigkl=neigkl,
                             flnam=flnam, createdat=createdat,
                             kommentar=kommentar, nextid=nextid, zuordnunabhezg=0)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(9b) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                nextid += 1

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Flaechen (nicht verschnitten) eingefuegt'.format(nextid - nr0), 0.80)

        # Teil 2: Zu verschneidende Flächen exportieren
        sql = u"""
          WITH flintersect AS (
            SELECT flaechen.flnam AS flnam, flaechen.neigkl AS neigkl, flaechen.he_typ AS he_typ, 
            flaechen.speicherzahl AS speicherzahl, flaechen.speicherkonst AS speicherkonst,
            flaechen.fliesszeit AS fliesszeit, flaechen.fliesszeitkanal AS fliesszeitkanal,
            flaechen.regenschreiber AS regenschreiber,
            flaechen.abflussparameter AS abflussparameter, flaechen.createdat AS createdat,
            flaechen.kommentar AS kommentar, CastToMultiPolygon(intersection(flaechen.geom,tezg.geom)) AS geom
            FROM flaechen
            INNER JOIN tezg
            ON intersects(flaechen.geom,tezg.geom)
            WHERE flaechen.aufteilen = 'ja'{auswahl})
          SELECT flintersect.flnam AS flnam, haltungen.haltnam AS haltnam, flintersect.neigkl AS neigkl,
            flintersect.he_typ AS he_typ, flintersect.speicherzahl AS speicherzahl, flintersect.speicherkonst AS speicherkonst,
            flintersect.fliesszeit AS fliesszeit, flintersect.fliesszeitkanal AS fliesszeitkanal,
            area(flintersect.geom)/10000 AS flaeche, flintersect.regenschreiber AS regenschreiber,
            flintersect.abflussparameter AS abflussparameter, flintersect.createdat AS createdat,
            flintersect.kommentar AS kommentar
          FROM flintersect
          LEFT JOIN abflussparameter
          ON flintersect.abflussparameter = abflussparameter.apnam
          INNER JOIN linkfl
          ON within(StartPoint(linkfl.glink),flintersect.geom)
          INNER JOIN haltungen
          ON intersects(buffer(EndPoint(linkfl.glink),{fangradius}),haltungen.geom)
          WHERE area(flintersect.geom)/10000 > 0.01
        """.format(auswahl=auswahl, fangradius=fangradius)
        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"QKan_Export (23) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        fortschritt('Export befestigte Flaechen...', 0.70)

        nr0 = nextid

        for attr in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (flnam, haltnam, neigkl,
             he_typ, speicherzahl, speicherkonst,
             fliesszeit, fliesszeitkanal,
             flaeche, regenschreiber,
             abflussparameter, createdat,
             kommentar) = \
                ('NULL' if el is None else el for el in attr)

            # Datenkorrekturen
            if regenschreiber == 'NULL':
                regenschreiber = 'Regenschreiber1'

            if he_typ == 'NULL':
                he_typ = 0  # Flächentyp 'Direkt'

            if neigkl == 'NULL':
                neigkl = 1

            if speicherzahl == 'NULL':
                speicherzahl = 3

            if speicherkonst == 'NULL':
                speicherkonst = math.sqrt(flaeche) * 2.

            if fliesszeit == 'NULL':
                fliesszeit = math.sqrt(flaeche) * 6.

            if fliesszeitkanal == 'NULL':
                fliesszeitkanal = 0

            if createdat == 'NULL':
                createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

            if kommentar == 'NULL' or kommentar == '':
                kommentar = 'eingefuegt von k_qkhe'

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export['modify_flaechenrw']:
                sql = u"""
                  UPDATE FLAECHE SET
                  GROESSE={flaeche:.4f}, REGENSCHREIBER='{regenschreiber}', HALTUNG='{haltnam}',
                  BERECHNUNGSPEICHERKONSTANTE={he_typ}, TYP={fltyp}, ANZAHLSPEICHER={speicherzahl},
                  SPEICHERKONSTANTE={speicherkonst:.3f}, SCHWERPUNKTLAUFZEIT={fliesszeit1:.2f},
                  FLIESSZEITOBERFLAECHE={fliesszeit2:.2f}, LAENGSTEFLIESSZEITKANAL={fliesszeitkanal:.2f},
                  PARAMETERSATZ='{abflussparameter}', NEIGUNGSKLASSE={neigkl},
                  NAME='fbef_{flnam}-{haltnam}', LASTMODIFIED='{createdat}',
                  KOMMENTAR='{kommentar}', ID={nextid}, ZUORDNUNABHEZG={zuordnunabhezg}
                  WHERE NAME = 'fbef_{flnam}-{haltnam}';
                  """.format(flaeche=flaeche, regenschreiber=regenschreiber, haltnam=haltnam,
                             he_typ=he_typ, fltyp=0, speicherzahl=speicherzahl,
                             speicherkonst=speicherkonst, fliesszeit1=fliesszeit,
                             fliesszeit2=fliesszeit, fliesszeitkanal=fliesszeitkanal,
                             abflussparameter=abflussparameter, neigkl=neigkl,
                             flnam=flnam, createdat=createdat,
                             kommentar=kommentar, nextid=nextid, zuordnunabhezg=0)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(9c) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

            # Einfuegen in die Datenbank
            if check_export['export_flaechenrw']:
                sql = u"""
                  INSERT INTO FLAECHE
                  ( GROESSE, REGENSCHREIBER, HALTUNG,
                    BERECHNUNGSPEICHERKONSTANTE, TYP, ANZAHLSPEICHER,
                    SPEICHERKONSTANTE, SCHWERPUNKTLAUFZEIT,
                    FLIESSZEITOBERFLAECHE, LAENGSTEFLIESSZEITKANAL,
                    PARAMETERSATZ, NEIGUNGSKLASSE,
                    NAME, LASTMODIFIED,
                    KOMMENTAR, ID, ZUORDNUNABHEZG)
                  SELECT
                    {flaeche:.4f}, '{regenschreiber}', '{haltnam}',
                    {he_typ}, {fltyp}, {speicherzahl},
                    {speicherkonst:.3f}, {fliesszeit1:.2f},
                    {fliesszeit2:.2f}, {fliesszeitkanal:.2f},
                    '{abflussparameter}', {neigkl},
                    'fbef_{flnam}-{haltnam}', '{createdat}',
                    '{kommentar}', {nextid}, {zuordnunabhezg}
                  FROM RDB$DATABASE
                  WHERE 'fbef_{flnam}-{haltnam}' NOT IN (SELECT NAME FROM FLAECHE);
                  """.format(flaeche=flaeche, regenschreiber=regenschreiber, haltnam=haltnam,
                             he_typ=he_typ, fltyp=0, speicherzahl=speicherzahl,
                             speicherkonst=speicherkonst, fliesszeit1=fliesszeit,
                             fliesszeit2=fliesszeit, fliesszeitkanal=fliesszeitkanal,
                             abflussparameter=abflussparameter, neigkl=neigkl,
                             flnam=flnam, createdat=createdat,
                             kommentar=kommentar, nextid=nextid, zuordnunabhezg=0)
                try:
                    dbHE.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(9d) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                    del dbQK
                    del dbHE
                    return False

                nextid += 1

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt('{} Flaechen (nicht verschnitten) eingefuegt'.format(nextid - nr0), 0.80)

    # -----------------------------------------------------------------------------------------
    # Bearbeitung in QKan: Vervollständigung der Teilgebiete
    """
      Prüfung der vorliegenden Teilgebiete in QKan
      ============================================
      Zunächst eine grundsätzliche Anmerkung: In HE gibt es keine Teilgebiete in der Form, wie sie
      in QKan vorhanden sind. Diese werden (nur) in QKan verwendet, um zum Einen die Grundlagendaten
       - einwohnerspezifischer Schmutzwasseranfall
       - Fremdwasseranteil
       - Stundenmittel
      zu verwalten und den tezg-Flächen zuzuordnen, die gleichzeitig Trockenwetterzufluss repräsentieren
      und zum Anderen, um die Möglichkeit zu haben, um für den Export Teile eines Netzes auszuwählen.

      Aus diesem Grund werden vor dem Export der Einzeleinleiter diese Daten geprüft:

      1 Wenn in QKan keine Teilgebiete vorhanden sind, wird zunächst geprüft, ob die
         tezg-Flächen einem (noch nicht angelegten) Teilgebiet zugeordnet sind.
         1.1 Keine tezg-Fläche ist einem Teilgebiet zugeordnet. Dann wird ein Teilgebiet "Teilgebiet1" 
             angelegt und alle tezg-Flächen diesem Teilgebiet zugeordnet
         1.2 Die tezg-Flächen sind einem oder mehreren noch nicht in der Tabelle "teilgebiete" vorhandenen 
             Teilgebieten zugeordnet. Dann werden entsprechende Teilgebiete mit Standardwerten angelegt.
      2 Wenn in QKan Teilgebiete vorhanden sind, wird geprüft, ob es auch tezg-Flächen gibt, die diesen
         Teilgebieten zugeordnet sind.
         2.1 Es gibt keine tezg-Flächen, die einem Teilgebiet zugeordnet sind.
             2.1.1 Es gibt in QKan genau ein Teilgebiet. Dann werden alle tezg-Flächen diesem Teilgebiet
                   zugeordnet.
             2.1.2 Es gibt in QKan mehrere Teilgebiete. Dann werden alle tezg-Flächen geographisch dem
                   betreffenden Teilgebiet zugeordnet.
         2.2 Es gibt mindestens eine tezg-Fläche, die einem Teilgebiet zugeordnet ist.
             Dann wird geprüft, ob es noch nicht zugeordnete tezg-Flächen gibt, eine Warnung angezeigt und
             diese tezg-Flächen aufgelistet.
    """

    if check_export['export_flaechensw'] or check_export['modify_flaechensw']:

        sql = 'SELECT count(*) AS anz FROM teilgebiete'
        dbQK.sql(sql)
        anztgb = int(dbQK.fetchone()[0])
        if anztgb == 0:
            # 1 Kein Teilgebiet in QKan -----------------------------------------------------------------
            createdat = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

            sql = u"""
                SELECT count(*) AS anz FROM tezg WHERE
                (teilgebiet is not NULL) AND
                (teilgebiet <> 'NULL') AND
                (teilgebiet <> '')
            """
            dbQK.sql(sql)
            anz = int(dbQK.fetchone()[0])
            if anz == 0:
                # 1.1 Keine tezg-Fläche mit Teilgebiet ----------------------------------------------------
                sql = u"""
                   INSERT INTO teilgebiete
                   ( tgnam, ewdichte, wverbrauch, stdmittel,
                     fremdwas, flaeche, kommentar, createdat, geom)
                   Values
                   ( 'Teilgebiet1', 60, 120, 14, 100, '{createdat}',
                     'Automatisch durch  QKan hinzugefuegt')""".format(createdat=createdat)
                try:
                    dbQK.sql(sql)
                except BaseException as err:
                    fehlermeldung(u"(27) Fehler in SQL:\n{sql}\n", err)
                    return False
                dbQK.commit()
            else:
                # 1.2 tezg-Flächen mit Teilgebiet ----------------------------------------------------
                # Liste der in allen tezg-Flächen vorkommenden Teilgebieten
                sql = 'SELECT teilgebiet FROM tezg WHERE teilgebiet is not NULL GROUP BY teilgebiet'
                dbQK.sql(sql)
                listeilgeb = dbQK.fetchall()
                for tgb in listeilgeb:
                    sql = u"""
                       INSERT INTO teilgebiete
                       ( tgnam, ewdichte, wverbrauch, stdmittel,
                         fremdwas, flaeche, kommentar, createdat, geom)
                       Values
                       ( '{tgnam}', 60, 120, 14, 100, '{createdat}',
                         'Hinzugefuegt aus QKan')""".format(tgnam=tgb[0], createdat=createdat)
                    try:
                        dbQK.sql(sql)
                    except BaseException as err:
                        fehlermeldung(u"(28) Fehler in SQL:\n{sql}\n", err)
                        return False
                    dbQK.commit()
                    iface.messageBar().pushMessage(u"Tabelle 'teilgebiete':\n",
                                                   u"Es wurden {} Teilgebiete hinzugefügt".format(len(tgb)),
                                                   level=QgsMessageBar.INFO, duration=3)

                # Kontrolle mit Warnung
                sql = u"""
                    SELECT count(*) AS anz
                    FROM tezg
                    LEFT JOIN teilgebiete ON tezg.teilgebiet = teilgebiete.tgnam
                    WHERE teilgebiete.pk IS NULL
                """
                dbQK.sql(sql)
                anz = int(dbQK.fetchone()[0])
                if anz > 0:
                    iface.messageBar().pushMessage(u"Fehlerhafte Daten in Tabelle 'tezg':",
                                                   u"{} Flächen sind keinem Teilgebiet zugeordnet".format(anz),
                                                   level=QgsMessageBar.WARNING, duration=0)
        else:
            # 2 Teilgebiete in QKan ----------------------------------------------------
            sql = u"""
                SELECT count(*) AS anz
                FROM tezg
                INNER JOIN teilgebiete ON tezg.teilgebiet = teilgebiete.tgnam
            """
            dbQK.sql(sql)
            anz = int(dbQK.fetchone()[0])
            if anz == 0:
                # 2.1 Keine tezg-Fläche mit Teilgebiet ----------------------------------------------------
                if anztgb == 1:
                    # 2.1.1 Es existiert genau ein Teilgebiet ---------------------------------------------
                    sql = u"UPDATE tezg SET teilgebiet = (SELECT tgnam FROM teilgebiete GROUP BY tgnam)"
                    try:
                        dbQK.sql(sql)
                    except BaseException as err:
                        fehlermeldung(u"(29) Fehler in SQL:\n{sql}\n", err)
                        return False
                    dbQK.commit()
                    iface.messageBar().pushMessage(u"Tabelle 'tezg':\n",
                                                   u"Alle Flächen in der Tabelle 'tezg' wurden einem Teilgebiet zugeordnet",
                                                   level=QgsMessageBar.INFO, duration=3)
                else:
                    # 2.1.2 Es existieren mehrere Teilgebiete ------------------------------------------
                    sql = u"""UPDATE tezg SET teilgebiet = (SELECT tgnam FROM teilgebiete
                          WHERE within(centroid(tezg.geom),teilgebiete.geom))"""
                    try:
                        dbQK.sql(sql)
                    except BaseException as err:
                        fehlermeldung(u"(30) Fehler in SQL:\n{sql}\n", err)
                        return False
                    dbQK.commit()
                    iface.messageBar().pushMessage(u"Tabelle 'tezg':\n",
                                                   u"Alle Flächen in der Tabelle 'tezg' wurden dem Teilgebiet zugeordnet, in dem sie liegen.",
                                                   level=QgsMessageBar.INFO, duration=3)

                    # Kontrolle mit Warnung
                    sql = u"""
                        SELECT count(*) AS anz
                        FROM tezg
                        LEFT JOIN teilgebiete ON tezg.teilgebiet = teilgebiete.tgnam
                        WHERE teilgebiete.pk IS NULL
                    """
                    dbQK.sql(sql)
                    anz = int(dbQK.fetchone()[0])
                    if anz > 0:
                        iface.messageBar().pushMessage(u"Fehlerhafte Daten in Tabelle 'tezg':",
                                                       u"{} Flächen sind keinem Teilgebiet zugeordnet".format(anz),
                                                       level=QgsMessageBar.WARNING, duration=0)
            else:
                # 2.2 Es gibt tezg mit zugeordnetem Teilgebiet
                # Kontrolle mit Warnung
                sql = u"""
                    SELECT count(*) AS anz
                    FROM tezg
                    LEFT JOIN teilgebiete ON tezg.teilgebiet = teilgebiete.tgnam
                    WHERE teilgebiete.pk is NULL
                """
                dbQK.sql(sql)
                anz = int(dbQK.fetchone()[0])
                if anz > 0:
                    iface.messageBar().pushMessage(u"Fehlerhafte Daten in Tabelle 'tezg':",
                                                   u"{} Flächen sind keinem Teilgebiet zugeordnet".format(anz),
                                                   level=QgsMessageBar.WARNING, duration=0)

        # --------------------------------------------------------------------------------------------
        # Export der Einzeleinleiter aus Schmutzwasser
        #
        # Referenzlisten (HE 7.8):
        #
        # ABWASSERART (Im Formular "Art"):
        #    0 = Häuslich
        #    1 = Gewerblich
        #    2 = Industriell
        #    5 = Regenwasser
        #
        # HERKUNFT (Im Formular "Herkunft"):
        #    0 = Siedlungstyp
        #    1 = Direkt
        #    2 = Frischwasserverbrauch
        #    3 = Einwohner
        #

        # HERKUNFT = 1 (Direkt) wird aus einer eigenen Tabelle "einleiter" erzeugt und ebenfalls in die 
        # HE-Tabelle "Einzeleinleiter" übertragen
        #
        # HERKUNFT = 2 (Frischwasserverbrauch) ist zurzeit nicht realisiert
        #
        # HERKUNFT = 3 (Einwohner) wird durch eine Verknüpfung aus den "tezg"-Flächen und dem verknüpften 
        # Teilgebiet erzeugt und in die HE-Tabelle "Einzeleinleiter" übertragen


        if check_export['init_flaechensw']:
            dbHE.sql("DELETE FROM EINZELEINLEITER")

        # --------------------------------------------------------------------------------------------
        # Herkunft = 1 (Direkt) und 3 (Einwohnerbezogen)

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        sql = u"""SELECT
          elnam AS elnam,
          x(geom) AS xel,
          y(geom) AS yel,
          haltnam AS haltnam,
          zufluss AS zufluss
          FROM einleit{auswahl}
        """.format(auswahl=auswahl)

        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(35) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        nr0 = nextid

        fortschritt('Export Einzeleinleiter (direkt)...', 0.92)
        for b in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            elnam, xel, yel, haltnam, zufluss = \
                ('NULL' if el is None else el for el in b)

            # Einfuegen in die Datenbank
            sql = u"""
              INSERT INTO EINZELEINLEITER
              ( XKOORDINATE, YKOORDINATE, ZUORDNUNGGESPERRT, ZUORDNUNABHEZG, ROHR,
                ABWASSERART, EINWOHNER, WASSERVERBRAUCH, HERKUNFT,
                STUNDENMITTEL, FREMDWASSERZUSCHLAG, FAKTOR, GESAMTFLAECHE,
                ZUFLUSSMODELL, ZUFLUSSDIREKT, ZUFLUSS, PLANUNGSSTATUS, NAME,
                ABRECHNUNGSZEITRAUM, ABZUG,
                LASTMODIFIED, ID) VALUES
              ( {xel}, {yel}, {zuordnunggesperrt}, {zuordnunabhezg}, '{haltnam}',
                {abwasserart}, {ew}, {wverbrauch}, {herkunft},
                {stdmittel}, {fremdwas}, {faktor}, {flaeche},
                {zuflussmodell}, {zuflussdirekt}, {zufluss}, {planungsstatus}, '{elnam}_SW_TEZG',
                {abrechnungszeitraum}, {abzug},
                '{createdat}', {nextid});
              """.format(xel = xel, yel = yel, zuordnunggesperrt = 0, zuordnunabhezg = 1,  haltnam = haltnam,
                         abwasserart = 0, ew = 0, wverbrauch = 0, herkunft = 1,
                         stdmittel = 0, fremdwas = 0, faktor = 1, flaeche = 0, 
                         zuflussmodell = 0, zuflussdirekt = 0, zufluss = zufluss, planungsstatus = 0, elnam = elnam,
                         abrechnungszeitraum = 365, abzug = 0,
                         createdat = createdat, nextid = nextid)
            try:
                dbHE.sql(sql)
            except BaseException as err:
                fehlermeldung(u"(36) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                del dbQK
                del dbHE
                return False

            nextid += 1
        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt(u'{} Einzeleinleiter (direkt) eingefuegt'.format(nextid - nr0), 0.95)


        # --------------------------------------------------------------------------------------------
        # Trockenwetter aus tezg-Flächen. Nur die Flächen werden berücksichtigt, die einem Teilgebiet 
        # mit Wasserverbrauch zugeordnet sind.
        # Herkunft = 3 (Einwohner)

        # Nur Daten fuer ausgewaehlte Teilgebiete

        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        sql = u"""SELECT
          elnam AS elnam,
          x(centroid(geom)) AS xel,
          y(centroid(geom)) AS yel,
          haltnam AS haltnam,
          wverbrauch AS wverbrauch, 
          stdmittel AS stdmittel,
          fremdwas AS fremdwas, 
          einwohner AS einwohner
          FROM einleit{auswahl}
        """.format(auswahl=auswahl)

        try:
            dbQK.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(35) SQL-Fehler in QKan-DB: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        nr0 = nextid

        fortschritt('Export Einzeleinleiter (direkt)...', 0.92)
        for b in dbQK.fetchall():

            # In allen Feldern None durch NULL ersetzen
            elnam, xel, yel, haltnam, wverbrauch, stdmittel, fremdwas, einwohner = \
                ('NULL' if el is None else el for el in b)

            # Einfuegen in die Datenbank
            sql = u"""
              INSERT INTO EINZELEINLEITER
              ( XKOORDINATE, YKOORDINATE, ZUORDNUNGGESPERRT, ZUORDNUNABHEZG, ROHR,
                ABWASSERART, EINWOHNER, WASSERVERBRAUCH, HERKUNFT,
                STUNDENMITTEL, FREMDWASSERZUSCHLAG, FAKTOR, GESAMTFLAECHE,
                ZUFLUSSMODELL, ZUFLUSSDIREKT, ZUFLUSS, PLANUNGSSTATUS, NAME,
                ABRECHNUNGSZEITRAUM, ABZUG,
                LASTMODIFIED, ID) VALUES
              ( {xel}, {yel}, {zuordnunggesperrt}, {zuordnunabhezg}, '{haltnam}',
                {abwasserart}, {einwohner}, {wverbrauch}, {herkunft},
                {stdmittel}, {fremdwas}, {faktor}, {flaeche},
                {zuflussmodell}, {zuflussdirekt}, {zufluss}, {planungsstatus}, '{elnam}_SW_TEZG',
                {abrechnungszeitraum}, {abzug},
                '{createdat}', {nextid});
              """.format(xel = xel, yel = yel, zuordnunggesperrt = 0, zuordnunabhezg = 1,  haltnam = haltnam,
                         abwasserart = 0, einwohner = einwohner, wverbrauch = wverbrauch, herkunft = 3,
                         stdmittel = stdmittel, fremdwas = fremdwas, faktor = 1, flaeche = 0, 
                         zuflussmodell = 0, zuflussdirekt = 0, zufluss = 0, planungsstatus = 0, elnam = elnam,
                         abrechnungszeitraum = 365, abzug = 0,
                         createdat = createdat, nextid = nextid)
            try:
                dbHE.sql(sql)
            except BaseException as err:
                fehlermeldung(u"(36) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
                del dbQK
                del dbHE
                return False

            nextid += 1
        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

        fortschritt(u'{} Einzeleinleiter (Einwohner bezogen) eingefuegt'.format(nextid - nr0), 0.95)

    # --------------------------------------------------------------------------------------------------
    # Setzen der internen Referenzen

    # --------------------------------------------------------------------------------------------------
    # 1. Schaechte: Anzahl Kanten

    # sql = u"""
    # select SCHACHT.ID, SCHACHT.NAME as schnam, count(*) as anz
    # from SCHACHT join ROHR
    # on (SCHACHT.NAME = ROHR.SCHACHTOBEN or SCHACHT.NAME = ROHR.SCHACHTUNTEN) group by SCHACHT.ID, SCHACHT.NAME
    # """

    # --------------------------------------------------------------------------------------------------
    # 2. Haltungen (="ROHR"): Referenz zu Schaechten (="SCHACHT")

    if False:
        sql = u"""
          UPDATE ROHR
          SET SCHACHTOBENREF =
            (SELECT ID FROM SCHACHT WHERE SCHACHT.NAME = ROHR.SCHACHTOBEN)
          WHERE EXISTS (SELECT ID FROM SCHACHT WHERE SCHACHT.NAME = ROHR.SCHACHTOBEN)
        """
        try:
            dbHE.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(13) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        sql = u"""
          UPDATE ROHR
          SET SCHACHTUNTENREF =
            (SELECT ID FROM SCHACHT WHERE SCHACHT.NAME = ROHR.SCHACHTUNTEN)
          WHERE EXISTS (SELECT ID FROM SCHACHT WHERE SCHACHT.NAME = ROHR.SCHACHTUNTEN)
        """
        try:
            dbHE.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(14) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

            # --------------------------------------------------------------------------------------------------
            # 3. Haltungen (="ROHR"): Referenz zu teileinzugsgebieten

        sql = u"""
          UPDATE ROHR
          SET TEILEINZUGSGEBIETREF =
            (SELECT ID FROM TEILEINZUGSGEBIET WHERE TEILEINZUGSGEBIET.NAME = ROHR.TEILEINZUGSGEBIET)
          WHERE EXISTS (SELECT ID FROM TEILEINZUGSGEBIET WHERE TEILEINZUGSGEBIET.NAME = ROHR.TEILEINZUGSGEBIET)
        """
        try:
            dbHE.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(15) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

            # --------------------------------------------------------------------------------------------------
            # 3. Abflussparameter: Referenz zu Bodenklasse

        sql = u"""
          UPDATE ABFLUSSPARAMETER
          SET BODENKLASSEREF =
            (SELECT ID FROM BODENKLASSE WHERE BODENKLASSE.NAME = ABFLUSSPARAMETER.BODENKLASSE)
          WHERE EXISTS (SELECT ID FROM BODENKLASSE WHERE BODENKLASSE.NAME = ABFLUSSPARAMETER.BODENKLASSE)
        """
        try:
            dbHE.sql(sql)
        except BaseException as err:
            fehlermeldung(u"(16) SQL-Fehler in Firebird: \n{}\n".format(err), sql)
            del dbQK
            del dbHE
            return False

        dbHE.sql("UPDATE ITWH$PROGINFO SET NEXTID = {:d}".format(nextid))
        dbHE.commit()

    del dbQK
    del dbHE

    fortschritt('Ende...', 1)

    iface.messageBar().pushMessage(u"Status: ", u"Datenexport abgeschlossen.",
                                   level=QgsMessageBar.INFO, duration=0)


# ----------------------------------------------------------------------------------------------------------------------

# Verzeichnis der Testdaten
pfad = 'C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/modelldb_itwh'

database_HE = os.path.join(pfad, 'muster-modelldatenbank.idbf')
database_QKan = os.path.join(pfad, 'muster.sqlite')

if __name__ == '__main__':
    exportKanaldaten(database_HE, database_QKan)
elif __name__ == '__console__':
    # QMessageBox.information(None, "Info", "Das Programm wurde aus der QGIS-Konsole aufgerufen")
    exportKanaldaten(database_HE, database_QKan)
elif __name__ == '__builtin__':
    # QMessageBox.information(None, "Info", "Das Programm wurde aus der QGIS-Toolbox aufgerufen")
    exportKanaldaten(database_HE, database_QKan)
# else:
# QMessageBox.information(None, "Info", "Die Variable __name__ enthält: {0:s}".format(__name__))
