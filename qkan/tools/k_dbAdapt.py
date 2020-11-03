# -*- coding: utf-8 -*-

"""

  k_dbAdapt.py
  ============
  
  Aktualsisierung der QKan-Datenbank
  
  | Dateiname            : k_dbAdapt.py
  | Date                 : Juli 2020
  | Copyright            : (C) 2020 by Joerg Hoettges
  | Email                : hoettges@fh-aachen.de
  | git sha              : $Format:%H$
  
  This program is free software; you can redistribute it and/or modify   
  it under the terms of the GNU General Public License as published by   
  the Free Software Foundation; either version 2 of the License, or      
  (at your option) any later version.

"""

__author__ = "Joerg Hoettges"
__date__ = "Juli 2020"
__copyright__ = "(C) 2020, Joerg Hoettges"

import logging

from qgis.core import Qgis, QgsProject
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung

logger = logging.getLogger(u"QKan.tools.k_dbAdapt")

progress_bar = None


def dbAdapt(
    qkanDB: str, projectFile: str, qkan_project: QgsProject,
):
    """Aktualisiert die QKan-Datenbank, indem die Tabellenstruktur auf den aktuellen Stand
    gebracht wird.

    Voraussetzungen: keine

    :qkanDB:                    Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :type qkanDB:               String

    :projectFile:               Zu Erzeugende Projektdatei
    :type projectFile:          String

    :returns:                   Statusmeldung
    """

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    if projectFile:
        qkan_project.setFileName(projectFile)
        qkan_project.write()

    dbQK = DBConnection(
        dbname=qkanDB, qkan_db_update=True
    )  # Datenbankobjekt zur Aktualisierung öffnen

    if not dbQK.connected:
        fehlermeldung(
            u"Fehler in k_qgsadapt:\n",
            u"QKan-Datenbank {:s} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!".format(
                qkanDB
            ),
        )
        return None

    dbQK.updateversion()
    # Datenbankverbindungen schliessen

    del dbQK

    qkan_project.clear()
