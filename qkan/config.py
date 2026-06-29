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
    anschlussschaechte: bool = True
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
    zustandsdaten: bool = False
    tezg_hf: bool = (
        False  # Sonderfall: Keine Flächenobjekte, stattdessen Befestigungsgrade in tezg
    )
    includeMissingKeys: bool = False
    cutNames:           bool = False

    hoehensystem: enums.Hoehensystem = enums.Hoehensystem.METER_UEBER_NN

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
    hausanschlussschaeden: bool = True
    symbole: bool = True                            # nur STRAKAT-Schächte, die Symbole darstellen
    testmodus: bool = False

    # Haltungsflächen aus GIPS, drei Typen in einer Tabelle
    tezg_ef: bool = True
    tezg_hf: bool = True    # Sonderfall: Keine Flächenobjekte, stattdessen Befestigungsgrade in tezg
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
    authConfigId: str = 'qkan001'


class SyncConfig(ClassObject):
    ext: str = ""
    check_schaechte: bool = True
    check_haltungen: bool = True
    check_haschaechte: bool = True
    check_haleitungen: bool = True
    check_flaechen: bool = True
    check_einleitdirekt: bool = True
    check_tezg: bool = True
    check_linkfl: bool = True
    check_linksw: bool = True
    check_schaechte_insp: bool = True
    check_haltungen_insp: bool = True
    check_haleitungen_insp: bool = True
    check_notizen: bool = True
    check_symbole: bool = True
    check_plausi: bool = True
    ckeck_refdata: bool = True
    check_showAttrTables: bool = True
    check_add: bool = True
    check_mod: bool = True
    check_del: bool = False

    check_allow_deletions: bool = False

    protfile: str = ""


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
    selectedObjects: bool = False
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
    import_file: str = ""   # Import-Datenbank *.idbm
    export_file: str = ""   # Export-Datenbank *.idbm
    results_file: str = ""  # Ergebnis-Datenbank *.idbr


class STRAKATConfig(ClassObject):
    import_dir: str = ""            # Importverzeichnis mit den STRAKAT-Dateien, u. a. kanal.rwtopen
    maxdiff: float = 0.1            # Abst
    coords_from_rohr: bool = False  # Haltungskoordinaten aus Rohranfang bzw. -ende statt Gerinne_o bzw. _u


class FLOODConfig(ClassObject):
    import_dir: str = ""                        # Importverzeichnis mit den Geodatabase-Ergebnisdaten
    database: str = ""                          # Ergebnisdatenbank
    velo: bool = True                           # Creation of velocity arrows checked
    wlevel: bool = True                         # Creation of water level triangles checked
    gdblayer: bool = False                      # Keeps GDB-Layer in layer list
    syncSelections: bool = True                 # Auswahl von einem der beiden Layer waterlevels und
                                                # velocities auf beide übertragen
    faktor_v: float = 5.                        # Factor for arrow length in relation to velocity
    min_w: float = 0.1                          # Minimal water level to display
    min_v: float = 0.1                          # Minimal velocitiy to display
    mikeversion: enums.MikeVersion = enums.MikeVersion.v1     # aktuell 2023 und 2025


class MUConfig(ClassObject):
    database: str = ""  # QKan-Projektdatenbank
    # database_erg: str = ""                    # ist jetzt: export_file
    qml_file_results: str = ""
    template: str = ""
    import_file: str = ""  # Import-Datenbank *.sqlite
    export_file: str = ""  # Export-Datenbank *.sqlite


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
    table_lookups: bool = True                  # deprecated
    adapt_layerstyles: bool = True              # replaces table_lookups
    update_node_type: bool = True
    zoom_all: bool = True


class ToolsConfig(ClassObject):

    apply_qkan_template: bool = True
    logeditor: str = ""
    panoramoplayer: str = ""
    manningrauheit_bef: float = 0.02
    manningrauheit_dur: float = 0.10
    runoffmodeltype_choice: enums.RunOffModelType = (
        enums.RunOffModelType.SPEICHERKASKADE
    )
    runoffparamstype_choice: enums.RunOffParamsType = enums.RunOffParamsType.ITWH

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

    runoffparamsfunctions: RunoffParams = RunoffParams()


    class Clipboard(ClassObject):
        """Patterns for replacing column names with the QKan database names"""

        # 1. required fields,
        required_fields: dict = {
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
        schacht_types: dict = {
            enums.LAYERBEZ.SCHAECHTE.value: "Schacht",                  # Filterkriterium in Attribut schachttyp
            enums.LAYERBEZ.GEOMETRIEN.value: "Schacht",
            enums.LAYERBEZ.KNOTENTYP.value: "Schacht",
            enums.LAYERBEZ.SPEICHER.value: "Speicher",
            enums.LAYERBEZ.AUSLAESSE.value: "Auslass",
        }

        # Layer names with data source table 'haltungen'
        haltung_types: dict = {
            enums.LAYERBEZ.HALTUNGEN.value: "Haltung",                  # Filterkriterium in Attribut haltungstyp
            enums.LAYERBEZ.PUMPEN.value: "Pumpe",
            enums.LAYERBEZ.WEHRE.value: "Wehr",
            enums.LAYERBEZ.DROSSELN.value: "Drossel",
            enums.LAYERBEZ.SCHIEBER.value: "Schieber",
            enums.LAYERBEZ.GRUND_SEITENAUSLASS.value: "GrundSeitenauslass",
            enums.LAYERBEZ.H_REGLER.value: "H-Regler",
            enums.LAYERBEZ.Q_REGLER.value: "Q-Regler",
        }
        def __str__(self) -> str:
            return "<Clipboard *hidden in __str__*>"

    clipboardattributes: Clipboard = Clipboard()


class XmlConfig(ClassObject):
    export_file: str = ""
    vorlage: str=""
    import_file: str = ""
    richt_choice: str = ""
    data_choice: str = ""
    ordner_bild: str = ""
    ordner_video: str = ""
    # init_database: bool = True
    import_stamm: bool = True
    import_haus: bool = True
    import_zustand: bool = True
    import_teilbefahrung: bool = False


class ZustandConfig(ClassObject):
    db: str = ""
    date: str = ""
    showschaedencolumns: int = 2
    abstand_zustandstexte: float = 0.35
    abstand_zustandsbloecke: float = 0.45
    abstand_knoten_anf: float = 0.
    abstand_knoten_1: float = 1.0
    abstand_knoten_2: float = 1.5
    abstand_knoten_end: float = 4.0
    versatz_anschlusstexte: float = 1.0             # Versatz der Zustandstexte relativ zu den Haltungen
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
    limitdata: bool = True


class Config(ClassObject):
    autokorrektur: bool = True
    epsg: int = 25832
    fangradius: float = 0.1
    max_loops: int = 1000
    mindestflaeche: float = 0.5
    mit_verschneidung: bool = True
    fotoRootPath: str = ""                          # Hauptpfad. Ergibt zusammen mit dem Attribut fotos.datei den Pfad zum Foto
    videoRootPath: str = ""                         # Hauptpfad. Ergibt zusammen mit dem Attribut videos.datei den Pfad zum Foto
    fotoPathCurrent: str = ""                       # aktuell vom Anwender ausgewählter absoluter Pfad
    videoPathCurrent: str = ""                      # aktuell vom Anwender ausgewählter absoluter Pfad
    # ---
    adapt: AdaptConfig = AdaptConfig()
    check_export: CheckExport = CheckExport()
    check_import: CheckImport = CheckImport()
    selections: SelectionConfig = SelectionConfig()
    database: DatabaseConfig = DatabaseConfig()
    sync: SyncConfig = SyncConfig()
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
