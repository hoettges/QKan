import logging

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.plugin import QKanPlugin

logger = logging.getLogger("QKan.mu.import")


class PlausiTask(QKanPlugin):
    def __init__(self, db_qkan: DBConnection):
        self.db_qkan = db_qkan

    def run(self) -> bool:
        selected_themes = QKan.config.plausi.themen

        # update damit die Charakterisirungsfehler funktionieren
        sql = f"""Update Untersuchdat_haltung
                            Set charakt1 = ''
                            where charakt1 = 'not found'
                            """
        if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1a)"):
            logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
            return False

        sql = f"""Update Untersuchdat_haltung
                                    Set charakt2 = ''
                                    where charakt2 = 'not found'
                                    """
        if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1b)"):
            logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
            return False

        sql = f"""Update Untersuchdat_schacht
                                    Set charakt1 = ''
                                    where charakt1 = 'not found'
                                    """
        if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1c)"):
            logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
            return False

        sql = f"""Update Untersuchdat_schacht
                                            Set charakt2 = ''
                                            where charakt2 = 'not found'
                                            """
        if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1d)"):
            logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
            return False

        sql = f"""Update Untersuchdat_schacht
                                                    Set bereich = ''
                                                    where bereich = 'not found'
                                                    """
        if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1e)"):
            logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
            return False

        if not QKan.config.plausi.keepdata:
            sql = """DELETE FROM pruefliste"""
            if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1)"):
                logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
                return False

        filter = "('" + "', '".join(selected_themes) + "')"
        sql = f"""SELECT 
                    gruppe, warntext, warntyp, warnlevel, sql, layername, attrname
                FROM pruefsql
                WHERE gruppe in {filter}"""

        if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1)"):
            logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
            return False

        for (gruppe, warntext, warntyp, warnlevel, sql, layername, attrname) in self.db_qkan.fetchall():
            sql = f"""INSERT INTO pruefliste (objname, warntext, warntyp, warnlevel, layername, attrname)
                SELECT
                    {attrname},
                    bemerkung AS warntext,
                    '{warntyp}' AS warntyp,
                    {warnlevel} AS warnlevel,
                    '{layername}' AS layername,
                    '{attrname}' AS attrname
                FROM
                ({sql});"""
            if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (2)"):
                logger.warning(f"Plausibilitätsabfrage '{warntext}' zum Thema '{gruppe}' ist fehlgeschlagen.")

        self.db_qkan.commit()

        return True
