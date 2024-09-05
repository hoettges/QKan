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
    def __init__(self, fig_1, canv_1, fig_2, canv_2, fig_3, canv_3, fig_4, canv_4, db_qkan: DBConnection):
        self.db_qkan = db_qkan
        self.anz_haltungen = 0
        self.anz_schaechte = 0
        self.laenge_haltungen = 0
        self.anz_teilgeb = 0
        self.canv_1 = canv_1
        self.fig_1 = fig_1
        self.canv_2 = canv_2
        self.fig_2 = fig_2
        self.canv_3 = canv_3
        self.fig_3 = fig_3
        self.canv_4 = canv_4
        self.fig_4 = fig_4

    def func(self, pct, allvals):
        if pct is not None and allvals is not None:
            try:
                absolute = int(np.round(pct / 100. * np.sum(allvals)))
            except BaseException as e:
                logger.error(
                    f'Fehler: {e}\n'
                    f'{pct=}\n'
                    f'{allvals=}\n'
                )
                raise Exception(f"{self.__class__.__name__}: Fehler in Funktion pct")
            return f"{pct:.1f}%\n({absolute:d})"
        else:
            return ""

    def _tableplot(self, figure, sql: str, title: str, pos:int):
        "Erzeugt eine Tabelle mit Bezeichnungen, Längen und Anzahl und fügt sie als subplot einem tab zu"

        if not self.db_qkan.sql(sql, "Dashboard - {title}"):
            raise Exception(f"{self.__class__.__name__}: SQL-Fehler")

        data = self.db_qkan.fetchall()
        l_bezeich = [el[0] for el in data]
        t_values = [[el[1], el[2]] for el in data]

        laenge_ges = sum([el[1] for el in data])
        anzahl_ges = sum([el[2] for el in data])

        t_values.append([laenge_ges, anzahl_ges])
        l_bezeich.append("Gesamt")

        colLabels = ["km", "Anzahl"]

        # plt.figure(figure.number)
        new_plot = figure.add_subplot(pos)

        try:
            new_plot.table(
                cellText=t_values,
                colLabels=colLabels,
                rowLabels=l_bezeich,
                loc='center'
            )
        except BaseException as e:
            logger.error(
                f'Fehler: {e}\n'
                f'{t_values=}\n'
                f'{l_bezeich=}\n'
             )
            raise  Exception(f"{self.__class__.__name__}: Fehler beim Erstellen der Tabelle")
        new_plot.axis('off')

        new_plot.set_title(title, fontsize=10, fontweight='bold', pad=20)

    def _pieplot(self, sql, figure, title, pos:int):
        """Erzeugt ein Pie-Chart mit Bezeichnungen und Anzahl bzw. Länge und fügt sie als subplot einem tab zu"""

        if not self.db_qkan.sql(sql, "Dashboard - {title}"):
            raise Exception(f"{self.__class__.__name__}: SQL-Fehler")

        data = self.db_qkan.fetchall()
        labels, values = [[el[i] for el in data] for i in range(2)]

        new_plot = figure.add_subplot(pos)
        wedges, texts, autotexts = new_plot.pie(values, labels=labels, autopct=lambda pct: self.func(pct, values), radius=1.1)
        # figure.tight_layout()
        new_plot.set_title(title)
        return wedges, texts, autotexts

    def _barplot(self, sql, figure, title:str, xlabel:str, ylabel: str, pos:int):
        """Erzeugt ein Balkendiagramm mit Bezeichnungen und fügt sie als subplot einem tab zu"""

        if not self.db_qkan.sql(sql, "Dashboard - {title}"):
            raise Exception(f"{self.__class__.__name__}: SQL-Fehler")

        data = self.db_qkan.fetchall()
        labels, values = [[el[i] for el in data] for i in range(2)]

        new_plot = figure.add_subplot(pos)

        y_pos = np.arange(len(values))
        box = new_plot.get_position()
        new_plot.set_position([box.x0 + 0.1, box.y0, box.width * 0.85, box.height* 0.9])
        new_plot.barh(y_pos, values, align='center')
        new_plot.set_yticks(y_pos)
        new_plot.set_yticklabels(labels)
        new_plot.invert_yaxis()
        new_plot.set_xlabel(xlabel)
        new_plot.set_ylabel(ylabel)
        new_plot.set_title(title)
        new_plot.autoscale()

    def _infos(self) -> None:
        #TODO: Anzeige anpassen um die Auswahl eines Teilgebietes zu ermöglichen!

        # Karteikarte 1 initialisieren
        figure = self.fig_4
        figure.clear()

        # Infos Haltungen nach Entwässerungsarten ------------------------------------------------------

        sql = """
            WITH liste AS (
                SELECT
                    entwart,
                    round(sum(iif(coalesce(laenge,0)=0,GLength(geom),laenge))/1000.,2) AS gesamtlaenge, 
                    count() AS anzahl
                FROM haltungen
                WHERE entwart IS NOT NULL 
                GROUP BY entwart
            )
            SELECT *
            FROM liste
            WHERE entwart NOT LIKE '%still%'
            ORDER BY gesamtlaenge DESC
        """

        self._tableplot(
            figure=figure,
            sql=sql,
            title="Haltungen",
            pos=111
        )

        # if not self.db_qkan.sql(sql, "Dashboard - Haltungen nach Entwässerungsarten"):
        #     raise Exception(f"{self.__class__.__name__}: SQL-Fehler")
        #
        # data = self.db_qkan.fetchall()
        # l_bezeich = [el[0] for el in data]
        # t_values = [[el[1], el[2]] for el in data]
        #
        # laenge_ges = sum([el[1] for el in data])
        # anzahl_ges = sum([el[2] for el in data])
        #
        # t_values.append([laenge_ges, anzahl_ges])
        # l_bezeich.append("Gesamt")
        #
        # try:
        #     new_plot.table(
        #         cellText=t_values,
        #         colLabels=["km", "Anzahl"],
        #         rowLabels=l_bezeich,
        #         loc='center'
        #     )
        # except BaseException as e:
        #     logger.error(
        #         f'Fehler: {e}\n'
        #         f'{t_values=}\n'
        #         f'{l_bezeich=}\n'
        #      )
        #     raise  Exception(f"{self.__class__.__name__}: Fehler beim Erstellen der Tabelle")
        # new_plot.axis('off')
        #
        # new_plot.set_title("Haltungen", fontsize=10, fontweight='bold', pad=20)
        #
        # # Tabelle anzeigen
        # self.canv_4.draw()


        # #Infos Schächte nach Entwässerungsarten ------------------------------------------------------
        # plt.figure(figure_4.number)
        # new_plot = figure_4.add_subplot(512)
        #
        # # Tabelle mit Allgemeinen Informationen
        #
        # sql = """
        #     WITH liste AS (
        #         SELECT entwart, count() AS anzahl
        #         FROM schaechte
        #         GROUP BY entwart
        #     )
        #     SELECT *
        #     FROM liste
        #     WHERE entwart NOT LIKE '%still%'
        #     ORDER BY anzahl DESC
        # """
        #
        # if not self.db_qkan.sql(sql, "Dashboard - Schächte nach Entwässerungsarten"):
        #     raise Exception(f"{self.__class__.__name__}: SQL-Fehler")
        #
        # data = self.db_qkan.fetchall()
        # l_bezeich, l_anzahl = [[el[i] for el in data] for i in range(2)]
        #
        # anzahl_ges = sum(l_anzahl)
        #
        # l_bezeich.append("Gesamt")
        # l_anzahl.append(anzahl_ges)
        #
        # new_plot.table(
        #     cellText=[l_anzahl],
        #     colLabels=l_bezeich,
        #     rowLabels=["Anzahl"],
        #     loc='center'
        # )
        # new_plot.axis('off')
        # new_plot.set_title("Schächte", fontsize=10, fontweight='bold', pad=20)
        #
        # # Tabelle anzeigen
        # self.canv_4.draw()
        #
        #
        # #Infos Anschlussleitungen nach Entwässerungsarten -------------------------------------------
        # plt.figure(figure_4.number)
        # new_plot = figure_4.add_subplot(513)
        #
        # # Tabelle mit Allgemeinen Informationen
        #
        # sql = """
        #     WITH liste AS (
        #         SELECT
        #             round(sum(iif(coalesce(laenge,0)=0,GLength(geom),laenge))/1000.,2) AS gesamtlaenge,
        #             entwart,
        #             count() AS anzahl
        #         FROM anschlussleitungen
        #         GROUP BY entwart
        #     )
        #     SELECT *
        #     FROM liste
        #     WHERE entwart NOT LIKE '%still%'
        #     ORDER BY gesamtlaenge DESC
        # """
        #
        # if not self.db_qkan.sql(sql, "Dashboard - Anschlussleitungen nach Entwässerungsarten"):
        #     raise Exception(f"{self.__class__.__name__}: SQL-Fehler")
        #
        # data = self.db_qkan.fetchall()
        # l_laengen, l_bezeich, l_anzahl = [[el[i] for el in data] for i in range(3)]
        #
        # laenge_ges = sum(l_laengen)
        # anzahl_ges = sum(l_laengen)
        #
        # l_laengen.append(laenge_ges)
        # l_bezeich.append("Gesamt")
        # l_anzahl.append(anzahl_ges)
        #
        # new_plot.table(
        #     cellText=[l_laengen, l_anzahl],
        #     colLabels=l_bezeich,
        #     rowLabels=["km", "Anzahl"],
        #     loc='center'
        # )
        # new_plot.axis('off')
        # new_plot.set_title("Anschlussleitungen", fontsize=10, fontweight='bold', pad=20)
        # figure_4.tight_layout()
        # # Tabelle anzeigen
        # self.canv_4.draw()
        #
        #
        # #infos Teilgebiete -------------------------------------------------------------------
        # plt.figure(figure_4.number)
        # new_plot = figure_4.add_subplot(514)
        #
        # sql = """
        #     SELECT
        #         coalesce(trim(teilgebiet), '') as tgb,
        #         round(sum(iif(coalesce(laenge,0)=0,GLength(geom),laenge))/1000.,2) AS gesamtlaenge,
        #         count() AS anzahl
        #     FROM haltungen
        #     GROUP BY tgb
        # """
        #
        # if not self.db_qkan.sql(sql, "Dashboard - Teilgebiete"):
        #     raise Exception(f"{self.__class__.__name__}: SQL-Fehler")
        #
        # data = self.db_qkan.fetchall()
        # l_bezeich, l_laengen, l_anzahl = [[el[i] for el in data] for i in range(3)]
        #
        # laenge_ges = sum(l_laengen)
        # anzahl_ges = sum(l_laengen)
        #
        # l_laengen.append(laenge_ges)
        # l_bezeich.append("Gesamt")
        # l_anzahl.append(anzahl_ges)
        #
        # new_plot.table(
        #     cellText=[l_laengen, l_anzahl],
        #     colLabels=l_bezeich,
        #     rowLabels=["km", "Anzahl"],
        #     loc='center'
        # )
        # new_plot.set_title("Name", fontsize=10, fontweight='bold', pad=20)
        # new_plot.axis('off')
        # figure_4.tight_layout()
        #
        # # Tabelle anzeigen
        # self.canv_4.draw()

    def handle_click(event, pie_wedges, run_script_callback):
        # TODO: Anpassen, sodass beim Anklicken der Grafik die jeweiligen Daten in QGIS ausgewählt werden!
        for wedge in pie_wedges:
            if wedge.contains_point([event.x, event.y]):
                run_script_callback()
                break

    def anzeigen(self):
        """Grafiken in den Karteikarten erstellen"""

        # Karteikarte 2 initialisieren
        figure = self.fig_1
        figure.clear()

        #Darstellung Haltungen nach Entwässerungsart bezogen auf km

        sql = """
            WITH liste AS (
                SELECT
                    entwart,
                    round(sum(iif(coalesce(laenge,0)=0,GLength(geom),laenge))/1000.,2) AS gesamtlaenge
                FROM haltungen
                WHERE entwart IS NOT NULL 
                GROUP BY entwart
            )
            SELECT *
            FROM liste
            WHERE gesamtlaenge > 0.1 AND entwart NOT LIKE '%still%'
            ORDER BY gesamtlaenge DESC
        """

        wedges, texts, autotexts = self._pieplot(
            sql=sql,
            figure=figure,
            title='Entwässerungsart',
            pos=231
        )

        #return self.canv_1, wedges

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
        # self.canv_1.draw()

        #Darstellungen Haltungen nach Baujahren

        sql = """
            WITH liste AS (
                SELECT 
                    iif(coalesce(laenge,0)=0,GLength(geom),laenge) AS laenge,
                    iif(
                        coalesce(baujahr, 0) = 0,
                        ' ohne Baujahr',
                        printf('bis %d', min(CAST(strftime('%Y', 'now') AS INT), ceil(baujahr/5.)*5.))) AS baujahr
                FROM haltungen
            )
            SELECT
                baujahr,
                round(sum(laenge)/1000.0 ,2) AS gesamtlaenge
            FROM liste
            GROUP BY baujahr
            ORDER BY baujahr
        """

        wedges, texts, autotexts = self._pieplot(
            sql=sql,
            figure=figure,
            title='Baujahre',
            pos=232
        )

        # Darstellungen Haltungen nach Durchmesser

        sql = """
            WITH liste AS (
                SELECT 
                    iif(hoehe <= 501, ceil(hoehe/100.)*100, iif(hoehe <= 1001, ceil(hoehe/250.)*250, iif(hoehe <= 3001, ceil(hoehe/250.)*250, ceil(hoehe/1000.)*1000))) AS Hoehe,
                    iif(coalesce(laenge,0)=0,GLength(geom),laenge) AS laenge
                FROM haltungen
            )
            SELECT 
                printf('bis %d', Hoehe) AS t_hoehe, 
                round(sum(laenge)/1000.,2) AS gesamtlaenge
            FROM liste
            GROUP BY Hoehe
            ORDER BY Hoehe
        """

        self._barplot(
            sql=sql,
            figure=figure,
            title='Gesamtlänge je Durchmesser',
            ylabel='Durhcmesser bis mm',
            xlabel='Gesamtlänge (km)',
            pos=233
        )

        # l_bezeich = []
        # sql = """select DISTINCT hoehe from haltungen """
        #
        # if not self.db_qkan.sql(sql):
        #     return
        #
        # for i in self.db_qkan.fetchall():
        #     i = str(i[0])
        #     l_bezeich.append(i)
        #
        # data = {k: None for k in l_bezeich}
        #
        # for i in data.keys():
        #     sql = f"""select sum(laenge) from haltungen WHERE hoehe = '{i}'"""
        #
        #     if not self.db_qkan.sql(sql):
        #         return
        #
        #     anz = self.db_qkan.fetchall()[0][0]
        #
        #     data[i] = anz
        #
        # total = sum(data.values())
        # threshold = 0.1 * total
        # daten = {k: v for k, v in data.items() if v >= threshold}
        # sonstiges = {k: v for k, v in data.items() if v < threshold}
        #
        # if sonstiges:
        #     daten['Sonstiges'] = sum(sonstiges.values())
        #
        # # Daten für das Kreisdiagramm
        # names = list(daten.keys())
        # values = list(daten.values())
        #
        # new_plot = figure.add_subplot(243)
        # wedges, texts, autotexts = new_plot.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        # new_plot.set_title('Durchmesser DN')
        # new_plot3 = figure.add_subplot(244)
        #
        # if 'Sonstiges' in daten:
        #     # fig_1, ax2 = plt.subplots()
        #     sonstiges_names = list(sonstiges.keys())
        #     sonstiges_values = list(sonstiges.values())
        #
        #     y_pos = np.arange(len(sonstiges_values))
        #     box = new_plot3.get_position()
        #     new_plot3.set_position([box.x0 + 0.05, box.y0, box.width * 0.5, box.height* 0.75])
        #     new_plot3.barh(y_pos, sonstiges_values, align='center')
        #     new_plot3.set_yticks(y_pos)
        #     new_plot3.set_yticklabels(sonstiges_names)
        #     new_plot3.invert_yaxis()
        #     new_plot3.set_xlabel('Durchmesser')
        #     new_plot3.set_title('Details der Kategorie "Sonstiges"')
        # new_plot.autoscale()
        # new_plot3.autoscale()

        #TODO:Darstellung nach Tiefenlage?


        # Darstellungen Haltungen nach Material

        sql = """
            WITH liste AS (
                SELECT
                    material,
                    round(sum(iif(coalesce(laenge,0)=0,GLength(geom),laenge))/1000.,2) AS gesamtlaenge
                FROM haltungen
                WHERE material IS NOT NULL 
                GROUP BY material
            )
            SELECT *
            FROM liste
            WHERE gesamtlaenge > 0.1
            ORDER BY gesamtlaenge DESC
        """

        self._barplot(
            sql=sql,
            figure=figure,
            title='Gesamtlänge nach Material',
            ylabel='Material',
            xlabel='Gesamtlänge (km)',
            pos=234
        )

        #
        #
        #
        #
        #
        #
        #
        #
        # l_bezeich = []
        # sql = """select DISTINCT material from haltungen """
        #
        # if not self.db_qkan.sql(sql):
        #     return
        #
        # for i in self.db_qkan.fetchall():
        #     i = str(i[0])
        #     l_bezeich.append(i)
        #
        # data = {k: None for k in l_bezeich}
        #
        # for i in data.keys():
        #     sql = f"""select sum(laenge) from haltungen WHERE material = '{i}'"""
        #
        #     if not self.db_qkan.sql(sql):
        #         return
        #
        #     anz = self.db_qkan.fetchall()[0][0]
        #
        #     data[i] = anz
        #
        # total = sum(data.values())
        # threshold = 0.1 * total
        # daten = {k: v for k, v in data.items() if v >= threshold}
        # sonstiges = {k: v for k, v in data.items() if v < threshold}
        #
        # if sonstiges:
        #     daten['Sonstiges'] = sum(sonstiges.values())
        #
        # # Daten für das Kreisdiagramm
        # names = list(daten.keys())
        # values = list(daten.values())
        #
        # # Plot
        # new_plot = figure.add_subplot(234)
        # wedges, texts, autotexts = new_plot.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        # new_plot.set_title('Material')
        # new_plot3 = figure.add_subplot(235)
        # if 'Sonstiges' in daten:
        #     sonstiges_names = list(sonstiges.keys())
        #     sonstiges_values = list(sonstiges.values())
        #
        #     y_pos = np.arange(len(sonstiges_values))
        #     box = new_plot3.get_position()
        #     new_plot3.set_position([box.x0 + 0.05, box.y0, box.width * 0.5, box.height * 0.75])
        #     new_plot3.barh(y_pos, sonstiges_values, align='center')
        #     new_plot3.set_yticks(y_pos)
        #     new_plot3.set_yticklabels(sonstiges_names)
        #     new_plot3.invert_yaxis()
        #     new_plot3.set_xlabel('Material')
        #     new_plot3.set_title('Details der Kategorie "Sonstiges"')
        # new_plot.autoscale()
        # new_plot3.autoscale()

        # Darstellungen Haltungen nach Profiltyp

        sql = """
            WITH liste AS (
                SELECT
                    profilnam,
                    round(sum(iif(coalesce(laenge,0)=0,GLength(geom),laenge))/1000.,2) AS gesamtlaenge
                FROM haltungen
                WHERE profilnam IS NOT NULL 
                GROUP BY profilnam
            )
            SELECT *
            FROM liste
            WHERE gesamtlaenge > 0.1
            ORDER BY gesamtlaenge DESC
        """

        self._barplot(
            sql=sql,
            figure=figure,
            title='Gesamtlänge nach Rohrprofil',
            ylabel='Rohrprofil',
            xlabel='Gesamtlänge (km)',
            pos=236
        )

        #
        #
        # l_bezeich = []
        # sql = """select DISTINCT profilnam from haltungen """
        #
        # if not self.db_qkan.sql(sql):
        #     return
        #
        # for i in self.db_qkan.fetchall():
        #     i = str(i[0])
        #     l_bezeich.append(i)
        #
        # data = {k: None for k in l_bezeich}
        #
        # for i in data.keys():
        #     sql = f"""select sum(laenge) from haltungen WHERE profilnam = '{i}'"""
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
        # # Plot
        # new_plot3 = figure.add_subplot(236)
        # new_plot3.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        # new_plot3.set_title('Profilart')
        # figure.tight_layout()

        self.canv_1.draw()

        #Haltungen nach Zustandsklasse
        # TODO: Farben nach Zustandsklassen anpassen

        # Karteikarte 3 initialisieren
        figure_3 = self.fig_3
        figure_3.clear()

        sql = """
            WITH liste AS (
                SELECT
                    MIN(max_ZD,max_ZS,max_ZB) AS Zustandszahl,
                    round(sum(iif(coalesce(laenge,0)=0,GLength(geom),laenge))/1000.,2) AS gesamtlaenge,
                    count() AS anzahl
                FROM haltungen_untersucht
                WHERE MIN(max_ZD,max_ZS,max_ZB) IS NOT NULL
                GROUP BY MIN(max_ZD,max_ZS,max_ZB)
            )
            SELECT *
            FROM liste
            WHERE gesamtlaenge > 0.1
            ORDER BY Zustandszahl
        """

        self._barplot(
            sql=sql,
            figure=figure_3,
            title='Gesamtlänge nach Zustandsklassen',
            ylabel='Zustandsklasse',
            xlabel='Gesamtlänge (km)',
            pos=121
        )






        # plt.figure(figure_3.number)
        new_plot_2 = figure_3.add_subplot(121)
        l_bezeich = []
        sql = """select DISTINCT MIN(max_ZD,max_ZS,max_ZB) from haltungen_untersucht """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i1 = str(i[0])
            l_bezeich.append(i1)

        data = {k: None for k in l_bezeich}

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
        new_plot_2.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        new_plot_2.set_title('Zustandsklasse Haltungen')
        figure_3.tight_layout()
        self.canv_3.draw()


        #Zustandsdaten Schächte
        l_bezeich = []
        sql = """select count() from schaechte_untersucht"""

        if not self.db_qkan.sql(sql):
            return

        sql = """select DISTINCT MIN(max_ZD,max_ZS,max_ZB) from schaechte_untersucht """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            l_bezeich.append(i)

        data = {k: None for k in l_bezeich}

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
        new_plot_2.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        new_plot_2.set_title('Zustandsklasse Schächte')
        figure_3.tight_layout()
        self.canv_3.draw()


        # Darstellung Schächte nach Entwässerungsart
        figure_2 = self.fig_2
        figure_2.clear()
        # plt.figure(figure_2.number)
        new_plot_2 = figure_2.add_subplot(131)

        l_bezeich = []
        sql = """select count() from schaechte"""

        if not self.db_qkan.sql(sql):
            return

        sql = """select DISTINCT entwart from schaechte """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            l_bezeich.append(i)

        data = {k: None for k in l_bezeich}

        for i in data.keys():
            sql = f"""select count() from schaechte WHERE entwart = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot_2.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        new_plot_2.set_title('Entwässerungsart')
        figure_2.tight_layout()
        self.canv_2.draw()

        # Darstellungen Schächte nach Baujahren
        l_bezeich = []
        sql = """select DISTINCT baujahr from schaechte """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            l_bezeich.append(i)

        data = {k: None for k in l_bezeich}

        for i in data.keys():
            sql = f"""select count() from schaechte WHERE baujahr = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot = figure_2.add_subplot(132)
        wedges, texts, autotexts = new_plot.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        new_plot.set_title('Baujahr')
        figure_2.tight_layout()
        self.canv_2.draw()


        # Darstellung Schächte nach Material
        l_bezeich = []
        sql = """select DISTINCT material from schaechte """

        if not self.db_qkan.sql(sql):
            return

        for i in self.db_qkan.fetchall():
            i = str(i[0])
            l_bezeich.append(i)

        data = {k: None for k in l_bezeich}

        for i in data.keys():
            sql = f"""select count() from schaechte WHERE material = '{i}'"""

            if not self.db_qkan.sql(sql):
                return

            anz = self.db_qkan.fetchall()[0][0]

            data[i] = anz

        names = list(data.keys())
        values = list(data.values())
        # Plot
        new_plot = figure_2.add_subplot(133)
        wedges, texts, autotexts = new_plot.pie(values, labels=names, autopct=lambda pct: self.func(pct, values))
        new_plot.set_title('Material')
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
                            WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam
                                AND haltungen_untersucht_bewertung.objektklasse_gesamt = 0
                                AND haltungen_untersucht_bewertung.untersuchtag like ?
                                      """
                data = (date,)

                try:
                    self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Haltungen Objektklasse 0", data)
                except:
                    pass

                attr = self.db_qkan.fetchall()
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
                    WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam
                        AND haltungen_untersucht_bewertung.objektklasse_gesamt = 1 
                        AND haltungen_untersucht_bewertung.untersuchtag like ?;
                """

                data = (date,)

                try:
                    self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Haltungen Objektklasse 1", data)
                except:
                    pass
                attr = self.db_qkan.fetchall()
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
                    WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam
                        AND haltungen_untersucht_bewertung.objektklasse_gesamt = 2
                        AND haltungen_untersucht_bewertung.untersuchtag like ?;
                """

                data = (date,)

                try:
                    self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Haltungen Objektklasse 2", data)
                except:
                    pass
                attr = self.db_qkan.fetchall()
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
                    WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam
                        AND haltungen_untersucht_bewertung.objektklasse_gesamt = 3
                        AND haltungen_untersucht_bewertung.untersuchtag like ?;
                """

                data = (date,)

                try:
                    self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Haltungen Objektklasse 3", data)
                except:
                    pass
                attr = self.db_qkan.fetchall()
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
                    WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam
                        AND haltungen_untersucht_bewertung.objektklasse_gesamt = 4
                        AND haltungen_untersucht_bewertung.untersuchtag like ?;
                """

                data = (date,)

                try:
                    self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Haltungen Objektklasse 44", data)
                except:
                    pass
                attr = self.db_qkan.fetchall()
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
                    WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam
                        AND haltungen_untersucht_bewertung.objektklasse_gesamt = 5
                        AND haltungen_untersucht_bewertung.untersuchtag like ?;
                """

                data = (date,)

                try:
                    self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Haltungen Objektklasse 5", data)
                except:
                    pass
                attr = self.db_qkan.fetchall()
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
               SELECT count(*)
               FROM schaechte
               WHERE entwart ='Mischwasser' OR entwart = 'KM'
            """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.anz_schaechte_mw = attr[0][0]

            sql = """
                SELECT *
                FROM sqlite_master
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
                    WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam
                        AND schaechte_untersucht_bewertung.objektklasse_gesamt = 0
                        AND schaechte_untersucht_bewertung.untersuchtag like ?;
                """

                data = (date,)

                try:
                    self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Schächte Objektklasse 0", data)
                except:
                    pass
                attr = self.db_qkan.fetchall()
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
                        WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam
                            AND schaechte_untersucht_bewertung.objektklasse_gesamt = 1
                            AND schaechte_untersucht_bewertung.untersuchtag like ?;
                    """

                    data = (date,)

                    try:
                        self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Schächte Objektklasse 1", data)
                    except:
                        pass
                    attr = self.db_qkan.fetchall()
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
                        WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam
                            AND schaechte_untersucht_bewertung.objektklasse_gesamt = 2
                            AND schaechte_untersucht_bewertung.untersuchtag like ?;
                    """

                    data = (date,)

                    try:
                        self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Schächte Objektklasse 2", data)
                    except:
                        pass
                    attr = self.db_qkan.fetchall()
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
                        WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam
                            AND schaechte_untersucht_bewertung.objektklasse_gesamt = 3
                            AND schaechte_untersucht_bewertung.untersuchtag like ?;
                    """

                    data = (date,)

                    try:
                        self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Schächte Objektklasse 3", data)
                    except:
                        pass
                    attr = self.db_qkan.fetchall()
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
                        WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam
                            AND schaechte_untersucht_bewertung.objektklasse_gesamt = 4
                            AND schaechte_untersucht_bewertung.untersuchtag like ?;
                    """

                    data = (date,)

                    try:
                        self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Schächte Objektklasse 4", data)
                    except:
                        pass
                    attr = self.db_qkan.fetchall()
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
                        WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam
                            AND schaechte_untersucht_bewertung.objektklasse_gesamt = 5
                            AND schaechte_untersucht_bewertung.untersuchtag like ?;
                    """

                    data = (date,)

                    try:
                        self.db_qkan.sql(sql, "Info Entwässerungsart bewertete Schächte Objektklasse 5", data)
                    except:
                        pass
                    attr = self.db_qkan.fetchall()
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




