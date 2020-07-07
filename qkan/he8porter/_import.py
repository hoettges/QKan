import logging
import typing

from qkan import QKan, enums
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

logger = logging.getLogger("QKan.he8.import")

class ImportTask:
    def __init__(self, db_qkan: DBConnection):
        self.db_qkan = db_qkan

    def run(self):
        result = all([ 
            self._schaechte(), 
            self._auslaesse(), 
            self._speicher(), 
            self._haltungen(), 
            self._wehre(), 
            self._pumpen()
        ])

        return result


    def _schaechte(self):
        """Import der Schächte"""

        sql = f"""
        INSERT INTO schaechte (
            schnam, xsch, ysch, 
            sohlhoehe, deckelhoehe, 
            durchm, 
            druckdicht, 
            entwart, schachttyp, simstatus, 
            kommentar, createdat
        )
        SELECT 
            Name AS schnam,
            x(Geometry) AS xsch, 
            y(Geometry) AS ysch, 
            Sohlhoehe AS sohlhoehe, 
            Deckelhoehe AS deckelhoehe, 
            Durchmesser AS durchm, 
            Druckdichterdeckel AS druckdicht, 
            Kanalart AS entwart, 
            'Schacht' AS schachttyp,
            Planungsstatus AS simstatus, 
            Kommentar AS kommentar, 
            Lastmodified AS createdat
        FROM he.Schacht"""

        if not self.db_qkan.sql(sql, "he8_import Schächte"):
            return False

        self.db_qkan.commit()


    def _auslaesse(self):
        """Import der Auslässe"""

        sql = f"""
        INSERT INTO schaechte (
            schnam, xsch, ysch, 
            sohlhoehe, deckelhoehe, 
            schachttyp, simstatus, 
            kommentar, createdat
        )
        SELECT 
            Name AS schnam,
            x(Geometry) AS xsch, 
            y(Geometry) AS ysch, 
            Sohlhoehe AS sohlhoehe, 
            Gelaendehoehe AS deckelhoehe, 
            'Auslass' AS schachttyp,
            Planungsstatus AS simstatus, 
            Kommentar AS kommentar, 
            Lastmodified AS createdat
        FROM he.Auslass"""

        if not self.db_qkan.sql(sql, "he8_import Auslässe"):
            return False

        self.db_qkan.commit()


    def _speicher(self):
        """Import der Speicher"""

        sql = f"""
        INSERT INTO schaechte (
            schnam, xsch, ysch, 
            sohlhoehe, deckelhoehe, 
            schachttyp, simstatus, 
            kommentar, createdat
        )
        SELECT 
            Name AS schnam,
            x(Geometry) AS xsch, 
            y(Geometry) AS ysch, 
            Sohlhoehe AS sohlhoehe, 
            Gelaendehoehe AS deckelhoehe, 
            'Speicher' AS schachttyp,
            Planungsstatus AS simstatus, 
            Kommentar AS kommentar, 
            Lastmodified AS createdat
        FROM he.Speicherschacht"""

        if not self.db_qkan.sql(sql, "he8_import Speicher"):
            return False

        self.db_qkan.commit()


    def _haltungen(self):
        """Import der Haltungen"""

        # Profilnummern aller Sonderprofile ergänzen. 
        sql = f"""
        INSERT INTO profile (
            profilnam, he_nr
        )
        SELECT 
            Sonderprofilbezeichnung, 68
        FROM he.Rohr
        INNER JOIN he.Sonderprofil
        ON he.Rohr.SonderprofilbezeichnungRef = he.Sonderprofil.Id
        GROUP BY 
            Profiltyp, Sonderprofilbezeichnung, SonderprofilbezeichnungRef
        """

        if not self.db_qkan.sql(sql, "he8_import Sonderprofile"):
            return None

        # Haltungen
        sql = f"""
        INSERT INTO haltungen  (
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
        """

        if not self.db_qkan.sql(sql, "he8_import Haltungen (1)"):
            return None

        # idk why this is necessary...
        if not self.db_qkan.sql("UPDATE haltungen SET geom = geom", "he8_import Haltungen (2)"):
            return None

        self.db_qkan.commit()


    def _wehre(self):
        """Import der Wehre"""

        sql = f"""
        INSERT INTO wehre (
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

        if not self.db_qkan.sql(sql, "he8_import Wehre (1)"):
            return None

        # idk why this is necessary...
        if not self.db_qkan.sql("UPDATE wehre SET geom = geom", "he8_import Wehre (2)"):
            return None

        self.db_qkan.commit()


    def _pumpen(self):
        """Import der Pumpen"""

        sql = f"""
        INSERT INTO pumpen (
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

        if not self.db_qkan.sql(sql, "he8_import Pumpen (1)"):
            return None

        # idk why this is necessary...
        if not self.db_qkan.sql("UPDATE pumpen SET geom = geom", "he8_import Pumpen (2)"):
            return None

        self.db_qkan.commit()


    def _flaechen(self):
        """Import der Flächen"""

        sql = f"""
        INSERT INTO flaechen ( 
            flnam, haltnam, schnam, neigkl, teilgebiet, regenschreiber, 
            abflussparameter, aufteilen, kommentar, createdat, geom)        
        """