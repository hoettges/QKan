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
Hier wird das Datenziel - die Sqlite-Datenbank - ausgewählt. Ist noch keine Zieldatenbank vorhanden, kann diese hier erstellt werden.

Projektdatei erzeugen
+++++++++++++++++++++
Werden die Daten in ein bereits existierendes Projekt geladen, dann ist hier bereits der Pfad der verwendeten Projektdatei angegeben. Existiert noch
keine Projektdatei, kann diese hier nun erstellt werden. Dabei ist es empfehlenswert, diese im selben Verzeichnis mit der Datenbank zu speichern.
    
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

Mit der Funktion |Tool_export_he| :guilabel:`Export nach HYSTEM-EXTRAN` können Kanaldaten aus QKan nach HYSTEM-EXTRAN exportiert werden.
Dazu muss jedoch zuerst in HYSTEM-EXTRAN eine Vorlagedatenbank angelegt werden, da QKan über keine Dateivorlagen für eine HYSTEM-EXTRAN 
Datenbank verfügt. In dieser Vorlagedatenbank sollten auch die Sonderbauwerke (z.B. Drosseln oder Pumpen) angelegt werden, da diese in
QKan nur mit Informationen, welche zur Herstellung des Netz-Zusammenhangs notwendig sind, gespeichert werden. Die Sonderbauwerke sollten
in HYSTEM-EXTRAN mit den jeweiligen (richtig benannten!) Anschluss-Schächten (Schacht oben & Schacht unten) angelegt werden. (Diese Schächte
werden mit dem Import der QKan Daten angelegt, müssen also zu diese Zeitpunkt noch nicht existieren. Die Fehlermeldung darf also ignoriert
werden.) Sind diese vorbereitenden Schritte ausgeführt, kann das Formular |Tool_export_he| geöffnet werden und wie unten beschrieben ausgefüllt
werden.


.. image:: ./QKan_Bilder/Formulare/export_he.png
.. |Tool_export_he| image:: ./QKan_Bilder/Tool_export_he.png
                             :width: 1.25 em

QKan-Projekt-Datenbank
++++++++++++++++++++++
Hier wird die gerade geöffnete QKan-Projektdatenbank angezeigt, welche hier nicht editiert werden kann. 
    
Zieldatenbank
+++++++++++++
- **Datenziel:** Hier wird der Name und Ablageort der mit diesem Formular erstellten Datenbank für den Import nach HYSTEM-EXTRAN gewählt.
- **Vorlage:** Hier muss die vorher mit HYSTEM-EXTRAN erstellte Vorlagedatenbank (siehe oben) ausgewählt werden.
    
Nur ausgewählte Teilgebiete berücksichtigen
+++++++++++++++++++++++++++++++++++++++++++
Soll nur ein Teilgebiet bearbeitet werden, dann kann dies hier, über die Aktivierung der Schaltfläche mit anschließender Auswahl des
entsprechenden Teilgebiets, geschehen.
    
Optionen
++++++++
- **Mit Haltungsflächen verschneiden:** Sind keine Haltungsflächen in zu exportierenden Datensatz vorhanden, **muss** diese Option
  deaktiviert sein. Wurden vorher :ref:`Haltungsflächen <linkhaltungsflaechen>` erstellt, kann diese Option gewählt werden, damit (große)
  Flächen aufgeteilt und die Teilstücke den entsprechenden Haltungen zugeordnet werden.
    
Tabellen exportieren
++++++++++++++++++++
Hier können die klassischen Datentabellen, die das Kanalnetz ausmachen, selektiert werden. In der Regel sollten hier die Optionen "Schächte",
" Haltungen" und "Auslässe" selektiert werden, da die Sonderbauwerke bereits vorher in HYSTEM-EXTRAN angelegt wurden. Im unteren Bereich 
schließt sich die Auswahl der Flächen an.

- **Flächen (RW):** Regenwasserflächen - Der Flächenexport steht im Zusammenhang mit der Verschneidung der Flächen und muss daher auch 
  aktiviert sein, wenn die Option "Mit Haltungsflächen verschneiden" gewählt wurde.
- **Haltungsflächen mit Befestigungsgraden:** Diese Option bezieht sich auf ältere Versionen von HYSTEM-EXTRAN, wobei die 
  Befestigungsgrade direkt in die Datensätze der Haltungsflächen geschrieben werden, um so von HYSTEM-EXTRAN weiterverarbeitet werden zu
  können.
- **SW-Einleiter:** Derzeit noch nicht implementiert.
- **Außengebiete:** Derzeit noch nicht implementiert.
- **Haltungsflächen:** HYSTEM-EXTRAN kann Haltungsflächen anzeigen, diese sind jedoch für eine Berechnung nicht unbedingt notwendig.
- **Einzugsgebiete:** Derzeit noch nicht implementiert.
- **Abflussparameter:** Sollte exportiert werden, wenn entsprechender Datensatz nicht schon in HYSTEM-EXTRAN vorliegt.
- **Bodenklassen:** Sollte exportiert werden, wenn entsprechender Datensatz nicht schon in HYSTEM-EXTRAN vorliegt.
- **Rohrprofile:** Derzeit noch nicht implementiert.
    
Aktionen beim Export
++++++++++++++++++++
In der Regel sollte die Option "hinzufügen" ausgewählt werden. Die Option "ändern" sollte gewählt werden, wenn bereit ein Export ausgeführt
wurde und in QKan Änderungen vorgenommen wurden und diese in die existierenden Daten eingespielt werden sollen. Dabei werden alle 
existierenden Datensätze in der Zieldatenbank überschrieben, jedoch keine neuen hinzugefügt.

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