# System Overview

This directory contains high-level architecture documentation for FinResolve AI.

## Documents

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — Full system architecture (root level)
- [ADR-001](../decisions/ADR-001-project-architecture.md) — Architecture decisions
- [Threat Model](../threat_model/threat_model.md) — Security analysis
- [Evaluation Plan](../evaluation/evaluation_plan.md) — Experimental methodology

## System Diagram

The system follows a 12-stage financial operations pipeline:

```
                    ┌─────────────────┐
                    │  External Data  │
                    │  Sources        │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   1. INGEST     │  Validate structure, reject malformed
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  2. NORMALIZE   │  Canonical schema, minor units, UTC
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   3. MATCH      │  Deterministic + fuzzy matching
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  4. DETECT      │  Field-by-field comparison
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────┐ ┌──────▼──────┐ ┌─────▼──────┐
     │ 5. EVIDENCE │ │ 6. DIAGNOSE │ │  ANOMALY   │
     │  COLLECTION │ │  ROOT CAUSE │ │  DETECTION │
     └────────┬────┘ └──────┬──────┘ └────────────┘
              │              │
              └──────┬───────┘
                     │
            ┌────────▼────────┐
            │ 7. SIMULATE     │  Counterfactual "what-if" analysis
            │  RESOLUTIONS    │  (deterministic)
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ 8. SELECT       │  Rank by evidence + simulation + risk
            │  RESOLUTION     │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ 9. POLICY CHECK │  Deterministic safety gate
            └───┬────┬────┬───┘
                │    │    │
        ┌───────┘    │    └───────┐
        │            │            │
   AUTO RESOLVE   HUMAN      BLOCK
        │         REVIEW        │
        │            │          │
        └────┬───────┘──────────┘
             │
    ┌────────▼────────┐
    │  10/11. RESOLVE │  Idempotent execution
    │   (if approved) │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │   12. AUDIT &   │  Immutable records
    │    EVALUATE     │
    └─────────────────┘
```

## Module Ownership

| Module | Responsibility | AI Type |
|--------|---------------|---------|
| Ingestion | Input validation and acceptance | None (deterministic) |
| Normalization | Schema standardization | None (deterministic) |
| Matching | Record linking | Deterministic + ML scoring |
| Evidence | Evidence collection | None (deterministic) |
| Anomaly Detection | Pattern detection | ML (scikit-learn, XGBoost) |
| Diagnosis | Root cause analysis | ML + LLM (read-only) |
| Counterfactual | Resolution simulation | None (deterministic) |
| Decision Engine | Resolution selection | Deterministic scoring |
| Policy Engine | Safety enforcement | None (deterministic) |
| Audit | Immutable logging | None (deterministic) |
