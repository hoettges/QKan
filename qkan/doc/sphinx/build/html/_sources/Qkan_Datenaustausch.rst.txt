Import von Kanaldaten aus einfachen Tabellen (Excel, TXT, CSV)
==============================================================

Der Import von Daten aus einfachen Tabellen ist prinzipiell mit allen Methoden möglich, die QGIS zur Verfügung 
stellt. Leider funktioniert das Einfügen aus der Zwischenablage nur dann, wenn alle Attribute einer Tabelle 
einschließlich der Geometrieattribute vorhanden sind. Deshalb wird an dieser Stelle eine Vorgehensweise 
empfohlen, die sich mit Excel oder Open Office Writer leicht realisieren lässt und damit auch für einfache 
Textdateien oder CSV-Dateien verwendet werden kann, da sich diese leicht in diese Programme importieren 
lassen. 

.. _importasciidata:

Importieren von Tabellendaten aus Excel, CSV- oder Textdateien
--------------------------------------------------------------

Das Prinzip beruht darauf, aus den tabellarischen Daten eine SQL-Anweisung zu erstellen. Zur Ausführung 
ist es lediglich notwendig, im Kontextmenü eines Layers in der Layerkontrolle mit "SQL-Layer aktualisieren..." 
das Datenbankfenster "DB-Verwaltung" aufzurufen. 

.. image:: ./QKan_Bilder/qgis_dbDialog.png
    :name: Datenbankfenster zur Ausführung von SQL-Befehlen

Abbildung: Datenbankfenster zur Ausführung von SQL-Befehlen

In einer zusätzlichen Spalte des Tabellenkalkulations-Arbeitsblattes werden folgende Zeilen erzeugt, wobei 
zusätzlich am Anfang eine sowie am Schluss zwei Zeilen hinzu kommen:

#. Erste Zeile (zusätzlich): Insert-Anweisung zusammen mit einer Liste von Attributnamen
#. Je Datenzeile: Liste der Attributwerte
#. Vorletzte Zeile (zusätzlich): Ende der Insert-Anweisung
#. Letzte Zeile (zusätzlich): Befehl zur Aktualisierung des Räumlichen Index

Beispiel: 


  +-----+-------+-----------+-----------+---------+-----------+
  |     |A      |B          |C          |D        |E          |
  +=====+=======+===========+===========+=========+===========+
  |1    |schnam |xsch       |ysch       |sohlhoehe|deckelhoehe|
  +-----+-------+-----------+-----------+---------+-----------+
  |2    |D110036|388798.8302|5709945.165|79.51    |82.56      |
  +-----+-------+-----------+-----------+---------+-----------+
  |3    |D110073|388749.989 |5709812.893|82.77    |85.47      |
  +-----+-------+-----------+-----------+---------+-----------+
  |4    |D110074|388709.6162|5709930.665|80.82    |83.49      |
  +-----+-------+-----------+-----------+---------+-----------+
  |5    |D110075|388813.9783|5709854.593|81.16    |84.09      |
  +-----+-------+-----------+-----------+---------+-----------+
  |...  |...    |...        |...        |...      |...        |
  +-----+-------+-----------+-----------+---------+-----------+
  |62   |D110076|388809.4738|5709888.006|80.49    |83.61      |
  +-----+-------+-----------+-----------+---------+-----------+

Die SQL-Anweisungen, um diese Daten in die QKan-Tabelle einzufügen, lauten: 

:: 

    INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe) VALUES
    ('D110036', 388798.830197, 5709945.16474, 79.51, 82.56), 
    ('D110073', 388749.988968, 5709812.89315, 82.77, 85.47), 
    ('D110074', 388709.61619, 5709930.66496, 80.82, 83.49), 
    ...
    ('B110001', 388860.048099, 5709747.15311, 82.37, 84.58);
    
    SELECT RecoverSpatialIndex();


Diese Zeilen können im Tabellenkalkulationsprogramm mit folgenden Befehlen erzeugt werden: 

Erste Zeile:

:: 

  ="INSERT INTO schaechte (schnam, xsch, ysch, sohlhoehe, deckelhoehe) VALUES"

Falls die Spaltennamen in der Tabelle mit denen der entsprechenden QKan-Tabelle übereinstimmen, 
können die Spaltennamen auch einfach übernommen werden:

:: 

  ="INSERT INTO schaechte ("&C1&", "&D1&", "&E1&", "&F1&", "&G1&") VALUES"

Folgende Zeilen mit Attributdaten: 

:: 

  ="('"&C2&"', "&D2&", "&E2&", "&F2&", "&G2&"), "
  ="('"&C3&"', "&D3&", "&E3&", "&F3&", "&G3&"), "
  ="('"&C4&"', "&D4&", "&E4&", "&F4&", "&G4&"), "
  ...
  ="('"&C62&"', "&D62&", "&E62&", "&F62&", "&G62&");"


Man beachte, dass die letzte Zeile ohne Komma enden muss. Das Semikolon (;) am Schluss kann 
weggelassen werden, wenn die SQL-Befehle einzeln nacheinander ausgeführt werden. 

Abschließende SQL-Anweisung zur Aktualisierung des Räumlichen Index:

::

  ="SELECT RecoverSpatialIndex()"

  
