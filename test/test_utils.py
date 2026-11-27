# Script muss mit geladenem Projekt in der Python-Konsole ausgeführt werden
# testprog = 'C:/FHAC/hoettges/Kanalprogramme/QKan/test/test_utils.py'
# exec(open(testprog).read())

import os

from qkan.tools.qkan_utils import loadLayer
from qgis.utils import pluginDirectory
from qkan import enums

loadLayer(
    layerbez='Layer_1',
    table='schaechte',
    geom_column='geom',
)

templatepath = os.path.join(pluginDirectory("qkan"), "templates")
loadLayer(
    layerbez=enums.LAYERBEZ.UEBERSTAUSCHAECHTE,
    gpos=1,
    table='ResultsSch',
    geom_column='geom',
    qmlfile=os.path.join(templatepath, "qml", "ueberstauhaeufigkeit.qml"),
    filter='',
    group=[enums.LAYERBEZ.ERGEBNISSE_GROUP],
)
