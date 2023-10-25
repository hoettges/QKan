import os
import shutil
from pathlib import Path

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import pluginDirectory

from qkan import QKan, enums, get_default_dir
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import read_qml, eval_node_types, fehlermeldung
from qkan.plugin import QKanPlugin
from qkan.tools.k_qgsadapt import qgsadapt

from ._export import ExportTask
from ._import import ImportTask
from ._results import ResultsTask
from .application_dialog import ExportDialog, ImportDialog, ResultsDialog

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip

# logger = logging.getLogger("QKan.he8.application")


class He8Porter(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        default_dir = get_default_dir()
        self.log.debug(f"He8Porter: default_dir: {default_dir}")

        self.export_dlg = ExportDialog(default_dir, tr=self.tr)
        self.import_dlg = ImportDialog(default_dir, tr=self.tr)
        self.results_dlg = ResultsDialog(default_dir, tr=self.tr)


    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon_export = ":/plugins/qkan/he8porter/res/icon_export.png"
        QKan.instance.add_action(
            icon_export,
            text=self.tr("Export nach Hystem-Extran 8"),
            callback=self.run_export,
            parent=self.iface.mainWindow(),
        )
        icon_import = ":/plugins/qkan/he8porter/res/icon_import.png"
        QKan.instance.add_action(
            icon_import,
            text=self.tr("Import aus Hystem-Extran 8"),
            callback=self.run_import,
            parent=self.iface.mainWindow(),
        )
        icon_results = ":/plugins/qkan/he8porter/res/icon_results.png"
        QKan.instance.add_action(
            icon_results,
            text=self.tr("Ergebnisse aus Hystem-Extran 8"),
            callback=self.run_results,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.export_dlg.close()
        self.import_dlg.close()
        self.results_dlg.close()

    def run_export(self) -> None:
        """Anzeigen des Exportformulars und anschließender Start des Exports in eine HE8-Datenbank"""

        # noinspection PyArgumentList

        with DBConnection() as db_qkan:
            dbname = db_qkan.dbname

            # Datenbankpfad in Dialog übernehmen
            self.export_dlg.tf_database.setText(dbname)

            if not self.export_dlg.prepareDialog(db_qkan):
                return

        # Formular anzeigen
        self.export_dlg.show()

        # Im Formular wurde [OK] geklickt
        if self.export_dlg.exec_():

            # Read from form and save to config
            QKan.config.database.qkan = self.export_dlg.tf_database.text()
            QKan.config.he8.export_file = self.export_dlg.tf_exportdb.text()
            QKan.config.he8.template = self.export_dlg.tf_template.text()

            QKan.config.check_export.haltungen = (
                self.export_dlg.cb_haltungen.isChecked()
            )
            QKan.config.check_export.schaechte = (
                self.export_dlg.cb_schaechte.isChecked()
            )
            QKan.config.check_export.auslaesse = (
                self.export_dlg.cb_auslaesse.isChecked()
            )
            QKan.config.check_export.speicher = self.export_dlg.cb_speicher.isChecked()
            QKan.config.check_export.pumpen = self.export_dlg.cb_pumpen.isChecked()
            QKan.config.check_export.wehre = self.export_dlg.cb_wehre.isChecked()
            QKan.config.check_export.drosseln = self.export_dlg.cb_drosseln.isChecked()
            QKan.config.check_export.schieber = self.export_dlg.cb_schieber.isChecked()
            QKan.config.check_export.qregler = self.export_dlg.cb_qregler.isChecked()
            QKan.config.check_export.hregler = self.export_dlg.cb_hregler.isChecked()
            QKan.config.check_export.grundseitenauslaesse = self.export_dlg.cb_grundseitenauslaesse.isChecked()
            QKan.config.check_export.flaechen = self.export_dlg.cb_flaechen.isChecked()
            QKan.config.check_export.rohrprofile = (
                self.export_dlg.cb_rohrprofile.isChecked()
            )
            QKan.config.check_export.abflussparameter = (
                self.export_dlg.cb_abflussparameter.isChecked()
            )
            QKan.config.check_export.bodenklassen = (
                self.export_dlg.cb_bodenklassen.isChecked()
            )
            QKan.config.check_export.einleitdirekt = (
                self.export_dlg.cb_einleitdirekt.isChecked()
            )
            QKan.config.check_export.aussengebiete = (
                self.export_dlg.cb_aussengebiete.isChecked()
            )
            QKan.config.check_export.einzugsgebiete = (
                self.export_dlg.cb_einzugsgebiete.isChecked()
            )
            QKan.config.check_export.tezg = self.export_dlg.cb_tezg.isChecked()
            QKan.config.check_export.tezg_hf = self.export_dlg.cb_tezg_hf.isChecked()

            QKan.config.check_export.append = True # self.export_dlg.rb_append.isChecked()
            # QKan.config.check_export.update = self.export_dlg.rb_update.isChecked()

            teilgebiete = [
                _.text() for _ in self.export_dlg.lw_teilgebiete.selectedItems()
            ]
            QKan.config.selections.teilgebiete = teilgebiete

            QKan.config.save()

            self._doexport()

    def _doexport(self) -> bool:
        """Start des Export in eine HE8-Datenbank

        Einspringpunkt für Test
        """

        # Zieldatenbank aus Vorlage kopieren
        if os.path.exists(QKan.config.he8.template):
            try:
                shutil.copyfile(QKan.config.he8.template, QKan.config.he8.export_file)
            except BaseException:
                fehlermeldung(
                    "Fehler in Export nach HE8",
                    "Fehler beim Kopieren der Vorlage: \n   {QKan.config.he8.template}\n"
                    + "nach Ziel: {QKan.config.he8.export_file}\n",
                )

        """Attach SQLite-Database with HE8 Data"""
        sql = f'ATTACH DATABASE "{QKan.config.he8.export_file}" AS he'

        # Für Test muss noch die Datenbankverbindung hergestellt werden
        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:

            if not db_qkan.sql(sql, "He8Porter.run_export_to_he8 Attach HE8"):
                self.log.error(
                    f"Fehler in He8Porter._doexport(): Attach fehlgeschlagen: {QKan.config.he8.export_file}"
                )
                return False

            # Run export
            ExportTask(db_qkan, QKan.config.selections.teilgebiete).run()

        self.log.debug("Closed DB")

        return True

    def run_import(self) -> None:
        """Anzeigen des Importformulars HE8 und anschließender Start des Import aus einer HE8-Datenbank"""

        self.import_dlg.show()

        if self.import_dlg.exec_():
            # Read from form and save to config
            QKan.config.database.qkan = self.import_dlg.tf_database.text()
            QKan.config.project.file = self.import_dlg.tf_project.text()
            QKan.config.he8.import_file = self.import_dlg.tf_import.text()

            QKan.config.check_import.haltungen = (
                self.import_dlg.cb_haltungen.isChecked()
            )
            QKan.config.check_import.schaechte = (
                self.import_dlg.cb_schaechte.isChecked()
            )
            QKan.config.check_import.auslaesse = (
                self.import_dlg.cb_auslaesse.isChecked()
            )
            QKan.config.check_import.speicher = self.import_dlg.cb_speicher.isChecked()
            QKan.config.check_import.pumpen = self.import_dlg.cb_pumpen.isChecked()
            QKan.config.check_import.wehre = self.import_dlg.cb_wehre.isChecked()
            QKan.config.check_import.drosseln = self.import_dlg.cb_drosseln.isChecked()
            QKan.config.check_import.schieber = self.import_dlg.cb_schieber.isChecked()
            QKan.config.check_import.qregler = self.import_dlg.cb_qregler.isChecked()
            QKan.config.check_import.hregler = self.import_dlg.cb_hregler.isChecked()
            QKan.config.check_import.grundseitenauslaesse = self.import_dlg.cb_grundseitenauslaesse.isChecked()
            QKan.config.check_import.flaechen = self.import_dlg.cb_flaechen.isChecked()
            QKan.config.check_import.rohrprofile = (
                self.import_dlg.cb_rohrprofile.isChecked()
            )
            QKan.config.check_import.abflussparameter = (
                self.import_dlg.cb_abflussparameter.isChecked()
            )
            QKan.config.check_import.bodenklassen = (
                self.import_dlg.cb_bodenklassen.isChecked()
            )
            QKan.config.check_import.einleitdirekt = (
                self.import_dlg.cb_einleitdirekt.isChecked()
            )
            QKan.config.check_import.aussengebiete = (
                self.import_dlg.cb_aussengebiete.isChecked()
            )
            QKan.config.check_import.einzugsgebiete = (
                self.import_dlg.cb_einzugsgebiete.isChecked()
            )

            QKan.config.check_import.tezg_ef = self.import_dlg.cb_tezg_ef.isChecked()
            QKan.config.check_import.tezg_hf = self.import_dlg.cb_tezg_hf.isChecked()
            QKan.config.check_import.tezg_tf = self.import_dlg.cb_tezg_tf.isChecked()

            QKan.config.check_import.append = True # self.import_dlg.rb_append.isChecked()
            # QKan.config.check_import.update = self.import_dlg.rb_update.isChecked()

            if not QKan.config.he8.import_file:
                fehlermeldung("Fehler beim Import", "Es wurde keine Datei ausgewählt!")
                self.iface.messageBar().pushMessage(
                    "Fehler beim Import",
                    "Es wurde keine Datei ausgewählt!",
                    level=Qgis.Critical,
                )
                return
            else:
                crs: QgsCoordinateReferenceSystem = self.import_dlg.pw_epsg.crs()

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

                    self._doimport()


    def _doimport(self) -> bool:
        """Start des Import aus einer HE8-Datenbank

        Einspringpunkt für Test
        """

        self.log.info("Creating DB")
        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:
            if not db_qkan.connected:
                fehlermeldung(
                    "Fehler im HE8-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im HE8-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )
                return False

            # Attach SQLite-Database with HE8 Data
            sql = f'ATTACH DATABASE "{QKan.config.he8.import_file}" AS he'
            if not db_qkan.sql(sql, "He8Porter.run_import_to_he8 Attach HE8"):
                self.log.error(
                    f"Fehler in He8Porter._doimport(): Attach fehlgeschlagen: {QKan.config.he8.import_file}"
                )
                return False

            #
            # sql = 'SELECT count(*) AS anz FROM he.Rohr'
            # db_qkan.sql(sql)
            # datatest = db_qkan.fetchone()
            # self.log.debug(f"Testdaten:\n{datatest}")
            #
            #
            self.log.info("DB creation finished, starting importer")
            imp = ImportTask(db_qkan)
            imp.run()
            del imp

            eval_node_types(db_qkan)  # in qkan.database.qkan_utils

            # Write and load new project file, only if new project
            if QgsProject.instance().fileName() == '':
                QKan.config.project.template = str(
                    Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
                )
                specific_qmls = {
                    'specificqmlpath': 'qml/he',
                    'Drosseln': 'drosseln.qml',
                    'Schieber': 'schieber.qml',
                    'Grund-/Seitenauslässe': 'grund_seitenauslaesse.qml',
                    'H-Regler': 'h_regler.qml',
                    'Q-Regler': 'q_regler.qml',
                    'Pumpen': 'pumpen.qml',
                    'Wehre': 'wehre.qml',
                    'Abflussparameter': 'abflussparameter.qml',
                }
                qgsadapt(
                    QKan.config.database.qkan,
                    db_qkan,
                    QKan.config.project.file,
                    QKan.config.project.template,
                    QKan.config.epsg,
                )

                # Load generated project
                # noinspection PyArgumentList
                project = QgsProject.instance()
                project.read(QKan.config.project.file)
                project.reloadAllLayers()

        self.log.debug("Closed DB")

        return True

    def run_results(self):
        """Öffnen des Formulars zum Einlesen der Simulationsergebnisse aus HE"""

        # show the dialog
        self.results_dlg.show()
        # Run the dialog event loop
        result = self.results_dlg.exec_()
        # See if OK was pressed
        if result:

            # Daten aus Formular übernehmen
            database_ErgHE = self.results_dlg.tf_resultsDB.text()
            qml_file_results = self.results_dlg.tf_qmlfile.text()

            if self.results_dlg.rb_uebh.isChecked():
                qml_choice = enums.QmlChoice.UEBH
            elif self.results_dlg.rb_uebvol.isChecked():
                qml_choice = enums.QmlChoice.UEBVOL
            elif self.results_dlg.rb_userqml.isChecked():
                qml_choice = enums.QmlChoice.USERQML
            elif self.results_dlg.rb_none.isChecked():
                qml_choice = enums.QmlChoice.NONE
            else:
                fehlermeldung("Fehler im Programmcode (2)", "Nicht definierte Option")
                return False
            # Konfigurationsdaten schreiben

            QKan.config.he8.results_file = database_ErgHE
            QKan.config.he8.qml_choice = qml_choice
            QKan.config.he8.qml_file_results = qml_file_results

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(f"""QKan-Modul Aufruf importResults()""")

            ResultsTask().run()
