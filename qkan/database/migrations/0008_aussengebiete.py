import logging

from qkan.database.dbfunc import DBConnection

VERSION = "2.5.2"

logger = logging.getLogger("QKan.database.migrations")


def run(dbcon: DBConnection) -> bool:
    # Einleitungen aus Aussengebieten ----------------------------------------------------------------
    sql = """
    CREATE TABLE IF NOT EXISTS aussengebiete (
        pk INTEGER PRIMARY KEY, 
        gebnam TEXT, 
        schnam TEXT, 
        hoeheob REAL, 
        hoeheun REAL, 
        fliessweg REAL, 
        basisabfluss REAL, 
        cn REAL, 
        regenschreiber TEXT, 
        teilgebiet TEXT, 
        kommentar TEXT, 
        createdat TEXT DEFAULT CURRENT_DATE
    )
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.2-1)"):
        return False

    if not dbcon.sql(
        "SELECT AddGeometryColumn('aussengebiete','geom',?,'MULTIPOLYGON',2)",
        "dbfunc.DBConnection.version (2.5.2-2)",
        parameters=(dbcon.epsg,),
    ):
        return False

    if not dbcon.sql(
        "SELECT CreateSpatialIndex('aussengebiete','geom')",
        "dbfunc.DBConnection.version (2.5.2-3)",
    ):
        return False

    # Anbindung Aussengebiete -------------------------------------------------------------------------

    sql = """
    CREATE TABLE IF NOT EXISTS linkageb (
        pk INTEGER PRIMARY KEY,
        gebnam TEXT,
        schnam TEXT
    )
    """

    if not dbcon.sql(sql, "dbfunc.DBConnection.version (2.5.2-4)"):
        return False

    if not dbcon.sql(
        "SELECT AddGeometryColumn('linkageb','glink',?,'LINESTRING',2)",
        "dbfunc.DBConnection.version (2.5.2-5)",
        parameters=(dbcon.epsg,),
    ):
        return False

    if not dbcon.sql(
        "SELECT CreateSpatialIndex('linkageb','glink')",
        "dbfunc.DBConnection.version (2.5.2-6)",
    ):
        return False

    dbcon.commit()

    # Formulare aktualisieren ----------------------------------------------------------
    #
    # Dieser Block muss im letzten Update vorkommen, in dem auch Formulare geändert wurden...
    #
    # Spielregel: QKan-Formulare werden ohne Rückfrage aktualisiert.
    # Falls eigene Formulare gewünscht sind, können diese im selben Verzeichnis liegen,
    # die Eingabeformulare müssen jedoch andere Namen verwenden, auf die entsprechend
    # in der Projektdatei verwiesen werden muss.

    # try:
    # projectpath = os.path.dirname(dbcon.dbname)
    # if 'eingabemasken' not in os.listdir(projectpath):
    # os.mkdir(os.path.join(projectpath, 'eingabemasken'))
    # formpath = os.path.join(projectpath, 'eingabemasken')
    # formlist = os.listdir(formpath)

    # logger.debug("\nEingabeformulare aktualisieren: \n" +
    # "projectpath = {projectpath}\n".format(projectpath=projectpath) +
    # "formpath = {formpath}\n".format(formpath=formpath) +
    # "formlist = {formlist}\n".format(formlist=formlist) +
    # "templatepath = {templatepath}".format(templatepath=dbcon.templatepath)
    # )

    # for formfile in glob.iglob(os.path.join(dbcon.templatepath, '*.ui')):
    # logger.debug("Eingabeformular aktualisieren: {} -> {}".format(formfile, formpath))
    # shutil.copy2(formfile, formpath)
    # except BaseException as err:
    # fehlermeldung('Fehler beim Aktualisieren der Eingabeformulare\n',
    # "{e}".format(e=repr(err)))
    return True
