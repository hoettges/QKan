Erstellen und Bearbeiten von Kanalnetzen
========================================

Bei der Erstellung sowie der Bearbeitung von Kanalnetzen können die QGIS-Standardfunktionen 
verwendet werden. Dabei ist zu beachten, dass die Änderungen erst dann in die QKan-Datenbank 
geschrieben werden, wenn die Änderungen jedes Layers gespeichert wurden. 


Zusatzfunktionen beim Editieren
-------------------------------

Sowohl QGIS als auch QKan bietet ein paar sehr nützliche Funktionalitäten an, die hier erläutert 
werden sollen. 


Digitalisieren von Kanälen
^^^^^^^^^^^^^^^^^^^^^^^^^^

Beim Digitalisieren mit QKan ist es wichtig zu berücksichtigen, dass beim Speichern des Haltungslayers Trigger 
ausgelöst werden, die einige sehr nützliche Funktionen ausführen. Deshalb ist es empfehlenswert, 
zunächst die Schächte zu erfassen, dabei die Namen zu vergeben und anschließend den Layer zu speichern. 

Wenn anschließend Haltungen digitalisiert werden und dieser Layer gespeichert wird, werden durch einen 
Trigger die Namen der Schächte, auf die die Haltungen gefangen wurden, jeweils als Schacht oben und Schacht 
unten übernommen. 

