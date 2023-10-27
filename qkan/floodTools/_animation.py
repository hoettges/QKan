import logging
from datetime import datetime
import os.path
import shutil
import xml.etree.ElementTree as ET

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import (
    Qgis, QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsVectorFileWriter,
    QgsCoordinateTransformContext, QgsInterval, QgsTemporalUtils, QgsRasterLayer, QgsLayerTreeLayer
)
from .flood_db import FloodDB
from qkan import QKan

logger = logging.getLogger("QKan.floodTools._animation")

class FloodanimationTask:
    def __init__(self):
        # all parameters are passed via QKan.config
        self.epsg = QKan.config.epsg
        self.import_dir = QKan.config.flood.import_dir
        self.projectfile = QKan.config.project.file
        self.db_name = QKan.config.flood.database
        self.velo_choice = QKan.config.flood.velo
        self.wlevel_choice = QKan.config.flood.wlevel
        self.gdblayer_choice = QKan.config.flood.gdblayer
        self.faktor_v = float(QKan.config.flood.faktor_v)
        self.min_v = float(QKan.config.flood.min_v)
        self.min_w = float(QKan.config.flood.min_w)

    def run(self) -> bool:

        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Flood-Animation wird erstellt. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

        datenbank_qkan_template = os.path.join(QKan.template_dir, "qkan.sqlite")
        shutil.copyfile(datenbank_qkan_template, self.db_name)

        # Read simulation parameters
        xml_file = os.path.join(self.import_dir, '..', 'report_info.xml')
        xml = ET.ElementTree()
        xml.parse(xml_file)
        starttime = datetime.strptime(xml.findtext("ReportStart"), '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        interval = float(xml.findtext("ReportInterval")) / 86400.

        if self.velo_choice:
            # Make sure that path includes 'Result2D.gdb'
            if 'Result2D.gdb' not in self.import_dir:
                result_dir = os.path.join(self.import_dir, 'Result2D.gdb|layername=Velocity')
            else:
                result_dir = self.import_dir.replace('Result2D.gdb', 'Result2D.gdb|layername=Velocity')
            logger.debug(f'floodTools._animation.run.velo: {result_dir=}')

            vlayer = QgsVectorLayer(
                result_dir,
                "result2d__velocity",
                "ogr"
            )
            vlayer.setCrs(QgsCoordinateReferenceSystem(self.epsg))
            QgsProject.instance().addMapLayer(vlayer)

            o_save_options = QgsVectorFileWriter.SaveVectorOptions()
            o_save_options.layerName = 'result2d__velocity'
            o_save_options.driverName = 'SQLite'
            o_save_options.fileEncoding = 'utf-8'
            o_save_options.onlySelectedFeatures = False
            # o_save_options.layerOptions = ['SPATIALITE=YES']
            o_save_options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
            erg = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer=vlayer,
                fileName=self.db_name,
                transformContext=QgsCoordinateTransformContext(),
                options=o_save_options
            )

            if not self.gdblayer_choice:
                QgsProject.instance().removeMapLayer(vlayer.id())

        if self.wlevel_choice:
            # Make sure that path includes 'Result2D.gdb'
            if 'Result2D.gdb' not in self.import_dir:
                result_dir = os.path.join(self.import_dir, 'Result2D.gdb|layername=Topo_Decimated')
            else:
                result_dir = self.import_dir.replace('Result2D.gdb', 'Result2D.gdb|layername=Topo_Decimated')
            logger.debug(f'floodTools._animation.run.wlevel: {result_dir=}')

            vlayer = QgsVectorLayer(
                result_dir,
                "result2d__topo_decimated",
                "ogr"
            )
            vlayer.setCrs(QgsCoordinateReferenceSystem(self.epsg))
            QgsProject.instance().addMapLayer(vlayer)

            o_save_options = QgsVectorFileWriter.SaveVectorOptions()
            o_save_options.layerName = 'result2d__topo_decimated'
            o_save_options.driverName = 'SQLite'
            o_save_options.fileEncoding = 'utf-8'
            o_save_options.onlySelectedFeatures = False
            # o_save_options.layerOptions = ['SPATIALITE=YES']
            o_save_options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
            erg = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer=vlayer,
                fileName=self.db_name,
                transformContext=QgsCoordinateTransformContext(),
                options=o_save_options
            )

            if not self.gdblayer_choice:
                QgsProject.instance().removeMapLayer(vlayer.id())

        with FloodDB(self.db_name) as db:
            timakt = datetime.now()

            if self.velo_choice:
                # Erstellung Tabelle wlevel
                sql = "PRAGMA table_list('wlevel')"
                data = db.select(sql, 'Tabelleninfos')
                print(f'{data=}\n')
                if not data:
                    print(f'not data\n')
                    sqls = [
                        """CREATE TABLE IF NOT EXISTS wlevel (
                           pk INTEGER PRIMARY KEY,
                           h REAL,
                           tanf TEXT,
                           tend TEXT)""",
                        f"SELECT AddGeometryColumn('wlevel','geom', {self.epsg},'POLYGON',2)",
                        "SELECT CreateSpatialIndex('wlevel','geom')",
                    ]

                    if not db.sqlmany(sqls, 'Erstellung Tabelle "wlevel"'):
                        return False

            if self.wlevel_choice:
                # Erstellung Tabelle velo
                sql = "PRAGMA table_list('velo')"
                data = db.select(sql, 'Tabelleninfos')
                print(f'{data=}\n')
                if not data:
                    print(f'not data\n')
                    sqls = [
                        """CREATE TABLE IF NOT EXISTS velo (
                           pk INTEGER PRIMARY KEY,
                           v REAL,
                           tanf TEXT,
                           tend TEXT)""",
                        f"SELECT AddGeometryColumn('velo','geom', {self.epsg},'LINESTRING',2)",
                        "SELECT CreateSpatialIndex('velo','geom')",
                    ]

                    if not db.sqlmany(sqls, 'Erstellung Tabelle "velo"'):
                        return False

            db.commit()

            if self.velo_choice:
                sql = 'DELETE FROM wlevel'
                if not db.sql(sql, 'Zurücksetzen der Flächen-Tabelle'):
                    return False

            if self.wlevel_choice:
                sql = 'DELETE FROM velo'
                if not db.sql(sql, 'Zurücksetzen der Flächen-Tabelle'):
                    return False

            # Berechnung der Anzahl Zeitschritte
            if self.velo_choice:
                sql = "PRAGMA table_info('result2d__velocity')"
                data = db.select(sql, 'Tabelleninfo result2d__velocity')
            elif self.wlevel_choice:
                sql = "PRAGMA table_info('result2d__topo_decimated')"
                data = db.select(sql, 'Tabelleninfo result2d__topo_decimated')
            else:
                logger.warning("In der Ergebnisauswahl wurde keine Auswahl getroffen. Abbruch!")
                return False
            db.logger.debug(f'{data=}\n')
            nstep = int((len(data) - 6) / 2)
            db.logger.debug(f'Anzahl Zeitschritte: {nstep=}\n')

            for tstep in range(nstep):
                if (datetime.now() - timakt).seconds > 10:
                    timakt = datetime.now()
                    db.logger.info(f'Zeitschritt {tstep}')

                if self.velo_choice:
                    # Flächen mit maßgeblichem Wasserstand übertragen
                    sql = f'''
                        INSERT INTO wlevel (h, tanf, tend, geom)
                        SELECT
                            wl_{tstep} AS h,
                            datetime(julianday('{starttime}') + {tstep} * {interval}) AS tanf,
                            datetime(julianday('{starttime}') + {tstep + 1} * {interval}) AS tend,
                            CastToXY(CastToPolygon(GEOMETRY)) AS geom
                        FROM result2d__topo_decimated
                        WHERE wl_{tstep} >= {self.min_w}
                        '''
                    if not db.sql(sql, 'Erzeugen der wlevel-Flächen'):
                        return False

                if self.wlevel_choice:
                    # Geschwindikeitspfeile für maßgebliche Geschwindigkeiten erzeugen
                    sql = f'''
                        INSERT INTO velo (v, tanf, tend, geom)
                        SELECT
                            v_{tstep} AS v,
                            datetime(julianday('{starttime}') + {tstep} * {interval}) AS tanf,
                            datetime(julianday('{starttime}') + {tstep + 1} * {interval}) AS tend,
                            Makeline(
                                Makepoint(x(GEOMETRY), 
                                          y(GEOMETRY), {self.epsg}), 
                                MakePoint(x(GEOMETRY)+v_{tstep}*cos(v_dir_{tstep}/57.2958)*{self.faktor_v}, 
                                          y(GEOMETRY)+v_{tstep}*sin(v_dir_{tstep}/57.2958)*{self.faktor_v},
                                          {self.epsg})
                            ) as geom
                        FROM result2d__velocity
                        WHERE v_{tstep} >= {self.min_v}
                        '''
                    if not db.sql(sql, 'Erzeugen der wlevel-Flächen'):
                        return False

            db.commit()

            if self.wlevel_choice:
                vlayer = QgsVectorLayer(
                    self.db_name + '|layername=wlevel',
                    "wlevel",
                    "ogr"
                )
                QgsProject.instance().addMapLayer(vlayer)
                qmlfile = os.path.join(QKan.template_dir, 'qml', "waterlevel.qml")
                try:
                    vlayer.loadNamedStyle(qmlfile)
                except:
                    db.logger.error(f'Die Styledatei {qmlfile} konnte nicht gelesen werden!')
                    iface.messageBar().pushMessage("Programmfehler",
                                                   f"Die Styledatei {qmlfile} konnte nicht gelesen werden!",
                                                   level=Qgis.Critical)
                    return False

            if self.velo_choice:
                vlayer = QgsVectorLayer(
                    self.db_name + '|layername=velo',
                    "velo",
                    "ogr"
                )
                QgsProject.instance().addMapLayer(vlayer)
                qmlfile = os.path.join(QKan.template_dir, 'qml', "velocity.qml")
                try:
                    vlayer.loadNamedStyle(qmlfile)
                except:
                    db.logger.error(f'Die Styledatei {qmlfile} konnte nicht gelesen werden!')
                    iface.messageBar().pushMessage("Programmfehler",
                                                   f"Die Styledatei {qmlfile} konnte nicht gelesen werden!",
                                                   level=Qgis.Critical)
                    return False

            canvas = iface.mapCanvas()

            # set frame duration
            timeController = canvas.temporalController()
            intervall = QgsInterval()
            intervall.setMinutes(interval * 1440)
            timeController.setFrameDuration(intervall)

            # set frame rate
            timeController.setFramesPerSecond(0.5)

            # set time range
            timerange = QgsTemporalUtils.calculateTemporalRangeForProject(QgsProject.instance())
            if timerange.isInfinite():
                db.logger.error(f'Die Ergebnisdaten enthalten keine Zeitschritte')
                iface.messageBar().pushMessage("Datenfehler", "Eine Ergebnistabelle enthält keine Zeitschritte. "
                                                              "Möglicherweise wurden bei der Ergebnisausgabe nicht "
                                                              "alle Zeitschrittausgaben aktiviert.",
                                               level=Qgis.Warning)
                return False

            timeController.setTemporalExtents(timerange)

            # set navigation mode to 'animated'
            timeController.setNavigationMode(1)

            urlWithParams = f"crs=EPSG:{self.epsg}&format=image/png&layers=web&" \
                            f"styles&url=https://sgx.geodatenzentrum.de/wms_topplus_open"
            rlayer = QgsRasterLayer(urlWithParams, 'TopPlusOpen', 'wms')
            if not rlayer.isValid():
                db.logger.error("Layer failed to load!")
                return False
            QgsProject.instance().addMapLayer(rlayer, False)
            QgsProject.instance().layerTreeRoot().insertChildNode(2, QgsLayerTreeLayer(rlayer))

            iface.messageBar().pushMessage("Hinweis", 'Bitte Bedienfeld "Zeitsteuerung aktivieren"', level=Qgis.Info)

