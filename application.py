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
import navigation
import plotter
# Import the code for the dialog
from application_dialog import LaengsschnittDialog
from qgis.core import *
import random
import os.path
import slider as s
from Enums import SliderMode, Type
import copy
from ganglinie import Ganglinie


class Laengsschnitt:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
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

        self.dbname = ""
        self.route = {}
        self.toolbar_widget = None
        self.id = 0
        self.maximizer = None
        self.animator = None
        self.speed_controller = None
        self.speed_label = None
        self.default_function = None
        self.ganglinie = Ganglinie()
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
        self.dlg.btn_path.clicked.connect(self.sel_dbPath)
        self.dlg.checkbox_maximum.stateChanged.connect(self.switch_max_values)
        self.dlg.btn_forward.clicked.connect(self.step_forward)
        self.dlg.btn_backward.clicked.connect(self.step_backward)
        self.dlg.btn_ganglinie.clicked.connect(self.ganglinie.show)

    def finished(self, res):
        """
        Schließt den Ganglinien-Dialog, falls geöffnet

        :param res: Return-Code beim schließen des Dialogs
        :type res: int
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
            self.maximizer = plotter.Maximizer(self.id, copy.deepcopy(self.route), self.dbname)
            self.maximizer.draw()
        if activate == 2:
            self.maximizer.show()
        else:
            self.maximizer.hide()

    def showMessageBox(self, title, string, _type):
        """
        Generiert eine Messagebox.
        Abhängig vom _type werden unterschiedliche Optionen in den Dialog eingebunden.
        Es wird False zurückgegeben, wenn der User auf "Abbrechen" drückt.


        :param title: Der Titel der MessageBox
        :type title: str
        :param string: Der Inhalt der MessageBox
        :type string: str
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
        string = string.decode("utf-8")
        msg = QMessageBox()
        msg.setStandardButtons(standard_buttons)
        msg.setDefaultButton(default_button)
        msg.setText(string)
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

    def sel_dbPath(self):
        self.animator.pause()
        filename = QFileDialog.getOpenFileName(self.dlg, "Wählen Sie eine Simulations-Datenbank".decode("utf-8"),
                                               filter="Datenbanken (*.idbf);; Alle Dateien (*.*)")
        if filename != "":
            self.dbname = filename
            self.dlg.label_dbname.setText(filename)
            self.run()

    def init_application(self):
        if self.animator is not None:
            self.animator.pause()
        if self.speed_controller is not None:
            self.speed_controller.reset()
        if self.ganglinie is not None:
            self.ganglinie.dialog.close()
        self.dlg.close()
        self.id = random.random()
        while self.dbname == "":
            stop = self.showMessageBox("Simulations-Datenbank", "Bitte wählen Sie eine Simulations-Datenbank aus!",
                                       Type.Selection)
            if stop:
                return False
            filename = QFileDialog.getOpenFileName(self.dlg, "Wählen Sie eine Simulations-Datenbank".decode("utf-8"),
                                                   filter="Datenbanken (*.idbf);; Alle Dateien (*.*)")
            self.dbname = filename
            self.dlg.label_dbname.setText(filename)

        layer = self.iface.activeLayer()
        if layer is None:
            self.showMessageBox("Fehler", "Wählen Sie zunächst ein Layer!", Type.Error)
            return False
        layer_source = layer.source()
        kvp = layer_source.split(" ")
        layer_name = ""
        for kv in kvp:
            if kv.startswith("table"):
                layer_name = kv.split("=")[1][1:-1]
        if layer_name not in ["haltungen", "schaechte"]:
            self.showMessageBox("Fehler", "Ausgewählter Layer wird nicht unterstützt!", Type.Error)
            return False
        if self.navigator is None or self.navigator.id != self.id:
            self.navigator = navigation.Navigator(self.dbname, self.id)
        return layer, layer_name

    def run(self):
        initialized = self.init_application()
        if initialized:
            layer, layer_name = initialized
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

        featureCount = layer.selectedFeatureCount()
        if featureCount < 2 and layer_name == "schaechte":
            self.showMessageBox("Fehler",
                                "Bitte wählen Sie mindestens einen Start- und Endpunkt Ihrer gewünschten Route!",
                                Type.Error)
            return
        elif featureCount < 1:
            self.showMessageBox("Fehler",
                                "Bitte wählen Sie mindestens einen Start- und Endpunkt Ihrer gewünschten Route!",
                                Type.Error)
            return
        # run application
        if featureCount == 2:
            features = layer.selectedFeatures()
            if layer_name == "haltungen":
                if featureCount == 1:
                    res, _route, reload = self.navigator.calculate_route_haltungen(features[0][1], None)
                else:
                    res, _route, reload = self.navigator.calculate_route_haltungen(features[0][1], features[1][1])
            else:
                res, _route, reload = self.navigator.calculate_route_schaechte(features[0][1], features[1][1])
        else:
            if layer_name == "haltungen":
                res, _route, reload = self.navigator.check_route_haltungen([f[1] for f in layer.selectedFeatures()])
            else:
                res, _route, reload = self.navigator.check_route_schaechte([f[1] for f in layer.selectedFeatures()])
        if res:
            self.route = _route
        else:
            self.showMessageBox("Fehler", _route, Type.Error)
            if reload:
                self.dbname = ""
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
        self.switch_max_values(2)
        if self.animator is None or self.animator.id != self.id:
            self.animator = plotter.Animator(self.id, copy.deepcopy(self.route),
                                             self.dbname, self.dlg.slider, self.dlg.btn_forward, self.dlg.btn_backward)
        plotter.set_legend()
        if self.ganglinie.id != self.id:
            self.ganglinie.refresh(_id=self.id, haltungen=self.route.get("haltungen"),
                                   schaechte=self.route.get("schaechte"), dbname=self.dbname,
                                   laengsschnitt=laengsschnitt)
            self.ganglinie.draw_at(self.animator.timestamps[self.animator.last_index])
        self.animator.ganglinie = self.ganglinie
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

    def run_ganglinie(self):
        initialized = self.init_application()
        if initialized:
            layer, layer_name = initialized
        else:
            return
        selected_features = layer.selectedFeatures()
        if len(selected_features) < 1:
            self.showMessageBox("Fehler",
                                "Bitte wählen Sie mindestens {} aus!".format(
                                    "einen Schacht" if layer_name == "schaechte" else "eine Haltung"),
                                Type.Error)
            return
        self.route = self.navigator.get_schaechte(
            [f[1] for f in selected_features]) if layer_name == "schaechte" else self.navigator.get_haltungen(
            [f[1] for f in selected_features])
        if self.ganglinie.id != self.id:
            self.ganglinie.refresh(_id=self.id, haltungen=self.route.get("haltungen"),
                                   schaechte=self.route.get("schaechte"), dbname=self.dbname)
        self.ganglinie.show()
