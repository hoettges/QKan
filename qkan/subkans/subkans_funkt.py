import os
from datetime import datetime

from qkan.utils import get_logger
from math import pi, floor, ceil
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import round_up, formf
import time

from qgis.core import (
    Qgis,
    QgsProject,
    QgsVectorLayer,
    QgsDataSourceUri,
)
from qgis.utils import iface, spatialite_connect

from qkan import enums


logger = get_logger("QKan.zustand.import")


class Subkans_funkt:
    def __init__(self, check_cb, db_qkan: DBConnection, date, epsg, datetype):

        self.check_cb = check_cb
        self.db = db_qkan
        self.date = date
        self.crs = epsg
        self.haltung = True

        self.datetype = datetype

    def run(self):
        check_cb = self.check_cb

        if check_cb['cb1']:
            self.einzelfallbetrachtung_haltung()

        if check_cb['cb2']:
            self.bewertung_dwa_neu_haltung()

        if check_cb['cb3']:
            self.bewertung_subkans()
            self.schadens_ueberlagerung()
            self.subkans()

    # jh: besser round(n, decimals), weil round_up_down bei negativen Zahlen falsch rundet...
    def round_up_down(self, n, decimals=2):
        expoN = n * 10 ** decimals
        if abs(expoN) - abs(floor(expoN)) < 0.5:
            return floor(expoN) / 10 ** decimals
        return ceil(expoN) / 10 ** decimals

    def round_up(self, n, decimals=2):
        expoN = n * 10 ** decimals
        return ceil(expoN) / 10 ** decimals


    def bewertung_dwa_neu_haltung(self):
        date = self.date
        db = self.db
        crs = self.crs
        haltung = self.haltung


        # jh: subkans_update_dichtheit
        try:
            db.sql("""UPDATE haltungen_substanz_bewertung 
                                SET objektklasse_dichtheit =
                                (SELECT min(Zustandsklasse_D) 
                                FROM substanz_haltung_bewertung
                                WHERE substanz_haltung_bewertung.untersuchhal = haltungen_substanz_bewertung.haltnam AND Zustandsklasse_D <> '-'
                                GROUP BY substanz_haltung_bewertung.untersuchhal);""")
            #db.commit()
        except:
            pass

        # jh: subkans_update_standsicherheit
        try:
            db.sql("""UPDATE haltungen_substanz_bewertung 
                                SET objektklasse_standsicherheit =
                                (SELECT min(Zustandsklasse_S) 
                                FROM substanz_haltung_bewertung
                                WHERE substanz_haltung_bewertung.untersuchhal = haltungen_substanz_bewertung.haltnam AND Zustandsklasse_S <> '-'
                                GROUP BY substanz_haltung_bewertung.untersuchhal);""")
            #db.commit()
        except:
            pass

        try:
            # jh: subkans_update_betriebssicherheit
            db.sql("""UPDATE haltungen_substanz_bewertung 
                                SET objektklasse_betriebssicherheit =
                                (SELECT min(Zustandsklasse_B) 
                                FROM substanz_haltung_bewertung
                                WHERE substanz_haltung_bewertung.untersuchhal = haltungen_substanz_bewertung.haltnam AND Zustandsklasse_B <> '-'
                                GROUP BY substanz_haltung_bewertung.untersuchhal);""")
            #db.commit()
        except:
            pass

        try:
            # jh: NULL als Feldinhalt ist in der Regel besser für Datenbanken...
            # bl: NULL liefert falsche Werte bei export nach Excel!
            db.sql("""update haltungen_substanz_bewertung 
                                set objektklasse_standsicherheit = '-'
                                WHERE objektklasse_standsicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_substanz_bewertung 
                                set objektklasse_dichtheit = '-'
                                WHERE objektklasse_dichtheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_substanz_bewertung 
                                set objektklasse_betriebssicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        # jh: subkans_update_objektklasse_gesamt
        try:
            db.sql("""Update
                                haltungen_substanz_bewertung
                                SET
                                objektklasse_gesamt =
                                (
                               SELECT MIN(wert)
                               FROM (
                                   SELECT objektklasse_dichtheit AS wert
                                   UNION ALL
                                   SELECT objektklasse_standsicherheit
                                   UNION ALL
                                   SELECT objektklasse_betriebssicherheit
                               )
                               WHERE wert IS NOT NULL
                           );""")
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('substanz_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('substanz_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_substanz_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_substanz_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass

    def einzelfallbetrachtung_haltung(self):

        date = self.date
        db = self.db
        db_x = db
        data = db
        haltung = self.haltung
        crs = self.crs
        liste_pk =[]
        db1 = self.db
        #curs1 = db1.cursl()

        # nach SubKans

        #data = db
        #db = spatialite_connect(data)
        #curs = db.cursor()

        # if not self.db_qkan.sqlyml(
        #         'subkans_create_substanz_haltung_bewertung',
        #         "Erstelle substanz_haltung_bewertung",
        # ):
        #     return False
        sql = """CREATE TABLE IF NOT EXISTS substanz_haltung_bewertung AS 
                        SELECT pk, 
                        untersuchhal, 
                        schoben,
                        schunten,
                        id,
                        videozaehler,
                        inspektionslaenge,
                        station,
                        timecode,
                        kuerzel,
                        charakt1,
                        charakt2,
                        quantnr1,
                        quantnr2,
                        streckenschaden,
                        streckenschaden_lfdnr,
                        pos_von,
                        pos_bis,
                        foto_dateiname,
                        film_dateiname,
                        kommentar,
                        bw_bs,
                        createdat,
                        Zustandsklasse_D,
                        Zustandsklasse_S,
                        Zustandsklasse_B,
                        untersuchtag,
                        geom
                        FROM untersuchdat_haltung_bewertung"""
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('substanz_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass


        #db = spatialite_connect(db_x)
        #curs = db.cursor()

        try:
            db.sql("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Zustandsklasse_ges TEXT ;""")
        except:
            pass

        db.commit()

        # if not self.db_qkan.sqlyml(
        #         'subkans_update_zustandsklasse_gesamt',
        #         "Ermittle Zustandsklasse_ges",
        # ):
        #     return False
        try:
            db.sql("""Update
                                            substanz_haltung_bewertung
                                            set
                                            Zustandsklasse_ges =
                                            (
                                               SELECT MIN(wert)
                                               FROM (
                                                   SELECT Zustandsklasse_D AS wert
                                                   UNION ALL
                                                   SELECT Zustandsklasse_S
                                                   UNION ALL
                                                   SELECT Zustandsklasse_B
                                               )
                                               WHERE wert IS NOT NULL
                                           );""")
            db1.commit()
        except:
            pass



        # if not self.db_qkan.sqlyml(
        #         'subkans_create_haltungen_substanz_bewertung',
        #         "Erstelle haltungen_substanz_bewertung",
        # ):
        #     return False
        sql = """CREATE TABLE IF NOT EXISTS haltungen_substanz_bewertung AS 
                               SELECT pk, 
                               haltnam, 
                               schoben, 
                               schunten,                                  
                               hoehe,                                     
                               breite,                                   
                               laenge,                                 
                               baujahr,
                               untersuchtag,
                               untersucher,
                               wetter,
                               bewertungsart,
                               bewertungstag,
                                strasse,
                                datenart,
                                max_ZD,
                                max_ZB, 
                                max_ZS,
                                objektklasse_dichtheit,
                                objektklasse_standsicherheit,
                                objektklasse_betriebssicherheit,
                                objektklasse_gesamt,
                               geom
                               FROM haltungen_untersucht_bewertung """
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('haltungen_substanz_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        if self.datetype == 'Befahrungsdatum':

            if haltung:

                sql = """SELECT
                            substanz_haltung_bewertung.pk,
                            substanz_haltung_bewertung.untersuchhal,
                            NULL,
                            substanz_haltung_bewertung.schoben,
                            substanz_haltung_bewertung.schunten,
                            substanz_haltung_bewertung.id,
                            substanz_haltung_bewertung.videozaehler,
                            substanz_haltung_bewertung.inspektionslaenge,
                            substanz_haltung_bewertung.station,
                            substanz_haltung_bewertung.timecode,
                            substanz_haltung_bewertung.kuerzel,
                            substanz_haltung_bewertung.charakt1,
                            substanz_haltung_bewertung.charakt2,
                            substanz_haltung_bewertung.quantnr1,
                            substanz_haltung_bewertung.quantnr2,
                            substanz_haltung_bewertung.streckenschaden,
                            substanz_haltung_bewertung.pos_von,
                            substanz_haltung_bewertung.pos_bis,
                            substanz_haltung_bewertung.foto_dateiname,
                            substanz_haltung_bewertung.film_dateiname,
                            substanz_haltung_bewertung.kommentar,
                            substanz_haltung_bewertung.bw_bs,
                            substanz_haltung_bewertung.createdat,
                            haltungen.haltnam,
                            haltungen.material,
                            haltungen.hoehe,
                            haltungen.createdat,
                            substanz_haltung_bewertung.Zustandsklasse_D,
                            substanz_haltung_bewertung.Zustandsklasse_S,
                            substanz_haltung_bewertung.Zustandsklasse_B,
                            substanz_haltung_bewertung.untersuchtag
                            FROM
                            substanz_haltung_bewertung, haltungen
                            WHERE
                            haltungen.haltnam = substanz_haltung_bewertung.untersuchhal
                            AND(substanz_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            substanz_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            substanz_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung') AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120"""
                data = (date,)
                db.sql(sql, parameters=data)
            db.commit()

                # if not self.db_qkan.sqlyml(
                #         'subkans_zustand_einzel_untersuchdat',
                #         "Waehle Daten",parameters=data ):
                #     return False

        elif self.datetype == 'Importdatum':

            if haltung:

                # jh: subkans_zustand_einzel_createdat
                sql = """SELECT
                            substanz_haltung_bewertung.pk,
                            substanz_haltung_bewertung.untersuchhal,
                            NULL,
                            substanz_haltung_bewertung.schoben,
                            substanz_haltung_bewertung.schunten,
                            substanz_haltung_bewertung.id,
                            substanz_haltung_bewertung.videozaehler,
                            substanz_haltung_bewertung.inspektionslaenge,
                            substanz_haltung_bewertung.station,
                            substanz_haltung_bewertung.timecode,
                            substanz_haltung_bewertung.kuerzel,
                            substanz_haltung_bewertung.charakt1,
                            substanz_haltung_bewertung.charakt2,
                            substanz_haltung_bewertung.quantnr1,
                            substanz_haltung_bewertung.quantnr2,
                            substanz_haltung_bewertung.streckenschaden,
                            substanz_haltung_bewertung.pos_von,
                            substanz_haltung_bewertung.pos_bis,
                            substanz_haltung_bewertung.foto_dateiname,
                            substanz_haltung_bewertung.film_dateiname,
                            substanz_haltung_bewertung.kommentar,
                            substanz_haltung_bewertung.bw_bs,
                            substanz_haltung_bewertung.createdat,
                            haltungen.haltnam,
                            haltungen.material,
                            haltungen.hoehe,
                            haltungen.createdat,
                            substanz_haltung_bewertung.Zustandsklasse_D,
                            substanz_haltung_bewertung.Zustandsklasse_S,
                            substanz_haltung_bewertung.Zustandsklasse_B
                            FROM
                            substanz_haltung_bewertung, haltungen
                            WHERE
                            haltungen.haltnam = substanz_haltung_bewertung.untersuchhal
                            AND(substanz_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            substanz_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            substanz_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung') AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 """
                data = (date,)
                db.sql(sql, parameters=data)
            db.commit()

        for attr in db.fetchall():
            liste_pk.append(attr[0])

            if attr[10] == "BAB":
                if attr[11] == "A" and attr[12] in["A", "B", "C", "D", "E"]:
                    z = '4'
                    # jh: subkans_update_zks
                    sql = """
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #     db.commit()
                        continue
                    except:
                        pass
                elif (attr[11] == "B" or attr[11] == "C"):
                    if attr[12] == "A":
                        if attr[25] in ["", "not found"]:
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 3:
                                z = '1'
                            elif 3 > attr[13] >= 2:
                                z = '2'
                            elif attr[13] < 2:
                                z = '3'
                            else:
                                z = '5'
                            sql = f"""
                                                         UPDATE substanz_haltung_bewertung
                                                           SET Zustandsklasse_D = ?
                                                           WHERE substanz_haltung_bewertung.pk = ?;
                                                           """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #     db.commit()
                            except:
                                pass
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 8:
                                z = '0'
                            elif 8 > attr[13] >= 5:
                                z = '1'
                            elif 5 > attr[13] >= 3:
                                z = '2'
                            elif 3 > attr[13] >= 1:
                                z = '3'
                            elif attr[13] < 1:
                                z = '4'
                            else:
                                z = '5'
                            sql = f"""
                                  UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE substanz_haltung_bewertung.pk = ?;
                                    """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #db.commit()
                                continue
                            except:
                                pass

                        elif attr[25]/1000 <= 0.3:
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 3:
                                z = '1'
                            elif 3 > attr[13] >= 2:
                                z = '2'
                            elif attr[13] < 2:
                                z = '3'
                            else:
                                z = '5'
                            sql = f"""
                                                         UPDATE substanz_haltung_bewertung
                                                           SET Zustandsklasse_D = ?
                                                           WHERE substanz_haltung_bewertung.pk = ?;
                                                           """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #     db.commit()
                            except:
                                pass
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 3:
                                z = '0'
                            elif 3 > attr[13] >= 2:
                                z = '1'
                            elif 2 > attr[13] >= 1:
                                z = '2'
                            elif 1 > attr[13] >= 0.5:
                                z = '3'
                            else:
                                z = '5'
                            # jh: subkans_update_zks
                            sql = """
                                  UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE substanz_haltung_bewertung.pk = ?;
                                    """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #db.commit()
                                continue
                            except:
                                pass
                        elif 0.5 >= attr[25]/1000 > 0.3:
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 3:
                                z = '1'
                            elif 3 > attr[13] >= 2:
                                z = '2'
                            elif attr[13] < 2:
                                z = '3'
                            else:
                                z = '5'
                            sql = f"""
                                                         UPDATE substanz_haltung_bewertung
                                                           SET Zustandsklasse_D = ?
                                                           WHERE substanz_haltung_bewertung.pk = ?;
                                                           """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #     db.commit()
                            except:
                                pass
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 5:
                                z = '0'
                            elif 5 > attr[13] >= 3:
                                z = '1'
                            elif 3 > attr[13] >= 2:
                                z = '2'
                            elif 2 > attr[13] >= 1:
                                z = '3'
                            elif attr[13] < 1:
                                z = '4'
                            else:
                                z = '5'
                            # jh: subkans_update_zks
                            sql = """
                                  UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE substanz_haltung_bewertung.pk = ?;
                                    """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #db.commit()
                                continue
                            except:
                                pass
                        elif 0.7 >= attr[25]/1000 > 0.5:
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 3:
                                z = '1'
                            elif 3 > attr[13] >= 2:
                                z = '2'
                            elif attr[13] < 2:
                                z = '3'
                            else:
                                z = '5'
                            sql = f"""
                                                         UPDATE substanz_haltung_bewertung
                                                           SET Zustandsklasse_D = ?
                                                           WHERE substanz_haltung_bewertung.pk = ?;
                                                           """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #     db.commit()
                            except:
                                pass
                            if attr[13] is None:
                                z = 'Bitte pruefen!'
                            elif attr[13] >= 8:
                                z = '0'
                            elif 8 > attr[13] >= 4:
                                z = '1'
                            elif 4 > attr[13] >= 3:
                                z = '2'
                            elif 3 > attr[13] >= 2:
                                z = '3'
                            elif attr[13] < 2:
                                z = '4'
                            else:
                                z = '5'
                            # jh: subkans_update_zks
                            sql = """
                                  UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE substanz_haltung_bewertung.pk = ?;
                                    """
                            data = (z, attr[0])
                            try:
                                db.sql(sql,parameters=data)
                                #db.commit()
                                continue
                            except:
                                pass
                    if attr[12] == "B":
                        z = '4'
                        sql = f"""
                              UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 3:
                            z = '1'
                        elif 3 > attr[13] >= 2:
                            z = '2'
                        elif attr[13] < 2:
                            z = '3'
                        else:
                            z = '5'
                        sql = f"""
                                                     UPDATE substanz_haltung_bewertung
                                                       SET Zustandsklasse_D = ?
                                                       WHERE substanz_haltung_bewertung.pk = ?;
                                                       """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #     db.commit()
                            continue
                        except:
                            pass
                    if attr[12] in ["C", "D", "E"]:
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 3:
                            z = '1'
                        elif 3 > attr[13] >= 2:
                            z = '2'
                        elif attr[13] < 2:
                            z = '3'
                        else:
                            z = '5'
                        sql = f"""
                              UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #     db.commit()
                            continue
                        except:
                            pass
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 8:
                            z = '0'
                        elif 8 > attr[13] >= 5:
                            z = '1'
                        elif 5 > attr[13] >= 3:
                            z = '2'
                        elif 3 > attr[13] >= 1:
                            z = '3'
                        elif attr[13] < 1:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                              UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
            elif attr[10] == "BAC":
                if attr[11] == "A":
                    z = '1'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0]);
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B":
                    z = '1'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                                          UPDATE substanz_haltung_bewertung
                                            SET Zustandsklasse_B = ?
                                            WHERE substanz_haltung_bewertung.pk = ?;
                                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        # db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "C":
                    z = '0'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAD":
                if attr[11] == "A":
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B" and attr[12] == "A":
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B" and attr[12] == "B":
                    z = '1'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "C":
                    z = '0'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '0'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "D":
                    z = '0'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAE":
                if attr[13] is None:
                    z = 'Bitte pruefen!'
                elif attr[13] >= 100:
                    z = '2'
                elif attr[13] < 100:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                if attr[13] >= 100:
                    z = '2'
                elif 100 > attr[13] > 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BAF":
                if attr[11] == "A" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B" and attr[12] in ["A", "E", "Z"]:
                    z = '3'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "C" and attr[12] in["A", "B", "C", "D", "E", "Z"]:
                    z = '3'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "D" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "E" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '1'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "F" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '3'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "G" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "H" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '1'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "I" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '1'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "J" and attr[12] in ["B", "C", "D", "E", "Z"]:
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "K" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '3'
                    sql = f"""
                                          UPDATE substanz_haltung_bewertung
                                            SET Zustandsklasse_B = ?
                                            WHERE substanz_haltung_bewertung.pk = ?;
                                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "Z" and attr[12] in ["A", "B", "C", "D", "E", "Z"]:
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAG":
                if attr[25]/1000 <= 0.25:
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 30:
                        z = '1'
                    elif 30 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                elif 0.25 < attr[25]/1000 <= 0.5:
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 80:
                        z = '0'
                    elif 80 > attr[13] >= 60:
                        z = '1'
                    elif 60 > attr[13] >= 40:
                        z = '2'
                    elif 40 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                elif 0.5 < attr[25]/1000 <= 0.8:
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 70:
                        z = '2'
                    elif 70 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                elif attr[25]/1000 > 0.8:
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 30:
                        z = '3'
                    elif attr[13] < 30:
                        z = '4'
                    else:
                        z = '5'
                sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BAH":
                if attr[11] in ["B", "C", "D"]:
                    z = '2'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "E":
                    z = '-'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "Z":
                    z = '3'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAI":
                if attr[11] == "A":
                    if attr[12] == "A":
                        z = '2'
                        sql = f"""
                              UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                        z = '4'
                        sql = f"""
                              UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    elif attr[12] in ["B", "C", "D"]:
                        z = '2'
                        sql = f"""
                              UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                        z = '3'
                        sql = f"""
                              UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                elif attr[11] == "Z" and attr[12] == "Y":
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 35:
                        z = '1'
                    elif 35 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAJ":
                if attr[11] == "A":
                    if attr[25]/1000 <= 0.4:
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 70:
                            z = '0'
                        elif 70 > attr[13] >= 50:
                            z = '1'
                        elif 50 > attr[13] >= 30:
                            z = '2'
                        elif 30 > attr[13] >= 20:
                            z = '3'
                        elif attr[13] < 20:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                    elif 0.4 < attr[25]/1000 <= 0.8:
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 80:
                            z = '0'
                        elif 80 > attr[13] >= 60:
                            z = '1'
                        elif 60 > attr[13] >= 40:
                            z = '2'
                        elif 40 > attr[13] >= 20:
                            z = '3'
                        elif attr[13] < 20:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                    elif attr[25]/1000 > 0.8:
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 90:
                            z = '0'
                        elif 90 > attr[13] >= 65:
                            z = '1'
                        elif 65 > attr[13] >= 40:
                            z = '2'
                        elif 40 > attr[13] >= 20:
                            z = '3'
                        elif attr[13] < 20:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                    z = '4'
                    sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B":
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 30:
                        z = '0'
                    elif 30 > attr[13] >= 20:
                        z = '1'
                    elif 20 > attr[13] >= 15:
                        z = '2'
                    elif 15 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "C":
                    if attr[25]/1000 <= 0.2:
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 12:
                            z = '0'
                        elif 12 > attr[13] >= 9:
                            z = '1'
                        elif 9 > attr[13] >= 7:
                            z = '2'
                        elif 7 > attr[13] >= 5:
                            z = '3'
                        elif attr[13] < 5:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                    elif 0.2 < attr[25]/1000 <= 0.5:
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 6:
                            z = '0'
                        elif 6 > attr[13] >= 4:
                            z = '1'
                        elif 4 > attr[13] >= 3:
                            z = '2'
                        elif 3 > attr[13] >= 2:
                            z = '3'
                        elif attr[13] < 2:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                    elif attr[25]/1000 > 0.5:
                        if attr[13] is None:
                            z = 'Bitte pruefen!'
                        elif attr[13] >= 6:
                            z = '0'
                        elif 6 > attr[13] >= 4:
                            z = '1'
                        elif 4 > attr[13] >= 3:
                            z = '2'
                        elif 3 > attr[13] >= 1:
                            z = '3'
                        elif attr[13] < 1:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                          UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass
                    z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAK":
                if attr[11] == "A":
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 35:
                        z = '1'
                    elif 35 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B":
                    z = '4'
                    sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_D = ?
                                        WHERE substanz_haltung_bewertung.pk = ?;
                                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "C":
                    z = '2'
                    sql = f"""
                            UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "D" and attr[12] in ["A", "B", "D"]:
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "D" and attr[12] == "C":
                    z = '2'
                    sql = f"""
                            UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?;
                            """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "E":
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 35:
                        z = '1'
                    elif 35 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "F":
                    z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "G":
                    z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "H":
                    z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "I":
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "J":
                    z = '1'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "K":
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "L":
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_S = ?
                                        WHERE substanz_haltung_bewertung.pk = ?;
                                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "M":
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "N":
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "Z":
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAL":
                if attr[11] == "A" and attr[12] in ["A", "B", "C", "D"]:
                    z = '1'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B" and attr[12] in ["A", "B", "C", "D"]:
                    z = '1'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "C" and attr[12] in ["A", "B", "C", "D"]:
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "D" and attr[12] in ["A", "B", "C", "D"]:
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "E" and attr[12] in ["A", "B", "C", "D"]:
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 35:
                        z = '1'
                    elif 35 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "F" and attr[12] in ["A", "B", "C","D"]:
                    z = '1'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "G" and attr[12] in ["A", "B", "C", "D"]:
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "Z" and attr[12] in ["A", "B", "C", "D"]:
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAM":
                if (attr[11] == "A" or attr[11] == "C"):
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[10] == "BAM" and attr[11] == "B":
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BAN":
                z = '2'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BAO":
                z = '1'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BAP":
                z = '1'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BBA" and attr[11] in ["A", "B", "C"]:
                z = '2'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                if attr[13] is None:
                    z = 'Bitte pruefen!'
                elif attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BBB" and attr[11] == "A":
                z = '3'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                if attr[13] is None:
                    z = 'Bitte pruefen!'
                elif attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif 10 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BBB" and (attr[11] == "B" or attr[11] == "C" or attr[11] == "Z"):
                if attr[13] is None:
                    z = 'Bitte pruefen!'
                elif attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif 10 > attr[13] >= 5:
                    z = '3'
                elif attr[13] < 5:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BBC":
                if (attr[11] == "A" or attr[11] == "B"):
                    z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif (attr[11] == "C" or attr[11] == "Z"):
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 40:
                        z = '1'
                    elif 40 > attr[13] >= 25:
                        z = '2'
                    elif 25 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BBD" and attr[11] in ["A", "B", "C", "D", "Z"]:
                z = '1'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                if attr[13] is None:
                    z = 'Bitte pruefen!'
                elif attr[13] >= 30:
                    z = '0'
                elif 30 > attr[13] >= 20:
                    z = '1'
                elif 20 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BBE":
                if (attr[11] == "D" or attr[11] == "G"):
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 35:
                        z = '1'
                    elif 35 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        # db.commit()
                        continue
                    except:
                        pass
                elif attr[11] in ["A", "B", "C", "E", "F", "H", "Z"]:
                    if attr[13] is None:
                        z = 'Bitte pruefen!'
                    elif attr[13] >= 50:
                        z = '0'
                    elif 50 > attr[13] >= 35:
                        z = '1'
                    elif 35 > attr[13] >= 20:
                        z = '2'
                    elif 20 > attr[13] >= 5:
                        z = '3'
                    elif attr[13] < 5:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BBF":
                if attr[11] == "A":
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "B" or attr[11] == "C":
                    z = '1'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] == "D":
                    z = '1'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
            elif attr[10] == "BBG":
                z = '1'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BBH" and attr[11] in ["A", "B", "Z"] and attr[12] in ["A", "B", "C", "Z"]:
                z = '-'
                sql = f"""
                    UPDATE substanz_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE substanz_haltung_bewertung.pk = ?;
                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass
            elif attr[10] == "BDB":
                if attr[11] in ["AA", "AB", "AC", "AD", "AE"]:
                    z = '3'
                    sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_D = ?
                                        WHERE substanz_haltung_bewertung.pk = ?;
                                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[11] in ["BA", "BB", "BC"]:
                    z = '3'
                    sql = f"""
                                UPDATE substanz_haltung_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE substanz_haltung_bewertung.pk = ?;
                                """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            elif attr[10] == "BDE" and attr[11] in ["A", "C", "D", "E"]:
                if attr[12] == "A":
                    z = '1'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                elif attr[12] == "B":
                    z = '2'
                    sql = f"""
                        UPDATE substanz_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE substanz_haltung_bewertung.pk = ?;
                        """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            try:
                db.commit()
            except:
                pass

            z = '-'
            sql = f"""
                            UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE substanz_haltung_bewertung.pk = ?
                            """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass
            sql = f"""
                            UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE substanz_haltung_bewertung.pk = ?
                            """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass
            sql = f"""
                            UPDATE substanz_haltung_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE substanz_haltung_bewertung.pk = ?
                            """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass


            z = '-'
            sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_D = ?
                                        WHERE substanz_haltung_bewertung.pk = ?
                                        """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass
            sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_B = ?
                                        WHERE substanz_haltung_bewertung.pk = ?
                                        """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass
            sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_S = ?
                                        WHERE substanz_haltung_bewertung.pk = ?
                                        """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass

        z = '5'
        sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Zustandsklasse_D is Null or Zustandsklasse_D = '-'
                                    """
        data = (z,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass
        sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_B = ?
                                    WHERE Zustandsklasse_B is Null or Zustandsklasse_B = '-'
                                    """
        data = (z,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass
        sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE Zustandsklasse_S is Null or Zustandsklasse_S = '-'
                                    """
        data = (z,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('substanz_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('substanz_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_substanz_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_substanz_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db.dbname)
        schema = ''
        table = 'substanz_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        substanz_haltung_bewertung =  enums.LAYERBEZ.SK_EINZELSCHAEDEN_HALTUNGEN.value
        vlayer = QgsVectorLayer(uri.uri(), substanz_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(substanz_haltung_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/substanz_haltung_bewertung_dwa.qml')
        #QgsProject.instance().addMapLayer(vlayer)
        group = 'Ergebnisse'
        layersRoot = QgsProject.instance().layerTreeRoot()
        QgsProject.instance().addMapLayer(vlayer, False)
        atcGroup = layersRoot.findGroup(group)
        if atcGroup is None:
            atcGroup = layersRoot.addGroup(group)
        atcGroup.addLayer(vlayer)



    def bewertung_subkans(self):
        date = self.date
        db = self.db
        db_x = db
        data = db
        haltung = self.haltung
        crs = self.crs
        liste_pk = []
        db1 = self.db
        #curs1 = db1.cursl()

        # nach SubKans
        logger.debug(f'Start der Zuordnung von Schadensart und Schadensauspraegung: {datetime.now()}')
        data = db
        #db = spatialite_connect(data)
        #curs = db.cursor()
        if self.datetype == 'Befahrungsdatum':


            # jh: subkans_zustand_bc_ab_untersuchdat
            sql = """SELECT
                                    substanz_haltung_bewertung.pk,
                                    substanz_haltung_bewertung.untersuchhal,
                                    NULL,
                                    substanz_haltung_bewertung.schoben,
                                    substanz_haltung_bewertung.schunten,
                                    substanz_haltung_bewertung.id,
                                    substanz_haltung_bewertung.videozaehler,
                                    substanz_haltung_bewertung.inspektionslaenge,
                                    substanz_haltung_bewertung.station,
                                    substanz_haltung_bewertung.timecode,
                                    substanz_haltung_bewertung.kuerzel,
                                    substanz_haltung_bewertung.charakt1,
                                    substanz_haltung_bewertung.charakt2,
                                    substanz_haltung_bewertung.quantnr1,
                                    substanz_haltung_bewertung.quantnr2,
                                    substanz_haltung_bewertung.streckenschaden,
                                    substanz_haltung_bewertung.pos_von,
                                    substanz_haltung_bewertung.pos_bis,
                                    substanz_haltung_bewertung.foto_dateiname,
                                    substanz_haltung_bewertung.film_dateiname,
                                    substanz_haltung_bewertung.kommentar,
                                    substanz_haltung_bewertung.bw_bs,
                                    substanz_haltung_bewertung.createdat,
                                    haltungen.haltnam,
                                    haltungen.material,
                                    haltungen.hoehe,
                                    haltungen.createdat,
                                    substanz_haltung_bewertung.Zustandsklasse_D,
                                    substanz_haltung_bewertung.Zustandsklasse_S,
                                    substanz_haltung_bewertung.Zustandsklasse_B,
                                    substanz_haltung_bewertung.untersuchtag
                                    FROM
                                    substanz_haltung_bewertung, haltungen
                                    WHERE
                                    haltungen.haltnam = substanz_haltung_bewertung.untersuchhal
                                    AND ((substanz_haltung_bewertung.kuerzel = 'BCA') OR ( substanz_haltung_bewertung.kuerzel = 'BCB'))
                                     AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120 """

        elif self.datetype == 'Importdatum':

            sql = """SELECT
                                    substanz_haltung_bewertung.pk,
                                    substanz_haltung_bewertung.untersuchhal,
                                    NULL,
                                    substanz_haltung_bewertung.schoben,
                                    substanz_haltung_bewertung.schunten,
                                    substanz_haltung_bewertung.id,
                                    substanz_haltung_bewertung.videozaehler,
                                    substanz_haltung_bewertung.inspektionslaenge,
                                    substanz_haltung_bewertung.station,
                                    substanz_haltung_bewertung.timecode,
                                    substanz_haltung_bewertung.kuerzel,
                                    substanz_haltung_bewertung.charakt1,
                                    substanz_haltung_bewertung.charakt2,
                                    substanz_haltung_bewertung.quantnr1,
                                    substanz_haltung_bewertung.quantnr2,
                                    substanz_haltung_bewertung.streckenschaden,
                                    substanz_haltung_bewertung.pos_von,
                                    substanz_haltung_bewertung.pos_bis,
                                    substanz_haltung_bewertung.foto_dateiname,
                                    substanz_haltung_bewertung.film_dateiname,
                                    substanz_haltung_bewertung.kommentar,
                                    substanz_haltung_bewertung.bw_bs,
                                    substanz_haltung_bewertung.createdat,
                                    haltungen.haltnam,
                                    haltungen.material,
                                    haltungen.hoehe,
                                    haltungen.createdat,
                                    substanz_haltung_bewertung.Zustandsklasse_D,
                                    substanz_haltung_bewertung.Zustandsklasse_S,
                                    substanz_haltung_bewertung.Zustandsklasse_B
                                    FROM
                                    substanz_haltung_bewertung, haltungen
                                    WHERE
                                    haltungen.haltnam = substanz_haltung_bewertung.untersuchhal
                                    AND ((substanz_haltung_bewertung.kuerzel = 'BCA') OR ( substanz_haltung_bewertung.kuerzel = 'BCB'))
                                    AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 """
        else:
            logger.error_code(f"{self.datetype=} ist ungültig")
            raise BaseException

        data = (date,)
        db.sql(sql,parameters=data)

        for attr in db.fetchall():
            if attr[10] == "BCA" and (attr[11] == "C" or attr[11] == "E"):
                z = '4'
                sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE substanz_haltung_bewertung.pk = ?;
                                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    continue
                except:
                    pass

            if attr[10] == "BCB":
                z = '4'
                sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_B = ?
                                    WHERE substanz_haltung_bewertung.pk = ?;
                                    """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    continue
                except:
                    pass

            try:
                db.commit()
            except:
                pass

            z = '-'
            sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_D = ?
                                        WHERE substanz_haltung_bewertung.pk = ?
                                        """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass
            sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_B = ?
                                        WHERE substanz_haltung_bewertung.pk = ?
                                        """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass
            sql = f"""
                                        UPDATE substanz_haltung_bewertung
                                        SET Zustandsklasse_S = ?
                                        WHERE substanz_haltung_bewertung.pk = ?
                                        """
            data = (z, attr[0])
            try:
                db.sql(sql,parameters=data)
                db.commit()
            except:
                pass

        z = '5'
        sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Zustandsklasse_D is Null or Zustandsklasse_D = '-'
                                    """
        data = (z,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass
        sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_B = ?
                                    WHERE Zustandsklasse_B is Null or Zustandsklasse_B = '-'
                                    """
        data = (z,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass
        sql = f"""
                                    UPDATE substanz_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE Zustandsklasse_S is Null or Zustandsklasse_S = '-'
                                    """
        data = (z,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass
        #Schadensart und -ausprägung ergänzen

        date = self.date
        db_x = self.db
        crs = self.crs
        haltung = self.haltung

        data = db_x

        db1 = self.db
        #curs1 = db1.cursl()


        # nach DWA

        sql = """CREATE TABLE IF NOT EXISTS substanz_haltung_bewertung AS 
                SELECT pk, 
                untersuchhal, 
                schoben,
                schunten,
                id,
                videozaehler,
                inspektionslaenge,
                station,
                timecode,
                kuerzel,
                charakt1,
                charakt2,
                quantnr1,
                quantnr2,
                streckenschaden,
                streckenschaden_lfdnr,
                pos_von,
                pos_bis,
                foto_dateiname,
                film_dateiname,
                kommentar,
                bw_bs,
                createdat,
                Zustandsklasse_D,
                Zustandsklasse_S,
                Zustandsklasse_B,
                untersuchtag,
                geom
                FROM untersuchdat_haltung_bewertung """
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('substanz_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        # db = spatialite_connect(db_x)
        # curs = db.cursor()

        # jh: Kann in vorheriger Abfrage einfach ergänzt werden
        # try:
            # db.sql("""PRAGMA table_info(substanz_haltung_bewertung);""")

        # except:
            # pass

        try:
            db.sql("""PRAGMA table_info(substanz_haltung_bewertung);""")

        except:
            pass

        columns = [row[1] for row in db.fetchall()]

        if 'Zustandsklasse_ges' not in columns:
            try:
                db.sql("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Zustandsklasse_ges TEXT ;""")
            except:
                pass
        db.commit()

        # jh: subkans_update_zustandsklasse_gesamt
        try:
            db.sql("""Update
                                    substanz_haltung_bewertung
                                    set
                                    Zustandsklasse_ges =
                                    (
                                               SELECT MIN(wert)
                                               FROM (
                                                   SELECT Zustandsklasse_D AS wert
                                                   UNION ALL
                                                   SELECT Zustandsklasse_S
                                                   UNION ALL
                                                   SELECT Zustandsklasse_B
                                               )
                                               WHERE wert IS NOT NULL
                                           );""")
            db1.commit()
        except:
            pass

        try:
            db.sql("""UPDATE haltungen_substanz_bewertung 
            							SET objektklasse_dichtheit =
            							(SELECT min(Zustandsklasse_D) 
            							FROM substanz_haltung_bewertung
            							WHERE substanz_haltung_bewertung.untersuchhal = haltungen_substanz_bewertung.haltnam AND Zustandsklasse_D <> '-'
            							GROUP BY substanz_haltung_bewertung.untersuchhal);""")

        except:
            pass

        try:
            db.sql("""UPDATE haltungen_substanz_bewertung 
            							SET objektklasse_betriebssicherheit =
            							(SELECT min(Zustandsklasse_B) 
            							FROM substanz_haltung_bewertung
            							WHERE substanz_haltung_bewertung.untersuchhal = haltungen_substanz_bewertung.haltnam AND Zustandsklasse_D <> '-'
            							GROUP BY substanz_haltung_bewertung.untersuchhal);""")

        except:
            pass

        try:
            db.sql("""UPDATE haltungen_substanz_bewertung 
            							SET objektklasse_standsicherheit =
            							(SELECT min(Zustandsklasse_S) 
            							FROM substanz_haltung_bewertung
            							WHERE substanz_haltung_bewertung.untersuchhal = haltungen_substanz_bewertung.haltnam AND Zustandsklasse_D <> '-'
            							GROUP BY substanz_haltung_bewertung.untersuchhal);""")

        except:
            pass

        try:
            db.sql("""Update
                    haltungen_substanz_bewertung
                    SET objektklasse_gesamt = (
                    SELECT
                    CASE
                    WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_haltung_bewertung WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_substanz_bewertung.haltnam)
                    THEN '-'
                    WHEN typeof(objektklasse_dichtheit) = 'text' AND  objektklasse_dichtheit != '-' THEN objektklasse_dichtheit
                    WHEN typeof(objektklasse_standsicherheit) = 'text' AND  objektklasse_standsicherheit != '-' THEN objektklasse_standsicherheit
                    WHEN typeof(objektklasse_betriebssicherheit) = 'text' AND  objektklasse_betriebssicherheit != '-' THEN objektklasse_betriebssicherheit
                    WHEN objektklasse_dichtheit = '-' AND objektklasse_standsicherheit = '-' AND objektklasse_betriebssicherheit = '-' THEN '5'

                    ELSE (
                    SELECT MIN(wert)
                    FROM (
                    SELECT CAST(objektklasse_dichtheit AS REAL) AS wert
                    UNION ALL
                    SELECT CAST(objektklasse_standsicherheit AS REAL)
                    UNION ALL
                    SELECT CAST(objektklasse_betriebssicherheit AS REAL)
                        )
                        )
                    END AS ergebnis
                    );""")
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadensart TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadensauspraegung TEXT ;""")
        except:
            pass

        db.commit()

        if self.datetype == 'Befahrungsdatum':

            sql = """
                   SELECT
                       substanz_haltung_bewertung.pk,
                       substanz_haltung_bewertung.untersuchhal,
                       NULL,
                       substanz_haltung_bewertung.schoben,
                       substanz_haltung_bewertung.schunten,
                       substanz_haltung_bewertung.id,
                       substanz_haltung_bewertung.videozaehler,
                       substanz_haltung_bewertung.inspektionslaenge,
                       substanz_haltung_bewertung.station,
                       substanz_haltung_bewertung.timecode,
                       substanz_haltung_bewertung.kuerzel,
                       substanz_haltung_bewertung.charakt1,
                       substanz_haltung_bewertung.charakt2,
                       substanz_haltung_bewertung.quantnr1,
                       substanz_haltung_bewertung.quantnr2,
                       substanz_haltung_bewertung.streckenschaden,
                       substanz_haltung_bewertung.pos_von,
                       substanz_haltung_bewertung.pos_bis,
                       substanz_haltung_bewertung.foto_dateiname,
                       substanz_haltung_bewertung.film_dateiname,
                       substanz_haltung_bewertung.bw_bs,
                       substanz_haltung_bewertung.createdat,
                       substanz_haltung_bewertung.Zustandsklasse_ges,
                       haltungen.haltnam,
                       haltungen.material,
                       haltungen.hoehe,
                       haltungen.createdat,
                       substanz_haltung_bewertung.untersuchtag
                   FROM substanz_haltung_bewertung, haltungen
                   WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120 AND Zustandsklasse_ges IN (0,1,2,3,4)
               """


        elif self.datetype == 'Importdatum':

            sql = """
                   SELECT
                       substanz_haltung_bewertung.pk,
                       substanz_haltung_bewertung.untersuchhal,
                       NULL,
                       substanz_haltung_bewertung.schoben,
                       substanz_haltung_bewertung.schunten,
                       substanz_haltung_bewertung.id,
                       substanz_haltung_bewertung.videozaehler,
                       substanz_haltung_bewertung.inspektionslaenge,
                       substanz_haltung_bewertung.station,
                       substanz_haltung_bewertung.timecode,
                       substanz_haltung_bewertung.kuerzel,
                       substanz_haltung_bewertung.charakt1,
                       substanz_haltung_bewertung.charakt2,
                       substanz_haltung_bewertung.quantnr1,
                       substanz_haltung_bewertung.quantnr2,
                       substanz_haltung_bewertung.streckenschaden,
                       substanz_haltung_bewertung.pos_von,
                       substanz_haltung_bewertung.pos_bis,
                       substanz_haltung_bewertung.foto_dateiname,
                       substanz_haltung_bewertung.film_dateiname,
                       substanz_haltung_bewertung.bw_bs,
                       substanz_haltung_bewertung.createdat,
                       substanz_haltung_bewertung.Zustandsklasse_ges,
                       haltungen.haltnam,
                       haltungen.material,
                       haltungen.hoehe,
                       haltungen.createdat
                   FROM substanz_haltung_bewertung, haltungen
                   WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 AND Zustandsklasse_ges IN (0,1,2,3,4)
               """
        else:
            logger.error_code(f"{self.datetype=} ist ungültig")
            raise BaseException

            # if not self.db.sqlyml(
            #         'subkans_zustand_bc_ab_createdat',
            #         "",
            #         data
            # ):
            #     return False
        data = (date,)
        db.sql(sql, parameters=data)
        db.commit()


        for attr in db.fetchall():

            # 1 BAA-AB
            if attr[10] == "BAA" and attr[11] in ["A", "B"]:
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 2 BAB-A-ACE
            if attr[10] == "BAB":
                if attr[11] == "A" and attr[12] in ["A", "C", "E"]:
                    if attr[15] in ["", None, "not found"]:
                        z = 'PktS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql, parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 2 BAB-A-BD
                if attr[11] == "A" and attr[12] == "B":

                    z = 'UmfS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'OfS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

                # 2 BAB-A-D
                if attr[11] == "A" and attr[12] == "D":
                    if attr[15] in ["", None, "not found"]:
                        z = 'UmfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 2 BAB-BC-ACE
                if attr[11] in ["B", "C"] and attr[12] in ["A", "C", "E"]:
                    if attr[15] in ["", None, "not found"]:
                        z = 'PktS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 2 BAB-BC-B
                if attr[11] in ["B", "C"] and attr[12] == "B":
                    z = 'UmfS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

                # 2 BAB-BC-D
                if attr[11] in ["B", "C" and attr[12] == "D"]:
                    if attr[15] in ["", None, "not found"]:
                        z = 'UmfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

            # 3 BAC-ABC
            elif attr[10] == "BAC" and attr[11] in ["A", "B","C"]:
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 4 BAD-ABCD-AB
            elif attr[10] == "BAD" and attr[11] in ["A", "B", "C", "D"] and attr[12] in ["A","B"]:
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 5 BAE
            elif attr[10] == "BAE":
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            elif attr[10] == "BAF":
                # 6 BAF-ABCDEFGHJKZ-ABCDEZ
                if attr[11] in ["A", "C", "D", "E", "F", "G", "H","J", "Z"]:
                    if attr[15] in ["", None, "not found"]:
                        z = 'PktS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 6 BAF-ABCDEFGHJKZ-ABCDEZ
                if attr[11] in ["B", "K"]:
                    z = 'PktS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'OfS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass


                # 6 BAF-I-ABCDEZ
                if attr[11] == "I":
                    if attr[15] in ["", None, "not found"]:
                        z = 'PktS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

            # 7 BAG
            elif (attr[10] == "BAG"):
                z = 'PktS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensart = ?
                                           WHERE substanz_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass

                z = 'SoB'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensauspraegung = ?
                                           WHERE substanz_haltung_bewertung.pk = ? 
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass


            # 8 BAH-ABCDZ
            elif attr[10] == "BAH" and attr[11] in ["A", "B", "C", "D", "Z"]:
                z = 'PktS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensart = ?
                                           WHERE substanz_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass

                z = 'DdS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensauspraegung = ?
                                           WHERE substanz_haltung_bewertung.pk = ? 
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass

            # 9 BAI-AZ-ABCD
            elif attr[10] == "BAI" and attr[11] in ["A", "Z"] and attr[12] in ["A", "B", "C", "D"]:

                z = 'UmfS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensart = ?
                                           WHERE substanz_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass

                z = 'SoB'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensauspraegung = ?
                                           WHERE substanz_haltung_bewertung.pk = ? 
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass

            # 10 BAJ-ABC
            elif attr[10] == "BAJ" and attr[11] in ["A", "B", "C"]:
                z = 'UmfS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensart = ?
                                           WHERE substanz_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass

                z = 'DdS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensauspraegung = ?
                                           WHERE substanz_haltung_bewertung.pk = ? 
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass

            # 11 BAK-ABCDEFGHIJKLMN-ABCD
            elif attr[10] == "BAK":
                if attr[11] in ["A", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"] and attr[12] in ["A", "B", "C", "D"]:
                    if attr[15] in ["", None,
                                    "not found"]:  # hier muss noch eine Unterscheidung für UmfS statt nur PktS/StrS getroffen werden. Wie sähe der Tabellenwert dann aus?
                        z = 'PktS'  # or z = 'UmfS' berücksichtigen!
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 11 BAK-BZ-ABCD
                if attr[11] in ["B", "Z"] and attr[12] in ["A", "B", "C", "D"]:
                    if attr[15] in ["", None,
                                    "not found"]:  # hier muss noch eine Unterscheidung für UmfS statt nur PktS/StrS getroffen werden. Wie sähe der Tabellenwert dann aus?
                        z = 'PktS'  # or z = 'UmfS' berücksichtigen!
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'SoB'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'SoB'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

            # 12 BAL-ABCDFGZ-ABCD
            elif attr[10] == "BAL":
                if attr[11] in ["A", "B", "C", "D", "F", "G", "Z"] and attr[12] in ["A", "B", "C", "D"]:
                    if attr[15] in ["", None,
                                    "not found"]:  # hier muss noch eine Unterscheidung für UmfS statt nur PktS/StrS getroffen werden. Wie sähe der Tabellenwert dann aus?
                        z = 'PktS'  # or z = 'UmfS' berücksichtigen!
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 12 BAL-E-ABCD
                if attr[11] == "E" and attr[12] in ["A", "B", "C", "D"]:
                    if attr[15] in ["", None,
                                    "not found"]:  # hier muss noch eine Unterscheidung für UmfS statt nur PktS/StrS getroffen werden. Wie sähe der Tabellenwert dann aus?
                        z = 'PktS'  # or z = 'UmfS' berücksichtigen!
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'SoB'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'SoB'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

            # 13 BAM-A
            elif attr[10] == "BAM":
                if attr[11] == "A":
                    if attr[15] in ["", None, "not found"]:
                        z = 'PktS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 13 BAM-B
                if attr[11] == "B":
                    z = 'UmfS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

                # 13 BAM-C
                if attr[11] == "C":
                    if attr[15] in ["", None, "not found"]:
                        z = 'UmfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'DdS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

            # 14 BAN
            elif attr[10] == "BAN":
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'OfS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'OfS'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 15 BAO
            elif attr[10] == "BAO":
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                       # db.commit()
                        continue
                    except:
                        pass

            # 16 BAP
            elif attr[10] == "BAP":
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 17 BBA-ABC
            elif attr[10] == "BBA" and attr[11] in ["A", "B", "C"]:
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 18 BBB-ABCZ
            elif attr[10] == "BBB" and attr[11] in ["A", "B", "C", "Z"]:
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 19 BBC-ABC
            elif attr[10] == "BBC" and attr[11] in ["A", "B", "C"]:
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 19 BBC-Z
            elif (attr[10] == "BBC" and attr[11] == "Z"):
                if attr[15] in ["", None, "not found"]:
                    z = '-'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = '-'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 20 BBD
            elif (attr[10] == "BBD"):
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # 21 BBE-ABDEFG
            elif attr[10] == "BBE":
                if attr[11] in ["A", "B", "D", "E", "F", "G"]:
                    z = 'PktS'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'SoB'
                    sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

                # 21 BBE-CHZ
                if  attr[11] in ["C", "H", "Z"]:
                    if attr[15] in ["", None, "not found"]:
                        z = 'PktS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'SoB'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'SoB'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

            # 22 BBF-ABCD
            elif attr[10] == "BBF" and attr[11] in ["A", "B", "C", "D"]:
                z = 'PktS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensart = ?
                                           WHERE substanz_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass

                z = 'DdS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensauspraegung = ?
                                           WHERE substanz_haltung_bewertung.pk = ? 
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass

            # 23 BBG
            elif (attr[10] == "BBG"):
                z = 'PktS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensart = ?
                                           WHERE substanz_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass

                z = 'DdS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensauspraegung = ?
                                           WHERE substanz_haltung_bewertung.pk = ? 
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass

            # 25 BCA-ABCDEFZ
            elif attr[10] == "BCA" and attr[11] in ["A", "B", "C", "D", "E", "F", "Z"] and attr[12] in ["A", "B"]:
                z = 'PktS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensart = ?
                                           WHERE substanz_haltung_bewertung.pk = ?;
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                except:
                    pass

                z = 'DdS'
                sql = f"""
                                         UPDATE substanz_haltung_bewertung
                                           SET Schadensauspraegung = ?
                                           WHERE substanz_haltung_bewertung.pk = ? 
                                           """
                data = (z, attr[0])
                try:
                    db.sql(sql,parameters=data)
                    #db.commit()
                    continue
                except:
                    pass

            # 26 BCB-AF
            elif attr[10] == "BCB":
                if attr[11] in ["A", "F"]:
                    z = 'StrS'
                    sql = f"""
                                                     UPDATE substanz_haltung_bewertung
                                                       SET Schadensart = ?
                                                       WHERE substanz_haltung_bewertung.pk = ?;
                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'OfS'
                    sql = f"""
                                                                             UPDATE substanz_haltung_bewertung
                                                                               SET Schadensauspraegung = ?
                                                                               WHERE substanz_haltung_bewertung.pk = ? 
                                                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

                # 26 BCB-G
                if  attr[11] == "G":
                    z = 'PktS'
                    sql = f"""
                                                     UPDATE substanz_haltung_bewertung
                                                       SET Schadensart = ?
                                                       WHERE substanz_haltung_bewertung.pk = ?;
                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'OfS'
                    sql = f"""
                                                     UPDATE substanz_haltung_bewertung
                                                       SET Schadensauspraegung = ?
                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

                # 26 BCB-BZ
                if attr[11] in ["B", "Z"]:
                    if attr[15] in ["", None, "not found"]:
                        z = 'PktS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensauspraegung = ?
                                                   WHERE substanz_haltung_bewertung.pk = ? 
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass
                    else:
                        z = 'StrS'
                        sql = f"""
                                                 UPDATE substanz_haltung_bewertung
                                                   SET Schadensart = ?
                                                   WHERE substanz_haltung_bewertung.pk = ?;
                                                   """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                        except:
                            pass

                        z = 'OfS'
                        sql = f"""
                                                                         UPDATE substanz_haltung_bewertung
                                                                           SET Schadensauspraegung = ?
                                                                           WHERE substanz_haltung_bewertung.pk = ? 
                                                                           """
                        data = (z, attr[0])
                        try:
                            db.sql(sql,parameters=data)
                            #db.commit()
                            continue
                        except:
                            pass

                # 26 BCB-CDE
                if attr[11] in ["C", "D", "E"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'DdS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

            # "keine Relevanz":  #24 BBH-ABZ, #27 BCC-AB, #28 BDB, #31 BDE-ACDEYY, #32 BDF-ABCZ, #33 BDG-ABCZ
            elif (attr[10] == "BBH" and attr[11] in ["A", "B", "Z"]) \
                    or (attr[10] == "BCC" and attr[11] in ["A", "B"])\
                    or (attr[10] == "BDB") \
                    or (attr[10] == "BDE" and attr[11] in ["A", "C", "D", "E","YY"])\
                    or (attr[10] == "BDF" and attr[11] in ["A", "B", "C", "Z"] )\
                    or (attr[10] == "BDG" and attr[11] in ["A", "B", "C", "Z"]):
                if attr[15] in ["", None, "not found"]:
                    z = '-'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'keine Relevanz'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    pass

            # "keine Relevanz": #8 BAH-E, #29 BDC-ABCZ, #30 BDD-ABCDE
            elif (attr[10] == "BAH" and attr[11] == "E") or (attr[10] == "BDC" and attr[11] in ["A", "B","C", "Z"]) or (
                    attr[10] == "BDD" and attr[11] in ["A", "B", "C", "D", "E"]):
                if attr[15] in ["", None, "not found"]:
                    z = 'PktS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'keine Relevanz'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensauspraegung = ?
                                               WHERE substanz_haltung_bewertung.pk = ? 
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass
                else:
                    z = 'StrS'
                    sql = f"""
                                             UPDATE substanz_haltung_bewertung
                                               SET Schadensart = ?
                                               WHERE substanz_haltung_bewertung.pk = ?;
                                               """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                    except:
                        pass

                    z = 'keine Relevanz'
                    sql = f"""
                                                                     UPDATE substanz_haltung_bewertung
                                                                       SET Schadensauspraegung = ?
                                                                       WHERE substanz_haltung_bewertung.pk = ? 
                                                                       """
                    data = (z, attr[0])
                    try:
                        db.sql(sql,parameters=data)
                        #db.commit()
                        continue
                    except:
                        pass

        try:
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('substanz_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql,parameters=data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db.dbname)
        schema = ''
        table = 'substanz_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        substanz_haltung_bewertung = enums.LAYERBEZ.SK_EINZELSCHAEDEN_HALTUNGEN.value
        vlayer = QgsVectorLayer(uri.uri(), substanz_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(substanz_haltung_bewertung)[0].id())
        except:
            pass


        #QgsProject.instance().addMapLayer(vlayer)
        group = 'Ergebnisse'
        layersRoot = QgsProject.instance().layerTreeRoot()
        QgsProject.instance().addMapLayer(vlayer, False)
        atcGroup = layersRoot.findGroup(group)
        if atcGroup is None:
            atcGroup = layersRoot.addGroup(group)
        atcGroup.addLayer(vlayer)
        logger.debug(f'Ende der Zuordnung von Schadensart und Schadensauspraegung: {datetime.now()}')


    def schadens_ueberlagerung(self):
        #Schadensüberlagerung, Schäden an der gleichen Position entfernen, der schwerste schaden wird behalten
        #bei Streckenschäden werden die Schädenden an den Überlagerungsstellen verkürzt
        #Sonderregeln für Streckenschäden ergänzen Anlage 8-9

        #Überlagerung SOB bei Punkt und Umfangschäden werden SOB nicht überlagert
        #Streckenschäden SOB werden nicht überlagert.
        date = self.date
        db = self.db
        crs = self.crs
        haltung = self.haltung

        #data = db_x

        entf_list=[]

        db1 = self.db
        #curs1 = db1.cursl()

        # db = spatialite_connect(db_x)
        # curs = db.cursor()

        logger.debug(f'Start der Schadensueberlagerung: {datetime.now()}')
        # nach DWA

        try:
            db.sql("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadenslaenge TEXT ;""")
        except:
            pass

        #Streckenschaden A-B

        db.sql("""SELECT 
                s.untersuchhal,
                s.pk,
                s.station,
                s.streckenschaden_lfdnr,
                s.streckenschaden,
                (
                    SELECT t.station
                    FROM substanz_haltung_bewertung t
                    WHERE s.streckenschaden_lfdnr = t.streckenschaden_lfdnr
                      AND s.streckenschaden = 'A'
                    ORDER BY t.untersuchhal ASC
                    LIMIT 1
                ) AS t_wert_a,
                (
                    SELECT t.station
                    FROM substanz_haltung_bewertung t
                    WHERE s.streckenschaden_lfdnr = t.streckenschaden_lfdnr
                      AND t.streckenschaden = 'B'
                    ORDER BY t.untersuchhal ASC
                    LIMIT 1
                ) AS t_wert_b,
                (
                    (
                        SELECT t.station
                        FROM substanz_haltung_bewertung t
                        WHERE s.streckenschaden_lfdnr = t.streckenschaden_lfdnr
                          AND t.streckenschaden = 'B'
                        ORDER BY t.untersuchhal ASC
                        LIMIT 1
                    ) 
                    - s.station
                ) AS summe
            FROM substanz_haltung_bewertung s Where s.streckenschaden = 'A'""")
        db1.commit()

        for attr in db.fetchall():

            x = attr[7]

            sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
            data = (x, attr[1])

            db.sql(sql,parameters=data)

        try:
            db1.commit()
        except:
            pass

        # Streckenschaden A-C

        db.sql("""SELECT 
                s.untersuchhal,
                s.pk,
                s.station,
                s.streckenschaden_lfdnr,
                s.streckenschaden,
                (
                    SELECT t.station
                    FROM substanz_haltung_bewertung t
                    WHERE s.streckenschaden_lfdnr = t.streckenschaden_lfdnr
                      AND s.streckenschaden = 'A'
                    ORDER BY t.untersuchhal ASC
                    LIMIT 1
                ) AS t_wert_a,
                (
                    SELECT t.station
                    FROM substanz_haltung_bewertung t
                    WHERE s.streckenschaden_lfdnr = t.streckenschaden_lfdnr
                      AND t.streckenschaden = 'C'
                    ORDER BY t.untersuchhal ASC
                    LIMIT 1
                ) AS t_wert_b,
                (
                    (
                        SELECT t.station
                        FROM substanz_haltung_bewertung t
                        WHERE s.streckenschaden_lfdnr = t.streckenschaden_lfdnr
                          AND t.streckenschaden = 'C'
                        ORDER BY t.untersuchhal ASC
                        LIMIT 1
                    ) 
                    - s.station
                ) AS summe
            FROM substanz_haltung_bewertung s Where s.streckenschaden = 'A' and summe >0
                """)
        db1.commit()

        for attr in db.fetchall():
            x = attr[7]

            sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
            data = (x, attr[1])

            db.sql(sql, parameters=data)

        try:
            db1.commit()
        except:
            pass


        #Streckenschaden C-C

        db.sql("""SELECT
                    pk, 
                    untersuchhal,
                        streckenschaden_lfdnr,
                        station AS s_station,
                        next_station,
                        next_station - station AS differenz
                    FROM (
                        SELECT 
                        pk,
                    untersuchhal,
                            station,
                            streckenschaden_lfdnr,
                            LEAD(station) OVER (
                                PARTITION BY streckenschaden_lfdnr, untersuchhal
                                ORDER BY untersuchhal ASC
                            ) AS next_station
                        FROM substanz_haltung_bewertung
                        WHERE streckenschaden = 'C'
                    ) sub
                    WHERE next_station IS NOT NULL;


                        """)
        db1.commit()

        for attr in db.fetchall():
            x = attr[5]

            sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
            data = (x, attr[0])

            db.sql(sql, parameters=data)

        try:
            db1.commit()
        except:
            pass


        #Streckenschaden C-B

        db.sql("""
                SELECT 
                    pk,
                    streckenschaden_lfdnr,
                    untersuchhal,
                    MAX(CASE WHEN streckenschaden = 'B' THEN station END) -
                    MAX(CASE WHEN streckenschaden = 'C' THEN station END) AS c_wert
                FROM substanz_haltung_bewertung
                WHERE streckenschaden IN ('B', 'C')
                GROUP BY streckenschaden_lfdnr, untersuchhal
                HAVING 
                    MAX(CASE WHEN streckenschaden = 'B' THEN station END) IS NOT NULL
                    AND MAX(CASE WHEN streckenschaden = 'C' THEN station END) IS NOT NULL;
                                """)
        db1.commit()

        for attr in db.fetchall():
            x = attr[3]

            sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
            data = (x, attr[0])

            db.sql(sql, parameters=data)

        try:
            db1.commit()
        except:
            pass


        if self.datetype == 'Befahrungsdatum':

            sql = """
                                                               SELECT
                                                                   substanz_haltung_bewertung.pk,
                                                                   substanz_haltung_bewertung.untersuchhal,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.schoben,
                                                                   substanz_haltung_bewertung.schunten,
                                                                   substanz_haltung_bewertung.id,
                                                                   substanz_haltung_bewertung.videozaehler,
                                                                   substanz_haltung_bewertung.inspektionslaenge,
                                                                   substanz_haltung_bewertung.station,
                                                                   substanz_haltung_bewertung.timecode,
                                                                   substanz_haltung_bewertung.kuerzel,
                                                                   substanz_haltung_bewertung.charakt1,
                                                                   substanz_haltung_bewertung.charakt2,
                                                                   substanz_haltung_bewertung.quantnr1,
                                                                   substanz_haltung_bewertung.quantnr2,
                                                                   substanz_haltung_bewertung.Schadensart,
                                                                   substanz_haltung_bewertung.Schadensauspraegung,
                                                                   substanz_haltung_bewertung.streckenschaden,
                                                                   substanz_haltung_bewertung.pos_von,
                                                                   substanz_haltung_bewertung.pos_bis,
                                                                   substanz_haltung_bewertung.foto_dateiname,
                                                                   substanz_haltung_bewertung.film_dateiname,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.bw_bs,
                                                                   substanz_haltung_bewertung.Zustandsklasse_D,
                                                                   substanz_haltung_bewertung.Zustandsklasse_S,
                                                                   substanz_haltung_bewertung.Zustandsklasse_B,
                                                                   substanz_haltung_bewertung.Zustandsklasse_ges,
                                                                   substanz_haltung_bewertung.Schadenslaenge,
                                                                   substanz_haltung_bewertung.createdat,
                                                                   haltungen.haltnam,
                                                                   haltungen.material,
                                                                   haltungen.breite,
                                                                   haltungen.createdat,
                                                                   haltungen.profilnam,
                                                                   substanz_haltung_bewertung.untersuchtag
                                                               FROM substanz_haltung_bewertung, haltungen
                                                               WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120
                                                               AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS') 
                                                               AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                           """
        elif self.datetype == 'Importdatum':
            sql = """
                                                               SELECT
                                                                   substanz_haltung_bewertung.pk,
                                                                   substanz_haltung_bewertung.untersuchhal,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.schoben,
                                                                   substanz_haltung_bewertung.schunten,
                                                                   substanz_haltung_bewertung.id,
                                                                   substanz_haltung_bewertung.videozaehler,
                                                                   substanz_haltung_bewertung.inspektionslaenge,
                                                                   substanz_haltung_bewertung.station,
                                                                   substanz_haltung_bewertung.timecode,
                                                                   substanz_haltung_bewertung.kuerzel,
                                                                   substanz_haltung_bewertung.charakt1,
                                                                   substanz_haltung_bewertung.charakt2,
                                                                   substanz_haltung_bewertung.quantnr1,
                                                                   substanz_haltung_bewertung.quantnr2,
                                                                   substanz_haltung_bewertung.Schadensart,
                                                                   substanz_haltung_bewertung.Schadensauspraegung,
                                                                   substanz_haltung_bewertung.streckenschaden,
                                                                   substanz_haltung_bewertung.pos_von,
                                                                   substanz_haltung_bewertung.pos_bis,
                                                                   substanz_haltung_bewertung.foto_dateiname,
                                                                   substanz_haltung_bewertung.film_dateiname,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.bw_bs,
                                                                   substanz_haltung_bewertung.Zustandsklasse_D,
                                                                   substanz_haltung_bewertung.Zustandsklasse_S,
                                                                   substanz_haltung_bewertung.Zustandsklasse_B,
                                                                   substanz_haltung_bewertung.Zustandsklasse_ges,
                                                                   substanz_haltung_bewertung.Schadenslaenge,
                                                                   substanz_haltung_bewertung.createdat,
                                                                   haltungen.haltnam,
                                                                   haltungen.material,
                                                                   haltungen.breite,
                                                                   haltungen.createdat,
                                                                   haltungen.profilnam
                                                               FROM substanz_haltung_bewertung, haltungen
                                                               WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 
                                                               AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS') 
                                                               AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                           """
        else:
            logger.error_code(f"{self.datetype=} ist ungültig")
            raise BaseException

        data = (date,)
        db.sql(sql,parameters=data)

        dictionary = {}
        entf_list = []
        for attr in db.fetchall():

            # schadenslänge ergänzen
            if attr[15] == "PktS":
                sl = 0.3

                sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
                data = (sl, attr[0])

                db.sql(sql,parameters=data)

            elif attr[15] == "UmfS":
                #für Ei-Profile berechnung vom Umfang nach DWA 110!

                if attr[32] in ['Ei', 'Ei (B:H = 2:3)', 'Ei überhöht (B:H=2:3.5)', 'Ei breit (B:H=2:2.5)', 'Ei gedrückt (B:H=2:2)' ]:
                    sl = float((formf(7.93 * attr[32] / 1000/ 2, 5)))

                else:
                    sl = float(formf(attr[32] / 1000 * pi, 5))


                sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
                data = (sl, attr[0])

                db.sql(sql,parameters=data)

            elif attr[15] in ["", "None"]:
                sl = 0

                sql = """UPDATE substanz_haltung_bewertung SET Schadenslaenge = ? WHERE substanz_haltung_bewertung.pk = ?"""
                data = (sl, attr[0])

                db.sql(sql,parameters=data)
            try:
                db.commit()
            except:
                pass

        try:
            db.sql("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Startgewicht REAL ;""")
        except:
            pass

        try:
            db.sql("""ALTER TABLE substanz_haltung_bewertung ADD COLUMN Schadensgewicht REAL ;""")
        except:
            pass


        if haltung == True:
            if self.datetype == 'Befahrungsdatum':
                sql = """
                                                                           SELECT
                                                                               substanz_haltung_bewertung.pk,
                                                                               substanz_haltung_bewertung.untersuchhal,
                                                                               NULL,
                                                                               substanz_haltung_bewertung.schoben,
                                                                               substanz_haltung_bewertung.schunten,
                                                                               substanz_haltung_bewertung.id,
                                                                               substanz_haltung_bewertung.videozaehler,
                                                                               substanz_haltung_bewertung.inspektionslaenge,
                                                                               substanz_haltung_bewertung.station,
                                                                               substanz_haltung_bewertung.timecode,
                                                                               substanz_haltung_bewertung.kuerzel,
                                                                               substanz_haltung_bewertung.charakt1,
                                                                               substanz_haltung_bewertung.charakt2,
                                                                               substanz_haltung_bewertung.quantnr1,
                                                                               substanz_haltung_bewertung.quantnr2,
                                                                               substanz_haltung_bewertung.Schadensart,
                                                                               substanz_haltung_bewertung.Schadensauspraegung,
                                                                               substanz_haltung_bewertung.streckenschaden,
                                                                               substanz_haltung_bewertung.pos_von,
                                                                               substanz_haltung_bewertung.pos_bis,
                                                                               substanz_haltung_bewertung.foto_dateiname,
                                                                               substanz_haltung_bewertung.film_dateiname,
                                                                               NULL,
                                                                               substanz_haltung_bewertung.bw_bs,
                                                                               substanz_haltung_bewertung.Zustandsklasse_D,
                                                                               substanz_haltung_bewertung.Zustandsklasse_S,
                                                                               substanz_haltung_bewertung.Zustandsklasse_B,
                                                                               substanz_haltung_bewertung.Zustandsklasse_ges,
                                                                               substanz_haltung_bewertung.Schadenslaenge,
                                                                               substanz_haltung_bewertung.createdat,
                                                                               haltungen.haltnam,
                                                                               haltungen.material,
                                                                               haltungen.hoehe,
                                                                               haltungen.createdat,
                                                                               substanz_haltung_bewertung.untersuchtag
                                                                           FROM substanz_haltung_bewertung, haltungen
                                                                           WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120
                                                                           AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS' OR (substanz_haltung_bewertung.Schadensart = 'StrS' AND streckenschaden ='A')OR (substanz_haltung_bewertung.Schadensart = 'StrS' AND streckenschaden ='C')) 
                                                                           AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS' OR substanz_haltung_bewertung.Schadensauspraegung = 'DdS' OR substanz_haltung_bewertung.Schadensauspraegung = 'SoB')
                                                                           AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                                       """

            elif self.datetype == 'Importdatum':
                sql = """
                                                                           SELECT
                                                                               substanz_haltung_bewertung.pk,
                                                                               substanz_haltung_bewertung.untersuchhal,
                                                                               NULL,
                                                                               substanz_haltung_bewertung.schoben,
                                                                               substanz_haltung_bewertung.schunten,
                                                                               substanz_haltung_bewertung.id,
                                                                               substanz_haltung_bewertung.videozaehler,
                                                                               substanz_haltung_bewertung.inspektionslaenge,
                                                                               substanz_haltung_bewertung.station,
                                                                               substanz_haltung_bewertung.timecode,
                                                                               substanz_haltung_bewertung.kuerzel,
                                                                               substanz_haltung_bewertung.charakt1,
                                                                               substanz_haltung_bewertung.charakt2,
                                                                               substanz_haltung_bewertung.quantnr1,
                                                                               substanz_haltung_bewertung.quantnr2,
                                                                               substanz_haltung_bewertung.Schadensart,
                                                                               substanz_haltung_bewertung.Schadensauspraegung,
                                                                               substanz_haltung_bewertung.streckenschaden,
                                                                               substanz_haltung_bewertung.pos_von,
                                                                               substanz_haltung_bewertung.pos_bis,
                                                                               substanz_haltung_bewertung.foto_dateiname,
                                                                               substanz_haltung_bewertung.film_dateiname,
                                                                               NULL,
                                                                               substanz_haltung_bewertung.bw_bs,
                                                                               substanz_haltung_bewertung.Zustandsklasse_D,
                                                                               substanz_haltung_bewertung.Zustandsklasse_S,
                                                                               substanz_haltung_bewertung.Zustandsklasse_B,
                                                                               substanz_haltung_bewertung.Zustandsklasse_ges,
                                                                               substanz_haltung_bewertung.Schadenslaenge,
                                                                               substanz_haltung_bewertung.createdat,
                                                                               haltungen.haltnam,
                                                                               haltungen.material,
                                                                               haltungen.hoehe,
                                                                               haltungen.createdat
                                                                           FROM substanz_haltung_bewertung, haltungen
                                                                           WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120
                                                                           AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS' OR (substanz_haltung_bewertung.Schadensart = 'StrS' AND streckenschaden ='A') OR (substanz_haltung_bewertung.Schadensart = 'StrS' AND streckenschaden ='C')) 
                                                                           AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS' OR substanz_haltung_bewertung.Schadensauspraegung = 'DdS' OR substanz_haltung_bewertung.Schadensauspraegung = 'SoB')
                                                                           AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                                       """
            else:
                logger.error_code(f"{self.datetype=} ist ungültig")
                raise BaseException

            data = (date,)
            db.sql(sql,parameters=data)

            for attr in db.fetchall():

                sl = attr[28]

                sg = 0
                kg = 0
                #stg = 0

                # Klassengewichte
                if int(attr[27]) == 0:
                    kg = 1.0
                elif int(attr[27]) == 1:
                    kg = 0.8
                elif int(attr[27]) == 2:
                    kg = 0.25
                elif int(attr[27]) == 3:
                    kg = 0.15
                elif int(attr[27]) == 4:
                    kg = 0.05
                elif int(attr[27]) == 5:
                    kg = 0.0

                # startgewicht:
                if attr[15] == 'PktS' and attr[16] in ['OfS', 'DdS', 'SoB']:
                    stg = 8

                elif attr[15] == 'UmfS' and attr[16] in ['OfS', 'DdS', 'SoB']:
                    stg = 3

                elif attr[15] == 'StrS' and attr[16] in ['OfS', 'DdS', 'SoB']:
                    stg = 1

                # schadensgewicht:

                if sl not in ("", None, "not found"):

                    sg = float(sl) * stg * kg

                    # schadensgewicht für streckenschäden seperat ermitteln
                    if attr[15] == 'StrS':
                        if sg < (8 * kg * 0.3):

                            stg_neu = (8 * kg * 0.3) / sg
                            sg = float(sl) * stg_neu * kg
                            stg = stg_neu

                sql = """UPDATE substanz_haltung_bewertung SET Startgewicht = ? WHERE substanz_haltung_bewertung.pk = ?"""
                data = (round_up(stg, 2), attr[0])

                db.sql(sql,parameters=data)

                # sg in tabelle schreiben

                sql = """UPDATE substanz_haltung_bewertung SET Schadensgewicht = ? WHERE substanz_haltung_bewertung.pk = ?"""
                data = (round_up(sg, 2), attr[0])

                db.sql(sql,parameters=data)


                db.commit()

            # Streckenschadenüberlagerung so umprogrammieren, dass die Schäden aufgeteilt werden in die C-Bereiche
            #und dann überlagert werden mit dem jeweiligen ZK-Wert und vorher immer schauen ob der Streckenschaden
            #schwerer ist als ein Punktschaden
            # Schadensüberlagerung Str-Ofs:
            if self.datetype == 'Befahrungsdatum':
                sql = """
                           SELECT
                               substanz_haltung_bewertung.pk,
                               substanz_haltung_bewertung.untersuchhal,
                               NULL,
                               substanz_haltung_bewertung.schoben,
                               substanz_haltung_bewertung.schunten,
                               substanz_haltung_bewertung.id,
                               substanz_haltung_bewertung.videozaehler,
                               substanz_haltung_bewertung.inspektionslaenge,
                               substanz_haltung_bewertung.station,
                               substanz_haltung_bewertung.timecode,
                               substanz_haltung_bewertung.kuerzel,
                               substanz_haltung_bewertung.charakt1,
                               substanz_haltung_bewertung.charakt2,
                               substanz_haltung_bewertung.quantnr1,
                               substanz_haltung_bewertung.quantnr2,
                               substanz_haltung_bewertung.Schadensart,
                               substanz_haltung_bewertung.Schadensauspraegung,
                               substanz_haltung_bewertung.streckenschaden,
                               substanz_haltung_bewertung.pos_von,
                               substanz_haltung_bewertung.pos_bis,
                               substanz_haltung_bewertung.foto_dateiname,
                               substanz_haltung_bewertung.film_dateiname,
                               NULL,
                               substanz_haltung_bewertung.bw_bs,
                               substanz_haltung_bewertung.Zustandsklasse_D,
                               substanz_haltung_bewertung.Zustandsklasse_S,
                               substanz_haltung_bewertung.Zustandsklasse_B,
                               substanz_haltung_bewertung.Zustandsklasse_ges,
                               substanz_haltung_bewertung.Schadenslaenge,
                               substanz_haltung_bewertung.Startgewicht,
                               substanz_haltung_bewertung.createdat,
                               haltungen.haltnam,
                               haltungen.material,
                               haltungen.hoehe,
                               haltungen.createdat,
                               substanz_haltung_bewertung.untersuchtag
                           FROM substanz_haltung_bewertung, haltungen
                           WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120
                           AND (substanz_haltung_bewertung.Schadensart = 'StrS' AND (substanz_haltung_bewertung.streckenschaden ='A' or substanz_haltung_bewertung.streckenschaden ='C')) 
                            AND substanz_haltung_bewertung.Schadenslaenge is not NULL
                            AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS')
                           AND Zustandsklasse_ges IN (0,1,2,3,4)
                       """
            elif self.datetype == 'Importdatum':
                sql = """
                           SELECT
                               substanz_haltung_bewertung.pk,
                               substanz_haltung_bewertung.untersuchhal,
                               NULL,
                               substanz_haltung_bewertung.schoben,
                               substanz_haltung_bewertung.schunten,
                               substanz_haltung_bewertung.id,
                               substanz_haltung_bewertung.videozaehler,
                               substanz_haltung_bewertung.inspektionslaenge,
                               substanz_haltung_bewertung.station,
                               substanz_haltung_bewertung.timecode,
                               substanz_haltung_bewertung.kuerzel,
                               substanz_haltung_bewertung.charakt1,
                               substanz_haltung_bewertung.charakt2,
                               substanz_haltung_bewertung.quantnr1,
                               substanz_haltung_bewertung.quantnr2,
                               substanz_haltung_bewertung.Schadensart,
                               substanz_haltung_bewertung.Schadensauspraegung,
                               substanz_haltung_bewertung.streckenschaden,
                               substanz_haltung_bewertung.pos_von,
                               substanz_haltung_bewertung.pos_bis,
                               substanz_haltung_bewertung.foto_dateiname,
                               substanz_haltung_bewertung.film_dateiname,
                               NULL,
                               substanz_haltung_bewertung.bw_bs,
                               substanz_haltung_bewertung.Zustandsklasse_D,
                               substanz_haltung_bewertung.Zustandsklasse_S,
                               substanz_haltung_bewertung.Zustandsklasse_B,
                               substanz_haltung_bewertung.Zustandsklasse_ges,
                               substanz_haltung_bewertung.Schadenslaenge,
                               substanz_haltung_bewertung.Startgewicht,
                               substanz_haltung_bewertung.createdat,
                               haltungen.haltnam,
                               haltungen.material,
                               haltungen.hoehe,
                               haltungen.createdat
                           FROM substanz_haltung_bewertung, haltungen
                           WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 
                           AND (substanz_haltung_bewertung.Schadensart = 'StrS' AND (substanz_haltung_bewertung.streckenschaden ='A' or substanz_haltung_bewertung.streckenschaden ='C')) 
                            AND substanz_haltung_bewertung.Schadenslaenge is not NULL
                            AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS')
                           AND Zustandsklasse_ges IN (0,1,2,3,4)
                       """
            else:
                logger.error_code(f"{self.datetype=} ist ungültig")
                raise BaseException

            data = (date,)
            db.sql(sql,parameters=data)

            dictionary = {}
            entf_list = []
            dat = db.fetchall()
            for attr in dat:

                if attr[1] in dictionary:
                    continue
                new_list = []
                for x in dat:
                    if x[1] == attr[1]:
                        new_list.append(x)
                dictionary[attr[1]] = new_list

            for values in dictionary.values():
                new_items = []
                vergl = []

                def check_overlap(start1, length1, start2, length2):
                    end1 = start1 + length1
                    end2 = start2 + length2
                    return (start1 < end2 and end1 > start2)

                overlapping_indices = set()

                for i in range(len(values)):
                    start1 = values[i][8]
                    length1 = float(values[i][28])
                    for j in range(i + 1, len(values)):
                        start2 = values[j][8]
                        length2 = float(values[j][28])
                        if check_overlap(start1, length1, start2, length2):
                            overlapping_indices.add(i)
                            overlapping_indices.add(j)

                vergl = [values[index] for index in overlapping_indices]

                zustand = []
                for i in vergl:
                    # testen, ob die streckenschaden sich überlagern
                    # startgewicht:
                    stg = 1
                    # Klassengewichte
                    if int(i[27]) == 0:
                        kg = 1.0
                    elif int(i[27]) == 1:
                        kg = 0.8
                    elif int(i[27]) == 2:
                        kg = 0.25
                    elif int(i[27]) == 3:
                        kg = 0.15
                    elif int(i[27]) == 4:
                        kg = 0.05
                    elif int(i[27]) == 5:
                        kg = 0.0

                    sl = float(i[28])

                    # schadensgewicht:
                    if sl not in ("", None, "not found"):
                        kg_stg = kg * float(i[29])

                        zustand.append(kg_stg)

                if len(zustand) > 0:
                    x = 0
                    z_min = zustand.index(max(zustand))
                    for _ in zustand:
                        if x != z_min:
                            entf = x

                            start1 = vergl[z_min][8]
                            length1 = float(vergl[z_min][28])

                            start2 = vergl[entf][8]
                            length2 = float(vergl[entf][28])
                            if check_overlap(start1, length1, start2, length1):
                                end1 = start1 + length1
                                end2 = start2 + length2
                                # überlappungslänge berechnen
                                ueberlappungs_start = max(start1, start2)
                                ueberlappungs_ende = min(end1, end2)

                                # Wenn der Startpunkt der Überlappung kleiner als der Endpunkt ist, gibt es eine Überlappung

                                # schadenslänge reduzieren um den wert der überlagerung!
                                if ueberlappungs_start < ueberlappungs_ende:
                                    ueberlappung = ueberlappungs_ende - ueberlappungs_start
                                else:
                                    ueberlappung = 0

                                len_neu = length2 - ueberlappung

                                a = vergl[entf][0]

                                sql = 'UPDATE substanz_haltung_bewertung SET schadenslaenge = ? WHERE pk=?'
                                data = (len_neu, a)
                                db.sql(sql,parameters=data)

                        else:
                            # immer den längeren schaden behalten und den kürzen dann kürzen!

                            zielwert = zustand[z_min]

                            other_indices = [i for i, v in enumerate(zustand) if v == zielwert and i != z_min]

                            if other_indices:  # Überprüfen, ob ein anderer Index gefunden wurde
                                entf = other_indices[0]  # Nehme den ersten passenden Index

                                # Extrahiere Werte für z_min
                                start1 = vergl[z_min][8]
                                length1 = float(vergl[z_min][28])

                                # Extrahiere Werte für entf
                                start2 = vergl[entf][8]
                                length2 = float(vergl[entf][28])

                                if check_overlap(start1, length1, start2, length1):
                                    end1 = start1 + length1
                                    end2 = start2 + length2
                                    # überlappungslänge berechnen
                                    ueberlappungs_start = max(start1, start2)
                                    ueberlappungs_ende = min(end1, end2)

                                    # Wenn der Startpunkt der Überlappung kleiner als der Endpunkt ist, gibt es eine Überlappung

                                    # schadenslänge reduzieren um den wert der überlagerung!
                                    if ueberlappungs_start < ueberlappungs_ende:
                                        ueberlappung = ueberlappungs_ende - ueberlappungs_start
                                    else:
                                        ueberlappung = 0

                                    len_neu = length2 - ueberlappung

                                    a = vergl[entf][0]

                                    sql = 'UPDATE substanz_haltung_bewertung SET schadenslaenge = ? WHERE pk=?'
                                    data = (len_neu, a)
                                    db.sql(sql,parameters=data)

                        x += 1

            db1.commit()

            # sql = """
            #                        SELECT
            #                            substanz_haltung_bewertung.pk,
            #                            substanz_haltung_bewertung.untersuchhal,
            #                            NULL,
            #                            substanz_haltung_bewertung.schoben,
            #                            substanz_haltung_bewertung.schunten,
            #                            substanz_haltung_bewertung.id,
            #                            substanz_haltung_bewertung.videozaehler,
            #                            substanz_haltung_bewertung.inspektionslaenge,
            #                            substanz_haltung_bewertung.station,
            #                            substanz_haltung_bewertung.timecode,
            #                            substanz_haltung_bewertung.kuerzel,
            #                            substanz_haltung_bewertung.charakt1,
            #                            substanz_haltung_bewertung.charakt2,
            #                            substanz_haltung_bewertung.quantnr1,
            #                            substanz_haltung_bewertung.quantnr2,
            #                            substanz_haltung_bewertung.Schadensart,
            #                            substanz_haltung_bewertung.Schadensauspraegung,
            #                            substanz_haltung_bewertung.streckenschaden,
            #                            substanz_haltung_bewertung.pos_von,
            #                            substanz_haltung_bewertung.pos_bis,
            #                            substanz_haltung_bewertung.foto_dateiname,
            #                            substanz_haltung_bewertung.film_dateiname,
            #                            NULL,
            #                            substanz_haltung_bewertung.bw_bs,
            #                            substanz_haltung_bewertung.Zustandsklasse_D,
            #                            substanz_haltung_bewertung.Zustandsklasse_S,
            #                            substanz_haltung_bewertung.Zustandsklasse_B,
            #                            substanz_haltung_bewertung.Zustandsklasse_ges,
            #                            substanz_haltung_bewertung.Schadenslaenge,
            #                            substanz_haltung_bewertung.Startgewicht,
            #                            substanz_haltung_bewertung.createdat,
            #                            haltungen.haltnam,
            #                            haltungen.material,
            #                            haltungen.hoehe,
            #                            haltungen.createdat
            #                        FROM substanz_haltung_bewertung, haltungen
            #                        WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120
            #                        AND (substanz_haltung_bewertung.Schadensart = 'StrS' AND streckenschaden ='A')
            #                        AND (substanz_haltung_bewertung.Schadensauspraegung = 'SoB')
            #                        AND Zustandsklasse_ges IN (0,1,2,3,4)
            #                    """
            # data = (date,)
            #
            # db.sql(sql,parameters=data)
            #
            # dictionary = {}
            # entf_list = []
            # dat = curs.fetchall()
            # for attr in dat:
            #
            #     if attr[1] in dictionary:
            #         continue
            #     new_list = []
            #     for x in dat:
            #         if x[1] == attr[1]:
            #             new_list.append(x)
            #     dictionary[attr[1]] = new_list
            #
            # for values in dictionary.values():
            #     new_items = []
            #     vergl = []
            #
            #     def check_overlap(start1, length1, start2, length2):
            #         end1 = start1 + length1
            #         end2 = start2 + length2
            #         return (start1 < end2 and end1 > start2)
            #
            #     overlapping_indices = set()
            #
            #     for i in range(len(values)):
            #         start1 = values[i][8]
            #         length1 = float(values[i][28])
            #         for j in range(i + 1, len(values)):
            #             start2 = values[j][8]
            #             length2 = float(values[j][28])
            #             if check_overlap(start1, length1, start2, length2):
            #                 overlapping_indices.add(i)
            #                 overlapping_indices.add(j)
            #
            #     vergl = [values[index] for index in overlapping_indices]
            #
            #     zustand = []
            #     for i in vergl:
            #         # testen, ob die streckenschaden sich überlagern
            #         # startgewicht:
            #         stg = 1
            #         # Klassengewichte
            #         if int(i[27]) == 0:
            #             kg = 1.0
            #         elif int(i[27]) == 1:
            #             kg = 0.8
            #         elif int(i[27]) == 2:
            #             kg = 0.25
            #         elif int(i[27]) == 3:
            #             kg = 0.15
            #         elif int(i[27]) == 4:
            #             kg = 0.05
            #         elif int(i[27]) == 5:
            #             kg = 0.0
            #
            #         sl = float(i[28])
            #
            #         # schadensgewicht:
            #         if sl not in ("", None, "not found"):
            #             kg_stg = kg * float(i[29])
            #
            #             zustand.append(kg_stg)
            #
            #     if len(zustand) > 0:
            #         x = 0
            #         z_min = zustand.index(max(zustand))
            #         for _ in zustand:
            #             if x != z_min:
            #                 entf = x
            #
            #                 start1 = vergl[z_min][8]
            #                 length1 = float(vergl[z_min][28])
            #
            #                 start2 = vergl[entf][8]
            #                 length2 = float(vergl[entf][28])
            #                 if check_overlap(start1, length1, start2, length1):
            #                     end1 = start1 + length1
            #                     end2 = start2 + length2
            #                     # überlappungslänge berechnen
            #                     ueberlappungs_start = max(start1, start2)
            #                     ueberlappungs_ende = min(end1, end2)
            #
            #                     # Wenn der Startpunkt der Überlappung kleiner als der Endpunkt ist, gibt es eine Überlappung
            #
            #                     # schadenslänge reduzieren um den wert der überlagerung!
            #                     if ueberlappungs_start < ueberlappungs_ende:
            #                         ueberlappung = ueberlappungs_ende - ueberlappungs_start
            #                     else:
            #                         ueberlappung = 0
            #
            #                     len_neu = length2 - ueberlappung
            #
            #                     a = vergl[entf][0]
            #
            #                     sql = 'UPDATE substanz_haltung_bewertung SET schadenslaenge = ? WHERE pk=?'
            #                     data = (len_neu, a)
            #                     db.sql(sql,parameters=data)
            #
            #             else:
            #                 # immer den längeren schaden behalten und den kürzen dann kürzen!
            #
            #                 zielwert = zustand[z_min]
            #
            #                 other_indices = [i for i, v in enumerate(zustand) if v == zielwert and i != z_min]
            #
            #                 if other_indices:  # Überprüfen, ob ein anderer Index gefunden wurde
            #                     entf = other_indices[0]  # Nehme den ersten passenden Index
            #
            #                     # Extrahiere Werte für z_min
            #                     start1 = vergl[z_min][8]
            #                     length1 = float(vergl[z_min][28])
            #
            #                     # Extrahiere Werte für entf
            #                     start2 = vergl[entf][8]
            #                     length2 = float(vergl[entf][28])
            #
            #                     if check_overlap(start1, length1, start2, length1):
            #                         end1 = start1 + length1
            #                         end2 = start2 + length2
            #                         # überlappungslänge berechnen
            #                         ueberlappungs_start = max(start1, start2)
            #                         ueberlappungs_ende = min(end1, end2)
            #
            #                         # Wenn der Startpunkt der Überlappung kleiner als der Endpunkt ist, gibt es eine Überlappung
            #
            #                         # schadenslänge reduzieren um den wert der überlagerung!
            #                         if ueberlappungs_start < ueberlappungs_ende:
            #                             ueberlappung = ueberlappungs_ende - ueberlappungs_start
            #                         else:
            #                             ueberlappung = 0
            #
            #                         len_neu = length2 - ueberlappung
            #
            #                         a = vergl[entf][0]
            #
            #                         sql = 'UPDATE substanz_haltung_bewertung SET schadenslaenge = ? WHERE pk=?'
            #                         data = (len_neu, a)
            #                         db.sql(sql,parameters=data)
            #
            #             x += 1
            #
            # db1.commit()

            if self.datetype == 'Befahrungsdatum':
                sql = """
                                       SELECT
                                           substanz_haltung_bewertung.pk,
                                           substanz_haltung_bewertung.untersuchhal,
                                           NULL,
                                           substanz_haltung_bewertung.schoben,
                                           substanz_haltung_bewertung.schunten,
                                           substanz_haltung_bewertung.id,
                                           substanz_haltung_bewertung.videozaehler,
                                           substanz_haltung_bewertung.inspektionslaenge,
                                           substanz_haltung_bewertung.station,
                                           substanz_haltung_bewertung.timecode,
                                           substanz_haltung_bewertung.kuerzel,
                                           substanz_haltung_bewertung.charakt1,
                                           substanz_haltung_bewertung.charakt2,
                                           substanz_haltung_bewertung.quantnr1,
                                           substanz_haltung_bewertung.quantnr2,
                                           substanz_haltung_bewertung.Schadensart,
                                           substanz_haltung_bewertung.Schadensauspraegung,
                                           substanz_haltung_bewertung.streckenschaden,
                                           substanz_haltung_bewertung.pos_von,
                                           substanz_haltung_bewertung.pos_bis,
                                           substanz_haltung_bewertung.foto_dateiname,
                                           substanz_haltung_bewertung.film_dateiname,
                                           NULL,
                                           substanz_haltung_bewertung.bw_bs,
                                           substanz_haltung_bewertung.Zustandsklasse_D,
                                           substanz_haltung_bewertung.Zustandsklasse_S,
                                           substanz_haltung_bewertung.Zustandsklasse_B,
                                           substanz_haltung_bewertung.Zustandsklasse_ges,
                                           substanz_haltung_bewertung.Schadenslaenge,
                                           substanz_haltung_bewertung.Startgewicht,
                                           substanz_haltung_bewertung.createdat,
                                           haltungen.haltnam,
                                           haltungen.material,
                                           haltungen.hoehe,
                                           haltungen.createdat,
                                           substanz_haltung_bewertung.untersuchtag
                                       FROM substanz_haltung_bewertung, haltungen
                                       WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120
                                       AND (substanz_haltung_bewertung.Schadensart = 'StrS' AND (substanz_haltung_bewertung.streckenschaden ='A' or substanz_haltung_bewertung.streckenschaden ='C')) 
						   AND substanz_haltung_bewertung.Schadenslaenge is not NULL 
                                       AND (substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                                       AND Zustandsklasse_ges IN (0,1,2,3,4)
                                   """
            elif self.datetype == 'Importdatum':
                sql = """
                                       SELECT
                                           substanz_haltung_bewertung.pk,
                                           substanz_haltung_bewertung.untersuchhal,
                                           NULL,
                                           substanz_haltung_bewertung.schoben,
                                           substanz_haltung_bewertung.schunten,
                                           substanz_haltung_bewertung.id,
                                           substanz_haltung_bewertung.videozaehler,
                                           substanz_haltung_bewertung.inspektionslaenge,
                                           substanz_haltung_bewertung.station,
                                           substanz_haltung_bewertung.timecode,
                                           substanz_haltung_bewertung.kuerzel,
                                           substanz_haltung_bewertung.charakt1,
                                           substanz_haltung_bewertung.charakt2,
                                           substanz_haltung_bewertung.quantnr1,
                                           substanz_haltung_bewertung.quantnr2,
                                           substanz_haltung_bewertung.Schadensart,
                                           substanz_haltung_bewertung.Schadensauspraegung,
                                           substanz_haltung_bewertung.streckenschaden,
                                           substanz_haltung_bewertung.pos_von,
                                           substanz_haltung_bewertung.pos_bis,
                                           substanz_haltung_bewertung.foto_dateiname,
                                           substanz_haltung_bewertung.film_dateiname,
                                           NULL,
                                           substanz_haltung_bewertung.bw_bs,
                                           substanz_haltung_bewertung.Zustandsklasse_D,
                                           substanz_haltung_bewertung.Zustandsklasse_S,
                                           substanz_haltung_bewertung.Zustandsklasse_B,
                                           substanz_haltung_bewertung.Zustandsklasse_ges,
                                           substanz_haltung_bewertung.Schadenslaenge,
                                           substanz_haltung_bewertung.Startgewicht,
                                           substanz_haltung_bewertung.createdat,
                                           haltungen.haltnam,
                                           haltungen.material,
                                           haltungen.hoehe,
                                           haltungen.createdat
                                       FROM substanz_haltung_bewertung, haltungen
                                       WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 
                                       AND (substanz_haltung_bewertung.Schadensart = 'StrS' AND (streckenschaden ='A' or streckenschaden ='C')) 
						   AND substanz_haltung_bewertung.Schadenslaenge is not NULL
                                       AND (substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                                       AND Zustandsklasse_ges IN (0,1,2,3,4)
                                   """
            else:
                logger.error_code(f"{self.datetype=} ist ungültig")
                raise BaseException

            data = (date,)
            db.sql(sql,parameters=data)

            dictionary = {}
            entf_list = []
            dat = db.fetchall()
            for attr in dat:

                if attr[1] in dictionary:
                    continue
                new_list = []
                for x in dat:
                    if x[1] == attr[1]:
                        new_list.append(x)
                dictionary[attr[1]] = new_list

            for values in dictionary.values():
                new_items = []
                vergl = []

                def check_overlap(start1, length1, start2, length2):
                    end1 = start1 + length1
                    end2 = start2 + length2
                    return (start1 < end2 and end1 > start2)

                overlapping_indices = set()

                for i in range(len(values)):
                    start1 = values[i][8]
                    length1 = float(values[i][28])
                    for j in range(i + 1, len(values)):
                        start2 = values[j][8]
                        length2 = float(values[j][28])
                        if check_overlap(start1, length1, start2, length2):
                            overlapping_indices.add(i)
                            overlapping_indices.add(j)

                vergl = [values[index] for index in overlapping_indices]


                zustand = []
                for i in vergl:
                    # testen, ob die streckenschaden sich überlagern
                    # startgewicht:
                    stg = 1
                    # Klassengewichte
                    if int(i[27]) == 0:
                        kg = 1.0
                    elif int(i[27]) == 1:
                        kg = 0.8
                    elif int(i[27]) == 2:
                        kg = 0.25
                    elif int(i[27]) == 3:
                        kg = 0.15
                    elif int(i[27]) == 4:
                        kg = 0.05
                    elif int(i[27]) == 5:
                        kg = 0.0

                    sl = float(i[28])

                    # schadensgewicht:
                    if sl not in ("", None, "not found"):
                        kg_stg = kg * float(i[29])

                        zustand.append(kg_stg)


                if len(zustand) > 0:
                    x = 0
                    z_min = zustand.index(max(zustand))
                    for _ in zustand:
                        if x != z_min:
                            entf = x

                            start1 = vergl[z_min][8]
                            length1 = float(vergl[z_min][28])

                            start2 = vergl[entf][8]
                            length2 = float(vergl[entf][28])
                            if check_overlap(start1, length1, start2, length1):
                                end1 = start1 + length1
                                end2 = start2 + length2
                                # überlappungslänge berechnen
                                ueberlappungs_start = max(start1, start2)
                                ueberlappungs_ende = min(end1, end2)

                                # Wenn der Startpunkt der Überlappung kleiner als der Endpunkt ist, gibt es eine Überlappung

                                # schadenslänge reduzieren um den wert der überlagerung!
                                if ueberlappungs_start < ueberlappungs_ende:
                                    ueberlappung = ueberlappungs_ende - ueberlappungs_start
                                else:
                                    ueberlappung = 0

                                len_neu = length2 - ueberlappung

                                a = vergl[entf][0]

                                sql = 'UPDATE substanz_haltung_bewertung SET schadenslaenge = ? WHERE pk=?'
                                data = (len_neu, a)
                                db.sql(sql,parameters=data)

                        else:
                            # immer den längeren schaden behalten und den kürzen dann kürzen!

                            zielwert = zustand[z_min]

                            other_indices = [i for i, v in enumerate(zustand) if v == zielwert and i != z_min]

                            if other_indices:  # Überprüfen, ob ein anderer Index gefunden wurde
                                entf = other_indices[0]  # Nehme den ersten passenden Index

                                # Extrahiere Werte für z_min
                                start1 = vergl[z_min][8]
                                length1 = float(vergl[z_min][28])

                                # Extrahiere Werte für entf
                                start2 = vergl[entf][8]
                                length2 = float(vergl[entf][28])

                                if check_overlap(start1, length1, start2, length1):
                                    end1 = start1 + length1
                                    end2 = start2 + length2
                                    # überlappungslänge berechnen
                                    ueberlappungs_start = max(start1, start2)
                                    ueberlappungs_ende = min(end1, end2)

                                    # Wenn der Startpunkt der Überlappung kleiner als der Endpunkt ist, gibt es eine Überlappung

                                    # schadenslänge reduzieren um den wert der überlagerung!
                                    if ueberlappungs_start < ueberlappungs_ende:
                                        ueberlappung = ueberlappungs_ende - ueberlappungs_start
                                    else:
                                        ueberlappung = 0

                                    len_neu = length2 - ueberlappung

                                    a = vergl[entf][0]

                                    sql = 'UPDATE substanz_haltung_bewertung SET schadenslaenge = ? WHERE pk=?'
                                    data = (len_neu, a)
                                    db.sql(sql,parameters=data)

                        x += 1

            db1.commit()

            if self.datetype == 'Befahrungsdatum':
                sql = """
                                           SELECT
                                               substanz_haltung_bewertung.pk,
                                               substanz_haltung_bewertung.untersuchhal,
                                               NULL,
                                               substanz_haltung_bewertung.schoben,
                                               substanz_haltung_bewertung.schunten,
                                               substanz_haltung_bewertung.id,
                                               substanz_haltung_bewertung.videozaehler,
                                               substanz_haltung_bewertung.inspektionslaenge,
                                               substanz_haltung_bewertung.station,
                                               substanz_haltung_bewertung.timecode,
                                               substanz_haltung_bewertung.kuerzel,
                                               substanz_haltung_bewertung.charakt1,
                                               substanz_haltung_bewertung.charakt2,
                                               substanz_haltung_bewertung.quantnr1,
                                               substanz_haltung_bewertung.quantnr2,
                                               substanz_haltung_bewertung.Schadensart,
                                               substanz_haltung_bewertung.Schadensauspraegung,
                                               substanz_haltung_bewertung.streckenschaden,
                                               substanz_haltung_bewertung.pos_von,
                                               substanz_haltung_bewertung.pos_bis,
                                               substanz_haltung_bewertung.foto_dateiname,
                                               substanz_haltung_bewertung.film_dateiname,
                                               NULL,
                                               substanz_haltung_bewertung.bw_bs,
                                               substanz_haltung_bewertung.Zustandsklasse_D,
                                               substanz_haltung_bewertung.Zustandsklasse_S,
                                               substanz_haltung_bewertung.Zustandsklasse_B,
                                               substanz_haltung_bewertung.Zustandsklasse_ges,
                                               substanz_haltung_bewertung.Schadenslaenge,
                                               substanz_haltung_bewertung.createdat,
                                               haltungen.haltnam,
                                               haltungen.material,
                                               haltungen.hoehe,
                                               haltungen.createdat,
                                               substanz_haltung_bewertung.untersuchtag
                                           FROM substanz_haltung_bewertung, haltungen
                                           WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120 
                                           AND (substanz_haltung_bewertung.Schadensart = 'PktS') 
                                           AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS')
                                           AND Zustandsklasse_ges IN (0,1,2,3,4)
                                       """
            elif self.datetype == 'Importdatum':
                sql = """
                                           SELECT
                                               substanz_haltung_bewertung.pk,
                                               substanz_haltung_bewertung.untersuchhal,
                                               NULL,
                                               substanz_haltung_bewertung.schoben,
                                               substanz_haltung_bewertung.schunten,
                                               substanz_haltung_bewertung.id,
                                               substanz_haltung_bewertung.videozaehler,
                                               substanz_haltung_bewertung.inspektionslaenge,
                                               substanz_haltung_bewertung.station,
                                               substanz_haltung_bewertung.timecode,
                                               substanz_haltung_bewertung.kuerzel,
                                               substanz_haltung_bewertung.charakt1,
                                               substanz_haltung_bewertung.charakt2,
                                               substanz_haltung_bewertung.quantnr1,
                                               substanz_haltung_bewertung.quantnr2,
                                               substanz_haltung_bewertung.Schadensart,
                                               substanz_haltung_bewertung.Schadensauspraegung,
                                               substanz_haltung_bewertung.streckenschaden,
                                               substanz_haltung_bewertung.pos_von,
                                               substanz_haltung_bewertung.pos_bis,
                                               substanz_haltung_bewertung.foto_dateiname,
                                               substanz_haltung_bewertung.film_dateiname,
                                               NULL,
                                               substanz_haltung_bewertung.bw_bs,
                                               substanz_haltung_bewertung.Zustandsklasse_D,
                                               substanz_haltung_bewertung.Zustandsklasse_S,
                                               substanz_haltung_bewertung.Zustandsklasse_B,
                                               substanz_haltung_bewertung.Zustandsklasse_ges,
                                               substanz_haltung_bewertung.Schadenslaenge,
                                               substanz_haltung_bewertung.createdat,
                                               haltungen.haltnam,
                                               haltungen.material,
                                               haltungen.hoehe,
                                               haltungen.createdat
                                           FROM substanz_haltung_bewertung, haltungen
                                           WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120
                                           AND (substanz_haltung_bewertung.Schadensart = 'PktS') 
                                           AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS')
                                           AND Zustandsklasse_ges IN (0,1,2,3,4)
                                       """
            else:
                logger.error_code(f"{self.datetype=} ist ungültig")
                raise BaseException

            data = (date,)
            db.sql(sql,parameters=data)

            dictionary = {}
            entf_list = []
            dat = db.fetchall()
            for attr in dat:
                if attr[1] in dictionary:
                    continue
                new_list = []
                for x in dat:
                    if x[1] == attr[1]:
                        new_list.append(x)
                dictionary[attr[1]] = new_list

            for values in dictionary.values():
                entf_list = []
                dictionary_2 = {}

                for i in values:
                    if i[8] not in dictionary_2:
                        dictionary_2[i[8]] = []
                    dictionary_2[i[8]].append(i)

                for z in dictionary_2.values():
                    vergl = []

                    for i_2 in z:
                        if i_2 not in vergl:
                            vergl.append(i_2)

                    zustand = []
                    for v in vergl:
                        # i[3] Zustandsbewertung
                        zustand.append(v[27])

                    if len(zustand) > 0:
                        x = 0
                        z_min = zustand.index(min(zustand))
                        for _ in zustand:
                            if x != z_min:
                                entf = x
                                # entf_index = zustand.index(entf)
                                # pk von dem element welches entfernt werden soll

                                entf_list.append(vergl[entf][0])

                            x += 1

                #Datenbank anweisung um die Elemente zu löschen
                for i in entf_list:

                    sql = "DELETE FROM substanz_haltung_bewertung WHERE pk=?"
                    data = (i,)
                    db.sql(sql,parameters=data)
            try:
                db.commit()
            except:
                pass

            if self.datetype == 'Befahrungsdatum':
                sql = """
                                                   SELECT
                                                       substanz_haltung_bewertung.pk,
                                                       substanz_haltung_bewertung.untersuchhal,
                                                       NULL,
                                                       substanz_haltung_bewertung.schoben,
                                                       substanz_haltung_bewertung.schunten,
                                                       substanz_haltung_bewertung.id,
                                                       substanz_haltung_bewertung.videozaehler,
                                                       substanz_haltung_bewertung.inspektionslaenge,
                                                       substanz_haltung_bewertung.station,
                                                       substanz_haltung_bewertung.timecode,
                                                       substanz_haltung_bewertung.kuerzel,
                                                       substanz_haltung_bewertung.charakt1,
                                                       substanz_haltung_bewertung.charakt2,
                                                       substanz_haltung_bewertung.quantnr1,
                                                       substanz_haltung_bewertung.quantnr2,
                                                       substanz_haltung_bewertung.Schadensart,
                                                       substanz_haltung_bewertung.Schadensauspraegung,
                                                       substanz_haltung_bewertung.streckenschaden,
                                                       substanz_haltung_bewertung.pos_von,
                                                       substanz_haltung_bewertung.pos_bis,
                                                       substanz_haltung_bewertung.foto_dateiname,
                                                       substanz_haltung_bewertung.film_dateiname,
                                                       NULL,
                                                       substanz_haltung_bewertung.bw_bs,
                                                       substanz_haltung_bewertung.Zustandsklasse_D,
                                                       substanz_haltung_bewertung.Zustandsklasse_S,
                                                       substanz_haltung_bewertung.Zustandsklasse_B,
                                                       substanz_haltung_bewertung.Zustandsklasse_ges,
                                                       substanz_haltung_bewertung.Schadenslaenge,
                                                       substanz_haltung_bewertung.createdat,
                                                       haltungen.haltnam,
                                                       haltungen.material,
                                                       haltungen.hoehe,
                                                       haltungen.createdat,
                                                       substanz_haltung_bewertung.untersuchtag
                                                   FROM substanz_haltung_bewertung, haltungen
                                                   WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120 
                                                   AND (substanz_haltung_bewertung.Schadensart = 'PktS') 
                                                   AND (substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                                                   AND Zustandsklasse_ges IN (0,1,2,3,4)
                                               """
            elif self.datetype == 'Importdatum':
                sql = """
                                                   SELECT
                                                       substanz_haltung_bewertung.pk,
                                                       substanz_haltung_bewertung.untersuchhal,
                                                       NULL,
                                                       substanz_haltung_bewertung.schoben,
                                                       substanz_haltung_bewertung.schunten,
                                                       substanz_haltung_bewertung.id,
                                                       substanz_haltung_bewertung.videozaehler,
                                                       substanz_haltung_bewertung.inspektionslaenge,
                                                       substanz_haltung_bewertung.station,
                                                       substanz_haltung_bewertung.timecode,
                                                       substanz_haltung_bewertung.kuerzel,
                                                       substanz_haltung_bewertung.charakt1,
                                                       substanz_haltung_bewertung.charakt2,
                                                       substanz_haltung_bewertung.quantnr1,
                                                       substanz_haltung_bewertung.quantnr2,
                                                       substanz_haltung_bewertung.Schadensart,
                                                       substanz_haltung_bewertung.Schadensauspraegung,
                                                       substanz_haltung_bewertung.streckenschaden,
                                                       substanz_haltung_bewertung.pos_von,
                                                       substanz_haltung_bewertung.pos_bis,
                                                       substanz_haltung_bewertung.foto_dateiname,
                                                       substanz_haltung_bewertung.film_dateiname,
                                                       NULL,
                                                       substanz_haltung_bewertung.bw_bs,
                                                       substanz_haltung_bewertung.Zustandsklasse_D,
                                                       substanz_haltung_bewertung.Zustandsklasse_S,
                                                       substanz_haltung_bewertung.Zustandsklasse_B,
                                                       substanz_haltung_bewertung.Zustandsklasse_ges,
                                                       substanz_haltung_bewertung.Schadenslaenge,
                                                       substanz_haltung_bewertung.createdat,
                                                       haltungen.haltnam,
                                                       haltungen.material,
                                                       haltungen.hoehe,
                                                       haltungen.createdat
                                                   FROM substanz_haltung_bewertung, haltungen
                                                   WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120
                                                   AND (substanz_haltung_bewertung.Schadensart = 'PktS') 
                                                   AND (substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                                                   AND Zustandsklasse_ges IN (0,1,2,3,4)
                                               """
            else:
                logger.error_code(f"{self.datetype=} ist ungültig")
                raise BaseException

            data = (date,)
            db.sql(sql,parameters=data)

            dictionary = {}
            entf_list = []
            dat = db.fetchall()
            for attr in dat:
                if attr[1] in dictionary:
                    continue
                new_list = []
                for x in dat:
                    if x[1] == attr[1]:
                        new_list.append(x)
                dictionary[attr[1]] = new_list


            for values in dictionary.values():
                entf_list = []
                dictionary_2 = {}

                for i in values:
                    if i[8] not in dictionary_2:
                        dictionary_2[i[8]] = []
                    dictionary_2[i[8]].append(i)

                for z in dictionary_2.values():
                    vergl = []

                    for i_2 in z:
                        if i_2 not in vergl:
                            vergl.append(i_2)

                    zustand = []
                    for v in vergl:
                        # i[3] Zustandsbewertung
                        zustand.append(v[27])

                    if len(zustand) > 0:
                        x = 0
                        z_min = zustand.index(min(zustand))
                        for _ in zustand:
                            if x != z_min:
                                entf = x
                                # entf_index = zustand.index(entf)
                                # pk von dem element welches entfernt werden soll

                                entf_list.append(vergl[entf][0])

                            x += 1

                # Datenbank anweisung um die Elemente zu löschen
                for i in entf_list:
                    sql = "DELETE FROM substanz_haltung_bewertung WHERE pk=?"
                    data = (i,)
                    db.sql(sql,parameters=data)
            try:
                db.commit()
            except:
                pass

            if self.datetype == 'Befahrungsdatum':

                sql = """
                                                       SELECT
                                                           substanz_haltung_bewertung.pk,
                                                           substanz_haltung_bewertung.untersuchhal,
                                                           NULL,
                                                           substanz_haltung_bewertung.schoben,
                                                           substanz_haltung_bewertung.schunten,
                                                           substanz_haltung_bewertung.id,
                                                           substanz_haltung_bewertung.videozaehler,
                                                           substanz_haltung_bewertung.inspektionslaenge,
                                                           substanz_haltung_bewertung.station,
                                                           substanz_haltung_bewertung.timecode,
                                                           substanz_haltung_bewertung.kuerzel,
                                                           substanz_haltung_bewertung.charakt1,
                                                           substanz_haltung_bewertung.charakt2,
                                                           substanz_haltung_bewertung.quantnr1,
                                                           substanz_haltung_bewertung.quantnr2,
                                                           substanz_haltung_bewertung.Schadensart,
                                                           substanz_haltung_bewertung.Schadensauspraegung,
                                                           substanz_haltung_bewertung.streckenschaden,
                                                           substanz_haltung_bewertung.pos_von,
                                                           substanz_haltung_bewertung.pos_bis,
                                                           substanz_haltung_bewertung.foto_dateiname,
                                                           substanz_haltung_bewertung.film_dateiname,
                                                           NULL,
                                                           substanz_haltung_bewertung.bw_bs,
                                                           substanz_haltung_bewertung.Zustandsklasse_D,
                                                           substanz_haltung_bewertung.Zustandsklasse_S,
                                                           substanz_haltung_bewertung.Zustandsklasse_B,
                                                           substanz_haltung_bewertung.Zustandsklasse_ges,
                                                           substanz_haltung_bewertung.Schadenslaenge,
                                                           substanz_haltung_bewertung.createdat,
                                                           haltungen.haltnam,
                                                           haltungen.material,
                                                           haltungen.hoehe,
                                                           haltungen.createdat,
                                                           substanz_haltung_bewertung.untersuchtag
                                                       FROM substanz_haltung_bewertung, haltungen
                                                       WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120 
                                                       AND (substanz_haltung_bewertung.Schadensart = 'UmfS') 
                                                       AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS')
                                                       AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                   """
            elif self.datetype == 'Importdatum':
                sql = """
                                                       SELECT
                                                           substanz_haltung_bewertung.pk,
                                                           substanz_haltung_bewertung.untersuchhal,
                                                           NULL,
                                                           substanz_haltung_bewertung.schoben,
                                                           substanz_haltung_bewertung.schunten,
                                                           substanz_haltung_bewertung.id,
                                                           substanz_haltung_bewertung.videozaehler,
                                                           substanz_haltung_bewertung.inspektionslaenge,
                                                           substanz_haltung_bewertung.station,
                                                           substanz_haltung_bewertung.timecode,
                                                           substanz_haltung_bewertung.kuerzel,
                                                           substanz_haltung_bewertung.charakt1,
                                                           substanz_haltung_bewertung.charakt2,
                                                           substanz_haltung_bewertung.quantnr1,
                                                           substanz_haltung_bewertung.quantnr2,
                                                           substanz_haltung_bewertung.Schadensart,
                                                           substanz_haltung_bewertung.Schadensauspraegung,
                                                           substanz_haltung_bewertung.streckenschaden,
                                                           substanz_haltung_bewertung.pos_von,
                                                           substanz_haltung_bewertung.pos_bis,
                                                           substanz_haltung_bewertung.foto_dateiname,
                                                           substanz_haltung_bewertung.film_dateiname,
                                                           NULL,
                                                           substanz_haltung_bewertung.bw_bs,
                                                           substanz_haltung_bewertung.Zustandsklasse_D,
                                                           substanz_haltung_bewertung.Zustandsklasse_S,
                                                           substanz_haltung_bewertung.Zustandsklasse_B,
                                                           substanz_haltung_bewertung.Zustandsklasse_ges,
                                                           substanz_haltung_bewertung.Schadenslaenge,
                                                           substanz_haltung_bewertung.createdat,
                                                           haltungen.haltnam,
                                                           haltungen.material,
                                                           haltungen.hoehe,
                                                           haltungen.createdat
                                                       FROM substanz_haltung_bewertung, haltungen
                                                       WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 
                                                       AND (substanz_haltung_bewertung.Schadensart = 'UmfS') 
                                                       AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS')
                                                       AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                   """
            else:
                logger.error_code(f"{self.datetype=} ist ungültig")
                raise BaseException

            data = (date,)
            db.sql(sql,parameters=data)

            dictionary = {}
            entf_list = []
            dat = db.fetchall()
            for attr in dat:
                if attr[1] in dictionary:
                    continue
                new_list = []
                for x in dat:
                    if x[1] == attr[1]:
                        new_list.append(x)
                dictionary[attr[1]] = new_list

            for values in dictionary.values():
                entf_list = []
                dictionary_2 = {}

                for i in values:
                    if i[8] not in dictionary_2:
                        dictionary_2[i[8]] = []
                    dictionary_2[i[8]].append(i)

                for z in dictionary_2.values():
                    vergl = []

                    for i_2 in z:
                        if i_2 not in vergl:
                            vergl.append(i_2)

                    zustand = []
                    for v in vergl:
                        # i[3] Zustandsbewertung
                        zustand.append(v[27])

                    if len(zustand) > 0:
                        x = 0
                        z_min = zustand.index(min(zustand))
                        for _ in zustand:
                            if x != z_min:
                                entf = x
                                # entf_index = zustand.index(entf)
                                # pk von dem element welches entfernt werden soll

                                entf_list.append(vergl[entf][0])

                            x += 1

                # Datenbank anweisung um die Elemente zu löschen
                for i in entf_list:
                    sql = "DELETE FROM substanz_haltung_bewertung WHERE pk=?"
                    data = (i,)
                    db.sql(sql,parameters=data)

            try:
                db.commit()
            except:
                pass

            if self.datetype == 'Befahrungsdatum':
                sql = """
                                                               SELECT
                                                                   substanz_haltung_bewertung.pk,
                                                                   substanz_haltung_bewertung.untersuchhal,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.schoben,
                                                                   substanz_haltung_bewertung.schunten,
                                                                   substanz_haltung_bewertung.id,
                                                                   substanz_haltung_bewertung.videozaehler,
                                                                   substanz_haltung_bewertung.inspektionslaenge,
                                                                   substanz_haltung_bewertung.station,
                                                                   substanz_haltung_bewertung.timecode,
                                                                   substanz_haltung_bewertung.kuerzel,
                                                                   substanz_haltung_bewertung.charakt1,
                                                                   substanz_haltung_bewertung.charakt2,
                                                                   substanz_haltung_bewertung.quantnr1,
                                                                   substanz_haltung_bewertung.quantnr2,
                                                                   substanz_haltung_bewertung.Schadensart,
                                                                   substanz_haltung_bewertung.Schadensauspraegung,
                                                                   substanz_haltung_bewertung.streckenschaden,
                                                                   substanz_haltung_bewertung.pos_von,
                                                                   substanz_haltung_bewertung.pos_bis,
                                                                   substanz_haltung_bewertung.foto_dateiname,
                                                                   substanz_haltung_bewertung.film_dateiname,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.bw_bs,
                                                                   substanz_haltung_bewertung.Zustandsklasse_D,
                                                                   substanz_haltung_bewertung.Zustandsklasse_S,
                                                                   substanz_haltung_bewertung.Zustandsklasse_B,
                                                                   substanz_haltung_bewertung.Zustandsklasse_ges,
                                                                   substanz_haltung_bewertung.Schadenslaenge,
                                                                   substanz_haltung_bewertung.createdat,
                                                                   haltungen.haltnam,
                                                                   haltungen.material,
                                                                   haltungen.hoehe,
                                                                   haltungen.createdat,
                                                                   substanz_haltung_bewertung.untersuchtag
                                                               FROM substanz_haltung_bewertung, haltungen
                                                               WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120 
                                                               AND (substanz_haltung_bewertung.Schadensart = 'UmfS') 
                                                               AND (substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                                                               AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                           """
            elif self.datetype == 'Importdatum':
                sql = """
                                                               SELECT
                                                                   substanz_haltung_bewertung.pk,
                                                                   substanz_haltung_bewertung.untersuchhal,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.schoben,
                                                                   substanz_haltung_bewertung.schunten,
                                                                   substanz_haltung_bewertung.id,
                                                                   substanz_haltung_bewertung.videozaehler,
                                                                   substanz_haltung_bewertung.inspektionslaenge,
                                                                   substanz_haltung_bewertung.station,
                                                                   substanz_haltung_bewertung.timecode,
                                                                   substanz_haltung_bewertung.kuerzel,
                                                                   substanz_haltung_bewertung.charakt1,
                                                                   substanz_haltung_bewertung.charakt2,
                                                                   substanz_haltung_bewertung.quantnr1,
                                                                   substanz_haltung_bewertung.quantnr2,
                                                                   substanz_haltung_bewertung.Schadensart,
                                                                   substanz_haltung_bewertung.Schadensauspraegung,
                                                                   substanz_haltung_bewertung.streckenschaden,
                                                                   substanz_haltung_bewertung.pos_von,
                                                                   substanz_haltung_bewertung.pos_bis,
                                                                   substanz_haltung_bewertung.foto_dateiname,
                                                                   substanz_haltung_bewertung.film_dateiname,
                                                                   NULL,
                                                                   substanz_haltung_bewertung.bw_bs,
                                                                   substanz_haltung_bewertung.Zustandsklasse_D,
                                                                   substanz_haltung_bewertung.Zustandsklasse_S,
                                                                   substanz_haltung_bewertung.Zustandsklasse_B,
                                                                   substanz_haltung_bewertung.Zustandsklasse_ges,
                                                                   substanz_haltung_bewertung.Schadenslaenge,
                                                                   substanz_haltung_bewertung.createdat,
                                                                   haltungen.haltnam,
                                                                   haltungen.material,
                                                                   haltungen.hoehe,
                                                                   haltungen.createdat
                                                               FROM substanz_haltung_bewertung, haltungen
                                                               WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 
                                                               AND (substanz_haltung_bewertung.Schadensart = 'UmfS') 
                                                               AND (substanz_haltung_bewertung.Schadensauspraegung = 'DdS')
                                                               AND Zustandsklasse_ges IN (0,1,2,3,4)
                                                           """
            else:
                logger.error_code(f"{self.datetype=} ist ungültig")
                raise BaseException

            data = (date,)
            db.sql(sql,parameters=data)

            dictionary = {}
            entf_list = []
            dat = db.fetchall()
            for attr in dat:
                if attr[1] in dictionary:
                    continue
                new_list = []
                for x in dat:
                    if x[1] == attr[1]:
                        new_list.append(x)
                dictionary[attr[1]] = new_list

            for values in dictionary.values():
                entf_list = []
                dictionary_2 = {}

                for i in values:
                    if i[8] not in dictionary_2:
                        dictionary_2[i[8]] = []
                    dictionary_2[i[8]].append(i)

                for z in dictionary_2.values():
                    vergl = []

                    for i_2 in z:
                        if i_2 not in vergl:
                            vergl.append(i_2)

                    zustand = []
                    for v in vergl:
                        # i[3] Zustandsbewertung
                        zustand.append(v[27])

                    if len(zustand) > 0:
                        x = 0
                        z_min = zustand.index(min(zustand))
                        for _ in zustand:
                            if x != z_min:
                                entf = x
                                # entf_index = zustand.index(entf)
                                # pk von dem element welches entfernt werden soll

                                entf_list.append(vergl[entf][0])

                            x += 1

                # Datenbank anweisung um die Elemente zu löschen
                for i in entf_list:
                    sql = "DELETE FROM substanz_haltung_bewertung WHERE pk=?"
                    data = (i,)
                    db.sql(sql,parameters=data)

            try:
                db.commit()
            except:
                pass
            logger.debug(f'Ende der Schadensueberlagerung: {datetime.now()}')

    def subkans(self):
        #Berechnung der Substanzklassen

        date = self.date
        db = self.db
        crs = self.crs
        haltung = self.haltung

        #data = db_x

        db1 = self.db
        #curs = db1.cursl()

        sql = """CREATE TABLE IF NOT EXISTS haltungen_substanz_bewertung AS 
                        SELECT pk, 
                        haltnam, 
                        schoben, 
                        schunten,                                  
                        hoehe,                                     
                        breite,                                   
                        laenge,                                 
                        baujahr,
                        untersuchtag,
                        untersucher,
                        wetter,
                        bewertungsart,
                        bewertungstag,
                         strasse,
                         datenart,
                         max_ZD,
                         max_ZB, 
                         max_ZS,
                         objektklasse_dichtheit,
                         objektklasse_standsicherheit,
                         objektklasse_betriebssicherheit,
                         objektklasse_gesamt,
                        geom
                        FROM haltungen_untersucht_bewertung """
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('haltungen_substanz_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE haltungen_substanz_bewertung ADD COLUMN Abnutzung INT ;""")
        except:
            pass

        try:
            db.sql("""ALTER TABLE haltungen_substanz_bewertung ADD COLUMN Substanzklasse INT ;""")
        except:
            pass


        if self.datetype == 'Befahrungsdatum':
            if haltung:
                sql = """
                                       SELECT
                                           substanz_haltung_bewertung.pk,
                                           substanz_haltung_bewertung.untersuchhal,
                                           NULL,
                                           substanz_haltung_bewertung.schoben,
                                           substanz_haltung_bewertung.schunten,
                                           substanz_haltung_bewertung.id,
                                           substanz_haltung_bewertung.videozaehler,
                                           substanz_haltung_bewertung.inspektionslaenge,
                                           substanz_haltung_bewertung.station,
                                           substanz_haltung_bewertung.timecode,
                                           substanz_haltung_bewertung.kuerzel,
                                           substanz_haltung_bewertung.charakt1,
                                           substanz_haltung_bewertung.charakt2,
                                           substanz_haltung_bewertung.quantnr1,
                                           substanz_haltung_bewertung.quantnr2,
                                           substanz_haltung_bewertung.Schadensart,
                                           substanz_haltung_bewertung.Schadensauspraegung,
                                           substanz_haltung_bewertung.streckenschaden,
                                           substanz_haltung_bewertung.pos_von,
                                           substanz_haltung_bewertung.pos_bis,
                                           substanz_haltung_bewertung.foto_dateiname,
                                           substanz_haltung_bewertung.film_dateiname,
                                           NULL,
                                           substanz_haltung_bewertung.bw_bs,
                                           substanz_haltung_bewertung.Zustandsklasse_D,
                                           substanz_haltung_bewertung.Zustandsklasse_S,
                                           substanz_haltung_bewertung.Zustandsklasse_B,
                                           substanz_haltung_bewertung.Zustandsklasse_ges,
                                           substanz_haltung_bewertung.Schadenslaenge,
                                           substanz_haltung_bewertung.createdat,
                                           substanz_haltung_bewertung.Startgewicht,
                                           haltungen.haltnam,
                                           haltungen.material,
                                           haltungen.hoehe,
                                           haltungen.createdat,
                                           substanz_haltung_bewertung.untersuchtag
                                       FROM substanz_haltung_bewertung, haltungen
                                       WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120
                                       AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS' OR (substanz_haltung_bewertung.Schadensart = 'StrS' AND streckenschaden ='A')) 
                                       AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS' OR substanz_haltung_bewertung.Schadensauspraegung = 'DdS' OR substanz_haltung_bewertung.Schadensauspraegung = 'SoB')
                                       AND Zustandsklasse_ges IN (0,1,2,3,4)
                                   """
        elif self.datetype == 'Importdatum':
            if haltung:
                sql = """
                                       SELECT
                                           substanz_haltung_bewertung.pk,
                                           substanz_haltung_bewertung.untersuchhal,
                                           NULL,
                                           substanz_haltung_bewertung.schoben,
                                           substanz_haltung_bewertung.schunten,
                                           substanz_haltung_bewertung.id,
                                           substanz_haltung_bewertung.videozaehler,
                                           substanz_haltung_bewertung.inspektionslaenge,
                                           substanz_haltung_bewertung.station,
                                           substanz_haltung_bewertung.timecode,
                                           substanz_haltung_bewertung.kuerzel,
                                           substanz_haltung_bewertung.charakt1,
                                           substanz_haltung_bewertung.charakt2,
                                           substanz_haltung_bewertung.quantnr1,
                                           substanz_haltung_bewertung.quantnr2,
                                           substanz_haltung_bewertung.Schadensart,
                                           substanz_haltung_bewertung.Schadensauspraegung,
                                           substanz_haltung_bewertung.streckenschaden,
                                           substanz_haltung_bewertung.pos_von,
                                           substanz_haltung_bewertung.pos_bis,
                                           substanz_haltung_bewertung.foto_dateiname,
                                           substanz_haltung_bewertung.film_dateiname,
                                           NULL,
                                           substanz_haltung_bewertung.bw_bs,
                                           substanz_haltung_bewertung.Zustandsklasse_D,
                                           substanz_haltung_bewertung.Zustandsklasse_S,
                                           substanz_haltung_bewertung.Zustandsklasse_B,
                                           substanz_haltung_bewertung.Zustandsklasse_ges,
                                           substanz_haltung_bewertung.Schadenslaenge,
                                           substanz_haltung_bewertung.createdat,
                                           substanz_haltung_bewertung.Startgewicht,
                                           haltungen.haltnam,
                                           haltungen.material,
                                           haltungen.hoehe,
                                           haltungen.createdat
                                       FROM substanz_haltung_bewertung, haltungen
                                       WHERE haltungen.haltnam = substanz_haltung_bewertung.untersuchhal AND ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120
                                       AND (substanz_haltung_bewertung.Schadensart = 'PktS' OR substanz_haltung_bewertung.Schadensart = 'UmfS' OR (substanz_haltung_bewertung.Schadensart = 'StrS' AND streckenschaden ='A')) 
                                       AND (substanz_haltung_bewertung.Schadensauspraegung = 'OfS' OR substanz_haltung_bewertung.Schadensauspraegung = 'DdS' OR substanz_haltung_bewertung.Schadensauspraegung = 'SoB')
                                       AND Zustandsklasse_ges IN (0,1,2,3,4)
                                   """
        else:
            logger.error_code(f"{self.datetype=} ist ungültig")
            raise BaseException
        data = (date,)
        db.sql(sql,parameters=data)

        for attr in db1.fetchall():

            sl = attr[28]
            # iface.messageBar().pushMessage("Error",
            #                                str(sl),
            #                                level=Qgis.MessageLevel.Critical)
            sg=0
            kg=0
            stg=float(attr[30])


            #Klassengewichte
            if int(attr[27]) == 0:
                kg = 1.0
            elif int(attr[27]) == 1:
                kg = 0.8
            elif int(attr[27]) == 2:
                kg = 0.25
            elif int(attr[27]) == 3:
                kg = 0.15
            elif int(attr[27]) == 4:
                kg = 0.05
            elif int(attr[27]) == 5:
                kg = 0.0

            # schadensgewicht:

            if sl not in ("", None, "not found"):

                sg = float(sl) * stg * kg


            #sg in tabelle schreiben
            sql = """UPDATE substanz_haltung_bewertung SET Schadensgewicht = ? WHERE substanz_haltung_bewertung.pk = ?"""
            data = (round_up(sg,2), attr[0])

            db.sql(sql,parameters=data)

        #Bruttoschadenslänge BSL und Abnutzung ABN


        if self.datetype == 'Befahrungsdatum':
            sql = """SELECT
                        substanz_haltung_bewertung.pk AS pk,
                        substanz_haltung_bewertung.untersuchhal,
                        SUM(substanz_haltung_bewertung.Schadensgewicht) AS Gesamtschadensgewicht,
                        haltungen_untersucht.haltnam,
                        coalesce(MIN(
                            CASE 
                                WHEN substanz_haltung_bewertung.kuerzel = 'BCE' 
                                     AND substanz_haltung_bewertung.station < haltungen_untersucht.laenge  
                                THEN substanz_haltung_bewertung.station
                                ELSE haltungen_untersucht.laenge
                            END
                        ),haltungen.laenge),  
                    haltungen_substanz_bewertung.pk,
                    haltungen_substanz_bewertung.objektklasse_gesamt
                    FROM 
                        substanz_haltung_bewertung
                    JOIN 
                        haltungen_untersucht ON haltungen_untersucht.haltnam = substanz_haltung_bewertung.untersuchhal
                    JOIN 
                        haltungen_substanz_bewertung ON haltungen_substanz_bewertung.haltnam = substanz_haltung_bewertung.untersuchhal
                    JOIN 
                        haltungen ON substanz_haltung_bewertung.untersuchhal = haltungen.haltnam
                    WHERE ABS(strftime('%s', substanz_haltung_bewertung.untersuchtag) - strftime('%s', ?)) < 120
                    GROUP BY 
                        substanz_haltung_bewertung.untersuchhal;"""
        elif self.datetype == 'Importdatum':
            sql = """SELECT
                                    substanz_haltung_bewertung.pk AS pk,
                                    substanz_haltung_bewertung.untersuchhal,
                                    SUM(substanz_haltung_bewertung.Schadensgewicht) AS Gesamtschadensgewicht,
                                    haltungen_untersucht.haltnam,
                                    coalesce(MIN(
                                        CASE 
                                            WHEN substanz_haltung_bewertung.kuerzel = 'BCE' 
                                                 AND substanz_haltung_bewertung.station < haltungen_untersucht.laenge  
                                            THEN substanz_haltung_bewertung.station
                                            ELSE haltungen_untersucht.laenge
                                        END
                                    ),haltungen.laenge),  
                                haltungen_substanz_bewertung.pk,
                                haltungen_substanz_bewertung.objektklasse_gesamt
                                FROM 
                                    substanz_haltung_bewertung
                                JOIN 
                                    haltungen_untersucht ON haltungen_untersucht.haltnam = substanz_haltung_bewertung.untersuchhal
                                JOIN 
                                    haltungen_substanz_bewertung ON haltungen_substanz_bewertung.haltnam = substanz_haltung_bewertung.untersuchhal
                                JOIN 
                                    haltungen ON substanz_haltung_bewertung.untersuchhal = haltungen.haltnam
                                WHERE ABS(strftime('%s', substanz_haltung_bewertung.createdat) - strftime('%s', ?)) < 120 
                                GROUP BY 
                                    substanz_haltung_bewertung.untersuchhal;"""

        data = (date,)

        db.sql(sql,parameters=data)
        sbk='-'
        abn='-'

        for attr in db.fetchall():
            # abn = bsl/länge*100
            if attr[2] not in ("","not found", None, None) and attr[3] not in ("","not found", None, None):
                print(abn)
                abn=formf(float(attr[2])/float(attr[4])*100,8)

                # #substanzklasse
                sub_ges = 100-float(abn)

                if sub_ges >= 95:
                    sbk = 5
                elif 95>sub_ges>=85:
                    sbk = 4
                elif 85>sub_ges>=67:
                    sbk = 3
                elif 67>sub_ges>=33:
                    sbk = 2
                elif 33>sub_ges>5:
                    sbk = 1
                elif 5>=sub_ges:
                    sbk = 0
            elif attr[6] == 5:
                abn = 0
                sbk = 5
            else:
                abn = 'None'
                sbk = 'None'
            # abn in tabelle schreiben
            sql = """UPDATE haltungen_substanz_bewertung SET Abnutzung = ? WHERE haltungen_substanz_bewertung.pk = ?"""
            data = (abn, attr[5])

            db.sql(sql,parameters=data)

            # sg in tabelle schreiben
            sql = """UPDATE haltungen_substanz_bewertung SET Substanzklasse = ? WHERE haltungen_substanz_bewertung.pk = ?"""
            data = (sbk, attr[5])

            db.sql(sql,parameters=data)


            #Sonderfall nur BDD in Haltung vorhanden als bewerteter Schaden

            sql= """
                    UPDATE haltungen_substanz_bewertung SET Abnutzung = 0 WHERE 
                    (     
                    SELECT untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        GROUP BY untersuchhal
                        HAVING COUNT(CASE WHEN kuerzel = 'BDD' THEN 1 END) > 0
                           AND COUNT(CASE WHEN kuerzel = 'BCD' THEN 1 END) > 0
                           AND COUNT(CASE WHEN kuerzel = 'BCE' THEN 1 END) > 0
                           AND COUNT(CASE WHEN kuerzel NOT IN ('BDD', 'BCD', 'BCE') THEN 1 END) = 0
                        )"""

            db.sql(sql)

            sql = """
                    UPDATE haltungen_substanz_bewertung SET Substanzklasse = 5 WHERE (
                    SELECT untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        GROUP BY untersuchhal
                        HAVING COUNT(CASE WHEN kuerzel = 'BDD' THEN 1 END) > 0
                           AND COUNT(CASE WHEN kuerzel = 'BCD' THEN 1 END) > 0
                           AND COUNT(CASE WHEN kuerzel = 'BCE' THEN 1 END) > 0
                           AND COUNT(CASE WHEN kuerzel NOT IN ('BDD', 'BCD', 'BCE') THEN 1 END) = 0
                        )"""

            db.sql(sql)

        try:
            db1.commit()
        except:
            pass



        sql = """SELECT RecoverGeometryColumn('haltungen_substanz_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql,parameters=data)
            db1.commit()
        except:
            pass

        logger.debug(f'Ende der Substanzklassifizierung: {datetime.now()}')


        uri = QgsDataSourceUri()
        uri.setDatabase(db.dbname)
        schema = ''
        table = 'haltungen_substanz_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        haltungen_substanz_bewertung = enums.LAYERBEZ.SK_ZUSTAND_HALTUNGEN.value
        vlayer = QgsVectorLayer(uri.uri(), haltungen_substanz_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(haltungen_substanz_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/haltungen_subkans.qml')
        #QgsProject.instance().addMapLayer(vlayer)
        group = 'Ergebnisse'
        layersRoot = QgsProject.instance().layerTreeRoot()
        QgsProject.instance().addMapLayer(vlayer, False)
        atcGroup = layersRoot.findGroup(group)
        if atcGroup is None:
            atcGroup = layersRoot.addGroup(group)
        atcGroup.addLayer(vlayer)
