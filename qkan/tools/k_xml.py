from qkan.utils import get_logger
import sys

logger = get_logger(f'QKan.{__file__}')

def _get_float(block, tag: str, default: float = None) -> [float, None]:
    """Liest einen Tag und meldet falschen Datentyp"""
    text = block.findtext(tag, default)
    if text is None:
        return None
    elif isinstance(text, float):
        return text
    elif text.strip() == "":
        logger.warning(f'Feld <{tag}> ist leer')
    elif isinstance(text, str):
        try:
            return float(text)
        except ValueError:
            logger.warning("_m150porter._import.py._get_float: %s" % sys.exc_info()[1])
            logger.warning(f'Falscher Datentyp in Feld <{tag}>')
        except Exception:
            logger.warning("_m150porter._import.py._get_float: %s" % sys.exc_info()[1])
            logger.warning(f'Fehler in Feld <{tag}>')
    return default

def _get_int(block, tag: str, default: int = None) -> [int, None]:
    """Liest einen Tag und meldet falschen Datentyp"""
    text = block.findtext(tag, default)
    if text is None:
        return None
    elif isinstance(text, int):
        return text
    elif text.strip() == "":
        logger.warning(f'Feld <{tag}> ist leer')
    elif isinstance(text, str):
        try:
            return int(text)
        except ValueError:
            logger.warning("_m150porter._import.py._get_int: %s" % sys.exc_info()[1])
            logger.warning(f'Falscher Datentyp in Feld <{tag}>')
        except Exception:
            logger.warning("_m150porter._import.py._get_int: %s" % sys.exc_info()[1])
            logger.warning(f'Fehler in Feld <{tag}>')
    return default
