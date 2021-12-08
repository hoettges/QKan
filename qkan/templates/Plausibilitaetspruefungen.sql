DELETE FROM pruefsql WHERE gruppe = 'Netzstruktur' AND warntext IN ('Schacht oben fehlerhaft', 'Schacht unten fehlerhaft');
DELETE FROM pruefsql WHERE gruppe = 'HYSTEM-EXTRAN' AND warntext IN ('Abflussparameter fehlen', 'Schwerpunktlaufzeiten fehlen');
INSERT INTO pruefsql (gruppe, warntext, warntyp, warnlevel, sql, layername, attrname)
SELECT pn.gruppe, pn.warntext, pn.warntyp, pn.warnlevel, pn.sql, pn.layername, pn.attrname FROM
(SELECT column1 AS gruppe, column2 AS warntext, column3 AS warntyp, column4 AS warnlevel, column5 AS sql, column6 AS layername, column7 AS attrname FROM 
(VALUES
('Netzstruktur', 'Schacht oben fehlerhaft', 'Fehler', 9, 
 'SELECT haltnam, ''Schacht oben fehlerhaft'' AS bemerkung FROM haltungen AS ha LEFT JOIN schaechte AS so ON ha.schoben = so.schnam WHERE within(so.geop, buffer(pointn(ha.geom,1), 0.1)) <> 1', 
 'Haltungen nach Typ', 'haltnam'),
('Netzstruktur', 'Schacht unten fehlerhaft', 'Fehler', 9, 'SELECT haltnam, ''Schacht unten fehlerhaft'' AS bemerkung FROM haltungen AS ha LEFT JOIN schaechte AS su ON ha.schunten = su.schnam WHERE within(su.geop, buffer(pointn(ha.geom,-1), 0.1)) <> 1', 'Haltungen nach Typ', 'haltnam'),
('HYSTEM-EXTRAN', 'Abflussparameter fehlen', 'Fehler', 9, 'SELECT flaechen.flnam, ''Abflussparameter fehlen'' AS bemerkung FROM flaechen LEFT JOIN abflussparameter ON flaechen.abflussparameter = abflussparameter.apnam WHERE abflussparameter.pk IS NULL GROUP BY flaechen.flnam', 'Abflussparameter', 'flnam'),
('HYSTEM-EXTRAN', 'Schwerpunktlaufzeiten fehlen', 'Fehler', 9, 'SELECT flnam, printf("Spalte ""fliesszeitflaeche"" in Layer ""Anbindungen Flächen"" in %d Datensätzen leer (nur 5 Datensätze exemplarisch aufgelistet)", (SELECT count(*) FROM linkfl WHERE fliesszeitflaeche IS NULL)) AS bemerkung FROM linkfl WHERE fliesszeitflaeche IS NULL LIMIT 5', 'Anbindungen Flächen', 'flnam'),
('HYSTEM-EXTRAN', 'Simulationsstatus fehlt oder nicht in Tabelle "Simulationsstatus"', 'Fehler', 9, 'SELECT s.schnam, printf("Spalte simstatus = %s in Spalte leer oder nicht in Simulationsstatus (nur 1 exemplarisch aufgelistet!)", s.simstatus) AS bemerkung FROM schaechte AS s LEFT JOIN simulationsstatus AS u ON s.simstatus = u.bezeichnung WHERE u.bezeichnung IS NULL GROUP BY s.simstatus', 'Schächte', 'schnam'),
('HYSTEM-EXTRAN', 'Neigungsklasse fehlt', 'Fehler', 9, 'SELECT flnam, printf("Spalte ""neigung"" in Layer ""Flächen"" in %d Datensätzen leer (nur 5 Datensätze exemplarisch aufgelistet)", (SELECT count(*) FROM flaechen WHERE neigung IS NULL)) AS bemerkung FROM flaechen WHERE neigung IS NULL LIMIT 5', 'Flächen', 'flnam'),
('HYSTEM-EXTRAN', 'Profil fehlt in Layer "Profile"', 'Fehler', 9,
'SELECT h.haltnam, printf("Profil ''%s'' fehlt in Layer Profile", h.profilnam) AS bemerkung FROM haltungen AS h
LEFT JOIN profile AS p
ON h.profilnam = p.profilnam
WHERE p.profilnam IS NULL
GROUP BY h.profilnam', 'Haltungen nach Typ', 'haltnam'),
('Kreuzende Haltungen', 'Kreuzende Haltungen', 'Warnung', 6, 
'SELECT 
  haltna1, haltna2, hoehob, hoehun, 
  abs((p3x-p1x)*ex+(p3y-p1y)*ey+(p3z-p1z)*ez)/SQRT(ex*ex+ey*ey+ez*ez) AS abstkreuz, 
  abs(L13/SQRT(L12))         AS abstpar,
  ((sx-p1x)*(p2x-p1x)+(sy-p1y)*(p2y-p1y))*((sx-p2x)*(p2x-p1x)+(sy-p2y)*(p2y-p1y)) AS d1, 
  ((sx-p3x)*(p4x-p3x)+(sy-p3y)*(p4y-p3y))*((sx-p4x)*(p4x-p3x)+(sy-p4y)*(p4y-p3y)) AS d2, 
  MAX(0, L12, L13, L14)-MIN(0, L12, L13, L14)-ABS(L12)-ABS(L34)                   AS d3
FROM (
  SELECT 
    haltna1, haltna2, hoehob, hoehun, 
    p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, ex, ey, ez,
    CASE WHEN abs(det) > 0.000001 * bet THEN
      p1x+(p2x-p1x)*((p3x-p1x)*(p3y-p4y)-(p3y-p1y)*(p3x-p4x))/det ELSE NULL END     AS sx,
    CASE WHEN abs(det) > 0.000001 * bet THEN
      p1y+(p2y-p1y)*((p3x-p1x)*(p3y-p4y)-(p3y-p1y)*(p3x-p4x))/det ELSE NULL END     AS sy,
    ((p2x-p1x)*(p2x-p1x)+(p2y-p1y)*(p2y-p1y))                                       AS L12,
    ((p3x-p1x)*(p2x-p1x)+(p3y-p1y)*(p2y-p1y))                                       AS L13,
    ((p4x-p1x)*(p2x-p1x)+(p4y-p1y)*(p2y-p1y))                                       AS L14,
    ((p4x-p3x)*(p2x-p1x)+(p4y-p3y)*(p2y-p1y))                                       AS L34
  FROM (
    SELECT 
      haltna1, haltna2, hoehob, hoehun, 
      p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, 
      (p2y-p1y)*(p4z-p3z)-(p2z-p1z)*(p4y-p3y) AS ex, 
      (p2z-p1z)*(p4x-p3x)-(p2x-p1x)*(p4z-p3z) AS ey,
      (p2x-p1x)*(p4y-p3y)-(p2y-p1y)*(p4x-p3x) AS ez,
      ((p2x-p1x)*(p3y-p4y)-(p2y-p1y)*(p3x-p4x)) AS det,
      ((p2x-p1x)*(p3x-p4x)+(p2y-p1y)*(p3y-p4y)) AS bet
    FROM (
      SELECT
        ho.haltnam            AS haltna1, 
        hu.haltnam            AS haltna2, 
        ho.hoehe              AS hoehob, 
        hu.hoehe              AS hoehun, 
        x(PointN(ho.geom,1))  AS p1x, 
        y(PointN(ho.geom,1))  AS p1y, 
        ho.zoben              AS p1z, 
        x(PointN(ho.geom,-1)) AS p2x, 
        y(PointN(ho.geom,-1)) AS p2y, 
        ho.zunten             AS p2z, 
        x(PointN(hu.geom,1))  AS p3x, 
        y(PointN(hu.geom,1))  AS p3y, 
        hu.zoben              AS p3z, 
        x(PointN(hu.geom,-1)) AS p4x, 
        y(PointN(hu.geom,-1)) AS p4y, 
        hu.zunten             AS p4z
      FROM (
        SELECT
          ha.haltnam AS haltnam, 
          ha.schoben AS schoben,
          ha.schunten AS schunten,
          ha.geom AS geom, 
          COALESCE(ha.sohleoben, so.sohlhoehe)  + COALESCE(ha.hoehe, ha.breite)*0.5 AS zoben, 
          COALESCE(ha.sohleunten, su.sohlhoehe) + COALESCE(ha.hoehe, ha.breite)*0.5 AS zunten,
          COALESCE(ha.hoehe, ha.breite) AS durchm, 
          CASE WHEN COALESCE(ha.hoehe, 0) = 0 THEN ha.breite ELSE ha.hoehe END AS hoehe
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
          COALESCE(ha.sohleoben, so.sohlhoehe)  + COALESCE(ha.hoehe, ha.breite)*0.5 AS zoben, 
          COALESCE(ha.sohleunten, su.sohlhoehe) + COALESCE(ha.hoehe, ha.breite)*0.5 AS zunten,
          COALESCE(ha.hoehe, ha.breite) AS durchm, 
          CASE WHEN COALESCE(ha.hoehe, 0) = 0 THEN ha.breite ELSE ha.hoehe END AS hoehe
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
        ho.zoben + ho.zunten >= hu.zoben + hu.zunten
      )
    )
  )
WHERE
CASE WHEN d1 IS NOT NULL AND d1 <= 0 AND d2 <= 0
    THEN abstkreuz <= (hoehob + hoehun) / 2.0 + 0.5
WHEN d1 IS NULL AND d3 <= 0
    THEN abstpar <= (hoehob + hoehun) / 2.0 + 0.5
ELSE FALSE END
', 'Haltungen nach Typ', 'haltnam'))) AS pn
LEFT JOIN pruefsql AS ps
ON (pn.gruppe = ps.gruppe AND pn.warntext = ps.warntext)
WHERE ps.warntext IS NULL;
