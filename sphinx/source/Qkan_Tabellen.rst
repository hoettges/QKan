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

QKan nutzt Referenztabellen anders als viele etablierte Kanalkatasterprogramme ausschließlich als Nachschlagetabellen. Statt der häufig 
verwendeten Schlüssel (z. B. "MW" für "Mischwasser") enthalten alle Datentabellen die Langbezeichnungen. Dies hat den Vorteil, dass in 
den Werte in den Tabellen direkt mit dem Ausdruckseditor im Tabellenfenster (Attributtabelle öffnen) bearbeitet werden können. 
Die in den Referenztabellen enthaltenen 
Schlüssel werden ausschließlich für den Datenaustausch benötigt. Beim Datenimport besteht deshalb je nach Datenquelle die Notwendigkeit, 
die Schlüsselwerte in die Langbezeichnungen umzuwandeln. Dazu durchsucht QKan zunächst die Datenquelle auf Referenztabellen. Falls diese 
nicht vorliegen, erzeugt QKan intern entsprechend der Datenquelle eine Tabelle mit Standardwerten, die dann beim Import zur Anwendung kommt. 

Falls Schlüsselwerte in den zu importierenden Daten vorkommen, für die keine Datensätze in der entsprechenden Referenztabelle angelegt werden 
konnten, werden diese hinzugefügt und der Schlüsselwert auch als Langbezeichnung eingetragen. Zur Information wird im Feld "Kommentar" der 
Hinweis eingetragen, dass die Langbezeichnung noch angepasst werden sollte. 

Von besonderer Bedeutung ist die Referenztabelle "Entwässerungsarten". Sie bestimmt die Linienstile im Lageplan. Beim Import versucht 
QKan, die intern festgelegten Linienstile mit den Langbezeichnungen abzustimmen. Falls dies nicht funktioniert oder nachträglich Änderungen 
am Attribut "Entwässerungsart" in der Tabelle "Haltungen" vorgenommen werden, müssen gegebenenfalls die Bezeichnungen in den 
Layereigenschaften des Layers "Haltungen" entsprechend angepasst werden. 

Nachfolgend sind die in QKan implementierten Refernztabellen aufgeführt. In der QKan-Datenbank haben die Tabellen aus softwaretechnischen 
Gründen leicht vereinfachte Tabellennamen.



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
