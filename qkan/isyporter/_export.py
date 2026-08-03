from datetime import date, datetime
from pathlib import Path
import locale

# noinspection PyUnresolvedReferences
from typing import Dict, List, Optional, Union
from lxml.etree import Element, SubElement
from lxml import etree

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis, QgsProject
from qgis.utils import iface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import fortschritt
from qkan.utils import get_logger

logger = get_logger("QKan.xml.export")
locale.setlocale(locale.LC_TIME, "deu_deu")

month_map = {
    "Jan": "01", "Jan.": "01", "Januar": "01",
    "Feb": "02", "Feb.": "02", "Februar": "02",
    "Mär": "03", "Mär.": "03", "März": "03",
    "Apr": "04", "Apr.": "04", "April": "04",
    "Mai": "05",
    "Jun": "06", "Juni": "06",
    "Jul": "07", "Juli": "07",
    "Aug": "08", "Aug.": "08", "August": "08",
    "Sep": "09", "Sept": "09", "Sept.": "09", "September": "09",
    "Okt": "10", "Okt.": "10", "Oktober": "10",
    "Nov": "11", "November": "11",
    "Dez": "12", "Dezember": "12",
}


def _create_children(parent: Element, names: List[str]) -> None:
    for child in names:
        SubElement(parent, child)


def _create_children_text(
    parent: Element, children: Dict[str, Union[str, int, None]]
) -> None:
    for name, text in children.items():
        if text is None:
            continue

        text = str(text).strip()
        if not text:
            continue

        SubElementText(parent, name, text)


# noinspection PyPep8Naming
def SubElementText(parent: Element, name: str, text: Union[str, int]) -> Element:
    s = SubElement(parent, name)
    if text is not None:
        s.text = str(text)
    return s

#TODO: Testen und Verknuepfung zu Refernztabellen prüfen

# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self, db_qkan: DBConnection, export_file: str, vorlage: str, auswahl_zustand:str):
        self.db_qkan = db_qkan
        self.export_file = export_file
        self.vorlage = ''
        self.auswahl_zustand = auswahl_zustand

        # XML base
        self.stamm: Optional[Element] = None
        self.zustand: Optional[Element] = None
        self.hydraulik_objekte: Optional[Element] = None

        if self.vorlage != "":
            tree = etree.parse(self.vorlage)
            x = tree.xpath('namespace-uri(.)')
            self.NS = {"d": x}


    def _export_wehre(self) -> None:

        if self.vorlage == "":

            if (
                not getattr(QKan.config.check_export, "export_wehre", True)
                #or not self.hydraulik_objekte
                or not self.stamm
            ):
                return
            sql = f"""
            SELECT
                ha.haltnam,
                ha.schoben,
                ha.schunten,
                ha.sohleunten,
                ha.sohleoben,
                ha.hoehe,
                ha.breite,
                ha.laenge,
                si.isybau AS simstatus,
                ha.kommentar
            FROM haltungen AS ha
            LEFT JOIN simulationsstatus AS si ON ha.simstatus = si.bezeichnung
            WHERE haltungstyp = 'Wehr' {self.abfrage_h_and}
            """

            if not self.db_qkan.sql(sql, "db_qkan: export_wehre"):
                return

            fortschritt("Export Wehre...", 0.5)

            for attr in self.db_qkan.fetchall():
                (
                    haltnam,
                    schoben,
                    schunten,
                    sohleoben,
                    sohleunten,
                    hoehe,
                    breite,
                    laenge,
                    simstatus_nr,
                    kommentar,
                ) = attr

                obj = SubElement(self.hydraulik_objekte, "Hydraulikobjekt")
                _create_children_text(
                    obj, {"HydObjektTyp": None, "Objektbezeichnung": haltnam}
                )

                _create_children_text(
                    SubElement(obj, "Wehr"),
                    {
                        "SchachtZulauf": schoben,                               # schoben
                        "SchachtAblauf": schunten,                               # schunten
                        "Schwellenhoehe": sohleunten,                              # sohleoben
                        "Kammerhoehe": hoehe,                                 # hoehe
                        "LaengeWehrschwelle": round(laenge,2),                          # laenge
                    },
                )

                abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
                SubElementText(abw, "Objektbezeichnung", haltnam)               # haltnam
                SubElementText(abw, "Objektart", "1")
                SubElementText(abw, "Status", simstatus_nr)                          # simstatus
                _create_children_text(
                    SubElement(
                        SubElement(SubElement(abw, "Knoten"), "Bauwerk"), "Wehr_Ueberlauf"
                    ),
                    {"LaengeWehrschwelle": round(laenge,2)},                            # laenge
                )

            fortschritt("Wehre eingefügt", 0.10)

    def _export_pumpen(self) -> None:

        if self.vorlage == "":

            if (
                not getattr(QKan.config.check_export, "export_pumpen", True)
                #or not self.hydraulik_objekte
                or not self.stamm
            ):
                return

            sql = f"""
            SELECT
                ha.haltnam,
                ha.sohleoben,
                ha.schoben,
                ha.schunten,
                si.isybau AS simstatus,
                ha.kommentar
            FROM haltungen AS ha
            LEFT JOIN simulationsstatus AS si ON ha.simstatus = si.bezeichnung
            WHERE haltungstyp = 'Pumpe' {self.abfrage_h_and}
            """

            if not self.db_qkan.sql(sql, "db_qkan: export_pumpen"):
                return

            fortschritt("Export Pumpen...", 0.15)

            for attr in self.db_qkan.fetchall():
                (
                    haltnam,
                    sohleoben,
                    schoben,
                    schunten,
                    simstatus_nr,
                    kommentar,
                ) = attr

                obj = SubElement(self.hydraulik_objekte, "Hydraulikobjekt")
                SubElementText(obj, "Objektbezeichnung", haltnam)
                _create_children_text(
                    SubElement(obj, "Pumpe"),
                    {
                        "HydObjektTyp": None,
                        "Sohlhoehe": sohleoben,
                        "SchachtAblauf": schunten,
                        "SchachtZulauf": schoben,
                    },
                )

                abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
                _create_children_text(
                    abw,
                    {
                        "Objektbezeichnung": haltnam,
                        "Objektart": str(1),
                        "Status": simstatus_nr,
                    },
                )
                SubElement(SubElement(abw, "Knoten"), "Bauwerk")

            fortschritt("Pumpen eingefügt", 0.20)

    def _export_auslaesse(self) -> None:

        if self.vorlage == "":

            if (
                not getattr(QKan.config.check_export, "export_auslaesse", True)
                or not self.stamm
            ):
                return

            sql = f"""
            SELECT
                schaechte.schnam,
                schaechte.deckelhoehe,
                schaechte.sohlhoehe,
                schaechte.durchm,
                x(schaechte.geop) AS xsch,
                y(schaechte.geop) AS ysch,
                schaechte.kommentar,
                si.isybau,
                ea.isybau,
                schaechte.strasse,
                schaechte.knotentyp,
                schaechte.baujahr,
                ma.isybau
            FROM schaechte
            LEFT JOIN Entwaesserungsarten AS ea
            ON schaechte.entwart = ea.bezeichnung
            LEFT JOIN simulationsstatus AS si ON schaechte.simstatus = si.bezeichnung
            LEFT JOIN material AS ma ON schaechte.material = ma.bezeichnung
            WHERE schaechte.schachttyp = 'Auslass' {self.abfrage_s_and}
            """

            if not self.db_qkan.sql(sql, u"db_qkan: export_auslaesse"):
                return

            fortschritt("Export Auslässe...", 0.25)
            for attr in self.db_qkan.fetchall():

                (
                    schnam,
                    deckelhoehe,
                    sohlhoehe,
                    durchm,
                    xsch,
                    ysch,
                    kommentar,
                    simstatus_nr,
                    entwart_nr,
                    strasse_nam,
                    kntoentyp,
                    baujahr,
                    material,
                ) = attr

                abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
                if baujahr not in (0, '0', None, 'NULL'):
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": schnam,
                            "Objektart": str(2),
                            "Status": simstatus_nr,
                            "Baujahr": baujahr,
                            "Entwaesserungsart": entwart_nr,
                            "Kommentar": kommentar,
                        },
                    )

                else:
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": schnam,
                            "Objektart": str(2),
                            "Status": simstatus_nr,
                            "Entwaesserungsart": entwart_nr,
                            "Kommentar": kommentar,
                        },
                    )
                knoten = SubElement(abw, "Knoten")
                SubElementText(knoten, "KnotenTyp", 0)
                schacht = SubElement(knoten, "Schacht")
                strasse = SubElement(abw, "Lage")
                SubElementText(strasse, "Strassenname", strasse_nam)
                SubElementText(schacht, "Schachttiefe", round(deckelhoehe-sohlhoehe,2))
                _create_children(
                    SubElement(knoten, "Bauwerk"), ["Bauwerktyp", "Auslaufbauwerk"]
                )
                # geom_knoten = SubElement(
                #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
                # )

                geo = SubElement(abw, "Geometrie")


                geom_knoten = SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
                _create_children_text(
                    SubElement(geom_knoten, "Punkt"),
                    {
                        "PunktattributAbwasser": "DMP",
                        "Punkthoehe": sohlhoehe,
                        "Rechtswert": xsch,
                        "Hochwert": ysch,
                    },
                )
                _create_children_text(
                    SubElement(geom_knoten, "Punkt"),
                    {"PunktattributAbwasser": "GOK", "Punkthoehe": deckelhoehe},
                )

                _create_children_text(
                    SubElement(geom_knoten, "Punkt"),
                    {
                        "PunktattributAbwasser": "SMP",
                        "Punkthoehe": sohlhoehe,
                        "Rechtswert": xsch,
                        "Hochwert": ysch,
                    },
                )
                x = QgsProject.instance().crs().authid()
                x.replace('EPSG:', '')
                _create_children_text(
                    geo,
                    {
                        "CRSLage": x,
                    }, )
            fortschritt("Auslässe eingefügt", 0.3)

        if self.vorlage != "":
            # Daten äbandern oder zu bestehender datei hinzufügen
            tree = etree.parse(self.vorlage)
            root = tree.getroot()

            sql = f"""
                        SELECT
                            schaechte.schnam,
                            schaechte.deckelhoehe,
                            schaechte.sohlhoehe,
                            schaechte.durchm,
                            x(schaechte.geop) AS xsch,
                            y(schaechte.geop) AS ysch,
                            schaechte.kommentar,
                            si.isybau,
                            ea.isybau,
                            schaechte.strasse,
                            schaechte.knotentyp,
                            schaechte.baujahr,
                            ma.isybau
                        FROM schaechte
                        LEFT JOIN Entwaesserungsarten AS ea
                        ON schaechte.entwart = ea.bezeichnung
                        LEFT JOIN simulationsstatus AS si ON schaechte.simstatus = si.bezeichnung
                        LEFT JOIN material AS ma ON schaechte.material = ma.bezeichnung
                        WHERE schaechte.schachttyp = 'Auslass' {self.abfrage_s_and}
                        """

            if not self.db_qkan.sql(sql, u"db_qkan: export_auslaesse"):
                return

            fortschritt("Export Auslässe...", 0.25)
            for attr in self.db_qkan.fetchall():

                (
                    schnam,
                    deckelhoehe,
                    sohlhoehe,
                    durchm,
                    xsch,
                    ysch,
                    kommentar,
                    simstatus_nr,
                    entwart_nr,
                    strasse_nam,
                    kntoentyp,
                    baujahr,
                    material,
                ) = attr

                blocks = root.find(
                    f"d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektbezeichnung={schnam}/"
                    "d:Knoten/d:Bauwerk/d:Auslaufbauwerk/../../..", self.NS,)

                if blocks is None:
                    #Daten ergänzen
                    new_item = etree.Element('AbwassertechnischeAnlage')

                    stammdaten = root.find('Stammdatenkollektiv')
                    stammdaten.append(new_item)
                    if baujahr not in (0, '0', None, 'NULL'):
                        _create_children_text(
                            new_item,
                            {
                                "Objektbezeichnung": schnam,
                                "Objektart": str(2),
                                "Status": simstatus_nr,
                                "Baujahr": baujahr,
                                "Entwaesserungsart": entwart_nr,
                                "Kommentar": kommentar,
                            },
                        )
                    else:
                        _create_children_text(
                            new_item,
                            {
                                "Objektbezeichnung": schnam,
                                "Objektart": str(2),
                                "Status": simstatus_nr,
                                "Entwaesserungsart": entwart_nr,
                                "Kommentar": kommentar,
                            },
                        )

                    knoten = SubElement(new_item, "Knoten")
                    SubElementText(knoten, "KnotenTyp", 0)
                    schacht = SubElement(knoten, "Schacht")
                    strasse = SubElement(new_item, "Lage")
                    SubElementText(strasse, "Strassenname", strasse_nam)
                    SubElementText(schacht, "Schachttiefe", round(deckelhoehe - sohlhoehe,2))
                    _create_children(
                        SubElement(knoten, "Bauwerk"), ["Bauwerktyp", "Auslaufbauwerk"]
                    )
                    # geom_knoten = SubElement(
                    #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
                    # )
                    geo = SubElement(new_item, "Geometrie")


                    geom_knoten = SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {
                            "PunktattributAbwasser": "DMP",
                            "Punkthoehe": deckelhoehe,
                            "Rechtswert": xsch,
                            "Hochwert": ysch,
                        },
                    )
                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {"PunktattributAbwasser": "GOK", "Punkthoehe": deckelhoehe},
                    )

                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {
                            "PunktattributAbwasser": "SMP",
                            "Punkthoehe": sohlhoehe,
                            "Rechtswert": xsch,
                            "Hochwert": ysch,
                        },
                    )
                    x = QgsProject.instance().crs().authid()
                    x.replace('EPSG:', '')
                    _create_children_text(
                        geo,
                        {
                            "CRSLage": x,
                        }, )
                fortschritt("Auslässe eingefügt", 0.3)
                if blocks is not None:
                    pass
                    # blocks.find('Status').text = attr[7]
                    # blocks.find('Baujahr').text = attr[12]
            tree.write(self.export_file)


    def _export_schaechte(self) -> None:

        if self.vorlage == "":

            if (
                not getattr(QKan.config.check_export, "export_schaechte", True)
                or not self.stamm
            ):
                return

            sql = f"""
            SELECT
                schaechte.schnam,
                schaechte.deckelhoehe,
                schaechte.sohlhoehe,
                schaechte.durchm,
                schaechte.druckdicht,
                ea.isybau,
                schaechte.strasse,
                schaechte.knotentyp,
                schaechte.kommentar,
                si.isybau,
                x(schaechte.geop) AS xsch,
                y(schaechte.geop) AS ysch,
                schaechte.baujahr
            FROM schaechte
            LEFT JOIN Entwaesserungsarten AS ea
            ON schaechte.entwart = ea.bezeichnung
            LEFT JOIN simulationsstatus AS si ON schaechte.simstatus = si.bezeichnung
            LEFT JOIN material AS ma ON schaechte.material = ma.bezeichnung
            WHERE schaechte.schachttyp = 'Schacht' {self.abfrage_s_and}
            """
            if not self.db_qkan.sql(sql, "db_qkan: export_schaechte"):
                return


            fortschritt("Export Schächte...", 0.35)
            for attr in self.db_qkan.fetchall():

                (
                    schnam,
                    deckelhoehe,
                    sohlhoehe,
                    durchm,
                    druckdicht,
                    entwart_nr,
                    strasse_nam,
                    kntoentyp,
                    kommentar,
                    simstatus_nr,
                    xsch,
                    ysch,
                    baujahr,
                ) = attr

                abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
                if baujahr not in (0, '0', None, 'NULL'):
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": schnam,
                            "Objektart": str(2),
                            "Status": simstatus_nr,
                            "Baujahr": baujahr,
                            "Entwaesserungsart": entwart_nr,
                            "Kommentar": kommentar,
                        },
                    )
                else:
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": schnam,
                            "Objektart": str(2),
                            "Status": simstatus_nr,
                            "Entwaesserungsart": entwart_nr,
                            "Kommentar": kommentar,
                        },
                    )

                knoten = SubElement(abw, "Knoten")
                SubElementText(knoten, "KnotenTyp", 0)
                schacht = SubElement(knoten, "Schacht")
                if deckelhoehe is not None and deckelhoehe>0:
                    SubElementText(schacht, "Schachttiefe", round(deckelhoehe - sohlhoehe,2))
                _create_children(
                    SubElement(knoten, "Schacht"), ["Schachttiefe", "AnzahlAnschluesse"]
                )
                # geom_knoten = SubElement(
                #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
                #
                geo = SubElement(abw, "Geometrie")


                geom_knoten = SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
                _create_children_text(
                    SubElement(geom_knoten, "Punkt"),
                    {
                        "PunktattributAbwasser": "DMP",
                        "Punkthoehe": deckelhoehe,
                        "Rechtswert": xsch,
                        "Hochwert": ysch,
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
                        "Punkthoehe": sohlhoehe,
                        "Rechtswert": xsch,
                        "Hochwert": ysch,
                    },
                )
                x = QgsProject.instance().crs().authid()
                x.replace('EPSG:', '')
                _create_children_text(
                    geo,
                    {
                        "CRSLage": x,
                    }, )

            fortschritt("Schächte eingefügt", 0.4)

        if self.vorlage != "":
            # Daten äbandern oder zu bestehender datei hinzufügen
            tree = etree.parse(self.vorlage)
            root = tree.getroot()

            sql = f"""
                        SELECT
                            schaechte.schnam,
                            schaechte.deckelhoehe,
                            schaechte.sohlhoehe,
                            schaechte.durchm,
                            schaechte.druckdicht,
                            ea.isybau,
                            schaechte.entwart,
                            schaechte.strasse,
                            schaechte.knotentyp,
                            schaechte.kommentar,
                            si.isybau,
                            x(schaechte.geop) AS xsch,
                            y(schaechte.geop) AS ysch,
                            schaechte.baujahr
                        FROM schaechte
                        LEFT JOIN Entwaesserungsarten AS ea
                        ON schaechte.entwart = ea.bezeichnung
                        LEFT JOIN simulationsstatus AS si ON schaechte.simstatus = si.bezeichnung
                        LEFT JOIN material AS ma ON schaechte.material = ma.bezeichnung
                        WHERE schaechte.schachttyp = 'Schacht' {self.abfrage_s_and}
                    """

            if not self.db_qkan.sql(sql, u"db_qkan: export_schaechte"):
                return

            fortschritt("Export Schacht...", 0.25)
            for attr in self.db_qkan.fetchall():

                (
                    schnam,
                    deckelhoehe,
                    sohlhoehe,
                    durchm,
                    xsch,
                    ysch,
                    kommentar,
                    simstatus_nr,
                    entwart_nr,
                    strasse_nam,
                    kntoentyp,
                    baujahr,
                    material,
                ) = attr

                blocks = root.find(
                    f".//d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektbezeichnung={schnam}]/[d:Objektart='2']", self.NS, )

                if blocks is None:
                    # Daten ergänzen
                    new_item = etree.Element('AbwassertechnischeAnlage')

                    stammdaten = root.find('Stammdatenkollektiv')
                    stammdaten.append(new_item)
                    if baujahr not in (0, '0', None, 'NULL'):
                        _create_children_text(
                            new_item,
                            {
                                "Objektbezeichnung": schnam,
                                "Objektart": str(2),
                                "Status": simstatus_nr,
                                "Baujahr": baujahr,
                                "Entwaesserungsart": entwart_nr,
                                "Kommentar": kommentar,
                            },
                        )
                    else:
                        _create_children_text(
                            new_item,
                            {
                                "Objektbezeichnung": schnam,
                                "Objektart": str(2),
                                "Status": simstatus_nr,
                                "Entwaesserungsart": entwart_nr,
                                "Kommentar": kommentar,
                            },
                        )
                    knoten = SubElement(new_item, "Knoten")
                    SubElementText(knoten, "KnotenTyp", 0)
                    schacht = SubElement(knoten, "Schacht")
                    strasse = SubElement(new_item, "Lage")
                    SubElementText(strasse, "Strassenname", strasse_nam)
                    SubElementText(schacht, "Schachttiefe", round(deckelhoehe - sohlhoehe,2))
                    _create_children(
                        SubElement(knoten, "Schacht"), ["Schachttiefe", "AnzahlAnschluesse"]
                    )
                    # geom_knoten = SubElement(
                    #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
                    # )
                    geo = SubElement(new_item, "Geometrie")


                    geom_knoten = SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {
                            "PunktattributAbwasser": "DMP",
                            "Punkthoehe": deckelhoehe,
                            "Rechtswert": xsch,
                            "Hochwert": ysch,
                        },
                    )
                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {"PunktattributAbwasser": "GOK", "Punkthoehe": deckelhoehe},
                    )

                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {
                            "PunktattributAbwasser": "SMP",
                            "Punkthoehe": sohlhoehe,
                            "Rechtswert": xsch,
                            "Hochwert": ysch,
                        },
                    )
                    x = QgsProject.instance().crs().authid()
                    x.replace('EPSG:', '')
                    _create_children_text(
                        geo,
                        {
                            "CRSLage": x,
                        }, )
                fortschritt("Schaechte eingefügt", 0.3)
                if blocks is not None:
                    pass
                    # blocks.find('Status').text = attr[7]
                    # blocks.find('Baujahr').text = attr[12]
            tree.write(self.export_file)

    def _export_speicher(self) -> None:

        if self.vorlage == "":

            if (
                not getattr(QKan.config.check_export, "export_speicher", True)
                or not self.stamm
            ):
                return

            sql = f"""
            SELECT
                schaechte.schnam,
                schaechte.deckelhoehe,
                schaechte.sohlhoehe,
                schaechte.durchm,
                ea.isybau,
                schaechte.strasse,
                x(schaechte.geop) AS xsch,
                y(schaechte.geop) AS ysch,
                schaechte.kommentar,
                si.isybau,
                schaechte.knotentyp,
                schaechte.baujahr
            FROM schaechte
            left join Entwaesserungsarten AS ea
            ON schaechte.entwart = ea.bezeichnung
            LEFT JOIN simulationsstatus AS si ON schaechte.simstatus = si.bezeichnung
            LEFT JOIN material AS ma ON schaechte.material = ma.bezeichnung
            WHERE schaechte.schachttyp = 'Speicher' {self.abfrage_s_and}
            """

            if not self.db_qkan.sql(sql, "db_qkan: export_speicher"):
                return

            fortschritt("Export Speicherschächte...", 0.45)
            for attr in self.db_qkan.fetchall():

                (
                    schnam,
                    deckelhoehe,
                    sohlhoehe,
                    durchm,
                    entwart_nr,
                    strasse_nam,
                    xsch,
                    ysch,
                    kommentar,
                    simstatus_nr,
                    kntoentyp,
                    baujahr,
                ) = attr

                abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
                if baujahr not in (0, '0', None, 'NULL'):
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": schnam,
                            "Objektart": str(2),
                            "Status": simstatus_nr,
                            "Baujahr": baujahr,
                            "Entwaesserungsart": entwart_nr,
                            "Kommentar": kommentar,
                        },
                    )
                else:
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": schnam,
                            "Objektart": str(2),
                            "Status": simstatus_nr,
                            "Entwaesserungsart": entwart_nr,
                            "Kommentar": kommentar,
                        },
                    )

                knoten = SubElement(abw, "Knoten")
                SubElementText(knoten, "KnotenTyp",0)
                bauwerk = SubElement(knoten, "Bauwerk")
                SubElement(bauwerk, "Bauwerkstyp")
                _create_children(
                    SubElement(bauwerk, "Becken"), ["AnzahlZulaeufe", "AnzahlAblaeufe"]
                )

                #geom_knoten = SubElement(
                #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
                #)
                geo = SubElement(abw, "Geometrie")


                geom_knoten= SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
                _create_children_text(
                    SubElement(geom_knoten, "Punkt"),
                    {
                        "PunktattributAbwasser": "DMP",
                        "Punkthoehe": deckelhoehe,
                        "Rechtswert": xsch,
                        "Hochwert": ysch,
                    },
                )
                _create_children_text(
                    SubElement(geom_knoten, "Punkt"),
                    {
                        "PunktattributAbwasser": "SMP",
                        "Punkthoehe": sohlhoehe,
                        "Rechtswert": xsch,
                        "Hochwert": ysch,
                    },
                )
                x = QgsProject.instance().crs().authid()
                x.replace('EPSG:', '')
                _create_children_text(
                    geo,
                    {
                        "CRSLage": x,
                    }, )
            fortschritt("Speicher eingefügt", 0.5)


        if self.vorlage != "":
            # Daten äbandern oder zu bestehender datei hinzufügen
            tree = etree.parse(self.vorlage)
            root = tree.getroot()

            sql = f"""
                        SELECT
                            schaechte.schnam,
                            schaechte.deckelhoehe,
                            schaechte.sohlhoehe,
                            schaechte.durchm,
                            schaechte.druckdicht,
                            ea.isybau,
                            schaechte.entwart,
                            schaechte.strasse,
                            schaechte.knotentyp,
                            schaechte.kommentar,
                            si.isybau,
                            x(schaechte.geop) AS xsch,
                            y(schaechte.geop) AS ysch,
                            schaechte.baujahr
                        FROM schaechte
                        LEFT JOIN Entwaesserungsarten AS ea
                        ON schaechte.entwart = ea.bezeichnung
                        LEFT JOIN simulationsstatus AS si ON schaechte.simstatus = si.bezeichnung
                        LEFT JOIN material AS ma ON schaechte.material = ma.bezeichnung
                        WHERE schaechte.schachttyp = 'Speicher' {self.abfrage_s_and}
                    """

            if not self.db_qkan.sql(sql, u"db_qkan: export_schaechte"):
                return

            fortschritt("Export Speicher...", 0.25)
            for attr in self.db_qkan.fetchall():

                (
                    schnam,
                    deckelhoehe,
                    sohlhoehe,
                    durchm,
                    entwart_nr,
                    strasse_nam,
                    xsch,
                    ysch,
                    kommentar,
                    simstatus_nr,
                    kntoentyp,
                    baujahr,
                ) = attr

                blocks = root.find(
                    f".//d:Datenkollektive/d:Stammdatenkollektiv/d:AbwassertechnischeAnlage/[d:Objektbezeichnung={schnam}/[d:Objektart='2']", self.NS, )

                if blocks is None:
                    # Daten ergänzen
                    new_item = etree.Element('AbwassertechnischeAnlage')

                    stammdaten = root.find('Stammdatenkollektiv')
                    stammdaten.append(new_item)
                    if baujahr not in (0, '0', None, 'NULL'):
                        _create_children_text(
                            new_item,
                            {
                                "Objektbezeichnung": schnam,
                                "Objektart": str(2),
                                "Status": simstatus_nr,
                                "Baujahr": baujahr,
                                "Entwaesserungsart": entwart_nr,
                                "Kommentar": kommentar,
                            },
                        )
                    else:
                        _create_children_text(
                            new_item,
                            {
                                "Objektbezeichnung": schnam,
                                "Objektart": str(2),
                                "Status": simstatus_nr,
                                "Entwaesserungsart": entwart_nr,
                                "Kommentar": kommentar,
                            },
                        )
                    knoten = SubElement(new_item, "Knoten")
                    SubElementText(knoten, "KnotenTyp", 0)
                    bauwerk = SubElement(knoten, "Bauwerk")
                    SubElement(bauwerk, "Bauwerkstyp")
                    _create_children(
                        SubElement(bauwerk, "Becken"), ["AnzahlZulaeufe", "AnzahlAblaeufe"]
                    )
                    # geom_knoten = SubElement(
                    #    SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
                    # )
                    geo = SubElement(new_item, "Geometrie")


                    geom_knoten = SubElement(SubElement(geo, "Geometriedaten"), "Knoten")
                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {
                            "PunktattributAbwasser": "DMP",
                            "Punkthoehe": deckelhoehe,
                            "Rechtswert": xsch,
                            "Hochwert": ysch,
                        },
                    )
                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {"PunktattributAbwasser": "GOK", "Punkthoehe": deckelhoehe},
                    )

                    _create_children_text(
                        SubElement(geom_knoten, "Punkt"),
                        {
                            "PunktattributAbwasser": "SMP",
                            "Punkthoehe": sohlhoehe,
                            "Rechtswert": xsch,
                            "Hochwert": ysch,
                        },
                    )
                    x = QgsProject.instance().crs().authid()
                    x.replace('EPSG:', '')
                    _create_children_text(
                        geo,
                        {
                            "CRSLage": x,
                        }, )
                fortschritt("Speicher eingefügt", 0.3)
                if blocks is not None:
                    pass
                    # blocks.find('Status').text = attr[7]
                    # blocks.find('Baujahr').text = attr[12]

            tree.write(self.export_file)

    def _export_haltungen(self) -> None:

        if self.vorlage == "":

            if (
                not getattr(QKan.config.check_export, "export_haltungen", True)
                #or not self.hydraulik_objekte
                or not self.stamm
            ):
                return

            sql = f"""
            SELECT
                haltungen.haltnam,
                haltungen.schoben,
                haltungen.schunten,
                haltungen.hoehe,
                haltungen.breite,
                haltungen.laenge,
                haltungen.sohleoben,
                haltungen.sohleunten,
                pr.isybau,
                haltungen.strasse,
                ma.isybau,
                ea.isybau,
                haltungen.ks,
                si.bezeichnung,
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
            LEFT JOIN simulationsstatus AS si ON haltungen.simstatus = si.bezeichnung
            LEFT JOIN material AS ma ON haltungen.material = ma.bezeichnung
            LEFT JOIN profile AS pr ON haltungen.profilnam = pr.profilnam
            LEFT JOIN Entwaesserungsarten AS ea 
            ON haltungen.entwart = ea.bezeichnung {self.abfrage_h_where}
            """

            if not self.db_qkan.sql(sql, "db_qkan: export_haltungen"):
                return

            fortschritt("Export Haltungen...", 0.55)

            for attr in self.db_qkan.fetchall():
                (
                    haltnam,
                    schoben,
                    schunten,
                    hoehe,
                    breite,
                    laenge,
                    sohleoben,
                    sohleunten,
                    profilnam_nr,
                    strasse_nam,
                    material,
                    entwart_nr,
                    ks,
                    simstatus_nr,
                    kommentar,
                    xschob,
                    yschob,
                    xschun,
                    yschun,
                    baujahr,
                    aussendurchmesser,
                    profilauskleidung,
                    innenmaterial,
                ) = attr

                obj = SubElement(self.hydraulik_objekte, "HydraulikObjekt")
                _create_children(obj, ["HydObjektTyp", "Objektbezeichnung"])
                _create_children_text(
                    SubElement(obj, "Haltung"),
                    {"Objektbezeichnung": haltnam, "Berechnungslaenge": laenge,"Rauigkeitsansatz": 1, "RauigkeitsbeiwertKb": ks},
                )

                abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
                if baujahr not in (0, '0', None, 'NULL'):
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": haltnam,
                            "Objektart": str(1),
                            "Status": simstatus_nr,
                            "Baujahr": baujahr,
                            "Entwaesserungsart": entwart_nr,
                        },
                    )
                else:
                    _create_children_text(
                        abw,
                        {
                            "Objektbezeichnung": haltnam,
                            "Objektart": str(1),
                            "Status": simstatus_nr,
                            "Entwaesserungsart": entwart_nr,
                        },
                    )

                kante = SubElement(abw, "Kante")
                _create_children_text(
                    kante,
                    {
                        "KantenTyp": 0,
                        "KnotenZulauf": schoben,
                        "KnotenZulaufTyp": 0,
                        "KnotenAblauf": schunten,
                        "KnotenAblaufTyp": 0,
                        "SohlhoeheZulauf": sohleoben,
                        "SohlhoeheAblauf": sohleunten,
                        "Laenge": round(laenge,2),
                        "Material": material,
                    },
                )

                _create_children_text(
                    SubElement(kante, "Profil"),
                    {
                        "ProfilID": None,
                        "SonderprofilVorhanden": 0,
                        "Profilart": profilnam_nr,
                        "Profilbreite": breite,
                        "Profilhoehe": hoehe,
                        "Aussendurchmesser": aussendurchmesser,
                        "Auskleidung": profilauskleidung,
                        "MaterialAuskleidung": innenmaterial,
                    },
                )

                #SubElementText(SubElement(kante, "Haltung"), "DMPLaenge", laenge)

                strasse = SubElement(abw, "Lage")
                _create_children_text(
                    strasse,
                    {
                        "Strassenname": strasse_nam,
                    },
                )

                geom = SubElement(abw, "Geometrie")


                _create_children(geom, ["GeoObjektart", "GeoObjekttyp"])

                kante = SubElement(
                    SubElement(SubElement(geom, "Geometriedaten"), "Kanten"), "Kante"
                )


                _create_children_text(
                    SubElement(kante, "Start"),
                    {
                        "PunktattributAbwasser": "DMP",
                        "Rechtswert": xschob,
                        "Hochwert": yschob,
                        "Punkthoehe": sohleoben,
                    },
                )
                _create_children_text(
                    SubElement(kante, "Ende"),
                    {
                        "PunktattributAbwasser": "DMP",
                        "Rechtswert": xschun,
                        "Hochwert": yschun,
                        "Punkthoehe":sohleunten,
                    },
                )
                x = QgsProject.instance().crs().authid()
                x.replace('EPSG:', '')
                _create_children_text(
                    geom,
                    {
                        "CRSLage": x,
                    }, )

            fortschritt("Haltungen eingefügt", 0.60)

    def _export_anschlussleitungen(self) -> None:

        if self.vorlage == "":

            if (
                not getattr(QKan.config.check_export, "export_anschlussleitungen", True)
                #or not self.hydraulik_objekte
                or not self.stamm
            ):
                return

            if self.abfrage_h_where:
                sql = f"""
                        WITH anschluss_haltung as( SELECT 
                        a.pk AS anschluss_id, 
                         haltungen.pk AS haltung_id
                        FROM anschlussleitungen a
                        JOIN haltungen 
                        ON ST_Intersects(a.geom, haltungen.geom)
                         {self.abfrage_h_where}
                        )
                        
                        SELECT
                        anschlussleitungen.leitnam,
                        anschlussleitungen.schoben,
                        anschlussleitungen.schunten,
                        anschlussleitungen.hoehe,
                        anschlussleitungen.breite,
                        anschlussleitungen.laenge,
                        anschlussleitungen.sohleoben,
                        anschlussleitungen.sohleunten,
                        pr.isybau,
                        ma.isybau,
                        ea.isybau,
                        anschlussleitungen.ks,
                        si.isybau,
                        anschlussleitungen.kommentar,
                        x(PointN(anschlussleitungen.geom, 1)) AS xschob,
                        y(PointN(anschlussleitungen.geom, 1)) AS yschob,
                        x(PointN(anschlussleitungen.geom, -1)) AS xschun,
                        y(PointN(anschlussleitungen.geom, -1)) AS yschun
                    FROM anschlussleitungen
                    LEFT JOIN Entwaesserungsarten AS ea 
                    ON anschlussleitungen.entwart = ea.bezeichnung
                    LEFT JOIN simulationsstatus AS si ON anschlussleitungen.simstatus = si.bezeichnung
                    LEFT JOIN material AS ma ON anschlussleitungen.material = ma.bezeichnung
                    LEFT JOIN profile AS pr ON anschlussleitungen.profilnam = pr.profilnam
                    INNER JOIN anschluss_haltung  ah
                    ON anschlussleitungen.pk =ah.anschluss_id
                        """

                if not self.db_qkan.sql(sql, "db_qkan: export_anschlussleitungen"):
                    return


            else:
                sql = f"""
                        SELECT
                            anschlussleitungen.leitnam,
                            anschlussleitungen.schoben,
                            anschlussleitungen.schunten,
                            anschlussleitungen.hoehe,
                            anschlussleitungen.breite,
                            anschlussleitungen.laenge,
                            anschlussleitungen.sohleoben,
                            anschlussleitungen.sohleunten,
                            pr.isybau,
                            ma.isybau,
                            ea.isybau,
                            anschlussleitungen.ks,
                            si.isybau,
                            anschlussleitungen.kommentar,
                            x(PointN(anschlussleitungen.geom, 1)) AS xschob,
                            y(PointN(anschlussleitungen.geom, 1)) AS yschob,
                            x(PointN(anschlussleitungen.geom, -1)) AS xschun,
                            y(PointN(anschlussleitungen.geom, -1)) AS yschun
                        FROM anschlussleitungen
                        LEFT JOIN Entwaesserungsarten AS ea 
                        ON anschlussleitungen.entwart = ea.bezeichnung 
                        LEFT JOIN simulationsstatus AS si ON anschlussleitungen.simstatus = si.bezeichnung
                        LEFT JOIN material AS ma ON anschlussleitungen.material = ma.bezeichnung
                        LEFT JOIN profile AS pr ON anschlussleitungen.profilnam = pr.profilnam
                        """

                if not self.db_qkan.sql(sql, "db_qkan: export_anschlussleitungen"):
                    return

            fortschritt("Export Anschlussleitungen...", 0.65)

            for attr in self.db_qkan.fetchall():
                (
                    leitnam,
                    schoben,
                    schunten,
                    hoehe,
                    breite,
                    laenge,
                    sohleoben,
                    sohleunten,
                    profilnam_nr,
                    material,
                    entwart_nr,
                    ks,
                    simstatus_nr,
                    kommentar,
                    xschob,
                    yschob,
                    xschun,
                    yschun,
                ) = attr

                obj = SubElement(self.hydraulik_objekte, "HydraulikObjekt")
                _create_children(obj, ["HydObjektTyp", "Objektbezeichnung"])
                _create_children_text(
                    SubElement(obj, "Leitung"),
                    {"Objektbezeichnung": leitnam, "Berechnungslaenge": laenge, "Rauigkeitsansatz": 1,  "RauigkeitsbeiwertKb": ks},
                )

                abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
                _create_children_text(
                    abw,
                    {
                        "Objektbezeichnung": leitnam,
                        "Objektart": str(1),
                        "Entwaesserungsart": entwart_nr,
                        "Status": simstatus_nr,
                    },
                )

                kante = SubElement(abw, "Kante")
                _create_children_text(
                    kante,
                    {
                        "KantenTyp": 1,
                        "KnotenZulauf": schoben,
                        "KnotenZulaufTyp": 0,
                        "KnotenAblauf": schunten,
                        "KnotenAblaufTyp": 0,
                        "Material": material,
                        "SohlhoeheZulauf": sohleoben,
                        "SohlhoeheAblauf": sohleunten,
                        "Laenge": round(laenge,2),
                    },
                )

                _create_children_text(
                    SubElement(kante, "Profil"),
                    {
                        "ProfilID": None,
                        "SonderprofilVorhanden": 0,
                        "Profilart": profilnam_nr,
                        "Profilbreite": breite,
                        "Profilhoehe": hoehe,
                    },
                )

                #SubElementText(SubElement(kante, "Leitung"), "DMPLaenge", laenge)

                geom = SubElement(abw, "Geometrie")

                _create_children(geom, ["GeoObjektart", "GeoObjekttyp"])

                kante = SubElement(
                    SubElement(SubElement(geom, "Geometriedaten"), "Kanten"), "Kante"
                )
                _create_children_text(
                    SubElement(kante, "Start"),
                    {
                        "PunktattributAbwasser": "DMP",
                        "Rechtswert": xschob,
                        "Hochwert":yschob,
                    },
                )
                _create_children_text(
                    SubElement(kante, "Ende"),
                    {
                        "PunktattributAbwasser": "DMP",
                        "Rechtswert": xschun,
                        "Hochwert": yschun,
                    },
                )
                x = QgsProject.instance().crs().authid()
                x.replace('EPSG:', '')
                _create_children_text(
                    geom,
                    {
                        "CRSLage": x,
                    }, )

            fortschritt("Leitung eingefügt", 0.7)

#TODO abhier weiter die referenzdaten verknüpfen
    def _export_zustandsdaten_haltungen(self):
        if self.vorlage == "":

            if (
                    not getattr(QKan.config.check_export, "export_zustandsdaten", True)
                    # or not self.hydraulik_objekte
                    or not self.zustand
            ):
                return

            #Haltungen

            last_pk = None


            if self.auswahl_zustand == "Stammdaten":

                sql = f"""
                 SELECT
                    haltungen_untersucht.pk,
                    haltungen_untersucht.haltnam,
                    haltungen_untersucht.bezugspunkt,
                    haltungen_untersucht.schoben,
                    haltungen_untersucht.schunten,
                    haltungen_untersucht.hoehe,
                    haltungen_untersucht.breite,
                    haltungen_untersucht.laenge,
                    haltungen_untersucht.baujahr,
                    haltungen_untersucht.untersuchtag,
                    haltungen_untersucht.untersucher,
                    haltungen_untersucht.untersuchrichtung,
                    haltungen_untersucht.wetter,
                    haltungen_untersucht.bewertungsart,
                    haltungen_untersucht.bewertungstag,
                    haltungen_untersucht.strasse,
                    haltungen_untersucht.datenart,
                    haltungen_untersucht.auftragsbezeichnung,
                    haltungen_untersucht.max_ZD,
                    haltungen_untersucht.max_ZB,
                    haltungen_untersucht.max_ZS,
                    x(PointN(haltungen_untersucht.geom, 1)) AS xschob,
                    y(PointN(haltungen_untersucht.geom, 1)) AS yschob,
                    x(PointN(haltungen_untersucht.geom, -1)) AS xschun,
                    y(PointN(haltungen_untersucht.geom, -1)) AS yschun,
                    haltungen_untersucht.kommentar,
                    untersuchdat_haltung.station,
                    untersuchdat_haltung.timecode,
                    untersuchdat_haltung.kuerzel,
                    untersuchdat_haltung.charakt1,
                    untersuchdat_haltung.charakt2,
                    untersuchdat_haltung.quantnr1,
                    untersuchdat_haltung.quantnr2,
                    untersuchdat_haltung.streckenschaden,
                    untersuchdat_haltung.streckenschaden_lfdnr,
                    untersuchdat_haltung.pos_von,
                    untersuchdat_haltung.pos_bis,
                    untersuchdat_haltung.foto_dateiname,
                    untersuchdat_haltung.ZD,
                    untersuchdat_haltung.ZB,
                    untersuchdat_haltung.ZS,
                    haltungen.profilnam,
                    haltungen.material,
                    haltungen.entwart
                    FROM haltungen_untersucht
                    JOIN untersuchdat_haltung 
                    JOIN haltungen where haltungen_untersucht.haltnam = untersuchdat_haltung.untersuchhal and haltungen_untersucht.haltnam = haltungen.haltnam
                    {self.abfrage_h_and}
                    """

                if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                    return

            elif self.auswahl_zustand == "Bewertet (Zustandsklassifizierung)":

                sql = f"""
                 SELECT
                    haltungen_untersucht_bewertung.pk,
                    haltungen_untersucht_bewertung.haltnam,
                    haltungen_untersucht_bewertung.bezugspunkt,
                    haltungen_untersucht_bewertung.schoben,
                    haltungen_untersucht_bewertung.schunten,
                    haltungen_untersucht_bewertung.hoehe,
                    haltungen_untersucht_bewertung.breite,
                    haltungen_untersucht_bewertung.laenge,
                    haltungen_untersucht_bewertung.baujahr,
                    haltungen_untersucht_bewertung.untersuchtag,
                    haltungen_untersucht_bewertung.untersucher,
                    haltungen_untersucht_bewertung.untersuchrichtung,
                    haltungen_untersucht_bewertung.wetter,
                    haltungen_untersucht_bewertung.bewertungsart,
                    haltungen_untersucht_bewertung.bewertungstag,
                    haltungen_untersucht_bewertung.strasse,
                    haltungen_untersucht_bewertung.datenart,
                    haltungen_untersucht_bewertung.auftragsbezeichnung,
                    haltungen_untersucht_bewertung.max_ZD,
                    haltungen_untersucht_bewertung.max_ZB,
                    haltungen_untersucht_bewertung.max_ZS,
                    x(PointN(haltungen_untersucht_bewertung.geom, 1)) AS xschob,
                    y(PointN(haltungen_untersucht_bewertung.geom, 1)) AS yschob,
                    x(PointN(haltungen_untersucht_bewertung.geom, -1)) AS xschun,
                    y(PointN(haltungen_untersucht_bewertung.geom, -1)) AS yschun,
                    haltungen_untersucht_bewertung.kommentar,
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
                    untersuchdat_haltung_bewertung.ZD,
                    untersuchdat_haltung_bewertung.ZB,
                    untersuchdat_haltung_bewertung.ZS,
                    haltungen.profilnam,
                    haltungen.material,
                    haltungen.entwart
                    FROM haltungen_untersucht_bewertung
                    JOIN untersuchdat_haltung_bewertung 
                    JOIN haltungen where haltungen_untersucht_bewertung.haltnam = untersuchdat_haltung_bewertung.untersuchhal and haltungen_untersucht_bewertung.haltnam = haltungen.haltnam
                    {self.abfrage_h_and}
                    """

                if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                    return

            elif self.auswahl_zustand == "Bewertet (Substanzklassifizierung)":

                sql = f"""
                 SELECT
                    haltungen_substanz_bewertung.pk,
                    haltungen_substanz_bewertung.haltnam,
                    NULL,
                    haltungen_substanz_bewertung.schoben,
                    haltungen_substanz_bewertung.schunten,
                    haltungen_substanz_bewertung.hoehe,
                    haltungen_substanz_bewertung.breite,
                    haltungen_substanz_bewertung.laenge,
                    haltungen_substanz_bewertung.baujahr,
                    haltungen_substanz_bewertung.untersuchtag,
                    haltungen_substanz_bewertung.untersucher,
                    NULL,
                    haltungen_substanz_bewertung.wetter,
                    haltungen_substanz_bewertung.bewertungsart,
                    haltungen_substanz_bewertung.bewertungstag,
                    haltungen_substanz_bewertung.strasse,
                    haltungen_substanz_bewertung.datenart,
                    NULL,
                    haltungen_substanz_bewertung.max_ZD,
                    haltungen_substanz_bewertung.max_ZB,
                    haltungen_substanz_bewertung.max_ZS,
                    x(PointN(haltungen_substanz_bewertung.geom, 1)) AS xschob,
                    y(PointN(haltungen_substanz_bewertung.geom, 1)) AS yschob,
                    x(PointN(haltungen_substanz_bewertung.geom, -1)) AS xschun,
                    y(PointN(haltungen_substanz_bewertung.geom, -1)) AS yschun,
                    NULL,
                    substanz_haltung_bewertung.station,
                    substanz_haltung_bewertung.timecode,
                    substanz_haltung_bewertung.kuerzel,
                    substanz_haltung_bewertung.charakt1,
                    substanz_haltung_bewertung.charakt2,
                    substanz_haltung_bewertung.quantnr1,
                    substanz_haltung_bewertung.quantnr2,
                    substanz_haltung_bewertung.streckenschaden,
                    substanz_haltung_bewertung.streckenschaden_lfdnr,
                    substanz_haltung_bewertung.pos_von,
                    substanz_haltung_bewertung.pos_bis,
                    substanz_haltung_bewertung.foto_dateiname,
                    substanz_haltung_bewertung.Zustandsklasse_D,
                    substanz_haltung_bewertung.Zustandsklasse_B,
                    substanz_haltung_bewertung.Zustandsklasse_S,
                    haltungen.profilnam,
                    haltungen.material,
                    haltungen.entwart
                    FROM haltungen_substanz_bewertung
                    JOIN substanz_haltung_bewertung 
                    JOIN haltungen where haltungen_substanz_bewertung.haltnam = substanz_haltung_bewertung.untersuchhal and haltungen_substanz_bewertung.haltnam = haltungen.haltnam
                    {self.abfrage_h_and}
                    """

                if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                    return

            #fortschritt("Export Zustandsdaten...", 0.55)

            for attr in self.db_qkan.fetchall():

                (
                    pk,
                    haltnam,
                    bezugspunkt,
                    schoben,
                    schunten,
                    hoehe,
                    breite,
                    laenge,
                    baujahr,
                    untersuchtag,
                    untersucher,
                    untersuchrichtung,
                    wetter_nr,
                    bewertungsart,
                    bewertungstag,
                    strasse_nam,
                    datenart,
                    auftragsbezeichnung,
                    max_ZD,
                    max_ZB,
                    max_ZS,
                    xschob,
                    yschob,
                    xschun,
                    yschun,
                    kommentar,
                    station,
                    timekode,
                    kuerzel,
                    charakt1,
                    charakt2,
                    quantnr1,
                    quantnr2,
                    streckenschaden,
                    streckenschadenlfdnr,
                    posvon,
                    posbis,
                    foto,
                    zd,
                    zb,
                    zs,
                    profilnam_nr,
                    material,
                    entwart_nr,
                ) = attr

                if pk != last_pk:
                    insp = SubElement(self.zustand, "InspizierteAbwassertechnischeAnlage")
                    _create_children_text(
                        insp,
                        {
                            "Objektbezeichnung": haltnam,
                            "Anlagentyp": str(1),
                        },
                    )

                    strasse = SubElement(insp, "Lage")
                    _create_children_text(
                        strasse,
                        {
                            "Strassenname": strasse_nam,
                        },
                    )

                    for de in sorted(month_map, key=len, reverse=True):
                        untersuchtag = untersuchtag.replace(de, month_map[de])

                    tag, monat, jahr = untersuchtag.replace(".", "").split()

                    datum = f"{jahr}-{monat}-{int(tag):02d}"

                    opt = SubElement(insp, "OptischeInspektion")
                    if wetter_nr not in (0,'0', None,'NULL'):
                        _create_children_text(
                            opt,
                            {
                                "Auftragskennung": 1,
                                "Inspektionsdatum": datum,
                                "NameUntersucher": untersucher,
                                "Wetter": wetter_nr,
                            },
                        )
                    else:
                        _create_children_text(
                            opt,
                            {
                                "Auftragskennung": 1,
                                "Inspektionsdatum": datum,
                                "NameUntersucher": untersucher,
                            },
                        )


                    rohr = SubElement(opt, "Rohrleitung")
                    _create_children_text(
                        rohr,
                        {
                            "Rohrleitungstyp": 0,
                            "Inspektionsrichtung": untersuchrichtung,
                            "Bezugspunktlage": bezugspunkt,
                            "Inspektionslaenge": laenge,
                        },
                    )

                    rgrund = SubElement(rohr, "RGrunddaten")
                    _create_children_text(
                        rgrund,
                        {
                            "KnotenZulauf": 0,
                            "KnotenZulauftyp": schoben,
                            "KnotenAblauf": 0,
                            "KnotenAblauftyp": schunten,
                            "Profilhoehe": hoehe,
                            "Profilbreite": breite,
                            "Profilart": profilnam_nr,
                            "Material": material,
                            "Kanalart": entwart_nr,
                        },
                    )
                    inspdat = SubElement(rohr, "Inspektionsdaten")

                    last_pk = pk


                    rzu = SubElement(inspdat, "RZustand")
                    _create_children_text(
                        rzu,
                        {
                            "Station": station,
                            "Timecode": timekode,
                            "InspektionsKode": kuerzel,
                            "Charakterisierung1": charakt1,
                            "Charakterisierung2": charakt2,
                            "Quantifizierung1Numerisch": quantnr1,
                            "Quantifizierung2Numerisch": quantnr2,
                            "Streckenschaden": streckenschaden,
                            "StreckenschadenLfdNr": streckenschadenlfdnr,
                            "PositionVon": posvon,
                            "PositionBis": posbis,
                            "Fotodatei": foto,
                        },
                    )
                    kl = SubElement(rzu, "Klassifizierung")
                    _create_children_text(
                        kl,
                        {
                            "Dichtheit": zd,
                            "Standsicherheit": zs,
                            "Betriebssicherheit": zb,
                        },
                    )

    def _export_zustandsdaten_anschlussleitungen(self):
        if self.vorlage == "":

            if (
                    not getattr(QKan.config.check_export, "export_zustandsdaten", True)
                    # or not self.hydraulik_objekte
                    or not self.zustand
            ):
                return

            # Haltungen

            last_pk = None
            if self.auswahl_zustand == "Stammdaten":

                if self.abfrage_h_where:
                    sql = f"""
                            WITH anschluss_haltung as( SELECT 
                                    a.leitnam AS leitnam, 
                                    haltungen.pk AS haltung_id
                                FROM anschlussleitungen a
                                JOIN haltungen 
                                ON ST_Intersects(a.geom, haltungen.geom)
                                {self.abfrage_h_where}
                                )
                                
                                SELECT
                            anschlussleitungen_untersucht.pk,
                            anschlussleitungen_untersucht.leitnam,
                            anschlussleitungen_untersucht.bezugspunkt,
                            anschlussleitungen_untersucht.schoben,
                            anschlussleitungen_untersucht.schunten,
                            anschlussleitungen_untersucht.hoehe,
                            anschlussleitungen_untersucht.breite,
                            anschlussleitungen_untersucht.laenge,
                            anschlussleitungen_untersucht.baujahr,
                            anschlussleitungen_untersucht.untersuchtag,
                            anschlussleitungen_untersucht.untersucher,
                            anschlussleitungen_untersucht.untersuchrichtung,
                            anschlussleitungen_untersucht.wetter,
                            anschlussleitungen_untersucht.bewertungsart,
                            anschlussleitungen_untersucht.bewertungstag,
                            anschlussleitungen_untersucht.strasse,
                            anschlussleitungen_untersucht.datenart,
                            anschlussleitungen_untersucht.auftragsbezeichnung,
                            anschlussleitungen_untersucht.max_ZD,
                            anschlussleitungen_untersucht.max_ZB,
                            anschlussleitungen_untersucht.max_ZS,
                            x(PointN(anschlussleitungen_untersucht.geom, 1)) AS xschob,
                            y(PointN(anschlussleitungen_untersucht.geom, 1)) AS yschob,
                            x(PointN(anschlussleitungen_untersucht.geom, -1)) AS xschun,
                            y(PointN(anschlussleitungen_untersucht.geom, -1)) AS yschun,
                            anschlussleitungen_untersucht.kommentar,
                            untersuchdat_anschlussleitung.station,
                            untersuchdat_anschlussleitung.timecode,
                            untersuchdat_anschlussleitung.kuerzel,
                            untersuchdat_anschlussleitung.charakt1,
                            untersuchdat_anschlussleitung.charakt2,
                            untersuchdat_anschlussleitung.quantnr1,
                            untersuchdat_anschlussleitung.quantnr2,
                            untersuchdat_anschlussleitung.streckenschaden,
                            untersuchdat_anschlussleitung.streckenschaden_lfdnr,
                            untersuchdat_anschlussleitung.pos_von,
                            untersuchdat_anschlussleitung.pos_bis,
                            untersuchdat_anschlussleitung.foto_dateiname,
                            untersuchdat_anschlussleitung.ZD,
                            untersuchdat_anschlussleitung.ZB,
                            untersuchdat_anschlussleitung.ZS,
                            anschlussleitungen.profilnam,
                            anschlussleitungen.material,
                            anschlussleitungen.entwart
                            FROM anschlussleitungen_untersucht
                            JOIN untersuchdat_anschlussleitung  ON anschlussleitungen_untersucht.leitnam = untersuchdat_anschlussleitung.untersuchleit
                            JOIN anschlussleitungen ON anschlussleitungen_untersucht.leitnam = anschlussleitungen.leitnam
                            LEFT JOIN Entwaesserungsarten ea
                            ON anschlussleitungen.entwart = ea.bezeichnung
                            INNER JOIN anschluss_haltung ah
                            ON anschlussleitungen.leitnam = ah.leitnam;
                                """

                    if not self.db_qkan.sql(sql, "db_qkan: export_anschlussleitungen"):
                        return

                else:

                    sql = f"""
                     SELECT
                        anschlussleitungen_untersucht.pk,
                        anschlussleitungen_untersucht.leitnam,
                        anschlussleitungen_untersucht.bezugspunkt,
                        anschlussleitungen_untersucht.schoben,
                        anschlussleitungen_untersucht.schunten,
                        anschlussleitungen_untersucht.hoehe,
                        anschlussleitungen_untersucht.breite,
                        anschlussleitungen_untersucht.laenge,
                        anschlussleitungen_untersucht.baujahr,
                        anschlussleitungen_untersucht.untersuchtag,
                        anschlussleitungen_untersucht.untersucher,
                        anschlussleitungen_untersucht.untersuchrichtung,
                        anschlussleitungen_untersucht.wetter,
                        anschlussleitungen_untersucht.bewertungsart,
                        anschlussleitungen_untersucht.bewertungstag,
                        anschlussleitungen_untersucht.strasse,
                        anschlussleitungen_untersucht.datenart,
                        anschlussleitungen_untersucht.auftragsbezeichnung,
                        anschlussleitungen_untersucht.max_ZD,
                        anschlussleitungen_untersucht.max_ZB,
                        anschlussleitungen_untersucht.max_ZS,
                        x(PointN(anschlussleitungen_untersucht.geom, 1)) AS xschob,
                        y(PointN(anschlussleitungen_untersucht.geom, 1)) AS yschob,
                        x(PointN(anschlussleitungen_untersucht.geom, -1)) AS xschun,
                        y(PointN(anschlussleitungen_untersucht.geom, -1)) AS yschun,
                        anschlussleitungen_untersucht.kommentar,
                        untersuchdat_anschlussleitung.station,
                        untersuchdat_anschlussleitung.timecode,
                        untersuchdat_anschlussleitung.kuerzel,
                        untersuchdat_anschlussleitung.charakt1,
                        untersuchdat_anschlussleitung.charakt2,
                        untersuchdat_anschlussleitung.quantnr1,
                        untersuchdat_anschlussleitung.quantnr2,
                        untersuchdat_anschlussleitung.streckenschaden,
                        untersuchdat_anschlussleitung.streckenschaden_lfdnr,
                        untersuchdat_anschlussleitung.pos_von,
                        untersuchdat_anschlussleitung.pos_bis,
                        untersuchdat_anschlussleitung.foto_dateiname,
                        untersuchdat_anschlussleitung.ZD,
                        untersuchdat_anschlussleitung.ZB,
                        untersuchdat_anschlussleitung.ZS,
                        anschlussleitungen.profilnam,
                        anschlussleitungen.material,
                        anschlussleitungen.entwart
                        FROM anschlussleitungen_untersucht
                        JOIN untersuchdat_anschlussleitung 
                        JOIN anschlussleitungen where anschlussleitungen_untersucht.leitnam = untersuchdat_anschlussleitung.untersuchleit and anschlussleitungen_untersucht.leitnam = anschlussleitungen.leitnam
                        """

                    if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                        return

            elif self.auswahl_zustand == "Bewertet (Zustandsklassifizierung)":

                if self.abfrage_h_where:
                    sql = f"""
                            WITH anschluss_haltung as( SELECT 
                                    a.leitnam AS leitnam, 
                                    haltungen.pk AS haltung_id
                                FROM anschlussleitungen a
                                JOIN haltungen 
                                ON ST_Intersects(a.geom, haltungen.geom)
                                {self.abfrage_h_where}
                                )

                                SELECT
                            anschlussleitungen_untersucht_bewertet.pk,
                            anschlussleitungen_untersucht_bewertet.leitnam,
                            anschlussleitungen_untersucht_bewertet.bezugspunkt,
                            anschlussleitungen_untersucht_bewertet.schoben,
                            anschlussleitungen_untersucht_bewertet.schunten,
                            anschlussleitungen_untersucht_bewertet.hoehe,
                            anschlussleitungen_untersucht_bewertet.breite,
                            anschlussleitungen_untersucht_bewertet.laenge,
                            anschlussleitungen_untersucht_bewertet.baujahr,
                            anschlussleitungen_untersucht_bewertet.untersuchtag,
                            anschlussleitungen_untersucht_bewertet.untersucher,
                            anschlussleitungen_untersucht_bewertet.untersuchrichtung,
                            anschlussleitungen_untersucht_bewertet.wetter,
                            anschlussleitungen_untersucht_bewertet.bewertungsart,
                            anschlussleitungen_untersucht_bewertet.bewertungstag,
                            anschlussleitungen_untersucht_bewertet.strasse,
                            anschlussleitungen_untersucht_bewertet.datenart,
                            anschlussleitungen_untersucht_bewertet.auftragsbezeichnung,
                            anschlussleitungen_untersucht_bewertet.max_ZD,
                            anschlussleitungen_untersucht_bewertet.max_ZB,
                            anschlussleitungen_untersucht_bewertet.max_ZS,
                            x(PointN(anschlussleitungen_untersucht_bewertet.geom, 1)) AS xschob,
                            y(PointN(anschlussleitungen_untersucht_bewertet.geom, 1)) AS yschob,
                            x(PointN(anschlussleitungen_untersucht_bewertet.geom, -1)) AS xschun,
                            y(PointN(anschlussleitungen_untersucht_bewertet.geom, -1)) AS yschun,
                            anschlussleitungen_untersucht_bewertet.kommentar,
                            untersuchdat_anschlussleitung_bewertet.station,
                            untersuchdat_anschlussleitung_bewertet.timecode,
                            untersuchdat_anschlussleitung_bewertet.kuerzel,
                            untersuchdat_anschlussleitung_bewertet.charakt1,
                            untersuchdat_anschlussleitung_bewertet.charakt2,
                            untersuchdat_anschlussleitung_bewertet.quantnr1,
                            untersuchdat_anschlussleitung_bewertet.quantnr2,
                            untersuchdat_anschlussleitung_bewertet.streckenschaden,
                            untersuchdat_anschlussleitung_bewertet.streckenschaden_lfdnr,
                            untersuchdat_anschlussleitung_bewertet.pos_von,
                            untersuchdat_anschlussleitung_bewertet.pos_bis,
                            untersuchdat_anschlussleitung_bewertet.foto_dateiname,
                            untersuchdat_anschlussleitung_bewertet.ZD,
                            untersuchdat_anschlussleitung_bewertet.ZB,
                            untersuchdat_anschlussleitung_bewertet.ZS,
                            anschlussleitungen.profilnam,
                            anschlussleitungen.material,
                            anschlussleitungen.entwart
                            FROM anschlussleitungen_untersucht
                            JOIN untersuchdat_anschlussleitung_bewertet  ON anschlussleitungen_untersucht_bewertet.leitnam = untersuchdat_anschlussleitung_bewertet.untersuchleit
                            JOIN anschlussleitungen ON anschlussleitungen_untersucht_bewertet.leitnam = anschlussleitungen.leitnam
                            LEFT JOIN Entwaesserungsarten ea
                            ON anschlussleitungen.entwart = ea.bezeichnung
                            INNER JOIN anschluss_haltung ah
                            ON anschlussleitungen.leitnam = ah.leitnam;
                                """

                    if not self.db_qkan.sql(sql, "db_qkan: export_anschlussleitungen"):
                        return

                else:

                    sql = f"""
                     SELECT
                        anschlussleitungen_untersucht_bewertet.pk,
                        anschlussleitungen_untersucht_bewertet.leitnam,
                        anschlussleitungen_untersucht_bewertet.bezugspunkt,
                        anschlussleitungen_untersucht_bewertet.schoben,
                        anschlussleitungen_untersucht_bewertet.schunten,
                        anschlussleitungen_untersucht_bewertet.hoehe,
                        anschlussleitungen_untersucht_bewertet.breite,
                        anschlussleitungen_untersucht_bewertet.laenge,
                        anschlussleitungen_untersucht_bewertet.baujahr,
                        anschlussleitungen_untersucht_bewertet.untersuchtag,
                        anschlussleitungen_untersucht_bewertet.untersucher,
                        anschlussleitungen_untersucht_bewertet.untersuchrichtung,
                        anschlussleitungen_untersucht_bewertet.wetter,
                        anschlussleitungen_untersucht_bewertet.bewertungsart,
                        anschlussleitungen_untersucht_bewertet.bewertungstag,
                        anschlussleitungen_untersucht_bewertet.strasse,
                        anschlussleitungen_untersucht_bewertet.datenart,
                        anschlussleitungen_untersucht_bewertet.auftragsbezeichnung,
                        anschlussleitungen_untersucht_bewertet.max_ZD,
                        anschlussleitungen_untersucht_bewertet.max_ZB,
                        anschlussleitungen_untersucht_bewertet.max_ZS,
                        x(PointN(anschlussleitungen_untersucht_bewertet.geom, 1)) AS xschob,
                        y(PointN(anschlussleitungen_untersucht_bewertet.geom, 1)) AS yschob,
                        x(PointN(anschlussleitungen_untersucht_bewertet.geom, -1)) AS xschun,
                        y(PointN(anschlussleitungen_untersucht_bewertet.geom, -1)) AS yschun,
                        anschlussleitungen_untersucht_bewertet.kommentar,
                        untersuchdat_anschlussleitung_bewertet.station,
                        untersuchdat_anschlussleitung_bewertet.timecode,
                        untersuchdat_anschlussleitung_bewertet.kuerzel,
                        untersuchdat_anschlussleitung_bewertet.charakt1,
                        untersuchdat_anschlussleitung_bewertet.charakt2,
                        untersuchdat_anschlussleitung_bewertet.quantnr1,
                        untersuchdat_anschlussleitung_bewertet.quantnr2,
                        untersuchdat_anschlussleitung_bewertet.streckenschaden,
                        untersuchdat_anschlussleitung_bewertet.streckenschaden_lfdnr,
                        untersuchdat_anschlussleitung_bewertet.pos_von,
                        untersuchdat_anschlussleitung_bewertet.pos_bis,
                        untersuchdat_anschlussleitung_bewertet.foto_dateiname,
                        untersuchdat_anschlussleitung_bewertet.ZD,
                        untersuchdat_anschlussleitung_bewertet.ZB,
                        untersuchdat_anschlussleitung_bewertet.ZS,
                        anschlussleitungen.profilnam,
                        anschlussleitungen.material,
                        anschlussleitungen.entwart
                        FROM anschlussleitungen_untersucht_bewertet
                        JOIN untersuchdat_anschlussleitung_bewertet 
                        JOIN anschlussleitungen where anschlussleitungen_untersucht_bewertet.leitnam = untersuchdat_anschlussleitung_bewertet.untersuchleit and anschlussleitungen_untersucht_bewertet.leitnam = anschlussleitungen.leitnam

                        """

                    if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                        return

            # fortschritt("Export Zustandsdaten...", 0.55)

            for attr in self.db_qkan.fetchall():

                (
                    pk,
                    haltnam,
                    bezugspunkt,
                    schoben,
                    schunten,
                    hoehe,
                    breite,
                    laenge,
                    baujahr,
                    untersuchtag,
                    untersucher,
                    untersuchrichtung,
                    wetter_nr,
                    bewertungsart,
                    bewertungstag,
                    strasse_nam,
                    datenart,
                    auftragsbezeichnung,
                    max_ZD,
                    max_ZB,
                    max_ZS,
                    xschob,
                    yschob,
                    xschun,
                    yschun,
                    kommentar,
                    station,
                    timekode,
                    kuerzel,
                    charakt1,
                    charakt2,
                    quantnr1,
                    quantnr2,
                    streckenschaden,
                    streckenschadenlfdnr,
                    posvon,
                    posbis,
                    foto,
                    zd,
                    zs,
                    zb,
                    profilnam_nr,
                    material,
                    entwart_nr,
                ) = attr

                if pk != last_pk:
                    insp = SubElement(self.zustand, "InspizierteAbwassertechnischeAnlage")
                    _create_children_text(
                        insp,
                        {
                            "Objektbezeichnung": haltnam,
                            "Anlagentyp": str(2),
                        },
                    )

                    strasse = SubElement(insp, "Lage")
                    _create_children_text(
                        strasse,
                        {
                            "Strassenname": strasse_nam,
                        },
                    )

                    for de in sorted(month_map, key=len, reverse=True):
                        untersuchtag = untersuchtag.replace(de, month_map[de])

                    tag, monat, jahr = untersuchtag.replace(".", "").split()

                    datum = f"{jahr}-{monat}-{int(tag):02d}"

                    opt = SubElement(insp, "OptischeInspektion")
                    if wetter_nr not in (0, '0', None, 'NULL'):
                        _create_children_text(
                            opt,
                            {
                                "Auftragskennung": 1,
                                "Inspektionsdatum": datum,
                                "NameUntersucher": untersucher,
                                "Wetter": wetter_nr,
                            },
                        )
                    else:
                        _create_children_text(
                            opt,
                            {
                                "Auftragskennung": 1,
                                "Inspektionsdatum": datum,
                                "NameUntersucher": untersucher,
                            },
                        )


                    rohr = SubElement(opt, "Rohrleitung")
                    _create_children_text(
                        rohr,
                        {
                            "Rohrleitungstyp": 1,
                            "Inspektionsrichtung": untersuchrichtung,
                            "Bezugspunktlage": bezugspunkt,
                            "Inspektionslaenge": laenge,
                        },
                    )

                    rgrund = SubElement(rohr, "RGrunddaten")
                    _create_children_text(
                        rgrund,
                        {
                            "KnotenZulauf": 0,
                            "KnotenZulauftyp": schoben,
                            "KnotenAblauf": 0,
                            "KnotenAblauftyp": schunten,
                            "Profilhoehe": hoehe,
                            "Profilbreite": breite,
                            "Profilart": profilnam_nr,
                            "Material": material,
                            "Kanalart": entwart_nr,
                        },
                    )
                    inspdat = SubElement(rohr, "Inspektionsdaten")

                    last_pk = pk

                    rzu = SubElement(inspdat, "RZustand")
                    _create_children_text(
                        rzu,
                        {
                            "Station": station,
                            "Timecode": timekode,
                            "InspektionsKode": kuerzel,
                            "Charakterisierung1": charakt1,
                            "Charakterisierung2": charakt2,
                            "Quantifizierung1Numerisch": quantnr1,
                            "Quantifizierung2Numerisch": quantnr2,
                            "Streckenschaden": streckenschaden,
                            "StreckenschadenLfdNr": streckenschadenlfdnr,
                            "PositionVon": posvon,
                            "PositionBis": posbis,
                            "Fotodatei": foto,
                        },
                    )
                    kl = SubElement(rzu, "Klassifizierung")

                    _create_children_text(
                        kl,
                        {
                            "Dichtheit": zd,
                            "Standsicherheit": zs,
                            "Betriebssicherheit": zb,
                        },
                    )

    def _export_zustandsdaten_schaechte(self):
        if self.vorlage == "":

            if (
                    not getattr(QKan.config.check_export, "export_zustandsdaten", True)
                    # or not self.hydraulik_objekte
                    or not self.zustand
            ):
                return

            # Haltungen

            last_pk = None

            if self.auswahl_zustand == "Stammdaten":

                sql = f"""
                    SELECT
                    schaechte_untersucht.pk,
                    schaechte_untersucht.schnam,
                    schaechte_untersucht.bezugspunkt,
                    schaechte_untersucht.baujahr,
                    schaechte_untersucht.untersuchtag,
                    schaechte_untersucht.untersucher,
                    schaechte_untersucht.wetter,
                    schaechte_untersucht.bewertungsart,
                    schaechte_untersucht.bewertungstag,
                    schaechte_untersucht.strasse,
                    schaechte_untersucht.datenart,
                    schaechte_untersucht.auftragsbezeichnung,
                    schaechte_untersucht.max_ZD,
                    schaechte_untersucht.max_ZB,
                    schaechte_untersucht.max_ZS,
                    x(PointN(schaechte_untersucht.geop, 1)) AS x,
                    y(PointN(schaechte_untersucht.geop, 1)) AS y,
                    schaechte_untersucht.kommentar,
                    untersuchdat_schacht.vertikale_lage,
                    untersuchdat_schacht.timecode,
                    untersuchdat_schacht.kuerzel,
                    untersuchdat_schacht.charakt1,
                    untersuchdat_schacht.charakt2,
                    untersuchdat_schacht.quantnr1,
                    untersuchdat_schacht.quantnr2,
                    untersuchdat_schacht.streckenschaden,
                    untersuchdat_schacht.streckenschaden_lfdnr,
                    untersuchdat_schacht.pos_von,
                    untersuchdat_schacht.pos_bis,
                    untersuchdat_schacht.foto_dateiname,
                    untersuchdat_schacht.ZD,
                    untersuchdat_schacht.ZB,
                    untersuchdat_schacht.ZS,
                    schaechte.material,
                    schaechte.entwart
                    FROM schaechte_untersucht
                    JOIN untersuchdat_schacht 
                    JOIN schaechte where schaechte_untersucht.schnam = untersuchdat_schacht.untersuchsch and schaechte_untersucht.schnam = schaechte.schnam
                 {self.abfrage_s_and}
                 """

                if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                    return

            elif self.auswahl_zustand == "Bewertet (Zustandsklassifizierung)":

                sql = f"""
                    SELECT
                    schaechte_untersucht_bewertet.pk,
                    schaechte_untersucht_bewertet.schnam,
                    schaechte_untersucht_bewertet.bezugspunkt,
                    schaechte_untersucht_bewertet.baujahr,
                    schaechte_untersucht_bewertet.untersuchtag,
                    schaechte_untersucht_bewertet.untersucher,
                    schaechte_untersucht_bewertet.wetter,
                    schaechte_untersucht_bewertet.bewertungsart,
                    schaechte_untersucht_bewertet.bewertungstag,
                    schaechte_untersucht_bewertet.strasse,
                    schaechte_untersucht_bewertet.datenart,
                    schaechte_untersucht_bewertet.auftragsbezeichnung,
                    schaechte_untersucht_bewertet.max_ZD,
                    schaechte_untersucht_bewertet.max_ZB,
                    schaechte_untersucht_bewertet.max_ZS,
                    x(PointN(schaechte_untersucht_bewertet.geop, 1)) AS x,
                    y(PointN(schaechte_untersucht_bewertet.geop, 1)) AS y,
                    schaechte_untersucht_bewertet.kommentar,
                    untersuchdat_schacht_bewertet.vertikale_lage,
                    untersuchdat_schacht_bewertet.timecode,
                    untersuchdat_schacht_bewertet.kuerzel,
                    untersuchdat_schacht_bewertet.charakt1,
                    untersuchdat_schacht_bewertet.charakt2,
                    untersuchdat_schacht_bewertet.quantnr1,
                    untersuchdat_schacht_bewertet.quantnr2,
                    untersuchdat_schacht_bewertet.streckenschaden,
                    untersuchdat_schacht_bewertet.streckenschaden_lfdnr,
                    untersuchdat_schacht_bewertet.pos_von,
                    untersuchdat_schacht_bewertet.pos_bis,
                    untersuchdat_schacht_bewertet.foto_dateiname,
                    untersuchdat_schacht_bewertet.ZD,
                    untersuchdat_schacht_bewertet.ZB,
                    untersuchdat_schacht_bewertet.ZS,
                    schaechte.material,
                    schaechte.entwart
                    FROM schaechte_untersucht_bewertet
                    JOIN untersuchdat_schacht_bewertet 
                    JOIN schaechte where schaechte_untersucht_bewertet.schnam = untersuchdat_schacht_bewertet.untersuchsch and schaechte_untersucht_bewertet.schnam = schaechte.schnam
                 {self.abfrage_s_and}
                 """

                if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                    return

            # fortschritt("Export Zustandsdaten...", 0.55)

            for attr in self.db_qkan.fetchall():

                (
                    pk,
                    schnam,
                    bezugspunkt,
                    baujahr,
                    untersuchtag,
                    untersucher,
                    wetter_nr,
                    bewertungsart,
                    bewertungstag,
                    strasse_nam,
                    datenart,
                    auftragsbezeichnung,
                    max_ZD,
                    max_ZB,
                    max_ZS,
                    xschob,
                    yschob,
                    xschun,
                    yschun,
                    kommentar,
                    vertikale_lage,
                    timekode,
                    kuerzel,
                    charakt1,
                    charakt2,
                    quantnr1,
                    quantnr2,
                    streckenschaden,
                    streckenschadenlfdnr,
                    posvon,
                    posbis,
                    foto,
                    zd,
                    zs,
                    zb,
                    material,
                    entwart_nr,
                ) = attr

                if pk != last_pk:
                    insp = SubElement(self.zustand, "InspizierteAbwassertechnischeAnlage")
                    _create_children_text(
                        insp,
                        {
                            "Objektbezeichnung": schnam,
                            "Anlagentyp": str(3),
                        },
                    )

                    strasse = SubElement(insp, "Lage")
                    _create_children_text(
                        strasse,
                        {
                            "Strassenname": strasse_nam,
                        },
                    )

                    for de in sorted(month_map, key=len, reverse=True):
                        untersuchtag = untersuchtag.replace(de, month_map[de])

                    tag, monat, jahr = untersuchtag.replace(".", "").split()

                    datum = f"{jahr}-{monat}-{int(tag):02d}"

                    opt = SubElement(insp, "OptischeInspektion")
                    if wetter_nr not in (0, '0', None, 'NULL'):
                        _create_children_text(
                            opt,
                            {
                                "Auftragskennung": 1,
                                "Inspektionsdatum": datum,
                                "NameUntersucher": untersucher,
                                "Wetter": wetter_nr,
                            },
                        )
                    else:
                        _create_children_text(
                            opt,
                            {
                                "Auftragskennung": 1,
                                "Inspektionsdatum": datum,
                                "NameUntersucher": untersucher,
                            },
                        )


                    knoten = SubElement(opt, "Knoten")
                    _create_children_text(
                        knoten,
                        {
                            "BezugspunktVertikal": bezugspunkt,
                        },
                    )

                    rgrund = SubElement(knoten, "KGrunddaten")
                    # _create_children_text(
                    #     rgrund,
                    #     {
                    #         "Material": material,
                    #         "Kanalart": entwart_nr,
                    #     },
                    # )
                    inspdat = SubElement(opt, "Inspektionsdaten")

                    last_pk = pk

                rzu = SubElement(inspdat, "RZustand")
                _create_children_text(
                    rzu,
                    {
                        "VertikaleLage": vertikale_lage,
                        "Timecode": timekode,
                        "InspektionsKode": kuerzel,
                        "Charakterisierung1": charakt1,
                        "Charakterisierung2": charakt2,
                        "Quantifizierung1Numerisch": quantnr1,
                        "Quantifizierung2Numerisch": quantnr2,
                        "Streckenschaden": streckenschaden,
                        "StreckenschadenLfdNr": streckenschadenlfdnr,
                        "PositionVon": posvon,
                        "PositionBis": posbis,
                        "Fotodatei": foto,
                    },
                )
                kl = SubElement(rzu, "Klassifizierung")

                _create_children_text(
                    kl,
                    {
                        "Dichtheit": zd,
                        "Standsicherheit": zs,
                        "Betriebssicherheit": zb,
                    },
                )

    def _export_zustandsdaten_filme(self):
        if self.vorlage == "":

            if (
                    not getattr(QKan.config.check_export, "export_zustandsdaten", True)
                    # or not self.hydraulik_objekte
                    or not self.zustand
            ):
                return

            last_pk = None

            #TODO: jenachdem um was für ein objekt es sich handelt müssen unterschiedliche joins durchgeführt werden für inspektionsrichtung usw.

            sql = """
                    select name,
                    untersuchtag,
                    objekt,
                    datei
                    from videos
             """

            if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                return

            # fortschritt("Export Zustandsdaten...", 0.55)
            filme = SubElement(self.zustand, "Filme")

            for attr in self.db_qkan.fetchall():

                (
                    name,
                    untersuchtag,
                    objekt,
                    datei,
                ) = attr

                film = SubElement(self.zustand, "Film")


                _create_children_text(
                    film,
                    {
                        "Filmname": datei,
                        "Auftragskennung": "",
                    },
                )

                objekte = SubElement(film, "FilmObjekte")
                objekt = SubElement(objekte, "FilmObjekt")
                _create_children_text(
                    objekt,
                    {
                        "Objektbezeichnung": name,
                        "Typ": "",
                        "Inspektionsrichtung":"",
                    },
                )


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
        iface.messageBar().pushWidget(status_message, Qgis.MessageLevel.Info, 10)


        # region Create XML structure

        NS = "http://www.ofd-hannover.la/Identifikation"
        XSI = "http://www.w3.org/2001/XMLSchema-instance"

        root = etree.Element(
            f"{{{NS}}}Identifikation",
            nsmap={
                None: NS,
                "xsi": XSI
            }
        )

        root.attrib[f"{{{XSI}}}schemaLocation"] = (
            f"{NS} schema/1302-metadaten.xsd"
        )

        etree.SubElement(root, f"{{{NS}}}Version").text = "2013-02"
        #root = Element("Identifikation", nsmap={"xmlns":"http://www.ofd-hannover.la/Identifikation","xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance","xsi:schemaLocation":"http://www.ofd-hannover.la/Identifikation schema/1302-metadaten.xsd",})
        #SubElementText(root, "Version", "2013-02")

        admin_daten = SubElement(root, "Admindaten")
        _create_children(
            SubElement(admin_daten, "Liegenschaft"),
            ["Liegenschaftsnummer", "Liegenschaftsbezeichnung"],
        )

        daten_kollektive = SubElement(root, "Datenkollektive")
        _create_children_text(
            daten_kollektive,
            {
                "Datenstatus": '1',
                "Erstellungsdatum": str(date.today()),
                "Kommentar": "Created with QKan's XML export module",
            },
        )
        kennungen = SubElement(SubElement(daten_kollektive, "Kennungen"), "Kollektiv")

        _create_children_text(
            kennungen,
            {
                "Kennung": "STA01",
                "Kollektivart": "1",
            },
        )

        #TODO: aufträge ergänzen zur Vollständigkeit bei stammdaten und zustandsdaten
        #wenn nur zahl in auftragsbezeichnung, dann auftragskennung sonst als auftragsbezeichnung

        self.stamm = SubElement(daten_kollektive, "Stammdatenkollektiv")
        _create_children_text(self.stamm, {"Kennung": "STA01", "Beschreibung": "Stammdaten",},)

        if QKan.config.check_export.zustandsdaten:
            _create_children_text(
                kennungen,
                {
                    "Kennung": "ZUS01",
                    "Kollektivart": "2",
                },
            )
            self.zustand = SubElement(daten_kollektive, "Zustandsdatenkollektiv")
            _create_children_text(self.zustand, {"Kennung": "ZUS01", "Beschreibung": "Zustandsdaten", }, )
            self.auftraege = SubElement(self.zustand, "Auftraege")
            self.auftrag = SubElement(self.auftraege, "Auftrag")
            _create_children_text( self.auftrag, {"Auftragsbezeichnung": '1', "Auftragsnummer": 1, "Auftragskennung": '1', }, )

        hydro_kollektiv = SubElement(daten_kollektive, "Hydraulikdatenkollektiv")
        _create_children_text(
            hydro_kollektiv,
            {"Kennung": "STA01", "Beschreibung": "Hydraulikdaten",},
        )
        rechen = SubElement(hydro_kollektiv, "Rechennetz")
        SubElement(rechen, "Stammdatenkennung")
        self.hydraulik_objekte = SubElement(rechen, "HydraulikObjekte")
        # endregion

        # Path(self.export_file).write_text(
        #     minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        # )


        if QKan.config.selections.selectedObjects:
            select_s = []
            select_h = []

            sql = f"""
                                SELECT
                                pk
                                from sel_schaechte
                             """

            if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                return


            for attr in self.db_qkan.fetchall():
                select_s.append(attr[0])

            sql = f"""
                                            SELECT
                                            pk
                                            from sel_haltungen
                                         """

            if not self.db_qkan.sql(sql, "db_qkan: export_zustandsdaten"):
                return

            for attr in self.db_qkan.fetchall():
                select_h.append(attr[0])

            select_s_t = tuple(select_s)

            select_h_t = tuple(select_h)


            self.abfrage_s_and = f"AND schaechte.pk in {select_s_t}"

            self.abfrage_s_where = f"WHERE schaechte.pk in {select_s_t}"

            self.abfrage_h_and = f"AND haltungen.pk in {select_h_t}"

            self.abfrage_h_where = f"WHERE haltungen.pk in {select_h_t}"

        else:
            self.abfrage_s_and = ""
            self.abfrage_s_where = ""
            self.abfrage_h_and = ""
            self.abfrage_h_where = ""


        # Export
        if QKan.config.check_export.wehre:
            self._export_wehre()
        if QKan.config.check_export.pumpen:
            self._export_pumpen()
        if QKan.config.check_export.auslaesse:
            self._export_auslaesse()
        if QKan.config.check_export.schaechte:
            self._export_schaechte()
        if QKan.config.check_export.speicher:
            self._export_speicher()
        if QKan.config.check_export.haltungen:
            self._export_haltungen()
        if QKan.config.check_export.anschlussleitungen:
            self._export_anschlussleitungen()

        if QKan.config.check_export.zustandsdaten:
            self._export_zustandsdaten_haltungen()
            self._export_zustandsdaten_schaechte()
            self._export_zustandsdaten_anschlussleitungen()

        # Path(self.export_file).write_text(
        #     etree.tostring(root, pretty_print=True, encoding="unicode")
        # )

        Path(self.export_file).write_bytes(
            etree.tostring(
                root,
                pretty_print=True,
                encoding="ISO-8859-1",
                xml_declaration=True,
                standalone=True,
            )
        )


        # Close connection
        del self.db_qkan

        fortschritt("Ende...", 1)
        progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")
        status_message.setLevel(Qgis.MessageLevel.Success)
