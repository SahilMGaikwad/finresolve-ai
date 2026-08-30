# Case Detail Workspace Specification

## 1. Hierarchy & Purpose
The **Case Detail Workspace** (`apps/web/app/cases/[id]/page.tsx`) is the primary workspace where an operations analyst investigates discrepancies, reviews evidence, triggers investigations, and inspects counterfactual simulations.

## 2. Core Panels & Layout
1. **Header & Context Bar**: Case ID, Merchant ID, Ingestion Difficulty badge, Status Badge, and Primary `[ Run AI Investigation ]` Action button.
2. **Discrepancy Alert Banner**: Highlights detected rule violations (e.g. `settlement_amount_mismatch`, `fee_calculation_error`) with explicit monetary difference descriptions.
3. **Records Inspector Tabs**:
   - `Payments`: Gateway ID, method, captured timestamp, amount (paise $\to$ INR).
   - `Settlements`: UTR, gross amount, fee deducted, net amount.
   - `Fees`: Fee type, rate in basis points, applied tax amounts.
   - `Refunds`: Refund reason, status, processed timestamp.
   - `Double-Entry Ledger`: Debit, Credit, running balance after posting.
4. **Sub-View Selectors**: Switch between Financial Records, Deterministic Evidence Graph, AI Investigation Console, and Counterfactual Resolution Simulator.
