import logging
import typing

from qkan import QKan, enums
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung


def _strip_float(value: typing.Union[str, float], default: float = 0.0) -> float:
    if isinstance(value, float):
        return value

    if isinstance(value, str) and value.strip() != "":
        return float(value)

    return default


def _strip_int(value: typing.Union[str, int], default: int = 0) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip() != "":
        return int(value)

    return default


def _consume_smp_block(
    _block: ElementTree.Element,
) -> typing.Tuple[str, int, float, float, float]:
    name = _block.findtext("d:Objektbezeichnung", "not found", NS)
    knoten_typ = 0

    for _schacht in _block.findall("d:Knoten", NS):
        knoten_typ = _strip_int(_schacht.findtext("d:KnotenTyp", -1, NS))

    smp = _block.find(
        "d:Geometrie/d:Geometriedaten/d:Knoten/d:Punkt[d:PunktattributAbwasser='SMP']",
        NS,
    )

    if not smp:
        fehlermeldung(
            "Fehler beim XML-Import: Schächte",
            f'Keine Geometrie "SMP" für Schacht {name}',
        )
        xsch, ysch, sohlhoehe = (0.0,) * 3
    else:
        xsch = _strip_float(smp.findtext("d:Rechtswert", 0.0, NS))
        ysch = _strip_float(smp.findtext("d:Hochwert", 0.0, NS))
        sohlhoehe = _strip_float(smp.findtext("d:Punkthoehe", 0.0, NS))
    return name, knoten_typ, xsch, ysch, sohlhoehe


def geo_smp(_schacht: Schacht) -> typing.Tuple[str, str]:
    """
    Returns geom, geom SQL expressions
    """
    db_type = QKan.config.database.type
    if db_type == enums.QKanDBChoice.SPATIALITE:
        geop = f"MakePoint({_schacht.xsch}, {_schacht.ysch}, {QKan.config.epsg})"
        geom = (
            "CastToMultiPolygon(MakePolygon("
            f"MakeCircle({_schacht.xsch}, {_schacht.ysch}, {_schacht.durchm / 1000}, {QKan.config.epsg})"
            "))"
        )
    elif db_type == enums.QKanDBChoice.POSTGIS:
        geop = f"ST_SetSRID(ST_MakePoint({_schacht.xsch},{_schacht.ysch}),{QKan.config.epsg})"
        geom = ""  # TODO: GEOM is missing
    else:
        raise Exception("Unimplemented database type: {}".format(db_type))

    return geop, geom


def geo_hydro() -> str:
    db_type = QKan.config.database.type
    if db_type == enums.QKanDBChoice.SPATIALITE:
        geom = (
            f"MakeLine(MakePoint(SCHOB.xsch, SCHOB.ysch, {QKan.config.epsg}), "
            f"MakePoint(SCHUN.xsch, SCHUN.ysch, {QKan.config.epsg}))"
        )
    elif db_type == enums.QKanDBChoice.POSTGIS:
        geom = (
            f"ST_MakeLine(ST_SetSRID(ST_MakePoint(SCHOB.xsch, SCHOB.ysch, {QKan.config.epsg}),"
            f"ST_SetSRID(ST_MakePoint(SCHUN.xsch, SCHUN.ysch, {QKan.config.epsg}))"
        )
    else:
        raise Exception("Unimplemented database type: {}".format(db_type))
    return geom


# noinspection SqlNoDataSourceInspection, SqlResolve
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


    def __schaechte(self):
        """Import der Schächte"""

        sql = f"""
        INSERT INTO schaechte (
            schnam, xsch, ysch, 
            sohlhoehe, deckelhoehe, 
            durchm, 
            druckdicht, 
            entwart, schachttyp, simstatus, 
            kommentar, createdat, 
            geop, geom
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
            Lastmodified AS createdat,
            SetSrid(Geometry, {QKan.config.epsg}) AS geop, 
            CastToMultiPolygon(MakePolygon(MakeCircle(x(Geometry),y(Geometry),
                    coalesce(DURCHMESSER/1000., 1.0),{QKan.config.epsg}))) AS geom
        FROM he.Schacht"""

        if not self.db_qkan.sql(sql, "he8_import Schächte"):
            return False

        self.db_qkan.commit()


    def __auslaesse(self):
        """Import der Auslässe"""

        sql = f"""
        INSERT INTO schaechte (
            schnam, xsch, ysch, 
            sohlhoehe, deckelhoehe, 
            durchm, 
            druckdicht, 
            entwart, schachttyp, simstatus, 
            kommentar, createdat, 
            geop, geom
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
            Lastmodified AS createdat,
            SetSrid(Geometry, {QKan.config.epsg}) AS geop, 
            CastToMultiPolygon(MakePolygon(MakeCircle(x(Geometry),y(Geometry),
                    coalesce(Durchmesser/1000., 1.0),{QKan.config.epsg}))) AS geom
        FROM he.Auslass"""

        if not self.db_qkan.sql(sql, "he8_import Auslässe"):
            return False

        self.db_qkan.commit()


    def __speicher(self):
        """Import der Speicher"""

        sql = f"""
        INSERT INTO schaechte (
            schnam, xsch, ysch, 
            sohlhoehe, deckelhoehe, 
            durchm, 
            druckdicht, 
            entwart, schachttyp, simstatus, 
            kommentar, createdat, 
            geop, geom
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
            Lastmodified AS createdat,
            SetSrid(Geometry, {QKan.config.epsg}) AS geop, 
            CastToMultiPolygon(MakePolygon(MakeCircle(x(Geometry),y(Geometry),
                    coalesce(Durchmesser/1000., 1.0),{QKan.config.epsg}))) AS geom
        FROM he.Speicher"""

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
        FROM a.Rohr
        INNER JOIN a.Sonderprofil
        ON a.Rohr.SonderprofilbezeichnungRef = a.Sonderprofil.Id
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
            xschob, yschob, xschun, yschun, 
            geom
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
            y(PointN(ro.Geometry, -1)) AS yschun,
            SetSrid(ro.Geometry, {QKan.config.epsg}) AS geom
        FROM a.Rohr AS ro
        INNER JOIN (SELECT Name, Deckelhoehe FROM a.Schacht
             UNION SELECT Name, Gelaendehoehe AS Deckelhoehe FROM a.Speicherschacht) AS so
        ON ro.Schachtoben = so.Name 
        INNER JOIN (SELECT Name, Deckelhoehe FROM a.Schacht
             UNION SELECT Name, Gelaendehoehe AS Deckelhoehe FROM a.Auslass
             UNION SELECT Name, Gelaendehoehe AS Deckelhoehe FROM a.Speicherschacht) AS su
        ON ro.Schachtunten = su.Name
        LEFT JOIN profile AS pr
        ON ro.Profiltyp = pr.he_nr
        LEFT JOIN entwaesserungsarten AS ea 
        ON ea.he_nr = ro.Kanalart
        LEFT JOIN simulationsstatus AS si 
        ON si.he_nr = ro.Planungsstatus
        """

        if not self.db_qkan.sql(sql, "he8_import Haltungen"):
            return None

        self.db_qkan.commit()


    def _wehre(self):
        """Import der Wehre"""

            sql = f"""
            INSERT INTO wehre (
                wnam, schoben, schunten, 
                wehrtyp, schwellenhoehe, kammerhoehe, 
                laenge, uebeiwert, simstatus, 
                kommentar, createdat, 
                geom)
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
                we.Lastmodified AS createdat, 
                SetSrid(we.Geometry, {QKan.config.epsg}) AS geom
            FROM a.Wehr AS we
            LEFT JOIN (SELECT Name, Deckelhoehe FROM a.Schacht
                 UNION SELECT Name, Gelaendehoehe AS deckelhoehe FROM a.Speicherschacht) AS so
            ON we.Schachtoben = so.Name 
            LEFT JOIN (SELECT Name, Deckelhoehe FROM a.Schacht
                 UNION SELECT Name, Gelaendehoehe AS deckelhoehe FROM a.Auslass
                 UNION SELECT Name, Gelaendehoehe AS deckelhoehe FROM a.Speicherschacht) AS su
            ON we.Schachtunten = su.Name
            LEFT JOIN simulationsstatus AS si 
            ON si.he_nr = we.Planungsstatus"""

            if not self.db_qkan.sql(sql, "he8_import Wehre"):
                return None

        self.db_qkan.commit()


    def _pumpen(self):
        """Import der Pumpen"""

        sql = f"""
        INSERT INTO pumpen (
            pnam, schoben, schunten, pumpentyp, steuersch, einschalthoehe, ausschalthoehe, 
            simstatus, kommentar, createdat, geom)
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
            pu.Lastmodified AS createdat, 
            SetSrid(pu.Geometry, {QKan.config.epsg}) AS geom
        FROM a.Pumpe AS pu
        LEFT JOIN (SELECT Name FROM a.Schacht
             UNION SELECT Name FROM a.Speicherschacht) AS so
        ON pu.Schachtoben = SO.Name 
        LEFT JOIN (SELECT Name FROM a.Schacht
             UNION SELECT Name FROM a.Auslass
             UNION SELECT Name FROM a.Speicherschacht) AS su
        ON pu.Schachtunten = su.Name
        LEFT JOIN simulationsstatus AS si 
        ON si.he_nr = we.Planungsstatus
        LEFT JOIN pumpentypen AS pt 
        ON pt.he_nr = pu.Typ"""

        if not self.db_qkan.sql(sql, "he8_import Pumpen"):
            return None

        self.db_qkan.commit()
