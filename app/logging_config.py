"""Logging setup for the whole application."""

import logging
from pathlib import Path

LOGGER_NAME = "calculator"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
DEFAULT_LOG_FILE = Path("logs") / "app.log"

# The handlers that setup_logging installed, so they can be removed again
_installed_handlers = []


def setup_logging(level=logging.INFO, log_file=DEFAULT_LOG_FILE):
    """Send the application's log messages to the console and to a log file."""
    close_logging()  # start clean, so calling this twice never repeats messages

    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding="utf-8"),
    ]

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        _installed_handlers.append(handler)
    return logger


def close_logging():
    """Remove and close the handlers that setup_logging installed."""
    logger = logging.getLogger(LOGGER_NAME)
    while _installed_handlers:
        handler = _installed_handlers.pop()
        logger.removeHandler(handler)
        handler.close()