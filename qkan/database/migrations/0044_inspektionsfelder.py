from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError

VERSION = "3.4.12"  # must be higher than previous one and correspond with QKan.dbVersion

logger = get_logger("QKan.database.migrations.0044")


def run(dbcon: DBConnection) -> bool:
    # Ergänzung der M150-Inspektionsfelder Reinigung, Auskleidung und Verbindung

    if "reinigung" not in dbcon.attrlist("haltungen_untersucht"):
        try:
            dbcon.alter_table(
                tabnam="haltungen_untersucht",
                attributes_new=[
                    "haltnam TEXT",
                    "bezugspunkt TEXT",
                    "schoben TEXT                                   /* join schaechte.schnam */ ",
                    "schunten TEXT                                  /* join schaechte.schnam */ ",
                    "hoehe REAL                                     /* Profilhoehe (mm) */ ",
                    "breite REAL                                    /* Profilbreite (mm) */ ",
                    "laenge REAL                                    /* abweichende Haltungslänge (m) */ ",
                    "baujahr INTEGER",
                    "id INTEGER                                     /* absolute Nummer der Inspektion */ ",
                    "untersuchtag TEXT",
                    "untersucher TEXT",
                    "untersuchrichtung TEXT",
                    "wetter INTEGER DEFAULT 0",
                    "reinigung TEXT",
                    "bewertungsart TEXT",
                    "bewertungstag TEXT",
                    "strasse TEXT",
                    "datenart TEXT",
                    "auftragsbezeichnung TEXT",
                    "max_ZD INTEGER",
                    "max_ZB INTEGER",
                    "max_ZS INTEGER",
                    "xschob REAL",
                    "yschob REAL",
                    "xschun REAL",
                    "yschun REAL",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
                ],
            )
        except:
            logger.error_code(
                "Fehlgeschlagen: migration_0044, reinigung in haltungen_untersucht ergänzen"
            )

    if "reinigung" not in dbcon.attrlist("anschlussleitungen_untersucht"):
        try:
            dbcon.alter_table(
                tabnam="anschlussleitungen_untersucht",
                attributes_new=[
                    "leitnam TEXT",
                    "bezugspunkt TEXT",
                    "schoben TEXT                                   /* join schaechte.schnam */ ",
                    "schunten TEXT                                  /* join schaechte.schnam */ ",
                    "hoehe REAL                                     /* Profilhoehe (mm) */ ",
                    "breite REAL                                    /* Profilbreite (mm) */ ",
                    "laenge REAL                                    /* abweichende Haltungslänge (m) */ ",
                    "baujahr INTEGER",
                    "id INTEGER                                     /* absolute Nummer der Inspektion */ ",
                    "untersuchtag TEXT",
                    "untersucher TEXT",
                    "untersuchrichtung TEXT",
                    "wetter INTEGER DEFAULT 0",
                    "reinigung TEXT",
                    "bewertungsart TEXT",
                    "bewertungstag TEXT",
                    "strasse TEXT",
                    "datenart TEXT",
                    "auftragsbezeichnung TEXT",
                    "max_ZD INTEGER",
                    "max_ZB INTEGER",
                    "max_ZS INTEGER",
                    "xschob REAL",
                    "yschob REAL",
                    "xschun REAL",
                    "yschun REAL",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
                ],
            )
        except:
            logger.error_code(
                "Fehlgeschlagen: migration_0044, reinigung in anschlussleitungen_untersucht ergänzen"
            )

    if "reinigung" not in dbcon.attrlist("schaechte_untersucht"):
        try:
            dbcon.alter_table(
                tabnam="schaechte_untersucht",
                attributes_new=[
                    "schnam TEXT",
                    "durchm REAL                                    /* Schachtdurchmesser (m) */ ",
                    "baujahr INTEGER",
                    "bezugspunkt TEXT",
                    "id INTEGER                                     /* absolute Nummer der Inspektion */ ",
                    "untersuchtag TEXT",
                    "untersucher TEXT",
                    "wetter INTEGER DEFAULT 0",
                    "reinigung TEXT",
                    "strasse TEXT",
                    "bewertungsart TEXT",
                    "bewertungstag TEXT",
                    "datenart TEXT",
                    "auftragsbezeichnung TEXT",
                    "max_ZD INTEGER",
                    "max_ZB INTEGER",
                    "max_ZS INTEGER",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
                ],
            )
        except:
            logger.error_code(
                "Fehlgeschlagen: migration_0044, reinigung in schaechte_untersucht ergänzen"
            )

    if "auskleidung" not in dbcon.attrlist("untersuchdat_haltung"):
        try:
            dbcon.alter_table(
                tabnam="untersuchdat_haltung",
                attributes_new=[
                    "untersuchhal TEXT",
                    "schoben TEXT                                   /* join schaechte.schnam */ ",
                    "schunten TEXT                                  /* join schaechte.schnam */ ",
                    "id INTEGER                                     /* absolute Nummer der Inspektion */ ",
                    "untersuchtag TEXT",
                    "untersuchrichtung TEXT",
                    "bandnr INTEGER",
                    "videozaehler TEXT",
                    "inspektionslaenge REAL",
                    "station REAL",
                    "stationtext REAL",
                    "timecode TEXT",
                    "video_offset REAL",
                    "langtext TEXT",
                    "kuerzel TEXT",
                    "charakt1 TEXT",
                    "charakt2 TEXT",
                    "quantnr1 REAL",
                    "quantnr2 REAL",
                    "streckenschaden TEXT",
                    "streckenschaden_lfdnr INTEGER",
                    "pos_von INTEGER",
                    "pos_bis INTEGER",
                    "auskleidung TEXT",
                    "foto_dateiname TEXT",
                    "film_dateiname TEXT",
                    "ordner_bild TEXT",
                    "ordner_video TEXT",
                    "filmtyp INTEGER",
                    "video_start INTEGER",
                    "video_ende INTEGER",
                    "bw_bs TEXT",
                    "ZD INTEGER",
                    "ZB INTEGER",
                    "ZS INTEGER",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
                ],
            )
        except:
            logger.error_code(
                "Fehlgeschlagen: migration_0044, auskleidung in untersuchdat_haltung ergänzen"
            )

    if "auskleidung" not in dbcon.attrlist("untersuchdat_anschlussleitung"):
        try:
            dbcon.alter_table(
                tabnam="untersuchdat_anschlussleitung",
                attributes_new=[
                    "untersuchleit TEXT",
                    "schoben TEXT                                   /* join schaechte.schnam */ ",
                    "schunten TEXT                                  /* join schaechte.schnam */ ",
                    "id INTEGER                                     /* absolute Nummer der Inspektion */ ",
                    "untersuchtag TEXT",
                    "bandnr INTEGER",
                    "videozaehler TEXT",
                    "inspektionslaenge REAL",
                    "station REAL",
                    "stationtext REAL",
                    "timecode TEXT",
                    "video_offset REAL",
                    "langtext TEXT",
                    "kuerzel TEXT",
                    "charakt1 TEXT",
                    "charakt2 TEXT",
                    "quantnr1 REAL",
                    "quantnr2 REAL",
                    "streckenschaden TEXT",
                    "streckenschaden_lfdnr INTEGER",
                    "pos_von INTEGER",
                    "pos_bis INTEGER",
                    "auskleidung TEXT",
                    "foto_dateiname TEXT",
                    "film_dateiname TEXT",
                    "ordner_bild TEXT",
                    "ordner_video TEXT",
                    "filmtyp INTEGER",
                    "video_start INTEGER",
                    "video_ende INTEGER",
                    "bw_bs TEXT",
                    "ZD INTEGER",
                    "ZB INTEGER",
                    "ZS INTEGER",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
                ],
            )
        except:
            logger.error_code(
                "Fehlgeschlagen: migration_0044, auskleidung in untersuchdat_anschlussleitung ergänzen"
            )

    if "verbindung" not in dbcon.attrlist("untersuchdat_schacht"):
        try:
            dbcon.alter_table(
                tabnam="untersuchdat_schacht",
                attributes_new=[
                    "untersuchsch TEXT",
                    "id INTEGER                                     /* absolute Nummer der Inspektion */ ",
                    "untersuchtag TEXT",
                    "bandnr INTEGER",
                    "videozaehler TEXT",
                    "timecode TEXT",
                    "langtext TEXT",
                    "kuerzel TEXT",
                    "charakt1 TEXT",
                    "charakt2 TEXT",
                    "quantnr1 REAL",
                    "quantnr2 REAL",
                    "streckenschaden TEXT",
                    "streckenschaden_lfdnr INTEGER",
                    "pos_von INTEGER",
                    "pos_bis INTEGER",
                    "vertikale_lage REAL",
                    "inspektionslaenge REAL",
                    "verbindung TEXT",
                    "bereich TEXT",
                    "foto_dateiname TEXT",
                    "ordner_bild TEXT",
                    "film_dateiname TEXT",
                    "ordner_video TEXT",
                    "filmtyp INTEGER",
                    "video_start INTEGER",
                    "video_ende INTEGER",
                    "bw_bs TEXT",
                    "ZD INTEGER",
                    "ZB INTEGER",
                    "ZS INTEGER",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP",
                ],
            )
        except:
            logger.error_code(
                "Fehlgeschlagen: migration_0044, verbindung in untersuchdat_schacht ergänzen"
            )

    return True
