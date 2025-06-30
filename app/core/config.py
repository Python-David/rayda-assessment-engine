from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None
    JWT_SECRET_KEY: str = "your_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    INITIAL_SUPERADMIN_EMAIL: str = "superadmin@example.com"
    INITIAL_SUPERADMIN_PASSWORD: str = "SuperSecretPassword123!"

    INITIAL_ADMIN_EMAIL: str = "admin@testorg.com"
    INITIAL_ADMIN_PASSWORD: str = "AdminPass123!"

    REDIS_BROKER_URL: str = "redis://localhost:6379/0"
    REDIS_BACKEND_URL: str = "redis://localhost:6379/1"

    CELERY_MAX_RETRIES: int = 3
    CELERY_RETRY_BACKOFF_BASE: int = 2

    FORCE_SERVICE_FAILURES: int = 0
    ENABLE_RANDOM_FAILURES: bool = False

    WEBHOOK_RATE_LIMIT_COUNT: int = 10
    WEBHOOK_RATE_LIMIT_PERIOD: str = "minute"  # could be "second", "hour", "day"

    @property
    def webhook_rate_limit(self) -> str:
        return f"{self.WEBHOOK_RATE_LIMIT_COUNT}/{self.WEBHOOK_RATE_LIMIT_PERIOD}"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
