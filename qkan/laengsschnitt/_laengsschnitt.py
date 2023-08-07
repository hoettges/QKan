import logging
from qgis.utils import iface, spatialite_connect
from qgis.core import Qgis
import csv
from pathlib import Path
import datetime

import win32com.client
import pythoncom
from win32com.client import VARIANT
import pywintypes
from PyQt5 import QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
import matplotlib.animation as animation
from matplotlib.widgets import Slider
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.database.qkan_utils import get_qkanlayer_attributes
from .dijkstra import find_route
import numpy as np
import random


logger = logging.getLogger("QKan.laengs.import")


#TODO: mit einpflegen, dass die Geländehöhe von meheren DGM Layern angezeigt wird


class LaengsTask:
    def __init__(self, db_qkan: DBConnection, file: str, fig: plt.figure, canv: FigureCanvas, fig_2: plt.figure,
                 canv_2: FigureCanvas, fig_3: plt.figure, canv_3: FigureCanvas, selected, auswahl, point,
                 massstab, features, db_erg, ausgabe, max, label_4,
                 pushButton_4, horizontalSlider_3, geschw_2):
        self.db_qkan = db_qkan
        self.fig = fig
        self.canv = canv
        self.fig_2 = fig_2
        self.canv_2 = canv_2
        self.fig_3 = fig_3
        self.canv_3 = canv_3
        self.selected = selected
        self.auswahl = auswahl
        self.point = point
        self.massstab = massstab
        self.features = features
        self.db_erg = db_erg
        self.ausgabe = ausgabe
        self.max = max
        self.label_4 = label_4
        self.pushButton_4 = pushButton_4
        self.horizontalSlider_3 = horizontalSlider_3
        self.geschw_2 = geschw_2
        self.anf = 0

        self.db_erg = spatialite_connect(self.db_erg)
        self.db_erg_curs = self.db_erg.cursor()

        self.pushButton_4.clicked.connect(self.stop)
        self.horizontalSlider_3.sliderReleased.connect(self.slider)
        self.horizontalSlider_3.sliderPressed.connect(self.stop_slider)
        self.geschw_2.sliderReleased.connect(self.slider_2)
        self.geschw = self.geschw_2.value()*10



    def run(self) -> bool:
        self.zeichnen()

    def stop(self):
        if self.pushButton_4.text() == 'Stop':
            try:
                self.anim.event_source.stop()
                self.pushButton_4.setText('Start')
            except AttributeError:
                pass
        elif self.pushButton_4.text() == 'Start':
            try:
                self.anim.event_source.start()
                self.pushButton_4.setText('Stop')
            except AttributeError:
                pass


    def stop_slider(self):
        try:
            self.anim.event_source.stop()
            self.pushButton_4.setText('Start')
        except AttributeError:
            pass


    def slider(self):
        """Ändern der frames der Animation"""

        # aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)

        t = None

        # selektierte elemente anzeigen
        self.selected = layer.selectedFeatures()
        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste = []
        liste2 = []

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.Critical)
            return

        if table == 'schaechte':
            for f in self.selected:
                x = f['schnam']
                liste.append(x)

        if table == 'haltungen':
            for f in self.selected:
                x = f['schoben']
                x2 = f['schunten']
                x3 = f['haltnam']
                liste2.append(x3)
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)

        route = find_route(self.db_qkan, liste)
        logger.debug(f'Fehler in slider. liste: {liste}')
        logger.debug(f'route: {route}')

        if route is None:
            iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente Ausgewählt', level=Qgis.Critical)
            return 'nicht erstellt'

        # route = (['2747.1J55', '2747.1J56', '2747.1J57'], ['M2747.1J55', 'M2747.1J56'])
        x_sohle = []
        y_sohle = []
        x_sohle2 = []
        y_sohle2 = []
        x_deckel = []
        y_deckel = []
        y_label = []
        name = []
        haltnam_l = []
        schoben_l = []
        schunten_l = []
        laenge_l = []
        entwart_l = []
        hoehe_l = []
        breite_l = []
        material_l = []
        strasse_l = []
        haltungstyp_l = []

        sel = '), ('.join([f"'{num}', {el}" for el, num in enumerate(route[1])])  # sel = ('15600000-45', 0), ('15600000-50', 1), ...)
        sql = f"""
                    SELECT
                        h.schoben,
                        h.hoehe,
                        h.schunten,
                        h.laenge,
                        schob.deckelhoehe,
                        schob.sohlhoehe,
                        schun.deckelhoehe,
                        schun.sohlhoehe,
                        h.entwart,
                        h.haltnam,
                        h.breite,
                        h.material,
                        h.strasse,
                        h.haltungstyp,
                        h.sohleoben,
                        h.sohleunten,
                        schob.knotentyp,
                        schun.knotentyp,
                        schob.entwart,
                        schun.entwart,
                        sum(h.laenge) OVER (ORDER BY sel.column2 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as laenge_sum
                    FROM haltungen AS h
                    INNER JOIN schaechte AS schob ON schob.schnam = h.schoben
                    INNER JOIN schaechte AS schun ON schun.schnam = h.schunten
                    INNER JOIN (VALUES ({sel})) AS sel ON sel.column1 = h.haltnam
                    """

        if not self.db_qkan.sql(sql, "laengsschnitt.zeichnen.1"):
            logger.error(f"{__file__}: Fehler in laengsschnitt.zeichnen.1: Datenbankzugriff nicht möglich")
            return 'nicht erstellt'

        for attr in self.db_qkan.fetchall():
            (
                schoben, hoehe, schunten, laenge, deckeloben, sohleoben, deckelunten, sohleunten, entwart,
                haltnam, breite, material, strasse, haltungstyp, haltung_sohle_o, haltung_sohle_u,
                schob_typ, schun_typ, entwart_o, entwart_u, laenge2
            ) = attr

            if int(haltung_sohle_o) == 0:
                haltung_sohle_o = sohleoben
            if int(haltung_sohle_u) == 0:
                haltung_sohle_u = sohleunten

            y_sohle.append(sohleoben)
            y_sohle.append(haltung_sohle_o)
            y_sohle.append(haltung_sohle_u)
            y_sohle.append(sohleunten)
            x_sohle.append(laenge2 - laenge)
            x_sohle.append(laenge2 - laenge)
            x_sohle.append(laenge2)
            x_sohle.append(laenge2)

            if sohleoben > 0:
                y_sohle2.append(sohleoben + hoehe)
            else:
                y_sohle2.append(sohleoben)
            if haltung_sohle_o > 0:
                y_sohle2.append(haltung_sohle_o + hoehe)
            else:
                y_sohle2.append(haltung_sohle_o)
            if haltung_sohle_u > 0:
                y_sohle2.append(haltung_sohle_u + hoehe)
            else:
                y_sohle2.append(haltung_sohle_u)
            if sohleunten > 0:
                y_sohle2.append(sohleunten + hoehe)
            else:
                y_sohle2.append(sohleunten)
            x_sohle2.append(laenge2 - laenge)
            x_sohle2.append(laenge2 - laenge)
            x_sohle2.append(laenge2)
            x_sohle2.append(laenge2)

            y_deckel.append(deckeloben)
            y_deckel.append(deckeloben)
            y_deckel.append(deckelunten)
            y_deckel.append(deckelunten)
            x_deckel.append(laenge2 - laenge)
            x_deckel.append(laenge2 - laenge)
            x_deckel.append(laenge2)
            x_deckel.append(laenge2)

            y_label.append((deckeloben + sohleoben - hoehe) / 2)
            y_label.append((deckelunten + sohleunten - hoehe) / 2)

            name.append(schoben)
            name.append(schunten)
            haltnam_l.append(haltnam)
            schoben_l.append(schoben)
            schunten_l.append(schunten)
            laenge_l.append(laenge)
            entwart_l.append(entwart)
            hoehe_l.append(hoehe)
            breite_l.append(breite)
            material_l.append(material)
            strasse_l.append(strasse)
            haltungstyp_l.append(haltungstyp)

        x = [i for i in y_deckel if i != 0]
        x2 = [i for i in y_sohle if i != 0]
        x3 = [i for i in y_sohle2 if i != 0]

        max_deckel = max(x)
        min_sohle = min(x2)
        min_sohle2 = min(x3)
        y_deckel_n = []
        y_sohle_n = []
        y_sohle2_n = []

        i = 0
        for x in y_deckel:
            if x == 0:
                y_deckel_n.append(max_deckel)
            else:
                y_deckel_n.append(y_deckel[i])
            i += 1
        i = 0
        for x in y_sohle:
            if x == 0:
                y_sohle_n.append(min_sohle)
            else:
                y_sohle_n.append(y_sohle[i])
            i += 1
        i = 0
        for x in y_sohle2:
            if x == 0:
                y_sohle2_n.append(min_sohle2)
            else:
                y_sohle2_n.append(y_sohle2[i])
            i += 1

        haltungen = {}
        schaechte = {}

        if table == 'haltungen':
            for haltung, xkoordinate_o, xkoordinate_u in zip(liste2, x_sohle2[0::2], x_sohle2[1::2]):
                sql = 'SELECT wasserstandoben,wasserstandunten,zeitpunkt FROM lau_gl_el WHERE KANTE=?'
                data = (haltung,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.Critical)

                wasserstaende = self.db_erg_curs.fetchall()

                for wasserstandoben, wasserstandunten, zeitpunkt_t in wasserstaende:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       "Konvertierung vom Zeitpunkt fehlgeschlagen",
                                                       level=Qgis.Critical)
                    if haltungen.get(zeitpunkt) is None:
                        haltungen[zeitpunkt] = {}
                    haltungen[zeitpunkt][haltung] = dict(
                        wasserstandoben=wasserstandoben, wasserstandunten=wasserstandunten, xkoordinate_o=xkoordinate_o,
                        xkoordinate_u=xkoordinate_u
                    )
            zeit = []
            y_liste = []
            x_liste = []

            for i in haltungen:
                zeit.append(i)
            for time in zeit:
                x = []
                y = []
                for h in liste2:
                    y.append(haltungen[time][h]['wasserstandoben'])
                    y.append(haltungen[time][h]['wasserstandunten'])
                    x.append(haltungen[time][h]['xkoordinate_o'])
                    x.append(haltungen[time][h]['xkoordinate_u'])
                x_liste.append(x)
                y_liste.append(y)

            y_sohle_2 = []
            y_deckel_3 = []
            x_deckel_2 = []
            delete = []
            # wenn die höhen null sind schachthöhen =max und min werte setzen und farbe grau
            y1 = [i for i in y_sohle if i != 0]
            y2 = [i for i in y_deckel if i != 0]

            min_sohle = min(y1)
            max_deckel = max(y2)

            i = 0
            for x, y in zip(y_sohle, y_deckel_n):
                if y_sohle[i] == 0.0 or y_deckel_n[i] == 0.0:
                    y_sohle_2.append(min_sohle)
                    y_deckel_3.append(max_deckel)
                    x_deckel_2.append(x_deckel[i])
                    delete.append(i)
                i += 1

            for x in delete[::-1]:
                y_sohle.pop(x)
                y_deckel_n.pop(x)
                x_deckel.pop(x)

        if table == 'schaechte':
            x_deckel_neu = []

            for i in x_deckel:
                if i not in x_deckel_neu:
                    x_deckel_neu.append(i)

            for schacht, xkoordinate in zip(liste, x_deckel_neu):
                sql = 'SELECT wasserstand,zeitpunkt FROM lau_gl_s WHERE KNOTEN=?'
                data = (schacht,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.Critical)
                wasserstaende = self.db_erg_curs.fetchall()

                for wasserstand, zeitpunkt_t in wasserstaende:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       "Daten konnten nicht ausgelesen werden",
                                                       level=Qgis.Critical)
                    if schaechte.get(zeitpunkt) is None:
                        schaechte[zeitpunkt] = {}
                    schaechte[zeitpunkt][schacht] = dict(
                        wasserstand=wasserstand, xkoordinate=xkoordinate
                    )

            zeit = []
            y_liste = []
            x_liste = []

            for i in schaechte:
                zeit.append(i)
            for time in zeit:
                x = []
                y = []
                for s in liste:
                    y.append(schaechte[time][s]['wasserstand'])
                    x.append(schaechte[time][s]['xkoordinate'])
                x_liste.append(x)
                y_liste.append(y)

            y_sohle_2 = []
            y_deckel_3 = []
            x_deckel_2 = []
            delete = []

            # wenn die höhen null sind schachthöhen =max und min werte setzen und farbe grau
            y1 = [i for i in y_sohle if i != 0]
            y2 = [i for i in y_deckel if i != 0]

            min_sohle = min(y1)
            max_deckel = max(y2)

            i = 0
            for x, y in zip(y_sohle, y_deckel_n):
                if y_sohle[i] == 0.0 or y_deckel_n[i] == 0.0:
                    y_sohle_2.append(min_sohle)
                    y_deckel_3.append(max_deckel)
                    x_deckel_2.append(x_deckel[i])
                    delete.append(i)
                i += 1

            for x in delete[::-1]:
                y_sohle.pop(x)
                y_deckel_n.pop(x)
                x_deckel.pop(x)

        self.anf = self.horizontalSlider_3.value()
        #self.anim.frames = range(self.anf, len(zeit))
        self.anim.event_source.frames = range(self.anf, len(zeit))
        self.anim.event_source.stop()

        try:
            self.anim.event_source.start()
            self.pushButton_4.setText('Stop')
        except AttributeError:
            pass


    def slider_2(self):
        """Geschwindigkeit der Animation ändern"""

        self.anim._interval = float(self.geschw)
        #self.anim.event_source.interval = float(self.geschw)
        self.anim.event_source.stop()

        try:
            self.anim.event_source.start()
            self.pushButton_4.setText('Stop')
        except AttributeError:
            pass


    def zeichnen(self):
        """Längsschnitt in das Fenster zeichnen"""
        figure = self.fig
        figure.clear()
        plt.figure(figure.number)
        new_plot = figure.add_subplot(111)

        points = self.point.split(",", 1)
        massstab_liste = self.massstab.split(":", 1)
        pointx = float(points[0])
        pointy = float(points[1])
        massstab = float(massstab_liste[1])

        #aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        #mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)


        #selektierte elemente anzeigen
        self.selected = layer.selectedFeatures()
        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste=[]
        liste2=[]

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.Critical)
            return

        if table == 'schaechte':
            for f in self.selected:
                x = f['schnam']
                liste.append(x)

        if table == 'haltungen':
            for f in self.selected:
                x = f['schoben']
                x2 = f['schunten']
                x3 = f['haltnam']
                liste2.append(x3)
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)


        route = find_route(self.db_qkan, liste)
        logger.debug(f'Fehler in zeichnen. liste: {liste}')
        logger.debug(f'route: {route}')

        if route is None:
            iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente Ausgewählt', level=Qgis.Critical)
            return 'nicht erstellt'

        # route = (['2747.1J55', '2747.1J56', '2747.1J57'], ['M2747.1J55', 'M2747.1J56'])
        if table == 'schaechte':
            liste = []
            for f in route[0]:
                liste.append(f)

        if table == 'haltungen':
            liste = []
            for x in route[0]:
                liste.append(x)
            liste2 = []
            for y in route[1]:
                liste2.append(y)

        x_sohle = []
        y_sohle = []
        x_sohle2 = []
        y_sohle2 = []
        x_deckel = []
        y_deckel = []
        y_label = []
        name = []
        haltnam_l = []
        schoben_l = []
        schunten_l = []
        laenge_l = []
        entwart_l = []
        hoehe_l = []
        breite_l = []
        material_l = []
        strasse_l = []
        haltungstyp_l = []
        schachttyp_l =[]
        schaechte_l = []
        deckel_l = []
        sohle_l = []
        entwart_s =[]

        z_deckel = []
        z_sohle = []
        z_sohle_h = []

        sel = '), ('.join([f"'{num}', {el}" for el, num in enumerate(route[1])])         # sel = ('15600000-45', 0), ('15600000-50', 1), ...)
        sql = f"""
            SELECT
                h.schoben,
                h.hoehe,
                h.schunten,
                h.laenge,
                schob.deckelhoehe,
                schob.sohlhoehe,
                schun.deckelhoehe,
                schun.sohlhoehe,
                h.entwart,
                h.haltnam,
                h.breite,
                h.material,
                h.strasse,
                h.haltungstyp,
                h.sohleoben,
                h.sohleunten,
                schob.knotentyp,
                schun.knotentyp,
                schob.entwart,
                schun.entwart,
                sum(h.laenge) OVER (ORDER BY sel.column2 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as laenge_sum
            FROM haltungen AS h
            INNER JOIN schaechte AS schob ON schob.schnam = h.schoben
            INNER JOIN schaechte AS schun ON schun.schnam = h.schunten
            INNER JOIN (VALUES ({sel})) AS sel ON sel.column1 = h.haltnam
            """

        if not self.db_qkan.sql(sql, "laengsschnitt.zeichnen.2"):
            logger.error(f"{__file__}: Fehler in laengsschnitt.zeichnen.2: Datenbankzugriff nicht möglich")
            return 'nicht erstellt'

        for attr in self.db_qkan.fetchall():
            (
                schoben, hoehe, schunten, laenge, deckeloben, sohleoben, deckelunten, sohleunten, entwart,
                haltnam, breite, material, strasse, haltungstyp, haltung_sohle_o, haltung_sohle_u,
                schob_typ, schun_typ, entwart_o, entwart_u, laenge2
            ) = attr

            hschoben = sohleoben
            hschunten = sohleunten

            if int(haltung_sohle_o) == 0:
                haltung_sohle_o = sohleoben
            if int(haltung_sohle_u) == 0:
                haltung_sohle_u = sohleunten

            y_sohle.append(sohleoben)
            y_sohle.append(haltung_sohle_o)
            y_sohle.append(haltung_sohle_u)
            y_sohle.append(sohleunten)
            x_sohle.append(laenge2 - laenge)
            x_sohle.append(laenge2 - laenge)
            x_sohle.append(laenge2)
            x_sohle.append(laenge2)

            if sohleoben > 0:
                y_sohle2.append(sohleoben + hoehe)
            else:
                y_sohle2.append(sohleoben)
            if haltung_sohle_o > 0:
                y_sohle2.append(haltung_sohle_o + hoehe)
            else:
                y_sohle2.append(haltung_sohle_o)
            if haltung_sohle_u > 0:
                y_sohle2.append(haltung_sohle_u + hoehe)
            else:
                y_sohle2.append(haltung_sohle_u)
            if sohleunten > 0:
                y_sohle2.append(sohleunten + hoehe)
            else:
                y_sohle2.append(sohleunten)
            x_sohle2.append(round(laenge2 - laenge,2))
            x_sohle2.append(round(laenge2 - laenge,2))
            x_sohle2.append(laenge2)
            x_sohle2.append(laenge2)

            y_deckel.append(deckeloben)
            y_deckel.append(deckeloben)
            y_deckel.append(deckelunten)
            y_deckel.append(deckelunten)
            x_deckel.append(round(laenge2 - laenge,2))
            x_deckel.append(round(laenge2 - laenge,2))
            x_deckel.append(laenge2)
            x_deckel.append(laenge2)

            z_sohle_h.append(hschoben)
            z_sohle_h.append(hschunten)
            z_deckel.append(deckeloben)
            z_deckel.append(deckelunten)
            z_sohle.append(sohleoben)
            z_sohle.append(sohleunten)

            y_label.append(round((deckeloben+sohleoben-hoehe)/2,2))
            y_label.append(round((deckelunten+sohleunten-hoehe)/2,2))

            name.append(schoben)
            name.append(schunten)
            haltnam_l.append(haltnam)
            schoben_l.append(schoben)
            schunten_l.append(schunten)
            laenge_l.append(laenge)
            entwart_l.append(entwart)
            hoehe_l.append(hoehe)
            breite_l.append(breite)
            material_l.append(material)
            strasse_l.append(strasse)
            haltungstyp_l.append(haltungstyp)
            schaechte_l.append(schoben)
            schaechte_l.append(schunten)
            schachttyp_l.append(schob_typ)
            schachttyp_l.append(schun_typ)
            deckel_l.append(deckeloben)
            deckel_l.append(deckelunten)
            sohle_l.append(sohleoben)
            sohle_l.append(sohleunten)
            entwart_s.append(entwart_o)
            entwart_s.append(entwart_u)

        y_liste = []

        #wenn alle höhen null sind dann fehlermeldung an nutzer!

        if all(num == 0 for num in x_deckel) and len(x_deckel) > 0 and all(num == 0 for num in x_sohle) and len(x_sohle) > 0:
            iface.messageBar().pushMessage("Fehler", 'Es sind keine Höhenangaben vorhanden!', level=Qgis.Critical)



        if self.max == True:
            haltungen = {}
            schaechte = {}
            if table == 'haltungen':
                for haltung in liste2:
                    sql = 'SELECT wasserstandoben,wasserstandunten FROM lau_max_el WHERE KANTE=?'
                    data = (haltung,)

                    try:
                        self.db_erg_curs.execute(sql, data)
                    except:
                        iface.messageBar().pushMessage("Error",
                                                       "Daten konnten nicht ausgelesen werden",
                                                       level=Qgis.Critical)
                    wasserstaende = self.db_erg_curs.fetchall()

                    for wasserstandoben, wasserstandunten in wasserstaende:
                        haltungen[haltung] = dict(
                            wasserstandoben=wasserstandoben, wasserstandunten=wasserstandunten
                        )

                for h in liste2:
                    y_liste.append(haltungen[h]['wasserstandoben'])
                    y_liste.append(haltungen[h]['wasserstandunten'])

            if table == 'schaechte':

                for schacht in liste:
                    sql = 'SELECT wasserstand FROM lau_max_s WHERE KNOTEN=?'
                    data = (schacht,)

                    try:
                        self.db_erg_curs.execute(sql, data)
                    except:
                        iface.messageBar().pushMessage("Error",
                                                       "Daten konnten nicht ausgelesen werden",
                                                       level=Qgis.Critical)
                    wasserstaende = self.db_erg_curs.fetchall()

                    for wasserstand in wasserstaende:
                        schaechte[schacht] = dict(
                            wasserstand=wasserstand[0])

                for s in liste:
                    y_liste.append(schaechte[s]['wasserstand'])


        farbe = 'black'
        if entwart == 'MW' or entwart =='KM' or entwart =='Mischwasser':
            farbe = 'pink'

        elif entwart == 'RW' or entwart =='KR' or entwart =='Regenwasser':
            farbe = 'blue'

        elif entwart == 'SW' or entwart =='KS' or entwart =='Schmutzwasser':
            farbe = 'red'

        schaechte_l_neu = []
        list = []
        list_deckel = []
        list_sohle = []
        list_laenge = []
        list_entwart = []
        list_hoehe = []
        list_breite = []
        list_material = []
        list_strasse = []
        list_typ = []
        s_leer =[]
        h_leer = []

        for i in schaechte_l:
            s_leer.append('')
            if i not in schaechte_l_neu:
                schaechte_l_neu.append(i)

        schachttyp_l_neu = schachttyp_l[::2]
        schachttyp_l_neu.append(schachttyp_l[-1])

        deckel_neu = deckel_l[::2]
        deckel_neu.append(deckel_l[-1])

        sohle_neu = sohle_l[::2]
        sohle_neu.append(sohle_l[-1])

        entwart_s_neu = entwart_s[::2]
        entwart_s_neu.append(entwart_s[-1])

        for i in haltnam_l:
            h_leer.append('')

        for x, y in zip(schaechte_l_neu, haltnam_l):
            list.append(x)
            list.append(y)
        list.append(schaechte_l_neu[-1])

        for x, y in zip(s_leer, laenge_l):
            list_laenge.append(x)
            list_laenge.append(y)
        list_laenge.append(s_leer[-1])

        for x, y in zip(entwart_s_neu, entwart_l):
            list_entwart.append(x)
            list_entwart.append(y)
        list_entwart.append(entwart_s_neu[-1])

        for x, y in zip(s_leer, hoehe_l):
            list_hoehe.append(x)
            list_hoehe.append(y)
        list_hoehe.append(s_leer[-1])

        for x, y in zip(s_leer, breite_l):
            list_breite.append(x)
            list_breite.append(y)
        list_breite.append(s_leer[-1])

        for x, y in zip(s_leer, material_l):
            list_material.append(x)
            list_material.append(y)
        list_material.append(s_leer[-1])

        for x, y in zip(s_leer, strasse_l):
            list_strasse.append(x)
            list_strasse.append(y)
        list_strasse.append(s_leer[-1])

        for x, y in zip(schachttyp_l_neu, haltungstyp_l):
            list_typ.append(x)
            list_typ.append(y)
        list_typ.append(schachttyp_l_neu[-1])

        for x, y in zip(deckel_neu, h_leer):
            list_deckel.append(x)
            list_deckel.append(y)
        list_deckel.append(deckel_neu[-1])

        for x, y in zip(sohle_neu, h_leer):
            list_sohle.append(x)
            list_sohle.append(y)
        list_sohle.append(sohle_neu[-1])

        data = [list_deckel, list_sohle, list_laenge, list_entwart, list_hoehe, list_breite, list_material, list_strasse, list_typ]


        columns = tuple(list)
        rows = ('Deckelhöhe [m NHN]', 'Sohlhöhe [m NHN]', 'Länge [m]', 'Entwässerungsart', 'Höhe [m]', 'Breite [m]', 'Material', 'Strasse', 'Typ')

        x = [i for i in y_deckel if i != 0]
        x2 = [i for i in y_sohle if i != 0]
        x3 = [i for i in y_sohle2 if i != 0]

        max_deckel = max(x)
        min_sohle = min(x2)
        min_sohle2 = min(x3)
        y_deckel_n = []
        y_sohle_n = []
        y_sohle2_n = []

        i = 0
        for x in y_deckel:
            if x == 0:
                y_deckel_n.append(max_deckel)
            else:
                y_deckel_n.append(y_deckel[i])
            i += 1
        i = 0
        for x in y_sohle:
            if x == 0:
                y_sohle_n.append(min_sohle)
            else:
                y_sohle_n.append(y_sohle[i])
            i += 1
        i = 0
        for x in y_sohle2:
            if x == 0:
                y_sohle2_n.append(min_sohle2)
            else:
                y_sohle2_n.append(y_sohle2[i])
            i += 1

        new_plot.plot(x_deckel, y_deckel_n, color="black", label='Deckel')
        new_plot.plot(x_sohle, y_sohle_n, color=farbe, label='Kanalsohle')
        new_plot.plot(x_sohle2, y_sohle2_n, color=farbe, label='Kanalscheitel')

        x_deckel_neu = []
        name_neu = []
        y_label_neu = []

        for i in x_deckel:
            if i not in x_deckel_neu:
                x_deckel_neu.append(i)

        for i in name:
            if i not in name_neu:
                name_neu.append(i)

        for i in y_label:
            if i not in y_label_neu:
                y_label_neu.append(i)


        for x, y, nam in zip(x_deckel_neu, y_label_neu, name_neu):
            plt.annotate(nam, (x, y),
                         textcoords="offset points",
                         xytext=(-10, 0),
                         rotation=90,
                         ha='center')

        if all(num == 0 for num in y_liste) and len(y_liste) > 0:
            iface.messageBar().pushMessage("Fehler", 'Es sind keine maximalen Wasserstände vorhanden!', level=Qgis.Critical)
        else:
            if len(y_liste) > 0 and table == 'schaechte':
                new_plot.plot(x_deckel_neu, y_liste, color="blue", label='maximaler Wasserstand')

            if len(y_liste) > 0 and table == 'haltungen':

                new_plot.plot(x_deckel[::2], y_liste, color="blue", label='maximaler Wasserstand')

        # wenn die höhen null sind schachthöhen =max und min werte setzen und farbe grau
        y1 = [i for i in y_sohle if i != 0]
        y2 = [i for i in y_deckel if i != 0]

        min_sohle = min(y1)
        max_deckel = max(y2)

        y_sohle_2 = []
        y_deckel_3 = []
        x_deckel_2 = []
        delete = []

        i = 0
        for x, y in zip(y_sohle, y_deckel_n):
            if y_sohle[i] == 0.0 or y_deckel_n[i] == 0.0:
                y_sohle_2.append(min_sohle)
                y_deckel_3.append(max_deckel)
                x_deckel_2.append(x_deckel[i])
                delete.append(i)
            i += 1

        for x in delete[::-1]:
            y_sohle.pop(x)
            y_deckel_n.pop(x)
            x_deckel.pop(x)

        plt.vlines(x_deckel, y_sohle, y_deckel_n, color="red", linestyles='solid', label='Schacht', linewidth=5)
        plt.vlines(x_deckel_2, y_sohle_2, y_deckel_3, color="gray", linestyles='solid', label='Schacht', linewidth=5)


        x_min = -0.5
        y_min = float(min(y_sohle)) - 0.5
        y_max = float(max(y_deckel)) + 0.5
        #x_max = laenge2 / massstab + 2.5 + pointx
        x_max = laenge2 + 2.5
        x=[x_min, x_max]
        y=[y_min, y_min]
        plt.hlines(y_min, x_min, x_max+5, color="grey", linestyles='solid')
        plt.hlines(y_min, x_min-60, x_max+5, color="grey", linestyles='solid')
        plt.hlines(y_min-0.6 , x_min - 60, x_max+5, color="grey", linestyles='solid')
        plt.hlines(y_min - 1.1, x_min - 60, x_max+5, color="grey", linestyles='solid')
        plt.hlines(y_min - 1.6, x_min - 60, x_max+5, color="grey", linestyles='solid')
        plt.hlines(y_min - 2.1, x_min - 60, x_max+5, color="grey", linestyles='solid')
        plt.hlines(y_min - 2.6, x_min - 60, x_max+5, color="grey", linestyles='solid')
        plt.hlines(y_min - 3.1, x_min - 60, x_max+5, color="grey", linestyles='solid')

        plt.annotate("Deckelhöhe [m ü. NHN]", (x_min-30, y_min-0.4), textcoords="offset points", xytext=(-10, 0), ha='center')
        plt.annotate("Schachtname", (x_min - 40, y_min - 0.9), textcoords="offset points", xytext=(-10, 0),
                     ha='center')
        plt.annotate("Sohlehöhe Schacht [m ü. NHN]", (x_min - 30, y_min - 1.4), textcoords="offset points", xytext=(-10, 0),
                     ha='center')
        plt.annotate("Sohlhöhe Haltung [m ü. NHN]", (x_min - 30, y_min - 1.9), textcoords="offset points", xytext=(-10, 0),
                     ha='center')
        plt.annotate("Länge [m]", (x_min - 30, y_min - 2.5), textcoords="offset points", xytext=(-10, 0),
                     ha='center')
        plt.annotate("Nennweite / Material [mm]", (x_min - 30, y_min - 3), textcoords="offset points", xytext=(-10, 0),
                     ha='center')


        z_sohle_neu = []
        for i in z_sohle:
            if i not in z_sohle_neu:
                z_sohle_neu.append(i)
        z_deckel_neu = []
        for i in z_deckel:
            if i not in z_deckel_neu:
                z_deckel_neu.append(i)


        for i, j, x, y in zip(x_deckel_neu, name_neu, z_deckel_neu, z_sohle_neu):
            plt.vlines(i, y_min, y_min-3.1, color="grey", linestyles='solid')

            plt.annotate(x, (i+0.1, y_min - 0.4), bbox=dict(facecolor='white', edgecolor='none'),
                          ha='center')

            plt.annotate(j, (i +0.1, y_min - 0.9), bbox=dict(facecolor='white', edgecolor='none'),
                          ha='center')

            plt.annotate(y, (i +0.1, y_min - 1.4), bbox=dict(facecolor='white', edgecolor='none'),
                          ha='center')

        x = 0

        for i, j in zip(x_deckel_neu, z_sohle_h):
            # so verschieben, dass die TExte passend stehen
            if x % 2:
                plt.annotate(j, (i +0.1, y_min - 1.9), bbox=dict(facecolor='white', edgecolor='none'),
                              ha='center')
            else:
                plt.annotate(j, (i +0.1, y_min - 1.9), bbox=dict(facecolor='white', edgecolor='none'),
                              ha='center')
            x += 1

        laenge = laenge_l
        dn = breite_l
        material = material_l

        x_mitte = []
        x = 0
        while x + 1 < len(x_deckel_neu):
            m = (x_deckel_neu[x] + x_deckel_neu[x + 1]) / 2
            x += 1
            x_mitte.append(m)

        # mittig zwischen zwei Schächte schreiben Länge, Nennweite und Material, Gefälle, Stationierung
        for i, k, l, m in zip(x_mitte, laenge, dn, material):
            plt.annotate(k, (i , y_min - 2.5), textcoords="offset points",
                         xytext=(-10, 0), ha='center')

            plt.annotate(str(l * 1000), (i, y_min - 3), textcoords="offset points",
                         xytext=(-10, 0), ha='center')


        plt.xlabel('Länge [m]')
        plt.ylabel('Höhe [m NHN]')
        new_plot.legend()
        plt.tight_layout()
        # plt.table(cellText=data, rowLabels=rows, colLabels=columns, loc='bottom', bbox=[0.0, -0.65, 1, 0.45], cellLoc='center')
        # plt.subplots_adjust(top=0.98,
        #                      bottom=0.4,
        #                      left=0.13,
        #                      right=0.99,
        #                      hspace=0.2,
        #                      wspace=0.2)

        self.auswahl[figure.number] = self.selected

    def show(self):
        """selektierte Elemente anzeigen"""
        layer = iface.activeLayer()
        layer.selectByExpression("pk in {}".format(tuple(self.features)))


    def cad(self):
        """Längsschnitt in CAD zeichnen"""
        points = self.point.split(",", 1)
        massstab_liste = self.massstab.split(":", 1)

        #Koordinaten für Einfügepunkt
        pointx = float(points[0])
        pointy = float(points[1])
        # Maßstab
        massstab = float(massstab_liste[1])

        layer = iface.activeLayer()
        x = layer.source()

        # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)

        # selektierte elemente anzeigen

        figure = self.fig
        self.selected = self.auswahl[figure.number]

        liste = []
        liste2 = []

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.Critical)
            return

        if table == 'schaechte':
            for f in self.selected:
                x = f['schnam']
                liste.append(x)

        if table == 'haltungen':
            for f in self.selected:
                x = f['schoben']
                x2 = f['schunten']
                x3 = f['haltnam']
                liste2.append(x3)
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)

        route = find_route(self.db_qkan, liste)
        logger.debug(f'Fehler in cad. liste: {liste}')
        logger.debug(f'route: {route}')

        if route is None:
            iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente Ausgewählt', level=Qgis.Critical)
            return

        if table == 'schaechte':
            liste = []
            for f in route[0]:
                liste.append(f)

        if table == 'haltungen':
            liste = []
            for x in route[0]:
                liste.append(x)
            liste2 = []
            for y in route[1]:
                liste2.append(y)

        x_sohle = []
        y_sohle = []
        x_sohle2 = []
        y_sohle2 = []
        x_deckel = []
        y_deckel = []
        y_label = []
        name = []
        z_deckel = []
        z_sohle = []
        z_sohle_h = []

        haltnam_l = ['Haltungsname']
        schoben_l = ['Schacht oben']
        schunten_l = ['Schacht unten']
        laenge_l = ['Laenge [m]']
        entwart_l = ['Entwaesserungsart']
        hoehe_l = ['Hoehe [m]']
        breite_l = ['Breite [m]']
        material_l = ['Material']
        strasse_l = ['Strasse']
        haltungstyp_l = ['Typ']

        sel = '), ('.join(
            [f"'{num}', {el}" for el, num in enumerate(route[1])])  # sel = ('15600000-45', 0), ('15600000-50', 1), ...)
        sql = f"""
                    SELECT
                        h.schoben,
                        h.hoehe,
                        h.schunten,
                        h.laenge,
                        schob.deckelhoehe,
                        schob.sohlhoehe,
                        schun.deckelhoehe,
                        schun.sohlhoehe,
                        h.entwart,
                        h.haltnam,
                        h.breite,
                        h.material,
                        h.strasse,
                        h.haltungstyp,
                        h.sohleoben,
                        h.sohleunten,
                        schob.knotentyp,
                        schun.knotentyp,
                        schob.entwart,
                        schun.entwart,
                        sum(h.laenge) OVER (ORDER BY sel.column2 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as laenge_sum
                    FROM haltungen AS h
                    INNER JOIN schaechte AS schob ON schob.schnam = h.schoben
                    INNER JOIN schaechte AS schun ON schun.schnam = h.schunten
                    INNER JOIN (VALUES ({sel})) AS sel ON sel.column1 = h.haltnam
                    """

        if not self.db_qkan.sql(sql, "laengsschnitt.3"):
            logger.error(f"{__file__}: Fehler in laengsschnitt.3: Datenbankzugriff nicht möglich")
            return 'nicht erstellt'

        for attr in self.db_qkan.fetchall():
            (
                schoben, hoehe, schunten, laenge, deckeloben, sohleoben, deckelunten, sohleunten, entwart,
                haltnam, breite, material, strasse, haltungstyp, haltung_sohle_o, haltung_sohle_u,
                schob_typ, schun_typ, entwart_o, entwart_u, laenge2
            ) = attr

            hschoben = sohleoben
            hschunten = sohleunten

            if int(haltung_sohle_o) == 0:
                haltung_sohle_o = sohleoben
            if int(haltung_sohle_u) == 0:
                haltung_sohle_u = sohleunten

            y_sohle.append(sohleoben+pointy)
            y_sohle.append(haltung_sohle_o+pointy)
            y_sohle.append(haltung_sohle_u+pointy)
            y_sohle.append(sohleunten+pointy)
            x_sohle.append(((laenge2 - laenge)/massstab)+pointx)
            x_sohle.append(((laenge2 - laenge)/massstab)+pointx)
            x_sohle.append((laenge2/massstab)+pointx)
            x_sohle.append((laenge2/massstab)+pointx)

            if sohleoben > 0:
                y_sohle2.append(sohleoben + hoehe+pointy)
            else:
                y_sohle2.append(sohleoben+pointy)
            if haltung_sohle_o > 0:
                y_sohle2.append(haltung_sohle_o + hoehe+pointy)
            else:
                y_sohle2.append(haltung_sohle_o+pointy)
            if haltung_sohle_u > 0:
                y_sohle2.append(haltung_sohle_u + hoehe+pointy)
            else:
                y_sohle2.append(haltung_sohle_u+pointy)
            if sohleunten > 0:
                y_sohle2.append(sohleunten + hoehe+pointy)
            else:
                y_sohle2.append(sohleunten+pointy)
            x_sohle2.append(((laenge2 - laenge)/massstab)+pointx)
            x_sohle2.append(((laenge2 - laenge)/massstab)+pointx)
            x_sohle2.append((laenge2/massstab)+pointx)
            x_sohle2.append((laenge2/massstab)+pointx)


            z_sohle_h.append(hschoben)
            z_sohle_h.append(hschunten)

            y_deckel.append(deckeloben + pointy)
            y_deckel.append(deckeloben + pointy)
            y_deckel.append(deckelunten + pointy)
            y_deckel.append(deckelunten + pointy)
            x_deckel.append(round(((laenge2 - laenge)/massstab)+pointx,2))
            x_deckel.append(round(((laenge2 - laenge)/massstab)+pointx,2))
            x_deckel.append(round((laenge2 / massstab) + pointx,2))
            x_deckel.append(round((laenge2 / massstab) + pointx,2))


            y_label.append(round(((deckeloben + sohleoben) / 2)+pointy,2))
            y_label.append(round(((deckelunten + sohleunten) / 2)+pointy,2))

            name.append(schoben)
            name.append(schunten)
            z_deckel.append(deckeloben)
            z_deckel.append(deckelunten)
            z_sohle.append(sohleoben)
            z_sohle.append(sohleunten)

            haltnam_l.append(haltnam)
            schoben_l.append(schoben)
            schunten_l.append(schunten)
            laenge_l.append(laenge)
            entwart_l.append(entwart)
            hoehe_l.append(hoehe)
            breite_l.append(breite)
            material_l.append(material)
            strasse_l.append(strasse)
            haltungstyp_l.append(haltungstyp)

        y_liste = []

        if all(num == 0 for num in x_deckel) and len(x_deckel) > 0 and all(num == 0 for num in x_sohle) and len(x_sohle) > 0:
            iface.messageBar().pushMessage("Fehler", 'Es sind keine Höhenangaben vorhanden!', level=Qgis.Critical)

        x = [i for i in y_deckel if i != 0]
        x2 = [i for i in y_sohle if i != 0]
        x3 = [i for i in y_sohle2 if i != 0]

        max_deckel = max(x)
        min_sohle = min(x2)
        min_sohle2 = min(x3)
        y_deckel_n = []
        y_sohle_n = []
        y_sohle2_n = []

        i = 0
        for x in y_deckel:
            if x == 0:
                y_deckel_n.append(max_deckel)
            else:
                y_deckel_n.append(y_deckel[i])
            i += 1
        i = 0
        for x in y_sohle:
            if x == 0:
                y_sohle_n.append(min_sohle)
            else:
                y_sohle_n.append(y_sohle[i])
            i += 1
        i = 0
        for x in y_sohle2:
            if x == 0:
                y_sohle2_n.append(min_sohle2)
            else:
                y_sohle2_n.append(y_sohle2[i])
            i += 1

        # wenn die höhen null sind schachthöhen =max und min werte setzen und farbe grau
        y1 = [i for i in y_sohle if i != 0]
        y2 = [i for i in y_deckel if i != 0]

        min_sohle = min(y1)
        max_deckel = max(y2)

        y_sohle_2 = []
        y_deckel_3 = []
        x_deckel_2 = []
        delete = []

        i = 0
        for x, y in zip(y_sohle, y_deckel_n):
            if y_sohle[i] == 0.0 or y_deckel_n[i] == 0.0:
                y_sohle_2.append(min_sohle)
                y_deckel_3.append(max_deckel)
                x_deckel_2.append(x_deckel[i])
                delete.append(i)
            i += 1

        for x in delete[::-1]:
            y_sohle.pop(x)
            y_deckel_n.pop(x)
            x_deckel.pop(x)

        if self.max == True:
            haltungen = {}
            schaechte = {}
            if table == 'haltungen':
                for haltung in liste2:
                    sql = 'SELECT wasserstandoben,wasserstandunten FROM lau_max_el WHERE KANTE=?'
                    data = (haltung,)

                    try:
                        self.db_erg_curs.execute(sql, data)
                    except:
                        iface.messageBar().pushMessage("Error",
                                                       "Daten konnten nicht ausgelesen werden",
                                                       level=Qgis.Critical)
                    wasserstaende = self.db_erg_curs.fetchall()

                    for wasserstandoben, wasserstandunten in wasserstaende:
                        haltungen[haltung] = dict(
                            wasserstandoben=wasserstandoben, wasserstandunten=wasserstandunten
                        )

                for h in liste2:
                    y_liste.append(haltungen[h]['wasserstandoben'])
                    y_liste.append(haltungen[h]['wasserstandunten'])

            if table == 'schaechte':
                for schacht in liste:
                    sql = 'SELECT wasserstand FROM lau_max_s WHERE KNOTEN=?'
                    data = (schacht,)

                    try:
                        self.db_erg_curs.execute(sql, data)
                    except:
                        iface.messageBar().pushMessage("Error",
                                                       "Daten konnten nicht ausgelesen werden",
                                                       level=Qgis.Critical)
                    wasserstaende = self.db_erg_curs.fetchall()

                    for wasserstand in wasserstaende:
                        schaechte[schacht] = dict(
                            wasserstand=wasserstand[0])

                for s in liste:
                    y_liste.append(schaechte[s]['wasserstand'])

        farbe = "-FARBE" +"\n"+ "7\n" "\n"
        if entwart == 'MW' or entwart == 'KM' or entwart == 'Mischwasser':
            farbe = "-FARBE" +"\n"+ "6\n" "\n"

        elif entwart == 'RW' or entwart == 'KR' or entwart == 'Regenwasser':
            farbe = "-FARBE" +"\n"+ "5\n" "\n"

        elif entwart == 'SW' or entwart == 'KS' or entwart == 'Schmutzwasser':
            farbe = "-FARBE" +"\n"+ "1\n" "\n"

        # autocad benötigt andere daten als matplotlib (Koordinatenpaare erwartet!)
        deckel = "LINIE"
        scheitel = "LINIE"
        sohle = "LINIE"
        max_wasser = "LINIE"

        x_deckel_neu = []

        for i in x_deckel:
            if i not in x_deckel_neu:
                x_deckel_neu.append(i)

        # deckelkoordinaten
        for i, j in zip(x_deckel, y_deckel_n):
            deckel += " " + str(i) + "," + str(j)

        deckel += "\n" "\n"

        # scheitelkoordinaten
        for i, j in zip(x_sohle2, y_sohle2_n):
            scheitel += " " + str(i) + "," + str(j)

        scheitel += "\n" "\n"

        # sohlenkoordinaten
        for i, j in zip(x_sohle, y_sohle_n):
            sohle += " " + str(i) + "," + str(j)

        sohle += "\n" "\n"

        #max_wasserstand
        if len(y_liste) > 0 and table == 'schaechte':
            for i, j in zip(x_deckel_neu, y_liste):
                max_wasser += " " + str(i) + "," + str(float(j)+pointy)

        #new_plot.plot(x_deckel_neu, y_liste, color="blue", label='maximaler Wasserstand')

        if len(y_liste) > 0 and table == 'haltungen':
            for i, j in zip(x_deckel, y_liste):
                max_wasser += " " + str(i) + "," + str(float(j)+pointy)

        max_wasser += "\n" "\n"


        #cad anbindung starten
        acad = None
        doc = None

        try:
            acad = win32com.client.Dispatch('AutoCAD.Application')
            acad.Visible = True
        except WindowsError:
            print('Autocad wird gestartet. Das kann ca. eine halbe Minute dauern...')
            acad = win32com.client.CreateObject('AutoCAD.Application')
            acad = win32com.client.GetActiveObject('AutoCAD.Application')  # scheint zwar doppelt,
            # aber sonst erscheint ein Fehler
            acad.Visible = True
        except pywintypes.error as e:
            print(e)
        except BaseException as e:
            print(e)

        # Prüfen, ob schon eine Datei offen ist. Falls nicht, wird eine neue Datei angelegt.
        if acad is None:
            iface.messageBar().pushMessage("Error", "Autocad ist nicht installiert!", level=Qgis.Critical)
        elif acad.Documents.Count > 0:
            doc = acad.ActiveDocument
            print("Eine Datei ist bereits offen")
        else:
            print("Eine neue Datei wird angelegt")
            doc = acad.Documents.Add()

        if doc is not None:
            #print("Bitte klicken Sie in der AutoCAD-Datei auf einen Punkt!")
            #x0, y0, z0 = doc.Utility.GetPoint()  # z0 wird nicht benötigt
            #print('Geklickt: ({},{})'.format(x0, y0))

            #längssschnitt in cad erstellen

            # mit "FARBE" die Farbe der zu zeichnenden Linie ändern
            doc.SendCommand("-FARBE" + "\n" + "7\n" "\n")
            doc.SendCommand(deckel)
            doc.SendCommand(farbe)
            doc.SendCommand(scheitel)
            doc.SendCommand(farbe)
            doc.SendCommand(sohle)
            doc.SendCommand("-FARBE" + "\n" + "5\n" "\n")
            if len(y_liste) > 0:
                doc.SendCommand(max_wasser)

            # schacht linien einzeichnen
            for i, j, z in zip(x_deckel, y_sohle, y_deckel_n):
                schacht = "LINIE"
                schacht += " " + str(i) + "," + str(j)
                schacht += " " + str(i) + "," + str(z)
                schacht += "\n" "\n"
                doc.SendCommand("-FARBE" + "\n" + "1\n" "\n")
                doc.SendCommand(schacht)

            # schacht linien einzeichnen
            for i, j, z in zip(x_deckel_2, y_sohle_2, y_deckel_3):
                schacht = "LINIE"
                schacht += " " + str(i) + "," + str(j)
                schacht += " " + str(i) + "," + str(z)
                schacht += "\n" "\n"
                doc.SendCommand("-FARBE" + "\n" + "1\n" "\n")
                doc.SendCommand(schacht)

            # Graphen zeichnen lassen
            doc.SendCommand("-FARBE" + "\n" + "7\n" "\n")
            x_min = -2.5 + pointx
            y_min = float(min(y_sohle)) - 2.5
            y_max = float(max(y_deckel)) + 2.5
            x_max = laenge2 / massstab + 2.5 + pointx
            x_linie = "LINIE " + str(x_min - 5) + "," + str(y_min) + " " + str(x_max) + "," + str(y_min) + "\n" + "\n"
            doc.SendCommand(x_linie)
            x_linie2 = "LINIE " + str(x_min - 5) + "," + str(y_min - 1.0) + " " + str(x_max) + "," + str(
                y_min - 1.0) + "\n" + "\n"
            doc.SendCommand(x_linie2)
            x_linie3 = "LINIE " + str(x_min - 5) + "," + str(y_min - 2.5) + " " + str(x_max) + "," + str(
                y_min - 2.5) + "\n" + "\n"
            doc.SendCommand(x_linie3)
            x_linie4 = "LINIE " + str(x_min - 5) + "," + str(y_min - 3.5) + " " + str(x_max) + "," + str(
                y_min - 3.5) + "\n" + "\n"
            doc.SendCommand(x_linie4)
            x_linie5 = "LINIE " + str(x_min - 5) + "," + str(y_min - 4.5) + " " + str(x_max) + "," + str(
                y_min - 4.5) + "\n" + "\n"
            doc.SendCommand(x_linie5)
            x_linie6 = "LINIE " + str(x_min - 5) + "," + str(y_min - 5.5) + " " + str(x_max) + "," + str(
                y_min - 5.5) + "\n" + "\n"
            doc.SendCommand(x_linie6)
            x_linie7 = "LINIE " + str(x_min - 5) + "," + str(y_min - 6.5) + " " + str(x_max) + "," + str(
                y_min - 6.5) + "\n" + "\n"
            doc.SendCommand(x_linie7)

            beschr = "-TEXT" + "\n" + str(x_min - 5) + "," + str(
                y_min - 0.5) + "\n" + "0.25" + "\n" + "0" + "\n" + "Deckelhöhe [m ü. NHN]" + "\n" "\n"
            doc.SendCommand(beschr)
            beschr = "-TEXT" + "\n" + str(x_min - 5) + "," + str(
                y_min - 2) + "\n" + "0.25" + "\n" + "0" + "\n" + "Schachtname" + "\n" "\n"
            doc.SendCommand(beschr)
            beschr = "-TEXT" + "\n" + str(x_min - 5) + "," + str(
                y_min - 3) + "\n" + "0.25" + "\n" + "0" + "\n" + "Sohlehöhe Schacht [m ü. NHN]" + "\n" "\n"
            doc.SendCommand(beschr)
            beschr = "-TEXT" + "\n" + str(x_min - 5) + "," + str(
                y_min - 4) + "\n" + "0.25" + "\n" + "0" + "\n" + "Sohlhöhe Haltung [m ü. NHN]" + "\n" "\n"
            doc.SendCommand(beschr)
            beschr = "-TEXT" + "\n" + str(x_min - 5) + "," + str(
                y_min - 5) + "\n" + "0.25" + "\n" + "0" + "\n" + "Länge [m]" + "\n" "\n"
            doc.SendCommand(beschr)
            beschr = "-TEXT" + "\n" + str(x_min - 5) + "," + str(
                y_min - 6) + "\n" + "0.25" + "\n" + "0" + "\n" + "Nennweite / Material [mm]" + "\n" "\n"
            doc.SendCommand(beschr)

            # TODO: Kasten um die Schrift zeichen

            # zu den eingefügten Daten zoomen
            doc.SendCommand("ZOOM" + "\n" + "A" + "\n")

            # regelmäßige Striche für die Beschriftung der Graphen erzeugen

            x_deckel_neu = x_deckel[::2]
            x_deckel_neu.append(x_deckel[-1])
            name_neu = name[::2]
            name_neu.append(name[-1])
            z_sohle_neu = z_sohle[::2]
            z_sohle_neu.append(z_sohle[-1])
            z_deckel_neu = z_deckel[::2]
            z_deckel_neu.append(z_deckel[-1])

            # iface.messageBar().pushMessage("Fehler", str(z_sohle), level=Qgis.Critical)
            # iface.messageBar().pushMessage("Fehler", str(z_sohle_neu), level=Qgis.Critical)

            for i, j, x, y in zip(x_deckel_neu, name_neu, z_deckel_neu, z_sohle_neu):
                linien = "LINIE"
                linien += " " + str(i) + "," + str(y_min)
                linien += " " + str(i) + "," + str(y_min - 7.5)
                linien += "\n" "\n"
                doc.SendCommand(linien)

                text_deckelhoehe = "-TEXT" + "\n" + str(i - 0.3) + "," + str(
                    y_min - 0.5) + "\n" + "0.125" + "\n" + "90" + "\n" + str(x) + "\n" "\n"
                doc.SendCommand(text_deckelhoehe)
                text_name = "-TEXT" + "\n" + str(i - 1.5) + "," + str(
                    y_min - 2) + "\n" + "0.15" + "\n" + "0" + "\n" + str(j) + "\n" "\n"
                doc.SendCommand(text_name)
                text_sohlhoehe_s = "-TEXT" + "\n" + str(i - 1.5) + "," + str(
                    y_min - 3) + "\n" + "0.125" + "\n" + "0" + "\n" + str(y) + "\n" "\n"
                doc.SendCommand(text_sohlhoehe_s)

            x = 0
            # iface.messageBar().pushMessage("Fehler", str(x_deckel), level=Qgis.Critical)
            # iface.messageBar().pushMessage("Fehler", str(z_sohle_h), level=Qgis.Critical)

            for i, j in zip(x_deckel, z_sohle_h):
                # so verschieben, dass die TExte passend stehen
                if x % 2:
                    text_sohlhoehe_h = "-TEXT" + "\n" + str(i - 1.5) + "," + str(
                        y_min - 4) + "\n" + "0.125" + "\n" + "0" + "\n" + str(j) + "\n" "\n"
                    doc.SendCommand(text_sohlhoehe_h)
                else:
                    text_sohlhoehe_h = "-TEXT" + "\n" + str(i + 0.5) + "," + str(
                        y_min - 4) + "\n" + "0.125" + "\n" + "0" + "\n" + str(j) + "\n" "\n"
                    doc.SendCommand(text_sohlhoehe_h)
                x += 1

            laenge = laenge_l
            laenge.pop(0)
            dn = breite_l
            dn.pop(0)
            material = material_l
            material.pop(0)

            x_mitte = []
            x = 0
            while x + 1 < len(x_deckel_neu):
                m = (x_deckel_neu[x] + x_deckel_neu[x + 1]) / 2
                x += 1
                x_mitte.append(m)

            # mittig zwischen zwei Schächte schreiben Länge, Nennweite und Material, Gefälle, Stationierung
            for i, k, l, m in zip(x_mitte, laenge, dn, material):
                text_laenge = "-TEXT" + "\n" + str(i) + "," + str(y_min - 5) + "\n" + "0.125" + "\n" + "0" + "\n" + str(
                    k) + "\n" "\n"
                doc.SendCommand(text_laenge)
                text_dn = "-TEXT" + "\n" + str(i) + "," + str(y_min - 6) + "\n" + "0.125" + "\n" + "0" + "\n" + str(
                    l * 1000) + " " + str(m) + "\n" "\n"
                doc.SendCommand(text_dn)
                # text_material = "-TEXT" + "\n" + str(i) + "," + str(y_min - 8) + "\n" + "0.25" + "\n" + "0" + "\n" + str(m) + "\n" "\n"
                # doc.SendCommand(text_material)


    def ganglinie(self):
        figure = self.fig_3
        figure.clear()
        plt.figure(figure.number)
        new_plot = figure.add_subplot(111)

        # aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)

        # selektierte elemente anzeigen
        self.selected = layer.selectedFeatures()
        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste = []

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.Critical)
            return

        if table == 'schaechte':
            for f in self.selected:
                x = f['schnam']
                liste.append(x)

        if table == 'haltungen':
            for f in self.selected:
                x = f['haltnam']
                liste.append(x)

        schaechte = {}
        haltungen = {}

        if table == 'schaechte':
            for schacht in liste:
                sql = '''SELECT es.zeitpunkt AS zeitpunkt,
                          es.zufluss AS zufluss,
                          es.wasserstand AS wasserstand,
                          es.durchfluss AS durchfluss,
                          es.wasserstand - kn.Sohlhoehe AS wassertiefe  
                   FROM LAU_GL_S AS es
                   INNER JOIN (
                     SELECT Name, Sohlhoehe FROM Schacht UNION
                     SELECT Name, Sohlhoehe FROM Speicherschacht UNION
                     SELECT Name, Sohlhoehe FROM Auslass
                   ) AS kn
                   ON es.Knoten = kn.Name
                   WHERE es.Knoten=?'''
                data = (schacht,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.Critical)

                res = self.db_erg_curs.fetchall()
                for zeitpunkt_t, zufluss, wasserstand, durchfluss, wassertiefe in res:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       "Konvertierung vom Zeitpunkt fehlgeschlagen",
                                                       level=Qgis.Critical)
                    if schaechte.get(zeitpunkt) is None:
                        schaechte[zeitpunkt] = {}
                    schaechte[zeitpunkt][schacht] = dict(
                        zufluss=zufluss, durchfluss=durchfluss, wasserstand=wasserstand, wassertiefe=wassertiefe,
                    )

        if table == 'haltungen':
            for haltung in liste:
                sql='''SELECT zeitpunkt,auslastung,durchfluss,geschwindigkeit,wasserstand AS wassertiefe FROM lau_gl_el WHERE KANTE=?'''
                data = (haltung,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.Critical)

                res = self.db_erg_curs.fetchall()
                for zeitpunkt_t, auslastung, durchfluss, geschwindigkeit, wassertiefe in res:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       "Konvertierung vom Zeitpunkt fehlgeschlagen",
                                                       level=Qgis.Critical)
                    if haltungen.get(zeitpunkt) is None:
                        haltungen[zeitpunkt] = {}
                    haltungen[zeitpunkt][haltung] = dict(
                        auslastung=auslastung,
                        durchfluss=durchfluss,
                        geschwindigkeit=geschwindigkeit,
                        wassertiefe=wassertiefe,
                    )


        if table == 'haltungen':

            if self.ausgabe == 'Durchfluss':
                plt.xlabel('Zeit')
                plt.ylabel('m³/s')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['durchfluss'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()

            if self.ausgabe == 'Geschwindigkeit':
                plt.xlabel('Zeit')
                plt.ylabel('m/s')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['geschwindigkeit'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()

            if self.ausgabe == 'Auslastung':
                plt.xlabel('Zeit')
                plt.ylabel('%')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['auslastung'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()

            if self.ausgabe == 'Wassertiefe':
                plt.xlabel('Zeit')
                plt.ylabel('m')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['wassertiefe'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()

        if table == 'schaechte':
            if self.ausgabe == 'Zufluss':
                plt.xlabel('Zeit')
                plt.ylabel('m³/s')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['zufluss'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()



            if self.ausgabe == 'Wasserstand':
                plt.xlabel('Zeit')
                plt.ylabel('m NN')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['wasserstand'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()

            if self.ausgabe == 'Wassertiefe':
                plt.xlabel('Zeit')
                plt.ylabel('m')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['wassertiefe'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()

            if self.ausgabe == 'Durchfluss':
                plt.xlabel('Zeit')
                plt.ylabel('m³/s"')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['durchfluss'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend()


    def laengs(self):
        label_4 = self.label_4
        horizontalSlider_3 = self.horizontalSlider_3
        anf = self.anf
        geschw = self.geschw

        # hier wird der animierte Längsschnitt in das Fenster gezeichnet

        figure = self.fig_2
        figure.clear()
        plt.clf()
        plt.figure(figure.number)


        #ax = figure.add_subplot(1, 1, 1)
        new_plot = figure.add_subplot(111)

        #aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        #mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)

        t=None

        #selektierte elemente anzeigen
        self.selected = layer.selectedFeatures()
        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste=[]
        liste2=[]

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.Critical)
            return

        if table == 'schaechte':
            for f in self.selected:
                x = f['schnam']
                liste.append(x)

        if table == 'haltungen':
            for f in self.selected:
                x = f['schoben']
                x2 = f['schunten']
                x3 = f['haltnam']
                liste2.append(x3)
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)

        route = find_route(self.db_qkan, liste)
        logger.debug(f'Fehler in laengs. liste: {liste}')
        logger.debug(f'route: {route}')

        if route is None:
            iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente Ausgewählt', level=Qgis.Critical)
            return 'nicht erstellt'

        if table == 'schaechte':
            liste = []
            for f in route[0]:
                liste.append(f)

        if table == 'haltungen':
            liste = []
            for x in route[0]:
                liste.append(x)
            liste2 = []
            for y in route[1]:
                liste2.append(y)
        logger.debug(f'zeichnen.ausgewaehlt.3: {liste}')
        logger.debug(f'route: {route}')
        # route = (['2747.1J55', '2747.1J56', '2747.1J57'], ['M2747.1J55', 'M2747.1J56'])
        x_sohle = []
        y_sohle = []
        x_sohle2 = []
        y_sohle2 = []
        x_deckel = []
        y_deckel = []
        y_label = []
        name = []
        haltnam_l = []
        schoben_l = []
        schunten_l = []
        laenge_l = []
        entwart_l = []
        hoehe_l = []
        breite_l = []
        material_l = []
        strasse_l = []
        haltungstyp_l = []

        sel = '), ('.join(
            [f"'{num}', {el}" for el, num in enumerate(route[1])])  # sel = ('15600000-45', 0), ('15600000-50', 1), ...)
        sql = f"""
                    SELECT
                        h.schoben,
                        h.hoehe,
                        h.schunten,
                        h.laenge,
                        schob.deckelhoehe,
                        schob.sohlhoehe,
                        schun.deckelhoehe,
                        schun.sohlhoehe,
                        h.entwart,
                        h.haltnam,
                        h.breite,
                        h.material,
                        h.strasse,
                        h.haltungstyp,
                        h.sohleoben,
                        h.sohleunten,
                        schob.knotentyp,
                        schun.knotentyp,
                        schob.entwart,
                        schun.entwart,
                        sum(h.laenge) OVER (ORDER BY sel.column2 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as laenge_sum
                    FROM haltungen AS h
                    INNER JOIN schaechte AS schob ON schob.schnam = h.schoben
                    INNER JOIN schaechte AS schun ON schun.schnam = h.schunten
                    INNER JOIN (VALUES ({sel})) AS sel ON sel.column1 = h.haltnam
                    """

        if not self.db_qkan.sql(sql, "laengsschnitt.zeichnen.4"):
            logger.error(f"{__file__}: Fehler in laengsschnitt.zeichnen.4: Datenbankzugriff nicht möglich")
            return 'nicht erstellt'

        for attr in self.db_qkan.fetchall():
            (
                schoben, hoehe, schunten, laenge, deckeloben, sohleoben, deckelunten, sohleunten, entwart,
                haltnam, breite, material, strasse, haltungstyp, haltung_sohle_o, haltung_sohle_u,
                schob_typ, schun_typ, entwart_o, entwart_u, laenge2
            ) = attr

            if int(haltung_sohle_o) == 0:
                haltung_sohle_o = sohleoben
            if int(haltung_sohle_u) == 0:
                haltung_sohle_u = sohleunten

            y_sohle.append(sohleoben)
            y_sohle.append(haltung_sohle_o)
            y_sohle.append(haltung_sohle_u)
            y_sohle.append(sohleunten)
            x_sohle.append(laenge2 - laenge)
            x_sohle.append(laenge2 - laenge)
            x_sohle.append(laenge2)
            x_sohle.append(laenge2)

            if sohleoben > 0:
                y_sohle2.append(sohleoben + hoehe)
            else:
                y_sohle2.append(sohleoben)
            if haltung_sohle_o > 0:
                y_sohle2.append(haltung_sohle_o + hoehe)
            else:
                y_sohle2.append(haltung_sohle_o)
            if haltung_sohle_u > 0:
                y_sohle2.append(haltung_sohle_u + hoehe)
            else:
                y_sohle2.append(haltung_sohle_u)
            if sohleunten > 0:
                y_sohle2.append(sohleunten + hoehe)
            else:
                y_sohle2.append(sohleunten)
            x_sohle2.append(laenge2 - laenge)
            x_sohle2.append(laenge2 - laenge)
            x_sohle2.append(laenge2)
            x_sohle2.append(laenge2)

            y_deckel.append(deckeloben)
            y_deckel.append(deckeloben)
            y_deckel.append(deckelunten)
            y_deckel.append(deckelunten)
            x_deckel.append(laenge2 - laenge)
            x_deckel.append(laenge2 - laenge)
            x_deckel.append(laenge2)
            x_deckel.append(laenge2)

            y_label.append((deckeloben + sohleoben - hoehe) / 2)
            y_label.append((deckelunten + sohleunten - hoehe) / 2)

            name.append(schoben)
            name.append(schunten)
            haltnam_l.append(haltnam)
            schoben_l.append(schoben)
            schunten_l.append(schunten)
            laenge_l.append(laenge)
            entwart_l.append(entwart)
            hoehe_l.append(hoehe)
            breite_l.append(breite)
            material_l.append(material)
            strasse_l.append(strasse)
            haltungstyp_l.append(haltungstyp)

        x = [i for i in y_deckel if i != 0]
        x2 = [i for i in y_sohle if i != 0]
        x3 = [i for i in y_sohle2 if i != 0]

        max_deckel = max(x)
        min_sohle = min(x2)
        min_sohle2 = min(x3)
        y_deckel_n = []
        y_sohle_n = []
        y_sohle2_n = []

        i = 0
        for x in y_deckel:
            if x == 0:
                y_deckel_n.append(max_deckel)
            else:
                y_deckel_n.append(y_deckel[i])
            i += 1
        i = 0
        for x in y_sohle:
            if x == 0:
                y_sohle_n.append(min_sohle)
            else:
                y_sohle_n.append(y_sohle[i])
            i += 1
        i = 0
        for x in y_sohle2:
            if x == 0:
                y_sohle2_n.append(min_sohle2)
            else:
                y_sohle2_n.append(y_sohle2[i])
            i += 1

        haltungen = {}
        schaechte = {}
        zeitpunkt = None

        if table == 'haltungen':
            for haltung, xkoordinate_o, xkoordinate_u in zip(liste2, x_sohle2[0::2], x_sohle2[1::2]):
                sql = 'SELECT wasserstandoben,wasserstandunten,zeitpunkt FROM lau_gl_el WHERE KANTE=?'
                data = (haltung,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.Critical)

                wasserstaende = self.db_erg_curs.fetchall()

                for wasserstandoben, wasserstandunten, zeitpunkt_t in wasserstaende:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                 zeitpunkt_t, "%Y-%m-%d %H:%M:%S.%f"
                             )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                 zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                             )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                        "Konvertierung vom Zeitpunkt fehlgeschlagen",
                                                        level=Qgis.Critical)
                    if haltungen.get(zeitpunkt) is None:
                        haltungen[zeitpunkt] = {}
                    haltungen[zeitpunkt][haltung] = dict(
                        wasserstandoben=wasserstandoben, wasserstandunten=wasserstandunten, xkoordinate_o=xkoordinate_o,
                        xkoordinate_u=xkoordinate_u
                    )

            zeit = []
            y_liste = []
            x_liste = []

            for i in haltungen:
                zeit.append(i)
            for time in zeit:
                x = []
                y = []
                for h in liste2:
                    y.append(haltungen[time][h]['wasserstandoben'])
                    y.append(haltungen[time][h]['wasserstandunten'])
                    x.append(haltungen[time][h]['xkoordinate_o'])
                    x.append(haltungen[time][h]['xkoordinate_u'])
                x_liste.append(x)
                y_liste.append(y)

            horizontalSlider_3.setMinimum(0)
            horizontalSlider_3.setMaximum(len(zeit))

            y_sohle_2 = []
            y_deckel_3 = []
            x_deckel_2 = []
            delete = []
            # wenn die höhen null sind schachthöhen =max und min werte setzen und farbe grau
            y1 = [i for i in y_sohle if i != 0]
            y2 = [i for i in y_deckel if i != 0]

            min_sohle = min(y1)
            max_deckel = max(y2)

            i = 0
            for x, y in zip(y_sohle, y_deckel_n):
                if y_sohle[i] == 0.0 or y_deckel_n[i] == 0.0:
                    y_sohle_2.append(min_sohle)
                    y_deckel_3.append(max_deckel)
                    x_deckel_2.append(x_deckel[i])
                    delete.append(i)
                i += 1

            for x in delete[::-1]:
                y_sohle.pop(x)
                y_deckel_n.pop(x)
                x_deckel.pop(x)

            def animate(t):

                plt.cla()  # clear the previous image
                plt.xlabel('Länge [m]')
                plt.ylabel('Höhe [m NHN]')
                x_deckel_neu = []
                new_plot.plot(x_deckel, y_deckel_n, color="black", label='Deckel')
                new_plot.plot(x_sohle, y_sohle_n, color="black", label='Kanalsohle')
                new_plot.plot(x_sohle2, y_sohle2_n, color="black", label='Kanalscheitel')

                name_neu = []
                y_label_neu = []

                for i in x_deckel:
                    if i not in x_deckel_neu:
                        x_deckel_neu.append(i)

                for i in name:
                    if i not in name_neu:
                        name_neu.append(i)

                for i in y_label:
                    if i not in y_label_neu:
                        y_label_neu.append(i)

                for x, y, nam in zip(x_deckel_neu, y_label_neu, name_neu):
                    plt.annotate(nam, (x, y),
                                 textcoords="offset points",
                                 xytext=(-10, 0),
                                 rotation=90,
                                 ha='center')

                new_plot.vlines(x_deckel, y_sohle, y_deckel, color="red", linestyles='solid', label='Schacht',
                                linewidth=5)
                new_plot.vlines(x_deckel_2, y_sohle_2, y_deckel_3, color="gray", linestyles='solid', label='Schacht',
                                linewidth=5)

                new_plot.plot(x_liste[t], y_liste[t], color="blue", label='Wasserstand')  # plot the line

                timestamp = zeit[t]
                time = timestamp.strftime("%d.%m.%Y %H:%M:%S")[:-3]
                label_4.setText(time)
                horizontalSlider_3.setValue(t)


            self.anim = animation.FuncAnimation(figure, animate, frames=range(anf, len(zeit)), interval=geschw, blit=False)
            self.anim.event_source.stop()
            try:
                self.anim.event_source.start()
                self.pushButton_4.setText('Stop')
            except AttributeError:
                pass


        if table == 'schaechte':
            x_deckel_neu = []

            for i in x_deckel:
                if i not in x_deckel_neu:
                    x_deckel_neu.append(i)

            for schacht, xkoordinate in zip(liste, x_deckel_neu):
                sql = 'SELECT wasserstand,zeitpunkt FROM lau_gl_s WHERE KNOTEN=?'
                data = (schacht,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.Critical)
                wasserstaende = self.db_erg_curs.fetchall()

                for wasserstand, zeitpunkt_t in wasserstaende:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       "Konvertierung vom Zeitpunkt fehlgeschlagen",
                                                       level=Qgis.Critical)
                    if schaechte.get(zeitpunkt) is None:
                        schaechte[zeitpunkt] = {}
                    schaechte[zeitpunkt][schacht] = dict(
                        wasserstand=wasserstand, xkoordinate=xkoordinate
                    )

            zeit = []
            y_liste = []
            x_liste = []

            for i in schaechte:
                zeit.append(i)
            for time in zeit:
                x = []
                y = []
                for s in liste:
                    y.append(schaechte[time][s]['wasserstand'])
                    x.append(schaechte[time][s]['xkoordinate'])
                x_liste.append(x)
                y_liste.append(y)

            horizontalSlider_3.setMinimum(0)
            horizontalSlider_3.setMaximum(len(zeit))

            y_sohle_2 = []
            y_deckel_3 = []
            x_deckel_2 = []
            delete = []

            # wenn die höhen null sind schachthöhen =max und min werte setzen und farbe grau
            y1 = [i for i in y_sohle if i != 0]
            y2 = [i for i in y_deckel if i != 0]

            min_sohle = min(y1)
            max_deckel = max(y2)

            i = 0
            for x, y in zip(y_sohle, y_deckel_n):
                if y_sohle[i] == 0.0 or y_deckel_n[i] == 0.0:
                    y_sohle_2.append(min_sohle)
                    y_deckel_3.append(max_deckel)
                    x_deckel_2.append(x_deckel[i])
                    delete.append(i)
                i += 1

            for x in delete[::-1]:
                y_sohle.pop(x)
                y_deckel_n.pop(x)
                x_deckel.pop(x)

            def animate(t):

                plt.cla()  # clear the previous image
                plt.xlabel('Länge [m]')
                plt.ylabel('Höhe [m NHN]')
                x_deckel_neu = []
                new_plot.plot(x_deckel, y_deckel_n, color="black", label='Deckel')
                new_plot.plot(x_sohle, y_sohle_n, color="black", label='Kanalsohle')
                new_plot.plot(x_sohle2, y_sohle2_n, color="black", label='Kanalscheitel')

                name_neu = []
                y_label_neu = []

                for i in x_deckel:
                    if i not in x_deckel_neu:
                        x_deckel_neu.append(i)

                for i in name:
                    if i not in name_neu:
                        name_neu.append(i)

                for i in y_label:
                    if i not in y_label_neu:
                        y_label_neu.append(i)

                for x, y, nam in zip(x_deckel_neu, y_label_neu, name_neu):
                    plt.annotate(nam, (x, y),
                                 textcoords="offset points",
                                 xytext=(-10, 0),
                                 rotation=90,
                                 ha='center')

                new_plot.vlines(x_deckel, y_sohle, y_deckel_n, color="red", linestyles='solid', label='Schacht',
                                linewidth=5)
                new_plot.vlines(x_deckel_2, y_sohle_2, y_deckel_3, color="gray", linestyles='solid', label='Schacht',
                                linewidth=5)

                new_plot.plot(x_liste[t], y_liste[t], color="blue", label='Wasserstand')  # plot the line

                timestamp = zeit[t]
                time = timestamp.strftime("%d.%m.%Y %H:%M:%S")[:-3]
                label_4.setText(time)
                horizontalSlider_3.setValue(t)


            self.anim = animation.FuncAnimation(figure, animate, frames=range(anf, len(zeit)), interval=geschw, blit=False)
            self.anim.event_source.stop()
            try:
                self.anim.event_source.start()
                self.pushButton_4.setText('Stop')
            except AttributeError:
                pass

        self.pushButton_4.setDefault(True)
        QtCore.QTimer.singleShot(100, self.pushButton_4.setFocus)



