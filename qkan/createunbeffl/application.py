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
import os
import site
import webbrowser
import json

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QTableWidgetItem, QTableWidgetSelectionRange
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

    def helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(self.plugin_dir, '../doc/sphinx/build/html/Qkan_Formulare.html#erzeugen-der-unbefestigten-flachen')
        webbrowser.open_new_tab(helpfile)

    def tw_selAbflparamTeilgebClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlg.cb_selActive.setChecked(True)
        self.countselection()

    def selActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlg.cb_selActive.isChecked():
            # Nix tun ...
            logger.debug('\nChecked = True')
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlg.tw_selAbflparamTeilgeb.rowCount()
            range = QTableWidgetSelectionRange(0,0,anz-1,4)
            self.dlg.tw_selAbflparamTeilgeb.setRangeSelected(range,False)
            logger.debug('\nChecked = False\nQWidget: anzahl = {}'.format(anz))

            # Anzahl in der Anzeige aktualisieren
            self.countselection()

    def countselection(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen TEZG-Flächen"""

        liste_selAbflparamTeilgeb = self.listselectedTabitems(self.dlg.tw_selAbflparamTeilgeb)

        # logger.debug(u'QKan.createunbeffl.application.countselection (1)\nlen(liste_selAbflparamTeilgeb) = {}'.format(len(liste_selAbflparamTeilgeb)))
        # logger.debug(u'QKan.createunbeffl.application.countselection (2)\nliste_selAbflparamTeilgeb = {}'.format(str(liste_selAbflparamTeilgeb)))

        # Aufbereiten für SQL-Abfrage

        # Unterschiedliches Vorgehen, je nachdem ob mindestens eine oder keine Zeile
        # ausgewählt wurde

        # if len(liste_selAbflparamTeilgeb) == 0:
            # anzahl = sum([int(attr[-2]) for attr in self.listetezg])
        # else:
            # anzahl = sum([int(attr[-2]) for attr in liste_selAbflparamTeilgeb])

        # Vorbereitung des Auswahlkriteriums für die SQL-Abfrage: Kombination aus abflussparameter und teilgebiet
        # Dieser Block ist identisch in k_unbef und in application enthalten

        if len(liste_selAbflparamTeilgeb) == 0:
            auswahl = u''
        elif len(liste_selAbflparamTeilgeb) == 1:
            auswahl = u' AND'
        elif len(liste_selAbflparamTeilgeb) >= 2:
            auswahl = u' AND ('
        else:
            fehlermeldung(u"Interner Fehler", u"Fehler in Fallunterscheidung!")
            return False

        # Anfang SQL-Krierien zur Auswahl der tezg-Flächen
        first = True
        for attr in liste_selAbflparamTeilgeb:
            if attr[4] == u'None' or attr[1] == u'None':
                fehlermeldung(u'Datenfehler: ', u'In den ausgewählten Daten sind noch Datenfelder nicht definiert ("NULL").')
                return False
            if first:
                first = False
                auswahl += u""" (tezg.abflussparameter = '{abflussparameter}' AND
                                tezg.teilgebiet = '{teilgebiet}')""".format(abflussparameter=attr[0], teilgebiet=attr[1])
            else:
                auswahl += u""" OR\n      (tezg.abflussparameter = '{abflussparameter}' AND
                                tezg.teilgebiet = '{teilgebiet}')""".format(abflussparameter=attr[0], teilgebiet=attr[1])

        if len(liste_selAbflparamTeilgeb) >= 2:
            auswahl += u")"
        # Ende SQL-Krierien zur Auswahl der tezg-Flächen

        # Ende SQL-Krierien zur Auswahl der tezg-Flächen

        # Trick: Der Zusatz "WHERE 1" dient nur dazu, dass der Block zur Zusammenstellung von 'auswahl' identisch mit dem 
        # Block in 'k_unbef.py' bleiben kann...
        sql = u"""SELECT count(*) AS anz
                FROM tezg WHERE 1{auswahl}
        """.format(auswahl=auswahl)

        if not self.dbQK.sql(sql, u"QKan.CreateUnbefFlaechen (5)"):
            return False

        data = self.dbQK.fetchone()

        if not (data is None):
            self.dlg.lf_anzahl_tezg.setText(u'{}'.format(data[0]))
        else:
            self.dlg.lf_anzahl_tezg.setText(u'0')


    # -------------------------------------------------------------------------
    # Funktion zur Zusammenstellung einer Auswahlliste für eine SQL-Abfrage
    def listselectedTabitems(self, tableWidget, nCols = 5):
        """Erstellt eine Liste aus den in einem Auswahllisten-Widget angeklickten Objektnamen

        :param tableWidget: Tabelle zur Auswahl der Arten von Haltungsflächen.
        :type tableWidget: QTableWidget

        :param nCols:       Anzahl Spalten des tableWidget-Elements
        :type nCols:        integer

        :returns: Tuple mit ausgewählten Abflussparametern
        :rtype: tuple
        """
        items = tableWidget.selectedItems()
        anz = len(items)
        nRows = anz // nCols

        if len(items) > nCols:
            # mehr als eine Zeile ausgewählt
            if tableWidget.row(items[1]) == 1:
                # Elemente wurden spaltenweise übergeben
                liste = [[el.text() for el in items][i:anz:nRows] for i in range(nRows)]
            else:
                # Elemente wurden zeilenweise übergeben
                liste = [[el.text() for el in items][i:i+5] for i in range(0,anz,5)]
        else:
            # Elemente wurden zeilenweise übergeben oder Liste ist leer
            liste = [[el.text() for el in items][i:i+5] for i in range(0,anz,5)]

        return liste


    # ------------------------------------------------------------------------------------------------------------
    # Vorbereiten und Öffnen des Formulars

    def run(self):
        """Run method that performs all the real work"""

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in CreateUnbefFl",
                          u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error(u"CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Abfragen der Tabelle tezg nach verwendeten Abflussparametern
        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if self.dbQK is None:
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

        if not self.dbQK.sql(sql, u'createunbeffl.run (1)'):
            return False

        data = self.dbQK.fetchone()

        if data is None:
            if autokorrektur:
                daten = [u"'$Default_Unbef', u'von QKan ergänzt', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', '13.01.2011 08:44:50'"]

                for ds in daten:
                    sql = u"""INSERT INTO abflussparameter
                             ( 'apnam', 'kommentar', 'anfangsabflussbeiwert', 'endabflussbeiwert', 'benetzungsverlust', 
                               'muldenverlust', 'benetzung_startwert', 'mulden_startwert', 'bodenklasse', 
                               'createdat') Values ({})""".format(ds)
                    if not self.dbQK.sql(sql, u'createunbeffl.run (2)'):
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

        # if not self.dbQK.sql(sql, u'createunbeffl.run (3)'):
            # return False

        # data = self.dbQK.fetchall()

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
        if not self.dbQK.sql(sql, u'createunbeffl.run (4)'):
            return None

        self.listetezg = self.dbQK.fetchall()
        nzeilen = len(self.listetezg)
        self.dlg.tw_selAbflparamTeilgeb.setRowCount(nzeilen)
        self.dlg.tw_selAbflparamTeilgeb.setHorizontalHeaderLabels([u"Abflussparameter", u"Teilgebiet", 
                                                                     u"Bodenklasse", u"Anzahl", u"Anmerkungen"])
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(0, 144)  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(1, 140)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(2, 90)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(3, 50)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(4, 200)
        for i, elem in enumerate(self.listetezg):
            for j, item in enumerate(elem):
                cell = u'{}'.format(elem[j])
                self.dlg.tw_selAbflparamTeilgeb.setItem(i, j, QTableWidgetItem(cell))
                self.dlg.tw_selAbflparamTeilgeb.setRowHeight(i, 20)

        # config in Dialog übernehmen

        # Autokorrektur

        if 'autokorrektur' in self.config:
            autokorrektur = self.config['autokorrektur']
        else:
            autokorrektur = True
        self.dlg.cb_autokorrektur.setChecked(autokorrektur)

        self.dlg.tw_selAbflparamTeilgeb.itemClicked.connect(self.tw_selAbflparamTeilgebClick)
        self.countselection()

        self.dlg.cb_selActive.stateChanged.connect(self.selActiveClick)

        self.dlg.button_box.helpRequested.connect(self.helpClick)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        logger.debug('\n\nresult = {}'.format(repr(result)))
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # Start der Verarbeitung
            liste_selAbflparamTeilgeb = self.listselectedTabitems(self.dlg.tw_selAbflparamTeilgeb)
            logger.debug(u'\nliste_selAbflparamTeilgeb (1): {}'.format(liste_selAbflparamTeilgeb))
            autokorrektur = self.dlg.cb_autokorrektur.isChecked()

            self.config['autokorrektur'] = autokorrektur

            with open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            createUnbefFlaechen(self.dbQK, liste_selAbflparamTeilgeb, autokorrektur)

