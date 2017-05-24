# -*- coding: utf-8 -*-

from QKan_Database.fbfunc import FBConnection
from matplotlib import pyplot as plt
from PyQt4.QtGui import QWidget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.lines import Line2D
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext
import matplotlib.lines as lines
import matplotlib.animation as animation
from Enums import SliderMode, LayerType
import datetime
import logging

logger = logging.getLogger('QKan_Laengsschnitt')

plots = {
    "surface": None,
    "max": None,
    "water-level": None
}


class Laengsschnitt:
    def __init__(self, _route):
        """
        Constructor

        :param _route: Entspricht einem Dictionary, das bereits mit allen nötigen Informationen über alle
        selektierten Elemente verfügt.
        :type _route: dict
        """
        self.route = _route
        self.fig = plt.figure(0)
        self.ax = None
        self.x_pointer = 0
        self.minY = None
        self.maxY = None
        self.schacht_breite = 1
        self.objects = {"haltungen": {}, "schaechte": {}}

        plt.gcf().clear()

    def __del__(self):
        """
        Destruktor
        """
        del self.fig

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
        canv = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(canv, qw, True)
        margin = self.x_pointer * 0.05
        plt.axis([-margin, self.x_pointer + margin, self.minY - 1, self.maxY + 1])
        self.fig.axes[0].grid(True)
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
        for key2 in self.objects[key]:
            for plot in self.objects[key][key2]:
                color = colors.get("plots").get(key2)
                if isinstance(plot, HaltungLinie) or isinstance(plot, SchachtLinie):
                    plot.text.set_color(color)
                plot.set_color(color)
        self.fig.canvas.draw()

    def reset_colors(self):
        """
        Setzt alle Plots des Längsschnitts zurück auf Default (Schwarz).
        """
        for schacht in self.objects["schaechte"]:
            for plot in self.objects["schaechte"][schacht]:
                if isinstance(plot, SchachtLinie):
                    plot.text.set_color("k")
                plot.set_color("k")
        for haltung in self.objects["haltungen"]:
            for plot in self.objects["haltungen"][haltung]:
                if isinstance(plot, HaltungLinie):
                    plot.text.set_color("k")
                plot.set_color("k")
        self.fig.canvas.draw()

    def draw(self):
        """
        Zeichnet die Plots des Längsschnitts
        """
        self.ax = self.fig.add_subplot(111)
        switch = True

        def draw_schacht(name):
            """
            Zeichnet den Schacht in die Figure und geht dabei von einer Fixen Schachtbreite aus, welche in den 
            Attributen steht.

            :param name: Entspricht dem Namen des Schachts
            :type name:str 
            """
            schacht = self.route.get("schachtinfo").get(name)
            boden = schacht.get("sohlhoehe")
            decke = schacht.get("deckelhoehe")
            l = SchachtLinie([self.x_pointer, self.x_pointer], [boden, decke], color='k', label=name)
            l.set_schacht_width(self.schacht_breite)
            l.set_name(name)
            self.objects["schaechte"][name] = [l]
            self.ax.add_line(l)
            l = Line2D([self.x_pointer, self.x_pointer + self.schacht_breite], [boden, boden], color='k')
            self.objects["schaechte"][name].append(l)
            self.ax.add_line(l)
            self.x_pointer += self.schacht_breite
            l = Line2D([self.x_pointer, self.x_pointer], [boden, decke], color='k')
            self.objects["schaechte"][name].append(l)
            self.ax.add_line(l)
            if self.minY is None:
                self.minY = boden
                self.maxY = decke
            else:
                self.minY = boden if boden < self.minY else self.minY
                self.maxY = decke if decke > self.maxY else self.maxY

        def draw_haltung(name):
            """
            Zeichnet die Haltung und zusätzlich die Oberfläche in die Figure ein.

            :param name: Entspricht dem Namen der Haltung.
            :type name:str 
            """
            haltung = self.route.get("haltunginfo").get(name)
            laenge = haltung.get("laenge")
            oben = haltung.get("sohlhoeheoben")
            unten = haltung.get("sohlhoeheunten")
            hoehe = haltung.get("querschnitt")
            schacht_oben = haltung.get("schachtoben")
            schacht_unten = haltung.get("schachtunten")

            deckel_hoehe1 = self.route.get("schachtinfo")[schacht_oben].get("deckelhoehe")
            deckel_hoehe2 = self.route.get("schachtinfo")[schacht_unten].get("deckelhoehe")

            laenge -= self.schacht_breite
            l = HaltungLinie([self.x_pointer, self.x_pointer + laenge], [oben, unten], color='k', label=name)
            l.set_name(name)
            self.objects["haltungen"][name] = [l]
            self.ax.add_line(l)
            l = Line2D([self.x_pointer, self.x_pointer + laenge], [oben + hoehe, unten + hoehe], color='k')
            self.ax.add_line(l)
            self.objects["haltungen"][name].append(l)
            l = Line2D([self.x_pointer, self.x_pointer + laenge], [deckel_hoehe1, deckel_hoehe2], color='g',
                       label="Oberflaeche",
                       linewidth=3, linestyle=':')
            self.ax.add_line(l)
            if plots.get("surface") is None:
                plots["surface"] = l
            l = Line2D([self.x_pointer, self.x_pointer], [oben, oben + hoehe], color='w', linewidth=2, alpha=0.5,
                       zorder=4)
            self.ax.add_line(l)
            l = Line2D([self.x_pointer + laenge, self.x_pointer + laenge], [unten, unten + hoehe], color='w',
                       linewidth=2, alpha=0.5, zorder=4)
            self.ax.add_line(l)
            self.x_pointer += laenge

        while True:
            if switch:
                draw_schacht(self.route.get("schaechte").pop(0))
                if len(self.route.get("schaechte")) == 0:
                    break
            else:
                draw_haltung(self.route.get("haltungen").pop(0))
            switch = not switch


class Maximizer:
    def __init__(self, _id, _route, _dbname):
        """
        Constructor

        :param _id: Entspricht einer ID, welche pro Instanz unique ist.
        :type _id: float
        :param _route: Entspricht einem Dictionary, das bereits mit allen nötigen Informationen über alle
        selektierten Elemente verfügt.
        :type _route: dict
        :param _dbname: Entspricht dem Datenbank-Pfad der Ereignis-Datenbank
        :type _dbname: str
        """
        self.db = FBConnection(_dbname)
        self.id = _id
        self.route = _route
        self.fig = plt.figure(0)
        self.ax = None
        self.x_pointer = 0
        self.schacht_breite = 1
        self.x = []
        self.y = []
        self.plot = None
        self.simulation = self.fetch_max_simulation_data()

    def __del__(self):
        """
        Destruktor
        """
        del self.fig

    def fetch_max_simulation_data(self):
        """
        Berechnet die maximalen Wasserstände über den gesamten Zeitraum einer Simulation und gibt diese zurück.

        :return: Gibt ein Dictionary zurück, welche alle Haltungen und Schächte und deren maximale Wasserstände 
        beinhaltet.
        :rtype: dict
        """
        haltungen = {}
        schaechte = {}
        for haltung in self.route.get("haltungen"):
            statement = u'SELECT wasserstandoben,wasserstandunten FROM lau_max_el WHERE "KANTE"={}'.format(
                u"'{}'".format(haltung))
            self.db.sql(statement)
            wasserstandoben, wasserstandunten = self.db.fetchone()
            haltungen[haltung] = {"wasserstandoben": wasserstandoben, "wasserstandunten": wasserstandunten}

        for schacht in self.route.get("schaechte"):
            self.db.sql(u'SELECT wasserstand FROM lau_max_s WHERE "KNOTEN"={}'.format(u"'{}'".format(schacht)))
            wasserstand, = self.db.fetchone()
            schaechte[schacht] = wasserstand
        return {"haltungen": haltungen, "schaechte": schaechte}

    def draw(self):
        """
        Zeichnet den Plot für den maximalen Wasserstand.
        """
        self.ax = self.fig.add_subplot(111)
        switch = True

        def draw_schacht(name):
            """
            Zeichnet den maximalen Wasserstand des Schachts ein und geht dabei von einer festen Schachtbreite aus.

            :param name: Entspricht dem Namen des Schachts.
            :type name: str
            """
            wasserstand = self.simulation.get("schaechte").get(name)
            self.x += [self.x_pointer, self.x_pointer + self.schacht_breite]
            self.y += [wasserstand, wasserstand]
            self.x_pointer += self.schacht_breite

        def draw_haltung(name):
            """
            Zeichnet den maximalen Wasserstand der Haltung ein.

            :param name: Entspricht dem Namen der Haltung. 
            :type name:str 
            """
            haltung = self.route.get("haltunginfo").get(name)
            laenge = haltung.get("laenge") - self.schacht_breite
            wasseroben = self.simulation.get("haltungen").get(name).get("wasserstandoben")
            wasserunten = self.simulation.get("haltungen").get(name).get("wasserstandunten")

            self.x += [self.x_pointer, self.x_pointer + laenge]
            self.y += [wasseroben, wasserunten]
            self.x_pointer += laenge

        while True:
            if switch:
                draw_schacht(self.route.get("schaechte").pop(0))
                if len(self.route.get("schaechte")) == 0:
                    break
            else:
                draw_haltung(self.route.get("haltungen").pop(0))
            switch = not switch
        self.plot = self.ax.plot(self.x, self.y, "b--", label="Maximum", alpha=0.6)[0]
        if plots.get("max") is None:
            plots["max"] = self.plot

    def hide(self):
        """
        Versteckt den maximalen Wasserstand, indem der Alpha-Wert auf 0 gesetzt wird.
        """
        self.plot.set_alpha(0)
        self.fig.canvas.draw()

    def show(self):
        """
        Zeigt den maximalen Wasserstand. Der Alpha-Wert wird hierbei auf 0.6 gesetzt.
        """
        self.plot.set_alpha(0.6)
        self.fig.canvas.draw()


class Animator:
    def __init__(self, _id, _route, _dbname, slider, _forward, _backward):
        """
        Constructor

        :param _id: Entspricht einer ID pro Animator-Instanz. Sollte unique sein.
        :type _id: float
        :param _route: Entspricht einem Dictionary über alle Schächte und Haltungen
        :type _route: dict
        :param _dbname: Entspricht dem Datei-Pfad zur Ergebnis-Datenbank.
        :type _dbname: str
        :param slider: Entspricht einer Referenz auf den Slider innerhalb der GUI, welcher für die Animations-
        Geschwindigkeit zuständig ist.
        :type slider: Slider
        :param _forward: Entspricht einer Referenz auf den "Vorwärts"-Button innerhalb der GUI.
        :type _forward: QPushButton
        :param _backward: Entspricht einer Referenz auf den "Zurück"-Button innerhalb der GUI.
        :type _backward: QPushButton
        """
        self.db = FBConnection(_dbname)
        self.id = _id
        self.ganglinie = None
        self.route = _route
        self.fig = plt.figure(0)
        self.ax = self.fig.add_subplot(111)
        self.x_pointer = 0
        self.schacht_breite = 1
        self.x = []
        self.y = []
        self.plot, = self.ax.plot([], [], "b:", label="Wasserstand", alpha=1)
        if plots.get("water-level") is None:
            plots["water-level"] = self.plot
        self.max_value, self.simulation, self.timestamps = self.fetch_simulation_data()
        slider.setRange(0, self.max_value)
        self.slider = slider
        self.animation = None
        self.speed = 1
        self.mode = SliderMode.Forward
        self.last_index = -1
        self.time = 0
        self.last_time = None
        self.simulation_second = 60
        self.init_animation()
        self.btn_step_forward = _forward
        self.btn_step_backward = _backward
        self.update_controls()

    def __del__(self):
        """
        Destruktor
        """
        del self.fig

    def fetch_simulation_data(self):
        """
        Liest die Datenbank aus, um alle nötigen Datensätze für die Animation zu erhalten.

        :return: Gibt die Anzahl an zuzeichnenden Elementen, ein Dictionary, das die Wasserstände zu jedem Zeitpunkt 
        aller Haltungen und Schächte beinhaltet und alle Schacht-Namen in der richtigen Reihenfolge zurück.
        :rtype: (int,dict,list)
        """
        haltungen = {}
        schaechte = {}
        for haltung in self.route.get("haltungen"):
            self.db.sql(u'SELECT wasserstandoben,wasserstandunten,zeitpunkt FROM lau_gl_el WHERE "KANTE"={}'.format(
                u"'{}'".format(haltung)))
            wasserstaende = self.db.fetchall()
            for wasserstandoben, wasserstandunten, zeitpunkt in wasserstaende:
                if haltungen.get(zeitpunkt) is None:
                    haltungen[zeitpunkt] = {}
                haltungen[zeitpunkt][haltung] = {"wasserstandoben": wasserstandoben,
                                                 "wasserstandunten": wasserstandunten}

        for schacht in self.route.get("schaechte"):
            self.db.sql(u'SELECT wasserstand,zeitpunkt FROM lau_gl_s WHERE "KNOTEN"={}'.format(u"'{}'".format(schacht)))
            wasserstaende = self.db.fetchall()
            for wasserstand, zeitpunkt in wasserstaende:
                if schaechte.get(zeitpunkt) is None:
                    schaechte[zeitpunkt] = {}
                schaechte[zeitpunkt][schacht] = wasserstand
        return len(schaechte.keys()) - 1, {"haltungen": haltungen, "schaechte": schaechte}, sorted(schaechte.keys())

    def draw(self, timestamp):
        """
        Zeichnet den Wasserstand zu einem bestimmten Zeitpunkt

        :param timestamp: Entspricht dem zu zeichnenden Zeitpunkt.
        :type timestamp: datetime
        """
        self.x_pointer = 0
        self.x = []
        self.y = []
        switch = True
        haltungen = list(self.route.get("haltungen"))
        schaechte = list(self.route.get("schaechte"))

        def draw_schacht(name):
            # if name == "Auslass":  # todo
            #     return
            """
            Zeichnet den Wasserstand eines bestimmten Schachts.
            
            :param name: Entspricht dem Namen des Schachts. 
            :type name: str
            """
            wasserstand = self.simulation.get("schaechte").get(timestamp).get(name)

            self.x += [self.x_pointer, self.x_pointer + self.schacht_breite]
            self.y += [wasserstand, wasserstand]
            self.x_pointer += self.schacht_breite

        def draw_haltung(name):
            """
            Zeichnet den Wasserstand einer bestimmten Haltung.

            :param name: Entspricht dem Namen der Haltung
            :type name: str
            """
            haltung = self.route.get("haltunginfo").get(name)

            laenge = haltung.get("laenge") - self.schacht_breite
            wasseroben = self.simulation.get("haltungen").get(timestamp).get(name).get("wasserstandoben")
            wasserunten = self.simulation.get("haltungen").get(timestamp).get(name).get("wasserstandunten")

            self.x += [self.x_pointer, self.x_pointer + laenge]
            self.y += [wasseroben, wasserunten]
            self.x_pointer += laenge

        while True:
            if switch:
                draw_schacht(schaechte.pop(0))
                if len(schaechte) == 0:
                    break
            else:
                draw_haltung(haltungen.pop(0))
            switch = not switch

    def update_coordinates(self, value):
        """
        Zeichnet einen bestimmten Zeitpunkt, welcher im GUI gewählt wurde, in das Ganglinien-Tool.

        :param value: Enspricht dem Index des Zeitpunkts an dem gezeichnet werden soll
        :type value: int
        """
        if self.ganglinie is not None:
            self.ganglinie.draw_at(self.timestamps[value])
        self.draw(self.timestamps[value])

    def go_step(self, value):
        """
        Zeichnet den Zustand zu einem übergebenen Zeitpunkt

        :param value: Entspricht dem Index des Zeitpunkts, der gezeichnet werden soll
        :type value:int 
        """
        self.update_controls()
        if self.last_index == value:
            return
        self.last_index = value
        self.update_coordinates(value)
        self.update_timestamp(value)
        self.plot.set_data(self.x, self.y)
        self.fig.canvas.draw()

    def play(self, value, mode):
        """
        Startet die Animation in einer übergebenen Geschwindigkeit und Richtung.
        
        :param value: Entspricht der Geschwindigkeit von 0 bis 50
        :type value: int
        :param mode: Entspricht dem aktuellen Modus. Forwärts oder Rückwärts
        :type mode: SliderMode
        """
        speed = self.get_speed(value)
        self.speed = speed
        self.mode = mode
        self.last_time = datetime.datetime.today()
        self.animation.event_source.start()

    def get_speed(self, x):
        """
        Rechnet die übergebene Geschwindigkeit in eine Simulationsgeschwindigkeit um

        :param x: Entspricht der übergebenen Geschwindigkeit.
        :type x: int
        :return: Tatsächliche Geschwindigkeit der Simulation.
        :rtype: int
        """
        speed = x * self.simulation_second * 0.01
        return speed

    def pause(self):
        """
        Stoppt die Simulation.
        """
        try:
            self.animation.event_source.stop()
        except AttributeError:
            pass

    def get_next_timestamp(self, index, speed, mode):
        """
        Berechnet, welcher Zeitpunkt als nächstes auszugeben ist anhand der Simulationsgeschwindigkeit.

        :param index: Entspricht dem aktuellen Index
        :type index: int
        :param speed: Entspricht der tatsächlichen Simulationsgeschwindigkeit.  
        :type speed: int
        :param mode: Entspricht dem Modus. Forwärts oder Rückwärts.
        :type mode: SliderMode
        :return: Gibt den Index des Zeitpunkts zurück, welcher als nächstes auszugeben ist.
        :rtype: int
        """
        if self.last_index == -1:
            self.last_index = index
            return index
        diff = (datetime.datetime.today() - self.last_time).microseconds / 10000.
        self.time += speed * diff if diff > 0 else speed
        self.last_time = datetime.datetime.today()
        if mode == SliderMode.Forward:
            if self.last_index == self.max_value and self.time >= self.simulation_second:
                self.last_index = 0
                self.time = 0
                return self.last_index
            for i, val in reversed(list(enumerate(self.timestamps[self.last_index + 1:]))):
                diff = val - self.timestamps[self.last_index]
                if diff.seconds < self.time:
                    self.time = 0
                    self.last_index += i + 1
                    return self.last_index
            return self.last_index
        else:
            if self.last_index == 0 and self.time >= self.simulation_second:
                self.last_index = self.max_value
                self.time = 0
                return self.last_index
            for i, val in reversed(list(enumerate(self.timestamps[:self.last_index]))):
                diff = self.timestamps[self.last_index] - val
                if diff.seconds < self.time:
                    self.time = 0
                    self.last_index = i
                    return self.last_index
            return self.last_index

    def init_animation(self):
        """
        Initialisiert die Animation mit den nötigen Daten.
        """
        self.pause()
        self.last_time = datetime.datetime.today()

        def animate(i):
            tmp = self.last_index
            index = self.get_next_timestamp(i, self.speed, self.mode)
            if index != tmp:
                self.update_coordinates(index)
                self.plot.set_data(self.x, self.y)
                self.update_timestamp(index)
            self.slider.setValue(index)

        self.animation = animation.FuncAnimation(self.fig, animate, frames=self.max_value, interval=10)
        self.fig.canvas.draw()
        self.pause()

    def update_timestamp(self, value):
        """
        Updatet die Überschrift des Längsschnitts und setzt diese auf den aktuellen Zeitpunkt.

        :param value: Entspricht dem Index des aktuellen Zeitpunkts. 
        :type value: int
        """
        timestamp = self.timestamps[value]
        time = timestamp.strftime("%d.%m.%Y %H:%M:%S")[:-3]
        self.fig.suptitle("Zeitpunkt: {}".format(time), fontsize=20)

    def update_controls(self):
        """
        Disabled ggf. die jeweiligen Buttons, wenn das Ende oder der Anfang der Simulation erreicht wurde.
        """
        value = self.slider.value()
        _min = self.slider.minimum()
        _max = self.slider.maximum()
        if value == _min:
            self.btn_step_forward.setDisabled(False)
            self.btn_step_backward.setDisabled(True)
        elif value == _max:
            self.btn_step_forward.setDisabled(True)
            self.btn_step_backward.setDisabled(False)
        else:
            self.btn_step_forward.setDisabled(False)
            self.btn_step_backward.setDisabled(False)


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


def set_legend():
    """
    Setzt die Legende des Längsschnitts. Die Oberfläche wird nur einmal definiert.
    """
    legend_plots = []
    waterlevel = plots.get("water-level")
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


def reset_legend():
    """
    Löscht alle Plots aus der Figure des Längsschnitts
    """
    del plots[:]


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
        self.text = mtext.Text(0, 0, "")
        self.name = ""
        lines.Line2D.__init__(self, *args, **kwargs)
        self.text.set_text(self.get_label())

    def set_figure(self, figure):
        """
        Fügt den Text in die Figure ein.

        :param figure: Enthält die entsprechende Figure.
        :type figure: Figure
        """
        self.text.set_figure(figure)
        lines.Line2D.set_figure(self, figure)

    def set_axes(self, axes):
        """
        Setzt die übergebenen Achsen.

        :param axes: Enthält die zu setzenden Achsen.
        :type axes: Axes
        """
        self.text.set_axes(axes)
        lines.Line2D.set_axes(self, axes)

    def set_transform(self, transform):
        """
        Transformiert die Beschriftung der Linien
        
        :param transform: Entspricht der übergebenen Transformation.
        :type transform: CompositeGenericTransform
        """
        texttrans = transform + mtransforms.Affine2D().translate(2, 2)
        self.text.set_transform(texttrans)
        lines.Line2D.set_transform(self, transform)

    def set_name(self, name):
        """
        Setter von Name

        :param name: Der Name der Haltung bzw. des Schachts.
        :type name: str
        """
        self.name = name

    def draw(self, renderer):
        """
        Plotted die Linie.

        :param renderer: Entspricht einem Reder-Objekt.
        :type renderer: RenderAgg
        """
        lines.Line2D.draw(self, renderer)
        self.text.draw(renderer)

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
        :type args: (list,list)
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
        text_length = self.text.get_size()
        if len(x):
            self.text.set_position((start + (length / 2.) - (text_length / 2.), y[-1]))
        lines.Line2D.set_data(self, x, y)


class SchachtLinie(ILines):
    def __init__(self, *args, **kwargs):
        """
        Constructor

        :param args: Beinhaltet den Start- und Endwert in X- und Y-Punkte
        :type args: (list,list)
        :param kwargs: Beinhaltet Name und Farbe der Linie
        :type kwargs: dict
        """
        self.schacht_breite = 1
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
            self.text.set_position((x[-1] + (self.schacht_breite / 2.) - (self.text.get_size() / 2.), y[-1]))
        lines.Line2D.set_data(self, x, y)

    def set_schacht_width(self, width):
        """
        Setter der Schacht-Breite

        :param width: Entspricht der fixen Schacht-Breite.
        :type width: str
        """
        self.schacht_breite = width
