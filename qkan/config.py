import json
import logging
import os
import site
import warnings
from pathlib import Path

log = logging.getLogger("QKan.config")


class ConfigEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class ClassObject:
    def __init__(self, **kwargs):
        annotation_keys = self.__annotations__.keys()

        # Assign values
        for key, value in kwargs.items():
            if key in annotation_keys:
                # Handle classes
                if issubclass(self.__annotations__[key], ClassObject) and isinstance(
                    value, dict
                ):
                    # Try to parse class
                    setattr(self, key, self.__annotations__[key](**value))
                    continue

                # Type does not match annotation
                if type(value) is not self.__annotations__[key]:
                    # TODO: Notify user that setting has been reset/removed
                    if hasattr(self, key):
                        log.warning(
                            f"{self.__class__.__name__}: Replaced setting {key} "
                            f"with default value {getattr(self, key)}, previously {value}"
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

    def __getitem__(self, key):
        warnings.warn(
            f"{self.__class__.__name__}: The dict-like config has been replaced "
            f"with a class, use hasattr() instead.",
            DeprecationWarning,
            2,
        )
        return getattr(self, key)

    def __contains__(self, item):
        warnings.warn(
            f"{self.__class__.__name__}: The dict-like config has been replaced "
            f"with a class, use hasattr() instead.",
            DeprecationWarning,
            2,
        )
        return hasattr(self, item)

    def __setattr__(self, key, value):
        # Allow setting anything in temporary storage
        if hasattr(self, "allow_any"):
            super().__setattr__(key, value)
            return

        # Verify type if in annotation
        if key in self.__annotations__ and type(value) is not self.__annotations__[key]:
            raise TypeError(
                f"{self.__class__.__name__}: Value of {key} ({value}, "
                f"{type(value)}) does not match"
                f" annotation's type ({self.__annotations__[key]})."
            )
        elif key not in self.__annotations__:
            log.warning(
                f"{self.__class__.__name__}: Setting unknown value/key "
                f"combination in config {key}={value} ({type(value)})"
            )
        super().__setattr__(key, value)

    def __str__(self):
        sorted_kv = sorted([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"<{self.__class__.__name__} {' '.join(sorted_kv)}>"

    def __repr__(self):
        return self.__dict__


class TempStorage(ClassObject):
    """
    May be used to save anything, will be written to config file
    """

    __annotations__ = {}
    allow_any = True


class DatabaseConfig(ClassObject):
    he: str = ""
    he_ergebnis: str = ""
    qkan: str = ""
    he_template: str = ""
    type: str = "spatialite"


class DynaConfig(ClassObject):
    autonummerierung: bool = False
    bef_choice: str = "flaechen"  # TODO: Enum ['flaechen', 'tezg']
    dynafile: str = ""
    profile_ergaenzen: bool = True
    prof_choice: str = "profilname"  # TODO: Enum ['profilname', 'profilkey']
    template: str = ""


class LinkFlConfig(ClassObject):
    # Linkflaechen
    auswahltyp: str = "within"  # TODO: Enum ['within', 'overlaps']
    bezug_abstand: str = "kante"  # TODO: Enum ['kante', 'mittelpunkt']
    bufferradius: int = 0
    delete_geom_none: bool = True
    flaechen_abflussparam: list = []
    hal_entw: list = []
    links_in_tezg: bool = True
    suchradius: int = 50


class HEConfig(ClassObject):
    verschneidung: bool = True
    qml_choice: str = "uebh"  # TODO: Enum ['uebh', 'uebvol', 'userqml', 'none']
    qml_file_results: str = ""


class ToolsConfig(ClassObject):
    class RunoffParams(ClassObject):
        # TODO: Implement user choice of hard-coded and custom functions
        itwh: list = [
            "0.8693*log(area(geom))+ 5.6317",
            "pow(18.904*pow(neigkl,0.686)*area(geom), 0.2535*pow(neigkl,0.244))",
        ]
        dyna: list = [
            "0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*0.02 * "
            "(abstand + fliesslaenge) / SQRT(neigung), 0.467)",
            "pow(2*0.10 * (abstand + fliesslaenge) / SQRT(neigung), 0.467)",
        ]
        maniak: list = [
            "0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*0.02 * "
            "(abstand + fliesslaenge) / SQRT(neigung), 0.467)",
            "pow(2*0.10 * (abstand + fliesslaenge) / SQRT(neigung), 0.467)",
            "0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*0.02 * abstand / SQRT(neigung), 0.467)",
            "pow(2*0.10 * abstand / SQRT(neigung), 0.467)",
            "0.02 * pow(abstand, 0.77) * pow(neigung, -0.385) + pow(2*0.02 * fliesslaenge / SQRT(neigung), 0.467)",
            "pow(2*0.10 * fliesslaenge / SQRT(neigung), 0.467)",
        ]

    abflussparameter: list = []
    adapt_db: bool = True
    adapt_forms: bool = True
    adapt_kbs: bool = True
    adapt_selected: str = "alle_anpassen"  # TODO: Enum ['alle_anpassen', 'auswahl_anpassen']
    adapt_table_lookups: bool = True
    apply_qkan_template: bool = True
    fehlende_layer_ergaenzen: bool = True
    logeditor: str = ""
    manningrauheit_bef: float = 0.02
    manningrauheit_dur: float = 0.10
    project_template: str = ""
    qkan_db_update: bool = True
    runoffparamsfunctions: RunoffParams = RunoffParams()
    runoffparamstype_choice: str = "Maniak"  # TODO: Enum? ['iwth', 'dyna', 'Maniak']
    # TODO: Enum ['Speicherkaskade', 'Fliesszeiten', 'Schwerpunktlaufzeit']
    runoffmodeltype_choice: str = "Speicherkaskade"
    update_node_type: bool = True
    zoom_all: bool = True


class Config(ClassObject):
    autokorrektur: bool = True
    epsg: int = 25832
    fangradius: float = 0.1
    mindestflaeche: float = 0.5
    mit_verschneidung: bool = True
    max_loops: int = 1000
    project_file: str = ""
    teilgebiete: list = []
    database: DatabaseConfig = DatabaseConfig()
    dyna: DynaConfig = DynaConfig()
    he: HEConfig = HEConfig()
    linkflaechen: LinkFlConfig = LinkFlConfig()
    tools: ToolsConfig = ToolsConfig()
    check_export: TempStorage = TempStorage()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def save(self):
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
    def load():
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
