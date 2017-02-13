# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Gangliniengrafik
                                 A QGIS plugin
 Dieses Plugin erzeugt Ganglininen von Kanalnetzen
                             -------------------
        begin                : 2017-02-09
        copyright            : (C) 2017 by Michael Gesenhues
        email                : Gesenhues@fh-aachen.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Gangliniengrafik class from file Gangliniengrafik.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mod import Gangliniengrafik
    return Gangliniengrafik(iface)
