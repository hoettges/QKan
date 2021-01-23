# -*- coding: utf-8 -*-

"""
  Import from HE

  Aus einer Hystem-Extran-Datenbank im Firebird-Format werden Kanaldaten
  in die QKan-Datenbank importiert. Dazu wird eine Projektdatei erstellt,
  die verschiedene thematische Layer erzeugt, u.a. eine Klassifizierung
  der Schachttypen.
"""


__author__ = "Joerg Hoettges"
__date__ = "September 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"

import logging
import os
import xml.etree.ElementTree as ElementTree
from typing import Tuple, cast

from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsMessageLog, QgsProject
from qgis.utils import pluginDirectory
from qkan import QKAN_FORMS, QKAN_TABLES, QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import eval_node_types, fehlermeldung, fzahl

logger = logging.getLogger("QKan.dynaporter.import_from_dyna")


# Hilfsfunktionen --------------------------------------------------------------------------
class Rahmen:
    """Koordinatengrenzen in 2D"""

    def __init__(self) -> None:
        self.xmin = self.ymin = self.xmax = self.ymax = 0.0

    def reset(self, x: float, y: float) -> None:
        self.xmin = self.xmax = x
        self.ymin = self.ymax = y

    def p(self, x: float, y: float) -> None:
        self.xmin = min(self.xmin, x)
        self.ymin = min(self.ymin, y)
        self.xmax = max(self.xmax, x)
        self.ymax = max(self.ymax, y)

    def line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.xmin = min(self.xmin, x1, x2)
        self.ymin = min(self.ymin, y1, y2)
        self.xmax = max(self.xmax, x1, x2)
        self.ymax = max(self.ymax, y1, y2)

    def ppr(self, x1: float, y1: float, x2: float, y2: float, r: float) -> None:
        d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if abs(r - d / 2) < (r + d / 2) / 10000000.0:
            h = 0.0
        elif r > d / 2:
            h = (r ** 2 - d ** 2 / 4.0) ** 0.5
        else:
            return None
        xm = (x1 + x2) / 2.0 - h / d * (y2 - y1)
        ym = (y1 + y2) / 2.0 + h / d * (x2 - x1)

        # Anpassen der Koordinatengrenzen

        self.xmin = min(self.xmin, x1, x2)
        self.ymin = min(self.ymin, y1, y2)
        self.xmax = max(self.xmax, x1, x2)
        self.ymax = max(self.ymax, y1, y2)

        # Berücksichtung des äußeren Punktes der verbindenden Bogens

        xob, yob = xm, ym + r
        xli, yli = xm - r, ym
        xun, yun = xm, ym - r
        xre, yre = xm + r, ym

        # Nordpol
        if (xob - x1) * (y2 - yob) > (yob - y1) * (x2 - xob):
            self.ymax = max(self.ymax, yob)

        # Westen
        if (xli - x1) * (y2 - yli) > (yli - y1) * (x2 - xli):
            self.xmin = min(self.xmin, xli)

        # Süden
        if (xun - x1) * (y2 - yun) > (yun - y1) * (x2 - xun):
            self.ymin = min(self.ymin, yun)

        # Osten
        if (xre - x1) * (y2 - yre) > (yre - y1) * (x2 - xre):
            self.xmax = max(self.xmax, xre)

        # Berücksichtung des äußeren Punktes der verbindenden Bogens

        # if min(y1, y2) < ym < max(y1, y2):
        #     # Bogen geht linken oder rechten Äquator
        #     if x1 + x2 < 0:
        #         self.xmin = min(self.xmin, xm + r)          # Bogen geht über rechten Äquator
        #     else:
        #         self.xmax = max(self.xmax, xm - r)          # Bogen geht über linken Äquator
        #
        # if min(y1, y2) < ym < max(y1, y2):
        #     # Bogen geht Nord- oder Südpol
        #     if y1 + y2 > 0:
        #         self.ymax = max(self.ymax, ym + r)                    # Bogen geht über Nordpol
        #     else:
        #         self.ymin = min(self.ymin, ym - r)                    # Bogen geht über Südpol

    def ppp(
        self, x1: float, y1: float, x0: float, y0: float, x2: float, y2: float
    ) -> None:
        """Kreisbogen wird durch 3 Punkte definiert"""
        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        dist = (
            ((x1 - x0) ** 2 + (y1 - y0) ** 2)
            + ((x0 - x2) ** 2 + (y0 - y2) ** 2)
            + ((x2 - x1) ** 2 + (y2 - y1) ** 2)
        ) / 3.0

        if abs(det) > dist / 10000.0:
            # Determinante darf nicht sehr klein sein.
            xm = (
                (
                    ((x1 - x0) * (x1 + x0) + (y1 - y0) * (y1 + y0)) * (y2 - y0)
                    - ((x2 - x0) * (x2 + x0) + (y2 - y0) * (y2 + y0)) * (y1 - y0)
                )
                / 2.0
                / det
            )
            ym = (
                (
                    ((x2 - x0) * (x2 + x0) + (y2 - y0) * (y2 + y0)) * (x1 - x0)
                    - ((x1 - x0) * (x1 + x0) + (y1 - y0) * (y1 + y0)) * (x2 - x0)
                )
                / 2.0
                / det
            )
            r = ((xm - x1) ** 2 + (ym - y1) ** 2) ** 0.5
        else:
            return None

        # Anpassen der Koordinatengrenzen

        self.xmin = min(self.xmin, x1, x2)
        self.ymin = min(self.ymin, y1, y2)
        self.xmax = max(self.xmax, x1, x2)
        self.ymax = max(self.ymax, y1, y2)

        # Berücksichtung des äußeren Punktes der verbindenden Bogens

        xob, yob = xm, ym + r
        xli, yli = xm - r, ym
        xun, yun = xm, ym - r
        xre, yre = xm + r, ym

        # Nordpol
        if (xob - x1) * (y0 - yob) > (yob - y1) * (x0 - xob) or (xob - x0) * (
            y2 - yob
        ) > (yob - y0) * (x2 - xob):
            self.ymax = max(self.ymax, yob)

        # Westen
        if (xli - x1) * (y0 - yli) > (yli - y1) * (x0 - xli) or (xli - x0) * (
            y2 - yli
        ) > (yli - y0) * (x2 - xli):
            self.xmin = min(self.xmin, xli)

        # Süden
        if (xun - x1) * (y0 - yun) > (yun - y1) * (x0 - xun) or (xun - x0) * (
            y2 - yun
        ) > (yun - y0) * (x2 - xun):
            self.ymin = min(self.ymin, yun)

        # Osten
        if (xre - x1) * (y0 - yre) > (yre - y1) * (x0 - xre) or (xre - x0) * (
            y2 - yre
        ) > (yre - y0) * (x2 - xre):
            self.xmax = max(self.xmax, xre)


# ------------------------------------------------------------------------------
# Hauptprogramm


def import_kanaldaten(
    dynafile: str, database_qkan: str, projectfile: str, epsg: int = 25832
) -> bool:

    """Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    :param dynafile:        Datei mit den DYNA-Daten (*.EIN)
    :param database_qkan:   Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param projectfile:     Pfad der Projektdatei zum Schreiben. Die Vorlage "projekt.qgs" aus dem
                            template-Verzeichnis wird auf das in diesem Modul zu importierende Projekt
                            angepasst und unter dem angegebenen Pfad gespeichert.
    :param epsg:            EPSG-Nummer
    """

    # Datenbankobjekt der QKan-Datenbank zum Schreiben
    db_qkan = DBConnection(dbname=database_qkan, epsg=epsg)

    if not db_qkan.connected:
        fehlermeldung(
            "Fehler in import_from_dyna:\n",
            "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                database_qkan
            ),
        )
        return False

    # # Referenztabellen laden.

    # # Profile. Attribut [profilnam] enthält die Bezeichnung des Benutzers. Dies kann auch ein Kürzel sein.
    # if not dbQK.sql('SELECT kp_key, profilnam FROM profile', 'importkanaldaten_dyna (3)'):
    # return None
    # daten = dbQK.fetchall()
    # ref_profil = {}
    # for el in daten:
    # ref_profil[el[0]] = el[1]

    # # Entwässerungssystem. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
    # if not dbQK.sql('SELECT kp_nr, bezeichnung FROM entwaesserungsarten', 'importkanaldaten_dyna (4)'):
    # return None
    # daten = dbQK.fetchall()
    # ref_entwart = {}
    # for el in daten:
    # ref_entwart[el[0]] = el[1]

    # # Simulationsstatus der Haltungen in Kanal++. Attribut [bezeichnung] enthält die Bezeichnung des Benutzers.
    # if not dbQK.sql('SELECT kp_nr, bezeichnung FROM simulationsstatus', 'importkanaldaten_dyna (5)'):
    # return None
    # daten = dbQK.fetchall()
    # ref_simstat = {}
    # for el in daten:
    # ref_simstat[el[0]] = el[1]

    # ref_kb = {}                # Wird aus der dyna-Datei gelesen

    # abflspendelis = {}             # Wird aus der dyna-Datei gelesen

    # ------------------------------------------------------------------------------
    # Vorverarbeitung der überhaupt nicht Datenbank kopatiblen Datenstruktur aus DYNA...

    # Einlesen der DYNA-Datei

    status_einw = False

    sqllist = [
        """CREATE TABLE IF NOT EXISTS dyna12 (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           ID INTEGER,
           IDob INTEGER,
           IDun INTEGER,
           kanalnummer TEXT,
           haltungsnummer TEXT,
           laenge REAL,
           deckeloben REAL,
           sohleoben REAL,
           sohleunten REAL,
           schdmoben REAL,
           material INTEGER,
           profil_key TEXT,
           hoehe REAL,
           ks_key INTEGER,
           flaeche REAL,
           flaecheund TEXT,
           flaechenid TEXT,
           neigkl INTEGER,
           entwart_nr INTEGER,
           simstatus_nr INTEGER,
           haeufigkeit INTEGER,
           typ INTEGER,
           schoben TEXT,
           schunten TEXT,
           xob REAL,
           yob REAL,
           strschluessel TEXT)""",
        "DELETE FROM dyna12",
        """CREATE TABLE IF NOT EXISTS dyna41 (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           schnam TEXT,
           deckelhoehe REAL,
           xkoor REAL,
           ykoor REAL,
           kanalnummer TEXT,
           haltungsnummer TEXT)""",
        "DELETE FROM dyna41",
        """CREATE TABLE IF NOT EXISTS dynarauheit (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           ks_key TEXT,
           ks REAL)""",
        "DELETE FROM dynarauheit",
        """CREATE TABLE IF NOT EXISTS dynaprofil (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           profil_key TEXT,
           profilnam TEXT,
           breite REAL,
           hoehe REAL)""",
        "DELETE FROM dynaprofil",
    ]

    for sql in sqllist:
        if not db_qkan.sql(sql, "importkanaldaten_dyna create tab_typ12"):
            del db_qkan
            return False

    # Initialisierung von Parametern für die nachfolgende Leseschleife

    kanalnummer_vor = (
        ""  # um bei doppelten Haltungsdatensätzen diese nur einmal zu lesen.
    )
    haltungnummer_vor = (
        ""  # Erläuterung: Die doppelten Haltungsdatensätze tauchen in DYNA immer dann
    )
    # auf, wenn mehrere Zuflüsse angegeben werden müssen.

    # Initialisierungen für Profile
    profilmodus = -1  # -1: Nicht im Profilblock, Nächste Zeile ist bei:
    #  0: Bezeichnung des gesamten Profile-Blocks.
    #  1: Profilname, Koordinaten, nächster Block oder Ende
    #  2: Profilnr.
    #  3: Erste Koordinaten des Querprofils

    x1 = y1 = None  # markiert, dass noch kein Profil eingelesen wurde (s. u.)

    try:
        profilnam = ""
        for zeile in open(dynafile, encoding="windows-1252"):
            if zeile[0:2] == "##":
                continue  # Kommentarzeile wird übersprungen

            # Zuerst werden Abschnitte mit besonderen Daten bearbeitet (Profildaten etc.)
            if profilmodus >= 0:
                if profilmodus == 0:
                    # Bezeichnung des gesamten Profile-Blocks. Wird nicht weiter verwendet
                    profilmodus = 1
                    grenzen = Rahmen()  # Grenzen-Objekt erstellen
                    continue
                elif profilmodus == 2:
                    # Profilnr.

                    profil_key = zeile.strip()
                    profilmodus = 3
                    continue
                elif profilmodus == 3:
                    # Erster Profilpunkt
                    werte = (
                        zeile.strip()[1:-2]
                        .replace(")(", ",")
                        .replace(")", ",")
                        .split(",")
                    )
                    if len(werte) != 2:
                        logger.error(
                            "Erste Zeile von Profil {} ist keine Punktkoordinate: {}".format(
                                profilnam, zeile
                            )
                        )
                    xp, yp = [float(w) for w in werte]
                    grenzen.reset(xp, yp)

                    plmodus = "Linie"  # Alternative: 'Kreis'
                    profilmodus = 1
                    x1, y1 = (
                        xp,
                        yp,
                    )  # Punkt als Startpunkt für nächstes Teilstück speichern
                    continue
                elif profilmodus == 1:
                    # weitere Profilpunkte, nächstes Profil oder Ende der Profile
                    if zeile[0:1] == "(":
                        # profilmodus == 1, weitere Profilpunkte
                        werte = (
                            zeile.strip()[1:-2]
                            .replace(")(", ",")
                            .replace(")", ",")
                            .split(",")
                        )
                        nargs = len(werte)

                        if nargs == 2:
                            # Geradensegment
                            xp, yp = cast(
                                Tuple[float, float], [float(w) for w in werte]
                            )
                            grenzen.line(
                                cast(float, x1),
                                cast(float, y1),
                                xp,
                                yp,
                            )  # Grenzen aktualisieren
                            x1, y1 = (
                                xp,
                                yp,
                            )  # Punkt als Startpunkt für nächstes Teilstück speichern

                        elif nargs == 3:
                            # Polyliniensegment mit Radius und Endpunkt
                            xp, yp, radius = cast(
                                Tuple[float, float, float], [float(w) for w in werte]
                            )
                            grenzen.line(
                                cast(float, x1), cast(float, y1), xp, yp
                            )  # Grenzen mit Stützstellen aktualisieren
                            grenzen.ppr(
                                cast(float, x1),
                                cast(float, y1),
                                xp,
                                yp,
                                radius,
                            )  # Grenzen für äußeren Punkt des Bogens aktualisieren
                            x1, y1 = (
                                xp,
                                yp,
                            )  # Punkt als Startpunkt für nächstes Teilstück speichern

                        elif nargs == 4:
                            # Polyliniensegment mit Punkt auf Bogen und Endpunkt
                            xm, ym, xp, yp = cast(
                                Tuple[float, float, float, float],
                                [float(w) for w in werte],
                            )
                            grenzen.line(
                                cast(float, x1), cast(float, y1), xm, ym
                            )  # Grenzen mit Stützstellen aktualisieren
                            grenzen.p(xp, yp)  # Grenzen mit Stützstellen aktualisieren
                            grenzen.ppp(
                                cast(float, x1), cast(float, y1), xm, ym, xp, yp
                            )  # Grenzen für äußere Punkte des Bogens aktualisieren
                            x1, y1 = (
                                xp,
                                yp,
                            )  # Punkt als Startpunkt für nächstes Teilstück speichern

                        continue
                    else:
                        # Nächstes Profil oder Ende Querprofile (=Ende des aktuellen Profils)

                        # Beschriftung des Profils. Grund: Berechnung von Breite und Höhe ist erst nach
                        # Einlesen aller Profilzeilen möglich.

                        # Erst wenn das erste Profil eingelesen wurde
                        if x1 is not None:
                            # Höhe zu Breite-Verhältnis berechnen
                            breite = (grenzen.xmax - grenzen.xmin) / 1000.0
                            hoehe = (grenzen.ymax - grenzen.ymin) / 1000.0
                            sql = """INSERT INTO dynaprofil (profil_key, profilnam, breite, hoehe)
                                        VALUES (?, ?, ?, ?)"""
                            logger.debug("sql = {}".format(sql))
                            if not db_qkan.sql(
                                sql,
                                "importkanaldaten_kp (1)",
                                parameters=(profil_key, profilnam, breite, hoehe),
                            ):
                                del db_qkan
                                return False

                        if zeile[0:2] != "++":
                            # Profilname
                            profilnam = zeile.strip()
                            profilmodus = 2
                            continue
                        else:
                            # Ende Block Querprofile (es sind mehrere möglich!)
                            profilmodus = -1
                            x1 = y1 = None

            # Optionen und Daten
            if zeile[0:6] == "++QUER":
                profilmodus = 0

            elif zeile[0:6] == "++KANA" and not status_einw:
                status_einw = "EINW" in zeile

            elif zeile[0:2] == "05":
                ks_key = zeile[3:4].strip()
                abflspende = float("0" + zeile[10:20].strip())
                ks = float("0" + zeile[20:30].strip())

                if not db_qkan.sql(
                    "INSERT INTO dynarauheit (ks_key, ks) Values (?, ?)",
                    "importkanaldaten_kp (2)",
                    parameters=(ks_key, ks),
                ):
                    del db_qkan
                    return False

            elif zeile[0:2] == "12":

                n = 1
                kanalnummer = zeile[6:14].lstrip("0 ").replace(" ", "0")
                n = 3  # wegen der merkwürdigen DYNA-Logik für Kanalnamen
                haltungsnummer = str(int("0" + zeile[14:17].strip()))
                n = 4
                if (kanalnummer, haltungsnummer) != (
                    kanalnummer_vor,
                    haltungnummer_vor,
                ):
                    kanalnummer_vor, haltungnummer_vor = (
                        kanalnummer,
                        haltungsnummer,
                    )  # doppelte Haltungen werden übersprungen, weil Flächen-
                    # daten z.Zt. nicht eingelesen werden.
                    try:
                        strschluessel = zeile[2:6].strip()
                        n = 2
                        laenge = fzahl(zeile[17:24], 2)
                        n = 5
                        deckeloben = fzahl(zeile[24:31], 3)
                        n = 6
                        sohleoben = fzahl(zeile[31:38], 3)
                        n = 7
                        sohleunten = fzahl(zeile[38:45], 3)
                        n = 8
                        material = zeile[45:46]
                        n = 9
                        profil_key = zeile[46:48].strip()
                        n = 10
                        hoehe = fzahl(zeile[48:52], 0) / 1000.0
                        n = 11
                        ks_key = zeile[52:53].strip()
                        n = 12
                        flaeche = fzahl(zeile[71:76], 2) * 10000.0
                        n = 20
                        flaecheund = round(fzahl(zeile[53:55]) / 100.0 * flaeche, 1)
                        n = 13
                        qgewerbeind = zeile[55:56].strip()
                        n = 14
                        qfremdind = zeile[56:57].strip()
                        n = 15
                        zuflussid = zeile[57:58]
                        n = 16
                        qzu = fzahl(zeile[58:63], 1)
                        n = 17
                        if status_einw:
                            ew = fzahl(zeile[63:66])
                            n = 18
                        else:
                            ew = fzahl(zeile[63:66]) * flaeche / 10000.0
                        flaechenid = zeile[66:71]
                        n = 19
                        neigkl = int("0" + zeile[76:77].strip())
                        n = 21
                        entwart_nr = int("0" + zeile[77:78].strip())
                        n = 22
                        simstatus_nr = int("0" + zeile[78:79].strip())
                        n = 23
                        haeufigkeit = int("0" + zeile[80:81].strip())
                        n = 24
                        schoben = zeile[81:93].strip()
                        n = 25
                        schunten = zeile[94:106].strip()
                        n = 26
                        xob = fzahl(zeile[106:120])
                        n = 27
                        yob = fzahl(zeile[120:134])
                        n = 28
                        schdmoben = fzahl(zeile[180:187])
                    except BaseException as err:
                        fehlermeldung(
                            "Programmfehler", "import_from_dyna.importKanaldaten (1)"
                        )
                        logger.error(
                            "12er: Wert Nr. {} - {}\nZeile: {}".format(n, err, zeile)
                        )
                        del db_qkan
                        return False

                    try:
                        sql = """
                        INSERT INTO dyna12
                        (kanalnummer, haltungsnummer, schoben, schunten,
                        xob, yob, laenge, deckeloben, sohleoben, sohleunten,
                        material, profil_key, hoehe, ks_key, flaeche, flaecheund, neigkl,
                        entwart_nr, simstatus_nr, 
                        flaechenid, strschluessel, haeufigkeit, schdmoben)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """

                    except BaseException as err:
                        logger.error("12er: {}\n{}".format(err, zeile))
                    else:
                        if not db_qkan.sql(
                            sql,
                            "importkanaldaten_dyna import typ12",
                            parameters=(
                                kanalnummer,
                                haltungsnummer,
                                schoben,
                                schunten,
                                xob,
                                yob,
                                laenge,
                                deckeloben,
                                sohleoben,
                                sohleunten,
                                material,
                                profil_key,
                                hoehe,
                                ks_key,
                                flaeche,
                                flaecheund,
                                neigkl,
                                entwart_nr,
                                simstatus_nr,
                                flaechenid,
                                strschluessel,
                                haeufigkeit,
                                schdmoben,
                            ),
                        ):
                            del db_qkan
                            return False

            elif zeile[0:2] == "41":
                try:
                    n = 1
                    kanalnummer = zeile[6:14].lstrip("0 ").replace(" ", "0")
                    n = 2  # wegen der eigenwilligen DYNA-Logik für Kanalnamen;
                    haltungsnummer = zeile[14:17]
                    n = 3
                    deckelhoehe = fzahl(zeile[24:31], 3)
                    n = 4
                    xkoor = fzahl(zeile[31:45], 0)
                    n = 5
                    ykoor = fzahl(zeile[45:59], 0)
                    n = 6
                    schnam = zeile[59:71].strip()
                    n = 7
                except BaseException as err:
                    logger.error(
                        "16er: Wert Nr. {} - {}\nZeile: {}".format(n, err, zeile)
                    )
                    return False

                sql = """
                INSERT INTO dyna41
                (schnam, deckelhoehe, xkoor, ykoor, kanalnummer, haltungsnummer)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                if not db_qkan.sql(
                    sql,
                    "importkanaldaten_dyna typ16",
                    parameters=(
                        schnam,
                        deckelhoehe,
                        xkoor,
                        ykoor,
                        kanalnummer,
                        haltungsnummer,
                    ),
                ):
                    del db_qkan
                    return False
    except BaseException as err:
        fehlermeldung(
            "Dateifehler",
            "Die Datei {} ist offensichtlich keine ANSI-Datei! ".format(dynafile),
        )
        logger.error("12er: Wert Nr. {} - {}\nZeile: {}".format(n, err, zeile))
        del db_qkan
        return False

    # ------------------------------------------------------------------------------
    # Profile aus DYNA-Datei in Tabelle profile ergänzen
    # 1. Bei Namenskonflikten mit bereits gespeicherten Profilen wird die kp_key auf NULL gesetzt

    sql = """UPDATE profile 
        SET kp_key = NULL
        WHERE profilnam IN 
        (   SELECT profilnam
            FROM dynaprofil
            WHERE profile.profilnam = dynaprofil.profilnam and profile.kp_key <> dynaprofil.profil_key)"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna profile-1"):
        del db_qkan
        return False

    # 2. Neue Profile aus DYNA hinzufügen

    sql = """INSERT INTO profile 
        (profilnam, kp_key)
        SELECT profilnam, profil_key
        FROM dynaprofil
        WHERE profil_key not in 
        (   SELECT kp_key 
            FROM profile WHERE kp_key IS NOT NULL)"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna profile-2"):
        del db_qkan
        return False

    # ------------------------------------------------------------------------------
    # Schachtdaten

    # Tabelle in QKan-Datenbank leeren
    # if check_tabinit:
    # if not dbQK.sql('DELETE FROM schaechte', 'importkanaldaten_dyna (10)'):
    # return None

    # Daten aus temporären DYNA-Tabellen abfragen
    sql = """
        SELECT 
            dyna12.schoben as schnam,
            dyna12.xob as xsch, 
            dyna12.yob as ysch, 
            dyna12.sohleoben as sohlhoehe, 
            dyna12.deckeloben as deckelhoehe, 
            1000 as durchm, 
            0 as druckdicht, 
            entwaesserungsarten.bezeichnung as entwart, 
            simulationsstatus.bezeichnung AS simstatus, 
            'Importiert mit QKan' AS kommentar
        FROM dyna12
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN entwaesserungsarten
        ON dyna12.entwart_nr = entwaesserungsarten.kp_nr
        GROUP BY dyna12.schoben"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna (11)"):
        del db_qkan
        return False
    daten = db_qkan.fetchall()

    # Schachtdaten aufbereiten und in die QKan-DB schreiben

    for attr in daten:
        (
            schnam,
            xsch,
            ysch,
            sohlhoehe,
            deckelhoehe,
            durchm,
            druckdicht,
            entwart,
            simstatus,
            kommentar,
        ) = ["NULL" if el is None else el for el in attr]

        # schnam = schnam_ansi.decode('iso-8859-1')

        # # Entwasserungsarten
        # if entwart_kp in ref_entwart:
        # entwart = ref_entwart[entwart_kp]
        # else:
        # # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergänzen
        # sql = "INSERT INTO entwaesserungsarten (bezeichnung, kp_nr) Values ('({0:})', {0:d})".format(entwart_kp)
        # entwart = u'({:})'.format(entwart_kp)
        # if not dbQK.sql(sql, 'importkanaldaten_dyna (11)'):
        # return None

        # # Simstatus-Nr aus EIN-Datei ersetzten
        # if simstat_kp in ref_simstat:
        # simstatus = ref_simstat[simstat_kp]
        # else:
        # # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
        # simstatus = u'({}_kp)'.format(simstat_kp)
        # sql = "INSERT INTO simulationsstatus (bezeichnung, kp_nr) Values ('{simstatus}', {kp_nr})".format( \
        # simstatus=simstatus, kp_nr=simstat_kp)
        # ref_simstat[simstat_kp] = simstatus
        # if not dbQK.sql(sql, 'importkanaldaten_dyna (12)'):
        # return None

        # Geo-Objekte erzeugen

        # if QKan.config.database.type == enums.QKanDBChoice.SPATIALITE:
        #     geop = f"MakePoint({xsch},{ysch},{epsg})"
        #     du = 1.0 if durchm == "NULL" else durchm / 1000.0
        #     geom = f"CastToMultiPolygon(MakePolygon(MakeCircle({xsch},{ysch},{du},{epsg})))"
        # elif QKan.config.database.type == enums.QKanDBChoice.POSTGIS:
        #     geop = f"ST_SetSRID(ST_MakePoint({xsch},{ysch}),{epsg})"
        # else:
        #     fehlermeldung(
        #         "Programmfehler!",
        #         "Datenbanktyp ist fehlerhaft {}!\nAbbruch!".format(
        #             QKan.config.database.type
        #         ),
        #     )

        # Datensatz in die QKan-DB schreiben

        try:
            sql = f"""
                INSERT INTO schaechte_data (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                        schachttyp, simstatus, kommentar)
                VALUES (?, ?, ?, ?, ?, ?/1000, ?, ?, 'Schacht', ?, ?)"""
            if not db_qkan.sql(
                sql,
                "importkanaldaten_dyna (13)",
                parameters=(
                    schnam,
                    xsch,
                    ysch,
                    sohlhoehe,
                    deckelhoehe,
                    durchm,
                    druckdicht,
                    entwart,
                    simstatus,
                    kommentar,
                ),
            ):
                del db_qkan
                return False
        except BaseException as e:
            fehlermeldung("SQL-Fehler", str(e))
            fehlermeldung(
                "Fehler in QKan_Import_from_KP",
                "\nSchächte: in sql: \n" + sql + "\n\n",
            )

    if not db_qkan.sql(
        "UPDATE schaechte SET (geom, geop) = (geom, geop) ",
        "importkanaldaten_dyna (13a)",
    ):
        del db_qkan
        return False

    db_qkan.commit()

    # ------------------------------------------------------------------------------
    # Auslässe

    # Daten aus temporären DYNA-Tabellen abfragen
    sql = """
        SELECT
            dyna41.schnam as schnam,
            dyna41.xkoor as xsch, 
            dyna41.ykoor as ysch, 
            dyna12.sohleunten as sohlhoehe, 
            dyna41.deckelhoehe as deckelhoehe, 
            1000 as durchm, 
            0 as druckdicht, 
            entwaesserungsarten.bezeichnung as entwart, 
            simulationsstatus.bezeichnung AS simstat, 
            'Importiert mit QKan' AS kommentar
        FROM dyna41
        LEFT JOIN dyna12
        ON dyna41.schnam = dyna12.schunten
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN entwaesserungsarten
        ON dyna12.entwart_nr = entwaesserungsarten.kp_nr
        GROUP BY dyna41.schnam"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna (14)"):
        del db_qkan
        return False
    daten = db_qkan.fetchall()

    # Auslassdaten aufbereiten und in die QKan-DB schreiben

    for attr in daten:
        (
            schnam,
            xsch,
            ysch,
            sohlhoehe,
            deckelhoehe,
            durchm,
            druckdicht,
            entwart,
            simstat,
            kommentar,
        ) = ["NULL" if el is None else el for el in attr]

        # schnam = schnam_ansi.decode('iso-8859-1')

        # # Entwasserungsarten
        # if entwart_kp in ref_entwart:
        # entwart = ref_entwart[entwart_kp]
        # else:
        # # Noch nicht in Tabelle [entwaesserungsarten] enthalten, also ergänzen
        # sql = "INSERT INTO entwaesserungsarten (bezeichnung, kp_nr) Values ('({0:})', {0:d})".format(entwart_kp)
        # entwart = u'({:})'.format(entwart_kp)
        # if not dbQK.sql(sql, 'importkanaldaten_dyna (14)'):
        # return None

        # # Simstatus-Nr aus EIN-Datei ersetzten
        # if simstat_kp in ref_simstat:
        # simstatus = ref_simstat[simstat_kp]
        # else:
        # # Noch nicht in Tabelle [simulationsstatus] enthalten, also ergqenzen
        # simstatus = u'({}_kp)'.format(simstat_kp)
        # sql = "INSERT INTO simulationsstatus (bezeichnung, kp_nr) Values ('{simstatus}', {kp_nr})".format( \
        # simstatus=simstatus, kp_nr=simstat_kp)
        # ref_simstat[simstat_kp] = simstatus
        # if not dbQK.sql(sql, 'importkanaldaten_dyna (15)'):
        # return None

        # Geo-Objekte erzeugen

        # if QKan.config.database.type == enums.QKanDBChoice.SPATIALITE:
        #     geop = f"MakePoint({xsch},{ysch},{epsg})"
        #     du = 1.0 if durchm == "NULL" else durchm / 1000.0
        #     geom = f"CastToMultiPolygon(MakePolygon(MakeCircle({xsch},{ysch},{du},{epsg})))"
        # elif QKan.config.database.type == enums.QKanDBChoice.POSTGIS:
        #     geop = f"ST_SetSRID(ST_MakePoint({xsch},{ysch}),{epsg})"
        # else:
        #     fehlermeldung(
        #         "Programmfehler!",
        #         "Datenbanktyp ist fehlerhaft {}!\nAbbruch!".format(dbtyp),
        #     )

        # Datensatz in die QKan-DB schreiben

        try:
            sql = f"""
                INSERT INTO schaechte_data (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                        schachttyp, simstatus, kommentar)
                VALUES (?, ?, ?, ?, ?, ?/1000, ?, ?, 'Auslass', ?, ?)
                """
            if not db_qkan.sql(
                sql,
                "importkanaldaten_dyna (16)",
                parameters=(
                    schnam,
                    xsch,
                    ysch,
                    sohlhoehe,
                    deckelhoehe,
                    durchm,
                    druckdicht,
                    entwart,
                    simstat,
                    kommentar,
                ),
            ):
                del db_qkan
                return False
        except BaseException as e:
            fehlermeldung("SQL-Fehler", str(e))
            fehlermeldung(
                "Fehler in QKan_Import_from_KP",
                "\nSchächte: in sql: \n" + sql + "\n\n",
            )

    if not db_qkan.sql(
        "UPDATE schaechte SET (geom, geop) = (geom, geop) ",
        "importkanaldaten_dyna (16a)",
    ):
        del db_qkan
        return False

    db_qkan.commit()

    # ------------------------------------------------------------------------------
    # Haltungsdaten

    # Tabelle in QKan-Datenbank leeren
    # if check_tabinit:
    # sql = """DELETE FROM haltungen"""
    # if not dbQK.sql(sql, 'importkanaldaten_dyna (6)'):
    # return None

    # Daten aUS temporären DYNA-Tabellen abfragen
    sql = """
        SELECT 
            printf('%s-%s', dyna12.kanalnummer, dyna12.haltungsnummer) AS haltnam, 
            dyna12.schoben AS schoben, 
            dyna12.schunten AS schunten, 
            dyna12.hoehe AS hoehe, 
            dyna12.hoehe*dynaprofil.breite/dynaprofil.hoehe AS breite, 
            dyna12.laenge AS laenge, 
            dyna12.sohleoben AS sohleoben, 
            dyna12.sohleunten AS sohleunten, 
            dyna12.deckeloben AS deckeloben, 
            coalesce(dy12un.deckeloben, dyna41.deckelhoehe) as deckelunten, 
            NULL as teilgebiet, 
            dynaprofil.profilnam as profilnam, 
            entwaesserungsarten.bezeichnung as entwart, 
            dynarauheit.ks as ks, 
            simulationsstatus.bezeichnung as simstatus, 
            'DYNA-Import' AS kommentar, 
            dyna12.xob as xob, 
            dyna12.yob as yob, 
            coalesce(dy12un.xob, dyna41.xkoor) as xun, 
            coalesce(dy12un.yob, dyna41.ykoor) as yun
        FROM dyna12
        LEFT JOIN dyna12 AS dy12un
        ON dyna12.schunten = dy12un.schoben
        LEFT JOIN dyna41
        ON dyna12.schunten = dyna41.schnam
        LEFT JOIN dynarauheit
        ON dyna12.ks_key = dynarauheit.ks_key
        LEFT JOIN dynaprofil
        ON dyna12.profil_key = dynaprofil.profil_key
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN entwaesserungsarten
        ON dyna12.entwart_nr = entwaesserungsarten.kp_nr
        GROUP BY dyna12.kanalnummer, dyna12.haltungsnummer"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna (7)"):
        del db_qkan
        return False
    daten = db_qkan.fetchall()

    # Haltungsdaten in die QKan-DB schreiben

    for attr in daten:
        (
            haltnam,
            schoben,
            schunten,
            hoehe,
            breite,
            laenge,
            sohleoben,
            sohleunten,
            deckeloben,
            deckelunten,
            teilgebiet,
            profilnam,
            entwart,
            ks,
            simstatus,
            kommentar,
            xob,
            yob,
            xun,
            yun,
        ) = ["NULL" if el is None else el for el in attr]

        # (haltnam, schoben, schunten) = \
        # [tt.decode('iso-8859-1') for tt in (haltnam_ansi, schoben_ansi, schunten_ansi)]

        # Geo-Objekt erzeugen
        # if QKan.config.database.type == enums.QKanDBChoice.SPATIALITE:
        #     geom = (
        #         f"MakeLine(MakePoint({xob},{yob},{epsg}),MakePoint({xun},{yun},{epsg}))"
        #     )
        # elif QKan.config.database.type == enums.QKanDBChoice.POSTGIS:
        #     geom = f"ST_MakeLine(ST_SetSRID(ST_MakePoint({xob},{yob}),{epsg}),ST_SetSRID(ST_MakePoint({xun},{yun}),{epsg}))"
        # else:
        #     fehlermeldung(
        #         "Programmfehler!",
        #         "Datenbanktyp ist fehlerhaft {}!\nAbbruch!".format(
        #             QKan.config.database.type
        #         ),
        #     )

        # Datensatz aufbereiten in die QKan-DB schreiben

        if not db_qkan.sql(
            """
            INSERT INTO haltungen_data 
            (haltnam, schoben, schunten, 
            hoehe, breite, laenge, sohleoben, sohleunten, 
            deckeloben, deckelunten, teilgebiet, profilnam, entwart, ks, simstatus, kommentar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            "importkanaldaten_dyna (9a)",
            parameters=(
                haltnam,
                schoben,
                schunten,
                hoehe,
                breite,
                laenge,
                sohleoben,
                sohleunten,
                deckeloben,
                deckelunten,
                teilgebiet,
                profilnam,
                entwart,
                ks,
                simstatus,
                kommentar,
            ),
        ):
            del db_qkan
            return False

    if not db_qkan.sql(
        "UPDATE haltungen SET geom = geom", "importkanaldaten_dyna (9a)"
    ):
        del db_qkan
        return False

    db_qkan.commit()

    # --------------------------------------------------------------------------
    # Schachttypen auswerten
    eval_node_types(db_qkan)  # in qkan.database.qkan_utils

    # --------------------------------------------------------------------------
    # Zoom-Bereich für die Projektdatei vorbereiten
    sql = """SELECT min(x(geop)) AS xmin, 
                    max(x(geop)) AS xmax, 
                    min(y(geop)) AS ymin, 
                    max(y(geop)) AS ymax
             FROM schaechte"""
    try:
        if not db_qkan.sql(sql, "importkanaldaten_dyna (17)"):
            del db_qkan
            return False
    except BaseException as e:
        fehlermeldung("SQL-Fehler", str(e))
        fehlermeldung(
            "Fehler in QKan_Import_from_KP", "\nFehler in sql_zoom: \n" + sql + "\n\n"
        )

    try:
        zoom = db_qkan.fetchone()
    except BaseException as e:
        fehlermeldung("SQL-Fehler", str(e))
        fehlermeldung(
            "Fehler in QKan_Import_from_KP",
            "\nFehler in sql_zoom; daten= " + str(daten) + "\n",
        )
        zoom = [0.0, 100.0, 0.0, 100.0]

    # --------------------------------------------------------------------------
    # Projektionssystem für die Projektdatei vorbereiten
    sql = """SELECT srid
            FROM geom_cols_ref_sys
            WHERE Lower(f_table_name) = Lower('schaechte')
            AND Lower(f_geometry_column) = Lower('geom')"""
    if not db_qkan.sql(sql, "importkanaldaten_dyna (37)"):
        del db_qkan
        return False

    srid = db_qkan.fetchone()[0]
    try:
        crs = QgsCoordinateReferenceSystem(srid, QgsCoordinateReferenceSystem.EpsgCrsId)
        srsid = crs.srsid()
        proj4text = crs.toProj4()
        description = crs.description()
        projectionacronym = crs.projectionAcronym()
        if "ellipsoidAcronym" in dir(crs):
            ellipsoidacronym = crs.ellipsoidAcronym()
        else:
            ellipsoidacronym = None
    except BaseException as e:
        srid, srsid, proj4text, description, projectionacronym, ellipsoidacronym = (
            "dummy",
            "dummy",
            "dummy",
            "dummy",
            "dummy",
            "dummy",
        )

        fehlermeldung('\nFehler in "daten"', str(e))
        fehlermeldung(
            "Fehler in QKan_Import_from_KP",
            "\nFehler bei der Ermittlung der srid: \n" + str(daten),
        )

    # --------------------------------------------------------------------------
    # Datenbankverbindungen schliessen

    del db_qkan

    # --------------------------------------------------------------------------
    # Projektdatei schreiben, falls ausgewählt

    if projectfile is not None and projectfile != "":
        templatepath = os.path.join(pluginDirectory("qkan"), "templates")
        projecttemplate = os.path.join(templatepath, "projekt.qgs")
        projectpath = os.path.dirname(projectfile)
        if os.path.dirname(database_qkan) == projectpath:
            datasource = database_qkan.replace(os.path.dirname(database_qkan), ".")
        else:
            datasource = database_qkan

        # Lesen der Projektdatei ------------------------------------------------------------------
        qgsxml = ElementTree.parse(projecttemplate)
        root = qgsxml.getroot()

        # Projektionssystem anpassen --------------------------------------------------------------

        for tag_maplayer in root.findall(".//projectlayers/maplayer"):
            tag_datasource = tag_maplayer.find("./datasource")
            if not tag_datasource:
                continue

            tex = tag_datasource.text
            if not tex:
                continue

            # Nur QKan-Tabellen bearbeiten
            if tex[tex.index('table="') + 7 :].split('" ')[0] in QKAN_TABLES:

                # <extend> löschen
                for tag_extent in tag_maplayer.findall("./extent"):
                    tag_maplayer.remove(tag_extent)

                for tag_spatialrefsys in tag_maplayer.findall("./srs/spatialrefsys"):
                    tag_spatialrefsys.clear()

                    elem = ElementTree.SubElement(tag_spatialrefsys, "proj4")
                    elem.text = proj4text
                    elem = ElementTree.SubElement(tag_spatialrefsys, "srsid")
                    elem.text = "{}".format(srsid)
                    elem = ElementTree.SubElement(tag_spatialrefsys, "srid")
                    elem.text = "{}".format(srid)
                    elem = ElementTree.SubElement(tag_spatialrefsys, "authid")
                    elem.text = "EPSG: {}".format(srid)
                    elem = ElementTree.SubElement(tag_spatialrefsys, "description")
                    elem.text = description
                    elem = ElementTree.SubElement(
                        tag_spatialrefsys, "projectionacronym"
                    )
                    elem.text = projectionacronym
                    if ellipsoidacronym is not None:
                        elem = ElementTree.SubElement(
                            tag_spatialrefsys, "ellipsoidacronym"
                        )
                        elem.text = ellipsoidacronym

        # Pfad zu Formularen auf plugin-Verzeichnis setzen -----------------------------------------
        formspath = os.path.join(pluginDirectory("qkan"), "forms")
        for tag_maplayer in root.findall(".//projectlayers/maplayer"):
            tag_editform = tag_maplayer.find("./editform")
            if tag_editform and tag_editform.text:
                dateiname = os.path.basename(tag_editform.text)
                if dateiname in QKAN_FORMS:
                    # Nur QKan-Tabellen bearbeiten
                    tag_editform.text = os.path.join(formspath, dateiname)

        # Zoom für Kartenfenster einstellen -------------------------------------------------------
        if len(zoom) == 0 or any([x is None for x in zoom]):
            zoom = [0.0, 100.0, 0.0, 100.0]
        for tag_extent in root.findall(".//mapcanvas/extent"):
            for extent in root.findall(".//mapcanvas/extent"):
                for idx, name in enumerate(["xmin", "ymin", "xmax", "ymax"]):
                    element = extent.find(f"./{name}")
                    if element is not None:
                        element.text = "{:.3f}".format(zoom[idx])

        # Projektionssystem anpassen --------------------------------------------------------------

        for tag_spatialrefsys in root.findall(".//projectCrs/spatialrefsys"):
            tag_spatialrefsys.clear()

            elem = ElementTree.SubElement(tag_spatialrefsys, "proj4")
            elem.text = proj4text
            elem = ElementTree.SubElement(tag_spatialrefsys, "srid")
            elem.text = "{}".format(srid)
            elem = ElementTree.SubElement(tag_spatialrefsys, "authid")
            elem.text = "EPSG: {}".format(srid)
            elem = ElementTree.SubElement(tag_spatialrefsys, "description")
            elem.text = description
            elem = ElementTree.SubElement(tag_spatialrefsys, "projectionacronym")
            elem.text = projectionacronym
            if ellipsoidacronym is not None:
                elem = ElementTree.SubElement(tag_spatialrefsys, "ellipsoidacronym")
                elem.text = ellipsoidacronym

        # Pfad zur QKan-Datenbank anpassen

        for tag_datasource in root.findall(".//projectlayers/maplayer/datasource"):
            text = tag_datasource.text
            if not text:
                continue

            tag_datasource.text = (
                "dbname='" + datasource + "' " + text[text.find("table=") :]
            )

        qgsxml.write(projectfile)  # writing modified project file
        logger.debug("Projektdatei: {}".format(projectfile))
        # logger.debug(u'encoded string: {}'.format(tex))

    # ------------------------------------------------------------------------------
    # Abschluss: Ggfs. Protokoll schreiben und Datenbankverbindungen schliessen

    QKan.instance.iface.mainWindow().statusBar().clearMessage()
    QKan.instance.iface.messageBar().pushMessage(
        "Information", "Datenimport ist fertig!", level=Qgis.Info
    )
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="\nFertig: Datenimport erfolgreich!", level=Qgis.Info
    )

    # Importiertes Projekt laden
    # noinspection PyArgumentList
    project = QgsProject.instance()
    project.read(projectfile)  # read the new project file

    return True
