Daten: prüfen, auswählen, darstellen
====================================

Plausibilitätsprüfung
---------------------

Mit der Funktion |Tool_plausibilitaet| :guilabel:`Plausibilitätsprüfung` können die in der Tabelle 
„Plausibilitätsprüfungen“ definierten Prüfungen komfortabel ausgeführt werden.
Die auswählbaren Themen entsprechen den dort hinterlegten Gruppen. Die Tabelle 
„Plausibilitätsprüfungen“ enthält zudem Beschreibungen und die jeweiligen SQL-Abfragen der einzelnen Prüfungen. 

.. image:: ./QKan_Bilder/Formulare/plausibilitaet.png
.. image:: ./QKan_Bilder/tabelle_plausi.png
.. |Tool_plausibilitaet| image:: ./QKan_Bilder/Tool_plausibilitaet.png
                             :width: 1.25 em
                             
Zur Durchführung können eine oder mehrere Themen ausgewählt und die entsprechenden SQL-Abfragen ausgeführt werden. 
Nach Durchführung der Plausibilitätsprüfung öffnet sich die Tabelle "Fehlerliste" automatisch. 

.. image:: ./QKan_Bilder/tabelle_fehler.png

Hier werden gefundene Fehler aufgelistet. Über das Symbol in
der ersten Spalte „Aktionen“ kann das betroffene Objekt in der Karte markiert und automatisch herangezoomt werden.
Mit der Option „Ergebnisse zu bestehenden hinzufügen“ wird die vorhandene Fehlerliste ergänzt statt überschrieben.
Die Option „Fehlerliste auf 5 Meldungen je Fehlertyp beschränken“ zeigt pro Fehlertyp maximal fünf Einträge an und verbessert so die Übersicht.
Die Gesamtanzahl je Fehlertyp wird am Ende jeder Warnung angezeigt.
Die Plausibilitätsprüfungen können erweitert werden. Dazu muss in der Spalte „sql“ eine SQL-Abfrage hinterlegt werden, die folgende Spalten liefert:
•	objid: Identifikation des betroffenen Objekts 
•	bemerkung: Beschreibung des Fehlers, ggf. mit Zusatzinformationen 
Die Bezeichnung in der Spalte „Gruppe“ erscheint in der Themenauswahl des Formulars „Plausibilitätsprüfungen“.
Eigene Prüfungen sollten eine abweichende Gruppenbezeichnung erhalten, z. B. „Netzstruktur, ergänzt“.
Nur die von QKan vorgegebenen Standardgruppen werden bei Updates automatisch aktualisiert.


.. index:: Auswahl erweitern / Netzverfolgung

Auswahl erweitern / Netzverfolgung
----------------------------------

Mit dem Tool |Tool_auswahl| :guilabel:`Auswahl erweitern/Netzverfolgung` kann auf verschiedene Arten eine Auswahl 
von Elementen im Kanalnetz erzeugt werden. Die ausgewählten Elemente werden 
automatisch in den Datenbanktabellen sel_schaechte, sel_haltungen und sel_flaechen gespeichert.

.. image:: ./QKan_Bilder/Formulare/auswahl_netzverfolgung.png
.. |Tool_auswahl| image:: ./QKan_Bilder/Tool_auswahl.png
                             :width: 1.25 em

Bei einer erneuten Auswahl werden die bestehenden Einträge in diesen Tabellen automatisch überschrieben, sodass 
immer nur die aktuell ausgewählten Elemente berücksichtigt werden.
Auswahlmöglichkeiten im Detail

1. Kanalnetz oberhalb / unterhalb / längster Fließweg oberhalb
    - Für diese Auswahlmethoden muss mindestens ein Schacht im Kanalnetz ausgewählt werden.
    - Das Tool markiert automatisch alle Schächte, Haltungen und zugehörigen Flächen, die stromaufwärts oder 
      stromabwärts vom ausgewählten Schacht liegen bzw. entlang des längsten 
      Fließweges oberhalb.

2. Auswahl zwischen zwei Elementen
    - Hierfür können entweder zwei Schächte oder zwei Haltungen ausgewählt werden.
    - Das Tool wählt automatisch alle Elemente aus, die zwischen diesen beiden Punkten liegen, unabhängig davon, 
      wie viele Haltungen dazwischen liegen.

3. Auswahl innerhalb von Teilgebieten
    - Um alle Elemente eines bestimmten Teilgebiets auszuwählen, muss das entsprechende Teilgebiet ausgewählt werden.
    - Das Tool markiert dann alle Schächte, Haltungen und Flächen, die zu diesem Teilgebiet gehören.

Hinweise
    - Jede Auswahl wird sofort in den Datenbanktabellen gespeichert, sodass nachfolgende Funktionen wie Längsschnitt, Substanzklassifizierung oder Export direkt auf dieser 
      Auswahl arbeiten können.
    - Bei Änderungen an der Auswahl empfiehlt es sich, die Tabellen ggf. zu aktualisieren, um sicherzustellen, dass 
      alle Analysen auf den aktuellen Elementen basieren.


.. index:: Längsschnitt

Längsschnitt
------------
Mit dem Tool |Tool_laengsschnitt| :guilabel:`Längsschnitt` lassen sich Längsschnitte des Kanalnetzes erzeugen.

.. image:: ./QKan_Bilder/Formulare/laengsschnitt.png
.. |Tool_laengsschnitt| image:: ./QKan_Bilder/Tool_laengsschnitt.png
                             :width: 1.25 em

Um den Längsschnitt nutzen zu können, müssen zunächst Elemente aus dem Layer „Schächte“ oder „Haltungen“ ausgewählt werden. Der Längsschnitt wird entweder 
zwischen zwei ausgewählten Elementen erzeugt oder entlang einer Reihe mehrerer ausgewählter Elemente.
Wenn sich die Auswahl oder Eingaben ändern, kann über den Refresh-Button die Anzeige aktualisiert werden.
Mit dem Button „Auswahl anzeigen“ lassen sich die für den Längsschnitt verwendeten Elemente erneut in der Karte markieren.
Mit dem Button „Export in DXF“ kann eine DXF Datei vom aktuell angezeigt Längsschnitt abgespeichert werden. Wenn der maximale Wasserstand aktiviert ist, wird dieser mit exportiert.
Damit die Anzeige des maximalen Wasserstands, der animierte Längsschnitt sowie die Ganglinie genutzt werden können, muss zunächst eine HYSTEM-EXTRAN-Ergebnisdatei ausgewählt werden.
Im Anschluss kann im Reiter „Animierter Längsschnitt“ über den Button „Längsschnitt anzeigen“ der animierte Längsschnitt geöffnet werden
Die Animation kann anschließend über die Steuerelemente im unteren Bereich in Bezug auf Abspielgeschwindigkeit und Zeitpunkt bedient werden.
Im Reiter „Ganglinien“ lassen sich mit dem Button „Ganglinie anzeigen“ verschiedene Ganglinien aus den Ergebnisdaten erzeugen – beispielsweise Zufluss, Wasserstand oder Durchfluss.


.. index:: Transformation

Transformation
--------------
Mit dem Tool |Tool_transformation| :guilabel:`Transformation` können alle Tabellen eines Projektes von einem anderen Koordinatensystem in das für ein Projekt festgelegtes 
Koordinatensystem transformiert werden.

.. image:: ./QKan_Bilder/Formulare/transformation.png
.. |Tool_transformation| image:: ./QKan_Bilder/icon_transformation.png
                             :width: 1.25 em

Falls Kanaldaten mit einer der QKan-Importfunktionen (M150, HYSTEM-EXTRAN, Clipboard, etc.) importiert werden sollen, diese aber in einem anderen als dem für das QKan-Projekt 
vorgesehenen Koordinatensystem gespeichert sind, wird folgendes Vorgehen empfohlen, um die Daten nach dem Import in das vorgesehene Koordinatensystem zu transformieren: 

1. Import der Daten, wobei bereits das endgültig vorgesehene Koordinatensystem eingestellt werden muss. Die Daten erscheinen zunächst an einer falschen Position im Kartenfenster.

2. Transformation, wobei im Formular nur das Koordinatensystem der Quelldaten ausgewählt werden muss. Das Koordinatensystem des Zielsystems ist ja durch das Projekt bereits vorgegeben. 

3. Es empfiehlt sich, das Projekt nach der Transformation neu zu laden, weil dabei einige interne geographische Indizes aktualisiert werden, die z. B. für die Layer-Funktion 
   :guilabel:`Auf Layer Zoomen` benötigt werden.