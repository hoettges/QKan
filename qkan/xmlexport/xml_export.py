# -*- coding: utf-8 -*-

"""
  Export Kanaldaten in Isybau-xml
  ====================================

  Transfer von Kanaldaten aus einer QKan-Datenbank nach Xml

  | Dateiname            : xml_export.py
  | Date                 : 2019
  | Copyright            : (C)
  | Email                : @fh-aachen.de
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
#from qkan.database.fbfunc import FBConnection
from qkan.database.qkan_utils import fortschritt, fehlermeldung, meldung, checknames
from qkan.linkflaechen.updatelinks import updatelinkfl, updatelinksw, updatelinkageb

import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

# Referenzlisten
#abändern?
from qkan.database.reflists import abflusstypen
from qkan.database.qkan_database import versionolder

logger = logging.getLogger('QKan')

progress_bar = None


# Hauptprogramm ---------------------------------------------------------------------------------------------

def exportKanaldaten(dbQK, xmlExportFile, check_export, liste_teilgebiete=[], datenbanktyp=u'spatialite'):
    '''Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine Xml Datei

    :iface:


    :dbQK:                  Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :type dbQK:             DBConnection

    :xmlexportfile:         Xml Export Datei in die Daten geschrieben werden soll
    :type xmlExportFile:    Xml

    :check_export:          gibt an welche Daten aus der Datenbank in die Xml geschrieben werden sollen
    :type check_export:

    :liste_teilgebiete:     Liste der ausgewählten Teilgebiete
    :type liste_teilgebiete: String

    :datenbanktyp:          Typ der Datenbank (SpatiaLite)
    :type datenbanktyp:     String


    :returns:               void
    '''

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(u"", u"Export in Arbeit. Bitte warten.")
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, QgsMessageBar.INFO, 10)



    elem = Element('Identifikation', {'xmlns': "http://www.ofd-hannover.la/Identifikation"})

    child = SubElement(elem, 'Version')

    child1 = SubElement(elem, 'Admindaten')
    lieg = SubElement(child1, 'Liegenschaft')
    liegn = SubElement(lieg, 'Liegenschaftsnummer')
    liegb = SubElement(lieg, 'Liegenschaftsbezeichnung')

    child2 = SubElement(elem, 'Datenkollektive')
    datens = SubElement(child2, 'Datenstatus')
    erstel = SubElement(child2, 'Erstellungsdatum')
    kom = SubElement(child2, 'Kommentar')
    kenn = SubElement(child2, 'Kennungen')
    kol = SubElement(kenn, 'Kollektiv')

    stamm = SubElement(child2, 'Stammdatenkollektiv')
    kenn1 = SubElement(stamm, 'Kennung')
    besch1 = SubElement(stamm, 'Beschreibung')
    abw = SubElement(stamm, 'AbwassertechnischeAnlage')

    # Wehr

    # Pumpe

    # Auslässe

    # Schacht

    # Speicher

    # Haltung


    hydro = SubElement(child2, 'Hydraulikdatenkollektiv')
    kenn2 = SubElement(hydro, 'Kennung')
    besch2 = SubElement(hydro, 'Beschreibung')
    rechen = SubElement(hydro, 'Rechennetz')
    stammd = SubElement(rechen, 'Stammdatenkennung')
    hydra = SubElement(rechen, 'HydraulikObjekte')

    flae = SubElement(hydro, 'Flaechen')
    # Flaechendaten

    sys = SubElement(hydro, 'Systembelastungen')

    # Wehr

    # Pumpe

    # Schacht

    # Speicher

    # Auslässe

    # Haltung

    # --------------------------------------------------------------------------------------------
    # Export der Wehre

    if check_export['export_wehre']:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        # if len(liste_teilgebiete) != 0:
        #    auswahl = u" AND wehre.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        # else:
        #    auswahl = u""

        wnam = ''
        schoben = ''
        schunten = ''
        wehrtyp = ''
        schwellenhoehe = 0.0
        kammerhoehe = 0.0
        laenge = 0.0
        uebeiwert = 0.0
        simstatus = 0

        sql = u"""
                SELECT
                    wehre.wnam AS wnam,
                    wehre.schoben AS schoben,
                    wehre.schunten AS schunten,
                    wehre.wehrtyp AS wehrtyp,
                    wehre.schwellenhoehe AS schwellenhoehe,
                    wehre.kammerhoehe AS kammerhoehe,
                    wehre.laenge AS laenge,
                    wehre.uebeiwert AS uebeiwert,
                    wehre.aussentyp AS aussentyp,
                    wehre.aussenwsp AS aussenwsp,
                    wehre.simstatus AS simstaus,
                    wehre.kommentar AS kommentar             
                FROM wehre
            """

        if not dbQK.sql(sql, u'dbQK: export_wehre'):
            return False

        fortschritt(u'Export Wehre...', 0.35)

        for attr in dbQK.fetchall():


            wnam, schoben, schunten, wehrtyp, schwellenhoehe, kammerhoehe, laenge, uebeiwert, aussentyp, aussenwsp, simstatus, kommentar = attr

            wnam = str(wnam)
            schoben = str(schoben)
            schunten = str(schunten)
            wehrtyp = str(wehrtyp)
            schwellenhoehe = str(schwellenhoehe)
            kammerhoehe = str(kammerhoehe)
            laenge = str(laenge)
            uebeiwert = str(uebeiwert)
            aussentyp = str(aussentyp)
            aussenwsp = str(aussenwsp)
            simstatus = str(simstatus)
            kommentar = str(kommentar)

            hydroo = SubElement(hydra, 'Hydraulikobjekt')
            objbek = SubElement(hydroo, 'Objektbezeichnung')
            objbek.text = wnam
            hydobt = SubElement(hydroo, 'HydObjektTyp')
            we = SubElement(hydroo, 'Wehr')
            wety = SubElement(we, 'Wehrtyp')
            wety.text = wehrtyp
            schz = SubElement(we, 'SchachtZulauf')
            schz.text = schoben
            scha = SubElement(we, 'SchachtAblauf')
            scha.text = schunten
            lenw = SubElement(we, 'LaengeWehrschwelle')
            lenw.text = laenge
            schw = SubElement(we, 'Schwellenhoehe')
            schw.text = schwellenhoehe
            kam = SubElement(we, 'Kammerhoehe')
            kam.text = kammerhoehe
            ueb = SubElement(we, 'Ueberfallbeiwert')
            ueb.text = uebeiwert

            abw = SubElement(stamm, 'AbwassertechnischeAnlage')
            objb = SubElement(abw, 'Objektbezeichnung')
            objb.text = wnam
            obja = SubElement(abw, 'Objektart')
            stat = SubElement(abw, 'Status')
            stat.text = simstatus
            knote = SubElement(abw, 'Knoten')
            bauw = SubElement(knote, 'Bauwerk')
            weu = SubElement(bauw, 'Wehr_Ueberlauf')
            wet = SubElement(weu, 'Wehrtyp')
            wet.text = wehrtyp
            lean = SubElement(weu, 'LaengeWehrschwelle')
            lean.text = laenge

        fortschritt(u'{} Wehre eingefuegt')
    progress_bar.setValue(70)

    # --------------------------------------------------------------------------------------------
    # Export der Pumpen

    if check_export['export_pumpen']:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        # if len(liste_teilgebiete) != 0:
        #    auswahl = u" AND pumpen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        # else:
        #    auswahl = u""

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

        sql = u"""
                    SELECT
                        pumpen.pnam AS pnam,
                        pumpen.volanf AS volanf,
                        pumpen.volges AS volges,
                        pumpen.sohle AS sohle,
                        pumpen.schunten AS schunten,
                        pumpen.schoben AS schoben,
                        pumpen.steuersch AS steuersch,
                        pumpen.einschalthoehe AS einschalthoehe,
                        pumpen.ausschalthoehe AS ausschalthoehe,
                        pumpen.simstatus AS simstatus,
                        pumpen.kommentar AS kommentar,
                        pumpen.pumpentyp AS pumpentyp   
                    FROM pumpen
                """

        if not dbQK.sql(sql, u'dbQK: export_pumpen'):
            return False

        fortschritt(u'Export Pumpen...', 0.35)

        for attr in dbQK.fetchall():


            pnam, volanf, volges, sohle, schunten, schoben, steuersch, einschalthoehe, ausschalthoehe, simstatus, kommentar, pumpentyp = attr

            pnam = str(pnam)
            volanf = str(volanf)
            volges = str(volges)
            sohle = str(sohle)
            schunten = str(schunten)
            schoben = str(schoben)
            steuersch = str(steuersch)
            einschalthoehe = str(einschalthoehe)
            ausschalthoehe = str(ausschalthoehe)
            simstatus = str(simstatus)
            kommentar = str(kommentar)
            pumpentyp = str(pumpentyp)

            hydrat = SubElement(hydra, 'HydraulikObjekt')
            objbek = SubElement(hydrat, 'Objektbezeichnung')
            objbek.text = pnam
            hydobt = SubElement(hydrat, 'HydObjektTyp')
            pum = SubElement(hydrat, 'Pumpe')
            pumt = SubElement(pum, 'PumpenTyp')
            pumt.text = pumpentyp
            steu = SubElement(pum, 'Steuerschacht')
            steu.text = steuersch
            schaz = SubElement(pum, 'SchachtZulauf')
            schaz.text = schoben
            schaa = SubElement(pum, 'SchachtAblauf')
            schaa.text = schunten
            sohl = SubElement(pum, 'Sohlhoehe')
            sohl.text = sohle
            anf = SubElement(pum, 'Anfangsvolumen')
            anf.text = volanf
            ges = SubElement(pum, 'Gesamtvolumen')
            ges.text = volges
            oken = SubElement(pum, 'OhneKennlinie')
            schal = SubElement(oken, 'Schaltpunkte')
            schal1 = SubElement(schal, 'Schaltpunkt1-2')
            schal1.text = einschalthoehe
            schal2 = SubElement(schal, 'Schaltpunkt2-1')
            schal2.text = ausschalthoehe

            abw = SubElement(stamm, 'AbwassertechnischeAnlage')
            objb = SubElement(abw, 'Objektbezeichnung')
            objb.text = pnam
            obja = SubElement(abw, 'Objektart')
            stat = SubElement(abw, 'Status')
            stat.text = simstatus
            knote = SubElement(abw, 'Knoten')
            bauw = SubElement(knote, 'Bauwerk')

        fortschritt(u'{} Pumpen eingefuegt')
    progress_bar.setValue(70)

    # --------------------------------------------------------------------------------------------

    # Export der Auslaesse

    if check_export['export_auslaesse']:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        # if len(liste_teilgebiete) != 0:
        #    auswahl = u" AND schaechte.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        # else:
        #    auswahl = u""

        schnam = ''
        xsch = 0.0
        ysch = 0.0
        sohlhoehe = 0.0
        deckelhoehe = 0.0
        durchm = 0.5
        entwartnr = ''
        knotentyp = 0
        simstatus = 0
        kommentar = ''

        sql = u"""
                SELECT
                    schaechte.schnam AS schnam,
                    schaechte.deckelhoehe AS deckelhoehe,
                    schaechte.sohlhoehe AS sohlhoehe,
                    schaechte.durchm AS durchm,
                    schaechte.xsch AS xsch,
                    schaechte.ysch AS ysch,
                    schaechte.kommentar AS kommentar,
                    schaechte.simstatus AS simstatus,
                    ea.he_nr AS entwartnr,
                    schaechte.knotentyp AS knotentyp
                FROM schaechte 
                left join Entwaesserungsarten AS ea 
                ON schaechte.entwart = ea.bezeichnung
                WHERE schaechte.schachttyp = 'Auslass'
                """

        if not dbQK.sql(sql, u'dbQK: k_qkhe.export_auslaesse'):
            return False

        fortschritt(u'Export Auslässe...', 0.20)

        for attr in dbQK.fetchall():
            schnam, deckelhoehe, sohlhoehe, durchm, xsch, ysch, kommentar, simstatus, entwartnr, knotentyp = attr

            schnam = str(schnam)
            deckelhoehe = str(deckelhoehe)
            sohlhoehe = str(sohlhoehe)
            durchm = str(durchm)
            xsch = str(xsch)
            ysch = str(ysch)
            kommentar = str(kommentar)
            simstatus = str(simstatus)
            entwartnr = str(entwartnr)
            knotentyp = str(knotentyp)

            # Einfuegen in xml

            abw = SubElement(stamm, 'AbwassertechnischeAnlage')

            obj = SubElement(abw, 'Objektbezeichnung')
            obj.text = schnam

            obja = SubElement(abw, 'Objektart')
            sta = SubElement(abw, 'Status')
            sta.text = simstatus
            entw = SubElement(abw, 'Entwaesserungsart')
            entw.text = entwartnr
            komm = SubElement(abw, 'Kommentar')
            komm.text = kommentar

            kno = SubElement(abw, 'Knoten')
            knoty = SubElement(kno, 'Knotentyp')
            knoty.text = knotentyp

            bauw = SubElement(kno, 'Bauwerk')
            bauwt = SubElement(bauw, 'Bauwerkstyp')
            ausl = SubElement(bauw, 'Auslaufbauwerk')

            geo = SubElement(abw, 'Geometrie')

            geomda = SubElement(geo, 'Geometriedaten')

            knot = SubElement(geomda, 'Knoten')

            punk1 = SubElement(knot, 'Punkt')
            rech1 = SubElement(punk1, 'Rechtswert')
            rech1.text = xsch
            hoch1 = SubElement(punk1, 'Hochwert')
            hoch1.text = ysch
            punkh1 = SubElement(punk1, 'Punkthoehe')
            punka1 = SubElement(punk1, 'PunktattributAbwasser')

            punk2 = SubElement(knot, 'Punkt')
            punkh2 = SubElement(punk2, 'Punkthoehe')
            punkh2.text = sohlhoehe
            punka2 = SubElement(punk2, 'PunktattributAbwasser')

            punk3 = SubElement(knot, 'Punkt')
            rech3 = SubElement(punk3, 'Rechtswert')
            rech3.text = xsch
            hoch3 = SubElement(punk3, 'Hochwert')
            hoch3.text = ysch
            punkh3 = SubElement(punk3, 'Punkthoehe')
            punkh3.text = sohlhoehe
            punka3 = SubElement(punk3, 'PunktattributAbwasser')

        fortschritt(u'{} Auslässe eingefuegt')
    progress_bar.setValue(50)

    # --------------------------------------------------------------------------------------------
    # Export der Schaechte

    if check_export['export_schaechte'] :

        # Nur Daten fuer ausgewaehlte Teilgebiete
        #if len(liste_teilgebiete) != 0:
        #    auswahl = u" AND schaechte.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        #else:
         #   auswahl = u""

        schnam = ''
        xsch = 0.0
        ysch = 0.0
        sohlhoehe = 0.0
        deckelhoehe = 0.0
        durchm = 1.0
        entwartnr = ''
        knotentyp = 0
        simstatus = 0
        kommentar = ''


        sql = u"""
            SELECT
                schaechte.schnam AS schnam,
                schaechte.deckelhoehe AS deckelhoehe,
                schaechte.sohlhoehe AS sohlhoehe,
                schaechte.durchm AS durchm,
                ea.he_nr AS entwartnr,
                schaechte.knotentyp AS knotentyp,
                schaechte.simstatus AS simstatus,
                schaechte.kommentar AS kommentar,
                schaechte.xsch AS xsch,
                schaechte.ysch AS ysch
            FROM schaechte
            left join Entwaesserungsarten AS ea 
            ON schaechte.entwart = ea.bezeichnung
            WHERE schaechte.schachttyp = 'Schacht'
            """
        if not dbQK.sql(sql, u'dbQK: export_schaechte'):
            return False



        fortschritt(u'Export Schaechte ', 0.1)
        progress_bar.setValue(15)

        for attr in dbQK.fetchall():

            schnam, deckelhoehe, sohlhoehe, durchm, entwartnr, knotentyp, simstatus, kommentar, xsch, ysch = attr

            schnam = str(schnam)
            deckelhoehe = str(deckelhoehe)
            sohlhoehe = str(sohlhoehe)
            durchm = str(durchm)
            entwartnr = str(entwartnr)
            knotentyp = str(knotentyp)
            simstatus = str(simstatus)
            kommentar = str(kommentar)
            xsch = str(xsch)
            ysch = str(ysch)



            #Einfügen in xml

            abw = SubElement(stamm, 'AbwassertechnischeAnlage')

            obj = SubElement(abw, 'Objektbezeichnung')
            obj.text = schnam

            obja = SubElement(abw, 'Objektart')
            sta = SubElement(abw, 'Status')
            sta.text = simstatus
            entw = SubElement(abw, 'Entwaesserungsart')
            entw.text = entwartnr
            komm = SubElement(abw, 'Kommentar')
            komm.text = kommentar

            kno = SubElement(abw, 'Knoten')
            knoty = SubElement(kno, 'Knotentyp')
            knoty.text = knotentyp

            scha = SubElement(kno, 'Schacht')
            schati = SubElement(scha, 'Schachttiefe')
            anza = SubElement(scha, 'AnzahlAnschluesse')

            geo= SubElement(abw, 'Geometrie')

            geomda = SubElement(geo, 'Geometriedaten')

            knot = SubElement(geomda, 'Knoten')

            punk1 = SubElement(knot, 'Punkt')
            rech1 = SubElement(punk1, 'Rechtswert')
            rech1.text = xsch
            hoch1 = SubElement(punk1, 'Hochwert')
            hoch1.text = ysch
            punkh1 = SubElement(punk1, 'Punkthoehe')
            punkh1.text = deckelhoehe
            punka1 = SubElement(punk1, 'PunktattributAbwasser')


            punk2 = SubElement(knot, 'Punkt')
            punkh2 = SubElement(punk2, 'Punkthoehe')
            punkh2.text = sohlhoehe
            punka2 = SubElement(punk2, 'PunktattributAbwasser')


            punk3 = SubElement(knot, 'Punkt')
            rech3 = SubElement(punk3, 'Rechtswert')
            rech3.text = xsch
            hoch3 = SubElement(punk3, 'Hochwert')
            hoch3.text = ysch
            punkh3 = SubElement(punk3, 'Punkthoehe')
            punkh3.text = sohlhoehe
            punka3 = SubElement(punk3, 'PunktattributAbwasser')

        fortschritt(u'{} Schaechte eingefuegt')

    # --------------------------------------------------------------------------------------------
    # Export der Speicherbauwerke


    if check_export['export_speicher']:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        #if len(liste_teilgebiete) != 0:
        #    auswahl = u" AND schaechte.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        #else:
        #    auswahl = u""

        schnam = ''
        xsch = 0.0
        ysch = 0.0
        sohlhoehe = 0.0
        deckelhoehe = 0.0
        durchm = 0.5
        entwartnr = ''
        knotentyp = 0
        simstatus = 0
        kommentar = ''


        sql = u"""
            SELECT
                schaechte.schnam AS schnam,
                schaechte.deckelhoehe AS deckelhoehe,
                schaechte.sohlhoehe AS sohlhoehe,
                schaechte.durchm AS durchm,
                ea.he_nr AS entwartnr,
                schaechte.xsch AS xsch,
                schaechte.ysch AS ysch,
                schaechte.kommentar AS kommentar,
                schaechte.simstatus AS simstatus,
                schaechte.knotentyp AS knotentyp
            FROM schaechte
            left join Entwaesserungsarten AS ea 
            ON schaechte.entwart = ea.bezeichnung
            WHERE schaechte.schachttyp = 'Speicher'
            """

        if not dbQK.sql(sql, u'dbQK: export_speicher'):
            return False


        fortschritt(u'Export Speicherschaechte...', 0.35)

        for attr in dbQK.fetchall():

            schnam, deckelhoehe, sohlhoehe, durchm, entwartnr, xsch, ysch, kommentar, simstatus, knotentyp = attr


            schnam = str(schnam)
            deckelhoehe = str(deckelhoehe)
            sohlhoehe = str(sohlhoehe)
            durchm = str(durchm)
            entwartnr = str(entwartnr)
            xsch = str(xsch)
            ysch = str(ysch)
            kommentar = str(kommentar)
            simstatus = str(simstatus)
            knotentyp = str(knotentyp)



            # Einfuegen in xml


            abw = SubElement(stamm, 'AbwassertechnischeAnlage')

            obj = SubElement(abw, 'Objektbezeichnung')
            obj.text = schnam

            obja = SubElement(abw, 'Objektart')
            sta = SubElement(abw, 'Status')
            sta.text = simstatus
            entw = SubElement(abw, 'Entwaesserungsart')
            entw.text = entwartnr
            komm = SubElement(abw, 'Kommentar')
            komm.text = kommentar

            kno = SubElement(abw, 'Knoten')
            knoty = SubElement(kno, 'Knotentyp')
            knoty.text = knotentyp

            bauw = SubElement(kno, 'Bauwerk')
            bauwt = SubElement(bauw, 'Bauwerkstyp')
            bec = SubElement(bauw, 'Becken')
            anzz = SubElement(bec, 'AnzahlZulaeufe')
            anza = SubElement(bec, 'AnzahlAblaeufe')



            geo = SubElement(abw, 'Geometrie')

            geomda = SubElement(geo, 'Geometriedaten')

            knot = SubElement(geomda, 'Knoten')

            punk1 = SubElement(knot, 'Punkt')
            rech1 = SubElement(punk1, 'Rechtswert')
            rech1.text = xsch
            hoch1 = SubElement(punk1, 'Hochwert')
            hoch1.text = ysch
            punkh1 = SubElement(punk1, 'Punkthoehe')
            punkh1.text = deckelhoehe
            punka1 = SubElement(punk1, 'PunktattributAbwasser')

            punk2 = SubElement(knot, 'Punkt')
            punkh2 = SubElement(punk2, 'Punkthoehe')
            punkh2.text = sohlhoehe
            punka2 = SubElement(punk2, 'PunktattributAbwasser')

            punk3 = SubElement(knot, 'Punkt')
            rech3 = SubElement(punk3, 'Rechtswert')
            rech3.text = xsch
            hoch3 = SubElement(punk3, 'Hochwert')
            hoch3.text = ysch
            punkh3 = SubElement(punk3, 'Punkthoehe')
            punkh3.text = sohlhoehe
            punka3 = SubElement(punk3, 'PunktattributAbwasser')



        fortschritt(u'{} Speicher eingefuegt')


    # --------------------------------------------------------------------------------------------
    # Export der Haltungen


    if check_export['export_haltungen']:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        #if len(liste_teilgebiete) != 0:
        #    auswahl = u" AND haltungen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        #else:
        #    auswahl = u""

        haltnam = ''
        schoben = ''
        schunten = ''
        hoehe = 0.0
        breite = 0.0
        laenge = 0.0  # in Hydraulikdaten enthalten.
        sohleoben = 0.0
        sohleunten = 0.0
        deckeloben = 0.0
        deckelunten = 0.0
        profilnam = ''
        entwartnr = ''
        ks = '1.5'  # in Hydraulikdaten enthalten.
        simstatus = 0
        kommentar = ''
        xschob = 0.0
        yschob = 0.0
        xschun = 0.0
        yschun = 0.0


        sql = u"""
            SELECT
                haltungen.haltnam AS haltnam,
                haltungen.schoben AS schoben,
                haltungen.schunten AS schunten,
                haltungen.hoehe AS hoehe,
                haltungen.breite AS breite,
                haltungen.laenge AS laenge,
                haltungen.sohleoben AS sohleoben,
                haltungen.sohleunten AS sohleunten,
                haltungen.deckeloben AS deckeloben,
                haltungen.deckelunten AS deckelunten,
                haltungen.profilnam AS profilnam,
                ea.he_nr AS entwartnr,
                haltungen.ks AS ks,
                haltungen.simstatus AS simstatus,
                haltungen.kommentar AS kommentar,
                haltungen.xschob AS xschob,
                haltungen.yschob AS yschob,
                haltungen.xschun AS xschun,
                haltungen.yschun AS yschun
            FROM haltungen
            left join Entwaesserungsarten AS ea 
            ON haltungen.entwart = ea.bezeichnung
        """

        if not dbQK.sql(sql, u'dbQK: export_haltungen'):
            return False

        fortschritt(u'Export Haltungen...', 0.35)



        for attr in dbQK.fetchall():

            haltnam, schoben, schunten, hoehe, breite, laenge, sohleoben, sohleunten, deckeloben, deckelunten, profilnam, entwartnr, ks, simstatus, kommentar, xschob, yschob, xschun, yschun = attr

            haltnam = str(haltnam)
            schoben = str(schoben)
            schunten = str(schunten)
            hoehe = str(hoehe)
            breite = str(breite)
            laenge = str(laenge)
            sohleoben = str(sohleoben)
            sohleunten = str(sohleunten)
            deckeloben = str(deckeloben)
            deckelunten = str(deckelunten)
            profilnam = str(profilnam)
            entwartnr = str(entwartnr)
            ks = str(ks)
            simstatus = str(simstatus)
            kommentar = str(kommentar)
            xschob = str(xschob)
            yschob = str(yschob)
            xschun = str(xschun)
            yschun = str(yschun)


            abw = SubElement(stamm, 'AbwassertechnischeAnlage')
            objb = SubElement(abw, 'Objektbezeichnung')
            objb.text = haltnam
            obja = SubElement(abw, 'Objektart')
            stat = SubElement(abw, 'Status')
            stat.text = simstatus
            entwa = SubElement(abw, 'Entwaesserungsart')
            entwa.text = entwartnr

            kan = SubElement(abw, 'Kante')
            kant = SubElement(kan, 'KantenTyp')
            kanz = SubElement(kan, 'KnotenZulauf')
            kanz.text = schoben
            kanzt = SubElement(kan, 'KnotenZulaufTyp')
            kana = SubElement(kan, 'KnotenAblauf')
            kana.text = schunten
            kanat = SubElement(kan, 'KnotenAblaufTyp')
            solz = SubElement(kan, 'SohlhoeheZulauf')
            solz.text = sohleoben
            sola = SubElement(kan, 'SohlhoeheAblauf')
            sola.text = sohleunten
            lae = SubElement(kan, 'Laenge')
            lae.text = laenge
            mat = SubElement(kan, 'Material')

            prof = SubElement(kan, 'Profil')
            sonp = SubElement(prof, 'SonderprofilVorhanden')
            profa = SubElement(prof, 'Profilart')
            profa.text = profilnam
            profi = SubElement(prof, 'ProfilID')
            profb = SubElement(prof, 'Profilbreite')
            profb.text = breite
            profh = SubElement(prof, 'Profilhoehe')
            profh.text = hoehe

            hal = SubElement(kan, 'Haltung')
            dmp = SubElement(hal, 'DMPLaenge')
            dmp.text = laenge

            geom = SubElement(abw, 'Geometrie')
            geoa = SubElement(geom, 'GeoObjektart')
            geot = SubElement(geom, 'GeoObjekttyp')
            geod = SubElement(geom, 'Geometriedaten')
            kann = SubElement(geod, 'Kanten')
            kat = SubElement(kann, 'Kante')

            star = SubElement(kat, 'Start')
            recht1 = SubElement(star, 'Rechtswert')
            recht1.text = xschob
            hoh1 = SubElement(star, 'Hochwert')
            hoh1.text = yschob
            punkt1 = SubElement(star, 'Punkthoehe')
            punkt1.text = deckeloben
            punkta1 = SubElement(star, 'PunktattributAbwasser')

            end = SubElement(kat, 'Ende')
            recht2 = SubElement(end, 'Rechtswert')
            recht2.text = xschun
            hoh2 = SubElement(end, 'Hochwert')
            hoh2.text = yschun
            punkt2 = SubElement(end, 'Punkthoehe')
            punkt2.text = deckelunten
            punkta2 = SubElement(end, 'PunktattributAbwasser')



            # Haltung Hydraulikdaten

            hydroo = SubElement(hydra, 'HydraulikObjekt')
            objbe = SubElement(hydroo, 'Objektbezeichnung')
            hydob = SubElement(hydroo, 'HydObjektTyp')
            halt = SubElement(hydroo, 'Haltung')
            raub = SubElement(halt, 'RauigkeitsbeiwertKb')
            raub.text = ks
            bel = SubElement(halt, 'Berechnungslaenge')
            bel.text = laenge



        fortschritt(u'{} Haltungen eingefuegt')
    progress_bar.setValue(70)




    # --------------------------------------------------------------------------------------------
    # Zum Schluss: Schließen der Datenbankverbindungen

    liste = et.tostring(elem)
    y = minidom.parseString(liste)
    xml = y.toprettyxml(indent=' ')
    #print (xml)

    file = open(xmlExportFile, "w")
    file.write(xml)

    del dbQK


    fortschritt(u'Ende...', 1)
    progress_bar.setValue(100)
    status_message.setText(u"Datenexport abgeschlossen.")
    status_message.setLevel(QgsMessageBar.SUCCESS)

    return True