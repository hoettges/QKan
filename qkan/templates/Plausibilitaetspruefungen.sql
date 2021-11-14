DELETE FROM pruefsql WHERE gruppe = 'Netzstruktur' AND warntext IN ('Schacht oben fehlerhaft', 'Schacht unten fehlerhaft');
DELETE FROM pruefsql WHERE gruppe = 'HYSTEM-EXTRAN' AND warntext = 'Abflussparameter fehlen';
INSERT INTO pruefsql (gruppe, warntext, warntyp, warnlevel, sql, layername, attrname)
SELECT pn.gruppe, pn.warntext, pn.warntyp, pn.warnlevel, pn.sql, pn.layername, pn.attrname FROM
(SELECT column1 AS gruppe, column2 AS warntext, column3 AS warntyp, column4 AS warnlevel, column5 AS sql, column6 AS layername, column7 AS attrname FROM 
(VALUES
('Netzstruktur', 'Schacht oben fehlerhaft', 'Fehler', 9, 
 'SELECT haltnam, ''Schacht oben fehlerhaft'' AS bemerkung FROM haltungen AS ha LEFT JOIN schaechte AS so ON ha.schoben = so.schnam WHERE within(so.geop, buffer(pointn(ha.geom,1), 0.1)) <> 1', 
 'Haltungen nach Typ', 'haltnam'),
('Netzstruktur', 'Schacht unten fehlerhaft', 'Fehler', 9, 'SELECT haltnam, ''Schacht unten fehlerhaft'' AS bemerkung FROM haltungen AS ha LEFT JOIN schaechte AS su ON ha.schunten = su.schnam WHERE within(su.geop, buffer(pointn(ha.geom,-1), 0.1)) <> 1', 'Haltungen nach Typ', 'haltnam'),
('HYSTEM-EXTRAN', 'Abflussparameter fehlen', 'Fehler', 9, 'SELECT flaechen.flnam, ''Abflussparameter fehlen'' AS bemerkung FROM flaechen LEFT JOIN abflussparameter ON flaechen.abflussparameter = abflussparameter.apnam WHERE abflussparameter.pk IS NULL GROUP BY flaechen.flnam', 'Abflussparameter', 'flnam'),
('Netzstruktur', 'Kreuzende Haltungen', 'Warnung', 6, 
'SELECT
     haltna1 AS haltnam, 
     printf("Theoretischer Abstand zu Haltung %s beträgt d = %.2f", haltna2, abs((huax-hoax)*vx+(huay-hoay)*vy+(huaz-hoaz)*vz)/SQRT(vx*vx+vy*vy+vz*vz)) as bemerkung
FROM (
  SELECT 
    haltna1, haltna2, durchob, durchun, hoehob, hoehun, 
    hoax, hoay, hoaz, hoex, hoey, hoez, huax, huay, huaz, huex, huey, huez, 
    (hoey-hoay)*(huez-huaz)-(hoez-hoaz)*(huey-huay) AS vx, 
    (hoez-hoaz)*(huex-huax)-(hoex-hoax)*(huez-huaz) AS vy,
    (hoex-hoax)*(huey-huay)-(hoey-hoay)*(huex-huax) AS vz
  FROM (
    SELECT
      ho.haltnam            AS haltna1, 
      hu.haltnam            AS haltna2, 
      ho.durchm             AS durchob, 
      hu.durchm             AS durchun, 
      ho.hoehe              AS hoehob, 
      hu.hoehe              AS hoehun, 
      x(PointN(ho.geom,1))  AS hoax, 
      y(PointN(ho.geom,1))  AS hoay, 
      ho.sohleoben          AS hoaz, 
      x(PointN(ho.geom,-1)) AS hoex, 
      y(PointN(ho.geom,-1)) AS hoey, 
      ho.sohleunten         AS hoez, 
      x(PointN(hu.geom,1))  AS huax, 
      y(PointN(hu.geom,1))  AS huay, 
      hu.sohleoben          AS huaz, 
      x(PointN(hu.geom,-1)) AS huex, 
      y(PointN(hu.geom,-1)) AS huey, 
      hu.sohleunten         AS huez
    FROM (
      SELECT
        ha.haltnam AS haltnam, 
        ha.schoben AS schoben,
        ha.schunten AS schunten,
        ha.geom AS geom, 
        COALESCE(ha.sohleoben, so.sohlhoehe) AS sohleoben, 
        COALESCE(ha.sohleunten, su.sohlhoehe) AS sohleunten,
        MAX(ha.hoehe, ha.breite) AS durchm, 
        CASE WHEN ha.hoehe = 0 THEN ha.breite ELSE ha.hoehe END AS hoehe
      FROM haltungen AS ha 
      INNER JOIN schaechte AS so 
      ON ha.schoben = so.schnam
      INNER JOIN schaechte AS su 
      ON ha.schunten = su.schnam
    ) AS ho 
    INNER JOIN (
      SELECT
        ha.haltnam AS haltnam, 
        ha.schoben AS schoben,
        ha.schunten AS schunten,
        ha.geom AS geom, 
        COALESCE(ha.sohleoben, so.sohlhoehe) AS sohleoben, 
        COALESCE(ha.sohleunten, su.sohlhoehe) AS sohleunten,
        MAX(ha.hoehe, ha.breite) AS durchm, 
        CASE WHEN ha.hoehe = 0 THEN ha.breite ELSE ha.hoehe END AS hoehe
      FROM haltungen AS ha 
      INNER JOIN schaechte AS so 
      ON ha.schoben = so.schnam
      INNER JOIN schaechte AS su 
      ON ha.schunten = su.schnam
    ) AS hu
    ON Distance(ho.geom, hu.geom) < 0.5 + (ho.durchm + hu.durchm) / 2.0
    WHERE
      ho.haltnam <> hu.haltnam AND 
      ho.schoben not in (hu.schoben, hu.schunten) AND 
      ho.schunten not in (hu.schoben, hu.schunten) AND 
      ho.sohleoben + ho.sohleunten >= hu.sohleoben + hu.sohleunten
    )
  )
WHERE
  abs((huax-hoax)*vx+(huay-hoay)*vy+(huaz-hoaz)*vz)/SQRT(vx*vx+vy*vy+vz*vz) <= 0.5 +
  CASE WHEN MAX(huaz, huez) + durchun < MIN(hoaz, hoez) 
    THEN hoehun
    ELSE (durchob + durchun) / 2.0 
  END
', 'Haltungen nach Typ', 'haltnam'))) AS pn
LEFT JOIN pruefsql AS ps
ON (pn.gruppe = ps.gruppe AND pn.warntext = ps.warntext)
WHERE ps.warntext IS NULL;
