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

        self.hydraulik_objekte: Optional[Element] = None


    def _export_wehre(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_wehre", True)
            #or not self.hydraulik_objekte

        ):
            return
        sql = """
        SELECT
            haltnam,
            sohleoben,
            schunten,
            schoben,
            simstatus,
            kommentar,
            entwart,
            xschob,
            yschob
        FROM haltungen WHERE haltungstyp = 'Wehr'
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_wehre"):
            return

        fortschritt("Export Wehre...", 0.5)

        for attr in self.db_qkan.fetchall():
            if attr[1] in [None, 'NULL']:
                sohleoben = 0
            else:
                sohleoben = attr[1]

            abw = SubElement(self.root,"KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "KG211": sohleoben,
                    "KG302": attr[6],
                    "KG305": "B",
                    "KG306": "ZPW",
                    "KG309": attr[3],
                    "KG999": attr[5],
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

        fortschritt("Wehre eingefügt", 0.10)

    def _export_pumpen(self) -> None:
        if (
            not getattr(QKan.config.check_export, "export_pumpen", True)
            #or not self.hydraulik_objekte

        ):
            return

        sql = """
        SELECT
            haltnam,
            sohleoben,
            schunten,
            schoben,
            simstatus,
            kommentar,
            entwart,
            xschob,
            yschob
        FROM haltungen WHERE haltungstyp = 'Pumpe'
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_pumpen"):
            return

        fortschritt("Export Pumpen...", 0.15)

        for attr in self.db_qkan.fetchall():

            if attr[1] in [None, 'NULL']:
                sohleoben = 0
            else:
                sohleoben = attr[1]

            abw = SubElement(self.root,"KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "KG211": sohleoben,
                    "KG302": attr[6],
                    "KG305": "B",
                    "KG306": "ZPW",
                    "KG309": attr[3],
                    "KG999": attr[5],
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
            schaechte.knotentyp,
            schaechte.baujahr
        FROM schaechte
        LEFT JOIN Entwaesserungsarten AS ea
        ON schaechte.entwart = ea.bezeichnung
        WHERE schaechte.schachttyp = 'Auslass'
        """

        if not self.db_qkan.sql(sql, u"db_qkan: export_auslaesse"):
            return

        fortschritt("Export Auslässe...", 0.25)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.root,"KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "KG211": attr[1] - attr[2],
                    "KG302": attr[5],
                    "KG303": attr[12],
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
            y(schaechte.geop) AS ysch,
            schaechte.baujahr
        FROM schaechte
        LEFT JOIN Entwaesserungsarten AS ea
        ON schaechte.entwart = ea.bezeichnung
        WHERE schaechte.schachttyp = 'Schacht'
    """
        if not self.db_qkan.sql(sql, "db_qkan: export_schaechte"):
            return

        fortschritt("Export Schächte...", 0.35)
        for attr in self.db_qkan.fetchall():
            if attr[1] in [None, 'NULL']:
                sohleoben = 0
            else:
                sohleoben = attr[1]

            if attr[2] in [None, 'NULL']:
                sohleunten = 0
            else:
                sohleunten = attr[2]

            abw = SubElement(self.root,"KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "KG211": sohleoben-sohleunten,
                    "KG302": attr[5],
                    "KG303": attr[13],
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
            abw = SubElement(self.root, "KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
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
            schaechte.knotentyp,
            schaechte.baujahr
        FROM schaechte
        left join Entwaesserungsarten AS ea
        ON schaechte.entwart = ea.bezeichnung
        WHERE schaechte.schachttyp = 'Speicher'
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_speicher"):
            return

        fortschritt("Export Speicherschächte...", 0.45)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.root, "KG")
            _create_children_text(
                abw,
                {
                    "KG001": attr[0],
                    "Objektart": str(2),
                    "KG211": attr[1]-attr[2],
                    "KG302": attr[5],
                    "KG303": attr[12],
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
            y(PointN(haltungen.geom, -1)) AS yschun,
            haltungen.baujahr,
            haltungen.aussendurchmesser,
            haltungen.profilauskleidung,
            haltungen.innenmaterial
        FROM haltungen
        LEFT JOIN Entwaesserungsarten AS ea 
        ON haltungen.entwart = ea.bezeichnung
        """

        if not self.db_qkan.sql(sql, "db_qkan: export_haltungen"):
            return

        fortschritt("Export Haltungen...", 0.55)

        for attr in self.db_qkan.fetchall():

            abw = SubElement(self.root, "HG")
            _create_children_text(
                abw,
                {
                    "HG001": attr[0],
                    "HG003": attr[1],
                    "HG004": attr[2],
                    "HG102": attr[9],
                    "HG301": 'K',
                    "HG302": attr[11],
                    "HG303": attr[20],
                    "HG304": attr[10],
                    "HG305": attr[8],
                    "HG306": attr[4],
                    "HG307": attr[3],
                    "HG308": attr[22],
                    "HG309": attr[23],
                    "HG310": attr[5],
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

            abw = SubElement(self.root,"HG")
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
                    y(PointN(anschlussleitungen.geom, -1)) AS yschun,
                    anschlussleitungen.baujahr,
                    anschlussleitungen.aussendurchmesser,
                    anschlussleitungen.profilauskleidung,
                    anschlussleitungen.innenmaterial
                FROM anschlussleitungen
                LEFT JOIN Entwaesserungsarten AS ea 
                ON anschlussleitungen.entwart = ea.bezeichnung
                """

        if not self.db_qkan.sql(sql, "db_qkan: export_anschlussleitungen"):
            return

        fortschritt("Export Anschlussleitungen...", 0.65)

        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.root,"HG")
            _create_children_text(
                abw,
                {
                    "HG001": attr[0],
                    "HG003": attr[1],
                    "HG004": attr[2],
                    "HG301": 'L',
                    "HG302": attr[9],
                    "HG303": attr[19],
                    "HG304": attr[8],
                    "HG306": attr[4],
                    "HG307": attr[3],
                    "HG308": attr[21],
                    "HG309": attr[22],
                    "HG310": attr[5],
                    "HG999": attr[13],
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
                    "GP003": attr[14],
                    "GP004": attr[15],
                    "GP007": attr[6],
                },
            )

            kante = SubElement(abw, "GO")
            geom = SubElement(kante, "GP")
            _create_children_text(
                geom,
                {
                    "GP001": attr[2],
                    "GP003": attr[16],
                    "GP004": attr[17],
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
        self.root = Element("DATA", {"xmlns": "",}
        )

        # Export
        self._export_wehre()
        self._export_pumpen()
        self._export_auslaesse()
        self._export_schaechte()
        self._export_speicher()
        self._export_haltungen()
        self._export_anschlussleitungen()

        Path(self.export_file).write_text(
            minidom.parseString(tostring(self.root)).toprettyxml(indent="  ")
        )

        # Close connection
        del self.db_qkan

        fortschritt("Ende...", 1)
        progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")
        status_message.setLevel(Qgis.Success)
