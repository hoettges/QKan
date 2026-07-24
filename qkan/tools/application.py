"""
Flaechenzuordnungen
Diverse Tools zur QKan-Datenbank
"""
import os
from typing import Optional, cast

from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.PyQt.QtWidgets import QApplication

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgisInterface
from qgis.utils import iface
from PyQt5.QtGui import QPixmap

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import (
    get_database_QKan,
    get_editable_layers,
    list_selected_items,
)
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
from .dialogs.dbAdapt import DbAdaptDialog
from .dialogs.empty_db import EmptyDBDialog
from .dialogs.filepath import QgsFileDialog
from .dialogs.bericht import QgsBerichtDialog
from .dialogs.befahrung import QgsBefahrungDialog
from .dialogs.help import QgsHelpDialog
from .dialogs.layersadapt import LayersAdaptDialog
from .dialogs.qgsadapt import QgsAdaptDialog
from .dialogs.qkanoptions import QKanOptionsDialog
from .dialogs.read_data import ReadData
from .dialogs.runoffparams import RunoffParamsDialog
from .dialogs.zoom_clipboard import QgsZoomDialog
from .k_filepath import setfilepath
from .k_bericht import bericht
from .k_layersadapt import layersadapt
from .k_qgsadapt import qgsadapt
from .k_runoffparams import setRunoffparams
from .k_befahrung import setbefahrung

from qkan.tools.k_schadenstexte import Schadenstexte
from qkan.tools.qkan_utils import get_database_QKan
from ..utils import get_logger, QkanError, QkanDbError

logger = get_logger("QKan.tools.application")

class QKanTools(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.database_name: Optional[str] = None

        self.dlgla = LayersAdaptDialog(self)
        self.dlgop = QKanOptionsDialog(self)
        self.dlgpr = QgsAdaptDialog(self)
        self.dlgro = RunoffParamsDialog(self)
        self.dlged = EmptyDBDialog(self)
        self.dlgrd = ReadData(self, proceed=True)
        self.dlgrc = ReadData(self, proceed=False)
        self.dlgdb = DbAdaptDialog(self)
        self.dlghp = QgsHelpDialog(self)
        self.dlgfp = QgsFileDialog(self)
        self.dlgbf = QgsBefahrungDialog(self)
        self.dlgzc = QgsZoomDialog(self)
        self.dlgb = QgsBerichtDialog(self)
        self.iface = iface

        self.clip = QApplication.clipboard()

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_qgsadapt_path = ":/plugins/qkan/tools/res/icon_qgsadapt.png"
        QKan.instance.add_action(
            icon_qgsadapt_path,
            text=self.tr("QKan-Projektdatei übernehmen"),
            toolbar='QKan-Allgemein',
            callback=self.run_qgsadapt,
            parent=self.iface.mainWindow(),
        )

        icon_layersadapt_path = ":/plugins/qkan/tools/res/icon_layersadapt.png"
        QKan.instance.add_action(
            icon_layersadapt_path,
            text=self.tr("QKan-Projekt anpassen"),
            toolbar='QKan-Allgemein',
            callback=self.run_layersadapt,
            parent=self.iface.mainWindow(),
        )

        icon_qkanoptions_path = ":/plugins/qkan/tools/res/icon_qkanoptions.png"
        QKan.instance.add_action(
            icon_qkanoptions_path,
            text=self.tr("Optionen"),
            toolbar='QKan-Allgemein',
            callback=self.run_qkanoptions,
            parent=self.iface.mainWindow(),
        )

        icon_runoffparams_path = ":/plugins/qkan/tools/res/icon_runoffparams.png"
        QKan.instance.add_action(
            icon_runoffparams_path,
            text=self.tr("Oberflächenabflussparameter eintragen"),
            toolbar='QKan-Flächenbearbeitung',
            callback=self.run_runoffparams,
            parent=self.iface.mainWindow(),
        )

        # TODO: Translations
        icon_emptyDB_path = ":/plugins/qkan/tools/res/icon_emptyDB.png"
        QKan.instance.add_action(
            icon_emptyDB_path,
            text=self.tr("Neue QKan-Datenbank erstellen"),
            toolbar='QKan-Allgemein',
            callback=self.dlged.run,
            parent=self.iface.mainWindow(),
        )

        icon_readCheck_path = ":/plugins/qkan/tools/res/icon_readCheck.png"
        QKan.instance.add_action(
            icon_readCheck_path,
            text=self.tr("Tabellendaten aus Clipboard: Zuordnung anzeigen"),
            toolbar='QKan-Allgemein',
            callback=self.dlgrc.run,
            parent=self.iface.mainWindow(),
        )

        icon_readData_path = ":/plugins/qkan/tools/res/icon_readData.png"
        QKan.instance.add_action(
            icon_readData_path,
            text=self.tr("Tabellendaten aus Clipboard einfügen"),
            toolbar='QKan-Allgemein',
            callback=self.dlgrd.run,
            parent=self.iface.mainWindow(),
        )

        icon_dbAdapt_path = ":/plugins/qkan/tools/res/icon_dbAdapt.png"
        QKan.instance.add_action(
            icon_dbAdapt_path,
            text=self.tr("QKan-Datenbank aktualisieren"),
            toolbar='QKan-Allgemein',
            callback=self.run_dbAdapt,
            parent=self.iface.mainWindow(),
        )

        icon_file_path = ":/plugins/qkan/tools/res/icon_filepath.png"
        QKan.instance.add_action(
            icon_file_path,
            text=self.tr("Dateipfade suchen"),
            toolbar='QKan-Allgemein',
            callback=self.run_filepath,
            parent=self.iface.mainWindow(),
        )

        icon_file_path = ":/plugins/qkan/tools/res/icon_zoom_clipboard.png"
        self.action = QKan.instance.add_action(
            icon_file_path,
            text=self.tr("Zur Auswahl zoomen"),
            toolbar='QKan-Allgemein',
            callback=self.run_zoom_clipboard,
            parent=self.iface.mainWindow(),
        )
        self.action.setCheckable(True)
        self.action.toggled.connect(self.run_zoom_clipboard)


        icon_befahrung = ":/plugins/qkan/tools/res/icon_befahrung.png"
        QKan.instance.add_action(
            icon_befahrung,
            text=self.tr("Inspektionsdaten anpassen"),
            toolbar='QKan-Allgemein',
            callback=self.run_befahrung,
            parent=self.iface.mainWindow(),
        )

        icon_bericht = ":/plugins/qkan/tools/res/icon_bericht.png"
        QKan.instance.add_action(
            icon_bericht,
            text=self.tr("Haltungsbericht"),
            toolbar='QKan-Allgemein',
            callback=self.run_bericht,
            parent=self.iface.mainWindow(),
        )

        icon_help_path = ":/plugins/qkan/tools/res/icon_help.png"
        QKan.instance.add_action(
            icon_help_path,
            text=self.tr("Über QKan"),
            toolbar='QKan-Allgemein',
            callback=self.run_help,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlgla.close()
        self.dlgop.close()
        self.dlgpr.close()
        self.dlgro.close()
        self.dlged.close()
        self.dlghp.close()
        # self.dlgrd.close()                    # doesn't use a form
        self.dlgdb.close()
        self.dlgfp.close()

    def run_qgsadapt(self) -> None:
        """Erstellen einer Projektdatei aus einer Vorlage"""

        # Prüfen, ob Projekt gespeichert und kein Layer bearbeitbar
        project = QgsProject.instance()
        if project.isDirty():
            logger.error_user('Das Projekt wurde geändert. Bitte speichern oder neu laden!')
            return
        if len(lis := get_editable_layers()) > 0:
            logger.error_user(f'Es darf kein Layer im Modus "bearbeitbar" sein! Bitte für '
                              f'Layer {list(lis)[0]} umschalten'
            )
            return

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        get_database_QKan(silent=True)
        self.database_name = QKan.config.database.qkan

        if self.database_name is not None and self.database_name != '':
            self.default_dir = os.path.dirname(
                self.database_name
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.database_name = QKan.config.database.qkan
            self.default_dir = os.path.dirname(self.database_name)
        self.dlgpr.tf_qkanDB.setText(self.database_name)

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgpr.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # Status initialisieren
        self.dlgpr.click_apply_template()

        # show the dialog
        self.dlgpr.show()
        # Run the dialog event loop
        result = self.dlgpr.exec_()

        # See if OK was pressed
        if result:
            # Inhalte aus Formular lesen --------------------------------------------------------------

            self.database_name = self.dlgpr.tf_qkanDB.text()
            project_file: str = self.dlgpr.tf_projectFile.text()
            self.apply_qkan_template = self.dlgpr.cb_applyQKanTemplate.isChecked()

            # QKanTemplate nur, wenn nicht Option "QKan_Standard_anwenden" gewählt
            if self.apply_qkan_template:
                project_template: str = os.path.join(QKan.template_dir, "Projekt.qgs")
            else:
                project_template = self.dlgpr.tf_projectTemplate.text()

            # Konfigurationsdaten schreiben -----------------------------
            if self.database_name is not None and self.database_name != '':
                QKan.config.database.qkan = self.database_name
            QKan.config.project.file = project_file
            QKan.config.project.template = project_template
            QKan.config.tools.apply_qkan_template = self.apply_qkan_template

            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                qgsadapt(
                    "{project_template}",
                    "{self.database_name}",
                    N/A,
                    "{project_file}",
                    epsg = {QKan.config.epsg}, 
                )"""
            )

            # ------------------------------------------------------------------------------
            # Datenbankverbindungen
            if not self.database_name:
                return

            with DBConnection(dbname=self.database_name) as db_qkan:
                if not db_qkan.isCurrentDbVersion:
                    logger.warning('QKan-Datenbank wurde mit einer älteren Version erstellt.\n'
                                   'Bitte aktualisieren Sie zuerst die Datenbank! ')
                    return None
                if not db_qkan.connected:
                    logger.error_user(f"Die QKan-Datenbank {self.database_name} wurde nicht gefunden\nAbbruch!"                    )
                    return None

                qgsadapt(
                    self.database_name,
                    db_qkan,
                    project_file,
                    project_template,
                    epsg=QKan.config.epsg,
                )

            # ------------------------------------------------------------------------------
            # Abschluss: Projektdatei neu laden

            project.clear()
            project.read(project_file)  # read the new project file

            self.iface.mainWindow().statusBar().clearMessage()
            self.iface.messageBar().pushMessage(
            "Information",
            "Projektdatei wurde angepasst und neu geladen.",
            level=Qgis.MessageLevel.Info,
            )

    def run_qkanoptions(self) -> None:
        """Bearbeitung allgemeiner QKan-Optionen"""

        # Formularfelder setzen -------------------------------------------------------------------------

        # Fangradius für Anfang der Anbindungslinie
        self.dlgop.tf_fangradius.setText(str(QKan.config.fangradius))

        # Abstand zwischen Zustandstexten
        self.dlgop.tf_abstand_zustandstexte.setText(str(QKan.config.zustand.abstand_zustandstexte))

        # Abstand zwischen Blöcken von Zustandstexten
        self.dlgop.tf_abstand_zustandsbloecke.setText(str(QKan.config.zustand.abstand_zustandsbloecke))

        # Stützstellen der Verbindungslinie zum Zustandstext
        self.dlgop.tf_abstand_knoten_anf.setText(str(QKan.config.zustand.abstand_knoten_anf))
        self.dlgop.tf_abstand_knoten_1.setText(str(QKan.config.zustand.abstand_knoten_1))
        self.dlgop.tf_abstand_knoten_2.setText(str(QKan.config.zustand.abstand_knoten_2))
        self.dlgop.tf_abstand_knoten_end.setText(str(QKan.config.zustand.abstand_knoten_end))

        # Mindestflächengröße
        self.dlgop.tf_mindestflaeche.setText(str(QKan.config.mindestflaeche))

        # Maximalzahl Schleifendurchläufe
        self.dlgop.tf_max_loops.setText(str(QKan.config.max_loops))

        # Optionen zum Typ der QKan-Datenbank
        if QKan.config.database.type == enums.QKanDBChoice.SPATIALITE:
            self.dlgop.rb_spatialite.setChecked(True)
        # elif QKan.config.database.type == enums.QKanDBChoice.POSTGIS:
        # self.dlgop.rb_postgis.setChecked(True)

        self.dlgop.tf_fotopath.setText(QKan.config.fotoRootPath)
        self.dlgop.tf_videopath.setText(QKan.config.videoRootPath)

        # noinspection PyCallByClass,PyArgumentList
        self.dlgop.qsw_epsg.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(QKan.config.epsg))

        self.dlgop.tf_logeditor.setText(QKan.config.tools.logeditor)

        # Textfeld für Editor deaktivieren, falls leer:
        status_logeditor = QKan.config.tools.logeditor == ""
        self.dlgop.tf_logeditor.setEnabled(status_logeditor)

        # Check Triggers
        if get_database_QKan():                     # prüfen, ob Projekt geöffnet
            with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:
                if not db_qkan.connected:
                    self.log.error(f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    )
                    raise QkanDbError

                db_qkan.loadmodule('tools')

                # Test Trigger Referenztabellen
                sql = 'tools_list_triggers_ref'
                if not db_qkan.sqlyml(
                    sql,
                    sql,
                ):
                    self.log.error_data('Trigger für Referenztabellen konnte nicht gelesen werden')
                    raise QkanDbError

                data = db_qkan.fetchall()
                self.dlgop.cb_trigger_referenztabellen.setChecked(len(data) > 2)

                # Test Trigger Fang auf Schacht bei Neuerstellung oder Bearbeitung einer Haltung
                sql = 'tools_check_triggers_fang_schacht'
                if not db_qkan.sqlyml(
                    sql,
                    sql,
                ):
                    self.log.error_data('Trigger für Schachtfang konnte nicht gelesen werden')
                    raise QkanDbError

                data = [el[0] for el in db_qkan.fetchall()]
                if len(data) >= 1:
                    self.dlgop.cb_trigger_fang_schacht.setChecked(True)
                    # Trigger Fang auf Schacht bei Bearbeitung einer Haltung, scheint nicht zu funktionieren ...
                    # if 'trig_mod_hal_all' in data:
                    #     self.dlgop.rb_trigger_fang_schacht_all.setChecked(True)
                    # elif 'trig_mod_hal_nul' in data:
                    #     self.dlgop.rb_trigger_fang_schacht_nul.setChecked(True)
                    # else:
                    #     self.log.error_code('Option Datenübernahme bei Fang Schacht fehlerhaft\n'
                    #                         f'{data=}')
                    #     raise QkanError

        # show the dialog
        self.dlgop.show()
        # Run the dialog event loop
        result = self.dlgop.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            QKan.config.fangradius = float(self.dlgop.tf_fangradius.text())
            QKan.config.zustand.abstand_zustandstexte = float(self.dlgop.tf_abstand_zustandstexte.text().replace(",", "."))
            QKan.config.zustand.abstand_zustandsbloecke = float(self.dlgop.tf_abstand_zustandsbloecke.text().replace(",", "."))
            QKan.config.zustand.abstand_knoten_anf = float(self.dlgop.tf_abstand_knoten_anf.text())
            QKan.config.zustand.abstand_knoten_1 = float(self.dlgop.tf_abstand_knoten_1.text())
            QKan.config.zustand.abstand_knoten_2 = float(self.dlgop.tf_abstand_knoten_2.text())
            QKan.config.zustand.abstand_knoten_end = float(self.dlgop.tf_abstand_knoten_end.text())
            QKan.config.max_loops = int(self.dlgop.tf_max_loops.text())
            QKan.config.mindestflaeche = float(self.dlgop.tf_mindestflaeche.text())
            QKan.config.logeditor = self.dlgop.tf_logeditor.text().strip()

            QKan.config.fotoRootPath = self.dlgop.tf_fotopath.text()
            QKan.config.videoRootPath = self.dlgop.tf_videopath.text()

            print(self.dlgop.tf_videopath.text())
            print(type(self.dlgop.tf_videopath.text()))

            if self.dlgop.rb_spatialite.isChecked():
                QKan.config.database.type = enums.QKanDBChoice.SPATIALITE
            # elif self.dlgop.rb_postgis.isChecked():
            # QKan.config.database.type = enums.QKanDBChoice.POSTGIS
            else:
                logger.error_code(
                    "tools.application.run: "
                    f"Fehlerhafte Option: \ndatenbanktyp = {QKan.config.database.type}",
                )
                raise QkanError
            QKan.config.epsg = int(self.dlgop.qsw_epsg.crs().postgisSrid())

            QKan.config.save()

            # Set/Drop Triggers
            if get_database_QKan():  # prüfen, ob Projekt geöffnet
                with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:
                    if not db_qkan.connected:
                        self.log.error(f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                        )
                        raise QkanDbError

                    db_qkan.loadmodule('tools')

                    if self.dlgop.cb_textposition_akt.isChecked():
                        Schadenstexte.setschadenstexte_haltungen(db_qkan)
                        Schadenstexte.setschadenstexte_schaechte(db_qkan)
                        Schadenstexte.setschadenstexte_anschlussleitungen(db_qkan)

                    # Trigger Referenztabellen
                    triggerlist = [
                        'profile', 'entwart', 'simstatus', 'material', 'abflussparameter']

                    for trigger in triggerlist:
                        if self.dlgop.cb_trigger_referenztabellen.isChecked():
                            sql = f'tools_create_trig_ref_{trigger}'
                        else:
                            sql = f'tools_drop_trig_ref_{trigger}'

                        if not db_qkan.sqlyml(
                            sql,
                            sql,
                        ):
                            self.log.error_data(f'Trigger für Referenztabelle tools_create_trigger_{trigger} '
                                                f'konnte nicht erzeugt werden')
                            raise QkanDbError

                    # Trigger Fang auf Schacht bei Neuerstellung einer Haltung
                    if self.dlgop.cb_trigger_fang_schacht.isChecked():
                        sql = f'tools_create_trig_new_hal'
                    else:
                        sql = f'tools_drop_trig_new_hal'
                    if not db_qkan.sqlyml(
                        sql,
                        sql,
                    ):
                        self.log.error_data(f'Trigger für Schachtfang bei neuer Haltunge konnte nicht geändert werden')
                        raise QkanDbError


                    # Trigger Fang auf Schacht bei Bearbeitung einer Haltung, scheint nicht zu funktionieren ...
                    # sqllis = ['tools_drop_trig_mod_hal_nul', 'tools_drop_trig_mod_hal_all']
                    # if self.dlgop.cb_trigger_fang_schacht.isChecked():
                    #     if self.dlgop.rb_trigger_fang_schacht_all.isChecked():
                    #         sqllis.append(f'tools_create_trig_mod_hal_all')
                    #     elif self.dlgop.rb_trigger_fang_schacht_nul.isChecked():
                    #         sqllis.append(f'tools_create_trig_mod_hal_nul')
                    # else:
                    #     pass                # nur Trigger löschen
                    # for sql in sqllis:
                    #     if not db_qkan.sqlyml(
                    #         sql,
                    #         sql,
                    #     ):
                    #         self.log.error_data(f'Trigger für Schachtfang bei Haltungsänderung konnte nicht geändert werden')
                    #         raise QkanDbError

                    db_qkan.commit()

    def run_runoffparams(self) -> None:
        """Berechnen und Eintragen der Oberflächenabflussparameter in die Tabelle flaechen"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({
                   enums.LAYERBEZ.EINZELFLAECHEN.value,
               } & get_editable_layers()) > 0:
            logger.warning_user(
                "Bedienerfehler: "
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!'
            )
            return

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        get_database_QKan()
        database_qkan = QKan.config.database.qkan
        if not database_qkan:
            self.log.error(
                "tools.application: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return
        self.dlgro.tf_qkanDB.setText(database_qkan)

        with DBConnection(dbname=database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error_code(
                    "Fehler in tools.application.runoffparams: "
                    "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                        database_qkan
                    ),
                )
                raise QkanDbError

            # Check, ob alle Teilgebiete in Flächen auch in Tabelle "teilgebiete" enthalten
            sql = """INSERT INTO teilgebiete (tgnam)
                    SELECT teilgebiet FROM flaechen 
                    WHERE teilgebiet IS NOT NULL AND
                    teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                    GROUP BY teilgebiet"""
            if not db_qkan.sql(sql, "QKan_Tools.application.run (1) "):
                return

            # Check, ob alle Abflussparameter in Flächen auch in Tabelle "abflussparameter" enthalten
            sql = """INSERT INTO abflussparameter (apnam)
                    SELECT abflussparameter FROM flaechen 
                    WHERE abflussparameter IS NOT NULL AND
                    abflussparameter NOT IN (SELECT apnam FROM abflussparameter)
                    GROUP BY abflussparameter"""
            if not db_qkan.sql(sql, "QKan_Tools.application.run (2) "):
                return

            db_qkan.commit()

            # Anlegen der Tabelle zur Auswahl der Teilgebiete

            # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
            liste_teilgebiete = QKan.config.selections.teilgebiete

            # Abfragen der Tabelle teilgebiete nach Teilgebieten
            if not db_qkan.sql(
                'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"',
                "QKan_Tools.application.run (4) ",
            ):
                return
            daten = db_qkan.fetchall()

            self.dlgro.lw_teilgebiete.clear()

            for ielem, elem in enumerate(daten):
                self.dlgro.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                try:
                    if elem[0] in liste_teilgebiete:
                        self.dlgro.lw_teilgebiete.setCurrentRow(ielem)
                        self.dlgro.cb_selTgbActive.setChecked(True)
                except BaseException as err:
                    logger.error_code(
                        "QKan_Tools (6), Fehler in elem = {}\n".format(elem), repr(err)
                    )
                    raise QkanError
                    # if len(daten) == 1:
                    # self.dlgro.lw_teilgebiete.setCurrentRow(0)

            # Anlegen der Tabelle zur Auswahl der Abflussparameter

            # Zunächst wird die Liste der beim letzten Mal gewählten Abflussparameter aus config gelesen
            liste_abflussparameter = QKan.config.selections.abflussparameter

            # Abfragen der Tabelle abflussparameter nach Abflussparametern
            if not db_qkan.sql(
                'SELECT "apnam" FROM "abflussparameter" GROUP BY "apnam"',
                "QKan_Tools.application.run (4) ",
            ):
                return

            daten = db_qkan.fetchall()
            self.dlgro.lw_abflussparameter.clear()

            for ielem, elem in enumerate(daten):
                self.dlgro.lw_abflussparameter.addItem(QListWidgetItem(elem[0]))
                try:
                    if elem[0] in liste_abflussparameter:
                        self.dlgro.lw_abflussparameter.setCurrentRow(ielem)
                        self.dlgro.cb_selParActive.setChecked(True)
                except BaseException as err:
                    logger.error_code(
                        "QKan_Tools (6), Fehler in elem = {}\n".format(elem), repr(err)
                    )
                    raise QkanError

                    # if len(daten) == 1:
                    # self.dlgro.lw_abflussparameter.setCurrentRow(0)

            self.dlgro.db_qkan = db_qkan

            self.dlgro.count_selection()

            # Funktionen zur Berechnung des Oberflächenabflusses
            # Werden nur gelesen
            runoffparamsfunctions = QKan.config.tools.runoffparamsfunctions

            # Optionen zur Berechnung des Oberflächenabflusses
            runoffparamstype_choice = QKan.config.tools.runoffparamstype_choice

            if runoffparamstype_choice == enums.RunOffParamsType.ITWH:
                self.dlgro.rb_itwh.setChecked(True)
            elif runoffparamstype_choice == enums.RunOffParamsType.DYNA:
                self.dlgro.rb_dyna.setChecked(True)
            elif runoffparamstype_choice == enums.RunOffParamsType.MANIAK:
                self.dlgro.rb_maniak.setChecked(True)

            runoffmodeltype_choice = QKan.config.tools.runoffmodeltype_choice

            if runoffmodeltype_choice == enums.RunOffModelType.SPEICHERKASKADE:
                self.dlgro.rb_kaskade.setChecked(True)
            elif runoffmodeltype_choice == enums.RunOffModelType.FLIESSZEITEN:
                self.dlgro.rb_fliesszeiten.setChecked(True)
            elif runoffmodeltype_choice == enums.RunOffModelType.SCHWERPUNKTLAUFZEIT:
                self.dlgro.rb_schwerpunktlaufzeit.setChecked(True)

            # Status Radiobuttons initialisieren
            self.dlgro.toggle_itwh()

            # Formular anzeigen
            self.dlgro.show()
            # Run the dialog event loop
            result = self.dlgro.exec_()
            # See if OK was pressed

            if result:

                # Abrufen der ausgewählten Elemente in den Listen
                liste_teilgebiete = list_selected_items(self.dlgro.lw_teilgebiete)
                liste_abflussparameter = list_selected_items(self.dlgro.lw_abflussparameter)

                # Eingaben aus Formular übernehmen
                database_qkan = self.dlgro.tf_qkanDB.text()
                if self.dlgro.rb_itwh.isChecked():
                    runoffparamstype_choice = enums.RunOffParamsType.ITWH
                elif self.dlgro.rb_dyna.isChecked():
                    runoffparamstype_choice = enums.RunOffParamsType.DYNA
                elif self.dlgro.rb_maniak.isChecked():
                    runoffparamstype_choice = enums.RunOffParamsType.MANIAK
                else:
                    logger.error_code(
                        "tools.runoffparams.run_runoffparams: "
                        "Fehlerhafte Option: runoffparamstype_choice"
                    )
                    raise QkanError
                if self.dlgro.rb_kaskade.isChecked():
                    runoffmodeltype_choice = enums.RunOffModelType.SPEICHERKASKADE
                elif self.dlgro.rb_fliesszeiten.isChecked():
                    runoffmodeltype_choice = enums.RunOffModelType.FLIESSZEITEN
                elif self.dlgro.rb_schwerpunktlaufzeit.isChecked():
                    runoffmodeltype_choice = enums.RunOffModelType.SCHWERPUNKTLAUFZEIT
                else:
                    logger.error_code(
                        "tools.runoffparams.run_runoffparams: "
                        "Fehlerhafte Option: runoffmodeltype_choice"
                    )
                    raise QkanError
                # Konfigurationsdaten schreiben
                QKan.config.selections.abflussparameter = liste_abflussparameter
                QKan.config.selections.teilgebiete = liste_teilgebiete
                if database_qkan != '':
                    QKan.config.database.qkan = database_qkan
                QKan.config.tools.runoffmodeltype_choice = runoffmodeltype_choice
                QKan.config.tools.runoffparamstype_choice = runoffparamstype_choice

                QKan.config.save()

                # Modulaufruf in Logdatei schreiben
                self.log.debug(
                    f"""QKan-Modul Aufruf
                    setRunoffparams(
                        self.dbQK,
                        {runoffparamstype_choice},
                        {runoffmodeltype_choice},
                        {runoffparamsfunctions},
                        {liste_teilgebiete},
                        {liste_abflussparameter},
                    )"""
                )

                setRunoffparams(
                    db_qkan,
                    runoffparamstype_choice,
                    runoffmodeltype_choice,
                    runoffparamsfunctions,
                    liste_teilgebiete,
                    liste_abflussparameter,
                )

    def run_layersadapt(self) -> None:
        """Anpassen oder Ergänzen von Layern entsprechend der QKan-Datenstrukturen"""

        # QKan-Projekt
        # noinspection PyArgumentList
        project = QgsProject.instance()

        if project.count() == 0:
            logger.warning("Es ist kein Projekt geladen.")
            return

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        get_database_QKan(silent=True)
        self.database_name = QKan.config.database.qkan

        if self.database_name is not None and self.database_name != '':
            self.default_dir = os.path.dirname(
                self.database_name
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.database_name = QKan.config.database.qkan
            self.dlgla.tf_qkanDB.setText(self.database_name)
            self.default_dir = os.path.dirname(self.database_name)
        self.dlgla.tf_qkanDB.setText(self.database_name)

        with DBConnection(dbname=self.database_name) as db_qkan:
            # Falls die Datenbank nicht aktuell ist (self.dbIsUptodate = False), werden alle Elemente im Formular
            # deaktiviert. Nur der Checkbutton zur Aktualisierung der Datenbank bleibt aktiv und es erscheint
            # eine Information.
            self.db_is_uptodate = db_qkan.connected

        if not self.db_is_uptodate:
            logger.error("Versionskontrolle: Die QKan-Datenbank ist nicht aktuell")
            return

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgla.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # GGfs. Standardvorlage schon eintragen
        if self.apply_qkan_template:
            self.projectTemplate = os.path.join(QKan.template_dir, "Projekt.qgs")
            self.dlgla.tf_projectTemplate.setText(self.projectTemplate)

        # Groupbox "Layer anpassen" ---------------------------------------------------------------------------

        # Checkbox "Projektmakros"
        adapt_macros = QKan.config.adapt.macros
        self.dlgla.cb_adaptMacros.setChecked(adapt_macros)

        # Checkbox "Datenbankanbindung"
        adapt_db = QKan.config.adapt.database
        self.dlgla.cb_adaptDB.setChecked(adapt_db)

        # Checkbox "Projektionssystem anpassen"
        adapt_kbs = QKan.config.adapt.kbs
        self.dlgla.cb_adaptKBS.setChecked(adapt_kbs)

        # Checkbox "Wertbeziehungungen in Tabellen"
        adapt_layerstyles = QKan.config.adapt.adapt_layerstyles
        self.dlgla.cb_adaptLayerstyles.setChecked(adapt_layerstyles)

        # Checkbox "Formularanbindungen"
        adapt_forms = QKan.config.adapt.forms
        self.dlgla.cb_adaptForms.setChecked(adapt_forms)

        # Groupbox "QKan-Layer" ---------------------------------------------------------------------------

        # Optionen zur Berücksichtigung der vorhandenen Tabellen
        adapt_selected = QKan.config.adapt.selected_layers
        if adapt_selected == enums.SelectedLayers.SELECTED:
            self.dlgla.rb_adaptSelected.setChecked(True)
        elif adapt_selected == enums.SelectedLayers.ALL:
            self.dlgla.rb_adaptAll.setChecked(True)
        else:
            logger.error_code("Fehler im Programmcode: Nicht definierte Option")
            raise QkanError

        # Checkbox: Fehlende QKan-Layer ergänzen
        fehlende_layer_ergaenzen = QKan.config.adapt.add_missing_layers
        self.dlgla.cb_completeLayers.setChecked(fehlende_layer_ergaenzen)

        # Weitere Formularfelder ---------------------------------------------------------------------------

        # Checkbox: Knotentype per Abfrage ermitteln und in "schaechte.knotentyp" eintragen
        update_node_type = QKan.config.adapt.update_node_type
        self.dlgla.cb_updateNodetype.setChecked(update_node_type)

        # Checkbox: Nach Aktualisierung auf alle Layer zoomen
        self.dlgla.cb_zoomAll.setChecked(QKan.config.adapt.zoom_all)

        # Checkbox: QKan-Standard anwenden
        self.apply_qkan_template = QKan.config.tools.apply_qkan_template
        self.dlgla.cb_applyQKanTemplate.setChecked(self.apply_qkan_template)

        # Status initialisieren
        self.dlgla.click_apply_template()
        self.dlgla.enable_project_template_group()

        # -----------------------------------------------------------------------------------------------------
        # show the dialog
        self.dlgla.show()
        # Run the dialog event loop
        result = self.dlgla.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            self.database_name = self.dlgla.tf_qkanDB.text()
            adapt_db = self.dlgla.cb_adaptDB.isChecked()
            adapt_macros = self.dlgla.cb_adaptMacros.isChecked()
            adapt_layerstyles = self.dlgla.cb_adaptLayerstyles.isChecked()
            adapt_forms = self.dlgla.cb_adaptForms.isChecked()
            adapt_kbs = self.dlgla.cb_adaptKBS.isChecked()
            update_node_type = self.dlgla.cb_updateNodetype.isChecked()
            zoom_alles = self.dlgla.cb_zoomAll.isChecked()
            self.apply_qkan_template = self.dlgla.cb_applyQKanTemplate.isChecked()
            if self.apply_qkan_template:
                self.projectTemplate = ""
            else:
                self.projectTemplate = self.dlgla.tf_projectTemplate.text()

            # Optionen zur Berücksichtigung der vorhandenen Tabellen
            fehlende_layer_ergaenzen = self.dlgla.cb_completeLayers.isChecked()
            if self.dlgla.rb_adaptAll.isChecked():
                adapt_selected = enums.SelectedLayers.ALL
            elif self.dlgla.rb_adaptSelected.isChecked():
                adapt_selected = enums.SelectedLayers.SELECTED
            else:
                logger.error_code("Fehler im Programmcode: Nicht definierte Option (2)")
                raise QkanError

            # Konfigurationsdaten schreiben -----------------------------------------------------------

            QKan.config.adapt.add_missing_layers = fehlende_layer_ergaenzen
            QKan.config.adapt.database = adapt_db
            QKan.config.adapt.forms = adapt_forms
            QKan.config.adapt.kbs = adapt_kbs
            QKan.config.adapt.selected_layers = adapt_selected
            QKan.config.adapt.macros = adapt_macros
            QKan.config.adapt.adapt_layerstyles = adapt_layerstyles
            QKan.config.adapt.update_node_type = update_node_type
            QKan.config.adapt.zoom_all = zoom_alles
            QKan.config.database.qkan = cast(str, self.database_name)
            QKan.config.tools.apply_qkan_template = self.apply_qkan_template
            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                layersadapt(
                    "{self.database_name}",
                    "{self.projectTemplate}",
                    {adapt_macros},
                    {adapt_db},
                    {adapt_layerstyles},
                    {adapt_forms},
                    {adapt_kbs},
                    {update_node_type},
                    {zoom_alles},
                    {fehlende_layer_ergaenzen},
                    {adapt_selected},
                )"""
            )

            layersadapt(
                database_QKan=cast(str, self.database_name),
                projectTemplate=self.projectTemplate,
                anpassen_ProjektMakros=adapt_macros,
                anpassen_svgPaths=False,
                anpassen_Datenbankanbindung=adapt_db,
                anpassen_Layerstile=adapt_layerstyles,
                anpassen_Formulare=adapt_forms,
                anpassen_Projektionssystem=adapt_kbs,
                aktualisieren_Schachttypen=update_node_type,
                zoom_alles=zoom_alles,
                fehlende_layer_ergaenzen=fehlende_layer_ergaenzen,
                anpassen_auswahl=adapt_selected,
            )

    def run_dbAdapt(self) -> None:
        """Aktualisiert die QKan-Datenbank"""

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        get_database_QKan(silent=True)
        self.database_name = QKan.config.database.qkan

        if self.database_name is not None and self.database_name != '':
            self.default_dir = os.path.dirname(
                self.database_name
            )  # bereits geladene QKan-Datenbank übernehmen
        else:
            self.database_name = QKan.config.database.qkan
            self.default_dir = os.path.dirname(self.database_name)
        self.dlgdb.tf_qkanDB.setText(self.database_name)

        project = QgsProject.instance()
        project_file = project.absoluteFilePath()
        self.dlgdb.tf_projectFile.setText(project_file)

        # Sicherungskopien
        self.dlgdb.cb_dbBackup.setChecked(True)
        self.dlgdb.cb_qgsBackup.setChecked(True)

        # Falls Projektdatei geändert wurde, Gruppe zum Speichern der Projektdatei anzeigen
        # noinspection PyArgumentList
        # project = QgsProject.instance()
        # project_is_dirty = project.isDirty()
        # self.dlgdb.gb_updateQkanDB.setEnabled(project_is_dirty)

        # show the dialog
        self.dlgdb.show()

        # Run the dialog event loop
        result = self.dlgdb.exec_()

        # See if OK was pressed
        if result:

            self.database_name = self.dlgdb.tf_qkanDB.text()
            project_file: str = self.dlgdb.tf_projectFile.text()
            writeDbBackup = self.dlgdb.cb_dbBackup.isChecked()
            writeQgsBackup = self.dlgdb.cb_dbBackup.isChecked()

            # Konfigurationsdaten schreiben -----------------------------
            QKan.config.database.qkan = cast(str, self.database_name)
            QKan.config.project.file = project_file
            QKan.config.save()

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                DBConnection(
                    "{self.database_name}",
                    "{True}",
                    "{writeDbBackup}",
                    "{writeQgsBackup}",
                )"""
            )

            # Öffnen der Datenbank, nur um die Aktualisierung durchzuführen.
            with DBConnection(
                    dbname=cast(str, self.database_name),
                    qkan_db_update=True,
                    writeDbBackup=writeDbBackup,
                    writeQgsBackup=writeQgsBackup
            ) as dbQK:  # Datenbankobjekt zur Aktualisierung öffnen

                if not dbQK.connected:
                    errormsg = (
                        "Fehler in k_qgsadapt: QKan-Datenbank {self.database_name}"
                        f" wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"
                    )
                    logger.error(errormsg)
                    raise QkanDbError(f"{__name__}: {errormsg}")

                dbQK.sql("SELECT RecoverSpatialIndex()")  # Geometrie-Indizes bereinigen

            # layersadapt(
            #     database_QKan=cast(str, self.database_name),
            #     projectTemplate=os.path.join(pluginDirectory("qkan"), "templates/Projekt.qgs"),
            #     anpassen_ProjektMakros=True,
            #     anpassen_svgPaths=False,
            #     anpassen_Datenbankanbindung=False,
            #     anpassen_Layerstile=True,
            #     anpassen_Formulare=True,
            #     anpassen_Projektionssystem=False,
            #     aktualisieren_Schachttypen=False,
            #     zoom_alles=False,
            #     fehlende_layer_ergaenzen=False,
            #     anpassen_auswahl=enums.SelectedLayers.ALL,
            # )
            # QgsProject.instance().clear()
            # QgsProject.instance().read()
            # project.readPath(project_file)


    def run_help(self) -> None:

        self.dlghp.textBrowser_2.setText(f'{QKan.qgsVersion}.{QKan.build}')
        plugin_dir = os.path.dirname(__file__)
        bild_pfad = os.path.join(plugin_dir, "Qkan_Logo.png")

        self.dlghp.label_2.setScaledContents(True)
        self.dlghp.label_2.setPixmap(QPixmap(bild_pfad))

        # show the dialog
        self.dlghp.show()
        # Run the dialog event loop
        result = self.dlghp.exec_()


    def run_filepath(self) -> None:

        self.dlgfp.lineEdit.setText(QKan.config.videoPathCurrent)
        self.dlgfp.lineEdit_2.setText(QKan.config.fotoPathCurrent)

        # show the dialog
        self.dlgfp.show()

        # Run the dialog event loop
        result = self.dlgfp.exec()

        # See if OK was pressed
        if result:

            # Abrufen der ausgewählten Elemente in den Listen
            videopath = self.dlgfp.lineEdit.text()
            fotopath = self.dlgfp.lineEdit_2.text()
            fotopath_2 = self.dlgfp.lineEdit_3.text()
            videopath_2 = self.dlgfp.lineEdit_5.text()
            fotopath_3 = self.dlgfp.lineEdit_6.text()
            videopath_3 = self.dlgfp.lineEdit_7.text()
            ausw_haltung = self.dlgfp.checkBox.isChecked()
            ausw_schacht = self.dlgfp.checkBox_2.isChecked()
            ausw_leitung = self.dlgfp.checkBox_3.isChecked()

            QKan.config.videoRootPath = videopath
            QKan.config.fotoRootPath = fotopath

            QKan.config.save()

            with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:
                if not db_qkan.connected:
                    self.log.error(
                        "Fehler im XML-Export\n"
                        f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    )
                    raise Exception(f"{self.__class__.__name__}: {QKan.config.database.qkan} wurde nicht gefunden!")

                # Run

                setfilepath(
                    db_qkan,
                    videopath,
                    fotopath,
                    fotopath_2,
                    videopath_2,
                    fotopath_3,
                    videopath_3,
                    ausw_haltung,
                    ausw_schacht,
                    ausw_leitung,
                )

    def run_bericht(self) -> None:


        # show the dialog
        self.dlgb.show()

        # Run the dialog event loop
        result = self.dlgb.exec()

        path = self.dlgb.save_path.text()
        if self.dlgb.select_auswahl.isChecked():
            auswahl = True
        else:
            auswahl = False

        art = self.dlgb.bewertungsart.currentText()

        # See if OK was pressed
        if result:

            QKan.config.save()

            with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:
                if not db_qkan.connected:
                    self.log.error(
                        "Fehler im XML-Export\n"
                        f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    )
                    raise Exception(f"{self.__class__.__name__}: {QKan.config.database.qkan} wurde nicht gefunden!")

                # Run

                bericht(
                    db_qkan,
                    path,
                    auswahl, art
                )

    def on_change(self):
        text = self.clip.text()
        self.text = text

    def zoom_clip2(self):
        get_database_QKan()
        with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:
            if not db_qkan.connected:
                self.log.error(
                    "Fehler im XML-Export\n"
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                raise Exception(f"{self.__class__.__name__}: {QKan.config.database.qkan} wurde nicht gefunden!")

            clip = self.text

            layer = QgsProject.instance().mapLayersByName('Haltungen')[0]
            if layer is not None and clip is not None:
                value = str(clip)
                field = "Bezeichnung"
                layer.removeSelection()

                if value != '':

                    expr = f'"{field}" = \'{value}\''
                    layer.selectByExpression(expr)
                    iface.mapCanvas().zoomToSelected(layer)

                    sel = layer.selectedFeatureIds()

                    if not sel:
                        layer = QgsProject.instance().mapLayersByName('Schächte')[0]
                        layer.removeSelection()
                        value = str(clip)
                        field = "Schachtname"

                        expr = f'"{field}" = \'{value}\''
                        layer.selectByExpression(expr)
                        iface.mapCanvas().zoomToSelected(layer)
                        # 42780133

    def run_zoom_clipboard(self):
        text = self.clip.text()
        self.text = text

        if self.action.isChecked():
            self.clip.dataChanged.connect(self.on_change)
            self.dlgzc.clip.dataChanged.connect(self.zoom_clip2)
        else:
            self.clip.dataChanged.disconnect(self.on_change)

    def run_befahrung(self) -> None:

        # show the dialog
        self.dlgbf.show()

        # Run the dialog event loop
        result = self.dlgbf.exec()

        # See if OK was pressed
        if result:

            with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:
                if not db_qkan.connected:
                    self.log.error(
                        "Fehler im XML-Export\n"
                        f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    )
                    raise Exception(f"{self.__class__.__name__}: {QKan.config.database.qkan} wurde nicht gefunden!")

                # Run

                setbefahrung(
                    db_qkan,
                )
