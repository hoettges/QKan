import logging
import typing
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fortschritt, fehlermeldung, checknames, meldung

from qkan.database.reflists import abflusstypen
from qkan.linkflaechen.updatelinks import updatelinkageb, updatelinkfl, updatelinksw

logger = logging.getLogger("QKan.he8.export")

# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self, db_qkan, liste_teilgebiete):

        self.liste_teilgebiete = liste_teilgebiete
        self.db_qkan = db_qkan

        self.append = QKan.config.check_import.append
        self.update = QKan.config.check_import.update

        self.nextid = 0

    def run(self):
        """
        Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in
        eine HE_SpatiaLite-Datenbank
        """
        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Export in Arbeit. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

        # --------------------------------------------------------------------------------------------
        # Besonderes Gimmick des ITWH-Programmiers: Die IDs der Tabellen muessen sequentiell
        # vergeben werden!!! Ein Grund ist, dass (u.a.?) die Tabelle "tabelleninhalte" mit verschiedenen
        # Tabellen verknuepft ist und dieser ID eindeutig sein muss.

        self.db_qkan.sql("SELECT NextId, Version FROM he.Itwh$ProgInfo")
        data = self.db_qkan.fetchone()
        if not data:
            logger.error("he8porter._export.run: SELECT NextId, Version FROM he.Itwh$ProgInfo"
                         f"\nAbfrageergebnis ist leer: {data}")
        self.nextid = int(data[0]) + 1
        he_db_version = data[1].split(".")
        logger.debug(f"HE IDBF-Version {he_db_version}")

        # Export
        result = all([
            # self._profile(),
            # self._bodenklassen(),
            # self._abflussparameter(),
            self._schaechte(),
            self._auslaesse(),
            self._speicher(),
            self._haltungen(),
            self._wehre(),
            self._pumpen(),
            self._flaechen(),
            # self._einleitdirekt(),
            # self._aussengebiete(),
            # self._einzugsgebiet(),
            # self._tezg()
        ])

        self.progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")

        return result

        # fortschritt("Ende...", 1)
        # self.progress_bar.setValue(100)
        # status_message.setText("Datenexport abgeschlossen.")
        # status_message.setLevel(Qgis.Success)

    def _schaechte(self):
        """Export Schächte"""

        if QKan.config.check_export.schaechte:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
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
                        strftime('%Y-%m-%d %H:%M:%S', 
                            coalesce(schaechte.createdat, 'now'
                    )               ) AS lastmodified, 
                        schaechte.durchm*1000 AS durchmesser,
                        SetSrid(schaechte.geop, -1) AS geometry
                      FROM schaechte
                      LEFT JOIN simulationsstatus AS st
                      ON schaechte.simstatus = st.bezeichnung
                      WHERE schaechte.schnam = he.Schacht.Name and 
                            schaechte.schachttyp = 'Schacht'{auswahl})
                    WHERE he.Schacht.Name IN (
                        SELECT schnam 
                        FROM schaechte 
                        WHERE schaechte.schachttyp = 'Schacht'{auswahl})
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (35) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )
                nr0 = self.nextid
                id0 = self.nextid - idmin

                sql = f"""
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
                """

                if not self.db_qkan.sql(sql, "dbQK: export_schaechte (3)"):
                    return False

                self.nextid += idmax - idmin + 1
                self.db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}")
                self.db_qkan.commit()

                fortschritt(f"{self.nextid - nr0} Schaechte eingefügt", 0.30)
                self.progress_bar.setValue(30)

    def _speicher(self):
        """Export Speicherbauwerke"""

        if QKan.config.check_export.speicher:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
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
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_speicher (1)"):
                    return False

            if self.append:
                nr0 = self.nextid

                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (35) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )
                nr0 = self.nextid
                id0 = self.nextid - idmin

                sql = f"""
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
                """

                if not self.db_qkan.sql(sql, "dbQK: export_speicher (1)"):
                    return False

                self.nextid += idmax - idmin + 1
                self.db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}")
                self.db_qkan.commit()

                fortschritt(f"{self.nextid - nr0} Speicher eingefügt", 0.40)
                self.progress_bar.setValue(40)

    def _auslaesse(self):
        """Export Auslässe"""

        if QKan.config.check_export.auslaesse:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND schaechte.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
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
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_auslaesse (1)"):
                    return False

            if self.append:
                nr0 = self.nextid

                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_schaechte (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (35) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )
                nr0 = self.nextid
                id0 = self.nextid - idmin

                sql = f"""
                    INSERT INTO he.Auslass
                    ( Id, Name, Typ, Sohlhoehe,
                      Gelaendehoehe, Art, AnzahlKanten,
                      Scheitelhoehe, 
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
                      st.he_nr AS planungsstatus, 
                      strftime('%Y-%m-%d %H:%M:%S', coalesce(schaechte.createdat, 'now')) AS lastmodified, 
                      kommentar AS kommentar,
                      SetSrid(schaechte.geop, -1) AS geometry
                    FROM schaechte
                    LEFT JOIN simulationsstatus AS st
                    ON schaechte.simstatus = st.bezeichnung
                    WHERE schaechte.schnam NOT IN (SELECT Name FROM he.Auslass) and 
                          schaechte.schachttyp = 'Auslass'{auswahl}
                """

                if not self.db_qkan.sql(sql, "dbQK: export_auslaesse (2)"):
                    return False

                self.nextid += idmax - idmin + 1
                self.db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}")
                self.db_qkan.commit()

                fortschritt(f"{self.nextid - nr0} Auslässe eingefügt", 0.50)
                self.progress_bar.setValue(50)

    def _haltungen(self):
        """Export Haltungen"""

        if QKan.config.check_export.haltungen:
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND haltungen.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
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
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche) =
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
                      28 AS materialart, 
                      0 AS einzugsgebiet, 
                      0 AS konstanterzuflusstezg, 
                      0 AS befestigteflaeche, 
                      0 AS unbefestigteflaeche
                    FROM
                      (haltungen JOIN schaechte AS sob ON haltungen.schoben = sob.schnam)
                      JOIN schaechte AS sun ON haltungen.schunten = sun.schnam
                      LEFT JOIN profile ON haltungen.profilnam = profile.profilnam
                      LEFT JOIN entwaesserungsarten ON haltungen.entwart = entwaesserungsarten.bezeichnung
                      LEFT JOIN simulationsstatus AS st ON haltungen.simstatus = st.bezeichnung
                      WHERE haltungen.haltnam = he.Rohr.Name{auswahl})
                  WHERE he.Rohr.Name IN 
                  ( SELECT haltnam FROM haltungen){auswahl})
                  """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_haltungen (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_haltungen (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (35) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )
                nr0 = self.nextid
                id0 = self.nextid - idmin

                sql = f"""
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
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche)
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
                    28 AS materialart,
                    0 AS einzugsgebiet,
                    0 AS konstanterzuflusstezg,
                    0 AS befestigteflaeche,
                    0 AS unbefestigteflaeche
                  FROM
                    (haltungen JOIN schaechte AS sob ON haltungen.schoben = sob.schnam)
                    JOIN schaechte AS sun ON haltungen.schunten = sun.schnam
                    LEFT JOIN profile ON haltungen.profilnam = profile.profilnam
                    LEFT JOIN entwaesserungsarten ON haltungen.entwart = entwaesserungsarten.bezeichnung
                    LEFT JOIN simulationsstatus AS st ON haltungen.simstatus = st.bezeichnung
                    WHERE haltungen.haltnam NOT IN (SELECT Name FROM he.Rohr){auswahl};
                  """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_haltungen (3)"):
                    return False

                self.nextid += idmax - idmin + 1
                self.db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}")
                self.db_qkan.commit()

                fortschritt(f"{self.nextid - nr0} Haltungen eingefügt", 0.60)
                self.progress_bar.setValue(60)

    def _flaechen(self):
        """Export Flächenobjekte"""

        if QKan.config.check_export.flaechen:

            mindestflaeche = QKan.config.mindestflaeche
            autokorrektur = QKan.config.autokorrektur
            fangradius = QKan.config.fangradius
            mit_verschneidung = QKan.config.mit_verschneidung

            nr0 = None  # Für Fortschrittsmeldung

            # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
            if not checknames(self.db_qkan, "flaechen", "flnam", "f_", autokorrektur):
                return False

            if not updatelinkfl(self.db_qkan, fangradius):
                fehlermeldung(
                    "Fehler beim Update der Flächen-Verknüpfungen",
                    "Der logische Cache konnte nicht aktualisiert werden.",
                )
                return False

            # Zu verschneidende zusammen mit nicht zu verschneidene Flächen exportieren

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" WHERE fl.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

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

            if self.update:
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
                      ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl}""",
                    f"""
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
                      ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl})
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
                    """,
                )

                for sql in sqllis:
                    if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_flaechen (1)"):
                        return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM linkfl"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_flaechen (2)"):
                    return False

                data = self.db_qkan.fetchone()
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
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
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
                          ON ap.flaechentyp = ft.bezeichnung{join_verschneidung}{auswahl})
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
                        WHERE flaeche*10000 > {mindestflaeche} and (flnam NOT IN (SELECT Name FROM he.Flaeche))"""

                    if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_flaechen (3)"):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}")
            self.db_qkan.commit()

            if nr0:
                fortschritt("{} Flaechen eingefuegt".format(self.nextid - nr0), 0.80)

    def _pumpen(self):
        """Export Pumpen"""

        if QKan.config.check_export.pumpen:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl_w = f" WHERE pumpen.teilgebiet in ('{lis}')"
                auswahl_a = f" AND pumpen.teilgebiet in ('{lis}')"
            else:
                auswahl_w = ""
                auswahl_a = ""


            if self.update:
                sql = f"""
                    UPDATE he.Pumpe SET
                    (   SchachtOben, SchachtUnten, 
                        Typ, Steuerschacht, 
                        Einschalthoehe, Ausschalthoehe, 
                        Planungsstatus, 
                        Kommentar, LastModified 
                    ) = 
                    (   SELECT
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
                        ON pumpen.simstatus = simulationsstatus.bezeichnung{auswahl_w}
                    )
                    WHERE (he.Pumpe.Name IN 
                    (   SELECT pnam FROM pumpen)){auswahl_a})
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_pumpen (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM pumpen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_pumpen (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (36) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )
                nr0 = self.nextid
                id0 = self.nextid - idmin

                sql = f"""
                INSERT INTO he.Pumpe (
                    Id,
                    Name, 
                    SchachtOben, SchachtUnten, 
                    Typ, Steuerschacht, 
                    Einschalthoehe, Ausschalthoehe, 
                    Planungsstatus, 
                    Kommentar, LastModified 
                ) 
                SELECT
                    pumpen.rowid + {id0} AS id, 
                    pumpen.pnam AS Name,
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
                ON pumpen.simstatus = simulationsstatus.bezeichnung
                WHERE (pumpen.pnam NOT IN (SELECT Name FROM he.Pumpe)){auswahl_a};
                """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_pumpen (3)"):
                    return False

                self.nextid += idmax - idmin + 1
                self.db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}")
                self.db_qkan.commit()

                fortschritt(f"{self.nextid - nr0} Pumpen eingefügt", 0.85)
                self.progress_bar.setValue(85)

    def _wehre(self):
        """Export Pumpen"""

        if QKan.config.check_export.wehre:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl_w = f" WHERE wehre.teilgebiet in ('{lis}')"
                auswahl_a = f" AND wehre.teilgebiet in ('{lis}')"
            else:
                auswahl_w = ""
                auswahl_a = ""

            if self.update:
                sql = f"""
                    UPDATE he.Wehr SET
                    (   SchachtOben, SchachtUnten, 
                        SohlhoeheOben, SohlhoeheUnten, 
                        Schwellenhoehe, Geometrie1, 
                        Geometrie2, Ueberfallbeiwert, 
                        Rueckschlagklappe, Verfahrbar, Profiltyp, 
                        Ereignisbilanzierung, EreignisGrenzwertEnde,
                        EreignisGrenzwertAnfang, EreignisTrenndauer, 
                        EreignisIndividuell, Planungsstatus, 
                        Kommentar, LastModified 
                    ) = 
                    (   SELECT
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
                        LEFT JOIN pumpentypen
                        ON pumpen.pumpentyp = pumpentypen.bezeichnung
                        LEFT JOIN simulationsstatus
                        ON wehre.simstatus = simulationsstatus.bezeichnung{auswahl_w}
                    )
                    WHERE (he.Wehr.Name IN 
                    (   SELECT wnam FROM wehre)){auswahl_a})
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_wehre (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM wehre"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_wehre (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (36) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )
                nr0 = self.nextid
                id0 = self.nextid - idmin

                sql = f"""
                INSERT INTO he.Wehr (
                    Id,
                    Name, 
                    SchachtOben, SchachtUnten, 
                    SohlhoeheOben, SohlhoeheUnten, 
                    Schwellenhoehe, Geometrie1, 
                    Geometrie2, Ueberfallbeiwert, 
                    Rueckschlagklappe, Verfahrbar, Profiltyp, 
                    Ereignisbilanzierung, EreignisGrenzwertEnde,
                    EreignisGrenzwertAnfang, EreignisTrenndauer, 
                    EreignisIndividuell, Planungsstatus, 
                    Kommentar, LastModified 
                ) 
                SELECT
                    wehre.rowid + {id0} AS id, 
                    wehre.wnam AS Name,
                    wehre.schoben AS schoben,
                    wehre.schunten AS schunten,
                    coalesce(sob.sohlhoehe, 0) AS sohleoben_t,
                    coalesce(sun.sohlhoehe, 0) AS sohleunten_t,
                    wehre.schwellenhoehe AS schwellenhoehe_t,
                    wehre.kammerhoehe AS kammerhoehe_t,
                    wehre.laenge AS laenge_t,
                    wehre.uebeiwert AS uebeiwert_t,
                    0 AS rueckschlagklappe,
                    0 AS verfahrbar,
                    52 AS profiltyp,
                    0 AS ereignisbilanzierung,
                    0 AS ereignisgrenzwertende,
                    0 AS ereignisgrenzwertanfang,
                    0 AS ereignistrenndauer,
                    0 AS ereignisindividuell,
                    simulationsstatus.he_nr AS simstatusnr,
                    wehre.kommentar AS kommentar,
                    wehre.createdat AS createdat
                FROM wehre
                LEFT JOIN simulationsstatus
                ON wehre.simstatus = simulationsstatus.bezeichnung
                LEFT JOIN schaechte AS sob 
                ON wehre.schoben = sob.schnam
                LEFT JOIN schaechte AS sun 
                ON wehre.schunten = sun.schnam
                WHERE (wehre.wnam NOT IN (SELECT Name FROM he.Wehr)){auswahl_a};
                """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_wehre (3)"):
                    return False

                self.nextid += idmax - idmin + 1
                self.db_qkan.sql(f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}")
                self.db_qkan.commit()

                fortschritt(f"{self.nextid - nr0} Wehre eingefügt", 0.85)
                self.progress_bar.setValue(90)
