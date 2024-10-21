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

from qgis.core import QgsProject

from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import fehlermeldung
from qkan.utils import get_logger

logger = get_logger("QKan.tools.k_dbAdapt")

progress_bar = None


def dbAdapt(
    qkanDB: str,
    projectFile: str = None,
    qkan_project: QgsProject = None,
) -> None:
    """Aktualisiert die QKan-Datenbank, indem die Tabellenstruktur auf den aktuellen Stand
    gebracht wird.

    Voraussetzungen: keine

    :qkanDB:                    Ziel-Datenbank, auf die die Projektdatei angepasst werden soll
    :projectFile:               Zu Erzeugende Projektdatei
    """

    # ------------------------------------------------------------------------------
    # Datenbankverbindungen

    if projectFile:
        qkan_project.setFileName(projectFile)
        qkan_project.write()

    with DBConnection(dbname=qkanDB, qkan_db_update=True) as dbQK:   # Datenbankobjekt zur Aktualisierung öffnen

        if not dbQK.connected:
            errormsg = (
                "Fehler in k_qgsadapt:\n"
                f"QKan-Datenbank {qkanDB} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"
            )
            logger.error(errormsg)
            raise  Exception(f"{__name__}: {errormsg}")

        dbQK.sql("SELECT RecoverSpatialIndex()")  # Geometrie-Indizes bereinigen

    # if projectFile:
    #     qkan_project.clear()
