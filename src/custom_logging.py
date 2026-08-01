# src/custom_logging.py
import logging
from logging.handlers import RotatingFileHandler
import os
import re
from datetime import datetime
from pathlib import Path

APP_LOGGER_NAME = "FaceSort"
# Eigene Log-Level
LOADING = 24
SUCCESS = 25
logging.addLevelName(LOADING, "LOADING")
logging.addLevelName(SUCCESS, "SUCCESS")


os.makedirs("logs", exist_ok=True)


def loading(self, message, *args, **kwargs):
    if self.isEnabledFor(LOADING):
        self._log(LOADING, message, args, **kwargs)


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)


logging.Logger.loading = loading
logging.Logger.success = success

# Regex zum Entfernen von ANSI-Escape-Sequenzen
_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')


def strip_ansi(s: str) -> str:
    """Entferne ANSI-Farbcodes aus einem String."""
    if not isinstance(s, str):
        return s
    return _ANSI_RE.sub('', s)


#
# Formatters
#
class ColoredFormatter(logging.Formatter):
    """
    Formatter mit ANSI-Farben für die Konsole.
    """
    green = "\033[1;92m"
    yellow = "\033[1;93m"
    red = "\033[1;31m"
    purple = "\033[1;35m"
    blue = "\033[1;94m"
    reset = "\033[0m"
    fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    FORMATS = {
        logging.DEBUG: blue + fmt + reset,
        logging.INFO: blue + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: red + fmt + reset,
        LOADING: purple + fmt + reset,
        SUCCESS: green + fmt + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.fmt)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class PlainFormatter(logging.Formatter):
    """
    Plain formatter ohne ANSI-Codes (für WebSocket/SSE-Ausgabe).
    """
    fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    def __init__(self):
        super().__init__(self.fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        # Verwende gewöhnliche Formatierung (ohne Farben)
        return super().format(record)




# Regex: erkennt Log-Level Wörter
_LEVEL_RE = re.compile(r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|LOADING|SUCCESS)\b', re.IGNORECASE)
# Regex: erkennt typische Beginn eines Log-Eintrags mit Datum "YYYY-MM-DD "
_TIMESTAMP_SPLIT_RE = re.compile(r'(?=\d{4}-\d{2}-\d{2}\s)')



#
# Logger-Setup-Funktion
#
def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Alte Handler entfernen
    if logger.hasHandlers():
        logger.handlers.clear()

    #
    # Konsolen-Handler
    #
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    #
    # Datei-Handler
    #
    log_dir = Path("logs")

    # Suche nur Logdateien dieses Loggers und sortiere nach Änderungszeit
    log_files = sorted(
        log_dir.glob(f"{name}-*.log"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    # Entferne sehr alte Logdateien: behalte nur die 5 neuesten
    for old_file in log_files[5:]:
        try:
            old_file.unlink()
        except Exception as e:
            logger.warning(f"Fehler beim Löschen von {old_file}: {e}")

    # Erzeuge bei jedem Programmstart eine neue Logdatei mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rotating_log = log_dir / f"{name}-{timestamp}.log"

    # Rotierender Datei-Handler: begrenzt Dateigröße (kein zusätzliches Backup,
    # weil wir die Anzahl der Dateien manuell auf 5 beschränken)
    file_handler = RotatingFileHandler(
        filename=str(rotating_log),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=0,
        encoding="utf-8",
    )

    file_handler.setLevel(level)
    file_handler.setFormatter(PlainFormatter())

    logger.addHandler(file_handler)

    logger.propagate = False

    return logger
