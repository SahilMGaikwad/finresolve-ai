# FinResolve AI — Multi-Step Resolution Planning

## 1. Motivation

Phase 4 demonstrated that 24 out of 47 unresolved cases were caused by **compound corruptions** (e.g. `amount_mismatch` + `fee_discrepancy` + `incorrect_reference`). Single-step actions left residual discrepancies and failed closed-loop simulation.

Phase 5 addresses this by composing sequential `PlanStep` sequences within a unified [`ResolutionPlan`](file:///Users/sahilgaikwad/finresolve-ai/data/schemas/investigation.py).

---

## 2. Dependency Execution Order

1. **Reference & Identity Corrections** (`REFERENCE_CORRECTION`, `STATUS_CORRECTION`)
2. **Fee & Tax Recalculations** (`FEE_ADJUSTMENT`)
3. **Missing Record Reconstructions** (`MISSING_RECORD_RECONSTRUCTION`)
4. **Settlement Balance Adjustments** (`SETTLEMENT_ADJUSTMENT`)
5. **Duplicate Compensations** (`LEDGER_CORRECTION`)

---

## 3. Simulation & Validation Lifecycle

```
[Initial Virtual State_0]
        │
        ▼ (Step 1: Reference Repair)
[Projected State_1]
        │
        ▼ (Step 2: Fee Recalculation)
[Projected State_2]
        │
        ▼ (Step 3: Settlement Balance Sync)
[Final Projected State_N]
        │
        ▼
[Closed-Loop Reconciliation & Zero-Sum Delta Verification]
```
