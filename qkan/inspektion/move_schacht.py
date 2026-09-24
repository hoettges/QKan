"""Verschiebt Schächte und führt verbundene Netzgeometrien nach."""

import logging
from math import hypot

from qgis.core import QgsGeometry, QgsPointXY, QgsProject
from qgis.utils import iface
from qgis.PyQt.QtWidgets import QMessageBox, QAction
from qgis.gui import QgsAdvancedDigitizingDockWidget

from .datenquelle import datenquelle_waehlen, layer_finden


LOGGER = logging.getLogger(__name__)


# Geometrische Rückfalltoleranzen in den Karteneinheiten des Projekts. Eine
# namentliche Netzbeziehung hat stets Vorrang vor diesem Lagevergleich.
ANSCHLUSS_TOLERANZ = 0.05
SCHACHT_TOLERANZ = 0.10


def _text(wert):
    """Normalisiert einen Attributwert zu Text.

    :param wert: Zu normalisierender Wert.
    :return: Bereinigter Text; ``NULL`` und ``None`` ergeben einen Leerstring.
    """
    if wert is None:
        return ""
    text = str(wert).strip()
    if text.upper() == "NULL":
        return ""
    return text


def _punktabstand(punkt_a, punkt_b):
    """Berechnet den euklidischen Abstand zwischen zwei Punkten.

    :param punkt_a: Erster Kartenpunkt.
    :param punkt_b: Zweiter Kartenpunkt.
    :return: Abstand in Karteneinheiten.
    """
    return hypot(
        float(punkt_a.x()) - float(punkt_b.x()),
        float(punkt_a.y()) - float(punkt_b.y())
    )


def _linienenden(geometrie):
    """Liest Start- und Endpunkt einer Liniengeometrie.

    :param geometrie: Zu prüfende Liniengeometrie.
    :return: Tupel aus Start- und Endpunkt oder ``None``.
    """
    if geometrie is None or geometrie.isEmpty():
        return None

    punkte = list(geometrie.vertices())
    if len(punkte) < 2:
        return None

    return QgsPointXY(punkte[0]), QgsPointXY(punkte[-1])


def _linienende_verschieben(geometrie, ende_index, neuer_punkt):
    """Verschiebt ein Ende einer Liniengeometrie.

    :param geometrie: Ausgangsgeometrie.
    :param ende_index: ``0`` für den Startpunkt, sonst das Linienende.
    :param neuer_punkt: Neue Position des Endpunkts.
    :return: Geänderte Geometrie oder ``None`` bei einem Fehler.
    """
    neue_geometrie = QgsGeometry(geometrie)
    punkte = list(neue_geometrie.vertices())
    if len(punkte) < 2:
        return None

    vertex_index = 0 if ende_index == 0 else len(punkte) - 1
    if not neue_geometrie.moveVertex(
        float(neuer_punkt.x()),
        float(neuer_punkt.y()),
        vertex_index
    ):
        return None

    return neue_geometrie


def _punktgeometrie(punkt):
    """Erzeugt eine Punktgeometrie.

    :param punkt: Zu übernehmender Kartenpunkt.
    :return: QGIS-Punktgeometrie.
    """
    return QgsGeometry.fromPointXY(QgsPointXY(punkt))


def _stationspunkt_nach_aenderung(
    alte_haltungsgeometrie,
    neue_haltungsgeometrie,
    alter_anschlusspunkt,
    urstation
):
    """Überträgt einen Anschlusspunkt auf eine geänderte Haltung.

    :param alte_haltungsgeometrie: Haltung vor der Änderung.
    :param neue_haltungsgeometrie: Haltung nach der Änderung.
    :param alter_anschlusspunkt: Bisheriger Anschlusspunkt.
    :param urstation: Gespeicherte Station der Anschlussleitung.
    :return: Neuer Stationspunkt oder ``None`` bei ungültigen Geometrien.
    """
    if (
        alte_haltungsgeometrie is None
        or alte_haltungsgeometrie.isEmpty()
        or neue_haltungsgeometrie is None
        or neue_haltungsgeometrie.isEmpty()
    ):
        return None

    alte_laenge = float(alte_haltungsgeometrie.length())
    neue_laenge = float(neue_haltungsgeometrie.length())
    if neue_laenge <= 0:
        return None

    try:
        alte_station = float(
            alte_haltungsgeometrie.lineLocatePoint(
                _punktgeometrie(alter_anschlusspunkt)
            )
        )
    except (TypeError, ValueError):
        alte_station = -1.0

    if alte_station < 0:
        alte_station = 0.0

    station = None
    try:
        if urstation not in (None, "", "NULL"):
            station = float(urstation)
    except (TypeError, ValueError):
        station = None

    if station is not None and alte_laenge > 0:
        # In älteren QKan-Beständen kann ``urstation`` je nach Datenquelle
        # vom Linienstart oder vom Linienende aus gemeint sein. Der bisherige
        # reale Anschlusspunkt entscheidet, welche der beiden Lesarten passt.
        station_von_start = max(0.0, min(station, alte_laenge))
        station_von_ende = max(0.0, min(alte_laenge - station, alte_laenge))

        if abs(alte_station - station_von_start) <= abs(
            alte_station - station_von_ende
        ):
            neue_station = max(0.0, min(station, neue_laenge))
        else:
            neue_station = max(
                0.0,
                min(neue_laenge - station, neue_laenge)
            )
    elif alte_laenge > 0:
        # Ohne belastbare Station bleibt die relative Position auf der Haltung
        # erhalten, wenn sich deren Länge durch die Bearbeitung ändert.
        anteil = max(0.0, min(alte_station / alte_laenge, 1.0))
        neue_station = anteil * neue_laenge
    else:
        neue_station = 0.0

    punktgeometrie = neue_haltungsgeometrie.interpolate(neue_station)
    if punktgeometrie is None or punktgeometrie.isEmpty():
        return None

    return QgsPointXY(punktgeometrie.asPoint())


def _laenge_aktualisieren(layer, fid, geometrie):
    """Aktualisiert das Feld ``laenge`` anhand der Geometrie.

    :param layer: Zu bearbeitender Linienlayer.
    :param fid: Feature-ID des Objekts.
    :param geometrie: Geometrie, deren Länge gespeichert wird.
    """
    feld_index = layer.fields().indexFromName("laenge")
    if feld_index >= 0:
        layer.changeAttributeValue(
            fid,
            feld_index,
            round(geometrie.length(), 3),
        )


def _anschlussleitungen_an_haltung_verschieben(
    anschluss_layer,
    haltnam,
    alte_haltungsgeometrie,
    neue_haltungsgeometrie
):
    """Führt Anschlussleitungen nach einer Haltungsänderung nach.

    :param anschluss_layer: Layer der Anschlussleitungen.
    :param haltnam: Name der geänderten Haltung.
    :param alte_haltungsgeometrie: Haltung vor der Änderung.
    :param neue_haltungsgeometrie: Haltung nach der Änderung.
    """
    if anschluss_layer is None:
        return

    feldnamen = set(anschluss_layer.fields().names())

    for anschluss in anschluss_layer.getFeatures():
        anschlussgeometrie = anschluss.geometry()
        enden = _linienenden(anschlussgeometrie)
        if enden is None:
            continue

        startpunkt, endpunkt = enden
        start_abstand = alte_haltungsgeometrie.distance(
            _punktgeometrie(startpunkt)
        )
        end_abstand = alte_haltungsgeometrie.distance(
            _punktgeometrie(endpunkt)
        )

        anschluss_haltnam = ""
        if "haltnam" in feldnamen:
            anschluss_haltnam = _text(anschluss["haltnam"])

        if haltnam:
            if anschluss_haltnam and anschluss_haltnam != haltnam:
                continue
            if (
                not anschluss_haltnam
                and min(start_abstand, end_abstand) > ANSCHLUSS_TOLERANZ
            ):
                continue
        elif min(start_abstand, end_abstand) > ANSCHLUSS_TOLERANZ:
            continue

        if start_abstand <= end_abstand:
            ende_index = 0
            alter_anschlusspunkt = startpunkt
        else:
            ende_index = -1
            alter_anschlusspunkt = endpunkt

        urstation = None
        if "urstation" in feldnamen:
            urstation = anschluss["urstation"]

        neuer_anschlusspunkt = _stationspunkt_nach_aenderung(
            alte_haltungsgeometrie,
            neue_haltungsgeometrie,
            alter_anschlusspunkt,
            urstation
        )
        if neuer_anschlusspunkt is None:
            continue

        neue_anschlussgeometrie = _linienende_verschieben(
            anschlussgeometrie,
            ende_index,
            neuer_anschlusspunkt
        )
        if neue_anschlussgeometrie is not None:
            anschluss_layer.changeGeometry(
                anschluss.id(),
                neue_anschlussgeometrie
            )


def _anschlussleitungen_am_schacht_verschieben(
    anschluss_layer,
    schachtnam,
    alter_punkt,
    neuer_punkt
):
    """Verschiebt Anschlussleitungsenden am bewegten Schacht.

    :param anschluss_layer: Layer der Anschlussleitungen.
    :param schachtnam: Name des verschobenen Schachts.
    :param alter_punkt: Bisherige Schachtposition.
    :param neuer_punkt: Neue Schachtposition.
    """
    if anschluss_layer is None:
        return

    feldnamen = set(anschluss_layer.fields().names())

    for anschluss in anschluss_layer.getFeatures():
        anschlussgeometrie = anschluss.geometry()
        enden = _linienenden(anschlussgeometrie)
        if enden is None:
            continue

        startpunkt, endpunkt = enden
        start_abstand = _punktabstand(startpunkt, alter_punkt)
        end_abstand = _punktabstand(endpunkt, alter_punkt)

        namensverbindung = False
        if schachtnam:
            for feldname in ("schoben", "schunten"):
                if feldname in feldnamen:
                    if _text(anschluss[feldname]) == schachtnam:
                        namensverbindung = True
                        break

        if not namensverbindung:
            if min(start_abstand, end_abstand) > SCHACHT_TOLERANZ:
                continue

        ende_index = 0 if start_abstand <= end_abstand else -1
        neue_geometrie = _linienende_verschieben(
            anschlussgeometrie,
            ende_index,
            neuer_punkt
        )
        if neue_geometrie is not None:
            anschluss_layer.changeGeometry(anschluss.id(), neue_geometrie)


def change_schacht():
    """Aktiviert oder beendet das Werkzeug zum Verschieben eines Schachts."""

    project = QgsProject.instance()

    datenquelle = datenquelle_waehlen(
        project,
        ("schaechte", "haltungen", "anschlussleitungen"),
        iface.mainWindow(),
        "QKan – Schacht verschieben",
        getattr(change_schacht, "_datenquelle", None)
        if getattr(change_schacht, "_active", False)
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
            "Es wurde keine vollständige, eindeutige QKan-Datenquelle mit "
            "den Layern 'Schächte', 'Haltungen' und 'HA-Leitungen' "
            "gefunden. Unterstützt werden SpatiaLite und PostgreSQL/PostGIS."
        )
        return

    iface.setActiveLayer(layer)

    action = getattr(iface, "action_change_schacht", None)

    if action is None:
        action = iface.actionVertexTool()

    # ------------------------------------------
    # Eigenen Umschaltzustand der Aktion verwalten
    # ------------------------------------------

    if getattr(change_schacht, "_active", False):

        iface.actionPan().trigger()

        action.setChecked(False)
        change_schacht._active = False
        change_schacht._datenquelle = None

        handler = getattr(change_schacht, "_geometry_handler", None)
        if handler is not None:
            try:
                layer.geometryChanged.disconnect(handler)
            except (TypeError, RuntimeError):
                LOGGER.debug(
                    "Geometriesignal war bereits getrennt.",
                    exc_info=True,
                )
            change_schacht._geometry_handler = None

        vertex_action = iface.actionVertexTool()
        enable_action = iface.mainWindow().findChild(QAction, "mEnableAction")
        cad_dock = iface.mainWindow().findChild(
            QgsAdvancedDigitizingDockWidget
        )

        if enable_action and enable_action.isChecked():
            enable_action.trigger()

        if cad_dock:
            cad_dock.hide()

        layer.commitChanges()

        for mitbearbeiteter_layer in getattr(
            change_schacht, "_gestartete_layer", []
        ):
            if mitbearbeiteter_layer is not layer:
                mitbearbeiteter_layer.commitChanges()
        change_schacht._gestartete_layer = []
        return

    # ------------------------------------------
    # andere Buttons deaktivieren
    # ------------------------------------------

    for name in [
        "action_create_schacht",
        "action_create_haltung",
        "action_change_haltung",
        "action_export_teilgebiet"
    ]:
        other = getattr(iface, name, None)
        if other and other is not action:
            other.setChecked(False)

    if getattr(change_schacht, "_running", False):
        return

    haltung_layer = layer_finden(project, "haltungen", datenquelle)
    anschluss_layer = layer_finden(
        project, "anschlussleitungen", datenquelle
    )
    if haltung_layer is None or anschluss_layer is None:
        QMessageBox.warning(
            iface.mainWindow(),
            "QKan",
            "Zum Verschieben werden die Layer 'Schächte', 'Haltungen' und "
            "'HA-Leitungen' aus derselben QKan-Datenquelle benötigt."
        )
        return

    vertex_action = iface.actionVertexTool()
    enable_action = iface.mainWindow().findChild(QAction, "mEnableAction")
    cad_dock = iface.mainWindow().findChild(
        QgsAdvancedDigitizingDockWidget
    )

    # ------------------------------------------
    # Bearbeitungsmodus starten
    # ------------------------------------------

    change_schacht._gestartete_layer = []

    if not layer.isEditable():
        if not layer.startEditing():
            QMessageBox.warning(
                iface.mainWindow(),
                "QKan",
                "Bearbeitungsmodus konnte nicht gestartet werden."
            )
            return
        change_schacht._gestartete_layer.append(layer)

    for mitbearbeiteter_layer in [haltung_layer, anschluss_layer]:
        if (
            mitbearbeiteter_layer is not None
            and not mitbearbeiteter_layer.isEditable()
            and mitbearbeiteter_layer.startEditing()
        ):
            change_schacht._gestartete_layer.append(mitbearbeiteter_layer)

    geometrie_speicher = {
        feature.id(): QgsGeometry(feature.geometry())
        for feature in layer.getFeatures()
        if feature.geometry() is not None
    }
    change_schacht._geometrie_speicher = geometrie_speicher
    change_schacht._syncing = False

    def geometrie_geaendert(fid, neue_geometrie):
        """Verarbeitet eine geänderte Schachtgeometrie.

        :param fid: Feature-ID des geänderten Schachts.
        :param neue_geometrie: Aktuelle Geometrie des Schachts.
        """
        if (
            getattr(change_schacht, "_syncing", False)
            or not action.isChecked()
        ):
            return

        alte_geometrie = geometrie_speicher.get(fid)
        geometrie_speicher[fid] = QgsGeometry(neue_geometrie)

        if (
            alte_geometrie is None
            or alte_geometrie.isEmpty()
            or neue_geometrie is None
            or neue_geometrie.isEmpty()
            or haltung_layer is None
        ):
            return

        alter_punkt = QgsPointXY(alte_geometrie.asPoint())
        neuer_punkt = QgsPointXY(neue_geometrie.asPoint())
        if _punktabstand(alter_punkt, neuer_punkt) <= 0.000001:
            return

        schacht = layer.getFeature(fid)
        schacht_feldnamen = set(layer.fields().names())
        schachtnam = (
            _text(schacht["schnam"])
            if "schnam" in schacht_feldnamen
            else ""
        )

        change_schacht._syncing = True
        try:
            haltung_feldnamen = set(haltung_layer.fields().names())

            for haltung in haltung_layer.getFeatures():
                namensverbindung = False
                if schachtnam:
                    for feldname in ("schoben", "schunten"):
                        if feldname in haltung_feldnamen:
                            if _text(haltung[feldname]) == schachtnam:
                                namensverbindung = True
                                break

                alte_haltungsgeometrie = haltung.geometry()
                enden = _linienenden(alte_haltungsgeometrie)
                if enden is None:
                    continue

                startpunkt, endpunkt = enden
                start_abstand = _punktabstand(startpunkt, alter_punkt)
                end_abstand = _punktabstand(endpunkt, alter_punkt)

                if (
                    not namensverbindung
                    and min(start_abstand, end_abstand) > SCHACHT_TOLERANZ
                ):
                    continue

                ende_index = 0 if start_abstand <= end_abstand else -1
                neue_haltungsgeometrie = _linienende_verschieben(
                    alte_haltungsgeometrie,
                    ende_index,
                    neuer_punkt
                )
                if neue_haltungsgeometrie is None:
                    continue

                haltung_layer.changeGeometry(
                    haltung.id(),
                    neue_haltungsgeometrie
                )
                _laenge_aktualisieren(
                    haltung_layer,
                    haltung.id(),
                    neue_haltungsgeometrie
                )

                haltnam = ""
                if "haltnam" in haltung_feldnamen:
                    haltnam = _text(haltung["haltnam"])

                _anschlussleitungen_an_haltung_verschieben(
                    anschluss_layer,
                    haltnam,
                    alte_haltungsgeometrie,
                    neue_haltungsgeometrie
                )

            _anschlussleitungen_am_schacht_verschieben(
                anschluss_layer,
                schachtnam,
                alter_punkt,
                neuer_punkt
            )
        finally:
            geometrie_speicher[fid] = QgsGeometry(neue_geometrie)
            change_schacht._syncing = False

    alter_handler = getattr(change_schacht, "_geometry_handler", None)
    if alter_handler is not None:
        try:
            layer.geometryChanged.disconnect(alter_handler)
        except (TypeError, RuntimeError):
            LOGGER.debug(
                "Geometriesignal war bereits getrennt.",
                exc_info=True,
            )

    change_schacht._geometry_handler = geometrie_geaendert
    layer.geometryChanged.connect(geometrie_geaendert)

    # ------------------------------------------
    # Vertex Tool aktivieren
    # ------------------------------------------

    if not vertex_action.isChecked():
        vertex_action.trigger()

    action.setChecked(True)
    change_schacht._active = True
    change_schacht._datenquelle = datenquelle

    # ------------------------------------------
    # CAD Dock anzeigen
    # ------------------------------------------

    if cad_dock:
        cad_dock.show()

    # ------------------------------------------
    # CAD Modus aktivieren
    # ------------------------------------------

    if enable_action and not enable_action.isChecked():
        enable_action.trigger()
