# -*- coding: utf-8 -*-
from QKan_Database.dbfunc import DBConnection


class Navigator:
    def __init__(self, db, _id):
        """
        Constructor

        :param db: Entspricht dem Datei-Pfad zur SpatiaLite-Datenbank. 
        :type db: str
        :param _id: Entspricht einem float, welche für alle Navigator-Instanzen unique sein sollte.
        :type _id: float
        """
        self.__id = _id
        self.__db = DBConnection(db)

    def get_id(self):
        """
        Getter der ID 
        """
        return self.__id

    def calculate_route_haltungen(self, startpoint, endpoint=None, additional_points=None):
        """
        * Führt die Berechnungen für die Route für jeweils den Start- und Endpunkt durch
        * Fließrichtung ist nicht immer eindeutig

        :param startpoint: Entspricht dem Haltungs-Namen aus QGis.
        :type startpoint:str
        :param endpoint: Entspricht dem Haltungs-Namen aus QGis.
        :type endpoint: str
        :param additional_points: Entspricht einer Liste von Haltungs-Namen, die zusätzlich ausgewählt wurden.
        :type additional_points: list
        :return:* Ob das berechnen funktioniert hat
                * Die Route als Dictionary unterteilt in Haltungen und Schächte
                * Ob das Plugin neu laden muss. Wenn bspw. eine falsche Datenbank übergeben wurde.
        :rtype: (bool,dict,bool)
        """
        res, a, b = self.__calculate_route_haltungen(startpoint, endpoint, additional_points)
        if res:
            return res, a, b
        else:
            return self.__calculate_route_haltungen(endpoint, startpoint, additional_points)

    def __calculate_route_haltungen(self, startpoint, endpoint=None, additional_points=None):
        """
        Berechnet die Schächte und Haltungen, die zwischen einem Start- und Endpunkt liegen.
        * Start- und Endhöhe müssen nicht in der richtigen Reihenfolge übergeben werden.
        * Zusätzliche Punkte müssen nur übergeben werden, wenn der Endpunkt über mehrere Wege zu erreichen ist.

        :param startpoint: Entspricht dem Haltungs-Namen aus QGis.
        :type startpoint:str 
        :param endpoint: Entspricht dem Haltungs-Namen aus QGis.
        :type endpoint: str
        :param additional_points: Entspricht einer Liste von Haltungs-Namen, die zusätzlich ausgewählt wurden. 
        :type additional_points: list
        :return:* Ob das berechnen funktioniert hat
                * Die Route als Dictionary unterteilt in Haltungen und Schächte
                * Ob das Plugin neu laden muss. Wenn bspw. eine falsche Datenbank übergeben wurde.
        :rtype: (bool,dict,bool)
        """
        if startpoint is None:
            startpoint = endpoint
            endpoint = None
        if endpoint is not None:
            if additional_points is None:
                additional_points = [endpoint]
            else:
                additional_points.append(endpoint)
        haltungen = []
        schaechte = []
        next_haltung = startpoint
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
        while next_haltung != endpoint:
            haltungen.append(next_haltung)
            self.__db.sql(statement.format(next_haltung))
            try:
                _next_haltungen = [t[0] for t in self.__db.fetchall()]
                if endpoint in _next_haltungen:
                    break
                if len(_next_haltungen) > 1:
                    solution = self.__decide_direction(_next_haltungen, additional_points)
                    if solution:
                        next_haltung = solution
                    else:
                        return False, u"Zu viele Möglichkeiten oder Pfad unerreichbar. Bitte wählen Sie einen Wegpunkt" \
                                      u" auf dem kritischen Pfad!", False

                elif len(_next_haltungen) == 0:
                    return False, u"Endpunkt nicht erreichbar!", False
                else:
                    next_haltung = _next_haltungen[0]
            except TypeError as e:
                return False, u"Endpunkt nicht erreichbar!", False
        haltungen.append(endpoint)
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
        self.__db.sql(statement.format(haltungen[0]))
        schaechte.append(self.__db.fetchone()[0])
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
            self.__db.sql(statement.format(h))
            schaechte.append(self.__db.fetchone()[0])
        route = {"haltungen": haltungen, "schaechte": schaechte}
        schacht_info, haltung_info = self.__fetch_data(route)
        route["schachtinfo"] = schacht_info
        route["haltunginfo"] = haltung_info
        return True, route, False

    def __get_possibilities(self, options, additional_points):
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
        possibilities = []
        for option in options:
            run = [option]
            if option in additional_points:
                possibilities.append(run)
                continue
            self.__db.sql(statement.format(option))
            next_haltungen = [t[0] for t in self.__db.fetchall()]
            if len(next_haltungen) == 0:
                continue
            elif len(next_haltungen) == 1:
                run.append(next_haltungen[0])
                self.__db.sql(statement.format(next_haltungen[0]))
                next_haltungen = [t[0] for t in self.__db.fetchall()]
                while len(next_haltungen) == 1:
                    run.append(next_haltungen[0])
                    if next_haltungen[0] in additional_points:
                        possibilities.append(run)
                        break
                    self.__db.sql(statement.format(next_haltungen[0]))
                    next_haltungen = [t[0] for t in self.__db.fetchall()]
                if len(next_haltungen) == 0:
                    continue
            if len(next_haltungen) == 1:
                continue
            else:
                for r in self.__get_possibilities(next_haltungen, additional_points):
                    if len(r) > 0:
                        possibilities.append(run + r)
        return possibilities

    def calculate_route_schaechte(self, startpoint, endpoint, additional_points=None):
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
        :return:* Ob das berechnen funktioniert hat
                * Die Route als Dictionary unterteilt in Haltungen und Schächte
                * Ob das Plugin neu laden muss. Wenn bspw. eine falsche Datenbank übergeben wurde.
        :rtype: (bool,dict,bool)
        """
        statement = u"""
        SELECT sohlhoehe FROM schaechte WHERE schnam="{}"
        """
        self.__db.sql(statement.format(startpoint))
        start_hoehe, = self.__db.fetchone()
        self.__db.sql(statement.format(endpoint))
        end_hoehe, = self.__db.fetchone()
        if start_hoehe < end_hoehe:
            tmp = startpoint
            startpoint = endpoint
            endpoint = tmp
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
        self.__db.sql(statement.format(startpoint))
        start_haltungen = [h[0] for h in self.__db.fetchall()]
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
        self.__db.sql(statement_2.format(endpoint))
        end_haltungen = [h[0] for h in self.__db.fetchall()]
        nodes = []
        if additional_points is not None:
            for p in additional_points:
                self.__db.sql(statement.format(p))
                nodes += [h[0] for h in self.__db.fetchall()]
        possibilities = 0
        route = None
        error = ""
        _reload = False
        nodes = list(set(nodes))
        for start_haltung in start_haltungen:
            for end_haltung in end_haltungen:
                _res, _route, must_reload = self.calculate_route_haltungen(start_haltung, end_haltung, nodes)
                if _res:
                    possibilities += 1
                    if possibilities > 1:
                        return False, u"Zu viele Möglichkeiten. Bitte wählen Sie einen Wegpunkt auf" \
                                      u" dem kritischen Pfad!", False
                    route = _route
                else:
                    if _reload is not True:
                        _reload = must_reload
                    error = _route
        if route is None:
            return False, error, _reload
        schacht_info, haltung_info = self.__fetch_data(route)
        route["schachtinfo"] = schacht_info
        route["haltunginfo"] = haltung_info
        return True, route, False

    def __decide_direction(self, options, additional_points):
        possibilities = self.__get_possibilities(options, additional_points)
        possible_runs = []
        for run in possibilities:
            for p in run:
                if p in additional_points[:-1]:
                    possible_runs.append(run)
        if len(possible_runs) > 0:
            pos = -1
            first_p = ""
            _run = None
            for run in possible_runs:
                for i, p in enumerate(run):
                    if p in additional_points:
                        if first_p == "":
                            first_p = p
                            pos = i
                            _run = run
                            break
                        elif first_p == p:
                            return False
                        else:
                            if i < pos:
                                _run = run
            if _run is not None:
                return _run[0]

        return False

    def check_route_haltungen(self, nodes):
        """
        * Wird ausgeführt, wenn mehr als ein Start- und Endpunkt übergeben wurde.
        * Berechnet die Route aus Start- und Endpunkt, prüft am Ende, ob alle anderen Haltungen innerhalb der 
        berechneten Route liegen.

        :param nodes: Entspricht einer Liste von den selektierten Haltungs-Namen aus QGis.
        :type nodes: list
        :return:* Ob das berechnen funktioniert hat
                * Die Route als Dictionary unterteilt in Haltungen und Schächte
                * Ob das Plugin neu laden muss. Wenn bspw. eine falsche Datenbank übergeben wurde.
        :rtype: (bool,dict,bool)
        """
        route = ""
        for node in nodes:
            _additional = list(nodes)
            _additional.remove(node)
            for a in _additional:
                additional = list(_additional)
                additional.remove(a)
                res, route, _reload = self.__calculate_route_haltungen(node, a, additional)
                if res:
                    _result = True
                    for n in nodes:
                        if n not in route["haltungen"]:
                            _result = False
                    if _result:
                        return res, route, _reload
        route = u"Gegebener Pfad ist fehlerhaft" if isinstance(route, dict) else route
        return False, route, False

    def check_route_schaechte(self, nodes):
        """
        * Wird ausgeführt, wenn mehr als ein Start- und Endpunkt übergeben wurde.
        * Berechnet die Route aus Start- und Endpunkt, prüft am Ende, ob alle anderen Schächte innerhalb der 
        berechneten Route liegen.

        :param nodes: Entspricht einer Liste von den selektierten Schacht-Namen aus QGis.
        :type nodes: list
        :return:* Ob das berechnen funktioniert hat
                * Die Route als Dictionary unterteilt in Haltungen und Schächte
                * Ob das Plugin neu laden muss. Wenn bspw. eine falsche Datenbank übergeben wurde.
        :rtype: (bool,dict,bool) 
        """
        endpoint = nodes[0]
        startpoint = nodes[0]
        statement = u"""
        SELECT sohlhoehe FROM schaechte WHERE schnam="{}"
        """
        self.__db.sql(statement.format(nodes[0]))
        min_value, = self.__db.fetchone()
        max_value = min_value
        for n in nodes:
            self.__db.sql(statement.format(n))
            value, = self.__db.fetchone()
            if value < min_value:
                min_value = value
                endpoint = n
            elif value > max_value:
                max_value = value
                startpoint = n
        nodes.remove(startpoint)
        nodes.remove(endpoint)
        if len(nodes) == 0:
            nodes = None
        res, route, _reload = self.calculate_route_schaechte(startpoint, endpoint, additional_points=nodes)
        if not res:
            return False, route, _reload
        if nodes is not None:
            for n in nodes:
                if n not in route["schaechte"]:
                    return False, u"Gegebener Pfad ist fehlerhaft!", False
        return res, route, _reload

    def __fetch_data(self, route):
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

        :param route: Beinhaltet getrennt von einander die Haltungs- und Schacht-Namen aus QGis.
        :type route: dict 
        :return: Gibt ein Dictionary zurück mit allen Haltungs- und Schacht-Namen und den nötigen Informationen zu 
                diesen
        :rtype: dict
        """
        haltung_info = {}
        schacht_info = {}
        statement = u"""
                SELECT * FROM (SELECT
                         haltnam                            AS name,
                         schoben,
                         schunten,
                         laenge,
                         COALESCE(sohleoben, SO.sohlhoehe)  AS sohleoben,
                         COALESCE(sohleunten, SU.sohlhoehe) AS sohleunten,
                         hoehe
                       FROM haltungen
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SO ON haltungen.schoben = SO.schnam
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SU ON haltungen.schunten = SU.schnam
                       UNION
                       SELECT
                         wnam         AS name,
                         schoben,
                         schunten,
                         laenge,
                         SO.sohlhoehe AS sohleoben,
                         SU.sohlhoehe AS sohleunten,
                         0.5          AS hoehe
                       FROM wehre
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SO ON wehre.schoben = SO.schnam
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SU ON wehre.schunten = SU.schnam
                       UNION
                       SELECT
                         pnam        AS name,
                         schoben,
                         schunten,
                         5            AS laenge,
                         SO.sohlhoehe AS sohleoben,
                         SU.sohlhoehe AS sohleunten,
                         0.5          AS hoehe
                       FROM pumpen
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SO ON pumpen.schoben = SO.schnam
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SU ON pumpen.schunten = SU.schnam
                      )
                WHERE name="{}"
                """
        for haltung in route.get("haltungen"):
            self.__db.sql(statement.format(haltung))
            name, schachtoben, schachtunten, laenge, sohlhoeheoben, sohlhoeheunten, querschnitt = self.__db.fetchone()
            haltung_info[haltung] = {
                "schachtoben": schachtoben,
                "schachtunten": schachtunten,
                "laenge": laenge,
                "sohlhoeheoben": sohlhoeheoben,
                "sohlhoeheunten": sohlhoeheunten,
                "querschnitt": querschnitt
            }
        statement = u"""
        SELECT sohlhoehe,deckelhoehe FROM schaechte WHERE schnam="{}"
        """
        for schacht in route.get("schaechte"):
            self.__db.sql(statement.format(schacht))
            res = self.__db.fetchone()
            schacht_info[schacht] = {
                "deckelhoehe": res[1],
                "sohlhoehe": res[0]
            }
        return schacht_info, haltung_info

    @staticmethod
    def get_schaechte(schaechte):
        """
        Erswtellt ein Route-Objekt, welches einem Dictionary über alle Haltungen und Schächten getrennt voneinander
        entspricht.

        :param schaechte: Entspricht den selektierten Schacht-Namen aus QGis.
        :type schaechte: list 
        :return: Gibt ein Dictionary mit den Schacht- und Haltungs-Namen zurück.
        :rtype: dict
        """
        _route = {"schaechte": [], "haltungen": []}
        for schacht in schaechte:
            _route["schaechte"].append(schacht)
        return _route

    @staticmethod
    def get_haltungen(haltungen):
        """
        Erstellt ein Route-Objekt, welches einem Dictionary über alle Haltungen und Schächten getrennt voneinander 
        entspricht.

        :param haltungen: Entspricht den selektierten Haltungs-Namen aus QGis.
        :type haltungen: list 
        :return: Gibt ein Dictionary mit den Schacht- und Haltungs-Namen zurück.
        :rtype: dict 
        """
        _route = {"schaechte": [], "haltungen": []}
        for haltung in haltungen:
            _route["haltungen"].append(haltung)
        return _route
