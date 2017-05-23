# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Laengsschnitt
                                 A QGIS plugin
 Plugin für einen animierten Laengsschnitt
                              -------------------
        begin                : 2017-02-16
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Leon Ochsenfeld
        email                : Ochsenfeld@fh-aachen.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources_laengs
import resources_gangl
from QKan_Navigation.navigation import Navigator
import plotter
# Import the code for the dialog
from application_dialog import LaengsschnittDialog
from qgis.core import *
import random
import os.path
import slider as s
from Enums import SliderMode, Type, LayerType
import copy
from ganglinie import Ganglinie


class Laengsschnitt:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.t = 2
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Laengsschnitt_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Laengsschnitt')
        self.toolbar = self.iface.addToolBar(u'Laengsschnitt')
        self.toolbar.setObjectName(u'Laengsschnitt')
        self.dlg = None
        self.result_db = ""
        self.spartialite = ""
        self.route = {}
        self.toolbar_widget = None
        self.id = 0
        self.maximizer = None
        self.auto_update = False
        self.animator = None
        self.speed_controller = None
        self.speed_label = None
        self.default_function = None
        self.ganglinie = Ganglinie(1)
        self.dlg2 = self.ganglinie.dialog
        self.navigator = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Laengsschnitt', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = LaengsschnittDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """
            Create the menu entries and toolbar icons inside the QGIS GUI.
            Längsschnit-Tool wird als Hauptanwendung angezeigt.
            Ganglinien-Tool wird als Dropdown des Längsschnitt angezeigt.
            Events werden mit Funktionen verknüpft.
        """
        icon_path_laengs = ':/plugins/QKan_Laengsschnitt/icon_laengs.png'
        icon_path_gangl = ':/plugins/QKan_Laengsschnitt/icon_gangl.png'

        action1 = self.add_action(
            icon_path_laengs,
            text='Längsschnitt-Tool'.decode("utf-8"),
            callback=self.run
        )
        action2 = self.add_action(
            icon_path_gangl,
            text='Ganglinien-Tool'.decode("utf-8"),
            callback=self.run_ganglinie
        )

        workspace = os.path.dirname(__file__)
        self.dlg.btn_forward.setText("")
        self.dlg.btn_forward.setIcon(QIcon(os.path.join(workspace, "forward.png")))
        self.dlg.btn_backward.setText("")
        self.dlg.btn_backward.setIcon(QIcon(os.path.join(workspace, "backward.png")))
        self.dlg.finished.connect(self.finished)
        self.dlg.btn_path.clicked.connect(self.select_db)
        self.dlg.checkbox_maximum.stateChanged.connect(self.switch_max_values)
        self.dlg.btn_forward.clicked.connect(self.step_forward)
        self.dlg.btn_backward.clicked.connect(self.step_backward)
        self.dlg.btn_ganglinie.clicked.connect(self.ganglinie.show)

    def finished(self):
        """
        Schließt den Ganglinien-Dialog, falls geöffnet
        """
        self.dlg2.close()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Laengsschnitt'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def step_forward(self):
        """
        Geht einen Datensatz nach rechts im Zeitstrahl, falls der Entpunkt nicht erreicht ist.
        Pausiert die Animation, falls diese läuft.
        """
        if self.speed_controller.mode != SliderMode.Pause:
            self.speed_controller.set_paused()
            self.animator.pause()
        value = self.dlg.slider.value()
        maximum = self.dlg.slider.maximum()
        if value < maximum:
            self.dlg.slider.setValue(value + 1)

    def step_backward(self):
        """
        Geht einen Datensatz nach links im Zeitstrahl, falls der Anfangspunkt nicht erreicht ist.
        Pausiert die Animation, falls diese läuft.
        """
        if self.speed_controller.mode != SliderMode.Pause:
            self.speed_controller.set_paused()
            self.animator.pause()
        value = self.dlg.slider.value()
        minimum = self.dlg.slider.minimum()
        if value > minimum:
            self.dlg.slider.setValue(value - 1)

    def switch_max_values(self, activate):
        """
        Macht die Maximal-Linie sichtbar bzw unsichtbar, abhängig vom Zustand der Checkbox.
        Plottet die Maximal-Linie falls nicht vorhanden.

        :param activate: Zustand der Checkbox, nach dem anklicken.
        :type activate: int
        """
        if self.maximizer is None or self.maximizer.id != self.id:
            self.maximizer = plotter.Maximizer(self.id, copy.deepcopy(self.route), self.result_db)
            self.maximizer.draw()
        if activate == 2:
            self.maximizer.show()
        else:
            self.maximizer.hide()

    @staticmethod
    def show_message_box(title, _string, _type):
        """
        Generiert eine Messagebox.
        Abhängig vom _type werden unterschiedliche Optionen in den Dialog eingebunden.
        Es wird False zurückgegeben, wenn der User auf "Abbrechen" drückt.


        :param title: Der Titel der MessageBox
        :type title: str
        :param _string: Der Inhalt der MessageBox
        :type _string: str
        :param _type: Welche Buttons generiert werden sollen. Bzw die Art der MessageBox.
        :type _type: Type
        :return: Ob der User auf "Abbrechen" gedrückt hat
        :rtype: bool
        """
        if _type == Type.Error:
            standard_buttons = QMessageBox.Ok
            default_button = QMessageBox.Ok
        else:
            standard_buttons = (QMessageBox.Cancel | QMessageBox.Open)
            default_button = QMessageBox.Open
        title = title.decode("utf-8")
        _string = _string.decode("utf-8")
        msg = QMessageBox()
        msg.setStandardButtons(standard_buttons)
        msg.setDefaultButton(default_button)
        msg.setText(_string)
        msg.setWindowTitle(title)
        if default_button == QMessageBox.Open:
            return msg.exec_() != QMessageBox.Open
        else:
            msg.exec_()

    def speed_control(self, value):
        """
        Übergibt der Animation die neue Geschwindigkeit.
        Ist die Geschwindigkeit 0, wird die Animation pausiert.

        :param value: Geänderte Geschwindigkeit.
        :type value: int
        :return: Returned wenn der Speed-Controller auf "Pause" steht
        """
        if self.speed_controller.mode == SliderMode.Pause:
            if self.speed_controller.last_mode == SliderMode.Forward:
                self.speed_label.setText("Geschwindigkeit: {}x".format(value))
                self.speed_label.setStyleSheet(
                    "QLabel {color:qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #050DFF, stop:1 #757AFF);}")
            else:
                self.speed_label.setText("Geschwindigkeit: -{}x".format(value))
                self.speed_label.setStyleSheet(
                    "QLabel {color:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #8f8f8f);}")
        elif self.speed_controller.mode == SliderMode.Forward:
            self.speed_label.setText("Geschwindigkeit: {}x".format(value))
            self.speed_label.setStyleSheet(
                "QLabel {color:qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #050DFF, stop:1 #757AFF);}")
        else:
            self.speed_label.setText("Geschwindigkeit: -{}x".format(value))
            self.speed_label.setStyleSheet(
                "QLabel {color:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #8f8f8f);}")

        if self.speed_controller.mode == SliderMode.Pause:
            self.animator.pause()
            return
        if value == 0:
            self.animator.pause()
        else:
            self.animator.play(value, self.speed_controller.mode)

    def slider_click(self, event):
        """

        :param event:
        :type event:
        """
        ctrl = event.modifiers() == Qt.ControlModifier
        if event.button() == Qt.RightButton:
            if ctrl:
                self.speed_controller.ctrl_click()
            else:
                self.speed_controller.set_paused()
                if self.speed_controller.mode == SliderMode.Pause:
                    self.animator.pause()
        else:
            if self.speed_controller.mode != SliderMode.Pause:
                self.speed_controller.set_paused()
                self.animator.pause()
            self.default_function(event)

    def select_db(self):
        self.animator.pause()
        filename = QFileDialog.getOpenFileName(self.dlg, "Wählen Sie eine Ergebnis-Datenbank".decode("utf-8"),
                                               filter="IDBF (*.idbf);; Alle Dateien (*.*)")
        if filename != "":
            self.result_db = filename
            self.dlg.label_dbname.setText(filename)
            self.run()

    @staticmethod
    def layer_to_type(layer):
        layer_source = layer.source()
        kvp = layer_source.split(" ")
        name = ""
        for kv in kvp:
            if kv.startswith("table"):
                name = kv.split("=")[1][1:-1]
        types = {
            "wehre": LayerType.Wehr,
            "haltungen": LayerType.Haltung,
            "schaechte": LayerType.Schacht,
            "pumpen": LayerType.Pumpe
        }
        try:
            return types[name]
        except KeyError:
            return -1

    def run(self):
        def init_application():
            if self.animator is not None:
                self.animator.pause()
            if self.speed_controller is not None:
                self.speed_controller.reset()
            if self.ganglinie is not None:
                self.ganglinie.dialog.close()
            self.dlg.close()
            self.id = random.random()
            while self.result_db == "":
                stop = self.show_message_box("Ergebnis-Datenbank",
                                             "Bitte wählen Sie eine Ergebnis-Datenbank aus!",
                                             Type.Selection)
                if stop:
                    return False
                filename = QFileDialog.getOpenFileName(self.dlg,
                                                       "Wählen Sie eine Simulations-Datenbank".decode("utf-8"),
                                                       filter="IDBF (*.idbf);; Alle Dateien (*.*)")
                self.result_db = filename
                self.dlg.label_dbname.setText(filename)
            while self.spartialite == "":
                stop = self.show_message_box("Datenbank",
                                             "Bitte wählen Sie eine Datenbank aus!",
                                             Type.Selection)
                if stop:
                    return False
                filename = QFileDialog.getOpenFileName(self.dlg,
                                                       "Wählen Sie eine Datenbank".decode("utf-8"),
                                                       filter="SQLITE (*.sqlite);; Alle Dateien (*.*)")
                self.spartialite = filename
            selected_layers = self.get_selected_layers()
            if len(selected_layers) == 0:
                self.show_message_box("Fehler", "Wählen Sie zunächst ein Layer!", Type.Error)
                return False
            layer_types = []
            for layer in selected_layers:
                layer_types.append(self.layer_to_type(layer))
            layer_types = list(set(layer_types))
            if len(layer_types) != 1:
                for _l in layer_types:
                    if _l not in [LayerType.Haltung, LayerType.Wehr, LayerType.Pumpe]:
                        self.show_message_box("Fehler", "Inkompatible Layer-Kombination!", Type.Error)
                        return False
                _layer_type = LayerType.Haltung
            else:
                _layer_type = layer_types[0]
            if _layer_type in [LayerType.Wehr, LayerType.Pumpe]:
                _layer_type = LayerType.Haltung
            if _layer_type not in [LayerType.Haltung, LayerType.Schacht]:
                self.show_message_box("Fehler", "Ausgewählter Layer wird nicht unterstützt!", Type.Error)
                return False
            if self.navigator is None or self.navigator.id != self.id:
                self.navigator = Navigator(self.spartialite, self.id)
            return selected_layers, _layer_type

        initialized = init_application()
        if initialized:
            layers, layer_type = initialized
        else:
            return
        speed_controller_initialized = self.speed_controller is None
        layout = QGridLayout()
        if speed_controller_initialized:
            self.speed_controller = s.Slider()
            self.speed_controller.setMaximumWidth(500)
            self.speed_controller.setMinimumWidth(300)
            layout.addWidget(self.speed_controller, 0, 0, 1, 1, Qt.AlignRight)
            self.speed_label = QLabel("Geschwindigkeit: 0x")
            self.speed_label.setStyleSheet(
                "QLabel {color:qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #050DFF, stop:1 #757AFF);}")
            self.speed_controller.setToolTip(
                "Links: Geschwindigkeit einstellen\nRechts: Pause/Start\nStrg+Rechts: Geschwindigkeit umkehren")
            layout.addWidget(self.speed_label, 1, 0, 1, 1, Qt.AlignCenter)
        self.dlg.widget.setLayout(layout)
        feature_count = 0
        for l in layers:
            feature_count += l.selectedFeatureCount()
        if feature_count < 2 and layer_type == LayerType.Schacht:
            self.show_message_box("Fehler",
                                  "Bitte wählen Sie mindestens einen Start- und Endpunkt Ihrer gewünschten Route!",
                                  Type.Error)
            return
        elif feature_count < 1:
            self.show_message_box("Fehler",
                                  "Bitte wählen Sie mindestens einen Start- und Endpunkt Ihrer gewünschten Route!",
                                  Type.Error)
            return
        # run application
        features = []
        for l in layers:
            features += [f[1] for f in l.selectedFeatures()]
        features = list(set(features))
        if feature_count == 2:
            if layer_type == LayerType.Haltung:
                res, _route, _reload = self.navigator.calculate_route_haltungen(features[0], features[1])
            else:
                res, _route, _reload = self.navigator.calculate_route_schaechte(features[0], features[1])
        else:
            if layer_type == LayerType.Haltung:
                res, _route, _reload = self.navigator.check_route_haltungen(features)
            else:
                res, _route, _reload = self.navigator.check_route_schaechte(features)
        if res:
            self.route = _route
        else:
            self.show_message_box("Fehler", _route, Type.Error)
            if _reload:
                self.result_db = ""
            return
        laengsschnitt = plotter.Laengsschnitt(copy.deepcopy(self.route))
        laengsschnitt.draw()
        plotter.set_ax_labels("m", "m")
        widget, _toolbar = laengsschnitt.get_widget()
        if self.toolbar_widget is not None:
            for i in reversed(range(self.dlg.verticalLayout.count())):
                self.dlg.verticalLayout.itemAt(i).widget().setParent(None)
        self.toolbar_widget = _toolbar
        self.dlg.verticalLayout.addWidget(self.toolbar_widget)
        self.dlg.stackedWidget.insertWidget(0, widget)
        self.dlg.stackedWidget.setCurrentIndex(0)
        # init methods

        self.dlg.checkbox_maximum.setChecked(True)
        self.switch_max_values(2)
        if self.animator is None or self.animator.id != self.id:
            self.animator = plotter.Animator(self.id, copy.deepcopy(self.route),
                                             self.result_db, self.dlg.slider, self.dlg.btn_forward,
                                             self.dlg.btn_backward)
        plotter.set_legend()
        if self.ganglinie.id != self.id:
            self.ganglinie.refresh(_id=self.id, haltungen=self.route.get("haltungen"),
                                   schaechte=self.route.get("schaechte"), dbname=self.result_db,
                                   laengsschnitt=laengsschnitt)
            self.ganglinie.draw_at(self.animator.timestamps[self.animator.last_index])
        self.animator.ganglinie = self.ganglinie
        self.dlg2.auto_update.hide()
        self.speed_controller.valueChanged.connect(self.speed_control)
        self.dlg.slider.valueChanged.connect(self.animator.go_step)
        self.dlg.slider.setToolTip(
            "Links: Zeitpunkt einstellen\nRechts: Pause/Start\nStrg+Rechts: Geschwindigkeit umkehren")
        if self.default_function is None:
            self.default_function = self.dlg.slider.mousePressEvent
        self.dlg.slider.mousePressEvent = lambda event: self.slider_click(event)
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # neustart
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
            # else:
            # beenden
        self.animator.pause()
        # self.ganglinie.reset()
        self.speed_controller.reset()

    def get_selected_layers(self):
        layers = self.iface.legendInterface().layers()
        selected_layers = []
        for l in layers:
            if l.selectedFeatureCount() > 0:
                selected_layers.append(l)
        return selected_layers

    def run_ganglinie(self):
        tmp = Ganglinie(self.t)
        self.t += 1

        def init_application():
            self.id = random.random()
            while self.result_db == "":
                stop = self.show_message_box("Ergebnis-Datenbank",
                                             "Bitte wählen Sie eine Ergebnis-Datenbank aus!",
                                             Type.Selection)
                if stop:
                    return False
                filename = QFileDialog.getOpenFileName(self.dlg,
                                                       "Wählen Sie eine Simulations-Datenbank".decode("utf-8"),
                                                       filter="IDBF (*.idbf);; Alle Dateien (*.*)")
                self.result_db = filename
            while self.spartialite == "":
                stop = self.show_message_box("Datenbank",
                                             "Bitte wählen Sie eine Datenbank aus!",
                                             Type.Selection)
                if stop:
                    return False
                filename = QFileDialog.getOpenFileName(self.dlg,
                                                       "Wählen Sie eine Datenbank".decode("utf-8"),
                                                       filter="SQLITE (*.sqlite);; Alle Dateien (*.*)")
                self.spartialite = filename
            selected_layers = self.get_selected_layers()
            if len(selected_layers) == 0:
                self.show_message_box("Fehler", "Wählen Sie zunächst ein Layer!", Type.Error)
                return False
            layer_types = []
            for layer in selected_layers:
                layer_types.append(self.layer_to_type(layer))
            layer_types = list(set(layer_types))
            if len(layer_types) != 1:
                _layer_type = LayerType.Haltung
            else:
                _layer_type = layer_types[0]
            if _layer_type in [LayerType.Wehr, LayerType.Pumpe]:
                _layer_type = LayerType.Haltung
            if _layer_type not in [LayerType.Haltung, LayerType.Schacht]:
                self.show_message_box("Fehler", "Ausgewählter Layer wird nicht unterstützt!", Type.Error)
                return False
            if self.navigator is None or self.navigator.id != self.id:
                self.navigator = Navigator(self.spartialite, self.id)
            return selected_layers, _layer_type

        def auto_update_changed(state):
            if state == 2:
                subscribe_auto_update()
                selection_changed([0])
            else:
                subscribe_auto_update(False)

        def subscribe_auto_update(subscribing=True):
            _layers = self.iface.legendInterface().layers()
            important_layers = []
            for _l in _layers:
                if self.layer_to_type(_l) != -1:
                    important_layers.append(_l)
            for layer in important_layers:
                if subscribing:
                    layer.selectionChanged.connect(selection_changed)
                else:
                    try:
                        layer.selectionChanged.disconnect(selection_changed)
                    except TypeError:
                        pass

        def selection_changed(selection):
            if len(selection) == 0:
                return
            _layers = self.get_selected_layers()
            _schaechte = []
            _haltungen = []
            for _l in _layers:
                _layer_type = self.layer_to_type(_l)
                if _layer_type == LayerType.Schacht:
                    _schaechte += [_f[1] for _f in _l.selectedFeatures()]
                elif _layer_type in [LayerType.Haltung, LayerType.Pumpe, LayerType.Wehr]:
                    _haltungen += [_f[1] for _f in _l.selectedFeatures()]
            _schaechte = list(set(self.navigator.get_schaechte(_schaechte).get("schaechte")))
            _haltungen = list(set(self.navigator.get_haltungen(_haltungen).get("haltungen")))
            _route = {"haltungen": _haltungen, "schaechte": _schaechte}
            tmp.refresh(_id=self.id, haltungen=_route.get("haltungen"),
                        schaechte=_route.get("schaechte"), dbname=self.result_db)
            tmp.show()

        initialized = init_application()
        if initialized:
            layers, layer_type = initialized
        else:
            return
        feature_count = 0
        for l in layers:
            feature_count += l.selectedFeatureCount()
        if feature_count < 1:
            self.show_message_box("Fehler",
                                  "Bitte wählen Sie mindestens ein Element aus aus!",
                                  Type.Error)
            return

        layers = self.get_selected_layers()
        schaechte = []
        haltungen = []
        for l in layers:
            layer_type = self.layer_to_type(l)
            if layer_type == LayerType.Schacht:
                schaechte += [f[1] for f in l.selectedFeatures()]
            elif layer_type in [LayerType.Haltung, LayerType.Pumpe, LayerType.Wehr]:
                haltungen += [f[1] for f in l.selectedFeatures()]
        schaechte = list(set(self.navigator.get_schaechte(schaechte).get("schaechte")))
        haltungen = list(set(self.navigator.get_haltungen(haltungen).get("haltungen")))
        route = {"haltungen": haltungen, "schaechte": schaechte}
        tmp.dialog.auto_update.show()
        subscribe_auto_update()
        tmp.dialog.auto_update.stateChanged.connect(auto_update_changed)
        tmp.refresh(_id=self.id, haltungen=route.get("haltungen"),
                    schaechte=route.get("schaechte"), dbname=self.result_db)
        tmp.draw()
        tmp.show()
        subscribe_auto_update(False)
