Allgemeines
===========

QKan baut auf QGIS 3 auf und besteht zur Zeit aus 2 Plugins, die eine Palette von Funktionen zur Verarbeitung von Kanaldaten umfassen. 

Ein besonderer Schwerpunkt ist die Verarbeitung der befestigten und unbefestigten Flächen. QKan enthält eine Funktion zur automatisierten 
Zuordnung dieser Flächen zu den Haltungen, die optional beim Export in das Simulationsprogramm mit Haltungflächen verschnitten werden. 
Dabei ist es sowohl möglich, die Flächenzuordnung interaktiv für kleine Teilgebiete als auch automatisch für große Kanalnetze durchzuführen. 

Langfristig soll QKan eine Anbindung an die in Deutschland weit verbreiteten hydrodynamischen Simulationsprogramme bekommen. Bereits realisiert sind: 

    - Kanal++/DYNA
    - HYSTEM-EXTRAN 7.8 und 7.9 (setzt zusätzliche Installationen voraus)

Außerdem bestehen verschiedene Möglichkeiten des Datenim- und Exports:

    - Text (ASCII)
    - CSV
    - Excel
    - MS-Access-Datenbanken
    - (fast) beliebige OGC-konforme Geodaten

Wesentlicher Bestandteil von QKan ist eine Datenstruktur, die einen gemeinsamen Nenner der verschiedenen in Deutschland eingesetzten Programme darstellt. 
Sie ist die Basis für die QKan-Funktionen, ermöglicht aber gleichzeitig für den versierten QGIS-Anwender, die vielfältigen und umfassenden Funktionen von QGIS zu nutzen. 
Da QGIS eine Vielzahl an Datenim- und Exportfunktionen enthält, können beinahe beliebige Datenbestände mit QKan genutzt werden. 
Weiterhin kann mit Hilfe der Datenbanksprache SQL beinahe jede denkbare Aufgabe realisiert werden. 

Grundlagen
==========

Bei QKan handelt es sich um ein Open-Source-Projekt von `Jörg Höttges`_ .

.. _`Jörg Höttges`: https://www.fh-aachen.de/hoettges  

Es steht auf der Plattform GITHUB zum Download zur Verfügung (siehe Installation von QKan) und unterliegt der Open-Source-Lizenz GPL 3.0. 