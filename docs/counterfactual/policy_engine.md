# FinResolve AI — Deterministic Policy Engine

## Overview

The Deterministic Policy Engine evaluates simulated resolution proposals against strict risk bounds, monetary limits, and safety invariants before allowing any action to proceed.

---

## 1. Decision Categories

| Decision | Criteria | Next Action |
| :--- | :--- | :--- |
| **`AUTO_RESOLVABLE`** | Valid simulation + $\ge 1$ evidence item + Amount $\le ₹5,000$ + Low/Medium Risk + Master switch enabled | Eligible for automated processing |
| **`HUMAN_REVIEW`** | Valid simulation + High monetary amount ($> ₹5,000$) OR High/Critical Risk OR Master switch disabled | Routed to financial analyst queue with separation of duties |
| **`BLOCKED`** | Failed simulation OR secondary residual discrepancies OR invalid ledger result | Action rejected and logged with blocking reasons |
| **`NO_SAFE_ACTION`** | Insufficient or contradictory evidence | Escalated for manual case investigation |

---

## 2. Policy Rule Hierarchy

- `POL-001 (SimulationValidity)`: Simulation must clear 100% of discrepancies with zero residuals.
- `POL-002 (EvidenceSufficiency)`: Action must cite verifiable diagnostic evidence items.
- `POL-003 (MonetaryThreshold)`: Autonomous action value cannot exceed configured threshold (`policy_auto_resolve_max_amount`).
- `POL-004 (RiskClassification)`: Actions classified as High or Critical risk require human approval.
- `POL-005 (MasterAutoResolveSwitch)`: Auto-resolution must be explicitly enabled via `policy_auto_resolve_enabled` setting.
