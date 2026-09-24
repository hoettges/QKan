"""Verschiebt Haltungen und führt verbundene Netzgeometrien nach."""

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


def _naechster_endpunkt_index(geometrie, punkt):
    """Bestimmt das zum Punkt nächstgelegene Linienende.

    :param geometrie: Zu prüfende Liniengeometrie.
    :param punkt: Vergleichspunkt.
    :return: ``0`` für den Start, ``-1`` für das Ende oder ``None``.
    """
    enden = _linienenden(geometrie)
    if enden is None:
        return None

    startpunkt, endpunkt = enden
    if _punktabstand(startpunkt, punkt) <= _punktabstand(endpunkt, punkt):
        return 0
    return -1


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


def _schacht_fuer_haltungsende(
    schacht_layer,
    haltung,
    haltung_feldnamen,
    alter_punkt
):
    """Ermittelt den Schacht an einem Haltungsende.

    :param schacht_layer: Layer der Schächte.
    :param haltung: Betroffene Haltung.
    :param haltung_feldnamen: Feldnamen der Haltung.
    :param alter_punkt: Bisherige Position des Haltungsendes.
    :return: Gefundener Schacht und sein Name; andernfalls ``(None, "")``.
    """
    if schacht_layer is None:
        return None, ""

    schachtnamen = set()
    for feldname in ("schoben", "schunten"):
        if feldname in haltung_feldnamen:
            name = _text(haltung[feldname])
            if name:
                schachtnamen.add(name)

    schacht_feldnamen = set(schacht_layer.fields().names())
    bester_benannter_schacht = None
    bester_benannter_name = ""
    kleinster_benannter_abstand = None
    naechster_schacht = None
    naechster_name = ""
    kleinster_abstand = None

    for schacht in schacht_layer.getFeatures():
        geometrie = schacht.geometry()
        if geometrie is None or geometrie.isEmpty():
            continue

        punkt = QgsPointXY(geometrie.asPoint())
        abstand = _punktabstand(punkt, alter_punkt)
        name = (
            _text(schacht["schnam"])
            if "schnam" in schacht_feldnamen
            else ""
        )

        if name in schachtnamen:
            if (
                kleinster_benannter_abstand is None
                or abstand < kleinster_benannter_abstand
            ):
                kleinster_benannter_abstand = abstand
                bester_benannter_schacht = schacht
                bester_benannter_name = name

        if kleinster_abstand is None or abstand < kleinster_abstand:
            kleinster_abstand = abstand
            naechster_schacht = schacht
            naechster_name = name

    if bester_benannter_schacht is not None:
        return bester_benannter_schacht, bester_benannter_name

    if kleinster_abstand is not None and kleinster_abstand <= SCHACHT_TOLERANZ:
        return naechster_schacht, naechster_name

    return None, ""


def _haltung_an_schacht_verschieben(
    haltung_layer,
    anschluss_layer,
    aktuelle_haltung_id,
    schachtnam,
    alter_punkt,
    neuer_punkt,
    geometrie_speicher
):
    """Führt weitere Haltungen am verschobenen Schacht nach.

    :param haltung_layer: Layer der Haltungen.
    :param anschluss_layer: Layer der Anschlussleitungen.
    :param aktuelle_haltung_id: Feature-ID der direkt bearbeiteten Haltung.
    :param schachtnam: Name des gemeinsamen Schachts.
    :param alter_punkt: Bisherige Schachtposition.
    :param neuer_punkt: Neue Schachtposition.
    :param geometrie_speicher: Zwischenspeicher der ursprünglichen Geometrien.
    """
    feldnamen = set(haltung_layer.fields().names())

    for haltung in haltung_layer.getFeatures():
        if haltung.id() == aktuelle_haltung_id:
            continue

        namensverbindung = False
        if schachtnam:
            for feldname in ("schoben", "schunten"):
                if feldname in feldnamen:
                    if _text(haltung[feldname]) == schachtnam:
                        namensverbindung = True
                        break

        alte_geometrie = haltung.geometry()
        enden = _linienenden(alte_geometrie)
        if enden is None:
            continue

        startpunkt, endpunkt = enden
        kleinster_endabstand = min(
            _punktabstand(startpunkt, alter_punkt),
            _punktabstand(endpunkt, alter_punkt)
        )

        if not namensverbindung and kleinster_endabstand > SCHACHT_TOLERANZ:
            continue

        ende_index = _naechster_endpunkt_index(alte_geometrie, alter_punkt)
        neue_geometrie = _linienende_verschieben(
            alte_geometrie,
            ende_index,
            neuer_punkt
        )
        if neue_geometrie is None:
            continue

        haltung_layer.changeGeometry(haltung.id(), neue_geometrie)
        geometrie_speicher[haltung.id()] = QgsGeometry(neue_geometrie)
        _laenge_aktualisieren(haltung_layer, haltung.id(), neue_geometrie)

        haltnam = ""
        if "haltnam" in feldnamen:
            haltnam = _text(haltung["haltnam"])

        _anschlussleitungen_an_haltung_verschieben(
            anschluss_layer,
            haltnam,
            alte_geometrie,
            neue_geometrie
        )


def change_haltung():
    """Aktiviert oder beendet das Werkzeug zum Verschieben einer Haltung."""

    project = QgsProject.instance()

    datenquelle = datenquelle_waehlen(
        project,
        ("haltungen", "schaechte", "anschlussleitungen"),
        iface.mainWindow(),
        "QKan – Haltung verschieben",
        getattr(change_haltung, "_datenquelle", None)
        if getattr(change_haltung, "_active", False)
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
            "den Layern 'Haltungen', 'Schächte' und 'HA-Leitungen' "
            "gefunden. Unterstützt werden SpatiaLite und PostgreSQL/PostGIS."
        )
        return

    iface.setActiveLayer(layer)

    action = getattr(iface, "action_change_haltung", None)

    if action is None:
        action = iface.actionVertexTool()

    # ------------------------------------------
    # Eigenen Umschaltzustand der Aktion verwalten
    # ------------------------------------------

    if getattr(change_haltung, "_active", False):

        iface.actionPan().trigger()

        action.setChecked(False)
        change_haltung._active = False
        change_haltung._datenquelle = None

        handler = getattr(change_haltung, "_geometry_handler", None)
        if handler is not None:
            try:
                layer.geometryChanged.disconnect(handler)
            except (TypeError, RuntimeError):
                LOGGER.debug(
                    "Geometriesignal war bereits getrennt.",
                    exc_info=True,
                )
            change_haltung._geometry_handler = None

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
            change_haltung, "_gestartete_layer", []
        ):
            if mitbearbeiteter_layer is not layer:
                mitbearbeiteter_layer.commitChanges()
        change_haltung._gestartete_layer = []
        return

    # ------------------------------------------
    # andere Buttons deaktivieren
    # ------------------------------------------

    for name in [
        "action_create_schacht",
        "action_create_haltung",
        "action_change_schacht",
        "action_export_teilgebiet"
    ]:
        other = getattr(iface, name, None)
        if other and other is not action:
            other.setChecked(False)

    if getattr(change_haltung, "_running", False):
        return

    schacht_layer = layer_finden(project, "schaechte", datenquelle)
    anschluss_layer = layer_finden(
        project, "anschlussleitungen", datenquelle
    )
    if schacht_layer is None or anschluss_layer is None:
        QMessageBox.warning(
            iface.mainWindow(),
            "QKan",
            "Zum Verschieben werden die Layer 'Haltungen', 'Schächte' und "
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

    change_haltung._gestartete_layer = []

    if not layer.isEditable():
        if not layer.startEditing():
            QMessageBox.warning(
                iface.mainWindow(),
                "QKan",
                "Bearbeitungsmodus konnte nicht gestartet werden."
            )
            return
        change_haltung._gestartete_layer.append(layer)

    for mitbearbeiteter_layer in [schacht_layer, anschluss_layer]:
        if (
            mitbearbeiteter_layer is not None
            and not mitbearbeiteter_layer.isEditable()
            and mitbearbeiteter_layer.startEditing()
        ):
            change_haltung._gestartete_layer.append(mitbearbeiteter_layer)

    geometrie_speicher = {
        feature.id(): QgsGeometry(feature.geometry())
        for feature in layer.getFeatures()
        if feature.geometry() is not None
    }
    change_haltung._geometrie_speicher = geometrie_speicher
    change_haltung._syncing = False

    def geometrie_geaendert(fid, neue_geometrie):
        """Verarbeitet eine geänderte Haltungsgeometrie.

        :param fid: Feature-ID der geänderten Haltung.
        :param neue_geometrie: Aktuelle Geometrie der Haltung.
        """
        if (
            getattr(change_haltung, "_syncing", False)
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
        ):
            return

        haltung = layer.getFeature(fid)
        feldnamen = set(layer.fields().names())
        haltnam = _text(haltung["haltnam"]) if "haltnam" in feldnamen else ""

        alte_enden = _linienenden(alte_geometrie)
        neue_enden = _linienenden(neue_geometrie)
        if alte_enden is None or neue_enden is None:
            return

        change_haltung._syncing = True
        try:
            _laenge_aktualisieren(layer, fid, neue_geometrie)

            _anschlussleitungen_an_haltung_verschieben(
                anschluss_layer,
                haltnam,
                alte_geometrie,
                neue_geometrie
            )

            for ende_index in (0, -1):
                alter_punkt = alte_enden[0 if ende_index == 0 else 1]
                neuer_punkt = neue_enden[0 if ende_index == 0 else 1]

                if _punktabstand(alter_punkt, neuer_punkt) <= 0.000001:
                    continue

                schacht, schachtnam = _schacht_fuer_haltungsende(
                    schacht_layer,
                    haltung,
                    feldnamen,
                    alter_punkt
                )

                if schacht is not None:
                    schacht_layer.changeGeometry(
                        schacht.id(),
                        QgsGeometry.fromPointXY(QgsPointXY(neuer_punkt))
                    )

                _haltung_an_schacht_verschieben(
                    layer,
                    anschluss_layer,
                    fid,
                    schachtnam,
                    alter_punkt,
                    neuer_punkt,
                    geometrie_speicher
                )

                _anschlussleitungen_am_schacht_verschieben(
                    anschluss_layer,
                    schachtnam,
                    alter_punkt,
                    neuer_punkt
                )
        finally:
            geometrie_speicher[fid] = QgsGeometry(neue_geometrie)
            change_haltung._syncing = False

    alter_handler = getattr(change_haltung, "_geometry_handler", None)
    if alter_handler is not None:
        try:
            layer.geometryChanged.disconnect(alter_handler)
        except (TypeError, RuntimeError):
            LOGGER.debug(
                "Geometriesignal war bereits getrennt.",
                exc_info=True,
            )

    change_haltung._geometry_handler = geometrie_geaendert
    layer.geometryChanged.connect(geometrie_geaendert)

    # ------------------------------------------
    # Vertex Tool aktivieren
    # ------------------------------------------

    if not vertex_action.isChecked():
        vertex_action.trigger()

    action.setChecked(True)
    change_haltung._active = True
    change_haltung._datenquelle = datenquelle

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
