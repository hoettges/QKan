import enum
import json
import os
import site
import warnings
from pathlib import Path
from typing import Any, Dict

from qkan import enums
from qkan.utils import get_logger

log = get_logger("QKan.config")


class ConfigEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, enum.Enum):
            return o.value
        return o.__dict__


class ClassObject:
    def __init__(self, **kwargs: Any):
        annotation_keys = self.__annotations__.keys()

        # Assign values
        for key, value in kwargs.items():
            if key in annotation_keys:
                # Handle classes
                try:
                    if issubclass(self.__annotations__[key], ClassObject) and isinstance(
                        value, dict
                    ):
                        # Try to parse class
                        setattr(self, key, self.__annotations__[key](**value))
                        continue
                # except TypeError:
                #     raise TypeError(f"key {self.__annotations__[key]} is not a class")
                except:
                    log.error(f"key {self.__annotations__[key]} is not a class")
                    raise TypeError(f"key {self.__annotations__[key]} is not a class")

                # Handle enums, right now only string enums are supported
                if issubclass(self.__annotations__[key], enum.Enum) and isinstance(
                    value, str
                ):
                    try:
                        setattr(self, key, self.__annotations__[key](value))
                    except ValueError:
                        # Set default if the config's value does not exist in the enum
                        setattr(self, key, getattr(self, key))
                    continue

                # Type does not match annotation
                if (type(value) is not self.__annotations__[key] and value is not None):
                    # TODO: Notify user that setting has been reset/removed
                    if hasattr(self, key):
                        log.warning(
                            f"{self.__class__.__name__}: Replaced setting {key} "
                            f"with default value {getattr(self, key)}, previously "
                            f"{value} ({type(value)})"
                        )
                        setattr(self, key, getattr(self, key))
                        continue
                    else:
                        # Default setting does not exist
                        raise TypeError(
                            f"{self.__class__.__name__}: Value of {key} ({value}, "
                            f"{type(value)}) does not match"
                            f" annotation's type ({self.__annotations__[key]})."
                        )

            # Silently ignore/preserve setting, even if it doesn't exist
            setattr(self, key, value)

        # Check if all values are set
        kwargs_keys = kwargs.keys()
        for key in annotation_keys:
            # Set default values so that they appear in __dict__
            if not hasattr(self, key) and key not in kwargs_keys:
                raise Exception(
                    f"{self.__class__.__name__}: No default setting was defined "
                    f"for {key}, please report this to the developers."
                )
            elif key not in kwargs_keys:
                setattr(self, key, getattr(self, key))

    def __getitem__(self, key: str) -> Any:
        warnings.warn(
            f"{self.__class__.__name__}: The dict-like config has been replaced "
            f"with a class, use hasattr() instead.",
            DeprecationWarning,
            2,
        )
        return getattr(self, key)

    def __contains__(self, item: str) -> Any:
        warnings.warn(
            f"{self.__class__.__name__}: The dict-like config has been replaced "
            f"with a class, use hasattr() instead.",
            DeprecationWarning,
            2,
        )
        return hasattr(self, item)

    def __setattr__(self, key: str, value: Any) -> None:
        # Allow setting anything in temporary storage
        if hasattr(self, "allow_any"):
            super().__setattr__(key, value)
            return

        # Verify type if in annotation
        if key in self.__annotations__ and (type(value) is not self.__annotations__[key] and value is not None):
            raise TypeError(
                f"{self.__class__.__name__}: Value of {key} ({value}, "
                f"{type(value)}) does not match"
                f" annotation's type ({self.__annotations__[key]})."
            )
        elif key not in self.__annotations__:
            log.warning(
                f"{self.__class__.__name__}: Dropping unknown value/key "
                f"combination in config {key}={value} ({type(value)})"
            )
            return
        super().__setattr__(key, value)

    def __str__(self) -> str:
        sorted_kv = sorted([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"<{self.__class__.__name__} {' '.join(sorted_kv)}>"


class TempStorage(ClassObject):
    """
    May be used to save anything, will be written to config file
    """

    __annotations__: Dict[str, Any] = {}
    allow_any = True


class CheckExport(ClassObject):
    """Auswahl der zu exportierenden Datenbestände
    Bei 'Aktionen' kann die Methode der Synchronisation ausgewählt werden.
    Dabei basieren die Aktion auf einem Abgleich zwischen Quell- und Zieldaten
    Achtung: Falls eine Beschränkung auf Teilgebiete aktiviert ist, bezieht
    sich die Synchronisation nur auf die gewählten Teilgebiete!
    """

    # Tabellen mit Geo-Objekten
    schaechte: bool = True
    auslaesse: bool = True
    speicher: bool = True
    haltungen: bool = True
    anschlussleitungen: bool = True
    pumpen: bool = True
    wehre: bool = True
    drosseln: bool = True
    grundseitenauslaesse: bool = True
    schieber: bool = True
    qregler: bool = True
    hregler: bool = True
    flaechen: bool = True
    einleitdirekt: bool = True
    aussengebiete: bool = True
    einzugsgebiete: bool = True
    tezg: bool = True
    tezg_hf: bool = (
        False  # Sonderfall: Keine Flächenobjekte, stattdessen Befestigungsgrade in tezg
    )

    # Referenztabellen
    abflussparameter: bool = True
    bodenklassen: bool = True
    rohrprofile: bool = True

    # Aktionen
    append: bool = True  # Daten hinzufügen
    update: bool = False  # Daten ändern
    synch: bool = False  # Daten löschen


class CheckImport(ClassObject):
    """Auswahl der zu importierenden Datenbestände
    Bei 'Aktionen' kann die Methode der Synchronisation ausgewählt werden.
    Dabei basieren die Aktion auf einem Abgleich zwischen Quell- und Zieldaten
    Achtung: Falls eine Beschränkung auf Teilgebiete aktiviert ist, bezieht
    sich die Synchronisation nur auf die gewählten Teilgebiete!
    """

    # Tabellen mit Geo-Objekten
    schaechte: bool = True
    auslaesse: bool = True
    speicher: bool = True
    haltungen: bool = True
    pumpen: bool = True
    wehre: bool = True
    drosseln: bool = True
    grundseitenauslaesse: bool = True
    schieber: bool = True
    qregler: bool = True
    hregler: bool = True
    flaechen: bool = True
    einleitdirekt: bool = True
    aussengebiete: bool = True
    einzugsgebiete: bool = True
    hausanschluesse: bool = True
    schachtschaeden: bool = True
    haltungsschaeden: bool = True
    testmodus: bool = False

    # Haltungsflächen aus GIPS, drei Typen in einer Tabelle
    tezg_ef: bool = True
    tezg_hf: bool = (
        True  # Sonderfall: Keine Flächenobjekte, stattdessen Befestigungsgrade in tezg
    )
    tezg_tf: bool = True

    # Referenztabellen
    abflussparameter: bool = True
    bodenklassen: bool = True
    rohrprofile: bool = True

    # Aktionen
    append: bool = True  # Daten hinzufügen
    update: bool = False  # Daten ändern
    synch: bool = False  # Daten löschen
    allrefs: bool = (
        False  # Daten aus Referenztabellen: Nicht verwendete Referenzwerte einschließen
    )


class DatabaseConfig(ClassObject):
    qkan: str = ""
    type: enums.QKanDBChoice = enums.QKanDBChoice.SPATIALITE


class DynaConfig(ClassObject):
    autonummerierung: bool = False
    bef_choice: enums.BefChoice = enums.BefChoice.FLAECHEN
    file: str = ""
    prof_choice: enums.ProfChoice = enums.ProfChoice.PROFILNAME
    profile_ergaenzen: bool = True
    template: str = ""


class SWMMConfig(ClassObject):
    autonummerierung: bool = False
    # bef_choice: enums.BefChoice = enums.BefChoice.FLAECHEN
    database: str = ""  # QKan-Projektdatenbank
    file: str = ""
    # prof_choice: enums.ProfChoice = enums.ProfChoice.PROFILNAME
    profile_ergaenzen: bool = True
    template: str = ""
    import_file: str = ""  # Importdatei *.inp
    export_file: str = ""  # Exportdatei *.inp
    liste_teilgebiete: list = []


class LinkFlConfig(ClassObject):
    """Einstellungen der Flächenverknüpfungsfunktionen Linkflaechen"""
    auswahltyp: enums.AuswahlTyp = enums.AuswahlTyp.WITHIN
    bezug_abstand: enums.BezugAbstand = enums.BezugAbstand.KANTE
    bufferradius: float = 0.0
    delete_geom_none: bool = True
    links_in_tezg: bool = True
    suchradius: float = 50.0


class SelectionConfig(ClassObject):
    abflussparameter: list = []
    flaechen_abflussparam: list = []
    hal_entw: list = []
    teilgebiete: list = []


class HEConfig(ClassObject):
    database: str = ""
    database_erg: str = ""
    # database_erg_fb: str = ""
    # database_fb: str = ""
    qml_choice: enums.QmlChoice = enums.QmlChoice.UEBH
    qml_file_results: str = ""
    template: str = ""
    # template_fb: str = ""


class HE8Config(ClassObject):
    database: str = ""  # QKan-Projektdatenbank
    # database_erg: str = ""                    # ist jetzt: results_file
    qml_choice: enums.QmlChoice = enums.QmlChoice.UEBH
    qml_file_results: str = ""
    template: str = ""  # Vorlage für Export-Datenbank
    import_file: str = ""  # Import-Datenbank *.idbm
    export_file: str = ""  # Export-Datenbank *.idbm
    results_file: str = ""  # Ergebnis-Datenbank *.idbr


class STRAKATConfig(ClassObject):
    import_dir: str = ""  # Importverzeichnis mit den STRAKAT-Dateien, u. a. kanal.rwtopen


class FLOODConfig(ClassObject):
    import_dir: str = ""    # Importverzeichnis mit den Geodatabase-Ergebnisdaten
    database: str = ""      # Ergebnisdatenbank
    velo: bool = True       # Creation of volocity arrows checked
    wlevel: bool = True     # Creation of water level triangles checked
    gdblayer: bool = False  # Keeps GDB-Layer in layer list
    faktor_v: float = 5.    # Factor for arrow length in relation to velocity
    min_w: float = 0.1      # Minimal water level to display
    min_v: float = 0.1      # Minimal velocitiy to display


class MUConfig(ClassObject):
    database: str = ""  # QKan-Projektdatenbank
    # database_erg: str = ""                    # ist jetzt: export_file
    qml_file_results: str = ""
    template: str = ""
    import_file: str = ""  # Import-Datenbank *.sqlite
    export_file: str = ""  # Export-Datenbank *.sqlite


class SWMMConfig(ClassObject):
    database: str = ""      # QKan-Projektdatenbank
    template: str = ""
    import_file: str = ""   # Importdatei *.inp
    export_file: str = ""   # Exportdatei *.inp


class ProjectConfig(ClassObject):
    file: str = ""
    save_file: bool = True
    template: str = ""


class AdaptConfig(ClassObject):
    add_missing_layers: bool = True
    database: bool = True
    forms: bool = True
    macros: bool = True
    kbs: bool = True
    qkan_db_update: bool = True
    selected_layers: enums.SelectedLayers = enums.SelectedLayers.ALL
    table_lookups: bool = True
    update_node_type: bool = True
    zoom_all: bool = True


class ToolsConfig(ClassObject):
    class RunoffParams(ClassObject):
        # TODO: Implement user choice of hard-coded and custom functions
        itwh: list = [
            "round(0.8693*log(area(geom))+ 5.6317, 2)",
            "round(pow(18.904*pow(neigkl,0.686)*area(geom), 0.2535*pow(neigkl,0.244)), 2)",
        ]
        dyna: list = [
            "round(0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*0.02 * "
                "(abstand + fliesslaenge) / SQRT(neigung), 0.467), 2)",
            "round(pow(2*0.10 * (abstand + fliesslaenge) / SQRT(neigung), 0.467), 2)",
        ]
        maniak: list = [
            "round(0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*0.02 * "
                "(abstand + fliesslaenge) / SQRT(neigung), 0.467), 2)",
            "round(pow(2*0.10 * (abstand + fliesslaenge) / SQRT(neigung), 0.467), 2)",
            "round(0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*0.02 * abstand / SQRT(neigung), 0.467), 2)",
            "round(pow(2*0.10 * abstand / SQRT(neigung), 0.467), 2)",
            "round(0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + "
                "pow(2*0.02 * fliesslaenge / SQRT(neigung), 0.467), 2)",
            "round(pow(2*0.10 * fliesslaenge / SQRT(neigung), 0.467), 2)",
        ]
        def __str__(self) -> str:
            return "<RunoffParams *hidden in __str__*>"


    class Clipboard(ClassObject):
        """Patterns for replacing column names with the QKan database names"""

        # 1. required fields,
        required_fields = {
            "schaechte": ["schnam", "sohlhoehe"],
            "auslaesse": ["schnam", "sohlhoehe"],
            "speicher": ["schnam", "sohlhoehe"],
            "haltungen": ["haltnam"],
            "pumpen": ["pnam", "schoben", "schunten"],
            "wehre": ["wnam", "schoben", "schunten"],
            "drosseln": ["wnam", "schoben", "schunten"],
            "schieber": ["wnam", "schoben", "schunten"],
            "grundseitenauslaesse": ["wnam", "schoben", "schunten"],
            "qregler": ["wnam", "schoben", "schunten"],
            "hregler": ["wnam", "schoben", "schunten"],
            "tezg": [],
            "flaechen": [],
            "teilgebiete": [],
            "anschlussleitungen": ["leitnam"],
            "untersuchdat_haltung": ["untersuchhal", "schoben", "schunten", "station", 'kuerzel'],
            "untersuchdat_schacht": ['untersuchsch', 'kuerzel'],
            'haltungen_untersucht': ['haltnam', 'schoben', 'schunten'],
            'schaechte_untersucht': ['schnam'],
        }

        # Layer names with data source table 'schaechte'
        schacht_types = {
            "Schächte": "Schacht",
            "Knotenpunkte": "Schacht",
            "Knotentyp": "Schacht",
            "Speicher": "Speicher",
            "Auslässe": "Auslass",
        }

        # Layer names with data source table 'haltungen'
        haltung_types = {
            "Haltungen": "Haltung",
            "Pumpen": "Pumpe",
            "Wehre": "Wehr",
            "Drosseln": "Drossel",
            "Schieber": "Schieber",
            "Grund-/Seitenauslässe": "GrundSeitenauslass",
            "H-Regler": "H-Regler",
            "Q-Regler": "Q-Regler",
        }

        # patterns must be lower case
        qkan_patterns = {
            'schaechte': {
                'schnam': ['scha*', 'schna*', 'nam*'],
                'xsch': ['x*', 'laengs*', 'breit*'],
                'ysch': ['y*', 'hoch*', 'hoeh*'],
                'deckelhoehe': ['deckel*'],
                'sohlhoehe': ['sohl*', 'sohl*h*'],
                'durchm': ['durchm*', 'diam*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['geom'],
                'geop': ['wkt_geom', 'geop'],
            },
            'haltungen': {
                'haltnam': ['haltn*', 'haltu*', 'kanaln*', 'nam*', ],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'xschob': ['xob*', 'xschob*'],
                'yschob': ['yob*', 'yschob*'],
                'xschun': ['xun*', 'xschun*'],
                'yschun': ['yun*', 'yschun*'],
                'breite': ['brei*', 'rohrbrei*', 'prof*brei*', ],
                'hoehe': ['hoe*', 'höh*', 'h\xf6h*',
                          'rohrhoe*', 'rohrhöh*', 'rohrh\xf6h*',
                          'prof*hoe*', 'prof*höh*', 'prof*h\xf6*',
                          'durchm*'],
                'laenge': ['laen*', 'läng*'],
                'sohleoben': ['sohl*ob*', 'sohl*anf'],
                'sohleunten': ['sohl*un*', 'sohl*end*'],
                'profilnam': ['profil*', ],
                'ks': ['ks*', 'rauh*'],
                'strasse': ['stras*', 'stra\xdf*', 'straß*'],
                'entwart': ['entw*art', 'entw*typ*', 'entw*ver*', 'kanalart*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'pumpen': {
                'pnam': ['p*nam*', 'nam*', ],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'sohlhoehe': ['sohl*h*'],
                'einschalthoehe': ['eins*h*', ],
                'ausschalthoehe': ['auss*h*', ],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'wehre': {
                'wnam': ['w*nam*', 'nam*', ],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'sohlhoehe': ['sohl*h*'],
                'schwellenhoehe': ['schwel*h*', 'kant*h*', ],
                'kammerhoehe': ['kamm*h*', ],
                'laenge': ['*laen*', '*läng*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'drosseln': {
                'name': ['*nam*', 'nam*', ],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'sohlabstand': ['sohl*ab*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'schieber': {
                'name': ['nam*', '*nam*'],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'breite': ['brei*', 'rohrbrei*', 'prof*brei*', ],
                'hoehe': ['hoe*', 'höh*', 'h\xf6h*',
                          'rohrhoe*', 'rohrhöh*', 'rohrh\xf6h*',
                          'prof*hoe*', 'prof*höh*', 'prof*h\xf6*',
                          'durchm*'],
                'sohleoben': ['sohl*ob*', 'sohl*anf'],
                'sohleunten': ['sohl*un*', 'sohl*end*'],
                'profilnam': ['profil*', ],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'grundseitenanlaesse': {
                'name': ['nam*', '*nam*'],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'breite': ['brei*', 'rohrbrei*', 'prof*brei*', ],
                'hoehe': ['hoe*', 'höh*', 'h\xf6h*',
                          'rohrhoe*', 'rohrhöh*', 'rohrh\xf6h*',
                          'prof*hoe*', 'prof*höh*', 'prof*h\xf6*',
                          'durchm*'],
                'sohleoben': ['sohl*ob*', 'sohl*anf'],
                'sohleunten': ['sohl*un*', 'sohl*end*'],
                'profilnam': ['profil*', ],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'qregler': {
                'name': ['nam*', '*nam*'],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'breite': ['brei*', 'rohrbrei*', 'prof*brei*', ],
                'hoehe': ['hoe*', 'höh*', 'h\xf6h*',
                          'rohrhoe*', 'rohrhöh*', 'rohrh\xf6h*',
                          'prof*hoe*', 'prof*höh*', 'prof*h\xf6*',
                          'durchm*'],
                'laenge': ['laen*', 'läng*'],
                'sohleoben': ['sohl*ob*', 'sohl*anf'],
                'sohleunten': ['sohl*un*', 'sohl*end*'],
                'profilnam': ['profil*', ],
                'ks': ['ks*', 'rauh*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'hregler': {
                'name': ['nam*', '*nam*'],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'breite': ['brei*', 'rohrbrei*', 'prof*brei*', ],
                'hoehe': ['hoe*', 'höh*', 'h\xf6h*',
                          'rohrhoe*', 'rohrhöh*', 'rohrh\xf6h*',
                          'prof*hoe*', 'prof*höh*', 'prof*h\xf6*',
                          'durchm*'],
                'laenge': ['laen*', 'läng*'],
                'sohleoben': ['sohl*ob*', 'sohl*anf'],
                'sohleunten': ['sohl*un*', 'sohl*end*'],
                'profilnam': ['profil*', ],
                'ks': ['ks*', 'rauh*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'abflussparameter': {
                'apnam': ['nam*', 'bez*'],
                'anfangsabflussbeiwert': ['*', ],
                'endabflussbeiwert': ['*', ],
                'benetzungsverlust': ['*', ],
                'muldenverlust': ['*', ],
                'benetzungs_startwert': ['*', ],
                'mulden_startwert': ['*', ],
                'bodenklasse': ['*', ],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
            },
            'tezg': {
                'flnam': ['nam*', 'bez*'],
                'flaeche': ['flae*', 'flä*', 'fl\x4e*'],
                'befgrad': ['*bef*', '*und*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'flaechen': {
                'flnam': ['f*nam*', 'bez*'],
                'haltnam': ['haltn*', 'haltu*', 'kanaln*', 'nam*', ],
                'schnam': ['sch*', ],
                'neigkl': ['neig*kl*'],
                'neigung': ['neigung', 'neig*grad'],
                'regenschreiber': ['regen*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'teilgebiete': {
                'tgnam': ['nam*', 'bez*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'anschlussleitungen': {
                'leitnam': ['leit*', 'haltn*', 'haltu*', 'bez*', 'kanaln*', 'nam*', ],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'xschob': ['xob*', 'xschob*'],
                'yschob': ['yob*', 'yschob*'],
                'xschun': ['xun*', 'xschun*'],
                'yschun': ['yun*', 'yschun*'],
                'breite': ['brei*', 'rohrbrei*', 'prof*brei*', ],
                'hoehe': ['hoe*', 'höh*', 'h\xf6h*',
                          'rohrhoe*', 'rohrhöh*', 'rohrh\xf6h*',
                          'prof*hoe*', 'prof*höh*', 'prof*h\xf6*',
                          'durchm*'],
                'laenge': ['laen*', 'läng*'],
                'sohleoben': ['sohl*ob*', 'sohl*anf'],
                'sohleunten': ['sohl*un*', 'sohl*end*'],
                'deckeloben': ['deckel*ob*', 'deckel*anf'],
                'deckelunten': ['deckel*un*', 'deckel*end*'],
                'profilnam': ['profil*', ],
                'ks': ['ks*', 'rauh*'],
                'entwart': ['entw*art', 'entw*typ*', 'kanalart*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geo*'],
            },
            'untersuchdat_haltung': {
                'untersuchhal': ['untersuchh*', 'hal*', 'nam'],
                'untersuchrichtung': ['untersuchr*'],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'id': ['id'],
                'untersuchtag': ['inspekt*d*', 'dat*inspekt*', 'unters*d*', 'dat*unters*', 'unters*tag', 'tag*unters*'],
                'bandnr': ['bandn*'],
                'videozaehler': ['zaehl*', 'z\xe4hl*', 'videozaehl*', 'videoz\xe4hl*'],
                'inspektionslaenge': ['inspekt*l*', 'l*inspek*'],
                'station': ['stati*'],
                'timecode': ['timec*', 'zeit*'],
                'video_offset': ['*offset'],
                'kuerzel': ['scha*kuerz*', 'kuerz', 'scha*k\xfcrz*', 'k\xfcrz'],
                'charakt1': ['cara*1', 'chara*1'],
                'charakt2': ['cara*2', 'chara*2'],
                'quantnr1': ['qua*1'],
                'quantnr2': ['qua*2'],
                'streckenschaden_lfdnr': ['streck*schad*nr'],
                'streckenschaden': ['stre*scha'],
                'pos_von': ['pos*von'],
                'pos_bis': ['pos*bis'],
                'foto_dateiname': ['fot*datei*'],
                'film_dateiname': ['fil*datei*', 'vid*datei'],
                'ordner_bild': ['ordner_bil*', 'ordner_fot*', 'pfad_bil*', 'pfad_fot*', 'dir_bil*', 'dir_fot*',
                                'bil*_ordner', 'fot*_ordner', 'bil*_pfad', 'fot*_pfad', 'bil*_dir', 'fot*_dir'],
                'ordner_video': ['ordner_film', 'ordner_vid*', 'pfad_film', 'pfad_vid*', 'dir_film', 'dir_vid*',
                                 'film_ordner', 'vid*_ordner', 'film_pfad', 'vid*_pfad', 'film_dir', 'vid*_dir'],
                'richtung': ['richt*'],
                'ZD': ['zd', 'zkd'],
                'ZB': ['zb', 'zkb'],
                'ZS': ['zs', 'zks'],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geom'],
            },
            'haltungen_untersucht': {
                'haltnam': ['haltn*', 'haltu*', 'kanaln*', 'nam*', ],
                'schoben': ['sch*ob*', 'sch*anf', 'anf*sch*', ],
                'schunten': ['sch*un*', 'sch*end', 'end*sch*', ],
                'hoehe': ['hoe*', 'höh*', 'h\xf6h*',
                          'rohrhoe*', 'rohrhöh*', 'rohrh\xf6h*',
                          'prof*hoe*', 'prof*höh*', 'prof*h\xf6*',
                          'durchm*'],
                'breite': ['brei*', 'rohrbrei*', 'prof*brei*', ],
                'laenge': ['laen*', 'läng*'],
                'baujahr': ['bauj*', 'jahr*'],
                'untersuchtag': ['inspekt*d*', 'dat*inspekt*', 'unters*d*', 'dat*unters*', 'unters*tag', 'tag*unters*'],
                'untersucher': ['untersucher', 'inspekteur', '*firma*'],
                'wetter': ['wetter*'],
                'strasse': ['stras*', 'stra\xdf*', 'straß*'],
                'bewertungsart': ['bewer*art'],
                'bewertungstag': ['bewer*tag'],
                'datenart': ['dat*art', 'dat*typ'],
                'max_ZD': ['max*zd', 'max*zkd', 'zkd*', 'zd*', 'skdich*'],
                'max_ZB': ['max*zb', 'max*zkb', 'zkb*', 'zb*', 'skbetr*'],
                'max_ZS': ['max*zs', 'max*zks', 'zks*', 'zs*', 'skstand*'],
                'xschob': ['xob*', 'xschob*'],
                'yschob': ['yob*', 'yschob*'],
                'xschun': ['xun*', 'xschun*'],
                'yschun': ['yun*', 'yschun*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geom': ['wkt_geom', 'geom'],
            },
            'schaechte_untersucht': {
                'schnam': ['scha*', 'schna*', 'nam*'],
                'durchm': ['durchm*', 'diam*'],
                'xsch': ['x*', 'laengs*', 'breit*'],
                'ysch': ['y*', 'hoch*', 'hoeh*'],
                'baujahr': ['bauj*', 'jahr*'],
                'untersuchtag': ['inspekt*d*', 'dat*inspekt*', 'unters*d*', 'dat*unters*', 'unters*tag', 'tag*unters*'],
                'untersucher': ['untersucher'],
                'wetter': ['wetter*'],
                'strasse': ['stras*', 'stra\xdf*', 'straß*'],
                'bewertungsart': ['bewer*art'],
                'bewertungstag': ['bewer*tag'],
                'datenart': ['dat*art', 'dat*typ'],
                'max_ZD': ['max*zd', 'max*zkd', 'zkd*', 'zd*', 'skdich*'],
                'max_ZB': ['max*zb', 'max*zkb', 'zkb*', 'zb*', 'skbetr*'],
                'max_ZS': ['max*zs', 'max*zks', 'zks*', 'zs*', 'skstand*'],
                'kommentar': ['kommen*', 'zusatzt*', 'bemerk*', ],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geop': ['wkt_geom', 'geop'],
            },
            'untersuchdat_schacht': {
                'untersuchsch': ['untersuchsch*', 'scha*', 'schna*', 'nam*'],
                'id': ['id'],
                'untersuchtag': ['inspekt*d*', 'dat*inspekt*', 'unters*d*', 'dat*unters*', 'unters*tag', 'tag*unters*'],
                'bandnr': ['bandn*'],
                'videozaehler': ['videoz*'],
                'timecode': ['timeco*', 'zeitco*'],
                'kuerzel''': ['kuerz*', 'kürz*', 'k\xfcrz*'],
                'charakt1': ['cara*1', 'chara*1'],
                'charakt2': ['cara*2', 'chara*2'],
                'quantnr1': ['quan*1'],
                'quantnr2': ['quan*1'],
                'streckenschaden_lfdnr': ['streck*schad*nr'],
                'streckenschaden': ['streck*scha*'],
                'pos_von': ['pos*von'],
                'pos_bis': ['pos*bis'],
                'vertikale_lage': ['vert*lag*', 'lag*vert*'],
                'inspektionslaenge': ['inspekt*l*', 'l*inspek*'],
                'bereich': ['berei*'],
                'foto_dateiname': ['*datei*'],
                'ordner': ['ordner', 'pfad', 'dir'],
                'ZD': ['zd', 'zkd'],
                'ZB': ['zb', 'zkb'],
                'ZS': ['zs', 'zks'],
                'createdat': ['crea*da*', 'erst*', '*änder*', '*\xe4nder*'],
                'geop': ['wkt_geom', 'geop'],
            },
            'entwart': {
                'Mischwasser': ['M*'],
                'Schmutzwasser': ['S*'],
                'Regenwasser': ['R*']
            },
        }

        def __str__(self) -> str:
            return "<Clipboard *hidden in __str__*>"

    apply_qkan_template: bool = True
    logeditor: str = ""
    panoramoplayer: str = ""
    manningrauheit_bef: float = 0.02
    manningrauheit_dur: float = 0.10
    runoffmodeltype_choice: enums.RunOffModelType = (
        enums.RunOffModelType.SPEICHERKASKADE
    )
    runoffparamsfunctions: RunoffParams = RunoffParams()
    runoffparamstype_choice: enums.RunOffParamsType = enums.RunOffParamsType.ITWH


class XmlConfig(ClassObject):
    export_file: str = ""
    import_file: str = ""
    richt_choice: str = ""
    data_choice: str = ""
    ordner_bild: str = ""
    ordner_video: str = ""
    # init_database: bool = True
    import_stamm: bool = True
    import_haus: bool = True
    import_zustand: bool = True


class ZustandConfig(ClassObject):
    db: str = ""
    date: str = ""
    showschaedencolumns: int = 2
    kriterienschaeden: dict = {'haltung': '[ABC][A-E][A-Z]', 'schacht': '[D][A-E][A-Z]'}


class SanierungConfig(ClassObject):
    db: str = ""
    date: str = ""
    speicher: str = ""
    atlas: str = ""
    speicher2: str = ""


class PlausiConfig(ClassObject):
    """Einstellungen der Plausibilitätskontrolle datacheck"""
    themen: list = ['Netzstruktur']
    keepdata: bool = False


class Config(ClassObject):
    autokorrektur: bool = True
    epsg: int = 25832
    fangradius: float = 0.1
    max_loops: int = 1000
    mindestflaeche: float = 0.5
    mit_verschneidung: bool = True
    database_typ: str = 'sqlite'
    # ---
    adapt: AdaptConfig = AdaptConfig()
    check_export: CheckExport = CheckExport()
    check_import: CheckImport = CheckImport()
    selections: SelectionConfig = SelectionConfig()
    database: DatabaseConfig = DatabaseConfig()
    dyna: DynaConfig = DynaConfig()
    swmm: SWMMConfig = SWMMConfig()
    he: HEConfig = HEConfig()
    he8: HE8Config = HE8Config()
    strakat: STRAKATConfig = STRAKATConfig()
    flood: FLOODConfig = FLOODConfig()
    mu: MUConfig = MUConfig()
    linkflaechen: LinkFlConfig = LinkFlConfig()
    project: ProjectConfig = ProjectConfig()
    tools: ToolsConfig = ToolsConfig()
    xml: XmlConfig = XmlConfig()
    plausi: PlausiConfig = PlausiConfig()
    zustand: ZustandConfig = ZustandConfig()
    sanierung: SanierungConfig = SanierungConfig()

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def save(self) -> None:
        cfile = Path(site.getuserbase()) / "qkan" / "qkan.json"
        if not cfile.parent.exists():
            os.makedirs(cfile.parent)
        try:
            cfile.write_text(
                json.dumps(self, cls=ConfigEncoder, sort_keys=True, indent=4)
            )
        except OSError as e:
            log.exception("Failed to save config")
            raise e

    @staticmethod
    def load() -> "Config":
        """
        Load config from file or generate a new on based on defaults

        @raises json.JSONDecodeError, OSError upon failure
        """
        cfile = Path(site.getuserbase()) / "qkan" / "qkan.json"
        if cfile.exists():
            cjson = json.loads(cfile.read_text())

            return Config(**cjson)
        else:
            return Config()
