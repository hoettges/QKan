Erzeugung unbefestigter Flächen
===============================
  
Eine Videoanleitung zur Erzeugung von unbefestigten Flächen ist `hier <https://fh-aachen.sciebo.de/s/DPMnlKBMS9jjqTC>`_ zu finden. 

Bevor die unbefestigten Flächen erzeugt werden können ist es wichtig, zu prüfen, ob die Attributtabellen der Flächenobjekte 
(„Haltungsflächen“ und „Flächen“) vollständig ausgefüllt sind. Das bedeutet, die Spalten „Name“, „Teilgebiet“, „Regenschreiber“ und 
„Abflussparameter“ müssen vollständig ausgefüllt sein. Wenn keine Flächen vorhanden sind oder die Tabellen unvollständig sind, 
ist `hier <Import_gebaeudedaten>`_ eine Beschreibung des Vorgehens.  

Eine Verschmelzung der kleinen Flächen ist nicht mehr notwendig, da eine hohe Anzahl an Flächenschwerpunkten für die Programme heute kein Problem mehr darstellen.

Die unbefestigten Flächen können nun also direkt erstellt werden. Dies geschieht ganz leicht durch das QKan-Tool „Erzeuge unbefestigte Flächen“.  
Wenn dieses Werkzeug angeklickt wird, öffnet sich automatisch ein Fenster welches ohne eine Auswahl mit „OK“ bestätigt werden kann.

.. image:: ./QKan_Bilder/Erstellung_unbefestigte_flaechen/Fenster.png

Die unbefestigten Flächen werden nun automatisch erstellt und liegen auf dem Layer "$Default_Unbef" welches auch die Schraffur der Flächen anzeigt.

.. image:: ./QKan_Bilder/Erstellung_unbefestigte_flaechen/vor_unbef_fl.png
     :name: Flächen vor Anwendung des Tools

Abbildung: Flächen vor Anwendung des Tools

.. image:: ./QKan_Bilder/Erstellung_unbefestigte_flaechen/nach_unbef_fl.png
	 :name: Schraffur der unbefestigten Flächen

Abbildung: Schraffur der unbefestigten Flächen

Als nächstes müssen die befestigten Flächen für die Zuordnung zu den Haltungen vorbereitet werden. 
