# -*- coding: utf-8 -*-
import os

from qgis.core import *
from qgis.utils import iface, spatialite_connect, pluginDirectory
import sqlite3
import math
import pandas as pd

class sanierungsbedarfszahl_funkt:
    def __init__(self, check_cb, db, date, speicher, atlas_path, massstab, format, excel_format, excel_speicher, epsg, db_format):

        self.check_cb = check_cb
        self.db = db
        self.date = date
        self.speicher = speicher
        self.massstab = massstab
        self.format = format
        self.atlas_path = atlas_path
        self.excel_format = excel_format
        self.excel_speicher = excel_speicher
        self.crs = epsg
        self.db_format = db_format
        self.formsDir = os.path.join(pluginDirectory("qkan"), "forms")
        self.qmlDir = os.path.join(pluginDirectory("qkan"), "templates/qml")

        self.haltung = False
        self.leitung = False


    def run(self):
        check_cb = self.check_cb
        if check_cb['cb3'] and check_cb['cb1']:
            self.haltung = True
            self.leitung = False
            self.schadenslaenge_haltung()
            self.sanierungszahl_dwa_haltung()

        if check_cb['cb5'] and check_cb['cb4']:
            self.schadenslaenge_schacht()
            self.sanierungszahl_dwa_schacht()

        if check_cb['cb3'] and check_cb['cb2']:
            self.haltung = True
            self.leitung = False
            self.schadenslaenge_haltung()
            self.systemzahl_isy_haltung()

        if check_cb['cb5'] and check_cb['cb6']:
            self.schadenslaenge_schacht()
            self.systemzahl_isy_schacht()

        if check_cb['cb14'] and check_cb['cb12']:
            self.leitung = True
            self.haltung = False
            self.schadenslaenge_haltung()
            self.sanierungszahl_dwa_haltung()

        if check_cb['cb14'] and check_cb['cb13']:
            self.leitung = True
            self.haltung = False
            self.schadenslaenge_haltung()
            self.systemzahl_isy_haltung()

        if check_cb['cb7']:
            self.atlas()

        if check_cb['cb8']:
            self.plan()

        if check_cb['cb9']:
            self.excel_haltungen()

        if check_cb['cb10']:
            self.excel_schaechte()

        if check_cb['cb11']:
            self.excel_leitungen()


    def schadenslaenge_haltung(self):
        db = self.db
        date = self.date
        data = db
        db = spatialite_connect(data)
        curs = db.cursor()
        leitung = self.leitung
        haltung = self.haltung

        try:
            curs.execute("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Schadenslaenge INTEGER ;""")
            db.commit()
        except:
            pass

        db = spatialite_connect(data)
        curs = db.cursor()

        if haltung == True:
            sql = """
                SELECT
                    untersuchdat_haltung_bewertung.pk,
                    untersuchdat_haltung_bewertung.untersuchhal,
                    untersuchdat_haltung_bewertung.untersuchrichtung,
                    untersuchdat_haltung_bewertung.schoben,
                    untersuchdat_haltung_bewertung.schunten,
                    untersuchdat_haltung_bewertung.id,
                    untersuchdat_haltung_bewertung.videozaehler,
                    untersuchdat_haltung_bewertung.inspektionslaenge,
                    untersuchdat_haltung_bewertung.station,
                    untersuchdat_haltung_bewertung.timecode,
                    untersuchdat_haltung_bewertung.kuerzel,
                    untersuchdat_haltung_bewertung.charakt1,
                    untersuchdat_haltung_bewertung.charakt2,
                    untersuchdat_haltung_bewertung.quantnr1,
                    untersuchdat_haltung_bewertung.quantnr2,
                    untersuchdat_haltung_bewertung.streckenschaden,
                    untersuchdat_haltung_bewertung.streckenschaden_lfdnr,
                    untersuchdat_haltung_bewertung.pos_von,
                    untersuchdat_haltung_bewertung.pos_bis,
                    untersuchdat_haltung_bewertung.foto_dateiname,
                    untersuchdat_haltung_bewertung.film_dateiname,
                    untersuchdat_haltung_bewertung.richtung,
                    untersuchdat_haltung_bewertung.createdat,
                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.createdat,
                    haltungen.haltnam
                FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, haltungen
                WHERE haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ?  AND  substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? 
            """
            data = (date, date)

        if leitung == True:
            sql = """
                        SELECT
                            untersuchdat_haltung_bewertung.pk,
                            untersuchdat_haltung_bewertung.untersuchhal,
                            untersuchdat_haltung_bewertung.untersuchrichtung,
                            untersuchdat_haltung_bewertung.schoben,
                            untersuchdat_haltung_bewertung.schunten,
                            untersuchdat_haltung_bewertung.id,
                            untersuchdat_haltung_bewertung.videozaehler,
                            untersuchdat_haltung_bewertung.inspektionslaenge,
                            untersuchdat_haltung_bewertung.station,
                            untersuchdat_haltung_bewertung.timecode,
                            untersuchdat_haltung_bewertung.kuerzel,
                            untersuchdat_haltung_bewertung.charakt1,
                            untersuchdat_haltung_bewertung.charakt2,
                            untersuchdat_haltung_bewertung.quantnr1,
                            untersuchdat_haltung_bewertung.quantnr2,
                            untersuchdat_haltung_bewertung.streckenschaden,
                            untersuchdat_haltung_bewertung.streckenschaden_lfdnr,
                            untersuchdat_haltung_bewertung.pos_von,
                            untersuchdat_haltung_bewertung.pos_bis,
                            untersuchdat_haltung_bewertung.foto_dateiname,
                            untersuchdat_haltung_bewertung.film_dateiname,
                            untersuchdat_haltung_bewertung.richtung,
                            untersuchdat_haltung_bewertung.createdat,
                            haltungen_untersucht_bewertung.haltnam,
                            haltungen_untersucht_bewertung.laenge,
                            haltungen_untersucht_bewertung.untersuchtag,
                            haltungen_untersucht_bewertung.untersucher,
                            haltungen_untersucht_bewertung.wetter,
                            haltungen_untersucht_bewertung.bewertungsart,
                            haltungen_untersucht_bewertung.bewertungstag,
                            haltungen_untersucht_bewertung.createdat,
                            anschlussleitungen.leitnam
                        FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung,anschlussleitungen
                        WHERE anschlussleitungen.leitnam= untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ?  AND  substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? 
                    """
            data = (date, date)

        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error", "Die Schadenslänge konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        x = curs.fetchall()
        liste = []
        for attr in x:
            if attr[1] not in liste:
                halt = [y for y in x if y[1] == attr[1]]
                liste.append(attr[1])
                liste_sch = []
                for h in halt:
                    sch = h[15]
                    sch_nr = h[16]
                    laenge = h[8]
                    liste_sch.append((h[0], sch, sch_nr, laenge))
                out_tup = [i for i in liste_sch if i[1] != 'not found']
                print(liste_sch)
                tup = []
                test = 1
                for pk, sch, sch_nr, laenge in out_tup:
                    tup = list(filter(lambda x: x[2] == test, out_tup))
                    print(tup)
                    print(test)
                    for elem in tup:
                        if elem[1] == 'A' and elem[2] == test:
                            id = elem[0]
                            l_1 = elem[3]
                        if elem[1] == 'B' and elem[2] == test:
                            l_2 = elem[3]
                            l = l_2 - l_1

                            sql = f"""
                                UPDATE untersuchdat_haltung_bewertung
                                    SET Schadenslaenge = ?
                                    WHERE untersuchdat_haltung_bewertung.pk = ?
                                    """
                            data = (l, id)
                            try:
                                curs.execute(sql, data)
                                db.commit()
                            except:
                                iface.messageBar().pushMessage("Error", "Die Schadenslänge der Haltungen/Leitungen konnte nicht ermittelt werden",
                                                               level=Qgis.Critical)
                    test += 1

    def schadenslaenge_schacht(self):
        db = self.db
        date = self.date
        data = db
        db = spatialite_connect(data)
        curs = db.cursor()

        try:
            curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Schadenslaenge INTEGER ;""")
            db.commit()
        except:
            pass

        db = spatialite_connect(data)
        curs = db.cursor()
        sql = """
                    SELECT
                        Untersuchdat_schacht_bewertung.pk,
                        Untersuchdat_schacht_bewertung.untersuchsch,
                        Untersuchdat_schacht_bewertung.id,
                        Untersuchdat_schacht_bewertung.videozaehler,
                        Untersuchdat_schacht_bewertung.vertikale_lage,
                        Untersuchdat_schacht_bewertung.timecode,
                        Untersuchdat_schacht_bewertung.kuerzel,
                        Untersuchdat_schacht_bewertung.charakt1,
                        Untersuchdat_schacht_bewertung.charakt2,
                        Untersuchdat_schacht_bewertung.quantnr1,
                        Untersuchdat_schacht_bewertung.quantnr2,
                        Untersuchdat_schacht_bewertung.streckenschaden,
                        Untersuchdat_schacht_bewertung.streckenschaden_lfdnr,
                        Untersuchdat_schacht_bewertung.pos_von,
                        Untersuchdat_schacht_bewertung.pos_bis,
                        Untersuchdat_schacht_bewertung.foto_dateiname,
                        Untersuchdat_schacht_bewertung.createdat,
                        schaechte_untersucht_bewertung.schnam,
                        schaechte_untersucht_bewertung.untersuchtag,
                        schaechte_untersucht_bewertung.untersucher,
                        schaechte_untersucht_bewertung.wetter,
                        schaechte_untersucht_bewertung.bewertungsart,
                        schaechte_untersucht_bewertung.bewertungstag,
                        schaechte_untersucht_bewertung.createdat
                    FROM Untersuchdat_schacht_bewertung, schaechte_untersucht_bewertung
                    WHERE schaechte_untersucht_bewertung.schnam = Untersuchdat_schacht_bewertung.untersuchsch AND substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ? AND substr(schaechte_untersucht_bewertung.createdat, 0, 17) = ? 
                """

        data = (date, date)

        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error", "Die Schadenslänge der Schächte konnte nicht ermittelt werden",
                                           level=Qgis.Critical)
        x = curs.fetchall()
        liste = []
        for attr in x:
            if attr[1] not in liste:
                halt = [y for y in x if y[1] == attr[1]]
                liste.append(attr[1])
                liste_sch = []
                for h in halt:
                    sch = h[11]
                    sch_nr = h[12]
                    laenge = h[4]
                    liste_sch.append((h[0], sch, sch_nr, laenge))
                out_tup = [i for i in liste_sch if i[1] != 'not found']
                print(liste_sch)
                tup = []
                test = 1
                for pk, sch, sch_nr, laenge in out_tup:
                    tup = list(filter(lambda x: x[2] == test, out_tup))
                    print(tup)
                    print(test)
                    for elem in tup:
                        if elem[1] == 'A' and elem[2] == test:
                            id = elem[0]
                            l_1 = elem[3]
                        if elem[1] == 'B' and elem[2] == test:
                            l_2 = elem[3]
                            l = l_2 - l_1

                            sql = f"""
                                        UPDATE Untersuchdat_schacht_bewertung
                                        SET Schadenslaenge = ?
                                        WHERE Untersuchdat_schacht_bewertung.pk = ?
                                        """
                            data = (l, id)
                            try:
                                curs.execute(sql, data)
                                db.commit()
                            except:
                                iface.messageBar().pushMessage("Error",
                                                               "Die Schadenslänge konnte nicht ermittelt werden",
                                                               level=Qgis.Critical)
                    test += 1


    def sanierungszahl_dwa_haltung(self):
        db = self.db
        date = self.date
        db_x = db
        data = db
        db = spatialite_connect(data)
        curs = db.cursor()
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Sanierungsbedarfszahl INTEGER ;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Handlungsbedarf TEXT ;""")
            db.commit()
        except:
            pass

        if haltung == True:

            sql = """
                SELECT
                    untersuchdat_haltung_bewertung.pk,
                    untersuchdat_haltung_bewertung.untersuchhal,
                    untersuchdat_haltung_bewertung.untersuchrichtung,
                    untersuchdat_haltung_bewertung.schoben,
                    untersuchdat_haltung_bewertung.schunten,
                    untersuchdat_haltung_bewertung.id,
                    untersuchdat_haltung_bewertung.videozaehler,
                    untersuchdat_haltung_bewertung.inspektionslaenge,
                    untersuchdat_haltung_bewertung.station,
                    untersuchdat_haltung_bewertung.timecode,
                    untersuchdat_haltung_bewertung.kuerzel,
                    untersuchdat_haltung_bewertung.charakt1,
                    untersuchdat_haltung_bewertung.charakt2,
                    untersuchdat_haltung_bewertung.quantnr1,
                    untersuchdat_haltung_bewertung.quantnr2,
                    untersuchdat_haltung_bewertung.streckenschaden,
                    untersuchdat_haltung_bewertung.Schadenslaenge,
                    untersuchdat_haltung_bewertung.pos_von,
                    untersuchdat_haltung_bewertung.pos_bis,
                    untersuchdat_haltung_bewertung.foto_dateiname,
                    untersuchdat_haltung_bewertung.film_dateiname,
                    untersuchdat_haltung_bewertung.richtung,
                    untersuchdat_haltung_bewertung.Zustandsklasse_D,
                    untersuchdat_haltung_bewertung.Zustandsklasse_S,
                    untersuchdat_haltung_bewertung.Zustandsklasse_B,
                    untersuchdat_haltung_bewertung.createdat,
    
                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.objektklasse_dichtheit,
                    haltungen_untersucht_bewertung.objektklasse_standsicherheit,
                    haltungen_untersucht_bewertung.objektklasse_betriebssicherheit,
                    haltungen_untersucht_bewertung.objektklasse_gesamt,
                    haltungen_untersucht_bewertung.baujahr,
                    haltungen_untersucht_bewertung.hydraulische_auslastung,
                    haltungen_untersucht_bewertung.lage_grundwasser,
                    haltungen_untersucht_bewertung.ueberdeckung,
                    haltungen_untersucht_bewertung.bodengruppe,
                    haltungen_untersucht_bewertung.createdat,
                    haltungen.haltnam
                FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, haltungen
                WHERE haltungen.haltnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ? AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ?
            """

        if leitung == True:
            sql = """
                SELECT
                    untersuchdat_haltung_bewertung.pk,
                    untersuchdat_haltung_bewertung.untersuchhal,
                    untersuchdat_haltung_bewertung.untersuchrichtung,
                    untersuchdat_haltung_bewertung.schoben,
                    untersuchdat_haltung_bewertung.schunten,
                    untersuchdat_haltung_bewertung.id,
                    untersuchdat_haltung_bewertung.videozaehler,
                    untersuchdat_haltung_bewertung.inspektionslaenge,
                    untersuchdat_haltung_bewertung.station,
                    untersuchdat_haltung_bewertung.timecode,
                    untersuchdat_haltung_bewertung.kuerzel,
                    untersuchdat_haltung_bewertung.charakt1,
                    untersuchdat_haltung_bewertung.charakt2,
                    untersuchdat_haltung_bewertung.quantnr1,
                    untersuchdat_haltung_bewertung.quantnr2,
                    untersuchdat_haltung_bewertung.streckenschaden,
                    untersuchdat_haltung_bewertung.Schadenslaenge,
                    untersuchdat_haltung_bewertung.pos_von,
                    untersuchdat_haltung_bewertung.pos_bis,
                    untersuchdat_haltung_bewertung.foto_dateiname,
                    untersuchdat_haltung_bewertung.film_dateiname,
                    untersuchdat_haltung_bewertung.richtung,
                    untersuchdat_haltung_bewertung.Zustandsklasse_D,
                    untersuchdat_haltung_bewertung.Zustandsklasse_S,
                    untersuchdat_haltung_bewertung.Zustandsklasse_B,
                    untersuchdat_haltung_bewertung.createdat,

                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.objektklasse_dichtheit,
                    haltungen_untersucht_bewertung.objektklasse_standsicherheit,
                    haltungen_untersucht_bewertung.objektklasse_betriebssicherheit,
                    haltungen_untersucht_bewertung.objektklasse_gesamt,
                    haltungen_untersucht_bewertung.baujahr,
                    haltungen_untersucht_bewertung.hydraulische_auslastung,
                    haltungen_untersucht_bewertung.lage_grundwasser,
                    haltungen_untersucht_bewertung.ueberdeckung,
                    haltungen_untersucht_bewertung.bodengruppe,
                    haltungen_untersucht_bewertung.createdat,
                    anschlussleitungen.leitnam
                FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, anschlussleitungen
                WHERE anschlussleitungen.leitnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ? AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ?
            """

        data = (date, date)
        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Sanierungsbedarfszahl der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.Critical)


        x = curs.fetchall()
        liste = []
        for attr in x:
            if attr[1] not in liste:
                # prüfen ob für die haltung berechnet werden muss!
                halt = [y for y in x if y[1] == attr[1]]
                liste.append(attr[1])
                list_zd = []
                list_zs = []
                list_zb = []
                for h in halt:

                    sl = h[16]
                    if sl == NULL or sl == 'not found' or sl == '-':
                        sl = 0
                    else:
                        sl = float(sl)
                    if sl <= 2.5:
                        sl = 2.5
                    else:
                        sl
                    z_dl = h[22]
                    list_zd.append(z_dl)
                    z_sl = h[23]
                    list_zs.append(z_sl)
                    z_bl = h[24]
                    list_zb.append(z_bl)

                # höchste Klassifizierung für die haltung bestimmen!!
                # darus folgt z

                z_d = attr[33]
                z_s = attr[34]
                z_b = attr[35]
                zp_0d = 0
                zp_0s = 0
                zp_0b = 0

                if isinstance(z_d, int):
                    if z_d == 0:
                        zp_0d = 400
                    if z_d == 1:
                        zp_0d = 300
                    if z_d == 2:
                        zp_0d = 200
                    if z_d == 3:
                        zp_0d = 100
                    if z_d == 4:
                        zp_0d = 0
                else:
                    z_d = 0

                if isinstance(z_s, int):
                    if z_s == 0:
                        zp_0s = 400
                    if z_s == 1:
                        zp_0s = 300
                    if z_s == 2:
                        zp_0s = 200
                    if z_s == 3:
                        zp_0s = 100
                    if z_s == 4:
                        zp_0s = 0
                else:
                    z_s = 0

                if isinstance(z_b, int):
                    if z_b == 0:
                        zp_0b = 400
                    if z_b == 1:
                        zp_0b = 300
                    if z_b == 2:
                        zp_0b = 200
                    if z_b == 3:
                        zp_0b = 100
                    if z_b == 4:
                        zp_0b = 0
                else:
                    z_b = 0

                # zp__zj = 50*(sum((5-k_ij)*l)/((5-k_ij)*ol))

                # zp_j = zp_0 + zp_zj

                # Schadensdichte alle schäden berücksichtigen

                # sd_d = (5-float(z_d)*sl)/((5-kd)*h[25])
                # hier restliche berechnungen !!!!! die einzelnen schäden den listen entnehmen

                list_zd = [s for s in list_zd if s != '-']

                list_zs = [s for s in list_zs if s != '-']

                list_zb = [s for s in list_zb if s != '-']

                if len(list_zd) == 0 and len(list_zs) == 0 and len(list_zb) == 0:
                    continue

                xd=0
                for i in list_zd:
                    xd+=((5-int(i))*sl)

                if ((5-z_d)*attr[7]) == 0:
                    sd_d = 0
                else:
                    sd_d = xd / ((5 - z_d) * attr[7])
                zp_d = 50 * sd_d

                xs = 0
                for i in list_zs:
                    xs += ((5 - int(i)) * sl)

                if ((5-z_s)*attr[7]) == 0:
                    sd_s = 0
                else:
                    sd_s = xs / ((5 - z_s) * attr[7])
                zp_s = 50 * sd_s

                xb = 0
                for i in list_zb:
                    xb += ((5 - int(i)) * sl)

                if ((5 - z_b) * attr[7]) == 0:
                    sd_b = 0
                else:
                    sd_b = xb / ((5 - z_b) * attr[7])

                zp_b = 50 * sd_b

                zp_jd = zp_0d + zp_d

                zp_js = zp_0s + zp_s

                zp_jb = zp_0b + zp_b

                # Bewertungsfaktor Fj

                #f_j = sum(r_jk / n_j)

                # fuer Kanal/Leitung
                baujahr = attr[37]
                hydraul = attr[38]
                gw = attr[39]
                ueberdeck = attr[40]
                boden = attr[41]

                if baujahr <= 1965 or baujahr == 0:
                    r_d1 = 1
                else:
                    r_d1 = 0

                if hydraul=="eingehlaten":
                    r_d2 = 0
                else:
                    r_d2 = 1

                if gw=="im Grundwasser":
                    r_d3 = 1
                if gw=="in der Wechselzone":
                    r_d3 = 0.5
                if gw=="oberhalb des Grundwassers" or gw=="kein Grundwasser":
                    r_d3 = 0
                else:
                    r_d3 = 1

                f_d = (r_d1+r_d2+r_d3)/3

                if ueberdeck == float:
                    if ueberdeck <= 2.5:
                        r_s1 = 1
                    if 2.5 < ueberdeck <= 4:
                        r_s1 = 0.5
                    if ueberdeck > 4:
                        r_s1 = 0
                else:
                    r_s1 = 1

                if boden=="Bodengruppe 1" or boden=="Bodengruppe 2":
                    r_s2 = 0
                if boden=="Bodengruppe 3":
                    r_s2 = 0.5
                if boden=="Bodengruppe 4":
                    r_s2 = 1
                else:
                    r_s2 = 1

                f_s = (r_s1+r_s2)/2


                if hydraul=="eingehlaten":
                    r_b1 = 0
                else:
                    r_b1 = 1

                if ueberdeck == float:
                    if ueberdeck <= 2.5:
                        r_b2 = 1
                    if 2.5 < ueberdeck <= 4:
                        r_b2 = 0.5
                    if ueberdeck > 4:
                        r_b2 = 0
                else:
                    r_b2 = 1

                f_b = (r_b1+r_b2)/2

                # Bewertungspunkte
                # bp_j=500+zp_j+50*f_j

                bp_d = 500 + zp_jd + 50 * f_d

                bp_s = 500 + zp_js + 50 * f_s

                bp_b = 500 + zp_jb + 50 * f_b

                # Objektklasse

                k = min(z_d, z_s, z_b)

                # Sanierungsbedarfszahl

                # bp der größe nach sortieren
                bp = [bp_d, bp_s, bp_b]
                bp_sort = sorted(bp)

                bp_1 = str(int(bp_sort[2]))
                bp_2 = str(int(bp_sort[1]))
                bp_3 = str(int(bp_sort[0]))

                x_1 = int(bp_1[-2:])
                x_2 = int(bp_2[-2:])
                x_3 = int(bp_3[-2:])

                sz = (int(int(bp_1) / 100) * 10 ** 3) + (int(int(bp_2) / 100) * 10 ** 2) + (
                            int(int(bp_3) / 100) * 10) + (int(
                    (x_1 + x_2 + x_3) / 30))
                if sz >= 9000:
                    handlung = 'sofort'
                if 8000 <= sz < 9000:
                    handlung = 'kurzfristig'
                if 7000 <= sz < 8000:
                    handlung = 'mittelfristig'
                if 6000 <= sz < 7000:
                    handlung = 'langfristig'
                if 5000 <= sz < 6000:
                    handlung = 'kein Handlungsbedarf'
                if sz == 0:
                    handlung = 'schadensfrei'


                sql = f"""
                        UPDATE haltungen_untersucht_bewertung
                        SET Sanierungsbedarfszahl = ?, Handlungsbedarf = ?
                        WHERE haltungen_untersucht_bewertung.haltnam = ?
                        """
                data = (sz, handlung, attr[26])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        untersuchdat_haltung_bewertung = 'untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        qmlpath = os.path.join(self.qmlDir, 'res/untersuchdat_haltung_bewertung_dwa.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'untersuchdat_haltung_bewertung_dwa.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'haltungen_untersucht_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        haltungen_untersucht_bewertung = 'haltungen_untersucht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), haltungen_untersucht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(haltungen_untersucht_bewertung)[0].id())
        except:
            pass

        qmlpath = os.path.join(self.qmlDir, 'res/haltungen_untersucht_bewertung_dwa.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'haltungen_untersucht_bewertung_dwa.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)

    def sanierungszahl_dwa_schacht(self):
        db = self.db
        date = self.date
        db_x = db
        data = db
        db = spatialite_connect(data)
        curs = db.cursor()
        crs = self.crs

        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Sanierungsbedarfszahl INTEGER ;""")
        except:
            pass

        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Handlungsbedarf TEXT ;""")
        except:
            pass

        sql = """
                SELECT
                Untersuchdat_schacht_bewertung.pk,
                Untersuchdat_schacht_bewertung.untersuchsch,
                Untersuchdat_schacht_bewertung.id,
                Untersuchdat_schacht_bewertung.videozaehler,
                Untersuchdat_schacht_bewertung.timecode,
                Untersuchdat_schacht_bewertung.kuerzel,
                Untersuchdat_schacht_bewertung.charakt1,
                Untersuchdat_schacht_bewertung.charakt2,
                Untersuchdat_schacht_bewertung.quantnr1,
                Untersuchdat_schacht_bewertung.quantnr2,
                Untersuchdat_schacht_bewertung.streckenschaden,
                Untersuchdat_schacht_bewertung.Schadenslaenge,
                Untersuchdat_schacht_bewertung.vertikale_lage,
                Untersuchdat_schacht_bewertung.pos_von,
                Untersuchdat_schacht_bewertung.pos_bis,
                Untersuchdat_schacht_bewertung.bereich,
                Untersuchdat_schacht_bewertung.foto_dateiname,
                Untersuchdat_schacht_bewertung.Zustandsklasse_D,
                Untersuchdat_schacht_bewertung.Zustandsklasse_S,
                Untersuchdat_schacht_bewertung.Zustandsklasse_B,
                Untersuchdat_schacht_bewertung.createdat,
                
                schaechte_untersucht_bewertung.schnam,
                schaechte_untersucht_bewertung.untersuchtag,
                schaechte_untersucht_bewertung.untersucher,
                schaechte_untersucht_bewertung.wetter,
                schaechte_untersucht_bewertung.bewertungsart,
                schaechte_untersucht_bewertung.bewertungstag,
                schaechte_untersucht_bewertung.objektklasse_dichtheit,
                schaechte_untersucht_bewertung.objektklasse_standsicherheit,
                schaechte_untersucht_bewertung.objektklasse_betriebssicherheit,
                schaechte_untersucht_bewertung.objektklasse_gesamt,
                schaechte_untersucht_bewertung.baujahr,
                schaechte_untersucht_bewertung.hydraulische_auslastung,
                schaechte_untersucht_bewertung.lage_grundwasser,
                schaechte_untersucht_bewertung.ueberdeckung,
                schaechte_untersucht_bewertung.bodengruppe,
                schaechte_untersucht_bewertung.createdat,
                Untersuchdat_schacht_bewertung.inspektionslaenge
                FROM Untersuchdat_schacht_bewertung, schaechte_untersucht_bewertung
                WHERE schaechte_untersucht_bewertung.schnam = Untersuchdat_schacht_bewertung.untersuchsch AND substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ? AND substr(schaechte_untersucht_bewertung.createdat, 0, 17) = ? 
                """
        #WHERE schaechte_untersucht_bewertung.schnam = Untersuchdat_schacht_bewertung.untersuchsch AND Untersuchdat_schacht_bewertung.createdat=? AND schaechte_untersucht_bewertung.createdat = Untersuchdat_schacht_bewertung.createdat AND Untersuchdat_schacht_bewertung.streckenschaden='A' OR Untersuchdat_schacht_bewertung.streckenschaden='not found'

        data = (date, date)

        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Sanierungsbedarfszahl der Schächte konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        x = curs.fetchall()
        liste = []
        for attr in x:
            if attr[1] not in liste:

                halt = [y for y in x if y[1] == attr[1]]
                liste.append(attr[1])
                list_zd = []
                list_zs = []
                list_zb = []
                for h in halt:

                    sl = h[11]
                    if sl == NULL or sl == 'not found' or sl =='-':
                        sl = 0
                    else:
                        sl = float(sl)
                    if sl <= 0.5:
                        sl = 0.5
                    else:
                        sl
                    z_dl = h[17]
                    list_zd.append(z_dl)
                    z_sl = h[18]
                    list_zs.append(z_sl)
                    z_bl = h[19]
                    list_zb.append(z_bl)

                z_d = attr[27]
                z_s = attr[28]
                z_b = attr[29]

                zp_0d = 0
                zp_0s = 0
                zp_0b = 0

                if isinstance(z_d, int):
                    if z_d == 0:
                        zp_0d = 400
                    if z_d == 1:
                        zp_0d = 300
                    if z_d == 2:
                        zp_0d = 200
                    if z_d == 3:
                        zp_0d = 100
                    if z_d == 4:
                        zp_0d = 0
                else:
                    z_d = 0

                if isinstance(z_s, int):
                    if z_s == 0:
                        zp_0s = 400
                    if z_s == 1:
                        zp_0s = 300
                    if z_s == 2:
                        zp_0s = 200
                    if z_s == 3:
                        zp_0s = 100
                    if z_s == 4:
                        zp_0s = 0
                else:
                    z_s = 0

                if isinstance(z_b, int):
                    if z_b == 0:
                        zp_0b = 400
                    if z_b == 1:
                        zp_0b = 300
                    if z_b == 2:
                        zp_0b = 200
                    if z_b == 3:
                        zp_0b = 100
                    if z_b == 4:
                        zp_0b = 0
                else:
                    z_b = 0

                list_zd = [s for s in list_zd if s != '-']

                list_zs = [s for s in list_zs if s != '-']

                list_zb = [s for s in list_zb if s != '-']

                if len(list_zd) == 0 and len(list_zs) == 0 and len(list_zb) == 0:
                    continue

                l = attr[37]
                if l == NULL or l == 'not found' or l == '-':
                    l = 0
                else:
                    l = float(l)


                xd = 0
                for i in list_zd:
                    xd += ((5 - int(i)) * sl)


                if ((5 - z_d) * l) == 0:
                    sd_d = 0
                else:
                    sd_d = xd / ((5 - z_d) * attr[37])
                zp_d = 50 * sd_d

                xs = 0
                for i in list_zs:
                    xs += ((5 - int(i)) * sl)

                if ((5 - z_s) * l) == 0:
                    sd_s = 0
                else:
                    sd_s = xs / ((5 - z_s) * attr[37])
                zp_s = 50 * sd_s

                xb = 0
                for i in list_zb:
                    xb += ((5 - int(i)) * sl)

                if ((5 - z_b) * l) == 0:
                    sd_b = 0
                else:
                    sd_b = xb / ((5 - z_b) * attr[37])

                zp_b = 50 * sd_b

                zp_jd = zp_0d + zp_d

                zp_js = zp_0s + zp_s

                zp_jb = zp_0b + zp_b

                # Bewertungsfaktor Fj

                # f_j = sum(r_jk / n_j)

                hydraul = attr[32]
                gw = attr[33]
                boden = attr[34]

                # fuer schacht

                if hydraul == "eingehalten":
                    r_d1 = 0
                else:
                    r_d1 = 1

                if gw == "im Grundwasser":
                    r_d2 = 1
                if gw == "in der Wechselzone":
                    r_d2 = 0.5
                if gw == "oberhalb des Grundwassers" or gw == "kein Grundwasser":
                    r_d2 = 0
                else:
                    r_d2 = 1

                f_d = (r_d1+r_d2)/2

                if boden == "Bodengruppe 1" or boden == "Bodengruppe 2":
                    r_s1 = 0
                if boden == "Bodengruppe 3":
                    r_s1 = 0.5
                if boden == "Bodengruppe 4":
                    r_s1 = 1
                else:
                    r_s1 = 1

                f_s = r_s1

                f_b = 0

                # Bewertungspunkte
                # bp_j=500+zp_j+50*f_j

                bp_d = 500 + zp_jd + 50 * f_d

                bp_s = 500 + zp_js + 50 * f_s

                bp_b = 500 + zp_jb + 50 * f_b

                # Objektklasse
                k = min(z_d, z_s, z_b)

                # bp der größe nach sortieren
                bp = [bp_d, bp_s, bp_b]
                bp_sort = sorted(bp)

                bp_1 = str(int(bp_sort[2]))
                bp_2 = str(int(bp_sort[1]))
                bp_3 = str(int(bp_sort[0]))

                x_1 = int(bp_1[-2:])
                x_2 = int(bp_2[-2:])
                x_3 = int(bp_3[-2:])

                sz = (int(int(bp_1) / 100) * 10 ** 3) + (int(int(bp_2) / 100) * 10 ** 2) + (
                            int(int(bp_3) / 100) * 10) + (int(
                    (x_1 + x_2 + x_3) / 30))
                if sz >= 9000:
                    handlung = 'sofort'
                if 8000 <= sz < 9000:
                    handlung = 'kurzfristig'
                if 7000 <= sz < 8000:
                    handlung = 'mittelfristig'
                if 6000 <= sz < 7000:
                    handlung = 'langfristig'
                if 5000 <= sz < 6000:
                    handlung = 'kein Handlungsbedarf'
                if sz == 0:
                    handlung = 'schadensfrei'

                #sanierungsbedarfszahl in datenbank schreiben
                sql = f"""
                        UPDATE schaechte_untersucht_bewertung
                        SET Sanierungsbedarfszahl = ?, Handlungsbedarf = ?
                        WHERE schaechte_untersucht_bewertung.schnam = ?
                        """
                data = (sz, handlung, attr[21])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('Untersuchdat_schacht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'Untersuchdat_schacht_bewertung'
        geom_column = 'geop'
        uri.setDataSource(schema, table, geom_column)
        Untersuchdat_schacht_bewertung = 'Untersuchdat_schacht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), Untersuchdat_schacht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(Untersuchdat_schacht_bewertung)[0].id())
        except:
            pass

        qmlpath = os.path.join(self.qmlDir, 'res/untersuchdat_schacht_bewertung_dwa.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'untersuchdat_schacht_bewertung_dwa.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'schaechte_untersucht_bewertung'
        geom_column = 'geop'
        uri.setDataSource(schema, table, geom_column)
        schaechte_untersucht_bewertung = 'schaechte_untersucht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), schaechte_untersucht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(schaechte_untersucht_bewertung)[0].id())
        except:
            pass


        qmlpath = os.path.join(self.qmlDir, 'res/schaechte_untersucht_bewertung_dwa.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'schaechte_untersucht_bewertung_dwa.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)

    def systemzahl_isy_haltung(self):
        db = self.db
        date = self.date
        crs = self.crs
        db_x = db
        data = db
        db = spatialite_connect(data)
        curs = db.cursor()
        leitung = self.leitung
        haltung = self.haltung

        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Objektklasse INTEGER ;""")
        except:
            pass

        if haltung == True:
            sql = """
                    SELECT
                        haltungen_untersucht_bewertung.pk,
                        untersuchdat_haltung_bewertung.untersuchhal,
                        untersuchdat_haltung_bewertung.untersuchrichtung,
                        untersuchdat_haltung_bewertung.schoben,
                        untersuchdat_haltung_bewertung.schunten,
                        untersuchdat_haltung_bewertung.id,
                        untersuchdat_haltung_bewertung.videozaehler,
                        untersuchdat_haltung_bewertung.inspektionslaenge,
                        untersuchdat_haltung_bewertung.station,
                        untersuchdat_haltung_bewertung.timecode,
                        untersuchdat_haltung_bewertung.kuerzel,
                        untersuchdat_haltung_bewertung.charakt1,
                        untersuchdat_haltung_bewertung.charakt2,
                        untersuchdat_haltung_bewertung.quantnr1,
                        untersuchdat_haltung_bewertung.quantnr2,
                        untersuchdat_haltung_bewertung.streckenschaden,
                        untersuchdat_haltung_bewertung.Schadenslaenge,
                        untersuchdat_haltung_bewertung.pos_von,
                        untersuchdat_haltung_bewertung.pos_bis,
                        untersuchdat_haltung_bewertung.foto_dateiname,
                        untersuchdat_haltung_bewertung.film_dateiname,
                        untersuchdat_haltung_bewertung.richtung,
                        untersuchdat_haltung_bewertung.bw_bs,
                        untersuchdat_haltung_bewertung.createdat,
                        untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_D,
                        untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_S,
                        untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_B,
                        
                        haltungen_untersucht_bewertung.haltnam,
                        haltungen_untersucht_bewertung.laenge,
                        haltungen_untersucht_bewertung.untersuchtag,
                        haltungen_untersucht_bewertung.untersucher,
                        haltungen_untersucht_bewertung.wetter,
                        haltungen_untersucht_bewertung.bewertungsart,
                        haltungen_untersucht_bewertung.bewertungstag,
                        haltungen_untersucht_bewertung.Entwaesserungssystem,
                        haltungen_untersucht_bewertung.Abwasserart,
                        haltungen_untersucht_bewertung.Wasserschutzzone,
                        haltungen_untersucht_bewertung.Grundwasserabstand,
                        haltungen_untersucht_bewertung.Bodenart,
                        haltungen_untersucht_bewertung.Lage_am_Umfang,
                        haltungen_untersucht_bewertung.Lage_an_Bauteilverbindung,
                        haltungen_untersucht_bewertung.createdat,
                        haltungen.haltnam
                    FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, haltungen
                    WHERE haltungen.haltnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ? AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? 
                """
            data = (date, date)

        if leitung == True:
            sql = """
                    SELECT
                        haltungen_untersucht_bewertung.pk,
                        untersuchdat_haltung_bewertung.untersuchhal,
                        untersuchdat_haltung_bewertung.untersuchrichtung,
                        untersuchdat_haltung_bewertung.schoben,
                        untersuchdat_haltung_bewertung.schunten,
                        untersuchdat_haltung_bewertung.id,
                        untersuchdat_haltung_bewertung.videozaehler,
                        untersuchdat_haltung_bewertung.inspektionslaenge,
                        untersuchdat_haltung_bewertung.station,
                        untersuchdat_haltung_bewertung.timecode,
                        untersuchdat_haltung_bewertung.kuerzel,
                        untersuchdat_haltung_bewertung.charakt1,
                        untersuchdat_haltung_bewertung.charakt2,
                        untersuchdat_haltung_bewertung.quantnr1,
                        untersuchdat_haltung_bewertung.quantnr2,
                        untersuchdat_haltung_bewertung.streckenschaden,
                        untersuchdat_haltung_bewertung.Schadenslaenge,
                        untersuchdat_haltung_bewertung.pos_von,
                        untersuchdat_haltung_bewertung.pos_bis,
                        untersuchdat_haltung_bewertung.foto_dateiname,
                        untersuchdat_haltung_bewertung.film_dateiname,
                        untersuchdat_haltung_bewertung.richtung,
                        untersuchdat_haltung_bewertung.bw_bs,
                        untersuchdat_haltung_bewertung.createdat,
                        untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_D,
                        untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_S,
                        untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_B,

                        haltungen_untersucht_bewertung.haltnam,
                        haltungen_untersucht_bewertung.laenge,
                        haltungen_untersucht_bewertung.untersuchtag,
                        haltungen_untersucht_bewertung.untersucher,
                        haltungen_untersucht_bewertung.wetter,
                        haltungen_untersucht_bewertung.bewertungsart,
                        haltungen_untersucht_bewertung.bewertungstag,
                        haltungen_untersucht_bewertung.Entwaesserungssystem,
                        haltungen_untersucht_bewertung.Abwasserart,
                        haltungen_untersucht_bewertung.Wasserschutzzone,
                        haltungen_untersucht_bewertung.Grundwasserabstand,
                        haltungen_untersucht_bewertung.Bodenart,
                        haltungen_untersucht_bewertung.Lage_am_Umfang,
                        haltungen_untersucht_bewertung.Lage_an_Bauteilverbindung,
                        haltungen_untersucht_bewertung.createdat,
                        anschlussleitungen.leitnam
                    FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, anschlussleitungen
                    WHERE anschlussleitungen.leitnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ? AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? 
                """
            data = (date, date)

        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Systemzahl der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        x = curs.fetchall()
        liste = []
        for attr in x:
            if attr[1] not in liste:
                halt = [y for y in x if y[1] == attr[1]]
                liste.append(attr[1])
                list_sze = []
                list_sze_dl = []
                list_okl = []
                for h in halt:

                    sl = h[16]
                    if sl == NULL or sl == 'not found':
                        sl = 0.3
                    else:
                        sl = float(sl)
                    if sl <= 1:
                        sl = 1
                    else:
                        sl

                    sz_d = h[24]
                    sz_s = h[25]
                    sz_b = h[26]


                    entwaesserungssystem = h[34]
                    abwasser = h[35]
                    wasserschutzzone = h[36]
                    gw_abstand = h[37]
                    boden = h[38]
                    lage_umfang = h[39]
                    lage_an_verbindung = h[40]

                    zd1 = 0
                    zd2 = 0
                    zd3 = 0
                    zd4 = 0
                    zd5 = 0
                    zd6 = 0
                    zd7 = 0
                    zs1 = 0
                    zs2 = 0
                    zs3 = 0
                    zb1 = 0
                    zb2 = 0

                    if entwaesserungssystem == "Fließgewässer kanalisiert":
                        zd1=-50
                        zb1=0
                    if entwaesserungssystem == "Regenwasser":
                        zd1=-30
                        zb1=0
                    if entwaesserungssystem == "Schmutzwasser":
                        zd1=30
                        zb1=40
                    if entwaesserungssystem == "Mischwasser":
                        zd1=30
                        zb1=40


                    if abwasser == "Wassergefährdende Stoffe":
                        zd2=150


                    if wasserschutzzone == "außerhalb einer Wasserschutzzone":
                        zd3=0
                    if wasserschutzzone == "Schutzzone IIIb":
                        zd3=20
                    if wasserschutzzone == "Schutzzone IIIa":
                        zd3=40
                    if wasserschutzzone == "Schutzzone II":
                        zd3=250
                    if wasserschutzzone == "Schutzzone I":
                        zd3=400


                    if gw_abstand == "Gerinne oberhalb des Grundwasserleiters":
                        zd4=0
                        zs1=0
                    if gw_abstand == "Gerinne in der Wechselzone":
                        zd4=10
                        zs1=10
                    if gw_abstand == "Gerinne im Grundwasserleiter":
                        zd4=10
                        zs1=10


                    if boden == "Lehm, Ton":
                        zd5=0
                        zs2=40
                    if boden == "Sandiger Lehm, Löss, Lehmiger Sand, Feinsand":
                        zd5=15
                        zs2=20
                    if boden == "Mittel-, Grobsand, Kies":
                        zd5=30
                        zs2=0

                    if lage_umfang == "03 bis 09 Uhr":
                        zd6=10
                        zs3=0
                        zb2=20
                    if lage_umfang == "09 bis 03 Uhr":
                        zd6=0
                        zs3=10
                        zb2=0
                    if lage_umfang == "Gesamter Umfang":
                        zd6=10
                        zs3=20
                        zb2=20


                    if lage_an_verbindung == "Ja":
                        zd7=10
                    if lage_an_verbindung == "Nein":
                        zd7=0


                    if sz_d == NULL or sz_d == 'not found' or sz_d == '-':
                        sze_d = 0
                    else:
                        sze_d = sz_d + zd1 + zd2 + zd3 + zd4 + zd5 + zd6 + zd7

                    if sz_s == NULL or sz_s == 'not found' or sz_s == '-':
                        sze_s = 0
                    else:
                        sze_s = sz_s + zs1 + zs2 + zs3

                    if sz_b == NULL or sz_b == 'not found' or sz_b == '-':
                        sze_b = 0
                    else:
                        sze_b = sz_b + zb1 + zb2

                    sze = max(sze_d, sze_s, sze_b)

                    if isinstance(sze_d, int):
                        if sze_d >=10 and sze_d<=99:
                            skd=1
                        if sze_d >=100 and sze_d<=199:
                            skd=2
                        if sze_d >=200 and sze_d<=299:
                            skd=3
                        if sze_d >=300 and sze_d<=399:
                            skd=4
                        if sze_d >=400:
                            skd=5
                    else:
                        skd=0

                    if isinstance(sze_s, int):
                        if sze_s >=10 and sze_s<=99:
                            sks=1
                        if sze_s >=100 and sze_s<=199:
                            sks=2
                        if sze_s >=200 and sze_s<=299:
                            sks=3
                        if sze_s >=300 and sze_s<=399:
                            sks=4
                        if sze_s >=400:
                            sks=5
                    else:
                        sks=0

                    if isinstance(sze_b, int):
                        if sze_b >=10 and sze_b<=99:
                            skb=1
                        if sze_b >=100 and sze_b<=199:
                            skb=2
                        if sze_b >=200 and sze_b<=299:
                            skb=3
                        if sze_b >=300 and sze_b<=399:
                            skb=4
                        if sze_b >=400:
                            skb=5
                    else:
                        skb=0

                    list_sze.append(sze)
                    szed= sze*sl

                    list_sze_dl.append(szed)


                slz = sum(list_sze_dl)

                oz_v = max(list_sze)

                if attr[7] == NULL:
                    h1 = attr[28]
                else:
                    hl = attr[7]

                if (oz_v*hl) ==0:
                    sl =0
                else:
                    if (slz/(oz_v*hl))<= 0.1:
                        sl = 0
                    if 0.1<(slz/(oz_v*hl))<=0.5:
                        sl = (slz/(oz_v*hl))*100-10
                    if (slz/(oz_v*hl))>0.5:
                        sl = 40

                oz_e = oz_v +sl

                if oz_e == 0:
                    ok = 0
                if oz_e >= 10 and oz_e <= 99:
                    ok = 1
                if oz_e >= 100 and oz_e <= 199:
                    ok = 2
                if oz_e >= 200 and oz_e <= 299:
                    ok = 3
                if oz_e >= 300 and oz_e <= 399:
                    ok = 4
                if oz_e >= 400:
                    ok = 5

                okl = ok * attr[28]

                sql = f"""
                        UPDATE haltungen_untersucht_bewertung
                        SET Objektklasse = ?
                        WHERE haltungen_untersucht_bewertung.pk = ?
                        """
                data = (ok, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass

                list_okl.append(okl)
                l=0
                l+=attr[28]

        #ganzes system (systemzahl)
        syl = 1/l*sum(list_okl)

        iface.messageBar().pushMessage("Info", "Die Systemzahl der Haltungen/Leitungen beträgt {}".format(syl),
                                       level=Qgis.Info)

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        untersuchdat_haltung_bewertung = 'untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        qmlpath = os.path.join(self.qmlDir, 'res/untersuchdat_haltung_bewertung_isy.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'untersuchdat_haltung_bewertung_isy.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'haltungen_untersucht_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        haltungen_untersucht_bewertung = 'haltungen_untersucht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), haltungen_untersucht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(haltungen_untersucht_bewertung)[0].id())
        except:
            pass


        qmlpath = os.path.join(self.qmlDir, 'res/haltungen_untersucht_bewertung_isy.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'haltungen_untersucht_bewertung_isy.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)


    def systemzahl_isy_schacht(self):
        db = self.db
        date = self.date
        crs = self.crs
        db_x = db
        data = db
        db = spatialite_connect(data)
        curs = db.cursor()

        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Objektklasse INTEGER ;""")
        except:
            pass


        sql = """
                SELECT
                    schaechte_untersucht_bewertung.pk,
                    Untersuchdat_schacht_bewertung.untersuchsch,
                    Untersuchdat_schacht_bewertung.id,
                    Untersuchdat_schacht_bewertung.videozaehler,
                    Untersuchdat_schacht_bewertung.timecode,
                    Untersuchdat_schacht_bewertung.kuerzel,
                    Untersuchdat_schacht_bewertung.charakt1,
                    Untersuchdat_schacht_bewertung.charakt2,
                    Untersuchdat_schacht_bewertung.quantnr1,
                    Untersuchdat_schacht_bewertung.quantnr2,
                    Untersuchdat_schacht_bewertung.streckenschaden,
                    Untersuchdat_schacht_bewertung.Schadenslaenge,
                    Untersuchdat_schacht_bewertung.vertikale_lage,
                    Untersuchdat_schacht_bewertung.pos_von,
                    Untersuchdat_schacht_bewertung.pos_bis,
                    Untersuchdat_schacht_bewertung.bereich,
                    Untersuchdat_schacht_bewertung.foto_dateiname,
                    Untersuchdat_schacht_bewertung.ordner,
                    Untersuchdat_schacht_bewertung.bw_bs,
                    Untersuchdat_schacht_bewertung.createdat,
                    Untersuchdat_schacht_bewertung.vorlaufige_Schadenszahl_D,
                    Untersuchdat_schacht_bewertung.vorlaufige_Schadenszahl_S,
                    Untersuchdat_schacht_bewertung.vorlaufige_Schadenszahl_B,

                    schaechte_untersucht_bewertung.schnam,
                    schaechte_untersucht_bewertung.untersuchtag,
                    schaechte_untersucht_bewertung.untersucher,
                    schaechte_untersucht_bewertung.wetter,
                    schaechte_untersucht_bewertung.bewertungsart,
                    schaechte_untersucht_bewertung.bewertungstag,
                    schaechte_untersucht_bewertung.Entwaesserungssystem,
                    schaechte_untersucht_bewertung.Abwasserart,
                    schaechte_untersucht_bewertung.Wasserschutzzone,
                    schaechte_untersucht_bewertung.Grundwasserabstand,
                    schaechte_untersucht_bewertung.Bodenart,
                    schaechte_untersucht_bewertung.Lage_an_Bauteilverbindung,
                    schaechte_untersucht_bewertung.createdat,
                    Untersuchdat_schacht_bewertung.inspektionslaenge
                FROM Untersuchdat_schacht_bewertung, schaechte_untersucht_bewertung
                WHERE schaechte_untersucht_bewertung.schnam = Untersuchdat_schacht_bewertung.untersuchsch AND substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ? AND substr(schaechte_untersucht_bewertung.createdat, 0, 17) = ?
            """
        data = (date, date)

        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Systemzahl der Schächte konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        x = curs.fetchall()
        liste = []
        for attr in x:
            if attr[1] not in liste:
                halt = [y for y in x if y[1] == attr[1]]
                liste.append(attr[1])
                list_sze = []
                list_sze_dl = []
                list_okl = []
                for h in halt:

                    sl = h[12]
                    if sl == NULL or sl == 'not found':
                        sl = 0.5
                    else:
                        sl = float(sl)
                    if sl <= 0.5:
                        sl = 0.5
                    else:
                        sl

                    sz_d = h[20]
                    sz_s = h[21]
                    sz_b = h[22]

                    # für jeden schaden

                    entwaesserungssystem = h[29]
                    abwasser = h[30]
                    wasserschutzzone = h[31]
                    gw_abstand = h[32]
                    boden = h[33]
                    lage_an_verbindung = h[34]

                    zd1 = 0
                    zd2 = 0
                    zd3 = 0
                    zd4 = 0
                    zd5 = 0
                    zd6 = 0
                    zd7 = 0
                    zs1 = 0
                    zs2 = 0
                    zs3 = 0
                    zb1 = 0
                    zb2 = 0

                    if entwaesserungssystem == "Fließgewässer kanalisiert":
                        zd1 = -50
                        zb1 = 0
                    if entwaesserungssystem == "Regenwasser":
                        zd1 = -30
                        zb1 = 0
                    if entwaesserungssystem == "Schmutzwasser":
                        zd1 = 30
                        zb1 = 40
                    if entwaesserungssystem == "Mischwasser":
                        zd1 = 30
                        zb1 = 40

                    if abwasser == "Wassergefährdende Stoffe":
                        zd2 = 150

                    if wasserschutzzone == "außerhalb einer Wasserschutzzone":
                        zd3 = 0
                    if wasserschutzzone == "Schutzzone IIIb":
                        zd3 = 20
                    if wasserschutzzone == "Schutzzone IIIa":
                        zd3 = 40
                    if wasserschutzzone == "Schutzzone II":
                        zd3 = 250
                    if wasserschutzzone == "Schutzzone I":
                        zd3 = 400

                    if gw_abstand == "Gerinne oberhalb des Grundwasserleiters":
                        zd4 = 0
                        zs1 = 0
                    if gw_abstand == "Gerinne in der Wechselzone":
                        zd4 = 10
                        zs1 = 10
                    if gw_abstand == "Gerinne im Grundwasserleiter":
                        zd4 = 10
                        zs1 = 10

                    if boden == "Lehm, Ton":
                        zd5 = 0
                        zs2 = 40
                    if boden == "Sandiger Lehm, Löss, Lehmiger Sand, Feinsand":
                        zd5 = 15
                        zs2 = 20
                    if boden == "Mittel-, Grobsand, Kies":
                        zd5 = 30
                        zs2 = 0

                    if lage_an_verbindung == "Ja":
                        zd7 = 10
                    if lage_an_verbindung == "Nein":
                        zd7 = 0

                    if sz_d == NULL or sz_d == 'not found' or sz_d == '-':
                        sze_d = 0
                    else:
                        sze_d = sz_d + zd1 + zd2 + zd3 + zd4 + zd5 + zd6 + zd7

                    if sz_s == NULL or sz_s == 'not found' or sz_s == '-':
                        sze_s = 0
                    else:
                        sze_s = sz_s + zs1 + zs2 + zs3

                    if sz_b == NULL or sz_b == 'not found' or sz_b == '-':
                        sze_b = 0
                    else:
                        sze_b = sz_b + zb1 + zb2

                    sze = max(sze_d, sze_s, sze_b)


                    if isinstance(sze_d, int):
                        if sze_d >=10 and sze_d<=99:
                            skd=1
                        if sze_d >=100 and sze_d<=199:
                            skd=2
                        if sze_d >=200 and sze_d<=299:
                            skd=3
                        if sze_d >=300 and sze_d<=399:
                            skd=4
                        if sze_d >=400:
                            skd=5
                    else:
                        skd=0

                    if isinstance(sze_s, int):
                        if sze_s >=10 and sze_s<=99:
                            sks=1
                        if sze_s >=100 and sze_s<=199:
                            sks=2
                        if sze_s >=200 and sze_s<=299:
                            sks=3
                        if sze_s >=300 and sze_s<=399:
                            sks=4
                        if sze_s >=400:
                            sks=5
                    else:
                        sks=0

                    if isinstance(sze_b, int):
                        if sze_b >=10 and sze_b<=99:
                            skb=1
                        if sze_b >=100 and sze_b<=199:
                            skb=2
                        if sze_b >=200 and sze_b<=299:
                            skb=3
                        if sze_b >=300 and sze_b<=399:
                            skb=4
                        if sze_b >=400:
                            skb=5
                    else:
                        skb=0



                    list_sze.append(sze)
                    szed = sze * sl

                    list_sze_dl.append(szed)

                slz = sum(list_sze_dl)

                oz_v = max(list_sze)

                hl = attr[36]
                if hl == NULL or hl == 'not found':
                    hl = 0
                else:
                    hl = float(hl)

                if (oz_v * hl) == 0:
                    sl = 0
                else:
                    if (slz / (oz_v * hl)) <= 0.1:
                        sl = 0
                    if 0.1 < (slz / (oz_v * hl)) <= 0.5:
                        sl = (slz / (oz_v * hl)) * 100 - 10
                    if (slz / (oz_v * hl)) > 0.5:
                        sl = 40

                oz_e = oz_v + sl

                if oz_e == 0:
                    ok = 0
                if oz_e >= 10 and oz_e <= 99:
                    ok = 1
                if oz_e >= 100 and oz_e <= 199:
                    ok = 2
                if oz_e >= 200 and oz_e <= 299:
                    ok = 3
                if oz_e >= 300 and oz_e <= 399:
                    ok = 4
                if oz_e >= 400:
                    ok = 5

                okl = ok * attr[27]

                sql = f"""
                                UPDATE schaechte_untersucht_bewertung
                                SET Objektklasse = ?
                                WHERE schaechte_untersucht_bewertung.pk = ?
                                """
                data = (ok, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass

                list_okl.append(okl)
                l=0
                l += attr[12]

            # ganzes system (systemzahl)
        if (l * sum(list_okl)) == 0:
            syl = 0
        else:
            syl = 1 / l * sum(list_okl)

        iface.messageBar().pushMessage("Info", "Die Systemzahl der Schächte beträgt {}".format(syl), level=Qgis.Info)

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('Untersuchdat_schacht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'Untersuchdat_schacht_bewertung'
        geom_column = 'geop'
        uri.setDataSource(schema, table, geom_column)
        Untersuchdat_schacht_bewertung = 'Untersuchdat_schacht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), Untersuchdat_schacht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(Untersuchdat_schacht_bewertung)[0].id())
        except:
            pass


        qmlpath = os.path.join(self.qmlDir, 'res/untersuchdat_schacht_bewertung_isy.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'untersuchdat_schacht_bewertung_isy.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'schaechte_untersucht_bewertung'
        geom_column = 'geop'
        uri.setDataSource(schema, table, geom_column)
        schaechte_untersucht_bewertung = 'schaechte_untersucht_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), schaechte_untersucht_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(schaechte_untersucht_bewertung)[0].id())
        except:
            pass

        qmlpath = os.path.join(self.qmlDir, 'res/schaechte_untersucht_bewertung_isy.qml')
        vlayer.loadNamedStyle(qmlpath)
        # Adapt path to forms directory
        editFormConfig = vlayer.editFormConfig()
        editFormConfig.setUiForm(os.path.join(self.formsDir, 'schaechte_untersucht_bewertung_isy.ui'))
        vlayer.setEditFormConfig(editFormConfig)
        QgsProject.instance().addMapLayer(vlayer)

    def atlas(self):
        mass =  self.massstab
        format = self.format
        atlas_path = self.atlas_path
        db = self.db
        date = self.date
        data = db
        db_x = data
        crs = self.crs

        db = spatialite_connect(data)
        curs = db.cursor()
        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'haltungen'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        haltungen = 'haltungen'
        layer = QgsVectorLayer(uri.uri(), haltungen, 'spatialite')
        ext = layer.extent()
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()

        if format == 'A0':
            b_layout = 993 / 1000
            h_layout = 831 / 1000
        if format == 'A1':
            b_layout = 645 / 1000
            h_layout = 583 / 1000
        if format == 'A2':
            b_layout = 398 / 1000
            h_layout = 409 / 1000
        if format == 'A3':
            b_layout = 224 / 1000
            h_layout = 286 / 1000

        x_li = xmin
        x_re = xmax

        b = x_re - x_li
        b_ges = math.ceil(b)

        b_u = 5

        b_r = b_layout * mass

        n_x = (b_ges - b_u) / (b_r - b_u)

        anz_x = math.ceil(n_x)

        b_rest = (anz_x - n_x) * (b_r - b_u)

        x_1 = math.floor(x_li - (b_rest / 2))

        xm = x_1 + b_r / 2

        y_un = ymin
        y_ob = ymax

        h = y_ob - y_un
        h_ges = math.ceil(h)

        h_u = 5

        h_r = h_layout * mass
        n_y = (h_ges - h_u) / (h_r - h_u)

        anz_y = math.ceil(n_y)

        h_rest = (anz_y - n_y) * (h_r - h_u)

        y_1 = math.floor(y_un - (h_rest / 2))

        ym = y_1 + h_r / 2

        dx = b_r - b_u

        dy = h_r - h_u

        j = 0
        points = []
        while j < anz_y:
            j += 1
            i = 0
            xm_x = xm
            while i < anz_x:
                i += 1
                points.append((xm_x, ym))
                xm_x = xm_x + dx
            ym = ym + dy


        layerFields = QgsFields()
        writer = QgsVectorFileWriter(atlas_path, 'UTF-8', layerFields, QgsWkbTypes.Point,
                                     QgsCoordinateReferenceSystem(crs), 'ESRI Shapefile')

        for i in points:
            # liste mit allen punkten!!!
            x = i[0]
            y = i[1]
            point = QgsPointXY(x, y)

            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(point))
            writer.addFeature(feat)
        layer.updateExtents()
        layer = iface.addVectorLayer(atlas_path, '', 'ogr')

        del (writer)

    def plan(self):
        format = self.format
        mass = self.massstab
        base_path = self.speicher
        atlas_path = self.atlas_path


        projectInstance = QgsProject.instance()
        layoutmanager = projectInstance.layoutManager()
        layout = layoutmanager.layoutByName(format)

        map = layout.itemById('Karte 1')
        map.setScale(mass)
        map.setAtlasDriven(True)
        layout.addLayoutItem(map)
        atlas = QgsLayoutAtlas(layout)
        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(layout.itemById('Karte 1'))
        legend.setLegendFilterOutAtlas(True)
        legend.refresh()
        legend.setLegendFilterByMapEnabled(True)

        vlayer = QgsVectorLayer(atlas_path, "atlas", "ogr")
        atlas.setCoverageLayer(vlayer)
        atlas.filterExpression()
        atlas.setSortExpression('FID')

        my_atlas = layout.atlas()
        my_atlas.setCoverageLayer(vlayer)
        my_atlas.setEnabled(True)
        my_atlas.setHideCoverage(True)
        my_atlas.beginRender()
        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        pdf_settings.forceVectorOutput = True
        pdf_settings.exportMetadata = True
        pdf_settings.rasterizeWholeImage = False
        pdf_settings.appendGeoreference = False
        pdf_settings.textRenderFormat = QgsRenderContext.TextFormatAlwaysOutlines
        while my_atlas.next():
            pdfpath = os.path.join(base_path, my_atlas.currentFilename() + ".pdf")
            atlas_layout = my_atlas.layout()
            exporter = QgsLayoutExporter(atlas_layout)
            exporter.exportToPdf(pdfpath, pdf_settings)


    def excel_haltungen(self):
        excel_speicher = self.excel_speicher
        excel_format = self.excel_format
        db_format = self.db_format
        pfad = excel_speicher
        file = os.path.join(pfad, "haltungen.xlsx")

        data = self.db
        date = self.date

        db = sqlite3.connect(data)
        curs = db.cursor()

        if db_format == "Datenbank mit DWA-M 149 Daten":

            sql = """
                SELECT
                    untersuchdat_haltung_bewertung.pk,
                    untersuchdat_haltung_bewertung.id,
                    untersuchdat_haltung_bewertung.untersuchhal,
                    untersuchdat_haltung_bewertung.schoben,
                    untersuchdat_haltung_bewertung.schunten,
                    haltungen.material,
                    untersuchdat_haltung_bewertung.untersuchrichtung,
                    untersuchdat_haltung_bewertung.inspektionslaenge,
                    untersuchdat_haltung_bewertung.videozaehler,
                    untersuchdat_haltung_bewertung.timecode,
                    untersuchdat_haltung_bewertung.station,
                    untersuchdat_haltung_bewertung.kuerzel,
                    untersuchdat_haltung_bewertung.charakt1,
                    untersuchdat_haltung_bewertung.charakt2,
                    untersuchdat_haltung_bewertung.quantnr1,
                    untersuchdat_haltung_bewertung.quantnr2,
                    untersuchdat_haltung_bewertung.streckenschaden,
                    untersuchdat_haltung_bewertung.streckenschaden_lfdnr,
                    untersuchdat_haltung_bewertung.pos_von,
                    untersuchdat_haltung_bewertung.pos_bis,
                    untersuchdat_haltung_bewertung.Zustandsklasse_D,
                    untersuchdat_haltung_bewertung.Zustandsklasse_S,
                    untersuchdat_haltung_bewertung.Zustandsklasse_B,
                    untersuchdat_haltung_bewertung.Schadenslaenge,
                    untersuchdat_haltung_bewertung.bw_bs,
                    untersuchdat_haltung_bewertung.createdat,
                    untersuchdat_haltung_bewertung.foto_dateiname,
                    untersuchdat_haltung_bewertung.film_dateiname,
    
                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.hoehe,
                    haltungen_untersucht_bewertung.breite,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.baujahr,
                    haltungen_untersucht_bewertung.hydraulische_auslastung,
                    haltungen_untersucht_bewertung.lage_grundwasser,
                    haltungen_untersucht_bewertung.ueberdeckung,
                    haltungen_untersucht_bewertung.bodengruppe,
                    haltungen_untersucht_bewertung.objektklasse_dichtheit,
                    haltungen_untersucht_bewertung.objektklasse_standsicherheit,
                    haltungen_untersucht_bewertung.objektklasse_betriebssicherheit,
                    haltungen_untersucht_bewertung.objektklasse_gesamt,
                    haltungen_untersucht_bewertung.Sanierungsbedarfszahl,
                    haltungen_untersucht_bewertung.Handlungsbedarf,
                    haltungen_untersucht_bewertung.createdat,
                    haltungen.haltnam
                FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, haltungen
                WHERE haltungen.haltnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ?
                """

        if db_format == "Datenbank mit ISYBAU Daten":
            sql = """
                SELECT
                    untersuchdat_haltung_bewertung.pk,
                    untersuchdat_haltung_bewertung.id,
                    untersuchdat_haltung_bewertung.untersuchhal,
                    untersuchdat_haltung_bewertung.schoben,
                    untersuchdat_haltung_bewertung.schunten,
                    haltungen.material,
                    untersuchdat_haltung_bewertung.untersuchrichtung,
                    untersuchdat_haltung_bewertung.inspektionslaenge,
                    untersuchdat_haltung_bewertung.videozaehler,
                    untersuchdat_haltung_bewertung.timecode,
                    untersuchdat_haltung_bewertung.station,
                    untersuchdat_haltung_bewertung.kuerzel,
                    untersuchdat_haltung_bewertung.charakt1,
                    untersuchdat_haltung_bewertung.charakt2,
                    untersuchdat_haltung_bewertung.quantnr1,
                    untersuchdat_haltung_bewertung.quantnr2,
                    untersuchdat_haltung_bewertung.streckenschaden,
                    untersuchdat_haltung_bewertung.streckenschaden_lfdnr,
                    untersuchdat_haltung_bewertung.pos_von,
                    untersuchdat_haltung_bewertung.pos_bis,
                    untersuchdat_haltung_bewertung.Schadensklasse_D,
                    untersuchdat_haltung_bewertung.Schadensklasse_S,
                    untersuchdat_haltung_bewertung.Schadensklasse_B,
                    untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_D,
                    untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_S,
                    untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_B,
                    untersuchdat_haltung_bewertung.Schadenslaenge,
                    untersuchdat_haltung_bewertung.bw_bs,
                    untersuchdat_haltung_bewertung.createdat,
                    untersuchdat_haltung_bewertung.foto_dateiname,
                    untersuchdat_haltung_bewertung.film_dateiname,

                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.hoehe,
                    haltungen_untersucht_bewertung.breite,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.baujahr,
                    haltungen_untersucht_bewertung.Entwaesserungssystem,
                    haltungen_untersucht_bewertung.Abwasserart,
                    haltungen_untersucht_bewertung.Wasserschutzzone,
                    haltungen_untersucht_bewertung.Grundwasserabstand,
                    haltungen_untersucht_bewertung.Bodenart,
                    haltungen_untersucht_bewertung.Lage_am_Umfang,
                    haltungen_untersucht_bewertung.Lage_an_Bauteilverbindung,
                    haltungen_untersucht_bewertung.Objektklasse,
                    haltungen_untersucht_bewertung.createdat,
                    haltungen.haltnam
                FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, haltungen
                WHERE haltungen.haltnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ?
                """


        if excel_format == 'Alle Daten in ein Excel Tabellenblatt':

            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            try:
                dft = pd.read_sql(sql, db, params=(date, date))
            except:
                iface.messageBar().pushMessage("Error",
                                               "Die Excel Tabelle der Haltungen konnte nicht erstellt werden",
                                               level=Qgis.Critical)
                return



            dft.to_excel(writer, sheet_name="Haltungen", index=False)
            writer.save()

            df = pd.read_excel(file, decimal=',')

            df_styled = df.style.apply(lambda x: ["background-color: blue" if x == 1 else "background-color: white" for x in df.id])

            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            df_styled.to_excel(writer, sheet_name="Haltungen", index=False)
            writer.save()

        if excel_format == 'Für jede Haltung/Schacht ein eigenes Excel Tabellenblatt':

            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            try:
                dft = pd.read_sql(sql, db,  params=(date, date))
            except:
                iface.messageBar().pushMessage("Error",
                                               "Die Excel Tabelle der Haltungen konnte nicht erstellt werden",
                                               level=Qgis.Critical)
                return

            for table_name in dft['untersuchhal']:
                sheet_name = table_name

                sql = "select *  FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, haltungen WHERE haltungen.haltnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = '" + sheet_name + "' AND untersuchdat_haltung_bewertung.untersuchhal = '" + sheet_name +"' AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17)= '" + date +"' AND substr(haltungen_untersucht_bewertung.createdat, 0, 17)= '" + date +"'"

                dft = pd.read_sql(sql, db)

                dft.to_excel(writer, sheet_name=sheet_name, index=False)

                writer.save()

                df = pd.read_excel(file, decimal=',')

                df_styled = df.style.apply(
                    lambda x: ["background-color: blue" if x == 1 else "background-color: white" for x in df.id])

                writer = pd.ExcelWriter(file, engine='xlsxwriter')

                df_styled.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()

        else:
            pass

    def excel_leitungen(self):
        excel_speicher = self.excel_speicher
        excel_format = self.excel_format
        db_format = self.db_format
        pfad = excel_speicher
        file = os.path.join(pfad, "leitungen.xlsx")

        data = self.db
        date = self.date

        db = sqlite3.connect(data)
        curs = db.cursor()

        if db_format == "Datenbank mit DWA-M 149 Daten":
            sql = """
                SELECT
                    untersuchdat_haltung_bewertung.pk,
                    untersuchdat_haltung_bewertung.id,
                    untersuchdat_haltung_bewertung.untersuchhal,
                    untersuchdat_haltung_bewertung.schoben,
                    untersuchdat_haltung_bewertung.schunten,
                    anschlussleitungen.material,
                    untersuchdat_haltung_bewertung.untersuchrichtung,
                    untersuchdat_haltung_bewertung.inspektionslaenge,
                    untersuchdat_haltung_bewertung.videozaehler,
                    untersuchdat_haltung_bewertung.timecode,
                    untersuchdat_haltung_bewertung.station,
                    untersuchdat_haltung_bewertung.kuerzel,
                    untersuchdat_haltung_bewertung.charakt1,
                    untersuchdat_haltung_bewertung.charakt2,
                    untersuchdat_haltung_bewertung.quantnr1,
                    untersuchdat_haltung_bewertung.quantnr2,
                    untersuchdat_haltung_bewertung.streckenschaden,
                    untersuchdat_haltung_bewertung.streckenschaden_lfdnr,
                    untersuchdat_haltung_bewertung.pos_von,
                    untersuchdat_haltung_bewertung.pos_bis,
                    untersuchdat_haltung_bewertung.Zustandsklasse_D,
                    untersuchdat_haltung_bewertung.Zustandsklasse_S,
                    untersuchdat_haltung_bewertung.Zustandsklasse_B,
                    untersuchdat_haltung_bewertung.Schadenslaenge,
                    untersuchdat_haltung_bewertung.bw_bs,
                    untersuchdat_haltung_bewertung.createdat,
                    untersuchdat_haltung_bewertung.foto_dateiname,
                    untersuchdat_haltung_bewertung.film_dateiname,

                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.hoehe,
                    haltungen_untersucht_bewertung.breite,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.baujahr,
                    haltungen_untersucht_bewertung.hydraulische_auslastung,
                    haltungen_untersucht_bewertung.lage_grundwasser,
                    haltungen_untersucht_bewertung.ueberdeckung,
                    haltungen_untersucht_bewertung.bodengruppe,
                    haltungen_untersucht_bewertung.objektklasse_dichtheit,
                    haltungen_untersucht_bewertung.objektklasse_standsicherheit,
                    haltungen_untersucht_bewertung.objektklasse_betriebssicherheit,
                    haltungen_untersucht_bewertung.objektklasse_gesamt,
                    haltungen_untersucht_bewertung.Sanierungsbedarfszahl,
                    haltungen_untersucht_bewertung.Handlungsbedarf,
                    haltungen_untersucht_bewertung.createdat,
                    anschlussleitungen.leitnam
                    FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, anschlussleitungen
                    WHERE anschlussleitungen.leitnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ?
                    """

        if db_format == "Datenbank mit ISYBAU Daten":
            sql = """
                SELECT
                    untersuchdat_haltung_bewertung.pk,
                    untersuchdat_haltung_bewertung.id,
                    untersuchdat_haltung_bewertung.untersuchhal,
                    untersuchdat_haltung_bewertung.schoben,
                    untersuchdat_haltung_bewertung.schunten,
                    anschlussleitungen.material,
                    untersuchdat_haltung_bewertung.untersuchrichtung,
                    untersuchdat_haltung_bewertung.inspektionslaenge,
                    untersuchdat_haltung_bewertung.videozaehler,
                    untersuchdat_haltung_bewertung.timecode,
                    untersuchdat_haltung_bewertung.station,
                    untersuchdat_haltung_bewertung.kuerzel,
                    untersuchdat_haltung_bewertung.charakt1,
                    untersuchdat_haltung_bewertung.charakt2,
                    untersuchdat_haltung_bewertung.quantnr1,
                    untersuchdat_haltung_bewertung.quantnr2,
                    untersuchdat_haltung_bewertung.streckenschaden,
                    untersuchdat_haltung_bewertung.streckenschaden_lfdnr,
                    untersuchdat_haltung_bewertung.pos_von,
                    untersuchdat_haltung_bewertung.pos_bis,
                    untersuchdat_haltung_bewertung.Schadensklasse_D,
                    untersuchdat_haltung_bewertung.Schadensklasse_S,
                    untersuchdat_haltung_bewertung.Schadensklasse_B,
                    untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_D,
                    untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_S,
                    untersuchdat_haltung_bewertung.vorlaufige_Schadenszahl_B,
                    untersuchdat_haltung_bewertung.Schadenslaenge,
                    untersuchdat_haltung_bewertung.bw_bs,
                    untersuchdat_haltung_bewertung.createdat,
                    untersuchdat_haltung_bewertung.foto_dateiname,
                    untersuchdat_haltung_bewertung.film_dateiname,

                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.hoehe,
                    haltungen_untersucht_bewertung.breite,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.baujahr,
                    haltungen_untersucht_bewertung.Entwaesserungssystem,
                    haltungen_untersucht_bewertung.Abwasserart,
                    haltungen_untersucht_bewertung.Wasserschutzzone,
                    haltungen_untersucht_bewertung.Grundwasserabstand,
                    haltungen_untersucht_bewertung.Bodenart,
                    haltungen_untersucht_bewertung.Lage_am_Umfang,
                    haltungen_untersucht_bewertung.Lage_an_Bauteilverbindung,
                    haltungen_untersucht_bewertung.Objektklasse,
                    haltungen_untersucht_bewertung.createdat,
                    anschlussleitungen.leitnam
                    FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, anschlussleitungen
                    WHERE anschlussleitungen.leitnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal AND substr(haltungen_untersucht_bewertung.createdat, 0, 17) = ? AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17) = ?
                    """


        if excel_format == 'Alle Daten in ein Excel Tabellenblatt':

            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            try:
                dft = pd.read_sql(sql, db, params=(date, date))
            except:
                iface.messageBar().pushMessage("Error",
                                               "Die Excel Tabelle der Leitungen konnte nicht erstellt werden",
                                               level=Qgis.Critical)
                return

            dft.to_excel(writer, sheet_name="Leitungen", index=False)

            writer.save()

            df = pd.read_excel(file, decimal=',')

            df_styled = df.style.apply(lambda x: ["background-color: blue" if x == 1 else "background-color: white" for x in df.id])

            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            df_styled.to_excel(writer, sheet_name="Leitungen", index=False)
            writer.save()

        if excel_format == 'Für jede Haltung/Schacht ein eigenes Excel Tabellenblatt':

            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            try:
                dft = pd.read_sql(sql, db,  params=(date, date))
            except:
                iface.messageBar().pushMessage("Error",
                                               "Die Excel Tabelle der Leitungen konnte nicht erstellt werden",
                                               level=Qgis.Critical)
                return

            for table_name in dft['untersuchhal']:
                sheet_name = table_name

                SQL = "select *  FROM untersuchdat_haltung_bewertung, haltungen_untersucht_bewertung, anschlussleitungen WHERE anschlussleitungen.leitnam=untersuchdat_haltung_bewertung.untersuchhal AND haltungen_untersucht_bewertung.haltnam = '" + sheet_name + "' AND untersuchdat_haltung_bewertung.untersuchhal ='" + sheet_name +"' AND substr(untersuchdat_haltung_bewertung.createdat, 0, 17)='"+date+"' AND substr(haltungen_untersucht_bewertung.createdat, 0, 17)='"+date+"'"

                dft = pd.read_sql(SQL, db)

                dft.to_excel(writer, sheet_name=sheet_name, index=False)

                writer.save()

                df = pd.read_excel(file, decimal=',')

                df_styled = df.style.apply(
                    lambda x: ["background-color: blue" if x == 1 else "background-color: white" for x in df.id])

                writer = pd.ExcelWriter(file, engine='xlsxwriter')

                df_styled.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()

        else:
            pass

    def excel_schaechte(self):
        excel_speicher = self.excel_speicher
        excel_format = self.excel_format
        db_format = self.db_format
        pfad = excel_speicher
        file = os.path.join(pfad, "schaechte.xlsx")

        data = self.db
        date = self.date

        db = sqlite3.connect(data)
        curs = db.cursor()

        if db_format == "Datenbank mit DWA-M 149 Daten":
            sql2 = """
                    SELECT
                        Untersuchdat_schacht_bewertung.pk,
                        Untersuchdat_schacht_bewertung.id,
                        Untersuchdat_schacht_bewertung.untersuchsch,
                        Untersuchdat_schacht_bewertung.videozaehler,
                        Untersuchdat_schacht_bewertung.timecode,
                        Untersuchdat_schacht_bewertung.vertikale_lage,
                        Untersuchdat_schacht_bewertung.kuerzel,
                        Untersuchdat_schacht_bewertung.charakt1,
                        Untersuchdat_schacht_bewertung.charakt2,
                        Untersuchdat_schacht_bewertung.bereich,
                        Untersuchdat_schacht_bewertung.quantnr1,
                        Untersuchdat_schacht_bewertung.quantnr2,
                        Untersuchdat_schacht_bewertung.streckenschaden,
                        Untersuchdat_schacht_bewertung.streckenschaden_lfdnr,
                        Untersuchdat_schacht_bewertung.pos_von,
                        Untersuchdat_schacht_bewertung.pos_bis,
                        Untersuchdat_schacht_bewertung.bw_bs,
                        Untersuchdat_schacht_bewertung.Zustandsklasse_D,
                        Untersuchdat_schacht_bewertung.Zustandsklasse_S,
                        Untersuchdat_schacht_bewertung.Zustandsklasse_B,
                        Untersuchdat_schacht_bewertung.inspektionslaenge,
                        Untersuchdat_schacht_bewertung.foto_dateiname,
                        Untersuchdat_schacht_bewertung.createdat,
                        
                        schaechte_untersucht_bewertung.schnam,
                        schaechte_untersucht_bewertung.untersuchtag,
                        schaechte_untersucht_bewertung.untersucher,
                        schaechte_untersucht_bewertung.wetter,
                        schaechte_untersucht_bewertung.bewertungsart,
                        schaechte_untersucht_bewertung.bewertungstag,
                        schaechte_untersucht_bewertung.baujahr,
                        schaechte_untersucht_bewertung.hydraulische_auslastung,
                        schaechte_untersucht_bewertung.lage_grundwasser,
                        schaechte_untersucht_bewertung.ueberdeckung,
                        schaechte_untersucht_bewertung.bodengruppe,
                        schaechte_untersucht_bewertung.objektklasse_dichtheit,
                        schaechte_untersucht_bewertung.objektklasse_standsicherheit,
                        schaechte_untersucht_bewertung.objektklasse_betriebssicherheit,
                        schaechte_untersucht_bewertung.objektklasse_gesamt,
                        schaechte_untersucht_bewertung.Sanierungsbedarfszahl,
                        schaechte_untersucht_bewertung.Handlungsbedarf,
                        schaechte_untersucht_bewertung.createdat
                    FROM Untersuchdat_schacht_bewertung, schaechte_untersucht_bewertung
                     WHERE schaechte_untersucht_bewertung.schnam = Untersuchdat_schacht_bewertung.untersuchsch AND substr(schaechte_untersucht_bewertung.createdat, 0, 17) = ? AND substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ? 
                """

        if db_format == "Datenbank mit ISYBAU Daten":
            sql2 = """
                SELECT
                    Untersuchdat_schacht_bewertung.pk,
                    Untersuchdat_schacht_bewertung.id,
                    Untersuchdat_schacht_bewertung.untersuchsch,
                    Untersuchdat_schacht_bewertung.videozaehler,
                    Untersuchdat_schacht_bewertung.timecode,
                    Untersuchdat_schacht_bewertung.vertikale_lage,
                    Untersuchdat_schacht_bewertung.kuerzel,
                    Untersuchdat_schacht_bewertung.charakt1,
                    Untersuchdat_schacht_bewertung.charakt2,
                    Untersuchdat_schacht_bewertung.bereich,
                    Untersuchdat_schacht_bewertung.quantnr1,
                    Untersuchdat_schacht_bewertung.quantnr2,
                    Untersuchdat_schacht_bewertung.streckenschaden,
                    Untersuchdat_schacht_bewertung.streckenschaden_lfdnr,
                    Untersuchdat_schacht_bewertung.pos_von,
                    Untersuchdat_schacht_bewertung.pos_bis,
                    Untersuchdat_schacht_bewertung.bw_bs,
                    Untersuchdat_schacht_bewertung.Schadensklasse_D,
                    Untersuchdat_schacht_bewertung.Schadensklasse_S,
                    Untersuchdat_schacht_bewertung.Schadensklasse_B,
                    Untersuchdat_schacht_bewertung.vorlaufige_Schadenszahl_D,
                    Untersuchdat_schacht_bewertung.vorlaufige_Schadenszahl_S,
                    Untersuchdat_schacht_bewertung.vorlaufige_Schadenszahl_B,
                    Untersuchdat_schacht_bewertung.Schadenslaenge,
                    Untersuchdat_schacht_bewertung.foto_dateiname,
                    Untersuchdat_schacht_bewertung.createdat,

                    schaechte_untersucht_bewertung.schnam,
                    schaechte_untersucht_bewertung.untersuchtag,
                    schaechte_untersucht_bewertung.untersucher,
                    schaechte_untersucht_bewertung.wetter,
                    schaechte_untersucht_bewertung.bewertungsart,
                    schaechte_untersucht_bewertung.bewertungstag,
                    schaechte_untersucht_bewertung.baujahr,
                    schaechte_untersucht_bewertung.Entwaesserungssystem,
                    schaechte_untersucht_bewertung.Abwasserart,
                    schaechte_untersucht_bewertung.Wasserschutzzone,
                    schaechte_untersucht_bewertung.Grundwasserabstand,
                    schaechte_untersucht_bewertung.Bodenart,
                    schaechte_untersucht_bewertung.Lage_an_Bauteilverbindung,
                    schaechte_untersucht_bewertung.Objektklasse,
                    schaechte_untersucht_bewertung.createdat
                FROM Untersuchdat_schacht_bewertung, schaechte_untersucht_bewertung
                 WHERE schaechte_untersucht_bewertung.schnam = Untersuchdat_schacht_bewertung.untersuchsch AND substr(schaechte_untersucht_bewertung.createdat, 0, 17) = ? AND substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ? 
            """

        if excel_format == 'Alle Daten in ein Excel Tabellenblatt':
            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            try:
                dft = pd.read_sql(sql2, db, params=(date, date))
            except:
                iface.messageBar().pushMessage("Error",
                                               "Die Excel Tabelle der Schächte konnte nicht erstellt werden",
                                               level=Qgis.Critical)
                return

            dft.to_excel(writer, sheet_name="Schächte", index=False)

            writer.save()

            df = pd.read_excel(file, decimal=',')

            df_styled = df.style.apply(lambda x: ["background-color: blue" if x == 1 else "background-color: white" for x in df.id])

            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            df_styled.to_excel(writer, sheet_name="Schächte", index=False)
            writer.save()

        if excel_format == 'Für jede Haltung/Schacht ein eigenes Excel Tabellenblatt':
            writer = pd.ExcelWriter(file, engine='xlsxwriter')

            try:
                dft = pd.read_sql(sql2, db,  params=(date, date))
            except:
                iface.messageBar().pushMessage("Error",
                                               "Die Excel Tabelle der Schächte konnte nicht erstellt werden",
                                               level=Qgis.Critical)
                return

            for table_name in dft['untersuchsch']:
                sheet_name = table_name

                SQL = "select *  FROM Untersuchdat_schacht_bewertung, schaechte_untersucht_bewertung WHERE schaechte_untersucht_bewertung.schnam = '" + sheet_name + "' AND Untersuchdat_schacht_bewertung.untersuchsch ='" + sheet_name +"' AND substr(Untersuchdat_schacht_bewertung.createdat, 0, 17)='"+date +"' AND substr(schaechte_untersucht_bewertung.createdat, 0, 17)='"+date+"'"

                dft = pd.read_sql(SQL, db)

                dft.to_excel(writer, sheet_name=sheet_name, index=False)

                writer.save()

                df = pd.read_excel(file, decimal=',')

                df_styled = df.style.apply(
                    lambda x: ["background-color: blue" if x == 1 else "background-color: white" for x in df.id])

                writer = pd.ExcelWriter(file, engine='xlsxwriter')

                df_styled.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()

        else:
            pass
