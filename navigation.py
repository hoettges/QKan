# -*- coding: utf-8 -*-
from QKan_Database.fbfunc import FBConnection


class Navigator:
    def __init__(self, dbname, id):
        self.db = FBConnection(dbname)
        self.id = id

    def calculate_route_haltungen(self, startpoint, endpoint=None, additional_points=None):
        self.db.sql("SELECT sohlhoeheunten FROM rohr WHERE name='{}'".format(startpoint))
        start_hoehe, = self.db.fetchone()
        self.db.sql("SELECT sohlhoeheunten FROM rohr WHERE name='{}'".format(endpoint))
        end_hoehe, = self.db.fetchone()
        if start_hoehe < end_hoehe:
            tmp = startpoint
            startpoint = endpoint
            endpoint = tmp
        haltungen = []
        schaechte = []
        next_haltung = startpoint
        while next_haltung != endpoint:
            haltungen.append(next_haltung)
            self.db.sql(
                "SELECT name FROM rohr WHERE schachtoben=(SELECT schachtunten FROM rohr WHERE name='{}')".format(
                    next_haltung))
            try:
                _next_haltungen = self.db.fetchall()
                if len(_next_haltungen) > 1:
                    if additional_points is None:
                        return False, "Zu viele Möglichkeiten. Bitte wählen Sie einen Wegpunkt auf dem kritischen Pfad!", False
                    solution = self.decide_direction(_next_haltungen, additional_points)
                    if solution:
                        next_haltung = solution
                    else:
                        return False, "Zu viele Möglichkeiten oder Pfad unerreichbar. Bitte wählen Sie einen Wegpunkt auf dem kritischen Pfad!", False
                elif len(_next_haltungen) == 0:
                    return False, "Endpunkt nicht erreichbar!", False
                else:
                    next_haltung, = _next_haltungen[0]
            except TypeError as e:
                return False, "Endpunkt nicht erreichbar!", False
        haltungen.append(endpoint)
        self.db.sql("SELECT schachtoben FROM rohr WHERE name = '{}'".format(haltungen[0]))
        schaechte.append(self.db.fetchone()[0])
        for h in haltungen:
            self.db.sql("SELECT schachtunten FROM rohr WHERE name='{}'".format(h))
            schaechte.append(self.db.fetchone()[0])
        route = {"haltungen": haltungen, "schaechte": schaechte}
        schacht_info, haltung_info = self.fetch_data(route)
        route["schachtinfo"] = schacht_info
        route["haltunginfo"] = haltung_info
        return True, route, False

    def decide_direction(self, options, additional_points):
        for x, in options:
            if x in additional_points:
                return x
            self.db.sql(
                "SELECT name FROM rohr WHERE schachtoben=(SELECT schachtunten FROM rohr WHERE name='{}')".format(
                    x))
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
                self.db.sql(
                    "SELECT name FROM rohr WHERE schachtoben=(SELECT schachtunten FROM rohr WHERE name='{}')".format(
                        next_haltung))
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
        self.db.sql("SELECT sohlhoehe FROM schacht WHERE name='{}'".format(startpoint))
        start_hoehe, = self.db.fetchone()
        self.db.sql("SELECT sohlhoehe FROM schacht WHERE name='{}'".format(endpoint))
        end_hoehe, = self.db.fetchone()
        if start_hoehe < end_hoehe:
            tmp = startpoint
            startpoint = endpoint
            endpoint = tmp
        self.db.sql("SELECT name FROM rohr WHERE schachtoben='{}'".format(startpoint))
        start_haltungen = [h[0] for h in self.db.fetchall()]
        self.db.sql("SELECT name FROM rohr WHERE schachtunten='{}'".format(endpoint))
        end_haltungen = [h[0] for h in self.db.fetchall()]
        nodes = []
        if additional_points is not None:
            for p in additional_points:
                self.db.sql("SELECT name FROM rohr WHERE schachtoben='{}'".format(p))
                nodes += [h[0] for h in self.db.fetchall()]
        possibilities = 0
        route = None
        error = ""
        _reload = False
        for start_haltung in start_haltungen:
            for end_haltung in end_haltungen:
                _res, _route, reload = self.calculate_route_haltungen(start_haltung, end_haltung,
                                                                      additional_points=nodes)
                if _res:
                    possibilities += 1
                    if possibilities > 1:
                        return False, "Zu viele Möglichkeiten. Bitte wählen Sie einen Wegpunkt auf dem kritischen Pfad!", False
                    route = _route
                else:
                    if _reload is not True:
                        _reload = reload
                    error = _route
        if route is None:
            return False, error, _reload
        schacht_info, haltung_info = self.fetch_data(route)
        route["schachtinfo"] = schacht_info
        route["haltunginfo"] = haltung_info
        return True, route, False

    def check_route_haltungen(self, nodes):
        endpoint = nodes[0]
        startpoint = nodes[0]
        self.db.sql("SELECT sohlhoeheunten FROM rohr WHERE name='{}'".format(nodes[0]))
        try:
            minValue, = self.db.fetchone()
        except TypeError:
            return False, "Falsche Datenbank übermittelt", True
        maxValue = minValue
        for n in nodes:
            self.db.sql("SELECT sohlhoeheunten FROM rohr WHERE name='{}'".format(n))
            value, = self.db.fetchone()
            if value < minValue:
                minValue = value
                endpoint = n
            elif value > maxValue:
                maxValue = value
                startpoint = n
        try:
            nodes.remove(startpoint)
            nodes.remove(endpoint)
        except:
            pass
        if len(nodes) == 0:
            nodes = None
        res, route, reload = self.calculate_route_haltungen(startpoint, endpoint, additional_points=nodes)
        if not res:
            return False, route, reload
        if nodes is not None:
            for n in nodes:
                if n not in route["haltungen"]:
                    return False, "Gegebener Pfad ist fehlerhaft!", False
        return res, route, reload

    def check_route_schaechte(self, nodes):
        endpoint = nodes[0]
        startpoint = nodes[0]
        self.db.sql("SELECT sohlhoehe FROM schacht WHERE name='{}'".format(nodes[0]))
        minValue, = self.db.fetchone()
        maxValue = minValue
        for n in nodes:
            self.db.sql("SELECT sohlhoehe FROM schacht WHERE name='{}'".format(n))
            value, = self.db.fetchone()
            if value < minValue:
                minValue = value
                endpoint = n
            elif value > maxValue:
                maxValue = value
                startpoint = n
        nodes.remove(startpoint)
        nodes.remove(endpoint)
        if len(nodes) == 0:
            nodes = None
        res, route, reload = self.calculate_route_schaechte(startpoint, endpoint, additional_points=nodes)
        if not res:
            return False, route, reload
        for n in nodes:
            if n not in route["schaechte"]:
                return False, "Gegebener Pfad ist fehlerhaft!", False
        return res, route, reload

    def fetch_data(self, route):
        haltung_info = {}
        schacht_info = {}
        for haltung in route.get("haltungen"):
            self.db.sql(
                "SELECT SCHACHTOBEN,SCHACHTUNTEN,LAENGE,SOHLHOEHEOBEN,SOHLHOEHEUNTEN,QUERSCHNITT FROM rohr WHERE name='{}'".format(
                    haltung))
            schachtoben, schachtunten, laenge, sohlhoeheoben, sohlhoeheunten, querschnitt = self.db.fetchone()
            haltung_info[haltung] = {
                "schachtoben": schachtoben,
                "schachtunten": schachtunten,
                "laenge": laenge,
                "sohlhoeheoben": sohlhoeheoben,
                "sohlhoeheunten": sohlhoeheunten,
                "querschnitt": querschnitt
            }
        for schacht in route.get("schaechte"):
            self.db.sql(
                "SELECT sohlhoehe,deckelhoehe FROM schacht WHERE name='{}'".format(
                    schacht))
            res = self.db.fetchone()
            if res is None:
                self.db.sql("SELECT sohlhoehe,gelaendehoehe FROM auslass WHERE name='{}'".format(schacht))
                res = self.db.fetchone()
                if res is None:
                    self.db.sql("SELECT sohlhoehe,gelaendehoehe FROM speicherschacht WHERE name='{}'".format(schacht))
                    res = self.db.fetchone()
                    if res is None:
                        return
            schacht_info[schacht] = {
                "deckelhoehe": res[1],
                "sohlhoehe": res[0]
            }
        return schacht_info, haltung_info

    def get_schaechte(self, schaechte):
        _route = {"schaechte": [], "haltungen": []}
        for schacht in schaechte:
            _route["schaechte"].append(schacht)
        return _route

    def get_haltungen(self, haltungen):
        _route = {"schaechte": [], "haltungen": []}
        for haltung in haltungen:
            _route["haltungen"].append(haltung)
        return _route
