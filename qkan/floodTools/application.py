import os
import logging

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface

from qkan import QKan, get_default_dir
from qkan.plugin import QKanPlugin

from ._animation import FloodanimationTask
from .application_dialog import AnimationDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip

logger = logging.getLogger("QKan.floodTools.application_dialog")


class FloodTools(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.animation_dlg = AnimationDialog(iface, default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_animation = ":/plugins/qkan/floodTools/res/icon_animation.png"
        QKan.instance.add_action(
            icon_animation,
            text=self.tr("Überflutungsanimation"),
            callback=self.run_floodAnimation,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.animation_dlg.close()

    def run_floodAnimation(self) -> None:
        """Anzeigen des Formulars und anschließende Erstellung der Animation"""

        self.animation_dlg.show()

        if self.animation_dlg.exec_():
            # Read from form and save to config
            QKan.config.flood.database = self.animation_dlg.tf_database.text()
            QKan.config.project.file = self.animation_dlg.tf_project.text()
            QKan.config.flood.import_dir = self.animation_dlg.tf_import.text()

            QKan.config.flood.velo = self.animation_dlg.cb_velo.isChecked()
            QKan.config.flood.wlevel = self.animation_dlg.cb_wlevel.isChecked()

            QKan.config.flood.faktor_v = self.animation_dlg.tf_faktor_v.text()
            QKan.config.flood.gdblayer = self.animation_dlg.cb_gdb_remove.isChecked()

            if not QKan.config.flood.import_dir:

                logger.error("Fehler: Es wurde kein Verzeichnis ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler:",
                    "Es wurde kein Verzeichnis ausgewählt!",
                    level=Qgis.Critical,
                )
                return False
            else:
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
                else:
                    # TODO: This should all be run in a QgsTask to prevent the main
                    #  thread/GUI from hanging. However this seems to either not work
                    #  or crash QGIS currently. (QGIS 3.10.3/0e1f846438)
                    QKan.config.epsg = epsg

                    QKan.config.save()

                    self._dofloodAnimation()


    def _dofloodAnimation(self) -> bool:
        """Start des Templates

        Einspringpunkt für Test
        """

        task = FloodanimationTask()
        task.run()
        del task

        # Write project file (whether new or not)
        if QKan.config.project.file != '':
            project = QgsProject.instance()
            project.write(QKan.config.project.file)

        self.log.debug("FloodanimationTask finished")

        return True

    def click_help(self) -> None:
        """Reaktion auf Klick auf Help-Schaltfläche"""

        help_file = "https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/" \
                    "QKan/Doku/Qkan_allgemein.html?highlight=strakat"
        os.startfile(help_file)

































