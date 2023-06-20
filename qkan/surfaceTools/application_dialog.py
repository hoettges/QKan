import os
from typing import Callable, Optional, List
import logging

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLabel, QWidget, QComboBox, QCheckBox, QListWidget, \
    QListWidgetItem
from qkan.database.dbfunc import DBConnection
from qkan import QKan, list_selected_items

logger = logging.getLogger(f"QKan.surfaceTools.application_dialog")


class _Dialog(QDialog):
    def __init__(
            self,
            default_dir: str,
            tr: Callable,
            parent: Optional[QWidget] = None,
    ):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)
        self.default_dir = str(default_dir)
        logger.debug(
            f"swmm.application_dialog._Dialog.__init__:"
            f"\nself.default_dir: {self.default_dir}"
        )
        self.tr = tr


SURFACE_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "surfaceTool.ui")
)


class SurfaceToolDialog(_Dialog, SURFACE_CLASS):  # type: ignore
    buttonBox: QDialogButtonBox
    label_2: QLabel
    label: QLabel
    cb_haupt: QComboBox
    cb_geschnitten: QComboBox

    def __init__(self,
                 default_dir: str,
                 tr: Callable,
                 parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super().__init__(default_dir, tr, parent)
        self.setupUi(self)

    def prepareDialog(self, database_qkan: str, epsg: int) -> bool:
        """Bereitet das Formular vor"""

        self.database_qkan = database_qkan
        self.epsg = epsg

        self.cb_haupt.clear()
        self.cb_geschnitten.clear()

        with DBConnection(dbname=self.database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in surfaceTools.SurfaceToolDialog.prepareDialog:\n"
                    f"QKan-Datenbank {self.database_qkan:s} wurde nicht"
                    " gefunden oder war nicht aktuell!\nAbbruch!"
                )
                return False
            if not db_qkan.sql("SELECT abflussparameter FROM flaechen", mute_logger=True):
                return False

            temp_list = db_qkan.fetchall()

        abflussparameter = list(set(temp_list))
        for tempAttr in abflussparameter:
            attr = str(tempAttr).lstrip("('").rstrip(",')")
            self.cb_haupt.addItem(attr)
            self.cb_geschnitten.addItem(attr)

        return True


VORONOI_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "voronoiTool.ui")
)


class VoronoiDialog(_Dialog, VORONOI_CLASS):  # type: ignore
    """Erzeugen von Haltungsflächen.
    Dabei werden in der Tabelle tezg für Haltungen, deren "Entwässerungsart"
    in der Listebox "lw_hal_entw" ausgewählt wurden, zunächst temporäre
    Voronoi-Flächen erzeugt und damit anschließend für
    ausgewählte Flächen (flaechen where aufteilen) die mit diesen überschneidenden
    Flächen in der Tabelle tezg verschnitten.
    """

    buttonBox: QDialogButtonBox
    label_1: QLabel
    label_2: QLabel
    label_3: QLabel
    lf_anzahl_haltungen: QLabel
    lf_anzahl_flaechen: QLabel
    lf_warning: QLabel
    cb_selHalActive: QCheckBox
    lw_hal_entw: QListWidget

    database_qkan: str = ''

    def __init__(self,
                 default_dir: str,
                 tr: Callable,
                 parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super().__init__(default_dir, tr, parent)
        self.setupUi(self)

        self.lw_hal_entw.itemClicked.connect(self.click_lw_hal_entw)
        self.cb_selHalActive.stateChanged.connect(self.click_hal_selection)

    def click_lw_hal_entw(self) -> None:
        """Reaktion auf Klick in Listbox"""

        self.cb_selHalActive.setChecked(True)
        self.count_selection()

    def click_hal_selection(self) -> None:
        """Reagktion auf Checkbox zur Aktivierung der Auswahl"""

        # Checkbox hat den Status nach dem Klick
        if self.cb_selHalActive.isChecked():
            # Nix tun ...
            pass
        else:
            # Auswahl deaktivieren und Liste zurücksetzen
            anz = self.lw_hal_entw.count()
            for i in range(anz):
                item = self.lw_hal_entw.item(i)
                item.setSelected(False)

            # Anzahl in der Anzeige aktualisieren
            self.count_selection()

    def count_selection(self) -> None:
        """Zählt nach Änderung der Auswahl in der Liste im Formular die Anzahl
        der betroffenen Haltungen"""

        liste_hal_entw: List[str] = list_selected_items(self.lw_hal_entw)

        # Zu berücksichtigende Haltungen zählen
        if len(liste_hal_entw) == 0:
            auswahl = ""
        else:
            auswahl = " WHERE haltungen.entwart in ('{}')".format(
                "', '".join(liste_hal_entw)
            )

        with DBConnection(dbname=self.database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in surfaceTools.VoronoiDialog.count_selection:\n"
                    "QKan-Datenbank %s wurde nicht"
                    " gefunden oder war nicht aktuell!\nAbbruch!", self.database_qkan
                )
                return

            # Anzahl betroffene Flächen abfragen
            sql = "SELECT count(*) AS anz FROM flaechen WHERE aufteilen"
            if not db_qkan.sql(sql, mute_logger=True):
                return
            anz_flaechen = db_qkan.fetchone()

            sql = f"SELECT count(*) AS anzahl FROM haltungen {auswahl}"
            if not db_qkan.sql(sql, "count_selection"):
                return
            anz_haltungen = db_qkan.fetchone()

        logger.debug(f'{__name__}.count_selection (177): {anz_flaechen[0]}')
        logger.debug(f'Methoden von lf_warning: {dir(self.lf_warning)}')
        if not (anz_flaechen is None):
            self.lf_anzahl_flaechen.setText(str(anz_flaechen[0]))
            if anz_flaechen[0]==0:
                self.lf_warning.setText(
                    "Warnung: Es wurde keine aufzuteilenden Flächen gefunden!"
                )
            else:
                self.lf_warning.setText("")
        else:
            self.lf_anzahl_flaechen.clear()
            self.lf_warning.setText(
                "Warnung: Es wurde keine aufzuteilenden Flächen gefunden!"
            )
        logger.debug(f'lf_warning.text: {self.lf_warning.text()}')

        if not (anz_haltungen is None):
            self.lf_anzahl_haltungen.setText(str(anz_haltungen[0]))
        else:
            self.lf_anzahl_haltungen.clear()


    def prepareDialog(self, database_qkan: str, epsg: int) -> bool:
        """Bereitet das Formular vor"""

        self.database_qkan = database_qkan
        self.epsg = epsg

        self.lw_hal_entw.clear()

        with DBConnection(dbname=self.database_qkan) as db_qkan:
            if not db_qkan.connected:
                logger.error(
                    "Fehler in surfaceTools.VoronoiDialog.prepareDialog:\n"
                    "QKan-Datenbank %s wurde nicht"
                    " gefunden oder war nicht aktuell!\nAbbruch!", self.database_qkan
                )
                return False
            if not db_qkan.sql("SELECT abflussparameter FROM flaechen", mute_logger=True):
                return False

            sql = 'SELECT "entwart" FROM "haltungen" GROUP BY "entwart"'
            if not db_qkan.sql(sql, "QKan_LinkFlaechen.run_createlinefl (2)", mute_logger=True):
                return False

            daten = db_qkan.fetchall()

        self.lw_hal_entw.clear()
        for ielem, elem in enumerate(daten):
            if elem[0] is not None:
                self.lw_hal_entw.addItem(QListWidgetItem(elem[0]))
                if elem[0] in QKan.config.selections.hal_entw:
                    self.lw_hal_entw.setCurrentRow(ielem)
                    self.cb_selHalActive.setChecked(True)

        logger.debug(f'Modul {__name__}, \n'
                     f'QKan.config.selections.hal_entw: {QKan.config.selections.hal_entw}\n'
                     f'daten: {daten}')

        self.count_selection()
