DYNA
====

Import aus DYNA-Datei
---------------------
Mit der Funktion |Tool_import_dyna| :guilabel:`Import aus DYNA-Datei` können leicht Daten aus einer DYNA-Datei in ein QKan-Projekt geladen werden.

.. image:: ./QKan_Bilder/Formulare/import_dyna.png
.. |Tool_import_dyna| image:: ./QKan_Bilder/Tool_import_dyna.png
                             :width: 1.25 em

Datenquelle
+++++++++++
In diesem Bereich wird die mit Kanal++ erstellte Quelldatenbank (Endung .ein) ausgewählt. Darunter muss das Projektionssystem ausgewählt werden, 
in dem die Daten **in der Datenquelle** gespeichert sind. In dem gleichen Projektionssystem wird das QKan-Projekt aufgebaut, sodass beide 
Projektionssysteme identisch sind.

Datenbank-Verbindung
++++++++++++++++++++
Hier wird das Datenziel - die Sqlite-Datenbank - ausgewählt. Ist noch keine Zieldatenbank vorhanden, kann diese hier erstellt werden.

Projektdatei erzeugen
+++++++++++++++++++++
Werden die Daten in ein bereits existierendes Projekt geladen, dann ist hier bereits der Pfad der verwendeten Projektdatei angegeben.
Existiert noch keine Projektdatei, kann diese hier erstellt werden. Dabei ist es empfehlenswert, diese im selben Verzeichnis mit der
QKan-Datenbank zu speichern. 
  
Export in DYNA-Datei
--------------------
Mit der Funktion |Tool_export_dyna| :guilabel:`Export in DYNA-Datei` ist ein schneller Export der QKan-Daten in eine DYNA-Datei möglich.

..
    (?Jörg?): Evtl. Ergänzen welche Daten genau und wofür? (Welches Programm arbeitet mit DYNA-Dateien)
    
.. image:: ./QKan_Bilder/Formulare/export_dyna.png
.. |Tool_export_dyna| image:: ./QKan_Bilder/Tool_export_dyna.png
                             :width: 1.25 em
..
    (?Jörg?): (Bitte Erklärungen ergänzen)
    QKan-Projekt-Datenbank
    ++++++++++++++++++++++
    Ziel: DYNA-Datei
    ++++++++++++++++
    
    Nur ausgewählte Teilgebiete berücksichtigen
    +++++++++++++++++++++++++++++++++++++++++++
    Soll nur ein Teilgebiet bearbeitet werden, dann kann dies hier, über die Aktivierung der Schaltfläche mit anschließender Auswahl des
    entsprechenden Teilgebiets, geschehen.
    
    Allgemeine Optionen
    +++++++++++++++++++
    -**Automatische Vergabe der Kanal- und Haltungsnummern:**
    -**Fehlende Profile in Tabelle "profile" ergänzen:**
    
    Zuordnung der Profile anhand...
    +++++++++++++++++++++++++++++++
    -**... Profilname (Langbezeichnung):** (?Jörg?): Am besten mit Beispiel, ebenso für nächsten Punkt
    -**... Profilschlüssel:**
    
    Berechnung des Befestigungsgrades aus ... (?Jörg?): Erklären, wann was gewählt werden soll und Unterschiede verdeutlichen; evtl. Vorraussetzungen erwähnen
    +++++++++++++++++++++++++++++++++++++++++
    -**... befestigten und unbefestigten Flächenobjekten:**
    -**... Haltungsflächen (tezg) und befestigten Flächen:**
    -**Mit Haltungsflächen verschneiden:**