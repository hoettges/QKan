# -*- coding: utf-8 -*-

"""
  Import from HE
  ==============

  Aus einer Hystem-Extran-Datenbank im Firebird-Format werden Kanaldaten
  in die QKan-Datenbank importiert. Dazu wird eine Projektdatei erstellt,
  die verschiedene thematische Layer erzeugt, u.a. eine Klassifizierung
  der Schachttypen.

"""

__author__ = "Joerg Hoettges"
__date__ = "September 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"

import logging
from typing import List

from qgis.core import Qgis, QgsMessageLog
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QProgressBar

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import checknames, fehlermeldung

logger = logging.getLogger("QKan.createunbeffl.k_unbef")
progress_bar = None


def create_unpaved_areas(
    iface: QgisInterface,
    db_qkan: DBConnection,
    selected_abflparam: List,
    autokorrektur: bool,
) -> bool:
    """Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    @param iface
    @param db_qkan              Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.

    @param selected_abflparam   Liste der bei der Bearbeitung zu berücksichtigenden Kombinationen aus
                                Abflussparameter und Teilgebiet (Tabelle tezg)

    @param autokorrektur        Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                                werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                                abgebrochen.

    Für alle TEZG-Flächen wird, falls nicht schon vorhanden, ein unbefestigtes Flächenobjekt erzeugt.
    Dazu können in der Auswahlmaske zunächst die Kombinationen aus Abflussparameter und Teilgebiet
    gewählt werden, die in der Tabelle "tezg" vorkommen und die nachfolgenden Voraussetzungen erfüllen:

    - Im Feld "abflussparameter" muss auf einen Abflussparameter verwiesen werden, der für unbefestigte
      Flächen erzeugt wurde (infiltrationsparameter > 0)
    """

    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "Info", "Erzeugung von unbefestigten Flächen " "in Arbeit. Bitte warten."
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # status_message.setText("Erzeugung von unbefestigten Flächen ist in Arbeit.")
    progress_bar.setValue(1)

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    # Kontrolle, ob tezg-Flächen eindeutig Namen haben:

    if not checknames(db_qkan, "tezg", "flnam", "ft_", autokorrektur):
        return False
    if not checknames(db_qkan, "flaechen", "flnam", "f_", autokorrektur):
        return False

    # Prüfung, ob unzulässige Kombinationen ausgewählt wurden
    if len(selected_abflparam) > 0:
        logger.debug("\nliste_selAbflparamTeilgeb (2): {}".format(selected_abflparam))
        if False in [(attr[-1] == "") for attr in selected_abflparam]:
            fehlermeldung(
                "Falsche Auswahl",
                "Bitte nur zulässige Abflussparameter und Teilgebiete auswählen "
                "(siehe Spalte 'Anmerkungen')",
            )
            return False
    else:
        sql = """SELECT count(*) AS anz
            FROM tezg AS te
            LEFT JOIN abflussparameter AS ap
            ON te.abflussparameter = ap.apnam
            LEFT JOIN bodenklassen AS bk
            ON bk.bknam = ap.bodenklasse
            WHERE te.abflussparameter ISNULL OR
                  bk.infiltrationsrateanfang ISNULL OR
                  bk.infiltrationsrateanfang < 0.00001"""
        if not db_qkan.sql(sql, "QKan.CreateUnbefFlaechen (1)"):
            return False
        data = db_qkan.fetchall()
        if len(data) > 0:
            if data[0][0] > 0:
                fehlermeldung(
                    "Unvollständige Daten",
                    "In der Tabelle Haltungsflächen sind noch fehlerhafte Daten zu den Abflussparametern "
                    "oder den Bodenklassen enthalten. ",
                )
                return False

    # Für die Erzeugung der Restflächen reicht eine SQL-Abfrage aus.

    # status_message.setText("Erzeugung von unbefestigten Flächen")
    progress_bar.setValue(10)

    # Vorbereitung des Auswahlkriteriums für die SQL-Abfrage: Kombination aus abflussparameter und teilgebiet
    # Dieser Block ist identisch in k_unbef und in application enthalten

    if len(selected_abflparam) == 0:
        auswahl = ""
    elif len(selected_abflparam) == 1:
        auswahl = " AND"
    elif len(selected_abflparam) >= 2:
        auswahl = " AND ("
    else:
        fehlermeldung("Interner Fehler", "Fehler in Fallunterscheidung!")
        return False

    # Anfang SQL-Krierien zur Auswahl der tezg-Flächen
    first = True
    for attr in selected_abflparam:
        if attr[4] == "None" or attr[1] == "None":
            fehlermeldung(
                "Datenfehler: ",
                u'In den ausgewählten Daten sind noch Datenfelder nicht definiert ("NULL").',
            )
            return False
        if first:
            first = False
            auswahl += """ (tezg.abflussparameter = '{abflussparameter}' AND
                            tezg.teilgebiet = '{teilgebiet}')""".format(
                abflussparameter=attr[0], teilgebiet=attr[1]
            )
        else:
            auswahl += """ OR\n      (tezg.abflussparameter = '{abflussparameter}' AND
                            tezg.teilgebiet = '{teilgebiet}')""".format(
                abflussparameter=attr[0], teilgebiet=attr[1]
            )

    if len(selected_abflparam) >= 2:
        auswahl += ")"
    # Ende SQL-Krierien zur Auswahl der tezg-Flächen

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # 1. aus der Abfrage werden alle Datensätze ohne geom-Objekte ausgeschlossen
    # 2. Wenn in einer tezg-Fläche keine Fläche liegt, wird einfach die tezg-Fläche übernommen

    sql = """WITH flbef AS (
            SELECT 'fd_' || ltrim(tezg.flnam, 'ft_') AS flnam, 
              tezg.haltnam AS haltnam, tezg.neigkl AS neigkl, 
              tezg.regenschreiber AS regenschreiber, tezg.teilgebiet AS teilgebiet,
              tezg.abflussparameter AS abflussparameter,
              'Erzeugt mit Plugin Erzeuge unbefestigte Flaechen' AS kommentar, 
              MakeValid(tezg.geom) AS geot, 
              ST_Union(MakeValid(flaechen.geom)) AS geob
            FROM (SELECT * FROM tezg WHERE geom IS NOT NULL) AS tezg
            LEFT JOIN (SELECT * FROM flaechen WHERE geom IS NOT NULL) AS flaechen
            ON Intersects(tezg.geom, flaechen.geom)
            WHERE 'fd_' || ltrim(tezg.flnam, 'ft_') not in 
            (   SELECT flnam FROM flaechen WHERE flnam IS NOT NULL){auswahl}
            GROUP BY tezg.pk)
            INSERT INTO flaechen (flnam, haltnam, neigkl, regenschreiber, teilgebiet, abflussparameter, kommentar, geom) 
             SELECT flnam AS flnam, haltnam, neigkl, regenschreiber, teilgebiet, abflussparameter,
            kommentar, 
            CASE WHEN geob IS NULL  THEN geot ELSE CastToMultiPolygon(Difference(geot,geob)) END AS geof FROM flbef
            WHERE area(geof) > 0.5 AND geof IS NOT NULL""".format(
        auswahl=auswahl
    )

    logger.debug(
        "QKan.k_unbef (3) - liste_selAbflparamTeilgeb = \n{}".format(
            str(selected_abflparam)
        )
    )
    if not db_qkan.sql(sql, "QKan.CreateUnbefFlaechen (4)"):
        return False

    # # status_message.setText("Erstellen der Anbindungen für die unbefestigten Flächen")
    # progress_bar.setValue(50)

    # # Hinzufügen von Verknüpfungen in die Tabelle linkfl für die neu erstellten unbefestigten Flächen
    # sql = """INSERT INTO linkfl (flnam, aufteilen, teilgebiet, geom, glink)
    # SELECT
    # fl.flnam AS flnam,
    # NULL AS aufteilen,
    # fl.teilgebiet AS teilgebiet,
    # NULL AS geom,
    # MakeLine(PointOnSurface(fl.geom),Centroid(ha.geom)) AS glink
    # FROM flaechen AS fl
    # LEFT JOIN haltungen AS ha
    # ON fl.haltnam = ha.haltnam
    # INNER JOIN tezg AS tg
    # ON 'fd_' || ltrim(tg.flnam, 'ft_') = fl.flnam
    # WHERE fl.flnam NOT IN
    # (   SELECT flnam FROM linkfl WHERE flnam IS NOT NULL)"""

    # if not db_qkan.sql(sql, "QKan.CreateUnbefFlaechen (5)"):
    # return False

    # status_message.setText("Nachbearbeitung")
    progress_bar.setValue(90)

    db_qkan.commit()

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    iface.mainWindow().statusBar().clearMessage()
    iface.messageBar().pushMessage(
        "Information", "Restflächen sind erstellt!", level=Qgis.Info
    )
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(message="\nRestflächen sind erstellt!", level=Qgis.Info)

    progress_bar.setValue(100)
    status_message.setText("Erzeugung von unbefestigten Flächen abgeschlossen.")
    status_message.setLevel(Qgis.Success)
    return True
