STRAKAT
=======

Import aus STRAKAT
------------------

Eine Videoanleitung zum Import von Kanal- und Untersuchungsdaten aus einem STRAKAT-Projekt ist |video_import_strakat| zu finden.

.. |video_import_strakat| raw:: html

   <a href="https://fh-aachen.sciebo.de/s/WlkCo0BO1mdC8Qy" target="_blank">hier</a>

Mit der Funktion |Tool_import_strakat| :guilabel:`Import aus STRAKAT` ist es nun möglich Daten aus einem STRAKAT-Verzeichnis in ein QKan-Projekt 
zu laden.

.. image:: ./QKan_Bilder/Formulare/import_strakat.png
.. |Tool_import_strakat| image:: ./QKan_Bilder/Tool_import_strakat.png
                             :width: 1.25 em

Datenquelle
+++++++++++
Die Kanalnetzdaten werden in Strakat in mehreren Dateien mit der Endung `*`.rwtopen gespeichert. Die betreffenden Dateien enthalten die 
Kanalnetzdaten, Hausanschlussleitungen und die Zustandsdaten aus den Kanal-TV-Untersuchungen. Dieser Ordner muss hier ausgewählt werden 
und der QKan Import zieht die richtigen Dateien vollautomatisch aus.  Ebenfalls sollte hier das entsprechende Projektionssystem (i.d.R. 
UTM Zone 32N) gewählt werden. 
 
Datenziel
+++++++++
Hier wird das Datenziel - die Sqlite-Datenbank und QGIS-Projektdatei - ausgewählt. Ist noch keine Zieldatenbank (bzw. Projektdatei) 
vorhanden, kann diese hier erstellt werden.

Verzeichnisse Medien der TV-Befahrung
+++++++++++++++++++++++++++++++++++++
Die Verzeichnisse für die Fotos und Videos der TV-Befahrung werden hier ausgewählt bzw. können hier neu erstellt werden. 
    
Auswahl Kanalnetzdaten
++++++++++++++++++++++
Hier kann gewählt werden, welche Daten importiert werden sollen. Die Option „Rohranfänge verwenden“ sollte gewählt werden, wenn die 
Haltungsanfänge auf die extra gespeicherten Rohranfangs-Koordinaten gesetzt werden sollen. Ist diese Option nicht aktiviert, werden nur
die Koordinaten für die Schnittpunkt-Mittelpunkte der Haltungen aus STRAKAT importiert. 
 
Auswahl Untersuchungsdaten
++++++++++++++++++++++++++
Auch bei den Untersuchungsdaten, kann ausgewählt werden, welche Daten importiert werden sollen. Zusätzlich gibt es hier die Option, einen 
Testimport durchzuführen, welcher zeitlich deutlich schneller ist. 
   
Toleranzen
++++++++++
Diese Option ist sehr wichtig, da STRAKAT identische Schächte mehrfach abspeichert und diese nicht immer exakt gefangen sind. Durch die 
Angabe eines Toleranzwerts können diese Schächte dennoch als identisch identifiziert werden. Es wird empfohlen den gegebenen Zahlenwert 
(0,1 m) zu lassen. 