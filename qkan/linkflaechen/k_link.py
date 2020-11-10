# -*- coding: utf-8 -*-

"""
Import from HE

Aus einer Hystem-Extran-Datenbank im Firebird-Format werden Kanaldaten
in die QKan-Datenbank importiert. Dazu wird eine Projektdatei erstellt,
die verschiedene thematische Layer erzeugt, u.a. eine Klassifizierung
der Schachttypen.
"""

__author__ = "Joerg Hoettges"
__date__ = "September 2016"
__copyright__ = "(C) 2016, Joerg Hoettges"

import logging
from typing import List

from qgis.core import Qgis, QgsMessageLog
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QProgressBar
from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.database.qkan_utils import check_flaechenbilanz, checknames, fehlermeldung
from qkan.linkflaechen.updatelinks import updatelinkfl, updatelinksw

logger = logging.getLogger("QKan.linkflaechen.k_link")

# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Flächen


# noinspection PyArgumentList
def createlinkfl(
    iface: QgisInterface,
    db_qkan: DBConnection,
    liste_flaechen_abflussparam: List[str],
    liste_hal_entw: List[str],
    liste_teilgebiete: List[str],
    links_in_tezg: bool = False,
    mit_verschneidung: bool = False,
    autokorrektur: bool = True,
    flaechen_bereinigen: bool = False,
    suchradius: float = 50.0,
    mindestflaeche: float = 0.5,
    fangradius: float = 0.1,
    bezug_abstand: enums.BezugAbstand = enums.BezugAbstand.KANTE,
) -> bool:
    """
    Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.

    Die Bearbeitung erfolgt in einer zusätzlichen Tabelle 'linkfl'
    Sie wird zunächst aus der Tabelle "flaechen" erstellt, und enthält zusätzlich
    zwei weitere Geo-Attribute:
     gbuf  - Buffer sind die mit einem Buffer erweiterten Flächen
     glink - linkfl sind Verbindungslinien, die von der Fläche zur Haltung zeigen
    zusätzlich wird die zugeordnete Haltung im entsprechenden Attribut verwaltet.

    Änderungen an der Zuordnung erfolgen ausschließlich über die Bearbeitung des
    Grafikobjektes, d.h. über die Verbindungslinie. Beim Export werden alle
    Verknüpfungen über die Attributfelder (!) geprüft und alle Unstimmigkeiten, die
    z. B. durch spätere Änderungen der Verbindungslinie entstanden sind, in den
    Attributfeldern aktualisiert. Grund dafür ist, dass nur in dieser Reihenfolge
    ein schneller Export möglich ist. Der "erste" Export kann dagegen viel mehr
    Zeit benötigen, wenn bei vielen (allen?) Verbindungslinien die Attribute erst
    eingetragen werden müssen.

    Die Tabelle linkfl hat außer dem Primärschlüssel "pk" kein eindeutiges
    Primärschlüsselfeld.

    Das Feld tezg.flnam enthält immer den Namen der betreffenden Haltungsfläche,
    unabhängig davon, ob es sich um eine aufzuteilende Fläche handelt.

    :param iface:
    :param db_qkan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param liste_flaechen_abflussparam: Liste der ausgewählten Abflussparameter für die Flächen
    :param liste_hal_entw: Liste der ausgewählten Entwässerungsarten für die Haltungen
    :param liste_teilgebiete: Liste der ausgewählten Teilgebiete
    :param links_in_tezg: Verbindungslinien nur innerhalb der selben Haltungsfläche
    :param mit_verschneidung: Flächen werden mit Haltungsflächen verschnitten (abhängig von Attribut "aufteilen")
    :param autokorrektur: Vor der Bearbeitung werden automatische einheitliche Flächenbezeichnungen vergeben
    :param flaechen_bereinigen: Vor der Bearbeitung werden die Tabellen "flaechen" und "tezg" mit MakeValid korrigiert
    :param suchradius: Suchradius in der SQL-Abfrage
    :param mindestflaeche: Mindestflächengröße bei Einzelflächen und Teilflächenstücken
    :param fangradius:
    :param bezug_abstand: Bestimmt, ob in der SQL-Abfrage der Mittelpunkt oder die
                    nächste Kante der Fläche berücksichtigt wird
    """

    # Statusmeldung in der Anzeige
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "",
        "Verknüpfungen zwischen Flächen und Haltungen werden hergestellt. Bitte warten...",
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # MakeValid auf Tabellen "flaechen" und "tezg".
    if flaechen_bereinigen:
        sql = """UPDATE flaechen SET geom=MakeValid(geom)"""
        if not db_qkan.sql(sql, "k_link.createlinkfl (1)"):
            del db_qkan
            progress_bar.reset()
            return False
        sql = """UPDATE tezg SET geom=MakeValid(geom)"""
        if not db_qkan.sql(sql, "k_link.createlinkfl (2)"):
            del db_qkan
            progress_bar.reset()
            return False
        # Flächen prüfen und ggfs. Meldung anzeigen
        if not check_flaechenbilanz(db_qkan):
            return False

    # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
    if not checknames(db_qkan, "flaechen", "flnam", "f_", autokorrektur):
        del db_qkan
        return False

    progress_bar.setValue(5)

    # Aktualisierung des logischen Cache

    if not updatelinkfl(
        db_qkan, fangradius, flaechen_bereinigen=False, deletelinkGeomNone=False
    ):
        fehlermeldung(
            "Fehler beim Update der Flächen-Verknüpfungen",
            "Der logische Cache konnte nicht aktualisiert werden.",
        )
        return False

    progress_bar.setValue(20)

    # Kopieren der Flaechenobjekte in die Tabelle linkfl

    lis_einf = [
        ""
    ]  # einfache Flächen. Erstes Element leer, damit beim join ' and ' schon am Anfang eingefügt wird
    lis_teil = [
        ""
    ]  # aufzuteilende Flächen. Erstes Element leer, damit beim join ' and ' schon am Anfang eingefügt wird
    lis_vers = [""]  # dito nur mit anderem Namensraum

    if len(liste_flaechen_abflussparam) == 0:
        pass
        # logger.debug(u'Warnung in Link Flaechen: Keine Auswahl bei Flächen...')
    else:
        lis_einf.append(
            "fl.abflussparameter in ('{}')".format(
                "', '".join(liste_flaechen_abflussparam)
            )
        )
        lis_teil.append(
            "la.abflussparameter in ('{}')".format(
                "', '".join(liste_flaechen_abflussparam)
            )
        )
        lis_vers.append(
            "fl.abflussparameter in ('{}')".format(
                "', '".join(liste_flaechen_abflussparam)
            )
        )

    if len(liste_teilgebiete) != 0:
        lis_einf.append(
            "fl.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        )
        lis_teil.append(
            "tg.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        )
        lis_vers.append(
            "tg.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        )

    ausw_einf = " and ".join(lis_einf)
    ausw_teil = " and ".join(lis_teil)
    ausw_vers = " and ".join(lis_vers)

    # Sowohl Flächen, die nicht als auch die, die verschnitten werden müssen

    # if not checkgeom(dbQK, 'tezg', 'geom', autokorrektur, liste_teilgebiete):
    # del dbQK
    # progress_bar.reset()
    # return False

    # if not checkgeom(dbQK, 'flaechen', 'geom', autokorrektur, liste_teilgebiete):
    # del dbQK
    # progress_bar.reset()
    # return False

    if mit_verschneidung:

        # 1. Nicht zu verschneidende Flächen: aufteilen <> 'ja'
        if links_in_tezg:
            sql = f"""WITH linkadd AS (
                          SELECT fl.flnam, fl.teilgebiet, fl.abflussparameter, fl.geom
                          FROM flaechen AS fl
                          LEFT JOIN linkfl AS lf
                          ON lf.flnam = fl.flnam
                          WHERE (fl.aufteilen <> 'ja' or fl.aufteilen IS NULL) AND
                                lf.pk IS NULL AND area(fl.geom) > {mindestflaeche}{ausw_einf})
                      INSERT INTO linkfl (flnam, tezgnam, teilgebiet, geom)
                      SELECT la.flnam, tg.flnam AS tezgnam, la.teilgebiet, la.geom
                      FROM linkadd AS la
                      INNER JOIN tezg AS tg
                      ON within(PointOnSurface(la.geom),tg.geom){ausw_teil}
                      """

        else:
            sql = f"""WITH linkadd AS (
                          SELECT fl.flnam, fl.teilgebiet, fl.abflussparameter, fl.geom
                          FROM flaechen AS fl
                          LEFT JOIN linkfl AS lf
                          ON lf.flnam = fl.flnam
                          WHERE (fl.aufteilen <> 'ja' or fl.aufteilen IS NULL) AND
                                lf.pk IS NULL AND area(fl.geom) > {mindestflaeche}{ausw_einf})
                      INSERT INTO linkfl (flnam, tezgnam, teilgebiet, geom)
                      SELECT la.flnam, NULL AS tezgnam, la.teilgebiet, la.geom
                      FROM linkadd AS la"""

        if not db_qkan.sql(sql, "QKan_LinkFlaechen (4a)"):
            del db_qkan
            progress_bar.reset()
            return False

        # 1. Zu verschneidende Flächen: aufteilen = 'ja'
        sql = f"""WITH linkadd AS (
                      SELECT fl.flnam, tg.flnam AS tezgnam, fl.teilgebiet, 
                             fl.geom AS geof, tg.geom AS geot
                      FROM flaechen AS fl
                      INNER JOIN tezg AS tg
                      ON intersects(fl.geom, tg.geom) AND fl.geom IS NOT NULL AND tg.geom IS NOT NULL
                      LEFT JOIN linkfl AS lf
                      ON lf.flnam = fl.flnam AND lf.tezgnam = tg.flnam
                      WHERE fl.aufteilen = 'ja' AND
                            lf.pk IS NULL AND area(fl.geom) > {mindestflaeche}{ausw_vers})
                  INSERT INTO linkfl (flnam, tezgnam, teilgebiet, geom)
                  SELECT la.flnam, la.tezgnam, la.teilgebiet, 
                          CastToMultiPolygon(CollectionExtract(intersection(la.geof,la.geot),3)) AS geom
                  FROM linkadd AS la 
                  WHERE geom IS NOT NULL AND 
                        area(geom) > {mindestflaeche}"""

        if not db_qkan.sql(sql, "QKan_LinkFlaechen (4b)"):
            del db_qkan
            progress_bar.reset()
            return False

        # sql = """WITH linkadd AS (
        # SELECT
        # linkfl.pk AS lpk, tezg.flnam AS tezgnam, flaechen.flnam,
        # flaechen.geom
        # FROM flaechen
        # INNER JOIN tezg
        # ON within(centroid(flaechen.geom),tezg.geom)
        # LEFT JOIN linkfl
        # ON linkfl.flnam = flaechen.flnam
        # WHERE ((flaechen.aufteilen <> 'ja' or flaechen.aufteilen IS NULL)
        # and flaechen.geom IS NOT NULL and tezg.geom IS NOT NULL){ausw_einf}
        # UNION
        # SELECT
        # linkfl.pk AS lpk, tezg.flnam AS tezgnam, flaechen.flnam,
        # CastToMultiPolygon(CollectionExtract(intersection(flaechen.geom,tezg.geom),3)) AS geom
        # FROM flaechen
        # INNER JOIN tezg
        # ON intersects(flaechen.geom,tezg.geom)
        # LEFT JOIN linkfl
        # ON linkfl.flnam = flaechen.flnam AND linkfl.tezgnam = tezg.flnam
        # WHERE (flaechen.aufteilen = 'ja'
        # and flaechen.geom IS NOT NULL and tezg.geom IS NOT NULL){ausw_teil})
        # INSERT INTO linkfl (flnam, tezgnam, geom)
        # SELECT flnam, tezgnam, geom
        # FROM linkadd
        # WHERE lpk IS NULL AND area(geom) > {minfl}""".format(ausw_einf=ausw_einf, ausw_teil=ausw_teil, minfl=mindestflaeche)

    else:
        sql = f"""WITH linkadd AS (
                SELECT
                    linkfl.pk AS lpk, fl.flnam, fl.aufteilen, fl.teilgebiet, 
                    fl.geom
                FROM flaechen AS fl
                LEFT JOIN linkfl
                ON linkfl.flnam = fl.flnam
                WHERE ((fl.aufteilen <> 'ja' or fl.aufteilen IS NULL) 
                    AND linkfl.pk IS NULL
                    AND fl.geom IS NOT NULL){ausw_einf})
            INSERT INTO linkfl (flnam, teilgebiet, geom)
            SELECT flnam, teilgebiet, geom
            FROM linkadd
            WHERE area(geom) > {mindestflaeche}"""

        if not db_qkan.sql(sql, "QKan_LinkFlaechen (4c)"):
            del db_qkan
            progress_bar.reset()
            return False

    progress_bar.setValue(60)

    # Jetzt werden die Flächenobjekte mit einem Buffer erweitert und jeweils neu
    # hinzugekommmene mögliche Zuordnungen eingetragen.

    sql = f"UPDATE linkfl SET gbuf = CastToMultiPolygon(buffer(geom,{suchradius})) WHERE linkfl.glink IS NULL"
    if not db_qkan.sql(sql, "createlinkfl (2)"):
        del db_qkan
        progress_bar.reset()
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche.
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen
    # in tlink gefiltert wurden.

    if len(liste_hal_entw) == 0:
        auswha = ""
    else:
        auswha = " AND ha.entwart in ('{}')".format("', '".join(liste_hal_entw))

    if len(liste_teilgebiete) == 0:
        auswlinkfl = ""
    else:
        auswha += " AND  ha.teilgebiet in ('{}')".format("', '".join(liste_teilgebiete))
        auswlinkfl = " AND  linkfl.teilgebiet in ('{}')".format(
            "', '".join(liste_teilgebiete)
        )

    if bezug_abstand == enums.BezugAbstand.MITTELPUNKT:
        bezug = "lf.geom"
    else:
        bezug = "PointonSurface(lf.geom)"

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # tlink enthält alle potenziellen Verbindungen zwischen Flächen und Haltungen mit der jeweiligen Entfernung
    # t2 enthält von diesen Verbindungen nur die Fläche (als pk) und den minimalen Abstand,
    # so dass in der Abfrage nach "update" nur die jeweils nächste Verbindung gefiltert wird.
    # Da diese Abfrage nur für neu zu erstellende Verknüpfungen gelten soll (also noch kein Eintrag
    # im Feld "flaechen.haltnam" -> fl.haltnam -> tlink.linkhal -> t1.linkhal).

    # Varianten ohne und mit Beschränkung der Anbindungslinien auf die Haltungsfläche

    # Tipp: within und intersects schließt Datensätze ohne Geoobjekt ein. Deshalb müssen
    # sie ausgeschlossen werden.

    if links_in_tezg and mit_verschneidung:
        # links_in_tezg funktioniert nur, wenn mit_verschneidung aktiviert ist
        sql = f"""WITH tlink AS
            (SELECT lf.pk AS pk,
                    ha.haltnam, 
                    Distance(ha.geom,{bezug}) AS dist, 
                    ha.geom AS geohal, lf.geom AS geolf
                FROM haltungen AS ha
                INNER JOIN linkfl AS lf
                ON Intersects(ha.geom,lf.gbuf)
                INNER JOIN tezg AS tg
                ON tg.flnam = lf.tezgnam
                WHERE (within(centroid(ha.geom),tg.geom) and lf.glink IS NULL 
                    and ha.geom IS NOT NULL and lf.gbuf IS NOT NULL and tg.geom IS NOT NULL){auswha})
            UPDATE linkfl SET (glink, haltnam) = 
            (   SELECT MakeLine(PointOnSurface(Buffer(t1.geolf, -1.1*{fangradius})),Centroid(t1.geohal)), t1.haltnam
                FROM tlink AS t1
                INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
                ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
                WHERE linkfl.pk = t1.pk AND area(Buffer(t1.geolf, -1.1*{fangradius})) IS NOT NULL)
            WHERE linkfl.glink IS NULL {auswlinkfl}"""
    else:
        sql = f"""WITH tlink AS
            (SELECT lf.pk AS pk,
                    ha.haltnam, 
                    Distance(ha.geom,{bezug}) AS dist, 
                    ha.geom AS geohal, lf.geom AS geolf
                FROM haltungen AS ha
                INNER JOIN linkfl AS lf
                ON Intersects(ha.geom,lf.gbuf)
                WHERE lf.glink IS NULL
                    and ha.geom IS NOT NULL and lf.gbuf IS NOT NULL {auswha})
            UPDATE linkfl SET (glink, haltnam) =  
            (   SELECT MakeLine(PointOnSurface(Buffer(t1.geolf, -1.1*{fangradius})),Centroid(t1.geohal)), t1.haltnam
                FROM tlink AS t1
                INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
                ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
                WHERE linkfl.pk = t1.pk AND area(Buffer(t1.geolf, -1.1*{fangradius})) IS NOT NULL)
            WHERE linkfl.glink IS NULL {auswlinkfl}"""

    logger.debug("\nSQL-3a:\n{}\n".format(sql))

    if not db_qkan.sql(sql, "createlinkfl (5)"):
        del db_qkan
        progress_bar.reset()
        return False

    progress_bar.setValue(80)

    # Löschen der Datensätze in linkfl, bei denen keine Verbindung erstellt wurde, weil die
    # nächste Haltung zu weit entfernt ist.

    sql = """DELETE FROM linkfl WHERE glink IS NULL"""

    if not db_qkan.sql(sql, "QKan_LinkFlaechen (7)"):
        del db_qkan
        progress_bar.reset()
        return False

    db_qkan.commit()

    # Aktualisierung des logischen Cache

    if not updatelinkfl(
        db_qkan, fangradius, flaechen_bereinigen=False, deletelinkGeomNone=False
    ):
        fehlermeldung(
            "Fehler beim Update der Flächen-Verknüpfungen",
            "Der logische Cache konnte nicht aktualisiert werden.",
        )
        del db_qkan
        progress_bar.reset()
        return False

    progress_bar.setValue(100)
    status_message.setText("Fertig!")
    status_message.setLevel(Qgis.Success)

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage("Information", "Verknüpfungen sind erstellt!", level=Qgis.Info)
    QgsMessageLog.logMessage(message="\nVerknüpfungen sind erstellt!", level=Qgis.Info)

    return True


# ------------------------------------------------------------------------------
# Erzeugung der graphischen Verknüpfungen für Direkteinleitungen


def createlinksw(
    iface: QgisInterface,
    db_qkan: DBConnection,
    liste_teilgebiete: List[str],
    suchradius: float = 50.0,
    epsg: int = 25832,
) -> bool:
    """
    Import der Kanaldaten aus einer HE-Firebird-Datenbank und Schreiben in eine QKan-SpatiaLite-Datenbank.
    :param iface:
    :param db_qkan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param liste_teilgebiete: Liste der ausgewählten Teilgebiete
    :param suchradius: Suchradius in der SQL-Abfrage
    :param epsg: Nummer des Projektionssystems
    """

    # ------------------------------------------------------------------------------
    # Die Bearbeitung erfolgt analog zu createlinkfl, mit folgenden Änderungen:
    # - Es gibt keine Auswahl nach Abflussparametern und Entwässerungssystem
    # - Es handelt sich um Punktobjekte anstelle von Flächen.
    #   - Daher entfällt die Option, ob der Abstand auf die Kante oder den
    #     Mittelpunkt bezogen werden soll
    #   - es gibt keine Verschneidung

    # Kopieren der Direkteinleitungen-Punkte in die Tabelle linksw. Dabei wird aus dem Punktobjekt
    # aus einleit ein Flächenobjekt, damit ein Spatialindex verwendet werden kann
    # (für POINT gibt es keinen MBR?)

    # Statusmeldung in der Anzeige
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "",
        "Verknüpfungen zwischen Einleitpunkten und Haltungen werden hergestellt. Bitte warten...",
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    # Aktualisierung des logischen Cache

    if not updatelinksw(db_qkan, deletelinkGeomNone=False):
        fehlermeldung(
            "Fehler beim Update der Einzeleinleiter-Verknüpfungen",
            "Der logische Cache konnte nicht aktualisiert werden.",
        )
        return False

    if len(liste_teilgebiete) != 0:
        auswahl = " AND einleit.teilgebiet in ('{}')".format(
            "', '".join(liste_teilgebiete)
        )
    else:
        auswahl = ""

    sql = f"""INSERT INTO linksw (elnam, teilgebiet, geom)
            SELECT einleit.elnam, einleit.teilgebiet,buffer(einleit.geom,0.5)
            FROM einleit
            LEFT JOIN linksw
            ON linksw.elnam = einleit.elnam
            WHERE linksw.pk IS NULL {auswahl}"""

    # logger.debug(u'\nSQL-2a:\n{}\n'.format(sql))

    if not db_qkan.sql(sql, "QKan_LinkSW (4a)"):
        return False

    progress_bar.setValue(25)

    # Jetzt werden die Direkteinleitungen-Punkte mit einem Buffer erweitert und jeweils neu
    # hinzugekommmene mögliche Zuordnungen eingetragen.
    # Wenn das Attribut "haltnam" vergeben ist, gilt die Fläche als zugeordnet.

    sql = f"""UPDATE linksw SET gbuf = CastToMultiPolygon(buffer(geom,{suchradius})) WHERE linksw.glink IS NULL"""

    if not db_qkan.sql(sql, "QKan_LinkSW (2)"):
        return False

    # Erzeugung der Verbindungslinie zwischen dem Zentroiden der Haltung und dem PointonSurface der Fläche.
    # Filter braucht nur noch für Haltungen berücksichtigt zu werden, da Flächen bereits beim Einfügen
    # in tlink gefiltert wurden.

    if len(liste_teilgebiete) != 0:
        auswahl = " AND  hal.teilgebiet in ('{}')".format(
            "', '".join(liste_teilgebiete)
        )
        auswlin = " AND  linksw.teilgebiet in ('{}')".format(
            "', '".join(liste_teilgebiete)
        )
    else:
        auswahl = ""
        auswlin = ""

    # Erläuterung zur nachfolgenden SQL-Abfrage:
    # tlink enthält alle potenziellen Verbindungen zwischen Flächen und Haltungen mit der jeweiligen Entfernung
    # t2 enthält von diesen Verbindungen nur die Fläche (als pk) und den minimalen Abstand,
    # so dass in der Abfrage nach "update" nur die jeweils nächste Verbindung gefiltert wird.
    # Da diese Abfrage nur für neu zu erstellende Verknüpfungen gelten soll (also noch kein Eintrag
    # im Feld "einleit.haltnam" -> sw.haltnam -> tlink.linkhal -> t1.linkhal).

    sql = f"""WITH tlink AS
            (SELECT sw.pk AS pk,
                    Distance(hal.geom,sw.geom) AS dist, 
                    hal.geom AS geohal, sw.geom AS geosw
                FROM
                    haltungen AS hal
                INNER JOIN
                    linksw AS sw
                ON Intersects(hal.geom,sw.gbuf)
                WHERE sw.glink IS NULL AND hal.ROWID IN
                (   SELECT ROWID FROM SpatialIndex WHERE
                    f_table_name = 'haltungen' AND
                    search_frame = sw.gbuf)
                    and hal.geom IS NOT NULL and sw.gbuf IS NOT NULL {auswahl})
            UPDATE linksw SET glink =  
            (SELECT MakeLine(PointOnSurface(t1.geosw),Centroid(t1.geohal))
            FROM tlink AS t1
            INNER JOIN (SELECT pk, Min(dist) AS dmin FROM tlink GROUP BY pk) AS t2
            ON t1.pk=t2.pk AND t1.dist <= t2.dmin + 0.000001
            WHERE linksw.pk = t1.pk)
            WHERE linksw.glink IS NULL {auswlin}"""

    # logger.debug(u'\nSQL-3a:\n{}\n'.format(sql))

    if not db_qkan.sql(sql, "QKan_LinkSW (5)"):
        return False

    progress_bar.setValue(50)

    # Löschen der Datensätze in linksw, bei denen keine Verbindung erstellt wurde, weil die
    # nächste Haltung zu weit entfernt ist.

    sql = """DELETE FROM linksw WHERE glink IS NULL"""

    if not db_qkan.sql(sql, "QKan_LinkSW (7)"):
        return False

    # Aktualisierung des logischen Cache

    if not updatelinksw(db_qkan, deletelinkGeomNone=False):
        fehlermeldung(
            "Fehler beim Update der Einzeleinleiter-Verknüpfungen",
            "Der logische Cache konnte nicht aktualisiert werden.",
        )
        return False

    progress_bar.setValue(100)
    status_message.setText("Fertig!")
    status_message.setLevel(Qgis.Success)

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage("Information", "Verknüpfungen sind erstellt!", level=Qgis.Info)
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(message="\nVerknüpfungen sind erstellt!", level=Qgis.Info)

    return True


# -------------------------------------------------------------------------------------------------------------


def assigntgeb(
    iface: QgisInterface,
    db_qkan: DBConnection,
    auswahltyp: enums.AuswahlTyp,
    liste_teilgebiete: List[str],
    tablist: List[List[str]],
    autokorrektur: bool,
    flaechen_bereinigen: bool = False,
    bufferradius: float = 0.0,
) -> bool:
    """Ordnet alle Objete aus den in "tablist" enthaltenen Tabellen einer der in "liste_teilgebiete" enthaltenen
       Teilgebiete zu. Falls sich mehrere dieser Teilgebiete überlappen, ist das Resultat zufällig eines von diesen. 
    :param iface:
    :param db_qkan:             Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param auswahltyp:
    :param liste_teilgebiete:   Name des auf die gewählten Tabellen zu übertragenden Teilgebietes

    :param tablist:             Liste der Tabellen, auf die die Teilgebiet "liste_teilgebiete" zu übertragen sind.
    :type tablist:              list of String

    :param autokorrektur:       Option, ob eine automatische Korrektur der Bezeichnungen durchgeführt
                                werden soll. Falls nicht, wird die Bearbeitung mit einer Fehlermeldung
                                abgebrochen.

    :param flaechen_bereinigen: Vor der Bearbeitung werden die Tabellen "flaechen" und "tezg" mit MakeValid korrigiert
    :param bufferradius:

    """

    # Statusmeldung in der Anzeige
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "", "Teilgebiete werden zugeordnet. Bitte warten..."
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    logger.debug("\nbetroffene Tabellen (1):\n{}\n".format(str(tablist)))
    logger.debug("\nbetroffene Teilgebiete (2):\n{}\n".format(str(liste_teilgebiete)))

    # MakeValid auf Tabellen "flaechen" und "tezg".
    if flaechen_bereinigen:
        sql = """UPDATE flaechen SET geom=MakeValid(geom)"""
        if not db_qkan.sql(sql, "k_link.assigntgeb (1)"):
            del db_qkan
            progress_bar.reset()
            return False
        sql = """UPDATE tezg SET geom=MakeValid(geom)"""
        if not db_qkan.sql(sql, "k_link.assigntgeb (2)"):
            del db_qkan
            progress_bar.reset()
            return False
        # Flächen prüfen und ggfs. Meldung anzeigen
        if not check_flaechenbilanz(db_qkan):
            return False

    if not checknames(db_qkan, "teilgebiete", "tgnam", "tg_", autokorrektur):
        del db_qkan
        return False

    if len(liste_teilgebiete) != 0:
        tgnames = "', '".join(liste_teilgebiete)
        auswahl_1 = " AND teilgebiete.tgnam in ('{tgnames}')".format(tgnames=tgnames)
        auswahl_2 = " WHERE teilgebiete.tgnam in ('{tgnames}')".format(tgnames=tgnames)
    else:
        auswahl_1 = ""

    for table, geom in tablist:

        if auswahltyp == enums.AuswahlTyp.WITHIN:
            if bufferradius <= 0.00001:
                sql = f"""
                UPDATE {table} SET teilgebiet = 
                (SELECT teilgebiete.tgnam
                    FROM teilgebiete
                    INNER JOIN {table} AS tt
                    ON within(tt.{geom}, teilgebiete.geom)
                    WHERE tt.pk = {table}.pk
                        and tt.{geom} IS NOT NULL and teilgebiete.geom IS NOT NULL {auswahl_1})
                WHERE {table}.pk IN
                (SELECT {table}.pk
                    FROM teilgebiete
                    INNER JOIN {table}
                    ON within({table}.{geom}, teilgebiete.geom)
                    WHERE {table}.{geom} IS NOT NULL and teilgebiete.geom IS NOT NULL {auswahl_1})
                """
            else:
                sql = f"""
                UPDATE {table} SET teilgebiet = 
                (SELECT teilgebiete.tgnam
                    FROM teilgebiete
                    INNER JOIN {table} AS tt
                    ON within(tt.{geom}, buffer(teilgebiete.geom, {bufferradius}))
                    WHERE tt.pk = {table}.pk
                        and tt.{geom} IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
                WHERE {table}.pk IN
                (SELECT {table}.pk
                    FROM teilgebiete
                    INNER JOIN {table}
                    ON within({table}.{geom}, buffer(teilgebiete.geom, {bufferradius}))
                    WHERE {table}.{geom} IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
                """
        elif auswahltyp == enums.AuswahlTyp.OVERLAPS:
            sql = f"""
            UPDATE {table} SET teilgebiet = 
            (	SELECT teilgebiete.tgnam
                FROM teilgebiete
                INNER JOIN {table} AS tt
                ON intersects(tt.{geom},teilgebiete.geom)
                WHERE tt.pk = {table}.pk
                    and tt.{geom} IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
            WHERE {table}.pk IN
            (	SELECT {table}.pk
                FROM teilgebiete
                INNER JOIN {table}
                ON intersects({table}.{geom},teilgebiete.geom)
                WHERE {table}.{geom} IS NOT NULL and teilgebiete.geom IS NOT NULL{auswahl_1})
            """
        else:
            fehlermeldung(
                "Programmfehler",
                "k_link.assigntgeb: auswahltyp hat unbekannten Fall {}".format(
                    repr(auswahltyp)
                ),
            )
            del db_qkan
            return False

        # logger.debug(u'\nSQL:\n{}\n'.format(sql))
        if not db_qkan.sql(sql, "QKan.k_link.assigntgeb (8)", repeatmessage=True):
            return False

    db_qkan.commit()

    progress_bar.setValue(100)
    status_message.setText("Fertig!")
    status_message.setLevel(Qgis.Success)

    # Karte aktualisieren
    iface.mapCanvas().refreshAllLayers()

    # iface.mainWindow().statusBar().clearMessage()
    # iface.messageBar().pushMessage("Information", "Zuordnung von Haltungen und Flächen ist fertig!", level=Qgis.Info)
    # noinspection PyArgumentList
    QgsMessageLog.logMessage(
        message="\nZuordnung von Haltungen und Flächen ist fertig!", level=Qgis.Info
    )

    return True


# -------------------------------------------------------------------------------------------------------------


def reload_group(iface: QgisInterface, db_qkan: DBConnection, gruppenname: str) -> bool:
    """
    Lädt die unter einem Gruppennamen gespeicherten Teilgebietszuordnungen zurück in die Tabellen
    "haltungen", "schaechte", "flaechen", "tezg", "linkfl", "linksw", "einleit"

    :param iface:
    :param db_qkan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param gruppenname: Bezeichnung der Gruppe, unter der die Teilgebietszuordnungen abgelegt wurden.
    """

    # Statusmeldung in der Anzeige
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "",
        "Teilgebiete werden aus der gewählten Gruppe wiederhergestellt. Bitte warten...",
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    tablist = [
        "haltungen",
        "schaechte",
        "flaechen",
        "linkfl",
        "linksw",
        "tezg",
        "einleit",
    ]

    for table in tablist:
        sql = f"""
        UPDATE {table}
        SET teilgebiet = 
        (   SELECT g.teilgebiet
            FROM gruppen AS g
            WHERE g.grnam = '{gruppenname}' AND
            g.tabelle = '{table}' AND
            {table}.pk = g.pktab)
        WHERE {table}.pk IN
        (   SELECT g.teilgebiet
            FROM gruppen AS g
            WHERE g.grnam = '{gruppenname}' AND
            g.tabelle = '{table}')"""
        # logger.debug(u'reloadgroup.sql: \n{}'.format(sql))

        if not db_qkan.sql(sql, "QKan_LinkFlaechen.reloadgroup (9): \n"):
            return False

    db_qkan.commit()

    progress_bar.setValue(100)
    status_message.setText("Fertig!")
    status_message.setLevel(Qgis.Success)

    return True


# -------------------------------------------------------------------------------------------------------------


def store_group(
    iface: QgisInterface, db_qkan: DBConnection, gruppenname: str, kommentar: str
) -> bool:
    """Speichert die aktuellen Teilgebietszuordnungen der Tabellen 
       "haltungen", "schaechte", "flaechen", "tezg", "linkfl", "linksw", "einleit"
       unter einem neuen Gruppennamen
    :param iface:
    :param db_qkan: Datenbankobjekt, das die Verknüpfung zur QKan-SpatiaLite-Datenbank verwaltet.
    :param gruppenname: Bezeichnung der Gruppe, unter der die Teilgebietszuordnungen abgelegt werden.
    :param kommentar:
    """

    # Statusmeldung in der Anzeige
    progress_bar = QProgressBar(iface.messageBar())
    progress_bar.setRange(0, 100)
    status_message = iface.messageBar().createMessage(
        "", "Teilgebiete werden in der angegebenen Gruppe gespeichert. Bitte warten...",
    )
    status_message.layout().addWidget(progress_bar)
    iface.messageBar().pushWidget(status_message, Qgis.Info, 10)

    tablist = [
        "haltungen",
        "schaechte",
        "flaechen",
        "linkfl",
        "linksw",
        "tezg",
        "einleit",
    ]

    # Abfrage setzt sich aus den mit UNION verbundenen Tabellen aus tablist zusammen...
    sql = f"""
    INSERT INTO gruppen
    (grnam, pktab, teilgebiet, tabelle, kommentar)
    SELECT 
      '{gruppenname}' AS grnam,
      pk AS pktab, 
      teilgebiet AS teilgebiet, 
      'haltungen' AS tabelle, 
      '{kommentar}' AS kommentar
    FROM
      haltungen
    WHERE teilgebiet <> '' And teilgebiet IS NOT NULL
    """

    for table in tablist[1:]:
        sql += f"""UNION
        SELECT 
          '{gruppenname}' AS grnam,
          pk AS pktab, 
          teilgebiet AS teilgebiet, 
          '{table}' AS tabelle, 
          '{kommentar}' AS kommentar
        FROM
          {table}
        WHERE teilgebiet <> '' And teilgebiet IS NOT NULL
        """

    # logger.debug(u'\nSQL-4:\n{}\n'.format(sql))
    # Zusammengesetzte SQL-Abfrage ausführen...

    if not db_qkan.sql(sql, "QKan_LinkFlaechen.savegroup (10)"):
        return False

    db_qkan.commit()

    progress_bar.setValue(100)
    status_message.setText("Fertig!")
    status_message.setLevel(Qgis.Success)

    return True
