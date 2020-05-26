import logging
import typing

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QTableWidgetItem
from qgis.gui import QgisInterface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, get_database_QKan

# noinspection PyUnresolvedReferences
from . import resources
from .application_dialog import CreateUnbefFlDialog, list_selected_tab_items
from .k_unbef import create_unpaved_areas

# Anbindung an Logging-System (Initialisierung in __init__)
logger = logging.getLogger("QKan.createunbeffl.application")


class CreateUnbefFl:
    def __init__(self, iface: QgisInterface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.db_qkan: typing.Optional[DBConnection] = None

        self.dlg = CreateUnbefFlDialog(self)

        logger.info("QKan_CreateUnbefFlaechen initialisiert...")

    # noinspection PyMethodMayBeStatic
    def tr(self, message: str):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("CreateUnbefFl", message)

    # noinspection PyPep8Naming
    def initGui(self):
        icon_path = ":/plugins/qkan/createunbeffl/icon.png"
        QKan.instance.add_action(
            icon_path,
            text=self.tr("Erzeuge unbefestigte Flächen..."),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        self.dlg.close()

    def run(self):
        """Run method that performs all the real work"""

        database_qkan, epsg = get_database_QKan()
        if not database_qkan:
            logger.error(
                "CreateUnbefFl: database_QKan konnte nicht aus den Layern ermittelt werden. Abbruch!"
            )
            return False

        # Abfragen der Tabelle tezg nach verwendeten Abflussparametern
        self.db_qkan = DBConnection(dbname=database_qkan)
        if not self.db_qkan.connected:
            fehlermeldung(
                "Fehler in createunbeffl.application:\n",
                f"QKan-Datenbank {database_qkan} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!",
            )
            return None

        # Kontrolle, ob in Tabelle "abflussparameter" ein Datensatz für unbefestigte Flächen vorhanden ist
        # (Standard: apnam = '$Default_Unbef')

        sql = """SELECT apnam
            FROM abflussparameter
            WHERE bodenklasse IS NOT NULL AND trim(bodenklasse) <> ''"""

        if not self.db_qkan.sql(sql, "createunbeffl.run (1)"):
            del self.db_qkan
            return False

        data = self.db_qkan.fetchone()

        if data is None:
            if QKan.config.autokorrektur:
                daten = [
                    u"'$Default_Unbef', u'von QKan ergänzt', 0.5, 0.5, 2, 5, 0, 0, 'LehmLoess', '13.01.2011 08:44:50'"
                ]

                for ds in daten:
                    sql = u"""INSERT INTO abflussparameter
                             ( 'apnam', 'kommentar', 'anfangsabflussbeiwert', 'endabflussbeiwert', 'benetzungsverlust', 
                               'muldenverlust', 'benetzung_startwert', 'mulden_startwert', 'bodenklasse', 
                               'createdat') Values ({})""".format(
                        ds
                    )
                    if not self.dbQK.sql(sql, u"createunbeffl.run (2)"):
                        del self.dbQK
                        return False
            else:
                fehlermeldung(
                    "Datenfehler: ",
                    'Bitte ergänzen Sie in der Tabelle "abflussparameter" einen Datensatz '
                    'für unbefestigte Flächen ("bodenklasse" darf nicht leer oder NULL sein)',
                )

        # # Kontrolle, ob noch Flächen in Tabelle "tezg" ohne Zuordnung zu einem Abflussparameter oder zu einem
        # # Abflussparameter, bei dem keine Bodenklasse definiert ist (Kennzeichen für undurchlässige Flächen).

        # sql = """SELECT te.abflussparameter, te.teilgebiet, count(*) AS anz
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

        # fehlermeldung(u'In Tabelle "tezg" fehlen Abflussparameter oder gehören zu'
        # 'befestigten Flächen (Bodenklasse = NULL):\n',
        # u'\n'.join(liste))
        # return False

        sql = """SELECT te.abflussparameter, te.teilgebiet, bk.bknam, count(*) AS anz, 
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
        if not self.db_qkan.sql(sql, "createunbeffl.run (4)"):
            del self.db_qkan
            return None

        listetezg = self.db_qkan.fetchall()
        nzeilen = len(listetezg)
        self.dlg.tw_selAbflparamTeilgeb.setRowCount(nzeilen)
        self.dlg.tw_selAbflparamTeilgeb.setHorizontalHeaderLabels(
            [
                "Abflussparameter",
                "Teilgebiet",
                "Bodenklasse",
                "Anzahl",
                "Anmerkungen",
                "",
            ]
        )
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(
            0, 144
        )  # 17 Pixel für Rand und Nummernspalte (und je Spalte?)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(1, 140)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(2, 90)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(3, 50)
        self.dlg.tw_selAbflparamTeilgeb.setColumnWidth(4, 200)
        for i, elem in enumerate(listetezg):
            for j, item in enumerate(elem):
                cell = "{}".format(elem[j])
                self.dlg.tw_selAbflparamTeilgeb.setItem(i, j, QTableWidgetItem(cell))
                self.dlg.tw_selAbflparamTeilgeb.setRowHeight(i, 20)

        # Autokorrektur
        self.dlg.cb_autokorrektur.setChecked(QKan.config.autokorrektur)

        self.dlg.count_selection()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        logger.debug("result = {}".format(repr(result)))
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass

            selected_abflparam = list_selected_tab_items(
                self.dlg.tw_selAbflparamTeilgeb
            )
            logger.debug(
                "\nliste_selAbflparamTeilgeb (1): {}".format(selected_abflparam)
            )
            autokorrektur: bool = self.dlg.cb_autokorrektur.isChecked()

            QKan.config.autokorrektur = autokorrektur
            QKan.config.save()

            # Start der Verarbeitung

            # Modulaufruf in Logdatei schreiben
            logger.debug(
                f"""QKan-Modul Aufruf
                createUnbefFlaechen(
                    self.iface, 
                    self.dbQK, 
                    {selected_abflparam}, 
                    {autokorrektur}
                )"""
            )

            if not create_unpaved_areas(
                self.iface, self.db_qkan, selected_abflparam, autokorrektur
            ):
                del self.db_qkan
                return False
