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

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
import matplotlib.animation as animation
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.database.qkan_utils import get_qkanlayer_attributes
from .dijkstra import find_route



logger = logging.getLogger("QKan.laengs.import")


#TODO: mit einpflegen, dass die Geländehöhe von meheren DGM Layern angezeigt wird


class LaengsTask:
    def __init__(self, db_qkan: DBConnection, file: str, fig: plt.figure, canv: FigureCanvas, fig_2: plt.figure, canv_2: FigureCanvas, fig_3: plt.figure, canv_3: FigureCanvas, selected, auswahl, point, massstab, features, db_erg, ausgabe):
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
        #TODO: datenbank anbindung

        self.db_erg = spatialite_connect(self.db_erg)
        self.db_erg_curs = self.db_erg.cursor()

    def run(self) -> bool:
        self.zeichnen()

    def zeichnen(self):
        #hier wird der Längsschnitt in das Fenster gezeichnet
        figure = self.fig
        figure.clear()
        plt.figure(figure.number)
        new_plot = figure.add_subplot(111)

        #aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        #mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        dbname, table, geom, sql = get_qkanlayer_attributes(x)


        #selektierte elemente anzeigen
        self.selected = layer.selectedFeatures()
        for i in self.selected:
            attrs = i["pk"]
            self.features.append(attrs)

        liste=[]

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
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)

        route = find_route(self.db_qkan, liste)
        logger.debug(f'zeichnen.ausgewaehlt: {liste}')
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
        laenge1 = 0
        laenge2 = 0

        if route is None:
            iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente Ausgewählt', level=Qgis.Critical)
            x = 'nicht erstellt'
            return x

        #iface.messageBar().pushMessage("Fehler", str(route), level=Qgis.Critical)

        for i in route[1]:

            sql = """
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
                        h.sohleunten
                    FROM haltungen AS h,
                        schaechte AS schob,
                        schaechte AS schun
                    WHERE schob.schnam = h.schoben AND schun.schnam = h.schunten AND haltnam = ?
                    """

            if not self.db_qkan.sql(sql, "laengsschnitt.zeichnen", parameters=(str(i),)):
                logger.error(f"{__file__}: Fehler beim  in Zeile 137: Datenbankzugriff nicht möglich")
                x = 'nicht erstellt'
                return x

            for attr in self.db_qkan.fetchall():
                schoben = attr[0]
                hoehe = attr[1]
                schunten = attr[2]
                laenge = attr[3]
                deckeloben = attr[4]
                sohleoben = attr[14]
                deckelunten = attr[6]
                sohleunten = attr[15]
                entwart = attr[8]
                haltnam = attr[9]
                breite = attr[10]
                material = attr[11]
                strasse = attr[12]
                haltungstyp = attr[13]

                laenge2 += laenge

                y_sohle.append(sohleoben)
                y_sohle.append(sohleunten)
                x_sohle.append(laenge1)
                x_sohle.append(laenge2)

                y_sohle2.append(sohleoben + hoehe)
                y_sohle2.append(sohleunten + hoehe)
                x_sohle2.append(laenge1)
                x_sohle2.append(laenge2)

                y_deckel.append(deckeloben)
                y_deckel.append(deckelunten)
                x_deckel.append(laenge1)
                x_deckel.append(laenge2)

                y_label.append((deckeloben+sohleoben-hoehe)/2)
                y_label.append((deckelunten+sohleunten-hoehe)/2)

                laenge1 += laenge
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

        farbe = 'black'
        if entwart == 'MW' or entwart =='KM' or entwart =='Mischwasser':
            farbe = 'pink'

        elif entwart == 'RW' or entwart =='KR' or entwart =='Regenwasser':
            farbe = 'blue'

        elif entwart == 'SW' or entwart =='KS' or entwart =='Schmutzwasser':
            farbe = 'red'

        data = [schoben_l, schunten_l, laenge_l, entwart_l, hoehe_l, breite_l, material_l, strasse_l, haltungstyp_l]

        columns = tuple(haltnam_l)
        rows = ('Schacht oben', 'Schacht unten', 'Länge [m]', 'Entwässerungsart', 'Höhe [m]', 'Breite [m]', 'Material', 'Strasse', 'Typ')

        new_plot.plot(x_deckel, y_deckel, color="black", label='Deckel')
        new_plot.plot(x_sohle, y_sohle, color=farbe, label='Kanalsohle')
        new_plot.plot(x_sohle2, y_sohle2, color=farbe, label='Kanalscheitel')

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

        plt.vlines(x_deckel, y_sohle, y_deckel, color="red", linestyles='solid', label='Schacht', linewidth=5)
        plt.xlabel('Länge [m]')
        plt.ylabel('Höhe [m NHN]')
        new_plot.legend()
        plt.table(cellText=data, rowLabels=rows, colLabels=columns, loc='bottom', bbox=[0.0, -0.65, 1, 0.45], cellLoc='center')
        plt.subplots_adjust(top=0.98,
                            bottom=0.4,
                            left=0.13,
                            right=0.99,
                            hspace=0.2,
                            wspace=0.2)

        self.auswahl[figure.number] = self.selected


    def show(self):
        # selektierte elemente anzeigen
        layer = iface.activeLayer()
        layer.selectByExpression("pk in {}".format(tuple(self.features)))


    def cad(self):
        points = self.point.split(",", 1)
        massstab_liste = self.massstab.split(":", 1)

        #Koordinaten für Einfügepunkt
        pointx = float(points[0])
        pointy = float(points[1])
        iface.messageBar().pushMessage("Fehler", str(pointx), level=Qgis.Critical)
        iface.messageBar().pushMessage("Fehler", str(pointy), level=Qgis.Critical)
        # Maßstab
        massstab = float(massstab_liste[1])

        layer = iface.activeLayer()
        x = layer.source()

        # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        dbname, table, geom, sql = get_qkanlayer_attributes(x)

        # selektierte elemente anzeigen

        figure = self.fig
        self.selected = self.auswahl[figure.number]

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
                x = f['schoben']
                x2 = f['schunten']
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)

        route = find_route(self.db_qkan, liste)

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
        laenge1 = 0
        laenge2 = 0


        if route is None:
            iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente Ausgewählt', level=Qgis.Critical)
            return

        for i in route[1]:

            sql = """
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
                                h.sohleunten
                            FROM haltungen AS h,
                                schaechte AS schob,
                                schaechte AS schun
                            WHERE schob.schnam = h.schoben AND schun.schnam = h.schunten AND haltnam = {}
                            """.format("'" + str(i) + "'")

            if not self.db_qkan.sql(sql, "laengsschnitt: Datenbankzugriff nicht möglich"):
                return

            for attr in self.db_qkan.fetchall():
                schoben = attr[0]
                hoehe = attr[1]
                schunten = attr[2]
                laenge = attr[3]
                deckeloben = attr[4]
                sohleoben = attr[14]
                deckelunten = attr[6]
                sohleunten = attr[15]
                entwart = attr[8]
                haltnam = attr[9]
                breite = attr[10]
                material = attr[11]
                strasse = attr[12]
                haltungstyp = attr[13]
                hschoben = attr[14]
                hschunten = attr[15]

                laenge2 += laenge

                z_sohle_h.append(hschoben)
                z_sohle_h.append(hschunten)

                y_sohle.append(sohleoben+pointy)
                y_sohle.append(sohleunten+pointy)
                x_sohle.append((laenge1/massstab)+pointx)
                x_sohle.append((laenge2/massstab)+pointx)

                y_sohle2.append(sohleoben + hoehe+pointy)
                y_sohle2.append(sohleunten + hoehe+pointy)
                x_sohle2.append((laenge1/massstab)+pointx)
                x_sohle2.append((laenge2/massstab)+pointx)

                y_deckel.append(deckeloben+pointy)
                y_deckel.append(deckelunten+pointy)
                x_deckel.append((laenge1/massstab)+pointx)
                x_deckel.append((laenge2/massstab)+pointx)

                y_label.append(((deckeloben + sohleoben) / 2)+pointy)
                y_label.append(((deckelunten + sohleunten) / 2)+pointy)

                laenge1 += laenge
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

        #deckelkoordinaten
        for i, j in zip(x_deckel, y_deckel):
            deckel += " " + str(i) + "," + str(j)

        deckel += "\n" "\n"

        #scheitelkoordinaten
        for i, j in zip(x_sohle2, y_sohle2):
            scheitel += " " + str(i) + "," + str(j)

        scheitel += "\n" "\n"

        #sohlenkoordinaten
        for i, j in zip(x_sohle, y_sohle):
            sohle += " " + str(i) + "," + str(j)

        sohle += "\n" "\n"

        #CSV-Tabelle erstellen
        #path = Path(__file__).parent.absolute()
        #path = str(path)+'/some.csv'
        #with open(path, 'w', newline='') as f:
         #   writer = csv.writer(f)
          #  rows = tuple(haltnam_l)
           # writer.writerow(rows)

            #data = [schoben_l, schunten_l, laenge_l, entwart_l, hoehe_l, breite_l, material_l, strasse_l, haltungstyp_l]
            #for i in data:
             #   writer.writerow(i)

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

            # schacht linien einzeichnen
            for i, j, z in zip(x_deckel, y_sohle, y_deckel):
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
        #TODO: max wasserstand in den Plott zeichnen?
        figure = self.fig_3
        figure.clear()
        plt.figure(figure.number)
        new_plot = figure.add_subplot(111)

        # aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        dbname, table, geom, sql = get_qkanlayer_attributes(x)

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

            if self.ausgabe == 'Wasserstand':
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
        # hier wird der Längsschnitt in das Fenster gezeichnet
        figure = self.fig_2
        figure.clear()
        plt.figure(figure.number)
        new_plot = figure.add_subplot(111)

        # aktuellen layer auswählen
        layer = iface.activeLayer()
        x = layer.source()

        # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        dbname, table, geom, sql = get_qkanlayer_attributes(x)

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
                x = f['schoben']
                x2 = f['schunten']
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)

        route = find_route(self.db_qkan, liste)
        logger.debug(f'zeichnen.ausgewaehlt: {liste}')
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
        laenge1 = 0
        laenge2 = 0

        if route is None:
            iface.messageBar().pushMessage("Fehler", 'Es wurden keine Elemente Ausgewählt', level=Qgis.Critical)
            x = 'nicht erstellt'
            return x

        # iface.messageBar().pushMessage("Fehler", str(route), level=Qgis.Critical)

        for i in route[1]:

            sql = """
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
                                h.sohleunten
                            FROM haltungen AS h,
                                schaechte AS schob,
                                schaechte AS schun
                            WHERE schob.schnam = h.schoben AND schun.schnam = h.schunten AND haltnam = ?
                            """

            if not self.db_qkan.sql(sql, "laengsschnitt.zeichnen", parameters=(str(i),)):
                logger.error(f"{__file__}: Fehler beim  in Zeile 137: Datenbankzugriff nicht möglich")
                x = 'nicht erstellt'
                return x

            for attr in self.db_qkan.fetchall():
                schoben = attr[0]
                hoehe = attr[1]
                schunten = attr[2]
                laenge = attr[3]
                deckeloben = attr[4]
                sohleoben = attr[14]
                deckelunten = attr[6]
                sohleunten = attr[15]
                entwart = attr[8]
                haltnam = attr[9]
                breite = attr[10]
                material = attr[11]
                strasse = attr[12]
                haltungstyp = attr[13]

                laenge2 += laenge

                y_sohle.append(sohleoben)
                y_sohle.append(sohleunten)
                x_sohle.append(laenge1)
                x_sohle.append(laenge2)

                y_sohle2.append(sohleoben + hoehe)
                y_sohle2.append(sohleunten + hoehe)
                x_sohle2.append(laenge1)
                x_sohle2.append(laenge2)

                y_deckel.append(deckeloben)
                y_deckel.append(deckelunten)
                x_deckel.append(laenge1)
                x_deckel.append(laenge2)

                y_label.append((deckeloben + sohleoben - hoehe) / 2)
                y_label.append((deckelunten + sohleunten - hoehe) / 2)

                laenge1 += laenge
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

        farbe = 'black'
        if entwart == 'MW' or entwart == 'KM' or entwart == 'Mischwasser':
            farbe = 'pink'

        elif entwart == 'RW' or entwart == 'KR' or entwart == 'Regenwasser':
            farbe = 'blue'

        elif entwart == 'SW' or entwart == 'KS' or entwart == 'Schmutzwasser':
            farbe = 'red'

        data = [schoben_l, schunten_l, laenge_l, entwart_l, hoehe_l, breite_l, material_l, strasse_l, haltungstyp_l]

        columns = tuple(haltnam_l)
        rows = ('Schacht oben', 'Schacht unten', 'Länge [m]', 'Entwässerungsart', 'Höhe [m]', 'Breite [m]', 'Material',
                'Strasse', 'Typ')

        new_plot.plot(x_deckel, y_deckel, color="black", label='Deckel')
        new_plot.plot(x_sohle, y_sohle, color=farbe, label='Kanalsohle')
        new_plot.plot(x_sohle2, y_sohle2, color=farbe, label='Kanalscheitel')

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

        plt.vlines(x_deckel, y_sohle, y_deckel, color="red", linestyles='solid', label='Schacht', linewidth=5)
        plt.xlabel('Länge [m]')
        plt.ylabel('Höhe [m NHN]')
        new_plot.legend()

        haltungen = {}
        schaechte = {}
        if table == 'haltungen':
            for haltung in liste:
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
                        wasserstandoben=wasserstandoben, wasserstandunten=wasserstandunten
                    )


            #x_liste = []
            #y_liste = []
            #for h in liste:
            #    for x, y in haltungen.items():
            #        x_liste.append(x)
            #        y_liste.append(y[h]['wasserstandoben'])
            #        y_liste.append(y[h]['wasserstandunten'])
            #iface.messageBar().pushMessage("Error", str(x_deckel),
            #                               level=Qgis.Critical)
            #iface.messageBar().pushMessage("Error", str(y_liste),
            #                               level=Qgis.Critical)

        if table == 'schaechte':
            for schacht in liste:
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
                    schaechte[zeitpunkt][schacht] = wasserstand
