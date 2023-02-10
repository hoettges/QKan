import logging
from typing import List

from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QProgressBar

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import checknames, fehlermeldung, fortschritt, meldung
from qkan.linkflaechen.updatelinks import updatelinkfl

logger = logging.getLogger("QKan.he8.export")


# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self, db_qkan: DBConnection, liste_teilgebiete: List[str]):

        self.liste_teilgebiete = liste_teilgebiete
        self.db_qkan = db_qkan

        self.append = QKan.config.check_export.append
        self.update = QKan.config.check_export.update

        self.nextid = 0

    def run(self) -> bool:
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
            logger.error(
                "he8porter._export.run: SELECT NextId, Version FROM he.Itwh$ProgInfo"
                f"\nAbfrageergebnis ist leer: {data}"
            )
        self.nextid = int(data[0]) + 1
        he_db_version = data[1].split(".")
        logger.debug(f"HE IDBF-Version {he_db_version}")

        # Export
        result = all(
            [
                # self._profile(),
                self._bodenklassen(),
                self._abflussparameter(),
                self._schaechte(),
                self._auslaesse(),
                self._speicher(),
                self._haltungen(),
                self._wehre(),
                self._pumpen(),
                self._drosseln(),
                self._schieber(),
                self._qregler(),
                self._hregler(),
                self._grundseitenauslaesse(),
                self._flaechen(),
                # self._einleitdirekt(),
                # self._aussengebiete(),
                # self._einzugsgebiet(),
                self._tezg(),
            ]
        )

        self.progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")

        return result

        # fortschritt("Ende...", 1)
        # self.progress_bar.setValue(100)
        # status_message.setText("Datenexport abgeschlossen.")
        # status_message.setLevel(Qgis.Success)

    def _schaechte(self) -> bool:
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
                        coalesce(schaechte.createdat, datetime('now'))
                                                AS lastmodified, 
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

                if not self.db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_schaechte (1)"
                ):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_schaechte (2)"
                ):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (1) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Schächte", "Keine Schächte vorhanden")
                else:
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
                          coalesce(schaechte.createdat, datetime('now')) AS lastmodified, 
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
                    self.db_qkan.sql(
                        f"UPDATE he.Itwh$ProgInfo SET NextId = {self.nextid}"
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Schaechte eingefügt", 0.30)
                    self.progress_bar.setValue(30)
        return True

    def _speicher(self) -> bool:
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
                        coalesce(schaechte.createdat, datetime('now')) AS lastmodified, 
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
                if not self.db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_schaechte (2)"
                ):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (2) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung(
                        "Einfügen Speicherschächte", "Keine Speicherschächte vorhanden"
                    )
                else:
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
                          coalesce(schaechte.createdat, datetime('now')) AS lastmodified, 
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
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Speicher eingefügt", 0.40)
                    self.progress_bar.setValue(40)
        return True

    def _auslaesse(self) -> bool:
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
                        coalesce(schaechte.createdat, datetime('now')) AS lastmodified, 
                        kommentar AS kommentar,
                        SetSrid(schaechte.geop, -1) AS Geometry
                      FROM schaechte
                      LEFT JOIN simulationsstatus AS st
                      ON schaechte.simstatus = st.bezeichnung
                      WHERE schaechte.schnam = he.Auslass.Name and schaechte.schachttyp = 'Auslass'{auswahl})
                    WHERE he.Auslass.Name IN 
                          (SELECT schnam FROM schaechte WHERE schaechte.schachttyp = 'Auslass'{auswahl})
                    """

                if not self.db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_auslaesse (1)"
                ):
                    return False

            if self.append:
                nr0 = self.nextid

                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                if not self.db_qkan.sql(
                    "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen",
                    "dbQK: export_to_he8.export_schaechte (2)",
                ):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (3) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Auslässe", "Keine Auslässe vorhanden")
                else:
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
                          coalesce(schaechte.createdat, datetime('now')) AS lastmodified, 
                          kommentar AS kommentar,
                          SetSrid(schaechte.geop, -1) AS Geometry
                        FROM schaechte
                        LEFT JOIN simulationsstatus AS st
                        ON schaechte.simstatus = st.bezeichnung
                        WHERE schaechte.schnam NOT IN (SELECT Name FROM he.Auslass) and 
                              schaechte.schachttyp = 'Auslass'{auswahl}
                    """

                    if not self.db_qkan.sql(sql, "dbQK: export_auslaesse (2)"):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Auslässe eingefügt", 0.50)
                    self.progress_bar.setValue(50)
        return True

    def _haltungen(self) -> bool:
        """Export Haltungen"""

        if QKan.config.check_export.haltungen:
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
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
                    Kommentar,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry) =
                  ( SELECT
                      ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                      coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                      coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                      coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                      coalesce(profile.he_nr, 68) AS Profiltyp, 
                      CASE WHEN coalesce(profile.he_nr, 68) = 68 THEN ha.profilnam
                      ELSE NULL
                      END
                      AS Sonderprofilbezeichnung, 
                      ha.hoehe AS Geometrie1, ha.breite AS Geometrie2,
                      entwaesserungsarten.he_nr AS Kanalart,
                      coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                      coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                      ha.kommentar AS Kommentar,
                      coalesce(ha.createdat, datetime('now')) AS LastModified, 
                      28 AS Materialart, 
                      0 AS Einzugsgebiet, 
                      0 AS KonstanterZuflussTezg, 
                      0 AS BefestigteFlaeche, 
                      0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                    FROM
                      haltungen AS ha 
                      JOIN schaechte AS sob ON ha.schoben = sob.schnam
                      JOIN schaechte AS sun ON ha.schunten = sun.schnam
                      LEFT JOIN profile ON ha.profilnam = profile.profilnam
                      LEFT JOIN entwaesserungsarten ON ha.entwart = entwaesserungsarten.bezeichnung
                      LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                      WHERE (ha.haltungstyp IS NULL or ha.haltungstyp = 'Haltung') AND ha.haltnam = he.Rohr.Name{auswahl})
                  WHERE he.Rohr.Name IN 
                  ( SELECT haltnam FROM haltungen AND 
                    (haltungen.haltungstyp IS NULL OR haltungen.haltungstyp = 'Haltung')){auswahl}
                  """

                if not self.db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_haltungen (1)"
                ):
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
                        "Fehler (4) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Haltungen", "Keine Haltungen vorhanden")
                else:
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
                        Rauigkeitsansatz, 
                        RauhigkeitAnzeige,
                        Kommentar,
                        LastModified, 
                        Materialart, 
                        Einzugsgebiet, 
                        KonstanterZuflussTezg, 
                        BefestigteFlaeche, 
                        UnbefestigteFlaeche, Geometry)
                      SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name, ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                        coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                        coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                        coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                        coalesce(profile.he_nr, 68) AS Profiltyp,
                        CASE WHEN coalesce(profile.he_nr, 68) = 68 THEN ha.profilnam
                        ELSE NULL
                        END
                        AS Sonderprofilbezeichnung, 
                        ha.hoehe AS Geometrie1, ha.breite AS Geometrie2,
                        entwaesserungsarten.he_nr AS Kanalart,
                        coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                        1 AS Rauigkeitsansatz, 
                        coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                        ha.kommentar AS Kommentar,
                        coalesce(ha.createdat, datetime('now')) AS LastModified, 
                        28 AS Materialart,
                        0 AS Einzugsgebiet,
                        0 AS KonstanterZuflussTezg,
                        0 AS BefestigteFlaeche,
                        0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                      FROM
                        haltungen AS ha
                        JOIN schaechte AS sob ON ha.schoben = sob.schnam
                        JOIN schaechte AS sun ON ha.schunten = sun.schnam
                        LEFT JOIN profile ON ha.profilnam = profile.profilnam
                        LEFT JOIN entwaesserungsarten ON ha.entwart = entwaesserungsarten.bezeichnung
                        LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                        WHERE ha.haltnam NOT IN (SELECT Name FROM he.Rohr) 
                        AND (ha.haltungstyp IS NULL OR ha.haltungstyp = 'Haltung'){auswahl};
                      """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_haltungen (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Haltungen eingefügt", 0.60)
                    self.progress_bar.setValue(60)
        return True

    def _flaechen(self) -> bool:
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
                case_verschneidung = "(fl.aufteilen <> 'ja' AND not fl.aufteilen) OR fl.aufteilen IS NULL"
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
                    """DELETE FROM flupdate""",
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
                        coalesce(lf.speicherzahl, 2) AS speicherzahl, coalesce(lf.speicherkonst, 0) AS speicherkonst,
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
                        abflussparameter AS Parametersatz, coalesce(neigkl, 1) AS Neigungsklasse, 
                        coalesce(createdat, datetime('now')) AS lastmodified, 
                        kommentar AS Kommentar, 
                        SetSrid(geom, -1) AS Geometry
                      FROM flintersect AS fi
                      WHERE flnam = he.Flaeche.Name and flaeche*10000 > {mindestflaeche} and flaeche IS NOT NULL
                    ) WHERE he.Flaeche.Name IN (SELECT flnam FROM flupdate)
                    """,
                )

                for sql in sqllis:
                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_flaechen (1)"
                    ):
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
                        "Fehler (5) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Flächen", "Keine Flächen vorhanden")
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
                            coalesce(lf.speicherzahl, 2) AS speicherzahl, coalesce(lf.speicherkonst, 0) AS speicherkonst,
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
                          abflussparameter AS Parametersatz, coalesce(neigkl, 1) AS Neigungsklasse, 
                          1 AS IstPolygonalflaeche, 1 AS ZuordnungGesperrt, 0 AS ZuordnUnabhEZG, 
                          coalesce(createdat, datetime('now')) AS lastmodified, 
                          kommentar AS Kommentar, 
                          SetSrid(geom, -1) AS Geometry
                        FROM flintersect AS fi
                        WHERE flaeche*10000 > {mindestflaeche} and (flnam NOT IN (SELECT Name FROM he.Flaeche))"""

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_flaechen (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )

                    fortschritt("{} Flaechen eingefuegt".format(self.nextid - nr0), 0.80)
                    self.progress_bar.setValue(80)

            self.db_qkan.commit()

        return True

    def _tezg(self) -> bool:
        """Export Haltungsflächen als befestigte und unbefestigte Flächen"""

        if QKan.config.check_export.tezg_hf:
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM tezg"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_tezg"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                    idanz = idmax - idmin + 1
                    logger.debug(f"idmin = {idmin}\nidmax = {idmax}\n")
                else:
                    fehlermeldung(
                        "Fehler (6) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung(
                        "Einfügen tezg als Flächen", "Keine Haltungsflächen vorhanden"
                    )
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    mindestflaeche = QKan.config.mindestflaeche

                    sql = f"""
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
                          tg.rowid + {id0} + {idanz} * tb.bef AS id,                -- doppelte Anzahl
                          CASE WHEN tb.bef = 0
                            THEN printf('%s_b', tg.flnam)
                            ELSE printf('%s_u', tg.flnam) 
                          END           AS Name, 
                          tg.haltnam AS Haltung, 
                          area(tg.geom)/10000.*abs(tb.bef - coalesce(tg.befgrad, 0)/100.) AS Groesse, 
                          tg.regenschreiber AS Regenschreiber, 
                          coalesce(ft.he_nr, 0) AS Flaechentyp, 
                          2 AS BerechnungSpeicherkonstante, 
                          tb.bef AS Typ, 
                          2 AS AnzahlSpeicher, 
                          0. AS Speicherkonstante,                                  -- nicht verwendet 
                          coalesce(tg.schwerpunktlaufzeit/60., 0.) AS Schwerpunktlaufzeit,
                          0. AS FliesszeitOberflaeche,                              -- nicht verwendet 
                          0. AS LaengsteFliesszeitKanal,                            -- nicht verwendet
                          CASE WHEN tb.bef = 0
                            THEN '$Default_Bef'
                            ELSE '$Default_Unbef'
                          END       AS Parametersatz, 
                          coalesce(tg.neigkl, 1) AS Neigungsklasse, 
                          1 AS IstPolygonalflaeche, 1 AS ZuordnungGesperrt, 0 AS ZuordnUnabhEZG, 
                          coalesce(tg.createdat, datetime('now')) AS lastmodified, 
                          tg.kommentar AS Kommentar, 
                          SetSrid(tg.geom, -1) AS Geometry
                        FROM tezg AS tg
                        LEFT JOIN he.Flaeche AS fh
                        ON fh.Name = tg.flnam
                        , (SELECT he_nr FROM flaechentypen WHERE bezeichnung = 'Gebäude') AS ft
                        , (SELECT column1 AS bef FROM (VALUES (0) , (1))) AS tb
                        WHERE fh.Name IS NULL AND
                         area(tg.geom)*abs(tb.bef - coalesce(tg.befgrad, 0)/100.) > {mindestflaeche}"""

                    if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_tezg (1)"):
                        return False

                    self.nextid += (idmax - idmin + 1) * 2
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )

                    fortschritt("{} Haltungsflaechen eingefuegt".format(self.nextid - nr0), 0.80)
                    self.progress_bar.setValue(80)
        elif QKan.config.check_export.tezg:
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM tezg"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_tezg"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                    idanz = idmax - idmin + 1
                    logger.debug(f"idmin = {idmin}\nidmax = {idmax}\n")
                else:
                    fehlermeldung(
                        "Fehler (7) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung(
                        "Einfügen tezg als GIPS-TEZG", "Keine Haltungsflächen vorhanden"
                    )
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    mindestflaeche = QKan.config.mindestflaeche

                    sql = f"""
                        INSERT INTO he.GipsEinzugsflaeche (
                            id, 
                            Name, Haltung,
                            IsEinzugsflaeche,
                            IsHaltungsflaeche,
                            IsTwEinzugsflaeche, 
                            LastModified,
                            Kommentar, 
                            Geometry)
                        SELECT 
                            tg.rowid + {id0} AS id,
                            tg.flnam AS Name,
                            tg.haltnam AS Haltung,
                            0 AS IsEinzugsflaeche,
                            1 AS IsHaltungflaeche,
                            0 AS IsTwEinzugsflaeche, 
                            coalesce(tg.createdat, datetime('now')) AS lastmodified, 
                            tg.kommentar AS Kommentar, 
                            SetSrid(tg.geom, -1) AS Geometry
                        FROM tezg AS tg
                    """

                    if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_tezg (2)"):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )

                    fortschritt("{} Haltungsflaechen eingefuegt".format(self.nextid - nr0), 0.90)
                    self.progress_bar.setValue(90)

        self.db_qkan.commit()

        return True

    def _pumpen(self) -> bool:
        """Export Pumpen"""

        if QKan.config.check_export.pumpen:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Pumpe SET
                    (   SchachtOben, SchachtUnten, 
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry 
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        WHERE ha.haltnam = he.Pumpe.Name
                    )
                    WHERE he.Pumpe.Name IN (
                        SELECT haltnam FROM haltungen WHERE ha.haltungstyp = 'Pumpe'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_pumpen (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_pumpen (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (8) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Pumpen", "Keine Pumpen vorhanden")
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
                    INSERT INTO he.Pumpe (
                        Id,
                        Name, 
                        SchachtOben, SchachtUnten,
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry 
                    ) 
                    SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name,
                        ha.schoben AS SchachtOben,
                        ha.schunten AS SchachtUnten,
                        si.he_nr AS Planungsstatus,
                        ha.kommentar AS Kommentar,
                        ha.createdat AS LastModified,
                        SetSrid(ha.geom, -1) AS Geometry
                    FROM haltungen AS ha
                    LEFT JOIN simulationsstatus AS si
                    ON ha.simstatus = si.bezeichnung
                    WHERE ha.haltungstyp = 'Pumpe'
                    AND ha.haltnam NOT IN (SELECT Name FROM he.Pumpe){auswahl};
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_pumpen (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Pumpen eingefügt", 0.85)
                    self.progress_bar.setValue(85)
        return True

    def _wehre(self) -> bool:
        """Export Pumpen"""

        if QKan.config.check_export.wehre:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Wehr SET
                    (   SchachtOben, SchachtUnten, 
                        Ueberfallbeiwert, 
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            wehre.uebeiwert AS Ueberfallbeiwert,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        WHERE ha.haltnam = he.Wehr.Name{auswahl}
                    )
                    WHERE he.Wehr.Name IN (
                        SELECT haltnam FROM haltungen WHERE ha.haltungstyp = 'Wehr'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_wehre (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_wehre (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (9) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Wehre", "Keine Wehre vorhanden")
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
                    INSERT INTO he.Wehr (
                        Id,
                        Name, 
                        SchachtOben, SchachtUnten, 
                        Ueberfallbeiwert, 
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) 
                    SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name,
                        ha.schoben AS SchachtOben,
                        ha.schunten AS SchachtUnten,
                        ha.ks AS Ueberfallbeiwert,
                        si.he_nr AS Planungsstatus,
                        ha.kommentar AS Kommentar,
                        ha.createdat AS LastModified,
                        SetSrid(ha.geom, -1) AS Geometry
                    FROM haltungen AS ha
                    LEFT JOIN simulationsstatus AS si
                    ON ha.simstatus = si.bezeichnung
                    WHERE ha.haltungstyp = 'Wehr'
                    AND ha.haltnam NOT IN (SELECT Name FROM he.Wehr){auswahl};
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_wehre (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Wehre eingefügt", 0.90)
                    self.progress_bar.setValue(90)
        return True

    def _drosseln(self) -> bool:
        """Export Drosseln"""

        if QKan.config.check_export.drosseln:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Drossel SET
                    (   SchachtOben, SchachtUnten, 
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        WHERE ha.haltnam = he.Drossel.Name{auswahl}
                    )
                    WHERE he.Drossel.Name IN (
                        SELECT haltnam FROM haltungen WHERE ha.haltungstyp = 'Drossel'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_drosseln (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_drosseln (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (10) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Drosseln", "Keine Drosseln vorhanden")
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
                    INSERT INTO he.Drossel (
                        Id,
                        Name, 
                        SchachtOben, SchachtUnten,
                        Planungsstatus,
                        Kommentar, LastModified,
                        Geometry
                    ) 
                    SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name,
                        ha.schoben AS SchachtOben,
                        ha.schunten AS SchachtUnten,
                        si.he_nr AS Planungsstatus,
                        ha.kommentar AS Kommentar,
                        ha.createdat AS LastModified,
                        SetSrid(ha.geom, -1) AS Geometry
                    FROM haltungen AS ha
                    LEFT JOIN simulationsstatus AS si
                    ON ha.simstatus = si.bezeichnung
                    WHERE ha.haltungstyp = 'Drossel'
                    AND ha.haltnam NOT IN (SELECT Name FROM he.Drossel){auswahl};
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_drosseln (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Drosseln eingefügt", 0.90)
                    self.progress_bar.setValue(90)
        return True

    def _schieber(self) -> bool:
        """Export Drosseln"""

        if QKan.config.check_export.schieber:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.Schieber SET
                    (   SchachtOben, SchachtUnten, 
                        Anfangsstellung, 
                        MaximaleHubhoehe,
                        Geometrie2,
                        Verluste,
                        Profiltyp,
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            ha.sohleoben AS Anfangsstellung,
                            ha.sohleoben + ha.hoehe AS MaximaleHubhoehe,
                            ha.breite AS Geometrie2,
                            ha.ks AS Verluste,
                            profile.he_nr AS Profiltyp,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        LEFT JOIN profile
                        ON ha.profilnam = profile.profilnam
                        WHERE ha.haltnam = he.Schieber.Name{auswahl}
                    )
                    WHERE he.Schieber.Name IN (
                        SELECT haltnam FROM haltungen WHERE ha.haltungstyp = 'Schieber'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_schieber (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_schieber (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (11) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Schieber", "Keine Schieber vorhanden")
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
                    INSERT INTO he.Schieber (
                        Id,
                        Name, 
                        SchachtOben, SchachtUnten,
                        Anfangsstellung, 
                        MaximaleHubhoehe,
                        Geometrie2,
                        Verluste,
                        Profiltyp,
                        Planungsstatus,
                        Kommentar, LastModified,
                        Geometry
                    ) 
                    SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name,
                        ha.schoben AS SchachtOben,
                        ha.schunten AS SchachtUnten,
                        ha.sohleoben AS Anfangsstellung,
                        ha.sohleoben + ha.hoehe AS MaximaleHubhoehe,
                        ha.breite AS Geometrie2,
                        ha.ks AS Verluste,
                        profile.he_nr AS Profiltyp,
                        si.he_nr AS Planungsstatus,
                        ha.kommentar AS Kommentar,
                        ha.createdat AS LastModified,
                        SetSrid(ha.geom, -1) AS Geometry
                    FROM haltungen AS ha
                    LEFT JOIN simulationsstatus AS si
                    ON ha.simstatus = si.bezeichnung
                    LEFT JOIN profile
                    ON ha.profilnam = profile.profilnam
                    WHERE ha.haltungstyp = 'Schieber'
                    AND ha.haltnam NOT IN (SELECT Name FROM he.Schieber){auswahl};
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_schieber (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Schieber eingefügt", 0.90)
                    self.progress_bar.setValue(90)
        return True

    def _grundseitenauslaesse(self) -> bool:
        """Export Grund- und Seitenauslässe"""

        if QKan.config.check_export.grundseitenauslaesse:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                    UPDATE he.GrundSeitenauslass SET
                    (   SchachtOben, SchachtUnten, 
                        HoeheUnterkante,
                        Geometrie2,
                        Auslassbeiwert,
                        Profiltyp,
                        Planungsstatus, 
                        Kommentar, LastModified,
                        Geometry
                    ) = 
                    (   SELECT
                            ha.schoben AS SchachtOben,
                            ha.schunten AS SchachtUnten,
                            ha.sohleoben AS HoeheUnterkante,
                            ha.breite AS Geometrie2,
                            ha.ks AS Auslassbeiwert,
                            profile.he_nr AS Profiltyp,
                            si.he_nr AS Planungsstatus,
                            ha.kommentar AS Kommentar,
                            ha.createdat AS LastModified,
                            SetSrid(ha.geom, -1) AS Geometry
                        FROM haltungen AS ha
                        LEFT JOIN simulationsstatus AS si
                        ON ha.simstatus = si.bezeichnung
                        LEFT JOIN profile
                        ON ha.profilnam = profile.profilnam
                        WHERE ha.haltnam = he.GrundSeitenauslass.Name{auswahl}
                    )
                    WHERE he.GrundSeitenauslass.Name IN (
                        SELECT haltnam FROM haltungen WHERE ha.haltungstyp = 'GrundSeitenauslass'{auswahl}
                        )
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_grundseitenauslaesse (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_grundseitenauslaesse (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (12) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Grund- und Seitenauslässe", "Keine Grund- und Seitenauslass vorhanden")
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
                    INSERT INTO he.GrundSeitenauslass (
                        Id,
                        Name, 
                        SchachtOben, SchachtUnten,
                        HoeheUnterkante,
                        Geometrie2,
                        Auslassbeiwert,
                        Profiltyp,
                        Planungsstatus,
                        Kommentar, LastModified,
                        Geometry
                    ) 
                    SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name,
                        ha.schoben AS SchachtOben,
                        ha.schunten AS SchachtUnten,
                        ha.sohleoben AS HoeheUnterkante,
                        ha.breite AS Geometrie2,
                        ha.ks AS Auslassbeiwert,
                        profile.he_nr AS Profiltyp,
                        si.he_nr AS Planungsstatus,
                        ha.kommentar AS Kommentar,
                        ha.createdat AS LastModified,
                        SetSrid(ha.geom, -1) AS Geometry
                    FROM haltungen AS ha
                    LEFT JOIN simulationsstatus AS si
                    ON ha.simstatus = si.bezeichnung
                    LEFT JOIN profile
                    ON ha.profilnam = profile.profilnam
                    WHERE ha.haltungstyp = 'GrundSeitenauslass'
                    AND ha.haltnam NOT IN (SELECT Name FROM he.GrundSeitenauslass){auswahl};
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_grundseitenauslaesse (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Grund- und Seitenauslässe eingefügt", 0.90)
                    self.progress_bar.setValue(90)
        return True

    def _qregler(self) -> bool:
        """Export Q-Regler"""

        if QKan.config.check_export.qregler:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                  UPDATE he.QRegler SET
                  ( SchachtOben, SchachtUnten,
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Geometrie1, Geometrie2, 
                    Kanalart,
                    Rauigkeitsbeiwert, Anzahl,
                    RauhigkeitAnzeige,
                    Profiltyp,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry) =
                  ( SELECT
                      ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                      coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                      coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                      coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                      ha.hoehe AS Geometrie1, ha.breite AS Geometrie2,
                      entwaesserungsarten.he_nr AS Kanalart,
                      coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                      coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                      profile.he_nr AS Profiltyp,
                      coalesce(ha.createdat, datetime('now')) AS LastModified, 
                      28 AS Materialart, 
                      0 AS Einzugsgebiet, 
                      0 AS KonstanterZuflussTezg, 
                      0 AS BefestigteFlaeche, 
                      0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                    FROM
                      haltungen AS ha 
                      JOIN schaechte AS sob ON ha.schoben = sob.schnam
                      JOIN schaechte AS sun ON ha.schunten = sun.schnam
                      LEFT JOIN profile ON ha.profilnam = profile.profilnam
                      LEFT JOIN entwaesserungsarten ON ha.entwart = entwaesserungsarten.bezeichnung
                      LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                      WHERE ha.haltungstyp = 'Q-Regler' AND ha.haltnam = he.QRegler.Name{auswahl})
                  WHERE he.Rohr.Name IN 
                  ( SELECT haltnam FROM haltungen AND haltungen.haltungstyp = 'Q-Regler'){auswahl}
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_qregler (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_qregler (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (13) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Q-Regler", "Keine Q-Regler vorhanden")
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
                      INSERT INTO he.QRegler
                      ( Id, 
                        Name, SchachtOben, SchachtUnten, 
                        Laenge, 
                        SohlhoeheOben,
                        SohlhoeheUnten, 
                        Geometrie1, Geometrie2, 
                        Kanalart, 
                        Rauigkeitsbeiwert, Anzahl, 
                        Rauigkeitsansatz, 
                        RauhigkeitAnzeige,
                        Profiltyp,
                        LastModified, 
                        Materialart, 
                        Einzugsgebiet, 
                        KonstanterZuflussTezg, 
                        BefestigteFlaeche, 
                        UnbefestigteFlaeche, Geometry)
                      SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name, ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                        coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                        coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                        coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                        ha.hoehe AS Geometrie1, ha.breite AS Geometrie2,
                        entwaesserungsarten.he_nr AS Kanalart,
                        coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                        1 AS Rauigkeitsansatz, 
                        coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                        profile.he_nr AS Profiltyp,
                        coalesce(ha.createdat, datetime('now')) AS LastModified, 
                        28 AS Materialart,
                        0 AS Einzugsgebiet,
                        0 AS KonstanterZuflussTezg,
                        0 AS BefestigteFlaeche,
                        0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                      FROM
                        haltungen AS ha
                        JOIN schaechte AS sob ON ha.schoben = sob.schnam
                        JOIN schaechte AS sun ON ha.schunten = sun.schnam
                        LEFT JOIN profile ON ha.profilnam = profile.profilnam
                        LEFT JOIN entwaesserungsarten ON ha.entwart = entwaesserungsarten.bezeichnung
                        LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                        WHERE ha.haltnam NOT IN (SELECT Name FROM he.QRegler) 
                        AND ha.haltungstyp = 'Q-Regler'{auswahl};
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_qregler (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} Q-Regler eingefügt", 0.90)
                    self.progress_bar.setValue(90)
        return True

    def _hregler(self) -> bool:
        """Export H-Regler"""

        if QKan.config.check_export.hregler:

            # Nur Daten fuer ausgewaehlte Teilgebiete
            if len(self.liste_teilgebiete) != 0:
                lis = "', '".join(self.liste_teilgebiete)
                auswahl = f" AND ha.teilgebiet in ('{lis}')"
            else:
                auswahl = ""

            if self.update:
                sql = f"""
                  UPDATE he.HRegler SET
                  ( SchachtOben, SchachtUnten,
                    Laenge, 
                    SohlhoeheOben,
                    SohlhoeheUnten, 
                    Geometrie1, Geometrie2, 
                    Kanalart,
                    Rauigkeitsbeiwert, Anzahl,
                    RauhigkeitAnzeige,
                    Profiltyp,
                    LastModified, 
                    Materialart, 
                    Einzugsgebiet, 
                    KonstanterZuflussTezg, 
                    BefestigteFlaeche, 
                    UnbefestigteFlaeche, Geometry) =
                  ( SELECT
                      ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                      coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                      coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                      coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                      ha.hoehe AS Geometrie1, ha.breite AS Geometrie2,
                      entwaesserungsarten.he_nr AS Kanalart,
                      coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                      coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                      profile.he_nr AS Profiltyp,
                      coalesce(ha.createdat, datetime('now')) AS LastModified, 
                      28 AS Materialart, 
                      0 AS Einzugsgebiet, 
                      0 AS KonstanterZuflussTezg, 
                      0 AS BefestigteFlaeche, 
                      0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                    FROM
                      haltungen AS ha 
                      JOIN schaechte AS sob ON ha.schoben = sob.schnam
                      JOIN schaechte AS sun ON ha.schunten = sun.schnam
                      LEFT JOIN profile ON ha.profilnam = profile.profilnam
                      LEFT JOIN entwaesserungsarten ON ha.entwart = entwaesserungsarten.bezeichnung
                      LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                      WHERE ha.haltungstyp = 'H-Regler' AND ha.haltnam = he.HRegler.Name{auswahl})
                  WHERE he.Rohr.Name IN 
                  ( SELECT haltnam FROM haltungen AND haltungen.haltungstyp = 'H-Regler'){auswahl}
                    """

                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_hregler (1)"):
                    return False

            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM haltungen"
                if not self.db_qkan.sql(sql, "dbQK: export_to_he8.export_hregler (2)"):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (14) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen H-Regler", "Keine H-Regler vorhanden")
                else:
                    nr0 = self.nextid
                    id0 = self.nextid - idmin

                    sql = f"""
                      INSERT INTO he.HRegler
                      ( Id, 
                        Name, SchachtOben, SchachtUnten, 
                        Laenge, 
                        SohlhoeheOben,
                        SohlhoeheUnten, 
                        Geometrie1, Geometrie2, 
                        Kanalart, 
                        Rauigkeitsbeiwert, Anzahl, 
                        Rauigkeitsansatz, 
                        RauhigkeitAnzeige,
                        Profiltyp,
                        LastModified, 
                        Materialart, 
                        Einzugsgebiet, 
                        KonstanterZuflussTezg, 
                        BefestigteFlaeche, 
                        UnbefestigteFlaeche, Geometry)
                      SELECT
                        ha.rowid + {id0} AS Id, 
                        ha.haltnam AS Name, ha.schoben AS SchachtOben, ha.schunten AS SchachtUnten,
                        coalesce(ha.laenge, glength(ha.geom)) AS Laenge,
                        coalesce(ha.sohleoben,sob.sohlhoehe) AS SohlhoeheOben,
                        coalesce(ha.sohleunten,sun.sohlhoehe) AS SohlhoeheUnten,
                        ha.hoehe AS Geometrie1, ha.breite AS Geometrie2,
                        entwaesserungsarten.he_nr AS Kanalart,
                        coalesce(ha.ks, 1.5) AS Rauigkeitsbeiwert, 1 AS Anzahl, 
                        1 AS Rauigkeitsansatz, 
                        coalesce(ha.ks, 1.5) AS RauhigkeitAnzeige,
                        profile.he_nr AS Profiltyp,
                        coalesce(ha.createdat, datetime('now')) AS LastModified, 
                        28 AS Materialart,
                        0 AS Einzugsgebiet,
                        0 AS KonstanterZuflussTezg,
                        0 AS BefestigteFlaeche,
                        0 AS UnbefestigteFlaeche,
                      SetSrid(ha.geom, -1) AS Geometry
                      FROM
                        haltungen AS ha
                        JOIN schaechte AS sob ON ha.schoben = sob.schnam
                        JOIN schaechte AS sun ON ha.schunten = sun.schnam
                        LEFT JOIN profile ON ha.profilnam = profile.profilnam
                        LEFT JOIN entwaesserungsarten ON ha.entwart = entwaesserungsarten.bezeichnung
                        LEFT JOIN simulationsstatus AS st ON ha.simstatus = st.bezeichnung
                        WHERE ha.haltnam NOT IN (SELECT Name FROM he.HRegler) 
                        AND ha.haltungstyp = 'H-Regler'{auswahl};
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_hregler (3)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )
                    self.db_qkan.commit()

                    fortschritt(f"{self.nextid - nr0} H-Regler eingefügt", 0.90)
                    self.progress_bar.setValue(90)
        return True

    def _abflussparameter(self) -> bool:
        """Export Abflussparameter"""

        if QKan.config.check_export.abflussparameter:
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = "SELECT min(rowid) as idmin, max(rowid) as idmax FROM abflussparameter"
                if not self.db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_Abflussparameter (2)"
                ):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (15) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Pumpen", "Keine Abflussparameter vorhanden")
                else:
                    nr0 = self.nextid
                    self.nextid - idmin

                    sql = f"""
                    INSERT INTO he.AbflussParameter (
                        Name, 
                        AbflussbeiwertAnfang, AbflussbeiwertEnde, 
                        Muldenverlust, Benetzungsverlust, 
                        BenetzungSpeicherStart, MuldenauffuellgradStart, 
                        Typ, 
                        Bodenklasse, 
                        Kommentar, LastModified
                        )
                    SELECT 
                        ap.apnam,
                        ap.anfangsabflussbeiwert, ap.endabflussbeiwert,
                        ap.muldenverlust, ap.benetzungsverlust, 
                        ap.benetzung_startwert, ap.mulden_startwert, 
                        CASE WHEN ap.bodenklasse IS NULL THEN 0 ELSE 1 END AS Typ,
                        ap.bodenklasse, 
                        ap.kommentar, ap.createdat
                    FROM abflussparameter AS ap
                    LEFT JOIN he.AbflussParameter AS ha
                    ON ha.Name = ap.apnam
                    WHERE ha.Name IS NULL
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_abflussparameter (2)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )

                    fortschritt("{} Abflussparameter eingefuegt".format(self.nextid - nr0), 0.92)
                    self.progress_bar.setValue(92)

            self.db_qkan.commit()

        return True

    def _bodenklassen(self) -> bool:
        """Export der Bodenklassen"""

        if QKan.config.check_export.bodenklassen:
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                sql = (
                    "SELECT min(rowid) as idmin, max(rowid) as idmax FROM bodenklassen"
                )
                if not self.db_qkan.sql(
                    sql, "dbQK: export_to_he8.export_Bodenklassen (2)"
                ):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                else:
                    fehlermeldung(
                        "Fehler (16) in QKan_Export",
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}",
                    )

                if idmin is None:
                    meldung("Einfügen Pumpen", "Keine Bodenklassen vorhanden")
                else:
                    nr0 = self.nextid
                    self.nextid - idmin

                    sql = f"""
                    INSERT INTO he.Bodenklasse (
                        Name, 
                        InfiltrationsrateAnfang, InfiltrationsrateEnde, InfiltrationsrateStart, 
                        Rueckgangskonstante, Regenerationskonstante, Saettigungswassergehalt, 
                        Kommentar, LastModified
                    )
                    SELECT 
                        bk.bknam, 
                        bk.infiltrationsrateanfang, bk.infiltrationsrateende, bk.infiltrationsratestart, 
                        bk.rueckgangskonstante, bk.regenerationskonstante, bk.saettigungswassergehalt, 
                        bk.kommentar, bk.createdat
                    FROM bodenklassen AS bk
                    LEFT JOIN he.Bodenklasse AS hb
                    ON hb.Name = bk.bknam
                    WHERE hb.Name IS NULL
                    """

                    if not self.db_qkan.sql(
                        sql, "dbQK: export_to_he8.export_abflussparameter (2)"
                    ):
                        return False

                    self.nextid += idmax - idmin + 1
                    self.db_qkan.sql(
                        "UPDATE he.Itwh$ProgInfo SET NextId = ?",
                        parameters=(self.nextid,),
                    )

                    fortschritt("{} Abflussparameter eingefuegt".format(self.nextid - nr0), 1.00)
                    self.progress_bar.setValue(100)
            self.db_qkan.commit()

        return True
