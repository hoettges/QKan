from qgis.utils import spatialite_connect

from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger
import matplotlib.pyplot as plt
import numpy as np

from qgis.core import (
    Qgis,
    QgsProject,
    QgsVectorLayer,
    QgsDataSourceUri,
)
from qgis.utils import iface, spatialite_connect


logger = get_logger("QKan.xml.info")


class Info:
    def __init__(self, fig, canv, fig_2, canv_2, fig_3, canv_3, fig_4, canv_4, db_qkan: DBConnection):
        self.db_qkan = db_qkan
        self.anz_haltungen = 0
        self.anz_schaechte = 0
        self.laenge_haltungen = 0
        self.anz_teilgeb = 0
        path = db_qkan.dbname
        db = spatialite_connect(path)
        self.curs = db.cursor()
        self.canv = canv
        self.fig = fig
        self.canv_2 = canv_2
        self.fig_2 = fig_2
        self.canv_3 = canv_3
        self.fig_3 = fig_3
        self.canv_4 = canv_4
        self.fig_4 = fig_4


    def _infos(self) -> None:
        #TODO: Anzeige anpassen um die Auswahl eines Teilgebietes zu ermöglichen!

        figure_4 = self.fig_4
        figure_4.clear()
        plt.figure(figure_4.number)
        new_plot = figure_4.add_subplot(511)

        #Tabelle mit Algemeinen Informationen

        entwart_list = []
        sql = """select count() from haltungen"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select sum(laenge) from haltungen"""

        if not self.db_qkan.sql(sql):
            return

        l_haltungen_ges = round(self.db_qkan.fetchall()[0][0]/1000., 2)

        sql = """select sum(laenge), entwart, count() from haltungen group by entwart """

        if not self.db_qkan.sql(sql):
            return

        laenge = []
        anzahl = []

        for i in self.db_qkan.fetchall():
            entwart_list.append(i[1])
            laenge.append(round(i[0]/1000., 2))
            anzahl.append(i[2])

        laenge.append(l_haltungen_ges)
        anzahl.append(anz_haltungen_ges)
        entwart_list.append("Gesamt")

        data = [
            laenge,
            anzahl
        ]

        rows = ["km", "Anzahl"]

        new_plot.table(cellText=data, colLabels=entwart_list, rowLabels=rows, loc='center')
        new_plot.axis('off')

        new_plot.set_title("Haltungen", fontsize=10, fontweight='bold', pad=20)

        # Tabelle anzeigen
        self.canv_4.draw()


        #Infos Schächte
        plt.figure(figure_4.number)
        new_plot = figure_4.add_subplot(512)

        # Tabelle mit Algemeinen Informationen

        entwart_list = []
        sql = """select count() from schaechte WHERE schachttyp is 'Schacht'"""

        if not self.db_qkan.sql(sql):
            return

        anz_schaechte = self.db_qkan.fetchall()[0][0]

        sql = """select count(), entwart from schaechte where schachttyp =' Schacht' group by entwart"""

        if not self.db_qkan.sql(sql):
            return

        anzahl_schacht = []

        for i in self.db_qkan.fetchall():
            entwart_list.append(i[1])
            anzahl_schacht.append(i[0])

        anzahl_schacht.append(anz_schaechte)
        entwart_list.append("Gesamt")

        data = [
            anzahl_schacht
        ]

        rows = ["Anzahl Schaechte"]

        new_plot.table(cellText=data, colLabels=entwart_list, rowLabels=rows, loc='center')
        new_plot.axis('off')
        new_plot.set_title("Schächte", fontsize=10, fontweight='bold', pad=20)

        # Tabelle anzeigen
        self.canv_4.draw()


        #Infos Anschlussleitungen
        plt.figure(figure_4.number)
        new_plot = figure_4.add_subplot(513)

        # Tabelle mit Algemeinen Informationen

        data = {}
        entwart_list = []
        sql = """select count() from anschlussleitungen"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select sum(laenge) from anschlussleitungen"""

        if not self.db_qkan.sql(sql):
            return

        l_haltungen_ges = self.db_qkan.fetchall()[0][0]

        if l_haltungen_ges in ['NULL', 'None', None]:

            l_haltungen_ges = 0


        else:
            l_haltungen_ges = round(l_haltungen_ges / 1000.0, 2)

        sql = """select sum(laenge), entwart, count() from anschlussleitungen group by entwart """

        if not self.db_qkan.sql(sql):
            return

        laenge = []
        anzahl = []

        for i in self.db_qkan.fetchall():
            entwart_list.append(i[1])
            laenge.append(round(i[0] / 1000., 2))
            anzahl.append(i[2])

        laenge.append(l_haltungen_ges)
        anzahl.append(anz_haltungen_ges)
        entwart_list.append("Gesamt")

        data = [
            laenge,
            anzahl
        ]

        rows = ["km", "Anzahl"]

        new_plot.table(cellText=data, colLabels=entwart_list, rowLabels=rows, loc='center')
        new_plot.axis('off')
        new_plot.set_title("Anschlussleitungen", fontsize=10, fontweight='bold', pad=20)
        figure_4.tight_layout()
        # Tabelle anzeigen
        self.canv_4.draw()

        #infos Sonderbauwerke

        plt.figure(figure_4.number)
        new_plot = figure_4.add_subplot(514)

        # Tabelle mit Algemeinen Informationen

        data = {}
        entwart_list = []
        sql = """select count() from haltungen"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select sum(laenge) from haltungen"""

        if not self.db_qkan.sql(sql):
            return

        l_haltungen_ges = round(self.db_qkan.fetchall()[0][0] / 1000, 2)

        sql = """select sum(laenge), haltungstyp, count() from haltungen group by haltungstyp """
        if not self.db_qkan.sql(sql):
            return

        laenge = []
        anzahl = []

        for i in self.db_qkan.fetchall():
            entwart_list.append(i[1])
            laenge.append(round(i[0] / 1000., 2))
            anzahl.append(i[2])

        laenge.append(l_haltungen_ges)
        anzahl.append(anz_haltungen_ges)
        entwart_list.append("Gesamt")

        data = [
            laenge,
            anzahl
        ]

        rows = ["km", "Anzahl"]

        new_plot.table(cellText=data, colLabels=entwart_list, rowLabels=rows, loc='center')
        new_plot.set_title("Haltungstyp", fontsize=10, fontweight='bold', pad=20)
        new_plot.axis('off')
        figure_4.tight_layout()

        # Tabelle anzeigen
        self.canv_4.draw()


        # Infos Schachttyp
        plt.figure(figure_4.number)
        new_plot = figure_4.add_subplot(515)

        # Tabelle mit Algemeinen Informationen

        entwart_list = []
        sql = """select count() from schaechte """

        if not self.db_qkan.sql(sql):
            return

        anz_schaechte = self.db_qkan.fetchall()[0][0]

        sql = """select count(), schachttyp from schaechte group by schachttyp """
        if not self.db_qkan.sql(sql):
            return

        anzahl = []

        for i in self.db_qkan.fetchall():
            entwart_list.append(i[1])
            anzahl.append(i[0])

        anzahl.append(anz_schaechte)
        entwart_list.append("Gesamt")

        data = [
            anzahl
        ]

        columns = ("Gesamt",)
        # columns ergänzen um die einzelnen entwässerungsarten
        rows = ["Anzahl Schaechte"]
        # rows mit den Daten aus der Datenbank
        # fig, ax = new_plot.subplots()

        new_plot.table(cellText=data, colLabels=entwart_list, rowLabels=rows, loc='center')
        new_plot.axis('off')
        new_plot.set_title("Schachttypen", fontsize=10, fontweight='bold', pad=20)

        # Tabelle anzeigen
        figure_4.tight_layout()
        self.canv_4.draw()


        # anzahl teilgebiete
        sql = """select count() from teilgebiete"""

        if not self.db_qkan.sql(sql):
            return

        self.anz_teilgeb = self.db_qkan.fetchall()[0][0]

    def handle_click(event, pie_wedges, run_script_callback):
        # TODO: Anpassen, sodass beim Anklicken der Grafik die jeweiligen Daten in QGIS ausgewählt werden!
        for wedge in pie_wedges:
            if wedge.contains_point([event.x, event.y]):
                run_script_callback()
                break

    def anzeigen(self):
        def func(pct, allvals):
            absolute = int(np.round(pct / 100. * np.sum(allvals)))
            return f"{pct:.1f}%\n({absolute:d})"
        figure = self.fig
        figure.clear()
        plt.figure(figure.number)
        new_plot = figure.add_subplot(241)

        #Darstellung Haltungen nach Entwässerungsart bezogen auf km
        data = {}
        entwart_list =[]
        sql = """select count() from haltungen"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select DISTINCT entwart from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)


        data = {k:None for k in entwart_list}

        for i in data.keys():
            sql = f"""select sum(laenge) from haltungen WHERE entwart = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())

        wedges, texts, autotexts = new_plot.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot.set_title('Entwässerungsart')


        #return self.canv, wedges

        # # Event handler for mouse clicks
        # def on_click(event):
        #     # Check if the event was in the pie chart area
        #     if event.inaxes == new_plot:
        #         for wedge in wedges:
        #             if wedge.contains_point((event.x, event.y)):
        #                 index = wedges.index(wedge)
        #                 # Display the label of the clicked wedge
        #                 label = names[index]
        #                 iface.messageBar().pushMessage("Error",
        #                                                str(label),
        #                                                level=Qgis.Critical)
        #                 #funktioniert nur beim ersten Mal anklicken
        #
        #                 layers = QgsProject.instance().mapLayersByName('Haltungen')
        #                 ids = []
        #
        #                 sql = f"""select pk from haltungen where entwart = '{label}'"""
        #
        #                 if not self.db_qkan.sql(sql):
        #                     return
        #                 for attr in self.db_qkan.fetchall():
        #                     ids.append(attr[0])
        #
        #                 layers[0].selectByIds(ids)
        #
        #                 plt.draw()
        #                 #break

        #figure.canvas.mpl_connect('button_press_event', on_click)
        self.canv.draw()

        #Darstellungen Haltungen nach Baujahren

        data = {}
        entwart_list = []
        sql = """select DISTINCT baujahr from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select sum(laenge) from haltungen WHERE baujahr = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot2 = figure.add_subplot(242)
        new_plot2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot2.set_title('Baujahr')
        self.canv.draw()


        # Darstellungen Haltungen nach Durchmesser

        entwart_list = []
        sql = """select DISTINCT hoehe from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select sum(laenge) from haltungen WHERE hoehe = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        total = sum(data.values())
        threshold = 0.1 * total
        daten = {k: v for k, v in data.items() if v >= threshold}
        sonstiges = {k: v for k, v in data.items() if v < threshold}

        if sonstiges:
            daten['Sonstiges'] = sum(sonstiges.values())

        # Daten für das Kreisdiagramm
        names = list(daten.keys())
        values = list(daten.values())

        new_plot2 = figure.add_subplot(243)
        new_plot2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot2.set_title('Durchmesser DN')
        new_plot3 = figure.add_subplot(244)

        if 'Sonstiges' in daten:
            fig, ax2 = plt.subplots()
            sonstiges_names = list(sonstiges.keys())
            sonstiges_values = list(sonstiges.values())

            y_pos = np.arange(len(sonstiges_values))
            box = new_plot3.get_position()
            new_plot3.set_position([box.x0 + 0.05, box.y0, box.width * 0.5, box.height* 0.75])
            new_plot3.barh(y_pos, sonstiges_values, align='center')
            new_plot3.set_yticks(y_pos)
            new_plot3.set_yticklabels(sonstiges_names)
            new_plot3.invert_yaxis()
            new_plot3.set_xlabel('Durchmesser')
            new_plot3.set_title('Details der Kategorie "Sonstiges"')
        new_plot2.autoscale()
        new_plot3.autoscale()
        self.canv.draw()

        #TODO:Darstellung nach Tiefenlage?


        # Darstellungen Haltungen nach Material

        entwart_list = []
        sql = """select DISTINCT material from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select sum(laenge) from haltungen WHERE material = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        total = sum(data.values())
        threshold = 0.1 * total
        daten = {k: v for k, v in data.items() if v >= threshold}
        sonstiges = {k: v for k, v in data.items() if v < threshold}

        if sonstiges:
            daten['Sonstiges'] = sum(sonstiges.values())

        # Daten für das Kreisdiagramm
        names = list(daten.keys())
        values = list(daten.values())

        # Plot
        new_plot2 = figure.add_subplot(245)
        new_plot2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot2.set_title('Material')
        new_plot3 = figure.add_subplot(246)
        if 'Sonstiges' in daten:
            sonstiges_names = list(sonstiges.keys())
            sonstiges_values = list(sonstiges.values())

            y_pos = np.arange(len(sonstiges_values))
            box = new_plot3.get_position()
            new_plot3.set_position([box.x0 + 0.05, box.y0, box.width * 0.5, box.height * 0.75])
            new_plot3.barh(y_pos, sonstiges_values, align='center')
            new_plot3.set_yticks(y_pos)
            new_plot3.set_yticklabels(sonstiges_names)
            new_plot3.invert_yaxis()
            new_plot3.set_xlabel('Material')
            new_plot3.set_title('Details der Kategorie "Sonstiges"')
        new_plot2.autoscale()
        new_plot3.autoscale()
        self.canv.draw()

        # Darstellungen Haltungen nach Profiltyp
        entwart_list = []
        sql = """select DISTINCT profilnam from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select sum(laenge) from haltungen WHERE profilnam = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot3 = figure.add_subplot(247)
        new_plot3.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot3.set_title('Profilart')
        figure.tight_layout()
        self.canv.draw()

        #Haltungen nach Zustandsklasse (Farben nach Zustandsklassen anpassen)
        figure_3 = self.fig_3
        figure_3.clear()
        plt.figure(figure_3.number)
        new_plot_2 = figure_3.add_subplot(121)
        entwart_list = []
        sql = """select sum(laenge) from haltungen_untersucht"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select DISTINCT MIN(max_ZD,max_ZS,max_ZB) from haltungen_untersucht """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            if i != 'None':
                sql = f"""select sum(laenge) from haltungen_untersucht WHERE MIN(max_ZD,max_ZS,max_ZB) = {i}"""

                if not self.db_qkan.sql(sql):
                    return

                anz = self.db_qkan.fetchall()[0][0]

                data[i] = anz

        #TODO: Verbesserung von Jörg einbauen
        #sql = f"""select MIN(max_ZD,max_ZS,max_ZB) as minz, count() as anz from haltungen_untersucht WHERE GROUP BY minz"""

        if 'None' in data.keys():
            del data['None']
        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot_2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot_2.set_title('Zustandsklasse Haltungen')
        figure_3.tight_layout()
        self.canv_3.draw()


        #Zustandsdaten Schächte

        entwart_list = []
        sql = """select count() from schaechte_untersucht"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select DISTINCT MIN(max_ZD,max_ZS,max_ZB) from schaechte_untersucht """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            if i != 'None':
                sql = f"""select count() from schaechte_untersucht WHERE MIN(max_ZD,max_ZS,max_ZB) = {i}"""

                if not self.db_qkan.sql(sql):
                    return

                anz = self.db_qkan.fetchall()[0][0]

                data[i] = anz
        if 'None' in data.keys():
            del data['None']
        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot_2 = figure_3.add_subplot(122)
        new_plot_2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot_2.set_title('Zustandsklasse Schächte')
        figure_3.tight_layout()
        self.canv_3.draw()


        # Darstellung Schächte nach Entwässerungsart
        figure_2 = self.fig_2
        figure_2.clear()
        plt.figure(figure_2.number)
        new_plot_2 = figure_2.add_subplot(131)

        entwart_list = []
        sql = """select count() from schaechte"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select DISTINCT entwart from schaechte """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select count() from schaechte WHERE entwart = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot_2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot_2.set_title('Entwässerungsart')
        figure_2.tight_layout()
        self.canv_2.draw()

        # Darstellungen Schächte nach Baujahren
        data = {}
        entwart_list = []
        sql = """select DISTINCT baujahr from schaechte """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select count() from schaechte WHERE baujahr = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot2 = figure_2.add_subplot(132)
        new_plot2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot2.set_title('Baujahr')
        figure_2.tight_layout()
        self.canv_2.draw()


        # Darstellung Schächte nach Material
        entwart_list = []
        sql = """select DISTINCT material from schaechte """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select count() from schaechte WHERE material = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot2 = figure_2.add_subplot(133)
        new_plot2.pie(values, labels=names, autopct=lambda pct: func(pct, values))
        new_plot2.set_title('Material')
        figure_2.tight_layout()
        self.canv_2.draw()

    def _suewvo(self):
        date = self.date+'%'
        self.bew_art = 'DWA'
        self.laenge_haltungen_rw = 0
        self.laenge_haltungen_sw = 0
        self.laenge_haltungen_mw = 0
        self.haltungen_0_rw = 0
        self.haltungen_1_rw = 0
        self.haltungen_2_rw = 0
        self.haltungen_3_rw = 0
        self.haltungen_4_rw = 0
        self.haltungen_5_rw = 0
        self.laenge_haltungen_untersuch_rw = 0
        self.laenge_haltungen_untersuch_bj_rw = 0
        self.laenge_haltungen_saniert_rw = 0
        self.haltungen_0_sw = 0
        self.haltungen_1_sw = 0
        self.haltungen_2_sw = 0
        self.haltungen_3_sw = 0
        self.haltungen_4_sw = 0
        self.haltungen_5_sw = 0
        self.laenge_haltungen_untersuch_sw = 0
        self.laenge_haltungen_untersuch_bj_sw = 0
        self.laenge_haltungen_saniert_sw = 0
        self.haltungen_0_mw = 0
        self.haltungen_1_mw = 0
        self.haltungen_2_mw = 0
        self.haltungen_3_mw = 0
        self.haltungen_4_mw = 0
        self.haltungen_5_mw = 0
        self.laenge_haltungen_untersuch_mw = 0
        self.laenge_haltungen_untersuch_bj_mw = 0
        self.laenge_haltungen_saniert_mw = 0
        self.anz_schaechte_rw = 0
        self.anz_schaechte_sw = 0
        self.anz_schaechte_mw = 0
        self.anz_schaechte_0_rw = 0
        self.anz_schaechte_1_rw = 0
        self.anz_schaechte_2_rw = 0
        self.anz_schaechte_3_rw = 0
        self.anz_schaechte_4_rw = 0
        self.anz_schaechte_5_rw = 0
        self.anz_schaechte_untersuch_rw = 0
        self.anz_schaechte_untersuch_bj_rw = 0
        self.anz_schaechte_saniert_rw = 0
        self.anz_schaechte_0_sw = 0
        self.anz_schaechte_1_sw = 0
        self.anz_schaechte_2_sw = 0
        self.anz_schaechte_3_sw = 0
        self.anz_schaechte_4_sw = 0
        self.anz_schaechte_5_sw = 0
        self.anz_schaechte_untersuch_sw = 0
        self.anz_schaechte_untersuch_bj_sw = 0
        self.anz_schaechte_saniert_sw = 0
        self.anz_schaechte_0_mw = 0
        self.anz_schaechte_1_mw = 0
        self.anz_schaechte_2_mw = 0
        self.anz_schaechte_3_mw = 0
        self.anz_schaechte_4_mw = 0
        self.anz_schaechte_5_mw = 0
        self.anz_schaechte_untersuch_mw = 0
        self.anz_schaechte_untersuch_bj_mw = 0
        self.anz_schaechte_saniert_mw = 0

        #testen ob zustandsbewertungen vorhanden sind
        sql = """
                   SELECT
                    pk
                    FROM
                    haltungen_untersucht
                   """
        if not self.db_qkan.sql(sql):
            return

        if len(self.db_qkan.fetchall()) != 0:
            #abfragen Haltungen

            # anzahl lange haltungen RW
            sql = """
                       SELECT
                        SUM(laenge)
                        FROM
                        haltungen
                        WHERE entwart = 'Regenwasser'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.laenge_haltungen_rw = round(attr[0][0]/1000, 2)

            # anzahl lange haltungen SW
            sql = """
                                   SELECT
                                    SUM(laenge)
                                    FROM
                                    haltungen
                                    WHERE entwart = 'Schmutzwasser'
                                   """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.laenge_haltungen_sw = round(attr[0][0]/1000, 2)

            # anzahl lange haltungen MW
            sql = """
                       SELECT
                        SUM(laenge)
                        FROM
                        haltungen
                        WHERE entwart = 'Mischwasser'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.laenge_haltungen_mw = round(attr[0][0]/1000, 2)

            sql = """
                        SELECT * FROM
                        sqlite_master
                        WHERE
                        name = 'haltungen_untersucht_bewertung' and type = 'table'
                        """
            if not self.db_qkan.sql(sql):
                return

            if len(self.db_qkan.fetchall()) != 0:

                sql = """
                            SELECT MAX(haltungen_untersucht_bewertung.datenart)

                            FROM haltungen_untersucht_bewertung
                                   """
                if not self.db_qkan.sql(sql):
                    return

                attr = self.db_qkan.fetchall()
                if attr[0][0] != None and attr != []:
                    self.bew_art = attr[0][0]

                # laenge haltungen 0
                sql = """
                            SELECT haltungen_untersucht_bewertung.haltnam,
                            haltungen.entwart,
                            haltungen.laenge
                            FROM haltungen_untersucht_bewertung,haltungen
                            WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 0 and haltungen_untersucht_bewertung.untersuchtag like ?
                                      """
                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass

                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_0_rw = round(rw/1000,2)
                        self.haltungen_0_sw = round(sw/1000,2)
                        self.haltungen_0_mw = round(mw/1000,2)

                # laenge haltungen 1
                sql = """
                                SELECT haltungen_untersucht_bewertung.haltnam,
                                haltungen.entwart,
                                haltungen.laenge
                                FROM haltungen_untersucht_bewertung,haltungen
                                WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 1 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                          """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_1_rw = round(rw/1000,2)
                        self.haltungen_1_sw = round(sw/1000,2)
                        self.haltungen_1_mw = round(mw/1000,2)

                # laenge haltungen 2
                sql = """
                        SELECT haltungen_untersucht_bewertung.haltnam,
                        haltungen.entwart,
                        haltungen.laenge
                        FROM haltungen_untersucht_bewertung,haltungen
                        WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 2 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                  """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_2_rw = round(rw/1000,2)
                        self.haltungen_2_sw = round(sw/1000,2)
                        self.haltungen_2_mw = round(mw/1000,2)

                # laenge haltungen 3
                sql = """
                                SELECT haltungen_untersucht_bewertung.haltnam,
                                haltungen.entwart,
                                haltungen.laenge
                                FROM haltungen_untersucht_bewertung,haltungen
                                WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 3 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                          """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_3_rw = round(rw/1000,2)
                        self.haltungen_3_sw = round(sw/1000,2)
                        self.haltungen_3_mw = round(mw/1000,2)

                # laenge haltungen 4
                sql = """
                            SELECT haltungen_untersucht_bewertung.haltnam,
                            haltungen.entwart,
                            haltungen.laenge
                            FROM haltungen_untersucht_bewertung,haltungen
                            WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 4 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                      """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_4_rw = round(rw/1000,2)
                        self.haltungen_4_sw = round(sw/1000,2)
                        self.haltungen_4_mw = round(mw/1000,2)

                # laenge haltungen 5
                sql = """
                            SELECT haltungen_untersucht_bewertung.haltnam,
                            haltungen.entwart,
                            haltungen.laenge
                            FROM haltungen_untersucht_bewertung,haltungen
                            WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 5 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                      """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_5_rw = round(rw/1000,2)
                        self.haltungen_5_sw = round(sw/1000,2)
                        self.haltungen_5_mw = round(mw/1000,2)


       #Abfragen Schaechte
        sql = """
                   SELECT
                    pk
                    FROM
                    schaechte_untersucht
                   """
        if not self.db_qkan.sql(sql):
            return

        if len(self.db_qkan.fetchall()) != 0:
            # abfragen schaechte

            # anzahl schaechte rw
            sql = """
                       SELECT
                       count(*)
                        FROM
                        schaechte
                        WHERE entwart ='Regenwasser' OR entwart = 'KR'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.anz_schaechte_rw = attr[0][0]

            # anzahl schaechte sw
            sql = """
                           SELECT
                           count(*)
                            FROM
                            schaechte
                            WHERE entwart ='Schmutzwasser' OR entwart = 'KS'
                           """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.anz_schaechte_sw = attr[0][0]

            # anzahl schaechte mw
            sql = """
                       SELECT
                       count(*)
                        FROM
                        schaechte
                        WHERE entwart ='Mischwasser' OR entwart = 'KM'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.anz_schaechte_mw = attr[0][0]

            sql = """
            SELECT * FROM
            sqlite_master
            WHERE
            name = 'schaechte_untersucht_bewertung' and type = 'table'
            """
            if not self.db_qkan.sql(sql):
                return

            if len(self.db_qkan.fetchall()) != 0:
                sql = """
                                                            SELECT MAX(schaechte_untersucht_bewertung.datenart)

                                                            FROM schaechte_untersucht_bewertung
                                                                   """
                if not self.db_qkan.sql(sql):
                    return

                attr = self.db_qkan.fetchall()
                if attr[0][0] != None and attr != []:
                    self.bew_art = attr[0][0]

                # anzahl schaechte 0
                sql = """
                            SELECT schaechte_untersucht_bewertung.schnam,
                            schaechte.entwart
                            FROM schaechte_untersucht_bewertung,schaechte
                            WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 0 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                   """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += 1
                        if i[1] == 'Schmutzwasser':
                            sw += 1
                        if i[1] == 'Mischwasser':
                            mw += 1

                        self.anz_schaechte_0_rw = rw
                        self.anz_schaechte_0_sw = sw
                        self.anz_schaechte_0_mw = mw

                    # anzahl schaechte 1
                    sql = """
                                    SELECT schaechte_untersucht_bewertung.schnam,
                                    schaechte.entwart
                                    FROM schaechte_untersucht_bewertung,schaechte
                                    WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 1 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                           """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_1_rw = rw
                                self.anz_schaechte_1_sw = sw
                                self.anz_schaechte_1_mw = mw

                    # anzahl schaechte 2
                    sql = """
                                            SELECT schaechte_untersucht_bewertung.schnam,
                                            schaechte.entwart
                                            FROM schaechte_untersucht_bewertung,schaechte
                                            WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 2 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                                   """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_2_rw = rw
                                self.anz_schaechte_2_sw = sw
                                self.anz_schaechte_2_mw = mw

                    # anzahl schaechte 3
                    sql = """
                                        SELECT schaechte_untersucht_bewertung.schnam,
                                        schaechte.entwart
                                        FROM schaechte_untersucht_bewertung,schaechte
                                        WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 3 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                               """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_3_rw = rw
                                self.anz_schaechte_3_sw = sw
                                self.anz_schaechte_3_mw = mw

                    # anzahl schaechte 4
                    sql = """
                            SELECT schaechte_untersucht_bewertung.schnam,
                            schaechte.entwart
                            FROM schaechte_untersucht_bewertung,schaechte
                            WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 4
                                   """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_4_rw = rw
                                self.anz_schaechte_4_sw = sw
                                self.anz_schaechte_4_mw = mw

                    # anzahl schaechte 5
                    sql = """
                                SELECT schaechte_untersucht_bewertung.schnam,
                                schaechte.entwart
                                FROM schaechte_untersucht_bewertung,schaechte
                                WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 5 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                       """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_5_rw = rw
                                self.anz_schaechte_5_sw = sw
                                self.anz_schaechte_5_mw = mw


    def run(self, date) -> None:
            """
            Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine XML-Datei
            """
            self.date = date
            self._infos()
            self.anzeigen()
            self._suewvo()

            # Close connection
            del self.db_qkan




