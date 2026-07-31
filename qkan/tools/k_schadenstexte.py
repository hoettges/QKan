from qkan import QKan
from qkan.utils import get_logger
from array import array
from qgis.core import QgsGeometry, QgsPoint
from qkan.database.dbfunc import DBConnection

from qgis.utils import iface
from qgis.core import Qgis, QgsCoordinateReferenceSystem, QgsProject

logger = get_logger(f'QKan.{__file__}')


class Schadenstexte:
    """Zusätzliche Funktionen für alle Import-Module, um nach dem Import von 
       Schadensdaten die Textlabel zu erzeugen
    """
    db_qkan: DBConnection = None               # wird in der aufrufenden Klasse festgelegt

    @staticmethod
    def calctextpositions_haltungen(data_hu: dict, data_uh: list,
                                    seite_texte: str = 'rechts', epsg: int = 25832
                                    ):
        """Berechnet in einer internen Tabelle die Textpositionen für die Haltungsschäden.
           Dabei werden zunächst vom Haltungsanfang (pa) sowie dem Haltungsende aus die Textpositionen
           mindestens im Abstand bdist gesetzt. Die endgültigen Textpositionen ergeben sich im Anfangs-
           und Endbereich jeweils aus diesen Werten, dazwischen aus deren Mittelwert.
        """

        # Die folgenden Felder enthalten die Textpositionen einer Haltung. Aus Effizienzgründen wird auf
        # 1000 dimensioniert. Falls das zuwenig ist, muss individuell neu dimensioniert werden.

        tdist = QKan.config.zustand.abstand_zustandstexte
        bdist = QKan.config.zustand.abstand_zustandsbloecke - QKan.config.zustand.abstand_zustandstexte
        maxsj = 1000
        sj = maxsj
        pa = array('d', [0.0] * sj)  # Textposition berechnet mit Haltungsrichtung
        pe = array('d', [0.0] * sj)  # Textposition berechnet gegen Haltungsrichtung
        ma = array('B', [0] * sj)  # markiert den Anfangsbereich, in dem nur pa verwendet wird
        me = array('B', [0] * sj)  # markiert den Endbereich, in dem nur pe verwendet wird
        po = array('d', [0.0] * sj)  # Für ma: pa, für me: pe, sonst: (pa+pe)/2.

        # Abstände der Knickpunkte von der Haltung
        abst = [
            QKan.config.zustand.abstand_knoten_anf,
            QKan.config.zustand.abstand_knoten_1,
            QKan.config.zustand.abstand_knoten_2,
            QKan.config.zustand.abstand_knoten_end,
        ]

        si = len(data_uh)  # Anzahl Untersuchungen
        if si == 0:
            logger.warning("Untersuchungsdaten Haltungen: "
               "Es konnten keine Schadenstexte erzeugt werden. Wahrscheinlich ist ein notwendiges Attribut noch leer"
                         )
            return

        pk = data_uh[0][1]              # pk der aktuellen untersuchten Haltung initialisieren
        ianf = 0                        # markiert den Beginn von Untersuchungsdaten zu einer untersuchten Haltung (pk)
        for iend in range(si + 1):
            if iend < si and data_uh[iend][1] == pk:
                # iend innerhalb eines Blocks der aktuellen untersuchten Haltung (pk)
                continue

            # Hinweis: Nach der Vergrößerung bleiben die Felder so, Zurücksetzen wäre zu umständlich ...
            if iend - ianf > si:
                si = iend - ianf
                pa = array('d', [0.0] * sj)  # Textposition berechnet mit Haltungsrichtung
                pe = array('d', [0.0] * sj)  # Textposition berechnet gegen Haltungsrichtung
                ma = array('B', [0] * sj)  # markiert den Anfangsbereich, in dem nur pa verwendet wird
                me = array('B', [0] * sj)  # markiert den Endbereich, in dem nur pe verwendet wird
                po = array('d', [0.0] * sj)  # Für ma: pa, für me: pe, sonst: (pa+pe)/2.

            pavor = 0
            mavor = 1  # Initialisierung mit 1 = True
            stvor = None        # zum Vergleich mit vorheriger Station
            for i in range(ianf, iend):
                station = data_uh[i][2]
                if i == ianf:
                    dist = 0
                else:
                    # Wenn gleiche Station, dann Abstand tdist, sonst noch bdist dazu
                    dist = (abs(station - stvor) > 0.0001) * bdist + tdist
                ma[i - ianf] = mavor = mavor * (pavor + dist > station - 0.0001)
                pa[i - ianf] = pavor = max(station, pavor + dist)
                stvor = station

            xa, ya, xe, ye = data_hu[pk]
            laenge = ((xe - xa) ** 2. + (ye - ya) ** 2.) ** 0.5

            pevor = laenge - (tdist + bdist)
            mevor = 1  # Initialisierung mit 1 = True
            stvor = None        # zum Vergleich mit vorheriger Station
            for i in range(iend - 1, ianf - 1, -1):
                station = data_uh[i][2]
                if i == iend - 1:
                    dist = 0
                else:
                    # Wenn gleiche Station, dann Abstand tdist, sonst noch bdist dazu
                    dist = (abs(station - stvor) > 0.0001) * bdist + tdist
                me[i - ianf] = mevor = mevor * (pevor - dist < station + 0.0001)
                pe[i - ianf] = pevor = min(station, pevor - dist)
                stvor = station

            for i in range(ianf, iend):
                if ma[i - ianf]:
                    po[i - ianf] = pa[i - ianf]
                elif me[i - ianf]:
                    po[i - ianf] = pe[i - ianf]
                else:
                    po[i - ianf] = (pa[i - ianf] + pe[i - ianf]) / 2.

            # Verbindungsobjekte für diese untersuchte Haltung schreiben

            if laenge > 0.045:
                # Koordinaten relativ zur Haltung
                xu = (xe - xa) / laenge
                yu = (ye - ya) / laenge
                if seite_texte == 'rechts':
                    xv = yu
                    yv = -xu
                else:
                    xv = -yu
                    yv = xu

                for i in range(ianf, iend):
                    pk = data_uh[i][0]
                    st0 = data_uh[i][2]
                    st1 = po[i - ianf]
                    x1 = xa + xu * st0 + xv * abst[0]
                    y1 = ya + yu * st0 + yv * abst[0]
                    x2 = xa + xu * st0 + xv * abst[1]
                    y2 = ya + yu * st0 + yv * abst[1]
                    x3 = xa + xu * st1 + xv * abst[2]
                    y3 = ya + yu * st1 + yv * abst[2]
                    x4 = xa + xu * st1 + xv * abst[3]
                    y4 = ya + yu * st1 + yv * abst[3]
                    geoobj = QgsGeometry.asWkb(
                        QgsGeometry.fromPolyline([QgsPoint(x1, y1), QgsPoint(x2, y2), QgsPoint(x3, y3),
                                                  QgsPoint(x4, y4)]))
                    sql = "UPDATE untersuchdat_haltung SET geom = GeomFromWKB(?, ?) WHERE pk = ? AND geom IS NULL"

                    if not Schadenstexte.db_qkan.sql(sql, 'set_objekt', parameters=(geoobj, epsg, pk,)):
                        logger.error(f"Fehler in {sql}")

            # Nächsten Block vorbereiten
            if iend < si:
                ianf = iend
                pk = data_uh[iend][1]

        Schadenstexte.db_qkan.commit()

    @staticmethod
    def setschadenstexte_haltungen(db_qkan):
        """Textpositionen für Schadenstexte zu Haltungen berechnen"""

        Schadenstexte.db_qkan = db_qkan

        sql = "UPDATE untersuchdat_haltung SET geom = NULL"

        if not Schadenstexte.db_qkan.sql(sql, 'set_objekt', ):
            logger.error(f"Fehler in {sql}")

        logger.debug("Schadenstexte Haltungen werden neu arrangiert ...")

        sql = """SELECT
            hu.pk AS id,
            st_x(pointn(hu.geom, 1))                AS xanf,
            st_y(pointn(hu.geom, 1))                AS yanf,
            st_x(pointn(hu.geom, -1))               AS xend,
            st_y(pointn(hu.geom, -1))               AS yend
            FROM haltungen_untersucht AS hu
            WHERE hu.haltnam IS NOT NULL AND
                  hu.untersuchtag IS NOT NULL
            ORDER BY id"""

        if not db_qkan.sql(
            sql, "read haltungen_untersucht"
        ):
            raise Exception(f"{__class__.__name__}: Fehler beim Lesen der Stationen (1)")
        data = db_qkan.fetchall()

        data_hu = {}
        for vals in data:
            data_hu[vals[0]] = vals[1:]

        sql = """SELECT
            uh.pk, hu.pk AS id,
            CASE hu.untersuchrichtung
                WHEN 'gegen Fließrichtung' THEN min(max(GLength(hu.geom) - uh.station, 0.0), GLength(hu.geom))
                WHEN 'in Fließrichtung'    THEN min(max(uh.station                   , 0.0), GLength(hu.geom))
                                           ELSE NULL END        AS station
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
                  hu.geom IS NOT NULL AND
                  uh.station IS NOT NULL 
            GROUP BY hu.haltnam, hu.untersuchtag, round(station, 3), uh.kuerzel
            ORDER BY id, station"""

        if not db_qkan.sql(
            sql, "read untersuchdat_haltungen"
        ):
            raise Exception(f"{__class__.__name__}: Fehler beim Lesen der Stationen (2)")

        data_uh = db_qkan.fetchall()

        seite_texte = 'rechts'

        Schadenstexte.calctextpositions_haltungen(
            data_hu,
            data_uh,
            seite_texte,
            db_qkan.epsg
        )

        # Nummerieren der Untersuchungen an der selben Haltung "haltungen_untersucht"

        sql = """
            UPDATE haltungen_untersucht
            SET id = unum.row_number
            FROM (
                SELECT
                    hu.pk AS pk, hu.haltnam, 
                    row_number() OVER (PARTITION BY hu.haltnam, hu.schoben, hu.schunten ORDER BY hu.untersuchtag DESC) AS row_number
                FROM haltungen_untersucht AS hu
            ) AS unum
            WHERE haltungen_untersucht.pk = unum.pk
        """

        if not db_qkan.sql(
            sql, "num haltungen_untersucht"
        ):
            raise Exception(f"{__class__.__name__}: Fehler in num haltungen_untersucht")

        # Nummerieren der Untersuchungsdaten "untersuchdat_haltung"

        sql = """
            WITH num AS (
                SELECT
                    hu.haltnam, hu.schoben, hu.schunten, hu.untersuchtag, hu.laenge,
                    row_number() OVER (PARTITION BY hu.haltnam, hu.schoben, hu.schunten ORDER BY hu.untersuchtag DESC) AS row_number
                FROM haltungen_untersucht AS hu
                GROUP BY hu.haltnam, hu.schoben, hu.schunten, hu.untersuchtag, hu.laenge
            )
            UPDATE untersuchdat_haltung
            SET id = uid.id
            FROM (
                SELECT uh.pk AS pk, num.row_number AS id
                FROM untersuchdat_haltung AS uh
                JOIN num
                ON	uh.untersuchhal = num.haltnam AND
                    uh.schoben = num.schoben AND
                    uh.schunten = num.schunten AND
                    uh.untersuchtag = num.untersuchtag AND
                    uh.inspektionslaenge = num.laenge
            ) AS uid
            WHERE untersuchdat_haltung.pk = uid.pk
        """

        if not db_qkan.sql(
            sql, "num untersuchdat_haltung"
        ):
            raise Exception(f"{__class__.__name__}: Fehler in num untersuchdat_haltung")

        db_qkan.commit()

        return True

    @staticmethod
    def calctextpositions_schaechte(data_hu: dict, data_uh: list,
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
            logger.debug("Untersuchungsdaten Schächte: "
                "Es konnten keine Schadenstexte erzeugt werden. Wahrscheinlich ist ein notwendiges Attribut noch leer",
            )
            return

        pk = data_uh[0][1]  # pk der aktuellen untersuchten Haltung initialisieren
        ianf = 0
        for iend in range(si + 1):
            if iend < si and data_uh[iend][1] == pk:
                # iend innerhalb eines Blocks der aktuellen pk
                continue

            laenge = 20.
            xa, ya = data_hu[pk]
            xe, ye = (xa, ya - laenge)

            # Koordinaten relativ zur Haltung
            xu = (xe - xa) / laenge
            yu = (ye - ya) / laenge
            if seite_texte == 'rechts':
                xv = -yu
                yv = xu
            else:
                xv = yu
                yv = -xu

            ypos = 0.  # vertikale Textposition
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

                if not Schadenstexte.db_qkan.sql(sql, 'set_objekt', parameters=(geoobj, epsg, pk,)):
                    logger.error(f"Fehler in {sql}")

            # Nächsten Block vorbereiten
            if iend < si:
                ianf = iend
                pk = data_uh[iend][1]

        Schadenstexte.db_qkan.commit()

    @staticmethod
    def setschadenstexte_schaechte(db_qkan):
        """Textpositionen für Schadenstexte zu Schächten berechnen"""

        Schadenstexte.db_qkan = db_qkan

        sql = "UPDATE untersuchdat_schacht SET geom = NULL"

        if not Schadenstexte.db_qkan.sql(sql, 'set_objekt', ):
            logger.error(f"Fehler in {sql}")

        logger.debug("Schadenstexte Schächte werden neu arrangiert ...")

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
            raise Exception(f"{__class__.__name__}: Fehler beim Lesen der Stationen (1)")
        data = db_qkan.fetchall()

        data_hu = {}
        for vals in data:
            data_hu[vals[0]] = vals[1:]

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
            sql, "read untersuchdat_schacht"
        ):
            raise Exception(f"{__class__.__name__}: Fehler beim Lesen der Stationen (2)")

        data_uh = db_qkan.fetchall()

        seite_texte = 'rechts'

        Schadenstexte.calctextpositions_schaechte(
            data_hu,
            data_uh,
            seite_texte,
            db_qkan.epsg
        )

        # Nummerieren der Untersuchungen an dem selben Schacht "schaechte_untersucht"

        sql = """
            UPDATE schaechte_untersucht
            SET id = unum.row_number
            FROM (
                SELECT
                    su.pk AS pk, su.schnam, 
                    row_number() OVER (PARTITION BY su.schnam ORDER BY su.untersuchtag DESC) AS row_number
                FROM schaechte_untersucht AS su
            ) AS unum
            WHERE schaechte_untersucht.pk = unum.pk
        """

        if not db_qkan.sql(
            sql, "num schaechte_untersucht"
        ):
            raise Exception(f"{__class__.__name__}: Fehler in num schaechte_untersucht")

        # Nummerieren der Untersuchungsdaten "untersuchdat_schacht"

        sql = """
            WITH num AS (
                SELECT
                    su.schnam, su.untersuchtag, 
                    row_number() OVER (PARTITION BY su.schnam ORDER BY su.untersuchtag DESC) AS row_number
                FROM schaechte_untersucht AS su
                GROUP BY su.schnam, su.untersuchtag
            )
            UPDATE untersuchdat_schacht
            SET id = uid.id
            FROM (
                SELECT uh.pk AS pk, num.row_number AS id
                FROM untersuchdat_schacht AS uh
                JOIN num
                ON	uh.untersuchsch = num.schnam AND
                    uh.untersuchtag = num.untersuchtag
            ) AS uid
            WHERE untersuchdat_schacht.pk = uid.pk
        """

        if not db_qkan.sql(
            sql, "num untersuchdat_schacht"
        ):
            raise Exception(f"{__class__.__name__}: Fehler in num untersuchdat_schacht")

        db_qkan.commit()

        return True

    @staticmethod
    def calctextpositions_anschlussleitungen(data_hu: dict, data_uh: list,
                                             seite_texte: str = 'rechts', epsg: int = 25832
                                             ):
        """Berechnet in einer internen Tabelle die Textpositionen für die Sschäden an den Anschlussleitungen.
           Dabei werden zunächst vom Anschlussleitungssanfang (pa) sowie dem Anschlussleitungsende aus die Textpositionen
           mindestens im Abstand bdist gesetzt. Die endgültigen Textpositionen ergeben sich im Anfangs-
           und Endbereich jeweils aus diesen Werten, dazwischen aus deren Mittelwert.
        """

        # Die folgenden Felder enthalten die Textpositionen einer Anschlussleitung. Aus Effizienzgründen wird auf
        # 1000 dimensioniert. Falls das zuwenig ist, muss individuell neu dimensioniert werden.

        tdist = QKan.config.zustand.abstand_zustandstexte
        bdist = QKan.config.zustand.abstand_zustandsbloecke - QKan.config.zustand.abstand_zustandstexte
        maxsj = 1000
        sj = maxsj
        pa = array('d', [0.0] * sj)  # Textposition berechnet in Anschlussleitungsrichtung
        pe = array('d', [0.0] * sj)  # Textposition berechnet gegen Anschlussleitungsrichtung
        ma = array('B', [0] * sj)  # markiert den Anfangsbereich, in dem nur pa verwendet wird
        me = array('B', [0] * sj)  # markiert den Endbereich, in dem nur pe verwendet wird
        po = array('d', [0.0] * sj)  # Für ma: pa, für me: pe, sonst: (pa+pe)/2.

        abst = [
            QKan.config.zustand.abstand_knoten_anf,
            QKan.config.zustand.abstand_knoten_1,
            QKan.config.zustand.abstand_knoten_2,
            QKan.config.zustand.abstand_knoten_end,
        ]

        si = len(data_uh)  # Anzahl Untersuchungen
        if si == 0:
            logger.debug("Untersuchungsdaten Anschlussleitungen: "
                "Es konnten keine Schadenstexte erzeugt werden. Wahrscheinlich ist ein notwendiges Attribut noch leer",
            )
            return

        pk = data_uh[0][1]  # pk der aktuellen untersuchten Anschlussleitung initialisieren
        ianf = 0  # markiert den Beginn von Untersuchungsdaten zu einer untersuchten Anschlussleitung (pk)
        for iend in range(si + 1):
            if iend < si and data_uh[iend][1] == pk:
                # iend innerhalb eines Blocks der aktuellen untersuchten Anschlussleitung (pk)
                continue

            # Hinweis: Nach der Vergrößerung bleiben die Felder so, Zurücksetzen wäre zu umständlich ...
            if iend - ianf > si:
                si = iend - ianf
                pa = array('d', [0.0] * sj)  # Textposition berechnet in Anschlussleitungsrichtung
                pe = array('d', [0.0] * sj)  # Textposition berechnet gegen Anschlussleitungsrichtung
                ma = array('B', [0] * sj)  # markiert den Anfangsbereich, in dem nur pa verwendet wird
                me = array('B', [0] * sj)  # markiert den Endbereich, in dem nur pe verwendet wird
                po = array('d', [0.0] * sj)  # Für ma: pa, für me: pe, sonst: (pa+pe)/2.

            pavor = None
            mavor = 1  # Initialisierung mit 1 = True
            stvor = None        # zum Vergleich mit vorheriger Station
            for i in range(ianf, iend):
                station = data_uh[i][2]
                if i == ianf:
                    dist = 0
                    pavor = station
                else:
                    # Wenn gleiche Station, dann Abstand tdist, sonst noch bdist dazu
                    dist = (abs(station - stvor) > 0.0001) * bdist + tdist
                ma[i - ianf] = mavor = mavor * (pavor + dist > station - 0.0001)
                pa[i - ianf] = pavor = max(station, pavor + dist)
                stvor = station

            xa, ya, xe, ye, laeng_, geom_wkb = data_hu[pk]
            # Länge muss ggfs. auf den Bereich der Stationen erweitert werden
            laenge = max(laeng_, data_uh[iend-1][2] - data_uh[ianf][2])

            versatz = QKan.config.zustand.versatz_anschlusstexte    # Abstand der Texte zur Haltung
            pevor = laeng_ - (tdist + bdist) - versatz
            mevor = 1  # Initialisierung mit 1 = True
            stvor = None        # zum Vergleich mit vorheriger Station
            for i in range(iend - 1, ianf - 1, -1):
                station = data_uh[i][2]
                if i == iend - 1:
                    dist = 0
                else:
                    # Wenn gleiche Station, dann Abstand tdist, sonst noch bdist dazu
                    dist = (abs(station - stvor) > 0.0001) * bdist + tdist
                me[i - ianf] = mevor = mevor * (pevor - dist < station + 0.0001)
                pe[i - ianf] = pevor = min(station, pevor - dist)
                stvor = station

            for i in range(ianf, iend):
                if me[i - ianf]:
                    # auch wenn beides wahr ist ...
                    po[i - ianf] = pe[i - ianf]
                elif ma[i - ianf]:
                    po[i - ianf] = pa[i - ianf]
                else:
                    po[i - ianf] = (pa[i - ianf] + pe[i - ianf]) / 2.

            # Verbindungsobjekte für diese untersuchte Anschlussleitung schreiben

            if laenge > 0.045:
                # Koordinaten relativ zur Anschlussleitung
                laeng_ = ((xe - xa)**2 + (ye - ya)**2)**0.5
                xu = (xe - xa) / laeng_
                yu = (ye - ya) / laeng_
                if seite_texte == 'rechts':
                    xv = yu
                    yv = -xu
                else:
                    xv = -yu
                    yv = xu

                # Abstände der Knickpunkte von der Anschlussleitung, damit diese nicht über die Haltung geschrieben
                # werden. Besonderheit: Zunächst werden die Texte um versatz verschoben, weiter weg wird der Versatz
                # wenn möglich verringert.
                versatz = QKan.config.zustand.versatz_anschlusstexte - (tdist)
                # st1_akt = 0                     # Position des letzten Textes, um sicherzustellen, dass die unter-
                                                # schiedlichen Abstände tdist und bdist erhalten bleiben
                for i in range(ianf, iend):
                    pk = data_uh[i][0]
                    st0 = data_uh[i][2]
                    # st1_vor = st1_akt           # Speichern der vorherigen (nicht versetzten) Position
                    st1 =  po[i - ianf]
                    # Feststellen, ob zwischen der vorherigen und der aktuellen Position ein vergrößerter Abstand vorlag
                    # if st1_akt - st1_vor < tdist + 0.001:
                    #     vdist = tdist
                    # else:
                    #     vdist = tdist + bdist
                    # st1_ver = max(versatz + vdist, st1_akt)
                    # versatz = st1_ver
                    # Der Anfangspunkt liegt auf der Anschlussleitung im Abstand st0 vom Anfangspunkt
                    leitobj = QgsGeometry()
                    leitobj.fromWkb(bytes.fromhex(geom_wkb.hex()))
                    pint = leitobj.interpolate(st0)
                    if pint:
                        p1 = QgsPoint(pint.asPoint())
                    else:
                        x1 = xa + xu * st0 + xv * abst[0]
                        y1 = ya + yu * st0 + yv * abst[0]
                        p1 = QgsPoint(x1, y1)
                    x2 = xa + xu * st0 + xv * abst[1]
                    y2 = ya + yu * st0 + yv * abst[1]
                    x3 = xa + xu * st1 + xv * abst[2]
                    y3 = ya + yu * st1 + yv * abst[2]
                    x4 = xa + xu * st1 + xv * abst[3]
                    y4 = ya + yu * st1 + yv * abst[3]
                    geoobj = QgsGeometry.asWkb(
                        QgsGeometry.fromPolyline([p1, QgsPoint(x2, y2), QgsPoint(x3, y3), QgsPoint(x4, y4)]))
                    sql = "UPDATE untersuchdat_anschlussleitung SET geom = GeomFromWKB(?, ?) WHERE pk = ? AND geom IS NULL"

                    if not Schadenstexte.db_qkan.sql(sql, 'set_objekt', parameters=(geoobj, epsg, pk,)):
                        logger.error(f"Fehler in {sql}")

            # Nächsten Block vorbereiten
            if iend < si:
                ianf = iend
                pk = data_uh[iend][1]

        Schadenstexte.db_qkan.commit()

    @staticmethod
    def setschadenstexte_anschlussleitungen(db_qkan):
        """Textpositionen für Schadenstexte zu Anschlussleitungen berechnen"""

        Schadenstexte.db_qkan = db_qkan

        sql = "UPDATE untersuchdat_anschlussleitung SET geom = NULL"

        if not Schadenstexte.db_qkan.sql(sql, 'set_objekt', ):
            logger.error(f"Fehler in {sql}")

        logger.debug("Schadenstexte Anschlussleitungen werden neu arrangiert ...")

        sql = """SELECT
            hu.pk AS id,
            st_x(pointn(hu.geom, 1))                AS xanf,
            st_y(pointn(hu.geom, 1))                AS yanf,
            st_x(pointn(hu.geom, -1))               AS xend,
            st_y(pointn(hu.geom, -1))               AS yend,
            GLength(hu.geom)                        AS laenge,
            AsBinary(hu.geom) 						AS geom_wkb
            FROM anschlussleitungen_untersucht AS hu
            WHERE hu.leitnam IS NOT NULL AND
                  hu.untersuchtag IS NOT NULL
            ORDER BY id"""

        if not db_qkan.sql(
                sql, "read anschlussleitungen_untersucht"
        ):
            raise Exception(f"{__class__.__name__}: Fehler beim Lesen der Stationen (1)")
        data = db_qkan.fetchall()

        data_hu = {}
        for vals in data:
            data_hu[vals[0]] = vals[1:]

        sql = """SELECT
            uh.pk, hu.pk AS id,
            CASE hu.untersuchrichtung
                WHEN 'gegen Fließrichtung' THEN GLength(hu.geom) - uh.station
                WHEN 'in Fließrichtung'    THEN uh.station
                                           ELSE uh.station END        AS station
            FROM untersuchdat_anschlussleitung AS uh
            JOIN anschlussleitungen_untersucht AS hu
            ON hu.leitnam = uh.untersuchleit AND
               hu.schoben = uh.schoben AND
               hu.schunten = uh.schunten AND
               hu.untersuchtag = uh.untersuchtag
            WHERE hu.leitnam IS NOT NULL AND
                  hu.untersuchtag IS NOT NULL AND
                  coalesce(laenge, 0) > 0.05 AND
                  uh.station IS NOT NULL AND
                  hu.geom IS NOT NULL AND
                  abs(uh.station) < 10000 AND
                  hu.untersuchrichtung IS NOT NULL
            GROUP BY hu.leitnam, hu.untersuchtag, round(station, 3), uh.kuerzel
            ORDER BY id, station"""

        if not db_qkan.sql(
                sql, "read untersuchdat_anschlussleitungen"
        ):
            raise Exception(f"{__class__.__name__}: Fehler beim Lesen der Stationen (2)")

        data_uh = db_qkan.fetchall()

        seite_texte = 'rechts'

        Schadenstexte.calctextpositions_anschlussleitungen(
            data_hu,
            data_uh,
            seite_texte,
            db_qkan.epsg
        )

        # Nummerieren der Untersuchungen an der selben Anschlussleitung "anschlussleitungen_untersucht"

        sql = """
            UPDATE anschlussleitungen_untersucht
            SET id = unum.row_number
            FROM (
                SELECT
                    hu.pk AS pk, hu.leitnam, 
                    row_number() OVER (PARTITION BY hu.leitnam, hu.schoben, hu.schunten 
                                       ORDER BY hu.untersuchtag DESC) AS row_number
                FROM anschlussleitungen_untersucht AS hu
            ) AS unum
            WHERE anschlussleitungen_untersucht.pk = unum.pk
        """

        if not db_qkan.sql(
                sql, "num anschlussleitungen_untersucht"
        ):
            raise Exception(f"{__class__.__name__}: Fehler in num anschlussleitungen_untersucht")

        # Nummerieren der Untersuchungsdaten "untersuchdat_anschlussleitung"

        sql = """
            WITH num AS (
                SELECT
                    hu.leitnam, hu.schoben, hu.schunten, hu.untersuchtag, hu.laenge,
                    row_number() OVER (PARTITION BY hu.leitnam, hu.schoben, hu.schunten 
                                       ORDER BY hu.untersuchtag DESC) AS row_number
                FROM anschlussleitungen_untersucht AS hu
                GROUP BY hu.leitnam, hu.schoben, hu.schunten, hu.untersuchtag, hu.laenge
            )
            UPDATE untersuchdat_anschlussleitung
            SET id = uid.id
            FROM (
                SELECT uh.pk AS pk, num.row_number AS id
                FROM untersuchdat_anschlussleitung AS uh
                JOIN num
                ON	uh.untersuchleit = num.leitnam AND
                    uh.schoben = num.schoben AND
                    uh.schunten = num.schunten AND
                    uh.untersuchtag = num.untersuchtag AND
                    uh.inspektionslaenge = num.laenge
            ) AS uid
            WHERE untersuchdat_anschlussleitung.pk = uid.pk
        """

        if not db_qkan.sql(
                sql, "num untersuchdat_anschlussleitung"
        ):
            raise Exception(f"{__class__.__name__}: Fehler in num untersuchdat_anschlussleitung")

        db_qkan.commit()

        return True
