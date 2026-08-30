# ADR-001: Project Architecture

**Status**: Accepted
**Date**: 2026-08-30
**Decision Makers**: Project Team
**Context**: Initial architecture selection for FinResolve AI

---

## Context

We are building FinResolve AI, a counterfactual financial reconciliation engine that must:

1. Process heterogeneous financial records (payments, orders, settlements, refunds, fees, ledger entries, payouts)
2. Detect and diagnose discrepancies between related records
3. Simulate possible resolutions and select the safest option
4. Enforce strict safety policies on all financial actions
5. Maintain complete audit trails
6. Support ML-based anomaly detection and LLM-assisted diagnosis
7. Be evaluated against synthetic data with ground truth

This ADR documents the key architectural decisions and the alternatives considered.

---

## Decision 1: Modular Monolith over Microservices

### Decision

Use a **modular monolith** architecture within a monorepo, with clear module boundaries that could be extracted into microservices later.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Modular monolith** (chosen) | Simple deployment, easy debugging, low operational overhead, refactor-friendly | Harder to scale individual components independently |
| Microservices | Independent scaling, technology diversity | High operational complexity, distributed debugging, network latency between services, premature for an internship project |
| Monolith (no module boundaries) | Simplest | Tight coupling, hard to test, hard to extend |

### Rationale

A modular monolith provides the benefits of clear separation (testable boundaries, independent development) without the operational burden of microservices. For an internship project, operational simplicity is critical. The module boundaries are designed so that extraction to microservices is straightforward if needed.

---

## Decision 2: FastAPI over Django/Flask

### Decision

Use **FastAPI** for the backend API layer.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **FastAPI** (chosen) | Async-first, auto-generated OpenAPI docs, Pydantic integration, modern Python typing, high performance | Smaller ecosystem than Django |
| Django + DRF | Mature ecosystem, built-in admin, ORM | Synchronous by default, heavier, more opinionated than needed |
| Flask | Lightweight, flexible | No built-in validation, no auto-docs, more boilerplate |

### Rationale

FastAPI's native Pydantic integration is critical for a system that processes structured financial records. Auto-generated OpenAPI documentation reduces documentation burden. Async support is valuable for I/O-bound operations (database queries, LLM calls).

---

## Decision 3: PostgreSQL as Primary Database

### Decision

Use **PostgreSQL** as the single primary database.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **PostgreSQL** (chosen) | ACID compliance, JSON support, mature, widely supported | Requires management |
| SQLite | Zero config, embedded | No concurrent write support, not suitable for production |
| MongoDB | Flexible schema | Weaker consistency guarantees, less suitable for financial data |
| PostgreSQL + Redis | Caching layer | Additional infrastructure complexity |

### Rationale

Financial data requires ACID transactions. PostgreSQL provides this with excellent performance, JSON/JSONB support for semi-structured data (evidence records, metadata), and a mature ecosystem. Redis can be added later if caching is needed.

---

## Decision 4: LangGraph over LangChain for Agent Orchestration

### Decision

Use **LangGraph** for agent orchestration.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **LangGraph** (chosen) | State machine model, explicit control flow, better debuggability, controllable cycles | Newer, smaller community |
| LangChain agents | Large ecosystem, many integrations | Opaque chains, harder to debug, implicit control flow |
| Custom agent loop | Full control | More development effort, reinventing solved problems |
| CrewAI | Multi-agent support | Less control over individual agent steps |

### Rationale

LangGraph's state-machine model maps directly to the investigation workflow (collect → diagnose → simulate → decide). The explicit state transitions are critical for auditability — we need to know exactly which step the agent is in and why. LangChain's implicit chain composition makes debugging and auditing harder.

---

## Decision 5: Deterministic Policy Engine (No ML/LLM)

### Decision

The policy engine is **purely deterministic**. No ML or LLM involvement in safety-critical decisions.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Deterministic rules** (chosen) | Predictable, auditable, testable, no hallucination risk | Less flexible, may miss edge cases |
| ML-assisted policy | Could learn from historical decisions | Non-deterministic, harder to audit, hallucination risk in safety-critical path |

### Rationale

The policy engine is the last safety gate before financial actions. It must be fully deterministic, testable, and auditable. Every policy decision must be explainable as "rule X evaluated to Y because of inputs Z." ML-based policy decisions would introduce non-determinism into the safety-critical path.

---

## Decision 6: Integer Minor Currency Units for Money

### Decision

All monetary values are stored and computed as **integers in minor currency units** (paise for INR, cents for USD).

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Integer minor units** (chosen) | No rounding errors, exact arithmetic, simple comparison | Requires conversion for display |
| Python `Decimal` | Arbitrary precision | Slower, more complex, still needs care with division |
| Floating-point | Easy to use | Rounding errors in financial calculations — unacceptable |

### Rationale

Integer arithmetic eliminates rounding errors entirely for addition, subtraction, and multiplication. For the reconciliation use case, these are the dominant operations. Division (e.g., fee percentage calculations) requires explicit rounding rules, which is handled at the point of calculation with documented rounding policy.

---

## Decision 7: Synthetic Data with Ground Truth for Evaluation

### Decision

Evaluate using **synthetic data with embedded ground truth** labels.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Synthetic with ground truth** (chosen) | Known correct answers, reproducible, tunable complexity | May not capture all real-world patterns |
| Real anonymized data | Realistic patterns | No ground truth, privacy concerns, not reproducible |
| Manual test cases | Precise control | Too small for statistical significance |

### Rationale

Without ground truth, metrics cannot be computed honestly. Synthetic data with labeled discrepancy types, root causes, and correct resolutions enables rigorous evaluation. The generator can be tuned to create progressively harder scenarios. Real data can be used for qualitative validation in the future.

---

## Consequences

1. The modular monolith requires discipline in maintaining module boundaries — enforced through code review and import rules.
2. FastAPI + Pydantic couples the schema layer tightly to the API framework — acceptable given the benefits.
3. PostgreSQL requires database management (migrations, backups) — handled by Alembic and Docker.
4. LangGraph is newer and may have fewer community resources — mitigated by the well-documented state machine design.
5. The deterministic policy engine may need rule updates as new edge cases are discovered — this is preferable to non-deterministic behavior.

---

## References

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — Full system architecture
- [Threat Model](../threat_model/threat_model.md) — Security analysis
- [Evaluation Plan](../evaluation/evaluation_plan.md) — Experimental methodology
