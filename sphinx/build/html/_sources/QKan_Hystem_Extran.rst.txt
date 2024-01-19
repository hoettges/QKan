Hystem-Extran
=============

.. _linkimporthe:

Import aus HYSTEM-EXTRAN
------------------------

Mit der Funktion |Tool_Import_HE| :guilabel:`Import aus HYSTEM-EXTRAN` geschieht der Import leicht mit Hilfe einer HE Quelldatenbank (Endung .idbf).

.. image:: ./QKan_Bilder/Formulare/import_aus_he.png
.. |Tool_Import_HE| image:: ./QKan_Bilder/Tool_Import_HE.png
                             :width: 1.25 em

Datenquelle
+++++++++++
In diesem Bereich wird die mit HE erstellte Quelldatenbank (Endung .idbf) ausgewählt. Darunter muss das Projektionssystem ausgewählt werden, 
in dem die Daten **in der Datenquelle** gespeichert sind. In dem gleichen Projektionssystem wird das QKan-Projekt aufgebaut, sodass beide 
Projektionssysteme identisch sind.

Datenziel
+++++++++
Hier wird das Datenziel, die Sqlite-Datenbank und optional die zugehörige Projektdatei, ausgewählt. Ist noch keine Zieldatenbank oder 
Projektdatei vorhanden, können diese hier auch erstellt werden.

..
    Projektdatei erzeugen
    +++++++++++++++++++++
    (?Jörg?): Wann/Wie kann man hier Änderungen machen?
    
Tabellen importieren
++++++++++++++++++++
Hier können die klassischen Datentabellen, die das Kanalnetz ausmachen, selektiert werden. Im unteren Bereich schließt sich die Auswahl 
der Flächen an, dabei steht "Flächen (RW)" für Regenwasserflächen und "SW-Einleiter" für Schmutzwasser-Einleiter.
    
Haltungsflächen importieren, markiert als:
++++++++++++++++++++++++++++++++++++++++++
Die Selektion in diesem Block bezieht sich auf die Auswahl der entsprechenden Datensätze in HE (siehe Bild unten).
Hierbei können bei Bedarf bestimmte Flächentypen, durch löschen des Hakens im QKan-Formular, vom Import ausgeschlossen werden. 

|bild_einzugsfl_he| 

.. |bild_einzugsfl_he| image:: ./QKan_Bilder/Einzugsflaeche_HE.png
                                    :width: 30 em

Eingabeformular aus dem Programm `HYSTEM-EXTRAN, ITWH GmbH <https://itwh.de/de/softwareprodukte/desktop/hystem-extran/>`_
    
Referenztabellen importieren
++++++++++++++++++++++++++++
Hier kann festgelegt werden, welche Referenztabellen importiert werden sollen. Wird hier keine Auswahl getroffen, so füllt QKan 
selbstständig entsprechende Referenztabellen mit Standardwerten. Werden die zur Auswahl stehenden Referenztabellen gewählt, so importiert 
QKan nur genutzte, das heißt, mit anderen Tabellen verbundene, Werte. Einträge, die Angelegt wurden, aber in diesem Projekt nicht 
verwendet wurden, werden nur importiert, wenn die Option "Auch nicht verwendete Datensätze importieren" gewählt wird. Diese Option sollte 
nur gewählt werden, wenn eigene Referenztabellen (z.B. für Bodenklassen) in HYSTEM-EXTRAN angelegt wurden und davon auszugehen ist, dass 
diese in der Zukunft benötigt werden.

Tabelle zur Auswahl der zu importierenden Daten
+++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann der Import auf bestimmte Datentabellen des Kanalnetzes, bestimmte Flächen 
oder Referenztabellen beschränkt werden.

Ausführliche Erläuterung zu diesem Thema: :ref:`Import aus HYSTEM-EXTRAN <datenaustimporthe>`


.. index:: Export nach HYSTEM-EXTRAN (Menü)

Export nach HYSTEM-EXTRAN
-------------------------

Mit der Funktion |Tool_export_he| :guilabel:`Export nach HYSTEM-EXTRAN` funktioniert der Export für Version 7.8 und 7.9. 

.. image:: ./QKan_Bilder/Formulare/export_he.png
.. |Tool_export_he| image:: ./QKan_Bilder/Tool_export_he.png
                             :width: 1.25 em

..
    (?Jörg?): (Kontrollieren bzw. ergänzen)
    -**QKan-Projekt-Datenbank:**
    -**Zieldatenbank:** Die in diesem Formular geforderte HYSTEM-EXTRAN Vorlage-Datenbank benötigt eine Regenreihe mit einem dazugehörigen Regenschreiber 
    (muss gleichen Namen wie in den QKan-Flächendaten haben)
    -**Nur ausgewählte Teilgebiete berücksichtigen:** Soll nur ein Teilgebiet bearbeitet werden, dann kann dies hier, über die Aktivierung 
    der Schaltfläche mit anschließender Auswahl des entsprechenden Teilgebiets, geschehen.
    
    Optionen
    ++++++++
    
    Tabellen exportieren
    ++++++++++++++++++++
    Hier können die klassischen Datentabellen, die das Kanalnetz ausmachen, selektiert werden. Im unteren Bereich schließt sich die Auswahl 
    der Flächen an, dabei steht "Flächen (RW)" für Regenwasserflächen
    
    Aktionen beim Export
    ++++++++++++++++++++

Die Nutzung dieses Formulars in einem Anwendungsfall ist :ref:`hier <workflexporthe>` zu sehen.


Tabelle zur Auswahl der zu exportierenden Daten
+++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann der Export auf ausgewählte Teilgebiete beschränkt werden.


Ergebnisse aus HYSTEM-EXTRAN 8
------------------------------

Mit der Funktion |Tool_ergebnisse_he| :guilabel:`Ergebnisse aus HYSTEM-EXTRAN 8` können leicht die Simulationsergebnisse aus HYSTEM-EXTRAN 8 in ein bestehendes QKan-Projekt geladen werden.

.. image:: ./QKan_Bilder/Formulare/ergebnisse_he.png
.. |Tool_ergebnisse_he| image:: ./QKan_Bilder/Tool_ergebnisse_he.png
                             :width: 1.25 em
                             
..
    (?Jörg?): (Erstmal was allgemeines zur zu ladenden Datei, dann erklärung der Punkte)
    Datenbank-Verbindungen
    ++++++++++++++++++++++
    
    -**Überstauhäufigkeiten:**
    -**Überstauvolumina:**
    -**eigene Stildatei:**
    -**ohne:**