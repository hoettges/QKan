# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Flaechenzuordnungen
                                 A QGIS plugin
 Diverse Tools zur QKan-Datenbank
                              -------------------
        begin                : 2017-06-12
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Jörg Höttges/FH Aachen
        email                : hoettges@fh-aachen.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import json
import logging
import os.path
import site

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QFileDialog, QListWidgetItem, QTableWidgetItem
from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface, pluginDirectory
from qgis.gui import QgsGenericProjectionSelector

# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences 
import resources
# Import the code for the dialog
from application_dialog import QgsadaptDialog, QKanOptionsDialog
from k_tools import qgsadapt
from qkan import Dummy
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger(u'QKan')


class QgsUpdate:
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
            'Flaechenzuordnungen_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg_pr = QgsadaptDialog()
        self.dlg_op = QKanOptionsDialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 12.06.2017)

        logger.info(u'\n\nQKan_Tools initialisiert...')

        # --------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(), 'qkan')

        if not os.path.isdir(wordir):
            os.makedirs(wordir)

        # --------------------------------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        self.configfil = os.path.join(wordir, 'qkan.json')
        if os.path.exists(self.configfil):
            with open(self.configfil, 'r') as fileconfig:
                self.config = json.loads(fileconfig.read())
        else:
            self.config = {'epsg': '25832'}  # Projektionssystem
            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

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
        return QCoreApplication.translate('Flaechenzuordnungen', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_qgsadapt_path = ':/plugins/qkan/tools/res/icon_qgsadapt.png'
        Dummy.instance.add_action(
            icon_qgsadapt_path, 
            text=self.tr(u'Projektdatei auf bestehende QKan-Datenbank übertragen'), 
            callback=self.run_qgsadapt, 
            parent=self.iface.mainWindow())

        icon_qkanoptions_path = ':/plugins/qkan/tools/res/icon_qkanoptions.png'
        Dummy.instance.add_action(
            icon_qkanoptions_path, 
            text=self.tr(u'Allgemeine Optionen'), 
            callback=self.run_qkanoptions, 
            parent=self.iface.mainWindow())

    def unload(self):
        pass

    # ----------------------------------------------------------------------------------------------------------
    # Erstellen einer Projektdatei aus einer Vorlage

    # 1. Formularfunktionen

    def selectFile_projectFile(self):
        """Zu erstellende Projektdatei festlegen"""

        filename = QFileDialog.getSaveFileName(self.dlg_pr,
                                               "Dateinamen der zu erstellenden Projektdatei eingeben",
                                               self.default_dir,
                                               "*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlg_pr.tf_projectFile.setText(filename)


    def selectFile_qkanDB(self):
        """Anzubindende QKan-Datenbank festlegen"""

        filename = QFileDialog.getOpenFileName(self.dlg_pr,
                                               "QKan-Datenbank auswählen",
                                               self.default_dir,
                                               "*.sqlite")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlg_pr.tf_qkanDB.setText(filename)


    def selectFile_projectTemplate(self):
        """Vorlage-Projektdatei auswählen"""

        self.setPathToTemplateDir = self.dlg_pr.cb_setPathToTemplateDir.isChecked()
        if self.setPathToTemplateDir:
            self.templateDir = os.path.join(pluginDirectory('qkan'), u"database/templates")
        else:
            try:
                self.templateDir = os.path.dirname(self.database_QKan)
            except:
                logger.error('Programmfehler in tools.run_qgsadapt:\nPfad konnte nicht auf ' + \
                             'database_QKan gesetzt werden.\n database_QKan = {}'.format(
                               self.database_QKan))
                self.templateDir = ''

        filename = QFileDialog.getOpenFileName(self.dlg_pr,
                                               "Vorlage für zu erstellende Projektdatei auswählen",
                                               self.templateDir,
                                               "*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlg_pr.tf_projectTemplate.setText(filename)

    # ----------------------------------------------------------------------------------------------------------
    # 2. Aufruf des Formulars

    def run_qgsadapt(self):
        '''Erstellen einer Projektdatei aus einer Vorlage'''

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        self.database_QKan, epsg = get_database_QKan(silent = True)

        if self.database_QKan:
            self.default_dir = os.path.dirname(self.database_QKan)       # bereits geladene QKan-Datenbank übernehmen
        elif 'database_QKan' in self.config:
            self.database_QKan = self.config['database_QKan']
            self.dlg_pr.tf_qkanDB.setText(self.database_QKan)
            self.default_dir = os.path.dirname(self.database_QKan)
        else:
            self.database_QKan = ''
            self.default_dir = '.'
        self.dlg_pr.tf_qkanDB.setText(self.database_QKan)

        # Formularfeld Vorlagedatei
        if 'projectTemplate' in self.config:
            projectTemplate = self.config['projectTemplate']
        else:
            projectTemplate = ''

        # Formularfeld Projektdatei
        if 'projectfile' in self.config:
            projectfile = self.config['projectfile']
        else:
            projectfile = ''

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen 
        if 'setPathToTemplateDir' in self.config:
            self.setPathToTemplateDir = self.config['setPathToTemplateDir']
        else:
            self.setPathToTemplateDir = True
        self.dlg_pr.cb_setPathToTemplateDir.setChecked(self.setPathToTemplateDir)

        # Option: QKan-Datenbank aktualisieren
        if 'qkanDBUpdate' in self.config:
            qkanDBUpdate = self.config['qkanDBUpdate']
        else:
            qkanDBUpdate = True
        self.dlg_pr.cb_qkanDBUpdate.setChecked(qkanDBUpdate)

        # Ereignisse anbinden
        self.dlg_pr.pb_selectProjectFile.clicked.connect(self.selectFile_projectFile)
        self.dlg_pr.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)
        self.dlg_pr.pb_selectProjectTemplate.clicked.connect(self.selectFile_projectTemplate)

        # show the dialog
        self.dlg_pr.show()
        # Run the dialog event loop
        result = self.dlg_pr.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            projectTemplate = self.dlg_pr.tf_projectTemplate.text()
            self.database_QKan = self.dlg_pr.tf_qkanDB.text()
            projectfile = self.dlg_pr.tf_projectFile.text()
            self.setPathToTemplateDir = self.dlg_pr.cb_setPathToTemplateDir.isChecked()
            qkanDBUpdate = self.dlg_pr.cb_qkanDBUpdate.isChecked()


            # Konfigurationsdaten schreiben -----------------------------------------------------------

            self.config['projectTemplate'] = projectTemplate
            self.config['database_QKan'] = self.database_QKan
            self.config['projectfile'] = projectfile
            self.config['setPathToTemplateDir'] = self.setPathToTemplateDir
            self.config['qkanDBUpdate'] = qkanDBUpdate

            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            qgsadapt(projectTemplate, self.database_QKan, epsg, projectfile, self.setPathToTemplateDir, 
                     u'SpatiaLite')

    # ----------------------------------------------------------------------------------------------------------
    # Allgemeine Optionen

    # 1. Formularfunktionen

    def selectKBS(self):
        """KBS auswählen. Setzt das KBS für die weiteren Funktionen

        :returns: void
        """
        projSelector = QgsGenericProjectionSelector()
        projSelector.exec_()
        erg = projSelector.selectedAuthId()
        if len(erg.split(u':')) == 2:
            self.dlg_op.tf_epsg.setText(erg.split(u':')[1])
        else:
            self.dlg_op.tf_epsg.setText(erg)

    def fangradiusDefault(self):
        self.dlg_op.tf_fangradius.setText('0.1')

    def mindestflaecheDefault(self):
        self.dlg_op.tf_mindestflaeche.setText('0.5')

    def max_loopsDefault(self):
        self.dlg_op.tf_max_loops.setText('1000')

    # -----------------------------------------------------------------------------------------
    # 2. Aufruf des Formulars

    def run_qkanoptions(self):
        '''Bearbeitung allgemeiner QKan-Optionen'''

        # Formularfelder setzen -------------------------------------------------------------------------

        # Fangradius für Anfang der Anbindungslinie
        if 'fangradius' in self.config:
            fangradius = self.config['fangradius']
        else:
            fangradius = u'0.1'
        self.dlg_op.tf_fangradius.setText(str(fangradius))

        # Mindestflächengröße
        if 'mindestflaeche' in self.config:
            mindestflaeche = self.config['mindestflaeche']
        else:
            mindestflaeche = u'0.5'
        self.dlg_op.tf_mindestflaeche.setText(str(mindestflaeche))

        # Maximalzahl Schleifendurchläufe
        if 'max_loops' in self.config:
            max_loops = self.config['max_loops']
        else:
            max_loops = '1000'
        self.dlg_op.tf_max_loops.setText(str(max_loops))

        # Optionen zum Typ der QKan-Datenbank
        if 'datenbanktyp' in self.config:
            datenbanktyp = self.config['datenbanktyp']
        else:
            datenbanktyp = u'spatialite'

        if datenbanktyp == u'spatialite':
            self.dlg_op.rb_spatialite.setChecked(True)
        # elif datenbanktyp == u'postgis':
            # self.dlg_op.rb_postgis.setChecked(True)

        if 'epsg' in self.config:
            self.epsg = self.config['epsg']
        else:
            self.epsg = u'25832'
        self.dlg_op.tf_epsg.setText(self.epsg)

        # Ereignisse anbinden

        self.dlg_op.pb_fangradiusDefault.clicked.connect(self.fangradiusDefault)
        self.dlg_op.pb_mindestflaecheDefault.clicked.connect(self.mindestflaecheDefault)
        self.dlg_op.pb_max_loopsDefault.clicked.connect(self.max_loopsDefault)
        self.dlg_op.pb_selectKBS.clicked.connect(self.selectKBS)

        # show the dialog
        self.dlg_op.show()
        # Run the dialog event loop
        result = self.dlg_op.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            fangradius = self.dlg_op.tf_fangradius.text()
            mindestflaeche = self.dlg_op.tf_mindestflaeche.text()
            max_loops = self.dlg_op.tf_max_loops.text()
            if self.dlg_op.rb_spatialite.isChecked():
                datenbanktyp = u'spatialite'
            # elif self.dlg_op.rb_postgis.isChecked():
                # datenbanktyp = u'postgis'
            else:
                fehlermeldung(u"tools.application.run", 
                              u"Fehlerhafte Option: \ndatenbanktyp = {}".format(repr(datenbanktyp)))
            epsg = self.dlg_op.tf_epsg.text()

            self.config['fangradius'] = fangradius
            self.config['mindestflaeche'] = mindestflaeche
            self.config['max_loops'] = max_loops
            self.config['datenbanktyp'] = datenbanktyp
            self.config['epsg'] = epsg

            with open(self.configfil, 'w') as fileconfig:
                # logger.debug(u"Config-Dictionary: {}".format(self.config))
                fileconfig.write(json.dumps(self.config))
