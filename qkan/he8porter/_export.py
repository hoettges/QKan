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

logger = logging.getLogger("QKan.he8.export")

# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self,
        database_he: str,
        dbtemplate_he: str,
        db_qkan: DBConnection,
        liste_teilgebiete: typing.List[str],
        autokorrektur: bool,
        fangradius: float = 0.1,
        mindestflaeche: float = 0.5,
        mit_verschneidung: bool = True,
        export_flaechen_he8: bool = True,
        check_export: dict = {},
    ):
        """
        Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine HE8-SQLite-Datenbank.

        :param database_he:         Pfad zur HE8-SQLite-Datenbank
        :param dbtemplate_he:       Vorlage für die zu erstellende HE8-SQLite-Datenbank
        :param db_qkan:                Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
        :param liste_teilgebiete:   Liste der ausgewählten Teilgebiete
        :param autokorrektur:       Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                                    werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                                    abgebrochen.
        :param fangradius:          Suchradius, mit dem an den Enden der Verknüpfungen (linkfl, linksw) eine
                                    Haltung bzw. ein Einleitpunkt zugeordnet wird.
        :param mindestflaeche:      Mindestflächengröße bei Einzelflächen und Teilflächenstücken
        :param mit_verschneidung:   Flächen werden mit Haltungsflächen verschnitten (abhängig von Attribut "aufteilen")
        :param export_flaechen_he8:
        :param check_export:        Liste von Export-Optionen
        """

        self.database_he = database_he
        self.dbtemplate_he = dbtemplate_he
        self.db_qkan = db_qkan
        self.liste_teilgebiete = liste_teilgebiete
        self.autokorrektur = autokorrektur
        self.fangradius = fangradius
        self.mindestflaeche = mindestflaeche
        self.mit_verschneidung = mit_verschneidung
        self.export_flaechen_he8 = export_flaechen_he8
        self.check_export = check_export

        if os.path.exists(database_he):
            try:
                shutil.copyfile(dbtemplate_he, database_he)
            except BaseException as err:
                fehlermeldung("Fehler in Export nach HE8",
                              "Fehler beim Kopieren der Vorlage: \n   {self.dbtemplate_he}\n" + \
                              "nach Ziel: {self.database_he}\n"

    def _export_wehre(self):
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

        if not self.db_qkan.sql(sql, "db_qkan: export_wehre"):
            return

        fortschritt("Export Wehre...", 0.35)

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
                    "Wehrtyp": attr[3],
                    "Schwellenhoehe": attr[4],
                    "Kammerhoehe": attr[5],
                    "LaengeWehrschwelle": attr[6],
                    "Ueberfallbeiwert": attr[7],
                },
            )

            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            SubElementText(abw, "Objektbezeichnung", attr[0])
            SubElement(abw, "Objektart")
            SubElementText(abw, "Status", self.mapper_simstatus.get(attr[10], -1))
            _create_children_text(
                SubElement(
                    SubElement(SubElement(abw, "Knoten"), "Bauwerk"), "Wehr_Ueberlauf"
                ),
                {"Wehrtyp": attr[3], "LaengeWehrschwelle": attr[6]},
            )

        fortschritt("Wehre eingefügt")

    def _export_pumpen(self):
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

        if not self.db_qkan.sql(sql, "db_qkan: export_pumpen"):
            return

        fortschritt("Export Pumpen...", 0.35)

        for attr in self.db_qkan.fetchall():
            obj = SubElement(self.hydraulik_objekte, "Hydraulikobjekt")
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

            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektbezeichnung": attr[0],
                    "Status": self.mapper_simstatus.get(attr[9], -1),
                    "Objektart": None,
                },
            )
            SubElement(SubElement(abw, "Knoten"), "Bauwerk")

        fortschritt("Pumpen eingefügt")

    def _export_auslaesse(self):
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

        if not self.db_qkan.sql(sql, u"dbQK: export_auslaesse"):
            return False

        fortschritt("Export Auslässe...", 0.20)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektart": None,
                    "Objektbezeichnung": attr[0],
                    "Kommentar": attr[6],
                    "Status": self.mapper_simstatus.get(attr[7], -1),
                    "Entwaesserungsart": attr[8],
                },
            )

            knoten = SubElement(abw, "Knoten")
            SubElementText(knoten, "KnotenTyp", attr[9])  # TODO: Is None sometimes
            _create_children(
                SubElement(knoten, "Bauwerk"), ["Bauwerktyp", "Auslaufbauwerk"]
            )

            geom_knoten = SubElement(
                SubElement(SubElement(abw, "Geometrie"), "Geometriedaten"), "Knoten"
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "GOK",
                    "Punkthoehe": attr[1],
                    "Rechtswert": attr[4],
                    "Hochwert": attr[5],
                },
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {"PunktattributAbwasser": "HP", "Punkthoehe": attr[2]},
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "SMP",
                    "Punkthoehe": attr[2],
                    "Rechtswert": attr[4],
                    "Hochwert": attr[5],
                },
            )
        fortschritt("Auslässe eingefügt")

    def _export_schaechte(self):
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
            schaechte.kommentar,
            schaechte.simstatus,
            schaechte.xsch,
            schaechte.ysch
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
                    "Objektart": None,
                    "Objektbezeichnung": attr[0],
                    "Entwaesserungsart": attr[4],
                    "Kommentar": attr[6],
                    "Status": self.mapper_simstatus.get(attr[7], -1),
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
                    "PunktattributAbwasser": "GOK",
                    "Punkthoehe": attr[1],
                    "Rechtswert": attr[8],
                    "Hochwert": attr[9],
                },
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {"PunktattributAbwasser": "HP", "Punkthoehe": attr[2]},
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "SMP",
                    "Punkthoehe": attr[2],
                    "Rechtswert": attr[8],
                    "Hochwert": attr[9],
                },
            )

        fortschritt("Schächte eingefügt")

    def _export_speicher(self):
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

        if not self.db_qkan.sql(sql, "db_qkan: export_speicher"):
            return

        fortschritt("Export Speicherschächte...", 0.35)
        for attr in self.db_qkan.fetchall():
            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektart": None,
                    "Objektbezeichnung": attr[0],
                    "Entwaesserungsart": attr[4],
                    "Kommentar": attr[7],
                    "Status": self.mapper_simstatus.get(attr[8], -1),
                },
            )

            knoten = SubElement(abw, "Knoten")
            SubElementText(knoten, "KnotenTyp", attr[9])  # TODO: Is None sometimes
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
                    "PunktattributAbwasser": "DMP",
                    "Punkthoehe": attr[1],
                    "Rechtswert": attr[5],
                    "Hochwert": attr[6],
                },
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {"PunktattributAbwasser": "HP", "Punkthoehe": attr[2]},
            )
            _create_children_text(
                SubElement(geom_knoten, "Punkt"),
                {
                    "PunktattributAbwasser": "SMP",
                    "Punkthoehe": attr[2],
                    "Rechtswert": attr[5],
                    "Hochwert": attr[6],
                },
            )
        fortschritt("Speicher eingefügt")

    def _export_haltungen(self):
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

        if not self.db_qkan.sql(sql, "db_qkan: export_haltungen"):
            return

        fortschritt("Export Haltungen...", 0.35)

        for attr in self.db_qkan.fetchall():
            obj = SubElement(self.hydraulik_objekte, "HydraulikObjekt")
            _create_children(obj, ["HydObjektTyp", "Objektbezeichnung"])
            _create_children_text(
                SubElement(obj, "Haltung"),
                {"Berechnungslaenge": attr[5], "RauigkeitsbeiwertKb": attr[12]},
            )

            abw = SubElement(self.stamm, "AbwassertechnischeAnlage")
            _create_children_text(
                abw,
                {
                    "Objektart": None,
                    "Objektbezeichnung": attr[0],
                    "Entwaesserungsart": attr[11],
                    "Status": self.mapper_simstatus.get(attr[13], -1),
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
                    "PunktattributAbwasser": "DMP",
                    "Rechtswert": attr[15],
                    "Hochwert": attr[16],
                    "Punkthoehe": attr[8],
                },
            )
            _create_children_text(
                SubElement(kante, "Ende"),
                {
                    "PunktattributAbwasser": "DMP",
                    "Rechtswert": attr[17],
                    "Hochwert": attr[18],
                    "Punkthoehe": attr[9],
                },
            )

        fortschritt("Haltungen eingefügt")

    def run(self):
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


        # Export
        self._export_wehre()
        self._export_pumpen()
        self._export_auslaesse()
        self._export_schaechte()
        self._export_speicher()
        self._export_haltungen()

        Path(self.export_file).write_text(
            minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        )

        # Close connection
        del self.db_qkan

        fortschritt("Ende...", 1)
        progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")
        status_message.setLevel(Qgis.Success)
