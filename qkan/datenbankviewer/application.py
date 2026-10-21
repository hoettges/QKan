# qkan/datenbankviewer/application.py

import os

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import plugins

from ..netzuebersicht.db_backend import get_backend
from . import databaseviewer


class DatenbankviewerPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.dlg = None
        self.action = None
        self.conn = None
        self.cursor = None

        self.plugin_dir = os.path.dirname(__file__)
        self.icon_path = os.path.join(self.plugin_dir, "databaseviewer.png")

        print("[Datenbankviewer] __init__")
        print(f"[Datenbankviewer] plugin_dir = {self.plugin_dir}")
        print(f"[Datenbankviewer] icon_path = {self.icon_path}")

    def _get_qkan_instance(self):
        qkan_plugin = plugins.get("qkan")
        print(f"[Datenbankviewer] qkan plugin instance = {qkan_plugin}")
        return qkan_plugin

    def initGui(self):
        print("[Datenbankviewer] initGui() gestartet")
        try:
            qkan_instance = self._get_qkan_instance()
            if qkan_instance is None:
                raise RuntimeError("QKan-Hauptinstanz konnte nicht gefunden werden.")

            icon_path = self.icon_path if os.path.exists(self.icon_path) else ""
            print(f"[Datenbankviewer] verwende icon_path = {icon_path}")

            self.action = qkan_instance.add_action(
                icon_path=icon_path,
                text="Datenbankviewer",
                toolbar="QKan-Allgemein",
                callback=self.run,
                parent=self.iface.mainWindow(),
            )
            print(f"[Datenbankviewer] QAction registriert: {self.action}")

        except Exception as e:
            print(f"[Datenbankviewer] initGui ERROR: {e}")
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Datenbankviewer",
                f"Fehler beim Registrieren des Tools:\n{e}",
            )

    def unload(self):
        print("[Datenbankviewer] unload()")

        if self.dlg is not None:
            try:
                self.dlg.close()
            except Exception as e:
                print(f"[Datenbankviewer] dlg close warning: {e}")
            self.dlg = None

        try:
            if self.cursor is not None:
                self.cursor.close()
        except Exception as e:
            print(f"[Datenbankviewer] cursor close warning: {e}")
        self.cursor = None

        try:
            if self.conn is not None:
                self.conn.close()
        except Exception as e:
            print(f"[Datenbankviewer] conn close warning: {e}")
        self.conn = None

        self.action = None

    def run(self):
        print("[Datenbankviewer] run()")
        try:
            qkan_instance = self._get_qkan_instance()
            if qkan_instance is None:
                raise RuntimeError("QKan-Hauptinstanz konnte nicht gefunden werden.")

            dbsource = qkan_instance.get_active_dbsource()
            if not dbsource:
                raise RuntimeError(
                    "Es konnte keine aktive QKan-Datenbank ermittelt werden."
                )

            if self.dlg is not None:
                try:
                    print("[Datenbankviewer] vorhandenen Dialog nach vorne holen")
                    self.dlg.show()
                    self.dlg.raise_()
                    self.dlg.activateWindow()
                    return
                except Exception as e:
                    print(f"[Datenbankviewer] reuse warning: {e}")
                    self.dlg = None

            print("[Datenbankviewer] erzeuge Dialog neu")
            backend = get_backend("spatialite")

            self.conn, self.cursor, config = backend.load_native_connection_from_qkan(
                parent=self.iface.mainWindow(),
                dbsource=dbsource,
            )

            self.dlg = databaseviewer(
                parent=self.iface.mainWindow(),
                db_type="spatialite",
                spatialite_conn=self.conn,
            )

            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()
            print("[Datenbankviewer] Dialog angezeigt")

        except Exception as e:
            print(f"[Datenbankviewer] run ERROR: {e}")
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Datenbankviewer",
                f"Fehler beim Starten des Datenbankviewers:\n{e}",
            )
