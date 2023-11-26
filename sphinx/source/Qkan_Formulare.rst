Übersicht
=========

.. index:: Berechnung von Oberflächenabflussparametern (Menü)

    
Berechnung von Oberflächenabflussparametern
-------------------------------------------

Für befestigte und unbefestigte Flächen werden die Oberflächenabflussparameter
nach HYSTEM-EXTRAN (geplante Alternative: Kanal++) berechnet. 


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
.. _linkverbindunghaltungflaeche:

Verbindungslinien von Flächen zu Haltungen erstellen
----------------------------------------------------

Für jede Fläche, für die noch keine Anbindung erstellt wurde (automatisch oder manuell), wird 
eine Linie erzeugt, die innerhalb der Fläche beginnt und auf der damit verknüpften Haltung 
endet. 

Abhängig von dem Flächenattribut "aufteilen" ist eine Anbindung pro Fläche oder pro Flächenteilstück 
und Haltungsfläche (Tabelle "tezg") vorgesehen. 

.. image:: ./QKan_Bilder/Formulare/Verbindungslinien_fl_hal.png

..
    1. (?Jörg?)
    2. Die Voreinstellung, dass das Feld "Nur ausgewählte Bewässerungsarten berücksichtigen" aktiviert ist, sollte i.d.R. nicht geändert werden. (?Jörg?) Eine Ausnahme ist,....

3. Sind Teilgebiete erstellt worden und es soll in diesen gearbeitet werden, kann dies über die Auswahl in diesem Kasten geschehen.

.. 
    4. Hier kann ausgewählt werden, wie die Fläche zugeordnet werden soll - entweder über die nächste Kante einer Fläche zu einer Haltung oder über den Mittelpunkt der Fläche zur nächstliegenden Haltung. Auch hier sollte die Voreinstellung beibehalten werden. Die Option "Abstand zum Mittelpunkt" ist für... (Anwendungsfall)
    5. Der Suchradius gibt an, in welchem Umkreis von den Haltungen (?Jörg?) das Programm nach zu verknüpfenden Flächen sucht. Daher sollte er ausreichend groß gewählt werden, sodass alle Elemente bei der Zuordnung berücksichtigt werden. Ein zu großer Suchradius verlangsamt jedoch den Vorgang (?Jörg?) (? Oder warum sollte er nicht maximal gesetzt werden?). Mit dem Fangradius wird eingestellt, wie genau man eine Verbindungslinie zum uswählen mit der Maus treffen muss (?Richtig?), daher sollte er möglichst klein sein, da sonst die Auswahl einzelner Verbindungslinien erschwert wird.
    6. Diese Optionen sollten in der Regel nicht aktiviert werden. (?Jörg?)(?Wofür sind sie?)
    7. Auch diese Optionen sollten im Normalfall nicht geändert werden. Die Option "Mit Haltungsflächen verschneiden" sollte nur deaktiviert werden, wenn ...(?Jörg?)(Wann "mit Haltungsflächen verschneiden" deaktivieren?) Ist zu befürchten, da
    
Die Zuordnung sollte anschließend immer visuell überprüft werden.

Tabelle zur Auswahl der zu berücksichtigenden Flächen, Haltungen und Haltungsflächen
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung auf Flächen mit ausgewählten Abflussparametern, 
Haltungen mit ausgewählten Entwässerungsarten sowie allgemein auf ausgewählte Teilgebiete beschränkt 
werden. 



Ausführliche Erläuterung zu diesem Thema: :ref:`createlinkfl`


.. index:: Unbefestigte Fläche (Menü)
.. _linkerzeugungunbefflaechen:

Erzeugen von unbefestigten Flächen
----------------------------------

Die Funktion |Tool_unbef_flaechen| :guilabel:`Erzeuge unbefestigte Flächen` legt für jede Haltungsfläche (Tabelle tezg) aus dem Zwischenraum 
der befestigten Flächen ein Flächenobjekt angelegt. Dieses kann aus mehreren Flächenteilen bestehen. 

Die Attributdaten werden dabei aus den Haltungsflächen übernommen. 

.. image:: ./QKan_Bilder/Formulare/erz_unbef_fl.png

1. Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann die Bearbeitung auf ausgewählte Haltungsflächen beschränkt werden. Aufgelistet sind alle Abflussparameter und Teilgebiete, die in den Haltungsflächen verwendet werden. Durch die Auswahl einer Zeile in der Tabelle werden alle Haltungsflächen mit der dargestellten Kombination aus Abflussparameter und Teilgebiet für die Bearbeitung ausgewählt.

..
    2. (?Jörg?) Erklären, in welcher Situation die beiden Optionen gewählt werden sollten. 
    
Ausführliche Erläuterung zu diesem Thema: :ref:`Erzeugen von unbefestigten Flächen <createunbeffl>`

Die Nutzung dieses Formulars in einem Anwendungsfall ist :ref:`hier <workflunbeffl>` zu sehen. 

.. |Tool_unbef_flaechen| image:: ./QKan_Bilder/Tool_unbef_flaechen.png
                             :width: 1.25 em


.. _linkerzhaltungsfl:

Erzeugung von Haltungsflächen
-----------------------------
Mit dieser Funktion können (große) Haltungsflächen aufgeteilt werden, sodass jede Fläche eindeutig einer Haltung zugeordnet werden kann. 

.. image:: ./QKan_Bilder/Formulare/erz_haltungsfl.png

..
    1. In der Regel sollte diese Voreinstellung "Nur ausgewählte Entwässerungsarten berücksichtigen" aktiviert bleiben. (?Jörg?): Wann sollte man sie deaktivieren bzw. sonstige Änderungen hier vornehmen?
    
2. Soll nur ein Teilgebiet bearbeitet werden, dann kann dies hier, über die Aktivierung der Option "Nur ausgewählte Teilgebiete berücksichtigen" mit anschließender Auswahl des entsprechenden Teilgebiets, geschehen.
3. Sind keine aufzuteilenden Flächen im Vorfeld :ref:`markiert <linkflaechenaufteilung>` worden, erscheint diese Warnmeldung. Die Funktion kann so nicht ausgeführt werden.


.. index:: Export nach HYSTEM-EXTRAN (Menü)

Export nach HYSTEM-EXTRAN
-------------------------

Der Export funktioniert für Version 7.8 und 7.9. Die in diesem Formular geforderte HYSTEM-EXTRAN Vorlage-Datenbank benötigt eine Regenreihe 
mit einem dazugehörigen Regenschreiber (muss gleichen Namen wie in den QKan-Flächendaten haben). 

Die Nutzung dieses Formulars in einem Anwendungsfall ist :ref:`hier <workflexporthe>` zu sehen.


Tabelle zur Auswahl der zu exportierenden Daten
+++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann der Export auf ausgewählte Teilgebiete beschränkt werden.


.. index:: Projektlayer aktualisieren (Menü)


Import aus HYSTEM-EXTRAN
------------------------

Der Import aus HYSTEM-EXTRAN geschieht mit Hilfe einer HE Quelldatenbank (Endung .idbf).


Tabelle zur Auswahl der zu importierenden Daten
+++++++++++++++++++++++++++++++++++++++++++++++

Mit Hilfe der :ref:`Auswahltabelle<selectionTable>` kann der Import auf bestimmte Datentabellen des Kanalnetzes, bestimmte Flächen 
oder Referenztabellen beschränkt werden.

Ausführliche Erläuterung zu diesem Thema: :ref:`Import aus HYSTEM-EXTRAN <datenaustimporthe>`


Projektlayer aktualisieren
--------------------------

Mit diesem Formular können Projekte, die noch auf einer älteren QKan-Version basieren, auf den aktuellsten Stand gebracht werden. 
Neben Änderungen an der Datenbankstruktur sind dabei meistens auch Anpassungen an den Projektlayern notwendig. Dazu sollte in dem Formular 
unter der Überschrift „QKan-Datenbank“ die Option „auf aktuelle Version anpassen“ (4) gewählt werden. Es wird automatisch sichergestellt, 
dass die Wertbeziehungen (Überschrift „Layer anpassen“) aktualisiert werden. Weiterhin ist es empfehlenswert, unter der gleichen 
Überschrift auch die Option „Formularanbindungen auf QKan-Standard setzen“ aktiviert ist.

.. _image_qkan_layersadapt:
.. image:: ./QKan_Bilder/qkan_layersadapt.png

1. „QKan-Standard verwenden“ sollte aktiviert werden, wenn keine eigenen Standards vorliegen. Sollen Einstellungen aus bereits existierenden Projektdateien übernommen werden, so kann die entsprechende Datei unter „Einstellungen aus Projektdatei übernehmen“ mit der Schaltfläche […] rechts daneben ausgewählt werden.
2. In diesem Bereich kann eine Datenbank ausgewählt werden, an die das Projekt angebunden werden soll. Auch die übrigen Optionen sollten in der Regel aktiviert werden. 
3. Unter dieser Überschrift kann ausgewählt werden, welche Layer bearbeitet werden sollen. Allgemein ist „alle anpassen“ empfehlenswert.
4. Ist die vorliegende Datenbank nicht auf dem aktuellen Stand (oder es besteht Unsicherheit darüber), kann hier die Option „auf aktuelle Version anpassen“ aktiviert werden.
5. Mit der Schaltfläche […] wird der Namen und Standort des angepassten Projekts festgelegt.


Datenbank aktualisieren
-----------------------

Diese Funktion wird beim Aufruf vieler Plugins immer dann automatisch aufgerufen, wenn QKan feststellt, dass die geladene QKan-Datenbank nicht mehr auf dem aktuellen Stand ist. 
Dabei wird das aktuell geladene Projekt geschlossen. Falls Ihre Projektdatei nach dem Laden geändert 
wurde, können Sie mit den Optionsfeldern auswählen, ob die Projektdatei vor der Aktualisierung noch gespeichert werden soll.

.. index:: Datenbank aktualisieren


Projektdatei auf andere Datenbank übertragen
--------------------------------------------

Oft entstehen nach einiger Zeit komplexe Projektdateien, die besondere Layerdarstellungen enthalten und quasi „Firmenstandards“ darstellen. 
Solch eine Projektdatei kann mit dem Formular folgendermaßen auf ein anderes Projekt übertragen werden:

.. _image_qkan_qgsAdapt:
.. image:: ./QKan_Bilder/qkan_qgsAdapt.png

1. Wählen Sie die einzubindende QKan-Datenbank.
2. Wählen Sie die Projektdatei, die Sie mit dieser Datenbank verknüpfen möchten. Sie können stattdessen auch die QKan-Standardvorlage verwenden.
3. Wählen Sie den Pfad der neu zu erstellenden Projektdatei aus.

.. index:: Projektdatei übertragen

.. _linkelementeteilgebietzuordnen:

Zuordnung zu Teilgebiet
-----------------------

Mit der Funktion |Tool_elemente_tezg_zuordnen| :guilabel:`Zuordnung zu Teilgebiet` ist die automatische Zuordnung von Kanalnetz-Elementen zu einem
Teilgebiet möglich. Dabei wird das Teilgebiet automatisch in die jeweilige Spalte der Datentabellen eingetragen. 

.. image:: ./QKan_Bilder/Formulare/Zuordnung_zu_teilgebiet.png

1. Die Option "überlappend" sollte gewählt werden, wenn sichergestellt werden soll, dass auch Flächen, die nur zum Teil im Teilgebiet liegen (z.B von großen Gebäuden), bei der Bearbeitung des Gebietes berücksichtigt werden.
2. Hier kann des entsprechende zuvor erstellte (:ref:`Teilgebiet <linkteilgebiete>`) ausgewählt werden. 

.. 
    3. (?Jörg?) Sinn und Zweck der Pufferbreite erläutern.
    4. (?Jörg?) Erklären, in welcher Situation die beiden Optionen gewählt werden sollten. 

Die Nutzung dieses Formulars in einem Anwendungsfall ist :ref:`hier <linkteilgebiete>` zu sehen.

.. |Tool_elemente_tezg_zuordnen| image:: ./QKan_Bilder/Tool_elemente_tezg_zuordnen.png
                             :width: 1.25 em


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

