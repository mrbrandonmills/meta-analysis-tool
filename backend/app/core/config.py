"""Application configuration."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    anthropic_api_key: str
    openai_api_key: Optional[str] = None

    # Database
    database_url: str = "sqlite:///./meta_analysis.db"
    redis_url: str = "redis://localhost:6379/0"

    # Vector Database
    chroma_persist_dir: str = "./data/chroma"

    # Research APIs
    pubmed_api_key: Optional[str] = None
    pubmed_email: Optional[str] = None

    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Feature Flags
    enable_voice: bool = False
    enable_learning: bool = True
    enable_verification: bool = True

    # Paths
    temp_dir: str = "./temp"
    data_dir: str = "./data"
    downloads_dir: str = "./downloads"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
