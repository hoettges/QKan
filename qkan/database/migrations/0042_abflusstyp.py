from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError
VERSION = "3.4.11"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations.0042")

def run(dbcon: DBConnection) -> bool:
    # Ergänzung einiger Felder in Videos

    if 'abflussart' not in dbcon.attrlist('haltungen'):
        try:
            dbcon.alter_table(
                tabnam='haltungen',
                attributes_new=[
                    "haltnam TEXT",
                    "schoben TEXT                                    /* join schaechte.schnam */ ",
                    "schunten TEXT                                   /* join schaechte.schnam */ ",
                    "hoehe REAL                                      /* Profilhoehe (mm) */ ",
                    "breite REAL                                     /* Profilbreite (mm) */ ",
                    "laenge REAL                                     /* abweichende Haltungslänge (m) */ ",
                    "aussendurchmesser REAL",
                    "sohleoben REAL                                  /* Sohlhöhe oben (m) */ ",
                    "sohleunten REAL                                 /* Sohlhöhe unten (m) */ ",
                    "baujahr INTEGER",
                    "eigentum TEXT                                   /* join eigentum.name */ ",
                    "teilgebiet TEXT                                 /* join teilgebiet.tgnam */ ",
                    "strasse TEXT                                    /* für ISYBAU benötigt */ ",
                    "profilnam TEXT DEFAULT 'Kreisquerschnitt'       /* join profile.profilnam */ ",
                    "entwart TEXT DEFAULT 'Regenwasser'              /* join entwaesserungsarten.bezeichnung */ ",
                    "abflussart TEXT DEFAULT 'Freispiegel'           /* join abflussart.bezeichnung */ ",
                    "material TEXT                                   /* join material.bezeichnung */ ",
                    "profilauskleidung TEXT",
                    "innenmaterial TEXT",
                    "ks REAL DEFAULT 1.5                             /* abs. Rauheit (mmm, Prandtl-Colebrook) */ ",
                    "haltungstyp TEXT DEFAULT 'Haltung'              /* join haltungstypen.bezeichnung */ ",
                    "simstatus TEXT DEFAULT 'vorhanden'              /* join simulationsstatus.bezeichnung */ ",
                    "rwanschluss INTEGER DEFAULT 1                   /* soll bei TEZG-Erstellung berücksichtigt werden */ ",
                    "druckdicht INTEGER DEFAULT 0                    /* Druckleitung */ ",
                    "xschob REAL",
                    "yschob REAL",
                    "xschun REAL",
                    "yschun REAL",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
                ]
            )
        except:
            logger.error_code('Fehlgeschlagen: migration_0041, abflussart ergänzen')

    return True
