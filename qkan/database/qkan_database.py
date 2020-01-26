# -*- coding: utf-8 -*-

"""

  Datenbankmanagement der QKan-Datenbank
  ======================================

  Erstellt eine leere QKan-Datenbank und legt die Referenztabellen an.

  | Dateiname            : qkan_database.py
  | Date                 : October 2016
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

"""

__author__ = "Joerg Hoettges"
__date__ = "August 2019"
__copyright__ = "(C) 2016, Joerg Hoettges"
__dbVersion__ = "3.0.10"  # Version der QKan-Datenbank
__qgsVersion__ = (
    "3.0.10"
)  # Version des Projektes und der Projektdatei. Kann höher als die der QKan-Datenbank sein


import logging
import os
import traceback

from qgis.core import Qgis, QgsProject
from qgis.PyQt import Qt
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import iface, spatialite_connect

from .qkan_utils import fehlermeldung, fortschritt, meldung

logger = logging.getLogger("QKan.database.qkan_database")


def dbVersion():
    """Returns actual version of the QKan database"""
    return __dbVersion__


def qgsVersion():
    """Returns actual project version"""
    return __qgsVersion__


def versionolder(versliste, verslisref, depth=3):
    """Gibt wahr zurück, wenn eine Versionsliste älter als eine Referenz-Versionsliste ist, 
       falsch, wenn diese gleich oder größer ist. 

    :param versliste:   Liste von Versionsnummern, höchstwertige zuerst
    :type versliste:    list

    :param verslisref:  Liste von Versionsnummern zum Vergleich, höchstwertige zuerst
    :type verslisref:   list

    :param depth:       Untersuchungstiefe
    :type depth:        integer
    """
    for v1, v2 in zip(versliste[:depth], verslisref[:depth]):
        if v1 < v2:
            return True
        elif v1 > v2:
            return False
    return False


def qgsActualVersion(update=True, warning=False):
    """Prüft die Version des aktiven Projektes und aktualisiert die Layer gegebenenfalls

    :param warning: Aktiviert Warnung in QGIS-Meldungsleiste
    :type warning:  Boolean

    :returns:       Boolean
    
    Prüft im Vergleich zur Version der QKan-Datenbank, ob das geladene Projekt die gleiche oder höhere
    Versionsnummer aufweist.
    """

    layers = iface.layerTreeCanvasBridge().rootGroup().findLayers()
    if len(layers) == 0 and warning:
        logger.error("qkan_database.qgsActualVersion: Keine Layer vorhanden...")
        meldung("Fehler: ", "Kein QKan-Projekt geladen!")
        return False

    actQgsVersion = QgsProject.instance().title().replace("QKan Version ", "")
    if actQgsVersion == "":
        if len(layers) == 0:
            meldung("Benutzerfehler: ", "Es ist kein Projekt geladen")
        else:
            actQgsVersion = (
                "2.5.3"
            )  # davor wurde die Version der Projektdatei noch nicht verwaltet.
    curQgsVersion = qgsVersion()
    try:
        actQgsVersionLis = [
            int(el.replace("a", "").replace("b", "").replace("c", ""))
            for el in actQgsVersion.split(".")
        ]
    except BaseException as err:
        logger.error(
            "\nqkan_database.qgsActualVersion: {}\nVersionsstring fehlerhaft: {}".format(
                err, actQgsVersion
            )
        )
        actQgsVersion = (
            "2.5.3"
        )  # davor wurde die Version der Projektdatei noch nicht verwaltet.
        actQgsVersionLis = [
            int(el.replace("a", "").replace("b", "").replace("c", ""))
            for el in actQgsVersion.split(".")
        ]

    curQgsVersionLis = [
        int(el.replace("a", "").replace("b", "").replace("c", ""))
        for el in curQgsVersion.split(".")
    ]

    logger.debug("actQgsVersion: {}".format(actQgsVersion))
    logger.debug("curQgsVersion: {}".format(curQgsVersion))

    isActual = not versionolder(actQgsVersionLis, curQgsVersionLis)
    if not isActual:
        if warning:
            meldung(
                "Warnung: ",
                "Das geladene Projekt entspricht nicht der aktuellen Version. ",
            )
        if update:

            # Bis Version 2.5.11
            if versionolder(actQgsVersionLis, [2, 5, 12]):
                wlayers = [la for la in layers if la.name() == "Abflussparameter"]
                if len(wlayers) != 1:
                    logger.debug(
                        'Fehler in Layerliste: Es gibt mehr als einen Layer "Abflussparameter"'
                    )
                    layerList = [la.name() for la in layers]
                    logger.debug("layerList: {}".format(layerList))
                    return False
                wlayer = wlayers[0]
                logger.debug("vorher: wlayer.name(): {}".format(wlayer.name()))
                wlayer.setName("Abflussparameter HE")
                logger.debug("nachher: wlayer.name(): {}".format(wlayer.name()))

                project = QgsProject.instance()
                project.setTitle("QKan Version {}".format(qgsVersion()))

            isActual = True
    return isActual


# Erzeuge QKan-Tabellen


def createdbtables(consl, cursl, version=__dbVersion__, epsg=25832):
    """ Erstellt fuer eine neue QKan-Datenbank die benötigten Tabellen.

        :param consl: Datenbankobjekt der SpatiaLite-QKan-Datenbank
        :type consl: spatialite.dbapi2.Connection

        :param cursl: Zugriffsobjekt der SpatiaLite-QKan-Datenbank
        :type cursl: spatialite.dbapi2.Cursor

        :returns: Testergebnis: True = alles o.k.
        :rtype: logical
    """

    # Haltungen ----------------------------------------------------------------

    sql = """CREATE TABLE haltungen (
    pk INTEGER PRIMARY KEY,
    haltnam TEXT,
    schoben TEXT,
    schunten TEXT,
    hoehe REAL,
    breite REAL,
    laenge REAL,
    sohleoben REAL,
    sohleunten REAL,
    deckeloben REAL,
    deckelunten REAL,
    teilgebiet TEXT,
    qzu REAL,
    profilnam TEXT DEFAULT 'Kreisquerschnitt',
    entwart TEXT,
    rohrtyp TEXT,
    ks REAL,
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')),
    xschob REAL,
    yschob REAL,
    xschun REAL,
    yschun REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Haltungen" konnte nicht erstellt werden',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('haltungen','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('haltungen','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Haltungen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Schaechte ----------------------------------------------------------------
    # [knotentyp]: Typ der Verknüpfung (kommt aus Kanal++)

    sql = """CREATE TABLE schaechte (
    pk INTEGER PRIMARY KEY,
    schnam TEXT,
    xsch REAL,
    ysch REAL,
    sohlhoehe REAL,
    deckelhoehe REAL,
    durchm REAL,
    druckdicht INTEGER DEFAULT 0, 
    ueberstauflaeche REAL,
    entwart TEXT,
    strasse TEXT,
    teilgebiet TEXT,
    knotentyp TEXT,
    auslasstyp TEXT,
    schachttyp TEXT DEFAULT 'Schacht', 
    istspeicher INTEGER, 
    istauslass INTEGER, 
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Schaechte" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = """SELECT AddGeometryColumn('schaechte','geop',{},'POINT',2);""".format(epsg)
    sql2 = """SELECT AddGeometryColumn('schaechte','geom',{},'MULTIPOLYGON',2);""".format(
        epsg
    )
    sqlindex = """SELECT CreateSpatialIndex('schaechte','geom')"""
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Schaechte" konnten die Attribute "geop" und "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Profile ------------------------------------------------------------------

    sql = """CREATE TABLE profile (
    pk INTEGER PRIMARY KEY,
    profilnam TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_key TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Profile" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'Kreisquerschnitt', 1, NULL, NULL",
            "'Rechteckquerschnitt', 2, NULL, NULL",
            "'Eiquerschnitt 0,67', 3, NULL, NULL",
            "'Maulquerschnitt 1,20', 4, NULL, NULL",
            "'Halbschalenquerschnitt, offen 2,00', 5, NULL, NULL",
            "'Kreisquerschnitt, gestreckt 0,89', 6, NULL, NULL",
            "'Kreisquerschnitt, \xfcberh\xf6ht 0,67', 7, NULL, NULL",
            "'Eiquerschnitt, \xfcberh\xf6ht 0,57', 8, NULL, NULL",
            "'Eiquerschnitt, breit 0,80', 9, NULL, NULL",
            "'Eiquerschnitt, gedr\xfcckt 1,00', 10, NULL, NULL",
            "'Drachenquerschnitt 1,00', 11, NULL, NULL",
            "'Maulquerschnitt 1,33', 12, NULL, NULL",
            "'Maulquerschnitt, \xfcberh\xf6ht 1,00', 13, NULL, NULL",
            "'Maulquerschnitt, gedr\xfcckt 0,89', 14, NULL, NULL",
            "'Maulquerschnitt, gestreckt 1,14', 15, NULL, NULL",
            "'Maulquerschnitt, gestaucht 2,00', 16, NULL, NULL",
            "'Haubenquerschnitt 0,89', 17, NULL, NULL",
            "'Parabelquerschnitt 1,00', 18, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle 2,00', 19, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle 1,00', 20, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle 0,50', 21, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 2,00, b=0,2B', 22, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 1,00, b=0,2B', 23, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 0,50, b=0,2B', 24, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 2,00, b=0,4B', 25, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 1,00, b=0,4B', 26, NULL, NULL",
            "'Rechteckquerschnitt mit geneigter Sohle und horizontaler Sohle 0,50, b=0,4B', 27, NULL, NULL",
            "'Trapezquerschnitt', 68, NULL, NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO profile (profilnam, he_nr, mu_nr, kp_key) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "Profile" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Geometrie Sonderprofile --------------------------------------------------

    sql = """CREATE TABLE profildaten (
    pk INTEGER PRIMARY KEY, 
    profilnam TEXT, 
    wspiegel REAL, 
    wbreite REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "profildaten" konnte nicht erstellt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Entwaesserungssysteme ----------------------------------------------------

    sql = """CREATE TABLE entwaesserungsarten (
    pk INTEGER PRIMARY KEY, 
    kuerzel TEXT, 
    bezeichnung TEXT, 
    bemerkung TEXT, 
    he_nr INTEGER, 
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "entwaesserungsarten" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'MW', 'Mischwasser', NULL, 0, 0",
            "'RW', 'Regenwasser', NULL, 1, 2",
            "'SW', 'Schmutzwasser', NULL, 2, 1",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO entwaesserungsarten (kuerzel, bezeichnung, bemerkung, he_nr, kp_nr) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "entwaesserungsarten" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Pumpentypen --------------------------------------------------------------

    sql = """CREATE TABLE pumpentypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT, 
    he_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "pumpentypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'Offline', 1",
            "'Online Schaltstufen', 2",
            "'Online Kennlinie', 3",
            "'Online Wasserstandsdifferenz', 4",
            "'Ideal', 5",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO pumpentypen (bezeichnung, he_nr) VALUES ({})".format(ds)
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "pumpentypen" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Pumpen -------------------------------------------------------------------

    sql = """CREATE TABLE pumpen (
    pk INTEGER PRIMARY KEY,
    pnam TEXT,
    schoben TEXT,
    schunten TEXT,
    pumpentyp TEXT,
    volanf REAL,
    volges REAL,
    sohle REAL,
    steuersch TEXT,
    einschalthoehe REAL,
    ausschalthoehe REAL,
    teilgebiet TEXT,
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "pumpen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('pumpen','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('pumpen','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "pumpen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Wehre --------------------------------------------------------------------

    sql = """CREATE TABLE wehre (
    pk INTEGER PRIMARY KEY,
    wnam TEXT,
    schoben TEXT,
    schunten TEXT,
    wehrtyp TEXT,
    schwellenhoehe REAL,
    kammerhoehe REAL,
    laenge REAL,
    uebeiwert REAL,
    aussentyp TEXT,
    aussenwsp REAL,
    teilgebiet TEXT,
    simstatus TEXT DEFAULT 'vorhanden',
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "wehre" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('wehre','geom',{},'LINESTRING',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('wehre','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "wehre" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Einzugsgebiete ------------------------------------------------------------------
    # Entsprechen in HYSTEM-EXTRAN 7.x den Siedlungstypen
    # "flaeche" wird nur für den Import benötigt, wenn keine Flächenobjekte vorhanden sind
    # Verwendung:
    # Spezifische Verbrauchsdaten in Verbindung mit "einwohner"
    # Einheiten:
    #  - ewdichte: EW/ha
    #  - wverbrauch: l/(EW·d)
    #  - stdmittel: h/d
    #  - fremdwas: %
    #  - flaeche: ha

    sql = """CREATE TABLE einzugsgebiete (
    pk INTEGER PRIMARY KEY,
    tgnam TEXT,
    ewdichte REAL,
    wverbrauch REAL,
    stdmittel REAL,
    fremdwas REAL,
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Einzugsgebiete" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('einzugsgebiete','geom',{},'MULTIPOLYGON',2)".format(
        epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('einzugsgebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Einzugsgebiete" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Teilgebiete ------------------------------------------------------------------
    #  Verwendung:
    # Auswahl von Objekten in verschiedenen Tabellen für verschiedene Aufgaben (z. B.
    # automatische Verknüpfung von befestigten Flächen und direkten Einleitungen).

    sql = """CREATE TABLE teilgebiete (
    pk INTEGER PRIMARY KEY,
    tgnam TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "Teilgebiete" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('teilgebiete','geom',{},'MULTIPOLYGON',2)".format(
        epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('teilgebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "Teilgebiete" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Gruppen ------------------------------------------------------------------
    # Bearbeitungen, die auf Auswahlen basieren, verwenden ausschließlich die
    # Tabelle "Teilgebiete". Diese Zuordnung ist sozusagen aktiv, im Gegensatz
    # zu inaktiven Zuordnungen, die in der Tabelle "gruppen" gespeichert werden.
    # Mit einem plugin "Zuordnung zu Teilgebieten" können gespeicherte
    # Zuordnungen gespeichert und geladen werden. Dabei werden die
    # Zuordnungen für folgende Tabellen verwaltet:
    #  - "haltungen"
    #  - "schaechte"
    #  - "flaechen"
    #  - "linkfl"
    #  - "linksw"
    #  - "tezg"
    #  - "einleit"
    #  - "swgebaeude"

    sql = """CREATE TABLE gruppen (
    pk INTEGER PRIMARY KEY,
    pktab INTEGER,
    grnam TEXT,
    teilgebiet TEXT,
    tabelle TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "gruppen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Befestigte und unbefestigte Flächen ------------------------------------------------------

    sql = """CREATE TABLE flaechen (
    pk INTEGER PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,
    neigkl INTEGER DEFAULT 0,
    teilgebiet TEXT,
    regenschreiber TEXT,
    abflussparameter TEXT,
    aufteilen TEXT DEFAULT 'nein',
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "flaechen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = """SELECT AddGeometryColumn('flaechen','geom',{},'MULTIPOLYGON',2)""".format(
        epsg
    )
    sqlindex = """SELECT CreateSpatialIndex('flaechen','geom')"""
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "flaechen" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Anbindung Flächen
    # Die Tabelle linkfl verwaltet die Anbindung von Flächen an Haltungen. Diese Anbindung
    # wird ausschließlich grafisch verwaltet und beim Export direkt verwendet.
    # Flächen, bei denen das Attribut "aufteilen" den Wert 'ja' hat, werden mit dem
    # Werkzeug "QKan_Link_Flaechen" mit allen durch die Verschneidung mit tezg entstehenden
    # Anteilen zugeordnet.

    sql = """CREATE TABLE linkfl (
    pk INTEGER PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,
    tezgnam TEXT,
    teilgebiet TEXT,
    abflusstyp TEXT,
    speicherzahl INTEGER,
    speicherkonst REAL,
    fliesszeitkanal REAL,
    fliesszeitflaeche REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "linkfl" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = """SELECT AddGeometryColumn('linkfl','geom',{epsg},'MULTIPOLYGON',2)""".format(
        epsg=epsg
    )
    sql2 = """SELECT AddGeometryColumn('linkfl','gbuf',{epsg},'MULTIPOLYGON',2)""".format(
        epsg=epsg
    )
    sql3 = """SELECT AddGeometryColumn('linkfl','glink',{epsg},'LINESTRING',2)""".format(
        epsg=epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('linkfl','glink')"
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sql3)
        cursl.execute(sqlindex)
    except Exception as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            "QKan_Database (1) SQL-Fehler in SpatiaLite:",
        )
        consl.close()
        return False
    consl.commit()

    # Anbindung Direkteinleitungen --------------------------------------------------------------
    # Die Tabelle linksw verwaltet die Anbindung von Gebäuden an Haltungen. Diese Anbindung
    # wird anschließend in das Feld haltnam eingetragen. Der Export erfolgt allerdings anhand
    # der grafischen Verknüpfungen dieser Tabelle.

    sql = """CREATE TABLE linksw (
    pk INTEGER PRIMARY KEY,
    elnam TEXT,
    haltnam TEXT,
    teilgebiet TEXT)"""

    try:
        cursl.execute(sql)
    except:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(traceback.format_exc()),
            'Tabelle "linksw" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql1 = """SELECT AddGeometryColumn('linksw','geom',{epsg},'POLYGON',2)""".format(
        epsg=epsg
    )
    sql2 = """SELECT AddGeometryColumn('linksw','gbuf',{epsg},'MULTIPOLYGON',2)""".format(
        epsg=epsg
    )
    sql3 = """SELECT AddGeometryColumn('linksw','glink',{epsg},'LINESTRING',2)""".format(
        epsg=epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('linksw','geom')"
    try:
        cursl.execute(sql1)
        cursl.execute(sql2)
        cursl.execute(sql3)
        cursl.execute(sqlindex)
    except:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(traceback.format_exc()),
            "QKan_Database (2) SQL-Fehler in SpatiaLite: \n",
        )
        consl.close()
        return False
    consl.commit()

    # Teileinzugsgebiete ------------------------------------------------------------------

    sql = """CREATE TABLE tezg (
    pk INTEGER PRIMARY KEY,
    flnam TEXT,
    haltnam TEXT,
    neigkl INTEGER DEFAULT 1,
    regenschreiber TEXT,
    teilgebiet TEXT,
    abflussparameter TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "tezg" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('tezg','geom',{},'MULTIPOLYGON',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('tezg','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "tezg" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Direkte Einleitungen ----------------------------------------------------------
    # Erfasst alle Direkteinleitungen mit festem SW-Zufluss (m³/a)
    # Die Zuordnung zum Teilgebiet dient nur der Auswahl

    sql = """CREATE TABLE einleit (
    pk INTEGER PRIMARY KEY,
    elnam TEXT,
    haltnam TEXT,
    teilgebiet TEXT, 
    zufluss REAL,
    ew REAL,
    einzugsgebiet TEXT,
    kommentar TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "einleit" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = "SELECT AddGeometryColumn('einleit','geom',{},'POINT',2)".format(epsg)
    sqlindex = "SELECT CreateSpatialIndex('einleit','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'In der Tabelle "einleit" konnte das Attribut "geom" nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Einleitungen aus Aussengebieten ----------------------------------------------------------------
    # Erfasst alle Außengebiete
    # Die Zuordnung zum Teilgebiet dient nur der Auswahl

    sql = """CREATE TABLE aussengebiete (
        pk INTEGER PRIMARY KEY, 
        gebnam TEXT, 
        schnam TEXT, 
        hoeheob REAL, 
        hoeheun REAL, 
        fliessweg REAL, 
        basisabfluss REAL, 
        cn REAL, 
        regenschreiber TEXT, 
        teilgebiet TEXT, 
        kommentar TEXT, 
        createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            'Tabelle "aussengebiete" konnte nicht erstellt werden: \n{}'.format(
                repr(err)
            )
        )
        consl.close()
        return False

    sql = """SELECT AddGeometryColumn('aussengebiete','geom',{epsg},'MULTIPOLYGON',2)""".format(
        epsg=epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('aussengebiete','geom')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except BaseException as err:
        fehlermeldung(
            'In der Tabelle "aussengebiete" konnte das Attribut "geom" nicht hinzugefuegt werden: \n{}'.format(
                repr(err)
            )
        )
        consl.close()
        return False
    consl.commit()

    # Anbindung Aussengebiete -----------------------------------------------------------------------------
    # Die Tabelle linkageb verwaltet die Anbindung von Aussengebieten an Schächte. Diese Anbindung
    # wird anschließend in das Feld schnam eingetragen. Der Export erfolgt allerdings anhand
    # der grafischen Verknüpfungen dieser Tabelle.

    sql = """CREATE TABLE linkageb (
    pk INTEGER PRIMARY KEY,
    gebnam TEXT,
    schnam TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "linkageb" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    sql = """SELECT AddGeometryColumn('linkageb','glink',{epsg},'LINESTRING',2)""".format(
        epsg=epsg
    )
    sqlindex = "SELECT CreateSpatialIndex('linkageb','glink')"
    try:
        cursl.execute(sql)
        cursl.execute(sqlindex)
    except:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(traceback.format_exc()),
            "QKan_Database (2) SQL-Fehler in SpatiaLite: \n",
            sql,
        )
        consl.close()
        return False
    consl.commit()

    # Simulationsstatus/Planungsstatus -----------------------------------------

    sql = """CREATE TABLE simulationsstatus (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "simulationsstatus" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'keine Angabe', 0, NULL, 5",
            "'vorhanden', 1, NULL, 0",
            "'geplant', 2, NULL, 1",
            "'fiktiv', 3, NULL, 2",
            "'außer Betrieb (keine Sim.)', 4, NULL, 3",
            "'verfüllt (keine Sim.)', 5, NULL, NULL",
            "'stillgelegt', NULL, NULL, 4",
            "'rückgebaut', NULL, NULL, 6",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO simulationsstatus (bezeichnung, he_nr, mu_nr, kp_nr) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "simulationsstatus" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Auslasstypen -------------------------------------------------------------

    sql = """CREATE TABLE auslasstypen (
    pk INTEGER PRIMARY KEY, 
    bezeichnung TEXT,
    he_nr INTEGER,
    mu_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "auslasstypen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:

        daten = [
            "'frei', 0, NULL, NULL",
            "'normal', 1, NULL, NULL",
            "'konstant', 2, NULL, NULL",
            "'Tide', 3, NULL, NULL",
            "'Zeitreihe', 4, NULL, NULL",
        ]

        for ds in daten:
            cursl.execute(
                "INSERT INTO auslasstypen (bezeichnung, he_nr, mu_nr, kp_nr) VALUES ({})".format(
                    ds
                )
            )

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "auslasstypen" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False
    consl.commit()

    # Abflussparameter -------------------------------------------------------------

    sql = """CREATE TABLE abflussparameter (
    pk INTEGER PRIMARY KEY, 
    apnam TEXT, 
    anfangsabflussbeiwert REAL, 
    endabflussbeiwert REAL, 
    benetzungsverlust REAL, 
    muldenverlust REAL, 
    benetzung_startwert REAL, 
    mulden_startwert REAL, 
    bodenklasse TEXT, 
    flaechentyp INTEGER, 
    kommentar TEXT, 
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "abflussparameter" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:
        daten = [
            "'$Default_Bef', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, NULL, NULL, '13.01.2011 08:44'",
            "'$Default_Unbef', 'Standart qkhe', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', 'Grünfläche', '13.01.2011 08:44'",
            "'Gebäude', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, NULL, 'Gebäude', '13.01.2020 14:13'",
            "'Straße', 'Standart qkhe', 0.25, 0.85, 0.7, 1.8, 0, 0, NULL, 'Straße', '13.01.2020 14:13'",
            "'Grünfläche', 'Standart qkhe', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', 'Grünfläche', '13.01.2020 14:13'",
            "'Gewässer', 'Standart qkhe', 0, 0, 0, 0, 0, 0, NULL, 'Gewässer', '13.01.2020 14:13'",
        ]

        for ds in daten:
            sql = """INSERT INTO abflussparameter
                     ( apnam, kommentar, anfangsabflussbeiwert, endabflussbeiwert, benetzungsverlust, 
                       muldenverlust, benetzung_startwert, mulden_startwert, bodenklasse, flaechentyp, 
                       createdat) Values ({})""".format(
                ds
            )
            cursl.execute(sql)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "abflussparameter" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Tabelle "flaechentypen" --------------------------------------------------------------------

    sql = """CREATE TABLE IF NOT EXISTS flaechentypen (
        pk INTEGER PRIMARY KEY,
        bezeichnung TEXT,
        he_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "flaechentypen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    try:
        daten = [["Gebäude", 0], ["Straße", 1], ["Grünfläche", 2], ["Gewässer", 3]]

        for bez, num in daten:
            sql = u"""INSERT INTO flaechentypen
                     (bezeichnung, he_nr) Values ('{bez}', {num})""".format(
                bez=bez, num=num
            )
            cursl.execute(sql)

    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabellendaten "abflussparameter" konnten nicht hinzugefuegt werden.',
        )
        consl.close()
        return False

    consl.commit()

    # Bodenklasse -------------------------------------------------------------

    sql = """CREATE TABLE bodenklassen (
    pk INTEGER PRIMARY KEY, 
    bknam TEXT, 
    infiltrationsrateanfang REAL,
    infiltrationsrateende REAL,
    infiltrationsratestart REAL,
    rueckgangskonstante REAL,
    regenerationskonstante REAL,
    saettigungswassergehalt REAL,
    kommentar TEXT, 
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "bodenklassen" konnten nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        "'VollDurchlaessig', 10, 9, 10, 144, 1.584, 100, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
        "'Sand', 2.099, 0.16, 1.256, 227.9, 1.584, 12, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
        "'SandigerLehm', 1.798, 0.101, 1.06, 143.9, 0.72, 18, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
        "'LehmLoess', 1.601, 0.081, 0.94, 100.2, 0.432, 23, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
        "'Ton', 1.9, 0.03, 1.087, 180, 0.144, 16, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
        "'Undurchlaessig', 0, 0, 0, 100, 1, 0, '13.01.2011 08:44:50', 'Importiert mit qg2he'",
        "NULL, 0, 0, 0, 0, 0, 0, '13.01.2011 08:44:50', 'nur für interne QKan-Aufgaben'",
    ]

    for ds in daten:
        try:
            sql = """INSERT INTO bodenklassen
                     ( 'bknam', 'infiltrationsrateanfang', 'infiltrationsrateende', 'infiltrationsratestart', 
                       'rueckgangskonstante', 'regenerationskonstante', 'saettigungswassergehalt', 
                       'createdat', 'kommentar') Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "bodenklassen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
                sql,
            )
            consl.close()
            return False
    consl.commit()

    # Abflusstypen -------------------------------------------------------------

    sql = """CREATE TABLE abflusstypen (
    pk INTEGER PRIMARY KEY, 
    abflusstyp TEXT,
    he_nr INTEGER,
    kp_nr INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "abflusstypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        "'Speicherkaskade', 0, 0",
        "'Direktabfluss', 0, 0",
        "'Fliesszeiten', 1, 1",
        "'Schwerpunktlaufzeit', 2, 2",
        "'Schwerpunktfließzeit', 2, 2",
    ]

    for ds in daten:
        try:
            sql = """INSERT INTO abflusstypen
                     (abflusstyp, he_nr, kp_nr) Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "abflusstypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
                sql,
            )
            consl.close()
            return False
    consl.commit()

    # Knotentypen -------------------------------------------------------------

    sql = """CREATE TABLE knotentypen (
    pk INTEGER PRIMARY KEY, 
    knotentyp TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "knotentypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = [
        "'Anfangsschacht'",
        "'Einzelschacht'",
        "'Endschacht'",
        "'Hochpunkt'",
        "'Normalschacht'",
        "'Tiefpunkt'",
        "'Verzweigung'",
        "'Fliesszeiten'",
    ]

    for ds in daten:
        try:
            sql = """INSERT INTO knotentypen
                     ( 'knotentyp') Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "knotentypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
                sql,
            )
            consl.close()
            return False
    consl.commit()

    # Schachttypen -------------------------------------------------------------

    sql = """CREATE TABLE schachttypen (
    pk INTEGER PRIMARY KEY, 
    schachttyp TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Tabelle "schachttypen" konnte nicht erstellt werden.',
        )
        consl.close()
        return False

    daten = ["'Auslass'", "'Schacht'", "'Speicher'"]

    for ds in daten:
        try:
            sql = """INSERT INTO schachttypen
                     ( 'schachttyp') Values ({})""".format(
                ds
            )
            cursl.execute(sql)

        except BaseException as err:
            fehlermeldung(
                "qkan_database.createdbtables: {}".format(err),
                'Tabellendaten "schachttypen" konnten nicht hinzugefuegt werden: \n{}\n'.format(
                    err
                ),
                sql,
            )
            consl.close()
            return False
    consl.commit()

    # Kennlinie Speicherbauwerke -----------------------------------------------

    sql = """CREATE TABLE speicherkennlinien (
    pk INTEGER PRIMARY KEY, 
    schnam TEXT, 
    wspiegel REAL, 
    oberfl REAL)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "Speicherkennlinien".',
        )
        consl.close()
        return False
    consl.commit()

    # Hilfstabelle für den DYNA-Export -----------------------------------------

    sql = """
        CREATE TABLE IF NOT EXISTS dynahal (
            pk INTEGER PRIMARY KEY,
            haltnam TEXT,
            schoben TEXT,
            schunten TEXT,
            teilgebiet TEXT,
            kanalnummer TEXT,
            haltungsnummer TEXT,
            anzobob INTEGER,
            anzobun INTEGER,
            anzunun INTEGER,
            anzunob INTEGER)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "dynahal".',
        )
        consl.close()
        return False
    consl.commit()

    # Hilfstabelle für den Flächen-Export

    sql = """
        CREATE TABLE IF NOT EXISTS flaechen_he8 (
            pk INTEGER PRIMARY KEY,
            Name TEXT, 
            Haltung TEXT, 
            Groesse REAL, 
            Regenschreiber TEXT, 
            Flaechentyp INTEGER, 
            BerechnungSpeicherkonstante INTEGER, 
            Typ INTEGER, 
            AnzahlSpeicher INTEGER, 
            Speicherkonstante REAL, 
            Schwerpunktlaufzeit REAL, 
            FliesszeitOberflaeche REAL, 
            LaengsteFliesszeitKanal REAL, 
            Parametersatz TEXT, 
            Neigungsklasse INTEGER, 
            ZuordnUnabhEZG INTEGER,
            IstPolygonalflaeche SMALLINT, 
            ZuordnungGesperrt SMALLINT, 
            LastModified TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')), 
            Kommentar TEXT)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen der Tabelle "flaechen_he8".',
        )
        consl.close()
        return False

    sql = """SELECT AddGeometryColumn('flaechen_he8','Geometry', -1,
            'MULTIPOLYGON',2)"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen des Attributes "flaechen_he8.Geometry".',
        )
        consl.close()
        return False

    sql = """SELECT CreateSpatialIndex('flaechen_he8', 'Geometry')"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Erzeugen des Spatial Index für Attribut "Geometry".',
        )
        consl.close()
        return False

    consl.commit()

    # Allgemeine Informationen -----------------------------------------------

    sql = """CREATE TABLE info (
    pk INTEGER PRIMARY KEY, 
    subject TEXT, 
    value TEXT,
    createdat TEXT DEFAULT (strftime('%d.%m.%Y %H:%M','now')))"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Tabelle "Info".',
        )
        consl.close()
        return False

    # Plausibilitätskontrollen --------------------------------------------------

    # Prüfung der Anbindungen in "linkfl" auf eindeutige Zuordnung zu Flächen und Haltungen

    sql = """CREATE VIEW IF NOT EXISTS "v_linkfl_check" AS 
            WITH lfok AS
            (   SELECT 
                    lf.pk AS "pk",
                    lf.flnam AS "linkfl_nam", 
                    lf.haltnam AS "linkfl_haltnam", 
                    fl.flnam AS "flaech_nam",
                    tg.flnam AS "tezg_nam",
                    min(lf.pk) AS pkmin, 
                    max(lf.pk) AS pkmax,
                    count(*) AS anzahl
                FROM linkfl AS lf
                LEFT JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam
                WHERE fl.aufteilen = "ja" and fl.aufteilen IS NOT NULL
                GROUP BY fl.flnam, tg.flnam
                UNION
                SELECT 
                    lf.pk AS "pk",
                    lf.flnam AS "linkfl_nam", 
                    lf.haltnam AS "linkfl_haltnam", 
                    fl.flnam AS "flaech_nam",
                    NULL AS "tezg_nam",
                    min(lf.pk) AS pkmin, 
                    max(lf.pk) AS pkmax,
                    count(*) AS anzahl
                FROM linkfl AS lf
                LEFT JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                WHERE fl.aufteilen <> "ja" OR fl.aufteilen IS NULL
                GROUP BY fl.flnam)
            SELECT pk, anzahl, CASE WHEN anzahl > 1 THEN 'mehrfach vorhanden' WHEN flaech_nam IS NULL THEN 'Keine Fläche' WHEN linkfl_haltnam IS NULL THEN  'Keine Haltung' ELSE 'o.k.' END AS fehler
            FROM lfok"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_linkfl_check".',
        )
        consl.close()
        return False

    # Feststellen der Flächen ohne Anbindung

    sql = """CREATE VIEW IF NOT EXISTS "v_flaechen_ohne_linkfl" AS 
            SELECT 
                fl.pk, 
                fl.flnam AS "flaech_nam",
                fl.aufteilen AS "flaech_aufteilen", 
                'Verbindung fehlt' AS "Fehler"
            FROM flaechen AS fl
            LEFT JOIN linkfl AS lf
            ON lf.flnam = fl.flnam
            LEFT JOIN tezg AS tg
            ON tg.flnam = lf.tezgnam
            WHERE ( (fl.aufteilen <> "ja" or fl.aufteilen IS NULL) AND
                     lf.pk IS NULL) OR
                  (  fl.aufteilen = "ja" AND fl.aufteilen IS NOT NULL AND 
                     lf.pk IS NULL)
            UNION
            VALUES
                (0, '', '', 'o.k.') """

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_flaechen_ohne_linkfl".',
        )
        consl.close()
        return False

    # Vergleich der Flächengröße mit der Summe der verschnittenen Teile

    sql = """CREATE VIEW IF NOT EXISTS "v_flaechen_check" AS 
            WITH flintersect AS (
                SELECT fl.flnam AS finam, 
                       CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                       ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                       END AS flaeche
                FROM linkfl AS lf
                INNER JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam)
            SELECT fa.flnam, 
                   AREA(fa.geom) AS flaeche, 
                   sum(fi.flaeche) AS "summe_flaechen_stuecke", 
                   sum(fi.flaeche) - AREA(fa.geom) AS differenz
            FROM flaechen AS fa
            LEFT JOIN flintersect AS fi
            ON fa.flnam = fi.finam
            GROUP BY fa.flnam
            HAVING ABS(sum(fi.flaeche) - AREA(fa.geom)) > 2"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_flaechen_check".',
        )
        consl.close()
        return False

    # Vergleich der Haltungsflächengrößen mit der Summe der verschnittenen Teile

    sql = """CREATE VIEW IF NOT EXISTS "v_tezg_check" AS 
            WITH flintersect AS (
                SELECT tg.flnam AS finam, 
                       CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN area(fl.geom) 
                       ELSE area(CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))) 
                       END AS flaeche
                FROM linkfl AS lf
                INNER JOIN flaechen AS fl
                ON lf.flnam = fl.flnam
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam)
            SELECT tg.flnam, 
                   AREA(tg.geom) AS haltungsflaeche, 
                   sum(fi.flaeche) AS summe_flaechen_stuecke, 
                   sum(fi.flaeche) - AREA(tg.geom) AS differenz
            FROM tezg AS tg
            LEFT JOIN flintersect AS fi
            ON tg.flnam = fi.finam
            GROUP BY tg.flnam
            HAVING ABS(sum(fi.flaeche) - AREA(tg.geom)) > 2"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_tezg_check".',
        )
        consl.close()
        return False

    consl.commit()

    # Doppelte Verbindungslinien an Flächen prüfen
    
    sql = """CREATE VIEW IF NOT EXISTS "v_linkfl_redundant" AS 
            WITH lfm AS (
                SELECT flnam, tezgnam, count(*) AS anz
                FROM linkfl AS lf
                GROUP BY flnam, tezgnam)
            SELECT lf.pk, lf.flnam, lf.tezgnam, lfm.anz
            FROM linkfl AS lf
            LEFT JOIN lfm
            ON lf.flnam = lfm.flnam and lf.tezgnam = lfm.tezgnam
            WHERE anz <> 1 or lf.flnam IS NULL
            ORDER BY lf.flnam"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_linkfl_redundant".',
        )
        consl.close()
        return False

    consl.commit()

    # Doppelte Verbindungslinien an Direkteinleitungen prüfen
    
    sql = """CREATE VIEW IF NOT EXISTS "v_linksw_redundant" AS 
            WITH lsm AS (
                SELECT elnam, count(*) AS anz
                FROM linksw AS ls
                GROUP BY elnam)
            SELECT ls.pk, ls.elnam, lsm.anz
            FROM linksw AS ls
            LEFT JOIN lsm
            ON ls.elnam = lsm.elnam
            WHERE anz <> 1 or ls.elnam IS NULL
            ORDER BY ls.elnam"""

    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createviews: Fehler {}".format(err),
            'Fehler beim Erzeugen der Plausibilitätskontrolle "v_linksw_redundant".',
        )
        consl.close()
        return False

    consl.commit()


    # Abschluss --------------------------------------------------------------------

    # Aktuelle Version eintragen
    sql = """INSERT INTO info (subject, value) VALUES ('version', '{}'); \n""".format(
        version
    )
    try:
        cursl.execute(sql)
    except BaseException as err:
        fehlermeldung(
            "qkan_database.createdbtables: {}".format(err),
            'Fehler beim Einfügen der Tabelle "Info".',
        )
        consl.close()
        return False
    consl.commit()

    fortschritt("Tabellen erstellt...", 0.01)

    return True


# ----------------------------------------------------------------------------------------------------------------------

if __name__ in ("__main__", "__console__", "__builtin__"):

    # Verzeichnis der Testdaten
    pfad = "C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_heqk/beispiele/modelldb_itwh"
    database_QKan = os.path.join(pfad, "test1.sqlite")

    if os.path.exists(database_QKan):
        os.remove(database_QKan)

    consl = spatialite_connect(database=database_QKan)
    cursl = consl.cursor()

    progressMessageBar = iface.messageBar().createMessage("Doing something boring...")
    progress = QProgressBar()
    progress.setMaximum(10)
    progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)
    progress.setValue(2)
    iface.messageBar().clearWidgets()

    iface.mainWindow().statusBar().showMessage(
        "SpatiaLite-Datenbank wird erstellt. Bitte warten... {} %".format(20)
    )
    import time

    time.sleep(1)

    sql = "SELECT InitSpatialMetadata(transaction = TRUE)"
    cursl.execute(sql)

    iface.messageBar().pushMessage(
        "Information", "SpatiaLite-Datenbank ist erstellt!", level=Qgis.Info
    )

    createdbtables(consl, cursl, version="1.0.0")
    consl.close()
