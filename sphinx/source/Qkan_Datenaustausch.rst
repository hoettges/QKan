Datenaustausch
==============

Import von Kanaldaten aus einfachen Tabellen
--------------------------------------------

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

Zum Einfügen der Daten muss nur noch |Tool_clipboard_einfuegen| :guilabel:`Tabellendaten aus Clipboard einfügen` angeklickt werden.

.. |Tool_clipboard_einfuegen| image:: ./QKan_Bilder/Tool_clipboard_einfügen.png
                             :width: 1.25 em

Um vorab zu überprüfen, welche Spaltennamen erkannt werden, kann zuvor |Tool_clipboard_zuordnung| :guilabel:`Tabellen aus Clipboard: Zuordnung anzeigen`
angeklickt werden.

.. |Tool_clipboard_zuordnung| image:: ./QKan_Bilder/Tool_clipboard_zuordnung.png
                             :width: 1.25 em

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


Arbeiten mit Projektdateien
---------------------------

Projektdateien übertragen
^^^^^^^^^^^^^^^^^^^^^^^^^

Die Funktion |Tool_projektdatei_uebertragen| :guilabel:`Projektdatei übertragen` dient dazu, eine Vorlage-Projektdatei zu laden, 
um das Projekt nach eigenen Bedürfnissen z.B. Firmenstandards darzustellen. In der Projektdatei können z.B. Beschriftungsstile 
oder Linientypdarstellungen definiert sein. (1) In der Maske wird oben zunächst die aktuelle geladene Projektdatenbank angezeigt, 
welche sich nicht ändern lässt. Durch anklicken der Box darunter, kann die QKan-Datenbank mit dem Laden der neuen Datei 
aktualisiert werden - dies sollte in der Regel jedoch nicht nötig sein, da die Datenbank sich automatisch durch die 
Update-Funktion aktualisiert. 

(2) Ist noch keine Firmenstandard-Datei vorhanden, gibt es die Möglichkeit über das Auswahlfeld :guilabel:`Standarad-QKan-Vorlage verwenden` 
einen allgemeinen Stil zu laden. Diese Vorlage bietet eine gute Grundlage, um einen eigenen Standard zu entwickeln. 
Liegt bereits eine Firmenstandard-Datei vor, kann diese in dem Auswahlfeld darunter geöffnet werden. (3) Die Projektdatei wird auf 
das aktuelle QKan-Projekt angepasst und anschließend unter dem Namen gespeichert, welcher unter :guilabel:`Erzeugte Projektdatei speichern als...` 
ausgewählt wird. Dieser Name kann der Name der aktuell geladenen Projektdatei sein, wenn die Vorlage auf diese angewendet 
werden soll. Mit :guilabel:`OK` wird die Projektdatei geschrieben, jedoch aus programmtechnischen Gründen nicht sofort geladen.

.. _image_qkan_qgsAdapt:
.. image:: ./QKan_Bilder/qkan_qgsAdapt.png

Die neue Projektdatei kann geladen werden, indem das aktuelle Projekt über :guilabel:`Projekt` → :guilabel:`Zuletzt verwendet` 
neu geladen wird. Der Standard sollte nun in dem aktuellen Projekt geladen sein. 

.. |Tool_projektdatei_uebertragen| image:: ./QKan_Bilder/Tool_projektdatei_uebertragen.png
                                    :width: 1.25 em

..
    Export mit HYSTEM-EXTRAN
    ------------------------

.. _datenaustimporthe:  

Import aus HYSTEM-EXTRAN
------------------------
Eine Videoerläuterung des Formulars zum Import aus HYSTEM-EXTRAN ist |video_import_he| zu finden. 

.. |video_import_he| raw:: html

   <a href="https://fh-aachen.sciebo.de/s/cZPuvpgKkeBE56Q" target="_blank">hier</a>

Daten können leicht von einem HYSTEM-EXTRAN Projekt nach QKan übertragen werden mit dem Tool |Tool_Import_HE| :guilabel:`Import aus HYSTEM-EXTRAN`.

.. image:: ./QKan_Bilder/Formular_Import_HE.png
.. |Tool_Import_HE| image:: ./QKan_Bilder/Tool_Import_HE.png
                                    :width: 1.25 em

Unter Datenquelle wird die mit HE erstellte Quelldatenbank (Endung .idbf) ausgewählt. 
Darunter muss das Projektionssystem ausgewählt werden, in dem die Daten **in der Datenquelle** gespeichert sind.
In dem gleichen Projektionssystem wird das QKan-Projekt aufgebaut, sodass beide Projektionssysteme identisch sind.
Als nächstes wird das Datenziel, die Sqlite-Datenbank und optional die zugehörige Projektdatei, ausgewählt.
Ist noch keine Zieldatenbank oder Projektdatei vorhanden, können diese hier auch erstellt werden.

Im rechten Bereich der Maske befinden sich die Auswahlfelder zur Selektion der zu importierenden Daten.
In dem Bereich "Tabellen importieren", können die klassischen Datentabellen, die das Kanalnetz ausmachen, selektiert werden. 
Darunter schließt sich der Bereich zur Auswahl der Flächen an.
Dabei steht "Flächen (RW)" für Regenwasserflächen und "SW-Einleiter" für Schmutzwasser-Einleiter.
Die Selektion, die im Block "Haltungsflächen importieren, markiert als:" angeboten wird, bezieht sich auf die Auswahl der entsprechenden Datensätze in HE (siehe Bild unten).
Hierbei können bei Bedarf bestimmte Flächentypen, durch löschen des Hakens im QKan-Formular, vom Import ausgeschlossen werden. 

|bild_einzugsfl_he| 

.. |bild_einzugsfl_he| image:: ./QKan_Bilder/Einzugsflaeche_HE.png
                                    :width: 30 em

Eingabeformular aus dem Programm `HYSTEM-EXTRAN, ITWH GmbH <https://itwh.de/de/softwareprodukte/desktop/hystem-extran/>`_

Im rechten unteren Feld der Maske lässt sich festlegen, welche Referenztabellen importiert werden sollen. Wird hier keine Auswahl getroffen, 
so füllt QKan selbstständig entsprechende Referenztabellen mit Standardwerten. Werden die zur Auswahl stehenden Referenztabellen gewählt, 
so importiert QKan nur genutzte, das heißt, mit anderen Tabellen verbundene, Werte. Einträge, die Angelegt wurden, aber in diesem Projekt 
nicht verwendet wurden, werden nur importiert, wenn die Option "Auch nicht verwendete Datensätze importieren" gewählt wird. Diese Option 
sollte nur gewählt werden, wenn eigene Referenztabellen (z.B. für Bodenklassen) in HYSTEM-EXTRAN angelegt wurden und davon auszugehen ist, 
dass diese in der Zukunft benötigt werden. 

Nun kann das Formular mit :guilabel:`OK` geschlossen werden und der Import wird gestartet. 