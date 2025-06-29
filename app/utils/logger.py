import logging
from app.core.config import settings

def get_logger(name: str = "rayda-app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    return logger
