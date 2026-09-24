"""Steuert die interaktive Erstellung neuer Haltungen in QGIS."""

import os
import re

from qgis.core import (
    QgsProject,
    QgsEditFormConfig
)

from qgis.utils import iface, pluginDirectory
from qgis.PyQt.QtWidgets import QMessageBox, QLineEdit, QDialog, QPushButton

from .datenquelle import datenquelle_waehlen, layer_finden


def create_haltung():
    """Aktiviert oder beendet das Werkzeug zum Erstellen einer Haltung."""

    project = QgsProject.instance()

    # ------------------------------------------
    # Haltungs-Layer finden
    # ------------------------------------------

    datenquelle = datenquelle_waehlen(
        project,
        ("haltungen", "schaechte"),
        iface.mainWindow(),
        "QKan – Haltung erstellen",
        getattr(create_haltung, "_datenquelle", None)
        if getattr(create_haltung, "_active", False)
        else None,
    )
    layer = (
        layer_finden(project, "haltungen", datenquelle)
        if datenquelle is not None
        else None
    )

    if layer is None:
        QMessageBox.warning(
            iface.mainWindow(),
            "QKan",
            "Es wurde keine vollständige, eindeutige QKan-Datenquelle mit "
            "den Layern 'Haltungen' und 'Schächte' gefunden. Unterstützt "
            "werden SpatiaLite und PostgreSQL/PostGIS."
        )
        return

    schacht_layer = layer_finden(project, "schaechte", datenquelle)
    if schacht_layer is None:
        QMessageBox.warning(
            iface.mainWindow(),
            "QKan",
            "In derselben QKan-Datenquelle wurde kein eindeutiger Layer "
            "'Schächte' aus der Tabelle 'schaechte' gefunden."
        )
        return

    iface.setActiveLayer(layer)

    # ------------------------------------------
    # Plugin-Action holen
    # ------------------------------------------

    action = getattr(iface, "action_create_haltung", None)

    if action is None:
        action = iface.actionAddFeature()

    # ------------------------------------------
    # Mehrfachausführung durch verschachtelte QGIS-Signale verhindern
    # ------------------------------------------

    if getattr(create_haltung, "_running", False):
        return

    # ------------------------------------------
    # Bereits aktiven Erfassungsmodus beenden
    # ------------------------------------------

    if getattr(create_haltung, "_active", False):

        config = layer.editFormConfig()
        config.setSuppress(QgsEditFormConfig.SuppressOff)
        layer.setEditFormConfig(config)

        iface.actionPan().trigger()

        action.setChecked(False)
        create_haltung._active = False
        create_haltung._datenquelle = None

        handler = getattr(create_haltung, "_feature_added_handler", None)
        if handler is not None:
            try:
                layer.featureAdded.disconnect(handler)
            except TypeError:
                pass
            create_haltung._feature_added_handler = None

        layer.commitChanges()
        return

    # ------------------------------------------
    # andere Buttons deaktivieren
    # ------------------------------------------

    for name in [
        "action_create_schacht",
        "action_change_schacht",
        "action_change_haltung",
        "action_export_teilgebiet"
    ]:
        other = getattr(iface, name, None)
        if other and other is not action:
            other.setChecked(False)

    # ------------------------------------------
    # alte Signalverbindung entfernen
    # ------------------------------------------

    old_handler = getattr(create_haltung, "_feature_added_handler", None)
    if old_handler is not None:
        try:
            layer.featureAdded.disconnect(old_handler)
        except TypeError:
            pass
        create_haltung._feature_added_handler = None

    # ------------------------------------------
    # Bearbeitungsmodus
    # ------------------------------------------

    if not layer.isEditable():
        if not layer.startEditing():
            QMessageBox.warning(
                iface.mainWindow(),
                "QKan",
                "Bearbeitungsmodus konnte nicht gestartet werden."
            )
            return

    # ------------------------------------------
    # Formular deaktivieren
    # ------------------------------------------

    config = layer.editFormConfig()
    config.setSuppress(QgsEditFormConfig.SuppressOn)

    # ------------------------------------------
    # Create-UI Pfad
    # ------------------------------------------

    create_form_path = os.path.join(
        pluginDirectory("qkan"),
        "inspektion",
        "res",
        "qkan_create_haltungen.ui"
    )

    config.setUiForm(create_form_path)
    layer.setEditFormConfig(config)

    # ------------------------------------------
    # Werkzeugwechsel oder Abbruch der Erfassung erkennen
    # ------------------------------------------

    def on_tool_changed(new_tool, old_tool):
        """Setzt den Erstellungsmodus nach einem Werkzeugwechsel zurück.

        :param new_tool: Neu aktiviertes Kartenwerkzeug.
        :param old_tool: Zuvor aktives Kartenwerkzeug.
        """

        if not action.isChecked():
            return

        # Tool wurde beendet → reset
        if not iface.actionAddFeature().isChecked():

            config = layer.editFormConfig()
            config.setSuppress(QgsEditFormConfig.SuppressOff)
            layer.setEditFormConfig(config)

            action.setChecked(False)
            create_haltung._active = False
            create_haltung._datenquelle = None

            iface.mapCanvas().mapToolSet.disconnect(on_tool_changed)

    iface.mapCanvas().mapToolSet.connect(on_tool_changed)

    # ------------------------------------------
    # Nach Feature-Erstellung
    # ------------------------------------------

    def stop_digitizing(fid):
        """Übernimmt eine neu gezeichnete Haltung und öffnet ihr Formular.

        :param fid: Feature-ID der neu erstellten Haltung.
        """

        if getattr(create_haltung, "_running", False):
            return
        create_haltung._running = True

        feature = layer.getFeature(fid)
        geom = feature.geometry()

        if geom is None or geom.isEmpty():
            create_haltung._running = False
            return

        if geom.isMultipart():
            line = geom.asMultiPolyline()[0]
        else:
            line = geom.asPolyline()

        if len(line) < 2:
            create_haltung._running = False
            return

        start_point = line[0]
        end_point = line[-1]

        laenge = round(geom.length(), 3)

        schoben = ""
        schunten = ""

        oben_sohle = None
        oben_deckel = None
        unten_sohle = None
        unten_deckel = None

        min_start = None
        min_end = None

        for f in schacht_layer.getFeatures():

            p = f.geometry().asPoint()

            d_start = p.distance(start_point)
            d_end = p.distance(end_point)

            if min_start is None or d_start < min_start:

                min_start = d_start
                schoben = f["schnam"]
                oben_sohle = f["sohlhoehe"]
                oben_deckel = f["deckelhoehe"]

            if min_end is None or d_end < min_end:

                min_end = d_end
                schunten = f["schnam"]
                unten_sohle = f["sohlhoehe"]
                unten_deckel = f["deckelhoehe"]

        if oben_sohle is not None and unten_sohle is not None:
            if oben_sohle < unten_sohle:

                schoben, schunten = schunten, schoben
                oben_sohle, unten_sohle = unten_sohle, oben_sohle
                oben_deckel, unten_deckel = unten_deckel, oben_deckel

        feature["schoben"] = schoben
        feature["schunten"] = schunten

        if "laenge" in layer.fields().names():
            feature["laenge"] = laenge

        layer.updateFeature(feature)

        dialog = iface.getFeatureForm(layer, feature)

        if dialog:

            def fmt(v):
                """Formatiert einen Wert mit deutschem Dezimaltrennzeichen.

                :param v: Zu formatierender Wert.
                :return: Formatierter Text oder ein Leerstring.
                """
                if v is None:
                    return ""

                if isinstance(v, (int, float)):
                    return f"{float(v):.2f}".replace(".", ",")

                text = str(v).strip().replace(",", ".")
                if re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)", text):
                    return f"{float(text):.2f}".replace(".", ",")

                return str(v).replace(".", ",")

            widget = dialog.findChild(QLineEdit, "schacht_oben_sohle")
            if widget and oben_sohle is not None:
                widget.setText(fmt(oben_sohle))

            widget = dialog.findChild(QLineEdit, "schacht_oben_deckel")
            if widget and oben_deckel is not None:
                widget.setText(fmt(oben_deckel))

            widget = dialog.findChild(QLineEdit, "schacht_unten_sohle")
            if widget and unten_sohle is not None:
                widget.setText(fmt(unten_sohle))

            widget = dialog.findChild(QLineEdit, "schacht_unten_deckel")
            if widget and unten_deckel is not None:
                widget.setText(fmt(unten_deckel))

            widget = dialog.findChild(QLineEdit, "sohleoben")
            if widget and oben_sohle is not None:
                widget.setText(fmt(oben_sohle))

            widget = dialog.findChild(QLineEdit, "sohleunten")
            if widget and unten_sohle is not None:
                widget.setText(fmt(unten_sohle))

            widget = dialog.findChild(QLineEdit, "laenge")
            if widget:
                widget.setText(fmt(laenge))

            def update_neigung():
                """Berechnet die Neigung aus Sohlhöhen und Länge neu."""

                def zahl_aus_feld(feldname):
                    """Liest eine Dezimalzahl aus einem Formularfeld.

                    :param feldname: Objektname des QLineEdit-Felds.
                    :return: Eingelesene Zahl oder ``None`` bei leerer
                        beziehungsweise ungültiger Eingabe.
                    """
                    widget = dialog.findChild(QLineEdit, feldname)
                    if widget is None:
                        return None

                    text = widget.text().strip().replace(",", ".")
                    if not text:
                        return None

                    if not re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)", text):
                        return None

                    return float(text)

                sohle_oben = zahl_aus_feld("sohleoben")
                sohle_unten = zahl_aus_feld("sohleunten")
                laenge_val = zahl_aus_feld("laenge")

                if (
                    sohle_oben is None
                    or sohle_unten is None
                    or laenge_val is None
                ):
                    return

                if laenge_val == 0:
                    return

                delta_h = sohle_oben - sohle_unten
                neigung = (delta_h / laenge_val) * 1000

                neigung_widget = dialog.findChild(QLineEdit, "neigung")

                if neigung_widget:
                    neigung_widget.setText(
                        f"{neigung:.3f}".replace(".", ",")
                    )

            btn = dialog.findChild(QPushButton, "btn_update_neigung")

            if btn:
                btn.clicked.connect(update_neigung)

        result = dialog.exec()

        if result == QDialog.Rejected:
            layer.deleteFeature(fid)

        iface.actionPan().trigger()

        config = layer.editFormConfig()
        config.setSuppress(QgsEditFormConfig.SuppressOff)
        layer.setEditFormConfig(config)

        action.setChecked(False)
        create_haltung._active = False
        create_haltung._datenquelle = None

        try:
            layer.featureAdded.disconnect(stop_digitizing)
        except TypeError:
            pass
        create_haltung._feature_added_handler = None

        create_haltung._running = False

    create_haltung._feature_added_handler = stop_digitizing
    layer.featureAdded.connect(stop_digitizing)

    action.setChecked(True)
    create_haltung._active = True
    create_haltung._datenquelle = datenquelle

    iface.actionAddFeature().trigger()
