Vorbereitung zur Flächenzuordnung
=================================

Eine Videoanleitung zur Vorbereitung zur Flächenaufteilung ist `hier <https://fh-aachen.sciebo.de/s/cu4krqOti0rf8Vq>`_ zu finden.

Nachdem die unbefestigten Flächen erstellt wurden, ist nun noch ein letzter Vorbereitungsschritt notwendig, bevor der Export in ein Simulationsprogramm (HYSTEM-EXTRAN, Mike++ o.ä.) durchgeführt werden kann.
Simulationsprogrammme erfordern, dass alle Flächen genau einer Haltung zugeordnet werden können.
Große Flächen (welche sich über mehrere Haltungen erstrecken), müssen hierfür aufgeteilt werden, damit die Teilstücke der entsprechenden Haltung zugeordnet werden können. Dies ist mit QKan nun automatisch möglich.
Hierfür zerteilt QKan die Flächenobjekte selber nicht, was den Vorteil hat, dass die Flächendaten im originalen Zustand erhalten bleiben und einzelne Objekte ohne Probleme ausgetauscht werden können. 
Die Aufteilung der Flächen geschieht erst beim Export in das Simulationsprogramm anhand der Haltungsflächen.

Bevor die automatische Flächenzuordnung jedoch durchgeführt werden kann, müssen die Daten noch entsprechend vorbereitet werden. 
Dafür sollten als erstes die Haltungen markiert werden, an welche kein Regenwasser angeschlossen ist, da sie bei der automatischen Flächenzuordnung ignoriert werden sollen. 
Diese Markierung geschieht über das Attribut "Entwässerungssysteme" der Haltungsdaten. 
Hierfür muss der Layer Haltungen → Haltungen nach Typ ausgewählt und im Bearbeitungsmodus sein. 
Es sollten nun alle Haltungen ausgewählt werden, an die kein Regenwasser angeschlossen ist (z.B. Haltungen die "nur" zum Auslauf führen; kurze Haltungen in Kreuzungsbereichen etc.). 
Anschließend können die gewählten Haltungen in der Attributtabelle über den Filter "Alle gewählten Objekte anzeigen" (siehe Bild unten) angezeigt werden. 
Das Entwässerungssystem muss nun für diese Haltungen von "Mischwasser" auf "MW nicht angeschlossen" geändert werden.
Dafür sollte von der Listen-Ansicht auf die Formular-Ansicht gewechselt werden (Schaltfäche rechts unten, siehe Bild unten). 

.. image:: ./QKan_Bilder/Flaechen_vorbereiten/liste_gewaehlte_haltungen.png 

Hierbei sollte darauf geachtet werden, dass eine der gewählten Haltungen ausgewählt ist (und nicht die erste Haltung der Liste). 
Dies kann sichergestellt werden, indem man über den Pfeil links unten, einen Schritt nach vorne geht (siehe Bild unten). 
Der Haltungsname oben im Formular sollte nun mit einem Eintrag aus der Liste (links, grau hinterlegt) übereinstimmen.
Anschließend kann das Entwässerungssystem über die Drop-Down-Liste von "Mischwasser" zu "MW nicht angeschlossen" geändert werden. 

.. image:: ./QKan_Bilder/Flaechen_vorbereiten/formular_haltung.png 

Nun kann wieder in die Listen-Ansicht gewechselt werden. 
Mit einem Rechtsklick auf die geänderte Zelle kann der Zellinhalt kopiert werden. 
Anschließend kann in der Drop-Down-Liste der Quick Field Calculation Bar die Spalte "Entwässerungssystem" gewählt werden. 
In das Formelfenster wird der kopierte Zellinhalt **mit Anführungsstrichen** eingefügt und über "Gewählte aktualisieren" werden alle ausgewählten Haltungen entsprechend angepasst. 

.. image:: ./QKan_Bilder/Flaechen_vorbereiten/liste_gewaehlte_aktualisieren.png 

Nun können die Änderungen gespeichert, der Bearbeitungsmodus ausgeschalten und die Auswahl aufgehoben werden. 

Als nächstes sollten die großen Flächen markiert werden, welche bei einem Export aufgeteilt werden müssen.  
In der Attributtabelle der Flächen ist hierfür eine extra Spalte "Aufteilen" vorgesehen. 
Diese sollte zunächst für alle Flächen das Attribut "false" enthalten. 
Ist dies nicht der Fall, kann dies einfach geändert werden, indem aus der Drop-Down-Liste der Quick Field Calculation Bar die Spalte "Aufteilen" gewählt wird und in das Formelfenster der Wert "0" eingegeben wird. 
Mit "Alle aktualisieren" wird die Änderung für alle Flächen übernommen. 
(In der Spalte sollte nun "false" ohne Klammern erscheinen.) 
 
Danach müssen alle Flächen ausgewählt werden, die mehreren Haltungen zugeordnet werden können (z.B. Straßen, große Gebäude oder große unbefestigte Flächen). 

Die Auswahl könnte beispielsweiße so aussehen: 

.. image:: ./QKan_Bilder/Flaechen_vorbereiten/auswahl_grosse_flaechen.png 

Jetzt kann in der Attributtabelle die Spalte "Aufteilen" für die gewählten Flächen angepasst werden. 
Dabei muss für die entsprechende Spalte der Wert "1" in die Calculation Bar eingegeben werden und mit "Gewählte aktualisieren" wird er Wert für die gewünschten Flächen übernommen. 
Die Flächen sollten nun den Wert "true" (ohne Klammern) in der Spalte "Aufteilen" enthalten. 
Anschließend können die Änderungen wieder gespeichert und die Auswahl aufgehoben werden. 

Als letzten Schritt müssen die Voronoiflächen erzeugt werden. 
Diese Flächen verfeinern die Haltungsflächen an den Stellen, wo eine Aufteilung der darin enthaltenen Flächen (z.B. Straßen) notwendig ist. 
Dies ist nun ganz einfach mit dem Werkzeug "Erzeuge Voronoiflächen zu Haltungen" möglich.

.. image:: ./QKan_Bilder/Flaechen_vorbereiten/Voronoiflaechen_tool.png

Nach einem Klick auf die Schaltfläche muss in dem sich öffnenden Fenster nur die richtige Entwässerungsart (Mischwasser) ausgewählt werden und kann anschließend mit "OK" bestätigt werden. 
Das Programm nimmt nun die Verfeinerung der Haltungsflächen selbstständig vor. 