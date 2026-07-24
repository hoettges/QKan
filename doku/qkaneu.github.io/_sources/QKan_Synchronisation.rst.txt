Synchronisation von QKan-Projekten
==================================

Es gibt in der Praxis mehrere Fälle, in denen ein Vergleich zwischen zwei QKan-Projekten sinnvoll ist: 

    - Ein Teilgebiet wurde zur Bearbeitung herausgegeben und die Änderungen sollen übernommen werden
    - Im Rahmen einer TV-Untersuchung wurde ein QKan-Projekt erstellt, dessen Daten in ein QKan-Bestandsprojekt 
      übernommen werden sollen.
    - Es existieren zwei Versionen eines QKan-Projektes, aus denen wieder eine Version erstellt werden soll

Das grundsätzliche Vorgehen bei der Synchronisation von QKan-Projekten ist wie folgt: 

#. Das aktuell geladene Projekt wird mit einem ausgewählten *externen Projekt* mit der 
   Funktion |Tool_Abgleich| :guilabel:`Vergleich mit einem anderen QKan-Projekt` verglichen. Datei wird für 
   jede QKan-Tabelle eine Synchronisationstabelle erstellt, in der der Anwender festgelegt kann, welche 
   der möglichen Maßnahmen (ändern, hinzufügen, löschen) auch tatsächlich ausgeführt werden sollen.

.. image:: ./QKan_Bilder/tabelle_sync.png

#. Die eigentliche Synchronisation erfolgt mit der Funktion |Tool_Sync| :guilabel:`Synchronisation mit einem anderen QKan-Projekt`

.. |Tool_Abgleich| image:: ./QKan_Bilder/Tool_Abgleich.png
                             :width: 1.25 em
.. |Tool_Sync| image:: ./QKan_Bilder/Tool_Sync.png
                             :width: 1.25 em
