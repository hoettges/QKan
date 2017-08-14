# -*- coding: utf-8 -*-

import logging

import matplotlib.dates as mdates
from PyQt4.QtGui import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from Enums import LayerType
from ganglinie_dialog import GanglinieDialog
from qkan.database.fbfunc import FBConnection

main_logger = logging.getLogger("QKan")
main_logger.info("Ganglinien-Modul gestartet")


class Ganglinie:
    def __init__(self, t):
        """
        Constructor
        
        :param t: Gibt an, in welche Figure gezeichnet wird. Darf niemals den gleichen Wert für unterschiedliche 
         Ganglinien haben.
        :type t: int
        """
        self.__log = logging.getLogger("QKan.ganglinie.Ganglinie")
        self.__t = t
        self.__dialog = GanglinieDialog()
        self.__laengsschnitt = None
        self.__route = None
        self.__fig = plt.figure(t)
        self.__toolbar_widget = None
        self.__x = []
        self.__axes = []
        self.__plots = []
        self.__route = None
        self.__db = None
        self.__active_layer = None
        self.__colors = {}
        self.__time_plot = None
        self.__time_axes = None
        self.__dialog.combo_type.currentIndexChanged.connect(self.__type_changed)
        self.__dialog.combo_method.currentIndexChanged.connect(self.draw)

    def get_dialog(self):
        """
        Getter des Dialogs 
        """
        return self.__dialog

    def show(self):
        """
        Wenn ein Längsschnitt vorhanden ist, wird dieser entsprechend den Vorgaben eingefärbt. Nach schließen 
        der Ganglinie, werden die Farben zurückgesetzt.
        Öffnet den Ganglinien-Dialog.
        """
        if self.__dialog.isVisible():
            self.__log.info(u"Ganglinie wird bereits angezeigt")
            return
        if self.__laengsschnitt is not None:
            self.__refresh_colors()
        self.__dialog.show()
        self.__log.info(u"Ganglinie wird angezeigt")
        self.__dialog.exec_()
        if self.__laengsschnitt is not None:
            self.__log.info(u"Ganglinie wird geschlossen und Farben des Längsschnitts zurückgesetzt")
            self.__laengsschnitt.reset_colors()

    def __get_route(self, haltungen, schaechte):
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
            self.__db.sql(
                u'SELECT zeitpunkt,auslastung,durchfluss,geschwindigkeit FROM lau_gl_el WHERE "KANTE"={}'.format(
                    u"'{}'".format(haltung)))
            res = self.__db.fetchall()
            for zeitpunkt, auslastung, durchfluss, geschwindigkeit in res:
                if _haltungen.get(zeitpunkt) is None:
                    _haltungen[zeitpunkt] = {}
                _haltungen[zeitpunkt][haltung] = dict(auslastung=auslastung, durchfluss=durchfluss,
                                                      geschwindigkeit=geschwindigkeit)
        self.__log.info(u"Messdaten der Haltungen wurden abgefragt")
        for schacht in schaechte:
            self.__db.sql(u'SELECT zeitpunkt,zufluss,wasserstand,durchfluss FROM lau_gl_s WHERE "KNOTEN"={}'.format(
                u"'{}'".format(schacht)))
            res = self.__db.fetchall()
            for zeitpunkt, zufluss, wasserstand, durchfluss in res:
                if _schaechte.get(zeitpunkt) is None:
                    _schaechte[zeitpunkt] = {}
                _schaechte[zeitpunkt][schacht] = dict(zufluss=zufluss, durchfluss=durchfluss, wasserstand=wasserstand)

        self.__log.info(u"Messdaten der Schächte wurden abgefragt")
        return dict(schaechte=schaechte, haltungen=haltungen, haltunginfo=_haltungen, schachtinfo=_schaechte)

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
            for haltung in self.__route.get("haltungen"):
                for zeitpunkt in self.__x:
                    if _y.get(haltung) is None:
                        _y[haltung] = []
                    _y[haltung].append(self.__route.get("haltunginfo").get(zeitpunkt).get(haltung).get(method))
            self.__log.info(u"Y-Werte der Haltungen wurden zusammengefasst")
            return _y

        def draw_schacht():
            """
            Schreibt die Y-Werte für die jeweilige Methode zu einem gegebenen Zeitpunkt.
            
            :return: Gibt ein Dictionary mit allen Y-Werten eines bestimmten Schachts zurück
            :rtype: dict
            """
            _y = {}
            for schacht in self.__route.get("schaechte"):
                for zeitpunkt in self.__x:
                    if _y.get(schacht) is None:
                        _y[schacht] = []
                    _y[schacht].append(self.__route.get("schachtinfo").get(zeitpunkt).get(schacht).get(method))
            self.__log.info(u"Y-Werte der Schächte wurden zusammengefasst")
            return _y

        idx = self.__dialog.combo_type.currentIndex()
        self.__log.debug(u"Aktueller Index der Layer-Combobox:\t{}".format(idx))
        self.__active_layer = LayerType.Haltung if idx == 0 else LayerType.Schacht
        method_idx = self.__dialog.combo_method.currentIndex()
        self.__log.debug(u"Aktueller Index der Methoden-Combobox:\t{}".format(method_idx))
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
                ax = self.__fig.add_subplot(111)
                ax.set_ylabel(axes[idx][method_idx])
                ax.grid(True)
                ax.xaxis.set_major_formatter(formatter)
                self.__axes.append(ax)
                _plot, = ax.plot_date(self.__x, _y.get(obj),
                                      color=colors[index % len(colors)], linestyle="-",
                                      marker=None,
                                      label=obj)
                self.__plots.append(_plot)

        formatter = mdates.DateFormatter('%H:%M')
        if idx == 0:
            y = draw_haltung()
            if len(y) == 0:
                self.__dialog.combo_type.setCurrentIndex(1)
                return
            data = self.__route.get("haltungen")
            plot(y, data)
            self.__log.info(u"Haltungen wurden geplottet")
        else:
            y = draw_schacht()
            if len(y) == 0:
                self.__dialog.combo_type.setCurrentIndex(0)
                return
            data = self.__route.get("schaechte")
            plot(y, data)
            self.__log.info(u"Schächte wurden geplottet")

        plt.gcf().autofmt_xdate()
        plt.figure(self.__t)
        plt.legend(handles=self.__plots)
        self.__fig.canvas.draw()

    def __init_x(self):
        """
        Schreibt alle Zeitpunkte in eine Liste. Wichtig, um durch diese später zu iterieren.
        """
        for zeitpunkt in (
                self.__route.get("haltunginfo") if len(self.__route.get("haltunginfo")) > 0 else self.__route.get(
                    "schachtinfo")):
            self.__x.append(zeitpunkt)
        self.__x = sorted(self.__x)
        self.__log.debug(u"Alle möglichen Zeitpunkte:\t{}".format(self.__x))

    def __get_widget(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        plt.figure(self.__t)
        qw = QWidget()
        canv = FigureCanvas(self.__fig)
        toolbar = NavigationToolbar(canv, qw, True)
        for i in reversed(range(self.__dialog.verticalLayout_2.count())):
            self.__dialog.verticalLayout_2.itemAt(i).widget().setParent(None)
        self.__log.info(u"Toolbars wurden entfernt")
        self.__toolbar_widget = toolbar
        self.__dialog.verticalLayout_2.addWidget(self.__toolbar_widget)
        self.__dialog.stackedWidget.insertWidget(0, canv)
        self.__dialog.stackedWidget.setCurrentIndex(0)
        self.__log.info(u"Toolbar und Matplotlib-Widget wurden eingefügt")

    def __type_changed(self, index):
        """
        Ist der Event-Listener, falls der Typ des Layers geändert wird. Von Schacht auf Haltung zb.
        
        :param index: Entspricht dem aktuell ausgewählten Typen.
        :type index: int
        """
        self.__log.info(u"Layer-Combobox wurde umgeschaltet")
        methods = [["Durchfluss", "Geschwindigkeit", "Auslastung"], ["Zufluss", "Wasserstand", "Durchfluss"]]
        for i in range(self.__dialog.combo_method.count()):
            self.__dialog.combo_method.setItemText(i, methods[index][i])
        self.__log.info(u"Methoden-Combobox wurde mit Items gefüllt")
        self.draw()
        self.__init_colors()
        if self.__laengsschnitt is not None:
            self.__refresh_colors()

    def draw_at(self, timestamp):
        """
        Schreibt die Zeitlinie der Ganglinie zu dem Zeitpunkt, in dem sich die Simulation befindet.
        Nur wichtig im Zusammenhang mit dem Längsschnitt.

        :param timestamp: Entspricht dem Zeitpunkt, welcher visualisiert werden soll.
        :type timestamp: datetime
        """
        if self.__time_plot is None:
            self.__time_axes = self.__fig.add_subplot(111)
            y_lim = self.__time_axes.get_ylim()
            self.__time_plot, = self.__time_axes.plot_date([timestamp, timestamp], y_lim,
                                                           color="k", linestyle="-",
                                                           marker=None,
                                                           label="Zeitlinie", alpha=0.5)
            self.__time_axes.set_ylim(y_lim)
        else:
            self.__time_plot.set_data([timestamp, timestamp], self.__time_axes.get_ylim())
        try:
            self.__fig.canvas.draw()
        except ValueError:
            pass

    def refresh(self, haltungen, schaechte, dbname, laengsschnitt=None):
        """
        Wird aufgerufen, um die Ganglinie mit allen wichtigen Datensätzen abzudaten.
        Wichtig bspw. wenn neue Elemente ausgewählt wurden.

        :param haltungen: Entspricht einer Liste alle Haltungs-Namen aus QGis
        :type haltungen: list
        :param schaechte: Entspricht einer Liste aller Schächte-Namen aus QGis
        :type schaechte: list
        :param dbname: Entspricht dem Datenbank-Pfad der Ergebnis-Datenbank
        :type dbname: str
        :param laengsschnitt: Entspricht einer verknüpften Laengsschnitt-Instanz
        :type laengsschnitt: Laengsschnitt
        """
        self.__db = FBConnection(dbname)
        self.__route = self.__get_route(haltungen, schaechte)
        self.__laengsschnitt = laengsschnitt
        self.__init_x()
        self.__get_widget()
        self.draw()
        self.__init_colors()

    def __init_colors(self):
        """
        Speicher die Farbwerte der Ganglinien-Plots in einem Dictionary, um diese auch im Längsschnitt einzufärben.
        """
        tmp_colors = dict(layer=self.__active_layer, plots={})
        for plot in self.__plots:
            tmp_colors["plots"][plot.get_label()] = plot.get_color()
        self.__colors = tmp_colors
        self.__log.info(u"Farbwerte der Plots wurden abgespeichert")
        self.__log.debug(u"Farbwerte:\t{}".format(tmp_colors))

    def reset(self):
        """
        Wird aufgerufen, um die Ganglinie zurückzusetzen. Hier werden alle Plots aus der Figure entfernt.
        """
        for plot in self.__axes:
            try:
                self.__fig.delaxes(plot)
            except KeyError:
                pass
        self.__log.info(u"Plots wurden entfernt")
        self.__plots = []
        if self.__time_plot is not None:
            self.__time_plot = None
            self.__time_axes = None
            self.__log.info(u"Vertikale Linie wurde zurückgesetzt")

    def __refresh_colors(self):
        """
        Weist die Länggsschnitt-Instanz an, die Plots in den übergebenen Farben einzufärben.
        """
        self.__colors["layer"] = self.__active_layer
        self.__laengsschnitt.set_colors(self.__colors)
        self.__log.info(u"Farben des Längsschnitts wurden angepasst")
