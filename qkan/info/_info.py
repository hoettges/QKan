import logging
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qgis.core import Qgis
from qgis.utils import iface, spatialite_connect

logger = logging.getLogger("QKan.xml.info")


class Info:
    def __init__(self, db_qkan: DBConnection):
        self.db_qkan = db_qkan
        self.anz_haltungen = 0
        self.anz_schaechte = 0
        self.laenge_haltungen = 0
        self.anz_teilgeb = 0
        path = db_qkan.dbname
        db = spatialite_connect(path)
        self.curs = db.cursor()

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

        self.laenge_haltungen = round(self.db_qkan.fetchall()[0][0],2)

    def _suewvo(self):
        date = self.date+'%'
        self.bew_art = 'DWA'
        self.laenge_haltungen_rw = 0
        self.laenge_haltungen_sw = 0
        self.laenge_haltungen_mw = 0
        self.haltungen_0_rw = 0
        self.haltungen_1_rw = 0
        self.haltungen_2_rw = 0
        self.haltungen_3_rw = 0
        self.haltungen_4_rw = 0
        self.haltungen_5_rw = 0
        self.laenge_haltungen_untersuch_rw = 0
        self.laenge_haltungen_untersuch_bj_rw = 0
        self.laenge_haltungen_saniert_rw = 0
        self.haltungen_0_sw = 0
        self.haltungen_1_sw = 0
        self.haltungen_2_sw = 0
        self.haltungen_3_sw = 0
        self.haltungen_4_sw = 0
        self.haltungen_5_sw = 0
        self.laenge_haltungen_untersuch_sw = 0
        self.laenge_haltungen_untersuch_bj_sw = 0
        self.laenge_haltungen_saniert_sw = 0
        self.haltungen_0_mw = 0
        self.haltungen_1_mw = 0
        self.haltungen_2_mw = 0
        self.haltungen_3_mw = 0
        self.haltungen_4_mw = 0
        self.haltungen_5_mw = 0
        self.laenge_haltungen_untersuch_mw = 0
        self.laenge_haltungen_untersuch_bj_mw = 0
        self.laenge_haltungen_saniert_mw = 0
        self.anz_schaechte_rw = 0
        self.anz_schaechte_sw = 0
        self.anz_schaechte_mw = 0
        self.anz_schaechte_0_rw = 0
        self.anz_schaechte_1_rw = 0
        self.anz_schaechte_2_rw = 0
        self.anz_schaechte_3_rw = 0
        self.anz_schaechte_4_rw = 0
        self.anz_schaechte_5_rw = 0
        self.anz_schaechte_untersuch_rw = 0
        self.anz_schaechte_untersuch_bj_rw = 0
        self.anz_schaechte_saniert_rw = 0
        self.anz_schaechte_0_sw = 0
        self.anz_schaechte_1_sw = 0
        self.anz_schaechte_2_sw = 0
        self.anz_schaechte_3_sw = 0
        self.anz_schaechte_4_sw = 0
        self.anz_schaechte_5_sw = 0
        self.anz_schaechte_untersuch_sw = 0
        self.anz_schaechte_untersuch_bj_sw = 0
        self.anz_schaechte_saniert_sw = 0
        self.anz_schaechte_0_mw = 0
        self.anz_schaechte_1_mw = 0
        self.anz_schaechte_2_mw = 0
        self.anz_schaechte_3_mw = 0
        self.anz_schaechte_4_mw = 0
        self.anz_schaechte_5_mw = 0
        self.anz_schaechte_untersuch_mw = 0
        self.anz_schaechte_untersuch_bj_mw = 0
        self.anz_schaechte_saniert_mw = 0

        #testen ob zustandsbewertungen vorhanden sind
        sql = """
                   SELECT
                    pk
                    FROM
                    haltungen_untersucht
                   """
        if not self.db_qkan.sql(sql):
            return

        if len(self.db_qkan.fetchall()) != 0:
            #abfragen Haltungen

            # anzahl lange haltungen RW
            sql = """
                       SELECT
                        SUM(laenge)
                        FROM
                        haltungen
                        WHERE entwart = 'Regenwasser'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.laenge_haltungen_rw = round(attr[0][0], 2)

            # anzahl lange haltungen SW
            sql = """
                                   SELECT
                                    SUM(laenge)
                                    FROM
                                    haltungen
                                    WHERE entwart = 'Schmutzwasser'
                                   """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.laenge_haltungen_sw = round(attr[0][0], 2)

            # anzahl lange haltungen MW
            sql = """
                       SELECT
                        SUM(laenge)
                        FROM
                        haltungen
                        WHERE entwart = 'Mischwasser'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.laenge_haltungen_mw = round(attr[0][0], 2)

            sql = """
                        SELECT * FROM
                        sqlite_master
                        WHERE
                        name = 'haltungen_untersucht_bewertung' and type = 'table'
                        """
            if not self.db_qkan.sql(sql):
                return

            if len(self.db_qkan.fetchall()) != 0:

                sql = """
                            SELECT MAX(haltungen_untersucht_bewertung.datenart)

                            FROM haltungen_untersucht_bewertung
                                   """
                if not self.db_qkan.sql(sql):
                    return

                attr = self.db_qkan.fetchall()
                if attr[0][0] != None and attr != []:
                    self.bew_art = attr[0][0]

                # laenge haltungen 0
                sql = """
                            SELECT haltungen_untersucht_bewertung.haltnam,
                            haltungen.entwart,
                            haltungen.laenge
                            FROM haltungen_untersucht_bewertung,haltungen
                            WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 0 and haltungen_untersucht_bewertung.untersuchtag like ?
                                      """
                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass

                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_0_rw = round(rw,2)
                        self.haltungen_0_sw = round(sw,2)
                        self.haltungen_0_mw = round(mw,2)

                # laenge haltungen 1
                sql = """
                                SELECT haltungen_untersucht_bewertung.haltnam,
                                haltungen.entwart,
                                haltungen.laenge
                                FROM haltungen_untersucht_bewertung,haltungen
                                WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 1 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                          """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_1_rw = round(rw,2)
                        self.haltungen_1_sw = round(sw,2)
                        self.haltungen_1_mw = round(mw,2)

                # laenge haltungen 2
                sql = """
                        SELECT haltungen_untersucht_bewertung.haltnam,
                        haltungen.entwart,
                        haltungen.laenge
                        FROM haltungen_untersucht_bewertung,haltungen
                        WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 2 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                  """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_2_rw = round(rw,2)
                        self.haltungen_2_sw = round(sw,2)
                        self.haltungen_2_mw = round(mw,2)

                # laenge haltungen 3
                sql = """
                                SELECT haltungen_untersucht_bewertung.haltnam,
                                haltungen.entwart,
                                haltungen.laenge
                                FROM haltungen_untersucht_bewertung,haltungen
                                WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 3 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                          """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_3_rw = round(rw,2)
                        self.haltungen_3_sw = round(sw,2)
                        self.haltungen_3_mw = round(mw,2)

                # laenge haltungen 4
                sql = """
                            SELECT haltungen_untersucht_bewertung.haltnam,
                            haltungen.entwart,
                            haltungen.laenge
                            FROM haltungen_untersucht_bewertung,haltungen
                            WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 4 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                      """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_4_rw = round(rw,2)
                        self.haltungen_4_sw = round(sw,2)
                        self.haltungen_4_mw = round(mw,2)

                # laenge haltungen 5
                sql = """
                            SELECT haltungen_untersucht_bewertung.haltnam,
                            haltungen.entwart,
                            haltungen.laenge
                            FROM haltungen_untersucht_bewertung,haltungen
                            WHERE haltungen_untersucht_bewertung.haltnam =haltungen.haltnam AND haltungen_untersucht_bewertung.objektklasse_gesamt = 5 and haltungen_untersucht_bewertung.untersuchtag like ?;
                                      """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != None and attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += i[2]
                        if i[1] == 'Schmutzwasser':
                            sw += i[2]
                        if i[1] == 'Mischwasser':
                            mw += i[2]

                        self.haltungen_5_rw = round(rw,2)
                        self.haltungen_5_sw = round(sw,2)
                        self.haltungen_5_mw = round(mw,2)


       #Abfragen Schaechte
        sql = """
                   SELECT
                    pk
                    FROM
                    schaechte_untersucht
                   """
        if not self.db_qkan.sql(sql):
            return

        if len(self.db_qkan.fetchall()) != 0:
            # abfragen schaechte

            # anzahl schaechte rw
            sql = """
                       SELECT
                       count(*)
                        FROM
                        schaechte
                        WHERE entwart ='Regenwasser' OR entwart = 'KR'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.anz_schaechte_rw = attr[0][0]

            # anzahl schaechte sw
            sql = """
                           SELECT
                           count(*)
                            FROM
                            schaechte
                            WHERE entwart ='Schmutzwasser' OR entwart = 'KS'
                           """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.anz_schaechte_sw = attr[0][0]

            # anzahl schaechte mw
            sql = """
                       SELECT
                       count(*)
                        FROM
                        schaechte
                        WHERE entwart ='Mischwasser' OR entwart = 'KM'
                       """

            if not self.db_qkan.sql(sql):
                return
            attr = self.db_qkan.fetchall()
            if attr[0][0] != None and attr != []:
                self.anz_schaechte_mw = attr[0][0]

            sql = """
            SELECT * FROM
            sqlite_master
            WHERE
            name = 'schaechte_untersucht_bewertung' and type = 'table'
            """
            if not self.db_qkan.sql(sql):
                return

            if len(self.db_qkan.fetchall()) != 0:
                sql = """
                                                            SELECT MAX(schaechte_untersucht_bewertung.datenart)

                                                            FROM schaechte_untersucht_bewertung
                                                                   """
                if not self.db_qkan.sql(sql):
                    return

                attr = self.db_qkan.fetchall()
                if attr[0][0] != None and attr != []:
                    self.bew_art = attr[0][0]

                # anzahl schaechte 0
                sql = """
                            SELECT schaechte_untersucht_bewertung.schnam,
                            schaechte.entwart
                            FROM schaechte_untersucht_bewertung,schaechte
                            WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 0 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                   """

                data = (date,)

                try:
                    self.curs.execute(sql, data)
                except:
                    pass
                attr = self.curs.fetchall()
                if attr != []:
                    rw = 0
                    sw = 0
                    mw = 0
                    for i in attr:
                        if i[1] == 'Regenwasser':
                            rw += 1
                        if i[1] == 'Schmutzwasser':
                            sw += 1
                        if i[1] == 'Mischwasser':
                            mw += 1

                        self.anz_schaechte_0_rw = rw
                        self.anz_schaechte_0_sw = sw
                        self.anz_schaechte_0_mw = mw

                    # anzahl schaechte 1
                    sql = """
                                    SELECT schaechte_untersucht_bewertung.schnam,
                                    schaechte.entwart
                                    FROM schaechte_untersucht_bewertung,schaechte
                                    WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 1 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                           """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_1_rw = rw
                                self.anz_schaechte_1_sw = sw
                                self.anz_schaechte_1_mw = mw

                    # anzahl schaechte 2
                    sql = """
                                            SELECT schaechte_untersucht_bewertung.schnam,
                                            schaechte.entwart
                                            FROM schaechte_untersucht_bewertung,schaechte
                                            WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 2 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                                   """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_2_rw = rw
                                self.anz_schaechte_2_sw = sw
                                self.anz_schaechte_2_mw = mw

                    # anzahl schaechte 3
                    sql = """
                                        SELECT schaechte_untersucht_bewertung.schnam,
                                        schaechte.entwart
                                        FROM schaechte_untersucht_bewertung,schaechte
                                        WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 3 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                               """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_3_rw = rw
                                self.anz_schaechte_3_sw = sw
                                self.anz_schaechte_3_mw = mw

                    # anzahl schaechte 4
                    sql = """
                            SELECT schaechte_untersucht_bewertung.schnam,
                            schaechte.entwart
                            FROM schaechte_untersucht_bewertung,schaechte
                            WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 4
                                   """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_4_rw = rw
                                self.anz_schaechte_4_sw = sw
                                self.anz_schaechte_4_mw = mw

                    # anzahl schaechte 5
                    sql = """
                                SELECT schaechte_untersucht_bewertung.schnam,
                                schaechte.entwart
                                FROM schaechte_untersucht_bewertung,schaechte
                                WHERE schaechte_untersucht_bewertung.schnam =schaechte.schnam AND schaechte_untersucht_bewertung.objektklasse_gesamt = 5 and schaechte_untersucht_bewertung.untersuchtag like ?;
                                       """

                    data = (date,)

                    try:
                        self.curs.execute(sql, data)
                    except:
                        pass
                    attr = self.curs.fetchall()
                    if attr != []:
                        if attr[0] != None:
                            rw = 0
                            sw = 0
                            mw = 0
                            for i in attr:
                                if i[1] == 'Regenwasser':
                                    rw += 1
                                if i[1] == 'Schmutzwasser':
                                    sw += 1
                                if i[1] == 'Mischwasser':
                                    mw += 1

                                self.anz_schaechte_5_rw = rw
                                self.anz_schaechte_5_sw = sw
                                self.anz_schaechte_5_mw = mw


    def run(self, date) -> None:
            """
            Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine XML-Datei
            """
            self.date = date
            self._infos()
            self._suewvo()

            # Close connection
            del self.db_qkan




