# -*- coding: utf-8 -*-

"""

  QGis-Plugin
  ===========

  Definition der Formularklasse

  | Dateiname            : application.py
  | Date                 : September 2019
  | Copyright            : (C) 2019 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.                                  

"""
import logging
import os.path

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator, qVersion
from qgis.PyQt.QtWidgets import QFileDialog, QListWidgetItem
from qgis.utils import pluginDirectory
from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
)

# noinspection PyUnresolvedReferences
from . import resources
from .application_dialog import ExportToHE8Dialog
from .k_qkhe8 import export2he8

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.exporthe8.application")

progress_bar = None


class ExportToHE8:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        self.templatepath = os.path.join(pluginDirectory("qkan"), u"templates")

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "ExportToHE8_{}.qm".format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ExportToHE8Dialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 08.02.2017)

        logger.info("\n\nQKan_ExportHE8 initialisiert...")

        # --------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        # wordir = os.path.join(site.getuserbase(), 'qkan')

        # if not os.path.isdir(wordir):
        # os.makedirs(wordir)

        # --------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        # self.configfil = os.path.join(wordir, 'qkan.json')
        # if os.path.exists(self.configfil):
        # with open(self.configfil, 'r') as fileconfig:
        # self.config = json.loads(fileconfig.read())
        # else:
        # self.config['database_HE'] = ''
        # # Vorlagedatenbank nur für den Fall, dass der Anwender keine eigene Vorlage erstellen will
        # self.config['dbtemplate_HE'] = os.path.join(os.path.dirname(__file__), "templates", "itwh.idbm")
        # self.config['database_QKan'] = ''
        # with open(self.configfil, 'w') as fileconfig:
        # fileconfig.write(json.dumps(self.config))

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        # Formularereignisse anbinden ----------------------------------------------

        self.dlg.pb_exportall.clicked.connect(self.exportall)
        self.dlg.pb_modifyall.clicked.connect(self.modifyall)
        self.dlg.pb_exportnone.clicked.connect(self.exportnone)
        self.dlg.pb_modifynone.clicked.connect(self.modifynone)

        self.dlg.lw_teilgebiete.itemClicked.connect(self.countselection)
        self.dlg.lw_teilgebiete.itemClicked.connect(self.lw_teilgebieteClick)
        self.dlg.cb_selActive.stateChanged.connect(self.selActiveClick)
        self.dlg.button_box.helpRequested.connect(self.helpClick)

        # Ende Eigene Funktionen ---------------------------------------------------

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("ExportToHE8", message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/qkan/exporthe8/icon_qk2he8.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr(u"Export to Hystem-Extran 8"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        pass

    # Anfang Eigene Funktionen -------------------------------------------------
    # (jh, 08.02.2017)

    def selectFile_HeDB_dest(self):
        """Datenbankverbindung zur HE-Datenbank (Firebird) auswaehlen und gegebenenfalls die Zieldatenbank
           erstellen, aber noch nicht verbinden."""

        filename, __ = QFileDialog.getSaveFileName(
            self.dlg,
            "Dateinamen der Ziel-HE-Datenbank eingeben",
            self.default_dir,
            "*.idbm",
        )
        # if os.path.dirname(filename) != '':
        # os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB_dest.setText(filename)

    def selectFile_HeDB_template(self):
        """Vorlage-HE-Datenbank (Firebird) auswaehlen."""

        filename, __ = QFileDialog.getOpenFileName(
            self.dlg, u"Vorlage-HE-Datenbank auswählen", self.default_dir, "*.idbm"
        )
        # if os.path.dirname(filename) != '':
        # os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB_template.setText(filename)

    def selectFile_HeDB_emptytemplate(self):
        """Vorlage-HE-Datenbank (Firebird) auswaehlen."""

        filename, __ = QFileDialog.getOpenFileName(
            self.dlg,
            u"Leere Vorlage-HE-Datenbank auswählen",
            self.templatepath,
            "*.idbm",
        )
        # if os.path.dirname(filename) != '':
        # os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB_template.setText(filename)

    def selectFile_QKanDB(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        filename, __ = QFileDialog.getOpenFileName(
            self.dlg, u"QKan-Datenbank auswählen", self.default_dir, "*.sqlite"
        )
        # if os.path.dirname(filename) != '':
        # os.chdir(os.path.dirname(filename))
        self.dlg.tf_QKanDB.setText(filename)

    def exportall(self):
        """Aktiviert alle Checkboxen zm Export"""

        self.dlg.cb_export_schaechte.setChecked(True)
        self.dlg.cb_export_auslaesse.setChecked(True)
        self.dlg.cb_export_speicher.setChecked(True)
        self.dlg.cb_export_haltungen.setChecked(True)
        self.dlg.cb_export_pumpen.setChecked(True)
        self.dlg.cb_export_wehre.setChecked(True)
        self.dlg.cb_export_flaechenrw.setChecked(True)
        self.dlg.cb_export_einleitdirekt.setChecked(True)
        self.dlg.cb_export_aussengebiete.setChecked(True)
        self.dlg.cb_export_abflussparameter.setChecked(True)
        self.dlg.cb_export_regenschreiber.setChecked(True)
        self.dlg.cb_export_rohrprofile.setChecked(True)
        self.dlg.cb_export_speicherkennlinien.setChecked(True)
        self.dlg.cb_export_bodenklassen.setChecked(True)

    def modifyall(self):
        """Aktiviert alle Checkboxen zm Ändern"""

        self.dlg.cb_modify_schaechte.setChecked(True)
        self.dlg.cb_modify_auslaesse.setChecked(True)
        self.dlg.cb_modify_speicher.setChecked(True)
        self.dlg.cb_modify_haltungen.setChecked(True)
        self.dlg.cb_modify_pumpen.setChecked(True)
        self.dlg.cb_modify_wehre.setChecked(True)
        self.dlg.cb_modify_flaechenrw.setChecked(True)
        self.dlg.cb_modify_einleitdirekt.setChecked(True)
        self.dlg.cb_modify_aussengebiete.setChecked(True)
        self.dlg.cb_modify_abflussparameter.setChecked(True)
        self.dlg.cb_modify_regenschreiber.setChecked(True)
        self.dlg.cb_modify_rohrprofile.setChecked(True)
        self.dlg.cb_modify_speicherkennlinien.setChecked(True)
        self.dlg.cb_modify_bodenklassen.setChecked(True)

    def exportnone(self):
        """Deaktiviert alle Checkboxen zm Export"""

        self.dlg.cb_export_schaechte.setChecked(False)
        self.dlg.cb_export_auslaesse.setChecked(False)
        self.dlg.cb_export_speicher.setChecked(False)
        self.dlg.cb_export_haltungen.setChecked(False)
        self.dlg.cb_export_pumpen.setChecked(False)
        self.dlg.cb_export_wehre.setChecked(False)
        self.dlg.cb_export_flaechenrw.setChecked(False)
        self.dlg.cb_export_einleitdirekt.setChecked(False)
        self.dlg.cb_export_aussengebiete.setChecked(False)
        self.dlg.cb_export_abflussparameter.setChecked(False)
        self.dlg.cb_export_regenschreiber.setChecked(False)
        self.dlg.cb_export_rohrprofile.setChecked(False)
        self.dlg.cb_export_speicherkennlinien.setChecked(False)
        self.dlg.cb_export_bodenklassen.setChecked(False)

    def modifynone(self):
        """Deaktiviert alle Checkboxen zm Ändern"""

        self.dlg.cb_modify_schaechte.setChecked(False)
        self.dlg.cb_modify_auslaesse.setChecked(False)
        self.dlg.cb_modify_speicher.setChecked(False)
        self.dlg.cb_modify_haltungen.setChecked(False)
        self.dlg.cb_modify_pumpen.setChecked(False)
        self.dlg.cb_modify_wehre.setChecked(False)
        self.dlg.cb_modify_flaechenrw.setChecked(False)
        self.dlg.cb_modify_einleitdirekt.setChecked(False)
        self.dlg.cb_modify_aussengebiete.setChecked(False)
        self.dlg.cb_modify_abflussparameter.setChecked(False)
        self.dlg.cb_modify_regenschreiber.setChecked(False)
        self.dlg.cb_modify_rohrprofile.setChecked(False)
        self.dlg.cb_modify_speicherkennlinien.setChecked(False)
        self.dlg.cb_modify_bodenklassen.setChecked(False)

    # -------------------------------------------------------------------------
    # Formularfunktionen

    def helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(self.plugin_dir, "..\doc", "exporthe8.html")
        os.startfile(helpfile)

    def lw_teilgebieteClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlg.cb_selActive.setChecked(True)
        self.countselection()

    def selActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlg.cb_selActive.isChecked():
            # Nix tun ...
            logger.debug("\nChecked = True")
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlg.lw_teilgebiete.count()
            for i in range(anz):
                item = self.dlg.lw_teilgebiete.item(i)
                item.setSelected(False)
                # self.dlg.lw_teilgebiete.setItemSelected(item, False)

            # Anzahl in der Anzeige aktualisieren
            self.countselection()

    def countselection(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        liste_teilgebiete: list = self.listselecteditems(self.dlg.lw_teilgebiete)

        # Zu berücksichtigende Flächen zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = u" WHERE flaechen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = u"""SELECT count(*) AS anzahl FROM flaechen{auswahl}""".format(
            auswahl=auswahl
        )

        if not self.dbQK.sql(sql, u"QKan_ExportHE.application.countselection (1)"):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.dlg.lf_anzahl_flaechen.setText("0")

        # Zu berücksichtigende Schächte zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = u" WHERE schaechte.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = u"""SELECT count(*) AS anzahl FROM schaechte{auswahl}""".format(
            auswahl=auswahl
        )
        if not self.dbQK.sql(sql, u"QKan_ExportHE.application.countselection (2) "):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg.lf_anzahl_schaechte.setText(str(daten[0]))
        else:
            self.dlg.lf_anzahl_schaechte.setText("0")

        # Zu berücksichtigende Haltungen zählen
        auswahl = ""
        if len(liste_teilgebiete) != 0:
            auswahl = u" WHERE haltungen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )

        sql = u"""SELECT count(*) AS anzahl FROM haltungen{auswahl}""".format(
            auswahl=auswahl
        )
        if not self.dbQK.sql(sql, u"QKan_ExportHE.application.countselection (3) "):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.dlg.lf_anzahl_haltungen.setText("0")

    # -------------------------------------------------------------------------
    # Funktion zur Zusammenstellung einer Auswahlliste für eine SQL-Abfrage

    def listselecteditems(self, listWidget):
        """Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

        :param listWidget: String for translation.
        :type listWidget: QListWidget

        :returns: List containing selected teilgebiete
        :rtype: list
        """
        return [_.text() for _ in listWidget.selectedItems()]

    # Ende Eigene Funktionen ---------------------------------------------------

    def run(self):
        """Run method that performs all the real work"""

        self.dlg.tf_QKanDB.setText(QKan.config.database.qkan)
        self.dlg.pb_selectQKanDB.clicked.connect(self.selectFile_QKanDB)

        self.dlg.tf_heDB_dest.setText(QKan.config.he.database)
        self.dlg.pb_selectHeDB_dest.clicked.connect(self.selectFile_HeDB_dest)

        self.dlg.tf_heDB_template.setText(QKan.config.he.template)
        self.dlg.pb_selectHeDB_template.clicked.connect(self.selectFile_HeDB_template)
        self.dlg.pb_selectHeDB_emptytemplate.clicked.connect(
            self.selectFile_HeDB_emptytemplate
        )
        # Auswahl der zu exportierenden Tabellen ----------------------------------------------

        # Eigene Funktion für die zahlreichen Checkboxen

        def cb_set(name, cbox, default):
            if hasattr(QKan.config.check_export, name):
                checked = getattr(QKan.config.check_export, name)
            else:
                checked = default
            cbox.setChecked(checked)
            return checked

        def cb_setfalse(name, cbox, default):
            """Die selbe Funktion wie vor, deaktiviert jedoch die Optionen,
               weil die entsprechende Funktion noch nicht fertig ist"""
            checked = False
            cbox.setChecked(checked)
            return checked

        export_schaechte = cb_set(
            "export_schaechte", self.dlg.cb_export_schaechte, True)
        export_auslaesse = cb_setfalse(
            "export_auslaesse", self.dlg.cb_export_auslaesse, True)
        export_speicher = cb_set("export_speicher", self.dlg.cb_export_speicher, True)
        export_haltungen = cb_set(
            "export_haltungen", self.dlg.cb_export_haltungen, True)
        export_pumpen = cb_setfalse("export_pumpen", self.dlg.cb_export_pumpen, False) 
        export_wehre = cb_setfalse("export_wehre", self.dlg.cb_export_wehre, False) 
        export_flaechenrw = cb_set(
            "export_flaechenrw", self.dlg.cb_export_flaechenrw, True)
        export_einleitdirekt = cb_setfalse(
            "export_einleitdirekt", self.dlg.cb_export_einleitdirekt, True)
        export_aussengebiete = cb_setfalse(
            "export_aussengebiete", self.dlg.cb_export_aussengebiete, True)
        export_abflussparameter = cb_setfalse(
            "export_abflussparameter", self.dlg.cb_export_abflussparameter, True)
        export_regenschreiber = cb_setfalse(
            "export_regenschreiber", self.dlg.cb_export_regenschreiber, False) 
        export_rohrprofile = cb_setfalse(
            "export_rohrprofile", self.dlg.cb_export_rohrprofile, False) 
        export_speicherkennlinien = cb_setfalse(
            "export_speicherkennlinien", self.dlg.cb_export_speicherkennlinien, False) 
        export_bodenklassen = cb_setfalse(
            "export_bodenklassen", self.dlg.cb_export_bodenklassen, False) 

        modify_schaechte = cb_set(
            "modify_schaechte", self.dlg.cb_modify_schaechte, False)
        modify_auslaesse = cb_setfalse(
            "modify_auslaesse", self.dlg.cb_modify_auslaesse, False) 
        modify_speicher = cb_set("modify_speicher", self.dlg.cb_modify_speicher, False)
        modify_haltungen = cb_set(
            "modify_haltungen", self.dlg.cb_modify_haltungen, False) 
        modify_pumpen = cb_setfalse("modify_pumpen", self.dlg.cb_modify_pumpen, False) 
        modify_wehre = cb_setfalse("modify_wehre", self.dlg.cb_modify_wehre, False) 
        modify_flaechenrw = cb_set(
            "modify_flaechenrw", self.dlg.cb_modify_flaechenrw, False)
        modify_einleitdirekt = cb_setfalse(
            "modify_einleitdirekt", self.dlg.cb_modify_einleitdirekt, False) 
        modify_aussengebiete = cb_setfalse(
            "modify_aussengebiete", self.dlg.cb_modify_aussengebiete, False) 
        modify_abflussparameter = cb_setfalse(
            "modify_abflussparameter", self.dlg.cb_modify_abflussparameter, False) 
        modify_regenschreiber = cb_setfalse(
            "modify_regenschreiber", self.dlg.cb_modify_regenschreiber, False) 
        modify_rohrprofile = cb_setfalse(
            "modify_rohrprofile", self.dlg.cb_modify_rohrprofile, False) 
        modify_speicherkennlinien = cb_setfalse(
            "modify_speicherkennlinien", self.dlg.cb_modify_speicherkennlinien, False) 
        modify_bodenklassen = cb_setfalse(
            "modify_bodenklassen", self.dlg.cb_modify_bodenklassen, False) 

        combine_einleitdirekt = cb_setfalse(
            "combine_einleitdirekt", self.dlg.cb_combine_einleitdirekt, True)

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {"flaechen", "haltungen", "linkfl", "tezg", "schaechte"}
                & get_editable_layers()
            )
            > 0
        ):
            self.iface.messageBar().pushMessage(
                u"Bedienerfehler: ",
                u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return False

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(
                u"Fehler in exporthe8",
                u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!",
            )
            logger.error(
                "exporthe8: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False

        if database_QKan != "":
            self.dlg.tf_QKanDB.setText(database_QKan)

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen
        if not self.dbQK.connected:
            logger.error(
                u"Fehler in exportdyna.application:\n",
                u"QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        # Check, ob alle Teilgebiete in Flächen, Schächten und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"QKan_ExportHE.application.run (1) "):
            return False

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"QKan_ExportHE.application.run (2) "):
            return False

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM schaechte 
                WHERE teilgebiet IS NOT NULL AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"QKan_ExportHE.application.run (3) "):
            return False

        self.dbQK.commit()

        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        liste_teilgebiete = QKan.config.selections.teilgebiete

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.dbQK.sql(sql, u"QKan_ExportHE.application.run (4) "):
            return False
        daten = self.dbQK.fetchall()
        self.dlg.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.dlg.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in liste_teilgebiete:
                    self.dlg.lw_teilgebiete.setCurrentRow(ielem)
            except BaseException as err:
                fehlermeldung(
                    u"QKan_ExportHE (6), Fehler in elem = {}\n".format(elem), repr(err)
                )
                # if len(daten) == 1:
                # self.dlg.lw_teilgebiete.setCurrentRow(0)

        # Ereignis bei Auswahländerung in Liste Teilgebiete

        self.countselection()

        # Autokorrektur
        self.dlg.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

        # Festlegung des Fangradius
        # Kann über Menü "Optionen" eingegeben werden
        fangradius = QKan.config.fangradius

        # Haltungsflächen (tezg) berücksichtigen
        self.dlg.cb_regardTezg.setChecked(QKan.config.mit_verschneidung)

        # Mindestflächengröße
        # Kann über Menü "Optionen" eingegeben werden
        mindestflaeche = QKan.config.mindestflaeche

        self.countselection()

        # Formular anzeigen

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Abrufen der ausgewählten Elemente in beiden Listen
            liste_teilgebiete: list = self.listselecteditems(self.dlg.lw_teilgebiete)

            # Eingaben aus Formular übernehmen
            database_QKan: str = self.dlg.tf_QKanDB.text()
            database_HE: str = self.dlg.tf_heDB_dest.text()
            dbtemplate_HE: str = self.dlg.tf_heDB_template.text()
            autokorrektur: bool = self.dlg.cb_autokorrektur.isChecked()
            mit_verschneidung: bool = self.dlg.cb_regardTezg.isChecked()

            exportFlaechenHE8: bool = self.dlg.cb_copyFlaechenHE8.isChecked()

            check_export = {}
            check_export["export_schaechte"] = self.dlg.cb_export_schaechte.isChecked()
            check_export["export_auslaesse"] = self.dlg.cb_export_auslaesse.isChecked()
            check_export["export_speicher"] = self.dlg.cb_export_speicher.isChecked()
            check_export["export_haltungen"] = self.dlg.cb_export_haltungen.isChecked()
            check_export["export_pumpen"] = self.dlg.cb_export_pumpen.isChecked()
            check_export["export_wehre"] = self.dlg.cb_export_wehre.isChecked()
            check_export[
                "export_flaechenrw"
            ] = self.dlg.cb_export_flaechenrw.isChecked()
            check_export[
                "export_einleitdirekt"
            ] = self.dlg.cb_export_einleitdirekt.isChecked()
            check_export[
                "export_aussengebiete"
            ] = self.dlg.cb_export_aussengebiete.isChecked()
            check_export[
                "export_abflussparameter"
            ] = self.dlg.cb_export_abflussparameter.isChecked()
            check_export[
                "export_regenschreiber"
            ] = self.dlg.cb_export_regenschreiber.isChecked()
            check_export[
                "export_rohrprofile"
            ] = self.dlg.cb_export_rohrprofile.isChecked()
            check_export[
                "export_speicherkennlinien"
            ] = self.dlg.cb_export_speicherkennlinien.isChecked()
            check_export[
                "export_bodenklassen"
            ] = self.dlg.cb_export_bodenklassen.isChecked()

            check_export["modify_schaechte"] = self.dlg.cb_modify_schaechte.isChecked()
            check_export["modify_auslaesse"] = self.dlg.cb_modify_auslaesse.isChecked()
            check_export["modify_speicher"] = self.dlg.cb_modify_speicher.isChecked()
            check_export["modify_haltungen"] = self.dlg.cb_modify_haltungen.isChecked()
            check_export["modify_pumpen"] = self.dlg.cb_modify_pumpen.isChecked()
            check_export["modify_wehre"] = self.dlg.cb_modify_wehre.isChecked()
            check_export[
                "modify_flaechenrw"
            ] = self.dlg.cb_modify_flaechenrw.isChecked()
            check_export[
                "modify_einleitdirekt"
            ] = self.dlg.cb_modify_einleitdirekt.isChecked()
            check_export[
                "modify_aussengebiete"
            ] = self.dlg.cb_modify_aussengebiete.isChecked()
            check_export[
                "modify_abflussparameter"
            ] = self.dlg.cb_modify_abflussparameter.isChecked()
            check_export[
                "modify_regenschreiber"
            ] = self.dlg.cb_modify_regenschreiber.isChecked()
            check_export[
                "modify_rohrprofile"
            ] = self.dlg.cb_modify_rohrprofile.isChecked()
            check_export[
                "modify_speicherkennlinien"
            ] = self.dlg.cb_modify_speicherkennlinien.isChecked()
            check_export[
                "modify_bodenklassen"
            ] = self.dlg.cb_modify_bodenklassen.isChecked()

            check_export[
                "combine_einleitdirekt"
            ] = self.dlg.cb_combine_einleitdirekt.isChecked()

            # Konfigurationsdaten schreiben
            QKan.config.autokorrektur = autokorrektur
            QKan.config.selections.teilgebiete = liste_teilgebiete
            QKan.config.database.qkan = database_QKan
            QKan.config.fangradius = fangradius
            QKan.config.he.database = database_HE
            QKan.config.he.template = dbtemplate_HE
            QKan.config.mindestflaeche = mindestflaeche
            QKan.config.mit_verschneidung = mit_verschneidung

            for el in check_export:
                setattr(QKan.config.check_export, el, check_export[el])

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            logger.debug(f"""QKan-Modul Aufruf
                export2he8(
                self.iface,
                "{database_HE}",
                "{dbtemplate_HE}",
                self.dbQK,
                {liste_teilgebiete},
                {autokorrektur},
                {fangradius},
                {mindestflaeche},
                {mit_verschneidung},
                {exportFlaechenHE8},
                {check_export},
            )""")

            if not export2he8(
                self.iface,
                database_HE,
                dbtemplate_HE,
                self.dbQK,
                liste_teilgebiete,
                autokorrektur,
                fangradius,
                mindestflaeche,
                mit_verschneidung,
                exportFlaechenHE8,
                check_export,
            ):
                del self.dbQK
