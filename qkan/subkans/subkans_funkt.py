# -*- coding: utf-8 -*-

import os
import logging
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import Qgis, QgsProject, QgsVectorLayer, QgsDataSourceUri, QgsPrintLayout, QgsReadWriteContext
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt import Qt
from qgis.utils import iface, spatialite_connect
import xml.etree.ElementTree as ElementTree
from typing import Dict, Iterator, Tuple, Union
from lxml import etree
import sqlite3

from datetime import datetime

logger = logging.getLogger("QKan.zustand.import")


class Subkans_funkt:
    def __init__(self, check_cb, db, date, epsg):

        self.check_cb = check_cb
        self.db = db
        self.date = date
        self.crs = epsg
        self.haltung = True

    def run(self):
        check_cb = self.check_cb


        if check_cb['cb1']:
            self.einzelfallbetrachtung_haltung()

        if check_cb['cb2']:
            self.bewertung_dwa_neu_haltung()

        if check_cb['cb3']:
            self.bewertung_subkans()


        if check_cb['cb4']:
            self.schadens_ueberlagerung()

        if check_cb['cb5']:
            self.subkans()

    def bewertung_dwa_neu_haltung(self):
        date = self.date
        db_x = self.db
        crs = self.crs
        haltung = self.haltung

        data = db_x
        db = spatialite_connect(db_x)
        curs = db.cursor()

        if haltung == True:
            sql = """
                        SELECT
                            untersuchdat_haltung_bewertung.pk,
                            untersuchdat_haltung_bewertung.untersuchhal,
                            untersuchdat_haltung_bewertung.untersuchrichtung,
                            untersuchdat_haltung_bewertung.schoben,
                            untersuchdat_haltung_bewertung.schunten,
                            untersuchdat_haltung_bewertung.id,
                            untersuchdat_haltung_bewertung.videozaehler,
                            untersuchdat_haltung_bewertung.inspektionslaenge,
                            untersuchdat_haltung_bewertung.station,
                            untersuchdat_haltung_bewertung.timecode,
                            untersuchdat_haltung_bewertung.kuerzel,
                            untersuchdat_haltung_bewertung.charakt1,
                            untersuchdat_haltung_bewertung.charakt2,
                            untersuchdat_haltung_bewertung.quantnr1,
                            untersuchdat_haltung_bewertung.quantnr2,
                            untersuchdat_haltung_bewertung.streckenschaden,
                            untersuchdat_haltung_bewertung.pos_von,
                            untersuchdat_haltung_bewertung.pos_bis,
                            untersuchdat_haltung_bewertung.foto_dateiname,
                            untersuchdat_haltung_bewertung.film_dateiname,
                            untersuchdat_haltung_bewertung.richtung,
                            untersuchdat_haltung_bewertung.bw_bs,
                            untersuchdat_haltung_bewertung.createdat,
                            haltungen.haltnam,
                            haltungen.material,
                            haltungen.hoehe,
                            haltungen.createdat
                        FROM untersuchdat_haltung_bewertung, haltungen
                        WHERE haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND untersuchdat_haltung_bewertung.createdat like ? 
                    """
            data = (date,)

            curs.execute(sql, data)


        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_dichtheit =
                                (SELECT min(Zustandsklasse_D) 
                                FROM untersuchdat_haltung_bewertung
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_haltung_bewertung.untersuchhal);""")
            #db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_standsicherheit =
                                (SELECT min(Zustandsklasse_S) 
                                FROM untersuchdat_haltung_bewertung
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_haltung_bewertung.untersuchhal);""")
            #db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_betriebssicherheit =
                                (SELECT min(Zustandsklasse_B) 
                                FROM untersuchdat_haltung_bewertung
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_haltung_bewertung.untersuchhal);""")
            #db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_standsicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_dichtheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_betriebssicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            curs.execute("""Update
                                haltungen_untersucht_bewertung
                                SET
                                objektklasse_gesamt =
                                (Case
                                 When objektklasse_dichtheit <= objektklasse_standsicherheit And objektklasse_dichtheit <= objektklasse_betriebssicherheit Then objektklasse_dichtheit
                                 When objektklasse_standsicherheit <= objektklasse_dichtheit And objektklasse_standsicherheit <= objektklasse_betriebssicherheit Then objektklasse_standsicherheit
                                 When objektklasse_betriebssicherheit <= objektklasse_dichtheit And objektklasse_betriebssicherheit <= objektklasse_standsicherheit Then objektklasse_betriebssicherheit
                                 Else NULL
                                 END
                                 );""")
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        untersuchdat_haltung_bewertung = 'untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'haltungen_untersucht_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        haltungen_untersucht_bewertung = 'haltungen_untersucht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), haltungen_untersucht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(haltungen_untersucht_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/haltungen_untersucht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)


    def einzelfallbetrachtung_haltung(self):

        date = self.date+'%'
        db = self.db
        db_x = db
        data = db
        haltung = self.haltung
        crs = self.crs
        liste_pk =[]
        db1 = spatialite_connect(data)
        curs1 = db1.cursor()

        # nach SubKans

        data = db
        db = spatialite_connect(data)
        curs = db.cursor()

        if haltung == True:
            sql = """SELECT
                        untersuchdat_haltung_bewertung.pk,
                        untersuchdat_haltung_bewertung.untersuchhal,
                        untersuchdat_haltung_bewertung.untersuchrichtung,
                        untersuchdat_haltung_bewertung.schoben,
                        untersuchdat_haltung_bewertung.schunten,
                        untersuchdat_haltung_bewertung.id,
                        untersuchdat_haltung_bewertung.videozaehler,
                        untersuchdat_haltung_bewertung.inspektionslaenge,
                        untersuchdat_haltung_bewertung.station,
                        untersuchdat_haltung_bewertung.timecode,
                        untersuchdat_haltung_bewertung.kuerzel,
                        untersuchdat_haltung_bewertung.charakt1,
                        untersuchdat_haltung_bewertung.charakt2,
                        untersuchdat_haltung_bewertung.quantnr1,
                        untersuchdat_haltung_bewertung.quantnr2,
                        untersuchdat_haltung_bewertung.streckenschaden,
                        untersuchdat_haltung_bewertung.pos_von,
                        untersuchdat_haltung_bewertung.pos_bis,
                        untersuchdat_haltung_bewertung.foto_dateiname,
                        untersuchdat_haltung_bewertung.film_dateiname,
                        untersuchdat_haltung_bewertung.richtung,
                        untersuchdat_haltung_bewertung.bw_bs,
                        untersuchdat_haltung_bewertung.createdat,
                        haltungen.haltnam,
                        haltungen.material,
                        haltungen.hoehe,
                        haltungen.createdat,
                        untersuchdat_haltung_bewertung.Zustandsklasse_D,
                        untersuchdat_haltung_bewertung.Zustandsklasse_S,
                        untersuchdat_haltung_bewertung.Zustandsklasse_B
                        FROM
                        untersuchdat_haltung_bewertung, haltungen
                        WHERE
                        haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
                        AND(untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                        OR
                        untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                        OR
                        untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung') AND untersuchdat_haltung_bewertung.createdat like ? """
            data = (date,)
            curs.execute(sql, data)


        for attr in curs.fetchall():
            liste_pk.append(attr[0])

            if attr[10] == "BAB" and attr[11] == "A" and (attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #     db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                if attr[13] >= 3:
                    z = '1'
                elif 3 > attr[13] >= 2:
                    z = '2'
                elif attr[13] < 2:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #     db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] in ["", "not found"]:
                if attr[13] >= 8:
                    z = '0'
                elif 8 > attr[13] >= 5:
                    z = '1'
                elif 5 > attr[13] >= 3:
                    z = '2'
                elif 3 > attr[13] >= 1:
                    z = '3'
                elif attr[13] < 1:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] <= 0.3:
                if attr[13] >= 3:
                    z = '0'
                elif 3 > attr[13] >= 2:
                    z = '1'
                elif 2 > attr[13] >= 1:
                    z = '2'
                elif 1 > attr[13] >= 0.5:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.5 >= attr[25] > 0.3:
                if attr[13] >= 5:
                    z = '0'
                elif 5 > attr[13] >= 3:
                    z = '1'
                elif 3 > attr[13] >= 2:
                    z = '2'
                elif 2 > attr[13] >= 1:
                    z = '3'
                elif attr[13] < 1:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.7 >= attr[25] > 0.5:
                if attr[13] >= 8:
                    z = '0'
                elif 8 > attr[13] >= 4:
                    z = '1'
                elif 4 > attr[13] >= 3:
                    z = '2'
                elif 3 > attr[13] >= 2:
                    z = '3'
                elif attr[13] < 2:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "B":
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                if attr[13] >= 8:
                    z = '0'
                elif 8 > attr[13] >= 5:
                    z = '1'
                elif 5 > attr[13] >= 3:
                    z = '2'
                elif 3 > attr[13] >= 1:
                    z = '3'
                elif attr[13] < 1:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "A":
                z = '1'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0]);
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "B":
                z = '1'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                                      UPDATE untersuchdat_haltung_bewertung
                                        SET Zustandsklasse_B = ?
                                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "C":
                z = '0'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "A":
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "B" and attr[12] == "A":
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "B" and attr[12] == "B":
                z = '1'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "C":
                z = '0'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "D":
                z = '0'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAE":
                if attr[13] >= 100:
                    z = '2'
                if attr[13] < 100:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                if attr[13] >= 100:
                    z = '2'
                elif 100 > attr[13] > 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "A" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "B" and (attr[12] == "A" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "C" and (
                    attr[12] == "A"  or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "D" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "E" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '1'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "F" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "G" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "H" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '1'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "I" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '1'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '1'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "J" and (attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "K" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                                      UPDATE untersuchdat_haltung_bewertung
                                        SET Zustandsklasse_B = ?
                                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "Z" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAG":
                if attr[25] <= 0.25:
                    if attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 30:
                        z = '1'
                    elif 30 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                if 0.25 < attr[25] <= 0.5:
                    if attr[13] >= 80:
                        z = '0'
                    elif 80 > attr[13] >= 60:
                        z = '1'
                    elif 60 > attr[13] >= 40:
                        z = '2'
                    elif 40 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                if 0.5 < attr[25] <= 0.8:
                    if attr[13] >= 70:
                        z = '2'
                    elif 70 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                if attr[25] > 0.8:
                    if attr[13] >= 30:
                        z = '3'
                    elif attr[13] < 30:
                        z = '4'
                    else:
                        z = '5'
                sql = f"""
                        UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and (attr[11] == "B" or attr[11] == "C" or attr[11] == "D"):
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and attr[11] == "E":
                z = '-'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and attr[11] == "Z":
                z = '3'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "A" and attr[12] == "A":
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "A" and (attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '2'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "Z" and attr[12] == "Y":
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "A":
                if attr[25] <= 0.4:
                    if attr[13] >= 70:
                        z = '0'
                    elif 70 > attr[13] >= 50:
                        z = '1'
                    elif 50 > attr[13] >= 30:
                        z = '2'
                    elif 30 > attr[13] >= 20:
                        z = '3'
                    elif attr[13] < 20:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #db.commit()
                    except:
                        pass
                if 0.4 < attr[25] <= 0.8:
                    if attr[13] >= 80:
                        z = '0'
                    elif 80 > attr[13] >= 60:
                        z = '1'
                    elif 60 > attr[13] >= 40:
                        z = '2'
                    elif 40 > attr[13] >= 20:
                        z = '3'
                    elif attr[13] < 20:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #db.commit()
                    except:
                        pass
                if attr[25] > 0.8:
                    if attr[13] >= 90:
                        z = '0'
                    elif 90 > attr[13] >= 65:
                        z = '1'
                    elif 65 > attr[13] >= 40:
                        z = '2'
                    elif 40 > attr[13] >= 20:
                        z = '3'
                    elif attr[13] < 20:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #db.commit()
                    except:
                        pass
                z = '4'
                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "B":
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 15:
                    z = '2'
                elif 15 > attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                if attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "C":
                if attr[25] <= 0.2:
                    if attr[13] >= 12:
                        z = '0'
                    elif 12 > attr[13] >= 9:
                        z = '1'
                    elif 9 > attr[13] >= 7:
                        z = '2'
                    elif 7 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #db.commit()
                    except:
                        pass
                if 0.2 < attr[25] <= 0.5:
                    if attr[13] >= 6:
                        z = '0'
                    elif 6 > attr[13] >= 4:
                        z = '1'
                    elif 4 > attr[13] >= 3:
                        z = '2'
                    elif 3 > attr[13] >= 2:
                        z = '3'
                    elif attr[13] < 2:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #db.commit()
                    except:
                        pass
                if attr[25] > 0.5:
                    if attr[13] >= 6:
                        z = '0'
                    elif 6 > attr[13] >= 4:
                        z = '1'
                    elif 4 > attr[13] >= 3:
                        z = '2'
                    elif 3 > attr[13] >= 1:
                        z = '3'
                    elif attr[13] < 1:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #db.commit()
                    except:
                        pass
                z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "A":
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "B":
                z = '4'
                sql = f"""
                                    UPDATE untersuchdat_haltung_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and (attr[11] == "C"):
                z = '2'
                sql = f"""
                        UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D" and (attr[12] == "A" or attr[12] == "B" or attr[12] == "D"):
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D" and (attr[12] == "C"):
                z = '2'
                sql = f"""
                        UPDATE untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE untersuchdat_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "E":
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "F":
                z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "G":
                z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "H":
                z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "I":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "J":
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "K":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "L":
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                                    UPDATE untersuchdat_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "M":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "N":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "Z":
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "A" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "B" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "C" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "D" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "E" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "F" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "G" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "Z" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and (attr[11] == "A" or attr[11] == "C"):
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and attr[11] == "B":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAN":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAO":
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAP":
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBA" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C"):
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB" and attr[11] == "A":
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif 10 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC" and (attr[11] == "A" or attr[11] == "B"):
                z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC" and (attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 40:
                    z = '1'
                elif 40 > attr[13] >= 25:
                    z = '2'
                elif 25 > attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBD" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "Z"):
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (attr[11] == "D" or attr[11] == "G"):
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E" or attr[
                11] == "F" or attr[11] == "G" or attr[11] == "H" or attr[11] == "Z"):
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and attr[11] == "A":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and (attr[11] == "B" or attr[11] == "C"):
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and attr[11] == "D":
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBG":
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBH" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "Z") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "Z"):
                z = '-'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and (attr[11] == "AA" or attr[11] == "AB" or attr[11] == "AC" or attr[11] == "AD" or attr[11] == "AE"):
                z = '3'
                sql = f"""
                                    UPDATE untersuchdat_haltung_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and (attr[11] == "BA" or attr[11] == "BB" or attr[11] == "BC"):
                z = '3'
                sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE untersuchdat_haltung_bewertung.pk = ?;
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E") and attr[12] == "A":
                z = '1'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E") and attr[12] == "B":
                z = '2'
                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE untersuchdat_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #db.commit()
                    continue
                except:
                    pass

            try:
                db.commit()
            except:
                pass

            z = '-'
            sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE untersuchdat_haltung_bewertung.pk = ?
                            """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE untersuchdat_haltung_bewertung.pk = ?
                            """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE untersuchdat_haltung_bewertung.pk = ?
                            """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
        z = '5'
        sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Zustandsklasse_D is Null
                            """
        data = (z,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass
        sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Zustandsklasse_B is Null
                            """
        data = (z,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass
        sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Zustandsklasse_S is Null
                            """
        data = (z,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass


        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        untersuchdat_haltung_bewertung = 'untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'haltungen_untersucht_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        haltungen_untersucht_bewertung = 'haltungen_untersucht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), haltungen_untersucht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(haltungen_untersucht_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/haltungen_untersucht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)


    def bewertung_dwa_haltung(self):
        #Beispielcode aus Zustandsklassen

        date = self.date + '%'
        db_x = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        data = db_x

        db1 = spatialite_connect(data)
        curs1 = db1.cursor()

        logger.debug(f'Start_Bewertung_Haltungen.liste: {datetime.now()}')
        # nach DWA

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_haltung_bewertung AS SELECT * FROM untersuchdat_haltung"""
        curs1.execute(sql)

        if haltung == True:
            sql = """
                   SELECT
                       haltungen.haltnam,
                       haltungen.material,
                       haltungen.hoehe,
                       untersuchdat_haltung_bewertung.untersuchhal
                   FROM haltungen
                   INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
               """

        if leitung == True:
            sql = """
                       SELECT
                           anschlussleitungen.leitnam,
                           anschlussleitungen.material,
                           anschlussleitungen.hoehe,
                           untersuchdat_haltung_bewertung.untersuchhal
                       FROM anschlussleitungen
                       INNER JOIN untersuchdat_haltung_bewertung ON anschlussleitungen.leitnam = untersuchdat_haltung_bewertung.untersuchhal
                   """

        try:
            curs1.execute(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        for attr1 in curs1.fetchall():

            untersuchhalt = attr1[0]
            try:
                curs1.execute("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "B", "BS", "FZ", "MA", "OB", "P", "PC", "PCC", "PHB", "SFB", "SPB", "SB", "STZ",
                            "SZB", "ZG"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                           SET bw_bs = ?
                           WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                           """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass

            if attr1[1] in ["CNS", "EIS", "GFK", "GG", "GGG", "KST", "PE", "PEHD", "PH", "PP", "PVC", "PVCU", "ST"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET bw_bs = ?
                           WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                           """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass
            db1.commit()

        db = spatialite_connect(db_x)
        curs = db.cursor()

        if haltung == True:
            sql = """
                   SELECT
                       untersuchdat_haltung_bewertung.pk,
                       untersuchdat_haltung_bewertung.untersuchhal,
                       untersuchdat_haltung_bewertung.untersuchrichtung,
                       untersuchdat_haltung_bewertung.schoben,
                       untersuchdat_haltung_bewertung.schunten,
                       untersuchdat_haltung_bewertung.id,
                       untersuchdat_haltung_bewertung.videozaehler,
                       untersuchdat_haltung_bewertung.inspektionslaenge,
                       untersuchdat_haltung_bewertung.station,
                       untersuchdat_haltung_bewertung.timecode,
                       untersuchdat_haltung_bewertung.kuerzel,
                       untersuchdat_haltung_bewertung.charakt1,
                       untersuchdat_haltung_bewertung.charakt2,
                       untersuchdat_haltung_bewertung.quantnr1,
                       untersuchdat_haltung_bewertung.quantnr2,
                       untersuchdat_haltung_bewertung.streckenschaden,
                       untersuchdat_haltung_bewertung.pos_von,
                       untersuchdat_haltung_bewertung.pos_bis,
                       untersuchdat_haltung_bewertung.foto_dateiname,
                       untersuchdat_haltung_bewertung.film_dateiname,
                       untersuchdat_haltung_bewertung.richtung,
                       untersuchdat_haltung_bewertung.bw_bs,
                       untersuchdat_haltung_bewertung.createdat,
                       haltungen.haltnam,
                       haltungen.material,
                       haltungen.hoehe,
                       haltungen.createdat
                   FROM untersuchdat_haltung_bewertung, haltungen
                   WHERE haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND untersuchdat_haltung_bewertung.createdat like ? 
               """
            data = (date,)

            curs.execute(sql, data)

        if leitung == True:
            sql = """
                   SELECT
                       untersuchdat_haltung_bewertung.pk,
                       untersuchdat_haltung_bewertung.untersuchhal,
                       untersuchdat_haltung_bewertung.untersuchrichtung,
                       untersuchdat_haltung_bewertung.schoben,
                       untersuchdat_haltung_bewertung.schunten,
                       untersuchdat_haltung_bewertung.id,
                       untersuchdat_haltung_bewertung.videozaehler,
                       untersuchdat_haltung_bewertung.inspektionslaenge,
                       untersuchdat_haltung_bewertung.station,
                       untersuchdat_haltung_bewertung.timecode,
                       untersuchdat_haltung_bewertung.kuerzel,
                       untersuchdat_haltung_bewertung.charakt1,
                       untersuchdat_haltung_bewertung.charakt2,
                       untersuchdat_haltung_bewertung.quantnr1,
                       untersuchdat_haltung_bewertung.quantnr2,
                       untersuchdat_haltung_bewertung.streckenschaden,
                       untersuchdat_haltung_bewertung.pos_von,
                       untersuchdat_haltung_bewertung.pos_bis,
                       untersuchdat_haltung_bewertung.foto_dateiname,
                       untersuchdat_haltung_bewertung.film_dateiname,
                       untersuchdat_haltung_bewertung.richtung,
                       untersuchdat_haltung_bewertung.bw_bs,
                       untersuchdat_haltung_bewertung.createdat,
                       anschlussleitungen.leitnam,
                       anschlussleitungen.material,
                       anschlussleitungen.hoehe,
                       anschlussleitungen.createdat
                   FROM untersuchdat_haltung_bewertung, anschlussleitungen
                   WHERE anschlussleitungen.leitnam = untersuchdat_haltung_bewertung.untersuchhal AND untersuchdat_haltung_bewertung.createdat , 0, 15 like ? 
               """
            data = (date,)

            curs.execute(sql, data)

        logger.debug(f'Start_forloop_Bewertung_Haltungen.liste: {datetime.now()}')

        for attr in curs.fetchall():
            try:
                curs.execute("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
            except:
                pass

            # Tab A.2
            if (attr[21] == "biegessteif" and attr[10] == "BAA" and attr[11] == "A") or (
                    attr[21] == "biegessteif" and attr[10] == "BAA" and attr[11] == "B"):
                if attr[13] >= 7:
                    z = '0'
                elif 4 <= attr[13] < 7:
                    z = '1'
                elif 3 <= attr[13] < 4:
                    z = '2'
                elif 1 <= attr[13] < 3:
                    z = '3'
                elif attr[13] < 1:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '0'
                elif 40 <= attr[13] < 50:
                    z = '1'
                elif 25 <= attr[13] < 40:
                    z = '2'
                elif 10 <= attr[13] < 25:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ? 
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if (attr[21] == "biegeweich" and attr[10] == "BAA" and attr[11] == "A") or (
                    attr[21] == "biegeweich" and attr[10] == "BAA" and attr[11] == "B"):
                if attr[13] >= 15:
                    z = '0'
                elif 10 <= attr[13] < 15:
                    z = '1'
                elif 6 <= attr[13] < 10:
                    z = '2'
                elif 2 <= attr[13] < 6:
                    z = '3'
                elif attr[13] < 2:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ? 
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '0'
                elif 40 <= attr[13] < 50:
                    z = '1'
                elif 25 <= attr[13] < 40:
                    z = '2'
                elif 10 <= attr[13] < 25:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ? 
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            sql = ""
            data = ()

            # Tab A.3
            if attr[10] == "BAB" and attr[11] == "A" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #     db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                if attr[13] >= 3:
                    z = '1'
                elif 3 > attr[13] >= 2:
                    z = '2'
                elif attr[13] < 2:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    #     db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] in ["",
                                                                                                               "not found"]:
                if attr[13] >= 8:
                    z = '0'
                elif 8 > attr[13] >= 5:
                    z = '1'
                elif 5 > attr[13] >= 3:
                    z = '2'
                elif 3 > attr[13] >= 1:
                    z = '3'
                elif attr[13] < 1:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] <= 0.3:
                if attr[13] >= 3:
                    z = '0'
                elif 3 > attr[13] >= 2:
                    z = '1'
                elif 2 > attr[13] >= 1:
                    z = '2'
                elif 1 > attr[13] >= 0.5:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.5 >= attr[
                25] > 0.3:
                if attr[13] >= 5:
                    z = '0'
                elif 5 > attr[13] >= 3:
                    z = '1'
                elif 3 > attr[13] >= 2:
                    z = '2'
                elif 2 > attr[13] >= 1:
                    z = '3'
                elif attr[13] < 1:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.7 >= attr[
                25] > 0.5:
                if attr[13] >= 8:
                    z = '0'
                elif 8 > attr[13] >= 4:
                    z = '1'
                elif 4 > attr[13] >= 3:
                    z = '2'
                elif 3 > attr[13] >= 2:
                    z = '3'
                elif attr[13] < 2:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "B":
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (
                    attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "A":
                z = '1'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0]);
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "B":
                z = '1'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "C":
                z = '0'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "A":
                z = '2'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "B" and attr[12] == "A":
                z = '2'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "B" and attr[12] == "B":
                z = '1'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "C":
                z = '0'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "D":
                z = '0'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAE":
                if attr[13] >= 100:
                    z = '2'
                if attr[13] < 100:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                if attr[13] >= 100:
                    z = '2'
                elif 100 > attr[13] > 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "A" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "B" and (attr[12] == "A" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "C" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '3'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "D" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '2'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "E" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '1'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "F" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '3'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "G" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '2'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "H" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '1'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "I" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '1'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "J" and (
                    attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "K" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = '3'
                sql = f"""
                                         UPDATE untersuchdat_haltung_bewertung
                                           SET Zustandsklasse_B = ?
                                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "Z" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or
                    attr[12] == "Z"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAG":
                if attr[25] <= 0.25:
                    if attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 30:
                        z = '1'
                    elif 30 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                if 0.25 < attr[25] <= 0.5:
                    if attr[13] >= 80:
                        z = '0'
                    elif 80 > attr[13] >= 60:
                        z = '1'
                    elif 60 > attr[13] >= 40:
                        z = '2'
                    elif 40 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                if 0.5 < attr[25] <= 0.8:
                    if attr[13] >= 70:
                        z = '2'
                    elif 70 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                if attr[25] > 0.8:
                    if attr[13] >= 30:
                        z = '3'
                    elif attr[13] < 30:
                        z = '4'
                    else:
                        z = '5'
                sql = f"""
                           UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and (attr[11] == "B" or attr[11] == "C" or attr[11] == "D"):
                z = '2'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and attr[11] == "E":
                z = '-'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and attr[11] == "Z":
                z = 'Einzelfallbetrachtung'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "A" and attr[12] == "A":
                z = '2'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "A" and (attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '2'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "Z" and attr[12] == "Y":
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_B = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "A":
                if attr[25] <= 0.4:
                    if attr[13] >= 70:
                        z = '0'
                    elif 70 > attr[13] >= 50:
                        z = '1'
                    elif 50 > attr[13] >= 30:
                        z = '2'
                    elif 30 > attr[13] >= 20:
                        z = '3'
                    elif attr[13] < 20:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                    except:
                        pass
                if 0.4 < attr[25] <= 0.8:
                    if attr[13] >= 80:
                        z = '0'
                    elif 80 > attr[13] >= 60:
                        z = '1'
                    elif 60 > attr[13] >= 40:
                        z = '2'
                    elif 40 > attr[13] >= 20:
                        z = '3'
                    elif attr[13] < 20:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                    except:
                        pass
                if attr[25] > 0.8:
                    if attr[13] >= 90:
                        z = '0'
                    elif 90 > attr[13] >= 65:
                        z = '1'
                    elif 65 > attr[13] >= 40:
                        z = '2'
                    elif 40 > attr[13] >= 20:
                        z = '3'
                    elif attr[13] < 20:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                    except:
                        pass
                z = '4'
                sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "B":
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 15:
                    z = '2'
                elif 15 > attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "C":
                if attr[25] <= 0.2:
                    if attr[13] >= 12:
                        z = '0'
                    elif 12 > attr[13] >= 9:
                        z = '1'
                    elif 9 > attr[13] >= 7:
                        z = '2'
                    elif 7 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                    except:
                        pass
                if 0.2 < attr[25] <= 0.5:
                    if attr[13] >= 6:
                        z = '0'
                    elif 6 > attr[13] >= 4:
                        z = '1'
                    elif 4 > attr[13] >= 3:
                        z = '2'
                    elif 3 > attr[13] >= 2:
                        z = '3'
                    elif attr[13] < 2:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                    except:
                        pass
                if attr[25] > 0.5:
                    if attr[13] >= 6:
                        z = '0'
                    elif 6 > attr[13] >= 4:
                        z = '1'
                    elif 4 > attr[13] >= 3:
                        z = '2'
                    elif 3 > attr[13] >= 1:
                        z = '3'
                    elif attr[13] < 1:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                         UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                    except:
                        pass
                z = '4'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "A":
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "B":
                z = '4'
                sql = f"""
                                       UPDATE untersuchdat_haltung_bewertung
                                       SET Zustandsklasse_D = ?
                                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and (attr[11] == "C"):
                z = '2'
                sql = f"""
                           UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_D = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D" and (attr[12] == "A" or attr[12] == "B" or attr[12] == "D"):
                z = 'Einzelfalletrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D" and (attr[12] == "C"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                           UPDATE untersuchdat_haltung_bewertung
                           SET Zustandsklasse_S = ?
                           WHERE untersuchdat_haltung_bewertung.pk = ?;
                           """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "E":
                z = 'Einzelfallbetrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "F":
                z = '4'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "G":
                z = '4'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "H":
                z = '4'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "I":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "J":
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "K":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "L":
                z = '3'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                                       UPDATE untersuchdat_haltung_bewertung
                                       SET Zustandsklasse_S = ?
                                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "M":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "N":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "Z":
                z = 'Einzelfalletrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "A" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "B" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "C" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "D" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "E" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "F" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "G" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '3'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "Z" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and (attr[11] == "A" or attr[11] == "C"):
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and attr[11] == "B":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAN":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAO":
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAP":
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBA" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C"):
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB" and attr[11] == "A":
                z = '3'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif 10 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC" and (attr[11] == "A" or attr[11] == "B"):
                z = '4'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC" and (attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 40:
                    z = '1'
                elif 40 > attr[13] >= 25:
                    z = '2'
                elif 25 > attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBD" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "Z"):
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                if attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (attr[11] == "D" or attr[11] == "G"):
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E" or
                    attr[
                        11] == "F" or attr[11] == "G" or attr[11] == "H" or attr[11] == "Z"):
                if attr[13] >= 50:
                    z = '0'
                elif 50 > attr[13] >= 35:
                    z = '1'
                elif 35 > attr[13] >= 20:
                    z = '2'
                elif 20 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and attr[11] == "A":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and (attr[11] == "B" or attr[11] == "C"):
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and attr[11] == "D":
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBG":
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBH" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "Z") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "Z"):
                z = '-'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and (
                    attr[11] == "AA" or attr[11] == "AB" or attr[11] == "AC" or attr[11] == "AD" or attr[
                11] == "AE"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                                       UPDATE untersuchdat_haltung_bewertung
                                       SET Zustandsklasse_D = ?
                                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and (attr[11] == "BA" or attr[11] == "BB" or attr[11] == "BC"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                               UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_D = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E") and \
                    attr[12] == "A":
                z = '1'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E") and \
                    attr[12] == "B":
                z = '2'
                sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE untersuchdat_haltung_bewertung.pk = ?;
                       """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass

            # if für alle übrigen sachen Haltungsanfang ende usw.
            if attr[10] in ["BCD", "BDD", "BCE", "BDC", "BCA", "BCB", "BCC", "BDA", "BDF", "BDG", "BDB", "AEC",
                            "AED"]:
                z = '-'
                sql = f"""
                                  UPDATE untersuchdat_haltung_bewertung
                                  SET Zustandsklasse_D = ?
                                  WHERE untersuchdat_haltung_bewertung.pk = ?;
                                  """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                                  UPDATE untersuchdat_haltung_bewertung
                                  SET Zustandsklasse_B = ?
                                  WHERE untersuchdat_haltung_bewertung.pk = ?;
                                  """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                except:
                    pass
                sql = f"""
                                  UPDATE untersuchdat_haltung_bewertung
                                  SET Zustandsklasse_S = ?
                                  WHERE untersuchdat_haltung_bewertung.pk = ?;
                                  """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    # db.commit()
                    continue
                except:
                    pass

            try:
                db.commit()
            except:
                pass

            z = 'Bitte pruefen!'
            sql = f"""
                   UPDATE untersuchdat_haltung_bewertung
                   SET Zustandsklasse_D = ?
                   WHERE untersuchdat_haltung_bewertung.pk = ?;
                   """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                # db.commit()
            except:
                pass
            sql = f"""
                   UPDATE untersuchdat_haltung_bewertung
                   SET Zustandsklasse_B = ?
                   WHERE untersuchdat_haltung_bewertung.pk = ?;
                   """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                # db.commit()
            except:
                pass
            sql = f"""
                   UPDATE untersuchdat_haltung_bewertung
                   SET Zustandsklasse_S = ?
                   WHERE untersuchdat_haltung_bewertung.pk = ?;
                   """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                # db.commit()
            except:
                pass
            z = '5'
            sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_D = ?
                       WHERE Zustandsklasse_D is Null;
                       """
            data = (z,)
            try:
                curs.execute(sql, data)
                # db.commit()
            except:
                pass
            sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_B = ?
                       WHERE Zustandsklasse_B is Null;
                       """
            data = (z,)
            try:
                curs.execute(sql, data)
                # db.commit()
            except:
                pass
            sql = f"""
                       UPDATE untersuchdat_haltung_bewertung
                       SET Zustandsklasse_S = ?
                       WHERE Zustandsklasse_S is Null;
                       """
            data = (z,)
            try:
                curs.execute(sql, data)
                # db.commit()
            except:
                pass

            try:
                db.commit()
            except:
                pass

        sql = """CREATE TABLE IF NOT EXISTS haltungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
        curs.execute(sql)
        try:
            curs.execute(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
        except:
            pass
        try:
            curs.execute(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            curs.execute(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
            # db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT;""")
            # db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
            # db.commit()
        except:
            pass

        # Objektklasse berechnen für jede Haltung dafür abfragen

        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                               SET objektklasse_dichtheit =
                               (SELECT min(Zustandsklasse_D) 
                               FROM untersuchdat_haltung_bewertung
                               WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_D <> '-'
                               GROUP BY untersuchdat_haltung_bewertung.untersuchhal);""")
            # db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                               SET objektklasse_standsicherheit =
                               (SELECT min(Zustandsklasse_S) 
                               FROM untersuchdat_haltung_bewertung
                               WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_S <> '-'
                               GROUP BY untersuchdat_haltung_bewertung.untersuchhal);""")
            # db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                               SET objektklasse_betriebssicherheit =
                               (SELECT min(Zustandsklasse_B) 
                               FROM untersuchdat_haltung_bewertung
                               WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_B <> '-'
                               GROUP BY untersuchdat_haltung_bewertung.untersuchhal);""")
            # db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                               set objektklasse_standsicherheit = '-'
                               WHERE objektklasse_betriebssicherheit IS NULL;""")
            # db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                               set objektklasse_dichtheit = '-'
                               WHERE objektklasse_betriebssicherheit IS NULL;""")
            # db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                               set objektklasse_betriebssicherheit = '-'
                               WHERE objektklasse_betriebssicherheit IS NULL;""")
            # db.commit()
        except:
            pass

        try:
            curs.execute("""Update
                               haltungen_untersucht_bewertung
                               SET
                               objektklasse_gesamt =
                               (Case
                                When objektklasse_dichtheit <= objektklasse_standsicherheit And objektklasse_dichtheit <= objektklasse_betriebssicherheit Then objektklasse_dichtheit
                                When objektklasse_standsicherheit <= objektklasse_dichtheit And objektklasse_standsicherheit <= objektklasse_betriebssicherheit Then objektklasse_standsicherheit
                                When objektklasse_betriebssicherheit <= objektklasse_dichtheit And objektklasse_betriebssicherheit <= objektklasse_standsicherheit Then objektklasse_betriebssicherheit
                                Else NULL
                                END
                                );""")
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        logger.debug(f'Ende_Bewertung_Haltungen.liste: {datetime.now()}')

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        untersuchdat_haltung_bewertung = 'untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'haltungen_untersucht_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        haltungen_untersucht_bewertung = 'haltungen_untersucht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), haltungen_untersucht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(haltungen_untersucht_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/haltungen_untersucht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)

    def bewertung_subkans(self):
        #Schadensart und -ausprägung ergänzen

        date = self.date + '%'
        db_x = self.db
        crs = self.crs
        haltung = self.haltung

        data = db_x

        db1 = spatialite_connect(data)
        curs1 = db1.cursor()

        logger.debug(f'Start_Bewertung_Haltungen.liste: {datetime.now()}')
        # nach DWA

        sql = """CREATE TABLE IF NOT EXISTS substanz_haltung_bewertung AS 
                SELECT pk, 
                untersuchhal, 
                untersuchrichtung,
                schoben,
                schunten,
                id,
                videozaehler,
                inspektionslaenge,
                station,
                timecode,
                kuerzel,
                charakt1,
                charakt2,
                quantnr1,
                quantnr2,
                streckenschaden,
                pos_von,
                pos_bis,
                foto_dateiname,
                film_dateiname,
                bw_bs,
                cratedat,
                Zustandsklasse_D,
                Zustandsklasse_S,
                Zustandsklasse_B,
                FROM untersuchdat_haltung_bewertung"""
        curs1.execute(sql)

        db = spatialite_connect(db_x)
        curs = db.cursor()

        if haltung == True:
            sql = """
                   SELECT
                       substanz_haltung_bewertung.pk,
                       substanz_haltung_bewertung.untersuchhal,
                       substanz_haltung_bewertung.untersuchrichtung,
                       substanz_haltung_bewertung.schoben,
                       substanz_haltung_bewertung.schunten,
                       substanz_haltung_bewertung.id,
                       substanz_haltung_bewertung.videozaehler,
                       substanz_haltung_bewertung.inspektionslaenge,
                       substanz_haltung_bewertung.station,
                       substanz_haltung_bewertung.timecode,
                       substanz_haltung_bewertung.kuerzel,
                       substanz_haltung_bewertung.charakt1,
                       substanz_haltung_bewertung.charakt2,
                       substanz_haltung_bewertung.quantnr1,
                       substanz_haltung_bewertung.quantnr2,
                       substanz_haltung_bewertung.streckenschaden,
                       substanz_haltung_bewertung.pos_von,
                       substanz_haltung_bewertung.pos_bis,
                       substanz_haltung_bewertung.foto_dateiname,
                       substanz_haltung_bewertung.film_dateiname,
                       substanz_haltung_bewertung.richtung,
                       substanz_haltung_bewertung.bw_bs,
                       substanz_haltung_bewertung.createdat,
                       haltungen.haltnam,
                       haltungen.material,
                       haltungen.hoehe,
                       haltungen.createdat
                   FROM substanz_haltung_bewertung, haltungen
                   WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND substanz_haltung_bewertung.createdat like ? 
               """
            data = (date,)

            curs.execute(sql, data)

            try:
                curs.execute("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadensart TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadensauspraegung TEXT ;""")
            except:
                pass

            for attr in curs.fetchall():

                if (attr[10] == "BAA" and attr[11] == "A") or ( attr[10] == "BAA" and attr[11] == "B"):
                    if attr[15] in ["", "None", "not found"]:
                        z = 'PktS'
                        sql = f"""
                                 UPDATE substanz_haltung_bewertung
                                   SET Schadensart = ?
                                   WHERE substanz_haltung_bewertung.pk = ?;
                                   """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                 UPDATE substanz_haltung_bewertung
                                   SET Schadensauspraegung = ?
                                   WHERE substanz_haltung_bewertung.pk = ? 
                                   """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                 UPDATE substanz_haltung_bewertung
                                   SET Schadensart = ?
                                   WHERE substanz_haltung_bewertung.pk = ?;
                                   """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                         UPDATE substanz_haltung_bewertung
                                                           SET Schadensauspraegung = ?
                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                           """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass

                # Tab A.3
                if attr[10] == "BAB" and attr[11] == "A" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                    z = '4'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_S = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #     db.commit()
                        continue
                    except:
                        pass
                if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                    if attr[13] >= 3:
                        z = '1'
                    elif 3 > attr[13] >= 2:
                        z = '2'
                    elif attr[13] < 2:
                        z = '3'
                    else:
                        z = '5'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_D = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        #     db.commit()
                        continue
                    except:
                        pass
                if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] in ["",
                                                                                                                   "not found"]:
                    if attr[13] >= 8:
                        z = '0'
                    elif 8 > attr[13] >= 5:
                        z = '1'
                    elif 5 > attr[13] >= 3:
                        z = '2'
                    elif 3 > attr[13] >= 1:
                        z = '3'
                    elif attr[13] < 1:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_S = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                        continue
                    except:
                        pass
                if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] <= 0.3:
                    if attr[13] >= 3:
                        z = '0'
                    elif 3 > attr[13] >= 2:
                        z = '1'
                    elif 2 > attr[13] >= 1:
                        z = '2'
                    elif 1 > attr[13] >= 0.5:
                        z = '3'
                    else:
                        z = '5'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_S = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                        continue
                    except:
                        pass
                if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.5 >= attr[
                    25] > 0.3:
                    if attr[13] >= 5:
                        z = '0'
                    elif 5 > attr[13] >= 3:
                        z = '1'
                    elif 3 > attr[13] >= 2:
                        z = '2'
                    elif 2 > attr[13] >= 1:
                        z = '3'
                    elif attr[13] < 1:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_S = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                        continue
                    except:
                        pass
                if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.7 >= attr[
                    25] > 0.5:
                    if attr[13] >= 8:
                        z = '0'
                    elif 8 > attr[13] >= 4:
                        z = '1'
                    elif 4 > attr[13] >= 3:
                        z = '2'
                    elif 3 > attr[13] >= 2:
                        z = '3'
                    elif attr[13] < 2:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_S = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                        continue
                    except:
                        pass
                if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "B":
                    z = '4'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_S = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                        continue
                    except:
                        pass
                if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (
                        attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                             UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_S = ?
                               WHERE untersuchdat_haltung_bewertung.pk = ?;
                               """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        # db.commit()
                        continue
                    except:
                        pass


    def schadens_ueberlagerung(self):
        #Schadensüberlagerung, Schäden an der gleichen Position entfernen, der schwerste schaden wird behalten

        date = self.date + '%'
        db_x = self.db
        crs = self.crs
        haltung = self.haltung

        data = db_x

        entf_list=[]

        db1 = spatialite_connect(data)
        curs = db1.cursor()

        logger.debug(f'Start_Bewertung_Haltungen.liste: {datetime.now()}')
        # nach DWA
        try:
            curs.execute("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Zustandsklasse_ges TEXT ;""")
        except:
            pass

        try:
            curs.execute("""Update
                                    substanz_haltung_bewertung
                                    set
                                    Zustandsklasse_ges =
                                    (Case
                                     When Zustandsklasse_D <= Zustandsklasse_S And Zustandsklasse_D <= Zustandsklasse_B Then Zustandsklasse_D
                                     When Zustandsklasse_S <= Zustandsklasse_D And Zustandsklasse_S <= Zustandsklasse_B Then Zustandsklasse_S
                                     When Zustandsklasse_B <= Zustandsklasse_D And Zustandsklasse_B <= Zustandsklasse_S Then Zustandsklasse_B
                                     Else 'Prüfen!'
                                     END
                                     );""")
            db1.commit()
        except:
            pass

        try:
            curs.execute("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadenslaenge TEXT ;""")
        except:
            pass

        curs.execute("""SELECT s.untersuchhal, (t.station-s.station) as length from substanz_haltung_bewertung AS s INNER JOIN substanz_haltung_bewertung AS t ON s.untersuchhal = t.untersuchhal
                WHERE s.streckenschaden='A' AND t.streckenschaden ='B' AND s.streckenschaden_lfdnr = t.streckenschaden_lfdnr""")
        db1.commit()

        for attr in curs.fetchall:

            sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.untersuchhal = ?"""
            data = (attr[1],attr[0])

            curs.execute(sql, data)

        if haltung == True:
            sql = """
                           SELECT
                               substanz_haltung_bewertung.pk,
                               substanz_haltung_bewertung.untersuchhal,
                               substanz_haltung_bewertung.untersuchrichtung,
                               substanz_haltung_bewertung.schoben,
                               substanz_haltung_bewertung.schunten,
                               substanz_haltung_bewertung.id,
                               substanz_haltung_bewertung.videozaehler,
                               substanz_haltung_bewertung.inspektionslaenge,
                               substanz_haltung_bewertung.station,
                               substanz_haltung_bewertung.timecode,
                               substanz_haltung_bewertung.kuerzel,
                               substanz_haltung_bewertung.charakt1,
                               substanz_haltung_bewertung.charakt2,
                               substanz_haltung_bewertung.quantnr1,
                               substanz_haltung_bewertung.quantnr2,
                               substanz_haltung_bewertung.Schadensart,
                               substanz_haltung_bewertung.Schadensauspraegung,
                               substanz_haltung_bewertung.streckenschaden,
                               substanz_haltung_bewertung.pos_von,
                               substanz_haltung_bewertung.pos_bis,
                               substanz_haltung_bewertung.foto_dateiname,
                               substanz_haltung_bewertung.film_dateiname,
                               substanz_haltung_bewertung.richtung,
                               substanz_haltung_bewertung.bw_bs,
                               substanz_haltung_bewertung.Zustandsklasse_D,
                               substanz_haltung_bewertung.Zustandsklasse_S,
                               substanz_haltung_bewertung.Zustandsklasse_B,
                               substanz_haltung_bewertung.Zustandsklasse_ges,
                               substanz_haltung_bewertung.Schadenslaenge,
                               substanz_haltung_bewertung.createdat,
                               haltungen.haltnam,
                               haltungen.material,
                               haltungen.hoehe,
                               haltungen.createdat
                           FROM substanz_haltung_bewertung, haltungen
                           WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND substanz_haltung_bewertung.createdat like ? 
                           AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS') 
                           AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS' OR substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                       """
            data = (date,)

            curs.execute(sql, data)

            #nur schäden mit OfS und DdS auswählen
            #nur PktS und UmfS auswählem

            # TODO: Sonderregeln für Streckenschäden ergänzen Anlage 8-9

            #streckenschaden überlagern anhand von kg*stg?

            dictionary = {}
            entf_list = []
            for attr in curs.fetchall():

                #schadenslänge ergänzen
                if attr[15] == "PktS":
                    sl = 0.3

                    sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
                    data = (sl, attr[0])

                    curs.execute(sql, data)

                if attr[15] == "UmfS":
                    sl = attr[31]

                    sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
                    data = (sl, attr[0])

                    curs.execute(sql, data)


                if attr[0] in dictionary:
                    continue
                new_list = []
                for x in curs.fetchall():
                    if x[0] == attr[0]:
                        new_list.append(x)
                dictionary[attr[0]] = new_list

            for values in dictionary.values():
                new_items = []
                vergl = []

                for i in values:
                    if i[8] not in new_items:
                        # i[1] ist die Stationierung
                        x = i[8]
                        new_items.append(i[8])
                    else:
                        for i in values:
                            if i[8] == x:
                                vergl.append(i)

                zustand = []
                for i in vergl:
                    # i[3] Zustandsbewertung
                    zustand.append(i[27])

                if len(zustand) > 0:
                    entf = min(zustand)
                    entf_index = zustand.index(entf)

                    # pk von dem element welches entfernt werden soll
                    entf_list.append(vergl[entf_index][0])

        #Datenbank anweisung um die Elemente zu löschen
        for i in entf_list:

            sql = 'DELETE FROM substanz_haltung_bewertung WHERE pk=?'
            data = (i,)
            curs.execute(sql, data)


    def subkans(self):
        #Berechnung der Substanzklassen

        date = self.date + '%'
        db_x = self.db
        crs = self.crs
        haltung = self.haltung

        data = db_x

        db1 = spatialite_connect(data)
        curs = db1.cursor()

        try:
            curs.execute("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Substanzklasse TEXT ;""")
        except:
            pass

        try:
            curs.execute("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadensgewicht TEXT ;""")
        except:
            pass

        if haltung == True:
            sql = """
                                   SELECT
                                       substanz_haltung_bewertung.pk,
                                       substanz_haltung_bewertung.untersuchhal,
                                       substanz_haltung_bewertung.untersuchrichtung,
                                       substanz_haltung_bewertung.schoben,
                                       substanz_haltung_bewertung.schunten,
                                       substanz_haltung_bewertung.id,
                                       substanz_haltung_bewertung.videozaehler,
                                       substanz_haltung_bewertung.inspektionslaenge,
                                       substanz_haltung_bewertung.station,
                                       substanz_haltung_bewertung.timecode,
                                       substanz_haltung_bewertung.kuerzel,
                                       substanz_haltung_bewertung.charakt1,
                                       substanz_haltung_bewertung.charakt2,
                                       substanz_haltung_bewertung.quantnr1,
                                       substanz_haltung_bewertung.quantnr2,
                                       substanz_haltung_bewertung.Schadensart,
                                       substanz_haltung_bewertung.Schadensauspraegung,
                                       substanz_haltung_bewertung.streckenschaden,
                                       substanz_haltung_bewertung.pos_von,
                                       substanz_haltung_bewertung.pos_bis,
                                       substanz_haltung_bewertung.foto_dateiname,
                                       substanz_haltung_bewertung.film_dateiname,
                                       substanz_haltung_bewertung.richtung,
                                       substanz_haltung_bewertung.bw_bs,
                                       substanz_haltung_bewertung.Zustandsklasse_D,
                                       substanz_haltung_bewertung.Zustandsklasse_S,
                                       substanz_haltung_bewertung.Zustandsklasse_B,
                                       substanz_haltung_bewertung.Zustandsklasse_ges,
                                       substanz_haltung_bewertung.Schadenslaenge,
                                       substanz_haltung_bewertung.createdat,
                                       haltungen.haltnam,
                                       haltungen.material,
                                       haltungen.hoehe,
                                       haltungen.createdat
                                   FROM substanz_haltung_bewertung, haltungen
                                   WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND substanz_haltung_bewertung.createdat like ? 
                                   AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS') 
                                   AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS' OR substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                               """
            data = (date,)

            curs.execute(sql, data)

        for attr in curs.fetchall():

            sl = attr[28]


            #Klassengewichte
            if attr[27] == 0:
                kg = 1.0
            if attr[27] == 1:
                kg = 0.8
            if attr[27] == 2:
                kg = 0.25
            if attr[27] == 3:
                kg = 0.15
            if attr[27] == 4:
                kg = 0.05
            if attr[27] == 5:
                kg =0

            #startgewicht:
            if attr[15] == 'PktS' and attr[16] in [ 'OfS','DdS', 'SoB']:
                stg = 8

            if attr[15] == 'UmfS' and attr[16] in ['OfS', 'DdS', 'SoB']:
                stg = 3

            if attr[15] == 'StrS' and attr[16] in ['OfS', 'DdS', 'SoB']:
                stg = 1

            # schadensgewicht:
            sg = sl * stg * kg

            #schadensgewicht für streckenschäden seperat ermitteln
            if attr[15] == 'StrS':
                if sg < (8*kg*0.3):
                    stg_neu = (8*kg*0.3)/sg
                    sg = sl * stg_neu * kg
                else:
                    continue

            #sg in tabelle schreiben
            sql = """UPDATE substanz_haltung_bewertung SET Schadensgewicht = ? WHERE substanz_haltung_bewertung.pk = ?"""
            data = (sg, attr[0])

            curs.execute(sql, data)


        sql = """CREATE TABLE IF NOT EXISTS haltungen_substanz_bewertung AS 
                        SELECT pk, 
                        haltnam, 
                        schoben,
                        schunten,
                        hoehe,
                        breite,
                        laenge,
                        baujahr,
                        untersuchtag,
                        untersucher,
                        wetter,
                        bewertungsart,
                        bewertungstag,
                        strasse,
                        datenart,
                        objektklasse_dichtheit,
                        objektklasse_standsicherheit,
                        objektklasse_betriebssicherheit,
                        objektklasse_gesamt,
                        kommentar,
                        cratedat,
                        FROM haltungen_untersucht_bewertung"""
        curs.execute(sql)

        db = spatialite_connect(db_x)
        curs = db.cursor()


        # #Bruttoschadenslänge BSL und Abnutzung ABN
        #
        # bsl= summe von allen sg
        sql = """SELECT
                   pk,
                   untersuchhal,
                   SUM(Schadensgewicht),
                   laenge,
                FROM substanz_haltung_bewertung
                GROUP BY untersuchhal;"""

        data = (date,)

        curs.execute(sql, data)

        for attr in curs.fetchall():
            # abn = bsl/länge*100
            abn=attr[2]/attr[3]*100

            # #substanzklasse
            sub_ges = 100-abn

            if sub_ges >= 95:
                sbk = 5
            if 95>sub_ges>=85:
                sbk = 4
            if 85>sub_ges>=67:
                sbk = 3
            if 67>sub_ges>=33:
                sbk = 2
            if 33>sub_ges>5:
                sbk = 1
            if 5>=sub_ges:
                sbk = 0

            # sg in tabelle schreiben
            sql = """UPDATE haltungen_substanz_bewertung SET Substanzklasse = ? WHERE haltungen_substanz_bewertung.haltnam = ?"""
            data = (sbk, attr[1])

            curs.execute(sql, data)
