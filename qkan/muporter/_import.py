import logging

from qkan import QKan
from qkan.database.dbfunc import DBConnection

logger = logging.getLogger("QKan.mu.import")


class ImportTask:
    def __init__(self, db_qkan: DBConnection):
        self.db_qkan = db_qkan

        self.append = QKan.config.check_import.append
        self.update = QKan.config.check_import.update

        self.epsg = QKan.config.epsg

    def run(self) -> bool:

        result = all(
            [
                self._abflussparameter(),
                self._schaechte(),
                self._profile(),
                self._haltungen(),
                self._wehre(),
                self._pumpen(),
                self._flaechen(),
                self._tezg(),
            ]
        )

        return result

    def _schaechte(self) -> bool:
        """Import der Schächte"""

        # Selected Nodetypes
        seltypes = []
        if QKan.config.check_import.schaechte:
            seltypes += [1]
        if QKan.config.check_import.auslaesse:
            seltypes += [3]
        if QKan.config.check_import.auslaesse:
            seltypes += [2, 4]
        selectedtypes = tuple(seltypes)

        if self.append:
            sql = f"""
            INSERT INTO schaechte_data (
                schnam, xsch, ysch, simstatus, 
                sohlhoehe, deckelhoehe, 
                durchm, druckdicht, schachttyp,
                kommentar, createdat
            )
            SELECT
                sm.muid AS schnam
              , x(sm.geometry)
              , y(sm.geometry)
              , 'vorhanden'                     AS simstatus
              , sm.invertlevel                  AS sohlhoehe
              , sm.groundlevel                  AS deckelhoehe
              , sm.diameter                     AS durchm
              , (sm.covertypeno = 2)            AS druckdicht
              , CASE sm.typeno 
                WHEN 1 THEN 'Schacht'
                WHEN 2 THEN 'Speicher'
                WHEN 3 THEN 'Auslass'
                WHEN 4 THEN 'Speicher' END      AS schachttyp
              , 'Importiert mit QKan'           AS kommentar
              , coalesce(createdat, datetime('now')) 
                                                AS createdat
            FROM mu.msm_Node    AS sm
            LEFT JOIN schaechte AS sq
            ON sm.muid = sq.schnam 
            WHERE sq.pk IS NULL
              AND sm.typeno IN {selectedtypes}
            """

            if not self.db_qkan.sql(sql, "mu_import Schächte"):
                return False

            self.db_qkan.commit()

        return True

    def _profile(self) -> bool:
        """Import der Profile"""

        # Sonderprofile haben die TypeNo=2, ansonsten gibt's nur 5 Standardprofile
        if QKan.config.check_import.rohrprofile:
            if self.append:
                sql = f"""
                INSERT INTO profile (
                    profilnam, mu_nr
                )
                SELECT 
                    sp.muid, 2
                FROM mu.ms_CRS AS sp
                LEFT JOIN profile AS pr
                ON pr.profilnam = sp.muid
                WHERE pr.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "mu_import Sonderprofile"):
                    return False

                self.db_qkan.commit()

        return True

    def _haltungen(self) -> bool:
        """Import der Haltungen"""

        # Haltungen
        if QKan.config.check_import.haltungen:
            if self.append:
                sql = f"""
                INSERT INTO haltungen (
                    haltnam, schoben, schunten, 
                    hoehe, breite, laenge, 
                    profilnam, entwart, 
                    sohleoben, sohleunten, 
                    ks, simstatus, 
                    kommentar, createdat, 
                    geom
                )
                SELECT
                    ro.muid                             AS haltnam
                  , ro.fromnodeid                       AS schoben
                  , ro.tonodeid                         AS schunten
                  , coalesce(ro.height, ro.diameter)    AS hoehe
                  , coalesce(ro.width, ro.diameter)     AS breite
                  , ro.length                           AS laenge
                  , CASE WHEN ro.typeno = 2 
                        THEN ro.crsid 
                        ELSE pr.profilnam END           AS profilnam
                  , 'Mischwasser'                       AS entwart
                  , ro.uplevel                          AS sohleoben
                  , ro.dwlevel                          AS sohleunten
                  , coalesce(mt.eqrough, pow((25.68/coalesce(ro.manning, mt.manning, 85)),6)*1000)    
                                                        AS ks
                  , 'vorhanden'                         AS simstatus
                  , 'Importiert mit QKan'               AS kommentar
                  , coalesce(createdat, datetime('now')) 
                                                        AS createdat
                  , SetSRID(ro.geometry, {self.epsg})    AS geom
                FROM mu.msm_Link AS ro
                LEFT JOIN mu.ms_Material AS mt
                ON ro.materialid = mt.muid
                LEFT JOIN profile AS pr
                ON ro.typeno = pr.he_nr
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = ro.muid
                WHERE ha.pk IS NULL AND ro.active
                """

                if not self.db_qkan.sql(sql, "mu_import Haltungen"):
                    return False

                self.db_qkan.commit()

        return True

    def _wehre(self) -> bool:
        """Import der Wehre"""

        if QKan.config.check_import.wehre:
            if self.append:
                # sql = f"""
                # INSERT INTO wehre (
                #     wnam, schoben, schunten,
                #     schwellenhoehe,
                #     laenge, uebeiwert, simstatus,
                #     kommentar, createdat, geom)
                # SELECT
                #     wu.muid                             AS wnam
                #   , wu.fromnodeid                       AS schoben
                #   , wu.tonodeid                         AS schunten
                #   , wu.crestlevel                       AS schwellenhoehe
                #   , wu.crestwidth                       AS laenge
                #   , wu.coeff                            AS uebeiwert
                #   , 'vorhanden'                         AS simstatus
                #   , 'Importiert mit QKan'               AS kommentar
                #   , coalesce(createdat, datetime('now'))
                #                                         AS createdat
                #   , SetSRID(wu.geometry, {self.epsg})   AS geom
                # FROM mu.msm_Weir AS wu
                # LEFT JOIN wehre AS wq
                # ON wq.wnam = wu.muid
                # WHERE wq.pk IS NULL"""
                #
                # if not self.db_qkan.sql(sql, "mu_import Wehre"):
                #     return False

                sql = f"""
                INSERT INTO haltungen (
                    haltnam, schoben, schunten,
                    hoehe,
                    sonderelement, 
                    simstatus,
                    kommentar, createdat, 
                    geom)
                SELECT 
                    wu.muid AS haltnam,
                    wu.fromnodeid AS schoben, 
                    wu.tonodeid AS schunten,
                    coalesce(wu.maxcrestlevel - mincrestlevel, 0.3) AS hoehe, 
                    wu.crestwidth AS breite,
                    wu.crestlevel AS sohleoben,
                    wu.crestlevel AS sohleunten,
                    'Wehr' AS sonderelement, 
                    'vorhanden' AS simstatus, 
                  , 'Importiert mit QKan'               AS kommentar
                  , coalesce(createdat, datetime('now')) 
                                                        AS createdat
                  , SetSRID(wu.geometry, {self.epsg})   AS geom
                                FROM mu.msm_Pump AS wu
                FROM mu.msm_Weir AS wu
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = wu.muid
                WHERE ha.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "mu_import Wehre"):
                    return False

                self.db_qkan.commit()

        return True

    def _pumpen(self) -> bool:
        """Import der Pumpen"""

        if QKan.config.check_import.pumpen:
            if self.append:
                # sql = f"""
                # INSERT INTO pumpen (
                #     pnam, schoben, schunten, pumpentyp, steuersch, einschalthoehe, ausschalthoehe,
                #     simstatus, kommentar, createdat, geom)
                # SELECT
                #     pu.muid                             AS pnam
                #   , pu.fromnodeid                       AS schoben
                #   , pu.tonodeid                         AS schunten
                #   , CASE pu.CapTypeNo
                #         WHEN 1 THEN 'Online Kennlinie'
                #         WHEN 2 THEN 'Online Wasserstandsdifferenz' END
                #                                         AS pumpentyp
                #   , pu.dutypoint                        AS steuersch
                #   , pu.startlevel                       AS einschalthoehe
                #   , pu.stoplevel                        AS ausschalthoehe
                #   , 'vorhanden'                         AS simstatus
                #   , 'Importiert mit QKan'               AS kommentar
                #   , coalesce(createdat, datetime('now'))
                #                                         AS createdat
                #   , SetSRID(pu.geometry, {self.epsg})   AS geom
                # FROM mu.msm_Pump AS pu
                # LEFT JOIN pumpen AS pq
                # ON pq.pnam = pu.muid
                # WHERE pq.pk IS NULL
                # """
                #
                # if not self.db_qkan.sql(sql, "mu_import Pumpen(1)"):
                #     return False

                sql = f"""
                INSERT INTO haltungen (
                    haltnam, schoben, schunten,
                    hoehe,
                    sonderelement, 
                    simstatus,
                    kommentar, createdat, 
                    geom)
                SELECT 
                    pu.muid AS haltnam,
                    pu.fromnodeid AS schoben, 
                    pu.tonodeid AS schunten,
                    0.3 AS hoehe,                   /* nur fuer Laengsschnitt */ 
                    'Pumpe' AS sonderelement, 
                    'vorhanden' AS simstatus, 
                  , 'Importiert mit QKan'               AS kommentar
                  , coalesce(createdat, datetime('now')) 
                                                        AS createdat
                  , SetSRID(pu.geometry, {self.epsg})   AS geom
                                FROM mu.msm_Pump AS pu
                FROM mu.msm_Pump AS pu
                LEFT JOIN haltungen AS ha
                ON ha.haltnam = pu.muid
                WHERE ha.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "mu_import Pumpen(2)"):
                    return False

                self.db_qkan.commit()

        return True

    def _flaechen(self) -> bool:
        """Import der Flächen"""

        if QKan.config.check_import.flaechen:
            if self.append:
                sql = f"""
                INSERT INTO flaechen (
                    flnam, haltnam, schnam, 
                    neigung, neigkl, 
                    abflussparameter, 
                    aufteilen, 
                    kommentar, createdat, geom
                    )
                SELECT
                    fm.muid                             AS flnam
                  , coalesce(fl.linkid, n2l.muid)       AS haltnam
                  , fl.nodeid                           AS schnam
                  , fm.modelbslope                      AS neigung
                  , CASE WHEN fm.modelbslope < 0.01 THEN 1
                         WHEN fm.modelbslope < 0.04 THEN 2
                         WHEN fm.modelbslope < 0.10 THEN 3
                         ELSE 4 END                     AS neigkl
                  , fm.modelbparbid                     AS abflussparameter
                  , false                               AS aufteilen
                  , 'Importiert mit QKan'               AS kommentar
                  , coalesce(createdat, datetime('now')) 
                                                        AS createdat
                  , CastToMultiPolygon(SetSRID(fm.geometry, {self.epsg}))
                                                        AS geom
                FROM mu.msm_Catchment AS fm
                JOIN mu.msm_CatchCon AS fl
                ON fl.catchid = fm.muid
                LEFT JOIN flaechen AS fq
                ON fq.flnam = fm.muid
                LEFT JOIN 
                (
                    SELECT ml.fromnodeid AS fromnodeid, ml.muid AS muid
                    FROM mu.msm_Link AS ml
                    LEFT JOIN 
                    (
                        SELECT ld.fromnodeid, max(ld.diameter) AS diameter
                        FROM mu.msm_Link AS ld
                        GROUP BY ld.fromnodeid
                    ) AS lm
                    ON lm.fromnodeid = ml.fromnodeid 
                    WHERE ml.diameter >= lm.diameter*0.999999
                    GROUP BY ml.fromnodeid
                ) AS n2l
                ON fl.nodeid = n2l.fromnodeid
                WHERE fq.pk IS NULL
                """

                if not self.db_qkan.sql(sql, "mu_import Flaechen (1)"):
                    return False

                sql = """
                INSERT INTO linkfl (flnam, haltnam, fliesszeitflaeche, abflusstyp, glink)
                SELECT fl.flnam, fl.haltnam, fm.modelaconctime/60., 'Schwerpunktfließzeit',
                    MakeLine(PointOnSurface(fl.geom),Centroid(ha.geom))
                    FROM flaechen AS fl
                    INNER JOIN haltungen AS ha
                    ON fl.haltnam = ha.haltnam
                    INNER JOIN mu.msm_Catchment AS fm
                    ON fl.flnam = fm.muid
                """

                if not self.db_qkan.sql(sql, "mu_import Flaechen (2)"):
                    return False

                self.db_qkan.commit()

        return True

    def _tezg(self) -> bool:
        """Import Flächen als Haltungsflächen"""

        if QKan.config.check_import.tezg_hf:
            if self.append:
                sql = f"""
                INSERT INTO tezg (
                    flnam, haltnam, schnam, neigung, 
                    neigkl, befgrad, schwerpunktlaufzeit, 
                    regenschreiber, abflussparameter, 
                    kommentar, createdat, 
                    geom
                )
                SELECT
                    fm.muid                             AS flnam
                  , coalesce(fl.linkid, n2l.muid)       AS haltnam
                  , fl.nodeid                           AS schnam
                  , fm.modelbslope                      AS neigung
                  , CASE WHEN fm.modelbslope < 0.01 THEN 1
                         WHEN fm.modelbslope < 0.04 THEN 2
                         WHEN fm.modelbslope < 0.10 THEN 3
                         ELSE 4 END                     AS neigkl
                  , fm.modelaimparea*100.               AS befgrad
                  , fm.modelblength                     AS schwerpunktlaufzeit
                  , NULL                                AS regenschreiber
                  , fm.modelaparaid                     AS abflussparameter
                  , 'Importiert mit QKan'               AS kommentar
                  , coalesce(createdat, datetime('now')) 
                                                        AS createdat
                  , CastToMultiPolygon(SetSRID(fm.geometry, {self.epsg}))
                                                        AS geom
                FROM mu.msm_Catchment AS fm
                JOIN mu.msm_CatchCon AS fl
                ON fl.catchid = fm.muid
                LEFT JOIN tezg AS tg
                ON tg.flnam = fm.muid
                LEFT JOIN 
                (
                    SELECT ml.fromnodeid AS fromnodeid, ml.muid AS muid
                    FROM mu.msm_Link AS ml
                    LEFT JOIN 
                    (
                        SELECT ld.fromnodeid, max(ld.diameter) AS diameter
                        FROM mu.msm_Link AS ld
                        GROUP BY ld.fromnodeid
                    ) AS lm
                    ON lm.fromnodeid = ml.fromnodeid 
                    WHERE ml.diameter >= lm.diameter*0.999999
                    GROUP BY ml.fromnodeid
                ) AS n2l
                ON fl.nodeid = n2l.fromnodeid
                WHERE tg.pk IS NULL
                """

            if not self.db_qkan.sql(sql, "mu_import Haltungsflaechen"):
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
                    apnam, benetzungsverlust, muldenverlust,
                    anfangsabflussbeiwert, endabflussbeiwert, 
                    mulden_startwert, benetzung_startwert,  
                    kommentar, createdat 
                )
                SELECT 
                      ap_mu.muid AS apnam 
                    , ap_mu.wetmedium AS benetzungsverlust 
                    , ap_mu.storagemedium AS muldenverlust
                    , 0.90, 0.90
                    , 0.0, 0.0
                    , 'Werte aus Modell B, nicht vollständig' AS kommentar
                    , coalesce(createdat, datetime('now')) 
                                                        AS createdat 
                FROM mu.msm_HParB AS ap_mu
                LEFT JOIN abflussparameter as ap_qk
                ON ap_mu.muid = ap_qk.apnam
                INNER JOIN mu.msm_Catchment AS fl_mu
                ON fl_mu.modelbparbid = ap_mu.muid
                WHERE ap_qk.pk IS NULL
                GROUP BY ap_mu.muid
                """

                if not self.db_qkan.sql(sql, "mu_import Abflussparameter"):
                    return False

                self.db_qkan.commit()

        return True
