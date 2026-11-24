# planauskunft/berichte/daten.py
"""
Datenzugriff für Berichte (PostgreSQL über psycopg2 oder SpatiaLite über sqlite3).

Gelesen werden die QKan-Tabellen:
  haltungen / anschlussleitungen          Stammdaten
  untersuchhal / untersuchleit            Kopfdaten der Befahrung (falls vorhanden)
  haltungen_untersucht / anschlussleitungen_untersucht   Gesamtbewertung (max_ZD/ZB/ZS, falls vorhanden)
  untersuchdat_haltung / untersuchdat_anschlussleitung    Einzelbefunde

Es wird bewusst mit SELECT * gearbeitet, damit unterschiedliche Spaltenstände
(Strakat-Import, M150-Import, QKan-Versionen) funktionieren.
"""

import os
import datetime
from dataclasses import dataclass, field
from typing import Any, Optional

OBJEKTARTEN = {
    "Haltung": {
        "stamm_tabelle": "haltungen", "stamm_spalte": "haltnam",
        "kopf_tabelle": "untersuchhal", "kopf_spalte": "haltnam",
        "bewertung_tabelle": "haltungen_untersucht", "bewertung_spalte": "haltnam",
        "befund_tabelle": "untersuchdat_haltung", "befund_spalte": "untersuchhal",
        "layer_feld": "haltnam", "station_spalte": "station",
        "layer_namen": ["haltungen"], "titel": "Haltungsbericht",
    },
    "Anschlussleitung": {
        "stamm_tabelle": "anschlussleitungen", "stamm_spalte": "leitnam",
        "kopf_tabelle": "untersuchleit", "kopf_spalte": "leitnam",
        "bewertung_tabelle": "anschlussleitungen_untersucht", "bewertung_spalte": "leitnam",
        "befund_tabelle": "untersuchdat_anschlussleitung", "befund_spalte": "untersuchleit",
        "layer_feld": "leitnam", "station_spalte": "station",
        "layer_namen": ["anschlussleitungen", "gal"], "titel": "Bericht Anschlussleitung",
    },
    "Schacht": {
        "stamm_tabelle": "schaechte", "stamm_spalte": "schnam",
        "kopf_tabelle": "untersuchsch", "kopf_spalte": "schnam",
        "bewertung_tabelle": "schaechte_untersucht", "bewertung_spalte": "schnam",
        "befund_tabelle": "untersuchdat_schacht", "befund_spalte": "untersuchsch",
        "layer_feld": "schnam", "station_spalte": "vertikale_lage",
        "layer_namen": ["schächte", "schaechte"], "titel": "Schachtbericht",
    },
}

# Farben der Zustandsklassen (wie im Datenbankviewer)
ZK_FARBEN = {0: "#d62728", 1: "#e6b800", 2: "#1f77b4", 3: "#7fc97f", 4: "#2ca02c", 5: "#d9d9d9"}
ZK_TEXT = {0: "ZK 0 – sofortiger Handlungsbedarf", 1: "ZK 1 – kurzfristiger Handlungsbedarf",
           2: "ZK 2 – mittelfristiger Handlungsbedarf", 3: "ZK 3 – langfristiger Handlungsbedarf",
           4: "ZK 4 – kein Handlungsbedarf", 5: "ZK 5 – schadensfrei"}


def zahl(wert, standard=None):
    if wert is None:
        return standard
    try:
        return float(str(wert).strip().replace(",", "."))
    except (TypeError, ValueError):
        return standard


def text(wert):
    if wert is None:
        return ""
    if isinstance(wert, (datetime.date, datetime.datetime)):
        return wert.strftime("%d.%m.%Y")
    s = str(wert).strip()
    if s.lower() in ("none", "null", "nan"):
        return ""
    return s


def datum_text(wert):
    """'2024-05-17' / date -> '17.05.2024'."""
    if isinstance(wert, (datetime.date, datetime.datetime)):
        return wert.strftime("%d.%m.%Y")
    s = text(wert)
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(s[:19] if "%H" in fmt else s[:10], fmt).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return s


def zk(wert):
    z = zahl(wert)
    if z is None:
        return None
    z = int(round(z))
    return z if 0 <= z <= 5 else None


@dataclass
class Befund:
    station: Optional[float]
    kuerzel: str
    langtext: str
    werte: dict = field(default_factory=dict)

    @property
    def zd(self):
        return zk(self.werte.get("zd"))

    @property
    def zs(self):
        return zk(self.werte.get("zs"))

    @property
    def zb(self):
        return zk(self.werte.get("zb"))

    @property
    def klasse(self):
        """Maßgebende (kleinste) Zustandsklasse des Befundes."""
        k = [z for z in (self.zd, self.zs, self.zb) if z is not None]
        return min(k) if k else None

    def wert(self, name):
        return text(self.werte.get(name))


@dataclass
class Objektdaten:
    art: str
    name: str
    befahrung: Any = None                 # Wert von untersuchtag (wie in der DB)
    stamm: dict = field(default_factory=dict)
    kopf: dict = field(default_factory=dict)
    bewertung: dict = field(default_factory=dict)
    befunde: list = field(default_factory=list)
    befahrungen: list = field(default_factory=list)
    zusatz: dict = field(default_factory=dict)      # z.B. "rohre" am Schacht

    def s(self, *namen):
        """Erster gefüllter Wert aus Stammdaten / Kopfdaten / Bewertung."""
        for quelle in (self.stamm, self.kopf, self.bewertung):
            for n in namen:
                v = text(quelle.get(n.lower()))
                if v:
                    return v
        return ""

    @property
    def inspektionsrichtung(self):
        """1 = in Fließrichtung, 0 = gegen Fließrichtung (auch O/U)."""
        roh = self.s("untersuchrichtung", "inspektionsrichtung")
        if not roh:
            return ""
        z = zahl(roh)
        if z is not None:
            return {1: "in Fließrichtung", 0: "gegen Fließrichtung"}.get(int(round(z)), roh)
        return {"O": "in Fließrichtung", "U": "gegen Fließrichtung"}.get(roh.strip().upper(), roh)

    @property
    def gegen_fliessrichtung(self):
        """True, wenn gegen die Fließrichtung inspiziert wurde (Code 0 bzw. U)."""
        if self.art == "Schacht":
            return False
        roh = self.s("untersuchrichtung", "inspektionsrichtung").strip().upper()
        z = zahl(roh)
        if z is not None:
            return int(round(z)) == 0
        return roh == "U"

    @property
    def ist_schacht(self):
        return self.art == "Schacht"

    @property
    def tiefe(self):
        """Schachttiefe Deckel – Sohle (m) oder None."""
        d, so = zahl(self.s("deckelhoehe")), zahl(self.s("sohlhoehe"))
        if d is not None and so is not None and d > so:
            return d - so
        return zahl(self.s("tiefe", "schachttiefe"))

    @property
    def laenge(self):
        if self.ist_schacht:
            t = self.tiefe
            tiefen = [b.station for b in self.befunde if b.station is not None]
            return max([t or 0.0] + tiefen + [1.0])
        l = zahl(self.s("laenge"))
        stationen = [b.station for b in self.befunde if b.station is not None]
        max_st = max(stationen) if stationen else 0.0
        if not l or l <= 0:
            return max(max_st, 1.0)
        # wie im Datenbankviewer: weicht die Inspektion > 2 m ab, gilt die Inspektionslänge
        if max_st > 0 and abs(l - max_st) > 2.0:
            return max_st
        return l

    @property
    def dimension(self):
        if self.ist_schacht:
            from .schachtgrafik import durchmesser_text
            return durchmesser_text(self)
        b, h = zahl(self.s("breite")), zahl(self.s("hoehe"))
        if b and h and abs(b - h) > 0.5:
            return f"{b:.0f}/{h:.0f}"
        if b or h:
            return f"DN {int(round(b or h))}"
        return self.s("dimension", "dn")

    @property
    def gefaelle(self):
        so, su, l = zahl(self.s("sohleoben")), zahl(self.s("sohleunten")), zahl(self.s("laenge"))
        if so is not None and su is not None and l:
            return f"{(so - su) / l * 1000:.1f} ‰"
        g = self.s("gefaelle")
        return f"{g} ‰" if g else ""

    def zustandsklassen(self):
        """Gespeicherte Gesamtbewertung der Befahrung wie im TV-Tool."""
        werte = [zk(self.bewertung.get(key)) for key in ("max_zd", "max_zs", "max_zb")]
        gueltig = [wert for wert in werte if wert is not None]
        return (*werte, min(gueltig) if gueltig else None)


# ======================================================================
# Datenquelle
# ======================================================================

class Datenquelle:
    """Dünne Schicht über einer DB-API-Verbindung (psycopg2 oder sqlite3)."""

    def __init__(self, conn, art):
        self.conn = conn
        self.art = art                     # "postgres" | "spatialite"
        self.ph = "%s" if art == "postgres" else "?"
        self._tabellen = None
    def schliessen(self):
        try:
            self.conn.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _abfrage(self, sql, parameter=()):
        cur = self.conn.cursor()
        try:
            cur.execute(sql, parameter)
            namen = [d[0].lower() for d in cur.description]
            zeilen = []
            for r in cur.fetchall():
                if hasattr(r, "keys"):
                    zeilen.append({k.lower(): r[k] for k in r.keys()})
                else:
                    zeilen.append(dict(zip(namen, r)))
            return zeilen
        except Exception:
            if self.art == "postgres":
                try:
                    self.conn.rollback()
                except Exception:
                    pass
            raise
        finally:
            cur.close()

    def tabellen(self):
        if self._tabellen is None:
            if self.art == "postgres":
                z = self._abfrage("SELECT table_name AS n FROM information_schema.tables "
                                  "WHERE table_schema = current_schema() "
                                  "UNION SELECT table_name FROM information_schema.views "
                                  "WHERE table_schema = current_schema()")
            else:
                z = self._abfrage("SELECT name AS n FROM sqlite_master WHERE type IN ('table','view')")
            self._tabellen = {str(r["n"]).lower() for r in z}
        return self._tabellen

    def _hat(self, tabelle):
        return tabelle.lower() in self.tabellen()

    @staticmethod
    def _q(name):
        return '"' + str(name).replace('"', '""') + '"'

    # ------------------------------------------------------------------
    def befahrungen(self, art, name):
        """Befahrungsdaten (untersuchtag) eines Objekts, neueste zuerst."""
        cfg = OBJEKTARTEN[art]
        if not self._hat(cfg["befund_tabelle"]):
            return []
        z = self._abfrage(
            f"SELECT DISTINCT untersuchtag FROM {self._q(cfg['befund_tabelle'])} "
            f"WHERE {self._q(cfg['befund_spalte'])} = {self.ph} AND untersuchtag IS NOT NULL "
            f"ORDER BY untersuchtag DESC", (name,))
        return [r["untersuchtag"] for r in z]

    def lade(self, art, name, befahrung=None):
        """Alle Daten eines Objekts für eine Befahrung (None = neueste)."""
        cfg = OBJEKTARTEN[art]
        od = Objektdaten(art=art, name=name)
        od.befahrungen = self.befahrungen(art, name)
        od.befahrung = befahrung if befahrung not in (None, "") else (od.befahrungen[0] if od.befahrungen else None)

        if self._hat(cfg["stamm_tabelle"]):
            z = self._abfrage(f"SELECT * FROM {self._q(cfg['stamm_tabelle'])} "
                              f"WHERE {self._q(cfg['stamm_spalte'])} = {self.ph}", (name,))
            od.stamm = z[0] if z else {}

        tag_bed = " AND untersuchtag = " + self.ph if od.befahrung is not None else ""
        par = (name, od.befahrung) if od.befahrung is not None else (name,)
        for tab, spalte, ziel in ((cfg["kopf_tabelle"], cfg["kopf_spalte"], "kopf"),
                                  (cfg["bewertung_tabelle"], cfg["bewertung_spalte"], "bewertung")):
            if not self._hat(tab):
                continue
            try:
                sortierung = " ORDER BY pk DESC" if ziel == "bewertung" else ""
                z = self._abfrage(f"SELECT * FROM {self._q(tab)} WHERE {self._q(spalte)} = {self.ph}{tag_bed}{sortierung}",
                                  par)
                setattr(od, ziel, z[0] if z else {})
            except Exception as e:
                if ziel == "bewertung":
                    raise
                print(f"[BERICHT] {tab}: {e}")

        if self._hat(cfg["befund_tabelle"]):
            z = self._abfrage(f"SELECT * FROM {self._q(cfg['befund_tabelle'])} "
                              f"WHERE {self._q(cfg['befund_spalte'])} = {self.ph}{tag_bed}", par)
            for r in z:
                kuerzel = text(r.get("kuerzel"))
                od.befunde.append(Befund(station=zahl(r.get(cfg["station_spalte"])), kuerzel=kuerzel,
                                         langtext=text(r.get("langtext")), werte=r))
            od.befunde.sort(key=lambda b: (b.station if b.station is not None else 1e9))
            if art == "Schacht":
                # vertikale_lage = Höhe über Sohle: vom Deckel (größter Wert) zur Sohle sortieren
                od.befunde.sort(key=lambda b: -(b.station if b.station is not None else -1e9))
        if art == "Schacht":
            try:
                od.zusatz["rohre"] = self.schacht_rohre(name)
            except Exception as e:
                print(f"[BERICHT] Rohre am Schacht {name}: {e}")
                od.zusatz["rohre"] = []
        return od

    def schacht_rohre(self, schnam):
        """Haltungen am Schacht (Zu- und Abläufe) mit DN und Uhrlage aus der Geometrie.

        Uhrlage: Draufsicht, im Uhrzeigersinn, 12 Uhr = Hauptablauf (größter Ablauf).
        Die Richtung jeder Haltung wird aus ihrem ersten Segment am Schacht bestimmt."""
        if not self._hat("haltungen"):
            return []
        fkt = "ST_AsText" if self.art == "postgres" else "AsText"
        z = self._abfrage(f"SELECT haltnam, schoben, schunten, breite, hoehe, {fkt}(geom) AS wkt "
                          f"FROM haltungen WHERE schoben = {self.ph} OR schunten = {self.ph}", (schnam, schnam))
        rohre = []
        for r in z:
            ablauf = text(r.get("schoben")) == schnam
            dn = zahl(r.get("breite")) or zahl(r.get("hoehe"))
            if dn and dn < 10:
                dn *= 1000                      # m -> mm
            rohre.append({"haltnam": text(r.get("haltnam")), "rolle": "Ablauf" if ablauf else "Zulauf",
                          "dn": dn, "azimut": _azimut_am_schacht(r.get("wkt"), ablauf), "uhr": None})
        ablaeufe = [r for r in rohre if r["rolle"] == "Ablauf" and r["azimut"] is not None]
        if ablaeufe:
            haupt = max(ablaeufe, key=lambda r: r["dn"] or 0)
            for r in rohre:
                if r["azimut"] is None:
                    continue
                delta = (r["azimut"] - haupt["azimut"]) % 360.0
                u = int(round(delta / 30.0)) % 12
                r["uhr"] = 12 if u == 0 else u
        return rohre

    def geometrie_wkt(self, art, name):
        """Geometrie des Objekts als WKT (für den Bestandsplan, falls kein Layer passt)."""
        cfg = OBJEKTARTEN[art]
        if not self._hat(cfg["stamm_tabelle"]):
            return None, None
        fkt = "ST_AsText" if self.art == "postgres" else "AsText"
        srid = "ST_SRID" if self.art == "postgres" else "SRID"
        try:
            z = self._abfrage(f"SELECT {fkt}(geom) AS wkt, {srid}(geom) AS srid FROM "
                              f"{self._q(cfg['stamm_tabelle'])} WHERE {self._q(cfg['stamm_spalte'])} = {self.ph}",
                              (name,))
        except Exception:
            return None, None
        if not z:
            return None, None
        return z[0].get("wkt"), z[0].get("srid")


# ======================================================================
# Schadensbilder
# ======================================================================

def _azimut_am_schacht(wkt, am_anfang):
    """Richtung (Grad, im Uhrzeigersinn ab Nord) vom Schacht weg entlang der Haltung."""
    if not wkt:
        return None
    try:
        from qgis.core import QgsGeometry
        g = QgsGeometry.fromWkt(str(wkt))
        pts = [(v.x(), v.y()) for v in g.vertices()]
    except Exception:
        return None
    if len(pts) < 2:
        return None
    (x0, y0), (x1, y1) = (pts[0], pts[1]) if am_anfang else (pts[-1], pts[-2])
    if abs(x1 - x0) < 1e-9 and abs(y1 - y0) < 1e-9:
        return None
    import math
    return math.degrees(math.atan2(x1 - x0, y1 - y0)) % 360.0
