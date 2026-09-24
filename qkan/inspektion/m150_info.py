"""Gemeinsamer Info-Dialog für den M150-Import und -Export."""

from __future__ import annotations

import os

from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class M150InfoDialog(QDialog):
    """Zeigt die gemeinsame M150-Dokumentation an."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("DWA-M 150 – Informationen")
        self.resize(900, 700)

        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        layout.addWidget(self.text_browser)

        buttons = QDialogButtonBox(QDialogButtonBox.Close, parent=self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._dokumentation_laden()

    def _dokumentation_laden(self) -> None:
        """Lädt die HTML-Dokumentation aus dem res-Verzeichnis."""
        html_pfad = os.path.join(
            os.path.dirname(__file__),
            "res",
            "m150_dokumentation.html",
        )

        try:
            with open(html_pfad, "r", encoding="utf-8") as datei:
                self.text_browser.setHtml(datei.read())
        except OSError as err:
            self.text_browser.setPlainText(
                "Die M150-Dokumentation konnte nicht geladen werden."
            )
            QMessageBox.warning(
                self,
                "DWA-M 150 – Informationen",
                "Die Datei 'm150_dokumentation.html' konnte nicht "
                f"geladen werden.\n\n{err}",
            )


def zeige_m150_info(parent: QWidget | None = None) -> None:
    """Öffnet den gemeinsamen M150-Info-Dialog modal."""
    dialog = M150InfoDialog(parent)
    dialog.exec_()
