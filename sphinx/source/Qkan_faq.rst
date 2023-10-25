FAQ
===

Fehlerhafte Anzeige Linienelemente
----------------------------------

**Problem:** Symbole auf Haltungen und Verbindungselementen (Pumpen, Wehre, etc.) wiederholen sich in viel zu engem Abstand

**Lösung:** Der Grund für dieses Problem ist eine Änderung in der Liniendarstellung von QGIS nach Version 3.22: Wenn Projekte mit einer 
höheren QGIS-Version erstellt und anschließend mit einer niedrigeren Version weiterverarbeitet werden, wird das Attribut zur Wiederholung 
von Symbolen auf Linien falsch gespeichert. So wird beispielsweise, wie auf dem Bild unten, der Fließpfeil statt nur mittig nun in einem 
Intervall angezeigt.

.. image:: ./QKan_Bilder/symbole_auf_linien.png

Zur Fehlerbehebung wird im Menü unter :guilabel:`QKan` unter dem Punkt :guilabel:`Allgemein` mit |Tool_projekt_aktualisieren| :guilabel:`QKan-Projekt aktualisieren` 
ein Fenster geöffnet, welches ohne eine weitere Auswahl mit :guilabel:`OK` geschlossen werden kann. Nun sollten die Symbole richtig 
angezeigt werden.

.. |Tool_projekt_aktualisieren| image:: ./QKan_Bilder/Tool_projekt_aktualisieren.png
                             :width: 1.25 em
                             

Objektabfrage funktioniert nicht
--------------------------------

**Problem:** Bei der Verwendung der Menüfunktion |Tool_info| :guilabel:`Objekt abfragen` wird nur ein Formular mit tabellarisch 
angeordneten Feldern anstelle eines QKan-Formulares angezeigt.

**Lösung:** Hierfür gibt es zwei mögliche Ursachen, welche auch beide zusammen vorliegen können:

1. Die Projektdatei wurde (in der Regel zusammen mit der eingebundenen QKan-Datenbank) in ein anderes Verzeichnis verschoben. Ist dies der Fall, kann im Menü unter :guilabel:`QKan` unter dem Punkt :guilabel:`Allgemein` mit |Tool_projekt_aktualisieren| :guilabel:`QKan-Projekt aktualisieren` der Pfad wieder hergestellt werden. Dazu muss in dem sich öffnenden Fesnter das Kontrollfeld im Bereich "Layer anpassen > Formularanbindung auf QKan-Standard setzten" sowie das Optionsfeld im Bereich "QKan-Layer > alle anpassen" aktiviert werden (siehe Bild unten).

.. image:: ./QKan_Bilder/formularpfade_wiederherstellen.png

.. |Tool_info| image:: ./QKan_Bilder/Tool_info.png
                             :width: 1.25 em

2. Der Modus für die Anzeige von Objektinformationen wurde noch nicht umgestellt. Es wird empfohlen folgende Einstellung vorzunehmen: Über dem Menüpunkt :guilabel:`Ansicht` > :guilabel:`Bedienfelder` > :guilabel:`Identifikationsergebnis` das Formular öffnen. Dort über den Menüpunkt :guilabel:`Abfrageeinstellung` das Kontrollfeld "Objektformular automatsich öffnen, wenn ein einzelnes Objekt abgefragt wird" aktivieren. Außerdem sollte unten in der Auswahlliste :guilabel:`Modus` der Eintrag "Layerauswahl" gewählt werden.

.. image:: ./QKan_Bilder/abfrageeinstellung_formularanzeige.png