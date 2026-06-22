import os
from datetime import datetime

from qgis.core import Qgis
from qgis.utils import iface, pluginDirectory
from qkan.database.dbfunc import DBConnection

from qkan.utils import get_logger
from qkan.tools.qkan_utils import loadLayer
from qkan import enums

logger = get_logger("QKan.zustand.import")


class Zustandsklassen_funkt:
    def __init__(self, check_cb,  db_qkan: DBConnection, date, epsg, datetype):

        self.check_cb = check_cb
        self.db = db_qkan
        self.date = date
        self.crs = epsg
        self.datetype = datetype

        self.haltung=False
        self.leitung=False
        self.qmlDir = os.path.join(pluginDirectory("qkan"), "zustandsklassen")
    
    def run(self):
        check_cb = self.check_cb

        #x = os.path.dirname(os.path.abspath(__file__))
        # for file in os.listdir(x+"/Layouts"):
        #     if file.endswith(".qpt"):
        #         project = QgsProject.instance()
        #         composition = QgsPrintLayout(project)
        #         document = QDomDocument()
        #         template = open(x+"/Layouts/" + file)
        #         template_content = template.read()
        #         template.close()
        #         document.setContent(template_content)
        #         composition.loadFromTemplate(document, QgsReadWriteContext())
        #         project.layoutManager().addLayout(composition)

        self.bewertungstexte()

        if check_cb['cb7']:
            self.haltung = True
            self.leitung = False
            self.bewertungstexte_haltung()

        if check_cb['cb8']:
            self.bewertungstexte_schacht()

        if check_cb['cb10']:
            self.leitung = True
            self.haltung = False
            self.bewertungstexte_leitung()

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
            self.bewertung_dwa_neu_leitung()

        if check_cb['cb11'] and check_cb['cb12']:
            self.leitung = True
            self.haltung = False
            self.bewertung_dwa_leitung()

        if check_cb['cb11'] and check_cb['cb13']:
            self.bewertung_isy_leitung()

        if check_cb['cb16']:
            self.einzelfallbetrachtung_haltung()
            self.bewertung_dwa_neu_haltung()

        if check_cb['cb17']:
            self.einzelfallbetrachtung_schacht()
            self.bewertung_dwa_neu_schaechte()

        if check_cb['cb18']:
            self.einzelfallbetrachtung_leitung()
            self.bewertung_dwa_neu_leitung()

        if check_cb['cb19']:
            self.tab_dwa_haltung()
            self.tab_dwa_leitung()
            self.tab_dwa_schacht()

        if check_cb['cb20']:
            self.tab_isybau_haltung()
            self.tab_isybau_leitung()
            self.tab_isybau_schacht()

    def bewertungstexte(self):
        db = self.db

        sql = """CREATE TABLE IF NOT EXISTS bewertungstexte (
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        kuerzel TEXT NOT NULL,
                        charakt1 TEXT,
                        langtext TEXT
                        ) """
        db.sql(sql)

        try:
            db.sql("""INSERT INTO bewertungstexte (kuerzel, charakt1, langtext) VALUES
                        ('BAA', '', 'Verformung'),
                        ('BAB', '', 'Rissbildung'),
                         ('BAC', '', 'Rohrbruch/Einsturz'),
                         ('BAD', '', 'Defektes Mauerwerk'),
                         ('BAE', '', 'Fehlender Mörtel'),
                         ('BAF', '', 'Oberflächenschäden'),
                         ('BAG', '', 'Einragender Anschluss'),
                         ('BAH', '', 'Schadhafter Anschluss'),
                         ('BAI', '', 'Einragendes Dichtungsmaterial'),
                         ('BAJ', '', 'Verschobene Verbindung'),
                         ('BAK', 'A', 'Feststellung der Innenauskleidung: Innenauskleidung abgelöst'),
                         ('BAK', 'B', 'Feststellung der Innenauskleidung: Innenauskleidung verfärbt'),
                         ('BAK', 'C', 'Feststellung der Innenauskleidung: Endstelle der Auskleidung schadhaft'),
                         ('BAK', 'D', 'Feststellung der Innenauskleidung: Faten in der Auskleidung'),
                         ('BAK', 'E', 'Feststellung der Innenauskleidung: Blasen oder Beulen in der Auskleidung nach innen'),
                         ('BAK', 'F', 'Feststellung der Innenauskleidung: Beulen aussen'),
                         ('BAK', 'G', 'Feststellung der Innenauskleidung: Ablösen der Innenhaut/Beschichtung'),
                         ('BAK', 'H', 'Feststellung der Innenauskleidung: Ablösen der Abdeckung der Verbindungsnaht'),
                         ('BAK', 'I', 'Feststellung der Innenauskleidung: Riss oder Spalt (einschließlich schadhafter Schweissnaht'),
                         ('BAK', 'J', 'Feststellung der Innenauskleidung: Loch in der Auskleidung'),
                         ('BAK', 'K', 'Feststellung der Innenauskleidung: Auskleidungsverbindung defekt'),
                         ('BAK', 'L', 'Feststellung der Innenauskleidung: Auskleidungswerkstoff erscheint weich'),
                         ('BAK', 'M', 'Feststellung der Innenauskleidung: Harz fehlt im Laminat'),
                         ('BAK', 'N', 'Feststellung der Innenauskleidung: Ende der Auskleidung ist nicht abgedichtet, um das Rohr oder den Schacht aufzunehmen'),
                         ('BAK', 'Z', 'Feststellung der Innenauskleidung: Anderer Auskleidungsschaden'),
                         ('BAL', 'A', 'Schadhafte Reperatur: Wand fehlt teilweise'),
                         ('BAL', 'B', 'Schadhafte Reperatur: Reperatur zur Abdichtung eines Lochs ist schadhaft'),
                         ('BAL', 'C', 'Schadhafte Reperatur: Ablösen des Reperaturwerkstofes vom Basisrohr'),
                         ('BAL', 'D', 'Schadhafte Reperatur: fehlender Reperaturwerkstoff an der Kontaktfläche'),
                         ('BAL', 'E', 'Schadhafte Reperatur: überschüssiger Reperaturwerkstoff, der ein Hindernis darstellt'),
                         ('BAL', 'P', 'Schadhafte Reperatur: Loch im Reperaturwerkstoff'),
                         ('BAL', 'G', 'Schadhafte Reperatur: Riss im Reperaturwerkstoff'),
                         ('BAL', 'Z', 'Schadhafte Reperatur: Andere'),
                         ('BAM', '', 'Schadhafte Schweissnaht'),
                         ('BAN', '', 'Poroeses Rohr'),
                         ('BAO', '', 'Boden sichtbar'),
                         ('BAP', '', 'Hohlraum sichtbar'),
                         ('BBA', '', 'Wurzeln'),
                         ('BBB', '', 'Anhaftende Stoffe'),
                         ('BBC', '', 'Ablagerungen'),
                         ('BBD', '', 'Eindringen von Bodenmaterial'),
                         ('BBE', '', 'Andere Hindernisse'),
                         ('BBF', '', 'Infiltration'),
                         ('BBG', '', 'Exfiltration'),
                         ('BBH', '', 'Ungeziefer'),
                         ('BCA', '', 'Anschluss'),
                         ('BCB', 'A', 'Punktuelle Reperatur: Reperatur mit Injektionstechnik'),
                         ('BCB', 'B', 'Punktuelle Reperatur: Reperatur mit Roboter'),
                         ('BCB', 'C', 'Punktuelle Reperatur: Reperatur mit partieller Auskleidungs-/Manchettentechnik'),
                         ('BCB', 'D', 'Punktuelle Reperatur: Zulaufeinbindung'),
                         ('BCB', 'E', 'Punktuelle Reperatur: Reperatur Rohrwand manuell'),
                         ('BCB', 'F', 'Punktuelle Reperatur: Reperatur Rohrverbindung manuell'),
                         ('BCB', 'G', 'Punktuelle Reperatur: Ringspalt-/-raumdichtung (der Auskleidung) zum Anschluss an Schacht/Inspektionsöffnung'),
                         ('BCB', 'H', 'Punktuelle Reperatur: Zulauföffnung ohne Einbindung (Auskleidung)'),
                         ('BCB', 'I', 'Punktuelle Reperatur: Rohr ausgetauscht'),
                         ('BCB', 'Z', 'Punktuelle Reperatur: sonstige Technink'),
                         ('BCC', '', 'Krümmung der Leitung'),
                         ('BCD', '', 'Anfangsknoten'),
                         ('BCE', '', 'Endknoten'),
                         ('BDA', '', 'Allgemeines Foto'),
                         ('BDB', 'AA', 'Rissbildung'),
                         ('BDB', 'AB', 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, uebergestuelpt, gerade'),
                         ('BDB', 'AC', 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, eingesteckt, abgewinkelt'),
                         ('BDB', 'AD', 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, uebergestuelpt, abgewinkelt'),
                         ('BDB', 'AE', 'Allgemeine Anmerkung: Verbindung zweier Rohre ohne Fomrstück, stumpf aneinandergestossen'),
                         ('BDB', 'BA', 'Allgemeine Anmerkung: Verschluss eines Rohrs durch Abmauerung'),
                         ('BDB', 'BB', 'Allgemeine Anmerkung: Verschluss eines Rohrs durch Moertel'),
                         ('BDB', 'BC', 'Allgemeine Anmerkung: Verschluss eines Rohrs durch Deckel (Muffenstopfen)'),
                         ('BDC', '', 'Inspektion endet vor dem Endknoten'),
                         ('BDD', '', 'Wasserspiegel'),
                         ('BDE', '', 'Zufluss aus einem Anschluss'),
                         ('BDF', '', 'Atmosphäre in der Leitung'),
                         ('BDG', '', 'Keine Sicht'),
                         ('DAA', '', 'Verformung'),
                         ('DAB', '', 'Rissbildung'),
                         ('DAC', '', 'Bruch/Einsturz'),
                         ('DAD', '', 'Defektes Mauerwerk'),
                         ('DAE', '', 'Fehlender Moertel'),
                         ('DAF', '', 'Oberflaechenschaden'),
                         ('DAG', '', 'Einragender Anschluss'),
                         ('DAH', '', 'Schadhafter Anschluss'),
                         ('DAI', '', 'Einragendes Dichtungsmaterial'),
                         ('DAJ', '', 'Verschobene Verbindung'),
                         ('DAK', 'A', 'Feststellung der Innenauskleidung: Innenauskleidung abgeloest'),
                         ('DAK', 'B', 'Feststellung der Innenauskleidung: Innenauskleidung verfaerbt'),
                         ('DAK', 'C', 'Feststellung der Innenauskleidung: Endstelle der Auskleidung schadhaft'),
                         ('DAK', 'D', 'Feststellung der Innenauskleidung: Falten in der Innenauskleidung'),
                         ('DAK', 'E', 'Feststellung der Innenauskleidung: Blasen oder Beulen in der Auskleidung innen'),
                         ('DAK', 'F', 'Feststellung der Innenauskleidung: Beulen aussen'),
                         ('DAK', 'G', 'Feststellung der Innenauskleidung: Abloesen der Innenhaut/Beschichtung'),
                         ('DAK', 'H', 'Feststellung der Innenauskleidung: Abloesen der Abdeckung der Verbindungsnaht'),
                         ('DAK', 'I', 'Feststellung der Innenauskleidung: Riss oder Spalt (einschliesslich schadhafter Schweissnaht)'),
                         ('DAK', 'J', 'Feststellung der Innenauskleidung: Loch in der Auskleidung'),
                         ('DAK', 'K', 'Feststellung der Innenauskleidung: Auskleidungsverbindung defekt'),
                         ('DAK', 'L', 'Feststellung der Innenauskleidung: Auskleidungswerkstoff erscheint weich'),
                         ('DAK', 'M', 'Feststellung der Innenauskleidung: Harz fehlt im Laminat'),
                         ('DAK', 'N', 'Feststellung der Innenauskleidung: Ende der Auskleidung ist nicht abgedichtet, um das Rohr oder den Schacht aufzunehmen'),
                         ('DAK', 'Z', 'Feststellung der Innenauskleidung: Anderer Auskleidungsschaden'),
                         ('DAL', 'A', 'Schadhafte Reperatur: Wand fehlt teilweise'),
                         ('DAL', 'B', 'Schadhafte Reperatur: Reperatur zur Abdichtung eines Lochs ist schadhaft'),
                         ('DAL', 'C', 'Schadhafte Reperatur: Abloesen des Reperaturwerkstoffs vom Basisrohr'),
                         ('DAL', 'D', 'Schadhafte Reperatur: fehlender Reperaturwerkstoff an der Kontaktflaeche'),
                         ('DAL', 'E', 'Schadhafte Reperatur: ueberschuessiger Reperaturwerkstof, der ein Hindernis darstellt'),
                         ('DAL', 'F', 'Schadhafte Reperatur: Loch im Reperaturwerkstoff'),
                         ('DAL', 'G', 'Schadhafte Reperatur: Riss im Reperaturwerkstoff'),
                         ('DAL', 'Z', 'Schadhafte Reperatur: Andere'),
                         ('DAM', '', 'Schadhafte Schweissnaht'),
                         ('DAN', '', 'Poroese Wand'),
                         ('DAO', '', 'Boden sichtbar'),
                         ('DAP', '', 'Hohlraum sichtbar'),
                         ('DAQ', '', 'Schadhafte Steighilfen'),
                         ('DAR', '', 'Schaeden an Abdeckung oder Rahmen'),
                         ('DBA', '', 'Wurzeln'),
                         ('DBB', '', 'Anhaftene Stoffe'),
                         ('DBC', '', 'Ablagerungen'),
                         ('DBD', '', 'Eindringen von Bodenmaterial'),
                         ('DBE', '', 'Andere Hindernisse'),
                         ('DBF', '', 'Infiltration'),
                         ('DBG', '', 'Exfiltration'),
                         ('DBH', '', 'Ungeziefer'),
                         ('DCA', '', 'Anschluss'),
                         ('DCB', 'A', 'Punktuelle Reperatur: Reperatur mit Injektionstechnik'),
                         ('DCB', 'B', 'Punktuelle Reperatur: Reperatur Bauteilwandung'),
                         ('DCB', 'C', 'Punktuelle Reperatur: Reperatur Bauteilverbindung'),
                         ('DCB', 'D', 'Punktuelle Reperatur: Ringsplat-/-raumabdichtung(Auskleidung in Kanaelen/Leitungen) zum Anschuss an Schacht/Inspektionsoeffnung'),
                         ('DCB', 'E', 'Punktuelle Reperatur: Anschlusseinbindung manuell'),
                         ('DCB', 'F', 'Punktuelle Reperatur: Anschlusseoeffnung ohne Einbindung(Auskleidung)'),
                         ('DCB', 'G', 'Punktuelle Reperatur: Schachtbauteil ausgetauscht'),
                         ('DCB', 'Z', 'Punktuelle Reperatur: Reperatur sonstige Technik'),
                         ('DCG', '', 'Anschlussleitung'),
                         ('DCH', '', 'Auftritt'),
                         ('DCI', '', 'Gerinne'),
                         ('DCJ', '', 'Sicherheitsketten/-balken'),
                         ('DCK', '', 'Abflussregulierung'),
                         ('DCL', '', 'Rohrdurchfuehrung durch andere Abwasserleitung'),
                         ('DCM', '', 'Schmutzfaenger unter der Abdeckung'),
                         ('DCN', '', 'Schlammfang in der Sohle'),
                         ('DCO', '', 'Querschnitt'),
                         ('DDA', '', 'Allgemeines Foto'),
                         ('DDB', '', 'Allgemeine Anmerkung'),
                         ('DDC', '', 'Inspektion nicht vollstaendig durchgefuehrt'),
                         ('DDD', '', 'Wasserspiegel'),
                         ('DDE', '', 'Zufluss aus einem Anschluss'),
                         ('DDF', '', 'Atmosphäre im Schacht oder in der Inspektionsoeffnung'),
                         ('DDG', '', 'Keine Sicht')
                         ;""")
            db.commit()
        except:
            pass

    def bewertungstexte_haltung(self):
        date = self.date
        db = self.db

        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        logger.debug(f'Start_Haltungstexte.liste: {datetime.now()}')

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_haltung_bewertung AS SELECT * FROM untersuchdat_haltung"""
        db.sql(sql)

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Beschreibung TEXT ;""")
            db.commit()
        except:
            pass

        sql = """SELECT CreateSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql ="""UPDATE untersuchdat_haltung_bewertung
                    SET beschreibung = (
                        SELECT bewertungstexte.langtext
                        FROM bewertungstexte
                        WHERE bewertungstexte.kuerzel = untersuchdat_haltung_bewertung.kuerzel
                         AND (
                                bewertungstexte.charakt1 IS NULL
                             OR bewertungstexte.charakt1 = ''
                             OR bewertungstexte.charakt1 = untersuchdat_haltung_bewertung.charakt1
                          )
                        LIMIT 1
                        
                    )
                    WHERE EXISTS (
                        SELECT 1
                        FROM bewertungstexte
                        WHERE bewertungstexte.kuerzel = untersuchdat_haltung_bewertung.kuerzel
                        AND (
                                bewertungstexte.charakt1 IS NULL
                             OR bewertungstexte.charakt1 = ''
                             OR bewertungstexte.charakt1 = untersuchdat_haltung_bewertung.charakt1
                          )
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_haltung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_haltung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                          )
                        );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        logger.debug(f'Ende_Haltungstexte.liste: {datetime.now()}')

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value,
            table='untersuchdat_haltung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_haltung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

    def bewertungstexte_leitung(self):
        date = self.date
        db = self.db
        data = db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        logger.debug(f'Start_Haltungstexte.liste: {datetime.now()}')

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_anschlussleitung_bewertung AS SELECT * FROM untersuchdat_anschlussleitung"""
        db.sql(sql)

        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        sql = """SELECT CreateSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """UPDATE untersuchdat_anschlussleitung_bewertung
                            SET beschreibung = (
                                SELECT bewertungstexte.langtext
                                FROM bewertungstexte
                                WHERE bewertungstexte.kuerzel = untersuchdat_anschlussleitung_bewertung.kuerzel
                                 AND (
                                        bewertungstexte.charakt1 IS NULL
                                     OR bewertungstexte.charakt1 = ''
                                     OR bewertungstexte.charakt1 = untersuchdat_anschlussleitung_bewertung.charakt1
                                  )
                                LIMIT 1

                            )
                            WHERE EXISTS (
                                SELECT 1
                                FROM bewertungstexte
                                WHERE bewertungstexte.kuerzel = untersuchdat_anschlussleitung_bewertung.kuerzel
                                AND (
                                        bewertungstexte.charakt1 IS NULL
                                     OR bewertungstexte.charakt1 = ''
                                     OR bewertungstexte.charakt1 = untersuchdat_anschlussleitung_bewertung.charakt1
                                  )
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                                    OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                                  )
                                );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass



        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        logger.debug(f'Ende_Haltungstexte.liste: {datetime.now()}')

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HA_LEITUNGEN.value,
            table='untersuchdat_anschlussleitung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_anschlussleitung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )


    def bewertungstexte_schacht(self):
        date = self.date
        db = self.db
        data = db
        crs = self.crs

        logger.debug(f'Start_Schachttexte.liste: {datetime.now()}')

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_schacht_bewertung AS SELECT * FROM untersuchdat_schacht"""
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        sql = """UPDATE untersuchdat_schacht_bewertung
                                    SET beschreibung = (
                                        SELECT bewertungstexte.langtext
                                        FROM bewertungstexte
                                        WHERE bewertungstexte.kuerzel = untersuchdat_schacht_bewertung.kuerzel
                                         AND (
                                                bewertungstexte.charakt1 IS NULL
                                             OR bewertungstexte.charakt1 = ''
                                             OR bewertungstexte.charakt1 = untersuchdat_schacht_bewertung.charakt1
                                          )
                                        LIMIT 1

                                    )
                                    WHERE EXISTS (
                                        SELECT 1
                                        FROM bewertungstexte
                                        WHERE bewertungstexte.kuerzel = untersuchdat_schacht_bewertung.kuerzel
                                        AND (
                                                bewertungstexte.charakt1 IS NULL
                                             OR bewertungstexte.charakt1 = ''
                                             OR bewertungstexte.charakt1 = untersuchdat_schacht_bewertung.charakt1
                                          )
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_schacht_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_schacht_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                                          )
                                        );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        sql = """SELECT RecoverGeometryColumn('untersuchdat_schacht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        logger.debug(f'Ende_Schachttexte.liste: {datetime.now()}')

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_SCHAECHTE.value,
            table='untersuchdat_schacht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_schacht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )


    def bewertung_dwa_neu_haltung(self):
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung


        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                        SET objektklasse_dichtheit = q.objektklasse_dichtheit
                        FROM (
                        SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                        untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        WHERE Zustandsklasse_D <> '-'
                        GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                        WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                        SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                        FROM (
                        SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                        untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        WHERE Zustandsklasse_S <> '-'
                        GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                        WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                        SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                        FROM (
                        SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                        untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        WHERE Zustandsklasse_B <> '-'
                        GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                        WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung 
                                set objektklasse_standsicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung 
                                set objektklasse_dichtheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung 
                                set objektklasse_betriebssicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        haltungen_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_haltung_bewertung WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam)
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
                    );
                    """)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value,
            table='untersuchdat_haltung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_haltung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HALTUNGEN.value,
            table='haltungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'haltungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

    def bewertung_dwa_neu_leitung(self):
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_dichtheit = q.objektklasse_dichtheit
                            FROM (
                                SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                            FROM (
                                SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                            FROM (
                                SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung 
                                set objektklasse_standsicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung 
                                set objektklasse_dichtheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung 
                                set objektklasse_betriebssicherheit = '-'
                                WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        anschlussleitungen_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_anschlussleitung_bewertung WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam)
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
                    );
                """)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('anschlussleitungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HA_LEITUNGEN.value,
            table='untersuchdat_anschlussleitung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_anschlussleitung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HA_LEITUNGEN.value,
            table='anschlussleitungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'anschlussleitungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

    def bewertung_dwa_neu_schaechte(self):
        date = self.date
        db = self.db
        crs = self.crs

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_dichtheit = q.objektklasse_dichtheit
                            FROM (
                                SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                            FROM (
                                SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                            FROM (
                                SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        schaechte_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_schacht_bewertung WHERE untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam)
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
                    );
                    """)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_schacht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_SCHAECHTE.value,
            table='untersuchdat_schacht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_schacht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_SCHAECHTE.value,
            table='schaechte_untersucht_bewertung',
            geom_column = 'geop',
            qmlfile=os.path.join(self.qmlDir, 'schaechte_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

    def bewertung_dwa_haltung(self):
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung


        logger.debug(f'Start_Bewertung_Haltungen.liste: {datetime.now()}')
        # nach DWA

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_haltung_bewertung AS SELECT * FROM untersuchdat_haltung"""
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """CREATE TABLE IF NOT EXISTS haltungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
        db.sql(sql)

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
        except:
            pass

        if haltung is True:
            sql = """
                SELECT
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    untersuchdat_haltung_bewertung.untersuchhal
                FROM haltungen
                INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
            """

        if leitung is True:
            sql = """
                    SELECT
                        anschlussleitungen.leitnam,
                        anschlussleitungen.material,
                        anschlussleitungen.hoehe,
                        untersuchdat_haltung_bewertung.untersuchhal
                    FROM anschlussleitungen
                    INNER JOIN untersuchdat_haltung_bewertung ON anschlussleitungen.leitnam = untersuchdat_haltung_bewertung.untersuchhal
                """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchleit = attr1[0]


            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC", "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk", "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton", "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK", "GFK Glasfaserverstärkter Kunststoff",
                            "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST", "KST Nichtidentifizier Kunststoff",
                            "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP", "PP Polypropylen",
                            "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                            "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                            "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                            "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl", "NBR"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
            else:
                continue
        db.commit()


        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_haltung_bewertung set Zustandsklasse_D = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_haltung_bewertung set Zustandsklasse_B = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_haltung_bewertung set Zustandsklasse_S = NULL ;""")
        except:
            pass

        db.commit()


        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_S = (CASE
                                            WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 1 THEN 4
                                            WHEN quantnr1 < 3 THEN 3
                                            WHEN quantnr1 < 4 THEN 2
                                            WHEN quantnr1 < 7 THEN 1
                                            WHEN quantnr1 >= 7 THEN 0
                                            ELSE 5
                                        END)
                            WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegesteif'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                        Zustandsklasse_B = (CASE
                                                    WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 10 THEN 4
                                                    WHEN quantnr1 < 25 THEN 3
                                                    WHEN quantnr1 < 40 THEN 2
                                                    WHEN quantnr1 < 50 THEN 1
                                                    WHEN quantnr1 >= 50 THEN 0
                                                    ELSE 5
                                                END)
                                    WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') 
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                    Zustandsklasse_S = (CASE
                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 2 THEN 4
                                WHEN quantnr1 < 6 THEN 3
                                WHEN quantnr1 < 10 THEN 2
                                WHEN quantnr1 < 15 THEN 1
                                WHEN quantnr1 >= 15 THEN 0
                                ELSE 5
                            END)
                WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegeweich'
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_S = 4
                        WHERE kuerzel = 'BAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Zustandsklasse_D = (
                                CASE
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 2 THEN 3
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 2
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >= 3 THEN 1
                                    ELSE 5
                                END),
                        Zustandsklasse_S = (
                                CASE WHEN untersuchdat_haltung_bewertung.charakt2 = 'A' THEN
                                    CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 300 THEN
                                            CASE
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 1 THEN 3
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 2 THEN 2
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 1
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 >= 3 THEN 0
                                            ELSE 5
                                            END
                                        WHEN haltungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                            CASE
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 1 THEN 4
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 2 THEN 3
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 2
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 5 THEN 1
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 >= 5 THEN 0
                                            ELSE 5
                                            END
                                        WHEN haltungen_untersucht_bewertung.breite/1000 <= 700 THEN
                                            CASE
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 2 THEN 4
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 3
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 4 THEN 2
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 8 THEN 1
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 >= 8 THEN 0
                                            ELSE 5
                                            END
                                        ELSE
                                            CASE
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 1 THEN 4
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 3
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 5 THEN 2
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 < 8 THEN 1
                                            WHEN untersuchdat_haltung_bewertung.quantnr1 >= 8 THEN 0
                                            ELSE 5
                                            END
                                    END
                                    WHEN untersuchdat_haltung_bewertung.charakt2 = 'B' THEN 4
                                    WHEN charakt2 in ('C', 'D', 'E') THEN 'Einzelfallbetrachtung'
                                    
                                 END                       
                                )
                     FROM haltungen_untersucht_bewertung
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam
                        AND untersuchdat_haltung_bewertung.kuerzel = 'BAB' AND untersuchdat_haltung_bewertung.charakt1 in ('B', 'C') AND charakt2 in ('A','B','C','D','E')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_haltung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_haltung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'A' THEN 1
                                            WHEN charakt1 = 'B' THEN 1
                                            WHEN charakt1 = 'C' THEN 0
                                    END
                                    ),
                                    Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'B' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'C' THEN 0
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'C' THEN 0
                                    END
                                    )
                                WHERE kuerzel = 'BAC' AND charakt1 in ('A', 'B', 'C')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Zustandsklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 2
                                WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 2
                                WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 1
                                WHEN charakt1 = 'C' THEN 0
                                WHEN charakt1 = 'D' THEN 0
                        END
                        ),
                        Zustandsklasse_S = (
                        CASE WHEN charakt1 = 'A' THEN 2
                            WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 2
                            WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 1
                            WHEN charakt1 = 'C' THEN 0
                            WHEN charakt1 = 'D' THEN 0
                        END
                        ),
                        Zustandsklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                            WHEN charakt1 = 'C' THEN 'Einzelfallbetrachtung'
                            WHEN charakt1 = 'D' THEN 0
                        END
                        )
                    WHERE kuerzel = 'BAD' AND charakt1 in ('A', 'B', 'C', 'D')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 <100 THEN 4
                                        ELSE 2
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 <20 THEN 4
                                    WHEN quantnr1 <50 THEN 3
                                    WHEN quantnr1 <100 THEN 2
                                    WHEN quantnr1 >=100 THEN 1
                                END
                                )
                            WHERE kuerzel = 'BAE' 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Zustandsklasse_D = (
                        CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                                WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                        END
                        ),
                        Zustandsklasse_S = (
                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 3
                            WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                            WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                            WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 1
                            WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                            WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                            WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                        END
                        ),
                        Zustandsklasse_B = (
                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 4
                            WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                        END
                        )
                    WHERE kuerzel = 'BAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                      AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_B = (
                            CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 250 THEN
                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <10 THEN 4
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <20 THEN 3
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <30 THEN 2
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <50 THEN 1
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >=50 THEN 0
                                END
                            WHEN haltungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <10 THEN 4
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <40 THEN 3
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <60 THEN 2
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <80 THEN 1
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >=80 THEN 0
                                END
                            WHEN haltungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <10 THEN 4
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <70 THEN 3
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >=70 THEN 2
                                END
                            WHEN haltungen_untersucht_bewertung.breite/1000 > 800 THEN
                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <30 THEN 4
                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >=30 THEN 3
                                END
                            END
                            )
                        FROM haltungen_untersucht_bewertung
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam
                        AND untersuchdat_haltung_bewertung.kuerzel = 'BAG' 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_haltung_bewertung.untersuchtag) = julianday(:datumswert))*1440<=15)
                                OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_haltung_bewertung.createdat)    = julianday(:datumswert)))*1440<=15
                              );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_D = (
                            CASE WHEN charakt1 in ('B', 'C','D') THEN 2
                                WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                            END
                            ),
                            Zustandsklasse_S = (
                            CASE WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                            END
                            ),
                            Zustandsklasse_B = (
                            CASE WHEN charakt1 = 'A' THEN 3
                            END
                            )
                        WHERE kuerzel = 'BAH' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'Z')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_D = (
                            CASE WHEN charakt1 = 'A' THEN 2
                            END
                            ),
                            Zustandsklasse_B = (
                            CASE WHEN charakt1 = 'A' THEN
                                        CASE WHEN charakt2 = 'A' THEN 4
                                            WHEN  charakt2 in ('B','C','D') THEN 3
                                            END
                                WHEN charakt1 = 'Z' THEN
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 5 THEN 4
                                        WHEN quantnr1 < 20 THEN 3
                                        WHEN quantnr1 < 35 THEN 2
                                        WHEN quantnr1 < 50 THEN 1
                                        WHEN quantnr1 >= 50 THEN 0
                                    END
                            END
                            )
                        WHERE kuerzel = 'BAI' AND charakt1 in ('A', 'Z')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN untersuchdat_haltung_bewertung.charakt1 = 'A' THEN
                                            CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 400 THEN
                                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 4
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 30 THEN 3
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <50 THEN 2
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <70 THEN 1 
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >=70 THEN 0
                                                    END
                                            WHEN haltungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 4
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 40 THEN 3
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <60 THEN 2
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <90 THEN 1 
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >=90 THEN 0
                                                    END
                                            WHEN haltungen_untersucht_bewertung.breite/1000 > 800 THEN
                                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 4
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 40 THEN 3
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <65 THEN 2
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 <90 THEN 1 
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >=90 THEN 0
                                                    END
                                            END
                                        WHEN untersuchdat_haltung_bewertung.charakt1 = 'B' THEN
                                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 10 THEN 4
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 15 THEN 3
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 2
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 30 THEN 1 
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >= 30 THEN 0
                                                    END
                                        WHEN untersuchdat_haltung_bewertung.charakt1 = 'C' THEN
                                            CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 200 THEN
                                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 5 THEN 4
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 7 THEN 3
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 9 THEN 2
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 12 THEN 1 
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >= 12 THEN 0
                                                    END
                                            WHEN haltungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_haltung_bewertung. quantnr1 < 2 THEN 4
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 3
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 4 THEN 2
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 6 THEN 1 
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >= 6 THEN 0
                                                    END
                                            WHEN haltungen_untersucht_bewertung.breite/1000 > 500 THEN
                                                CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 1 THEN 4
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 3
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 4 THEN 2
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 < 6 THEN 1 
                                                    WHEN untersuchdat_haltung_bewertung.quantnr1 >= 6 THEN 0
                                                    END
                                            END
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN untersuchdat_haltung_bewertung.charakt1 = 'B' THEN 'Einzelfallbetrachtung'
        
                                    END
                                    ),
                                    Zustandsklasse_S = 4
        
                                FROM haltungen_untersucht_bewertung
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam
                                AND untersuchdat_haltung_bewertung.kuerzel = 'BAJ' AND untersuchdat_haltung_bewertung.charakt1 in ('A', 'B', 'C')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_haltung_bewertung.untersuchtag) = julianday(:datumswert))*1440<=15)
                                        OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_haltung_bewertung.createdat)    = julianday(:datumswert)))*1440<=15
                                      );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'B' THEN 4
                                        WHEN charakt1 = 'C' THEN 2
                                        WHEN charakt1 = 'I' THEN 2
                                        WHEN charakt1 = 'J' THEN 1
                                        WHEN charakt1 = 'K' THEN 2
                                        WHEN charakt1 = 'L' THEN 3
                                        WHEN charakt1 = 'M' THEN 2
                                        WHEN charakt1 = 'N' THEN 2
                                        WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN 4
                                                    WHEN quantnr1 < 20 THEN 3
                                                    WHEN quantnr1 < 35 THEN 2
                                                    WHEN quantnr1 < 50 THEN 1
                                                    WHEN quantnr1 >= 50 THEN 0
                                                    END
                                        WHEN charakt1 = 'C' THEN 2
                                        WHEN charakt1 = 'D' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'E' THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN 4
                                                    WHEN quantnr1 < 20 THEN 3
                                                    WHEN quantnr1 < 35 THEN 2
                                                    WHEN quantnr1 < 50 THEN 1
                                                    WHEN quantnr1 >= 50 THEN 0
                                                    END
                                        WHEN charakt1 = 'G' THEN 4
                                        WHEN charakt1 = 'H' THEN 4
                                        WHEN charakt1 = 'K' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                    ),
                                    Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'D' AND charakt2 = 'C' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'E' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'F' THEN 4
                                        WHEN charakt1 = 'L' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                    )
                                WHERE kuerzel = 'BAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'A' THEN 1
                                        WHEN charakt1 = 'B' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'C' THEN 2
                                        WHEN charakt1 = 'D' THEN 2
                                        WHEN charakt1 = 'F' THEN 1
                                        WHEN charakt1 = 'G' THEN 3
                                        WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'E' THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN 4
                                                    WHEN quantnr1 < 20 THEN 3
                                                    WHEN quantnr1 < 35 THEN 2
                                                    WHEN quantnr1 < 50 THEN 1
                                                    WHEN quantnr1 >= 50 THEN 0
                                                    END
                                        WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                    )
                                WHERE kuerzel = 'BAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F','G', 'Z')
                                    AND charakt2 in ('A', 'B', 'C', 'D')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_D = 2,
                            Zustandsklasse_S = (
                            CASE WHEN charakt1 in ('A', 'C') THEN 'Einzelfallbetrachtung'
                                WHEN charakt1 = 'B' THEN 3
                            END
                            )
                        WHERE kuerzel = 'BAM' AND charakt1 in ('A', 'B', 'C')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = 2,
                                    Zustandsklasse_S = 2
                                WHERE kuerzel = 'BAN' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                            Zustandsklasse_D = 1,
                                            Zustandsklasse_S = 1
                                        WHERE kuerzel = 'BAO' 
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = 1,
                                Zustandsklasse_S = 0
                            WHERE kuerzel = 'BAP' 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Zustandsklasse_D = 2,
                        Zustandsklasse_B = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                            WHEN quantnr1 < 10 THEN 3
                            WHEN quantnr1 < 20 THEN 2
                            WHEN quantnr1 < 30 THEN 1
                            WHEN quantnr1 >= 30 THEN 0
                        END
                        )
                    WHERE kuerzel = 'BBA' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN 3
                                END
                            ),
                            Zustandsklasse_B = (
                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 5 THEN 4
                                WHEN quantnr1 < 10 THEN 3
                                WHEN quantnr1 < 20 THEN 2
                                WHEN quantnr1 < 30 THEN 1
                                WHEN quantnr1 >= 30 THEN 0
                            END
                            )
                        WHERE kuerzel = 'BBB' AND charakt1 in ('A', 'B', 'C', 'Z')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_B = (
                                CASE WHEN charakt1 in ('A', 'B') THEN 4
                                    WHEN charakt1 in ('C', 'Z') THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 10 THEN 4
                                            WHEN quantnr1 < 25 THEN 3
                                            WHEN quantnr1 < 40 THEN 2
                                            WHEN quantnr1 < 50 THEN 1
                                            WHEN quantnr1 >= 50 THEN 0
                                        END
                                END
                            )
                        WHERE kuerzel = 'BBC' AND charakt1 in ('A', 'B', 'C', 'Z')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Zustandsklasse_D = 1,
                        Zustandsklasse_S = 0,
                        Zustandsklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN 3
                                        WHEN quantnr1 < 20 THEN 2
                                        WHEN quantnr1 < 30 THEN 1
                                        WHEN quantnr1 >= 30 THEN 0
                            END
                        )
                    WHERE kuerzel = 'BBD' AND charakt1 in ('A', 'B', 'C', 'D', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Zustandsklasse_D = (
                                    CASE WHEN charakt1 in ('D', 'G') THEN 2
                            END
                        ),
                        Zustandsklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 5 THEN 4
                                        WHEN quantnr1 < 20 THEN 3
                                        WHEN quantnr1 < 35 THEN 2
                                        WHEN quantnr1 < 50 THEN 1
                                        WHEN quantnr1 >= 50 THEN 0
                            END
                        )
                    WHERE kuerzel = 'BBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'A' THEN 2
                                        WHEN charakt1 in ('B', 'C') THEN 1
                                        WHEN charakt1 = 'D' THEN 1
                                    END
                                ),
                                Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'A' THEN 3
                                        WHEN charakt1 in ('B', 'C') THEN 2
                                        WHEN charakt1 = 'D' THEN 1
                                    END
                                ),
                                Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN 4
                                        WHEN charakt1 in ('B', 'C') THEN 3
                                        WHEN charakt1 = 'D' THEN 3
                                    END
                                )
                            WHERE kuerzel = 'BBF' AND charakt1 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                        Zustandsklasse_D = 1,
                                        Zustandsklasse_S = 'Einzelfallbetrachtung'
                                    WHERE kuerzel = 'BBG' 
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                                Zustandsklasse_D = 'Einzelfallbetrachtung',
                                                Zustandsklasse_B = 'Einzelfallbetrachtung'
                                            WHERE kuerzel = 'BDB' AND charakt1 in ('AA', 'AB', 'AC', 'AD', 'AE')
                                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                                        Zustandsklasse_D = 'Einzelfallbetrachtung'
                                                    WHERE kuerzel = 'BDB' AND charakt1 in ('BA', 'BB', 'BC')
                                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_B = 'Einzelfallbetrachtung'
                            WHERE kuerzel = 'BDD' AND charakt1 in ('A', 'B', 'C', 'D', 'E')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_B = (
                                    CASE WHEN charakt2 = 'A' THEN 1
                                        WHEN charakt2 = 'B' THEN 2
                                    END
                                )
                        WHERE kuerzel = 'BDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_B = '-',
                                    Zustandsklasse_S = '-',
                                    Zustandsklasse_D = '-'
                                WHERE kuerzel in ('BCD', 'BCE', 'BDC', 'BCA', 'BCB', 'BCC', 'BDA', 'BDF', 'BDG', 'BDB', 'AEC', 'AED')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Zustandsklasse_B = 'Bitte pruefen!',
                        Zustandsklasse_S = 'Bitte pruefen!',
                        Zustandsklasse_D = 'Bitte pruefen!'
                    WHERE kuerzel not NULL AND Zustandsklasse_B is NULL AND Zustandsklasse_S is NULL AND Zustandsklasse_D is NULL
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                    Zustandsklasse_B = 5
                    WHERE kuerzel not NULL AND Zustandsklasse_B is NULL 
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_S = 5
                            WHERE kuerzel not NULL AND Zustandsklasse_S is NULL 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = 5
                                    WHERE kuerzel not NULL AND Zustandsklasse_D is NULL 
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass




        sql = """SELECT CreateSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
            #db.commit()
        except:
            pass


        #Objektklasse berechnen für jede Haltung dafür abfragen

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                        SET objektklasse_dichtheit = q.objektklasse_dichtheit
                        FROM (
                        SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                        untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        WHERE Zustandsklasse_D <> '-'
                        GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                        WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                        SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                        FROM (
                        SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                        untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        WHERE Zustandsklasse_S <> '-'
                        GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                        WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                        SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                        FROM (
                        SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                        untersuchhal
                        FROM untersuchdat_haltung_bewertung
                        WHERE Zustandsklasse_B <> '-'
                        GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                        WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung 
                            set objektklasse_standsicherheit = '-'
                            WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung 
                            set objektklasse_dichtheit = '-'
                            WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung 
                            set objektklasse_betriebssicherheit = '-'
                            WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        haltungen_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_haltung_bewertung WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam)
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

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        logger.debug(f'Ende_Bewertung_Haltungen.liste: {datetime.now()}')

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value,
            table='untersuchdat_haltung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_haltung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HALTUNGEN.value,
            table='haltungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'haltungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )


    def bewertung_dwa_leitung(self):
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        logger.debug(f'Start_Bewertung_Haltungen.liste: {datetime.now()}')
        # nach DWA

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_anschlussleitung_bewertung AS SELECT * FROM untersuchdat_anschlussleitung"""
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """CREATE TABLE IF NOT EXISTS anschlussleitungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
        db.sql(sql)

        if haltung is True:
            sql = """
                        SELECT
                            haltungen.haltnam,
                            haltungen.material,
                            haltungen.hoehe,
                            untersuchdat_haltung_bewertung.untersuchhal
                        FROM haltungen
                        INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
                    """

        if leitung is True:
            sql = """
                            SELECT
                                anschlussleitungen.leitnam,
                                anschlussleitungen.material,
                                anschlussleitungen.hoehe,
                                untersuchdat_haltung_bewertung.untersuchhal
                            FROM anschlussleitungen
                            INNER JOIN untersuchdat_haltung_bewertung ON anschlussleitungen.leitnam = untersuchdat_haltung_bewertung.untersuchhal
                        """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchleit = attr1[0]
            try:
                db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                            "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk",
                            "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                            "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                            UPDATE untersuchdat_anschlussleitung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                              "GFK Glasfaserverstärkter Kunststoff",
                              "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                              "KST Nichtidentifizier Kunststoff",
                              "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                              "PP Polypropylen",
                              "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                              "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                              "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                              "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl", "NBR"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                              UPDATE untersuchdat_anschlussleitung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
            else:
                continue
        db.commit()

        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_anschlussleitung_bewertung set Zustandsklasse_D = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_anschlussleitung_bewertung set Zustandsklasse_B = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_anschlussleitung_bewertung set Zustandsklasse_S = NULL ;""")
        except:
            pass

        db.commit()

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                        Zustandsklasse_S = (CASE
                                                    WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 1 THEN 4
                                                    WHEN quantnr1 < 3 THEN 3
                                                    WHEN quantnr1 < 4 THEN 2
                                                    WHEN quantnr1 < 7 THEN 1
                                                    WHEN quantnr1 >= 7 THEN 0
                                                    ELSE 5
                                                END)
                                    WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegesteif'
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                                Zustandsklasse_B = (CASE
                                                            WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN quantnr1 < 10 THEN 4
                                                            WHEN quantnr1 < 25 THEN 3
                                                            WHEN quantnr1 < 40 THEN 2
                                                            WHEN quantnr1 < 50 THEN 1
                                                            WHEN quantnr1 >= 50 THEN 0
                                                            ELSE 5
                                                        END)
                                            WHERE kuerzel = 'BAA' AND charakt1 in ('A','B')
                                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Zustandsklasse_S = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 2 THEN 4
                                        WHEN quantnr1 < 6 THEN 3
                                        WHEN quantnr1 < 10 THEN 2
                                        WHEN quantnr1 < 15 THEN 1
                                        WHEN quantnr1 >= 15 THEN 0
                                        ELSE 5
                                    END)
                        WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegeweich'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_S = 4
                                WHERE kuerzel = 'BAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                        CASE
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 2 THEN 3
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 2
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 3 THEN 1
                                            ELSE 5
                                        END),
                                Zustandsklasse_S = (
                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.charakt2 = 'A' THEN
                                            CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 300 THEN
                                                    CASE
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 1 THEN 3
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 2 THEN 2
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 1
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 3 THEN 0
                                                    ELSE 5
                                                    END
                                                WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                                    CASE
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 1 THEN 4
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 2 THEN 3
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 2
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 5 THEN 1
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 5 THEN 0
                                                    ELSE 5
                                                    END
                                                WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 700 THEN
                                                    CASE
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 2 THEN 4
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 3
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 4 THEN 2
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 8 THEN 1
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 8 THEN 0
                                                    ELSE 5
                                                    END
                                                ELSE
                                                    CASE
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 1 THEN 4
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 3
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 5 THEN 2
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 8 THEN 1
                                                    WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 8 THEN 0
                                                    ELSE 5
                                                    END
                                                    END
                                            WHEN charakt2 = 'B' THEN 4
                                            WHEN charakt2 in ('C', 'D', 'E') THEN 'Einzelfallbetrachtung'
                                           
                                        END

                                        )
                            FROM anschlussleitungen_untersucht_bewertung
                            WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam
                            AND kuerzel = 'BAB' AND charakt1 in ('B', 'C') AND charakt2 in ('A','B','C','D','E')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'A' THEN 1
                                                    WHEN charakt1 = 'B' THEN 1
                                                    WHEN charakt1 = 'C' THEN 0
                                            END
                                            ),
                                            Zustandsklasse_S = (
                                            CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'B' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'C' THEN 0
                                            END
                                            ),
                                            Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'C' THEN 0
                                            END
                                            )
                                        WHERE kuerzel = 'BAC' AND charakt1 in ('A', 'B', 'C')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN 2
                                        WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 2
                                        WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 1
                                        WHEN charakt1 = 'C' THEN 0
                                        WHEN charakt1 = 'D' THEN 0
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' THEN 2
                                    WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 2
                                    WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 1
                                    WHEN charakt1 = 'C' THEN 0
                                    WHEN charakt1 = 'D' THEN 0
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                                    WHEN charakt1 = 'C' THEN 'Einzelfallbetrachtung'
                                    WHEN charakt1 = 'D' THEN 0
                                END
                                )
                            WHERE kuerzel = 'BAD' AND charakt1 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                        Zustandsklasse_D = (
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 <100 THEN 4
                                                ELSE 2
                                        END
                                        ),
                                        Zustandsklasse_S = (
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 <20 THEN 4
                                            WHEN quantnr1 <50 THEN 3
                                            WHEN quantnr1 <100 THEN 2
                                            WHEN quantnr1 >=100 THEN 1
                                        END
                                        )
                                    WHERE kuerzel = 'BAE' 
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                                        WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 3
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 1
                                    WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                                    WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 'Einzelfallbetrachtung'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 4
                                    WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                                END
                                )
                            WHERE kuerzel = 'BAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                              AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_B = (
                                    CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 250 THEN
                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <10 THEN 4
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <20 THEN 3
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <30 THEN 2
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <50 THEN 1
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=50 THEN 0
                                        END
                                    WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <10 THEN 4
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <40 THEN 3
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <60 THEN 2
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <80 THEN 1
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=80 THEN 0
                                        END
                                    WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <10 THEN 4
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <70 THEN 3
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=70 THEN 2
                                        END
                                    WHEN anschlussleitungen_untersucht_bewertung.breite/1000 > 800 THEN
                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <30 THEN 4
                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=30 THEN 3
                                        END
                                    END
                                    )
                                FROM anschlussleitungen_untersucht_bewertung
                                WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam
                                AND kuerzel = 'BAG' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN charakt1 in ('B', 'C','D') THEN 2
                                        WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                    ),
                                    Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN 3
                                    END
                                    )
                                WHERE kuerzel = 'BAH' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'Z')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'A' THEN 2
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN
                                                CASE WHEN charakt2 = 'A' THEN 4
                                                    WHEN  charakt2 in ('B','C','D') THEN 3
                                                    END
                                        WHEN charakt1 = 'Z' THEN
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN 4
                                                WHEN quantnr1 < 20 THEN 3
                                                WHEN quantnr1 < 35 THEN 2
                                                WHEN quantnr1 < 50 THEN 1
                                                WHEN quantnr1 >= 50 THEN 0
                                            END
                                    END
                                    )
                                WHERE kuerzel = 'BAI' AND charakt1 in ('A', 'Z')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_D = (
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'A' THEN
                                                    CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 400 THEN
                                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 4
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 30 THEN 3
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <50 THEN 2
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <70 THEN 1 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=70 THEN 0
                                                            END
                                                    WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 4
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 40 THEN 3
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <60 THEN 2
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <90 THEN 1 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=90 THEN 0
                                                            END
                                                    WHEN anschlussleitungen_untersucht_bewertung.breite/1000 > 800 THEN
                                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 4
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 40 THEN 3
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <65 THEN 2
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <90 THEN 1 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=90 THEN 0
                                                            END
                                                    END
                                                WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'B' THEN
                                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 10 THEN 4
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 15 THEN 3
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 2
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 30 THEN 1 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 30 THEN 0
                                                            END
                                                WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'C' THEN
                                                    CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 200 THEN
                                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 5 THEN 4
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 7 THEN 3
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 9 THEN 2
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 12 THEN 1 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 12 THEN 0
                                                            END
                                                    WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen' 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 2 THEN 4
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 3
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 4 THEN 2
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 6 THEN 1 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 6 THEN 0
                                                            END
                                                    WHEN anschlussleitungen_untersucht_bewertung.breite/1000 > 500 THEN
                                                        CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen' 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 1 THEN 4
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 3
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 4 THEN 2
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 6 THEN 1 
                                                            WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 6 THEN 0
                                                            END
                                                    END
                                            END
                                            ),
                                            Zustandsklasse_B = (
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'B' THEN 'Einzelfallbetrachtung'

                                            END
                                            ),
                                            Zustandsklasse_S = 4
                                        FROM anschlussleitungen_untersucht_bewertung
                                        WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam
                                        AND kuerzel = 'BAJ' AND charakt1 in ('A', 'B', 'C')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'B' THEN 4
                                                WHEN charakt1 = 'C' THEN 2
                                                WHEN charakt1 = 'I' THEN 2
                                                WHEN charakt1 = 'J' THEN 1
                                                WHEN charakt1 = 'K' THEN 2
                                                WHEN charakt1 = 'L' THEN 3
                                                WHEN charakt1 = 'M' THEN 2
                                                WHEN charakt1 = 'N' THEN 2
                                                WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                            END
                                            ),
                                            Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A' THEN
                                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN quantnr1 < 5 THEN 4
                                                            WHEN quantnr1 < 20 THEN 3
                                                            WHEN quantnr1 < 35 THEN 2
                                                            WHEN quantnr1 < 50 THEN 1
                                                            WHEN quantnr1 >= 50 THEN 0
                                                            END
                                                WHEN charakt1 = 'C' THEN 2
                                                WHEN charakt1 = 'D' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'E' THEN
                                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                            WHEN quantnr1 < 5 THEN 4
                                                            WHEN quantnr1 < 20 THEN 3
                                                            WHEN quantnr1 < 35 THEN 2
                                                            WHEN quantnr1 < 50 THEN 1
                                                            WHEN quantnr1 >= 50 THEN 0
                                                            END
                                                WHEN charakt1 = 'G' THEN 4
                                                WHEN charakt1 = 'H' THEN 4
                                                WHEN charakt1 = 'K' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                            END
                                            ),
                                            Zustandsklasse_S = (
                                            CASE WHEN charakt1 = 'D' AND charakt2 = 'C' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'E' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'F' THEN 4
                                                WHEN charakt1 = 'L' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                            END
                                            )
                                        WHERE kuerzel = 'BAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'A' THEN 1
                                                WHEN charakt1 = 'B' THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'C' THEN 2
                                                WHEN charakt1 = 'D' THEN 2
                                                WHEN charakt1 = 'F' THEN 1
                                                WHEN charakt1 = 'G' THEN 3
                                                WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                            END
                                            ),
                                            Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'E' THEN
                                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen' 
                                                            WHEN quantnr1 < 5 THEN 4
                                                            WHEN quantnr1 < 20 THEN 3
                                                            WHEN quantnr1 < 35 THEN 2
                                                            WHEN quantnr1 < 50 THEN 1
                                                            WHEN quantnr1 >= 50 THEN 0
                                                            END
                                                WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                            END
                                            )
                                        WHERE kuerzel = 'BAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F','G', 'Z')
                                            AND charakt2 in ('A', 'B', 'C', 'D')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = 2,
                                    Zustandsklasse_S = (
                                    CASE WHEN charakt1 in ('A', 'C') THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'B' THEN 3
                                    END
                                    )
                                WHERE kuerzel = 'BAM' AND charakt1 in ('A', 'B', 'C')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_D = 2,
                                            Zustandsklasse_S = 2
                                        WHERE kuerzel = 'BAN' 
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                                    Zustandsklasse_D = 1,
                                                    Zustandsklasse_S = 1
                                                WHERE kuerzel = 'BAO' 
                                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                        Zustandsklasse_D = 1,
                                        Zustandsklasse_S = 0
                                    WHERE kuerzel = 'BAP' 
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = 2,
                                Zustandsklasse_B = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen' 
                                    WHEN quantnr1 < 10 THEN 3
                                    WHEN quantnr1 < 20 THEN 2
                                    WHEN quantnr1 < 30 THEN 1
                                    WHEN quantnr1 >= 30 THEN 0
                                END
                                )
                            WHERE kuerzel = 'BBA' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = (
                                        CASE WHEN charakt1 = 'A' THEN 3
                                        END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen' 
                                        WHEN quantnr1 < 5 THEN 4
                                        WHEN quantnr1 < 10 THEN 3
                                        WHEN quantnr1 < 20 THEN 2
                                        WHEN quantnr1 < 30 THEN 1
                                        WHEN quantnr1 >= 30 THEN 0
                                    END
                                    )
                                WHERE kuerzel = 'BBB' AND charakt1 in ('A', 'B', 'C', 'Z')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_B = (
                                        CASE WHEN charakt1 in ('A', 'B') THEN 4
                                            WHEN charakt1 in ('C', 'Z') THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 10 THEN 4
                                                    WHEN quantnr1 < 25 THEN 3
                                                    WHEN quantnr1 < 40 THEN 2
                                                    WHEN quantnr1 < 50 THEN 1
                                                    WHEN quantnr1 >= 50 THEN 0
                                                END
                                        END
                                    )
                                WHERE kuerzel = 'BBC' AND charakt1 in ('A', 'B', 'C', 'Z')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = 1,
                                Zustandsklasse_S = 0,
                                Zustandsklasse_B = (
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 10 THEN 3
                                                WHEN quantnr1 < 20 THEN 2
                                                WHEN quantnr1 < 30 THEN 1
                                                WHEN quantnr1 >= 30 THEN 0
                                    END
                                )
                            WHERE kuerzel = 'BBD' AND charakt1 in ('A', 'B', 'C', 'D', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                            CASE WHEN charakt1 in ('D', 'G') THEN 2
                                    END
                                ),
                                Zustandsklasse_B = (
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN 4
                                                WHEN quantnr1 < 20 THEN 3
                                                WHEN quantnr1 < 35 THEN 2
                                                WHEN quantnr1 < 50 THEN 1
                                                WHEN quantnr1 >= 50 THEN 0
                                    END
                                )
                            WHERE kuerzel = 'BBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                        Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'A' THEN 2
                                                WHEN charakt1 in ('B', 'C') THEN 1
                                                WHEN charakt1 = 'D' THEN 1
                                            END
                                        ),
                                        Zustandsklasse_S = (
                                            CASE WHEN charakt1 = 'A' THEN 3
                                                WHEN charakt1 in ('B', 'C') THEN 2
                                                WHEN charakt1 = 'D' THEN 1
                                            END
                                        ),
                                        Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A' THEN 4
                                                WHEN charakt1 in ('B', 'C') THEN 3
                                                WHEN charakt1 = 'D' THEN 3
                                            END
                                        )
                                    WHERE kuerzel = 'BBF' AND charakt1 in ('A', 'B', 'C', 'D')
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                                Zustandsklasse_D = 1,
                                                Zustandsklasse_S = 'Einzelfallbetrachtung'
                                            WHERE kuerzel = 'BBG' 
                                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                                        Zustandsklasse_D = 'Einzelfallbetrachtung',
                                                        Zustandsklasse_B = 'Einzelfallbetrachtung'
                                                    WHERE kuerzel = 'BDB' AND charakt1 in ('AA', 'AB', 'AC', 'AD', 'AE')
                                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                                                Zustandsklasse_D = 'Einzelfallbetrachtung'
                                                            WHERE kuerzel = 'BDB' AND charakt1 in ('BA', 'BB', 'BC')
                                                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                        Zustandsklasse_B = 'Einzelfallbetrachtung'
                                    WHERE kuerzel = 'BDD' AND charakt1 in ('A', 'B', 'C', 'D', 'E')
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_B = (
                                            CASE WHEN charakt2 = 'A' THEN 1
                                                WHEN charakt2 = 'B' THEN 2
                                            END
                                        )
                                WHERE kuerzel = 'BDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_B = '-',
                                            Zustandsklasse_S = '-',
                                            Zustandsklasse_D = '-'
                                        WHERE kuerzel in ('BCD', 'BCE', 'BDC', 'BCA', 'BCB', 'BCC', 'BDA', 'BDF', 'BDG', 'BDB', 'AEC', 'AED')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_B = 'Bitte pruefen!',
                                Zustandsklasse_S = 'Bitte pruefen!',
                                Zustandsklasse_D = 'Bitte pruefen!'
                            WHERE kuerzel not NULL AND Zustandsklasse_B is NULL AND Zustandsklasse_S is NULL AND Zustandsklasse_D is NULL
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Zustandsklasse_B = 5
                            WHERE kuerzel not NULL AND Zustandsklasse_B is NULL 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_S = 5
                                    WHERE kuerzel not NULL AND Zustandsklasse_S is NULL 
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_D = 5
                                            WHERE kuerzel not NULL AND Zustandsklasse_D is NULL 
                                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass



        sql = """SELECT CreateSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
            # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT;""")
            # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
            # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
            # db.commit()
        except:
            pass

        # Objektklasse berechnen für jede Haltung dafür abfragen

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_dichtheit = q.objektklasse_dichtheit
                            FROM (
                                SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
            # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                            FROM (
                                SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
            # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                            FROM (
                                SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
            # db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung 
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            # db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung 
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            # db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung 
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            # db.commit()
        except:
            pass

        try:
            db.sql("""Update
                                anschlussleitungen_untersucht_bewertung
                               SET objektklasse_gesamt = (
                             SELECT
                              CASE
                              WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_anschlussleitung_bewertung WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam)
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

        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass


        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('anschlussleitungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        logger.debug(f'Ende_Bewertung_Haltungen.liste: {datetime.now()}')

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HA_LEITUNGEN.value,
            table='untersuchdat_anschlussleitung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_anschlussleitung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HA_LEITUNGEN.value,
            table='anschlussleitungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'anschlussleitungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )


    def bewertung_dwa_schacht(self):
        date = self.date
        db = self.db
        crs = self.crs

        # nach DWA

        logger.debug(f'Start_Bewertung_Schaechte.liste: {datetime.now()}')

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_schacht_bewertung AS SELECT * FROM untersuchdat_schacht"""
        db.sql(sql)
        sql = """CREATE TABLE IF NOT EXISTS schaechte_untersucht_bewertung AS SELECT * FROM schaechte_untersucht"""
        db.sql(sql)

        sql = """SELECT CreateSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """
            SELECT
                schaechte.schnam,
                schaechte.material,
                untersuchdat_schacht_bewertung.untersuchsch
            FROM schaechte
                INNER JOIN untersuchdat_schacht_bewertung  ON schaechte.schnam = untersuchdat_schacht_bewertung.untersuchsch
        """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)


        for attr1 in db.fetchall():
            try:
                db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC", "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk", "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton", "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK", "GFK Glasfaserverstärkter Kunststoff",
                            "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST", "KST Nichtidentifizier Kunststoff",
                            "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP", "PP Polypropylen",
                            "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                            "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                            "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                            "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()


        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_schacht_bewertung set Zustandsklasse_D = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_schacht_bewertung set Zustandsklasse_B = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_schacht_bewertung set Zustandsklasse_S = NULL ;""")
        except:
            pass

        db.commit()

        sql = f"""update untersuchdat_schacht_bewertung set
                    Zustandsklasse_S = (CASE
                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 1 THEN 4
                                WHEN quantnr1 < 3 THEN 3
                                WHEN quantnr1 < 4 THEN 2
                                WHEN quantnr1 < 7 THEN 1
                                WHEN quantnr1 >= 7 THEN 0
                            END)
                WHERE kuerzel = 'DAA' AND charakt1 in ('A','B') AND bereich in ('B', 'C', 'D', 'F') AND bw_bs = 'biegesteif'
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_S = 'Einzelfallbetrachtung'
                        WHERE kuerzel = 'DAA' AND charakt1 in ('A','B') AND bereich in ('B', 'C', 'D', 'F') AND bw_bs = 'biegeweich'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_B = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN 4
                                        WHEN quantnr1 < 20 THEN 3
                                        WHEN quantnr1 < 30 THEN 2
                                        WHEN quantnr1 < 40 THEN 1
                                        WHEN quantnr1 >= 40 THEN 0
                                    END)
                        WHERE kuerzel = 'DAA' AND charakt1 in ('A','B') AND bereich in ('B', 'C', 'D', 'F') 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_S = 4
                    WHERE kuerzel = 'DAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E') AND bereich in ('B', 'C', 'D', 'F', 'H', 'I', 'J') 
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                    Zustandsklasse_D = (
                            CASE WHEN bereich in ('C', 'D', 'E', 'F') THEN 3
                                WHEN bereich in ('I', 'J') THEN 
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 2 THEN 3
                                    WHEN quantnr1 < 3 THEN 2
                                    WHEN quantnr1 >= 3 THEN 1
                                    END
                            END),
                    Zustandsklasse_S = (
                            CASE WHEN charakt2 = 'A' THEN
                                CASE WHEN bereich in ('B', 'C', 'D', 'F') THEN
                                        CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 1 THEN 4
                                        WHEN quantnr1 < 3 THEN 3
                                        WHEN quantnr1 < 5 THEN 2
                                        WHEN quantnr1 < 8 THEN 1
                                        WHEN quantnr1 >= 8 THEN 0
                                        END
                                END
                                WHEN charakt2 = 'B' THEN 4
                                WHEN charakt2 in ('C', 'D', 'E') THEN 'Einzelfallbetrachtung'
                                END
                            )
                WHERE kuerzel = 'DAB' AND charakt1 in ('B', 'C') AND charakt2 in ('A','B','C','D','E') AND bereich in ('B', 'C', 'D', 'F', 'I', 'J')
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 1
                                        WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'B' AND bereich in ('I', 'J') THEN 1
                                        WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 1
                                        WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 0
                                    END),
                            Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'B' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H') THEN 0
                                        END
                                    ),
                            Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN 'Einzelfallbetrachtung'
                                        WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H') THEN 0
                                        END
                                    )
                        WHERE kuerzel = 'DAC' AND charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'F','H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                                WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 2
                                                WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                                WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('I', 'J') THEN 2
                                                WHEN charakt1 = 'B' AND charakt2 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                                WHEN charakt1 = 'B' AND charakt2 = 'B' AND bereich in ('I', 'J') THEN 1
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 1
                                                WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 0
                                            END),
                                    Zustandsklasse_S = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'F') THEN 2
                                                WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('C', 'D', 'F') THEN 2
                                                WHEN charakt1 = 'B' AND charakt2 = 'B' AND bereich in ('C', 'D', 'F') THEN 1
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'F') THEN 0
                                                END
                                            ),
                                    Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'F') THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'A' AND bereich in ('H','I','J') THEN 2
                                                 WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('H','I','J') THEN 2
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'F', 'H', 'I', 'J') THEN 0
                                                END
                                            )
                                WHERE kuerzel = 'DAD' AND charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 100 THEN 4
                                            WHEN quantnr1 >= 100 THEN 3
                                        END
                                    WHEN bereich in ('I', 'J') THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 100 THEN 4
                                            WHEN quantnr1 >= 100 THEN 2
                                        END
                                END),
                        Zustandsklasse_S = (
                                CASE WHEN bereich in ('C', 'D', 'F') THEN 
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN 4
                                        WHEN quantnr1 < 100 THEN 3
                                        WHEN quantnr1 >= 100 THEN 3
                                   END
                                END
                                )
                    WHERE kuerzel = 'DAE' AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN
                                       1
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN
                                         'Einzelfallbetrachtung'
                                END),
                        Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 4
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 1
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 1
                                    WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 'Einzelfallbetrachtung'
                                    WHEN charakt1 = 'J' AND charakt2 in ('B', 'C', 'D', 'E')  THEN 'Einzelfallbetrachtung'
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F', 'H') THEN 'Einzelfallbetrachtung'       
                                END
                                ),
                        Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in ('I', 'J') THEN 4
                                    WHEN charakt1 = 'J' AND charakt2 in ('B', 'C', 'D', 'E')  THEN 4
                                    WHEN charakt1 = 'K' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 3
                                    END
                                )
                    WHERE kuerzel = 'DAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                    Zustandsklasse_B = (
                            CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 100 THEN 4 
                                    WHEN quantnr1 < 200 THEN 3
                                    WHEN quantnr1 < 300 THEN 2
                                    WHEN quantnr1 < 400 THEN 1
                                    WHEN quantnr1 >= 400 THEN 0
                                    END
                            
                                WHEN bereich in ('I','J') THEN 'Einzelfallbetrachtung'
                                END
                            )
                WHERE kuerzel = 'DAG' AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN charakt1 in ('B', 'C', 'D') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                    WHEN charakt1 in ('B', 'C', 'D') AND bereich in ('I', 'J') THEN 2
                                    WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 'Einzelfallbetrachtung'
                                    END
                                )
                    WHERE kuerzel = 'DAH' AND charakt1 in ('B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                            WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C') AND bereich in ('I','J') THEN 2
                                            END
                                        ),
                                Zustandsklasse_B = (
                                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 4
                                            WHEN charakt1 = 'Z'  AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 4
                                            END
                                        )
                            WHERE kuerzel = 'DAI' AND charakt1 in ('A', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                     END
                                ),
                        Zustandsklasse_S = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'F') THEN 4
                                     END
                                )
                    WHERE kuerzel = 'DAJ' AND charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'E', 'F')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 4
                                            WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                            WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 2
                                            WHEN charakt1 = 'I' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                            WHEN charakt1 = 'I' AND bereich in ('I', 'J') THEN 2
                                            WHEN charakt1 = 'J' AND bereich in ('C', 'D', 'E', 'F') THEN 2
                                            WHEN charakt1 = 'J' AND bereich in ('I', 'J') THEN 1
                                            WHEN charakt1 = 'K' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                            WHEN charakt1 = 'K' AND bereich in ('I', 'J') THEN 2
                                            WHEN charakt1 = 'L' AND bereich in ('C', 'D', 'E', 'F') THEN 4
                                            WHEN charakt1 = 'L' AND bereich in ('I', 'J') THEN 3
                                            WHEN charakt1 = 'M' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                            WHEN charakt1 = 'M' AND bereich in ('I', 'J') THEN 2
                                            WHEN charakt1 = 'N' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 'Einzelfallbetrachtung'
                                            WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 'Einzelfallbetrachtung'
                                            END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN charakt1 = 'D' AND charakt2 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J' ) THEN 'Einzelfallbetrachtung'
                                             WHEN charakt1 = 'E' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J' ) THEN 'Einzelfallbetrachtung'
                                             WHEN charakt1 = 'F' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J' ) THEN 4
                                             WHEN charakt1 = 'L' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J' ) THEN 'Einzelfallbetrachtung'
                                             WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J' ) THEN 'Einzelfallbetrachtung'
                                             END
                                        ),
                                Zustandsklasse_B = (
                                        CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 10 THEN 4
                                                    WHEN quantnr1 < 20 THEN 3
                                                    WHEN quantnr1 < 30 THEN 2
                                                    WHEN quantnr1 < 40 THEN 1
                                                    WHEN quantnr1 >= 40 THEN 0
                                                END
                                            WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN 4
                                                    WHEN quantnr1 < 20 THEN 3
                                                    WHEN quantnr1 < 35 THEN 2
                                                    WHEN quantnr1 < 50 THEN 1
                                                    WHEN quantnr1 >= 50 THEN 0
                                                END
                                            WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 2
                                            WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D') AND bereich in ('I', 'J') THEN 'Einzelfallbetrachtung'
                                            WHEN charakt1 = 'E' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 10 THEN 4
                                                    WHEN quantnr1 < 20 THEN 3
                                                    WHEN quantnr1 < 30 THEN 2
                                                    WHEN quantnr1 < 40 THEN 1
                                                    WHEN quantnr1 >= 40 THEN 0
                                                END
                                            WHEN charakt1 = 'E' AND bereich in ('I', 'J') THEN 
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN 4
                                                    WHEN quantnr1 < 20 THEN 3
                                                    WHEN quantnr1 < 35 THEN 2
                                                    WHEN quantnr1 < 50 THEN 1
                                                    WHEN quantnr1 >= 50 THEN 0
                                                END
                                            WHEN charakt1 = 'G' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 4
                                            WHEN charakt1 = 'H' AND bereich in ('I', 'J') THEN 4
                                            WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 'Einzelfallbetrachtung'
                                            END
                                        )
                            WHERE kuerzel = 'DAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z') 
                            AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                    Zustandsklasse_D = (
                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F') THEN 2
                                WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 'Einzelfallbetrachtung'
                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 2
                                WHEN charakt1 = 'D' AND bereich in ('C', 'D', 'E', 'F') THEN 4
                                WHEN charakt1 = 'D' AND bereich in ('I', 'J') THEN 2
                                WHEN charakt1 = 'F' AND bereich in ('C', 'D', 'E', 'F') THEN 2
                                WHEN charakt1 = 'F' AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'G' AND bereich in ('C', 'D', 'E', 'F') THEN 4
                                WHEN charakt1 = 'G' AND bereich in ('I', 'J') THEN 3
                                WHEN charakt1 = 'Z'  THEN 'Einzelfallbetrachtung'
                                 END
                            ),
                    Zustandsklasse_B = (
                            CASE WHEN charakt1 = 'E' AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') THEN
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 10 THEN 4
                                    WHEN quantnr1 < 20 THEN 3
                                    WHEN quantnr1 < 30 THEN 2
                                    WHEN quantnr1 < 40 THEN 1
                                    WHEN quantnr1 >= 40 THEN 0
                                 END
                                WHEN charakt1 = 'E' AND bereich in ('I', 'J') THEN
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen' 
                                    WHEN quantnr1 < 5 THEN 4
                                    WHEN quantnr1 < 20 THEN 3
                                    WHEN quantnr1 < 3 THEN 2
                                    WHEN quantnr1 < 50 THEN 1
                                    WHEN quantnr1 >= 50 THEN 0
                                 END
                                WHEN charakt1 = 'Z'  THEN 'Einzelfallbetrachtung'
                            END
                            )
                WHERE kuerzel = 'DAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'Z') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 2
                                    WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'B' AND bereich in ('I', 'J') THEN 2
                                    WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 2
                                   END
                                ),
                        Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' AND bereich in ('B', 'C', 'D', 'F') THEN 'Einzelfallbetrachtung'
                                    WHEN charakt1 = 'B' AND bereich in ('B', 'C', 'D', 'F') THEN 4
                                    WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'F') THEN 'Einzelfallbetrachtung'
                                END
                                )
                    WHERE kuerzel = 'DAM' AND charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F') THEN 3
                                    WHEN bereich in ('I', 'J') THEN 2
                                    END
                                ),
                        Zustandsklasse_S = (
                                CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                   END
                                )
                    WHERE kuerzel = 'DAN' AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F') THEN 2
                                    WHEN bereich in ('I', 'J') THEN 1
                                    END
                                ),
                        Zustandsklasse_S = (
                                CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 1
                                   END
                                )
                    WHERE kuerzel = 'DAO' AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN bereich in ('C', 'D', 'E', 'F') THEN 2
                                            WHEN bereich in ('I', 'J') THEN 1
                                            END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 0
                                           END
                                        )
                            WHERE kuerzel = 'DAP' AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_B = (
                                CASE WHEN charakt1 in ('A', 'C', 'D', 'F', 'G', 'H', 'I', 'J', 'K') THEN 1
                                    WHEN charakt1 = 'B' THEN 0
                                    WHEN charakt1 = 'E' THEN 3
                                    WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                    END
                                )
                    WHERE kuerzel = 'DAQ' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z') AND bereich in ('C', 'D', 'F')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_B = (
                                    CASE WHEN charakt1 in ('A', 'C', 'F') THEN 0
                                        WHEN charakt1 in ('B', 'E') THEN 3
                                        WHEN charakt1 = 'D' THEN 1
                                        WHEN charakt1 in ('G', 'H') THEN 2
                                        WHEN charakt1 = 'Z' THEN 'Einzelfallbetrachtung'
                                        END
                                    )
                        WHERE kuerzel = 'DAR' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z') AND bereich = 'A'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_D = (
                                    CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                        WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN 2
                                        END
                                    ),
                            Zustandsklasse_B = (
                                    CASE WHEN charakt1 in ('A', 'B', 'C') THEN 'Einzelfallbetrachtung'
                                        END
                                    )
                        WHERE kuerzel = 'DBA' AND charakt1 in ('A', 'B', 'C')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 = 'A'  THEN 3
                                            END
                                        ),
                                Zustandsklasse_B = (
                                        CASE WHEN charakt1 in ('A', 'B', 'C', 'Z') THEN 3
                                            END
                                        )
                            WHERE kuerzel = 'DBB' AND charakt1 in ('A', 'B', 'C', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_B = (
                                    CASE WHEN charakt1 in ('C', 'Z') AND bereich = 'J' THEN 
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen' 
                                            WHEN quantnr1 < 50 THEN 4
                                            WHEN quantnr1 < 100 THEN 3
                                            WHEN quantnr1 < 300 THEN 2
                                            WHEN quantnr1 >= 300 THEN 1
                                        END
                                        WHEN charakt1 in ('C', 'Z') AND bereich = 'H' THEN 3
                                    END
                                    )
                        WHERE kuerzel = 'DBC' AND charakt1 in ('C', 'Z') AND bereich in ('J', 'H')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_D = (
                                            CASE WHEN bereich in ('C', 'D', 'E', 'F') THEN 2
                                                WHEN bereich in ('I', 'J') THEN 1
                                            END
                                            ),
                                    Zustandsklasse_S = (
                                            CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 0
                                            END
                                            ),
                                    Zustandsklasse_B = (
                                            CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 'Einzelfallbetrachtung'
                                            END
                                            )
                                WHERE kuerzel = 'DBD' AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'D' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'D' AND bereich in ('I', 'J') THEN 2
                                    WHEN charakt1 = 'G' AND bereich in ('C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 = 'G' AND bereich in ('I', 'J') THEN 2
                                END
                                ),
                        Zustandsklasse_B = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN 3
                                    WHEN charakt1 = 'D' THEN 2
                                    WHEN charakt1 in ('E', 'F', 'H', 'Z') THEN 2
                                    WHEN charakt1 = 'G' THEN 2
                                END
                                )
                    WHERE kuerzel = 'DBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z') 
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 2
                                    WHEN charakt1 in ('B', 'C') AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 1
                                    WHEN charakt1 = 'D' AND bereich in ('C', 'D', 'E', 'F', 'I', 'J') THEN 1
                                END
                                ),
                        Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                    WHEN charakt1 in ('B', 'C') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                    WHEN charakt1 = 'D' AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 1
                                END
                                ),
                        Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN 4
                                    WHEN charakt1 in ('B', 'C') THEN 3
                                    WHEN charakt1 = 'D' THEN 3
                                END
                                )
                    WHERE kuerzel = 'DBF' AND charakt1 in ('A', 'B', 'C', 'D') AND charakt2 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_D = 1,
                        Zustandsklasse_S = 'Einzelfallbetrachtung'
                    WHERE kuerzel = 'DBG' AND bereich in ('I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = 'Einzelfallbetrachtung'
                            WHERE kuerzel = 'DCH' AND charakt1 = 'A' AND bereich = 'H'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('A', 'B', 'C', 'D') THEN 'Einzelfallbetrachtung'
                                                WHEN charakt1 = 'C' AND bereich ='Y' THEN 'Einzelfallbetrachtung'
                                            END
                                            )
                            WHERE kuerzel = 'DCI' AND charakt1 in ('A', 'C') AND charakt2 in ('A', 'B', 'C', 'D', 'Y') AND bereich = 'I'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_B = (
                                        CASE WHEN charakt1 in ('B', 'F') THEN 0
                                            WHEN charakt1 in ('C', 'D', 'G', 'H') THEN 'Einzelfallbetrachtung'
                                        END
                                        )
                        WHERE kuerzel = 'DCJ' AND charakt1 in ('B', 'C', 'D', 'F', 'G', 'H') AND bereich = 'F'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_B = 'Einzelfallbetrachtung'
                    WHERE kuerzel = 'DCL' AND charakt1 in ('A', 'B', 'C') AND charakt2 = 'A' AND bereich = 'F'
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = 3
                            WHERE kuerzel = 'DCM' AND charakt1 in ('B', 'C') AND bereich = 'A'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = 'Einzelfallbetrachtung'
                            WHERE kuerzel = 'DCN' AND charakt1 = 'B' AND bereich = 'J'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Zustandsklasse_B = (
                                    CASE WHEN charakt2 = 'A'  THEN 1
                                        WHEN charakt2 = 'B' THEN 2
                                    END
                                    )
                    WHERE kuerzel = 'DDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = '-',
                                Zustandsklasse_D = '-',
                                Zustandsklasse_S = '-'
                            WHERE kuerzel in ('CED', 'DCA', 'DCB', 'DCG', 'DCK', 'DCO', 'DDA', 'DDB', 'DDC', 'DDD', 'DDF', 'DDG')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = 'Bitte pruefen!',
                                Zustandsklasse_S = 'Bitte pruefen!',
                                Zustandsklasse_D = 'Bitte pruefen!'
                            WHERE kuerzel not NULL AND Zustandsklasse_B is NULL AND Zustandsklasse_S is NULL AND Zustandsklasse_D is NULL
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_B = 5
                            WHERE kuerzel not NULL AND Zustandsklasse_B is NULL 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_S = 5
                                    WHERE kuerzel not NULL AND Zustandsklasse_S is NULL 
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                            Zustandsklasse_D = 5
                                            WHERE kuerzel not NULL AND Zustandsklasse_D is NULL 
                                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        #db.commit()
        sql = """SELECT CreateSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
            #db.commit()
        except:
            pass


        # objektklasse berechnen für jede Schacht dafür abfragen

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_dichtheit = q.objektklasse_dichtheit
                            FROM (
                                SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                            FROM (
                                SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                            FROM (
                                SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_standsicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_dichtheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
            #db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        schaechte_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_schacht_bewertung WHERE untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam)
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
                    );"""
                    )
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_schacht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_SCHAECHTE.value,
            table='untersuchdat_schacht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_schacht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

        logger.debug(f'Ende_Bewertung_Schaechte.liste: {datetime.now()}')

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_SCHAECHTE.value,
            table='schaechte_untersucht_bewertung',
            geom_column = 'geop',
            qmlfile=os.path.join(self.qmlDir, 'schaechte_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

    def bewertung_isy_haltung(self):
        date = self.date
        db = self.db

        leitung = self.leitung
        haltung = self.haltung
        crs = self.crs

        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_haltung_bewertung AS SELECT * FROM untersuchdat_haltung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """CREATE TABLE IF NOT EXISTS haltungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
        db.sql(sql)

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
        except:
            pass

        if haltung is True:
            sql = """
                SELECT
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    untersuchdat_haltung_bewertung.untersuchhal
                FROM haltungen
                INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
            """

        if leitung is True:
            sql = """
                SELECT
                    anschlussleitungen.leitnam,
                    anschlussleitungen.material,
                    anschlussleitungen.hoehe,
                    untersuchdat_haltung_bewertung.untersuchhal
                FROM anschlussleitungen
                INNER JOIN untersuchdat_haltung_bewertung  ON anschlussleitungen.leitnam = untersuchdat_haltung_bewertung.untersuchhal
            """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():
            untersuchhalt = attr1[0]


            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC", "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk", "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton", "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK", "GFK Glasfaserverstärkter Kunststoff",
                            "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST", "KST Nichtidentifizier Kunststoff",
                            "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP", "PP Polypropylen",
                            "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                            "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                            "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                            "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()


        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_haltung_bewertung set Schadensklasse_D = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_haltung_bewertung set Schadensklasse_S = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_haltung_bewertung set Schadensklasse_B = NULL ;""")
        except:
            pass

        db.commit()

        sql = f"""update untersuchdat_haltung_bewertung set
                    Schadensklasse_S = (CASE
                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 6 THEN 3
                                WHEN quantnr1 < 15 THEN 4
                                WHEN quantnr1 >= 15 THEN 5
                            END)
                WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegesteif'
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Schadensklasse_S = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 2 THEN 1
                                        WHEN quantnr1 < 6 THEN 2
                                        WHEN quantnr1 < 10 THEN 3
                                        WHEN quantnr1 < 15 THEN 4
                                        WHEN quantnr1 >= 15 THEN 5
                                    END)
                        WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegeweich'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_B = (CASE
                                    WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 10 THEN 1
                                    WHEN quantnr1 < 25 THEN 2
                                    WHEN quantnr1 < 40 THEN 3
                                    WHEN quantnr1 < 50 THEN 4
                                    WHEN quantnr1 >= 50 THEN 5
                                END)
                    WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs IN ('biegesteif','biegeweich')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Schadensklasse_S = 1,
                                    Schadensklasse_D = 1
                                WHERE kuerzel = 'BAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                                CASE
                                    WHEN charakt1 = 'B' THEN 3
                                    WHEN charakt1 = 'C' THEN 1
                                END),
                        Schadensklasse_S = (
                                CASE WHEN charakt2 = 'B' THEN 1
                                    WHEN charakt2 in ('A', 'C', 'D', 'E') THEN 
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 2 AND quantnr1 > 0.5 THEN 2
                                            WHEN quantnr1 < 5 THEN 3
                                            WHEN quantnr1 < 10 THEN 4
                                            WHEN quantnr1 >= 10 THEN 5
                                    END
                                END
                                )
                    WHERE kuerzel = 'BAB' AND charakt1 in ('B', 'C') AND charakt2 in ('A','B','C','D','E')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 4
                                WHEN charakt1 = 'B' THEN 4
                                WHEN charakt1 = 'C' THEN 5
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN charakt1 = 'A' THEN 3
                            WHEN charakt1 = 'B' THEN 3
                            WHEN charakt1 = 'C' THEN 5
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN 3
                            WHEN charakt1 = 'C' THEN 5
                        END
                        )
                    WHERE kuerzel = 'BAC' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 3
                                WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 3
                                WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 3
                                WHEN charakt1 = 'C' THEN 5
                                WHEN charakt1 = 'D' THEN 5
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN charakt1 = 'A' THEN 3
                            WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 3
                            WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 3
                            WHEN charakt1 = 'C' THEN 5
                            WHEN charakt1 = 'D' THEN 5
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN 2
                            WHEN charakt1 = 'C' THEN 5
                            WHEN charakt1 = 'D' THEN 5
                        END
                        )
                    WHERE kuerzel = 'BAD' AND charakt1 in ('A', 'B', 'C', 'D')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 <100 THEN 1
                                ELSE 3
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                            WHEN quantnr1 <20 THEN 1
                            WHEN quantnr1 <50 THEN 2
                            WHEN quantnr1 <100 THEN 3
                            WHEN quantnr1 >=100 THEN 4
                        END
                        )
                    WHERE kuerzel = 'BAE' 
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 5
                                WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                            WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                            WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 4
                            WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 1
                            WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                        END
                        )
                    WHERE kuerzel = 'BAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                      AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                           Schadensklasse_B = (
                               CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                   WHEN quantnr1 < 15 THEN 1
                                   WHEN quantnr1 < 40 THEN 2
                                   WHEN quantnr1 < 60 THEN 3
                                   WHEN quantnr1 < 75 THEN 4
                                   WHEN quantnr1 >= 75 THEN 5
                               END
                           )
                       WHERE kuerzel = 'BAG' 
                         AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                             );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 in ('B', 'C','D') THEN 3
                            WHEN charakt1 = 'Z' THEN 2
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN 2
                        END
                        )
                    WHERE kuerzel = 'BAH' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 3
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN
                                    CASE WHEN charakt2 = 'A' THEN 1
                                        WHEN  charakt2 in ('B','C','D') THEN 2
                                        END
                            WHEN charakt1 = 'Z' THEN
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 5 THEN 1
                                    WHEN quantnr1 < 20 THEN 2
                                    WHEN quantnr1 < 35 THEN 3
                                    WHEN quantnr1 < 50 THEN 4
                                    WHEN quantnr1 >= 50 THEN 5
                                END
                        END
                        )
                    WHERE kuerzel = 'BAI' AND charakt1 in ('A', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN untersuchdat_haltung_bewertung.charakt1 = 'A' THEN
                                CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 400 THEN
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 30 THEN 2
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 <50 THEN 3
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 <70 THEN 4 
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >=70 THEN 5
                                        END
                                WHEN haltungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 40 THEN 2
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 <60 THEN 3
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 <80 THEN  4
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >=80 THEN 5
                                        END
                                WHEN haltungen_untersucht_bewertung.breite/1000 > 800 THEN
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 40 THEN 2
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 <65 THEN 3
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 <90 THEN 4
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >=90 THEN 5
                                        END
                                END
                            WHEN untersuchdat_haltung_bewertung.charakt1 = 'B' THEN
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 10 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 15 THEN 2
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN 3
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 30 THEN 4 
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >= 30 THEN 5
                                        END
                            WHEN untersuchdat_haltung_bewertung.charakt1 = 'C' THEN
                                CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 200 THEN
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 5 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 7 THEN 2
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 9 THEN 3
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 12 THEN 4 
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >= 12 THEN 5
                                        END
                                WHEN haltungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 2 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 2
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 4 THEN 3
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 6 THEN 4 
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >= 6 THEN 5
                                        END
                                WHEN haltungen_untersucht_bewertung.breite/1000 > 500 THEN
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 1 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN 2
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 4 THEN 3
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 6 THEN 4
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >= 6 THEN 5
                                        END
                                END
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN untersuchdat_haltung_bewertung.charakt1 = 'B' THEN 
                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 < 10 THEN 1
                                        WHEN untersuchdat_haltung_bewertung.quantnr1 >= 10 THEN 2
                                        END
                        END
                        ),
                        Schadensklasse_S = 1
                    FROM haltungen_untersucht_bewertung
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam
                        AND kuerzel = 'BAJ' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_haltung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_haltung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Schadensklasse_D = (
                            CASE WHEN charakt1 = 'B' THEN 1
                                WHEN charakt1 = 'C' THEN 3
                                WHEN charakt1 = 'I' THEN 3
                                WHEN charakt1 = 'J' THEN 4
                                WHEN charakt1 = 'K' THEN 3
                                WHEN charakt1 = 'L' THEN 2
                                WHEN charakt1 = 'M' THEN 3
                                WHEN charakt1 = 'N' THEN 3
                                WHEN charakt1 = 'Z' THEN 2
                            END
                            ),
                            Schadensklasse_B = (
                            CASE WHEN charakt1 = 'A' THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 5 THEN 1
                                            WHEN quantnr1 < 20 THEN 2
                                            WHEN quantnr1 < 35 THEN 3
                                            WHEN quantnr1 < 50 THEN 4
                                            WHEN quantnr1 >= 50 THEN 5
                                            END
                                WHEN charakt1 = 'C' THEN 3
                                WHEN charakt1 = 'D' THEN 2
                                WHEN charakt1 = 'E' THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 5 THEN 1
                                            WHEN quantnr1 < 20 THEN 2
                                            WHEN quantnr1 < 35 THEN 3
                                            WHEN quantnr1 < 50 THEN 4
                                            WHEN quantnr1 >= 50 THEN 5
                                            END
                                WHEN charakt1 = 'G' THEN 1
                                WHEN charakt1 = 'H' THEN 1
                                WHEN charakt1 = 'Z' THEN 2
                            END
                            ),
                            Schadensklasse_S = (
                            CASE WHEN charakt1 = 'D' AND charakt2 = 'C' THEN 3
                                WHEN charakt1 = 'E' THEN 2
                                WHEN charakt1 = 'F' THEN 2
                                WHEN charakt1 = 'L' THEN 2
                                WHEN charakt1 = 'Z' THEN 2
                            END
                            )
                        WHERE kuerzel = 'BAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 4
                            WHEN charakt1 = 'B' THEN 4
                            WHEN charakt1 = 'C' THEN 3
                            WHEN charakt1 = 'D' THEN 3
                            WHEN charakt1 = 'F' THEN 4
                            WHEN charakt1 = 'G' THEN 2
                            WHEN charakt1 = 'Z' THEN 2
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'E' THEN
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 5 THEN 1
                                        WHEN quantnr1 < 20 THEN 2
                                        WHEN quantnr1 < 35 THEN 3
                                        WHEN quantnr1 < 50 THEN 4
                                        WHEN quantnr1 >= 50 THEN 5
                                        END
                            WHEN charakt1 = 'Z' THEN 2
                        END
                        )
                    WHERE kuerzel = 'BAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F','G', 'Z')
                        AND charakt2 in ('A', 'B', 'C', 'D')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = 3,
                        Schadensklasse_S = (
                        CASE WHEN charakt1 in ('A', 'C') THEN 2
                            WHEN charakt1 = 'B' THEN 1
                        END
                        )
                    WHERE kuerzel = 'BAM' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Schadensklasse_D = 3,
                            Schadensklasse_S = 3
                        WHERE kuerzel = 'BAN' 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = 4,
                        Schadensklasse_S = 4
                    WHERE kuerzel = 'BAO' 
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Schadensklasse_D = 4, 
                            Schadensklasse_S = 5
                        WHERE kuerzel = 'BAP' 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = 3,
                        Schadensklasse_B = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                            WHEN quantnr1 < 10 THEN 2
                            WHEN quantnr1 < 20 THEN 3
                            WHEN quantnr1 < 30 THEN 4
                            WHEN quantnr1 >= 30 THEN 5
                        END
                        )
                    WHERE kuerzel = 'BBA' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_B = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                            WHEN quantnr1 < 10 THEN 2
                            WHEN quantnr1 < 20 THEN 3
                            WHEN quantnr1 < 30 THEN 4
                            WHEN quantnr1 >= 30 THEN 5
                        END
                        )
                    WHERE kuerzel = 'BBB' AND charakt1 in ('A', 'B', 'C', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_B = (
                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 10 THEN 1
                                WHEN quantnr1 < 25 THEN 2
                                WHEN quantnr1 < 40 THEN 3
                                WHEN quantnr1 < 50 THEN 4
                                WHEN quantnr1 >= 50 THEN 5
                            END
                        )
                    WHERE kuerzel = 'BBC' AND charakt1 in ('A', 'B', 'C', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = 4,
                        Schadensklasse_S = 5,
                        Schadensklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN 2
                                        WHEN quantnr1 < 20 THEN 3
                                        WHEN quantnr1 < 30 THEN 4
                                        WHEN quantnr1 >= 30 THEN 5
                            END
                        )
                    WHERE kuerzel = 'BBD' AND charakt1 in ('A', 'B', 'C', 'D', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                                    CASE WHEN charakt1 in ('D', 'G') THEN 3
                            END
                        ),
                        Schadensklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 5 THEN 1
                                        WHEN quantnr1 < 20 THEN 2
                                        WHEN quantnr1 < 35 THEN 3
                                        WHEN quantnr1 < 50 THEN 4
                                        WHEN quantnr1 >= 50 THEN 5
                            END
                        )
                    WHERE kuerzel = 'BBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_D = (
                            CASE WHEN charakt1 in ('A', 'B') THEN 3
                                WHEN charakt1 in ('C', 'D') THEN 4
                            END
                        ),
                        Schadensklasse_S = (
                            CASE WHEN charakt1 in ('A', 'B') THEN 2
                                WHEN charakt1 = 'C' THEN 3
                                WHEN charakt1 = 'D' THEN 4
                            END
                        ),
                        Schadensklasse_B = (
                            CASE WHEN charakt1 in ('A', 'B') THEN 1
                                WHEN charakt1 in ('C', 'D') THEN 2
                            END
                        )
                    WHERE kuerzel = 'BBF' AND charakt1 in ('A', 'B', 'C', 'D')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Schadensklasse_D = 4,
                            Schadensklasse_S = 2
                        WHERE kuerzel = 'BBG' 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Schadensklasse_D = 2,
                            Schadensklasse_B = 2
                        WHERE kuerzel = 'BDB' AND charakt1 in ('AA', 'AB', 'AC', 'AD', 'AE')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                            Schadensklasse_D = 2
                        WHERE kuerzel = 'BDB' AND charakt1 in ('BA', 'BB', 'BC')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_B = 2
                    WHERE kuerzel = 'BDD' AND charakt1 in ('A', 'B', 'C', 'D', 'E')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                        Schadensklasse_B = (
                                CASE WHEN charakt2 = 'A' THEN 4
                                    WHEN charakt2 = 'B' THEN 3
                                END
                            )
                    WHERE kuerzel = 'BDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                            Schadensklasse_B = '-',
                                            Schadensklasse_S = '-',
                                            Schadensklasse_D = '-'
                                        WHERE kuerzel in ('BCD', 'BCE', 'BDC', 'BCA', 'BCB', 'BCC', 'BDA', 'BDF', 'BDG', 'BDB', 'AEC', 'AED')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Schadensklasse_B = 'Bitte pruefen!',
                                Schadensklasse_S = 'Bitte pruefen!',
                                Schadensklasse_D = 'Bitte pruefen!'
                            WHERE kuerzel not NULL AND Schadensklasse_B is NULL AND Schadensklasse_S is NULL AND Schadensklasse_D is NULL
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                           Schadensklasse_B = '-'
                           WHERE kuerzel not NULL AND Schadensklasse_B is NULL 
                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                 );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                   Schadensklasse_S = '-'
                                   WHERE kuerzel not NULL AND Schadensklasse_S is NULL 
                                     AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                           OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                         );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                           Schadensklasse_D = '-'
                           WHERE kuerzel not NULL AND Schadensklasse_D is NULL 
                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                 );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        try:
            db.sql(
                """ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """UPDATE untersuchdat_haltung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_haltung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_haltung_bewertung
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

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value,
            table='untersuchdat_haltung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_haltung_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )


        sql = """SELECT CreateSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Lage_am_Umfang TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
            #db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HALTUNGEN.value,
            table='haltungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'haltungen_untersucht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

    def bewertung_isy_leitung(self):
        date = self.date
        db = self.db
        leitung = self.leitung
        haltung = self.haltung
        crs = self.crs


        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_anschlussleitung_bewertung AS SELECT * FROM untersuchdat_anschlussleitung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """CREATE TABLE IF NOT EXISTS anschlussleitungen_untersucht_bewertung AS SELECT * FROM anschlussleitungen_untersucht"""
        db.sql(sql)

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
        except:
            pass

        if haltung is True:
            sql = """
                SELECT
                    haltungen.haltnam,
                    haltungen.material,
                    haltungen.hoehe,
                    untersuchdat_haltung_bewertung.untersuchhal
                FROM haltungen
                INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
            """

        if leitung is True:
            sql = """
                SELECT
                    anschlussleitungen.leitnam,
                    anschlussleitungen.material,
                    anschlussleitungen.hoehe,
                    untersuchdat_anschlussleitung_bewertung.untersuchleit
                FROM anschlussleitungen
                INNER JOIN untersuchdat_anschlussleitung_bewertung  ON anschlussleitungen.leitnam = untersuchdat_anschlussleitung_bewertung.untersuchleit
            """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():
            untersuchhalt = attr1[0]


            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC", "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk", "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton", "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE untersuchdat_anschlussleitung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK", "GFK Glasfaserverstärkter Kunststoff",
                            "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST", "KST Nichtidentifizier Kunststoff",
                            "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP", "PP Polypropylen",
                            "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                            "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                            "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                            "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE untersuchdat_anschlussleitung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()


        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_anschlussleitung_bewertung set Schadensklasse_D = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_anschlussleitung_bewertung set Schadensklasse_S = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_anschlussleitung_bewertung set Schadensklasse_B = NULL ;""")
        except:
            pass

        db.commit()

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                    Schadensklasse_S = (CASE
                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 6 THEN 3
                                WHEN quantnr1 < 15 THEN 4
                                WHEN quantnr1 >= 15 THEN 5
                            END)
                WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegesteif'
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Schadensklasse_S = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 2 THEN 1
                                        WHEN quantnr1 < 6 THEN 2
                                        WHEN quantnr1 < 10 THEN 3
                                        WHEN quantnr1 < 15 THEN 4
                                        WHEN quantnr1 >= 15 THEN 5
                                    END)
                        WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegeweich'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_B = (CASE
                                    WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 10 THEN 1
                                    WHEN quantnr1 < 25 THEN 2
                                    WHEN quantnr1 < 40 THEN 3
                                    WHEN quantnr1 < 50 THEN 4
                                    WHEN quantnr1 >= 50 THEN 5
                                END)
                    WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs IN ('biegesteif','biegeweich')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Schadensklasse_S = 1,
                                    Schadensklasse_D = 1
                                WHERE kuerzel = 'BAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                                CASE
                                    WHEN charakt1 = 'B' THEN 3
                                    WHEN charakt1 = 'C' THEN 1
                                END),
                        Schadensklasse_S = (
                                CASE WHEN charakt2 = 'B' THEN 1
                                    WHEN charakt2 in ('A', 'C', 'D', 'E') THEN 
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 2 AND quantnr1 > 0.5 THEN 2
                                            WHEN quantnr1 < 5 THEN 3
                                            WHEN quantnr1 < 10 THEN 4
                                            WHEN quantnr1 >= 10 THEN 5
                                    END
                                END
                                )
                    WHERE kuerzel = 'BAB' AND charakt1 in ('B', 'C') AND charakt2 in ('A','B','C','D','E')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 4
                                WHEN charakt1 = 'B' THEN 4
                                WHEN charakt1 = 'C' THEN 5
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN charakt1 = 'A' THEN 3
                            WHEN charakt1 = 'B' THEN 3
                            WHEN charakt1 = 'C' THEN 5
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN 3
                            WHEN charakt1 = 'C' THEN 5
                        END
                        )
                    WHERE kuerzel = 'BAC' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 3
                                WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 3
                                WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 3
                                WHEN charakt1 = 'C' THEN 5
                                WHEN charakt1 = 'D' THEN 5
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN charakt1 = 'A' THEN 3
                            WHEN charakt1 = 'B' AND charakt2 = 'A' THEN 3
                            WHEN charakt1 = 'B' AND charakt2 = 'B' THEN 3
                            WHEN charakt1 = 'C' THEN 5
                            WHEN charakt1 = 'D' THEN 5
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN 2
                            WHEN charakt1 = 'C' THEN 5
                            WHEN charakt1 = 'D' THEN 5
                        END
                        )
                    WHERE kuerzel = 'BAD' AND charakt1 in ('A', 'B', 'C', 'D')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 <100 THEN 1
                                ELSE 3
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                            WHEN quantnr1 <20 THEN 1
                            WHEN quantnr1 <50 THEN 2
                            WHEN quantnr1 <100 THEN 3
                            WHEN quantnr1 >=100 THEN 4
                        END
                        )
                    WHERE kuerzel = 'BAE' 
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 5
                                WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                        END
                        ),
                        Schadensklasse_S = (
                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                            WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 3
                            WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 4
                            WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 4
                            WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN 1
                            WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                            WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 2
                            WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN 1
                        END
                        )
                    WHERE kuerzel = 'BAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                      AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                           Schadensklasse_B = (
                               CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                   WHEN quantnr1 < 15 THEN 1
                                   WHEN quantnr1 < 40 THEN 2
                                   WHEN quantnr1 < 60 THEN 3
                                   WHEN quantnr1 < 75 THEN 4
                                   WHEN quantnr1 >= 75 THEN 5
                               END
                           )
                       WHERE kuerzel = 'BAG' 
                         AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                             );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 in ('B', 'C','D') THEN 3
                            WHEN charakt1 = 'Z' THEN 2
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN 2
                        END
                        )
                    WHERE kuerzel = 'BAH' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 3
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'A' THEN
                                    CASE WHEN charakt2 = 'A' THEN 1
                                        WHEN  charakt2 in ('B','C','D') THEN 2
                                        END
                            WHEN charakt1 = 'Z' THEN
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 5 THEN 1
                                    WHEN quantnr1 < 20 THEN 2
                                    WHEN quantnr1 < 35 THEN 3
                                    WHEN quantnr1 < 50 THEN 4
                                    WHEN quantnr1 >= 50 THEN 5
                                END
                        END
                        )
                    WHERE kuerzel = 'BAI' AND charakt1 in ('A', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'A' THEN
                                CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 400 THEN
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 30 THEN 2
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <50 THEN 3
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <70 THEN 4 
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=70 THEN 5
                                        END
                                WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 40 THEN 2
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <60 THEN 3
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <80 THEN  4
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=80 THEN 5
                                        END
                                WHEN anschlussleitungen_untersucht_bewertung.breite/1000 > 800 THEN
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 40 THEN 2
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <65 THEN 3
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <90 THEN 4
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=90 THEN 5
                                        END
                                END
                            WHEN charakt1 = 'B' THEN
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 10 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 15 THEN 2
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN 3
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 30 THEN 4 
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 30 THEN 5
                                        END
                            WHEN charakt1 = 'C' THEN
                                CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 200 THEN
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 5 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 7 THEN 2
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 9 THEN 3
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 12 THEN 4 
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 12 THEN 5
                                        END
                                WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 2 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 2
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 4 THEN 3
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 6 THEN 4 
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 6 THEN 5
                                        END
                                WHEN anschlussleitungen_untersucht_bewertung.breite/1000 > 500 THEN
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 1 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN 2
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 4 THEN 3
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 6 THEN 4
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 6 THEN 5
                                        END
                                END
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'B' THEN 
                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 10 THEN 1
                                        WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 10 THEN 2
                                        END
                        END
                        ),
                        Schadensklasse_S = 1
                    FROM anschlussleitungen_untersucht_bewertung
                            WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam
                            AND kuerzel = 'BAJ' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Schadensklasse_D = (
                            CASE WHEN charakt1 = 'B' THEN 1
                                WHEN charakt1 = 'C' THEN 3
                                WHEN charakt1 = 'I' THEN 3
                                WHEN charakt1 = 'J' THEN 4
                                WHEN charakt1 = 'K' THEN 3
                                WHEN charakt1 = 'L' THEN 2
                                WHEN charakt1 = 'M' THEN 3
                                WHEN charakt1 = 'N' THEN 3
                                WHEN charakt1 = 'Z' THEN 2
                            END
                            ),
                            Schadensklasse_B = (
                            CASE WHEN charakt1 = 'A' THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 5 THEN 1
                                            WHEN quantnr1 < 20 THEN 2
                                            WHEN quantnr1 < 35 THEN 3
                                            WHEN quantnr1 < 50 THEN 4
                                            WHEN quantnr1 >= 50 THEN 5
                                            END
                                WHEN charakt1 = 'C' THEN 3
                                WHEN charakt1 = 'D' THEN 2
                                WHEN charakt1 = 'E' THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 5 THEN 1
                                            WHEN quantnr1 < 20 THEN 2
                                            WHEN quantnr1 < 35 THEN 3
                                            WHEN quantnr1 < 50 THEN 4
                                            WHEN quantnr1 >= 50 THEN 5
                                            END
                                WHEN charakt1 = 'G' THEN 1
                                WHEN charakt1 = 'H' THEN 1
                                WHEN charakt1 = 'Z' THEN 2
                            END
                            ),
                            Schadensklasse_S = (
                            CASE WHEN charakt1 = 'D' AND charakt2 = 'C' THEN 3
                                WHEN charakt1 = 'E' THEN 2
                                WHEN charakt1 = 'F' THEN 2
                                WHEN charakt1 = 'L' THEN 2
                                WHEN charakt1 = 'Z' THEN 2
                            END
                            )
                        WHERE kuerzel = 'BAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                        CASE WHEN charakt1 = 'A' THEN 4
                            WHEN charakt1 = 'B' THEN 4
                            WHEN charakt1 = 'C' THEN 3
                            WHEN charakt1 = 'D' THEN 3
                            WHEN charakt1 = 'F' THEN 4
                            WHEN charakt1 = 'G' THEN 2
                            WHEN charakt1 = 'Z' THEN 2
                        END
                        ),
                        Schadensklasse_B = (
                        CASE WHEN charakt1 = 'E' THEN
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 5 THEN 1
                                        WHEN quantnr1 < 20 THEN 2
                                        WHEN quantnr1 < 35 THEN 3
                                        WHEN quantnr1 < 50 THEN 4
                                        WHEN quantnr1 >= 50 THEN 5
                                        END
                            WHEN charakt1 = 'Z' THEN 2
                        END
                        )
                    WHERE kuerzel = 'BAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F','G', 'Z')
                        AND charakt2 in ('A', 'B', 'C', 'D')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = 3,
                        Schadensklasse_S = (
                        CASE WHEN charakt1 in ('A', 'C') THEN 2
                            WHEN charakt1 = 'B' THEN 1
                        END
                        )
                    WHERE kuerzel = 'BAM' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Schadensklasse_D = 3,
                            Schadensklasse_S = 3
                        WHERE kuerzel = 'BAN' 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = 4,
                        Schadensklasse_S = 4
                    WHERE kuerzel = 'BAO' 
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Schadensklasse_D = 4, 
                            Schadensklasse_S = 5
                        WHERE kuerzel = 'BAP' 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = 3,
                        Schadensklasse_B = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                            WHEN quantnr1 < 10 THEN 2
                            WHEN quantnr1 < 20 THEN 3
                            WHEN quantnr1 < 30 THEN 4
                            WHEN quantnr1 >= 30 THEN 5
                        END
                        )
                    WHERE kuerzel = 'BBA' AND charakt1 in ('A', 'B', 'C')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_B = (
                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                            WHEN quantnr1 < 10 THEN 2
                            WHEN quantnr1 < 20 THEN 3
                            WHEN quantnr1 < 30 THEN 4
                            WHEN quantnr1 >= 30 THEN 5
                        END
                        )
                    WHERE kuerzel = 'BBB' AND charakt1 in ('A', 'B', 'C', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_B = (
                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 10 THEN 1
                                WHEN quantnr1 < 25 THEN 2
                                WHEN quantnr1 < 40 THEN 3
                                WHEN quantnr1 < 50 THEN 4
                                WHEN quantnr1 >= 50 THEN 5
                            END
                        )
                    WHERE kuerzel = 'BBC' AND charakt1 in ('A', 'B', 'C', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = 4,
                        Schadensklasse_S = 5,
                        Schadensklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN 2
                                        WHEN quantnr1 < 20 THEN 3
                                        WHEN quantnr1 < 30 THEN 4
                                        WHEN quantnr1 >= 30 THEN 5
                            END
                        )
                    WHERE kuerzel = 'BBD' AND charakt1 in ('A', 'B', 'C', 'D', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                                    CASE WHEN charakt1 in ('D', 'G') THEN 3
                            END
                        ),
                        Schadensklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 5 THEN 1
                                        WHEN quantnr1 < 20 THEN 2
                                        WHEN quantnr1 < 35 THEN 3
                                        WHEN quantnr1 < 50 THEN 4
                                        WHEN quantnr1 >= 50 THEN 5
                            END
                        )
                    WHERE kuerzel = 'BBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_D = (
                            CASE WHEN charakt1 in ('A', 'B') THEN 3
                                WHEN charakt1 in ('C', 'D') THEN 4
                            END
                        ),
                        Schadensklasse_S = (
                            CASE WHEN charakt1 in ('A', 'B') THEN 2
                                WHEN charakt1 = 'C' THEN 3
                                WHEN charakt1 = 'D' THEN 4
                            END
                        ),
                        Schadensklasse_B = (
                            CASE WHEN charakt1 in ('A', 'B') THEN 1
                                WHEN charakt1 in ('C', 'D') THEN 2
                            END
                        )
                    WHERE kuerzel = 'BBF' AND charakt1 in ('A', 'B', 'C', 'D')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Schadensklasse_D = 4,
                            Schadensklasse_S = 2
                        WHERE kuerzel = 'BBG' 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Schadensklasse_D = 2,
                            Schadensklasse_B = 2
                        WHERE kuerzel = 'BDB' AND charakt1 in ('AA', 'AB', 'AC', 'AD', 'AE')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Schadensklasse_D = 2
                        WHERE kuerzel = 'BDB' AND charakt1 in ('BA', 'BB', 'BC')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_B = 2
                    WHERE kuerzel = 'BDD' AND charakt1 in ('A', 'B', 'C', 'D', 'E')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                        Schadensklasse_B = (
                                CASE WHEN charakt2 = 'A' THEN 4
                                    WHEN charakt2 = 'B' THEN 3
                                END
                            )
                    WHERE kuerzel = 'BDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Schadensklasse_B = '-',
                                            Schadensklasse_S = '-',
                                            Schadensklasse_D = '-'
                                        WHERE kuerzel in ('BCD', 'BCE', 'BDC', 'BCA', 'BCB', 'BCC', 'BDA', 'BDF', 'BDG', 'BDB', 'AEC', 'AED')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Schadensklasse_B = 'Bitte pruefen!',
                                Schadensklasse_S = 'Bitte pruefen!',
                                Schadensklasse_D = 'Bitte pruefen!'
                            WHERE kuerzel not NULL AND Schadensklasse_B is NULL AND Schadensklasse_S is NULL AND Schadensklasse_D is NULL
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                           Schadensklasse_B = '-'
                           WHERE kuerzel not NULL AND Schadensklasse_B is NULL 
                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                 );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                   Schadensklasse_S = '-'
                                   WHERE kuerzel not NULL AND Schadensklasse_S is NULL 
                                     AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                           OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                         );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                           Schadensklasse_D = '-'
                           WHERE kuerzel not NULL AND Schadensklasse_D is NULL 
                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                 );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """UPDATE untersuchdat_anschlussleitung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_anschlussleitung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_anschlussleitung_bewertung
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

        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HA_LEITUNGEN.value,
            table='untersuchdat_anschlussleitung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_anschlussleitung_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )


        sql = """SELECT CreateSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Lage_am_Umfang TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
            #db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('anschlussleitungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HA_LEITUNGEN.value,
            table='anschlussleitungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'anschlussleitungen_untersucht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

    def bewertung_isy_schacht(self):
        date = self.date
        db = self.db
        crs = self.crs


        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_schacht_bewertung AS SELECT * FROM untersuchdat_schacht"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """CREATE TABLE IF NOT EXISTS schaechte_untersucht_bewertung AS SELECT * FROM schaechte_untersucht"""
        db.sql(sql)

        sql = """
                    SELECT
                        schaechte.schnam,
                        schaechte.material,
                        untersuchdat_schacht_bewertung.untersuchsch
                    FROM schaechte
                        INNER JOIN untersuchdat_schacht_bewertung  ON schaechte.schnam = untersuchdat_schacht_bewertung.untersuchsch
                """
        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Schächte konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchhalt = attr1[0]
            try:
                db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC", "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk", "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton", "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK", "GFK Glasfaserverstärkter Kunststoff",
                            "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST", "KST Nichtidentifizier Kunststoff",
                            "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP", "PP Polypropylen",
                            "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                            "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                            "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                            "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE untersuchdat_schacht_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()

        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_schacht_bewertung set Schadensklasse_D = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_schacht_bewertung set Schadensklasse_S = NULL ;""")
        except:
            pass

        try:
            db.sql("""update untersuchdat_schacht_bewertung set Schadensklasse_B = NULL ;""")
        except:
            pass

        db.commit()

        sql = f"""update untersuchdat_schacht_bewertung set
                    Schadensklasse_S = 2,
                    Schadensklasse_B = (CASE
                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 10 THEN 1
                                WHEN quantnr1 < 20 THEN 2
                                WHEN quantnr1 < 30 THEN 3
                                WHEN quantnr1 < 40 THEN 4
                                WHEN quantnr1 >= 40 THEN 5
                            END)
                WHERE kuerzel = 'DAA' AND charakt1 in ('A','B') AND bereich in ('B', 'C', 'D', 'F') AND bw_bs = 'biegeweich'
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                    Schadensklasse_S = 3,
                    Schadensklasse_B = (CASE
                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                WHEN quantnr1 < 10 THEN 1
                                WHEN quantnr1 < 20 THEN 2
                                WHEN quantnr1 < 30 THEN 3
                                WHEN quantnr1 < 40 THEN 4
                                WHEN quantnr1 >= 40 THEN 5
                            END)
                WHERE kuerzel = 'DAA' AND charakt1 in ('A','B') AND bereich in ('B', 'C', 'D', 'F') AND bw_bs = 'biegesteif'
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Schadensklasse_S = 1
                        WHERE kuerzel = 'DAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E') AND bereich in ('B', 'C', 'D', 'F', 'H', 'I', 'J') 
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                       Schadensklasse_D = (
                               CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 1
                                    WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                    WHEN charakt1 = 'B' AND bereich in ('I', 'J') THEN 3
                                    WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                    WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 4
                               END),
                       Schadensklasse_S = (
                               CASE WHEN charakt1 in ('B', 'C') AND charakt2 = 'A' AND bereich in ('B', 'C', 'D', 'F') THEN
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                       WHEN quantnr1 < 1 THEN 1
                                       WHEN quantnr1 < 3 THEN 2
                                       WHEN quantnr1 < 5 THEN 3
                                       WHEN quantnr1 < 8 THEN 4
                                       WHEN quantnr1 >= 8 THEN 5
                                       END
                                   WHEN charakt1 in ('B', 'C') AND charakt2 = 'B' AND bereich in ('B', 'C', 'D', 'F') THEN 1
                                   WHEN charakt1 in ('B', 'C') AND charakt2 in ('C', 'D', 'E') AND bereich in ('B', 'C', 'D', 'F') THEN 2
                                   END
                               )
                   WHERE kuerzel = 'DAB' AND charakt1 in ('A', 'B', 'C') AND charakt2 in ('A','B','C','D','E') AND bereich in ('B', 'C', 'D', 'F', 'I', 'J')
                     AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                           OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                         );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Schadensklasse_D = (
                                    CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                        WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 4
                                        WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                        WHEN charakt1 = 'B' AND bereich in ('I', 'J') THEN 4
                                        WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 4
                                        WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 5
                                    END),
                            Schadensklasse_S = (
                                    CASE WHEN charakt1 in ('A', 'B') AND bereich in ('B', 'C', 'D', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'F', 'H') THEN 5
                                        END
                                    ),
                            Schadensklasse_B = (
                                    CASE WHEN charakt1 = 'A'  AND bereich in ('B', 'C', 'D', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'F', 'H') THEN 5
                                        END
                                    )
                        WHERE kuerzel = 'DAC' AND charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'F','H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Schadensklasse_D = (
                                    CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 3
                                        WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('I', 'J') THEN 3
                                        WHEN charakt1 = 'B' AND charakt2 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                        WHEN charakt1 = 'B' AND charakt2 = 'B' AND bereich in ('I', 'J') THEN 4
                                        WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 4
                                        WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 5
                                    END),
                            Schadensklasse_S = (
                                    CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'F') THEN 2
                                        WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('C', 'D', 'F') THEN 3
                                        WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'F') THEN 5
                                        END
                                    ),
                            Schadensklasse_B = (
                                    CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'F') THEN 2
                                        WHEN charakt1 = 'A' AND bereich in ('H','I','J') THEN 3
                                         WHEN charakt1 = 'B' AND charakt2 in ('A', 'B') AND bereich in ('H','I','J') THEN 3
                                        WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'F', 'H', 'I', 'J') THEN 5
                                        END
                                    )
                        WHERE kuerzel = 'DAD' AND charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 100 THEN 1
                                            WHEN quantnr1 >= 100 THEN 2
                                        END
                                    WHEN bereich in ('I', 'J') THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 100 THEN 1
                                            WHEN quantnr1 >= 100 THEN 3
                                        END
                                END),
                        Schadensklasse_S = (
                                CASE WHEN bereich in ('C', 'D', 'F') THEN 
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN 1
                                        WHEN quantnr1 < 100 THEN 2
                                        WHEN quantnr1 >= 100 THEN 3
                                   END
                                END
                                )
                    WHERE kuerzel = 'DAE' AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                    Schadensklasse_D = (
                            CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN
                                   4
                                WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN
                                   5
                                WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN
                                     2
                            END),
                    Schadensklasse_S = (
                            CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 1
                                WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 4
                                WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 4
                                WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                WHEN charakt1 = 'J' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in (A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 1
                                WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F', 'H') THEN 2       
                            END
                            ),
                    Schadensklasse_B = (
                            CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in ('I', 'J') THEN 1
                                WHEN charakt1 = 'J' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in (A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 1
                                WHEN charakt1 = 'K' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN 2
                                END
                            )
                WHERE kuerzel = 'DAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                    Schadensklasse_B = (
                            CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 100 THEN 1 
                                    WHEN quantnr1 < 200 THEN 2
                                    WHEN quantnr1 < 300 THEN 3
                                    WHEN quantnr1 < 400 THEN 4
                                    WHEN quantnr1 >= 400 THEN 5
                                    END

                                WHEN bereich in ('I','J') THEN 2
                                END
                            )
                WHERE kuerzel = 'DAG' AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN charakt1 in ('B', 'C', 'D') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                    WHEN charakt1 in ('B', 'C', 'D') AND bereich in ('I', 'J') THEN 3
                                    WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 2
                                    END
                                )
                    WHERE kuerzel = 'DAH' AND charakt1 in ('B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F') THEN 2
                                    WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C') AND bereich in ('I','J') THEN 3
                                    END
                                ),
                        Schadensklasse_B = (
                                CASE WHEN charakt1 = 'Z'  AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 1
                                    END
                                )
                    WHERE kuerzel = 'DAI' AND charakt1 in ('A', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F') THEN 2
                                     END
                                ),
                        Schadensklasse_S = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'F') THEN 1
                                     END
                                )
                    WHERE kuerzel = 'DAJ' AND charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'E', 'F')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Schadensklasse_D = (
                                    CASE WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 1
                                        WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 3
                                        WHEN charakt1 = 'I' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'I' AND bereich in ('I', 'J') THEN 3
                                        WHEN charakt1 = 'J' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                        WHEN charakt1 = 'J' AND bereich in ('I','J') THEN 2
                                        WHEN charakt1 = 'K' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'K' AND bereich in ('I','J') THEN 3
                                        WHEN charakt1 = 'L' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 1
                                        WHEN charakt1 = 'L' AND bereich in ('I', 'J') THEN 2
                                        WHEN charakt1 = 'M' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 = 'M' AND bereich in ('I', 'J') THEN 3
                                        WHEN charakt1 = 'N' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 2
                                        WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 2
                                         END
                                    ),
                            Schadensklasse_S = (
                                    CASE WHEN charakt1 = 'D' AND charakt2 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 2
                                         WHEN charakt1 in ('E', 'F', 'L', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 2
                                         END
                                    ),
                            Schadensklasse_B = (
                                    CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 10 THEN 1
                                                WHEN quantnr1 < 20 THEN 2
                                                WHEN quantnr1 < 30 THEN 3
                                                WHEN quantnr1 < 40 THEN 4
                                                WHEN quantnr1 >= 40 THEN 5
                                            END
                                        WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN 1
                                                WHEN quantnr1 < 20 THEN 2
                                                WHEN quantnr1 < 35 THEN 3
                                                WHEN quantnr1 < 50 THEN 4
                                                WHEN quantnr1 >= 50 THEN 5
                                            END
                                        WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 3
                                        WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D') AND bereich in ('I', 'J') THEN 2
                                        WHEN charakt1 = 'E' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 10 THEN 1
                                                WHEN quantnr1 < 20 THEN 2
                                                WHEN quantnr1 < 30 THEN 3
                                                WHEN quantnr1 < 40 THEN 4
                                                WHEN quantnr1 >= 40 THEN 5
                                            END
                                        WHEN charakt1 = 'E' AND bereich in ('I', 'J') THEN 
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN 1
                                                WHEN quantnr1 < 20 THEN 2
                                                WHEN quantnr1 < 35 THEN 3
                                                WHEN quantnr1 < 50 THEN 4
                                                WHEN quantnr1 >= 50 THEN 5
                                            END
                                        WHEN charakt1 = 'G' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 1
                                        WHEN charakt1 = 'H' AND bereich in ('I', 'J') THEN 1
                                        WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 2
                                        END
                                    )
                        WHERE kuerzel = 'DAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z') 
                        AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Schadensklasse_D = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                                WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 4
                                                WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN 2
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                                WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN 3
                                                WHEN charakt1 = 'D' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 1
                                                WHEN charakt1 = 'D' AND bereich in ('I', 'J') THEN 3
                                                WHEN charakt1 = 'F' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                                WHEN charakt1 = 'F' AND bereich in ('I', 'J') THEN 4
                                                WHEN charakt1 = 'G' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 1
                                                WHEN charakt1 = 'G' AND bereich in ('I', 'J') THEN 2
                                                WHEN charakt1 = 'Z' AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 2
                                                END
                                            ),
                                    Schadensklasse_B = (
                                            CASE WHEN charakt1 = 'E' AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') THEN 
                                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                        WHEN quantnr1 < 10 THEN 1
                                                        WHEN quantnr1 < 20 THEN 2
                                                        WHEN quantnr1 < 30 THEN 3
                                                        WHEN quantnr1 < 40 THEN 4
                                                        WHEN quantnr1 >= 40 THEN 5
                                                    END
                                                WHEN charakt1 = 'E' AND bereich in ('I', 'J') THEN 
                                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                        WHEN quantnr1 < 5 THEN 1
                                                        WHEN quantnr1 < 20 THEN 2
                                                        WHEN quantnr1 < 35 THEN 3
                                                        WHEN quantnr1 < 50 THEN 4
                                                        WHEN quantnr1 >= 50 THEN 5
                                                    END
                                                WHEN charakt1 = 'Z' AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 2
                                                END
                                            )
                                WHERE kuerzel = 'DAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'Z') 
                                AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                    WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN 3
                                    END
                                ),
                        Schadensklasse_S = (
                                CASE WHEN charakt1 in ('A', 'C') AND bereich in ('B', 'C', 'D', 'F') THEN 2
                                    WHEN charakt1 = 'B' AND bereich in ('B', 'C', 'D', 'F') THEN 1
                                    END
                                )
                    WHERE kuerzel = 'DAM' AND charakt1 in ('A', 'B', 'C') 
                    AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                    WHEN bereich in ('I', 'J') THEN 3
                                    END
                                ),
                        Schadensklasse_S = (
                                CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                   END
                                )
                    WHERE kuerzel = 'DAN' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                    WHEN bereich in ('I', 'J') THEN 4
                                    END
                                ),
                        Schadensklasse_S = (
                                CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 4
                                   END
                                )
                    WHERE kuerzel = 'DAO' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                    WHEN bereich in ('I', 'J') THEN 4
                                    END
                                ),
                        Schadensklasse_S = (
                                CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 5
                                   END
                                )
                    WHERE kuerzel = 'DAP' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_B = (
                                CASE WHEN charakt1 in ('A', 'C', 'D', 'F', 'G', 'H', 'I', 'J', 'K') AND bereich in ('C', 'D', 'F') THEN 4
                                    WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'F') THEN 5
                                    WHEN charakt1 = 'E' AND bereich in ('C', 'D', 'F') THEN 2
                                    WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'F') THEN 2
                                    END
                                )
                        
                    WHERE kuerzel = 'DAQ' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z') 
                    AND bereich in ('C', 'D', 'F')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_B = (
                                CASE WHEN charakt1 in ('A', 'C', 'F') THEN 5
                                    WHEN charakt1 in ('B', 'E') THEN 2
                                    WHEN charakt1 = 'D' THEN 4
                                    WHEN charakt1 in ('G', 'H') THEN 3
                                    WHEN charakt1 = 'Z' THEN 2
                                    END
                                )

                    WHERE kuerzel = 'DAR' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z') 
                    AND bereich = 'A'
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                    WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN 3
                                    END
                                ),
                        Schadensklasse_B = (
                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 2
                                    END
                                )
                    WHERE kuerzel = 'DBA' AND charakt1 in ('A', 'B', 'C') 
                    AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Schadensklasse_B = 2
                        WHERE kuerzel = 'DBB' AND charakt1 in ('A', 'B', 'C', 'Z') 
                        AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_B = (
                                CASE WHEN bereich = 'H' THEN 2
                                    WHEN bereich = 'J' THEN 
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 50 THEN 1
                                            WHEN quantnr1 < 100 THEN 2
                                            WHEN quantnr1 < 300 THEN 3
                                            WHEN quantnr1 >= 300 THEN 4
                                        END
                                    END
                                )
                    WHERE kuerzel = 'DBC' AND charakt1 in ('C', 'Z') 
                    AND bereich in ('H', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = (
                                CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                    WHEN bereich in ('I', 'J') THEN 4
                                    END
                                ),
                        Schadensklasse_B = (
                                CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                   END
                                ),
                        Schadensklasse_S = (
                                CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN 5
                                   END
                                )
                    WHERE kuerzel = 'DBD' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Schadensklasse_D = (
                                        CASE WHEN charakt1 in ('D', 'G') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                            WHEN charakt1 in ('D', 'G') AND bereich in ('I', 'J') THEN 3
                                            END
                                        ),
                                Schadensklasse_B = (
                                        CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN 2
                                            WHEN charakt1 in ('D', 'E', 'F', 'G', 'H', 'Z') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 3
                                           END
                                        )
                                
                            WHERE kuerzel = 'DBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z') 
                            AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Schadensklasse_D = (
                                    CASE WHEN charakt1 in ('A', 'B') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 2
                                        WHEN charakt1 in ('A', 'B') AND bereich in ('I', 'J') THEN 3
                                        WHEN charakt1 in ('C', 'D') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 3
                                        WHEN charakt1 in ('C', 'D') AND bereich in ('I', 'J') THEN 4
                                        END
                                    ),
                            Schadensklasse_S = (
                                    CASE WHEN charakt1 in ('A', 'B') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 2
                                        WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 3
                                        WHEN charakt1 = 'D' AND bereich in ('B', 'C', 'D', 'E', 'F') THEN 4
                                        END
                                    ),
                            Schadensklasse_B = (
                                    CASE WHEN charakt1 in ('A', 'B') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 1
                                        WHEN charakt1 in ('C', 'D') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN 2
                                        END
                                    )

                        WHERE kuerzel = 'DBF' AND charakt1 in ('A', 'B', 'C', 'D') AND charakt2 in ('A', 'B', 'C') 
                        AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_D = 4,
                        Schadensklasse_S = 2
                    WHERE kuerzel = 'DBG' AND bereich in ('I', 'J')
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Schadensklasse_B = 2
                            WHERE kuerzel = 'DCH' AND charakt1 = 'A' AND bereich = 'H'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_B = 2
                    WHERE kuerzel = 'DCI' AND charakt1 in ('A', 'C') AND bereich = 'I'
                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Schadensklasse_B = (
                                    CASE WHEN charakt1 in ('B', 'F')  THEN 5
                                        WHEN charakt1 in ('C', 'D', 'G', 'H')  THEN 2
                                        END
                                    )
                            WHERE kuerzel = 'DCJ' AND charakt1 in ('B', 'C', 'D', 'F', 'G', 'H') AND bereich = 'F'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                               Schadensklasse_B = 2
                           WHERE kuerzel = 'DCL' AND charakt1 in ('A', 'B', 'C') AND charakt2 = 'A' AND bereich = 'F'
                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                 );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                           Schadensklasse_B = 2
                       WHERE kuerzel = 'DCM' AND charakt1 in ('B', 'C') AND bereich = 'A'
                         AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                             );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                   Schadensklasse_B = 2
                               WHERE kuerzel = 'DCN' AND charakt1 = 'B' AND bereich = 'J'
                                 AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                       OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                     );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                        Schadensklasse_B = (
                                CASE WHEN charakt2 = 'A' THEN 4
                                    WHEN charakt2 = 'B' THEN 3
                                    END
                                )
                        WHERE kuerzel = 'DDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B') 
                        AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                    Schadensklasse_B = '-',
                    Schadensklasse_S = '-',
                    Schadensklasse_D = '-'
                    WHERE kuerzel in ('CED', 'DCA', 'DCB', 'DCG', 'DCK', 'DCO', 'DDA', 'DDB', 'DDC', 'DDD', 'DDF', 'DDG') 
                    AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                        Schadensklasse_B = 'Bitte pruefen!',
                                        Schadensklasse_S = 'Bitte pruefen!',
                                        Schadensklasse_D = 'Bitte pruefen!'
                                    WHERE kuerzel not NULL AND Schadensklasse_B is NULL AND Schadensklasse_S is NULL AND Schadensklasse_D is NULL
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                   Schadensklasse_B = '-'
                                   WHERE kuerzel not NULL AND Schadensklasse_B is NULL 
                                     AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                           OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                         );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                           Schadensklasse_S = '-'
                           WHERE kuerzel not NULL AND Schadensklasse_S is NULL 
                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                 );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                   Schadensklasse_D = '-'
                                   WHERE kuerzel not NULL AND Schadensklasse_D is NULL 
                                     AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                           OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                         );"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        try:
            db.sql(
                """ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """UPDATE untersuchdat_schacht_bewertung
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
            db.sql(
                """UPDATE untersuchdat_schacht_bewertung
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
            db.sql(
                """UPDATE untersuchdat_schacht_bewertung
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

        sql = """SELECT RecoverGeometryColumn('untersuchdat_schacht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_SCHAECHTE.value,
            table='untersuchdat_schacht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_schacht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )


        sql = """SELECT CreateSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
            #db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
            #db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_SCHAECHTE.value,
            table='schaechte_untersucht_bewertung',
            geom_column = 'geop',
            qmlfile=os.path.join(self.qmlDir, 'schaechte_untersucht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

    def einzelfallbetrachtung_haltung(self):
        date = self.date
        db = self.db

        leitung = self.leitung
        haltung = self.haltung
        crs = self.crs

        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_haltung_bewertung AS SELECT * FROM untersuchdat_haltung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
        except:
            pass

        if haltung is True:
            sql = """
                        SELECT
                            haltungen.haltnam,
                            haltungen.material,
                            haltungen.hoehe,
                            untersuchdat_haltung_bewertung.untersuchhal
                        FROM haltungen
                        INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
                    """

        if leitung is True:
            sql = """
                        SELECT
                            anschlussleitungen.leitnam,
                            anschlussleitungen.material,
                            anschlussleitungen.hoehe,
                            untersuchdat_haltung_bewertung.untersuchhal
                        FROM anschlussleitungen
                        INNER JOIN untersuchdat_haltung_bewertung  ON anschlussleitungen.leitnam = untersuchdat_haltung_bewertung.untersuchhal
                    """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():
            untersuchhalt = attr1[0]


            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                            "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk",
                            "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                            "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                              "GFK Glasfaserverstärkter Kunststoff",
                              "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                              "KST Nichtidentifizier Kunststoff",
                              "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                              "PP Polypropylen",
                              "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                              "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                              "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                              "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                              UPDATE untersuchdat_haltung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()


        sql = f"""update untersuchdat_haltung_bewertung set
                            Zustandsklasse_S = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 6 THEN '3_isy'
                                        WHEN quantnr1 < 15 THEN '4_isy'
                                        WHEN quantnr1 >= 15 THEN '5_isy'
                                    END)
                        WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegesteif'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung') 
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_S = (CASE
                                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 2 THEN '1_isy'
                                                WHEN quantnr1 < 6 THEN '2_isy'
                                                WHEN quantnr1 < 10 THEN '3_isy'
                                                WHEN quantnr1 < 15 THEN '4_isy'
                                                WHEN quantnr1 >= 15 THEN '5_isy'
                                            END)
                                WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegeweich'
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung') 
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_B = (CASE
                                            WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 10 THEN '1_isy'
                                            WHEN quantnr1 < 25 THEN '2_isy'
                                            WHEN quantnr1 < 40 THEN '3_isy'
                                            WHEN quantnr1 < 50 THEN '4_isy'
                                            WHEN quantnr1 >= 50 THEN '5_isy'
                                        END)
                            WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs IN ('biegesteif','biegeweich')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                            Zustandsklasse_S = '1_isy',
                                            Zustandsklasse_D = '1_isy'
                                        WHERE kuerzel = 'BAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                        CASE
                                            WHEN charakt1 = 'B' THEN '3_isy'
                                            WHEN charakt1 = 'C' THEN '1_isy'
                                        END),
                                Zustandsklasse_S = (
                                        CASE WHEN charakt2 = 'B' THEN '1_isy'
                                            WHEN charakt2 in ('A', 'C', 'D', 'E') THEN 
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 2 AND quantnr1 > 0.5 THEN '2_isy'
                                                    WHEN quantnr1 < 5 THEN '3_isy'
                                                    WHEN quantnr1 < 10 THEN '4_isy'
                                                    WHEN quantnr1 >= 10 THEN '5_isy'
                                            END
                                        END
                                        )
                            WHERE kuerzel = 'BAB' AND charakt1 in ('B', 'C') AND charakt2 in ('A','B','C','D','E')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '4_isy'
                                        WHEN charakt1 = 'B' THEN '4_isy'
                                        WHEN charakt1 = 'C' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'B' THEN '3_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BAC' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                        WHEN charakt1 = 'B' AND charakt2 = 'A' THEN '3_isy'
                                        WHEN charakt1 = 'B' AND charakt2 = 'B' THEN '3_isy'
                                        WHEN charakt1 = 'C' THEN '5_isy'
                                        WHEN charakt1 = 'D' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'B' AND charakt2 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'B' AND charakt2 = 'B' THEN '3_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                    WHEN charakt1 = 'D' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN '2_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                    WHEN charakt1 = 'D' THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BAD' AND charakt1 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 <100 THEN '1_isy'
                                        ELSE '3_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 <20 THEN '1_isy'
                                    WHEN quantnr1 <50 THEN '2_isy'
                                    WHEN quantnr1 <100 THEN '3_isy'
                                    WHEN quantnr1 >=100 THEN '4_isy'
                                END
                                )
                            WHERE kuerzel = 'BAE' 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '5_isy'
                                        WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '3_isy'
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '4_isy'
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '3_isy'
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN '4_isy'
                                    WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '4_isy'
                                    WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN '1_isy'
                                    WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                END
                                )
                            WHERE kuerzel = 'BAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                              AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                   Zustandsklasse_B = (
                                       CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                           WHEN quantnr1 < 15 THEN '1_isy'
                                           WHEN quantnr1 < 40 THEN '2_isy'
                                           WHEN quantnr1 < 60 THEN '3_isy'
                                           WHEN quantnr1 < 75 THEN '4_isy'
                                           WHEN quantnr1 >= 75 THEN '5_isy'
                                       END
                                   )
                               WHERE kuerzel = 'BAG' 
                                 AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                       OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                     ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 in ('B', 'C','D') THEN '3_isy'
                                    WHEN charakt1 = 'Z' THEN '2_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN '2_isy'
                                END
                                )
                            WHERE kuerzel = 'BAH' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN
                                            CASE WHEN charakt2 = 'A' THEN '1_isy'
                                                WHEN  charakt2 in ('B','C','D') THEN '2_isy'
                                                END
                                    WHEN charakt1 = 'Z' THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 5 THEN '1_isy'
                                            WHEN quantnr1 < 20 THEN '2_isy'
                                            WHEN quantnr1 < 35 THEN '3_isy'
                                            WHEN quantnr1 < 50 THEN '4_isy'
                                            WHEN quantnr1 >= 50 THEN '5_isy'
                                        END
                                END
                                )
                            WHERE kuerzel = 'BAI' AND charakt1 in ('A', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN untersuchdat_haltung_bewertung.charakt1 = 'A' THEN
                                        CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 400 THEN
                                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 30 THEN '2_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 <50 THEN '3_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 <70 THEN '4_isy' 
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >=70 THEN '5_isy'
                                                END
                                        WHEN haltungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 40 THEN '2_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 <60 THEN '3_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 <80 THEN  '4_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >=80 THEN '5_isy'
                                                END
                                        WHEN haltungen_untersucht_bewertung.breite/1000 > 800 THEN
                                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 40 THEN '2_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 <65 THEN '3_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 <90 THEN '4_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >=90 THEN '5_isy'
                                                END
                                        END
                                    WHEN untersuchdat_haltung_bewertung.charakt1 = 'B' THEN
                                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 10 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 15 THEN '2_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 20 THEN '3_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 30 THEN '4_isy' 
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >= 30 THEN '5_isy'
                                                END
                                    WHEN untersuchdat_haltung_bewertung.charakt1 = 'C' THEN
                                        CASE WHEN haltungen_untersucht_bewertung.breite/1000 <= 200 THEN
                                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 5 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 7 THEN '2_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 9 THEN '3_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 12 THEN '4_isy' 
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >= 12 THEN '5_isy'
                                                END
                                        WHEN haltungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 2 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN '2_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 4 THEN '3_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 6 THEN '4_isy' 
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >= 6 THEN '5_isy'
                                                END
                                        WHEN haltungen_untersucht_bewertung.breite/1000 > 500 THEN
                                            CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 1 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 3 THEN '2_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 4 THEN '3_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 6 THEN '4_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >= 6 THEN '5_isy'
                                                END
                                        END
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN untersuchdat_haltung_bewertung.charakt1 = 'B' THEN 
                                    CASE WHEN untersuchdat_haltung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 < 10 THEN '1_isy'
                                                WHEN untersuchdat_haltung_bewertung.quantnr1 >= 10 THEN '2_isy'
                                                END
                                END
                                ),
                                Zustandsklasse_S = '1_isy'
                            FROM haltungen_untersucht_bewertung
                            WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam
                            AND kuerzel = 'BAJ' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_haltung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_haltung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'B' THEN '1_isy'
                                        WHEN charakt1 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'I' THEN '3_isy'
                                        WHEN charakt1 = 'J' THEN '4_isy'
                                        WHEN charakt1 = 'K' THEN '3_isy'
                                        WHEN charakt1 = 'L' THEN '2_isy'
                                        WHEN charakt1 = 'M' THEN '3_isy'
                                        WHEN charakt1 = 'N' THEN '3_isy'
                                        WHEN charakt1 = 'Z' THEN '2_isy'
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN '1_isy'
                                                    WHEN quantnr1 < 20 THEN '2_isy'
                                                    WHEN quantnr1 < 35 THEN '3_isy'
                                                    WHEN quantnr1 < 50 THEN '4_isy'
                                                    WHEN quantnr1 >= 50 THEN '5_isy'
                                                    END
                                        WHEN charakt1 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'D' THEN '2_isy'
                                        WHEN charakt1 = 'E' THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN '1_isy'
                                                    WHEN quantnr1 < 20 THEN '2_isy'
                                                    WHEN quantnr1 < 35 THEN '3_isy'
                                                    WHEN quantnr1 < 50 THEN '4_isy'
                                                    WHEN quantnr1 >= 50 THEN '5_isy'
                                                    END
                                        WHEN charakt1 = 'G' THEN '1_isy'
                                        WHEN charakt1 = 'H' THEN '1_isy'
                                        WHEN charakt1 = 'Z' THEN '2_isy'
                                    END
                                    ),
                                    Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'D' AND charakt2 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'E' THEN '2_isy'
                                        WHEN charakt1 = 'F' THEN '2_isy'
                                        WHEN charakt1 = 'L' THEN '2_isy'
                                        WHEN charakt1 = 'Z' THEN '2_isy'
                                    END
                                    )
                                WHERE kuerzel = 'BAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '4_isy'
                                    WHEN charakt1 = 'B' THEN '4_isy'
                                    WHEN charakt1 = 'C' THEN '3_isy'
                                    WHEN charakt1 = 'D' THEN '3_isy'
                                    WHEN charakt1 = 'F' THEN '4_isy'
                                    WHEN charakt1 = 'G' THEN '2_isy'
                                    WHEN charakt1 = 'Z' THEN '2_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'E' THEN
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN '1_isy'
                                                WHEN quantnr1 < 20 THEN '2_isy'
                                                WHEN quantnr1 < 35 THEN '3_isy'
                                                WHEN quantnr1 < 50 THEN '4_isy'
                                                WHEN quantnr1 >= 50 THEN '5_isy'
                                                END
                                    WHEN charakt1 = 'Z' THEN '2_isy'
                                END
                                )
                            WHERE kuerzel = 'BAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F','G', 'Z')
                                AND charakt2 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = '3_isy',
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 in ('A', 'C') THEN '2_isy'
                                    WHEN charakt1 = 'B' THEN '1_isy'
                                END
                                )
                            WHERE kuerzel = 'BAM' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = '3_isy',
                                    Zustandsklasse_S = '3_isy'
                                WHERE kuerzel = 'BAN' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = '4_isy',
                                Zustandsklasse_S = '4_isy'
                            WHERE kuerzel = 'BAO' 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = '4_isy',
                                    Zustandsklasse_S = '5_isy'
                                WHERE kuerzel = 'BAP' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = '3_isy',
                                Zustandsklasse_B = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 10 THEN '2_isy'
                                    WHEN quantnr1 < 20 THEN '3_isy'
                                    WHEN quantnr1 < 30 THEN '4_isy'
                                    WHEN quantnr1 >= 30 THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BBA' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_B = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 10 THEN '2_isy'
                                    WHEN quantnr1 < 20 THEN '3_isy'
                                    WHEN quantnr1 < 30 THEN '4_isy'
                                    WHEN quantnr1 >= 30 THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BBB' AND charakt1 in ('A', 'B', 'C', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN '1_isy'
                                        WHEN quantnr1 < 25 THEN '2_isy'
                                        WHEN quantnr1 < 40 THEN '3_isy'
                                        WHEN quantnr1 < 50 THEN '4_isy'
                                        WHEN quantnr1 >= 50 THEN '5_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBC' AND charakt1 in ('A', 'B', 'C', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = '4_isy',
                                Zustandsklasse_S = '5_isy',
                                Zustandsklasse_B = (
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 10 THEN '2_isy'
                                                WHEN quantnr1 < 20 THEN '3_isy'
                                                WHEN quantnr1 < 30 THEN '4_isy'
                                                WHEN quantnr1 >= 30 THEN '5_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBD' AND charakt1 in ('A', 'B', 'C', 'D', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                            CASE WHEN charakt1 in ('D', 'G') THEN '3_isy'
                                    END
                                ),
                                Zustandsklasse_B = (
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN '1_isy'
                                                WHEN quantnr1 < 20 THEN '2_isy'
                                                WHEN quantnr1 < 35 THEN '3_isy'
                                                WHEN quantnr1 < 50 THEN '4_isy'
                                                WHEN quantnr1 >= 50 THEN '5_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_D = (
                                    CASE WHEN charakt1 in ('A', 'B') THEN '3_isy'
                                        WHEN charakt1 in ('C', 'D') THEN '4_isy'
                                    END
                                ),
                                Zustandsklasse_S = (
                                    CASE WHEN charakt1 in ('A', 'B') THEN '2_isy'
                                        WHEN charakt1 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'D' THEN '4_isy'
                                    END
                                ),
                                Zustandsklasse_B = (
                                    CASE WHEN charakt1 in ('A', 'B') THEN '1_isy'
                                        WHEN charakt1 in ('C', 'D') THEN '2_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBF' AND charakt1 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = '4_isy',
                                    Zustandsklasse_S = '2_isy'
                                WHERE kuerzel = 'BBG' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = '2_isy',
                                    Zustandsklasse_B = '2_isy'
                                WHERE kuerzel = 'BDB' AND charakt1 in ('AA', 'AB', 'AC', 'AD', 'AE')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                    Zustandsklasse_D = '2_isy'
                                WHERE kuerzel = 'BDB' AND charakt1 in ('BA', 'BB', 'BC')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_B = '2_isy'
                            WHERE kuerzel = 'BDD' AND charakt1 in ('A', 'B', 'C', 'D', 'E')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                Zustandsklasse_B = (
                                        CASE WHEN charakt2 = 'A' THEN '4_isy'
                                            WHEN charakt2 = 'B' THEN '3_isy'
                                        END
                                    )
                            WHERE kuerzel = 'BDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_haltung_bewertung set
                                                    Zustandsklasse_B = '-',
                                                    Zustandsklasse_S = '-',
                                                    Zustandsklasse_D = '-'
                                                WHERE kuerzel in ('BCD', 'BCE', 'BDC', 'BCA', 'BCB', 'BCC', 'BDA', 'BDF', 'BDG', 'BDB', 'AEC', 'AED')
                                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_haltung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_haltung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung');"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = """UPDATE untersuchdat_haltung_bewertung
                   SET Zustandsklasse_S = (Case 
                   WHEN Zustandsklasse_S = '5_isy'  THEN 0
                   WHEN Zustandsklasse_S = '4_isy'  THEN 1
                   WHEN Zustandsklasse_S = '3_isy'  THEN 2
                   WHEN Zustandsklasse_S = '2_isy'  THEN 3
                   WHEN Zustandsklasse_S = '1_isy'  THEN 4
                   WHEN Zustandsklasse_S = '0_isy'  THEN 5
                   ELSE Zustandsklasse_S
                   END)
                   WHERE (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                                                  );"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass
        sql = """UPDATE untersuchdat_haltung_bewertung
                               SET Zustandsklasse_B = (Case 
                               WHEN Zustandsklasse_B = '5_isy'  THEN 0
                               WHEN Zustandsklasse_B = '4_isy'  THEN 1
                               WHEN Zustandsklasse_B = '3_isy'  THEN 2
                               WHEN Zustandsklasse_B = '2_isy'  THEN 3
                               WHEN Zustandsklasse_B = '1_isy'  THEN 4
                               WHEN Zustandsklasse_B = '0_isy'  THEN 5
                               ELSE Zustandsklasse_B
                               END)
                               WHERE (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass
        sql = """UPDATE untersuchdat_haltung_bewertung
                                           SET Zustandsklasse_D = (Case 
                                           WHEN Zustandsklasse_D = '5_isy'  THEN 0
                                           WHEN Zustandsklasse_D = '4_isy'  THEN 1
                                           WHEN Zustandsklasse_D = '3_isy'  THEN 2
                                           WHEN Zustandsklasse_D = '2_isy'  THEN 3
                                           WHEN Zustandsklasse_D = '1_isy'  THEN 4
                                           WHEN Zustandsklasse_D = '0_isy'  THEN 5
                                           ELSE Zustandsklasse_D
                                           END)
                                           WHERE (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass


        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value,
            table='untersuchdat_haltung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_haltung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HALTUNGEN.value,
            table='haltungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'haltungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

    def einzelfallbetrachtung_leitung(self):

        date = self.date
        db = self.db
        leitung = self.leitung
        haltung = self.haltung
        crs = self.crs

        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_anschlussleitung_bewertung AS SELECT * FROM untersuchdat_anschlussleitung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
        except:
            pass

        if haltung is True:
            sql = """
                        SELECT
                            haltungen.haltnam,
                            haltungen.material,
                            haltungen.hoehe,
                            untersuchdat_haltung_bewertung.untersuchhal
                        FROM haltungen
                        INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
                    """

        if leitung is True:
            sql = """
                        SELECT
                            anschlussleitungen.leitnam,
                            anschlussleitungen.material,
                            anschlussleitungen.hoehe,
                            untersuchdat_anschlussleitung_bewertung.untersuchleit
                        FROM anschlussleitungen
                        INNER JOIN untersuchdat_anschlussleitung_bewertung  ON anschlussleitungen.leitnam = untersuchdat_anschlussleitung_bewertung.untersuchleit
                    """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():
            untersuchhalt = attr1[0]


            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                            "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk",
                            "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                            "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                            UPDATE untersuchdat_anschlussleitung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                              "GFK Glasfaserverstärkter Kunststoff",
                              "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                              "KST Nichtidentifizier Kunststoff",
                              "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                              "PP Polypropylen",
                              "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                              "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                              "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                              "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                              UPDATE untersuchdat_anschlussleitung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()


        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                            Zustandsklasse_S = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 6 THEN '3_isy'
                                        WHEN quantnr1 < 15 THEN '4_isy'
                                        WHEN quantnr1 >= 15 THEN '5_isy'
                                    END)
                        WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegesteif'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_S = (CASE
                                                WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 2 THEN '1_isy'
                                                WHEN quantnr1 < 6 THEN '2_isy'
                                                WHEN quantnr1 < 10 THEN '3_isy'
                                                WHEN quantnr1 < 15 THEN '4_isy'
                                                WHEN quantnr1 >= 15 THEN '5_isy'
                                            END)
                                WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs = 'biegeweich'
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_B = (CASE
                                            WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 10 THEN '1_isy'
                                            WHEN quantnr1 < 25 THEN '2_isy'
                                            WHEN quantnr1 < 40 THEN '3_isy'
                                            WHEN quantnr1 < 50 THEN '4_isy'
                                            WHEN quantnr1 >= 50 THEN '5_isy'
                                        END)
                            WHERE kuerzel = 'BAA' AND charakt1 in ('A','B') AND bw_bs IN ('biegesteif','biegeweich')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                            Zustandsklasse_S = '1_isy',
                                            Zustandsklasse_D = '1_isy'
                                        WHERE kuerzel = 'BAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                        CASE
                                            WHEN charakt1 = 'B' THEN '3_isy'
                                            WHEN charakt1 = 'C' THEN '1_isy'
                                        END),
                                Zustandsklasse_S = (
                                        CASE WHEN charakt2 = 'B' THEN '1_isy'
                                            WHEN charakt2 in ('A', 'C', 'D', 'E') THEN 
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 2 AND quantnr1 > 0.5 THEN '2_isy'
                                                    WHEN quantnr1 < 5 THEN '3_isy'
                                                    WHEN quantnr1 < 10 THEN '4_isy'
                                                    WHEN quantnr1 >= 10 THEN '5_isy'
                                            END
                                        END
                                        )
                            WHERE kuerzel = 'BAB' AND charakt1 in ('B', 'C') AND charakt2 in ('A','B','C','D','E')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '4_isy'
                                        WHEN charakt1 = 'B' THEN '4_isy'
                                        WHEN charakt1 = 'C' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'B' THEN '3_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BAC' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                        WHEN charakt1 = 'B' AND charakt2 = 'A' THEN '3_isy'
                                        WHEN charakt1 = 'B' AND charakt2 = 'B' THEN '3_isy'
                                        WHEN charakt1 = 'C' THEN '5_isy'
                                        WHEN charakt1 = 'D' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'B' AND charakt2 = 'A' THEN '3_isy'
                                    WHEN charakt1 = 'B' AND charakt2 = 'B' THEN '3_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                    WHEN charakt1 = 'D' THEN '5_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN '2_isy'
                                    WHEN charakt1 = 'C' THEN '5_isy'
                                    WHEN charakt1 = 'D' THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BAD' AND charakt1 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 <100 THEN '1_isy'
                                        ELSE '3_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 <20 THEN '1_isy'
                                    WHEN quantnr1 <50 THEN '2_isy'
                                    WHEN quantnr1 <100 THEN '3_isy'
                                    WHEN quantnr1 >=100 THEN '4_isy'
                                END
                                )
                            WHERE kuerzel = 'BAE' 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '5_isy'
                                        WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                END
                                ),
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '3_isy'
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '4_isy'
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '3_isy'
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN '4_isy'
                                    WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '4_isy'
                                    WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') THEN '1_isy'
                                    WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                    WHEN charakt1 = 'J' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '2_isy'
                                    WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') THEN '1_isy'
                                END
                                )
                            WHERE kuerzel = 'BAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                              AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                   Zustandsklasse_B = (
                                       CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                           WHEN quantnr1 < 15 THEN '1_isy'
                                           WHEN quantnr1 < 40 THEN '2_isy'
                                           WHEN quantnr1 < 60 THEN '3_isy'
                                           WHEN quantnr1 < 75 THEN '4_isy'
                                           WHEN quantnr1 >= 75 THEN '5_isy'
                                       END
                                   )
                               WHERE kuerzel = 'BAG' 
                                 AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                       OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                     ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 in ('B', 'C','D') THEN '3_isy'
                                    WHEN charakt1 = 'Z' THEN '2_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN '2_isy'
                                END
                                )
                            WHERE kuerzel = 'BAH' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '3_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'A' THEN
                                            CASE WHEN charakt2 = 'A' THEN '1_isy'
                                                WHEN  charakt2 in ('B','C','D') THEN '2_isy'
                                                END
                                    WHEN charakt1 = 'Z' THEN
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 5 THEN '1_isy'
                                            WHEN quantnr1 < 20 THEN '2_isy'
                                            WHEN quantnr1 < 35 THEN '3_isy'
                                            WHEN quantnr1 < 50 THEN '4_isy'
                                            WHEN quantnr1 >= 50 THEN '5_isy'
                                        END
                                END
                                )
                            WHERE kuerzel = 'BAI' AND charakt1 in ('A', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'A' THEN
                                        CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 400 THEN
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 30 THEN '2_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <50 THEN '3_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <70 THEN '4_isy' 
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=70 THEN '5_isy'
                                                END
                                        WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 800 THEN
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 40 THEN '2_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <60 THEN '3_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <80 THEN  '4_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=80 THEN '5_isy'
                                                END
                                        WHEN anschlussleitungen_untersucht_bewertung.breite/1000 > 800 THEN
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 40 THEN '2_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <65 THEN '3_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 <90 THEN '4_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >=90 THEN '5_isy'
                                                END
                                        END
                                    WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'B' THEN
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 10 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 15 THEN '2_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 20 THEN '3_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 30 THEN '4_isy' 
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 30 THEN '5_isy'
                                                END
                                    WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'C' THEN
                                        CASE WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 200 THEN
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 5 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 7 THEN '2_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 9 THEN '3_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 12 THEN '4_isy' 
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 12 THEN '5_isy'
                                                END
                                        WHEN anschlussleitungen_untersucht_bewertung.breite/1000 <= 500 THEN
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 2 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN '2_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 4 THEN '3_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 6 THEN '4_isy' 
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 6 THEN '5_isy'
                                                END
                                        WHEN anschlussleitungen_untersucht_bewertung.breite/1000 > 500 THEN
                                            CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 1 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 3 THEN '2_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 4 THEN '3_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 6 THEN '4_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 6 THEN '5_isy'
                                                END
                                        END
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN untersuchdat_anschlussleitung_bewertung.charakt1 = 'B' THEN 
                                    CASE WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 < 10 THEN '1_isy'
                                                WHEN untersuchdat_anschlussleitung_bewertung.quantnr1 >= 10 THEN '2_isy'
                                                END
                                    END
                                ),
                                Zustandsklasse_S = '1_isy'
                            FROM anschlussleitungen_untersucht_bewertung
                            WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam
                            AND kuerzel = 'BAJ' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchdat_anschlussleitung_bewertung.untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'B' THEN '1_isy'
                                        WHEN charakt1 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'I' THEN '3_isy'
                                        WHEN charakt1 = 'J' THEN '4_isy'
                                        WHEN charakt1 = 'K' THEN '3_isy'
                                        WHEN charakt1 = 'L' THEN '2_isy'
                                        WHEN charakt1 = 'M' THEN '3_isy'
                                        WHEN charakt1 = 'N' THEN '3_isy'
                                        WHEN charakt1 = 'Z' THEN '2_isy'
                                    END
                                    ),
                                    Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN '1_isy'
                                                    WHEN quantnr1 < 20 THEN '2_isy'
                                                    WHEN quantnr1 < 35 THEN '3_isy'
                                                    WHEN quantnr1 < 50 THEN '4_isy'
                                                    WHEN quantnr1 >= 50 THEN '5_isy'
                                                    END
                                        WHEN charakt1 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'D' THEN '2_isy'
                                        WHEN charakt1 = 'E' THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 5 THEN '1_isy'
                                                    WHEN quantnr1 < 20 THEN '2_isy'
                                                    WHEN quantnr1 < 35 THEN '3_isy'
                                                    WHEN quantnr1 < 50 THEN '4_isy'
                                                    WHEN quantnr1 >= 50 THEN '5_isy'
                                                    END
                                        WHEN charakt1 = 'G' THEN '1_isy'
                                        WHEN charakt1 = 'H' THEN '1_isy'
                                        WHEN charakt1 = 'Z' THEN '2_isy'
                                    END
                                    ),
                                    Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'D' AND charakt2 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'E' THEN '2_isy'
                                        WHEN charakt1 = 'F' THEN '2_isy'
                                        WHEN charakt1 = 'L' THEN '2_isy'
                                        WHEN charakt1 = 'Z' THEN '2_isy'
                                    END
                                    )
                                WHERE kuerzel = 'BAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                CASE WHEN charakt1 = 'A' THEN '4_isy'
                                    WHEN charakt1 = 'B' THEN '4_isy'
                                    WHEN charakt1 = 'C' THEN '3_isy'
                                    WHEN charakt1 = 'D' THEN '3_isy'
                                    WHEN charakt1 = 'F' THEN '4_isy'
                                    WHEN charakt1 = 'G' THEN '2_isy'
                                    WHEN charakt1 = 'Z' THEN '2_isy'
                                END
                                ),
                                Zustandsklasse_B = (
                                CASE WHEN charakt1 = 'E' THEN
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN '1_isy'
                                                WHEN quantnr1 < 20 THEN '2_isy'
                                                WHEN quantnr1 < 35 THEN '3_isy'
                                                WHEN quantnr1 < 50 THEN '4_isy'
                                                WHEN quantnr1 >= 50 THEN '5_isy'
                                                END
                                    WHEN charakt1 = 'Z' THEN '2_isy'
                                END
                                )
                            WHERE kuerzel = 'BAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F','G', 'Z')
                                AND charakt2 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = '3_isy',
                                Zustandsklasse_S = (
                                CASE WHEN charakt1 in ('A', 'C') THEN '2_isy'
                                    WHEN charakt1 = 'B' THEN '1_isy'
                                END
                                )
                            WHERE kuerzel = 'BAM' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = '3_isy',
                                    Zustandsklasse_S = '3_isy'
                                WHERE kuerzel = 'BAN' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = '4_isy',
                                Zustandsklasse_S = '4_isy'
                            WHERE kuerzel = 'BAO' 
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = '4_isy' ,
                                    Zustandsklasse_S = '5_isy'
                                WHERE kuerzel = 'BAP' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = '3_isy',
                                Zustandsklasse_B = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 10 THEN '2_isy'
                                    WHEN quantnr1 < 20 THEN '3_isy'
                                    WHEN quantnr1 < 30 THEN '4_isy'
                                    WHEN quantnr1 >= 30 THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BBA' AND charakt1 in ('A', 'B', 'C')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_B = (
                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                    WHEN quantnr1 < 10 THEN '2_isy'
                                    WHEN quantnr1 < 20 THEN '3_isy'
                                    WHEN quantnr1 < 30 THEN '4_isy'
                                    WHEN quantnr1 >= 30 THEN '5_isy'
                                END
                                )
                            WHERE kuerzel = 'BBB' AND charakt1 in ('A', 'B', 'C', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_B = (
                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN '1_isy'
                                        WHEN quantnr1 < 25 THEN '2_isy'
                                        WHEN quantnr1 < 40 THEN '3_isy'
                                        WHEN quantnr1 < 50 THEN '4_isy'
                                        WHEN quantnr1 >= 50 THEN '5_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBC' AND charakt1 in ('A', 'B', 'C', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = '4_isy',
                                Zustandsklasse_S = '5_isy',
                                Zustandsklasse_B = (
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 10 THEN '2_isy'
                                                WHEN quantnr1 < 20 THEN '3_isy'
                                                WHEN quantnr1 < 30 THEN '4_isy'
                                                WHEN quantnr1 >= 30 THEN '5_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBD' AND charakt1 in ('A', 'B', 'C', 'D', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                            CASE WHEN charakt1 in ('D', 'G') THEN '3_isy'
                                    END
                                ),
                                Zustandsklasse_B = (
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 5 THEN '1_isy'
                                                WHEN quantnr1 < 20 THEN '2_isy'
                                                WHEN quantnr1 < 35 THEN '3_isy'
                                                WHEN quantnr1 < 50 THEN '4_isy'
                                                WHEN quantnr1 >= 50 THEN '5_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_D = (
                                    CASE WHEN charakt1 in ('A', 'B') THEN '3_isy'
                                        WHEN charakt1 in ('C', 'D') THEN '4_isy'
                                    END
                                ),
                                Zustandsklasse_S = (
                                    CASE WHEN charakt1 in ('A', 'B') THEN '2_isy'
                                        WHEN charakt1 = 'C' THEN '3_isy'
                                        WHEN charakt1 = 'D' THEN '4_isy'
                                    END
                                ),
                                Zustandsklasse_B = (
                                    CASE WHEN charakt1 in ('A', 'B') THEN '1_isy'
                                        WHEN charakt1 in ('C', 'D') THEN '2_isy'
                                    END
                                )
                            WHERE kuerzel = 'BBF' AND charakt1 in ('A', 'B', 'C', 'D')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = '4_isy',
                                    Zustandsklasse_S = '2_isy'
                                WHERE kuerzel = 'BBG' 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = '2_isy',
                                    Zustandsklasse_B = '2_isy'
                                WHERE kuerzel = 'BDB' AND charakt1 in ('AA', 'AB', 'AC', 'AD', 'AE')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                    Zustandsklasse_D = '2_isy'
                                WHERE kuerzel = 'BDB' AND charakt1 in ('BA', 'BB', 'BC')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_B = '2_isy'
                            WHERE kuerzel = 'BDD' AND charakt1 in ('A', 'B', 'C', 'D', 'E')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                Zustandsklasse_B = (
                                        CASE WHEN charakt2 = 'A' THEN '4_isy'
                                            WHEN charakt2 = 'B' THEN '3_isy'
                                        END
                                    )
                            WHERE kuerzel = 'BDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

            sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                       Zustandsklasse_B = '-'
                                       WHERE kuerzel not NULL AND Zustandsklasse_B is NULL 
                                         AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                             ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

            data = {'datumswahl': self.datetype, 'datumswert': date}

            try:
                db.sql(sql, parameters=data)
            except:
                pass

            sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                               Zustandsklasse_S = '-'
                                               WHERE kuerzel not NULL AND Zustandsklasse_S is NULL 
                                                 AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                                       OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                                     ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

            data = {'datumswahl': self.datetype, 'datumswert': date}

            try:
                db.sql(sql, parameters=data)
            except:
                pass

            sql = f"""update untersuchdat_anschlussleitung_bewertung set
                                       Zustandsklasse_D = '-'
                                       WHERE kuerzel not NULL AND Zustandsklasse_D is NULL 
                                         AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                             ) AND (untersuchdat_anschlussleitung_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_anschlussleitung_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

            data = {'datumswahl': self.datetype, 'datumswert': date}

            try:
                db.sql(sql, parameters=data)
            except:
                pass


        sql = """UPDATE untersuchdat_anschlussleitung_bewertung
                   SET Zustandsklasse_S = (Case 
                   WHEN Zustandsklasse_S = '5_isy'  THEN 0
                   WHEN Zustandsklasse_S = '4_isy'  THEN 1
                   WHEN Zustandsklasse_S = '3_isy'  THEN 2
                   WHEN Zustandsklasse_S = '2_isy'  THEN 3
                   WHEN Zustandsklasse_S = '1_isy'  THEN 4
                   WHEN Zustandsklasse_S = '0_isy'  THEN 5
                   ELSE Zustandsklasse_S
                   END)
                   WHERE (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                             ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass
        sql = """UPDATE untersuchdat_anschlussleitung_bewertung
                               SET Zustandsklasse_B = (Case 
                               WHEN Zustandsklasse_B = '5_isy'  THEN 0
                               WHEN Zustandsklasse_B = '4_isy'  THEN 1
                               WHEN Zustandsklasse_B = '3_isy'  THEN 2
                               WHEN Zustandsklasse_B = '2_isy'  THEN 3
                               WHEN Zustandsklasse_B = '1_isy'  THEN 4
                               WHEN Zustandsklasse_B = '0_isy'  THEN 5
                               ELSE Zustandsklasse_B
                               END)
                               WHERE (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                             ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass
        sql = """UPDATE untersuchdat_anschlussleitung_bewertung
                                           SET Zustandsklasse_D = (Case 
                                           WHEN Zustandsklasse_D = '5_isy'  THEN 0
                                           WHEN Zustandsklasse_D = '4_isy'  THEN 1
                                           WHEN Zustandsklasse_D = '3_isy'  THEN 2
                                           WHEN Zustandsklasse_D = '2_isy'  THEN 3
                                           WHEN Zustandsklasse_D = '1_isy'  THEN 4
                                           WHEN Zustandsklasse_D = '0_isy'  THEN 5
                                           ELSE Zustandsklasse_D
                                           END)
                                           WHERE (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                             ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass


        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('anschlussleitungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HA_LEITUNGEN.value,
            table='untersuchdat_anschlussleitung_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_anschlussleitung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HA_LEITUNGEN.value,
            table='anschlussleitungen_untersucht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'anschlussleitungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

    def einzelfallbetrachtung_schacht(self):
        date = self.date
        db = self.db
        crs = self.crs

        # nach Isybau

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_schacht_bewertung AS SELECT * FROM untersuchdat_schacht"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """
                            SELECT
                                schaechte.schnam,
                                schaechte.material,
                                untersuchdat_schacht_bewertung.untersuchsch
                            FROM schaechte
                                INNER JOIN untersuchdat_schacht_bewertung  ON schaechte.schnam = untersuchdat_schacht_bewertung.untersuchsch
                        """
        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Schächte konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchhalt = attr1[0]
            try:
                db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                            "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk",
                            "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                            "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                            UPDATE untersuchdat_schacht_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                              "GFK Glasfaserverstärkter Kunststoff",
                              "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                              "KST Nichtidentifizier Kunststoff",
                              "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                              "PP Polypropylen",
                              "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                              "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                              "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                              "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                              UPDATE untersuchdat_schacht_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()


        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_S = '2_isy',
                            Zustandsklasse_B = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN '1_isy'
                                        WHEN quantnr1 < 20 THEN '2_isy'
                                        WHEN quantnr1 < 30 THEN '3_isy'
                                        WHEN quantnr1 < 40 THEN '4_isy'
                                        WHEN quantnr1 >= 40 THEN '5_isy'
                                    END)
                        WHERE kuerzel = 'DAA' AND charakt1 in ('A','B') AND bereich in ('B', 'C', 'D', 'F') AND bw_bs = 'biegeweich'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_S = '3_isy',
                            Zustandsklasse_B = (CASE
                                        WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                        WHEN quantnr1 < 10 THEN '1_isy'
                                        WHEN quantnr1 < 20 THEN '2_isy'
                                        WHEN quantnr1 < 30 THEN '3_isy'
                                        WHEN quantnr1 < 40 THEN '4_isy'
                                        WHEN quantnr1 >= 40 THEN '5_isy'
                                    END)
                        WHERE kuerzel = 'DAA' AND charakt1 in ('A','B') AND bereich in ('B', 'C', 'D', 'F') AND bw_bs = 'biegesteif'
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_S = '1_isy'
                                WHERE kuerzel = 'DAB' AND charakt1 = 'A' AND charakt2 in ('A','B','C','D','E') AND bereich in ('B', 'C', 'D', 'F', 'H', 'I', 'J') 
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                               Zustandsklasse_D = (
                                       CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '1_isy'
                                            WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                            WHEN charakt1 = 'B' AND bereich in ('I', 'J') THEN '3_isy'
                                            WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                            WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN '4_isy'
                                       END),
                               Zustandsklasse_S = (
                                       CASE WHEN charakt1 in ('B', 'C') AND charakt2 = 'A' AND bereich in ('B', 'C', 'D', 'F') THEN
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                               WHEN quantnr1 < 1 THEN '1_isy'
                                               WHEN quantnr1 < 3 THEN '2_isy'
                                               WHEN quantnr1 < 5 THEN '3_isy'
                                               WHEN quantnr1 < 8 THEN '4_isy'
                                               WHEN quantnr1 >= 8 THEN '5_isy'
                                               END
                                           WHEN charakt1 in ('B', 'C') AND charakt2 = 'B' AND bereich in ('B', 'C', 'D', 'F') THEN '1_isy'
                                           WHEN charakt1 in ('B', 'C') AND charakt2 in ('C', 'D', 'E') AND bereich in ('B', 'C', 'D', 'F') THEN '2_isy'
                                           END
                                       )
                           WHERE kuerzel = 'DAB' AND charakt1 in ('A', 'B', 'C') AND charakt2 in ('A','B','C','D','E') AND bereich in ('B', 'C', 'D', 'F', 'I', 'J')
                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                 ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                                WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN '4_isy'
                                                WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                                WHEN charakt1 = 'B' AND bereich in ('I', 'J') THEN '4_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '4_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN '5_isy'
                                            END),
                                    Zustandsklasse_S = (
                                            CASE WHEN charakt1 in ('A', 'B') AND bereich in ('B', 'C', 'D', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'F', 'H') THEN '5_isy'
                                                END
                                            ),
                                    Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A'  AND bereich in ('B', 'C', 'D', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'F', 'H') THEN '5_isy'
                                                END
                                            )
                                WHERE kuerzel = 'DAC' AND charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'F','H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN '3_isy'
                                                WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('I', 'J') THEN '3_isy'
                                                WHEN charakt1 = 'B' AND charakt2 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                                WHEN charakt1 = 'B' AND charakt2 = 'B' AND bereich in ('I', 'J') THEN '4_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '4_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN '5_isy'
                                            END),
                                    Zustandsklasse_S = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'F') THEN '2_isy'
                                                WHEN charakt1 = 'B' AND charakt2 = 'A' AND bereich in ('C', 'D', 'F') THEN '3_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'F') THEN '5_isy'
                                                END
                                            ),
                                    Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'F') THEN '2_isy'
                                                WHEN charakt1 = 'A' AND bereich in ('H','I','J') THEN '3_isy'
                                                 WHEN charakt1 = 'B' AND charakt2 in ('A', 'B') AND bereich in ('H','I','J') THEN '3_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'F', 'H', 'I', 'J') THEN '5_isy'
                                                END
                                            )
                                WHERE kuerzel = 'DAD' AND charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 100 THEN '1_isy'
                                                    WHEN quantnr1 >= 100 THEN '2_isy'
                                                END
                                            WHEN bereich in ('I', 'J') THEN
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 100 THEN '1_isy'
                                                    WHEN quantnr1 >= 100 THEN '3_isy'
                                                END
                                        END),
                                Zustandsklasse_S = (
                                        CASE WHEN bereich in ('C', 'D', 'F') THEN 
                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                WHEN quantnr1 < 10 THEN '1_isy'
                                                WHEN quantnr1 < 100 THEN '2_isy'
                                                WHEN quantnr1 >= 100 THEN '3_isy'
                                           END
                                        END
                                        )
                            WHERE kuerzel = 'DAE' AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_D = (
                                    CASE WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN
                                           '4_isy'
                                        WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN
                                           '5_isy'
                                        WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN
                                             '2_isy'
                                    END),
                            Zustandsklasse_S = (
                                    CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '1_isy'
                                        WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '2_isy'
                                        WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '2_isy'
                                        WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '3_isy'
                                        WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '4_isy'
                                        WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '2_isy'
                                        WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '3_isy'
                                        WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '4_isy'
                                        WHEN charakt1 = 'I' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                        WHEN charakt1 = 'J' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in (A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'Z' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F', 'H') THEN '2_isy'       
                                    END
                                    ),
                            Zustandsklasse_B = (
                                    CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'B' AND charakt2 in ('A', 'E', 'Z') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'C' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'E' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'F' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'G' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'H' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in ('I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'J' AND charakt2 in ('B', 'C', 'D', 'E') AND bereich in (A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '1_isy'
                                        WHEN charakt1 = 'K' AND charakt2 in ('A', 'B', 'C', 'D', 'E', 'Z') AND bereich in ('I', 'J') THEN '2_isy'
                                        END
                                    )
                        WHERE kuerzel = 'DAF' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_B = (
                                    CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                        CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                            WHEN quantnr1 < 100 THEN '1_isy' 
                                            WHEN quantnr1 < 200 THEN '2_isy'
                                            WHEN quantnr1 < 300 THEN '3_isy'
                                            WHEN quantnr1 < 400 THEN '4_isy'
                                            WHEN quantnr1 >= 400 THEN '5_isy'
                                            END

                                        WHEN bereich in ('I','J') THEN '2_isy'
                                        END
                                    )
                        WHERE kuerzel = 'DAG' AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 in ('B', 'C', 'D') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                            WHEN charakt1 in ('B', 'C', 'D') AND bereich in ('I', 'J') THEN '3_isy'
                                            WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '2_isy'
                                            END
                                        )
                            WHERE kuerzel = 'DAH' AND charakt1 in ('B', 'C', 'D', 'E', 'Z') AND bereich in ('C', 'D', 'E', 'F','H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F') THEN '2_isy'
                                            WHEN charakt1 = 'A' AND charakt2 in ('A', 'B', 'C') AND bereich in ('I','J') THEN '3_isy'
                                            END
                                        ),
                                Zustandsklasse_B = (
                                        CASE WHEN charakt1 = 'Z'  AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '1_isy'
                                            END
                                        )
                            WHERE kuerzel = 'DAI' AND charakt1 in ('A', 'Z') AND bereich in ('B', 'C', 'D', 'E', 'F', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F') THEN '2_isy'
                                             END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'F') THEN '1_isy'
                                             END
                                        )
                            WHERE kuerzel = 'DAJ' AND charakt1 in ('A', 'B', 'C') AND bereich in ('B', 'C', 'D', 'E', 'F')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_D = (
                                            CASE WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '1_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN '3_isy'
                                                WHEN charakt1 = 'I' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'I' AND bereich in ('I', 'J') THEN '3_isy'
                                                WHEN charakt1 = 'J' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                                WHEN charakt1 = 'J' AND bereich in ('I','J') THEN '2_isy'
                                                WHEN charakt1 = 'K' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'K' AND bereich in ('I','J') THEN '3_isy'
                                                WHEN charakt1 = 'L' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '1_isy'
                                                WHEN charakt1 = 'L' AND bereich in ('I', 'J') THEN '2_isy'
                                                WHEN charakt1 = 'M' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 = 'M' AND bereich in ('I', 'J') THEN '3_isy'
                                                WHEN charakt1 = 'N' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '2_isy'
                                                WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '2_isy'
                                                 END
                                            ),
                                    Zustandsklasse_S = (
                                            CASE WHEN charakt1 = 'D' AND charakt2 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '2_isy'
                                                 WHEN charakt1 in ('E', 'F', 'L', 'Z') AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '2_isy'
                                                 END
                                            ),
                                    Zustandsklasse_B = (
                                            CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                        WHEN quantnr1 < 10 THEN '1_isy'
                                                        WHEN quantnr1 < 20 THEN '2_isy'
                                                        WHEN quantnr1 < 30 THEN '3_isy'
                                                        WHEN quantnr1 < 40 THEN '4_isy'
                                                        WHEN quantnr1 >= 40 THEN '5_isy'
                                                    END
                                                WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN 
                                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                        WHEN quantnr1 < 5 THEN '1_isy'
                                                        WHEN quantnr1 < 20 THEN '2_isy'
                                                        WHEN quantnr1 < 35 THEN '3_isy'
                                                        WHEN quantnr1 < 50 THEN '4_isy'
                                                        WHEN quantnr1 >= 50 THEN '5_isy'
                                                    END
                                                WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN '3_isy'
                                                WHEN charakt1 = 'D' AND charakt2 in ('A', 'B', 'C', 'D') AND bereich in ('I', 'J') THEN '2_isy'
                                                WHEN charakt1 = 'E' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN 
                                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                        WHEN quantnr1 < 10 THEN '1_isy'
                                                        WHEN quantnr1 < 20 THEN '2_isy'
                                                        WHEN quantnr1 < 30 THEN '3_isy'
                                                        WHEN quantnr1 < 40 THEN '4_isy'
                                                        WHEN quantnr1 >= 40 THEN '5_isy'
                                                    END
                                                WHEN charakt1 = 'E' AND bereich in ('I', 'J') THEN 
                                                    CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                        WHEN quantnr1 < 5 THEN '1_isy'
                                                        WHEN quantnr1 < 20 THEN '2_isy'
                                                        WHEN quantnr1 < 35 THEN '3_isy'
                                                        WHEN quantnr1 < 50 THEN '4_isy'
                                                        WHEN quantnr1 >= 50 THEN '5_isy'
                                                    END
                                                WHEN charakt1 = 'G' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '1_isy'
                                                WHEN charakt1 = 'H' AND bereich in ('I', 'J') THEN '1_isy'
                                                WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '2_isy'
                                                END
                                            )
                                WHERE kuerzel = 'DAK' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Z') 
                                AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                            Zustandsklasse_D = (
                                                    CASE WHEN charakt1 = 'A' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                                        WHEN charakt1 = 'A' AND bereich in ('I', 'J') THEN '4_isy'
                                                        WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'E', 'F', 'H', 'I', 'J') THEN '2_isy'
                                                        WHEN charakt1 = 'C' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                        WHEN charakt1 = 'C' AND bereich in ('I', 'J') THEN '3_isy'
                                                        WHEN charakt1 = 'D' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '1_isy'
                                                        WHEN charakt1 = 'D' AND bereich in ('I', 'J') THEN '3_isy'
                                                        WHEN charakt1 = 'F' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                                        WHEN charakt1 = 'F' AND bereich in ('I', 'J') THEN '4_isy'
                                                        WHEN charakt1 = 'G' AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '1_isy'
                                                        WHEN charakt1 = 'G' AND bereich in ('I', 'J') THEN '2_isy'
                                                        WHEN charakt1 = 'Z' AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '2_isy'
                                                        END
                                                    ),
                                            Zustandsklasse_B = (
                                                    CASE WHEN charakt1 = 'E' AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') THEN 
                                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                                WHEN quantnr1 < 10 THEN '1_isy'
                                                                WHEN quantnr1 < 20 THEN '2_isy'
                                                                WHEN quantnr1 < 30 THEN '3_isy'
                                                                WHEN quantnr1 < 40 THEN '4_isy'
                                                                WHEN quantnr1 >= 40 THEN '5_isy'
                                                            END
                                                        WHEN charakt1 = 'E' AND bereich in ('I', 'J') THEN 
                                                            CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                                WHEN quantnr1 < 5 THEN '1_isy'
                                                                WHEN quantnr1 < 20 THEN '2_isy'
                                                                WHEN quantnr1 < 35 THEN '3_isy'
                                                                WHEN quantnr1 < 50 THEN '4_isy'
                                                                WHEN quantnr1 >= 50 THEN '5_isy'
                                                            END
                                                        WHEN charakt1 = 'Z' AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '2_isy'
                                                        END
                                                    )
                                        WHERE kuerzel = 'DAL' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'Z') 
                                        AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                                          AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                            WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN '3_isy'
                                            END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN charakt1 in ('A', 'C') AND bereich in ('B', 'C', 'D', 'F') THEN '2_isy'
                                            WHEN charakt1 = 'B' AND bereich in ('B', 'C', 'D', 'F') THEN '1_isy'
                                            END
                                        )
                            WHERE kuerzel = 'DAM' AND charakt1 in ('A', 'B', 'C') 
                            AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                            WHEN bereich in ('I', 'J') THEN '3_isy'
                                            END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN '3_isy'
                                           END
                                        )
                            WHERE kuerzel = 'DAN' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                            WHEN bereich in ('I', 'J') THEN '4_isy'
                                            END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN '4_isy'
                                           END
                                        )
                            WHERE kuerzel = 'DAO' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                            WHEN bereich in ('I', 'J') THEN '4_isy'
                                            END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN '5_isy'
                                           END
                                        )
                            WHERE kuerzel = 'DAP' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = (
                                        CASE WHEN charakt1 in ('A', 'C', 'D', 'F', 'G', 'H', 'I', 'J', 'K') AND bereich in ('C', 'D', 'F') THEN '4_isy'
                                            WHEN charakt1 = 'B' AND bereich in ('C', 'D', 'F') THEN '5_isy'
                                            WHEN charakt1 = 'E' AND bereich in ('C', 'D', 'F') THEN '2_isy'
                                            WHEN charakt1 = 'Z' AND bereich in ('C', 'D', 'F') THEN '2_isy'
                                            END
                                        )

                            WHERE kuerzel = 'DAQ' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'Z') 
                            AND bereich in ('C', 'D', 'F')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = (
                                        CASE WHEN charakt1 in ('A', 'C', 'F') THEN '5_isy'
                                            WHEN charakt1 in ('B', 'E') THEN '2_isy'
                                            WHEN charakt1 = 'D' THEN '4_isy'
                                            WHEN charakt1 in ('G', 'H') THEN '3_isy'
                                            WHEN charakt1 = 'Z' THEN '2_isy'
                                            END
                                        )

                            WHERE kuerzel = 'DAR' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z') 
                            AND bereich = 'A'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                            WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN '3_isy'
                                            END
                                        ),
                                Zustandsklasse_B = (
                                        CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '2_isy'
                                            END
                                        )
                            WHERE kuerzel = 'DBA' AND charakt1 in ('A', 'B', 'C') 
                            AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_B = '2_isy'
                                WHERE kuerzel = 'DBB' AND charakt1 in ('A', 'B', 'C', 'Z') 
                                AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = (
                                        CASE WHEN bereich = 'H' THEN '2_isy'
                                            WHEN bereich = 'J' THEN 
                                                CASE WHEN quantnr1 IS NULL THEN 'Bitte pruefen'
                                                    WHEN quantnr1 < 50 THEN '1_isy'
                                                    WHEN quantnr1 < 100 THEN '2_isy'
                                                    WHEN quantnr1 < 300 THEN '3_isy'
                                                    WHEN quantnr1 >= 300 THEN '4_isy'
                                                END
                                            END
                                        )
                            WHERE kuerzel = 'DBC' AND charakt1 in ('C', 'Z') 
                            AND bereich in ('H', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = (
                                        CASE WHEN bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                            WHEN bereich in ('I', 'J') THEN '4_isy'
                                            END
                                        ),
                                Zustandsklasse_B = (
                                        CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN '2_isy'
                                           END
                                        ),
                                Zustandsklasse_S = (
                                        CASE WHEN bereich in ('B', 'C', 'D', 'E', 'F') THEN '5_isy'
                                           END
                                        )
                            WHERE kuerzel = 'DBD' AND bereich in ('B', 'C', 'D', 'E', 'F', 'H', 'I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                        Zustandsklasse_D = (
                                                CASE WHEN charakt1 in ('D', 'G') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                    WHEN charakt1 in ('D', 'G') AND bereich in ('I', 'J') THEN '3_isy'
                                                    END
                                                ),
                                        Zustandsklasse_B = (
                                                CASE WHEN charakt1 in ('A', 'B', 'C') AND bereich in ('I', 'J') THEN '2_isy'
                                                    WHEN charakt1 in ('D', 'E', 'F', 'G', 'H', 'Z') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '3_isy'
                                                   END
                                                )

                                    WHERE kuerzel = 'DBE' AND charakt1 in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'Z') 
                                    AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_D = (
                                            CASE WHEN charakt1 in ('A', 'B') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '2_isy'
                                                WHEN charakt1 in ('A', 'B') AND bereich in ('I', 'J') THEN '3_isy'
                                                WHEN charakt1 in ('C', 'D') AND bereich in ('C', 'D', 'E', 'F', 'H') THEN '3_isy'
                                                WHEN charakt1 in ('C', 'D') AND bereich in ('I', 'J') THEN '4_isy'
                                                END
                                            ),
                                    Zustandsklasse_S = (
                                            CASE WHEN charakt1 in ('A', 'B') AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '2_isy'
                                                WHEN charakt1 = 'C' AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '3_isy'
                                                WHEN charakt1 = 'D' AND bereich in ('B', 'C', 'D', 'E', 'F') THEN '4_isy'
                                                END
                                            ),
                                    Zustandsklasse_B = (
                                            CASE WHEN charakt1 in ('A', 'B') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '1_isy'
                                                WHEN charakt1 in ('C', 'D') AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN '2_isy'
                                                END
                                            )

                                WHERE kuerzel = 'DBF' AND charakt1 in ('A', 'B', 'C', 'D') AND charakt2 in ('A', 'B', 'C') 
                                AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_D = '4_isy',
                                Zustandsklasse_S = '2_isy'
                            WHERE kuerzel = 'DBG' AND bereich in ('I', 'J')
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                        Zustandsklasse_B = '2_isy'
                                    WHERE kuerzel = 'DCH' AND charakt1 = 'A' AND bereich = 'H'
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = '2_isy'
                            WHERE kuerzel = 'DCI' AND charakt1 in ('A', 'C') AND bereich = 'I'
                              AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                    Zustandsklasse_B = (
                                            CASE WHEN charakt1 in ('B', 'F')  THEN '5_isy'
                                                WHEN charakt1 in ('C', 'D', 'G', 'H')  THEN '2_isy'
                                                END
                                            )
                                    WHERE kuerzel = 'DCJ' AND charakt1 in ('B', 'C', 'D', 'F', 'G', 'H') AND bereich = 'F'
                                      AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                       Zustandsklasse_B = '2_isy'
                                   WHERE kuerzel = 'DCL' AND charakt1 in ('A', 'B', 'C') AND charakt2 = 'A' AND bereich = 'F'
                                     AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                   Zustandsklasse_B = '2_isy'
                               WHERE kuerzel = 'DCM' AND charakt1 in ('B', 'C') AND bereich = 'A'
                                 AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                       OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                     ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                           Zustandsklasse_B = '2_isy'
                                       WHERE kuerzel = 'DCN' AND charakt1 = 'B' AND bereich = 'J'
                                         AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                               OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                             ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                Zustandsklasse_B = (
                                        CASE WHEN charakt2 = 'A' THEN '4_isy'
                                            WHEN charakt2 = 'B' THEN '3_isy'
                                            END
                                        )
                                WHERE kuerzel = 'DDE' AND charakt1 in ('A', 'C', 'D', 'E') AND charakt2 in ('A', 'B') 
                                AND bereich in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
                                  AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                            Zustandsklasse_B = '-',
                            Zustandsklasse_S = '-',
                            Zustandsklasse_D = '-'
                            WHERE kuerzel in ('CED', 'DCA', 'DCB', 'DCG', 'DCK', 'DCO', 'DDA', 'DDB', 'DDC', 'DDD', 'DDF', 'DDG') 
                            AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass


        sql = f"""update untersuchdat_schacht_bewertung set
                                           Zustandsklasse_B = '-'
                                           WHERE kuerzel not NULL AND Zustandsklasse_B is NULL 
                                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                                 ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                   Zustandsklasse_S = '-'
                                   WHERE kuerzel not NULL AND Zustandsklasse_S is NULL 
                                     AND (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass

        sql = f"""update untersuchdat_schacht_bewertung set
                                           Zustandsklasse_D = '-'
                                           WHERE kuerzel not NULL AND Zustandsklasse_D is NULL 
                                             AND (    (:datumswahl = 'Importdatum'     AND julianday(untersuchtag) = julianday(:datumswert))
                                                   OR (:datumswahl = 'Befahrungsdatum' AND julianday(createdat)    = julianday(:datumswert))
                                                 ) AND (untersuchdat_schacht_bewertung.Zustandsklasse_D = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_B = 'Einzelfallbetrachtung'
                            OR
                            untersuchdat_schacht_bewertung.Zustandsklasse_S = 'Einzelfallbetrachtung')
;"""

        data = {'datumswahl': self.datetype, 'datumswert': date}

        try:
            db.sql(sql, parameters=data)
        except:
            pass



        sql = """UPDATE untersuchdat_schacht_bewertung
                   SET Zustandsklasse_S = (Case 
                   WHEN Zustandsklasse_S = '5_isy'  THEN 0
                   WHEN Zustandsklasse_S = '4_isy'  THEN 1
                   WHEN Zustandsklasse_S = '3_isy'  THEN 2
                   WHEN Zustandsklasse_S = '2_isy'  THEN 3
                   WHEN Zustandsklasse_S = '1_isy'  THEN 4
                   WHEN Zustandsklasse_S = '0_isy'  THEN 5
                   ELSE Zustandsklasse_S
                   END)
                   WHERE (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass
        sql = """UPDATE untersuchdat_schacht_bewertung
                               SET Zustandsklasse_B = (Case 
                               WHEN Zustandsklasse_B = '5_isy'  THEN 0
                               WHEN Zustandsklasse_B = '4_isy'  THEN 1
                               WHEN Zustandsklasse_B = '3_isy'  THEN 2
                               WHEN Zustandsklasse_B = '2_isy'  THEN 3
                               WHEN Zustandsklasse_B = '1_isy'  THEN 4
                               WHEN Zustandsklasse_B = '0_isy'  THEN 5
                               ELSE Zustandsklasse_B
                               END)
                               WHERE (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass
        sql = """UPDATE untersuchdat_schacht_bewertung
                                           SET Zustandsklasse_D = (Case 
                                           WHEN Zustandsklasse_D = '5_isy'  THEN 0
                                           WHEN Zustandsklasse_D = '4_isy'  THEN 1
                                           WHEN Zustandsklasse_D = '3_isy'  THEN 2
                                           WHEN Zustandsklasse_D = '2_isy'  THEN 3
                                           WHEN Zustandsklasse_D = '1_isy'  THEN 4
                                           WHEN Zustandsklasse_D = '0_isy'  THEN 5
                                           ELSE Zustandsklasse_D
                                           END)
                                           WHERE (    (:datumswahl = 'Importdatum'     AND ABS(julianday(createdat) = julianday(:datumswert))*1440<=15)
                            OR (:datumswahl = 'Befahrungsdatum' AND ABS(julianday(untersuchtag)    = julianday(:datumswert))*1440<=15)
                          ) ;"""
        data = {'datumswahl': self.datetype, 'datumswert': date}
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_schacht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_SCHAECHTE.value,
            table='untersuchdat_schacht_bewertung',
            geom_column = 'geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_schacht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_SCHAECHTE.value,
            table='schaechte_untersucht_bewertung',
            geom_column = 'geop',
            qmlfile=os.path.join(self.qmlDir, 'schaechte_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

    def tab_dwa_haltung(self):
        #tabellen DWA anlegen und vorhandene Zustandsklassen in richtige Spalte kopieren
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung


        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_haltung_bewertung AS SELECT * FROM untersuchdat_haltung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        sql = """CREATE TABLE IF NOT EXISTS haltungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
        db.sql(sql)
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
        except:
            pass


        sql = """
            SELECT
                haltungen.haltnam,
                haltungen.material,
                haltungen.hoehe,
                untersuchdat_haltung_bewertung.untersuchhal
            FROM haltungen
            INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
        """


        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchleit = attr1[0]


            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC", "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk", "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton", "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK", "GFK Glasfaserverstärkter Kunststoff",
                            "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST", "KST Nichtidentifizier Kunststoff",
                            "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP", "PP Polypropylen",
                            "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                            "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                            "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                            "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE untersuchdat_haltung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
            else:
                continue
        db.commit()
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""Update untersuchdat_haltung_bewertung set Zustandsklasse_B = ZB ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_haltung_bewertung set Zustandsklasse_D = ZD ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_haltung_bewertung set Zustandsklasse_S = ZS ;""")
        except:
            pass

        sql = """SELECT CreateSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
        # db.commit()
        except:
            pass

        #Objektklasse berechnen für jede Haltung dafür abfragen

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                            SET objektklasse_dichtheit = q.objektklasse_dichtheit
                            FROM (
                                SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                                untersuchhal
                                FROM untersuchdat_haltung_bewertung
                                WHERE Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                            WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                            SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                            FROM (
                                SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                                untersuchhal
                                FROM untersuchdat_haltung_bewertung
                                WHERE Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                            WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam
                            ;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE haltungen_untersucht_bewertung 
                            SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                            FROM (
                                SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                                untersuchhal
                                FROM untersuchdat_haltung_bewertung
                                WHERE Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_haltung_bewertung.untersuchhal) AS q
                            WHERE q.untersuchhal = haltungen_untersucht_bewertung.haltnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update haltungen_untersucht_bewertung
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        haltungen_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_haltung_bewertung WHERE untersuchdat_haltung_bewertung.untersuchhal = haltungen_untersucht_bewertung.haltnam)
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

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value,
            table='untersuchdat_haltung_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_haltung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HALTUNGEN.value,
            table='haltungen_untersucht_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'haltungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

    def tab_dwa_leitung(self):
        #tabellen DWA anlegen und vorhandene Zustandsklassen in richtige Spalte kopieren
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung


        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_anschlussleitung_bewertung AS SELECT * FROM untersuchdat_anschlussleitung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        sql = """CREATE TABLE IF NOT EXISTS anschlussleitungen_untersucht_bewertung AS SELECT * FROM anschlussleitungen_untersucht"""
        db.sql(sql)
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        sql = """
                SELECT
                    anschlussleitungen.leitnam,
                    anschlussleitungen.material,
                    anschlussleitungen.hoehe,
                    untersuchdat_anschlussleitung_bewertung.untersuchleit
                FROM anschlussleitungen
                INNER JOIN untersuchdat_anschlussleitung_bewertung ON anschlussleitungen.leitnam = untersuchdat_anschlussleitung_bewertung.untersuchleit
            """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchleit = attr1[0]
            try:
                db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC", "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk", "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton", "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                    UPDATE untersuchdat_anschlussleitung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK", "GFK Glasfaserverstärkter Kunststoff",
                            "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST", "KST Nichtidentifizier Kunststoff",
                            "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP", "PP Polypropylen",
                            "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                            "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                            "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                            "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                      UPDATE untersuchdat_anschlussleitung_bewertung
                        SET bw_bs = ?
                        WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                        """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
            else:
                continue
        db.commit()
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""Update untersuchdat_anschlussleitung_bewertung set Zustandsklasse_B = ZB ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_anschlussleitung_bewertung set Zustandsklasse_D = ZD ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_anschlussleitung_bewertung set Zustandsklasse_S = ZS ;""")
        except:
            pass

        sql = """SELECT CreateSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
        # db.commit()
        except:
            pass

        #Objektklasse berechnen für jede Haltung dafür abfragen

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_dichtheit = q.objektklasse_dichtheit
                            FROM (
                                SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                            FROM (
                                SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE anschlussleitungen_untersucht_bewertung 
                            SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                            FROM (
                                SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                                untersuchleit
                                FROM untersuchdat_anschlussleitung_bewertung
                                WHERE Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_anschlussleitung_bewertung.untersuchleit) AS q
                            WHERE q.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update anschlussleitungen_untersucht_bewertung
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        anschlussleitungen_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_anschlussleitung_bewertung WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = anschlussleitungen_untersucht_bewertung.leitnam)
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
                    );
                    """)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('anschlussleitungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HA_LEITUNGEN.value,
            table='untersuchdat_anschlussleitung_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_anschlussleitung_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HA_LEITUNGEN.value,
            table='anschlussleitungen_untersucht_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'anschlussleitungen_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

    def tab_dwa_schacht(self):
        #tabellen DWA anlegen und vorhandene Zustandsklassen in richtige Spalte kopieren
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung


        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_schacht_bewertung AS SELECT * FROM untersuchdat_schacht"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        sql = """CREATE TABLE IF NOT EXISTS schaechte_untersucht_bewertung AS SELECT * FROM schaechte_untersucht"""
        db.sql(sql)
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        sql = """
                    SELECT
                        schaechte.schnam,
                        schaechte.material,
                        untersuchdat_schacht_bewertung.untersuchsch
                    FROM schaechte
                        INNER JOIN untersuchdat_schacht_bewertung  ON schaechte.schnam = untersuchdat_schacht_bewertung.untersuchsch
                """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():
            try:
                db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                            "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk",
                            "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                            "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                            UPDATE untersuchdat_schacht_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                              "GFK Glasfaserverstärkter Kunststoff",
                              "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                              "KST Nichtidentifizier Kunststoff",
                              "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                              "PP Polypropylen",
                              "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                              "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                              "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                              "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                              UPDATE untersuchdat_schacht_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
        db.commit()

        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Zustandsklasse_B TEXT ;""")
        except:
            pass

        try:
            db.sql("""Update untersuchdat_schacht_bewertung set Zustandsklasse_B = ZB ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_schacht_bewertung set Zustandsklasse_D = ZD ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_schacht_bewertung set Zustandsklasse_S = ZS ;""")
        except:
            pass

        sql = """SELECT CreateSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_dichtheit INTEGER ;""")
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_standsicherheit INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_betriebssicherheit INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN objektklasse_gesamt INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN hydraulische_auslastung TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN lage_grundwasser TEXT;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN ueberdeckung INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN bodengruppe TEXT ;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_dichtheit = q.objektklasse_dichtheit
                            FROM (
                                SELECT min(Zustandsklasse_D) AS objektklasse_dichtheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_D <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_standsicherheit = q.objektklasse_standsicherheit
                            FROM (
                                SELECT min(Zustandsklasse_S) AS objektklasse_standsicherheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_S <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""UPDATE schaechte_untersucht_bewertung 
                            SET objektklasse_betriebssicherheit = q.objektklasse_betriebssicherheit
                            FROM (
                                SELECT min(Zustandsklasse_B) AS objektklasse_betriebssicherheit,
                                untersuchsch
                                FROM untersuchdat_schacht_bewertung
                                WHERE Zustandsklasse_B <> '-'
                                GROUP BY untersuchdat_schacht_bewertung.untersuchsch) AS q
                            WHERE q.untersuchsch = schaechte_untersucht_bewertung.schnam;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_standsicherheit = '-'
                                    WHERE objektklasse_standsicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_dichtheit = '-'
                                    WHERE objektklasse_dichtheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""update schaechte_untersucht_bewertung 
                                    set objektklasse_betriebssicherheit = '-'
                                    WHERE objektklasse_betriebssicherheit IS NULL;""")
        # db.commit()
        except:
            pass

        try:
            db.sql("""Update
                        schaechte_untersucht_bewertung
                       SET objektklasse_gesamt = (
                     SELECT
                      CASE
                      WHEN NOT EXISTS(SELECT 1 FROM untersuchdat_schacht_bewertung WHERE untersuchdat_schacht_bewertung.untersuchsch = schaechte_untersucht_bewertung.schnam)
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
                    );
                """)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_schacht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_SCHAECHTE.value,
            table='untersuchdat_schacht_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_schacht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_SCHAECHTE.value,
            table='schaechte_untersucht_bewertung',
            geom_column='geop',
            qmlfile=os.path.join(self.qmlDir, 'schaechte_untersucht_bewertung_dwa.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

    def tab_isybau_haltung(self):
        # tabellen ISYBAU anlegen und vorhandene Zustandsklassen in richtige Spalte kopieren

        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung


        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_haltung_bewertung AS SELECT * FROM untersuchdat_haltung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        sql = """CREATE TABLE IF NOT EXISTS haltungen_untersucht_bewertung AS SELECT * FROM haltungen_untersucht"""
        db.sql(sql)
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN bw_bs TEXT;""")
        except:
            pass


        sql = """
                    SELECT
                        haltungen.haltnam,
                        haltungen.material,
                        haltungen.hoehe,
                        untersuchdat_haltung_bewertung.untersuchhal
                    FROM haltungen
                    INNER JOIN untersuchdat_haltung_bewertung  ON haltungen.haltnam = untersuchdat_haltung_bewertung.untersuchhal
                """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchleit = attr1[0]


            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                            "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk",
                            "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                            "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                            UPDATE untersuchdat_haltung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                              "GFK Glasfaserverstärkter Kunststoff",
                              "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                              "KST Nichtidentifizier Kunststoff",
                              "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                              "PP Polypropylen",
                              "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                              "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                              "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                              "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                              UPDATE untersuchdat_haltung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_haltung_bewertung.untersuchhal = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
            else:
                continue
        db.commit()

        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
        except:
            pass


        try:
            db.sql("""Update untersuchdat_haltung_bewertung set Schadensklasse_B = ZB ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_haltung_bewertung set Schadensklasse_D = ZD ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_haltung_bewertung set Schadensklasse_S = ZS ;""")
        except:
            pass


        try:
            db.sql(
                """ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_haltung_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """UPDATE untersuchdat_haltung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_haltung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_haltung_bewertung
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

        sql = """SELECT CreateSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Lage_am_Umfang TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE haltungen_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
        # db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_haltung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_haltung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('haltungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('haltungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HALTUNGEN.value,
            table='untersuchdat_haltung_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_haltung_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HALTUNGEN.value,
            table='haltungen_untersucht_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'haltungen_untersucht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HALTUNGEN_GROUP.value],
        )

    def tab_isybau_leitung(self):
        # tabellen ISYBAU anlegen und vorhandene Zustandsklassen in richtige Spalte kopieren
        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_anschlussleitung_bewertung AS SELECT * FROM untersuchdat_anschlussleitung"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        sql = """CREATE TABLE IF NOT EXISTS anschlussleitungen_untersucht_bewertung AS SELECT * FROM anschlussleitungen_untersucht"""
        db.sql(sql)
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        sql = """
                        SELECT
                            anschlussleitungen.leitnam,
                            anschlussleitungen.material,
                            anschlussleitungen.hoehe,
                            untersuchdat_anschlussleitung_bewertung.untersuchleit
                        FROM anschlussleitungen
                        INNER JOIN untersuchdat_anschlussleitung_bewertung ON anschlussleitungen.leitnam = untersuchdat_anschlussleitung_bewertung.untersuchleit
                    """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchleit = attr1[0]
            try:
                db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

            if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ", "FZ Fasezement",
                            "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                            "PC Polymermodifizierter Zementbeton",
                            "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB", "SPB Spannbeton",
                            "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                            "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement", "Mauerwerk",
                            "Ortbeton",
                            "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                            "Spannbeton",
                            "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                bw_bs = "biegesteif"
                x = attr1[0]

                sql = f"""
                            UPDATE untersuchdat_anschlussleitung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass

            elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                              "GFK Glasfaserverstärkter Kunststoff",
                              "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                              "KST Nichtidentifizier Kunststoff",
                              "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                              "PP Polypropylen",
                              "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                              "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff", "Grauguß",
                              "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                              "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                bw_bs = 'biegeweich'
                x = attr1[0]

                sql = f"""
                              UPDATE untersuchdat_anschlussleitung_bewertung
                                SET bw_bs = ?
                                WHERE untersuchdat_anschlussleitung_bewertung.untersuchleit = ?
                                """
                data = (bw_bs, x)
                try:
                    db.sql(sql, parameters=data)
                except:
                    pass
            else:
                continue
        db.commit()

        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
        except:
            pass


        try:
            db.sql("""Update untersuchdat_anschlussleitung_bewertung set Schadensklasse_B = ZB ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_anschlussleitung_bewertung set Schadensklasse_D = ZD ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_anschlussleitung_bewertung set Schadensklasse_S = ZS ;""")
        except:
            pass


        try:
            db.sql(
                """ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_anschlussleitung_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """UPDATE untersuchdat_anschlussleitung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_anschlussleitung_bewertung
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
            db.sql(
                """UPDATE untersuchdat_anschlussleitung_bewertung
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

        sql = """SELECT CreateSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Lage_am_Umfang TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE anschlussleitungen_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
        # db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_anschlussleitung_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_anschlussleitung_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('anschlussleitungen_untersucht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('anschlussleitungen_untersucht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_HA_LEITUNGEN.value,
            table='untersuchdat_anschlussleitung_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_anschlussleitung_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_HA_LEITUNGEN.value,
            table='anschlussleitungen_untersucht_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'anschlussleitungen_untersucht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_HA_LEITUNGEN_GROUP.value],
        )

    def tab_isybau_schacht(self):
        # tabellen ISYBAU anlegen und vorhandene Zustandsklassen in richtige Spalte kopieren

        date = self.date
        db = self.db
        crs = self.crs
        leitung = self.leitung
        haltung = self.haltung

        sql = """CREATE TABLE IF NOT EXISTS untersuchdat_schacht_bewertung AS SELECT * FROM untersuchdat_schacht"""
        db.sql(sql)
        sql = """SELECT CreateSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass
        sql = """CREATE TABLE IF NOT EXISTS schaechte_untersucht_bewertung AS SELECT * FROM schaechte_untersucht"""
        db.sql(sql)
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Beschreibung TEXT ;""")
        except:
            pass

        sql = """
                            SELECT
                                schaechte.schnam,
                                schaechte.material,
                                untersuchdat_schacht_bewertung.untersuchsch
                            FROM schaechte
                                INNER JOIN untersuchdat_schacht_bewertung  ON schaechte.schnam = untersuchdat_schacht_bewertung.untersuchsch
                        """

        try:
            db.sql(sql)
        except:
            iface.messageBar().pushMessage("Error",
                                           "Die Klassifizierung der Haltungen/Leitungen konnte nicht ermittelt werden",
                                           level=Qgis.MessageLevel.Critical)

        for attr1 in db.fetchall():

            untersuchleit = attr1[0]
            try:
                db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN bw_bs TEXT;""")
            except:
                pass

                if attr1[1] in ["AZ", "AZ Asbestzement", "B", "B Beton", "BS", "BS Betonsegmente ", "FZ",
                                "FZ Fasezement",
                                "MA", "MA Mauerwerk", "OB", "OB Ortbeton", "P", "P Polymerbeton", "PC",
                                "PC Polymermodifizierter Zementbeton",
                                "PCC", "PHB", "PHB Polyesterharz", "SFB", "SFB Stahlfaserbeton", "SPB",
                                "SPB Spannbeton",
                                "SB", "SB Stahlbeton", "STZ", "STZ Steinzeug", "SZB", "SZB Spritzbeton",
                                "ZG", "ZG Ziegelwerk", "Asbestzement", "Beton", "Betonsegmente", "Fasezement",
                                "Mauerwerk",
                                "Ortbeton",
                                "Polymerbeton", "Polymermodifizierter Zementbeton", "Polyesterharz", "Stahlfaserbeton",
                                "Spannbeton",
                                "Stahlbeton", "Steinzeug", "Spritzbeton", "Ziegelwerk"]:
                    bw_bs = "biegesteif"
                    x = attr1[0]

                    sql = f"""
                                UPDATE untersuchdat_schacht_bewertung
                                    SET bw_bs = ?
                                    WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                                    """
                    data = (bw_bs, x)
                    try:
                        db.sql(sql, parameters=data)
                    except:
                        pass

                elif attr1[1] in ["CN", "CN Edelstahl", "EIS", "EIS Nichtidentifiziertes Metall", "GFK",
                                  "GFK Glasfaserverstärkter Kunststoff",
                                  "GG", "GG Grauguß", "GGG", "GGG Duktiles Gußeisen", "KST",
                                  "KST Nichtidentifizier Kunststoff",
                                  "PE", "PE Polyethylen", "PEHD", "PEHD Polyethylen", "PH", "PH Polyesterharz", "PP",
                                  "PP Polypropylen",
                                  "PVC", "PVC Polyvinylchlorid", "PVCU", "PVCU Polyvinylchlorid hart", "ST", "ST Stahl",
                                  "Edelstahl", "Nichtidentifiziertes Metall", "Glasfaserverstärkter Kunststoff",
                                  "Grauguß",
                                  "Duktiles Gußeisen", "Nichtidentifizier Kunststoff", "Polyethylen", "Polyesterharz",
                                  "Polypropylen", "Polyvinylchlorid", "Polyvinylchlorid hart", "Stahl"]:
                    bw_bs = 'biegeweich'
                    x = attr1[0]

                    sql = f"""
                                  UPDATE untersuchdat_schacht_bewertung
                                    SET bw_bs = ?
                                    WHERE untersuchdat_schacht_bewertung.untersuchsch = ?
                                    """
                    data = (bw_bs, x)
                    try:
                        db.sql(sql, parameters=data)
                    except:
                        pass
            db.commit()

        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_D TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_S TEXT ;""")
        except:
            pass
        try:
            db.sql("""ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN Schadensklasse_B TEXT ;""")
        except:
            pass


        try:
            db.sql("""Update untersuchdat_schacht_bewertung set Schadensklasse_B = ZB ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_schacht_bewertung set Schadensklasse_D = ZD ;""")
        except:
            pass
        try:
            db.sql("""Update untersuchdat_schacht_bewertung set Schadensklasse_S = ZS ;""")
        except:
            pass


        try:
            db.sql(
                """ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_D INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_B INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE untersuchdat_schacht_bewertung ADD COLUMN vorlaufige_Schadenszahl_S INTEGER ;""")
        except:
            pass

        try:
            db.sql(
                """UPDATE untersuchdat_schacht_bewertung
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
            db.sql(
                """UPDATE untersuchdat_schacht_bewertung
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
            db.sql(
                """UPDATE untersuchdat_schacht_bewertung
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

        sql = """SELECT CreateSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        try:
            db.sql(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Entwaesserungssystem TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Abwasserart TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Wasserschutzzone TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Grundwasserabstand INTEGER ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Bodenart TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql("""ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Lage_am_Umfang TEXT ;""")
        # db.commit()
        except:
            pass
        try:
            db.sql(
                """ALTER TABLE schaechte_untersucht_bewertung ADD COLUMN Lage_an_Bauteilverbindung TEXT ;""")
        # db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('untersuchdat_schacht_bewertung', 'geom', ?, 'LINESTRING', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('untersuchdat_schacht_bewertung', 'geom');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverGeometryColumn('schaechte_untersucht_bewertung', 'geop', ?, 'POINT', 'XY');"""
        data = (crs,)
        try:
            db.sql(sql, parameters=data)
            db.commit()
        except:
            pass

        sql = """SELECT RecoverSpatialIndex('schaechte_untersucht_bewertung', 'geop');"""
        try:
            db.sql(sql)
            db.commit()
        except:
            pass

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_EINZELSCHAEDEN_SCHAECHTE.value,
            table='untersuchdat_schacht_bewertung',
            geom_column='geom',
            qmlfile=os.path.join(self.qmlDir, 'untersuchdat_schacht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )

        loadLayer(
            layerbez=enums.LAYERBEZ.ZK_ZUSTAND_SCHAECHTE.value,
            table='schaechte_untersucht_bewertung',
            geom_column='geop',
            qmlfile=os.path.join(self.qmlDir, 'schaechte_untersucht_bewertung_isy.qml'),
            group=['QKan', enums.LAYERBEZ.ZUSTANDSBEWERTUNG_GROUP.value, enums.LAYERBEZ.ZK_SCHAECHTE_GROUP.value],
        )