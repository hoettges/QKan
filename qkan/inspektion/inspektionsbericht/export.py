"""PDF-Ausgabe für die aktive Datenquelle und die Terminauswahl des TV-Tools."""
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

from qgis.PyQt.QtCore import QStandardPaths, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QFileDialog,
                                 QVBoxLayout, QMessageBox)
from qgis.core import Qgis, QgsLayoutExporter

from .daten import Datenquelle
from .layout import _neues_layout, _Seiten, baue_bericht


@contextmanager
def berichtsquelle(aktiv):
    if aktiv.provider == "spatialite":
        from qgis.utils import spatialite_connect
        conn = spatialite_connect(Path(aktiv.sqlite_pfad).resolve().as_uri() + "?mode=ro", uri=True)
    elif aktiv.provider == "postgres":
        import psycopg2
        conn = psycopg2.connect(aktiv.verbindungs_uri)
    else:
        raise ValueError("Unbekannte QKan-Datenquelle.")
    try:
        if aktiv.provider == "postgres":
            from psycopg2 import sql
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(aktiv.schema)))
        yield Datenquelle(conn, aktiv.provider)
    finally:
        conn.close()


def bericht_schreiben(aktiv, art, name, termine, optionen, ziel):
    ziel = Path(ziel)
    with berichtsquelle(aktiv) as quelle, tempfile.TemporaryDirectory() as bilder:
        layout = _neues_layout("Inspektionsbericht")
        seiten = _Seiten(layout)
        for datum in termine:
            objekt = quelle.lade(art, name, datum)
            if optionen["fotos"] and quelle._hat("fotos"):
                sql = f"SELECT datei FROM fotos WHERE objekt = {quelle.ph} AND name = {quelle.ph}"
                params = [art, name]
                if datum:
                    sql += f" AND untersuchtag = {quelle.ph}"
                    params.append(datum)
                objekt.zusatz["fotos"] = quelle._abfrage(sql + " ORDER BY pk", params)
            baue_bericht(layout, seiten, objekt, optionen, bilder)
        with tempfile.TemporaryDirectory(dir=ziel.parent) as ausgabe:
            pdf = Path(ausgabe) / "Bericht.pdf"
            exporter = QgsLayoutExporter(layout)
            settings = QgsLayoutExporter.PdfExportSettings()
            settings.textRenderFormat = Qgis.TextRenderFormat.AlwaysText
            status = exporter.exportToPdf(str(pdf), settings)
            if status != QgsLayoutExporter.Success:
                raise RuntimeError(f"PDF-Export fehlgeschlagen (QGIS-Status {status}).")
            os.replace(pdf, ziel)


def bericht_dialog(parent, aktiv, art, name, termine, foto_root):
    from ..befahrungsmedien import _direkte_medientreffer

    def fotopfad(datei, ordner):
        treffer = _direkte_medientreffer("Bild", datei, ordner)
        return treffer[0].full_path if treffer else ""

    dialog = QDialog(parent)
    dialog.setWindowTitle(f"Inspektionsbericht – {art} {name}")
    layout = QVBoxLayout(dialog)
    felder = {}
    for key, titel in (("grafik", "Inspektionsgrafik"), ("liste", "Schadensliste"), ("fotos", "Fotos")):
        feld = QCheckBox(titel, dialog)
        feld.setChecked(True)
        layout.addWidget(feld)
        felder[key] = feld
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    if not dialog.exec():
        return
    dateiname = re.sub(r"[^\w.-]+", "_", name)
    downloads = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
    ordner = Path(downloads) if downloads else Path.home() / "Downloads"
    ordner.mkdir(parents=True, exist_ok=True)
    vorschlag = ordner / f"Inspektionsbericht_{dateiname}.pdf"
    ziel, _ = QFileDialog.getSaveFileName(parent, "Inspektionsbericht speichern",
                                          str(vorschlag), "PDF (*.pdf)")
    if not ziel:
        return
    optionen = {key: feld.isChecked() for key, feld in felder.items()}
    optionen.update(bildordner=foto_root, fotopfad=fotopfad)
    bericht_schreiben(aktiv, art, name, termine, optionen, ziel)
    if QMessageBox.question(parent, "Inspektionsbericht", "Gespeichertes PDF öffnen?") == QMessageBox.Yes:
        QDesktopServices.openUrl(QUrl.fromLocalFile(ziel))
