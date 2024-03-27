import os
import logging

from qgis.core import Qgis
from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QApplication, QDialog, QTableWidgetItem
from qgis.PyQt.uic import loadUiType
from qkan.database.dbfunc import DBConnection
from qkan import QKan

# app = QApplication(sys.argv)
form_class, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'res/qkan_schadensliste.ui'))

logger = logging.getLogger("QKan.tools.zeige_schaeden")

class ShowHaltungsschaeden(QDialog, form_class):
    def __init__(self, haltnam: str, schoben: str, schunten: str):
        super(ShowHaltungsschaeden, self).__init__()

        self.setupUi(self)

        self.showlist(haltnam, schoben, schunten)

        self.tw_schadenstabelle.rb_show_1.clicked.connect(self.recalc_1)
        self.tw_schadenstabelle.rb_show_2.clicked.connect(self.recalc_2)
        self.tw_schadenstabelle.rb_show_3.clicked.connect(self.recalc_3)
        self.tw_schadenstabelle.rb_show_4.clicked.connect(self.recalc_4)
        self.tw_schadenstabelle.rb_show_all.clicked.connect(self.recalc_all)

    def showlist(self, haltnam: str, schoben: str, schunten: str):
        """Textfelder zur Haltung füllen und Liste mit den Haltungsschäden  erstellen"""

        with DBConnection(dbname=QKan.config.database.qkan, epsg=QKan.config.epsg) as db_qkan:
            if not db_qkan.connected:
                self.iface.messageBar().pushMessage(
                    "Fehler im STRAKAT-Import",
                    f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.Critical,
                )
                return False

            sql = """
                SELECT hu.untersuchtag
                FROM haltungen_untersucht AS hu
                WHERE hu.haltnam IS NOT NULL AND
                    hu.untersuchtag IS NOT NULL AND
                    coalesce(hu.laenge, 0) > 0.05 AND
                    hu.haltnam = :haltnam AND
                    hu.schoben = :schoben AND
                    hu.schunten = :schunten
                    GROUP BY hu.untersuchtag
                    ORDER BY hu.untersuchtag DESC
                    LIMIT :anzahl
                """
            params = {'haltnam': haltnam, 'schoben': schoben, 'schunten': schunten, 'anzahl': 5}

            if not db_qkan.sql(sql=sql, stmt_category="Anzeige Zustandsdaten (1)", parameters=params):
                logger.error('Fehler in Anzeige Zustandsdaten (1)')
                return False

            data = db_qkan.fetchall()
            headers = ['Station'] + [el[0] for el in data]
            logger.debug(f'{headers=}')
            ncols = len(headers) - 1
            self.tw_schadenstabelle.setColumnCount(ncols + 1)
            self.tw_schadenstabelle.setHorizontalHeaderLabels(headers)

            for i in range(len(headers)):
                self.tw_schadenstabelle.setColumnWidth(i,70)

            sql = """
                WITH hs AS (
                    SELECT
                        hu.haltnam, hu.schoben, hu.schunten,
                        CASE untersuchrichtung
                            WHEN 'gegen Fließrichtung' THEN round(hu.laenge - uh.station, 2)
                            WHEN 'in Fließrichtung'    THEN round(uh.station, 2)
                                                       ELSE round(uh.station, 2) END        AS station,
                        uh.kuerzel
                        FROM untersuchdat_haltung AS uh
                        JOIN haltungen_untersucht AS hu
                        ON hu.haltnam = uh.untersuchhal AND
                           hu.schoben = uh.schoben AND
                           hu.schunten = uh.schunten AND
                           hu.untersuchtag = uh.untersuchtag
                        WHERE hu.haltnam IS NOT NULL AND
                              hu.untersuchtag IS NOT NULL AND
                              coalesce(laenge, 0) > 0.05 AND
                              uh.station IS NOT NULL AND
                              abs(uh.station) < 10000 AND
                              untersuchrichtung IS NOT NULL AND
                              hu.haltnam = :haltnam AND hu.schoben = :schoben AND hu.schunten = :schunten
                        GROUP BY hu.haltnam, hu.schoben, hu.schunten, station, uh.kuerzel
                ),
                ud AS (
                    SELECT
                        hu.untersuchtag
                    FROM haltungen_untersucht AS hu
                    WHERE hu.haltnam IS NOT NULL AND
                          hu.untersuchtag IS NOT NULL AND
                          coalesce(hu.laenge, 0) > 0.05 AND
                          hu.haltnam = :haltnam AND
                          hu.schoben = :schoben AND
                          hu.schunten = :schunten
                    GROUP BY hu.untersuchtag
                    ORDER BY hu.untersuchtag DESC
                    LIMIT :anzahl
                ),
                zd AS (
                SELECT
                    uh.pk,
                    uh.untersuchhal AS haltnam, 
                    uh.schoben,
                    uh.schunten,
                    uh.untersuchtag,
                    uh.kuerzel,
                    CASE untersuchrichtung
                        WHEN 'gegen Fließrichtung' THEN round(hu.laenge - uh.station, 2)
                        WHEN 'in Fließrichtung'    THEN round(uh.station, 2)
                                                   ELSE round(uh.station, 2) END        AS station
                    FROM untersuchdat_haltung AS uh
                    JOIN haltungen_untersucht AS hu
                    ON hu.haltnam = uh.untersuchhal AND
                       hu.schoben = uh.schoben AND
                       hu.schunten = uh.schunten AND
                       hu.untersuchtag = uh.untersuchtag
                    WHERE hu.haltnam IS NOT NULL AND
                          hu.untersuchtag IS NOT NULL AND
                          coalesce(laenge, 0) > 0.05 AND
                          uh.station IS NOT NULL AND
                          abs(uh.station) < 10000 AND
                          untersuchrichtung IS NOT NULL AND
                          hu.haltnam = :haltnam AND hu.schoben = :schoben AND hu.schunten = :schunten
                    GROUP BY hu.haltnam, hu.untersuchtag, round(station, 3), uh.kuerzel
                )
                SELECT
                    hs.station,
                    zd.kuerzel
                    FROM hs
                    CROSS JOIN ud
                    LEFT JOIN zd
                    ON zd.haltnam = hs.haltnam AND
                       zd.schoben = hs.schoben AND
                       zd.schunten = hs.schunten AND
                       zd.kuerzel = hs.kuerzel AND
                       zd.station = hs.station AND
                       zd.untersuchtag = ud.untersuchtag
                    ORDER BY ud.untersuchtag DESC, hs.station, zd.kuerzel
            """
            params = {'haltnam': haltnam, 'schoben': schoben, 'schunten': schunten, 'anzahl': 5}

            if not db_qkan.sql(sql=sql, stmt_category="Anzeige Zustandsdaten (2)", parameters=params):
                logger.error('Fehler in Anzeige Zustandsdaten (2)')
                return False

            data = db_qkan.fetchall()
            logger.debug(f'Zustandsdaten geladen. Dimension: {len(data)} x {len(data[0])}')

            nrows = len(data) // ncols
            logger.debug(f'Zustandsdaten geladen. Tabellenspalten, -zeilen: {ncols}, {nrows}')

            self.tw_schadenstabelle.setRowCount(nrows)

            for i, elem in enumerate(data):
                row = i % nrows
                col = i // nrows
                if i < nrows:       # Spalten "untersuchtag" und "station" nur beim 1. Mal schreiben
                    cell = "{:.2f}".format(elem[0])
                    self.tw_schadenstabelle.setItem(row, 0, QTableWidgetItem(cell))
                    logger.debug(f'Schreibe {cell} in Zelle {row}, 0')
                    self.tw_schadenstabelle.setRowHeight(row, 20)
                cell = ("{}".format(elem[1])).replace('None', '')
                logger.debug(f'Schreibe {cell} in Zelle {row}, {col + 1}')
                self.tw_schadenstabelle.setItem(row, col + 1, QTableWidgetItem(cell))


if __name__ == '__main__':
    form = ShowHaltungsschaeden('74115531', '74115531', '74115529')
    form.show()
# form.exec_()
# form.close()
# sys.exit(app.exec_())

# exec(open('C:/FHAC/hoettges/Kanalprogramme/k_qkan/k_strakat/snippets/zeige_schaeden.py').read())

