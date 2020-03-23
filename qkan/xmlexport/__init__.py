# -*- coding: utf-8 -*-
"""
/***************************************************************************
 xmlexport
                                 A QGIS plugin
 xml
                             -------------------
        begin                : 2018-05-18
        copyright            : (C) 2018 by fhaachen
        email                : @fhaachen
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
    """Load xmlimport class from file xmlimport.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .application import xmlexport
    return xmlexport(iface)
