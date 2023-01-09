import logging
from logging import StreamHandler, LogRecord

from qgis.core import QgsMessageLog, Qgis


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
