import logging
import sys
from app.core.config import settings


def get_logger(name: str = "rayda-app") -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.flush = lambda: sys.stdout.flush()

        formatter = logging.Formatter(
            settings.LOG_FORMAT,
            settings.LOG_DATE_FORMAT,
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(settings.LOG_LEVEL)

    logger.propagate = False

    return logger