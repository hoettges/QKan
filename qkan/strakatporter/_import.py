import os
import re
from struct import unpack
from typing import Iterator
from pathlib import Path

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis, QgsGeometry, QgsPoint
from qkan import QKan
from qkan.config import ClassObject
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError, QkanUserError
from qkan.tools.k_schadenstexte import Schadenstexte

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
    bandnr: int = 0
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
    strangnr: int = 0
    betriebspunkt: int = 0
    strakatid: str = ""


class ImportTask():
    def __init__(
        self,
        db_qkan: DBConnection,
    ):
        # all parameters (except db_qkan) are passed via QKan.config
        self.db_qkan = db_qkan
        self.allrefs = QKan.config.check_import.allrefs
        self.epsg = QKan.config.epsg
        self.strakatdir = QKan.config.strakat.import_dir
        self.projectfile = QKan.config.project.file
        self.db_name = QKan.config.database.qkan
        self.richtung = QKan.config.xml.richt_choice
        self.kriterienschaeden = QKan.config.zustand.kriterienschaeden
        self.maxdiff = QKan.config.strakat.maxdiff

        self.db_qkan.loadmodule('strakatporter')

    def run(self) -> bool:

        self.iface = QKan.instance.iface

        pathfull = Path(QKan.config.fotoPathCurrent)
        if QKan.config.fotoRootPath != '':
            pathroot = Path(QKan.config.fotoRootPath)
            try:
                self.ordner_bild = str(pathfull.relative_to(pathroot))
            except ValueError as err:
                logger.error_user('Der Wurzelpfad zu den Fotos passt nicht zum ausgewählten Verzeichnis.\n'
                                  'Bitte in Maske "Optionen" korrigieren')
                return False
        else:
            self.ordner_bild = str(pathfull)

        pathfull = Path(QKan.config.videoPathCurrent)
        if QKan.config.videoRootPath != '':
            pathroot = Path(QKan.config.videoRootPath)
            try:
                self.ordner_video = str(pathfull.relative_to(pathroot))
            except ValueError as err:
                logger.error_user('Der Wurzelpfad zu den Videos passt nicht zum ausgewählten Verzeichnis.\n'
                                  'Bitte in Maske "Optionen" korrigieren')
                return False
        else:
            self.ordner_video = str(pathfull)

        # Create progress bar
        self.progress_bar = QProgressBar(self.iface.messageBar())
        self.progress_bar.setRange(0, 100)

        self.status_message = self.iface.messageBar().createMessage(
            "", "Import aus STRAKAT läuft. Bitte warten..."
        )
        self.status_message.layout().addWidget(self.progress_bar)
        self.iface.messageBar().pushWidget(self.status_message, Qgis.MessageLevel.Info, 60)
        self.progress_bar.setValue(0)
        logger.debug("progress_bar initialisiert")

        result = all(
            [
                self._strakat_kanaltabelle(), self.progress_bar.setValue(5),            logger.debug("_strakat_kanaltabelle"),
                self._strakat_reftables(), self.progress_bar.setValue(10),              logger.debug("_strakat_reftables"),
                self._reftables(), self.progress_bar.setValue(15),                      logger.debug("_reftables"),
                self._schaechte(), self.progress_bar.setValue(20),                      logger.debug("_schaechte"),
                self._haltungen(), self.progress_bar.setValue(25),                      logger.debug("_haltungen"),
                self._symbole(),  self.progress_bar.setValue(29),                       logger.debug("_symbole"),
                self._adapt_refvals(),                                                  logger.debug("_adapt_refvals"),
                self._strakat_hausanschl(), self.progress_bar.setValue(30),             logger.debug("_strakat_hausanschl"),
                self._anschlussleitungen(), self.progress_bar.setValue(35),             logger.debug("_anschlussleitungen"),
                self._anschlussschaechte(), self.progress_bar.setValue(38),             logger.debug("_anschlussschaechte"),
                self._strakat_berichte(), self.progress_bar.setValue(40),               logger.debug("_strakat_berichte"),
                self._schachtuntersuchungen(), self.progress_bar.setValue(45),          logger.debug("_schachtuntersuchungen"),
                self._haltungsuntersuchungen(), self.progress_bar.setValue(60),         logger.debug("_haltungsuntersuchungen"),
                self._anschlussleitungsuntersuchungen(), self.progress_bar.setValue(80),  logger.debug("_anschlussleitungsuntersuchungen"),
            ]
        )

        self.progress_bar.setValue(100)
        self.status_message.setText("Fertig! STRAKAT-Import abgeschlossen.")

        self.iface.messageBar().clearWidgets()

        return result

    def _strakat_kanaltabelle(self) -> bool:
        """Import der Kanaldaten aus der STRAKAT-Datei 'kanal.rwtopen', entspricht ACCESS-Tabelle 'KANALTABELLE'
        """

        if not self.db_qkan.sqlyml(
            sqlnam='strakat_drop_t_strakatkanal',
        ):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen

        # Erstellung Tabelle t_strakatkanal
        if not self.db_qkan.sqlyml(
            sqlnam= 'strakat_create_t_strakatkanal',
            stmt_category='create_t_strakatkanal',
        ):
            logger.error("Erstellen der Tabelle 't_strakatkanal' schlug fehlt")
            raise QkanDbError

        parameters = (self.epsg,)

        if not self.db_qkan.sqlyml(
            sqlnam='strakat_addgeometrycolumn_geom',
            parameters=parameters,
        ):
            logger.error_code("Geometrie in t_strakatkanal konnte nicht hinzugefügt werden")
            raise QkanDbError

        if not self.db_qkan.sqlyml(
            sqlnam='strakat_addgeometrycolumn_geop',
            parameters=parameters,
        ):
            logger.error_code("Geometrie in t_strakatkanal konnte nicht hinzugefügt werden")
            raise QkanDbError

        if not self.db_qkan.sqlyml(
            sqlnam='strakat_createspatialindex_geom',
        ):
            logger.error_code("SpatialIndex in t_strakatkanal konnte nicht hinzugefügt werden")
            raise QkanDbError

        if not self.db_qkan.sqlyml(
            sqlnam='strakat_createspatialindex_geop',
        ):
            logger.error_code("SpatialIndex in t_strakatkanal konnte nicht hinzugefügt werden")
            raise QkanDbError

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

                    schacht_oben = b[172:b[172:187].find(b'\x00')+172].decode('latin_1').strip()
                    haltungsname = b[187:b[187:202].find(b'\x00')+187].decode('latin_1').strip()

                    (
                        rohrbreite_v, rohrbreite_g, rohrhoehe___v, rohrhoehe___g,
                        wandstaerke_v, wandstaerke_g, ersatzdu___v, ersatzdu___g,
                        flaechenfactor_v, flaechenfactor_g, umfangsfactor_v, umfangsfactor_g,
                        hydr__radius_v, hydr__radius_g
                    ) = unpack('ffffffffffffff', b[116:172])
                    if not isinstance(rohrhoehe___g, float):
                        rohrhoehe___g = rohrbreite_g
                    if not isinstance(rohrhoehe___v, float):
                        rohrhoehe___v = rohrbreite_v

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

                    strangnr = unpack('h', b[882:884])[0]
                    betriebspunkt = unpack('h', b[902:904])[0]

                    (
                        h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                    ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[917:933])]
                    strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                    schacht_unten = b[965:b[965:980].find(b'\x00')+965].decode('latin_1').strip()

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
                        strangnr=strangnr,
                        betriebspunkt=betriebspunkt,
                        strakatid=strakatid,
                    )
                else:
                    raise Exception(f'{self.__class__.__name__}:Programmfehler: Einlesen der Datei "kanal.rwtopen"'
                                    f' wurde nach 1000000 Datensätze abgebrochen!"')

        params = ()                           # STRAKAT data stored in tuple of dicts for better performance
        # with sql-statement executemany
        logger.debug("{__name__}: Berichte werden gelesen und in data gespeichert ...")

        for _kanal in _iter():
            data = {
                'nummer': _kanal.nummer,
                'rw_gerinne_o': _kanal.rw_gerinne_o, 'hw_gerinne_o': _kanal.hw_gerinne_o,
                'rw_gerinne_u': _kanal.rw_gerinne_u, 'hw_gerinne_u': _kanal.hw_gerinne_u,
                'rw_rohranfang': _kanal.rw_rohranfang, 'hw_rohranfang': _kanal.hw_rohranfang,
                'rw_rohrende': _kanal.rw_rohrende, 'hw_rohrende': _kanal.hw_rohrende,
                'zuflussnummer1': _kanal.zuflussnummer1, 'zuflussnummer2': _kanal.zuflussnummer2,
                'zuflussnummer3': _kanal.zuflussnummer3, 'zuflussnummer4': _kanal.zuflussnummer4,
                'zuflussnummer5': _kanal.zuflussnummer5, 'zuflussnummer6': _kanal.zuflussnummer6,
                'zuflussnummer7': _kanal.zuflussnummer7, 'zuflussnummer8': _kanal.zuflussnummer8,
                'abflussnummer1': _kanal.abflussnummer1, 'abflussnummer2': _kanal.abflussnummer2,
                'abflussnummer3': _kanal.abflussnummer3, 'abflussnummer4': _kanal.abflussnummer4,
                'abflussnummer5': _kanal.abflussnummer5,
                'schacht_oben': _kanal.schacht_oben, 'schacht_unten': _kanal.schacht_unten,
                'haltungsname': _kanal.haltungsname,
                'rohrbreite_v': _kanal.rohrbreite_v, 'rohrhoehe___v': _kanal.rohrhoehe___v,
                'flaechenfactor_v': _kanal.flaechenfactor_v,
                'deckel_oben_v': _kanal.deckel_oben_v, 'deckel_unten_v': _kanal.deckel_unten_v,
                'sohle_oben___v': _kanal.sohle_oben___v, 'sohle_unten__v': _kanal.sohle_unten__v,
                's_sohle_oben_v': 0.0,
                'sohle_zufluss1': _kanal.sohle_zufluss1, 'sohle_zufluss2': _kanal.sohle_zufluss2,
                'sohle_zufluss3': _kanal.sohle_zufluss3, 'sohle_zufluss4': _kanal.sohle_zufluss4,
                'sohle_zufluss5': _kanal.sohle_zufluss5, 'sohle_zufluss6': _kanal.sohle_zufluss6,
                'sohle_zufluss7': _kanal.sohle_zufluss7, 'sohle_zufluss8': _kanal.sohle_zufluss8,
                'kanalart': _kanal.kanalart, 'profilart_v': _kanal.profilart_v,
                'material_v': _kanal.material_v,
                'e_gebiet': _kanal.e_gebiet, 'strassennummer': _kanal.strassennummer,
                'schachtnummer': _kanal.schachtnummer, 'schachtart': _kanal.schachtart,
                'berichtsnummer': _kanal.berichtsnummer,
                'laenge': _kanal.laenge, 'schachtmaterial': _kanal.schachtmaterial,
                'oberflaeche': _kanal.oberflaeche,
                'baujahr': _kanal.baujahr, 'wasserschutz': _kanal.wasserschutz, 'eigentum': _kanal.eigentum,
                'naechste_halt': _kanal.naechste_halt, 'rueckadresse': _kanal.rueckadresse,
                'strangnr': _kanal.strangnr, 'betriebspunkt': _kanal.betriebspunkt,
                'strakatid': _kanal.strakatid
            }
            params += (data,)

        logger.debug("{__name__}: Berichte werden in temporäre STRAKAT-Tabellen geschrieben ...")

        if not self.db_qkan.sqlyml(
            sqlnam='strakat_kanaltabelle',
            stmt_category="strakat_import STRAKAT Kanaltabelle",
            parameters=params,
            many=True
        ):
            raise Exception(f'{self.__class__.__name__}:Fehler beim Lesen der Datei "kanal.rwtopen"')

        sqlnams = [
            'strakat_update_geom',
            'strakat_update_geop',
            # 'strakat_delete_schnr0',              alle gelöschten Kanäle entfernen
        ]

        params = {"epsg": self.epsg, "coordsFromRohr": False}   # für Netzlogik sind Gerinneschnittpunkte relevant
        for sqlnam in sqlnams:
            if not self.db_qkan.sqlyml(
                sqlnam=sqlnam,
                stmt_category="strakat_import Geoobjekte t_strakatkanal",
                parameters=params,
            ):
                logger.error_code('Fehler beim Erzeugen der Geoobjekte t_strakatkanal')
                raise QkanDbError

        # Kopie von t_strakatkanal, um inkonsistente Schachtbezeichnungen nachvollziehbar zu machen
        # if not self.db_qkan.sqlyml(
            # sqlnam='strakat_copy2ori',
            # stmt_category="strakat_import Kopie von t_strakatkanal"
        # ):
            # logger.error_code('Fehler bei strakat_import Kopie von t_strakatkanal')
            # raise QkanDbError

        # Bereinigung inkonsistenter Schachtbezeichnungen

        # 1. Übertragen des schacht_oben auf Kanäle ohne schachtoben oder mit einem schachtoben,
        #    der nicht mit anderen Schachtoben übereinstimmt.
        sqlnams = [
            "strakat_prep1",
            "strakat_prep2",
            "strakat_prep3",
            "strakat_prep4",
            "strakat_prep5",
            "strakat_prep6",
            # "strakat_prep7",
            # "strakat_prep8",
            # "strakat_prep9",
        ]

        params = {"epsg": self.epsg, "maxdiff": self.maxdiff}
        for sqlnam in sqlnams:
            if not self.db_qkan.sqlyml(
                    sqlnam=sqlnam,
                    stmt_category="strakat_import Korrektur Schachtnamen t_strakatkanal",
                    parameters=params
            ):
                raise Exception(f'{self.__class__.__name__}:Fehler bei der Korrektur der Schachtnamen t_strakatkanal')

        self.db_qkan.commit()

        return True

    def _strakat_reftables(self) -> bool:
        """Import der STRAKAT-Referenztabellen aus der STRAKAT-Datei 'referenztabelle.strakat'
        """

        # Erstellung Tabelle t_reflists. Diese Tabelle enthält die STRAKAT-Rohdaten aller Referenztabellen.
        # Diese werden in den einzelnen Importen mittels Filter auf die Spalte "tabtyp" spezifiziert und eingebunden.
        if not self.db_qkan.fetchone():
            sqlnam = """strakat_create_t_reflists"""

            if not self.db_qkan.sqlyml(
                sqlnam=sqlnam,
                stmt_category='Erstellung Tabelle "t_reflists"'
            ):
                logger.error_code('Fehler bei der Erstellung der Tabelle t_reflists')
                raise QkanDbError

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

                try:
                    kurz = b[10:b[10:26].find(b'\x00')+10].decode('latin_1')
                except UnicodeDecodeError:
                    _ = b[10:b[10:26].find(b'\x00')+10]
                    logger.error_code(f"Fehlerhaftes Zeichen in Block {n}: {_}")
                try:
                    text = b[26:b[26:128].find(b'\x00')+26].decode('latin_1')
                except UnicodeDecodeError:
                    _ = b[10:b[10:26].find(b'\x00')+10]
                    logger.error_code("Fehlerhaftes Zeichen in Block {n}: {_}")

                params = {'tabtyp': tabtyp, 'id': id,
                          'n1': n1, 'n2': n2, 'n3': n3, 'n4': n4, 'n5': n5,
                          'kurz': kurz, 'text': text}

                if not self.db_qkan.sqlyml(
                        sqlnam = "strakat_add_t_reflists",
                        stmt_category= "strakat_import Referenztabellen",
                        parameters=params):
                    raise Exception(f'{self.__class__.__name__}:Fehler beim Lesen der Datei "system/referenztabelle.strakat"')
            else:
                raise Exception(f'{self.__class__.__name__}:Programmfehler: Einlesen der Datei '
                                f'"system/referenztabelle.strakat" wurde nicht ordnungsgemäß abgeschlossen!"')

        self.db_qkan.commit()

        return True

    def _strakat_hausanschl(self) -> bool:
        """Import der Hausanschlussdaten aus der STRAKAT-Datei 'haus.rwtopen', entspricht ACCESS-Tabelle 'HAUSANSCHLUSSTABELLE'
        """

        sqlnam = "strakat_02"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category='Löschung Tabelle "t_strakathausanschluesse wegen Neuanlage"',
        ):
            raise Exception(f'{self.__class__.__name__}: Fehler beim Löschen der Tabelle t_strakathausanschluesse')

        sqlnam = "strakat_03"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category='Erstellung Tabelle "t_strakathausanschluesse"',
        ):
            return False

        sqlnams = [
            "strakat_addgeom_t_strakathausanschluesse",
            "strakat_index_t_strakathausanschluesse",
        ]
        parameters = {'epsg': self.epsg}
        for sqlnam in sqlnams:
            if not self.db_qkan.sqlyml(
                sqlnam=sqlnam,
                stmt_category="strakat_import ergänze geom n t_strakathausanschluesse",
                parameters=parameters,
            ):
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
                zlis = list(unpack('fffffffff', b[180:216]))
                # d1, d2, d3, d4, d5, d6, d7, d8, d9 = unpack('fffffffff', b[220:256])

                # Erste x-Koordinate = 0 auf alle folgenden übertragen, weil in STRAKAT manchmal
                # in den hinteren Spalten noch Reste von alten Koordinaten stehen
                # In QKan (s. u.) werden alle Koordinaten mit xi < 0 unterdrückt
                for i in range(2, 8):
                    if xlis[i] < 1:
                        xlis[i+1] = -xlis[i+1]      # für nachträgliche Kontrolle

                (x1, x2, x3, x4, x5, x6, x7, x8, x9) = xlis
                (y1, y2, y3, y4, y5, y6, y7, y8, y9) = ylis
                (z1, z2, z3, z4, z5, z6, z7, z8, z9) = zlis

                # Hausanschlusslinie erzeugen
                ptlis = []
                for x, y, z in zip(xlis, ylis, zlis):
                    if x < 1 or y < 1:
                        break
                    ptlis.append(QgsPoint(x, y))
                    xanf = x                            # enthält nach Ende der Schleife den letzten gültigen Wert
                    yanf = y
                    zanf = z
                if len(ptlis) <= 1:
                    continue
                ptlis.reverse()                         # STRAKAT beginnt mit den Punkten an der Haltung
                geomwkb = QgsGeometry.fromPolyline(ptlis).asWkb()

                sohleoben = z1
                sohleunten = zanf

                rohrbreite = unpack('f', b[220:224])[0]  # nur erste von 9 Rohrbreiten lesen

                hausnummer = b[288:b[288:299].find(b'\x00')+288].decode('latin_1').strip()

                berichtnr = unpack('i', b[299:303])[0]
                anschlusshalnr = unpack('i', b[303:307])[0]
                nextnum = unpack('i', b[311:315])[0]

                geloescht = unpack('b', b[317:318])[0]

                anschlussschob = b[326:b[326:362].find(b'\x00')+326].decode('latin_1').strip()    # vermutlich kürzer als 36 Zeichen
                anschlussschun = b[362:b[362:398].find(b'\x00')+362].decode('latin_1').strip()    # vermutlich kürzer als 36 Zeichen

                urstation = unpack('f', b[515:519])[0]

                strassennummer = unpack('h', b[597:599])[0]

                anschlusshalname = b[611:b[611:631].find(b'\x00')+611].decode('latin_1').strip()
                if anschlusshalname == '':
                    if anschlussschob != '':
                        anschlusshalname = anschlussschob
                    else:
                        anschlusshalname = hausnummer

                (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                 ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[524:540])]
                strakatid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'
                (h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, ha, hb, hc, hd, he, hf
                 ) = [hex(z).replace('0x', '0')[-2:] for z in unpack('B' * 16, b[540:556])]
                hausanschlid = f'{h3}{h2}{h1}{h0}-{h5}{h4}-{h7}{h6}-{h8}{h9}-{ha}{hb}{hc}{hd}{he}{hf}'

                # gelöschte Datensätze überspringen
                # if geloescht == 1:
                #     continue

                params = {
                    'nummer': nummer, 'nextnum': nextnum,
                    'x1': x1, 'x2': x2, 'x3': x3,
                    'x4': x4, 'x5': x5, 'x6': x6,
                    'x7': x7, 'x8': x8, 'x9': x9,
                    'y1': y1, 'y2': y2, 'y3': y3,
                    'y4': y4, 'y5': y5, 'y6': y6,
                    'y7': y7, 'y8': y8, 'y9': y9,
                    'z1': z1, 'z2': z2, 'z3': z3,
                    'z4': z4, 'z5': z5, 'z6': z6,
                    'z7': z7, 'z8': z8, 'z9': z9,
                    'xanf': xanf, 'yanf': yanf, 'zanf': zanf,
                    'rohrbreite': rohrbreite,
                    'berichtnr': berichtnr,
                    'anschlusshalnr': anschlusshalnr, 'anschlusshalname': anschlusshalname,
                    'anschlussschob': anschlussschob, 'anschlussschun': anschlussschun,
                    'sohleoben': sohleoben, 'sohleunten': sohleunten,
                    'urstation': urstation, 'geloescht': geloescht,
                    'strassennummer': strassennummer, 'hausnummer': hausnummer,
                    'strakatid': strakatid, 'hausanschlid': hausanschlid, 'geomwkb': geomwkb, "epsg": self.epsg,
                }

                sqlnam = "strakat_04"

                if not self.db_qkan.sqlyml(
                    sqlnam=sqlnam,
                    stmt_category="strakat_import Hausanschlüsse",
                    parameters=params,
                ):
                    raise Exception(f'{self.__class__.__name__}: Fehler beim Lesen der Datei "haus.rwtopen"')
            else:
                raise Exception(f'{self.__class__.__name__}: Programmfehler: Einlesen der Datei kanal.rwtopen wurde'
                                f' nicht ordnungsgemäß abgeschlossen!"')

        # Eindeutige Werte in anschlusshalnam
        sqlnam = "strakat_05"

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Eindeutige Bezeichnungen für Hausanschlüsse",
         ):
            raise Exception(f'{self.__class__.__name__}: Fehler beim eindeutigen Bezeichnungen für Hausanschlüsse"')

        self.db_qkan.commit()

        return True

    def _anschlussschaechte(self) -> bool:
        """Erzeugen der zusätzlichen Schächte aus Anschlussleitungen"""
        pass
        return True

    def _strakat_berichte(self) -> bool:
        """Import der Schadensdaten aus der STRAKAT-Datei 'ENBericht.rwtopen', entspricht ACCESS-Tabelle 'SCHADENSTABELLE'
        """
        if not (QKan.config.check_import.haltungsschaeden or
            QKan.config.check_import.schachtschaeden or
            QKan.config.check_import.hausanschlussschaeden
        ):
            return True

        # Erstellung Tabelle t_strakatberichte
        sqlnam = "strakat_06"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
                stmt_category='Löschung Tabelle "t_strakatberichte wegen Neuanlage"',
        ):
            raise Exception(f'{self.__class__.__name__}: Fehler beim Löschen der Tabelle t_strakatberichte')

        sqlnam = "strakat_07"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category='Erstellung Tabelle "t_strakatberichte"',
        ):
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
                    datum = b[0:10].decode('latin_1')
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
                    untersucher = b[11:b[11:31].find(b'\x00') + 11].decode('latin_1').strip()
                    ag_kontrolle = b[31:b[31:46].find(b'\x00') + 31].decode('latin_1').strip()
                    fahrzeug = b[46:b[46:57].find(b'\x00') + 46].decode('latin_1').strip()
                    inspekteur = b[58:b[58:74].find(b'\x00') + 58].decode('latin_1').strip()
                    wetter = b[73:b[73:88].find(b'\x00') + 73].decode('latin_1').strip()

                    atv149 = unpack('f', b[90:94])[0]

                    fortsetzung = unpack('I', b[103:107])[0]
                    station_gegen = round(unpack('d', b[107:115])[0], 3)
                    station_untersucher = round(unpack('d', b[115:123])[0], 3)

                    atv_kuerzel = b[123:b[123:134].find(b'\x00') + 123].decode('latin_1').strip()
                    if not atv_kuerzel:
                        continue
                    atv_langtext = b[134:b[134:295].find(b'\x00') + 134].decode('latin_1').strip()
                    sandatum = b[284:294].decode('latin_1')
                    geloescht = unpack('b', b[296:297])[0]
                    schadensklasse = unpack('B', b[295:296])[0]
                    untersuchungsrichtung = unpack('B', b[297:298])[0]
                    bandnr_ = b[301:b[301:320].find(b'\x00') + 301].decode('latin_1').strip()
                    try:
                        bandnr = int(bandnr_)
                    except:
                        bandnr = 0
                    videozaehler = unpack('I', b[320:324])[0]
                    try:
                        foto_dateiname = f'{bandnr:0>3d}{int(videozaehler):0>5d}'
                    except BaseException as err:
                        logger.debug(f'Datenfehler: {bandnr=}, {videozaehler=}')
                        foto_dateiname = '00000000'

                    wert8 = unpack('B', b[298:299])                         # STRAKAT: Bewertungsart
                    if wert8 == 4:
                        bewertungsart = 'DWA'
                    else:
                        bewertungsart = 'ATV'
                    pos_von, pos_bis = unpack('BB', b[366:368])             # STRAKAT: von/bis Uhr
                    sanierung = b[402:b[402:413].find(b'\x00') + 402].decode('latin_1').strip()
                    atv143 = unpack('f', b[430:434])[0]

                    quantnr1, quantnr2 = unpack('bb', b[434:436])
                    streckenschaden = b[436:b[436:437].find(b'\x00') + 436].decode('latin_1').strip()
                    charakt1 = b[438:b[438:449].find(b'\x00') + 438].decode('latin_1').strip()
                    charakt2 = b[449:b[449:].find(b'\x00') + 449].decode('latin_1').strip()

                    anmerkung = b[463:b[463:715].find(b'\x00') + 463].decode('latin_1').strip()
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

        sqlnam = "strakat_08"
        if not self.db_qkan.sqlyml(
                sqlnam=sqlnam,
                stmt_category="strakat_import Bericht",
                parameters=params,
                many=True,
        ):
            raise Exception(f'{self.__class__.__name__}: Fehler beim Lesen der Datei ENBericht.rwtopen')

        self.db_qkan.commit()

        logger.debug("{__name__}: Berichte werden in QKan-Tabellen geschrieben ...")

        return True

    def _reftables(self) -> bool:
        """Referenztabellen füllen"""

        # Hinweis: 'None' bewirkt beim Import eine Zuordnung unabhängig vom Wert

        # Referenztabelle Entwässerungsarten

        sqlnam = "strakat_09"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste entwaesserungsarten",
        ):
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
        sqlnam = "strakat_10"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste haltungstypen",
            parameters=params,
            many=True,
        ):
            return False

        # Referenztabelle Rohrprofile

        sqlnam = "strakat_11"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste profile",
        ):
            return False

        # Referenztabelle Entwässerungsgebiete

        sqlnam = "strakat_12"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste profile",
        ):
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
        sqlnam = "strakat_13"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste pumpentypen",
            parameters=params,
            many=True,
        ):
            return False

        # Referenztabelle Untersuchungsrichtung

        daten = [
            ('in Fließrichtung', '0', 'automatisch hinzugefügt'),
            ('gegen Fließrichtung', 'U', 'automatisch hinzugefügt'),
        ]

        params = [el + (el[0],) for el in daten]         # repeat last argument for WHERE statement
        sqlnam = "strakat_14"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste untersuchrichtung",
            parameters=params,
            many=True,
        ):
            return False

        # Erstellung Tabelle t_mapper_untersuchrichtung
        sqlnam = "strakat_15"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="Prüfen, ob temporäre Tabelle 't_mapper_untersuchrichtung', vorhanden ist"
        ):
            return False                                        # Abbruch weil Anfrage fehlgeschlagen

        if not self.db_qkan.fetchone():
            sqlnam = "strakat_16"
            if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category='Erstellung Tabelle "t_mapper_untersuchrichtung"'
        ):
                return False

        # Liste enthält nur Schachtarten, die nicht 'Schacht' und dabei 'vorhanden' sind (einschließlich 1: 'NS Normalschacht')
        daten = [
            (0,  'in Fließrichtung'),
            (1,  'gegen Fließrichtung'),
        ]
        sqlnam = "strakat_17"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste t_mapper_untersuchrichtung",
            parameters=daten,
            many=True
        ):
            return False

        # Simulationsstatus
        # In STRAKAT gibt es keinen Simulationsstatus. Allerdings enthalten einige Referenzwerte aus der
        # Referenztabelle "Kanalart" Werte, die in QKan in die Tabelle Simulationsstatus übertragen werden müssen.

        sqlnam = "strakat_18"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Referenzliste simulationsstatus",
        ):
            return False

        # Referenztabelle Eigentum

        sqlnam = "strakat_19"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Referenzliste eigentum",
        ):
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
        # self.db_qkan._adapt_reftable('entwaesserungsarten')           # funktionierte sowieso nicht, jh 01.12.2025

        daten = [
            ('Regenwasser', 'R', 'Regenwasser', 1, 2, 'R', 'KR'),
            ('Schmutzwasser', 'S', 'Schmutzwasser', 2, 1, 'S', 'KS'),
            ('Mischwasser', 'M', 'Mischwasser', 0, 0, 'M', 'KM'),
            ('RW Druckleitung', 'RD', 'RW Druckleitung', 1, 2, None, 'DR'),
            ('SW Druckleitung', 'SD', 'RW Druckleitung', 2, 1, None, 'DS'),
            ('MW Druckleitung', 'MD', 'RW Druckleitung', 0, 0, None, 'DW'),
            ('Rinnen/Gräben', 'GR', 'Rinnen/Gräben', None, None, None, None),
            ('stillgelegt', 'SG', 'stillgelegt', None, None, None, None),
        ]

        # Ergänzen der Standarddatensätze, falls nicht vorhanden
        daten = [el + (el[0],) for el in daten]         # repeat last argument for ? after WHERE in SQL
        sqlnam = "strakat_20"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="Isybau Referenzliste entwaesserungsarten",
            parameters=daten,
            many=True
        ):
            return False
        #
        # # Ergänzen weiterer Kennnummern in speziellen Datensätzen
        # params = [(ds[2], ds[3], ds[4], ds[5], ds[6], ds[0],) for ds in daten]           # umsortieren
        # sql = """UPDATE entwaesserungsarten
        #          SET he_nr = ?, kp_nr = ?, m150 = ?, isybau = ?, bemerkung = ?
        #          WHERE bezeichnung = ?"""
        # if not self.db_qkan.sql(sql, "strakat_import Referenzliste entwaesserungsarten", params, many=True):
        #     return False

        # Simulationsstatus

        # Bezeichnungen in Referenztabelle und bezogenen Tabellen (über trigger) an QKan-Standard anpassen
        # self.db_qkan._adapt_reftable('simulationsstatus')           # funktionierte sowieso nicht, jh 01.12.2025

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
        sqlnam = "strakat_21"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "Ergänzung Referenzliste simulationsstatus",
            parameters=daten,
            many=True
        ):
            return False

        # Ergänzen weiterer Kennnummern in speziellen Datensätzen
        params = [(ds[2], ds[3], ds[4], ds[5], ds[6], ds[7], ds[8], ds[0],) for ds in daten]           # umsortieren
        sqlnam = "strakat_22"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Referenzliste simulationsstatus",
            parameters=params,
            many=True
        ):
            return False

    def _schaechte(self) -> bool:
        """Import der Schächte aus der STRAKAT-Tabelle KANALTABELLE"""

        if not QKan.config.check_import.schaechte:
            return True

        sqlnam = "strakat_23"
        params = {"epsg": self.epsg}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category="strakat_import Schächte",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler in strakat_import Schächte")

        self.db_qkan.commit()

        return True

    def _symbole(self) -> bool:
        """Import aller STRAKAT-Schächte, die in Wirklichkeit Symbole sind"""

        if not QKan.config.check_import.symbole:
            return True

        sqlnam = "strakat_24"
        params = {"epsg": self.epsg}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Symbole",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler in strakat_import Symbole")

        sqlnam = "strakat_25"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Symbolkatalog",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler in strakat_import Symbolkatalog")

        self.db_qkan.commit()

        return True

    def _haltungen(self) -> bool:
        """Import der Haltungen aus der STRAKAT-Tabelle KANALTABELLE"""

        if not QKan.config.check_import.haltungen:
            return True

        sqlnam = "strakat_haltungen"

        params = {"epsg": self.epsg, "coordsFromRohr": QKan.config.strakat.coords_from_rohr}

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Haltungen (1)",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler in strakat_import Haltungen (1)")

        self.db_qkan.commit()

        # Zusammengesetzte Haltungen werden neu erzeugt und überschreiben das geom-Objekt der jeweiligen Anfanghaltung
        # Erkennungsmerkmal: 1. Kanal hat Schachtart.n4 <>0, alle weiteren haben die Schachtart.n4 0.
        # Einschränkung: Als 1. Kanal zählen nur Kanäle, die nicht gemeinsam mit einem anderen Kanal mit schachtart.n4 = 0
        # in einen Schacht einleiten. Zusätzlich müssen aufeinander folgende Teile in folgenden Attribute
        # identisch sein: eigentum, kanalart

        def _getstraenge():
            """Liest alle zusammengesetzten Kanäle (Kriterium: knotenart.n4 = 0 zuzüglich oberhalb liegendem Kanal)"""
            sqlnam = "strakat_straenge"

            params = {"coordsFromRohr": QKan.config.strakat.coords_from_rohr}
            if not self.db_qkan.sqlyml(
                sqlnam=sqlnam,
                stmt_category='get_straenge',
                parameters=params,
            ):
                raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Haltungen (2)")

            stnet = self.db_qkan.fetchall()        # haltnam, schob, schun, strangnr, xob, yob, xun, yun

            idxschob = {ds[1]: ds for ds in stnet}
            idxschun = {ds[2]: ds for ds in stnet}

            # Schleife bis alle Haltungsteilstücke verarbeitet sind
            while len(idxschob) > 0:
                gplis = []  # Knotenpunkte einer zusammengesetzten Haltung
                # Anfang finden
                for anf in idxschob:
                    # Anfang bei Strangnr = 1
                    if idxschob.get(anf)[3] == 1:
                        break
                else:
                    logger.debug('\nInhalt von idxschob:\nschacht_unten: haltungsname, schacht_oben, schacht_unten, '
                                 'xob, yob, xun, yun')
                    errormsg = '\n'.join([f'{anf}: {idxschob.get(anf, "Error: anf nicht gefunden")}' for anf in idxschob])
                    logger.debug(errormsg + '\n')
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
                    QkanUserError(errormsg)
                # Kanal verfolgen und jedes Teilstück entnehmen
                haltnam = idxschob[anf][0]
                node = anf  # Anfang übernehmen
                xend, yend = None, None
                while True:
                    ds = idxschob.get(node)
                    if ds is None:
                        # Strang hat nur 1 Element ...
                        gplis.append([xend, yend])  # Endkoordinate
                        break
                    gplis.append([ds[4], ds[5]])  # Anfangskoordinate
                    xend, yend = (ds[6], ds[7])   # nur für den Fall, dass Strang nur 1 Element hat (s. o.)
                    next = idxschob.get(node)[2]  # Schacht unten als nächsten Schacht übernehmen
                    if idxschob.get(node)[3] == 3:
                        # Ende gefunden
                        gplis.append([ds[6], ds[7]])  # Endkoordinate
                        del idxschob[node]
                        break
                    del idxschob[node]
                    node = next

                ptlis = [QgsPoint(x, y) for x, y in gplis]
                geom = QgsGeometry.fromPolyline(ptlis)

                yield haltnam, geom.asWkb()

        for strang_haltnam, strang_wkb in _getstraenge():
            params = {"geom": strang_wkb, "haltnam": strang_haltnam, "epsg": self.epsg}
            sqlnam = "strakat_28"
            if not self.db_qkan.sqlyml(
                sqlnam=sqlnam,
                stmt_category= "strakat_import Zusammensetzen der Kanalstränge",
                parameters=params,
            ):
                raise Exception(f"{self.__class__.__name__}: Fehler bei ")

        self.db_qkan.commit()

        return True

    def _anschlussleitungen(self) -> bool:
        """Import der STRAKAT-Tabelle anschlussleitungen"""

        if not QKan.config.check_import.hausanschluesse:
            return True

        sqlnam = "strakat_anschlussleitungen"

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import anschlussleitungen",
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei ")

        self.db_qkan.commit()

        return True

    def _schachtuntersuchungen(self) -> bool:
        """Import der Schächte mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.schachtschaeden:
            return True

        sqlnam = "strakat_schaechte_untersucht"
        params = {"epsg": self.epsg}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Schächte untersucht",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Schächte untersucht")

        sqlnam = "strakat_videos_schaechte"
        params = {'ordner_video': self.ordner_video,}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei Videos Schächte")

        sqlnam = "strakat_untersuchdat_schacht"
        params = {'ordner_bild': self.ordner_bild, 'ordner_video': self.ordner_video, 'epsg': self.epsg}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import der Schachtschäden",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei Untersuchdat Schächte")

        self.db_qkan.commit()

        Schadenstexte.setschadenstexte_schaechte(self.db_qkan)
        self.progress_bar.setValue(55)
        logger.debug("setschadenstexte_schaechte"),

        return True

    def _haltungsuntersuchungen(self) -> bool:
        """Import der Haltungen mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.haltungsschaeden:
            return True

        sqlnam = "strakat_haltungen_untersucht"
        params = {"epsg": self.epsg, "coordsFromRohr": QKan.config.strakat.coords_from_rohr}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import untersuchte Haltungen",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei ")

        sqlnam = "strakat_videos_haltungen"
        params = {'ordner_video': self.ordner_video,}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei {sqlnam}")

        sqlnam = "strakat_untersuchdat_haltung"
        params = {'ordner_bild': self.ordner_bild, 'ordner_video': self.ordner_video}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Haltungsschäden",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Haltungsschäden")

        self.db_qkan.commit()

        Schadenstexte.setschadenstexte_haltungen(self.db_qkan)
        self.progress_bar.setValue(75)
        logger.debug("setschadenstexte_haltungen"),

        return True

    def _anschlussleitungsuntersuchungen(self) -> bool:
        """Import der Anschlussleitungen mit Berichten aus der STRAKAT-Tabelle t_strakatberichte"""

        if not QKan.config.check_import.hausanschlussschaeden:
            return True

        sqlnam = "strakat_anschlussleitungen_untersucht"
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Anschlussleitungen untersucht",
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Anschlussleitungen untersucht")

        sqlnam = "strakat_videos_anschlussleitungen"
        params = {'ordner_video': self.ordner_video,}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei {sqlnam}")

        sqlnam = "strakat_untersuchdat_anschlussleitung"
        params = {'ordner_bild': self.ordner_bild, 'ordner_video': self.ordner_video}
        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category= "strakat_import Untersuchungsdaten Anschlussleitungen",
            parameters=params,
        ):
            raise Exception(f"{self.__class__.__name__}: Fehler bei strakat_import Untersuchungsdaten Anschlussleitungen")

        self.db_qkan.commit()

        Schadenstexte.setschadenstexte_anschlussleitungen(self.db_qkan)
        self.progress_bar.setValue(100)
        logger.debug("setschadenstexte_anschlussleitungen"),

        return True
