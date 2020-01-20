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
import logging
import os.path
import webbrowser

from qgis.core import Qgis, QgsDataSourceUri, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QListWidgetItem, QTableWidgetItem
from qgis.utils import iface

from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
    meldung,
)
from qkan.linkflaechen.updatelinks import updatelinkfl, updatelinksw

# noinspection PyUnresolvedReferences
from . import resources

# Import the code for the dialog
from .application_dialog import (
    AssigntgebDialog,
    CreatelineflDialog,
    CreatelineswDialog,
    ManagegroupsDialog,
    UpdateLinksDialog,
)
from .k_link import assigntgeb, createlinkfl, createlinksw, reloadgroup, storegroup

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger(u"QKan.linkflaechen.application")


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

        # Create the dialog (after translation) and keep reference
        self.dlg_at = AssigntgebDialog()
        self.dlg_cl = CreatelineflDialog()
        self.dlg_sw = CreatelineswDialog()
        self.dlg_ul = UpdateLinksDialog()
        self.dlg_mg = ManagegroupsDialog()

        logger.info(u"QKan_LinkFlaechen initialisiert...")

        # Formularereignisse anbinden ----------------------------------------------

        # Dialog dlg_cl
        self.dlg_cl.lw_flaechen_abflussparam.itemClicked.connect(
            self.cl_lw_flaechen_abflussparamClick
        )
        self.dlg_cl.lw_hal_entw.itemClicked.connect(self.cl_lw_hal_entwClick)
        self.dlg_cl.lw_teilgebiete.itemClicked.connect(self.cl_lw_teilgebieteClick)
        self.dlg_cl.cb_selFlActive.stateChanged.connect(self.cl_selFlActiveClick)
        self.dlg_cl.cb_selHalActive.stateChanged.connect(self.cl_selHalActiveClick)
        self.dlg_cl.cb_selTgbActive.stateChanged.connect(self.cl_selTgbActiveClick)
        self.dlg_cl.button_box.helpRequested.connect(self.cl_helpClick)

        # Dialog dlg_sw
        self.dlg_sw.lw_hal_entw.itemClicked.connect(self.sw_lw_hal_entwClick)
        self.dlg_sw.lw_teilgebiete.itemClicked.connect(self.sw_lw_teilgebieteClick)
        self.dlg_sw.cb_selHalActive.stateChanged.connect(self.sw_selHalActiveClick)
        self.dlg_sw.cb_selTgbActive.stateChanged.connect(self.sw_selTgbActiveClick)
        self.dlg_sw.button_box.helpRequested.connect(self.sw_helpClick)

        # Dialog dlg_at
        self.dlg_at.rb_within.clicked.connect(self.select_within)
        self.dlg_at.rb_overlaps.clicked.connect(self.select_overlaps)

        # Dialog dlg_mg
        self.dlg_mg.lw_gruppen.itemClicked.connect(self.listGroupAttr)
        self.dlg_mg.pb_storegroup.clicked.connect(self.storegrouptgb)
        self.dlg_mg.pb_reloadgroup.clicked.connect(self.reloadgrouptgb)

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
        return QCoreApplication.translate("LinkFl", message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_assigntgeb_path = ":/plugins/qkan/linkflaechen/res/icon_assigntgeb.png"
        QKan.instance.add_action(
            icon_assigntgeb_path,
            text=self.tr(
                u"Alle Elemente des Entwässerungsnetzes zu Teilgebiet zuordnen"
            ),
            callback=self.run_assigntgeb,
            parent=self.iface.mainWindow(),
        )

        icon_createlinefl_path = ":/plugins/qkan/linkflaechen/res/icon_createlinefl.png"
        QKan.instance.add_action(
            icon_createlinefl_path,
            text=self.tr(u"Erzeuge Verknüpfungslinien von Flächen zu Haltungen"),
            callback=self.run_createlinefl,
            parent=self.iface.mainWindow(),
        )

        icon_createlinesw_path = ":/plugins/qkan/linkflaechen/res/icon_createlinesw.png"
        QKan.instance.add_action(
            icon_createlinesw_path,
            text=self.tr(
                u"Erzeuge Verknüpfungslinien von Direkteinleitungen zu Haltungen"
            ),
            callback=self.run_createlinesw,
            parent=self.iface.mainWindow(),
        )

        icon_updatelinks_path = ":/plugins/qkan/linkflaechen/res/icon_updatelinks.png"
        QKan.instance.add_action(
            icon_updatelinks_path,
            text=self.tr(u"Verknüpfungen bereinigen"),
            callback=self.run_updatelinks,
            parent=self.iface.mainWindow(),
        )

        icon_managegroups_path = ":/plugins/qkan/linkflaechen/res/icon_managegroups.png"
        QKan.instance.add_action(
            icon_managegroups_path,
            text=self.tr(u"Teilgebietszuordnungen als Gruppen verwalten"),
            callback=self.run_managegroups,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        pass

    # -------------------------------------------------------------------------
    # Formularfunktionen linkfl

    def cl_helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(
            self.plugin_dir,
            "../doc/sphinx/build/html/Qkan_Formulare.html#automatisches-erzeugen-von-flachenanbindungen",
        )
        webbrowser.open_new_tab(helpfile)

    def cl_lw_flaechen_abflussparamClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlg_cl.cb_selFlActive.setChecked(True)
        self.countselectionfl()

    def cl_lw_hal_entwClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlg_cl.cb_selHalActive.setChecked(True)
        self.countselectionfl()

    def cl_lw_teilgebieteClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlg_cl.cb_selTgbActive.setChecked(True)
        self.countselectionfl()

    def cl_selFlActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlg_cl.cb_selFlActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlg_cl.lw_flaechen_abflussparam.count()
            for i in range(anz):
                item = self.dlg_cl.lw_flaechen_abflussparam.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.countselectionfl()

    def cl_selHalActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlg_cl.cb_selHalActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlg_cl.lw_hal_entw.count()
            for i in range(anz):
                item = self.dlg_cl.lw_hal_entw.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.countselectionfl()

    def cl_selTgbActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlg_cl.cb_selTgbActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlg_cl.lw_teilgebiete.count()
            for i in range(anz):
                item = self.dlg_cl.lw_teilgebiete.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.countselectionfl()

    def countselectionfl(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Flächen und Haltungen"""
        liste_flaechen_abflussparam = self.listselecteditems(
            self.dlg_cl.lw_flaechen_abflussparam
        )
        liste_hal_entw = self.listselecteditems(self.dlg_cl.lw_hal_entw)
        liste_teilgebiete = self.listselecteditems(self.dlg_cl.lw_teilgebiete)
        # Aufbereiten für SQL-Abfrage

        # Zu berücksichtigende ganze Flächen zählen
        if len(liste_flaechen_abflussparam) == 0:
            # Keine Auswahl. Soll eigentlich nicht vorkommen, funktioniert aber...
            auswahl = u""
            logger.debug(
                u"liste_flaechen_abflussparam:\n{}".format(liste_flaechen_abflussparam)
            )
        else:
            auswahl = u" AND flaechen.abflussparameter in ('{}')".format(
                u"', '".join(liste_flaechen_abflussparam)
            )

        if len(liste_teilgebiete) != 0:
            auswahl += u" and flaechen.teilgebiet in ('{}')".format(
                u"', '".join(liste_teilgebiete)
            )

        sql = u"""SELECT count(*) AS anzahl FROM flaechen
                WHERE (aufteilen <> 'ja' OR aufteilen IS NULL){auswahl}""".format(
            auswahl=auswahl
        )

        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.countselectionfl (1)"):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_flaechen.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_flaechen.setText(u"0")

        # Zu berücksichtigende zu verschneidende Flächen zählen

        sql = u"""SELECT count(*) AS anzahl FROM flaechen
                WHERE aufteilen = 'ja'{auswahl}""".format(
            auswahl=auswahl
        )
        logger.debug(u"sql Flaechen zu verschneiden:\n{}".format(sql))
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.countselectionfl (2)"):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_flaechsec.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_flaechsec.setText(u"0")

        # Zu berücksichtigende Haltungen zählen
        if len(liste_hal_entw) == 0:
            auswahl = u""
        else:
            auswahl = u" WHERE haltungen.entwart in ('{}')".format(
                u"', '".join(liste_hal_entw)
            )

        if len(liste_teilgebiete) != 0:
            if auswahl == u"":
                auswahl = u" WHERE haltungen.teilgebiet in ('{}')".format(
                    u"', '".join(liste_teilgebiete)
                )
            else:
                auswahl += u" and haltungen.teilgebiet in ('{}')".format(
                    u"', '".join(liste_teilgebiete)
                )

        sql = u"""SELECT count(*) AS anzahl FROM haltungen{auswahl}""".format(
            auswahl=auswahl
        )
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.countselectionfl (3)"):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_cl.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.dlg_cl.lf_anzahl_haltungen.setText(u"0")

    # -------------------------------------------------------------------------
    # Formularfunktionen links

    def sw_helpClick(self):
        """Reaktion auf Klick auf Help-Schaltfläche"""
        helpfile = os.path.join(
            self.plugin_dir,
            "../doc/sphinx/build/html/Qkan_Formulare.html#automatisches-erzeugen-von-anbindungen-von-einzeleinleitern",
        )
        webbrowser.open_new_tab(helpfile)

    def sw_lw_hal_entwClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlg_sw.cb_selHalActive.setChecked(True)
        self.countselectionsw()

    def sw_lw_teilgebieteClick(self):
        """Reaktion auf Klick in Tabelle"""

        self.dlg_sw.cb_selTgbActive.setChecked(True)
        self.countselectionsw()

    def sw_selHalActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlg_sw.cb_selHalActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlg_sw.lw_hal_entw.count()
            for i in range(anz):
                item = self.dlg_sw.lw_hal_entw.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.countselectionsw()

    def sw_selTgbActiveClick(self):
        """Reagiert auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.dlg_sw.cb_selTgbActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.dlg_sw.lw_teilgebiete.count()
            for i in range(anz):
                item = self.dlg_sw.lw_teilgebiete.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.countselectionsw()

    def countselectionsw(self):
        """Zählt nach Änderung der Auswahlen in den Listen im Formular die Anzahl
        der betroffenen Haltungen"""
        liste_hal_entw = self.listselecteditems(self.dlg_sw.lw_hal_entw)
        liste_teilgebiete = self.listselecteditems(self.dlg_sw.lw_teilgebiete)
        # Aufbereiten für SQL-Abfrage

        # Zu berücksichtigende Haltungen zählen
        if len(liste_hal_entw) == 0:
            auswahl = u""
        else:
            auswahl = u" WHERE haltungen.entwart in ('{}')".format(
                u"', '".join(liste_hal_entw)
            )

        if len(liste_teilgebiete) != 0:
            if auswahl == u"":
                auswahl = u" WHERE haltungen.teilgebiet in ('{}')".format(
                    u"', '".join(liste_teilgebiete)
                )
            else:
                auswahl += u" and haltungen.teilgebiet in ('{}')".format(
                    u"', '".join(liste_teilgebiete)
                )

        sql = u"""SELECT count(*) AS anzahl FROM haltungen{auswahl}""".format(
            auswahl=auswahl
        )
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.countselectionsw (1)"):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_sw.lf_anzahl_haltungen.setText(str(daten[0]))
        else:
            self.dlg_sw.lf_anzahl_haltungen.setText(u"0")

        # Zu berücksichtigende Direkteinleitungen zählen

        if len(liste_teilgebiete) != 0:
            auswahl = u" WHERE einleit.teilgebiet in ('{}')".format(
                u"', '".join(liste_teilgebiete)
            )
        else:
            auswahl = u""

        sql = u"""SELECT count(*) AS anzahl FROM einleit{auswahl}""".format(
            auswahl=auswahl
        )
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.countselectionsw (2)"):
            return False
        daten = self.dbQK.fetchone()
        if not (daten is None):
            self.dlg_sw.lf_anzahl_einleit.setText(str(daten[0]))
        else:
            self.dlg_sw.lf_anzahl_einleit.setText(u"0")

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

    # ----------------------------------------------------------------------------
    # Funktion zum Auflisten der Gruppen
    def showgroups(self):
        """Abfragen der Tabelle gruppen nach verwendeten vorhandenen Gruppen"""

        sql = u"""SELECT grnam FROM gruppen GROUP BY grnam"""
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.showgroups (1)"):
            return False
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
            self.gruppe = self.listselecteditems(self.dlg_mg.lw_gruppen)[
                0
            ]  # Im Formular gesetzt: selectionMode = SingleSelection

            sql = u"""
                SELECT teilgebiet, tabelle, printf('%i',count(*)) AS Anzahl
                FROM gruppen
                WHERE grnam = '{gruppe}'
                GROUP BY tabelle, teilgebiet
                ORDER BY tabelle, teilgebiet
                """.format(
                gruppe=self.gruppe
            )
            if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.listGroupAttr (1)"):
                return False
            daten = self.dbQK.fetchall()
            logger.debug(u"\ndaten: {}".format(str(daten)))  # debug
            nzeilen = len(daten)
            self.dlg_mg.tw_gruppenattr.setRowCount(nzeilen)
            # self.dlg_mg.tw_gruppenattr.setHorizontalHeaderLabels([u"Teilgebiet", u"Tabelle", u"Anzahl"])
            self.dlg_mg.tw_gruppenattr.setColumnWidth(
                0, 174
            )  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
            self.dlg_mg.tw_gruppenattr.setColumnWidth(1, 80)
            self.dlg_mg.tw_gruppenattr.setColumnWidth(2, 50)
            for i, elem in enumerate(daten):
                for j, item in enumerate(elem):
                    self.dlg_mg.tw_gruppenattr.setItem(i, j, QTableWidgetItem(elem[j]))
                    self.dlg_mg.tw_gruppenattr.setRowHeight(i, 20)

    def reloadgrouptgb(self):
        reloadgroup(self.dbQK, self.gruppe, dbtyp=u"SpatiaLite")
        iface.messageBar().pushMessage(
            u"Fertig!", u"Teilgebiete wurden geladen!", level=Qgis.Info
        )

    def storegrouptgb(self):
        neuegruppe = self.dlg_mg.tf_newgroup.text()
        if neuegruppe != u"" and neuegruppe is not None:
            kommentar = self.dlg_mg.tf_kommentar.toPlainText()
            if kommentar is None:
                kommentar = u""
            storegroup(self.dbQK, neuegruppe, kommentar, dbtyp=u"SpatiaLite")
            self.showgroups()
            iface.messageBar().pushMessage(
                u"Fertig!", u"Teilgebiete wurden gespeichert", level=Qgis.Info
            )

    # -------------------------------------------------------------------------
    # Öffnen des Formulars zur Erstellung der Verknüpfungen

    def run_createlinefl(self):
        """Run method that performs all the real work"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({u"flaechen", u"haltungen", u"linkfl"} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(
                u"Bedienerfehler: ",
                u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return False

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            logger.error(
                u"k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            fehlermeldung(
                u"Fehler in linkflaechen.application (1):\n",
                u"QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        # Check, ob alle Teilgebiete in Flächen und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen (1)"):
            return False

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen (1)"):
            return False

        self.dbQK.commit()

        # Abfragen der Tabelle flaechen nach verwendeten Abflussparametern
        sql = u"SELECT abflussparameter FROM flaechen GROUP BY abflussparameter"
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.run_createlinefl (1)"):
            return False
        daten = self.dbQK.fetchall()
        # logger.debug(u'\ndaten: {}'.format(str(daten)))  # debug
        self.dlg_cl.lw_flaechen_abflussparam.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_flaechen_abflussparam.addItem(QListWidgetItem(elem[0]))
                try:
                    if elem[0] in QKan.config.choices.flaechen_abflussparam:
                        self.dlg_cl.lw_flaechen_abflussparam.setCurrentRow(ielem)
                        self.dlg_cl.cb_selFlActive.setChecked(
                            True
                        )  # Auswahlcheckbox aktivieren
                except BaseException as err:
                    del self.dbQK
                    # logger.debug(u'\nelem: {}'.format(str(elem)))  # debug
                    # if len(daten) == 1:
                    # self.dlg_cl.lw_flaechen_abflussparam.setCurrentRow(0)

        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = u'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.run_createlinefl (2)"):
            return False
        daten = self.dbQK.fetchall()
        self.dlg_cl.lw_hal_entw.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.choices.hal_entw:
                    self.dlg_cl.lw_hal_entw.setCurrentRow(ielem)
                    self.dlg_cl.cb_selHalActive.setChecked(
                        True
                    )  # Auswahlcheckbox aktivieren
                    # if len(daten) == 1:
                    # self.dlg_cl.lw_hal_entw.setCurrentRow(0)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = u'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.run_createlinefl (3)"):
            return False
        daten = self.dbQK.fetchall()
        self.dlg_cl.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.choices.teilgebiete:
                    self.dlg_cl.lw_teilgebiete.setCurrentRow(ielem)
                    self.dlg_cl.cb_selTgbActive.setChecked(
                        True
                    )  # Auswahlcheckbox aktivieren
                    # if len(daten) == 1:
                    # self.dlg_cl.lw_teilgebiete.setCurrentRow(0)

        # config in Dialog übernehmen

        # Autokorrektur
        self.dlg_cl.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

        # MakeValid auf Tabellen "flaechen" und "tezg". Muss jedes Mal aktiviert werden
        flaechen_bereinigen = False
        self.dlg_cl.cb_geomMakeValid.setChecked(flaechen_bereinigen)

        # Verbindungslinien nur innerhalb tezg
        self.dlg_cl.cb_linksInTezg.setChecked(QKan.config.linkflaechen.links_in_tezg)

        # Haltungsflächen (tezg) berücksichtigen
        self.dlg_cl.cb_regardTezg.setChecked(QKan.config.mit_verschneidung)

        # Suchradius
        self.dlg_cl.tf_suchradius.setText(str(QKan.config.linkflaechen.suchradius))

        # Mindestflächengröße
        # TODO: Never written to, only read from config
        mindestflaeche = QKan.config.mindestflaeche

        # Fangradius für Anfang der Anbindungslinie
        # Kann über Menü "Optionen" eingegeben werden
        fangradius = QKan.config.fangradius

        # Festlegung, ob sich der Abstand auf die Flächenkante oder deren Mittelpunkt bezieht
        bezug_abstand = QKan.config.linkflaechen.bezug_abstand

        if bezug_abstand == enums.BezugAbstand.KANTE:
            self.dlg_cl.rb_abstandkante.setChecked(True)
        elif bezug_abstand == enums.BezugAbstand.MITTELPUNKT:
            self.dlg_cl.rb_abstandmittelpunkt.setChecked(True)
        else:
            fehlermeldung(u"Fehler im Programmcode", u"Nicht definierte Option")
            return False

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
            liste_flaechen_abflussparam: list = self.listselecteditems(
                self.dlg_cl.lw_flaechen_abflussparam
            )

            liste_hal_entw: list = self.listselecteditems(self.dlg_cl.lw_hal_entw)
            liste_teilgebiete: list = self.listselecteditems(self.dlg_cl.lw_teilgebiete)
            suchradius: int = int(self.dlg_cl.tf_suchradius.text())
            if self.dlg_cl.rb_abstandkante.isChecked():
                bezug_abstand = enums.BezugAbstand.KANTE
            elif self.dlg_cl.rb_abstandmittelpunkt.isChecked():
                bezug_abstand = enums.BezugAbstand.MITTELPUNKT
            else:
                fehlermeldung(u"Fehler im Programmcode", u"Nicht definierte Option")
                return False

            autokorrektur: bool = self.dlg_cl.cb_autokorrektur.isChecked()
            flaechen_bereinigen: bool = self.dlg_cl.cb_geomMakeValid.isChecked()
            links_in_tezg: bool = self.dlg_cl.cb_linksInTezg.isChecked()
            mit_verschneidung: bool = self.dlg_cl.cb_regardTezg.isChecked()

            # if len(liste_flaechen_abflussparam) == 0 or len(liste_hal_entw) == 0:
            # iface.messageBar().pushMessage(u"Bedienerfehler: ",
            # u'Bitte in beiden Tabellen mindestens ein Element auswählen!',
            # level=Qgis.Critical)
            # self.run_createlinefl()

            # Konfigurationsdaten schreiben
            QKan.config.autokorrektur = autokorrektur
            QKan.config.choices.flaechen_abflussparam = liste_flaechen_abflussparam
            QKan.config.choices.hal_entw = liste_hal_entw
            QKan.config.choices.teilgebiete = liste_teilgebiete
            QKan.config.epsg = epsg
            QKan.config.fangradius = fangradius
            QKan.config.linkflaechen.bezug_abstand = bezug_abstand
            QKan.config.linkflaechen.links_in_tezg = links_in_tezg
            QKan.config.linkflaechen.suchradius = suchradius
            QKan.config.mindestflaeche = mindestflaeche
            QKan.config.mit_verschneidung = mit_verschneidung

            QKan.config.save()

            # Start der Verarbeitung

            createlinkfl(
                self.dbQK,
                liste_flaechen_abflussparam,
                liste_hal_entw,
                liste_teilgebiete,
                links_in_tezg,
                mit_verschneidung,
                autokorrektur,
                flaechen_bereinigen,
                suchradius,
                mindestflaeche,
                fangradius,
                bezug_abstand,
                epsg,
            )

            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = iface.layerTreeCanvasBridge().rootGroup().findLayers()
            if u"Anbindungen Flächen" not in [
                lay.name() for lay in layers
            ]:  # layers wurde oben erstellt
                uri = QgsDataSourceUri()
                uri.setDatabase(database_QKan)
                uri.setDataSource(u"", u"linkfl", u"glink")
                vlayer = QgsVectorLayer(
                    uri.uri(), u"Anbindungen Flächen", u"spatialite"
                )
                QgsProject.instance().addMapLayer(vlayer)

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK

    # -------------------------------------------------------------------------
    # Öffnen des Formulars zur Erstellung der Verknüpfungen

    def run_createlinesw(self):
        """Run method that performs all the real work"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({u"einleit", u"haltungen", u"linksw"} & get_editable_layers()) > 0:
            iface.messageBar().pushMessage(
                u"Bedienerfehler: ",
                u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return False

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            logger.error(
                u"LinkFl.run_createlinesw: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            fehlermeldung(
                u"Fehler in linkflaechen.application (2):\n",
                u"QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        # Check, ob alle Teilgebiete in Flächen und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM einleit 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"LinkFl.run_createlinesw (1)"):
            return False

        sql = u"""INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.dbQK.sql(sql, u"LinkFl.run_createlinesw (2)"):
            return False

        self.dbQK.commit()

        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = u'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.run_createlinesw (1)"):
            return False
        daten = self.dbQK.fetchall()
        self.dlg_sw.lw_hal_entw.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_sw.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.choices.hal_entw:
                    self.dlg_sw.lw_hal_entw.setCurrentRow(ielem)
                    self.dlg_sw.cb_selHalActive.setChecked(
                        True
                    )  # Auswahlcheckbox aktivieren
                    # if len(daten) == 1:
                    # self.dlg_sw.lw_hal_entw.setCurrentRow(0)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = u'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.run_createlinesw (2)"):
            return False
        daten = self.dbQK.fetchall()
        self.dlg_sw.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_sw.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.choices.teilgebiete:
                    self.dlg_sw.lw_teilgebiete.setCurrentRow(ielem)
                    self.dlg_sw.cb_selTgbActive.setChecked(
                        True
                    )  # Auswahlcheckbox aktivieren
                    # if len(daten) == 1:
                    # self.dlg_sw.lw_teilgebiete.setCurrentRow(0)

        # config in Dialog übernehmen

        # Suchradius
        self.dlg_sw.tf_suchradius.setText(str(QKan.config.linkflaechen.suchradius))

        # Haltungen direkt in einleit eintragen. Es kann wegen der längeren Zeitdauer sinnvoll
        # sein, dies erst am Schluss der Bearbeitung in einem eigenen Vorgang zu machen.

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

            # Inhalte aus Formular lesen
            suchradius = int(self.dlg_sw.tf_suchradius.text())

            # Abrufen der ausgewählten Elemente in beiden Listen

            liste_hal_entw: list = self.listselecteditems(self.dlg_sw.lw_hal_entw)
            liste_teilgebiete: list = self.listselecteditems(self.dlg_sw.lw_teilgebiete)

            # Konfigurationsdaten schreiben

            QKan.config.choices.hal_entw = liste_hal_entw
            QKan.config.choices.teilgebiete = liste_teilgebiete
            QKan.config.epsg = epsg
            QKan.config.linkflaechen.suchradius = suchradius
            QKan.config.save()

            # Start der Verarbeitung
            createlinksw(self.dbQK, liste_teilgebiete, suchradius, epsg)

            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = iface.layerTreeCanvasBridge().rootGroup().findLayers()
            if u"Anbindungen Direkteinleitungen" not in [
                lay.name() for lay in layers
            ]:  # layers wurde oben erstellt
                uri = QgsDataSourceUri()
                uri.setDatabase(database_QKan)
                uri.setDataSource(u"", u"linksw", u"glink")
                vlayer = QgsVectorLayer(
                    uri.uri(), u"Anbindungen Direkteinleitungen", u"spatialite"
                )
                QgsProject.instance().addMapLayer(vlayer)

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK

    # Zuordnen der Haltungs- etc. -objekte zu (ausgewählten) Teilgebieten

    # Hilfsfunktionen

    def enable_bufferradius(self, onoff=True):
        """Aktiviert/Deaktiviert die Eingabe der Pufferbreite abhängig von der 
        Auswahloption"""

        self.dlg_at.lb_bufferradius.setEnabled(onoff)
        self.dlg_at.tf_bufferradius.setEnabled(onoff)
        self.dlg_at.unit_bufferradius.setEnabled(onoff)

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
        if (
            len(
                {u"flaechen", u"haltungen", u"linkfl", u"linksw", u"tezg", u"einleit"}
                & get_editable_layers()
            )
            > 0
        ):
            iface.messageBar().pushMessage(
                u"Bedienerfehler: ",
                u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return False

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            logger.error(
                u"k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            fehlermeldung(
                u"Fehler in linkflaechen.application (3):\n",
                u"QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        # config in Dialog übernehmen

        # Autokorrektur
        self.dlg_at.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

        # MakeValid auf Tabellen "flaechen" und "tezg". Muss jedes Mal aktiviert werden
        flaechen_bereinigen = False
        self.dlg_at.cb_geomMakeValid.setChecked(flaechen_bereinigen)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = u'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.dbQK.sql(sql, u"QKan_LinkFlaechen.run_assigntgeb (1)"):
            return False
        daten = self.dbQK.fetchall()
        self.dlg_at.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_at.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.choices.teilgebiete:
                    self.dlg_at.lw_teilgebiete.setCurrentRow(ielem)

        # Festlegung, ob die Auswahl nur Objekte innerhalb oder aller überlappenden berücksichtigt
        auswahltyp = QKan.config.linkflaechen.auswahltyp
        if auswahltyp == enums.AuswahlTyp.WITHIN:
            self.dlg_at.rb_within.setChecked(True)
            self.enable_bufferradius(True)
        elif auswahltyp == enums.AuswahlTyp.OVERLAPS:
            self.dlg_at.rb_overlaps.setChecked(True)
            self.enable_bufferradius(False)
        else:
            fehlermeldung(u"Fehler im Programmcode (3)", u"Nicht definierte Option")
            return False

        # Festlegung des Pufferradius
        bufferradius = QKan.config.linkflaechen.bufferradius
        self.dlg_at.tf_bufferradius.setText(str(bufferradius))

        # show the dialog
        self.dlg_at.show()
        # Run the dialog event loop
        result = self.dlg_at.exec_()
        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen

            liste_teilgebiete: list = self.listselecteditems(self.dlg_at.lw_teilgebiete)
            if self.dlg_at.rb_within.isChecked():
                auswahltyp = enums.AuswahlTyp.WITHIN
            elif self.dlg_at.rb_overlaps.isChecked():
                auswahltyp = enums.AuswahlTyp.OVERLAPS
            else:
                fehlermeldung(u"Fehler im Programmcode (4)", u"Nicht definierte Option")
                return False

            autokorrektur: bool = self.dlg_at.cb_autokorrektur.isChecked()
            flaechen_bereinigen: bool = self.dlg_at.cb_geomMakeValid.isChecked()
            bufferradius: int = int(self.dlg_at.tf_bufferradius.text())

            # config schreiben
            #
            QKan.config.autokorrektur = autokorrektur
            QKan.config.choices.teilgebiete = liste_teilgebiete
            QKan.config.epsg = epsg
            QKan.config.linkflaechen.auswahltyp = auswahltyp
            QKan.config.linkflaechen.bufferradius = bufferradius

            QKan.config.save()

            # Start der Verarbeitung

            assigntgeb(
                self.dbQK,
                auswahltyp,
                liste_teilgebiete,
                [
                    [u"haltungen", "geom"],
                    [u"flaechen", "geom"],
                    [u"schaechte", "geop"],
                    [u"einleit", "geom"],
                    [u"tezg", "geom"],
                    [u"linksw", "glink"],
                    [u"linkfl", "glink"],
                ],
                autokorrektur,
                flaechen_bereinigen,
                bufferradius,
            )

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK

    # ----------------------------------------------------------------------------------------------
    # Laden und Speichern von Teilgebietszuordnungen als Gruppe

    def run_managegroups(self):
        """Speichern und Wiederherstellen von Teilgebietszuordnungen als Gruppe"""

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {
                    u"flaechen",
                    u"haltungen",
                    u"schaechte",
                    u"linksw",
                    u"einleit",
                    u"linkfl",
                    u"teilgebiete",
                    u"tezg",
                }
                & get_editable_layers()
            )
            > 0
        ):
            iface.messageBar().pushMessage(
                u"Bedienerfehler: ",
                u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return False

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            logger.error(
                u"CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False

        self.dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            fehlermeldung(
                u"Fehler in linkflaechen.application (4):\n",
                u"QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        self.showgroups()

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

        # ----------------------------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK

    # ----------------------------------------------------------------------------------------------
    # Logischen Cache der Verknüpfungen aktualisieren

    def run_updatelinks(self):
        """Aktualisieren des logischen Verknüpfungscaches in linkfl und linksw"""

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {u"flaechen", u"haltungen", u"linkfl", u"linksw", u"tezg", u"einleit"}
                & get_editable_layers()
            )
            > 0
        ):
            iface.messageBar().pushMessage(
                u"Bedienerfehler: ",
                u'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return False

        database_QKan, epsg = get_database_QKan()
        if not database_QKan:
            logger.error(
                u"k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False

        # Datenbankverbindung für Abfragen
        self.dbQK = DBConnection(
            dbname=database_QKan
        )  # Datenbankobjekt der QKan-Datenbank zum Lesen

        if not self.dbQK.connected:
            fehlermeldung(
                u"Fehler in linkflaechen.application (5):\n",
                u"QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_QKan
                ),
            )
            return None

        self.dlg_ul.tf_qkDB.setText(database_QKan)

        # Festlegung des Fangradius
        fangradius = QKan.config.fangradius
        self.dlg_ul.tf_fangradius.setText(str(fangradius))
        logger.debug("fangradius: {}".format(fangradius))

        # Löschen von Flächenverknüpfungen ohne Linienobjekt
        delete_geom_none = QKan.config.linkflaechen.delete_geom_none
        self.dlg_ul.cb_deleteGeomNone.setChecked(delete_geom_none)

        # MakeValid auf Tabellen "flaechen" und "tezg". Muss jedes Mal aktiviert werden
        flaechen_bereinigen = False
        self.dlg_ul.cb_geomMakeValid.setChecked(flaechen_bereinigen)

        # show the dialog
        self.dlg_ul.show()
        # Run the dialog event loop
        result = self.dlg_ul.exec_()
        # See if OK was pressed
        if result:

            # Inhalte aus Formular lesen
            delete_geom_none: bool = self.dlg_ul.cb_deleteGeomNone.isChecked()
            flaechen_bereinigen: bool = self.dlg_ul.cb_geomMakeValid.isChecked()

            # config schreiben
            QKan.config.linkflaechen.delete_geom_none = delete_geom_none
            QKan.config.fangradius = fangradius
            QKan.config.save()

            # Start der Verarbeitung
            if self.dlg_ul.cb_linkfl.isChecked():
                updatelinkfl(
                    self.dbQK, fangradius, flaechen_bereinigen, delete_geom_none
                )

            if self.dlg_ul.cb_linksw.isChecked():
                updatelinksw(self.dbQK, fangradius, delete_geom_none)

            meldung(u"Fertig!", u"Bereinigung Flächenverknüpfungen abgeschlossen.")

        # ----------------------------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.dbQK
