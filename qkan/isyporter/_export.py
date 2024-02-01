import logging
from pathlib import Path

# noinspection PyUnresolvedReferences
from typing import Dict, List, Optional, Union
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import date
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.utils import iface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fortschritt

logger = logging.getLogger("QKan.xml.export")


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

        # Mappings
        self.mapper_simstatus: Dict[int, str] = {}

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
            SubElementText(abw, "Status", self.mapper_simstatus.get(attr[10], -1))
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
            obj = SubElement(self.hydraulik_objekte, "Hydraulikobjekt")
            SubElementText(obj, "Objektbezeichnung", attr[0])
            _create_children_text(
                SubElement(obj, "Pumpe"),
                {
                    "HydObjektTyp": None,
                    "Sohlhoehe": attr[1],
                    "SchachtAblauf": attr[2],
                    "SchachtZulauf": attr[3],
                },
            )

            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektbezeichnung": attr[0],
                    "Objektart": str(1),
                    "Status": self.mapper_simstatus.get(attr[4], -1),
                },
            )
            SubElement(SubElement(abw, "Knoten"), "Bauwerk")

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
            ea.he_nr,
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
            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektbezeichnung": attr[0],
                    "Objektart": str(2),
                    "Kommentar": attr[6],
                    "Status": self.mapper_simstatus.get(attr[7], -1),
                    "Entwaesserungsart": attr[9],
                },
            )
            strasse = SubElement(abw, "Lage")
            SubElementText(strasse, "Strassenname", attr[10])
            knoten = SubElement(abw, "Knoten")
            SubElementText(knoten, "KnotenTyp", attr[11])  # TODO: Is None sometimes
            _create_children(
                SubElement(knoten, "Bauwerk"), ["Bauwerktyp", "Auslaufbauwerk"]
            )
            # geom_knoten = SubElement(
            #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
            # )
            # TODO: Geometrie/CRSLage mit Koordinatesystem ergänzen (qgis.utils.iface.activeLayer().crs().authid())
            geo = SubElement(abw, "Geometrie")
            _create_children_text(
                geo,
                {
                    "CRSLage": iface.activeLayer().crs().authid(),
                }, )

            geom_knoten = SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Punkthoehe": attr[1],
                    "Rechtswert": attr[7],
                    "Hochwert": attr[8],
                },
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {"PunktattributAbwasser": "GOK", "Punkthoehe": attr[2]},
            )
            #TODO: prüfen ob GOK oder HP
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "SMP",
                    "Punkthoehe": attr[2],
                    "Rechtswert": attr[4],
                    "Hochwert": attr[5],
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
            ea.he_nr,
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
            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektbezeichnung": attr[0],
                    "Objektart": str(2),
                    "Entwaesserungsart": attr[6],
                    "Kommentar": attr[9],
                    "Status": self.mapper_simstatus.get(attr[10], -1),
                },
            )

            knoten = SubElement(abw, "Knoten")
            SubElementText(knoten, "KnotenTyp", attr[8])
            _create_children(
                SubElement(knoten, "Schacht"), ["Schachttiefe", "AnzahlAnschluesse"]
            )
            # geom_knoten = SubElement(
            #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
            # )
            # TODO: Geometrie/CRSLage mit Koordinatesystem ergänzen (qgis.utils.iface.activeLayer().crs().authid())
            geo = SubElement(abw, "Geometrie")
            _create_children_text(
                geo,
                {
                    "CRSLage": iface.activeLayer().crs().authid(),
                }, )

            geom_knoten = SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Punkthoehe": attr[1],
                    "Rechtswert": attr[7],
                    "Hochwert": attr[8],
                },
            )

            #_create_children_text(
            #    SubElement(geom_knoten, "Punkt"),
            #    {"PunktattributAbwasser": "HP", "Punkthoehe": attr[2]},
            #)
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "SMP",
                    "Punkthoehe": attr[2],
                    "Rechtswert": attr[11],
                    "Hochwert": attr[12],
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
            ea.he_nr,
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
            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektbezeichnung": attr[0],
                    "Objektart": str(2),
                    "Entwaesserungsart": attr[5],
                    "Kommentar": attr[9],
                    "Status": self.mapper_simstatus.get(attr[10], -1),
                },
            )

            knoten = SubElement(abw, "Knoten")
            SubElementText(knoten, "KnotenTyp", attr[11])  # TODO: Is None sometimes
            bauwerk = SubElement(knoten, "Bauwerk")
            SubElement(bauwerk, "Bauwerkstyp")
            _create_children(
                SubElement(bauwerk, "Becken"), ["AnzahlZulaeufe", "AnzahlAblaeufe"]
            )

            #geom_knoten = SubElement(
            #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
            #)
            # TODO: Geometrie/CRSLage mit Koordinatesystem ergänzen (qgis.utils.iface.activeLayer().crs().authid())
            geo = SubElement(abw, "Geometrie")
            _create_children_text(
                geo,
                {
                    "CRSLage": iface.activeLayer().crs().authid(),
                },)

            geom_knoten= SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Punkthoehe": attr[1],
                    "Rechtswert": attr[7],
                    "Hochwert": attr[8],
                },
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "SMP",
                    "Punkthoehe": attr[2],
                    "Rechtswert": attr[7],
                    "Hochwert": attr[8],
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
            ea.he_nr,
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
            obj = SubElement(self.hydraulik_objekte, "HydraulikObjekt")
            _create_children(obj, ["HydObjektTyp", "Objektbezeichnung"])
            _create_children_text(
                SubElement(obj, "Haltung"),
                {"Objektbezeichnung": attr[0], "Berechnungslaenge": attr[5],"Rauigkeitsansatz": 1, "RauigkeitsbeiwertKb": attr[13]},
            )

            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektbezeichnung": attr[0],
                    "Objektart": str(1),
                    "Entwaesserungsart": attr[12],
                    "Status": self.mapper_simstatus.get(attr[14], -1),
                },
            )

            strasse = SubElement(abw, "Lage")
            _create_children_text(
                strasse,
                {
                    "Strassenname": attr[9],
                },
            )

            kante = SubElement(abw, "Kante")
            _create_children_text(
                kante,
                {
                    "KantenTyp": None,
                    "KnotenAblaufTyp": None,
                    "KnotenZulaufTyp": None,
                    "Material": attr[10],
                    "KnotenZulauf": attr[1],
                    "KnotenAblauf": attr[2],
                    "SohlhoeheZulauf": attr[6],
                    "SohlhoeheAblauf": attr[7],
                    "Laenge": attr[5],
                },
            )

            _create_children_text(
                SubElement(kante, "Profil"),
                {
                    "ProfilID": None,
                    "SonderprofilVorhanden": None,
                    "Profilart": attr[8],
                    "Profilbreite": (attr[4]*1000),
                    "Profilhoehe": (attr[3]*1000),
                },
            )

            SubElementText(SubElement(kante, "Haltung"), "DMPLaenge", attr[5])

            geom = SubElement(abw, "Geometrie")

            _create_children_text(
                geom,
                {
                    "CRSLage": iface.activeLayer().crs().authid(),
                }, )

            _create_children(geom, ["GeoObjektart", "GeoObjekttyp"])

            kante = SubElement(
                SubElement(SubElement(geom, "Geometriedaten"), "Kanten"), "Kante"
            )
            _create_children_text(
                SubElement(kante, "Start"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Rechtswert": attr[16],
                    "Hochwert": attr[17],
                },
            )
            _create_children_text(
                SubElement(kante, "Ende"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Rechtswert": attr[18],
                    "Hochwert": attr[19],
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
            ea.he_nr,
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
            obj = SubElement(self.hydraulik_objekte, "HydraulikObjekt")
            _create_children(obj, ["HydObjektTyp", "Objektbezeichnung"])
            _create_children_text(
                SubElement(obj, "Leitung"),
                {"Objektbezeichnung": attr[0], "Berechnungslaenge": attr[5], "Rauigkeitsansatz": 1,  "RauigkeitsbeiwertKb": attr[14]},
            )

            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektbezeichnung": attr[0],
                    "Objektart": str(1),
                    "Entwaesserungsart": attr[13],
                    "Status": self.mapper_simstatus.get(attr[15], -1),
                },
            )

            kante = SubElement(abw, "Kante")
            _create_children_text(
                kante,
                {
                    "KantenTyp": None,
                    "KnotenAblaufTyp": None,
                    "KnotenZulaufTyp": None,
                    "Material": attr[11],
                    "KnotenZulauf": attr[1],
                    "KnotenAblauf": attr[2],
                    "SohlhoeheZulauf": attr[6],
                    "SohlhoeheAblauf": attr[7],
                    "Laenge": attr[5],
                },
            )

            _create_children_text(
                SubElement(kante, "Profil"),
                {
                    "ProfilID": None,
                    "SonderprofilVorhanden": None,
                    "Profilart": attr[10],
                    "Profilbreite": (attr[4]*1000),
                    "Profilhoehe": (attr[3]*1000),
                },
            )

            SubElementText(SubElement(kante, "Leitung"), "DMPLaenge", attr[5])

            geom = SubElement(abw, "Geometrie")
            _create_children_text(
                geom,
                {
                    "CRSLage": iface.activeLayer().crs().authid(),
                }, )
            _create_children(geom, ["GeoObjektart", "GeoObjekttyp"])

            kante = SubElement(
                SubElement(SubElement(geom, "Geometriedaten"), "Kanten"), "Kante"
            )
            _create_children_text(
                SubElement(kante, "Start"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Rechtswert": attr[17],
                    "Hochwert": attr[18],
                },
            )
            _create_children_text(
                SubElement(kante, "Ende"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Rechtswert": attr[19],
                    "Hochwert": attr[20],
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

        # Init status mapper
        if not self.db_qkan.sql(
            "SELECT he_nr, bezeichnung FROM simulationsstatus",
            "xml_export simulationsstatus",
        ):
            raise Exception("Failed to init SIMSTATUS mapper")
        for row in self.db_qkan.fetchall():
            self.mapper_simstatus[row[1]] = row[0]

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
