DWA-M 150 – Import, Export und TV-Befahrung in QKan
===================================================

Diese Hilfe beschreibt die Funktionen des QKan-Moduls **Inspektion** für Arbeitsabläufe rund um TV-Befahrungen sowie den Import und Export von Daten im XML-Austauschformat nach DWA-M 150.

.. contents:: Inhalt
   :depth: 2

.. _funktion:

1. Funktion und Zielsetzung
---------------------------

Das Inspektionsmodul unterstützt die Vorbereitung, Durchführung und Nachbearbeitung von TV-Befahrungen in QKan. Neben dem Datenaustausch über DWA-M-150-XML stehen einfache Werkzeuge zur Bearbeitung des Kanalnetzes direkt in QGIS zur Verfügung.

1.1 Werkzeuge für die Befahrung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Für die schnelle Bearbeitung des Netzes stehen vier Werkzeuge zur Verfügung: **Schacht erstellen**, **Haltung erstellen**, **Schacht verschieben** und **Haltung verschieben**. Sie dienen insbesondere dazu, fehlende oder falsch liegende Netzobjekte während der Vorbereitung oder Bearbeitung einer Befahrung direkt im Kartenfenster zu korrigieren.

1.2 M150-Export
~~~~~~~~~~~~~~~

Der Export ist auf die gezielte Übergabe ausgewählter Netzobjekte ausgelegt. Ausgangspunkt ist die Auswahl einer oder mehrerer Haltungen im Kartenfenster. Die Auswahl kann direkt über das Kartenwerkzeug erfolgen; die erkannten Objekte werden anschließend im Exportdialog getrennt als Haltungen, Schächte und Anschlussleitungen angezeigt.

#. Haltung bzw. Haltungen im Kartenfenster auswählen.
#. Optional verbundene Elemente einbeziehen. Dazu gehören die zugehörigen Schächte und – sofern aktiviert – Anschlussleitungen.
#. Auswahl im Dialog kontrollieren.
#. Exportziel und Dateinamen festlegen.
#. Export starten.

Der Export liest ausschließlich gespeicherte QKan-Daten. Offene Änderungen in exportrelevanten Layern müssen vor dem Export gespeichert werden. Der Export selbst verändert keine Netzobjekte.

1.3 M150-Import
~~~~~~~~~~~~~~~

Beim Import wird eine M150-XML-Datei ausgewählt und anschließend festgelegt, welche Daten übernommen werden sollen. Stamm- und Inspektionsdaten können getrennt verarbeitet werden.

#. M150-XML-Datei auswählen.
#. Import für **Inspektionsdaten** und/oder **Stammdaten** wählen.
#. Optional **Anschlüsse aus BCA erzeugen**, wenn fehlende Anschlussleitungen aus entsprechenden Befahrungsdaten ergänzt werden sollen.
#. Import starten.
#. Ergebnisse, Zuordnungen, Änderungen, Hinweise und Fehler im Logbuch kontrollieren.

Das Importprotokoll wird direkt im Dialog angezeigt. Zusätzlich wird derselbe Inhalt fortlaufend in der Datei ``M150_Import_Log.txt`` im Ordner des aktuell geöffneten QGIS-Projekts gespeichert.

.. _besonderheiten:

2. Datenmodell und Besonderheiten
---------------------------------

2.1 QKan und DWA-M 150
~~~~~~~~~~~~~~~~~~~~~~

QKan und DWA-M 150 besitzen unterschiedliche Datenmodelle. Deshalb können nicht alle Informationen direkt Feld für Feld übertragen werden. Das Modul verwendet für den Export ein QKan-spezifisches **Typ-Z-Profil**. Im XML wird dafür ``FD002 = Z`` verwendet.

Die wichtigsten M150-Blöcke werden wie folgt behandelt:

-  **HG** – Haltungen und Anschlussleitungen
-  **KG** – Schächte und Anschlussknoten
-  **HI / HZ** – Inspektionen und Zustände von Haltungen bzw. Anschlussleitungen
-  **KI / KZ** – Inspektionen und Zustände von Schächten
-  **GO / GP** – Geometrie und Geometriepunkte
-  **RT** – Referenztabellen

2.2 Anschlussleitungen und Stationierung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Die M150-Felder ``HG005`` bis ``HG012`` beschreiben Anschlussleitungen und ihre Beziehung zum übergeordneten Netzobjekt. Besonders wichtig sind ``HG007`` und ``HG008``: Die Station und ihre Richtung werden beim Import gemeinsam ausgewertet und in die QKan-``urstation`` überführt.

``HG009`` wird als Lage des Anschlusses am Rohrumfang in ``anschlussleitungen.lageanschluss`` übernommen.

2.3 Anschlussknoten und freie Leitungsenden
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

M150 unterscheidet Knoten über ``KG305`` bzw. Referenztabelle 116. QKan behandelt diese Werte beim Import und Export unterschiedlich:

-  **S** – echter Schacht; Zuordnung zu ``schaechte``
-  **F** – fiktiver Schacht; es wird kein reales QKan-Knotenobjekt angelegt
-  andere Knotenarten wie Revisionsschacht oder Straßenablauf – Zuordnung zu ``anschlussschaechte``

Beim Export wird am freien Ende einer Anschlussleitung zuerst nach einem realen Schacht, anschließend nach einem Anschlussknoten gesucht. Gibt es keinen passenden realen Knoten, wird für die M150-Netztopologie ein fiktiver Endpunkt ausgegeben, ohne dafür ein neues QKan-Bestandsobjekt anzulegen.

2.4 Referenztabellen
~~~~~~~~~~~~~~~~~~~~

Mitgelieferte RT-Blöcke einer Importdatei werden eingelesen und bei der Zuordnung von Referenzwerten berücksichtigt. Dadurch können auch projektspezifische oder vom DWA-Standard abweichende Referenzwerte verarbeitet werden.Bei der Auflösung werden vorhandene XML-Referenzen, QKan-/YAML-Zuordnungen und DWA-Standardwerte berücksichtigt.

2.5 Wiederholbarer Import
~~~~~~~~~~~~~~~~~~~~~~~~~

Ein erneuter Import derselben Daten soll keine unnötigen Dubletten erzeugen. Stammobjekte werden anhand ihrer Objektkennungen wiedergefunden. Gesamtinspektionen werden über Objekt und Untersuchungsdatum zugeordnet; Einzelschäden zusätzlich über ihre laufende Reihenfolge innerhalb der Inspektion.

Leere optionale XML-Felder löschen beim Aktualisieren keine bereits vorhandenen QKan-Werte.

2.6 Geometrie und Schadensdarstellung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Geometrien werden über ``GO``- und ``GP``-Blöcke übertragen. Für Haltungen und Leitungen wird die Fließrichtung bei der Geometrieausgabe berücksichtigt.

Die nach dem Import in QGIS dargestellten Schadens- und Beschriftungslinien sind QKan-spezifische Darstellungen. Sie dienen der übersichtlichen Visualisierung im Kartenfenster und sind keine zusätzliche Vorgabe des DWA-M 150.

2.7 Informationen nur im Protokoll
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nicht jede M150-Information besitzt ein entsprechendes QKan-Datenbankfeld. Einige Angaben werden deshalb bewusst nur im Importprotokoll ausgegeben. Welche Felder ausschließlich protokolliert werden, ist in der DWA-M-150-Feldliste mit dem Status „Log“ gekennzeichnet.

.. _feldliste:

3. Unterstützte DWA-M-150-Feldliste
-----------------------------------

Die folgende Liste zeigt die vom aktuellen QKan-Modul beim M150-Datenaustausch im Formattyp Z unterstützten Felder. Aufgeführt werden ausschließlich Felder, die im aktuellen QKan-Modul tatsächlich importiert, exportiert, für Berechnungen oder Zuordnungen verwendet oder im Importprotokoll ausgegeben werden.

.. note::

   **Statuslegende:** „Ja“ = wird fachlich übernommen oder ausgegeben; „Log“ = nur Importprotokoll; „Fallback“ = nur als Rückfall; „Zuordnung / Berechnung / Sonderlogik“ = steuert eine QKan-spezifische Verarbeitung; „Konstant“ = QKan schreibt einen festen Wert; „Leer“ = XML-Feld wird erzeugt, bleibt derzeit aber leer; „–“ = auf dieser Seite nicht verarbeitet.

FD – Formatdaten
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``FD001``
     - Versionsnummer der Schnittstelle
     - Log
     - Konstant: 04-2010
     - Beim Import im Protokoll ausgegeben; Export kennzeichnet die verwendete M150-Version.
   * - ``FD002``
     - Formattypbezeichnung
     - Log
     - Konstant: Z
     - Beim Import im Protokoll ausgegeben; QKan exportiert das projektspezifische Typ-Z-Profil.

HG – Haltungsgrunddaten
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``HG001``
     - Haltungsbezeichnung
     - Ja
     - Ja
     - Kennung der Haltung; bei Anschlussleitungen zusätzlich Bezug zur zugehörigen Haltung.
   * - ``HG002``
     - Alternative Haltungsbezeichnung
     - Fallback
     - –
     - Rückfall für die Objektzuordnung bei Inspektions-/BCA-Daten, wenn HG001 fehlt.
   * - ``HG003``
     - Knotenbezeichnung oben
     - Ja
     - Ja
     - QKan schoben; wird außerdem bei Inspektionsdaten und BCA-Erzeugung berücksichtigt.
   * - ``HG004``
     - Knotenbezeichnung unten
     - Ja
     - Ja
     - QKan schunten; wird bei Haltungsinspektionen mitgeführt.
   * - ``HG005``
     - Bezeichnung Endpunkt
     - Zuordnung
     - Ja
     - Bei Anschlussleitungen zur Endpunkt-/Anschlussknoten-Zuordnung; Export schreibt das reale oder fiktive Endobjekt.
   * - ``HG006``
     - Objekttyp bei Anschlussleitung
     - –
     - Ja
     - Export: H bei direktem Anschluss an eine Haltung, L bei Verzweigung von einer Anschlussleitung.
   * - ``HG007``
     - Stationierung der Anschlussleitung
     - Berechnung
     - Ja
     - Grundlage der QKan-urstation. Wird zusammen mit HG008 ausgewertet; Export verwendet urstation bzw. eine geometrisch berechnete Station.
   * - ``HG008``
     - Stationierungsrichtung der Anschlussleitung
     - Berechnung
     - Leer
     - I = in Fließrichtung, G = gegen Fließrichtung. Beim Import Umrechnung von HG007 in QKan-urstation; Exportfeld bleibt derzeit leer.
   * - ``HG009``
     - Positionierung bei Anschlussleitungen
     - Ja
     - Ja
     - QKan anschlussleitungen.lageanschluss; Export zweistellig als Uhrlage.
   * - ``HG010``
     - Typ Endpunkt
     - –
     - Ja
     - Exportiert die Knotenart des freien Endes nach RT116; fiktive/unbestimmte Enden werden nach der QKan-Regel behandelt.
   * - ``HG011``
     - Leitungsbezeichnung
     - Ja
     - Ja
     - QKan leitnam; zentrale Kennung einer Anschlussleitung.
   * - ``HG012``
     - Kind von
     - –
     - Ja
     - Exportiert die direkte Eltern-Anschlussleitung bei verzweigten Anschlussnetzen.
   * - ``HG301``
     - Kanalart
     - Ja
     - Ja
     - Import nach QKan abflussart für Haltungen. Bei Anschlussleitungen übernimmt der Export die Kanalart der zugeordneten Haltung.
   * - ``HG302``
     - Kanalnutzung
     - Ja
     - Ja
     - QKan entwart; Referenzauflösung über RT104/YAML/Standardwerte.
   * - ``HG303``
     - Baujahr
     - Ja
     - Ja
     - QKan baujahr.
   * - ``HG304``
     - Materialart
     - Ja
     - Ja
     - QKan material; Referenzauflösung über RT105/YAML/Standardwerte.
   * - ``HG305``
     - Profilart
     - Ja
     - Ja
     - QKan profilnam; Referenzauflösung über RT106/YAML/Standardwerte.
   * - ``HG306``
     - Profilbreite
     - Ja
     - Ja
     - QKan breite; zusätzlich als durchm verwendet, wenn das QKan-Ziel einen Durchmesser führt.
   * - ``HG307``
     - Profilhöhe
     - Ja
     - Ja
     - QKan hoehe.
   * - ``HG308``
     - Profilauskleidung
     - Ja
     - Ja
     - QKan profilauskleidung; Referenzauflösung über RT107/YAML/Standardwerte.
   * - ``HG309``
     - Profilauskleidungsmaterial
     - Ja
     - Ja
     - QKan innenmaterial; Materialauflösung über RT105.
   * - ``HG310``
     - Haltungslänge
     - Ja
     - Ja
     - QKan laenge; wird auch in untersuchten Haltungen/Anschlussleitungen mitgeführt.
   * - ``HG313``
     - Haltungsart
     - Zuordnung
     - Ja
     - Steuert die Objektart: A/C/Z werden als Haltung behandelt, B als Anschlussleitung. Export schreibt A bzw. B.
   * - ``HG999``
     - Bemerkung
     - Ja
     - –
     - Wird beim Stammimport als QKan-Kommentar übernommen.

GO / GP – Geometrie
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``GO001``
     - Geometrieobjektbezeichnung
     - Log-Kontext
     - Ja
     - Beim Import nur zur genaueren Protokollzuordnung verwendet; Export kennzeichnet Geometrieobjekte.
   * - ``GO002``
     - Geometrieobjektkennung
     - –
     - Ja
     - Exportiert die Objektkennung der Geometrie, z. B. Haltung/Geometrieobjekt.
   * - ``GO003``
     - Geometrieobjekttyp
     - –
     - Ja
     - Exportiert Pkt für Punkt- und L für Liniengeometrien.
   * - ``GP001``
     - Punktbezeichnung
     - Log-Kontext
     - Ja
     - Beim Import zur Protokollzuordnung; Export als Kennung des Geometriepunkts.
   * - ``GP002``
     - Angabe des Koordinatensystems
     - Log
     - Konstant: UTM
     - Import wird protokolliert; Export schreibt derzeit UTM.
   * - ``GP003``
     - Rechtswert
     - Fallback
     - –
     - Koordinaten-Rückfall beim Import, wenn GP005/GP006 fehlen.
   * - ``GP004``
     - Hochwert
     - Fallback
     - –
     - Koordinaten-Rückfall beim Import, wenn GP005/GP006 fehlen.
   * - ``GP005``
     - Ostkoordinate
     - Ja
     - Ja
     - Primäre X-Koordinate der importierten/exportierten Geometrie.
   * - ``GP006``
     - Nordkoordinate
     - Ja
     - Ja
     - Primäre Y-Koordinate der importierten/exportierten Geometrie.
   * - ``GP007``
     - Höhe
     - Ja
     - Ja
     - Sohl-/Punkthöhen. Bei Haltungen werden RA/RE-Rollen für die Zuordnung der Endhöhen verwendet.
   * - ``GP008``
     - Lagegenauigkeit
     - –
     - Konstant: G
     - Wird bei Anschlussleitungs-Geometriepunkten als G = geschätzt ausgegeben.
   * - ``GP009``
     - Höhengenauigkeit
     - –
     - Konstant: G
     - Wird bei Anschlussleitungs-Geometriepunkten als G = geschätzt ausgegeben.
   * - ``GP010``
     - Angabe des Höhensystems
     - Log
     - Konstant: mNN
     - Import wird protokolliert; Export schreibt derzeit mNN.
   * - ``GP999``
     - Bemerkung
     - Sonderlogik
     - Sonderlogik
     - QKan verwendet bei Haltungen die freien Marker RA/RE zur eindeutigen Zuordnung von Rohranfangs-/Rohrendhöhen.

HI – Haltungsinspektionsdaten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``HI001``
     - Auftraggeber
     - Log
     - –
     - Nur Ausgabe im Importprotokoll; keine QKan-Datenbankspeicherung.
   * - ``HI002``
     - Projektnummer
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``HI003``
     - Inspektionsnummer
     - Ja
     - –
     - QKan id der Gesamtinspektion.
   * - ``HI004``
     - Inspektionsgrund
     - Log
     - –
     - Nur Ausgabe im Importprotokoll; Referenzwert wird verständlich aufgelöst.
   * - ``HI005``
     - Kodiersystem
     - Ja
     - –
     - Wird als QKan bewertungsart übernommen; Referenzauflösung über RT202.
   * - ``HI006``
     - Eingesetztes Kamerasystem
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``HI101``
     - Inspektionsrichtung
     - Ja / Berechnung
     - –
     - I/G wird in die QKan-Untersuchungsrichtung übersetzt und für richtungsabhängige Schadensgeometrie verwendet.
   * - ``HI102``
     - Bezugspunkt Start
     - Ja
     - –
     - A/leer wird als Rohranfang übernommen; andere gültige Angaben werden auf Gerinnemittelpunkt zusammengeführt.
   * - ``HI103``
     - Inspektionsart
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``HI104``
     - Inspektionsdatum
     - Ja
     - –
     - QKan untersuchtag; zusammen mit dem Objektnamen zentraler Schlüssel für wiederholbare Importe.
   * - ``HI106``
     - Wetter
     - Ja
     - –
     - Wird in das vorhandene QKan-Feld wetter übernommen.
   * - ``HI107``
     - Reinigung
     - Ja
     - –
     - J/N wird als Ja/Nein in QKan übernommen; Speicherung in ``haltungen_untersucht.reinigung`` bzw. ``anschlussleitungen_untersucht.reinigung``.
   * - ``HI111``
     - Firma
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``HI112``
     - Inspekteur
     - Ja
     - –
     - QKan untersucher bei Haltungen und Anschlussleitungen.
   * - ``HI114``
     - Videospeichermedium
     - Log
     - –
     - Nur Ausgabe im Importprotokoll; keine DB-Speicherung.
   * - ``HI115``
     - Name des Speichermediums
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``HI116``
     - Dateiname digitales Video
     - Ja
     - –
     - Wird den Einzelschäden der Inspektion als film_dateiname zugeordnet.
   * - ``HI204``
     - Datum der Beurteilung
     - Ja
     - –
     - QKan bewertungstag.
   * - ``HI206``
     - Maximale Zustandsklasse Dichtheit
     - Ja
     - –
     - QKan max_ZD.
   * - ``HI207``
     - Maximale Zustandsklasse Standsicherheit
     - Ja
     - –
     - QKan max_ZS.
   * - ``HI208``
     - Maximale Zustandsklasse Betriebssicherheit
     - Ja
     - –
     - QKan max_ZB.
   * - ``HI999``
     - Bemerkung
     - Ja
     - –
     - QKan Kommentar der Gesamtinspektion.

HZ – Haltungszustandsdaten
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``HZ001``
     - Station
     - Ja / Berechnung
     - –
     - QKan station; außerdem bei BCA-Anschlusserzeugung und für die Schadensgeometrie verwendet.
   * - ``HZ002``
     - Kode
     - Ja / Sonderlogik
     - –
     - QKan kuerzel; kann zusätzlich den BCA-Code zur optionalen Erzeugung fehlender Anschlussleitungen enthalten.
   * - ``HZ003``
     - Quantifizierung 1
     - Ja
     - –
     - QKan quantnr1; bei BCA zusätzlich für die Erzeugungslogik berücksichtigt.
   * - ``HZ004``
     - Quantifizierung 2
     - Ja
     - –
     - QKan quantnr2.
   * - ``HZ005``
     - Streckenschaden
     - Ja / Berechnung
     - –
     - Wird in QKan in Streckenschaden-Kennzeichen und laufende Nummer aufgeteilt.
   * - ``HZ006``
     - Position von
     - Ja / Sonderlogik
     - –
     - QKan pos_von; bei BCA zusätzlich für die Anschlussrichtung/-lage berücksichtigt.
   * - ``HZ007``
     - Position nach
     - Ja
     - –
     - QKan pos_bis.
   * - ``HZ008``
     - Videozählerstand
     - Ja
     - –
     - QKan videozaehler und timecode.
   * - ``HZ009``
     - Bildname
     - Ja
     - –
     - QKan foto_dateiname.
   * - ``HZ010``
     - Langtext
     - Ja
     - –
     - QKan langtext.
   * - ``HZ012``
     - Auskleidung
     - Ja
     - –
     - 1/0 wird als Ja/Nein in ``untersuchdat_haltung.auskleidung`` bzw. ``untersuchdat_anschlussleitung.auskleidung`` übernommen.
   * - ``HZ014``
     - Charakterisierung 1
     - Ja
     - –
     - QKan charakt1.
   * - ``HZ015``
     - Charakterisierung 2
     - Ja
     - –
     - QKan charakt2.
   * - ``HZ206``
     - Zustandsklasse Dichtheit
     - Ja
     - –
     - QKan ZD.
   * - ``HZ207``
     - Zustandsklasse Standsicherheit
     - Ja
     - –
     - QKan ZS.
   * - ``HZ208``
     - Zustandsklasse Betriebssicherheit
     - Ja
     - –
     - QKan ZB.
   * - ``HZ999``
     - Bemerkung
     - Ja
     - –
     - QKan Kommentar des Einzelschadens.

KG – Knotengrunddaten
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``KG001``
     - Knotenbezeichnung
     - Ja / Zuordnung
     - Ja
     - QKan schnam; steuert außerdem die Zuordnung von Schacht- und Anschlussknoten.
   * - ``KG102``
     - Straßenname
     - Ja
     - Ja
     - Bei Anschlussknoten QKan strasse; Export bei realen Anschlussknoten.
   * - ``KG302``
     - Kanalnutzung
     - Ja
     - Ja
     - QKan entwart; Referenzauflösung über RT104.
   * - ``KG303``
     - Baujahr
     - Ja
     - Ja
     - Bei Anschlussknoten QKan baujahr; Export für reale Anschlussknoten.
   * - ``KG304``
     - Materialart
     - Ja
     - Ja
     - QKan material; Referenzauflösung über RT105.
   * - ``KG305``
     - Knotenart
     - Ja / Zuordnung
     - Ja
     - S wird als echter Schacht behandelt, F als fiktiver Knoten nicht angelegt, andere Typen als Anschlussknoten klassifiziert. Export nach RT116.
   * - ``KG308``
     - Schachtlänge
     - Ja
     - Ja
     - Primäre Quelle für QKan durchm; mm werden beim Import in m umgerechnet. Export schreibt den QKan-Durchmesser wieder in mm.
   * - ``KG309``
     - Schachtbreite
     - Fallback
     - Ja
     - Nur Rückfall für QKan durchm, wenn KG308 fehlt; Export schreibt denselben Durchmesser wie KG308.
   * - ``KG315``
     - Deckel verschraubt
     - Ja
     - Ja
     - Wird in QKan über das vorhandene Feld ``schaechte.druckdicht`` geführt; Import und Export verwenden 1/0.
   * - ``KG401``
     - Funktionszustand
     - Ja
     - Ja
     - QKan simstatus; Exportauflösung über RT109.
   * - ``KG999``
     - Bemerkung
     - Ja
     - Ja
     - QKan kommentar.

KI – Knoteninspektionsdaten
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``KI002``
     - Projektnummer
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``KI003``
     - Inspektionsnummer
     - Ja
     - –
     - QKan id der Schachtinspektion.
   * - ``KI004``
     - Inspektionsgrund
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``KI005``
     - Kodiersystem
     - Ja
     - –
     - QKan bewertungsart; Referenzauflösung über RT202.
   * - ``KI006``
     - Eingesetztes Kamerasystem
     - Log
     - –
     - Nur Ausgabe im Importprotokoll.
   * - ``KI104``
     - Inspektionsdatum
     - Ja
     - –
     - QKan untersuchtag; zusammen mit dem Schachtnamen zentraler Importschlüssel.
   * - ``KI106``
     - Wetter
     - Ja
     - –
     - Wird in das vorhandene QKan-Feld wetter übernommen.
   * - ``KI107``
     - Reinigung
     - Ja
     - –
     - J/N wird als Ja/Nein in ``schaechte_untersucht.reinigung`` übernommen.
   * - ``KI111``
     - Firma
     - Ja
     - –
     - Primäre Quelle für QKan untersucher bei Schachtinspektionen.
   * - ``KI112``
     - Inspekteur
     - Fallback
     - –
     - Rückfall für QKan untersucher, wenn KI111 leer ist.
   * - ``KI116``
     - Dateiname des digitalen Videos
     - Ja
     - –
     - Wird den KZ-Einzelschäden als film_dateiname zugeordnet.
   * - ``KI204``
     - Datum der Beurteilung
     - Ja
     - –
     - QKan bewertungstag.
   * - ``KI206``
     - Maximale Zustandsklasse Dichtheit
     - Ja
     - –
     - QKan max_ZD.
   * - ``KI207``
     - Maximale Zustandsklasse Standsicherheit
     - Ja
     - –
     - QKan max_ZS.
   * - ``KI208``
     - Maximale Zustandsklasse Betriebssicherheit
     - Ja
     - –
     - QKan max_ZB.
   * - ``KI999``
     - Bemerkung
     - Ja
     - –
     - QKan Kommentar der Schachtinspektion.

KZ – Knotenzustandsdaten
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``KZ001``
     - Tiefe
     - Ja
     - –
     - QKan vertikale_lage.
   * - ``KZ002``
     - Kode
     - Ja
     - –
     - QKan kuerzel.
   * - ``KZ003``
     - Quantifizierung 1
     - Ja
     - –
     - QKan quantnr1.
   * - ``KZ004``
     - Quantifizierung 2
     - Ja
     - –
     - QKan quantnr2.
   * - ``KZ005``
     - Streckenschaden
     - Ja
     - –
     - QKan streckenschaden.
   * - ``KZ006``
     - Position Beginn
     - Ja
     - –
     - QKan pos_von.
   * - ``KZ007``
     - Position Ende
     - Ja
     - –
     - QKan pos_bis.
   * - ``KZ008``
     - Videozählerstand
     - Ja
     - –
     - QKan videozaehler und timecode.
   * - ``KZ009``
     - Bildname
     - Ja
     - –
     - QKan foto_dateiname.
   * - ``KZ010``
     - Langtext des Zustandes
     - Ja
     - –
     - QKan langtext.
   * - ``KZ011``
     - Verbindung
     - Ja
     - –
     - A/leer wird als Ja/Nein in ``untersuchdat_schacht.verbindung`` übernommen.
   * - ``KZ013``
     - Schachtbereich
     - Ja
     - –
     - QKan bereich.
   * - ``KZ014``
     - Charakterisierung 1
     - Ja
     - –
     - QKan charakt1.
   * - ``KZ015``
     - Charakterisierung 2
     - Ja
     - –
     - QKan charakt2.
   * - ``KZ206``
     - Zustandsklasse Dichtheit
     - Ja
     - –
     - QKan ZD.
   * - ``KZ207``
     - Zustandsklasse Standsicherheit
     - Ja
     - –
     - QKan ZS.
   * - ``KZ208``
     - Zustandsklasse Betriebssicherheit
     - Ja
     - –
     - QKan ZB.
   * - ``KZ999``
     - Bemerkung
     - Ja
     - –
     - QKan Kommentar des Einzelschadens.

RT – Referenztabellen
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 23 13 13 41

   * - Feld
     - DWA-Bezeichnung
     - Import
     - Export
     - Verwendung / Besonderheit in QKan
   * - ``RT001``
     - Tabelle
     - Ja
     - –
     - Kennung der mitgelieferten Referenztabelle. XML-Referenzen werden vor QKan-/Standardzuordnungen berücksichtigt.
   * - ``RT002``
     - Schlüssel
     - Ja
     - –
     - Schlüssel des Referenzeintrags.
   * - ``RT004``
     - Langtext
     - Ja
     - –
     - Langtext des Referenzeintrags; wird zur Auflösung projektspezifischer Referenzwerte verwendet.
