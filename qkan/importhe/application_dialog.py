# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImportFromHEDialog
                                 A QGIS plugin
 Importiert Kanaldaten aus Hystem-Extran
                             -------------------
        begin                : 2016-10-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Jörg Höttges/FH Aachen
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

FORM_CLASS_import, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'resources', 'application_import.ui'))


class ImportFromHEDialog(QtGui.QDialog, FORM_CLASS_import):
    def __init__(self, parent=None):
        """Constructor."""
        super(ImportFromHEDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS_results, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'resources', 'application_results.ui'))


class ResultsFromHEDialog(QtGui.QDialog, FORM_CLASS_results):
    def __init__(self, parent=None):
        """Constructor."""
        super(ResultsFromHEDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
