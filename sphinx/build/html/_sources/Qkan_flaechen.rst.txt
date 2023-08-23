Arbeiten mit Flächen
====================


Verarbeitung von befestigten und unbefestigten Flächen
------------------------------------------------------

Abflusswirksame Flächen, z. B. Dachflächen, Parkplätze, Straßen, werden in QKan in der Tabelle "flaechen" verwaltet. 
Diese werden mit Hilfe des Attributs "abflussparameter" klassifiziert, und in der entsprechenden Tabelle 
"abflussparameter" sind die für die hydraulische 
Berechnung benötigten Parameter gespeichert. In dieser Tabelle ist wiederum ein Attribut "bodenklasse" enthalten, 
das für durchlässige Flächen die Versickerungsparameter enthält. Unbefestigte Flächen sind in QKan dadurch 
gekennzeichnet, dass entweder keine Bodenklasse oder aber eine Bodenklasse zugeordnet ist, deren Durchlässigkeit 0 ist.

.. _createlinkfl:


Grundprinzip
------------

Die Zuordnung der abflusswirksamen Flächen zu den Haltungen des Kanalnetzes stellt bei der Vorbereitung 
einer hydrodynamischen Simulation einen aufwändigen Arbeitsschritt dar. Deshalb enthält QKan Funktionen 
zur automatischen Verknüpfung und zur Plausibilitäskontrolle. 

.. image:: ./QKan_Bilder/qkan_linkfl.png
    :name: Anbindungen von Flächen an Haltungen

Abbildung: Anbindungen von Flächen an Haltungen

Die abflusswirksamen Flächen werden mittels Linien mit den Haltungen verbunden, die von einem Punkt innerhalb 
der jeweiligen Fläche zur Haltung führen und im Layer "Anbindungen Flächen" (QKan-Tabelle "linkfl") gespeichert werden. 

Weiterhin können bei der Flächenverarbeitung sogenannte Haltungsflächen (QKan-Tabelle "Teilgebiete") berücksichtigt 
werden, die entweder anhand der Geometrie und gegebenenfalls unter Berücksichtigung des Geländegefälles 
konstruiert oder aus Flurstücken erzeugt worden sind. Damit ist es möglich, große Flächen (z. B. 
grosse Gebäude), die sich über mehrere Flurstücke erstrecken, automatisch aufzuteilen. Außerdem können 
automatisch unbefestigte Flächen aus den freien Flächen zwischen den befestigten Flächen erzeugt werden. 

Es wird unterschieden zwischen Flächen, die als ganzes zugeordnet werden und großen Flächen, die sich über 
mehrere Haltungsflächen erstrecken und deshalb aufgeteilt 
werden müssen. Für diese muss der Anwender in der Tabelle "flaechen" das Attribut "aufteilen" aktivieren bzw. "ja" 
eintragen. In diesem Fall wird für jedes Teilstück, das in einer anderen Haltungsfläche liegt, eine eigene 
Verbindungslinie angelegt. 

.. image:: ./QKan_Bilder/qkan_linkfl_aufteil.png
    :name: Anbindung einer aufgeteilten Fläche


Abbildung: Anbindung einer aufgeteilten Fläche

.. image:: ./QKan_Bilder/Form_Flaechen_aufteil.png
    :name: Formular Flächen

Abbildung: Formular Flächen (hervorgehoben: Attribut "aufteilen")


Die Verbindungslinien können jederzeit manuell nachbearbeitet, ergänzt oder gelöscht werden. 
Maßgebend für den Anwender sind ausschließlich die sichtbaren Verbindungslinien! 

Der Algorithmus ist so angelegt, dass die abflusswirksamen Flächen nach dem Import aus einem externen 
Datenbestand während der gesamten Bearbeitung im Original erhalten bleiben. Sie brauchen also nicht vorher 
durch den Anwender aufgeteilt zu werden. Der Anwender sollte die Flächen lediglich so vorbereiten, dass keine 
Überschneidungen und "Löcher" mehr vorhanden sind, wozu QGIS mehrere Werkzeuge enthält. 

Erst beim Datenexport in das Simulationsprogramm wird die Aufteilung der mit dem Attribut "aufteilen" markierten 
Flächen mittels Verschneidung mit den Haltungsflächen vorgenommen. Das hat den Vorteil, dass der Anwender 
jederzeit Änderungen an den 
Flächen, Haltungsflächen oder Kanalnetzdaten vornehmen kann, um dann erneut die Daten in das Simulationsprogramm zu 
exportieren. 

.. index:: Teilgebiete

.. _linkteilgebiete:

Teilgebiete
-----------

Bei größeren Entwässerungsnetzen ist es hilfreich, die Bearbeitung nacheinander für mehrere Teilgebiete vorzunehmen. 
In QKan dient dazu ein entsprechender Layer "Teilgebiete" (QKan-Tabelle "teilgebiete"). Alle für die Flächenaufteilung 
verwendeten Layer enthalten ein entsprechendes Attribut, mit dem die automatische Erzeugung der Verbindungslinien 
eines oder mehrere ausgewählte Teilgebiete beschränkt werden kann. 

Erstellung eines Teilgebietes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Ein Teilgebiet kann leicht aus :ref:`Haltungsflächen <linkhaltungsflaechen>` erzeugt werden. Dazu müssen alle Haltungsflächen auf dem 
gleichnamigen Layer ausgewählt werden, welche ein Teilgebiet ergeben sollen und über :guilabel:`Bearbeiten` → :guilabel:`Objekte kopieren` 
kopiert werden. Anschließend können diese auf dem Layer "Teilgebiete" eingefügt werden, wenn dieser sich im |Tool_bearbeitungsmodus| 
:guilabel:`Bearbeitungsmodus` befindet. Als erstes müssen nun die eingefügten Flächen mit |Tool_layeraenderungen_speichern| 
:guilabel:`Layeränderungen speichern` gespeichert werden, damit sie im Folgenden mit |Tool_objekte_verschmelzen| 
:guilabel:`Gewählte Objekte verschmelzen` zusammen gefasst werden können. In der Attribut-Tabelle kann das Teilgebiet in der Spalte 
"Namen" benannt werden. Soll die Bearbeitung des Projektes in den erstellten Teilgebieten geschehen, müssen nun als nächstes die Elemente 
des Entwässerungsnetzes den Teilgebieten zugeordnet werden. Dies ist mit der Funktion |Tool_elemente_tezg_zuordnen| 
:guilabel:`Alle Elemente des Entwässerungsnetzes zu Teilgebiet zuordnen` möglich. Dabei ist es wichtig, dass in dem sich öffnenden Fenster 
die Option "überlappend" für Haltungen und Flächen ausgewählt wird (siehe Bild unten). Damit wird sichergestellt, dass auch Flächen 
(z.B. von großen Gebäuden), die nur zum Teil im Teilgebiet liegen, bei der Bearbeitung des Gebietes berücksichtigt werden.

.. image:: ./QKan_Bilder/Fenster_elemente_tezg_zuordnen.png

Abbildung: Formular Elemente einem Teilgebiet zuordnen

.. |Tool_layeraenderungen_speichern| image:: ./QKan_Bilder/Tool_layeraenderungen_speichern.png
                             :width: 1.25 em
.. |Tool_objekte_verschmelzen| image:: ./QKan_Bilder/Tool_objekte_verschmelzen.png
                             :width: 1.25 em
.. |Tool_elemente_tezg_zuordnen| image:: ./QKan_Bilder/Tool_elemente_tezg_zuordnen.png
                             :width: 1.25 em
                             
..
    Import der abflusswirksamen Flächen
    -----------------------------------

    Ausgangspunkt für die nachfolgend beschriebenen Arbeitsschritte ist ein bestehendes QKan-Projekt. Empfehlenswert ist 
    es, dieses durch Import aus einem der in QKan verfügbaren Datenformate (HYSTEM-EXTRAN, Kanal++) zu erzeugen. Die 
    entsprechende Datei des Simulationsprogramms sollte bereits Kanaldaten enthalten; es ist aber auch möglich, eine leere 
    Datei zu verwenden, die vorher mit dem gewünschten Simulationsprogramm angelegt wurde. 

    Die abflusswirksamen Flächen können mit QGIS aus einer Vielzahl von Datenquellen übernommen werden. Empfehlenswert 
    ist es dabei, zunächst die Daten mit QGIS in einen zusätzlichen Layer zu laden. Anschließend können die Flächen 
    mit "Copy & Paste" in den Layer "Flächen" übertragen und der zusätzliche Layer wieder entfernt werden. 

.. index:: Erzeugung von Haltungsflächen

.. _linkhaltungsflaechen:


Erzeugung von Haltungsflächen
-----------------------------

Haltungsflächen haben mit den neueren Simulationsprogrammen einen Paradigmenwechsel erfahren. Früher galt die 
Anforderung, dass je eine Haltungsfläche zu einer Haltung zugeordnet war. 
Heute werden die Haltungsflächen nur noch für zwei Aufgaben benötigt: 

    #. **Erzeugung der unbefestigten Flächen**: diese werden als eigenständige Flächenobjekte gebraucht, um ihnen spezifische Abflussparameter zuordnen zu können, u. a. die Bodenklasse 
    #. **Geometrische Aufteilung von Flächen**, die so groß sind, dass sie mehreren Haltungen zugeordnet werden müssen. 

Nach wie vor gilt die Anforderung, dass die Haltungsflächen das gesamte Einzugsgebiet geschlossen abdecken müssen. 
Da in der heutigen Zeit in der Regel die Grundstücksflächen als Open Data zur  Verfügung stehen, bietet es sich an, 
diese als Ersatz für die früher mühsam erstellten Haltungsflächen einzusetzen.
Die nachfolgend erläuterten Schritte dienen der Datenvorbereitung. 

    #. Die sogenannten Transporthaltungen werden so markiert, dass sie nicht berücksichtigt werden. Es handelt sich dabei um die Haltungen, die nicht an eine Regenentwässerung angeschlossen sind und somit bei der Flächenzuordnung nicht berücksichtigt werden sollen. 
    #. Markieren der aufzuteilenden Flächen. Da die Funktion nur diese Flächen bearbeiten muss, spart QKan erheblich Zeit im Vergleich mit einer Bearbeitung aller Flächen.

.. _linktransporthaltungen:

Markierung von Transporthaltungen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Die Markierung erfolgt hier indirekt über die Zuordnung einer entsprechenden Entwässerungsart: In der 
entsprechenden Referenztabelle, die in der Layerkontrolle in der Gruppe "Referenztabellen" zu finden ist, 
sind eigene Datensätze für Transporthaltungen enthalten, die in der Spalte "ohne RW-Zufluss" den Wert 1 haben sollen 
bzw. das Häkchen gesetzt sein soll. Für betreffenden Haltungen muss nun eine dieser Entwässerungsarten gesetzt werden.
Dazu sollen alle Haltungen ausgewählt werden, an die kein Regenwasser angeschlossen ist. Das sind zum einen 
Transporthaltungen aber auch kurze Verbindungs-Haltungen in Kreuzungsbereichen oder ähnlichem, denen im Folgenden 
keine Flächen zugeordnet werden sollen (siehe Bild unten).

Sind alle Flächen ausgewählt, kann mit :guilabel:`F6` die Attributtabelle geöffnet werden und der 
|Tool_bearbeitungsmodus| :guilabel:`Bearbeitungsmodus` eingeschalten werden. Es empfiehlt sich, nur die 
ausgewählten Datensätze anzeigen zu lassen. Dazu kann unten links in der Schaltfläche 
:guilabel:`Alle gewählten Objekte anzeigen` ausgewählt werden (roter Kasten links, siehe Bild unten).

Um Tippfehler beim nächsten Schritt zu vermeiden, sollte zunächst einen Datensatz in der Formularansicht bearbeitet 
werden. Dazu dient die zweiten Schaltfläche rechts unten (roter Kasten rechts, siehe Bild unten).

.. image:: ./QKan_Bilder/Flaechen_vorbereiten/liste_gewaehlte_haltungen.png

.. |Tool_bearbeitungsmodus| image:: ./QKan_Bilder/Tool_bearbeitungsmodus.png
                             :width: 1.25 em

Nun wird als Entwässerungssystem eine der nicht angeschlossenen Arten, z. B. "MW nicht angeschlossen" gewählt. 
Anschließend kann wieder in die Listen-Ansicht gewechselt werden. 
Mit einem Rechtsklick auf die geänderte Zelle kann der Zellinhalt kopiert werden. 
Dann kann in der Drop-Down-Liste der Quick Field Calculation Bar die Spalte :guilabel:`Entwässerungssystem` 
gewählt werden. In das Formelfenster wird der kopierte Zellinhalt **mit Anführungsstrichen** eingefügt und mit 
:guilabel:`Gewählte aktualisieren` werden alle ausgewählten Haltungen entsprechend angepasst.

.. image:: ./QKan_Bilder/Flaechen_vorbereiten/liste_gewaehlte_aktualisieren.png 

Nun können die Änderungen gespeichert, der Bearbeitungsmodus ausgeschalten und die Auswahl aufgehoben werden.

.. _linkflaechenaufteilung:

Markierung großer aufzuteilender Flächen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Die Flächen, die markiert werden sollten, sind in der Regel alle Straßenflächen, große unbefestigte Flächen 
und besonders große Gebäude. Wenn der Layer "Flächen" in der gleichnamigen Gruppe aktiviert wurde, können 
die betroffenen Flächen mit der |Tool_auswahlfunktion| Auswahlfunktion selektiert werden. Auch hier gilt: 
falls es sich um sehr viele Flächen handelt, können die Bearbeitungsschritte jeweils für eine Teilauswahl 
wiederholt durchgeführt werden.

.. |Tool_auswahlfunktion| image:: ./QKan_Bilder/Tool_auswahlmodus.png
                             :width: 1.25 em

Nun muss für die ausgewählten Flächen nur das Attribut "aufteilen" gesetzt bzw. dort eine 1 eingetragen werden. 
Dies geschieht wie bereits für die Haltungen in folgenden Schritten: 

- Anzeigen der Attributtabelle (Funktionstaste :guilabel:`F6`)
- Bearbeitungsmodus aktivieren (Tastenkombination :guilabel:`Strg` + :guilabel:`E`)
 
In der Bearbeitungszeile sollten folgende Schritte durchgeführt werden: 

- in der Auswahlliste links das Attribut :guilabel:`aufteilen` wählen
- in der Eingabezeile die Zahl "1" (das steht für "aktiviert") eingeben
- Schaltfläche :guilabel:`Gewählte aktualisieren` anklicken

Gegebenenfalls werden diese Schritte für eine weitere Auswahl wiederholt. 

Nun können die Änderungen wieder gespeichert, der Bearbeitungsmodus ausgeschalten und die Auswahl aufgehoben werden. 

Teilen der betroffenen Haltungsflächen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Nach diesen Vorbereitungen können nun mit Hilfe der Funktion |Tool_voronoiflaechen| :guilabel:`Erzeugung von Voronoiflächen zu Haltungen` 
die Haltungsflächen aufgeteilt werden. Falls keine aufzuteilenden Flächen ausgewählt wurden, erscheint eine Warnung. 
Die Funktion würde dann keine Haltungsflächen aufteilen. 

.. |Tool_voronoiflaechen| image:: ./QKan_Bilder/Tool_voronoiflaechen.png
                             :width: 1.25 em

Jetzt sind alle Vorbereitungen getroffen, um unbefestigte Flächen zu erzeugen.

.. index:: Unbefestigte Flächen

.. _createunbeffl:


Erzeugung von unbefestigten Flächen
-----------------------------------

In der Regel enthalten die Datenbestände der abflusswirksamen Flächen nur befestigte Flächen. Für die Verarbeitung in 
QKan ist es empfehlenswert auch für die unbefestigten Flächenanteile entsprechende Flächenobjekte anzulegen. Hierzu 
dient die Funktion |Tool_unbef_flaechen| :guilabel:`Erzeuge unbefestigte Flächen`. Voraussetzung ist, dass im Layer 
"Haltungsflächen" Flächen vorhanden sind, die das Entwässerungsgebiet in Teilflächen unterteilen, die den einzelnen 
Haltungen zugeordnet sind. Ist dies nicht der Fall, ist :ref:`hier <linkhaltungsflaechen>` das Vorgehen zur Erstellung der Haltungsflächen 
beschrieben. Diese Haltungsflächen beziehen sich ausschließlich auf den Niederschlagsabfluss, so dass 
bei der Erstellung nur das Mischwasser- und Regenwassernetz zu berücksichtigen ist. 

.. |Tool_unbef_flaechen| image:: ./QKan_Bilder/Tool_unbef_flaechen.png
                             :width: 1.25 em

Die Haltungsflächen enthalten folgende Attribute, die bei der Erzeugung der unbefestigten Flächen übernommen werden, 
und deshalb vorher entsprechend bearbeitet werden sollten (aber nicht müssen): 

- regenschreiber
- neigkl
- abflussparameter
- haltnam
- teilgebiet

Teilgebiete dienen ausschließlich dazu, die Bearbeitung auf einen Teilbereich eines Gesamtprojektes zu beschränken, 
um einen besseren Überblick über den Bearbeitungsfortgang zu behalten. Außerdem beeinflusst die zu bearbeitende 
Anzahl an Objekten bei einigen Funktionen die Laufzeit. Näheres hierzu siehe :ref:`Teilgebiete <linkteilgebiete>`


Flächen mit Haltungen verknüpfen
--------------------------------

Ein Video zur Verknüpfung von Flächen mit Haltungen ist |video_flanb_erst| zu finden. 

.. |video_flanb_erst| raw:: html

   <a href="https://fh-aachen.sciebo.de/s/SCQxuaInPgGsAFK" target="_blank">hier</a>
   
Die Verbindung von Flächen mit Haltungen geschieht über Linien, welche in dem Layer "Anbindungen Flächen" unter "Flächen" abgelegt sind. 
Diese Verbindungslinien können automatisch erzeugt werden, wenn vorher entsprechende Bearbeitungsschritte durchgeführt werden. 
Dafür müssen zum einen große Flächen, welche mehr als einer Haltung zugeordnet werden können aufgeteilt werden (eine Anleitung ist 
:ref:`hier <linkflaechenaufteilung>` zu finden) und zum anderen müssen Haltungen, an welche keine Flächen angeschlossen sind, 
gekennzeichnet werden (eine Anleitung ist :ref:`hier <linktransporthaltungen>` zu finden). Außerdem kann es bei größeren Einzugsgebieten 
hilfreich sein, wenn diese in mehrere :ref:`Teilgebiete <linkteilgebiete>` unterteilt werden. 

Sind die Vorbereitungen abgeschlossen, können nun die Flächen den Haltungen zugeordnet werden. Dies geschieht mit der Funktion 
|Tool_verknuepfungslinien_erstellen| :guilabel:`Erzeuge Verknüpfungslinien von Flächen zu Haltungen`. Hierbei sollte die Voreinstellung, 
dass nur ausgewählte Entwässerungsarten berücksichtigt werden, nicht verändert werden. Sind Teilgebiete erstellt worden und es soll in 
diesen gearbeitet werden, kann dies über die Auswahl im rechten Kasten der Filteroptionen "Allgemein" geschehen (siehe Bild unten). 
In dem Abschnitt "Optionen zur Erzeugung von Zuordnungen" kann ausgewählt werden, wie Flächen zugeordnet werden sollen - entweder über 
die nächste Kante einer Fläche zu einer Haltung oder über den Mittelpunkt der Fläche zu der nächstliegenden Haltung. 
Der Suchradius sollte ausreichend groß gewählt werden, sodass alle Elemente bei der Zuordnung berücksichtigt werden. Dahingegen sollte der 
Fangradius möglichst klein sein, da sonst die Auswahl einzelner Verbindungslinien erschwert wird. Der Rest der Optionen sollte in der Regel 
nicht verändert werden. (Ist zu befürchten, dass Flächenobjekte Fehler haben, wie z.B. doppelte Stützstellen, so sollte die Option 
"Flächenobjekte bereinigen" zusätzlich ausgewählt werden. Das Formular kann mit :guilabel:`OK` geschlossen werden und die Verbindungslinien 
erscheinen nun auf dem Plan.

.. image:: ./QKan_Bilder/Verbindungslinien_erstellen.png
Abbildung: Formular Verbindungslinien erstellen

.. |Tool_verknuepfungslinien_erstellen| image:: ./QKan_Bilder/Tool_verknuepfungslinien_erstellen.png
                             :width: 1.25 em

Die Zuordnung sollte visuell überprüft werden.

Verbindungslinien bearbeiten
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Gibt es unerwünschte Zuordnungen von Flächen zu Haltungen können diese leicht manuell gelöscht oder verschoben werden. Ist der Layer auf 
dem die Verbindungslinien liegen im |Tool_bearbeitungsmodus| :guilabel:`Bearbeitungsmodus`, kann das |Tool_stuetzpunktwerkzeug| 
:guilabel:`Stützpunktwerkzeug` ausgewählt werden. Damit die Bearbeitung funktioniert ist es wichtig, dass das 
|Tool_topologisches_editieren| :guilabel:`topoligisches editieren Werkzeug` deaktiviert ist. Um eine Stützstelle zu ändern, muss nach 
Aktivierung des |Tool_stuetzpunktwerkzeug| :guilabel:`Stützpunktwerkzeug` die zu bearbeitende Verbindungslinien mit Rechtsklick fixiert 
werden. So ist es möglich, dass nur die Stützstelle der gewünschten Verbindungslinien gewählt wird, wenn anschließend die entsprechende 
Stützstelle mit Linksklick ausgewählt wird. Als nächstes wird die Haltung ausgewählt, mit welcher die Fläche eigentlich verbunden werden 
sollte. Nach Klick auf die Haltung sollte die geänderte Verbindungslinie auf dem Plan erscheinen. Die Auswahl der Verbindungslinie kann 
durch einen erneuten Rechtsklick auf die gewählt Linie aufgehoben werden.

.. |Tool_stuetzpunktwerkzeug| image:: ./QKan_Bilder/Tool_stuetzpunktwerkzeug.png
                             :width: 1.25 em
.. |Tool_topologisches_editieren| image:: ./QKan_Bilder/Tool_topologisches_editieren.png
                             :width: 1.25 em
..
    Erzeugung von Anbindungen zwischen Einzeleinleitern und Haltungen
    -----------------------------------------------------------------

    (Dieses Kapitel muss noch erstellt werden)