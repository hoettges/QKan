import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.29"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Ergänze verschiedene Haltungstypen, die alle in der Tabelle haltungen gespeichert werden.
    """

    # Attribut sonderelement in Tabelle haltungen ergänzen
    sql = """
        ALTER TABLE haltungen ADD sonderelement TEXT
    """
    if not dbcon.sql(sql):
        logger.error(f"Fehler bei Migration zu Version {VERSION}")
        return False

    # Tabelle SonderelementeHaltungen ergänzen, mit der "normale" Haltungen von
    # Sonderbauwerksarten unterschieden werden
    sql = """CREATE TABLE sonderelementehaltungen(
        pk INTEGER PRIMARY KEY, 
        bezeichnung TEXT, 
        bemerkung TEXT)"""
    if not dbcon.sql(sql):
        logger.error("Fehler bei Migration zu Version {VERSION}:\n{err}\n"
            'Tabelle "sonderelementehaltungen" konnte nicht erstellt werden.',
        return False
    daten = [
        ('Drossel', 'HYSTEM-EXTRAN 8'),
        ('H-Regler', 'HYSTEM-EXTRAN 8'),
        ('Q-Regler', 'HYSTEM-EXTRAN 8'),
        ('Schieber', 'HYSTEM-EXTRAN 8'),
        ('GrundSeitenauslass', 'HYSTEM-EXTRAN 8'),
        ('Pumpe', None),
        ('Wehr', None),
    ]
    sql = "INSERT INTO sonderelementehaltungen (bezeichnung, bemerkung) VALUES (?, ?)"
    for dat in daten:
        if not dbcon.sql(sql, parameters=dat):
            logger.error(f"Fehler bei Migration zu Version {VERSION}:\n{err}"
                        '\nTabellendaten "sonderelementehaltungen" konnten nicht hinzugefuegt werden.'
                        '\nDaten: {dat}\n'
        )
        return False
    dbcon.commit()
    return True
