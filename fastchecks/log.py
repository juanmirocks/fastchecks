import logging

from fastchecks import meta

DEFAULT_LOG_CONSOLE_LEVEL = "INFO"

_LOG_NAME = meta.NAME


def config_console_logger(level: str, name: str = _LOG_NAME) -> logging.Logger:
    """
    Configure a console logger with the given level.
    """
    logging.basicConfig(format="%(asctime)s  %(levelname)-8s %(name)-15s %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger


MAIN_LOGGER: logging.Logger = config_console_logger(DEFAULT_LOG_CONSOLE_LEVEL)
"""Main application logger."""


def reset_main_console_logger(level: str) -> logging.Logger:
    """
    Re-initialize the main application logger to console with the given level.
    """
    global MAIN_LOGGER

    MAIN_LOGGER = config_console_logger(level)

    return MAIN_LOGGER


def reset_root_logger(level: str) -> None:
    logging.getLogger().setLevel(level)
