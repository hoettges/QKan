from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanUserError

from qkan.laengsschnitt.dijkstra import Netz, find_route
from qkan.tools.qkan_utils import get_qkanlayer_attributes

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
)
from qgis.utils import iface
from PyQt6.QtGui import QAction


logger = get_logger("QKan.selection")


class Select:
    def __init__(self, db_qkan: DBConnection, auswahl):
        self.db_qkan = db_qkan
        # self.check_cb = check_cb
        self.auswahl = auswahl
        print(self.auswahl)

    #Überall am Ende die Länge des Weges printen

    def laengster_weg_oben(self, netz, ziel):
        reverse_netz = {}

        for u in netz:
            if u[2] not in reverse_netz:
                reverse_netz[u[2]] = []
            reverse_netz[u[2]].append((u[1], u[3], u[0]))

        topo_order = []
        visited = set()

        def dfs_topo(u):
            visited.add(u)
            for v, _, _ in reverse_netz.get(u, []):
                if v not in visited:
                    dfs_topo(v)
            topo_order.append(u)
        dfs_topo(ziel)
        topo_order.reverse()

        dists = {}
        haltungen = {}
        for k in topo_order:
            dists[k] = float('-inf')
        dists[ziel] = 0

        vorgaenger = {}

        for u in topo_order:
            for v, l, nam in reverse_netz.get(u, []):
                if dists[v] < dists[u] + l:
                    dists[v] = dists[u] + l
                    vorgaenger[v] = u
                    haltungen[v] = nam

        return dists, vorgaenger, haltungen

    def laengster_weg_unten(self, netz, ziel):
        reverse_netz = {}
        in_degree = {}
        for u in netz:
            if u[1] not in reverse_netz:
                reverse_netz[u[1]] = []
            reverse_netz[u[1]].append((u[2], u[3], u[0]))

            if u not in in_degree:
                in_degree[u[1]] = 0
            in_degree[u[1]] += 1
        topo_order = []
        visited = set()


        def dfs_topo(u):
            visited.add(u)
            for v, _, _ in reverse_netz.get(u, []):
                if v not in visited:
                    dfs_topo(v)
            topo_order.append(u)

        dfs_topo(ziel)
        topo_order.reverse()

        dists = {}
        haltungen = {}
        for k in topo_order:
            dists[k] = float('-inf')
        dists[ziel] = 0

        vorgaenger = {}

        for u in topo_order:
            for v, l, nam in reverse_netz.get(u, []):
                if dists[v] < dists[u] + l:
                    dists[v] = dists[u] + l
                    vorgaenger[v] = u
                    haltungen[v] = nam

        return dists, vorgaenger, haltungen

    def rekonstruier_pfad(self, start, ziel, vorgaenger, haltungen):
        pfad = [start]
        pfad_haltungen = []
        while start != ziel:
            if start not in vorgaenger:
                return [] , [] # kein Pfad
            start_n = vorgaenger[start]
            pfad.append(start_n)
            pfad_haltungen.append(haltungen[start])
            start = start_n
        return pfad, list(reversed(pfad_haltungen))


    def gebiet(self):
        #db anweisung mit der alle haltung inner halb der gewählten teilgebiete ausgewählt werden

        layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.TEILGEBIETE.value)[0]
        features = layer.selectedFeatures()
        pks = ','.join([str(el[0]) for el in features])
        # logger.debug(f'pks: {pks}')

        # Selektionen in allen Layern aufheben:
        iface.mainWindow().findChild(QAction, 'mActionDeselectAll').trigger()

        # Alle Haltungen in gewählten Teilgebieten auswählen
        sql = f"""SELECT DISTINCT h.pk FROM haltungen AS h JOIN teilgebiete AS t ON ST_WITHIN(h.geom, t.geom) = 1
                  WHERE t.pk IN ({pks})"""
        self.db_qkan.sql(sql)
        x = self.db_qkan.fetchall()
        ids = [el[0] for el in x]
        logger.debug(f'ids: {ids[:10]}')
        layers = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)
        for layer in layers:
            layer.selectByIds(ids)

        # Alle Schächte in gewählten Teilgebieten auswählen
        sql = f"""SELECT DISTINCT s.pk FROM schaechte AS s JOIN teilgebiete AS t ON ST_WITHIN(s.geom, t.geom) = 1
                  WHERE t.pk IN ({pks})"""
        # sql = f"""SELECT pk FROM schaechte WHERE ST_WITHIN(geop ,(SELECT geom from teilgebiete where pk IN (?)))"""
        self.db_qkan.sql(sql)
        x = self.db_qkan.fetchall()
        ids = [el[0] for el in x]
        layers = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)
        for layer in layers:
            layer.selectByIds(ids)

        # Alle Flächen in gewählten Teilgebieten auswählen
        sql = f"""SELECT DISTINCT f.pk FROM flaechen AS f JOIN teilgebiete AS t ON ST_WITHIN(f.geom, t.geom) = 1
                  WHERE t.pk IN ({pks})"""
        self.db_qkan.sql(sql)
        x = self.db_qkan.fetchall()
        ids = [el[0] for el in x]
        layers = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)
        for layer in layers:
            layer.selectByIds(ids)

    def run(self) -> None:

        max_laenge = float('-inf')
        if self.auswahl == 'Objekte innerhalb Teilgebiet':
            self.gebiet()

        if self.auswahl == 'Objekte oberhalb':
            layer = iface.activeLayer()
            x = layer.source()

            # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
            _, table, _, _ = get_qkanlayer_attributes(x)
            # selektierte elemente anzeigen
            selected = layer.selectedFeatures()
            x = len(selected)

            if table not in ['schaechte', 'haltungen']:
                msg = (
                    f"Es wurde keine Auswahl getroffen!"
                )
                logger.warning_user(msg)
                raise QkanUserError(msg)

            if x > 1:
                logger.error_user(
                    "Bedienerfehler: "
                    'Es darf nur ein Schacht gewählt werden!'
                )
                return
            else:
                for feature in layer.selectedFeatures():
                    ziel = feature['Schachtname']

                self.db_qkan.sql("""
                                    SELECT haltnam, schoben, schunten, coalesce(laenge,ST_LENGTH(geom))
                                    FROM haltungen
                                """)
                netz = self.db_qkan.fetchall()

                self.db_qkan.sql("""
                                        SELECT schnam
                                        FROM schaechte WHERE schachttyp = 'Schacht' and schaechte.schnam NOT IN (select schunten from haltungen)
                                    """)
                startpunkte = []
                for i in self.db_qkan.fetchall():
                    startpunkte.append(i[0])

                dists, vorgaenger, haltungen = self.laengster_weg_oben(netz, ziel)
                haltungen_ges = []
                schaechte_ges = []
                for start in startpunkte:
                    if start in dists and dists[start] != float('-inf'):
                        pfad, pfad_haltungen = self.rekonstruier_pfad(start, ziel, vorgaenger, haltungen)
                        haltungen_ges.extend(pfad_haltungen)
                        schaechte_ges.extend(pfad)

                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)[0]

                if layer is not None:
                    auswahl = '"Bezeichnung" IN ({})'.format(", ".join(f"\'{w}\'" for w in haltungen_ges))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                self.db_qkan.getSelection(True)
                self.db_qkan.commit()


                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

                if layer is not None:
                    auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in schaechte_ges))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)


                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

                if layer is not None:
                    auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in schaechte_ges))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                self.db_qkan.getSelection(True)
                self.db_qkan.commit()

                haltungen = ','.join([f'"{str(x)}"' for x in pfad_haltungen])
                sql = f"""Select pk from flaechen where haltnam in ({haltungen})"""

                self.db_qkan.sql(sql)
                flaechen = []
                for i in self.db_qkan.fetchall():
                    flaechen.append(i[0])

                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
                if layer is not None:
                    auswahl = '"pk" IN ({})'.format(", ".join(f"\'{w}\'" for w in flaechen))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                self.db_qkan.getSelection(True)
                self.db_qkan.commit()


        if self.auswahl == 'Objekte unterhalb':
            layer = iface.activeLayer()
            x = layer.source()

            # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
            _, table, _, _ = get_qkanlayer_attributes(x)
            # selektierte elemente anzeigen
            selected = layer.selectedFeatures()
            x = len(selected)

            if table not in ['schaechte', 'haltungen']:
                msg = (
                    f"Es wurde keine Auswahl getroffen!"
                )
                raise QkanUserError(msg)

            if x > 1:
                logger.error_user(
                    "Bedienerfehler: "
                    'Es darf nur ein Schacht gewählt werden!'
                )
                return
            else:
                for feature in layer.selectedFeatures():
                    ziel = feature['Schachtname']

                self.db_qkan.sql("""
                    SELECT haltnam, schoben, schunten, coalesce(laenge,ST_LENGTH(geom))
                    FROM haltungen""")
                netz = self.db_qkan.fetchall()

                self.db_qkan.sql("""
                    SELECT schnam
                    FROM schaechte
                    WHERE schachttyp IN ('Schacht','Auslass', 'Speicher')
                      AND schaechte.schnam NOT IN (select schoben from haltungen)"""
                 )
                startpunkte = []
                for i in self.db_qkan.fetchall():
                    startpunkte.append(i[0])

                dists, vorgaenger, haltungen = self.laengster_weg_unten(netz, ziel)
                haltungen_ges = []
                schaechte_ges = []
                for start in startpunkte:
                    if start in dists and dists[start] != float('-inf'):
                        pfad, pfad_haltungen = self.rekonstruier_pfad(start, ziel, vorgaenger, haltungen)
                        haltungen_ges.extend(pfad_haltungen)
                        schaechte_ges.extend(pfad)

                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)[0]

                if layer is not None:
                    auswahl = '"Bezeichnung" IN ({})'.format(", ".join(f"\'{w}\'" for w in haltungen_ges))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)


                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

                if layer is not None:
                    auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in schaechte_ges))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)
                self.db_qkan.getSelection(True)
                self.db_qkan.commit()
                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

                if layer is not None:
                    auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in schaechte_ges))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                haltungen = ','.join([f'"{str(x)}"' for x in pfad_haltungen])

                sql = f"""Select pk from flaechen where haltnam in ({haltungen})"""

                self.db_qkan.sql(sql)
                flaechen = []
                for i in self.db_qkan.fetchall():
                    flaechen.append(i[0])

                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
                if layer is not None:
                    auswahl = '"pk" IN ({})'.format(", ".join(f"\'{w}\'" for w in flaechen))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                self.db_qkan.getSelection(True)
                self.db_qkan.commit()


        if self.auswahl == 'längster Fließweg oberhalb':
            max_haltungen = None
            layer = iface.activeLayer()
            x = layer.source()

            # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
            _, table, _, _ = get_qkanlayer_attributes(x)
            # selektierte elemente anzeigen
            selected = layer.selectedFeatures()
            x = len(selected)

            if table not in ['schaechte', 'haltungen']:
                msg = (
                    f"Es wurde keine Auswahl getroffen!"
                )
                raise QkanUserError(msg)

            if x > 1 or x is None:
                logger.error_user(
                    "Bedienerfehler: "
                    'Es darf nur ein Schacht gewählt werden!'
                )
                return
            else:
                for feature in layer.selectedFeatures():
                   ziel = feature['Schachtname']

                self.db_qkan.sql("""
                        SELECT haltnam, schoben, schunten, coalesce(laenge,ST_LENGTH(geom))
                        FROM haltungen
                    """)
                netz = self.db_qkan.fetchall()

                self.db_qkan.sql("""
                            SELECT schnam
                            FROM schaechte WHERE schachttyp = 'Schacht' and schaechte.schnam NOT IN (select schunten from haltungen)
                        """)
                startpunkte = []
                for i in self.db_qkan.fetchall():
                    startpunkte.append(i[0])

                liste = []
                dists, vorgaenger, haltungen = self.laengster_weg_oben(netz, ziel)
                for start in startpunkte:
                    if start in dists and dists[start] != float('-inf'):
                        pfad, pfad_haltungen = self.rekonstruier_pfad(start, ziel, vorgaenger, haltungen)
                        laenge = dists[start]
                        if laenge > max_laenge:
                            max_laenge = laenge
                            max_start = start
                            max_haltungen = pfad_haltungen
                            max_pfad = pfad

                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)[0]

                if layer is not None:
                    auswahl = '"Bezeichnung" IN ({})'.format(", ".join(f"\'{w}\'" for w in max_haltungen))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                haltungen = ','.join([f'"{str(x)}"' for x in max_haltungen])

                sql = f"""Select sum(laenge) from haltungen where haltnam in ({haltungen})"""

                self.db_qkan.sql(sql)
                x = self.db_qkan.fetchall()[0][0]


                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

                if layer is not None:
                    auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in max_pfad))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

                if layer is not None:
                    auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in max_pfad))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                self.db_qkan.getSelection(True)
                self.db_qkan.commit()

                haltungen = ','.join([f'"{str(x)}"' for x in max_haltungen])
                sql = f"""Select pk from flaechen where haltnam in ({haltungen})"""

                self.db_qkan.sql(sql)
                flaechen = []
                for i in self.db_qkan.fetchall():
                    flaechen.append(i[0])

                layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
                if layer is not None:
                    auswahl = '"pk" IN ({})'.format(", ".join(f"\'{w}\'" for w in flaechen))
                    layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                    iface.mapCanvas().zoomToSelected(layer)

                self.db_qkan.getSelection(True)
                self.db_qkan.commit()
            logger.info(f'Der Längeste Fließweg beträgt {x} m')


        # if self.check_cb['cb10']:
        #     max_haltungen = None
        #     layer = iface.activeLayer()
        #     x = layer.source()
        #
        #     # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        #     _, table, _, _ = get_qkanlayer_attributes(x)
        #     # selektierte elemente anzeigen
        #     selected = layer.selectedFeatures()
        #     x = len(selected)
        #
        #     if x > 1:
        #         logger.error_user(
        #             "Bedienerfehler: "
        #             'Es darf nur ein Schacht gewählt werden!'
        #         )
        #         return
        #     else:
        #         for feature in layer.selectedFeatures():
        #             ziel = feature['Schachtname']
        #
        #         self.db_qkan.sql("""
        #                             SELECT haltnam, schoben, schunten, coalesce(laenge,ST_LENGTH(geom))
        #                             FROM haltungen
        #                         """)
        #         netz = self.db_qkan.fetchall()
        #
        #         self.db_qkan.sql("""
        #                             SELECT schnam
        #                             FROM schaechte WHERE schachttyp IN ('Schacht','Auslass') and schaechte.schnam NOT IN (select schoben from haltungen)""")
        #         startpunkte = []
        #         for i in self.db_qkan.fetchall():
        #             startpunkte.append(i[0])
        #
        #         dists, vorgaenger, haltungen = self.laengster_weg_unten(netz, ziel)
        #         for start in startpunkte:
        #             if start in dists and dists[start] != float('-inf'):
        #                 pfad, pfad_haltungen = self.rekonstruier_pfad(start, ziel, vorgaenger, haltungen)
        #                 laenge = dists[start]
        #                 if laenge > max_laenge:
        #                     max_laenge = laenge
        #                     max_start = start
        #                     max_haltungen = pfad_haltungen
        #                     max_pfad = pfad
        #
        #         layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)[0]
        #
        #         if layer is not None and max_haltungen is not None:
        #             auswahl = '"Bezeichnung" IN ({})'.format(", ".join(f"\'{w}\'" for w in max_haltungen))
        #             layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #             iface.mapCanvas().zoomToSelected(layer)
        #
        #         if max_haltungen is not None:
        #             haltungen = ','.join([f'"{str(x)}"' for x in max_haltungen])
        #
        #             sql = f"""Select sum(laenge) from haltungen where haltnam in ({haltungen})"""
        #
        #             self.db_qkan.sql(sql)
        #             x = self.db_qkan.fetchall()[0][0]
        #
        #         if self.check_cb['cb_Schaechte']:
        #
        #             layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]
        #
        #             if layer is not None:
        #                 auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in max_pfad))
        #                 layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #                 iface.mapCanvas().zoomToSelected(layer)
        #
        #         if self.check_cb['cb_Flaechen']:
        #             layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]
        #
        #             if layer is not None:
        #                 auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in max_pfad))
        #                 layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #                 iface.mapCanvas().zoomToSelected(layer)
        #
        #             haltungen = ','.join([f'"{str(x)}"' for x in max_haltungen])
        #             sql = f"""Select pk from flaechen where haltnam in ({haltungen})"""
        #
        #             self.db_qkan.sql(sql)
        #             flaechen = []
        #             for i in self.db_qkan.fetchall():
        #                 flaechen.append(i[0])
        #
        #             layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
        #             if layer is not None:
        #                 auswahl = '"pk" IN ({})'.format(", ".join(f"\'{w}\'" for w in flaechen))
        #                 layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #                 iface.mapCanvas().zoomToSelected(layer)
        #
        #     self.db_qkan.getSelection(True)
        #     self.db_qkan.commit()
        #     logger.info(f'Der Längeste Fließweg beträgt {x} m')

        # if self.auswahl == 'kuerzester' and iface.activeLayer().name() == 'Haltungen':
        #     # aktuellen layer auswählen
        #     features = []
        #     layer = iface.activeLayer()
        #     x = layer.source()
        #
        #     # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
        #     _, table, _, _ = get_qkanlayer_attributes(x)
        #     # selektierte elemente anzeigen
        #     self.selected = layer.selectedFeatures()
        #
        #     if not self.selected:
        #         logger.error_user(
        #             "Bedienerfehler: "
        #             'Es wurde keine Auswahl getroffen!'
        #         )
        #         return
        #
        #     for i in self.selected:
        #         attrs = i["pk"]
        #         features.append(attrs)
        #
        #     liste = []
        #     liste2 = []
        #
        #     if table not in ['schaechte', 'haltungen']:
        #         iface.messageBar().pushMessage("Fehler", 'Bitte Haltungen oder Schächte wählen', level=Qgis.MessageLevel.Critical)
        #         return
        #
        #     if table == 'schaechte':
        #         for f in self.selected:
        #             x = f['schnam']
        #             liste.append(x)
        #
        #     if table == 'haltungen':
        #         for f in self.selected:
        #             x = f['schoben']
        #             x2 = f['schunten']
        #             x3 = f['haltnam']
        #             liste2.append(x3)
        #             if x not in liste:
        #                 liste.append(x)
        #             if x2 not in liste:
        #                 liste.append(x2)
        #
        #     route = find_route(self.db_qkan, liste)
        #
        #     liste = []
        #     for x in route[0]:
        #         liste.append(x)
        #     liste2 = []
        #     for y in route[1]:
        #         liste2.append(y)
        #
        #     layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)[0]
        #
        #     if layer is not None:
        #         auswahl = '"Bezeichnung" IN ({})'.format(", ".join(f"\'{w}\'" for w in liste2))
        #         layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #         iface.mapCanvas().zoomToSelected(layer)
        #
        #     haltungen = ','.join([f'"{str(x)}"' for x in liste2])
        #
        #     sql = f"""Select sum(laenge) from haltungen where haltnam in ({haltungen})"""
        #
        #     self.db_qkan.sql(sql)
        #     x = self.db_qkan.fetchall()[0][0]
        #
        #     if self.check_cb['cb_Schaechte']:
        #
        #         layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]
        #
        #         if layer is not None:
        #             auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in liste))
        #             layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #             iface.mapCanvas().zoomToSelected(layer)
        #
        #     if self.check_cb['cb_Flaechen']:
        #         layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]
        #
        #         if layer is not None:
        #             auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in liste))
        #             layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #             iface.mapCanvas().zoomToSelected(layer)
        #
        #         haltungen = ','.join([f'"{str(x)}"' for x in liste2])
        #         sql = f"""Select pk from flaechen where haltnam in ({haltungen})"""
        #
        #         self.db_qkan.sql(sql)
        #         flaechen = []
        #         for i in self.db_qkan.fetchall():
        #             flaechen.append(i[0])
        #
        #         layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
        #         if layer is not None:
        #             auswahl = '"pk" IN ({})'.format(", ".join(f"\'{w}\'" for w in flaechen))
        #             layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
        #             iface.mapCanvas().zoomToSelected(layer)
        #
        #     self.db_qkan.getSelection(True)
        #     self.db_qkan.commit()
        #     logger.info(f'Der kürzeste Fließweg beträgt {x} m')

        if self.auswahl == 'kürzester Weg':
            features = []
            layer = iface.activeLayer()
            x = layer.source()

            # mit dbfunk layer namen anzeigen lassen (für die information ob haltungen oder schächte ausgewählt wurden)
            _, table, _, _ = get_qkanlayer_attributes(x)
            # selektierte elemente anzeigen
            self.selected = layer.selectedFeatures()


            if table not in ['schaechte', 'haltungen']:
                msg = (
                    f"Es wurde keine Auswahl getroffen!"
                )
                raise QkanUserError(msg)

            for i in self.selected:
                attrs = i["pk"]
                features.append(attrs)

            liste = []
            liste2 = []


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
            liste = []
            if route is None:
                logger.warning_user("Zwischen den ausgewählten Objekten besteht keine Verbindung. Bitte Auswahl anpassen!")
                raise QkanUserError
            for x in route[0]:
                liste.append(x)
            liste2 = []
            for y in route[1]:
                liste2.append(y)

            layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.HALTUNGEN.value)[0]

            if layer is not None:
                auswahl = '"Bezeichnung" IN ({})'.format(", ".join(f"\'{w}\'" for w in liste2))
                layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                iface.mapCanvas().zoomToSelected(layer)

            haltungen = ','.join([f'"{str(x)}"' for x in liste2])

            sql = f"""Select sum(laenge) from haltungen where haltnam in ({haltungen})"""

            self.db_qkan.sql(sql)
            x = self.db_qkan.fetchall()[0][0]


            layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

            if layer is not None:
                auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in liste))
                layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                iface.mapCanvas().zoomToSelected(layer)

            layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.SCHAECHTE.value)[0]

            if layer is not None:
                auswahl = '"Schachtname" IN ({})'.format(", ".join(f"\'{w}\'" for w in liste))
                layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                iface.mapCanvas().zoomToSelected(layer)

            self.db_qkan.getSelection(True)
            self.db_qkan.commit()

            haltungen = ','.join([f'"{str(x)}"' for x in liste2])
            sql = f"""Select pk from flaechen where haltnam in ({haltungen})"""

            self.db_qkan.sql(sql)
            flaechen = []
            for i in self.db_qkan.fetchall():
                flaechen.append(i[0])

            layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
            if layer is not None:
                auswahl = '"pk" IN ({})'.format(", ".join(f"\'{w}\'" for w in flaechen))
                layer.selectByExpression(auswahl, QgsVectorLayer.SetSelection)
                iface.mapCanvas().zoomToSelected(layer)

            self.db_qkan.getSelection(True)
            self.db_qkan.commit()
            logger.info(f'Der kürzeste Fließweg beträgt {x} m')

        #Close connection
        #self.db_qkan.__del__()