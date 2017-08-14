# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PervSum
                                 A QGIS plugin
 Bilanziert befestigte Flaechenanteile zu Haltungsflaechen
                             -------------------
        begin                : 2016-09-19
        copyright            : (C) 2016 by Joerg Hoettges/FH Aachen
        email                : hoettges@fh-aachen.de
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

import logging
import os.path
import tempfile
from datetime import datetime as dt

# Aufsetzen des Logging-Systems
logger = logging.getLogger('QKan')

if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s: %(message)s')

    # Consolen-Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File-Handler
    dnam = dt.today().strftime("%Y%m%d")
    fnam = os.path.join(tempfile.gettempdir(), 'QKan{}.log'.format(dnam))
    fh = logging.FileHandler(fnam)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Warnlevel des Logging-Systems setzten
    logger.setLevel(logging.DEBUG)

    # Warnlever der Logging-Protokolle setzen
    ch.setLevel(logging.ERROR)
    fh.setLevel(logging.DEBUG)

    logger.info('Initialisierung logger erfolgreich!')
else:
    logger.info('Logger ist schon initialisiert')


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PervSum class from file PervSum.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    # from .perv_sum import PervSum
    # return PervSum(iface)
    pass
