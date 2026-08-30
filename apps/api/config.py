"""
FinResolve AI — API Configuration

Typed configuration loaded from environment variables using Pydantic BaseSettings.
All configuration is centralized here to avoid scattered os.environ calls.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---- Application ----
    app_name: str = "finresolve-ai"
    app_env: str = "development"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    debug: bool = True

    # ---- API Server ----
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    cors_origins: str = "http://localhost:3000"

    # ---- Database ----
    database_url: str = "postgresql://finresolve:CHANGE_ME_IN_PRODUCTION@localhost:5432/finresolve"

    # ---- Policy Engine Thresholds ----
    policy_auto_resolve_confidence_threshold: float = 0.95
    policy_auto_resolve_max_amount: int = 500_000  # in minor currency units (paise)
    policy_auto_resolve_enabled: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


def get_settings() -> Settings:
    """Factory function for settings. Enables dependency injection in tests."""
    return Settings()
