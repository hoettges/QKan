import logging, os
from struct import unpack
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QProgressBar

from qkan import QKan
from qkan.database.dbfunc import DBConnection

logger = logging.getLogger("QKan.strakat.import")


class ImportTask:
    def __init__(
        self,
        db_qkan: DBConnection,
    ):
        # all parameters (except db_qkan) are passed via QKan.config
        self.db_qkan = db_qkan
        self.allrefs = QKan.config.check_import.allrefs
        self.epsg = QKan.config.epsg
        self.dbtyp = QKan.config.database_typ
        self.strakatdir = QKan.config.strakat.import_dir
        self.projectfile = QKan.config.project.file
        self.db_name = QKan.config.database.qkan

    def run(self) -> bool:

        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Import aus STRAKAT läuft. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

        result = all(
            [
                self._strakat_kanaltabelle(),
                self._strakat_reftables(),
                self._strakat_hausanschl(),
                # self._strakat_berichte(),
                self._reftables(),
                self._schaechte(),
                self._haltungen(),
                self._anschlussleitungen(),
                # self._schachtschaeden(),
                # self._haltungsschaeden(),
            ]
        )

        self.progress_bar.setValue(100)
        status_message.setText("Fertig! STRAKAT-Import abgeschlossen.")

        return result

    def _strakat_kanaltabelle(self) -> bool:
        """Import der Kanaldaten aus der STRAKAT-Datei 'kanal.rwtopen', ACCESS-Tabelle 'KANALTABELLE'
        """

        # Erstellung Tabelle t_strakatkanal
        sql = "PRAGMA table_list('t_strakatkanal')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_strakatkanal', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_strakatkanal (
                pk INTEGER PRIMARY KEY,
                nummer INTEGER,
                rw_gerinne_o REAL,
                hw_gerinne_o REAL,
                rw_gerinne_u REAL,
                hw_gerinne_u REAL,
                rw_rohranfang REAL,
                hw_rohranfang REAL,
                rw_rohrende REAL,
                hw_rohrende REAL,
                zuflussnummer1 INTEGER,
                zuflussnummer2 INTEGER,
                zuflussnummer3 INTEGER,
                zuflussnummer4 INTEGER,
                zuflussnummer5 INTEGER,
                zuflussnummer6 INTEGER,
                zuflussnummer7 INTEGER,
                zuflussnummer8 INTEGER,
                abflussnummer1 INTEGER,
                abflussnummer2 INTEGER,
                abflussnummer3 INTEGER,
                abflussnummer4 INTEGER,
                abflussnummer5 INTEGER,
                schacht_oben TEXT,
                schacht_unten TEXT,
                haltungsname TEXT,
                rohrbreite_v REAL,
                rohrhoehe___v REAL,
                flaechenfactor_v REAL,
                deckel_oben_v REAL,
                deckel_unten_v REAL,
                sohle_oben___v REAL,
                sohle_unten__v REAL,
                s_sohle_oben_v REAL,           -- Position in Datei kanal.rwtopen unbekannt
                sohle_zufluss1 REAL,
                sohle_zufluss2 REAL,
                sohle_zufluss3 REAL,
                sohle_zufluss4 REAL,
                sohle_zufluss5 REAL,
                sohle_zufluss6 REAL,
                sohle_zufluss7 REAL,
                sohle_zufluss8 REAL,
                kanalart INTEGER,
                profilart_v INTEGER,
                material_v INTEGER,
                e_gebiet INTEGER,
                strassennummer INTEGER,
                schachtnummer INTEGER,
                schachtart INTEGER,
                berichtsnummer INTEGER,
                laenge REAL,
                schachtmaterial INTEGER,
                oberflaeche INTEGER,
                baujahr INTEGER,
                wasserschutz INTEGER,
                eigentum INTEGER,
                naechste_halt INTEGER,
                rueckadresse INTEGER,
                strakatid TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakatkanal"'):
                return False

        # Datei kanal.rwtopen einlesen und in Tabelle schreiben
        blength = 1024                      # Blocklänge in der STRAKAT-Datei
        with open(os.path.join(self.strakatdir, 'kanal.rwtopen'), 'rb') as fo:
            _ = fo.read(blength)               # Kopfzeile ohne Bedeutung?
            for n in range(1, 1000000):
                """Einlesen der Blöcke. Begrenzung nur zur Sicherheit"""
                b = fo.read(blength)
                if not b:
                    break
                (
                    rw_gerinne_o, hw_gerinne_o,
                    rw_gerinne_u, hw_gerinne_u,
                    rw_rohranfang, hw_rohranfang,
                    rw_rohrende, hw_rohrende
                ) = (round(el, 3) for el in unpack('dddddddd', b[0:64]))

                (
                    zuflussnummer1, zuflussnummer2,
                    zuflussnummer3, zuflussnummer4,
                    zuflussnummer5, zuflussnummer6,
                    zuflussnummer7, zuflussnummer8,
                    abflussnummer1, abflussnummer2,
                    abflussnummer3, abflussnummer4,
                    abflussnummer5
                ) = unpack('iiiiiiiiiiiii', b[64:116])

                (
                    schacht_oben, haltungsname
                ) = [t.decode('ansi').strip() for t in unpack('15s15s', b[172:202].replace(b'\x00', b' '))]

                (
                    rohrbreite_v, rohrbreite_g, rohrhoehe___v, rohrhoehe___g,
                    wandstaerke_v, wandstaerke_g, ersatzdu___v, ersatzdu___g,
                    flaechenfactor_v, flaechenfactor_g, umfangsfactor_v, umfangsfactor_g,
                    hydr__radius_v, hydr__radius_g
                ) = unpack('ffffffffffffff', b[116:172])

                (
                    deckel_oben_v, deckel_oben_g, deckel_unten_v, deckel_unten_g,
                    sohle_oben___v, sohle_oben___g, sohle_unten__v, sohle_unten__g
                ) = (round(el, 3) for el in unpack('ffffffff', b[202:234]))

                (
                    sohle_zufluss1, sohle_zufluss2, sohle_zufluss3, sohle_zufluss4,
                    sohle_zufluss5, sohle_zufluss6, sohle_zufluss7, sohle_zufluss8
                ) = (round(el, 3) for el in unpack('ffffffff', b[434:466]))

                (
                    kanalart, profilart_v, profilart_g, material_v,
                    material_g, e_gebiet, strassennummer
                ) = unpack('hhhhhhh', b[490:504])

                (
                    schachtnummer, schachtart
                ) = unpack('ih', b[504:510])

                (  # kann nicht mit dem vorherigen
                    berichtsnummer, laenge, schachtmaterial  # zusammengefasst werden, weil Startadresse
                ) = unpack('ifh', b[510:520])  # glattes Vielfaches der Länge sein muss

                laenge = round(laenge, 3)

                oberflaeche = unpack('h', b[528:530])[0]
                oberflaeche_b = b[528:530]
                baujahr = unpack('h', b[550:552])[0]
                wasserschutz = unpack('h', b[554:556])[0]
                eigentum = unpack('h', b[556:558])[0]
                naechste_halt = unpack('i', b[558:562])[0]
                rueckadresse = unpack('i', b[562:566])[0]

                nummer = unpack('i', b[829:833])[0]

                (
                    h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[917:933])]
                strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                schacht_unten = unpack('15s', b[965:980])[0].replace(b'\x00', b' ').decode('ansi').strip()

                params = {
                        'nummer': nummer,
                        'rw_gerinne_o': rw_gerinne_o, 'hw_gerinne_o': hw_gerinne_o,
                        'rw_gerinne_u': rw_gerinne_u, 'hw_gerinne_u': hw_gerinne_u,
                        'rw_rohranfang': rw_rohranfang, 'hw_rohranfang': hw_rohranfang,
                        'rw_rohrende': rw_rohrende, 'hw_rohrende': hw_rohrende,
                        'zuflussnummer1': zuflussnummer1, 'zuflussnummer2': zuflussnummer2,
                        'zuflussnummer3': zuflussnummer3, 'zuflussnummer4': zuflussnummer4,
                        'zuflussnummer5': zuflussnummer5, 'zuflussnummer6': zuflussnummer6,
                        'zuflussnummer7': zuflussnummer7, 'zuflussnummer8': zuflussnummer8,
                        'abflussnummer1': abflussnummer1, 'abflussnummer2': abflussnummer2,
                        'abflussnummer3': abflussnummer3, 'abflussnummer4': abflussnummer4,
                        'abflussnummer5': abflussnummer5,
                        'schacht_oben': schacht_oben, 'schacht_unten': schacht_unten, 'haltungsname': haltungsname,
                        'rohrbreite_v': rohrbreite_v, 'rohrhoehe___v': rohrhoehe___v,
                        'flaechenfactor_v': flaechenfactor_v,
                        'deckel_oben_v': deckel_oben_v, 'deckel_unten_v': deckel_unten_v,
                        'sohle_oben___v': sohle_oben___v, 'sohle_unten__v': sohle_unten__v,
                        's_sohle_oben_v': 0,
                        'sohle_zufluss1': sohle_zufluss1, 'sohle_zufluss2': sohle_zufluss2,
                        'sohle_zufluss3': sohle_zufluss3, 'sohle_zufluss4': sohle_zufluss4,
                        'sohle_zufluss5': sohle_zufluss5, 'sohle_zufluss6': sohle_zufluss6,
                        'sohle_zufluss7': sohle_zufluss7, 'sohle_zufluss8': sohle_zufluss8,
                        'kanalart': kanalart, 'profilart_v': profilart_v, 'material_v': material_v,
                        'e_gebiet': e_gebiet, 'strassennummer': strassennummer,
                        'schachtnummer': schachtnummer, 'schachtart': schachtart, 'berichtsnummer': berichtsnummer,
                        'laenge': laenge, 'schachtmaterial': schachtmaterial, 'oberflaeche': oberflaeche,
                        'baujahr': baujahr, 'wasserschutz': wasserschutz, 'eigentum': eigentum,
                        'naechste_halt': naechste_halt, 'rueckadresse': rueckadresse, 'strakatid': strakatid}

                sql = """INSERT INTO t_strakatkanal (
                    nummer, 
                    rw_gerinne_o, hw_gerinne_o, rw_gerinne_u, hw_gerinne_u,
                    rw_rohranfang, hw_rohranfang, rw_rohrende, hw_rohrende,
                    zuflussnummer1, zuflussnummer2, zuflussnummer3, zuflussnummer4,
                    zuflussnummer5, zuflussnummer6, zuflussnummer7, zuflussnummer8,
                    abflussnummer1, abflussnummer2, abflussnummer3, abflussnummer4, abflussnummer5,
                    schacht_oben, schacht_unten, haltungsname,
                    rohrbreite_v, rohrhoehe___v, flaechenfactor_v,
                    deckel_oben_v, deckel_unten_v, sohle_oben___v, sohle_unten__v, s_sohle_oben_v,
                    sohle_zufluss1, sohle_zufluss2, sohle_zufluss3, sohle_zufluss4,
                    sohle_zufluss5, sohle_zufluss6, sohle_zufluss7, sohle_zufluss8,
                    kanalart, profilart_v, material_v,
                    e_gebiet, strassennummer,
                    schachtnummer, schachtart, berichtsnummer,
                    laenge, schachtmaterial, oberflaeche,
                    baujahr, wasserschutz, eigentum,
                    naechste_halt, rueckadresse, strakatid
                )
                VALUES (
                    :nummer, 
                    :rw_gerinne_o, :hw_gerinne_o, :rw_gerinne_u, :hw_gerinne_u,
                    :rw_rohranfang, :hw_rohranfang, :rw_rohrende, :hw_rohrende,
                    :zuflussnummer1, :zuflussnummer2, :zuflussnummer3, :zuflussnummer4,
                    :zuflussnummer5, :zuflussnummer6, :zuflussnummer7, :zuflussnummer8,
                    :abflussnummer1, :abflussnummer2, :abflussnummer3, :abflussnummer4, :abflussnummer5,
                    :schacht_oben, :schacht_unten, :haltungsname,
                    :rohrbreite_v, :rohrhoehe___v, :flaechenfactor_v,
                    :deckel_oben_v, :deckel_unten_v, :sohle_oben___v, :sohle_unten__v, :s_sohle_oben_v,
                    :sohle_zufluss1, :sohle_zufluss2, :sohle_zufluss3, :sohle_zufluss4,
                    :sohle_zufluss5, :sohle_zufluss6, :sohle_zufluss7, :sohle_zufluss8,
                    :kanalart, :profilart_v, :material_v,
                    :e_gebiet, :strassennummer,
                    :schachtnummer, :schachtart, :berichtsnummer,
                    :laenge, :schachtmaterial, :oberflaeche,
                    :baujahr, :wasserschutz, :eigentum,
                    :naechste_halt, :rueckadresse, :strakatid                
                )"""

                if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
                    logger.error('Fehler beim Lesen der Datei "kanal.rwtopen"')
                    return False
            else:
                logger.error('Programmfehler: Einlesen der Datei "kanal.rwtopen wurde nicht '
                             'ordnungsgemäß abgeschlossen!"')
                return False

        self.db_qkan.commit()

        self.progress_bar.setValue(20)

        return True

    def _strakat_reftables(self) -> bool:
        """Import der STRAKAT-Referenztabellen aus der STRAKAT-Datei 'referenztabelle.strakat'
        """

        # Erstellung Tabelle t_reflists
        sql = "PRAGMA table_list('t_reflists')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_reflists', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_reflists (
                pk INTEGER PRIMARY KEY,
                id INTEGER,                 -- Schlüssel je Tabellenart
                tabtyp TEXT,                -- Tabellenart
                n1 INTEGER,                 -- Inhalt abhängig von von tabtyp 
                n2 INTEGER,                 -- Inhalt abhängig von von tabtyp
                n3 INTEGER,                 -- Inhalt abhängig von von tabtyp
                n4 INTEGER,                 -- Inhalt abhängig von von tabtyp
                n5 INTEGER,                 -- Inhalt abhängig von von tabtyp
                kurz TEXT, 
                text TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_reflists"'):
                return False

        t_typen = {
            1: 'kanalart',
            2: 'rohrmaterial',
            3: 'profilart',
            4: 'entwaesserungsgebiet',
            5: 'schachtart',
            6: 'auflagerart',
            7: 'wasserhaltung',
            8: 'verbau',
            9: 'absturzart',
            10: 'deckelart',
            11: 'erschwernis',
            12: 'oberflaeche',
            13: 'eigentum',
            14: 'wasserschutzzone',
            15: 'massnahme',
            16: 'genauigkeit',
            17: 'sanierungsmassnahme',
            19: 'herkunkft',
            20: 'hausanschlussart',
            21: 'schachtmaterial',
            27: 'strasse',
        }

        # Datei referenztabelle.strakat einlesen und in Tabelle schreiben
        blength = 128                       # Blocklänge in der STRAKAT-Datei
        with open(os.path.join(self.strakatdir, 'system', 'referenztabelle.strakat'), 'rb') as fo:
            idvor = -1                          # Erkennung eines neuen Tabellentyps
            for n in range(1, 1000000):
                """Einlesen der Blöcke. Begrenzung nur zur Sicherheit"""
                b = fo.read(blength)

                if b:
                    (
                        n0, n1, n2, n3, n4, n5
                    ) = unpack('HHHHBB', b[0:10])
                else:
                    break

                # Prüfen, ob: 1. Wechsel zu anderer List, 2. Listenende
                nextlist = False
                if n0 != idvor:
                    endelist = False
                    nextlist = True
                    idvor = n0
                elif endelist:
                    continue
                if b[10:128] == b'\x00' * 118:
                    endelist = True
                    continue

                tabtyp = t_typen.get(n0, None)
                if not tabtyp:
                    # Tabellentyp unbekannt
                    continue

                id = n1

                kurz = b[10:b[10:26].find(b'\x00')+10].decode('ansi')
                text = b[26:b[26:128].find(b'\x00')+26].decode('ansi')

                params = {'tabtyp': tabtyp, 'id': id,
                          'n1': n1, 'n2': n2, 'n3': n3, 'n4': n4, 'n5': n5,
                          'kurz': kurz, 'text': text}

                sql = """INSERT INTO t_reflists (
                    tabtyp, id,
                    n1, n2, n3, n4, n5, 
                    kurz, text                    
                )
                VALUES (
                    :tabtyp, :id, :n1, :n2, :n3, :n4, :n5, :kurz, :text
                )"""

                if not self.db_qkan.sql(sql, "strakat_import Referenztabellen", params):
                    logger.error('Fehler beim Lesen der Datei "system/referenztabelle.strakat"')
                    return False
            else:
                logger.error('Programmfehler: Einlesen der Datei "system/referenztabelle.strakat"'
                             ' wurde nicht ordnungsgemäß abgeschlossen!"')
                return False

        self.db_qkan.commit()

        self.progress_bar.setValue(40)

        return True

    def _strakat_hausanschl(self) -> bool:
        """Import der Hausanschlussdaten aus der STRAKAT-Datei 'haus.rwtopen', ACCESS-Tabelle 'HAUSANSCHLUSSTABELLE'
        """

        # Erstellung Tabelle t_strakathausanschluesse
        sql = "PRAGMA table_list('t_strakathausanschluesse')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_strakathausanschluesse', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_strakathausanschluesse (
                pk INTEGER PRIMARY KEY,
                nummer INTEGER,
                nextnum INTEGER,
                x1 REAL,
                x2 REAL,
                x3 REAL,
                x4 REAL,
                x5 REAL,
                x6 REAL,
                x7 REAL,
                x8 REAL,
                x9 REAL,
                y1 REAL,
                y2 REAL,
                y3 REAL,
                y4 REAL,
                y5 REAL,
                y6 REAL,
                y7 REAL,
                y8 REAL,
                y9 REAL,
                rohrbreite REAL,
                berichtnr INTEGER,
                anschlusshalnr INTEGER,
                anschlusshalname TEXT,
                haschob TEXT,
                haschun TEXT,
                urstation REAL,
                strakatid TEXT,
                hausanschlid TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakathausanschluesse"'):
                return False

        # Datei haus.rwtopen einlesen und in Tabelle schreiben
        blength = 640                      # Blocklänge in der STRAKAT-Datei
        with open(os.path.join(self.strakatdir, 'haus.rwtopen'), 'rb') as fo:
            _ = fo.read(blength)               # Kopfzeile ohne Bedeutung?
            for nummer in range(1, 1000000):
                """Einlesen der Blöcke. Begrenzung nur zur Sicherheit"""
                b = fo.read(blength)
                if not b or len(b) < blength:
                    break
                (x1, x2, x3, x4, x5, x6, x7, x8, x9) = unpack('ddddddddd', b[20:92])
                (y1, y2, y3, y4, y5, y6, y7, y8, y9) = unpack('ddddddddd', b[100:172])
                # d1, d2, d3, d4, d5, d6, d7, d8, d9 = unpack('fffffffff', b[220:256])

                rohrbreite = unpack('f', b[220:224])[0]  # nur erste von 9 Rohrbreiten lesen

                berichtnr = unpack('i', b[299:303])[0]
                anschlusshalnr = unpack('i', b[303:307])[0]
                nextnum = unpack('i', b[311:315])[0]

                haschob = unpack('20s', b[326:346])[0].replace(b'\x00', b' ').decode('ansi').strip()
                haschun = unpack('20s', b[362:382])[0].replace(b'\x00', b' ').decode('ansi').strip()

                urstation = unpack('f', b[515:519])[0]

                anschlusshalname = unpack('20s', b[611:631])[0].replace(b'\x00', b' ').decode('ansi').strip()

                (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                 ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[524:540])]
                strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'
                (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                 ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[540:556])]
                hausanschlid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                params = {
                    'nummer': nummer, 'nextnum': nextnum,
                    'x1': x1, 'x2': x2, 'x3': x3,
                    'x4': x4, 'x5': x5, 'x6': x6,
                    'x7': x7, 'x8': x8, 'x9': x9,
                    'y1': y1, 'y2': y2, 'y3': y3,
                    'y4': y4, 'y5': y5, 'y6': y6,
                    'y7': y7, 'y8': y8, 'y9': y9,
                    'rohrbreite': rohrbreite,
                    'berichtnr': berichtnr,
                    'anschlusshalnr': anschlusshalnr, 'anschlusshalname': anschlusshalname,
                    'haschob': haschob, 'haschun': haschun, 'urstation': urstation,
                    'strakatid': strakatid, 'hausanschlid': hausanschlid,
                }

                sql = """INSERT INTO t_strakathausanschluesse (
                    nummer, nextnum,
                    x1, x2, x3,
                    x4, x5, x6,
                    x7, x8, x9,
                    y1, y2, y3,
                    y4, y5, y6,
                    y7, y8, y9,
                    rohrbreite,
                    berichtnr,
                    anschlusshalnr, anschlusshalname,
                    haschob, haschun, urstation,
                    strakatid, hausanschlid
                )
                VALUES (
                    :nummer, :nextnum,
                    :x1, :x2, :x3,
                    :x4, :x5, :x6,
                    :x7, :x8, :x9,
                    :y1, :y2, :y3,
                    :y4, :y5, :y6,
                    :y7, :y8, :y9,
                    :rohrbreite,
                    :berichtnr,
                    :anschlusshalnr, :anschlusshalname,
                    :haschob, :haschun, :urstation,
                    :strakatid, :hausanschlid
                )"""

                if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
                    logger.error('Fehler beim Lesen der Datei "haus.rwtopen"')
                    return False
            else:
                logger.error('Programmfehler: Einlesen der Datei "kanal.rwtopen wurde nicht '
                             'ordnungsgemäß abgeschlossen!"')
                return False

        self.db_qkan.commit()

        self.progress_bar.setValue(60)

        return True

    def _strakat_berichte(self) -> bool:
        """Import der Schadensdaten aus der STRAKAT-Datei 'ENBericht.rwtopen', ACCESS-Tabelle 'SCHADENSTABELLE'
        """

        sql = """
        """

        params = {}
        if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
            return False

        self.db_qkan.commit()

        return True

    def _reftables(self) -> bool:
        """Referenztabellen mit Datensätzen für HE-Import füllen"""

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert
        daten = [
            ('Regenwasser', 'R', 'Regenwasser', 1, 2, 'R', 'KR', 0, 0),
            ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1, 'S', 'KS', 0, 0),
            ('Mischwasser', 'M', 'Mischwasser', 0, 0, 'M', 'KM', 0, 0),
            ('RW Druckleitung', 'RD', 'Transporthaltung ohne Anschlüsse', 1, 2, None, 'DR', 1, 1),
            ('SW Druckleitung', 'SD', 'Transporthaltung ohne Anschlüsse', 2, 1, None, 'DS', 1, 1),
            ('MW Druckleitung', 'MD', 'Transporthaltung ohne Anschlüsse', 0, 0, None, 'DW', 1, 1),
            ('RW nicht angeschlossen', 'RT', 'Transporthaltung ohne Anschlüsse', 1, 2, None, None, 1, 0),
            ('MW nicht angeschlossen', 'MT', 'Transporthaltung ohne Anschlüsse', 0, 0, None, None, 1, 0),
            ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, None, None, 0, None),
            ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None, 0, None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m145, isybau, transport, druckdicht)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste entwaesserungsarten", daten, many=True):
            return False

        daten = [
            ('Haltung', None),
            ('Drossel', 'HYSTEM-EXTRAN 8'),
            ('H-Regler', 'HYSTEM-EXTRAN 8'),
            ('Q-Regler', 'HYSTEM-EXTRAN 8'),
            ('Schieber', 'HYSTEM-EXTRAN 8'),
            ('GrundSeitenauslass', 'HYSTEM-EXTRAN 8'),
            ('Pumpe', None),
            ('Wehr', None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO haltungstypen (bezeichnung, bemerkung)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM haltungstypen)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste haltungstypen", daten, many=True):
            return False

        daten = [
            ('Kreis', 1, 1, None),
            ('Rechteck (geschlossen)', 2, 3, None),
            ('Ei (B:H = 2:3)', 3, 5, None),
            ('Maul (B:H = 2:1,66)', 4, 4, None),
            ('Halbschale (offen) (B:H = 2:1)', 5, None, None),
            ('Kreis gestreckt (B:H=2:2.5)', 6, None, None),
            ('Kreis überhöht (B:H=2:3)', 7, None, None),
            ('Ei überhöht (B:H=2:3.5)', 8, None, None),
            ('Ei breit (B:H=2:2.5)', 9, None, None),
            ('Ei gedrückt (B:H=2:2)', 10, None, None),
            ('Drachen (B:H=2:2)', 11, None, None),
            ('Maul (DIN) (B:H=2:1.5)', 12, None, None),
            ('Maul überhöht (B:H=2:2)', 13, None, None),
            ('Maul gedrückt (B:H=2:1.25)', 14, None, None),
            ('Maul gestreckt (B:H=2:1.75)', 15, None, None),
            ('Maul gestaucht (B:H=2:1)', 16, None, None),
            ('Haube (B:H=2:2.5)', 17, None, None),
            ('Parabel (B:H=2:2)', 18, None, None),
            ('Rechteck mit geneigter Sohle (B:H=2:1)', 19, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:1)', 20, None, None),
            ('Rechteck mit geneigter Sohle (B:H=1:2)', 21, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.2B)', 22, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.2B)', 23, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.2B)', 24, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=2:1,b=0.4B)', 25, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:1,b=0.4B)', 26, None, None),
            ('Rechteck mit geneigter und horizontaler Sohle (B:H=1:2,b=0.4B)', 27, None, None),
            ('Druckrohrleitung', 50, None, None),
            ('Sonderprofil', 68, 2, None),
            ('Gerinne', 69, None, None),
            ('Trapez (offen)', 900, None, None),
            ('Doppeltrapez (offen)', 901, None, None),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO profile (profilnam, he_nr, mu_nr, kp_key)
                    SELECT ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT profilnam FROM profile)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste profile", daten, many=True):
            return False

        daten = [
             ('Offline', 1),
             ('Online Schaltstufen', 2),
             ('Online Kennlinie', 3),
             ('Online Wasserstandsdifferenz', 4),
             ('Ideal', 5),
        ]

        daten = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO pumpentypen (bezeichnung, he_nr)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM pumpentypen)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste pumpentypen", daten, many=True):
            return False

        # Wegen der sehr eigenwilligen Logik in STRAKAT enthält die Tabelle 'schachtarten'
        # Zuordnungen sowohl zu Schächten als auch Haltungen

        # Erstellung Tabelle t_schachtarten2schachttypen
        sql = "PRAGMA table_list('t_schachtarten2schachttypen')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_schachtarten2schachttypen', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_schachtarten2schachttypen (
                id INTEGER PRIMARY KEY,
                schachttyp TEXT,
                simstatus TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_schachtarten2schachttypen"'):
                return False

        # Liste enthält nur Schachtarten, die nicht 'Schacht' und 'vorhanden' sind (einschließlich 1: 'NS Normalschacht')
        daten = [
            (2,  'Auslass', 'vorhanden'),
            (5,  'Schacht', 'fiktiv'),
            (10, 'Speicher', 'vorhanden'),
            (19, 'Speicher', 'vorhanden'),
            (20, 'Speicher', 'vorhanden'),
            (23, 'Speicher', 'vorhanden'),
            (24, 'Schacht', 'fiktiv'),
            (27, 'Schacht', 'geplant'),
            (31, 'Schacht', 'fiktiv'),
        ]
        sql = """INSERT INTO t_schachtarten2schachttypen (id, schachttyp, simstatus)
                    VALUES (?, ?, ?)"""

        if not self.db_qkan.sql(sql,
                                "strakat_import Referenzliste t_schachtarten2schachttypen",
                                daten,
                                many=True):
            return False

        # Erstellung Tabelle t_schachtarten2haltungstypen
        sql = "PRAGMA table_list('t_schachtarten2haltungstypen')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_schachtarten2haltungstypen', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_schachtarten2haltungstypen (
                id INTEGER PRIMARY KEY,
                haltungstyp TEXT,
                simstatus TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_schachtarten2haltungstypen"'):
                return False

        # Liste enthält nur Haltungsarten, die nicht 'Haltung' und 'vorhanden' sind
        daten = [
            (5,  'Haltung', 'fiktiv'),
            (15, 'Schieber', 'vorhanden'),
            (18, 'Pumpe', 'vorhanden'),
            (21, 'Pumpe', 'vorhanden'),
            (24, 'Haltung', 'fiktiv'),
            (27, 'Haltung', 'geplant'),
            (31, 'Haltung', 'fiktiv'),
        ]
        sql = """INSERT INTO t_schachtarten2haltungstypen (id, haltungstyp, simstatus)
                    VALUES (?, ?, ?)"""

        if not self.db_qkan.sql(sql,
                                "strakat_import Referenzliste t_schachtarten2haltungstypen",
                                daten,
                                many=True):
            return False

        # Erstellung Tabelle t_kanalarten2entwart
        sql = "PRAGMA table_list('t_kanalarten2entwart')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_kanalarten2entwart', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_kanalarten2entwart (
                id INTEGER PRIMARY KEY,
                entwart TEXT,
                druckdicht INTEGER
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_kanalarten2entwart"'):
                return False

        # Liste enthält nur Haltungsarten, die nicht 'Haltung' sind
        daten = [
            (1, 'Regenwasser', False),
            (2, 'Schmutzwasser', False),
            (3, 'Mischwasser', False),
            (4, 'RW Druckleitung', True),
            (5, 'SW Druckleitung', True),
            (6, 'MW Druckleitung', True),
            (16, 'Rinnen/Gräben', False),
            (9, 'stillgelegt', False),
        ]
        sql = """INSERT INTO t_kanalarten2entwart (id, entwart, druckdicht)
                    VALUES (?, ?, ?)"""

        if not self.db_qkan.sql(sql,
                                "strakat_import Referenzliste t_kanalarten2entwart",
                                daten,
                                many=True):
            return False

        self.db_qkan.commit()

        self.progress_bar.setValue(70)

        return True

        # Liste der Kanalarten entspricht im Wesentlichen der QKan-Tabelle 'Entwässerungsarten'

    def _schaechte(self) -> bool:
        """Import der STRAKAT-Tabelle KANALTABELLE"""

        sql = """WITH
            t_strakatkanal_oberhalb AS (
                SELECT nummer, abflussnummer1
                FROM t_strakatkanal
                WHERE schachtnummer <> 0
            ),
            strassen AS (
                SELECT n1 AS id, kurz, text AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            schachtmaterial AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'schachtmaterial'
            )
            
            INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, strasse, material, 
                                durchm, 
                                druckdicht, 
                                entwart, schachttyp, simstatus, 
                                kommentar, geop, geom)
            
            
            SELECT
                CASE WHEN Trim(t_strakatkanal.schacht_oben) = ''
                THEN printf('strakatnr_%1', t_strakatkanal.nummer)
                ELSE Trim(t_strakatkanal.schacht_oben)
                END                                         AS schnam,
                t_strakatkanal.rw_gerinne_o                 AS xsch,
                t_strakatkanal.hw_gerinne_o                 AS ysch,
                MIN(CASE WHEN t_strakatkanal.s_sohle_oben_v<1 Or t_strakatkanal.s_sohle_oben_v > 5000
                    THEN t_strakatkanal.sohle_oben___v
                    ELSE t_strakatkanal.s_sohle_oben_v
                    END
                )                                           AS sohlhoehe,
                MAX(CASE WHEN t_strakatkanal.deckel_oben_v <1 Or t_strakatkanal.deckel_oben_v > 5000
                    THEN Null 
                    ELSE t_strakatkanal.deckel_oben_v
                    END
                )                                           AS deckelhoehe,
                CASE WHEN INSTR(strassen.name,' ') > 0
                    THEN substr(strassen.name, INSTR(strassen.name,' ')+1)
                    ELSE strassen.name
                END                                         AS strasse,
                schachtmaterial.text                        AS material,
                1.0                                         AS durchm,
                k2e.druckdicht                              AS druckdicht, 
                k2e.entwart                                 AS entwart,
                Coalesce(s2s.schachttyp ,'Schacht')         AS schachttyp,
                Coalesce(s2s.simstatus, 'vorhanden')        AS simstatus,
                'QKan-STRAKAT-Import'                       AS kommentar,
                Makepoint(t_strakatkanal.rw_gerinne_o, t_strakatkanal.hw_gerinne_o, :epsg)  AS geop,
                CastToMultiPolygon(MakePolygon(MakeCircle(
                    t_strakatkanal.rw_gerinne_o, t_strakatkanal.hw_gerinne_o, 1.0, :epsg))) AS geom
            FROM
                t_strakatkanal
                LEFT JOIN t_strakatkanal_oberhalb               
                ON t_strakatkanal.nummer = t_strakatkanal_oberhalb.abflussnummer1
                LEFT JOIN strassen                              
                ON t_strakatkanal.strassennummer = strassen.id
                LEFT JOIN schachtmaterial                       
                ON t_strakatkanal.schachtmaterial = schachtmaterial.id
                LEFT JOIN t_schachtarten2schachttypen AS s2s    
                ON t_strakatkanal.schachtart = s2s.id
                LEFT JOIN t_kanalarten2entwart AS k2e           
                ON t_strakatkanal.kanalart = k2e.id
            WHERE
                t_strakatkanal.schachtnummer <> 0
                AND (
                    t_strakatkanal_oberhalb.abflussnummer1 Is Not Null AND 
                    t_strakatkanal.zuflussnummer1 = t_strakatkanal_oberhalb.nummer
                    OR
                    t_strakatkanal_oberhalb.abflussnummer1 Is Null AND
                    t_strakatkanal.zuflussnummer1 = 0
                )
            GROUP BY
                schnam, xsch, ysch,
                strasse, material, schachttyp
            HAVING
                schnam Is Not Null
                AND xsch Is Not Null
                AND ysch Is Not Null
            ORDER BY
                schnam"""

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
            logger.error('Fehler in strakat_import Schächte')
            return False

        self.db_qkan.commit()

        self.progress_bar.setValue(80)

        return True

    def _haltungen(self) -> bool:
        """Import der STRAKAT-Tabelle KANALTABELLE"""

        sql = """
            WITH
            t_strakatkanal_oberhalb AS (
                SELECT nummer, schacht_unten
                FROM t_strakatkanal
                WHERE schachtnummer <> 0
            ),
            profilarten AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'profilart'
            ),
            rohrmaterialien AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'rohrmaterial'
            ),
            strassen AS (
                SELECT n1 AS id, kurz, text AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            )
            INSERT INTO haltungen (haltnam, schoben, schunten, laenge, 
                xschob, yschob, xschun, yschun, 
                breite, hoehe, 
                sohleoben, sohleunten, 
                profilnam, entwart, material, strasse, 
                haltungstyp, simstatus, kommentar, geom)
            SELECT
                Trim(t_strakatkanal.haltungsname)       AS haltnam,
                Trim(Coalesce(
                    t_strakatkanal_oberhalb.schacht_unten,t_strakatkanal.schacht_oben
                    ))                                  AS schoben,
                Trim(t_strakatkanal.schacht_unten)      AS schunten,
                t_strakatkanal.laenge                   AS laenge,
                t_strakatkanal.rw_gerinne_o             AS xschob,
                t_strakatkanal.hw_gerinne_o             AS yschob,
                t_strakatkanal.rw_gerinne_u             AS xschun,
                t_strakatkanal.hw_gerinne_u             AS yschun,
                t_strakatkanal.rohrbreite_v/1000.       AS breite,
                t_strakatkanal.rohrhoehe___v/1000.      AS hoehe,
                t_strakatkanal.sohle_oben___v           AS sohleoben,
                t_strakatkanal.sohle_unten__v           AS sohleunten,
                profilarten.text                        AS profilnam,
                k2e.entwart                             AS entwart,
                rohrmaterialien.text                    AS material,
                CASE WHEN INSTR(strassen.name,' ') > 0
                    THEN substr(strassen.name, INSTR(strassen.name,' ')+1)
                    ELSE strassen.name
                END                                     AS strasse,
                Coalesce(s2h.haltungstyp ,'Haltung')    AS haltungstyp,
                Coalesce(s2h.simstatus, 'vorhanden')    AS simstatus,
                'QKan-STRAKAT-Import'                   AS kommentar,
                MakeLine(MakePoint(t_strakatkanal.rw_gerinne_o,
                                   t_strakatkanal.hw_gerinne_o, :epsg),
                         MakePoint(t_strakatkanal.rw_gerinne_u,
                                   t_strakatkanal.hw_gerinne_u, :epsg)) AS geom
            FROM
                t_strakatkanal
                LEFT JOIN profilarten
                ON t_strakatkanal.profilart_v = profilarten.id
                LEFT JOIN rohrmaterialien
                ON t_strakatkanal.Material_v = rohrmaterialien.ID
                LEFT JOIN Strassen
                ON t_strakatkanal.strassennummer = Strassen.ID
                LEFT JOIN t_schachtarten2haltungstypen AS s2h
                ON t_strakatkanal.schachtart = s2h.id
                LEFT JOIN t_kanalarten2entwart AS k2e
                ON t_strakatkanal.kanalart = k2e.id
                LEFT JOIN t_strakatkanal_oberhalb
                ON t_strakatkanal.Zuflussnummer1 = t_strakatkanal_oberhalb.Nummer
            WHERE t_strakatkanal.laenge > 0.04 AND
                   t_strakatkanal.schachtnummer <> 0"""

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import Haltungen", params):
            logger.error('Fehler in strakat_import Haltungen')
            return False

        self.db_qkan.commit()

        self.progress_bar.setValue(90)

        return True

    def _anschlussleitungen(self) -> bool:
        """Import der STRAKAT-Tabelle anschlussleitungen"""

        sql = """
            WITH lo AS (
                SELECT
                    h.pk, 
                    0 AS n, 
                MakePoint(k.[rw_gerinne_u]+(k.[rw_gerinne_o]-k.[rw_gerinne_u])*h.urstation/
                    sqrt(pow(k.[rw_gerinne_o]-k.[rw_gerinne_u],2)+pow(k.[hw_gerinne_o]-k.[hw_gerinne_u],2)),
                          k.[hw_gerinne_u]+(k.[hw_gerinne_o]-k.[hw_gerinne_u])*h.urstation/
                    sqrt(pow(k.[rw_gerinne_o]-k.[rw_gerinne_u],2)+pow(k.[hw_gerinne_o]-k.[hw_gerinne_u],2)),
                    :epsg) AS p
                FROM t_strakathausanschluesse AS h
                JOIN t_strakatkanal AS k ON k.nummer = h.anschlusshalnr
                UNION
                SELECT pk, 1 AS n, Makepoint(x1, y1, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x1 > 1
                UNION 
                SELECT pk, 2 AS n, Makepoint(x2, y2, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x2 > 1
                UNION 
                SELECT pk, 3 AS n, Makepoint(x3, y3, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x3 > 1
                UNION 
                SELECT pk, 4 AS n, Makepoint(x4, y4, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x4 > 1
                UNION 
                SELECT pk, 5 AS n, Makepoint(x5, y5, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x5 > 1
                UNION 
                SELECT pk, 6 AS n, Makepoint(x6, y6, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x6 > 1
                UNION 
                SELECT pk, 7 AS n, Makepoint(x7, y7, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x7 > 1
                UNION 
                SELECT pk, 8 AS n, Makepoint(x8, y8, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x8 > 1
                UNION 
                SELECT pk, 9 AS n, Makepoint(x9, y9, :epsg) AS p
                FROM t_strakathausanschluesse
                WHERE x9 > 1
            ),
            lp AS (
            SELECT pk, p
            FROM lo
            ORDER BY n
            )
            INSERT INTO anschlussleitungen (leitnam, schoben, schunten, 
                hoehe, breite, 
                simstatus, kommentar, geom)
            SELECT
                CASE WHEN Trim(ha.anschlusshalname) = ''
                THEN replace(printf('ha_%d', 1000000 + ha.nummer), 'ha_1', 'ha')
                ELSE Trim(ha.anschlusshalname)
                END                         AS leitnam,
                Trim(ha.haschob)            AS schoben,
                Trim(ha.haschun)            AS schunten,
                ha.rohrbreite/1000.         AS hoehe,
                ha.rohrbreite/1000.         AS breite,
                'vorhanden'                 AS simstatus,
                'QKan-STRAKAT-Import'       AS kommentar,
                MakeLine(lp.p)          AS geom
            FROM
                t_strakathausanschluesse AS ha
                JOIN lp USING (pk)
			GROUP BY pk"""

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import anschlussleitungen", params):
            return False

        self.db_qkan.commit()

        self.progress_bar.setValue(98)

        return True

    def _schachtschaeden(self) -> bool:
        """Import der STRAKAT-Tabelle KANALTABELLE"""

        sql = """
        """

        params = {}
        if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
            return False

        self.db_qkan.commit()

        return True

    def _haltungsschaeden(self) -> bool:
        """Import der STRAKAT-Tabelle KANALTABELLE"""

        sql = """
        """

        params = {}
        if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
            return False

        self.db_qkan.commit()

        return True

