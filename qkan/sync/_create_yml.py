# SQL name pattern for all tables:
#   sync_create_{table},
#   sync_create_{table}_geom,
#   sync_reset_{table},
#   sync_{table}_ext,
#   sync_{table}_local,
#   sync_{table}_dif,
#
#   sync_{table}_add,
#   sync_{table}_del,
#   sync_{table}_mod

import textwrap
from qkan import enums
from qkan.database.dbfunc import DBConnection
from qkan.utils import get_logger, QkanDbError, QkanError

logger = get_logger("QKan.sync._create_yml")

def _create_yml_postgis(db_qkan: DBConnection):
    """Erstellt die SQL-Anweisungen für die Synchronisation für eine POSTGIS-Datenbank
       und ergänzt sie in QKan.sqls['sync']"""
    pass

def _create_yml_spatialite(db_qkan: DBConnection):
    """Erstellt die SQL-Anweisungen für die Synchronisation für eine SpatiaLite-Datenbank
       und ergänzt sie in QKan.sqls['sync']"""

    TABLES_GEOM = enums.SyncTables.TABLES_GEOM.value
    TABLES_GEOP = enums.SyncTables.TABLES_GEOP.value
    TABLES_GLINK = enums.SyncTables.TABLES_GLINK.value
    TABLES_ATTR = enums.SyncTables.TABLES_ATTR.value
    TABLES_UNTERSUCH = enums.SyncTables.TABLES_UNTERSUCH.value

    # db_qkan.loadmodule('sync')

    # params = (QKan.config.sync.ext,)
    # if not db_qkan.sql(
    #     sql='ATTACH DATABASE ? AS ext;',
    #     stmt_category='Attach external DB',
    #     parameters=params,
    # ):
    #     logger.error_data('Datenbank {QKan.config.sync.ext=} konnte nicht angebunden werden')
    #     raise QkanDbError

    tables = TABLES_GEOM + TABLES_GEOP + TABLES_GLINK + TABLES_ATTR
    t_ = sorted(list(set(tables)))
    if len(tables) != len(t_):
        logger.error_code('Fehler: Keine Tabelle darf in mehr als einer Liste "TABLES_XXXX" vorkommen!')
        raise QkanError

    # Initialisierung
    sqls = {}

    for tabnam in tables:

        if not db_qkan.sql(
                sql=f'PRAGMA table_info({tabnam});',
                stmt_category=f'table attributes of {tabnam}',
        ):
            logger.error_data(f'Tabellenattribute für {tabnam} konnten nicht abgerufen werden')
            raise QkanDbError
        fields_be = db_qkan.fetchall()          #note_1: Attributnamen aus PRAGMA-Abfrage

        if not db_qkan.sql(
                sql=f'PRAGMA ext.table_info({tabnam});',
                stmt_category=f'table attributes of {tabnam}',
        ):
            logger.error_data('Tabellenattribute für ext.{tabnam} konnten nicht abgerufen werden')
            raise QkanDbError
        fields_ex = db_qkan.fetchall()

        # Tabelle in interner oder externer Datenbank nicht vorhanden
        if len(fields_ex) == 0 or len(fields_be) == 0:
            continue

        attrlis = []
        typlis  = []
        fieldlis = []
        objnam = None
        igeo = None            # Index des ersten Geoobjekts
        ngeo = None            # Index des zu synchronisierenden Geoobjekts in attrlis und typlis.
                               # Bei Attributtabellen ohne Geo-Objekt ist ngeo = None
        nattr = 0              # Gesamtlänge der Attributliste inkl. Geoobjekte

        if tabnam in TABLES_GEOM:
            gobj = 'geom'
        elif tabnam in TABLES_GEOP:
            gobj = 'geop'
        elif tabnam in TABLES_GLINK:
            gobj = 'glink'
        elif tabnam in TABLES_ATTR:
            gobj = None
        else:
            logger.error_code('Fehler: {tabnam=} konnte in den Tabellenlisten nicht gefunden werden')
            raise QkanDbError

        attrs_ex = [el[1] for el in fields_ex]
        types_ex = [el[2] for el in fields_ex]
        for _, attr, typ, notnull, dflt_value, is_pk in fields_be:
            if attr in attrs_ex:
                i = attrs_ex.index(attr)
                if types_ex[i] != typ:
                    continue                    # Datentyp weicht ab, also keine Synchronisation
            else:
                continue                        # Attribut nicht in externer Tabelle, also keine Synchronisation
            if is_pk == 0 and attr != 'createdat':
                attrlis.append(attr)
                typlis.append(typ)
                fieldlis.append([attr, typ])
                if objnam is None:
                    objnam = attr
                if typ[:3] not in ['INT', 'REA', 'TEX']:
                    if igeo is None:
                        igeo = nattr
                nattr += 1

        if igeo is None:
            nlis = nattr        # Anzahl Attribute ohne Geoobjekte
        else:
            nlis = igeo         # Anzahl Attribute ohne Geoobjekte

            for i in range(nlis,nattr):
                if attrlis[i] == gobj:
                    ngeo = i
            if ngeo is None:
                logger.error_code(f'Fehler: Das Geoobjekt konnte in den Listen "TABLES_XXXX" nicht gefunden werden!')
                raise QkanDbError

        # Attributlisten ohne und mit prefixen vorbereiten
        attributes = '\n    '.join(textwrap.wrap(', '.join(attrlis[:nlis])))
        attributes_ex = '\n    '.join(textwrap.wrap(', ex.'.join(attrlis[:nlis])))
        attributes_be = '\n    '.join(textwrap.wrap(', be.'.join(attrlis[:nlis])))
        attributes_t =  '\n    '.join(textwrap.wrap( ', t.'.join(attrlis[:nlis])))
        if gobj is not None:
            geoattr =   f',\n    geom'
            geoattrs =  f',\n    {gobj}'
            geoattr_ex = f',\n    ex.{gobj} AS {gobj}'
            geoattr_be = f',\n    be.{gobj} AS {gobj}'
            geoattr_t  = f',\n    t.{gobj} AS {gobj}'
            objattr = 'objekt, '
        else:
            geoattr = ''
            geoattrs =  ''
            geoattr_ex = ''
            geoattr_be = ''
            geoattr_t = ''
            objattr = ''

        if tabnam in TABLES_UNTERSUCH:
            untersuch = ' AND be.untersuchtag = ex.untersuchtag'
        else:
            untersuch = ''

        # ---------------------------------------------------------------------------------------------------------------------
        # Synchronisationstabelle löschen
        sqls[f'sync_drop_{tabnam}'] = f'''DROP TABLE IF EXISTS sync_{tabnam};'''

        # logger.debug(f'sync_create_{tabnam}:\n')
        # logger.debug(sqls[f'sync_create_{tabnam}'])

        if gobj is not None:
            if ngeo is None:
                logger.error_code(f'Fehler in Tabelle {tabnam}: {gobj=}, aber ngeo = None')
                raise QkanError
            typ = typlis[ngeo]
            sqls[f'sync_drop_{tabnam}_geom'] = f"SELECT DiscardGeometryColumn('sync_{tabnam}', 'geom');"

        # ---------------------------------------------------------------------------------------------------------------------
        # Synchronisationstabelle erstellen
        sqls[f'sync_create_{tabnam}'] = f'''        CREATE TABLE IF NOT EXISTS sync_{tabnam} (
            pk INTEGER PRIMARY KEY,
            pk_best INTEGER,
            pk_ext INTEGER,
            aktion TEXT,
            status INTEGER''' + \
        (',\n    ' if gobj is None else ',\n    objekt TEXT,\n    ') + \
        ',\n    '.join([f'{attr} {typ}' for attr, typ in fieldlis[:nlis] if attr != 'createdat']) + ');'

        # logger.debug(f'sync_create_{tabnam}:\n')
        # logger.debug(sqls[f'sync_create_{tabnam}'])

        if gobj is not None:
            if ngeo is None:
                logger.error_code(f'Fehler in Tabelle {tabnam}: {gobj=}, aber ngeo = None')
                raise QkanError
            typ = typlis[ngeo]
            sqls[f'sync_create_{tabnam}_geom'] = \
            f'''SELECT AddGeometryColumn('sync_{tabnam}', 'geom', :epsg, '{typ}', 2);'''

        sqls[f'sync_reset_{tabnam}'] = f'DELETE FROM sync_{tabnam};'        # nosec B608 - only internal strings

        # ---------------------------------------------------------------------------------------------------------------------
        # Datensätze, die nur in der externen Datenbank vorkommen, Vergleich anhand Objektbezeichnung
        sqls[f'sync_{tabnam}_ext'] = f'''            INSERT INTO sync_{tabnam} (
                pk_best, pk_ext, {objnam}, {objattr}aktion, status,
                {attributes}{geoattr})
            SELECT 
                NULL AS pk_best, ex.pk AS pk_ext, ex.{objnam},''' + \
        ("" if gobj is None else "\n    'Datensatz nicht im Bestand' AS objekt,") + f'''
                'hinzufügen' AS aktion, :status_add AS status,      /* hinzufügen */ 
                ex.{attributes_ex}{geoattr_ex}
              FROM ext.{tabnam} AS ex
              LEFT JOIN main.{tabnam} AS be
              ON be.{objnam} = ex.{objnam}{untersuch}
              WHERE be.pk IS NULL;'''

        # ---------------------------------------------------------------------------------------------------------------------
        # Datensätze, die nur in der bestehenden Datenbank vorkommen, Vergleich anhand Objektbezeichnung
        sqls[f'sync_{tabnam}_local'] = f'''                INSERT INTO sync_{tabnam} (
                    pk_best, pk_ext, {objnam}, {objattr}aktion, status,
                    {attributes}{geoattr})
                SELECT
                    be.pk AS pk_best, NULL AS pk_ext, be.{objnam},''' + \
        ("" if gobj is None else "\n    'Datensatz extern nicht vorhanden' AS objekt,") + f'''
                 'löschen' AS aktion, :status_del AS status,      /* löschen */
                  be.{attributes_be}{geoattr_be}
            FROM main.{tabnam} AS be
            LEFT JOIN ext.{tabnam} AS ex
            ON be.{objnam} = ex.{objnam}{untersuch}
            WHERE ex.pk IS NULL;'''

        # ---------------------------------------------------------------------------------------------------------------------
        # Datensätze mit gleichem Namen, die sich in mindestens einem Attribut unterscheiden
        sql = f'''            INSERT INTO sync_{tabnam} (
                pk_best, pk_ext, {objnam}, {objattr}aktion, status,
                {attributes}{geoattr})
            SELECT
                be.pk AS pk_best,
                ex.pk AS pk_ext,
                ex.{objnam},''' + \
        ("" if gobj is None else f"\n    iif(be.{gobj} <> ex.{gobj}, printf('Geometrie geändert'), '') AS objekt,") + f'''
                'ändern' AS aktion,
                :status_mod AS status'''    # nosec B608 - only internal strings or: note_1
        for attr, typ in fieldlis[:nlis]:
            if attr == 'createdat':
                pass
            elif typ == 'TEXT':
                sql += (f",\n    iif(be.{attr} <> ex.{attr}, printf('%s -> %s', be.{attr}, ex.{attr}), '') "
                        f"AS {attr}")                                   # nosec B608 - note_1
            elif typ[:3] == 'INT':
                sql += (f",\n    iif(be.{attr} <> ex.{attr}, printf('%d -> %d', be.{attr}, ex.{attr}), '') "
                        f"AS {attr}")                                   # nosec B608 - note_1
            elif typ == 'REAL':
                sql += (f",\n    iif(coalesce(abs(be.{attr} - ex.{attr}), 0) > 0.001, printf('%.3f -> %.3f', "
                        f"be.{attr}, ex.{attr}), '') AS {attr}")        # nosec B608 - note_1
            else:
                logger.error_code(f'Fehler: {attr=}, {typ=}')
                raise QkanError
        sql += ("" if gobj is None else f",\n    be.{gobj} AS {gobj}") + f'''
            FROM (
                SELECT *
                FROM main.{tabnam} AS t
                GROUP BY t.{objnam}
                HAVING count() = 1
            ) AS be
            JOIN (
                SELECT * 
                FROM ext.{tabnam} AS t
                GROUP BY t.{objnam}
                HAVING count() = 1
            ) AS ex
            ON ex.{objnam} = be.{objnam}
            WHERE
            '''         # nosec B608 - only internal strings or: note_1
        prefix = ''
        for attr, typ in fieldlis[:nlis]:
            if attr == 'createdat':
                pass
            elif typ in ['TEXT', 'INT', 'INTEGER']:
                sql += prefix + f"be.{attr} <> ex.{attr}"
            elif typ == 'REAL':
                sql += prefix + f"coalesce(abs(be.{attr} - ex.{attr}), 0) > 0.001"
            if prefix == '':
                prefix = ' OR\n    '
        sql += (";" if gobj is None else prefix + f"be.{gobj} <> ex.{gobj};")
        sqls[f'sync_{tabnam}_dif'] = sql

        # ---------------------------------------------------------------------------------------------------------------------
        # Doppelte Datensätze in externer Datenbank
        if tabnam not in TABLES_UNTERSUCH:
            sql = f'''            WITH ex AS (
                    SELECT {objnam}, count() AS anz
                    FROM ext.{tabnam}
                    GROUP BY {objnam}
                ),
                be AS (
                    SELECT DISTINCT {objnam}
                    FROM main.{tabnam}
                )
                INSERT INTO sync_{tabnam} (
                    pk_best, pk_ext, {objnam}, {objattr}aktion, status,
                    {attributes}{geoattr})
                SELECT
                    NULL AS pk_best, t.pk AS pk_ext, t.{objnam},'''     # nosec B608 - only internal strings or: note_1
            sql += "" if gobj is None else "\n    '' AS objekt,"
            sql += f'''                    'Bezeichnung extern nicht eindeutig' AS aktion, NULL AS status,
                    t.{attributes_t}{geoattr_t}
                FROM {tabnam} AS t
                JOIN ex ON ex.{objnam} = t.{objnam}
                JOIN be ON be.{objnam} = t.{objnam}
                WHERE ex.anz > 1;'''                                    # nosec B608 - only internal strings or: note_1
            sqls[f'sync_{tabnam}_ex_redundant'] = sql

        # ---------------------------------------------------------------------------------------------------------------------
        # Doppelte Datensätze in bestehender Datenbank
            sql = f'''            WITH be AS (
                SELECT {objnam}, count() AS anz
                FROM main.{tabnam}
                GROUP BY {objnam}
            ),
            ex AS (
                SELECT DISTINCT {objnam}
                FROM ext.{tabnam}
            )
            INSERT INTO sync_{tabnam} (
                pk_best, pk_ext, {objnam}, {objattr}aktion, status,
                {attributes}{geoattr})
            SELECT
                t.pk AS pk_best, NULL AS pk_ext, t.{objnam},'''     # nosec B608 - only internal strings or: note_1
            sql += "" if gobj is None else "\n    '' AS objekt,"
            sql += f'''                'Bezeichnung im Bestand nicht eindeutig' AS aktion, NULL AS status,
                t.{attributes_t}{geoattr_t}
            FROM {tabnam} AS t
            JOIN be ON be.{objnam} = t.{objnam}
            JOIN ex ON ex.{objnam} = t.{objnam}
            WHERE be.anz > 1;'''                                    # nosec B608 - only internal strings or: note_1
            sqls[f'sync_{tabnam}_be_redundant'] = sql

        # ---------------------------------------------------------------------------------------------------------------------
        # Datensätze hinzufügen
        sql = f'''            INSERT INTO main.{tabnam} (
                {objnam}, {attributes}{geoattrs})
            SELECT
                ex.{objnam}, ex.{attributes_ex}'''                      # nosec B608 - only internal strings or: note_1
        sql += "" if gobj is None else f",\n    ex.{gobj} AS {gobj}"    # nosec B608 - only internal strings
        sql += f'''            FROM ext.{tabnam} AS ex
            JOIN sync_{tabnam} AS sy ON ex.pk = sy.pk_ext
            WHERE sy.aktion = 'hinzufügen'
              AND sy.status;'''                                         # nosec B608 - only internal strings
        sqls[f'sync_{tabnam}_add'] = sql

        # ---------------------------------------------------------------------------------------------------------------------
        # Datensätze löschen
        sqls[f'sync_{tabnam}_del'] = f'''            DELETE FROM main.{tabnam}
            WHERE pk IN (
                SELECT pk_best
                FROM sync_{tabnam}
                WHERE aktion = 'löschen'
                  AND status);'''   # nosec B608 - only internal strings

        # ---------------------------------------------------------------------------------------------------------------------
        # Datensätze ändern
        sql = f'''            UPDATE main.{tabnam}
            SET\n    '''     # nosec B608 - only internal strings
        sql += ',\n    '.join([f'{el} = mo.{el}' for el in attrlis[:nlis]])     # nosec B608 - note_1
        sql += '\n' if gobj is None else f',\n    {gobj} = mo.{gobj}\n'         # nosec B608 - only internal strings
        sql += '''           FROM (
           SELECT
               sy.pk_best AS pk_best'''     # nosec B608 - only internal strings or: note_1
        for attr, typ in fieldlis[:nlis]:
            if typ == 'TEXT':
                sql += (f",\n        iif(sy.{attr} IS NOT NULL AND sy.{attr} <> '', ex.{attr}, be.{attr}) "
                        f"AS {attr}")           # nosec B608 - note_1
            elif typ in ['REAL', 'INT', 'INTEGER']:
                sql += (f",\n        iif(sy.{attr} IS NOT NULL, ex.{attr}, be.{attr}) "
                        f"AS {attr}")           # nosec B608 - note_1
            else:
                logger.error_code(f'Fehler: {attr=}, {typ=}')
                raise QkanError
        sql += ("" if gobj is None else f",\n        iif(sy.objekt IS NOT NULL AND sy.objekt <> '', ex.{gobj}, be.{gobj}) AS {gobj}")
        sql += f'''
                FROM sync_{tabnam} AS sy
                JOIN main.{tabnam} AS be ON be.pk = sy.pk_best
                JOIN ext.{tabnam} AS ex ON ex.pk = sy.pk_ext
                WHERE sy.aktion = 'ändern'
                  AND status
            ) AS mo
            WHERE main.{tabnam}.pk = mo.pk_best;'''
        sqls[f'sync_{tabnam}_mod'] = sql
        # ---------------------------------------------------------------------------------------------------------------------
        # Datensätze auflisten
        sqls[f'sync_{tabnam}_prot'] = f'SELECT * FROM sync_{tabnam} WHERE status;'  # nosec B608 - only internal strings

    db_qkan.sqls.update(sqls)

    # Nur zur Kontrolle
    # with open(
    #     'C:/FHAC/hoettges/Kanalprogramme/QKan/test/work/sqlite_check.yml',
    #     'w',
    #     encoding = 'utf-8'
    # ) as fw:
    #     fw.write(f'Aktuelles Verzeichnis: {os.getcwd()}\n')
    #     fw.write(f'{tables=}\n')
    #     for key in db_qkan.sqls.keys():
    #         fw.write(f"{key}:\n{db_qkan.sqls[key]}\n\n")
    # del fw
    #
    # anz = len(db_qkan.sqls)
    # logger.debug(f"Anzahl SQLs in 'sync': {anz}")
    # for key in db_qkan.sqls['sync'].keys():
    #     logger.debug(f"{key}:\n{db_qkan.sqls['sync'][key]}\n")
