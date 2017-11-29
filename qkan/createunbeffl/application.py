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

        logger.info(u'\n\nQKan_CreateUnbefFlaechen initialisiert...')

        # --------------------------------------------------------------------------
        # Pfad zum Arbeitsverzeichnis sicherstellen
        wordir = os.path.join(site.getuserbase(), u'qkan')

        if not os.path.isdir(wordir):
            os.makedirs(wordir)

        # --------------------------------------------------------------------------------------------------
        # Konfigurationsdatei qkan.json lesen
        #

        self.configfil = os.path.join(wordir, u'qkan.json')
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
    # Formularfunktionen

    def countselection(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen TEZG-Flächen"""

        liste_selected = self.listselectedTabitems(self.dlg.tw_cnt_abflussparameter)
        # Aufbereiten für SQL-Abfrage

        # Unterschiedliches Vorgehen, je nachdem ob mindestens eine oder keine Zeile
        # ausgewählt wurde

        if len(liste_selected) == 0:
            anzahl = sum([int(attr[-2]) for attr in self.listetezg])
        else:
            anzahl = sum([int(attr[-2]) for attr in liste_selected])

        if not (anzahl is None):
            self.dlg.lf_anzahl_tezg.setText(u'{}'.format(anzahl))
        else:
            self.dlg.lf_anzahl_tezg.setText(u'0')


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
            sel.append(elem.text())
        # zum Schluss noch das letzte Element hinzufügen
        if len(items) > 0:
            liste.append(sel)

        return liste

    # ------------------------------------------------------------------------------------------------------------
    # Vorbereiten und Öffnen des Formulars

    def run(self):
        """Run method that performs all the real work"""

        database_QKan = u''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in CreateUnbefFl",
                          u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error(u"CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Abfragen der Tabelle tezg nach verwendeten Abflussparametern
        dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if dbQK is None:
            fehlermeldung(u"Fehler in QKan_CreateUnbefFl",
                          u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage(u"Fehler in QKan_Import_from_HE",
                                           u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                                               database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        # Kontrolle, ob in Tabelle "abflussparameter" ein Datensatz für unbefestigte Flächen vorhanden ist
        # (Standard: apnam = '$Default_Unbef')

        sql = u"""SELECT apnam
            FROM abflussparameter
            WHERE bodenklasse IS NOT NULL AND trim(bodenklasse) <> ''"""

        if not dbQK.sql(sql, u'createunbeffl.run (1)'):
            return False

        data = dbQK.fetchone()

        if data is None:
            if autokorrektur:
                daten = [u"'$Default_Unbef', u'von QKan ergänzt', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', '13.01.2011 08:44:50'"]

                for ds in daten:
                    sql = u"""INSERT INTO abflussparameter
                             ( 'apnam', 'kommentar', 'anfangsabflussbeiwert', 'endabflussbeiwert', 'benetzungsverlust', 
                               'muldenverlust', 'benetzung_startwert', 'mulden_startwert', 'bodenklasse', 
                               'createdat') Values ({})""".format(ds)
                    if not dbQK.sql(sql, u'createunbeffl.run (2)'):
                        return False
            else:
                fehlermeldung(u'Datenfehler: ', u'Bitte ergänzen Sie in der Tabelle "abflussparameter" einen Datensatz für unbefestigte Flächen ("bodenklasse" darf nicht leer oder NULL sein)')

        # # Kontrolle, ob noch Flächen in Tabelle "tezg" ohne Zuordnung zu einem Abflussparameter oder zu einem 
        # # Abflussparameter, bei dem keine Bodenklasse definiert ist (Kennzeichen für undurchlässige Flächen).

        # sql = u"""SELECT te.abflussparameter, te.teilgebiet, count(*) AS anz 
            # FROM tezg AS te
            # LEFT JOIN abflussparameter AS ap
            # ON te.abflussparameter = ap.apnam
            # WHERE ap.bodenklasse IS NULL
            # GROUP BY abflussparameter, teilgebiet"""

        # if not dbQK.sql(sql, u'createunbeffl.run (3)'):
            # return False

        # data = dbQK.fetchall()

        # if len(data) > 0:
            # liste = [u'{}\t{}\t{}'.format(el1, el2, el3) for el1, el2, el3 in data]
            # liste.insert(0, u'\nAbflussparameter\tTeilgebiet\tAnzahl')
            
            # fehlermeldung(u'In Tabelle "tezg" fehlen Abflussparameter oder gehören zu befestigten Flächen (Bodenklasse = NULL):\n', 
                          # u'\n'.join(liste))
            # return False

        sql = u"""SELECT te.abflussparameter, te.teilgebiet, bk.bknam, count(*) AS anz, 
                CASE WHEN te.abflussparameter ISNULL THEN 'Fehler: Kein Abflussparameter angegeben' ELSE
                    CASE WHEN bk.infiltrationsrateanfang ISNULL THEN 'Fehler: Keine Bodenklasse angegeben' 
                         WHEN bk.infiltrationsrateanfang < 0.00001 THEN 'Fehler: undurchlässige Bodenart'
                         ELSE ''
                    END
                END AS status
                            FROM tezg AS te
                            LEFT JOIN abflussparameter AS ap
                            ON te.abflussparameter = ap.apnam
                            LEFT JOIN bodenklassen AS bk
                            ON bk.bknam = ap.bodenklasse
                            GROUP BY abflussparameter, teilgebiet"""
        if not dbQK.sql(sql, u'createunbeffl.run (4)'):
            return None

        self.listetezg = dbQK.fetchall()
        nzeilen = len(self.listetezg)
        self.dlg.tw_cnt_abflussparameter.setRowCount(nzeilen)
        self.dlg.tw_cnt_abflussparameter.setHorizontalHeaderLabels([u"Abflussparameter", u"Teilgebiet", 
                                                                     u"Bodenklasse", u"Anzahl", u"Anmerkungen"])
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(0, 144)  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(1, 140)
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(2, 90)
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(3, 50)
        self.dlg.tw_cnt_abflussparameter.setColumnWidth(4, 200)
        for i, elem in enumerate(self.listetezg):
            for j, item in enumerate(elem):
                cell = u'{}'.format(elem[j])
                self.dlg.tw_cnt_abflussparameter.setItem(i, j, QTableWidgetItem(cell))
                self.dlg.tw_cnt_abflussparameter.setRowHeight(i, 20)

        # config in Dialog übernehmen

        # Autokorrektur

        if 'autokorrektur' in self.config:
            autokorrektur = self.config['autokorrektur']
        else:
            autokorrektur = True
        self.dlg.cb_autokorrektur.setChecked(autokorrektur)

        self.dlg.tw_cnt_abflussparameter.itemClicked.connect(self.countselection)
        self.countselection()
 
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
            liste_abflussparam = self.listselectedTabitems(self.dlg.tw_cnt_abflussparameter)
            logger.debug(u'\nliste_abflussparam (1): {}'.format(liste_abflussparam))
            autokorrektur = self.dlg.cb_autokorrektur.isChecked()

            self.config['autokorrektur'] = autokorrektur

            with codecs.open(self.configfil,'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            createUnbefFlaechen(dbQK, liste_abflussparam, autokorrektur)

            # else:
            # logger.debug(u'Selected: \n{}'.format(self.listselectedTabitems(self.dlg.tw_cnt_abflussparameter)))
            # logger.debug(u'Methoden von QTableWidgetItem:\n{}'.format(str(dir(self.dlg.tw_cnt_abflussparameter))))
