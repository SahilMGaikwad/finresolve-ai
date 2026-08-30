# FinResolve AI

**Counterfactual Financial Reconciliation & Resolution Engine**

---

## Overview

FinResolve AI is an AI-assisted financial operations controller designed to reconcile fragmented merchant financial records, detect discrepancies, investigate their root causes, evaluate possible resolutions through counterfactual simulation, and safely resolve eligible cases — with human oversight where required.

### The Problem

Financial operations at scale produce fragmented records across multiple systems: payments, orders, settlements, refunds, fees, ledger entries, and payouts. When these records disagree, operations teams must manually investigate discrepancies — a slow, error-prone process that scales poorly.

### The Approach

FinResolve AI doesn't just detect mismatches. It asks: **"What plausible explanations could produce this discrepancy?"**

For each discrepancy, the system:

1. Generates candidate hypotheses (e.g., fee deduction, partial settlement, refund adjustment)
2. Collects structured evidence from related records
3. Scores each hypothesis against the evidence
4. Simulates the financial consequence of each possible resolution
5. Selects the best-supported resolution
6. Enforces safety policies before any action
7. Escalates to human review when confidence or evidence is insufficient

### Core Differentiator

The **Counterfactual Resolution Engine** — instead of binary "match/mismatch" detection, the system performs "what-if" analysis to determine the most likely root cause and the safest resolution path.

---

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project scaffolding, architecture, documentation | ✅ Complete |
| 2 | Data schemas, synthetic data generation, ingestion pipeline | 🔲 Not started |
| 3 | Matching engine, evidence collection, policy engine | 🔲 Not started |
| 4 | Counterfactual engine, diagnosis, decision engine | 🔲 Not started |
| 5 | Agent orchestration, LLM integration, frontend | 🔲 Not started |
| 6 | Evaluation, benchmarking, Razorpay test-mode integration | 🔲 Not started |

> **Note**: Only Phase 1 is implemented. All other phases are planned but not yet built.

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system architecture.

### Finance Operations Pipeline

```
INGEST → NORMALIZE → MATCH → DETECT DISCREPANCY
    → COLLECT EVIDENCE → DIAGNOSE ROOT CAUSE
    → SIMULATE RESOLUTIONS → SELECT SAFE RESOLUTION
    → POLICY CHECK → HUMAN APPROVAL (if required)
    → RESOLVE → AUDIT → EVALUATE
```

### AI Boundaries

| Technology | Responsibility |
|-----------|----------------|
| **Deterministic logic** | Amount calculations, currency arithmetic, matching rules, policy enforcement |
| **ML** | Anomaly detection, candidate ranking, probability estimation |
| **LLM** | Evidence interpretation, root-cause reasoning, explanation generation |
| **Agent** | Orchestration, tool selection, investigation workflow |
| **Policy engine** | Safety rules, confidence thresholds, human approval requirements |

The LLM **never** directly modifies financial records. All actions pass through the deterministic policy engine.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js + TypeScript |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| ML | scikit-learn + XGBoost |
| Data processing | Pandas / Polars |
| Agent orchestration | LangGraph |
| Testing | Pytest |
| Containers | Docker |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized development)
- Git

### Local Development

```bash
# Clone the repository
git clone <repo-url>
cd finresolve-ai

# Run setup script
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt

# Copy environment configuration
cp .env.example .env

# Run tests
python -m pytest tests/ -v

# Start API server
uvicorn apps.api.main:app --reload
```

### Docker Development

```bash
docker compose up
```

The API will be available at `http://localhost:8000`.
Health check: `http://localhost:8000/health`.

---

## Project Structure

```
finresolve-ai/
├── apps/
│   ├── api/              # FastAPI backend
│   └── web/              # Next.js frontend (Phase 5+)
├── services/
│   ├── ingestion/        # Record ingestion and validation
│   ├── normalization/    # Schema normalization
│   ├── matching/         # Deterministic + fuzzy matching
│   ├── evidence/         # Evidence collection and scoring
│   ├── anomaly_detection/# ML-based anomaly detection
│   ├── diagnosis/        # Root cause diagnosis
│   ├── counterfactual/   # Counterfactual resolution engine
│   ├── decision_engine/  # Resolution selection
│   ├── policy_engine/    # Deterministic safety enforcement
│   └── audit/            # Immutable audit logging
├── ml/
│   ├── features/         # Feature engineering
│   ├── models/           # Model definitions
│   ├── training/         # Training pipelines
│   └── evaluation/       # Model evaluation
├── data/
│   ├── schemas/          # Pydantic/JSON schemas
│   ├── generators/       # Synthetic data generation
│   └── fixtures/         # Test fixtures
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── adversarial/
│   └── evaluation/
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── threat_model/
│   └── evaluation/
├── scripts/
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── README.md
├── docker-compose.yml
├── pytest.ini
├── .env.example
└── .gitignore
```

---

## Documentation

- [Architecture](ARCHITECTURE.md) — System design, data flow, module boundaries
- [Contributing](CONTRIBUTING.md) — Development standards and workflow
- [ADR-001: Project Architecture](docs/decisions/ADR-001-project-architecture.md) — Architecture decisions
- [Threat Model](docs/threat_model/threat_model.md) — Security analysis
- [Evaluation Plan](docs/evaluation/evaluation_plan.md) — Experimental methodology

---

## License

This project is developed for the Razorpay AI Builder Internship 2026 evaluation.
