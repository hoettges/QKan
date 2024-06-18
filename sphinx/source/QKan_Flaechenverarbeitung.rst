Flächenverarbeitung
===================

.. index:: Unbefestigte Fläche (Menü)
.. _linkerzeugungunbefflaechen:

Erzeugen von unbefestigten Flächen
----------------------------------

Die Funktion |Tool_unbef_flaechen| :guilabel:`Erzeuge unbefestigte Flächen` legt für jede Haltungsfläche (Tabelle tezg) aus dem Zwischenraum 
der befestigten Flächen ein Flächenobjekt angelegt. Dieses kann aus mehreren Flächenteilen bestehen. 

Die Attributdaten werden dabei aus den Haltungsflächen übernommen. 

.. image:: ./QKan_Bilder/Formulare/erz_unbef_fl.png
.. |Tool_unbef_flaechen| image:: ./QKan_Bilder/Tool_unbef_flaechen.png
                             :width: 1.25 em
                             
Auswahl der zu bearbeitenden Arten von Haltungsflächen (tezg)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung auf ausgewählte Haltungsflächen beschränkt werden. Aufgelistet
sind alle Abflussparameter und Teilgebiete, die in den Haltungsflächen verwendet werden. Durch die Auswahl einer Zeile in der Tabelle 
werden alle Haltungsflächen mit der dargestellten Kombination aus Abflussparameter und Teilgebiet für die Bearbeitung ausgewählt.

..
    Optionen
    ++++++++
    (?Jörg?) Erklären, in welcher Situation die beiden Optionen gewählt werden sollten.
    - **Autokorrektur von Namen und Abflussfaktoren in den TEZG-Flächen:**
    - **Flächenobjekte bereinigen:**
    
Ausführliche Erläuterung zu diesem Thema: :ref:`Erzeugen von unbefestigten Flächen <createunbeffl>`

Die Nutzung dieses Formulars in einem Anwendungsfall ist :ref:`hier <workflunbeffl>` zu sehen. 
  
  
 .. _linkerzhaltungsfl:

Erzeugung von Haltungsflächen
-----------------------------
Mit der Funktion |Tool_voronoiflaechen| :guilabel:`Erzeugung von Voronoiflächen zu Haltungen` können (große) Haltungsflächen aufgeteilt
werden, sodass jede Fläche eindeutig einer Haltung zugeordnet werden kann. 

.. image:: ./QKan_Bilder/Formulare/erz_haltungsfl.png
.. |Tool_voronoiflaechen| image:: ./QKan_Bilder/Tool_voronoiflaechen.png
                             :width: 1.25 em
..
    - **Nur ausgewählte Entwässerungsarten berücksichtigen:** In der Regel sollte diese Voreinstellung "Nur ausgewählte Entwässerungsarten berücksichtigen" aktiviert bleiben. (?Jörg?): Wann sollte man sie deaktivieren bzw. sonstige Änderungen hier vornehmen?
    
- **Nur ausgewählte Teilgebiete berücksichtigen:** Soll nur ein Teilgebiet bearbeitet werden, dann kann dies hier, über die Aktivierung der Option "Nur ausgewählte Teilgebiete 
  berücksichtigen" mit anschließender Auswahl des entsprechenden Teilgebiets, geschehen.
- **Warnung:** Sind keine aufzuteilenden Flächen im Vorfeld :ref:`markiert <linkflaechenaufteilung>` worden, erscheint diese Warnmeldung. Die Funktion 
  kann so nicht ausgeführt werden.


Entferne Überlappungen
----------------------

..
    (?Jörg?) Stimmt der Satz vom Inhalt?: Mit der Funktion |Tool_flaechenbereinigung| :guilabel:`Entferne Überlappungen` können automatisch 
    Flächen überprüft werden und Fehler behoben werden.

.. image:: ./QKan_Bilder/Formulare/flaechenbereinigung.png
.. |Tool_flaechenbereinigung| image:: ./QKan_Bilder/Tool_flaechenbereinigung.png
                             :width: 1.25 em
                             
..
    (?Jörg?) Bitte ergänzen
    -**Masterflächen:**
    -**anzupassende Flächen:**

.. _linkelementeteilgebietzuordnen:

Zuordnung zu Teilgebiet
-----------------------

Mit der Funktion |Tool_elemente_tezg_zuordnen| :guilabel:`Zuordnung zu Teilgebiet` ist die automatische Zuordnung aller Elemente eines 
Entwässerungsnetzes zu einem Teilgebiet möglich. Dabei wird das Teilgebiet automatisch in die jeweilige Spalte der Datentabellen eingetragen. 

.. image:: ./QKan_Bilder/Formulare/Zuordnung_zu_teilgebiet.png
.. |Tool_elemente_tezg_zuordnen| image:: ./QKan_Bilder/Tool_elemente_tezg_zuordnen.png
                             :width: 1.25 em
                             
- **Haltungen und Flächen:** In der Regel sollte die Standardeinstellung "innnerhalb" nicht geändert werden. Die Option "überlappend" 
  sollte gewählt werden, wenn sichergestellt werden soll, dass auch Flächen, die nur zum Teil im Teilgebiet liegen (z.B von großen 
  Gebäuden), bei der Bearbeitung des Gebietes berücksichtigt werden. In der darunter liegenden Auswahlbox kann das entsprechende - 
  zuvor erstellte - (:ref:`Teilgebiet <linkteilgebiete>`) ausgewählt werden 

.. 
    - **Pufferbreite:** (?Jörg?) Sinn und Zweck der Pufferbreite erläutern.
    - **Autokorrektur der TEZG-Namen:** (?Jörg?) Erklären, in welcher Situation die beiden Optionen gewählt werden sollten.
    - **Flächenobjekte bereinigen:**

Die Nutzung dieses Formulars in einem Anwendungsfall ist :ref:`hier <linkteilgebiete>` zu sehen.
                             

Teilgebietszuordnung als Gruppe verwalten
-----------------------------------------

..
    (?Jörg?) Was macht die Funktion genau? Satz vervollständigen...
    Mit der Funktion |Tool_tgz_verwalten| :guilabel:`Teilgebietszuordnungen als Gruppe verwalten`

.. image:: ./QKan_Bilder/Formulare/tgz_verwalten.png
.. |Tool_tgz_verwalten| image:: ./QKan_Bilder/Tool_tgz_verwalten.png
                             :width: 1.25 em
                             
..
    (?Jörg?) Bitte ergänzen
    -**Teilgebietszuordnungen verwalten:**
    -**Neue Gruppe:**
                          
.. index:: Anbindungen Einzeleinleiter (Menü)

Verknüpfungslinien von Einzeleinleitungen zu Haltungen erstellen
----------------------------------------------------------------

Die Funktion |Tool_verknuepfung_direkteinleiter| :guilabel:`Erzeuge Verknüpfungslinien von Einzeleinleitungen zu Haltungen` erzeugt für 
jeden Einzeleinleiter, für den noch keine Anbindung erstellt wurde (automatisch oder manuell), eine Linie, die am Punkte des 
Einzeleinleiters beginnt und auf der damit verknüpften Haltung endet. 

.. image:: ./QKan_Bilder/Formulare/Verbindungslinien_einzel_hal.png
.. |Tool_verknuepfung_direkteinleiter| image:: ./QKan_Bilder/Tool_verknuepfung_direkteinleiter.png
                             :width: 1.25 em
                             
- **Tabelle Haltungen:** Hier können die zu berücksichtigenden Haltungen anhand der Entwässerungsarten ausgewählt werden. Es 
  sollten Schmutzwasser und andere Abwasserarten, die kein Regenwasser enthalten, ausgeschlossen werden
- **Allgemein:** Sind Teilgebiete erstellt worden und es soll in diesen gearbeitet werden, kann dies über die Auswahl in diesem Kasten geschehen
- **Suchradius:** Maximaler Abstand zur Haltung, innnerhalb dessen die Einzeleinleiter berücksichtigt werden. Der Wert sollte ausreichend 
  groß gewählt werden. Ein zu großer Suchradius verlangsamt jedoch den Suchvorgang unnötig, weshalb Werte bis 100 m empfohlen werden
                             
Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung 
auf Haltungen mit ausgewählten 
Entwässerungsarten sowie allgemein auf ausgewählte Teilgebiete beschränkt werden. 

Ausführliche Erläuterung zu diesem Thema: :ref:`Anbindungen von Einzeleinleitern <createlinksw>`


.. index:: Flächenanbindungen (Menü)
.. _linkverbindunghaltungflaeche:

Verknüpfungslinien von Flächen zu Haltungen erstellen
-----------------------------------------------------

Mit der Funktion |Tool_verknuepfungslinien_erstellen| :guilabel:`Erzeuge Verknüpfungslinien von Flächen zu Haltungen` wird für jede 
Fläche, für die noch keine Anbindung erstellt wurde (automatisch oder manuell), eine Linie erzeugt, die innerhalb der Fläche beginnt und 
auf der damit verknüpften Haltung endet. 

Abhängig von dem Flächenattribut "aufteilen" ist eine Anbindung pro Fläche oder pro Flächenteilstück 
und Haltungsfläche (Tabelle "tezg") vorgesehen. 

.. image:: ./QKan_Bilder/Formulare/Verbindungslinien_fl_hal.png
.. |Tool_verknuepfungslinien_erstellen| image:: ./QKan_Bilder/Tool_verknuepfungslinien_erstellen.png
                             :width: 1.25 em

Filteroptionen
++++++++++++++

1. Mit dieser Auswahl kann die Bearbeitung auf Flächen mit den ausgewählten Abflussparametern beschränkt werden 
2. Hier können die zu berücksichtigenden Haltungen anhand der Entwässerungsarten ausgewählt werden. Hier 
   sollten Schmutzwasser und andere Abwasserarten, die kein Regenwasser enthalten, ausgeschlossen werden 
3. Sind Teilgebiete erstellt worden und es soll in diesen gearbeitet werden, kann dies über die Auswahl in diesem Kasten geschehen 

Optionen zur Erzeugung von Zuordnungen
++++++++++++++++++++++++++++++++++++++

- **Abstand zur nächsten Kante:** Die nächste Haltung wird anhand des geringsten Abstandes zur nächsten Kante einer Fläche bestimmt - im 
  Regelfall sollte diese Option gewählt werden
- **Abstand zum Mittelpunkt:** Die nächste Haltung wird anhand des geringsten Abstandes zum Mittelpunkt einer Fläche bestimmt
- **Suchradius:** Maximaler Abstand zur Haltung, innnerhalb dessen die Flächen berücksichtigt werden. Der Wert sollte ausreichend groß gewählt werden.
  Ein zu großer Suchradius verlangsamt jedoch den Suchvorgang unnötig, weshalb Werte bis 100 m empfohlen werden
- **Fangradius:** Der maximal zulässige Abstand zwischen dem Ende der Verbindungslinie und der zu verknüpfenden Haltung
- **Verbindungen nur innerhalb Haltungsfläche (tezg) erstellen:** Nur in besonderen Fällen zu empfehlen, in denen die Haltungen nur mit den Flächen 
  verknüpft werden sollen, die innerhalb der selben Haltungsfläche liegen
- **Autokorrektur von Namen in Flächen und Einleitpunkten:** Diese Option bewirkt, dass vor Erstellung der Zuordnungen zunächst nicht eindeutige Bezeichnungen von Flächen 
  und Einleitpunkten automatisch so durch eine fortlaufende Nummer ergänzt werden, dass nur noch eindeutige Bezeichnungen vorkommen. 
  Ist diese Option nicht aktiviert, bricht die Erstellung der Zuordnungen bei nicht eindeutigen Bezeichnungen mit einer Fehlermeldung ab
- **Mit Haltungsflächen verschneiden:** Diese Option muss aktiviert werden, wenn Flächen, für die die Option "Aufteilen" festgelegt wurde, beim Export in 
  ein Simulationsprogramm auf die Haltungsflächen verteilt ("verschnitten") werden sollen
- **Flächenobjekte bereinigen:** Bei Auswahl wird eine automatische Sanierung aller fehlerhaften Flächenobjekte vor der Erstellung der Zuordnungen durchgeführt, 
  dabei werden typische Fehler wie z. B. doppelte Stützstellen und Schleifen beseitigt


Die Zuordnung kann auch manuell vorgenommen und überarbeitet werden, falls bei der automatischen Erstellung unplausible Verbindungen entstanden sind oder 
sich infolge einer späteren Bearbeitung Änderungen bei den Flächen ergeben haben. 

Tabelle zur Auswahl der zu berücksichtigenden Flächen, Haltungen und Haltungsflächen
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung auf Flächen mit ausgewählten Abflussparametern, 
Haltungen mit ausgewählten Entwässerungsarten sowie allgemein auf ausgewählte Teilgebiete beschränkt 
werden. 

Ausführliche Erläuterung zu diesem Thema: :ref:`createlinkfl`


.. index:: Berechnung von Oberflächenabflussparametern (Menü)
    
Berechnung von Oberflächenabflussparametern
-------------------------------------------

Mit der Funktion |Tool_oberflaechenabflussparameter| :guilabel:`Oberflächenabflussparameter eintragen` werden die 
Oberflächenabflussparameter für befestigte und unbefestigte Flächen berechnet. Diese Funktion ist vorrangig für das Simulationsprogramm 
HYSTEM-EXTRAN gedacht. In HYSTEM-EXTRAN ist ein Assistent zur Berechnung der Oberflächenabflussparameter vorhanden, 
der diese Werte ebenfalls berechnen kann und dessen Anwendung empfohlen wird. 

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung 
auf Haltungen mit ausgewählten 
Entwässerungsarten sowie allgemein auf ausgewählte Teilgebiete beschränkt werden. 

.. image:: ./QKan_Bilder/Oberflaechenabflussparameter/oberflaechenabflussparameter.png
.. |Tool_oberflaechenabflussparameter| image:: ./QKan_Bilder/Tool_oberflaechenabflussparameter.png
                             :width: 1.25 em


Verknüpfungen bereinigen
------------------------

..
    (?Jörg?) Was macht die Funktion genau? Satz vervollständigen...
    Mit der Funktion |Tool_verknuepfungen_ber| :guilabel:`Verknüpfungen bereinigen`

.. image:: ./QKan_Bilder/Formulare/verknuepfungen_ber.png
.. |Tool_verknuepfungen_ber| image:: ./QKan_Bilder/Tool_verknuepfungen_ber.png
                             :width: 1.25 em
                             
..
    (?Jörg?) Bitte ergänzen
    -**Aktuelle QKan-Datenbank:**
    -**Flächenverknüpfungen bereinigen:**
    -**Einzeleinleiter-Verknüpfungen bereinigen:**
    -**Datensätze ohne Linienobjekt löschen:**
    -**Flächenobjekt bereinigen:**
    -**Fangradius auf Haltungen:**