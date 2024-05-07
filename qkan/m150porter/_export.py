from datetime import date
from pathlib import Path

# noinspection PyUnresolvedReferences
from typing import Dict, List, Optional, Union
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis
from qgis.utils import iface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fortschritt
from qkan.utils import get_logger

logger = get_logger("QKan.xml.export")


def _create_children(parent: Element, names: List[str]) -> None:
    for child in names:
        SubElement(parent, child)


def _create_children_text(
    parent: Element, children: Dict[str, Union[str, int, None]]
) -> None:
    for name, text in children.items():
        if text is None:
            SubElement(parent, name)
        else:
            SubElementText(parent, name, str(text))


# noinspection PyPep8Naming
def SubElementText(parent: Element, name: str, text: Union[str, int]) -> Element:
    s = SubElement(parent, name)
    if text is not None:
        s.text = str(text)
    return s

#TODO: Testen und Verknuepfung zu Refernztabellen prüfen

# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self, db_qkan: DBConnection, export_file: str):
        self.db_qkan = db_qkan
        self.export_file = export_file

        # XML base
        self.stamm: Optional[Element] = None
        self.hydraulik_objekte: Optional[Element] = None


    def _export_wehre(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_wehre", True)
            #or not self.hydraulik_objekte
            or not self.stamm
        ):
            return
        sql = """
        SELECT
            haltnam,
            schoben,
            schunten,
            sohleunten,
            sohleoben,
            laenge,
            simstatus,
            kommentar
        FROM haltungen WHERE haltungstyp = 'Wehr'
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_wehre"):
            return

        fortschritt("Export Wehre...", 0.5)

        for attr in self.db_qkan.fetchall():
            obj = SubElement(self.hydraulik_objekte, "Hydraulikobjekt")
            _create_children_text(
                obj, {"HydObjektTyp": None, "Objektbezeichnung": attr[0]}
            )

            _create_children_text(
                SubElement(obj, "Wehr"),
                {
                    "SchachtZulauf": attr[1],
                    "SchachtAblauf": attr[2],
                    "Schwellenhoehe": attr[4],
                    "Kammerhoehe": attr[5],
                    "LaengeWehrschwelle": attr[6],
                },
            )

            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            SubElementText(abw, "Objektbezeichnung", attr[0])
            SubElement(abw, "Objektart", str(1))
            SubElementText(abw, "Status", attr[10])
            _create_children_text(
                SubElement(
                    SubElement(SubElement(abw, "Knoten"), "Bauwerk"), "Wehr_Ueberlauf"
                ),
                {"LaengeWehrschwelle": attr[6]},
            )

        fortschritt("Wehre eingefügt", 0.10)

    def _export_pumpen(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_pumpen", True)
            #or not self.hydraulik_objekte
            or not self.stamm
        ):
            return

        sql = """
        SELECT
            haltnam,
            sohleoben,
            schunten,
            schoben,
            simstatus,
            kommentar
        FROM haltungen WHERE haltungstyp = 'Pumpe'
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_pumpen"):
            return

        fortschritt("Export Pumpen...", 0.15)

        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "Objektart": str(2),
                    "KG211": attr[1]-attr[2],
                    "KG302": attr[5],
                    "KG305": "B",
                    "KG306": "ZPW",
                    "KG309": attr[3],
                    "KG999": attr[9],
                },
            )

            geo = SubElement(abw, "GO")
            _create_children_text(
                geo,
                {
                    "GO001": attr[0],

                },
            )

            _create_children_text(
                SubElement(geo, "GP"),
                {
                    "GO001": attr[0],
                    "GP003": attr[7],
                    "GP004": attr[8],
                    "GP007": attr[1],
                },
            )

        fortschritt("Pumpen eingefügt", 0.20)

    def _export_auslaesse(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_auslaesse", True)
            or not self.stamm
        ):
            return

        sql = """
        SELECT
            schaechte.schnam,
            schaechte.deckelhoehe,
            schaechte.sohlhoehe,
            schaechte.durchm,
            x(schaechte.geop) AS xsch,
            y(schaechte.geop) AS ysch,
            schaechte.kommentar,
            schaechte.simstatus,
            ea.m150,
            schaechte.entwart,
            schaechte.strasse,
            schaechte.knotentyp
        FROM schaechte
        LEFT JOIN Entwaesserungsarten AS ea
        ON schaechte.entwart = ea.bezeichnung
        WHERE schaechte.schachttyp = 'Auslass'
        """

        if not self.db_qkan.sql(sql, u"db_qkan: export_auslaesse"):
            return

        fortschritt("Export Auslässe...", 0.25)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "Objektart": str(2),
                    "KG211": attr[1] - attr[2],
                    "KG302": attr[5],
                    "KG305": "A",
                    "KG309": attr[3],
                    "KG999": attr[9],
                },
            )

            geo = SubElement(abw, "GO")
            _create_children_text(
                geo,
                {
                    "GO001": attr[0],

                },
            )

            _create_children_text(
                SubElement(geo, "GP"),
                {
                    "GO001": attr[0],
                    "GP003": attr[7],
                    "GP004": attr[8],
                    "GP007": attr[1],
                },
            )
        fortschritt("Auslässe eingefügt", 0.3)

    def _export_schaechte(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_schaechte", True)
            or not self.stamm
        ):
            return

        sql = """
        SELECT
            schaechte.schnam,
            schaechte.deckelhoehe,
            schaechte.sohlhoehe,
            schaechte.durchm,
            schaechte.druckdicht,
            ea.m150,
            schaechte.entwart,
            schaechte.strasse,
            schaechte.knotentyp,
            schaechte.kommentar,
            schaechte.simstatus,
            x(schaechte.geop) AS xsch,
            y(schaechte.geop) AS ysch
        FROM schaechte
        LEFT JOIN Entwaesserungsarten AS ea
        ON schaechte.entwart = ea.bezeichnung
        WHERE schaechte.schachttyp = 'Schacht'
    """
        if not self.db_qkan.sql(sql, "db_qkan: export_schaechte"):
            return

        fortschritt("Export Schächte...", 0.35)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "Objektart": str(2),
                    "KG211": attr[1]-attr[2],
                    "KG302": attr[5],
                    "KG305": "S",
                    "KG309": attr[3],
                    "KG999": attr[9],
                },
            )

            geo = SubElement(abw, "GO")
            _create_children_text(
                geo,
                {
                    "GO001": attr[0],

                },
            )

            _create_children_text(
                SubElement(geo, "GP"),
                {
                    "GO001": attr[0],
                    "GP003": attr[7],
                    "GP004": attr[8],
                    "GP007": attr[1],
                },
            )

        fortschritt("Schächte eingefügt", 0.4)

    def _export_schaechte_inspektion(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_schaechte", True)
            or not self.stamm
        ):
            return

        sql = """
        SELECT
            schaechte.schnam,
            schaechte.deckelhoehe,
            schaechte.sohlhoehe,
            schaechte.durchm,
            schaechte.druckdicht,
            ea.m150,
            schaechte.entwart,
            schaechte.strasse,
            schaechte.knotentyp,
            schaechte.kommentar,
            schaechte.simstatus,
            x(schaechte.geop) AS xsch,
            y(schaechte.geop) AS ysch
        FROM schaechte
        LEFT JOIN Entwaesserungsarten AS ea
        ON schaechte.entwart = ea.bezeichnung
        WHERE schaechte.schachttyp = 'Schacht'
    """
        if not self.db_qkan.sql(sql, "db_qkan: export_schaechte"):
            return

        fortschritt("Export Schächte...", 0.35)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "Objektart": str(2),
                    "KG211": attr[1]-attr[2],
                    "KG302": attr[5],
                    "KG305": "S",
                    "KG309": attr[3],
                    "KG999": attr[9],
                },
            )

            geo = SubElement(abw, "GO")
            _create_children_text(
                geo,
                {
                    "GO001": attr[0],

                },
            )

            _create_children_text(
                SubElement(geo, "GP"),
                {
                    "GO001": attr[0],
                    "GP003": attr[7],
                    "GP004": attr[8],
                    "GP007": attr[1],
                },
            )

        fortschritt("Schächte eingefügt", 0.4)

    def _export_speicher(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_pumpen", True)
            or not self.stamm
        ):
            return

        sql = """
        SELECT
            schaechte.schnam,
            schaechte.deckelhoehe,
            schaechte.sohlhoehe,
            schaechte.durchm,
            ea.m150,
            schaechte.entwart,
            schaechte.strasse,
            x(schaechte.geop) AS xsch,
            y(schaechte.geop) AS ysch,
            schaechte.kommentar,
            schaechte.simstatus,
            schaechte.knotentyp
        FROM schaechte
        left join Entwaesserungsarten AS ea
        ON schaechte.entwart = ea.bezeichnung
        WHERE schaechte.schachttyp = 'Speicher'
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_speicher"):
            return

        fortschritt("Export Speicherschächte...", 0.45)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "Objektart": str(2),
                    "KG211": attr[1]-attr[2],
                    "KG302": attr[5],
                    "KG305": "B",
                    "KG309": attr[3],
                    "KG999": attr[9],
                },
            )

            geo = SubElement(abw, "GO")
            _create_children_text(
                geo,
                {
                    "GO001": attr[0],

                },
            )

            _create_children_text(
                SubElement(geo, "GP"),
                {
                    "GO001": attr[0],
                    "GP003": attr[7],
                    "GP004": attr[8],
                    "GP007": attr[1],
                },
            )
        fortschritt("Speicher eingefügt", 0.5)

    def _export_haltungen(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_haltungen", True)
            #or not self.hydraulik_objekte
            or not self.stamm
        ):
            return

        sql = """
        SELECT
            haltungen.haltnam,
            haltungen.schoben,
            haltungen.schunten,
            haltungen.hoehe,
            haltungen.breite,
            haltungen.laenge,
            haltungen.sohleoben,
            haltungen.sohleunten,
            haltungen.profilnam,
            haltungen.strasse,
            haltungen.material,
            ea.m150,
            haltungen.entwart,
            haltungen.ks,
            haltungen.simstatus,
            haltungen.kommentar,
            x(PointN(haltungen.geom, 1)) AS xschob,
            y(PointN(haltungen.geom, 1)) AS yschob,
            x(PointN(haltungen.geom, -1)) AS xschun,
            y(PointN(haltungen.geom, -1)) AS yschun
        FROM haltungen
        LEFT JOIN Entwaesserungsarten AS ea 
        ON haltungen.entwart = ea.bezeichnung
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_haltungen"):
            return

        fortschritt("Export Haltungen...", 0.55)

        for attr in self.db_qkan.fetchall():

            abw = SubElement(self.stamm, "HG")
            _create_children_text(
                abw,
                {
                    "HG001": attr[0],
                    "HG003": attr[1],
                    "HG004": attr[2],
                    "HG102": attr[9],
                    "HG301": 'K',
                    "HG302": attr[11],
                    "HG304": attr[10],
                    "HG305": attr[8],
                    "HG306": attr[4],
                    "HG307": attr[3],
                    "HG310": attr[5],
                    "Status": attr[14],
                    "HG999": attr[15],
                },
            )

            kante = SubElement(abw, "GO")
            _create_children_text(
                kante,
                {
                    "GO001": attr[0],
                    "GO002": 'H',
                },
            )

            geom = SubElement(kante, "GP")
            _create_children_text(
                geom,
                {
                    "GP001": attr[1],
                    "GP003": attr[16],
                    "GP004": attr[17],
                    "GP007": attr[6],
                },
            )

            kante = SubElement(abw, "GO")
            geom = SubElement(kante, "GP")
            _create_children_text(
                geom,
                {
                    "GP001": attr[2],
                    "GP003": attr[18],
                    "GP004": attr[19],
                    "GP007": attr[7],
                },
            )

        fortschritt("Haltungen eingefügt", 0.60)

    def _export_haltungen_inspektion(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_haltungen", True)
            #or not self.hydraulik_objekte
            or not self.stamm
        ):
            return

        sql = """
        SELECT
            haltungen.haltnam,
            haltungen.schoben,
            haltungen.schunten,
            haltungen.hoehe,
            haltungen.breite,
            haltungen.laenge,
            haltungen.sohleoben,
            haltungen.sohleunten,
            haltungen.profilnam,
            haltungen.strasse,
            haltungen.material,
            ea.m150,
            haltungen.entwart,
            haltungen.ks,
            haltungen.simstatus,
            haltungen.kommentar,
            x(PointN(haltungen.geom, 1)) AS xschob,
            y(PointN(haltungen.geom, 1)) AS yschob,
            x(PointN(haltungen.geom, -1)) AS xschun,
            y(PointN(haltungen.geom, -1)) AS yschun
        FROM haltungen
        LEFT JOIN Entwaesserungsarten AS ea 
        ON haltungen.entwart = ea.bezeichnung
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_haltungen"):
            return

        fortschritt("Export Haltungen...", 0.55)

        for attr in self.db_qkan.fetchall():

            abw = SubElement(self.stamm, "HG")
            _create_children_text(
                abw,
                {
                    "HG001": attr[0],
                    "HG003": attr[1],
                    "HG004": attr[2],
                    "HG102": attr[9],
                    "HG301": 'K',
                    "HG302": attr[11],
                    "HG304": attr[10],
                    "HG305": attr[8],
                    "HG306": attr[4],
                    "HG307": attr[3],
                    "HG310": attr[5],
                    "Status": attr[14],
                    "HG999": attr[15],
                },
            )

            kante = SubElement(abw, "GO")
            _create_children_text(
                kante,
                {
                    "GO001": attr[0],
                    "GO002": 'H',
                },
            )

            geom = SubElement(kante, "GP")
            _create_children_text(
                geom,
                {
                    "GP001": attr[1],
                    "GP003": x_koordinate,
                    "GP004": y_koordinate,
                    "GP007": attr[6],
                },
            )

            kante = SubElement(abw, "GO")
            geom = SubElement(kante, "GP")
            _create_children_text(
                geom,
                {
                    "GP001": attr[2],
                    "GP003": x_koordinate,
                    "GP004": y_koordinate,
                    "GP007": attr[7],
                },
            )

        fortschritt("Haltungen eingefügt", 0.60)

    def _export_anschlussleitungen(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_anschlussleitungen", True)
            #or not self.hydraulik_objekte
            or not self.stamm
        ):
            return

        sql = """
                SELECT
                    anschlussleitungen.leitnam,
                    anschlussleitungen.schoben,
                    anschlussleitungen.schunten,
                    anschlussleitungen.hoehe,
                    anschlussleitungen.breite,
                    anschlussleitungen.laenge,
                    anschlussleitungen.sohleoben,
                    anschlussleitungen.sohleunten,
                    anschlussleitungen.deckeloben,
                    anschlussleitungen.deckelunten,
                    anschlussleitungen.profilnam,
                    anschlussleitungen.material,
                    ea.m150,
                    anschlussleitungen.entwart,
                    anschlussleitungen.ks,
                    anschlussleitungen.simstatus,
                    anschlussleitungen.kommentar,
                    x(PointN(anschlussleitungen.geom, 1)) AS xschob,
                    y(PointN(anschlussleitungen.geom, 1)) AS yschob,
                    x(PointN(anschlussleitungen.geom, -1)) AS xschun,
                    y(PointN(anschlussleitungen.geom, -1)) AS yschun
                FROM anschlussleitungen
                LEFT JOIN Entwaesserungsarten AS ea 
                ON anschlussleitungen.entwart = ea.bezeichnung
                """

        if not self.db_qkan.sql(sql, "db_qkan: export_anschlussleitungen"):
            return

        fortschritt("Export Anschlussleitungen...", 0.65)

        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "HG")
            _create_children_text(
                abw,
                {
                    "HG001": attr[0],
                    "HG003": attr[1],
                    "HG004": attr[2],
                    "HG102": attr[9],
                    "HG301": 'L',
                    "HG302": attr[11],
                    "HG304": attr[10],
                    "HG305": attr[8],
                    "HG306": attr[4],
                    "HG307": attr[3],
                    "HG310": attr[5],
                    "Status": attr[14],
                    "HG999": attr[15],
                },
            )

            kante = SubElement(abw, "GO")
            _create_children_text(
                kante,
                {
                    "GO001": attr[0],
                    "GO002": 'H',
                },
            )

            geom = SubElement(kante, "GP")
            _create_children_text(
                geom,
                {
                    "GP001": attr[1],
                    "GP003": attr[16],
                    "GP004": attr[17],
                    "GP007": attr[6],
                },
            )

            kante = SubElement(abw, "GO")
            geom = SubElement(kante, "GP")
            _create_children_text(
                geom,
                {
                    "GP001": attr[2],
                    "GP003": attr[18],
                    "GP004": attr[19],
                    "GP007": attr[7],
                },
            )

        fortschritt("Leitung eingefügt", 0.7)

    def run(self) -> None:
        """
        Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine XML-Datei
        """
        iface = QKan.instance.iface

        # Create progress bar
        progress_bar = QProgressBar(iface.messageBar())
        progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Export in Arbeit. Bitte warten..."
        )
        status_message.layout().addWidget(progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.Info, 10)


        # region Create XML structure
        root = Element(
            "Identifikation", {"xmlns": "http://www.ofd-hannover.la/Identifikation", "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",}
        )
        SubElementText(root, "Version", "2013-02")

        admin_daten = SubElement(root, "Admindaten")
        _create_children(
            SubElement(admin_daten, "Liegenschaft"),
            ["Liegenschaftsnummer", "Liegenschaftsbezeichnung"],
        )

        daten_kollektive = SubElement(root, "Datenkollektive")
        _create_children_text(
            daten_kollektive,
            {
                "Datenstatus": "2",
                "Erstellungsdatum": str(date.today()),
                "Kommentar": "Created with QKan's XML export module",
            },
        )
        kennungen = SubElement(SubElement(daten_kollektive, "Kennungen"), "Kollektiv")
        #je ein Kollektiv für Stammdaten und Zustandsdaten, die Kennung muss dort auftauchen
        _create_children_text(
            kennungen,
            {
                "Kennung": "STA01",
                "Kollektivart": "1",
            },
        )

        self.stamm = SubElement(daten_kollektive, "Stammdatenkollektiv")
        _create_children_text(self.stamm, {"Kennung": "STA01", "Beschreibung": "Stammdaten",},)

        hydro_kollektiv = SubElement(daten_kollektive, "Hydraulikdatenkollektiv")
        _create_children_text(
            hydro_kollektiv,
            {"Kennung": "STA01", "Beschreibung": "Hydraulikdaten",},
        )
        rechen = SubElement(hydro_kollektiv, "Rechennetz")
        SubElement(rechen, "Stammdatenkennung")
        self.hydraulik_objekte = SubElement(rechen, "HydraulikObjekt")
        # endregion

        # Export
        self._export_wehre()
        self._export_pumpen()
        self._export_auslaesse()
        self._export_schaechte()
        self._export_speicher()
        self._export_haltungen()
        self._export_anschlussleitungen()

        Path(self.export_file).write_text(
            minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        )

        # Close connection
        del self.db_qkan

        fortschritt("Ende...", 1)
        progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")
        status_message.setLevel(Qgis.Success)
