# FinResolve AI — Counterfactual Simulation Architecture

## Overview

The Counterfactual Simulation Engine is the core predictive differentiator of FinResolve AI. It evaluates *"what if"* financial scenarios by projecting candidate corrective actions onto an isolated in-memory state and re-running the deterministic reconciliation engine.

**Core Principle**:
> **AI MAY RECOMMEND. DETERMINISTIC CONTROLS MAY VALIDATE. POLICY ENGINE MAY AUTHORIZE. HUMANS MAY APPROVE HIGH-RISK ACTIONS. REAL FINANCIAL EXECUTION IS OUTSIDE THE CURRENT PROTOTYPE.**

---

## 1. Simulation Lifecycle

```
[Observed Records]
       │
       ▼
[Deep Clone: CounterfactualState]  <--- Zero mutation of source records
       │
       ▼
[Apply ResolutionAction]
       │
       ▼
[Closed-Loop Deterministic Reconciliation]
       │
       ▼
[Ledger & Delta Verification]
       │
       ▼
[SimulationResult (is_valid, residual_discrepancies, delta)]
```

---

## 2. Invariants Enforced During Simulation

1. **State Isolation**: The simulator deep-clones all observed records. Source records remain untouched.
2. **Integer Arithmetic**: All monetary quantities operate strictly in minor currency units (paise). Zero floating-point math.
3. **Discrepancy Elimination**: A simulation is considered `is_valid == True` if and only if re-running reconciliation yields `status == RECONCILED` with zero residual discrepancies.
4. **Double-Entry Ledger Integrity**: Validates that all ledger debit/credit postings maintain non-negative positive flows and appropriate balancing.
