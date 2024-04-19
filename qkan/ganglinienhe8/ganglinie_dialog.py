"""
/***************************************************************************
 LaengsschnittDialog
                                 A QGIS plugin
 Plugin für einen animierten Laengsschnitt
                             -------------------
        begin                : 2017-02-16
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Leon Ochsenfeld
        email                : Ochsenfeld@fh-aachen.de
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
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QWidget

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ganglinie_dialog_base.ui")
)


class GanglinieDialog(QDialog, FORM_CLASS):  # type: ignore
    def __init__(self, parent: Optional[QWidget] = None):
        """Constructor."""
        super(GanglinieDialog, self).__init__(parent)
        self.setupUi(self)
