# -*- coding: utf-8 -*-

"""
  Export Kanaldaten in eine DYNA-Datei (*.ein)
  Transfer von Kanaldaten aus einer QKan-Datenbank nach HYSTEM EXTRAN 7.6
"""

import logging
import os
from typing import List, Optional, TextIO, Union, cast

from qgis.core import Qgis
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QProgressBar

from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung, formf, fortschritt, meldung
from qkan.linkflaechen.updatelinks import updatelinkfl, updatelinksw

logger = logging.getLogger("QKan.dynaporter.export_to_dyna")

progress_bar: Optional[QProgressBar] = None


# Hilfsfunktionen --------------------------------------------------------------------------

# Funktion zur Umwandlung der Neigungsklassen
def fneigkl(neigung: Optional[float]) -> float:
    """Berechnung der Neigungsklasse aus Neigungswert (absolut)"""

    if neigung is None:
        return 0

    neigungliste = [0.0, 0.01, 0.04, 0.1, 999.0]
    neigklliste = [0, 1, 2, 3, 4]
    for neig, nkl in zip(neigungliste, neigklliste):
        if neigung < neig:
            return nkl
    else:
        fehlermeldung(
            "Programmfehler in export_to_dyna.fneigkl!", "Neigungsklasse fehlerhaft"
        )
        return 0.0


# Funktionen zum Schreiben der DYNA-Daten. Werden aus exportKanaldaten aufgerufen
def write12(
    db_qkan: DBConnection,
    db_handle: TextIO,
    dynakeys_id: List[str],
    dynakeys_ks: List[Union[str, float]],
    mindestflaeche: float,
    mit_verschneidung: bool,
    dynaprof_choice: enums.ProfChoice,
    dynabef_choice: enums.BefChoice,
    dynaprof_nam: List[str],
    dynaprof_key: List[str],
    ausw_and: str,
    auswahl: str,
) -> bool:
    """Schreiben der DYNA-Typ12-Datenzeilen

    :param db_qkan              Datenbankobjekt, das die Verknüpfung zur
                                QKan-SpatiaLite-Datenbank verwaltet.
    :param db_handle:           Zu Schreibende DYNA-Datei
    :param dynakeys_id:         Liste der DYNA-Schlüssel für Rauheitsbeiwerte,
                                Material und Regenspende
    :param dynakeys_ks:         Liste der Rauheitsbeiwerte in der DYNA-Datei
    :param mindestflaeche:      Mindestflächengröße, ab der Flächenobjekte
                                berücksichtigt werden
    :param mit_verschneidung:   Flächen werden mit Haltungsflächen verschnitten
                                (abhängig von Attribut "aufteilen")
    :param dynaprof_choice:     Option, wie die Zuordnung der Querprofile aus
                                QKan zu den in der DYNA-Datei vorhandenen
                                erfolgt: Über den gemeinsamen Profilnamen oder
                                den gemeinsamen Profilkey
    :param dynabef_choice:      Option für die Haltungsgesamtfläche: Bestimmung
                                als Summe der Einzelflächen oder über das
                                tezg-Flächenobjekt
    :param dynaprof_nam:        Liste der Querprofilnamen aus der
                                Vorlage-DYNA-Datei
    :param dynaprof_key:        Liste der Querprofilschlüssel aus der
                                Vorlage-DYNA-Datei
    :param ausw_and:            SQL-Textbaustein, um eine Bedingung mit "AND"
                                anzuhängen
    :param auswahl:             SQL-Textbaustein mit der Bedingung zur Filterung
                                auf eine Liste von Teilgebieten
    """

    # Optionen zur Berechnung der befestigten Flächen
    # ... benötigt keine Modifikation der Abfrage

    # Optionen zur Zuordnung des Profilschlüssels
    if dynaprof_choice == enums.ProfChoice.PROFILNAME:
        sql_prof1 = "h.profilnam AS profilid"
        sql_prof2 = ""
    elif dynaprof_choice == enums.ProfChoice.PROFILKEY:
        sql_prof1 = "p.kp_key AS profilid"
        sql_prof2 = """
        INNER JOIN profile as p
        ON h.profilnam = p.profilnam"""
    else:
        logger.error(
            "Fehler in export_to_dyna.write12: Unbekannte Option in dynaprof_choice: {}".format(
                dynaprof_choice
            )
        )
        raise Exception()

    # Verschneidung nur, wenn (mit_verschneidung)
    if mit_verschneidung:
        case_verschneidung = """
                CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom 
                ELSE CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3)) END AS geom"""
        join_verschneidung = """
            LEFT JOIN tezg AS tg
            ON lf.tezgnam = tg.flnam"""
        tezg_verschneidung = """area(tg.geom) AS fltezg,"""
    else:
        case_verschneidung = "fl.geom AS geom"
        join_verschneidung = ""
        tezg_verschneidung = "0 AS fltezg,"

    # wdistbef ist die mit der (Teil-) Fläche gewichtete Fließlänge zur Haltung für die befestigten Flächen zu
    # einer Haltung,
    # wdistdur entsprechend für die durchlässigen Flächen.

    sql = f"""
        WITH flintersect AS (
            SELECT lf.flnam AS flnam, lf.haltnam AS haltnam, 
                CASE fl.neigkl
                    WHEN 0 THEN 0.5
                    WHEN 1 THEN 2.5
                    WHEN 2 THEN 7.0
                    WHEN 3 THEN 12.0
                    ELSE 20.0
                    END AS neigung, 
                fl.abflussparameter AS abflussparameter, 
                {tezg_verschneidung}
                {case_verschneidung}
            FROM linkfl AS lf
            INNER JOIN flaechen AS fl
            ON lf.flnam = fl.flnam {join_verschneidung}),
        halflaech AS (
            SELECT
                fi.haltnam AS haltnam, 
                coalesce(ap.endabflussbeiwert, 1.0) AS abflussbeiwert, 
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN area(fi.geom)/10000.
                    ELSE 0 END) AS flbef,
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN 0
                    ELSE area(fi.geom)/10000. END) AS fldur,
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN distance(fi.geom,h.geom)*area(fi.geom)/10000.
                           ELSE 0 END) AS wdistbef,
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN 0
                           ELSE distance(fi.geom,h.geom)*area(fi.geom)/10000. END) AS wdistdur,
                sum(area(fi.geom)/10000.) AS flges,
                fi.fltezg AS fltezg,
                distance(fi.geom,h.geom) AS disttezg, 
                sum(neigung*area(fi.geom)/10000.) AS wneigung
            FROM flintersect AS fi
            LEFT JOIN abflussparameter AS ap
            ON fi.abflussparameter = ap.apnam
            INNER JOIN haltungen AS h 
            ON fi.haltnam = h.haltnam
            WHERE area(fi.geom) > {mindestflaeche}{ausw_and}{auswahl}
            GROUP BY fi.haltnam),
        einleitsw AS (
            SELECT haltnam, sum(zufluss) AS zufluss
            FROM einleit
            GROUP BY haltnam
        )
        SELECT 
            d.kanalnummer AS kanalnummer,
            d.haltungsnummer AS haltungsnummer, 
            h.laenge AS laenge,
            so.deckelhoehe AS deckelhoehe, 
            coalesce(h.sohleoben, so.sohlhoehe) AS sohleob,
            coalesce(h.sohleunten, su.sohlhoehe) AS sohleun,
            '0' AS material, 
            {sql_prof1}, 
            h.hoehe*1000. AS profilhoehe, 
            h.ks AS ks, 
            f.flbef*abflussbeiwert AS flbef, 
            f.flges AS flges,
            f.wdistbef/(f.flbef + 0.00000001) AS distbef,
            f.wdistdur/(f.fldur + 0.00000001) AS distdur,
            f.fltezg AS fltezg,
            f.disttezg AS disttezg,
            3 AS abfltyp, 
            e.zufluss AS qzu, 
            0 AS ewdichte, 
            0 AS tgnr, 
            f.wneigung/(f.flges + 0.00000001) AS neigung,
            a.kp_nr AS entwart, 
            0 AS haltyp,
            h.schoben AS schoben, 
            h.schunten AS schunten,
            x(so.geop) AS xob, 
            y(so.geop) AS yob
        FROM haltungen AS h
        INNER JOIN dynahal AS d
        ON h.pk = d.pk
        INNER JOIN schaechte AS so
        ON h.schoben = so.schnam
        INNER JOIN schaechte AS su
        ON h.schunten = su.schnam{sql_prof2}
        LEFT JOIN halflaech AS f
        ON h.haltnam = f.haltnam
        LEFT JOIN einleitsw AS e
        ON e.haltnam = h.haltnam
        LEFT JOIN entwaesserungsarten AS a
        ON h.entwart = a.bezeichnung
    """

    if not db_qkan.sql(sql, "dbQK: export_to_dyna.write12 (1)"):
        return False

    fortschritt("Export Datensätze Typ12", 0.3)
    if progress_bar:
        progress_bar.setValue(30)
    # createdat = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # Lesen der Daten aus der SQL-Abfrage und Schreiben in die DYNA-Datei --------------------
    for attr in db_qkan.fetchall():

        # Attribute in Variablen speichern
        (
            kanalnummer,
            haltungsnummer,
            laenge,
            deckelhoehe,
            sohleob,
            sohleun,
            material,
            profilid,
            profilhoehe,
            ks,
            flbef,
            flges,
            distbef,
            distdur,
            fltezg,
            disttezg,
            abfltyp,
            qzu,
            ewdichte,
            tgnr,
            neigung,
            entwart,
            haltyp,
            schoben,
            schunten,
            xob,
            yob,
        ) = attr

        laenge_t = formf(laenge, 7)
        deckelhoehe_t = formf(deckelhoehe, 7)
        sohleob_t = formf(sohleob, 7)
        sohleun_t = formf(sohleun, 7)
        profilhoehe_t = "{:4d}".format(int(profilhoehe))[:4]
        qzu_t = formf(qzu, 5)
        xob_t = formf(xob, 14)
        yob_t = formf(yob, 14)

        # Schlüssel für DYNA einsetzen
        try:
            float_list = ["{0:10.6f}".format(float(kb)) for kb in dynakeys_ks]
            kskey: str = dynakeys_id[float_list.index("{0:10.6f}".format(ks))]
            # logger.debug('ks= {0:10.6f}\ndynakeys_ks= {1:s}\ndynakeys_id= {2:s}\nkskey= {3:s}'.format(
            # ks,
            # ', '.join(['{0:10.6f}'.format(kb) for kb in dynakeys_ks]),
            # ', '.join(dynakeys_id),
            # kskey
            # ))
        except BaseException as err:
            fehlermeldung(
                "Fehler in export_to_dyna.write12 (2): {}".format(err),
                "ks {} konnte in dynakeys_ks nicht gefunden werden\ndynakeys_ks = {}".format(
                    ks, str(dynakeys_ks)
                ),
            )
            raise err

        if flges is None:
            flges_t = "     "
            befgrad_t = "  "
            neigkl_t = " "
            neigung_t = "       0"
            distbef_t = "       0"
            distdur_t = "       0"

            # XXX: TODO: befgrad/neigkl undefined
            befgrad, neigkl = 0.0, 0.0
        else:
            if dynabef_choice == enums.BefChoice.FLAECHEN:
                if flges != 0:
                    befgrad = flbef / flges * 100.0
                    befgrad = max(
                        0, min(99, int(round(befgrad, 0)))
                    )  # runden auf ganze Werte und Begrenzung auf 0 .. 99
                    neigkl = fneigkl(neigung)
                else:
                    # XXX: TODO: befgrad/neigkl undefined
                    befgrad, neigkl = 0, 0
            elif dynabef_choice == enums.BefChoice.TEZG:
                if fltezg == 0:
                    flges = 0

                    # XXX: TODO: befgrad/neigkl undefined
                    befgrad, neigkl = 0, 0
                else:
                    flges = fltezg
                    befgrad = flbef / flges * 100.0
                    befgrad = max(
                        0, min(99, int(round(befgrad, 0)))
                    )  # runden auf ganze Werte und Begrenzung auf 0 .. 99
                    neigkl = fneigkl(neigung)

                    # Berechnungen der Fließlänge für die durchlässigen Flächen
                    # XXX: TODO: wdistbef undefined
                    wdistbef = 0
                    distdur = (disttezg * flges - wdistbef) / (flges - flbef)
            else:
                raise Exception()

            # Vorbereitung der Ausgabefelder für DYNA
            if flges == 0:
                flges_t = "    0"
                befgrad_t = " 0"
                neigkl_t = "0"
                neigung_t = "       0"
                distbef_t = "       0"
                distdur_t = "       0"
            else:
                flges_t = formf(flges, 5)
                befgrad_t = "{0:2d}".format(befgrad)
                neigkl_t = "{0:1d}".format(int(neigkl))
                neigung_t = formf(neigung, 8)
                distbef_t = formf(distbef, 8)
                distdur_t = formf(distdur, 8)

        # Auswahl dynaprof_choice
        if dynaprof_choice == enums.ProfChoice.PROFILNAME:
            try:
                profilkey = dynaprof_key[dynaprof_nam.index(profilid)]
            except BaseException as err:
                fehlermeldung(
                    "Fehler in export_to_dyna.write12 (3): {}".format(err),
                    "Profilkey {id} konnte in interner Zuordnungsliste nicht gefunden werden\n",
                )
                logger.debug("dynprof_nam: {}".format(", ".join(dynaprof_nam)))
                raise err

        elif dynaprof_choice == enums.ProfChoice.PROFILKEY:
            profilkey = profilid
        else:
            raise Exception()

        try:
            zeile = (
                "12    {kanalnummer:>8s}{haltungsnummer:>3s}{laenge:7s}".format(
                    kanalnummer=kanalnummer,
                    haltungsnummer=haltungsnummer,
                    laenge=laenge_t,
                )
                + "{deckelhoehe:7s}{sohleob:7s}{sohleun:7s}{material:1s}".format(
                    deckelhoehe=deckelhoehe_t,
                    sohleob=sohleob_t,
                    sohleun=sohleun_t,
                    material=material,
                )
                + "{profilkey:2s}{profilhoehe:4s}{kskey:1s}".format(
                    profilkey=profilkey, profilhoehe=profilhoehe_t, kskey=kskey
                )
                + "{befgrad:2s}  {abfltyp:1d}".format(
                    befgrad=befgrad_t, abfltyp=abfltyp
                )
                + "{qzu:5s}{ewdichte:3d}{tgnr:5d}".format(
                    qzu=qzu_t, ewdichte=ewdichte, tgnr=tgnr
                )
                + "{flges:5s}{neigkl:1s}{entwart:1d}{haltyp:1d}".format(
                    flges=flges_t, neigkl=neigkl_t, entwart=entwart, haltyp=haltyp
                )
                + "  {schoben:>12s} {schunten:>12s}{xob:14s}{yob:14s}".format(
                    schoben=schoben, schunten=schunten, xob=xob_t, yob=yob_t
                )
                + "{distbef:>8s}{distdur:>8s}{neigung:>8s}\n".format(
                    distbef=distbef_t, distdur=distdur_t, neigung=neigung_t
                )
            )

            # logger.debug(
            # 'material = {}\n'.format(material) + \
            # 'profilkey = {}\n'.format(profilkey) + \
            # 'profilhoehe = {}\n'.format(profilhoehe) + \
            # 'ks = {}\n'.format(ks) + \
            # 'befgrad = {}\n'.format(befgrad) + \
            # 'abfltyp = {}\n'.format(abfltyp) + \
            # 'qzu = {}\n'.format(qzu) + \
            # 'ewdichte = {}\n'.format(ewdichte))

            db_handle.write(zeile)
        except BaseException as err:
            fehlermeldung(
                "Fehler in QKan_ExportDYNA.write12: {}\n".format(err),
                "Datentypfehler in Variablenliste:\n"
                + "kanalnummer = {}\n".format(kanalnummer)
                + "haltungsnummer = {}\n".format(haltungsnummer)
                + "laenge = {}\n".format(laenge)
                + "deckelhoehe = {}\n".format(deckelhoehe)
                + "sohleob = {}\n".format(sohleob)
                + "sohleun = {}\n".format(sohleun)
                + "material = {}\n".format(material)
                + "profilkey = {}\n".format(profilkey)
                + "profilhoehe = {}\n".format(profilhoehe)
                + "ks = {}\n".format(ks)
                + "befgrad = {}\n".format(befgrad)
                + "abfltyp = {}\n".format(abfltyp)
                + "qzu = {}\n".format(qzu)
                + "ewdichte = {}\n".format(ewdichte)
                + "tgnr = {}\n".format(tgnr)
                + "flges = {}\n".format(flges)
                + "neigkl = {}\n".format(neigkl)
                + "entwart = {}\n".format(entwart)
                + "haltyp = {}\n".format(haltyp)
                + "schoben = {}\n".format(schoben)
                + "schunten = {}\n".format(schunten)
                + "xob = {}\n".format(xob)
                + "yob = {}\n".format(yob),
            )
            return False

    return True


def write16(
    db_qkan: DBConnection, db_handle: TextIO, ausw_and: str, auswahl: str
) -> bool:
    """
    Schreiben der DYNA-Typ16-Datenzeilen

    :param db_qkan:     Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param db_handle:   Zu schreibende DYNA-Datei
    :param ausw_and:    SQL-Textbaustein, um eine Bedingung mit "AND" anzuhängen
    :param auswahl:     SQL-Textbaustein mit der Bedingung zur Filterung auf eine Liste von Teilgebieten
    """

    # SQL-Baustein, um die Bedingung {auswahl} um den Tabellennamen zu ergänzen
    if auswahl == "":
        ausw_tab = ""
    else:
        ausw_tab = "s."

    # Zusammenstellen der Daten.
    sql = f"""
        WITH v_anzan AS
    (   SELECT h.schunten, count(*) AS anzahl
        FROM haltungen AS h
        GROUP BY h.schunten),
    v_anzab AS
    (   SELECT h.schoben, count(*) AS anzahl
        FROM haltungen AS h
        GROUP BY h.schoben),
    v_halan AS
    (   SELECT h.schunten, x(s.geop) AS xschob, y(s.geop) AS yschob,
        d.kanalnummer AS kanalnummer,
        d.haltungsnummer AS haltungsnummer
        FROM haltungen AS h
        INNER JOIN dynahal AS d
        ON h.pk = d.pk
        INNER JOIN schaechte AS s
        ON s.schnam = h.schoben),
    v_halab AS
    (   SELECT h.schoben, x(s.geop) AS xschun, y(s.geop) AS yschun,
        d.kanalnummer AS kanalnummer,
        d.haltungsnummer AS haltungsnummer
        FROM haltungen AS h
        INNER JOIN dynahal AS d
        ON h.pk = d.pk
        INNER JOIN schaechte AS s
        ON s.schnam = h.schunten)
    SELECT s.schnam, 
        han.kanalnummer AS an_kanalnummer, han.haltungsnummer AS an_haltungsnummer, 
        hab.kanalnummer AS ab_kanalnummer, hab.haltungsnummer AS ab_haltungsnummer, 
        coalesce(anzan.anzahl, 0) AS an_anz, 
        coalesce(anzab.anzahl, 0) AS ab_anz
    FROM schaechte AS s
    LEFT JOIN v_anzan AS anzan
    ON anzan.schunten = s.schnam
    LEFT JOIN v_anzab AS anzab
    ON anzab.schoben = s.schnam
    LEFT JOIN v_halan AS han
    ON han.schunten = s.schnam
    LEFT JOIN v_halab AS hab
    ON hab.schoben = s.schnam
    WHERE ((anzab.anzahl <> 1 OR anzab.anzahl IS NULL) OR
           (anzan.anzahl <> 1 OR anzan.anzahl IS NULL) OR
           (anzab.anzahl = 1 AND anzan.anzahl = 1 AND han.kanalnummer <> hab.kanalnummer)){ausw_and}{ausw_tab}{auswahl}
    ORDER BY s.schnam, han.kanalnummer, han.haltungsnummer
    """

    if not db_qkan.sql(sql, "dbQK: export_to_dyna.write16 (1)"):
        return False

    akt_schnam = ""  # Identifiziert Datensätze zum gleichen Knoten
    knotennr = 0  # Knotennummer
    zeilan = ""
    zeilab = ""
    zeilkn = None
    # XXX: TODO: akt_i undefined
    akt_i = 0

    for i, attr in enumerate(db_qkan.fetchall()):

        # Attribute in Variablen speichern
        (
            schnam,
            an_kanalnummer,
            an_haltungsnummer,
            ab_kanalnummer,
            ab_haltungsnummer,
            an_anz,
            ab_anz,
        ) = attr

        if schnam != akt_schnam:
            # Vorherigen Knoten schreiben.
            if i > 0:
                # Dies darf erst ab 2. gelesener Zeile geschehen...

                db_handle.write("{0:15s}{1:}{2:}\n".format(zeilkn, zeilan, zeilab))

            # Nächsten Knoten initialisieren

            akt_schnam = schnam
            knotennr += 1  # Knotennummer inkrementieren
            akt_i = i  # Nummer aktualisieren
            # Datensatz Typ16 schreiben (Achtung: Letzter Datensatz wird nach Abschluss der Schleife geschrieben)
            zeilkn = "16{knotennr:4d}  {an_anz:1d}{ab_anz:1d}     ".format(
                knotennr=knotennr, an_anz=an_anz, ab_anz=ab_anz
            )

            # Es gibt entweder mindestens eine ankommende oder abgehende Haltung
            if an_anz > 0:
                zeilan = " 1{kanalnummer:>8s}{haltungsnummer:>3s}".format(
                    kanalnummer=an_kanalnummer, haltungsnummer=an_haltungsnummer
                )
            else:
                zeilan = ""  # Ankommende Haltungen zurücksetzen

            if ab_anz > 0:
                zeilab = " 2{kanalnummer:>8s}{haltungsnummer:>3s}".format(
                    kanalnummer=ab_kanalnummer, haltungsnummer=ab_haltungsnummer
                )
            else:
                zeilab = ""  # Abgehende Haltungen zurücksetzen

        else:
            # Folgedatensatz zum selben Knoten

            if ab_anz != 0:
                akt_an = (i - akt_i) // ab_anz  # Lfd. Nummer der ankommenden Haltung
                akt_ab = (i - akt_i) % ab_anz
            else:
                akt_an = 0
                akt_ab = 0

            if akt_an == 0:
                # abgehende Haltung übernehmen; nur im ersten Teilblock
                zeilab += "02{kanalnummer:>8s}{haltungsnummer:>3s}".format(
                    kanalnummer=ab_kanalnummer, haltungsnummer=ab_haltungsnummer
                )
            if akt_ab == 0:
                # ankommende Haltung übernehmen; jeweils zu Beginn jedes Teilblocks
                zeilan += "51{kanalnummer:>8s}{haltungsnummer:>3s}".format(
                    kanalnummer=an_kanalnummer, haltungsnummer=an_haltungsnummer
                )

    else:
        # Letzter Typ16-Datensatz kann erst jetzt geschrieben werden.
        if zeilkn is not None:
            db_handle.write("{0:15s}{1:}{2:}\n".format(zeilkn, zeilan, zeilab))

    return True


def write41(
    db_qkan: DBConnection, db_handle: TextIO, ausw_and: str, auswahl: str
) -> bool:
    """
    Schreiben der DYNA-Typ41-Datenzeilen (Endschächte = Auslässe)

    :param db_qkan:     Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param db_handle:   Zu schreibende DYNA-Datei
    :param ausw_and:    SQL-Textbaustein, um eine Bedingung mit "AND" anzuhängen
    :param auswahl:     SQL-Textbaustein mit der Bedingung zur Filterung auf eine Liste von Teilgebieten
    """

    # SQL-Baustein, um die Bedingung {auswahl} um den Tabellennamen zu ergänzen
    if auswahl == "":
        ausw_tab = ""
    else:
        ausw_tab = "s."

    # Zusammenstellen der Daten.
    sql = f"""
        SELECT
            d.kanalnummer AS kanalnummer,
            d.haltungsnummer AS haltungsnummer,
            s.deckelhoehe AS deckelhoehe, 
            x(s.geop) AS xsch, 
            y(s.geop) AS ysch, 
            s.schnam AS schnam
        FROM dynahal AS d
        INNER JOIN schaechte AS s
        ON s.schnam = d.schunten
        WHERE s.schachttyp = 'Auslass'{ausw_and}{ausw_tab}{auswahl}
    """

    if not db_qkan.sql(sql, "dbQK: export_to_dyna.write41 (1)"):
        return False

    for attr in db_qkan.fetchall():
        # Attribute in Variablen speichern
        (kanalnummer, haltungsnummer, deckelhoehe, xsch, ysch, schnam) = attr

        deckelhoehe_t = formf(deckelhoehe, 7)
        xsch_t = formf(xsch, 14)
        ysch_t = formf(ysch, 14)

        db_handle.write(
            "41    {kanalnummer:>8s}{haltungsnummer:>3s}       ".format(
                kanalnummer=kanalnummer, haltungsnummer=haltungsnummer
            )
            + "{deckelhoehe:7s}{xsch:14s}{ysch:14s}{schnam:>12s}\n".format(
                deckelhoehe=deckelhoehe_t, xsch=xsch_t, ysch=ysch_t, schnam=schnam
            )
        )

    return True


# Hauptfunktion ----------------------------------------------------------------------------
def export_kanaldaten(
    iface: QgisInterface,
    dynafile: str,
    template_dyna: str,
    db_qkan: DBConnection,
    dynabef_choice: enums.BefChoice,
    dynaprof_choice: enums.ProfChoice,
    liste_teilgebiete: List[str],
    profile_ergaenzen: bool,
    autonum_dyna: bool,
    mit_verschneidung: bool,
    fangradius: float = 0.1,
    mindestflaeche: float = 0.5,
    max_loops: int = 1000,
) -> bool:
    """Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine HE-Firebird-Datenbank.

    :param iface:
    :param dynafile:            Zu Schreibende DYNA-Datei; kann mit Vorlagedatei identisch sein
    :param template_dyna:       Vorlage-DYNA-Datei
    :param db_qkan:             Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param dynabef_choice:
    :param dynaprof_choice:
    :param liste_teilgebiete:   Liste der ausgewählten Teilgebiete
    :param profile_ergaenzen:   Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                                werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                                abgebrochen.
    :param autonum_dyna:        Sollen die Haltungen in der DYNA-Zusatztabelle nummeriert werden?
    :param mit_verschneidung:
    :param fangradius:          Suchradius, mit dem an den Enden der Verknüpfungen (linkfl, linksw) eine
                                Haltung bzw. ein Einleitpunkt zugeordnet wird.
    :param mindestflaeche:
    :param max_loops:

    """

    # Statusmeldung in der Anzeige
    global progress_bar
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "", "Export in Arbeit. Bitte warten."
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # Aktualisierung der Verknüpfungen
    if not updatelinkfl(db_qkan, fangradius):
        fehlermeldung(
            "Fehler beim Update der Flächen-Verknüpfungen (dyna.export 1)",
            "Der logische Cache konnte nicht aktualisiert werden.",
        )
        return False

    if not updatelinksw(db_qkan, fangradius):
        fehlermeldung(
            "Fehler beim Update der Einzeleinleiter-Verknüpfungen (dyna.export 1)",
            "Der logische Cache konnte nicht aktualisiert werden.",
        )
        return False

    # DYNA-Vorlagedatei lesen. Dies geschieht zu Beginn, damit Zieldatei selbst Vorlage sein kann!
    try:
        dynatempfile = open(template_dyna, encoding="windows-1252")
        dynatemplate = dynatempfile.readlines()
        dynatempfile.close()
    except IOError as err:
        fehlermeldung(
            "Fehler (32) in QKan_ExportDYNA {}".format(err),
            "Die Vorlage-DYNA-Datei ist nicht vorhanden: {}".format(
                repr(template_dyna)
            ),
        )
        return False

    # DYNA-Datei löschen, falls schon vorhanden
    if os.path.exists(dynafile):
        try:
            os.remove(dynafile)
        except BaseException as err:
            fehlermeldung(
                "Fehler (33) in QKan_ExportDYNA {}".format(err),
                "Die DYNA-Datei ist schon vorhanden und kann nicht ersetzt werden: {}".format(
                    repr(dynafile)
                ),
            )
            return False

    fortschritt("DYNA-Datei aus Vorlage kopiert...", 0.01)
    progress_bar.setValue(1)

    # --------------------------------------------------------------------------------------------------
    # Zur Abschaetzung der voraussichtlichen Laufzeit

    db_qkan.sql("SELECT count(*) AS n FROM schaechte")
    anzdata = float(db_qkan.fetchone()[0])
    fortschritt("Anzahl Schächte: {}".format(anzdata))

    db_qkan.sql("SELECT count(*) AS n FROM haltungen")
    anzdata += float(db_qkan.fetchone()[0])
    fortschritt("Anzahl Haltungen: {}".format(anzdata))

    db_qkan.sql("SELECT count(*) AS n FROM flaechen")
    anzdata += float(db_qkan.fetchone()[0]) * 2
    fortschritt("Anzahl Flächen: {}".format(anzdata))

    # Nur Daten fuer ausgewaehlte Teilgebiete
    if len(liste_teilgebiete) != 0:
        ausw_where = """ WHERE """
        ausw_and = """ AND """
        auswahl = """teilgebiet in ('{}')""".format("', '".join(liste_teilgebiete))
    else:
        ausw_where = ""
        ausw_and = ""
        auswahl = ""

    # --------------------------------------------------------------------------------------------
    # Haltungsnummerierung, falls aktiviert
    # Diese ist nur für das gesamte Entwässerungsnetz möglich, damit keine Redundanzen entstehen.

    if autonum_dyna:

        # Zurücksetzen von "kanalnummer" und "haltungsnummer"
        sql = f"""
            UPDATE dynahal
            SET kanalnummer = NULL,
                haltungsnummer = NULL {ausw_where}{auswahl}"""

        if not db_qkan.sql(sql, "dbQK: export_to_dyna.init_dynahal (1)"):
            return False

        db_qkan.commit()

        # Einfügen der Haltungsdaten in die Zusatztabelle "dynahal"

        sql = f"""
            WITH halnumob AS (
                SELECT schunten, count(*) AS anzahl
                FROM haltungen
                GROUP BY schunten
            ), halnumun AS (
                SELECT schoben, count(*) AS anzahl
                FROM haltungen
                GROUP BY schoben
            )
            INSERT INTO dynahal
            (pk, haltnam, schoben, schunten, teilgebiet, anzobob, anzobun, anzunun, anzunob)
            SELECT
                haltungen.pk, haltungen.haltnam, haltungen.schoben, haltungen.schunten, haltungen.teilgebiet,
                coalesce(haltobob.anzahl, 0) AS anzobob, coalesce(haltobun.anzahl, 0) AS anzobun,
                coalesce(haltunun.anzahl, 0) AS anzunun, coalesce(haltunob.anzahl, 0) AS anzunob
            FROM haltungen
            LEFT JOIN halnumob AS haltobob
            ON haltungen.schoben = haltobob.schunten
            LEFT JOIN halnumun AS haltobun
            ON haltungen.schoben = haltobun.schoben
            LEFT JOIN halnumun AS haltunun
            ON haltungen.schunten = haltunun.schoben
            LEFT JOIN halnumob AS haltunob
            ON haltungen.schunten = haltunob.schunten
            WHERE haltnam NOT IN (
                SELECT haltnam FROM dynahal)
                {ausw_and}{auswahl}"""

        if not db_qkan.sql(sql, "dbQK: export_to_dyna.init_dynahal (2)"):
            return False

        # Zurücksetzen von "kanalnummer" und "haltungsnummer"

        sql = f"""
            UPDATE dynahal
            SET kanalnummer = NULL,
                haltungsnummer = NULL
                {ausw_where}{auswahl}"""

        if not db_qkan.sql(sql, "dbQK: export_to_dyna.init_dynahal (3)"):
            return False

        # Nummerierung der Anfangshaltungen

        if len(liste_teilgebiete) == 0:
            sql = f"""
                UPDATE dynahal
                SET kanalnummer = ROWID, haltungsnummer = 1
                WHERE anzobob <> 1 OR anzobun <> 1
                    {ausw_and}{auswahl}"""

        if not db_qkan.sql(sql, "dbQK: export_to_dyna.init_dynahal (4)"):
            return False

        db_qkan.commit()

        # Weitergabe der Nummerierung an die Folgehaltung im selben Strang,
        # solange change() nicht 0 zurückgibt

        nchange = 1  # Initialisierung
        changelog = []
        nlimit = 0

        while (nchange > 0) and (max_loops > nlimit):
            nlimit += 1
            sql = f"""
                UPDATE dynahal
                SET 
                    kanalnummer = 
                    (   SELECT kanalnummer
                        FROM dynahal AS dh
                        WHERE dh.schunten = dynahal.schoben),
                    haltungsnummer = 
                    (   SELECT haltungsnummer + 1
                        FROM dynahal AS dh
                        WHERE dh.schunten = dynahal.schoben)
                WHERE
                    dynahal.anzobob = 1 AND
                    dynahal.anzobun = 1 AND
                    dynahal.kanalnummer IS NULL
                    {ausw_and}{auswahl};
                """

            if not db_qkan.sql(sql, "dbQK: export_to_dyna.init_dynahal (5)"):
                return False

            if not db_qkan.sql(
                "SELECT changes();", "dbQK: export_to_dyna.init_dynahal (6)"
            ):
                return False

            nchange = int(
                db_qkan.fetchone()[0]
            )  # Zahl der zuletzt geänderten Datensätze
            changelog.append(nchange)

        db_qkan.commit()

        if nlimit >= max_loops:
            fehlermeldung(
                "Fehler in QKan_ExportDYNA",
                f"{nlimit} Schleifendurchläufe in der Autonummerierung. "
                f"Gegebenenfalls muss max_loops in der config-Datei angepasst werden...",
            )

        logger.debug(
            "Anzahl Änderungen für DYNA:\n{}".format(
                ", ".join([str(n) for n in changelog])
            )
        )

    else:
        # Keine Autonummerierung. Dann müssen die Haltungsnamen so vergeben sein, dass sich Kanal- und Haltungs-
        # nummer daraus wieder herstellen lassen (8 Zeichen für Kanal + "-" + 3 Zeichen für Haltungsnummer).

        # noinspection SqlWithoutWhere
        if not db_qkan.sql(
            "DELETE FROM dynahal;",
            "dbQK: export_to_dyna.init_dynahal (7): Daten in Tabelle dynahal konnten nicht gelöscht werden",
        ):
            return False

        sql = f"""
            INSERT INTO dynahal
            (pk, haltnam, kanalnummer, haltungsnummer, schoben, schunten, teilgebiet)
            SELECT
                h.pk, h.haltnam,
                substr(h.haltnam, 1, instr(h.haltnam, '-')-1) AS kn,
                substr(h.haltnam, instr(h.haltnam, '-') - length(h.haltnam)) AS hn,
                h.schoben, h.schunten, h.teilgebiet
            FROM haltungen AS h
            WHERE haltnam NOT IN (
                SELECT haltnam FROM dynahal)
                {ausw_and}{auswahl}"""

        if not db_qkan.sql(sql, "dbQK: export_to_dyna.init_dynahal (8)"):
            return False

    progress_bar.setValue(20)

    # DYNA-Schlüsselwerte für Rauheit, Material und Regenspende ------------------------------------------------------

    # Einlesen der Schlüsselwerte aus der DYNA-Datei, die bereits als Textliste dynatemplate vorliegt
    # Da die keys willkürlich sind, werden zunächst die 4 Spalten getrennt gelesen und bei Bedarf aus
    # den Daten der QKan-Datenbank ergänzt.

    typ05 = False
    dynakeys_id = []
    dynakeys_mat = []
    dynakeys_spende = []
    dynakeys_ks = []

    for z in dynatemplate:
        if typ05:
            if z[:2] == "##":
                pass
            elif z[:2] == "05":
                id = z[3:4]
                mat = z[5:9]
                spende = z[10:20]
                ks = z[20:30]
                dynakeys_id.append(id)
                if mat.strip() != "":
                    dynakeys_mat.append(mat)
                if spende.strip() != "":
                    dynakeys_spende.append(spende)
                if ks.strip() != "":
                    dynakeys_ks.append(float(ks))
            else:
                break
        if z[:6] == "++SCHL":
            typ05 = True
    else:
        dynakeys_id = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        dynakeys_mat = ["Az", "B", "Stz"]
        dynakeys_ks = [0.0, 0.4, 0.75, 1.5]

    # Prüfung, ob alle Werte, die in der QKan-Datenbank vorkommen, bereits vorhanden sind.

    sql = """
        SELECT printf('%10.6f',ks) AS ks
        FROM haltungen
        GROUP BY ks
    """
    if not db_qkan.sql(sql, "QKan_ExportDYNA.export_to_dyna (1) "):
        return False

    daten = db_qkan.fetchall()
    for kslis in daten:
        ks_new = kslis[0]
        if ks_new not in ["{0:10.6f}".format(ks) for ks in dynakeys_ks]:
            dynakeys_ks.append(ks_new)

    # So viele Schlüssel ergänzen, bis Anzahl in dynakeys_ks erreicht (meistens schon der Fall...)
    next_id = dynakeys_id[-1]
    while len(dynakeys_ks) > len(dynakeys_id):
        n = ord(next_id) + 1
        if n == 58:
            next_id = "A"
        else:
            next_id = chr(n)
        dynakeys_id.append(next_id)

    # Übrige DYNA-Key-Listen auf gleich Länge auffüllen
    dynakeys_mat += [""] * (len(dynakeys_id) - len(dynakeys_mat))
    dynakeys_ks += [0] * (len(dynakeys_id) - len(dynakeys_ks))

    # DYNA-Profile lesen und mit den benötigten Profilen abgleichen -----------------------------------

    dynaprof_nam = []
    dynaprof_key = []

    # Initialisierungen für Profile
    profilmodus = -1  # -1: Nicht im Profilblock, Nächste Zeile ist bei:
    #  0: Bezeichnung des gesamten Profile-Blocks.
    #  1: Profilname, Koordinaten, nächster Block oder Ende
    #  2: Profilnr.
    #  3: Erste Koordinaten des Querprofils

    x1 = None  # markiert, dass noch kein Profil eingelesen wurde (s. u.)
    profilnam, profil_key = "", ""
    for zeile in dynatemplate:
        if zeile[0:2] == "##":
            continue  # Kommentarzeile wird übersprungen

        # Zuerst werden Abschnitte mit besonderen Daten bearbeitet (Profildaten etc.)
        if profilmodus >= 0:
            if profilmodus == 0:
                # Bezeichnung des gesamten Profile-Blocks. Wird nicht weiter verwendet
                profilmodus = 1
                continue
            elif profilmodus == 2:
                # Profilnr.

                profil_key = zeile.strip()
                profilmodus = 3
                continue
            elif profilmodus == 3:
                # Erster Profilpunkt
                profilmodus = 1
                x1 = 1  # Punkt als Startpunkt für nächstes Teilstück speichern
                continue
            elif profilmodus == 1:
                # weitere Profilpunkte, nächstes Profil oder Ende der Profile
                if zeile[0:1] == "(":
                    # profilmodus == 1, weitere Profilpunkte
                    continue
                else:
                    # Nächstes Profil oder Ende Querprofile (=Ende des aktuellen Profils)

                    # Beschriftung des Profils. Grund: Berechnung von Breite und Höhe ist erst nach
                    # Einlesen aller Profilzeilen möglich.

                    # Erst wenn das erste Profil eingelesen wurde
                    if x1 is not None:
                        # Höhe zu Breite-Verhältnis berechnen
                        dynaprof_key.append(profil_key)
                        dynaprof_nam.append(profilnam)
                        logger.debug(
                            "export_to_dyna.exportKanaldaten (2): profilnam = {}".format(
                                profilnam
                            )
                        )
                        # sql = '''INSERT INTO dynaprofil (profil_key, profilnam, breite, hoehe)
                        # VALUES ('{key}', '{nam}', {br}, {ho})'''.format(
                        # key=profil_key, nam=profilnam, br=breite, ho=hoehe)
                        # logger.debug('sql = {}'.format(sql))
                        # if not dbQK.sql(sql, 'importkanaldaten_kp (1)'):
                        # return None

                    if zeile[0:2] != "++":
                        # Profilname
                        profilnam = zeile.strip()
                        profilmodus = 2
                        continue
                    else:
                        # Ende Block Querprofile (es sind mehrere möglich!)
                        profilmodus = -1
                        x1 = None

        # Optionen und Daten
        if zeile[0:6] == "++QUER":
            profilmodus = 0

    # Prüfen, ob alle in den zu exportierenden Daten enthaltenen Profile schon definiert sind.

    fehler = 0

    if dynaprof_choice == enums.ProfChoice.PROFILNAME:
        # Die DYNA-Schlüssel werden entsprechend der DYNA-Vorlagedatei vergeben. Daher braucht
        # nur das Vorhandensein der Profilnamen geprüft zu werden.
        sql = f"""SELECT profilnam
                FROM haltungen {ausw_where}{auswahl}
                GROUP BY profilnam"""

        if not db_qkan.sql(sql, "dbQK: QKan_ExportDYNA.export_to_dyna.profile (1)"):
            return False

        daten = db_qkan.fetchall()
        for profil in daten:
            profil_new = profil[0]
            if profil_new not in dynaprof_nam:
                meldung(
                    "Fehlende Profildaten in DYNA-Vorlagedatei {fn}".format(
                        fn=template_dyna
                    ),
                    "{pn}".format(pn=profil_new),
                )
                logger.debug(
                    "export_to_dyna.exportKanaldaten (1): dynaprof_nam = {}".format(
                        ", ".join(dynaprof_nam)
                    )
                )
                if profile_ergaenzen:
                    if not db_qkan.sql(
                        "INSERT INTO profile (profilnam) VALUES (?)",
                        "dbQK: export_to_dyna.exportKanaldaten (1)",
                        parameters=(profil_new,),
                    ):
                        return False
                    db_qkan.commit()
                fehler = 2
        if fehler == 2:
            fehlermeldung(
                "Fehler in den Profildaten",
                "Es gibt Profile in den Haltungsdaten, die nicht in der DYNA-Vorlage ",
            )
            return False

    elif dynaprof_choice == enums.ProfChoice.PROFILKEY:
        sql = f"""SELECT p.kp_key, h.profilnam
                FROM haltungen AS h
                LEFT JOIN profile AS p
                ON h.profilnam = p.profilnam {ausw_where}{auswahl}
                GROUP BY p.kp_key"""

        if not db_qkan.sql(sql, "dbQK: QKan_ExportDYNA.export_to_dyna.profile (2)"):
            return False

        daten = db_qkan.fetchall()
        for profil in daten:
            profil_key, profilnam = profil
            if profil_key is None:
                profil_key = "NULL"
            if profil_key not in dynaprof_key:
                meldung(
                    "Fehlende Profildaten in DYNA-Vorlagedatei {fn}".format(
                        fn=template_dyna
                    ),
                    "{id}".format(id=profil_key),
                )
                logger.debug("dynaprof_key = {}".format(", ".join(dynaprof_key)))
                if profile_ergaenzen:
                    if not db_qkan.sql(
                        "INSERT INTO profile (profilnam, kp_key) VALUES (?, ?)",
                        "dbQK: export_to_dyna.exportKanaldaten (1)",
                        parameters=(profilnam, profil_key),
                    ):
                        return False
                    db_qkan.commit()
                fehler = 2
            elif profil_key is None:
                # XXX: TODO: profil_new undefined
                profil_new = profilnam
                fehlermeldung(
                    "Fehlende ID in DYNA-Vorlagedatei {fn}".format(fn=template_dyna),
                    "Es fehlt die ID für Profil {pn}".format(pn=profil_new),
                )
                fehler = max(fehler, 1)  # fehler = 2 hat Priorität

        if fehler == 1:
            fehlermeldung(
                "Fehler in den Profildaten",
                "Es gibt Profile ohne eine DYNA-Nummer (kp_key)",
            )
            return False
        elif fehler == 2:
            fehlermeldung(
                "Fehler in den Profildaten",
                "Es gibt Profile in den Haltungsdaten, die nicht in der DYNA-Vorlage vorhanden sind",
            )
            return False

    # Schreiben der DYNA-Datei ------------------------------------------------------------------------

    with open(dynafile, "w", encoding="windows-1252") as df:

        typ05 = False  # markiert, ob in der Vorlagedatei Block mit Datentyp 05 erreicht
        typ12 = False  # markiert, ob in der Vorlagedatei Block mit Datentyp 12 erreicht
        typ16 = False  # markiert, ob in der Vorlagedatei Block mit Datentyp 16 erreicht
        typ41 = False  # markiert, ob in der Vorlagedatei Block mit Datentyp 41 erreicht

        # Die nachfolgende Schleife durchläuft das DYNA-Template in der Liste "dynatemplate", schreibt die
        # Standardzeilen. An den Stellen, an denen in der Vorlage Daten eingefügt und gegebenfalls in der
        # Vorlage vorhandene Daten übersprungen werden müssen, sind entsprechende Blöcke eingefügt.
        # Diese sind durch Flags gekennzeichnet, z.B. typ05

        for z in dynatemplate:

            if z[:2] == "##":
                # Kommentarzeilen werden geschrieben, solange keine Blöcke aktiv sind
                df.write(z)
                continue

            # Schreiben des aktiven Datenblocks

            # Block Typ05
            if typ05:
                if z[:2] == "++":
                    # Sobald nächster Block erreicht, ist Typ05 beendet
                    # Jetzt werden alle neuen Typ-05-Datensätze geschrieben
                    for id, mat, kb in zip(dynakeys_id, dynakeys_mat, dynakeys_ks):
                        df.write(
                            "05 {id:1s} {mat:4s} {sp:10.6f}{kb:10.6f}{ks:10.6f}\n".format(
                                id=id[:1], mat=mat[:4], sp=0, kb=kb, ks=0
                            ).replace(
                                "  0.000000", "          "
                            )
                        )
                    typ05 = False
                    df.write(z)

            # Block Typ12
            elif typ12:
                if z[:2] == "++":
                    # Sobald nächster Block erreicht, ist Typ12 beendet
                    # Jetzt werden alle neuen Typ-12-Datensätze geschrieben
                    if not write12(
                        db_qkan,
                        df,
                        dynakeys_id,
                        cast(List[Union[str, float]], dynakeys_ks),
                        mindestflaeche,
                        mit_verschneidung,
                        dynaprof_choice,
                        dynabef_choice,
                        dynaprof_nam,
                        dynaprof_key,
                        ausw_and,
                        auswahl,
                    ):
                        return False
                    typ12 = False
                    df.write(z)

            # Block Typ16
            elif typ16:
                if z[:2] == "++":
                    # Sobald nächster Block erreicht, ist Typ16 beendet
                    # Jetzt werden alle neuen Typ-16-Datensätze geschrieben
                    if not write16(db_qkan, df, ausw_and, auswahl):
                        return False
                    typ16 = False
                    df.write(z)
                elif z[6:8] != "  ":
                    df.write(z)  # Bauwerksverknüpfungen
            # Block Typ41
            elif typ41:
                if z[:2] == "++":
                    # Sobald nächster Block erreicht, ist Typ41 beendet
                    # Jetzt werden alle neuen Typ-41-Datensätze geschrieben
                    if not write41(db_qkan, df, ausw_and, auswahl):
                        return False
                    typ41 = False
                    df.write(z)
            else:
                # Allgemeine Zeilen werden direkt aus der Templatedatei geschrieben
                df.write(z)

            # Aktivierung der Datenblöcke

            if z[:6] == "++SCHL":
                # Block Typ05 beginnt: "Schlüsseltabellen für Rauheit, Material und Regenspende"
                typ05 = True
                # df.write(z)
                continue
            elif z[:6] == "++KANA":
                # Block Typ12 beginnt: "Haltungs- und Flächendaten"
                typ12 = True
                # df.write(z)
                continue
            elif z[:6] == "++NETZ":
                # Block Typ16 beginnt: "Verzweigungen und Endschächte"
                typ16 = True
                # df.write(z)
                continue
            elif z[:6] == "++DECK":
                # Block Typ41 beginnt: "Verzweigungen und Endschächte"
                typ41 = True
                # df.write(z)
                continue

    fortschritt("Ende...", 1)
    progress_bar.setValue(100)
    status_message.setText("Datenexport abgeschlossen.")
    status_message.setLevel(Qgis.Success)
    return True
