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
from PyQt4.QtGui import QListWidgetItem, QTableWidgetItem
from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface, pluginDirectory

# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences 
import resources
# Import the code for the dialog
from application_dialog import QgsadaptDialog
from k_tools import qgsadapt
from qkan import Dummy
from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import fehlermeldung, get_database_QKan

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
            self.config['database_QKan'] = ''
            self.config['projectfile'] = ''
            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

        self.dlg_pr.pb_selectProjectFile.clicked.connect(self.selectFile_projectFile)
        self.dlg_pr.pb_selectqkanDB.clicked.connect(self.selectFile_qkanDB)
        self.dlg_pr.pb_selectProjectTemplate.clicked.connect(self.selectFile_projectTemplate)

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

    def unload(self):
        pass

    # Formularfunktionen --------------------------------------------------------------------------------------

    def selectFile_projectFile(self):
        """Zu erstellende Projektdatei festlegen"""

        filename = QFileDialog.getSaveFileName(self.dlg,
                                               "Dateinamen der zu erstellenden Projektdatei eingeben",
                                               self.default_dir,
                                               "*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlg.tf_projectFile.setText(filename)


    def selectFile_qkanDB(self):
        """Anzubindende QKan-Datenbank festlegen"""

        filename = QFileDialog.getOpenFileName(self.dlg,
                                               "QKan-Datenbank auswählen",
                                               self.default_dir,
                                               "*.sqlite")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlg.tf_qkanDB.setText(filename)


    def selectFile_projectTemplate(self):
        """DYNA (*.ein) -datei auswählen"""

        filename = QFileDialog.getOpenFileName(self.dlg,
                                               "Vorlage für zu erstellende Projektdatei auswählen",
                                               self.templateDir,
                                               "*.qgs")
        if os.path.dirname(filename) != '':
            os.chdir(os.path.dirname(filename))
            self.dlg.tf_projectTemplate.setText(filename)


    # ----------------------------------------------------------------------------------------------------------
    # Erstellen einer Projektdatei aus einer Vorlage

    def run_qgsadapt(self):
        '''Erstellen einer Projektdatei aus einer Vorlage'''

        # Formularfelder setzen -------------------------------------------------------------------------

        # Formularfeld Datenbank

        # Falls eine Datenbank angebunden ist, wird diese zunächst in das Formular eingetragen.
        database_QKan, epsg = get_database_QKan(silent = True)

        if database_QKan:
            self.default_dir = os.path.dirname(database_QKan)       # bereits geladene QKan-Datenbank übernehmen
        elif 'database_QKan' in self.config:
            database_QKan = self.config['database_QKan']
            self.dlg_pr.tf_qkanDB.setText(database_QKan)
            self.default_dir = os.path.dirname(database_QKan)
        else:
            database_QKan = ''
            self.default_dir = '.'
        self.dlg_pr.tf_qkanDB.setText(database_QKan)

        # Formularfeld Vorlagedatei
        if 'projectTemplate' in self.config:
            projectTemplate = self.config['projectTemplate']
        else:
            projectTemplate = ''

        # Formularfeld Projektdatei
        if 'projectFile' in self.config:
            projectFile = self.config['projectFile']
        else:
            projectFile = ''

        # Option: Suchpfad für Vorlagedatei auf template-Verzeichnis setzen 
        if 'setPathToTemplateDir' in self.config:
            setPathToTemplateDir = self.config['setPathToTemplateDir']
        else:
            setPathToTemplateDir = True
        self.dlg_pr.cb_setPathToTemplateDir.setChecked(setPathToTemplateDir)
        if setPathToTemplateDir:
            self.templateDir = os.path.join(pluginDirectory('qkan'), u"database/templates")
        else:
            try:
                self.templateDir = os.path.dirname(database_QKan)
            except:
                logger.error('Programmfehler in tools.run_qgsadapt:\nPfad konnte nicht auf ' + \
                             'database_QKan gesetzt werden.\n database_QKan = {}'.format(database_QKan))
                self.templateDir = ''

        # Option: Eingabeformulare kopieren bzw. aktualisieren
        if 'copy_forms' in self.config:
            copy_forms = self.config['copy_forms']
        else:
            copy_forms = True
        self.dlg_pr.cb_copy_forms.setChecked(copy_forms)

        # Option: QKan-Datenbank aktualisieren
        if 'qkanDBUpdate' in self.config:
            qkanDBUpdate = self.config['qkanDBUpdate']
        else:
            qkanDBUpdate = True
        self.dlg_pr.cb_qkanDBUpdate.setChecked(qkanDBUpdate)

        # show the dialog
        self.dlg_pr.show()
        # Run the dialog event loop
        result = self.dlg_pr.exec_()

        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen --------------------------------------------------------------

            projectTemplate = self.dlg_pr.tf_projectTemplate.text()
            database_QKan = self.dlg_pr.tf_database_QKan.text()
            projectFile = self.dlg_pr.tf_projectFile.text()
            setPathToTemplateDir = self.dlg_pr.cb_setPathToTemplateDir.isChecked()
            copy_forms = self.dlg_pr.cb_copy_forms.isChecked()
            qkanDBUpdate = self.dlg_pr.cb_qkanDBUpdate.isChecked()


            # Konfigurationsdaten schreiben -----------------------------------------------------------

            self.config['projectTemplate'] = projectTemplate
            self.config['database_QKan'] = database_QKan
            self.config['projectFile'] = projectFile
            self.config['setPathToTemplateDir'] = setPathToTemplateDir
            self.config['copy_forms'] = copy_forms
            self.config['qkanDBUpdate'] = qkanDBUpdate

            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))


            qgsadapt(projectTemplate, database_QKan, projectFile, setPathToTemplateDir, 
                    copy_forms, u'SpatiaLite')
