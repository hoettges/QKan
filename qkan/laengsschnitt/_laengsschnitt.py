import logging
import sys
import re
import xml.etree.ElementTree as ElementTree
from typing import Dict, Iterator, Tuple, Union
from qgis.utils import iface
from qgis.core import Qgis
import os
import codecs
import array
import math

import win32com.client
import pythoncom
from win32com.client import VARIANT

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from qkan import QKan
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.database.qkan_utils import get_qkanlayer_attributes
from .dijkstra import find_route


logger = logging.getLogger("QKan.laengs.import")


#TODO: mit einpflegen, dass die Geländehöhe von meheren DGM Layern angezeigt wird


class LaengsTask:
    def __init__(self, db_qkan: DBConnection, file: str, fig: plt.figure, canv:FigureCanvas):
        self.db_qkan = db_qkan
        self.fig = fig
        self.canv = canv

        self.file = file


    def run(self) -> bool:
        self.zeichnen()

    def zeichnen(self):
        #hier wird der Längsschnitt in das Fenster gezeichnet

        figure = self.fig
        figure.clear()
        new_plot = figure.add_subplot(111)

        #liste mit x werten der haltungen
        #liste mit y werten der haltungen

        # data = [
        #     ['1704', 'E119027', 'E119019', 0.75, 0.5, 54.33, 75.88, 75.75, 78.66, 78.52, 162.05, 75.88, 75.75, 0.000],
        #     ['1711', 'E119028', 'E119027', 0.75, 0.5, 54.13, 75.92, 75.88, 78.74, 78.66, 107.92, 75.92, 75.88, 75.88],
        #     ['1712', 'E119029', 'E119028', 0.75, 0.5, 54.04, 76.11, 75.92, 78.97, 78.74, 53.880, 76.11, 75.92, 75.92],
        #     ['1713', 'E119030', 'E119029', 0.75, 0.5, 53.88, 76.40, 76.11, 79.30, 78.97, 0.0000, 76.40, 76.11, 76.11]]
        #
        # x_sohle = []
        # y_sohle = []
        # x_sohle2 = []
        # y_sohle2 = []
        # x_deckel = []
        # y_deckel = []
        # laenge1 = 0
        # laenge2 = 0
        #
        # for attr in data:
        #     (haltnam_ansi, schoben_ansi, schunten_ansi, hoehe, breite, laenge, sohleoben, sohleunten,
        #      deckeloben, deckelunten, laengesum, sohle_schacht_oben, sohle_schacht_unten, sohle_hal_abgehend) = \
        #         ['NULL' if el is None else el for el in attr]
        #
        #     (haltnam, schoben, schunten) = \
        #         [tt for tt in (haltnam_ansi, schoben_ansi, schunten_ansi)]
        #
        #     laenge2 += laenge
        #
        #     y_sohle.append(sohleoben)
        #     y_sohle.append(sohleunten)
        #     x_sohle.append(laenge1)
        #     x_sohle.append(laenge2)
        #
        #     y_sohle2.append(sohleoben+hoehe)
        #     y_sohle2.append(sohleunten+hoehe)
        #     x_sohle2.append(laenge1)
        #     x_sohle2.append(laenge2)
        #
        #     y_deckel.append(deckeloben)
        #     y_deckel.append(deckelunten)
        #     x_deckel.append(laenge1)
        #     x_deckel.append(laenge2)
        #
        #     laenge1 += laenge

       # new_plot.plot(x_deckel, y_deckel, label='Deckel')
       # new_plot.plot(x_sohle, y_sohle, label='Sohle')
       # new_plot.plot(x_sohle2, y_sohle2, label='Sohle')

       # plt.vlines(x_deckel, y_sohle, y_deckel, linestyles='solid', label='Schacht', linewidth=5)
       # new_plot.legend()

        #aktuellen layer auswählen

        layer = iface.activeLayer()
        x = layer.source()

        #mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        dbname, table, geom, sql = get_qkanlayer_attributes(x)


        #selektierte elemente anzeigen
        selected = layer.selectedFeatures()
        liste=[]

        if table not in ['schaechte', 'haltungen']:
            iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.Critical)
            return

        if table == 'schaechte':
            for f in selected:
                x = f['schnam']
                liste.append(x)

        if table == 'haltungen':
            for f in selected:
                x = f['schoben']
                x2 = f['schunten']
                if x not in liste:
                    liste.append(x)
                if x2 not in liste:
                    liste.append(x2)

        route = find_route(self.file, liste)
        # route = (['2747.1J55', '2747.1J56', '2747.1J57'], ['M2747.1J55', 'M2747.1J56'])
        x_sohle = []
        y_sohle = []
        x_sohle2 = []
        y_sohle2 = []
        x_deckel = []
        y_deckel = []
        y_label = []
        name = []
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
                        h.entwart
                    FROM haltungen AS h,
                        schaechte AS schob,
                        schaechte AS schun
                    WHERE schob.schnam = h.schoben AND schun.schnam = h.schunten AND haltnam = {}
                    """.format("'"+str(i)+"'")

            if not self.db_qkan.sql(sql, "laengsschnitt: Datenbankzugriff nicht möoeglich"):
                return

            for attr in self.db_qkan.fetchall():
                schoben = attr[0]
                hoehe = attr[1]
                schunten = attr[2]
                laenge = attr[3]
                deckeloben = attr[4]
                sohleoben = attr[5]
                deckelunten = attr[6]
                sohleunten = attr[7]
                entwart = attr[8]

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

                y_label.append((deckeloben+sohleoben)/2)
                y_label.append((deckelunten+sohleunten)/2)

                laenge1 += laenge
                name.append(schoben)
                name.append(schunten)

        farbe = 'black'
        if entwart == 'MW' or 'KM' or 'Mischwasser':
            farbe = 'pink'

        elif entwart == 'RW' or 'KR' or 'Regenwasser':
            farbe = 'blue'

        elif entwart == 'SW' or 'KS' or 'Schmutzwasser':
            farbe = 'red'

        new_plot.plot(x_deckel, y_deckel, color="black", label='Deckel')
        new_plot.plot(x_sohle, y_sohle, color=farbe, label='Kanalsohle')
        new_plot.plot(x_sohle2, y_sohle2, color=farbe, label='Kanalscheitel')

        for x, y, nam in zip(x_deckel, y_label, name):

            plt.annotate(nam, (x, y),
                         textcoords="offset points",
                         xytext=(-10, 0),
                         rotation=90,
                         ha='center')

        plt.vlines(x_deckel, y_sohle, y_deckel, color="red", linestyles='solid', label='Schacht', linewidth=5)
        plt.xlabel('Länge [m]')
        plt.ylabel('Höhe [m NHN]')
        new_plot.legend()

    def cad(self):
        pass

        #wie oben elemente wählen
        #daten für autocad aufbereiten
        #autocad benötigt andere daten als matplotlib (Koordinatenpaare erwartet!)
        #cad anbindung starten
        #längssschnitt in cad erstellen

        try:
            acad = win32com.client.Dispatch('AutoCAD.Application')
            acad.Visible = True
        except WindowsError:
            print('Autocad wird gestartet. Das kann ca. eine halbe Minute dauern...')
            acad = win32com.client.CreateObject('AutoCAD.Application')
            acad = win32com.client.GetActiveObject('AutoCAD.Application')  # scheint zwar doppelt,
            # aber sonst erscheint ein Fehler
            acad.Visible = True
        except BaseException as e:
            print(e)

        # Prüfen, ob schon eine Datei offen ist. Falls nicht, wird eine neue Datei angelegt.

        if acad.Documents.Count > 0:
            doc = acad.ActiveDocument
            print("Eine Datei ist bereits offen")
        else:
            print("Eine neue Datei wird angelegt")
            doc = acad.Documents.Add()

        print("Bitte klicken Sie in der AutoCAD-Datei auf einen Punkt!")
        x0, y0, z0 = doc.Utility.GetPoint()  # z0 wird nicht benötigt
        print('Geklickt: ({},{})'.format(x0, y0))


        #wie untenstehenden für die Linien sowie auch für alle anderen Sachene erweitern
        #Graphen zeichnen lasse
        #Beschriftung einfügen

        doc.SendCommand("LINIE " "1,1 " "3,5\n" "5,-2\n" "\n")



