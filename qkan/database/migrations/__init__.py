import dataclasses
import importlib
import pkgutil
from distutils.version import LooseVersion
from types import ModuleType
from typing import Callable, List, Optional

from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

logger = get_logger("QKan.database.migrations")


@dataclasses.dataclass(init=True)
class Migration:
    version: LooseVersion
    run: Callable[[DBConnection], bool]
    name: str


def parse_migration(module: ModuleType) -> Optional[Migration]:
    if not isinstance(getattr(module, "VERSION", None), str):
        logger.error("Migration %s is missing the VERSION tag.", module.__name__)
        return None

    # Parse and check version for int-yness
    version = LooseVersion(getattr(module, "VERSION", None))
    if not len(version.version) > 0 or not isinstance(version.version[0], int):
        logger.error(
            "Could not parse version of %s or the version is not an int.",
            module.__name__,
        )
        return None

    # Check for existence of run function
    if not callable(getattr(module, "run", None)):
        logger.error("Could not find migration function in %s.", module.__name__)
        return None

    # Check for proper parameters
    run = getattr(module, "run")
    if (
        len(run.__annotations__.keys()) != 2
        or list(run.__annotations__.keys()) != ["dbcon", "return"]
        or list(run.__annotations__.values()) != [DBConnection, bool]
    ):
        logger.error(
            "Migration function of %s does not have the required parameter scheme. Found: %s",
            module.__name__,
            run.__annotations__,
        )
        return None

    return Migration(name=module.__name__.split(".")[-1], version=version, run=run)


def find_migrations(version: LooseVersion) -> Optional[List[Migration]]:
    migrations = []
    for importer, modname, ispkg in pkgutil.iter_modules(
        __path__, prefix=__name__ + "."
    ):
        try:
            migration_module = importlib.import_module(modname)
            migration = parse_migration(migration_module)

            # Migration could not be verified to have the necessary fields
            if migration is None:
                raise Exception(
                    f"Migration {modname} does not conform with the current migration "
                    "standards, please notify the maintainers."
                )

            # Migration is valid and is newer than our current version
            if migration is not None and migration.version > version:
                migrations.append(migration)

        except ImportError:
            logger.exception("Failed to load migration, stopping.")
            raise

    logger.info("Found %s migration(s) to run", len(migrations))
    return migrations
