import sys
from importlib import util
from types import NoneType
from typing import List, Union
from unittest import mock

qgis_mocks = [
    "qgis",
    "qgis.core",
    "qgis.utils",
    "qgis.gui",
    "qgis.PyQt",
    "qgis.PyQt.QtCore",
    "qgis.PyQt.QtGui",
    "qgis.PyQt.QtWidgets",
    # Python 3.10?
    "distutils.version",
    "qgsprojectionselectionwidget",
]


def mock_imports(to_ignore: Union[NoneType, List[str]] = None, mock_gui_components=True):

    if not to_ignore and not mock_gui_components:
        return {
            "mocked": [],
            "not_mocked": []
        }
    elif not to_ignore:
        to_ignore = []

    if mock_gui_components:
        for module in qgis_mocks:
            if module == "qgis.PyQt":
                module_mock = mock.MagicMock()
                module_mock.uic.loadUiType.return_value = (mock.MagicMock(), None)
                sys.modules["qgis.PyQt"] = module_mock
            else:
                sys.modules[module] = mock.MagicMock()

    mocked = []
    not_mocked = []

    for module in sorted(set(to_ignore)):
        if module in sys.modules:
            if isinstance(sys.modules[module], mock.MagicMock):
                print(f"mock: {module}")
                mocked.append(module)
            else:
                not_mocked.append(module)
        else:
            try:
                found_module = util.find_spec(module)
            except (ModuleNotFoundError, ArithmeticError):
                found_module = None

            if found_module is not None:
                not_mocked.append(module)
            else:
                sys.modules[module] = mock.MagicMock()
                print(f"mock: {module}")
                mocked.append(module)

    return {
        "mocked": mocked,
        "not_mocked": not_mocked
    }
