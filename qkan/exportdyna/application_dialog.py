# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ExportToKPDialog
                                 A QGIS plugin
 Export sewage system data to Hystem-Extran
                             -------------------
        begin                : 2018-03-03
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Jörg Höttge/FH Aachen
        email                : hoettges@fh-aachen.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "application_exportDYNA.ui")
)


class ExportToKPDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ExportToKPDialog, self).__init__(parent)
        self.setupUi(self)
