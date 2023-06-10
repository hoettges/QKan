Import von Kanaldaten aus einfachen Tabellen
============================================

Der Import von Daten aus einfachen Tabellen ist prinzipiell mit allen Methoden möglich, die QGIS zur Verfügung 
stellt. Leider funktioniert das Einfügen aus der Zwischenablage nur dann, wenn alle Attribute einer Tabelle 
einschließlich der Geometrieattribute vorhanden sind, die Namen exakt mit denen der Tabelle übereinstimmen 
und in der gleichen Reihenfolge stehen. Da dies nicht besonders praktikabel ist, wurde in QKan eine 
intelligente Clipboard-Einfügefunktion implementiert. 

Die Bedienung ist denkbar einfach: Um Daten mit Copy&Paste aus einer Tabelle (Excel, Textdatei, 
ACCESS-Datenbank, etc.) einzufügen, muss der entsprechende Layer in der Layerkontrolle aktiviert sein. Er darf 
sich dabei nicht im Bearbeitungsmodus befinden. Dabei gelten folgende Anforderungen: 

 - bestimmte Pflichtattribute müssen vorhanden sein
 - Die Reihenfolge der Daten ist beliebig
 - Für die meisten Attributnamen werden zahlreiche Synonyme akzeptiert (z. B. "schnam", "schachtname" oder 
   "Schachtbezeichnung"). Die Synonyme werden anhand vorgegebener "regulärer Ausdrücke" den Attributnamen der 
   QKan-Tabellen zugeordnet, die gegebenenfalls erweitert werden können. 

Zum Einfügen der Daten muss nur noch die Schaltfläche "Tabellendaten aus Clipboard einfügen" angeklickt werden (siehe nachfolgende Abbildung)

.. image:: ./QKan_Bilder/clipboard_einfuegen.png

Abbildung: Schaltfläche zum Einfügen von Tabellendaten aus dem Clipboard

Um vorab zu überprüfen, welche Spaltennamen erkannt werden, kann vorab die Schaltfläche "Tabellen aus Clipboard: Zuordnung anzeigen" (siehe nachfolgende Abbildung) angeklickt werden.

.. image:: ./QKan_Bilder/clipboard_testen.png

Abbildung: Überprüfen der automatischen Spaltennamenerkennung

Bei Tabellen mit Geometrien (Schächte, Haltungen, Fläche, etc.) werden in den Fällen, wo Punktkoordinaten 
oder Paare davon ausreichen (z. B. Schächte: Punktkoordinate, Haltungen und Wehre: 2 Punktkoordinaten für 
Anfangs- und Endpunkt) diese aus den eingefügten Koordinatenwerten erzeugt. 

Es ist aber auch möglich, Geometrien als WKT-Text einzufügen. Die Schreibweise entspricht der von QGIS, 
wenn Datensätze mit Geometrien kopiert und in eine Textdatei eingefügt werden. 

Beispiel zum Ausprobieren: 

| 1. Leere QKan-Datenbank anlegen (Schaltfläche "Neue QKan-Datenbank erstellen")

| 2. Schachtdaten (in Layer "Schächte" einfügen):
|
| Schacht;x;y;Sohle;Deckel                   
| D110076;388809.4738;5709888.006;80.49;83.61
| D110077;388806.8219;5709900.202;80.34;83.71
| D110075;388813.9783;5709854.593;81.16;84.09
| D110073;388749.989;5709812.893;82.77;85.47
| D110074;388709.6162;5709930.665;80.82;83.49
| D110801;388806.4423;5709907.041;80.22;83.28
| D110036;388798.8302;5709945.165;79.51;82.56
| D119801;388784.1633;5709985.519;78.84;81.86

| 3. Haltungsdaten (in Layer "Haltungen" einfügen):
|
| Haltung;Schacht_oben;Schacht_unten;Höhe;Breite;Länge;Sohleoben;Sohleunten;Profilname
| 410;D110076;D110077;0.3;0.3;12.55;80.5;80.32;Kreisquerschnitt
| 409;D110075;D110076;0.3;0.3;34.04;81.16;80.52;Kreisquerschnitt
| 408;D110073;D110074;0.2;0.2;124.28;82.8;80.85;Kreisquerschnitt
| 407;D110801;D110036;0.3;0.3;40.14;80.2;79.49;Kreisquerschnitt
| 443;D110036;D119801;0.3;0.3;42.4;79.49;78.88;Kreisquerschnitt
| 1364;D110077;D110801;0.3;0.3;5.5;80.3;80.2;Kreisquerschnitt


.. image:: ./QKan_Bilder/netz_aus_clipboard.png

Abbildung: Eingefügtes Kanalnetz in QKan
