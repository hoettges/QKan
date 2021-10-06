INSERT INTO pruefsql (gruppe, warntext, warntyp, warnlevel, sql, layername, attrname)
SELECT pn.gruppe, pn.warntext, pn.warntyp, pn.warnlevel, pn.sql, pn.layername, pn.attrname FROM
(SELECT column1 AS gruppe, column2 AS warntext, column3 AS warntyp, column4 AS warnlevel, column5 AS sql, column6 AS layername, column7 AS attrname FROM 
(VALUES
('Netzstruktur', 'Schacht oben fehlerhaft', 'Fehler', 9, 'SELECT haltnam FROM haltungen AS ha LEFT JOIN schaechte AS so ON ha.schoben = so.schnam WHERE within(so.geop, buffer(pointn(ha.geom,1), 0.1)) <> 1', 'Haltungen nach Typ', 'haltnam'),
('Netzstruktur', 'Schacht unten fehlerhaft', 'Fehler', 9, 'SELECT haltnam FROM haltungen AS ha LEFT JOIN schaechte AS su ON ha.schunten = su.schnam WHERE within(su.geop, buffer(pointn(ha.geom,-1), 0.1)) <> 1', 'Haltungen nach Typ', 'haltnam'),
('HYSTEM-EXTRAN', 'Abflussparameter fehlen', 'Fehler', 9, 'SELECT flaechen.flnam FROM flaechen LEFT JOIN abflussparameter ON flaechen.abflussparameter = abflussparameter.apnam WHERE abflussparameter.pk IS NULL GROUP BY flaechen.flnam', 'Abflussparameter', 'flnam'))) AS pn
LEFT JOIN pruefsql AS ps
ON (pn.gruppe = ps.gruppe AND pn.warntext = ps.warntext)
WHERE ps.warntext IS NULL;
