# -*- coding: utf-8 -*-

"""
  Export Kanaldaten nach HYSTEM-EXTRAN 8
  Transfer von Kanaldaten aus einer QKan-Datenbank nach HYSTEM EXTRAN 8
"""

import logging
import os
import shutil
import time
from typing import List

from qgis.gui import QgisInterface
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_database import versionolder
from qkan.database.qkan_utils import checknames, fehlermeldung, fortschritt, meldung

# Referenzlisten
from qkan.linkflaechen.updatelinks import updatelinkageb, updatelinkfl, updatelinksw

logger = logging.getLogger("QKan.exporthe.export_to_he8")

progress_bar = None


def exporthe8(
    database_he: str,
    dbtemplate_he: str,
    db_qkan: DBConnection,
    liste_teilgebiete: List[str],
    autokorrektur: bool,
    fangradius: float = 0.1,
    mindestflaeche: float = 0.5,
    mit_verschneidung: bool = True,
    export_flaechen_he8: bool = True,
    check_export: dict = None,
) -> bool:
    """
    Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine HE8-SQLite-Datenbank.

    :param database_he:         Pfad zur HE8-SQLite-Datenbank
    :param dbtemplate_he:       Vorlage für die zu erstellende HE8-SQLite-Datenbank
    :param db_qkan:                Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param liste_teilgebiete:   Liste der ausgewählten Teilgebiete
    :param autokorrektur:       Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                                werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                                abgebrochen.
    :param fangradius:          Suchradius, mit dem an den Enden der Verknüpfungen (linkfl, linksw) eine
                                Haltung bzw. ein Einleitpunkt zugeordnet wird.
    :param mindestflaeche:      Mindestflächengröße bei Einzelflächen und Teilflächenstücken
    :param mit_verschneidung:   Flächen werden mit Haltungsflächen verschnitten (abhängig von Attribut "aufteilen")
    :param export_flaechen_he8:
    :param check_export:        Liste von Export-Optionen
    """

    if check_export is None:
        check_export = {}

    # Statusmeldung in der Anzeige
    global progress_bar
    # progress_bar = QProgressBar(iface.messageBar())
    # progress_bar.setRange(0, 100)
    # status_message = iface.messageBar().createMessage(
    #    "", "Export in Arbeit. Bitte warten."
    # )
    # status_message.layout().addWidget(progress_bar)
    # iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # ITWH-Datenbank aus gewählter Vorlage kopieren
    if os.path.exists(database_he):
        try:
            os.remove(database_he)
        except BaseException as err:
            fehlermeldung(
                "Fehler (33) in QKan_Export",
                "Die HE-Datenbank ist schon vorhanden und kann nicht ersetzt werden: {}".format(
                    repr(err)
                ),
            )
            return False
    try:
        shutil.copyfile(dbtemplate_he, database_he)
    except BaseException as err:
        fehlermeldung(
            "Fehler (34) in QKan_Export",
            "Kopieren der Vorlage HE-Datenbank fehlgeschlagen: {}\nVorlage: {}\nZiel: {}\n".format(
                repr(err), dbtemplate_he, database_he
            ),
        )
        return False
    fortschritt("SQLite-Datenbank aus Vorlage kopiert...", 0.01)
    # progress_bar.setValue(1)

    # Verbindung zur Hystem-Extran-Datenbank

    sql = f'ATTACH DATABASE "{database_he}" AS he'
    if not db_qkan.sql(sql, "dbQK: export_to_he8.attach_he8"):
        return False

    # --------------------------------------------------------------------------------------------
    # Besonderes Gimmick des ITWH-Programmiers: Die IDs der Tabellen muessen sequentiell
    # vergeben werden!!! Ein Grund ist, dass (u.a.?) die Tabelle "tabelleninhalte" mit verschiedenen
    # Tabellen verknuepft ist und dieser ID eindeutig sein muss.

    db_qkan.sql("SELECT NextId, Version FROM he.Itwh$ProgInfo")
    data = db_qkan.fetchone()
    nextid = int(data[0]) + 1
    he_db_version = [int(_) for _ in data[1].split(".")]
    logger.debug("HE IDBF-Version {}".format(he_db_version))

    # --------------------------------------------------------------------------------------------
    # Export der Schaechte

    if check_export["export_schaechte"] or check_export["modify_schaechte"]:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND schaechte.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl = ""

        fortschritt("Export Schaechte Teil 1...", 0.1)
        # progress_bar.setValue(15)

        if check_export["modify_schaechte"]:
            sql = """
                UPDATE he.Schacht SET (
                  Deckelhoehe, 
                  Sohlhoehe,
                  Gelaendehoehe,
                  Art,
                  Planungsstatus, LastModified,
                  Durchmesser, Geometry) =
                ( SELECT
                    schaechte.deckelhoehe AS deckelhoehe,
                    schaechte.sohlhoehe AS sohlhoehe,
                    schaechte.deckelhoehe AS gelaendehoehe, 
                    1 AS art, 
                    st.he_nr AS planungsstatus, 
                    strftime('%Y-%m-%d %H:%M:%S', coalesce(schaechte.createdat, 'now')) AS lastmodified, 
                    schaechte.durchm*1000 AS durchmesser,
                    SetSrid(schaechte.geop, -1) AS geometry
                  FROM schaechte
                  LEFT JOIN simulationsstatus AS st
                  ON schaechte.simstatus = st.bezeichnung
                  WHERE schaechte.schnam = he.Schacht.Name and schaechte.schachttyp = 'Schacht'{auswahl})
                WHERE he.Schacht.Name IN 
                      (SELECT schnam FROM schaechte WHERE schaechte.schachttyp = 'Schacht'{auswahl})
                """.format(
                auswahl=auswahl
            )

            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (1)"):
                return False

        # Einfuegen in die Datenbank
        if check_export["export_schaechte"]:

            # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
            sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (2)"):
                return False

            data = db_qkan.fetchone()
            if len(data) == 2:
                idmin, idmax = data
            else:
                fehlermeldung(
                    "Fehler (35) in QKan_Export",
                    f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                )
            nr0 = nextid
            id0 = nextid - idmin

            sql = """
                INSERT INTO he.Schacht
                ( Name, Deckelhoehe, Sohlhoehe, 
                  Gelaendehoehe, Art,
                  Planungsstatus, LastModified, Id, Durchmesser, Geometry)
                SELECT
                  schaechte.schnam AS name, 
                  schaechte.deckelhoehe AS deckelhoehe, 
                  schaechte.sohlhoehe AS sohlhoehe,
                  schaechte.deckelhoehe AS gelaendehoehe, 
                  1 AS art, 
                  st.he_nr AS planungsstatus, 
                  strftime('%Y-%m-%d %H:%M:%S', coalesce(schaechte.createdat, 'now')) AS lastmodified, 
                  schaechte.rowid + {id0} AS id, 
                  schaechte.durchm*1000 AS durchmesser,
                  SetSrid(schaechte.geop, -1) AS geometry
                FROM schaechte
                LEFT JOIN simulationsstatus AS st
                ON schaechte.simstatus = st.bezeichnung
                WHERE schaechte.schnam NOT IN (SELECT Name FROM he.Schacht) and 
                      schaechte.schachttyp = 'Schacht'{auswahl}
            """.format(
                auswahl=auswahl, id0=id0
            )

            if not db_qkan.sql(sql, "dbQK: export_schaechte (3)"):
                return False

            nextid += idmax - idmin + 1
            db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {nextid}")
            db_qkan.commit()

            fortschritt("{} Schaechte eingefuegt".format(nextid - nr0), 0.30)

        # progress_bar.setValue(30)

    # --------------------------------------------------------------------------------------------
    # Export der Speicherbauwerke
    #

    if check_export["export_speicher"] or check_export["modify_speicher"]:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND schaechte.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl = ""

        fortschritt("Export Speicherschaechte...", 0.35)
        # progress_bar.setValue(35)

        # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
        if check_export["modify_speicher"]:

            sql = """
                UPDATE he.Speicherschacht SET
                (   Sohlhoehe, Gelaendehoehe, 
                    Scheitelhoehe,
                    Planungsstatus,
                    LastModified, Kommentar, Geometry
                    ) =
                ( SELECT
                    schaechte.sohlhoehe AS sohlhoehe, 
                    schaechte.deckelhoehe AS gelaendehoehe,
                    schaechte.deckelhoehe AS scheitelhoehe,
                    st.he_nr AS planungsstatus, 
                    strftime('%Y-%m-%d %H:%M:%S', coalesce(schaechte.createdat, 'now')) AS lastmodified, 
                    kommentar AS kommentar,
                    SetSrid(schaechte.geop, -1) AS geometry
                  FROM schaechte
                  LEFT JOIN simulationsstatus AS st
                  ON schaechte.simstatus = st.bezeichnung
                  WHERE schaechte.schnam = he.Speicherschacht.Name and schaechte.schachttyp = 'Speicher'{auswahl})
                WHERE he.Speicherschacht.Name IN 
                      (SELECT schnam FROM schaechte WHERE schaechte.schachttyp = 'Speicher'{auswahl})
                """.format(
                auswahl=auswahl
            )

            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_speicher (1)"):
                return False

        # Einfuegen in die Datenbank
        if check_export["export_speicher"]:

            nr0 = nextid

            # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
            sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (2)"):
                return False

            data = db_qkan.fetchone()
            if len(data) == 2:
                idmin, idmax = data
            else:
                fehlermeldung(
                    "Fehler (35) in QKan_Export",
                    f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                )
            nr0 = nextid
            id0 = nextid - idmin

            sql = """
                INSERT INTO he.Speicherschacht
                ( Id, Name, Typ, Sohlhoehe,
                  Gelaendehoehe, Art, AnzahlKanten,
                  Scheitelhoehe, HoeheVollfuellung,
                  Planungsstatus,
                  LastModified, Kommentar, Geometry)
                SELECT
                  schaechte.rowid + {id0} AS id, 
                  schaechte.schnam AS name, 
                  1 AS typ, 
                  schaechte.sohlhoehe AS sohlhoehe, 
                  schaechte.deckelhoehe AS gelaendehoehe,
                  1 AS art, 
                  2 AS anzahlkanten, 
                  schaechte.deckelhoehe AS scheitelhoehe,
                  schaechte.deckelhoehe AS hoehevollfuellung,
                  st.he_nr AS planungsstatus, 
                  strftime('%Y-%m-%d %H:%M:%S', coalesce(schaechte.createdat, 'now')) AS lastmodified, 
                  kommentar AS kommentar,
                  SetSrid(schaechte.geop, -1) AS geometry
                FROM schaechte
                LEFT JOIN simulationsstatus AS st
                ON schaechte.simstatus = st.bezeichnung
                WHERE schaechte.schnam NOT IN (SELECT Name FROM he.Speicherschacht) and 
                      schaechte.schachttyp = 'Speicher'{auswahl}
            """.format(
                auswahl=auswahl, id0=id0
            )

            if not db_qkan.sql(sql, "dbQK: export_speicher (2)"):
                return False

            nextid += idmax - idmin + 1
            db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {nextid}")
            db_qkan.commit()

            fortschritt("{} Speicher eingefuegt".format(nextid - nr0), 0.40)

    # --------------------------------------------------------------------------------------------
    # Export der Auslaesse
    #

    if check_export["export_auslaesse"] or check_export["modify_auslaesse"]:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND schaechte.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl = ""

        fortschritt("Export Auslässe...", 0.40)
        # progress_bar.setValue(40)

        # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
        if check_export["modify_auslaesse"]:

            sql = """
                UPDATE he.Auslass SET
                (   Sohlhoehe, Gelaendehoehe, 
                    Scheitelhoehe,
                    Planungsstatus,
                    LastModified, Kommentar, Geometry
                    ) =
                ( SELECT
                    schaechte.sohlhoehe AS sohlhoehe, 
                    schaechte.deckelhoehe AS gelaendehoehe,
                    schaechte.deckelhoehe AS scheitelhoehe,
                    st.he_nr AS planungsstatus, 
                    strftime('%Y-%m-%d %H:%M:%S', coalesce(schaechte.createdat, 'now')) AS lastmodified, 
                    kommentar AS kommentar,
                    SetSrid(schaechte.geop, -1) AS geometry
                  FROM schaechte
                  LEFT JOIN simulationsstatus AS st
                  ON schaechte.simstatus = st.bezeichnung
                  WHERE schaechte.schnam = he.Auslass.Name and schaechte.schachttyp = 'Auslass'{auswahl})
                WHERE he.Auslass.Name IN 
                      (SELECT schnam FROM schaechte WHERE schaechte.schachttyp = 'Auslass'{auswahl})
                """.format(
                auswahl=auswahl
            )

            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_auslaesse (1)"):
                return False

        # Einfuegen in die Datenbank
        if check_export["export_auslaesse"]:

            nr0 = nextid

            # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
            sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (2)"):
                return False

            data = db_qkan.fetchone()
            if len(data) == 2:
                idmin, idmax = data
            else:
                fehlermeldung(
                    "Fehler (35) in QKan_Export",
                    f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                )
            nr0 = nextid
            id0 = nextid - idmin

            sql = """
                INSERT INTO he.Auslass
                ( Id, Name, Typ, Sohlhoehe,
                  Gelaendehoehe, Art, AnzahlKanten,
                  Scheitelhoehe, HoeheVollfuellung,
                  Planungsstatus,
                  LastModified, Kommentar, Geometry)
                SELECT
                  schaechte.rowid + {id0} AS id, 
                  schaechte.schnam AS name, 
                  1 AS typ, 
                  schaechte.sohlhoehe AS sohlhoehe, 
                  schaechte.deckelhoehe AS gelaendehoehe,
                  1 AS art, 
                  2 AS anzahlkanten, 
                  schaechte.deckelhoehe AS scheitelhoehe,
                  schaechte.deckelhoehe AS hoehevollfuellung,
                  st.he_nr AS planungsstatus, 
                  strftime('%Y-%m-%d %H:%M:%S', coalesce(schaechte.createdat, 'now')) AS lastmodified, 
                  kommentar AS kommentar,
                  SetSrid(schaechte.geop, -1) AS geometry
                FROM schaechte
                LEFT JOIN simulationsstatus AS st
                ON schaechte.simstatus = st.bezeichnung
                WHERE schaechte.schnam NOT IN (SELECT Name FROM he.Auslass) and 
                      schaechte.schachttyp = 'Speicher'{auswahl}
            """.format(
                auswahl=auswahl, id0=id0
            )

            if not db_qkan.sql(sql, "dbQK: export_speicher (2)"):
                return False

            nextid += idmax - idmin + 1
            db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {nextid}")
            db_qkan.commit()

            fortschritt("{} Speicher eingefuegt".format(nextid - nr0), 0.40)

        sql = """
            SELECT
                schaechte.schnam AS schnam,
                schaechte.deckelhoehe AS deckelhoehe,
                schaechte.sohlhoehe AS sohlhoehe,
                schaechte.durchm*1000 AS durchmesser,
                kommentar AS kommentar,
                createdat,
                geom
            FROM schaechte
            WHERE schaechte.schachttyp = 'Auslass'{}
            """.format(
            auswahl
        )

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_auslaesse"):
            del db_qkan
            return False

        nr0 = nextid

        fortschritt("Export Auslässe...", 0.20)

        for attr in db_qkan.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (
                schnam,
                deckelhoehe_t,
                sohlhoehe_t,
                durchmesser_t,
                kommentar,
                createdat_t,
                geom,
            ) = ("NULL" if el is None else el for el in attr)

            # Formatierung der Zahlen
            (deckelhoehe, sohlhoehe, durchmesser) = (
                "NULL" if tt == "NULL" else "{:.3f}".format(float(tt))
                for tt in (deckelhoehe_t, sohlhoehe_t, durchmesser_t)
            )

            # Standardwerte, falls keine Vorgaben
            if createdat_t == "NULL":
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            else:
                try:
                    if createdat_t.count(":") == 1:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M")
                    else:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M:%S")
                except:
                    createdat_s = time.localtime()
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", createdat_s)

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export["modify_auslaesse"]:
                sql = f"""
                    UPDATE Auslass SET
                    Typ=1, Rueckschlagklappe=0,
                    Sohlhoehe={sohlhoehe},
                    Gelaendehoehe={deckelhoehe}, Art=3, AnzahlKanten=0,
                    Scheitelhoehe={deckelhoehe}, KonstanterZufluss=0,
                    Planungsstatus='0',
                    LastModified='{createdat}', Kommentar='{kommentar}', Geometry='{geom}'
                    WHERE Name = '{schnam}';
                """

                if not db_qkan.sql(sql, "db_qkan: export_auslaesse (1)"):
                    return False

            # Einfuegen in die Datenbank
            if check_export["export_auslaesse"]:
                sql = f"""
                    INSERT INTO he.Auslass
                    ( Id, Typ, Rueckschlagklappe, Sohlhoehe,
                      Gelaendehoehe, Art, AnzahlKanten,
                      Scheitelhoehe, KonstanterZufluss, Planungsstatus,
                      Name, LastModified, Kommentar, Geometry)
                    SELECT
                      {nextid}, 1, 0, {sohlhoehe},
                      {deckelhoehe}, 3, 0,
                      {deckelhoehe}, 0, '0',
                      '{schnam}', '{createdat}', '{kommentar}', '{geom}'
                    WHERE '{schnam}' NOT IN (SELECT Name FROM Auslass);
                """

                if not db_qkan.sql(sql, "db_qkan: export_auslaesse (2)"):
                    return False

                nextid += 1

        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Auslässe eingefuegt".format(nextid - nr0), 0.40)
    # progress_bar.setValue(50)

    # --------------------------------------------------------------------------------------------
    # Export der Pumpen
    #

    if check_export["export_pumpen"] or check_export["modify_pumpen"]:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE pumpen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl = ""

        sql = """
            SELECT
                pumpen.pnam AS pnam,
                pumpen.schoben AS schoben,
                pumpen.schunten AS schunten,
                pumpentypen.he_nr AS pumpentypnr,
                pumpen.steuersch AS steuersch,
                pumpen.einschalthoehe AS einschalthoehe_t,
                pumpen.ausschalthoehe AS ausschalthoehe_t,
                simulationsstatus.he_nr AS simstatusnr,
                pumpen.kommentar AS kommentar,
                pumpen.createdat AS createdat
            FROM pumpen
            LEFT JOIN pumpentypen
            ON pumpen.pumpentyp = pumpentypen.bezeichnung
            LEFT JOIN simulationsstatus
            ON pumpen.simstatus = simulationsstatus.bezeichnung{}
            """.format(
            auswahl
        )

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_pumpen"):
            del db_qkan
            return False

        nr0 = nextid

        fortschritt("Export Pumpen...", 0.60)

        for attr in db_qkan.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (
                pnam,
                schoben,
                schunten,
                pumpentypnr,
                steuersch,
                einschalthoehe_t,
                ausschalthoehe_t,
                simstatusnr,
                kommentar,
                createdat,
            ) = ("NULL" if el is None else el for el in attr)

            # Formatierung der Zahlen
            (einschalthoehe, ausschalthoehe) = (
                "NULL" if tt == "NULL" else "{:.3f}".format(float(tt))
                for tt in (einschalthoehe_t, ausschalthoehe_t)
            )

            # Standardwerte, falls keine Vorgaben
            if createdat_t == "NULL":
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            else:
                try:
                    if createdat_t.count(":") == 1:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M")
                    else:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M:%S")
                except:
                    createdat_s = time.localtime()
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", createdat_s)

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export["modify_pumpen"]:
                sql = """
                    UPDATE Pumpe SET
                    Typ={typ}, SchachtOben='{schoben}', SchachtUnten='{schunten}', 
                    Steuerschacht='{steuersch}', 
                    Einschalthoehe={einschalthoehe}, 
                    Ausschalthoehe={ausschalthoehe}, Planungsstatus={simstatusnr},
                    LastModified='{lastmodified}', Kommentar='{kommentar}'
                    WHERE Name = '{name}';
                """.format(
                    name=pnam,
                    typ=pumpentypnr,
                    schoben=schoben,
                    schunten=schunten,
                    steuersch=steuersch,
                    einschalthoehe=einschalthoehe,
                    ausschalthoehe=ausschalthoehe,
                    simstatusnr=simstatusnr,
                    lastmodified=createdat,
                    kommentar=kommentar,
                )

                if not db_qkan.sql(sql, "db_qkan: export_pumpen (1)"):
                    return False

            # Einfuegen in die Datenbank
            if check_export["export_pumpen"]:
                sql = """
                    INSERT INTO he.Pumpe
                    ( Id, Name, Typ, SchachtOben, SchachtUnten, 
                      Steuerschacht, Einschalthoehe, 
                      Ausschalthoehe, Planungsstatus,
                      LastModified, Kommentar)
                    SELECT
                      {id}, '{name}', {typ}, '{schoben}', '{schunten}', 
                      '{steuersch}', {einschalthoehe}, {ausschalthoehe}, 
                      {simstatusnr},
                      '{lastmodified}', '{kommentar}'
                    WHERE '{name}' NOT IN (SELECT Name FROM Pumpe);
                """.format(
                    id=nextid,
                    name=pnam,
                    typ=pumpentypnr,
                    schoben=schoben,
                    schunten=schunten,
                    steuersch=steuersch,
                    einschalthoehe=einschalthoehe,
                    ausschalthoehe=ausschalthoehe,
                    simstatusnr=simstatusnr,
                    lastmodified=createdat,
                    kommentar=kommentar,
                )

                if not db_qkan.sql(sql, "db_qkan: export_pumpen (2)"):
                    return False

                nextid += 1

        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Pumpen eingefuegt".format(nextid - nr0), 0.40)
    # progress_bar.setValue(60)

    # --------------------------------------------------------------------------------------------
    # Export der Wehre
    #

    if check_export["export_wehre"] or check_export["modify_wehre"]:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE wehre.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl = ""

        sql = """
            SELECT
                wehre.wnam AS wnam,
                wehre.schoben AS schoben,
                wehre.schunten AS schunten,
                coalesce(sob.sohlhoehe, 0) AS sohleoben_t,
                coalesce(sun.sohlhoehe, 0) AS sohleunten_t,
                wehre.schwellenhoehe AS schwellenhoehe_t,
                wehre.kammerhoehe AS kammerhoehe_t,
                wehre.laenge AS laenge_t,
                wehre.uebeiwert AS uebeiwert_t,
                simulationsstatus.he_nr AS simstatusnr,
                wehre.kommentar AS kommentar,
                wehre.createdat AS createdat
            FROM wehre
            LEFT JOIN simulationsstatus
            ON wehre.simstatus = simulationsstatus.bezeichnung
            LEFT JOIN schaechte AS sob 
            ON wehre.schoben = sob.schnam
            LEFT JOIN schaechte AS sun 
            ON wehre.schunten = sun.schnam{}
            """.format(
            auswahl
        )

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_wehre"):
            del db_qkan
            return False

        nr0 = nextid

        fortschritt("Export Wehre...", 0.65)

        for attr in db_qkan.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (
                wnam,
                schoben,
                schunten,
                sohleoben_t,
                sohleunten_t,
                schwellenhoehe_t,
                kammerhoehe_t,
                laenge_t,
                uebeiwert_t,
                simstatusnr,
                kommentar,
                createdat,
            ) = ("NULL" if el is None else el for el in attr)

            # Formatierung der Zahlen
            (sohleoben, sohleunten, schwellenhoehe, kammerhoehe, laenge, uebeiwert) = (
                "NULL" if tt == "NULL" else "{:.3f}".format(float(tt))
                for tt in (
                    sohleoben_t,
                    sohleunten_t,
                    schwellenhoehe_t,
                    kammerhoehe_t,
                    laenge_t,
                    uebeiwert_t,
                )
            )

            # Standardwerte, falls keine Vorgaben
            if createdat_t == "NULL":
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            else:
                try:
                    if createdat_t.count(":") == 1:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M")
                    else:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M:%S")
                except:
                    createdat_s = time.localtime()
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", createdat_s)

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export["modify_wehre"]:
                sql = """
                    UPDATE Wehr SET
                    Typ=1, Schwellenhoehe={schwellenhoehe},	Ueberfallbeiwert={uebeiwert},
                    Geometrie1={kammerhoehe}, Geometrie2={laenge},
                    SchachtOben='{schoben}', SchachtUnten='{schunten}', 
                    SohlhoeheOben='{sohleoben}', SohlhoeheUnten='{sohleunten}', 
                    Planungsstatus={simstatusnr},
                    LastModified='{lastmodified}', Kommentar='{kommentar}'
                    WHERE Name = '{name}';
                """.format(
                    name=wnam,
                    schoben=schoben,
                    schunten=schunten,
                    sohleoben=sohleoben,
                    sohleunten=sohleunten,
                    schwellenhoehe=schwellenhoehe,
                    kammerhoehe=kammerhoehe,
                    laenge=laenge,
                    uebeiwert=uebeiwert,
                    simstatusnr=simstatusnr,
                    lastmodified=createdat,
                    kommentar=kommentar,
                )

                if not db_qkan.sql(sql, "db_qkan: export_wehre (1)"):
                    return False

            # Einfuegen in die Datenbank
            if check_export["export_wehre"]:
                sql = f"""
                    INSERT INTO he.Wehr
                    (Id, Name, Typ, SchachtOben, SchachtUnten, 
                     SohlhoeheOben, SohlhoeheUnten, 
                     Schwellenhoehe, Geometrie1, 
                     Geometrie2, Ueberfallbeiwert, 
                     Rueckschlagklappe, Verfahrbar, Profiltyp, 
                     Ereignisbilanzierung, EreignisGrenzwertEnde,
                     EreignisGrenzwertAnfang, EreignisTrenndauer, 
                     EreignisIndividuell, Planungsstatus, 
                     LastModified, Kommentar)
                    SELECT
                      {nextid}, '{wnam}', 1, '{schoben}', '{schunten}', 
                      {sohleoben}, {sohleunten}, 
                      {schwellenhoehe}, {kammerhoehe}, 
                      {laenge}, {uebeiwert}, 
                      0, 0, 52, 0, 0, 0, 0, 0, {simstatusnr},
                      '{createdat}', '{kommentar}'
                    WHERE '{wnam}' NOT IN (SELECT Name FROM Wehr);
                """

                if not db_qkan.sql(sql, "db_qkan: export_wehre (2)"):
                    return False

                nextid += 1

        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Wehre eingefuegt".format(nextid - nr0), 0.40)
    # progress_bar.setValue(60)

    # --------------------------------------------------------------------------------------------
    # Export der Haltungen
    #
    # Erläuterung zum Feld "GESAMTFLAECHE":
    # Die Haltungsfläche (area(tezg.geom)) wird in das Feld "GESAMTFLAECHE" eingetragen und erscheint damit
    # in HYSTEM-EXTRAN in der Karteikarte "Haltungen > Trockenwetter". Solange dort kein
    # Siedlungstyp zugeordnet ist, wird diese Fläche nicht wirksam und dient nur der Information!

    # Vorbereitung für die SQL-Abfragen
    if check_export["modify_haltungen"] or check_export["export_haltungen"]:

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            auswahl = " AND haltungen.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl = ""

        # Varianten abhängig von HE-Version
        if versionolder(he_db_version[0:2], [7, 8], 2):
            logger.debug("Version vor 7.8 erkannt")
            fieldsnew = ""
            attrsnew = ""
        elif versionolder(he_db_version[0:2], [7, 9], 2):
            logger.debug("Version vor 7.9 erkannt")
            fieldsnew = ", 0 AS einzugsgebiet, 0 as konstanterzuflusstezg"
            attrsnew = ", Einzugsgebiet, KonstanterZuflussTezg"
        else:
            logger.debug("Version 7.9 erkannt")
            fieldsnew = """, 0 AS einzugsgebiet, 0 AS konstanterzuflusstezg
                           , 0 AS befestigteflaeche, 0 AS unbefestigteflaeche"""
            attrsnew = ", Einzugsgebiet, KonstanterZuflussTezg, BefestigteFlaeche, UnbefestigteFlaeche"

        # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
        if check_export["modify_haltungen"]:

            sql = """
              UPDATE he.Rohr SET
              ( SchachtOben, SchachtUnten,
                Laenge, 
                SohlhoeheOben,
                SohlhoeheUnten, 
                Profiltyp, Sonderprofilbezeichnung,
                Geometrie1, Geometrie2, 
                Kanalart,
                Rauigkeitsbeiwert, Anzahl,
                RauhigkeitAnzeige,
                LastModified, Materialart{attrsnew}) =
              ( SELECT
                  haltungen.schoben AS schachtoben, haltungen.schunten AS schachtunten,
                  coalesce(haltungen.laenge, glength(haltungen.geom)) AS laenge,
                  coalesce(haltungen.sohleoben,sob.sohlhoehe) AS sohlhoeheoben,
                  coalesce(haltungen.sohleunten,sun.sohlhoehe) AS sohlhoeheunten,
                  profile.he_nr AS profiltyp, haltungen.profilnam AS sonderprofilbezeichnung, 
                  haltungen.hoehe AS geometrie1, haltungen.breite AS geometrie2,
                  entwaesserungsarten.he_nr AS kanalart,
                  coalesce(haltungen.ks, 1.5) AS rauigkeitsbeiwert, 1 AS anzahl, 
                  coalesce(haltungen.ks, 1.5) AS rauhigkeitanzeige,
                  coalesce(haltungen.createdat, strftime('%Y-%m-%d %H:%M:%S','now')) AS lastmodified, 
                  28 AS materialart{fieldsnew}
                FROM
                  (haltungen JOIN schaechte AS sob ON haltungen.schoben = sob.schnam)
                  JOIN schaechte AS sun ON haltungen.schunten = sun.schnam
                  LEFT JOIN profile ON haltungen.profilnam = profile.profilnam
                  LEFT JOIN entwaesserungsarten ON haltungen.entwart = entwaesserungsarten.bezeichnung
                  LEFT JOIN simulationsstatus AS st ON haltungen.simstatus = st.bezeichnung
                  WHERE haltungen.haltnam = he.Rohr.Name and 
                        (st.he_nr IN ('0', '1', '2') or st.he_nr IS NULL){auswahl})
              WHERE he.Rohr.Name IN 
              ( SELECT haltnam 
                FROM haltungen
                LEFT JOIN simulationsstatus AS sa 
                ON haltungen.simstatus = sa.bezeichnung 
                WHERE (sa.he_nr IN ('0', '1', '2') or sa.he_nr IS NULL){auswahl})
              """.format(
                attrsnew=attrsnew, fieldsnew=fieldsnew, auswahl=auswahl
            )

            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_haltungen (1)"):
                return False

        # Einfuegen in die Datenbank
        if check_export["export_haltungen"]:

            # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
            sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_haltungen (2)"):
                return False

            data = db_qkan.fetchone()
            if len(data) == 2:
                idmin, idmax = data
            else:
                fehlermeldung(
                    "Fehler (35) in QKan_Export",
                    f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                )
            nr0 = nextid
            id0 = nextid - idmin

            sql = """
              INSERT INTO he.Rohr
              ( Id, 
                Name, SchachtOben, SchachtUnten, 
                Laenge, 
                SohlhoeheOben,
                SohlhoeheUnten, 
                Profiltyp, Sonderprofilbezeichnung, 
                Geometrie1, Geometrie2, 
                Kanalart, 
                Rauigkeitsbeiwert, Anzahl, 
                RauhigkeitAnzeige,
                LastModified, 
                Materialart{attrsnew})
              SELECT
                haltungen.rowid + {id0} AS id, 
                haltungen.haltnam AS name, haltungen.schoben AS schachtoben, haltungen.schunten AS schachtunten,
                coalesce(haltungen.laenge, glength(haltungen.geom)) AS laenge,
                coalesce(haltungen.sohleoben,sob.sohlhoehe) AS sohlhoeheoben,
                coalesce(haltungen.sohleunten,sun.sohlhoehe) AS sohlhoeheunten,
                profile.he_nr AS profiltyp, haltungen.profilnam AS sonderprofilbezeichnung, 
                haltungen.hoehe AS geometrie1, haltungen.breite AS geometrie2,
                entwaesserungsarten.he_nr AS kanalart,
                coalesce(haltungen.ks, 1.5) AS rauigkeitsbeiwert, 1 AS anzahl, 
                coalesce(haltungen.ks, 1.5) AS rauhigkeitanzeige,
                coalesce(haltungen.createdat, strftime('%Y-%m-%d %H:%M:%S','now')) AS lastmodified, 
                28 AS materialart{fieldsnew}
              FROM
                (haltungen JOIN schaechte AS sob ON haltungen.schoben = sob.schnam)
                JOIN schaechte AS sun ON haltungen.schunten = sun.schnam
                LEFT JOIN profile ON haltungen.profilnam = profile.profilnam
                LEFT JOIN entwaesserungsarten ON haltungen.entwart = entwaesserungsarten.bezeichnung
                LEFT JOIN simulationsstatus AS st ON haltungen.simstatus = st.bezeichnung
                WHERE haltungen.haltnam NOT IN (SELECT Name FROM he.Rohr) and
                      (st.he_nr IN ('0', '1', '2') or st.he_nr IS NULL){auswahl};
              """.format(
                attrsnew=attrsnew, fieldsnew=fieldsnew, auswahl=auswahl, id0=id0
            )

            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_haltungen (3)"):
                return False

            nextid += idmax - idmin + 1
            db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {nextid}")
            db_qkan.commit()

            fortschritt("Ca. {} Haltungen eingefuegt".format(nextid - nr0), 0.60)

        # progress_bar.setValue(70)

    # --------------------------------------------------------------------------------------------
    # Export der Bodenklassen

    if check_export["export_bodenklassen"] or check_export["modify_bodenklassen"]:

        sql = """
            SELECT
                bknam AS bknam,
                infiltrationsrateanfang AS infiltrationsrateanfang, 
                infiltrationsrateende AS infiltrationsrateende, 
                infiltrationsratestart AS infiltrationsratestart, 
                rueckgangskonstante AS rueckgangskonstante, 
                regenerationskonstante AS regenerationskonstante, 
                saettigungswassergehalt AS saettigungswassergehalt, 
                createdat AS createdat,
                kommentar AS kommentar
            FROM bodenklassen
            """

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_bodenklassen"):
            del db_qkan
            return False

        nr0 = nextid

        for attr in db_qkan.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (
                bknam,
                infiltrationsrateanfang,
                infiltrationsrateende,
                infiltrationsratestart,
                rueckgangskonstante,
                regenerationskonstante,
                saettigungswassergehalt,
                createdat_t,
                kommentar,
            ) = ("NULL" if el is None else el for el in attr)

            # Der leere Satz Bodenklasse ist nur für interne QKan-Zwecke da.
            if bknam == "NULL":
                continue

            # Standardwerte, falls keine Vorgaben
            if createdat_t == "NULL":
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            else:
                try:
                    if createdat_t.count(":") == 1:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M")
                    else:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M:%S")
                except:
                    createdat_s = time.localtime()
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", createdat_s)

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export["modify_bodenklassen"]:
                sql = """
                    UPDATE Bodenklasse SET
                    InfiltrationsrateAnfang={infiltrationsrateanfang},
                    InfiltrationsrateEnde={infiltrationsrateende},
                    InfiltrationsrateStart={infiltrationsratestart},
                    Rueckgangskonstante={rueckgangskonstante},
                    Regenerationskonstante={regenerationskonstante},
                    Saettigungswassergehalt={saettigungswassergehalt},
                    LastModified='{lastmodified}',
                    Kommentar='{kommentar}'
                    WHERE Name = '{name}';
                    """.format(
                    infiltrationsrateanfang=infiltrationsrateanfang,
                    infiltrationsrateende=infiltrationsrateende,
                    infiltrationsratestart=infiltrationsratestart,
                    rueckgangskonstante=rueckgangskonstante,
                    regenerationskonstante=regenerationskonstante,
                    saettigungswassergehalt=saettigungswassergehalt,
                    name=bknam,
                    lastmodified=createdat,
                    kommentar=kommentar,
                )

                if not db_qkan.sql(sql, "db_qkan: export_bodenklassen (1)"):
                    return False

            # Einfuegen in die Datenbank
            if check_export["export_bodenklassen"]:
                sql = """
                  INSERT INTO he.Bodenklasse
                  ( InfiltrationsrateAnfang, InfiltrationsrateEnde,
                    InfiltrationsrateStart, Rueckgangskonstante, Regenerationskonstante,
                    Saettigungswassergehalt, Name, LastModified, Kommentar,  Id)
                  SELECT
                    {infiltrationsrateanfang}, {infiltrationsrateende},
                    {infiltrationsratestart}, {rueckgangskonstante}, {regenerationskonstante},
                    {saettigungswassergehalt}, '{name}', '{lastmodified}', '{kommentar}', {id}
                    WHERE '{name}' NOT IN (SELECT Name FROM Bodenklasse);
                    """.format(
                    infiltrationsrateanfang=infiltrationsrateanfang,
                    infiltrationsrateende=infiltrationsrateende,
                    infiltrationsratestart=infiltrationsratestart,
                    rueckgangskonstante=rueckgangskonstante,
                    regenerationskonstante=regenerationskonstante,
                    saettigungswassergehalt=saettigungswassergehalt,
                    name=bknam,
                    lastmodified=createdat,
                    kommentar=kommentar,
                    id=nextid,
                )

                if not db_qkan.sql(sql, "db_qkan: export_bodenklassen (2)"):
                    return False

                nextid += 1

        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Bodenklassen eingefuegt".format(nextid - nr0), 0.62)
    # progress_bar.setValue(80)

    # --------------------------------------------------------------------------------------------
    # Export der Abflussparameter

    if (
        check_export["export_abflussparameter"]
        or check_export["modify_abflussparameter"]
    ):

        sql = """
            SELECT
                apnam,
                anfangsabflussbeiwert AS anfangsabflussbeiwert_t,
                endabflussbeiwert AS endabflussbeiwert_t,
                benetzungsverlust AS benetzungsverlust_t,
                muldenverlust AS muldenverlust_t,
                benetzung_startwert AS benetzung_startwert_t,
                mulden_startwert AS mulden_startwert_t,
                bodenklasse, kommentar, createdat
            FROM abflussparameter
            """

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_abflussparameter"):
            del db_qkan
            return False

        nr0 = nextid

        fortschritt("Export Abflussparameter...", 0.7)

        for attr in db_qkan.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (
                apnam,
                anfangsabflussbeiwert_t,
                endabflussbeiwert_t,
                benetzungsverlust_t,
                muldenverlust_t,
                benetzung_startwert_t,
                mulden_startwert_t,
                bodenklasse,
                kommentar,
                createdat_t,
            ) = ("NULL" if el is None else el for el in attr)

            # Formatierung der Zahlen
            (
                anfangsabflussbeiwert,
                endabflussbeiwert,
                benetzungsverlust,
                muldenverlust,
                benetzung_startwert,
                mulden_startwert,
            ) = (
                "NULL" if tt == "NULL" else "{:.2f}".format(float(tt))
                for tt in (
                    anfangsabflussbeiwert_t,
                    endabflussbeiwert_t,
                    benetzungsverlust_t,
                    muldenverlust_t,
                    benetzung_startwert_t,
                    mulden_startwert_t,
                )
            )

            # Standardwerte, falls keine Vorgaben
            if createdat_t == "NULL":
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            else:
                try:
                    if createdat_t.count(":") == 1:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M")
                    else:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M:%S")
                except:
                    createdat_s = time.localtime()
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", createdat_s)

            if bodenklasse == "NULL":
                typ = 0  # undurchlässig
                bodenklasse = ""
            else:
                typ = 1  # durchlässig

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export["modify_abflussparameter"]:
                sql = """
                  UPDATE AbflussParameter SET
                  AbflussbeiwertAnfang={anfangsabflussbeiwert},
                  AbflussbeiwertEnde={endabflussbeiwert}, Benetzungsverlust={benetzungsverlust},
                  Muldenverlust={muldenverlust}, BenetzungSpeicherStart={benetzung_startwert},
                  MuldenauffuellgradStart={mulden_startwert},
                  SpeicherkonstanteKonstant={speicherkonstantekonstant},
                  SpeicherkonstanteMin={speicherkonstantemin},
                  SpeicherkonstanteMax={speicherkonstantemax},
                  SpeicherkonstanteKonstant2={speicherkonstantekonstant2},
                  SpeicherkonstanteMin2={speicherkonstantemin2}, SpeicherkonstanteMax2={speicherkonstantemax2},
                  Bodenklasse='{bodenklasse}', CharakteristischeRegenspende={charakteristischeregenspende},
                  CharakteristischeRegenspende2={charakteristischeregenspende2},
                  Typ={typ}, JahresgangVerluste={jahresgangverluste}, LastModified='{createdat}',
                  Kommentar='{kommentar}'
                  WHERE Name = '{apnam}';
                """.format(
                    apnam=apnam,
                    anfangsabflussbeiwert=anfangsabflussbeiwert,
                    endabflussbeiwert=endabflussbeiwert,
                    benetzungsverlust=benetzungsverlust,
                    muldenverlust=muldenverlust,
                    benetzung_startwert=benetzung_startwert,
                    mulden_startwert=mulden_startwert,
                    speicherkonstantekonstant=1,
                    speicherkonstantemin=0,
                    speicherkonstantemax=0,
                    speicherkonstantekonstant2=1,
                    speicherkonstantemin2=0,
                    speicherkonstantemax2=0,
                    bodenklasse=bodenklasse,
                    charakteristischeregenspende=0,
                    charakteristischeregenspende2=0,
                    typ=typ,
                    jahresgangverluste=0,
                    createdat=createdat,
                    kommentar=kommentar,
                )

                if not db_qkan.sql(sql, "db_qkan: export_abflussparameter (1)"):
                    return False

            # Einfuegen in die Datenbank
            if check_export["export_abflussparameter"]:
                sql = """
                  INSERT INTO he.AbflussParameter
                  ( Name, AbflussbeiwertAnfang, AbflussbeiwertEnde, Benetzungsverlust,
                    Muldenverlust, BenetzungSpeicherStart, MuldenauffuellgradStart, SpeicherkonstanteKonstant,
                    SpeicherkonstanteMin, SpeicherkonstanteMax, SpeicherkonstanteKonstant2,
                    SpeicherkonstanteMin2, SpeicherkonstanteMax2,
                    Bodenklasse, CharakteristischeRegenspende, CharakteristischeRegenspende2,
                    Typ, JahresgangVerluste, LastModified, Kommentar, Id)
                  SELECT
                    '{apnam}', {anfangsabflussbeiwert}, {endabflussbeiwert}, {benetzungsverlust},
                    {muldenverlust}, {benetzung_startwert}, {mulden_startwert}, {speicherkonstantekonstant},
                    {speicherkonstantemin}, {speicherkonstantemax}, {speicherkonstantekonstant2},
                    {speicherkonstantemin2}, {speicherkonstantemax2},
                    '{bodenklasse}', {charakteristischeregenspende}, {charakteristischeregenspende2},
                    {typ}, {jahresgangverluste}, '{createdat}', '{kommentar}', {id}
                  WHERE '{apnam}' NOT IN (SELECT Name FROM AbflussParameter);
                """.format(
                    apnam=apnam,
                    anfangsabflussbeiwert=anfangsabflussbeiwert,
                    endabflussbeiwert=endabflussbeiwert,
                    benetzungsverlust=benetzungsverlust,
                    muldenverlust=muldenverlust,
                    benetzung_startwert=benetzung_startwert,
                    mulden_startwert=mulden_startwert,
                    speicherkonstantekonstant=1,
                    speicherkonstantemin=0,
                    speicherkonstantemax=0,
                    speicherkonstantekonstant2=1,
                    speicherkonstantemin2=0,
                    speicherkonstantemax2=0,
                    bodenklasse=bodenklasse,
                    charakteristischeregenspende=0,
                    charakteristischeregenspende2=0,
                    typ=typ,
                    jahresgangverluste=0,
                    createdat=createdat,
                    kommentar=kommentar,
                    id=nextid,
                )

                if not db_qkan.sql(sql, "db_qkan: export_abflussparameter (2)"):
                    return False

                nextid += 1

        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Abflussparameter eingefuegt".format(nextid - nr0), 0.65)
    # progress_bar.setValue(85)

    # ------------------------------------------------------------------------------------------------
    # Export der Regenschreiber
    #
    # Wenn in QKan keine Regenschreiber eingetragen sind, wird als Name "Regenschreiber1" angenommen.

    if check_export["export_regenschreiber"] or check_export["modify_regenschreiber"]:

        # # Pruefung, ob Regenschreiber fuer Export vorhanden
        # if len(liste_teilgebiete) != 0:
        #     auswahl = " AND flaechen.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        # else:
        #     auswahl = ""
        #
        # sql = "SELECT regenschreiber FROM flaechen GROUP BY regenschreiber{}".format(auswahl)

        # Regenschreiber berücksichtigen nicht ausgewählte Teilgebiete
        sql = """SELECT regenschreiber FROM flaechen GROUP BY regenschreiber"""

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_regenschreiber"):
            del db_qkan
            return False

        attr = db_qkan.fetchall()
        if attr == [(None,)]:
            reglis = tuple(["Regenschreiber1"])
            logger.debug(
                'In QKan war kein Regenschreiber vorhanden. "Regenschreiber1" ergänzt'
            )
        else:
            reglis = tuple([str(el[0]) for el in attr])
            logger.debug(
                "In QKan wurden folgende Regenschreiber referenziert: {}".format(
                    str(reglis)
                )
            )

        logger.debug("Regenschreiber - reglis: {}".format(str(reglis)))

        # Liste der fehlenden Regenschreiber in der Ziel- (*.idbf-) Datenbank
        # Hier muss eine Besonderheit von tuple berücksichtigt werden. Ein Tuple mit einem Element
        # endet mit ",)", z.B. (1,), während ohne oder bei mehr als einem Element alles wie üblich
        # ist: () oder (1,2,3,4)
        if len(reglis) == 1:
            sql = """SELECT Name FROM Regenschreiber WHERE Name NOT IN {})""".format(
                str(reglis)[:-2]
            )
        else:
            sql = """SELECT Name FROM Regenschreiber WHERE Name NOT IN {}""".format(
                str(reglis)
            )

        if not db_qkan.sql(sql, "db_qkan: export_regenschreiber (1)"):
            del db_qkan
            return False

        attr = db_qkan.fetchall()
        logger.debug("Regenschreiber - attr: {}".format(str(attr)))

        nr0 = nextid

        createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())

        regschnr = 1
        for regenschreiber in reglis:
            if regenschreiber not in attr:
                sql = """
                  INSERT INTO he.Regenschreiber
                  ( Nummer, Station,
                    ZKoordinate, Name,
                    FlaecheGesamt, FlaecheDurchlaessig, FlaecheUndurchlaessig,
                    AnzahlHaltungen, InterneNummer,
                    LastModified, Kommentar, Id) SELECT
                      {nummer}, '{station}',
                      {zkoordinate}, '{name}',
                      {flaechegesamt}, {flaechedurchlaessig}, {flaecheundurchlaessig},
                      {anzahlhaltungen}, {internenummer},
                      '{lastmodified}', '{kommentar}', {id}
                    WHERE '{name}' NOT IN (SELECT Name FROM Regenschreiber);
                  """.format(
                    nummer=regschnr,
                    station=10000 + regschnr,
                    zkoordinate=0,
                    name=regenschreiber,
                    flaechegesamt=0,
                    flaechedurchlaessig=0,
                    flaecheundurchlaessig=0,
                    anzahlhaltungen=0,
                    internenummer=0,
                    lastmodified=createdat,
                    kommentar="Ergänzt durch QKan",
                    id=nextid,
                )

                if not db_qkan.sql(sql, "db_qkan: export_regenschreiber (2)"):
                    return False

                logger.debug("In HE folgenden Regenschreiber ergänzt: {}".format(sql))

                nextid += 1
        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Regenschreiber eingefuegt".format(nextid - nr0), 0.68)
    # progress_bar.setValue(90)

    # ------------------------------------------------------------------------------------------------
    # Export der Flächen

    if (
        check_export["export_flaechenrw"]
        or check_export["modify_flaechenrw"]
        or export_flaechen_he8
    ):
        """
        Export der Flaechendaten

        Die Daten werden in max. drei Teilen nach HYSTEM-EXTRAN exportiert:
        1. Befestigte Flächen
        2.2 Unbefestigte Flächen

        Die Abflusseigenschaften werden über die Tabelle "abflussparameter" geregelt. Dort ist 
        im attribut bodenklasse nur bei unbefestigten Flächen ein Eintrag. Dies ist das Kriterium
        zur Unterscheidung

        undurchlässigen Flächen -------------------------------------------------------------------------------

        Es gibt in HYSTEM-EXTRAN 3 Flächentypen (BERECHNUNGSSPEICHERKONSTANTE):
        verwendete Parameter:    Anz_Sp  SpKonst.  Fz_SschwP  Fz_Oberfl  Fz_Kanal
        0 - direkt                 x       x
        1 - Fließzeiten                                          x          x
        2 - Schwerpunktfließzeit                       x

        In der QKan-Datenbank sind Fz_SschwP und Fz_oberfl zu einem Feld zusammengefasst (fliesszeitflaeche)

        Befestigte Flächen"""

        nr0 = 0  # Für Fortschrittsmeldung

        # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
        if not checknames(db_qkan, "flaechen", "flnam", "f_", autokorrektur):
            return False

        if not updatelinkfl(db_qkan, fangradius):
            fehlermeldung(
                "Fehler beim Update der Flächen-Verknüpfungen",
                "Der logische Cache konnte nicht aktualisiert werden.",
            )
            return False

        # Zu verschneidende zusammen mit nicht zu verschneidene Flächen exportieren

        # Nur Daten fuer ausgewaehlte Teilgebiete
        if len(liste_teilgebiete) != 0:
            # auswahl_c = " AND ha.teilgebiet in ('{}')".format(
            #     "', '".join(liste_teilgebiete)
            # )
            auswahl_a = " WHERE ha.teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl_a = ""

        # Verschneidung nur, wenn (mit_verschneidung)
        if mit_verschneidung:
            case_verschneidung = "fl.aufteilen IS NULL or fl.aufteilen <> 'ja'"
            join_verschneidung = """
                LEFT JOIN tezg AS tg
                ON lf.tezgnam = tg.flnam"""
            expr_verschneidung = """CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3))"""
        else:
            case_verschneidung = "1"
            join_verschneidung = ""
            expr_verschneidung = "fl.geom"  # dummy

        # Einfuegen der Flächendaten in die QKan-Datenbank, Tabelle "flaechen_he8"

        if export_flaechen_he8:

            logger.debug("Export flaechen_he8 aktiviert")

            # Vorbereitung: Leeren der Tabelle "flaechen_he8"

            sql = "DELETE FROM flaechen_he8"
            if not db_qkan.sql(sql, "dbQK: k_qkhe.exportFlaechenHE8.delete"):
                del db_qkan
                return False

            # Einfügen aller verschnittenen Flächen in Tabelle "flaechen_he8", zusammengefasst
            # nach Haltungen, Regenschreiber, etc.

            sql = """
            WITH flintersect AS (
              SELECT 
                substr(printf('%s-%d', fl.flnam, lf.pk),1,30) AS flnam, 
                ha.haltnam AS haltnam, fl.neigkl AS neigkl,
                at.he_nr AS abflusstyp, 
                CASE WHEN ap.bodenklasse IS NULL THEN 0 ELSE 1 END AS typbef, 
                lf.speicherzahl AS speicherzahl, lf.speicherkonst AS speicherkonst,
                lf.fliesszeitflaeche AS fliesszeitflaeche, lf.fliesszeitkanal AS fliesszeitkanal,
                CASE WHEN {case_verschneidung} THEN area(fl.geom)/10000 
                ELSE area({expr_verschneidung})/10000 
                END AS flaeche, 
                fl.regenschreiber AS regenschreiber, coalesce(ft.he_nr, 0) AS flaechentypnr, 
                fl.abflussparameter AS abflussparameter, fl.createdat AS createdat,
                fl.kommentar AS kommentar,
                CASE WHEN {case_verschneidung} THEN fl.geom
                ELSE {expr_verschneidung} 
                END AS geom
              FROM linkfl AS lf
              INNER JOIN flaechen AS fl
              ON lf.flnam = fl.flnam
              INNER JOIN haltungen AS ha
              ON lf.haltnam = ha.haltnam
              LEFT JOIN abflusstypen AS at
              ON lf.abflusstyp = at.abflusstyp
              LEFT JOIN abflussparameter AS ap
              ON fl.abflussparameter = ap.apnam
              LEFT JOIN flaechentypen AS ft
              ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl_a})
            INSERT INTO flaechen_he8 (
              Name, Haltung, Groesse, Regenschreiber, Flaechentyp, 
              BerechnungSpeicherkonstante, Typ, AnzahlSpeicher,
              Speicherkonstante, 
              Schwerpunktlaufzeit,
              FliesszeitOberflaeche, LaengsteFliesszeitKanal,
              Parametersatz, Neigungsklasse, ZuordnUnabhEZG, 
              IstPolygonalflaeche, ZuordnungGesperrt, 
              LastModified,
              Kommentar, 
              Geometry)
            SELECT 
              flnam AS Name, haltnam AS Haltung, flaeche AS Groesse, regenschreiber AS Regenschreiber, 
              flaechentypnr AS Flaechentyp, 
              abflusstyp AS BerechnungSpeicherkonstante, typbef AS Typ, speicherzahl AS AnzahlSpeicher, 
              speicherkonst AS Speicherkonstante, 
              coalesce(fliesszeitflaeche, 0.0) AS Schwerpunktlaufzeit, 
              fliesszeitflaeche AS FliesszeitOberflaeche, fliesszeitkanal AS LaengsteFliesszeitKanal, 
              abflussparameter AS Parametersatz, neigkl AS Neigungsklasse, 
              1 AS IstPolygonalflaeche, 1 AS ZuordnungGesperrt, 0 AS ZuordnUnabhEZG, 
              strftime('%Y-%m-%d %H:%M:%S', coalesce(createdat, 'now')) AS lastmodified, 
              kommentar AS Kommentar, 
              SetSrid(geom, -1) AS Geometry
            FROM flintersect AS fi
            WHERE flaeche*10000 > {mindestflaeche}""".format(
                mindestflaeche=mindestflaeche,
                auswahl_a=auswahl_a,
                case_verschneidung=case_verschneidung,
                join_verschneidung=join_verschneidung,
                expr_verschneidung=expr_verschneidung,
            )

            logger.debug(
                "Abfrage zum Export der Flächendaten nach HE8: \n{}".format(sql)
            )

            if not db_qkan.sql(sql, "dbQK: k_qkhe.export_flaechenhe8"):
                return False

        if check_export["modify_flaechenrw"]:

            # aus Performancegründen wird die Auswahl der zu bearbeitenden Flächen in eine
            # temporäre Tabelle tempfl geschrieben
            sqllis = (
                """CREATE TEMP TABLE IF NOT EXISTS flupdate (flnam TEXT)""",
                """DELETE FROM flupdate"""
                f"""
                    INSERT INTO flupdate (flnam)
                      SELECT substr(printf('%s-%d', fl.flnam, lf.pk),1,30) AS flnam 
                      FROM linkfl AS lf
                      INNER JOIN flaechen AS fl
                      ON lf.flnam = fl.flnam
                      INNER JOIN haltungen AS ha
                      ON lf.haltnam = ha.haltnam
                      LEFT JOIN abflusstypen AS at
                      ON lf.abflusstyp = at.abflusstyp
                      LEFT JOIN abflussparameter AS ap
                      ON fl.abflussparameter = ap.apnam
                      LEFT JOIN flaechentypen AS ft
                      ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl_a}""",
                """
                    WITH flintersect AS (
                      SELECT substr(printf('%s-%d', fl.flnam, lf.pk),1,30) AS flnam, 
                        ha.haltnam AS haltnam, fl.neigkl AS neigkl,
                        at.he_nr AS abflusstyp, 
                        CASE WHEN ap.bodenklasse IS NULL THEN 0 ELSE 1 END AS typbef, 
                        lf.speicherzahl AS speicherzahl, lf.speicherkonst AS speicherkonst,
                        lf.fliesszeitflaeche AS fliesszeitflaeche, lf.fliesszeitkanal AS fliesszeitkanal,
                        CASE WHEN {case_verschneidung} THEN area(fl.geom)/10000 
                        ELSE area({expr_verschneidung})/10000 
                        END AS flaeche, 
                        fl.regenschreiber AS regenschreiber,
                        coalesce(ft.he_nr, 0) AS flaechentypnr, 
                        fl.abflussparameter AS abflussparameter, fl.createdat AS createdat,
                        fl.kommentar AS kommentar,
                        CASE WHEN {case_verschneidung} THEN fl.geom
                        ELSE {expr_verschneidung} 
                        END AS geom
                      FROM linkfl AS lf
                      INNER JOIN flaechen AS fl
                      ON lf.flnam = fl.flnam
                      INNER JOIN haltungen AS ha
                      ON lf.haltnam = ha.haltnam
                      LEFT JOIN abflusstypen AS at
                      ON lf.abflusstyp = at.abflusstyp
                      LEFT JOIN abflussparameter AS ap
                      ON fl.abflussparameter = ap.apnam
                      LEFT JOIN flaechentypen AS ft
                      ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl_a})
                    UPDATE he.Flaeche SET (
                      Haltung, Groesse, Regenschreiber, Flaechentyp, 
                      BerechnungSpeicherkonstante, Typ, AnzahlSpeicher,
                      Speicherkonstante, 
                      Schwerpunktlaufzeit,
                      FliesszeitOberflaeche, LaengsteFliesszeitKanal,
                      Parametersatz, Neigungsklasse, 
                      LastModified,
                      Kommentar, 
                      Geometry) = 
                    ( SELECT 
                        haltnam AS Haltung, flaeche AS Groesse, regenschreiber AS Regenschreiber, 
                        flaechentypnr AS Flaechentyp, 
                        abflusstyp AS BerechnungSpeicherkonstante, typbef AS Typ, speicherzahl AS AnzahlSpeicher, 
                        speicherkonst AS Speicherkonstante, 
                        coalesce(fliesszeitflaeche, 0.0) AS Schwerpunktlaufzeit, 
                        fliesszeitflaeche AS FliesszeitOberflaeche, fliesszeitkanal AS LaengsteFliesszeitKanal, 
                        abflussparameter AS Parametersatz, neigkl AS Neigungsklasse, 
                        coalesce(createdat, strftime('%Y-%m-%d %H:%M:%S','now')) AS lastmodified, 
                        kommentar AS Kommentar, 
                        SetSrid(geom, -1) AS geometry
                      FROM flintersect AS fi
                      WHERE flnam = he.Flaeche.Name and flaeche*10000 > {mindestflaeche} and flaeche IS NOT NULL
                    ) WHERE he.Flaeche.Name IN (SELECT flnam FROM flupdate)
                    """.format(
                    mindestflaeche=mindestflaeche,
                    auswahl_a=auswahl_a,
                    case_verschneidung=case_verschneidung,
                    join_verschneidung=join_verschneidung,
                    expr_verschneidung=expr_verschneidung,
                ),
            )

            for sql in sqllis:
                if not db_qkan.sql(sql, "dbQK: export_to_he8.export_flaechenrw (1)"):
                    return False

        if check_export["export_flaechenrw"]:

            # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
            sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM linkfl"
            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_haltungen (2)"):
                return False

            data = db_qkan.fetchone()
            if len(data) == 2:
                idmin, idmax = data
                logger.debug(f"idmin = {idmin}\nidmax = {idmax}\n")
            else:
                fehlermeldung(
                    "Fehler (35) in QKan_Export",
                    f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                )

            if idmin is None:
                meldung("Einfügen Flächen", "Keine Flächen zum Einfügen gefunden")
            else:
                nr0 = nextid
                id0 = nextid - idmin

                sql = """
                WITH flintersect AS (
                  SELECT
                    lf.rowid + {id0} AS id, 
                    substr(printf('%s-%d', fl.flnam, lf.pk),1,30) AS flnam, 
                    ha.haltnam AS haltnam, fl.neigkl AS neigkl,
                    at.he_nr AS abflusstyp, 
                    CASE WHEN ap.bodenklasse IS NULL THEN 0 ELSE 1 END AS typbef, 
                    lf.speicherzahl AS speicherzahl, lf.speicherkonst AS speicherkonst,
                    lf.fliesszeitflaeche AS fliesszeitflaeche, lf.fliesszeitkanal AS fliesszeitkanal,
                    CASE WHEN {case_verschneidung} THEN area(fl.geom)/10000 
                    ELSE area({expr_verschneidung})/10000 
                    END AS flaeche, 
                    fl.regenschreiber AS regenschreiber, coalesce(ft.he_nr, 0) AS flaechentypnr, 
                    fl.abflussparameter AS abflussparameter, fl.createdat AS createdat,
                    fl.kommentar AS kommentar,
                    CASE WHEN {case_verschneidung} THEN fl.geom
                    ELSE {expr_verschneidung} 
                    END AS geom
                  FROM linkfl AS lf
                  INNER JOIN flaechen AS fl
                  ON lf.flnam = fl.flnam
                  INNER JOIN haltungen AS ha
                  ON lf.haltnam = ha.haltnam
                  LEFT JOIN abflusstypen AS at
                  ON lf.abflusstyp = at.abflusstyp
                  LEFT JOIN abflussparameter AS ap
                  ON fl.abflussparameter = ap.apnam
                  LEFT JOIN flaechentypen AS ft
                  ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl_a})
                INSERT INTO he.Flaeche (
                  id, 
                  Name, Haltung, Groesse, Regenschreiber, Flaechentyp, 
                  BerechnungSpeicherkonstante, Typ, AnzahlSpeicher,
                  Speicherkonstante, 
                  Schwerpunktlaufzeit,
                  FliesszeitOberflaeche, LaengsteFliesszeitKanal,
                  Parametersatz, Neigungsklasse, ZuordnUnabhEZG, 
                  IstPolygonalflaeche, ZuordnungGesperrt, 
                  LastModified,
                  Kommentar, 
                  Geometry)
                SELECT 
                  id AS id, 
                  flnam AS Name, haltnam AS Haltung, flaeche AS Groesse, regenschreiber AS Regenschreiber, 
                  flaechentypnr AS Flaechentyp, 
                  abflusstyp AS BerechnungSpeicherkonstante, typbef AS Typ, speicherzahl AS AnzahlSpeicher, 
                  speicherkonst AS Speicherkonstante, 
                  coalesce(fliesszeitflaeche, 0.0) AS Schwerpunktlaufzeit, 
                  fliesszeitflaeche AS FliesszeitOberflaeche, fliesszeitkanal AS LaengsteFliesszeitKanal, 
                  abflussparameter AS Parametersatz, neigkl AS Neigungsklasse, 
                  1 AS IstPolygonalflaeche, 1 AS ZuordnungGesperrt, 0 AS ZuordnUnabhEZG, 
                  strftime('%Y-%m-%d %H:%M:%S', coalesce(createdat, 'now')) AS lastmodified, 
                  kommentar AS Kommentar, 
                  SetSrid(geom, -1) AS geometry
                FROM flintersect AS fi
                WHERE flaeche*10000 > {mindestflaeche} and (flnam NOT IN (SELECT Name FROM he.Flaeche))""".format(
                    mindestflaeche=mindestflaeche,
                    auswahl_a=auswahl_a,
                    case_verschneidung=case_verschneidung,
                    join_verschneidung=join_verschneidung,
                    expr_verschneidung=expr_verschneidung,
                    id0=id0,
                )

                if not db_qkan.sql(sql, "dbQK: export_to_he8.export_flaechenrw (2)"):
                    return False

                nextid += idmax - idmin + 1
                db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {nextid}")
        db_qkan.commit()

        if nr0:
            fortschritt("{} Flaechen eingefuegt".format(nextid - nr0), 0.80)

    # progress_bar.setValue(90)

    # ------------------------------------------------------------------------------------------------
    # Export der Direkteinleitungen

    if check_export["export_einleitdirekt"] or check_export["modify_einleitdirekt"]:
        # Herkunft = 1 (Direkt) und 3 (Einwohnerbezogen)

        """
        Bearbeitung in QKan: Vervollständigung der Einzugsgebiete

        Prüfung der vorliegenden Einzugsgebiete in QKan
        ============================================
        Zunächst eine grundsätzliche Anmerkung: In HE gibt es keine Einzugsgebiete in der Form, wie sie
        in QKan vorhanden sind. Diese werden (nur) in QKan verwendet, um für die Variante 
        Herkunft = 3 die Grundlagendaten
         - einwohnerspezifischer Schmutzwasseranfall
         - Fremdwasseranteil
         - Stundenmittel
        zu verwalten.

        Aus diesem Grund werden vor dem Export der Einzeleinleiter diese Daten geprüft:

        1 Wenn in QKan keine Einzugsgebiete vorhanden sind, wird zunächst geprüft, ob die
           Einwohnerpunkte einem (noch nicht angelegten) Einzugsgebiet zugeordnet sind.
           1.1 Kein Einwohnerpunkt ist einem Einzugsgebiet zugeordnet. Dann wird ein Einzugsgebiet "Einzugsgebiet1" 
               angelegt und alle Einwohnerpunkte diesem Einzugsgebiet zugeordnet
           1.2 Die Einwohnerpunkte sind einem oder mehreren noch nicht in der Tabelle "einzugsgebiete" vorhandenen 
               Einzugsgebieten zugeordnet. Dann werden entsprechende Einzugsgebiete mit Standardwerten angelegt.
        2 Wenn in QKan Einzugsgebiete vorhanden sind, wird geprüft, ob es auch Einwohnerpunkte gibt, die diesen
           Einzugsgebieten zugeordnet sind.
           2.1 Es gibt keine Einwohnerpunkte, die einem Einzugsgebiet zugeordnet sind.
               2.1.1 Es gibt in QKan genau ein Einzugsgebiet. Dann werden alle Einwohnerpunkte diesem Einzugsgebiet
                     zugeordnet.
               2.1.2 Es gibt in QKan mehrere Einzugsgebiete. Dann werden alle Einwohnerpunkte geographisch dem
                     betreffenden Einzugsgebiet zugeordnet.
           2.2 Es gibt mindestens einen Einwohnerpunkt, der einem Einzugsgebiet zugeordnet ist.
               Dann wird geprüft, ob es noch nicht zugeordnete Einwohnerpunkte gibt, eine Warnung angezeigt und
               diese Einwohnerpunkte aufgelistet.
        """

        sql = "SELECT count(*) AS anz FROM einzugsgebiete"

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_einzugsgebiete (1)"):
            del db_qkan
            return False

        anztgb = int(db_qkan.fetchone()[0])
        if anztgb == 0:
            # 1 Kein Einzugsgebiet in QKan -----------------------------------------------------------------
            createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())

            sql = """
                SELECT count(*) AS anz FROM einleit WHERE
                (einzugsgebiet is not NULL) AND
                (einzugsgebiet <> 'NULL') AND
                (einzugsgebiet <> '')
            """

            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_einzugsgebiete (2)"):
                del db_qkan
                return False

            anz = int(db_qkan.fetchone()[0])
            if anz == 0:
                # 1.1 Kein Einwohnerpunkt mit Einzugsgebiet ----------------------------------------------------
                sql = """
                   INSERT INTO einzugsgebiete
                   ( tgnam, ewdichte, wverbrauch, stdmittel,
                     fremdwas, createdat, kommentar)
                   Values
                   ( 'einzugsgebiet1', 60, 120, 14, 100, '{createdat}',
                     'Automatisch durch  QKan hinzugefuegt')""".format(
                    createdat=createdat
                )

                if not db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_einzugsgebiete (3)"
                ):
                    del db_qkan
                    return False

                db_qkan.commit()
            else:
                # 1.2 Einwohnerpunkte mit Einzugsgebiet ----------------------------------------------------
                # Liste der in allen Einwohnerpunkten vorkommenden Einzugsgebiete
                sql = """SELECT einzugsgebiet FROM einleit WHERE einzugsgebiet is not NULL GROUP BY einzugsgebiet"""

                if not db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_einzugsgebiete (4)"
                ):
                    del db_qkan
                    return False

                listeilgeb = db_qkan.fetchall()
                for tgb in listeilgeb:
                    sql = """
                       INSERT INTO einzugsgebiete
                       ( tgnam, ewdichte, wverbrauch, stdmittel,
                         fremdwas, createdat, kommentar)
                       Values
                       ( '{tgnam}', 60, 120, 14, 100, '{createdat}',
                         'Hinzugefuegt aus QKan')""".format(
                        tgnam=tgb[0], createdat=createdat
                    )

                    if not db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_einzugsgebiete (5)"
                    ):
                        del db_qkan
                        return False

                    db_qkan.commit()
                    meldung(
                        "Tabelle 'einzugsgebiete':\n",
                        "Es wurden {} Einzugsgebiete hinzugefügt".format(len(tgb)),
                    )

                # Kontrolle mit Warnung
                sql = """
                    SELECT count(*) AS anz
                    FROM einleit
                    LEFT JOIN einzugsgebiete ON einleit.einzugsgebiet = einzugsgebiete.tgnam
                    WHERE einzugsgebiete.pk IS NULL
                """

                if not db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_einzugsgebiete (6)"
                ):
                    del db_qkan
                    return False

                anz = int(db_qkan.fetchone()[0])
                if anz > 0:
                    meldung(
                        "Fehlerhafte Daten in Tabelle 'einleit':",
                        "{} Einleitpunkte sind keinem Einzugsgebiet zugeordnet".format(
                            anz
                        ),
                    )
        else:
            # 2 Einzugsgebiete in QKan ----------------------------------------------------
            sql = """
                SELECT count(*) AS anz
                FROM einleit
                INNER JOIN einzugsgebiete ON einleit.einzugsgebiet = einzugsgebiete.tgnam
            """

            if not db_qkan.sql(sql, "dbQK: export_to_he8.export_einzugsgebiete (7)"):
                del db_qkan
                return False

            anz = int(db_qkan.fetchone()[0])
            if anz == 0:
                # 2.1 Keine Einleitpunkte mit Einzugsgebiet ----------------------------------------------------
                if anztgb == 1:
                    # 2.1.1 Es existiert genau ein Einzugsgebiet ---------------------------------------------
                    sql = """UPDATE einleit SET einzugsgebiet = (SELECT tgnam FROM einzugsgebiete GROUP BY tgnam)"""

                    if not db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_einzugsgebiete (8)"
                    ):
                        del db_qkan
                        return False

                    db_qkan.commit()
                    meldung(
                        "Tabelle 'einleit':\n",
                        "Alle Einleitpunkte in der Tabelle 'einleit' wurden einem Einzugsgebiet zugeordnet",
                    )
                else:
                    # 2.1.2 Es existieren mehrere Einzugsgebiete ------------------------------------------
                    sql = """UPDATE einleit SET einzugsgebiet = (SELECT tgnam FROM einzugsgebiete
                          WHERE within(einleit.geom, einzugsgebiete.geom) 
                              and einleit.geom IS NOT NULL and einzugsgebiete.geom IS NOT NULL)"""

                    if not db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_einzugsgebiete (9)"
                    ):
                        del db_qkan
                        return False

                    db_qkan.commit()
                    meldung(
                        "Tabelle 'einleit':\n",
                        "Alle Einleitpunkte in der Tabelle 'einleit' wurden dem Einzugsgebiet zugeordnet, in dem sie liegen.",
                    )

                    # Kontrolle mit Warnung
                    sql = """
                        SELECT count(*) AS anz
                        FROM einleit
                        LEFT JOIN einzugsgebiete ON einleit.einzugsgebiet = einzugsgebiete.tgnam
                        WHERE einzugsgebiete.pk IS NULL
                    """
                    if not db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_einzugsgebiete (10)"
                    ):
                        del db_qkan
                        return False

                    anz = int(db_qkan.fetchone()[0])
                    if anz > 0:
                        meldung(
                            "Fehlerhafte Daten in Tabelle 'einleit':",
                            "{} Einleitpunkte sind keinem Einzugsgebiet zugeordnet".format(
                                anz
                            ),
                        )
            else:
                # 2.2 Es gibt Einleitpunkte mit zugeordnetem Einzugsgebiet
                # Kontrolle mit Warnung
                sql = """
                    SELECT count(*) AS anz
                    FROM einleit
                    LEFT JOIN einzugsgebiete ON einleit.einzugsgebiet = einzugsgebiete.tgnam
                    WHERE einzugsgebiete.pk is NULL
                """

                if not db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_einzugsgebiete (11)"
                ):
                    del db_qkan
                    return False

                anz = int(db_qkan.fetchone()[0])
                if anz > 0:
                    meldung(
                        "Fehlerhafte Daten in Tabelle 'einleit':",
                        "{} Einleitpunkte sind keinem Einzugsgebiet zugeordnet".format(
                            anz
                        ),
                    )

        # --------------------------------------------------------------------------------------------
        # Export der Einzeleinleiter aus Schmutzwasser
        #
        # Referenzlisten (HE 7.8):
        #
        # ABWASSERART (Im Formular "Art"):
        #    0 = Häuslich
        #    1 = Gewerblich
        #    2 = Industriell
        #    5 = Regenwasser
        #
        # HERKUNFT (Im Formular "Herkunft"):
        #    0 = Siedlungstyp
        #    1 = Direkt
        #    2 = Frischwasserverbrauch
        #    3 = Einwohner
        #

        # HERKUNFT = 1 (Direkt) wird aus einer eigenen Tabelle "einleiter" erzeugt und ebenfalls in die
        # HE-Tabelle "Einzeleinleiter" übertragen
        #
        # HERKUNFT = 2 (Frischwasserverbrauch) ist zurzeit nicht realisiert
        #
        # Herkunft = 3 (Einwohner).
        # Nur die Flächen werden berücksichtigt, die einem Einzugsgebiet
        # mit Wasserverbrauch zugeordnet sind.

        # Vorbereitung einleit: Falls elnam leer ist, plausibel ergänzen:

        if not checknames(db_qkan, "einleit", "elnam", "e_", autokorrektur):
            del db_qkan
            del db_qkan
            return False

        if not updatelinksw(db_qkan, fangradius):
            del db_qkan  # Im Fehlerfall wird dbQK in updatelinksw geschlossen.
            fehlermeldung(
                "Fehler beim Update der Einzeleinleiter-Verknüpfungen",
                "Der logische Cache konnte nicht aktualisiert werden.",
            )

        # Nur Daten fuer ausgewaehlte Teilgebiete

        if len(liste_teilgebiete) != 0:
            auswahl = " and teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        else:
            auswahl = ""

        sql = """SELECT
          elnam,
          haltnam AS haltnam,
          NULL AS wverbrauch, 
          NULL AS stdmittel,
          NULL AS fremdwas, 
          NULL AS einwohner,
          zufluss AS zuflussdirekt, 
          1 AS herkunft,
          einleit.createdat AS createdat,
          geom
          FROM einleit
          WHERE zufluss IS NOT NULL {auswahl}
      UNION
          SELECT
          el.elnam AS elnam,
          el.haltnam AS haltnam,
          tg.wverbrauch AS wverbrauch, 
          tg.stdmittel AS stdmittel,
          tg.fremdwas AS fremdwas, 
          el.ew AS einwohner,
          NULL AS zuflussdirekt, 
          3 AS herkunft,
          el.createdat AS createdat,
          geom
          FROM einleit AS el
          INNER JOIN einzugsgebiete AS tg
          ON el.einzugsgebiet = tg.tgnam 
          WHERE zufluss IS NULL {auswahl}
        """.format(
            auswahl=auswahl
        )

        logger.debug("\nSQL-4e:\n{}\n".format(sql))

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_einleitdirekt (6)"):
            del db_qkan
            return False

        nr0 = nextid

        fortschritt("Export Einzeleinleiter (direkt)...", 0.92)

        # Varianten abhängig von HE-Version
        if versionolder(he_db_version[0:2], [7, 9], 2):
            logger.debug("Version vor 7.9 erkannt")
            fieldsnew = ""
            attrsnew = ""
            valuesnew = ""
        else:
            logger.debug("Version 7.9 erkannt")
            fieldsnew = ", ZUFLUSSOBERERSchacht = 0"
            attrsnew = ", ZUFLUSSOBERERSchacht"
            valuesnew = ", 0"

        for b in db_qkan.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (
                elnam,
                haltnam,
                wverbrauch,
                stdmittel,
                fremdwas,
                einwohner,
                zuflussdirekt,
                herkunft,
                createdat_t,
                geom,
            ) = ("NULL" if el is None else el for el in b)

            if createdat_t == "NULL":
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            else:
                try:
                    if createdat_t.count(":") == 1:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M")
                    else:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M:%S")
                except:
                    createdat_s = time.localtime()
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", createdat_s)

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export["modify_einleitdirekt"]:
                sql = """
                    UPDATE Einzeleinleiter SET
                    ZuordnungGesperrt={zuordnunggesperrt}, 
                    ZuordnUnabhEZG={zuordnunabhezg}, Rohr='{haltnam}',
                    Abwasserart={abwasserart}, Einwohner={einwohner}, Wasserverbrauch={wverbrauch}, 
                    Herkunft={herkunft},
                    Stundenmittel={stdmittel}, Fremdwasserzuschlag={fremdwas}, Faktor={faktor}, 
                    Gesamtflaeche={flaeche},
                    ZuflussModell={zuflussmodell}, ZuflussDirekt={zuflussdirekt}, 
                    Zufluss={zufluss}, Planungsstatus={planungsstatus},
                    Abrechnungszeitraum={abrechnungszeitraum}, Abzug={abzug},
                    LastModified='{createdat}',Geometry='{geom}'{fieldsnew}
                    WHERE Name='{elnam}';
                    """.format(
                    zuordnunggesperrt=0,
                    zuordnunabhezg=1,
                    haltnam=haltnam,
                    abwasserart=0,
                    einwohner=einwohner,
                    wverbrauch=wverbrauch,
                    herkunft=herkunft,
                    stdmittel=stdmittel,
                    fremdwas=fremdwas,
                    faktor=1,
                    flaeche=0,
                    zuflussmodell=0,
                    zuflussdirekt=zuflussdirekt,
                    zufluss=0,
                    planungsstatus=0,
                    elnam=elnam[:27],
                    abrechnungszeitraum=365,
                    abzug=0,
                    createdat=createdat,
                    geom=geom,
                    fieldsnew=fieldsnew,
                )

                if not db_qkan.sql(sql, "db_qkan: export_einleitdirekt (1)"):
                    return False

            # Einfuegen in die Datenbank
            if check_export["export_einleitdirekt"]:
                sql = """
                  INSERT INTO he.Einzeleinleiter
                  ( ZuordnungGesperrt, ZuordnUnabhEZG, Rohr,
                    Abwasserart, Einwohner, Wasserverbrauch, Herkunft,
                    Stundenmittel, Fremdwasserzuschlag, Faktor, Gesamtflaeche,
                    ZuflussModell, ZuflussDirekt, Zufluss, Planungsstatus, Name,
                    Abrechnungszeitraum, Abzug,
                    LastModified, Id, Geometry{attrsnew}) 
                  SELECT
                    xel, yel, {zuordnunggesperrt}, {zuordnunabhezg}, '{haltnam}',
                    {abwasserart}, {einwohner}, {wverbrauch}, {herkunft},
                    {stdmittel}, {fremdwas}, {faktor}, {flaeche},
                    {zuflussmodell}, {zuflussdirekt}, {zufluss}, {planungsstatus}, '{elnam}',
                    {abrechnungszeitraum}, {abzug},
                    '{createdat}', {nextid}, Geometry='{geom}'{valuesnew}
                  WHERE '{elnam}' NOT IN (SELECT Name FROM Einzeleinleiter);
              """.format(
                    zuordnunggesperrt=0,
                    zuordnunabhezg=1,
                    haltnam=haltnam,
                    abwasserart=0,
                    einwohner=einwohner,
                    wverbrauch=wverbrauch,
                    herkunft=herkunft,
                    stdmittel=stdmittel,
                    fremdwas=fremdwas,
                    faktor=1,
                    flaeche=0,
                    zuflussmodell=0,
                    zuflussdirekt=zuflussdirekt,
                    zufluss=0,
                    planungsstatus=0,
                    elnam=elnam[:27],
                    abrechnungszeitraum=365,
                    abzug=0,
                    createdat=createdat,
                    nextid=nextid,
                    geom=geom,
                    attrsnew=attrsnew,
                    valuesnew=valuesnew,
                )

                if not db_qkan.sql(sql, "db_qkan: export_einleitdirekt (2)"):
                    return False

                nextid += 1

        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Einzeleinleiter (direkt) eingefuegt".format(nextid - nr0), 0.95)

    # ------------------------------------------------------------------------------------------------
    # Export der Aussengebiete

    if check_export["export_aussengebiete"] or check_export["modify_aussengebiete"]:

        # Aktualisierung der Anbindungen, insbesondere wird der richtige Schacht in die
        # Tabelle "aussengebiete" eingetragen.

        if not updatelinkageb(db_qkan, fangradius):
            del db_qkan  # Im Fehlerfall wird dbQK in updatelinkageb geschlossen.
            fehlermeldung(
                "Fehler beim Update der Außengebiete-Verknüpfungen",
                "Der logische Cache konnte nicht aktualisiert werden.",
            )

        # Nur Daten fuer ausgewaehlte Teilgebiete

        if len(liste_teilgebiete) != 0:
            auswahl = " WHERE teilgebiet in ('{}')".format(
                "', '".join(liste_teilgebiete)
            )
        else:
            auswahl = ""

        sql = """SELECT
          gebnam,
          x(centroid(geom)) AS xel,
          y(centroid(geom)) AS yel,
          schnam,
          hoeheob, 
          hoeheun, 
          fliessweg, 
          area(geom)/10000 AS gesflaeche, 
          basisabfluss, 
          cn, 
          regenschreiber, 
          kommentar, 
          createdat
          FROM aussengebiete{auswahl}
        """.format(
            auswahl=auswahl
        )

        logger.debug("\nSQL-4e:\n{}\n".format(sql))

        if not db_qkan.sql(sql, "dbQK: export_to_he8.export_aussengebiete (6)"):
            del db_qkan
            return False

        nr0 = nextid

        fortschritt("Export Außengebiete...", 0.92)
        for b in db_qkan.fetchall():

            # In allen Feldern None durch NULL ersetzen
            (
                gebnam,
                xel,
                yel,
                schnam,
                hoeheob,
                hoeheun,
                fliessweg,
                gesflaeche,
                basisabfluss,
                cn,
                regenschreiber,
                kommentar,
                createdat_t,
            ) = ("NULL" if el is None else el for el in b)

            if createdat_t == "NULL":
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            else:
                try:
                    if createdat_t.count(":") == 1:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M")
                    else:
                        createdat_s = time.strptime(createdat_t, "%d.%m.%Y %H:%M:%S")
                except:
                    createdat_s = time.localtime()
                createdat = time.strftime("%d.%m.%Y %H:%M:%S", createdat_s)

            # Ändern vorhandener Datensätze (geschickterweise vor dem Einfügen!)
            if check_export["modify_aussengebiete"]:
                sql = """
                    UPDATE Aussengebiet SET
                    Name='{gebnam}', Schacht='{schnam}', HoeheOben={hoeheob}, 
                    HoeheUnten={hoeheun}, 
                    Gesamtflaeche={gesflaeche}, CNMittelwert={cn}, BasisZufluss={basisabfluss}, 
                    FliessLaenge={fliessweg}, Verfahren={verfahren}, Regenschreiber='{regenschreiber}', 
                    LastModified='{createdat}', Kommentar='{kommentar}', 
                    Geometry=MakePoint({xel}, {yel})
                    WHERE Name='{gebnam}';
                    """.format(
                    gebnam=gebnam,
                    schnam=schnam,
                    hoeheob=hoeheob,
                    hoeheun=hoeheun,
                    xel=xel,
                    yel=yel,
                    gesflaeche=gesflaeche,
                    cn=cn,
                    basisabfluss=basisabfluss,
                    fliessweg=fliessweg,
                    verfahren=0,
                    regenschreiber=regenschreiber,
                    createdat=createdat,
                    kommentar=kommentar,
                )

                if not db_qkan.sql(sql, "db_qkan: export_aussengebiete (1)"):
                    return False

                sql = """
                    UPDATE Tabelleninhalte 
                    SET KeyWert = {cn}, Wert = {gesflaeche}
                    WHERE Id = (SELECT Id FROM Aussengebiet WHERE Name = '{gebnam}')
                    """.format(
                    cn=cn, gesflaeche=gesflaeche, gebnam=gebnam
                )

                if not db_qkan.sql(sql, "db_qkan: export_aussengebiete (2)"):
                    return False

            # Einfuegen in die Datenbank
            if check_export["export_aussengebiete"]:
                sql = """
                    INSERT INTO he.Aussengebiet
                    ( Name, Schacht, HoeheOben, HoeheUnten, 
                      Gesamtflaeche, CNMittelwert, BasisZufluss, 
                      FliessLaenge, Verfahren, Regenschreiber, 
                      LastModified, Kommentar, Id, Geometry) 
                    SELECT
                      '{gebnam}', '{schnam}', {hoeheob}, {hoeheun}, 
                      {gesflaeche}, {cn}, {basisabfluss}, 
                      {fliessweg}, {verfahren}, '{regenschreiber}', 
                      '{createdat}', '{kommentar}', {nextid}, MakePoint({xel}, {yel})
                    WHERE '{gebnam}' NOT IN (SELECT Name FROM Aussengebiet);
                    """.format(
                    gebnam=gebnam,
                    schnam=schnam,
                    hoeheob=hoeheob,
                    hoeheun=hoeheun,
                    xel=xel,
                    yel=yel,
                    gesflaeche=gesflaeche,
                    cn=cn,
                    basisabfluss=basisabfluss,
                    fliessweg=fliessweg,
                    verfahren=0,
                    regenschreiber=regenschreiber,
                    createdat=createdat,
                    kommentar=kommentar,
                    nextid=nextid,
                )

                if not db_qkan.sql(sql, "db_qkan: export_aussengebiete (2)"):
                    return False

                sql = """
                    INSERT INTO he.Tabelleninhalte
                    ( KeyWert, Wert, Reihenfolge, Id)
                    SELECT
                      {cn}, {gesflaeche}, {reihenfolge}, {id};
                    """.format(
                    cn=cn, gesflaeche=gesflaeche, reihenfolge=1, id=nextid
                )

                if not db_qkan.sql(sql, "db_qkan: export_aussengebiete (2)"):
                    return False

                nextid += 1

        db_qkan.sql("UPDATE Itwh$ProgInfo SET NextId = {:d}".format(nextid))
        db_qkan.commit()

        fortschritt("{} Aussengebiete eingefuegt".format(nextid - nr0), 0.98)

    fortschritt("Ende...", 1)
    # progress_bar.setValue(100)
    # status_message.setText("Datenexport abgeschlossen.")
    # status_message.setLevel(Qgis.Success)

    return True


dummy = __name__

if __name__ == "__console__" or __name__ == "__main__":

    import datetime
    import tempfile
    from pathlib import Path

    from qgis.core import QgsApplication
    from qkan.database.dbfunc import DBConnection

    # Supply path to qgis install location
    QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.4/apps/qgis-ltr", True)

    # Create a reference to the QgsApplication.  Setting the
    # second argument to False disables the GUI.
    qgs = QgsApplication([], True)

    # Load providers
    qgs.initQgis()

    iface = QgisInterface()

    # Write your code here to load some layers, use processing
    # algorithms, etc.

    # logger = logging.getLogger("QKan")
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(
        Path(tempfile.gettempdir())
        / "QKan_{}.log".format(datetime.datetime.today().strftime("%Y-%m-%d"))
    )
    # stream_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    # stream_handler.setFormatter(formatter)

    file_handler.setLevel(logging.DEBUG)
    # stream_handler.setLevel(logging.DEBUG)

    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(file_handler)
        # logger.addHandler(stream_handler)

    # logger.debug(f'Aufruf von export_to_he8 aus der QGIS-Konsole: {__name__}')

    database_QKan = "C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_validate/work/itwh.sqlite"
    dbQK = DBConnection(
        dbname=database_QKan
    )  # Datenbankobjekt der QKan-Datenbank zum Lesen
    if not dbQK.connected:
        logger.error(
            "Fehler in exportdyna.application:\n",
            "QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                database_QKan
            ),
        )

    exporthe8(
        "C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_validate/work/erg/itwh.idbm",
        "C:/FHAC/jupiter/hoettges/team_data/Kanalprogramme/k_qkan/k_validate/work/muster_vorlage.idbm",
        dbQK,
        [],
        False,
        0.1,
        0.5,
        True,
        False,
        {
            "export_schaechte": True,
            "export_auslaesse": False,
            "export_speicher": True,
            "export_haltungen": True,
            "export_pumpen": False,
            "export_wehre": False,
            "export_flaechenrw": True,
            "export_einleitdirekt": False,
            "export_aussengebiete": False,
            "export_abflussparameter": False,
            "export_regenschreiber": False,
            "export_rohrprofile": False,
            "export_speicherkennlinien": False,
            "export_bodenklassen": False,
            "modify_schaechte": True,
            "modify_auslaesse": False,
            "modify_speicher": True,
            "modify_haltungen": True,
            "modify_pumpen": False,
            "modify_wehre": False,
            "modify_flaechenrw": True,
            "modify_einleitdirekt": False,
            "modify_aussengebiete": False,
            "modify_abflussparameter": False,
            "modify_regenschreiber": False,
            "modify_rohrprofile": False,
            "modify_speicherkennlinien": False,
            "modify_bodenklassen": False,
            "combine_einleitdirekt": False,
        },
    )

    # Finally, exitQgis() is called to remove the
    # provider and layer registries from memory
    qgs.exitQgis()
