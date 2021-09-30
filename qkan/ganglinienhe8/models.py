# -*- coding: utf-8 -*-
import sys
from typing import Dict, List, Union


class SliderMode:
    Forward = 1
    Pause = 0
    Backward = -1


class Type:
    Error = 0
    Selection = 1


class LayerType:
    Schacht = 0
    Haltung = 1
    Wehr = 2
    Pumpe = 3


if sys.version_info >= (3, 8):
    from typing import TypedDict

    class SchachtInfo(TypedDict):
        sohlhoehe: float
        deckelhoehe: float

    class HaltungInfo(TypedDict):
        schachtoben: str
        schachtunten: str
        laenge: float
        sohlhoeheoben: float
        sohlhoeheunten: float
        querschnitt: float

    class HaltungenStruct(TypedDict):
        haltungen: List[str]
        schaechte: List[str]
        schachtinfo: Dict[str, SchachtInfo]
        haltunginfo: Dict[str, HaltungInfo]


else:
    HaltungenStruct = Dict[str, Union[List[str], Dict[str, Union[str, float]]]]
