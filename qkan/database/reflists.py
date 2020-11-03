# -*- coding: utf-8 -*-
"""Referenzlisten zum Export in die verschiedenen Simulationsprogramme
   Bisher definiert:
    - HYSTEM-EXTRAN (he)
"""

# flaechen.abflusstyp
from typing import Dict, Optional

from .qkan_utils import fehlermeldung


def abflusstypen(simprog: str) -> Optional[Dict[str, int]]:
    typen = {
        "he": {
            "Speicherkaskade": 0,
            "Fliesszeiten": 1,
            "Schwerpunktlaufzeit": 2,
            "Direktabfluss": 0,
            "Schwerpunktfließzeit": 2,
        },
        "kp": {
            "Speicherkaskade": 0,
            "Fliesszeiten": 1,
            "Schwerpunktlaufzeit": 2,
            "Direktabfluss": 0,
            "Schwerpunktfließzeit": 2,
        },
    }

    if simprog in typen:
        return typen[simprog]
    else:
        fehlermeldung(
            "Fehler in Modul reflist", u"simprog nicht definiert: {}".format(simprog)
        )
        return None
