import logging
import sys

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter

from app.core.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    datefmt=settings.LOG_DATE_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)]
)

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import user, org, webhooks, integrations
from app.commands.migrate import run_migrations
from app.commands.bootstrap import create_initial_superadmin
from fastapi.middleware.cors import CORSMiddleware

from app.utils.logger import get_logger

logger = get_logger("startup")

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    logger.info("Starting application initialization...")
    try:
        run_migrations()
        create_initial_superadmin()
        logger.info("Application initialization completed successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield
    logger.info("Application shutting down...")

app = FastAPI(title="Multi-Tenant SaaS Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(org.router, prefix="/orgs", tags=["Organizations"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
