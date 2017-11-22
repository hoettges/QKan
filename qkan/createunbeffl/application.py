# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CreateUnbefFl
                                 A QGIS plugin
 Erzeugt unbefestigte Flächen aus der Differenz von TEZG-Flächen und befestigten Flächen
                              -------------------
        begin                : 2017-06-20
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
import logging
import os.path
# Ergaenzt (jh, 12.06.2017) -------------------------------------------------
import site
import codecs
import json

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QTableWidgetItem
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# noinspection PyUnresolvedReferences
import resources
# Import the code for the dialog
from application_dialog import CreateUnbefFlDialog
from k_unbef import createUnbefFlaechen
from qkan import Dummy
from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import get_database_QKan, fortschritt, fehlermeldung

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger('QKan')


class CreateUnbefFl:
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
            'CreateUnbefFl_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = CreateUnbefFlDialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 12.06.2017)

        logger.info('\n\nQKan_CreateUnbefFlaechen initialisiert...')

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
            with codecs.open(self.configfil, 'r', 'utf-8') as fileconfig:
                self.config = json.loads(fileconfig.read().replace('\\', '/'))
        else:
            self.config = {'epsg': '25832'}  # Projektionssystem
            self.config['database_QKan'] = ''
            self.config['database_HE'] = ''
            self.config['projectfile'] = ''
            with codecs.open(self.configfil, 'w', 'utf-8') as fileconfig:
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
        return QCoreApplication.translate('CreateUnbefFl', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/qkan/createunbeffl/icon.png'
        Dummy.instance.add_action(
            icon_path,
            text=self.tr(u'Erzeuge unbefestigte Flächen...'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        pass

    # -------------------------------------------------------------------------
    # Funktion zur Zusammenstellung einer Auswahlliste für eine SQL-Abfrage
    def listselectedTabitems(self, listWidget):
        """Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

        :param listWidget: String for translation.
        :type listWidget: QListWidgetItem

        :returns: Tuple containing selected teilgebiete
        :rtype: tuple
        """
        items = listWidget.selectedItems()
        liste = []
        rowakt = None  # aktuelle Zeile
        sel = []  # Liste mit in einer Zeile ausgewählten Attributen: ablussparameter, teilgebiet
        for elem in items:
            # Initialisierung
            if rowakt is None:
                rowakt = elem.row()

            # Falls neue Zeile, vorherige in liste hinzufügen
            if rowakt != elem.row():
                liste.append(sel)
                sel = []
                rowakt = elem.row()

            # Text hinzufügen, aber dabei Spalte "Anzahl" ignorieren
            if elem.column() != 2:
                sel.append(elem.text())
        # zum Schluss noch das letzte Element hinzufügen
        if len(items) > 0:
            liste.append(sel)

        return liste

    # ------------------------------------------------------------------------------------------------------------
    # Vorbereiten und Öffnen des Formulars

    def run(self):
        """Run method that performs all the real work"""

        database_QKan = ''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in CreateUnbefFl",
                          u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error("CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Abfragen der Tabelle tezg nach verwendeten Abflussparametern
        dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if dbQK is None:
            fehlermeldung("Fehler in QKan_CreateUnbefFl",
                          u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage("Fehler in QKan_Import_from_HE",
                                           u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                                               database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        sql = u"""SELECT abflussparameter, teilgebiet, count(*) AS anz FROM tezg GROUP BY abflussparameter, teilgebiet"""
        if not dbQK.sql(sql, 'createunbeffl.run'):
            return None

        daten = dbQK.fetchall()
        nzeilen = len(daten)
        self.dlg.tw_cnt_abflussparameter.setRowCount(nzeilen)
        self.dlg.tw_cnt_abflussparameter.setHorizontalHeaderLabels(["Abflussparameter", "Teilgebiet", "Anzahl"])
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(0, 184)  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(1, 150)
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(2, 50)
        for i, elem in enumerate(daten):
            for j, item in enumerate(elem):
                self.dlg.tw_cnt_abflussparameter.setItem(i, j, QTableWidgetItem(str(elem[j])))
                self.dlg.tw_cnt_abflussparameter.setRowHeight(i, 20)

        # config in Dialog übernehmen

        # Autokorrektur

        if 'autokorrektur' in self.config:
            autokorrektur = self.config['autokorrektur']
        else:
            autokorrektur = True
        self.dlg.cb_autokorrektur.setChecked(autokorrektur)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # Start der Verarbeitung
            liste_tezg = self.listselectedTabitems(self.dlg.tw_cnt_abflussparameter)
            autokorrektur = self.dlg.cb_autokorrektur.isChecked()

            self.config['autokorrektur'] = autokorrektur

            with codecs.open(self.configfil,'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            createUnbefFlaechen(dbQK, liste_tezg, autokorrektur)

            # else:
            # logger.debug('Selected: \n{}'.format(self.listselectedTabitems(self.dlg.tw_cnt_abflussparameter)))
            # logger.debug('Methoden von QTableWidgetItem:\n{}'.format(str(dir(self.dlg.tw_cnt_abflussparameter))))
