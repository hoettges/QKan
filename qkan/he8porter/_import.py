import logging

from qkan import QKan
from qkan.database.dbfunc import DBConnection

logger = logging.getLogger("QKan.he8.import")


class ImportTask:
    def __init__(self, db_qkan: DBConnection):
        self.db_qkan = db_qkan

        self.append = QKan.config.check_import.append
        self.update = QKan.config.check_import.update

        self.epsg = QKan.config.epsg

    def run(self) -> bool:

        result = all(
            [
                self._profile(),
                self._bodenklassen(),
                self._abflussparameter(),
                self._schaechte(),
                self._auslaesse(),
                self._speicher(),
                self._haltungen(),
                self._wehre(),
                self._pumpen(),
                self._flaechen(),
                self._einleitdirekt(),
                self._aussengebiete(),
                self._einzugsgebiet(),
                self._tezg(),
            ]
        )

        return result

    def _schaechte(self) -> bool:
        """Import der Schächte"""

        if QKan.config.check_import.schaechte:
            if self.append:
                sql = """
                INSERT INTO schaechte_data (
                    schnam, xsch, ysch, 
                    sohlhoehe, deckelhoehe, 
                    durchm, 
                    druckdicht, 
                    entwart, schachttyp, simstatus, 
                    kommentar, createdat
                )
                SELECT 
                    sh.Name AS schnam,
                    x(sh.Geometry) AS xsch, 
                    y(sh.Geometry) AS ysch, 
                    sh.Sohlhoehe AS sohlhoehe, 
                    sh.Deckelhoehe AS deckelhoehe, 
                    sh.Durchmesser/1000 AS durchm, 
                    sh.Druckdichterdeckel AS druckdicht, 
                    sh.Kanalart AS entwart, 
                    'Schacht' AS schachttyp,
                    sh.Planungsstatus AS simstatus, 
                    sh.Kommentar AS kommentar, 
                    sh.Lastmodified AS createdat
                FROM he.Schacht AS sh
                LEFT JOIN schaechte AS sq
                ON sh.Name = sq.schnam
                WHERE sq.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "he8_import Schächte"):
                    return False

                self.db_qkan.commit()

        return True

    def _auslaesse(self) -> bool:
        """Import der Auslässe"""

        if QKan.config.check_import.auslaesse:
            if self.append:
                sql = """
                INSERT INTO schaechte_data (
                    schnam, xsch, ysch, 
                    sohlhoehe, deckelhoehe, 
                    schachttyp, simstatus, 
                    kommentar, createdat
                )
                SELECT 
                    al.Name AS schnam,
                    x(al.Geometry) AS xsch, 
                    y(al.Geometry) AS ysch, 
                    al.Sohlhoehe AS sohlhoehe, 
                    al.Gelaendehoehe AS deckelhoehe, 
                    'Auslass' AS schachttyp,
                    al.Planungsstatus AS simstatus, 
                    al.Kommentar AS kommentar, 
                    al.Lastmodified AS createdat
                FROM he.Auslass AS al
                LEFT JOIN schaechte AS sq
                ON al.Name = sq.schnam
                WHERE sq.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "he8_import Auslässe"):
                    return False

                self.db_qkan.commit()

        return True

    def _speicher(self) -> bool:
        """Import der Speicher"""

        if QKan.config.check_import.speicher:
            if self.append:
                sql = """
                INSERT INTO schaechte_data (
                    schnam, xsch, ysch, 
                    sohlhoehe, deckelhoehe, 
                    schachttyp, simstatus, 
                    kommentar, createdat
                )
                SELECT 
                    sp.Name AS schnam,
                    x(sp.Geometry) AS xsch, 
                    y(sp.Geometry) AS ysch, 
                    sp.Sohlhoehe AS sohlhoehe, 
                    sp.Gelaendehoehe AS deckelhoehe, 
                    'Speicher' AS schachttyp,
                    sp.Planungsstatus AS simstatus, 
                    sp.Kommentar AS kommentar, 
                    sp.Lastmodified AS createdat
                FROM he.Speicherschacht AS sp
                LEFT JOIN schaechte AS sq
                ON sp.Name = sq.schnam
                WHERE sq.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "he8_import Speicher"):
                    return False

                self.db_qkan.commit()

        return True

    def _profile(self) -> bool:
        """Import der Profile"""

        # Profilnummern aller Sonderprofile ergänzen.
        if QKan.config.check_import.rohrprofile:
            if self.append:
                sql = """
                INSERT INTO profile (
                    profilnam, he_nr
                )
                SELECT 
                    hh.Sonderprofilbezeichnung, 68
                FROM he.Rohr AS hh
                INNER JOIN he.Sonderprofil AS sp
                ON hh.SonderprofilbezeichnungRef = sp.Id
                LEFT JOIN profile AS pr
                ON pr.profilnam = hh.Sonderprofilbezeichnung
                WHERE pr.pk IS NULL
                GROUP BY 
                    Profiltyp, hh.Sonderprofilbezeichnung, hh.SonderprofilbezeichnungRef
                """

                if not self.db_qkan.sql(sql, "he8_import Sonderprofile"):
                    return False

                self.db_qkan.commit()

        return True

    def _haltungen(self) -> bool:
        """Import der Haltungen"""

        # Haltungen
        if QKan.config.check_import.haltungen:
            if self.append:
                sql = """
                INSERT INTO haltungen_data (
                    haltnam, schoben, schunten, 
                    hoehe, breite, laenge, 
                    sohleoben, sohleunten, deckeloben, deckelunten, 
                    profilnam, entwart, 
                    ks, simstatus, 
                    kommentar, createdat, 
                    xschob, yschob, xschun, yschun
                )
                SELECT 
                    ro.Name AS haltnam, 
                    ro.Schachtoben AS schoben, 
                    ro.Schachtunten AS schunten, 
                    ro.Geometrie1 AS hoehe, 
                    ro.Geometrie2 AS breite, 
                    ro.Laenge AS laenge, 
                    ro.Sohlhoeheoben AS sohleoben, 
                    ro.Sohlhoeheunten AS sohleunten, 
                    so.Deckelhoehe AS deckeloben, 
                    su.Deckelhoehe AS deckelunten, 
                    CASE WHEN ro.Profiltyp = 68 
                         THEN ro.Sonderprofilbezeichnung 
                         ELSE pr.profilnam END AS profilnam, 
                    ea.bezeichnung AS entwart, 
                    ro.Rauigkeitsbeiwert AS ks, 
                    si.bezeichnung AS simstatus, 
                    ro.Kommentar AS kommentar, 
                    ro.Lastmodified AS createdat, 
                    x(PointN(ro.Geometry, 1)) AS xschob, 
                    y(PointN(ro.Geometry, 1)) AS yschob,
                    x(PointN(ro.Geometry, -1)) AS xschun, 
                    y(PointN(ro.Geometry, -1)) AS yschun
                FROM he.Rohr AS ro
                INNER JOIN (SELECT Name, Deckelhoehe FROM he.Schacht
                     UNION SELECT Name, Gelaendehoehe AS Deckelhoehe FROM he.Speicherschacht) AS so
                ON ro.Schachtoben = so.Name 
                INNER JOIN (SELECT Name, Deckelhoehe FROM he.Schacht
                     UNION SELECT Name, Gelaendehoehe AS Deckelhoehe FROM he.Auslass
                     UNION SELECT Name, Gelaendehoehe AS Deckelhoehe FROM he.Speicherschacht) AS su
                ON ro.Schachtunten = su.Name
                LEFT JOIN profile AS pr
                ON ro.Profiltyp = pr.he_nr
                LEFT JOIN entwaesserungsarten AS ea 
                ON ea.he_nr = ro.Kanalart
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = ro.Planungsstatus
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = ro.Name
                WHERE ha.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "he8_import Haltungen"):
                    return False

                # idk why this is necessary...
                if not self.db_qkan.sql(
                    "UPDATE haltungen SET geom = geom", "he8_import Haltungen (2)"
                ):
                    return False

                self.db_qkan.commit()

        return True

    def _wehre(self) -> bool:
        """Import der Wehre"""

        if QKan.config.check_import.wehre:
            if self.append:
                sql = """
                INSERT INTO wehre_data (
                    wnam, schoben, schunten, 
                    wehrtyp, schwellenhoehe, kammerhoehe, 
                    laenge, uebeiwert, simstatus, 
                    kommentar, createdat)
                SELECT 
                    we.Name AS wnam,
                    we.Schachtoben AS schoben, 
                    we.Schachtunten AS schunten, 
                    we.Typ AS typ_he, 
                    we.Schwellenhoehe AS schwellenhoehe, 
                    we.Geometrie1 AS kammerhoehe, 
                    we.Geometrie2 AS laenge,
                    we.Ueberfallbeiwert AS uebeiwert,
                    si.bezeichnung AS simstatus, 
                    we.Kommentar AS kommentar, 
                    we.Lastmodified AS createdat
                FROM he.Wehr AS we
                LEFT JOIN (SELECT Name, Deckelhoehe FROM he.Schacht
                     UNION SELECT Name, Gelaendehoehe AS deckelhoehe FROM he.Speicherschacht) AS so
                ON we.Schachtoben = so.Name 
                LEFT JOIN (SELECT Name, Deckelhoehe FROM he.Schacht
                     UNION SELECT Name, Gelaendehoehe AS deckelhoehe FROM he.Auslass
                     UNION SELECT Name, Gelaendehoehe AS deckelhoehe FROM he.Speicherschacht) AS su
                ON we.Schachtunten = su.Name
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = we.Planungsstatus"""

                if not self.db_qkan.sql(sql, "he8_import Wehre"):
                    return False

                # idk why this is necessary...
                if not self.db_qkan.sql(
                    "UPDATE wehre SET geom = geom", "he8_import Wehre (2)"
                ):
                    return False

                self.db_qkan.commit()

        return True

    def _pumpen(self) -> bool:
        """Import der Pumpen"""

        if QKan.config.check_import.pumpen:
            if self.append:
                sql = """
                INSERT INTO pumpen_data (
                    pnam, schoben, schunten, pumpentyp, steuersch, einschalthoehe, ausschalthoehe, 
                    simstatus, kommentar, createdat)
                SELECT 
                    pu.Name AS pnam, 
                    pu.Schachtoben AS schoben, 
                    pu.Schachtunten AS schunten, 
                    pt.bezeichnung AS pumpentyp, 
                    pu.Steuerschacht AS steuersch, 
                    pu.Einschalthoehe AS einschalthoehe, 
                    pu.Ausschalthoehe AS ausschalthoehe,
                    si.bezeichnung AS simstatus, 
                    pu.Kommentar AS kommentar, 
                    pu.Lastmodified AS createdat
                FROM he.Pumpe AS pu
                LEFT JOIN (SELECT Name FROM he.Schacht
                     UNION SELECT Name FROM he.Speicherschacht) AS so
                ON pu.Schachtoben = SO.Name 
                LEFT JOIN (SELECT Name FROM he.Schacht
                     UNION SELECT Name FROM he.Auslass
                     UNION SELECT Name FROM he.Speicherschacht) AS su
                ON pu.Schachtunten = su.Name
                LEFT JOIN simulationsstatus AS si 
                ON si.he_nr = pu.Planungsstatus
                LEFT JOIN pumpentypen AS pt 
                ON pt.he_nr = pu.Typ"""

                if not self.db_qkan.sql(sql, "he8_import Pumpen"):
                    return False

                # idk why this is necessary...
                if not self.db_qkan.sql(
                    "UPDATE pumpen SET geom = geom", "he8_import Pumpen (2)"
                ):
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
                    SetSRID(fl.Geometry, {self.epsg}) AS geom
                FROM he.Flaeche AS fl
                """

                if not self.db_qkan.sql(sql, "he8_import Flaechen"):
                    return False

                self.db_qkan.commit()

        return True

    def _abflussparameter(self) -> bool:
        """Import der Abflussbeiwerte

        Es werden nur die in QKan fehlenden Abflussbeiwerte, die in der
        HE-Datenbank in Flächen verwendet werden, importiert"""

        if QKan.config.check_import.abflussparameter:
            if self.append:
                sql = """
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
                INNER JOIN he.Flaeche AS fl_he
                ON fl_he.Parametersatz = ap_he.Name
                WHERE ap_qk.pk IS NULL
                GROUP BY ap_qk.apnam
                """

                if not self.db_qkan.sql(sql, "he8_import Abflussparameter"):
                    return False

                self.db_qkan.commit()

        return True

    def _bodenklassen(self) -> bool:
        """Import der Bodenklassen

        Es werden nur die in QKan fehlenden Bodenklassen, die in der
        HE-Datenbank in Abflussparametern verwendet werden, importiert"""

        if QKan.config.check_import.bodenklassen:
            if self.append:
                sql = """
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
                ON bk_he.Name = bk_qk.bknam
                INNER JOIN he.abflussparameter AS ap_he
                ON ap_he.bodenklasse = bk_he.Name
                WHERE bk_qk.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "he8_import Bodenklassen"):
                    return False

                self.db_qkan.commit()

        return True

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
                        CastToPolygon(
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
                    kommentar, createdat
                )
                SELECT
                    el_he.Name AS elnam,
                    el_he.Rohr AS haltnam,
                    el_he.Zufluss AS zufluss,
                    el_he.Einwohner AS ew,
                    el_he.Teileinzugsgebiet AS einzugsgebiet,
                    el_he.Kommentar AS kommentar,
                    el_he.LastModified AS createdat
                FROM Einzeleinleiter AS el_he
                LEFT JOIN einleit AS el_qk
                ON el_he.Name = el_qk.elnam
                WHERE el_qk.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "he8_import Direkteinleiter"):
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
            or QKan.config.check_import.tezg_tf
        ):

            if self.append:
                choice_ef = str(QKan.config.check_import.tezg_ef)
                choice_hf = str(QKan.config.check_import.tezg_hf)
                choice_tf = str(QKan.config.check_import.tezg_tf)

                sql = f"""
                INSERT INTO tezg (
                    flnam, haltnam, 
                    kommentar, createdat, 
                    geom
                )
                SELECT
                    eg_he.Name AS flnam, 
                    eg_he.Haltung AS haltnam, 
                    eg_he.Kommentar AS kommentar, 
                    eg_he.LastModified AS createdat, 
                    SetSRID(eg_he.Geometry, {self.epsg}) AS geom
                FROM GipsEinzugsflaeche AS eg_he
                LEFT JOIN tezg AS eg_qk
                ON eg_he.Name = eg_qk.flnam
                WHERE (
                    (IsEinzugsflaeche and {choice_ef}) or
                    (IsHaltungsflaeche and {choice_hf}) or
                    (IsTwEinzugsflaeche and {choice_tf})
                ) and eg_qk.pk IS NULL 
                """
                if not self.db_qkan.sql(sql, "he8_import Haltungsflächen"):
                    return False

                self.db_qkan.commit()

        return True
