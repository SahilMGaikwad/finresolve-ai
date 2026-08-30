# FinResolve AI — Frontend (Next.js + TypeScript)

This directory will contain the web frontend for FinResolve AI.

## Status: NOT IMPLEMENTED (Phase 5+)

The frontend will be scaffolded using Next.js with TypeScript when the backend
APIs are stable enough to consume.

## Planned Features

- Reconciliation dashboard with match/discrepancy overview
- Discrepancy investigation workflow
- Evidence viewer with hypothesis comparison
- Counterfactual simulation results visualization
- Human review queue for escalated cases
- Audit trail viewer
- Policy configuration interface

## Technology

- Next.js 14+ (App Router)
- TypeScript (strict mode)
- React Server Components where appropriate
- API integration with the FastAPI backend

## Design Principles

- Read-only views for financial data — no direct financial mutations from the frontend
- All actions routed through the API's policy engine
- Clear escalation UI for human-review cases
- Audit-friendly: all user actions logged
