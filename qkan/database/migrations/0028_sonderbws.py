from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger

VERSION = "3.2.29"

logger = get_logger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    """Ergänze verschiedene Haltungstypen, die alle in der Tabelle haltungen gespeichert werden."""

    # Alle Tabellen erneuern, in denen createdat vorkommt
    # "tezg_data" aus Liste entfernt, jh, 18.01.2023

    views = [
        "haltungen_data", "haltungen_untersucht_data", "untersuchdat_haltung_data",
        "anschlussleitungen_data", "schaechte_data", "schaechte_untersucht_data",
        "untersuchdat_schacht_data", "pumpen_data", "wehre_data",
        "v_linkfl_check", "v_flaechen_ohne_linkfl", "v_flaechen_check",
        "v_tezg_check", "v_linkfl_redundant", "v_linksw_redundant",
        ]
    
    for view in views:
        sql = f"DROP VIEW IF EXISTS {view}"
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
            "haltnam TEXT",
            "schoben TEXT                                    -- join schaechte.schnam",
            "schunten TEXT                                   -- join schaechte.schnam",
            "hoehe REAL                                      -- Profilhoehe (m)",
            "breite REAL                                     -- Profilbreite (m)",
            "laenge REAL                                     -- abweichende Haltungslänge (m)",
            "sohleoben REAL                                  -- abweichende Sohlhöhe oben (m)",
            "sohleunten REAL                                 -- abweichende Sohlhöhe unten (m)",
            "teilgebiet TEXT                                 -- join teilgebiet.tgnam",
            "strasse TEXT                                    -- für ISYBAU benötigt",
            "profilnam TEXT DEFAULT 'Kreisquerschnitt'       -- join profile.profilnam",
            "entwart TEXT DEFAULT 'Regenwasser'              -- join entwaesserungsarten.bezeichnung",
            "material TEXT",
            "ks REAL DEFAULT 1.5                             -- abs. Rauheit (Prandtl-Colebrook)",
            "haltungstyp TEXT DEFAULT 'Haltung'              -- Art der Kante",
            "simstatus TEXT DEFAULT 'vorhanden'              -- join simulationsstatus.bezeichnung",
            "xschob REAL",
            "yschob REAL",
            "xschun REAL",
            "yschun REAL",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        [   "qzu",
            "rohrtyp",
            "deckeloben",
            "deckelunten",
        ],
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Hinzufügen von haltungstyp und material zu Tabelle 'haltungen' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "haltungen_untersucht",
        [
            "haltnam TEXT",
            "schoben TEXT                                    -- join schaechte_untersucht.schnam",
            "schunten TEXT                                   -- join schaechte_untersucht.schnam",
            "hoehe REAL                                      -- Profilhoehe (m)",
            "breite REAL                                     -- Profilbreite (m)",
            "laenge REAL                                     -- abweichende Haltungslänge (m)",
            "baujahr INTEGER",
            "max_ZD INTEGER",
            "max_ZB INTEGER",
            "max_ZS INTEGER",
            "strasse TEXT",
            "untersuchtag TEXT",
            "untersucher TEXT",
            "wetter INTEGER DEFAULT 0",
            "bewertungsart INTEGER DEFAULT 0",
            "bewertungstag TEXT",
            "xschob REAL",
            "yschob REAL",
            "xschun REAL",
            "yschun REAL",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'haltungen_untersucht' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "untersuchdat_haltung",
        [
            "untersuchhal TEXT",
            "untersuchrichtung TEXT",
            "schoben TEXT                                    -- join schaechte_untersucht.schnam",
            "schunten TEXT                                   -- join schaechte_untersucht.schnam",
            "id INTEGER",
            "videozaehler INTEGER",
            "inspektionslaenge REAL",
            "station REAL",
            "timecode INTEGER",
            "video_offset REAL",
            "ZD INTEGER",
            "ZB INTEGER",
            "ZS INTEGER",
            "kuerzel TEXT",
            "charakt1 TEXT",
            "charakt2 TEXT",
            "quantnr1 REAL",
            "quantnr2 REAL",
            "streckenschaden TEXT",
            "streckenschaden_lfdnr INTEGER",
            "pos_von INTEGER",
            "pos_bis INTEGER",
            "foto_dateiname TEXT",
            "film_dateiname TEXT",
            "ordner_bild TEXT",
            "ordner_video TEXT",
            "richtung TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle haltungen fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "anschlussleitungen",
        [
            "leitnam TEXT",
            "schoben TEXT                                    -- join schaechte.schnam",
            "schunten TEXT                                   -- join schaechte.schnam",
            "hoehe REAL                                      -- Profilhoehe (m)",
            "breite REAL                                     -- Profilbreite (m)",
            "laenge REAL                                     -- abweichende Haltungslänge (m)",
            "sohleoben REAL                                  -- abweichende Sohlhöhe oben (m)",
            "sohleunten REAL                                 -- abweichende Sohlhöhe unten (m)",
            "deckeloben REAL",
            "deckelunten REAL",
            "teilgebiet TEXT                                 -- join teilgebiet.tgnam",
            "qzu REAL",
            "profilnam TEXT DEFAULT 'Kreisquerschnitt'",
            "entwart TEXT DEFAULT 'Regenwasser'              -- join entwaesserungsarten.bezeichnung",
            "material TEXT",
            "ks REAL DEFAULT 1.5",
            "simstatus TEXT DEFAULT 'vorhanden'              -- join simulationsstatus.bezeichnung",
            "xschob REAL",
            "yschob REAL",
            "xschun REAL",
            "yschun REAL",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        ["rohrtyp"
        ]
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'anschlussleitungen' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "schaechte",
        [
            "schnam TEXT",
            "sohlhoehe REAL",
            "deckelhoehe REAL",
            "durchm REAL",
            "druckdicht INTEGER",
            "ueberstauflaeche REAL DEFAULT 0",
            "entwart TEXT DEFAULT 'Regenwasser'              -- join entwaesserungsarten.bezeichnung",
            "strasse TEXT",
            "teilgebiet TEXT                                 -- join teilgebiet.tgnam",
            "knotentyp TEXT                                  -- join knotentypen.knotentyp",
            "auslasstyp TEXT                                 -- join auslasstypen.bezeichnung",
            "schachttyp TEXT DEFAULT 'Schacht'               -- join schachttypen.schachttyp",
            "simstatus TEXT DEFAULT 'vorhanden'              -- join simulationsstatus.bezeichnung",
            "material TEXT",
            "xsch REAL",
            "ysch REAL",
            "kommentar TEXT",
            "istauslass",
            "istspeicher",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        ["istauslass",
         "istspeicher"
        ]
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'schaechte' fehlgeschlagen"
        )

    if not (dbcon.sql("DROP TRIGGER ggi_schaechte_geom") and
             dbcon.sql("DROP TRIGGER ggu_schaechte_geom")):
        logger.error(f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Löschen der geometry-constraints in Tabelle 'schaechte' fehlgeschlagen")

    if not dbcon.alter_table(
        "schaechte_untersucht",
        [
            "schnam TEXT",
            "durchm REAL",
            "baujahr INTEGER",
            "untersuchtag TEXT",
            "untersucher TEXT",
            "wetter INTEGER DEFAULT 0",
            "bewertungsart INTEGER DEFAULT 0",
            "bewertungstag TEXT",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'schaechte_untersucht' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "untersuchdat_schacht",
        [
            "untersuchsch TEXT",
            "id INTEGER",
            "videozaehler INTEGER",
            "timecode INTEGER",
            "kuerzel TEXT",
            "charakt1 TEXT",
            "charakt2 TEXT",
            "quantnr1 REAL",
            "quantnr2 REAL",
            "streckenschaden TEXT",
            "streckenschaden_lfdnr INTEGER",
            "pos_von INTEGER",
            "pos_bis INTEGER",
            "vertikale_lage INTEGER",
            "inspektionslaenge INTEGER",
            "bereich TEXT",
            "foto_dateiname TEXT",
            "ordner TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'untersuchdat_schacht' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "einzugsgebiete",
        [
            "tgnam TEXT",
            "ewdichte REAL",
            "wverbrauch REAL",
            "stdmittel REAL",
            "fremdwas REAL",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'einzugsgebiete' fehlgeschlagen"
        )

    if not (dbcon.sql("DROP TRIGGER ggi_einzugsgebiete_geom") and
             dbcon.sql("DROP TRIGGER ggu_einzugsgebiete_geom")):
        logger.error(f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Löschen der geometry-constraints in Tabelle 'einzugsgebiete' fehlgeschlagen")

    if not dbcon.alter_table(
        "teilgebiete",
        [
            "tgnam TEXT",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'teilgebiete' fehlgeschlagen"
        )

    if not (dbcon.sql("DROP TRIGGER ggi_teilgebiete_geom") and
             dbcon.sql("DROP TRIGGER ggu_teilgebiete_geom")):
        logger.error(f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Löschen der geometry-constraints in Tabelle 'teilgebiete' fehlgeschlagen")

    if not dbcon.alter_table(
        "gruppen",
        [
            "pktab INTEGER",
            "grnam TEXT",
            "teilgebiet TEXT                                -- join teilgebiet.tgnam",
            "tabelle TEXT",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'gruppen' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "flaechen",
        [
            "flnam TEXT",
            "haltnam TEXT                            -- join haltungen.haltnam",
            "schnam TEXT                             -- join schaechte.schnam",
            "neigkl INTEGER DEFAULT 1                -- Neigungsklasse (1-4)",
            "neigung REAL                            -- absolute Neigung (%)",
            "teilgebiet TEXT                         -- join teilgebiet.tgnam",
            "regenschreiber TEXT",
            "abflussparameter TEXT                   -- join abflussparameter.apnam",
            "aufteilen TEXT DEFAULT 'nein'",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'flaechen' fehlgeschlagen"
        )

    if not (dbcon.sql("DROP TRIGGER ggi_flaechen_geom") and
             dbcon.sql("DROP TRIGGER ggu_flaechen_geom")):
        logger.error(f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Löschen der geometry-constraints in Tabelle 'flaechen' fehlgeschlagen")

    if not dbcon.alter_table(
        "tezg",
        [
            "flnam TEXT",
            "haltnam TEXT                -- join haltungen.haltnam",
            "schnam TEXT                 -- join schaechte.schnam",
            "neigkl INTEGER DEFAULT 1    -- Werte [1-5], als Vorgabe fuer automatisch erzeugte unbef Flaechen",
            "neigung REAL                -- absolute Neigung (%)",
            "befgrad REAL                -- (-) Befestigungsgrad absolut, nur optional fuer SWMM und HE6",
            "schwerpunktlaufzeit REAL    -- nur, wenn nur Haltungsflächen aber keine Flächen eingelesen werden",
            "regenschreiber TEXT         -- Regenschreiber beziehen sich auf Zieldaten",
            "teilgebiet TEXT             -- join teilgebiet.tgnam",
            "abflussparameter TEXT       -- als Vorgabe fuer automatisch erzeugte unbef Flaechen",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'tezg' fehlgeschlagen"
        )

    if not (dbcon.sql("DROP TRIGGER ggi_tezg_geom") and
             dbcon.sql("DROP TRIGGER ggu_tezg_geom")):
        logger.error(f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Löschen der geometry-constraints in Tabelle 'tezg' fehlgeschlagen")

    if not dbcon.alter_table(
        "einleit",
        [
            "elnam TEXT",
            "haltnam TEXT               -- join haltungen.haltnam",
            "schnam TEXT                -- join schaechte.schnam",
            "teilgebiet TEXT            -- join teilgebiet.tgnam ",
            "zufluss REAL",
            "ew REAL",
            "einzugsgebiet TEXT         -- join einzugsgebiete.tgnam",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'einleit' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "aussengebiete",
        [
            "gebnam TEXT",
            "schnam TEXT                -- join schaechte.schnam",
            "hoeheob REAL",
            "hoeheun REAL",
            "fliessweg REAL",
            "basisabfluss REAL",
            "cn REAL",
            "regenschreiber TEXT",
            "teilgebiet TEXT            -- join teilgebiet.tgnam ",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'aussengebiete' fehlgeschlagen"
        )

    if not (dbcon.sql("DROP TRIGGER ggi_aussengebiete_geom") and
             dbcon.sql("DROP TRIGGER ggu_aussengebiete_geom")):
        logger.error(f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Löschen der geometry-constraints in Tabelle 'aussengebiete' fehlgeschlagen")

    if not dbcon.alter_table(
        "abflussparameter",
        [
            "apnam TEXT",
            "anfangsabflussbeiwert REAL",
            "endabflussbeiwert REAL",
            "benetzungsverlust REAL",
            "muldenverlust REAL",
            "benetzung_startwert REAL",
            "mulden_startwert REAL",
            "rauheit_kst REAL                        -- Rauheit Stricklerbeiwert = 1/n",
            "pctZero REAL                            -- SWMM: % Zero-Imperv",
            "bodenklasse TEXT                        -- impervious: NULL, pervious: JOIN TO bodenklasse.bknam",
            "flaechentyp TEXT                        -- JOIN TO flaechentypen.bezeichnung",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'abflussparameter' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "bodenklassen",
        [
            "bknam TEXT",
            "infiltrationsrateanfang REAL                -- (mm/min)",
            "infiltrationsrateende REAL                  -- (mm/min)",
            "infiltrationsratestart REAL                 -- (mm/min)",
            "rueckgangskonstante REAL                    -- (1/d)",
            "regenerationskonstante REAL                 -- (1/d)",
            "saettigungswassergehalt REAL                -- (mm)",
            "kommentar TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'bodenklassen' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "pruefsql",
        [
            "gruppe TEXT                         -- zur Auswahl nach Thema",
            "warntext TEXT                       -- Beschreibung der SQL-Abfrage",
            "warntyp TEXT                        -- 'Info', 'Warnung', 'Fehler'",
            "warnlevel INTEGER                   -- zur Sortierung, 1-3: Info, 4-7: Warnung, 8-10: Fehler",
            "sql TEXT",
            "layername TEXT                      -- Objektsuche: Layername",
            "attrname TEXT                       -- Objektsuche: Attribut zur Objektidentifikation",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'pruefsql' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "pruefliste",
        [
            "warntext TEXT                       -- Beschreibung der SQL-Abfrage",
            "warntyp TEXT                        -- 'Info', 'Warnung', 'Fehler'",
            "warnlevel INTEGER                   -- zur Sortierung, 1-3: Info, 4-7: Warnung, 8-10: Fehler",
            "layername TEXT                      -- Objektsuche: Layername",
            "attrname TEXT                       -- Objektsuche: Attribut zur Objektidentifikation",
            "objname TEXT                        -- Objektsuche: Objektname",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'pruefliste' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "info",
        [
            "subject TEXT",
            "value TEXT",
            "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'info' fehlgeschlagen"
        )

    if not dbcon.alter_table(
        "flaechen_he8",
        [
            "Name TEXT",
            "Haltung TEXT",
            "Groesse REAL",
            "Regenschreiber TEXT",
            "Flaechentyp INTEGER",
            "BerechnungSpeicherkonstante INTEGER",
            "Typ INTEGER",
            "AnzahlSpeicher INTEGER",
            "Speicherkonstante REAL",
            "Schwerpunktlaufzeit REAL",
            "FliesszeitOberflaeche REAL",
            "LaengsteFliesszeitKanal REAL",
            "Parametersatz TEXT",
            "Neigungsklasse INTEGER",
            "ZuordnUnabhEZG INTEGER",
            "IstPolygonalflaeche SMALLINT",
            "ZuordnungGesperrt SMALLINT",
            "LastModified TEXT DEFAULT CURRENT_TIMESTAMP",
            "Kommentar TEXT"
        ],
        []
    ):
        logger.error(
            f"Fehler 2 bei Migration zu Version {VERSION}: "
            "Änderungen in Tabelle 'flaechen_he8' fehlgeschlagen"
        )

    # if not (dbcon.sql("DROP TRIGGER ggi_flaechen_he8_geometry") and
    #          dbcon.sql("DROP TRIGGER ggu_flaechen_he8_geometry")):
    #     logger.error(f"Fehler 2 bei Migration zu Version {VERSION}: "
    #         "Löschen der geometry-constraints in Tabelle 'flaechen_he8' fehlgeschlagen")
    #
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
