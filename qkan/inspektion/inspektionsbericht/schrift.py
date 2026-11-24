from qgis.PyQt.QtGui import QColor, QFont
from .kompat import versuche


def _textformat(groesse, fett=False, farbe=QColor("black")):
    from qgis.core import QgsTextFormat
    font = QFont("Arial")
    font.setBold(fett)
    font.setPointSizeF(groesse)
    fmt = QgsTextFormat()
    fmt.setFont(font)
    fmt.setSize(groesse)
    versuche(fmt.setSizeUnit, "Qgis.RenderUnit.Points", "QgsUnitTypes.RenderPoints")
    fmt.setColor(farbe)
    return fmt


def _schrift(label, groesse, fett=False, farbe=QColor("black")):
    if hasattr(label, "setTextFormat"):
        label.setTextFormat(_textformat(groesse, fett, farbe))
    else:
        font = QFont("Arial")
        font.setBold(fett)
        font.setPointSizeF(groesse)
        label.setFont(font)
        label.setFontColor(farbe)


