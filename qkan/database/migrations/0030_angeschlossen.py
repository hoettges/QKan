from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.2.32"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Datensätze für nicht angeschlossene Haltungen hinzufügen"""

    sql = """
    WITH dsnew AS (
        VALUES ('MD', 'MW Druck', 'Mischwasserdruckleitung', 0, 0),
               ('RD', 'SW Druck', 'Schmutzwasserdruckleitung', 0, 0),
               ('SD', 'RW Druck', 'Regenwasserdruckleitung', 0, 0),
               ('GR', 'Rinnen/Gräben', 'Rinnen/Gräben', 0, 0),
               ('SG', 'stillgelegt', 'stillgelegt', 0, 0),
               ('MN', 'MW nicht angeschlossen', 'ohne Mischwasseranschlüsse', 0, 0),
               ('RN', 'RW nicht angeschlossen', 'ohne Regenwasseranschlüsse', 1, 2))
    INSERT INTO entwaesserungsarten (kuerzel, bezeichnung, bemerkung, he_nr, kp_nr)
    SELECT * 
    FROM dsnew
    WHERE column2 NOT IN (SELECT bezeichnung FROM entwaesserungsarten)
    """
    if not dbcon.sql(sql):
        logger.error(f'QKan.database.migrations.0030_angeschlossen.py:\n'
                     f'Fehler bei Ausführung der SQL-Anweisung:\n{sql}\n')

    return True
