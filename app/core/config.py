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

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

