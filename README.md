# QKan
Kanalkataster basierend auf QGIS
<!---
Hier die Auflistung der Module und der Funktionen?
Je nach Länge sollte diese eventuell unter den Punkt Installation
-->

## Installation
- Lorem Ipsum Dolor Sit Amet


<!---
Inhalt vorheriger metadata.txts:  
Database: Grundlegende Klassen und Funktionen, die für QKan nötig sind

CreateUnbefFL: Tool zur Erzeung von unbefestigten Flächenobjekten, die zur Tabelle "flaechen" hinzugefügt werden. Voraussetzung:
- Haltungsbezogene Teileinzugsgebietsflächen (Tabelle "tezg")
- Flächenobjekte (Tabelle flaechen), in der Regel befestigte Flächen, können aber auch schon unbefestigte Flächen sein.
Durch Differenzbildung mit Verschneidung werden für jede Teileinzugsgebietsfläche Differenzflächen erzeugt und als unbefestigte Flächen zur Tabelle "flaechen" hinzugefügt. Optional können zusammengesetzte Flächenobjekte, wie sie bei der Verscheidung entstehen können, in entsprechend viele Einzelflächen umgewandelt werden.

ExportHE
Exportiert Kanaldaten aus der QKan-Datenbank (SpatiaLite) in die HYSTEM-EXTRAN-Datenbank (Firebird)

ImportHE
Importiert Kanaldaten aus Hystem-Extran
 
 LinkFlaechen
Tool zur automatischen Verknüpfung von Flächenobjekten mit der geometrisch nächsten Haltung.

GanglinienHE
Tool zur Simulieren von Ganglinien. Wählen Sie zunächst den gewünschten Anfangs- und Endpunkt aus und starten Sie dann das Plugin.
-->