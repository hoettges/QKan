# -*- coding: utf-8 -*-
"""
Flaechenzuordnungen
Verknüpft Flächen mit nächster Haltung
"""
from typing import List, Optional, cast

from qgis.core import Qgis, QgsDataSourceUri, QgsProject, QgsVectorLayer
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QListWidgetItem
from qkan import QKan, enums, list_selected_items
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import (
    fehlermeldung,
    get_database_QKan,
    get_editable_layers,
    meldung,
)
from qkan.linkflaechen.updatelinks import updatelinkfl, updatelinksw
from qkan.plugin import QKanPlugin

from .application_dialog import (
    AssigntgebDialog,
    CreatelineflDialog,
    CreatelineswDialog,
    ManagegroupsDialog,
    UpdateLinksDialog,
)
from .k_link import assigntgeb, createlinkfl, createlinksw

# noinspection PyUnresolvedReferences
from . import resources  # isort:skip


class LinkFl(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)
        self.db_qkan: Optional[DBConnection] = None

        self.dlg_at = AssigntgebDialog()
        self.dlg_cl = CreatelineflDialog(self)
        self.dlg_mg = ManagegroupsDialog(self)
        self.dlg_sw = CreatelineswDialog(self)
        self.dlg_ul = UpdateLinksDialog()

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_assigntgeb_path = ":/plugins/qkan/linkflaechen/res/icon_assigntgeb.png"
        QKan.instance.add_action(
            icon_assigntgeb_path,
            text=self.tr(
                "Alle Elemente des Entwässerungsnetzes zu Teilgebiet zuordnen"
            ),
            callback=self.run_assigntgeb,
            parent=self.iface.mainWindow(),
        )

        icon_createlinefl_path = ":/plugins/qkan/linkflaechen/res/icon_createlinefl.png"
        QKan.instance.add_action(
            icon_createlinefl_path,
            text=self.tr("Erzeuge Verknüpfungslinien von Flächen zu Haltungen"),
            callback=self.run_createlinefl,
            parent=self.iface.mainWindow(),
        )

        icon_createlinesw_path = ":/plugins/qkan/linkflaechen/res/icon_createlinesw.png"
        QKan.instance.add_action(
            icon_createlinesw_path,
            text=self.tr(
                "Erzeuge Verknüpfungslinien von Direkteinleitungen zu Haltungen"
            ),
            callback=self.run_createlinesw,
            parent=self.iface.mainWindow(),
        )

        icon_updatelinks_path = ":/plugins/qkan/linkflaechen/res/icon_updatelinks.png"
        QKan.instance.add_action(
            icon_updatelinks_path,
            text=self.tr("Verknüpfungen bereinigen"),
            callback=self.run_updatelinks,
            parent=self.iface.mainWindow(),
        )

        icon_managegroups_path = ":/plugins/qkan/linkflaechen/res/icon_managegroups.png"
        QKan.instance.add_action(
            icon_managegroups_path,
            text=self.tr("Teilgebietszuordnungen als Gruppen verwalten"),
            callback=self.run_managegroups,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        self.dlg_at.close()
        self.dlg_cl.close()
        self.dlg_mg.close()
        self.dlg_sw.close()
        self.dlg_ul.close()

    def run_createlinefl(self) -> None:
        """Run method that performs all the real work"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({"flaechen", "haltungen", "linkfl"} & get_editable_layers()) > 0:
            self.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            self.log.error(
                "k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return

        # Datenbankverbindung für Abfragen
        self.db_qkan = DBConnection(dbname=database_qkan)

        if not self.db_qkan.connected:
            fehlermeldung(
                "Fehler in linkflaechen.application (1):\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )
            return

        # Check, ob alle Teilgebiete in Flächen und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM flaechen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen (1)"):
            del self.db_qkan
            return

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen (1)"):
            del self.db_qkan
            return

        self.db_qkan.commit()

        # Abfragen der Tabelle flaechen nach verwendeten Abflussparametern
        sql = "SELECT abflussparameter FROM flaechen GROUP BY abflussparameter"
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen.run_createlinefl (1)"):
            del self.db_qkan
            return
        daten = self.db_qkan.fetchall()
        # self.log.debug(u'\ndaten: {}'.format(str(daten)))  # debug
        self.dlg_cl.lw_flaechen_abflussparam.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_flaechen_abflussparam.addItem(QListWidgetItem(elem[0]))
                try:
                    if elem[0] in QKan.config.selections.flaechen_abflussparam:
                        self.dlg_cl.lw_flaechen_abflussparam.setCurrentRow(ielem)
                        self.dlg_cl.cb_selFlActive.setChecked(
                            True
                        )  # Auswahlcheckbox aktivieren
                except BaseException:
                    del self.db_qkan
                    # self.log.debug(u'\nelem: {}'.format(str(elem)))  # debug
                    # if len(daten) == 1:
                    # self.dlg_cl.lw_flaechen_abflussparam.setCurrentRow(0)

        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = 'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen.run_createlinefl (2)"):
            del self.db_qkan
            return
        daten = self.db_qkan.fetchall()
        self.dlg_cl.lw_hal_entw.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.selections.hal_entw:
                    self.dlg_cl.lw_hal_entw.setCurrentRow(ielem)
                    self.dlg_cl.cb_selHalActive.setChecked(
                        True
                    )  # Auswahlcheckbox aktivieren
                    # if len(daten) == 1:
                    # self.dlg_cl.lw_hal_entw.setCurrentRow(0)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen.run_createlinefl (3)"):
            del self.db_qkan
            return
        daten = self.db_qkan.fetchall()
        self.dlg_cl.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_cl.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.selections.teilgebiete:
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
        self.dlg_cl.tf_fangradius.setText(str(fangradius))

        # Festlegung, ob sich der Abstand auf die Flächenkante oder deren Mittelpunkt bezieht
        bezug_abstand = QKan.config.linkflaechen.bezug_abstand

        if bezug_abstand == enums.BezugAbstand.KANTE:
            self.dlg_cl.rb_abstandkante.setChecked(True)
        elif bezug_abstand == enums.BezugAbstand.MITTELPUNKT:
            self.dlg_cl.rb_abstandmittelpunkt.setChecked(True)
        else:
            fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
            del self.db_qkan
            return

        self.dlg_cl.count_selection()

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
            liste_flaechen_abflussparam: List[str] = list_selected_items(
                self.dlg_cl.lw_flaechen_abflussparam
            )

            liste_hal_entw: List[str] = list_selected_items(self.dlg_cl.lw_hal_entw)
            liste_teilgebiete: List[str] = list_selected_items(
                self.dlg_cl.lw_teilgebiete
            )
            suchradius: float = float(self.dlg_cl.tf_suchradius.text())
            if self.dlg_cl.rb_abstandkante.isChecked():
                bezug_abstand = enums.BezugAbstand.KANTE
            elif self.dlg_cl.rb_abstandmittelpunkt.isChecked():
                bezug_abstand = enums.BezugAbstand.MITTELPUNKT
            else:
                fehlermeldung("Fehler im Programmcode", "Nicht definierte Option")
                del self.db_qkan
                return

            autokorrektur: bool = self.dlg_cl.cb_autokorrektur.isChecked()
            flaechen_bereinigen = cast(bool, self.dlg_cl.cb_geomMakeValid.isChecked())
            links_in_tezg = self.dlg_cl.cb_linksInTezg.isChecked()
            mit_verschneidung = self.dlg_cl.cb_regardTezg.isChecked()
            fangradius = float(self.dlg_cl.tf_fangradius.text())

            # if len(liste_flaechen_abflussparam) == 0 or len(liste_hal_entw) == 0:
            # self.iface.messageBar().pushMessage("Bedienerfehler: ",
            # u'Bitte in beiden Tabellen mindestens ein Element auswählen!',
            # level=Qgis.Critical)
            # self.run_createlinefl()

            # Konfigurationsdaten schreiben
            QKan.config.autokorrektur = autokorrektur
            QKan.config.selections.flaechen_abflussparam = liste_flaechen_abflussparam
            QKan.config.selections.hal_entw = liste_hal_entw
            QKan.config.selections.teilgebiete = liste_teilgebiete
            if epsg:
                QKan.config.epsg = epsg
            QKan.config.fangradius = fangradius
            QKan.config.linkflaechen.bezug_abstand = bezug_abstand
            QKan.config.linkflaechen.links_in_tezg = links_in_tezg
            QKan.config.linkflaechen.suchradius = suchradius
            QKan.config.mindestflaeche = mindestflaeche
            QKan.config.mit_verschneidung = mit_verschneidung

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                createlinkfl(
                    iface, 
                    self.dbQK,
                    {liste_flaechen_abflussparam},
                    {liste_hal_entw},
                    {liste_teilgebiete},
                    {links_in_tezg},
                    {mit_verschneidung},
                    {autokorrektur},
                    {flaechen_bereinigen},
                    {suchradius},
                    {mindestflaeche},
                    {fangradius},
                    {bezug_abstand},
            )"""
            )

            if not createlinkfl(
                self.iface,
                self.db_qkan,
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
            ):
                del self.db_qkan

            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = self.iface.layerTreeCanvasBridge().rootGroup().findLayers()
            if "Anbindungen Flächen" not in [
                lay.name() for lay in layers
            ]:  # layers wurde oben erstellt
                uri = QgsDataSourceUri()
                uri.setDatabase(database_qkan)
                uri.setDataSource("", "linkfl", "glink")
                vlayer = QgsVectorLayer(
                    uri.uri(),
                    "Anbindungen Flächen",
                    enums.QKanDBChoice.SPATIALITE.value,
                )
                # noinspection PyArgumentList
                QgsProject.instance().addMapLayer(vlayer)

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.db_qkan

    # -------------------------------------------------------------------------
    # Öffnen des Formulars zur Erstellung der Verknüpfungen

    def run_createlinesw(self) -> None:
        """Run method that performs all the real work"""

        # Check, ob die relevanten Layer nicht editable sind.
        if len({"einleit", "haltungen", "linksw"} & get_editable_layers()) > 0:
            self.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            self.log.error(
                "LinkFl.run_createlinesw: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return

        # Datenbankverbindung für Abfragen
        self.db_qkan = DBConnection(dbname=database_qkan)

        if not self.db_qkan.connected:
            fehlermeldung(
                "Fehler in linkflaechen.application (2):\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )
            return

        # Check, ob alle Teilgebiete in Flächen und Haltungen auch in Tabelle "teilgebiete" enthalten

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM einleit 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "LinkFl.run_createlinesw (1)"):
            del self.db_qkan
            return

        sql = """INSERT INTO teilgebiete (tgnam)
                SELECT teilgebiet FROM haltungen 
                WHERE teilgebiet IS NOT NULL AND teilgebiet <> '' AND
                teilgebiet NOT IN (SELECT tgnam FROM teilgebiete)
                GROUP BY teilgebiet"""
        if not self.db_qkan.sql(sql, "LinkFl.run_createlinesw (2)"):
            del self.db_qkan
            return

        self.db_qkan.commit()

        # Abfragen der Tabelle haltungen nach vorhandenen Entwässerungsarten
        sql = 'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen.run_createlinesw (1)"):
            del self.db_qkan
            return
        daten = self.db_qkan.fetchall()
        self.dlg_sw.lw_hal_entw.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_sw.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.selections.hal_entw:
                    self.dlg_sw.lw_hal_entw.setCurrentRow(ielem)
                    self.dlg_sw.cb_selHalActive.setChecked(
                        True
                    )  # Auswahlcheckbox aktivieren
                    # if len(daten) == 1:
                    # self.dlg_sw.lw_hal_entw.setCurrentRow(0)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen.run_createlinesw (2)"):
            del self.db_qkan
            return
        daten = self.db_qkan.fetchall()
        self.dlg_sw.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_sw.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.selections.teilgebiete:
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

        self.dlg_sw.count_selection()

        # show the dialog
        self.dlg_sw.show()
        # Run the dialog event loop
        result = self.dlg_sw.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            # Inhalte aus Formular lesen
            suchradius = float(self.dlg_sw.tf_suchradius.text())

            # Abrufen der ausgewählten Elemente in beiden Listen

            liste_hal_entw: List[str] = list_selected_items(self.dlg_sw.lw_hal_entw)
            liste_teilgebiete: List[str] = list_selected_items(
                self.dlg_sw.lw_teilgebiete
            )

            # Konfigurationsdaten schreiben

            QKan.config.selections.hal_entw = liste_hal_entw
            QKan.config.selections.teilgebiete = liste_teilgebiete
            if epsg:
                QKan.config.epsg = epsg
            QKan.config.linkflaechen.suchradius = suchradius
            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                createlinksw(
                    self.dbQK, 
                    {liste_teilgebiete}, 
                    {suchradius}, 
                    {epsg},
            )"""
            )

            if not createlinksw(
                self.iface,
                self.db_qkan,
                liste_teilgebiete,
                suchradius,
                epsg or QKan.config.epsg,
            ):
                del self.db_qkan
                return

            # Einfügen der Verbindungslinien in die Layerliste, wenn nicht schon geladen
            layers = self.iface.layerTreeCanvasBridge().rootGroup().findLayers()
            if "Anbindungen Direkteinleitungen" not in [
                lay.name() for lay in layers
            ]:  # layers wurde oben erstellt
                uri = QgsDataSourceUri()
                uri.setDatabase(database_qkan)
                uri.setDataSource("", "linksw", "glink")
                vlayer = QgsVectorLayer(
                    uri.uri(),
                    "Anbindungen Direkteinleitungen",
                    enums.QKanDBChoice.SPATIALITE.value,
                )
                # noinspection PyArgumentList
                QgsProject.instance().addMapLayer(vlayer)

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.db_qkan

    # Zuordnen der Haltungs- etc. -objekte zu (ausgewählten) Teilgebieten

    # Hilfsfunktionen

    # -------------------------------------------------------------------------
    # Öffnen des Formulars

    def run_assigntgeb(self) -> None:
        """Öffnen des Formulars zur Zuordnung von Teilgebieten auf Haltungen und Flächen"""

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {"flaechen", "haltungen", "linkfl", "linksw", "tezg", "einleit"}
                & get_editable_layers()
            )
            > 0
        ):
            self.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            self.log.error(
                "k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return

        # Datenbankverbindung für Abfragen
        self.db_qkan = DBConnection(dbname=database_qkan)

        if not self.db_qkan.connected:
            fehlermeldung(
                "Fehler in linkflaechen.application (3):\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )
            return

        # config in Dialog übernehmen

        # Autokorrektur
        self.dlg_at.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

        # MakeValid auf Tabellen "flaechen" und "tezg". Muss jedes Mal aktiviert werden
        flaechen_bereinigen = False
        self.dlg_at.cb_geomMakeValid.setChecked(flaechen_bereinigen)

        # Abfragen der Tabelle teilgebiete nach Teilgebieten
        sql = 'SELECT "tgnam" FROM "teilgebiete" GROUP BY "tgnam"'
        if not self.db_qkan.sql(sql, "QKan_LinkFlaechen.run_assigntgeb (1)"):
            del self.db_qkan
            return
        daten = self.db_qkan.fetchall()
        self.dlg_at.lw_teilgebiete.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.dlg_at.lw_teilgebiete.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.selections.teilgebiete:
                    self.dlg_at.lw_teilgebiete.setCurrentRow(ielem)

        # Festlegung, ob die Auswahl nur Objekte innerhalb oder aller überlappenden berücksichtigt
        auswahltyp = QKan.config.linkflaechen.auswahltyp
        if auswahltyp == enums.AuswahlTyp.WITHIN:
            self.dlg_at.rb_within.setChecked(True)
            self.dlg_at.enable_bufferradius(True)
        elif auswahltyp == enums.AuswahlTyp.OVERLAPS:
            self.dlg_at.rb_overlaps.setChecked(True)
            self.dlg_at.enable_bufferradius(False)
        else:
            fehlermeldung("Fehler im Programmcode (3)", "Nicht definierte Option")
            del self.db_qkan
            return

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

            liste_teilgebiete: List[str] = list_selected_items(
                self.dlg_at.lw_teilgebiete
            )
            if self.dlg_at.rb_within.isChecked():
                auswahltyp = enums.AuswahlTyp.WITHIN
            elif self.dlg_at.rb_overlaps.isChecked():
                auswahltyp = enums.AuswahlTyp.OVERLAPS
            else:
                fehlermeldung("Fehler im Programmcode (4)", "Nicht definierte Option")
                del self.db_qkan
                return

            autokorrektur: bool = self.dlg_at.cb_autokorrektur.isChecked()
            flaechen_bereinigen = self.dlg_at.cb_geomMakeValid.isChecked()
            bufferradius = float(self.dlg_at.tf_bufferradius.text())

            # config schreiben
            #
            QKan.config.autokorrektur = autokorrektur
            QKan.config.selections.teilgebiete = liste_teilgebiete
            if epsg:
                QKan.config.epsg = epsg
            QKan.config.linkflaechen.auswahltyp = auswahltyp
            QKan.config.linkflaechen.bufferradius = bufferradius

            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            self.log.debug(
                f"""QKan-Modul Aufruf
                assigntgeb(
                    self.dbQK,
                    {auswahltyp},
                    {liste_teilgebiete},
                    [
                        ["haltungen", "geom"],
                        ["flaechen", "geom"],
                        ["schaechte", "geop"],
                        ["einleit", "geom"],
                        ["tezg", "geom"],
                        ["linksw", "glink"],
                        ["linkfl", "glink"],
                    ],
                    {autokorrektur},
                    {flaechen_bereinigen},
                    {bufferradius},
            )"""
            )

            if not assigntgeb(
                self.iface,
                self.db_qkan,
                auswahltyp,
                liste_teilgebiete,
                [
                    ["haltungen", "geom"],
                    ["flaechen", "geom"],
                    ["schaechte", "geop"],
                    ["einleit", "geom"],
                    ["tezg", "geom"],
                    ["linksw", "glink"],
                    ["linkfl", "glink"],
                ],
                autokorrektur,
                flaechen_bereinigen,
                bufferradius,
            ):
                del self.db_qkan
                return

        # --------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.db_qkan

    # ----------------------------------------------------------------------------------------------
    # Laden und Speichern von Teilgebietszuordnungen als Gruppe

    def run_managegroups(self) -> None:
        """Speichern und Wiederherstellen von Teilgebietszuordnungen als Gruppe"""

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {
                    "flaechen",
                    "haltungen",
                    "schaechte",
                    "linksw",
                    "einleit",
                    "linkfl",
                    "teilgebiete",
                    "tezg",
                }
                & get_editable_layers()
            )
            > 0
        ):
            self.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            self.log.error(
                "CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return

        self.db_qkan = DBConnection(dbname=database_qkan)

        if not self.db_qkan.connected:
            fehlermeldung(
                "Fehler in linkflaechen.application (4):\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )
            return

        # Anzeige initialisieren
        self.dlg_mg.show_groups()
        self.dlg_mg.lw_gruppen.setCurrentRow(0)
        self.dlg_mg.click_lw_groups()

        # show the dialog
        self.dlg_mg.show()
        self.dlg_mg.exec_()

        # Datenbankverbindungen schliessen
        del self.db_qkan

    # ----------------------------------------------------------------------------------------------
    # Logischen Cache der Verknüpfungen aktualisieren

    def run_updatelinks(self) -> None:
        """Aktualisieren des logischen Verknüpfungscaches in linkfl und linksw"""

        # Check, ob die relevanten Layer nicht editable sind.
        if (
            len(
                {"flaechen", "haltungen", "linkfl", "linksw", "tezg", "einleit"}
                & get_editable_layers()
            )
            > 0
        ):
            self.iface.messageBar().pushMessage(
                "Bedienerfehler: ",
                'Die zu verarbeitenden Layer dürfen nicht im Status "bearbeitbar" sein. Abbruch!',
                level=Qgis.Critical,
            )
            return

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            self.log.error(
                "k_link: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return

        # Datenbankverbindung für Abfragen
        self.db_qkan = DBConnection(dbname=database_qkan)

        if not self.db_qkan.connected:
            fehlermeldung(
                "Fehler in linkflaechen.application (5):\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )
            return

        self.dlg_ul.tf_qkDB.setText(database_qkan)

        # Festlegung des Fangradius
        fangradius = QKan.config.fangradius
        self.dlg_ul.tf_fangradius.setText(str(fangradius))
        self.log.debug("fangradius: {}".format(fangradius))

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
            delete_geom_none = self.dlg_ul.cb_deleteGeomNone.isChecked()
            flaechen_bereinigen = self.dlg_ul.cb_geomMakeValid.isChecked()
            fangradius = float(self.dlg_ul.tf_fangradius.text())

            # config schreiben
            QKan.config.linkflaechen.delete_geom_none = delete_geom_none
            QKan.config.fangradius = fangradius
            QKan.config.save()

            # Start der Verarbeitung
            if self.dlg_ul.cb_linkfl.isChecked():
                if not updatelinkfl(
                    self.db_qkan, fangradius, flaechen_bereinigen, delete_geom_none
                ):
                    del self.db_qkan
                    return

            if self.dlg_ul.cb_linksw.isChecked():
                if not updatelinksw(self.db_qkan, fangradius, delete_geom_none):
                    del self.db_qkan
                    return

            meldung("Fertig!", "Bereinigung Flächenverknüpfungen abgeschlossen.")

        # ----------------------------------------------------------------------------------------------
        # Datenbankverbindungen schliessen

        del self.db_qkan
