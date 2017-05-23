# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from ganglinie_dialog import GanglinieDialog
from QKan_Database.fbfunc import FBConnection
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.dates as mdates
from Enums import LayerType


class Ganglinie:
    def __init__(self, t):
        self.t = t
        self.dialog = GanglinieDialog()
        self.laengsschnitt = None
        self.db = ""
        self.id = -1
        self.route = None
        self.fig = plt.figure(t)
        self.toolbar_widget = None
        self.x = []
        self.axes = []
        self.plots = []
        self.route = None
        self.db = None
        self.active_layer = None
        self.colors = {}
        self.time_plot = None
        self.time_axes = None
        self.dialog.combo_type.currentIndexChanged.connect(self.type_changed)
        self.dialog.combo_method.currentIndexChanged.connect(self.draw)

    def show(self):
        if self.laengsschnitt is not None:
            self.refresh_colors()
        self.dialog.show()
        self.dialog.exec_()
        if self.laengsschnitt is not None:
            self.laengsschnitt.reset_colors()

    def get_route(self, haltungen, schaechte):
        _haltungen = {}
        _schaechte = {}
        for haltung in haltungen:
            self.db.sql(
                u'SELECT zeitpunkt,auslastung,durchfluss,geschwindigkeit FROM lau_gl_el WHERE "KANTE"={}'.format(
                    u"'{}'".format(haltung)))
            res = self.db.fetchall()
            for zeitpunkt, auslastung, durchfluss, geschwindigkeit in res:
                if _haltungen.get(zeitpunkt) is None:
                    _haltungen[zeitpunkt] = {}
                _haltungen[zeitpunkt][haltung] = {"auslastung": auslastung, "durchfluss": durchfluss,
                                                  "geschwindigkeit": geschwindigkeit}
        for schacht in schaechte:
            self.db.sql(u'SELECT zeitpunkt,zufluss,wasserstand,durchfluss FROM lau_gl_s WHERE "KNOTEN"={}'.format(
                u"'{}'".format(schacht)))
            res = self.db.fetchall()
            for zeitpunkt, zufluss, wasserstand, durchfluss in res:
                if _schaechte.get(zeitpunkt) is None:
                    _schaechte[zeitpunkt] = {}
                _schaechte[zeitpunkt][schacht] = {"zufluss": zufluss, "durchfluss": durchfluss,
                                                  "wasserstand": wasserstand}
        return {"schaechte": schaechte, "haltungen": haltungen, "haltunginfo": _haltungen, "schachtinfo": _schaechte}

    def draw(self):
        self.reset()

        def draw_haltung():
            y = {}
            for haltung in self.route.get("haltungen"):
                for zeitpunkt in self.x:
                    if y.get(haltung) is None:
                        y[haltung] = []
                    y[haltung].append(self.route.get("haltunginfo").get(zeitpunkt).get(haltung).get(method))
            return y

        def draw_schacht():
            y = {}
            for schacht in self.route.get("schaechte"):
                for zeitpunkt in self.x:
                    if y.get(schacht) is None:
                        y[schacht] = []
                    y[schacht].append(self.route.get("schachtinfo").get(zeitpunkt).get(schacht).get(method))
            return y

        idx = self.dialog.combo_type.currentIndex()
        self.active_layer = LayerType.Haltung if idx == 0 else LayerType.Schacht
        method_idx = self.dialog.combo_method.currentIndex()
        methods = [["durchfluss", "geschwindigkeit", "auslastung"], ["zufluss", "wasserstand", "durchfluss"]]
        method = methods[idx][method_idx]
        axes = [["cbm/s", "m/s", "%"], ["cbm/s", "m NN", "cbm/s"]]

        colors = ["#00BFFF", "#C000FF", "#FF4000", "#40FF00", "#00FFD5", "#A9FF00", "#FF0077", "#F6FF00", "#FFDD00",
                  "#FF8800", "#FF00A2", "#FF9E00"]

        def plot(_y, _data):
            for index, obj in enumerate(_data):
                ax = self.fig.add_subplot(111)
                ax.set_ylabel(axes[idx][method_idx])
                self.axes.append(ax)
                _plot, = ax.plot_date(self.x, _y.get(obj),
                                      color=colors[index % len(colors)], linestyle="-",
                                      marker=None,
                                      label=obj)
                self.plots.append(_plot)

        if idx == 0:
            y = draw_haltung()
            if len(y) == 0:
                self.dialog.combo_type.setCurrentIndex(1)
                return
            data = self.route.get("haltungen")
            plot(y, data)
        else:
            y = draw_schacht()
            if len(y) == 0:
                self.dialog.combo_type.setCurrentIndex(0)
                return
            data = self.route.get("schaechte")
            plot(y, data)

        plt.gcf().autofmt_xdate()
        formatter = mdates.DateFormatter('%H:%M')
        try:
            plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
            plt.gcf().axes[0].grid(True)
        except IndexError:
            pass
        plt.figure(self.t)
        plt.legend(handles=self.plots)
        self.fig.canvas.draw()

    def init_x(self):
        for zeitpunkt in (
                self.route.get("haltunginfo") if len(self.route.get("haltunginfo")) > 0 else self.route.get(
                    "schachtinfo")):
            self.x.append(zeitpunkt)
        self.x = sorted(self.x)

    def get_widget(self):
        plt.figure(self.t)
        qw = QWidget()
        canv = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(canv, qw, True)
        for i in reversed(range(self.dialog.verticalLayout_2.count())):
            self.dialog.verticalLayout_2.itemAt(i).widget().setParent(None)
        self.toolbar_widget = toolbar
        self.dialog.verticalLayout_2.addWidget(self.toolbar_widget)
        self.dialog.stackedWidget.insertWidget(0, canv)
        self.dialog.stackedWidget.setCurrentIndex(0)

    def type_changed(self, index):
        methods = [["Durchfluss", "Geschwindigkeit", "Auslastung"], ["Zufluss", "Wasserstand", "Durchfluss"]]
        for i in range(self.dialog.combo_method.count()):
            self.dialog.combo_method.setItemText(i, methods[index][i])
        self.draw()
        self.init_colors()
        if self.laengsschnitt is not None:
            self.refresh_colors()

    def draw_at(self, timestamp):
        if self.time_plot is None:
            self.time_axes = self.fig.add_subplot(111)
            y_lim = self.time_axes.get_ylim()
            self.time_plot, = self.time_axes.plot_date([timestamp, timestamp], y_lim,
                                                       color="k", linestyle="-",
                                                       marker=None,
                                                       label="Zeitlinie", alpha=0.5)
            self.time_axes.set_ylim(y_lim)
        else:
            self.time_plot.set_data([timestamp, timestamp], self.time_axes.get_ylim())
        try:
            self.fig.canvas.draw()
        except ValueError:
            pass

    def refresh(self, _id, haltungen, schaechte, dbname, laengsschnitt=None):
        self.id = _id
        self.db = self.db = FBConnection(dbname)
        self.route = self.get_route(haltungen, schaechte)
        self.laengsschnitt = laengsschnitt
        self.init_x()
        self.get_widget()
        self.draw()
        self.init_colors()

    def init_colors(self):
        tmp_colors = {"layer": self.active_layer, "plots": {}}
        for plot in self.plots:
            tmp_colors["plots"][plot.get_label()] = plot.get_color()
        self.colors = tmp_colors

    def reset(self):
        for plot in self.axes:
            try:
                self.fig.delaxes(plot)
            except KeyError:
                pass
        self.plots = []
        if self.time_plot is not None:
            self.time_plot = None
            self.time_axes = None

    def refresh_colors(self):
        self.colors["layer"] = self.active_layer
        self.laengsschnitt.set_colors(self.colors)
