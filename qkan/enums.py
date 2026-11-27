import enum


class BefChoice(enum.Enum):
    FLAECHEN = "flaechen"
    TEZG = "tezg"


class ProfChoice(enum.Enum):
    PROFILNAME = "profilname"
    PROFILKEY = "profilkey"


class AuswahlTyp(enum.Enum):
    WITHIN = "within"
    OVERLAPS = "overlaps"


class BezugAbstand(enum.Enum):
    KANTE = "kante"
    MITTELPUNKT = "mittelpunkt"


class QmlChoice(enum.Enum):
    UEBH = "uebh"
    UEBVOL = "uebvol"
    USERQML = "userqml"
    NONE = "none"


class SelectedLayers(enum.Enum):
    ALL = "alle_anpassen"
    SELECTED = "auswahl_anpassen"
    NONE = "None"  # für Tests


class RunOffModelType(enum.Enum):
    SPEICHERKASKADE = "Speicherkaskade"
    FLIESSZEITEN = "Fliesszeiten"
    SCHWERPUNKTLAUFZEIT = "Schwerpunktlaufzeit"


class RunOffParamsType(enum.Enum):
    ITWH = "itwh"
    DYNA = "dyna"
    MANIAK = "maniak"


class QKanDBChoice(enum.Enum):
    SPATIALITE          = "spatialite"
    POSTGIS             = "postgis"                 # Achtung: lay.providerType() liefert 'postgres'


class UntersuchBezugpunkt(enum.Enum):
    ROHRANFANG          = 'Rohranfang'
    GERINNEMITTELPUNKT  = 'Gerinnemittelpunkt'


class Hoehensystem(enum.Enum):
    METER_UEBER_NN      = 'mnn'
    NORMAL_HOEHENNULL   = 'nhn'

class LAYERBEZ(enum.Enum):
    #Allgemeine Layer
    NOTIZEN             = "Notizen"
    SCHAECHTE           = "Schächte"
    AUSLAESSE           = "Auslässe"
    SPEICHER            = "Speicher"
    KNOTENTYP           = "Knotentyp"
    GEOMETRIEN          = "Geometrien"
    HALTUNGEN           = "Haltungen"
    HA_LEITUNGEN        = "HA-Leitungen"
    HA_SCHAECHTE        = "HA-Schächte"
    DROSSELN            = "Drosseln"
    SCHIEBER            = "Schieber"
    GRUND_SEITENAUSLASS = "Grund-/Seitenauslässe"
    H_REGLER            = "H-Regler"
    Q_REGLER            = "Q-Regler"
    PUMPEN              = "Pumpen"
    WEHRE               = "Wehre"
    HALTUNGSFLAECHEN    = "Haltungsflächen"
    ANBINDUNG_FLAECHEN  = "Anbindungen Flächen"
    EINZELFLAECHEN      = "Einzelflächen"
    TEILGEBIETE         = "Teilgebiete"
    DIREKTEINLEITUNGEN  = "Direkteinleitungen"
    ANBINDUNG_DIREKTEINLEITUNGEN    = "Anbindungen Direkteinleitungen"
    AUSSENGEBIETE                   = "Außengebiete"
    ANBINDUNG_AUSSENGEBIETE         = "Anbindung Außengebiete"
    ZUSTAND_HALTUNGEN               = "Zustand_Haltungen_gesamt"
    EINZELSCHAEDEN_HALTUNGEN        = "Einzelschäden_Haltungen"
    ZUSTAND_SCHAECHTE               = "Zustand_Schächte_gesamt"
    EINZELSCHAEDEN_SCHAECHTE        = "Einzelschäden_Schächte"
    ZUSTAND_HA_LEITUNGEN            = "Zustand_HA-Leitungen_gesamt"
    EINZELSCHAEDEN_HA_LEITUNGEN     = "Einzelschäden_HA-Leitungen"
    FEHLERLISTE                     = "Fehlerliste"
    PRUEFABFRAGEN                   = "Prüfabfragen"
    UEBERSTAUSCHAECHTE              = "Überstau Schächte"
    SYMBOLE                         = "Symbole"
    PLAUSISQL                       = "Prüfabfragen"
    REFDATA                         = "Alle Referendaten"

    # nur für Synchronisation
    VIDEOS                          = "Videos"
    FOTOS                           = "Fotos"

    QKAN_GROUP              = "QKan"
    ALLGEMEIN_GROUP         = "Allgemein"
    SCHAECHTE_GROUP         = "Schächte"
    HALTUNGEN_GROUP         = "Haltungen"
    SONDERELEMENTE_GROUP    = "Sonderelemente"
    FLAECHEN_GROUP          = "Flächen"
    EINLEITUNGEN_GROUP      = "Einleitungen"
    AUSSENGEBIETE_GROUP     = "Außengebiete"
    INSPEKTIONSDATEN_GROUP  = "Inspektionsdaten"
    ZUSTANDSBEWERTUNG_GROUP = "Zustandsbewertung"
    ZK_HALTUNGEN_GROUP      = "ZK_Haltungen"
    ZK_SCHAECHTE_GROUP      = "ZK_Schächte"
    ZK_HA_LEITUNGEN_GROUP   = "ZK_HA_Leitungen"
    SANIERUNGSBEDARF_GROUP  = "Sanierungsbedarf"
    SBZ_HALTUNGEN_GROUP     = "SBZ_Haltungen"
    SBZ_SCHAECHTE_GROUP     = "SBZ_Schächte"
    SBZ_HA_LEITUNGEN_GROUP  = "SBZ_HA_Leitungen"
    SYMBOLE_GROUP           = "Symbole"
    REFERENZTABELLEN_GROUP  = "Referenztabellen"
    M150_GROUP              = "M150"
    PLAUSI_GROUP            = "Plausibilitätsprüfungen"
    WMS_GROUP               = "WMS-Dienste"
    ERGEBNISSE_GROUP        = "Ergebnisse"

    #Referenztabellen
    ENTWAESSERUNGSARTEN     = "Entwässerungsarten"
    PROFILE                 = "Profile"
    PUMPENTYPEN             = "Pumpentypen"
    EIGENTUM                = "Eigentum"
    AUSLASSTYPEN            = "Auslasstypen"
    PLANUNGSSTATUS          = "Planungsstatus"
    BODENARTEN              = "Bodenarten"
    ABFLUSSPARAMETER        = "Abflussparameter"
    ABFLUSSTYPEN            = "Abflussmodelle"
    KNOTENTYPEN             = "Knotentypen"
    SCHACHTTYPEN            = "Schachttypen"
    SYMBOLKATALOG           = "Symbolkatalog"
    FLAECHENTYPEN           = "Flächentypen"
    MATERIAL                = "Material"
    M150_KNOTENARTEN        = "M150 Knotenarten"
    M150_KUERZEL_ERG        = "M150 Kürzel zu ergänzen"

    #Ergebnislayer
    ZK_EINZELSCHAEDEN_HA_LEITUNGEN  = "Ergebnis_ZK_Einzelschäden_HA_Leitungen"
    ZK_ZUSTAND_HA_LEITUNGEN         = "Ergebnis_ZK_HA_Leitungen"
    ZK_EINZELSCHAEDEN_SCHAECHTE     = "Ergebnis_ZK_Einzelschäden_Schächte"
    ZK_ZUSTAND_SCHAECHTE            = "Ergebnis_ZK_Schächte"
    ZK_EINZELSCHAEDEN_HALTUNGEN     = "Ergebnis_ZK_Einzelschäden_Haltungen"
    ZK_ZUSTAND_HALTUNGEN            = "Ergebnis_ZK_Haltungen"
    SK_EINZELSCHAEDEN_HALTUNGEN     = "Bewertung_Substanz_Einzelschäden_Haltungen"
    SK_ZUSTAND_HALTUNGEN            = "Bewertung_Substanz_Haltungen"

    # Anwendungsbezogene Layer
    STRAKAT_SYMBOLE = "STRAKAT-Symbole"

    # Synchronisation
    SYNC_SCHAECHTE_COMPARE              = "Synchronisation Schächte"
    SYNC_SCHAECHTE_EXT                  = "Schächte extern"
    SYNC_HALTUNGEN_COMPARE              = "Synchronisation Haltungen"
    SYNC_HALTUNGEN_EXT                  = "Haltungen extern"
    SYNC_HA_SCHAECHTE_COMPARE           = "Synchronisation HA-Schächte"
    SYNC_HA_SCHAECHTE_EXT               = "HA-Schächte extern"
    SYNC_HA_LEITUNGEN_COMPARE           = "Synchronisation HA-Leitungen"
    SYNC_HA_LEITUNGEN_EXT               = "HA-Leitungen extern"
    SYNC_FLAECHEN_COMPARE               = "Synchronisation Einzelflächen"
    SYNC_FLAECHEN_EXT                   = "Einzelflächen extern"
    SYNC_DIREKT_COMPARE                 = "Synchronisation Direkteinleiter"
    SYNC_DIREKT_EXT                     = "Direkteinleiter extern"
    SYNC_AUSSEN_COMPARE                 = "Synchronisation Außengebiete"
    SYNC_AUSSEN_EXT                     = "Außengebiete extern"
    SYNC_TEZG_COMPARE                   = "Synchronisation Haltungsflächen"
    SYNC_TEZG_EXT                       = "Haltungsflächen extern"
    SYNC_ANBINDUNG_FLAECHEN_COMPARE     = "Synchronisation Anbindungen Flächen"
    SYNC_ANBINDUNG_FLAECHEN_EXT         = "Anbindungen Flächen extern"
    SYNC_ANBINDUNG_DIREKT_COMPARE       = "Synchronisation Anbindungen Flächen"
    SYNC_ANBINDUNG_DIREKT_EXT           = "Anbindungen Flächen extern"
    SYNC_ANBINDUNG_AUSSEN_COMPARE       = "Synchronisation Anbindungen Flächen"
    SYNC_ANBINDUNG_AUSSEN_EXT           = "Anbindungen Flächen extern"
    SYNC_ZUSTAND_SCHAECHTE_COMPARE      = "Synchronisation Zustand Schächte"
    SYNC_ZUSTAND_SCHAECHTE_EXT          = "Zustand Schächte extern"
    SYNC_SCHAEDEN_SCHAECHTE_COMPARE     = "Synchronisation Einzelschäden Schächte"
    SYNC_SCHAEDEN_SCHAECHTE_EXT         = "Einzelschäden Schächte extern"
    SYNC_ZUSTAND_HALTUNGEN_COMPARE      = "Synchronisation Zustand Haltungen"
    SYNC_ZUSTAND_HALTUNGEN_EXT          = "Zustand Haltungen extern"
    SYNC_SCHAEDEN_HALTUNGEN_COMPARE     = "Synchronisation Einzelschäden Haltungen"
    SYNC_SCHAEDEN_HALTUNGEN_EXT         = "Einzelschäden Haltungen extern"
    SYNC_ZUSTAND_HA_LEITUNGEN_COMPARE   = "Synchronisation Zustand HA-Leitungen"
    SYNC_ZUSTAND_HA_LEITUNGEN_EXT       = "Zustand HA-Leitungen extern"
    SYNC_SCHAEDEN_HA_LEITUNGEN_COMPARE  = "Synchronisation Einzelschäden HA-Leitungen"
    SYNC_SCHAEDEN_HA_LEITUNGEN_EXT      = "Einzelschäden HA-Leitungen extern"
    SYNC_NOTIZEN_COMPARE                = "Synchronisation Notizen"
    SYNC_NOTIZEN_EXT                    = "Notizen extern"
    SYNC_SYMBOLE_COMPARE                = "Synchronisation Symbole"
    SYNC_SYMBOLE_EXT                    = "Symbole extern"
    SYNC_PLAUSI_COMPARE                 = "Synchronisation Plausibilitätsabfragen"
    SYNC_PLAUSI_EXT                     = "Plausibilitätsabfragen extern"
    SYNC_VIDEOS_COMPARE                 = "Synchronisation Videos"
    SYNC_VIDEOS_EXT                     = "Videos extern"
    SYNC_FOTOS_COMPARE                  = "Synchronisation Fotos"
    SYNC_FOTOS_EXT                      = "Fotos extern"
    SYNC_REFDATA_COMPARE                = "Synchronisation Referenztabellen"
    SYNC_REFDATA_EXT                    = "Referenztabellen extern"

    SYNC_GROUP_SYNCHRONISATION          = "Synchronisation"
    SYNC_GROUP_SCHAECHTE                = "Vergleich Schächte"
    SYNC_GROUP_HALTUNGEN                = "Vergleich Haltungen"
    SYNC_GROUP_HA_SCHAECHTE             = "Vergleich HA-Schächte"
    SYNC_GROUP_HA_LEITUNGEN             = "Vergleich HA-Leitungen"
    SYNC_GROUP_FLAECHEN                 = "Vergleich Flächen"
    SYNC_GROUP_DIREKT                   = "Vergleich Direkteinleiter"
    SYNC_GROUP_AUSSEN                   = "Vergleich Außengebiete"
    SYNC_GROUP_TEZG                     = "Vergleich Haltungsflächen"
    SYNC_GROUP_ANBINDUNG_FLAECHEN       = "Vergleich Anbindungen Flächen"
    SYNC_GROUP_ANBINDUNG_DIREKT         = "Vergleich Anbindungen Flächen"
    SYNC_GROUP_ANBINDUNG_AUSSEN         = "Vergleich Anbindungen Flächen"
    SYNC_GROUP_ZUSTAND_SCHAECHTE        = "Vergleich Zustand Schächte"
    SYNC_GROUP_SCHAEDEN_SCHAECHTE       = "Vergleich Einzelschäden Schächte"
    SYNC_GROUP_ZUSTAND_HALTUNGEN        = "Vergleich Zustand Haltungen"
    SYNC_GROUP_SCHAEDEN_HALTUNGEN       = "Vergleich Einzelschäden Haltungen"
    SYNC_GROUP_ZUSTAND_HA_LEITUNGEN     = "Vergleich Zustand HA-Leitungen"
    SYNC_GROUP_SCHAEDEN_HA_LEITUNGEN    = "Vergleich Einzelschäden HA-Leitungen"
    SYNC_GROUP_NOTIZEN                  = "Vergleich Notizen"
    SYNC_GROUP_SYMBOLE                  = "Vergleich Symbole"
    SYNC_GROUP_PLAUSI                   = "Vergleich Plausibilitätsabfragen"
    SYNC_GROUP_VIDEOS                   = "Vergleich Videos"
    SYNC_GROUP_FOTOS                    = "Vergleich Fotos"
    SYNC_GROUP_REFDATA                  = "Vergleich Referenztabellen"


class MikeVersion(enum.Enum):
    """Programmversion der Ergebnisdateien zu Mike+"""
    v1 = '2023'
    v2 = '2025'


class SyncTables(enum.Enum):
    """Synchronisation: Klassifizierung der Tabellen nach Geo-Objekt"""
    TABLES_GEOM = [
        "notizen",
        "haltungen",
        "haltungen_untersucht",
        "untersuchdat_haltung",
        "anschlussleitungen",
        "anschlussleitungen_untersucht",
        "anschlussschaechte",
        "untersuchdat_anschlussleitung",
        "untersuchdat_schacht",
        "einzugsgebiete",
        "teilgebiete",
        "flaechen",
        "tezg",
        "einleit",
        "aussengebiete",
        "symbole",
    ]

    TABLES_GEOP = [
        "schaechte",
        "schaechte_untersucht",
    ]

    TABLES_GLINK = [
        "linkfl",
        "linksw",
        "linkageb",
    ]

    TABLES_ATTR = [
        # "simulationsstatus",
        # "material",
        # "auslasstypen",
        # "abflussparameter",
        # "flaechentypen",
        # "bodenklassen",
        # "abflusstypen",
        # "knotentypen",
        # "schachttypen",
        # "eigentum",
        # "symbolkatalog",
        # # "dynahal",
        # "gruppen",
        # "profile",
        # "entwaesserungsarten",
        # "haltungstypen",
        # "untersuchrichtung",
        # "wetter",
        # "bewertungsart",
        # "pumpentypen",
        "pruefsql",
        # "pruefliste",
        # "reflist_zustand",
        # "info",
        "refdata",
        "fotos",
        "videos",
    ]

    TABLES_UNTERSUCH = [
        "untersuchdat_haltung",
        "untersuchdat_schacht",
        "untersuchdat_anschlussleitung",
        "haltungen_untersucht",
        "schaechte_untersucht",
        "anschlussleitungen_untersucht",
    ]