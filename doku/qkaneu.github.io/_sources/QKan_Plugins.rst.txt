Erstellung von QKan-Plugins
===========================

Grundsätzlich entspricht die Erstellung von QKan-Plugins in Teilen der für QGIS empfohlenen Vorgehensweise. 
Wenn das Plugin als Bestandteil von QKan fungieren soll, sind einige Anpassungen und Ergänzungen notwendig. 
An dieser Stelle wird der Einfachheit halber der gesamte Workflow erläutert. 


Vorbereitung des Moduls
-----------------------

Am einfachsten ist es, den Vorlage-Ordner "template" in das QKan-Module-Verzeichnis .plugins/qkan zu kopieren und diesen dann entsprechend dem 
gewünschten Modulnamen umzubenennen. Das neueste Modul, das nach dem hier erläuterten Standard erstellt wurde, ist das Modul "sync", und ist 
deshalb ebenfalls als Vorlage empfehlendswert.


Erzeugen von Modul-Icons
------------------------

Ein Modul benötigt mindestens ein Icon, kann aber auch mehrere verwenden. Diese sollten im Dateityp `*`.png in der Größe von 32 x 32 oder 
64 x 64 Pixeln vorliegen, wobei beinahe beliebige Pixelgrößen verarbeitet werden. 
Alle Icons eines Moduls müssen mit dem Programm "pyrcc5.exe" in die Python-Datei resources.py umgewandelt werden. Dazu muss der Pfad zu 
den Icons in der Datei resource.qrc als relatvier Pfad bezogen auf das Modulverzeichnis eingetragen sein. Da für die Umwandlung 
einige Voreinstellungen (hierfür ist das Ausführen der Datei "o4w_env.bat" empfehlenswert) notwendig sind, empfiehlt sich die 
Verwendung der durch das ISCE erstellten Batch-Datei "make resource.bat".


Anpassungen in den Moduldateien (`*`.py)
----------------------------------------

Folgende Bezeichnungen müssen angepasst werden: 

    - "template" durch den gewählten Modulnamen
    - Icon-Bezeichnungen. Bei mehreren Icons müssen auch mehrere Aufrufe von QKan.instance.add_action() erfolgen
    - In der Methode unload(self) müssen alle Dialoge wieder geschlossen werden


Help-Schaltfläche anbinden
++++++++++++++++++++++++++

Die Schaltfläche im Formular ruft die Methode application_dialog.click_help() auf. Hier muss der Link auf die Dokumentation 
angepasst werden. Natürlich muss auch in der Dokumentation der Link, der hinter dem #-Zeichen steht (z. B. **name_des_links**), 
vorhanden sein. Meistens steht in der entsprechenden `*`.rst-Datei über der entsprechenden Überschrift ein 
Eintrag ".. _name_des_links:", wobei das führende Unterstrichzeichen nicht zum Namen des Links gehört.


Zentrale Plugin-Dateien
+++++++++++++++++++++++


Datei application.py
^^^^^^^^^^^^^^^^^^^^

Im Modul *application,py* wird eine Klasse mit einem Namen ähnlich dem Modulnamen definiert, die folgende Aufgaben erfüllt: 

- Die Funktion initGui stellt die nötigen Informationen zur Einbindung des Moduls in die Menüleiste von QKan zur Verfügung
- Öffnen des Formulars
- Aufruf des Modulcodes

Dabei stehen über die geerbte Klasse "QKanPlugin" folgende Funktionen zur Verfügung: 

- self.default_dir: Standardverzeichnis des QKan-Projektes

- self.iface: iface-Modul von QGIS. Beim Debuggen wird es durch ein internes Modul ersetzt, damit die 
  iface-Methodenaufrufe nicht ins Leere laufen

- self.log: Mit diesem Modul können Fehlermeldungen erzeugt werden, die je nach Aufruf in der internen
  Protokolldatei, im Meldungsfenster und/oder in der QGIS-Meldungsleiste erscheinen. Aktuell stehen zur Verfügung:
  - self.log.error_user('Anwenderfehler...')
  - self.log.error_code('Interner Programmierfehler')
  - self.log.error_data('Datenfehler')
  - self.log.notice('Information für den Anwender...')

Datei application_dialog.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In dieser Datei werden zunächst einmal die Bedienfunktionen des Formulars definiert und mit den entsprechenden Ereignissen
verbunden (connect). 

Weiterhin werden die Felder des Formulars mit Standardwerten besetzt und nach Bestätigung von [OK] durch den Anwender 
wieder gelesen und in die QKan-Konfiguration übernommen (QKN.congig.xxx.varieble):

    - _load_template_config(): Schreiben der in der QKan-Konfiguration gespeicherten Standardwerte in das Formular
    - _save_template_config(): Auslesen der im Formular vorgenommenen Einträge und Speichern in der QKan-Konfiguration


Ordner *res*
^^^^^^^^^^^^

Im Ordner *res* befinden sich die Formulardatei (`*`.ui) sowie die Icon-Datei. 
Die Icon-Datei muss für QGIS in Form der Python-Datei "resources.py" zur Verfügung gestellt werden. 
Dazu muss zunächst der Verweis auf die Icon-Datei in der Datei "resources.qrc" eingetragen und gegebenenfalls der Pfad 
in der Batch-Datei "make resources.bat" auf das richtige QGIS-Verzeichnis angepasst werden. Anschließend kann mit der 
Batch-Datei "make resources.bat" die Python-Datei erstellt werden. 


Einbindung in die QKan-Plugins
++++++++++++++++++++++++++++++

QKan-Plugins müssen zur Einbindung nur in der Datei "__init__.py" im Hauptverzeichnis eingetragen werden.
    #. in der PLUGIN_LIST
    #. in der Funktion "sort_actions(): Zu Beginn steht die Liste der Hauptmenüs und im Anschluss folgen die dazu gehörenden Menüeinträge


Vorlage-Plugin "Template"
+++++++++++++++++++++++++

Hier können Sie ein ZIP-Archiv mit der Grundstruktur eines QKan-Plugins 
downloaden: :download:`template_plugin.zip <_static/template_plugin.zip>`

Zunächst sollten Sie an allen Stellen den Text *template* durch den Namen Ihres Moduls ersetzen, wobei unbedingt 
auf Groß- und Kleinschreibung zu achten ist. 
