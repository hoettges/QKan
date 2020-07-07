import logging
import os
import typing

from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
)

logger = logging.getLogger("QKan.tools.dialogs")

if typing.TYPE_CHECKING:
    from qkan.tools.application import QKanTools


class QKanDialog(QDialog):
    def __init__(self, plugin: "QKanTools", parent=None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin


class QKanDBDialog(QKanDialog):
    pb_selectQKanDB: QPushButton
    tf_qkanDB: QLineEdit

    def __init__(self, plugin: "QKanTools", parent=None):
        super().__init__(plugin, parent)
        self.pb_selectQKanDB.clicked.connect(self.select_qkan_db)

    def select_qkan_db(self):
        """Anzubindende QKan-Datenbank festlegen"""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getOpenFileName(
            self, "QKan-Datenbank auswählen", self.plugin.default_dir, "*.sqlite"
        )
        if os.path.dirname(filename) != "":
            self.tf_qkanDB.setText(filename)


class QKanProjectDialog(QKanDialog):
    pb_selectProjectFile: QPushButton
    tf_projectFile: QLineEdit

    def __init__(self, plugin: "QKanTools", parent=None):
        super().__init__(plugin, parent)

        self.pb_selectProjectFile.clicked.connect(self.select_project_file)

    def select_project_file(self):
        """Zu erstellende Projektdatei festlegen"""

        # noinspection PyArgumentList,PyCallByClass
        filename, __ = QFileDialog.getSaveFileName(
            self,
            "Dateinamen der zu erstellenden Projektdatei eingeben",
            self.plugin.default_dir,
            "*.qgs",
        )

        if os.path.dirname(filename) != "":
            self.tf_projectFile.setText(filename)