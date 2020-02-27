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
    NONE = "None"                       # für Tests


class RunOffModelType(enum.Enum):
    SPEICHERKASKADE = "Speicherkaskade"
    FLIESSZEITEN = "Fliesszeiten"
    SCHWERPUNKTLAUFZEIT = "Schwerpunktlaufzeit"


class RunOffParamsType(enum.Enum):
    ITWH = "itwh"
    DYNA = "dyna"
    MANIAK = "maniak"


class QKanDBChoice(enum.Enum):
    SPATIALITE = "spatialite"
    POSTGIS    = "postgis"
