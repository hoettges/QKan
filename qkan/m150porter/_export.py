from pathlib import Path

# noinspection PyUnresolvedReferences
from typing import Dict, List, Optional, Union
from xml.dom import minidom
from lxml.etree import Element, SubElement, tostring
from lxml import etree

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis, QgsGeometry

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import fortschritt
from qkan.utils import get_logger, QkanDbError, QkanAbortError

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

def formatm150(zahl: Union[float, None]):
    """Formatiert auf 3 Nachkommastellen. None wird weitergegeben"""
    if isinstance(zahl, float):
        return f'{zahl:.3f}'
    elif isinstance(zahl, int):
        return f'{zahl:d}'
    else:
        return zahl

def cutm150(text: Union[str, None], limit: int = 16):
    """Begrenzt einen Text auf die vorgegebene Länge, wenn die Option cutNames aktiv ist"""
    if QKan.config.check_export.cutNames and text is not None:
            return text.lstrip()[:limit]
    else:
        return text


# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self, db_qkan: DBConnection, export_file: str):
        self.db_qkan = db_qkan
        self.export_file = export_file
        self.liste_teilgebiete = QKan.config.selections.teilgebiete

        # XML base

        self.hydraulik_objekte: Optional[Element] = None

        self.root: Element = None

        if round(QKan.config.epsg - 5, -1) in (25830, 3040):
            self.ksys = 'UTM'
            self.gp_x = 'GP005'
            self.gp_y = 'GP006'
        elif round(QKan.config.epsg - 5, -1) in (31460, 4640):
            self.ksys = 'GK'
            self.gp_x = 'GP003'
            self.gp_y = 'GP004'
        else:
            logger.error_data(f"Fehler beim Koordinatensystem: {QKan.config.epsg}")
            raise QkanAbortError

    def _export_refdata(self) -> None:
        """Exportiert die Referenztabellen"""
        if not self.db_qkan.sqlyml(
            sqlnam='m150_ex_refdata'
        ):
            raise QkanDbError
        for (
            bezext,
            kuerzel,
            m150tabelle,
        ) in self.db_qkan.fetchall():
            x_elem = SubElement(self.root, "RT")
            _create_children_text(
                x_elem,
                {
                    "RT001": m150tabelle,
                    "RT002": kuerzel,
                    "RT004": bezext,
                },
            )

    def _export_wehre(self) -> None:
        if not QKan.config.check_export.wehre:
            return

        sqlnam = 'm150_ex_halwp' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters={'bauwerkstyp': 'Wehr'}
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Wehre'")
            raise QkanDbError

        for (
            schoben,
            deckelhoehe,
            sohlhoehe,
            tiefe,
            knotenart,
            durchm,
            entwart,
            strasse,
            strassenname,
            baujahr,
            bauwerksart,
            simstatus,
            material,
            kommentar,
            geobline,
            geobpoint,
        ) in self.db_qkan.fetchall():
            geop = QgsGeometry()
            geop.fromWkb(geobpoint)
            ptsch = geop.asPoint()
            xsch = ptsch.x()
            ysch = ptsch.y()

            if geobline is None:
                ptlis = []
            else:
                geom = QgsGeometry()
                geom.fromWkb(geobline)
                ptlis = geom.asMultiPolyline()              # Achtung: 2-dimensional

            x_elem = SubElement(self.root, "KG")
            _create_children_text(
                x_elem,
                {
                    "KG001": cutm150(schoben, 16),
                    "KG101": strasse,
                    "KG102": strassenname,
                    "KG211": formatm150(tiefe),
                    "KG301": 'K',
                    "KG302": entwart,
                    "KG303": None if baujahr is None else f'{baujahr:d}',
                    "KG304": material,
                    "KG305": knotenart,
                    "KG306": bauwerksart,
                    "KG309": None if durchm is None else f'{durchm:d}',
                    "KG401": simstatus,
                    "KG407": 'B',
                    "KG999": kommentar,
                },
            )

            #Schachtsohle
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schoben, 30),
                    "GO002": 'G',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schoben, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(sohlhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            #Deckel
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schoben, 30),
                    "GO002": 'D',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schoben, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(deckelhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            # Geometrieobjekt. Wenn ptlis = [] wird diese Schleife übersprungen
            for i, part in enumerate(ptlis):
                x_obj = SubElement(x_elem, "GO")
                suffix = f' - {i}'
                _create_children_text(
                    x_obj,
                    {
                        "GO001": cutm150(schoben, 30 - len(suffix)) + suffix,
                        "GO002": 'B',
                        "GO003": 'Poly',
                    },
                )
                for j, point in enumerate(part):
                    xpt = point.x()
                    ypt = point.y()
                    suffix = f'-{j}'
                    _create_children_text(
                        SubElement(x_obj, "GP"),
                        {
                            "GP001": cutm150(schoben, 30 - len(suffix)) + suffix,
                            "GP002": self.ksys,
                            self.gp_x: formatm150(xpt),
                            self.gp_y: formatm150(ypt),
                        },
                    )

    def _export_pumpen(self) -> None:
        if not QKan.config.check_export.pumpen:
            return

        sqlnam = 'm150_ex_halwp' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters={'bauwerkstyp': 'Pumpe'}
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Pumpen'")
            raise QkanDbError

        for (
            schoben,
            deckelhoehe,
            sohlhoehe,
            tiefe,
            knotenart,
            durchm,
            entwart,
            strasse,
            strassenname,
            baujahr,
            bauwerksart,
            simstatus,
            material,
            kommentar,
            geobline,
            geobpoint,
        ) in self.db_qkan.fetchall():
            geop = QgsGeometry()
            geop.fromWkb(geobpoint)
            ptsch = geop.asPoint()
            xsch = ptsch.x()
            ysch = ptsch.y()

            if geobline is None:
                ptlis = []
            else:
                geom = QgsGeometry()
                geom.fromWkb(geobline)
                ptlis = geom.asMultiPolyline()              # Achtung: 2-dimensional

            x_elem = SubElement(self.root, "KG")
            _create_children_text(
                x_elem,
                {
                    "KG001": cutm150(schoben, 16),
                    "KG101": strasse,
                    "KG102": strassenname,
                    "KG211": formatm150(tiefe),
                    "KG301": 'K',
                    "KG302": entwart,
                    "KG303": None if baujahr is None else f'{baujahr:d}',
                    "KG304": material,
                    "KG305": knotenart,
                    "KG306": bauwerksart,
                    "KG309": None if durchm is None else f'{durchm:d}',
                    "KG401": simstatus,
                    "KG407": 'B',
                    "KG999": kommentar,
                },
            )

            #Schachtsohle
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schoben, 30),
                    "GO002": 'G',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schoben, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(sohlhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            #Deckel
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schoben, 30),
                    "GO002": 'D',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schoben, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(deckelhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            # Geometrieobjekt. Wenn ptlis = [] wird diese Schleife übersprungen
            for i, part in enumerate(ptlis):
                x_obj = SubElement(x_elem, "GO")
                suffix = f' - {i}'
                _create_children_text(
                    x_obj,
                    {
                        "GO001": cutm150(schoben, 30 - len(suffix)) + suffix,
                        "GO002": 'B',
                        "GO003": 'Poly',
                    },
                )
                for j, point in enumerate(part):
                    xpt = point.x()
                    ypt = point.y()
                    suffix = f'-{j}'
                    _create_children_text(
                        SubElement(x_obj, "GP"),
                        {
                            "GP001": cutm150(schoben, 30 - len(suffix)) + suffix,
                            "GP002": self.ksys,
                            self.gp_x: formatm150(xpt),
                            self.gp_y: formatm150(ypt),
                        },
                    )

    def _export_auslaesse(self) -> None:
        if not QKan.config.check_export.auslaesse:
            return

        sqlnam = 'm150_ex_schaechte' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters={'schachttyp': 'Auslass'}
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Auslaesse'")
            raise QkanDbError

        for (
            schnam,
            deckelhoehe,
            sohlhoehe,
            tiefe,
            knotenart,
            durchm,
            entwart,
            strasse,
            strassenname,
            baujahr,
            bauwerksart,
            simstatus,
            material,
            kommentar,
            geobline,
            geobpoint,
        ) in self.db_qkan.fetchall():

            geop = QgsGeometry()
            geop.fromWkb(geobpoint)
            ptsch = geop.asPoint()
            xsch = ptsch.x()
            ysch = ptsch.y()

            if geobline is None:
                ptlis = []
            else:
                geom = QgsGeometry()
                geom.fromWkb(geobline)
                ptlis = geom.asMultiPolyline()              # Achtung: 2-dimensional

            x_elem = SubElement(self.root, "KG")
            _create_children_text(
                x_elem,
                {
                    "KG001": cutm150(schnam, 16),
                    "KG101": strasse,
                    "KG102": strassenname,
                    "KG211": formatm150(tiefe),
                    "KG301": 'K',
                    "KG302": entwart,
                    "KG303": None if baujahr is None else f'{baujahr:d}',
                    "KG304": material,
                    "KG305": knotenart,
                    "KG306": bauwerksart,
                    "KG309": None if durchm is None else f'{durchm:d}',
                    "KG401": simstatus,
                    "KG407": 'B',
                    "KG999": kommentar,
                },
            )

            #Schachtsohle
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'G',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(sohlhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            #Deckel
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'D',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(deckelhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            # Geometrieobjekt. Wenn ptlis = [] wird diese Schleife übersprungen
            for i, part in enumerate(ptlis):
                x_obj = SubElement(x_elem, "GO")
                suffix = f' - {i}'
                _create_children_text(
                    x_obj,
                    {
                        "GO001": cutm150(schnam, 30 - len(suffix)) + suffix,
                        "GO002": 'B',
                        "GO003": 'Poly',
                    },
                )
                for j, point in enumerate(part):
                    xpt = point.x()
                    ypt = point.y()
                    suffix = f'-{j}'
                    _create_children_text(
                        SubElement(x_obj, "GP"),
                        {
                            "GP001": cutm150(schnam, 30 - len(suffix)) + suffix,
                            "GP002": self.ksys,
                            self.gp_x: formatm150(xpt),
                            self.gp_y: formatm150(ypt),
                        },
                    )

    def _export_header(self) -> None:
        "Kopfzeilen mit Version schreiben"

        x_elem = SubElement(self.root, "FD")
        _create_children_text(
            x_elem,
            {
                "FD001": '04-2010',
                "FD002": 'A',
            },
        )

    def _export_schaechte(self) -> None:
        if not QKan.config.check_export.schaechte:
            return

        sqlnam = 'm150_ex_schaechte' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters={'schachttyp': 'Schacht'}
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Schaechte'")
            raise QkanDbError

        for (
            schnam,
            deckelhoehe,
            sohlhoehe,
            tiefe,
            knotenart,
            durchm,
            entwart,
            strasse,
            strassenname,
            baujahr,
            bauwerksart,
            simstatus,
            material,
            kommentar,
            geobline,
            geobpoint,
        ) in self.db_qkan.fetchall():

            geop = QgsGeometry()
            geop.fromWkb(geobpoint)
            ptsch = geop.asPoint()
            xsch = ptsch.x()
            ysch = ptsch.y()

            if geobline is None:
                ptlis = []
            else:
                geom = QgsGeometry()
                geom.fromWkb(geobline)
                ptlis = geom.asMultiPolyline()              # Achtung: 2-dimensional

            x_elem = SubElement(self.root, "KG")
            _create_children_text(
                x_elem,
                {
                    "KG001": cutm150(schnam, 16),
                    "KG101": strasse,
                    "KG102": strassenname,
                    "KG211": formatm150(tiefe),
                    "KG301": 'K',
                    "KG302": entwart,
                    "KG303": None if baujahr is None else f'{baujahr:d}',
                    "KG304": material,
                    "KG305": knotenart,
                    "KG306": bauwerksart,
                    "KG309": None if durchm is None else f'{durchm:d}',
                    "KG401": simstatus,
                    "KG407": 'B',
                    "KG999": kommentar,
                },
            )

            #Schachtsohle
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'G',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(sohlhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            #Deckel
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'D',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(deckelhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            # Geometrieobjekt. Wenn ptlis = [] wird diese Schleife übersprungen
            for i, part in enumerate(ptlis):
                x_obj = SubElement(x_elem, "GO")
                suffix = f' - {i}'
                _create_children_text(
                    x_obj,
                    {
                        "GO001": cutm150(schnam, 30 - len(suffix)) + suffix,
                        "GO002": 'B',
                        "GO003": 'Poly',
                    },
                )
                for j, point in enumerate(part):
                    xpt = point.x()
                    ypt = point.y()
                    suffix = f'-{j}'
                    _create_children_text(
                        SubElement(x_obj, "GP"),
                        {
                            "GP001": cutm150(schnam, 30 - len(suffix)) + suffix,
                            "GP002": self.ksys,
                            self.gp_x: formatm150(xpt),
                            self.gp_y: formatm150(ypt),
                        },
                    )

    def _export_speicher(self) -> None:
        if not QKan.config.check_export.speicher:
            return

        sqlnam = 'm150_ex_schaechte' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
            parameters={'schachttyp': 'Speicher'}
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Speicher'")
            raise QkanDbError

        for (
            schnam,
            deckelhoehe,
            sohlhoehe,
            tiefe,
            knotenart,
            durchm,
            entwart,
            strasse,
            strassenname,
            baujahr,
            bauwerksart,
            simstatus,
            material,
            kommentar,
            geobline,
            geobpoint,
        ) in self.db_qkan.fetchall():

            geop = QgsGeometry()
            geop.fromWkb(geobpoint)
            ptsch = geop.asPoint()
            xsch = ptsch.x()
            ysch = ptsch.y()

            if geobline is None:
                ptlis = []
            else:
                geom = QgsGeometry()
                geom.fromWkb(geobline)
                ptlis = geom.asMultiPolyline()              # Achtung: 2-dimensional

            x_elem = SubElement(self.root, "KG")
            _create_children_text(
                x_elem,
                {
                    "KG001": cutm150(schnam, 16),
                    "KG101": strasse,
                    "KG102": strassenname,
                    "KG211": formatm150(tiefe),
                    "KG301": 'K',
                    "KG302": entwart,
                    "KG303": None if baujahr is None else f'{baujahr:d}',
                    "KG304": material,
                    "KG305": knotenart,
                    "KG306": bauwerksart,
                    "KG309": None if durchm is None else f'{durchm:d}',
                    "KG401": simstatus,
                    "KG407": 'B',
                    "KG999": kommentar,
                },
            )

            #Schachtsohle
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'G',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(sohlhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            #Deckel
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'D',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(deckelhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            # Geometrieobjekt. Wenn ptlis = [] wird diese Schleife übersprungen
            for i, part in enumerate(ptlis):
                x_obj = SubElement(x_elem, "GO")
                suffix = f' - {i}'
                _create_children_text(
                    x_obj,
                    {
                        "GO001": cutm150(schnam, 30 - len(suffix)) + suffix,
                        "GO002": 'B',
                        "GO003": 'Poly',
                    },
                )
                for j, point in enumerate(part):
                    xpt = point.x()
                    ypt = point.y()
                    suffix = f'-{j}'
                    _create_children_text(
                        SubElement(x_obj, "GP"),
                        {
                            "GP001": cutm150(schnam, 30 - len(suffix)) + suffix,
                            "GP002": self.ksys,
                            self.gp_x: formatm150(xpt),
                            self.gp_y: formatm150(ypt),
                        },
                    )

    def _export_haltungen(self) -> None:
        if not QKan.config.check_export.haltungen:
            # or not self.hydraulik_objekte
            return

        sqlnam = 'm150_ex_haltungen' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Haltungen'")
            raise QkanDbError

        for (
            haltnam,
            schoben,
            schunten,
            hoehe,
            breite,
            laenge,
            rohrlaenge,
            sohleoben,
            sohleunten,
            profil,
            strasse,
            strassenname,
            material,
            entwart,
            baujahr,
            profilauskleidung,
            innenmaterial,
            simstatus,
            kommentar,
            gline,
        ) in self.db_qkan.fetchall():

            x_elem = SubElement(self.root, "HG")
            _create_children_text(
                x_elem,
                {
                    "HG001": cutm150(haltnam, 33),
                    "HG003": cutm150(schoben, 16),
                    "HG004": cutm150(schunten, 16),
                    "HG101": strasse,
                    "HG102": strassenname,
                    "HG301": 'K',
                    "HG302": entwart,
                    "HG303": None if baujahr is None else f'{baujahr:d}',
                    "HG304": material,
                    "HG305": profil,
                    "HG306": formatm150(breite),
                    "HG307": formatm150(hoehe),
                    "HG310": formatm150(laenge),
                    "HG313": 'A',
                    "HG314": rohrlaenge,
                    "HG401": simstatus,
                    "HG999": kommentar,
                },
            )

            geom = QgsGeometry()
            geom.fromWkb(gline)
            ptlis = geom.asPolyline()
            npt = len(ptlis)
            if npt == 2:
                objecttyp = 'L'
            elif npt > 2:
                objecttyp = 'Poly'
            else:
                logger.error_data(f"Die Haltungsgeometrie {geom=} hat weniger als 2 Punkte")
                raise QkanAbortError

            x_line = SubElement(x_elem, "GO")
            _create_children_text(
                x_line,
                {
                    "GO001": cutm150(haltnam, 30),
                    "GO002": 'H',
                    "GO003": objecttyp,
                },
            )

            # Erste Stützstelle
            pt = ptlis[0]
            x_point = SubElement(x_line, "GP")
            _create_children_text(
                x_point,
                {
                    "GP001": cutm150(schoben, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(pt.x()),
                    self.gp_y: formatm150(pt.y()),
                    "GP007": formatm150(sohleoben),
                },
            )

            # Alle Stützstellen außer erster und letzter
            for ip, pt in enumerate(ptlis[1:-1]):
                x_point = SubElement(x_line, "GP")
                suffix = f'-{ip-1}'
                _create_children_text(
                    x_point,
                    {
                        "GP001": cutm150(haltnam, 30 - len(suffix)) + suffix,
                        "GP002": self.ksys,
                        self.gp_x: formatm150(pt.x()),
                        self.gp_y: formatm150(pt.y()),
                    },
                )

            # Letzte Stützstelle
            pt = ptlis[-1]
            x_point = SubElement(x_line, "GP")
            _create_children_text(
                x_point,
                {
                    "GP001": cutm150(schunten, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(pt.x()),
                    self.gp_y: formatm150(pt.y()),
                    "GP007": formatm150(sohleunten),
                },
            )

    def _export_anschlussleitungen(self) -> None:
        if not QKan.config.check_export.anschlussleitungen:
            # or not self.hydraulik_objekte
            return

        sqlnam = 'm150_ex_anschlussleitungen' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Anschlussleitungen'")
            raise QkanDbError

        for (
            leitnam,
            asoben,
            asunten,
            haltnam,
            haoben,
            haunten,
            urstation,
            lageanschluss,
            knotenart,
            hoehe,
            breite,
            laenge,
            sohleoben,
            sohleunten,
            strasse,
            strassenname,
            profil,
            material,
            entwart,
            simstatus,
            baujahr,
            aussendurchmesser,
            profilauskleidung,
            innenmaterial,
            kommentar,
            gline
        ) in self.db_qkan.fetchall():
            x_elem = SubElement(self.root, "HG")
            _create_children_text(
                x_elem,
                {
                    "HG001": cutm150(haltnam, 33),
                    "HG003": cutm150(haoben, 16),
                    "HG004": cutm150(haunten, 16),
                    "HG005": cutm150(asunten, 33),
                    "HG006": 'H',
                    "HG007": urstation,
                    "HG008": 'I',                   # QKan-Standard: in Fließrichtung
                    "HG009": lageanschluss,
                    "HG010": knotenart,
                    "HG011": cutm150(leitnam, 33),
                    "HG101": strasse,
                    "HG102": strassenname,
                    "HG301": 'K',
                    "HG302": entwart,
                    "HG303": None if baujahr is None else f'{baujahr:d}',
                    "HG304": material,
                    "HG306": formatm150(breite),
                    "HG307": formatm150(hoehe),
                    "HG308": profilauskleidung,
                    "HG309": innenmaterial,
                    "HG310": formatm150(laenge),
                    "HG313": 'B',
                    "HG401": simstatus,
                    "HG999": kommentar,
                },
            )

            geom = QgsGeometry()
            geom.fromWkb(gline)
            ptlis = geom.asPolyline()
            npt = len(ptlis)
            if npt == 2:
                objecttyp = 'L'
            elif npt > 2:
                objecttyp = 'Poly'
            else:
                logger.error_data(f"Fehler beim Erzeugen des Geoobjektes: {ptlis=}")
                raise QkanAbortError

            x_line = SubElement(x_elem, "GO")
            _create_children_text(
                x_line,
                {
                    "GO001": cutm150(leitnam, 30),
                    "GO002": 'H',
                    "GO003": objecttyp
                },
            )

            # Erste Stützstelle
            pt = ptlis[0]
            x_point = SubElement(x_line, "GP")
            _create_children_text(
                x_point,
                {
                    "GP001": cutm150(asoben, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(pt.x()),
                    self.gp_y: formatm150(pt.y()),
                    "GP007": formatm150(sohleoben),
                },
            )

            # Alle Stützstellen außer erster und letzter
            for ip, pt in enumerate(ptlis[1:-1]):
                x_point = SubElement(x_line, "GP")
                suffix = f'-{ip+1}'
                _create_children_text(
                    x_point,
                    {
                        "GP001": cutm150(leitnam, 30 - len(suffix)) + suffix,
                        "GP002": self.ksys,
                        self.gp_x: formatm150(pt.x()),
                        self.gp_y: formatm150(pt.y()),
                    },
                )

            # Letzte Stützstelle
            pt = ptlis[-1]
            x_point = SubElement(x_line, "GP")
            _create_children_text(
                x_point,
                {
                    "GP001": cutm150(asunten, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(pt.x()),
                    self.gp_y: formatm150(pt.y()),
                    "GP007": formatm150(sohleunten),
                },
            )


    def _export_anschlussschaechte(self) -> None:
        if not QKan.config.check_export.anschlussschaechte:
            # or not self.hydraulik_objekte
            return

        sqlnam = 'm150_ex_anschlussschaechte' + self.select

        if not self.db_qkan.sqlyml(
            sqlnam=sqlnam,
            stmt_category=sqlnam,
        ):
            logger.error_code(f"{self.__class__.__name__}: Fehler in 'm150 Export Anschlussschaechte'")
            raise QkanDbError

        for (
            schnam,
            sohlhoehe,
            deckelhoehe,
            tiefe,
            durchm,
            entwart,
            strasse,
            strassenname,
            baujahr,
            simstatus,
            material,
            knotenart,
            kommentar,
            geopoint,
        ) in self.db_qkan.fetchall():

            geop = QgsGeometry()
            geop.fromWkb(geopoint)
            ptsch = geop.asPoint()
            xsch = ptsch.x()
            ysch = ptsch.y()

            x_elem = SubElement(self.root, "KG")
            _create_children_text(
                x_elem,
                {
                    "KG001": cutm150(schnam, 16),
                    "KG101": strasse,
                    "KG102": strassenname,
                    "KG211": formatm150(tiefe),
                    "KG301": 'K',
                    "KG302": entwart,
                    "KG303": None if baujahr is None else f'{baujahr:d}',
                    "KG304": material,
                    "KG305": knotenart,
                    "KG309": None if durchm is None else f'{durchm:d}',
                    "KG401": simstatus,
                    "KG407": 'B',
                    "KG999": kommentar,
                },
            )

            #Schachtsohle
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'G',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(sohlhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

            #Deckel
            x_obj = SubElement(x_elem, "GO")
            _create_children_text(
                x_obj,
                {
                    "GO001": cutm150(schnam, 30),
                    "GO002": 'D',
                    "GO003": 'Pkt',
                },
            )

            _create_children_text(
                SubElement(x_obj, "GP"),
                {
                    "GP001": cutm150(schnam, 30),
                    "GP002": self.ksys,
                    self.gp_x: formatm150(xsch),
                    self.gp_y: formatm150(ysch),
                    "GP007": formatm150(deckelhoehe),
                    "GP010": QKan.config.check_export.hoehensystem,
                },
            )

    def run(self) -> None:
        """
        Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in eine XML-Datei
        """
        iface = QKan.instance.iface

        self.db_qkan.loadmodule("m150porter")

        # Create progress bar
        progress_bar = QProgressBar(iface.messageBar())
        progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Export in Arbeit. Bitte warten..."
        )
        status_message.layout().addWidget(progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.MessageLevel.Info, 10)

        fortschritt("Export startet...", 0.05)

        # region Create XML structure
        self.root = Element("DATA", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", }
        )

        # Export

        # 2 Selektionsfaktoren: ausgewählte, fehlende
        if QKan.config.selections.selectedObjects:
            self.select = '_sel'
        else:
            self.select = '_all'
        if QKan.config.check_export.includeMissingKeys:
            self.select += '_include'

        # self._prepare_refdata()              ; fortschritt("Rerenzdaten aus import übernommen", 0.10)
        self._export_header()
        self._export_schaechte()            ; fortschritt("Schächte geschrieben", 0.30)
        self._export_wehre()                ; fortschritt("Wehre geschrieben", 0.35)
        self._export_pumpen()               ; fortschritt("Pumpen geschrieben", 0.40)
        self._export_auslaesse()            ; fortschritt("Auslässe geschrieben", 0.45)
        self._export_speicher()             ; fortschritt("Speicher geschrieben", 0.50)
        self._export_anschlussschaechte()   ; fortschritt("Anschlussleitungen geschrieben", 0.95)
        self._export_haltungen()            ; fortschritt("Haltungen geschrieben", 0.75)
        self._export_anschlussleitungen()   ; fortschritt("Anschlussleitungen geschrieben", 0.85)
        # self._export_haltungen_inspektion() ; fortschritt("Haltungen Inspektion geschrieben", 0.60)
        # self._export_schaechte_inspektion() ; fortschritt("Schächte geschrieben", 0.4)
        self._export_refdata()              ; fortschritt("Referenzdaten geschrieben", 0.95)

        Path(self.export_file).write_bytes(
            minidom.parseString(tostring(self.root)).toprettyxml(
                indent="  ",
                standalone = False,
                encoding = 'iso-8859-1'
            )
        )

        # Close connection
        del self.db_qkan

        fortschritt("Export abgeschlossen.", 1)
        progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")
        status_message.setLevel(Qgis.MessageLevel.Success)
