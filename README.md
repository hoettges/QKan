# QKan

Das Kanalkataster QKan dient dazu, Daten von städtischen 
Entwässerungssystemen für Berechnungen aufzubereiten und die Ergebnisse 
auszuwerten sowie in Plänen flexibel darstellen zu können. 

QKan besteht aus zahlreichen Plugins für das Open-Source-GIS QGIS und 
speichert die Daten in der Datenbank SpatiaLite, die eine GIS-Erweiterung 
der weltweit am meisten verwendeten Datenbank SQLite darstellt. 

Mit QKan können Kanaldaten mit den Berechnungsprogrammen "HYSTEM-EXTRAN" und 
"Kanal++" (noch in Bearbeitung) ausgetauscht werden. Damit besteht zum Einen 
die Möglichkeit, Kanaldaten aus anderen Quellen zu importieren und für die 
Berechnung aufzubereiten, aber auch die Kanaldaten aus dem 
Berechnungsprogramm zu exportieren, um im GIS weitere Datenaufbereitungen 
vorzunehmen, die nicht im Berechungsprogramm integriert sind, wie z. B. die 
Zuordnung von GIS-basierten Flächendaten. 

Als Anwender wird vor allem der planende Ingenieur gesehen, der vor allem 
Wert auf Flexibilität und Offenheit der Datenstrukturen legt, wobei 
grundlegende Kenntnisse im Umgang mit Datenbanken erforderlich sind. 
Hierdurch unterscheidet sich die QKan wesentlich von klassischen 
Kanalkatasterprogrammen, deren Aufgabe die langsfristige Bestandsverwaltung 
ist. 

Mit QKan wird ein Programmieransatz verfolgt, bei dem für die Datenverarbeitung 
insbesondere der geographischen Objekte (z. B. befestigte Flächen) 
ausschließlich die Geo-Funktionen der eingesetzten Datenbank genutzt werden. 
Dies hat den Vorteil, dass bei verknüpften Tabellen durch die sehr 
leistungsfähige Indizierung der Datenbanken erhebliche Effizienzgewinne 
erzielt werden können und zum anderen die Programmierung stark 

Das Projekt wird mit Förderung durch das Programm "Mittelstand.innovativ!" 
des Landes NRW von folgenden Ingenieurbüros finanziert:
- blue-ing, Düsseldorf: www.blue-ing.de
- Ingenieurbüro Reinhard Beck, Wuppertal: www.ibbeck.de

Details zu den Plugins sind in mehreren Vorträgen erläutert:

- Höttges, J. (2017): "QKan - Kanalkataster mit QGIS". FOSSGIS 2017, Passau: 
  https://doi.org/10.5446/30533
- Höttges, J. (2017): "QKan - Management of drainage system data with QGIS".
  FOSS4G 2017, Boston. presentation and paper accepted for publication.

## Installation
Eine ausführliche Installationsanleitung finden Sie unter:
https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/QKan/Doku/index.html


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
