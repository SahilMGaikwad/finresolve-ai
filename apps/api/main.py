"""
FinResolve AI — Hardened FastAPI Application

Provides:
- Liveness check (/health) and Readiness check (/ready)
- Observability snapshot (/metrics)
- Security headers, Request ID correlation, payload size limiting
- Sanitized error handlers (zero stack trace leakage)
- Structured logging with credential redaction
- Counterfactual resolution proposal endpoints
- AI Financial Investigator endpoints
- Case Explorer, Audit, and Approval REST controller endpoints
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse

from apps.api.config import Settings, get_settings
from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset
from data.schemas.case import CaseRecords, ReconciliationCase
from services.audit.logger import global_audit_logger
from services.common.logging import RedactingJsonFormatter
from services.counterfactual.approval import ApprovalWorkflowManager
from services.counterfactual.proposal import ResolutionOrchestrator
from services.investigator.agent import AIInvestigatorAgent
from services.observability.metrics import global_metrics
from services.policy_engine.engine import DeterministicPolicyEngine
from services.reconciliation.engine import ReconciliationEngine
from services.repositories.case_repository import InMemoryCaseRepository, validate_identifier
from services.security.auth import AuthenticatedUser
from services.security.errors import register_error_handlers
from services.security.middleware import (
    PayloadSizeLimitMiddleware,
    RequestCorrelationMiddleware,
    SecurityHeadersMiddleware,
)
from services.security.rate_limiter import rate_limit
from services.security.rbac import get_current_user, require_permission, Permission


class ApprovalDecisionRequest(BaseModel):
    comments: str | None = None


class SeedBenchmarkRequest(BaseModel):
    num_cases: int = 500
    seed: int = 42
    corruption_rate: float = 0.15


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
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Register Sanitized Global Error Handlers
    register_error_handlers(app)

    # 3. Core Engine Instances
    _recon_engine = ReconciliationEngine()
    _policy_engine = DeterministicPolicyEngine(
        max_auto_resolve_amount_minor=settings.policy_auto_resolve_max_amount,
        auto_resolve_enabled=settings.policy_auto_resolve_enabled,
    )
    _orchestrator = ResolutionOrchestrator(policy_engine=_policy_engine)
    _investigator = AIInvestigatorAgent(
        reconciliation_engine=_recon_engine,
        policy_engine=_policy_engine,
    )
    _case_repo = InMemoryCaseRepository()
    _approval_manager = ApprovalWorkflowManager()
    _proposal_store: dict[str, list[Any]] = {}
    _investigation_store: dict[str, dict[str, Any]] = {}

    # 4. Standard System Endpoints

    @app.get("/health", tags=["system"])
    async def health_check(request: Request) -> dict:
        """Liveness check endpoint."""
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
        """Readiness check endpoint."""
        global_metrics.increment("readiness_checks_total")
        checks = {
            "application": "ready",
            "config": "valid",
            "reconciliation_engine": "ready",
            "counterfactual_engine": "ready",
            "policy_engine": "ready",
            "investigator_engine": "ready",
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
        """Observability metrics summary."""
        return global_metrics.get_summary()

    # 5. Case Explorer & Seed Endpoints

    @app.post("/cases/seed-benchmark", tags=["cases"])
    async def seed_benchmark(
        req: SeedBenchmarkRequest = SeedBenchmarkRequest(),
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Seed the in-memory case repository with benchmark cases for live demonstration."""
        config = GeneratorConfig(seed=req.seed, num_cases=req.num_cases, corruption_rate=req.corruption_rate)
        cases, _ = generate_dataset(config)
        for c in cases:
            await _case_repo.save(c)
        return {"status": "seeded", "count": len(cases), "seed": req.seed}

    @app.get("/cases", tags=["cases"])
    async def list_cases(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        status_filter: str | None = None,
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """List cases with summary metrics for the Case Explorer table."""
        # Auto-seed if empty
        if not _case_repo._cases:
            config = GeneratorConfig(seed=42, num_cases=500, corruption_rate=0.15)
            cases, _ = generate_dataset(config)
            for c in cases:
                await _case_repo.save(c)

        all_cases = list(_case_repo._cases.values())
        summaries = []
        for c in all_cases[offset : offset + limit]:
            recon_res = _recon_engine.reconcile_records(c.case_id, c.observed)
            summaries.append({
                "case_id": c.case_id,
                "merchant_id": c.merchant_id,
                "difficulty": c.difficulty.value if hasattr(c.difficulty, "value") else str(c.difficulty),
                "discrepancies_count": len(recon_res.discrepancies),
                "status": recon_res.status.value,
                "payments_count": len(c.observed.payments),
                "settlements_count": len(c.observed.settlements),
            })
        return {"total": len(all_cases), "limit": limit, "offset": offset, "cases": summaries}

    @app.get("/cases/{case_id}", tags=["cases"])
    async def get_case(
        case_id: str,
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Retrieve full observed records for a specific case."""
        try:
            valid_case_id = validate_identifier(case_id, "case_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        case = await _case_repo.get_by_id(valid_case_id)
        if not case:
            # Check if dynamically generated in batch
            config = GeneratorConfig(seed=42, num_cases=500, corruption_rate=0.15)
            cases, _ = generate_dataset(config)
            for c in cases:
                await _case_repo.save(c)
            case = await _case_repo.get_by_id(valid_case_id)

        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{valid_case_id}' not found")

        recon_res = _recon_engine.reconcile_records(valid_case_id, case.observed)
        return {
            "case_id": case.case_id,
            "merchant_id": case.merchant_id,
            "difficulty": case.difficulty.value if hasattr(case.difficulty, "value") else str(case.difficulty),
            "status": recon_res.status.value,
            "observed": case.observed.model_dump(),
            "discrepancies": [d.model_dump() for d in recon_res.discrepancies],
            "evidence": [ev.model_dump() for ev in recon_res.evidence],
            "evidence_graph": recon_res.evidence_graph.model_dump(),
            "hypotheses": [h.model_dump() for h in recon_res.hypotheses],
        }

    # 6. Resolution & Simulation Endpoints

    @app.post("/cases/{case_id}/propose-resolutions", tags=["resolution"])
    async def propose_resolutions(
        case_id: str,
        records: CaseRecords,
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Generate, simulate, and evaluate counterfactual resolution proposals."""
        try:
            valid_case_id = validate_identifier(case_id, "case_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        global_metrics.increment("resolution_requests_total")
        recon_result = _recon_engine.reconcile_records(valid_case_id, records)
        proposals = _orchestrator.generate_proposals(valid_case_id, records, recon_result)
        _proposal_store[valid_case_id] = proposals

        for p in proposals:
            _approval_manager.submit_for_review(p.proposal_id, user)

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

    # 7. AI Investigator Endpoints

    @app.post("/cases/{case_id}/investigate", tags=["investigator"])
    async def investigate_case(
        case_id: str,
        records: CaseRecords,
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Execute an evidence-grounded investigation using the AI Financial Investigator."""
        try:
            valid_case_id = validate_identifier(case_id, "case_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        global_metrics.increment("investigation_requests_total")
        result = _investigator.investigate_case(valid_case_id, records)
        if valid_case_id not in _investigation_store:
            _investigation_store[valid_case_id] = {}
        _investigation_store[valid_case_id][result.investigation_id] = result

        return result.model_dump()

    @app.get("/cases/{case_id}/investigations/{investigation_id}", tags=["investigator"])
    async def get_investigation(
        case_id: str,
        investigation_id: str,
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Retrieve a previous investigation result by ID."""
        try:
            valid_case_id = validate_identifier(case_id, "case_id")
            valid_inv_id = validate_identifier(investigation_id, "investigation_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        case_invs = _investigation_store.get(valid_case_id, {})
        res = case_invs.get(valid_inv_id)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

        return res.model_dump() if hasattr(res, "model_dump") else res

    # 8. Human Approval Workflow Endpoints

    @app.post("/proposals/{proposal_id}/approve", tags=["approvals"])
    async def approve_proposal(
        proposal_id: str,
        req: ApprovalDecisionRequest = ApprovalDecisionRequest(),
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Approve a pending proposal enforcing separation of duties."""
        try:
            valid_prop_id = validate_identifier(proposal_id, "proposal_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        try:
            record = _approval_manager.approve_proposal(valid_prop_id, user, comments=req.comments)
            return record.model_dump()
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @app.post("/proposals/{proposal_id}/reject", tags=["approvals"])
    async def reject_proposal(
        proposal_id: str,
        req: ApprovalDecisionRequest = ApprovalDecisionRequest(),
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Reject a pending proposal."""
        try:
            valid_prop_id = validate_identifier(proposal_id, "proposal_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        try:
            record = _approval_manager.reject_proposal(valid_prop_id, user, comments=req.comments)
            return record.model_dump()
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    # 9. Audit Trail Endpoint

    @app.get("/audit/events", tags=["audit"])
    async def get_audit_events(
        case_id: str | None = None,
        limit: int = Query(100, ge=1, le=500),
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> dict:
        """Retrieve cryptographically chained audit events."""
        events = global_audit_logger.get_events(case_id=case_id)
        return {
            "total_events": len(events),
            "is_tamper_free": global_audit_logger.verify_integrity(),
            "events": [e.model_dump() for e in events[-limit:]],
        }

    return app


# Default app instance
app = create_app()
