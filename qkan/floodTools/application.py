import os

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface

from qkan import QKan, enums
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
from ._animation import FloodanimationTask
from .application_dialog import AnimationDialog
from qkan.tools.qkan_utils import get_default_dir
from ..utils import get_logger, QkanError

logger = get_logger("QKan.floodTools.application_dialog")


class FloodTools(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.animation_dlg = AnimationDialog(iface, default_dir, tr=self.tr)
        self.selected = False

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_animation = ":/plugins/qkan/floodTools/res/icon_animation.png"
        QKan.instance.add_action(
            icon_animation,
            text=self.tr("Überflutungsanimation"),
            toolbar='QKan-Datenaustausch',
            callback=self.run_floodAnimation,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.animation_dlg.close()

    def run_floodAnimation(self) -> None:
        """Anzeigen des Formulars und anschließende Erstellung der Animation"""

        # Wenn Formular geladen und Layer bereits angelegt, erneut Selected-Event verbinden
        try:
            # Für den Fall, dass das Objekt nicht mehr existiert ...
            _ = self.animation_dlg.layervelo
        except:
            self.animation_dlg.layervelo = None
        if not self.animation_dlg.layervelo:
            layers = QgsProject.instance().mapLayersByName('velocities')
            if layers:
                self.animation_dlg.layervelo = layers[0]
                self.animation_dlg.layervelo.selectionChanged.connect(self.animation_dlg.selChanged)

        try:
            # Für den Fall, dass das Objekt nicht mehr existiert ...
            _ = self.animation_dlg.layerwlevel
        except:
            self.animation_dlg.layerwlevel = None

        if not self.animation_dlg.layerwlevel:
            layers = QgsProject.instance().mapLayersByName('waterlevels')
            if layers:
                self.animation_dlg.layerwlevel = layers[0]
                self.animation_dlg.layerwlevel.selectionChanged.connect(self.animation_dlg.selChanged)

        self.animation_dlg.show()

        if self.animation_dlg.exec():
            # Read from form and save to config
            QKan.config.flood.velo = self.animation_dlg.cb_velo.isChecked()
            QKan.config.flood.wlevel = self.animation_dlg.cb_wlevel.isChecked()
            QKan.config.flood.gdblayer = self.animation_dlg.cb_gdb_remove.isChecked()
            QKan.config.flood.syncSelections = self.animation_dlg.cb_syncSelections.isChecked()

            # QKan.config.flood.faktor_v = float(self.animation_dlg.tf_faktor_v.text())
            QKan.config.flood.min_v = float(self.animation_dlg.tf_min_v.text())
            QKan.config.flood.min_w = float(self.animation_dlg.tf_min_w.text())
            # if self.animation_dlg.rb_v1.isChecked():
            #     QKan.config.flood.mikeversion = enums.MikeVersion.v1
            # elif self.animation_dlg.rb_v2.isChecked():
            #     QKan.config.flood.mikeversion = enums.MikeVersion.v2
            # else:
            #     logger.error_code(f'Keine gültige Mike-Version: {QKan.config.flood.mikeversion}')
            #     raise QkanError

            # if not QKan.config.flood.import_dir:
            #
            #     logger.warning("Fehler: Es wurde kein Verzeichnis ausgewählt!")
            #     self.iface.messageBar().pushMessage(
            #         "Fehler:",
            #         "Es wurde kein Verzeichnis ausgewählt!",
            #         level=Qgis.MessageLevel.Critical,
            #     )
            #     return
            # else:
            crs: QgsCoordinateReferenceSystem = self.animation_dlg.pw_epsg.crs()

            try:
                epsg = int(crs.postgisSrid())
            except ValueError:
                # TODO: Reporting this to the user might be preferable
                self.log.exception(
                    "Failed to parse selected CRS %s\nauthid:%s\n"
                    "description:%s\nproj:%s\npostgisSrid:%s\nsrsid:%s\nacronym:%s",
                    crs,
                    crs.authid(),
                    crs.description(),
                    crs.findMatchingProj(),
                    crs.postgisSrid(),
                    crs.srsid(),
                    crs.ellipsoidAcronym(),
                )
                return
            # else:
                # TODO: This should all be run in a QgsTask to prevent the main
                #  thread/GUI from hanging. However this seems to either not work
                #  or crash QGIS currently. (QGIS 3.10.3/0e1f846438)

            self.selected = self.animation_dlg.cb_selected.isChecked()

            QKan.config.epsg = epsg

            QKan.config.save()

            self._dofloodAnimation()

    def _dofloodAnimation(self) -> bool:
        """Start des Templates

        Einspringpunkt für Test
        """

        task = FloodanimationTask()
        task.run(self.selected)
        del task

        # Write project file (whether new or not)
        if QKan.config.project.file != '':
            project = QgsProject.instance()
            project.write(QKan.config.project.file)

        self.log.debug("FloodanimationTask finished")

        return True
