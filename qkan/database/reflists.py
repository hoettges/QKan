# -*- coding: utf-8 -*-
"""Referenzlisten zum Export in die verschiedenen Simulationsprogramme
   Bisher definiert:
    - HYSTEM-EXTRAN (he)
"""

# flaechen.abflusstyp
def abflusstypen(simprog):
    abflusstypen =  {u'he': {u'Speicherkaskade': 0, u'Fliesszeiten': 1, u'Schwerpunktlaufzeit': 2},
                      u'kp': {u'Speicherkaskade': 0, u'Fliesszeiten': 1, u'Schwerpunktlaufzeit': 2}
                    }

    if simprog in abflusstypen:
        return abflusstypen[simprog]
    else:
        fehlermeldung(u'Fehler in Modul reflist', u'simprog nicht definiert: {}'.format(simprog))
        return None

