Installation
============

Willkommen beim Step by Step Tutorial zur Installation von QKan mit dem Betriebssystem Windows. QKan kann auch unter 
Linux verwendet werden, wo QGIS zum größten Teil weiterhin entwickelt wird. Die nachfolgenden Schritte sind dort in 
ähnlicher Weise durchzuführen. 

Um QKan auf einem Computer neu einzurichten sind einige Arbeitsschritte notwendig, welche im Folgenden vorgestellt werden. 
Zunächst aber noch eine grundlegende Anmerkung: QKan besteht aus einem Plugin, mit dem das Open-Source GIS-Progamm QGIS um 
vielfältige Funktionen zur Kanaldatenverwaltung erweitert wird. Ausschließlich für die Verwendung im Zusammenhang mit dem 
Simulationsprogramms HYSTEM-EXTRAN 7.x wird ein zweites Plugin benötigt, das aber noch zusätzlich weitere Installationen 
notwendig macht. Dies hängt damit zusammen, dass HYSTEM-EXTRAN 7.x eine Firebird-Datenbank verwendet. 


QGIS Installieren
-----------------

QKan basiert auf dem Open-Source-Programm QGIS 3. Deshalb wird dieses als erstes benötigt.
Die aktuelle Version von QGIS finden Sie hier: QGIS_ oder falls dieser Link nicht funktioniert können Sie manuell 
www.QGIS.org aufrufen. Für größere Organisationen ist die sogenannte LTR (long time release) Version empfehlenswert, 
weil bei dieser Variante mehr Wert auf Stabilität als auf die neuesten Funktionen gelegt wird. 

.. _QGIS: http://www.QGIS.org/de/site/forusers/download.html

Laden Sie die für Sie zutreffende "Eigenständige QGIS-Installation" herunter. Stellen Sie sicher, 
dass Ihnen genügend freier Speicherplatz zur Verfügung steht, da die QGIS-Installation etwa 1,5 GB 
Speicherplatz einnehmen wird. Wählen Sie in Abhänigkeit von Ihrem Betriebssystem und Ihrer Betriebssystem-Version einen Downloadlink aus. 
Die nachstehende Abbildung zeigt die "Eigenständige QGIS-Installation Version 3.xx (64bit)":

.. image:: ./QKan_Bilder/QGIS_herunterladen.png

Starten Sie die Installation, akzeptieren das Lizenzabkommen und bestätigen die Installation im Standardverzeichnis "C:\\Programme\\QGIS 3.xx". Als letztes werden Sie nach zusätzlichen Komponenten, wie zum Beispiel dem North Carolina Data Set gefragt:

.. image:: ./QKan_Bilder/QGIS_komponenten.png

Es handelt sich um Beispieldaten, die für die Nutzung von QKan nicht benötigt werden. Klicken Sie anschließend auf "Installieren", um die Installation zu starten. Diese Installation kann einige Minuten in Anspruch nehmen.

.. _QKan_plugins_fuer_QGIS

QKan-Plugin Installation
------------------------

Nachdem QGIS erfolgreich auf Ihrem System installiert wurde, kann nun das QKan-Plugin installiert werden. 
Dieses kann unter Erweiterungen -> Erweiterungen verwalten und installieren... auf dem Reiter "Alle" in der Liste der Plug-Ins gefunden werden. 
Wenn es ausgewählt ist, kann es über den Button "Erweiterung installieren" auf dem Rechner installiert werden. 
Es sollte darauf geachtet werden, dass immer mit der aktuellsten Version gearbeitet wird. 
Installationen von weiteren Plugins für den Export nach HYSTEM-EXTRAN sind nun nicht mehr nötig. 

.. image:: ./QKan_Bilder/QKan_Plugin.png

Grafikeinstellung für QKan
^^^^^^^^^^^^^^^^^^^^^^^^^^

Wenn QKan auf einem Laptop genutzt wird, kann es vorkommen, dass die Formulare fehlerhaft angezeigt werden (Beispiel siehe Bild unten). 
Dies beeinträchtigt die Funktion der Formulare nicht, kann jedoch die Nutzung dieser erschweren. 

.. image:: ./QKan_Bilder/Formular_fehlerhaft.png

Um dieses Problem zu beheben kann über die Windows-Suchleiste mit "Systemumgebungsvariablen bearbeiten" die Systemeigenschaften geöffnet 
werden. 