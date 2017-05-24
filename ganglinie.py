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
        """
        Constructor
        
        :param t: Gibt an, in welche Figure gezeichnet wird. Darf niemals den gleichen Wert für unterschiedliche 
         Ganglinien haben.
        :type t: int
        """
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
        """
        Wenn ein Längsschnitt vorhanden ist, wird dieser entsprechend den Vorgaben eingefärbt. Nach schließen 
        der Ganglinie, werden die Farben zurückgesetzt.
        Öffnet den Ganglinien-Dialog.
        """
        if self.dialog.isVisible():
            return
        if self.laengsschnitt is not None:
            self.refresh_colors()
        self.dialog.show()
        self.dialog.exec_()
        if self.laengsschnitt is not None:
            self.laengsschnitt.reset_colors()

    def get_route(self, haltungen, schaechte):
        """
        Fragt die Datenbank nach allen nötigen Informationen der ausgewählten Elemente ab, die für die Ganglinie 
        benötigt werden.

        :param haltungen: Enthält alle selektierten Haltungs-Namen aus QGis
        :type haltungen: list
        :param schaechte: Enthält alle selektierten Schacht-Namen aus QGis
        :type schaechte: list
        :return: Gibt ein Dictionary zurück mit allen nötigen Datensätzen
        :rtype: dict
        """
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
        """
        Schreibt die Datensätze in eine Figure von Matplotlib.
        """
        self.reset()

        def draw_haltung():
            """
            Schreibt die Y-Werte für die jeweilige Methode zu einem gegebenen Zeitpunkt.
            
            :return: Gibt ein Dictionary mit allen Y-Werten einer bestimmten Haltung zurück
            :rtype: dict
            """
            _y = {}
            for haltung in self.route.get("haltungen"):
                for zeitpunkt in self.x:
                    if _y.get(haltung) is None:
                        _y[haltung] = []
                    _y[haltung].append(self.route.get("haltunginfo").get(zeitpunkt).get(haltung).get(method))
            return _y

        def draw_schacht():
            """
            Schreibt die Y-Werte für die jeweilige Methode zu einem gegebenen Zeitpunkt.
            
            :return: Gibt ein Dictionary mit allen Y-Werten eines bestimmten Schachts zurück
            :rtype: dict
            """
            _y = {}
            for schacht in self.route.get("schaechte"):
                for zeitpunkt in self.x:
                    if _y.get(schacht) is None:
                        _y[schacht] = []
                    _y[schacht].append(self.route.get("schachtinfo").get(zeitpunkt).get(schacht).get(method))
            return _y

        idx = self.dialog.combo_type.currentIndex()
        self.active_layer = LayerType.Haltung if idx == 0 else LayerType.Schacht
        method_idx = self.dialog.combo_method.currentIndex()
        methods = [["durchfluss", "geschwindigkeit", "auslastung"], ["zufluss", "wasserstand", "durchfluss"]]
        method = methods[idx][method_idx]
        axes = [["cbm/s", "m/s", "%"], ["cbm/s", "m NN", "cbm/s"]]

        colors = ["#00BFFF", "#C000FF", "#FF4000", "#40FF00", "#00FFD5", "#A9FF00", "#FF0077", "#F6FF00", "#FFDD00",
                  "#FF8800", "#FF00A2", "#FF9E00"]

        def plot(_y, _data):
            """
            Schreibt die Datensätze in die Figure der Ganglinie.
            
            :param _y: Beinhaltet entweder alle Y-Werte der Schächte oder Haltungen.
            :type _y: dict
            :param _data: Entspricht allen Haltungs- bzw. Schachtnamen
            :type _data: list
            """
            for index, obj in enumerate(_data):
                ax = self.fig.add_subplot(111)
                ax.set_ylabel(axes[idx][method_idx])
                ax.grid(True)
                ax.xaxis.set_major_formatter(formatter)
                self.axes.append(ax)
                _plot, = ax.plot_date(self.x, _y.get(obj),
                                      color=colors[index % len(colors)], linestyle="-",
                                      marker=None,
                                      label=obj)
                self.plots.append(_plot)

        formatter = mdates.DateFormatter('%H:%M')
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
        plt.figure(self.t)
        plt.legend(handles=self.plots)
        self.fig.canvas.draw()

    def init_x(self):
        """
        Schreibt alle Zeitpunkte in eine Liste. Wichtig, um durch diese später zu iterieren.
        """
        for zeitpunkt in (
                self.route.get("haltunginfo") if len(self.route.get("haltunginfo")) > 0 else self.route.get(
                    "schachtinfo")):
            self.x.append(zeitpunkt)
        self.x = sorted(self.x)

    def get_widget(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
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
        """
        Ist der Event-Listener, falls der Typ des Layers geändert wird. Von Schacht auf Haltung zb.
        
        :param index: Entspricht dem aktuell ausgewählten Typen.
        :type index: int
        """
        methods = [["Durchfluss", "Geschwindigkeit", "Auslastung"], ["Zufluss", "Wasserstand", "Durchfluss"]]
        for i in range(self.dialog.combo_method.count()):
            self.dialog.combo_method.setItemText(i, methods[index][i])
        self.draw()
        self.init_colors()
        if self.laengsschnitt is not None:
            self.refresh_colors()

    def draw_at(self, timestamp):
        """
        Schreibt die Zeitlinie der Ganglinie zu dem Zeitpunkt, in dem sich die Simulation befindet.
        Nur wichtig im Zusammenhang mit dem Längsschnitt.

        :param timestamp: Entspricht dem Zeitpunkt, welcher visualisiert werden soll.
        :type timestamp: datetime
        """
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
        """
        Wird aufgerufen, um die Ganglinie mit allen wichtigen Datensätzen abzudaten.
        Wichtig bspw. wenn neue Elemente ausgewählt wurden.

        :param _id: Entspricht einer ID des aktuellen Ganglinien-Objektes
        :type _id: float
        :param haltungen: Entspricht einer Liste alle Haltungs-Namen aus QGis
        :type haltungen: list
        :param schaechte: Entspricht einer Liste aller Schächte-Namen aus QGis
        :type schaechte: list
        :param dbname: Entspricht dem Datenbank-Pfad der Ergebnis-Datenbank
        :type dbname: str
        :param laengsschnitt: Entspricht einer verknüpften Laengsschnitt-Instanz
        :type laengsschnitt: Laengsschnitt
        """
        self.id = _id
        self.db = self.db = FBConnection(dbname)
        self.route = self.get_route(haltungen, schaechte)
        self.laengsschnitt = laengsschnitt
        self.init_x()
        self.get_widget()
        self.draw()
        self.init_colors()

    def init_colors(self):
        """
        Speicher die Farbwerte der Ganglinien-Plots in einem Dictionary, um diese auch im Längsschnitt einzufärben.
        """
        tmp_colors = {"layer": self.active_layer, "plots": {}}
        for plot in self.plots:
            tmp_colors["plots"][plot.get_label()] = plot.get_color()
        self.colors = tmp_colors

    def reset(self):
        """
        Wird aufgerufen, um die Ganglinie zurückzusetzen. Hier werden alle Plots auf der Figure entfernt.
        """
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
        """
        Weist die Länggsschnitt-Instanz an, die Plots in den übergebenen Farben einzufärben.
        """
        self.colors["layer"] = self.active_layer
        self.laengsschnitt.set_colors(self.colors)
