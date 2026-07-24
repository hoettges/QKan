QKan-Projekte auf dem Tablet
============================

Um ein QKan-Projekt auf dem Tablet darzustellen, sind mehrere vorbereitende Schritte notwendig. 

 - Erzeugen eines QField-Projektes mit dem Plugin :guilabel:`QField-Sync`
 - Anpassen der Formulare für die Anzeige auf dem Tablet
 - Übertragung auf das Tablet


Erzeugen des QField-Projektes
-----------------------------

Zunächst muss das Verzeichnis für das zu erzeugende QField-Projekt festgelegt werden. Dazu wird über das 
Menü :guilabel:`Erweiterungen` > :guilabel: `QFielSync` > :guilabel: `Einstellungen` das Export-Verzeichnis
"Standard-Verzeichnis für den Paket-Export" ausgewählt. Hier empfiehlt es sich, ein leicht zugängliches 
Verzeichnis zu wählen, z. B. `%homepath%\documents\QField\export` (`%homepath%` wird 
automatisch durch das Userverzeichnis ersetzt).


Projektkonfiguration
^^^^^^^^^^^^^^^^^^^^

Obwohl das QField-Projekt konventionell durch Datenübertragung und nicht mit Hilfe der QFieldCloud auf das 
Tablet übertragen soll, muss die Konfiguration in der Karteikarte :guilabel:`QFieldCloud` 
vorgenommen werden. Dort muss die gewählte Option von "Online-Layer bevorzugen" in die entsprechende 
Offline-Variante geändert werden. 

In dieser Anleitung wird davon ausgegangen, dass die Hintergrundkarten über eine Online-Verbindung 
über WMS-Dienste zur Verfügung stehen. Es wäre aber auch möglich, lokale Hintergrundkarten in das Projekt 
zu integrieren, was allerdings je nach gewählter Auflösung zu exorbitant großen Datenmengen führt. Die 
entsprechenden Einstellungen stehen nach Aktivierung des Kontrollfeldes :guilabel:`Grundkarte` zur 
Verfügung. 


Erstellung des QField-Projektes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Die Erstellung des QField-Projektes erfolgt mit dem 
Menü :guilabel:`Erweiterungen` > :guilabel:`QFieldSync` > :guilabel:`Für QField verpacken`. 

Der Ordner, in dem das Projekt gespeichert wird, kann ganz einfach über die Informationszeile, die nach 
Fertigstellung in QGIS angezeigt wird, geöffnet werden. Für die Datenübertragung auf das Tablet empfiehlt 
es sich, das Projekt als ZIP-Archiv zusammenzufassen und dieses anschließend auf ein Cloud-Verzeichnis
zu laden. Der Grund ist, dass iPads nur noch sehr eingeschränkte Datenübertragung zulassen, und der 
Download aus dem Internet vergleichsweise simpel ist. 


Übertragung auf das iPad
^^^^^^^^^^^^^^^^^^^^^^^^

Der Download erfolgt am besten über den Safari-Browser. Nachdem das ZIP-Archiv mit dem QField-Projekt 
heruntergeladen ist, wird darin enthaltene Verzeichnis entpackt und auf den dafür vorgesehenen 
Ordner :guilabel:`QField` > :guilabel:`Imported projects` verschoben. Anschließend kann das Projekt 
mit QField geöffnet werden. 


Videoanleitungen
----------------

Zwei Videoanleitungen führen die Erstellung des QField-Projektes sowie die Übertragung auf das iPad 
beispielhaft vor:

 - |video_qkan2qfield|
 - |video_qkan_ipad|

.. |video_qkan2qfield| raw:: html

   <a href="https://fh-aachen.sciebo.de/s/CHVnPYpbWxpe13x" target="_blank">Video: Erstellung des QField-Projektes</a>

.. |video_qkan_ipad| raw:: html

   <a href="https://fh-aachen.sciebo.de/s/641RTNe0tEwIc4W" target="_blank">Video: Übertragung auf das iPad</a>

