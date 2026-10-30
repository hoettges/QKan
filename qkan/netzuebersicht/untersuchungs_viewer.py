"""Öffnet den QKan-Medieninspektor für ein Objekt aus der Netzübersicht."""

from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject
from qgis.utils import iface

from qkan.inspektion.befahrungsmedien import BefahrungsmedienDialog
from qkan.inspektion.datenquelle import datenquelle_waehlen, layerdaten
from .gis_actions import layer_import_aktuell


# Netzuebersicht-Tab -> Objektart des QKan-Medieninspektors, DB-Tabelle,
# Schluesselspalte und moegliche Namen des zugehoerigen QGIS-Layers.
OBJEKTARTEN = {
    0: ("Haltung", "haltungen", "haltnam", ("Haltungen",)),
    1: ("Schacht", "schaechte", "schnam", ("Schächte",)),
    2: ("Anschlussleitung", "anschlussleitungen", "leitnam", (
        "Anschlussleitungen", "HA-Leitungen", "GAL"
    )),
}
NOTWENDIGE_TABELLEN = ("haltungen", "schaechte", "anschlussleitungen")


def show_object_untersuchung(self):
    """Übernimmt genau eine Tabellenzeile in die kompakte Inspektionsansicht.

    Der Medieninspektor erhält eine QKan-Datenquelle und den Objektnamen.
    Er liest Befahrungen, Schäden und Medien selbst; eine gemeinsame
    native DB-Verbindung mit der Netzübersicht ist nicht erforderlich.
    """
    config = OBJEKTARTEN.get(self.tab_Overview.currentIndex())
    if config is None:
        QMessageBox.warning(self, "Netzübersicht", "Dieser Tab wird nicht unterstützt.")
        return
    objektart, tabellenname, schluesselspalte, layernamen = config
    tabellenmodell = (
        self.model_haltungen if tabellenname == "haltungen" else
        self.model_schaechte if tabellenname == "schaechte" else
        self.model_anschlussleitungen
    )
    proxy = (
        self.proxy_model_haltungen if tabellenname == "haltungen" else
        self.proxy_model_schaechte if tabellenname == "schaechte" else
        self.proxy_model_anschlussleitungen
    )
    tabelle = (
        self.tableView_Haltungen if tabellenname == "haltungen" else
        self.tableView_Schaechte if tabellenname == "schaechte" else
        self.tableView_GAL
    )
    selection = tabelle.selectionModel()
    rows = selection.selectedRows() if selection else []
    if len(rows) != 1:
        QMessageBox.information(
            self, "Untersuchungen anzeigen",
            "Bitte genau ein Objekt in der Tabelle auswählen.",
        )
        return
    column_index = tabellenmodell.record().indexOf(schluesselspalte)
    if column_index < 0:
        QMessageBox.warning(
            self, "Untersuchungen anzeigen",
            f"Schlüsselspalte '{schluesselspalte}' wurde nicht gefunden.",
        )
        return
    source_index = proxy.mapToSource(rows[0])
    object_name = tabellenmodell.data(
        source_index.sibling(source_index.row(), column_index), Qt.DisplayRole
    )
    object_name = str(object_name).strip() if object_name is not None else ""
    if not object_name:
        QMessageBox.warning(self, "Untersuchungen anzeigen", "Der Objektname ist leer.")
        return

    # Den passenden Layer für die Kartenauswahl aktivieren; die Auswahl
    # selbst wird bei einem Objekt bewusst nicht auf mehrere ausgedehnt.
    projekt = QgsProject.instance()
    layers = []
    for name in layernamen:
        layers = projekt.mapLayersByName(name)
        if layers:
            break
    if not layers:
        layer_import_aktuell(self)
        for name in layernamen:
            layers = projekt.mapLayersByName(name)
            if layers:
                break
    if not layers:
        QMessageBox.warning(
            self, "Untersuchungen anzeigen",
            f"Kein passender QKan-Layer gefunden ({', '.join(layernamen)}).",
        )
        return
    layer = layers[0]
    iface.setActiveLayer(layer)
    escaped_name = object_name.replace("'", "''")
    expression = '"' + schluesselspalte + '" = ' + chr(39) + escaped_name + chr(39)
    layer.selectByExpression(expression)

    # Datenquelle des konkreten Layers benutzen, um bei mehreren offenen
    # QKan-Datenbanken nicht versehentlich Daten aus einer anderen zu öffnen.
    layer_info = layerdaten(layer)
    if layer_info is not None and layer_info[0] == tabellenname:
        datenquelle = layer_info[1]
    else:
        datenquelle = datenquelle_waehlen(
            projekt, NOTWENDIGE_TABELLEN, self, "QKan – Befahrungsmedien"
        )
    if datenquelle is None:
        QMessageBox.warning(
            self, "Untersuchungen anzeigen",
            "Keine geeignete QKan-Datenquelle gefunden.",
        )
        return

    try:
        dialog = getattr(self, "viewer_dialog", None)
        if dialog is None:
            dialog = BefahrungsmedienDialog(iface, parent=self, viewer_only=True)
            self.viewer_dialog = dialog
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

        # _objekt_auswaehlen lädt genau dieses Objekt, die neueste
        # Befahrung, alle Schäden und deren Fotos/Videos/Panoramo-Medien.
        # Der Aufruf erfolgt erst nach Anzeige des Dialogs (wie beim
        # bereits vorhandenen TV-Werkzeug in qkan.inspektion).
        def objekt_laden():
            try:
                dialog._objekt_auswaehlen(objektart, object_name, datenquelle)
            except Exception as error:
                QMessageBox.critical(
                    dialog, "Untersuchungen anzeigen",
                    f"Das Objekt konnte nicht geladen werden:\n{error}",
                )
        QTimer.singleShot(0, objekt_laden)
    except Exception as error:
        QMessageBox.critical(
            self, "Untersuchungen anzeigen",
            f"Der Medieninspektor konnte nicht geöffnet werden:\n{error}",
        )
