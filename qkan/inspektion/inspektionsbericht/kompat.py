# planauskunft/kompat.py
"""
Kompatibilität zwischen QGIS-Versionen.

Ab QGIS 3.40 prüfen die Python-Bindungen Enum-Typen streng; manche alten Kurzformen
(z.B. QgsPalLayerSettings.OverPoint) zeigen dann auf ein falsches Enum. Deshalb werden
Enum-Werte hier über mehrere mögliche Pfade gesucht (neue API zuerst) und nacheinander
ausprobiert.
"""


def kandidaten(*pfade):
    """Enum-Werte zu mehreren möglichen Pfaden, z.B. 'Qgis.LabelPlacement.OverPoint'."""
    from qgis import core
    werte = []
    for pfad in pfade:
        obj = core
        try:
            for teil in pfad.split("."):
                obj = getattr(obj, teil)
        except AttributeError:
            continue
        werte.append(obj)
    return werte


def versuche(aufruf, *pfade):
    """Ruft aufruf(wert) mit dem ersten Enum-Wert auf, den diese QGIS-Version akzeptiert."""
    letzter = None
    for wert in kandidaten(*pfade):
        try:
            aufruf(wert)
            return True
        except (TypeError, ValueError, AttributeError) as e:
            letzter = e
    print(f"[PLANAUSKUNFT] Enum nicht gesetzt ({pfade[0] if pfade else '?'}): {letzter}")
    return False


def wert(*pfade):
    """Erster vorhandener Enum-Wert (ohne Typprüfung)."""
    w = kandidaten(*pfade)
    if not w:
        raise AttributeError(f"Kein Enum gefunden: {pfade}")
    return w[0]
