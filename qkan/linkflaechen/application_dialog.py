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

from PyQt4 import QtGui, uic

FORM_CLASS_createlinefl, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'resources', 'application_createlinefl.ui'))


class CreatelineflDialog(QtGui.QDialog, FORM_CLASS_createlinefl):
    def __init__(self, parent=None):
        """Constructor."""
        super(CreatelineflDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


FORM_CLASS_createlinesw, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'resources', 'application_createlinesw.ui'))


class CreatelineswDialog(QtGui.QDialog, FORM_CLASS_createlinesw):
    def __init__(self, parent=None):
        """Constructor."""
        super(CreatelineswDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


FORM_CLASS_assigntgeb, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'resources', 'application_assigntgeb.ui'))


class AssigntgebDialog(QtGui.QDialog, FORM_CLASS_assigntgeb):
    def __init__(self, parent=None):
        """Constructor."""
        super(AssigntgebDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


FORM_CLASS_managegroups, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'resources', 'application_managegroups.ui'))


class ManagegroupsDialog(QtGui.QDialog, FORM_CLASS_managegroups):
    def __init__(self, parent=None):
        """Constructor."""
        super(ManagegroupsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
