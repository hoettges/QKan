Allgemeines
===========

QKan baut auf QGIS 3 auf und besteht aus einer Vielzahl von Plugins, die eine Palette von Funktionen zur Verarbeitung von Kanaldaten umfassen. 

Ein besonderer Schwerpunkt ist die Verarbeitung der befestigten und unbefestigten Flächen. QKan enthält eine Funktion zur automatisierten 
Zuordnung dieser Flächen zu den Haltungen, die optional beim Export in das Simulationsprogramm mit Haltungflächen verschnitten werden. 
Dabei ist es sowohl möglich, die Flächenzuordnung interaktiv für kleine Teilgebiete als auch automatisch für große Kanalnetze durchzuführen. 

Langfristig soll QKan eine Anbindung an die in Deutschland weit verbreiteten hydrodynamischen Simulationsprogramme bekommen. Bereits realisiert sind: 

    - Kanal++/DYNA
    - HYSTEM-EXTRAN 7.8 und 7.9 (setzt zusätzliche Installationen voraus)
    - HYSTEM-EXTRAN 8.x
    - MIKE+

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
==========

Bei QKan handelt es sich um ein Open-Source-Projekt von `Jörg Höttges`_ .

.. _`Jörg Höttges`: https://www.fh-aachen.de/hoettges  

Es steht auf der Plattform GITHUB zum Download zur Verfügung (siehe Installation von QKan) und unterliegt der Open-Source-Lizenz GPL 3.0. 