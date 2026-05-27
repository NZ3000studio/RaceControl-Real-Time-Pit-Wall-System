"""FastAPI configuration."""

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Server configuration
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Application info
    title: str = "RaceControl API"
    version: str = "0.1.0"
    description: str = "Real-time telemetry ingestion for Assetto Corsa"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
