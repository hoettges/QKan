Allgemeine Funktionen
---------------------

.. index:: Video: Flächenanbindung

Eine Anleitung zum Erstellen von Flächenanbindungen 

- Video_QKan_Flaechenverknuepfung_

.. _Video_QKan_Flaechenverknuepfung: https://fh-aachen.sciebo.de/s/Z0a5sIPUd0EWrTD



Übernahme von Kanaldaten aus Excel- oder ASCII-Tabellen
-------------------------------------------------------

.. index:: Video: Clipboard

Eine Anleitung zum Einfügen von Kanaldaten aus Tabellendaten

- Video_QKan_Clipboard_

.. _Video_QKan_Clipboard: https://fh-aachen.sciebo.de/s/J1MC92ShnQWzUtD


Anlegen eines neuen QKan-Projektes
----------------------------------

.. index:: Video: HYSTEM/EXTRAN-Projekt anlegen

Eine Videoanleitung zum Anlegen eines neuen QKan-Projektes aus einer bestehenden HYSTEM-EXTRAN-Datenbank und zum 
anschließenden Einbinden von Flächendaten finden Sie hier:

- Video_QKan_Kanaldatenflaechen_

.. _Video_QKan_Kanaldatenflaechen: https://fh-aachen.sciebo.de/s/PK3WwcNaaGJJQVi


.. index:: Video: Projektdatei übertragen


Übertragen einer anderen Projektdatei auf eine QKan-Datenbank
-------------------------------------------------------------

Eine Videoanleitung, wie für eine bestehende QKan-Kanaldatenbank eine Vorlage-Projektdatei geladen werden kann:

- Video_QKan_Projekt_laden_

.. _Video_QKan_Projekt_laden: https://fh-aachen.sciebo.de/s/JOjxXdF72eLrJsw


.. index:: Video: DXF-Datei als Zeichnungsrahmen

Einfügen eines Zeichnungsrahmens aus einer mit Autocad erstellten Vorlage
-------------------------------------------------------------------------

Eine Videoanleitung, wie ein mit AutoCAD erstellter Zeichnungsrahmen in ein QGIS-Layout eingefügt wird, 
finden Sie hier: 

- QGISZeichnungsrahmen_

.. _QGISZeichnungsrahmen: https://fh-aachen.sciebo.de/s/pJZayVce4VQMiFl


.. index:: Video: Bearbeiten eines DYNA-Projektes mit QKan

Übertragen eines Kanal++ Projektes nach QKan und zurück
-------------------------------------------------------------------------

Eine Videoanleitung, wie ein Kanal++ Projekt nach QKan übertragen werden kann, um es nach 
der Bearbeitung wieder zurückzuspielen und dort eine Berechnung auszuführen. 

- Video_Kanalpp_nach_QKan_1_
- Video_Kanalpp_nach_QKan_2_

.. _Video_Kanalpp_nach_QKan_1: https://youtu.be/UcAW8JGQZ1w
.. _Video_Kanalpp_nach_QKan_2: https://youtu.be/Lgl9eGOmMNw

Für diese Anleitung werden zwei SQL-Anweisungen benötigt. Diese können Sie hier kopieren:

::

    SELECT Name AS flnam, replace(ltrim(Name, '0 '), ' ', '0') AS haltnam, 
    Neigungskl AS neigkl, 'aus Kanal++ HoltorfV5' AS kommentar, 
    ShiftCoordinates(geometry, 4000000, 5000000) AS geom FROM mw

::

    SELECT Name AS elnam, replace(ltrim(Name, '0 '), ' ', '0') AS haltnam, 
    Einwohner AS ew,  
    ShiftCoordinates(Centroid(geometry), 4000000, 5000000) AS geom FROM mw
