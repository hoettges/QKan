# -*- coding: utf-8 -*-
from QKan_Database.dbfunc import DBConnection
from PyQt4 import QtCore
import logging
import os.path

main_logger = logging.getLogger("QKan_Database")
main_logger.setLevel(logging.INFO)
logging_file = os.path.join(os.path.dirname(__file__), "log_navigation.txt")
ch = logging.FileHandler(filename=logging_file, mode="a", encoding="utf8")
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
ch.setFormatter(formatter)
main_logger.addHandler(ch)
main_logger.info("Navigation-Modul gestartet")


class Navigator:
    def __init__(self, dbname, _id):
        """
        Constructor

        :param dbname: Entspricht dem Datei-Pfad zur SpatiaLite-Datenbank.
        :type dbname: str
        :param _id: Entspricht einem float, welche für alle Navigator-Instanzen unique sein sollte.
        :type _id: float
        """
        self.__id = _id
        self.__dbname = dbname
        self.__error_msg = ""
        self.db = DBConnection(dbname)
        self.log = logging.getLogger("QKan_Database.navigation.Navigator")

    def get_id(self):
        """
        Getter der ID

         :return: Gibt die ID zurück
         :rtype: float
        """
        return self.__id

    def calculate_route_schacht(self, nodes):
        """
        * Wird ausgeführt, wenn eine Route zwischen Schächten gefunden werden soll.
        * Berechnet die Route aus Start- und Endpunkt, prüft am Ende, ob alle anderen Schächte innerhalb der
        berechneten Route liegen.
        * Benötigt mindestens zwei Schächte

        :param nodes: Entspricht einer Liste von den selektierten Schacht-Namen aus QGis.
        :type nodes: list
        :return: Gibt ein Routen-Objekt zurück mit allen Haltungen und Schächten
        :rtype: list
        """
        self.log.debug(u"Übergebene Schächte:\t{}".format(nodes))
        endpoint = nodes[0]
        startpoint = nodes[0]
        statement = u"""
        SELECT sohlhoehe FROM schaechte WHERE schnam="{}"
        """
        self.db.sql(statement.format(nodes[0]))
        min_value, = self.db.fetchone()
        max_value = min_value
        for n in nodes:
            self.db.sql(statement.format(n))
            value, = self.db.fetchone()
            if value < min_value:
                min_value = value
                endpoint = n
            elif value > max_value:
                max_value = value
                startpoint = n
        self.log.info(u"Start- und Endpunkt wurden gesetzt")
        self.log.debug(u"Startpunkt:\t{}\nEndpunkt:\t{}".format(startpoint, endpoint))
        nodes.remove(startpoint)
        nodes.remove(endpoint)
        if len(nodes) == 0:
            nodes = None
        self.log.debug(u"Zusätzliche Punkte:\t{}".format(nodes))
        return self.__calculate_route_schacht(startpoint, endpoint, additional_points=nodes)

    def __calculate_route_schacht(self, startpoint, endpoint, additional_points):
        """
        Berechnet die Schächte und Haltungen, die zwischen einem Start- und Endpunkt liegen.
        * Start- und Endhöhe müssen nicht in der richtigen Reihenfolge übergeben werden.
        * Zusätzliche Punkte müssen nur übergeben werden, wenn der Endpunkt über mehrere Wege zu erreichen ist.

        :param startpoint: Entspricht dem Schacht-Namen aus QGis.
        :type startpoint:str
        :param endpoint: Entspricht dem Schacht-Namen aus QGis.
        :type endpoint: str
        :param additional_points: Entspricht einer Liste von Schacht-Namen, die zusätzlich ausgewählt wurden.
        :type additional_points: list
        :return: Gibt ein Routen-Objekt zurück, bestehend aus allen Haltungen und Schächten
        :rtype: dict
        """
        # statement = u"""
        #     SELECT sohlhoehe FROM schaechte WHERE schnam="{}"
        # """
        # self.__db.sql(statement.format(startpoint))
        # start_hoehe, = self.__db.fetchone()
        # self.__db.sql(statement.format(endpoint))
        # end_hoehe, = self.__db.fetchone()
        # if start_hoehe < end_hoehe:
        #     tmp = startpoint
        #     startpoint = endpoint
        #     endpoint = tmp
        statement = u"""
        SELECT name
        FROM (SELECT
                haltnam AS name,
                schoben
              FROM haltungen
              UNION SELECT
                      wnam AS name,
                      schoben
                    FROM wehre
              UNION SELECT
                      pnam AS name,
                      schoben
                    FROM pumpen)
        WHERE schoben ="{}"
                """
        self.db.sql(statement.format(startpoint))
        start_haltungen = [h[0] for h in self.db.fetchall()]
        self.log.debug(u"Start-Haltungen:\t{}".format(start_haltungen))
        statement_2 = u"""
                SELECT name
                FROM (SELECT
                        haltnam AS name,
                        schunten
                      FROM haltungen
                      UNION SELECT
                              wnam AS name,
                              schunten
                            FROM wehre
                      UNION SELECT
                              pnam AS name,
                              schunten
                            FROM pumpen)
                WHERE schunten ="{}"
                        """
        self.db.sql(statement_2.format(endpoint))
        end_haltungen = [h[0] for h in self.db.fetchall()]
        self.log.debug(u"End-Haltungen:\t{}".format(end_haltungen))
        nodes = []
        if additional_points is not None:
            for p in additional_points:
                self.db.sql(statement.format(p))
                nodes += [h[0] for h in self.db.fetchall()]
        possibilities = 0
        nodes = list(set(nodes))
        route = None
        self.log.debug(u"Zusätzliche Haltungen:\t{}".format(nodes))
        self.log.info(u"Alle nötigen Haltungen gesetzt")
        for start_haltung in start_haltungen:
            for end_haltung in end_haltungen:
                _nodes = list(set([start_haltung, end_haltung] + nodes))
                self.log.debug(u"Aktuelle Haltungen:\t{}".format(_nodes))
                _route = self.calculate_route_haltung(_nodes)
                if _route:
                    self.log.info(u"Aktuelle Route ist valide")
                    possibilities += 1
                    if possibilities > 1:
                        self.log.error(u"Zu viele Möglichkeiten zwischen Start- und End-Haltung.")
                        self.__error_msg = u"Zu viele Möglichkeiten. Bitte wählen Sie einen Wegpunkt auf" \
                                           u" dem kritischen Pfad!"
                        return None
                    route = _route
        return route

    def calculate_route_haltung(self, nodes):
        """
        Berechnet eine Route zwischen mehreren Haltungen.

        :param nodes: Alle selektierten Haltungs-Namen aus QGis
        :type nodes: list
        :return: Gibt eine Routen-Objekt mit allen Haltungen und Schächten zurück
        :rtype: dict
        """
        tasks = Tasks(self.__dbname, nodes)
        self.log.info(u"Tasks wurden initialisiert")
        routes = tasks.start()
        self.log.info(u"Alle möglichen Routen ({}) berechnet".format(len(routes)))
        counter = 0
        result = None
        for route in routes:
            if set(route).issuperset(nodes):
                counter += 1
                result = route
        if counter == 1:
            self.log.info(u"Eine einzige mögliche Route gefunden")
            return self.__fetch_data(result)
        elif counter == 0:
            self.log.error(u"Keine Route gefunden. Pfad ist fehlerhaft!")
            self.__error_msg = u"Übergebener Pfad ist fehlerhaft."
            return None
        else:
            self.log.error(u"Es gibt {} mögliche Routen. Der Pfad muss spezifiziert werden".format(counter))
            self.__error_msg = u"Mehrere Möglichkeiten ({}) den Endpunkt zu erreichen. Bitte spezifizieren Sie die Route.".format(
                counter)
            return None

    def __fetch_data(self, haltungen):
        """
        Fragt die Datenbank nach den benötigten Attributen ab und speichert sie in einem Dictionary.
        Das Dictionary hat folgende Struktur:
        *{haltungen:[haltungsnamen],
        schaechte:[schachtnamen],
        schachtinfo:{schachtname:
            {sohlhoehe:float,
            deckelhoehe:float}
            },
        haltunginfo:{haltungsname:
            {schachtoben: schachtname,
            schachtunten: schachtname,
            laenge: float,
            sohlhoeheoben: float,
            sohlhoeheunten: float,
            querschnitt: float}
            }
        }

        :param haltungen: Liste aller Haltungs-Namen aus QGis
        :type haltungen: list
        :return: Gibt ein Routen-Objekt zurück.
        :rtype: dict
        """
        statement = u"""
         SELECT schoben
         FROM (SELECT
                 haltnam AS name,
                 schoben
               FROM haltungen
               UNION SELECT
                       wnam AS name,
                       schoben
                     FROM wehre
               UNION SELECT
                       pnam AS name,
                       schoben
                     FROM pumpen)
         WHERE name = "{}"
                 """
        schaechte = []
        self.log.debug(u"Haltungen:\t{}".format(haltungen))
        self.db.sql(statement.format(haltungen[0]))
        schaechte.append(self.db.fetchone()[0])
        statement = u"""
             SELECT schunten
             FROM (SELECT
                  haltnam AS name,
                  schunten
                   FROM haltungen
                   UNION SELECT
                   wnam AS name,
                   schunten
                    FROM wehre
                    UNION SELECT
                   pnam AS name,
                   schunten
                  FROM pumpen)
             WHERE name = "{}"
             """
        for h in haltungen:
            self.db.sql(statement.format(h))
            schaechte.append(self.db.fetchone()[0])
        self.log.debug(u"Schächte:\t{}".format(schaechte))
        route = dict(haltungen=haltungen, schaechte=schaechte)

        route["schachtinfo"], route["haltunginfo"] = self.get_info(route)
        self.log.info(u"Route wurde erfolgreich erstellt!")
        return route

    def get_info(self, route):
        pass


    def get_error_msg(self):
        """
        Getter der Error-Message.

        :return: Gibt die Error-Message zurück
        :rtype: str
        """
        return self.__error_msg


class Worker(QtCore.QRunnable):
    def __init__(self, dbname, startpoint, nodes, parent):
        """
        Constructor

        :param dbname:Entspricht dem SpatiaLite-Datenbank-Pfad
        :type dbname: str
        :param startpoint:Haltungs-Name des Startpunktes
        :type startpoint: str
        :param nodes: Liste alle Haltungs-Namen, die in der Route vorkommen müssen
        :type nodes: list
        :param parent: Verweis auf die Task-Klasse, damit die Ergebnisse gespeichert werden können
        :type parent: Tasks
        """
        super(Worker, self).__init__()
        self.__startpoint = startpoint
        self.__nodes = nodes
        self.__db = DBConnection(dbname)
        self.__parent = parent

    def run(self):
        """
        Berechnet alle Routen zwischen einem Startpunkt und allen anderen Punkten
        """
        routes = self.__get_routes(self.__startpoint)
        for route in routes:
            self.__parent.results.append(route)

    def __get_routes(self, startpoint):
        """
        Berechnet rekursiv alle Routen von einem Startpunkt bis zum Endpunkt (Keine weitere Haltung verfügbar)
        Außerdem wird abgebrochen, wenn alle Punkte in der Route vorkommen.

        :param startpoint: Entspricht dem Haltungs-Namen des Startpunkts aus QGis
        :type startpoint: str
        :return: Gibt eine Liste von allen möglichen Routen zurück
        :rtype: list
        """
        statement = u"""SELECT name
        FROM (SELECT
                haltnam AS name,
                schoben
              FROM haltungen
              UNION SELECT
                      wnam AS name,
                      schoben
                    FROM wehre
              UNION SELECT
                      pnam AS name,
                      schoben
                    FROM pumpen)
        WHERE schoben =
          (SELECT schunten
           FROM (SELECT
                   haltnam AS name,
                   schunten
                 FROM haltungen
                 UNION SELECT
                         wnam AS name,
                         schunten
                       FROM wehre
                 UNION SELECT
                         pnam AS name,
                         schunten
                       FROM pumpen)
           WHERE name = "{}")
            """
        next_haltung = startpoint
        routes = []
        haltungen = [next_haltung]
        next_haltungen = []
        while not set(haltungen).issuperset(set(self.__nodes)):
            self.__db.sql(statement.format(next_haltung))
            next_haltungen = self.__db.fetchall()
            if len(next_haltungen) == 0:
                break
            elif len(next_haltungen) == 1:
                next_haltung, = next_haltungen[0]
                haltungen.append(next_haltung)
            else:
                break
        if len(next_haltungen) > 1:
            for option, in next_haltungen:
                for route in self.__get_routes(option):
                    routes.append(haltungen + route)
        else:
            routes.append(haltungen)
        return routes


class Tasks(QtCore.QObject):
    def __init__(self, dbname, nodes):
        """
        Constructor

        :param dbname:Entspricht dem SpatialListe-Datenbank-Pfad
        :type dbname: str
        :param nodes: Entspricht einer Liste von allen Haltungsnamenm, welche in der Route vorkommen sollen.
        :type nodes: list
        """
        super(Tasks, self).__init__()
        self.pool = QtCore.QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(2)
        self.__dbname = dbname
        self.__nodes = nodes
        self.results = []

    def start(self):
        """
        Startet alle Threads für jeden möglichen Startpunkt

        :return: Gibt alle möglichen Routen zurück nachdem alle Threads beendet wurden
        :rtype: list
        """
        for n in self.__nodes:
            others = list(self.__nodes)
            others.remove(n)
            worker = Worker(self.__dbname, n, others, self)
            self.pool.start(worker)
        self.pool.waitForDone()
        return self.results
