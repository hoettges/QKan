CREATE TRIGGER IF NOT EXISTS trig_new_hal        -- Datenuebernahme aus Schaechten
AFTER INSERT ON haltungen
BEGIN
    UPDATE haltungen
    SET haltnam = (
        WITH startpunkt AS (
            SELECT coalesce(nullif(trim(new.schoben), ''), (
                SELECT s.schnam FROM schaechte AS s
                WHERE s.ROWID IN (
                    SELECT ROWID FROM SpatialIndex
                    WHERE f_table_name = 'schaechte' AND f_geometry_column = 'geop'
                      AND search_frame = buffer(ST_StartPoint(new.geom), 0.1))
                  AND ST_Distance(s.geop, ST_StartPoint(new.geom)) <= 0.1
                ORDER BY ST_Distance(s.geop, ST_StartPoint(new.geom)), s.pk LIMIT 1
            )) AS name
        ), reihe AS (
            SELECT name, CASE WHEN name GLOB '*[0-9]'
                              THEN rtrim(name, '0123456789') ELSE '' END AS prefix
            FROM startpunkt
        ), nummern AS (
            SELECT substr(h.haltnam, length(r.prefix) + 1) AS ziffern
            FROM haltungen AS h, reihe AS r
            WHERE h.pk <> new.pk
              AND h.haltnam GLOB '*[0-9]'
              AND rtrim(h.haltnam, '0123456789') = r.prefix
        )
        SELECT CASE WHEN r.name IS NOT NULL AND NOT EXISTS (
                         SELECT 1 FROM haltungen AS h WHERE h.haltnam = r.name AND h.pk <> new.pk)
                    THEN r.name
                    ELSE r.prefix || (SELECT printf('%0*d', coalesce(max(length(ziffern)), 1),
                                          coalesce(max(CAST(ziffern AS INTEGER)), 0) + 1) FROM nummern)
               END FROM reihe AS r
    )
    WHERE pk = new.pk AND nullif(trim(new.haltnam), '') IS NULL;

    UPDATE haltungen SET
    schoben = (
        SELECT schnam
        FROM schaechte AS s
        WHERE ST_Within(s.geop, buffer(ST_PointN(new.geom, 1), 0.1)) = 1
        AND s.ROWID IN (
            SELECT ROWID
            FROM SpatialIndex
            WHERE f_table_name = 'schaechte'
                AND F_geometry_column = 'geop'
                AND search_frame = ST_PointN(new.geom, 1))
    )
    WHERE pk = new.pk AND (schoben = '' OR schoben IS NULL);

    UPDATE haltungen SET 
    schunten = (
        SELECT schnam
        FROM schaechte AS s
        WHERE ST_Within(s.geop, buffer(ST_PointN(new.geom, -1), 0.1)) = 1
        AND s.ROWID IN (
            SELECT ROWID
            FROM SpatialIndex
            WHERE f_table_name = 'schaechte'
                AND F_geometry_column = 'geop'
                AND search_frame = ST_PointN(new.geom, -1))
    )
    WHERE pk = new.pk AND (schunten = '' OR schunten IS NULL);
END;

CREATE TRIGGER IF NOT EXISTS trig_mod_hal        -- Datenuebernahme aus Schaechten
AFTER UPDATE OF geom ON haltungen
BEGIN
    UPDATE haltungen SET 
    schoben = (
        SELECT coalesce(schnam, OLD.schoben)
        FROM schaechte AS s
        WHERE ST_Within(s.geop, buffer(ST_PointN(new.geom, 1), 0.1)) = 1
        AND s.ROWID IN (
            SELECT ROWID
            FROM SpatialIndex
            WHERE f_table_name = 'schaechte'
                AND F_geometry_column = 'geop'
                AND search_frame = ST_PointN(new.geom, 1))
    )
    WHERE pk = old.pk;

    UPDATE haltungen SET 
        laenge = NULL,
        sohleoben = NULL,
        sohleunten = NULL
    WHERE pk = old.pk;

    UPDATE haltungen SET 
    schunten = (
        SELECT coalesce(schnam, OLD.schunten)
        FROM schaechte AS s
        WHERE ST_Within(s.geop, buffer(ST_PointN(new.geom, -1), 0.1)) = 1
        AND s.ROWID IN (
            SELECT ROWID
            FROM SpatialIndex
            WHERE f_table_name = 'schaechte'
                AND F_geometry_column = 'geop'
                AND search_frame = ST_PointN(new.geom, -1))
    )
    WHERE pk = old.pk;
END;
