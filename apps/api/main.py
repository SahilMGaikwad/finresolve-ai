"""
FinResolve AI — FastAPI Application

Minimal API server for Phase 1. Provides:
- Health check endpoint
- Structured logging
- CORS middleware
- Lifespan management stubs
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.config import Settings, get_settings


def _configure_logging(settings: Settings) -> logging.Logger:
    """Configure structured logging for the application."""
    logger = logging.getLogger("finresolve")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    logger = logging.getLogger("finresolve")
    logger.info("FinResolve AI API starting up")

    # TODO(phase-2): Initialize database connection pool
    # TODO(phase-3): Initialize ML model registry
    # TODO(phase-4): Initialize agent orchestrator

    yield

    # Shutdown
    logger.info("FinResolve AI API shutting down")
    # TODO(phase-2): Close database connections
    # TODO(phase-3): Cleanup ML resources


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Application factory.

    Using a factory pattern so tests can create isolated app instances
    with custom settings.
    """
    if settings is None:
        settings = get_settings()

    _configure_logging(settings)

    app = FastAPI(
        title="FinResolve AI",
        description="Counterfactual Financial Reconciliation & Resolution Engine",
        version=settings.app_version,
        lifespan=lifespan,
    )

    # CORS
    origins = [origin.strip() for origin in settings.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store settings on app state for access in endpoints
    app.state.settings = settings

    # ---- Routes ----

    @app.get("/health", tags=["system"])
    async def health_check() -> dict:
        """
        Health check endpoint.

        Returns basic application status. Used by Docker health checks,
        load balancers, and monitoring systems.
        """
        return {
            "status": "ok",
            "version": settings.app_version,
            "environment": settings.app_env,
            "phase": "1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # TODO(phase-2): Mount ingestion router
    # TODO(phase-2): Mount reconciliation router
    # TODO(phase-3): Mount investigation router
    # TODO(phase-5): Mount dashboard API router

    return app


# Default app instance for `uvicorn apps.api.main:app`
app = create_app()
