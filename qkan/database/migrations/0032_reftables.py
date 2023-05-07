import logging

from qkan.database.dbfunc import DBConnection
from qgis.utils import pluginDirectory

VERSION = "3.2.39"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Erweiterung der Tabelle entwaesserungsarten"""

    if not dbcon.alter_table(
        "entwaesserungsarten",
        [
            "bezeichnung TEXT                    -- eindeutige QKan-Bezeichnung",
            "kuerzel TEXT                        -- nur für Beschriftung",
            "bemerkung TEXT",
            "he_nr INTEGER                       -- HYSTEM-EXTRAN",
            "kp_nr INTEGER                       -- DYNA / Kanal++",
            "m145 TEXT                           -- DWA M145",
            "isybau TEXT                         -- BFR Abwasser",
            "transport INTEGER                   -- Transporthaltung?",
            "druckdicht INTEGER                  -- Druckleitung?",
    ]
    ):
        logger.error(
            f"Fehler bei Migration zu Version {VERSION}: "
            "Änderung der Tabelle entwaesserungsarten fehlgeschlagen"
        )

    # Daten ergänzen, falls nicht schon vorhanden
    daten = [
        ('Regenwasser', 'R', 'Regenwasser', 1, 2, 'R', 'KR', 0, 0),
        ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1, 'S', 'KS', 0, 0),
        ('Mischwasser', 'M', 'Mischwasser', 0, 0, 'M', 'KM', 0, 0),
        ('RW Druckleitung', 'RD', 'Transporthaltung ohne Anschlüsse', 1, 2, None, 'DR', None, 1),
        ('SW Druckleitung', 'SD', 'Transporthaltung ohne Anschlüsse', 2, 1, None, 'DS', None, 1),
        ('MW Druckleitung', 'MD', 'Transporthaltung ohne Anschlüsse', 0, 0, None, 'DW', None, 1),
        ('RW nicht angeschlossen', 'RT', 'Transporthaltung ohne Anschlüsse', 1, 2, None, None, 1, 0),
        ('MW nicht angeschlossen', 'MT', 'Transporthaltung ohne Anschlüsse', 0, 0, None, None, 1, 0),
        ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, None, None, 0, None),
        ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None, 0, None),
    ]

    daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
    sql = """INSERT INTO entwaesserungsarten (
                bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m145, isybau, transport, druckdicht)
                SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
    if not dbcon.sql(sql, "Migration 0032 Referenzliste entwaesserungsarten", daten, many=True):
        return False

    dbcon.commit()
    return True
