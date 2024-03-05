import datetime
import logging
import tempfile
from logging import StreamHandler, LogRecord
from pathlib import Path
from typing import Any, cast

from qgis.core import QgsMessageLog, Qgis

LOG_NOTICE = logging.DEBUG + 1
LOG_ERROR_USER = logging.ERROR + 1
LOG_ERROR_DATA = logging.ERROR + 1
LOG_ERROR_CODE = logging.ERROR + 1


def _translate_level(level: int) -> Qgis.MessageLevel:
    """Translate logging level to Qgis logging level."""
    return {
        logging.CRITICAL: Qgis.Critical,
        logging.ERROR: Qgis.Critical,
        logging.WARNING: Qgis.Warning,
        logging.INFO: Qgis.Info,
        logging.DEBUG: Qgis.Info,
        logging.NOTSET: Qgis.NoLevel,
    }.get(level, Qgis.NoLevel)


class QgisPanelLogger(StreamHandler):
    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)

        # Notify user about warnings and above
        QgsMessageLog.logMessage(
            tag="QKan",
            message=msg,
            notifyUser=record.levelno >= 30,
            level=_translate_level(record.levelno),
        )


class QKanLogger(logging.Logger):
    def notice(self, msg: str, *args: Any, **kwargs: Any):
        self._log(LOG_NOTICE, msg, args, **kwargs)

    def error_user(self, msg: str, *args, **kwargs):
        kwargs.setdefault("exc_info", True)
        self._log(LOG_ERROR_USER, msg, args, **kwargs)

    def error_data(self, msg: str, *args, **kwargs):
        kwargs.setdefault("exc_info", True)
        self._log(LOG_ERROR_DATA, msg, args, **kwargs)

    def error_code(self, msg: str, *args, **kwargs):
        kwargs.setdefault("exc_info", True)
        self._log(LOG_ERROR_CODE, msg, args, **kwargs)


class QKanLoggingManager(logging.Manager):
    def __init__(self, rootnode: QKanLogger):
        super().__init__(cast(logging.RootLogger, rootnode))
        self.setLoggerClass(QKanLogger)


def setup_logging(log_to_console: bool) -> tuple[QKanLogger, Path]:
    """Set up our custom logger & logging manager"""

    # create custom logger
    logger = QKanLogger("Qkan")
    logger.setLevel(logging.DEBUG)

    # inject custom manager as default
    QKanLogger.manager = QKanLoggingManager(logger)

    # register custom logging levels
    for level, name in [
        (LOG_NOTICE, "NOTICE"),
        (LOG_ERROR_USER, "ERROR_USER"),
        (LOG_ERROR_DATA, "ERROR_DATA"),
        (LOG_ERROR_CODE, "ERROR_CODE"),
    ]:
        logging.addLevelName(level, name)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_path = Path(tempfile.gettempdir()) / "QKan_{}.log".format(
        datetime.datetime.today().strftime("%Y-%m-%d")
    )
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # todo: dynamically decide where to log to, configurable in settings
    qgis_handler = QgisPanelLogger()
    qgis_handler.setFormatter(logging.Formatter(fmt="%(name)s - %(message)s"))
    qgis_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(qgis_handler)

    if log_to_console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)

    return logger, log_path


def get_logger(name: str) -> QKanLogger:
    """Return custom QKanLogger instance."""

    return QKanLogger("Qkan").getChild(name.replace("QKan.", ""))
