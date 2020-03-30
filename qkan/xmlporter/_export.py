import logging
import typing
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fortschritt

logger = logging.getLogger("QKan.xml.export")


def _create_children(parent: Element, names: typing.List[str]):
    for child in names:
        SubElement(parent, child)


def _create_children_text(
    parent: Element, children: typing.Dict[str, typing.Union[str, int]]
):
    for name, text in children.items():
        if text is None:
            SubElement(parent, name)
        else:
            SubElementText(parent, name, str(text))


# noinspection PyPep8Naming
def SubElementText(parent: Element, name: str, text: typing.Union[str, int]):
    s = SubElement(parent, name)
    s.text = str(text)
    return s


def _export_wehre(db_qkan: DBConnection, parent: Element, stamm: Element):
    if not getattr(QKan.config.check_export, "export_wehre", True):
        return

    sql = """
    SELECT
        wnam,
        schoben,
        schunten,
        wehrtyp,
        schwellenhoehe,
        kammerhoehe,
        laenge,
        uebeiwert,
        aussentyp,
        aussenwsp,
        simstatus,
        kommentar
    FROM wehre
    """

    if not db_qkan.sql(sql, "db_qkan: export_wehre"):
        return

    fortschritt("Export Wehre...", 0.35)

    for attr in db_qkan.fetchall():
        obj = SubElement(parent, "Hydraulikobjekt")
        SubElementText(obj, "Objektbezeichnung", attr[0])
        _create_children_text(
            SubElement(obj, "Wehr"),
            {
                "HydObjektTyp": None,
                "SchachtZulauf": attr[1],
                "SchachtAblauf": attr[2],
                "Wehrtyp": attr[3],
                "Schwellenhoehe": attr[4],
                "Kammerhoehe": attr[5],
                "LaengeWehrschwelle": attr[6],
                "Ueberfallbeiwert": attr[7],
            },
        )

        abw = SubElement(stamm, "AbwassertechnischeAnlage")
        SubElementText(abw, "Objektbezeichnung", attr[0])
        SubElement(abw, "Objektart")
        SubElementText(abw, "Status", attr[10])
        _create_children_text(
            SubElement(
                SubElement(SubElement(abw, "Knoten"), "Bauwerk"), "Wehr_Ueberlauf"
            ),
            {"Wehrtyp": attr[3], "LaengeWehrschwelle": attr[6]},
        )

    fortschritt("Wehre eingefügt")


def _export_pumpen(db_qkan: DBConnection, parent: Element, stamm: Element):
    if not getattr(QKan.config.check_export, "export_pumpen", True):
        return

    sql = """
    SELECT
        pnam,
        volanf,
        volges,
        sohle,
        schunten,
        schoben,
        steuersch,
        einschalthoehe,
        ausschalthoehe,
        simstatus,
        kommentar,
        pumpentyp
    FROM pumpen
    """

    if not db_qkan.sql(sql, "db_qkan: export_pumpen"):
        return

    fortschritt("Export Pumpen...", 0.35)

    for attr in db_qkan.fetchall():
        obj = SubElement(parent, "Hydraulikobjekt")
        SubElementText(obj, "Objektbezeichnung", attr[0])
        _create_children_text(
            SubElement(obj, "Pumpe"),
            {
                "HydObjektTyp": None,
                "Anfangsvolumen": attr[1],
                "Gesamtvolumen": attr[2],
                "Sohlhoehe": attr[3],
                "SchachtAblauf": attr[4],
                "SchachtZulauf": attr[5],
                "Steuerschacht": attr[6],
                "Schaltpunkt1-2": attr[7],
                "Schaltpunkt2-1": attr[8],
                "PumpenTyp": attr[11],
            },
        )

        abw = SubElement(stamm, "AbwassertechnischeAnlage")
        _create_children_text(
            abw, {"Objektbezeichnung": attr[0], "Status": attr[9], "Objektart": None}
        )
        SubElement(SubElement(abw, "Knoten"), "Bauwerk")

    fortschritt("Pumpen eingefügt")


def _export_auslaesse(db_qkan: DBConnection, stamm: Element):
    if not getattr(QKan.config.check_export, "export_auslaesse", True):
        return

    sql = """
    SELECT
        schaechte.schnam,
        schaechte.deckelhoehe,
        schaechte.sohlhoehe,
        schaechte.durchm,
        schaechte.xsch,
        schaechte.ysch,
        schaechte.kommentar,
        schaechte.simstatus,
        ea.he_nr,
        schaechte.knotentyp
    FROM schaechte
    LEFT JOIN Entwaesserungsarten AS ea
    ON schaechte.entwart = ea.bezeichnung
    WHERE schaechte.schachttyp = 'Auslass'
    """

    if not db_qkan.sql(sql, u"dbQK: export_auslaesse"):
        return False

    fortschritt("Export Auslässe...", 0.20)
    for attr in db_qkan.fetchall():
        abw = SubElement(stamm, "AbwassertechnischeAnlage")
        _create_children_text(
            abw,
            {
                "Objektart": None,
                "Objektbezeichnung": attr[0],
                "Kommentar": attr[6],
                "Status": attr[7],
                "Entwaesserungsart": attr[8],
            },
        )

        knoten = SubElement(abw, "Knoten")
        SubElementText(knoten, "Knotentyp", attr[9])
        _create_children(
            SubElement(knoten, "Bauwerk"), ["Bauwerktyp", "Auslaufbauwerk"]
        )

        geom_knoten = SubElement(
            SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {
                "PunktattributAbwasser": None,
                "Punkthoehe": None,
                "Rechtswert": attr[4],
                "Hochwert": attr[5],
            },
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {"PunktattributAbwasser": None, "Punkthoehe": attr[2]},
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {
                "PunktattributAbwasser": None,
                "Punkthoehe": attr[2],
                "Rechtswert": attr[4],
                "Hochwert": attr[5],
            },
        )
    fortschritt("Auslässe eingefügt")


def _export_schaechte(db_qkan: DBConnection, stamm: Element):
    if not getattr(QKan.config.check_export, "export_schaechte", True):
        return

    sql = """
    SELECT
        schaechte.schnam,
        schaechte.deckelhoehe,
        schaechte.sohlhoehe,
        schaechte.durchm,
        ea.he_nr,
        schaechte.knotentyp,
        schaechte.simstatus,
        schaechte.kommentar,
        schaechte.xsch,
        schaechte.ysch
    FROM schaechte
    LEFT JOIN Entwaesserungsarten AS ea
    ON schaechte.entwart = ea.bezeichnung
    WHERE schaechte.schachttyp = 'Schacht'
"""
    if not db_qkan.sql(sql, "db_qkan: export_schaechte"):
        return

    fortschritt("Export Schächte...", 0.35)
    for attr in db_qkan.fetchall():
        abw = SubElement(stamm, "AbwassertechnischeAnlage")
        _create_children_text(
            abw,
            {
                "Objektart": None,
                "Objektbezeichnung": attr[0],
                "Entwaesserungsart": attr[4],
                "Kommentar": attr[6],
                "Status": attr[7],
            },
        )

        knoten = SubElement(abw, "Knoten")
        SubElementText(knoten, "KnotenTyp", attr[5])
        _create_children(
            SubElement(knoten, "Schacht"), ["Schachttiefe", "AnzahlAnschluesse"]
        )

        geom_knoten = SubElement(
            SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {
                "PunktattributAbwasser": None,
                "Punkthoehe": attr[1],
                "Rechtswert": attr[8],
                "Hochwert": attr[9],
            },
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {"PunktattributAbwasser": None, "Punkthoehe": attr[2]},
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {
                "PunktattributAbwasser": None,
                "Punkthoehe": attr[2],
                "Rechtswert": attr[8],
                "Hochwert": attr[9],
            },
        )

    fortschritt("Schächte eingefügt")


def _export_speicher(db_qkan: DBConnection, parent: Element, stamm: Element):
    if not getattr(QKan.config.check_export, "export_pumpen", True):
        return

    sql = """
    SELECT
        schaechte.schnam,
        schaechte.deckelhoehe,
        schaechte.sohlhoehe,
        schaechte.durchm,
        ea.he_nr,
        schaechte.xsch,
        schaechte.ysch,
        schaechte.kommentar,
        schaechte.simstatus,
        schaechte.knotentyp
    FROM schaechte
    left join Entwaesserungsarten AS ea
    ON schaechte.entwart = ea.bezeichnung
    WHERE schaechte.schachttyp = 'Speicher'
    """

    if not db_qkan.sql(sql, "db_qkan: export_speicher"):
        return

    fortschritt("Export Speicherschächte...", 0.35)
    for attr in db_qkan.fetchall():
        abw = SubElement(stamm, "AbwassertechnischeAnlage")
        _create_children_text(
            abw,
            {
                "Objektart": None,
                "Objektbezeichnung": attr[0],
                "Entwaesserungsart": attr[4],
                "Kommentar": attr[7],
                "Status": attr[8],
            },
        )

        knoten = SubElement(abw, "Knoten")
        SubElementText(knoten, "Knotentyp", attr[9])
        bauwerk = SubElement(knoten, "Bauwerk")
        SubElement(bauwerk, "Bauwerkstyp")
        _create_children(
            SubElement(bauwerk, "Becken"), ["AnzahlZulaeufe", "AnzahlAblaeufe"]
        )

        geom_knoten = SubElement(
            SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {
                "PunktattributAbwasser": None,
                "Punkthoehe": attr[1],
                "Rechtswert": attr[5],
                "Hochwert": attr[6],
            },
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {"PunktattributAbwasser": None, "Punkthoehe": attr[2]},
        )
        _create_children_text(
            SubElement(geom_knoten, "Punkt"),
            {
                "PunktattributAbwasser": None,
                "Punkthoehe": attr[2],
                "Rechtswert": attr[5],
                "Hochwert": attr[6],
            },
        )
    fortschritt("Speicher eingefügt")


def _export_haltungen(db_qkan: DBConnection, parent: Element, stamm: Element):
    if not getattr(QKan.config.check_export, "export_haltungen", True):
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
        haltungen.deckeloben,
        haltungen.deckelunten,
        haltungen.profilnam,
        ea.he_nr,
        haltungen.ks,
        haltungen.simstatus,
        haltungen.kommentar,
        haltungen.xschob,
        haltungen.yschob,
        haltungen.xschun,
        haltungen.yschun
    FROM haltungen
    LEFT JOIN Entwaesserungsarten AS ea 
    ON haltungen.entwart = ea.bezeichnung
    """

    if not db_qkan.sql(sql, "db_qkan: export_haltungen"):
        return

    fortschritt("Export Haltungen...", 0.35)

    for attr in db_qkan.fetchall():
        obj = SubElement(parent, "HydraulikObjekt")
        _create_children(obj, ["HydObjektTyp", "Objektbezeichnung"])
        _create_children_text(
            SubElement(obj, "Haltung"),
            {"Berechnungslaenge": attr[5], "RauigkeitsbeiwertKb": attr[12]},
        )

        abw = SubElement(stamm, "AbwassertechnischeAnlage")
        _create_children_text(
            abw,
            {
                "Objektart": None,
                "Objektbezeichnung": attr[0],
                "Entwaesserungsart": attr[11],
                "Status": attr[13],
            },
        )

        kante = SubElement(abw, "Kante")
        _create_children_text(
            kante,
            {
                "KantenTyp": None,
                "KnotenAblaufTyp": None,
                "KnotenZulaufTyp": None,
                "Material": None,
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
                "Profilbreite": attr[4],
                "Profilhoehe": attr[3],
            },
        )

        SubElementText(SubElement(kante, "Haltung"), "DMPLaenge", attr[5])

        geom = SubElement(abw, "Geometrie")
        _create_children(geom, ["GeoObjektart", "GeoObjekttyp"])

        kante = SubElement(
            SubElement(SubElement(geom, "Geometriedaten"), "Kanten"), "Kante"
        )
        _create_children_text(
            SubElement(kante, "Start"),
            {
                "PunktattributAbwasser": None,
                "Rechtswert": attr[15],
                "Hochwert": attr[16],
                "Punkthoehe": attr[8],
            },
        )
        _create_children_text(
            SubElement(kante, "Ende"),
            {
                "PunktattributAbwasser": None,
                "Rechtswert": attr[17],
                "Hochwert": attr[18],
                "Punkthoehe": attr[9],
            },
        )

    fortschritt("Haltungen eingefügt")


def export_kanaldaten(db_qkan: DBConnection, export_file: str):
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
        "Identifikation", {"xmlns": "http://www.ofd-hannover.la/Identifikation"}
    )
    SubElement(root, "Version")

    admin_daten = SubElement(root, "Admindaten")
    _create_children(
        SubElement(admin_daten, "Liegenschaft"),
        ["Liegenschaftsnummer", "Liegenschaftsbezeichnung"],
    )

    daten_kollektive = SubElement(root, "Datenkollektive")
    _create_children(daten_kollektive, ["Datenstatus", "Erstellungsdatum", "Kommentar"])
    SubElement(SubElement(daten_kollektive, "Kennungen"), "Kollektiv")

    stamm = SubElement(daten_kollektive, "Stammdatenkollektiv")
    _create_children(stamm, ["Kennung", "Beschreibung"])

    hydro_kollektiv = SubElement(daten_kollektive, "Hydraulikdatenkollektiv")
    _create_children(
        hydro_kollektiv, ["Kennung", "Beschreibung", "Flaechen", "Systembelastungen"]
    )
    rechen = SubElement(hydro_kollektiv, "Rechennetz")
    SubElement(rechen, "Stammdatenkennung")
    hydraulik_objekte = SubElement(rechen, "HydraulikObjekte")
    # endregion

    # Export
    _export_wehre(db_qkan, hydraulik_objekte, stamm)
    _export_pumpen(db_qkan, hydraulik_objekte, stamm)
    _export_auslaesse(db_qkan, stamm)
    _export_schaechte(db_qkan, stamm)
    _export_haltungen(db_qkan, hydraulik_objekte, stamm)

    Path(export_file).write_text(
        minidom.parseString(tostring(root)).toprettyxml(indent="  ")
    )

    del db_qkan

    fortschritt("Ende...", 1)
    progress_bar.setValue(100)
    status_message.setText("Datenexport abgeschlossen.")
    status_message.setLevel(Qgis.Success)
