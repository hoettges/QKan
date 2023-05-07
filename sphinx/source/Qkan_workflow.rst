Best practice Beispiel "Workflow"
=================================

Anhand des Projekts "Workflow" sollen exemplarisch die Arbeitsschritte von der Datenerfassung über die Datenaufbereitung bis 
hin zum Export in das Simulationsprogramm HYSTEM-EXTRAN 8 erläutert werden. Es handelt sich dabei um ein Teilnetz im Norden 
des Bochumer Stadtteils Hiltrop. 


Vorbereitung
------------

Die Daten, die in diesem Workflow benutzt werden, stehen in dieser `Excel-Datei <https://fh-aachen.sciebo.de/s/Bvbz2c9cbCYDkaG>`_ zum download bereit. 
Eine Videoanleitung zur Vorbereitung des Projektes ist `hier <https://fh-aachen.sciebo.de/s/gCEqM9ZDOgmyf6s>`_ zu finden.

Falls QKan noch nicht auf dem Rechner installiert ist, ist `hier <QKan_plugins_fuer_QGIS>`_ eine Anleitung zur Installation des QKan Plugins zu finden. 


Anlegen einer neuen QKan-Datenbank
----------------------------------

Zu Beginn eines jeden Projektes muss eine neue QKan-Datenbank erzeugt werden.
Mit |Tool_datenbank_erstellen| :guilabel:`Neue QKan-Datenbank erstellen` öffnet sich ein Fenster für die automatische Erzeugung einer neuen Datenbank. 
Als erstes muss der Pfad und der Name der Datenbank gewählt und das gewünschte Projektionssystem festgelegt werden. 
Dann wird das entsprechende Projekt gewählt. Das Fenster sollte nun vollständig ausgefüllt sein und kann mit :guilabel:`OK` geschlossen werden. 

.. image:: ./QKan_Bilder/Vorbereitung_Workflow/QKan_datenbank_erstellen_fenster.png 

.. |Tool_datenbank_erstellen| image:: ./QKan_Bilder/Tool_datenbank_erstellen.png
                             :width: 1.25 em


Hinterlegung einer Karte 
------------------------

Zur Orientierung und ansprechenderen Darstellung sollte ein passender Kartendienst hinterlegt werden. 
Über "Strg + L" wird die Datenquellenverwaltung geöffnet. Unter "WMS/WMTS" kann ein entsprechender Kartendienst ausgesucht werden. 
Für dieses Projekt wird der Kartendienst (über :guilabel:`neu`) "DTK Open Data NRW" genommen mit der URL "https://www.wmts.nrw.de/geobasis/wmts_nw_dtk". 
Nachdem die Eingaben mit :guilabel:`OK` bestätigt wurden, werden über :guilabel:`Verbinden` die entsprechenden Kachelsätze geladen. 
In dem dazugehörigen Layer kann die gewünschte Karte ausgewählt (hier: DTK Farbe EPSG_25832...) und mit :guilabel:`Hinzufügen` zum Projekt hinzugefügt werden. 

.. image:: ./QKan_Bilder/Vorbereitung_Workflow/gew_karte.png

Die Karte erscheint nun in den Layern des QKan-Projektes. Empfehlenswert ist es Karten in einem eigenen Layer zu hinterlegen. 
Um die Karte sich anzeigen zu lassen kann über einen Rechtsklick auf den entsprechenden Layer die Option :guilabel:`Auf Layer zoomen` ausgewählt werden. 
Nun sollte die Karte im Fenster erscheinen. 


Übernahme von Kanaldaten aus Excel
----------------------------------

Als nächstes werden die Kanaldaten aus der Excel-Tabelle übernommen. 
Dafür können die Daten ganz einfach mit copy & paste aus der Excel-Tabelle nach QKan übernommen werden. 
Beispielhaft wird dies hier an den Daten für die Schächte gezeigt. 

Zunächst muss die Excel-Tabelle geöffnet und die dazugehörige Karteikarte "schaechte" ausgewählt werden. 
Mit "Strg + A" werden alle Einträge der Tabelle ausgewählt und mit "Strg + C" können diese in die Zwischenablage kopiert werden. 
Wichtig hierbei ist, dass auch die Kopfzeile mit den Überschriften mit ausgewählt und kopiert wird. 
Vor dem Einfügen in QGIS muss überprüft werden, dass der richtige Layer (hier "Schächte") ausgewählt, aber **nicht** im Bearbeitungsmodus ist. 
Anschließend kann noch die Zuordnung über |Tool_clipboard_zuordnung| :guilabel:`Tabellendaten aus Clipboard: Zuordnung anzeigen` überprüft werden. 
Wenn die Zuordnung wie gewünscht angezeigt wird, können nun über |Tool_clipboard_einfügen| :guilabel:`Tabellendaten aus Clipboard einfügen` die Schächte eingefügt werden. 
Die Schächte sollten nun als graue Punkte auf der Karte erscheinen. 

Analog dazu können nun die Daten für die Auslässe, Haltungen und das Teilgebiet übernommen werden. 
Es sollte immer darauf geachtet werden, dass der richtige Layer ausgewählt ist. 
Wurden alle Daten aus der Excel-Tabelle übernommen, sollte die Karte wie unten dargestellt aussehen: 

.. image:: ./QKan_Bilder/Vorbereitung_Workflow/Ergebnis_vorbereitung.png 

.. |Tool_clipboard_zuordnung| image:: ./QKan_Bilder/Tool_clipboard_zuordnung.png
                             :width: 1.25 em

.. |Tool_clipboard_einfügen| image:: ./QKan_Bilder/Tool_clipboard_einfügen.png
                             :width: 1.25 em

Korrektur von Demodaten
-----------------------

Es kann bei Datenimporten häufiger vorkommen, dass eine Korrektur notwendig ist, da die verwendeten Bezeichnungen mit den in QKan vorhandenen Bezeichnungen in den Referenztabellen übereinstimmen muss. 
Fehler in der Bezeichnung werden in den Attributtabellen durch Klammern () um den in der Referenztabelle nicht vorhandenen Begriff gekennzeichnet. 
In diesem Workflow ist so beispielsweise die Profilbezeichnung der Haltungen fehlerhaft. 
Wird die Attributtabelle der Haltungen geöffnet, so kann man sehen, dass die Profilbezeichnung "Kreisquerschnitt, normal" in Klammern () aufgeführt wird. 
Um diesen Fehler zu beheben, kann einfach die Bezeichnung aus der Attributtabelle mit einem Rechtsklick kopiert werden. 
Anschließend kann in der entsprechenden Referenztabelle (Hier: Profile) die Bezeichnung hinzugefügt oder eine bestehende Bezeichnung geändert werden. 
Da in diesem Fall bereits der Eintrag "Kreis" vorhanden ist, kann sie durch die kopierte Bezeichnung ersetzt werden. 
Dafür muss die Tabelle im Bearbeitungsmodus sein. 
Die entsprechende Zelle kann durch Doppelklick ausgewählt und die Bezeichnung eingefügt werden. 
Nun sollte die Änderung gespeichert und der Bearbeitungsmodus ausgeschalten werden. 
In der Attributtabelle sollte nun die Profilbezeichnung ohne Klammern erscheinen. 

Als nächstes kann mit dem Import der Flächendaten begonnen werden. 