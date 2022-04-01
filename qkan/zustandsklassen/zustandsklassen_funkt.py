# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import Qgis, QgsProject, QgsVectorLayer, QgsDataSourceUri, QgsPrintLayout, QgsReadWriteContext
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt import Qt
from qgis.utils import iface, spatialite_connect
import xml.etree.ElementTree as ElementTree
from typing import Dict, Iterator, Tuple, Union
from lxml import etree
import sqlite3



class zustandsklassen_funkt:
    def __init__(self, check_cb, db, date, epsg):

        self.check_cb = check_cb
        self.db = db
        self.date = date
        self.crs = epsg

        self.haltung=False
        self.leitung=False

    def run(self):
        check_cb = self.check_cb

        x = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(x+"/Layouts"):
            if file.endswith(".qpt"):
                project = QgsProject.instance()
                composition = QgsPrintLayout(project)
                document = QDomDocument()
                template = open(x+"/Layouts/" + file)
                template_content = template.read()
                template.close()
                document.setContent(template_content)
                composition.loadFromTemplate(document, QgsReadWriteContext())
                project.layoutManager().addLayout(composition)

        if check_cb['cb7']:
            self.haltung = True
            self.leitung = False
            self.bewertungstexte_haltung()

        if check_cb['cb8']:
            self.bewertungstexte_schacht()

        if check_cb['cb10']:
            self.leitung = True
            self.haltung = False
            self.bewertungstexte_haltung()

        if check_cb['cb3'] and check_cb['cb1']:
            self.haltung = True
            self.leitung = False
            self.bewertung_dwa_haltung()

        if check_cb['cb5'] and check_cb['cb4']:
            self.bewertung_dwa_schacht()

        if check_cb['cb3'] and check_cb['cb2']:
            self.bewertung_isy_haltung()

        if check_cb['cb5'] and check_cb['cb6']:
            self.bewertung_isy_schacht()

        if check_cb['cb9']:
            self.haltung = True
            self.leitung = False
            self.bewertung_dwa_neu_haltung()

        if check_cb['cb14']:
            self.bewertung_dwa_neu_schaechte()

        if check_cb['cb15']:
            self.leitung = True
            self.haltung = False
            self.bewertung_dwa_neu_haltung()

        if check_cb['cb11'] and check_cb['cb12']:
            self.leitung = True
            self.haltung = False
            self.bewertung_dwa_haltung()

        if check_cb['cb11'] and check_cb['cb13']:
            self.bewertung_isy_haltung()

    def bewertungstexte_haltung(self):
        date = self.date
        db = self.db
        data = db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung
        db_x = self.db
        db = spatialite_connect(data)
        curs = db.cursor()

        sql = """CREATE TABLE IF NOT EXISTS Untersuchdat_haltung_bewertung AS SELECT * FROM Untersuchdat_haltung"""
        curs.execute(sql)

        if haltung == True:

            sql = """
                SELECT
                    Untersuchdat_haltung_bewertung.pk,
                    Untersuchdat_haltung_bewertung.untersuchhal,
                    Untersuchdat_haltung_bewertung.untersuchrichtung,
                    Untersuchdat_haltung_bewertung.schoben,
                    Untersuchdat_haltung_bewertung.schunten,
                    Untersuchdat_haltung_bewertung.id,
                    Untersuchdat_haltung_bewertung.videozaehler,
                    Untersuchdat_haltung_bewertung.inspektionslaenge,
                    Untersuchdat_haltung_bewertung.station,
                    Untersuchdat_haltung_bewertung.timecode,
                    Untersuchdat_haltung_bewertung.kuerzel,
                    Untersuchdat_haltung_bewertung.charakt1,
                    Untersuchdat_haltung_bewertung.charakt2,
                    Untersuchdat_haltung_bewertung.quantnr1,
                    Untersuchdat_haltung_bewertung.quantnr2,
                    Untersuchdat_haltung_bewertung.streckenschaden,
                    Untersuchdat_haltung_bewertung.pos_von,
                    Untersuchdat_haltung_bewertung.pos_bis,
                    Untersuchdat_haltung_bewertung.foto_dateiname,
                    Untersuchdat_haltung_bewertung.film_dateiname,
                    Untersuchdat_haltung_bewertung.richtung,
                    Untersuchdat_haltung_bewertung.createdat,
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    haltungen.createdat
                FROM Untersuchdat_haltung_bewertung, haltungen
                WHERE haltungen.haltnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat, 0, 17) = ?
            """
            data = (date, )

        if leitung == True:

            sql = """
                    SELECT
                        Untersuchdat_haltung_bewertung.pk,
                        Untersuchdat_haltung_bewertung.untersuchhal,
                        Untersuchdat_haltung_bewertung.untersuchrichtung,
                        Untersuchdat_haltung_bewertung.schoben,
                        Untersuchdat_haltung_bewertung.schunten,
                        Untersuchdat_haltung_bewertung.id,
                        Untersuchdat_haltung_bewertung.videozaehler,
                        Untersuchdat_haltung_bewertung.inspektionslaenge,
                        Untersuchdat_haltung_bewertung.station,
                        Untersuchdat_haltung_bewertung.timecode,
                        Untersuchdat_haltung_bewertung.kuerzel,
                        Untersuchdat_haltung_bewertung.charakt1,
                        Untersuchdat_haltung_bewertung.charakt2,
                        Untersuchdat_haltung_bewertung.quantnr1,
                        Untersuchdat_haltung_bewertung.quantnr2,
                        Untersuchdat_haltung_bewertung.streckenschaden,
                        Untersuchdat_haltung_bewertung.pos_von,
                        Untersuchdat_haltung_bewertung.pos_bis,
                        Untersuchdat_haltung_bewertung.foto_dateiname,
                        Untersuchdat_haltung_bewertung.film_dateiname,
                        Untersuchdat_haltung_bewertung.richtung,
                        Untersuchdat_haltung_bewertung.createdat,
                        anschlussleitungen.leitnam,
                        anschlussleitungen.material,
                        anschlussleitungen.hoehe,
                        anschlussleitungen.createdat
                    FROM Untersuchdat_haltung_bewertung, anschlussleitungen
                    WHERE anschlussleitungen.leitnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat, 0, 17) = ? 
                """
            data = (date,)

        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Bewertungstexte der Haltungen/Leitungen konnten nicht ermittelt werden",
                                           level=Qgis.Critical)

        for attr in curs.fetchall():
            try:
                curs.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN Beschreibung TEXT ;""")
            except:
                pass

            # Tab A.2
            if attr[10] == "BAA":
                z = 'Verformung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            # Tab A.3
            if attr[10] == "BAB":
                z = 'Rissbildung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            if attr[10] == "BAC":
                z = 'Rohrbruch/Einsturz'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            if attr[10] == "BAD":
                z = 'Defektes Mauerwerk'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            if attr[10] == "BAE":
                z = 'Fehlender Mörtel'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            if attr[10] == "BAF":
                z = 'Oberflächenschäden'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            if attr[10] == "BAG":
                z = 'Einragender Anschluss'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            if attr[10] == "BAH":
                z = 'Schadhafter Anschluss'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI":
                z = 'Einragendes Dichtungsmaterial'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ":
                z = 'Verschobene Verbindung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "A":
                z = 'Feststellung der Innenauskleidung: Innenauskleidung abgelöst'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "B":
                z = 'Feststellung der Innenauskleidung: Innenauskleidung verfärbt'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "C":
                z = 'Feststellung der Innenauskleidung: Endstelle der Auskleidung schadhaft'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D":
                z = 'Feststellung der Innenauskleidung: Faten in der Auskleidung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "E":
                z = 'Feststellung der Innenauskleidung: Blasen oder Beulen in der Auskleidung nach innen'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "F":
                z = 'Feststellung der Innenauskleidung: Beulen aussen'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "G":
                z = 'Feststellung der Innenauskleidung: Ablösen der Innenhaut/Beschichtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "H":
                z = 'Feststellung der Innenauskleidung: Ablösen der Abdeckung der Verbindungsnaht'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "I":
                z = 'Feststellung der Innenauskleidung: Riss oder Spalt (einschließlich schadhafter Schweissnaht)'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "J":
                z = 'Feststellung der Innenauskleidung: Loch in der Auskleidung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "K":
                z = 'Feststellung der Innenauskleidung: Auskleidungsverbindung defekt'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "L":
                z = 'Feststellung der Innenauskleidung: Auskleidungswerkstoff erscheint weich'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "M":
                z = 'Feststellung der Innenauskleidung: Harz fehlt im Laminat'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "N":
                z = 'Feststellung der Innenauskleidung: Ende der Auskleidung ist nicht abgedichtet, um das Rohr oder den Schacht aufzunehmen.'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "Z":
                z = 'Feststellung der Innenauskleidung: Anderer Auskleidungsschaden'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "A":
                z = 'Schadhafte Reperatur: Wand fehlt teilweise'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "B":
                z = 'Schadhafte Reperatur: Reperatur zur Abdichtung eines Lochs ist schadhaft'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "C":
                z = 'Schadhafte Reperatur: Ablösen des Reperaturwerkstofes vom Basisrohr'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "D":
                z = 'Schadhafte Reperatur: fehlender Reperaturwerkstoff an der Kontaktfläche'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "E":
                z = 'Schadhafte Reperatur: überschüssiger Reperaturwerkstoff, der ein Hindernis darstellt'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "P":
                z = 'Schadhafte Reperatur: Loch im Reperaturwerkstoff'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "G":
                z = 'Schadhafte Reperatur: Riss im Reperaturwerkstoff'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "Z":
                z = 'Schadhafte Reperatur: Andere'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM":
                z = 'Schadhafte Schweissnaht'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAN":
                z = 'Poroeses Rohr'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAO":
                z = 'Boden sichtbar'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAP":
                z = 'Hohlraum sichtbar'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBA":
                z = 'Wurzeln'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB":
                z = 'Anhaftende Stoffe'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC":
                z = 'Ablagerungen'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBD":
                z = 'Eindringen von Bodenmaterial'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE":
                z = 'Andere Hindernisse'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF":
                z = 'Infiltration'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBG":
                z = 'Exfiltration'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBH":
                z = 'Ungeziefer'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCA":
                z = 'Anschluss'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "A":
                z = 'Punktuelle Reperatur: Reperatur mit Injektionstechnik'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "B":
                z = 'Punktuelle Reperatur: Reperatur mit Roboter'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "C":
                z = 'Punktuelle Reperatur: Reperatur mit partieller Auskleidungs-/Manchettentechnik'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "D":
                z = 'Punktuelle Reperatur: Zulaufeinbindung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "E":
                z = 'Punktuelle Reperatur: Reperatur Rohrwand manuell'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "F":
                z = 'Punktuelle Reperatur: Reperatur Rohrverbindung manuell'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "G":
                z = 'Punktuelle Reperatur: Ringspalt-/-raumdichtung (der Auskleidung) zum Anschluss an Schacht/Inspektionsöffnung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "H":
                z = 'Punktuelle Reperatur: Zulauföffnung ohne Einbindung (Auskleidung)'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "I":
                z = 'Punktuelle Reperatur: Rohr ausgetauscht'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCB" and attr[11] == "Z":
                z = 'Punktuelle Reperatur: sonstige Technink'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCC":
                z = 'Krümmung der Leitung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCD":
                z = 'Anfangsknoten'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BCE":
                z = 'Endknoten'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDA":
                z = 'Allgemeines Foto'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "AA":
                z = 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, eingesteckt, gerade'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "AB":
                z = 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, uebergestuelpt, gerade'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "AC":
                z = 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, eingesteckt, abgewinkelt'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "AD":
                z = 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, uebergestuelpt, abgewinkelt'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "AE":
                z = 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, stumpf aneinandergestossen'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "BA":
                z = 'Allgemeine Anmerkung: Verschluss eines Rohrs durch Abmauerung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "BB":
                z = 'Allgemeine Anmerkung: Verschluss eines Rohrs durch Moertel'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "BC":
                z = 'Allgemeine Anmerkung: Verschluss eines Rohrs durch Deckel (Muffenstopfen)'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDC":
                z = 'Inspektion endet vor dem Endknoten'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDD":
                z = 'Wasserspiegel'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE":
                z = 'Zufluss aus einem Anschluss'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDF":
                z = 'Atmosphäre in der Leitung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDG":
                z = 'Keine Sicht'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

        sql = """SELECT RecoverGeometryColumn('Untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'Untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        Untersuchdat_haltung_bewertung = 'Untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), Untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(Untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)


    def bewertungstexte_schacht(self):
        date = self.date
        db = self.db
        data = db
        db = spatialite_connect(data)
        curs = db.cursor()
        db_x = self.db
        crs = self.crs

        sql = """CREATE TABLE IF NOT EXISTS Untersuchdat_schacht_bewertung AS SELECT * FROM Untersuchdat_schacht"""
        curs.execute(sql)

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
                Untersuchdat_schacht_bewertung.pos_von,
                Untersuchdat_schacht_bewertung.pos_bis,
                Untersuchdat_schacht_bewertung.bereich,
                Untersuchdat_schacht_bewertung.foto_dateiname,
                Untersuchdat_schacht_bewertung.createdat
            FROM Untersuchdat_schacht_bewertung
            WHERE substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ? 
        """
        data = (date,)

        try:
            curs.execute(sql, data)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Bewertungstexte der Schächte konnten nicht ermittelt werden",
                                           level=Qgis.Critical)

        for attr in curs.fetchall():
            try:
                curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Beschreibung TEXT ;""")
            except:
                pass

            if attr[5] == "DAA":
                z = 'Verformung'
                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAB":
                z = 'Rissbildung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAC":
                z = 'Bruch/Einsturz'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAD":
                z = 'Defektes Mauerwerk'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAE":
                z = 'FEhlender Moertel'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAF":
                z = 'Oberflaechenschaden'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAG":
                z = 'Einragender Anschluss'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAH":
                z = 'Schadhafter Anschluss'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAI":
                z = 'Einragendes Dichtungsmaterial'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAJ":
                z = 'Verschobene Verbindung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "A":
                z = 'Feststellung der Innenauskleidung: Innenauskleidung abgeloest'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "B":
                z = 'Feststellung der Innenauskleidung: Innenauskleidung verfaerbt'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "C":
                z = 'Feststellung der Innenauskleidung: Endstelle der Auskleidung schadhaft'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "D":
                z = 'Feststellung der Innenauskleidung: Falten in der Innenauskleidung'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "E":
                z = 'Feststellung der Innenauskleidung: Blasen oder Beulen in der Auskleidung innen'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "F":
                z = 'Feststellung der Innenauskleidung: Beulen aussen'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "G":
                z = 'Feststellung der Innenauskleidung: Abloesen der Innenhaut/Beschichtung'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "H":
                z = 'Feststellung der Innenauskleidung: Abloesen der Abdeckung der Verbindungsnaht'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "I":
                z = 'Feststellung der Innenauskleidung: Riss oder Spalt (einschliesslich schadhafter Schweissnaht)'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "J":
                z = 'Feststellung der Innenauskleidung: Loch in der Auskleidung'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "K":
                z = 'Feststellung der Innenauskleidung: Auskleidungsverbindung defekt'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "L":
                z = 'Feststellung der Innenauskleidung: Auskleidungswerkstoff erscheint weich'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "M":
                z = 'Feststellung der Innenauskleidung: Harz fehlt im Laminat'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "N":
                z = 'Feststellung der Innenauskleidung: Ende der Auskleidung ist nicht abgedichtet, um das Rohr oder den Schacht aufzunehmen'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAK" and attr[6] == "Z":
                z = 'Feststellung der Innenauskleidung: Anderer Auskleidungsschaden'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            if attr[5] == "DAL" and attr[6] == "A":
                z = 'Schadhafte Reperatur: Wand fehlt teilweise'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAL" and attr[6] == "B":
                z = 'Schadhafte Reperatur: Reperatur zur Abdichtung eines Lochs ist schadhaft'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAL" and attr[6] == "C":
                z = 'Schadhafte Reperatur: Abloesen des Reperaturwerkstoffs vom Basisrohr'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAL" and attr[6] == "D":
                z = 'Schadhafte Reperatur: fehlender Reperaturwerkstoff an der Kontaktflaeche'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAL" and attr[6] == "E":
                z = 'Schadhafte Reperatur: ueberschuessiger Reperaturwerkstof, der ein Hindernis darstellt'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAL" and attr[6] == "F":
                z = 'Schadhafte Reperatur: Loch im Reperaturwerkstoff'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAL" and attr[6] == "G":
                z = 'Schadhafte Reperatur: Riss im Reperaturwerkstoff'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAL" and attr[6] == "Z":
                z = 'Schadhafte Reperatur: Andere'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAM":
                z = 'Schadhafte Schweissnaht'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAN":
                z = 'Poroese Wand'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAO":
                z = 'Boden sichtbar'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAP":
                z = 'Hohlraum sichtbar'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAQ":
                z = 'Schadhafte Steighilfen'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAR":
                z = 'Schaeden an Abdeckung oder Rahmen'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Beschreibung = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBA":
                z = 'Wurzeln'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBB":
                z = 'Anaftene Stoffe'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBC":
                z = 'Ablagerungen'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBD":
                z = 'Eindringen von Bodenmaterial'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBE":
                z = 'Andere Hindernisse'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Beschreibung = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBF":
                z = 'Infiltration'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBG":
                z = 'Exfiltration'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBH":
                z = 'Ungeziefer'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCA":
                z = 'Anschluss'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "A":
                z = 'Punktuelle Reperatur: Reperatur mit Injektionstechnik'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "B":
                z = 'Punktuelle Reperatur: Reperatur Bauteilwandung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "C":
                z = 'Punktuelle Reperatur: Reperatur Bauteilverbindung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "D":
                z = 'Punktuelle Reperatur: Ringsplat-/-raumabdichtung(Auskleidung in Kanaelen/Leitungen) zum Anschuss an Schacht/Inspektionsoeffnung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "E":
                z = 'Punktuelle Reperatur: Anschlusseinbindung manuell'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "F":
                z = 'Punktuelle Reperatur: Anschlusseoeffnung ohne Einbindung(Auskleidung)'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "G":
                z = 'Punktuelle Reperatur: Schachtbauteil ausgetauscht'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCB" and attr[6] == "Z":
                z = 'Punktuelle Reperatur: Reperatur sonstige Technik'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCG":
                z = 'Anschlussleitung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCH":
                z = 'Auftritt'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCI":
                z = 'Gerinne'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCJ":
                z = 'Sicherheitsketten/-balken'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCK":
                z = 'Abflussregulierung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCL":
                z = 'Rohrdurchfuehrung durch andere Abwasserleitung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCM":
                z = 'Schmutzfaenger unter der Abdeckung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCN":
                z = 'Schlammfang in der Sohle'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCO":
                z = 'Querschnitt'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDA":
                z = 'Allgemeines Foto'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDB":
                z = 'Allgemeine Anmerkung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDC":
                z = 'Inspektion nicht vollstaendig durchgefuehrt'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDD":
                z = 'Wasserspiegel'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDE":
                z = 'Zufluss aus einem Anschluss'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDF":
                z = 'Atmosphäre im Schacht oder in der Inspektionsoeffnung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDG":
                z = 'Keine Sicht'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Beschreibung = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
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

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_schacht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)


    def bewertung_dwa_neu_haltung(self):
        date = self.date
        db_x = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        data = db_x
        db = spatialite_connect(db_x)
        curs = db.cursor()

        if haltung == True:
            sql = """
                        SELECT
                            Untersuchdat_haltung_bewertung.pk,
                            Untersuchdat_haltung_bewertung.untersuchhal,
                            Untersuchdat_haltung_bewertung.untersuchrichtung,
                            Untersuchdat_haltung_bewertung.schoben,
                            Untersuchdat_haltung_bewertung.schunten,
                            Untersuchdat_haltung_bewertung.id,
                            Untersuchdat_haltung_bewertung.videozaehler,
                            Untersuchdat_haltung_bewertung.inspektionslaenge,
                            Untersuchdat_haltung_bewertung.station,
                            Untersuchdat_haltung_bewertung.timecode,
                            Untersuchdat_haltung_bewertung.kuerzel,
                            Untersuchdat_haltung_bewertung.charakt1,
                            Untersuchdat_haltung_bewertung.charakt2,
                            Untersuchdat_haltung_bewertung.quantnr1,
                            Untersuchdat_haltung_bewertung.quantnr2,
                            Untersuchdat_haltung_bewertung.streckenschaden,
                            Untersuchdat_haltung_bewertung.pos_von,
                            Untersuchdat_haltung_bewertung.pos_bis,
                            Untersuchdat_haltung_bewertung.foto_dateiname,
                            Untersuchdat_haltung_bewertung.film_dateiname,
                            Untersuchdat_haltung_bewertung.richtung,
                            Untersuchdat_haltung_bewertung.bw_bs,
                            Untersuchdat_haltung_bewertung.createdat,
                            haltungen.haltnam,
                            haltungen.material,
                            haltungen.hoehe,
                            haltungen.createdat
                        FROM Untersuchdat_haltung_bewertung, haltungen
                        WHERE haltungen.haltnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat, 0, 17) = ? 
                    """
            data = (date,)

            curs.execute(sql, data)

        if leitung == True:
            sql = """
                        SELECT
                            Untersuchdat_haltung_bewertung.pk,
                            Untersuchdat_haltung_bewertung.untersuchhal,
                            Untersuchdat_haltung_bewertung.untersuchrichtung,
                            Untersuchdat_haltung_bewertung.schoben,
                            Untersuchdat_haltung_bewertung.schunten,
                            Untersuchdat_haltung_bewertung.id,
                            Untersuchdat_haltung_bewertung.videozaehler,
                            Untersuchdat_haltung_bewertung.inspektionslaenge,
                            Untersuchdat_haltung_bewertung.station,
                            Untersuchdat_haltung_bewertung.timecode,
                            Untersuchdat_haltung_bewertung.kuerzel,
                            Untersuchdat_haltung_bewertung.charakt1,
                            Untersuchdat_haltung_bewertung.charakt2,
                            Untersuchdat_haltung_bewertung.quantnr1,
                            Untersuchdat_haltung_bewertung.quantnr2,
                            Untersuchdat_haltung_bewertung.streckenschaden,
                            Untersuchdat_haltung_bewertung.pos_von,
                            Untersuchdat_haltung_bewertung.pos_bis,
                            Untersuchdat_haltung_bewertung.foto_dateiname,
                            Untersuchdat_haltung_bewertung.film_dateiname,
                            Untersuchdat_haltung_bewertung.richtung,
                            Untersuchdat_haltung_bewertung.bw_bs,
                            Untersuchdat_haltung_bewertung.createdat,
                            anschlussleitungen.leitnam,
                            anschlussleitungen.material,
                            anschlussleitungen.hoehe,
                            anschlussleitungen.createdat
                        FROM Untersuchdat_haltung_bewertung, anschlussleitungen
                        WHERE anschlussleitungen.leitnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat, 0, 17) = ? 
                    """
            data = (date, )

            curs.execute(sql, data)


        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_dichtheit =
                                (SELECT min(Zustandsklasse_D) 
                                FROM Untersuchdat_haltung_bewertung
                                WHERE Untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_D <> '-'
                                GROUP BY Untersuchdat_haltung_bewertung.untersuchhal);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_standsicherheit =
                                (SELECT min(Zustandsklasse_S) 
                                FROM Untersuchdat_haltung_bewertung
                                WHERE Untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_S <> '-'
                                GROUP BY Untersuchdat_haltung_bewertung.untersuchhal);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_betriebssicherheit =
                                (SELECT min(Zustandsklasse_B) 
                                FROM Untersuchdat_haltung_bewertung
                                WHERE Untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_B <> '-'
                                GROUP BY Untersuchdat_haltung_bewertung.untersuchhal);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_standsicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_dichtheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_betriebssicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""Update
                                haltungen_untersucht_bewertung
                                SET
                                objektklasse_gesamt =
                                (Case
                                 When objektklasse_dichtheit <= objektklasse_standsicherheit And objektklasse_dichtheit <= objektklasse_betriebssicherheit Then objektklasse_dichtheit
                                 When objektklasse_standsicherheit <= objektklasse_dichtheit And objektklasse_standsicherheit <= objektklasse_betriebssicherheit Then objektklasse_standsicherheit
                                 When objektklasse_betriebssicherheit <= objektklasse_dichtheit And objektklasse_betriebssicherheit <= objektklasse_standsicherheit Then objektklasse_betriebssicherheit
                                 Else NULL
                                 END
                                 );""")
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('Untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
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

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'Untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        Untersuchdat_haltung_bewertung = 'Untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), Untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(Untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_dwa.qml')
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

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/haltungen_untersucht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)

    def bewertung_dwa_neu_schaechte(self):
        date = self.date
        db_x = self.db
        crs = self.crs

        data = db_x
        db = spatialite_connect(db_x)
        curs = db.cursor()

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
                        Untersuchdat_schacht_bewertung.pos_von,
                        Untersuchdat_schacht_bewertung.pos_bis,
                        Untersuchdat_schacht_bewertung.bereich,
                        Untersuchdat_schacht_bewertung.foto_dateiname,
                        Untersuchdat_schacht_bewertung.bw_bs,
                        Untersuchdat_schacht_bewertung.createdat
                    FROM Untersuchdat_schacht_bewertung  
                    WHERE substr(Untersuchdat_schacht_bewertung.createdat , 0, 17) = ? 
                """
        data = (date,)
        curs.execute(sql, data)


        try:
            curs.execute("""UPDATE schaechte_untersucht_bewertung 
                                    SET objektklasse_dichtheit =
                                    (SELECT min(Zustandsklasse_D) 
                                    FROM Untersuchdat_schacht_bewertung
                                    WHERE Untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam AND Zustandsklasse_D <> '-'
                                    GROUP BY Untersuchdat_schacht_bewertung.untersuchsch);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE schaechte_untersucht_bewertung 
                                    SET objektklasse_standsicherheit =
                                    (SELECT min(Zustandsklasse_S) 
                                    FROM Untersuchdat_schacht_bewertung
                                    WHERE Untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam AND Zustandsklasse_S <> '-'
                                    GROUP BY Untersuchdat_schacht_bewertung.untersuchsch);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE schaechte_untersucht_bewertung 
                                    SET objektklasse_betriebssicherheit =
                                    (SELECT min(Zustandsklasse_B) 
                                    FROM Untersuchdat_schacht_bewertung
                                    WHERE Untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam AND Zustandsklasse_B <> '-'
                                    GROUP BY Untersuchdat_schacht_bewertung.untersuchsch);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update schaechte_untersucht_bewertung 
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update schaechte_untersucht_bewertung 
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update schaechte_untersucht_bewertung 
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""Update
                                    schaechte_untersucht_bewertung
                                    set
                                    objektklasse_gesamt =
                                    (Case
                                     When objektklasse_dichtheit <= objektklasse_standsicherheit And objektklasse_dichtheit <= objektklasse_betriebssicherheit Then objektklasse_dichtheit
                                     When objektklasse_standsicherheit <= objektklasse_dichtheit And objektklasse_standsicherheit <= objektklasse_betriebssicherheit Then objektklasse_standsicherheit
                                     When objektklasse_betriebssicherheit <= objektklasse_dichtheit And objektklasse_betriebssicherheit <= objektklasse_standsicherheit Then objektklasse_betriebssicherheit
                                     Else NULL
                                     END
                                     );""")
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

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_schacht_bewertung_dwa.qml')
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

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/schaechte_untersucht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)



    def bewertung_dwa_haltung(self):
        date = self.date
        db_x = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        data = db_x

        db1 = spatialite_connect(data)
        curs1 = db1.cursor()

        # nach DWA

        sql = """CREATE TABLE IF NOT EXISTS Untersuchdat_haltung_bewertung AS SELECT * FROM Untersuchdat_haltung"""
        curs1.execute(sql)

        if haltung == True:
            sql = """
                SELECT
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    Untersuchdat_haltung_bewertung.untersuchhal
                FROM haltungen, Untersuchdat_haltung_bewertung
            """

        if leitung == True:
            sql = """
                    SELECT
                        anschlussleitungen.leitnam,
                        anschlussleitungen.material,
                        anschlussleitungen.hoehe,
                        Untersuchdat_haltung_bewertung.untersuchhal
                    FROM anschlussleitungen, Untersuchdat_haltung_bewertung
                """

        try:
            curs1.execute(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        for attr1 in curs1.fetchall():

            untersuchhalt = attr1[0]
            try:
                curs1.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "B", "BS", "FZ", "MA", "OB", "P", "PC", "PCC", "PHB", "SFB", "SPB", "SB", "STZ",
                            "SZB", "ZG"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass

            if attr1[1] in ["CNS", "EIS", "GFK", "GG", "GGG", "KST", "PE", "PEHD", "PH", "PP", "PVC", "PVCU", "ST"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass
            db1.commit()


        db = spatialite_connect(db_x)
        curs = db.cursor()

        if haltung == True:
            sql = """
                SELECT
                    Untersuchdat_haltung_bewertung.pk,
                    Untersuchdat_haltung_bewertung.untersuchhal,
                    Untersuchdat_haltung_bewertung.untersuchrichtung,
                    Untersuchdat_haltung_bewertung.schoben,
                    Untersuchdat_haltung_bewertung.schunten,
                    Untersuchdat_haltung_bewertung.id,
                    Untersuchdat_haltung_bewertung.videozaehler,
                    Untersuchdat_haltung_bewertung.inspektionslaenge,
                    Untersuchdat_haltung_bewertung.station,
                    Untersuchdat_haltung_bewertung.timecode,
                    Untersuchdat_haltung_bewertung.kuerzel,
                    Untersuchdat_haltung_bewertung.charakt1,
                    Untersuchdat_haltung_bewertung.charakt2,
                    Untersuchdat_haltung_bewertung.quantnr1,
                    Untersuchdat_haltung_bewertung.quantnr2,
                    Untersuchdat_haltung_bewertung.streckenschaden,
                    Untersuchdat_haltung_bewertung.pos_von,
                    Untersuchdat_haltung_bewertung.pos_bis,
                    Untersuchdat_haltung_bewertung.foto_dateiname,
                    Untersuchdat_haltung_bewertung.film_dateiname,
                    Untersuchdat_haltung_bewertung.richtung,
                    Untersuchdat_haltung_bewertung.bw_bs,
                    Untersuchdat_haltung_bewertung.createdat,
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    haltungen.createdat
                FROM Untersuchdat_haltung_bewertung, haltungen
                WHERE haltungen.haltnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat , 0, 17) = ? 
            """
            data = (date, )

            curs.execute(sql, data)

        if leitung == True:
            sql = """
                SELECT
                    Untersuchdat_haltung_bewertung.pk,
                    Untersuchdat_haltung_bewertung.untersuchhal,
                    Untersuchdat_haltung_bewertung.untersuchrichtung,
                    Untersuchdat_haltung_bewertung.schoben,
                    Untersuchdat_haltung_bewertung.schunten,
                    Untersuchdat_haltung_bewertung.id,
                    Untersuchdat_haltung_bewertung.videozaehler,
                    Untersuchdat_haltung_bewertung.inspektionslaenge,
                    Untersuchdat_haltung_bewertung.station,
                    Untersuchdat_haltung_bewertung.timecode,
                    Untersuchdat_haltung_bewertung.kuerzel,
                    Untersuchdat_haltung_bewertung.charakt1,
                    Untersuchdat_haltung_bewertung.charakt2,
                    Untersuchdat_haltung_bewertung.quantnr1,
                    Untersuchdat_haltung_bewertung.quantnr2,
                    Untersuchdat_haltung_bewertung.streckenschaden,
                    Untersuchdat_haltung_bewertung.pos_von,
                    Untersuchdat_haltung_bewertung.pos_bis,
                    Untersuchdat_haltung_bewertung.foto_dateiname,
                    Untersuchdat_haltung_bewertung.film_dateiname,
                    Untersuchdat_haltung_bewertung.richtung,
                    Untersuchdat_haltung_bewertung.bw_bs,
                    Untersuchdat_haltung_bewertung.createdat,
                    anschlussleitungen.leitnam,
                    anschlussleitungen.material,
                    anschlussleitungen.hoehe,
                    anschlussleitungen.createdat
                FROM Untersuchdat_haltung_bewertung, anschlussleitungen
                WHERE anschlussleitungen.leitnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat , 0, 17) = ? 
            """
            data = (date, )

            curs.execute(sql, data)


        for attr in curs.fetchall():
            try:
                curs.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
            except:
                pass

            # Tab A.2
            if (attr[21] == "biegessteif" and attr[10] == "BAA" and attr[11] == "A") or (
                    attr[21] == "biegessteif" and attr[10] == "BAA" and attr[11] == "B"):
                if attr[13] >= 7:
                    z = '0'
                elif 4 <= attr[13] < 7:
                    z = '1'
                elif 3 <= attr[13] < 4:
                    z = '2'
                elif 1 <= attr[13] < 3:
                    z = '3'
                elif attr[13] < 1:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '0'
                elif 40 <= attr[13] < 50:
                    z = '1'
                elif 25 <= attr[13] < 40:
                    z = '2'
                elif 10 <= attr[13] < 25:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if (attr[21] == "biegeweich" and attr[10] == "BAA" and attr[11] == "A") or (
                    attr[21] == "biegeweich" and attr[10] == "BAA" and attr[11] == "B"):
                if attr[13] >= 15:
                    z = '0'
                elif 10 <= attr[13] < 15:
                    z = '1'
                elif 6 <= attr[13] < 10:
                    z = '2'
                elif 2 <= attr[13] < 6:
                    z = '3'
                elif attr[13] < 2:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '0'
                elif 40 <= attr[13] < 50:
                    z = '1'
                elif 25 <= attr[13] < 40:
                    z = '2'
                elif 10 <= attr[13] < 25:
                    z = '3'
                elif attr[13] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            # Tab A.3
            if attr[10] == "BAB" and attr[11] == "A" and (attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                if attr[13] >= 3:
                    z = '1'
                elif 3 > attr[13] >= 2:
                    z = '2'
                elif attr[13] < 2:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] == "":
                if attr[13] >= 8:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and attr[25] <= 0.3:
                if attr[13] >= 3:
                    z = '0'
                elif 3 > attr[13] >= 2:
                    z = '1'
                elif 2 > attr[13] >= 1:
                    z = '2'
                elif 1 > attr[13] >= 0.5:
                    z = '3'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.5 >= attr[25] > 0.3:
                if attr[13] >= 5:
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
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "A" and 0.7 >= attr[25] > 0.5:
                if attr[13] >= 8:
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
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and attr[12] == "B":
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAB" and (attr[11] == "B" or attr[11] == "C") and (attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "A":
                z = '1'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "B":
                z = '1'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAC" and attr[11] == "C":
                z = '0'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "A":
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "B" and attr[12] == "A":
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "B" and attr[12] == "B":
                z = '1'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "C":
                z = '0'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAD" and attr[11] == "D":
                z = '0'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAE":
                if attr[13] >= 100:
                    z = '2'
                if attr[13] < 100:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "A" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "B" and (attr[12] == "A" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "C" and (
                    attr[12] == "A"  or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "D" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "E" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '1'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "F" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "G" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "H" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '1'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "I" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '1'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "J" and (attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "K" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = '3'
                sql = f"""
                                      UPDATE Untersuchdat_haltung_bewertung
                                        SET Zustandsklasse_B = ?
                                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF" and attr[11] == "Z" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAG":
                if attr[25] <= 0.25:
                    if attr[13] >= 50:
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
                if 0.25 < attr[25] <= 0.5:
                    if attr[13] >= 80:
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
                if 0.5 < attr[25] <= 0.8:
                    if attr[13] >= 70:
                        z = '2'
                    elif 70 > attr[13] >= 10:
                        z = '3'
                    elif attr[13] < 10:
                        z = '4'
                    else:
                        z = '5'
                if attr[25] > 0.8:
                    if attr[13] >= 30:
                        z = '3'
                    elif attr[13] < 30:
                        z = '4'
                    else:
                        z = '5'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and (attr[11] == "B" or attr[11] == "C" or attr[11] == "D"):
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and attr[11] == "E":
                z = '-'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH" and attr[11] == "Z":
                z = 'Einzelfallbetrachtung'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "A" and attr[12] == "A":
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "A" and (attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAI" and attr[11] == "Z" and attr[12] == "Y":
                if attr[13] >= 50:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "A":
                if attr[25] <= 0.4:
                    if attr[13] >= 70:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if 0.4 < attr[25] <= 0.8:
                    if attr[13] >= 80:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if attr[25] > 0.8:
                    if attr[13] >= 90:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                z = '4'
                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "B":
                if attr[13] >= 30:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "C":
                if attr[25] <= 0.2:
                    if attr[13] >= 12:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if 0.2 < attr[25] <= 0.5:
                    if attr[13] >= 6:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if attr[25] > 0.5:
                    if attr[13] >= 6:
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
                      UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "A":
                if attr[13] >= 50:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "B":
                z = '4'
                sql = f"""
                                    UPDATE Untersuchdat_haltung_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and (attr[11] == "C"):
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D" and (attr[12] == "A" or attr[12] == "B" or attr[12] == "D"):
                z = 'Einzelfalletrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D" and (attr[12] == "C"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "E":
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 50:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "F":
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "G":
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "H":
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "I":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "J":
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "K":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "L":
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                                    UPDATE Untersuchdat_haltung_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "M":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "N":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "Z":
                z = 'Einzelfalletrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "A" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "B" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "C" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "D" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "E" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                if attr[13] >= 50:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "F" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "G" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "Z" and (attr[12]=="A" or attr[12]=="B" or attr[12]=="C" or attr[12]=="D"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and (attr[11] == "A" or attr[11] == "C"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and attr[11] == "B":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAN":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAO":
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAP":
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBA" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 30:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB" and attr[11] == "A":
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 30:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC" and (attr[11] == "A" or attr[11] == "B"):
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC" and (attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 50:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBD" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "Z"):
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '0'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 30:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (attr[11] == "D" or attr[11] == "G"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E" or attr[
                11] == "F" or attr[11] == "G" or attr[11] == "H" or attr[11] == "Z"):
                if attr[13] >= 50:
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
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and attr[11] == "A":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and (attr[11] == "B" or attr[11] == "C"):
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and attr[11] == "D":
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBG":
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBH" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "Z") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "Z"):
                z = '-'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and (attr[11] == "AA" or attr[11] == "AB" or attr[11] == "AC" or attr[11] == "AD" or attr[11] == "AE"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                                    UPDATE Untersuchdat_haltung_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and (attr[11] == "BA" or attr[11] == "BB" or attr[11] == "BC"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                            UPDATE Untersuchdat_haltung_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E") and attr[12] == "A":
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E") and attr[12] == "B":
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            z = '-'
            sql = f"""
                UPDATE Untersuchdat_haltung_bewertung
                SET Zustandsklasse_D = ?
                WHERE Untersuchdat_haltung_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                UPDATE Untersuchdat_haltung_bewertung
                SET Zustandsklasse_B = ?
                WHERE Untersuchdat_haltung_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                UPDATE Untersuchdat_haltung_bewertung
                SET Zustandsklasse_S = ?
                WHERE Untersuchdat_haltung_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            z = '5'
            sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Zustandsklasse_D is Null
                    """
            data = (z, )
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Zustandsklasse_B is Null
                    """
            data = (z, )
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Zustandsklasse_S is Null
                    """
            data = (z, )
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass


            sql = """CREATE TABLE IF NOT EXISTS haltungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
            curs1.execute(sql)
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
                db.commit()
            except:
                pass
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
                db.commit()
            except:
                pass
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
                db.commit()
            except:
                pass
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
                db.commit()
            except:
                pass
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
                db.commit()
            except:
                pass
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT;""")
                db.commit()
            except:
                pass
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
                db.commit()
            except:
                pass
            try:
                curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
                db.commit()
            except:
                pass


            #Objektklasse berechnen für jede Haltung dafür abfragen

            try:
                curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_dichtheit =
                                (SELECT min(Zustandsklasse_D) 
                                FROM Untersuchdat_haltung_bewertung
                                WHERE Untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_D <> '-'
                                GROUP BY Untersuchdat_haltung_bewertung.untersuchhal);""")
                db.commit()
            except:
                pass

            try:
                curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_standsicherheit =
                                (SELECT min(Zustandsklasse_S) 
                                FROM Untersuchdat_haltung_bewertung
                                WHERE Untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_S <> '-'
                                GROUP BY Untersuchdat_haltung_bewertung.untersuchhal);""")
                db.commit()
            except:
                pass

            try:
                curs.execute("""UPDATE haltungen_untersucht_bewertung 
                                SET objektklasse_betriebssicherheit =
                                (SELECT min(Zustandsklasse_B) 
                                FROM Untersuchdat_haltung_bewertung
                                WHERE Untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam AND Zustandsklasse_B <> '-'
                                GROUP BY Untersuchdat_haltung_bewertung.untersuchhal);""")
                db.commit()
            except:
                pass

            try:
                curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_standsicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
                db.commit()
            except:
                pass

            try:
                curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_dichtheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
                db.commit()
            except:
                pass

            try:
                curs.execute("""update haltungen_untersucht_bewertung 
                                set objektklasse_betriebssicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
                db.commit()
            except:
                pass

            try:
                curs.execute("""Update
                                haltungen_untersucht_bewertung
                                SET
                                objektklasse_gesamt =
                                (Case
                                 When objektklasse_dichtheit <= objektklasse_standsicherheit And objektklasse_dichtheit <= objektklasse_betriebssicherheit Then objektklasse_dichtheit
                                 When objektklasse_standsicherheit <= objektklasse_dichtheit And objektklasse_standsicherheit <= objektklasse_betriebssicherheit Then objektklasse_standsicherheit
                                 When objektklasse_betriebssicherheit <= objektklasse_dichtheit And objektklasse_betriebssicherheit <= objektklasse_standsicherheit Then objektklasse_betriebssicherheit
                                 Else NULL
                                 END
                                 );""")
                db.commit()
            except:
                pass

        sql = """SELECT RecoverGeometryColumn('Untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
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

        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'Untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        Untersuchdat_haltung_bewertung = 'Untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), Untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(Untersuchdat_haltung_bewertung)[0].id())
        except:
            pass

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_dwa.qml')
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

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/haltungen_untersucht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)


    def bewertung_dwa_schacht(self):
        date = self.date
        db = self.db
        crs = self.crs
        db_x = db

        data = db
        db1 = spatialite_connect(data)
        curs1 = db1.cursor()
        # nach DWA

        sql = """CREATE TABLE IF NOT EXISTS Untersuchdat_schacht_bewertung AS SELECT * FROM Untersuchdat_schacht"""
        curs1.execute(sql)

        sql = """
            SELECT
                schaechte.schnam,
                schaechte.material,
                Untersuchdat_schacht_bewertung.untersuchsch
            FROM schaechte, Untersuchdat_schacht_bewertung
        """

        try:
            curs1.execute(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.Critical)


        for attr1 in curs1.fetchall():
            untersuchhalt = attr1[0]
            try:
                curs1.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "B", "BS", "FZ", "MA", "OB", "P", "PC", "PCC", "PHB", "SFB", "SPB", "SB", "STZ",
                            "SZB", "ZG"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass

            if attr1[1] in ["CNS", "EIS", "GFK", "GG", "GGG", "KST", "PE", "PEHD", "PH", "PP", "PVC", "PVCU", "ST"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass
            db1.commit()

        db = spatialite_connect(db_x)
        curs = db.cursor()

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
                Untersuchdat_schacht_bewertung.pos_von,
                Untersuchdat_schacht_bewertung.pos_bis,
                Untersuchdat_schacht_bewertung.bereich,
                Untersuchdat_schacht_bewertung.foto_dateiname,
                Untersuchdat_schacht_bewertung.bw_bs,
                Untersuchdat_schacht_bewertung.createdat
            FROM Untersuchdat_schacht_bewertung  
            WHERE substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ?  
        """
        data = (date,)
        curs.execute(sql, data)


        for attr in curs.fetchall():
            try:
                curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
            except:
                pass

            if attr[5] == "DAA" and (attr[6] == "A" or attr[6] == "B"):
                if attr[8] >= 40:
                    z = '0'
                elif 40 > attr[8] >= 30:
                    z = '1'
                elif 30 > attr[8] >= 20:
                    z = '2'
                elif 20 > attr[8] >= 10:
                    z = '3'
                elif attr[8] < 10:
                    z = '4'
                else:
                    z = '5'
                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '5'
                sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_D = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass

                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F") and attr[
                    15] == "biegesteif":
                    if attr[8] >= 7:
                        z = '0'
                    elif 7 > attr[8] >= 4:
                        z = '1'
                    elif 4 > attr[8] >= 3:
                        z = '2'
                    elif 3 > attr[8] >= 1:
                        z = '3'
                    elif attr[8] < 1:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F") and attr[
                    15] == "biegeweich":
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_S = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass

            if attr[5] == "DAB" and attr[6] == "A":
                if (attr[7] == "A" or attr[7] == "B") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass

            if attr[5] == "DAB" and (attr[6] == "B" or attr[6] == "C"):
                if (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '5'
                    sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "I" or attr[13] == "J"):
                    if attr[8] >= 3:
                        z = '1'
                    elif 3 > attr[8] >= 2:
                        z = '2'
                    elif 2 > attr[8]:
                        z = '3'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if attr[7] == "A" and (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    if attr[8] >= 8:
                        z = '0'
                    elif 8 > attr[8] >= 5:
                        z = '1'
                    elif 5 > attr[8] >= 3:
                        z = '2'
                    elif 3 > attr[8] >= 1:
                        z = '3'
                    elif attr[8] < 1:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[7] == "B" and (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAC" and attr[6] == "A":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAC" and attr[6] == "B":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAC" and attr[6] == "C":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAD" and attr[6] == "A":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAD" and attr[6] == "B" and attr[7] == "A":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAD" and attr[6] == "B" and attr[7] == "B":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAD" and attr[6] == "C":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F" or attr[13] == "H" or attr[13] == "I" or attr[
                    13] == "J"):
                    z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAE":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    if attr[8] >= 100:
                        z = '3'
                    elif attr[8] < 100:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    if attr[8] >= 100:
                        z = '2'
                    elif attr[8] < 100:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    if attr[8] >= 100:
                        z = '2'
                    elif 100 > attr[8] >= 10:
                        z = '3'
                    elif attr[8] < 10:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAF":
                if attr[6] == "A" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "B" and (attr[7] == "A" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "C" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "D" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "E" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "F" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "G" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "H" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "I" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "K" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "Z" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or
                        attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAG" and attr[6] == "" and attr[7] == "":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    if attr[8] >= 400:
                        z = '0'
                    elif 400 > attr[8] >= 300:
                        z = '1'
                    elif 300 > attr[8] >= 200:
                        z = '2'
                    elif 200 > attr[8] >= 100:
                        z = '3'
                    elif attr[8] < 100:
                        z = '4'
                    else:
                        z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAH":
                if (attr[6] == "B" or attr[6] == "C" or attr[6] == "D") and attr[7] == "":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "E" and attr[7] == "":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "Z" and attr[7] == "":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or
                            attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAI":
                if attr[6] == "A" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "Z" and attr[7] == "Y":
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAJ" and (attr[6] == "A" or attr[6] == "B" or attr[6] == "C"):
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAK":
                if attr[6] == "A":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        if attr[8] >= 40:
                            z = '0'
                        elif 40 > attr[8] >= 30:
                            z = '1'
                        elif 30 > attr[8] >= 20:
                            z = '2'
                        elif 20 > attr[8] >= 10:
                            z = '3'
                        elif attr[8] < 10:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_B = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        if attr[8] >= 50:
                            z = '0'
                        elif 50 > attr[8] >= 35:
                            z = '1'
                        elif 35 > attr[8] >= 20:
                            z = '2'
                        elif 20 > attr[8] >= 5:
                            z = '3'
                        elif attr[8] < 5:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "B" and (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or attr[13] == "J"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "C":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '3'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_B = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "D":
                    if (attr[7]=="A" or attr[7]=="B" or attr[7]=="C" or attr[7]=="D") and (attr[13] == "I" or attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[7] == "C") and (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "E":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        if attr[8] >= 40:
                            z = '0'
                        elif 40 > attr[8] >= 30:
                            z = '1'
                        elif 30 > attr[8] >= 20:
                            z = '2'
                        elif 20 > attr[8] >= 10:
                            z = '3'
                        elif attr[8] < 10:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        if attr[8] >= 50:
                            z = '0'
                        elif 50 > attr[8] >= 35:
                            z = '1'
                        elif 35 > attr[8] >= 20:
                            z = '2'
                        elif 20 > attr[8] >= 5:
                            z = '3'
                        elif attr[8] < 5:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "F" and (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "G" and (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "H" and (attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "I":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    continue
                if attr[6] == "J":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "K":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "L":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"  or attr[13] == "I"  or attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "E"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "M":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "N" and (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or
                            attr[13] == "I" or attr[13] == "J"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "Z":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or
                            attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAL":
                if attr[6] == "A":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "B":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or attr[13] == "J"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "C":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "D":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "E":
                    if (attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "G" or attr[13] == "H"):
                        if attr[8] >= 40:
                            z = '0'
                        elif 40 > attr[8] >= 30:
                            z = '1'
                        elif 30 > attr[8] >= 20:
                            z = '2'
                        elif 20 > attr[8] >= 10:
                            z = '3'
                        elif attr[8] < 10:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        if attr[8] >= 50:
                            z = '0'
                        elif 50 > attr[8] >= 35:
                            z = '1'
                        elif 35 > attr[8] >= 20:
                            z = '2'
                        elif 20 > attr[8] >= 5:
                            z = '3'
                        elif attr[8] < 5:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "F":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "G":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "Z":
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAM":
                if attr[6] == "A":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "B":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                        z = '4'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "C":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                        z = 'Einzelfallbetrachtung'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Zustandsklasse_S = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAN":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAO":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '1'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAP":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '1'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '0'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAQ":
                if (attr[6] == "A" or attr[6] == "C" or attr[6] == "D" or attr[6] == "F" or attr[6] == "G" or attr[
                    6] == "H" or attr[6] == "I" or attr[6] == "J" or attr[6] == "K") and (
                        attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "B") and (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '0'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "E") and (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "Z") and (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAR":
                if (attr[6] == "A" or attr[6] == "C" or attr[6] == "F") and (attr[13] == "A"):
                    z = '0'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "B" or attr[6] == "E") and (attr[13] == "A"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "D") and (attr[13] == "A"):
                    z = '1'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "G" or attr[6] == "H") and (attr[13] == "A"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "Z") and (attr[13] == "A"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBA":
                if (attr[6] == "A" or attr[6] == "B" or attr[6] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Zustandsklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBB":
                if attr[6] == "A":
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[6] == "A" or attr[6] == "B" or attr[6] == "C" or attr[6] == "Z"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBC":
                if (attr[6] == "C" or attr[6] == "Z"):
                    if attr[13] == "J":
                        if attr[8] >= 300:
                            z = '1'
                        elif 300 > attr[8] >= 100:
                            z = '2'
                        elif 100 > attr[8] >= 50:
                            z = '3'
                        elif attr[8] < 50:
                            z = '4'
                        else:
                            z = '5'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if attr[13] == "H":
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DBD":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '1'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '0'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBE":
                if (attr[6] == "A" or attr[6] == "B" or attr[6] == "C") and (attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "D":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "E" or attr[6] == "F" or attr[6] == "H" or attr[6] == "Z"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "G":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBF":
                if attr[6] == "A" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "B" or attr[6] == "C") and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "D") and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"  or attr[13] == "I"  or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Zustandsklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBG" and (attr[13] == "I" or attr[13] == "J"):
                z = '1'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DBH" and (attr[6] == "A" or attr[6] == "B" or attr[6] == "Z") and (
                    attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "Z"):
                z = '-'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCH" and (attr[6] == "A") and (attr[13] == "H"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCI" and (attr[6] == "A") and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D") and (attr[13] == "I"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCJ":
                if (attr[6] == "B" or attr[6] == "F") and (attr[13] == "F"):
                    z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[6] == "C" or attr[6] == "D" or attr[6] == "G" or attr[6] == "H") and (attr[13] == "F"):
                    z = 'Einzelfallbetrachtung'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DCL" and (attr[6] == "A" or attr[6] == "B" or attr[6] == "C") and attr[7] == "A" and (
                    attr[13] == "F"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCM" and (attr[6] == "B" or attr[6] == "C") and (attr[13] == "A"):
                z = '3'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCN" and (attr[6] == "B") and (attr[13] == "J"):
                z = 'Einzelfallbetrachtung'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDE" and (attr[6] == "A" or attr[6] == "C" or attr[6] == "D" or attr[6] == "E"):
                if attr[7] == "A":
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[7] == "B":
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Zustandsklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass

            z = '-'
            sql = f"""
                UPDATE Untersuchdat_schacht_bewertung
                SET Zustandsklasse_D = ?
                WHERE Untersuchdat_schacht_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                UPDATE Untersuchdat_schacht_bewertung
                SET Zustandsklasse_B = ?
                WHERE Untersuchdat_schacht_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                UPDATE Untersuchdat_schacht_bewertung
                SET Zustandsklasse_S = ?
                WHERE Untersuchdat_schacht_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            z = '5'
            sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_D = ?
                    WHERE Zustandsklasse_D is Null
                    """
            data = (z,)
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_B = ?
                    WHERE Zustandsklasse_B is Null
                    """
            data = (z,)
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Zustandsklasse_S = ?
                    WHERE Zustandsklasse_S is Null
                    """
            data = (z,)
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass



        sql = """CREATE TABLE IF NOT EXISTS schaechte_untersucht_bewertung AS SELECT * FROM schaechte_untersucht"""
        curs1.execute(sql)
        db.commit()

        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
            db.commit()
        except:
            pass


        # objektklasse berechnen für jede Schacht dafür abfragen

        try:
            curs.execute("""UPDATE schaechte_untersucht_bewertung 
                                    SET objektklasse_dichtheit =
                                    (SELECT min(Zustandsklasse_D) 
                                    FROM Untersuchdat_schacht_bewertung
                                    WHERE Untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam AND Zustandsklasse_D <> '-'
                                    GROUP BY Untersuchdat_schacht_bewertung.untersuchsch);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE schaechte_untersucht_bewertung 
                                    SET objektklasse_standsicherheit =
                                    (SELECT min(Zustandsklasse_S) 
                                    FROM Untersuchdat_schacht_bewertung
                                    WHERE Untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam AND Zustandsklasse_S <> '-'
                                    GROUP BY Untersuchdat_schacht_bewertung.untersuchsch);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""UPDATE schaechte_untersucht_bewertung 
                                    SET objektklasse_betriebssicherheit =
                                    (SELECT min(Zustandsklasse_B) 
                                    FROM Untersuchdat_schacht_bewertung
                                    WHERE Untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam AND Zustandsklasse_B <> '-'
                                    GROUP BY Untersuchdat_schacht_bewertung.untersuchsch);""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update schaechte_untersucht_bewertung 
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update schaechte_untersucht_bewertung 
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""update schaechte_untersucht_bewertung 
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            db.commit()
        except:
            pass

        try:
            curs.execute("""Update
                                    schaechte_untersucht_bewertung
                                    set
                                    objektklasse_gesamt =
                                    (Case
                                     When objektklasse_dichtheit <= objektklasse_standsicherheit And objektklasse_dichtheit <= objektklasse_betriebssicherheit Then objektklasse_dichtheit
                                     When objektklasse_standsicherheit <= objektklasse_dichtheit And objektklasse_standsicherheit <= objektklasse_betriebssicherheit Then objektklasse_standsicherheit
                                     When objektklasse_betriebssicherheit <= objektklasse_dichtheit And objektklasse_betriebssicherheit <= objektklasse_standsicherheit Then objektklasse_betriebssicherheit
                                     Else NULL
                                     END
                                     );""")
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


        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_schacht_bewertung_dwa.qml')
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

        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/schaechte_untersucht_bewertung_dwa.qml')
        QgsProject.instance().addMapLayer(vlayer)


    def bewertung_isy_haltung(self):
        date = self.date
        db = self.db
        db_x = db
        data = db
        leitung = self.leitung
        haltung = self.haltung
        crs = self.crs

        db1 = spatialite_connect(data)
        curs1 = db1.cursor()

        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS Untersuchdat_haltung_bewertung AS SELECT * FROM Untersuchdat_haltung"""
        curs1.execute(sql)

        if haltung == True:
            sql = """
                SELECT
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    Untersuchdat_haltung_bewertung.untersuchhal
                FROM haltungen, Untersuchdat_haltung_bewertung
            """

        if leitung == True:
            sql = """
                SELECT
                    anschlussleitungen.leitnam,
                    anschlussleitungen.material,
                    anschlussleitungen.hoehe,
                    Untersuchdat_haltung_bewertung.untersuchhal
                FROM anschlussleitungen, Untersuchdat_haltung_bewertung
            """

        try:
            curs1.execute(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        for attr1 in curs1.fetchall():
            untersuchhalt = attr1[0]
            try:
                curs1.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "B", "BS", "FZ", "MA", "OB", "P", "PC", "PCC", "PHB", "SFB", "SPB", "SB", "STZ",
                            "SZB", "ZG"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass

            if attr1[1] in ["CNS", "EIS", "GFK", "GG", "GGG", "KST", "PE", "PEHD", "PH", "PP", "PVC", "PVCU", "ST"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE Untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass
            db1.commit()

        data = db
        db = spatialite_connect(data)
        curs = db.cursor()

        if haltung == True:
            sql = """
                SELECT
                    Untersuchdat_haltung_bewertung.pk,
                    Untersuchdat_haltung_bewertung.untersuchhal,
                    Untersuchdat_haltung_bewertung.untersuchrichtung,
                    Untersuchdat_haltung_bewertung.schoben,
                    Untersuchdat_haltung_bewertung.schunten,
                    Untersuchdat_haltung_bewertung.id,
                    Untersuchdat_haltung_bewertung.videozaehler,
                    Untersuchdat_haltung_bewertung.inspektionslaenge,
                    Untersuchdat_haltung_bewertung.station,
                    Untersuchdat_haltung_bewertung.timecode,
                    Untersuchdat_haltung_bewertung.kuerzel,
                    Untersuchdat_haltung_bewertung.charakt1,
                    Untersuchdat_haltung_bewertung.charakt2,
                    Untersuchdat_haltung_bewertung.quantnr1,
                    Untersuchdat_haltung_bewertung.quantnr2,
                    Untersuchdat_haltung_bewertung.streckenschaden,
                    Untersuchdat_haltung_bewertung.pos_von,
                    Untersuchdat_haltung_bewertung.pos_bis,
                    Untersuchdat_haltung_bewertung.foto_dateiname,
                    Untersuchdat_haltung_bewertung.film_dateiname,
                    Untersuchdat_haltung_bewertung.richtung,
                    Untersuchdat_haltung_bewertung.bw_bs,
                    Untersuchdat_haltung_bewertung.createdat,
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    haltungen.createdat
                FROM Untersuchdat_haltung_bewertung, Haltungen
                WHERE haltungen.haltnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat, 0, 17) = ?
            """
            data = (date, )
            curs.execute(sql, data)

        if leitung == True:
            sql = """
                SELECT
                    Untersuchdat_haltung_bewertung.pk,
                    Untersuchdat_haltung_bewertung.untersuchhal,
                    Untersuchdat_haltung_bewertung.untersuchrichtung,
                    Untersuchdat_haltung_bewertung.schoben,
                    Untersuchdat_haltung_bewertung.schunten,
                    Untersuchdat_haltung_bewertung.id,
                    Untersuchdat_haltung_bewertung.videozaehler,
                    Untersuchdat_haltung_bewertung.inspektionslaenge,
                    Untersuchdat_haltung_bewertung.station,
                    Untersuchdat_haltung_bewertung.timecode,
                    Untersuchdat_haltung_bewertung.kuerzel,
                    Untersuchdat_haltung_bewertung.charakt1,
                    Untersuchdat_haltung_bewertung.charakt2,
                    Untersuchdat_haltung_bewertung.quantnr1,
                    Untersuchdat_haltung_bewertung.quantnr2,
                    Untersuchdat_haltung_bewertung.streckenschaden,
                    Untersuchdat_haltung_bewertung.pos_von,
                    Untersuchdat_haltung_bewertung.pos_bis,
                    Untersuchdat_haltung_bewertung.foto_dateiname,
                    Untersuchdat_haltung_bewertung.film_dateiname,
                    Untersuchdat_haltung_bewertung.richtung,
                    Untersuchdat_haltung_bewertung.bw_bs,
                    Untersuchdat_haltung_bewertung.createdat,
                    anschlussleitungen.leitnam,
                    anschlussleitungen.material,
                    anschlussleitungen.hoehe,
                    anschlussleitungen.createdat
                FROM Untersuchdat_haltung_bewertung, anschlussleitungen
                WHERE anschlussleitungen.leitnam = Untersuchdat_haltung_bewertung.untersuchhal AND substr(Untersuchdat_haltung_bewertung.createdat, 0, 17) = ? 
            """
            data = (date, )
            curs.execute(sql, data)


        for attr in curs.fetchall():
            try:
                curs.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
            except:
                pass

            if (attr[21] == "biegessteif" and attr[10] == "BAA" and (attr[11] == "A")) or (attr[21] == "biegessteif" and attr[10] == "BAA" and attr[11] == "B"):
                if attr[13] < 6:
                    z='3'
                elif 6 <= attr[13] < 15:
                    z='4'
                elif attr[13] >= 15:
                    z='5'
                else:
                    z='0'
                sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                data=(z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '5'
                elif 40 <= attr[13] < 50:
                    z = '4'
                elif 25 <= attr[13] < 40:
                    z = '3'
                elif 10 <= attr[13] < 25:
                    z = '2'
                elif attr[13] < 10:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if (attr[21] == "biegeweich" and attr[10] == "BAA" and attr[11] == "A") or (attr[21] == "biegeweich" and attr[10] == "BAA" and attr[11] == "B"):
                if attr[13] >= 15:
                    z = '5'
                elif 10 <= attr[13] < 15:
                    z = '4'
                elif 6 <= attr[13] < 10:
                    z = '3'
                elif 2 <= attr[13] < 6:
                    z = '2'
                elif attr[13] < 2:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
                if attr[13] >= 50:
                    z = '5'
                elif 40 <= attr[13] < 50:
                    z = '4'
                elif 25 <= attr[13] < 40:
                    z = '3'
                elif 10 <= attr[13] < 25:
                    z = '2'
                elif attr[13] < 10:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ? 
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            # Tab A.3
            if attr[10] == "BAB":
                if attr[11] == "A" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[11] == "B") and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[11] == "B" or attr[11] == "C") and (
                        attr[12] == "A" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                    if attr[13] >= 10:
                        z = '5'
                    elif 10 > attr[13] >= 5:
                        z = '4'
                    elif 5 > attr[13] >= 2:
                        z = '3'
                    elif 2 > attr[13] >= 0.5:
                        z = '2'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[11] == "B" or attr[11] == "C") and attr[12] == "B":
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[11] == "C") and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E"):
                    z = '4'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[10] == "BAC":
                if attr[11] == "A":
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[11] == "A" or attr[11] == "B"):
                    z = '4'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "C":
                    z = '5'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[10] == "BAD":
                if attr[11] == "A":
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "B" and (attr[12] == "A" or attr[12] == "B"):
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "C":
                    z = '5'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "D":
                    z = '5'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass

            if attr[10] == "BAE":
                if attr[13] >= 100:
                    z = '3'
                elif attr[13] < 100:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 100:
                    z = '3'
                elif 100 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAF":
                if attr[11] == "A" and (attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "B" and (attr[12] == "A" or attr[12] == "E" or attr[12] == "Z"):
                    z = '2'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "C" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '2'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "D" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "E" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '4'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "F" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '2'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "G" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "H" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '4'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "I" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '5'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '4'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "J" and (
                        attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[12] == "Z"):
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "K" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '2'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "Z" and (
                        attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D" or attr[12] == "E" or attr[
                    12] == "Z"):
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[10] == "BAG":
                if attr[13] >= 75:
                    z = '5'
                elif 75 > attr[13] >= 60:
                    z = '4'
                elif 60 > attr[13] >= 40:
                    z = '3'
                elif 40 > attr[13] >= 15:
                    z = '2'
                elif attr[13] < 15:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                            UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAH":
                if (attr[11] == "B" or attr[11] == "C" or attr[11] == "D"):
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "Z":
                    z = '2'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[10] == "BAI":
                if attr[11] == "A" and attr[12] == "A":
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '1'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "A" and (attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                    z = '3'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[11] == "Z":
                    if attr[13] >= 50:
                        z = '5'
                    elif 50 > attr[13] >= 35:
                        z = '4'
                    elif 35 > attr[13] >= 20:
                        z = '3'
                    elif 20 > attr[13] >= 5:
                        z = '2'
                    elif attr[13] < 5:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[10] == "BAJ" and attr[11] == "A":
                if attr[25] <= 0.4:
                    if attr[13] >= 70:
                        z = '5'
                    elif 70 > attr[13] >= 50:
                        z = '4'
                    elif 50 > attr[13] >= 30:
                        z = '3'
                    elif 30 > attr[13] >= 20:
                        z = '2'
                    elif attr[13] < 20:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if 0.4 < attr[25] <= 0.8:
                    if attr[13] >= 80:
                        z = '5'
                    elif 80 > attr[13] >= 60:
                        z = '4'
                    elif 60 > attr[13] >= 40:
                        z = '3'
                    elif 40 > attr[13] >= 20:
                        z = '2'
                    elif attr[13] < 20:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if attr[25] > 0.8:
                    if attr[13] >= 90:
                        z = '5'
                    elif 90 > attr[13] >= 65:
                        z = '4'
                    elif 65 > attr[13] >= 40:
                        z = '3'
                    elif 40 > attr[13] >= 20:
                        z = '2'
                    elif attr[13] < 20:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                z = '1'
                sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "B":
                if attr[13] >= 30:
                    z = '5'
                elif 30 > attr[13] >= 20:
                    z = '4'
                elif 20 > attr[13] >= 15:
                    z = '3'
                elif 15 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '1'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] < 10:
                    z = '1'
                elif attr[13] >= 10:
                    z = '2'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAJ" and attr[11] == "C":
                if attr[25] <= 0.2:
                    if attr[13] >= 12:
                        z = '5'
                    elif 12 > attr[13] >= 9:
                        z = '4'
                    elif 9 > attr[13] >= 7:
                        z = '3'
                    elif 7 > attr[13] >= 5:
                        z = '2'
                    elif attr[13] < 5:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if 0.2 < attr[25] <= 0.5:
                    if attr[13] >= 6:
                        z = '5'
                    elif 6 > attr[13] >= 4:
                        z = '4'
                    elif 4 > attr[13] >= 3:
                        z = '3'
                    elif 3 > attr[13] >= 2:
                        z = '2'
                    elif attr[13] < 2:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if attr[25] > 0.5:
                    if attr[13] >= 6:
                        z = '5'
                    elif 6 > attr[13] >= 4:
                        z = '4'
                    elif 4 > attr[13] >= 3:
                        z = '3'
                    elif 3 > attr[13] >= 1:
                        z = '2'
                    elif attr[13] < 1:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                          UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                z = '1'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "A":
                if attr[13] >= 50:
                    z = '5'
                elif 50 > attr[13] >= 35:
                    z = '4'
                elif 35 > attr[13] >= 20:
                    z = '3'
                elif 20 > attr[13] >= 5:
                    z = '2'
                elif attr[13] < 5:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "B":
                z = '1'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "C":
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "D":
                if (attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if attr[12] == "C":
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_haltung_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_haltung_bewertung.pk = ?
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[10] == "BAK" and attr[11] == "E":
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 50:
                    z = '5'
                elif 50 > attr[13] >= 35:
                    z = '4'
                elif 35 > attr[13] >= 20:
                    z = '3'
                elif 20 > attr[13] >= 5:
                    z = '2'
                elif attr[13] < 5:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "F":
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "G":
                z = '1'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "H":
                z = '1'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "I":
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "J":
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "K":
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "L":
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "M":
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "N":
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAK" and attr[11] == "Z":
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and (attr[11] == "A" or attr[11] == "B") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and (attr[11] == "C" or attr[11] == "D") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "E" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                if attr[13] >= 50:
                    z = '5'
                elif 50 > attr[13] >= 35:
                    z = '4'
                elif 35 > attr[13] >= 20:
                    z = '3'
                elif 20 > attr[13] >= 5:
                    z = '2'
                elif attr[13] < 5:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "F" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and (attr[11] == "G") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAL" and attr[11] == "Z" and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "D"):
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C"):
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
            if attr[10] == "BAM" and (attr[11] == "A" or attr[11] == "C"):
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAM" and attr[11] == "B":
                z = '1'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAN":
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAO":
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BAP":
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '5'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBA" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C"):
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 30:
                    z = '5'
                elif 30 > attr[13] >= 20:
                    z = '4'
                elif 20 > attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '2'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBB" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 30:
                    z = '5'
                elif 30 > attr[13] >= 20:
                    z = '4'
                elif 20 > attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '2'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBC" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "Z"):
                if attr[13] >= 50:
                    z = '5'
                elif 50 > attr[13] >= 40:
                    z = '4'
                elif 40 > attr[13] >= 25:
                    z = '3'
                elif 25 > attr[13] >= 10:
                    z = '2'
                elif attr[13] < 10:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBD" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "Z"):
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '5'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                if attr[13] >= 30:
                    z = '5'
                elif 30 > attr[13] >= 20:
                    z = '4'
                elif 20 > attr[13] >= 10:
                    z = '3'
                elif attr[13] < 10:
                    z = '2'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (attr[11] == "D" or attr[11] == "G"):
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBE" and (
                    attr[11] == "A" or attr[11] == "B" or attr[11] == "C" or attr[11] == "D" or attr[11] == "E" or attr[
                11] == "F" or attr[11] == "G" or attr[11] == "H" or attr[11] == "Z"):
                if attr[13] >= 50:
                    z = '5'
                elif 50 > attr[13] >= 35:
                    z = '4'
                elif 35 > attr[13] >= 20:
                    z = '3'
                elif 20 > attr[13] >= 5:
                    z = '2'
                elif attr[13] < 5:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and (attr[11] == "A" or attr[11] == "B"):
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '1'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBF" and (attr[11] == "C"):
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
            if attr[10] == "BBF" and (attr[11] == "D"):
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
            if attr[10] == "BBF" and (attr[11] == "C" or attr[11] == "D"):
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBG":
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BBH" and (attr[11] == "A" or attr[11] == "B" or attr[11] == "Z") and (
                    attr[12] == "A" or attr[12] == "B" or attr[12] == "C" or attr[12] == "Z"):
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDB" and attr[11] == "A":
                z = '2'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" and attr[11] == "C" and attr[11] == "D" and attr[11] == "E") and attr[
                12] == "A":
                z = '4'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[10] == "BDE" and (attr[11] == "A" and attr[11] == "C" and attr[11] == "D" and attr[11] == "E") and attr[
                12] == "B":
                z = '3'
                sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_haltung_bewertung.pk = ?
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass

            z = '-'
            sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Schadensklasse_D = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Schadensklasse_B = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_haltung_bewertung
                    SET Schadensklasse_S = ?
                    WHERE Untersuchdat_haltung_bewertung.pk = ?
                    """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            z = '-'
            sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_D = ?
                        WHERE Schadensklasse_D is Null
                        """
            data = (z, )
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Schadensklasse_B is Null
                        """
            data = (z,)
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                        UPDATE Untersuchdat_haltung_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Schadensklasse_S is Null
                        """
            data = (z, )
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass



        try:
            curs.execute(
                """ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            curs.execute(
                """ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            curs.execute(
                """ALTER TABLE Untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            curs.execute(
                """UPDATE Untersuchdat_haltung_bewertung
                    SET vorlaufige_Schadenszahl_D = (Case 
                    WHEN Schadensklasse_D = 1  THEN 10
                    WHEN Schadensklasse_D = 2  THEN 100
                    WHEN Schadensklasse_D = 3  THEN 200
                    WHEN Schadensklasse_D = 4  THEN 300
                    WHEN Schadensklasse_D = 5  THEN 400
                    ELSE NULL
                    END
                    ) ;""")
        except:
            pass

        try:
            curs.execute(
                """UPDATE Untersuchdat_haltung_bewertung
                    SET vorlaufige_Schadenszahl_B = (Case 
                    WHEN Schadensklasse_B = 1  THEN 10
                    WHEN Schadensklasse_B = 2  THEN 100
                    WHEN Schadensklasse_B = 3  THEN 200
                    WHEN Schadensklasse_B = 4  THEN 300
                    WHEN Schadensklasse_B = 5  THEN 400
                    ELSE NULL
                    END
                    ) ;""")
        except:
            pass

        try:
            curs.execute(
                """UPDATE Untersuchdat_haltung_bewertung
                    SET vorlaufige_Schadenszahl_S = (Case 
                    WHEN Schadensklasse_S = 1  THEN 10
                    WHEN Schadensklasse_S = 2  THEN 100
                    WHEN Schadensklasse_S = 3  THEN 200
                    WHEN Schadensklasse_S = 4  THEN 300
                    WHEN Schadensklasse_S = 5  THEN 400
                    ELSE NULL
                    END
                    ) ;""")
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('Untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data=(crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass


        uri = QgsDataSourceUri()
        uri.setDatabase(db_x)
        schema = ''
        table = 'Untersuchdat_haltung_bewertung'
        geom_column = 'geom'
        uri.setDataSource(schema, table, geom_column)
        Untersuchdat_haltung_bewertung = 'Untersuchdat_haltung_bewertung'
        vlayer = QgsVectorLayer(uri.uri(), Untersuchdat_haltung_bewertung, 'spatialite')
        x = QgsProject.instance()
        try:
            x.removeMapLayer(x.mapLayersByName(Untersuchdat_haltung_bewertung)[0].id())
        except:
            pass


        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_haltung_bewertung_isy.qml')
        QgsProject.instance().addMapLayer(vlayer)


        sql = """CREATE TABLE IF NOT EXISTS haltungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
        curs.execute(sql)


        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Lage_am_Umfang TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data=(crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

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


        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/haltungen_untersucht_bewertung_isy.qml')
        QgsProject.instance().addMapLayer(vlayer)


    def bewertung_isy_schacht(self):
        date = self.date
        db = self.db
        db_x = db
        crs = self.crs

        data = db
        db1 = spatialite_connect(data)
        curs1 = db1.cursor()
        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS Untersuchdat_schacht_bewertung AS SELECT * FROM Untersuchdat_schacht"""
        curs1.execute(sql)

        sql = """
            SELECT
                haltungen.haltnam,
                haltungen.rohrtyp,
                haltungen.hoehe,
                Untersuchdat_schacht_bewertung.untersuchsch
            FROM Haltungen, Untersuchdat_schacht_bewertung
        """
        try:
            curs1.execute(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Schächte konnte nicht ermittelt werden",
                                           level=Qgis.Critical)

        for attr1 in curs1.fetchall():

            untersuchhalt = attr1[0]
            try:
                curs1.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "B", "BS", "FZ", "MA", "OB", "P", "PC", "PCC", "PHB", "SFB", "SPB", "SB", "STZ",
                            "SZB", "ZG"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass

            if attr1[1] in ["CNS", "EIS", "GFK", "GG", "GGG", "KST", "PE", "PEHD", "PH", "PP", "PVC", "PVCU", "ST"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE Untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    curs1.execute(sql, data)
                except:
                    pass
            db1.commit()

        data = db
        db = spatialite_connect(data)
        curs = db.cursor()

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
                Untersuchdat_schacht_bewertung.pos_von,
                Untersuchdat_schacht_bewertung.pos_bis,
                Untersuchdat_schacht_bewertung.bereich,
                Untersuchdat_schacht_bewertung.foto_dateiname,
                Untersuchdat_schacht_bewertung.bw_bs,
                Untersuchdat_schacht_bewertung.createdat
            FROM Untersuchdat_schacht_bewertung
            WHERE substr(Untersuchdat_schacht_bewertung.createdat, 0, 17) = ? 
        """
        data=(date,)

        curs.execute(sql, data)


        for attr in curs.fetchall():
            try:
                curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
            except:
                pass
            try:
                curs.execute("""ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
            except:
                pass

            if attr[5] == "DAA" and (attr[6] == "A" or attr[6] == "B") and (
                    attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F") and attr[
                15] == "biegeweich":
                if attr[8] >= 40:
                    z = '5'
                elif 40 > attr[8] >= 30:
                    z = '4'
                elif 30 > attr[8] >= 20:
                    z = '3'
                elif 20 > attr[8] >= 10:
                    z = '2'
                elif attr[8] < 10:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAA" and (attr[6] == "A" or attr[6] == "B") and (
                    attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F") and attr[
                15] == "biegesteif":
                if attr[8] >= 40:
                    z = '5'
                elif 40 > attr[8] >= 30:
                    z = '4'
                elif 30 > attr[8] >= 20:
                    z = '3'
                elif 20 > attr[8] >= 10:
                    z = '2'
                elif attr[8] < 10:
                    z = '1'
                else:
                    z = '0'
                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '3'
                sql = f"""
                      UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_S = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DAB" and attr[6] == "A":
                if (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                        attr[13] == "I" or attr[13] == "J"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[7] == "A" or attr[7] == "B") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAB" and (attr[6] == "B"):
                if (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
            if attr[5] == "DAB" and (attr[6] == "C"):
                if (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
            if attr[5] == "DAB" and (attr[6] == "B" or attr[6] == "C"):
                if (attr[7] == "A") and (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    if attr[13] >= 8:
                        z = '5'
                    elif 8 > attr[13] >= 5:
                        z = '4'
                    elif 5 > attr[13] >= 3:
                        z = '3'
                    elif 3 > attr[13] >= 1:
                        z = '2'
                    elif attr[13] < 1:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[7] == "B") and (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[7] == "C" or attr[7] == "D" or attr[7] == "E") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAC" and attr[6] == "A":
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAC" and attr[6] == "B":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAC" and attr[6] == "C":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAD" and attr[6] == "A":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAD" and attr[6] == "B" and attr[7] == "A":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAD" and attr[6] == "B" and attr[7] == "B":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAD" and attr[6] == "C":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F" or attr[13] == "H" or attr[13] == "I" or attr[
                    13] == "J"):
                    z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAE":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    if attr[8] >= 100:
                        z = '2'
                    elif attr[8] < 100:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    if attr[8] >= 100:
                        z = '3'
                    elif attr[8] < 100:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    if attr[8] > 100:
                        z = '3'
                    elif 100 >= attr[8] > 10:
                        z = '2'
                    elif attr[8] <= 10:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAF":
                if attr[6] == "A" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "B" and (attr[7] == "A" or attr[7] == "E" or attr[7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "C" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "D" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "E" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "F" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "G" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "H" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (
                        attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "I" and (
                        attr[7] == "A" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[7] == "Z"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '5'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    continue
                if attr[6] == "K" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z") and (attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "Z" and (
                        attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D" or attr[7] == "E" or attr[
                    7] == "Z"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    continue
            if attr[5] == "DAG" and attr[6] == "" and attr[7] == "":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    if attr[8] >= 400:
                        z = '5'
                    elif 400 > attr[8] >= 300:
                        z = '4'
                    elif 300 > attr[8] >= 200:
                        z = '3'
                    elif 200 > attr[8] >= 100:
                        z = '2'
                    elif attr[8] < 100:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAH":
                if (attr[6] == "B" or attr[6] == "C" or attr[6] == "D") and attr[7] == "":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "Z" and attr[7] == "":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAI":
                if attr[6] == "A" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "Z" and attr[7] == "":
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAJ" and (attr[6] == "A" or attr[6] == "B" or attr[6] == "C"):
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '1'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAK":
                if attr[6] == "A" and (
                        attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    if attr[8] >= 40:
                        z = '5'
                    elif 40 > attr[8] >= 30:
                        z = '4'
                    elif 30 > attr[8] >= 20:
                        z = '3'
                    elif 20 > attr[8] >= 10:
                        z = '2'
                    elif attr[8] < 10:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "A" and (attr[13] == "I" or attr[13] == "J"):
                    if attr[8] >= 0:
                        z = '5'
                    elif 50 > attr[8] >= 35:
                        z = '4'
                    elif 35 > attr[8] >= 20:
                        z = '3'
                    elif 20 > attr[8] >= 5:
                        z = '2'
                    elif attr[8] < 5:
                        z = '1'
                    else:
                        z = '0'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[6] == "B":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "C":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "D" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C" or attr[7] == "D"):
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "D" and (attr[7] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "E":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        if attr[8] >= 40:
                            z = '5'
                        elif 40 > attr[8] >= 30:
                            z = '4'
                        elif 30 > attr[8] >= 20:
                            z = '3'
                        elif 20 > attr[8] >= 10:
                            z = '2'
                        elif attr[8] < 10:
                            z = '1'
                        else:
                            z = '0'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        if attr[8] >= 50:
                            z = '5'
                        elif 50 > attr[8] >= 35:
                            z = '4'
                        elif 35 > attr[8] >= 20:
                            z = '3'
                        elif 20 > attr[8] >= 5:
                            z = '2'
                        elif attr[8] < 5:
                            z = '1'
                        else:
                            z = '0'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "F":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "G":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "H":
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    continue
                if attr[6] == "I":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    continue
                if attr[6] == "J":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "K":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "L":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "M":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "N":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                if attr[6] == "Z":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DAL":
                if attr[6] == "A":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '3'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Schadensklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '4'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Schadensklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "B":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H" or
                            attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Schadensklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "C":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "D":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "E":
                    if (attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                            attr[13] == "F" or attr[13] == "G" or attr[13] == "H"):
                        if attr[8] >= 40:
                            z = '5'
                        elif 40 > attr[8] >= 30:
                            z = '4'
                        elif 30 > attr[8] >= 20:
                            z = '3'
                        elif 20 > attr[8] >= 10:
                            z = '2'
                        elif attr[8] < 10:
                            z = '1'
                        else:
                            z = '0'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        if attr[8] >= 50:
                            z = '5'
                        elif 50 > attr[8] >= 35:
                            z = '4'
                        elif 35 > attr[8] >= 20:
                            z = '3'
                        elif 20 > attr[8] >= 5:
                            z = '2'
                        elif attr[8] < 5:
                            z = '1'
                        else:
                            z = '0'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "F":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "G":
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "Z":
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAM":
                if (attr[6] == "A" or attr[6] == "B" or attr[6] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Schadensklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Schadensklasse_D = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if (attr[6] == "A" or attr[13] == "C"):
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                        z = '2'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Schadensklasse_S = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "B":
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                        z = '1'
                        sql = f"""
                                UPDATE Untersuchdat_schacht_bewertung
                                    SET Schadensklasse_S = ?
                                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                    """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                continue
            if attr[5] == "DAN":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAO":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAP":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_S = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DAQ":
                if (attr[6] == "A" or attr[6] == "C" or attr[6] == "D" or attr[6] == "F" or attr[6] == "G" or attr[
                    6] == "H" or attr[6] == "I" or attr[6] == "J" or attr[6] == "K") and (
                        attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '4'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "B") and (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "E") and (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "Z") and (attr[13] == "C" or attr[13] == "D" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DAR":
                if (attr[6] == "A" or attr[6] == "C" or attr[6] == "F") and (attr[13] == "A"):
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "B" or attr[6] == "E") and (attr[13] == "A"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "D") and (attr[13] == "A"):
                    z = '4'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "G" or attr[6] == "H") and (attr[13] == "A"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "Z") and (attr[13] == "A"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBA":
                if (attr[6] == "A" or attr[6] == "B" or attr[6] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_D = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                            attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[
                                13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                                SET Schadensklasse_B = ?
                                WHERE Untersuchdat_schacht_bewertung.pk = ? 
                                """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DBB":
                if (attr[6] == "A" or attr[6] == "B" or attr[6] == "C" or attr[6] == "Z") and (
                        attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                        attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DBC":
                if (attr[6] == "C" or attr[6] == "Z"):
                    if attr[13] == "J":
                        if attr[8] >= 300:
                            z = '4'
                        elif 300 > attr[8] >= 100:
                            z = '3'
                        elif 100 > attr[8] >= 50:
                            z = '2'
                        elif attr[8] < 50:
                            z = '1'
                        else:
                            z = '0'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if attr[13] == "H":
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DBD":
                if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                    z = '3'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '5'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                    except:
                        pass
                if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                continue
            if attr[5] == "DBE":
                if (attr[6] == "A" or attr[6] == "B" or attr[6] == "C") and (attr[13] == "I" or attr[13] == "J"):
                    z = '2'
                    sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "D" or attr[6] == "E" or attr[6] == "F" or attr[6] == "G" or attr[6] == "H" or attr[
                    6] == "Z"):
                    if (attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                            attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[
                                13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if (attr[6] == "D" or attr[6] == "G"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
            if attr[5] == "DBF":
                if (attr[6] == "A" or attr[6] == "B") and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                            attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[
                                13] == "J"):
                        z = '1'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                            continue
                        except:
                            pass
                if attr[6] == "C" and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                            attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[
                                13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                if (attr[6] == "D") and (attr[7] == "A" or attr[7] == "B" or attr[7] == "C"):
                    if (attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_S = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or attr[13] == "F" or attr[13] == "H"):
                        z = '3'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "I" or attr[13] == "J"):
                        z = '4'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_D = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
                    if (attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                            attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[
                                13] == "J"):
                        z = '2'
                        sql = f"""
                            UPDATE Untersuchdat_schacht_bewertung
                            SET Schadensklasse_B = ?
                            WHERE Untersuchdat_schacht_bewertung.pk = ? 
                            """
                        data = (z, attr[0])
                        try:
                            curs.execute(sql, data)
                            db.commit()
                        except:
                            pass
            if attr[5] == "DBG" and (attr[13] == "I" or attr[13] == "J"):
                z = '4'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_D = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                except:
                    pass
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_S = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCH" and (attr[6] == "A") and (attr[13] == "H"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCI" and (attr[6] == "A") and (attr[13] == "I"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCJ":
                if (attr[6] == "B" or attr[6] == "F") and (attr[13] == "F"):
                    z = '5'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if (attr[6] == "C" or attr[6] == "D" or attr[6] == "G" or attr[6] == "H") and (attr[13] == "F"):
                    z = '2'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
            if attr[5] == "DCL" and (attr[6] == "A" or attr[6] == "B" or attr[6] == "C") and attr[7] == "A" and (
                    attr[13] == "F"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCM" and (attr[6] == "B" or attr[6] == "C") and (attr[13] == "A"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DCN" and (attr[6] == "B") and (attr[13] == "J"):
                z = '2'
                sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_B = ?
                    WHERE Untersuchdat_schacht_bewertung.pk = ? 
                    """
                data = (z, attr[0])
                try:
                    curs.execute(sql, data)
                    db.commit()
                    continue
                except:
                    pass
            if attr[5] == "DDE" and (attr[6] == "A" or attr[6] == "C" or attr[6] == "D" or attr[6] == "E"):
                if attr[7] == "A" and (
                        attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                        attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '4'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass
                if attr[7] == "B" and (
                        attr[13] == "A" or attr[13] == "B" or attr[13] == "C" or attr[13] == "D" or attr[13] == "E" or
                        attr[13] == "F" or attr[13] == "G" or attr[13] == "H" or attr[13] == "I" or attr[13] == "J"):
                    z = '3'
                    sql = f"""
                        UPDATE Untersuchdat_schacht_bewertung
                        SET Schadensklasse_B = ?
                        WHERE Untersuchdat_schacht_bewertung.pk = ? 
                        """
                    data = (z, attr[0])
                    try:
                        curs.execute(sql, data)
                        db.commit()
                        continue
                    except:
                        pass

            z = '-'
            sql = f"""
                UPDATE Untersuchdat_schacht_bewertung
                SET Schadensklasse_D = ?
                WHERE Untersuchdat_schacht_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                UPDATE Untersuchdat_schacht_bewertung
                SET Schadensklasse_B = ?
                WHERE Untersuchdat_schacht_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                UPDATE Untersuchdat_schacht_bewertung
                SET Schadensklasse_S = ?
                WHERE Untersuchdat_schacht_bewertung.pk = ?
                """
            data = (z, attr[0])
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            z = '-'
            sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_D = ?
                    WHERE Schadensklasse_D is Null
                    """
            data = (z, )
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_B = ?
                    WHERE Schadensklasse_B is Null
                    """
            data = (z,)
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass
            sql = f"""
                    UPDATE Untersuchdat_schacht_bewertung
                    SET Schadensklasse_S = ?
                    WHERE Schadensklasse_S is Null
                    """
            data = (z, )
            try:
                curs.execute(sql, data)
                db.commit()
            except:
                pass


        try:
            curs.execute(
                """ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            curs.execute(
                """ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            curs.execute(
                """ALTER TABLE Untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            curs.execute(
                """UPDATE Untersuchdat_schacht_bewertung
                    SET vorlaufige_Schadenszahl_D = (Case 
                    WHEN Schadensklasse_D = 1  THEN 10
                    WHEN Schadensklasse_D = 2  THEN 100
                    WHEN Schadensklasse_D = 3  THEN 200
                    WHEN Schadensklasse_D = 4  THEN 300
                    WHEN Schadensklasse_D = 5  THEN 400
                    ELSE NULL
                    END
                    ) ;""")
        except:
            pass

        try:
            curs.execute(
                """UPDATE Untersuchdat_schacht_bewertung
                    SET vorlaufige_Schadenszahl_B = (Case 
                    WHEN Schadensklasse_B = 1  THEN 10
                    WHEN Schadensklasse_B = 2  THEN 100
                    WHEN Schadensklasse_B = 3  THEN 200
                    WHEN Schadensklasse_B = 4  THEN 300
                    WHEN Schadensklasse_B = 5  THEN 400
                    ELSE NULL
                    END
                    ) ;""")
        except:
            pass

        try:
            curs.execute(
                """UPDATE Untersuchdat_schacht_bewertung
                    SET vorlaufige_Schadenszahl_S = (Case 
                    WHEN Schadensklasse_S = 1  THEN 10
                    WHEN Schadensklasse_S = 2  THEN 100
                    WHEN Schadensklasse_S = 3  THEN 200
                    WHEN Schadensklasse_S = 4  THEN 300
                    WHEN Schadensklasse_S = 5  THEN 400
                    ELSE NULL
                    END
                    ) ;""")
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('Untersuchdat_schacht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data=(crs,)
        try:
            curs.execute(sql,data)
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


        x = os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x + '/untersuchdat_schacht_bewertung_isy.qml')
        QgsProject.instance().addMapLayer(vlayer)

        sql = """CREATE TABLE IF NOT EXISTS schaechte_untersucht_bewertung AS SELECT * FROM schaechte_untersucht"""
        curs1.execute(sql)

        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
            db.commit()
        except:
            pass
        try:
            curs.execute("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data=(crs,)
        try:
            curs.execute(sql, data)
            db.commit()
        except:
            pass

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

        x=os.path.dirname(os.path.abspath(__file__))
        vlayer.loadNamedStyle(x+'/schaechte_untersucht_bewertung_isy.qml')
        QgsProject.instance().addMapLayer(vlayer)

