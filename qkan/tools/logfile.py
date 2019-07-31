#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
__author__ = 'hoettges'

import logging
import os.path
import tempfile
from datetime import datetime as dt

def logfile(titel):
    ''' Aufsetzen eines Logging-Systems.
        Die Log-Datei wird in diesem Programm unter dem Namen "fnam" angelegt'''

    logger = logging.getLogger(titel)

    if not logger.hasHandlers() or not logger.handlers:
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
        logger.setLevel(logging.DEBUG)              # DEBUG, ERROR

        # Warnlever der Logging-Protokolle setzen
        ch.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)              # DEBUG, ERROR

        logger.info('Initialisierung logger {} erfolgreich!'.format('QKan.validate'))
    else:
        logger.info('Logger {} ist schon initialisiert'.format('QKan.validate'))
        
    return logger
