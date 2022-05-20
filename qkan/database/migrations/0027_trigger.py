import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.28"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Trigger zur Kontrolle der GeometryConstraints entfernen"""

    # Tabelle mit SQL-Abfragen
    sqls = [
        "DROP TRIGGER ggi_schaechte_geom",
        "DROP TRIGGER ggu_schaechte_geom",
        "DROP TRIGGER ggi_einzugsgebiete_geom",
        "DROP TRIGGER ggu_einzugsgebiete_geom",
        "DROP TRIGGER ggi_teilgebiete_geom",
        "DROP TRIGGER ggu_teilgebiete_geom",
        "DROP TRIGGER ggi_flaechen_geom",
        "DROP TRIGGER ggu_flaechen_geom",
        "DROP TRIGGER ggi_linkfl_geom",
        "DROP TRIGGER ggi_linkfl_gbuf",
        "DROP TRIGGER ggu_linkfl_geom",
        "DROP TRIGGER ggu_linkfl_gbuf",
        "DROP TRIGGER ggi_linksw_geom",
        "DROP TRIGGER ggi_linksw_gbuf",
        "DROP TRIGGER ggu_linksw_geom",
        "DROP TRIGGER ggu_linksw_gbuf",
        "DROP TRIGGER ggi_tezg_geom",
        "DROP TRIGGER ggu_tezg_geom",
        "DROP TRIGGER ggi_aussengebiete_geom",
        "DROP TRIGGER ggu_aussengebiete_geom",
        "DROP TRIGGER ggi_flaechen_he8_geometry",
        "DROP TRIGGER ggu_flaechen_he8_geometry",
    ]

    for sql in sqls:
        if not dbcon.sql(sql):
            logger.debug(f"Fehler bei Migration zu Version {VERSION}")
            return False

    dbcon.commit()
    return True
