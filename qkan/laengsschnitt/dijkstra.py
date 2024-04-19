from typing import Dict, List, Optional

from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

MAX_WEIGHT = 999999.0  # Defaultwert für Schacht ohne Verbindung

logger = get_logger("QKan.dijkstra")


# todo: duplicate class?
class Netz:
    """Erzeugt ein Netz aus einer Liste mit Haltungen"""

    # Klassenattribute, damit die Verknüpfungen nach dem Aufbau erhalten bleiben
    #links: Dict[str, Dict[str, float]] = {}
    #weights_template: Dict[str, float] = {}
    #haltung: Dict[str, Dict[str, str]] = {}
    #faktor = 2.0  # Faktor zur Unterscheidung der Fließrichtung

    def __init__(self, netz: None):
        """Beim ersten Aufruf muss das Netz angegeben werden, damit die Verknüpfungen
        erstellt werden können"""
        self.links: Dict[str, Dict[str, float]] = {}
        self.weights_template: Dict[str, float] = {}
        self.haltung: Dict[str, Dict[str, str]] = {}
        self.faktor = 2.0

        self.netz = netz

        if self.netz:
            if self.links == {}:
                # Nur beim ersten Aufruf
                for (name, schob, schun, laenge) in self.netz:
                    if not laenge:
                        laenge = 2.
                    # In Fließrichtung
                    if schob in self.links:
                        self.links[schob][schun]=laenge
                        self.haltung[schob][schun]=name
                    else:
                        self.links[schob] = {schun: laenge}
                        self.haltung[schob] = {schun: name}

                    # Gegen die Fließrichtung
                    if schun in self.links:
                        self.links[schun][schob]=laenge*self.faktor
                        self.haltung[schun][schob]=name
                    else:
                        self.links[schun] = {schob: laenge*self.faktor}
                        self.haltung[schun] = {schob: name}

                    # Template mit Gewichtungen erstellen
                    self.weights_template = {schacht: MAX_WEIGHT for schacht in self.links.keys()}
            else:
                """Verknüpfungen wurden schon aufgebaut"""
                pass
        else:
            if self.links == {}:
                raise RuntimeError("Programmfehler: Erstmaliger Aufruf von Netz ohne Netzdaten")

        # Initialisierung der Gewichtungen für die Instanz
        self.__weight = self.weights_template.copy()



    def analyse(self, schacht: str) -> None:
        """Verteilt die Schachtgewichtungen ausgehend vom vorgegebenen Schacht"""

        # Liste der noch bewertenden Schächte
        front = [schacht]
        # Bewertung Ausgangsschacht
        self.__weight[schacht] = 0

        while front:
            frontadd = []  # Liste neu hinzukommender Schächte
            frontdel = []  # Liste nicht mehr zu untersuchender Schächte

            for schanf in front:
                for schend in self.links[schanf]:
                    weight_old = self.__weight.get(schend, 0)
                    weight_new = (
                        self.__weight.get(schanf, 0) + self.links[schanf][schend]
                    )

                    if weight_new < weight_old:
                        # Schacht schend wird neu bewertet
                        self.__weight[schend] = weight_new
                        # schend muss jetzt auch untersucht werden
                        frontadd.append(schend)

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
    def weight(self) -> Dict[str, float]:
        """Gibt Schachtgewichtung zurück"""
        return self.__weight

#class Route:
 #   def init(self,qkan_db: DBConnection, schachtauswahl):
  #      self.qkan_db=qkan_db
   #     self.schachtauswahl =schachtauswahl

def find_route(qkan_db: DBConnection, schachtauswahl):
    if not qkan_db:
        logger.error(
            "Fehler in dijkstra.find_route:\n"
            f"QKan-Datenbank {qkan_db:s} wurde nicht"
            " gefunden oder war nicht aktuell!\nAbbruch!"
        )
        return None

    # Kanaldaten lesen
    sql = """
            SELECT haltnam, schoben, schunten, laenge
            FROM haltungen
        """
    qkan_db.sql(sql)
    netz = qkan_db.fetchall()

    # schachtauswahl prüfen: Schacht muss als Anfangs- oder Endschacht im Netz vorhanden sein
    for schacht in schachtauswahl.copy():
        if schacht not in [e[1] for e in netz] + [e[2] for e in netz]:
            schachtauswahl.remove(schacht)
            logger.debug(f'Schacht war nicht im Netz enthalten, deshalb entfernt: {schacht}')

    # Dict mit Gewichten bezogen auf die Schächte in 'schachtauswahl'
    # Hinweis: Parameter netz ist nur beim ersten Aufruf wirksam, um Netz.links und Netz.haltungen
    # als Klassenattribute zu erstellen
    knotennetz: Dict[str, Netz] = {e: Netz(netz) for e in schachtauswahl}

    for schacht in schachtauswahl.copy():
        if schacht in knotennetz:
            knotennetz[schacht].analyse(schacht)
        else:
            logger.error('Dijkstra-Fehler: Schacht {schacht} ist nicht vorhanden')
            schachtauswahl.remove(schacht)

    # Gewichtungen auf der Strecke von 'kvon' nach 'knach' für alle paarweisen
    # Kombinationen aus 'schachtauswahl'
    logger.info(knotennetz)
    gewicht: Dict[str, Dict[str, float]] = {
        kvon: {
            knach: knotennetz[kvon].weight.get(knach, 0)
            for knach in schachtauswahl
            if kvon != knach
        }
        for kvon in schachtauswahl
    }

    # Aufstellung der Liste mit Schächten in Reihenfolge des Länggschnitts: knotenlaengs
    knotenlaengs: List[str] = []
    krest: List[str] = schachtauswahl.copy()  # Vorlageliste zur sukzessiven Entnahme

    # Schacht mit der höchsten Wertung ist der Anfangsschacht
    knoten_max_wertung: Optional[str] = None
    wertung = 0.0                                     # Initialisierung

    for kvon in gewicht.keys():
        for knach in gewicht[kvon].keys():
            wertakt = gewicht[kvon][knach]  # Wertung des Kandidaten
            if wertakt > wertung:
                knoten_max_wertung = knach
                wertung = wertakt  # Übernahme der neuen höheren Wertung

    if wertung > MAX_WEIGHT - 0.0001:
        return None

    # Kontrolle, ob mindestens noch ein Schacht
    if knoten_max_wertung is None:
        logger.error(f"Fehler in Dijkstra: Keine Kanäle über Mindestwertung von 0")
        return None

    # Die weiteren Schächte werden jeweils nach der geringsten Wertigkeit gewählt
    knotenlaengs.append(knoten_max_wertung)
    krest.remove(knoten_max_wertung)  # Restliste

    schacht = knoten_max_wertung
    knoten_min_wertung: Optional[str] = None
    while krest:
        wertung = MAX_WEIGHT  # Initialisierung
        for knach in krest:
            wertakt = gewicht[schacht][knach]
            if wertakt < wertung:
                knoten_min_wertung = knach
                wertung = wertakt

        if knoten_min_wertung is None:
            continue

        # gefundenen nächsten Schacht verarbeiten
        schacht = knoten_min_wertung
        knotenlaengs.append(knoten_min_wertung)
        krest.remove(knoten_min_wertung)

    schacht = knotenlaengs.pop(0)
    schaechtelaengs: List[str] = [schacht]
    haltungenlaengs = []

    # Kontrolle, ob mindestens noch ein Schacht
    if len(gewicht) < 1:
        logger.error(f"Fehler in Dijkstra: Weniger als 2 Schächte: {knotenlaengs}")
        return None

    # Sukzessives Durchhangeln mit schacht zum jeweils nächsten Knoten in knotenlaengs
    schnext = None
    haltnext = None
    for knach in knotenlaengs:
        # Schleife solange, bis knach erreicht ist, d.h. kvon == knach
        while schacht != knach:
            # Auswahl des nächsten Schachtes mit der kleinsten Gewichtung bezogen auf knach
            wertung = MAX_WEIGHT   # Initialisierung

            for schtest in knotennetz[knach].links[schacht].keys():
                wertakt = knotennetz[knach].weight[schtest]
                if wertakt < wertung:
                    wertung = wertakt
                    schnext = schtest
                    haltnext = knotennetz[knach].haltung[schacht][schnext]

            if schnext is not None and haltnext is not None:
                # Damit der letzte Schacht nicht doppelt auftaucht
                # if schnext != knach:
                schaechtelaengs.append(schnext)
                haltungenlaengs.append(haltnext)

                # Schritt zum nächsten Schacht
            schacht = schnext

    # Letzten Knoten noch anhängen
    # schaechtelaengs.append(schacht)

    logger.debug(f'Haltungen längs: {haltungenlaengs}')
    logger.debug(f'Schächte längs: {schaechtelaengs}')

    return schaechtelaengs, haltungenlaengs


if __name__ == '__main__':
    dbname = 'C:/FHAC/Bayernallee/hoettges/NUMERIK/Python/eigene Versuche/dijkstra/nette.sqlite'
    # schachtauswahl = ['E120189', 'E120197', 'D120060', 'D120084', 'EP R010']
    schachtauswahl = ['E120170', 'E120136', 'E120172']

    schaechtelaengs, haltungenlaengs = Netz.find_route(dbname, schachtauswahl)

    if not schaechtelaengs:
        print('Die gewählen Schächte befinden sich nicht in einem zusammenhängenden Netz')
    else:
        for el in zip(schaechtelaengs, haltungenlaengs + ['']):
            print(f'{el[0]}\n {el[1]}')