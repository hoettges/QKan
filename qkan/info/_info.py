from qgis.utils import spatialite_connect

from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger
import matplotlib.pyplot as plt

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
        # figure_4 = self.fig_4
        # figure_4.clear()
        # plt.figure(figure_4.number)
        # new_plot = figure_4.add_subplot(231)
        #
        # #Tabelle mit Algemeinen Informationen
        #
        # data = {}
        # entwart_list = []
        # sql = """select count() from haltungen"""
        #
        # if not self.db_qkan.sql(sql):
        #     return
        #
        # anz_haltungen_ges = self.db_qkan.fetchall()[0][0]
        #
        # sql = """select count(laenge) from haltungen"""
        #
        # if not self.db_qkan.sql(sql):
        #     return
        #
        # l_haltungen_ges = self.db_qkan.fetchall()[0][0]
        #
        # sql = """select DISTINCT entwart from haltungen """
        #
        # if not self.db_qkan.sql(sql):
        #     return
        #
        # for i in self.db_qkan.fetchall():
        #     i = str(i[0])
        #     entwart_list.append(i)
        #
        # data = {k: None for k in entwart_list}
        #
        # for i in data.keys():
        #     sql = f"""select count() from haltungen WHERE entwart = '{i}'"""
        #
        #     if not self.db_qkan.sql(sql):
        #         return
        #
        #     anz = self.db_qkan.fetchall()[0][0]
        #
        #     data[i] = anz
        #
        # names = list(data.keys())
        # values = list(data.values())
        #
        #
        #
        # data = [
        #     [l_haltungen_ges],
        #     [anz_haltungen_ges]
        # ]
        #
        # columns = ( "Gesamt")
        # #columns ergänzen um die einzelnen entwässerungsarten
        # rows = ["km", "Anzahl"]
        # #rows mit den Daten aus der Datenbank
        # fig, ax = plt.subplots()
        #
        # ax.table(cellText=data, colLabels=columns, rowLabels=rows, loc='center')
        # ax.axis('off')
        # plt.show()
        #
        # # Tabelle anzeigen
        # self.canv_4.draw()

        # anzahl haltungen
        sql = """select count() from haltungen"""

        if not self.db_qkan.sql(sql):
            return

        self.anz_haltungen = self.db_qkan.fetchall()[0][0]

        # anzahl schaechte
        sql = """select count() from schaechte"""

        if not self.db_qkan.sql(sql):
            return

        self.anz_schaechte = self.db_qkan.fetchall()[0][0]

        # anzahl teilgebiete
        sql = """select count() from teilgebiete"""

        if not self.db_qkan.sql(sql):
            return

        self.anz_teilgeb = self.db_qkan.fetchall()[0][0]

        # anzahl lange haltungen
        sql = """SELECT SUM(laenge) FROM haltungen"""

        if not self.db_qkan.sql(sql):
            return

        self.laenge_haltungen = round(self.db_qkan.fetchall()[0][0],2)

    def handle_click(event, pie_wedges, run_script_callback):
        # Check if the click event is within any of the pie slices
        for wedge in pie_wedges:
            if wedge.contains_point([event.x, event.y]):
                run_script_callback()
                break

    def anzeigen(self):
        figure = self.fig
        figure.clear()
        plt.figure(figure.number)
        new_plot = figure.add_subplot(231)

        #Darstellung Haltungen nach Entwässerungsart
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
            sql = f"""select count() from haltungen WHERE entwart = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        #new_plot.pie(values, labels=names, autopct='%1.1f%%')
        #new_plot.set_title('Entwässerungsart')

        wedges, texts, autotexts = new_plot.pie(values, labels=names, autopct='%1.1f%%')
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

        # Connect the click event to the handler
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
            sql = f"""select count() from haltungen WHERE baujahr = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot2 = figure.add_subplot(232)
        new_plot2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot2.set_title('Baujahr')

        self.canv.draw()



        # Darstellungen Haltungen nach Durchmesser

        data = {}
        entwart_list = []
        sql = """select DISTINCT hoehe from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select count() from haltungen WHERE hoehe = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot2 = figure.add_subplot(233)
        new_plot2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot2.set_title('Durchmesser')

        self.canv.draw()

        #Darstellung nach Tiefenlage?


        # Darstellungen Haltungen nach Material
        data = {}
        entwart_list = []
        sql = """select DISTINCT material from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select count() from haltungen WHERE material = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot2 = figure.add_subplot(234)
        new_plot2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot2.set_title('Material')

        self.canv.draw()

        # Darstellungen Haltungen nach Profiltyp
        data = {}
        entwart_list = []
        sql = """select DISTINCT profilnam from haltungen """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            entwart_list.append(i)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            sql = f"""select count() from haltungen WHERE profilnam = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot3 = figure.add_subplot(235)
        new_plot3.pie(values, labels=names, autopct='%1.1f%%')
        new_plot3.set_title('Profilart')

        self.canv.draw()

        #Haltungen nach Zustandsklasse (Farben nach Zustandsklassen anpassen)
        figure_3 = self.fig_3
        figure_3.clear()
        plt.figure(figure_3.number)
        new_plot_2 = figure_3.add_subplot(221)

        data = {}
        entwart_list = []
        sql = """select count() from haltungen_untersucht"""

        if not self.db_qkan.sql(sql):
            return

        anz_haltungen_ges = self.db_qkan.fetchall()[0][0]

        sql = """select DISTINCT MIN(max_ZD,max_ZS,max_ZB) from haltungen_untersucht """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i1 = str(i[0])
            entwart_list.append(i1)

        data = {k: None for k in entwart_list}

        for i in data.keys():
            if i != 'None':
                sql = f"""select count() from haltungen_untersucht WHERE MIN(max_ZD,max_ZS,max_ZB) = {i}"""

                if not self.db_qkan.sql(sql):
                    return

                anz = self.db_qkan.fetchall()[0][0]

                data[i] = anz

        del data['None']
        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot_2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot_2.set_title('Zustandsklasse Haltungen')

        self.canv_3.draw()

        #Zustandsdaten Schächte

        data = {}
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

        del data['None']
        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot_2 = figure_3.add_subplot(222)
        new_plot_2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot_2.set_title('Zustandsklasse Schächte')

        self.canv_3.draw()

        # Darstellung Schächte nach Entwässerungsart
        figure_2 = self.fig_2
        figure_2.clear()
        plt.figure(figure_2.number)
        new_plot_2 = figure_2.add_subplot(231)

        data = {}
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
        new_plot_2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot_2.set_title('Entwässerungsart')

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
        new_plot2 = figure_2.add_subplot(232)
        new_plot2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot2.set_title('Baujahr')

        self.canv_2.draw()

        # Darstellung Schächte nach Material

        data = {}
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
        new_plot2 = figure_2.add_subplot(233)
        new_plot2.pie(values, labels=names, autopct='%1.1f%%')
        new_plot2.set_title('Material')

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




