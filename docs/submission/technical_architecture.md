# Technical Architecture — FinResolve AI

## Subsystem Specifications

### 1. Ingestion & Canonical Schemas ([`data/schemas/`](file:///Users/sahilgaikwad/finresolve-ai/data/schemas/))
- Strict integer minor currency units (`amount_minor` in paise).
- Full ingestion provenance tracking (`source_system`, `source_record_id`, `normalization_version`).

### 2. Multi-Signal Matching ([`services/matching/`](file:///Users/sahilgaikwad/finresolve-ai/services/matching/))
- Evaluates 6 deterministic signals without statistical drift.
- Supports 1:1, 1:N split settlements, and N:1 batch disbursements.

### 3. Evidence Engine & Diagnosis ([`services/evidence/`](file:///Users/sahilgaikwad/finresolve-ai/services/evidence/) & [`services/diagnosis/`](file:///Users/sahilgaikwad/finresolve-ai/services/diagnosis/))
- 5 reconciliation rules generating structured evidence artifacts.
- Bayesian plausibility scoring based on Evidence Graph topology.

### 4. AI Investigator & Claim Validator ([`services/investigator/`](file:///Users/sahilgaikwad/finresolve-ai/services/investigator/))
- Finite state machine with execution circuit breakers (max 8 steps, 12 tool calls, 10.0s timeout).
- Independent `ClaimValidator` verifying entity IDs, fields, and values against observable records.

### 5. Counterfactual Simulation & Policy Gating ([`services/counterfactual/`](file:///Users/sahilgaikwad/finresolve-ai/services/counterfactual/) & [`services/policy_engine/`](file:///Users/sahilgaikwad/finresolve-ai/services/policy_engine/))
- Isolated state cloning and closed-loop re-reconciliation.
- Rules `POL-001` - `POL-005` enforcing ₹5,000 threshold and separation of duties.

### 6. Cryptographic Audit Logger ([`services/audit/`](file:///Users/sahilgaikwad/finresolve-ai/services/audit/))
- Immutable append-only SHA-256 hash chaining.
