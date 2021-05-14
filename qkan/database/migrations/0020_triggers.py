import logging

from qkan.database.dbfunc import DBConnection

VERSION = "3.0.8"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Version 3.1.4: Trigger wurden verworfen, deshalb Zusatz unter Version 3.1.5

    # ------------------------------------------------------------------------------------
    logger.debug(f"Version: {dbcon.current_version}")
    if dbcon.current_version < "3.1.5":
        logger.debug(f"Version älter 3.1.5 erkannt: {dbcon.current_version}")

        if dbcon.current_version == "3.1.4":
            logger.debug(f"Version 3.1.4 erkannt: {dbcon.current_version}")

            # Trigger aus Version 3.1.4 wieder löschen
            if not dbcon.sql(
                "DROP TRIGGER create_missing_geoobject_haltungen",
                "dbfunc.DBConnection.version (3.1.5-1",
            ):
                return False
            dbcon.commit()

            if not dbcon.sql(
                "DROP TRIGGER create_missing_geoobject_schaechte",
                "dbfunc.DBConnection.version (3.1.5-2",
            ):
                return False
            dbcon.commit()

            if not dbcon.sql(
                "DROP TRIGGER create_missing_geoobject_pumpen",
                "dbfunc.DBConnection.version (3.1.5-3",
            ):
                return False
            dbcon.commit()

            if not dbcon.sql(
                "DROP TRIGGER create_missing_geoobject_wehre",
                "dbfunc.DBConnection.version (3.1.5-4",
            ):
                return False
            dbcon.commit()

        # Schächte -----------------------------------------------------------------
        if not dbcon.sql(
            f"""
            CREATE VIEW IF NOT EXISTS schaechte_data AS 
            SELECT
                schnam, 
                xsch, ysch, 
                sohlhoehe, 
                deckelhoehe, durchm, 
                druckdicht, ueberstauflaeche, 
                entwart, strasse, teilgebiet, 
                knotentyp, auslasstyp, schachttyp, 
                simstatus, 
                kommentar, createdat
            FROM schaechte;
            """,
            "dbfunc.DBConnection.version (3.1.5-5)"
            + "VIEW schaechte_data konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()

        if not dbcon.sql(
            f"""
            CREATE TRIGGER IF NOT EXISTS schaechte_insert_clipboard
            INSTEAD OF INSERT ON schaechte_data FOR EACH ROW
            BEGIN
                INSERT INTO schaechte
                  (schnam, sohlhoehe, 
                   deckelhoehe, durchm, 
                   druckdicht, ueberstauflaeche, 
                   entwart, strasse, teilgebiet, 
                   knotentyp, auslasstyp, schachttyp, 
                   simstatus, 
                   kommentar, createdat, 
                   geop, geom)
                VALUES (
                    new.schnam, new.sohlhoehe, new.deckelhoehe, 
                    CASE WHEN new.durchm > 200 THEN new.durchm/1000 ELSE new.durchm END, 
                    coalesce(new.druckdicht, 0), coalesce(new.ueberstauflaeche, 0), 
                    coalesce(new.entwart, 'Regenwasser'), new.strasse, new.teilgebiet, 
                    new.knotentyp, new.auslasstyp, coalesce(new.schachttyp, 'Schacht'), 
                    coalesce(new.simstatus, 'vorhanden'),
                    new.kommentar, coalesce(new.createdat, strftime('%d.%m.%Y %H:%M','now')),
                    MakePoint(new.xsch, new.ysch, {dbcon.epsg}),
                    CastToMultiPolygon(
                        MakePolygon(
                            MakeCircle(
                                new.xsch,
                                new.ysch,
                                coalesce(new.durchm/2, 0.5), {dbcon.epsg}
                            )
                        )
                    )
                );
            END
            """,
            "dbfunc.DBConnection.version (3.1.5-6)"
            + "TRIGGER schaechte_insert_clipboard konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()

        # Haltungen -----------------------------------------------------------------
        if not dbcon.sql(
            f"""
            CREATE VIEW IF NOT EXISTS haltungen_data AS
            SELECT
                haltnam, schoben, schunten,
                hoehe, breite, laenge,
                sohleoben, sohleunten,
                deckeloben, deckelunten,
                xschob, yschob, xschun, yschun,
                teilgebiet, qzu, profilnam,
                entwart, rohrtyp, ks,
                simstatus, kommentar, createdat
            FROM haltungen
            """,
            "dbfunc.DBConnection.version (3.1.5-5)"
            + "VIEW haltungen_data konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()

        if not dbcon.sql(
            f"""
            CREATE TRIGGER IF NOT EXISTS haltungen_insert_clipboard
            INSTEAD OF INSERT ON haltungen_data FOR EACH ROW
            BEGIN
                INSERT INTO haltungen
                (haltnam, schoben, schunten, hoehe, breite, laenge,
                sohleoben, sohleunten, deckeloben, deckelunten, 
                teilgebiet, qzu, profilnam, entwart, rohrtyp, ks,
                simstatus, kommentar, createdat, geom)
                SELECT
                    new.haltnam, new.schoben, new.schunten,
                    CASE WHEN new.hoehe > 20 THEN new.hoehe/1000 ELSE new.hoehe END,
                    CASE WHEN new.breite > 20 THEN new.breite/1000 ELSE new.breite END,
                    new.laenge, new.sohleoben, new.sohleunten, new.deckeloben, new.deckelunten, 
                    new.teilgebiet, new.qzu, coalesce(new.profilnam, 'Kreisquerschnitt'), 
                    coalesce(new.entwart, 'Regenwasser'), new.rohrtyp, coalesce(new.ks, 1.5), 
                    coalesce(new.simstatus, 'vorhanden'), new.kommentar, 
                    coalesce(new.createdat, strftime('%d.%m.%Y %H:%M','now')), 
                    MakeLine(
                        coalesce(
                            MakePoint(new.xschob, new.yschob, {dbcon.epsg}),
                            schob.geop
                        ), 
                        coalesce(
                            MakePoint(new.xschun, new.yschun, {dbcon.epsg}),
                            schun.geop
                        )
                    )
                FROM
                    schaechte AS schob,
                    schaechte AS schun
                WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
            END
            """,
            "dbfunc.DBConnection.version (3.1.5-6)"
            + "TRIGGER haltungen_insert_clipboard konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()

        # Pumpen -----------------------------------------------------------------
        if not dbcon.sql(
            """
            CREATE VIEW IF NOT EXISTS pumpen_data AS
            SELECT 
                pnam, schoben, schunten, 
                pumpentyp, volanf, volges, 
                sohle, steuersch, 
                einschalthoehe, ausschalthoehe,
                teilgebiet, simstatus, 
                kommentar, createdat
            FROM pumpen;
          """,
            "dbfunc.DBConnection.version (3.1.5-5)"
            + "VIEW haltungen_data konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()

        if not dbcon.sql(
            """
            CREATE TRIGGER IF NOT EXISTS pumpen_insert_clipboard
            INSTEAD OF INSERT ON pumpen_data FOR EACH ROW
            BEGIN
                INSERT INTO pumpen
                    (pnam, schoben, schunten, 
                    pumpentyp, volanf, volges, 
                    sohle, steuersch, 
                    einschalthoehe, ausschalthoehe,
                    teilgebiet, simstatus, 
                    kommentar, createdat, 
                    geom)
                SELECT 
                    new.pnam, new.schoben, new.schunten, 
                    new.pumpentyp, new.volanf, new.volges, 
                    new.sohle, new.steuersch, 
                    new.einschalthoehe, new.ausschalthoehe,
                    new.teilgebiet, coalesce(new.simstatus, 'vorhanden'), 
                    new.kommentar, new.createdat,
                    MakeLine(schob.geop, schun.geop)
                FROM
                    schaechte AS schob,
                    schaechte AS schun
                WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
            END;
            """,
            "dbfunc.DBConnection.version (3.1.5-6)"
            + "TRIGGER haltungen_insert_clipboard konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()

        # Wehre -----------------------------------------------------------------
        if not dbcon.sql(
            """
            CREATE VIEW IF NOT EXISTS wehre_data AS
            SELECT 
                wnam, schoben, schunten, 
                wehrtyp, schwellenhoehe, kammerhoehe, 
                laenge, uebeiwert, aussentyp, aussenwsp, 
                teilgebiet, simstatus, 
                kommentar, createdat
            FROM wehre;
            """,
            "dbfunc.DBConnection.version (3.1.5-5)"
            + "VIEW haltungen_data konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()

        if not dbcon.sql(
            """
            CREATE TRIGGER IF NOT EXISTS wehre_insert_clipboard
            INSTEAD OF INSERT ON wehre_data FOR EACH ROW
            BEGIN
                INSERT INTO wehre
                    (wnam, schoben, schunten, 
                    wehrtyp, schwellenhoehe, kammerhoehe, 
                    laenge, uebeiwert, aussentyp, aussenwsp, 
                    teilgebiet, simstatus, 
                    kommentar, createdat, 
                    geom)
                SELECT 
                    new.wnam, new.schoben, new.schunten, 
                    new.wehrtyp, new.schwellenhoehe, new.kammerhoehe, 
                    new.laenge, new.uebeiwert, new.aussentyp, new.aussenwsp, 
                    new.teilgebiet, coalesce(new.simstatus, 'vorhanden'), 
                    new.kommentar, new.createdat,
                    MakeLine(schob.geop, schun.geop)
                FROM
                    schaechte AS schob,
                    schaechte AS schun
                WHERE schob.schnam = new.schoben AND schun.schnam = new.schunten;
            END;
            """,
            "dbfunc.DBConnection.version (3.1.5-6)"
            + "TRIGGER haltungen_insert_clipboard konnten nicht erstellt werden.",
        ):
            return False
        dbcon.commit()
    return True
