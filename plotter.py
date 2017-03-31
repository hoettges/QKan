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
        self.route = _route
        self.fig = plt.figure(1)
        self.ax = None
        self.x_pointer = 0
        self.minY = None
        self.maxY = None
        self.schacht_breite = 1
        self.objects = {"haltungen": {}, "schaechte": {}}

        plt.gcf().clear()

    def __del__(self):
        del self.fig

    def get_widget(self):
        plt.figure(1)
        qw = QWidget()
        canv = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(canv, qw, True)
        margin = self.x_pointer * 0.05
        plt.axis([-margin, self.x_pointer + margin, self.minY - 1, self.maxY + 1])
        self.fig.axes[0].grid(True)
        return canv, toolbar

    def set_colors(self, colors):
        self.reset_colors()
        key = "schaechte" if colors.get("layer") == LayerType.Schacht else "haltungen"
        for key2 in self.objects[key]:
            for plot in self.objects[key][key2]:
                if isinstance(plot, HaltungLine) or isinstance(plot, SchachtLinie):
                    plot.text.set_color(colors.get("plots").get(key2))
                plot.set_color(colors.get("plots").get(key2))
        self.fig.canvas.draw()

    def reset_colors(self):
        for schacht in self.objects["schaechte"]:
            for plot in self.objects["schaechte"][schacht]:
                if isinstance(plot, SchachtLinie):
                    plot.text.set_color("k")
                plot.set_color("k")
        for haltung in self.objects["haltungen"]:
            for plot in self.objects["haltungen"][haltung]:
                if isinstance(plot, HaltungLine):
                    plot.text.set_color("k")
                plot.set_color("k")
        self.fig.canvas.draw()

    def draw(self):
        self.ax = self.fig.add_subplot(111)
        switch = True

        def draw_schacht(name):
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
            haltung = self.route.get("haltunginfo").get(name)
            laenge = haltung.get("laenge")
            oben = haltung.get("sohlhoeheoben")
            unten = haltung.get("sohlhoeheunten")
            hoehe = haltung.get("querschnitt")
            schachtO = haltung.get("schachtoben")
            schachtU = haltung.get("schachtunten")

            deckel_hoehe1 = self.route.get("schachtinfo")[schachtO].get("deckelhoehe")
            deckel_hoehe2 = self.route.get("schachtinfo")[schachtU].get("deckelhoehe")

            if deckel_hoehe2 > deckel_hoehe1:
                tmp = deckel_hoehe1
                deckel_hoehe1 = deckel_hoehe2
                deckel_hoehe2 = tmp

            laenge -= self.schacht_breite
            l = HaltungLine([self.x_pointer, self.x_pointer + laenge], [oben, unten], color='k', label=name)
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
        self.db = FBConnection(_dbname)
        self.id = _id
        self.route = _route
        self.fig = plt.figure(1)
        self.ax = None
        self.x_pointer = 0
        self.schacht_breite = 1
        self.x = []
        self.y = []
        self.plot = None
        self.simulation = self.fetch_max_simulation_data()

    def __del__(self):
        del self.fig

    def fetch_max_simulation_data(self):
        haltungen = {}
        schaechte = {}
        for haltung in self.route.get("haltungen"):
            self.db.sql("SELECT wasserstandoben,wasserstandunten FROM lau_max_el WHERE kante='{}'".format(haltung))
            wasserstandoben, wasserstandunten = self.db.fetchone()
            haltungen[haltung] = {"wasserstandoben": wasserstandoben, "wasserstandunten": wasserstandunten}

        for schacht in self.route.get("schaechte"):
            self.db.sql("SELECT wasserstand FROM lau_max_s WHERE knoten='{}'".format(schacht))
            wasserstand, = self.db.fetchone()
            schaechte[schacht] = wasserstand
        return {"haltungen": haltungen, "schaechte": schaechte}

    def draw(self):
        self.ax = self.fig.add_subplot(111)
        switch = True

        def draw_schacht(name):
            wasserstand = self.simulation.get("schaechte").get(name)
            self.x += [self.x_pointer, self.x_pointer + self.schacht_breite]
            self.y += [wasserstand, wasserstand]
            self.x_pointer += self.schacht_breite

        def draw_haltung(name):
            haltung = self.route.get("haltunginfo").get(name)
            laenge = haltung.get("laenge")
            laenge -= self.schacht_breite
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
        self.plot.set_alpha(0)
        self.fig.canvas.draw()

    def show(self):
        self.plot.set_alpha(0.6)
        self.fig.canvas.draw()


class Animator:
    def __init__(self, _id, _route, _dbname, slider, _forward, _backward):
        self.db = FBConnection(_dbname)
        self.id = _id
        self.ganglinie = None
        self.route = _route
        self.fig = plt.figure(1)
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
        del self.fig

    def fetch_simulation_data(self):
        haltungen = {}
        schaechte = {}
        for haltung in self.route.get("haltungen"):
            self.db.sql(
                "SELECT wasserstandoben,wasserstandunten,zeitpunkt FROM lau_gl_el WHERE kante='{}'".format(haltung))
            wasserstaende = self.db.fetchall()
            for wasserstandoben, wasserstandunten, zeitpunkt in wasserstaende:
                if haltungen.get(zeitpunkt) is None:
                    haltungen[zeitpunkt] = {}
                haltungen[zeitpunkt][haltung] = {"wasserstandoben": wasserstandoben,
                                                 "wasserstandunten": wasserstandunten}

        for schacht in self.route.get("schaechte"):
            self.db.sql("SELECT wasserstand,zeitpunkt FROM lau_gl_s WHERE knoten='{}'".format(schacht))
            wasserstaende = self.db.fetchall()
            for wasserstand, zeitpunkt in wasserstaende:
                if schaechte.get(zeitpunkt) is None:
                    schaechte[zeitpunkt] = {}
                schaechte[zeitpunkt][schacht] = wasserstand
        return len(schaechte.keys()) - 1, {"haltungen": haltungen, "schaechte": schaechte}, sorted(schaechte.keys())

    def draw(self, timestamp):
        self.x_pointer = 0
        self.x = []
        self.y = []
        switch = True
        haltungen = list(self.route.get("haltungen"))
        schaechte = list(self.route.get("schaechte"))

        def draw_schacht(name):
            if name == "Auslass":  # todo
                return
            wasserstand = self.simulation.get("schaechte").get(timestamp).get(name)

            self.x += [self.x_pointer, self.x_pointer + self.schacht_breite]
            self.y += [wasserstand, wasserstand]
            self.x_pointer += self.schacht_breite

        def draw_haltung(name):
            haltung = self.route.get("haltunginfo").get(name)

            laenge = haltung.get("laenge")
            laenge -= self.schacht_breite
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
        if self.ganglinie is not None:
            self.ganglinie.draw_at(self.timestamps[value])
        self.draw(self.timestamps[value])

    def go_step(self, value):
        self.update_controls()
        if self.last_index == value:
            return
        self.last_index = value
        self.update_coordinates(value)
        self.update_timestamp(value)
        self.plot.set_data(self.x, self.y)
        self.fig.canvas.draw()

    def play(self, value, mode):
        speed = self.get_speed(value)
        self.speed = speed
        self.mode = mode
        self.last_time = datetime.datetime.today()
        self.animation.event_source.start()

    def get_speed(self, x):
        # 1sec => 50sec & 1x == 1sec
        # speed = 9.183048666 * pow(10, -2) * pow(x, 2) + 8.166482413 * pow(10, -1) * x + 3.030302998 * pow(10, -2)
        speed = x * self.simulation_second * 0.01
        return speed

    def pause(self):
        try:
            self.animation.event_source.stop()
        except AttributeError:
            pass

    def get_next_timestamp(self, index, speed, mode):
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
        timestamp = self.timestamps[value]
        time = timestamp.strftime("%d.%m.%Y %H:%M:%S")[:-3]
        self.fig.suptitle("Zeitpunkt: {}".format(time), fontsize=20)

    def update_controls(self):
        value = self.slider.value()
        min = self.slider.minimum()
        max = self.slider.maximum()
        if value == min:
            self.btn_step_forward.setDisabled(False)
            self.btn_step_backward.setDisabled(True)
        elif value == max:
            self.btn_step_forward.setDisabled(True)
            self.btn_step_backward.setDisabled(False)
        else:
            self.btn_step_forward.setDisabled(False)
            self.btn_step_backward.setDisabled(False)


def set_ax_labels(x, y):
    plt.figure(1)
    plt.xlabel(x)
    plt.ylabel(y)


def set_legend():
    legend_plots = []
    waterlevel = plots.get("water-level")
    surface = plots.get("surface")
    max = plots.get("max")
    if waterlevel is not None:
        legend_plots.append(waterlevel)
    if surface is not None:
        legend_plots.append(surface)
    if max is not None:
        legend_plots.append(max)
    plt.figure(1)
    plt.legend(handles=legend_plots)


def reset_legend():
    del plots[:]


class HaltungLine(lines.Line2D):
    def __init__(self, *args, **kwargs):
        # we'll update the position when the line data is set
        self.name = ""
        self.text = mtext.Text(0, 0, '')
        lines.Line2D.__init__(self, *args, **kwargs)

        # we can't access the label attr until *after* the line is
        # inited
        self.text.set_text(self.get_label())

    def set_figure(self, figure):
        self.text.set_figure(figure)
        lines.Line2D.set_figure(self, figure)

    def set_axes(self, axes):
        self.text.set_axes(axes)
        lines.Line2D.set_axes(self, axes)

    def set_transform(self, transform):
        # 2 pixel offset
        texttrans = transform + mtransforms.Affine2D().translate(2, 2)
        self.text.set_transform(texttrans)
        lines.Line2D.set_transform(self, transform)

    def set_data(self, x, y):
        start = x[0]
        length = x[1] - x[0]
        text_length = self.text.get_size()
        if len(x):
            self.text.set_position((start + (length / 2.) - (text_length / 2.), y[-1]))

        lines.Line2D.set_data(self, x, y)

    def set_name(self, name):
        self.name = name

    def draw(self, renderer):
        # draw my label at the end of the line with 2 pixel offset
        lines.Line2D.draw(self, renderer)
        self.text.draw(renderer)


class SchachtLinie(lines.Line2D):
    def __init__(self, *args, **kwargs):
        # we'll update the position when the line data is set
        self.text = mtext.Text(0, 0, '')
        self.name = ""
        self.schacht_breite = 1
        lines.Line2D.__init__(self, *args, **kwargs)
        # we can't access the label attr until *after* the line is
        # inited
        self.text.set_text(self.get_label())

    def set_figure(self, figure):
        self.text.set_figure(figure)
        lines.Line2D.set_figure(self, figure)

    def set_axes(self, axes):
        self.text.set_axes(axes)
        lines.Line2D.set_axes(self, axes)

    def set_transform(self, transform):
        # 2 pixel offset
        texttrans = transform + mtransforms.Affine2D().translate(2, 2)
        self.text.set_transform(texttrans)
        lines.Line2D.set_transform(self, transform)

    def set_data(self, x, y):
        if len(x):
            self.text.set_position((x[-1] + (self.schacht_breite / 2.) - (self.text.get_size() / 2.), y[-1]))

        lines.Line2D.set_data(self, x, y)

    def set_schacht_width(self, width):
        self.schacht_breite = width

    def set_name(self, name):
        self.name = name

    def draw(self, renderer):
        # draw my label at the end of the line with 2 pixel offset
        lines.Line2D.draw(self, renderer)
        self.text.draw(renderer)
