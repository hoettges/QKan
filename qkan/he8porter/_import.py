from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

logger = get_logger("QKan.he8._import")


class ImportTask:
    def __init__(self, db_qkan: DBConnection):
        # all parameters are passed via QKan.config
        self.db_qkan = db_qkan
        self.append = QKan.config.check_import.append
        self.update = QKan.config.check_import.update
        self.allrefs = QKan.config.check_import.allrefs
        self.fangradius = QKan.config.fangradius

        self.epsg = QKan.config.epsg

    def run(self) -> bool:

        result = all(
            [
                self._reftables(),
                self._profile(),
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
                self._einleitdirekt(),
                self._aussengebiete(),
                self._einzugsgebiet(),
                self._tezg(),
            ]
        )

        return result

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für HE-Import füllen"""

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert
        daten = [
            ('Regenwasser', 'R', 'Regenwasser', 1, 2, 'R', 'KR', 0, 0),
            ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1, 'S', 'KS', 0, 0),
            ('Mischwasser', 'M', 'Mischwasser', 0, 0, 'M', 'KM', 0, 0),
            ('RW Druckleitung', 'RD', 'Transporthaltung ohne Anschlüsse', 1, 2, None, 'DR', 1, 1),
            ('SW Druckleitung', 'SD', 'Transporthaltung ohne Anschlüsse', 2, 1, None, 'DS', 1, 1),
            ('MW Druckleitung', 'MD', 'Transporthaltung ohne Anschlüsse', 0, 0, None, 'DW', 1, 1),
            ('RW nicht angeschlossen', 'RT', 'Transporthaltung ohne Anschlüsse', 1, 2, None, None, 1, 0),
            ('MW nicht angeschlossen', 'MT', 'Transporthaltung ohne Anschlüsse', 0, 0, None, None, 1, 0),
            ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, None, None, 0, None),
            ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None, 0, None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau, transport, druckdicht)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "he8_import Referenzliste entwaesserungsarten", daten, many=True):
            return False

        daten = [
            ('Haltung', None),
            ('Drossel', 'HYSTEM-EXTRAN 8'),
            ('H-Regler', 'HYSTEM-EXTRAN 8'),
            ('Q-Regler', 'HYSTEM-EXTRAN 8'),
            ('Schieber', 'HYSTEM-EXTRAN 8'),
            ('GrundSeitenauslass', 'HYSTEM-EXTRAN 8'),
            ('Pumpe', None),
            ('Wehr', None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO haltungstypen (bezeichnung, bemerkung)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM haltungstypen)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste haltungstypen", daten, many=True):
            return False

        daten = [
            ('Kreis', 1, 1, None),
            ('Rechteck (geschlossen)', 2, 3, None),
            ('Ei (B:H = 2:3)', 3, 5, None),
            ('Maul (B:H = 2:1,66)', 4, 4, None),
            ('Halbschale (offen) (B:H = 2:1)', 5, None, None),
            ('Kreis gestreckt (B:H=2:2.5)', 6, None, None),
            ('Kreis überhöht (B:H=2:3)', 7, None, None),
            ('Ei überhöht (B:H=2:3.5)', 8, None, None),
            ('Ei breit (B:H=2:2.5)', 9, None, None),
            ('Ei gedrückt (B:H=2:2)', 10, None, None),
            ('Drachen (B:H=2:2)', 11, None, None),
            ('Maul (DIN) (B:H=2:1.5)', 12, None, None),
            ('Maul überhöht (B:H=2:2)', 13, None, None),
            ('Maul gedrückt (B:H=2:1.25)', 14, None, None),
            ('Maul gestreckt (B:H=2:1.75)', 15, None, None),
            ('Maul gestaucht (B:H=2:1)', 16, None, None),
            ('Haube (B:H=2:2.5)', 17, None, None),
            ('Parabel (B:H=2:2)', 18, None, None),
            ('Rechteck mit geneigter Sohle (B:H=2:1)', 19, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:1)', 20, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:2)', 21, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.2B)', 22, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.2B)', 23, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.2B)', 24, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.4B)', 25, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.4B)', 26, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.4B)', 27, None, None),
            ('Druckrohrleitung', 50, None, None),
            ('Sonderprofil', 68, 2, None),
            ('Gerinne', 69, None, None),
            ('Trapez (offen)', 900, None, None),
            ('Doppeltrapez (offen)', 901, None, None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO profile (profilnam, he_nr, mu_nr, kp_key)
                    SELECT ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT profilnam FROM profile)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste profile", daten, many=True):
            return False

        daten = [
             ('Offline', 1),
             ('Online Schaltstufen', 2),
             ('Online Kennlinie', 3),
             ('Online Wasserstandsdifferenz', 4),
             ('Ideal', 5),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO pumpentypen (bezeichnung, he_nr)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM pumpentypen)"""

        if not self.db_qkan.sql(sql, "he8_import Referenzliste pumpentypen", daten, many=True):
            return False

        self.db_qkan.commit()
        return True

    def _schaechte(self) -> bool:
        """Import der Schächte"""

        if QKan.config.check_import.schaechte:
            if self.append:
                sql = """
                WITH ea AS (
                    SELECT 
                        bezeichnung, 
                        he_nr, 
                        CASE WHEN transport IS NULL THEN 0 ELSE transport END AS transport, 
                        CASE WHEN druckdicht IS NULL THEN 0 ELSE druckdicht END AS druckdicht
                    FROM entwaesserungsarten 
                    WHERE he_nr IS NOT NULL
                    GROUP BY he_nr, transport, druckdicht
                )
                INSERT INTO schaechte (
                    schnam, xsch, ysch, 
                    sohlhoehe, deckelhoehe, 
                    durchm, 
                    druckdicht, 
                    entwart, schachttyp, simstatus, 
                    kommentar, createdat, geop, geom
                )
                SELECT 
                    sh.Name AS schnam,
                    x(sh.Geometry) AS xsch, 
                    y(sh.Geometry) AS ysch, 
                    sh.Sohlhoehe AS sohlhoehe, 
                    sh.Deckelhoehe AS deckelhoehe, 
                    sh.Durchmesser/1000 AS durchm, 
                    sh.Druckdichterdeckel AS druckdicht, 
                    ea.bezeichnung AS entwart, 
                    'Schacht' AS schachttyp,
                    si.bezeichnung AS simstatus, 
                    sh.Kommentar AS kommentar, 
                    sh.Lastmodified AS createdat,
                    SetSrid(sh.Geometry, :epsg) AS geop,
                    CastToMultiPolygon(MakePolygon(MakeCircle(x(sh.Geometry),
                                                              y(sh.Geometry),
                                                              coalesce(sh.Durchmesser/1000.0, 1.0),
                                                              :epsg)
                                       )
                    ) AS geom
                FROM he.Schacht AS sh
                LEFT JOIN ea 
                ON ea.he_nr = sh.Kanalart AND 
                    sh.DruckdichterDeckel = ea.druckdicht AND
                    ea.transport = 0 
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = sh.Planungsstatus
                LEFT JOIN schaechte AS sq
                ON sh.Name = sq.schnam
                WHERE sq.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Schächte", params):
                    return False

                self.db_qkan.commit()

        return True

    def _auslaesse(self) -> bool:
        """Import der Auslässe"""

        if QKan.config.check_import.auslaesse:
            if self.append:
                sql = """
                INSERT INTO schaechte (
                    schnam, xsch, ysch, 
                    sohlhoehe, deckelhoehe, 
                    schachttyp, simstatus, 
                    kommentar, createdat, geop, geom
                )
                SELECT 
                    sh.Name AS schnam,
                    x(sh.Geometry) AS xsch, 
                    y(sh.Geometry) AS ysch, 
                    sh.Sohlhoehe AS sohlhoehe, 
                    sh.Gelaendehoehe AS deckelhoehe, 
                    'Auslass' AS schachttyp,
                    si.bezeichnung AS simstatus,
                    sh.Kommentar AS kommentar, 
                    sh.Lastmodified AS createdat,
                    SetSrid(sh.Geometry, :epsg) AS geop,
                    CastToMultiPolygon(MakePolygon(MakeCircle(x(sh.Geometry),
                                                              y(sh.Geometry),
                                                              1.0,
                                                              :epsg)
                                       )
                    ) AS geom
                FROM he.Auslass AS sh
                LEFT JOIN simulationsstatus AS si
                ON si.he_nr = sh.Planungsstatus
                LEFT JOIN schaechte AS sq
                ON sh.Name = sq.schnam
                WHERE sq.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Auslässe", params):
                    return False

                self.db_qkan.commit()

        return True

    def _speicher(self) -> bool:
        """Import der Speicher"""

        if QKan.config.check_import.speicher:
            if self.append:
                sql = """
                INSERT INTO schaechte (
                    schnam, xsch, ysch, 
                    sohlhoehe, deckelhoehe, 
                    schachttyp, simstatus, 
                    kommentar, createdat, geop, geom
                )
                SELECT 
                    sh.Name AS schnam,
                    x(sh.Geometry) AS xsch, 
                    y(sh.Geometry) AS ysch, 
                    sh.Sohlhoehe AS sohlhoehe, 
                    sh.Gelaendehoehe AS deckelhoehe, 
                    'Speicher' AS schachttyp,
                    si.bezeichnung AS simstatus,
                    sh.Kommentar AS kommentar, 
                    sh.Lastmodified AS createdat,
                    SetSrid(sh.Geometry, :epsg) AS geop,
                    CastToMultiPolygon(MakePolygon(MakeCircle(x(sh.Geometry),
                                                              y(sh.Geometry),
                                                              1.0,
                                                              :epsg)
                                       )
                    ) AS geom
                FROM he.Speicherschacht AS sh
                LEFT JOIN simulationsstatus AS si
                ON si.he_nr = sh.Planungsstatus
                LEFT JOIN schaechte AS sq
                ON sh.Name = sq.schnam
                WHERE sq.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Speicher", params):
                    return False

                self.db_qkan.commit()

        return True

    def _haltungen(self) -> bool:
        """Import der Haltungen"""

        # Haltungen
        if QKan.config.check_import.haltungen:
            if self.append:
                sql = """
                WITH ea AS (
                    SELECT 
                        bezeichnung, 
                        he_nr, 
                        CASE WHEN transport IS NULL THEN 0 ELSE transport END AS transport, 
                        CASE WHEN druckdicht IS NULL THEN 0 ELSE druckdicht END AS druckdicht
                    FROM entwaesserungsarten 
                    WHERE he_nr IS NOT NULL
                    GROUP BY he_nr, transport, druckdicht
                )
                INSERT INTO haltungen (
                    haltnam, schoben, schunten, 
                    hoehe, breite, laenge, 
                    sohleoben, sohleunten,
                    haltungstyp,
                    profilnam, entwart, 
                    ks, simstatus,  
                    kommentar, createdat, 
                    geom
                )
                SELECT 
                    ro.Name AS haltnam, 
                    ro.Schachtoben AS schoben, 
                    ro.Schachtunten AS schunten, 
                    ro.Geometrie1 AS hoehe, 
                    ro.Geometrie2 AS breite, 
                    ro.Laenge AS laenge, 
                    ro.SohlhoeheOben AS sohleoben, 
                    ro.SohlhoeheUnten AS sohleunten, 
                    'Haltung' AS haltungstyp, 
                    CASE WHEN ro.Profiltyp = 68 
                         THEN ro.Sonderprofilbezeichnung 
                         ELSE pr.profilnam END AS profilnam, 
                    ea.bezeichnung AS entwart, 
                    ro.Rauigkeitsbeiwert AS ks, 
                    si.bezeichnung AS simstatus,
                    ro.Kommentar AS kommentar, 
                    ro.Lastmodified AS createdat, 
                    SetSrid(Geometry,:epsg) AS geom
                FROM he.Rohr AS ro
                LEFT JOIN (SELECT he_nr, profilnam FROM profile WHERE he_nr <> 68 GROUP BY he_nr) AS pr
                ON ro.Profiltyp = pr.he_nr
                LEFT JOIN ea 
                ON ea.he_nr = ro.Kanalart AND 
                    ea.druckdicht = (ro.Abflussart % 2) AND             -- 2 = Abfluss im offenen Profil wird in QKan wie 0 verarbeitet  
                    ea.transport = ro.Transporthaltung 
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = ro.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = ro.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Haltungen", params):
                    return False

                self.db_qkan.commit()

        return True

    def _wehre(self) -> bool:
        """Import der Wehre"""

        if QKan.config.check_import.wehre:
            if self.append:
                # sql = """
                # WITH nodes AS (SELECT Name FROM he.Schacht
                #      UNION SELECT Name FROM he.Auslass
                #      UNION SELECT Name FROM he.Speicherschacht)
                # INSERT INTO wehre_data (
                #     wnam, schoben, schunten,
                #     wehrtyp, schwellenhoehe, kammerhoehe,
                #     laenge, uebeiwert, simstatus,
                #     kommentar, createdat)
                # SELECT
                #     we.Name AS wnam,
                #     we.Schachtoben AS schoben,
                #     we.Schachtunten AS schunten,
                #     we.Typ AS typ_he,
                #     we.Schwellenhoehe AS schwellenhoehe,
                #     we.Geometrie1 AS kammerhoehe,
                #     we.Geometrie2 AS laenge,
                #     we.Ueberfallbeiwert AS uebeiwert,
                #     si.bezeichnung AS simstatus,
                #     we.Kommentar AS kommentar,
                #     we.Lastmodified AS createdat
                # FROM he.Wehr AS we
                # LEFT JOIN nodes AS so
                # ON we.Schachtoben = so.Name
                # LEFT JOIN nodes AS su
                # ON we.Schachtunten = su.Name
                # LEFT JOIN simulationsstatus AS si
                # ON si.he_nr = we.Planungsstatus
                # LEFT JOIN wehre AS wq
                # ON wq.wnam = we.Name
                # WHERE wq.pk IS NULL
                # """
                #
                # if not self.db_qkan.sql(sql, "he8_import Wehre"):
                #     return False

                sql = """
                INSERT INTO haltungen (
                    haltnam, schoben, schunten,
                    hoehe, breite,
                    sohleoben, sohleunten,
                    haltungstyp,
                    simstatus,
                    kommentar, createdat, 
                    geom)
                SELECT 
                    we.Name AS haltnam,
                    we.Schachtoben AS schoben, 
                    we.Schachtunten AS schunten, 
                    we.Geometrie1 AS hoehe, 
                    we.Geometrie2 AS breite,
                    we.Schwellenhoehe AS sohleoben, 
                    we.Schwellenhoehe AS sohleunten, 
                    'Wehr' AS haltungstyp, 
                    si.bezeichnung AS simstatus, 
                    we.Kommentar AS kommentar, 
                    we.Lastmodified AS createdat,
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.Wehr AS we
                LEFT JOIN (SELECT he_nr, profilnam FROM profile WHERE he_nr <> 68 GROUP BY he_nr) AS pr
                ON we.Profiltyp = pr.he_nr
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = we.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = we.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Wehre", params):
                    return False

                self.db_qkan.commit()

        return True

    def _pumpen(self) -> bool:
        """Import der Pumpen"""

        if QKan.config.check_import.pumpen:
            if self.append:
                # sql = """
                # WITH nodes AS (SELECT Name FROM he.Schacht
                #      UNION SELECT Name FROM he.Auslass
                #      UNION SELECT Name FROM he.Speicherschacht)
                # INSERT INTO pumpen_data (
                #     pnam, schoben, schunten, pumpentyp, steuersch, einschalthoehe, ausschalthoehe,
                #     simstatus, kommentar, createdat)
                # SELECT
                #     pu.Name AS pnam,
                #     pu.Schachtoben AS schoben,
                #     pu.Schachtunten AS schunten,
                #     pt.bezeichnung AS pumpentyp,
                #     pu.Steuerschacht AS steuersch,
                #     pu.Einschalthoehe AS einschalthoehe,
                #     pu.Ausschalthoehe AS ausschalthoehe,
                #     si.bezeichnung AS simstatus,
                #     pu.Kommentar AS kommentar,
                #     pu.Lastmodified AS createdat
                # FROM he.Pumpe AS pu
                # LEFT JOIN nodes AS so
                # ON pu.Schachtoben = SO.Name
                # LEFT JOIN nodes AS su
                # ON pu.Schachtunten = su.Name
                # LEFT JOIN simulationsstatus AS si
                # ON si.he_nr = pu.Planungsstatus
                # LEFT JOIN pumpentypen AS pt
                # ON pt.he_nr = pu.Typ
                # LEFT JOIN pumpen AS pq
                # ON pq.pnam = pu.Name
                # WHERE pq.pk IS NULL
                # """
                #
                # if not self.db_qkan.sql(sql, "he8_import Pumpen"):
                #     return False

                sql = """
                INSERT INTO haltungen (
                    haltnam, schoben, schunten,
                    hoehe,
                    haltungstyp, 
                    simstatus,
                    kommentar, createdat, 
                    geom)
                SELECT 
                    pu.Name AS haltnam,
                    pu.Schachtoben AS schoben, 
                    pu.Schachtunten AS schunten,
                    0.3 AS hoehe,                   /* nur fuer Laengsschnitt */ 
                    'Pumpe' AS haltungstyp, 
                    si.bezeichnung AS simstatus, 
                    pu.Kommentar AS kommentar, 
                    pu.Lastmodified AS createdat,
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.Pumpe AS pu
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = pu.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = pu.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Pumpen", params):
                    return False

                self.db_qkan.commit()

        return True

    def _drosseln(self) -> bool:
        """Import der Drosseln"""

        if QKan.config.check_import.drosseln:
            if self.append:
                sql = """
                INSERT INTO haltungen (
                    haltnam, schoben, schunten,
                    hoehe,
                    haltungstyp, 
                    simstatus,
                    kommentar, createdat, 
                    geom)
                SELECT 
                    dr.Name AS haltnam,
                    dr.Schachtoben AS schoben, 
                    dr.Schachtunten AS schunten, 
                    dr.Sohlabstand AS hoehe, 
                    'Drossel' AS haltungstyp, 
                    si.bezeichnung AS simstatus, 
                    dr.Kommentar AS kommentar, 
                    dr.Lastmodified AS createdat,
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.Drossel AS dr
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = dr.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = dr.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Drosseln", params):
                    return False

                self.db_qkan.commit()
        return True

    def _schieber(self) -> bool:
        """Import der Schieber"""

        if QKan.config.check_import.schieber:
            if self.append:
                sql = """
                INSERT INTO haltungen (
                    haltnam, schoben, schunten,
                    sohleoben, sohleunten,
                    hoehe, breite,
                    ks,
                    profilnam,
                    haltungstyp,
                    simstatus,
                    kommentar, createdat, 
                    geom
                )
                SELECT 
                    sr.Name AS haltnam,
                    sr.Schachtoben AS schoben, 
                    sr.Schachtunten AS schunten, 
                    sr.Anfangsstellung AS sohleoben,
                    sr.Anfangsstellung AS sohleunten,
                    round(sr.MaximaleHubHoehe - sr.Anfangsstellung, 4) AS hoehe,
                    sr.Geometrie2 AS breite, 
                    sr.Verluste AS ks, 
                    pr.profilnam AS profilnam, 
                    'Schieber' AS haltungstyp, 
                    si.bezeichnung AS simstatus, 
                    sr.Kommentar AS kommentar, 
                    sr.Lastmodified AS createdat,
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.Schieber AS sr
                LEFT JOIN (SELECT he_nr, profilnam FROM profile WHERE he_nr <> 68 GROUP BY he_nr) AS pr
                ON sr.Profiltyp = pr.he_nr
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = sr.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = sr.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Schieber", params):
                    return False

                self.db_qkan.commit()
        return True

    def _qregler(self) -> bool:
        """Import der Q-Regler"""

        if QKan.config.check_import.qregler:
            if self.append:
                sql = """
                WITH ea AS (
                    SELECT 
                        bezeichnung, 
                        he_nr, 
                        CASE WHEN transport IS NULL THEN 0 ELSE transport END AS transport, 
                        CASE WHEN druckdicht IS NULL THEN 0 ELSE druckdicht END AS druckdicht
                    FROM entwaesserungsarten 
                    WHERE he_nr IS NOT NULL
                    GROUP BY he_nr, transport, druckdicht
                )
                INSERT INTO haltungen (
                    haltnam, schoben, schunten, 
                    hoehe, breite, laenge, 
                    sohleoben, sohleunten,
                    profilnam, entwart, ks,
                    haltungstyp, 
                    simstatus,  
                    kommentar, createdat, 
                    geom
                )
                SELECT 
                    qr.Name AS haltnam, 
                    qr.Schachtoben AS schoben, 
                    qr.Schachtunten AS schunten, 
                    qr.Geometrie1 AS hoehe, 
                    qr.Geometrie2 AS breite, 
                    qr.Laenge AS laenge, 
                    qr.SohlhoeheOben AS sohleoben, 
                    qr.SohlhoeheUnten AS sohleunten, 
                    pr.profilnam AS profilnam, 
                    ea.bezeichnung AS entwart, 
                    qr.Rauigkeitsbeiwert AS ks, 
                    'Q-Regler' AS haltungstyp, 
                    si.bezeichnung AS simstatus,
                    qr.Kommentar AS kommentar, 
                    qr.Lastmodified AS createdat, 
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.qRegler AS qr
                LEFT JOIN (SELECT he_nr, profilnam FROM profile WHERE he_nr <> 68 GROUP BY he_nr) AS pr
                ON qr.Profiltyp = pr.he_nr
                LEFT JOIN ea 
                ON ea.he_nr = qr.Kanalart AND 
                    ea.druckdicht = (qr.Abflussart % 2) AND             -- 2 = Abfluss im offenen Profil wird in QKan wie 0 verarbeitet  
                    ea.transport = qr.Transporthaltung 
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = qr.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = qr.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Q-Regler", params):
                    return False
                self.db_qkan.commit()
        return True

    def _hregler(self) -> bool:
        """Import der H-Regler"""

        if QKan.config.check_import.hregler:
            if self.append:
                sql = """
                WITH ea AS (
                    SELECT 
                        bezeichnung, 
                        he_nr, 
                        CASE WHEN transport IS NULL THEN 0 ELSE transport END AS transport, 
                        CASE WHEN druckdicht IS NULL THEN 0 ELSE druckdicht END AS druckdicht
                    FROM entwaesserungsarten 
                    WHERE he_nr IS NOT NULL
                    GROUP BY he_nr, transport, druckdicht
                )
                INSERT INTO haltungen (
                    haltnam, schoben, schunten, 
                    hoehe, breite, laenge, 
                    sohleoben, sohleunten,
                    profilnam, entwart, ks,
                    haltungstyp,
                    simstatus,
                    kommentar, createdat, 
                    geom
                )
                SELECT 
                    hr.Name AS haltnam,
                    hr.Schachtoben AS schoben,
                    hr.Schachtunten AS schunten,
                    hr.Geometrie1 AS hoehe,
                    hr.Geometrie2 AS breite,
                    hr.Laenge AS laenge,
                    hr.SohlhoeheOben AS sohleoben,
                    hr.SohlhoeheUnten AS sohleunten,
                    pr.profilnam AS profilnam,
                    ea.bezeichnung AS entwart,
                    hr.Rauigkeitsbeiwert AS ks,
                    'H-Regler' AS haltungstyp,
                    si.bezeichnung AS simstatus,
                    hr.Kommentar AS kommentar,
                    hr.Lastmodified AS createdat,
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.hRegler AS hr
                LEFT JOIN (SELECT he_nr, profilnam FROM profile WHERE he_nr <> 68 GROUP BY he_nr) AS pr
                ON hr.Profiltyp = pr.he_nr
                LEFT JOIN ea 
                ON ea.he_nr = hr.Kanalart AND 
                    ea.druckdicht = (hr.Abflussart % 2) AND             -- 2 = Abfluss im offenen Profil wird in QKan wie 0 verarbeitet  
                    ea.transport = hr.Transporthaltung 
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = hr.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = hr.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import H-Regler", params):
                    return False
                self.db_qkan.commit()
        return True

    def _grundseitenauslaesse(self) -> bool:
        """Import der Grund- und Seitenauslässe"""

        if QKan.config.check_import.grundseitenauslaesse:
            if self.append:
                sql = """
                INSERT INTO haltungen (
                    haltnam, schoben, schunten,
                    sohleoben, sohleunten,
                    hoehe, breite,
                    ks,
                    profilnam,
                    haltungstyp,
                    simstatus,  
                    kommentar, createdat, 
                    geom
                )
                SELECT 
                    gs.Name AS haltnam, 
                    gs.Schachtoben AS schoben, 
                    gs.Schachtunten AS schunten,
                    gs.HoeheUnterkante AS sohleoben, 
                    gs.HoeheUnterkante AS sohleunten, 
                    gs.Geometrie1 AS hoehe,
                    gs.Geometrie2 AS breite,
                    gs.Auslassbeiwert AS ks,
                    pr.profilnam AS profilnam,
                    'GrundSeitenauslass' AS haltungstyp, 
                    si.bezeichnung AS simstatus,
                    gs.Kommentar AS kommentar, 
                    gs.Lastmodified AS createdat, 
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.grundseitenauslass AS gs
                LEFT JOIN (SELECT he_nr, profilnam FROM profile WHERE he_nr <> 68 GROUP BY he_nr) AS pr
                ON gs.Profiltyp = pr.he_nr
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = gs.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = gs.Name
                WHERE ha.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Grund- und Seitenauslässe", params):
                    return False
                self.db_qkan.commit()
        return True

    def _flaechen(self) -> bool:
        """Import der Flächen"""

        if QKan.config.check_import.flaechen:
            if self.append:
                sql = f"""
                INSERT INTO flaechen ( 
                    flnam, haltnam, neigkl, regenschreiber, 
                    abflussparameter, aufteilen, kommentar, createdat, geom
                ) 
                SELECT
                    fl.Name AS flnam, 
                    fl.Haltung AS haltnam, 
                    fl.Neigungsklasse AS neigkl, 
                    fl.Regenschreiber AS regenschreiber, 
                    fl.Parametersatz AS abflussparameter,
                    false AS aufteilen, 
                    fl.Kommentar AS kommentar, 
                    fl.Lastmodified AS createdat, 
                    SetSrid(Geometry, :epsg) AS geom
                FROM he.Flaeche AS fl
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Flaechen", params):
                    return False

                self.db_qkan.commit()

                sql = f"""
                INSERT INTO linkfl (
                    flnam, 
                    haltnam, 
                    abflusstyp,
                    speicherzahl,
                    speicherkonst,
                    fliesszeitkanal,
                    fliesszeitflaeche,
                    glink
                )
                SELECT
                    fl.Name                     AS flnam,
                    fl.Haltung                  AS haltnam,
                    at.abflusstyp               AS abflusstyp,
                    fl.AnzahlSpeicher           AS speicherzahl,
                    fl.Speicherkonstante        AS speicherkonst,
                    fl.LaengsteFliesszeitKanal  AS fliesszeitkanal,
                    CASE fl.BerechnungSpeicherkonstante 
                        WHEN 1 THEN fl.FliesszeitOberflaeche
                        WHEN 2 THEN fl.Schwerpunktlaufzeit
                        ELSE 0. END             AS fliesszeitflaeche,  
                    SetSrid(MakeLine(
                        PointOnSurface(Buffer(fl.Geometry, -1.1*{self.fangradius})), 
                        Centroid(ro.Geometry)
                        ),  :epsg
                    )                           AS link
                    FROM he.Rohr AS ro
                    INNER JOIN he.Flaeche AS fl
                    ON fl.Haltung = ro.Name
                    LEFT JOIN abflusstypen AS at
                    ON at.he_nr = fl.BerechnungSpeicherkonstante
                    WHERE fl.Geometry IS NOT NULL AND ro.Geometry IS NOT NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import linkfl", params):
                    return False

                self.db_qkan.commit()

        return True

    def _abflussparameter(self) -> bool:
        """Import der Abflussbeiwerte

        Wahlweise (allrefs) werden nur die in QKan fehlenden Abflussbeiwerte, die in der
        HE-Datenbank in Flächen verwendet werden, importiert"""

        if QKan.config.check_import.abflussparameter:

            # Auch nicht referenzierte Datensätze importieren
            if self.allrefs:
                filter = ""
            else:
                filter = """
                INNER JOIN he.Flaeche AS fl_he
                ON fl_he.Parametersatz = ap_he.Name"""

            if self.append:

                sql = f"""
                INSERT INTO abflussparameter (
                    apnam, anfangsabflussbeiwert, endabflussbeiwert, 
                    benetzungsverlust, muldenverlust, 
                    benetzung_startwert, mulden_startwert, 
                    bodenklasse, kommentar, createdat 
                )
                SELECT 
                    ap_he.name AS apnam, 
                    ap_he.AbflussbeiwertAnfang AS anfangsabflussbeiwert,
                    ap_he.AbflussbeiwertEnde AS endabflussbeiwert,
                    ap_he.Benetzungsverlust AS benetzungsverlust, 
                    ap_he.Muldenverlust AS muldenverlust,
                    ap_he.BenetzungSpeicherStart AS benetzung_startwert, 
                    ap_he.MuldenauffuellgradStart AS mulden_startwert, 
                    ap_he.Bodenklasse AS bodenklasse,
                    ap_he.Kommentar AS kommentar, 
                    ap_he.Lastmodified AS createdat 
                FROM he.AbflussParameter AS ap_he
                LEFT JOIN abflussparameter as ap_qk
                ON ap_he.Name = ap_qk.apnam
                {filter}
                WHERE ap_qk.pk IS NULL
                GROUP BY ap_he.Name
                """

                if not self.db_qkan.sql(sql, "he8_import Abflussparameter"):
                    return False

                self.db_qkan.commit()

        return True

    def _bodenklassen(self) -> bool:
        """Import der Bodenklassen

        Wahlweise (allrefs) werden nur die in QKan fehlenden Bodenklassen, die in der
        HE-Datenbank in Abflussparametern verwendet werden, importiert"""

        if QKan.config.check_import.bodenklassen:

            # Auch nicht referenzierte Datensätze importieren
            if self.allrefs:
                filter = ""
            else:
                filter = """
                INNER JOIN he.abflussparameter AS ap_he
                ON ap_he.bodenklasse = bk_he.Name"""

            if self.append:
                sql = f"""
                INSERT INTO bodenklassen (
                    bknam, infiltrationsrateanfang, infiltrationsrateende, 
                    infiltrationsratestart, rueckgangskonstante, 
                    regenerationskonstante, saettigungswassergehalt, 
                    kommentar, createdat
                )
                SELECT
                    bk_he.Name AS bknam, 
                    bk_he.InfiltrationsrateAnfang AS infiltrationsrateanfang, 
                    bk_he.InfiltrationsrateEnde AS infiltrationsrateende, 
                    bk_he.InfiltrationsrateStart AS infiltrationsratestart, 
                    bk_he.Rueckgangskonstante AS rueckgangskonstante, 
                    bk_he.Regenerationskonstante AS regenerationskonstante, 
                    bk_he.Saettigungswassergehalt AS saettigungswassergehalt, 
                    bk_he.Kommentar AS kommentar, 
                    bk_he.LastModified AS createdat
                FROM he.Bodenklasse AS bk_he
                LEFT JOIN bodenklassen AS bk_qk
                ON bk_he.Name = bk_qk.bknam{filter}
                WHERE bk_qk.pk IS NULL
                GROUP BY bk_he.Name
                """

                if not self.db_qkan.sql(sql, "he8_import Bodenklassen"):
                    return False

                self.db_qkan.commit()

        return True

    def _profile(self) -> bool:
        """Import der Rohrprofile

        Wahlweise (allrefs) werden nur die in QKan fehlenden Rorhprifle, die in der
        HE-Datenbank in Abflussparametern verwendet werden, importiert"""

        if QKan.config.check_import.rohrprofile:

            # Auch nicht referenzierte Datensätze importieren
            if self.allrefs:
                filter = ""
            else:
                filter = """
                INNER JOIN (
                    SELECT Sonderprofilbezeichnung
                    FROM he.rohr
                    WHERE Profiltyp = 68
                    ) AS ha_he
                ON ha_he.Sonderprofilbezeichnung = pr_he.Name"""

            if self.append:
                sql = f"""
                INSERT INTO profile (
                    profilnam, 
                    he_nr)
                SELECT
                    pr_he.Name,
                    68
                FROM he.Sonderprofil AS pr_he
                LEFT JOIN profile AS pr_qk
                ON pr_he.Name = pr_qk.profilnam
                {filter}
                WHERE pr_he.Id IS NULL
                GROUP BY pr_he.Name
                  """

                if not self.db_qkan.sql(sql, "he8_import Sonderprofile"):
                    return False

                self.db_qkan.commit()

    def _aussengebiete(self) -> bool:
        """Import der Aussengebiete"""

        if QKan.config.check_import.aussengebiete:
            if self.append:
                sql = f"""
                INSERT INTO aussengebiete (
                    gebnam, schnam, 
                    hoeheob, hoeheun, 
                    fliessweg, basisabfluss, 
                    cn, regenschreiber,
                    kommentar, createdat, 
                    geom 
                )
                SELECT
                    ag_he.Name AS gebnam, 
                    ag_he.Schacht AS schnam, 
                    ag_he.HoeheOben AS hoeheob, 
                    ag_he.HoeheUnten AS hoeheun, 
                    ag_he.FliessLaenge AS fliessweg, 
                    ag_he.BasisZufluss AS basisabfluss, 
                    ag_he.CNMittelwert AS cn, 
                    ag_he.Regenschreiber AS regenschreiber, 
                    ag_he.Kommentar AS kommentar, 
                    ag_he.LastModified AS createdat,
                    CastToMultiPolygon(
                        MakePolygon(
                            MakeCircle(
                                x(ag_he.Geometry),
                                y(ag_he.Geometry),
                                sqrt(ag_he.Gesamtflaeche), 
                                {self.epsg}
                    )   )   ) AS geom
                FROM he.Aussengebiet AS ag_he
                LEFT JOIN aussengebiete AS ag_qk
                ON ag_he.Name = ag_qk.gebnam
                WHERE ag_qk.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "he8_import Außengebiete"):
                    return False

                self.db_qkan.commit()

        return True

    def _einleitdirekt(self) -> bool:
        """Import der Direkteinleiter"""

        if QKan.config.check_import.einleitdirekt:
            if self.append:
                sql = """
                INSERT INTO einleit (
                    elnam, haltnam, 
                    zufluss, ew, 
                    einzugsgebiet,
                    kommentar, createdat,
                    geom
                )
                SELECT
                    el_he.Name              AS elnam,
                    el_he.Rohr              AS haltnam,
                    el_he.Zufluss           AS zufluss,
                    el_he.Einwohner         AS ew,
                    el_he.Teileinzugsgebiet AS einzugsgebiet,
                    el_he.Kommentar         AS kommentar,
                    el_he.LastModified      AS createdat,
                    SetSrid(el_he.Geometry,  :epsg
                    )                       AS geom
                FROM Einzeleinleiter AS el_he
                LEFT JOIN einleit AS el_qk
                ON el_he.Name = el_qk.elnam
                WHERE el_qk.pk IS NULL
                """

                params = {'epsg': self.epsg}
                if not self.db_qkan.sql(sql, "he8_import Direkteinleiter", params):
                    return False

                self.db_qkan.commit()

        return True

    def _einzugsgebiet(self) -> bool:
        """Import der Einzugsgebiete"""

        if QKan.config.check_import.einzugsgebiete:
            if self.append:
                sql = """
                INSERT INTO einzugsgebiete (
                    tgnam, ewdichte, wverbrauch, stdmittel,
                    fremdwas, kommentar, createdat
                ) 
                SELECT 
                    eg_he.Name AS tgnam,
                    eg_he.Einwohnerdichte AS ewdichte,
                    eg_he.Wasserverbrauch AS wverbrauch,
                    eg_he.Stundenmittel AS stdmittel,
                    eg_he.Fremdwasseranteil AS fremdwas,
                    eg_he.Kommentar AS kommentar,
                    eg_he.LastModified AS createdat
                FROM Teileinzugsgebiet AS eg_he
                LEFT JOIN einzugsgebiete AS eg_qk
                ON eg_he.Name = eg_qk.tgnam
                WHERE eg_qk.pk IS NULL
                    """
                if not self.db_qkan.sql(sql, "he8_import Einzugsgebiete"):
                    return False

                self.db_qkan.commit()

        return True

    def _tezg(self) -> bool:
        """Import der Haltungsflaechen (tezg)

        Diese sind in HYSTEM-EXTRAN zusätzlich markiert als
         - Einzugsfläche
         - Haltungsfläche
         - TWEinzugsfläche

        Dieses Attribut wird nicht in QKan übernommen. Allerdings kann
        der Flächentyp selektiert werden.
        """

        if (
            QKan.config.check_import.tezg_ef
            or QKan.config.check_import.tezg_hf
        ):

            if self.append:
                choice_ef = str(QKan.config.check_import.tezg_ef)
                choice_hf = str(QKan.config.check_import.tezg_hf)

                sql = f"""
                INSERT INTO tezg (
                    flnam, haltnam,
                    abflussparameter,
                    kommentar, createdat,
                    geom
                )
                SELECT
                    eg_he.Name AS flnam, 
                    eg_he.Haltung AS haltnam, 
                    '$Default_Unbef' AS abflussparameter,
                    eg_he.Kommentar AS kommentar, 
                    eg_he.LastModified AS createdat, 
                    SetSRID(eg_he.Geometry, {self.epsg}) AS geom
                FROM he.GipsEinzugsflaeche AS eg_he
                LEFT JOIN tezg AS eg_qk
                ON eg_he.Name = eg_qk.flnam
                WHERE (
                    (IsEinzugsflaeche and {choice_ef}) or
                    (IsHaltungsflaeche and {choice_hf})
                ) and eg_qk.pk IS NULL 
                """
                if not self.db_qkan.sql(sql, "he8_import Haltungsflächen"):
                    return False
        elif QKan.config.check_import.tezg_tf:
            if self.append:
                choice_tf = str(QKan.config.check_import.tezg_tf)
                sql = f"""
                INSERT INTO einleit (
                    elnam, haltnam, 
                    zufluss, ew, 
                    einzugsgebiet,
                    kommentar, createdat,
                    geom
                )
                SELECT
                    eg_he.Name                              AS elnam, 
                    eg_he.Haltung                           AS haltnam, 
                    area(eg_he.Geometry)/10000. 
                        * coalesce(te_he.Einwohnerdichte, 100)
                        * coalesce(te_he.Wasserverbrauch, 130)
                        * ( 24. / coalesce(te_he.Stundenmittel, 12)
                            + coalesce(te_he.Fremdwasseranteil))
                                                            AS zufluss,
                    area(eg_he.Geometry)/10000. * te_he.Einwohnerdichte
                                                            AS ew,
                    eg_he.Name                              AS einzugsgebiet,
                    eg_he.Kommentar                         AS kommentar, 
                    eg_he.LastModified                      AS createdat, 
                    SetSRID(eg_he.Geometry, {self.epsg})    AS geom
                FROM he.GipsEinzugsflaeche      AS eg_he
                LEFT JOIN he.Teileinzugsgebiet  AS te_he                -- kein JOIN, da alle Datensätze
                LEFT JOIN tezg                  AS eg_qk
                ON eg_he.Name = eg_qk.flnam
                WHERE (IsTwEinzugsflaeche and {choice_tf})
                    AND eg_qk.pk IS NULL 
                """
                if not self.db_qkan.sql(sql, "he8_import Haltungsflächen"):
                    return False


        self.db_qkan.commit()

        return True
