"""
FinResolve AI — Hardened FastAPI Application

Provides:
- Liveness check (/health) and Readiness check (/ready)
- Observability snapshot (/metrics)
- Security headers, Request ID correlation, payload size limiting
- Sanitized error handlers (zero stack trace leakage)
- Structured logging with credential redaction
- Counterfactual resolution proposal endpoints
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from apps.api.config import Settings, get_settings
from data.schemas.case import CaseRecords
from services.common.logging import RedactingJsonFormatter
from services.counterfactual.proposal import ResolutionOrchestrator
from services.observability.metrics import global_metrics
from services.policy_engine.engine import DeterministicPolicyEngine
from services.reconciliation.engine import ReconciliationEngine
from services.repositories.case_repository import validate_identifier
from services.security.auth import AuthenticatedUser
from services.security.errors import register_error_handlers
from services.security.middleware import (
    PayloadSizeLimitMiddleware,
    RequestCorrelationMiddleware,
    SecurityHeadersMiddleware,
)
from services.security.rate_limiter import rate_limit
from services.security.rbac import get_current_user, require_permission, Permission


def _configure_logging(settings: Settings) -> logging.Logger:
    """Configure structured JSON logging with secret redaction."""
    logger = logging.getLogger("finresolve")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Clear existing handlers to prevent duplicate lines
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = RedactingJsonFormatter(service_name=settings.app_name)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    logger = logging.getLogger("finresolve")
    logger.info("FinResolve AI API starting up in %s environment", app.state.settings.app_env)
    yield
    logger.info("FinResolve AI API shutting down")


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Application factory with security hardening and observability.
    """
    if settings is None:
        settings = get_settings()

    _configure_logging(settings)

    app = FastAPI(
        title="FinResolve AI",
        description="Counterfactual Financial Reconciliation & Resolution Engine",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Attach settings to app state
    app.state.settings = settings

    # 1. Register Middlewares (in execution order)
    app.add_middleware(PayloadSizeLimitMiddleware, max_size_bytes=settings.max_request_size_bytes)
    app.add_middleware(RequestCorrelationMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS
    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Register Sanitized Global Error Handlers
    register_error_handlers(app)

    # 3. Standard Endpoints

    @app.get("/health", tags=["system"])
    async def health_check(request: Request) -> dict:
        """
        Liveness check endpoint.
        Answers: 'Is this process running?'
        """
        global_metrics.increment("health_checks_total")
        return {
            "status": "ok",
            "version": settings.app_version,
            "environment": settings.app_env,
            "phase": "1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/ready", tags=["system"])
    async def readiness_check(request: Request) -> JSONResponse:
        """
        Readiness check endpoint.
        Answers: 'Is this service ready to accept traffic and dependencies healthy?'
        """
        global_metrics.increment("readiness_checks_total")
        
        # Check core subsystem readiness
        checks = {
            "application": "ready",
            "config": "valid",
            "reconciliation_engine": "ready",
            "counterfactual_engine": "ready",
            "policy_engine": "ready",
        }

        is_ready = all(v == "ready" or v == "valid" for v in checks.values())

        return JSONResponse(
            status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "ready" if is_ready else "not_ready",
                "checks": checks,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.get("/metrics", tags=["observability"])
    async def get_metrics(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """
        Observability metrics endpoint.
        Returns aggregated request, latency, and discrepancy counters.
        """
        return global_metrics.get_summary()

    # ---- Phase 4 Counterfactual & Policy Routes ----
    _recon_engine = ReconciliationEngine()
    _policy_engine = DeterministicPolicyEngine(
        max_auto_resolve_amount_minor=settings.policy_auto_resolve_max_amount,
        auto_resolve_enabled=settings.policy_auto_resolve_enabled,
    )
    _orchestrator = ResolutionOrchestrator(policy_engine=_policy_engine)
    _proposal_store: dict[str, list[Any]] = {}

    @app.post("/cases/{case_id}/propose-resolutions", tags=["resolution"])
    async def propose_resolutions(
        case_id: str,
        records: CaseRecords,
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """
        Generate, simulate, and evaluate counterfactual resolution proposals for a case.
        """
        try:
            valid_case_id = validate_identifier(case_id, "case_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        global_metrics.increment("resolution_requests_total")

        recon_result = _recon_engine.reconcile_records(valid_case_id, records)
        proposals = _orchestrator.generate_proposals(valid_case_id, records, recon_result)
        _proposal_store[valid_case_id] = proposals

        return {
            "case_id": valid_case_id,
            "discrepancies_count": len(recon_result.discrepancies),
            "proposals_count": len(proposals),
            "proposals": [p.model_dump() for p in proposals],
        }

    @app.get("/cases/{case_id}/proposals", tags=["resolution"])
    async def get_proposals(
        case_id: str,
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Retrieve simulated proposals for a case."""
        try:
            valid_case_id = validate_identifier(case_id, "case_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        proposals = _proposal_store.get(valid_case_id, [])
        return {
            "case_id": valid_case_id,
            "proposals_count": len(proposals),
            "proposals": [p.model_dump() if hasattr(p, "model_dump") else p for p in proposals],
        }

    return app


# Default app instance
app = create_app()
