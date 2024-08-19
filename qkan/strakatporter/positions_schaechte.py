# coding: utf-8
__author__ = 'hoettges'
# 18.08.2024 Erstellung

# Dieses Snippet entspricht der Funktion calctextpositions_schaechte. Es kann in das Verzeichnis qkan/strakatporter verschoben 
# werden und dort mit Pycharm im Debug-Modus ausgeführt werden. 

import os, sys
from qkan.database.dbfunc import DBConnection
from qgis.core import QgsGeometry, QgsPoint

import logging, site
from datetime import datetime as dt
from array import array
from shutil import copy2

# Aufsetzen des Logging-Systems
# 1. Sender
logger = logging.getLogger('QKan.positions')

# 2. Empfänger
formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s: %(message)s')
# 2.1 Konsole
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
logger.addHandler(ch)
# 2.2 Datei
dnam = dt.today().strftime("%Y%m%d")
fnam = os.path.join(site.getuserbase(), f'log_positions_{dnam}.log')
fh = logging.FileHandler(fnam)
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# 3. Einstellen der Warn-Level
# 3.1 Warn-Level für die Protokollmeldungen, wirkt wie ein Filter

class QKan:
    class config:
        class xml:
            richt_choice = 'rechts'
        class zustand:
            abstand_zustandstexte = 0.35
            abstand_zustandsbloecke = 0.45
            abstand_knoten_anf = 0
            abstand_knoten_1 = 1.0
            abstand_knoten_2 = 1.5
            abstand_knoten_end = 4.0

logger.setLevel(logging.DEBUG)

def calctextpositions_schaechte(db_qkan, data_hu, data_uh,
                        seite_texte: str = 'rechts', epsg: int = 25832
                        ):
    """Erzeugt die Verbindungslinien zu den Zustandstexten für Schächte. Diese stehen rechts vom
       untersuchten Schacht untereinander
    """

    tdist = QKan.config.zustand.abstand_zustandstexte

    abst = [
        QKan.config.zustand.abstand_knoten_anf,
        QKan.config.zustand.abstand_knoten_end + QKan.config.zustand.abstand_knoten_1,
        QKan.config.zustand.abstand_knoten_end + QKan.config.zustand.abstand_knoten_2,
        QKan.config.zustand.abstand_knoten_end + QKan.config.zustand.abstand_knoten_end,
    ]

    si = len(data_uh)  # Anzahl Untersuchungen
    if si == 0:
        logger.error(
            "Es konnten keine Schadenstexte erzeugt werden. Wahrscheinlich ist ein notwendiges Attribut noch leer",
        )
        return

    pk = data_uh[0][1]                  # pk der aktuellen untersuchten Haltung initialisieren
    ianf = 0
    for iend in range(si + 1):
        if iend < si and data_uh[iend][1] == pk:
            # iend innerhalb eines Blocks der aktuellen pk
            continue

        xa, ya = data_hu[pk]
        xe, ye = (xa, ya - 20.0)
        laenge = 20

        # Koordinaten relativ zur Haltung
        xu = (xe - xa) / laenge
        yu = (ye - ya) / laenge
        xv = -yu
        yv = xu

        ypos = 0.                                       # vertikale Textposition
        for i in range(ianf, iend):
            pk = data_uh[i][0]
            st0 = data_uh[i][2]
            st1 = ypos
            x1 = xa + xu * st0 + xv * abst[0]
            y1 = ya + yu * st0 + yv * abst[0]
            x2 = xa + xu * st0 + xv * abst[1]
            y2 = ya + yu * st0 + yv * abst[1]
            x3 = xa + xu * st1 + xv * abst[2]
            y3 = ya + yu * st1 + yv * abst[2]
            x4 = xa + xu * st1 + xv * abst[3]
            y4 = ya + yu * st1 + yv * abst[3]
            ypos += tdist
            geoobj = QgsGeometry.asWkb(
                QgsGeometry.fromPolyline([QgsPoint(x1, y1), QgsPoint(x2, y2), QgsPoint(x3, y3), QgsPoint(x4, y4)]))
            sql = "UPDATE untersuchdat_schacht SET geom = GeomFromWKB(?, ?) WHERE pk = ? AND geom IS NULL"

            if not db_qkan.sql(sql, 'set_objekt', parameters=(geoobj, epsg, pk,)):
                logger.error(f"Fehler in {sql}")

        # Nächsten Block vorbereiten
        if iend < si:
            ianf = iend
            pk = data_uh[iend][1]

    # logzeilen = ['   uh_pk    hu_pk  station       pa       pe       ma       me       po']
    # for i in range(si):
    #      zeile = f'{data_uh[i][0]:8d} {data_uh[i][1]:8d} {data_uh[i][2]:8.2f} {pa[i]:8.2f} {pe[i]:8.2f} ' \
    #              f'{ma[i]:8.2f} {me[i]:8.2f} {po[i]:8.2f}'
    #     logzeilen.append(zeile)
    #     if i > 200:
    #         break
    # proto = '\n'.join(logzeilen)
    # with open('C:/Projekte/Erftverband/strakat_import/qkan/b240320/logfile.txt', 'w') as logfile:
    #     logfile.write(f'calctextpositions_schaechte: Ergebnis der SQL-Anweisung: \n{proto}')

    db_qkan.commit()

def testprog(dbnam):
    """Rahmenprogramm zum Test der Funktion calctextpositions_schaechte. Liest aus einer Datenbank 
       mit der aus einem Import vorhandenen STRAKAT-Importtabelle t_strakatberichte
       die Stationen, ATV-Kuerzel, ATV-Langtexte, berechnet die Textpositionen (calctextpositions)
       und schreibt diese anschließend in die Tabelle t_strakatberichte"""

    epsg = 25832

    with DBConnection(dbname=dbnam, epsg=epsg) as db_qkan:

        sql = """SELECT
            sc.pk AS id,
            st_x(sc.geop)                AS xsch,
            st_y(sc.geop)                AS ysch
            FROM schaechte_untersucht AS sc
            WHERE sc.schnam IS NOT NULL AND
                  sc.untersuchtag IS NOT NULL
            ORDER BY id"""

        if not db_qkan.sql(
            sql=sql,
            stmt_category="read schaechte_untersucht",
        ):
            logger.error(f"Fehler in {sql}")
            raise Exception("{self.__class__.__name__}: Fehler beim Lesen der Stationen (1)")
        data = db_qkan.fetchall()

        data_hu = {}
        for vals in data:
            data_hu[vals[0]] = vals[1:]
        # logger.debug(f'{data_hu[1]}')
        logger.debug(f'Anzahl Datensätze in calctextpositions_schaechte: {len(data_hu)}')

        sql = """SELECT
            us.pk, su.pk AS id,
            0.0                                 AS station
            FROM untersuchdat_schacht           AS us
            JOIN schaechte_untersucht AS su ON su.schnam = us.untersuchsch AND su.untersuchtag = us.untersuchtag
            WHERE su.schnam IS NOT NULL AND
                  su.untersuchtag IS NOT NULL AND
                  su.geop IS NOT NULL
            GROUP BY su.schnam, su.untersuchtag, us.kuerzel
            ORDER BY id, station, us.pk"""

        if not db_qkan.sql(
            sql, "read untersuchdat_schaechte"
        ):
            logger.error(f"Fehler in {sql}")
            raise Exception("{self.__class__.__name__}: Fehler beim Lesen der Stationen (2)")
        data_uh = db_qkan.fetchall()

        seite_texte = 'rechts'

        layer = 'schaechte'

        calctextpositions_schaechte(
            db_qkan,
            data_hu,
            data_uh,
            seite_texte,
            epsg
        )

        db_qkan.commit()

dbnam = 'C:/projekte/Juelich/qkan/b240818/juelich.sqlite'
copy2('C:/projekte/Juelich/qkan/b240816/juelich.sqlite', dbnam)

testprog(dbnam)































