import logging
import os
import webbrowser
from pathlib import Path
from typing import Callable, List, Optional

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QWidget,
    QLineEdit,
    QListWidget,
)
from qgis.utils import pluginDirectory

from qkan import QKan, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

logger = logging.getLogger("QKan.datacheck.application_dialog")


def click_help() -> None:
    """Reaktion auf Klick auf Help-Schaltfläche"""
    helpfile = (
        Path(__file__).parent / ".." / "doc/sphinx/build/html/Qkan_Formulare.html"
    )
    webbrowser.open_new_tab(str(helpfile) + "#erzeugen-der-unbefestigten-flachen")


class _Dialog(QDialog):
    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)
        self.default_dir = default_dir
        logger.debug(
            f"datacheck.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr


IMPORT_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_datacheck.ui")
)


class PlausiDialog(_Dialog, IMPORT_CLASS):  # type: ignore
    lw_themen: QListWidget
    le_anzahl: QLineEdit

    def __init__(
        self,
        default_dir: str,
        tr: Callable,
        parent: Optional[QWidget] = None
        ):
        # noinspection PyCallByClass,PyArgumentList
        super().__init__(default_dir, tr, parent)

    def run_plausi(self) -> None:
        """Anzeigen des Formulars zur Auswahl der durchzuführenden Plausibilitätsprüfungen und anschließender Start"""

        self.plausi_dlg.show()

        if self.plausi_dlg.exec_():
            # Read from form and save to config
            QKan.config.mu.database = self.plausi_dlg.tf_database.text()
            QKan.config.project.file = self.plausi_dlg.tf_project.text()
            QKan.config.mu.import_file = self.plausi_dlg.tf_import.text()

            QKan.config.check_import.haltungen = (
                self.plausi_dlg.cb_haltungen.isChecked()
            )
            QKan.config.check_import.schaechte = (
                self.plausi_dlg.cb_schaechte.isChecked()
            )
            QKan.config.check_import.auslaesse = (
                self.plausi_dlg.cb_auslaesse.isChecked()
            )
            QKan.config.check_import.speicher = self.plausi_dlg.cb_speicher.isChecked()
            QKan.config.check_import.pumpen = self.plausi_dlg.cb_pumpen.isChecked()
            QKan.config.check_import.wehre = self.plausi_dlg.cb_wehre.isChecked()
            QKan.config.check_import.flaechen = self.plausi_dlg.cb_flaechen.isChecked()
            QKan.config.check_import.rohrprofile = (
                self.plausi_dlg.cb_rohrprofile.isChecked()
            )
            QKan.config.check_import.abflussparameter = (
                self.plausi_dlg.cb_abflussparameter.isChecked()
            )
            QKan.config.check_import.bodenklassen = (
                self.plausi_dlg.cb_bodenklassen.isChecked()
            )
            QKan.config.check_import.einleitdirekt = (
                self.plausi_dlg.cb_einleitdirekt.isChecked()
            )
            QKan.config.check_import.aussengebiete = (
                self.plausi_dlg.cb_aussengebiete.isChecked()
            )
            QKan.config.check_import.einzugsgebiete = (
                self.plausi_dlg.cb_einzugsgebiete.isChecked()
            )

            # QKan.config.check_import.tezg_ef = self.plausi_dlg.cb_tezg_ef.isChecked()
            QKan.config.check_import.tezg_hf = self.plausi_dlg.cb_tezg_hf.isChecked()
            # QKan.config.check_import.tezg_tf = self.plausi_dlg.cb_tezg_tf.isChecked()

            QKan.config.check_import.append = self.plausi_dlg.rb_append.isChecked()
            QKan.config.check_import.update = self.plausi_dlg.rb_update.isChecked()

            crs: QgsCoordinateReferenceSystem = self.plausi_dlg.pw_epsg.crs()

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

            if not QKan.config.mu.import_file:
                fehlermeldung("Fehler beim Import", "Es wurde keine Datei ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde keine Datei ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                self._doplausi()

    def _doplausi(self) -> bool:
        """Start des Import aus einer HE8-Datenbank

        Einspringpunkt für Test
        """

        self.log.info("Creating DB")
        db_qkan = DBConnection(dbname=QKan.config.mu.database, epsg=QKan.config.epsg)

        if not db_qkan:
            fehlermeldung(
                "Fehler im Mike+-Import",
                f"QKan-Datenbank {QKan.config.mu.database} wurde nicht gefunden!\nAbbruch!",
            )
            self.iface.messageBar().pushMessage(
                "Fehler im Mike+-Import",
                f"QKan-Datenbank {QKan.config.mu.database} wurde nicht gefunden!\nAbbruch!",
                level=Qgis.Critical,
            )
            return False

        # Attach SQLite-Database with Mike+ Data
        sql = f'ATTACH DATABASE "{QKan.config.mu.import_file}" AS mu'
        if not db_qkan.sql(sql, "Plausi.run_import_to_mu Attach Mike+"):
            logger.error(
                f"Fehler in Plausi._doplausi(): Attach fehlgeschlagen: {QKan.config.mu.import_file}"
            )
            return False

        self.log.info("DB creation finished, starting importer")
        imp = ImportTask(db_qkan)
        imp.run()

        QKan.config.project.template = str(
            Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
        )
        qgsadapt(
            QKan.config.project.template,
            QKan.config.mu.database,
            db_qkan,
            QKan.config.project.file,
            QKan.config.epsg,
        )

        del db_qkan
        self.log.debug("Closed DB")

        # Load generated project
        # noinspection PyArgumentList
        project = QgsProject.instance()
        project.read(QKan.config.project.file)
        project.reloadAllLayers()

        # TODO: Some layers don't have a valid EPSG attached or wrong coordinates

        return True
