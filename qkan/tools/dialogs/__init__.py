import logging
import os
from typing import TYPE_CHECKING, Optional

from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QLineEdit, QPushButton, QWidget

from qkan.database.dbfunc import DBConnection

logger = logging.getLogger("QKan.tools.dialogs")

if TYPE_CHECKING:
    from qkan.plugin import QKanPlugin


class QKanDialog(QDialog):
    def __init__(self, plugin: "QKanPlugin", parent: Optional[QWidget] = None):
        # noinspection PyArgumentList
        super().__init__(parent)
        self.setupUi(self)

        self.plugin = plugin

    def bind_select_path(
        self,
        title: str,
        file_filter: str,
        line_edit: QLineEdit,
        push_button: QPushButton,
        is_open: bool,
        default_dir: Optional[str] = None,
    ) -> None:
        logger.debug(f'bind_select_path: \nfile_filter: {file_filter}\nis_open: {is_open}')
        if not default_dir:
            default_dir = self.plugin.default_dir

        push_button.clicked.connect(
            lambda: self.select_path(
                title, file_filter, line_edit, is_open, default_dir
            )
        )

    def select_path(
        self,
        title: str,
        file_filter: str,
        line_edit: QLineEdit,
        is_open: bool,
        default_dir: str,
    ) -> None:
        logger.debug(f'select_path: \nfile_filter: {file_filter}\nis_open: {is_open}')
        if is_open:
            # noinspection PyArgumentList,PyCallByClass
            filename, __ = QFileDialog.getOpenFileName(
                self, title, default_dir, file_filter
            )
        else:
            # noinspection PyArgumentList,PyCallByClass
            filename, __ = QFileDialog.getSaveFileName(
                self,
                title,
                default_dir,
                file_filter,
            )

        if os.path.dirname(filename) != "":
            line_edit.setText(filename)


class QKanDBDialog(QKanDialog):
    pb_selectQKanDB: QPushButton
    tf_qkanDB: QLineEdit

    open_mode = True

    def __init__(self, plugin: "QKanPlugin", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)
        self.db_qkan: Optional[DBConnection] = None


class QKanProjectDialog(QKanDialog):
    pb_selectProjectFile: QPushButton
    tf_projectFile: QLineEdit

    def __init__(self, plugin: "QKanPlugin", parent: Optional[QWidget] = None):
        super().__init__(plugin, parent)

        self.pb_selectProjectFile.clicked.connect(self.select_project_file)

    def select_project_file(self) -> None:
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
