import logging
import os
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
from xml.etree import ElementTree

from PyQt5.QtWidgets import QWidget
from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.utils import pluginDirectory
from qkan import QKAN_FORMS, QKAN_TABLES, QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

from . import QKanDBDialog, QKanProjectDialog

if TYPE_CHECKING:
    from qkan.tools.application import QKanTools

FORM_CLASS_empty_db, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "..", "res", "application_emptyDB.ui")
)

LOGGER = logging.getLogger("QKan.tools.dialogs.empty_db")


def create_project(
    project_path: Path, db_path: Path, srid: int, zoom: List[float]
) -> None:
    # Get reference system
    try:
        crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
        srs_id = crs.srsid()
        proj4 = crs.toProj4()
        description = crs.description()
        projection_acronym = crs.projectionAcronym()
        if callable(getattr(crs, "ellipsoidAcronym", None)):
            ellipsoid_acronym = crs.ellipsoidAcronym()
        else:
            ellipsoid_acronym = None
    except BaseException as e:
        srid = -1
        srs_id, proj4, description, projection_acronym, ellipsoid_acronym = (
            "dummy",
        ) * 5

        fehlermeldung('\nFehler in "create_project"', str(e))
        fehlermeldung(
            "Fehler beim Erstellen des Projekts",
            f"\nFehler bei der Ermittlung der srid: {srid}\n",
        )
    # Template project should be created
    template_project = Path(pluginDirectory("qkan")) / "templates" / "projekt.qgs"

    # Replace db path with relative path if the same output folder is used
    data_source = str(db_path.absolute())
    if db_path.parent.absolute() == project_path.parent.absolute():
        data_source = f"./{db_path.name}"

    qgs_xml = ElementTree.parse(template_project)
    root = qgs_xml.getroot()

    for tag_layer in root.findall(".//projectlayers/maplayer"):
        # Ignore unrelated tables
        element = tag_layer.find("./datasource")
        if not element:
            continue

        text = element.text or ""
        if text[text.index('table="') + 7 :].split('" ')[0] not in QKAN_TABLES:
            continue

        # Remove <extent>s
        for extent in tag_layer.findall("./extent"):
            tag_layer.remove(extent)

        # Replace projection info
        for spatialrefsys in tag_layer.findall("./srs/spatialrefsys") + root.findall(
            ".//projectCrs/spatialrefsys"
        ):
            spatialrefsys.clear()

            ElementTree.SubElement(spatialrefsys, "srid").text = f"{srid}"
            ElementTree.SubElement(spatialrefsys, "proj4").text = proj4
            ElementTree.SubElement(spatialrefsys, "srsid").text = f"{srs_id}"
            ElementTree.SubElement(spatialrefsys, "authid").text = f"EPSG: {srid}"
            ElementTree.SubElement(spatialrefsys, "description").text = description
            ElementTree.SubElement(
                spatialrefsys, "projectionacronym"
            ).text = projection_acronym
            if ellipsoid_acronym is not None:
                ElementTree.SubElement(
                    spatialrefsys, "ellipsoidacronym"
                ).text = ellipsoid_acronym

        # Replace path to forms
        form_path = Path(pluginDirectory("qkan")) / "forms"
        for maplayer in root.findall(".//projectlayers/maplayer"):
            editform = maplayer.find("./editform")

            if editform is not None and editform.text:
                file_name = Path(editform.text).stem

                # Ignore non-QKAN forms
                if file_name not in QKAN_FORMS:
                    continue

                editform.text = str(form_path / file_name)

        # Reset zoom
        if len(zoom) == 0 or any([x is None for x in zoom]):
            zoom = [0.0, 100.0, 0.0, 100.0]
        for extent in root.findall(".//mapcanvas/extent"):
            for idx, name in enumerate(["xmin", "ymin", "xmax", "ymax"]):
                element = extent.find(f"./{name}")
                if element is not None:
                    element.text = "{:.3f}".format(zoom[idx])

        # Set path to database
        for datasource in root.findall(".//projectlayers/maplayer/datasource"):
            text = datasource.text or ""
            datasource.text = (
                "dbname='" + data_source + "' " + text[text.find("table=") :]
            )

        # Write modified project file
        qgs_xml.write(str(project_path))
        LOGGER.debug("Created project file %s", project_path)


class EmptyDBDialog(QKanDBDialog, QKanProjectDialog, FORM_CLASS_empty_db):  # type: ignore
    epsg: QgsProjectionSelectionWidget

    def __init__(self, plugin: "QKanTools", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.open_mode = False

    def run(self) -> None:
        # noinspection PyCallByClass,PyArgumentList
        self.epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))
        self.tf_qkanDB.setText(QKan.config.database.qkan)
        self.tf_projectFile.setText(QKan.config.project.file)
        self.show()

        if self.exec_():
            QKan.config.database.qkan = self.tf_qkanDB.text()
            QKan.config.project.file = project_file = self.tf_projectFile.text()
            QKan.config.epsg = int(self.epsg.crs().postgisSrid())
            QKan.config.save()

            db_qkan = DBConnection(dbname=self.tf_qkanDB.text(), epsg=QKan.config.epsg)

            if not db_qkan.connected:
                fehlermeldung("Fehler beim Erstellen der Datenbank:\n")
                return

            if self.tf_projectFile.text() == "":
                del db_qkan
                return

            # Grab srid
            if not db_qkan.sql(
                """
                SELECT srid
                FROM geom_cols_ref_sys
                WHERE Lower(f_table_name) = Lower('schaechte')
                AND Lower(f_geometry_column) = Lower('geom')
                """,
                "empty_db (1)",
            ):
                srid = 0
            else:
                srid = db_qkan.fetchone()[0]

            # Grab zoom states
            if not db_qkan.sql(
                """
                SELECT min(x(geop)) AS xmin,
                    max(x(geop)) AS xmax,
                    min(y(geop)) AS ymin,
                    max(y(geop)) AS ymax
                FROM schaechte
             """,
                "empty_db (2)",
            ):
                zoom: List[float] = []
            else:
                zoom = db_qkan.fetchone()

            # Close database
            del db_qkan

            # Create project file
            create_project(
                Path(project_file), Path(self.tf_qkanDB.text()), srid, zoom,
            )

            # Load project
            # noinspection PyArgumentList
            QgsProject.instance().read(project_file)
