# FinResolve AI — Four Evaluator Demo Scenarios

This document details the exact, reproducible demo walkthrough across all four fundamental financial reconciliation scenarios using real case IDs from the controlled synthetic benchmark (Seed: 42).

---

## Scenario Summary Table

| Scenario | Case ID | Classification | Key Technical Concept Demonstrated |
| :--- | :--- | :--- | :--- |
| **A. Clean Baseline** | `CASE-000002` | Clean Reconciled | Zero false-positive alerts; clean baseline reconciliation. |
| **B. Discrepancy + Simulation** | `CASE-000003` | Discrepancy + Counterfactual Simulation | Single monetary discrepancy of ₹638.44. The system identifies the settlement mismatch, generates a corrective settlement adjustment, validates it through counterfactual simulation, and confirms zero residual discrepancies and balanced ledger conservation. The case demonstrates the complete discrepancy-to-simulation workflow. |
| **C. Human-in-the-Loop Review** | `CASE-000132` | Human Review Required | High-value monetary variance (-₹2,318.36); valid counterfactual simulation; policy gating to human approval queue; separation-of-duties sign-off. |
| **D. Blocked Compound Corruption** | `CASE-000009` | Blocked Compound Failure | 3 compound corruptions (`amount_mismatch`, `incorrect_reference`, `fee_discrepancy`); fail-closed invariant protection; structured analyst handoff package. |

---

## Scenario A: Clean Reconciled Case (`CASE-000002`)

- **Context**: Merchant `merchant_0002` processing standard payments and settlements with balanced fees and ledger postings.
- **What Evaluator Sees**:
  - Top green banner: *"All observed payments, settlements, fees, and ledger postings are perfectly balanced (0 Discrepancies)."*
  - Record counts: 1 Payment, 1 Settlement, 1 Fee, 2 Ledger Entries.
  - Evidence Graph: All entity relationships connected via solid green lines.
- **Action**: Click **`[ ⚡ Run AI Investigation ]`**.
- **Result**:
  - Investigation concludes immediately in `COMPLETED` state.
  - AI synthesizes: *"Case status concluded as reconciled. 0 discrepancies identified."*
  - Zero financial adjustments or resolution plans generated.
- **Technical Concept Demonstrated**: Grounded baseline reconciliation; system does not hallucinate false-positive errors or propose unneeded financial mutations.

---

## Scenario B: Discrepancy + Counterfactual Simulation (`CASE-000003`)

- **Context**: Merchant `merchant_0003` with a single settlement net amount variance.
- **What Evaluator Sees**:
  - Crimson Alert Banner: *"Settlement amount is short by ₹638.44 (Delta: -63,844 paise)"*.
  - Evidence Graph: Broken red dashed line connecting payment and settlement entities.
- **Action**: Click **`[ ⚡ Run AI Investigation ]`**, then switch to **"🔮 Resolution Simulator"**.
- **Result**:
  - Single monetary discrepancy of ₹638.44. The system identifies the settlement mismatch, generates a corrective settlement adjustment, validates it through counterfactual simulation, and confirms zero residual discrepancies and balanced ledger conservation. The case demonstrates the complete discrepancy-to-simulation workflow.
  - **Financial Delta**: `merchant_balance_delta_minor: +63844` (+₹638.44).
  - **Ledger Verification**: $\Delta \text{Merchant} + \Delta \text{Fee} + \Delta \text{Tax} + \Delta \text{Customer} = 0.00\text{ paise}$ (Balanced).
- **Technical Concept Demonstrated**: End-to-end discrepancy detection, evidence collection, candidate action generation, and closed-loop counterfactual simulation.

---

## Scenario C: High-Value Discrepancy Requiring Human Review (`CASE-000132`)

- **Context**: Merchant `merchant_0002` with a settlement over-calculation variance (-₹2,318.36 / -231,836 paise).
- **What Evaluator Sees**:
  - Crimson Alert Banner: *"Settlement net amount diverges from expected net by -231,836 paise"*.
  - Multi-tab records inspector showing gross payment, fee deduction, and elevated settlement posting.
- **Action**: Click **`[ ⚡ Run AI Investigation ]`**, then switch to **"🔮 Resolution Simulator"** and **Approval Drawer**.
- **Result**:
  - AI diagnoses root cause and generates a corrective `SETTLEMENT_ADJUSTMENT` plan.
  - Counterfactual simulation validates that the adjustment eliminates 100% of residual discrepancies.
  - Policy Engine enforces Rule `POL-003` / `POL-004` $\to$ **`HUMAN_REVIEW_REQUIRED`**.
  - **Approval Sign-Off**: Proposer attempts self-approval and is blocked (403 Forbidden). Authorized approver (`usr_approver_01`) enters audit notes and signs off.
- **Technical Concept Demonstrated**: High-value policy gating, multi-role separation of duties, and cryptographic audit sign-off.

---

## Scenario D: Blocked Compound Corruption Case (`CASE-000009`)

- **Context**: Merchant `merchant_0009` with multi-corruption interactions (`amount_mismatch`, `incorrect_reference`, `fee_discrepancy`).
- **What Evaluator Sees**:
  - Multiple simultaneous rule violations across fee rates, foreign key references, and settlement net amounts.
- **Action**: Click **`[ ⚡ Run AI Investigation ]`**.
- **Result**:
  - AI multi-step planner attempts candidate resolution.
  - Closed-loop counterfactual simulation detects that reference shadowing leaves secondary discrepancies unresolved.
  - Simulator marks plan `is_valid: false`.
  - Policy Engine triggers Rule `POL-001` (Simulation Invalid) $\to$ **`BLOCKED`**.
  - System generates structured `HumanReviewPackage` with key ambiguities and recommended analyst investigation steps.
- **Technical Concept Demonstrated**: Fail-closed safety guarantee; the system refuses to authorize invalid or imbalanced actions when compound errors cannot be mathematically verified.
