"""Steuert die interaktive Erstellung neuer Schächte in QGIS."""

import os

from qgis.core import QgsProject
from qgis.utils import iface, pluginDirectory
from qgis.PyQt.QtWidgets import QMessageBox

from .datenquelle import datenquelle_waehlen, layer_finden


def create_schacht():
    """Aktiviert oder beendet das Werkzeug zum Erstellen eines Schachts."""

    project = QgsProject.instance()

    datenquelle = datenquelle_waehlen(
        project,
        ("schaechte",),
        iface.mainWindow(),
        "QKan – Schacht erstellen",
        getattr(create_schacht, "_datenquelle", None)
        if getattr(create_schacht, "_active", False)
        else None,
    )
    layer = (
        layer_finden(project, "schaechte", datenquelle)
        if datenquelle is not None
        else None
    )

    if layer is None:
        QMessageBox.warning(
            iface.mainWindow(),
            "QKan",
            "Es wurde kein eindeutiger QKan-Layer 'Schächte' aus der "
            "Tabelle 'schaechte' gefunden. Unterstützt werden SpatiaLite "
            "und PostgreSQL/PostGIS."
        )
        return

    # -------------------------------------------------
    # Plugin-Action holen
    # -------------------------------------------------

    action = getattr(iface, "action_create_schacht", None)

    if action is None:
        action = iface.actionAddFeature()

    # -------------------------------------------------
    # Mehrfachausführung durch verschachtelte QGIS-Signale verhindern
    # -------------------------------------------------

    if getattr(create_schacht, "_running", False):
        return

    # -------------------------------------------------
    # Bereits aktiven Erfassungsmodus beenden
    # -------------------------------------------------

    if getattr(create_schacht, "_active", False):
        iface.actionPan().trigger()
        action.setChecked(False)
        create_schacht._active = False
        create_schacht._datenquelle = None
        return

    # -------------------------------------------------
    # NEU: andere Buttons deaktivieren
    # -------------------------------------------------

    for name in [
        "action_create_haltung",
        "action_change_schacht",
        "action_change_haltung",
        "action_export_teilgebiet"
    ]:
        other = getattr(iface, name, None)
        if other and other is not action:
            other.setChecked(False)

    # -------------------------------------------------
    # richtiges Formular setzen
    # -------------------------------------------------

    form_path = os.path.join(
        pluginDirectory("qkan"),
        "forms",
        "qkan_schaechte.ui"
    )

    config = layer.editFormConfig()
    config.setUiForm(form_path)
    layer.setEditFormConfig(config)

    # -------------------------------------------------
    # Layer aktivieren
    # -------------------------------------------------

    iface.setActiveLayer(layer)

    # -------------------------------------------------
    # Bearbeitungsmodus starten
    # -------------------------------------------------

    if not layer.isEditable():
        if not layer.startEditing():
            QMessageBox.warning(
                iface.mainWindow(),
                "QKan",
                "Bearbeitungsmodus für Layer 'Schächte' konnte nicht "
                "gestartet werden."
            )
            return

    # -------------------------------------------------
    # Zeichnen starten
    # -------------------------------------------------

    action.setChecked(True)
    create_schacht._active = True
    create_schacht._datenquelle = datenquelle
    iface.actionAddFeature().trigger()

    # -------------------------------------------------
    # Nach Feature-Erstellung: Modus beenden
    # -------------------------------------------------

    def stop_digitizing(*args):
        """Beendet den Erstellungsmodus nach dem Anlegen eines Schachts.

        :param args: Vom QGIS-Signal übergebene Argumente.
        """

        if getattr(create_schacht, "_running", False):
            return
        create_schacht._running = True

        iface.actionPan().trigger()
        action.setChecked(False)
        create_schacht._active = False
        create_schacht._datenquelle = None

        layer.featureAdded.disconnect(stop_digitizing)

        create_schacht._running = False

    old_handler = getattr(create_schacht, "_feature_added_handler", None)
    if old_handler is not None:
        layer.featureAdded.disconnect(old_handler)

    create_schacht._feature_added_handler = stop_digitizing
    layer.featureAdded.connect(stop_digitizing)
