Flächen mit Haltungen verknüpfen
================================

Nachdem die Flächen vorbereitet wurden, können diese nun mit den Haltungsflächen verknüpft werden, zu denen sie entwässern.
Eine Videoanleitung zur Verknüpfung der Flächen mit Haltungen ist `hier <LINK>` zu finden. 

Die Verknüpfung geschieht über das Tool |Tool_Verknuepfungslinie| "Erzeuge Verknüpfungslinien von Flächen zu Haltungen".
In der Regel werden bei den Filteroptionen, in dem nun geöffneten Fenster, nur die Haltungen spezifiziert.
Dafür wird in der Tabelle "Haltungen" der Eintrag "Mischwasser" ausgewählt (siehe Bild).
Bei den Optionen zur Erzeugung von Zuordnungen kann gegebenenfalls der Suchradius (siehe Bild) vergrößert werden.
Der Suchradius begrenzt den Bereich, indem die Zuordnung vorgenommen wird.
Daher ist die Anpassung vor allem sinnvoll, wenn einige Flächen weit entfernt von Haltungen liegen und dennoch angeschlossen werden sollen.
Auch die anderen Optionen sollten entsprechend dem hier dargestellten Beispiel ausgewählt werden.

.. image:: ./QKan_Bilder/Flaechen_verknuepfen/Fenster_verbindungslinien_erstellen.png
.. |Tool_Verknuepfungslinie| image:: ./QKan_Bilder/Flaechen_verknuepfen/Tool_verknuepfungslinien_fl_haltung.png
							 :width: 1.25 em

Das Fenster kann dann mit "OK" geschlossen werden. Die Verknüpfungslinien erscheinen nun im Plan.

.. image:: ./QKan_Bilder/Flaechen_verknuepfen/angeschlossene_flaechen.png

Nachdem die Verknüpfungslinien erstellt wurden, müssen noch die Parameter zur Oberflächenabflussberechnung angepasst werden.
Die entsprechenden Parameter sind in QKan in den Verknüpfungslinien gespeichert.
Erzeugt werden können diese über das Tool "Oberflächenabflussparameter eintragen" |Tool_oberflaechenabflussparameter|.
Dabei kann das sich öffnende Fenster ohne eine Änderung (siehe Bild unten) mit "OK" geschlossen werden.

.. image:: ./QKan_Bilder/Flaechen_verknuepfen/berechnung_oberflaechenabflussparameter.png

In der Attributtabelle ist nun die Spalte "Fließzeit Fläche" mit Werten gefüllt.
Alle nötigen Vorbereitungen für einen Export nach HYSTEM-EXTRAN sind nun durchgeführt.

.. |Tool_oberflaechenabflussparameter| image:: ./QKan_Bilder/Flaechen_verknuepfen/Tool_oberflaechenabflussparameter.png
							 :width: 1.25 em

Es können auch nachträglich Verbindungslinien bearbeitet oder hinzugefügt werden.

Verbindungslinien hinzufügen
----------------------------

War der Suchradius zu gering gewählt, kann es vorkommen, dass Flächen nicht mit Haltungen automatisch verknüpft werden.
Soll eine Fläche von Hand mit einer Haltung verknüpft werden,
muss dafür der entsprechende Layer "Anbindungen Flächen" ausgewählt und im Bearbeitungsmodus |Tool_bearbeitungsmodus| sein.
Anschließend kann über das Tool |Tool_linienobjekt_hinzufuegen| "Linienobjekt hinzufügen" durch Anklicken der entsprechenden Fläche,
danach der gewünschten Haltung und anschließend durch Bestätigung mit einem Rechtsklick, eine Verknüpfungslinie erstellt werden.
Im Gegensatz zu anderen Geo-Objekten, öffnet sich bei der Erstellung von Verknüpfungslinien kein Formularfenster.
Dies ist über die Layereigenschaften so vorgegeben, da es standartmäßig nicht benötigt wird.

.. |Tool_linienobjekt_hinzufuegen| image:: ./QKan_Bilder/Flaechen_verknuepfen/Tool_linienobjekt_hinzufuegen.png
							 :width: 1.25 em
							 
.. |Tool_bearbeitungsmodus| image:: ./QKan_Bilder/Tool_bearbeitungsmodus.png
							 :width: 1.25 em

Verbindungslinien bearbeiten
----------------------------

Vorhandene Verbindungslinien können auch im Nachhinein geändert werden.
Dazu muss im Bearbeitungsmodus |Tool_bearbeitungsmodus| das Stützpunkt-Werkzeug |Tool_stuetzpunkt_werkzeug| ausgewählt werden.
Nun kann die zu ändernde Verbindungslinie editiert werden, indem der Endpunkt angeklickt und auf die gewünschte Haltung gezogen wird.
Wichtig hierbei ist, dass der Menüpunkt "Topologisches Editieren" |Tool_topologisches_editieren| deaktiviert ist,
da sonst alle Haltungen, die an dieser Stelle verknüpft sind mitausgewählt werden.

.. |Tool_stuetzpunkt_werkzeug| image:: ./QKan_Bilder/Flaechen_verknuepfen/Tool_stuetzpunkt_werkzeug.png
							 :width: 1.25 em
.. |Tool_topologisches_editieren| image:: ./QKan_Bilder/Flaechen_verknuepfen/Tool_topologisches_editieren.png
							 :width: 1.25 em