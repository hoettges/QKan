# -*- coding: utf-8 -*-
from QKan_Database.dbfunc import DBConnection


class Navigator:
    def __init__(self, db, _id):
        self.id = _id
        self.db = DBConnection(db)

    def calculate_route_haltungen(self, startpoint, endpoint=None, additional_points=None):
        statement = u"""
                SELECT sohleunten FROM (SELECT
                         haltnam                            AS name,
                         schunten,
                         COALESCE(sohleunten, SU.sohlhoehe) AS sohleunten
                       FROM haltungen
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SU ON haltungen.schunten = SU.schnam
                       UNION
                       SELECT
                         wnam         AS name,
                         schunten,
                         SU.sohlhoehe AS sohleunten
                       FROM wehre
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SU ON wehre.schunten = SU.schnam
                       UNION
                       SELECT
                         pnam         AS name,
                         schunten,
                         SU.sohlhoehe AS sohleunten
                       FROM pumpen
                         LEFT JOIN
                         (SELECT
                            sohlhoehe,
                            schnam
                          FROM schaechte) AS SU ON pumpen.schunten = SU.schnam
                      )
                WHERE name="{}"
                """
        self.db.sql(statement.format(startpoint))
        start_hoehe = self.db.fetchone()
        self.db.sql(statement.format(endpoint))
        end_hoehe = self.db.fetchone()
        if start_hoehe < end_hoehe:
            tmp = startpoint
            startpoint = endpoint
            endpoint = tmp
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
            self.db.sql(statement.format(next_haltung))
            try:
                _next_haltungen = [t[0] for t in self.db.fetchall()]
                if endpoint in _next_haltungen:
                    break
                if len(_next_haltungen) > 1:
                    if additional_points is None:
                        return False, "Zu viele Möglichkeiten. Bitte wählen Sie einen Wegpunkt auf dem" \
                                      " kritischen Pfad!", False
                    solution = self.decide_direction(_next_haltungen, additional_points)
                    if solution:
                        next_haltung = solution
                    else:
                        return False, "Zu viele Möglichkeiten oder Pfad unerreichbar. Bitte wählen Sie einen Wegpunkt" \
                                      " auf dem kritischen Pfad!", False
                elif len(_next_haltungen) == 0:
                    return False, "Endpunkt nicht erreichbar!", False
                else:
                    next_haltung = _next_haltungen[0]
            except TypeError as e:
                return False, "Endpunkt nicht erreichbar!", False
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
        route = {"haltungen": haltungen, "schaechte": schaechte}
        schacht_info, haltung_info = self.fetch_data(route)
        route["schachtinfo"] = schacht_info
        route["haltunginfo"] = haltung_info
        return True, route, False

    def decide_direction(self, options, additional_points):
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
        for x in options:
            if x in additional_points:
                return x
            # self.db.sql(
            #     "SELECT name FROM rohr WHERE schachtoben=(SELECT schachtunten FROM rohr WHERE name='{}')".format(
            #         x))
            self.db.sql(statement.format(x))
            _next_haltungen = self.db.fetchall()
            if len(_next_haltungen) > 1:
                solution = self.decide_direction(_next_haltungen, additional_points)
                if solution:
                    next_haltung = solution
                else:
                    break
            elif len(_next_haltungen) == 0:
                break
            else:
                next_haltung, = _next_haltungen[0]
            while next_haltung not in additional_points:
                # self.db.sql(
                #     "SELECT name FROM rohr WHERE schachtoben=(SELECT schachtunten FROM rohr WHERE name='{}')".format(
                #         next_haltung))
                self.db.sql(statement.format(next_haltung))
                _next_haltungen = self.db.fetchall()
                if len(_next_haltungen) > 1:
                    solution = self.decide_direction(_next_haltungen, additional_points)
                    if solution:
                        next_haltung = solution
                    else:
                        break
                elif len(_next_haltungen) == 0:
                    break
                else:
                    next_haltung, = _next_haltungen[0]
            if next_haltung in additional_points:
                return x
        return False

    def calculate_route_schaechte(self, startpoint, endpoint, additional_points=None):
        statement = u"""
        SELECT sohlhoehe FROM schaechte WHERE schnam="{}"
        """
        self.db.sql(statement.format(startpoint))
        start_hoehe, = self.db.fetchone()
        self.db.sql(statement.format(endpoint))
        end_hoehe, = self.db.fetchone()
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
        self.db.sql(statement.format(startpoint))
        start_haltungen = [h[0] for h in self.db.fetchall()]
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
        nodes = []
        if additional_points is not None:
            for p in additional_points:
                self.db.sql(statement.format(p))
                nodes += [h[0] for h in self.db.fetchall()]
        possibilities = 0
        route = None
        error = ""
        _reload = False
        for start_haltung in start_haltungen:
            for end_haltung in end_haltungen:
                _res, _route, must_reload = self.calculate_route_haltungen(start_haltung, end_haltung,
                                                                           additional_points=nodes)
                if _res:
                    possibilities += 1
                    if possibilities > 1:
                        return False, "Zu viele Möglichkeiten. Bitte wählen Sie einen Wegpunkt auf" \
                                      " dem kritischen Pfad!", False
                    route = _route
                else:
                    if _reload is not True:
                        _reload = must_reload
                    error = _route
        if route is None:
            return False, error, _reload
        schacht_info, haltung_info = self.fetch_data(route)
        route["schachtinfo"] = schacht_info
        route["haltunginfo"] = haltung_info
        return True, route, False

    def check_route_haltungen(self, nodes):
        statement = u"""
        SELECT sohleunten FROM (SELECT
                 haltnam                            AS name,
                 schunten,
                 COALESCE(sohleunten, SU.sohlhoehe) AS sohleunten
               FROM haltungen
                 LEFT JOIN
                 (SELECT
                    sohlhoehe,
                    schnam
                  FROM schaechte) AS SU ON haltungen.schunten = SU.schnam
               UNION
               SELECT
                 wnam         AS name,
                 schunten,
                 SU.sohlhoehe AS sohleunten
               FROM wehre
                 LEFT JOIN
                 (SELECT
                    sohlhoehe,
                    schnam
                  FROM schaechte) AS SU ON wehre.schunten = SU.schnam
               UNION
               SELECT
                 pnam        AS name,
                 schunten,
                 SU.sohlhoehe AS sohleunten
               FROM pumpen
                 LEFT JOIN
                 (SELECT
                    sohlhoehe,
                    schnam
                  FROM schaechte) AS SU ON pumpen.schunten = SU.schnam
              )
        WHERE name="{}"
        """
        self.db.sql(statement.format(nodes[0]))
        startpoint = nodes[0]
        endpoint = nodes[0]
        try:
            min_value, = self.db.fetchone()
        except TypeError:
            return False, "Falsche Datenbank übermittelt", True
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
        try:
            nodes.remove(startpoint)
            nodes.remove(endpoint)
        except Exception as e:
            print(e)
            raise  # pass
        if len(nodes) == 0:
            nodes = None
        res, route, _reload = self.calculate_route_haltungen(startpoint, endpoint, additional_points=nodes)
        if not res:
            return False, route, _reload
        if nodes is not None:
            for n in nodes:
                if n not in route["haltungen"]:
                    return False, "Gegebener Pfad ist fehlerhaft!", False
        return res, route, _reload

    def check_route_schaechte(self, nodes):
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
        nodes.remove(startpoint)
        nodes.remove(endpoint)
        if len(nodes) == 0:
            nodes = None
        res, route, _reload = self.calculate_route_schaechte(startpoint, endpoint, additional_points=nodes)
        if not res:
            return False, route, _reload
        for n in nodes:
            if n not in route["schaechte"]:
                return False, "Gegebener Pfad ist fehlerhaft!", False
        return res, route, _reload

    def fetch_data(self, route):
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
            self.db.sql(statement.format(haltung))
            name, schachtoben, schachtunten, laenge, sohlhoeheoben, sohlhoeheunten, querschnitt = self.db.fetchone()
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
            self.db.sql(statement.format(schacht))
            res = self.db.fetchone()
            schacht_info[schacht] = {
                "deckelhoehe": res[1],
                "sohlhoehe": res[0]
            }
        return schacht_info, haltung_info

    @staticmethod
    def get_schaechte(schaechte):
        _route = {"schaechte": [], "haltungen": []}
        for schacht in schaechte:
            _route["schaechte"].append(schacht)
        return _route

    @staticmethod
    def get_haltungen(haltungen):
        _route = {"schaechte": [], "haltungen": []}
        for haltung in haltungen:
            _route["haltungen"].append(haltung)
        return _route
