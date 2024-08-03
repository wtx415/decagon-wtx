import logging
from typing import Optional


def get_console_logger(
    name, level: Optional[int] = None, log_format: Optional[str] = None
) -> logging.Logger:
    """
    Get a console logger.

    Args:
        name: The name of the logger.
        level: The logging level. Default is INFO.
        log_format: The logging format. Default is "%(asctime)s - %(name)s - %(levelname)s - %(message)s".

    Returns:
        logging.Logger: The logger object.
    """
    if level is None:
        level = logging.INFO

    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
