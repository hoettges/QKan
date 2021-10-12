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

        if not QKan.config.plausi.keepdata:
            sql = """DELETE FROM pruefliste"""
            if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1)"):
                logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
                del self.db_qkan
                return False

        filter = "('" + "', '".join(selected_themes) + "')"
        sql = f"""SELECT 
                    gruppe, warntext, warntyp, warnlevel, sql, layername, attrname
                FROM pruefsql
                WHERE gruppe in {filter}"""

        if not self.db_qkan.sql(sql, "datacheck.PlausiTask.run (1)"):
            logger.error('Plausibilitätsabfragen konnten nicht abgefragt werden.')
            del self.db_qkan
            return False

        for (gruppe, warntext, warntyp, warnlevel, sql, layername, attrname) in self.db_qkan.fetchall():
            sql = f"""INSERT INTO pruefliste (objname, warntext, warntyp, warnlevel, layername, attrname)
                SELECT
                    {attrname},
                    '{warntext}' AS warntext,
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
