import logging
from typing import Any, Dict, List, Optional, Tuple, cast

from qkan.database.dbfunc import DBConnection
from qkan.ganglinienhe8.models import HaltungenStruct
from .models import LayerType

MAX_WEIGHT = 999999.0  # Defaultwert für Schacht ohne Verbindung

logger = logging.getLogger("QKan.ganglinienhe8.dijkstra")

NetzType = List[Tuple[str, str, str, float]]


class Netz:
    """Erzeugt ein Netz aus einer Liste mit Haltungen"""

    # Klassenattribute, damit die Verknüpfungen nach dem Aufbau erhalten bleiben
    links: Dict[str, Dict[str, float]] = {}
    weights_template: Dict[str, float] = {}
    haltung: Dict[str, Dict[str, str]] = {}
    faktor = 2.0  # Faktor zur Unterscheidung der Fließrichtung

    def __init__(self, netz = None):
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
                    Netz.weights_template = {schacht: MAX_WEIGHT for schacht in Netz.links.keys()}
            else:
                """Verknüpfungen wurden schon aufgebaut"""
                pass
        else:
            if Netz.links == {}:
                raise RuntimeError("Programmfehler: Erstmaliger Aufruf von Netz ohne Netzdaten")

        # Initialisierung der Gewichtungen für die Instanz
        self.__weight = Netz.weights_template.copy()

        #
        # self.netz = netz
        #
        # if netz is None and len(Netz.links) == 0:
        #     raise RuntimeError(
        #         "Programmfehler: Erstmaliger Aufruf von Netz ohne Netzdaten"
        #     )
        #
        # # Initialisierung der Gewichtungen für die Instanz
        # self.__weight = Netz.weights_template.copy()
        #
        # # netz ist None, hier muss nichts erledigt werden
        # if self.netz is None:
        #     return
        #
        # # Verknüpfungen wurden schon aufgebaut
        # if len(Netz.links) != 0:
        #     return
        #
        # # Nur beim ersten Aufruf
        # for name, schob, schun, laenge in cast(NetzType, self.netz):
        #     # In Fließrichtung
        #     if schob in Netz.links:
        #         Netz.links[schob][schun] = laenge
        #         Netz.haltung[schob][schun] = name
        #     else:
        #         Netz.links[schob] = {schun: laenge}
        #         Netz.haltung[schob] = {schun: name}
        #
        #     # Gegen die Fließrichtung
        #     if schun in Netz.links:
        #         Netz.links[schun][schob] = laenge * Netz.faktor
        #         Netz.haltung[schun][schob] = name
        #     else:
        #         Netz.links[schun] = {schob: laenge * Netz.faktor}
        #         Netz.haltung[schun] = {schob: name}
        #
        #     # Template mit Gewichtungen erstellen
        #     Netz.weights_template = {
        #         schacht: MAX_WEIGHT for schacht in Netz.links.keys()
        #     }

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
                for schend in Netz.links[schanf]:
                    weight_old = self.__weight.get(schend, 0)
                    weight_new = (
                        self.__weight.get(schanf, 0) + Netz.links[schanf][schend]
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


def get_info(qkan_db: DBConnection, schaechte: List[str], haltungen: List[str]) -> Tuple[Any, Any]:
    """
    * Erstellt Dictionarys, welche folgende Informationen beinhalten.
    * Es wird je ein Dictionary für die Schächte und die Haltungen gemacht.
    * Schacht- bzw. Haltungs-Name entspricht dem Key.
    - Schacht:
        +sohlhoehe:float
        +deckelhoehe:float
    - Haltung:
        +laenge:float
        +schachtoben:str (Schacht-Name aus QGis)
        +schachtunten:str (Schacht-Name aus QGis)
        +sohlhoeheunten:float
        +sohlhoeheoben:float
        +querschnitt:float

    :param qkan_db: QKan DB
    :param route: Beinhaltet getrennt von einander die Haltungs- und Schacht-Namen aus QGis.
    :return: Gibt ein Tuple von zwei Dictionaries zurück mit allen Haltungs- und Schacht-Namen und den
    nötigen Informationen zu diesen
    """
    haltung_info = {}
    schacht_info = {}

    statement = """
        SELECT
            * 
        FROM
            (
            SELECT
                haltnam AS name,
                schoben,
                schunten,
                laenge,
                COALESCE( sohleoben, SO.sohlhoehe ) AS sohleoben,
                COALESCE( sohleunten, SU.sohlhoehe ) AS sohleunten,
                hoehe 
            FROM
                haltungen
                LEFT JOIN ( SELECT sohlhoehe, schnam FROM schaechte ) AS SO ON haltungen.schoben = SO.schnam
                LEFT JOIN ( SELECT sohlhoehe, schnam FROM schaechte ) AS SU ON haltungen.schunten = SU.schnam UNION
            SELECT
                wnam AS name,
                schoben,
                schunten,
                laenge,
                SO.sohlhoehe AS sohleoben,
                SU.sohlhoehe AS sohleunten,
                0.5 AS hoehe 
            FROM
                wehre
                LEFT JOIN ( SELECT sohlhoehe, schnam FROM schaechte ) AS SO ON wehre.schoben = SO.schnam
                LEFT JOIN ( SELECT sohlhoehe, schnam FROM schaechte ) AS SU ON wehre.schunten = SU.schnam UNION
            SELECT
                pnam AS name,
                schoben,
                schunten,
                5 AS laenge,
                SO.sohlhoehe AS sohleoben,
                SU.sohlhoehe AS sohleunten,
                0.5 AS hoehe 
            FROM
                pumpen
                LEFT JOIN ( SELECT sohlhoehe, schnam FROM schaechte ) AS SO ON pumpen.schoben = SO.schnam
                LEFT JOIN ( SELECT sohlhoehe, schnam FROM schaechte ) AS SU ON pumpen.schunten = SU.schnam 
            ) 
        WHERE
            name IN ('{}')
        """
    halselected = "', '".join(haltungen)
    qkan_db.sql(statement.format(halselected))
    for (
        name,
        schachtoben,
        schachtunten,
        laenge,
        sohlhoeheoben,
        sohlhoeheunten,
        querschnitt,
        ) in qkan_db.fetchall():
        haltung_info[name] = dict(
            schachtoben=schachtoben,
            schachtunten=schachtunten,
            laenge=laenge,
            sohlhoeheoben=sohlhoeheoben,
            sohlhoeheunten=sohlhoeheunten,
            querschnitt=querschnitt,
        )
    logger.info("Haltunginfo wurde erstellt")

    statement = """SELECT schnam, deckelhoehe, sohlhoehe FROM schaechte WHERE schnam IN ('{}')"""
    schselected = "', '".join(schaechte)
    qkan_db.sql(statement.format(schselected))
    for (
        name,
        deckelhoehe,
        sohlhoehe,
        ) in qkan_db.fetchall():
        schacht_info[name] = dict(
            deckelhoehe=deckelhoehe,
            sohlhoehe=sohlhoehe,
        )
    logger.info("Schachtinfo wurde erstellt")

    return schacht_info, haltung_info


def find_route(dbname: str, auswahl: List[str], layer_type: int) -> Optional[HaltungenStruct]:
    qkan_db: DBConnection = DBConnection(dbname=dbname)
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
        UNION
            SELECT wnam AS haltnam, schoben, schunten, 10.0 AS laenge
            FROM wehre
        UNION
            SELECT pnam AS haltnam, schoben, schunten, 10.0 AS laenge
            FROM pumpen
        """
    qkan_db.sql(sql)
    data = qkan_db.fetchall()
    netz = cast(NetzType, data)

    if layer_type == LayerType.Haltung:
        netzdict = dict([(hal[0], (hal[1], hal[2])) for hal in netz])
        schachtauswahl = list(set([netzdict[haltung][0] for haltung in auswahl] + \
                                  [netzdict[haltung][1] for haltung in auswahl]))
    elif layer_type == LayerType.Schacht:
        schachtauswahl = auswahl
    else:
        logger.error(f'Fehler bei der Objektauswahl\n'
                     f'Auswahl: {schachtauswahl}\n'
                     f'Auswahltyp: {layer_type}')
        return None

    logger.debug(f'Objektauswahl\n'
                 f'Auswahl: {schachtauswahl}\n'
                 f'Auswahltyp ({LayerType.Schacht}=Schächte, {LayerType.Haltung}=Haltungen): {layer_type}')

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
            logger.error("Dijkstra-Fehler: Schacht %s ist nicht vorhanden", schacht)
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
    wertung = 0.0

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
            wertung = MAX_WEIGHT

            for schtest in Netz.links[schacht].keys():
                wertakt = knotennetz[knach].weight[schtest]
                if wertakt < wertung:
                    wertung = wertakt
                    schnext = schtest
                    haltnext = Netz.haltung[schacht][schnext]

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

    schinfolaengs, halinfolaengs = get_info(qkan_db, schaechtelaengs, haltungenlaengs)

    return {
        "haltungen": haltungenlaengs,
        "schaechte": schaechtelaengs,
        "schachtinfo": schinfolaengs,
        "haltunginfo": halinfolaengs,
    }
