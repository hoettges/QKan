# -*- coding: utf-8 -*-


import logging
from typing import List
import os
from qgis.core import Qgis, QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import iface, spatialite_connect

from qkan import QKan, enums
from qkan.config import ToolsConfig
from qkan.database.dbfunc import DBConnection


logger = logging.getLogger("QKan.tools.k_filepath")


def setfilepath(
    db,
    videopath,
    fotopath,
    fotopath_2,
    ausw_haltung,
    ausw_schacht,
) -> None:
    """Schreibt die Dateipfade in die Datenbank.
    """

    db = spatialite_connect(db)
    curs = db.cursor()

    if ausw_haltung == True:
        bild=''
        if fotopath != "":
            #Bild suchen
            # ordner und dateiname aus datenbank abfragen

            sql = """select pk, foto_dateiname, ordner_bild 
                        from untersuchdat_haltung"""
            try:
                curs.execute(sql)
            except BaseException as err:
                return False


            for attr in curs.fetchall():

                bild_nam = attr[1]

                for root, dirs, files in os.walk(fotopath):
                    for file in files:
                        if file == bild_nam:
                            bild = root

                            # pfad in db erstzen
                            sql = """Update untersuchdat_haltung set ordner_bild = ?
                                                WHERE untersuchdat_haltung.pk = ?;"""
                            data = (str(bild), attr[0])

                            try:
                                curs.execute(sql, data)
                            except BaseException as err:
                                return False

        if videopath != "":
            video=''

            #Video suchen
            sql = """select pk, film_dateiname, ordner_video
                                from untersuchdat_haltung"""
            try:
                #curs.sql(sql)
                curs.execute(sql)
            except BaseException as err:
                return False

            for attr in curs.fetchall():
                video_nam = attr[1]

                for root, dirs, files in os.walk(videopath):
                    for file in files:
                        if file == video_nam:
                            video = root

                            # ordner_video in db ersetzen
                            sql = """Update untersuchdat_haltung set ordner_video = ?
                                                    WHERE untersuchdat_haltung.pk = ?;"""
                            data = (video, attr[0])

                            try:
                                curs.execute(sql, data)
                            except BaseException as err:
                                return False


    if ausw_schacht == True and fotopath_2 != "":
        bild = ''

        #ordner und dateiname aus datenbank abfragen
        sql = """select pk, foto_dateiname, ordner 
                    from untersuchdat_schacht"""
        try:
            #curs.sql(sql)
            curs.execute(sql)
        except BaseException as err:
            return False


        for attr in curs.fetchall():
            bild_nam = attr[1]

            for root, dirs, files in os.walk(fotopath_2):
                for file in files:
                    if file == bild_nam:
                        bild = root

                        # pfad in db erstzen
                        sql = """Update untersuchdat_schacht set ordner = ?
                                            WHERE untersuchdat_schacht.pk = ?;"""
                        data = (bild, attr[0])

                        try:
                            curs.execute(sql, data)
                        except BaseException as err:
                            return False


    db.commit()
