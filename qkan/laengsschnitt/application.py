from PyQt6.QtWidgets import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from qgis.core import Qgis
from qgis.gui import QgisInterface

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import fehlermeldung, get_database_QKan
from qkan.plugin import QKanPlugin

# noinspection PyUnresolvedReferences
from . import resources  # noqa: F401
from ._laengsschnitt import LaengsTask
from .application_dialog import LaengsDialog
from qkan.utils import QkanUserError, QkanAbortError, get_logger

logger = get_logger("QKan")


class Laengsschnitt(QKanPlugin):
    def __init__(self, iface: QgisInterface):
        super().__init__(iface)

        self.laengs_dlg = None
        self.db_qkan: DBConnection = None
        self.auswahl={}

        self.windows = []


    def refresh_function(self, database, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl, point, massstab,
                         features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3, geschw_2, anf):
        try:
            LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl,
                       point,
                       massstab, features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3,
                       geschw_2, anf).zeichnen()
            canv.draw()

            return LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, fig_3, canv_3, selected,
                              auswahl,
                              point, massstab, features, db_erg, ausgabe, max, label_4, pushButton_4,
                              horizontalSlider_3,
                              geschw_2, anf).zeichnen()
        except QkanUserError as e:
            # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
            logger.debug(f"Anwenderfehler bei Tool Längsschnitt: {e}")
        except Exception as e:
            logger.error_code(f"Fehler bei Tool Längsschnitt: {e}")
            raise QkanAbortError



    def export_cad_function(self, database, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl, point, massstab,
                            features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3, geschw_2, anf):
        try:
            LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl,
                       point,
                       massstab, features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3, geschw_2,
                       anf).cad()
        except QkanUserError as e:
            # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
            logger.debug(f"Anwenderfehler bei Tool Längsschnitt: {e}")
        except Exception as e:
            logger.error_code(f"Fehler bei Tool Längsschnitt: {e}")
            raise QkanAbortError

    def show_function(self, database, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl, point, massstab,
                      features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3, geschw_2, anf):

        try:
            LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl,
                       point,
                       massstab, features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3, geschw_2,
                       anf).show()
        except QkanUserError as e:
            # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
            logger.debug(f"Anwenderfehler bei Tool Längsschnitt: {e}")
        except Exception as e:
            logger.error_code(f"Fehler bei Tool Längsschnitt: {e}")
            raise QkanAbortError

    def gang_function(self, database, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl, point, massstab,
                      features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3, geschw_2, anf):
        try:
            LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl,
                       point,
                       massstab, features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3,
                       geschw_2, anf).ganglinie()
            canv_3.draw()
        except QkanUserError as e:
            # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
            logger.debug(f"Anwenderfehler bei Tool Längsschnitt: {e}")
        except Exception as e:
            logger.error_code(f"Fehler bei Tool Längsschnitt: {e}")
            raise QkanAbortError


    def animiert_laengs_function(self, database, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl, point,
                                 massstab, features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3,
                                 geschw_2, anf):
        try:
            LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, fig_3, canv_3,
                       selected, auswahl, point, massstab, features, db_erg, ausgabe, max, label_4,
                       pushButton_4, horizontalSlider_3, geschw_2, anf).laengs()
        except QkanUserError as e:
            # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
            logger.debug(f"Anwenderfehler bei Tool Längsschnitt: {e}")
        except Exception as e:
            logger.error_code(f"Fehler bei Tool Längsschnitt: {e}")
            raise QkanAbortError

    def stop_function(self, database, fig, canv, fig_2, canv_2, fig_3, canv_3, selected, auswahl, point,
                                 massstab, features, db_erg, ausgabe, max, label_4, pushButton_4, horizontalSlider_3,
                                 geschw_2, anf):
        self.animation = LaengsTask(self.db_qkan, self.database_qkan, fig, canv, fig_2, canv_2, fig_3, canv_3,
                                    selected, auswahl, point, massstab, features, db_erg, ausgabe, max, label_4,
                                    pushButton_4, horizontalSlider_3, geschw_2, anf)
        try:
            self.animation.stop_animation()
        except QkanUserError as e:
            # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
            logger.debug(f"Anwenderfehler bei Tool Längsschnitt: {e}")
        except Exception as e:
            logger.error_code(f"Fehler bei Tool Längsschnitt: {e}")
            raise QkanAbortError

    # noinspection PyPep8Naming
    def initGui(self) -> None:
        icon = ":/plugins/qkan/laengsschnitt/res/laengsschnitt.png"
        QKan.instance.add_action(
            icon,
            text=self.tr("Längsschnitt"),
            toolbar='QKan-Allgemein',
            callback=self.run_laengs,
            parent=self.iface.mainWindow(),
        )

    def unload(self) -> None:
        if self.laengs_dlg is None:
            return
        else:
            self.laengs_dlg.close()

    def closeEvent(self, event):
        #TODO: Animation stoppen und löchen wenn das Fenster geschlossen wird, da sonst immer ein fehler kommt!
        if self.animation:
            #self.animation.event_source.stop()  # Animation beenden
            self.animation.stop_animation()
            self.animation = None
        event.accept()

    def get_widget(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.laengs_dlg

        fig_attr ='fig1'

        if not hasattr(self.dialog, fig_attr):
            self.dialog.fig = Figure(figsize=(11.5, 5), constrained_layout=True)
            self.dialog.canv = FigureCanvas(self.dialog.fig)

            self.dialog.verticalLayout.addWidget(self.dialog.canv)
            self.dialog.verticalLayout.addWidget(NavigationToolbar(self.dialog.canv, self.dialog, True))

            setattr(self.dialog, fig_attr, self.dialog.fig)


    def get_widget_2(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.laengs_dlg


        fig_attr = 'fig2'

        if not hasattr(self.dialog, fig_attr):
            self.dialog.fig_2 = Figure( constrained_layout=True)
            self.dialog.canv_2 = FigureCanvas(self.dialog.fig_2)

            # # Achse einmal erstellen
            # self.dialog.ax = self.dialog.fig.add_subplot(111)

            self.dialog.verticalLayout_6.addWidget(self.dialog.canv_2)
            self.dialog.verticalLayout_6.addWidget(NavigationToolbar(self.dialog.canv_2, self.dialog, True))

            setattr(self.dialog, fig_attr, self.dialog.fig_2)

    def get_widget_3(self):
        """
        Fügt das Matplotlib-Widget in den jeweiligen Dialog ein.
        """
        self.dialog = self.laengs_dlg

        fig_attr = 'fig3'

        if not hasattr(self.dialog, 'fig3'):
            self.dialog.fig_3 = Figure( constrained_layout=True)
            self.dialog.canv_3 = FigureCanvas(self.dialog.fig_3)

            self.dialog.verticalLayout_2.addWidget(self.dialog.canv_3)
            self.dialog.verticalLayout_2.addWidget(NavigationToolbar(self.dialog.canv_3, self.dialog, True))

            setattr(self.dialog, fig_attr, self.dialog.fig_3)


    def run_laengs(self) -> None:

        #if self.laengs_dlg is not None:
        #    self.laengs_dlg.pushButton.setEnabled(False)
        #    self.laengs_dlg.pushButton_2.setEnabled(False)
        self.laengs_dlg = LaengsDialog(default_dir=self.default_dir, tr=self.tr)

        self.get_widget()
        self.get_widget_2()
        self.get_widget_3()
        self.fig = self.dialog.fig
        self.canv = self.dialog.canv
        self.selected = self.dialog.selected
        self.auswahl = self.dialog.auswahl
        self.features = self.dialog.features
        self.fig_2 = self.dialog.fig_2
        self.canv_2 = self.dialog.canv_2
        self.fig_3 = self.dialog.fig_3
        self.canv_3 = self.dialog.canv_3
        self.db_erg = self.dialog.db_erg
        self.ausgabe = self.laengs_dlg.comboBox.currentText()
        self.max = self.dialog.max
        self.label_4 = self.dialog.label_4


        # Fill dialog with current info
        get_database_QKan()
        self.database_qkan = QKan.config.database.qkan
        self.db_qkan = DBConnection(dbname=self.database_qkan)
        self.log.debug(f"{__file__}: Datenbankverbindung wurde hergestellt...")

        self.laengs_dlg.refresh_function = self.refresh_function
        self.laengs_dlg.export_cad_function = self.export_cad_function
        self.laengs_dlg.show_function = self.show_function
        self.laengs_dlg.gang_function = self.gang_function
        self.laengs_dlg.animiert_laengs_function = self.animiert_laengs_function
        self.laengs_dlg.stop_function = self.stop_function

        self.laengs_dlg.pushButton_2.click()
        self.laengs_dlg.show()

        self.point = self.laengs_dlg.lineEdit.text()
        self.massstab = self.laengs_dlg.lineEdit_2.text()


        if self.laengs_dlg.exec_():

            # Save to config
            QKan.config.save()

            #db_qkan = DBConnection(dbname=self.database_qkan)
            if not self.db_qkan:
                fehlermeldung(
                    "Fehler im Längsschnitt",
                    f"QKan-Datenbank {self.database_qkan} wurde nicht gefunden!\nAbbruch!",
                )
                self.iface.messageBar().pushMessage(
                    "Fehler im Längsschnitt",
                    f"QKan-Datenbank {self.database_qkan} wurde nicht gefunden!\nAbbruch!",
                    level=Qgis.MessageLevel.Critical,
                )

                # Run
            try:
                LaengsTask(self.db_qkan, self.database_qkan, self.fig, self.canv, self.fig_2,
                           self.canv_2, self.fig_3, self.canv_3, self.selected, self.auswahl, self.point,
                           self.massstab, self.features, self.db_erg, self.ausgabe, self.max, self.label_4,
                           self.pushButton_4, self.horizontalSlider_3, self.geschw_2, self.anf
                           ).run()
            except QkanUserError as e:
                # Anwenderfehler werden im Modul gemeldet, deshalb hier keine Meldung mehr
                logger.debug(f"Anwenderfehler bei Tool Längsschnitt: {e}")
            except Exception as e:
                logger.error_code(f"Fehler bei Tool Längsschnitt: {e}")
                raise QkanAbortError

