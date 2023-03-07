import os
import csv
from qgis.utils import pluginDirectory
from qgis.gui import QgisInterface
from qgis.core import QgsProject

from qkan import QKan, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin

from ._plausi import PlausiTask
from .application_dialog import PlausiDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


# logger = logging.getLogger("QKan.he8.application")


class Plausi(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"Plausi: default_dir: {default_dir}")
        self.plausi_dlg = PlausiDialog(default_dir, tr=self.tr)

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_plausi = ":/plugins/qkan/datacheck/res/icon_plausi.png"
        QKan.instance.add_action(
            icon_plausi,
            text=self.tr("Plausibilitätsprüfungen"),
            callback=self.run_plausi,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.plausi_dlg.close()

    def run_plausi(self) -> bool:
        """Anzeigen des Formulars zur Auswahl der durchzuführenden Plausibilitätsprüfungen und anschließender Start"""

        with DBConnection() as db_qkan:
            if not db_qkan.connected:
                return False

            if not self.plausi_dlg.prepareDialog(db_qkan):
                return False

            # Laden der Referenzliste
            db_qkan.cursl.execute("DELETE FROM reflist_zustand")
            db_qkan.commit()

            reflist_zustandfile = os.path.join(
                pluginDirectory("qkan"), "templates", "Plausi_Zustandsklassen.csv"
            )

            with open(reflist_zustandfile, "r") as fin:
                dr = csv.reader(fin, delimiter=";")

                to_db = []

                for a, b, c, d, e in dr:
                    c = [c] if c is None else c.split(",")
                    d = [d] if d is None else d.split(",")
                    e = [e] if e is None else e.split(",")
                    for i in c:
                        for j in d:
                            for k in e:
                                to_db.append([a, b, i, j, k])

                # to_db = [(i[0], i[1], i[2], i[3], i[4]) for i in dr]

            db_qkan.cursl.executemany(
                """
                INSERT INTO reflist_zustand
                    (art, hauptcode, charakterisierung1, charakterisierung2, bereich)
                VALUES (?, ?, ?, ?, ?);
                """,
                to_db,
            )
            db_qkan.commit()

            self.plausi_dlg.show()

            if self.plausi_dlg.exec_():
                # Read from form and save to config
                QKan.config.plausi.themen = (
                    self.plausi_dlg.selected_themes()
                )  # alternativ auch aus self.plausi_dlg.lw_themen zu entnehmen.
                QKan.config.plausi.keepdata = self.plausi_dlg.cb_keepdata.isChecked()

                QKan.config.save()

                self._doplausi(db_qkan)

    def _doplausi(self, db_qkan: DBConnection = None, is_test: bool = False) -> bool:
        """Start der Plausibilitätsabragen

        Einspringpunkt für Test
        """

        self.log.info("QKan: Plausibilitätsabragen")

        plau = PlausiTask(db_qkan)
        plau.run()

        self.log.debug("Closed DB")

        # Anzeige der Attributtabelle, nicht im Testmodus
        if not is_test:
            project = QgsProject.instance()
            layers = project.mapLayersByName("Fehlerliste")
            if not layers:
                self.log.warning('Layer "Fehlerliste" fehlt!')
                return True
            self.iface.showAttributeTable(layers[0])

        return True
