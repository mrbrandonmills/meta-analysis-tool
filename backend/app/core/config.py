"""Application configuration."""
import os
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
    anthropic_api_key: str = "dummy_key_for_migrations"
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
    # CRITICAL FIX: Environment-based debug default to prevent production debug mode
    # Default to False, but allow override via DEBUG environment variable
    # This prevents accidental debug mode in production deployments like Railway
    debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    log_level: str = "INFO"

    # Security
    secret_key: str = "dummy_secret_key_for_migrations_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Stripe Payment Integration
    stripe_secret_key: str = "sk_test_dummy_key_for_migrations"
    stripe_publishable_key: str = "pk_test_dummy_key_for_migrations"
    stripe_webhook_secret: str = "whsec_dummy_secret_for_migrations"
    stripe_price_id: Optional[str] = None  # Monthly $100 price ID

    # Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@metaanalysistool.com"
    smtp_from_name: str = "Meta-Analysis Tool"
    smtp_use_tls: bool = True

    # Feature Flags
    enable_voice: bool = False
    enable_learning: bool = True
    enable_verification: bool = True

    # Paths
    temp_dir: str = "./temp"
    data_dir: str = "./data"
    downloads_dir: str = "./downloads"

    # PDF Processing Configuration
    pdf_storage_dir: str = "./downloads/pdfs"
    pdf_max_file_size_mb: int = 50
    pdf_download_timeout_seconds: int = 30
    pdf_rate_limit_per_second: float = 3.0
    pdf_max_retries: int = 3
    pdf_cleanup_days: int = 30

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
