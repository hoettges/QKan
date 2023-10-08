import logging
from qkan import QKan
from qkan.database.dbfunc import DBConnection

logger = logging.getLogger("QKan.xml.info")


class Info:
    def __init__(self, db_qkan: DBConnection):
        self.db_qkan = db_qkan
        self.anz_haltungen = 0
        self.anz_schaechte = 0
        self.laenge_haltungen = 0
        self.anz_teilgeb = 0

        # nr (str) => description

    def _infos(self) -> None:
        #anzahl haltungen
        sql = """
        select count() from haltungen
        """

        if not self.db_qkan.sql(sql):
            return

        self.anz_haltungen = self.db_qkan.fetchall()[0][0]

        # anzahl schaechte
        sql = """
           select count() from schaechte
           """

        if not self.db_qkan.sql(sql):
            return

        self.anz_schaechte = self.db_qkan.fetchall()[0][0]

        # anzahl teilgebiete
        sql = """
               select count() from teilgebiete
               """

        if not self.db_qkan.sql(sql):
            return


        self.anz_teilgeb = self.db_qkan.fetchall()[0][0]

        # anzahl lange haltungen
        sql = """
                   SELECT
                    SUM(laenge)
                    FROM
                    haltungen
                   """

        if not self.db_qkan.sql(sql):
            return

        self.laenge_haltungen = self.db_qkan.fetchall()[0][0]

    def run(self) -> None:
        """
        Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine XML-Datei
        """
        iface = QKan.instance.iface

        self._infos()


        # Close connection
        del self.db_qkan




