"""

  Set runoff parameters
  =====================

  Berechnet für die Flächenobjekte die Oberflächenabflussparameter nach HYSTEM/EXTRAN 7 oder DYNA.

  | Dateiname            : k_runoffparams.py
  | Date                 : Juli 2018
  | Copyright            : (C) 2018 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

"""

__author__ = "Joerg Hoettges"
__date__ = "July 2018"
__copyright__ = "(C) 2018, Joerg Hoettges"

from typing import List

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis, QgsMessageLog

from qkan import QKan, enums
from qkan.config import ToolsConfig
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import sqlconditions
from qkan.utils import get_logger

logger = get_logger("QKan.tools.k_runoffparams")

progress_bar = None

# Fortschritts- und Fehlermeldungen


# ------------------------------------------------------------------------------
# Hauptprogramm


def setRunoffparams(
    dbQK: DBConnection,
    runoffparamstype_choice: enums.RunOffParamsType,
    runoffmodeltype_choice: enums.RunOffModelType,
    runoffparamsfunctions: ToolsConfig.RunoffParams,
    liste_teilgebiete: List[str],
    liste_abflussparameter: List[str],
) -> None:
    """Berechnet Oberlächenabflussparameter für HYSTEM/EXTRAN 7 und DYNA/Kanal++.

    :db_qkan:                          Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :runoffparamstype_choice:       Simulationsprogramm, für das die Paremter berechnet werden sollen.
    :runoffmodeltype_choice:        Funktionen, die von den Simulationsprogrammen genutzt werden sollen
    :liste_teilgebiete:             Liste der bei der Bearbeitung zu berücksichtigenden Teilgebiete (Tabelle tezg)
    :dbtyp:                         Typ der Datenbank (SpatiaLite, PostGIS)

    Für alle TEZG-Flächen wird, falls nicht schon vorhanden, ein unbefestigtes Flächenobjekt erzeugt.
    Dazu können in der Auswahlmaske zunächst die Kombinationen aus Abflussparameter und Teilgebiet
    gewählt werden, die in der Tabelle "tezg" vorkommen und die nachfolgenden Voraussetzungen erfüllen:

    - Im Feld "abflussparameter" muss auf einen Abflussparameter verwiesen werden, der für unbefestigte
      Flächen erzeugt wurde (infiltrationsparameter > 0)
    """

    iface = QKan.instance.iface

    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "Info", "Oberflächenabflussparameter werden berechnet... Bitte warten."
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # status_message.setText("Erzeugung von unbefestigten Flächen ist in Arbeit.")
    progress_bar.setValue(1)

    # Beide Funktionen werden in einer for-Schleife abgearbeitet
    funlis = getattr(runoffparamsfunctions, runoffparamstype_choice.value)
    logger.debug("\nfunlis:\n{}".format(funlis))
    kriterienlis = ["IS NULL", "IS NOT NULL"]

    # Auswahl der zu bearbeitenden Flächen
    auswahl = sqlconditions(
        "AND",
        ["fl.teilgebiet", "fl.abflussparameter"],
        [liste_teilgebiete, liste_abflussparameter],
    )

    if runoffmodeltype_choice == enums.RunOffModelType.SPEICHERKASKADE:
        # Es werden sowohl aufzuteilende und nicht aufzuteilende Flächen berücksichtigt
        # Schleife über befestigte und durchlässige Flächen (Kriterium: bodenklasse IS NULL)
        # dabei werden aus funlis und kriterienlis nacheinander zuerst die relevanten Inhalte für befestigte und anschließend
        # für durchlässige Flächen genommen.

        for fun, kriterium in zip(funlis[:2], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.pk,
                        lf.flnam AS flnam, 
                        coalesce(fl.neigkl, 1) AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        fl.teilgebiet AS teilgebiet, 
                        CASE WHEN (fl.aufteilen <> 'ja' AND not fl.aufteilen) OR fl.aufteilen IS NULL THEN fl.geom 
                             ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, speicherzahl, speicherkonst) = (
                    SELECT 'Speicherkaskade', 3, ({fun})*0.3333
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(
                auswahl=auswahl, fun=fun, kriterium=kriterium
            )
            if not dbQK.sql(sql, "QKan.tools.setRunoffparams (1), {}".format(kriterium)):
                return

    elif runoffmodeltype_choice == enums.RunOffModelType.SPEICHERKASKADE:
        # Fließzeit Kanal
        for fun, kriterium in zip(funlis[2:4], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.pk,
                        lf.flnam AS flnam, 
                        coalesce(fl.neigkl, 1) AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        fl.teilgebiet AS teilgebiet, 
                        CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, fliesszeitkanal) = (
                    SELECT 'Fliesszeiten', {fun}
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(
                auswahl=auswahl, fun=fun, kriterium=kriterium
            )
            if not dbQK.sql(sql, "QKan.tools.setRunoffparams (2)"):
                return

        # Fließzeit Oberfläche
        for fun, kriterium in zip(funlis[4:6], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.pk,
                        lf.flnam AS flnam, 
                        coalesce(fl.neigkl, 1) AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        fl.teilgebiet AS teilgebiet, 
                        CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, fliesszeitflaeche) = (
                    SELECT 'Fliesszeiten', {fun}
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(
                auswahl=auswahl, fun=fun, kriterium=kriterium
            )
            if not dbQK.sql(sql, "QKan.tools.setRunoffparams (3)"):
                return

    elif runoffmodeltype_choice == enums.RunOffModelType.SCHWERPUNKTLAUFZEIT:
        for fun, kriterium in zip(funlis[:2], kriterienlis):
            sql = """
                WITH flintersect AS (
                    SELECT
                        lf.pk,
                        lf.flnam AS flnam, 
                        coalesce(fl.neigkl, 1) AS neigkl,
                        fl.abflussparameter AS abflussparameter, 
                        fl.teilgebiet AS teilgebiet, 
                        CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom ELSE CastToMultiPolygon(intersection(fl.geom,tg.geom)) END AS geom
                    FROM linkfl AS lf
                    INNER JOIN flaechen AS fl
                    ON lf.flnam = fl.flnam
                    LEFT JOIN tezg AS tg
                    ON lf.tezgnam = tg.flnam),
                qdist AS (
                    SELECT 
                        lf.pk,
                        ST_Distance(fl.geom,ha.geom) AS "abstand",
                        CASE WHEN Intersects(ha.geom,fl.geom) THEN
                            HausdorffDistance(fl.geom,Intersection(ha.geom,fl.geom))
                        ELSE 
                            MaxDistance(fl.geom,ClosestPoint(ha.geom,fl.geom))-ST_Distance(fl.geom,ha.geom)
                        END AS "fliesslaenge",
                       fl.neigkl AS "neigkl", 
                       CASE fl.neigkl WHEN 1 THEN 0.5 WHEN 2 THEN 2.5 WHEN 3 THEN 7.0 WHEN 4 THEN 12 WHEN 5 THEN 20 END AS "neigung"
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN haltungen AS ha
                    ON ha.haltnam = lf.haltnam
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )
                UPDATE linkfl 
                SET (abflusstyp, fliesszeitflaeche) = (
                    SELECT 'Schwerpunktlaufzeit', {fun}
                    FROM qdist
                    WHERE qdist.pk = linkfl.pk)
                WHERE pk IN (
                    SELECT lf.pk
                    FROM linkfl AS lf
                    INNER JOIN flintersect AS fl
                    ON lf.pk = fl.pk
                    INNER JOIN abflussparameter AS ap
                    ON fl.abflussparameter = ap.apnam
                    WHERE ap.bodenklasse {kriterium}{auswahl}
                )""".format(
                auswahl=auswahl, fun=fun, kriterium=kriterium
            )
            if not dbQK.sql(sql, "QKan.tools.setRunoffparams (4)"):
                return

    # status_message.setText("Erzeugung von unbefestigten Flächen")
    progress_bar.setValue(90)

    dbQK.commit()

    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="\nOberflächenabflussparameter sind berechnet und eingetragen!",
        level=Qgis.Info,
    )

    progress_bar.setValue(100)
    status_message.setText(
        "Oberflächenabflussparameter sind berechnet und eingetragen!"
    )
    status_message.setLevel(Qgis.Success)
