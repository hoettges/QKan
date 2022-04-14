# -*- coding: utf-8 -*-

"""----------------------------------------------------------------------------------
/***************************************************************************
 k_qgsw
                                 A QGIS plugin
 Transfer von Kanaldaten aus QKan nach SWMM 5.0.1
                              -------------------
                            begin                : 2015-08-10
                            git sha              : $Format:%H$
                            copyright            : (C) 2015 by Jörg Höttges / FH Aachen
                            email                : hoettges@fh-aachen.de
 ***************************************************************************/

 Tool Name:   k_qgsw.py
 Source Name: k_qgsw.py
 Version:     1.0.0
 Date:        29.05.2016
 Author:      Joerg Hoettges
 Required Arguments:

Transfer von Kanaldaten aus QKan nach SWMM 5.0.1


----------------------------------------------------------------------------------"""

import logging
import math
from typing import List

from qgis.core import Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QProgressBar

from qkan import QKan
from qkan.database.dbfunc import DBConnection

logger = logging.getLogger("QKan.exportswmm")

progress_bar = None

# --------------------------------------------------------------------------------------------------
# Start des eigentlichen Programms

# MOUSE-Haltungstyp: 1 = Kreis, 2 = Profil (CRS), 3 = Rechteck, 4 = Maulprofil, 5 = Eiprofil, 6 = Quadrat, 7 = "Natural Channel"

ref_profile = {"1": "CIRCULAR", "3": "RECT_CLOSED", "5": "EGG"}


def exportKanaldaten(
    iface: QgisInterface,
    databaseQKan: str,
    templateSwmm: str,
    ergfileSwmm: str,
    mit_verschneidung: bool,
    liste_teilgebiete: List[str],
) -> None:
    """
    :iface:                 QGIS-Interface zur GUI
    :type:                  QgisInterface

    :databaseQKan:         Pfad zur QKan-Datenbank
    :type:                  string

    :templateSwmm:          Vorlage für die zu erstellende SWMM-Datei
    :type:                  string

    :ergfileSwmm:           Ergebnisdatei für SWMM
    :type:                  string

    :mit_verschneidung:     Flächen werden mit Haltungsflächen verschnitten (abhängig von Attribut "aufteilen")
    :type:                  Boolean

    :liste_teilgebiete:     Liste der ausgewählten Teilgebiete
    :type:                  string
    """

    # fortschritt('Start...',0.02)

    # --------------------------------------------------------------------------------------------------
    # Zuordnungstabellen. Profile sind in einer json-Datei gespeichert, die sich auf dem
    # Roaming-Verzeichnis befindet (abrufbar mit site.getuserbase()
    # Andere Tabellen sind in diesem Quellcode integriert, wie z. B. ref_typen

    iface = QKan.instance.iface

    # Create progress bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)

    status_message = iface.messageBar().createMessage(
        "", "Export in Arbeit. Bitte warten..."
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # Einlesen der Vorlagedatei

    with open(templateSwmm) as swvorlage:
        swdaten = swvorlage.read()

    # Verbindung zur Spatialite-Datenbank mit den Kanaldaten

    dbQK = DBConnection(
        dbname=databaseQKan
    )  # Datenbankobjekt der QKan-Datenbank zum Lesen
    if not dbQK.connected:
        logger.error(
            """Fehler in exportSwmm:
            QKan-Datenbank {databaseQKan} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"""
        )
        return None

    # --------------------------------------------------------------------------------------------------
    # Allgemeine Initialisierungen

    datacu = ""  # Datenzeilen für [CURVES]

    # --------------------------------------------------------------------------------------------------
    # Flächen. Die Daten müssen in mehrere Sektoren der *.inp-Datei geschrieben werden:
    # [SUBCATCHMENTS]
    # [SUBAREAS]
    # [INFILTRATION]

    # fortschritt('Flaechen...',0.04)

    # Nur Daten fuer ausgewaehlte Teilgebiete
    if len(liste_teilgebiete) != 0:
        auswahlw = " WHERE teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
    else:
        auswahlw = ""
    auswahlw.replace(" WHERE teilgebiet ", " AND teilgebiet ")

    # Erläuterung der Vorgehensweise für [SUBAREAS]:
    # Für jede tezg muss es zwei Datensätze in der Taelle abflussparameter geben: Eine für befestigte
    # und eine für durchlässige Flächen. Dies wird in QKan gekennzeichnet durch:
    # bodenklasse IS NULL or bodenklasse = ''
    # Falls keine solchen Datensätze für die zu exportierenden tezg vorliegen, werden diese hier angelegt

    numChanged = 0  # Für Meldung, falls Daten ergänzt wurden

    # Hinzufügen fehlender abflussparameter für befestigte Flächen
    sql = f"""
        INSERT INTO abflussparameter (
            apnam, anfangsabflussbeiwert, endabflussbeiwert, 
            benetzungsverlust, muldenverlust, benetzung_startwert, 
            mulden_startwert, rauheit_kst, pctZero, bodenklasse, 
            kommentar, 
            createdat)
        SELECT 
            tg.abflussparameter, 0.25, 0.85, 
            0.7, 1.8, 0., 
            0., 1./0.015, 0.06*2.54, NULL, 
            'Automatisch ergänzt für SWMM-Export',
            coalesce(createdat, CURRENT_TIMESTAMP)) AS createdat
        FROM tezg AS tg
        LEFT JOIN abflussparameter AS ap
        ON tg.abflussparameter = ap.apnam and (ap.bodenklasse IS NULL OR ap.bodenklasse = '')
        WHERE ap.apnam IS NULL
        GROUP BY tg.abflussparameter"""

    if not dbQK.sql(sql, "dbQK: exportSWMM (1)"):
        del dbQK
        return

    numChanged += dbQK.rowcount()

    # Hinzufügen fehlender abflussparameter für durchlässige Flächen
    sql = f"""
        INSERT INTO abflussparameter (
            apnam, anfangsabflussbeiwert, endabflussbeiwert, 
            benetzungsverlust, muldenverlust, benetzung_startwert, 
            mulden_startwert, rauheit_kst, pctZero, bodenklasse, 
            kommentar, 
            createdat)
        SELECT 
            tg.abflussparameter, 0.5, 0.5, 
            2.0, 5.0, 0., 
            0., 1./0.024, 0.3*2.54, NULL, 
            'Automatisch ergänzt für SWMM-Export',
            coalesce(createdat, CURRENT_TIMESTAMP)) AS createdat
        FROM tezg AS tg
        LEFT JOIN abflussparameter AS ap
        ON tg.abflussparameter = ap.apnam and ap.bodenklasse IS NOT NULL AND ap.bodenklasse <> ''
        WHERE ap.apnam IS NULL
        GROUP BY tg.abflussparameter"""

    if not dbQK.sql(sql, "dbQK: exportSWMM (2)"):
        del dbQK
        return

    numChanged += dbQK.rowcount()

    if numChanged > 0:
        status_message.setText(f"Es wurden {numChanged} Abflussparameter hinzugefügt!")

    sql = f"""
        SELECT
            tg.flnam AS name,
            tg.regenschreiber AS rain_gage,
            tg.schnam AS outlet,
            area(tg.geom)/10000. AS area,
            pow(area(tg.geom), 0.5)*1.3 AS width                        -- 1.3: pauschaler Faktor für SWMM
            tg.befgrad AS imperv,
            tg.neigung AS neigung,
            tg.abflussparameter AS abflussparameter, 
            apbef.rauheit_kst AS nImperv, 
            apdur.rauheit_kst AS nPerv,
            apbef.muldenverlust AS sImperv, 
            apdur.muldenverlust AS sPerv,
            apbef.pctZero AS pctZero, 
            bk.infiltrationsrateende*60 AS maxRate,                     -- mm/min -> mm/h
            bk.infiltrationsrateanfang*60 AS minRate,
            bk.rueckgangskonstante/24. AS decay,                        -- 1/d -> 1/h 
            1/(coalesce(bk.regenerationskonstante, 1./7.) AS dryTime,   -- 1/d -> d , Standardwert aus SWMM-Testdaten
            bk.saettigungswassergehalt AS maxInfil
        FROM tezg AS tg
        JOIN abflussparameter AS apbef
        ON tg.abflussparameter = ap.apnam and (apbef.bodenklasse IS NULL OR apbef.bodenklasse = '')
        JOIN abflussparameter AS apdur
        ON tg.abflussparameter = ap.apnam and apdur.bodenklasse IS NOT NULL AND apdur.bodenklasse <> ''
        JOIN bodenklassen AS bk
        ON apdur.bodenklasse = bodenklasse.bknam
        {auswahlw}"""

    if not dbQK.sql(sql, "dbQK: exportSWMM (3)"):
        del dbQK
        return

    datasc = ""  # Datenzeilen [subcatchments]
    datasa = ""  # Datenzeilen [subareas]
    datain = ""  # Datenzeilen [infiltration]

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        (
            name_1,
            rain_gage,
            outlet_1,
            area,
            width,
            imperv,
            neigung,
            abflussparameter,
            nImperv,
            nPerv,
            sImperv,
            sPerv,
            pctZero,
            maxRate,
            minRate,
            decay,
            dryTime,
            maxInfil,
        ) = ["NULL" if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        name = name_1.replace(" ", "_")
        outlet = outlet_1.replace(" ", "_")

        datasc += (
            f"{name:<16s} {rain_gage:<16s} {outlet:<16s} {area:<8.2f} "
            f"{imperv:<8.1f} {width:<8.0f} {neigung:<8.1f} 0                        \n"
        )
        datasa += (
            f"{name:<16s} {nImperv:<8.3f} {nPerv:<8.2f} {sImperv:<8.2f} {sPerv:<8.1f} "
            f"{pctZero:<8.0f} OUTLET    \n"
        )
        datain += f"{name:<16s} {maxRate:<8.1f} {minRate:<8.1f} {decay:<8.1f} {dryTime:<8.0f} {maxInfil}\n"

    swdaten = swdaten.replace("{SUBCATCHMENTS}\n", datasc)
    swdaten = swdaten.replace("{SUBAREAS}\n", datasa)
    swdaten = swdaten.replace("{INFILTRATION}\n", datain)

    # --------------------------------------------------------------------------------------------------
    # [DWF]

    # fortschritt('Flaechen...',0.08)
    progress_bar.setValue(20)

    sql = """SELECT
        e.schnam AS node,
        sum(e.zufluss) AS value
    FROM
        einleit AS e
        {auswahlw}
    GROUP BY e.schnam"""

    cursl.execute(sql)

    datadw = ""  # Datenzeilen dry weather inflow

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        (node_t, value) = ["NULL" if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        node_t.replace(" ", "_")

        datadw += "{node:<16s} FLOW             {value:<10.4f} \n"

    if "[DWF]" in swdaten:
        swdaten = swdaten.replace("{DWF}\n", datadw)
    else:
        meldung(
            f"Template in Abschnitt [DWF]: ",
            "Abschnitt nicht vorhanden und wurde am Ende ergänzt",
        )

        swdaten += (
            "\n[DWF]"
            ";;                                Average    Time"
            ";;Node           Parameter        Value      Patterns"
            ";;-------------- ---------------- ---------- ----------\n"
        )

        swdaten += datadw

    # --------------------------------------------------------------------------------------------------
    # [JUNCTIONS]
    # [COORDINATES]

    # fortschritt('Schaechte...',0.30)
    progress_bar.setValue(30)

    sql = """SELECT
        s.schnam AS name, 
        s.sohlhoehe AS invertElevation, 
        s.deckelhoehe - s.sohlhoehe AS maxDepth, 
        0 AS initDepth, 
        0 AS surchargeDepth,
        1000 AS pondedArea,   
        X(geop) AS xsch, Y(geop) AS ysch,  
    FROM schaechte AS s
    WHERE s.schachttyp = 'Schacht'
    """
    cursl.execute(sql)

    dataju = ""  # Datenzeilen [JUNCTIONS]
    # datacu = ''          # Datenzeilen [CURVES], ist schon oben initialisiert worden
    dataco = ""  # Datenzeilen [COORDINATES]

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        (
            name_t,
            invertElevation,
            maxDepth,
            initDepth,
            surchargeDepth,
            pondedArea,
            xsch,
            ysch,
        ) = ["NULL" if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        name = name_t.replace(" ", "_")

        # [JUNCTIONS]
        dataju += (
            f"{name:<16s} {invertElevation:<10.3f} {maxDepth:<10.3f} {initDepth:<10.3f} "
            f"{surchargeDepth:<10.3f} {pondedArea:<10.1f}\n"
        )

        # [COORDINATES]
        dataco += f"{name:<16s} {xsch:<18.3f} {ysch:<18.3f}\n"

    # swdaten = swdaten.replace('{JUNCTIONS}\n',dataju)         # siehe unten
    # swdaten = swdaten.replace('{COORDINATES}\n',dataco)       # siehe unten

    # --------------------------------------------------------------------------------------------------
    # [JUNCTIONS]
    # [OUTFALLS]

    dataou = ""  # Datenzeilen [OUTFALLS]
    # dataco = ''          # Datenzeilen [COORDINATES], ist schon oben initialisiert worden

    dataou += "{:<16s} {:<10.3f} FREE                        NO                       \n".format(
        c[0], c[3]
    )

    swdaten = swdaten.replace("{OUTFALLS}\n", dataou)
    swdaten = swdaten.replace("{JUNCTIONS}\n", dataju)

    # todo

    # --------------------------------------------------------------------------------------------------
    # [JUNCTIONS]
    # [STORAGE]

    datast = ""  # Datenzeilen [STORAGE]
    # dataco = ''          # Datenzeilen [COORDINATES], ist schon oben initialisiert worden

    datast += "{:<16s} {:<8.3f} 4          0          TABULAR    sp_{:<24}  0        0       \n".format(
        c[0], c[3], c[0]
    )
    if len(datacu) > 0:
        datacu += ";\n"  # ';' falls schon Datensätze
    datacu += "sp_{:<13s} Storage    0          500       \n".format(c[0][:13])
    datacu += "sp_{:<13s}            5          500       \n".format(c[0][:13])

    swdaten = swdaten.replace(
        "{JUNCTIONS}\n", dataju
    )  # Daten aus mehreren Abschnitten!
    swdaten = swdaten.replace("{STORAGE}\n", datast)

    # todo

    # --------------------------------------------------------------------------------------------------
    # [CONDUITS]
    # [XSECTIONS]

    # fortschritt('Haltungen...',0.60)
    progress_bar.setValue(40)

    sql = """SELECT
        h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, material, hoehe, breite
    FROM
        haltungen AS h
    JOIN
        gebiete AS g
    ON 
        Intersects(h.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY h.haltnam"""
    cursl.execute(sql)

    datacd = ""  # Datenzeilen
    dataxs = ""  # Datenzeilen

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ["NULL" if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(" ", "_")
        c[1] = c[1].replace(" ", "_")
        c[2] = c[2].replace(" ", "_")

        datacd += "{:<16s} {:<16s} {:<16s} {:<10.3f} {:<10.3f} 0          0          0          0         \n".format(
            c[0], c[1], c[2], c[3], c[4]
        )
        dataxs += "{:<16s} {:<12s} {:<16.3f} {:<10.3f} 0          0          1                    \n".format(
            c[0], ref_profile[c[5]], c[6], c[7]
        )

    swdaten = swdaten.replace("{CONDUITS}\n", datacd)
    # XSECTIONS wird erst nach [weirs] geschrieben

    # --------------------------------------------------------------------------------------------------
    # [PUMPS] + [CURVES]

    # fortschritt('Pumpen...',0.70)
    progress_bar.setValue(50)

    sql = """SELECT
        p.name AS name,
        p.schoben AS schoben,
        p.schunten AS schunten,
        p.typ AS typ,
        p.sohle AS sohle
    FROM
        pumpen AS p
    JOIN
        gebiete AS g
    ON 
        Intersects(p.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY p.name"""
    cursl.execute(sql)

    datapu = ""  # Datenzeilen
    # datacu = ''          # Datenzeilen, ist schon oben initialisiert worden

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ["NULL" if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(" ", "_")
        c[1] = c[1].replace(" ", "_")
        c[2] = c[2].replace(" ", "_")

        datapu += (
            "{:<16s} {:<16s} {:<16s} pu_{:<13s} ON       0        0       \n".format(
                c[0], c[1], c[2], c[0][:13]
            )
        )

        if len(datacu) > 0:
            datacu += ";\n"  # ';' falls schon Datensätze
        datacu += "pu_{:<13s} Pump3      0          0.120     \n".format(c[0][:13])
        datacu += "pu_{:<13s}            50         0.000     \n".format(c[0][:13])

    # d erst am Ende (s.u.)
    swdaten = swdaten.replace("{PUMPS}\n", datapu)

    # --------------------------------------------------------------------------------------------------
    # [WEIRS]
    # [XSECTIONS] zusaetzlich fuer Wehre

    # fortschritt('Wehre...',0.75)
    progress_bar.setValue(60)

    sql = """SELECT
        w.name AS name,
        w.schoben AS schoben,
        w.schunten AS schunten,
        w.typ AS typ,
        w.schwellenhoehe AS schwellenhoehe,
        w.kammerhoehe AS kammerhoehe,
        w.laenge AS laenge
    FROM
        wehre AS w
    JOIN
        gebiete AS g
    ON 
        Intersects(w.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY w.name"""
    cursl.execute(sql)

    datawe = ""  # Datenzeilen
    # dataxs schon oben initialisiert

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ["NULL" if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(" ", "_")
        c[1] = c[1].replace(" ", "_")
        c[2] = c[2].replace(" ", "_")

        datawe += "{:<16s} {:<16s} {:<16s} TRANSVERSE   0          3.33       NO       0        0          YES       \n".format(
            c[0], c[1], c[2]
        )
        dataxs += (
            "{:<16s} RECT_OPEN    {:<16.3f} {:<10.3f} 0          0         \n".format(
                c[0], c[5], c[6]
            )
        )

    swdaten = swdaten.replace("{WEIRS}\n", datawe)
    swdaten = swdaten.replace("{XSECTIONS}\n", dataxs)

    # --------------------------------------------------------------------------------------------------
    # [Polygons]

    # fortschritt('Flaechen...',0.60)
    progress_bar.setValue(70)

    sql = """SELECT f.flnam, AsText(f.geom) AS punkte FROM flaechen AS f
    JOIN
        gebiete AS g
    ON 
        Intersects(f.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY f.flnam"""

    cursl.execute(sql)

    datave = ""  # Datenzeilen

    for b in cursl.fetchall():

        # In allen Namen Leerzeichen durch '_' ersetzen
        nam = b[0].replace(" ", "_")

        # In allen Feldern None durch NULL ersetzen
        c = b[1].replace("MULTIPOLYGON(((", "").replace(")))", "").split(",")
        for k in c:
            x, y = k.split()
            datave += "{:<16s} {:<18.3f} {:<18.3f}\n".format(nam, float(x), float(y))

    swdaten = swdaten.replace("{Polygons}\n", datave)

    # --------------------------------------------------------------------------------------------------
    # [RAINGAGES]
    # [SYMBOLS]

    # fortschritt('Regenmesser...',0.92)
    progress_bar.setValue(80)

    sql = """SELECT f.regnr FROM flaechen AS f
    JOIN
        gebiete AS g
    ON 
        Intersects(f.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY f.regnr"""

    cursl.execute(sql)

    datarm = ""  # Datenzeilen
    datasy = ""  # Datenzeilen

    for c in cursl.fetchall():

        datarm += (
            "{:<16d} INTENSITY 1:00     1.0      TIMESERIES TS1             \n".format(
                c[0]
            )
        )
        datasy += "{:<16d} 9999.999           9999.999          \n".format(c[0])

    swdaten = swdaten.replace("{RAINGAGES}\n", datarm)
    swdaten = swdaten.replace("{SYMBOLS}\n", datasy)

    # --------------------------------------------------------------------------------------------------
    # [MAP]

    # fortschritt('Kartenausdehnung...',0.95)
    progress_bar.setValue(90)

    sql = """SELECT
        min(X(geop)) AS xmin, min(y(geop)) AS ymin, max(X(geop)) AS xmax, max(y(geop)) AS ymax
    FROM
        schaechte AS s
    JOIN
        gebiete AS g
    ON 
        Intersects(s.geop,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')"""
    cursl.execute(sql)

    # (entfaellt)

    b = cursl.fetchone()

    # In allen Feldern None durch NULL ersetzen
    c = ["NULL" if el is None else el for el in b]

    data = "{:<10.3f} {:<10.3f} {:<10.3f} {:<10.3f}\n".format(
        math.floor((c[0] - 200.0) / 200.0) * 200.0,
        math.floor((c[1] - 200.0) / 200.0) * 200.0,
        math.ceil((c[2] + 200.0) / 200.0) * 200.0,
        math.ceil((c[3] + 200.0) / 200.0) * 200.0,
    )

    swdaten = swdaten.replace("{MAP}\n", data)

    # --------------------------------------------------------------------------------------------------
    # [CURVES]   - wurde in mehreren Abschnitten zusammengestellt, deshalb erst jetzt schreiben

    swdaten = swdaten.replace("{CURVES}\n", datacu)

    # --------------------------------------------------------------------------------------------------
    # Schreiben der inp-Datei

    with open(ergfileSwmm, "w") as swvorlage:
        swvorlage.write(swdaten)

    consl.close()

    # fortschritt('Ende...',1)
    progress_bar.setValue(100)
