import os

from qkan.utils import get_logger

from qkan import QKan
from qkan import enums
from qkan.tools.k_schadenstexte import Schadenstexte
from qkan.tools.qkan_utils import loadLayer
from qgis.core import (
    QgsProject,
    QgsLayoutExporter,
    QgsDataSourceUri,
    QgsVectorLayer,
    QgsPrintLayout,
    QgsReadWriteContext,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsRectangle,
    QgsGeometry,
    QgsWkbTypes,
)
from PyQt5.QtCore import QVariant
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import pluginDirectory
from pathlib import Path


logger = get_logger("QKan.tools.k_bericht")


# # Feature erweitern
# def create_buffered_geometry(feature: QgsFeature):
#     geom = feature.geometry()
#     length = geom.length()
#
#     # Pufferwerte
#     left_pct = 0.1
#     right_pct = 0.05
#     top_bottom_pct = 0.025
#
#     # Bounding Box der Linie
#     bbox = geom.boundingBox()
#
#     # Asymmetrische Erweiterung
#     x_min = bbox.xMinimum() - left_pct * length
#     x_max = bbox.xMaximum() + right_pct * length
#     y_min = bbox.yMinimum() - top_bottom_pct * length
#     y_max = bbox.yMaximum() + top_bottom_pct * length
#
#     return QgsRectangle(x_min, y_min, x_max, y_max)

def bericht(
    db_qkan, filename, auswahl, art
) -> None:
    """Erzeugt Haltungsberichte.
    """
    #TODO: unterscheiden nach art ob _bewertung oder _subkans genutzt werden soll

    #Layout verändern
    table = 'untersuchdat_haltung_bewertung'
    layernam = enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value
    if db_qkan.attrlist(table) != []:
        loadLayer(
            layerbez=layernam,
            table=table,
            geom_column='geom',
            qmlfile='untersuchdat_haltung_bewertung_dwa_bericht.qml',
            group=['qkan', 'Ergebnisse'],
        )

    # Konfiguration zwischenspeichern
    storedvalues = [
        QKan.config.zustand.abstand_zustandstexte,
        QKan.config.zustand.abstand_zustandsbloecke,
        QKan.config.zustand.abstand_knoten_anf,
        QKan.config.zustand.abstand_knoten_1,
        QKan.config.zustand.abstand_knoten_2,
        QKan.config.zustand.abstand_knoten_end,
    ]

    QKan.config.zustand.abstand_zustandstexte = 0.6
    QKan.config.zustand.abstand_zustandsbloecke = 1.0
    QKan.config.zustand.abstand_knoten_anf = 0.0
    QKan.config.zustand.abstand_knoten_1 = 1.0
    QKan.config.zustand.abstand_knoten_2 = 1.5
    QKan.config.zustand.abstand_knoten_end = 5.0

    Schadenstexte.setschadenstexte_haltungen(db_qkan)
    Schadenstexte.setschadenstexte_schaechte(db_qkan)
    Schadenstexte.setschadenstexte_anschlussleitungen(db_qkan)


    #Bericht erstellen und abspeichern

    x = QgsProject.instance()

    layout = x.layoutManager().layoutByName('Haltungsbericht')

    if layout is None:
        template_path = str(
                    Path(pluginDirectory("qkan")) / "templates" / "Haltungsbericht.qpt"
                )
        layout = QgsPrintLayout(x)
        layout.initializeDefaults()
        layout.setName("Haltungsbericht")

        doc = QDomDocument()
        with open(template_path, 'r', encoding='utf-8') as f:
            doc.setContent(f.read())

        context = QgsReadWriteContext()
        layout.loadFromTemplate(doc, context)

        # Layout zum Projekt hinzufügen
        x.layoutManager().addLayout(layout)
        #layout = x.layoutManager().layoutByName('Haltungsbericht')


        image_path = str(
                    Path(pluginDirectory("qkan")) / "tools" / "res" / "QKan_Logo.png"
                )

        layout = x.layoutManager().layoutByName("Haltungsbericht")
        item = layout.itemById("Bild")
        item.setPicturePath(image_path)
        item.refresh()
        item = layout.itemById("Bild1")
        item.setPicturePath(image_path)
        item.refresh()


    atlas = layout.atlas()
    atlas.setEnabled(True)
    # layer = atlas.coverageLayer()
    #
    # # Temporärer Layer
    # temp_layer = QgsVectorLayer("LineString?crs=EPSG:25832", "atlas_buffered", "memory")
    # pr = temp_layer.dataProvider()
    # pr.addAttributes(layer.fields())
    # pr.addAttributes([QgsField("bbox_geom", QVariant.String, len=255)])
    # temp_layer.updateFields()
    #
    # for feat in layer.getFeatures():
    #     bbox = create_buffered_geometry(feat)
    #     if bbox is not None and not bbox.isEmpty():
    #         bbox_geom = QgsGeometry.fromRect(bbox)
    #         new_feat = QgsFeature(temp_layer.fields())
    #         new_feat.setGeometry(feat.geometry())  # originale Linie
    #         new_feat["bbox_geom"] = bbox_geom.asWkt()  # WKT speichern
    #         pr.addFeature(new_feat)

    exporter = QgsLayoutExporter(layout)
    settings = QgsLayoutExporter.PdfExportSettings()
    base_folder = filename
    coverage_layer = atlas.coverageLayer()

    if auswahl:

        haltungen_layer = QgsProject.instance().mapLayersByName("Haltungen")[0]
        geom_type = QgsWkbTypes.displayString(haltungen_layer.wkbType())

        # Auswahl übernehmen
        db_qkan.getSelection()

        sql = f"""
                SELECT pk from sel_haltungen
                """
        db_qkan.sql(sql)

        selected_ids =  [row[0] for row in db_qkan.fetchall()]


        fields = haltungen_layer.fields()
        temp_layer = QgsVectorLayer(f"{geom_type}?crs={haltungen_layer.crs().authid()}",
                                    "vl_atlas_temp", "memory")
        pr = temp_layer.dataProvider()
        pr.addAttributes(fields)
        temp_layer.updateFields()

        features = []

        for feat in haltungen_layer.getFeatures():
            if feat["pk"] in selected_ids:
                # new_feat = QgsFeature(fields)
                # new_feat.setGeometry(feat.geometry())
                # for f in fields:
                #     new_feat[f.name()] = feat[f.name()]
                # pr.addFeature(new_feat)
                features.append(feat)

        print(features)
        pr.addFeatures(features)

        QgsProject.instance().addMapLayer(temp_layer, addToLegend=False)

        atlas = layout.atlas()
        atlas.setEnabled(True)
        atlas.setCoverageLayer(temp_layer)
        atlas.setFilterFeatures(True)

        # expression = """
        # "haltnam" IN (
        #     aggregate(
        #         layer:='vl_atlas_temp',
        #         aggregate:='array_agg',
        #         expression:="haltnam"
        #     )
        # )
        # """
        # temp_layer.setSubsetString(expression)


        atlas.setFilterFeatures(True)

        layout.refresh() 

        atlas.beginRender()
        for i in range(temp_layer.featureCount()):
            atlas.next()
            #idx = atlas.currentFeatureNumber()
            #feature = (temp_layer.getFeature(idx))
            feature = features[atlas.currentFeatureNumber()]

            pdf_path = rf"{base_folder}\{feature['haltnam']}.pdf"
            exporter.exportToPdf(pdf_path, settings)
        atlas.endRender()

        haltungen_layer.setSubsetString("")

    else:
        haltungen = QgsProject.instance().mapLayersByName("Haltungen")[0]
        features = list(coverage_layer.getFeatures())
        coverage_layer = atlas.coverageLayer()
        coverage_layer.setSubsetString("")
        atlas.beginRender()
        for i in range(len(features)):
            atlas.next()  # Atlas auf die nächste Seite setzen
            feature = features[atlas.currentFeatureNumber()]

            pdf_path = rf"{base_folder}\{feature['haltnam']}.pdf"
            exporter.exportToPdf(pdf_path, settings)
        atlas.endRender()

        haltungen.setSubsetString("")


    #Layout zurücksetzen
    if db_qkan.attrlist(table) != []:
        # x = QgsProject.instance()
        # try:
        #     x.removeMapLayer(x.mapLayersByName(layernam)[0].id())
        # except:
        #     pass
        loadLayer(
            layerbez=layernam,
            table=table,
            geom_column='geom',
            qmlfile='untersuchdat_haltung_dwa.qml',
            group=['qkan', 'Ergebnisse'],
        )

    # uri = QgsDataSourceUri()
    # uri.setDatabase(db_qkan.dbname)
    # schema = ''
    # table = 'untersuchdat_haltung_bewertung'
    # geom_column = 'geom'
    # uri.setDataSource(schema, table, geom_column)
    # untersuchdat_haltung_bewertung = enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value
    # vlayer = QgsVectorLayer(uri.uri(), untersuchdat_haltung_bewertung, 'spatialite')
    # x = QgsProject.instance()
    # try:
    #     x.removeMapLayer(x.mapLayersByName(untersuchdat_haltung_bewertung)[0].id())
    # except:
    #     pass
    #
    # x = os.path.dirname(os.path.abspath(__file__))
    # vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_dwa.qml')
    # # QgsProject.instance().addMapLayer(vlayer)
    # group = 'Ergebnisse'
    # layersRoot = QgsProject.instance().layerTreeRoot()
    # QgsProject.instance().addMapLayer(vlayer, False)
    # atcGroup = layersRoot.findGroup(group)
    # if atcGroup is None:
    #     atcGroup = layersRoot.addGroup(group)
    # atcGroup.addLayer(vlayer)


    #Beschriftung zurücksetzen und neu berechnen

    (
        QKan.config.zustand.abstand_zustandstexte,
        QKan.config.zustand.abstand_zustandsbloecke,
        QKan.config.zustand.abstand_knoten_anf,
        QKan.config.zustand.abstand_knoten_1,
        QKan.config.zustand.abstand_knoten_2,
        QKan.config.zustand.abstand_knoten_end,
    ) = storedvalues

    Schadenstexte.setschadenstexte_haltungen(db_qkan)
    Schadenstexte.setschadenstexte_schaechte(db_qkan)
    Schadenstexte.setschadenstexte_anschlussleitungen(db_qkan)
