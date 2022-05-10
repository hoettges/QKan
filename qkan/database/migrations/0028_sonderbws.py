import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.2.29"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Ergänze verschiedene Haltungstypen, die alle in der Tabelle haltungen gespeichert werden.
    """

    # Alle Tabellen erneuern, in denen createdat vorkommt

    views = [
        "haltungen_data", "haltungen_untersucht_data", "untersuchdat_haltung_data",
        "anschlussleitungen_data", "schaechte_data", "schaechte_untersucht_data",
        "untersuchdat_schacht_data", "pumpen_data", "wehre_data", "tezg_data",
        "v_linkfl_check", "v_flaechen_ohne_linkfl", "v_flaechen_check",
        "v_tezg_check", "v_linkfl_redundant", "v_linksw_redundant",
        ]
    
    for view in views:
        sql = f"DROP VIEW {view}"
        if not dbcon.sql(sql, ignore=True):
            logger.warning(f"Fehler bei Migration zu Version {VERSION}: VIEW {view} konnte nicht gelöscht werden.")
            # return False

    dbcon.commit()

    # triggers are deleted together with the related views ...
    # triggers = [
    #     "haltungen_insert_clipboard", "haltungen_untersucht_insert_clipboard",
    #     "untersuchdat_haltung_insert_clipboard", "anschlussleitungen_insert_clipboard",
    #     "schaechte_insert_clipboard", "schaechte_untersucht_insert_clipboard",
    #     "untersuchdat_schacht_insert_clipboard", "pumpen_insert_clipboard",
    #     "wehre_insert_clipboard", "tezg_insert_clipboard",
    #     ]
    #
    # for trigger in triggers:
    #     sql = f"DROP TRIGGER {trigger}"
    #     if not dbcon.sql(sql):
    #         logger.error(f"Fehler bei Migration zu Version {VERSION}: TRIGGER {trigger} konnte nicht gelöscht werden.")
    #         return False

    if not dbcon.alter_table(
        "haltungen",
        [
            "haltnam TEXT,",
            "schoben TEXT,",
            "schunten TEXT,",
            "hoehe REAL,                                    -- Profilhoehe (m)",
            "breite REAL,                                   -- Profilbreite (m)",
            "laenge REAL,                                   -- abweichende Haltungslänge (m)",
            "sohleoben REAL,                                -- abweichende Sohlhöhe oben (m)",
            "sohleunten REAL,                               -- abweichende Sohlhöhe unten (m)",
            "teilgebiet TEXT,",
            "profilnam TEXT DEFAULT 'Kreisquerschnitt',",
            "entwart TEXT DEFAULT 'Regenwasser',",
            "material TEXT,",
            "ks REAL DEFAULT 1.5,                           -- abs. Rauheit (Prandtl-Colebrook)",
            "haltungstyp TEXT,",
            "simstatus TEXT DEFAULT 'vorhanden',",
            "kommentar TEXT,",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP,",
            "xschob REAL,",
            "yschob REAL,",
            "xschun REAL,",
            "yschun REAL",
        ],
        [   "qzu",
            "rohrtyp",
            "deckeloben",
            "deckelunten",
        ],
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Hinzufügen von haltungstyp und material zu Tabelle haltungen fehlgeschlagen"
        )

    dbcon.commit()

    # Daten von Wehren und Pumpen in Tabelle 'haltungen' als Sonderelemente übertragen
    sqllis = [
        """INSERT INTO haltungen (
            haltnam, schoben, schunten,
            hoehe,
            haltungstyp, 
            simstatus,
            kommentar, createdat, 
            geom)
        SELECT 
            pnam AS haltnam, 
            schoben, schunten,
            0.3 AS hoehe,                   /* nur fuer Laengsschnitt */
            'Pumpe' AS haltungstyp,
            simstatus,
            kommentar, createdat, 
            geom
            FROM pumpen
        """,
        """INSERT INTO haltungen (
            haltnam, schoben, schunten,
            hoehe,
            sohleoben, sohleunten,
            haltungstyp, 
            simstatus,
            kommentar, createdat, 
            geom)
        SELECT 
            wnam AS haltnam, 
            schoben, schunten,
            0.5 AS hoehe,                   /* nur fuer Laengsschnitt */
            schwellenhoehe AS sohleoben,    /* nur fuer Laengsschnitt */
            schwellenhoehe AS sohleunten,   /* nur fuer Laengsschnitt */
            'Wehr' AS haltungstyp,
            simstatus,
            kommentar, createdat, 
            geom
            FROM wehre
        """,
    ]
    for sql in sqllis:
        if not dbcon.sql(sql):
            logger.error(f"Fehler 2 bei Migration zu Version {VERSION}")
            return False

    dbcon.commit()

    sql = "DELETE FROM abflusstypen WHERE abflusstyp IN ('Direktabfluss', 'Schwerpunktfließzeit')"
    if not dbcon.sql(sql):
        logger.error(f"Fehler 3 bei Migration zu Version {VERSION}")
        return False

    dbcon.commit()

    # sqllis = [
    #     f"""CREATE TRIGGER IF NOT EXISTS untersuchdat_haltung_insert_clipboard
    #                     INSTEAD OF INSERT ON untersuchdat_haltung_data FOR EACH ROW
    #                   BEGIN
    #                     INSERT INTO untersuchdat_haltung
    #                       (untersuchhal, untersuchrichtung, schoben, schunten, id, videozaehler, inspektionslaenge, station, timecode, video_offset, kuerzel,
    #                         charakt1, charakt2, quantnr1, quantnr2, streckenschaden, streckenschaden_lfdnr, pos_von, pos_bis, foto_dateiname, film_dateiname, ordner_bild, ordner_video, richtung, createdat, geom)
    #                     SELECT
    #                       new.untersuchhal, new.untersuchrichtung, new.schoben, new.schunten,
    #                         new.id, new.videozaehler, new.inspektionslaenge , new.station, new.timecode, new.video_offset, new.kuerzel,
    #                         new.charakt1, new.charakt2, new.quantnr1, new.quantnr2, new.streckenschaden, new.streckenschaden_lfdnr, new.pos_von, new.pos_bis, new.foto_dateiname, new.film_dateiname, new.ordner_bild, new.ordner_video, new.richtung,
    #                         coalesce(new.createdat, CURRENT_TIMESTAMP),
    #                         CASE
    #                         WHEN (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))+2*((-1)/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))+2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         WHEN (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge)),(ST_Y(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/haltung.laenge))-2*((-1)/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/haltung.laenge))-2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         WHEN (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))-2*((-1)/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))-2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         WHEN (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> haltung.schoben AND new.schunten <> haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = haltung.schoben AND new.schunten = haltung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge)), (ST_Y(schun.geop)+(new.station*COALESCE(haltung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*MAX(haltung.laenge/new.inspektionslaenge,1)*(ST_X(schob.geop)-ST_X(schun.geop))/haltung.laenge))+2*((-1)/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*MAX(haltung.laenge/new.inspektionslaenge,1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/haltung.laenge))+2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         ELSE NULL
    #                         END
    #                     FROM
    #                     schaechte AS schob,
    #                     schaechte AS schun,
    #                     haltungen AS haltung
    #                     WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten AND haltung.haltnam = new.untersuchhal
    #                     UNION
    #                     SELECT
    #                     new.untersuchhal, new.untersuchrichtung, new.schoben, new.schunten,
    #                         new.id, new.videozaehler, new.inspektionslaenge , new.station, new.timecode, new.video_offset, new.kuerzel,
    #                         new.charakt1, new.charakt2, new.quantnr1, new.quantnr2, new.streckenschaden, new.streckenschaden_lfdnr, new.pos_von, new.pos_bis, new.foto_dateiname, new.film_dateiname, new.ordner_bild, new.ordner_video, new.richtung,
    #                         coalesce(new.createdat, CURRENT_TIMESTAMP),
    #                         CASE
    #                         WHEN (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/leitung.laenge)),(ST_Y(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/leitung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/leitung.laenge))+2*((-1)/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/leitung.laenge))+2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         WHEN (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) >=0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'in Fließrichtung' AND ST_X(schun.geop)-ST_X(schob.geop) < 0 AND ST_Y(schun.geop)-ST_Y(schob.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/leitung.laenge)),(ST_Y(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/leitung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schun.geop)-ST_X(schob.geop))/leitung.laenge))-2*((-1)/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), (ST_Y(schob.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schun.geop)-ST_Y(schob.geop))/leitung.laenge))-2*(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop)))/sqrt(1+(((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))*((ST_X(schun.geop)-ST_X(schob.geop))/(ST_Y(schun.geop)-ST_Y(schob.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         WHEN (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schob.geop)-ST_X(schun.geop))/leitung.laenge)), (ST_Y(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/leitung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schob.geop)-ST_X(schun.geop))/leitung.laenge))-2*((-1)/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/leitung.laenge))-2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         WHEN (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben <> leitung.schoben AND new.schunten <> leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) < 0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) < 0 AND new.richtung = 'fließrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop)  >=0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten) OR
    #                                 (new.untersuchrichtung = 'gegen Fließrichtung' AND ST_X(schob.geop)-ST_X(schun.geop) <0 AND ST_Y(schob.geop)-ST_Y(schun.geop) >= 0 AND new.richtung = 'untersuchungsrichtung' AND new.schoben = leitung.schoben AND new.schunten = leitung.schunten)
    #
    #                         THEN
    #                         MakeLine(
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schob.geop)-ST_X(schun.geop))/leitung.laenge)), (ST_Y(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/leitung.laenge)), {dbcon.epsg}),
    #                                 schob.geop
    #                             ),
    #                             coalesce(
    #                             MakePoint((ST_X(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_X(schob.geop)-ST_X(schun.geop))/leitung.laenge))+2*((-1)/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), (ST_Y(schun.geop)+(new.station*COALESCE(leitung.laenge/NULLIF(new.inspektionslaenge, 0),1)*(ST_Y(schob.geop)-ST_Y(schun.geop))/leitung.laenge))+2*(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop)))/sqrt(1+(((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))*((ST_X(schob.geop)-ST_X(schun.geop))/(ST_Y(schob.geop)-ST_Y(schun.geop))))), {dbcon.epsg}),
    #                                 schun.geop
    #                             )
    #                         )
    #                         ELSE NULL
    #                         END
    #                     FROM
    #                     schaechte AS schob,
    #                     schaechte AS schun,
    #                     anschlussleitungen AS leitung
    #                     WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten AND leitung.leitnam = new.untersuchhal;
    #                   END"""
    #           ]
    #
    # for sql in sqllis:
    #     if not dbcon.sql(sql):
    #         logger.error(f"Fehler 4 bei Migration zu Version {VERSION}")
    #         return False

    return True
