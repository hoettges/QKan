# -*- coding: utf-8 -*-
"""Referenzlisten zum Export in die verschiedenen Simulationsprogramme
   Bisher definiert:
    - HYSTEM-EXTRAN (he)
"""

# flaechen.abflusstyp
def abflusstypen(simprog):
    abflusstypen =  {u'he': {u'Direktabfluss': 0, u'Fließzeiten': 1, u'Schwerpunktfließzeit': 2},
                      u'kp': {u'Direktabfluss': 0, u'Fließzeiten': 1, u'Schwerpunktfließzeit': 2}
                    }

    if simprog in abflusstypen:
        return abflusstypen[simprog]
    else:
        fehlermeldung(u'Fehler in Modul reflist', u'simprog nicht definiert: {}'.format(simprog))
        return None

