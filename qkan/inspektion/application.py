"""Registriert die Werkzeuge des Inspektionsmoduls in der QKan-Oberfläche."""

from pathlib import Path

from xml.etree import ElementTree

from qgis.core import QgsDefaultValue, QgsEditFormConfig, QgsEditorWidgetSetup, QgsField, QgsProject
from qgis.PyQt.QtCore import QVariant
from qgis.gui import QgisInterface

from qkan import QKan
from qkan.plugin import QKanPlugin

from .atlas_layout import AtlasLayoutBeimLesen
from .befahrungsmedien import BefahrungsmedienPlugin


class Inspektion(QKanPlugin):
    """Stellt die Aktionen des Inspektionsmoduls in QGIS bereit."""

    def __init__(self, iface: QgisInterface):
        """Initialisiert das Inspektionsmodul.

        :param iface: Aktive QGIS-Schnittstelle.
        """
        super().__init__(iface)
        self._atlas_layout = AtlasLayoutBeimLesen()
        self.medienplayer = BefahrungsmedienPlugin(iface)

    def initGui(self):
        """Registriert die Aktionen und Symbole in der QKan-Werkzeugleiste."""

        # Schacht erstellen
        icon_create_schacht = str(
            Path(__file__).parent / "res" / "icon_create_schacht.png"
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
        icon_create_haltung = str(
            Path(__file__).parent / "res" / "icon_create_haltung.png"
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
        icon_change_schacht = str(
            Path(__file__).parent / "res" / "icon_change_schacht.png"
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
        icon_change_haltung = str(
            Path(__file__).parent / "res" / "icon_change_haltung.png"
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
        icon_export = str(
            Path(__file__).parent / "res" / "dwa_m150_export.png"
        )

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
        icon_import = str(
            Path(__file__).parent / "res" / "dwa_m150_import.png"
        )

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

        self.iface.actionAddFeature().triggered.connect(self._prepare_haltung_form)
        self.iface.currentLayerChanged.connect(self._capture_layer_changed)
        projekt = QgsProject.instance()
        projekt.readMapLayer.connect(self._atlas_layout.layer_gelesen)
        projekt.readProject.connect(self._atlas_layout.projekt_gelesen)
        self.iface.projectRead.connect(self._prepare_project_forms)
        self._prepare_project_forms()
        self.iface.actionAddFeature().changed.connect(self._sync_haltung_button)
        self._sync_haltung_button()

    def _prepare_project_forms(self):
        for layer in QgsProject.instance().mapLayers().values():
            self._prepare_standard_form(layer)

    def _prepare_standard_form(self, layer):
        """Übernimmt das Namensfeld aus dem mitgelieferten Feldstil."""
        from .datenquelle import layerdaten

        forms = {
            "Schächte": ("schaechte", "schnam", "Schächte.qml"),
            "Haltungen": ("haltungen", "haltnam", "Haltungen.qml"),
            "HA-Leitungen": ("anschlussleitungen", "leitnam", "HA-Leitungen.qml"),
            "Anschlussleitungen": ("anschlussleitungen", "leitnam", "HA-Leitungen.qml"),
        }
        if layer is None or layer.name() not in forms or not layer.isValid():
            return
        table, field, style_file = forms[layer.name()]
        source = layerdaten(layer)
        if not source or source[0] != table:
            return
        index = layer.fields().indexFromName(field)
        if index < 0:
            return
        marker = "qkan/standardFormVersion"
        directory = Path(__file__).resolve().parents[1]
        editor = layer.editorWidgetSetup(index)
        if layer.customProperty(marker, "") != "3.4.23.5" or editor.type() == "QKanObjektname":
            style = ElementTree.parse(directory / "templates/qml" / style_file)
            widget = style.find(f"fieldConfiguration/field[@name='{field}']/editWidget")
            default = style.find(f"defaults/default[@field='{field}']")
            if editor.type() != widget.get("type"):
                layer.setEditorWidgetSetup(index, QgsEditorWidgetSetup(widget.get("type"), {}))
            expr = default.get("expression")
            if table == "haltungen":
                from qgis.core import QgsExpression
                from .datenquelle import layer_finden
                nodes = layer_finden(QgsProject.instance(), "schaechte", source[1])
                if nodes is not None:
                    expr = expr.replace("coalesce(layer_property('schaechte20161220162259105','id'), 'Schächte')",
                                        QgsExpression.quotedString(nodes.id()))
            definition = QgsDefaultValue(expr, default.get("applyOnUpdate") == "1")
            if layer.defaultValueDefinition(index) != definition:
                layer.setDefaultValueDefinition(index, definition)
            config = layer.editFormConfig()
            config.setUiForm(str(directory / "forms" / ("qkan_" + table + ".ui")))
            config.setLayout(QgsEditFormConfig.UiFileLayout)
            config.setSuppress(QgsEditFormConfig.SuppressOff)
            layer.setEditFormConfig(config)
            layer.setCustomProperty(marker, "3.4.23.5")

    def _sync_haltung_button(self):
        from .datenquelle import layerdaten

        capture = self.iface.actionAddFeature()
        layer = self.iface.activeLayer()
        active = False
        if capture.isEnabled() and capture.isChecked() and layer and layer.name() == "Haltungen":
            source = layerdaten(layer)
            active = bool(source and source[0] == "haltungen" and layer.isEditable())
        self.action_create_haltung.setChecked(active)

    def _capture_layer_changed(self, layer):
        self._sync_haltung_button()
        if self.iface.actionAddFeature().isChecked():
            self._prepare_haltung_form()

    def _prepare_haltung_form(self, checked=False):
        """Aktiviert das Erfassungsformular auch bei älteren Projekteinstellungen."""
        from .datenquelle import layerdaten, layer_finden

        layer = self.iface.activeLayer()
        self._prepare_standard_form(layer)
        source = layerdaten(layer)
        if source and source[0] == "anschlussleitungen" and layer.name() in ("HA-Leitungen", "Anschlussleitungen"):
            self._prepare_anschlussleitung(layer, source[1])
            return
        if not source or source[0] != "haltungen" or layer.name() != "Haltungen":
            return

        plugin_dir = Path(__file__).resolve().parents[1]
        config = layer.editFormConfig()
        path = str(plugin_dir / "forms" / "qkan_haltungen.ui")
        if config.uiForm() != path or config.suppress() != QgsEditFormConfig.SuppressOff or config.layout() != QgsEditFormConfig.UiFileLayout:
            config.setUiForm(path)
            config.setLayout(QgsEditFormConfig.UiFileLayout)
            config.setSuppress(QgsEditFormConfig.SuppressOff)
            layer.setEditFormConfig(config)

        manholes = layer_finden(QgsProject.instance(), "schaechte", source[1])
        if manholes is None:
            return

        # Die Ausdrücke bleiben im Layerstil. Projektbezogene Layer-IDs
        # werden erst beim Übernehmen der Konfiguration aufgelöst.
        if not hasattr(self, "_haltung_style"):
            self._haltung_style = ElementTree.parse(plugin_dir / "templates" / "qml" / "Haltungen.qml")
        style = self._haltung_style
        template_ref = "coalesce(layer_property('schaechte20161220162259105','id'), 'Schächte')"
        from qgis.core import QgsExpression
        layer_ref = QgsExpression.quotedString(manholes.id())
        for default in style.findall("defaults/default"):
            expression = default.get("expression")
            index = layer.fields().indexFromName(default.get("field"))
            if expression and index >= 0:
                definition = QgsDefaultValue(expression.replace(template_ref, layer_ref))
                if layer.defaultValueDefinition(index) != definition:
                    layer.setDefaultValueDefinition(index, definition)

        for field in style.findall("expressionfields/field"):
            name = field.get("name")
            if not name.startswith("schacht_"):
                continue
            expression = field.get("expression").replace(template_ref, layer_ref)
            index = layer.fields().indexFromName(name)
            if index < 0:
                layer.addExpressionField(expression, QgsField(name, QVariant.Double))
            elif layer.expressionField(index) and layer.expressionField(index) != expression:
                layer.updateExpressionField(index, expression)

        for name in ("schoben", "schunten"):
            index = layer.fields().indexFromName(name)
            if index < 0:
                continue
            setup = layer.editorWidgetSetup(index)
            options = setup.config()
            binding = dict(Layer=manholes.id(), LayerName=manholes.name(),
                           LayerSource=manholes.source(), LayerProviderName=manholes.providerType(),
                           Key="schnam", Value="schnam", AllowNull=True)
            if setup.type() != "ValueRelation" or any(options.get(k) != v for k, v in binding.items()):
                options.update(binding)
                layer.setEditorWidgetSetup(index, QgsEditorWidgetSetup("ValueRelation", options))

    def _prepare_anschlussleitung(self, layer, source):
        """Bindet Erfassungsvorgaben an die Layer der gewählten Datenquelle."""
        from qgis.core import QgsExpression
        from .datenquelle import layer_finden

        project = QgsProject.instance()
        manholes = layer_finden(project, "schaechte", source)
        pipes = layer_finden(project, "haltungen", source)
        directory = Path(__file__).resolve().parents[1]
        if not hasattr(self, "_anschluss_style"):
            self._anschluss_style = ElementTree.parse(directory / "templates/qml/HA-Leitungen.qml")
        for field in ("haltnam", "schoben", "schunten"):
            index = layer.fields().indexFromName(field)
            if index < 0:
                continue
            expr = self._anschluss_style.find(f"defaults/default[@field='{field}']").get("expression")
            for template_id, target in (("schaechte20161220162259105", manholes), ("haltungen20161016203756230", pipes)):
                expr = expr.replace(QgsExpression.quotedString(template_id),
                                    QgsExpression.quotedString(target.id()) if target else "NULL")
            default = QgsDefaultValue(expr)
            if layer.defaultValueDefinition(index) != default:
                layer.setDefaultValueDefinition(index, default)
            setup = layer.editorWidgetSetup(index)
            if field != "haltnam":
                if setup.type() != "TextEdit":
                    layer.setEditorWidgetSetup(index, QgsEditorWidgetSetup("TextEdit", {}))
            elif pipes:
                options = dict(setup.config(), Layer=pipes.id(), LayerName=pipes.name(),
                               LayerSource=pipes.source(), LayerProviderName=pipes.providerType(),
                               Key="haltnam", Value="haltnam", AllowNull=True)
                if setup.type() != "ValueRelation" or setup.config() != options:
                    layer.setEditorWidgetSetup(index, QgsEditorWidgetSetup("ValueRelation", options))
        config = layer.editFormConfig()
        path = str(directory / "forms/qkan_anschlussleitungen.ui")
        if config.uiForm() != path or config.layout() != QgsEditFormConfig.UiFileLayout or config.suppress() != QgsEditFormConfig.SuppressOff:
            config.setUiForm(path)
            config.setLayout(QgsEditFormConfig.UiFileLayout)
            config.setSuppress(QgsEditFormConfig.SuppressOff)
            layer.setEditFormConfig(config)

    def unload(self) -> None:
        """Bereinigt den integrierten Medienplayer beim Entladen."""
        self.iface.actionAddFeature().triggered.disconnect(self._prepare_haltung_form)
        self.iface.currentLayerChanged.disconnect(self._capture_layer_changed)
        projekt = QgsProject.instance()
        projekt.readMapLayer.disconnect(self._atlas_layout.layer_gelesen)
        projekt.readProject.disconnect(self._atlas_layout.projekt_gelesen)
        self.iface.projectRead.disconnect(self._prepare_project_forms)
        self.iface.actionAddFeature().changed.disconnect(self._sync_haltung_button)
        self.medienplayer.unload()
        super().unload()

    def run_create_schacht(self):
        """Startet das Werkzeug zum Erstellen eines Schachts."""
        from .create_schacht import create_schacht
        create_schacht()

    def run_create_haltung(self, checked=True):
        """Startet das Werkzeug zum Erstellen einer Haltung."""
        from .datenquelle import datenquelle_waehlen_direkt, layer_finden

        if not checked:
            self.iface.actionPan().trigger()
            self._sync_haltung_button()
            return

        # Erst nach erfolgreicher Aktivierung als gedrückt anzeigen.
        self.action_create_haltung.setChecked(False)
        project = QgsProject.instance()
        source = datenquelle_waehlen_direkt(
            project, ("haltungen", "schaechte"), self.iface.mainWindow(),
            "QKan – Haltung erstellen",
        )
        if source is None:
            return
        layer = layer_finden(project, "haltungen", source)
        if layer is None or layer_finden(project, "schaechte", source) is None:
            self.iface.messageBar().pushWarning("QKan", "Bitte Haltungen und Schächte laden.")
            return
        self.iface.setActiveLayer(layer)
        if not layer.isEditable() and not layer.startEditing():
            self.iface.messageBar().pushWarning("QKan", "Bearbeitungsmodus konnte nicht gestartet werden.")
            return
        capture = self.iface.actionAddFeature()
        if not capture.isEnabled():
            self.iface.messageBar().pushWarning("QKan", "Linienerfassung ist für diesen Layer deaktiviert.")
            return
        capture.trigger()
        self._sync_haltung_button()
        if self.action_create_haltung.isChecked():
            self.iface.digitizeToolBar().show()
            dock = self.iface.cadDockWidget()
            dock.show()
            enable = dock.enableAction()
            if enable and enable.isEnabled() and not enable.isChecked():
                enable.trigger()

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
