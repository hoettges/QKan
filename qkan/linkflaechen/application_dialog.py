# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LinkFlaechenToHaltungDialog
                                 A QGIS plugin
 Verknüpft Flächen mit nächster Haltung
                             -------------------
        begin                : 2017-06-12
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Jörg Höttges/FH Aachen
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

FORM_CLASS_assigntgeb, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_assigntgeb.ui'))


class AssigntgebDialog(QDialog, FORM_CLASS_assigntgeb):
    def __init__(self, parent=None):
        """Constructor."""
        super(AssigntgebDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_createlinefl, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_createlinefl.ui'))


class CreatelineflDialog(QDialog, FORM_CLASS_createlinefl):
    def __init__(self, parent=None):
        """Constructor."""
        super(CreatelineflDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_createlinesw, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_createlinesw.ui'))


class CreatelineswDialog(QDialog, FORM_CLASS_createlinesw):
    def __init__(self, parent=None):
        """Constructor."""
        super(CreatelineswDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_updatelinks, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_updatelinks.ui'))


class UpdateLinksDialog(QDialog, FORM_CLASS_updatelinks):
    def __init__(self, parent=None):
        """Constructor."""
        super(UpdateLinksDialog, self).__init__(parent)
        self.setupUi(self)


FORM_CLASS_managegroups, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_managegroups.ui'))


class ManagegroupsDialog(QDialog, FORM_CLASS_managegroups):
    def __init__(self, parent=None):
        """Constructor."""
        super(ManagegroupsDialog, self).__init__(parent)
        self.setupUi(self)
