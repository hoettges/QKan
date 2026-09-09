"""Ermittelt und öffnet die QKan-Datenquelle des Inspektionsmoduls."""

from __future__ import annotations

import math
import logging
import os
import re
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import yaml
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.core import (
    QgsDataSourceUri,
    QgsMapLayerType,
    QgsProject,
    QgsProviderRegistry,
    QgsSQLStatement,
    QgsVectorLayer,
)
from qgis.utils import pluginDirectory

from qkan.database.dbfunc import DBConnection


LOGGER = logging.getLogger(__name__)


LAYER_NAMEN = {
    "haltungen": "Haltungen",
    "schaechte": "Schächte",
    "anschlussleitungen": "HA-Leitungen",
    "anschlussschaechte": "HA-Schächte",
    "haltungen_untersucht": "Zustand_Haltungen_gesamt",
    "untersuchdat_haltung": "Einzelschäden_Haltungen",
    "schaechte_untersucht": "Zustand_Schächte_gesamt",
    "untersuchdat_schacht": "Einzelschäden_Schächte",
    "anschlussleitungen_untersucht": "Zustand_HA-Leitungen_gesamt",
    "untersuchdat_anschlussleitung": "Einzelschäden_HA-Leitungen",
}


@dataclass(frozen=True)
class Datenquelle:
    """Eindeutige SpatiaLite- oder PostgreSQL-QKan-Datenquelle."""

    schluessel: Tuple[str, ...]
    provider: str = field(compare=False)
    bezeichnung: str = field(compare=False)
    verbindungs_uri: str = field(compare=False, repr=False)
    schema: str = field(default="", compare=False)
    sqlite_pfad: str = field(default="", compare=False)


def _bereinigen(wert: object) -> str:
    """Entfernt äußere Anführungszeichen und Leerraum."""
    return str(wert or "").strip().strip('"')


def layerdaten(layer: object) -> Optional[Tuple[str, Datenquelle]]:
    """Liest Tabelle und Identität einer unterstützten QGIS-Datenquelle."""
    if layer is None:
        return None

    try:
        if layer.type() != QgsMapLayerType.VectorLayer:
            return None
        provider = layer.providerType()
        if provider not in {"spatialite", "postgres"}:
            return None

        uri = QgsDataSourceUri(layer.source())
        tabelle = _bereinigen(uri.table())
        if not tabelle:
            return None

        if provider == "spatialite":
            datenbank = uri.database() or ""
            if not datenbank:
                return None
            pfad = os.path.normcase(
                os.path.abspath(os.path.normpath(datenbank))
            )
            datenquelle = Datenquelle(
                schluessel=("spatialite", pfad),
                provider=provider,
                bezeichnung=f"SpatiaLite: {pfad}",
                verbindungs_uri=pfad,
                sqlite_pfad=pfad,
            )
            return tabelle, datenquelle

        schema = _bereinigen(uri.schema())
        datenbank = _bereinigen(uri.database())
        if not schema or not datenbank:
            return None

        verbindung = uri.connectionInfo(False)
        verbindungs_uri = uri.connectionInfo(True)
        if not verbindung or not verbindungs_uri:
            return None

        dienst = _bereinigen(uri.service())
        if dienst:
            ort = f"Dienst {dienst}"
        else:
            host = _bereinigen(uri.host()) or "localhost"
            port = _bereinigen(uri.port())
            ort = f"{host}:{port}" if port else host

        benutzer = _bereinigen(uri.username())
        benutzer_text = f", Benutzer {benutzer}" if benutzer else ""
        datenquelle = Datenquelle(
            schluessel=("postgres", verbindung, schema),
            provider=provider,
            bezeichnung=(
                f"PostgreSQL: {ort}, Datenbank {datenbank}, "
                f"Schema {schema}{benutzer_text}"
            ),
            verbindungs_uri=verbindungs_uri,
            schema=schema,
        )
        return tabelle, datenquelle
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return None


def _passende_layer(
    projekt: QgsProject,
    tabellennamen: Iterable[str],
) -> Dict[Datenquelle, Dict[str, List[QgsVectorLayer]]]:
    """Gruppiert exakt benannte QKan-Layer nach ihrer Datenquelle."""
    erwartete_tabellen = set(tabellennamen)
    gruppen: Dict[Datenquelle, Dict[str, List[QgsVectorLayer]]] = {}

    for layer in projekt.mapLayers().values():
        daten = layerdaten(layer)
        if daten is None:
            continue

        tabelle, datenquelle = daten
        if tabelle not in erwartete_tabellen:
            continue
        if layer.name() != LAYER_NAMEN.get(tabelle):
            continue

        gruppen.setdefault(datenquelle, {}).setdefault(tabelle, []).append(
            layer
        )

    return gruppen


def datenquelle_waehlen(
    projekt: QgsProject,
    erforderliche_tabellen: Iterable[str],
    parent: object,
    titel: str,
    bevorzugte_datenquelle: Optional[Datenquelle] = None,
) -> Optional[Datenquelle]:
    """Wählt eine vollständige, eindeutige QKan-Datenquelle aus.

    Bei mehreren vollständigen Quellen entscheidet der Benutzer ausdrücklich.
    Quellen mit doppelten oder fehlenden Pflichtlayern werden nicht angeboten.
    """
    tabellen = tuple(dict.fromkeys(erforderliche_tabellen))
    gruppen = _passende_layer(projekt, tabellen)
    kandidaten = [
        datenquelle
        for datenquelle, layer_nach_tabelle in gruppen.items()
        if all(
            len(layer_nach_tabelle.get(tabelle, [])) == 1
            for tabelle in tabellen
        )
    ]
    kandidaten.sort(key=lambda quelle: quelle.bezeichnung.casefold())

    if not kandidaten:
        return None
    if bevorzugte_datenquelle in kandidaten:
        return bevorzugte_datenquelle
    if len(kandidaten) == 1:
        return kandidaten[0]

    beschriftungen = [quelle.bezeichnung for quelle in kandidaten]
    auswahl, bestaetigt = QInputDialog.getItem(
        parent,
        titel,
        "Mehrere vollständige QKan-Datenquellen sind geladen.\n"
        "Bitte die zu bearbeitende Datenquelle auswählen:",
        beschriftungen,
        0,
        False,
    )
    if not bestaetigt:
        return None

    return kandidaten[beschriftungen.index(auswahl)]


def layer_finden(
    projekt: QgsProject,
    tabellenname: str,
    datenquelle: Datenquelle,
) -> Optional[QgsVectorLayer]:
    """Findet genau einen QKan-Layer in der gewählten Datenquelle."""
    treffer = _passende_layer(projekt, (tabellenname,)).get(
        datenquelle, {}
    ).get(tabellenname, [])
    return treffer[0] if len(treffer) == 1 else None


def datenquellen_finden(
    projekt: QgsProject,
    tabellennamen: Iterable[str],
) -> List[Datenquelle]:
    """Liefert Quellen mit mindestens einem exakt passenden QKan-Layer."""
    return sorted(
        _passende_layer(projekt, tabellennamen),
        key=lambda quelle: quelle.bezeichnung.casefold(),
    )


class PostgresAbfragen:
    """Kleine DBConnection-kompatible Leseschicht für PostgreSQL."""

    def __init__(self, datenquelle: Datenquelle) -> None:
        if datenquelle.provider != "postgres":
            raise ValueError(
                "PostgresAbfragen benötigt eine PostgreSQL-Quelle."
            )

        self._datenquelle = datenquelle
        self._verbindung = None
        self.connected = False
        self.cursl = SimpleNamespace(description=())
        self._zeilen: List[Tuple[object, ...]] = []
        self._sqls: Dict[str, str] = {}

        try:
            metadaten = QgsProviderRegistry.instance().providerMetadata(
                "postgres"
            )
            if metadaten is None:
                return
            self._verbindung = metadaten.createConnection(
                datenquelle.verbindungs_uri,
                {},
            )
            self.connected = self._verbindung is not None
        except Exception:
            LOGGER.warning(
                "Die PostgreSQL-Verbindung konnte nicht geöffnet werden.",
                exc_info=True,
            )

    def __enter__(self) -> "PostgresAbfragen":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._verbindung = None
        self.connected = False

    def loadmodule(self, module: str) -> None:
        """Lädt die PostgreSQL-Abfragen des angegebenen QKan-Moduls."""
        sqlpfad = os.path.join(
            pluginDirectory("qkan"),
            module,
            "postgres.yml",
        )
        with open(sqlpfad, encoding="utf-8") as sql_datei:
            sqls = yaml.safe_load(sql_datei.read()) or {}
        if not isinstance(sqls, dict):
            raise RuntimeError(
                f"Die PostgreSQL-Abfragedatei '{sqlpfad}' ist ungültig."
            )
        self._sqls.update(sqls)

    @staticmethod
    def _sqlwert(wert: object) -> str:
        """Erzeugt ein sicher maskiertes SQL-Literal."""
        if wert is None:
            return "NULL"
        if isinstance(wert, bool):
            return "TRUE" if wert else "FALSE"
        if isinstance(wert, int):
            return str(wert)
        if isinstance(wert, float):
            if not math.isfinite(wert):
                raise ValueError("Nicht endliche SQL-Zahl ist unzulässig.")
            return repr(wert)
        return QgsSQLStatement.quotedString(str(wert))

    def _parameter_einsetzen(
        self,
        sqltext: str,
        parameter: Mapping[str, object],
    ) -> str:
        """Ersetzt ausschließlich benannte Platzhalter durch Literale."""
        for name in sorted(parameter, key=len, reverse=True):
            muster = re.compile(rf"(?<!:):{re.escape(str(name))}\b")
            sqltext, anzahl = muster.subn(
                self._sqlwert(parameter[name]),
                sqltext,
            )
            if anzahl == 0:
                raise ValueError(f"SQL-Platzhalter ':{name}' fehlt.")
        if re.search(r"(?<!:):[A-Za-z_]\w*", sqltext):
            raise ValueError("Nicht gebundener SQL-Platzhalter gefunden.")
        return sqltext

    def sqlyml(
        self,
        sqlnam: str,
        stmt_category: str = "allgemein",
        parameters: object = (),
        many: bool = False,
        mute_logger: bool = False,
        ignore: bool = False,
        replacefun: object = None,
    ) -> bool:
        """Führt eine benannte PostgreSQL-Abfrage lesend aus."""
        del stmt_category, mute_logger
        if many:
            raise ValueError("Mehrfachausführung wird hier nicht unterstützt.")

        try:
            sqltext = self._sqls[sqlnam]
            if replacefun is not None:
                sqltext = replacefun(sqltext)
            schema = QgsSQLStatement.quotedIdentifier(
                self._datenquelle.schema
            )
            sqltext = sqltext.replace("{schema}", schema)

            if isinstance(parameters, Mapping):
                sqltext = self._parameter_einsetzen(sqltext, parameters)
            elif parameters not in ((), [], None):
                raise ValueError(
                    "PostgreSQL-Abfragen benötigen benannte Parameter."
                )

            ergebnis = self._verbindung.execSql(sqltext)
            self.cursl.description = tuple(
                (str(spalte),) for spalte in ergebnis.columns()
            )
            self._zeilen = [
                tuple(zeile) for zeile in ergebnis.rows()
            ]
            return True
        except Exception:
            if ignore:
                return False
            raise

    def fetchall(self) -> List[Tuple[object, ...]]:
        """Gibt alle Zeilen der zuletzt ausgeführten Abfrage zurück."""
        return list(self._zeilen)

    def fetchone(self) -> Optional[Tuple[object, ...]]:
        """Gibt die erste Zeile der zuletzt ausgeführten Abfrage zurück."""
        return self._zeilen[0] if self._zeilen else None


def datenbank_oeffnen(datenquelle: Datenquelle) -> object:
    """Erzeugt die passende Leseverbindung für Import oder Export."""
    if datenquelle.provider == "spatialite":
        return DBConnection(dbname=datenquelle.sqlite_pfad)
    if datenquelle.provider == "postgres":
        return PostgresAbfragen(datenquelle)
    raise ValueError(f"Nicht unterstützter Provider: {datenquelle.provider}")
