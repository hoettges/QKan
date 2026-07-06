__author__ = "Joerg Hoettges"
__date__ = "Mai 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

from typing import List

from qgis import processing
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis

from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import fehlermeldung
from qkan.utils import get_logger

logger = get_logger("QKan.surfaceTools.surface_tools")


class SurfaceTask:
    def __init__(
        self, iface, database_qkan: str, epsg: int, dbtyp: str = "SpatiaLite"
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
            "Haltungsflächen werden an die angeschlossenen Haltungen angepasst. Bitte warten...",
        )
        status_message.layout().addWidget(progress_bar)
        self.iface.messageBar().pushWidget(status_message, Qgis.MessageLevel.Info, 10)
        # progress_bar.reset()
        progress_bar.setValue(0)

        # Anzahl betroffene Teilgebieteabfragen
        if len(liste_teilgebiete) == 0:
            auswahl_tg = ""  # keine Einschränkung auf Teilgebiete
        else:
            auswahl_tg = " WHERE teilgebiete.tgnam in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

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

        with DBConnection(dbname=self.database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error_user(
                    "Fehler in surface_tools:\n"
                    "QKan-Datenbank {} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                        self.database_qkan
                    ),
                )

            sql = f"""
                WITH haltungen_selected AS (SELECT ROWID, pk, geom, haltnam, schoben, schunten 
                    FROM haltungen
                    WHERE rwanschluss = 1
                      AND (haltungstyp = 'Haltung' OR haltungstyp IS NULL){auswahl_hal}
                ),
                fls AS (
                    SELECT ROWID, pk, geom, haltnam, schoben, schunten,
                        MakePolygon(AddPoint(AddPoint(AddPoint(
                            MakeLine(pointn(geom,1),
                                makepoint(x(centroid(geom))-(y(pointn(geom,-1))-y(pointn(geom,1)))*0.01,
                                    y(centroid(geom))+(x(pointn(geom,-1))-x(pointn(geom,1)))*0.01)),
                            pointn(geom,-1)),
                        makepoint(x(centroid(geom))+(y(pointn(geom,-1))-y(pointn(geom,1)))*0.01,
                            y(centroid(geom))-(x(pointn(geom,-1))-x(pointn(geom,1)))*0.01)),pointn(geom,1))
                        ) AS geof
                    FROM
                        haltungen_selected 
                )
                SELECT n1.pk AS objid,
                printf('Haltung "%s" und "%s" kreuzen sich. Bei einer von beiden muss der Status RW-Anschlüsse deaktiviert werden!', 
                    n1.haltnam, n2.haltnam) AS bemerkung
                FROM fls AS n1 JOIN fls AS n2 ON ST_Intersects(n1.geof, n2.geof) = 1
                WHERE 
                    n1.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name='haltungen' AND search_frame=n2.geof) 
                  AND n1.pk <> n2.pk
                  AND n1.schoben not in (n2.schunten, n2.schoben)
                  AND n2.schoben not in (n1.schunten, n1.schoben)
                  AND n1.schunten not in (n2.schunten, n2.schoben)
                  AND n2.schunten not in (n1.schunten, n1.schoben)"""

            if not db_qkan.sql(sql, mute_logger=True):
                return False

            data = db_qkan.fetchall()
            if len(data) > 0:
                logger.warning('Es wurden kreuzende oder zu nah beieinander liegende Haltungen gefunden\n'
                               'Bitte prüfen Sie diese mit der Plausibilitätsprüfung "Kreuzende Haltungen (im Plan)"')
                return False

            # Entfernen der gegebenenfalls schon vorhandenen temporären Tabellen 't_voronoihal' und 't_voronoi'
            sql = "PRAGMA table_list(t_voronoihal)"
            if not db_qkan.sql(sql, "Prüfen, ob die Tabelle 't_voronoihal' vorhanden ist"):
                return False  # Abbruch weil Anfrage fehlgeschlagen
            if db_qkan.fetchone() is not None:
                sql = "SELECT DiscardGeometryColumn('t_voronoihal', 'geom')"
                if not db_qkan.sql(sql, 'Entfernen geom in t_voronoihal'):
                    return False
                sql = "DROP TABLE t_voronoihal"
                if not db_qkan.sql(sql, 'Entfernen der Tabelle "t_voronoihal"'):
                    return False
                db_qkan.commit()

            sql = "PRAGMA table_list(t_voronoi)"
            if not db_qkan.sql(sql, "Prüfen, ob die Tabelle 't_voronoi' vorhanden ist"):
                return False  # Abbruch weil Anfrage fehlgeschlagen
            if db_qkan.fetchone() is not None:
                sql = "SELECT DiscardGeometryColumn('t_voronoi', 'geom')"
                if not db_qkan.sql(sql, 'Entfernen geom in t_voronoi'):
                    return False
                sql = "DROP TABLE t_voronoi"
                if not db_qkan.sql(sql, 'Entfernen der Tabelle "t_voronoi"'):
                    return False
                db_qkan.commit()

            # Feststellen der Ausdehnung für die Thiessen-Polygone, je 50% größer als ausgewählte Teilgebiete
            sql = f"""
                WITH flrange AS (
                    SELECT Extent(geom) AS geom 
                    FROM teilgebiete{auswahl_tg}
                ), e as (
                    SELECT 
                      MbrMinX(geom) AS xmi1,
                      MbrMaxX(geom) AS xma1,
                      MbrMinY(geom) AS ymi1,
                      MbrMaxY(geom) AS yma1
                    FROM flrange
                )
                SELECT
                    xmi1 * 1.5 - xma1 * 0.5 AS xmin,
                    xma1 * 1.5 - xmi1 * 0.5 AS xmax,
                    ymi1 * 1.5 - yma1 * 0.5 AS ymin,
                    yma1 * 1.5 - ymi1 * 0.5 AS ymax
                FROM e
                """

            if not db_qkan.sql(sql, mute_logger=True):
                return False

            data = db_qkan.fetchall()
            xmin, xmax, ymin, ymax = data[0]

        del db_qkan

        # Haltungslinien in schlanke Polygone umwandeln, da voronoi.skeleton nur Polygone verarbeitet

        logger.debug('Haltungsobjekte erzeugen')

        processing.run(
            "native:geometrybyexpression",
            {
                'INPUT': f'spatialite://dbname=\'{self.database_qkan}\' table="haltungen" (geom) '
                         f'sql=(haltungstyp IS NULL or haltungstyp = \'Haltung\') and rwanschluss = 1 and '
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
                'OUTPUT': f'spatialite://dbname=\'{self.database_qkan}\' table="t_voronoihal" (geom)'
            }
        )
        # layer=p_line2poly['OUTPUT']
        # QgsProject.instance().addMapLayer(layer)

        progress_bar.setValue(20)

        logger.debug('Thiessen-Polygone erzeugen')

        # Thiessen-Polygone erzeugen
        try:
            p_voronoi = processing.run(
                "grass7:v.voronoi.skeleton",
                {'input': f'spatialite://dbname=\'{self.database_qkan}\' table="t_voronoihal" (geom)',
                 'smoothness': 0.01,
                 'thin': -1,
                 '-a': True,
                 '-s': False,
                 '-l': False,
                 '-t': False,
                 'output':'TEMPORARY_OUTPUT',
                 'GRASS_REGION_PARAMETER': f'{xmin},{xmax},{ymin},{ymax} [EPSG:{self.epsg}]',
                 'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
                 'GRASS_MIN_AREA_PARAMETER': 0.0001,
                 'GRASS_OUTPUT_TYPE_PARAMETER': 0,
                 'GRASS_VECTOR_DSCO': '',
                 'GRASS_VECTOR_LCO': '',
                 'GRASS_VECTOR_EXPORT_NOCAT': False
                 }
            )
        except BaseException as err:
            logger.warning(
                f"Bei der Erstellung der Thiessen-Polygone ist folgender Fehler aufgetreten:\n {err}\n"
            )
                # "Möglicherweise ist die GRASS-Toolbox nicht verfügbar.\nIn diesem Fall aktivieren Sie"
                # " bitte die Erweiterung 'GRASS GIS provider' und starten Sie QGIS neu...")
            return False
        # layer = QgsVectorLayer(p_voronoi['output'], "skeleton", "ogr")
        # QgsProject.instance().addMapLayer(layer)

        progress_bar.setValue(50)

        logger.debug('Thiessen-Polygone in Spatialite-DB speichern')

        # Speichern der Thiessen-Polygone in der Spatialite-DB
        # Interessant: processing.run("qgis:importintospatialite"...) verursacht einen Datenbankzugriffsfehler.
        # Deshalb nachfolgender Workaraound
        processing.run("native:extractbyattribute",
                       {
                           'INPUT': p_voronoi['output'],
                           'FIELD': 'pk',
                           'OPERATOR': 9,
                           'VALUE': '',
                           'OUTPUT': f'spatialite://dbname=\'{self.database_qkan}\' table="t_voronoi" (geom)'})

        progress_bar.setValue(70)

        with DBConnection(dbname=self.database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error_user(
                    "Fehler in surface_tools:\n"
                    "QKan-Datenbank {} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                        self.database_qkan
                    ),
                )

            # Einfügen verschnittener Haltungsflächen (basierend auf Selektionstabelle tezgsel)
            sql = f"""
                WITH covered AS (
                    SELECT 
                    flnam, min(neigkl) AS neigkl, min(neigung) AS neigung,
                    regenschreiber,
                    teilgebiet, abflussparameter, 'automatisch erstellt' AS kommentar, CURRENT_DATE AS createdat,
                    CastToMultiPolygon(ST_Union(geom)) AS geom
                    FROM tezg
                ),
                tg AS (SELECT CastToMultiPolygon(ST_Union(geom)) AS geom FROM teilgebiete{auswahl_tg}
                ),
                fl AS (
                SELECT
                    printf('hf_%1', v.haltnam) AS flnam,
                    CASE WHEN co.geom IS NULL
                    THEN CastToMultiPolygon(ST_Intersection(v.geom, tg.geom))
                    ELSE CastToMultiPolygon(ST_Difference(ST_Intersection(v.geom, tg.geom), co.geom))
                    END AS geom
                    FROM t_voronoi AS v,
                    covered AS co,
                    tg
                )
                INSERT INTO tezg (
                    flnam,
                    neigkl, neigung,
                    regenschreiber,
                    teilgebiet, abflussparameter, kommentar, createdat,
                    geom
                )
                SELECT 
                    c.flnam,
                    c.neigkl,
                    c.neigung,
                    c.regenschreiber,
                    c.teilgebiet,
                    c.abflussparameter,
                    c.kommentar,
                    c.createdat,
                    f.geom
                FROM
                    covered AS c,
                    fl AS f
                WHERE f.geom IS NOT NULL
                """
            if not db_qkan.sql(sql, stmt_category="Voronoi_4"):
                return False

            db_qkan.commit()

        del db_qkan

        progress_bar.setValue(100)
        status_message.setText("Fertig!")
        status_message.setLevel(Qgis.MessageLevel.Success)
