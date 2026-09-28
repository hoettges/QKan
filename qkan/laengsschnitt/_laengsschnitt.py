import datetime

import matplotlib.animation as animation
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
try:
    import win32com.client
    WINDOWS = True
except ImportError:
    WINDOWS = False
from PyQt6 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.transforms import Affine2D
from qgis.core import Qgis
from qgis.utils import iface, spatialite_connect
import gc
import numpy as np
from PyQt6.QtCore import QTimer

from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import ffloat
from qkan.tools.qkan_utils import get_qkanlayer_attributes
from .dijkstra import find_route
from qkan.utils import  QkanUserError, QkanDbError, QkanAbortError, get_logger

logger = get_logger("QKan.laengs.import")

# TODO: mit einpflegen, dass die Geländehöhe von meheren DGM Layern angezeigt wird und Kreuzunde Haltungen dargestellt werden

class LaengsTask:
    def __init__(self, db_qkan: DBConnection, file: str, fig: plt.figure, canv: FigureCanvas, fig_2: plt.figure,
                 canv_2: FigureCanvas, fig_3: plt.figure, canv_3: FigureCanvas, selected, auswahl, point,
                 massstab, features, db_erg, ausgabe, max, label_4,
                 pushButton_4, horizontalSlider_3, geschw_2, anf):
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
        self.anf = anf

        self.fontsize = 5
        self.zeit = 1
        #self.plugin_instance = plugin_instance

        self.db_erg = spatialite_connect(self.db_erg)
        self.db_erg_curs = self.db_erg.cursor()

        self.pushButton_4.clicked.connect(self.toggle_animation)

        self.horizontalSlider_3.sliderReleased.connect(self.slider_connect)

        self.geschw = self.geschw_2.value()*10
        self.running = False
        self.timer = QTimer()

    def run(self) -> bool:
        self.zeichnen()

    def start_animation(self):
        if not self.timer.isActive():
            self.timer.start(self.geschw)
            self.running = True
            self.pushButton_4.setText('Stop')

    def stop_animation(self):
        if self.timer.isActive():
            self.timer.stop()
        self.running = False
        self.pushButton_4.setText('Start')

    def toggle_animation(self):
        if self.running:
            self.stop_animation()
        else:
            self.start_animation()

    def slider_connect(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timer.deleteLater()



    def zeichnen(self):
        """Längsschnitt in das Fenster zeichnen"""

        figure = self.fig
        #figure.set_size_inches(11.5, 5)
        #figure.tight_layout()
        # figure.clear()
        # plt.figure(figure.number)
        new_plot = figure.add_subplot(111)


        #points = self.point.split(",", 1)
        #pointx = float(points[0])
        #pointy = float(points[1])


        #aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        #mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)

        #selektierte elemente anzeigen
        self.selected = layer.selectedFeatures()

        if self.selected == []:
            msg = (
                f"Keine Daten ausgewählt"
            )
            logger.warning_user(msg)
            raise QkanUserError(msg)

        if not self.selected:
            return 'Kein Objekt gewählt'

        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste=[]
        liste2=[]

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.MessageLevel.Critical)
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
        if route is None:
            msg = (
                f"Keine Route gefunden!"
            )
            logger.warning_user(msg)
            raise QkanAbortError(msg)
        logger.debug(f'LaengsTask.zeichnen() - Ergebnis von find_route(liste):\n{liste=}\n{liste2=}\n{route=}')

        # if route is None:
        #     iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente ausgewählt (2)', level=Qgis.MessageLevel.Critical)
        #     return 'nicht erstellt'

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
        x_deckel_l =[]
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
                coalesce(h.breite, h.hoehe) AS breite,
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
            #logger.error(f"{__file__}: Fehler in laengsschnitt.zeichnen Datenbankzugriff nicht möglich")
            #return 'nicht erstellt'

            msg = (
                f"Fehler in laengsschnitt Datenbankzugriff nicht möglich"
            )
            logger.warning_user(msg)
            raise QkanDbError(msg)

        for attr in self.db_qkan.fetchall():
            (
                schoben, hoehe, schunten, laenge, deckeloben, sohleoben, deckelunten, sohleunten, entwart,
                haltnam, breite, material, strasse, haltungstyp, haltung_sohle_o, haltung_sohle_u,
                schob_typ, schun_typ, entwart_o, entwart_u, laenge2
            ) = attr

            hschoben = sohleoben
            hschunten = sohleunten

            if haltung_sohle_o is None or int(haltung_sohle_o) == 0:
                haltung_sohle_o = sohleoben
            if haltung_sohle_u is None or int(haltung_sohle_u) == 0:
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
                y_sohle2.append(sohleoben + hoehe/1000)
            else:
                y_sohle2.append(sohleoben)
            if haltung_sohle_o > 0:
                y_sohle2.append(haltung_sohle_o + hoehe/1000)
            else:
                y_sohle2.append(haltung_sohle_o)
            if haltung_sohle_u > 0:
                y_sohle2.append(haltung_sohle_u + hoehe/1000)
            else:
                y_sohle2.append(haltung_sohle_u)
            if sohleunten > 0:
                y_sohle2.append(sohleunten + hoehe/1000)
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

            #x_deckel_l.append(round(laenge2 - laenge, 2))
            x_deckel_l.append(laenge2)
            x_deckel_l.append(laenge2)

            z_sohle_h.append(haltung_sohle_o)
            z_sohle_h.append(haltung_sohle_u)
            z_deckel.append(deckeloben)
            z_deckel.append(deckelunten)
            z_sohle.append(sohleoben)
            z_sohle.append(sohleunten)

            y_label.append(round((deckeloben+sohleoben-hoehe/1000)/2,2))
            y_label.append(round((deckelunten+sohleunten-hoehe/1000)/2,2))

            name.append(schoben)
            name.append(schunten)
            haltnam_l.append(haltnam)
            schoben_l.append(schoben)
            schunten_l.append(schunten)
            laenge_l.append(round(laenge, 2))
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
            deckel_l.append(round(deckeloben,2))
            deckel_l.append(round(deckelunten,2))
            sohle_l.append(round(sohleoben,2))
            sohle_l.append(round(sohleunten,2))
            entwart_s.append(entwart_o)
            entwart_s.append(entwart_u)

        y_liste = []

        #wenn alle höhen null sind dann fehlermeldung an nutzer!

        if all(num == 0 for num in x_deckel) and len(x_deckel) > 0 and all(num == 0 for num in x_sohle) and len(x_sohle) > 0:
            iface.messageBar().pushMessage("Fehler", 'Es sind keine Höhenangaben vorhanden!', level=Qgis.MessageLevel.Critical)


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
                                                       level=Qgis.MessageLevel.Critical)
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
                                                       level=Qgis.MessageLevel.Critical)
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

        ax = new_plot
        #ax.gca()
        scale_x = 2

        line_deckel, = new_plot.plot(x_deckel, y_deckel_n, color="black", label='Deckel')
        line_deckel.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        line_sohle, = new_plot.plot(x_sohle, y_sohle_n, color=farbe, label='Kanalsohle')
        line_sohle.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        line_scheitel, = new_plot.plot(x_sohle2, y_sohle2_n, color=farbe, label='Kanalscheitel')
        line_scheitel.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)

        x_deckel_neu = []
        name_neu = []
        y_label_neu = []

        for i in x_deckel:
            if round(i,2) not in x_deckel_neu:
                x_deckel_neu.append(round(i,2))

        for i in name:
            if i not in name_neu:
                name_neu.append(i)

        for i in y_label:
            if round(i,2) not in y_label_neu:
                y_label_neu.append(round(i,2))

        annotations = []
        for x, y, nam in zip(x_deckel_neu, y_label_neu, name_neu):
            an=new_plot.annotate(nam, (x* scale_x, y),
                         textcoords="offset points",
                         xytext=(-10, 0),
                         rotation=90,
                         ha='center')
            annotations.append(an)

        if all(num == 0 for num in y_liste) and len(y_liste) > 0:
            iface.messageBar().pushMessage("Fehler", 'Es sind keine maximalen Wasserstände vorhanden!', level=Qgis.MessageLevel.Critical)
        else:
            if len(y_liste) > 0 and table == 'schaechte':
                #new_plot.plot(x_deckel_neu, y_liste, linestyle="dotted", color="blue", label='maximaler Wasserstand')
                hline0, = new_plot.plot(x_deckel_neu, y_liste, linestyle="dotted", color="blue", label='maximaler Wasserstand')
                hline0.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)

            if len(y_liste) > 0 and table == 'haltungen':

                #new_plot.plot(x_deckel[::2], y_liste, linestyle="dotted", color="blue", label='maximaler Wasserstand')
                hline0, = new_plot.plot(x_deckel[::2], y_liste, linestyle="dotted", color="blue", label='maximaler Wasserstand')
                hline0.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)

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


        line1 = new_plot.vlines(x_deckel, y_sohle, y_deckel_n, color="red", linestyles='solid', label='Schacht', linewidth=5)
        line1.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)

        line2 = new_plot.vlines(x_deckel_2, y_sohle_2, y_deckel_3, color="gray", linestyles='solid', label='fiktiver Schacht', linewidth=5)
        line2.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)

        x_min = -0.5
        y_min = float(min(y_sohle)) - 0.5
        y_max = float(max(y_deckel)) + 0.5
        #x_max = laenge2 / massstab + 2.5 + pointx
        x_max = laenge2 + 2.5
        x=[x_min, x_max]
        y=[y_min, y_min]
        hline1 = new_plot.hlines(y_min, x_min, x_max+5, color="grey", linestyles='solid')
        hline1.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        hline2 = new_plot.hlines(y_min, x_min-80, x_max+5, color="grey", linestyles='solid')
        hline2.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        hline3 = new_plot.hlines(y_min-0.6, x_min - 80, x_max+5, color="grey", linestyles='solid')
        hline3.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        hline4 = new_plot.hlines(y_min - 1.1, x_min - 80, x_max+5, color="grey", linestyles='solid')
        hline4.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        hline5 = new_plot.hlines(y_min - 1.6, x_min - 80, x_max+5, color="grey", linestyles='solid')
        hline5.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        hline6 = new_plot.hlines(y_min - 2.1, x_min - 80, x_max+5, color="grey", linestyles='solid')
        hline6.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        hline7 = new_plot.hlines(y_min - 2.6, x_min - 80, x_max+5, color="grey", linestyles='solid')
        hline7.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)
        hline8 = new_plot.hlines(y_min - 3.1, x_min - 80, x_max+5, color="grey", linestyles='solid')
        hline8.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)


        z_sohle_neu = []
        for i in z_sohle:
            if i not in z_sohle_neu:
                z_sohle_neu.append(i)
        z_deckel_neu = []
        for i in z_deckel:
            if round(i,2) not in z_deckel_neu:
                z_deckel_neu.append(round(i,2))

        name_neu.insert(0,"Schachtname")
        x_deckel_neu.insert(0, -70)
        z_deckel_neu.insert(0, "Deckelhöhe [m ü. NHN]")
        z_sohle_neu.insert(0, "Sohlhöhe Schacht [m ü. NHN]")


        for i, j, x, y in zip(x_deckel_neu, name_neu, z_deckel_neu, z_sohle_neu):
            #plt.vlines(i, y_min, y_min-3.1, color="grey", linestyles='solid')
            if i == x_deckel_neu[0]:
                #line = plt.vlines(i, y_min - 2.1, y_min - 3.1, color="grey", linestyles='solid')
                #line.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)

                an = new_plot.annotate(x, ((i + 0.1) * scale_x, y_min - 0.4), ha='left')
                annotations.append(an)

                an = new_plot.annotate(j, ((i + 0.1) * scale_x, y_min - 0.9), ha='left')
                annotations.append(an)

                an = new_plot.annotate(y, ((i + 0.1) * scale_x, y_min - 1.4), ha='left')
                annotations.append(an)

            else:

                line = new_plot.vlines(i, y_min-2.1, y_min -3.1, color="grey", linestyles='solid')
                line.set_transform(Affine2D().scale(scale_x, 1) + ax.transData)

                an = new_plot.annotate(x, ((i + 0.1)* scale_x, y_min - 0.4), ha='center')
                annotations.append(an)

                an = new_plot.annotate(j, ((i +0.1)* scale_x, y_min - 0.9), ha='center')
                annotations.append(an)

                an = new_plot.annotate(y, ((i +0.1)* scale_x, y_min - 1.4), ha='center')
                annotations.append(an)

        x = 0

        x_d = x_deckel_l

        del x_d[-1]
        x_d.insert(0, 0)

        x_d.insert(0, -70)
        z_sohle_h.insert(0, "Sohlhöhe Haltung [m ü. NHN]")

        for i, j in zip(x_d, z_sohle_h):
            # so verschieben, dass die Texte passend stehen!

            if i == x_d[0]:
                an = new_plot.annotate(j, ((i +0.1) * scale_x, y_min - 1.9),
                                  ha='left')
                annotations.append(an)

            elif i == x_d[1]:
                an = new_plot.annotate(j, ((i +4.) * scale_x, y_min - 1.9),
                                  ha='left')
                annotations.append(an)

            elif i == x_d[-1]:
                an = new_plot.annotate(j, ((i -5.) * scale_x, y_min - 1.9),
                                  ha='left')
                annotations.append(an)

            elif x % 2:
                an=new_plot.annotate(round(j, 2), ((i-6.)* scale_x, y_min- 1.9 ),
                              ha='center')
                annotations.append(an)
            else:
                an=new_plot.annotate(j, ((i+6.)* scale_x, y_min - 1.9),
                              ha='center')
                annotations.append(an)
            x += 1

        laenge = laenge_l
        dn = breite_l
        material = material_l

        x_mitte = []
        x = 0
        x_deckel_neu.pop(0)
        while x + 1 < len(x_deckel_neu):
            m = (x_deckel_neu[x] + x_deckel_neu[x + 1]) / 2
            x += 1
            x_mitte.append(m)

        # mittig zwischen zwei Schächte schreiben Länge, Nennweite und Material, Gefälle, Stationierung
        for i, k, l, m in zip(x_mitte, laenge, dn, material):
            if i == x_mitte[0]:
                an = new_plot.annotate("Nennweite [mm] / Material", ((-65+0.1) * scale_x, y_min - 3), textcoords="offset points",
                                  xytext=(-10, 0), ha='left')
                annotations.append(an)

                an = new_plot.annotate("Länge [m]", ((-65 +0.1) * scale_x, y_min - 2.5), textcoords="offset points",
                             xytext=(-10, 0), ha='left')
                annotations.append(an)

                an = new_plot.annotate(ffloat(k, 2), ((i+0.1) * scale_x, y_min - 2.5), textcoords="offset points",
                                  xytext=(-10, 0), ha='center')
                annotations.append(an)

                an = new_plot.annotate(f'{int(l)} / {m}', ((i+0.1) * scale_x, y_min - 3), textcoords="offset points",
                                  xytext=(-10, 0), ha='center')
                annotations.append(an)

            else:
                an = new_plot.annotate(ffloat(k, 2), ((i+0.1) * scale_x, y_min - 2.5), textcoords="offset points",
                                  xytext=(-10, 0), ha='center')
                annotations.append(an)


                an=new_plot.annotate(f'{int(l)} / {m}', ((i+0.1)* scale_x, y_min - 3), textcoords="offset points",
                             xytext=(-10, 0), ha='center')
                annotations.append(an)


        ax.set_xlim(- 170, (x_max * scale_x)+25)
        ax.set_xticks([])

        #new_xticks = np.linspace(0, x_max * scale_x, x_max)
        #new_xticks = np.linspace(0, x_max * scale_x)
        #ax.set_xticks(new_xticks)
        #ax.set_xticklabels([f"{xi:.1f}" for xi in x_max])

        new_plot.set_xlabel('Länge [m]')
        new_plot.set_ylabel('Höhe [m NHN]')
        new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)


        self.fig.tight_layout(pad=1.08)

        #self.auswahl[figure.number] = self.selected

        self.fig.canvas.draw()

        self.avoid_label_overlap(annotations, ax, self.fig)


    def avoid_label_overlap(self, annotations, ax,fig, pad=0.5, max_iter=100, min_fontsize=7):

        for _ in range(max_iter):
            moved = False
            renderer = fig.canvas.get_renderer()
            boxes = [ann.get_window_extent(renderer=renderer).transformed(ax.transData.inverted()) for ann in
                     annotations]

            for i in range(len(boxes)):
                for j in range(i + 1, len(boxes)):
                    if boxes[i].overlaps(boxes[j]):
                        xi, yi = annotations[i].get_position()
                        xj, yj = annotations[j].get_position()

                        dx, dy = xj - xi, yj - yi
                        dist = np.hypot(dx, dy) + 1e-9
                        dx, dy = dx / dist * pad / 2, dy / dist * pad / 2

                        # beide leicht auseinanderbewegen
                        annotations[i].set_position((xi - dx, yi ))
                        annotations[j].set_position((xj + dx, yj ))
                        moved = True

                    if moved:
                        continue

                    for j, ann in enumerate(annotations):
                        fontsize = ann.get_fontsize()
                        if fontsize > min_fontsize:
                            ann.set_fontsize(fontsize - 0.5)
                            resized = True

                    if not moved and not resized:
                        break


    def show(self):
        """selektierte Elemente anzeigen"""
        layer = iface.activeLayer()
        layer.selectByExpression("pk in {}".format(tuple(self.features)))


    def cad(self):
        """Längsschnitt in CAD zeichnen"""
        if self.point == '':
            msg = (
                f"Kein Speicherort ausgewählt"
            )
            logger.warning_user(msg)
            raise QkanUserError(msg)

        # Maßstab
        massstab = float(self.massstab)

        layer = iface.activeLayer()
        x = layer.source()

        # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)

        # selektierte elemente anzeigen

        figure = self.fig
        self.selected = layer.selectedFeatures()

        if not self.selected:
            return 'Kein Objekt gewählt'

        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste = []
        liste2 = []

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.MessageLevel.Critical)
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
        logger.debug(f'LaengsTask.cad() - Ergebnis von find_route(liste):\n{liste=}\n{liste2=}\n{route=}')

        # if route is None:
        #     iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente ausgewählt (3)', level=Qgis.MessageLevel.Critical)
        #     return

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
        x_deckel_l = []
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
        schachttyp_l = []
        schaechte_l = []
        deckel_l = []
        sohle_l = []
        entwart_s = []
        gefaelle = []
        durchmesser = []
        x_deckel_durchm = []
        y_deckel_durchm = []
        y_sohle_durchm = []
        y_sohle2_durchm = []

        z_deckel = []
        z_sohle = []
        z_sohle_h = []

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
                        coalesce(h.breite, h.hoehe) AS breite,
                        h.material,
                        h.strasse,
                        h.haltungstyp,
                        h.sohleoben,
                        h.sohleunten,
                        schob.knotentyp,
                        schun.knotentyp,
                        schob.entwart,
                        schun.entwart,
                        sum(h.laenge) OVER (ORDER BY sel.column2 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as laenge_sum,
                        schob.durchm,
                        schun.durchm
                    FROM haltungen AS h
                    INNER JOIN schaechte AS schob ON schob.schnam = h.schoben
                    INNER JOIN schaechte AS schun ON schun.schnam = h.schunten
                    INNER JOIN (VALUES ({sel})) AS sel ON sel.column1 = h.haltnam
                    """

        if not self.db_qkan.sql(sql, "laengsschnitt.zeichnen.2"):
            #logger.error(f"{__file__}: Fehler in laengsschnitt.zeichnen.2: Datenbankzugriff nicht möglich")
            #return 'nicht erstellt'

            msg = (
                f"Fehler in laengsschnitt Datenbankzugriff nicht möglich"
            )
            logger.warning_user(msg)
            raise QkanDbError(msg)

        for attr in self.db_qkan.fetchall():
            (
                schoben, hoehe, schunten, laenge, deckeloben, sohleoben, deckelunten, sohleunten, entwart,
                haltnam, breite, material, strasse, haltungstyp, haltung_sohle_o, haltung_sohle_u,
                schob_typ, schun_typ, entwart_o, entwart_u, laenge2, durchmesser_o, durchmesser_u
            ) = attr

            hschoben = sohleoben
            hschunten = sohleunten

            if haltung_sohle_o is None or int(haltung_sohle_o) == 0:
                haltung_sohle_o = sohleoben
            if haltung_sohle_u is None or int(haltung_sohle_u) == 0:
                haltung_sohle_u = sohleunten

            y_sohle.append(sohleoben)
            y_sohle.append(haltung_sohle_o)
            y_sohle.append(haltung_sohle_u)
            y_sohle.append(sohleunten)

            if sohleoben > 0:
                y_sohle2.append(sohleoben + hoehe / 1000)
            else:
                y_sohle2.append(sohleoben)
            if haltung_sohle_o > 0:
                y_sohle2.append(haltung_sohle_o + hoehe / 1000)
            else:
                y_sohle2.append(haltung_sohle_o)
            if haltung_sohle_u > 0:
                y_sohle2.append(haltung_sohle_u + hoehe / 1000)
            else:
                y_sohle2.append(haltung_sohle_u)
            if sohleunten > 0:
                y_sohle2.append(sohleunten + hoehe / 1000)
            else:
                y_sohle2.append(sohleunten)

            gefaelle.append((sohleoben-sohleunten)/laenge)

            y_deckel.append(deckeloben)
            y_deckel.append(deckeloben)
            y_deckel.append(deckelunten)
            y_deckel.append(deckelunten)
            x_deckel.append(round(laenge2 - laenge, 2))
            x_deckel.append(round(laenge2 - laenge, 2))
            x_deckel.append(laenge2)
            x_deckel.append(laenge2)

            # x_deckel_l.append(round(laenge2 - laenge, 2))
            x_deckel_l.append(laenge2)
            x_deckel_l.append(laenge2)

            durchmesser.append(durchmesser_o)
            durchmesser.append(durchmesser_o)
            durchmesser.append(durchmesser_u)
            durchmesser.append(durchmesser_u)

            y_deckel_durchm.append(deckeloben)
            y_deckel_durchm.append(deckeloben)
            y_deckel_durchm.append(deckelunten)
            y_deckel_durchm.append(deckelunten)

            y_sohle_durchm.append(sohleoben)
            y_sohle_durchm.append(haltung_sohle_o)
            y_sohle_durchm.append(haltung_sohle_u)
            y_sohle_durchm.append(sohleunten)

            if sohleoben > 0:
                y_sohle2_durchm.append(sohleoben + hoehe / 1000)
            else:
                y_sohle2_durchm.append(sohleoben)
            if haltung_sohle_o > 0:
                y_sohle2_durchm.append(haltung_sohle_o + hoehe / 1000)
            else:
                y_sohle2_durchm.append(haltung_sohle_o)
            if haltung_sohle_u > 0:
                y_sohle2_durchm.append(haltung_sohle_u + hoehe / 1000)
            else:
                y_sohle2_durchm.append(haltung_sohle_u)
            if sohleunten > 0:
                y_sohle2_durchm.append(sohleunten + hoehe / 1000)
            else:
                y_sohle2_durchm.append(sohleunten)

            z_sohle_h.append(haltung_sohle_o)
            z_sohle_h.append(haltung_sohle_u)
            z_deckel.append(deckeloben)
            z_deckel.append(deckelunten)
            z_sohle.append(sohleoben)
            z_sohle.append(sohleunten)

            y_label.append(round((deckeloben + sohleoben - hoehe / 1000) / 2, 2))
            y_label.append(round((deckelunten + sohleunten - hoehe / 1000) / 2, 2))

            name.append(schoben)
            name.append(schunten)
            haltnam_l.append(haltnam)
            schoben_l.append(schoben)
            schunten_l.append(schunten)
            laenge_l.append(round(laenge, 2))
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
            deckel_l.append(round(deckeloben, 2))
            deckel_l.append(round(deckelunten, 2))
            sohle_l.append(round(sohleoben, 2))
            sohle_l.append(round(sohleunten, 2))
            entwart_s.append(entwart_o)
            entwart_s.append(entwart_u)

        y_liste = []

        if all(num == 0 for num in x_deckel) and len(x_deckel) > 0 and all(num == 0 for num in y_sohle) and len(y_sohle) > 0:
            iface.messageBar().pushMessage("Fehler", 'Es sind keine Höhenangaben vorhanden!', level=Qgis.MessageLevel.Critical)

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
                                                       level=Qgis.MessageLevel.Critical)
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
                                                       level=Qgis.MessageLevel.Critical)
                    wasserstaende = self.db_erg_curs.fetchall()

                    for wasserstand in wasserstaende:
                        schaechte[schacht] = dict(
                            wasserstand=wasserstand[0])

                for s in liste:
                    y_liste.append(schaechte[s]['wasserstand'])

        def dxf_line(x1, y1, x2, y2, layer="0", color=7):
            """Erzeugt ein DXF-LINIE-Entity."""
            return f"""0
                    LINE
                    8
                    {layer}
                    62
                    {color}
                    10
                    {x1}
                    20
                    {y1}
                    30
                    0
                    11
                    {x2}
                    21
                    {y2}
                    31
                    0
                    """

        def dxf_text(x, y, text, height=10, layer="0", color=7):
            """Erzeugt ein DXF-TEXT-Entity."""
            return f"""0
                TEXT
                8
                {layer}
                62
                {color}
                10
                {x}
                20
                {y}
                30
                0
                40
                {height*massstab/5}
                1
                {text}
                """

        def dxf_text_mitte(x, y, text, height=10, layer="0", color=7):
            """Erzeugt ein DXF-TEXT-Entity."""
            return f"""0
                TEXT
                8
                {layer}
                62
                {color}
                10
                {x}
                20
                {y}
                30
                0
                40
                {height*massstab/5}
                1
                {text}
                72
                1
                11
                {x}
                21
                {y}
                31
                0
                """

        def write_dxf(filename, entities):
            """Schreibt eine vollständige DXF-Datei (AutoCAD R12 kompatibel)."""

            dxf_header = """0
                SECTION
                2
                HEADER
                0
                ENDSEC
                0
                SECTION
                2
                TABLES
                0
                TABLE
                2
                LAYER
                0
                LAYER
                2
                0
                70
                0
                62
                7
                6
                CONTINUOUS
                0
                ENDTAB
                0
                ENDSEC
                0
                SECTION
                2
                BLOCKS
                0
                ENDSEC
                0
                SECTION
                2
                ENTITIES
                """

            dxf_end = """0
                        ENDSEC
                        0
                        EOF
                        """

            with open(filename, "w", encoding="utf-8") as f:
                f.write(dxf_header)
                for e in entities:
                    f.write(e)
                f.write(dxf_end)


        farbe = 7
        if entwart == 'MW' or entwart == 'KM' or entwart == 'Mischwasser':
            farbe = 6

        elif entwart == 'RW' or entwart == 'KR' or entwart == 'Regenwasser':
            farbe = 5

        elif entwart == 'SW' or entwart == 'KS' or entwart == 'Schmutzwasser':
            farbe = 22

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
        s_leer = []
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

        entities = []
        x_deckel_neu = []
        name_neu = []
        y_label_neu = []

        for i in x_deckel:
            if round(i, 2) not in x_deckel_neu:
                x_deckel_neu.append(round(i, 2))


        x_deckel_durchm = []

        x_deckel_durchm.append(x_deckel[0] - durchmesser[0] / 2)
        x_index = 1

        for i in range(0, len(x_deckel) - 1, 2):
            block = x_deckel[i:i + 2]

            if (x_index % 2) == 1:  # gerade Blöcke → +
                x_deckel_durchm.extend([b + durchmesser[x_index] / 2 for b in block])
            else:  # ungerade Blöcke → -
                x_deckel_durchm.extend([b - durchmesser[x_index] / 2 for b in block])
            x_index += 1

        x_deckel_durchm.append(x_deckel[-1] + durchmesser[-1] / 2)

        y_sohle2_n_durchm = []
        y_sohle2_n_durchm = [y_sohle2_n[0]] + y_sohle2_n + [y_sohle2_n[-1]]

        y_deckel_n_durchm = []
        y_deckel_n_durchm = [y_deckel_n[0]] + y_deckel_n + [y_deckel_n[-1]]

        y_sohle_n_durchm = []
        y_sohle_n_durchm = [y_sohle_n[0]] + y_sohle_n + [y_sohle_n[-1]]


        for i in range(len(x_deckel_durchm)-1):

            entities.append(dxf_line(x_deckel_durchm[i], float(y_deckel_n_durchm[i])*massstab, x_deckel_durchm[i+1], float(y_deckel_n_durchm[i+1])*massstab, layer="0", color=7))

            entities.append(dxf_line(x_deckel_durchm[i], float(y_sohle_n_durchm[i])*massstab, x_deckel_durchm[i+1], float(y_sohle_n_durchm[i+1])*massstab, layer="0", color=farbe))

            entities.append(dxf_line(x_deckel_durchm[i], float(y_sohle2_n_durchm[i])*massstab, x_deckel_durchm[i+1], float(y_sohle2_n_durchm[i+1])*massstab, layer="0", color=farbe))


        x_deckel_neu = []
        name_neu = []
        y_label_neu = []

        for i in x_deckel:
            if round(i, 2) not in x_deckel_neu:
                x_deckel_neu.append(round(i, 2))

        for i in name:
            if i not in name_neu:
                name_neu.append(i)

        for i in y_label:
            if round(i, 2) not in y_label_neu:
                y_label_neu.append(round(i, 2))

        for i in range(len(x_deckel)):

            entities.append(dxf_line((x_deckel[i]-durchmesser[i]/2), float(y_sohle[i])*massstab, (x_deckel[i]-durchmesser[i]/2), float(y_deckel_n[i])*massstab, layer="0", color=1))
            entities.append(dxf_line((x_deckel[i] + durchmesser[i] / 2), float(y_sohle[i]) * massstab, (x_deckel[i] + durchmesser[i] / 2), float(y_deckel_n[i]) * massstab, layer="0", color=1))

        for i in range(len(x_deckel_2)):

            entities.append(dxf_line(x_deckel_2[i], float(y_sohle_2[i])*massstab, x_deckel_2[i], float(y_sohle_n[i])*massstab, layer="0", color=7))


        if all(num == 0 for num in y_liste) and len(y_liste) > 0:
            iface.messageBar().pushMessage("Fehler", 'Es sind keine maximalen Wasserstände vorhanden!',
                                           level=Qgis.MessageLevel.Critical)
        else:
            if len(y_liste) > 0 and table == 'schaechte':
                # new_plot.plot(x_deckel_neu, y_liste, linestyle="dotted", color="blue", label='maximaler Wasserstand')

                for i in range(len(x_deckel_neu)-1):
                    entities.append(dxf_line(x_deckel_neu[i], float(y_liste[i])*massstab, x_deckel_neu[i + 1], float(y_liste[i + 1])*massstab, layer="0", color=140))


            if len(y_liste) > 0 and table == 'haltungen':
                # new_plot.plot(x_deckel[::2], y_liste, linestyle="dotted", color="blue", label='maximaler Wasserstand')
                for i in range(len(x_deckel)-1):
                    entities.append(dxf_line(x_deckel_neu[i], float(y_liste[i])*massstab, x_deckel_neu[i + 1], float(y_liste[i + 1])*massstab, layer="0", color=140))


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

        x_min = -0.5
        y_min = float(min(y_sohle)) - 0.5
        y_max = float(max(y_deckel)) + 0.5
        # x_max = laenge2 / massstab + 2.5 + pointx
        x_max = laenge2 + 2.5
        x = [x_min, x_max]
        y = [y_min, y_min]


        #Tabelle
        entities.append(dxf_line(x_min, y_min*massstab, x_max + 5, y_min*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, y_min*massstab, x_max + 5, y_min*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, (y_min - 0.6)*massstab, x_max + 5, (y_min - 0.6)*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, (y_min - 0.6)*massstab, x_max + 5, (y_min - 0.6)*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, (y_min - 1.1)*massstab, x_max + 5, (y_min - 1.1)*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, (y_min - 1.6)*massstab, x_max + 5, (y_min - 1.6)*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, (y_min - 2.1)*massstab, x_max + 5, (y_min - 2.1)*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, (y_min - 2.6)*massstab, x_max + 5, (y_min - 2.6)*massstab, layer="0", color=7))

        entities.append(dxf_line(x_min - 80, (y_min - 3.1)*massstab, x_max + 5, (y_min - 3.1)*massstab, layer="0", color=7))

        z_sohle_neu = []
        for i in z_sohle:
            if i not in z_sohle_neu:
                z_sohle_neu.append(i)
        z_deckel_neu = []
        for i in z_deckel:
            if round(i, 2) not in z_deckel_neu:
                z_deckel_neu.append(round(i, 2))

        name_neu.insert(0, "Schachtname")
        x_deckel_neu.insert(0, -70)
        z_deckel_neu.insert(0, "Deckelhoehe [m NHN]")
        z_sohle_neu.insert(0, "Sohlhoehe Schacht [m NHN]")

        for i, j, x, y in zip(x_deckel_neu, name_neu, z_deckel_neu, z_sohle_neu):
            if i == x_deckel_neu[0]:

                entities.append(dxf_text(i, (y_min - 0.9)*massstab, x, height=1, layer="0", color=7))

                entities.append(dxf_text(i, (y_min - 0.4)*massstab, j, height=1, layer="0", color=7))

                entities.append(dxf_text(i, (y_min - 1.4)*massstab, y, height=1, layer="0", color=7))

            else:
                entities.append(dxf_line(i, (y_min - 1.6)*massstab, i, (y_min - 3.1)*massstab, layer="0", color=7))

                entities.append(dxf_text_mitte(i, (y_min - 0.9)*massstab, x, height=1, layer="0", color=7))

                entities.append(dxf_text_mitte(i, (y_min - 0.4)*massstab, j, height=1, layer="0", color=7))

                entities.append(dxf_text_mitte(i, (y_min - 1.4)*massstab, y, height=1, layer="0", color=7))

        x = 0

        x_d = x_deckel_l

        del x_d[-1]
        x_d.insert(0, 0)

        x_d.insert(0, -70)
        z_sohle_h.insert(0, "Sohlhoehe Haltung [m NHN]")

        for i, j in zip(x_d, z_sohle_h):
            # so verschieben, dass die Texte passend stehen!

            if i == x_d[0]:
                entities.append(dxf_text(i, (y_min - 1.9)*massstab, j, height=1, layer="0", color=7))

            elif i == x_d[1]:
                entities.append(dxf_text_mitte(i+5, (y_min - 1.9)*massstab, j, height=1, layer="0", color=7))

            elif i == x_d[-1]:
                entities.append(dxf_text_mitte(i-5, (y_min - 1.9)*massstab, j, height=1, layer="0", color=7))

            elif x % 2:
                entities.append(dxf_text_mitte(i-5, (y_min - 1.9)*massstab, j, height=1, layer="0", color=7))

            else:
                entities.append(dxf_text_mitte(i+5, (y_min - 1.9)*massstab, j, height=1, layer="0", color=7))
            x += 1

        laenge = laenge_l
        dn = breite_l
        material = material_l

        x_mitte = []
        x = 0
        x_deckel_neu.pop(0)
        while x + 1 < len(x_deckel_neu):
            m = (x_deckel_neu[x] + x_deckel_neu[x + 1]) / 2
            x += 1
            x_mitte.append(m)

        # mittig zwischen zwei Schächte schreiben Länge, Nennweite und Material, Gefälle, Stationierung
        for i, k, l, m, g in zip(x_mitte, laenge, dn, material, gefaelle):
            if i == x_mitte[0]:
                entities.append(dxf_text(-70, (y_min - 3)*massstab, "Nennweite [mm] / Material", height=1, layer="0", color=7))

                entities.append(dxf_text(-70, (y_min - 2.5)*massstab, "Laenge [m] / Gefaelle", height=1, layer="0", color=7))

                entities.append(dxf_text_mitte(i, (y_min - 2.5)*massstab, f'{ffloat(k, 2)} / {ffloat(g*100, 2)} %', height=1, layer="0", color=7))

                entities.append(dxf_text_mitte(i, (y_min - 3)*massstab, f'{int(l)} / {m}', height=1, layer="0", color=7))

            else:
                entities.append(dxf_text_mitte(i, (y_min - 2.5)*massstab, f'{ffloat(k, 2)} / {ffloat(g*100, 2)} %', height=1, layer="0", color=7))

                entities.append(dxf_text_mitte(i, (y_min - 3)*massstab, f'{int(l)} / {m}', height=1, layer="0", color=7))


        filename = self.point
        write_dxf(filename, entities)

        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        text = text.replace(" ", "")  # Tabs entfernen

        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)


    def ganglinie(self):
        figure = self.fig_3
        # figure.clear()
        # plt.figure(figure.number)
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
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.MessageLevel.Critical)
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
                                                   level=Qgis.MessageLevel.Critical)

                res = self.db_erg_curs.fetchall()
                for zeitpunkt_t, zufluss, wasserstand, durchfluss, wassertiefe in res:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t[:zeitpunkt_t.index('.')+7], "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       f"Konvertierung vom Zeitpunkt fehlgeschlagen (2)\n{err=}\n{zeitpunkt_t}",
                                                       level=Qgis.MessageLevel.Critical)
                        logger.error(f"Konvertierung vom Zeitpunkt fehlgeschlagen (2)\n{err=}\n{zeitpunkt_t}")
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
                                                   level=Qgis.MessageLevel.Critical)

                res = self.db_erg_curs.fetchall()
                for zeitpunkt_t, auslastung, durchfluss, geschwindigkeit, wassertiefe in res:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t[:zeitpunkt_t.index('.')+7], "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       f"Konvertierung vom Zeitpunkt fehlgeschlagen (3)\n{err=}\n{zeitpunkt_t}",
                                                       level=Qgis.MessageLevel.Critical)
                        logger.error(f"Konvertierung vom Zeitpunkt fehlgeschlagen (3)\n{err=}\n{zeitpunkt_t}")
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
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('m³/s')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['durchfluss'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)

            if self.ausgabe == 'Geschwindigkeit':
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('m/s')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['geschwindigkeit'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)

            if self.ausgabe == 'Auslastung':
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('%')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['auslastung'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)

            if self.ausgabe == 'Wassertiefe':
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('m')
                for h in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in haltungen.items():
                        x_liste.append(x)
                        y_liste.append(y[h]['wassertiefe'])
                    new_plot.plot(x_liste, y_liste, label=h)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)

        if table == 'schaechte':
            if self.ausgabe == 'Zufluss':
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('m³/s')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['zufluss'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)



            if self.ausgabe == 'Wasserstand':
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('m NN')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['wasserstand'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)

            if self.ausgabe == 'Wassertiefe':
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('m')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['wassertiefe'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)

            if self.ausgabe == 'Durchfluss':
                new_plot.set_xlabel('Zeit')
                new_plot.set_ylabel('m³/s')
                for s in liste:
                    x_liste = []
                    y_liste = []
                    for x, y in schaechte.items():
                        x_liste.append(x)
                        y_liste.append(y[s]['durchfluss'])
                    new_plot.plot(x_liste, y_liste, label=s)
                    new_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
                    new_plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5)

        figure.tight_layout(pad=1.08)


    def laengs(self):

        if self.timer is not None:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None

        #hier wird der animierte Längsschnitt in das Fenster gezeichnet
        label_4 = self.label_4
        anf = self.anf
        geschw = self.geschw
        self.running = True

        figure = self.fig_2
        # figure.clear()
        # plt.figure(figure.number)
        new_plot = figure.add_subplot(111)

        #aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        #mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        _, table, _, _ = get_qkanlayer_attributes(x)

        t = None

        #selektierte elemente anzeigen
        self.selected = layer.selectedFeatures()

        if self.selected == []:
            msg = (
                f"Keine Daten ausgewählt"
            )
            logger.warning_user(msg)
            raise QkanUserError(msg)
        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste=[]
        liste2=[]

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.MessageLevel.Critical)
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
        logger.debug(f'LaengsTask.laengs() - Ergebnis von find_route(liste):\n{liste=}\n{liste2=}\n{route=}')

        # if route is None:
        #     iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente ausgewählt (4)', level=Qgis.MessageLevel.Critical)
        #     return 'nicht erstellt'

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
        x_pos = []

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
            #logger.error(f"{__file__}: Fehler in laengsschnitt.zeichnen.4: Datenbankzugriff nicht möglich")
            #return 'nicht erstellt'

            msg = (
                f"Fehler in laengsschnitt Datenbankzugriff nicht möglich"
            )
            logger.warning_user(msg)
            raise QkanDbError(msg)

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
                y_sohle2.append(sohleoben + hoehe/1000)
            else:
                y_sohle2.append(sohleoben)
            if haltung_sohle_o > 0:
                y_sohle2.append(haltung_sohle_o + hoehe/1000)
            else:
                y_sohle2.append(haltung_sohle_o)
            if haltung_sohle_u > 0:
                y_sohle2.append(haltung_sohle_u + hoehe/1000)
            else:
                y_sohle2.append(haltung_sohle_u)
            if sohleunten > 0:
                y_sohle2.append(sohleunten + hoehe/1000)
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

            y_label.append((deckeloben + sohleoben - hoehe/1000) / 2)
            y_label.append((deckelunten + sohleunten - hoehe/1000) / 2)

            name.append(schoben)
            name.append(schunten)
            haltnam_l.append(haltnam)
            schoben_l.append(schoben)
            schunten_l.append(schunten)
            laenge_l.append(laenge)
            entwart_l.append(entwart)
            hoehe_l.append(hoehe/1000)
            breite_l.append(breite/1000)
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
            #liste2 = sum(zip(liste2, liste2), ())

            x_deckel_neu = x_sohle2[::2]

            for haltung, xkoordinate_o, xkoordinate_u in zip(liste2, x_deckel_neu[0::2], x_deckel_neu[1::2]):
                sql = 'SELECT wasserstandoben,wasserstandunten,zeitpunkt FROM lau_gl_el WHERE KANTE=?'
                data = (haltung,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.MessageLevel.Critical)

                wasserstaende = self.db_erg_curs.fetchall()

                for wasserstandoben, wasserstandunten, zeitpunkt_t in wasserstaende:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                 zeitpunkt_t[:zeitpunkt_t.index('.')+7], "%Y-%m-%d %H:%M:%S.%f"
                             )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                 zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                             )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                        f"Konvertierung vom Zeitpunkt fehlgeschlagen (4)\n{err=}\n{zeitpunkt_t}",
                                                        level=Qgis.MessageLevel.Critical)
                        logger.error(f"Konvertierung vom Zeitpunkt fehlgeschlagen (4)\n{err=}\n{zeitpunkt_t}")
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

            self.horizontalSlider_3.setMinimum(0)
            self.horizontalSlider_3.setMaximum(len(zeit))

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

            new_plot.set_xlabel('Länge [m]')
            new_plot.set_ylabel('Höhe [m NHN]')
            x_deckel_neu = []
            new_plot.plot(x_deckel, y_deckel_n, color="black", label='Deckel')
            new_plot.plot(x_sohle, y_sohle_n, color="black", label='Kanalsohle')
            new_plot.plot(x_sohle2, y_sohle2_n, color="black", label='Kanalscheitel')

            name_neu = []
            y_label_neu = []

            for i in x_deckel:
                if round(i, 2) not in x_deckel_neu:
                    x_deckel_neu.append(round(i, 2))

            for i in name:
                if i not in name_neu:
                    name_neu.append(i)

            for i in y_label:
                if i not in y_label_neu:
                    y_label_neu.append(i)

            for x, y, nam in zip(x_deckel_neu, y_label_neu, name_neu):
                new_plot.annotate(nam, (x, y),
                             textcoords="offset points",
                             xytext=(-10, 0),
                             rotation=90,
                             ha='center')

            new_plot.vlines(x_deckel, y_sohle, y_deckel, color="red", linestyles='solid', label='Schacht',
                            linewidth=5)
            new_plot.vlines(x_deckel_2, y_sohle_2, y_deckel_3, color="gray", linestyles='solid',
                            label='fiktiver Schacht',
                            linewidth=5)

            (wasserstand,) = new_plot.plot([], [], color="blue", label='Wasserstand')

            self.t = anf
            self.max_t = len(zeit)
            def animate():

                if self.t >= self.max_t:
                    self.timer.stop()
                    self.running = False
                    return

                wasserstand.set_data(x_liste[self.t], y_liste[self.t])

                timestamp = zeit[self.t]
                time = timestamp.strftime("%d.%m.%Y %H:%M:%S")[:-3]

                if label_4 is not None:
                    label_4.setText(time)

                if not self.horizontalSlider_3.isSliderDown():
                    self.horizontalSlider_3.blockSignals(True)
                    self.horizontalSlider_3.setValue(self.t)
                    self.horizontalSlider_3.blockSignals(False)

                self.canv_2.draw_idle()
                self.t+=1


            self.timer = QTimer()
            self.timer.timeout.connect(animate)
            self.timer.start(geschw)



        if table == 'schaechte':
            x_deckel_neu = []

            for i in x_deckel:
                if round(i,2) not in x_deckel_neu:
                    x_deckel_neu.append(round(i,2))


            for schacht, xkoordinate in zip(liste, x_deckel_neu):
                sql = 'SELECT wasserstand,zeitpunkt FROM lau_gl_s WHERE KNOTEN=?'
                data = (schacht,)

                try:
                    self.db_erg_curs.execute(sql, data)
                except:
                    iface.messageBar().pushMessage("Error",
                                                   "Daten konnten nicht ausgelesen werden",
                                                   level=Qgis.MessageLevel.Critical)
                wasserstaende = self.db_erg_curs.fetchall()

                for wasserstand, zeitpunkt_t in wasserstaende:
                    try:
                        if '.' in zeitpunkt_t:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t[:zeitpunkt_t.index('.')+7], "%Y-%m-%d %H:%M:%S.%f"
                            )
                        else:
                            zeitpunkt = datetime.datetime.strptime(
                                zeitpunkt_t, "%Y-%m-%d %H:%M:%S"
                            )
                    except BaseException as err:
                        iface.messageBar().pushMessage("Error",
                                                       f"Konvertierung vom Zeitpunkt fehlgeschlagen (5)\n{err=}\n{zeitpunkt_t}",
                                                       level=Qgis.MessageLevel.Critical)
                        logger.error(f"Konvertierung vom Zeitpunkt fehlgeschlagen (5)\n{err=}\n{zeitpunkt_t}")
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

            self.horizontalSlider_3.setMinimum(0)
            self.horizontalSlider_3.setMaximum(len(zeit))

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

            new_plot.set_xlabel('Länge [m]')
            new_plot.set_ylabel('Höhe [m NHN]')
            x_deckel_neu = []
            new_plot.plot(x_deckel, y_deckel_n, color="black", label='Deckel')
            new_plot.plot(x_sohle, y_sohle_n, color="black", label='Kanalsohle')
            new_plot.plot(x_sohle2, y_sohle2_n, color="black", label='Kanalscheitel')

            name_neu = []
            y_label_neu = []

            for i in x_deckel:
                if round(i, 2) not in x_deckel_neu:
                    x_deckel_neu.append(round(i, 2))

            for i in name:
                if i not in name_neu:
                    name_neu.append(i)

            for i in y_label:
                if i not in y_label_neu:
                    y_label_neu.append(i)

            for x, y, nam in zip(x_deckel_neu, y_label_neu, name_neu):
                new_plot.annotate(nam, (x, y),
                                  textcoords="offset points",
                                  xytext=(-10, 0),
                                  rotation=90,
                                  ha='center')

            new_plot.vlines(x_deckel, y_sohle, y_deckel, color="red", linestyles='solid', label='Schacht',
                            linewidth=5)
            new_plot.vlines(x_deckel_2, y_sohle_2, y_deckel_3, color="gray", linestyles='solid',
                            label='fiktiver Schacht',
                            linewidth=5)

            (wasserstand,) = new_plot.plot([], [], color="blue", label='Wasserstand')

            self.t = anf
            self.max_t = len(zeit)

            def animate():

                if self.t >= self.max_t:
                    self.stop_animation()
                    return

                wasserstand.set_data(x_liste[self.t], y_liste[self.t])

                timestamp = zeit[self.t]
                time = timestamp.strftime("%d.%m.%Y %H:%M:%S")[:-3]

                if label_4 is not None:
                    label_4.setText(time)
                if not self.horizontalSlider_3.isSliderDown():
                    self.horizontalSlider_3.blockSignals(True)
                    self.horizontalSlider_3.setValue(self.t)
                    self.horizontalSlider_3.blockSignals(False)
                self.canv_2.draw_idle()
                self.t += 1

            self.timer = QTimer()
            self.timer.timeout.connect(animate)
            self.timer.start(geschw)

        self.canv_2.flush_events()
        self.pushButton_4.setDefault(True)
        QtCore.QTimer.singleShot(100, self.pushButton_4.setFocus)