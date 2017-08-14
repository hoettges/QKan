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
from PyQt4.QtGui import QListWidgetItem
from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# noinspection PyUnresolvedReferences
import resources_connectflaechen
# noinspection PyUnresolvedReferences
import resources_createlines
# Initialize Qt resources from file resources.py
# Import the code for the dialog
from application_dialog import CreatelinesDialog
from k_link import createlinks
from qkan import Dummy
from qkan.database.dbfunc import DBConnection
from qkan.database.qgis_utils import get_database_QKan, get_editable_layers

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger('QKan')


def fortschritt(text, prozent):
    logger.debug(u'{:s} ({:.0f}%)'.format(text, prozent * 100))
    QgsMessageLog.logMessage(u'{:s} ({:.0f}%)'.format(text, prozent * 100), 'Export: ', QgsMessageLog.INFO)


def fehlermeldung(title, text):
    logger.debug(u'{:s} {:s}'.format(title, text))
    QgsMessageLog.logMessage(u'{:s} {:s}'.format(title, text), level=QgsMessageLog.CRITICAL)


class Application:
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
        self.dlg_cl = CreatelinesDialog()

        # Anfang Eigene Funktionen -------------------------------------------------
        # (jh, 12.06.2017)

        logger.info('\n\nQKan_LinkFlaechen initialisiert...')

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

        icon_createlines_path = ':/plugins/Flaechenzuordnungen/icon_createlines.png'
        Dummy.instance.add_action(
            icon_createlines_path,
            text=self.tr(u'Erzeuge Verknüpfungslinien von Flaechen zu Haltungen'),
            callback=self.run_createlines,
            parent=self.iface.mainWindow())

    def unload(self):
        pass

    # -------------------------------------------------------------------------
    # Formularfunktionen

    def countselection(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        liste_flaechen_abflussparam = self.listselecteditems(self.dlg_cl.lw_flaechen_abflussparam)
        liste_hal_entw = self.listselecteditems(self.dlg_cl.lw_hal_entw)
        liste_teilgebiete = self.listselecteditems(self.dlg_cl.lw_teilgebiete)
        # Aufbereiten für SQL-Abfrage

        # Zu berücksichtigende ganze Flächen zählen
        if len(liste_flaechen_abflussparam) == 0:
            # Keine Auswahl. Soll eigentlich nicht vorkommen, funktioniert aber...
            auswahl = ''
            logger.debug(u'Warnung in Link Flaechen: Keine Auswahl bei Flächen...')
        else:
            auswahl = " AND flaechen.abflussparameter in ('{}')".format("', '".join(liste_flaechen_abflussparam))

        if len(liste_teilgebiete) != 0:
            auswahl += " and flaechen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

        sql = """SELECT count(*) AS anzahl FROM flaechen
                WHERE (aufteilen <> 'ja' OR aufteilen IS NULL){auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen (9) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_flaechen.setText('0')

        # Zu berücksichtigende zu verschneidende Flächen zählen
        if liste_flaechen_abflussparam == '()':
            # Keine Auswahl. Soll eigentlich nicht vorkommen, funktioniert aber...
            auswahl = ''
            logger.debug(u'Warnung in Link Flaechen: Keine Auswahl bei Flächen...')
        else:
            auswahl = " AND flaechen.abflussparameter in ('{}')".format("', '".join(liste_flaechen_abflussparam))

        if len(liste_teilgebiete) != 0:
            auswahl += " and flaechen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

        sql = """SELECT count(*) AS anzahl FROM flaechen
                WHERE aufteilen = 'ja'{auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen (9) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_flaechsec.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_flaechsec.setText('0')

        # Zu berücksichtigende Haltungen zählen
        if len(liste_hal_entw) == 0:
            auswahl = ''
        else:
            auswahl = " WHERE haltungen.entwart in ('{}')".format("', '".join(liste_hal_entw))

        if len(liste_teilgebiete) != 0:
            if auswahl == '':
                auswahl = " WHERE haltungen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
            else:
                auswahl += " and haltungen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))

        sql = """SELECT count(*) AS anzahl FROM haltungen{auswahl}""".format(auswahl=auswahl)
        try:
            self.dbQK.sql(sql)
        except:
            fehlermeldung(u"QKan_LinkFlaechen (10) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_haltungen.setText('0')

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

    # -------------------------------------------------------------------------
    # Öffnen des Formulars

    def run_createlines(self):
        """Run method that performs all the real work"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({'flaechen', 'haltungen', 'linkfl', 'tezg'} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(u"Bedienerfehler: ",
                                           u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                                           level=QgsMessageBar.CRITICAL)
            return False

        database_QKan = ''

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            fehlermeldung(u"Fehler in k_link", u"database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            logger.error("k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!")
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(dbname=database_QKan)  # Datenbankobjekt der QKan-Datenbank zum Lesen
        if self.dbQK is None:
            fehlermeldung("Fehler in QKan_CreateUnbefFl",
                          u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format(database_QKan))
            iface.messageBar().pushMessage("Fehler in QKan_Import_from_HE",
                                           u'QKan-Datenbank {:s} wurde nicht gefunden!\nAbbruch!'.format( \
                                               database_QKan), level=QgsMessageBar.CRITICAL)
            return None

        # --------------------------------------------------------------------------------------------------
        # Anpassungen der Datenbank für neuere Versionen

        # Änderung gegen DB-Version 1.1.5
        if 'teilgebiet' not in self.dbQK.attrlist('linkfl'):
            sql = """ALTER TABLE linkfl ADD COLUMN teilgebiet TEXT"""
            try:
                self.dbQK.sql(sql)
            except:
                fehlermeldung(u"QKan_LinkFlaechen (6) SQL-Fehler in SpatiaLite: \n", sql)
                del self.dbQK
                return False

        if 'aufteilen' not in self.dbQK.attrlist('linkfl'):
            sql = """ALTER TABLE linkfl ADD COLUMN aufteilen TEXT"""
            try:
                self.dbQK.sql(sql)
            except:
                fehlermeldung(u"QKan_LinkFlaechen (6) SQL-Fehler in SpatiaLite: \n", sql)
                del self.dbQK
                return False

        if 'aufteilen' not in self.dbQK.attrlist('flaechen'):
            sql = """ALTER TABLE flaechen ADD COLUMN aufteilen TEXT"""
            try:
                self.dbQK.sql(sql)
            except:
                fehlermeldung(u"QKan_LinkFlaechen (7) SQL-Fehler in SpatiaLite: \n", sql)
                del self.dbQK
                return False

        self.dbQK.commit()

        # Änderung gegen DB-Version 1.1.5
        # Standard-Auswahl für teilgebiete hinzufügen
        sql = """INSERT INTO teilgebiete (tgnam, kommentar) 
                SELECT "" AS tgnam, ":1" AS kommentar FROM (VALUES 
                  ('auswahl1', 'für benutzerdefinierte Auswahl'), 
                  ('auswahl2', 'für benutzerdefinierte Auswahl'), 
                  ('auswahl3', 'für benutzerdefinierte Auswahl'))
                WHERE tgnam NOT IN (SELECT tgnam FROM teilgebiete)"""
        try:
            self.dbQK.sql(sql)
            self.dbQK.commit()
        except:
            fehlermeldung(u"QKan_LinkFlaechen (8) SQL-Fehler in SpatiaLite: \n", sql)
            del self.dbQK
            return False
        self.dbQK.commit()

        # Ende Anpassungen der Datenbank für neuere Versionen
        # --------------------------------------------------------------------------------------------------

        # Check, ob alle Teilgebiete in Flächen und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
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

        sql = """INSERT INTO teilgebiete (tgnam)
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

        # Abfragen der Tabelle tezg nach verwendeten Abflussparametern
        sql = 'SELECT abflussparameter FROM flaechen GROUP BY abflussparameter'
        self.dbQK.sql(sql)
        daten = self.dbQK.fetchall()
        logger.debug('\ndaten: {}'.format(str(daten)))  # debug
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
                        logger.debug('\nelem: {}'.format(str(elem)))  # debug
                        # if len(daten) == 1:
                        # self.dlg_cl.lw_flaechen_abflussparam.setCurrentRow(0)

        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = 'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
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
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
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

        # Suchradius
        if 'suchradius' in self.config:
            suchradius = self.config['suchradius']
        else:
            suchradius = 50.
        self.dlg_cl.tf_suchradius.setText(str(suchradius))

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
            fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
            return False

        self.dlg_cl.lw_flaechen_abflussparam.itemClicked.connect(self.countselection)
        self.dlg_cl.lw_hal_entw.itemClicked.connect(self.countselection)
        self.dlg_cl.lw_teilgebiete.itemClicked.connect(self.countselection)
        self.countselection()

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
            if self.dlg_cl.rb_abstandkante.isChecked():
                bezug_abstand = 'kante'
            elif self.dlg_cl.rb_abstandmittelpunkt.isChecked():
                bezug_abstand = 'mittelpunkt'
            else:
                fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
                return False

                # if len(liste_flaechen_abflussparam) == 0 or len(liste_hal_entw) == 0:
                # iface.messageBar().pushMessage(u"Bedienerfehler: ", 
                # u'Bitte in beiden Tabellen mindestens ein Element auswählen!',
                # level=QgsMessageBar.CRITICAL)
                # self.run_createlines()

            # Konfigurationsdaten schreiben

            self.config['suchradius'] = suchradius
            self.config['bezug_abstand'] = bezug_abstand
            self.config['liste_hal_entw'] = liste_hal_entw
            self.config['liste_flaechen_abflussparam'] = liste_flaechen_abflussparam
            self.config['liste_teilgebiete'] = liste_teilgebiete
            self.config['epsg'] = epsg

            with codecs.open(self.configfil, 'w') as fileconfig:
                fileconfig.write(json.dumps(self.config))

            # Start der Verarbeitung

            createlinks(self.dbQK, liste_flaechen_abflussparam, liste_hal_entw,
                        liste_teilgebiete, suchradius, bezug_abstand, epsg)

            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = iface.legendInterface().layers()
            if 'Anbindung' not in [lay.name() for lay in layers]:  # layers wurde oben erstellt
                uri = QgsDataSourceURI()
                uri.setDatabase(database_QKan)
                uri.setDataSource('', 'linkfl', 'glink')
                vlayer = QgsVectorLayer(uri.uri(), 'Anbindung', 'spatialite')
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)
