# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Flaechenzuordnungen
                                 A QGIS plugin
 Verknüpft Flächen mit nächster Haltung
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
import codecs
# Ergaenzt (jh, 12.06.2017) -------------------------------------------------
import json
import logging
import os.path
import site

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QListWidgetItem, QTableWidgetItem
from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# Initialize Qt resources from file resources.py
# noinspection PyUnresolvedReferences 
import resources
# Import the code for the dialog
from application_dialog import CreatelineflDialog, CreatelineswDialog, AssigntgebDialog, ManagegroupsDialog
from k_link import createlinkfl, createlinksw, assigntgeb, storegroup, reloadgroup
from qkan import Dummy
from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import get_database_QKan, get_editable_layers, fehlermeldung

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger(u'QKan')


class LinkFl:
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
        self.dlg_cl = CreatelineflDialog()
        self.dlg_sw = CreatelineswDialog()
        self.dlg_at = AssigntgebDialog()
        self.dlg_mg = ManagegroupsDialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 12.06.2017)

        logger.info(u'\n\nQKan_LinkFlaechen initialisiert...')

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
        return QCoreApplication.translate('Flaechenzuordnungen', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_assigntgeb_path = ':/plugins/qkan/linkflaechen/resources/icon_assigntgeb.png'
        Dummy.instance.add_action(
            icon_assigntgeb_path, 
            text=self.tr(u'Alle Elemente des Entwässerungsnetzes zu Teilgebiet zuordnen'), 
            callback=self.run_assigntgeb, 
            parent=self.iface.mainWindow())

        icon_createlinefl_path = ':/plugins/qkan/linkflaechen/resources/icon_createlinefl.png'
        Dummy.instance.add_action(
            icon_createlinefl_path, 
            text=self.tr(u'Erzeuge Verknüpfungslinien von Flaechen zu Haltungen'), 
            callback=self.run_createlinefl, 
            parent=self.iface.mainWindow())

        icon_createlinesw_path = ':/plugins/qkan/linkflaechen/resources/icon_createlinesw.png'
        Dummy.instance.add_action(
            icon_createlinesw_path, 
            text=self.tr(u'Erzeuge Verknüpfungslinien von Direkteinleitungen zu Haltungen'), 
            callback=self.run_createlinesw, 
            parent=self.iface.mainWindow())

        icon_managegroups_path = ':/plugins/qkan/linkflaechen/resources/icon_managegroups.png'
        Dummy.instance.add_action(
            icon_managegroups_path, 
            text=self.tr(u'Teilgebietszuordnungen als Gruppen verwalten'), 
            callback=self.run_managegroups, 
            parent=self.iface.mainWindow())

    def unload(self):
        pass

    # -------------------------------------------------------------------------
    # Formularfunktionen

    def countselectionfl(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        liste_flaechen_abflussparam = self.listselecteditems(self.dlg_cl.lw_flaechen_abflussparam)
        liste_hal_entw = self.listselecteditems(self.dlg_cl.lw_hal_entw)
        liste_teilgebiete = self.listselecteditems(self.dlg_cl.lw_teilgebiete)
        # Aufbereiten für SQL-Abfrage

        # Zu berücksichtigende ganze Flächen zählen
        if len(liste_flaechen_abflussparam) == 0:
            # Keine Auswahl. Soll eigentlich nicht vorkommen, funktioniert aber...
            auswahl = u''
            logger.debug(u'liste_flaechen_abflussparam:\n{}'.format(liste_flaechen_abflussparam))
        else:
            auswahl = u" AND flaechen.abflussparameter in ('{}')".format(u"', '".join(liste_flaechen_abflussparam))

        if len(liste_teilgebiete) != 0:
            auswahl += u" and flaechen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))

        sql = u"""SELECT count(*) AS anzahl FROM flaechen
                WHERE (aufteilen <> 'ja' OR aufteilen IS NULL){auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen.countselectionfl (9) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_flaechen.setText(u'0')

        # Zu berücksichtigende zu verschneidende Flächen zählen

        sql = u"""SELECT count(*) AS anzahl FROM flaechen
                WHERE aufteilen = 'ja'{auswahl}""".format(auswahl=auswahl)
        logger.debug(u'sql Flaechen zu verschneiden:\n{}'.format(sql))
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen.countselectionfl (9) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_flaechsec.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_flaechsec.setText(u'0')

        # Zu berücksichtigende Haltungen zählen
        if len(liste_hal_entw) == 0:
            auswahl = u''
        else:
            auswahl = u" WHERE haltungen.entwart in ('{}')".format(u"', '".join(liste_hal_entw))

        if len(liste_teilgebiete) != 0:
            if auswahl == u'':
                auswahl = u" WHERE haltungen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
            else:
                auswahl += u" and haltungen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))

        sql = u"""SELECT count(*) AS anzahl FROM haltungen{auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen.countselectionfl (10) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_haltungen.setText(u'0')


    def countselectionsw(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Haltungen"""
        liste_hal_entw = self.listselecteditems(self.dlg_sw.lw_hal_entw)
        liste_teilgebiete = self.listselecteditems(self.dlg_sw.lw_teilgebiete)
        # Aufbereiten für SQL-Abfrage

        # Zu berücksichtigende Haltungen zählen
        if len(liste_hal_entw) == 0:
            auswahl = u''
        else:
            auswahl = u" WHERE haltungen.entwart in ('{}')".format(u"', '".join(liste_hal_entw))

        if len(liste_teilgebiete) != 0:
            if auswahl == u'':
                auswahl = u" WHERE haltungen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
            else:
                auswahl += u" and haltungen.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))

        sql = u"""SELECT count(*) AS anzahl FROM haltungen{auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen.countselectionsw (10) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_sw.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.dlg_sw.lf_anzahl_haltungen.setText(u'0')

        # Zu berücksichtigende SW-Punkte zählen

        if len(liste_teilgebiete) != 0:
            auswahl = u" WHERE einleit.teilgebiet in ('{}')".format(u"', '".join(liste_teilgebiete))
        else:
            auswahl = u''

        sql = u"""SELECT count(*) AS anzahl FROM einleit{auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen.countselectionsw (11) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_sw.lf_anzahl_einleit.setText(str(daten[0]))
        else:
            self.dlg_sw.lf_anzahl_einleit.setText(u'0')


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


    # ----------------------------------------------------------------------------
    # Funktion zum Auflisten der Gruppen
    def showgroups(self):
        """Abfragen der Tabelle gruppen nach verwendeten vorhandenen Gruppen"""

        sql = u"""SELECT grnam FROM gruppen GROUP BY grnam"""
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()

        self.dlg_mg.lw_gruppen.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_mg.lw_gruppen.addItem(QListWidgetItem(elem[0]))

    # ----------------------------------------------------------------------------
    # Funktion zum Abfragen der zugeordneten Teilgebiete, betroffenen Tabellen und
    # Anzahl für eine ausgewählte Gruppe
    def listGroupAttr(self):

        # Angeklickte Gruppe aus QListWidget
        gr = self.listselecteditems(self.dlg_mg.lw_gruppen)
        if len(gr) > 0:
            self.gruppe = self.listselecteditems(self.dlg_mg.lw_gruppen)[0]     # Im Formular gesetzt: selectionMode = SingleSelection

            sql = u"""
                SELECT teilgebiet, tabelle, printf('%i',count(*)) AS Anzahl
                FROM gruppen
                WHERE grnam = '{gruppe}'
                GROUP BY tabelle, teilgebiet
                ORDER BY tabelle, teilgebiet
                """.format(gruppe=self.gruppe)
            self.dbQK.sql(sql)
            daten = self.dbQK.fetchall()
            logger.debug(u'\ndaten: {}'.format(str(daten)))  # debug
            nzeilen = len(daten)
            self.dlg_mg.tw_gruppenattr.setRowCount(nzeilen)
            # self.dlg_mg.tw_gruppenattr.setHorizontalHeaderLabels([u"Teilgebiet", u"Tabelle", u"Anzahl"])
            self.dlg_mg.tw_gruppenattr.setColumnWidth(0, 174)  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
            self.dlg_mg.tw_gruppenattr.setColumnWidth(1, 80)
            self.dlg_mg.tw_gruppenattr.setColumnWidth(2, 50)
            for i, elem in enumerate(daten):
                for j, item in enumerate(elem):
                    self.dlg_mg.tw_gruppenattr.setItem(i, j, QTableWidgetItem(elem[j]))
                    self.dlg_mg.tw_gruppenattr.setRowHeight(i, 20)

    def reloadgrouptgb(self):
        reloadgroup(self.dbQK, self.gruppe, dbtyp = u'SpatiaLite')
        iface.messageBar().pushMessage(u"Fertig!", u'Teilgebiete wurden geladen!', level=QgsMessageBar.INFO)

    def storegrouptgb(self):
        neuegruppe = self.dlg_mg.tf_newgroup.text()
        if neuegruppe != u'' and neuegruppe is not None:
            kommentar = self.dlg_mg.tf_kommentar.toPlainText()
            if kommentar is None:
                kommentar = u''
            storegroup(self.dbQK, neuegruppe, kommentar, dbtyp = u'SpatiaLite')
            self.showgroups()
            iface.messageBar().pushMessage(u"Fertig!", u'Teilgebiete wurden gespeichert', level=QgsMessageBar.INFO)

    # -------------------------------------------------------------------------
    # Öffnen des Formulars zur Erstellung der Verknüpfungen

    def run_createlinefl(self):
        """Run method that performs all the real work"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({u'flaechen', u'haltungen', u'linkfl'} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(u"Bedienerfehler: ",
                                           u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                                           level=QgsMessageBar.CRITICAL)
            return False

        database_QKan = u''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in k_link", 
                          u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error(u"k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if self.dbQK is None:
            fehlermeldung(u"Fehler in LinkFl.run_createlinefl",
                          u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage(u"Fehler in LinkFl.run_createlinefl",
                                           u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                                               database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        # Check, ob alle Teilgebiete in Flächen und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen (1) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen (1) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False

        self.dbQK.commit()

        # Abfragen der Tabelle flaechen nach verwendeten Abflussparametern
        sql = u'SELECT abflussparameter FROM flaechen GROUP BY abflussparameter'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        # logger.debug(u'\ndaten: {}'.format(str(daten)))  # debug
        self.dlg_cl.lw_flaechen_abflussparam.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_flaechen_abflussparam.addItem(QListWidgetItem(elem[0]))
                if 'liste_flaechen_abflussparam' in self.config:
                    try:
                        if elem[0] in self.config['liste_flaechen_abflussparam']:
                            self.dlg_cl.lw_flaechen_abflussparam.setCurrentRow(ielem)
                    except BaseException as err:
                        del self.dbQK
                        # logger.debug(u'\nelem: {}'.format(str(elem)))  # debug
                        # if len(daten) == 1:
                        # self.dlg_cl.lw_flaechen_abflussparam.setCurrentRow(0)

        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = u'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        self.dlg_cl.lw_hal_entw.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
                if 'liste_hal_entw' in self.config:
                    if elem[0] in self.config['liste_hal_entw']:
                        self.dlg_cl.lw_hal_entw.setCurrentRow(ielem)
                        # if len(daten) == 1:
                        # self.dlg_cl.lw_hal_entw.setCurrentRow(0)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = u'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        self.dlg_cl.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if 'liste_teilgebiete' in self.config:
                    if elem[0] in self.config['liste_teilgebiete']:
                        self.dlg_cl.lw_teilgebiete.setCurrentRow(ielem)
                        # if len(daten) == 1:
                        # self.dlg_cl.lw_teilgebiete.setCurrentRow(0)

        # config in Dialog übernehmen

        # Autokorrektur

        if 'autokorrektur' in self.config:
            autokorrektur = self.config['autokorrektur']
        else:
            autokorrektur = True
        self.dlg_cl.cb_autokorrektur.setChecked(autokorrektur)

        # Suchradius
        if 'suchradius' in self.config:
            suchradius = self.config['suchradius']
        else:
            suchradius = 50.
        self.dlg_cl.tf_suchradius.setText(str(suchradius))

        # Mindestflächengröße
        if 'mindestflaeche' in self.config:
            mindestflaeche = self.config['mindestflaeche']
        else:
            mindestflaeche = 0.5
        self.dlg_cl.tf_mindestflaeche.setText(str(mindestflaeche))

        # Festlegung, ob sich der Abstand auf die Flächenkante oder deren Mittelpunkt bezieht
        if 'bezug_abstand' in self.config:
            bezug_abstand = self.config['bezug_abstand']
        else:
            bezug_abstand = 'kante'

        if bezug_abstand == 'kante':
            self.dlg_cl.rb_abstandkante.setChecked(True)
        elif bezug_abstand == 'mittelpunkt':
            self.dlg_cl.rb_abstandmittelpunkt.setChecked(True)
        else:
            fehlermeldung(u"Fehler im Programmcode", u"Nicht definierte Option")
            return False

        self.dlg_cl.lw_flaechen_abflussparam.itemClicked.connect(self.countselectionfl)
        self.dlg_cl.lw_hal_entw.itemClicked.connect(self.countselectionfl)
        self.dlg_cl.lw_teilgebiete.itemClicked.connect(self.countselectionfl)
        self.countselectionfl()

        # show the dialog
        self.dlg_cl.show()
        # Run the dialog event loop
        result = self.dlg_cl.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # Start der Verarbeitung

            # Abrufen der ausgewählten Elemente in beiden Listen
            liste_flaechen_abflussparam = self.listselecteditems(self.dlg_cl.lw_flaechen_abflussparam)
            liste_hal_entw = self.listselecteditems(self.dlg_cl.lw_hal_entw)
            liste_teilgebiete = self.listselecteditems(self.dlg_cl.lw_teilgebiete)
            suchradius = self.dlg_cl.tf_suchradius.text()
            mindestflaeche = self.dlg_cl.tf_mindestflaeche.text()
            if self.dlg_cl.rb_abstandkante.isChecked():
                bezug_abstand = 'kante'
            elif self.dlg_cl.rb_abstandmittelpunkt.isChecked():
                bezug_abstand = 'mittelpunkt'
            else:
                fehlermeldung(u"Fehler im Programmcode", u"Nicht definierte Option")
                return False

            autokorrektur = self.dlg_cl.cb_autokorrektur.isChecked()

                # if len(liste_flaechen_abflussparam) == 0 or len(liste_hal_entw) == 0:
                # iface.messageBar().pushMessage(u"Bedienerfehler: ", 
                # u'Bitte in beiden Tabellen mindestens ein Element auswählen!',
                # level=QgsMessageBar.CRITICAL)
                # self.run_createlinefl()

            # Konfigurationsdaten schreiben

            self.config['suchradius'] = suchradius
            self.config['mindestflaeche'] = mindestflaeche
            self.config['bezug_abstand'] = bezug_abstand
            self.config['liste_hal_entw'] = liste_hal_entw
            self.config['liste_flaechen_abflussparam'] = liste_flaechen_abflussparam
            self.config['liste_teilgebiete'] = liste_teilgebiete
            self.config['epsg'] = epsg
            self.config['autokorrektur'] = autokorrektur

            with codecs.open(self.configfil, 'w', 'utf-8') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            # Start der Verarbeitung

            createlinkfl(self.dbQK, liste_flaechen_abflussparam, liste_hal_entw,
                        liste_teilgebiete, autokorrektur, suchradius, mindestflaeche, bezug_abstand, epsg)

            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = iface.legendInterface().layers()
            if u'Anbindungen Flächen' not in [lay.name() for lay in layers]:  # layers wurde oben erstellt
                uri = QgsDataSourceURI()
                uri.setDatabase(database_QKan)
                uri.setDataSource(u'', u'linkfl', u'glink')
                vlayer = QgsVectorLayer(uri.uri(), u'Anbindungen Flächen', u'spatialite')
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK


    # -------------------------------------------------------------------------
    # Öffnen des Formulars zur Erstellung der Verknüpfungen

    def run_createlinesw(self):
        """Run method that performs all the real work"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({u'einleit', u'haltungen', u'linksw'} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(u"Bedienerfehler: ",
                                           u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                                           level=QgsMessageBar.CRITICAL)
            return False

        database_QKan = u''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in LinkFl.run_createlinesw", 
                          u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error(u"LinkFl.run_createlinesw: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if self.dbQK is None:
            fehlermeldung(u"Fehler in LinkFl.run_createlinesw",
                          u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage(u"Fehler in LinkFl.run_createlinesw",
                                           u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                                               database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        # Check, ob alle Teilgebiete in Flächen und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM einleit 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"LinkFl.run_createlinesw (1) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"LinkFl.run_createlinesw (2) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False

        self.dbQK.commit()


        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = u'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        self.dlg_sw.lw_hal_entw.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_sw.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
                if 'liste_hal_entw' in self.config:
                    if elem[0] in self.config['liste_hal_entw']:
                        self.dlg_sw.lw_hal_entw.setCurrentRow(ielem)
                        # if len(daten) == 1:
                        # self.dlg_sw.lw_hal_entw.setCurrentRow(0)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = u'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        self.dlg_sw.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_sw.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if 'liste_teilgebiete' in self.config:
                    if elem[0] in self.config['liste_teilgebiete']:
                        self.dlg_sw.lw_teilgebiete.setCurrentRow(ielem)
                        # if len(daten) == 1:
                        # self.dlg_sw.lw_teilgebiete.setCurrentRow(0)

        # config in Dialog übernehmen

        # Suchradius
        if 'suchradius' in self.config:
            suchradius = self.config['suchradius']
        else:
            suchradius = 50.
        self.dlg_sw.tf_suchradius.setText(str(suchradius))

        # Mindestflächengröße
        if 'mindestflaeche' in self.config:
            mindestflaeche = self.config['mindestflaeche']
        else:
            mindestflaeche = 0.5
        self.dlg_sw.tf_mindestflaeche.setText(str(mindestflaeche))

        # Haltungen direkt in einleit eintragen. Es kann wegen der längeren Zeitdauer sinnvoll
        # sein, dies erst am Schluss der Bearbeitung in einem eigenen Vorgang zu machen.

        self.dlg_sw.lw_hal_entw.itemClicked.connect(self.countselectionsw)
        self.dlg_sw.lw_teilgebiete.itemClicked.connect(self.countselectionsw)
        self.countselectionsw()

        # show the dialog
        self.dlg_sw.show()
        # Run the dialog event loop
        result = self.dlg_sw.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # Start der Verarbeitung

            # Abrufen der ausgewählten Elemente in beiden Listen

            liste_hal_entw = self.listselecteditems(self.dlg_sw.lw_hal_entw)
            liste_teilgebiete = self.listselecteditems(self.dlg_sw.lw_teilgebiete)
            suchradius = self.dlg_sw.tf_suchradius.text()
            mindestflaeche = self.dlg_sw.tf_mindestflaeche.text()


            # Konfigurationsdaten schreiben

            self.config['suchradius'] = suchradius
            self.config['mindestflaeche'] = mindestflaeche
            self.config['liste_hal_entw'] = liste_hal_entw

            self.config['liste_teilgebiete'] = liste_teilgebiete
            self.config['epsg'] = epsg

            with codecs.open(self.configfil, 'w', 'utf-8') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            # Start der Verarbeitung

            createlinksw(self.dbQK, liste_teilgebiete, suchradius, mindestflaeche, epsg)


            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = iface.legendInterface().layers()
            if u'Anbindungen SW-Punkte' not in [lay.name() for lay in layers]:  # layers wurde oben erstellt
                uri = QgsDataSourceURI()
                uri.setDatabase(database_QKan)
                uri.setDataSource(u'', u'linksw', u'glink')
                vlayer = QgsVectorLayer(uri.uri(), u'Anbindungen SW-Punkte', u'spatialite')
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK


    # Zuordnen der Haltungs- etc. -objekte zu (ausgewählten) Teilgebieten

    # Hilfsfunktionen

    def enable_bufferradius(self, on=True):
        """Aktiviert/Deaktiviert die Eingabe der Pufferbreite abhängig von der 
        Auswahloption"""

        self.dlg_at.lb_bufferradius.setEnabled(on)
        self.dlg_at.tf_bufferradius.setEnabled(on)
        self.dlg_at.unit_bufferradius.setEnabled(on)


    def select_within(self):
        """Aktiviert die Eingabe der Pufferbreite"""
        self.enable_bufferradius(True)

    def select_overlaps(self):
        """Deaktiviert die Eingabe der Pufferbreite"""
        self.enable_bufferradius(False)

    # -------------------------------------------------------------------------
    # Öffnen des Formulars

    def run_assigntgeb(self):
        """Öffnen des Formulars zur Zuordnung von Teilgebieten auf Haltungen und Flächen"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({u'flaechen', u'haltungen', u'linkfl', u'linksw', u'teilgebiete', u'einzugsgebiete', 
                 u'einleit'} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(u"Bedienerfehler: ", 
                   u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!', 
                   level=QgsMessageBar.CRITICAL)
            return False

        database_QKan = u''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in k_link", u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error(u"k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(dbname=database_QKan)      # Datenbankobjekt der QKan-Datenbank zum Lesen
        if self.dbQK is None:
            fehlermeldung(u"Fehler in LinkFl.run_assigntgeb", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage(u"Fehler in LinkFl.run_assigntgeb", u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        self.dlg_at.rb_within.clicked.connect(self.select_within)
        self.dlg_at.rb_overlaps.clicked.connect(self.select_overlaps)

        # config in Dialog übernehmen

        # Autokorrektur

        if 'autokorrektur' in self.config:
            autokorrektur = self.config['autokorrektur']
        else:
            autokorrektur = True
        self.dlg_at.cb_autokorrektur.setChecked(autokorrektur)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = u'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        self.dlg_at.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_at.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if 'liste_teilgebiete' in self.config:
                    if elem[0] in self.config['liste_teilgebiete']:
                        self.dlg_at.lw_teilgebiete.setCurrentRow(ielem)

        # Festlegung, ob die Auswahl nur Objekte innerhalb oder aller überlappenden berücksichtigt
        if 'auswahltyp' in self.config:
            auswahltyp = self.config['auswahltyp']
        else:
            auswahltyp = u'within'

        if auswahltyp == u'within':
            self.dlg_at.rb_within.setChecked(True)
            self.enable_bufferradius(True)
        elif auswahltyp == u'overlaps':
            self.dlg_at.rb_overlaps.setChecked(True)
            self.enable_bufferradius(False)
        else:
            fehlermeldung(u"Fehler im Programmcode (3)", u"Nicht definierte Option")
            return False

        # Festlegung des Pufferradius
        if 'bufferradius' in self.config:
            bufferradius = self.config['bufferradius']
        else:
            bufferradius = u'0'
        self.dlg_at.tf_bufferradius.setText(bufferradius)


        # show the dialog
        self.dlg_at.show()
        # Run the dialog event loop
        result = self.dlg_at.exec_()
        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen

            liste_teilgebiete = self.listselecteditems(self.dlg_at.lw_teilgebiete)
            if self.dlg_at.rb_within.isChecked():
                auswahltyp = u'within'
            elif self.dlg_at.rb_overlaps.isChecked():
                auswahltyp = u'overlaps'
            else:
                fehlermeldung(u"Fehler im Programmcode (4)", u"Nicht definierte Option")
                return False

            autokorrektur = self.dlg_at.cb_autokorrektur.isChecked()

            # config schreiben

            self.config['liste_teilgebiete'] = liste_teilgebiete
            self.config['auswahltyp'] = auswahltyp
            self.config['epsg'] = epsg
            self.config['bufferradius'] = bufferradius
            self.config['autokorrektur'] = autokorrektur

            with codecs.open(self.configfil, 'w', 'utf-8') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            # Start der Verarbeitung

            assigntgeb(self.dbQK, auswahltyp, liste_teilgebiete, 
                       [u'haltungen', u'flaechen', u'schaechte', u'einleit', u'tezg'], 
                       autokorrektur, bufferradius)

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK


    # ----------------------------------------------------------------------------------------------
    # Laden und Speichern von Teilgebietszuordnungen als Gruppe

    def run_managegroups(self):
        """Speichern und Wiederherstellen von Teilgebietszuordnungen als Gruppe"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({u'flaechen', u'haltungen', u'schaechte', u'linksw', u'einleit', 
                 u'linkfl', u'teilgebiete', u'einzugsgebiete'} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(u"Bedienerfehler: ",
                                           u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                                           level=QgsMessageBar.CRITICAL)
            return False

        database_QKan = u''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in LinkFl.run_managegroups",
                          u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error(u"CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if self.dbQK is None:
            fehlermeldung(u"Fehler in LinkFl.run_managegroups",
                          u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage(u"Fehler in LinkFl.run_managegroups",
                                           u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                                               database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        self.showgroups()

        self.dlg_mg.lw_gruppen.itemClicked.connect(self.listGroupAttr)
        self.dlg_mg.pb_storegroup.clicked.connect(self.storegrouptgb)
        self.dlg_mg.pb_reloadgroup.clicked.connect(self.reloadgrouptgb)

        self.dlg_mg.lw_gruppen.setCurrentRow(0)
        # Anzeige initialisieren
        self.listGroupAttr()

        # show the dialog
        self.dlg_mg.show()
        # Run the dialog event loop
        result = self.dlg_mg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

            # Start der Verarbeitung
            # Nur Formular schließen

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK
