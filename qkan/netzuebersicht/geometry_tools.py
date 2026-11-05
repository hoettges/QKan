# qkan/netzuebersicht/geometry_tools.py
"""
Geometrie für neu angelegte Sonderbauwerke zeichnen und speichern.

Verwendet die Verbindung der Netzübersicht (parent.conn / parent.backend);
das SQL kommt aus sqlite.yml / postgres.yml (nz_sbw_geometrie_setzen).
"""
from qgis.core import QgsVectorLayer, QgsProject, QgsGeometry
from qgis.PyQt import QtWidgets


def _speichere_geometrie(parent, table_name, geomspalte, wkt):
    """
    Setzt die Geometrie des zuletzt angelegten Datensatzes der Tabelle.
    Rückgabe: True bei Erfolg.
    """
    conn = getattr(parent, "conn", None)
    backend = getattr(parent, "backend", None)
    if conn is None or backend is None:
        QtWidgets.QMessageBox.critical(parent, "Fehler", "Datenbankverbindung fehlt.")
        return False
    if table_name not in backend.SONDERBAUWERKE_TABELLEN:
        QtWidgets.QMessageBox.warning(parent, "Fehler", f"Unbekannte Tabelle {table_name}.")
        return False

    cur = conn.cursor()
    try:
        backend.execute(
            cur,
            "nz_sbw_geometrie_setzen",
            (wkt,),
            tabelle=backend.ident(table_name),
            geomspalte=backend.ident(geomspalte),
            id_spalte=backend.sbw_id_spalte(table_name),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()

def frage_nach_geometrie(parent, entry_id, table_name):
    """Fragt nach Polygon- und optional Punkt-Geometrie nach Anlegen eines Sonderbauwerks."""
    reply = QtWidgets.QMessageBox.question(
        parent,
        "Geometrie anlegen",
        "Möchten Sie für dieses Sonderbauwerk eine Geometrie anlegen?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )
    if reply == QtWidgets.QMessageBox.Yes:
        add_polygon_to_sonderbauwerk(parent, entry_id, table_name)

def add_polygon_to_sonderbauwerk(parent, entry_id, table_name):
    """Fügt einem Sonderbauwerk eine Polygon-Geometrie hinzu."""
    crs = "EPSG:25832"
    temp_layer = QgsVectorLayer(f"MultiPolygon?crs={crs}", "Sonderbauwerk Polygon", "memory")
    QgsProject.instance().addMapLayer(temp_layer)
    temp_layer.startEditing()

    QtWidgets.QMessageBox.information(
        parent, "Polygon zeichnen",
        "Bitte zeichnen Sie ein Polygon im Layer 'Sonderbauwerk Polygon' und speichern Sie ab."
    )

    uebernehmen_btn = QtWidgets.QPushButton("Geometrie übernehmen")
    uebernehmen_btn.show()

    def uebernehme_polygon():
        features = list(temp_layer.getFeatures())
        if not features:
            QtWidgets.QMessageBox.warning(parent, "Fehler", "Kein Polygon gefunden.")
            return
        
        geom = features[0].geometry()
        if geom is None or geom.isEmpty():
            QtWidgets.QMessageBox.warning(parent, "Fehler", "Keine gültige Geometrie.")
            return
        
        if not geom.isGeosValid():
            geom = geom.makeValid()

        wkt = geom.asWkt()
        
        try:
            if _speichere_geometrie(parent, table_name, "geom", wkt):
                QtWidgets.QMessageBox.information(parent, "Erfolg", "Polygon-Geometrie gespeichert.")
                # Nach Polygon → Punkt fragen
                frage_nach_punkt(parent, entry_id, table_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(parent, "Fehler", f"Geometrie speichern fehlgeschlagen:\n{str(e)}")
        
        # Cleanup
        QgsProject.instance().removeMapLayer(temp_layer.id())
        uebernehmen_btn.hide()

    uebernehmen_btn.clicked.connect(uebernehme_polygon)

def frage_nach_punkt(parent, entry_id, table_name):
    """Fragt nach optionaler Punkt-Geometrie."""
    reply = QtWidgets.QMessageBox.question(
        parent,
        "Punktgeometrie hinzufügen",
        "Möchten Sie diesem Sonderbauwerk auch eine Punktgeometrie (Position) hinzufügen?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )
    if reply == QtWidgets.QMessageBox.Yes:
        add_point_to_sonderbauwerk(parent, entry_id, table_name)

def add_point_to_sonderbauwerk(parent, entry_id, table_name):
    """Fügt einem Sonderbauwerk eine Punkt-Geometrie hinzu."""
    # Gleiche Logik wie bei Polygon, aber für geop
    crs = "EPSG:25832"
    temp_layer = QgsVectorLayer(f"Point?crs={crs}", "Sonderbauwerk Punkt", "memory")
    QgsProject.instance().addMapLayer(temp_layer)
    temp_layer.startEditing()

    QtWidgets.QMessageBox.information(
        parent, "Punkt zeichnen",
        "Bitte zeichnen Sie einen Punkt im Layer 'Sonderbauwerk Punkt' und speichern Sie ab."
    )

    uebernehmen_btn = QtWidgets.QPushButton("Position übernehmen")
    uebernehmen_btn.show()

    def uebernehme_punkt():
        features = list(temp_layer.getFeatures())
        if not features:
            QtWidgets.QMessageBox.warning(parent, "Fehler", "Kein Punkt gefunden.")
            return
        
        geom = features[0].geometry()
        if geom is None or geom.isEmpty():
            QtWidgets.QMessageBox.warning(parent, "Fehler", "Keine gültige Geometrie.")
            return

        wkt = geom.asWkt()
        
        try:
            if _speichere_geometrie(parent, table_name, "geop", wkt):
                QtWidgets.QMessageBox.information(parent, "Erfolg", "Punkt-Position gespeichert.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(parent, "Fehler", f"Punkt speichern fehlgeschlagen:\n{str(e)}")
        
        # Cleanup
        QgsProject.instance().removeMapLayer(temp_layer.id())
        uebernehmen_btn.hide()

    uebernehmen_btn.clicked.connect(uebernehme_punkt)