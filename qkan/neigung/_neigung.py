from qgis.utils import iface
from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.utils import  QkanUserError, QkanDbError, QkanAbortError, get_logger
from qgis import processing
import requests
import re

import urllib.request
import os


from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
)

logger = get_logger("QKan.neigung")


class NeigungTask:
    def __init__(self, base_url, zielordner_dmg, speicherort_dgm, db_qkan: DBConnection, cb, epsg):
        self.db_qkan = db_qkan
        self.base_url = base_url
        self.zielordner_dmg = zielordner_dmg
        self.speicherort_dgm = speicherort_dgm
        self.cb = cb
        self.epsg = epsg


    def ausdehnung(self, bbox):
        kacheln = []
        xmin = int(bbox["xmin"] // 1000)
        xmax = int(bbox["xmax"] // 1000)
        ymin = int(bbox["ymin"] // 1000)
        ymax = int(bbox["ymax"] // 1000)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                kacheln.append((x, y))
        return kacheln

    def download(self, base_url, x, y):
        prefix = f"dgm1_32_{x}_{y}_1_nw"
        response = requests.get(base_url)
        xml = response.text

        pattern = fr'name="({prefix}[^"]+)"'
        files = re.findall(pattern, xml)
        return files

    def laden(self, url, verzeichnis):
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                with open(verzeichnis, 'wb') as out_file:
                    out_file.write(response.read())
            else:
                msg = (
                    f"Daten konnten nicht heruntergeladen werden"
                )
                logger.warning_user(msg)
                raise QkanUserError(msg)



    def run(self) -> None:
        layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
        parameter = {
            'INPUT': layer,
            'TARGET_CRS': 'EPSG:'+str(self.epsg),
            'OUTPUT': 'memory:Reprojected'
        }
        result = processing.run('native:reprojectlayer', parameter)['OUTPUT']

        ext = result.extent()
        bbox = {
            "xmin": int(ext.xMinimum()),
            "ymin": int(ext.yMinimum()),
            "xmax": int(ext.xMaximum()),
            "ymax": int(ext.yMaximum())
        }

        if self.cb['cb1']:

            kacheln = self.ausdehnung(bbox)
            dgm_layer = []


            for x, y in kacheln:
                url = self.download(self.base_url, x, y)
                dateiname = os.path.basename(url[0])
                ordner = os.path.join(self.zielordner_dmg, dateiname)
                self.laden(self.base_url + url[0], ordner)
                dgm_layer.append(self.zielordner_dmg + '/' + dateiname)

            #DGM Daten verschmelzen
            dgm = processing.run("gdal:merge", {
                'INPUT': dgm_layer,
                'PCT': False, 'SEPARATE': False, 'NODATA_INPUT': None, 'NODATA_OUTPUT': None, 'OPTIONS': '', 'EXTRA': '',
                'DATA_TYPE': 5, 'OUTPUT': self.zielordner_dmg+'/'+'dgm_gesamt.tif'})

            dgm_gesamt = self.zielordner_dmg+'/'+'dgm_gesamt.tif'
            if dgm_gesamt == '':
                msg = (
                    f"Keine Daten ausgewählt"
                )
                logger.warning_user(msg)
                raise QkanUserError(msg)

        elif self.cb['cb2']:
            dgm_gesamt = self.speicherort_dgm
            if dgm_gesamt == '':
                msg = (
                    f"Keine Daten ausgewählt"
                )
                logger.warning_user(msg)
                raise QkanUserError(msg)

        #Hangneigung ermitteln

        neigung = processing.run("native:slope", {'INPUT': dgm_gesamt,'Z_FACTOR':1,'OUTPUT':self.zielordner_dmg+'/'+'neigung.tif'})

        #Mittlere Neigung dem Layer Einzelflächen oder Haltungsflächen zu

        temp = processing.run("native:zonalstatisticsfb", {
            'INPUT': 'spatialite://dbname=' + self.db_qkan.dbname + ' table="flaechen" (geom)',
            'INPUT_RASTER': self.zielordner_dmg+'/'+'neigung.tif',
            'RASTER_BAND': 1, 'COLUMN_PREFIX': '_', 'STATISTICS': [2], 'OUTPUT': self.zielordner_dmg+'/'+'neigung.shp'})

        #die daten aus temp zurück in die Datenbank spielen und anhand der mittelwerte die jeweilige klasse ermitteln!

        #layer = QgsProject.instance().mapLayersByName("neigung")[0]
        layer = QgsVectorLayer(self.zielordner_dmg+'/'+'neigung.shp', "neigung", "ogr")

        feldname = "neigkl"
        ausdruck = 'if( "_mean"<=1,1,if("_mean"<=4,2, if("_mean" <=10,3,if("_mean" <=14,4,if("_mean">14,5,NULL)))))'

        exp = QgsExpression(ausdruck)
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

        layer.startEditing()

        for feature in layer.getFeatures():
            context.setFeature(feature)
            wert = exp.evaluate(context)
            feld_index = layer.fields().indexFromName(feldname)
            layer.changeAttributeValue(feature.id(), feld_index, wert)

        layer.commitChanges()

        #Daten zurück in Datenbank schreiben

        temp_layer = QgsVectorLayer(self.zielordner_dmg+'/'+'neigung.shp', "neigung", "ogr")

        target_layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
        target_layer.startEditing()

        for temp_feat in temp_layer.getFeatures():
            fid = temp_feat.id()

            db_feat = target_layer.getFeature(fid)

            neigung = temp_feat["neigkl"]
            target_layer.changeAttributeValue(db_feat.id(), target_layer.fields().indexFromName("neigkl"), neigung)

        target_layer.commitChanges()

        temp_layer = QgsVectorLayer(self.zielordner_dmg + '/' + 'neigung.shp', "neigung", "ogr")

        target_layer = QgsProject.instance().mapLayersByName(enums.LAYERBEZ.EINZELFLAECHEN.value)[0]
        target_layer.startEditing()

        for temp_feat in temp_layer.getFeatures():
            fid = temp_feat.id()

            db_feat = target_layer.getFeature(fid)

            neigung = temp_feat["_mean"]
            target_layer.changeAttributeValue(db_feat.id(), target_layer.fields().indexFromName("neigung"), neigung)

        target_layer.commitChanges()


        #Close connection
        #self.db_qkan.__del__()