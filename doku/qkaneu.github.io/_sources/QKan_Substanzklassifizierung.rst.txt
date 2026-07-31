SubKanS
=======

Das Plugin SubKans beruht auf dem Projekt „ Entwicklung eines Standards zur Bewertung und Klassifizierung der baulichen Substanz von Abwasserkanälen und Schächten (SubKanS)“, 
welches 2021 in Zusammenarbeit der FH Aachen, der HS Magdeburg Stendal, dem Kompetenzzentrum Wasser Berlin gGmbh, dem Franz Fischer Ingenieurbüro GmbH, dem Ingenieurbüro Dr.-Ing. 
Klaus Hochstrate, der Dr.-Ing. Pecher und Partner Ingenieurgesellschaft mbH, der SiwaPlan Ingenieurgesellschaft mbH, der Stein Infrastructure Managment GmbH, der 3S Consult GmbH, 
der Gelsenwasser AG und der hanseWasser Bremen GmbH durchgeführt wurde.
Voraussetzung für die Nutzung des SubKans Tools ist die vorherige Nutzung der Zustandsklassifizierung, da die Substanzklassifizierung auf den Daten und Tabellen der 
Zustandsklassifizierung aufbaut. Aktuell ist die Substanzklassifizierung nur für die Haltungen möglich.

Der Aufruf des Plugins erfolgt nach dem Klick auf die Schaltfläche SubKans.

.. image:: ./QKan_Bilder/Formulare/zustandsklassen.png
.. |Zustandsklassifizierung1| image:: ./QKan_Bilder/subkans/subkans1.png
                             :width: 1.25 em
							 

Daraufhin öffnet sich die folgende Eingabemaske:

.. image:: ./QKan_Bilder/Formulare/zustandsklassen.png
.. |Zustandsklassifizierung2| image:: ./QKan_Bilder/subkans/subkans2.png
                             :width: 1.25 em
							 

In der Schaltfläche wird zuerst die Datenbank ausgewählt, mit welcher die Substanzklassifizierung durchgeführt werden soll. Danach erfolgt die Auswahl der Daten für die 
Substanzklassifizierung über das Datum der Daten dem Importdatum oder nach dem Befahrungsdatum. 
Als nächstes kann ausgewählt werden, ob die Einzelfallbetrachtungen nach SubKans ergänzt werden sollen. In dem Schritt werden alle Schäden mit einer Einzelfallbetrachtung mit 
Hilfe der Tabellen aus der SubKans Veröffentlichung ergänzt. Nur wenn in allen Feldern eine richtige Zustandsklasse steht werden die Schäden für die Substanzklasse berücksichtigt. 
Des Weiteren werden für die Schäden BCA und BCB Zustandsklassen ergänzt.  Im Nachgang an die Ergänzung der Einzelfallbetrachtungen müssen die Zustandsklassen der Haltungen neu 
berechnet werden.
Im nächsten Schritt erfolgt die Zuordnung von Schadensart- und Schadensausprägung. Dabei wird unterschieden in die Schadensarten Punktschaden (PktS), Umfangschaden (UmfS) und 
Streckenschäden (StrS). Bei den Schadensausprägungen wird zwischen durchdringenden Schäden (DdS), Oberflächenschäden (OfS) und Schäden ohne Bezug zur Baulichen Struktur (SoB) 
unterschieden. Es werden nur Streckenschäden berücksichtigt, die nach DWA 149 für die jeweiligen Kürzel erlaubt sind. Bei den Übrigen Schäden wird automatisch von Punkt oder 
Umfangsschäden ausgegangen.
Als nächstes wird die Schadensüberlagerung durchgeführt, bei dieser wird geprüft, ob Schäden an gleicher Stelle in der Haltung auftreten. Wenn zwei Schäden mit der gleichen 
Schadensart und Schadensausprägung vorhanden sind wird nur der schwere Schaden für die weitere Berechnung berücksichtigt. Bei den Streckenschäden wird eine Kürzung des schwächeren 
Schadens um die Länge der Überlagerung vorgenommen. Eine Schadensüberlagerung für Schäden ohne Bezug zur baulichen Struktur findet für Strecken-, Umfangs- und Punktschäden nicht 
statt. Die Schadenslänge für die Umfangschäden wird für Ei-Profile nach DWA 110 berechnet für alle anderen Profile wird die Breite* PI() gerechnet.
Zum Schluss erfolgt die Berechnung der Substanzklassen, diese werden anhand der vorher ermittelten Abnutzung berechnet. Die folgende Zuordnung wird vorgenommen:

.. image:: ./QKan_Bilder/Formulare/zustandsklassen.png
.. |Zustandsklassifizierung3| image:: ./QKan_Bilder/subkans/subkans3.png
                             :width: 1.25 em
							 

Bei der Berechnung der Abnutzung wird die kleinste Länge die in der Datenbank vorliegt genutzt. Dafür wird die Länge in den Stammdaten, Befahrungsdaten und die letzte Stationierung miteinander verglichen.
Die oben erläuterten Schritte können durch die Auswahlmöglichkeit in der Eingabemaske alle zusammen oder in einzelnen Schritten durchgeführt werden. Am Ende werden zwei neue Layer 
haltungen_substanz_bewertung und substanz_haltung_bewertung in QGIS angezeigt, diese enthalten alle Informationen aus der Substanzklassifizierung.
