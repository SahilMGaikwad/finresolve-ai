# Frontend to Backend API Mapping

This document details the REST API mapping between the Next.js frontend (`apps/web/lib/api.ts`) and the hardened FastAPI backend (`apps/api/main.py`).

| UI Feature / Screen | Backend Endpoint | HTTP Method | Payload / Params | Response Schema |
| :--- | :--- | :---: | :--- | :--- |
| **System Liveness** | `/health` | `GET` | None | `{"status": "ok", "version": "...", ...}` |
| **Subsystem Readiness** | `/ready` | `GET` | None | `{"status": "ready", "checks": {...}}` |
| **Observability Telemetry**| `/metrics` | `GET` | Bearer Token | `{"counters": {...}, "gauges": {...}}` |
| **Benchmark Seed Loader** | `/cases/seed-benchmark` | `POST` | `{"num_cases": 50}` | `{"status": "seeded", "count": 50}` |
| **Case Explorer List** | `/cases` | `GET` | `?limit=50&offset=0` | `{"total": 50, "cases": [CaseSummary]}`|
| **Case Detail Observed** | `/cases/{case_id}` | `GET` | None | `CaseDetail` (Full records + graph) |
| **AI Investigation** | `/cases/{case_id}/investigate` | `POST` | `CaseRecords` (JSON) | `InvestigationResult` |
| **Counterfactual Proposals**| `/cases/{case_id}/propose-resolutions` | `POST` | `CaseRecords` (JSON) | `{"proposals": [ResolutionProposal]}`|
| **Proposal Approval** | `/proposals/{proposal_id}/approve` | `POST` | `{"comments": "..."}` | `ApprovalRecord` |
| **Proposal Rejection** | `/proposals/{proposal_id}/reject` | `POST` | `{"comments": "..."}` | `ApprovalRecord` |
| **Audit Log Timeline** | `/audit/events` | `GET` | `?case_id=...&limit=100` | `{"total_events": ..., "events": [...]}`|
