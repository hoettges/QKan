import enum
import json
import logging
import os
import site
import warnings
from pathlib import Path

from qkan import enums

log = logging.getLogger("QKan.config")


class ConfigEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, enum.Enum):
            return o.value
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
                if type(value) is not self.__annotations__[key]:
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

    def __getitem__(self, key: str):
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

    def __setattr__(self, key: str, value):
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
                f"{self.__class__.__name__}: Dropping unknown value/key "
                f"combination in config {key}={value} ({type(value)})"
            )
            return
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


class CheckExport(TempStorage):
    pass
    # TODO: Requires additional changes in ExportHE8.
    #  Until then this will simply replicate a TempStorage
    # class CEObj(ClassObject):
    #     init: bool = False
    #     update: bool = True
    #     append: bool = True
    #     delete: bool = True

    # export_abflussparameter: CEObj = CEObj()
    # export_auslaesse: CEObj = CEObj()
    # export_aussengebiete: CEObj = CEObj()
    # export_bodenklassen: CEObj = CEObj()
    # export_einleitdirekt: CEObj = CEObj()
    # export_einleitew: CEObj = CEObj()
    # export_flaechenrw: CEObj = CEObj()
    # export_haltungen: CEObj = CEObj()
    # export_profildaten: CEObj = CEObj()
    # export_pumpen: CEObj = CEObj()
    # export_regenschreiber: CEObj = CEObj()
    # export_rohrprofile: CEObj = CEObj()
    # export_schaechte: CEObj = CEObj()
    # export_speicher: CEObj = CEObj()
    # export_speicherkennlinien: CEObj = CEObj()
    # export_wehre: CEObj = CEObj()
    # import_abflussparameter: CEObj = CEObj()
    # import_auslaesse: CEObj = CEObj()
    # import_aussengebiete: CEObj = CEObj()
    # import_bodenklassen: CEObj = CEObj()
    # import_einleitdirekt: CEObj = CEObj()
    # import_einleitew: CEObj = CEObj()
    # import_haltungen: CEObj = CEObj()
    # import_profildaten: CEObj = CEObj()
    # import_pumpen: CEObj = CEObj()
    # import_regenschreiber: CEObj = CEObj()
    # import_rohrprofile: CEObj = CEObj()
    # import_schaechte: CEObj = CEObj()
    # import_speicher: CEObj = CEObj()
    # import_speicherkennlinien: CEObj = CEObj()
    # import_wehre: CEObj = CEObj()

    def __str__(self):
        return "<CheckExport *hidden in __str__*>"


class DatabaseConfig(ClassObject):
    qkan: str = ""
    type: str = "spatialite"


class DynaConfig(ClassObject):
    autonummerierung: bool = False
    bef_choice: enums.BefChoice = enums.BefChoice.FLAECHEN
    file: str = ""
    prof_choice: enums.ProfChoice = enums.ProfChoice.PROFILNAME
    profile_ergaenzen: bool = True
    template: str = ""


class LinkFlConfig(ClassObject):
    # Linkflaechen
    auswahltyp: enums.AuswahlTyp = enums.AuswahlTyp.WITHIN
    bezug_abstand: enums.BezugAbstand = enums.BezugAbstand.KANTE
    bufferradius: int = 0
    delete_geom_none: bool = True
    links_in_tezg: bool = True
    suchradius: int = 50


class SelectionConfig(ClassObject):
    abflussparameter: list = []
    flaechen_abflussparam: list = []
    hal_entw: list = []
    teilgebiete: list = []


class HEConfig(ClassObject):
    database: str = ""
    database_erg: str = ""
    database_erg_fb: str = ""
    database_fb: str = ""
    qml_choice: enums.QmlChoice = enums.QmlChoice.UEBH
    qml_file_results: str = ""
    template: str = ""
    template_fb: str = ""


class ProjectConfig(ClassObject):
    file: str = ""
    save_file: bool = True
    template: str = ""


class AdaptConfig(ClassObject):
    add_missing_layers: bool = True
    database: bool = True
    forms: bool = True
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

        def __str__(self):
            return "<RunoffParams *hidden in __str__*>"

    apply_qkan_template: bool = True
    logeditor: str = ""
    manningrauheit_bef: float = 0.02
    manningrauheit_dur: float = 0.10
    runoffmodeltype_choice: enums.RunOffModelType = enums.RunOffModelType.SPEICHERKASKADE
    runoffparamsfunctions: RunoffParams = RunoffParams()
    runoffparamstype_choice: enums.RunOffParamsType = enums.RunOffParamsType.MANIAK


class Config(ClassObject):
    autokorrektur: bool = True
    epsg: int = 25832
    fangradius: float = 0.1
    max_loops: int = 1000
    mindestflaeche: float = 0.5
    mit_verschneidung: bool = True
    # ---
    adapt: AdaptConfig = AdaptConfig()
    check_export: CheckExport = CheckExport()
    selections: SelectionConfig = SelectionConfig()
    database: DatabaseConfig = DatabaseConfig()
    dyna: DynaConfig = DynaConfig()
    he: HEConfig = HEConfig()
    linkflaechen: LinkFlConfig = LinkFlConfig()
    project: ProjectConfig = ProjectConfig()
    tools: ToolsConfig = ToolsConfig()

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
