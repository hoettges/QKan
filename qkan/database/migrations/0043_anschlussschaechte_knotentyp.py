from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError
VERSION = "3.4.11"  # must be higher than previous one and correspond with qkan_database.py: __dbVersion__

logger = get_logger("QKan.database.migrations.0043")

def run(dbcon: DBConnection) -> bool:
    # Ergänzung des Feldes knotentyp in Anschlussschächte

    if 'knotentyp' not in dbcon.attrlist('anschlussschaechte'):
        try:
            dbcon.alter_table(
                tabnam='anschlussschaechte',
                attributes_new=[
                    "schnam TEXT",
                    "sohlhoehe REAL",
                    "deckelhoehe REAL",
                    "durchm REAL                                     /* Schachtdurchmesser (m) */ ",
                    "druckdicht INTEGER",
                    "entwart TEXT DEFAULT 'Regenwasser'              /* join entwaesserungsarten.bezeichnung */ ",
                    "strasse TEXT",
                    "baujahr INTEGER",
                    "haltnam TEXT                                    /* Anschluss an Haltung */ ",
                    "urstation REAL                                  /* Anschlussposition gegen Fließrichtung */ ",
                    "ursprung TEXT                                   /* Adresse oder Objektbezeichnung */ ",
                    "anschlusstyp TEXT                               /* STRAKAT-Symbolbezeichnung */ ",
                    "knotentyp TEXT                                  /* join knotentypen.knotentyp */ ",
                    "eigentum TEXT                                   /* join eigentum.name */ ",
                    "teilgebiet TEXT                                 /* join teilgebiet.tgnam */ ",
                    "simstatus TEXT DEFAULT 'vorhanden'              /* join simulationsstatus.bezeichnung */ ",
                    "material TEXT                                   /* join material.bezeichnung */ ",
                    "xsch REAL",
                    "ysch REAL",
                    "kommentar TEXT",
                    "createdat TEXT DEFAULT CURRENT_TIMESTAMP"
                ]
            )
        except:
            logger.error_code('Fehlgeschlagen: migration_0043, knotentyp ergänzen')

    return True
