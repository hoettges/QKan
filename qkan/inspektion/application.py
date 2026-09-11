"""Registriert die Werkzeuge des Inspektionsmoduls in der QKan-Oberfläche."""

from qgis.gui import QgisInterface

from qkan import QKan
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
from .befahrungsmedien import BefahrungsmedienPlugin


class Inspektion(QKanPlugin):
    """Stellt die Aktionen des Inspektionsmoduls in QGIS bereit."""

    def __init__(self, iface: QgisInterface):
        """Initialisiert das Inspektionsmodul.

        :param iface: Aktive QGIS-Schnittstelle.
        """
        super().__init__(iface)
        self._tool_hooked = False
        self._running_auto = False
        self.medienplayer = BefahrungsmedienPlugin(iface)

    def initGui(self):
        """Registriert die Aktionen und Symbole in der QKan-Werkzeugleiste."""

        # Schacht erstellen
        icon_create_schacht = (
            ":/plugins/qkan/inspektion/res/icon_create_schacht.png"
        )

        self.action_create_schacht = QKan.instance.add_action(
            icon_create_schacht,
            text=self.tr("Schacht erstellen"),
            toolbar="QKan-Inspektion",
            callback=self.run_create_schacht,
            parent=self.iface.mainWindow(),
        )
        self.action_create_schacht.setCheckable(True)
        self.iface.action_create_schacht = self.action_create_schacht

        # Haltung erstellen
        icon_create_haltung = (
            ":/plugins/qkan/inspektion/res/icon_create_haltung.png"
        )

        self.action_create_haltung = QKan.instance.add_action(
            icon_create_haltung,
            text=self.tr("Haltung erstellen"),
            toolbar="QKan-Inspektion",
            callback=self.run_create_haltung,
            parent=self.iface.mainWindow(),
        )
        self.action_create_haltung.setCheckable(True)
        self.iface.action_create_haltung = self.action_create_haltung

        # Schacht ändern
        icon_change_schacht = (
            ":/plugins/qkan/inspektion/res/icon_change_schacht.png"
        )

        self.action_change_schacht = QKan.instance.add_action(
            icon_change_schacht,
            text=self.tr("Schacht verschieben"),
            toolbar="QKan-Inspektion",
            callback=self.run_change_schacht,
            parent=self.iface.mainWindow(),
        )
        self.action_change_schacht.setCheckable(True)
        self.iface.action_change_schacht = self.action_change_schacht

        # Haltung ändern
        icon_change_haltung = (
            ":/plugins/qkan/inspektion/res/icon_change_haltung.png"
        )

        self.action_change_haltung = QKan.instance.add_action(
            icon_change_haltung,
            text=self.tr("Haltung verschieben"),
            toolbar="QKan-Inspektion",
            callback=self.run_change_haltung,
            parent=self.iface.mainWindow(),
        )
        self.action_change_haltung.setCheckable(True)
        self.iface.action_change_haltung = self.action_change_haltung

        # M150 Export
        icon_export = ":/plugins/qkan/inspektion/res/dwa_m150_export.png"

        self.action_befahrung_export = QKan.instance.add_action(
            icon_export,
            text=self.tr("M150 Export"),
            toolbar="QKan-Inspektion",
            callback=self.run_m150_export,
            parent=self.iface.mainWindow(),
        )

        self.action_befahrung_export.setCheckable(False)
        self.iface.action_befahrung_export = self.action_befahrung_export

        # M150 Import
        icon_import = ":/plugins/qkan/inspektion/res/dwa_m150_import.png"

        self.action_befahrung_import = QKan.instance.add_action(
            icon_import,
            text=self.tr("M150 Import"),
            toolbar="QKan-Inspektion",
            callback=self.run_m150_import,
            parent=self.iface.mainWindow(),
        )

        self.action_befahrung_import.setCheckable(False)
        self.iface.action_befahrung_import = self.action_befahrung_import

        # TV-Befahrung / Medienplayer
        self.medienplayer.initGui()

        # Dieser Teil verhindert das Default-Verhalten beim Bearbeiten
        # des Layers "Haltungen". Stattdessen wird create_haltung
        # erzwungen: mehr Kontrolle über UI-Formular und Daten.
        """
        def on_tool_changed(new_tool, old_tool):

            if self._running_auto:
                return

            tool_name = new_tool.__class__.__name__

            if tool_name != "QgsMapToolDigitizeFeature":
                return

            layer = iface.activeLayer()
            if not layer or layer.name() not in ["Haltungen", "haltungen"]:
                return

            self._running_auto = True

            try:
                iface.actionPan().trigger()

                from .create_haltung import create_haltung
                create_haltung()

            finally:
                self._running_auto = False

        if not self._tool_hooked:
            iface.mapCanvas().mapToolSet.connect(on_tool_changed)
            self._tool_hooked = True
        """

    def unload(self) -> None:
        """Bereinigt den integrierten Medienplayer beim Entladen."""
        self.medienplayer.unload()
        super().unload()

    def run_create_schacht(self):
        """Startet das Werkzeug zum Erstellen eines Schachts."""
        from .create_schacht import create_schacht
        create_schacht()

    def run_create_haltung(self):
        """Startet das Werkzeug zum Erstellen einer Haltung."""
        from .create_haltung import create_haltung
        create_haltung()

    def run_change_schacht(self):
        """Startet das Werkzeug zum Verschieben eines Schachts."""
        from .move_schacht import change_schacht
        change_schacht()

    def run_change_haltung(self):
        """Startet das Werkzeug zum Verschieben einer Haltung."""
        from .move_haltung import change_haltung
        change_haltung()

    def run_m150_export(self):
        """Öffnet den Dialog für den M150-Export."""
        from .m150_export import run_m150_export
        run_m150_export(self.iface)

    def run_m150_import(self):
        """Öffnet den Dialog für den M150-Import."""
        from .m150_import import run_m150_import
        run_m150_import(self.iface)
