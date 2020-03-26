# -*- coding: utf-8 -*-

"""----------------------------------------------------------------------------------
/***************************************************************************
 k_qgsw
                                 A QGIS plugin
 Transfer von Kanaldaten aus QKan nach SWMM 5.0.1
                              -------------------
                            begin                : 2015-08-10
                            git sha              : $Format:%H$
                            copyright            : (C) 2015 by Jörg Höttges / FH Aachen
                            email                : hoettges@fh-aachen.de
 ***************************************************************************/

 Tool Name:   k_qgsw.py
 Source Name: k_qgsw.py
 Version:     1.0.0
 Date:        29.05.2016
 Author:      Joerg Hoettges
 Required Arguments:

Transfer von Kanaldaten aus QKan nach SWMM 5.0.1


----------------------------------------------------------------------------------"""

import math
import logging

from qkan.database.dbfunc import DBConnection

logger = logging.getLogger("QKan.exportswmm")

progress_bar = None

# --------------------------------------------------------------------------------------------------
# Start des eigentlichen Programms

# MOUSE-Haltungstyp: 1 = Kreis, 2 = Profil (CRS), 3 = Rechteck, 4 = Maulprofil, 5 = Eiprofil, 6 = Quadrat, 7 = "Natural Channel"

ref_profile = {"1": "CIRCULAR", "3":"RECT_CLOSED", "5":"EGG"}

def exportKanaldaten(
    iface,
    databaseQKan,
    templateSwmm,
    ergfileSwmm,
    mit_verschneidung,
    liste_teilgebiete,
):
    """
    :iface:                 QGIS-Interface zur GUI
    :type:                  QgisInterface

    :databaseQKan:         Pfad zur QKan-Datenbank
    :type:                  string

    :templateSwmm:          Vorlage für die zu erstellende SWMM-Datei
    :type:                  string

    :ergfileSwmm:           Ergebnisdatei für SWMM
    :type:                  string

    :mit_verschneidung:     Flächen werden mit Haltungsflächen verschnitten (abhängig von Attribut "aufteilen")
    :type:                  Boolean

    :liste_teilgebiete:     Liste der ausgewählten Teilgebiete
    :type:                  string
    """

    #fortschritt('Start...',0.02)

    # --------------------------------------------------------------------------------------------------
    # Zuordnungstabellen. Profile sind in einer json-Datei gespeichert, die sich auf dem
    # Roaming-Verzeichnis befindet (abrufbar mit site.getuserbase()
    # Andere Tabellen sind in diesem Quellcode integriert, wie z. B. ref_typen

    # Einlesen der Vorlagedatei

    with open(templateSwmm) as swvorlage:
        swdaten = swvorlage.read()

    # Verbindung zur Spatialite-Datenbank mit den Kanaldaten

    dbQK = DBConnection(
        dbname=databaseQKan
    )  # Datenbankobjekt der QKan-Datenbank zum Lesen
    if not dbQK.connected:
        logger.error("""Fehler in exportSwmm:
            QKan-Datenbank {databaseQKan} wurde nicht gefunden oder war nicht aktuell!\nAbbruch!"""
        )
        return None

    # --------------------------------------------------------------------------------------------------
    # Allgemeine Initialisierungen

    datacu = ''          # Datenzeilen für [CURVES]

    # --------------------------------------------------------------------------------------------------
    # [SUBCATCHMENTS]
    # [SUBAREAS]
    # [INFILTRATION]

    #fortschritt('Flaechen...',0.04)

    # Nur Daten fuer ausgewaehlte Teilgebiete
    if len(liste_teilgebiete) != 0:
        auswahl = " AND schaechte.teilgebiet in ('{}')".format(
            "', '".join(liste_teilgebiete)
        )
    else:
        auswahl = ""

    # Verschneidung nur, wenn (mit_verschneidung)
    if mit_verschneidung:
        case_verschneidung = u"""
                CASE WHEN fl.aufteilen IS NULL or fl.aufteilen <> 'ja' THEN fl.geom 
                ELSE CastToMultiPolygon(CollectionExtract(intersection(fl.geom,tg.geom),3)) END AS geom"""
        join_verschneidung = u"""
            LEFT JOIN tezg AS tg
            ON lf.tezgnam = tg.flnam"""
        tezg_verschneidung = u"""area(tg.geom) AS fltezg,"""
    else:
        case_verschneidung = u"fl.geom AS geom"
        join_verschneidung = ""
        tezg_verschneidung = u"0 AS fltezg,"

    # wdistbef ist die mit der (Teil-) Fläche gewichtete Fließlänge zur Haltung für die befestigten Flächen zu
    # einer Haltung,
    # wdistdur entsprechend für die durchlässigen Flächen.

    sql = u"""
        WITH flintersect AS (
            SELECT lf.flnam AS flnam, lf.haltnam AS haltnam, 
                CASE fl.neigkl
                    WHEN 0 THEN 0.5
                    WHEN 1 THEN 2.5
                    WHEN 2 THEN 7.0
                    WHEN 3 THEN 12.0
                    ELSE 20.0
                    END AS neigung, 
                fl.abflussparameter AS abflussparameter, 
                {tezg_verschneidung}
                {case_verschneidung}
            FROM linkfl AS lf
            INNER JOIN flaechen AS fl
            ON lf.flnam = fl.flnam{join_verschneidung}),
        halflaech AS (
            SELECT
                fi.haltnam AS haltnam, 
                coalesce(ap.endabflussbeiwert, 1.0) AS abflussbeiwert, 
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN area(fi.geom)/10000.
                    ELSE 0 END) AS flbef,
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN 0
                    ELSE area(fi.geom)/10000. END) AS fldur,
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN distance(fi.geom,h.geom)*area(fi.geom)/10000.
                           ELSE 0 END) AS wdistbef,
                sum(CASE ap.bodenklasse IS NULL 
                    WHEN 1 THEN 0
                           ELSE distance(fi.geom,h.geom)*area(fi.geom)/10000. END) AS wdistdur,
                sum(area(fi.geom)/10000.) AS flges,
                fi.fltezg AS fltezg,
                distance(fi.geom,h.geom) AS disttezg, 
                sum(neigung*area(fi.geom)/10000.) AS wneigung
            FROM flintersect AS fi
            LEFT JOIN abflussparameter AS ap
            ON fi.abflussparameter = ap.apnam
            INNER JOIN haltungen AS h 
            ON fi.haltnam = h.haltnam
            WHERE area(fi.geom) > {mindestflaeche}{ausw_and}{auswahl}
            GROUP BY fi.haltnam),
        einleitsw AS (
            SELECT haltnam, sum(zufluss) AS zufluss
            FROM einleit
            GROUP BY haltnam
        )
        SELECT 
            d.kanalnummer AS kanalnummer,
            d.haltungsnummer AS haltungsnummer, 
            h.laenge AS laenge,
            so.deckelhoehe AS deckelhoehe, 
            coalesce(h.sohleoben, so.sohlhoehe) AS sohleob,
            coalesce(h.sohleunten, su.sohlhoehe) AS sohleun,
            '0' AS material, 
            {sql_prof1}, 
            h.hoehe*1000. AS profilhoehe, 
            h.ks AS ks, 
            f.flbef*abflussbeiwert AS flbef, 
            f.flges AS flges,
            f.wdistbef/(f.flbef + 0.00000001) AS distbef,
            f.wdistdur/(f.fldur + 0.00000001) AS distdur,
            f.fltezg AS fltezg,
            f.disttezg AS disttezg,
            3 AS abfltyp, 
            e.zufluss AS qzu, 
            0 AS ewdichte, 
            0 AS tgnr, 
            f.wneigung/(f.flges + 0.00000001) AS neigung,
            a.kp_nr AS entwart, 
            0 AS haltyp,
            h.schoben AS schoben, 
            h.schunten AS schunten,
            so.xsch AS xob, 
            so.ysch AS yob
        FROM haltungen AS h
        INNER JOIN dynahal AS d
        ON h.pk = d.pk
        INNER JOIN schaechte AS so
        ON h.schoben = so.schnam
        INNER JOIN schaechte AS su
        ON h.schunten = su.schnam{sql_prof2}
        LEFT JOIN halflaech AS f
        ON h.haltnam = f.haltnam
        LEFT JOIN einleitsw AS e
        ON e.haltnam = h.haltnam
        LEFT JOIN entwaesserungsarten AS a
        ON h.entwart = a.bezeichnung
    """.format(
        mindestflaeche=mindestflaeche,
        ausw_and=ausw_and,
        auswahl=auswahl,
        sql_prof1=sql_prof1,
        sql_prof2=sql_prof2,
        case_verschneidung=case_verschneidung,
        join_verschneidung=join_verschneidung,
        tezg_verschneidung=tezg_verschneidung,
    )

    if not dbQK.sql(sql, u"dbQK: k_qkkp.write12 (1)"):
        return False




    sql = f"""
        SELECT
            f.flnam AS name,
            '1' AS rain_gage,
            f.schnam AS outlet,
            f.aek AS area,
            f.aekbef/aek*100 AS imperv
        FROM
            flaechen AS f
        JOIN
            gebiete AS g
        ON 
            Intersects(f.geom,g.geom){auswahl}
        GROUP BY f.flnam"""

    if not dbQK.sql(sql, "dbQK: k_layersadapt (1)"):
        del dbQK
        return False

    datasc = ''          # Datenzeilen subcatchments
    datasa = ''          # Datenzeilen subareas
    datain = ''          # Datenzeilen infiltration

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ['NULL' if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(' ','_')
        c[2] = c[2].replace(' ','_')

        datasc += '{0:<16s} {1:<16s} {2:<16s} {3:<8.2f} {4:<8.2f} {5:<8.2f} 0.5      0                        \n'.format(c[0],c[1],c[2],c[3],c[4],c[3]**0.5*100.)
        datasa += '{0:<16s} 0.01       0.1        2.50       8.00       25         OUTLET    \n'.format(c[0])
        datain += '{0:<16s} 3.5        0.5        0.26      \n'.format(c[0])

    swdaten = swdaten.replace('{SUBCATCHMENTS}\n',datasc)
    swdaten = swdaten.replace('{SUBAREAS}\n',datasa)
    swdaten = swdaten.replace('{INFILTRATION}\n',datain)

    # --------------------------------------------------------------------------------------------------
    # [DWF]

    #fortschritt('Flaechen...',0.08)
    progress_bar.setValue(20)

    sql = '''SELECT
        f.schnam AS outlet,
        sum(f.ew*g.wverbrauch/86400) AS dwinflowf,
        sum(f.aek*g.ewdichte*wverbrauch/86400) AS dwinflowg
    FROM
        flaechen AS f
    JOIN
        gebiete AS g
    ON 
        Intersects(f.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY f.schnam'''

    cursl.execute(sql)

    datadw = ''          # Datenzeilen dry weather inflow

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ['NULL' if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(' ','_')

        # Schmutzwasserzufluss alternativ aus Flaechen oder Gebieten
        if c[1] != 'NULL':
              dwf = c[1]
        elif c[2] != 'NULL':
              dwf = c[2]
        else:
              dwf = 0.

        datadw += '{0:<16s} FLOW             {1:<10.4f} "Tag_EW"\n'.format(c[0],dwf)

    swdaten = swdaten.replace('{DWF}\n',datadw)

    # --------------------------------------------------------------------------------------------------
    # [JUNCTIONS]
    # [OUTFALLS]
    # [STORAGE]
    # [COORDINATES]

    #fortschritt('Schaechte...',0.30)
    progress_bar.setValue(30)

    sql = '''SELECT
        s.schnam AS name, X(geop) AS xsch, Y(geop) AS ysch, s.sohlhoehe AS elevation, s.deckelhoehe - s.sohlhoehe AS maxdepth,
        u.schoben AS auslassnam,
        p.schoben AS speicher_nam
    FROM
    (  schaechte AS s
    JOIN
        gebiete AS g
    ON 
        (Intersects(s.geop,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')))
    LEFT JOIN
        auslaesse AS u
    ON u.schoben = s.schnam
    LEFT JOIN
        speicher AS p
    ON p.schoben = s.schnam
    GROUP BY s.schnam
    '''
    cursl.execute(sql)

    dataju = ''          # Datenzeilen
    dataou = ''          # Datenzeilen
    datast = ''          # Datenzeilen
    # datacu = ''          # Datenzeilen, ist schon oben initialisiert worden
    dataco = ''          # Datenzeilen

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ['NULL' if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(' ','_')
        c[5] = c[5].replace(' ','_')
        c[6] = c[6].replace(' ','_')

        if c[5] != 'NULL':
              # [OUTFALLS]
              dataou += '{:<16s} {:<10.3f} FREE                        NO                       \n'.format(c[0],c[3])
        elif c[6] != 'NULL':
              # [STORAGE]
              datast += '{:<16s} {:<8.3f} 4          0          TABULAR    sp_{:<24}  0        0       \n'.format(c[0],c[3],c[0])

              # [CURVES]
              if len(datacu) >0:
                      datacu += ';\n'                                                                                # ';' falls schon Datensätze
              datacu += 'sp_{:<13s} Storage    0          500       \n'.format(c[0][:13])
              datacu += 'sp_{:<13s}            5          500       \n'.format(c[0][:13])
        else:
              # [JUNCTIONS]
              dataju += '{:<16s} {:<10.3f} {:<10.3f} 0          0          0         \n'.format(c[0],c[3],c[4])

        # [COORDINATES]
        dataco += '{:<16s} {:<18.3f} {:<18.3f}\n'.format(c[0],c[1],c[2])

    swdaten = swdaten.replace('{JUNCTIONS}\n',dataju)
    swdaten = swdaten.replace('{OUTFALLS}\n',dataou)
    swdaten = swdaten.replace('{STORAGE}\n',datast)
    swdaten = swdaten.replace('{COORDINATES}\n',dataco)

    # --------------------------------------------------------------------------------------------------
    # [CONDUITS]
    # [XSECTIONS]

    #fortschritt('Haltungen...',0.60)
    progress_bar.setValue(40)

    sql = '''SELECT
        h.haltnam AS name, h.schoben AS schoben, h.schunten AS schunten, h.laenge, h.ks, rohrtyp, hoehe, breite
    FROM
        haltungen AS h
    JOIN
        gebiete AS g
    ON 
        Intersects(h.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY h.haltnam'''
    cursl.execute(sql)

    datacd = ''          # Datenzeilen
    dataxs = ''          # Datenzeilen

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ['NULL' if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(' ','_')
        c[1] = c[1].replace(' ','_')
        c[2] = c[2].replace(' ','_')

        datacd += '{:<16s} {:<16s} {:<16s} {:<10.3f} {:<10.3f} 0          0          0          0         \n'.format(c[0],c[1],c[2],c[3],c[4])
        dataxs += '{:<16s} {:<12s} {:<16.3f} {:<10.3f} 0          0          1                    \n'.format(c[0],ref_profile[c[5]],c[6],c[7])

    swdaten = swdaten.replace('{CONDUITS}\n',datacd)
    # XSECTIONS wird erst nach [weirs] geschrieben

    # --------------------------------------------------------------------------------------------------
    # [PUMPS] + [CURVES]

    #fortschritt('Pumpen...',0.70)
    progress_bar.setValue(50)

    sql = '''SELECT
        p.name AS name,
        p.schoben AS schoben,
        p.schunten AS schunten,
        p.typ AS typ,
        p.sohle AS sohle
    FROM
        pumpen AS p
    JOIN
        gebiete AS g
    ON 
        Intersects(p.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY p.name'''
    cursl.execute(sql)

    datapu = ''          # Datenzeilen
    # datacu = ''          # Datenzeilen, ist schon oben initialisiert worden

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ['NULL' if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(' ','_')
        c[1] = c[1].replace(' ','_')
        c[2] = c[2].replace(' ','_')

        datapu += '{:<16s} {:<16s} {:<16s} pu_{:<13s} ON       0        0       \n'.format(c[0],c[1],c[2],c[0][:13])

        if len(datacu) >0:
              datacu += ';\n'                                                                                # ';' falls schon Datensätze
        datacu += 'pu_{:<13s} Pump3      0          0.120     \n'.format(c[0][:13])
        datacu += 'pu_{:<13s}            50         0.000     \n'.format(c[0][:13])

    # d erst am Ende (s.u.)
    swdaten = swdaten.replace('{PUMPS}\n',datapu)

    # --------------------------------------------------------------------------------------------------
    # [WEIRS]
    # [XSECTIONS] zusaetzlich fuer Wehre

    #fortschritt('Wehre...',0.75)
    progress_bar.setValue(60)

    sql = '''SELECT
        w.name AS name,
        w.schoben AS schoben,
        w.schunten AS schunten,
        w.typ AS typ,
        w.schwellenhoehe AS schwellenhoehe,
        w.kammerhoehe AS kammerhoehe,
        w.laenge AS laenge
    FROM
        wehre AS w
    JOIN
        gebiete AS g
    ON 
        Intersects(w.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY w.name'''
    cursl.execute(sql)

    datawe = ''          # Datenzeilen
    # dataxs schon oben initialisiert

    for b in cursl.fetchall():

        # In allen Feldern None durch NULL ersetzen
        c = ['NULL' if el is None else el for el in b]

        # In allen Namen Leerzeichen durch '_' ersetzen
        c[0] = c[0].replace(' ','_')
        c[1] = c[1].replace(' ','_')
        c[2] = c[2].replace(' ','_')

        datawe += '{:<16s} {:<16s} {:<16s} TRANSVERSE   0          3.33       NO       0        0          YES       \n'.format(c[0],c[1],c[2])
        dataxs += '{:<16s} RECT_OPEN    {:<16.3f} {:<10.3f} 0          0         \n'.format(c[0],c[5],c[6])

    swdaten = swdaten.replace('{WEIRS}\n',datawe)
    swdaten = swdaten.replace('{XSECTIONS}\n',dataxs)

    # --------------------------------------------------------------------------------------------------
    # [Polygons]

    #fortschritt('Flaechen...',0.60)
    progress_bar.setValue(70)

    sql = '''SELECT f.flnam, AsText(f.geom) AS punkte FROM flaechen AS f
    JOIN
        gebiete AS g
    ON 
        Intersects(f.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY f.flnam'''

    cursl.execute(sql)

    datave = ''          # Datenzeilen

    for b in cursl.fetchall():

        # In allen Namen Leerzeichen durch '_' ersetzen
        nam = b[0].replace(' ','_')

        # In allen Feldern None durch NULL ersetzen
        c = b[1].replace('MULTIPOLYGON(((','').replace(')))','').split(',')
        for k in c:
              x,y = k.split()
              datave += '{:<16s} {:<18.3f} {:<18.3f}\n'.format(nam,float(x),float(y))

    swdaten = swdaten.replace('{Polygons}\n',datave)


    # --------------------------------------------------------------------------------------------------
    # [RAINGAGES]
    # [SYMBOLS]

    #fortschritt('Regenmesser...',0.92)
    progress_bar.setValue(80)

    sql = '''SELECT f.regnr FROM flaechen AS f
    JOIN
        gebiete AS g
    ON 
        Intersects(f.geom,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')
    GROUP BY f.regnr'''

    cursl.execute(sql)

    datarm = ''          # Datenzeilen
    datasy = ''          # Datenzeilen

    for c in cursl.fetchall():

        datarm += '{:<16d} INTENSITY 1:00     1.0      TIMESERIES TS1             \n'.format(c[0])
        datasy += '{:<16d} 9999.999           9999.999          \n'.format(c[0])

    swdaten = swdaten.replace('{RAINGAGES}\n',datarm)
    swdaten = swdaten.replace('{SYMBOLS}\n',datasy)


    # --------------------------------------------------------------------------------------------------
    # [MAP]

    #fortschritt('Kartenausdehnung...',0.95)
    progress_bar.setValue(90)

    sql = '''SELECT
        min(X(geop)) AS xmin, min(y(geop)) AS ymin, max(X(geop)) AS xmax, max(y(geop)) AS ymax
    FROM
        schaechte AS s
    JOIN
        gebiete AS g
    ON 
        Intersects(s.geop,g.geom) and g.teilgebiet in ('Fa20', 'Fa22', 'Fa23', 'Fa25')'''
    cursl.execute(sql)

    # (entfaellt)

    b = cursl.fetchone()

    # In allen Feldern None durch NULL ersetzen
    c = ['NULL' if el is None else el for el in b]

    data = '{:<10.3f} {:<10.3f} {:<10.3f} {:<10.3f}\n'.format(math.floor((c[0]-200.)/200.)*200.,
                                                              math.floor((c[1]-200.)/200.)*200.,
                                                              math.ceil((c[2]+200.)/200.)*200.,
                                                              math.ceil((c[3]+200.)/200.)*200.)

    swdaten = swdaten.replace('{MAP}\n',data)


    # --------------------------------------------------------------------------------------------------
    # [CURVES]   - wurde in mehreren Abschnitten zusammengestellt, deshalb erst jetzt schreiben

    swdaten = swdaten.replace('{CURVES}\n',datacu)


    # --------------------------------------------------------------------------------------------------
    # Schreiben der inp-Datei

    with open(ergfileSwmm, "w") as swvorlage:
        swvorlage.write(swdaten)

    consl.close()

    #fortschritt('Ende...',1)
    progress_bar.setValue(100)

if __name__ in ('__main__', '__console__'):
    databaseQKan = 'C:/FHAC/Bayernallee/Abschlussarbeiten/Bachelorarbeiten/lippina_jonas_375255/eigene Versuche/qgis/kanalnetz.sqlite'
    templateSwmm = 'C:/FHAC/Bayernallee/Abschlussarbeiten/Bachelorarbeiten/lippina_jonas_375255/eigene Versuche/swmm/kanalvorlage.inp'
    ergfileSwmm = 'C:/FHAC/Bayernallee/Abschlussarbeiten/Bachelorarbeiten/lippina_jonas_375255/eigene Versuche/swmm/netteb.inp'

    main(
        databaseQKan,
        templateSwmm,
        ergfileSwmm,
    )
