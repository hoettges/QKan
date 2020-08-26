# -*- coding: utf-8 -*-

__author__ = "Joerg Hoettges"
__date__ = "Mai 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

import os
from pathlib import Path
from qkan.database.dbfunc import DBConnection
from qgis.utils import pluginDirectory
import xml.etree.ElementTree as ET
from qgis.core import QgsCoordinateReferenceSystem
from qkan.database.qkan_utils import fehlermeldung


import logging

logger = logging.getLogger("QKan.surfaceTools.surface_tools")


class SurfaceTool:
    def __init__(self, database_QKan, epsg=25832, dbtyp="SpatiaLite"):
        self.epsg = epsg
        self.dbtyp = dbtyp
        # self.sqlobject = Path(sqlfile)
        '''not sure if this is correct or needed'''
        self.database_QKan = database_QKan

        self.dbQK = DBConnection(
            dbname=database_QKan, epsg=epsg
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben

        self.connected = self.dbQK.connected

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in surface_tools:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )

    def create_table(self):
        sql = f'''
            CREATE TEMPORARY TABLE IF NOT EXISTS temp_flaechencut (
                pk INTEGER PRIMARY KEY,
                geom MULTIPOLYGON)
            '''

        if not self.dbQK.sql(sql, repeatmessage=True):
            del self.dbQK
            return False

        self.dbQK.commit()
        return True

    def processing(self, schneiden, geschnitten):
        sql = f'''
            WITH fl_cut AS (
                SELECT pk, geom AS geom FROM flaechen
                WHERE abflussparameter = '{geschnitten}'), 
            fl_over AS (
                SELECT pk, geom AS geom FROM flaechen
                WHERE abflussparameter = '{schneiden}'),
            fl_isect AS (
                SELECT 
                fl_cut.pk, fl_cut.geom AS geom_cut, fl_over.geom AS geom_over
                FROM fl_cut
                INNER JOIN fl_over
                ON Intersects(fl_cut.geom, fl_over.geom) = 1 AND 
                    CastToMultiPolygon(Difference(fl_cut.geom, fl_over.geom)) IS NOT NULL
                WHERE fl_cut.pk IN (
                    SELECT ROWID
                    FROM SpatialIndex
                    WHERE f_table_name = 'flaechen'
                        AND search_frame = fl_over.geom))
            INSERT INTO temp_flaechencut (pk, geom)
            SELECT 
            pk, CastToMultiPolygon(Difference(geom_cut, GUnion(geom_over))) AS geom
            FROM fl_isect
            GROUP BY pk
            '''
        if not self.dbQK.sql(sql, repeatmessage=True):
            del self.dbQK
            return False

        self.dbQK.commit()
        return True

    def update(self):
        sql = f'''
            UPDATE flaechen SET geom = (
                SELECT geom
                FROM temp_flaechencut
                WHERE flaechen.pk = temp_flaechencut.pk)
                WHERE flaechen.pk IN (SELECT pk FROM temp_flaechencut)
            '''
        if not self.dbQK.sql(sql, repeatmessage=True):
            del self.dbQK
            return False

        self.dbQK.commit()
        return True


class accessAttr:
    def __init__(self, database_QKan, epsg=25832, dbtyp="SpatiaLite"):
        self.epsg = epsg
        self.dbtyp = dbtyp
        self.database_QKan = database_QKan

        self.dbQK = DBConnection(
            dbname=database_QKan, epsg=epsg
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben

        self.connected = self.dbQK.connected

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in surface_tools:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )

    def accessAttribute(self):
        sql = f'''
                    SELECT abflussparameter FROM flaechen 
                    '''
        if not self.dbQK.sql(sql, repeatmessage=True):
            del self.dbQK
            return False

        newList = self.dbQK.fetchall()
        return newList


def FlaechenVerarbeitung(database_QKan: str, schneiden, geschnitten):
    overlap = SurfaceTool(
        database_QKan,
        epsg=25832,
        dbtyp="SpatiaLite"
    )

    if not overlap.connected:
        return False

    overlap.create_table()
    overlap.processing(schneiden, geschnitten)
    overlap.update()

    del overlap

    return True
