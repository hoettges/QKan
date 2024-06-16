QKan-Tabellen
=============


QKan basiert auf zwei Arten von Tabellen: 

- Datentabellen, z. B. Schächte, Haltungen, enthalten in der Regel grafische (Geo-)Objekte
- Referenztabellen, z. B. Entwässerungsarten, Profile


Tabelleninhalte
---------------

Im Folgenden werden QKan-Tabellen und ihre Inhalte dokumentiert. 


Haltungen
+++++++++

Die Tabelle enthält alle Verbindungselemente in einem Kanalnetz. In der nachfolgenden 
Tabelle sind die internen Attributnamen sowie für die verschiedenen Elementtypen in 
einem Kanalnetz mit den jeweils angepassten Attributinhalten dargestellt.

+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| Attributname | Haltungen            | Pumpen   | Wehre            | Drosseln   | Schieber           | Grund-/Seitenauslässe | Q-Regler        | H-Regler        |
+==============+======================+==========+==================+============+====================+=======================+=================+=================+
| haltnam      | Name                 |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| schoben      | Anfangsschacht       |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| schunten     | Endschacht           |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| hoehe        | Profilhöhe           | (n. v.)  | (n. v.)          | (n. v.)    | rel. Hubhöhe       | (n. v.)               |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
|              |                      |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| breite       | Profilbreite         | (n. v.)  | (n. v.)          | (n. v.)    | (n. v.)            | Öffnungsbreite        |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| laenge       | Haltungslänge        | (n. v.)  | (n. v.)          | (n. v.)    | (n. v.)            | (n. v.)               |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| sohleoben    | Sohlhöhe Anfang      | (n. v.)  | (n. v.)          | (n. v.)    | min. abs. Hubhöhe  | Höhe Unterkante       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| sohleunten   | Sohlhöhe Ende        | (n. v.)  | (n. v.)          | (n. v.)    | (n. v.)            | (n. v.)               |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
|              |                      |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| teilgebiet   | Teilgebiet           |          |                  | (n. v.)    |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| profilnam    | Profilbezeichnung    | (n. v.)  | (n. v.)          | (n. v.)    |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| entwart      | Entwässerungssystem  | (n. v.)  | (n. v.)          | (n. v.)    | (n. v.)            | (n. v.)               |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| material     | Material             | (n. v.)  | (n. v.)          | (n. v.)    | (n. v.)            | (n. v.)               | (n. v.)         | (n. v.)         |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| ks           | Rauheitsbeiwert      | (n. v.)  | Überfallbeiwert  | (n. v.)    | Verlustbeiwert     | Auslassbeiwert        | Verlustbeiwert  | Verlustbeiwert  |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
|              |                      |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| haltungstyp  | „Haltung“            | „Pumpe“  | „Wehr“           | „Drossel“  | „Schieber“         | „GrundSeitenauslass“  | „Q-Regler“      | „H-Regler“      |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
|              |                      |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| simstatus    | Planungsstatus       |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| kommentar    | Kommentar            |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| createdat    | bearbeitet           |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| xschob       | x_anf                |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| yschob       | y_anf                |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| xschun       | x_end                |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+
| yschun       | y_end                |          |                  |            |                    |                       |                 |                 |
+--------------+----------------------+----------+------------------+------------+--------------------+-----------------------+-----------------+-----------------+


Referenztabellen
----------------


Grundlagen
++++++++++

Eine QKan-Datenbank enthält neben den eigentlichen Geodatentabellen auch Referenztabellen, die in den Formularen als Nachschlagetabellen 
dienen. Anders als in vielen 
Datenbanken üblich erfolgt dabei der Zugriff nicht indirekt über die Schlüssel, sondern ausschließlich direkt über die Langbezeichnungen. 
Beispielsweise wird in der Haltungstabelle als Entwässerungsart "Mischwasser" und nicht das Kürzel "M" verwendet.  
Dies hat den Vorteil, dass Werte in den Tabellen direkt mit dem Ausdruckseditor im Tabellenfenster (Attributtabelle öffnen) bearbeitet werden können. 

Beim Datenimport werden zunächst in der zu importierenden Datei vorhandene Referenztabellen eingelesen und anschließend beim Einlesen 
alle Schlüsselwerte durch die zugeordneten Langbezeichnungen ersetzt. 

Falls in der zu importierenden Datei keine Referenztabelle enthalten ist, hält QKan drei Maßnahmen vor:

- es werden dem Dateiformat entsprechende Standardschlüssel angelegt (z. B. die im Merkblatt DWA-M 145 enthaltenen Werte der jeweiligen 
  Referenztabellen).
- bereits vor dem Datenimport können Schlüsselwerte und die zugehörigen Langbezeichnungen in den Referenztabellen hinzugefügt werden.
- unbekannte Schlüsselwerte werden beim Datenimport in die Referenztabelle übernommen, wobei der Schlüsselwert auch als Langbezeichnung 
  eingetragen wird. 
  Zusätzlich wird in der Kommentarspalte "unbekannt" ergänzt. Dem Anwender wird empfohlen, direkt nach dem Datenimmport an Stelle dieser 
  Langbezeichnungen entsprechende Bezeichnungen einzutragen, also z. B. "KM" durch "Mischwasser" zu ersetzen. 
  QKan enthält einen automatischen Trigger, der Änderungen der Langbezeichnungen automatisch (erst nach dem Speichern der Änderungen an 
  der Referenztabelle!) auch in den 
  zugeordneten Geodatentabellen ausführt, damit die logische Verknüpfung zwischen den Tabellen erhalten bleibt. 

Von besonderer Bedeutung ist die Referenztabelle "Entwässerungsarten". Sie bestimmt die Linienstile im Lageplan. Beim Import versucht 
QKan, die intern festgelegten Linienstile mit den Langbezeichnungen abzustimmen. Falls dies nicht funktioniert oder nachträglich Änderungen 
am Attribut "Entwässerungsart" in der Tabelle "Haltungen" vorgenommen werden, müssen gegebenenfalls die Bezeichnungen in den 
Layereigenschaften des Layers "Haltungen" entsprechend angepasst werden. 

Nachfolgend sind die in QKan implementierten Refernztabellen aufgeführt. Die Referenztabellen enthalten bis zu drei Blöcke:

- interne Schlüssel, z. B. für Schachttypen
- Schlüssel für den Datenaustausch mit Programmen zur hydrodynamsichen Simulation: HYSTEM-EXTRAN - "he", Mike+ - "mu", Kanal++ - "kp", SWMM - "sw"
- Schlüssel für den Datenaustausch mit allgemeinen Datenaustauschformaten (ISYBAU, DWA-M 150, DWA-M 145)

In der QKan-Datenbank haben die Tabellen aus softwaretechnischen Gründen leicht vereinfachte Tabellennamen. 



Abflussparameter
++++++++++++++++

Hydrologische Parameter für die hydrodynamsiche Simulation


Abflusstypen
++++++++++++

Art des hydrologischen Modells zur Beschreibung des Oberflächenabflusses


Auslasstypen
++++++++++++

Art des Auslasses


Bewertungsart
+++++++++++++

Art bzw. verwendete Richtlinie für die Zustandsbewertung


Bodenklassen
++++++++++++

Hydrogeologische Parameter für die hydrodynamsiche Simulation


Entwässerungsarten
++++++++++++++++++

Die Abwasserart wird für die farbige Darstellung der Haltungen verwendet. 


Flächentypen
++++++++++++

Klassifizierung der Flächen für das Simulationsprogramm HYSTEM/EXTRAN. Die Bezeichnungen werden für die farbige Darstellung verwendet


Haltungstypen
+++++++++++++

Art des Verbindungselements. Die interne Tabelle "haltungen" enthält nicht nur Haltungen, sondern auch alle anderen Elemente, die eine hydraulische Verbindung 
zwischen zwei Knotenelementen darstellen, also z. B. Wehre, Pumpen, Drosseln. Einige Elemente wie z. B. "Q-Regler" sind speziell für das Simulationsprogramm 
HYSTEM-EXTRAN eingefügt worden. 


Knotentypen
+++++++++++

Klassifizierung des Schachtes nach seiner Funktion im Entwässerungsnetz. Sie dient ausschließlich zur farbigen Auszeichnung im Lageplan. 


Profile
+++++++

Zusätzlich zu den Bezeichnungen enthält die Tabelle Schlüsselwerte für die Simulationsprogramme HYSTEM/EXTRAN (ITWH), Mike+ (DHI) sowie 
Kanal++ (Tandler)


Pumpentypen
+++++++++++

Die Tabelle wird ausschließlich für den Datenaustausch mit dem Simulationsprogramm HYSTEM/EXTRAN verwendet und enthält neben der 
Bezeichnung den zugehörigen Schlüsselwert.


Schachttypen
++++++++++++

Art des Knotenelements. Die interne Tabelle "schaechte" enthält nicht nur Schächte, sondern auch alle anderen Elemente, die Knotenelemente 
im Entwässerungsnetz darstellen, z. B. Speicher oder Auslässe. 


Simulationsstatus
+++++++++++++++++

Der Status ermöglicht die Klassifizierung als fiktives, geplantes, stillgelegtes etc. Element. Zusätzlich zu den Bezeichnungen enthält 
die Tabelle Schlüsselwerte für die Simulationsprogramme HYSTEM/EXTRAN (ITWH), Mike+ (DHI) sowie Kanal++ (Tandler)


Untersuchungsrichtung
+++++++++++++++++++++

Untersuchungsrichtung bei einer Kamerabefahrung


Wetter
++++++

Bezeichnung des Wetters während einer Kanaluntersuchung
