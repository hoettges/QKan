"""Übernimmt den Startschutz der Berichtsvorlage auch in gespeicherte Layouts."""

from functools import lru_cache
from pathlib import Path
import re
from xml.etree import ElementTree

from qgis.PyQt.QtXml import QDomElement


_SCHUTZ = "if(attribute(@atlas_feature, 'Name') IS NULL, NULL, ("
_LABEL_AUSDRUCK = re.compile(r"\[%(.*?)%\]", re.DOTALL)


@lru_cache(maxsize=1)
def _standardausdruecke():
    vorlage = Path(__file__).resolve().parents[1] / "templates" / "Haltungsbericht.qpt"
    layout = ElementTree.parse(vorlage)
    paare = {}
    for element in layout.iter():
        werte = [element.get("value", "")]
        werte.extend(_LABEL_AUSDRUCK.findall(element.get("labelText", "")))
        for wert in werte:
            if wert.startswith(_SCHUTZ) and wert.endswith("))"):
                original = wert[len(_SCHUTZ):-2]
                paare[original.replace("\r\n", "\n")] = wert
    return paare


def _ersetzen(text):
    return _standardausdruecke().get(text.replace("\r\n", "\n"), text)


class AtlasLayoutBeimLesen:
    """readMapLayer liefert das Projekt-XML, bevor QGIS die Drucklayouts aufbaut."""

    def __init__(self):
        self._layouts = QDomElement()

    def projekt_gelesen(self, *_):
        self._layouts = QDomElement()

    def layer_gelesen(self, layer, element):
        root = element.ownerDocument().documentElement()
        layouts = root.firstChildElement("Layouts")
        if layouts.isNull() or layouts == self._layouts:
            return
        self._layouts = layouts
        layout = layouts.firstChildElement("Layout")
        while not layout.isNull():
            if layout.attribute("name") == "Haltungsbericht":
                self._bericht_anpassen(layout)
            layout = layout.nextSiblingElement("Layout")

    @staticmethod
    def _bericht_anpassen(layout):
        for tag, attribut in (("Option", "value"), ("LayoutItem", "labelText")):
            knoten = layout.elementsByTagName(tag)
            for i in range(knoten.count()):
                element = knoten.at(i).toElement()
                text = element.attribute(attribut)
                if "@atlas_feature" not in text or "aggregate(" not in text:
                    continue
                if attribut == "labelText":
                    neu = _LABEL_AUSDRUCK.sub(lambda m: "[%" + _ersetzen(m[1]) + "%]", text)
                else:
                    neu = _ersetzen(text)
                if neu != text:
                    element.setAttribute(attribut, neu)
