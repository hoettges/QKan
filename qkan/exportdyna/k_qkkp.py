# -*- coding: utf-8 -*-

"""
  Export Kanaldaten in eine DYNA-Datei (*.ein)
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
import time

from qgis.PyQt.QtGui import QProgressBar

from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import fortschritt, fehlermeldung, meldung, checknames
from qkan.linkflaechen.updatelinks import updatelinkfl, updatelinksw


logger = logging.getLogger('QKan')

progress_bar = None

# Hilfsfunktionen --------------------------------------------------------------------------

# Funktion zur formatierten Ausgabe von Fließkommazahlen

def formf(zahl, anz):
    """Formatiert eine Fließkommazahl so, dass sie in einer vorgegebenen Anzahl von Zeichen
       mit maximaler Genauigkeit dargestellt werden kann.
    """
    if zahl is None:
        if anz == 1:
            erg = '.'
        else:
            erg = '{}0.'.format(' '*(anz-2))
        return erg

    if zahl < 0:
        logger.error(u'Fehler in k_qkkp.formf (2): Zahl ist negativ', u'zahl = {}\nanz = {}\n'.format(zahl, anz))
        return None

    nv = int(math.log10(zahl))          # Anzahl Stellen vor dem Komma.
    dez = True                          # In der Zahl kommt ein Dezimalkomma vor. Wird benötigt wenn 
                                        # Nullen am Ende gelöscht werden sollen

    # Prüfung, ob Zahl (auch nach Rundung!) kleiner 1 ist, so dass die führende Null weggelassen
    # werden kann

    if round(zahl, anz-1) < 1:
        fmt = '{0:' + '{:d}.{:d}f'.format(anz+1, anz-1) + '}'
        erg = fmt.format(zahl)[1:]
    else:
        if int(math.log10(round(zahl, 0))) + 1 > anz:
            logger.error(u'Fehler in k_qkkp.formf (3): Zahl ist zu groß!', u'zahl = {}\nanz = {}\n'.format(zahl, anz))
            return None
        # Korrektur von nv, für den Fall, dass zahl nahe an nächster 10-Potenz
        nv = int(math.log10(round(zahl, max(0,anz-2-nv))))
        if nv + 1 == anz:
            # Genau soviel Platz wie Vorkommastellen
            fmt = '{0:' + '{:d}.{:d}f'.format(anz, anz-1-nv) + '}'
            dez = False                                 # Nullen am Ende dürfen nicht gelöscht werden
        elif nv + 1 == anz - 1:
            # Platz für alle Vorkommastellen und das Dezimalzeichen (dieses muss ergänzt werden)
            fmt = '{0:' + '{:d}.{:d}f'.format(anz, anz-2-nv) + '}.'
            dez = False                                 # obsolet, weil Dezimalpunkt am Ende
        elif nv + 1 < anz - 1:
            # Platz für mindestens eine Nachkommastelle
            fmt = '{0:' + '{:d}.{:d}f'.format(anz, anz-2-nv) + '}'
        else:
            logger.error(u'Fehler in k_qkkp.formf (2):', u'zahl = {}\nanz = {}\n'.format(zahl, anz))
            return None
        erg = fmt.format(zahl)

        # Nullen am Ende löschen
        if dez:
            fmt = '{0:>' + '{:d}s'.format(anz) + '}'
            erg = fmt.format(erg.rstrip('0'))
    return erg


# Funktionen zum Schreiben der DYNA-Daten. Werden aus exportKanaldaten aufgerufen 
def write12(dbQK, df, dynakeys_id, dynakeys_ks, mindestflaeche, dynaprof_choice, dynabef_choice, 
             dynaprof_nam, dynaprof_key, ausw_and, auswahl):
    '''Schreiben der DYNA-Typ12-Datenzeilen

    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:             DBConnection

    :df:                    zu Schreibende DYNA-Datei
    :type df:               String

    :dynakeys_id:           Liste der DYNA-Schlüssel für Rauheitsbeiwerte, Material und Regenspende
    :type dbQK:             List

    :dynakeys_ks:           Liste der Rauheitsbeiwerte in der DYNA-Datei
    :type dbQK:             List

    :mindestflaeche:        Mindestflächengröße, ab der Flächenobjekte berücksichtigt werden   
    :type dbQK:             Float

    :dynaprof_choice:       Option, wie die Zuordnung der Querprofile aus QKan zu den in der DYNA-Datei 
                            vorhandenen erfolgt: Über den gemeinsamen Profilnamen oder den gemeinsamen Profilkey
    :type dbQK:             String

    :dynabef_choice:        Option für die Haltungsgesamtfläche: Bestimmung als Summe der Einzelflächen 
                            oder über das tezg-Flächenobjekt
    :type dbQK:             String

    :dynaprof_nam:          Liste der Querprofilnamen aus der Vorlage-DYNA-Datei
    :type dbQK:             List

    :dynaprof_key:          Liste der Querprofilschlüssel aus der Vorlage-DYNA-Datei
    :type dbQK:             List

    :ausw_and:              SQL-Textbaustein, um eine Bedingung mit "AND" anzuhängen
    :type dbQK:             String

    :auswahl:               SQL-Textbaustein mit der Bedingung zur Filterung auf eine Liste von Teilgebieten
    :type dbQK:             String

    :returns: void
    '''

    # Optionen zur Berechnung der befestigten Flächen
    # ... benötigt keine Modifikation der Abfrage

    # Optionen zur Zuordnung des Profilschlüssels
    if dynaprof_choice == u'profilname':
        sql_prof1 = u'h.profilnam AS profilid'
        sql_prof2 = ''
    elif dynaprof_choice == u'profilkey':
        sql_prof1 = u'p.kp_nr AS profilid'
        sql_prof2 = """
        INNER JOIN profile as p
        ON h.profilnam = p.profilnam"""
    else:
        logger.error(u'Fehler in k_qkkp.write12: Unbekannte Option in dynaprof_choice: {}'.format(dynaprof_choice))

    sql = u"""
        WITH flintersect AS (
            SELECT lf.flnam AS flnam, lf.haltnam AS haltnam, fl.neigkl AS neigkl, fl.abflussparameter AS abflussparameter, 
                area(tg.geom) AS fltezg,
                CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
            FROM linkfl AS lf
            INNER JOIN flaechen AS fl
            ON lf.flnam = fl.flnam
            LEFT JOIN tezg AS tg
            ON lf.tezgnam = tg.flnam),
        halflaech AS (
            SELECT
                fi.haltnam AS haltnam, 
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN area(fi.geom)/10000.
                    ELSE 0 END) AS flbef,
                sum(area(fi.geom)/10000.) AS flges,
                fltezg,
                max(neigkl) AS neigkl
            FROM flintersect AS fi
            INNER JOIN abflussparameter AS ap
            ON fi.abflussparameter = ap.apnam
            WHERE area(fi.geom) > {mindestflaeche}{ausw_and}{auswahl}
            GROUP BY fi.haltnam)
        SELECT 
            d.kanalnummer AS kanalnummer,
            d.haltungsnummer AS haltungsnummer, 
            h.laenge AS laenge,
            so.deckelhoehe AS deckelhoehe, 
            coalesce(h.sohleoben, so.sohlhoehe) AS sohleob,
            coalesce(h.sohleunten, su.sohlhoehe) AS sohleun,
            'O' AS material, 
            {sql_prof1}, 
            h.hoehe AS profilhoehe, 
            h.ks AS ks, 
            f.flbef AS flbef, 
            f.flges AS flges,
            f.fltezg AS fltezg,
            3 AS abfltyp, 
            e.zufluss AS qzu, 
            0 AS ewdichte, 
            0 AS tgnr, 
            f.neigkl AS neigkl,
            a.kp_nr AS entwart, 
            0 AS haltyp,
            h.schoben AS schoben, 
            h.schunten AS schunten,
            so.xsch AS xob, 
            so.ysch AS yob
        FROM haltungen AS h
        INNER JOIN dynahal AS d
        ON h.pk = d.pk
        INNER JOIN schaechte AS so
        ON h.schoben = so.schnam
        INNER JOIN schaechte AS su
        ON h.schunten = su.schnam{sql_prof2}
        LEFT JOIN halflaech AS f
        ON h.haltnam = f.haltnam
        LEFT JOIN einleit AS e
        ON e.haltnam = h.haltnam
        LEFT JOIN entwaesserungsarten AS a
        ON h.entwart = a.bezeichnung
    """.format(mindestflaeche=mindestflaeche, ausw_and=ausw_and, auswahl=auswahl, sql_prof1=sql_prof1, sql_prof2=sql_prof2)

    if not dbQK.sql(sql, u'dbQK: k_qkkp.write12 (1)'):
        return False

    fortschritt(u'Export Datensätze Typ12', 0.3)
    progress_bar.setValue(30)
    # createdat = time.strftime(u'%d.%m.%Y %H:%M:%S', time.localtime())

    # Lesen der Daten aus der SQL-Abfrage und Schreiben in die DYNA-Datei --------------------
    for attr in dbQK.fetchall():

        # Attribute in Variablen speichern
        (kanalnummer, haltungsnummer, laenge, deckelhoehe, sohleob, sohleun, material, 
         profilid, profilhoehe, ks, flbef, flges, fltezg, abfltyp, qzu, ewdichte, tgnr, 
         neigkl, entwart, haltyp, schoben, schunten, xob, yob) = attr

        laenge_t = formf(laenge, 7)
        deckelhoehe_t = formf(deckelhoehe, 7)
        sohleob_t = formf(sohleob, 7)
        sohleun_t = formf(sohleun, 7)
        profilhoehe_t = formf(profilhoehe, 4)
        qzu_t = formf(qzu, 5)
        xob_t = formf(xob, 14)
        yob_t = formf(yob, 14)
         
        # Schlüssel für DYNA einsetzen
        try:
            kskey = dynakeys_id[[u'{0:10.6f}'.format(kb) for kb in dynakeys_ks].index(u'{0:10.6f}'.format(ks))]
            # logger.debug(u'ks= {0:10.6f}\ndynakeys_ks= {1:s}\ndynakeys_id= {2:s}\nkskey= {3:s}'.format(
                # ks,
                # ', '.join([u'{0:10.6f}'.format(kb) for kb in dynakeys_ks]),
                # ', '.join(dynakeys_id),
                # kskey
                # ))
        except BaseException as err:
            fehlermeldung(u'Fehler in k_qkkp.write12 (1): {}'.format(err), 
                      u'ks {} konnte in dynakeys_ks nicht gefunden werden\ndynakeys_ks = {}'.format( \
                      ks, str(dynakeys_ks)))

        if flges is None:
            flges_t = '     '
            befgrad_t = '  '
            neigkl_t = ' '
            flges = 0
            befgrad = 0
            neigkl = 0
        elif dynabef_choice == u'flaechen':
            if flges == 0:
                flges_t = '    0'
                befgrad_t = ' 0'
                neigkl_t = ' '
                flges = 0
                befgrad = 0
                neigkl = 0
            else:
                befgrad = int(round(flbef / flges * 100.,0))
                if befgrad < 0:
                    befgrad = 0
                elif befgrad > 99:
                    befgrad = 99
                flges_t = formf(flges, 5)
                befgrad_t = '{0:2d}'.format(befgrad)
                neigkl_t = '{0:1d}'.format(neigkl)

        elif dynabef_choice == u'tezg':
            if fltezg == 0:
                flges_t = '    0'
                befgrad_t = ' 0'
                neigkl_t = ' '
                flges = 0
                befgrad = 0
                neigkl = 0
            else:
                befgrad = flbef / fltezg * 100.
                if befgrad < 0:
                    befgrad = 0
                elif befgrad > 99:
                    befgrad = 99
                flges_t = formf(flges, 5)
                befgrad_t = '{0:2d}'.format(befgrad)
                neigkl_t = '{0:1d}'.format(neigkl)

        # Auswahl dynaprof_choice
        if dynaprof_choice == u'profilname':
            try:
                profilkey = dynaprof_key[dynaprof_nam.index(profilid)]
            except BaseException as err:
                fehlermeldung(u'Fehler in k_qkkp.write12 (2): {}'.format(err), 
                    u'Profilkey {id} konnte in interner Zuordnungsliste nicht gefunden werden\n')
                logger.debug('dynprof_nam: {}'.format(', '.join(dynaprof_nam)))

        elif dynaprof_choice == u'profilkey':
            profilkey = profilid

        try:
            zeile = '12    {kanalnummer:>8s}{haltungsnummer:>3s}{laenge:7s}'.format(
                        kanalnummer=kanalnummer, haltungsnummer=haltungsnummer, laenge=laenge_t) + \
                    '{deckelhoehe:7s}{sohleob:7s}{sohleun:7s}{material:1s}'.format(
                        deckelhoehe=deckelhoehe_t, sohleob=sohleob_t, sohleun=sohleun_t, material=material) + \
                    '{profilkey:2s}{profilhoehe:4s}{kskey:1s}'.format(
                        profilkey=profilkey, profilhoehe=profilhoehe_t, kskey=kskey) + \
                    '{befgrad:2s}  {abfltyp:1d}'.format(
                        befgrad=befgrad_t, abfltyp=abfltyp) + \
                    '{qzu:5s}{ewdichte:3d}{tgnr:5d}'.format(
                        qzu=qzu_t, ewdichte=ewdichte, tgnr=tgnr) + \
                    '{flges:5s}{neigkl:1s}{entwart:1d}{haltyp:1d}'.format(
                        flges=flges_t, neigkl=neigkl_t, entwart=entwart, haltyp=haltyp) + \
                    '  {schoben:>12s} {schunten:>12s}{xob:14s}{yob:14s}\n'.format(
                    schoben=schoben, schunten=schunten, xob=xob_t, yob=yob_t)

            # logger.debug(
                # 'material = {}\n'.format(material) + \
                # 'profilkey = {}\n'.format(profilkey) + \
                # 'profilhoehe = {}\n'.format(profilhoehe) + \
                # 'ks = {}\n'.format(ks) + \
                # 'befgrad = {}\n'.format(befgrad) + \
                # 'abfltyp = {}\n'.format(abfltyp) + \
                # 'qzu = {}\n'.format(qzu) + \
                # 'ewdichte = {}\n'.format(ewdichte))

            df.write(zeile)
        except BaseException as err:
            fehlermeldung(u'Fehler in QKan_ExportDYNA.write12: {}\n'.format(err), 
                'Datentypfehler in Variablenliste:\n' + \
                'kanalnummer = {}\n'.format(kanalnummer) + \
                'haltungsnummer = {}\n'.format(haltungsnummer) + \
                'laenge = {}\n'.format(laenge) + \
                'deckelhoehe = {}\n'.format(deckelhoehe) + \
                'sohleob = {}\n'.format(sohleob) + \
                'sohleun = {}\n'.format(sohleun) + \
                'material = {}\n'.format(material) + \
                'profilkey = {}\n'.format(profilkey) + \
                'profilhoehe = {}\n'.format(profilhoehe) + \
                'ks = {}\n'.format(ks) + \
                'befgrad = {}\n'.format(befgrad) + \
                'abfltyp = {}\n'.format(abfltyp) + \
                'qzu = {}\n'.format(qzu) + \
                'ewdichte = {}\n'.format(ewdichte) + \
                'tgnr = {}\n'.format(tgnr) + \
                'flges = {}\n'.format(flges) + \
                'neigkl = {}\n'.format(neigkl) + \
                'entwart = {}\n'.format(entwart) + \
                'haltyp = {}\n'.format(haltyp) + \
                'schoben = {}\n'.format(schoben) + \
                'schunten = {}\n'.format(schunten) + \
                'xob = {}\n'.format(xob) + \
                'yob = {}\n'.format(yob))
            return False

    return True


def write16(dbQK, df, ausw_and, auswahl):
    '''Schreiben der DYNA-Typ16-Datenzeilen

    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:             DBConnection

    :df:                    zu Schreibende DYNA-Datei
    :type df:               String

    :ausw_and:              SQL-Textbaustein, um eine Bedingung mit "AND" anzuhängen
    :type dbQK:             String

    :auswahl:               SQL-Textbaustein mit der Bedingung zur Filterung auf eine Liste von Teilgebieten
    :type dbQK:             String

    :returns: void
    '''

    # SQL-Baustein, um die Bedingung {auswahl} um den Tabellennamen zu ergänzen
    if auswahl == '':
        ausw_tab = ''
    else:
        ausw_tab = 'schaechte'

    # Zusammenstellen der Daten. 
    sql = u"""
        WITH v_anzan AS
    (   SELECT h.schunten, count(*) AS anzahl
        FROM haltungen AS h
        GROUP BY h.schunten),
    v_anzab AS
    (   SELECT h.schoben, count(*) AS anzahl
        FROM haltungen AS h
        GROUP BY h.schoben),
    v_halan AS
    (   SELECT h.schunten, s.xsch AS xschob, s.ysch AS yschob,
        d.kanalnummer AS kanalnummer,
        d.haltungsnummer AS haltungsnummer
        FROM haltungen AS h
        INNER JOIN dynahal AS d
        ON h.pk = d.pk
        INNER JOIN schaechte AS s
        ON s.schnam = h.schoben),
    v_halab AS
    (   SELECT h.schoben, s.xsch AS xschun, s.ysch AS yschun,
        d.kanalnummer AS kanalnummer,
        d.haltungsnummer AS haltungsnummer
        FROM haltungen AS h
        INNER JOIN dynahal AS d
        ON h.pk = d.pk
        INNER JOIN schaechte AS s
        ON s.schnam = h.schunten)

    SELECT s.schnam, 
        han.kanalnummer AS an_kanalnummer, han.haltungsnummer AS an_haltungsnummer, 
        hab.kanalnummer AS ab_kanalnummer, hab.haltungsnummer AS ab_haltungsnummer, 
        coalesce(anzan.anzahl, 0) AS an_anz, 
        coalesce(anzab.anzahl, 0) AS ab_anz
    FROM schaechte AS s
    LEFT JOIN v_anzan AS anzan
    ON anzan.schunten = s.schnam
    LEFT JOIN v_anzab AS anzab
    ON anzab.schoben = s.schnam
    LEFT JOIN v_halan AS han
    ON han.schunten = s.schnam
    LEFT JOIN v_halab AS hab
    ON hab.schoben = s.schnam
    WHERE anzab.anzahl <> 1 OR anzan.anzahl <> 1{ausw_and}{ausw_tab}{auswahl}
    ORDER BY s.schnam, han.kanalnummer, han.haltungsnummer
    """.format(ausw_and=ausw_and, ausw_tab=ausw_tab, auswahl=auswahl)

    if not dbQK.sql(sql, u'dbQK: k_qkkp.write16 (1)'):
        return False

    akt_schnam = ''             # Identifiziert Datensätze zum gleichen Knoten
    knotennr = 0                # Knotennummer

    for i, attr in enumerate(dbQK.fetchall()):

        # Attribute in Variablen speichern
        (schnam, an_kanalnummer, an_haltungsnummer, ab_kanalnummer, ab_haltungsnummer, an_anz, ab_anz) = attr

        if schnam != akt_schnam:
            # Vorherigen Knoten schreiben. 
            if i > 1: 
                # Dies darf erst ab 2. gelesener Zeile geschehen...

                df.write('{0:15s}{1:}{2:}\n'.format(zeilkn, zeilan, zeilab))

            # Nächsten Knoten initialisieren

            knotennr += 1               # Knotennummer inkrementieren
            akt_i = i                   # Nummer aktualisieren
            # Datensatz Typ16 schreiben (Achtung: Letzter Datensatz wird nach Abschluss der Schleife geschrieben)
            zeilkn = '16{knotennr:4d}  {an_anz:1d}{ab_anz:1d}     '.format(
                        knotennr=knotennr, an_anz=an_anz, ab_anz=ab_anz)

            # Es gibt entweder mindestens eine ankommende oder abgehende Haltung
            if an_anz > 0:
                zeilan = ' 1{kanalnummer:>8s}{haltungsnummer:>3s}'.format(
                        kanalnummer=an_kanalnummer, haltungsnummer=an_haltungsnummer)
                zeilab = ''                 # Abgehende Haltungen zurücksetzen
            else:
                zeilan = ''                 # Ankommende Haltungen zurücksetzen
                if ab_anz > 0:
                    zeilab = ' 2{kanalnummer:>8s}{haltungsnummer:>3s}'.format(
                            kanalnummer=ab_kanalnummer, haltungsnummer=ab_haltungsnummer)
                else:
                    logger.error(u'Fehler in k_qkkp.write16 (1):', 
                                 u'Anzahl ankommende ({}) und abgehende ({}) Haltungen = 0?\n'.format(an_anz, ab_anz))
                    return None

        else:
            # Folgedatensatz zum selben Knoten
            akt_an = (i - akt_i) // an_anz               # Lfd. Nummer der ankommenden Haltung
            akt_ab = (i - akt_i) % ab_anz

            if akt_an == 0:
                # abgehende Haltung übernehmen; nur im ersten Teilblock
                zeilab += ' 2{kanalnummer:>8s}{haltungsnummer:>3s}'.format(
                        kanalnummer=ab_kanalnummer, haltungsnummer=ab_haltungsnummer)
            if akt_ab == 0:
                # ankommende Haltung übernehmen; jeweils zu Beginn jedes Teilblocks
                zeilan += ' 1{kanalnummer:>8s}{haltungsnummer:>3s}'.format(
                        kanalnummer=an_kanalnummer, haltungsnummer=an_haltungsnummer)

    else:
        # Letzter Typ16-Datensatz kann erst jetzt geschrieben werden. 
        df.write('{0:15s}{1:}{2:}\n'.format(zeilkn, zeilan, zeilab))

    return True


def write41(dbQK, df, ausw_and, auswahl):
    '''Schreiben der DYNA-Typ41-Datenzeilen (Endschächte = Auslässe)

    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:             DBConnection

    :df:                    zu Schreibende DYNA-Datei
    :type df:               String

    :ausw_and:              SQL-Textbaustein, um eine Bedingung mit "AND" anzuhängen
    :type dbQK:             String

    :auswahl:               SQL-Textbaustein mit der Bedingung zur Filterung auf eine Liste von Teilgebieten
    :type dbQK:             String

    :returns: void
    '''

    # SQL-Baustein, um die Bedingung {auswahl} um den Tabellennamen zu ergänzen
    if auswahl == '':
        ausw_tab = ''
    else:
        ausw_tab = 'schaechte'

    # Zusammenstellen der Daten. 
    sql = u"""
        SELECT
            d.kanalnummer AS kanalnummer,
            d.haltungsnummer AS haltungsnummer,
            s.deckelhoehe AS deckelhoehe, 
            s.xsch AS xsch, 
            s.ysch AS ysch, 
            s.schnam AS schnam
        FROM dynahal AS d
        INNER JOIN schaechte AS s
        ON s.schnam = d.schunten
        WHERE s.schachttyp = 'Auslass'{ausw_and}{ausw_tab}{auswahl}
    """.format(ausw_and=ausw_and, ausw_tab=ausw_tab, auswahl=auswahl)

    if not dbQK.sql(sql, u'dbQK: k_qkkp.write41 (1)'):
        return False

    for attr in dbQK.fetchall():
        
        # Attribute in Variablen speichern
        (kanalnummer, haltungsnummer, deckelhoehe, xsch, ysch, schnam) = attr

        deckelhoehe_t = formf(deckelhoehe, 7)
        xsch_t = formf(xsch, 14)
        ysch_t = formf(ysch, 14)

        df.write('41    {kanalnummer:>8s}{haltungsnummer:>3s}       '.format(
                    kanalnummer=kanalnummer, haltungsnummer=haltungsnummer) + \
                '{deckelhoehe:7s}{xsch:14s}{ysch:14s}{schnam:>12s}'.format(
                    deckelhoehe=deckelhoehe_t, xsch=xsch_t, ysch=ysch_t, schnam=schnam))

    return True



# Hauptfunktion ----------------------------------------------------------------------------
def exportKanaldaten(iface, dynafile, template_dyna, dbQK, dynabef_choice, dynaprof_choice, liste_teilgebiete, autokorrektur, 
                     autonum_dyna, fangradius=0.1, mindestflaeche=0.5, max_loops=1000, datenbanktyp=u'spatialite'):
    '''Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine HE-Firebird-Datenbank.

    :dynafile:              Zu Schreibende DYNA-Datei; kann mit Vorlagedatei identisch sein
    :type dynafile:         string

    :template_dyna:         Vorlage-DYNA-Datei
    :type template_dyna:    string

    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:             DBConnection

    :liste_teilgebiete:     Liste der ausgewählten Teilgebiete
    :type liste_teilgebiete: String

    :autokorrektur:         Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                            werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                            abgebrochen.
    :autonum_dyna:          Sollen die Haltungen in der DYNA-Zusatztabelle nummeriert werden?
    :boolean:

    :type autokorrektur:    String

    :fangradius:            Suchradius, mit dem an den Enden der Verknüpfungen (linkfl, linksw) eine 
                            Haltung bzw. ein Einleitpunkt zugeordnet wird. 
    :type fangradius:       Float

    :datenbanktyp:          Typ der Datenbank (SpatiaLite, PostGIS)
    :type datenbanktyp:     String

    :check_export:          Liste von Export-Optionen
    :type check_export:     Dictionary

    :returns: void
    '''

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"", u"Export in Arbeit. Bitte warten.")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)

    # DYNA-Vorlagedatei lesen. Dies geschieht zu Beginn, damit Zieldatei selbst Vorlage sein kann!
    dynatemplate = open(template_dyna).readlines()

    # DYNA-Datei löschen, falls schon vorhanden
    if os.path.exists(dynafile):
        try:
            os.remove(dynafile)
        except BaseException as err:
            fehlermeldung(u'Fehler (33) in QKan_ExportDYNA {}'.format(err), 
                'Die DYNA-Datei ist schon vorhanden und kann nicht ersetzt werden: {}'.format(repr(err)))
            return False

    fortschritt(u"DYNA-Datei aus Vorlage kopiert...", 0.01)
    progress_bar.setValue(1)

    # --------------------------------------------------------------------------------------------------
    # Zur Abschaetzung der voraussichtlichen Laufzeit

    dbQK.sql(u"SELECT count(*) AS n FROM schaechte")
    anzdata = float(dbQK.fetchone()[0])
    fortschritt(u"Anzahl Schächte: {}".format(anzdata))

    dbQK.sql(u"SELECT count(*) AS n FROM haltungen")
    anzdata += float(dbQK.fetchone()[0])
    fortschritt(u"Anzahl Haltungen: {}".format(anzdata))

    dbQK.sql(u"SELECT count(*) AS n FROM flaechen")
    anzdata += float(dbQK.fetchone()[0]) * 2
    fortschritt(u"Anzahl Flächen: {}".format(anzdata))

    # --------------------------------------------------------------------------------------------
    # Haltungsnummerierung, falls aktiviert
    # Diese ist nur für das gesamte Entwässerungsnetz möglich, damit keine Redundanzen entstehen.

    # Nur Daten fuer ausgewaehlte Teilgebiete
    if len(liste_teilgebiete) != 0:
        ausw_where = u""" WHERE """
        ausw_and = u""" AND """
        auswahl = u"""teilgebiet in ('{}')""".format(u"', '".join(liste_teilgebiete))
    else:
        ausw_where = u""
        ausw_and = u""
        auswahl = u""

    if autonum_dyna:

        # Zurücksetzen von "kanalnummer" und "haltungsnummer"
        sql = u"""
            UPDATE dynahal
            SET kanalnummer = NULL,
                haltungsnummer = NULL{ausw_where}{auswahl}""".format(ausw_where=ausw_where, auswahl=auswahl)

        if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (1)'):
            return False

        dbQK.commit()

        # Einfügen der Haltungsdaten in die Zusatztabelle "dynahal"

        sql = u"""
            WITH halnumob AS (
                SELECT schunten, count(*) AS anzahl
                FROM haltungen
                GROUP BY schunten
            ), halnumun AS (
                SELECT schoben, count(*) AS anzahl
                FROM haltungen
                GROUP BY schoben
            )
            INSERT INTO dynahal
            (pk, haltnam, schoben, schunten, teilgebiet, anzobob, anzobun, anzunun, anzunob)
            SELECT
                haltungen.pk, haltungen.haltnam, haltungen.schoben, haltungen.schunten, haltungen.teilgebiet,
                coalesce(haltobob.anzahl, 0) AS anzobob, coalesce(haltobun.anzahl, 0) AS anzobun,
                coalesce(haltunun.anzahl, 0) AS anzunun, coalesce(haltunob.anzahl, 0) AS anzunob
            FROM haltungen
            LEFT JOIN halnumob AS haltobob
            ON haltungen.schoben = haltobob.schunten
            LEFT JOIN halnumun AS haltobun
            ON haltungen.schoben = haltobun.schoben
            LEFT JOIN halnumun AS haltunun
            ON haltungen.schunten = haltunun.schoben
            LEFT JOIN halnumob AS haltunob
            ON haltungen.schunten = haltunob.schunten
            WHERE haltnam NOT IN (
                SELECT haltnam FROM dynahal)
                {ausw_and}{auswahl}""".format(ausw_and=ausw_and, auswahl=auswahl)

        if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (2)'):
            return False

        # Zurücksetzen von "kanalnummer" und "haltungsnummer"
        
        sql = u"""
            UPDATE dynahal
            SET kanalnummer = NULL,
                haltungsnummer = NULL
                {ausw_where}{auswahl}""".format(ausw_where=ausw_where, auswahl=auswahl)

        if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (3)'):
            return False

        # Nummerierung der Anfangshaltungen

        if len(liste_teilgebiete) == 0:
            sql = u"""
                UPDATE dynahal
                SET kanalnummer = ROWID, haltungsnummer = 1
                WHERE anzobob <> 1 OR anzobun <> 1
                    {ausw_and}{auswahl}""".format(ausw_and=ausw_and, auswahl=auswahl)

        if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (4)'):
            return False

        dbQK.commit()

        # Weitergabe der Nummerierung an die Folgehaltung im selben Strang, 
        # solange change() nicht 0 zurückgibt

        nchange = 1         # Initialisierung
        changelog = []
        nlimit = 0
        while nchange > 0 and nlimit < max_loops:
            sql = u"""
                UPDATE dynahal
                SET 
                    kanalnummer = 
                    (   SELECT kanalnummer
                        FROM dynahal AS dh
                        WHERE dh.schunten = dynahal.schoben),
                    haltungsnummer = 
                    (   SELECT haltungsnummer + 1
                        FROM dynahal AS dh
                        WHERE dh.schunten = dynahal.schoben)
                WHERE
                    dynahal.anzobob = 1 AND
                    dynahal.anzobun = 1 AND
                    dynahal.kanalnummer IS NULL
                    {ausw_and}{auswahl};
                """.format(ausw_and=ausw_and, auswahl=auswahl)

            if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (5)'):
                return False

            sql = u"""
                SELECT changes();
                """

            if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (6)'):
                return False

            nchange = int(dbQK.fetchone()[0])       # Zahl der zuletzt geänderten Datensätze
            changelog.append(nchange)

        dbQK.commit()

        if nlimit >= max_loops:
            fehlermeldung(u'Fehler in QKan_ExportDYNA', 
                u'{} Schleifendurchläufe in der Autonummerierung. Gegebenenfalls muss max_loops in der config-Datei angepasst werden...')

        logger.debug(u'Anzahl Änderungen für DYNA:\n{}'.format(u', '.join([str(n) for n in changelog])))

    else:
        # Keine Autonummerierung. Dann müssen die Haltungsnamen so vergeben sein, dass sich Kanal- und Haltungs-
        # nummer daraus wieder herstellen lassen (8 Zeichen für Kanal + "-" + 3 Zeichen für Haltungsnummer).

        sql = u"""DELETE FROM dynahal"""
        if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (7): Daten in Tabelle dynahal konnten nicht gelöscht werden'):
                return False

        sql = u"""
            INSERT INTO dynahal
            (pk, haltnam, kanalnummer, haltungsnummer, schoben, schunten, teilgebiet)
            SELECT
                h.pk, h.haltnam,
                substr(h.haltnam, 1, instr(h.haltnam, '-')-1) AS kn,
                substr(h.haltnam, instr(h.haltnam, '-') - length(h.haltnam)) AS hn,
                h.schoben, h.schunten, h.teilgebiet
            FROM haltungen AS h
            WHERE haltnam NOT IN (
                SELECT haltnam FROM dynahal)
                {ausw_and}{auswahl}""".format(ausw_and=ausw_and, auswahl=auswahl)

        if not dbQK.sql(sql, u'dbQK: k_qkkp.init_dynahal (8)'):
                return False

    progress_bar.setValue(20)

    # DYNA-Schlüsselwerte für Rauheit, Material und Regenspende ------------------------------------------------------

    # Einlesen der Schlüsselwerte aus der DYNA-Datei, die bereits als Textliste dynatemplate vorliegt
    # Da die keys willkürlich sind, werden zunächst die 4 Spalten getrennt gelesen und bei Bedarf aus 
    # den Daten der QKan-Datenbank ergänzt. 

    typ05 = False
    dynakeys_id = []
    dynakeys_mat = []
    dynakeys_spende = []
    dynakeys_ks = []

    for z in dynatemplate:
        if typ05:
            if z[:2] == '##':
                pass
            elif z[:2] == '05':
                id = z[3:4]
                mat = z[5:9]
                spende = z[10:20]
                ks = z[20:30]
                dynakeys_id.append(id)
                if mat.strip() != '':
                    dynakeys_mat.append(mat)
                if spende.strip() != '':
                    dynakeys_spende.append(spende)
                if ks.strip() != '':
                    dynakeys_ks.append(float(ks))
            else:
                break
        if z[:6] == '++SCHL':
            typ05 = True
    else:
        dynakeys_id = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
        dynakeys_mat = [u'Az', u'B', u'Stz']
        dynakeys_ks = [0., 0.4, 0.75, 1.5]

    # Prüfung, ob alle Werte, die in der QKan-Datenbank vorkommen, bereits vorhanden sind. 

    sql = u"""
        SELECT printf('%10.6f',ks) AS ks
        FROM haltungen
        GROUP BY ks
    """
    if not dbQK.sql(sql, u"QKan_ExportDYNA.k_qkkp (1) "):
        return False

    daten = dbQK.fetchall()
    for kslis in daten:
        ks_new = kslis[0]
        if ks_new not in [u'{0:10.6f}'.format(ks) for ks in dynakeys_ks]:
            dynakeys_ks.append(ks_new)

    # So viele Schlüssel ergänzen, bis Anzahl in dynakeys_ks erreicht (meistens schon der Fall...)
    next_id = dynakeys_id[-1]
    while len(dynakeys_ks) > len(dynakeys_id):
        n = ord(next_id) + 1
        if n == 58:
            next_id = u'A'
        else:
            next_id = chr(n)
        dynakeys_id.append(next_id)

    # Übrige DYNA-Key-Listen auf gleich Länge auffüllen
    dynakeys_mat += [''] * (len(dynakeys_id) - len(dynakeys_mat))
    dynakeys_ks += [0] * (len(dynakeys_id) - len(dynakeys_ks))

    # DYNA-Profile lesen und mit den benötigten Profilen abgleichen -----------------------------------

    dynaprof_nam = []
    dynaprof_key = []

    # Initialisierungen für Profile
    profilmodus = -1       # -1: Nicht im Profilblock, Nächste Zeile ist bei:
                           #  0: Bezeichnung des gesamten Profile-Blocks. 
                           #  1: Profilname, Koordinaten, nächster Block oder Ende
                           #  2: Profilnr.
                           #  3: Erste Koordinaten des Querprofils

    x1 = None   # markiert, dass noch kein Profil eingelesen wurde (s. u.)

    for zeile in dynatemplate:
        if zeile[0:2] == '##':
            continue                # Kommentarzeile wird übersprungen

        # Zuerst werden Abschnitte mit besonderen Daten bearbeitet (Profildaten etc.)
        if profilmodus >= 0:
            if profilmodus == 0:
                # Bezeichnung des gesamten Profile-Blocks. Wird nicht weiter verwendet
                profilmodus = 1
                continue
            elif profilmodus == 2:
                # Profilnr.

                profil_key = zeile.strip()
                profilmodus = 3
                continue
            elif profilmodus == 3:
                # Erster Profilpunkt
                profilmodus = 1
                x1 = 1                          # Punkt als Startpunkt für nächstes Teilstück speichern
                continue
            elif profilmodus == 1:
                # weitere Profilpunkte, nächstes Profil oder Ende der Profile
                if zeile[0:1] == '(':
                    # profilmodus == 1, weitere Profilpunkte
                    continue
                else:
                    # Nächstes Profil oder Ende Querprofile (=Ende des aktuellen Profils)

                    # Beschriftung des Profils. Grund: Berechnung von Breite und Höhe ist erst nach
                    # Einlesen aller Profilzeilen möglich.

                    # Erst wenn das erste Profil eingelesen wurde
                    if x1 is not None:
                        # Höhe zu Breite-Verhältnis berechnen
                        dynaprof_key.append(profil_key)
                        dynaprof_nam.append(profilnam)
                        logger.debug(u'k_qkkp.exportKanaldaten (2): profilnam = {}'.format(profilnam))
                        # sql = u'''INSERT INTO dynaprofil (profil_key, profilnam, breite, hoehe) 
                                      # VALUES ('{key}', '{nam}', {br}, {ho})'''.format(
                                      # key=profil_key, nam=profilnam, br=breite, ho=hoehe)
                        # logger.debug(u'sql = {}'.format(sql))
                        # if not dbQK.sql(sql, u'importkanaldaten_kp (1)'):
                            # return None

                    if zeile[0:2] != '++':
                        # Profilname
                        profilnam = zeile.strip()
                        profilmodus = 2
                        continue
                    else:
                        # Ende Block Querprofile (es sind mehrere möglich!)
                        profilmodus = -1
                        x1 = None

        # Optionen und Daten
        if zeile[0:6] == u'++QUER':
            profilmodus = 0

    # Prüfen, ob alle in den zu exportierenden Daten enthaltenen Profile schon definiert sind. 

    fehler = 0

    if dynaprof_choice == u'profilname':
        # Die DYNA-Schlüssel werden entsprechend der DYNA-Forlagedatei vergeben. Daher braucht 
        # nur das Vorhandensein der Profilnamen geprüft zu werden. 
        sql = u"""SELECT profilnam
                FROM haltungen{ausw_where}{auswahl}
                GROUP BY profilnam""".format(ausw_where=ausw_where, auswahl=auswahl)

        if not dbQK.sql(sql, u'dbQK: QKan_ExportDYNA.k_qkkp.profile (1)'):
            return False

        daten = dbQK.fetchall()
        for profil in daten:
            profil_new = profil[0]
            if profil_new not in dynaprof_nam:
                meldung(u'Fehlende Profildaten in DYNA-Vorlagedatei {fn}'.format(fn=template_dyna), 
                    u'{pn}'.format(pn=profil_new))
                logger.debug(u'k_qkkp.exportKanaldaten (1): dynaprof_nam = {}'.format(', '.join(dynaprof_nam)))
                if autokorrektur:
                    sql = """INSERT INTO profile (profilnam)
                            VALUES ({pn})""".format(pn=profil_new)
                    if not dbQK.sql(sql, u'dbQK: k_qkkp.exportKanaldaten (1)'):
                        return False
                fehler = 2
        if fehler == 2:
            fehlermeldung(u'Fehler in den Profildaten', u'Es gibt Profile in den Haltungsdaten, die nicht in der DYNA-Vorlage ')
            return False

    elif dynaprof_choice == u'profilkey':
        sql = u"""SELECT p.kp_nr
                FROM haltungen AS h
                LEFT JOIN profile AS p
                ON h.profilnam = p.profilnam{ausw_where}{auswahl}
                GROUP BY p.kp_nr""".format(ausw_where=ausw_where, auswahl=auswahl)

        if not dbQK.sql(sql, u'dbQK: QKan_ExportDYNA.k_qkkp.profile (2)'):
            return False

        daten = dbQK.fetchall()
        for profil in daten:
            profil_key = profil[3]
            if profil_key not in dynaprof_key:
                meldung(u'Fehlende Profildaten in DYNA-Vorlagedatei {fn}'.format(fn=template_dyna), 
                    u'{id}'.format(id=profil_key))
                logger.debug(u'dynaprof_key = {}'.format(', '.join(dynaprof_key)))
                if autokorrektur:
                    sql = """INSERT INTO profile (profilnam, kp_nr)
                            VALUES ({pn}, {id})""".format(pn=profil_new, id=profil_key)
                    if not dbQK.sql(sql, u'dbQK: k_qkkp.exportKanaldaten (1)'):
                        return False
                fehler = 2
            elif profil_key is None:
                fehlermeldung(u'Fehlende ID in DYNA-Vorlagedatei {fn}'.format(fn=template_dyna), 
                    u'Es fehlt die ID für Profil {pn}'.format(pn=profil_new))
                fehler = max(fehler, 1)         # fehler = 2 hat Priorität

        if fehler == 1:
            fehlermeldung(u'Fehler in den Profildaten', u'Es gibt Profile ohne eine DYNA-Nummer (kp_nr)')
            return False
        elif fehler == 2:
            fehlermeldung(u'Fehler in den Profildaten', 
                          u'Es gibt Profile in den Haltungsdaten, die nicht in der DYNA-Vorlage vorhanden sind')
            return False

    # Schreiben der DYNA-Datei ------------------------------------------------------------------------

    with open(dynafile, 'w') as df:

        typ05 = False                  # markiert, ob in der Vorlagedatei Block mit Datentyp 05 erreicht
        typ12 = False                  # markiert, ob in der Vorlagedatei Block mit Datentyp 12 erreicht
        typ16 = False                  # markiert, ob in der Vorlagedatei Block mit Datentyp 16 erreicht
        typ41 = False                  # markiert, ob in der Vorlagedatei Block mit Datentyp 41 erreicht

        # Die nachfolgende Schleife durchläuft das DYNA-Template in der Liste "dynatemplate", schreibt die 
        # Standardzeilen. An den Stellen, an denen in der Vorlage Daten eingefügt und gegebenfalls in der
        # Vorlage vorhandene Daten übersprungen werden müssen, sind entsprechende Blöcke eingefügt.
        # Diese sind durch Flags gekennzeichnet, z.B. typ05

        for z in dynatemplate:

            if z[:2] == '##':
                # Kommentarzeilen werden geschrieben, solange keine Blöcke aktiv sind
                df.write(z)
                continue

            # Schreiben des aktiven Datenblocks

            # Block Typ05
            if typ05:
                if z[:2] == '++':
                    # Sobald nächster Block erreicht, ist Typ05 beendet
                    # Jetzt werden alle neuen Typ-05-Datensätze geschrieben
                    for id, mat, kb in zip(dynakeys_id, dynakeys_mat, dynakeys_ks):
                        df.write(u'05 {id:1s} {mat:4s} {sp:10.6f}{kb:10.6f}{ks:10.6f}\n'.format(id=id[:1], mat=mat[:4], sp=0, kb=kb, ks=0).replace('  0.000000','          '))
                    typ05 = False
                    df.write(z)

            # Block Typ12
            elif typ12:
                if z[:2] == '++':
                    # Sobald nächster Block erreicht, ist Typ12 beendet
                    # Jetzt werden alle neuen Typ-12-Datensätze geschrieben
                    if not write12(dbQK, df, dynakeys_id, dynakeys_ks, mindestflaeche, dynaprof_choice, 
                                    dynabef_choice, dynaprof_nam, dynaprof_key, ausw_and, auswahl):
                        return False
                    typ12 = False
                    df.write(z)

            # Block Typ16
            elif typ16:
                if z[:2] == '++':
                    # Sobald nächster Block erreicht, ist Typ16 beendet
                    # Jetzt werden alle neuen Typ-16-Datensätze geschrieben
                    if not write16(dbQK, df, ausw_and, auswahl):
                        return False
                    typ16 = False
                    df.write(z)

            # Block Typ41
            elif typ41:
                if z[:2] == '++':
                    # Sobald nächster Block erreicht, ist Typ41 beendet
                    # Jetzt werden alle neuen Typ-41-Datensätze geschrieben
                    if not write41(dbQK, df, ausw_and, auswahl):
                        return False
                    typ41 = False
                    df.write(z)
            else:
                # Allgemeine Zeilen werden direkt aus der Templatedatei geschrieben
                df.write(z)


            # Aktivierung der Datenblöcke

            if z[:6] == '++SCHL':
                # Block Typ05 beginnt: "Schlüsseltabellen für Rauheit, Material und Regenspende"
                typ05 = True
                # df.write(z)
                continue
            elif z[:6] == '++KANA':
                # Block Typ12 beginnt: "Haltungs- und Flächendaten"
                typ12 = True
                # df.write(z)
                continue
            elif z[:6] == '++NETZ':
                # Block Typ16 beginnt: "Verzweigungen und Endschächte"
                typ16 = True
                # df.write(z)
                continue
            elif z[:6] == '++DECK':
                # Block Typ41 beginnt: "Verzweigungen und Endschächte"
                typ41 = True
                # df.write(z)
                continue

    del dbQK

    fortschritt(u'Ende...', 1)
    progress_bar.setValue(100)
    status_message.setText(u"Datenexport abgeschlossen.")
    status_message.setLevel(QgsMessageBar.SUCCESS)

