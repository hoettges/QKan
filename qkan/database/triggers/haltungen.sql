CREATE TRIGGER IF NOT EXISTS trig_new_hal        -- Datenuebernahme aus Schaechten
AFTER INSERT ON haltungen
BEGIN
    UPDATE haltungen SET 
    haltnam = (
        SELECT schnam || '.1'
        FROM schaechte AS s
        WHERE ST_Within(s.geop, buffer(ST_PointN(new.geom, 1), 0.1)) = 1
        AND s.ROWID IN (
            SELECT ROWID
            FROM SpatialIndex
            WHERE f_table_name = 'schaechte'
                AND F_geometry_column = 'geop'
                AND search_frame = ST_PointN(new.geom, 1))
    )
    WHERE pk = new.pk AND (haltnam = '' OR haltnam IS NULL);

    UPDATE haltungen SET 
    laenge = round(ST_Length(new.geom), 3)
    WHERE pk = new.pk AND (laenge = 0 OR laenge IS NULL);

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

    UPDATE haltungen SET 
    sohleoben = (
        SELECT sohlhoehe
        FROM schaechte AS s
        WHERE ST_Within(s.geop, buffer(ST_PointN(new.geom, 1), 0.1)) = 1
        AND s.ROWID IN (
            SELECT ROWID
            FROM SpatialIndex
            WHERE f_table_name = 'schaechte'
                AND F_geometry_column = 'geop'
                AND search_frame = ST_PointN(new.geom, 1))
    )
    WHERE pk = new.pk AND sohleoben IS NULL;

    UPDATE haltungen SET 
    sohleunten = (
        SELECT sohlhoehe
        FROM schaechte AS s
        WHERE ST_Within(s.geop, buffer(ST_PointN(new.geom, -1), 0.1)) = 1
        AND s.ROWID IN (
            SELECT ROWID
            FROM SpatialIndex
            WHERE f_table_name = 'schaechte'
                AND F_geometry_column = 'geop'
                AND search_frame = ST_PointN(new.geom, -1))
    )
    WHERE pk = new.pk AND sohleunten IS NULL;
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
    laenge = coalesce(round(ST_Length(new.geom), 3), OLD.laenge)
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

    UPDATE haltungen SET 
    sohleoben = (
        SELECT coalesce(sohlhoehe, OLD.sohleoben)
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
    sohleunten = (
        SELECT coalesce(sohlhoehe, OLD.sohleunten)
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
