"""
FinResolve AI — Application Configuration

Typed configuration loaded from environment variables using Pydantic BaseSettings.
Provides safe defaults for development and strict validation for production.
"""

from __future__ import annotations

import os
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment validation and production fail-safes."""

    # ---- Application Metadata ----
    app_name: str = "finresolve-ai"
    app_env: Literal["development", "staging", "production", "test", "testing"] = "development"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    debug: bool = False

    # ---- API Server & Security ----
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    cors_origins: str = "http://localhost:3000"
    trusted_hosts: str = "localhost,127.0.0.1"
    max_request_size_bytes: int = 10 * 1024 * 1024  # 10 MB limit
    
    # ---- Authentication & Security ----
    auth_enabled: bool = False
    auth_secret_key: str = "dev-secret-key-change-in-production-only-min-32-chars"
    auth_token_expire_minutes: int = 60
    
    # ---- Rate Limiting ----
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 120
    rate_limit_burst: int = 30

    # ---- Database ----
    database_url: str = "postgresql://finresolve:CHANGE_ME_IN_PRODUCTION@localhost:5432/finresolve"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ---- Policy Engine Thresholds (Simulation Only) ----
    policy_auto_resolve_confidence_threshold: float = 0.95
    policy_auto_resolve_max_amount: int = 500_000  # in minor currency units (paise)
    policy_auto_resolve_enabled: bool = False

    @field_validator("debug")
    @classmethod
    def validate_debug_for_env(cls, v: bool, info) -> bool:
        """Ensure debug is strictly disabled in production."""
        env = os.environ.get("APP_ENV", "development")
        if env == "production" and v is True:
            raise ValueError("Debug mode MUST be disabled (debug=False) in production environment!")
        return v

    @field_validator("auth_secret_key")
    @classmethod
    def validate_production_secrets(cls, v: str, info) -> str:
        """Fail fast if default dev secrets are used in production."""
        env = os.environ.get("APP_ENV", "development")
        if env == "production":
            if "dev-secret" in v.lower() or "change_me" in v.lower() or len(v) < 32:
                raise ValueError("Production environment requires a strong, non-default AUTH_SECRET_KEY (min 32 chars)!")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_production_db(cls, v: str, info) -> str:
        """Fail fast if placeholder DB credentials are used in production."""
        env = os.environ.get("APP_ENV", "development")
        if env == "production":
            if "CHANGE_ME" in v or "localhost" in v:
                raise ValueError("Production environment requires an explicit, secure DATABASE_URL!")
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


def get_settings() -> Settings:
    """Factory function for settings. Enables dependency injection in tests."""
    return Settings()
