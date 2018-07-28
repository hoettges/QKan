.. index:: Berechnung von Oberflächenabflussparametern (Menü)

Berechnung von Oberflächenabflussparametern
-----------------------------------------------------------

Für befestigte und unbefestigte Flächen werden die Oberflächenabflussparameter
nach HYSTEM/EXTRAN (geplante Alternative: Kanal++) berechnet. 

Tabellen zur Auswahl der zu berücksichtigenden Flächen
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung 
auf Haltungen mit ausgewählten 
Entwässerungsarten sowie allgemein auf ausgewählte Teilgebiete beschränkt werden. 


.. index:: Anbindungen Einzeleinleiter (Menü)

Automatisches Erzeugen von Anbindungen von Einzeleinleitern
-----------------------------------------------------------

Für jeden Einzeleinleiter, für den noch keine Anbindung erstellt wurde (automatisch oder manuell), wird 
eine Linie erzeugt, die am Punkte des Einzeleinleiters beginnt und auf der damit verknüpften Haltung
endet. 

Tabelle zur Auswahl der zu berücksichtigenden Flächen, Haltungen und Haltungsflächen
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung 
auf Haltungen mit ausgewählten 
Entwässerungsarten sowie allgemein auf ausgewählte Teilgebiete beschränkt werden. 

Ausführliche Erläuterung zu diesem Thema: :ref:`Anbindungen von Einzeleinleitern <createlinksw>`


.. index:: Flächenanbindungen (Menü)

Automatisches Erzeugen von Flächenanbindungen
---------------------------------------------

Für jede Fläche, für die noch keine Anbindung erstellt wurde (automatisch oder manuell), wird 
eine Linie erzeugt, die innerhalb der Fläche beginnt und auf der damit verknüpften Haltung
endet. 

Abhängig von dem Flächenattribut "aufteilen" ist eine Anbindung pro Fläche oder pro Flächenteilstück 
und Haltungsfläche (Tabelle "tezg") vorgesehen. 

Tabelle zur Auswahl der zu berücksichtigenden Flächen, Haltungen und Haltungsflächen
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung auf Flächen mit ausgewählten Abflussparametern, 
Haltungen mit ausgewählten Entwässerungsarten sowie allgemein auf ausgewählte Teilgebiete beschränkt 
werden. 



Ausführliche Erläuterung zu diesem Thema: :ref:`createlinkfl`


.. index:: Unbefestigte Fläche (Menü)

Erzeugen der unbefestigten Flächen
----------------------------------

Für jede Haltungsfläche (Tabelle tezg) wird aus dem Zwischenraum der befestigten Flächen ein Flächenobjekt angelegt. 
Dieses kann aus mehreren Flächenteilen bestehen.

Die Attributdaten werden dabei aus den Haltungsflächen übernommen.

Tabelle zur Auswahl der zu bearbeitenden Arten von Haltungsflächen
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung auf ausgewählte Haltungsflächen beschränkt werden. Aufgelistet sind alle Abflussparameter und Teilgebiete, die in den Haltungsflächen verwendet werden. Durch die Auswahl einer Zeile in der Tabelle werden alle Haltungsflächen mit der dargestellten Kombination aus Abflussparameter und Teilgebiet für die Bearbeitung ausgewählt.

Ausführliche Erläuterung zu diesem Thema: :ref:`Erzeugen von unbefestigten Flächen <createunbeffl>`



.. index:: Export nach HYSTEM/EXTRAN (Menü)

Export nach HYSTEM/EXTRAN
-------------------------

Der Export funktioniert für Version 7.8 und 7.9.

Tabelle zur Auswahl der zu exportierenden Daten
+++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann der Export auf ausgewählte Teilgebiete beschränkt werden.



Allgemeine Funktionselemente in Formularen
------------------------------------------

.. _selectionTable:

Auswahl in Listen
+++++++++++++++++

Für die Auswahl von Zeilen in der Tabelle stehen folgende Funktionen zur Verfügung:

    - Auswahl einer Zeile: Mausklick links
    - Auswahl einer weiteren Zeile: [Strg] + Mausklick links
    - Auswahl einer Zeile rückgängig machen: [Strg] + Mausklick links
    - Erweiterung der Auswahl von der zuvor ausgewählten Zeile bis zur gewünschten Zeile: [Shift] + Mausklick links

Ob eine Auswahl aktiv ist, kann mit Hilfe des Auswahlkästchen über der Tabelle gesteuert werden. Sobald eine Zeile 
in der Auswahltabelle angeklickt wird, wird die Auswahl automatisch aktiviert

