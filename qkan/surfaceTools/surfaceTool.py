# -*- coding: utf-8 -*-

__author__ = "Joerg Hoettges"
__date__ = "Mai 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

import logging
from typing import Any, List

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

logger = logging.getLogger("QKan.surfaceTools.surface_tools")


class SurfaceTool:
    def __init__(
        self, database_qkan: str, epsg: int = 25832, dbtyp: str = "SpatiaLite"
    ):
        self.epsg = epsg
        self.dbtyp = dbtyp
        # self.sqlobject = Path(sqlfile)
        """not sure if this is correct or needed"""
        self.database_QKan = database_qkan

        self.dbQK = DBConnection(
            dbname=database_qkan, epsg=epsg
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben

        self.connected = self.dbQK.connected

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in surface_tools:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )

    def create_table(self) -> bool:
        sql = f"""
            CREATE TEMPORARY TABLE IF NOT EXISTS temp_flaechencut (
                pk INTEGER PRIMARY KEY,
                geom MULTIPOLYGON)
            """

        if not self.dbQK.sql(sql, mute_logger=True):
            del self.dbQK
            return False

        self.dbQK.commit()
        return True

    def processing(self, schneiden: str, geschnitten: str) -> bool:
        sql = f"""
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
            """
        if not self.dbQK.sql(sql, mute_logger=True):
            del self.dbQK
            return False

        self.dbQK.commit()
        return True

    def update(self) -> bool:
        sql = f"""
            UPDATE flaechen SET geom = (
                SELECT geom
                FROM temp_flaechencut
                WHERE flaechen.pk = temp_flaechencut.pk)
                WHERE flaechen.pk IN (SELECT pk FROM temp_flaechencut)
            """
        if not self.dbQK.sql(sql, mute_logger=True):
            del self.dbQK
            return False

        self.dbQK.commit()
        return True


class AccessAttr:
    def __init__(
        self, database_qkan: str, epsg: int = 25832, dbtyp: str = "SpatiaLite"
    ):
        self.epsg = epsg
        self.dbtyp = dbtyp
        self.database_QKan = database_qkan

        self.dbQK = DBConnection(
            dbname=database_qkan, epsg=epsg
        )  # Datenbankobjekt der QKan-Datenbank zum Schreiben

        self.connected = self.dbQK.connected

        if not self.dbQK.connected:
            fehlermeldung(
                "Fehler in surface_tools:\n",
                "QKan-Datenbank {} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )

    def accessAttribute(self) -> List[Any]:
        if not self.dbQK.sql("SELECT abflussparameter FROM flaechen", mute_logger=True):
            del self.dbQK
            return []

        return self.dbQK.fetchall()


def FlaechenVerarbeitung(database_qkan: str, schneiden: str, geschnitten: str) -> bool:
    overlap = SurfaceTool(database_qkan, epsg=25832, dbtyp="SpatiaLite")

    if not overlap.connected:
        return False

    overlap.create_table()
    overlap.processing(schneiden, geschnitten)
    overlap.update()

    del overlap

    return True
