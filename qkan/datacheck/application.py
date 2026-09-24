import os
import csv
from qgis.utils import pluginDirectory
from qgis.gui import QgisInterface
from qgis.core import QgsProject

import qkan.config
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin

from ._plausi import PlausiTask
from .application_dialog import PlausiDialog

from qkan.utils import get_logger, QkanError
from qkan import enums
from qkan.tools.qkan_utils import get_default_dir

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401

logger = get_logger("QKan")


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
            toolbar='QKan-Allgemein',
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

            self._prepareplausi(db_qkan)            # Aktualisierung der Plausibilitätskontrollen

            self.plausi_dlg.show()

            if self.plausi_dlg.exec_():
                # Read from form and save to config
                QKan.config.plausi.themen = (
                    self.plausi_dlg.selected_themes()
                )  # alternativ auch aus self.plausi_dlg.lw_themen zu entnehmen.
                QKan.config.plausi.keepdata = self.plausi_dlg.cb_keepdata.isChecked()
                QKan.config.plausi.limitdata = self.plausi_dlg.cb_limitdata.isChecked()

                QKan.config.save()

                self._doplausi(db_qkan)


    def _prepareplausi(self, db_qkan: DBConnection = None) -> None:
        """Vorbereiten der Pluaisbilitätskontrollen
        Diese Funktion muss für die automatischen Tests (z. B. test_datacheck.py) vor
        _doplausi() aufgerufen werden"""

        # Laden der Referenzliste
        db_qkan.sql("DELETE FROM reflist_zustand", "Plausibilität: Zustandsliste zurücksetzen")
        db_qkan.commit()

        # Laden der Plausibilitätsprüfungen
        templateDir = os.path.join(pluginDirectory("qkan"), "templates")
        filenam = os.path.join(templateDir, 'Plausibilitaetspruefungen.sql')
        if db_qkan.executefile(filenam):
            logger.debug(f"Plausibilitätsabfragen aus Datei {filenam} eingelesen")
        else:
            logger.error("Fehler beim Lesen der Plausibilitätsabfragen:"
                          f"Die Datei {filenam} konnten nicht gelesen werden!")
        db_qkan.commit()
        logger.debug("Plausibilitätsprüfungen mit Datei 'Plausibilitaetspruefungen.sql' ergänzt.")

        if not self.plausi_dlg.prepareDialog(db_qkan):
            self.log.error_code(
                f'{self.__class__.__name__}: '
                f'prepareDialog fehlgeschlagen')
            raise QkanError

        # Laden der Plausibilitätsdaten zu Zustandsklassen
        reflist_zustandfile = os.path.join(
            pluginDirectory("qkan"), "templates", "Plausi_Zustandsklassen.csv"
        )

        with open(reflist_zustandfile, "r") as fin:
            dr = csv.reader(fin, delimiter=";")

            to_db = []


            for a, b, c, d, e in dr:
                c = [None if x.strip().upper() == "NULL" or not x.strip() else x.strip() for x in c.split(",")]
                d = [None if x.strip().upper() == "NULL" or not x.strip() else x.strip() for x in d.split(",")]
                e = [None if x.strip().upper() == "NULL" or not x.strip() else x.strip() for x in e.split(",")]

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

        db_qkan.sql(""" UPDATE reflist_zustand SET charakterisierung1 = NULL WHERE charakterisierung1 = ''; """)
        db_qkan.sql(""" UPDATE reflist_zustand SET charakterisierung2 = NULL WHERE charakterisierung2 = ''; """)
        db_qkan.sql(""" UPDATE reflist_zustand SET bereich = NULL WHERE bereich = ''; """)
        db_qkan.commit()


    def _doplausi(self, db_qkan: DBConnection = None, is_test: bool = False) -> bool:
        """Start der Plausibilitätsabragen

        Einspringpunkt für Test
        """

        plau = PlausiTask(db_qkan)
        plau.run()

        self.log.debug("Closed DB")

        # Anzeige der Attributtabelle, nicht im Testmodus
        if not is_test:
            project = QgsProject.instance()
            layers = project.mapLayersByName(enums.LAYERBEZ.FEHLERLISTE.value)
            if layers is None or layers == []:
                self.log.error_code(
                    f'{self.__class__.__name__}: '
                    f'Layer {enums.LAYERBEZ.FEHLERLISTE.value} fehlt!')
                raise QkanError
            self.iface.showAttributeTable(layers[0])

        return True
