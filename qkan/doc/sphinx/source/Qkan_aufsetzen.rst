QKan - Step by Step Installation
================================

Willkommen beim Step by Step Tutorial zur Installation von QKan mit dem Betriebssystem Windows. QKan kann auch unter Linux verwendet werden, wo es teilweise
entwickelt wurde. Die nachfolgenden Schritte sind dort in ähnlicher Weise durchzuführen. 

Um QKan auf einem Computer neu einzurichten sind einige Arbeitsschritte notwendig, welche Ihnen im Folgenden vorgestellt werden:

Schritt 1: QGIS Installieren
----------------------------

QKan basiert auf dem Open-Source-Programm QGIS. Deshalb wird dieses als erstes benötigt.
Die aktuelle Version von QGIS finden Sie hier: QGIS_ oder falls dieser Link nicht funktioniert könne Sie manuell www.QGIS.org aufrufen. 

.. _QGIS: http://www.QGIS.org/de/site/forusers/download.html

Die aktuelle Version von QGIS (Stand Februar 2017) trägt die Versionsnummer 2.18.7. (Beachten Sie bitte den Hinweis zur Version unter Kap. 3.3.) Durch Klicken auf den 
"Jetzt herunterladen"-Button auf der Startseite werden Sie sofort 
zur Downloadseite weitergeleitet. Gehen Sie vorher sicher, dass Ihnen genügend freier Speicherplatz zur Verfügung steht, da die QGIS-Installation etwa 1,5 GB 
Speicherplatz einnehmen wird. Wählen Sie in Abhänigkeit von Ihrem Betriebssystem und Ihrer Betriebssystem-Version einen Downloadlink aus. In diesem Beispiel verwenden wir die 
unter dem Punkt "Für Windows herunterladen" zu findende Version "Eigenständige QGIS-Installation Version 2.18 (64bit)":

.. image:: .\QKan_Bilder\QGIS_herunterladen.png

Wählen Sie ein entsprechendes Verzeichnis zum Speichern der Installationsdatei und führen Sie diese anschließend aus. Bestätigen Sie die Installation, 
aktzeptieren das Lizenzabkommen und wählen anschießend das Verzeichnis, in dem QGIS installiert werden soll. Sie können auch einfach auf den Weiter-Button
klicken, um es im Standartverzeichnis "C:\\Programme\\QGIS 2.18" zu installieren. Als letzes wird QGIS Sie nach den zusätzlichen Komponenten, wie zum Beispiel
dem North Carolina Data Set fragen:

.. image:: .\QKan_Bilder\QGIS_komponenten.png

Für die Nutzung von QKan wird keine dieser zusätzlichen Komponenten benötigt. Sollte QGIS jedoch noch für andere Zwecke genutzt werden, können diese Komponenten
noch Verwendung finden. Beachten Sie, dass sich der benötgte Speicherplatz entsprechend erhöht, wenn Sie sich dazu entscheiden, die zusätzlichen Komponenten zu 
installieren. Klicken Sie anschließend auf "Installieren", um die Installation zu starten. Diese Installation kann einige Minuten in Anspruch nehmen.

| Wenn Sie alles richtig gemacht haben, sollten Sie folgende Nachricht erhalten:

.. image:: .\QKan_Bilder\QGIS_fertigstellen.png

Schritt 2: Firebird Installieren
--------------------------------

Vor der Installation der Plugins, die für QKan entwickelt wurden, muss zunächst die Datenbankanwendung Firebird installiert werden. Sie wird für den 
Zugriff auf die HYSTEM-EXTRAN-Dateien (\*.idbf) benötigt. Einen Link zum Download finden sie hier: Firebird_ oder Sie besuchen www.firebirdsql.org und 
wählen dort unter dem Reiter "Downloads" den Punkt Firebird 2.5 aus.

.. _firebird: http://www.firebirdsql.org/en/firebird-2-5-6/
 
Auf der Seite befinden sich änhlich wie bei der QGIS Installation wieder mehrere Downloadlinks. Benötigt wird der "Installer for Superclassic/Classic or 
Superserver". Wählen Sie auch hier wieder den für Ihr Betriebssystem und Version passenden Link aus. In diesem Beispiel verwenden wir den "Windows executable 
installer for full Superclassic/Classic or Superserver, recommended for first-time users" für Windows 64-bit: 

.. image:: .\QKan_Bilder\firebird_herunterladen.png

Über diesen Link werden Sie zu einem Downloadportal namens sourceforge.net weitergeleitet, wo nach wenigen Sekunden der Download starten sollte. Sollte es 
Probleme mit dem Download geben, beachten Sie bitte die Hinweise auf der Seite. Anschließend starten Sie die heruntergeladene Datei Setup.exe. Aktzeptieren Sie auch
hier wieder die Lizenzvereinbarungen. Wählen Sie ein Verzeichnis, um Firebird zu speichern oder verwenden Sie das Standartverzeichnis 
"C:\\Program Files\\Firebird\\Firebird_2_5". Gehen Sie nun sicher, dass Sie bei der Installation der Komponenten den Punkt "Super Server Binärdateien" ausgewählt
haben.

.. image:: .\QKan_Bilder\firebird_komponenten.png

Als nächstes wird Firebird einen Startmenü-Ordner anlegen. Dieser wird nicht unbedingt benötigt und kann durch die Checkbox "Keinen Order im Startmenü erstellen"
verhindert werden. Anschließend wird eine Abfrage über die zusätzlichen Aufgaben von Firebird erscheinen. Gehen Sie sicher, dass Ihre Auswahl wie folgt aussieht:

.. image:: .\QKan_Bilder\firebird_aufgaben_dienst.png

Bevor die Installation fertiggestellt werden kann, werden noch zwei Checkboxen erscheinen:

.. image:: .\QKan_Bilder\firebird_fertigstellen.png

Der Punkt "After installation - What Next?" bringt Sie zurück auf die Firebirdseite und bietet weitere Informationen zur Nutzung von Firebird. Die zur Nutzung 
von QKan benötigten Informationen bekommen Sie jedoch hier. Um zu testen ob der Firebirdserver auch richitg auf Ihrem System läuft, öffnen Sie den Taskmanager
und suchen unter dem Reiter Prozesse nach "fbserver.exe". 

Schritt 3: Zusätzliche Python-Module
------------------------------------

Nun müssen einige in QGIS enthaltene Module aktualisiert beziehungsweise ergänzt werden. Da Installationen nur mit Administrator-Rechten ausgeführt werden 
können, müssen Sie zunächst die "OSGeo4W Shell" als Administrator ausführen, um dort die weiteren Schritte vornehmen zu können. Falls Sie keinen 
Administrator-Zugang haben, wenden Sie sich an Ihren IT-Administrator, damit er die nachfolgenden Schritte ausführt. 

Schritt 3.1: Starten der "OSGeo4W Shell" mit Administrator-Rechten
------------------------------------------------------------------

Das Vorgehen unterscheidet sich etwas, je nachdem, welche Version von Windows Sie haben. 

Unter Windows 7 klicken Sie im Startmenü mit der rechten Maustaste auf "OSGeo4W Shell" und wählen "Als Administrator ausführen...". Unter Windows 10 wählen 
Sie stattdessen unter "Mehr" die Zeile "Am Speicherort öffnen" und Klicken wieder mit der rechten Maustaste auf die Datei "OSGeo4W Shell", wo Sie dann 
ebenfalls "Als Administrator ausführen..." wählen. 

.. warning:: Achten Sie unbedingt darauf, die "OSGeo4W Shell" als Administrator auszuführen, da sonst kein Zugriff möglich ist!

.. image:: .\QKan_Bilder\OSGeo4Wexe.png

Geöffnet sieht sie dann etwa so aus:

.. image:: .\QKan_Bilder\OSGeo4Wshell.png

Schritt 3.2: pyfirebirdsql
--------------------------

Dieses Modul wird von der Programmiersprache für die Kommunikation mit der Firebird-Datenbank benötigt. Einen Link dazu finden Sie hier: pyfirebirdsql_ oder 
besuchen Sie www.gihub.com/nakagami/pyfirebirdsql.

.. _pyfirebirdsql: https://github.com/nakagami/pyfirebirdsql    

Sie sollten sich nun auf der folgenden Seite befinden:
 
.. image:: .\QKan_Bilder\pyfirebird_herunterladen.png

Wenn Sie die Seite manuell öffnen, achten Sie unbedingt darauf, dass Sie das richtige Modul auswählen. Wenn Sie auf der weiter oben angegebenen Seite angekommen
sind, können Sie durch den "clone or download"-Button die Datei herunterladen. Klicken Sie erst auf "clone or download" und anschließend auf "Dowload ZIP". Dann
führen Sie den Download entsprechend ihrem Browser durch.    

.. image:: .\QKan_Bilder\pyfirebird_dwn.png

Sie erhalten nun eine .zip Datei mit dem Namen "pyfirebirdsql-master". Der darin enthaltene Ordner kann jetzt entpackt und anschließend in ein beliebiges
Verzeichnis verschoben werden. Um das Modul zu installieren, müssen Sie in der bereits geöffneten "OSGeo4W Shell" mit Hilfe der Befehle "cd" in das Verzeichnis 
wechseln, in das Sie im vorherigen Schritt die Installationsdateien entpackt hatten. In diesem Beispiel ist das: 
"C:\\Users\\Christian\\Desktop\\QKan\\install\\pyfirebirdsql-master". Anschließend geben Sie den Befehl "python setup.py install" ein.

.. image:: .\QKan_Bilder\OSGeo4Wshellcd.png

Schritt 3.3: pip und matplotlib
-------------------------------

.. note:: Dieses Kapitel ist nur Für QGIS-Versionen vor 2.18.6 relevant, die noch eine ältere Version der Bibliothek "matplotlib" enhalten. Bei den neueren Versionen ist eine Aktualsierung von "matplotlib" nicht notwendig, so dass sie alle Schritte in diesem Kapitel überspringen und mit Kap. 4 fortfahren können. 

Das Modul matplotlib wird für die grafische Darstellung benötigt. Zu seiner Aktualisierung müssen zusätzlich die Programme "pip" sowie "setuptools" aktualisiert werden. 

Geben Sie nacheinander im Fenster "OSGeo4W Shell" folgende Befehle ein:

python -m pip install --upgrade pip

python -m pip install -U pip setuptools

pip install -U matplotlib


Schritt 4: QKan Plugins für QGIS
--------------------------------

Nachdem QGIS und Firebird erfolgreich auf Ihrem System installiert wurden, können nun die QKan spezifischen Erweiterungen für QGIS geladen werden. 

Als nächstes benötigen Sie die QKan spezifischen Plugins für QGIS. Diese erhalten Sie auf dem github Verzeichnis zu QKan. Einen Link dazu
finden Sie hier: Höttges_ oder auf github.com/hoettges. Dort finden Sie zwei Repositories: "QKan" und "QKan_Doku". 

.. _Höttges: https://github.com/hoettges

.. image:: .\QKan_Bilder\github_hoettges.png

Wenn Sie auf "QKan" klicken, erscheint eine Liste von Verzeichnissen und Dateien. 

.. image:: .\QKan_Bilder\github_qkan.png

Falls Sie die aktuelle Entwicklungsversion laden möchten, wechseln Sie zunächst in den entsprechenden Zweig ("Branch"). Unter der Schaltfläche
"Branch" kann der gewünschte Zweig aufgewählt werden und anschließend mit der grünen Schaltfläche "Clone or download" heruntergeladen werden. 

In dem heruntergeladenen Zip-Archiv befindet sich im oberen Ordner ("QKan-master" oder "QKan-dev") ein Unterordner "QKan". Dieser muss in das 
Plugin-Verzeichnis von QGIS kopiert werden. Das Plugin-Verzeichnis unter dem Betriebssystem Windows ist üblicherweise 
"C:\\{Benutzer}\\Benutzername\\.qgis2\\python\\plugins". Dabei ist {Benutzer} der Name, unter dem Sie am Computer angemeldet sind. Sollte das 
Verzeichnis noch nicht existieren, müssen Sie es erstellen.

.. image:: .\QKan_Bilder\QKan_plugins.png

Anschließend öffnen Sie QGIS mit Hilfe der "QGIS Desktop 2.18.x with GRASS 7.x" Verknüpfung, welche sich im QGIS Ordner auf Ihrem Desktop befinden sollte. 
Wenn Sie QGIS gestartet haben, wählen Sie in der Hauptmenüleiste unter dem Menüpunkt "Erweiterungen" den Unterpunkt 
"Erweiterungen verwalten und installieren..." aus um folgendes Fenster zu öffnen:

.. image:: .\QKan_Bilder\Qgis_erweiterungen.png

Wählen Sie an der linken Seite den Reiter "Installiert" und setzen Sie den Haken vor dem Plugin "QKan". Nach dem Schließen dieses Fensters stehen 
in QGIS ein Werkzeugkasten "QKan" mit mehreren Icons sowie ein Hauptmenü "QKan" mit mehreren Untermenüs zur Verfügung.  

.. image:: .\QKan_Bilder\Qgis_menue.png

Herzlichen Glückwunsch Sie haben QKan erfolgreich auf Ihren Computer installiert!


.. warning:: Die ersten Anwender von QKan berichten davon, dass die Firebird-Datenbank in der hier verwendeten lizenzkostenfreien Version Probleme verursacht, wenn sich die Hystem-Extran-Datenbankdatei (Kanalnetz- oder Ergebnisdaten) in einem Netzwerk-Verzeichnis befindet. In diesem Fall hilft es, die Datei in ein lokales Verzeichnis (auf C:) zu verschieben, und später nach Beendigung der Arbeit wieder zurück zu verschieben. 

