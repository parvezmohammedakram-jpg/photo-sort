"""
Logging configuration for PhotoSort.

Provides a consistent logger with appropriate levels.
Use: from app.utils.logger import logger
"""

import logging
import sys

from app.config import LOG_LEVEL


def setup_logger(name: str = "photosort") -> logging.Logger:
    """
    Create and configure the application logger.

    Args:
        name: Logger name.

    Returns:
        Configured logger instance.
    """
    log = logging.getLogger(name)
    log.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # Avoid adding duplicate handlers on repeated calls
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log


logger = setup_logger()
