Allgemeines
===========

QKan ist ein Werkzeug zur Simulation von Kanalnetzen. Es dient der Datenvor- und Nachbereitung und speichert die Kanalnetzdaten dazu in einer SQLite-Datenbank. 

QKan baut auf QGIS ab Version 3.22 auf und besteht aus einer Vielzahl von Plugins, die u.a. folgende Funktionsbereiche umfassen: 

 - Datenimport von Kanalnetzdaten aus Tabellen und einer Vielzahl von Austauschformaten und Darstellung in QGIS. 
 - Aufbereitung für die Nutzung in Simulationsprogrammen
 - Weitergabe eines vollständigen Kanalkatasters an Nutzer, die über keine Lizenz eines Simulationsprogramms verfügen
 - Ergebnisdarstellung
 - Darstellung von Kanalzustandsdaten und deren Auswertung nach ISYBAU oder DWA-Richtlinie

Ein besonderer Schwerpunkt ist die Verarbeitung der befestigten und unbefestigten Flächen. QKan enthält eine Funktion zur automatisierten 
Zuordnung dieser Flächen zu den Haltungen, die optional beim Export in das Simulationsprogramm mit Haltungflächen verschnitten werden. 
Dabei ist es sowohl möglich, die Flächenzuordnung interaktiv für kleine Teilgebiete als auch automatisch für große Kanalnetze durchzuführen. 

Langfristig soll QKan eine Anbindung an die in Deutschland weit verbreiteten hydrodynamischen Simulationsprogramme bekommen. Bereits realisiert sind: 

 - Kanal++/DYNA
 - HYSTEM-EXTRAN 8.x
 - MIKE+ (bisher nur Import für ausgewählte Datentypen)
 - SWMM
 - HYSTEM-EXTRAN 7.8 und 7.9 (setzt zusätzliche Installationen voraus)

Grundsätzlich enthält QKan die Möglichkeit, Daten über das Clipboard in alle QKan-Tabellen einzufügen. Dabei werden automatisch grafische Objekte (Schächte, Haltungen) erzeugt. 

Außerdem bestehen mit den Grundfunktionen von QGIS verschiedene Möglichkeiten des Datenim- und Exports:

 - Text (ASCII)
 - CSV
 - Excel
 - MS-Access-Datenbanken
 - (fast) beliebige OGC-konforme Geodaten

Wesentlicher Bestandteil von QKan ist eine Datenstruktur, die einen gemeinsamen Nenner der verschiedenen in Deutschland eingesetzten Programme darstellt. Das bedeutet insbesondere, dass die sogenannten "Sonderbauwerke", also Speicher, Pumpen, Wehre, Drosseln, Auslässe etc. nur mit den allgemeinen Daten in QKan verwaltet werden, programmspezifische Attribute jedoch in den Daten des jeweiligen Simulationsprogramms verwaltet werden müssen. 

Die Daten können sowohl mit den QKan-Funktionen verarbeitet werden, gleichzeitig stehen aber auch die vielfältigen und umfassenden Funktionen von QGIS zur Verfügung. Insbesondere kann mit Hilfe der Datenbanksprache SQL beinahe jede denkbare Aufgabe realisiert werden. 

Grundlagen
----------

QKan ist ein Open-Source-Projekt von `Jörg Höttges`_ . Es wird seit Aug 2016 an der FH Aachen entwickelt. 

.. _`Jörg Höttges`: https://www.fh-aachen.de/menschen/hoettges  

Es steht auf der Plattform GITHUB zum Download zur Verfügung (siehe Installation von QKan) und unterliegt der Open-Source-Lizenz GPL 3.0. 

Die Entwicklung wurde durch das Land NRW im Rahmen der Förderprogramme "Mittelstand.Innovativ! - Innovationsgutschein F+E" (1)
und "Mittelstand Innovativ & Digital (MID) – Teil MID-Digitalisierung" (2) sowie durch folgende Ingenieurbüros unterstützt: 

 - `blue-ing. GmbH, Düsseldorf (1, 2) <http://www.blue-ing.de/>`_
 - Ingenieurbüro Reinhard Beck GmbH, Wuppertal (1)
 - `Fischer Teamplan Ingenieurbüro GmbH, Erftstadt (1) <https://www.fischer-teamplan.de/>`_
 - `Ingenieurgesellschaft Dr. Ing. Nacken mbH, Aachen (1) <https://www.nacken-ingenieure.de/>`_
 - `ATD Ingenieurgesellschaft mbH, Aachen (2) <https://www.atdgmbh.de/>`_
 - `Tuttahs & Meyer Ing.-GmbH, Aachen (2) <https://tuttahs-meyer.de/>`_
 - `Ingenieurbüro Achten und Jansen GmbH, Aachen (2) <https://www.achten-jansen.de/>`_

Team
----

 - Jörg Höttges
 - Yannick Linke
 - Nora Blase
 - Friederike Kimmich

Ehemalige
---------

 - Leon Ochsenfeld

Weitere Quellen
---------------

 - Dank an `Gerhard Dreier <https://www.geoplaning.de>`_, aus dessen Plugins 
   `"DWA_M150_XML_Import" und "longitudinal" <https://plugins.qgis.org/plugins/user/amphibitus/admin>`_ 
   Teile des Quellcodes verwendet wurden.

