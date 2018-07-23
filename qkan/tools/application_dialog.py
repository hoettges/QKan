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

FORM_CLASS_qgsadapt, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_qgsadapt.ui'))


class QgsadaptDialog(QtGui.QDialog, FORM_CLASS_qgsadapt):
    def __init__(self, parent=None):
        """Constructor."""
        super(QgsadaptDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS_qkanoptions, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_qkanoptions.ui'))


class QKanOptionsDialog(QtGui.QDialog, FORM_CLASS_qkanoptions):
    def __init__(self, parent=None):
        """Constructor."""
        super(QKanOptionsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS_runoffparams, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'res', 'application_runoffparams.ui'))


class RunoffParamsDialog(QtGui.QDialog, FORM_CLASS_runoffparams):
    def __init__(self, parent=None):
        """Constructor."""
        super(RunoffParamsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
