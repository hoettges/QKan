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
from typing import Tuple, cast, Callable, List
from pathlib import Path

from qgis.core import Qgis, QgsMessageLog, QgsProject
from qgis.utils import pluginDirectory

from qkan import QKan
from qkan.database.dbfunc import DBConnection

from qkan.database.qkan_utils import read_qml, eval_node_types, fehlermeldung, fzahl
from qkan.tools.k_qgsadapt import qgsadapt

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
            h = (r**2 - d**2 / 4.0) ** 0.5
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

    tasks: List[Callable[[DBConnection], bool]] = [
        _recreate_tables,
        lambda x: _read_dynafile(x, dynafile=dynafile),
        _reftables,
        lambda x: _insert_data_from_dyna(x, epsg=epsg),
    ]

    with DBConnection(dbname=database_qkan, epsg=epsg) as db_qkan:
        if not db_qkan.connected:
            fehlermeldung(
                "Fehler in import_from_dyna:\n",
                "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                    database_qkan
                ),
            )
            return False

        # Run DYNA tasks
        for task in tasks:
            if not task(db_qkan):
                return False

        eval_node_types(db_qkan)  # in qkan.database.qkan_utils

        # --------------------------------------------------------------------------
        # Projektdatei schreiben und laden, nur wenn neues Projekt

        if QgsProject.instance().fileName() == "":
            QKan.config.project.template = str(
                Path(pluginDirectory("qkan")) / "templates" / "Projekt.qgs"
            )
            specific_qmls = {
                'specificqmlpath': 'qml/dyna',
                'Haltungen': 'haltungen.qml',
                'Abflussparameter': 'abflussparameter.qml',
            }
            qgsadapt(
                database_qkan,
                db_qkan,
                projectfile,
                QKan.config.project.template,
                epsg,
            )

            # noinspection PyArgumentList
            project = QgsProject.instance()
            project.read(projectfile)  # read the new project file
            project.reloadAllLayers()

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

    return True


def _recreate_tables(db_qkan: DBConnection) -> bool:
    """Create temporary tables necessary to disentangle pipe and node data in dyna file"""
    sqllist = [
        """CREATE TEMP TABLE IF NOT EXISTS dyna12 (
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
        """CREATE TEMP TABLE IF NOT EXISTS dyna41 (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           schnam TEXT,
           deckelhoehe REAL,
           xkoor REAL,
           ykoor REAL,
           kanalnummer TEXT,
           haltungsnummer TEXT)""",
        "DELETE FROM dyna41",
        """CREATE TEMP TABLE IF NOT EXISTS dynarauheit (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           ks_key TEXT,
           ks REAL)""",
        "DELETE FROM dynarauheit",
        """CREATE TEMP TABLE IF NOT EXISTS dynaprofil (
           pk INTEGER PRIMARY KEY AUTOINCREMENT,
           profil_key TEXT,
           profilnam TEXT,
           breite REAL,
           hoehe REAL)""",
        "DELETE FROM dynaprofil",
    ]

    for sql in sqllist:
        if not db_qkan.sql(sql, "importkanaldaten_dyna create tab_typ12"):
            return False

    db_qkan.commit()

    return True


def _read_dynafile(db_qkan: DBConnection, dynafile: str) -> bool:
    """read dyna file to temporary dyna tables"""


    # Initialisierung von Parametern für die nachfolgende Leseschleife

    status_einw = False

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
        with open(dynafile, encoding="windows-1252") as frobj:
            for zeile in frobj:
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
                                    Tuple[float, float, float],
                                    [float(w) for w in werte],
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
                                grenzen.p(
                                    xp, yp
                                )  # Grenzen mit Stützstellen aktualisieren
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
                            laenge = fzahl(zeile[17:24])
                            n = 5
                            deckeloben = fzahl(zeile[24:31])
                            n = 6
                            sohleoben = fzahl(zeile[31:38])
                            n = 7
                            sohleunten = fzahl(zeile[38:45])
                            n = 8
                            material = zeile[45:46]
                            n = 9
                            profil_key = zeile[46:48].strip()
                            n = 10
                            hoehe = fzahl(zeile[48:52]) / 1000.0
                            n = 11
                            ks_key = zeile[52:53].strip()
                            n = 12
                            flaeche = fzahl(zeile[71:76]) * 10000.0
                            n = 20
                            flaecheund = round(fzahl(zeile[53:55]) / 100.0 * flaeche, 1)
                            n = 13
                            qgewerbeind = zeile[55:56].strip()
                            n = 14
                            qfremdind = zeile[56:57].strip()
                            n = 15
                            zuflussid = zeile[57:58]
                            n = 16
                            qzu = fzahl(zeile[58:63])
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
                                "Programmfehler",
                                "import_from_dyna.importKanaldaten (1)",
                            )
                            logger.error(
                                "12er: Wert Nr. {} - {}\nZeile: {}".format(
                                    n, err, zeile
                                )
                            )
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
                                return False

                elif zeile[0:2] == "41":
                    try:
                        n = 1
                        kanalnummer = zeile[6:14].lstrip("0 ").replace(" ", "0")
                        n = 2  # wegen der eigenwilligen DYNA-Logik für Kanalnamen;
                        haltungsnummer = zeile[14:17]
                        n = 3
                        deckelhoehe = fzahl(zeile[24:31])
                        n = 4
                        xkoor = fzahl(zeile[31:45])
                        n = 5
                        ykoor = fzahl(zeile[45:59])
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
                        return False
    except BaseException as err:
        fehlermeldung(
            "Dateifehler",
            "Die Datei {} ist offensichtlich keine ANSI-Datei! ".format(dynafile),
        )
        logger.error("12er: Wert Nr. {} - {}\nZeile: {}".format(n, err, zeile))
        return False

    return True


def _reftables(db_qkan: DBConnection) -> bool:
    """add data to reference tables"""

    # 1. add data to table entwaesserungsarten

    daten = [
        ('Regenwasser', 'R', 'Freispiegelabfluss im geschlossenen Profil, Regenwassersystem', 1, 2, 'R', 'KR', 0, 0),
        ('Schmutzwasser', 'S', 'Freispiegelabfluss im geschlossenen Profil, Schmutzwassersystem', 2, 1, 'S', 'KS', 0, 0),
        ('Mischwasser', 'M', 'Freispiegelabfluss im geschlossenen Profil, Mischwassersystem', 0, 0, 'M', 'KM', 0, 0),
        ('RW Druckleitung', 'RD', 'Druckabfluss, Regenwassersystem', 1, None, None, 'DR', 1, 1),
        ('SW Druckleitung', 'SD', 'Druckabfluss, Schmutzwassersystem', 2, None, None, 'DS', 1, 1),
        ('MW Druckleitung', 'MD', 'Druckabfluss, Mischwassersystem', 0, None, None, 'DM', 1, 1),
        ('RW nicht angeschlossen', 'RT', 'Transporthaltung ohne Anschlüsse, Regenwassersystem', 1, 2, None, None, 1, 0),
        ('MW nicht angeschlossen', 'MT', 'Transporthaltung ohne Anschlüsse, Mischwassersystem', 0, 0, None, None, 1, 0),
        ('Rinne/Graben', 'RG', 'Abfluss im offenen Profil, Regenwassersystem (Rinnen, Gerinne, z.B. Entwässerungsgräben)', None, None, None, 'GR', None, None),
        ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None, None, None),
    ]

    daten = [el + (el[0],) for el in daten]  # trick: repeat last argument for ? after WHERE in SQL
    sql = """INSERT INTO entwaesserungsarten (
                bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau, transport, druckdicht)
                SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
    if not db_qkan.sql(sql, "dyna_import Referenzliste entwaesserungsarten", daten, many=True):
        return False

    # 2. add pipe profiles from temporary dyna tables

    # 2.1. Bei Namenskonflikten mit bereits gespeicherten Profilen wird die kp_key auf NULL gesetzt
    sql = """UPDATE profile
        SET kp_key = NULL
        WHERE profilnam IN 
        (   SELECT profilnam
            FROM dynaprofil
            WHERE profile.profilnam = dynaprofil.profilnam and profile.kp_key <> dynaprofil.profil_key)"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna profile-1"):
        return False

    # 2.2. Neue Profile aus DYNA hinzufügen
    sql = """INSERT INTO profile
        (profilnam, kp_key)
        SELECT profilnam, profil_key
        FROM dynaprofil
        WHERE profil_key not in 
        (   SELECT kp_key 
            FROM profile WHERE kp_key IS NOT NULL)"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna profile-2"):
        return False

    return True


def _insert_data_from_dyna(db_qkan: DBConnection, epsg: int) -> bool:
    # ------------------------------------------------------------------------------
    # Schachtdaten

    sql = """
        WITH ea AS (
            SELECT bezeichnung, kp_nr 
            FROM entwaesserungsarten 
            WHERE kp_nr IS NOT NULL
            GROUP BY kp_nr
        )
        INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                                    schachttyp, simstatus, kommentar, geop, geom)
        SELECT 
            dyna12.schoben as schnam,
            dyna12.xob as xsch, 
            dyna12.yob as ysch, 
            dyna12.sohleoben as sohlhoehe, 
            dyna12.deckeloben as deckelhoehe, 
            1.0 as durchm, 
            0 as druckdicht, 
            ea.bezeichnung as entwart, 
            'Schacht' AS schachttyp, 
            simulationsstatus.bezeichnung AS simstatus, 
            'Importiert mit QKan' AS kommentar,
            MakePoint(dyna12.xob, dyna12.yob, :epsg) AS geop,
            CastToMultiPolygon(MakePolygon(MakeCircle(dyna12.xob, dyna12.yob, 1.0, :epsg))) AS geom
        FROM dyna12
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN ea
        ON dyna12.entwart_nr = ea.kp_nr
        GROUP BY dyna12.schoben"""

    params = {"epsg": epsg}
    if not db_qkan.sql(sql, "importkanaldaten_dyna (11)", parameters=params):
        return False

    db_qkan.commit()

    # ------------------------------------------------------------------------------
    # Auslässe

    sql = """
        WITH ea AS (
            SELECT bezeichnung, kp_nr 
            FROM entwaesserungsarten 
            WHERE kp_nr IS NOT NULL
            GROUP BY kp_nr
        )
        INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, durchm, druckdicht, entwart, 
                                    schachttyp, simstatus, kommentar, geop, geom)
        SELECT
            dyna41.schnam as schnam,
            dyna41.xkoor as xsch, 
            dyna41.ykoor as ysch, 
            dyna12.sohleunten as sohlhoehe, 
            dyna41.deckelhoehe as deckelhoehe, 
            1.0 as durchm, 
            0 as druckdicht, 
            ea.bezeichnung as entwart,
            'Auslass' AS schachttyp, 
            simulationsstatus.bezeichnung AS simstatus, 
            'Importiert mit QKan' AS kommentar,
            MakePoint(dyna41.xkoor, dyna41.ykoor, :epsg) AS geop,
            CastToMultiPolygon(MakePolygon(MakeCircle(dyna41.xkoor, dyna41.ykoor, 1.0, :epsg))) AS geom
        FROM dyna41
        LEFT JOIN dyna12
        ON dyna41.schnam = dyna12.schunten
        LEFT JOIN simulationsstatus
        ON dyna12.simstatus_nr = simulationsstatus.kp_nr
        LEFT JOIN ea
        ON dyna12.entwart_nr = ea.kp_nr
        GROUP BY dyna41.schnam"""

    params = {"epsg": epsg}
    if not db_qkan.sql(sql, "importkanaldaten_dyna (14)", parameters=params):
        return False

    db_qkan.commit()

    # ------------------------------------------------------------------------------
    # Haltungsdaten

    # Daten aus temporären DYNA-Tabellen abfragen

    sql = """
        WITH ea AS (
            SELECT bezeichnung, kp_nr 
            FROM entwaesserungsarten 
            WHERE kp_nr IS NOT NULL
            GROUP BY kp_nr
        )
        INSERT INTO haltungen 
            (haltnam, schoben, schunten, 
            hoehe, breite, laenge, sohleoben, sohleunten, 
            teilgebiet, profilnam, entwart, ks, simstatus, kommentar, geom)
        SELECT 
            printf('%s-%s', dyna12.kanalnummer, dyna12.haltungsnummer) AS haltnam, 
            dyna12.schoben AS schoben, 
            dyna12.schunten AS schunten, 
            dyna12.hoehe AS hoehe, 
            dyna12.hoehe*dynaprofil.breite/dynaprofil.hoehe AS breite, 
            dyna12.laenge AS laenge, 
            dyna12.sohleoben AS sohleoben, 
            dyna12.sohleunten AS sohleunten, 
            NULL as teilgebiet, 
            dynaprofil.profilnam as profilnam, 
            ea.bezeichnung as entwart, 
            dynarauheit.ks as ks, 
            simulationsstatus.bezeichnung as simstatus, 
            'DYNA-Import' AS kommentar,
            MakeLine(MakePoint(dyna12.xob,dyna12.yob,:epsg),
                     MakePoint(coalesce(dy12un.xob, dyna41.xkoor),
                               coalesce(dy12un.yob, dyna41.ykoor),
                               :epsg))
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
        LEFT JOIN ea
        ON dyna12.entwart_nr = ea.kp_nr
        GROUP BY dyna12.kanalnummer, dyna12.haltungsnummer"""

    params = {'epsg': epsg}
    if not db_qkan.sql(sql, "importkanaldaten_dyna (7)", parameters=params):
        return False

    db_qkan.commit()

    sql = """
        INSERT INTO tezg
            (flnam, haltnam, schnam, neigkl, 
            schwerpunktlaufzeit, regenschreiber, 
            teilgebiet, abflussparameter, 
            kommentar)
        SELECT
            printf('f_%s-%s', dyna12.kanalnummer, dyna12.haltungsnummer) AS flnam, 
            printf('%s-%s', dyna12.kanalnummer, dyna12.haltungsnummer) AS haltnam, 
            dyna12.schoben AS schnam, 
            dyna12.neigkl AS neigkl,
            NULL AS schwerpunktlaufzeit, NULL AS regenschreiber, 
            NULL AS teilgebiet, '$Default_Unbef' AS abflussparameter, 
            'DYNA-Import' AS kommentar
        FROM dyna12
        GROUP BY dyna12.kanalnummer, dyna12.haltungsnummer"""

    if not db_qkan.sql(sql, "importkanaldaten_dyna (8)"):
        return False

    db_qkan.commit()

    return True
