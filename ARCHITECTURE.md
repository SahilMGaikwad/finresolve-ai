# FinResolve AI — Architecture

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Goals](#2-goals)
3. [Non-Goals](#3-non-goals)
4. [System Architecture](#4-system-architecture)
5. [Data Flow](#5-data-flow)
6. [Module Boundaries](#6-module-boundaries)
7. [Evidence Model](#7-evidence-model)
8. [Counterfactual Engine Design](#8-counterfactual-engine-design)
9. [AI/ML Boundaries](#9-aiml-boundaries)
10. [Agent Architecture](#10-agent-architecture)
11. [Policy Engine](#11-policy-engine)
12. [Audit System](#12-audit-system)
13. [Evaluation Architecture](#13-evaluation-architecture)
14. [Failure Handling](#14-failure-handling)
15. [Security Boundaries](#15-security-boundaries)
16. [Future Razorpay Test-Mode Integration](#16-future-razorpay-test-mode-integration)

---

## 1. Problem Statement

Financial operations at scale produce records across multiple systems: payment gateways, order management, settlement engines, refund processors, fee calculators, and ledger systems. These records frequently disagree due to:

- Timing differences between systems
- Fee deductions applied at different stages
- Partial settlements or refunds
- System errors and race conditions
- Data format inconsistencies across sources
- Missing or duplicate records

Manual reconciliation is slow, expensive, and error-prone. Existing automated reconciliation tools typically produce binary "match/mismatch" results without explaining *why* a discrepancy exists or *how* to resolve it.

FinResolve AI addresses this gap by not only detecting discrepancies but also investigating their root causes, simulating possible resolutions, and safely resolving eligible cases — with mandatory human oversight for uncertain or high-risk situations.

---

## 2. Goals

1. **Accurate reconciliation** across fragmented financial records (payments, orders, settlements, refunds, fees, ledger entries, payouts).
2. **Root-cause diagnosis** that explains *why* a discrepancy exists, not just *that* it exists.
3. **Counterfactual resolution** that simulates "what-if" scenarios to identify the most likely correct resolution.
4. **Safety-first resolution** where every proposed action passes through a deterministic policy engine before execution.
5. **Human escalation** when confidence or evidence is insufficient — the system must be able to say "I don't know."
6. **Full auditability** of every decision, from evidence collection through resolution.
7. **Measurable performance** evaluated against ground-truth synthetic data with honest metrics.
8. **Extensibility** to support future Razorpay API integration in test mode.

---

## 3. Non-Goals

1. **Production payment processing** — This system does not process live payments.
2. **Real-time sub-millisecond reconciliation** — Near-real-time is acceptable; microsecond latency is not a goal.
3. **Universal financial instrument support** — Scoped to the seven record types listed above.
4. **Replacing human judgment entirely** — The system assists humans; it does not replace them for high-risk decisions.
5. **Building a general-purpose accounting system** — This is a reconciliation and resolution tool, not an ERP.

---

## 4. System Architecture

The system follows a **modular monolith** architecture within a monorepo. Services are logically separated but deployed as a single unit initially, with the option to extract into microservices if scale demands.

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                       │
│   /ingest   /reconcile   /investigate   /resolve   /audit       │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│                    Service Layer (Python)                        │
│                                                                 │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │Ingestion │→│Normalizat.│→│ Matching │→│ Discrepancy Det. │  │
│  └──────────┘ └───────────┘ └──────────┘ └────────┬─────────┘  │
│                                                    │            │
│  ┌──────────┐ ┌───────────┐ ┌──────────────────┐  │            │
│  │ Evidence │←│ Diagnosis │←│ Anomaly Detection │←─┘            │
│  └────┬─────┘ └─────┬─────┘ └──────────────────┘              │
│       │             │                                           │
│  ┌────▼─────────────▼──────┐ ┌─────────────────┐              │
│  │ Counterfactual Engine   │→│ Decision Engine  │              │
│  └─────────────────────────┘ └────────┬────────┘              │
│                                       │                        │
│  ┌────────────────────────────────────▼────────────────────┐   │
│  │              Policy Engine (Deterministic)               │   │
│  │  confidence check → risk check → amount limit → action   │   │
│  └──────────┬──────────────────┬──────────────┬────────────┘   │
│             │                  │              │                 │
│         AUTO RESOLVE      HUMAN REVIEW      BLOCK              │
│             │                  │              │                 │
│  ┌──────────▼──────────────────▼──────────────▼────────────┐   │
│  │                    Audit Service                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│                   Data Layer (PostgreSQL)                        │
│   records   │  matches  │  evidence  │  decisions  │  audit     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Flow

The primary financial operations pipeline processes records through 12 stages:

### Stage 1: INGEST
Raw financial records (payments, orders, settlements, refunds, fees, ledger entries, payouts) are received from external sources. Each record is validated for structural integrity and assigned ingestion metadata (timestamp, source ID, ingestion ID). Malformed records are rejected and quarantined.

### Stage 2: NORMALIZE
Validated records are converted to a canonical internal schema. Field names, types, and formats are standardized. All monetary amounts are converted to integer minor currency units (e.g., paise for INR). Timestamps are normalized to UTC.

### Stage 3: MATCH
Normalized records are matched across data sources using:
- **Deterministic matching**: Exact match on shared identifiers (payment_id, order_id, settlement_id).
- **Fuzzy matching**: Approximate match on amount, timestamp proximity, and metadata similarity for records without shared IDs.

### Stage 4: DETECT DISCREPANCY
Matched record groups are compared field-by-field. Discrepancies are classified by type (amount mismatch, missing record, duplicate, timing mismatch, etc.) and severity.

### Stage 5: COLLECT EVIDENCE
For each discrepancy, structured evidence is gathered from the matched record group and related records. Evidence includes observed values, expected values, source records, and supporting rules.

### Stage 6: DIAGNOSE ROOT CAUSE
Candidate hypotheses are generated for the observed discrepancy. Each hypothesis is scored against the collected evidence. Hypotheses may be generated by:
- Rule-based systems (known fee structures, settlement patterns)
- ML models (pattern recognition from historical data)
- LLM (novel hypothesis generation with evidence interpretation)

### Stage 7: SIMULATE RESOLUTIONS
The counterfactual engine simulates the financial consequence of each candidate resolution. For each hypothesis, it constructs the "what-if" ledger state and compares it against the expected state. This is a **deterministic** operation.

### Stage 8: SELECT RESOLUTION
The decision engine ranks candidate resolutions by:
- Evidence support score
- Simulation consistency score
- Confidence level
- Risk assessment

### Stage 9: POLICY CHECK
The selected resolution passes through the deterministic policy engine:
- Confidence ≥ threshold?
- Evidence sufficient?
- Action permitted by policy?
- Transaction value ≤ autonomous limit?
- No risk flags?

Outcome: **AUTO RESOLVE**, **HUMAN REVIEW**, or **BLOCK**.

### Stage 10: HUMAN APPROVAL (conditional)
If the policy engine routes to HUMAN REVIEW, the case is queued for human operators with the full evidence chain, hypothesis ranking, and simulation results.

### Stage 11: RESOLVE
Approved resolutions are executed as idempotent operations. Each resolution produces an audit record before and after execution.

### Stage 12: EVALUATE
Resolution outcomes are compared against ground truth (in evaluation mode) to compute metrics: precision, recall, accuracy, escalation rate, etc.

---

## 6. Module Boundaries

Each service module has a defined interface contract:

| Module | Input | Output | Dependencies |
|--------|-------|--------|-------------|
| `ingestion` | Raw records | Validated records | Schemas |
| `normalization` | Validated records | Canonical records | Schemas |
| `matching` | Canonical records | Match groups + unmatched | — |
| `anomaly_detection` | Match groups | Anomaly scores | ML models |
| `evidence` | Match groups + anomaly scores | Evidence records | — |
| `diagnosis` | Evidence records | Ranked hypotheses | ML models, LLM |
| `counterfactual` | Hypotheses + match groups | Simulation results | — |
| `decision_engine` | Scored hypotheses + simulations | Selected resolution | — |
| `policy_engine` | Selected resolution | Action decision | Configuration |
| `audit` | Any action | Audit record | — |

**Key constraint**: Module dependencies flow in one direction. No circular dependencies.

---

## 7. Evidence Model

Every decision must be explainable through structured evidence. An evidence record captures:

```
EvidenceRecord:
    evidence_id:        UUID            # Unique identifier
    discrepancy_id:     UUID            # The discrepancy this evidence relates to
    source_record_id:   UUID            # The record this evidence was extracted from
    source_record_type: RecordType      # payment, order, settlement, etc.
    field:              str             # The field name (e.g., "amount", "status")
    observed_value:     str             # What the field actually contains
    expected_value:     str             # What the field should contain (if known)
    relationship:       str             # How this evidence relates to the hypothesis
    supporting_rule:    str | None      # The rule or logic that produced this evidence
    timestamp:          datetime        # When this evidence was collected
    evidence_strength:  float           # 0.0–1.0, how strongly this supports/refutes
    confidence:         float           # 0.0–1.0, confidence in the evidence itself
    hypothesis_id:      UUID | None     # The hypothesis this evidence supports
    decision_id:        UUID | None     # The decision this evidence contributed to
```

**Design principle**: Evidence records are the atomic unit of explainability. Every resolution must trace back to specific evidence records. Free-form LLM text alone is never sufficient as evidence.

---

## 8. Counterfactual Engine Design

The counterfactual engine is the core differentiator of FinResolve AI.

### Concept

Given a discrepancy and a set of candidate hypotheses, the engine asks:

> "If hypothesis H is correct, what would the financial state look like?"

### Process

1. **Receive** a discrepancy with matched records and candidate hypotheses.
2. **For each hypothesis**, construct a simulated ledger state:
   - If H = "settlement fee of 3%": compute payment × 0.97, compare to observed settlement.
   - If H = "partial settlement (batch 1 of 2)": look for other settlements summing to payment.
   - If H = "refund adjustment": look for refund records and adjust expected settlement.
   - If H = "incorrect settlement": expected settlement should equal payment amount.
3. **Score** each simulation by how well it explains the observed data.
4. **Rank** hypotheses by simulation consistency.
5. **Produce** a structured report with the simulation inputs, outputs, and scores.

### Implementation Principles

- All financial calculations use **deterministic integer arithmetic** (minor currency units).
- No floating-point arithmetic for monetary values.
- All simulations are **pure functions**: same inputs always produce the same outputs.
- Simulation results are **immutable** once produced.
- The engine does **not** use an LLM for calculations — LLMs may generate hypotheses upstream, but the simulation itself is deterministic.

### Example

```
Input:
    payment.amount  = 5000000  (₹50,000.00 in paise)
    settlement.amount = 4850000  (₹48,500.00 in paise)
    ledger.amount   = 5000000  (₹50,000.00 in paise)

Hypothesis A: "Settlement fee of 3%"
    simulated_settlement = 5000000 * (100 - 3) / 100 = 4850000
    observed_settlement  = 4850000
    delta = 0  →  PERFECT MATCH  →  score = 1.0

Hypothesis B: "Partial settlement (unknown remainder)"
    simulated_settlement = 4850000 (assumed partial)
    remaining = 5000000 - 4850000 = 150000
    No matching second settlement found.
    score = 0.3 (partial support, incomplete evidence)

Hypothesis C: "Incorrect settlement"
    expected_settlement = 5000000
    observed_settlement = 4850000
    delta = 150000
    No error record or correction found.
    score = 0.2 (possible but unsupported)
```

---

## 9. AI/ML Boundaries

The system enforces strict boundaries on what each technology is responsible for:

### Deterministic Logic (Rules + Code)
- Amount calculations and currency arithmetic
- ID matching and foreign-key relationships
- Timestamp comparison and ordering
- Reconciliation rule evaluation
- Policy enforcement
- Ledger simulation (counterfactual engine)
- Audit record generation
- Idempotency enforcement

### Machine Learning (scikit-learn, XGBoost)
- Anomaly detection in transaction patterns
- Matching confidence scoring for fuzzy matches
- Candidate hypothesis ranking
- Probability estimation for resolution outcomes
- Pattern detection across historical discrepancies

### Large Language Models (LLM)
- Evidence interpretation and summarization
- Root-cause reasoning from complex evidence chains
- Natural-language explanation generation for operators
- Novel hypothesis generation when rule-based generation is insufficient
- **Read-only**: LLMs receive evidence but never directly produce financial mutations

### Agent (LangGraph)
- Orchestrating the investigation workflow
- Selecting which tools (evidence collection, simulation, etc.) to invoke
- Managing the investigation state machine
- Routing between automated and human-review paths

### Critical Constraint

```
LLM ──suggests──→ Agent ──invokes──→ Deterministic Tool ──proposes──→ Policy Engine ──decides──→ Action
                                                                                    └──→ Human Review
                                                                                    └──→ Block
```

An LLM **never** directly modifies financial state. The chain is always:
LLM suggestion → agent action → deterministic validation → policy gate → audited execution.

---

## 10. Agent Architecture

The agent orchestrates the investigation workflow using LangGraph's state-machine model.

### Investigation State Machine (Planned)

```
START
  → COLLECT_RECORDS
  → NORMALIZE
  → MATCH
  → DETECT_DISCREPANCIES
  → [for each discrepancy]
      → COLLECT_EVIDENCE
      → GENERATE_HYPOTHESES
      → SCORE_HYPOTHESES
      → SIMULATE_RESOLUTIONS
      → SELECT_RESOLUTION
      → POLICY_CHECK
        → AUTO_RESOLVE | HUMAN_REVIEW | BLOCK
  → AUDIT
  → END
```

### Agent Tools (Planned)

The agent will have access to a defined set of tools:

| Tool | Purpose | Modifies State? |
|------|---------|----------------|
| `fetch_records` | Retrieve records by ID or query | No |
| `collect_evidence` | Gather evidence for a discrepancy | No |
| `run_simulation` | Execute counterfactual simulation | No |
| `score_hypothesis` | Score a hypothesis against evidence | No |
| `check_policy` | Validate an action against policy rules | No |
| `submit_resolution` | Submit a resolution for policy review | Yes (gated) |

**All state-modifying tools are gated by the policy engine.** The agent cannot bypass the policy engine.

---

## 11. Policy Engine

The policy engine is a **purely deterministic** rule evaluator. No ML. No LLM. No probabilistic behavior.

### Decision Flow

```python
# Pseudocode — actual implementation in Phase 3
def evaluate_resolution(resolution: Resolution, policy: PolicyConfig) -> PolicyDecision:
    # 1. Evidence sufficiency
    if resolution.evidence_count < policy.min_evidence_count:
        return PolicyDecision.HUMAN_REVIEW

    # 2. Confidence threshold
    if resolution.confidence < policy.auto_resolve_confidence_threshold:
        return PolicyDecision.HUMAN_REVIEW

    # 3. Risk flags
    if resolution.has_risk_flags():
        return PolicyDecision.HUMAN_REVIEW

    # 4. Action permission
    if resolution.action_type not in policy.permitted_actions:
        return PolicyDecision.BLOCK

    # 5. Amount limit
    if resolution.amount > policy.auto_resolve_max_amount:
        return PolicyDecision.HUMAN_REVIEW

    # 6. Duplicate check
    if resolution.is_duplicate():
        return PolicyDecision.BLOCK

    return PolicyDecision.AUTO_RESOLVE
```

### Policy Configuration

All thresholds are externalized as environment variables, never hardcoded:

- `POLICY_AUTO_RESOLVE_CONFIDENCE_THRESHOLD` (default: 0.95)
- `POLICY_AUTO_RESOLVE_MAX_AMOUNT` (default: 500,000 paise = ₹5,000)
- `POLICY_AUTO_RESOLVE_ENABLED` (default: false)

---

## 12. Audit System

Every action in the system produces an immutable audit record.

### Audit Record Schema (Planned)

```
AuditRecord:
    audit_id:           UUID
    timestamp:          datetime (UTC)
    actor:              str         # "system", "agent", "human:<user_id>"
    action_type:        str         # "match", "diagnose", "resolve", "escalate", "block"
    target_record_ids:  list[UUID]
    discrepancy_id:     UUID | None
    resolution_id:      UUID | None
    policy_decision:    str         # "auto_resolve", "human_review", "block"
    evidence_ids:       list[UUID]
    confidence:         float
    input_snapshot:     dict        # Serialized inputs at decision time
    output_snapshot:    dict        # Serialized outputs after action
    idempotency_key:    str         # For duplicate-action prevention
```

### Properties

- **Append-only**: Audit records are never modified or deleted.
- **Tamper-evident**: Records include a hash chain linking each record to its predecessor.
- **Complete**: Every state transition produces an audit record, including "no action" decisions.

---

## 13. Evaluation Architecture

The system is evaluated against synthetic datasets with known ground truth.

### Metrics (Defined, Not Yet Measured)

| Metric | Definition |
|--------|-----------|
| Match Precision | Correct matches / total matches |
| Match Recall | Correct matches / total true matches |
| Match Rate | Matched records / total records |
| False Match Rate | Incorrect matches / total matches |
| Discrepancy Detection Accuracy | Correctly detected discrepancies / total discrepancies |
| Root-Cause Accuracy | Correct root cause / total diagnosed discrepancies |
| Auto-Resolution Accuracy | Correct auto-resolutions / total auto-resolutions |
| Human Escalation Rate | Escalated cases / total cases |
| Unresolved Exception Rate | Unresolved cases / total cases |
| Throughput | Records processed per second |
| Latency (P50, P95, P99) | Time from ingestion to resolution |

### Evaluation Protocol

1. Generate synthetic dataset with known ground truth using `data/generators/`.
2. Run the full pipeline on the synthetic dataset.
3. Compare system outputs against ground truth labels.
4. Compute metrics.
5. Report results with confidence intervals where applicable.

**No metrics are hardcoded or fabricated.** All reported metrics must be computed from actual system execution.

---

## 14. Failure Handling

### Failure Modes

| Failure | Handling |
|---------|---------|
| Malformed input record | Reject at ingestion, quarantine, log |
| No match found | Flag as unmatched, include in exception report |
| Multiple ambiguous matches | Escalate to human review |
| Insufficient evidence | Escalate to human review with available evidence |
| All hypotheses low-confidence | Escalate to human review |
| Simulation produces impossible state | Flag as anomaly, block resolution |
| Policy engine rejects action | Block or escalate per policy |
| Database write failure | Retry with exponential backoff, then escalate |
| LLM timeout or error | Degrade gracefully: proceed with rule-based diagnosis only |
| LLM hallucination detected | Discard LLM output, fall back to evidence-only diagnosis |

### Design Principle

The system is designed to **fail safe**. When in doubt, the default action is **HUMAN REVIEW**, never silent acceptance.

---

## 15. Security Boundaries

### Trust Boundaries

```
UNTRUSTED                          TRUSTED
─────────────────────────────────────────────
Transaction metadata          →   Validated after ingestion
External record content       →   Normalized and sanitized
LLM-generated text            →   Treated as suggestions, never executed
User input (future UI)        →   Validated at API boundary
```

### Key Security Properties

1. **Transaction metadata is untrusted data.** Descriptions, notes, and metadata fields in financial records are never interpreted as instructions for the AI agent.
2. **LLM outputs are suggestions, not commands.** All LLM-generated hypotheses and explanations pass through deterministic validation before any action.
3. **Policy engine is not byppassable.** No code path exists that allows a financial action without policy evaluation.
4. **Audit log is append-only.** No API or internal function can modify or delete audit records.
5. **Idempotency keys prevent duplicate resolution.** Every resolution attempt requires a unique idempotency key.

See [docs/threat_model/threat_model.md](docs/threat_model/threat_model.md) for the full threat analysis.

---

## 16. Future Razorpay Test-Mode Integration

> **Status: NOT IMPLEMENTED** — This section describes the planned integration approach.

### Approach

1. Use Razorpay's **test-mode API keys** only. No production keys in this system.
2. Integrate with Razorpay's test APIs to:
   - Fetch test payments, orders, settlements, and refunds.
   - Use test data as input to the reconciliation pipeline.
   - Validate that the system correctly handles Razorpay's data formats.
3. All Razorpay API calls will go through a dedicated integration module with:
   - Rate limiting
   - Error handling
   - Response validation
   - Credential isolation (test keys only, enforced by configuration)

### Safety Constraints

- `RAZORPAY_TEST_MODE` environment variable must be `true`. The system will refuse to start if real (non-test) credentials are detected.
- No write operations to Razorpay from the reconciliation system. The system is read-only with respect to Razorpay's API.
- API credentials are never logged, stored in audit records, or passed to LLMs.

---

## Appendix: Decision Records

Architecture decisions are documented in [docs/decisions/](docs/decisions/).

- [ADR-001: Project Architecture](docs/decisions/ADR-001-project-architecture.md)
