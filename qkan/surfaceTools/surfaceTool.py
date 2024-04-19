__author__ = "Joerg Hoettges"
__date__ = "Mai 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

from typing import List

from qgis import processing
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.utils import get_logger

logger = get_logger("QKan.surfaceTools.surface_tools")


class SurfaceTask:
    def __init__(
        self, iface, database_qkan: str, epsg: int = 25832, dbtyp: str = "SpatiaLite"
    ):
        self.iface = iface
        self.database_qkan = database_qkan
        self.epsg = epsg
        self.dbtyp = dbtyp

        if not self.database_qkan:
            fehlermeldung("Fehler: Für diese Funktion muss ein Projekt geladen sein!")
            return

        return

    def create_table(self, db_qkan) -> bool:
        sql = """
            CREATE TEMPORARY TABLE IF NOT EXISTS temp_flaechencut (
                pk INTEGER PRIMARY KEY,
                geom MULTIPOLYGON)
            """

        if not db_qkan.sql(sql, mute_logger=True):
            return False

        db_qkan.commit()
        return True

    def cut_overlap(self, db_qkan: DBConnection, schneiden: str, geschnitten: str) -> bool:
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

        if not db_qkan.sql(sql, mute_logger=True):
            return False

        db_qkan.commit()
        return True

    def update(self, db_qkan: DBConnection) -> bool:
        sql = """
            UPDATE flaechen SET geom = (
                SELECT geom
                FROM temp_flaechencut
                WHERE flaechen.pk = temp_flaechencut.pk)
                WHERE flaechen.pk IN (SELECT pk FROM temp_flaechencut)
            """

        if not db_qkan.sql(sql, mute_logger=True):
            return False

        db_qkan.commit()

        return True

    def run_cut(self, schneiden: str, geschnitten: str) -> bool:
        with DBConnection(dbname=self.database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in surfaceTool.SurfaceTask.run_cut:\n"
                    "QKan-Datenbank %s wurde nicht gefunden oder war nicht aktuell!\nAbbruch!", self.database_qkan
                )
                return False

            self.create_table(db_qkan)
            self.cut_overlap(db_qkan, schneiden, geschnitten)
            self.update(db_qkan)

        return True

    def run_voronoi(self, liste_hal_entw: List[str], liste_teilgebiete: List[str]) -> bool:
        """Erstellt Voronoi-Gebiete zu ausgewählten Haltungen"""

        progress_bar = QProgressBar(self.iface.messageBar())
        progress_bar.setRange(0, 100)
        status_message = self.iface.messageBar().createMessage(
            "",
            "Haltungsflächen werden verschnitten. Bitte warten...",
        )
        status_message.layout().addWidget(progress_bar)
        self.iface.messageBar().pushWidget(status_message, Qgis.Info, 10)
        # progress_bar.reset()
        progress_bar.setValue(0)

        with DBConnection(dbname=self.database_qkan) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung(
                    "Fehler in surface_tools:\n",
                    "QKan-Datenbank {} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                        self.database_qkan
                    ),
                )

            # Anzahl betroffene Flächen abfragen
            if len(liste_teilgebiete) == 0:
                auswahl_fl = ""                        # keine Einschränkung auf Teilgebiete
            else:
                auswahl_fl = " and flaechen.teilgebiet in ('{}')".format(
                    "', '".join(liste_teilgebiete)
                )

            sql = f"""
                WITH flrange AS (
                    SELECT Extent(geom) AS geom 
                    FROM flaechen 
                    WHERE aufteilen and geom IS NOT NULL{auswahl_fl}
                )
                SELECT 
                  MbrMinX(geom) AS xmin,
                  MbrMaxX(geom) AS xmax,
                  MbrMinY(geom) AS ymin,
                  MbrMaxY(geom) AS ymax
                FROM flrange"""

            if not db_qkan.sql(sql, mute_logger=True):
                return False

            data = db_qkan.fetchall()
            xmin, xmax, ymin, ymax = data[0]

            # Haltungslinien in schlanke Polygone umwandeln, da voronoi.skeleton nur Polygone verarbeitet

            # Zu berücksichtigende Haltungen zählen
            if len(liste_hal_entw) == 0:
                auswahl_hal = ""
            else:
                auswahl_hal = " and haltungen.entwart in ('{}')".format(
                    "', '".join(liste_hal_entw)
                )

            if len(liste_teilgebiete) != 0:
                auswahl_hal += " and haltungen.teilgebiet in ('{}')".format(
                    "', '".join(liste_teilgebiete)
                )

            p_line2poly = processing.run(
                "native:geometrybyexpression",
                {
                    'INPUT': f'spatialite://dbname=\'{self.database_qkan}\' table="haltungen" (geom) '
                             f'sql=(haltungstyp IS NULL or haltungstyp = \'Haltung\') and '
                             f'geom IS NOT NULL{auswahl_hal}',
                    'OUTPUT_GEOMETRY': 0,
                    'WITH_Z': False,
                    'WITH_M': False,
                    'EXPRESSION': '''make_polygon(
                        make_line(
                            start_point($geometry),
                            make_point(
                                x(centroid($geometry))-(y(end_point($geometry))-y(start_point($geometry)))*0.01,
                                y(centroid($geometry))+(x(end_point($geometry))-x(start_point($geometry)))*0.01
                            ),
                            end_point($geometry),
                            make_point(
                                x(centroid($geometry))+(y(end_point($geometry))-y(start_point($geometry)))*0.01,
                                y(centroid($geometry))-(x(end_point($geometry))-x(start_point($geometry)))*0.01
                            )
                        )
                    )''',
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
            )
            # layer=p_line2poly['OUTPUT']
            # QgsProject.instance().addMapLayer(layer)

            progress_bar.setValue(20)

            # Voronoi-Gebiete erzeugen
            p_voronoi = processing.run(
                "grass7:v.voronoi.skeleton",
                {'input': p_line2poly['OUTPUT'],
                 'smoothness': 0.01,
                 'thin': -1,
                 '-a': True,
                 '-s': False,
                 '-l': False,
                 '-t': False,
                 'output': 'TEMPORARY_OUTPUT',
                 'GRASS_REGION_PARAMETER': f'{xmin},{xmax},{ymin},{ymax} [EPSG:{self.epsg}]',
                 'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
                 'GRASS_MIN_AREA_PARAMETER': 0.0001,
                 'GRASS_OUTPUT_TYPE_PARAMETER': 0,
                 'GRASS_VECTOR_DSCO': '',
                 'GRASS_VECTOR_LCO': '',
                 'GRASS_VECTOR_EXPORT_NOCAT': False
                 }
            )
            # layer = QgsVectorLayer(p_voronoi['output'], "skeleton", "ogr")
            # QgsProject.instance().addMapLayer(layer)

            progress_bar.setValue(50)

            # Speichern der Voronoi-Gebiete in der Spatialite-DB
            p_savedb = processing.run(
                "qgis:importintospatialite",
                {'INPUT': p_voronoi['output'],
                 'DATABASE': self.database_qkan,
                 'TABLENAME': 'voronoi',
                 'PRIMARY_KEY': '',
                 'GEOMETRY_COLUMN': 'geom',
                 'ENCODING': 'UTF-8',
                 'OVERWRITE': True,
                 'CREATEINDEX': True,
                 'LOWERCASE_NAMES': True,
                 'DROP_STRING_LENGTH': True,
                 'FORCE_SINGLEPART': False
                 }
            )

            progress_bar.setValue(70)

            # Erstellen einer temporären Tabelle zur Selektion aller Haltungsflächen, in denen
            # aufzuteilende Flächen liegen
            sql = """CREATE TEMP TABLE IF NOT EXISTS tezgsel (pk INTEGER PRIMARY KEY)"""
            if not db_qkan.sql(sql, stmt_category="Voronoi_1"):
                return False

            db_qkan.commit()

            progress_bar.setValue(80)

            # sql = """DELETE FROM tezg WHERE pk IN (SELECT pk FROM tezgsel)"""
            # if not db_qkan.sql(sql, stmt_category="Voronoi_2"):
            #     return False
            #
            # db_qkan.commit()
            #
            # progress_bar.setValue(85)
            #

            sql = f"""INSERT INTO tezgsel (pk)
                        SELECT t.pk
                        FROM tezg AS t
                        INNER JOIN (
                            SELECT ST_Buffer(geom, -0.05) AS geom 
                            FROM flaechen 
                            WHERE aufteilen and geom IS NOT NULL{auswahl_fl}
                        ) AS f
                        ON ST_Intersects(t.geom, f.geom)
                        WHERE t.geom IS NOT NULL
                        GROUP BY t.pk"""
            if not db_qkan.sql(sql, stmt_category="Voronoi_3"):
                return False

            db_qkan.commit()

            progress_bar.setValue(90)

            # Einfügen verschnittener Haltungsflächen (basierend auf Selektionstabelle tezgsel)
            sql = """INSERT INTO tezg (
                            flnam,
                            haltnam, schnam, neigkl, neigung,
                            befgrad, schwerpunktlaufzeit, regenschreiber,
                            teilgebiet, abflussparameter, kommentar, createdat,
                            geom)
                        SELECT
                            substr(t.flnam ||'-' || CAST(v.pk AS TEXT), 1, 30) AS flnam,
                            t.haltnam, t.schnam, t.neigkl, t.neigung,
                            t.befgrad, t.schwerpunktlaufzeit, t.regenschreiber,
                            t.teilgebiet, t.abflussparameter, t.kommentar, t.createdat,
                            ST_Intersection(t.geom, v.geom) AS geom
                        FROM tezg AS t
                        INNER JOIN tezgsel AS s  ON t.pk=s.pk
                        INNER JOIN voronoi AS v ON ST_Intersects(t.geom, v.geom)=1
                        WHERE  t.geom IS NOT NULL"""
            if not db_qkan.sql(sql, stmt_category="Voronoi_4"):
                return False

            db_qkan.commit()

            progress_bar.setValue(95)

            # Löschen der ursprünglichen Haltungsflächen basierend auf Selektionstabelle tezgsel
            sql = """DELETE FROM tezg WHERE pk IN (SELECT pk FROM tezgsel)"""
            if not db_qkan.sql(sql, stmt_category="Voronoi_5"):
                return False

            db_qkan.commit()

            progress_bar.setValue(100)
            status_message.setText("Fertig!")
            status_message.setLevel(Qgis.Success)
