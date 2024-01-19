Allgemein
=========

Projektdatei anpassen
---------------------

Mit der Funktion |Tool_projekt_aktualisieren| :guilabel:`QKan-Prejekt aktualisieren` können Projekte, die noch auf einer älteren QKan-Version basieren, auf den aktuellsten Stand gebracht werden. 
Neben Änderungen an der Datenbankstruktur sind dabei meistens auch Anpassungen an den Projektlayern notwendig. Dazu sollte in dem Formular 
unter der Überschrift „QKan-Datenbank“ die Option „auf aktuelle Version anpassen“ (4) gewählt werden. Es wird automatisch sichergestellt, 
dass die Wertbeziehungen (Überschrift „Layer anpassen“) aktualisiert werden. Weiterhin ist es empfehlenswert, unter der gleichen 
Überschrift auch die Option „Formularanbindungen auf QKan-Standard setzen“ aktiviert ist.

.. _image_qkan_layersadapt:
.. image:: ./QKan_Bilder/qkan_layersadapt.png
.. |Tool_projekt_aktualisieren| image:: ./QKan_Bilder/Tool_projekt_aktualisieren.png
                             :width: 1.25 em

Auswahl der Vorlage
+++++++++++++++++++
„QKan-Standard verwenden“ sollte aktiviert werden, wenn keine eigenen Standards vorliegen. Sollen Einstellungen aus bereits existierenden 
Projektdateien übernommen werden, so kann die entsprechende Datei unter „Einstellungen aus Projektdatei übernehmen“ mit der Schaltfläche 
[…] rechts daneben ausgewählt werden.

Layer anpassen
++++++++++++++
In diesem Bereich kann eine Datenbank ausgewählt werden, an die das Projekt angebunden werden soll. Auch die übrigen Optionen sollten in 
der Regel aktiviert werden. 

.. 
    (?Jörg?): Erläuterung der Funktionen und Beispiel, wann diese nicht aktiviert werden sollten wenn möglich.
    - **Datenbankanbindung der Layer anpassen:**
    - **Projektsionssystem an Datenquelle anpassen:**
    - **Layer an QKan-Vorlage anpassen:**
    - **Formularanbindungen auf QKan-Standard setzen:**
    - **Projektmakros auf QKan-Standard setzen:**
    - **Zoom auf alle Layer:**

QKan-Layer
++++++++++
Unter dieser Überschrift kann ausgewählt werden, welche Layer bearbeitet werden sollen. 

.. 
    (?Jörg?): Beispiel, wann man die andere Option wählen soll
    - **ausgewählte anpasen:** Diese Option sollte nur gewählt werden wenn, ...(?Jörg?)
    - **alle anpassen:** In der Regel sollte diese Option gewählt werden
    - **Fehlende QKan-Geodaten-Layer hinzuladen:** (?Jörg?): Wann wird das benötigt?

.. 
    Auswertung Knotentypen
    ++++++++++++++++++++++
    (?Jörg?): Erklärung, was das ist und wofür dies gebraucht wird (sagt mir gar nichts) und ob es i.d.R. aktiviert od. nicht aktiviert sein soll
    - **Knotentypen in Tabelle eintragen:**
    
    
.. index:: Projektdatei übertragen

Projektdatei auf andere Datenbank übertragen
--------------------------------------------

Oft entstehen nach einiger Zeit komplexe Projektdateien, die besondere Layerdarstellungen enthalten und quasi „Firmenstandards“ darstellen. 
Solch eine Projektdatei kann mit der Funktion |Tool_projektdatei_uebertragen| :guilabel:`QKan-Projektdatei übertragen` folgendermaßen auf 
ein anderes Projekt übertragen werden:

.. _image_qkan_qgsAdapt:
.. image:: ./QKan_Bilder/qkan_qgsAdapt.png
.. |Tool_projektdatei_uebertragen| image:: ./QKan_Bilder/Tool_projektdatei_uebertragen.png
                             :width: 1.25 em

QKan-Datenbank
++++++++++++++
Hier wird die einzubindende QKan-Datenbank gewählt. 

.. 
    (?Jörg?): Wann sollte darunter die Option aktiviert werden?

Projektdatei als Vorlage
++++++++++++++++++++++++
Mit der Schaltfläche :guilabel:`...` kann die Projektdatei gewählt werden, die mit der vorhandenen Datenbank verknüpft werden soll. Ist keine entsprechende 
Projektdatei vorhanden, kann auch die QKan-Standardvorlage gewählt werden.

Neue Projektdatei
+++++++++++++++++
Über :guilabel:`...` kann der Pfad der neu zu erstellenden Projektdatei ausgewählt werden.