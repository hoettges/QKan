Export nach HYSTEM-EXTRAN
=========================
.. Eine Videoanleitung zum Export nach HYSTEM-EXTRAN ist `hier <LIN>`_ zu finden.

Anpassung des Datumsformates
----------------------------

Bevor der Export-Vorgang gestartet wird, sollte das Datumsformat geprüft werden, da dieses häufiger zu Problemen führt.
Das Datumsformat muss für den Export in der Form "yyyy-mm-dd hh:mm:ss" in der Tabelle vorliegen.
In dem hier verwendeten Datensatz fehlt die Sekundenangabe.
Um dies zu ändern muss die Attributtabelle geöffnet und im :guilabel:`Bearbeitungsmodus` |Tool_bearbeitungsmodus| sein.
Anschließed sollte das Feld "bearbeitet" aus der Drop-Down-Liste ausgewählt werden.
In die Schnellfeldberechnungsleiste sollte nun das Datum in dem benötigten Format \'yyyy-mm-dd hh:mm:ss\' (Achtung: einfache Anführungszeichen verwenden!) eingetragen werden.
Mit "Alle aktualisieren" kann der Zellinhalt für alle Zellen übernommen werden.
Es ist zu empfehlne die Eingabe zu kopieren, da dieser Schritt für alle Attributtabellen wiederholt werden muss.

.. image:: ./QKan_Bilder/Export_he/Datum_unbearbeitet_kurz.png
     :name: Datumsformat **vor** Bearbeitung

Datumsformat **vor** Bearbeitung

.. image:: ./QKan_Bilder/Export_he/Datum_bearbeitet_kurz.png
     :name: Datumsformat **nach** Bearbeitung
	 
Datumsformat **nach** Bearbeitung

.. |Tool_bearbeitungsmodus| image:: ./QKan_Bilder/Tool_bearbeitungsmodus.png
                             :width: 1.25 em

Nun muss das Datum in allen Attributtabellen angepasst werden, die aus Excel übernommen wurden.
Daten, die das Programm selber erstellt hat, sind automatisch im richtigen Format gespeichert.


Erstellung einer Vorlagen-Datenbank in HYSTEM-EXTRAN
----------------------------------------------------
Für den Export der Daten von QKan nach HYSTEM-EXTRAN wird eine Vorlage-Datenbank benötigt.
Zur Erstellung dieser muss HYSTEM-EXTRAN gestartet werden.
Über :guilabel:`Datei` und :guilabel:`Neu...` kann eine neue Datenbank angelegt werden.
Für den Export ist es notwenidg, eine Regenreihe mit einem dazugehörigen Regenschreiber anzulegen.
In dem Dialogfenster des Regenschreibers können die Daten wie unten dargestellt ergänzt werden.
Wichtig hierbei ist, dass der Regenschreiber den Namen erhält, der auch in den Flächendaten verwendet wurde (hier: "1").

.. image:: ./QKan_Bilder/Export_he/Regenschreiber.png

Eingabeformular aus dem Programm `HYSTEM-EXTRAN, ITWH GmbH <https://itwh.de/de/softwareprodukte/desktop/hystem-extran/>`_

Die Regenreihe kann über :guilabel:`Assistenten` und :guilabel:`Modellregen...` hinzugefügt werden.
In diesem Beispiel wird eine Modellregen des Euler Typ II mit einer Jährlichkeit von drei Jahren erstellt.
Der Name kann frei gewählt werden (hier: Euler_II_3a).
Auch das Datum ist frei wählbar.
Es sollte jedoch darauf geachtet werden, dass die Dauer realistisch ist (hier: 60 Minuten mit einer Intervallbreite von 5 min.).
Anschließend sollte die Modellregen-Art "Euler Typ II" mit einer Jährlichkeit von 3 Jahren ("a") festgesetzt werden.
Die Regenmenge soll nach KOSTRA-DWD ermittelt werden.
Zum Definieren des KOSTRA-DWD-Datensatzes können die Daten wie unten abgebildet übernommen werden.

.. image:: ./QKan_Bilder/Export_he/Kostra_assistent_modellregen.png

Eingabeformular aus dem Programm `HYSTEM-EXTRAN, ITWH GmbH <https://itwh.de/de/softwareprodukte/desktop/hystem-extran/>`_

Diese Daten können aus einem Projekt, welches `hier <https://www.fh-aachen.de/fileadmin/people/fb02_hoettges/kostra_dwd_2010r.zip>`_ zum download zur Verfügung steht, übernommen werden.
Dazu muss das zu bearbeitende Gebiet auf der Karte gesucht werden.
Im Anschluss können die Daten über |Tool_info| :guilabel:`Info-Tool` mit einem Klick auf die Karte abgerufen werden.

.. image:: ./QKan_Bilder/Export_he/Koastra_objektattribute.png

Eingabeformular aus dem Programm `HYSTEM-EXTRAN, ITWH GmbH <https://itwh.de/de/softwareprodukte/desktop/hystem-extran/>`_

.. |Tool_info| image:: ./QKan_Bilder/Tool_info.png
							 :width: 1.25 em

Nun wurden alle nötigen Definitionen getroffen und der Modellregen kann erstellt werden.
Bei der nun erstellten Regenreihe muss noch der Name der Station mit dem Namen welcher beim Regenschreiber gewählt wurde angepasst werden (hier: "1234").
Anschließend kann die Maske geschlossen werden und das Projekt kann gespeichert werden.
Da das Beispielprojekt keine Sonderbauwerke (z.B. Drosseln, Pumpen oder Wehre) besitzt, müssen diese hier auch nicht angelegt werden.
So ist die Vorlage-Datenbank nun ausreichend vorbereitet und HYSTEM-EXTRAN muss geschlossen werden.
(HYSTEM-EXTRAN öffnet eine Datenbank exklusiv, dass heißt, dass es nicht möglich ist, gleichzeitig mit einer anderen Anwendung auf diese Datenbank zuzugreifen.
Dies würde daher zu einer Fehlermeldung beim QKan Export führen.)

Export nach HYSTEM-EXTRAN 8
---------------------------
Jetzt kann das Formular "Export to HE" mit |Tool_export| :guilabel:`Export nach HE` geöffnet werden.
In dem Formular wird die soeben erstellte Vorlage-Datenbank und ein Datenziel, welches definiert werden muss, ausgewählt.
Die übrigen Auswahlfelder sollten wie unten dargestellt übernommen werden.
Dann kann der Export mit :guilabel:`OK` gestartet werden.

.. image:: ./QKan_Bilder/Export_he/export_he.png

.. |Tool_export| image:: ./QKan_Bilder/Export_he/Tool_export_he.png
							 :width: 1.25 em

Die fertige Export-Datenbank kann nun mit HYSTEM-EXTRAN geöffnet werden.
Es sollten nur kleinere Fehler in den Meldungen erscheinen (z.B. fehlerhafte Sohlhöhen und zu lange Namen) die zum Teil händisch angepasst bzw. ignoriert werden können.
Damit ist der Workflow abgeschlossen.

.. image:: ./QKan_Bilder/Export_he/Ergebnis_HE.png
     :name: Ergebnis

Ergebnis mit dem Programm `HYSTEM-EXTRAN, ITWH GmbH <https://itwh.de/de/softwareprodukte/desktop/hystem-extran/>`_
