# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Laengsschnitt
                                 A QGIS plugin
 Plugin für einen animierten Laengsschnitt
                             -------------------
        begin                : 2017-02-16
        copyright            : (C) 2017 by Leon Ochsenfeld
        email                : Ochsenfeld@fh-aachen.de
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
    """Load Laengsschnitt class from file Laengsschnitt.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .application import Application
    return Application(iface)
