"""

  Qgsadapt
  ==============
  
  Für ein geladenes Projekt wird eine andere Projektdatei (default: Projekt.qgs im Verzeichnis templates)
  geladen und damit das aktuelle Projekt angepasst.
  
  | Dateiname            : k_qgsadapt.py
  | Date                 : November 2020
  | Copyright            : (C) 2020 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$
  
  This program is free software; you can redistribute it and/or modify   
  it under the terms of the GNU General Public License as published by   
  the Free Software Foundation; either version 2 of the License, or      
  (at your option) any later version.

"""

__author__ = "Joerg Hoettges"
__date__ = "November 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

import os
from pathlib import Path, PurePath
from xml.etree import ElementTree as ET

from qgis.core import QgsCoordinateReferenceSystem
from qgis.utils import pluginDirectory

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    list_qkan_layers,
    get_qkanlayer_attributes,
)
from qkan.utils import get_logger

logger = get_logger("QKan.tools.k_qgsadapt")

progress_bar = None


def qgsadapt(
    database_QKan: str,
    dbQK: DBConnection,
    projectfile: str,
    projecttemplate: str = None,
    epsg: int = None,
) -> bool:
    """Lädt eine (Vorlage-) Projektdatei (*.qgs) und adaptiert diese auf eine QKan-Datenbank an.
    Anschließend wird dieses Projekt geladen.
    Voraussetzungen: keine

    :projecttemplate:           Vorlage-Projektdatei
    :type database:             String

    :database_QKan:             Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :type database_QKan:        String

    :projectfile:               Zu Erzeugende Projektdatei
    :type projectfile:          String

    :epsg:                      EPSG-Code. Falls nicht vorgegeben, wird dieser aus der Tabelle 'schaechte' gelesen
    :type epsg:                 Integer

    :returns:                   Success
    :type:                      Boolean
    """

    # --------------------------------------------------------------------------
    # Zoom-Bereich für die Projektdatei vorbereiten
    sql = """SELECT min(x(coalesce(geop, centroid(geom)))) AS xmin, 
                    min(y(coalesce(geop, centroid(geom)))) AS ymin, 
                    max(x(coalesce(geop, centroid(geom)))) AS xmax, 
                    max(y(coalesce(geop, centroid(geom)))) AS ymax
             FROM schaechte"""
    try:
        dbQK.sql(sql)
    except BaseException as err:
        fehlermeldung("SQL-Fehler", repr(err))
        fehlermeldung("Fehler in qgsadapt", "\nFehler in sql_zoom: \n" + sql + "\n\n")
        return False

    try:
        zoom = dbQK.fetchone()
    except BaseException as err:
        fehlermeldung("SQL-Fehler", repr(err))
        fehlermeldung(
            "\nFehler in sql_zoom; daten= \n",
        )
        zoom = [0.0, 0.0, 100.0, 100.0]

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten,
    # außer: Wenn epsg aus Parameterliste vorgegeben, dann übernehmen
    if epsg:
        srid = epsg
        logger.debug(f"Vorgabe epsg: %s", epsg)
    else:
        sql = """SELECT srid
                FROM geom_cols_ref_sys
                WHERE Lower(f_table_name) = Lower('schaechte')
                AND Lower(f_geometry_column) = Lower('geom')"""
        if not dbQK.sql(sql, "k_qgsadapt (1)"):
            return False
        srid = dbQK.fetchone()

    try:
        crs = QgsCoordinateReferenceSystem.fromEpsgId(srid)
        srsid = crs.srsid()
        proj4 = crs.toProj()
        description = crs.description()
        projection_acronym = crs.projectionAcronym()
        if callable(getattr(crs, "ellipsoidAcronym", None)):
            ellipsoid_acronym = crs.ellipsoidAcronym()
        else:
            ellipsoid_acronym = None
    except BaseException as e:
        srsid, proj4, description, projection_acronym, ellipsoid_acronym = (
            "dummy",
        ) * 5

        fehlermeldung('\nFehler in "create_project"', str(e))
        fehlermeldung(
            "Fehler beim Erstellen des Projekts",
            f"\nFehler bei der Ermittlung der srid: {srid}\n",
        )
        srid = -1

    # --------------------------------------------------------------------------
    # Projektdatei schreiben, falls ausgewählt

    # Liste aller QKan-Layer erstellen. Dafür wird auf jeden Fall auf die
    # Standard-Projektdatei von QKan zurückgegriffen

    qkanTemplate = Path(pluginDirectory("qkan")) / "templates" / "projekt.qgs"

    logger.debug(f"k_qgsadapt.QKan-Projekttemplate: {qkanTemplate}")

    qkanLayers = list_qkan_layers(
        qkanTemplate
    )  # Liste aller Layernamen aus gewählter QGS-Vorlage
    qkanTables = set([el[0] for el in qkanLayers.values()])
    logger.debug(f'k_qgsadapt.qkanLayers: {qkanLayers}')
    logger.debug(f'k_qgsadapt.qkanLayers: {qkanTables}')

    # Fehlende Layer ergänzen. Unabhängig von der Auswahl werden die fehlenden Referenztabellen
    # auf jeden Fall ergänzt.

    if projectfile is not None and projectfile != "":
        templatepath = os.path.join(pluginDirectory("qkan"), "templates")
        if not projecttemplate:
            projecttemplate = os.path.join(templatepath, "projekt.qgs")
        projectpath = os.path.dirname(projectfile)
        if os.path.dirname(database_QKan) == projectpath:
            datasource = database_QKan.replace(os.path.dirname(database_QKan), ".")
        else:
            datasource = database_QKan

        # Replace db path with relative path if the same output folder is used
        db_path = Path(database_QKan)
        datasource = str(db_path.absolute())
        if db_path.parent.absolute() == Path(projectfile).parent.absolute():
            datasource = db_path.name

        # Lesen der Projektdatei ------------------------------------------------------------------
        qgsxml = ET.parse(projecttemplate)
        root = qgsxml.getroot()

        # Projektionssystem anpassen --------------------------------------------------------------

        for tag_maplayer in root.findall(".//projectlayers/maplayer"):
            tag_datasource = tag_maplayer.find("./datasource")
            if tag_datasource is None:
                continue

            tex = tag_datasource.text
            if not tex or tex[:6] != "dbname":
                continue

            # Nur QKan-Tabellen bearbeiten
            if 'table="' in tex and tex[tex.index('table="') + 7 :].split('" ')[0] in qkanTables:

                # <extent> löschen
                for tag_extent in tag_maplayer.findall("./extent"):
                    tag_maplayer.remove(tag_extent)

                for tag_spatialrefsys in tag_maplayer.findall("./srs/spatialrefsys"):
                    tag_spatialrefsys.clear()

                    ET.SubElement(tag_spatialrefsys, "srid").text = f"{srid}"
                    ET.SubElement(tag_spatialrefsys, "proj4").text = proj4
                    ET.SubElement(tag_spatialrefsys, "srsid").text = f"{srsid}"
                    ET.SubElement(tag_spatialrefsys, "authid").text = f"EPSG:{srid}"
                    ET.SubElement(tag_spatialrefsys, "description").text = description
                    ET.SubElement(tag_spatialrefsys, "projectionacronym").text = projection_acronym
                    if ellipsoid_acronym is not None:
                        ET.SubElement(
                            tag_spatialrefsys, "ellipsoidacronym"
                        ).text = ellipsoid_acronym

        # Projektionssystem des Plans anpassen --------------------------------------------------------------

        for tag_spatialrefsys in root.findall(
            ".//mapcanvas/destinationsrs/spatialrefsys"
        ):
            tag_spatialrefsys.clear()

            ET.SubElement(tag_spatialrefsys, "srid").text = f"{srid}"
            ET.SubElement(tag_spatialrefsys, "proj4").text = proj4
            ET.SubElement(tag_spatialrefsys, "srsid").text = f"{srsid}"
            ET.SubElement(tag_spatialrefsys, "authid").text = f"EPSG:{srid}"
            ET.SubElement(tag_spatialrefsys, "description").text = description
            ET.SubElement(tag_spatialrefsys, "projectionacronym").text = projection_acronym
            if ellipsoid_acronym is not None:
                ET.SubElement(
                    tag_spatialrefsys, "ellipsoidacronym"
                ).text = ellipsoid_acronym

        # Projektionssystem von QGIS anpassen --------------------------------------------------------------

        for tag_spatialrefsys in root.findall(".//projectCrs/spatialrefsys"):
            tag_spatialrefsys.clear()

            ET.SubElement(tag_spatialrefsys, "srid").text = f"{srid}"
            ET.SubElement(tag_spatialrefsys, "proj4").text = proj4
            ET.SubElement(tag_spatialrefsys, "srsid").text = f"{srsid}"
            ET.SubElement(tag_spatialrefsys, "authid").text = f"EPSG:{srid}"
            ET.SubElement(tag_spatialrefsys, "description").text = description
            ET.SubElement(tag_spatialrefsys, "projectionacronym").text = projection_acronym
            if ellipsoid_acronym is not None:
                ET.SubElement(
                    tag_spatialrefsys, "ellipsoidacronym"
                ).text = ellipsoid_acronym

        # Adapt path to forms
        # logger.debug(f'Liste aller QKan-Formulardateien: \n{QKan.forms}')
        form_path = Path(pluginDirectory("qkan")) / "forms"
        for tag_maplayer in root.findall(".//projectlayers/maplayer"):
            tag_editform = tag_maplayer.find("./editform")

            if tag_editform is not None and tag_editform.text:
                file_name = Path(tag_editform.text).name
                # logger.debug(f'Formularname in Projektdatei: file_name={file_name}')

                # Ignore non-QKAN forms
                if file_name not in QKan.forms:
                    # logger.debug(f"Formular gehört nicht zu QKan: {file_name}")
                    continue
                else:
                    tag_editform.text = str(form_path / file_name)
                    # logger.debug(f'Geänderter Formularpfad: {tag_editform.text}')

        # Adapt path to symbols, 2* for each layer
        symbols_path = Path(pluginDirectory("qkan")) / "symbols"
        for tag_option in root.findall(
                ".//projectlayers/maplayer/renderer-v2/symbols/symbol/"
                "layer/symbol/layer[@class='SvgMarker']/Option/Option[@name='name']"):
            svg_path = Path(tag_option.attrib['value'])
            if PurePath(svg_path).match('plugins/qkan/symbols/*.svg'):
                tag_option.attrib['value'] = str(symbols_path / svg_path.name)
        for tag_option in root.findall(
                ".//projectlayers/maplayer/renderer-v2/symbols/symbol/"
                "layer/symbol/layer[@class='SvgMarker']/prop[@k='name']"):
            svg_path = Path(tag_option.attrib['v'])
            if PurePath(svg_path).match('plugins/qkan/symbols/*.svg'):
                tag_option.attrib['v'] = str(symbols_path / svg_path.name)

        # Reset zoom
        if len(zoom) == 0 or any([x is None for x in zoom]):
            zoom = [0.0, 0.0, 100.0, 100.0]
        for tag_extent in root.findall(".//mapcanvas/extent"):
            for idx, name in enumerate(["xmin", "ymin", "xmax", "ymax"]):
                element = tag_extent.find(f"./{name}")
                if element is not None:
                    element.text = "{:.3f}".format(zoom[idx])

        # Set path to QKan database in datasource
        for tag_datasource in root.findall(".//projectlayers/maplayer/datasource"):
            text = tag_datasource.text or ""
            dbname, table, _, _ = get_qkanlayer_attributes(text)
            if not text or text[:6] != "dbname" or table not in qkanTables:
                continue
            tag_datasource.text = (
                "dbname='" + datasource + "' " + text[text.find("table=") :]
            )

        # Set path to QKan database in LayerSource
        for tag_layersource in root.findall(
                ".//projectlayers/maplayer/fieldConfiguration/field/editWidget/config/Option/Option[@name='LayerSource']"
        ):
            text = tag_layersource.attrib['value'] or ""
            dbname, table, _, _ = get_qkanlayer_attributes(text)
            if not text or text[:6] != "dbname" or table not in qkanTables:
                continue
            tag_layersource.attrib['value'] = (
                "dbname='" + datasource + "' " + text[text.find("table=") :]
            )

        # Set path to QKan database in layer-tree-layer
        for tag_layertreelayer in root.findall(
                ".//layer-tree-group/layer-tree-group/layer-tree-group/layer-tree-layer/[@providerKey='spatialite']"
        ):
            text = tag_layertreelayer.attrib['source'] or ""
            dbname, table, _, _ = get_qkanlayer_attributes(text)
            if not text or text[:6] != "dbname" or table not in qkanTables:
                continue
            tag_layertreelayer.attrib['source'] = (
                "dbname='" + datasource + "' " + text[text.find("table=") :]
            )

        # writing modified project file
        try:
            qgsxml.write(projectfile)
        except BaseException as e:
            fehlermeldung('\nFehler beim Schreiben der Projektdatei"', str(e))

        logger.debug("Projektdatei: {}".format(projectfile))

    return True
