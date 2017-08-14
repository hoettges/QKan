# -*- coding: utf-8 -*-

import datetime
import logging

import matplotlib.animation as animation
import matplotlib.lines as lines
import matplotlib.text as mtext
import matplotlib.transforms as mtransforms
from PyQt4.QtGui import QWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.lines import Line2D

from Enums import SliderMode, LayerType
from qkan.database.fbfunc import FBConnection

main_logger = logging.getLogger("QKan")
main_logger.info("Plotter-Modul gestartet")
plots = dict(surface=None, max=None, waterlevel=None)


class Laengsschnitt:
    def __init__(self, _route):
        """
        Constructor

        :param _route: Entspricht einem Dictionary, das bereits mit allen nötigen Informationen über alle
        selektierten Elemente verfügt.
        :type _route: dict
        """
        self.__log = logging.getLogger("QKan.plotter.Laengsschnitt")
        self.__route = _route
        self.__fig = plt.figure(0)
        self.__ax = None
        self.__x_pointer = 0
        self.__minY = None
        self.__maxY = None
        self.__schacht_breite = 1
        self.__objects = {"haltungen": {}, "schaechte": {}}
        plt.gcf().clear()
        self.__draw()

    def __del__(self):
        """
        Destruktor
        """
        del self.__fig
        self.__log.info(u"Figure wurde gelöscht")

    def get_widget(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        Gibt dabei auch das Navigations-Widget zurück, damit dieses nur einmal existiert und nicht bei
        jedem Aufruf erzeugt wird.

        :return Gibt ein das Figure-Element und das Navigations-Widget zurück
        :rtype (FigureCanvasQTAgg,NavigationToolbar2QT)
        """
        plt.figure(0)
        qw = QWidget()
        canv = FigureCanvas(self.__fig)
        toolbar = NavigationToolbar(canv, qw, True)
        margin = self.__x_pointer * 0.05
        plt.axis([-margin, self.__x_pointer + margin, self.__minY - 1, self.__maxY + 1])
        self.__fig.axes[0].grid(True)
        return canv, toolbar

    def set_colors(self, colors):
        """
        Färbt die Plots des Längsschnitts in der selben Farbe ein, wie innerhalb der Ganglinie vorgegeben ist.

        :param colors: Gibt ein Dictionary zurück mit den Haltungs-/Schacht-Namen als Key, und einer Farbe in Hex-
        Schreibweise als Value
        :type colors: dict
        """
        self.reset_colors()
        key = "schaechte" if colors.get("layer") == LayerType.Schacht else "haltungen"
        for key2 in self.__objects[key]:
            for plot in self.__objects[key][key2]:
                color = colors.get("plots").get(key2)
                if isinstance(plot, HaltungLinie) or isinstance(plot, SchachtLinie):
                    plot._text.set_color(color)
                plot.set_color(color)
        self.__log.info(u"Farben der {} wurden gesetzt".format(key))
        self.__fig.canvas.draw()

    def reset_colors(self):
        """
        Setzt alle Plots des Längsschnitts zurück auf Default (Schwarz).
        """
        for schacht in self.__objects["schaechte"]:
            for plot in self.__objects["schaechte"][schacht]:
                if isinstance(plot, SchachtLinie):
                    plot._text.set_color("k")
                plot.set_color("k")
        for haltung in self.__objects["haltungen"]:
            for plot in self.__objects["haltungen"][haltung]:
                if isinstance(plot, HaltungLinie):
                    plot._text.set_color("k")
                plot.set_color("k")
        self.__log.info(u"Schächte und Haltungen wurden schwarz eingefärbt")
        self.__fig.canvas.draw()

    def __draw(self):
        """
        Zeichnet die Plots des Längsschnitts
        """
        self.__ax = self.__fig.add_subplot(111)
        switch = True

        def draw_schacht(name):
            """
            Zeichnet den Schacht in die Figure und geht dabei von einer Fixen Schachtbreite aus, welche in den
            Attributen steht.

            :param name: Entspricht dem Namen des Schachts
            :type name:str
            """
            schacht = self.__route.get("schachtinfo").get(name)
            boden = schacht.get("sohlhoehe")
            decke = schacht.get("deckelhoehe")
            self.__log.info(u"Schacht \"{}\" wird geplottet".format(schacht))
            l = SchachtLinie([self.__x_pointer, self.__x_pointer], [boden, decke], color='k', label=name)
            l.set_schacht_width(self.__schacht_breite)
            l.set_name(name)
            self.__objects["schaechte"][name] = [l]
            self.__ax.add_line(l)
            l = Line2D([self.__x_pointer, self.__x_pointer + self.__schacht_breite], [boden, boden], color='k')
            self.__objects["schaechte"][name].append(l)
            self.__ax.add_line(l)
            self.__x_pointer += self.__schacht_breite
            self.__log.debug(u"x_pointer wurde auf {} gesetzt".format(self.__x_pointer))
            l = Line2D([self.__x_pointer, self.__x_pointer], [boden, decke], color='k')
            self.__objects["schaechte"][name].append(l)
            self.__ax.add_line(l)
            if self.__minY is None:
                self.__minY = boden
                self.__maxY = decke
            else:
                self.__minY = boden if boden < self.__minY else self.__minY
                self.__maxY = decke if decke > self.__maxY else self.__maxY

        def draw_haltung(name):
            """
            Zeichnet die Haltung und zusätzlich die Oberfläche in die Figure ein.

            :param name: Entspricht dem Namen der Haltung.
            :type name:str
            """
            haltung = self.__route.get("haltunginfo").get(name)
            self.__log.info(u"Haltung \"{}\" wird geplottet".format(name))
            laenge = haltung.get("laenge")
            oben = haltung.get("sohlhoeheoben")
            unten = haltung.get("sohlhoeheunten")
            hoehe = haltung.get("querschnitt")
            schacht_oben = haltung.get("schachtoben")
            schacht_unten = haltung.get("schachtunten")

            deckel_hoehe1 = self.__route.get("schachtinfo")[schacht_oben].get("deckelhoehe")
            deckel_hoehe2 = self.__route.get("schachtinfo")[schacht_unten].get("deckelhoehe")

            laenge -= self.__schacht_breite
            l = HaltungLinie([self.__x_pointer, self.__x_pointer + laenge], [oben, unten], color='k', label=name)
            l.set_name(name)
            self.__objects["haltungen"][name] = [l]
            self.__ax.add_line(l)
            l = Line2D([self.__x_pointer, self.__x_pointer + laenge], [oben + hoehe, unten + hoehe], color='k')
            self.__ax.add_line(l)
            self.__objects["haltungen"][name].append(l)
            l = Line2D([self.__x_pointer, self.__x_pointer + laenge], [deckel_hoehe1, deckel_hoehe2], color='g',
                       label=u"Oberfläche",
                       linewidth=3, linestyle=':')
            self.__log.info(u"Oberfläche wurde geplottet")
            self.__ax.add_line(l)
            if plots.get("surface") is None:
                plots["surface"] = l
            l = Line2D([self.__x_pointer, self.__x_pointer], [oben, oben + hoehe], color='w', linewidth=2, alpha=0.5,
                       zorder=4)
            self.__ax.add_line(l)
            l = Line2D([self.__x_pointer + laenge, self.__x_pointer + laenge], [unten, unten + hoehe], color='w',
                       linewidth=2, alpha=0.5, zorder=4)
            self.__ax.add_line(l)
            self.__x_pointer += laenge
            self.__log.debug(u"x_pointer wurde auf {} gesetzt".format(self.__x_pointer))

        while True:
            if switch:
                draw_schacht(self.__route.get("schaechte").pop(0))
                if len(self.__route.get("schaechte")) == 0:
                    break
            else:
                draw_haltung(self.__route.get("haltungen").pop(0))
            switch = not switch
        self.__log.debug("minY:\t{}\nmaxY:\t{}".format(self.__minY, self.__maxY))


class Maximizer:
    def __init__(self, _route, _dbname):
        """
        Constructor

        :param _route: Entspricht einem Dictionary, das bereits mit allen nötigen Informationen über alle
        selektierten Elemente verfügt.
        :type _route: dict
        :param _dbname: Entspricht dem Datenbank-Pfad der Ereignis-Datenbank
        :type _dbname: str
        """
        self.__log = logging.getLogger("QKan.plotter.Maximizer")
        self.__db = FBConnection(_dbname)
        self.__route = _route
        self.__fig = plt.figure(0)
        self.__ax = None
        self.__x_pointer = 0
        self.__schacht_breite = 1
        self.__x = []
        self.__y = []
        self.__plot = None
        self.__simulation = self.__fetch_max_simulation_data()
        self.__draw()

    def __del__(self):
        """
        Destruktor
        """
        del self.__fig
        self.__log.info(u"Figure wurde gelöscht")

    def __fetch_max_simulation_data(self):
        """
        Berechnet die maximalen Wasserstände über den gesamten Zeitraum einer Simulation und gibt diese zurück.

        :return: Gibt ein Dictionary zurück, welche alle Haltungen und Schächte und deren maximale Wasserstände
        beinhaltet.
        :rtype: dict
        """
        haltungen = {}
        schaechte = {}
        for haltung in self.__route.get("haltungen"):
            statement = u'SELECT wasserstandoben,wasserstandunten FROM lau_max_el WHERE "KANTE"={}'.format(
                u"'{}'".format(haltung))
            self.__db.sql(statement)
            wasserstandoben, wasserstandunten = self.__db.fetchone()
            haltungen[haltung] = dict(wasserstandoben=wasserstandoben, wasserstandunten=wasserstandunten)

        self.__log.info(u"Maximalwerte der Haltungen wurden abgefragt")
        for schacht in self.__route.get("schaechte"):
            self.__db.sql(u'SELECT wasserstand FROM lau_max_s WHERE "KNOTEN"={}'.format(u"'{}'".format(schacht)))
            wasserstand, = self.__db.fetchone()
            schaechte[schacht] = wasserstand
        self.__log.info(u"Maximalwerte der Schächte wurden abgefragt")
        return dict(haltungen=haltungen, schaechte=schaechte)

    def __draw(self):
        """
        Zeichnet den Plot für den maximalen Wasserstand.
        """
        self.__ax = self.__fig.add_subplot(111)
        switch = True

        def draw_schacht(name):
            """
            Zeichnet den maximalen Wasserstand des Schachts ein und geht dabei von einer festen Schachtbreite aus.

            :param name: Entspricht dem Namen des Schachts.
            :type name: str
            """
            wasserstand = self.__simulation.get("schaechte").get(name)
            self.__x += [self.__x_pointer, self.__x_pointer + self.__schacht_breite]
            self.__y += [wasserstand, wasserstand]
            self.__x_pointer += self.__schacht_breite

        def draw_haltung(name):
            """
            Zeichnet den maximalen Wasserstand der Haltung ein.

            :param name: Entspricht dem Namen der Haltung.
            :type name:str
            """
            haltung = self.__route.get("haltunginfo").get(name)
            laenge = haltung.get("laenge") - self.__schacht_breite
            wasseroben = self.__simulation.get("haltungen").get(name).get("wasserstandoben")
            wasserunten = self.__simulation.get("haltungen").get(name).get("wasserstandunten")

            self.__x += [self.__x_pointer, self.__x_pointer + laenge]
            self.__y += [wasseroben, wasserunten]
            self.__x_pointer += laenge

        while True:
            if switch:
                draw_schacht(self.__route.get("schaechte").pop(0))
                if len(self.__route.get("schaechte")) == 0:
                    break
            else:
                draw_haltung(self.__route.get("haltungen").pop(0))
            switch = not switch
        self.__log.debug(u"Y-Werte:\t{}\nX-Werte:\t{}".format(self.__y, self.__x))
        self.__plot, = self.__ax.plot(self.__x, self.__y, "b--", label="Maximum", alpha=0.6)
        self.__log.info(u"Maximal-Linie wurde geplottet")
        if plots.get("max") is None:
            plots["max"] = self.__plot
        self.__log.info(u"Maximal-Linie wurde gesetzt")

    def hide(self):
        """
        Versteckt den maximalen Wasserstand, indem der Alpha-Wert auf 0 gesetzt wird.
        """
        self.__plot.set_alpha(0)
        self.__fig.canvas.draw()
        self.__log.info(u"Alpha-Wert der Maximal-Linie wurde auf 0 gesetzt")

    def show(self):
        """
        Zeigt den maximalen Wasserstand. Der Alpha-Wert wird hierbei auf 0.6 gesetzt.
        """
        self.__plot.set_alpha(0.6)
        self.__fig.canvas.draw()
        self.__log.info(u"Alpha-Wert der Maximal-Linie wurde auf 0.6 gesetzt")


class Animator:
    def __init__(self, _route, _dbname, slider, _forward, _backward, _label):
        """
        Constructor

        :param _route: Entspricht einem Dictionary über alle Schächte und Haltungen
        :type _route: dict
        :param _dbname: Entspricht dem Datei-Pfad zur Ergebnis-Datenbank.
        :type _dbname: str
        :param slider: Entspricht einer Referenz auf den Slider innerhalb der GUI, welcher für die Animations-
        Geschwindigkeit zuständig ist.
        :type slider: QSlider
        :param _forward: Entspricht einer Referenz auf den "Vorwärts"-Button innerhalb der GUI.
        :type _forward: QPushButton
        :param _backward: Entspricht einer Referenz auf den "Zurück"-Button innerhalb der GUI.
        :type _backward: QPushButton
        """
        self.__log = logging.getLogger("QKan.plotter.Animator")
        self.__db = FBConnection(_dbname)
        self.__label = _label
        self.__ganglinie = None
        self.__route = _route
        self.__fig = plt.figure(0)
        self.__ax = self.__fig.add_subplot(111)
        self.__x_pointer = 0
        self.__schacht_breite = 1
        self.__x = []
        self.__y = []
        self.__plot, = self.__ax.plot([], [], "b:", label="Wasserstand", alpha=1)
        if plots.get("waterlevel") is None:
            plots["waterlevel"] = self.__plot
        self.__max_value, self.__simulation, self.__timestamps = self.__fetch_simulation_data()
        slider.setRange(0, self.__max_value)
        self.__slider = slider
        self.__animation = None
        self.__speed = 1
        self.__mode = SliderMode.Forward
        self.__last_index = -1
        self.__time = 0
        self.__last_time = None
        self.__simulation_second = 60
        self.__init_animation()
        self.__btn_step_forward = _forward
        self.__btn_step_backward = _backward
        self.__update_controls()

    def set_ganglinie(self, ganglinie):
        """
        Setter der Ganglinie

        :param ganglinie: Entspricht der Ganglinie des Längsschnitts
        :type ganglinie:Ganglinie
        """
        self.__ganglinie = ganglinie
        self.__log.info(u"Ganglinie wurde dem Längsschnitt zugewiesen")

    def get_timestamps(self):
        """
        Getter der Timestamps
        """
        return self.__timestamps

    def get_last_index(self):
        """
        Getter des letzten Index
        """
        return self.__last_index

    def __del__(self):
        """
        Destruktor
        """
        del self.__fig
        self.__log.info(u"Figure wurde gelöscht")

    def __fetch_simulation_data(self):
        """
        Liest die Datenbank aus, um alle nötigen Datensätze für die Animation zu erhalten.

        :return: Gibt die Anzahl an zuzeichnenden Elementen, ein Dictionary, das die Wasserstände zu jedem Zeitpunkt
        aller Haltungen und Schächte beinhaltet und alle Schacht-Namen in der richtigen Reihenfolge zurück.
        :rtype: (int,dict,list)
        """
        haltungen = {}
        schaechte = {}
        for haltung in self.__route.get("haltungen"):
            self.__db.sql(u'SELECT wasserstandoben,wasserstandunten,zeitpunkt FROM lau_gl_el WHERE "KANTE"={}'.format(
                u"'{}'".format(haltung)))
            wasserstaende = self.__db.fetchall()
            for wasserstandoben, wasserstandunten, zeitpunkt in wasserstaende:
                if haltungen.get(zeitpunkt) is None:
                    haltungen[zeitpunkt] = {}
                haltungen[zeitpunkt][haltung] = dict(wasserstandoben=wasserstandoben, wasserstandunten=wasserstandunten)

        self.__log.info(u"Wasserstände und Zeitpunkte der Haltungen wurden abgefragt")
        for schacht in self.__route.get("schaechte"):
            self.__db.sql(
                u'SELECT wasserstand,zeitpunkt FROM lau_gl_s WHERE "KNOTEN"={}'.format(u"'{}'".format(schacht)))
            wasserstaende = self.__db.fetchall()
            for wasserstand, zeitpunkt in wasserstaende:
                if schaechte.get(zeitpunkt) is None:
                    schaechte[zeitpunkt] = {}
                schaechte[zeitpunkt][schacht] = wasserstand
        self.__log.info(u"Wasserstände und Zeitpunkte der Schächte wurden abgefragt")
        return len(schaechte.keys()) - 1, dict(haltungen=haltungen, schaechte=schaechte), sorted(schaechte.keys())

    def draw(self, timestamp):
        """
        Sammelt alle X- und Y-Werte für den jeweiligen Zeitpunkt

        :param timestamp: Entspricht dem zu zeichnenden Zeitpunkt.
        :type timestamp: datetime
        """
        self.__x_pointer = 0
        self.__x = []
        self.__y = []
        switch = True
        haltungen = list(self.__route.get("haltungen"))
        schaechte = list(self.__route.get("schaechte"))

        def draw_schacht(name):
            #         if name == "Auslass":  # todo
            #             return
            """
            Fragt die X- und Y-Werte der Schächte für den Zeitpunkt ab.

            :param name: Entspricht dem Namen des Schachts.
            :type name: str
            """
            wasserstand = self.__simulation.get("schaechte").get(timestamp).get(name)

            self.__x += [self.__x_pointer, self.__x_pointer + self.__schacht_breite]
            self.__y += [wasserstand, wasserstand]
            self.__x_pointer += self.__schacht_breite

        def draw_haltung(name):
            """
            Fragt die X- und Y-Werte der Haltungen für den Zeitpunkt ab.

            :param name: Entspricht dem Namen der Haltung
            :type name: str
            """
            haltung = self.__route.get("haltunginfo").get(name)

            laenge = haltung.get("laenge") - self.__schacht_breite
            wasseroben = self.__simulation.get("haltungen").get(timestamp).get(name).get("wasserstandoben")
            wasserunten = self.__simulation.get("haltungen").get(timestamp).get(name).get("wasserstandunten")
            self.__x += [self.__x_pointer, self.__x_pointer + laenge]
            self.__y += [wasseroben, wasserunten]
            self.__x_pointer += laenge

        while True:
            if switch:
                draw_schacht(schaechte.pop(0))
                if len(schaechte) == 0:
                    break
            else:
                draw_haltung(haltungen.pop(0))
            switch = not switch

    def __update_coordinates(self, value):
        """
        Zeichnet einen bestimmten Zeitpunkt, welcher im GUI gewählt wurde, in das Ganglinien-Tool.

        :param value: Enspricht dem Index des Zeitpunkts an dem gezeichnet werden soll
        :type value: int
        """
        if self.__ganglinie is not None:
            self.__ganglinie.draw_at(self.__timestamps[value])
        self.draw(self.__timestamps[value])

    def go_step(self, value):
        """
        Zeichnet den Zustand zu einem übergebenen Zeitpunkt

        :param value: Entspricht dem Index des Zeitpunkts, der gezeichnet werden soll
        :type value:int
        """
        self.__update_controls()
        if self.__last_index == value:
            return
        self.__last_index = value
        self.__update_coordinates(value)
        self.__update_timestamp(value)
        self.__plot.set_data(self.__x, self.__y)
        self.__fig.canvas.draw()

    def play(self, value, mode):
        """
        Startet die Animation in einer übergebenen Geschwindigkeit und Richtung.

        :param value: Entspricht der Geschwindigkeit von 0 bis 50
        :type value: int
        :param mode: Entspricht dem aktuellen Modus. Vorwärts oder Rückwärts
        :type mode: SliderMode
        """
        speed = self.__get_speed(value)
        self.__log.info(u"Animation wurde mit Geschwindigkeit = {} gestartet".format(value))
        self.__speed = speed
        self.__mode = mode
        self.__log.debug(u"Modus:\t{}".format(u"Vorwärts" if mode == SliderMode.Forward else u"Rückwärts"))
        self.__last_time = datetime.datetime.today()
        self.__animation.event_source.start()
        self.__log.info(u"Animation wird fortgesetzt")

    def __get_speed(self, x):
        """
        Rechnet die übergebene Geschwindigkeit in eine Simulationsgeschwindigkeit um

        :param x: Entspricht der übergebenen Geschwindigkeit.
        :type x: int
        :return: Tatsächliche Geschwindigkeit der Simulation.
        :rtype: int
        """
        speed = x * self.__simulation_second * 0.01
        self.__log.debug(u"Animationsgeschwindigkeit:\t{}".format(speed))
        return speed

    def pause(self):
        """
        Stoppt die Simulation.
        """
        try:
            self.__animation.event_source.stop()
        except AttributeError:
            pass
        self.__log.info(u"Animation wurde pausiert")

    def __get_next_timestamp(self, index, speed, mode):
        """
        Berechnet, welcher Zeitpunkt als nächstes auszugeben ist anhand der Simulationsgeschwindigkeit.

        :param index: Entspricht dem aktuellen Index
        :type index: int
        :param speed: Entspricht der tatsächlichen Simulationsgeschwindigkeit.
        :type speed: int
        :param mode: Entspricht dem Modus. Vorwärts oder Rückwärts.
        :type mode: SliderMode
        :return: Gibt den Index des Zeitpunkts zurück, welcher als nächstes auszugeben ist.
        :rtype: int
        """
        if self.__last_index == -1:
            self.__last_index = index
            return index
        diff = (datetime.datetime.today() - self.__last_time).microseconds / 10000.
        self.__time += speed * diff if diff > 0 else speed
        self.__last_time = datetime.datetime.today()
        if mode == SliderMode.Forward:
            if self.__last_index == self.__max_value and self.__time >= self.__simulation_second:
                self.__last_index = 0
                self.__time = 0
                return self.__last_index
            for i, val in reversed(list(enumerate(self.__timestamps[self.__last_index + 1:]))):
                diff = val - self.__timestamps[self.__last_index]
                if diff.seconds < self.__time:
                    self.__time = 0
                    self.__last_index += i + 1
                    return self.__last_index
        else:
            if self.__last_index == 0 and self.__time >= self.__simulation_second:
                self.__last_index = self.__max_value
                self.__time = 0
                return self.__last_index
            for i, val in reversed(list(enumerate(self.__timestamps[:self.__last_index]))):
                diff = self.__timestamps[self.__last_index] - val
                if diff.seconds < self.__time:
                    self.__time = 0
                    self.__last_index = i
                    return self.__last_index
        return self.__last_index

    def __init_animation(self):
        """
        Initialisiert die Animation mit den nötigen Daten.
        """
        self.pause()
        self.__last_time = datetime.datetime.today()

        def animate(i):
            tmp = self.__last_index
            index = self.__get_next_timestamp(i, self.__speed, self.__mode)
            if index != tmp:
                self.__update_coordinates(index)
                self.__plot.set_data(self.__x, self.__y)
                self.__update_timestamp(index)
                self.__slider.setValue(index)

        self.__animation = animation.FuncAnimation(self.__fig, animate, frames=self.__max_value, interval=200)
        self.pause()
        self.__log.info(u"Animation wurde initialisiert und pausiert")

    def __update_timestamp(self, value):
        """
        Updatet die Überschrift des Längsschnitts und setzt diese auf den aktuellen Zeitpunkt.

        :param value: Entspricht dem Index des aktuellen Zeitpunkts.
        :type value: int
        """
        timestamp = self.__timestamps[value]
        time = timestamp.strftime("%d.%m.%Y %H:%M:%S")[:-3]
        self.__label.setText(time)

    def __update_controls(self):
        """
        Disabled ggf. die jeweiligen Buttons, wenn das Ende oder der Anfang der Simulation erreicht wurde.
        """
        value = self.__slider.value()
        _min = self.__slider.minimum()
        _max = self.__slider.maximum()
        if value == _min:
            self.__btn_step_forward.setDisabled(False)
            self.__btn_step_backward.setDisabled(True)
            self.__log.info("step_backward wurde disabled")
        elif value == _max:
            self.__btn_step_forward.setDisabled(True)
            self.__log.info("step_forward wurde disabled")
            self.__btn_step_backward.setDisabled(False)
        else:
            self.__btn_step_forward.setDisabled(False)
            self.__btn_step_backward.setDisabled(False)


def set_ax_labels(x, y):
    """
    Setzt die Achsenbeschriftung.

    :param x: Entspricht der X-Achsen-Beschriftung
    :type x: str
    :param y: Entspricht der Y-Achsen-Beschriftung
    :type y: str
    """
    plt.figure(0)
    plt.xlabel(x)
    plt.ylabel(y)
    main_logger.info(u"Plot-Achsen wurden beschriftet")
    main_logger.debug(u"X:\t{}\nY:\t{}".format(x, y))


def set_legend():
    """
    Setzt die Legende des Längsschnitts. Die Oberfläche wird nur einmal definiert.
    """
    legend_plots = []
    waterlevel = plots.get("waterlevel")
    surface = plots.get("surface")
    _max = plots.get("max")
    if waterlevel is not None:
        legend_plots.append(waterlevel)
    if surface is not None:
        legend_plots.append(surface)
    if _max is not None:
        legend_plots.append(_max)
    plt.figure(0)
    plt.legend(handles=legend_plots)
    main_logger.info(u"Legende wurde gesetzt")


def reset_legend():
    """
    Löscht alle Plots aus der Figure des Längsschnitts
    """
    del plots[:]
    main_logger.info(u"Alle Plots aus der Figure gelöscht")


class ILines(lines.Line2D):
    def remove(self):
        pass

    def __init__(self, *args, **kwargs):
        """
        Constructor

        :param args: Beinhaltet den Start- und Endwert in X- und Y-Punkte
        :type args: (list,list)
        :param kwargs: Beinhaltet Name und Farbe der Linie
        :type kwargs: dict
        """
        self._text = mtext.Text(0, 0, "")
        self._name = ""
        lines.Line2D.__init__(self, *args, **kwargs)
        self._text.set_text(self.get_label())

    def set_figure(self, figure):
        """
        Fügt den Text in die Figure ein.

        :param figure: Enthält die entsprechende Figure.
        :type figure: Figure
        """
        self._text.set_figure(figure)
        lines.Line2D.set_figure(self, figure)

    def set_axes(self, axes):
        """
        Setzt die übergebenen Achsen.

        :param axes: Enthält die zu setzenden Achsen.
        :type axes: Axes
        """
        self._text.set_axes(axes)
        lines.Line2D.set_axes(self, axes)

    def set_transform(self, transform):
        """
        Transformiert die Beschriftung der Linien

        :param transform: Entspricht der übergebenen Transformation.
        :type transform: CompositeGenericTransform
        """
        texttrans = transform + mtransforms.Affine2D().translate(2, 2)
        self._text.set_transform(texttrans)
        lines.Line2D.set_transform(self, transform)

    def set_name(self, name):
        """
        Setter von Name

        :param name: Der Name der Haltung bzw. des Schachts.
        :type name: str
        """
        self._name = name

    def draw(self, renderer):
        """
        Plotted die Linie.

        :param renderer: Entspricht einem Reder-Objekt.
        :type renderer: RenderAgg
        """
        lines.Line2D.draw(self, renderer)
        self._text.draw(renderer)

    def set_data(self, x, y):
        """
        Wird von der erbenden Klasse überschrieben und setzt den Start und Endpunkt der Linie.

        :param x: Entspricht den X-Werten des Start- und Endpunkts.
        :type x: list
        :param y: Entspricht den Y-Werten des Start- und Endpunkts.
        :type y: list
        """
        pass


class HaltungLinie(ILines):
    def __init__(self, *args, **kwargs):
        """
        Constructor

        :param args: Beinhaltet den Start- und Endwert in X- und Y-Punkte
        :type args: list,list
        :param kwargs: Beinhaltet Name und Farbe der Linie
        :type kwargs: dict
        """
        super(HaltungLinie, self).__init__(*args, **kwargs)

    def set_data(self, x, y):
        """
        Wird von der Basis-Klasse überschrieben und setzt den Start und Endpunkt der Linie. Als auch die Position des 
        Textes.

        :param x: Entspricht den X-Werten des Start- und Endpunkts.
        :type x: list
        :param y: Entspricht den Y-Werten des Start- und Endpunkts.
        :type y: list
        """
        start = x[0]
        length = x[1] - x[0]
        text_length = self._text.get_size()
        if len(x):
            self._text.set_position((start + (length / 2.) - (text_length / 2.), y[-1]))
        lines.Line2D.set_data(self, x, y)


class SchachtLinie(ILines):
    def __init__(self, *args, **kwargs):
        """
        Constructor

        :param args: Beinhaltet den Start- und Endwert in X- und Y-Punkte
        :type args: list,list
        :param kwargs: Beinhaltet Name und Farbe der Linie
        :type kwargs: dict
        """
        self.__schacht_breite = 1
        super(SchachtLinie, self).__init__(*args, **kwargs)

    def set_data(self, x, y):
        """
        Wird von der Basis-Klasse überschrieben und setzt den Start und Endpunkt der Linie. Als auch die Position des 
        Textes.

        :param x: Entspricht den X-Werten des Start- und Endpunkts.
        :type x: list
        :param y: Entspricht den Y-Werten des Start- und Endpunkts.
        :type y: list
        """
        if len(x):
            self._text.set_position((x[-1] + (self.__schacht_breite / 2.) - (self._text.get_size() / 2.), y[-1]))
        lines.Line2D.set_data(self, x, y)

    def set_schacht_width(self, width):
        """
        Setter der Schacht-Breite

        :param width: Entspricht der fixen Schacht-Breite.
        :type width: int
        """
        self.__schacht_breite = width
