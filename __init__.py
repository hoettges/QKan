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

import logging, site, os.path
from datetime import datetime as dt

# Aufsetzen des Logging-Systems
logger = logging.getLogger('QKan')
formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s: %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

dnam = dt.today().strftime("%Y%m%d")
fnam = os.path.join(tempfile.gettempdir(),'QKan{}.log'.format(dnam))
fh = logging.FileHandler(fnam)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Warnlevel setzten
logger.setLevel(logging.DEBUG)
ch.setLevel(logging.ERROR)
fh.setLevel(logging.DEBUG)


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Laengsschnitt class from file Laengsschnitt.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .application import Laengsschnitt
    return Laengsschnitt(iface)
