# Counterfactual Resolution Simulator Specification

## 1. Overview
The **Resolution Simulator Panel** (`apps/web/components/simulator/BeforeAfterTable.tsx`) visualizes the output of the Counterfactual Simulation engine (`services/counterfactual/simulator.py`).

## 2. Invariants & Financial Presentation
- **Exact Minor Unit Accuracy**: All monetary deltas are calculated in integer paise and formatted in INR (`₹XX,XXX.XX`).
- **Cumulative Financial Delta**:
  - `Δ Merchant Balance`
  - `Δ Platform Fee Balance`
  - `Δ GST Tax Liability`
  - `Conservation Law Check`: Confirms zero-sum net system delta ($\Delta \text{System Net} = 0.00\text{ paise}$).
- **Policy Decision Badge**: Highlights whether the simulated plan qualifies for `AUTO_RESOLVABLE`, requires `HUMAN_REVIEW_REQUIRED`, or is `BLOCKED`.
- **Sequential Steps Table**: Details each ordered corrective action (e.g. `SETTLEMENT_ADJUSTMENT`, `FEE_RECALCULATION`) with associated justification and target record ID.
