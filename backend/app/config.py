from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, centralized using Pydantic BaseSettings.
    Values are loaded from environment variables or the .env file.
    """
    # Application Config
    APP_NAME: str = "MedConnect CRM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://medconnect:medconnect@localhost:5432/medconnect"

    # JWT Authentication
    SECRET_KEY: str = "super-secret-medconnect-key-development-only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM Integrations
    GROQ_API_KEY: str = ""

    # CORS Settings
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # This tells pydantic to look for a .env file and ignore extra env vars not defined here
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings object.
    Uses lru_cache to ensure we only read the environment variables once.
    """
    return Settings()
