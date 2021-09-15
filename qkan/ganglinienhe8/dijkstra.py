#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
# import sqlite3
from qkan.database.dbfunc import DBConnection
import logging
import tempfile
from pathlib import Path

maxweight = 999999  # Defaultwert für Schacht ohne Verbindung

# Toggle in DEV to log to console
LOG_TO_CONSOLE = False

# Init logging
logger = logging.getLogger("QKan")
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log_path = Path(tempfile.gettempdir()) / "findpath_{}.log".format(
    datetime.datetime.today().strftime("%Y-%m-%d")
)
file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

if LOG_TO_CONSOLE:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)


class Netz():
    """Erzeugt ein Netz aus einer Liste mit Haltungen"""

    # Klassenattribute, damit die Verknüpfungen nach dem Aufbau erhalten bleiben
    links = {}
    weights_template = {}
    haltung = {}
    faktor = 2.0  # Faktor zur Unterscheidung der Fließrichtung
    maxweight = 999999  # Defaultwert für Schacht ohne Verbindung

    def __init__(self, netz=None):
        """Beim ersten Aufruf muss das Netz angegeben werden, damit die Verknüpfungen
        erstellt werden können"""

        self.netz = netz
        if self.netz:
            if Netz.links == {}:
                # Nur beim ersten Aufruf
                for (name, schob, schun, laenge) in self.netz:
                    # In Fließrichtung
                    if schob in Netz.links:
                        Netz.links[schob][schun]=laenge
                        Netz.haltung[schob][schun]=name
                    else:
                        Netz.links[schob] = {schun: laenge}
                        Netz.haltung[schob] = {schun: name}

                    # Gegen die Fließrichtung
                    if schun in Netz.links:
                        Netz.links[schun][schob]=laenge*Netz.faktor
                        Netz.haltung[schun][schob]=name
                    else:
                        Netz.links[schun] = {schob: laenge*Netz.faktor}
                        Netz.haltung[schun] = {schob: name}

                    # Template mit Gewichtungen erstellen
                    Netz.weights_template = {schacht: Netz.maxweight for schacht in Netz.links.keys()}
            else:
                """Verknüpfungen wurden schon aufgebaut"""
                pass
        else:
            if Netz.links == {}:
                raise RuntimeError("Programmfehler: Erstmaliger Aufruf von Netz ohne Netzdaten")

        # Initialisierung der Gewichtungen für die Instanz
        self.__weight = Netz.weights_template.copy()

    def analyse(self, schacht):
        """Verteilt die Schachtgewichtungen ausgehend vom vorgegebenen Schacht"""
        front = [schacht]           # Liste der noch bewertenden Schächte
        self.__weight[schacht] = 0  # Bewertung Ausgangsschacht
        while front:
            frontadd = []  # Liste neu hinzukommender Schächte
            frontdel = []  # Liste nicht mehr zu untersuchender Schächte
            for schanf in front:
                for schend in Netz.links[schanf]:
                    weight_old = self.__weight[schend]
                    weight_new = self.__weight[schanf] + Netz.links[schanf][schend]
                    if weight_new < weight_old:
                        # Schacht schend wird neu bewertet
                        self.__weight[schend] = weight_new
                        changed = True
                        frontadd.append(schend)         # schend muss jetzt auch untersucht werden
                    # Der Schacht braucht nicht weiter untersucht zu werden
                frontdel.append(schanf)
            # Löschen nicht mehr zu untersuchender Schächte.
            for schanf in frontdel:
                front.remove(schanf)
            # Hinzufügen der neu bewerteten Schächte. Es kann
            # durchaus ein gerade entfernter Schacht wieder dabei sein
            for schanf in frontadd:
                front.append(schanf)

    @property
    def weight(self):
        """Gibt Schachtgewichtung zurück"""
        return self.__weight

def findroute(dbname, schachtauswahl):

    qkanDb : DBConnection = DBConnection(dbname=dbname)
    if not qkanDb:
        logger.error(
            "Fehler in dijkstra.findroute:\n"
            f"QKan-Datenbank {qkanDb:s} wurde nicht"
            " gefunden oder war nicht aktuell!\nAbbruch!"
        )
        return False

    # Kanaldaten lesen
    sql = """
        SELECT haltnam, schoben, schunten, laenge
        FROM haltungen
        UNION 
        SELECT wnam AS haltnam, schoben, schunten, 10 AS laenge
        FROM wehre
        UNION
        SELECT pnam AS haltnam, schoben, schunten, 10 AS laenge
        FROM pumpen 
        """
    qkanDb.sql(sql)
    netz = qkanDb.fetchall()

    # schachtauswahl prüfen: Schacht muss als Anfangs- oder Endschacht im Netz vorhanden sein
    for schacht in schachtauswahl:
        if schacht not in [el[1] for el in netz] + [el[2] for el in netz]:
            schachtauswahl.remove(schacht)

    # Dict mit Gewichten bezogen auf die Schächte in 'schachtauswahl'
    # Hinweis: Parameter netz ist nur beim ersten Aufruf wirksam, um Netz.links und Netz.haltungen
    # als Klassenattribute zu erstellen
    knotennetz = {el: Netz(netz) for el in schachtauswahl}
    for schacht in schachtauswahl:
        if schacht in knotennetz:
            knotennetz[schacht].analyse(schacht)
        else:
            logger.error('Dijkstra-Fehler: Schacht {schacht} ist nicht vorhanden')
            schachtauswahl.remove(schacht)

    # Gewichtungen auf der Strecke von 'kvon' nach 'knach' für alle paarweisen
    # Kombinationen aus 'schachtauswahl'
    gewicht = {kvon: {knach: knotennetz[kvon].weight[knach]
                        for knach in schachtauswahl if kvon != knach} for kvon in schachtauswahl}

    # Aufstellung der Liste mit Schächten in Reihenfolge des Länggschnitts: knotenlaengs
    knotenlaengs = []
    krest = schachtauswahl.copy()         # Vorlageliste zur sukzessiven Entnahme

    # Schacht mit der höchsten Wertung ist der Anfangsschacht
    wertung = 0                                     # Initialisierung
    for kvon in gewicht.keys():
        for knach in gewicht[kvon].keys():
            wertakt = gewicht[kvon][knach]      # Wertung des Kandidaten
            if wertakt > wertung:
                knotenMaxWertung = knach
                wertung = wertakt                   # Übernahme der neuen höheren Wertung

    if wertung > maxweight - 0.0001:
        return None

    # Die weiteren Schächte werden jeweils nach der geringsten Wertigkeit gewählt
    knotenlaengs = [knotenMaxWertung]
    krest.remove(knotenMaxWertung)               # Restliste

    schacht = knotenMaxWertung
    knotenMinWertung = None
    while krest:
        wertung = maxweight                         # Initialisierung
        for knach in krest:
            wertakt = gewicht[schacht][knach]
            if wertakt < wertung:
                knotenMinWertung = knach
                wertung = wertakt

        # gefundenen nächsten Schacht verarbeiten
        schacht = knotenMinWertung
        knotenlaengs.append(knotenMinWertung)
        krest.remove(knotenMinWertung)

    schacht = knotenlaengs.pop(0)
    schaechtelaengs = [schacht]
    haltungenlaengs = []

    # Kontrolle, ob mindestens noch ein Schacht
    if not kvon:
        logger.error(f'Fehler in Dijkstra: Weniger als 2 Schächte: {knotenlaengs}')
        return None

    # Sukzessives Durchhangeln mit schacht zum jeweils nächsten Knoten in knotenlaengs
    for knach in knotenlaengs:
        # Schleife solange, bis knach erreicht ist, d.h. kvon == knach
        while schacht != knach:
            # Auswahl des nächsten Schachtes mit der kleinsten Gewichtung bezogen auf knach
            wertung = maxweight                    # Initialisierung
            for schtest in Netz.links[schacht].keys():
                wertakt = knotennetz[knach].weight[schtest]
                if wertakt < wertung:
                    wertung = wertakt
                    schnext = schtest
                    haltnext = Netz.haltung[schacht][schnext]
            schaechtelaengs.append(schnext)
            haltungenlaengs.append(haltnext)

            # Schritt zum nächsten Schacht
            schacht = schnext

    # Letzten Knoten noch anhängen
    schaechtelaengs.append(schacht)

    return schaechtelaengs, haltungenlaengs

if __name__ == '__main__':
    dbname = 'C:/FHAC/Bayernallee/hoettges/NUMERIK/Python/eigene Versuche/dijkstra/nette.sqlite'
    schachtauswahl = ['E120189', 'E120197', 'D120060', 'D120084', 'EP R010']

    schaechtelaengs, haltungenlaengs = findroute(dbname, schachtauswahl)

    if not schaechtelaengs:
        print('Die gewählen Schächte befinden sich nicht in einem zusammenhängenden Netz')
    else:
        for el in zip(schaechtelaengs, haltungenlaengs + ['']):
            print(f'{el[0]}\n {el[1]}')