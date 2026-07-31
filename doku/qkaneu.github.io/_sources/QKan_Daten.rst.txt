Daten
=====

Plausibilitätsprüfung
---------------------

Mit der Funktion |Tool_plausibilitaet| :guilabel:`Plausibilitätsprüfung` können die verschiedenen 
Plausibilitätsprüfungen, welche unter der gleichnamigen Tabelle zu finden sind, bequem ausgeführt werden. 
Die zur Auswahl stehenden Themen entsprechen dabei den Gruppen aus der Tabelle "Plausibilitätsprüfungen". In 
dieser Tabelle sind die einzelnen Plausibilitätsprüfungen, mit Beschreibung sowie der genauen SQL-Abfrage, zu 
finden. 

.. image:: ./QKan_Bilder/Formulare/plausibilitaet.png
.. image:: ./QKan_Bilder/tabelle_plausi.png
.. |Tool_plausibilitaet| image:: ./QKan_Bilder/Tool_plausibilitaet.png
                             :width: 1.25 em
                             
Zur Durchführung können eine oder mehrere Themen ausgewählt und die entsprechenden SQL-Abfragen ausgeführt werden. 
Nach Durchführung der Plausibilitätsprüfung öffnet sich die Tabelle "Fehlerliste" automatisch. 

.. image:: ./QKan_Bilder/tabelle_fehler.png

Hier werden die gefundenen Fehler aufgeführt und durch Klick auf das Symbol in 
der ersten Spalte "Aktionen" kann das fehlerhafte Objekt in der Karte markiert und die Karte auf dieses Objekt 
gezoomt werden. 

Durch die Option "Ergebnisse zu bestehenden hinzufügen" wird die vorhandene Fehlerliste nicht überschrieben, 
sondern ergänzt. Die Option "Fehlerliste auf 5 Meldungen je Fehlertyp beschränken" bewirkt, dass für jeden 
Fehlertyp maximal 5 Fälle aufgelistet werden, um einen besseren Überblick über die verschiedenen Fehlertypen 
zu ermöglichen. Am Ende jeder Warnung ist die Gesamtzahl je Fehlertyp aufgeführt. 

Die Liste der Plausibilitätsprüfungen kann durch den Anwender ergänzt werden. Dazu muss in der Spalte "sql" 
eine SQL-Abfrage eingetragen werden, die zwei Spalten liefert:
- objid: Bezeichnung, anhand derer die aufzulistenden Objekte identifiziert werden können. 
- bemerkung: Beschreibung des Fehlers, gegebenenfalls mit zusätzlichen Informationen (z. B. fehlerhafte Länge)

Die in der Spalte "Gruppe" 
eingetragende Bezeichnung erscheint in der Themenauswahl des Formulars "Plausibilitätsprüfungen". 
Wichtig ist zu beachten, dass die von QKan vorgegebenen Datenprüfungen bei Updates automatisch geändert werden 
können. Um selbst ergänzte Plausibilitätsprüfungen davon auszunehmen reicht es aus, in der Spalte "Gruppe" 
eine andere als die vorgegebenen Bezeichnungen zu verwenden, z. B. "Netzstruktur, ergänzt", da nur die von QKan 
vorgegebenen Standardgruppen (z. B. "Geoobjekte", "HYSTEM-EXTRAN", "Netzstruktur") von den Aktualisierungen 
betroffen sind (siehe auch Abbildung oben: "Plausibilitätsprüfungen"). 
