import os

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem
from qgis.PyQt.uic import loadUiType
from qkan.database.dbfunc import DBConnection
from qkan import QKan
from qkan.utils import get_logger

from qkan.database.qkan_utils import get_database_QKan

form_class, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'res/qkan_schadensliste.ui'))

logger = get_logger("QKan.tools.zeige_schaeden")

class ShowHaltungsschaeden(QDialog, form_class):
    """Zeigt Haltungsschäden an"""
    def __init__(self, haltnam: str, schoben: str, schunten: str, untersuch_id: int = None):
        super(ShowHaltungsschaeden, self).__init__()

        self.haltnam = haltnam
        self.schoben = schoben
        self.schunten = schunten
        self.untersuch_id = untersuch_id
        self.showschaedencolumns = QKan.config.zustand.showschaedencolumns      # evtl. ergänzen: Eingabe unter Optionen

        self.setupUi(self)

        self.iface = QKan.instance.iface

        self.show_selected()

        self.showlist()

        self.pb_showAll.clicked.connect(self.show_all)

    def show_all(self):
        """Aktualisiert die Schadensliste"""
        self.showschaedencolumns = 100
        self.showlist()

    def showlist(self):
        """Textfelder zur Haltung füllen und Liste mit den Haltungsschäden  erstellen"""

        database_qkan, epsg = get_database_QKan()

        with DBConnection(dbname=database_qkan, epsg=epsg) as db_qkan:
            if not db_qkan.connected:
                logger.error_user(
                    msg="Fehler im STRAKAT-Import"
                        f"QKan-Datenbank {QKan.config.database.qkan} wurde nicht gefunden!\nAbbruch!",
                )
                raise Exception("Abbruch!")

            sql = """
                SELECT
                    hoehe, breite, untersucher,
                    wetter, bewertungsart, laenge, baujahr
                FROM haltungen_untersucht
                WHERE
                    haltnam = :haltnam AND
                    schoben = :schoben AND
                    schunten = :schunten
                """
            params = {'haltnam': self.haltnam, 'schoben': self.schoben, 'schunten': self.schunten}

            if not db_qkan.sql(sql=sql, stmt_category="Anzeige Zustandsdaten (1)", parameters=params):
                logger.error('Fehler in Anzeige Zustandsdaten (1)')
                return False

            data = db_qkan.fetchone()

            (hoehe, breite, untersucher, wetter, bewertungsart, laenge, baujahr) = data

            self.tf_haltnam.setText(f'{self.haltnam}')
            self.tf_schoben.setText(f'{self.schoben}')
            self.tf_schunten.setText(f'{self.schunten}')
            self.tf_hoehe.setText(f'{hoehe}')
            self.tf_breite.setText(f'{breite}')
            self.tf_untersucher.setText(f'{untersucher}')
            self.tf_wetter.setText(f'{wetter}')
            self.tf_bewertungsart.setText(f'{bewertungsart}')
            self.tf_laenge.setText(f'{laenge}')
            self.tf_baujahr.setText(f'{baujahr}')

            # Auflisten aller Untersuchungstage. Kriterium muss identisch mit nachfolgenden
            # Abfragen sein, damit nur Untersuchungstage mit Untersuchungsdaten berücksichtigt werden

            sql = """
                SELECT hu.untersuchtag
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
                      coalesce(uh.untersuchrichtung, hu.untersuchrichtung) IS NOT NULL AND
                      hu.haltnam = :haltnam AND
                      hu.schoben = :schoben AND
                      hu.schunten = :schunten
                GROUP BY hu.untersuchtag
                ORDER BY hu.untersuchtag DESC
                LIMIT :anzahl
                """
            params = {'haltnam': self.haltnam, 'schoben': self.schoben, 'schunten': self.schunten,
                      'anzahl': self.showschaedencolumns}

            if not db_qkan.sql(sql=sql, stmt_category="Anzeige Zustandsdaten (2)", parameters=params):
                logger.error('Fehler in Anzeige Zustandsdaten (2)')
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
                WITH ud AS (
                    SELECT
                        hu.untersuchtag, hu.untersuchrichtung, 
                        hu.haltnam, hu.schoben, hu.schunten, hu.untersuchtag, hu.laenge
                    FROM untersuchdat_haltung AS uh
                    JOIN haltungen_untersucht AS hu
                    ON hu.haltnam = uh.untersuchhal AND
                       hu.schoben = uh.schoben AND
                       hu.schunten = uh.schunten AND
                       hu.untersuchtag = uh.untersuchtag
                    WHERE hu.haltnam IS NOT NULL AND
                          hu.untersuchtag IS NOT NULL AND
                          coalesce(hu.laenge, 0) > 0.05 AND
                          uh.station IS NOT NULL AND
                          abs(uh.station) < 10000 AND
                          coalesce(uh.untersuchrichtung, hu.untersuchrichtung) IS NOT NULL AND
                          hu.haltnam = :haltnam AND
                          hu.schoben = :schoben AND
                          hu.schunten = :schunten
                    GROUP BY hu.untersuchtag
                    ORDER BY hu.untersuchtag DESC
                    LIMIT :anzahl
                ),
                hs AS (
                    SELECT
                        hu.haltnam, hu.schoben, hu.schunten,
                        CASE coalesce(uh.untersuchrichtung, hu.untersuchrichtung)
                            WHEN 'gegen Fließrichtung' THEN round(hu.laenge - uh.station, 2)
                            WHEN 'in Fließrichtung'    THEN round(uh.station, 2)
                                                       ELSE round(uh.station, 2) END        AS station,
                        uh.kuerzel
                        FROM untersuchdat_haltung AS uh
                        JOIN ud AS hu
                        ON hu.haltnam = uh.untersuchhal AND
                           hu.schoben = uh.schoben AND
                           hu.schunten = uh.schunten AND
                           hu.untersuchtag = uh.untersuchtag
                        WHERE hu.haltnam IS NOT NULL AND
                              hu.untersuchtag IS NOT NULL AND
                              coalesce(hu.laenge, 0) > 0.05 AND
                              uh.station IS NOT NULL AND
                              abs(uh.station) < 10000 AND
                              coalesce(uh.untersuchrichtung, hu.untersuchrichtung) IS NOT NULL AND
                              hu.haltnam = :haltnam AND
                              hu.schoben = :schoben AND
                              hu.schunten = :schunten
                        GROUP BY station, uh.kuerzel
                ),
                zd AS (
                SELECT
                    uh.pk,
                    uh.untersuchhal                                                     AS haltnam, 
                    uh.schoben,
                    uh.schunten,
                    uh.untersuchtag,
                    uh.kuerzel,
                    uh.kuerzel || 
                        CASE  WHEN substr(uh.kuerzel, 1, 1) IN ('A', 'B', 'C', 'D') AND 
                                   substr(uh.kuerzel, 2, 1) IN ('A', 'B', 'C', 'D')
                        THEN
                            substr('  ' || printf('%s', uh.charakt1), 2) ||
                            substr('  ' || printf('%s', uh.charakt2), 2)
                        ELSE '' END                                                     AS text,
                    CASE coalesce(uh.untersuchrichtung, hu.untersuchrichtung)
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
                          coalesce(hu.laenge, 0) > 0.05 AND
                          uh.station IS NOT NULL AND
                          abs(uh.station) < 10000 AND
                          coalesce(uh.untersuchrichtung, hu.untersuchrichtung) IS NOT NULL AND
                          hu.haltnam = :haltnam AND
                          hu.schoben = :schoben AND
                          hu.schunten = :schunten
                    GROUP BY hu.untersuchtag, round(station, 3), uh.kuerzel
                )
                SELECT
                    hs.station,
                    zd.text
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
            params = {'haltnam': self.haltnam, 'schoben': self.schoben, 'schunten': self.schunten,
                      'anzahl': self.showschaedencolumns}

            if not db_qkan.sql(sql=sql, stmt_category="Anzeige Zustandsdaten (3)", parameters=params):
                logger.error('Fehler in Anzeige Zustandsdaten (3)')
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
                    self.tw_schadenstabelle.setRowHeight(row, 20)
                cell = ("{}".format(elem[1])).replace('None', '')
                self.tw_schadenstabelle.setItem(row, col + 1, QTableWidgetItem(cell))

    def show_selected(self):
        """Setzt einen Filter auf ausgewählte Haltungen_untersucht"""
        splitstr = ' AND untersuchhal = '
        layername = 'Untersuchungsdaten Haltung'
        project = QgsProject.instance()
        layer = project.mapLayersByName(layername)[0]
        # layer = iface.activeLayer()
        # layer.source()
        ren = layer.renderer()
        if ren.type() != 'RuleRenderer':
            logger.warning("Fehler: Der Layer 'Haltungen untersucht' enthält keine regelbasierenden Symbole"
                           "\nAktualisieren Sie das Projekt oder bearbeiten den Layer entsprechend.")
            return False
        try:
            root_rule = ren.rootRule()
        except BaseException as e:
            logger.error("Fehler: Der Layer 'Haltungen untersucht' enthält keine regelbasierenden Symbole")
            raise Exception(f"{self.__class__.__name__}")

        for child in root_rule.children():
            rule = root_rule.takeChild(child)
            kat = rule.filterExpression()
            ruleexpressions = kat.split(splitstr, 1)
            if len(ruleexpressions) == 2:
                baserule, fil = ruleexpressions
            elif  len(ruleexpressions) == 1:
                baserule = ruleexpressions[0]
            else:
                baserule = None
                logger.error('QKan-Fehler in ruleexpressions')
            logger.info(f'Ausgewählte Haltung_untersucht: {self.untersuch_id}')
            if self.untersuch_id is None:
                filter = baserule
            else:
                filter = baserule + splitstr + f"'{self.haltnam}' AND ID = {self.untersuch_id}"
            rule.setFilterExpression(filter)
            root_rule.appendChild(rule)
        #    layer.setRenderer(renderer)                            # notwendig?
        layer.triggerRepaint()
        self.iface.layerTreeView().refreshLayerSymbology(layer.id())

if __name__ == '__main__':
    form = ShowHaltungsschaeden('74115531', '74115531', '74115529')
    form.show()
