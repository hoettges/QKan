#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

  QGis-Plugin
  ===========

  Definition der Formularklasse

  | Dateiname            : application.py
  | Date                 : Februar 2017
  | Copyright            : (C) 2016 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify  
  it under the terms of the GNU General Public License as published by  
  the Free Software Foundation; either version 2 of the License, or     
  (at your option) any later version.                                  

"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QListWidgetItem
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from application_dialog import ExportToHEDialog
import site, os.path

# Ergaenzt (jh, 08.02.2017) -------------------------------------------------
import json
import logging

# from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.core import QgsProject, QgsMessageLog
from k_qkhe import exportKanaldaten
from QKan_Database.qgis_utils import get_database_QKan, get_editable_layers
from QKan_Database.dbfunc import DBConnection
import codecs

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger('QKan')

def fortschritt(text,prozent):
    logger.debug(u'{:s} ({:.0f}%)'.format(text,prozent*100))
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text,prozent*100), 'Export: ', QgsMessageLog.INFO)

def fehlermeldung(title, text):
    logger.debug(u'{:s} {:s}'.format(title,text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)

class ExportToHE:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ExportToHE_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ExportToHEDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Export to HE')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ExportToHE')
        self.toolbar.setObjectName(u'ExportToHE')

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 08.02.2017)

        logger.info('\n\nQKan_ExportHE initialisiert...')

        # --------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(),'qkan')

        if not os.path.isdir(wordir):
            os.makedirs(wordir)

        # --------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        self.configfil = os.path.join(wordir, 'qkan.json')
        if os.path.exists(self.configfil):
            with codecs.open(self.configfil,'r','utf-8') as fileconfig:
                self.config = json.loads(fileconfig.read().replace('\\','/'))
        else:
            self.config['database_HE'] = ''
            # Vorlagedatenbank nur für den Fall, dass der Anwender keine eigene Vorlage erstellen will
            self.config['dbtemplate_HE'] = os.path.join(os.path.dirname(__file__), "templates","itwh.idbf")
            self.config['database_QKan'] = ''
            with codecs.open(self.configfil,'w','utf-8') as fileconfig:
                fileconfig.write(json.dumps(self.config))

        # Standard für Suchverzeichnis festlegen
        project = QgsProject.instance()
        self.default_dir = os.path.dirname(project.fileName())

        if 'database_QKan' in self.config:
            database_QKan = self.config['database_QKan']
        else:
            database_QKan = ''
        self.dlg.tf_QKanDB.setText(database_QKan)
        self.dlg.pb_selectQKanDB.clicked.connect(self.selectFile_QKanDB)

        if 'database_HE' in self.config:
            database_HE = self.config['database_HE']
        else:
            database_HE = ''
        self.dlg.tf_heDB_dest.setText(database_HE)
        self.dlg.pb_selectHeDB_dest.clicked.connect(self.selectFile_HeDB_dest)

        if 'dbtemplate_HE' in self.config:
            dbtemplate_HE = self.config['dbtemplate_HE']
        else:
            dbtemplate_HE = ''
        self.dlg.tf_heDB_template.setText(dbtemplate_HE)
        self.dlg.pb_selectHeDB_template.clicked.connect(self.selectFile_HeDB_template)

        if 'datenbanktyp' in self.config:
            datenbanktyp = self.config['datenbanktyp']
        else:
            datenbanktyp = 'spatialite'
            pass                                    # Es gibt noch keine Wahlmöglichkeit

        self.dlg.pb_exportall.clicked.connect(self.exportall)
        self.dlg.pb_modifyall.clicked.connect(self.modifyall)
        self.dlg.pb_initall.clicked.connect(self.initall)
        self.dlg.pb_exportnone.clicked.connect(self.exportnone)
        self.dlg.pb_modifynone.clicked.connect(self.modifynone)
        self.dlg.pb_initnone.clicked.connect(self.initnone)

        # Auswahl der zu exportierenden Tabellen ----------------------------------------------

        # Eigene Funktion für die zahlreichen Checkboxen

        def cb_set(name, cbox, default):
            if name in self.config:
                checked = self.config[name]
            else:
                checked = default
            cbox.setChecked(checked)
            return checked

        export_schaechte =          cb_set('export_schaechte',          self.dlg.cb_export_schaechte, True)
        export_auslaesse =          cb_set('export_auslaesse',          self.dlg.cb_export_auslaesse, True)
        export_speicher =           cb_set('export_speicher',           self.dlg.cb_export_speicher, True)
        export_haltungen =          cb_set('export_haltungen',          self.dlg.cb_export_haltungen, True)
        export_pumpen =             cb_set('export_pumpen',             self.dlg.cb_export_pumpen, False)
        export_wehre =              cb_set('export_wehre',              self.dlg.cb_export_wehre, False)
        export_flaechenrw =         cb_set('export_flaechenrw',         self.dlg.cb_export_flaechenrw, True)
        export_flaechensw =         cb_set('export_flaechensw',         self.dlg.cb_export_flaechensw, True)
        export_abflussparameter =   cb_set('export_abflussparameter',   self.dlg.cb_export_abflussparameter, True)
        export_regenschreiber =     cb_set('export_regenschreiber',     self.dlg.cb_export_regenschreiber, False)
        export_rohrprofile =        cb_set('export_rohrprofile',        self.dlg.cb_export_rohrprofile, False)
        export_speicherkennlinien = cb_set('export_speicherkennlinien', self.dlg.cb_export_speicherkennlinien, False)
        export_bodenklassen =       cb_set('export_bodenklassen',       self.dlg.cb_export_bodenklassen, False)

        modify_schaechte =          cb_set('modify_schaechte',          self.dlg.cb_modify_schaechte, False)
        modify_auslaesse =          cb_set('modify_auslaesse',          self.dlg.cb_modify_auslaesse, False)
        modify_speicher =           cb_set('modify_speicher',           self.dlg.cb_modify_speicher, False)
        modify_haltungen =          cb_set('modify_haltungen',          self.dlg.cb_modify_haltungen, False)
        modify_pumpen =             cb_set('modify_pumpen',             self.dlg.cb_modify_pumpen, False)
        modify_wehre =              cb_set('modify_wehre',              self.dlg.cb_modify_wehre, False)
        modify_flaechenrw =         cb_set('modify_flaechenrw',         self.dlg.cb_modify_flaechenrw, False)
        modify_flaechensw =         cb_set('modify_flaechensw',         self.dlg.cb_modify_flaechensw, False)
        modify_abflussparameter =   cb_set('modify_abflussparameter',   self.dlg.cb_modify_abflussparameter, False)
        modify_regenschreiber =     cb_set('modify_regenschreiber',     self.dlg.cb_modify_regenschreiber, False)
        modify_rohrprofile =        cb_set('modify_rohrprofile',        self.dlg.cb_modify_rohrprofile, False)
        modify_speicherkennlinien = cb_set('modify_speicherkennlinien', self.dlg.cb_modify_speicherkennlinien, False)
        modify_bodenklassen =       cb_set('modify_bodenklassen',       self.dlg.cb_modify_bodenklassen, False)

        init_schaechte =            cb_set('init_schaechte',            self.dlg.cb_init_schaechte, False)
        init_auslaesse =            cb_set('init_auslaesse',            self.dlg.cb_init_auslaesse, False)
        init_speicher =             cb_set('init_speicher',             self.dlg.cb_init_speicher, False)
        init_haltungen =            cb_set('init_haltungen',            self.dlg.cb_init_haltungen, False)
        init_pumpen =               cb_set('init_pumpen',               self.dlg.cb_init_pumpen, False)
        init_wehre =                cb_set('init_wehre',                self.dlg.cb_init_wehre, False)
        init_flaechenrw =           cb_set('init_flaechenrw',           self.dlg.cb_init_flaechenrw, False)
        init_flaechensw =           cb_set('init_flaechensw',           self.dlg.cb_init_flaechensw, False)
        init_abflussparameter =     cb_set('init_abflussparameter',     self.dlg.cb_init_abflussparameter, False)
        init_regenschreiber =       cb_set('init_regenschreiber',       self.dlg.cb_init_regenschreiber, False)
        init_rohrprofile =          cb_set('init_rohrprofile',          self.dlg.cb_init_rohrprofile, False)
        init_speicherkennlinien =   cb_set('init_speicherkennlinien',   self.dlg.cb_init_speicherkennlinien, False)
        init_bodenklassen =         cb_set('init_bodenklassen',         self.dlg.cb_init_bodenklassen, False)

        export_difftezg =           cb_set('export_difftezg',           self.dlg.cb_export_difftezg, True)
        export_verschneidung =      cb_set('export_verschneidung',      self.dlg.cb_export_verschneidung, True)

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
        return QCoreApplication.translate('ExportToHE', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/QKan_ExportHE/icon_qk2he.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Export to Hystem-Extran'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Export to HE'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # Anfang Eigene Funktionen -------------------------------------------------
    # (jh, 08.02.2017)


    def selectFile_HeDB_dest(self):
        """Datenbankverbindung zur HE-Datenbank (Firebird) auswaehlen und gegebenenfalls die Zieldatenbank
           erstellen, aber noch nicht verbinden."""

        filename = QFileDialog.getSaveFileName(self.dlg, "Dateinamen der Ziel-HE-Datenbank eingeben",
                                               self.default_dir,"*.idbf")
        # if os.path.dirname(filename) != '':
            # os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB_dest.setText(filename)


    def selectFile_HeDB_template(self):
        """Vorlage-HE-Datenbank (Firebird) auswaehlen."""

        filename = QFileDialog.getOpenFileName(self.dlg, u"Dateinamen der Vorlage-HE-Datenbank eingeben",
                                               self.default_dir,"*.idbf")
        # if os.path.dirname(filename) != '':
            # os.chdir(os.path.dirname(filename))
        self.dlg.tf_heDB_template.setText(filename)


    def selectFile_QKanDB(self):
        """Datenbankverbindung zur QKan-Datenbank (SpatiLite) auswaehlen."""

        filename = QFileDialog.getOpenFileName(self.dlg, u"QKan-Datenbank auswählen",
                                               self.default_dir,"*.sqlite")
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
        self.dlg.cb_export_flaechensw.setChecked(True)
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
        self.dlg.cb_modify_flaechensw.setChecked(True)
        self.dlg.cb_modify_abflussparameter.setChecked(True)
        self.dlg.cb_modify_regenschreiber.setChecked(True)
        self.dlg.cb_modify_rohrprofile.setChecked(True)
        self.dlg.cb_modify_speicherkennlinien.setChecked(True)
        self.dlg.cb_modify_bodenklassen.setChecked(True)

    def initall(self):
        """Aktiviert alle Checkboxen zm Initialisieren"""

        self.dlg.cb_init_schaechte.setChecked(True)
        self.dlg.cb_init_auslaesse.setChecked(True)
        self.dlg.cb_init_speicher.setChecked(True)
        self.dlg.cb_init_haltungen.setChecked(True)
        self.dlg.cb_init_pumpen.setChecked(True)
        self.dlg.cb_init_wehre.setChecked(True)
        self.dlg.cb_init_flaechenrw.setChecked(True)
        self.dlg.cb_init_flaechensw.setChecked(True)
        self.dlg.cb_init_abflussparameter.setChecked(True)
        self.dlg.cb_init_regenschreiber.setChecked(True)
        self.dlg.cb_init_rohrprofile.setChecked(True)
        self.dlg.cb_init_speicherkennlinien.setChecked(True)
        self.dlg.cb_init_bodenklassen.setChecked(True)

    def exportnone(self):
        """Deaktiviert alle Checkboxen zm Export"""

        self.dlg.cb_export_schaechte.setChecked(False)
        self.dlg.cb_export_auslaesse.setChecked(False)
        self.dlg.cb_export_speicher.setChecked(False)
        self.dlg.cb_export_haltungen.setChecked(False)
        self.dlg.cb_export_pumpen.setChecked(False)
        self.dlg.cb_export_wehre.setChecked(False)
        self.dlg.cb_export_flaechenrw.setChecked(False)
        self.dlg.cb_export_flaechensw.setChecked(False)
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
        self.dlg.cb_modify_flaechensw.setChecked(False)
        self.dlg.cb_modify_abflussparameter.setChecked(False)
        self.dlg.cb_modify_regenschreiber.setChecked(False)
        self.dlg.cb_modify_rohrprofile.setChecked(False)
        self.dlg.cb_modify_speicherkennlinien.setChecked(False)
        self.dlg.cb_modify_bodenklassen.setChecked(False)

    def initnone(self):
        """Deaktiviert alle Checkboxen zm Initialisieren"""

        self.dlg.cb_init_schaechte.setChecked(False)
        self.dlg.cb_init_auslaesse.setChecked(False)
        self.dlg.cb_init_speicher.setChecked(False)
        self.dlg.cb_init_haltungen.setChecked(False)
        self.dlg.cb_init_pumpen.setChecked(False)
        self.dlg.cb_init_wehre.setChecked(False)
        self.dlg.cb_init_flaechenrw.setChecked(False)
        self.dlg.cb_init_flaechensw.setChecked(False)
        self.dlg.cb_init_abflussparameter.setChecked(False)
        self.dlg.cb_init_regenschreiber.setChecked(False)
        self.dlg.cb_init_rohrprofile.setChecked(False)
        self.dlg.cb_init_speicherkennlinien.setChecked(False)
        self.dlg.cb_init_bodenklassen.setChecked(False)

    # -------------------------------------------------------------------------
    # Formularfunktionen

    def countselection(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        liste_teilgebiete = self.listselecteditems(self.dlg.lw_teilgebiete)

        # Zu berücksichtigende Flächen zählen
        auswahl = ''
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE flaechen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

        sql = u"""SELECT count(*) AS anzahl FROM flaechen{auswahl}""".format(auswahl=auswahl)

        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_ExportHE (1) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.dlg.lf_anzahl_flaechen.setText('0')


        # Zu berücksichtigende Schächte zählen
        auswahl =''
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE schaechte.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

        sql = """SELECT count(*) AS anzahl FROM schaechte{auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_ExportHE (2) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg.lf_anzahl_schaechte.setText(str(daten[0]))
        else:
            self.dlg.lf_anzahl_schaechte.setText('0')


        # Zu berücksichtigende Haltungen zählen
        auswahl =''
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE haltungen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

        sql = """SELECT count(*) AS anzahl FROM haltungen{auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_ExportHE (2) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.dlg.lf_anzahl_haltungen.setText('0')

    # -------------------------------------------------------------------------
    # Funktion zur Zusammenstellung einer Auswahlliste für eine SQL-Abfrage

    def listselecteditems(self, listWidget):
        """Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

        :param listWidget: String for translation.
        :type listWidget: QListWidgetItem

        :returns: Tuple containing selected teilgebiete
        :rtype: tuple
        """
        items = listWidget.selectedItems()
        liste = []
        for elem in items:
            liste.append(elem.text())
        return liste


    # Ende Eigene Funktionen ---------------------------------------------------


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog

        # Check, ob die relevanten Layer nicht editable sind.
        if len({'flaechen', 'haltungen', 'linkfl', 'tezg', 'schaechte'} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(u"Bedienerfehler: ", 
                   u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!', 
                   level=QgsMessageBar.CRITICAL)
            return False

        # Übernahme der Quelldatenbank:
        # Wenn ein Projekt geladen ist, wird die Quelldatenbank daraus übernommen.
        # Wenn dies nicht der Fall ist, wird die Quelldatenbank aus der
        # json-Datei übernommen.

        database_QKan = ''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in k_link", u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error("k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        if database_QKan != '':
            self.dlg.tf_QKanDB.setText(database_QKan)

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(dbname=database_QKan)      # Datenbankobjekt der QKan-Datenbank zum Lesen
        if self.dbQK is None:
            fehlermeldung("Fehler in QKan_CreateUnbefFl", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage("Fehler in QKan_Import_from_HE", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        # Check, ob alle Teilgebiete in Flächen, Schächten und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL and
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_ExportHE (3) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL and
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_ExportHE (4) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM schaechte 
                WHERE teilgebiet IS NOT NULL and
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_ExportHE (5) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False

        self.dbQK.commit()


        # Anlegen der Tabelle zur Auswahl der Teilgebiete

        # Zunächst wird die Liste der beim letzten Mal gewählten Teilgebiete aus config gelesen
        liste_teilgebiete = []
        if 'liste_teilgebiete' in self.config:
            liste_teilgebiete = self.config['liste_teilgebiete']

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        self.dlg.lw_teilgebiete.clear()

        for ielem, elem in enumerate(daten):
            self.dlg.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
            try:
                if elem[0] in liste_teilgebiete:
                    self.dlg.lw_teilgebiete.setCurrentRow(ielem)
            except BaseException as err:
                fehlermeldung(u'QKan_ExportHE (6), Fehler in elem = {}\n'.format(str(elem)), err)
        # if len(daten) == 1:
            # self.dlg.lw_teilgebiete.setCurrentRow(0)

        # Ereignis bei Auswahländerung in Liste Teilgebiete

        self.dlg.lw_teilgebiete.itemClicked.connect(self.countselection)
        self.countselection()

        # Formular anzeigen

        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            # Abrufen der ausgewählten Elemente in beiden Listen
            liste_teilgebiete = self.listselecteditems(self.dlg.lw_teilgebiete)

            # Eingaben aus Formular übernehmen
            database_Qkan = self.dlg.tf_QKanDB.text()
            database_HE = self.dlg.tf_heDB_dest.text()
            dbtemplate_HE = self.dlg.tf_heDB_template.text()
            datenbanktyp = 'spatialite'

            check_export = {}
            check_export['export_schaechte'] = self.dlg.cb_export_schaechte.isChecked()
            check_export['export_auslaesse'] = self.dlg.cb_export_auslaesse.isChecked()
            check_export['export_speicher'] = self.dlg.cb_export_speicher.isChecked()
            check_export['export_haltungen'] = self.dlg.cb_export_haltungen.isChecked()
            check_export['export_pumpen'] = self.dlg.cb_export_pumpen.isChecked()
            check_export['export_wehre'] = self.dlg.cb_export_wehre.isChecked()
            check_export['export_flaechenrw'] = self.dlg.cb_export_flaechenrw.isChecked()
            check_export['export_flaechensw'] = self.dlg.cb_export_flaechensw.isChecked()
            check_export['export_abflussparameter'] = self.dlg.cb_export_abflussparameter.isChecked()
            check_export['export_regenschreiber'] = self.dlg.cb_export_regenschreiber.isChecked()
            check_export['export_rohrprofile'] = self.dlg.cb_export_rohrprofile.isChecked()
            check_export['export_speicherkennlinien'] = self.dlg.cb_export_speicherkennlinien.isChecked()
            check_export['export_bodenklassen'] = self.dlg.cb_export_bodenklassen.isChecked()

            check_export['modify_schaechte'] = self.dlg.cb_modify_schaechte.isChecked()
            check_export['modify_auslaesse'] = self.dlg.cb_modify_auslaesse.isChecked()
            check_export['modify_speicher'] = self.dlg.cb_modify_speicher.isChecked()
            check_export['modify_haltungen'] = self.dlg.cb_modify_haltungen.isChecked()
            check_export['modify_pumpen'] = self.dlg.cb_modify_pumpen.isChecked()
            check_export['modify_wehre'] = self.dlg.cb_modify_wehre.isChecked()
            check_export['modify_flaechenrw'] = self.dlg.cb_modify_flaechenrw.isChecked()
            check_export['modify_flaechensw'] = self.dlg.cb_modify_flaechensw.isChecked()
            check_export['modify_abflussparameter'] = self.dlg.cb_modify_abflussparameter.isChecked()
            check_export['modify_regenschreiber'] = self.dlg.cb_modify_regenschreiber.isChecked()
            check_export['modify_rohrprofile'] = self.dlg.cb_modify_rohrprofile.isChecked()
            check_export['modify_speicherkennlinien'] = self.dlg.cb_modify_speicherkennlinien.isChecked()
            check_export['modify_bodenklassen'] = self.dlg.cb_modify_bodenklassen.isChecked()

            check_export['init_schaechte'] = self.dlg.cb_init_schaechte.isChecked()
            check_export['init_auslaesse'] = self.dlg.cb_init_auslaesse.isChecked()
            check_export['init_speicher'] = self.dlg.cb_init_speicher.isChecked()
            check_export['init_haltungen'] = self.dlg.cb_init_haltungen.isChecked()
            check_export['init_pumpen'] = self.dlg.cb_init_pumpen.isChecked()
            check_export['init_wehre'] = self.dlg.cb_init_wehre.isChecked()
            check_export['init_flaechenrw'] = self.dlg.cb_init_flaechenrw.isChecked()
            check_export['init_flaechensw'] = self.dlg.cb_init_flaechensw.isChecked()
            check_export['init_abflussparameter'] = self.dlg.cb_init_abflussparameter.isChecked()
            check_export['init_regenschreiber'] = self.dlg.cb_init_regenschreiber.isChecked()
            check_export['init_rohrprofile'] = self.dlg.cb_init_rohrprofile.isChecked()
            check_export['init_speicherkennlinien'] = self.dlg.cb_init_speicherkennlinien.isChecked()
            check_export['init_bodenklassen'] = self.dlg.cb_init_bodenklassen.isChecked()

            check_export['export_difftezg'] = self.dlg.cb_export_difftezg.isChecked()
            check_export['export_verschneidung'] = self.dlg.cb_export_verschneidung.isChecked()

            # Konfigurationsdaten schreiben
            self.config['database_HE'] = database_HE
            self.config['dbtemplate_HE'] = dbtemplate_HE
            self.config['database_Qkan'] = database_Qkan
            self.config['datenbanktyp'] = datenbanktyp
            self.config['liste_teilgebiete'] = liste_teilgebiete
            for el in check_export:
                self.config[el] = check_export[el]

            with codecs.open(self.configfil,'w') as fileconfig:
                # logger.debug(u"Config-Dictionary: {}".format(self.config))
                fileconfig.write(json.dumps(self.config))


            exportKanaldaten(iface, database_HE, dbtemplate_HE, database_Qkan, liste_teilgebiete, 
                             0.1, datenbanktyp, check_export)
