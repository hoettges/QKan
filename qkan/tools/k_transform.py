from qkan import QKan, enums
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError

logger = get_logger("QKan.tools.transform")


class TransformTask:
    def __init__(self, epsg_from: int):
        # all parameters are passed via QKan.config

        self.epsg = QKan.config.epsg
        self.epsg_from = epsg_from

    def run(self) -> bool:

        result = self._transform()

        return result

    def _transform(self) -> bool:
        """Alle Tabellen vom fremden in das Projekt-KBS transformieren"""

        TABLES_GEOM = enums.SyncTables.TABLES_GEOM.value
        TABLES_GEOP = enums.SyncTables.TABLES_GEOP.value
        TABLES_GLINK = enums.SyncTables.TABLES_GLINK.value

        tables = TABLES_GEOM + TABLES_GEOP + TABLES_GLINK

        with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:
            db_qkan.loadmodule('tools')
            for tabnam in tables:
                if db_qkan.attrlist(tabnam) != []:
                    sqlnam = f'tools_transform_{tabnam}'
                    params = {
                        'epsg_from': self.epsg_from,
                        'epsg_to': self.epsg,
                    }

                    if not db_qkan.sqlyml(
                        sqlnam=sqlnam,
                        stmt_category="Transformation Tabelle {tabnam}",
                        parameters=params,
                    ):
                        raise QkanDbError()

            db_qkan.commit()
            return True
