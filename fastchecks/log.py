from fastchecks import meta
import logging

DEFAULT_LOG_CONSOLE_LEVEL = "INFO"

_LOG_NAME = meta.NAME


def _config_console_logger(level: str, name: str = _LOG_NAME) -> logging.Logger:
    """
    Configure root logging to console with the given level.
    """
    logging.basicConfig(format="%(asctime)s  %(levelname)-8s %(name)-10s %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger


LOGGER: logging.Logger = _config_console_logger(DEFAULT_LOG_CONSOLE_LEVEL)
"""Main application logger."""


def reset_console_logger(**kwargs) -> logging.Logger:
    """
    Initialize the root logger to console with the given level.
    """
    global LOGGER

    LOGGER = _config_console_logger(**kwargs)

    return LOGGER
