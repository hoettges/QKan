import os
import re
from struct import unpack
from typing import Iterator

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis, QgsGeometry, QgsPoint
from qkan import QKan
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

logger = get_logger("QKan.strakat.import")


class Bericht_STRAKAT(ClassObject):
    nummer: int = 0
    datum: str = ""
    untersucher: str = ""
    ag_kontrolle: str = ""
    fahrzeug: str = ""
    inspekteur: str = ""
    wetter: str = ""
    bewertungsart: str = ""
    atv149: float = 0.0
    fortsetzung: int = 0
    station_gegen: float = 0.0
    station_untersucher: float = 0.0
    atv_kuerzel: str = ""
    atv_langtext: str = ""
    charakt1: str = ""
    charakt2: str = ""
    quantnr1: int = 0
    quantnr2: int = 0
    streckenschaden: str = ""
    pos_von: int = 0
    pos_bis: int = 0
    sandatum: str = ""
    geloescht: int = 0
    schadensklasse: int = 0
    untersuchungsrichtung: int = 0
    bandnr: str = ""
    videozaehler: int = 0
    foto_dateiname: str = ""
    film_dateiname: str = ""
    sanierung: str = ""
    atv143: float = 0.0
    skdichtheit: int = 0
    skbetriebssicherheit: int = 0
    skstandsicherheit: int = 0
    kommentar: str = ""
    strakatid: str = ""
    hausanschlid: str = ""
    berichtid: str = ""


class Kanal_STRAKAT(ClassObject):
    nummer: int = 0
    rw_gerinne_o: float = 0.0
    hw_gerinne_o: float = 0.0
    rw_gerinne_u: float = 0.0
    hw_gerinne_u: float = 0.0
    rw_rohranfang: float = 0.0
    hw_rohranfang: float = 0.0
    rw_rohrende: float = 0.0
    hw_rohrende: float = 0.0
    zuflussnummer1: int = 0
    zuflussnummer2: int = 0
    zuflussnummer3: int = 0
    zuflussnummer4: int = 0
    zuflussnummer5: int = 0
    zuflussnummer6: int = 0
    zuflussnummer7: int = 0
    zuflussnummer8: int = 0
    abflussnummer1: int = 0
    abflussnummer2: int = 0
    abflussnummer3: int = 0
    abflussnummer4: int = 0
    abflussnummer5: int = 0
    schacht_oben: str = ""
    schacht_unten: str = ""
    haltungsname: str = ""
    rohrbreite_v: float = 0.0
    rohrhoehe___v: float = 0.0
    flaechenfactor_v: float = 0.0
    deckel_oben_v: float = 0.0
    deckel_unten_v: float = 0.0
    sohle_oben___v: float = 0.0
    sohle_unten__v: float = 0.0
    s_sohle_oben_v: float = 0.0
    sohle_zufluss1: float = 0.0
    sohle_zufluss2: float = 0.0
    sohle_zufluss3: float = 0.0
    sohle_zufluss4: float = 0.0
    sohle_zufluss5: float = 0.0
    sohle_zufluss6: float = 0.0
    sohle_zufluss7: float = 0.0
    sohle_zufluss8: float = 0.0
    kanalart: int = 0
    profilart_v: int = 0
    material_v: int = 0
    e_gebiet: int = 0
    strassennummer: int = 0
    schachtnummer: int = 0
    schachtart: int = 0
    berichtsnummer: int = 0
    laenge: float = 0.0
    schachtmaterial: int = 0
    oberflaeche: int = 0
    baujahr: int = 0
    wasserschutz: int = 0
    eigentum: int = 0
    naechste_halt: int = 0
    rueckadresse: int = 0
    strakatid: str = ""


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
        self.richtung = QKan.config.xml.richt_choice
        self.kriterienschaeden = QKan.config.zustand.kriterienschaeden
        self.maxdiff = QKan.config.strakat.maxdiff


    def run(self) -> bool:

        self.iface = QKan.instance.iface

        self.ordner_bild = QKan.config.xml.ordner_bild
        self.ordner_video = QKan.config.xml.ordner_video

        # Create progress bar
        self.progress_bar = QProgressBar(self.iface.messageBar())
        self.progress_bar.setRange(0, 100)

        self.status_message = self.iface.messageBar().createMessage(
            "", "Import aus STRAKAT läuft. Bitte warten..."
        )
        self.status_message.layout().addWidget(self.progress_bar)
        self.iface.messageBar().pushWidget(self.status_message, Qgis.Info, 60)
        self.progress_bar.setValue(0)
        logger.debug("progress_bar initialisiert")

        result = all(
            [
                self._strakat_kanaltabelle(), self.progress_bar.setValue(5),           logger.debug("_strakat_kanaltabelle"),
                self._strakat_reftables(), self.progress_bar.setValue(10),              logger.debug("_strakat_reftables"),
                self._reftables(), self.progress_bar.setValue(15),                      logger.debug("_reftables"),
                self._schaechte(), self.progress_bar.setValue(20),                      logger.debug("_schaechte"),
                self._haltungen(), self.progress_bar.setValue(25),                      logger.debug("_haltungen"),
                self._adapt_refvals(),                                                  logger.debug("_adapt_refvals"),
                self._strakat_hausanschl(), self.progress_bar.setValue(30),             logger.debug("_strakat_hausanschl"),
                self._anschlussleitungen(), self.progress_bar.setValue(35),             logger.debug("_anschlussleitungen"),
                self._strakat_berichte(), self.progress_bar.setValue(40),               logger.debug("_strakat_berichte"),
                self._schaechte_untersucht(), self.progress_bar.setValue(45),           logger.debug("_schaechte_untersucht"),
                self._untersuchdat_schacht(), self.progress_bar.setValue(50),           logger.debug("_untersuchdat_schacht"),
                self._haltungen_untersucht(), self.progress_bar.setValue(60),           logger.debug("_haltungen_untersucht"),
                self._untersuchdat_haltung(), self.progress_bar.setValue(70),           logger.debug("_untersuchdat_haltung"),
                self._anschlussleitungen_untersucht(), self.progress_bar.setValue(80),  logger.debug("_anschlussleitungen_untersucht"),
                self._untersuchdat_anschlussleitung(), self.progress_bar.setValue(90),  logger.debug("_untersuchdat_anschlussleitung"),
            ]
        )

        self.progress_bar.setValue(100)
        self.status_message.setText("Fertig! STRAKAT-Import abgeschlossen.")

        self.iface.messageBar().clearWidgets()

        return result

    def _strakat_kanaltabelle(self) -> bool:
        """Import der Kanaldaten aus der STRAKAT-Datei 'kanal.rwtopen', entspricht ACCESS-Tabelle 'KANALTABELLE'
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
                mark INTEGER DEFAULT 0,
                strakatid TEXT
            )"""
            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakatkanal"'):
                return False

            # Kopie von t_strakatkanal, um inkonsistente Schachtbezeichnungen nachvollziehbar zu machen
            if not self.db_qkan.sql(sql.replace('t_strakatkanal', 't_strakatk_ori'), 'Erstellung Tabelle "t_strakatk_ori"'):
                return False

            sqls = [
                f"SELECT AddGeometryColumn('t_strakatkanal', 'geom', {self.epsg}, 'LINESTRING')",
                "SELECT CreateSpatialIndex('t_strakatkanal', 'geom')",
                f"SELECT AddGeometryColumn('t_strakatkanal', 'geop', {self.epsg}, 'POINT')",
                "SELECT CreateSpatialIndex('t_strakatkanal', 'geop')",
            ]
            for sql in sqls:
                if not self.db_qkan.sql(sql=sql,
                                        stmt_category="strakat_import ergänze geom und geop in t_strakatkanal"):
                    raise Exception(f'{self.__class__.__name__}: Fehler beim Ergänzen von geom und geop in t_strakatkanal')

            # Kopie von t_strakatkanal, um inkonsistente Schachtbezeichnungen nachvollziehbar zu machen
            for sql in sqls:
                if not self.db_qkan.sql(sql=sql.replace('t_strakatkanal', 't_strakatk_ori'),
                                        stmt_category="strakat_import ergänze geom und geop in t_strakatk_ori"):
                    raise Exception(f'{self.__class__.__name__}: Fehler beim Ergänzen von geom und geop in t_strakatk_ori')

            self.db_qkan.commit()

        def _iter() -> Iterator[Kanal_STRAKAT]:
        # Datei kanal.rwtopen einlesen und in Tabelle schreiben
            blength = 1024                      # Blocklänge in der STRAKAT-Datei
            with open(os.path.join(self.strakatdir, 'kanal.rwtopen'), 'rb') as fo:

                _ = fo.read(blength)                # Kopfzeile ohne Bedeutung?

                maxloop = 1000000                   # Begrenzung zur Sicherheit. Falls erreicht: Meldung
                for n in range(1, maxloop):
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

                    schacht_oben = b[172:b[172:187].find(b'\x00')+172].decode('ansi').strip()
                    haltungsname = b[187:b[187:202].find(b'\x00')+187].decode('ansi').strip()

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

                    s_sohle_oben_v = 0.0                        # Position in Datei kanal.rwtopen unbekannt

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

                    schacht_unten = b[965:b[965:980].find(b'\x00')+965].decode('ansi').strip()

                    yield Kanal_STRAKAT(
                        nummer=nummer,
                        rw_gerinne_o=rw_gerinne_o,
                        hw_gerinne_o=hw_gerinne_o,
                        rw_gerinne_u=rw_gerinne_u,
                        hw_gerinne_u=hw_gerinne_u,
                        rw_rohranfang=rw_rohranfang,
                        hw_rohranfang=hw_rohranfang,
                        rw_rohrende=rw_rohrende,
                        hw_rohrende=hw_rohrende,
                        zuflussnummer1=zuflussnummer1,
                        zuflussnummer2=zuflussnummer2,
                        zuflussnummer3=zuflussnummer3,
                        zuflussnummer4=zuflussnummer4,
                        zuflussnummer5=zuflussnummer5,
                        zuflussnummer6=zuflussnummer6,
                        zuflussnummer7=zuflussnummer7,
                        zuflussnummer8=zuflussnummer8,
                        abflussnummer1=abflussnummer1,
                        abflussnummer2=abflussnummer2,
                        abflussnummer3=abflussnummer3,
                        abflussnummer4=abflussnummer4,
                        abflussnummer5=abflussnummer5,
                        schacht_oben=schacht_oben,
                        schacht_unten=schacht_unten,
                        haltungsname=haltungsname,
                        rohrbreite_v=rohrbreite_v,
                        rohrhoehe___v=rohrhoehe___v,
                        flaechenfactor_v=flaechenfactor_v,
                        deckel_oben_v=deckel_oben_v,
                        deckel_unten_v=deckel_unten_v,
                        sohle_oben___v=sohle_oben___v,
                        sohle_unten__v=sohle_unten__v,
                        s_sohle_oben_v=s_sohle_oben_v,
                        sohle_zufluss1=sohle_zufluss1,
                        sohle_zufluss2=sohle_zufluss2,
                        sohle_zufluss3=sohle_zufluss3,
                        sohle_zufluss4=sohle_zufluss4,
                        sohle_zufluss5=sohle_zufluss5,
                        sohle_zufluss6=sohle_zufluss6,
                        sohle_zufluss7=sohle_zufluss7,
                        sohle_zufluss8=sohle_zufluss8,
                        kanalart=kanalart,
                        profilart_v=profilart_v,
                        material_v=material_v,
                        e_gebiet=e_gebiet,
                        strassennummer=strassennummer,
                        schachtnummer=schachtnummer,
                        schachtart=schachtart,
                        berichtsnummer=berichtsnummer,
                        laenge=laenge,
                        schachtmaterial=schachtmaterial,
                        oberflaeche=oberflaeche,
                        baujahr=baujahr,
                        wasserschutz=wasserschutz,
                        eigentum=eigentum,
                        naechste_halt=naechste_halt,
                        rueckadresse=rueckadresse,
                        strakatid=strakatid,
                    )
                else:
                    raise Exception(f'{self.__class__.__name__}:Programmfehler: Einlesen der Datei "kanal.rwtopen"'
                                    f' wurde nach 1000000 Datensätze abgebrochen!"')

        params = ()                           # STRAKAT data stored in tuple of dicts for better performance
                                            # with sql-statement executemany
        logger.debug("{__name__}: Berichte werden gelesen und in data gespeichert ...")

        for _schacht in _iter():
            data = {
                'nummer': _schacht.nummer,
                'rw_gerinne_o': _schacht.rw_gerinne_o, 'hw_gerinne_o': _schacht.hw_gerinne_o,
                'rw_gerinne_u': _schacht.rw_gerinne_u, 'hw_gerinne_u': _schacht.hw_gerinne_u,
                'rw_rohranfang': _schacht.rw_rohranfang, 'hw_rohranfang': _schacht.hw_rohranfang,
                'rw_rohrende': _schacht.rw_rohrende, 'hw_rohrende': _schacht.hw_rohrende,
                'zuflussnummer1': _schacht.zuflussnummer1, 'zuflussnummer2': _schacht.zuflussnummer2,
                'zuflussnummer3': _schacht.zuflussnummer3, 'zuflussnummer4': _schacht.zuflussnummer4,
                'zuflussnummer5': _schacht.zuflussnummer5, 'zuflussnummer6': _schacht.zuflussnummer6,
                'zuflussnummer7': _schacht.zuflussnummer7, 'zuflussnummer8': _schacht.zuflussnummer8,
                'abflussnummer1': _schacht.abflussnummer1, 'abflussnummer2': _schacht.abflussnummer2,
                'abflussnummer3': _schacht.abflussnummer3, 'abflussnummer4': _schacht.abflussnummer4,
                'abflussnummer5': _schacht.abflussnummer5,
                'schacht_oben': _schacht.schacht_oben, 'schacht_unten': _schacht.schacht_unten,
                'haltungsname': _schacht.haltungsname,
                'rohrbreite_v': _schacht.rohrbreite_v, 'rohrhoehe___v': _schacht.rohrhoehe___v,
                'flaechenfactor_v': _schacht.flaechenfactor_v,
                'deckel_oben_v': _schacht.deckel_oben_v, 'deckel_unten_v': _schacht.deckel_unten_v,
                'sohle_oben___v': _schacht.sohle_oben___v, 'sohle_unten__v': _schacht.sohle_unten__v,
                's_sohle_oben_v': 0.0,
                'sohle_zufluss1': _schacht.sohle_zufluss1, 'sohle_zufluss2': _schacht.sohle_zufluss2,
                'sohle_zufluss3': _schacht.sohle_zufluss3, 'sohle_zufluss4': _schacht.sohle_zufluss4,
                'sohle_zufluss5': _schacht.sohle_zufluss5, 'sohle_zufluss6': _schacht.sohle_zufluss6,
                'sohle_zufluss7': _schacht.sohle_zufluss7, 'sohle_zufluss8': _schacht.sohle_zufluss8,
                'kanalart': _schacht.kanalart, 'profilart_v': _schacht.profilart_v,
                'material_v': _schacht.material_v,
                'e_gebiet': _schacht.e_gebiet, 'strassennummer': _schacht.strassennummer,
                'schachtnummer': _schacht.schachtnummer, 'schachtart': _schacht.schachtart,
                'berichtsnummer': _schacht.berichtsnummer,
                'laenge': _schacht.laenge, 'schachtmaterial': _schacht.schachtmaterial,
                'oberflaeche': _schacht.oberflaeche,
                'baujahr': _schacht.baujahr, 'wasserschutz': _schacht.wasserschutz, 'eigentum': _schacht.eigentum,
                'naechste_halt': _schacht.naechste_halt, 'rueckadresse': _schacht.rueckadresse,
                'strakatid': _schacht.strakatid
            }
            params += (data,)

        logger.debug("{__name__}: Berichte werden in temporäre STRAKAT-Tabellen geschrieben ...")

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

        if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import STRAKAT Kanaltabelle", parameters=params, many=True):
            raise Exception(f'{self.__class__.__name__}:Fehler beim Lesen der Datei "kanal.rwtopen"')

        sqls = [
            f"""UPDATE t_strakatkanal
                SET geom = MakeLine(
                    Makepoint(iif(:coordsFromRohr, rw_rohranfang, rw_gerinne_o), 
                              iif(:coordsFromRohr, hw_rohranfang, hw_gerinne_o),
                              :epsg),
                    Makepoint(iif(:coordsFromRohr, rw_rohrende, rw_gerinne_u), 
                              iif(:coordsFromRohr, hw_rohrende, hw_gerinne_u),
                              :epsg)
                )
                WHERE iif(:coordsFromRohr, rw_rohranfang, rw_gerinne_o) > 1
                  AND iif(:coordsFromRohr, hw_rohranfang, hw_gerinne_o) > 1
                  AND iif(:coordsFromRohr, rw_rohrende, rw_gerinne_u) > 1
                  AND iif(:coordsFromRohr, hw_rohrende, hw_gerinne_u) > 1
            """,
            f"""UPDATE t_strakatkanal
                SET geop = Makepoint(rw_gerinne_o, hw_gerinne_o, :epsg)
                WHERE rw_gerinne_o > 1   AND hw_gerinne_o > 1
            """,
            "DELETE FROM t_strakatkanal WHERE schachtnummer = 0"
        ]

        params = {"epsg": self.epsg, "coordsFromRohr": False}   # für Netzlogik sind Gerinneschnittpunkte relevant
        for sql in sqls:
            if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Geoobjekte t_strakatkanal", parameters=params):
                raise Exception(f'{self.__class__.__name__}:Fehler beim Erzeugen der Geoobjekte t_strakatkanal')

        # Kopie von t_strakatkanal, um inkonsistente Schachtbezeichnungen nachvollziehbar zu machen
        sql = "INSERT INTO t_strakatk_ori SELECT * FROM t_strakatkanal"
        if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Kopie von t_strakatkanal"):
            raise Exception(f'{self.__class__.__name__}:Fehler bei strakat_import Kopie von t_strakatkanal')

        # Bereinigung inkonsistenter Schachtbezeichnungen

        # 1. Übertragen des schacht_oben auf Kanäle ohne schachtoben oder mit einem schachtoben,
        #    der nicht mit anderen Schachtoben übereinstimmt.
        sqls = [
            # 1.0 Fehlende Schacht- und Haltungsbezeichnungen ergänzen
            """ UPDATE t_strakatkanal SET schacht_oben = 'SN_' || substr(printf('0000%d', pk), -5)
                WHERE schacht_oben = '' OR schacht_oben = '0'""",
            """ UPDATE t_strakatkanal SET haltungsname = 'HN_' || substr(printf('0000%d', pk), -5)
                WHERE haltungsname = '' OR haltungsname = '0'""",
            # 1.1 Doppelte Haltungsbezeichnungen eindeutig machen. Erkennungsmerkmal zur späteren
            # Analyse: Diese Haltungsnamen beginnen
            # mit HA_ im Gegensatz zu den Haltungen ohne Namen, die mit HN_ beginnen
            """ UPDATE t_strakatkanal
                SET haltungsname = 'HA_' || substr(printf('0000%d', t_strakatkanal.pk), -5)
                FROM (SELECT pk, haltungsname FROM t_strakatkanal) AS std
                WHERE t_strakatkanal.haltungsname = std.haltungsname AND t_strakatkanal.pk > std.pk""",
            # 1.2.1 Schacht_unten auf Schacht_oben von Haltungen übertragen, auf die Abflussnummer (abflussnummer1 - abflussnummer5) verweist.
            """ WITH abflussnummern AS (
                    SELECT abflussnummer1 AS abflussnummer, schacht_unten AS schachtname
                    FROM t_strakatkanal
                    UNION
                    SELECT abflussnummer2 AS abflussnummer, schacht_unten AS schachtname
                    FROM t_strakatkanal
                    UNION
                    SELECT abflussnummer3 AS abflussnummer, schacht_unten AS schachtname
                    FROM t_strakatkanal
                    UNION
                    SELECT abflussnummer4 AS abflussnummer, schacht_unten AS schachtname
                    FROM t_strakatkanal
                    UNION
                    SELECT abflussnummer5 AS abflussnummer, schacht_unten AS schachtname
                    FROM t_strakatkanal
                ), schaechte_unten AS (
                    SELECT abflussnummer, schachtname
                    FROM abflussnummern
                    WHERE abflussnummer IS NOT NULL AND
                          abflussnummer <> 0 AND
                          schachtname <> '0' AND
                          schachtname <> ''
                    ORDER BY abflussnummer
                )
                UPDATE t_strakatkanal SET schacht_oben = schaechte_unten.schachtname
                FROM schaechte_unten
                WHERE t_strakatkanal.nummer = schaechte_unten.abflussnummer
            """,
            # Mehrfache "schacht_oben" mit SA_ im Gegensatz zu den Haltungen ohne Namen, die mit SN_ beginnen
            """ UPDATE t_strakatkanal
                SET schacht_oben = 'SA_' || substr(printf('0000%d', t_strakatkanal.pk), -5)
                FROM (SELECT pk, schacht_oben FROM t_strakatkanal) AS std
                WHERE t_strakatkanal.schacht_oben = std.schacht_oben AND t_strakatkanal.pk > std.pk""",
            # 1.2.2 Abzweigende Haltungen (k1k), deren schacht_oben nicht mit dem eines durchlaufenden
            #     Stranges (schacht_unten = schacht_oben: k2k) übereinstimmt.
            """WITH k2k AS (
                    SELECT ku.ROWID, ku.nummer, ku.geop, ku.schacht_oben, ku.schachtart, ku.kanalart
                    FROM t_strakatkanal ko
                    JOIN t_strakatkanal ku ON ko.abflussnummer1 = ku.nummer AND ko.schacht_unten = ku.schacht_oben
                ),
                k1k AS (
                    SELECT
                        k1.nummer AS n1, k2.nummer AS n2, k1.schacht_oben AS schoben_diff, 
                        k2.schacht_oben AS schoben, k1.schachtart, k1.kanalart
                    FROM k2k AS k2
                    JOIN t_strakatkanal AS k1 ON st_distance(k2.geop, k1.geop) < :maxdiff
                    WHERE
                        k2.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name='t_strakatkanal'
                            AND search_frame=makecircle(x(k1.geop),y(k1.geop), :maxdiff, :epsg))
                        AND k2.schacht_oben <> k1.schacht_oben
                )
                UPDATE t_strakatkanal SET schacht_oben = ksk.schoben
                FROM (SELECT n1, schoben FROM k1k) AS ksk
                WHERE ksk.n1 = t_strakatkanal.nummer AND ksk.schoben <> '' AND ksk.schoben <> '0'""",

            # 1.3 Unterschiedliche Schachtnamen an der gleichen Position
            """WITH k2k AS (
                    SELECT k2.nummer AS nummer, k1.schacht_oben AS schoben
                    FROM t_strakatkanal AS k2
                    JOIN t_strakatkanal AS k1 ON st_distance(k2.geop, k1.geop) < :maxdiff
                    WHERE
                        k2.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name='t_strakatkanal'
                            AND search_frame=makecircle(x(k1.geop),y(k1.geop), :maxdiff, :epsg))
                        AND k1.schacht_oben <> k2.schacht_oben AND k1.nummer < k2.nummer
                )
                UPDATE t_strakatkanal SET schacht_oben = ksk.schoben
                FROM (SELECT nummer, schoben FROM k2k) AS ksk
                WHERE ksk.nummer = t_strakatkanal.nummer AND ksk.schoben <> ''""",

            # 1.4 Test der Haltungen, die über "abflussnummmerx" und "zuflussnummerx" verbunden sind.
            """ WITH ka AS (
                    SELECT n1 AS id, n4, kurz, text
                    FROM t_reflists
                    WHERE tabtyp = 'schachtart' 
                ),
                sx AS (
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer1 = ku.nummer
                    WHERE ko.abflussnummer1 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer2 = ku.nummer
                    WHERE ko.abflussnummer2 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer3 = ku.nummer
                    WHERE ko.abflussnummer3 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer4 = ku.nummer
                    WHERE ko.abflussnummer4 > 0 AND ko.schacht_unten <> ku.schacht_oben
                    UNION 
                    SELECT ko.nummer AS nummer_oben, ku.nummer AS nummer_unten, ko.schacht_unten, ku.schacht_oben, ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un
                    FROM t_strakatkanal AS ko
                    JOIN t_strakatkanal AS ku ON ko.abflussnummer5 = ku.nummer
                    WHERE ko.abflussnummer5 > 0 AND ko.schacht_unten <> ku.schacht_oben
                )
                UPDATE t_strakatkanal SET schacht_unten = sx.schacht_oben
                FROM sx
                WHERE sx.nummer_oben = t_strakatkanal.nummer AND t_strakatkanal.schacht_unten <> sx.schacht_oben AND sx.schacht_oben <> ''""",
        ]

        params = {"epsg": self.epsg, "maxdiff": self.maxdiff}
        for sql in sqls:
            if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Korrektur Schachtnamen t_strakatkanal", parameters=params):
                raise Exception(f'{self.__class__.__name__}:Fehler bei der Korrektur der Schachtnamen t_strakatkanal')

        self.db_qkan.commit()

        return True

    def _strakat_reftables(self) -> bool:
        """Import der STRAKAT-Referenztabellen aus der STRAKAT-Datei 'referenztabelle.strakat'
        """

        # Erstellung Tabelle t_reflists. Diese Tabelle enthält die STRAKAT-Rohdaten aller Referenztabellen.
        # Diese werden in den einzelnen Importen mittels Filter auf die Spalte "tabtyp" spezifiziert und eingebunden.
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
            maxloop = 1000000                   # Begrenzung zur Sicherheit. Falls erreicht: Meldung
            for n in range(1, maxloop):
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
                    raise Exception(f'{self.__class__.__name__}:Fehler beim Lesen der Datei "system/referenztabelle.strakat"')
            else:
                raise Exception(f'{self.__class__.__name__}:Programmfehler: Einlesen der Datei '
                                f'"system/referenztabelle.strakat" wurde nicht ordnungsgemäß abgeschlossen!"')

        self.db_qkan.commit()

        return True

    def _strakat_hausanschl(self) -> bool:
        """Import der Hausanschlussdaten aus der STRAKAT-Datei 'haus.rwtopen', entspricht ACCESS-Tabelle 'HAUSANSCHLUSSTABELLE'
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
                geloescht INTEGER,
                strakatid TEXT,
                hausanschlid TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakathausanschluesse"'):
                return False

            sqls = [
                f"SELECT AddGeometryColumn('t_strakathausanschluesse', 'geom', {self.epsg}, 'LINESTRING')",
                "SELECT CreateSpatialIndex('t_strakathausanschluesse', 'geom')",
            ]
            for sql in sqls:
                if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import ergänze geom n t_strakathausanschluesse"):
                    raise Exception(f'{self.__class__.__name__}: Fehler beim Ergänzen von geom in t_strakathausanschluesse')

        # Datei haus.rwtopen einlesen und in Tabelle schreiben
        blength = 640                      # Blocklänge in der STRAKAT-Datei
        with open(os.path.join(self.strakatdir, 'haus.rwtopen'), 'rb') as fo:
            _ = fo.read(blength)               # Kopfzeile ohne Bedeutung?
            maxloop = 1000000                   # Begrenzung zur Sicherheit. Falls erreicht: Meldung
            for nummer in range(1, maxloop):
                """Einlesen der Blöcke. Begrenzung nur zur Sicherheit"""
                b = fo.read(blength)
                if not b or len(b) < blength:
                    break
                xlis = list(unpack('ddddddddd', b[20:92]))
                ylis = list(unpack('ddddddddd', b[100:172]))
                # d1, d2, d3, d4, d5, d6, d7, d8, d9 = unpack('fffffffff', b[220:256])

                # Erste x-Koordinate = 0 auf alle folgenden übertragen, weil in STRAKAT manchmal
                # in den hinteren Spalten noch Reste von alten Koordinaten stehen
                # In QKan (s. u.) werden alle Koordinaten mit xi < 0 unterdrückt
                for i in range(2, 8):
                    if xlis[i] < 1:
                        xlis[i+1] = -xlis[i+1]      # für nachträgliche Kontrolle

                (x1, x2, x3, x4, x5, x6, x7, x8, x9) = xlis
                (y1, y2, y3, y4, y5, y6, y7, y8, y9) = ylis

                # Hausanschlusslinie erzeugen
                ptlis = []
                for x, y in zip(xlis, ylis):
                    if x < 1 or y < 1:
                        break
                    ptlis.append(QgsPoint(x, y))
                if len(ptlis) <= 1:
                    continue
                geomwkb = QgsGeometry.fromPolyline(ptlis).asWkb()

                rohrbreite = unpack('f', b[220:224])[0]  # nur erste von 9 Rohrbreiten lesen

                hausnr = b[288:b[288:299].find(b'\x00')+288].decode('ansi').strip()

                berichtnr = unpack('i', b[299:303])[0]
                anschlusshalnr = unpack('i', b[303:307])[0]
                nextnum = unpack('i', b[311:315])[0]

                geloescht = unpack('B', b[317:318])[0]

                haschob = b[326:b[326:346].find(b'\x00')+326].decode('ansi').strip()
                haschun = b[362:b[362:382].find(b'\x00')+362].decode('ansi').strip()

                urstation = unpack('f', b[515:519])[0]

                anschlusshalname = b[611:b[611:631].find(b'\x00')+611].decode('ansi').strip()
                if anschlusshalname == '':
                    if haschob != '':
                        anschlusshalname = haschob
                    else:
                        anschlusshalname = hausnr

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
                    'haschob': haschob, 'haschun': haschun, 'urstation': urstation, 'geloescht': geloescht,
                    'strakatid': strakatid, 'hausanschlid': hausanschlid, 'geomwkb': geomwkb, "epsg": self.epsg,
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
                    haschob, haschun, urstation, geloescht,
                    strakatid, hausanschlid, geom
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
                    :haschob, :haschun, :urstation, :geloescht,
                    :strakatid, :hausanschlid, GeomFromWKB(:geomwkb, :epsg)
                )"""

                if not self.db_qkan.sql(sql, "strakat_import Hausanschlüsse", params):
                    raise Exception(f'{self.__class__.__name__}: Fehler beim Lesen der Datei "haus.rwtopen"')
            else:
                raise Exception(f'{self.__class__.__name__}: Programmfehler: Einlesen der Datei kanal.rwtopen wurde'
                                f' nicht ordnungsgemäß abgeschlossen!"')

        # Eindeutige Werte in anschlusshalnam
        sql = """
            WITH sta AS (
                SELECT anschlusshalname, count() AS anzahl
                FROM t_strakathausanschluesse
                GROUP BY anschlusshalname
            ),
            sdd AS (
                SELECT 
                    sth.pk 					AS pk,
                    CASE WHEN abs(sth.urstation + 1.0) < 0.0001
                    THEN replace(printf('sc_%d', 1000000 + sth.nummer), 'sc_1', 'sc')    -- Schachtanschluss
                    ELSE replace(printf('ha_%d', 1000000 + sth.nummer), 'ha_1', 'ha')    -- Haltungsanschluss
                    END						AS anschlusshalname
                FROM sta
                JOIN t_strakathausanschluesse AS sth ON sth.anschlusshalname = sta.anschlusshalname
                WHERE sta.anzahl > 1 OR sth.anschlusshalname = '' OR sth.anschlusshalname IS NULL
            )
            UPDATE t_strakathausanschluesse AS snn
            SET anschlusshalname = sdd.anschlusshalname
            FROM sdd
            WHERE snn.pk = sdd.pk
            """

        if not self.db_qkan.sql(sql, "strakat_import Eindeutige Bezeichnungen für Hausanschlüsse", params):
            raise Exception(f'{self.__class__.__name__}: Fehler beim eindeutigen Bezeichnungen für Hausanschlüsse"')

        self.db_qkan.commit()

        return True

    def _strakat_berichte(self) -> bool:
        """Import der Schadensdaten aus der STRAKAT-Datei 'ENBericht.rwtopen', entspricht ACCESS-Tabelle 'SCHADENSTABELLE'
        """
        # Erstellung Tabelle t_strakatberichte
        sql = "PRAGMA table_list('t_strakatberichte')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_strakatberichte', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_strakatberichte (
                pk INTEGER PRIMARY KEY,
                nummer INTEGER,
                datum TEXT,
                untersucher TEXT,
                ag_kontrolle TEXT,
                fahrzeug TEXT,
                inspekteur TEXT,
                wetter TEXT,
                bewertungsart TEXT,
                atv149 REAL,
                fortsetzung INTEGER,
                station_gegen REAL,
                station_untersucher REAL,
                atv_kuerzel TEXT,
                atv_langtext TEXT,
                charakt1 TEXT,
                charakt2 TEXT,
                quantnr1 TEXT,
                quantnr2 TEXT,
                streckenschaden TEXT,
                pos_von INTEGER,
                pos_bis INTEGER,
                sandatum TEXT,
                geloescht INTEGER,
                schadensklasse INTEGER,
                untersuchungsrichtung INTEGER,
                bandnr TEXT,
                videozaehler INTEGER,
                foto_dateiname TEXT,
                film_dateiname TEXT,
                sanierung TEXT,
                atv143 REAL,
                skdichtheit INTEGER,
                skbetriebssicherheit INTEGER,
                skstandsicherheit INTEGER,
                kommentar TEXT,
                strakatid TEXT,
                hausanschlid TEXT,
                berichtid TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_strakatberichte"'):
                return False

        def _iter() -> Iterator[Bericht_STRAKAT]:
            # Datei kanal.rwtopen einlesen und in Tabelle schreiben
            blength = 1024                      # Blocklänge in der STRAKAT-Datei
            leer = b'\x00'*128
            with open(os.path.join(self.strakatdir, 'ENBericht.rwtopen'), 'rb') as fo:

                _ = fo.read(blength)               # Kopfzeile ohne Bedeutung?

                if QKan.config.check_import.testmodus:
                    maxloop = 20000  # Testmodus für Anwender
                else:
                    maxloop = 5000000  # Begrenzung zur Sicherheit. Falls erreicht: Meldung

                for nummer in range(1, maxloop):
                    b = fo.read(blength)
                    if not b:
                        break

                    anf = b[0:128]
                    rest = b[896:1024]          # if rest != leer
                    if anf == leer:
                        continue
                    datum = b[0:10].decode('ansi')
                    if datum[2] != '.' or datum[5] != '.':
                        if re.fullmatch('\\d\\d[\\.\\,\\:\\;\\/\\*\\>\\+\\-_]'
                                        '\\d\\d[\\.\\,\\:\\;\\/\\*\\>\\+\\-_]\\d\\d\\d\\d',
                                        datum
                                        ):
                            logger.debug(f"Warnung STRAKAT-Berichte Nr. {nummer}: Datumsformat wird korrigiert: {datum}")
                            datum = datum[:2] + '.' + datum[3:5] + '.' + datum[6:10]
                        else:
                            logger.debug(f"Lesefehler STRAKAT-Berichte Nr. {nummer}: Datumsformat fehlerhaft"
                                         f". Datensatz wird ignoriert: {datum}")

                            continue
                    datum = datum[6:10] + '-' + datum[3:5] + '-' + datum[:2]
                    untersucher = b[11:b[11:31].find(b'\x00') + 11].decode('ansi').strip()
                    ag_kontrolle = b[31:b[31:46].find(b'\x00') + 31].decode('ansi').strip()
                    fahrzeug = b[46:b[46:57].find(b'\x00') + 46].decode('ansi').strip()
                    inspekteur = b[58:b[58:74].find(b'\x00') + 58].decode('ansi').strip()
                    wetter = b[73:b[73:88].find(b'\x00') + 73].decode('ansi').strip()

                    atv149 = unpack('f', b[90:94])[0]

                    fortsetzung = unpack('I', b[103:107])[0]
                    station_gegen = round(unpack('d', b[107:115])[0], 3)
                    station_untersucher = round(unpack('d', b[115:123])[0], 3)

                    atv_kuerzel = b[123:b[123:134].find(b'\x00') + 123].decode('ansi').strip()
                    if not atv_kuerzel:
                        continue
                    atv_langtext = b[134:b[134:295].find(b'\x00') + 134].decode('ansi').strip()
                    sandatum = b[284:294].decode('ansi')
                    geloescht = unpack('b', b[296:297])[0]
                    schadensklasse = unpack('B', b[295:296])[0]
                    untersuchungsrichtung = unpack('B', b[297:298])[0]
                    bandnr = b[301:b[301:320].find(b'\x00') + 301].decode('ansi').strip()
                    videozaehler = unpack('I', b[320:324])[0]
                    foto_dateiname = (f'000{bandnr}'[-3:] if len(bandnr) <= 2 else f'{bandnr}') + \
                                     f'00000{videozaehler}'[-5:]

                    wert8 = unpack('B', b[365:366])                         # STRAKAT: Bewertungsart
                    if wert8 == 4:
                        bewertungsart = 'DWA'
                    else:
                        bewertungsart = 'ATV'
                    pos_von, pos_bis = unpack('BB', b[366:368])             # STRAKAT: von/bis Uhr
                    sanierung = b[400:b[400:411].find(b'\x00') + 400].decode('ansi').strip()
                    atv143 = unpack('f', b[430:434])[0]

                    quantnr1, quantnr2 = unpack('bb', b[434:436])
                    streckenschaden = b[436:b[436:437].find(b'\x00') + 436].decode('ansi').strip()
                    charakt1 = b[438:b[438:449].find(b'\x00') + 438].decode('ansi').strip()
                    charakt2 = b[449:b[449:].find(b'\x00') + 449].decode('ansi').strip()

                    anmerkung = b[463:b[463:715].find(b'\x00') + 463].decode('ansi').strip()
                    if sanierung != '' and anmerkung != '':
                        kommentar = sanierung + ', ' + anmerkung
                    else:
                        kommentar = sanierung + anmerkung               # eins von beiden ist leer

                    skdichtheit, skstandsicherheit, skbetriebssicherheit = unpack('BBB', b[634:637])

                    (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                     ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[643:659])]
                    strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'
                    (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                     ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[659:675])]
                    hausanschlid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'
                    (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                     ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[675:691])]
                    berichtid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                    yield Bericht_STRAKAT(
                        nummer=nummer,
                        datum=datum,
                        untersucher=untersucher,
                        ag_kontrolle=ag_kontrolle,
                        fahrzeug=fahrzeug,
                        inspekteur=inspekteur,
                        wetter=wetter,
                        bewertungsart=bewertungsart,
                        atv149=atv149,
                        fortsetzung=fortsetzung,
                        station_gegen=station_gegen,
                        station_untersucher=station_untersucher,
                        atv_kuerzel=atv_kuerzel,
                        atv_langtext=atv_langtext,
                        charakt1=charakt1,
                        charakt2=charakt2,
                        quantnr1=quantnr1,
                        quantnr2=quantnr2,
                        streckenschaden=streckenschaden,
                        pos_von=pos_von,
                        pos_bis=pos_bis,
                        sandatum=sandatum,
                        geloescht=geloescht,
                        schadensklasse=schadensklasse,
                        untersuchungsrichtung=untersuchungsrichtung,
                        bandnr=bandnr,
                        videozaehler=videozaehler,
                        foto_dateiname=foto_dateiname,
                        sanierung=sanierung,
                        atv143=atv143,
                        skdichtheit=skdichtheit,
                        skbetriebssicherheit=skbetriebssicherheit,
                        skstandsicherheit=skstandsicherheit,
                        kommentar=kommentar,
                        strakatid=strakatid,
                        hausanschlid=hausanschlid,
                        berichtid=berichtid,
                    )
                else:
                    if QKan.config.check_import.testmodus:
                        logger.debug(f"Testmodus: Import Berichte nach {maxloop}. Datensatz abgebrochen")
                    else:
                        raise Exception(f"{self.__class__.__name__}: Programmfehler: Einlesen der Datei "
                                        f"kanal.rwtopen wurde nicht ordnungsgemäß abgeschlossen!")

        params = ()                           # STRAKAT data stored in tuple of dicts for better performance
                                            # with sql-statement executemany
        logger.debug("{__name__}: Berichte werden gelesen und in data gespeichert ...")

        for _bericht in _iter():
            data = {
                'nummer': _bericht.nummer,
                'datum': _bericht.datum,
                'untersucher': _bericht.untersucher,
                'ag_kontrolle': _bericht.ag_kontrolle,
                'fahrzeug': _bericht.fahrzeug,
                'inspekteur': _bericht.inspekteur,
                'wetter': _bericht.wetter,
                'bewertungsart': _bericht.bewertungsart,
                'atv149': _bericht.atv149,
                'fortsetzung': _bericht.fortsetzung,
                'station_gegen': _bericht.station_gegen,
                'station_untersucher': _bericht.station_untersucher,
                'atv_kuerzel': _bericht.atv_kuerzel,
                'atv_langtext': _bericht.atv_langtext,
                'charakt1': _bericht.charakt1,
                'charakt2': _bericht.charakt2,
                'quantnr1': _bericht.quantnr1,
                'quantnr2': _bericht.quantnr2,
                'streckenschaden': _bericht.streckenschaden,
                'pos_von': _bericht.pos_von,
                'pos_bis': _bericht.pos_bis,
                'sandatum': _bericht.sandatum,
                'geloescht': _bericht.geloescht,
                'schadensklasse': _bericht.schadensklasse,
                'untersuchungsrichtung': _bericht.untersuchungsrichtung,
                'bandnr': _bericht.bandnr,
                'videozaehler': _bericht.videozaehler,
                'foto_dateiname': _bericht.foto_dateiname,
                'sanierung': _bericht.sanierung,
                'atv143': _bericht.atv143,
                'skdichtheit': _bericht.skdichtheit,
                'skbetriebssicherheit': _bericht.skbetriebssicherheit,
                'skstandsicherheit': _bericht.skstandsicherheit,
                'kommentar': _bericht.kommentar,
                'strakatid': _bericht.strakatid,
                'hausanschlid': _bericht.hausanschlid,
                'berichtid': _bericht.berichtid,
            }
            params += (data,)

        logger.debug("{__name__}: Berichte werden in temporäre STRAKAT-Tabellen geschrieben ...")

        sql = """
            INSERT INTO t_strakatberichte (
                nummer,
                datum,
                untersucher, 
                ag_kontrolle, 
                fahrzeug, 
                inspekteur, 
                wetter,
                bewertungsart, 
                atv149, 
                fortsetzung, 
                station_gegen, 
                station_untersucher, 
                atv_kuerzel, 
                atv_langtext, 
                charakt1,
                charakt2,
                quantnr1,
                quantnr2,
                streckenschaden,
                pos_von,
                pos_bis,
                sandatum, 
                geloescht, 
                schadensklasse, 
                untersuchungsrichtung, 
                bandnr, 
                videozaehler,
                foto_dateiname, 
                sanierung, 
                atv143, 
                skdichtheit, 
                skbetriebssicherheit,
                skstandsicherheit, 
                kommentar, 
                strakatid, 
                hausanschlid, 
                berichtid
            ) VALUES (
                :nummer,
                :datum, 
                :untersucher, 
                :ag_kontrolle, 
                :fahrzeug, 
                :inspekteur, 
                :wetter,
                :bewertungsart, 
                :atv149, 
                :fortsetzung, 
                :station_gegen, 
                :station_untersucher, 
                :atv_kuerzel, 
                :atv_langtext, 
                :charakt1,
                :charakt2,
                :quantnr1,
                :quantnr2,
                :streckenschaden,
                :pos_von,
                :pos_bis,
                :sandatum, 
                :geloescht, 
                :schadensklasse, 
                :untersuchungsrichtung, 
                :bandnr, 
                :videozaehler,
                :foto_dateiname, 
                :sanierung, 
                :atv143, 
                :skdichtheit, 
                :skbetriebssicherheit,
                :skstandsicherheit, 
                :kommentar, 
                :strakatid, 
                :hausanschlid, 
                :berichtid
            )
        """

        if not self.db_qkan.sql(sql=sql, stmt_category="strakat_import Bericht", parameters=params, many=True):
            raise Exception(f'{self.__class__.__name__}: Fehler beim Lesen der Datei ENBericht.rwtopen')

        self.db_qkan.commit()

        logger.debug("{__name__}: Berichte werden in QKan-Tabellen geschrieben ...")

        return True

    def _reftables(self) -> bool:
        """Referenztabellen füllen"""

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert

        # Referenztabelle Entwässerungsarten

        sql = """INSERT INTO entwaesserungsarten (bezeichnung, kuerzel, bemerkung)
                 SELECT text, kurz, 'Importiert aus STRAKAT'
                 FROM t_reflists
                 WHERE tabtyp = 'kanalart'"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste entwaesserungsarten"):
            return False

        # Referenztabelle Haltungstypen

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

        params = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE
        sql = """INSERT INTO haltungstypen (bezeichnung, bemerkung)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM haltungstypen)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste haltungstypen", params, many=True):
            return False

        # Referenztabelle Rohrprofile

        sql = """INSERT INTO profile (profilnam, kuerzel, kommentar)
                 SELECT iif(trim(text) = '', kurz,text), kurz, 'Importiert aus STRAKAT'
                 FROM t_reflists
                 WHERE tabtyp = 'profilart'"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste profile"):
            return False

        # Referenztabelle Entwässerungsgebiete

        sql = """INSERT INTO teilgebiete (tgnam, kommentar)
                 SELECT rl.text, 'Importiert aus STRAKAT'
                 FROM t_reflists AS rl
                 JOIN t_strakatkanal AS skt ON skt.e_gebiet = rl.id         -- nur verwendete
                 WHERE tabtyp = 'entwaesserungsgebiet'
                 GROUP BY rl.id"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste profile"):
            return False


        # Referenztabelle Pumpentypen

        daten = [
            ('Offline', 1),
            ('Online Schaltstufen', 2),
            ('Online Kennlinie', 3),
            ('Online Wasserstandsdifferenz', 4),
            ('Ideal', 5),
        ]

        params = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO pumpentypen (bezeichnung, he_nr)
                    SELECT ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM pumpentypen)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste pumpentypen", params, many=True):
            return False

        # Referenztabelle Untersuchungsrichtung

        daten = [
            ('in Fließrichtung', '0', 'automatisch hinzugefügt'),
            ('gegen Fließrichtung', 'U', 'automatisch hinzugefügt'),
        ]

        params = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sql = """INSERT INTO untersuchrichtung (bezeichnung, kuerzel, bemerkung)
                    SELECT ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM untersuchrichtung)"""

        if not self.db_qkan.sql(sql, "strakat_import Referenzliste untersuchrichtung", params, many=True):
            return False

        # Erstellung Tabelle t_mapper_untersuchrichtung
        sql = "PRAGMA table_list('t_mapper_untersuchrichtung')"
        if not self.db_qkan.sql(sql, "Prüfen, ob temporäre Tabelle 't_mapper_untersuchrichtung', vorhanden ist"):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen
        if not self.db_qkan.fetchone():
            sql = """ 
            CREATE TABLE IF NOT EXISTS t_mapper_untersuchrichtung (
                id INTEGER PRIMARY KEY,
                untersuchungsrichtung TEXT
            )"""

            if not self.db_qkan.sql(sql, 'Erstellung Tabelle "t_mapper_untersuchrichtung"'):
                return False

        # Liste enthält nur Schachtarten, die nicht 'Schacht' und dabei 'vorhanden' sind (einschließlich 1: 'NS Normalschacht')
        daten = [
            (0,  'in Fließrichtung'),
            (1,  'gegen Fließrichtung'),
        ]
        sql = """INSERT INTO t_mapper_untersuchrichtung (id, untersuchungsrichtung)
                    SELECT ? AS id, ? as untersuchungsrichtung
                WHERE id NOT IN (SELECT id FROM t_mapper_untersuchrichtung)"""

        if not self.db_qkan.sql(sql,
                                "strakat_import Referenzliste t_mapper_untersuchrichtung",
                                daten,
                                many=True):
            return False

        # Simulationsstatus
        # In STRAKAT gibt es keinen Simulationsstatus. Allerdings enthalten einige Referenzwerte aus der
        # Referenztabelle "Kanalart" Werte, die in QKan in die Tabelle Simulationsstatus übertragen werden müssen.

        sql = """
            INSERT INTO simulationsstatus (bezeichnung, kuerzel)
            SELECT text, kurz FROM t_reflists
            WHERE tabtyp = 'kanalart' AND 
                  (kurz like '%stillg%' OR kurz like '%neub%' OR kurz like '%plan%' OR kurz like '%verdäm%')
            GROUP BY text 
        """
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste simulationsstatus"):
            return False

        # Referenztabelle Eigentum

        sql = """INSERT INTO eigentum (name, kommentar)
                 SELECT text, 'Importiert aus STRAKAT'
                 FROM t_reflists
                 WHERE tabtyp = 'eigentum'"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste eigentum"):
            return False

        self.db_qkan.commit()

        return True

        # Liste der Kanalarten entspricht im Wesentlichen der QKan-Tabelle 'Entwässerungsarten'

    def _adapt_refvals(self):
        """Passt nach dem Import der Kanaldaten die Bezeichnungen an den QKan-Standard an.
           Die Werte in den Tabellen werden dabei über Trigger entsprechend den Referenztabellen geändert
           Anschließend werden für Standardwerte die Schlüssel für diverse Exportformate ergänzt. """

        # Entwässerungsarten

        # Bezeichnungen in Referenztabelle und bezogenen Tabellen (über trigger) an QKan-Standard anpassen
        self.db_qkan._adapt_reftable('entwaesserungsarten')

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

        # Ergänzen der Standarddatensätze, falls nicht vorhanden
        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sql = """INSERT INTO entwaesserungsarten (
                    bezeichnung, kuerzel, bemerkung, he_nr, kp_nr, m150, isybau, transport, druckdicht)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM entwaesserungsarten)"""
        if not self.db_qkan.sql(sql, "Isybau Referenzliste entwaesserungsarten", daten, many=True):
            return False

        # Ergänzen weiterer Kennnummern in speziellen Datensätzen
        params = [(ds[2], ds[3], ds[4], ds[5], ds[6], ds[0],) for ds in daten]           # umsortieren
        sql = """UPDATE entwaesserungsarten
                 SET he_nr = ?, kp_nr = ?, m150 = ?, isybau = ?, bemerkung = ?
                 WHERE bezeichnung = ?"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste entwaesserungsarten", params, many=True):
            return False

        # Simulationsstatus

        # Bezeichnungen in Referenztabelle und bezogenen Tabellen (über trigger) an QKan-Standard anpassen
        self.db_qkan._adapt_reftable('simulationsstatus')

        daten = [  # bez    kurz he mu kp m150 m145 isy
            ('in Betrieb', 'B', 1, 1, 0, 'B', '1', '0', 'QKan-Standard'),
            ('außer Betrieb', 'AB', 4, None, 3, 'B', '1', '20', 'QKan-Standard'),
            ('geplant', 'P', 2, None, 1, 'P', None, '10', 'QKan-Standard'),
            ('stillgelegt', 'N', None, None, 4, 'N', None, '21', 'QKan-Standard'),
            ('verdämmert', 'V', 5, None, None, 'V', None, None, 'QKan-Standard'),
            ('fiktiv', 'F', 3, None, 2, None, None, '99', 'QKan-Standard'),
            ('rückgebaut', 'P', None, None, 6, None, None, '22', 'QKan-Standard'),
        ]

        # Ergänzen der Standarddatensätze, falls nicht vorhanden
        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sql = """INSERT INTO simulationsstatus (
                    bezeichnung, kuerzel, he_nr, mu_nr, kp_nr, m150, m145, isybau, kommentar)
                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                    WHERE ? NOT IN (SELECT bezeichnung FROM simulationsstatus)"""
        if not self.db_qkan.sql(sql, "Ergänzung Referenzliste simulationsstatus", daten, many=True):
            return False

        # Ergänzen weiterer Kennnummern in speziellen Datensätzen
        params = [(ds[2], ds[3], ds[4], ds[5], ds[6], ds[7], ds[8], ds[0],) for ds in daten]           # umsortieren
        sql = """UPDATE simulationsstatus
                 SET he_nr = ?, mu_nr = ?, kp_nr = ?, m150 = ?, m145 = ?, isybau = ?, kommentar = ?
                 WHERE bezeichnung = ?"""
        if not self.db_qkan.sql(sql, "strakat_import Referenzliste simulationsstatus", params, many=True):
            return False

    def _schaechte(self) -> bool:
        """Import der Schächte aus der STRAKAT-Tabelle KANALTABELLE"""

        if not QKan.config.check_import.schaechte:
            return True

        sql = """WITH
            strassen AS (
                SELECT n1 AS id, kurz, trim(text) AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            schachtmaterial AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'schachtmaterial'
            ),
            entwart AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'kanalart' 
            ),
            knotenart AS (
                SELECT n1 AS id, n4, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'schachtart' 
            ),
            gebiet AS (
                SELECT n1 AS id, text, kurz
                FROM t_reflists
                WHERE tabtyp = 'entwaesserungsgebiet'
            ),
            eigentum AS (
                SELECT n1 AS id, text, kurz
                FROM t_reflists
                WHERE tabtyp = 'eigentum'
            )
            INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe, strasse, material, 
                                durchm, entwart, schachttyp, knotentyp, baujahr, eigentum, teilgebiet,
                                kommentar, geop, geom)
            SELECT
                stk.schacht_oben                            AS schnam,
                stk.rw_gerinne_o                            AS xsch,
                stk.hw_gerinne_o                            AS ysch,
                MIN(CASE WHEN stk.s_sohle_oben_v<1 Or stk.s_sohle_oben_v > 5000
                    THEN stk.sohle_oben___v
                    ELSE stk.s_sohle_oben_v
                    END
                )                                           AS sohlhoehe,
                MAX(CASE WHEN stk.deckel_oben_v <1 Or stk.deckel_oben_v > 5000
                    THEN Null 
                    ELSE stk.deckel_oben_v
                    END
                )                                           AS deckelhoehe,
                CASE WHEN INSTR(strassen.name,' ') > 0
                    THEN substr(strassen.name, INSTR(strassen.name,' ')+1)
                    ELSE strassen.name
                END                                         AS strasse,
                schachtmaterial.text                        AS material,
                1.0                                         AS durchm,
                k2e.text                                    AS entwart,
                'Schacht'                                   AS schachttyp,
                k2t.text                                    AS knotentyp,
                stk.baujahr                                 AS baujahr,
                eg.text                                     AS eigentum,
                k2g.text                                    AS teilgebiet,
                CASE WHEN count(*) > 1
                THEN printf('Schacht in STRAKAT %s mal vorhanden', count(*))
                ELSE 'QKan-STRAKAT-Import' END              AS kommentar,
                Makepoint(stk.rw_gerinne_o, stk.hw_gerinne_o, :epsg)  AS geop,
                CastToMultiPolygon(MakePolygon(MakeCircle(
                    stk.rw_gerinne_o, stk.hw_gerinne_o, 1.0, :epsg))) AS geom
            FROM
                t_strakatkanal AS stk
                LEFT JOIN strassen                              
                ON stk.strassennummer = strassen.id
                LEFT JOIN schachtmaterial                       
                ON stk.schachtmaterial = schachtmaterial.id
                JOIN entwart AS k2e           
                ON stk.kanalart = k2e.id
                JOIN knotenart AS k2t
                ON stk.schachtart = k2t.id
                JOIN gebiet AS k2g
                ON stk.e_gebiet = k2g.id
                LEFT JOIN schaechte AS sd
                ON sd.schnam = stk.schacht_oben
                LEFT JOIN eigentum AS eg
                ON eg.id = stk.eigentum 
            WHERE
                    stk.schachtnummer <> 0
                AND stk.schachtart <> 0                 -- keine Knickpunkte
                AND stk.schacht_oben Is Not Null
                AND stk.rw_gerinne_o Is Not Null
                AND stk.hw_gerinne_o Is Not Null
                AND sd.pk IS NULL                       -- nur neue hinzufügen
            GROUP BY
                stk.schacht_oben
            """

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import Schächte", params):
            raise Exception(f"{self.__class__.__name__}: Fehler in strakat_import Schächte")

        self.db_qkan.commit()

        return True

    def _haltungen(self) -> bool:
        """Import der Haltungen aus der STRAKAT-Tabelle KANALTABELLE"""

        if not QKan.config.check_import.haltungen:
            return True

        sql = """
            WITH
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
                SELECT n1 AS id, kurz, trim(text) AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            entwart AS (
                SELECT n1 AS id, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'kanalart' 
            ),
            knotenart AS (
                SELECT n1 AS id, n4, kurz, text
                FROM t_reflists
                WHERE tabtyp = 'schachtart' 
            ),
            gebiet AS (
                SELECT n1 AS id, text, kurz
                FROM t_reflists
                WHERE tabtyp = 'entwaesserungsgebiet'
            ),
            eigentum AS (
                SELECT n1 AS id, text, kurz
                FROM t_reflists
                WHERE tabtyp = 'eigentum'
            )
            INSERT INTO haltungen (haltnam, schoben, schunten, laenge, 
                xschob, yschob, xschun, yschun, 
                breite, hoehe, 
                sohleoben, sohleunten, 
                profilnam, entwart, druckdicht, material, strasse, eigentum, teilgebiet,  
                haltungstyp, baujahr, simstatus, kommentar, geom)
            SELECT
                stk.haltungsname                                            AS haltnam,
                stk.schacht_oben                                            AS schoben,
                stk.schacht_unten                                           AS schunten,
                stk.laenge                                                  AS laenge,
                iif(:coordsFromRohr, stk.rw_rohranfang, stk.rw_gerinne_o)   AS xschob,
                iif(:coordsFromRohr, stk.hw_rohranfang, stk.hw_gerinne_o)   AS yschob,
                iif(:coordsFromRohr, stk.rw_rohrende, stk.rw_gerinne_u)     AS xschun,
                iif(:coordsFromRohr, stk.hw_rohrende, stk.hw_gerinne_u)     AS yschun,
                stk.rohrbreite_v                                            AS breite,
                stk.rohrhoehe___v                                           AS hoehe,
                stk.sohle_oben___v                                          AS sohleoben,
                stk.sohle_unten__v                                          AS sohleunten,
                profilarten.text                                            AS profilnam,
                k2e.text                                                    AS entwart,
                CASE WHEN instr(lower(k2e.text),'druck') > 0
                    THEN 1 ELSE 0 END                                       AS druckdicht,
                rohrmaterialien.text                                        AS material,
                CASE WHEN INSTR(strassen.name,' ') > 0
                    THEN substr(strassen.name, INSTR(strassen.name,' ')+1)
                    ELSE strassen.name
                END                                                         AS strasse,
                eg.text                                                     AS eigentum,
                k2g.text                                                    AS teilgebiet,
                'Haltung'                                                   AS haltungstyp,
                stk.baujahr                                                 AS baujahr,
                'in Betrieb'                                                AS simstatus,
                'QKan-STRAKAT-Import'                                       AS kommentar,
                MakeLine(MakePoint(iif(:coordsFromRohr, stk.rw_rohranfang, stk.rw_gerinne_o),
                                   iif(:coordsFromRohr, stk.hw_rohranfang, stk.hw_gerinne_o), :epsg),
                         MakePoint(iif(:coordsFromRohr, stk.rw_rohrende, stk.rw_gerinne_u),
                                   iif(:coordsFromRohr, stk.hw_rohrende, stk.hw_gerinne_u), :epsg))
                                                                            AS geom
            FROM
                t_strakatkanal      AS stk
                LEFT JOIN profilarten       ON stk.profilart_v = profilarten.id
                LEFT JOIN rohrmaterialien   ON stk.Material_v = rohrmaterialien.ID
                LEFT JOIN strassen          ON stk.strassennummer = strassen.ID
                JOIN entwart        AS k2e  ON stk.kanalart = k2e.id
                JOIN knotenart      AS k2t  ON stk.schachtart = k2t.id
                JOIN gebiet         AS k2g  ON stk.e_gebiet = k2g.id
                LEFT JOIN haltungen         ON haltungen.haltnam = stk.haltungsname
                LEFT JOIN eigentum  AS eg   ON eg.id = stk.eigentum 
            WHERE stk.laenge > 0.045
              AND stk.schachtnummer <> 0                         -- nicht geloescht
              AND k2t.n4 <> 0
              AND haltungen.pk IS NULL                           -- nur neue Haltungen hinzufügen
              """

        params = {"epsg": self.epsg, "coordsFromRohr": QKan.config.strakat.coords_from_rohr}

        if not self.db_qkan.sql(sql, "strakat_import Haltungen (1)", params):
            raise Exception(f"{self.__class__.__name__}: Fehler in strakat_import Haltungen (1)")

        self.db_qkan.commit()

        # Zusammengesetzte Haltungen werden neu erzeugt und überschreiben das geom-Objekt der jeweiligen Anfanghaltung
        # Erkennungsmerkmal: 1. Kanal hat Schachtart.n4 <>0, alle weiteren haben die Schachtart.n4 0.
        # Einschränkung: Als 1. Kanal zählen nur Kanäle, die nicht gemeinsam mit einem anderen Kanal mit schachtart.n4 = 0
        # in einen Schacht einleiten. Zusätzlich müssen aufeinander folgende Teile in folgenden Attribute
        # identisch sein: eigentum, kanalart

        def _getstraenge():
            """Liest alle zusammengesetzten Kanäle (Kriterium: knotenart.n4 = 0 zuzüglich oberhalb liegendem Kanal)"""
            sql = """WITH
                    knotenart AS (
                        SELECT n1 AS id, n4, kurz, text
                        FROM t_reflists
                        WHERE tabtyp = 'schachtart' 
                    ),
                    kanal AS (
                        SELECT
                            stk.nummer          AS nummer,
                            stk.haltungsname    AS haltungsname,
                            stk.schacht_oben    AS schacht_oben,
                            stk.schacht_unten   AS schacht_unten,
                            stk.rw_gerinne_o    AS rw_gerinne_o,
                            stk.hw_gerinne_o    AS hw_gerinne_o,
                            stk.rw_gerinne_u    AS rw_gerinne_u,
                            stk.hw_gerinne_u    AS hw_gerinne_u,
                            stk.rw_rohranfang   AS rw_rohranfang,
                            stk.hw_rohranfang   AS hw_rohranfang,
                            stk.rw_rohrende     AS rw_rohrende,
                            stk.hw_rohrende     AS hw_rohrende,
                            stk.schachtart      AS schachtart,
                            stk.kanalart        AS kanalart,
                            stk.eigentum        AS eigentum,
                            k2t.n4              AS n4
                        FROM
                            t_strakatkanal AS stk
                            JOIN knotenart AS k2t ON k2t.id = stk.schachtart
                    ),
                    ko AS (
                        SELECT k1.*
                        FROM kanal AS k1
                        LEFT JOIN (SELECT * FROM kanal WHERE n4 = 0) AS k2
                        ON k2.schacht_unten = k1.schacht_unten          -- muendet gemeinsam in einen Schacht
                        WHERE k1.n4 = 0 OR k2.nummer IS NULL    -- entweder n4 = 0 oder wenn nicht, dann kein paralleler mit n4 = 0
                    )
                    SELECT
                        ko.haltungsname, ko.schacht_oben, ko.schacht_unten,
                        ko.schachtart AS schachtart_ob, ku.schachtart AS schachtart_un, 
                        iif(:coordsFromRohr, ko.rw_rohranfang, ko.rw_gerinne_o) as xob, 
                        iif(:coordsFromRohr, ko.hw_rohranfang, ko.hw_gerinne_o) as yob,
                        iif(:coordsFromRohr, ko.rw_rohrende, ko.rw_gerinne_u) as xun,
                        iif(:coordsFromRohr, ko.hw_rohrende, ko.hw_gerinne_u) as yun
                        FROM ko
                        JOIN kanal AS ku ON ku.schacht_oben = ko.schacht_unten
                        WHERE ko.n4 = 0
                           OR (ku.n4 = 0 AND ko.kanalart = ku.kanalart AND ko.eigentum = ku.eigentum)
                        GROUP BY ko.haltungsname, ko.schacht_oben, ko.schacht_unten
                       """

            params = {"coordsFromRohr": QKan.config.strakat.coords_from_rohr}
            if not self.db_qkan.sql(sql, parameters=params):
                raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Haltungen (2)")

            stnet = self.db_qkan.fetchall()

            idxschob = {ds[1]: ds for ds in stnet}
            idxschun = {ds[2]: ds for ds in stnet}

            # Schleife bis alle Haltungsteilstücke verarbeitet sind
            while len(idxschob) > 0:
                gplis = []  # Knotenpunkte einer zusammengesetzten Haltung
                # Anfang finden
                for anf in idxschob:
                    # Wenn kein Teilstück oberhalb
                    if not idxschun.get(anf):
                        break
                else:
                    logger.debug('\nInhalt von idxschob:\nschacht_unten: nummer_oben, nummer_unten, haltungsname, schacht_oben, schacht_unten, '
                                 'schachtart_ob, schachtart_un, xob, yob, xun, yun')
                    errormsg = '\n'.join([f'{anf}: {idxschob.get(anf, "Error: anf nicht gefunden")}' for anf in idxschob])
                    logger.error(errormsg + '\n')
                    errormsg = f'Fehler: Konnte (mindestens) ein Haltungsteilstück ' + \
                                    f'nicht verarbeiten: Schacht oben = {anf}'
                    # with open('c:/temp/strakat_polygons/net.csv', 'w') as fw:
                    #     fw.write(
                    #         '\nInhalt von idxschob:\nschacht_unten: nummer_oben, nummer_unten, haltungsname, schacht_oben, schacht_unten, '
                    #         'schachtart_ob, schachtart_un, xob, yob, xun, yun\n')
                    #     errormsg = '\n'.join(
                    #         [f'{anf}: {idxschob.get(anf, "Error: anf nicht gefunden")}' for anf in idxschob])
                    #     fw.write(errormsg + '\n')
                    #     errormsg = f'Fehler: Konnte (mindestens) ein Haltungsteilstück ' + \
                    #                f'nicht verarbeiten: Schacht oben = {anf}'
                    raise Exception(errormsg)
                # Kanal verfolgen und jedes Teilstück entnehmen
                haltnam = idxschob[anf][0]
                node = anf  # Anfang übernehmen
                while True:
                    ds = idxschob[node]
                    gplis.append([ds[5], ds[6]])  # Anfangskoordinate
                    next = idxschob.get(node)[2]  # Schacht unten als nächsten Schacht übernehmen
                    if not idxschob.get(next):
                        # Ende gefunden
                        gplis.append([ds[7], ds[8]])  # Endkoordinate
                        del idxschob[node]
                        break
                    del idxschob[node]
                    node = next

                ptlis = [QgsPoint(x, y) for x, y in gplis]
                geom = QgsGeometry.fromPolyline(ptlis)

                yield haltnam, geom.asWkb()

        for strang_haltnam, strang_wkb in _getstraenge():
            params = {"geom": strang_wkb, "haltnam": strang_haltnam, "epsg": self.epsg}
            sql = f"""UPDATE haltungen SET geom = GeomFromWKB(:geom, :epsg)
                        WHERE haltnam = :haltnam"""
            if not self.db_qkan.sql(sql, "strakat_import Zusammensetzen der Kanalstränge", params):
                raise Exception(f"{self.__class__.__name__}: Fehler bei ")

        self.db_qkan.commit()

        return True

    def _anschlussleitungen(self) -> bool:
        """Import der STRAKAT-Tabelle anschlussleitungen"""

        if not QKan.config.check_import.hausanschluesse:
            return True

        sql = """
            WITH ha AS (
            SELECT
                pk,
                nummer                          AS nummer, 
                anschlusshalname                AS leitnam,
                Trim(haschob)                   AS schoben,
                Trim(haschun)                   AS schunten,
                rohrbreite                      AS hoehe,
                rohrbreite                      AS breite,
                geom                            AS geom
            FROM t_strakathausanschluesse
            WHERE geloescht = 0
            )
            INSERT INTO anschlussleitungen (leitnam, schoben, schunten, 
                hoehe, breite, laenge,
                simstatus, kommentar, geom)
            SELECT
                ha.leitnam,
                ha.schoben,
                ha.schunten,
                ha.hoehe,
                ha.breite,
                GLength(ha.geom)                    AS laenge,
                'in Betrieb'                        AS simstatus,
                'QKan-STRAKAT-Import'               AS kommentar,
                ha.geom                             AS geom
            FROM
                ha
                LEFT JOIN anschlussleitungen    USING (leitnam, schoben, schunten)
            WHERE anschlussleitungen.pk IS NULL                         -- nur neue Anschlussleitungen hinzufügen
			"""

        params = {"epsg": self.epsg}

        if not self.db_qkan.sql(sql, "strakat_import anschlussleitungen", params):
            raise Exception(f"{self.__class__.__name__}: Fehler bei ")

        self.db_qkan.commit()

        return True

    def _schaechte_untersucht(self) -> bool:
        """Import der Schächte mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.schachtschaeden:
            return True

        sql = """
            WITH
            strassen AS (
                SELECT n1 AS id, kurz, trim(text) AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            sku AS (
            SELECT                                              -- Schacht oben
                stk.schacht_oben                            AS schnam,
                1.0                                         AS durchm,
                stk.baujahr                                 AS baujahr,
                stb.datum                                   AS untersuchtag,
                stb.untersucher                             AS untersucher,
                CASE WHEN instr(lower(stb.wetter), 'trock') + 
                           instr(lower(stb.wetter), 'kein Nied') > 0 THEN 1
                      WHEN instr(lower(stb.wetter), 'reg')       > 0 THEN 2
                      WHEN instr(lower(stb.wetter), 'fros') +
                           instr(lower(stb.wetter), 'chnee')     > 0 THEN 3
                      ELSE NULL END 		    AS wetter,
                CASE WHEN INSTR(trim(strassen.name),' ') > 0
                    THEN substr(trim(strassen.name), INSTR(trim(strassen.name),' ')+1)
                    ELSE trim(strassen.name)
                END                                         AS strasse,
                stb.bewertungsart                           AS bewertungsart,
                NULL                                        AS bewertungstag,
                NULL                                        AS auftragsbezeichnung,
                'DWA'                                       AS datenart,
                stb.skdichtheit                             AS max_ZD,
                stb.skbetriebssicherheit                    AS max_ZB,
                stb.skstandsicherheit                       AS max_ZS,
                'QKan-STRAKAT-Import'                       AS kommentar,
                Makepoint(stk.rw_gerinne_o, stk.hw_gerinne_o, :epsg)  AS geop
            FROM
                t_strakatkanal AS stk
                LEFT JOIN strassen              ON stk.strassennummer = strassen.id
                JOIN t_strakatberichte  AS stb  ON stb.strakatid = stk.strakatid
            WHERE
                    stk.schachtnummer <> 0
                AND stb.geloescht = 0
                AND stk.schachtart <> 0                 -- keine Knickpunkte
                AND schnam Is Not Null
                AND stk.rw_gerinne_o Is Not Null
                AND stk.hw_gerinne_o Is Not Null
                AND substr(stb.atv_kuerzel, 1, 1) = 'D' AND substr(stb.atv_kuerzel, 2, 1) <> '-' 
                AND (   (stb.untersuchungsrichtung = 1 AND stb.station_untersucher < 0.01) 
                     OR (stb.untersuchungsrichtung = 0 AND stb.station_untersucher > stk.laenge * 0.9)
                    ) 
            UNION
            SELECT                                              -- Schacht unten 
                stk.schacht_unten                           AS schnam,
                1.0                                         AS durchm,
                stk.baujahr                                 AS baujahr,
                stb.datum                                   AS untersuchtag,
                stb.untersucher                             AS untersucher,
                CASE WHEN instr(lower(stb.wetter), 'trock') + 
                           instr(lower(stb.wetter), 'kein Nied') > 0 THEN 1
                      WHEN instr(lower(stb.wetter), 'reg')       > 0 THEN 2
                      WHEN instr(lower(stb.wetter), 'fros') +
                           instr(lower(stb.wetter), 'chnee')     > 0 THEN 3
                      ELSE NULL END 		    AS wetter,
                CASE WHEN INSTR(trim(strassen.name),' ') > 0
                    THEN substr(trim(strassen.name), INSTR(trim(strassen.name),' ')+1)
                    ELSE trim(strassen.name)
                END                                         AS strasse,
                stb.bewertungsart                           AS bewertungsart,
                NULL                                        AS bewertungstag,
                NULL                                        AS auftragsbezeichnung,
                'DWA'                                       AS datenart,
                stb.skdichtheit                             AS max_ZD,
                stb.skbetriebssicherheit                    AS max_ZB,
                stb.skstandsicherheit                       AS max_ZS,
                'QKan-STRAKAT-Import'                       AS kommentar,
                Makepoint(stk.rw_gerinne_o, stk.hw_gerinne_o, :epsg)  AS geop
            FROM
                t_strakatkanal                  AS stk
                LEFT JOIN strassen                      ON stk.strassennummer = strassen.id
                JOIN t_strakatberichte          AS stb  ON stb.strakatid = stk.strakatid
            WHERE
                    stk.schachtnummer <> 0
                AND stb.geloescht = 0
                AND stk.schachtart <> 0                 -- keine Knickpunkte
                AND schnam Is Not Null
                AND stk.rw_gerinne_o Is Not Null
                AND stk.hw_gerinne_o Is Not Null
                AND substr(stb.atv_kuerzel, 1, 1) = 'D' AND substr(stb.atv_kuerzel, 2, 1) <> '-' 
                AND (   (stb.untersuchungsrichtung = 0 AND stb.station_untersucher < 0.01) 
                     OR (stb.untersuchungsrichtung = 1 AND stb.station_untersucher > stk.laenge * 0.9)
                    ) 
            )
            INSERT INTO schaechte_untersucht (
                schnam, durchm, baujahr, 
                untersuchtag, untersucher,
                wetter, strasse,
                bewertungsart, bewertungstag, auftragsbezeichnung, datenart,
                max_ZD, max_ZB, max_ZS,
                kommentar, geop)
            SELECT 
                sku.schnam, sku.durchm, sku.baujahr, 
                sku.untersuchtag, sku.untersucher,
                sku.wetter, sku.strasse,
                sku.bewertungsart, sku.bewertungstag, sku.auftragsbezeichnung, sku.datenart, 
                min(sku.max_ZD) AS max_ZD, min(sku.max_ZB) AS max_ZB, min(sku.max_ZS) AS max_ZS, 
                sku.kommentar, sku.geop
            FROM sku
            LEFT JOIN schaechte_untersucht AS schunt USING (schnam, untersuchtag)
            WHERE schunt.pk IS NULL                             -- nur neue Schächte untersucht hinzufügen 
            GROUP BY schnam, untersuchtag
        """

        params = {"epsg": self.epsg}
        if not self.db_qkan.sql(sql, "strakat_import Schächte untersucht", params):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Schächte untersucht")

        self.db_qkan.commit()

        return True

    def _untersuchdat_schacht(self) -> bool:
        """Import der Schachtschäden aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.schachtschaeden:
            return True

        sql = """
            WITH
            strassen AS (
                SELECT n1 AS id, kurz, trim(text) AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            uts AS (
                SELECT                                              -- Schacht oben
                    stk.schacht_oben                AS untersuchsch,
                    NULL                            AS id, 
                    stb.datum                       AS untersuchtag,
                    stb.bandnr                      AS bandnr,
                    stb.videozaehler                AS videozaehler,
                    NULL                            AS timecode,
                    stb.atv_langtext                AS langtext,
                    stb.atv_kuerzel                 AS kuerzel,
                    stb.charakt1                    AS charakt1,
                    stb.charakt2                    AS charakt2,                
                    stb.quantnr1                    AS quantnr1,
                    stb.quantnr2                    AS quantnr2,                
                    stb.streckenschaden             AS streckenschaden,
                    stb.fortsetzung                 AS streckenschaden_lfdnr,
                    stb.pos_von                     AS pos_von, 
                    stb.pos_bis                     AS pos_bis,
                    :ordner_bild  || replace(printf('\\band%d\\', 1000000 + stb.bandnr), 'band10', 'band')
                                  || stb.foto_dateiname || '.jpg'
                                                    AS foto_dateiname,
                    :ordner_video || '\\'  || stb.foto_dateiname
                                  || ' von '  || stk.schacht_oben
                                  || ' nach ' || stk.schacht_unten
                                  || ' - '    || strassen.name  || '.mpg' 
                                                    AS film_dateiname,
                    NULL                            AS filmtyp,
                    NULL                            AS video_start,
                    NULL                            AS video_ende,
                    stb.skdichtheit                 AS ZD,
                    stb.skbetriebssicherheit        AS ZB,
                    stb.skstandsicherheit           AS ZS,
                    stb.kommentar                   AS kommentar
                FROM
                    t_strakatberichte  AS stb
                    JOIN t_strakatkanal AS stk      ON stk.strakatid = stb.strakatid
                    LEFT JOIN strassen              ON stk.strassennummer = strassen.id
                WHERE stk.laenge > 0.045
                  AND stk.schachtnummer <> 0
                  AND stb.geloescht = 0
                  AND stb.hausanschlid = '00000000-0000-0000-0000-000000000000'
                  AND substr(stb.atv_kuerzel, 1, 1) = 'D' AND substr(stb.atv_kuerzel, 2, 1) <> '-' 
                  AND (   (stb.untersuchungsrichtung = 1 AND stb.station_untersucher < 0.01) 
                       OR (stb.untersuchungsrichtung = 0 AND stb.station_untersucher > stk.laenge * 0.9)
                      ) 
                UNION
                SELECT                                              -- Schacht unten
                    stk.schacht_unten               AS untersuchsch,
                    NULL                            AS id, 
                    stb.datum                       AS untersuchtag,
                    stb.bandnr                      AS bandnr,
                    stb.videozaehler                AS videozaehler,
                    NULL                            AS timecode,
                    stb.atv_langtext                AS langtext,
                    stb.atv_kuerzel                 AS kuerzel,
                    stb.charakt1                    AS charakt1,
                    stb.charakt2                    AS charakt2,                
                    stb.quantnr1                    AS quantnr1,
                    stb.quantnr2                    AS quantnr2,                
                    stb.streckenschaden             AS streckenschaden,
                    stb.fortsetzung                 AS streckenschaden_lfdnr,
                    stb.pos_von                     AS pos_von, 
                    stb.pos_bis                     AS pos_bis,
                    :ordner_bild  || replace(printf('\\band%d\\', 1000000 + stb.bandnr), 'band10', 'band')
                                  || stb.foto_dateiname || '.jpg'
                                                    AS foto_dateiname,
                    :ordner_video || '\\'  || stb.foto_dateiname
                                  || ' von '  || stk.schacht_oben
                                  || ' nach ' || stk.schacht_unten
                                  || ' - '    || strassen.name  || '.mpg' 
                                                    AS film_dateiname,
                    NULL                            AS filmtyp,
                    NULL                            AS video_start,
                    NULL                            AS video_ende,
                    stb.skdichtheit                 AS ZD,
                    stb.skbetriebssicherheit        AS ZB,
                    stb.skstandsicherheit           AS ZS,
                    stb.kommentar                   AS kommentar
                FROM
                    t_strakatberichte  AS stb
                    JOIN t_strakatkanal AS stk      ON stk.strakatid = stb.strakatid
                    LEFT JOIN strassen              ON stk.strassennummer = strassen.id
                WHERE stk.laenge > 0.045
                  AND stk.schachtnummer <> 0
                  AND stb.geloescht = 0
                  AND stb.hausanschlid = '00000000-0000-0000-0000-000000000000'
                  AND substr(stb.atv_kuerzel, 1, 1) = 'D' AND substr(stb.atv_kuerzel, 2, 1) <> '-' 
                  AND (   (stb.untersuchungsrichtung = 0 AND stb.station_untersucher < 0.01) 
                       OR (stb.untersuchungsrichtung = 1 AND stb.station_untersucher > stk.laenge * 0.9)
                      ) 
            )
            INSERT INTO untersuchdat_schacht (
                untersuchsch,
                id, untersuchtag,
                bandnr, videozaehler, timecode, langtext, 
                kuerzel, charakt1, charakt2, quantnr1, quantnr2,
                streckenschaden, streckenschaden_lfdnr,
                pos_von, pos_bis,
                foto_dateiname, film_dateiname,
                filmtyp, video_start, video_ende,
                ZD, ZB, ZS, kommentar
            )
            SELECT
                uts.untersuchsch,
                uts.id, uts.untersuchtag,
                uts.bandnr, uts.videozaehler, uts.timecode, uts.langtext, 
                uts.kuerzel, uts.charakt1, uts.charakt2, uts.quantnr1, uts.quantnr2,
                uts.streckenschaden, uts.streckenschaden_lfdnr,
                uts.pos_von, uts.pos_bis,
                uts.foto_dateiname, uts.film_dateiname,
                uts.filmtyp, uts.video_start, uts.video_ende,
                uts.ZD, uts.ZB, uts.ZS, uts.kommentar
            FROM uts
            LEFT JOIN untersuchdat_schacht AS usd 
            USING(untersuchsch, untersuchtag, kuerzel, bandnr, videozaehler, streckenschaden_lfdnr, langtext)
            WHERE usd.pk IS NULL                                        -- nur neue Schächte untersucht hinzufügen
        """

        params = {'ordner_bild': self.ordner_bild, 'ordner_video': self.ordner_video, 'epsg': self.epsg}
        if not self.db_qkan.sql(sql, "strakat_import der Schachtschäden", params):
            raise Exception(f"{self.__class__.__name__}: Fehler bei ")

        self.db_qkan.commit()

        self.db_qkan.setschadenstexte_schaechte()
        self.progress_bar.setValue(55)
        logger.debug("setschadenstexte_schaechte"),

        return True

    def _haltungen_untersucht(self) -> bool:
        """Import der Haltungen mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.haltungsschaeden:
            return True

        sql = """
            WITH
            strassen AS (
                SELECT n1 AS id, kurz, trim(text) AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            )
            INSERT INTO haltungen_untersucht (haltnam, schoben, schunten, laenge, 
                xschob, yschob, xschun, yschun, 
                breite, hoehe, 
                strasse, 
                baujahr, untersuchtag, untersucher, untersuchrichtung, 
                wetter,
                bewertungsart, bewertungstag, datenart, 
                max_ZD, max_ZB, max_ZS, 
                kommentar, geom)
            SELECT
                stk.haltungsname                AS haltnam,
                stk.schacht_oben                AS schoben,
                stk.schacht_unten               AS schunten,
                stk.laenge                      AS laenge,
                iif(:coordsFromRohr, stk.rw_rohranfang, stk.rw_gerinne_o)   AS xschob,
                iif(:coordsFromRohr, stk.hw_rohranfang, stk.hw_gerinne_o)   AS yschob,
                iif(:coordsFromRohr, stk.rw_rohrende, stk.rw_gerinne_u)     AS xschun,
                iif(:coordsFromRohr, stk.hw_rohrende, stk.hw_gerinne_u)     AS yschun,
                stk.rohrbreite_v                AS breite,
                stk.rohrhoehe___v               AS hoehe,
                CASE WHEN INSTR(trim(strassen.name),' ') > 0
                    THEN substr(trim(strassen.name), INSTR(trim(strassen.name),' ')+1)
                    ELSE trim(strassen.name)
                END                             AS strasse,
                stk.baujahr                     AS baujahr,
                stb.datum                       AS untersuchtag,
                stb.untersucher                 AS untersucher,
                stb.untersuchungsrichtung       AS untersuchrichtung,
                CASE WHEN instr(lower(stb.wetter), 'trock') + 
                           instr(lower(stb.wetter), 'kein Nied') > 0 THEN 1
                      WHEN instr(lower(stb.wetter), 'reg')       > 0 THEN 2
                      WHEN instr(lower(stb.wetter), 'fros') +
                           instr(lower(stb.wetter), 'chnee')     > 0 THEN 3
                      ELSE NULL END 		    AS wetter,
                stb.bewertungsart               AS bewertungsart,
                NULL                            AS bewertungstag,
                'DWA'                           AS datenart,
                stb.skdichtheit                 AS max_ZD,
                stb.skbetriebssicherheit        AS max_ZB,
                stb.skstandsicherheit           AS max_ZS,
                'QKan-STRAKAT-Import'                   AS kommentar,
                MakeLine(MakePoint(iif(:coordsFromRohr, stk.rw_rohranfang, stk.rw_gerinne_o),
                                   iif(:coordsFromRohr, stk.hw_rohranfang, stk.hw_gerinne_o), :epsg),
                         MakePoint(iif(:coordsFromRohr, stk.rw_rohrende, stk.rw_gerinne_u),
                                   iif(:coordsFromRohr, stk.hw_rohrende, stk.hw_gerinne_u), :epsg))
                                                                            AS geom
            FROM
                t_strakatkanal          AS stk
                LEFT JOIN strassen              ON stk.strassennummer = strassen.id
                JOIN t_strakatberichte  AS stb  ON stb.strakatid = stk.strakatid
                LEFT JOIN haltungen_untersucht AS hu
                ON hu.haltnam = stk.haltungsname AND
                   hu.schoben = stk.schacht_oben AND
                   hu.schunten = stk.schacht_unten AND
                   hu.untersuchtag = stb.datum AND
                   hu.untersuchrichtung = stb.untersuchungsrichtung
            WHERE  stk.laenge > 0.045 AND
                   stk.schachtnummer <> 0 AND
                   stb.geloescht = 0 AND
                   hu.pk IS NULL AND
                   stb.hausanschlid = '00000000-0000-0000-0000-000000000000' AND
                   (substr(stb.atv_kuerzel, 1, 1) <> 'D' OR substr(stb.atv_kuerzel, 2, 1) = '-') 
            GROUP BY stk.strakatid, stb.datum
        """

        params = {"epsg": self.epsg, "coordsFromRohr": QKan.config.strakat.coords_from_rohr}
        if not self.db_qkan.sql(sql, "strakat_import untersuchte Haltungen", params):
            raise Exception(f"{self.__class__.__name__}: Fehler bei ")

        self.db_qkan.commit()

        return True

    def _untersuchdat_haltung(self) -> bool:
        """Import der Haltungsschäden aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.haltungsschaeden:
            return True

        sql =  """
            WITH
            strassen AS (
                SELECT n1 AS id, kurz, trim(text) AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            )
            INSERT INTO untersuchdat_haltung (
                untersuchhal, schoben, schunten,
                id, untersuchtag,
                inspektionslaenge, bandnr, videozaehler, station, timecode,
                langtext, kuerzel, charakt1, charakt2, quantnr1, quantnr2,
                streckenschaden, streckenschaden_lfdnr,
                pos_von, pos_bis,
                foto_dateiname, film_dateiname,
                kommentar, ZD, ZB, ZS
            )
            SELECT
                stk.haltungsname                AS untersuchhal,
                stk.schacht_oben                AS schoben,
                stk.schacht_unten               AS schunten,
                NULL                            AS id, 
                stb.datum                       AS untersuchtag,
                stk.laenge                      AS inspektionslaenge,
                stb.bandnr                      AS bandnr,
                stb.videozaehler                AS videozaehler,
                stb.station_untersucher         AS station,
                NULL                            AS timecode,
                stb.atv_langtext                AS langtext,
                stb.atv_kuerzel                 AS kuerzel,
                stb.charakt1                    AS charakt1,
                stb.charakt2                    AS charakt2,                
                stb.quantnr1                    AS quantnr1,
                stb.quantnr2                    AS quantnr2,                
                stb.streckenschaden             AS streckenschaden,
                stb.fortsetzung                 AS streckenschaden_lfdnr,
                stb.pos_von                     AS pos_von, 
                stb.pos_bis                     AS pos_bis,
                    :ordner_bild  || replace(printf('\\band%d\\', 1000000 + stb.bandnr), 'band10', 'band')
                                  || stb.foto_dateiname || '.jpg'
                                                AS foto_dateiname,
                    :ordner_video || '\\'  || stb.foto_dateiname
                                  || ' von '  || stk.schacht_oben
                                  || ' nach ' || stk.schacht_unten
                                  || ' - '    || strassen.name  || '.mpg' 
                                                AS film_dateiname,
                stb.kommentar                   AS kommentar,
                stb.skdichtheit                 AS ZD,
                stb.skbetriebssicherheit        AS ZB,
                stb.skstandsicherheit           AS ZS
            FROM
                t_strakatkanal          AS stk
                JOIN t_strakatberichte  AS stb  ON stb.strakatid = stk.strakatid
                LEFT JOIN strassen              ON stk.strassennummer = strassen.id
                LEFT JOIN untersuchdat_haltung AS usd
                ON usd.untersuchhal =           stk.haltungsname AND
                   usd.schoben =                stk.schacht_oben AND
                   usd.schunten =               stk.schacht_unten AND
                   usd.untersuchtag =           stb.datum AND
                   usd.bandnr =                 stb.bandnr AND
                   usd.kuerzel =                stb.atv_kuerzel AND
                   usd.streckenschaden_lfdnr =   stb.fortsetzung AND
                   usd.langtext =               stb.atv_langtext  
            WHERE stk.laenge > 0.045 AND
                  stk.schachtnummer <> 0 AND
                  stb.geloescht = 0 AND
                  usd.pk IS NULL AND
                  stb.hausanschlid = '00000000-0000-0000-0000-000000000000' AND
                  (substr(stb.atv_kuerzel, 1, 1) <> 'D' OR substr(stb.atv_kuerzel, 2, 1) = '-')
        """

        params = {'ordner_bild': self.ordner_bild, 'ordner_video': self.ordner_video}

        if not self.db_qkan.sql(sql, "strakat_import Haltungsschäden", params):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Haltungsschäden")

        self.db_qkan.commit()

        self.db_qkan.setschadenstexte_haltungen()
        self.progress_bar.setValue(75)
        logger.debug("setschadenstexte_haltungen"),

        return True

    def _anschlussleitungen_untersucht(self) -> bool:
        """Import der Anschlussleitungen mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.hausanschlussschaeden:
            return True

        sql = """
            WITH stb AS (
                SELECT *
                FROM t_strakatberichte
                WHERE hausanschlid <> '00000000-0000-0000-0000-000000000000'
            ),
            lu AS (
            SELECT
                anschlusshalname                    AS leitnam,
                Trim(sha.haschob)                   AS schoben,
                Trim(sha.haschun)                   AS schunten,
                sha.rohrbreite                      AS hoehe,
                sha.rohrbreite                      AS breite,
                GLength(sha.geom)                   AS laenge,
                NULL                                AS id,
                stb.datum                           AS untersuchtag,
                stb.untersucher                     AS untersucher,
                stb.untersuchungsrichtung           AS untersuchrichtung,
                CASE WHEN instr(lower(stb.wetter), 'trock') + 
                           instr(lower(stb.wetter), 'kein Nied') > 0 THEN 1
                      WHEN instr(lower(stb.wetter), 'reg')       > 0 THEN 2
                      WHEN instr(lower(stb.wetter), 'fros') +
                           instr(lower(stb.wetter), 'chnee')     > 0 THEN 3
                      ELSE NULL END 		        AS wetter,
                NULL                                AS bewertungstag,
                'DWA'                               AS datenart,
                stb.skdichtheit                     AS max_ZD,
                stb.skbetriebssicherheit            AS max_ZB,
                stb.skstandsicherheit               AS max_ZS,
                'QKan-STRAKAT-Import'               AS kommentar,
                sha.geom                             AS geom
            FROM
                t_strakathausanschluesse   AS sha
                JOIN stb ON stb.nummer = sha.berichtnr
            WHERE stb.geloescht = 0 AND
                  sha.geloescht = 0
            )
            INSERT INTO anschlussleitungen_untersucht (
            leitnam, schoben, schunten, hoehe, breite, laenge, 
            id, untersuchtag, untersucher, untersuchrichtung, wetter,
            bewertungstag, datenart, max_ZD, max_ZB, max_ZS,
            kommentar, geom
            )
            SELECT
                lu.leitnam,
                lu.schoben,
                lu.schunten,
                lu.hoehe,
                lu.breite,
                lu.laenge,
                lu.id,
                lu.untersuchtag,
                lu.untersucher,
                lu.untersuchrichtung,
                lu.wetter,
                lu.bewertungstag,
                lu.datenart,
                lu.max_ZD,
                lu.max_ZB,
                lu.max_ZS,
                lu.kommentar,
                lu.geom
            FROM
                lu
                LEFT JOIN anschlussleitungen_untersucht AS la 
                USING (leitnam, schoben, schunten, untersuchtag, untersuchrichtung) 
            WHERE la.pk IS NULL
        """

        if not self.db_qkan.sql(sql, "strakat_import Anschlussleitungen untersucht"):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Anschlussleitungen untersucht")

        self.db_qkan.commit()

        return True

    def _untersuchdat_anschlussleitung(self) -> bool:
        """Import der Schäden an Anschlussleitungen aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.hausanschlussschaeden:
            return True

        sql = """
            WITH 
            strassen AS (
                SELECT n1 AS id, kurz, trim(text) AS name
                FROM t_reflists
                WHERE tabtyp = 'strasse'
            ),
            stb AS (
                SELECT *
                FROM t_strakatberichte
                WHERE hausanschlid <> '00000000-0000-0000-0000-000000000000'
            ),
            ua AS (
                SELECT
                    sha.anschlusshalname                    AS untersuchleit,
                    sha.haschob                             AS schoben,
                    sha.haschun                             AS schunten,
                    NULL                                    AS id, 
                    stb.datum                               AS untersuchtag,
                    NULL                                    AS inspektionslaenge,
                    stb.bandnr                              AS bandnr,
                    stb.videozaehler                        AS videozaehler,
                    stb.station_untersucher                 AS station,
                    NULL                                    AS timecode,
                    stb.atv_langtext                        AS langtext,
                    stb.atv_kuerzel                         AS kuerzel,
                    stb.charakt1                            AS charakt1,
                    stb.charakt2                            AS charakt2,                
                    stb.quantnr1                            AS quantnr1,
                    stb.quantnr2                            AS quantnr2,                
                    stb.streckenschaden                     AS streckenschaden,
                    stb.fortsetzung                         AS streckenschaden_lfdnr,
                    stb.pos_von                             AS pos_von, 
                    stb.pos_bis                             AS pos_bis,
                    :ordner_bild  || replace(printf('\\band%d\\', 1000000 + stb.bandnr), 'band10', 'band')
                                  || stb.foto_dateiname || '.jpg'
                                                            AS foto_dateiname,
                    :ordner_video || '\\'  || stb.foto_dateiname
                                  || ' von '  || stk.schacht_oben
                                  || ' nach ' || stk.schacht_unten
                                  || ' - '    || strassen.name  || '.mpg' 
                                                            AS film_dateiname,
                    stb.skdichtheit                         AS ZD,
                    stb.skbetriebssicherheit                AS ZB,
                    stb.skstandsicherheit                   AS ZS,
                    stb.kommentar                           AS kommentar
                FROM
                    t_strakathausanschluesse    AS sha
                    JOIN                           stb  ON stb.hausanschlid = sha.hausanschlid
                    JOIN t_strakatkanal         AS stk  ON stk.nummer = sha.anschlusshalnr
                    LEFT JOIN strassen                  ON stk.strassennummer = strassen.id
                WHERE stb.geloescht = 0
            )
            INSERT INTO untersuchdat_anschlussleitung (
                untersuchleit, schoben, schunten,
                id, untersuchtag,
                inspektionslaenge, bandnr, videozaehler, station, timecode,
                langtext, kuerzel, charakt1, charakt2, quantnr1, quantnr2,
                streckenschaden, streckenschaden_lfdnr,
                pos_von, pos_bis,
                foto_dateiname, film_dateiname,
                ZD, ZB, ZS, kommentar
            )
            SELECT 
                ua.untersuchleit, ua.schoben, ua.schunten,
                ua.id, ua.untersuchtag,
                ua.inspektionslaenge, ua.bandnr, ua.videozaehler, ua.station, ua.timecode,
                ua.langtext, ua.kuerzel, ua.charakt1, ua.charakt2, ua.quantnr1, ua.quantnr2,
                ua.streckenschaden, ua.streckenschaden_lfdnr,
                ua.pos_von, ua.pos_bis,
                ua.foto_dateiname, ua.film_dateiname,
                ua.ZD, ua.ZB, ua.ZS, ua.kommentar
            FROM ua
            LEFT JOIN untersuchdat_anschlussleitung AS ud
                USING (
                    untersuchleit, schoben, schunten, untersuchtag, bandnr, streckenschaden_lfdnr, kuerzel, 
                    langtext
                )
            WHERE ud.pk IS NULL
        """
        params = {'ordner_bild': self.ordner_bild, 'ordner_video': self.ordner_video}

        if not self.db_qkan.sql(sql, "strakat_import Untersuchungsdaten Anschlussleitungen", params):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Untersuchungsdaten Anschlussleitungen")

        self.db_qkan.commit()

        self.db_qkan.setschadenstexte_anschlussleitungen()
        self.progress_bar.setValue(100)
        logger.debug("setschadenstexte_anschlussleitungen"),

        return True

































