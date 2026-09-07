/* SQL-Abfragen für das Plausibilitätsprüfungs-Tool

Diese Datei wird beim Öffnen des Tools als SQL-Datei ausgeführt und fügt noch nicht in der Tabelle 'pruefsql' enthaltene Datensätze hinzu. 

Achtung: Innerhalb des SQL-Statements müssen Anführungsstriche doppelt gesetzt werden (''), weil das SQL-Statement selbst
schon ein String ist!

Die Attribute der Datensätze haben folgende Bedeutung:
 - gruppe: Bezeichnung erscheint im Formular und dient der Auswahl
 - warnbez: interne Bezeichnung. Muss eindeutig sein.
 - warntyp: Erscheint nach der Ausführung in der Tabelle 'Fehlerliste'
 - warnlevel: Erscheint nach der Ausführung in der Tabelle 'Fehlerliste': Gewichtung des Fehlers (1-9)
 - sql: SQL-Anweisung mit folgenden Attributen:
    - objid: Attribut, das zur Identifikation des fehlerhaften Objektes verwendet werden kann, meistens 'pk AS objid'
    - bemerkung: wird in der Fehlerliste in der Spalte 'Warntext' angezeigt
 - layername: Name des Layers, in dem sich das fehlerhafte Objekt befindet
 - attrname: Name des Attributs (string), anhand dessen das fehlerhafte Objekt in der entsprechenden Aktion im Layer "Fehlerliste" identifiziert werden kann 
 
 Die Gruppe muss in der DELETE-Abfrage ergänzt werden, damit Sie beim Aufruf der Plausibilitätskontrolle aktualisiert werden kann.
 
 Hinweis zur Fehlersuche: Diese Datei kann im SQL-Fenster des DB-Browser (bei geöffneter QKan-Datenbank) ausgeführt werden. 
 */

/* Löschen aller QKan-Standardabfragen, erkennbar am Schluss des Feldes warntext: */
DELETE FROM pruefsql WHERE gruppe IN ('Netzstruktur', 'Geoobjekte', 'HYSTEM-EXTRAN', 'Zustandsklassen', 'Kreuzende Haltungen (3D, braucht sehr lang!)', 'Kreuzende Haltungen (im Plan)', 'M150');

INSERT INTO pruefsql (gruppe, warntext, warntyp, warnlevel, sql, layername, attrname)
SELECT pn.gruppe, pn.warnbez, pn.warntyp, pn.warnlevel, pn.sql, pn.layername, pn.attrname FROM
(   SELECT column1 AS gruppe, column2 AS warnbez, column3 AS warntyp, column4 AS warnlevel, column5 AS sql, column6 AS layername, column7 AS attrname FROM 
    (   VALUES

('Netzstruktur', 'Schacht oben mehr als 1.0 m von Haltungsende entfernt', 'Fehler', 9, 
    'SELECT ha.pk AS objid, printf(''Schacht oben "%s" mehr als 1.0 m von Ende der Haltung "%s" entfernt'', so.schnam, ha.haltnam) AS bemerkung
    FROM haltungen AS ha
    LEFT JOIN schaechte AS so ON ha.schoben = so.schnam
    WHERE within(so.geop, buffer(pointn(ha.geom,1), 1.0)) <> 1 AND (ha.haltungstyp = ''Haltung'' OR ha.haltungstyp IS NULL)',
 'Haltungen', 'pk'),

('Netzstruktur', 'Schacht unten mehr als 1.0 m von Haltungsende entfernt', 'Fehler', 9, 
    'SELECT ha.pk AS objid, printf(''Schacht unten "%s" mehr als 1.0 m von Ende der Haltung "%s" entfernt'', su.schnam, ha.haltnam) AS bemerkung
    FROM haltungen AS ha
    LEFT JOIN schaechte AS su ON ha.schunten = su.schnam
    WHERE within(su.geop, buffer(pointn(ha.geom,-1), 1.0)) <> 1 AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)',
 'Haltungen', 'pk'),

('Kreuzende Haltungen (im Plan)', 'Zwei Haltungen kreuzen sich', 'Fehler', 9,
    'WITH haltungen_selected AS (SELECT ROWID, pk, geom, haltnam, schoben, schunten FROM haltungen WHERE rwanschluss = 1 AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)),
    fls AS (SELECT ROWID, pk, geom, haltnam, schoben, schunten,
		MakePolygon(AddPoint(AddPoint(AddPoint(
						MakeLine(pointn(geom,1),makepoint(x(centroid(geom))-(y(pointn(geom,-1))-y(pointn(geom,1)))*0.01,y(centroid(geom))+(x(pointn(geom,-1))-x(pointn(geom,1)))*0.01)),
						pointn(geom,-1)),
					makepoint(x(centroid(geom))+(y(pointn(geom,-1))-y(pointn(geom,1)))*0.01,y(centroid(geom))-(x(pointn(geom,-1))-x(pointn(geom,1)))*0.01)),pointn(geom,1))
		) AS geof
	FROM
		haltungen_selected 
    )
    SELECT n1.pk AS objid, printf(''Haltung "%s" und "%s" kreuzen sich. Bei einer von beiden muss der Status RW-Anschlüsse deaktiviert werden!'', n1.haltnam, n2.haltnam) AS bemerkung
    FROM fls AS n1 JOIN fls AS n2 ON ST_Intersects(n1.geof, n2.geof) = 1
    WHERE 
    	n1.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name=''haltungen'' AND search_frame=n2.geof) 
      AND n1.pk <> n2.pk
      AND n1.schoben not in (n2.schunten, n2.schoben)
      AND n2.schoben not in (n1.schunten, n1.schoben)
      AND n1.schunten not in (n2.schunten, n2.schoben)
      AND n2.schunten not in (n1.schunten, n1.schoben)',
'Haltungen', 'pk'),

('Netzstruktur', 'Zwei Schächte haben ein identisches Geoobjekt', 'Warnung', 5,
    'SELECT a.pk AS objid,
    printf(''Schacht "%s" ist identisch mit Schacht "%s"'', a.schnam, b.schnam) AS bemerkung
    FROM schaechte AS a
    JOIN schaechte AS b ON ST_Equals(a.geop, b.geop) = 1
    WHERE b.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name=''schaechte'' AND search_frame=a.geop) AND a.pk < b.pk',
'Schächte', 'pk'),

('Netzstruktur', 'Zwei Haltungen haben ein identisches Geoobjekt', 'Warnung', 5,
    'SELECT a.pk as objid, printf(''Haltung "%s" ist identisch mit "%s"'', a.haltnam, b.haltnam) As bemerkung
    FROM haltungen AS a JOIN haltungen AS b ON ST_Equals(a.geom, b.geom) = 1
    WHERE b.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name=''haltungen'' AND search_frame=a.geom) AND a.pk < b.pk
      AND (a.haltungstyp = ''Haltung'' OR a.haltungstyp IS NULL)',
'Haltungen', 'pk'),

('Netzstruktur', 'Zwei Haltungen mit identischen Schachtobjekten', 'Warnung', 5,
    'SELECT a.pk AS objid, printf(''Haltung "%s" hat die gleichen Schächte wie Haltung "%s"'', a.haltnam, b.haltnam) As bemerkung
    FROM haltungen AS a JOIN haltungen AS b ON (a.schoben = b.schoben AND a.schunten = b.schunten) OR (a.schoben = b.schunten AND a.schunten = b.schoben)
    WHERE a.pk < b.pk AND (a.haltungstyp = ''Haltung'' OR a.haltungstyp IS NULL)',
'Haltungen', 'pk'),

('Netzstruktur', 'Zwei Anschlussleitungen haben ein identisches Geoobjekt', 'Warnung', 5,
    'SELECT a.pk as objid, printf(''Anschlussleitung "%s" ist identisch mit "%s"'', a.leitnam, b.leitnam) As bemerkung
    FROM anschlussleitungen AS a JOIN anschlussleitungen AS b ON ST_Equals(a.geom, b.geom) = 1
    WHERE b.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name=''anschlussleitungen'' AND search_frame=a.geom) AND a.pk < b.pk',
'HA-Leitungen', 'pk'),

('Netzstruktur', 'Haltungslänge unplausibel', 'Warnung', 3,
    'SELECT pk as objid, printf(''Länge der Haltung "%s" (%.2f) ist unplausibel'', haltnam, st_length(geom)) AS bemerkung
    FROM haltungen WHERE st_length(geom)<2 OR st_length(geom)>80 AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)',
'Haltungen', 'pk'),

('Netzstruktur', 'Haltungslänge ungleich Geoobjekt', 'Fehler', 9,
    'SELECT pk as objid,
    printf(''Haltung "%s": vorgegebene Haltungslänge %.2f m weicht deutlich von der des Geometrieobjekts (%.2f m) ab'', haltnam, laenge, st_length(geom)) AS bemerkung
    FROM haltungen WHERE abs(st_length(geom)-laenge) / (st_length(geom) + laenge + 5.0) > 0.1',
'Haltungen', 'pk'),

('Netzstruktur', 'Haltungsgefälle unplausibel', 'Fehler', 9,
    'SELECT pk as objid, printf(''Unplausibles Gefälle %.2f ‰ in Haltung "%s"'', abs(sohleoben - sohleunten)/st_length(geom) * 1000.0, haltnam) AS bemerkung
    FROM haltungen
    WHERE (abs(sohleoben - sohleunten)/st_length(geom) < 0.001 OR abs(sohleoben - sohleunten )/st_length(geom) > 0.030)
      AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)',
'Haltungen', 'pk'),

('Netzstruktur', 'Entwässerungsart Haltung und angeschlossene Schächte unterschiedlich', 'Fehler', 9,
    'SELECT ha.pk as objid, printf(''Entwässerungsart in Haltung "%s" ("%s") und angeschlossenen Schächten "%s" ("%s"), "%s" ("%s") ist unterschiedlich'', ha.haltnam, ha.entwart, so.schnam, so.entwart, su.schnam, su.entwart) as bemerkung
    FROM haltungen AS ha LEFT JOIN schaechte AS so ON ha.schoben = so.schnam LEFT JOIN schaechte AS su ON ha.schoben = su.schnam
    WHERE (ha.entwart <> so.entwart OR ha.entwart <> su.entwart)
      AND (ha.haltungstyp = ''Haltung'' OR ha.haltungstyp IS NULL)', 'Haltungen', 'pk'),

('Netzstruktur', 'Haltungssohlhöhe oben tiefer als Schachtsohlhöhe', 'Fehler', 9,
    'SELECT ha.pk as objid, printf(''Sohlhöhe oben von Haltung "%s" (%.3f) ist tiefer als Schachtsohle "%s" (%.3f)'', ha.haltnam, ha.sohleoben, so.schnam, so.sohlhoehe) as bemerkung
    FROM schaechte AS so JOIN haltungen AS ha ON ha.schoben = so.schnam
    WHERE ha.sohleoben < so.sohlhoehe AND (ha.haltungstyp = ''Haltung'' OR ha.haltungstyp IS NULL)',
'Haltungen', 'pk'),

('Netzstruktur', 'Haltungssohlhöhe unten tiefer als Schachtsohlhöhe', 'Fehler', 9,
    'SELECT su.pk AS objid, printf(''Sohlhöhe unten von Haltung "%s" (%.3f) ist tiefer als Schachtsohle "%s" (%.3f)'', ha.haltnam, ha.sohleunten, su.schnam, su.sohlhoehe) AS bemerkung
    FROM schaechte AS su JOIN haltungen AS ha ON ha.schunten = su.schnam
    WHERE ha.sohleunten < su.sohlhoehe AND (ha.haltungstyp = ''Haltung'' OR ha.haltungstyp IS NULL)',
 'Haltungen', 'pk'),

('Netzstruktur', 'Abstand Deckel- und Sohlhöhe prüfen', 'Warnung', 3,
    'SELECT pk AS objid, printf(''Schacht "%s" Abstand Deckel- und Sohlhöhe prüfen'', schaechte.schnam) AS bemerkung
    FROM schaechte WHERE 0.8< deckelhoehe-sohlhoehe >= 8',
 'Schaechte', 'pk'),

('Netzstruktur', 'Schächte ohne zugehörge Haltung', 'Warnung', 3,
    'SELECT pk AS objid, printf(''Schacht "%s" ist an keiner Haltung angeschlossen'', schaechte.schnam) AS bemerkung
    FROM schaechte WHERE schaechte.schnam NOT IN (SELECT haltungen.schoben FROM haltungen UNION SELECT haltungen.schunten FROM haltungen)',
 'Haltungen', 'pk'),

('Geoobjekte', 'Haltungen ohne graphisches Linienobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Haltung "%s" hat kein graphisches Linienobjekt'', haltnam) AS bemerkung
    FROM haltungen WHERE geom IS NULL AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)',
 'Haltungen', 'pk'),

('Geoobjekte', 'Pumpe ohne graphisches Linienobjekt', 'Warnung', 9,
    'SELECT pk AS objid, printf(''Pumpe "%s" hat kein graphisches Linienobjekt'', haltnam) AS bemerkung
    FROM haltungen WHERE geom IS NULL AND (haltungstyp = ''Pumpe'')',
 'Pumpen', 'pk'),

('Geoobjekte', 'Wehre ohne graphisches Linienobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Wehr "%s" hat kein graphisches Linienobjekt'', haltnam) AS bemerkung
    FROM haltungen WHERE geom IS NULL AND (haltungstyp = ''Wehr'')',
 'Wehre', 'pk'),

('Geoobjekte', 'Schächte ohne graphisches Punktobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Schacht "%s" hat kein graphisches Punktobjekt'', schnam) AS bemerkung
    FROM schaechte WHERE geop IS NULL AND (schachttyp = ''Schacht'' OR schachttyp IS NULL)',
 'Schächte', 'pk'),

('Geoobjekte', 'Auslässe ohne graphisches Punktobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Auslass "%s" hat kein graphisches Punktobjekt'', schnam) AS bemerkung
    FROM schaechte WHERE geop IS NULL AND schachttyp = ''Auslass''',
 'Auslässe', 'pk'),

('Geoobjekte', 'Speicher ohne graphisches Punktobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Speicher "%s" hat kein graphisches Punktobjekt'', schnam) AS bemerkung
    FROM schaechte WHERE geop IS NULL AND schachttyp = ''Speicher''',
 'Speicher', 'pk'),

('Geoobjekte', 'Kein Flächenobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Fläche "%s" hat kein graphisches Flächenobjekt'', flnam) AS bemerkung
    FROM flaechen WHERE geom IS NULL',
 'Einzelflächen', 'pk'),

('Geoobjekte', 'Kein Flächenobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Haltungsfläche "%s" hat kein Flächenobjekt'', flnam) AS bemerkung
    FROM tezg WHERE geom IS NULL',
 'Haltungsflächen', 'pk'),

('Geoobjekte', 'Flächenanbindung ohne graphisches Linienobjekt', 'Fehler', 9,
    'SELECT pk AS objid, printf(''Anbindungen Flächen "%s" hat kein graphisches Linienobjekt'', flnam) AS bemerkung
    FROM linkfl WHERE geom IS NULL',
 'Anbindungen Flächen', 'pk'),

('HYSTEM-EXTRAN', 'Abflussparameter fehlen', 'Fehler', 9,
    'SELECT pk AS objid,
    printf(''Abflussparameter in Fläche "%s" fehlt'', flnam) AS bemerkung
    FROM flaechen
    WHERE abflussparameter IS NULL', 
 'Abflussparameter', 'pk'),

('HYSTEM-EXTRAN', 'Abflussparameter nicht in Referenzliste', 'Fehler', 9,
    'SELECT f1.pk AS objid,
    printf(''Abflussparameter "%s" wird in Fläche "%s" verwendet, fehlt aber in Referenztabelle "Abflussparameter"'', f1.abflussparameter, f1.flnam) AS bemerkung
    FROM flaechen AS f1
    LEFT JOIN abflussparameter ON f1.abflussparameter = abflussparameter.apnam
    WHERE abflussparameter.pk IS NULL AND f1.abflussparameter IS NOT NULL', 
 'Abflussparameter', 'pk'),

('HYSTEM-EXTRAN', 'Schwerpunktlaufzeiten fehlen', 'Fehler', 9, 
    'SELECT pk AS objid,
    printf(''"Fliesszeit Flaeche" fehlt in "Anbindungen Flächen" "%s"'', linkfl.flnam) AS bemerkung
    FROM linkfl WHERE fliesszeitflaeche IS NULL',
 'Anbindungen Flächen', 'pk'),

('HYSTEM-EXTRAN', 'Simulationsstatus fehlt', 'Fehler', 9,
    'SELECT pk AS objid,
    printf(''"Simulationsstatus" fehlt in Schacht "%s"'', schnam) AS bemerkung
    FROM schaechte WHERE simstatus IS NULL AND (schachttyp = ''Schacht'' OR schachttyp IS NULL)', 
 'Schächte', 'pk'),
 
 ('HYSTEM-EXTRAN', 'Simulationsstatus fehlt', 'Fehler', 9,
    'SELECT pk AS objid,
    printf(''"Simulationsstatus" fehlt in Haltung "%s"'', haltnam) AS bemerkung
    FROM haltungen WHERE simstatus IS NULL AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)', 
 'Haltungen', 'pk'),

('HYSTEM-EXTRAN', 'Simulationsstatus nicht in Referenzliste', 'Fehler', 9,
    'SELECT s.pk AS objid,
    printf(''Planungsstatus "%s" wird in Schacht "%s" verwendet, fehlt aber in Referenzliste "Planungsstatus")'', s.simstatus, s.schnam) AS bemerkung
    FROM schaechte AS s
    LEFT JOIN simulationsstatus AS u ON s.simstatus = u.bezeichnung
    WHERE u.bezeichnung IS NULL AND (s.schachttyp = ''Schacht'' OR s.schachttyp IS NULL)', 
 'Schächte', 'pk'),

('HYSTEM-EXTRAN', 'Neigungsklasse fehlt', 'Fehler', 9,
    'SELECT pk AS objid,
    printf(''"Neigungsklasse" fehlt in Fläche "%s"'', flnam) AS bemerkung
    FROM flaechen WHERE neigkl IS NULL',
 'Einzelflächen', 'pk'),

('HYSTEM-EXTRAN', 'Rohrprofil fehlt', 'Fehler', 9,
    'SELECT pk AS objid,
    printf(''"Profilname" fehlt in Haltung "%s"'', haltnam) AS bemerkung
    FROM haltungen
    WHERE profilnam IS NULL AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)',
 'Haltungen', 'pk'),

('HYSTEM-EXTRAN', 'Rohrprofil nicht in Referenzliste', 'Fehler', 9,
    'SELECT h.pk AS objid,
    printf(''Profil "%s" wird in Haltung "%s" verwendet, fehlt aber in Referenzliste "Profile"'', h.profilnam, h.haltnam) AS bemerkung 
    FROM haltungen AS h
    LEFT JOIN profile AS p
    ON h.profilnam = p.profilnam
    WHERE p.profilnam IS NULL AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL) AND h.profilnam IS NOT NULL',
 'Haltungen', 'pk'),

('HYSTEM-EXTRAN', 'Haltung ohne RW-Anschluss ist mit Flächen verknüpft', 'Fehler', 6,
    'SELECT h.pk AS objid, printf(''Haltung "%s" ohne RW-Anschluss ist mit Flächen verknüpft'', h.haltnam) AS bemerkung 
    FROM haltungen AS h
    JOIN linkfl AS l ON l.haltnam = h.haltnam
    WHERE NOT h.rwanschluss OR h.rwanschluss IS NULL
    GROUP BY h.pk',
 'Haltungen', 'pk'),

('HYSTEM-EXTRAN', 'Verschnittenes Flächenstück hat keine Verknüpfung zu einer Haltung', 'Fehler', 6,
    '    SELECT fl.pk AS objid, 
        printf(''Verschnittenes Flächenteilstück %s in Haltungsfläche %s hat keine Verknüpfung zur einer Haltung'', fl.flnam, tg.flnam) AS bemerkung
    FROM (SELECT pk, flnam, geom FROM flaechen WHERE aufteilen) AS fl
    LEFT JOIN tezg AS tg     ON St_Intersects(fl.geom, tg.geom) = 1
    LEFT JOIN linkfl AS lf   ON lf.flnam = fl.flnam
	WHERE lf.pk IS NULL',
 'Einzelflächen', 'pk'),

('Netzstruktur', 'Schachtnamen mehrfach', 'Fehler', 9,
    'SELECT pk AS objid,
    printf(''Schachtnamen "%s" mehrfach vergeben'', schnam) AS bemerkung
    FROM schaechte GROUP BY schnam HAVING count() > 1', 
 'Schächte', 'pk'),

('Netzstruktur', 'Haltungsnamen mehrfach', 'Fehler', 9,
    'SELECT pk AS objid,
    printf(''Haltungsnamen "%s" mehrfach vergeben'', haltnam) AS bemerkung
    FROM haltungen GROUP BY haltnam HAVING count() > 1', 
 'Haltungen', 'pk'),

('Zustandsklassen', 'Der Schadenskode hat mehr als 3 Zeichen', 'Fehler', 9,
    'SELECT pk AS objid, ''Der Schadenskode hat mehr als 3 Zeichen'' AS bemerkung
    FROM untersuchdat_haltung
    WHERE LENGTH(kuerzel) IS NOT 3',
 'Einzelschäden_Haltungen', 'pk'),
 
 ('Zustandsklassen', 'Untersuchungslänge prüfen', 'Fehler', 9,
    'SELECT 
    haltungen_untersucht.pk AS objid, ''Untersuchungslänge prüfen'' AS bemerkung
    FROM 
    haltungen_untersucht 
	LEFT JOIN 
    haltungen ON haltungen_untersucht.haltnam = haltungen.haltnam
	WHERE 
    ABS(haltungen_untersucht.laenge - haltungen.laenge) * 100.0 / ((haltungen_untersucht.laenge + haltungen.laenge) / 2.0) > 5
	GROUP BY haltungen_untersucht.haltnam',
 'Zustand_Haltungen_gesamt', 'pk'),

('Zustandsklassen', 'Haltungsname mehrfach', 'Fehler', 9,
    'SELECT pk AS objid, ''Haltungsname doppelt'' AS bemerkung
    FROM haltungen_untersucht group by haltnam having count(*)>1 ',
 'Zustand_Haltungen_gesamt', 'pk'),

('Zustandsklassen', 'Schachtname mehrfach', 'Fehler', 9,
    'SELECT pk AS objid, ''Schachtname doppelt'' AS bemerkung
    FROM schaechte_untersucht group by schnam having count(*)>1 ',
 'Zustand_Schächte_gesamt', 'pk'),

('Zustandsklassen', 'Der Schadenskode hat mehr als 3 Zeichen', 'Fehler', 9,
    'SELECT pk AS objid, ''Der Schadenskode hat mehr als 3 Zeichen'' AS bemerkung
    FROM untersuchdat_schacht
    WHERE LENGTH(kuerzel) IS NOT 3',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Fehlende Angabe der Streckenschadensnummer', 'Fehler', 9,
    'SELECT pk AS objid, ''Fehlende Angabe der Streckenschadensnummer'' AS bemerkung
    FROM untersuchdat_haltung
    WHERE streckenschaden IS NOT "not found" and streckenschaden_lfdnr IS 0',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Fehlende Angabe des Streckenschadens', 'Fehler', 9,
    'SELECT pk AS objid, ''Fehlende Angabe des Streckenschadens'' AS bemerkung
    FROM untersuchdat_haltung
    WHERE (streckenschaden IS "not found" or streckenschaden IS NULL) and streckenschaden_lfdnr IS NOT NULL',
 'Einzelschäden_Haltungen', 'pk'),
 
 ('Zustandsklassen', 'Fehlende Angabe vom Ende des Streckenschadens', 'Fehler', 9,
    'SELECT pk AS objid, ''Fehlende Angabe vom Ende des Streckenschadens'' AS bemerkung
    FROM untersuchdat_haltung
    GROUP BY untersuchhal
	HAVING SUM(CASE WHEN streckenschaden = ''A'' THEN 1 ELSE 0 END) > 0
   AND SUM(CASE WHEN streckenschaden = ''B'' THEN 1 ELSE 0 END) = 0',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen (DWA)', 'Fehler', 9,
    'SELECT pk AS objid, ''Das vergebene Schadenskürzel prüfen (DWA)'' AS bemerkung
    FROM untersuchdat_haltung
    WHERE  untersuchdat_haltung.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung DWA")
							AND  untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "DWA")',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen (ISYBAU)', 'Fehler', 9,
    'SELECT pk AS objid, ''Das vergebene Schadenskürzel prüfen (ISYBAU)'' AS bemerkung
    FROM untersuchdat_haltung
    WHERE  untersuchdat_haltung.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung ISYBAU")
							AND  untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "ISYBAU")',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen (DWA)', 'Fehler', 9,
    'SELECT pk AS objid, ''Das vergebene Schadenskürzel prüfen (DWA)'' AS bemerkung
    FROM untersuchdat_schacht
    WHERE  untersuchdat_schacht.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht DWA")
							AND  untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "DWA")',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen (ISYBAU)', 'Fehler', 9,
    'SELECT pk AS objid, ''Das vergebene Schadenskürzel prüfen (ISYBAU)'' AS bemerkung
    FROM untersuchdat_schacht
    WHERE untersuchdat_schacht.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht ISYBAU")
							AND  untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "ISYBAU")',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 1 prüfen (DWA)', 'Fehler', 9,
    'SELECT u.pk AS objid, ''Die Charakterisierung 1 prüfen (DWA)'' AS bemerkung
FROM untersuchdat_haltung u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Haltung DWA'')
  AND u.untersuchhal IN (SELECT haltnam FROM haltungen_untersucht WHERE datenart = ''DWA'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt1 = r.charakterisierung1)
            OR
            (u.charakt1 IS NULL AND r.charakterisierung1 IS NULL)
        )
  )',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 1 prüfen (ISYBAU)', 'Fehler', 9,
    'SELECT u.pk AS objid, ''Die Charakterisierung 1 prüfen (ISYBAU)'' AS bemerkung
FROM untersuchdat_haltung u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Haltung ISYBAU'')
  AND u.untersuchhal IN (SELECT haltnam FROM haltungen_untersucht WHERE datenart = ''ISYBAU'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt1 = r.charakterisierung1)
            OR
            (u.charakt1 IS NULL AND r.charakterisierung1 IS NULL)
        )
  )',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 1 prüfen (DWA)', 'Fehler', 9,
    'SELECT pk AS objid, ''Die Charakterisierung 1 prüfen (DWA)'' AS bemerkung
FROM untersuchdat_schacht u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Schacht DWA'')
  AND u.untersuchsch IN (SELECT schnam FROM schaechte_untersucht WHERE datenart = ''DWA'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt1 = r.charakterisierung1)
            OR
            (u.charakt1 IS NULL AND r.charakterisierung1 IS NULL)
        )
  )',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 1 prüfen (ISYBAU)', 'Fehler', 9,
    'SELECT pk AS objid, ''Die Charakterisierung 1 prüfen (ISYBAU)'' AS bemerkung
FROM untersuchdat_schacht u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Schacht ISYBAU'')
  AND u.untersuchsch IN (SELECT schnam FROM schaechte_untersucht WHERE datenart = ''ISYBAU'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt1 = r.charakterisierung1)
            OR
            (u.charakt1 IS NULL AND r.charakterisierung1 IS NULL)
        )
  )',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 2 prüfen (DWA)', 'Fehler', 9,
    'SELECT u.pk AS objid, ''Die Charakterisierung 2 prüfen (DWA)'' AS bemerkung
FROM untersuchdat_haltung u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Haltung DWA'')
  AND u.untersuchhal IN (SELECT haltnam FROM haltungen_untersucht WHERE datenart = ''DWA'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt2 = r.charakterisierung2)
            OR
            (u.charakt2 IS NULL AND r.charakterisierung2 IS NULL)
        )
  )',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 2 prüfen (ISYBAU)', 'Fehler', 9,
    'SELECT u.pk AS objid, ''Die Charakterisierung 2 prüfen (ISYBAU)'' AS bemerkung
FROM untersuchdat_haltung u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Haltung ISYBAU'')
  AND u.untersuchhal IN (SELECT haltnam FROM haltungen_untersucht WHERE datenart = ''ISYBAU'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt2 = r.charakterisierung2)
            OR
            (u.charakt2 IS NULL AND r.charakterisierung2 IS NULL)
        )
  )',
 'Einzelschäden_Haltungen', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 2 prüfen (DWA)', 'Fehler', 9,
    'SELECT pk AS objid, ''Die Charakterisierung 2 prüfen (DWA)'' AS bemerkung
FROM untersuchdat_schacht u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Schacht DWA'')
  AND u.untersuchsch IN (SELECT schnam FROM schaechte_untersucht WHERE datenart = ''DWA'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt2 = r.charakterisierung2)
            OR
            (u.charakt2 IS NULL AND r.charakterisierung2 IS NULL)
        )
  )',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Die Charakterisierung 2 prüfen(ISYBAU)', 'Fehler', 9,
    'SELECT pk AS objid, ''Die Charakterisierung 2 prüfen (ISYBAU)'' AS bemerkung
FROM untersuchdat_schacht u
WHERE u.kuerzel IN (SELECT hauptcode FROM reflist_zustand WHERE art = ''Schacht ISYBAU'')
  AND u.untersuchsch IN (SELECT schnam FROM schaechte_untersucht WHERE datenart = ''ISYBAU'')
  AND NOT EXISTS (
      SELECT 1
      FROM reflist_zustand r
      WHERE r.hauptcode = u.kuerzel
        AND (
            (u.charakt2 = r.charakterisierung2)
            OR
            (u.charakt2 IS NULL AND r.charakterisierung2 IS NULL)
        )
  )',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Die Angabe vom Bereich prüfen (DWA)', 'Fehler', 9,
    'SELECT pk AS objid, ''Die Angabe vom Bereich prüfen (DWA)'' AS bemerkung
    FROM untersuchdat_schacht
    WHERE untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht DWA")
							AND Untersuchdat_schacht.bereich
							not in (select reflist_zustand.bereich from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "DWA")',
 'Einzelschäden_Schächte', 'pk'),

('Zustandsklassen', 'Die Angabe vom Bereich prüfen (ISYBAU)', 'Fehler', 9,
    'SELECT pk AS objid, ''Die Angabe vom Bereich prüfen (ISYBAU)'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht ISYBAU")
							AND Untersuchdat_schacht.bereich
							not in (select reflist_zustand.bereich from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "ISYBAU")',
 'Einzelschäden_Schächte', 'pk')
    )
) AS pn
LEFT JOIN pruefsql AS ps
ON (pn.gruppe = ps.gruppe AND pn.warnbez = ps.warntext)
WHERE ps.warntext IS NULL;
