import os
import time

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.utils.logger import get_logger

load_dotenv()
logger = get_logger("migrate")

def wait_for_db(url, timeout=30):
    engine = create_engine(url)
    for _ in range(timeout):
        try:
            with engine.connect():
                logger.info("Database is ready!")
                return True
        except OperationalError:
            logger.info("Waiting for database to be ready...")
            time.sleep(1)
    logger.error("Database not ready after waiting.")
    return False

def run_migrations():
    db_url = os.getenv("DATABASE_URL")
    if not wait_for_db(db_url):
        raise RuntimeError("Database connection failed after retries.")

    try:
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../../alembic.ini"))
        logger.info("Starting database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")
    except Exception:
        logger.exception("Error occurred while running migrations!")
        raise
