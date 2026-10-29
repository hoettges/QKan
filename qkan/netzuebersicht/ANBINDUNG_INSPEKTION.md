# Medieninspektor aus der Netzübersicht öffnen

`Show_Object_Untersuchung` in den Tabs Haltungen, Schächte und GAL ruft
`show_object_untersuchung()` aus `netzuebersicht/untersuchungs_viewer.py` auf.

1. Genau eine Zeile in der Netzübersicht auswählen.
2. Den zugehörigen QKan-Layer aktivieren und darin das Objekt selektieren.
3. Die QKan-Datenquelle zum Layer ermitteln (SpatiaLite/PostGIS).
4. `BefahrungsmedienDialog(iface, parent=self, viewer_only=True)` anzeigen.
5. Das Objekt über `dialog._objekt_auswaehlen(objektart, objektname, datenquelle)` laden.

Unterstützte Objektarten: `Haltung`, `Schacht`, `Anschlussleitung`.
Die Inspektionsgrafik ist Bestandteil des Medieninspektors; sie muss nicht
separat gestartet werden. Stammdaten, Schäden, Fotos, Videos und Panoramo
lädt der Medieninspektor selbst. Es wird keine Datenbankverbindung geteilt.

Die separate Panoramo-**Dateiprüfung** auf das Vorhandensein von `.ipf`-Dateien
bleibt als Sammelfunktion der Netzübersicht erhalten. Die Verzeichnisse werden
beim ersten Aufruf abgefragt und über QSettings benutzerspezifisch gespeichert.

Hinweis: Der alte Datenbankviewer wurde aus QKan entfernt.
